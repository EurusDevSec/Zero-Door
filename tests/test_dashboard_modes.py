"""ZER-11 AC-03 / ZER-39: MANUAL, RULES and AI stay apart at the entrypoints that actually run.

The real ZER-9 gateway and archive serve over loopback HTTP; Gaia and Hephaestus are the real
modules with their real R1 client. The consumer is Hephaestus' own loop (one tick), the manual path
is POST /heal/trigger through ASGI. Kafka, Kubernetes and models are never contacted. The production
executor stays disabled; a fake executor is set only in the positive-control tests to prove the
refusals are mode refusals and not "everything is off".
"""
import asyncio
import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import unittest
import uuid
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id, now  # noqa: E402
from event_pipeline.gateway import Gateway, server  # noqa: E402
from event_pipeline.store import Archive  # noqa: E402
from event_pipeline.telemetry import Telemetry  # noqa: E402

GUARD = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())
CLOCK = {"clock_id": "clk_test", "clock_source": "UNKNOWN", "resolution_ms": None}
FORBIDDEN_IN_B0 = {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}


class TickComplete(Exception):
    pass


class Lab:
    """One run/trial of `group` behind the real gateway, with Gaia and Hephaestus loaded against it."""
    def __init__(self, group):
        self.temp = tempfile.TemporaryDirectory()
        d = Path(self.temp.name)
        self.archive = Archive(d / "O", "O")
        self.keys = {role: (role + "-test-token").ljust(48, "x")
                     for role in ("harness", "detector", "decision_rules", "operator_console", "reader")}
        telemetry = Telemetry("http://127.0.0.1:1", "http://127.0.0.1:1", [])
        self.gateway = Gateway(self.archive, self.keys, telemetry=telemetry)
        self.http = server(self.gateway, ("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.ctx = {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
                    "group": group, "config_ref": "sha256:" + "1" * 64, "method_version": "zer11-modes"}
        harness = Producer("harness", "test", CLOCK)
        for event in (harness.event(dict(self.ctx, trial_id=None), "RUN_CONTEXT", {}, "o.context"),
                      harness.event(self.ctx, "TRIAL_CONTEXT", {}, "o.context")):
            self.gateway.submit(event, "harness", "test-request")
        files = {}
        for actor, roles in (("gaia", ("detector", "reader")), ("hephaestus", ("decision_rules", "reader"))):
            files[actor] = d / (actor + "-keys.json")
            files[actor].write_text(json.dumps({k: self.keys[k] for k in roles}))
        self.heal_operator = {"id": "heal-fixture", "purpose": "heal-operator", "secret": "offline-heal-operator-token-0000000000"}
        (d / "heal-operator.json").write_text(json.dumps(self.heal_operator))
        policy = dict(GUARD["policy"], context={k: self.ctx[k] for k in ("run_id", "trial_id", "group")})
        (d / "policy.json").write_text(json.dumps(policy))
        self.env = {
            "ZD_EVENT_URL": "http://127.0.0.1:" + str(self.http.server_port), "ZD_RUN_ID": self.ctx["run_id"],
            "ZD_TRIAL_ID": self.ctx["trial_id"], "ZD_PRODUCER_VERSION": "zer11-modes", "ZD_CLOCK_ID": "clk_test",
            "ZD_CLOCK_SOURCE": "UNKNOWN", "ZD_COMMAND_POLICY_FILE": str(d / "policy.json"),
            "ZD_OPERATOR_TOKEN_FILE": str(d / "heal-operator.json"), "ZD_COMMAND_LEDGER_FILE": str(d / "claims.sqlite")}
        self.environment = patch.dict(os.environ, self.env)
        self.environment.start()
        self.gaia = self.load("gaia", files["gaia"])
        self.healer = self.load("hephaestus", files["hephaestus"])
        self.guards = [patch.object(module, name, side_effect=AssertionError("no Kafka/Kubernetes/heal offline"))
                       for module, name in ((self.gaia, "KafkaProducer"), (self.healer, "KafkaProducer"), (self.healer, "KafkaConsumer"),
                                            (self.healer, "init_k8s"), (self.healer, "action_scale_up"), (self.healer, "action_restart_pod"))]
        for guard in self.guards:
            guard.start()

    @staticmethod
    def load(name, keys):
        os.environ["ZD_O_KEYS_FILE"] = str(keys)
        spec = importlib.util.spec_from_file_location("zer11_modes_" + name, ROOT / "agent-orchestrator" / name / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def close(self):
        for guard in self.guards:
            guard.stop()
        self.environment.stop()
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(2)
        self.archive.close()
        self.temp.cleanup()

    def events(self):
        return [r["envelope"] for r in self.archive.records(self.ctx["run_id"])]

    def of(self, event_type):
        return [e for e in self.events() if e["event_type"] == event_type]

    def consumer_tick(self):
        """One iteration of Hephaestus' actual R1 consumer loop."""
        with patch.object(self.healer.time, "sleep", side_effect=TickComplete):
            try:
                self.healer._kafka_consumer_thread()
            except TickComplete:
                pass

    def operator_decision(self, source="operator_console"):
        alert = self.of("DETECTED")[0]
        kind = {"operator_console": "MANUAL", "decision_rules": "RULES"}[source]
        # Built in a group the source may write in, then given this run's group: a forged envelope
        # (e.g. RULES in BM, anything in B0) that only the gateway's own validation can stop.
        allowed = {"operator_console": "BM", "decision_rules": "B1"}[source]
        event = Producer(source, "test", CLOCK).event(dict(self.ctx, group=allowed), "DECISION", {
            "stage": "PROPOSAL", "decision_source": kind, "inputs": [{"event_id": alert["event_id"], "received_at": now()}],
            "response_kind": "ACTION", "proposal": {"action_type": "SCALE_UP", "params": {"service": "frontend"}},
            "fallback": False, "fallback_of": None, "prompt_version": None, "prompt_sha256": None,
            "evidence_package_version": "o-envelope/1.0.0"}, "o.decision",
            target={"namespace": "target-app", "service": "frontend", "flow": None},
            decision_id=new_id("dec"), causation_id=alert["event_id"])
        event["group"] = self.ctx["group"]
        try:
            self.gateway.submit(event, source, "operator-request")
        except Exception:
            pass  # a quarantined decision stays out of the records, which is what the trigger reads
        return event

    async def trigger(self, decision_id, token=None):
        headers = {"Authorization": "Bearer " + (token or self.heal_operator["secret"]), "Idempotency-Key": str(uuid.uuid4())}
        # Several labs may be open at once: the guard reads its policy/key files from this lab's env.
        with patch.dict(os.environ, self.env):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.healer.app), base_url="http://offline") as client:
                return await client.post("/heal/trigger", json={"decision_id": decision_id}, headers=headers)


