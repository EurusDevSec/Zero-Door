"""Bounded FUNCTIONAL_ONLY Nemesis sessions; never a recovery benchmark driver.

Only registry IDs leave the model. The existing CommandGuard constructs targets,
duration and concurrency; the existing signed worker remains the executor.
Nothing opens a client, spends tokens or starts a session at import.
"""
import asyncio
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import time
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field

from event_pipeline.contract import new_id
from event_pipeline.llm import BudgetExceeded
from nemesis.command_guard import CommandGuard, Refused, SQLI_TEMPLATE_IDS

PURPOSE = "FUNCTIONAL_ONLY_NOT_BENCHMARK"
PROMPT_VERSION = "zer19-registry-selector/1"
INSTRUCTIONS = """Select one existing ZERO DOOR local fixture template ID, or STOP.
Use only the supplied health observations and previous execution status. Cite
existing evidence IDs. Never invent a payload, target, command, intensity or URL.
STOP when health is unknown or unhealthy, or when another round is unnecessary.
This is a separate functional session, not a recovery comparison benchmark."""


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    template: Literal["STOP", "disclose-restricted", "benign-apparel", "benign-home", "benign-electronics"]
    evidence_ids: list[str] = Field(min_length=1, max_length=8)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def observation_valid(value, *, now=None):
    """A deliberately small O projection. No raw result, H oracle or free text."""
    if type(value) is not dict or set(value) != {"observed_at", "evidence"}:
        raise ValueError("OBSERVATION_SCHEMA")
    try:
        stamp = datetime.fromisoformat(value["observed_at"].replace("Z", "+00:00"))
        age = ((now or datetime.now(timezone.utc)) - stamp).total_seconds()
    except (ValueError, TypeError, AttributeError):
        raise ValueError("OBSERVATION_TIME") from None
    if stamp.tzinfo is None or not 0 <= age <= 60:
        raise ValueError("OBSERVATION_STALE")
    evidence = value["evidence"]
    if type(evidence) is not list or not 1 <= len(evidence) <= 8:
        raise ValueError("OBSERVATION_EVIDENCE")
    ids = set()
    for item in evidence:
        if (type(item) is not dict or set(item) != {"id", "health"}
                or type(item["id"]) is not str or not re.fullmatch(r"ev-[a-z0-9-]{1,48}", item["id"])
                or item["id"] in ids or item["health"] not in ("HEALTHY", "UNHEALTHY", "UNKNOWN")):
            raise ValueError("OBSERVATION_EVIDENCE")
        ids.add(item["id"])
    return deepcopy(value), ids


@dataclass(frozen=True)
class SessionLimits:
    max_rounds: int = 1
    duration_s: int = 120
    command_s: int = 1
    allowed_templates: tuple = tuple(sorted(SQLI_TEMPLATE_IDS))

    def __post_init__(self):
        for value, high in ((self.max_rounds, 3), (self.duration_s, 180), (self.command_s, 5)):
            if type(value) is not int or not 1 <= value <= high:
                raise ValueError("SESSION_LIMITS")
        if (type(self.allowed_templates) is not tuple or not self.allowed_templates
                or any(type(x) is not str or x not in SQLI_TEMPLATE_IDS for x in self.allowed_templates)
                or len(set(self.allowed_templates)) != len(self.allowed_templates)):
            raise ValueError("SESSION_TEMPLATES")


def result_valid(raw, command, max_sends):
    """Join the worker receipt, without interpreting disclosure as effect/recovery."""
    if (type(raw) is not dict or raw.get("commandId") != command["commandId"]
            or raw.get("source") != "chaos-worker" or raw.get("attackType") != "SQLI"
            or raw.get("status") not in ("SUCCESS", "FAILED", "REJECTED", "TIMEOUT")
            or type(raw.get("duration")) is not int or not 0 <= raw["duration"] <= 60_000):
        raise ValueError("EXECUTOR_RESULT_INVALID")
    if raw["status"] != "SUCCESS":
        return deepcopy(raw)
    detail = raw.get("details")
    sql = detail.get("sqli") if type(detail) is dict else None
    if (type(sql) is not dict or sql.get("templateId") != command["parameters"]["customParams"]["template"]
            or type(sql.get("sends")) is not list or not 1 <= len(sql["sends"]) <= max_sends):
        raise ValueError("EXECUTOR_RESULT_INVALID")
    for seq, item in enumerate(sql["sends"], 1):
        if (type(item) is not dict or type(item.get("seq")) is not int or item["seq"] != seq
                or item.get("requestId") != command["commandId"] + "/" + str(seq)
                or type(item.get("status")) is not int or item["status"] != 200
                or type(item.get("rows")) is not int or type(item.get("restrictedRows")) is not int
                or not 0 <= item["restrictedRows"] <= item["rows"]):
            raise ValueError("EXECUTOR_RESULT_INVALID")
    return deepcopy(raw)


