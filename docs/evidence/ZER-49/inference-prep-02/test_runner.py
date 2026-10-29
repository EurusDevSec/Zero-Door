"""No inference: approval refusal and owned native-process timeout only."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("zer49_runner", HERE / "run_once_02.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class Checks(unittest.TestCase):
    def test_default_is_plan_only(self):
        with patch.object(sys, "argv", ["run_once_02.py"]), patch.object(runner, "run_child", side_effect=AssertionError("NO_CHILD")):
            self.assertEqual(0, runner.main())

    def test_owner_approval_required_before_child(self):
        with tempfile.TemporaryDirectory() as folder:
            auth = Path(folder) / "auth.json"
            auth.write_text(json.dumps({"approved": False}))
            with patch.object(runner, "run_child", side_effect=AssertionError("NO_CHILD")):
                with self.assertRaisesRegex(ValueError, "EXACT_OWNER_APPROVAL_REQUIRED"):
                    runner.execute(auth)

    def test_source_drift_stops_before_child(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            here = root / "evidence"
            (here / "inference-prep-02").mkdir(parents=True)
            (here / "continuation-proposal.md").write_text("offline")
            source = root / "source.py"
            source.write_text("changed")
            manifest = here / "inference-prep-02/source-manifest.json"
            manifest.write_text(json.dumps({"sha256": {"source.py": "0" * 64}}))
            auth = root / "auth.json"
            auth.write_text(json.dumps({"approved": True, "issue": "ZER-49",
                "proposal_sha256": runner.sha(here / "continuation-proposal.md"),
                "source_manifest_sha256": runner.sha(manifest)}))
            with patch.object(runner, "ROOT", root), patch.object(runner, "HERE", here), \
                    patch.object(runner, "run_child", side_effect=AssertionError("NO_CHILD")):
                with self.assertRaisesRegex(ValueError, "SOURCE_CHANGED"):
                    runner.execute(auth)
            self.assertFalse((here / "inference-02").exists())

    def test_owned_native_process_completes_and_is_reaped(self):
        result = runner.run_child([sys.executable, "-B", "-c", "pass"], dict(os.environ), timeout=5)
        self.assertEqual(0, result["exit_code"])
        self.assertTrue(result["process_reaped"])
        self.assertFalse(result["timed_out"])

    def test_stalled_owned_native_process_is_killed_and_reaped(self):
        result = runner.run_child([sys.executable, "-B", "-c", "import time; time.sleep(10)"], dict(os.environ), timeout=.1)
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["process_reaped"])
        self.assertNotEqual(0, result["exit_code"])

    def test_interrupted_wait_still_kills_and_reaps_native_child(self):
        original_popen, children = runner.subprocess.Popen, []
        def spawn(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            children.append(child)
            wait, count = child.wait, [0]
            def interrupted_wait(timeout=None):
                count[0] += 1
                if count[0] == 1:
                    raise KeyboardInterrupt
                return wait(timeout=timeout)
            child.wait = interrupted_wait
            return child
        with patch.object(runner.subprocess, "Popen", side_effect=spawn):
            with self.assertRaises(KeyboardInterrupt):
                runner.run_child([sys.executable, "-B", "-c", "import time; time.sleep(10)"], dict(os.environ))
        self.assertEqual(1, len(children))
        self.assertIsNotNone(children[0].poll())
        self.assertNotEqual(0, children[0].returncode)

    def test_previous_attempt_must_have_confirmed_cleanup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            here = root / "evidence"
            (here / "inference-prep-02").mkdir(parents=True)
            (here / "inference-01").mkdir()
            (here / "continuation-proposal.md").write_text("offline")
            manifest = here / "inference-prep-02/source-manifest.json"
            manifest.write_text(json.dumps({"sha256": {}}))
            (here / "inference-01/final-conclusion.json").write_text(json.dumps({
                "status": "NOT_MET", "cleanup": "UNKNOWN", "provider_calls": 1}))
            auth = root / "auth.json"
            auth.write_text(json.dumps({"approved": True, "issue": "ZER-49",
                "proposal_sha256": runner.sha(here / "continuation-proposal.md"),
                "source_manifest_sha256": runner.sha(manifest)}))
            with patch.object(runner, "ROOT", root), patch.object(runner, "HERE", here), \
                    patch.object(runner, "run_child", side_effect=AssertionError("NO_CHILD")):
                with self.assertRaisesRegex(ValueError, "PREVIOUS_ATTEMPT_NOT_CLOSED"):
                    runner.execute(auth)
            self.assertFalse((here / "inference-02").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
