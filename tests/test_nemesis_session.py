"""ZER-19: actual shared adapter/session with fake model/executor; zero network."""
import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import forbidden_keys, new_id, validate
from event_pipeline.llm import Adapter, Limits, MODEL, RunBudget
from nemesis.command_guard import CommandGuard
from nemesis.session import PURPOSE, Plan, Session, SessionLimits, result_valid


def observation(health="HEALTHY"):
    return {"observed_at": datetime.now(timezone.utc).isoformat(),
            "evidence": [{"id": "ev-health-01", "health": health}]}


def reply(plan=None, *, status=200, body=None):
    if body is None:
        body = {"status": "completed", "model": MODEL, "id": "resp_offline",
                "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
                "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": json.dumps(
                    plan or {"template": "benign-apparel", "evidence_ids": ["ev-health-01"], "stop_reason": "NONE"})}]}]}
    return {"status": status, "body": body, "request_id": "req_offline"}


def result(command):
    return {"commandId": command["commandId"], "source": "chaos-worker", "attackType": "SQLI",
            "duration": 100, "status": "SUCCESS", "details": {"sqli": {
                "templateId": command["parameters"]["customParams"]["template"],
                "sends": [{"seq": 1, "requestId": command["commandId"] + "/1",
                           "status": 200, "rows": 2, "restrictedRows": 0}]}}}


class Fake:
    def __init__(self, responses=None):
        self.responses = list(responses or [reply()])
        self.requests = []

    async def send(self, payload, timeout):
        self.requests.append(deepcopy(payload))
        item = self.responses[min(len(self.requests) - 1, len(self.responses) - 1)]
        if isinstance(item, Exception):
            raise item
        return deepcopy(item)


class SessionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ctx = dict(run_id=new_id("run"), trial_id=new_id("trl"), group="B2",
                        incident_id=new_id("inc"), method_version="zer19-functional/1", config_ref="sha256:" + "a" * 64)
        self.policy = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())["policy"]
        self.policy["context"] = {k: self.ctx[k] for k in ("run_id", "trial_id", "group")}
        self.policy["sqli"] = {"enabled": True,
            "endpoint": "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search",
            "maxSends": 2, "maxCommandSec": 5}
        self.sent = []

    def session(self, fake=None, *, calls=3, budget_duration=180, limits=None, observe=None, execute=None):
        budget = RunBudget(self.ctx["run_id"], max_calls=calls, max_reserved_tokens=30_000,
                           max_estimated_usd=.005, duration_s=budget_duration)
        self.fake = fake or Fake()
        self.adapter = Adapter(self.fake, budget, limits=Limits(attempts=1, timeout_s=.1, deadline_s=.2,
                                                              retry_delay_s=0, max_output_tokens=256))
        async def default_observe():
            return observation()
        async def default_execute(command):
            self.sent.append(deepcopy(command))
            return result(command)
        return Session(purpose=PURPOSE, guard=CommandGuard(self.policy), adapter=self.adapter,
            observe=observe or default_observe, execute=execute or default_execute, context=self.ctx,
            limits=limits or SessionLimits())

    async def test_success_joins_observation_plan_guard_command_result_trace(self):
        session = self.session()
        receipt = await session.start()
        self.assertEqual(("MAX_ROUNDS", 1), (receipt["stop_reason"], receipt["completed_rounds"]))
        self.assertFalse(receipt["benchmark_eligible"])
        self.assertEqual(1, receipt["budget"]["attempts_dispatched"])
        self.assertEqual(100, receipt["budget"]["known_input_tokens"])
        events = {e["event"]: e for e in receipt["records"]}
        self.assertEqual(events["PLAN"]["decision_id"], events["DISPATCH_INTENT"]["decision_id"])
        self.assertEqual(events["GUARD_ACCEPTED"]["command_id"], self.sent[0]["commandId"])
        self.assertEqual(events["EXECUTOR_RESULT"]["raw"]["commandId"], self.sent[0]["commandId"])
        self.assertEqual("NOT_EVALUATED", events["EXECUTOR_RESULT"]["effect"])
        self.assertEqual(1, self.sent[0]["parameters"]["concurrency"])
        self.assertEqual(self.policy["sqli"]["endpoint"], self.sent[0]["target"]["url"])
        self.assertIsNone(validate(self.adapter.events[0]))

    async def test_next_round_uses_only_summary_of_result_and_accumulates_budget(self):
        receipt = await self.session(limits=SessionLimits(max_rounds=2)).start()
        self.assertEqual((2, 2), (receipt["completed_rounds"], receipt["budget"]["attempts_dispatched"]))
        second = json.loads(self.fake.requests[1]["input"])
        self.assertEqual("SUCCESS", second["previous_execution_status"])
        self.assertNotIn("details", second)
        self.assertNotIn("restrictedRows", json.dumps(second))
        self.assertNotEqual(self.sent[0]["commandId"], self.sent[1]["commandId"])

    async def test_call_budget_stops_next_round_without_reset(self):
        receipt = await self.session(calls=1, limits=SessionLimits(max_rounds=3)).start()
        self.assertEqual("CALL_BUDGET", receipt["stop_reason"])
        self.assertEqual((1, 1), (len(self.fake.requests), len(self.sent)))

    async def test_stop_proposal_never_dispatches(self):
        receipt = await self.session(Fake([reply({"template": "STOP", "evidence_ids": ["ev-health-01"],
                                                  "stop_reason": "UNSPECIFIED"})])).start()
        self.assertEqual("MODEL_STOP", receipt["stop_reason"])
        self.assertEqual([], self.sent)

    async def test_v2_request_carries_task_and_versions(self):
        receipt = await self.session(limits=SessionLimits(required_rounds=1)).start()
        self.assertEqual(("MAX_ROUNDS", 1), (receipt["stop_reason"], receipt["completed_rounds"]))
        self.assertEqual("nemesis-functional/2", receipt["version"])
        self.assertEqual("zer19-registry-selector/2", self.adapter.events[0]["payload"]["prompt_version"])
        sent = json.loads(self.fake.requests[0]["input"])
        self.assertEqual({"purpose": PURPOSE, "required_rounds": 1, "completed_rounds": 0}, sent["task"])
        self.assertEqual({"observed_at", "evidence", "previous_execution_status", "allowed_templates", "task"}, set(sent))
        self.assertFalse(forbidden_keys(sent))
        self.assertIn("stop_reason", self.fake.requests[0]["text"]["format"]["schema"]["required"])

    async def test_next_round_task_carries_actual_completed_count(self):
        await self.session(limits=SessionLimits(max_rounds=2, required_rounds=2)).start()
        counts = [json.loads(r["input"])["task"]["completed_rounds"] for r in self.fake.requests]
        self.assertEqual([0, 1], counts)

    async def test_stop_reason_is_recorded_claim_never_counted_rounds(self):
        # ROUNDS_COMPLETE contradicts required=1/completed=0: kept as the model's claim, still MODEL_STOP.
        for reason in ("ROUNDS_COMPLETE", "NO_SUITABLE_TEMPLATE", "UNSPECIFIED"):
            with self.subTest(reason=reason):
                plan = {"template": "STOP", "evidence_ids": ["ev-health-01"], "stop_reason": reason}
                receipt = await self.session(Fake([reply(plan)]), limits=SessionLimits(required_rounds=1)).start()
                self.assertEqual(("MODEL_STOP", 0), (receipt["stop_reason"], receipt["completed_rounds"]))
                self.assertEqual(plan, next(e["plan"] for e in receipt["records"] if e["event"] == "PLAN"))
                self.assertEqual([], self.sent)

    async def test_stop_reason_schema_violations_are_schema_invalid(self):
        for plan in [{"template": "STOP", "evidence_ids": ["ev-health-01"], "stop_reason": "NONE"},
                     {"template": "benign-apparel", "evidence_ids": ["ev-health-01"], "stop_reason": "ROUNDS_COMPLETE"},
                     {"template": "STOP", "evidence_ids": ["ev-health-01"]},
                     {"template": "STOP", "evidence_ids": ["ev-health-01"], "stop_reason": "HEALTHY"},
                     {"template": "STOP", "evidence_ids": ["ev-health-01"], "stop_reason": None}]:
            with self.subTest(plan=plan):
                receipt = await self.session(Fake([reply(plan)])).start()
                self.assertEqual("MODEL_SCHEMA_INVALID", receipt["stop_reason"])
                self.assertEqual("SCHEMA_INVALID", self.adapter.events[0]["payload"]["outcome"])
                self.assertNotIn("PLAN", [e["event"] for e in receipt["records"]])
                self.assertEqual([], self.sent)

    async def test_missing_usage_stops_without_executor_or_false_zero_cost(self):
        response = reply()
        response["body"].pop("usage")
        receipt = await self.session(Fake([response])).start()
        self.assertEqual("MODEL_USAGE_UNKNOWN", receipt["stop_reason"])
        self.assertEqual(1, receipt["budget"]["unknown_usage_attempts"])
        self.assertFalse(receipt["budget"]["cost_estimate_complete"])
        self.assertEqual([], self.sent)

    async def test_bad_model_schema_or_evidence_or_restricted_subset_never_dispatches(self):
        ok = {"evidence_ids": ["ev-health-01"], "stop_reason": "NONE"}
        for plan, outcome in [(dict(ok, template="HTTP_FLOOD"), "MODEL_SCHEMA_INVALID"),
                              (dict(ok, template="benign-apparel", target="x"), "MODEL_SCHEMA_INVALID"),
                              (dict(ok, template="benign-apparel", evidence_ids=["ev-missing"]), "VALIDATION_FAILED"),
                              (dict(ok, template="benign-apparel", evidence_ids=["ev-health-01"] * 2), "VALIDATION_FAILED"),
                              (dict(ok, template="disclose-restricted"), "VALIDATION_FAILED")]:
            with self.subTest(plan=plan):
                receipt = await self.session(Fake([reply(plan)]), limits=SessionLimits(
                    allowed_templates=("benign-apparel",))).start()
                self.assertEqual(outcome, receipt["stop_reason"])
                self.assertEqual([], self.sent)

    async def test_429_timeout_refusal_do_not_fallback_or_retry(self):
        cases = [reply(status=429, body={"error": {"code": "rate_limit_exceeded"}}),
                 asyncio.TimeoutError(), reply(body={"status": "completed", "model": MODEL,
                    "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [{"type": "refusal", "refusal": "no"}]}]})]
        for response in cases:
            with self.subTest(response=response):
                receipt = await self.session(Fake([response])).start()
                self.assertTrue(receipt["stop_reason"].startswith("MODEL_"))
                self.assertEqual(1, len(self.fake.requests))
                self.assertEqual([], self.sent)

    async def test_missing_stale_unhealthy_evidence_stops_before_model(self):
        old = observation()
        old["observed_at"] = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
        for value in [{}, old, observation("UNKNOWN"), observation("UNHEALTHY"),
                      dict(observation(), expected_action="x")]:
            async def observe():
                return value
            receipt = await self.session(observe=observe).start()
            self.assertIn(receipt["stop_reason"], {"VALIDATION_FAILED", "UNHEALTHY_OR_UNKNOWN"})
            self.assertEqual([], self.fake.requests)

    async def test_cancel_pending_model_is_traced_and_budget_retained(self):
        entered = asyncio.Event()
        class Pending(Fake):
            async def send(self, payload, timeout):
                entered.set()
                await asyncio.Event().wait()
        session = self.session(Pending())
        task = session.start()
        await asyncio.wait_for(entered.wait(), 1)
        session.stop()
        receipt = await task
        self.assertEqual("CANCELLED", receipt["stop_reason"])
        self.assertEqual((1, 1), (receipt["budget"]["attempts_dispatched"], receipt["budget"]["unknown_usage_attempts"]))
        trace = next(e["trace"] for e in receipt["records"] if e["event"] == "MODEL_TRACE")
        self.assertEqual("CANCELLED", trace["payload"]["reason_code"])
        self.assertEqual([], self.sent)

    async def test_stop_before_first_tick_still_writes_terminal_receipt(self):
        session = self.session()
        task = session.start()
        session.stop()
        receipt = await task
        self.assertEqual("CANCELLED", receipt["stop_reason"])
        self.assertEqual([], self.fake.requests)

    async def test_stop_during_execution_drains_bounded_command_no_next_round(self):
        entered, finish = asyncio.Event(), asyncio.Event()
        async def execute(command):
            entered.set()
            await finish.wait()
            self.sent.append(command)
            return result(command)
        session = self.session(execute=execute, limits=SessionLimits(max_rounds=3))
        task = session.start()
        await asyncio.wait_for(entered.wait(), 1)
        session.stop()
        self.assertFalse(task.done())
        finish.set()
        receipt = await task
        self.assertEqual(("CANCELLED", 1), (receipt["stop_reason"], receipt["completed_rounds"]))
        self.assertEqual(1, len(self.fake.requests))

    async def test_failed_missing_or_wrong_result_stops_without_next_round(self):
        for mode in ["missing", "wrong-id", "failed", "bad-sample"]:
            async def execute(command):
                raw = result(command)
                if mode == "missing":
                    raise TimeoutError()
                if mode == "wrong-id":
                    raw["commandId"] = "wrong"
                if mode == "failed":
                    raw["status"] = "FAILED"
                if mode == "bad-sample":
                    raw["details"]["sqli"]["sends"][0]["status"] = 503
                return raw
            receipt = await self.session(execute=execute, limits=SessionLimits(max_rounds=3)).start()
            self.assertNotEqual("MAX_ROUNDS", receipt["stop_reason"])
            self.assertEqual(1, len(self.fake.requests))

    async def test_deadline_while_observing_or_insufficient_execution_window(self):
        async def pending():
            await asyncio.Event().wait()
        receipt = await self.session(observe=pending, budget_duration=.02).start()
        self.assertEqual("SESSION_DEADLINE", receipt["stop_reason"])
        receipt = await self.session(budget_duration=10).start()
        self.assertEqual("INSUFFICIENT_EXECUTION_WINDOW", receipt["stop_reason"])
        self.assertEqual([], self.sent)

    async def test_session_cannot_start_twice_and_guard_is_snapshotted(self):
        session = self.session()
        self.policy["sqli"]["endpoint"] = "http://outside.invalid/"
        task = session.start()
        with self.assertRaises(ValueError):
            session.start()
        receipt = await task
        self.assertEqual("MAX_ROUNDS", receipt["stop_reason"])
        self.assertNotIn("outside", self.sent[0]["target"]["url"])

    async def test_benchmark_purpose_and_invalid_limits_rejected(self):
        session = self.session()
        with self.assertRaises(ValueError):
            Session(purpose="B2", guard=session.guard, adapter=self.adapter, observe=session.observe,
                    execute=session.execute, context=self.ctx)
        for kwargs in [{"max_rounds": True}, {"max_rounds": 4}, {"command_s": 6},
                       {"allowed_templates": ("new",)}, {"duration_s": 181},
                       {"required_rounds": True}, {"required_rounds": -1}, {"required_rounds": 2},
                       {"required_rounds": "1"}, {"required_rounds": 1.0}, {"required_rounds": None}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                SessionLimits(**kwargs)
        self.assertEqual((0, 3), (SessionLimits().required_rounds, SessionLimits(max_rounds=3, required_rounds=3).required_rounds))


if __name__ == "__main__":
    unittest.main()
