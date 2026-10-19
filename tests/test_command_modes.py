"""Locked contract mode semantics, with genuine valid proposals and a fake executor."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id, now, validate
from hephaestus.command_guard import ModeGate, GuardedRules
from nemesis.command_guard import Refused


def decision(group="B1", source="decision_rules", kind="RULES", fallback=False):
    context = {"run_id": new_id("run"), "trial_id": new_id("trl"), "group": group}
    full = dict(context, method_version="offline-mode", config_ref="sha256:" + "1" * 64, incident_id=new_id("inc"))
    producer = Producer(source, "offline-test", {"clock_id": "clk_test", "clock_source": "UNKNOWN", "resolution_ms": None})
    base_group = {"operator_console": "BM", "decision_llm": "B2", "decision_single_llm": "B3"}.get(source, group if fallback and group in {"B2", "B3"} else "B1")
    full["group"] = base_group
    event = producer.event(full, "DECISION", {
        "stage": "PROPOSAL", "decision_source": kind, "inputs": [{"event_id": new_id("evt"), "received_at": now()}],
        "response_kind": "ACTION", "proposal": {"action_type": "SCALE_UP", "params": {"service": "frontend"}},
        "fallback": fallback, "fallback_of": new_id("dec") if fallback else None,
        "prompt_version": "offline" if kind in {"LLM", "SINGLE_LLM"} else None,
        "prompt_sha256": "sha256:" + "a" * 64 if kind in {"LLM", "SINGLE_LLM"} else None,
        "evidence_package_version": "o-envelope/1.0.0",
    }, "o.decision", target={"namespace": "target-app", "service": "frontend", "flow": None}, decision_id=new_id("dec"))
    event["group"] = group  # Deliberately raw-invalid combinations test the consuming gate.
    return context, event


class ModeTests(unittest.TestCase):
    def test_allowed_proposals_and_production_executor_disabled(self):
        fixtures = json.loads((ROOT / "tests/fixtures/zer12/modes.json").read_text())
        for group, rows in fixtures["groups"].items():
            for source, kind, initiator in rows:
                with self.subTest(group=group, source=source):
                    ctx, event = decision(group, source, kind, source == "decision_rules" and group in {"B2", "B3"})
                    self.assertIsNone(validate(event, "O", source))
                    fallback = None
                    if event["payload"]["fallback"]:
                        _, fallback = decision(group, "decision_llm" if group == "B2" else "decision_single_llm", "LLM" if group == "B2" else "SINGLE_LLM")
                        fallback.update(ctx)
                        fallback["decision_id"] = event["payload"]["fallback_of"]
                        fallback["payload"].update(response_kind="TIMEOUT", proposal=None)
                        with self.assertRaisesRegex(Refused, "FALLBACK_EVIDENCE"):
                            ModeGate.admit(ctx, event, source, initiator)
                    effects = []
                    self.assertEqual("fake-only", ModeGate.dispatch(ctx, event, source, initiator, lambda p: effects.append(p) or "fake-only", fallback_decision=fallback))
                    self.assertEqual(1, len(effects))
                    with self.assertRaisesRegex(Refused, "R1_EXECUTOR_DISABLED"):
                        ModeGate.dispatch(ctx, event, source, initiator, fallback_decision=fallback)

    def test_blocked_context_source_manual_fallback_and_no_action(self):
        ctx, event = decision()
        cases = []
        for group in ["B0", "BM", "B2", "B3", "AUTO"]:
            c = dict(ctx, group=group)
            e = deepcopy(event); e["group"] = group
            cases.append((c, e, "decision_rules", "AUTO"))
        cases += [(dict(ctx, trial_id=new_id("trl")), event, "decision_rules", "AUTO"),
                  (ctx, event, "operator_console", "AUTO"), (ctx, event, "decision_rules", "OPERATOR")]
        no_action = deepcopy(event); no_action["payload"].update(response_kind="NO_ACTION", proposal=None)
        analysis = deepcopy(event); analysis["payload"]["stage"] = "ANALYSIS"
        cases += [(ctx, no_action, "decision_rules", "AUTO"), (ctx, analysis, "decision_rules", "AUTO")]
        effects = []
        for c, e, source, initiator in cases:
            with self.subTest(group=c["group"], source=source, initiator=initiator), self.assertRaises(Refused):
                ModeGate.dispatch(c, e, source, initiator, effects.append)
        self.assertEqual([], effects)

    def test_rules_wrapper_uses_trusted_context_before_locked_adapter(self):
        calls = []
        class Rules:
            def poll(self):
                calls.append("decision")
        class Client:
            run, trial, group = new_id("run"), new_id("trl"), "B0"
            def context(self):
                return dict(run_id=self.run, trial_id=self.trial, group=self.group)
        client = Client()
        wrapped = GuardedRules(client, Rules())
        for group in ("B0", "BM", "B2", "B3"):
            client.group = group
            wrapped.poll()
        self.assertEqual([], calls)
        client.group = "B1"
        wrapped.poll()
        self.assertEqual(["decision"], calls)
        client.group = "UNKNOWN"
        with self.assertRaises(Refused):
            wrapped.poll()
        self.assertEqual(["decision"], calls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
