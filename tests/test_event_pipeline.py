"""Offline contract/archive/access regression checks; no Kubernetes/LLM calls."""
import copy
import ast
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, canonical, new_id, now, validate
from event_pipeline.store import Archive, sha
from event_pipeline.gateway import Gateway, server
from event_pipeline.audit import audit
from event_pipeline.telemetry import Telemetry
from event_pipeline.adapters import Detector, RulesConsumer

CLOCK = {"clock_id": "clk_test", "clock_source": "UNKNOWN", "resolution_ms": None}


def context(group="B1"):
    return {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
            "group": group, "method_version": "transport-test-not-kpi", "config_ref": "sha256:" + "1" * 64}


def detected(ctx=None):
    return Producer("detector", "test", CLOCK).event(ctx or context(), "DETECTED", {
        "rule_id": "HIGH_CPU", "rule_version": "test", "signature": "HIGH_CPU/frontend",
        "metric": "cpu", "value": 0.9, "threshold": 0.8, "severity": "WARNING",
        "description": "Observed CPU above threshold"}, "o.alert",
        target={"namespace": "target-app", "service": "frontend", "flow": None}, alert_id=new_id("alt"))


def contexts(ctx):
    producer = Producer("harness", "test", CLOCK)
    run = dict(ctx, trial_id=None)
    run.pop("incident_id", None)
    return [producer.event(run, "RUN_CONTEXT", {}, "o.context"),
            producer.event(ctx, "TRIAL_CONTEXT", {}, "o.context")]


