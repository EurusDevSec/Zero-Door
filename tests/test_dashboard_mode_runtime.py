"""RT2 offline: real gateway, actual production Uvicorn startup, no Kubernetes/Kafka/model.

HTTP availability is injected only into the diagnostic observer, never into production
Hephaestus. The same driver/bundle bytes will be used in the separately approved lab.
This suite cannot establish live outage, deployed image, firewall or cleanup acceptance.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess  # nosec B404 -- fixed current interpreter + production uvicorn module, no shell
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
spec = importlib.util.spec_from_file_location("rt2", ROOT / "infrastructure/scripts/r1_mode_runtime.py")
rt2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt2)


class Bundle(unittest.TestCase):
    def test_private_bundle_keeps_production_entrypoint_and_limits_each_actor_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "bundle"
            receipt = rt2.prepare(out, "zd-zer11-rt2-01234567")
            self.assertFalse(receipt["built"])
            docs = json.loads((out / "private-resources.json").read_text())["items"]
            by_name = {(d["kind"], d["metadata"]["name"]): d for d in docs}
            secret = by_name["Secret", "rt2-keys"]["stringData"]
            values = json.loads(secret["gateway.json"])
            self.assertEqual(len(values), len(set(values.values())))
            self.assertTrue(all(len(v) >= 32 for v in values.values()))
            for group in rt2.GROUPS:
                pod = by_name["Pod", "rt2-" + group.lower()]
                container = pod["spec"]["containers"][0]
                self.assertNotIn("command", container)  # original Docker ENTRYPOINT really runs
                self.assertFalse(pod["spec"]["automountServiceAccountToken"])
                projection = next(v["secret"]["items"] for v in pod["spec"]["volumes"] if "secret" in v)
                self.assertEqual({"rules.json", "policy-" + group + ".json", "heal-operator.json"}, {i["key"] for i in projection})
                self.assertEqual({"reader", "decision_rules"}, set(json.loads(secret["rules.json"])))
                self.assertNotIn("EXECUTOR", " ".join(e["name"] for e in container["env"]))
            console = by_name["Pod", "rt2-console"]
            projection = next(v["secret"]["items"] for v in console["spec"]["volumes"] if "secret" in v)
            self.assertEqual({"operator.json", "heal-operator.json"}, {i["key"] for i in projection})
            source = json.loads((out / "source-manifest.json").read_text())
            for rel, digest in source["files"].items():
                self.assertEqual(digest, rt2.digest((out / "build" / rel).read_bytes()))
            self.assertEqual((ROOT / "agent-orchestrator/hephaestus/Dockerfile").read_bytes(), (out / "build/hephaestus/Dockerfile").read_bytes())
            self.assertEqual(1, rt2.specification()["limits"]["frontend_pod_deletes"])
            self.assertNotIn("HorizontalPodAutoscaler", {d["kind"] for d in docs})

    def test_existing_bundle_or_invalid_namespace_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                rt2.prepare(Path(temp) / "bad", "target-app")
            rt2.prepare(Path(temp) / "bundle", "zd-zer11-rt2-01234567")
            with self.assertRaises(FileExistsError):
                rt2.prepare(Path(temp) / "bundle", "zd-zer11-rt2-01234567")

    def test_request_budget_can_only_be_tightened(self):
        with tempfile.TemporaryDirectory() as temp:
            for settings in ({"interval_s": .1}, {"interval_s": float("nan")}, {"max_gets": 361}, {"max_gets": True}):
                with self.subTest(settings=settings), self.assertRaises(ValueError):
                    rt2.Driver(Path(temp) / "invalid", settings, {})


class RealProductionProcesses(unittest.TestCase):
    def test_boundary_and_fail_closed_counterexamples(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            rt2.prepare(work / "bundle", "zd-zer11-rt2-abcdef12")
            cfg = json.loads((work / "bundle/config.json").read_text())
            cfg["profile"] = "OFFLINE_TEST_ONLY"  # injected HTTP is never promoted to a live-window PASS
            docs = json.loads((work / "bundle/private-resources.json").read_text())["items"]
            secret = next(d["stringData"] for d in docs if d["kind"] == "Secret")
            keys = json.loads(secret["gateway.json"])
            driver = rt2.Driver(work / "driver", cfg, keys)
            processes, logs, ports, handles = {}, {}, {}, []
            try:
                for group in rt2.GROUPS:
                    actor = work / group
                    actor.mkdir()
                    for name, content in (("rules.json", secret["rules.json"]), ("policy.json", secret["policy-" + group + ".json"]),
                                          ("heal-operator.json", secret["heal-operator.json"])):
                        (actor / name).write_text(content)
                    with socket.socket() as sock:
                        sock.bind(("127.0.0.1", 0))
                        ports[group] = sock.getsockname()[1]
                    env = dict(os.environ, PYTHONPATH=str(ROOT / "agent-orchestrator"), PYTHONDONTWRITEBYTECODE="1",
                        ZD_EVENT_URL=driver.url, ZD_O_KEYS_FILE=str(actor / "rules.json"),
                        ZD_RUN_ID=cfg["contexts"][group]["run_id"], ZD_TRIAL_ID=cfg["contexts"][group]["trial_id"],
                        ZD_PRODUCER_VERSION="rt2-offline", ZD_CLOCK_ID="clk-offline", ZD_CLOCK_SOURCE="UNKNOWN",
                        ZD_COMMAND_POLICY_FILE=str(actor / "policy.json"), ZD_OPERATOR_TOKEN_FILE=str(actor / "heal-operator.json"),
                        ZD_COMMAND_LEDGER_FILE=str(actor / "claims.sqlite"))
                    logs[group] = actor / "uvicorn.log"
                    handle = logs[group].open("wb")
                    handles.append(handle)
                    # Production startup, real background consumer; no monkeypatch to healer globals.
                    processes[group] = subprocess.Popen([sys.executable, "-B", "-m", "uvicorn", "main:app", "--app-dir",
                        str(ROOT / "agent-orchestrator/hephaestus"), "--host", "127.0.0.1", "--port", str(ports[group])],
                        env=env, stdout=handle, stderr=subprocess.STDOUT)  # nosec B603 -- fixed reviewed module/paths
                until = time.monotonic() + 30
                for group in rt2.GROUPS:
                    while True:
                        if processes[group].poll() is not None:
                            self.fail(logs[group].read_text())
                        try:
                            code, data = rt2.http(f"http://127.0.0.1:{ports[group]}/healthz")
                            if code == 200:
                                self.assertEqual("DISABLED_PENDING_GUARD", json.loads(data)["execution"])
                                break
                        except OSError:
                            pass
                        if time.monotonic() >= until:
                            self.fail("production startup timeout")
                        time.sleep(0.1)
                with self.assertRaises(ValueError):
                    rt2.operator(cfg, json.loads(secret["operator.json"]), json.loads(secret["heal-operator.json"]),
                                 driver.url, f"http://127.0.0.1:{ports['BM']}")
                driver.observe(lambda *a, **kw: (200, b"healthy"))
                driver.observe(lambda *a, **kw: (503, b"unavailable"))
                driver.observe(lambda *a, **kw: (200, b"healthy"))
                self.assertEqual(1, len([e for e in driver.events("BM") if e["event_type"] == "DETECTED"]))
                # A plain observation must never be an automatic proposal in BM.
                driver.controls()
                while not any(e["event_type"] == "DECISION" for e in driver.events("B1")):
                    if time.monotonic() >= until:
                        self.fail("RULES positive control timeout")
                    time.sleep(0.1)
                time.sleep(1.2)  # second real consumer poll, including durable dedup
                self.assertFalse(any(e["event_type"] == "DECISION" for e in driver.events("BM")))
                code, _ = rt2.http(f"http://127.0.0.1:{ports['BM']}/heal/trigger", {"decision_id": "bad"}, "wrong")
                self.assertEqual(401, code)
                manual = rt2.operator(cfg, json.loads(secret["operator.json"]), json.loads(secret["heal-operator.json"]),
                                      driver.url, f"http://127.0.0.1:{ports['BM']}")
                self.assertEqual((409, {"detail": "R1_EXECUTOR_DISABLED"}), (manual["status"], manual["body"]))
            finally:
                for process in processes.values():
                    if process.poll() is None:
                        process.terminate()
                for process in processes.values():
                    try:
                        process.wait(5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(5)
                for handle in handles:
                    handle.close()
                try:
                    summary = driver.finish()
                finally:
                    driver.close()
            captured = {g: p.read_text() for g, p in logs.items()}
            result = rt2.assess(summary, captured, manual)
            self.assertEqual([], result["errors"], result)
            self.assertEqual("PASS_BOUNDARY_OFFLINE", result["verdict"])
            # Rejections must be evidence-sensitive, not an unconditional happy path.
            mutations = []
            missing = copy.deepcopy(summary)
            missing["samples"] = [{"ok": True}]
            mutations.append((missing, captured, manual, "BM_LIVE_FAILURE_NOT_OBSERVED"))
            missing = copy.deepcopy(summary)
            missing["events"]["B1"] = [e for e in missing["events"]["B1"] if e["event_type"] != "DECISION"]
            mutations.append((missing, captured, manual, "B1_DECISION_BOUNDARY"))
            missing = copy.deepcopy(summary)
            missing["events"]["BM"].append({"event_type": "HEAL_STARTED"})
            mutations.append((missing, captured, manual, "BM_FORBIDDEN_EVENT"))
            mutations.append((summary, dict(captured, BM=""), manual, "BM_CONSUMER_AUDIT_MISSING"))
            mutations.append((summary, captured, dict(manual, status=200), "MANUAL_EXECUTOR_REFUSAL_MISSING"))
            live = copy.deepcopy(summary)
            live["profile"] = "RUNTIME_PENDING"
            mutations.append((live, captured, manual, "BM_OBSERVATION_WINDOW_INCOMPLETE"))
            for data, audit, receipt, error in mutations:
                with self.subTest(error=error):
                    self.assertIn(error, rt2.assess(data, audit, receipt)["errors"])
            for group in rt2.GROUPS:
                self.assertTrue((work / "driver/exports" / group / "O.jsonl").is_file())
            # Optional sanitized evidence only. Never copy bundle Secret manifests or actor key files.
            if os.getenv("RT2_KEEP"):
                keep = Path(os.environ["RT2_KEEP"])
                keep.mkdir(parents=True, exist_ok=False)
                rt2.save(keep / "summary.json", summary)
                rt2.save(keep / "manual.json", manual)
                rt2.save(keep / "assessment.json", result)
                rt2.save(keep / "logs.json", captured)


if __name__ == "__main__":
    unittest.main(verbosity=2)
