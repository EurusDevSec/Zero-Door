"""ZER-48: fake/MockTransport only; never provider, Kafka, Kubernetes or SQLi traffic."""
import asyncio
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import new_id, validate
from event_pipeline.llm import Adapter, BudgetExceeded, HttpxTransport, Limits, MODEL, RunBudget


class Summary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification: Literal["NORMAL", "UNKNOWN"]
    evidence_ids: list[Literal["ev-01"]] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


def response(status=200, *, body=None):
    if body is None:
        body = {"id": "resp_offline", "model": MODEL, "status": "completed",
                "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [
                    {"type": "output_text", "text": json.dumps({"classification": "NORMAL",
                        "evidence_ids": ["ev-01"], "confidence": 0.9})}]}],
                "usage": {"input_tokens": 100, "output_tokens": 30, "total_tokens": 130}}
    return {"status": status, "body": body, "request_id": "req_offline"}


class Fake:
    def __init__(self, replies=None):
        self.replies = list(replies or [response()])
        self.requests = []

    async def send(self, payload, timeout):
        self.requests.append(copy.deepcopy(payload))
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return copy.deepcopy(item)


class AdapterCases(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.context = {"run_id": new_id("run"), "trial_id": new_id("trl"), "group": "B2",
                        "method_version": "zer48-offline", "config_ref": "sha256:" + "1" * 64,
                        "incident_id": new_id("inc")}
        self.args = {"decision_id": new_id("dec"), "instructions": "Summarize supplied health evidence. No tools or actions.",
                     "observation": {"service": "fixture", "evidence_ids": ["ev-01"], "healthy": True},
                     "output_model": Summary, "prompt_version": "zer48-health/1", "causation_id": new_id("evt")}

    def budget(self, **overrides):
        values = dict(max_calls=6, max_reserved_tokens=100_000, max_estimated_usd="1")
        values.update(overrides)
        return RunBudget(self.context["run_id"], **values)

    def adapter(self, fake=None, budget=None, **limits):
        return Adapter(fake or Fake(), budget or self.budget(), limits=Limits(retry_delay_s=0, **limits))

    async def test_success_is_structured_trace_and_accumulated_run_usage(self):
        fake = Fake([response(), response()])
        adapter = self.adapter(fake)
        first = await adapter.call(self.context, **self.args)
        second = await adapter.call(self.context, **dict(self.args, decision_id=new_id("dec")))
        self.assertEqual((first.outcome, first.decision_source), ("OK", "LLM"))
        self.assertEqual(first.value.classification, "NORMAL")
        self.assertEqual(second.budget["known_input_tokens"], 200)
        self.assertEqual(second.budget["known_output_tokens"], 60)
        self.assertAlmostEqual(second.budget["known_cost_estimate_usd"], .00005)
        for event in adapter.events:
            self.assertIsNone(validate(event))
            self.assertEqual(event["decision_id"], self.args["decision_id"] if event is adapter.events[0] else second.events[0]["decision_id"])
            self.assertEqual(event["incident_id"], self.context["incident_id"])
            self.assertEqual(event["payload"]["request_id"], "req_offline")
            self.assertEqual(event["payload"]["model_revision"], "UNKNOWN_NOT_INDEPENDENTLY_VERIFIED")
        self.assertFalse(fake.requests[0]["store"])
        self.assertEqual(fake.requests[0]["tools"], [])
        self.assertEqual(fake.requests[0]["max_output_tokens"], 512)

    async def test_retry_keeps_call_decision_and_prompt_identity(self):
        fake = Fake([response(429, body={"error": {"code": "rate_limit_exceeded"}}), response()])
        result = await self.adapter(fake).call(self.context, **self.args)
        self.assertEqual(result.outcome, "OK")
        self.assertEqual(len(fake.requests), 2)
        self.assertEqual(fake.requests[0], fake.requests[1])
        self.assertEqual(result.events[0]["call_id"], result.events[1]["call_id"])
        self.assertEqual(result.events[1]["payload"]["attempt_no"], 2)
        self.assertEqual(result.events[1]["payload"]["retry_reason"], "HTTP_429")
        self.assertFalse(result.budget["cost_estimate_complete"])
        self.assertEqual(result.budget["unknown_usage_attempts"], 1)

    async def test_fatal_errors_do_not_retry_or_invent_llm_success(self):
        for status, code in [(401, "invalid_api_key"), (403, "denied"), (429, "insufficient_quota"),
                             (429, "project_spend_limit_exceeded"), (429, "unknown"), (400, "bad_request"),
                             (500, "insufficient_quota")]:
            with self.subTest(status=status, code=code):
                fake = Fake([response(status, body={"error": {"code": code, "message": "sk-secret"}})])
                result = await self.adapter(fake).call(self.context, **self.args)
                self.assertEqual((len(fake.requests), result.outcome, result.decision_source), (1, "HTTP_ERROR", "NONE"))
                self.assertNotIn("sk-secret", json.dumps(result.events))

    async def test_schema_refusal_incomplete_and_wrong_model_are_final(self):
        cases = []
        for field, value in [("status", "incomplete"), ("model", "another-model"), ("error", {"message": "sk-secret"})]:
            item = response(); item["body"][field] = value; cases.append(item)
        item = response(); item["body"]["output"][0]["content"] = [{"type": "refusal", "refusal": "sk-secret"}]; cases.append(item)
        for text in ['{"classification":"NORMAL","evidence_ids":["ev-01"],"confidence":NaN}',
                     '{"classification":"NORMAL","classification":"UNKNOWN","evidence_ids":["ev-01"],"confidence":0.9}',
                     '{"classification":"NORMAL","evidence_ids":["wrong"],"confidence":0.9}',
                     '{"classification":"NORMAL","evidence_ids":["ev-01"],"confidence":"0.9"}',
                     '{"classification":"NORMAL","evidence_ids":["ev-01"],"confidence":0.9,"extra":true}']:
            item = response(); item["body"]["output"][0]["content"][0]["text"] = text; cases.append(item)
        for item in cases:
            with self.subTest(item=item):
                fake = Fake([item]); result = await self.adapter(fake).call(self.context, **self.args)
                self.assertEqual(len(fake.requests), 1)
                self.assertIn(result.outcome, {"SCHEMA_INVALID", "REFUSAL"})
                self.assertIsNone(result.value)
                self.assertNotIn("sk-secret", json.dumps(result.events))

    async def test_invalid_or_missing_usage_remains_unknown_without_refund(self):
        for usage in [None, {}, {"input_tokens": True, "output_tokens": 30, "total_tokens": 31},
                      {"input_tokens": 1, "output_tokens": 2, "total_tokens": 9}]:
            with self.subTest(usage=usage):
                item = response(); item["body"]["usage"] = usage
                result = await self.adapter(Fake([item])).call(self.context, **self.args)
                self.assertEqual(result.outcome, "OK")  # Valid inference, NOT complete accounting.
                self.assertEqual(result.events[0]["payload"]["cost"]["usd"], None)
                self.assertFalse(result.budget["cost_estimate_complete"])
                self.assertEqual(result.budget["unknown_usage_attempts"], 1)
                self.assertGreater(result.budget["reserved_tokens"], 0)

    async def test_observed_usage_over_reservation_blocks_next_dispatch(self):
        item = response(); item["body"]["usage"] = {"input_tokens": 10, "output_tokens": 513, "total_tokens": 523}
        fake = Fake([item]); adapter = self.adapter(fake)
        result = await adapter.call(self.context, **self.args)
        self.assertEqual(result.reason, "USAGE_RESERVATION_EXCEEDED")
        self.assertEqual(result.decision_source, "NONE")
        with self.assertRaises(BudgetExceeded):
            await adapter.call(self.context, **self.args)
        self.assertEqual(len(fake.requests), 1)

    async def test_call_token_and_estimated_cost_limits_reserve_before_dispatch(self):
        for overrides in [{"max_calls": 1}, {"max_reserved_tokens": 1}, {"max_estimated_usd": ".000000001"}]:
            with self.subTest(overrides=overrides):
                fake = Fake([response(), response()]); adapter = self.adapter(fake, self.budget(**overrides))
                if overrides == {"max_calls": 1}:
                    await adapter.call(self.context, **self.args)
                before = len(fake.requests)
                with self.assertRaises(BudgetExceeded):
                    await adapter.call(self.context, **self.args)
                self.assertEqual(len(fake.requests), before)

    async def test_nonblocking_and_cancel_propagates_with_unknown_attempt_trace(self):
        entered, release = asyncio.Event(), asyncio.Event()
        class Wait:
            async def send(self, payload, timeout):
                entered.set()
                await release.wait()
                return response()
        adapter = self.adapter(Wait())
        task = asyncio.create_task(adapter.call(self.context, **self.args))
        await asyncio.wait_for(entered.wait(), 1)
        await asyncio.sleep(0)  # Another coroutine runs while the request is pending.
        self.assertFalse(task.done())
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(adapter.events[0]["payload"]["reason_code"], "CANCELLED")
        self.assertEqual(adapter.budget.summary()["unknown_usage_attempts"], 1)

    async def test_timeout_is_bounded_to_two_attempts(self):
        fake = Fake([asyncio.TimeoutError(), asyncio.TimeoutError()])
        result = await self.adapter(fake).call(self.context, **self.args)
        self.assertEqual(result.outcome, "TIMEOUT")
        self.assertEqual(len(fake.requests), 2)
        self.assertEqual(result.budget["unknown_usage_attempts"], 2)

    async def test_shared_budget_applies_across_adapters_and_concurrent_calls(self):
        budget = self.budget(max_calls=1)
        fake = Fake([response()])
        a, b = self.adapter(fake, budget), self.adapter(fake, budget)
        values = await asyncio.gather(a.call(self.context, **self.args), b.call(self.context, **self.args), return_exceptions=True)
        self.assertEqual(len(fake.requests), 1)
        self.assertEqual(sum(isinstance(v, BudgetExceeded) for v in values), 1)

    async def test_run_deadline_bounds_a_pending_request(self):
        clock = [0.0]
        class Wait:
            async def send(self, payload, timeout):
                clock[0] = .03  # Run expires while this attempt is pending.
                await asyncio.Event().wait()
        adapter = self.adapter(Wait(), self.budget(duration_s=.02, clock=lambda: clock[0]))
        result = await asyncio.wait_for(adapter.call(self.context, **self.args), 1)
        self.assertEqual(result.outcome, "TIMEOUT")
        self.assertEqual(adapter.budget.summary()["attempts_dispatched"], 1)

    async def test_retry_backoff_cannot_outlive_shared_run_deadline(self):
        clock, sleeps = [0.0], []
        class Retry:
            async def send(self, payload, timeout):
                clock[0] = .09
                return response(429, body={"error": {"code": "rate_limit_exceeded"}})
        async def sleep(seconds):
            sleeps.append(seconds)
            clock[0] += seconds
        budget = self.budget(duration_s=.1, clock=lambda: clock[0])
        adapter = Adapter(Retry(), budget, limits=Limits(retry_delay_s=.5), clock=lambda: clock[0])
        with patch("event_pipeline.llm.asyncio.sleep", side_effect=sleep):
            result = await adapter.call(self.context, **self.args)
        self.assertEqual(sleeps, [])
        self.assertEqual(result.outcome, "TIMEOUT")
        self.assertEqual(budget.summary()["attempts_dispatched"], 1)

    async def test_exponent_overflow_is_not_valid_model_output(self):
        class Number(BaseModel):
            model_config = ConfigDict(extra="forbid")
            value: float
        item = response()
        item["body"]["output"][0]["content"][0]["text"] = '{"value":1e999}'
        result = await self.adapter(Fake([item])).call(self.context, **dict(self.args, output_model=Number))
        self.assertEqual(result.outcome, "SCHEMA_INVALID")
        self.assertIsNone(result.value)
        self.assertEqual(result.budget["known_input_tokens"], 100)

    async def test_context_is_pinned_before_await(self):
        entered, release = asyncio.Event(), asyncio.Event()
        class Wait:
            async def send(self, payload, timeout):
                entered.set(); await release.wait(); return response()
        adapter = self.adapter(Wait())
        original = copy.deepcopy(self.context)
        task = asyncio.create_task(adapter.call(self.context, **self.args))
        await entered.wait()
        self.context["trial_id"] = new_id("trl")
        release.set()
        result = await task
        self.assertEqual(result.events[0]["trial_id"], original["trial_id"])

    async def test_invalid_mode_context_hidden_input_and_size_fail_before_dispatch(self):
        fake = Fake(); adapter = self.adapter(fake)
        for group in ["B0", "B1", "BM", "B3"]:
            with self.subTest(group=group), self.assertRaises(ValueError):
                await adapter.call(dict(self.context, group=group), **self.args)
        for overrides in [{"observation": {"cause": "hidden-H-plane"}}, {"observation": {"text": "x" * 9000}},
                          {"decision_id": "dec_invalid"}]:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                await adapter.call(self.context, **dict(self.args, **overrides))
        self.assertEqual(fake.requests, [])

    async def test_loose_or_optional_default_output_schema_is_rejected(self):
        class Loose(BaseModel):
            text: str
        class Default(BaseModel):
            model_config = ConfigDict(extra="forbid")
            text: str = "default"
        fake = Fake()
        for model in [Loose, Default]:
            with self.assertRaises(ValueError):
                await self.adapter(fake).call(self.context, **dict(self.args, output_model=model))
        self.assertEqual(fake.requests, [])

    async def test_json_normalized_observation_is_checked_for_hidden_fields(self):
        fake = Fake(); adapter = self.adapter(fake)
        with self.assertRaises(ValueError):
            await adapter.call(self.context, **dict(self.args, observation={"items": ({"cause": "hidden-H-plane"},)}))
        self.assertEqual(fake.requests, [])
        self.assertEqual(adapter.budget.summary()["attempts_dispatched"], 0)

    async def test_invalid_limit_numbers_are_rejected(self):
        for args in [{"attempts": True}, {"attempts": 3}, {"timeout_s": float("nan")}, {"retry_delay_s": -1}]:
            with self.assertRaises(ValueError):
                Limits(**args)
        for args in [{"max_calls": True}, {"max_reserved_tokens": 0}, {"max_estimated_usd": "NaN"},
                     {"max_estimated_usd": True}, {"duration_s": float("inf")}]:
            with self.assertRaises(ValueError):
                self.budget(**args)


class TransportCases(unittest.IsolatedAsyncioTestCase):
    async def test_real_httpx_request_shape_and_only_allowlisted_response_fields(self):
        seen = []
        async def handle(request):
            seen.append(request)
            return httpx.Response(200, json=response()["body"], headers={"x-request-id": "req_offline", "set-cookie": "sk-secret"})
        transport = HttpxTransport("offline-key", transport=httpx.MockTransport(handle))
        reply = await transport.send({"model": MODEL, "store": False}, .5)
        self.assertEqual(str(seen[0].url), "https://api.openai.com/v1/responses")
        self.assertEqual(seen[0].headers["authorization"], "Bearer offline-key")
        self.assertNotIn("set-cookie", reply)
        self.assertEqual(reply["request_id"], "req_offline")

    async def test_redirect_is_not_followed_and_body_is_bounded(self):
        calls = []
        async def redirect(request):
            calls.append(request)
            return httpx.Response(302, headers={"location": "https://outside.invalid/"})
        reply = await HttpxTransport("offline-key", transport=httpx.MockTransport(redirect)).send({}, .5)
        self.assertEqual(reply["status"], 302)
        self.assertEqual(len(calls), 1)
        async def huge(request):
            return httpx.Response(200, content=b"x" * 1_048_577)
        with self.assertRaises(ValueError):
            await HttpxTransport("offline-key", transport=httpx.MockTransport(huge)).send({}, .5)

    async def test_response_and_client_close_when_outer_task_is_cancelled(self):
        entered, released = asyncio.Event(), asyncio.Event()
        closed = []
        class Stream(httpx.AsyncByteStream):
            async def __aiter__(self):
                entered.set(); await released.wait(); yield b"{}"
            async def aclose(self):
                closed.append("response")
        class Mock(httpx.MockTransport):
            async def aclose(self):
                closed.append("client")
        transport = HttpxTransport("offline-key", transport=Mock(lambda _: httpx.Response(200, stream=Stream())))
        task = asyncio.create_task(transport.send({}, .5))
        await entered.wait(); task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertIn("response", closed)
        self.assertIn("client", closed)


class ProbeCases(unittest.IsolatedAsyncioTestCase):
    async def test_probe_uses_actual_adapter_and_marks_fake_receipt(self):
        spec = importlib.util.spec_from_file_location("zer48_probe", ROOT / "infrastructure/scripts/verify_llm_adapter.py")
        probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(probe)
        receipt = await probe.verify(False)
        self.assertEqual(receipt["evidence_kind"], "OFFLINE_SIMULATED")
        self.assertEqual(receipt["budget"]["attempts_dispatched"], 1)
        self.assertEqual(receipt["verdict"], "PASS_ADAPTER_SYNTHETIC")
        self.assertEqual(receipt["events"][0]["payload"]["outcome"], "OK")
        self.assertIsNone(validate(receipt["events"][0]))
        self.assertEqual(receipt["config"]["new_lab_requests"], 0)
        self.assertEqual(probe.clean({"error": "sk-secret123 and a-test-key"}, "a-test-key"),
                         {"error": "[REDACTED] and [REDACTED]"})


if __name__ == "__main__":
    unittest.main()
