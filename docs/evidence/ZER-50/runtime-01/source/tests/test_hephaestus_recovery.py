"""ZER-50 product flow with fake model/API/probes; socket connections forbidden."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id, validate
from event_pipeline.llm import Adapter, Limits, MODEL, RunBudget
from hephaestus.recovery import Healer, Journal
from test_sqli_action_state import PINS, POD, probes

CLOCK = {"clock_id": "test", "clock_source": "UNKNOWN", "resolution_ms": None}


class Model:
    def __init__(self, mode="BLOCK_IP"):
        self.mode, self.requests = mode, []
        self.started, self.release = asyncio.Event(), asyncio.Event()

    async def send(self, payload, timeout):
        self.requests.append(deepcopy(payload))
        self.started.set()
        if self.mode == "SLOW":
            await self.release.wait()
        if self.mode == "TIMEOUT":
            raise asyncio.TimeoutError
        if self.mode == "429":
            return {"status": 429, "body": {"error": {"code": "rate_limit_exceeded"}}}
        action = self.mode if self.mode in {"NO_ACTION", "ABSTAIN"} else "BLOCK_IP"
        value = {"action": action, "reason": {"BLOCK_IP": "SQLI_DISCLOSURE", "NO_ACTION": "BENIGN",
            "ABSTAIN": "INSUFFICIENT_EVIDENCE"}[action],
            "evidence_ids": [json.loads(payload["input"])["detection"]["event_id"]]}
        if self.mode == "REFERENCE":
            value["evidence_ids"] = [new_id("evt")]
        if self.mode == "EXTRA":
            value["ip"] = "10.42.0.99"
        if self.mode == "ENUM":
            value["action"] = "RESTART"
        if self.mode == "REASON":
            value["reason"] = "BENIGN"
        content = [{"type": "output_text", "text": "{broken" if self.mode == "JSON" else json.dumps(value)}]
        if self.mode == "REFUSAL":
            content = [{"type": "refusal", "refusal": "offline"}]
        body = {"id": "resp_offline", "model": MODEL, "status": "completed", "output": [{
            "type": "message", "role": "assistant", "status": "completed", "content": content}],
            "usage": {"input_tokens": 100, "output_tokens": 40, "total_tokens": 140}}
        if self.mode == "USAGE":
            del body["usage"]
        return {"status": 200, "body": body, "request_id": "req_offline"}


class API:
    def __init__(self, pins):
        self.doc = {"metadata": {"name": "zer46-sqli-containment", "namespace": "zd-sqli-lab",
            "uid": PINS["uid"], "resourceVersion": "1", "labels": {"zero-door.io/containment-scope": PINS["scope"]}},
            "data": {"policy.json": json.dumps({"version": "zer46-containment/1", "scope": PINS["scope"],
                "run_id": pins["run_id"], "trial_id": pins["trial_id"], "rules": []})}}
        self.writes, self.reads = 0, 0
        self.timeout = self.slow = False
        self.started, self.release = threading.Event(), threading.Event()

    def read_namespaced_config_map(self, name, namespace, **kw):
        self.reads += 1
        return deepcopy(self.doc)

    def replace_namespaced_config_map(self, name, namespace, doc, **kw):
        self.started.set()
        if self.slow:
            assert self.release.wait(5), "offline API was not released"
        self.writes += 1
        self.doc = deepcopy(doc)
        self.doc["metadata"]["resourceVersion"] = str(self.writes + 1)
        if self.timeout:
            raise TimeoutError("offline ambiguous commit")
        return deepcopy(self.doc)


class Recovery(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.net = patch.object(socket.socket, "connect", side_effect=AssertionError("OFFLINE_ONLY"))
        self.net.start()
        self.addCleanup(self.net.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pins = dict(PINS, run_id=new_id("run"), trial_id=new_id("trl"))
        self.ctx = {"run_id": self.pins["run_id"], "trial_id": self.pins["trial_id"], "incident_id": new_id("inc"),
                    "group": "B2", "method_version": "zer50-offline", "config_ref": "sha256:" + "1" * 64}
        self.detected = Producer("detector", "test", CLOCK).event(self.ctx, "DETECTED", {
            "rule_id": "SUSPICIOUS_LOG", "rule_version": "1", "signature": "SQLI/fixture",
            "metric": "log_pattern_match", "value": 1, "threshold": 0, "severity": "WARNING",
            "description": "Observed restricted-row disclosure in owned fixture"}, "o.alert",
            target={"namespace": "zd-sqli-lab", "service": "sqli-fixture", "flow": None}, alert_id=new_id("alt"))
        self.access = {"ref": "observer/access-1", "request_id": "4" * 32, "ts": 1000,
            "client_ip": PINS["attacker_ip"], "tcp_peer": "10.42.0.12", "source_method": "XFF_AFTER_TRUSTED",
            "source_confidence": "PROXY_CHAIN", "method": "GET", "path": "/fixture/catalog/search",
            "status": 200, "rows": 3, "restricted_rows": 1, "delivered": True,
            "run_id": self.ctx["run_id"], "trial_id": self.ctx["trial_id"], "fixture_uid": POD,
            "detection_event_id": self.detected["event_id"]}
        self.wall, self.probe_calls, self.api = 1001, 0, API(self.pins)

    def engine(self, mode="BLOCK_IP", **kw):
        self.model = Model(mode)
        self.adapter = Adapter(self.model, RunBudget(self.ctx["run_id"], max_calls=3,
            max_reserved_tokens=30000, max_estimated_usd=.005, duration_s=60),
            limits=Limits(attempts=1, timeout_s=1, deadline_s=2, retry_delay_s=0, max_output_tokens=256))
        journal = Journal(kw.pop("output", self.tmp.name), self.ctx)
        self.addCleanup(journal.close)
        self.journal = journal
        return Healer(self.adapter, self.ctx, api=self.api, pins=self.pins, fixture_uid=POD,
            journal=journal, probe=kw.pop("probe", self.probe), wall_clock=lambda: self.wall, **kw)

    async def probe(self, api):
        self.probe_calls += 1
        rows = probes()
        rows[0]["access"]["action_ids"] = [api["rule"]["action_id"]]
        self.wall = 1010
        return {"attacker": rows[0], "benign": rows[1:], "fixture": {"uid": POD, "ready": True}}

    def records(self):
        return [json.loads(line) for line in (self.journal.directory / "events.jsonl").read_text().splitlines()]

    def test_projection_probe_timeout_bound(self):
        engine = self.engine(probe_timeout_s=120)
        self.assertEqual(120, engine.probe_timeout_s)
        from pathlib import Path
        output = Path(self.tmp.name) / 'invalid-bound'
        output.mkdir()
        with self.assertRaisesRegex(ValueError, 'HEAL_CONFIGURATION'):
            self.engine(output=output, probe_timeout_s=121)

    async def test_real_product_chain_mode_guard_backend_and_postconditions(self):
        engine = self.engine()
        before = deepcopy((self.detected, self.access))
        receipt = await engine.run(self.detected, self.access)
        self.assertEqual("ACTION_COMPLETED", receipt["status"])
        self.assertEqual((1, 1), (self.api.writes, self.probe_calls))
        self.assertEqual("SUCCESS", receipt["action_state"]["terminal"]["status"])
        self.assertEqual("EXTERNAL_H_PROBE_REQUIRED", receipt["recovery_verification"])
        self.assertFalse(receipt["benchmark_eligible"])
        self.assertEqual(before, (self.detected, self.access))
        self.assertEqual(self.detected["event_id"], receipt["decision"]["causation_id"])
        self.assertEqual(receipt["decision_id"], receipt["model_events"][0]["decision_id"])
        self.assertIsNone(validate(receipt["decision"]))
        kinds = [r["kind"] for r in self.records()]
        self.assertEqual(["OBSERVATION", "DECISION", "GUARD_VERDICT", "DISPATCH_INTENT",
                          "API_ACCEPTED", "ACTION_POSTCONDITION", "HEAL_RECEIPT"], kinds)
        self.assertIsNone(validate(self.records()[2]["event"]))
        self.assertEqual(1180, receipt["api_result"]["rule"]["expires_at"])
        self.assertEqual([], self.model.requests[0]["tools"])

    async def test_no_action_benign_and_abstain_never_touch_api_or_probes(self):
        # Fresh per-run output namespace for each independent case.
        for mode in ("NO_ACTION", "ABSTAIN"):
            with self.subTest(mode=mode):
                parent = str(Path(self.tmp.name) / mode)
                Path(parent).mkdir()
                engine = self.engine(mode, output=parent)
                receipt = await engine.run(self.detected, dict(self.access, restricted_rows=0))
                self.assertEqual(mode, receipt["status"])
                self.assertEqual((0, 0, 0), (self.api.writes, self.api.reads, self.probe_calls))
                self.assertFalse(receipt["fallback"])
                self.assertIsNone(receipt["decision"]["payload"]["proposal"])

    async def test_benign_guard_blocks_even_erroneous_model_action(self):
        receipt = await self.engine().run(self.detected, dict(self.access, restricted_rows=0))
        self.assertEqual("GUARD_REJECTED", receipt["status"])
        self.assertEqual(0, self.api.writes)
        self.assertEqual("SQLI_POLICY_EVIDENCE", receipt["reason"])
        self.assertEqual("REJECT", self.records()[-2]["event"]["payload"]["verdict"])

    async def test_model_cannot_block_benign_source_even_with_disclosure(self):
        receipt = await self.engine().run(self.detected, dict(self.access, client_ip=PINS["benign_ip"]))
        self.assertEqual("GUARD_REJECTED", receipt["status"])
        self.assertEqual(0, self.api.writes)

    async def test_missing_access_abstains_without_provider(self):
        receipt = await self.engine().run(self.detected, None)
        self.assertEqual("ABSTAIN", receipt["status"])
        self.assertEqual([], self.model.requests)
        self.assertTrue(receipt["fallback"])
        self.assertEqual("NONE", receipt["decision_source"])

    async def test_model_failures_refusals_reference_and_enum_never_dispatch(self):
        for mode in ("JSON", "ENUM", "EXTRA", "REFERENCE", "REASON", "429", "TIMEOUT", "REFUSAL", "USAGE"):
            with self.subTest(mode=mode):
                parent = str(Path(self.tmp.name) / mode)
                Path(parent).mkdir()
                receipt = await self.engine(mode, output=parent).run(self.detected, self.access)
                self.assertNotIn(receipt["status"], {"ACTION_COMPLETED", "OK"})
                self.assertEqual(0, self.api.writes)
                self.assertTrue(receipt["fallback"])
                self.assertEqual("NONE", receipt["decision_source"])
                self.assertEqual(1, len(self.model.requests))

    async def test_wrong_mode_context_target_or_h_plane_refuse_before_model(self):
        engine = self.engine()
        for event in (dict(self.detected, group="B1"), dict(self.detected, run_id=new_id("run")),
                      dict(self.detected, plane="H"), dict(self.detected, target={"namespace": "target-app",
                          "service": "frontend", "flow": None})):
            with self.assertRaises(ValueError):
                await engine.run(event, self.access)
        self.assertFalse(self.model.requests)

    async def test_untrusted_stale_nonfinite_or_extra_access_refuses_before_model(self):
        engine = self.engine()
        for changes in ({"ts": 900}, {"ts": float("nan")}, {"tcp_peer": "10.42.0.99"},
                {"source_confidence": "UNKNOWN"}, {"restricted_rows": -1}, {"delivered": False},
                {"expected_label": "SQLI"}, {"client_ip": "8.8.8.8"}, {"run_id": new_id("run")},
                {"trial_id": new_id("trl")}, {"fixture_uid": "99999999-9999-4999-8999-999999999999"},
                {"detection_event_id": new_id("evt")}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                await engine.run(self.detected, dict(self.access, **changes))
        self.assertFalse(self.model.requests)

    async def test_same_instance_and_directory_cannot_replay(self):
        engine = self.engine()
        await engine.run(self.detected, self.access)
        with self.assertRaises(ValueError):
            await engine.run(self.detected, self.access)
        with self.assertRaises(FileExistsError):
            Journal(self.tmp.name, self.ctx)
        self.assertEqual(1, self.api.writes)

    async def test_same_journal_cannot_be_reused_by_a_second_engine(self):
        first = self.engine()
        second = Healer(self.adapter, self.ctx, api=self.api, pins=self.pins, fixture_uid=POD,
            journal=self.journal, probe=self.probe, wall_clock=lambda: self.wall)
        await first.run(self.detected, self.access)
        with self.assertRaisesRegex(ValueError, "JOURNAL_ALREADY_USED"):
            await second.run(self.detected, self.access)
        self.assertEqual(1, self.api.writes)
        self.assertEqual(1, len(self.model.requests))

    async def test_shared_adapter_trace_does_not_claim_another_decision(self):
        engine = self.engine()
        send = self.model.send
        async def interleaved(payload, timeout):
            self.adapter.events.append({"decision_id": new_id("dec"), "kind": "OTHER_ACTOR"})
            return await send(payload, timeout)
        self.model.send = interleaved
        receipt = await engine.run(self.detected, self.access)
        self.assertEqual(1, len(receipt["model_events"]))
        self.assertTrue(all(e["decision_id"] == receipt["decision_id"] for e in receipt["model_events"]))

    async def test_ambiguous_api_result_is_unknown_and_never_retried(self):
        self.api.timeout = True
        engine = self.engine()
        receipt = await engine.run(self.detected, self.access)
        self.assertEqual("ACTION_OUTCOME_UNKNOWN", receipt["status"])
        self.assertEqual(1, self.api.writes)
        self.assertIsNone(receipt["action_state"])
        self.assertEqual(0, self.probe_calls)
        with self.assertRaises(ValueError):
            await engine.run(self.detected, self.access)

    async def test_api_ack_with_invalid_benign_content_is_not_completion(self):
        async def bad(api):
            proof = await self.probe(api)
            proof["benign"][2]["http"]["response"]["body"] = {"status": "FAKE"}
            return proof
        receipt = await self.engine(probe=bad).run(self.detected, self.access)
        self.assertEqual("NOT_VERIFIED", receipt["status"])
        self.assertEqual("PARTIAL", receipt["action_state"]["terminal"]["status"])
        self.assertFalse(receipt["action_state"]["terminal"]["postcondition"]["satisfied"])

    async def test_probe_timeout_is_terminal_and_not_success(self):
        async def slow(_):
            await asyncio.Event().wait()
        receipt = await self.engine(probe=slow, probe_timeout_s=.02).run(self.detected, self.access)
        self.assertEqual("PROBE_TIMEOUT", receipt["reason"])
        self.assertEqual("TIMEOUT", receipt["action_state"]["terminal"]["status"])

    async def test_model_cancel_has_no_effect_and_durable_receipt(self):
        engine = self.engine("SLOW")
        task = asyncio.create_task(engine.run(self.detected, self.access))
        await self.model.started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        receipt = self.records()[-1]["receipt"]
        self.assertEqual("CANCELLED", receipt["status"])
        self.assertEqual(0, self.api.writes)
        self.assertEqual("TIMEOUT", receipt["model_events"][0]["payload"]["outcome"])

    async def test_cancel_during_api_drains_owner_and_does_not_claim_undo(self):
        self.api.slow = True
        engine = self.engine()
        task = asyncio.create_task(engine.run(self.detected, self.access))
        self.assertTrue(await asyncio.to_thread(self.api.started.wait, 2))
        task.cancel()
        await asyncio.sleep(.01)
        self.assertFalse(task.done())
        self.api.release.set()
        with self.assertRaises(asyncio.CancelledError):
            await task
        receipt = self.records()[-1]["receipt"]
        self.assertEqual("ACTION_MAY_REMAIN", receipt["reason"])
        self.assertEqual("API_ACCEPTED", receipt["api_result"]["status"])
        self.assertEqual(1, self.api.writes)
        self.assertEqual(0, self.probe_calls)

    async def test_record_failure_before_model_or_dispatch_stops_effect(self):
        engine = self.engine()
        original = Journal.__call__
        def fail_intent(journal, item):
            if item["kind"] == "DISPATCH_INTENT":
                raise OSError("offline full disk")
            original(journal, item)
        with patch.object(Journal, "__call__", fail_intent):
            receipt = await engine.run(self.detected, self.access)
        self.assertEqual("FAILED", receipt["status"])
        self.assertEqual(0, self.api.writes)

    async def test_sink_failure_before_model_is_not_silently_ignored(self):
        engine = self.engine()
        with patch.object(Journal, "__call__", side_effect=OSError("offline disk")):
            with self.assertRaises(OSError):
                await engine.run(self.detected, self.access)
        self.assertFalse(self.model.requests)

    async def test_budget_shared_not_reset_and_exhaustion_no_dispatch(self):
        engine = self.engine()
        self.adapter.budget.calls = self.adapter.budget.max_calls
        receipt = await engine.run(self.detected, self.access)
        self.assertEqual("NOT_RUN", receipt["status"])
        self.assertFalse(self.model.requests)
        self.assertEqual(0, self.api.writes)

    async def test_expired_source_after_model_is_refused_before_write(self):
        engine = self.engine()
        send = self.model.send
        async def delayed(payload, timeout):
            result = await send(payload, timeout)
            self.wall = 1061
            return result
        self.model.send = delayed
        receipt = await engine.run(self.detected, self.access)
        self.assertEqual("GUARD_REJECTED", receipt["status"])
        self.assertEqual(0, self.api.writes)

    async def test_foreign_policy_uid_fails_closed(self):
        self.api.doc["metadata"]["uid"] = "99999999-9999-4999-8999-999999999999"
        receipt = await self.engine().run(self.detected, self.access)
        self.assertEqual("ACTION_OUTCOME_UNKNOWN", receipt["status"])
        self.assertEqual(0, self.api.writes)

    async def test_worker_api_does_not_block_event_loop(self):
        self.api.slow = True
        engine = self.engine()
        task = asyncio.create_task(engine.run(self.detected, self.access))
        self.assertTrue(await asyncio.to_thread(self.api.started.wait, 2))
        heartbeat = 0
        for _ in range(5):
            await asyncio.sleep(.005)
            heartbeat += 1
        self.assertEqual(5, heartbeat)
        self.api.release.set()
        self.assertEqual("ACTION_COMPLETED", (await task)["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
