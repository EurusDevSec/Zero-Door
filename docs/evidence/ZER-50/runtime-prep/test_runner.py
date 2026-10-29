"""Offline runner validation: fake joins, denied admission, owned local process trees only."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

PREP = Path(__file__).resolve().parent
sys.path.insert(0, str(PREP))
import run
import lab


class Runner(unittest.TestCase):
    def setUp(self):
        self.net = patch.object(socket.socket, "connect", side_effect=AssertionError("OFFLINE_ONLY"))
        self.net.start(); self.addCleanup(self.net.stop)
        self.ctx = {"run_id": "run_" + "1" * 32, "trial_id": "trl_" + "2" * 32}
        self.detected = dict(self.ctx, event_id="evt_" + "3" * 32)
        self.raw = {"request_id": "4" * 32, "correlation_id": "5" * 32, "ts": 101,
            "method": "GET", "path": "/fixture/catalog/search", "status": 200, "rows": 1,
            "restricted_rows": 0, "client_ip": "10.42.0.11", "tcp_peer": "10.42.0.12",
            "source_method": "XFF_AFTER_TRUSTED", "source_confidence": "PROXY_CHAIN"}
        self.http = {"request": {"method": "GET", "path": self.raw["path"] + "?category=electronics",
            "correlation": self.raw["correlation_id"]}, "response": {"request_id": self.raw["request_id"],
            "status": 200, "begin": 100, "end": 102, "body": {"count": 1, "results": [{"visibility": "public"}]}}}
        self.uid = "1" * 8 + "-" + "2" * 4 + "-" + "3" * 4 + "-" + "4" * 4 + "-" + "5" * 12

    def project(self, **kw):
        args = dict(pod_uid=self.uid, ref="http-001.json", at=103); args.update(kw)
        return lab.project(self.ctx, self.detected, self.uid, self.raw, self.http, **args)

    def test_success_delivery_is_projected_only_after_real_join(self):
        self.assertNotIn("delivered", self.raw)
        result = self.project()
        self.assertIs(True, result["delivered"])
        self.assertEqual(self.detected["event_id"], result["detection_event_id"])

    def test_failed_delivery_wrong_pod_request_correlation_time_and_counts_refused(self):
        for field, value in (("delivered", False), ("request_id", "f" * 32),
                ("correlation_id", "f" * 32), ("ts", 99), ("rows", 2), ("restricted_rows", 1)):
            with self.subTest(field=field), patch.dict(self.raw, {field: value}):
                with self.assertRaises(ValueError):
                    self.project()
        with self.assertRaises(ValueError):
            self.project(pod_uid="foreign")
        with self.assertRaises(ValueError):
            self.project(at=200)

    def test_default_is_plan_only(self):
        with patch.object(sys, "argv", ["run.py"]), patch.object(run, "execute", side_effect=AssertionError("NO_RUNTIME")):
            self.assertEqual(0, run.main())

    def test_unapproved_attempt_stops_before_output_or_process(self):
        with tempfile.TemporaryDirectory() as folder:
            auth = Path(folder) / "auth.json"; auth.write_text('{"approved":false}')
            with patch.object(run, "run_child", side_effect=AssertionError("NO_CHILD")):
                with self.assertRaisesRegex(ValueError, "FRESH_EXACT_OWNER_APPROVAL_REQUIRED"):
                    run.execute(auth)

    def test_expired_or_wrong_proposal_approval_stops_before_process(self):
        with tempfile.TemporaryDirectory() as folder:
            prep = Path(folder); (prep / "proposal.md").write_text("bounded")
            (prep / "source-manifest.json").write_text('{"sha256":{"source":"pin"}}')
            auth = prep / "auth.json"
            valid = {"approved": True, "issue": "ZER-50", "attempt": "runtime-01",
                "proposal_sha256": run.sha(prep / "proposal.md"),
                "source_manifest_sha256": run.sha(prep / "source-manifest.json"), "expires_epoch": time.time() + 60}
            for change in ({"expires_epoch": time.time() - 1}, {"proposal_sha256": "0" * 64}):
                auth.write_text(json.dumps(dict(valid, **change)))
                with patch.object(run, "PREP", prep), patch.object(run, "run_child", side_effect=AssertionError("NO_CHILD")):
                    with self.assertRaisesRegex(ValueError, "FRESH_EXACT_OWNER_APPROVAL_REQUIRED"):
                        run.execute(auth)

    def test_existing_attempt_is_never_replayed(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "runtime-01"; out.mkdir()
            with patch.object(run, "OUT", out), patch.object(run, "admit", return_value={}), \
                    patch.object(run, "run_child", side_effect=AssertionError("NO_CHILD")):
                with self.assertRaises(FileExistsError):
                    run.execute("fake")

    def test_direct_work_child_requires_approval_and_cannot_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            with patch.object(lab, "OUT", out):
                with self.assertRaises(FileNotFoundError):
                    lab.claim_work()
                (out / "started.json").write_text(json.dumps({"head": run.HEAD}))
                with patch.object(run, "admit", return_value={}):
                    lab.claim_work()
                    with self.assertRaises(FileExistsError):
                        lab.claim_work()

    def test_foreign_namespace_cleanup_refuses_delete(self):
        native = lab.make_lab()
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / "state.json").write_text(json.dumps({"creation_attempted": True,
                "owner": "zer46-123456abcdef", "ns_uid": self.uid}))
            calls = []
            def kube(*args):
                calls.append(args)
                self.assertEqual("get", args[0])
                return subprocess.CompletedProcess(args, 0, json.dumps({"metadata": {
                    "uid": self.uid, "labels": {"zero-door.io/run": "foreign"}}}).encode(), b"")
            with patch.object(lab, "OUT", out), patch.object(native, "kube", side_effect=kube), \
                    patch.object(native, "save"):
                result = native.cleanup_owned()
            self.assertEqual("INCOMPLETE", result["verdict"])
            self.assertIn("CLEANUP_OWNER_UID", result["errors"][0])
            self.assertEqual(1, len(calls))

    def test_manifest_rejects_drift_and_path_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); prep = root / "prep"; prep.mkdir()
            for relative in ("missing.py", "../outside.py"):
                (prep / "source-manifest.json").write_text(json.dumps({"sha256": {relative: "0" * 64}}))
                with self.assertRaises((ValueError, FileNotFoundError)):
                    run.verify_sources(root, prep)

    def test_foreign_endpoint_and_dynamic_auth_refused_without_kubectl(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            doc = {"contexts": [{"name": "k3d-zero-door", "context": {"cluster": "c", "user": "u"}}],
                "clusters": [{"name": "c", "cluster": {"server": "https://foreign.invalid:7356"}}],
                "users": [{"name": "u", "user": {}}]}
            with patch.dict(os.environ, {"KUBECONFIG": str(path)}, clear=True):
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(ValueError, "LOCAL_STATIC_KUBE_PIN"):
                    lab.kube_config_pin()
                doc["clusters"][0]["cluster"]["server"] = "https://127.0.0.1:7356"
                doc["users"][0]["user"]["exec"] = {"command": "forbidden"}
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(ValueError, "LOCAL_STATIC_KUBE_PIN"):
                    lab.kube_config_pin()

    def test_fixture_http_budget_stops_before_dispatch(self):
        native = lab.make_lab()
        native.fixture_http = 9
        with patch.object(native, "command", side_effect=AssertionError("NO_LAB")):
            with self.assertRaisesRegex(ValueError, "ZER50_HTTP_BUDGET"):
                native.http("a")

    def test_cached_renderer_has_four_private_workloads_and_no_public_route(self):
        driver = lab.load_fixture_driver()
        docs = driver.cached.parent.full.renderer.render("zer46-123456abcdef",
            "run_" + "1" * 32, "trl_" + "2" * 32, "10.42.0.12", node="k3d-zero-door-agent-0")
        workloads = [d for d in docs if d["kind"] in {"Deployment", "Pod"}]
        self.assertEqual(4, len(workloads))
        self.assertNotIn("Ingress", {d["kind"] for d in docs})
        for d in workloads:
            spec = d["spec"]["template"]["spec"] if d["kind"] == "Deployment" else d["spec"]
            self.assertTrue(all(c["imagePullPolicy"] == "Never" for c in spec["containers"]))

    def test_owned_native_child_completes_and_is_reaped(self):
        with tempfile.TemporaryDirectory() as folder:
            result = run.run_child([sys.executable, "-B", "-c", "import sys; assert sys.stdin.readline()=='GO\\n'"],
                dict(os.environ), Path(folder) / "child.log", timeout=5)
            self.assertEqual(0, result["exit_code"])
            self.assertTrue(result["process_reaped"])
            self.assertFalse(result["timed_out"])

    def test_owned_native_timeout_closes_tree_and_reaps_child(self):
        temp = tempfile.TemporaryDirectory()
        folder = temp.name
        try:
            result = run.run_child([sys.executable, "-B", "-c",
                "import sys,time; sys.stdin.readline(); time.sleep(20)"], dict(os.environ),
                Path(folder) / "child.log", timeout=1)
            self.assertTrue(result["timed_out"])
            self.assertTrue(result["process_reaped"])
            self.assertTrue(result["owned_tree_closed"])
        finally:
            # Windows may release file handles just after the process/Job is
            # signaled. Reviewer measured ~20ms; retry only this owned temp
            # deletion for <=1s, and fail if the lock persists. No runtime retry.
            deadline = time.monotonic() + 1
            while True:
                try:
                    temp.cleanup(); break
                except PermissionError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(.02)

    def test_actual_fixture_uid_must_remain_pinned_before_http(self):
        native = lab.make_lab(); native.fixture_uid = self.uid
        base = type(native).__mro__[1]
        with patch.object(base, "pod", return_value={"metadata": {"uid": "foreign"}}):
            with self.assertRaisesRegex(ValueError, "FIXTURE_UID_CHANGED"):
                native.pod()

    def test_interrupted_wait_still_closes_owned_tree(self):
        real = subprocess.Popen
        children = []
        def spawn(*a, **kw):
            child = real(*a, **kw); children.append(child)
            wait, count = child.wait, [0]
            def interrupted(timeout=None):
                count[0] += 1
                if count[0] == 1:
                    raise KeyboardInterrupt
                return wait(timeout=timeout)
            child.wait = interrupted
            return child
        with tempfile.TemporaryDirectory() as folder, patch.object(run.subprocess, "Popen", side_effect=spawn):
            with self.assertRaises(KeyboardInterrupt):
                run.run_child([sys.executable, "-B", "-c", "import sys,time; sys.stdin.readline(); time.sleep(20)"],
                    dict(os.environ), Path(folder) / "child.log", timeout=5)
        self.assertIsNotNone(children[0].poll())


if __name__ == "__main__":
    unittest.main(verbosity=2)
