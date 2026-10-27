"""Regression for the actual ZER-42 runtime packaging and cleanup failures; no lab I/O."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
sys.path.insert(0, str(ROOT / "docs/evidence/ZER-42/runtime-prep"))
from event_pipeline import contract
import sqli_executor_runtime as runtime
from render import render


class Packaging(unittest.TestCase):
    def test_actual_rendered_context_round_trips_archive(self):
        prior = ROOT / "docs/evidence/ZER-42/runtime-02/zer42-74545a02be28"
        result = json.loads((prior / "results-vulnerable.json").read_bytes())[2]["value"]
        images = ("zer41-fixture:" + "a" * 12, "traefik@sha256:" + "b" * 64,
                  "zer42-worker:" + "c" * 12, "zer42-nemesis:" + "d" * 12)
        docs = render(prior.name, *images)
        policy = next(d for d in docs if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "zer42-policy")
        context = json.loads(policy["data"]["policy.json"])["context"]
        self.assertTrue(contract.valid_id(context["run_id"], "run"))
        self.assertTrue(contract.valid_id(context["trial_id"], "trl"))
        # Stable per-run IDs, including the UUID version/variant bits required by zd-event/1.
        again = render(prior.name, *images)
        self.assertEqual(policy, next(d for d in again if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "zer42-policy"))
        context.update(incident_id=contract.new_id("inc"), method_version="zer42-packaging-test/1", config_ref="sha256:" + "a" * 64)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            bundle = runtime.prepare_bundle(result, context, p / "bundle.json")
            receipt = runtime.archive_bundle(bundle, p / "archive", p / "export")
            self.assertEqual("CONFIRMED", receipt["checked"][0]["status"])
            self.assertEqual(receipt, runtime.recheck_export(p / "export"))
        # Historical invalid IDs stay rejected. The fix must not relax contract.validate.
        context["run_id"] = "run_74545a02be280000000000000000000000"
        with self.assertRaisesRegex(ValueError, "INVALID_ID"):
            runtime.build_fault_result(context, result, runtime.executor_clock(result))

    def test_owned_consumers_stop_before_topic_deletion(self):
        path = ROOT / "docs/evidence/ZER-42/runtime-prep/run.py"
        spec = importlib.util.spec_from_file_location("zer42_acceptance_run", path)
        module = importlib.util.module_from_spec(spec)
        with patch.object(sys, "argv", [str(path)]):
            spec.loader.exec_module(module)
        module.namespace_creation_attempted = True
        module.namespace_uid = "owned-uid"
        module.topics_created = ["owned.commands", "owned.results"]
        seen = []
        def get(*args, **kwargs):
            seen.append("get-owner")
            return {"metadata": {"uid": "owned-uid", "labels": {"zero-door.io/run": module.RUN}}}
        def kube(*args, **kwargs):
            seen.append("kube-" + args[0])
            class Result:
                stdout = b""
            return Result()
        def topic(op, name, **kwargs):
            seen.append("topic-" + op)
            class Result:
                stdout = b""
            return Result()
        with patch.object(module, "get", get), patch.object(module, "kube", kube), patch.object(module, "topic", topic):
            self.assertEqual([], module.cleanup())
        self.assertLess(seen.index("kube-wait"), seen.index("topic-delete"))
        self.assertEqual(2, seen.count("topic-delete"))
        # A wrong namespace owner must neither delete that namespace nor touch topics with active consumers.
        def wrong_owner(*args, **kwargs):
            return {"metadata": {"uid": "foreign-uid", "labels": {"zero-door.io/run": "foreign-run"}}}
        with patch.object(module, "get", wrong_owner), patch.object(module, "kube") as kube_call, patch.object(module, "topic") as topic_call:
            failures = module.cleanup()
        self.assertTrue(failures)
        kube_call.assert_not_called()
        topic_call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
