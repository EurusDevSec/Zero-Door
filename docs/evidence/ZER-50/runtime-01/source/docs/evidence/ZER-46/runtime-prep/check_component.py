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

    def test_bootstrap_serializes_workload_startup(self):
        lab = module.Lab(); lab.kube = Mock(); lab.write_yaml = Mock(side_effect=lambda name, docs: name)
        lab.command = Mock()
        docs = [{"kind": "ConfigMap", "metadata": {"name": "config"}},
                {"kind": "Deployment", "metadata": {"name": "zer46-private-ingress"}},
                {"kind": "Pod", "metadata": {"name": "zer46-source-a"}},
                {"kind": "Pod", "metadata": {"name": "zer46-source-b"}}]
        actions = []
        lab.kube.side_effect = lambda *args: actions.append("apply:" + args[-1])
        lab.command.side_effect = lambda args, **kwargs: actions.append("wait:" + " ".join(args))
        lab.apply_bootstrap(docs)
        self.assertEqual(len(actions), 7)
        self.assertTrue(actions[0].endswith("bootstrap-static.yaml"))
        self.assertTrue(actions[1].endswith("bootstrap-proxy.yaml"))
        self.assertIn("rollout status", actions[2])
        self.assertTrue(actions[3].endswith("zer46-source-a.yaml"))
        self.assertIn("pod/zer46-source-a", actions[4])
        self.assertTrue(actions[5].endswith("zer46-source-b.yaml"))
        self.assertIn("pod/zer46-source-b", actions[6])


    def test_log_join_pins_new_pod_uid_with_old_pod_still_terminating(self):
        lab = module.Lab(); lab.save = Mock()
        old = {"metadata": {"name": "sqli-fixture-old", "uid": "old", "deletionTimestamp": "now",
            "labels": {"app": "sqli-fixture", "zero-door.io/run": lab.owner}}, "spec": {"nodeName": lab.node}}
        new = {"metadata": {"name": "sqli-fixture-new", "uid": "new",
            "labels": {"app": "sqli-fixture", "zero-door.io/run": lab.owner}}, "spec": {"nodeName": lab.node}}
        calls = []
        def kube(*args):
            calls.append(args)
            if args[2:5] == ('get', 'pods', '-o'): value = json.dumps({"items": [old, new]})
            elif args[2:5] == ('get', 'pod', 'sqli-fixture-new'): value = json.dumps(new)
            elif args[2:4] == ('logs', 'pod/sqli-fixture-new'): value = json.dumps({"request_id": "new-request"})
            else: raise AssertionError(args)
            return subprocess.CompletedProcess(args, 0, value.encode(), b'')
        lab.kube = kube
        self.assertEqual(lab.logs(), [{"request_id": "new-request"}])
        self.assertFalse(any('deployment/sqli-fixture' in args for args in calls))
        self.assertEqual(lab.save.call_args.args[1]['uid'], 'new')

    def test_changed_uid_never_reads_log_from_recreated_name(self):
        lab = module.Lab(); lab.save = Mock()
        pod = {"metadata": {"name": "sqli-fixture-new", "uid": "expected"}}
        foreign = {"metadata": {"name": "sqli-fixture-new", "uid": "different"}}
        lab.kube = Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(foreign).encode(), b''))
        with self.assertRaisesRegex(RuntimeError, 'LOG_POD_IDENTITY'): lab.logs(pod)
        self.assertEqual(lab.kube.call_count, 1)


    def test_old_pod_delete_readback_handles_already_absent_or_terminating(self):
        for values in ([b''], [b'{"metadata":{"uid":"owned","deletionTimestamp":"now"}}', b'']):
            lab = module.Lab(); lab.wait = Mock()
            lab.kube = Mock(side_effect=[subprocess.CompletedProcess([], 0, x, b'') for x in values])
            lab.wait_old_pod_absent('sqli-fixture-old', 'owned')
            self.assertEqual(lab.kube.call_count, len(values))
            self.assertTrue(all('--ignore-not-found' in call.args for call in lab.kube.call_args_list))

    def test_old_pod_uid_drift_or_timeout_stops_without_force_delete(self):
        lab = module.Lab(); lab.wait = Mock()
        lab.kube = Mock(return_value=subprocess.CompletedProcess([], 0, b'{"metadata":{"uid":"foreign"}}', b''))
        with self.assertRaisesRegex(RuntimeError, 'DELETED_POD_UID_DRIFT'):
            lab.wait_old_pod_absent('sqli-fixture-old', 'owned')
        lab.work_end = 0; lab.kube.reset_mock()
        with self.assertRaisesRegex(RuntimeError, 'OLD_POD_DELETE_TIMEOUT'):
            lab.wait_old_pod_absent('sqli-fixture-old', 'owned')
        lab.kube.assert_not_called()


if __name__ == "__main__":
    unittest.main()
