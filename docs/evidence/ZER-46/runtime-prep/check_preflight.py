"""Offline guard/counter checks; deny all subprocesses, never call the live execute method."""
import importlib.util
from pathlib import Path
import threading
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("zer46_preflight", Path(__file__).with_name("preflight.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Preflight(unittest.TestCase):
    def setUp(self):
        self.processes = patch.object(module.subprocess, "run", side_effect=AssertionError("no real process"))
        self.processes.start()

    def tearDown(self):
        self.processes.stop()

    def test_creation_and_import_have_no_runtime_effect(self):
        lab = module.Lab()
        self.assertEqual(lab.requests, 0)
        self.assertGreater(lab.deadline - lab.work_end, 299)

    def test_probe_budget_and_guard_stop_before_http(self):
        lab = module.Lab()
        lab.flow = Mock(per_sample_requests=9)
        lab.requests = 24
        with self.assertRaisesRegex(RuntimeError, "BOUTIQUE_REQUEST_BUDGET"):
            lab.probe()
        lab.requests = 0
        lab.stop.set()
        with self.assertRaisesRegex(RuntimeError, "GUARD_STOP"):
            lab.probe()
        lab.flow.run.assert_not_called()

    def test_slow_success_is_not_healthy_and_cleanup_failure_is_fatal(self):
        lab = module.Lab()
        lab.save = Mock()
        lab.flow = Mock(per_sample_requests=9)
        result = {"requests": 6, "ok": True, "elapsed_ms": 2001, "cleanup": {"cart": "DONE"}}
        lab.flow.run.return_value = result
        self.assertFalse(lab.probe()["healthy"])
        self.assertEqual(lab.requests, 6)
        lab.flow.run.return_value = dict(result, cleanup={"cart": "UNKNOWN"})
        with self.assertRaisesRegex(RuntimeError, "BUSINESS_CLEANUP_UNRESOLVED"):
            lab.probe()

    def test_inventory_identity_changes_are_not_ignored(self):
        before = {"items": [{"kind": "Deployment", "metadata": {"name": "x", "namespace": "target-app", "uid": "a"},
                             "spec": {"replicas": 1}}]}
        after = {"items": [{"kind": "Deployment", "metadata": {"name": "x", "namespace": "target-app", "uid": "b"},
                            "spec": {"replicas": 1}}]}
        self.assertNotEqual(module.Lab.specs(before), module.Lab.specs(after))


if __name__ == "__main__":
    unittest.main()
