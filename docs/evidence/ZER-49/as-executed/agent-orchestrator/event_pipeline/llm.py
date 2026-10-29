"""Bounded async Responses adapter. No tool execution or agent wiring (ZER-48).

The caller owns one RunBudget for the entire run and persists returned LLM_CALL
envelopes through its authenticated recorder. This module never writes O/H archives.
Reservations are conservative policy estimates, not a provider billing hard cap.
"""
import asyncio
import copy
import hashlib
import json
import math
import re
import threading
import time
from dataclasses import dataclass
from decimal import Decimal

import httpx
from pydantic import BaseModel

from .contract import Producer, canonical, forbidden_keys, new_id, valid_id

MODEL = "gpt-6-luna"
ENDPOINT = "https://api.openai.com/v1/responses"
PRICE_REF = "https://developers.openai.com/api/docs/models/gpt-6-luna#pricing"
INPUT_RATE = Decimal("0.10")
OUTPUT_RATE = Decimal("0.50")
MAX_BYTES = 8192
FATAL_CODES = {"insufficient_quota", "organization_spend_limit_exceeded", "project_spend_limit_exceeded",
               "organization_usage_limit_exceeded", "credit_balance_exhausted"}


def _cost(inputs, outputs):
    return (inputs * INPUT_RATE + outputs * OUTPUT_RATE) / Decimal(1_000_000)


def _integer(value, low, high):
    return type(value) is int and low <= value <= high


def _seconds(value, high):
    return type(value) in (float, int) and math.isfinite(value) and 0 < value <= high


def _usage(body):
    u = body.get("usage") if isinstance(body, dict) else None
    fields = ("input_tokens", "output_tokens", "total_tokens")
    if (not isinstance(u, dict) or any(not _integer(u.get(k), 0, 10_000_000) for k in fields)
            or u["total_tokens"] != u["input_tokens"] + u["output_tokens"]):
        return None
    return {k: u[k] for k in fields}


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def invalid(_):
        raise ValueError("NONFINITE_JSON")
    def finite(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("NONFINITE_JSON")
        return value
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite)


def _identifier(value):
    # Never retain arbitrary headers, provider errors or an echoed bearer token.
    if (isinstance(value, str) and re.fullmatch(r"(?:req|resp)_[A-Za-z0-9_-]{1,150}", value)
            and "sk-" not in value):
        return value
    return None


@dataclass(frozen=True)
class Limits:
    attempts: int = 2
    timeout_s: float = 30
    deadline_s: float = 65
    retry_delay_s: float = 1
    max_output_tokens: int = 512

    def __post_init__(self):
        if (not _integer(self.attempts, 1, 2) or not _integer(self.max_output_tokens, 1, 512)
                or not _seconds(self.timeout_s, 30) or not _seconds(self.deadline_s, 65)
                or type(self.retry_delay_s) not in (int, float)
                or not math.isfinite(self.retry_delay_s) or not 0 <= self.retry_delay_s <= 1):
            raise ValueError("LLM_LIMITS_INVALID")


class BudgetExceeded(ValueError):
    pass


