"""ZER-49: real Gaia functions/shared adapter, fake telemetry/model; no lab/provider."""
import asyncio
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.adapters import Detector
from event_pipeline.contract import Producer, canonical, new_id, validate
from event_pipeline.llm import Adapter, Limits, MODEL, RunBudget
from gaia.diagnosis import Diagnoser, PURPOSE
from gaia.diagnosis_cli import Journal, config_valid, main as cli

CLOCK = {"clock_id": "test", "clock_source": "UNKNOWN", "resolution_ms": None}


def context():
    return {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
        "group": "B2", "method_version": "zer49-offline", "config_ref": "sha256:" + "1" * 64}


def detection(ctx, metric="cpu_usage_percent"):
    return Producer("detector", "test", CLOCK).event(ctx, "DETECTED", {
        "rule_id": "HIGH_CPU", "rule_version": "test", "signature": "HIGH_CPU/frontend",
        "metric": metric, "value": 90.0, "threshold": 80.0, "severity": "WARNING",
        "description": "Offline observer sample"}, "o.alert",
        target={"namespace": "target-app", "service": "frontend", "flow": None}, alert_id=new_id("alt"))


def evidence(event, log=None):
    p = event["payload"]
    return {"metric": {"name": p["metric"], "value": p["value"], "threshold": p["threshold"]}, "log": log}


class Fake:
    def __init__(self, mode="OK"):
        self.mode, self.requests = mode, []
        self.started, self.release = asyncio.Event(), asyncio.Event()

    async def send(self, payload, timeout):
        self.requests.append(deepcopy(payload))
        self.started.set()
        if self.mode == "SLOW":
            await self.release.wait()
        if self.mode == "TIMEOUT":
            raise httpx.ReadTimeout("fake")
        if self.mode == "429":
            return {"status": 429, "body": {"error": {"code": "rate_limit_exceeded"}}}
        obs = json.loads(payload["input"])
        output = {"classification": "RESOURCE_PRESSURE", "summary": "Observed metric exceeds its threshold.",
                  "confidence": .8, "evidence_ids": [obs["detection"]["event_id"]]}
        if self.mode == "UNKNOWN":
            output["classification"] = "UNKNOWN"
        if self.mode == "REFERENCE":
            output["evidence_ids"] = [new_id("evt")]
        if self.mode == "ACTION":
            output["action"] = "RESTART"
        text = "{broken" if self.mode == "JSON" else json.dumps(output)
        content = [{"type": "refusal", "refusal": "fake"}] if self.mode == "REFUSAL" else [{"type": "output_text", "text": text}]
        return {"status": 200, "request_id": "req_offline", "body": {"id": "resp_offline", "model": MODEL,
            "status": "completed", "output": [{"type": "message", "role": "assistant", "status": "completed",
            "content": content}], "usage": {"input_tokens": 100, "output_tokens": 40, "total_tokens": 140}}}