class Session:
    """One owner, one task and one shared RunBudget; no retry/restart of sessions.

    stop() cancels observation/inference. Once an external command is dispatched,
    its existing worker deadline bounds it; stop never claims remote cancellation.
    No next command is sent while a previous outcome is unknown.
    """
    def __init__(self, *, purpose, guard, adapter, observe, execute, context,
                 limits=SessionLimits(), sink=None, clock=time.monotonic):
        if purpose != PURPOSE or not isinstance(guard, CommandGuard):
            raise ValueError("FUNCTIONAL_SESSION_REQUIRED")
        self.guard = CommandGuard(deepcopy(guard.policy))
        self.guard.enabled()
        self.context = deepcopy(context)
        if (self.context.get("group") != "B2" or adapter.budget.run_id != self.context.get("run_id")
                or any(self.context.get(k) != self.guard.policy["context"].get(k)
                       for k in ("run_id", "trial_id", "group"))):
            raise ValueError("SESSION_CONTEXT")
        # Validate the opt-in fixture capability without dispatching a command.
        for template in limits.allowed_templates:
            self.guard.command({"attackType": "SQLI", "template": template,
                                "durationSec": limits.command_s}, str(uuid.uuid4()))
        self.adapter, self.observe, self.execute = adapter, observe, execute
        self.limits, self.clock, self.sink = limits, clock, sink
        self.started = None
        self.task = None
        self.stopping = False
        self.phase = "NEW"
        self.records, self.rounds = [], 0

    def record(self, event, **data):
        item = dict(event=event, at=datetime.now(timezone.utc).isoformat(), **deepcopy(data))
        self.records.append(item)
        if self.sink is not None:
            self.sink(deepcopy(item))  # Recording failure stops before further effects.

    def remaining(self):
        elapsed = self.clock() - self.started
        return min(self.limits.duration_s - elapsed, self.adapter.budget.remaining()) if math.isfinite(elapsed) and elapsed >= 0 else 0

    def start(self):
        if self.task is not None:
            raise ValueError("SESSION_ALREADY_STARTED")
        self.started = self.clock()
        self.task = asyncio.create_task(self.run())
        return self.task

    def stop(self):
        self.stopping = True
        request_stop = getattr(self.execute, "request_stop", None)
        if request_stop is not None:
            request_stop()  # Prevent publication while the executor is still setting up.
        if self.task is not None and not self.task.done() and self.phase not in {"NEW", "EXECUTING"}:
            self.task.cancel()

    async def bounded(self, operation):
        remaining = self.remaining()
        if remaining <= 0:
            raise asyncio.TimeoutError
        return await asyncio.wait_for(operation(), timeout=remaining)

    async def run(self):
        reason = "MAX_ROUNDS"
        previous = None
        try:
            self.record("SESSION_STARTED", purpose=PURPOSE, benchmark_eligible=False)
            for number in range(1, self.limits.max_rounds + 1):
                if self.stopping:
                    reason = "CANCELLED"
                    break
                if self.adapter.budget.calls >= self.adapter.budget.max_calls:
                    reason = "CALL_BUDGET"
                    break
                if number > 1:
                    # The existing durable admission ledger has a six-second
                    # minimum interval. Preserve it; don't turn fast results into
                    # immediate redispatch or relax the ledger for this caller.
                    self.phase = "PACING"
                    await self.bounded(lambda: asyncio.sleep(6))
                self.phase = "OBSERVING"
                observation, ids = observation_valid(await self.bounded(self.observe))
                self.record("OBSERVATION", round=number, observation=observation, sha256=digest(observation))
                if any(e["health"] != "HEALTHY" for e in observation["evidence"]):
                    reason = "UNHEALTHY_OR_UNKNOWN"
                    break
                self.phase = "PLANNING"
                decision = new_id("dec")
                before = len(self.adapter.events)
                try:
                    response = await self.bounded(lambda: self.adapter.call(self.context,
                        decision_id=decision, instructions=INSTRUCTIONS,
                        observation=dict(observation, previous_execution_status=previous,
                                         allowed_templates=list(self.limits.allowed_templates)),
                        output_model=Plan, prompt_version=PROMPT_VERSION))
                finally:
                    for event in self.adapter.events[before:]:
                        self.record("MODEL_TRACE", trace=event)
                if response.outcome != "OK":
                    reason = "MODEL_" + response.outcome
                    break
                if not response.budget["cost_estimate_complete"]:
                    reason = "MODEL_USAGE_UNKNOWN"
                    break
                plan = response.value
                if (not plan.evidence_ids or len(set(plan.evidence_ids)) != len(plan.evidence_ids)
                        or not set(plan.evidence_ids) <= ids):
                    raise ValueError("PLAN_EVIDENCE")
                self.record("PLAN", round=number, decision_id=decision,
                            decision_source="LLM", plan=plan.model_dump())
                if plan.template == "STOP":
                    reason = "MODEL_STOP"
                    break
                if plan.template not in self.limits.allowed_templates:
                    raise ValueError("PLAN_NOT_ALLOWED")
                command = self.guard.command({"attackType": "SQLI", "template": plan.template,
                    "durationSec": self.limits.command_s}, str(uuid.uuid4()))
                # Reserve enough time for the existing worker deadline and its result.
                if self.remaining() < self.limits.command_s + 15:
                    reason = "INSUFFICIENT_EXECUTION_WINDOW"
                    break
                if self.stopping:
                    reason = "CANCELLED"
                    break
                self.record("GUARD_ACCEPTED", command_id=command["commandId"], decision_id=decision)
                self.record("DISPATCH_INTENT", round=number, command=command, decision_id=decision)
                self.phase = "EXECUTING"
                raw = await self.bounded(lambda: self.execute(command))
                raw = result_valid(raw, command, self.guard.policy["sqli"]["maxSends"])
                self.rounds += 1
                previous = raw["status"]
                self.record("EXECUTOR_RESULT", round=number, raw=raw, sha256=digest(raw),
                            effect="NOT_EVALUATED", remote_cancel_confirmed=False)
                if self.stopping or previous != "SUCCESS":
                    reason = "CANCELLED" if self.stopping else "EXECUTOR_" + previous
                    break
        except asyncio.CancelledError:
            reason = "CANCELLED"
        except asyncio.TimeoutError:
            reason = "SESSION_DEADLINE_OUTCOME_UNKNOWN" if self.phase == "EXECUTING" else "SESSION_DEADLINE"
        except BudgetExceeded:
            reason = "CALL_TOKEN_COST_BUDGET"
        except (ValueError, Refused) as error:
            if isinstance(error, Refused) and error.reason == "CANCELLED_BEFORE_SEND":
                reason = "CANCELLED_BEFORE_SEND"
            else:
                reason = "EXECUTOR_RESULT_UNKNOWN_OR_INVALID" if self.phase == "EXECUTING" else "VALIDATION_FAILED"
        except Exception:
            reason = "EXECUTION_OUTCOME_UNKNOWN" if self.phase == "EXECUTING" else "SESSION_FAILED"
        finally:
            self.phase = "STOPPED"
            self.record("SESSION_STOPPED", reason=reason, completed_rounds=self.rounds,
                        budget=self.adapter.budget.summary())
        return self.receipt(reason)

    def receipt(self, reason):
        return dict(version="nemesis-functional/1", purpose=PURPOSE, benchmark_eligible=False,
                    run_id=self.context["run_id"], stop_reason=reason, completed_rounds=self.rounds,
                    budget=self.adapter.budget.summary(), records=deepcopy(self.records))