class ContractTests(unittest.TestCase):
    def test_neutral_ids_and_timestamp(self):
        event = detected()
        self.assertIsNone(validate(event))
        self.assertEqual(24, len(event["ts_event"]))
        producer = Producer("detector", "test", CLOCK)
        one = producer.event(context(), "DETECTED", event["payload"], "o.alert", event["target"], alert_id=new_id("alt"))
        two = producer.event(context(), "DETECTED", event["payload"], "o.alert", event["target"], alert_id=new_id("alt"))
        self.assertEqual((0, 1), (one["seq"], two["seq"]))

    def test_malformed_input_never_crashes(self):
        for value in (None, [], "text", 3, {"event_id": "x"}):
            self.assertIsNotNone(validate(value))
        for key in detected():
            for value in (None, [], {}, float("nan")):
                event = detected()
                event[key] = value
                result = validate(event)
                self.assertTrue(result is None or isinstance(result, str))

    def test_missing_or_forged_id_not_repaired(self):
        event = detected()
        for key in ("run_id", "trial_id", "alert_id"):
            broken = copy.deepcopy(event)
            broken.pop(key)
            self.assertIsNotNone(validate(broken))
        event["incident_id"] = "inc_cpu-case-1"
        self.assertEqual("INVALID_ID", validate(event))

    def test_source_plane_version(self):
        event = detected()
        self.assertEqual("SOURCE_VIOLATION", validate(event, source="executor"))
        self.assertEqual("PLANE_VIOLATION", validate(event, plane="H"))
        event["schema_version"] = "zd-event/9.0.0"
        self.assertEqual("UNSUPPORTED", validate(event))

    def test_nested_answer_rejected_but_observed_ip_preserved(self):
        event = detected()
        event["payload"]["description"] = "Request source 192.0.2.9 contained UNION SELECT"
        self.assertIsNone(validate(event))
        event["payload"]["extra"] = [{"expected_action": "SCALE_UP"}]
        self.assertEqual("LEAK_DETECTED", validate(event))

    def test_action_does_not_imply_recovery(self):
        ctx = context()
        event = Producer("executor", "test", CLOCK).event(ctx, "ACTION_COMPLETED", {
            "status": "PARTIAL", "postcondition": {"name": "replicas_ready", "checked": False,
            "satisfied": False, "observed": None}, "error": None}, "o.action", action_id=new_id("act"))
        self.assertIsNone(validate(event))
        event["payload"]["status"] = "SUCCESS"
        self.assertEqual("SEMANTIC", validate(event))
        event["event_type"] = "RECOVERY_VERIFIED"
        self.assertEqual("PLANE_VIOLATION", validate(event))

    def test_b0_blocks_actions(self):
        event = detected(context("B0"))
        event.update(event_type="GUARD_VERDICT", source_component="guard", decision_id=new_id("dec"))
        event["payload"] = {"verdict": "REJECT", "reason_code": "TEST", "guard_version": "test"}
        self.assertEqual("MODE_VIOLATION", validate(event))

    def test_b2_rules_requires_a_real_fallback_reference(self):
        event = Producer("decision_rules", "test", CLOCK).event(context("B1"), "DECISION", {
            "stage": "PROPOSAL", "decision_source": "RULES", "inputs": [], "response_kind": "NO_ACTION",
            "proposal": None, "fallback": False, "fallback_of": None, "prompt_version": None,
            "prompt_sha256": None, "evidence_package_version": "test"}, "o.decision", decision_id=new_id("dec"))
        event["group"] = "B2"
        self.assertEqual("MODE_VIOLATION", validate(event))
        event["payload"]["fallback"] = True
        self.assertIsNotNone(validate(event))
        event["payload"]["fallback_of"] = new_id("dec")
        self.assertIsNone(validate(event))


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.archive = Archive(Path(self.temp.name) / "O", "O")
        self.event = detected()

    def tearDown(self):
        self.archive.close()
        self.temp.cleanup()

    def put(self, event):
        return self.archive.ingest(event, {"kind": "http", "request_id": "test"}, "detector")

    def test_duplicate_reopen_and_export_preserve_raw(self):
        self.assertEqual("RECORDED", self.put(self.event)["status"])
        self.assertEqual("DUPLICATE", self.put(self.event)["status"])
        self.archive.close()
        self.archive = Archive(Path(self.temp.name) / "O", "O")
        records = self.archive.records(self.event["run_id"])
        self.assertEqual(2, len(records))
        self.assertEqual(canonical(self.event), canonical(records[0]["envelope"]))
        output = Path(self.temp.name) / "export"
        manifest = self.archive.export(self.event["run_id"], output)
        self.assertEqual(manifest["sha256"], sha((output / "O.jsonl").read_bytes()))
        self.assertEqual(2, manifest["lines"])
        self.assertEqual("SEALED_DUPLICATE", self.put(self.event)["status"])
        other = copy.deepcopy(self.event)
        other["event_id"] = new_id("evt")
        with self.assertRaisesRegex(ValueError, "RUN_SEALED"):
            self.put(other)

    def test_conflict_durable_quarantine(self):
        self.put(self.event)
        broken = copy.deepcopy(self.event)
        broken["payload"]["value"] = 0.99
        with self.assertRaisesRegex(ValueError, "INTEGRITY_ERROR"):
            self.put(broken)
        self.assertEqual(1, len(self.archive.records(self.event["run_id"])))
        rejection = self.archive.path(self.event["run_id"]) / "rejections.jsonl"
        self.assertEqual("INTEGRITY_ERROR", json.loads(rejection.read_text())["classification"])
        output = Path(self.temp.name) / "conflict-export"
        manifest = self.archive.export(self.event["run_id"], output)
        self.assertEqual(1, manifest["rejections"]["lines"])
        self.assertEqual(rejection.read_bytes(), (output / "rejections.jsonl").read_bytes())

    def test_partial_record_and_hash_tamper_fail_closed(self):
        self.put(self.event)
        path = self.archive.path(self.event["run_id"]) / "O.jsonl"
        self.archive.close()
        with path.open("ab") as handle:
            handle.write(b"{")
        with self.assertRaisesRegex(ValueError, "incomplete raw"):
            Archive(self.archive.root, "O")
        # The operator must recover evidence explicitly; never auto-truncate.
        self.assertTrue(path.read_bytes().endswith(b"{"))

    def test_second_writer_and_path_escape_rejected(self):
        with self.assertRaises((OSError, IOError)):
            Archive(self.archive.root, "O")
        for run in ("../H", "run_../../H", self.event["run_id"] + "/../H"):
            with self.assertRaises(ValueError):
                self.archive.records(run)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.archive = Archive(Path(self.temp.name) / "O", "O")
        self.keys = {key: key.ljust(40, "x") for key in ("detector", "harness", "reader", "decision_rules")}
        self.gateway = Gateway(self.archive, self.keys)
        self.http = server(self.gateway, ("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.http.server_port)
        self.ctx = context()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(2)
        self.archive.close()
        self.temp.cleanup()

    def request(self, path, role="reader", event=None):
        request = Request(self.url + path, data=canonical(event) if event is not None else None,
                          headers={"Authorization": "Bearer " + self.keys.get(role, "invalid"), "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def setup_context(self):
        for event in contexts(self.ctx):
            self.assertEqual(201, self.request("/events", "harness", event)[0])

    def test_http_id_chain_and_no_h_api(self):
        self.setup_context()
        event = detected(self.ctx)
        self.assertEqual(201, self.request("/events", "detector", event)[0])
        code, result = self.request("/events?run_id=" + self.ctx["run_id"])
        self.assertEqual(200, code)
        self.assertEqual(event, result["records"][-1]["envelope"])
        for path in ("/H", "/raw", "/export", "/../H", "/events?run_id=../../H", "/events?run_id=" + self.ctx["run_id"] + "&plane=H"):
            self.assertIn(self.request(path)[0], (400, 404))
        self.assertEqual(401, self.request("/events", "unknown")[0])
        self.assertEqual(422, self.request("/events", "harness", event)[0])

    def test_context_before_detector_and_immutable(self):
        event = detected(self.ctx)
        self.assertEqual(422, self.request("/events", "detector", event)[0])
        self.setup_context()
        wrong = copy.deepcopy(event)
        wrong["incident_id"] = new_id("inc")
        self.assertEqual(422, self.request("/events", "detector", wrong)[0])
        wrong = contexts(self.ctx)[-1]
        wrong["incident_id"] = new_id("inc")
        self.assertEqual(422, self.request("/events", "harness", wrong)[0])

    def test_h_token_does_not_work_at_o_and_h_has_no_read(self):
        request = Request(self.url + "/events", headers={"Authorization": "Bearer " + "h" * 40})
        with self.assertRaises(HTTPError) as wrong_plane:
            urlopen(request, timeout=2)
        self.assertEqual(401, wrong_plane.exception.code)
        # Keys are intentionally separate dictionaries/processes in deployment.
        h = Archive(Path(self.temp.name) / "H", "H")
        http = server(Gateway(h, {"harness": "h" * 40}), ("127.0.0.1", 0))
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request("http://127.0.0.1:" + str(http.server_port) + "/events", headers={"Authorization": "Bearer " + "h" * 40})
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=2)
            self.assertEqual(403, caught.exception.code)
        finally:
            http.shutdown()
            http.server_close()
            thread.join(2)
            h.close()


class LeakTests(unittest.TestCase):
    def fixtures(self):
        ctx = context()
        producer = Producer("harness", "test", CLOCK)
        manifest = producer.event(ctx, "HARNESS_MANIFEST", {"manifest_version": "test", "allowlist_version": "test",
            "reveal_terms": ["stress"], "entries": [{"kind": "pod", "value": "wrk-a21d", "class": "NEUTRAL", "o_visible": True}]}, "h.audit")
        return [manifest], [detected(ctx)]

    def test_clean_vs_unknown(self):
        h, o = self.fixtures()
        self.assertEqual("CLEAN", audit(h, o, access_complete=True)["result"])
        self.assertEqual("UNKNOWN", audit(h, o)["result"])
        self.assertEqual("UNKNOWN", audit([], o, access_complete=True)["result"])

    def test_canary_prompt_and_revealing_resource(self):
        h, o = self.fixtures()
        h.append({"event_type": "RUN_STARTED", "payload": {"canary_token": "secret-canary-7"}})
        surfaces = [{"source_component": "decision_llm", "field": "prompt", "text": "secret-canary-7"}]
        self.assertEqual("LEAK_DETECTED", audit(h, o, surfaces, True)["result"])
        h[0]["payload"]["entries"][0]["value"] = "frontend-cpu_stress-21"
        self.assertIn("REVEALING_RESOURCE", audit(h, o, access_complete=True)["findings"])

    def test_natural_ip_allowlist(self):
        h, o = self.fixtures()
        h[0]["payload"]["entries"].append({"kind": "ip", "value": "192.0.2.9", "class": "OBSERVABLE", "o_visible": False,
            "allowed_o": [{"source_component": "detector", "field": "payload.description"}]})
        o[0]["payload"]["description"] = "Observed source 192.0.2.9"
        self.assertEqual("CLEAN", audit(h, o, access_complete=True)["result"])
        o[0]["target"]["service"] = "192.0.2.9"
        self.assertIn("OBSERVABLE_OUTSIDE_ALLOWLIST", audit(h, o, access_complete=True)["findings"])


class BoundaryTests(unittest.TestCase):
    def test_actual_healer_r1_entrypoints_cannot_execute_legacy_actions(self):
        tree = ast.parse((ROOT / "agent-orchestrator/hephaestus/main.py").read_text())
        functions = [copy.deepcopy(n) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in {"process_alert", "manual_heal"}]
        for function in functions:
            function.decorator_list = []
        class Rejected(Exception):
            def __init__(self, **kw):
                self.code = kw["status_code"]
        scope = {"r1_client": object(), "HTTPException": Rejected}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "actual-healer-entrypoints", "exec"), scope)
        with self.assertRaisesRegex(ValueError, "R1 accepts only"):
            scope["process_alert"]({"type": "HIGH_CPU", "affectedService": "frontend"})
        with self.assertRaises(Rejected) as caught:
            asyncio.run(scope["manual_heal"]({}))
        self.assertEqual(409, caught.exception.code)

    def test_metrics_allowlist_and_log_filter_cannot_be_removed(self):
        telemetry = Telemetry("http://prom", "http://es", ["known-query"])
        with self.assertRaises(ValueError):
            telemetry.metrics('sum(secret{namespace="zero-door"})')
        with patch.object(telemetry, "fetch", return_value={"hits": {"hits": []}}) as fetch:
            telemetry.logs({"query": {"match_all": {}}, "size": 9999})
            request = fetch.call_args.args[1]
            self.assertEqual(100, request["size"])
            self.assertEqual("target-app", request["query"]["bool"]["filter"][0]["term"]["kubernetes.namespace_name.keyword"])
        with self.assertRaises(ValueError):
            telemetry.logs({"query": {"match_all": {}}, "aggs": {"secret": {}}})
        with patch.object(telemetry, "fetch", return_value={"hits": {"hits": [{"_source": {"kubernetes": {"namespace_name": "zero-door"}}}]}}):
            with self.assertRaisesRegex(ValueError, "UPSTREAM_NAMESPACE"):
                telemetry.logs({"query": {"match_all": {}}})

    def test_detector_retry_preserves_envelope(self):
        class Fake:
            producer = Producer("detector", "test", CLOCK)
            sent = []
            def context(self):
                return ctx
            def publish(self, event):
                self.sent.append(copy.deepcopy(event))
                if len(self.sent) == 1:
                    raise TimeoutError()
        ctx = context()
        fake = Fake()
        detector = Detector(fake)
        with self.assertRaises(TimeoutError):
            detector.publish("HIGH_CPU", "frontend", "cpu", 0.9, 0.8, "natural symptom", "WARNING")
        detector.publish("HIGH_CPU", "frontend", "cpu", 0.99, 0.8, "changed symptom", "WARNING")
        self.assertEqual(fake.sent[0], fake.sent[1])

    def test_rules_dedup_and_mode_boundary(self):
        for group, expected in (("B0", 0), ("B1", 1), ("B2", 0), ("B3", 0), ("BM", 0)):
            ctx = context(group)
            class Fake:
                trial = ctx["trial_id"]
                producer = Producer("decision_rules", "test", CLOCK)
                rows = [{"envelope": detected(ctx)}]
                def records(self):
                    return self.rows
                def publish(self, event):
                    self.rows.append({"envelope": event})
            fake = Fake()
            RulesConsumer(fake, lambda *_: "SCALE_UP").poll()
            RulesConsumer(fake, lambda *_: "SCALE_UP").poll()
            decisions = [r["envelope"] for r in fake.rows if r["envelope"]["event_type"] == "DECISION"]
            self.assertEqual(expected, len(decisions), group)
            if decisions:
                self.assertEqual(fake.rows[0]["envelope"]["event_id"], decisions[0]["causation_id"])
                self.assertIsNone(validate(decisions[0]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
