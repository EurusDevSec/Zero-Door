"""Offline checks of runner boundaries; subprocess/network are prohibited by mocks."""
import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("zer46_component_check", Path(__file__).with_name("run_component.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Runner(unittest.TestCase):
    def setUp(self):
        self.block = patch.object(module.subprocess, "Popen", side_effect=AssertionError("offline: no process"))
        self.block.start()
        self.block_http = patch.object(module, "measured_request", side_effect=AssertionError("offline: no HTTP"))
        self.block_http.start()

    def tearDown(self):
        self.block_http.stop(); self.block.stop()

    def test_import_and_creation_do_not_start_any_actor(self):
        lab = module.Lab()
        self.assertEqual((lab.fixture_http, lab.worker_count, lab.creation_attempted), (0, 0, False))
        compile(module.CLIENT, "<client>", "exec")

    def test_request_budget_target_and_deadline_stop_before_exec(self):
        lab = module.Lab(); lab.kube = Mock(); lab.pace = Mock()
        lab.fixture_http = 120
        with self.assertRaisesRegex(RuntimeError, "HTTP_BOUNDARY"): lab.http("a")
        lab.fixture_http = 0
        for who, path in (("foreign", "/fixture/x"), ("a", "http://external.invalid/")):
            with self.assertRaisesRegex(RuntimeError, "HTTP_BOUNDARY"): lab.http(who, path)
        lab.deadline = 0
        with self.assertRaisesRegex(RuntimeError, "GLOBAL_BUDGET"): lab.check()
        lab.kube.assert_not_called()

    def test_rate_limit_paces_from_completion_even_when_first_request_is_slow(self):
        lab = module.Lab(); clock = [100.0]; starts = []
        lab.wait = lambda end: clock.__setitem__(0, end)
        def response(*a, **k):
            starts.append(clock[0]); clock[0] += .7; return object()
        with patch.object(module.time, "monotonic", side_effect=lambda: clock[0]), patch.object(module, "measured_request", side_effect=response):
            lab.boutique_http("http://127.0.0.1:8080/", "GET")
            lab.boutique_http("http://127.0.0.1:8080/", "GET")
        self.assertGreaterEqual(starts[1] - starts[0], 1.19)
        self.assertEqual(lab.requests, 2)

    def test_pacing_never_relabels_wall_clock_reference_slo_as_pass(self):
        lab = module.Lab(); lab.save = Mock()
        lab.flow = Mock(per_sample_requests=9)
        def run(*a, **k):
            lab.pacing_idle += 2.2
            return {"ok": True, "elapsed_ms": 3500, "requests": 5, "cleanup": {"cart": "DONE"}}
        lab.flow.run.side_effect = run
        result = lab.probe()
        self.assertTrue(result["healthy"])
        self.assertFalse(result["wall_reference_slo_met"])
        self.assertEqual(result["result"]["elapsed_ms"], 3500)
        self.assertAlmostEqual(result["active_ms"], 1300)

    def test_isolation_script_is_compilable_and_bounded_without_execution(self):
        lab = module.Lab(); captured = []
        def kube(*args):
            script = args[-1]; tree = ast.parse(script)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "exec":
                    compile(ast.literal_eval(node.args[0]), "<isolation>", "exec")
            captured.append(script)
            return subprocess.CompletedProcess(args, 0, b'{"denied":true}', b'')
        lab.kube = kube
        lab.isolation({"status": {"podIP": "10.42.1.22"}})
        self.assertEqual(len(captured), 2)
        lab.tcp_checks = 6
        with self.assertRaisesRegex(RuntimeError, "TCP_BUDGET"):
            lab.isolation({"status": {"podIP": "10.42.1.22"}})

    def test_foreign_namespace_is_never_deleted(self):
        lab = module.Lab(); lab.creation_attempted = True
        lab.before = {"items": []}; calls = []
        def kube(*args):
            calls.append(args)
            if args[:2] == ("get", "namespace"):
                return subprocess.CompletedProcess(args, 0, json.dumps({"metadata": {"uid": "foreign", "labels": {}}}).encode(), b'')
            raise AssertionError("unexpected call")
        lab.kube = kube; lab.save = Mock(); lab.snapshot = Mock(return_value={"items": []})
        lab.resources = Mock(); lab.probe = Mock(return_value={"healthy": True})
        result = lab.cleanup()
        self.assertEqual(result["verdict"], "INCOMPLETE")
        self.assertFalse(any(args[0] == "delete" for args in calls))

    def test_private_container_restart_is_not_hidden_by_shared_filter(self):
        doc = {"items": [{"kind": "Pod", "metadata": {"namespace": "zd-sqli-lab"},
                          "status": {"containerStatuses": [{"name": "fixture", "restartCount": 1}]}}]}
        with self.assertRaisesRegex(RuntimeError, "UNEXPECTED_PRIVATE_CONTAINER_RESTART"):
            module.Lab.private_restarts(doc)


if __name__ == "__main__":
    unittest.main()