class RunBudget:
    """Reserve before every dispatch; never refund uncertain or cancelled attempts.

    The byte-based input reservation includes 1024 tokens of overhead. This is a
    documented bound assumption, not a tokenizer guarantee. Observed overages block
    subsequent dispatch. Unknown usage stays unknown, with its reservation retained.
    Reconstructing/resetting this object on restart does NOT prove durable budgets.
    """
    def __init__(self, run_id, *, max_calls, max_reserved_tokens, max_estimated_usd,
                 duration_s=600, clock=time.monotonic):
        try:
            price = Decimal(str(max_estimated_usd))
        except ArithmeticError as error:
            raise ValueError("LLM_BUDGET_INVALID") from error
        if (not valid_id(run_id, "run") or not _integer(max_calls, 1, 10_000)
                or not _integer(max_reserved_tokens, 1, 100_000_000)
                or not price.is_finite() or price <= 0 or not _seconds(duration_s, 3600)):
            raise ValueError("LLM_BUDGET_INVALID")
        self.run_id, self.max_calls, self.max_tokens, self.max_cost = run_id, max_calls, max_reserved_tokens, price
        self.clock, self.started, self.duration = clock, clock(), duration_s
        self.lock = threading.Lock()
        self.calls = self.tokens = self.unknown = self.input_tokens = self.output_tokens = 0
        self.reserved_cost = self.known_cost = Decimal(0)
        self.blocked = False

    def remaining(self):
        elapsed = self.clock() - self.started
        return self.duration - elapsed if math.isfinite(elapsed) and elapsed >= 0 else 0

    def reserve(self, run_id, input_tokens, output_tokens):
        with self.lock:
            elapsed = self.clock() - self.started
            cost = _cost(input_tokens, output_tokens)
            if (run_id != self.run_id or not math.isfinite(elapsed) or not 0 <= elapsed < self.duration
                    or self.blocked or self.calls >= self.max_calls
                    or self.tokens + input_tokens + output_tokens > self.max_tokens
                    or self.reserved_cost + cost > self.max_cost):
                raise BudgetExceeded("LLM_RUN_BUDGET")
            self.calls += 1
            self.tokens += input_tokens + output_tokens
            self.reserved_cost += cost
            self.unknown += 1

    def account(self, usage, input_reserve, output_cap):
        with self.lock:
            if usage is None:
                return
            self.unknown -= 1
            self.input_tokens += usage["input_tokens"]
            self.output_tokens += usage["output_tokens"]
            self.known_cost += _cost(usage["input_tokens"], usage["output_tokens"])
            if usage["input_tokens"] > input_reserve or usage["output_tokens"] > output_cap:
                self.blocked = True

    def summary(self):
        with self.lock:
            return {"run_id": self.run_id, "attempts_dispatched": self.calls,
                    "reserved_tokens": self.tokens, "reserved_estimate_usd": float(self.reserved_cost),
                    "known_input_tokens": self.input_tokens, "known_output_tokens": self.output_tokens,
                    "known_cost_estimate_usd": float(self.known_cost), "unknown_usage_attempts": self.unknown,
                    "cost_estimate_complete": self.unknown == 0, "blocked": self.blocked,
                    "accounting_scope": "PROCESS_SINGLE_SHARED_RUN_BUDGET",
                    "price_ref": PRICE_REF, "price_checked": "2026-10-28",
                    "price_basis": "UNCACHED_STANDARD_ESTIMATE_NOT_BILLING",
                    "reservation_basis": "request_utf8_bytes_plus_1024_overhead_not_tokenizer_guarantee"}


class HttpxTransport:
    """Fixed HTTPS destination, no proxy environment/redirects/SDK retries.

    A supplied httpx transport is for offline tests. It cannot change the URL.
    Client/response ownership is per attempt, including timeout/cancellation.
    """
    def __init__(self, api_key, *, transport=None):
        if not isinstance(api_key, str) or not api_key or any(c.isspace() for c in api_key):
            raise ValueError("LLM_CREDENTIAL_REQUIRED")
        self._key, self._transport = api_key, transport

    async def send(self, payload, timeout):
        async with httpx.AsyncClient(transport=self._transport, trust_env=False,
                                    follow_redirects=False, timeout=timeout) as client:
            async with client.stream("POST", ENDPOINT, json=payload,
                                     headers={"Authorization": "Bearer " + self._key}) as response:
                chunks, size = [], 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > 1_048_576:
                        raise ValueError("LLM_RESPONSE_TOO_LARGE")
                    chunks.append(chunk)
                try:
                    body = strict_json(b"".join(chunks))
                except (ValueError, UnicodeError):
                    body = None
                return {"status": response.status_code, "body": body,
                        "request_id": _identifier(response.headers.get("x-request-id"))}


@dataclass
class Result:
    outcome: str
    value: object
    events: list
    budget: dict
    reason: str | None = None

    @property
    def decision_source(self):
        return "LLM" if self.outcome == "OK" else "NONE"


