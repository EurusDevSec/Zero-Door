"""Real agent functions over loopback HTTP; requires both agents' dependencies.

No startup hook, Kafka, Kubernetes, detector fault, heal or LLM is executed. Elasticsearch is a
loopback fake upstream behind the real gateway proxy; Gaia uses its real Elasticsearch client.
"""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id
from event_pipeline.gateway import Gateway, server
from event_pipeline.store import Archive
from event_pipeline.telemetry import Telemetry


class FakeElasticsearch(BaseHTTPRequestHandler):
    """Upstream ES stand-in: records each search body and returns one target-app hit."""
    seen = []

    def log_message(self, *_args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        FakeElasticsearch.seen.append((self.path, json.loads(body)))
        data = json.dumps({"took": 1, "timed_out": False, "hits": {"hits": [{"_source": {
            "message": "container OOMKilled", "kubernetes": {"namespace_name": "target-app",
            "pod_name": "frontend-7d9f-abc12", "container_name": "server"}}}]}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class AgentHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.archive = Archive(self.directory / "O", "O")
        self.keys = {role: (role + "-test-token").ljust(48, "x") for role in ("harness", "detector", "decision_rules", "reader")}
        FakeElasticsearch.seen = []
        self.upstream = ThreadingHTTPServer(("127.0.0.1", 0), FakeElasticsearch)
        threading.Thread(target=self.upstream.serve_forever, daemon=True).start()
        telemetry = Telemetry("http://127.0.0.1:1", "http://127.0.0.1:%d" % self.upstream.server_port, [])
        self.gateway = Gateway(self.archive, self.keys, telemetry=telemetry)
        self.http = server(self.gateway, ("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.ctx = {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
                    "group": "B1", "config_ref": "sha256:" + "1" * 64, "method_version": "source-http-test"}
        clock = {"clock_id": "clk_test", "clock_source": "UNKNOWN", "resolution_ms": None}
        producer = Producer("harness", "test", clock)
        run = dict(self.ctx, trial_id=None)
        for event in (producer.event(run, "RUN_CONTEXT", {}, "o.context"), producer.event(self.ctx, "TRIAL_CONTEXT", {}, "o.context")):
            self.gateway.submit(event, "harness", "test-request")
        # One key file per actor (ZR9-04); each agent module reads its own at import.
        self.key_files = {}
        for actor, roles in (("gaia", ("detector", "reader")), ("hephaestus", ("decision_rules", "reader"))):
            self.key_files[actor] = self.directory / (actor + "-keys.json")
            self.key_files[actor].write_text(json.dumps({k: self.keys[k] for k in roles}))
        self.environment = patch.dict(os.environ, {"ZD_EVENT_URL": "http://127.0.0.1:" + str(self.http.server_port),
            "ZD_RUN_ID": self.ctx["run_id"], "ZD_TRIAL_ID": self.ctx["trial_id"],
            "ZD_PRODUCER_VERSION": "source-http-test", "ZD_CLOCK_ID": "clk_test", "ZD_CLOCK_SOURCE": "UNKNOWN"})
        self.environment.start()
        self.gaia, self.healer = self.load("gaia"), self.load("hephaestus")
        self.network_guards = [patch.object(module, name, side_effect=AssertionError("no direct Kafka in offline test"))
                               for module, name in ((self.gaia, "KafkaProducer"), (self.healer, "KafkaProducer"), (self.healer, "KafkaConsumer"))]
        for guard in self.network_guards:
            guard.start()

    def load(self, name, keys=None):
        os.environ["ZD_O_KEYS_FILE"] = str(keys or self.key_files[name])
        spec = importlib.util.spec_from_file_location("source_http_" + name, ROOT / "agent-orchestrator" / name / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def tearDown(self):
        for guard in self.network_guards:
            guard.stop()
        self.environment.stop()
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(2)
        self.upstream.shutdown()
        self.upstream.server_close()
        self.archive.close()
        self.temp.cleanup()

    def events(self):
        return [r["envelope"] for r in self.archive.records(self.ctx["run_id"])]

    def test_actual_gaia_http_and_healer_consumer_keep_ids(self):
        self.gaia.publish_alert("HIGH_CPU", "frontend", "fixture", 90.0, 80.0, "Synthetic transport only", "WARNING")
        class TickComplete(Exception):
            pass
        with patch.object(self.healer.time, "sleep", side_effect=TickComplete), \
             patch.object(self.healer, "action_scale_up", side_effect=AssertionError("must not heal")):
            with self.assertRaises(TickComplete):
                self.healer._kafka_consumer_thread()
        events = self.events()
        detection = next(e for e in events if e["event_type"] == "DETECTED")
        decision = next(e for e in events if e["event_type"] == "DECISION")
        for key in ("run_id", "trial_id", "incident_id"):
            self.assertEqual(self.ctx[key], detection[key])
            self.assertEqual(self.ctx[key], decision[key])
        self.assertEqual(detection["event_id"], decision["causation_id"])
        self.assertEqual("SCALE_UP", decision["payload"]["proposal"]["action_type"])
        self.assertEqual("detector", detection["source_component"])
        self.assertEqual("decision_rules", decision["source_component"])
        self.assertFalse(any(e["event_type"] in {"HEAL_STARTED", "ACTION_COMPLETED", "RECOVERY_VERIFIED"} for e in events))

    def test_actual_r1_entrypoints_and_telemetry_use_boundary(self):
        self.assertIsNone(self.gaia.get_kafka_producer())
        self.assertEqual(self.gaia.r1_client.url + "/prometheus", self.gaia.PROMETHEUS_URL)
        self.assertEqual(self.gaia.r1_client.url + "/elasticsearch", self.gaia.ELASTICSEARCH_URL)
        self.assertEqual("DISABLED_PENDING_GUARD", self.healer.healthz()["execution"])
        with self.assertRaises(ValueError):
            self.healer.process_alert({"type": "HIGH_CPU", "affectedService": "frontend"})
        with self.assertRaises(Exception) as caught:
            asyncio.run(self.healer.manual_heal({}))
        self.assertEqual(409, caught.exception.status_code)
        self.healer.heal_cooldowns[("frontend", "SCALE_UP")] = 1.0
        with self.assertRaises(Exception) as caught:
            self.healer.experiment_reset()
        self.assertEqual(409, caught.exception.status_code)
        self.assertIn(("frontend", "SCALE_UP"), self.healer.heal_cooldowns)  # no state cleared, no success claimed

    def test_actual_gaia_elasticsearch_client_goes_through_gateway_proxy(self):
        asyncio.run(self.gaia.poll_elasticsearch_logs())
        self.assertEqual(1, len(FakeElasticsearch.seen))
        path, sent = FakeElasticsearch.seen[0]
        self.assertEqual("/zero-door-logs-*/_search", path)
        self.assertEqual({"term": {"kubernetes.namespace_name.keyword": "target-app"}}, sent["query"]["bool"]["filter"][0])
        self.assertLessEqual(sent["size"], 100)
        detection = next(e for e in self.events() if e["event_type"] == "DETECTED")
        # Gaia names the service by container for log alerts (source behaviour, unchanged here).
        self.assertEqual(("HIGH_MEMORY", "server"), (detection["payload"]["rule_id"], detection["target"]["service"]))

    def test_agent_refuses_a_key_file_with_another_actors_role(self):
        shared = self.directory / "shared.json"
        shared.write_text(json.dumps({k: self.keys[k] for k in ("detector", "decision_rules", "reader")}))
        with self.assertRaises(ValueError):
            self.load("gaia", shared)
        with self.assertRaises(ValueError):
            self.load("hephaestus", shared)


if __name__ == "__main__":
    unittest.main(verbosity=2)