class ConsumerModes(unittest.TestCase):
    def test_only_b1_auto_decides_through_the_real_consumer(self):
        for group in ("B0", "BM", "B1", "B2", "B3"):
            with self.subTest(group=group):
                lab = Lab(group)
                try:
                    lab.gaia.publish_alert("HIGH_CPU", "frontend", "fixture", 90.0, 80.0, "Synthetic transport only", "WARNING")
                    with self.assertLogs("hephaestus-agent", level="WARNING") if group != "B1" else _no_audit(self) as logs:
                        lab.consumer_tick()
                    decisions = lab.of("DECISION")
                    if group == "B1":
                        # Positive control: the path is live, the source is RULES and it is not an action.
                        self.assertEqual(1, len(decisions))
                        d = decisions[0]
                        self.assertEqual(("decision_rules", "RULES", "B1"), (d["source_component"], d["payload"]["decision_source"], d["group"]))
                        lab.consumer_tick()  # replay of the same alert: no second decision
                        self.assertEqual(1, len(lab.of("DECISION")))
                    else:
                        self.assertEqual([], decisions)
                        audit = [json.loads(line.split("MODE_AUDIT ", 1)[1]) for line in logs.output if "MODE_AUDIT" in line]
                        self.assertEqual([{"route": "consumer", "reason": "AUTO_DECISION_DISABLED_FOR_GROUP",
                                           "context": {"run_id": lab.ctx["run_id"], "trial_id": lab.ctx["trial_id"], "group": group}}], audit)
                    self.assertEqual([], [e for e in lab.events() if e["event_type"] in FORBIDDEN_IN_B0 - {"DECISION"}])
                finally:
                    lab.close()


class _no_audit:
    def __init__(self, case):
        self.case = case

    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


