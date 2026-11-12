"""Offline coverage of B1 source attribution and the role-bound B2 archive writer."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent-orchestrator"))

from event_pipeline.client import Client
from event_pipeline.contract import Producer, new_id
from event_pipeline.formal_capture import METHOD
from event_pipeline.formal_config import (RulesResolver, open_formal_o_sink, rules_options_from_env,
                                          rules_resolver_sha256)

CLOCK = {"clock_id": "observer-test", "clock_source": "HOST_SHARED", "resolution_ms": 1}


class FormalConfig(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.context = {"run_id": new_id("run"), "trial_id": new_id("trl"),
                        "incident_id": new_id("inc"), "group": "B2", "method_version": METHOD,
                        "config_ref": "sha256:" + "1" * 64}
        self.keys = self.directory / "test-o.json"
        self.keys.write_text(json.dumps({"decision_llm": "fake-writer", "reader": "fake-reader"}))
        self.environment = {"ZD_EVENT_URL": "http://127.0.0.1:1", "ZD_O_KEYS_FILE": str(self.directory / "unused"),
                            "ZD_RUN_ID": self.context["run_id"], "ZD_TRIAL_ID": self.context["trial_id"],
                            "ZD_CLOCK_ID": CLOCK["clock_id"], "ZD_PRODUCER_VERSION": "test"}
        network = patch("event_pipeline.client.urlopen", side_effect=AssertionError("OFFLINE_ONLY"))
        network.start()
        self.addCleanup(network.stop)

    def detection(self):
        return Producer("detector", "test", CLOCK).event(dict(self.context, group="B1"), "DETECTED", {
            "rule_id": "OBSERVED", "rule_version": "test", "signature": "observed/fixture",
            "metric": "observer_indicator", "value": 1, "threshold": 0, "severity": "WARNING",
            "description": "Synthetic observation"}, "o.alert",
            target={"namespace": "target-app", "service": "fixture", "flow": None}, alert_id=new_id("alt"))

    def decision(self):
        return Producer("decision_llm", "test", CLOCK).event(self.context, "DECISION", {
            "stage": "PROPOSAL", "decision_source": "LLM", "inputs": [], "response_kind": "ABSTAIN",
            "proposal": None, "fallback": False, "fallback_of": None, "prompt_version": "test",
            "prompt_sha256": "2" * 64, "evidence_package_version": "test"}, "o.decision",
            decision_id=new_id("dec"))

    def test_rules_resolver_joins_only_matching_observer_evidence(self):
        event = self.detection()
        resolver = RulesResolver(self.directory, run_id=self.context["run_id"], trial_id=self.context["trial_id"])
        path = self.directory / (event["event_id"] + ".json")
        self.assertEqual({"status": "OBSERVATION_MISSING"}, resolver(event))
        access = dict(run_id=event["run_id"], trial_id=event["trial_id"], detection_event_id=event["event_id"],
                      client_ip="192.0.2.7", fixture_uid="observed-fixture", source_method="XFF_AFTER_TRUSTED",
                      source_confidence="PROXY_CHAIN")
        path.write_text(json.dumps(access))
        self.assertEqual({"status": "RESOLVED", "source": "192.0.2.7", "fixture_uid": "observed-fixture",
                          "ttl_s": 180}, resolver(event))
        for changes in ({"trial_id": new_id("trl")}, {"detection_event_id": new_id("evt")},
                        {"seed": "hidden"}, {"source_confidence": "UNVERIFIED"}, {"client_ip": "bad"}):
            with self.subTest(changes=changes):
                path.write_text(json.dumps(dict(access, **changes)))
                self.assertEqual({"status": "RESOLVER_ERROR"}, resolver(event))
        path.write_bytes(b"x" * 8193)
        self.assertEqual({"status": "RESOLVER_ERROR"}, resolver(event))
        with self.assertRaisesRegex(ValueError, "RESOLVER_CONTEXT"):
            resolver(dict(event, run_id=new_id("run")))
        self.assertRegex(rules_resolver_sha256(), "^[a-f0-9]{64}$")

    def test_sink_publishes_only_a_decision_from_the_bound_context(self):
        event = self.decision()
        receipt = {"status": "RECORDED", "event_id": event["event_id"]}
        with patch.dict(os.environ, self.environment, clear=True), patch.object(Client, "request", return_value=receipt) as request:
            publish = open_formal_o_sink(self.context, keys_file=self.keys)
            self.assertEqual(receipt, publish(event))
            for field, value in (("trial_id", new_id("trl")), ("incident_id", new_id("inc")),
                                 ("method_version", "legacy"), ("config_ref", "sha256:" + "3" * 64),
                                 ("source_component", "guard")):
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, "DECISION_O_EVENT"):
                    publish(dict(event, **{field: value}))
            request.assert_called_once_with("/events", event)

    def test_wrong_role_or_trial_refuses_before_publish(self):
        with patch.dict(os.environ, self.environment, clear=True):
            with self.assertRaisesRegex(ValueError, "DECISION_O_CONTEXT"):
                open_formal_o_sink(dict(self.context, trial_id=new_id("trl")), keys_file=self.keys)
            self.keys.write_text(json.dumps({"decision_llm": "fake", "reader": "fake", "harness": "fake"}))
            with self.assertRaisesRegex(ValueError, "exactly the roles"):
                open_formal_o_sink(self.context, keys_file=self.keys)

    def test_rules_config_rejects_a_different_pin(self):
        client = SimpleNamespace(run=self.context["run_id"], trial=self.context["trial_id"])
        with patch.dict(os.environ, {"ZD_FORMAL_O_OBSERVATION_DIR": str(self.directory),
                                     "ZD_FORMAL_RULES_RESOLVER_SHA256": "0" * 64}, clear=True):
            with self.assertRaisesRegex(ValueError, "PIN_MISMATCH"):
                rules_options_from_env(client)
            os.environ["ZD_FORMAL_RULES_RESOLVER_SHA256"] = rules_resolver_sha256()
            options = rules_options_from_env(client)
            self.assertIsInstance(options["resolve_o"], RulesResolver)
            self.assertEqual(rules_resolver_sha256(), options["resolver_sha256"])

    def test_gaia_cli_formal_requires_o_writer_before_opening_model_or_journal(self):
        from gaia.diagnosis_cli import open_diagnoser, PURPOSE

        config = {"purpose": PURPOSE, "benchmark_eligible": False, "context": self.context,
                  "max_calls": 1, "max_reserved_tokens": 2000, "max_estimated_usd": 0.001, "duration_s": 60}
        with patch.dict(os.environ, self.environment, clear=True), patch("gaia.diagnosis_cli.HttpxTransport") as model:
            with self.assertRaisesRegex(ValueError, "DECISION_O_CONFIGURATION"):
                open_diagnoser(config, self.directory)
            model.assert_not_called()
            self.assertFalse((self.directory / self.context["run_id"]).exists())

            os.environ["ZD_FORMAL_O_KEYS_FILE"] = str(self.keys)
            engine, journal = open_diagnoser(config, self.directory)
            self.addCleanup(journal.close)
            event = self.decision()
            receipt = {"status": "RECORDED", "event_id": event["event_id"]}
            with patch.object(Client, "request", return_value=receipt) as request:
                self.assertEqual(receipt, engine.formal_o_sink(event))
                request.assert_called_once_with("/events", event)