class Cases(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # A fake must never silently become a provider or cluster connection.
        self.net = patch.object(socket.socket, "connect", side_effect=AssertionError("OFFLINE_ONLY"))
        self.net.start()
        self.addCleanup(self.net.stop)
        self.ctx, self.rows = context(), []
        self.event = detection(self.ctx)

    def engine(self, mode="OK", *, calls=1, sink=None, timeout=1):
        self.fake = Fake(mode)
        budget = RunBudget(self.ctx["run_id"], max_calls=calls, max_reserved_tokens=30000,
                           max_estimated_usd=.005, duration_s=60)
        self.adapter = Adapter(self.fake, budget, limits=Limits(attempts=1, timeout_s=timeout,
            deadline_s=2, retry_delay_s=0, max_output_tokens=256))
        return Diagnoser(self.adapter, self.ctx, sink or self.rows.append)

    async def test_success_has_metric_input_diagnosis_latency_and_join(self):
        engine = self.engine()
        before = canonical(self.event)
        result = await engine.analyze(self.event, evidence(self.event))
        self.assertEqual("OK", result["status"])
        self.assertEqual(before, canonical(self.event))
        self.assertEqual(self.event["ts_event"], result["detected_at"])
        self.assertEqual(["INCIDENT_DETECTED", "INCIDENT_DIAGNOSIS"], [r["kind"] for r in self.rows])
        self.assertGreaterEqual(result["latency_ms"], 0)
        self.assertEqual(self.event["event_id"], result["decision"]["causation_id"])
        self.assertEqual(self.event["event_id"], result["model_events"][0]["causation_id"])
        self.assertIsNone(validate(result["decision"]))
        self.assertIsNone(validate(result["model_events"][0]))
        self.assertIsNone(result["decision"]["payload"]["proposal"])
        self.assertEqual("ANALYSIS", result["decision"]["payload"]["stage"])
        self.assertEqual(evidence(self.event), self.rows[0]["observation"]["evidence"])
        self.assertEqual([], self.fake.requests[0]["tools"])

    async def test_model_failures_are_not_diagnosis_or_fallback_success(self):
        for mode, expected in [("JSON", "SCHEMA_INVALID"), ("ACTION", "SCHEMA_INVALID"),
                ("REFERENCE", "SCHEMA_INVALID"), ("429", "HTTP_ERROR"),
                ("TIMEOUT", "TIMEOUT"), ("REFUSAL", "REFUSAL")]:
            with self.subTest(mode=mode):
                self.rows.clear()
                result = await self.engine(mode).analyze(self.event, evidence(self.event))
                self.assertEqual(expected, result["status"])
                self.assertEqual("NONE", result["decision_source"])
                self.assertIsNone(result["diagnosis"])
                self.assertIsNone(result["decision"])
                self.assertFalse(result["fallback"])
                self.assertEqual(1, len(self.fake.requests))

    async def test_unknown_is_abstain_not_success(self):
        result = await self.engine("UNKNOWN").analyze(self.event, evidence(self.event))
        self.assertEqual("ABSTAIN", result["status"])
        self.assertEqual("ABSTAIN", result["decision"]["payload"]["response_kind"])
        self.assertIsNone(result["decision"]["payload"]["proposal"])

    async def test_missing_log_mismatched_metric_and_hidden_fields_refuse_before_call(self):
        for ev, e in [(detection(self.ctx, "log_pattern_match"), evidence(detection(self.ctx, "log_pattern_match"))),
                (self.event, {"metric": {"name": "wrong", "value": 90, "threshold": 80}, "log": None}),
                (self.event, dict(evidence(self.event), cause="hidden"))]:
            engine = self.engine()
            with self.assertRaises(ValueError):
                await engine.analyze(ev, e)
            self.assertFalse(self.fake.requests)

    async def test_context_and_B1_never_call_model(self):
        engine = self.engine()
        for changed in [dict(self.event, group="B1"), dict(self.event, run_id=new_id("run"))]:
            with self.assertRaises(ValueError):
                await engine.analyze(changed, evidence(changed))
        self.assertFalse(self.fake.requests)

    async def test_no_repeat_after_unknown_and_no_reset_budget_per_alert(self):
        engine = self.engine("TIMEOUT")
        await engine.analyze(self.event, evidence(self.event))
        self.assertEqual("DUPLICATE_DETECTION", (await engine.analyze(self.event, evidence(self.event)))["reason"])
        other = detection(self.ctx)
        self.assertEqual("RUN_LIMIT", (await engine.analyze(other, evidence(other)))["reason"])
        self.assertEqual(1, self.adapter.budget.calls)

    async def test_sink_failure_stops_before_provider(self):
        def broken(_):
            raise OSError("disk unavailable")
        engine = self.engine(sink=broken)
        with self.assertRaises(OSError):
            await engine.analyze(self.event, evidence(self.event))
        self.assertFalse(self.fake.requests)
        self.assertEqual("DUPLICATE_DETECTION", (await engine.analyze(self.event, evidence(self.event)))["reason"])

    async def test_cancellation_retains_unknown_trace_and_never_reports_success(self):
        engine = self.engine("SLOW")
        task = asyncio.create_task(engine.analyze(self.event, evidence(self.event)))
        await self.fake.started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual("CANCELLED", self.rows[-1]["status"])
        self.assertEqual("TIMEOUT", self.rows[-1]["model_events"][0]["payload"]["outcome"])
        self.assertEqual(1, self.rows[-1]["budget"]["unknown_usage_attempts"])

    async def test_adapter_timeout_is_finite(self):
        engine = self.engine("SLOW", timeout=.01)
        result = await asyncio.wait_for(engine.analyze(self.event, evidence(self.event)), 1)
        self.assertEqual("TIMEOUT", result["status"])

    def load_gaia(self):
        spec = importlib.util.spec_from_file_location("zer49_gaia", ROOT / "agent-orchestrator/gaia/main.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, {}, clear=True):
            spec.loader.exec_module(module)
        ctx, published = self.ctx, []
        class OClient:
            producer = Producer("detector", "test", CLOCK)
            def context(self):
                return ctx
            def publish(self, event):
                published.append(deepcopy(event))
        module.r1_client, module.r1_detector = OClient(), Detector(OClient())
        return module, published

    async def test_actual_poll_does_not_wait_for_model_or_move_detection_timestamp(self):
        module, published = self.load_gaia()
        module.diagnosis_engine = self.engine("SLOW")
        async def query(_client, text):
            return {"status": "success", "data": {"result": [
                {"metric": {"pod": "frontend-123-abc", "container": "server"}, "value": [0, ".2"]}
                ] if "cpu_usage_seconds_total" in text else []}}
        with patch.object(module, "query_prometheus", side_effect=query):
            await asyncio.wait_for(module.poll_prometheus_metrics(), .5)
        await self.fake.started.wait()
        self.assertEqual(1, len(published))
        before = canonical(published[0])
        self.assertEqual("HIGH_CPU", published[0]["payload"]["rule_id"])
        # Another detector result can be published while inference is still blocked.
        module.observe_alert("HIGH_MEMORY", "cartservice", "memory", 300., 200., "Offline second sample")
        self.assertEqual(2, len(published))
        self.fake.release.set()
        await asyncio.gather(*list(module.diagnosis_tasks))
        self.assertEqual(before, canonical(published[0]))
        self.assertEqual(published[0]["ts_event"], self.rows[-1]["detected_at"])
        self.assertEqual(1, len(self.fake.requests))

    async def test_actual_log_poll_retains_log_input_and_disabled_path_stays_model_free(self):
        module, published = self.load_gaia()
        module.diagnosis_engine = self.engine()
        class ES:
            def search(self, **_):
                return {"hits": {"hits": [{"_source": {"message": "ERROR sample from owned fixture",
                    "@timestamp": "2026-10-29T00:00:00.000Z", "kubernetes": {
                    "namespace_name": "target-app", "pod_name": "frontend-a-b", "container_name": "server"}}}]}}
        with patch.object(module, "get_es_client", return_value=ES()):
            await module.poll_elasticsearch_logs()
        await asyncio.gather(*list(module.diagnosis_tasks))
        obs = json.loads(self.fake.requests[0]["input"])
        self.assertEqual("ERROR sample from owned fixture", obs["evidence"]["log"]["message"])
        self.assertEqual(published[0]["ts_event"], self.rows[-1]["detected_at"])
        module.diagnosis_engine = None
        module.observe_alert("HIGH_CPU", "other", "cpu", 90., 80., "Offline metric")
        self.assertEqual(2, len(published))
        self.assertEqual(1, len(self.fake.requests))

    async def test_shutdown_drains_cancelled_model_before_closing_journal(self):
        module, _ = self.load_gaia()
        module.diagnosis_engine = self.engine("SLOW")
        module.observe_alert("HIGH_CPU", "frontend", "cpu", 90., 80., "Offline")
        await self.fake.started.wait()
        closed, rows = [], self.rows
        class JournalStub:
            def close(self):
                closed.append(rows[-1]["status"])
        module.diagnosis_journal = JournalStub()
        await module.shutdown_event()
        self.assertEqual(["CANCELLED"], closed)
        self.assertFalse(module.diagnosis_tasks)

    async def test_startup_default_has_no_model_client_and_stops_owned_loop(self):
        module, _ = self.load_gaia()
        async def loop():
            await asyncio.Event().wait()
        with patch.dict(os.environ, {}, clear=True), patch.object(module, "monitoring_loop", side_effect=loop), \
                patch("gaia.diagnosis_cli.HttpxTransport", side_effect=AssertionError("NO_PROVIDER")):
            await module.startup_event()
            await module.shutdown_event()
        self.assertIsNone(module.diagnosis_engine)
        self.assertTrue(module.monitoring_task.done())

    async def test_cli_live_path_uses_saved_observation_and_exclusive_receipts_with_fake_model(self):
        from argparse import Namespace
        from gaia.diagnosis_cli import live
        config = {"purpose": PURPOSE, "benchmark_eligible": False, "context": self.ctx, "max_calls": 1,
                  "max_reserved_tokens": 12000, "max_estimated_usd": .005, "duration_s": 60}
        fake = Fake()
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / "config.json").write_bytes(canonical(config))
            (folder / "input.json").write_bytes(canonical({"detection": self.event, "evidence": evidence(self.event)}))
            args = Namespace(config=str(folder / "config.json"), observation=str(folder / "input.json"), output=str(folder))
            with patch("gaia.diagnosis_cli.HttpxTransport", return_value=fake):
                self.assertEqual(0, await live(args))
                with self.assertRaises(FileExistsError):
                    await live(args)
            self.assertEqual(1, len(fake.requests))
            receipt = json.loads((folder / self.ctx["run_id"] / "receipt.json").read_bytes())
            self.assertEqual(self.event["ts_event"], receipt["detected_at"])
            self.assertEqual("OK", receipt["status"])
            self.assertEqual(2, len((folder / self.ctx["run_id"] / "events.jsonl").read_text().splitlines()))

    async def test_slow_evidence_disk_does_not_block_detection_and_cancel_drains_writer(self):
        module, published = self.load_gaia()
        entered, release, closed = threading.Event(), threading.Event(), []
        rows = self.rows
        def slow_sink(item):
            rows.append(item)
            entered.set()
            if not release.wait(3):
                raise OSError("offline sink test timed out")
        module.diagnosis_engine = self.engine(sink=slow_sink)
        class JournalStub:
            def close(self):
                closed.append(True)
        module.diagnosis_journal = JournalStub()
        try:
            module.observe_alert("HIGH_CPU", "frontend", "cpu", 90., 80., "Offline")
            async def entered_wait():
                while not entered.is_set():
                    await asyncio.sleep(.001)
            await asyncio.wait_for(entered_wait(), 1)
            module.observe_alert("HIGH_MEMORY", "cartservice", "memory", 300., 200., "Offline next sample")
            self.assertEqual(2, len(published))
            shutdown = asyncio.create_task(module.shutdown_event())
            await asyncio.sleep(.01)
            self.assertFalse(closed)  # Writer still owns the open journal.
            self.assertFalse(shutdown.done())
        finally:
            release.set()
        await asyncio.wait_for(shutdown, 1)
        self.assertEqual([True], closed)
        self.assertFalse(self.fake.requests)  # Cancel during pre-call evidence persistence.
        self.assertFalse(module.diagnosis_tasks)


class CliCases(unittest.TestCase):
    def config(self):
        return {"purpose": PURPOSE, "benchmark_eligible": False, "context": context(), "max_calls": 1,
                "max_reserved_tokens": 12000, "max_estimated_usd": .005, "duration_s": 60}

    def test_default_is_plan_only_and_does_not_construct_transport(self):
        with patch.object(sys, "argv", ["gaia.diagnosis_cli"]), \
             patch("gaia.diagnosis_cli.HttpxTransport", side_effect=AssertionError("NO_PROVIDER")):
            self.assertEqual(0, cli())

    def test_config_caps_modes_and_context_are_validated(self):
        config_valid(self.config())
        for key, bad in [("max_calls", 4), ("max_calls", True), ("max_estimated_usd", .006),
                ("duration_s", 0), ("duration_s", float("nan")), ("benchmark_eligible", True)]:
            value = self.config()
            value[key] = bad
            with self.assertRaises(ValueError):
                config_valid(value)
        bad = self.config()
        bad["context"]["config_ref"] = "not-a-hash"
        with self.assertRaises(ValueError):
            config_valid(bad)

    def test_exclusive_journal_prevents_restart_replay(self):
        config = self.config()
        with tempfile.TemporaryDirectory() as folder:
            journal = Journal(folder, config)
            journal({"kind": "OFFLINE_SENTINEL"})
            journal.close()
            with self.assertRaises(FileExistsError):
                Journal(folder, config)
            path = Path(folder) / config["context"]["run_id"] / "events.jsonl"
            self.assertEqual({"kind": "OFFLINE_SENTINEL"}, json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