def _schema(model):
    if (not isinstance(model, type) or not issubclass(model, BaseModel)
            or model.model_config.get("extra") != "forbid"):
        raise ValueError("LLM_OUTPUT_MODEL_MUST_FORBID_EXTRA")
    schema = model.model_json_schema()
    def strict(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                if (node.get("additionalProperties") is not False
                        or set(node.get("required", [])) != set(node.get("properties", {}))):
                    raise ValueError("LLM_OUTPUT_MODEL_MUST_BE_CLOSED_AND_REQUIRED")
            for value in node.values():
                strict(value)
        elif isinstance(node, list):
            for value in node:
                strict(value)
    strict(schema)
    return schema


class Adapter:
    """Common primitive; future agent callers supply O-only input and output models.

    Local envelopes are bounded by the shared run call limit. They are NOT evidence
    of authenticated delivery until a caller persists them through its recorder.
    """
    def __init__(self, transport, budget, *, limits=Limits(), clock=time.monotonic):
        self.transport, self.budget, self.limits, self.clock = transport, budget, limits, clock
        self.producer = Producer("decision_llm", "zer48/1", {
            "clock_id": "llm-host", "clock_source": "UNKNOWN", "resolution_ms": None})
        self.events = []

    async def call(self, context, *, decision_id, instructions, observation,
                   output_model, prompt_version, target=None, causation_id=None):
        if (not isinstance(context, dict) or context.get("group") != "B2" or context.get("run_id") != self.budget.run_id
                or not isinstance(instructions, str) or not instructions.strip()
                or not isinstance(prompt_version, str) or not prompt_version.strip()
                or not isinstance(observation, dict) or forbidden_keys(observation)):
            raise ValueError("LLM_INPUT_OR_MODE_INVALID")
        context, target = copy.deepcopy(context), copy.deepcopy(target)
        observation = strict_json(canonical(observation))
        if forbidden_keys(observation):
            raise ValueError("LLM_INPUT_OR_MODE_INVALID")
        payload = {"model": MODEL, "store": False, "service_tier": "default", "tools": [],
                   "reasoning": {"effort": "none"}, "max_output_tokens": self.limits.max_output_tokens,
                   "instructions": instructions, "input": canonical(observation).decode(),
                   "text": {"format": {"type": "json_schema", "name": "zd_output", "strict": True,
                                       "schema": _schema(output_model)}}}
        encoded = canonical(payload)
        if len(encoded) > MAX_BYTES:
            raise ValueError("LLM_REQUEST_TOO_LARGE")
        prompt_hash, call_id = "sha256:" + hashlib.sha256(encoded).hexdigest(), new_id("cal")
        input_reserve = len(encoded) + 1024
        base = {"provider": "openai", "model": MODEL, "prompt_version": prompt_version,
                "prompt_sha256": prompt_hash, "latency_ms": 0, "outcome": "HTTP_ERROR",
                "usage": {"status": "UNKNOWN"}, "cost": {"usd": None, "status": "UNKNOWN", "price_ref": PRICE_REF}}
        # Validate the complete context before spending a reservation or making a request.
        Producer("decision_llm", "validation-only", self.producer.clock).event(
            context, "LLM_CALL", dict(base, attempt_no=1, retry_reason=None), "o.decision",
            target=target, decision_id=decision_id, call_id=call_id, causation_id=causation_id)
        started, events, reason = self.clock(), [], None
        for number in range(1, self.limits.attempts + 1):
            remaining = min(self.limits.deadline_s - (self.clock() - started), self.budget.remaining())
            if not math.isfinite(remaining) or not 0 < remaining <= self.limits.deadline_s:
                return Result("TIMEOUT", None, events, self.budget.summary(), "CALL_DEADLINE")
            self.budget.reserve(context["run_id"], input_reserve, self.limits.max_output_tokens)
            tick, usage, value, retryable = self.clock(), None, None, False
            metadata = dict(base, attempt_no=number, retry_reason=reason)
            cancelled = False
            try:
                response = await asyncio.wait_for(self.transport.send(copy.deepcopy(payload),
                    min(self.limits.timeout_s, remaining)), timeout=min(self.limits.timeout_s, remaining))
                if not isinstance(response, dict) or type(response.get("status")) is not int:
                    raise ValueError("INVALID_TRANSPORT_RECEIPT")
                body, status = response.get("body"), response["status"]
                usage = _usage(body)
                metadata["request_id"] = _identifier(response.get("request_id"))
                if status != 200:
                    error = body.get("error") if isinstance(body, dict) else None
                    code = error.get("code") if isinstance(error, dict) else None
                    reason = "HTTP_" + str(status)
                    retryable = status in {500, 502, 503, 504} or (status == 429 and code == "rate_limit_exceeded")
                    if isinstance(code, str) and code in FATAL_CODES:
                        retryable = False
                    metadata["outcome"] = "HTTP_ERROR"
                else:
                    value, reason = self._parse(body, output_model)
                    metadata["outcome"] = "OK"
                    metadata["response_id"] = _identifier(body.get("id"))
                    metadata["model_returned"] = body["model"]
                    metadata["model_revision"] = "UNKNOWN_NOT_INDEPENDENTLY_VERIFIED"
            except asyncio.CancelledError:
                metadata["outcome"], reason, cancelled = "TIMEOUT", "CANCELLED", True
            except (asyncio.TimeoutError, httpx.TimeoutException):
                metadata["outcome"], reason, retryable = "TIMEOUT", "TIMEOUT", True
            except httpx.NetworkError:
                metadata["outcome"], reason, retryable = "HTTP_ERROR", "NETWORK", True
            except ValueError as error:
                # Error strings are local fixed codes; never persist exception/provider text.
                metadata["outcome"] = "REFUSAL" if str(error) == "PROVIDER_REFUSAL" else "SCHEMA_INVALID"
                reason = "PROVIDER_REFUSAL" if metadata["outcome"] == "REFUSAL" else "INVALID_RESPONSE"
            except Exception:
                metadata["outcome"], reason = "HTTP_ERROR", "TRANSPORT_ERROR"
            self.budget.account(usage, input_reserve, self.limits.max_output_tokens)
            if self.budget.blocked:
                metadata["outcome"], reason, retryable, value = "SCHEMA_INVALID", "USAGE_RESERVATION_EXCEEDED", False, None
            if usage is not None:
                metadata["usage"] = dict(usage, status="COMPLETE")
                metadata["cost"] = {"usd": float(_cost(usage["input_tokens"], usage["output_tokens"])),
                                    "status": "ESTIMATE", "price_ref": PRICE_REF}
            elapsed = self.clock() - tick
            if not math.isfinite(elapsed) or elapsed < 0:
                metadata["outcome"], reason, retryable, value = "TIMEOUT", "CLOCK_INVALID", False, None
                elapsed = 0
            metadata.update(latency_ms=elapsed * 1000, reason_code=reason)
            event = self.producer.event(context, "LLM_CALL", metadata, "o.decision", target=target,
                decision_id=decision_id, call_id=call_id, causation_id=causation_id)
            events.append(event)
            self.events.append(event)
            if cancelled:
                raise asyncio.CancelledError
            if metadata["outcome"] == "OK" or not retryable or number == self.limits.attempts:
                return Result(metadata["outcome"], value, events, self.budget.summary(), reason)
            remaining = min(self.limits.deadline_s - (self.clock() - started), self.budget.remaining())
            if remaining <= self.limits.retry_delay_s:
                return Result("TIMEOUT", None, events, self.budget.summary(), "CALL_DEADLINE")
            await asyncio.sleep(self.limits.retry_delay_s)

    @staticmethod
    def _parse(body, output_model):
        if (not isinstance(body, dict) or body.get("status") != "completed" or body.get("error")
                or body.get("incomplete_details") or not isinstance(body.get("model"), str)
                or not re.fullmatch(re.escape(MODEL) + r"(?:-[0-9]{4}-[0-9]{2}-[0-9]{2})?", body["model"])):
            raise ValueError("RESPONSE_NOT_COMPLETE_OR_WRONG_MODEL")
        parts = []
        if not isinstance(body.get("output"), list):
            raise ValueError("OUTPUT_INVALID")
        for item in body["output"]:
            if not isinstance(item, dict):
                raise ValueError("OUTPUT_INVALID")
            if item.get("type") == "reasoning":
                continue
            if item.get("type") != "message" or item.get("role") != "assistant" or item.get("status") != "completed":
                raise ValueError("OUTPUT_MESSAGE_INVALID")
            if not isinstance(item.get("content"), list):
                raise ValueError("OUTPUT_CONTENT_INVALID")
            for part in item["content"]:
                if not isinstance(part, dict):
                    raise ValueError("OUTPUT_CONTENT_INVALID")
                if part.get("type") == "refusal":
                    raise ValueError("PROVIDER_REFUSAL")
                if part.get("type") != "output_text" or not isinstance(part.get("text"), str):
                    raise ValueError("OUTPUT_CONTENT_INVALID")
                parts.append(part["text"])
        if len(parts) != 1:
            raise ValueError("OUTPUT_MISSING_OR_AMBIGUOUS")
        return output_model.model_validate(strict_json(parts[0]), strict=True), None