class ManualTrigger(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.labs = []

    async def asyncTearDown(self):
        for lab in self.labs:
            lab.close()

    def lab(self, group):
        lab = Lab(group)
        self.labs.append(lab)
        lab.gaia.publish_alert("HIGH_CPU", "frontend", "fixture", 90.0, 80.0, "Synthetic transport only", "WARNING")
        return lab

    async def test_bm_operator_decision_is_admitted_but_production_executor_stays_disabled(self):
        lab = self.lab("BM")
        decision = lab.operator_decision()
        self.assertIsNone(lab.healer.R1_EXECUTOR)
        with self.assertLogs("hephaestus-agent", level="WARNING") as logs:
            response = await lab.trigger(decision["decision_id"])
        self.assertEqual((409, {"detail": "R1_EXECUTOR_DISABLED"}), (response.status_code, response.json()))
        self.assertTrue(any("R1_EXECUTOR_DISABLED" in line and "MODE_AUDIT" in line for line in logs.output))
        self.assertEqual([], [e for e in lab.events() if e["event_type"] in {"GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}])

    async def test_positive_control_one_action_per_operator_decision(self):
        lab = self.lab("BM")
        decision = lab.operator_decision()
        effects = []
        lab.healer.R1_EXECUTOR = lambda proposal: effects.append(proposal) or {"status": "FAKE_EXECUTED"}
        first = await lab.trigger(decision["decision_id"])
        replay = await lab.trigger(decision["decision_id"])
        self.assertEqual((200, {"status": "FAKE_EXECUTED"}), (first.status_code, first.json()))
        self.assertEqual((200, {"status": "FAKE_EXECUTED"}), (replay.status_code, replay.json()))
        self.assertEqual([{"action_type": "SCALE_UP", "params": {"service": "frontend"}}], effects)

    async def test_mode_refusals_hold_even_with_an_executor(self):
        effects = []
        cases = []
        bm = self.lab("BM")
        rules = bm.operator_decision(source="decision_rules")  # an automatic decision in MANUAL is quarantined
        cases.append((bm, rules["decision_id"], "DECISION_MISSING_OR_AMBIGUOUS"))
        b1 = self.lab("B1")
        b1.consumer_tick()
        cases.append((b1, b1.of("DECISION")[0]["decision_id"], "MANUAL_GROUP_REQUIRED"))  # RULES is never run by the manual path
        b0 = self.lab("B0")
        cases.append((b0, new_id("dec"), "DECISION_MISSING_OR_AMBIGUOUS"))
        for lab, decision_id, reason in cases:
            with self.subTest(group=lab.ctx["group"], reason=reason):
                lab.healer.R1_EXECUTOR = lambda proposal: effects.append(proposal)
                with self.assertLogs("hephaestus-agent", level="WARNING") as logs:
                    response = await lab.trigger(decision_id)
                self.assertEqual((409, {"detail": reason}), (response.status_code, response.json()))
                audit = [json.loads(line.split("MODE_AUDIT ", 1)[1]) for line in logs.output if "MODE_AUDIT" in line]
                self.assertEqual(reason, audit[0]["reason"])
                self.assertEqual(lab.ctx["group"], audit[0]["context"]["group"])
        self.assertEqual([], effects)
        # B0: the refusal is an operational log line; no decision/guard/action event is written.
        self.assertEqual([], [e for e in b0.events() if e["event_type"] in FORBIDDEN_IN_B0])

    async def test_b0_with_a_forged_operator_decision_is_still_refused(self):
        lab = self.lab("B0")
        forged = lab.operator_decision()  # the gateway quarantines it: DECISION is forbidden in B0
        self.assertEqual([], lab.of("DECISION"))
        effects = []
        lab.healer.R1_EXECUTOR = lambda proposal: effects.append(proposal)
        response = await lab.trigger(forged["decision_id"])
        self.assertEqual(409, response.status_code)
        self.assertEqual([], effects)

    async def test_trigger_needs_the_trusted_context_and_heal_operator(self):
        lab = self.lab("BM")
        decision = lab.operator_decision()
        lab.healer.R1_EXECUTOR = lambda proposal: self.fail("must not execute")
        response = await lab.trigger(decision["decision_id"], token="wrong")
        self.assertEqual(401, response.status_code)
        policy = json.loads(Path(lab.env["ZD_COMMAND_POLICY_FILE"]).read_text())
        policy["context"]["trial_id"] = new_id("trl")
        Path(lab.env["ZD_COMMAND_POLICY_FILE"]).write_text(json.dumps(policy))
        response = await lab.trigger(decision["decision_id"])
        self.assertEqual((409, {"detail": "RUN_CONTEXT"}), (response.status_code, response.json()))


class ProductionWiring(unittest.TestCase):
    def test_executor_seam_is_never_configured_in_production(self):
        source = (ROOT / "agent-orchestrator/hephaestus/main.py").read_text(encoding="utf-8")
        self.assertEqual(["R1_EXECUTOR = None"], re.findall(r"^R1_EXECUTOR\s*=.*$", source, re.M))
        self.assertEqual(1, len(re.findall(r"R1_EXECUTOR\(", source)))  # only inside the once() wrapper
        self.assertNotRegex(source, r"getenv\([^)]*EXECUTOR|environ[^\n]*EXECUTOR")
        self.assertNotIn("executor=", re.sub(r"ModeGate\.dispatch\([^\n]*executor=executor\)", "", source))


if __name__ == "__main__":
    unittest.main(verbosity=2)
