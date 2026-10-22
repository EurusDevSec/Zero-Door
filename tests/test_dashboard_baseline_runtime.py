"""H-RT1 (G-ZER11-RT1) offline: the harness's own orchestration code against fakes. No cluster, Docker or model.

What is fake: kubectl (an in-memory cluster with a ReplicaSet controller, an HPA and events), the target's
reachability (the ZER-10 fake Boutique on loopback, cut to CONNECT failures or hangs while the fake has no
ready frontend pod) and the time scale (a SYNTHETIC copy of RT1 with seconds instead of minutes; the
orchestrator's clock can jump). What is real: this harness end to end, the production H/O gateways and
archives, the ZER-10 ProbeRunner and RecoveryMonitor, seal/export, the ZER-10 scorer CLI, register and the
serve-results app. `kubectl exec` reaches the agent in process through the same JSON command it sends in the pod.
"""
import copy
import errno
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import shutil
import tarfile
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import r1_baseline_runtime as rt  # noqa: E402
from measurement.flows import Failure, deadline_value, request  # noqa: E402
from test_measurement_probe import Boutique, serve, stop  # noqa: E402

spec = importlib.util.spec_from_file_location("zer11_verify_rt1", ROOT / "infrastructure/scripts/verify-dashboard-baselines.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
import yaml  # noqa: E402  (test side only: stands in for kubectl's client-side YAML conversion)


def scaled_plan(total_s=240):
    """RT1 with the same structure, in seconds (SYNTHETIC; F-01 PILOT values are not these)."""
    plan = copy.deepcopy(verify.RT1)
    plan["f01"] = {"delta_s": 0.2, "k": 3, "s_s": 0.6, "l_ms": 2000, "gap_s": 0.6, "eps_s": 1, "cap_det_s": 3, "cap_rec_s": 3}
    plan["w_eff_s"], plan["stop_margin_s"] = 2.0, 0.3
    for t in plan["trials"].values():
        t.update(warmup_s=0.4, baseline_s=0.6)
    plan["trials"]["B0-HPA"]["load_s"] = 1.6
    plan["phases_s"] = {"P0": 20, "P1": 20, "P2": 20, "P4_hpa_ready": 4, "P5_seal_export": 20, "P7": 25}
    plan["caps"]["total_s"] = total_s
    return plan


# The scenario runs in seconds instead of minutes, but a host stall (scheduler, disk, antivirus) does not shrink
# with it: the control-ACK deadline (grace_s) and the probe ACK stall limit keep their production values (N1,
# rt1-fix-01). test_control_ack_later_than_its_deadline_fails_closed still runs that path with a 2 s deadline.
OVERRIDES = {"poll_s": 0.1, "watch_gap_s": 1.0, "ack_stall_s": rt.EXEC["ack_stall_s"], "grace_s": rt.EXEC["grace_s"],
             "timeouts": {"step_s": 2, "transaction_s": 2},
             "heartbeat_s": 1, "pod_ready_s": 5, "scale_wait_s": 5, "namespace_gone_s": 5, "load_grace_s": 1,
             "baseline_grace_s": 3, "agent_call_s": 30, "export_tar_s": 30}


def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000)) + f".{int(ms % 1000):03d}Z"


class FakeCluster:
    """kubectl argv -> in-memory objects. Scenario knobs change one behaviour each."""

    def __init__(self, tmp, origin, **knobs):
        self.tmp, self.origin = Path(tmp), origin
        self.k = dict({"recreate_s": 0.6, "after_fault": None, "hpa": "idle", "rescale_after_s": 0.3, "hpa_pod_ready_s": 1.2,
                       "metrics": True, "frontend_replicas": 1, "scale_manager": "kubectl"}, **knobs)
        self.lock = threading.RLock()
        self.rv = 100
        self.deploys, self.pods, self.hpas, self.cms, self.events = {}, [], {}, {}, []
        self.namespaces = {"target-app": {"uid": self.uid()}, "zero-door": {"uid": self.uid()}}
        self.agent = None
        self.load = None
        self.fault_at = None
        self.calls, self.hooks, self.fail_if = [], [], None
        for ns, name, replicas in (("target-app", "frontend", self.k["frontend_replicas"]), ("target-app", "cartservice", 1),
                                   ("target-app", "redis-cart", 1), ("zero-door", "gaia", 1), ("zero-door", "hephaestus", 1)):
            self.add_deploy(ns, name, replicas)

    def uid(self):
        return str(uuid.uuid4())

    def next_rv(self):
        self.rv += 1
        return str(self.rv)

    def add_deploy(self, ns, name, replicas, uid=None):
        self.deploys[(ns, name)] = {"rs_uid": self.uid(), "metadata": {"name": name, "namespace": ns, "uid": uid or self.uid(), "resourceVersion": self.next_rv(),
                                                 "generation": 1, "labels": {}, "managedFields": [{"manager": "kubectl-client-side-apply",
                                                 "operation": "Update", "fieldsV1": {"f:spec": {"f:replicas": {}, "f:template": {}}}}]},
                                    "spec": {"replicas": replicas, "selector": {"matchLabels": {"app": name}},
                                             "template": {"metadata": {"labels": {"app": name}}, "spec": {"containers": [{"name": name, "image": name}]}}},
                                    "status": {}}
        self.reconcile()

    @staticmethod
    def own_replicas(d, manager):
        """A write through /scale moves spec.replicas to that manager (the API server's field ownership)."""
        fields = d["metadata"]["managedFields"]
        for entry in fields:
            entry.get("fieldsV1", {}).get("f:spec", {}).pop("f:replicas", None)
        # k3s v1.31.5 observed: scaling to zero drops replicas ownership; retain the scale-up observation.
        if d["spec"]["replicas"] != 0:
            fields.append({"manager": manager, "operation": "Update", "subresource": "scale", "fieldsV1": {"f:spec": {"f:replicas": {}}}})

    def event(self, ns, reason, kind, name, source, message="", uid=None, at_ms=None):
        now = time.time() * 1000 if at_ms is None else at_ms
        self.events.append({"metadata": {"namespace": ns}, "reason": reason, "involvedObject": {"kind": kind, "name": name, "uid": uid},
                            "source": {"component": source}, "eventTime": iso(now), "message": message})

    def reconcile(self):
        """ReplicaSet controller: live pods follow spec.replicas; a new pod is Ready after recreate_s."""
        now = time.monotonic()
        for (ns, name), d in self.deploys.items():
            live = [p for p in self.pods if p["ns"] == ns and p["app"] == name]
            want = d["spec"]["replicas"]
            for p in live[want:]:
                self.pods.remove(p)
                self.event(ns, "SuccessfulDelete", "ReplicaSet", name + "-rs", "replicaset-controller", f"Deleted pod: {p['name']}", d["rs_uid"])
            for _ in range(want - len(live)):
                # Only a pod recreated after the fault takes recreate_s; the initial pods are already Ready.
                delay = self.k["recreate_s"] if ns == "target-app" and name == "frontend" and self.fault_at else 0.05
                if self.load and name == "frontend" and self.load.get("rescaled"):
                    delay = self.k["hpa_pod_ready_s"]
                pod = {"ns": ns, "app": name, "name": f"{name}-{uuid.uuid4().hex[:5]}", "uid": self.uid(), "ready_at": now + delay,
                       "owner": d["rs_uid"]}
                self.pods.append(pod)
                self.event(ns, "SuccessfulCreate", "ReplicaSet", name + "-rs", "replicaset-controller", f"Created pod: {pod['name']}", d["rs_uid"])
            d["status"]["readyReplicas"] = sum(1 for p in self.pods if p["ns"] == ns and p["app"] == name and p["ready_at"] <= now)
        self.hpa_controller()

    def hpa_controller(self):
        if not self.load or self.k["hpa"] != "scales" or self.load.get("rescaled") or "frontend-hpa-r1" not in self.hpas:
            return
        if time.monotonic() >= self.load["t"] + self.k["rescale_after_s"]:
            d = self.deploys[("target-app", "frontend")]
            d["spec"]["replicas"] = 2
            d["metadata"]["resourceVersion"] = self.next_rv()
            self.own_replicas(d, "horizontal-pod-autoscaler")
            self.load["rescaled"] = True
            self.event("target-app", "SuccessfulRescale", "HorizontalPodAutoscaler", "frontend-hpa-r1", "horizontal-pod-autoscaler",
                       "New size: 2; reason: cpu resource utilization above target", self.hpas["frontend-hpa-r1"]["metadata"]["uid"])
            self.reconcile()

    def frontend_state(self):
        with self.lock:
            self.reconcile()
            now = time.monotonic()
            ready = [p for p in self.pods if p["app"] == "frontend" and p["ready_at"] <= now]
            if self.fault_at is not None and self.k["after_fault"] == "hang":
                return "hang"
            if not ready:
                return "down"
            if self.load and self.k["hpa"] == "scales" and now < self.load["t"] + self.load["s"] and len(ready) < 2:
                return "overload"
            if self.load and self.k["hpa"] == "slow" and now < self.load["t"] + self.load["s"]:
                return "slow"
            return "up"

    def http(self, url, method="GET", headers=(), body=b"", deadline_ns=0, cancel=None, **kw):
        state = self.frontend_state()
        if state == "down":
            raise Failure("CONNECT", "CONNECTION_REFUSED")
        if state == "overload":
            raise Failure("HTTP", "STATUS_503")
        if state == "hang":
            # A live bound (callable) is what Flow.cleanup passes (bounded_deadline): N1, rt1-fix-01.
            while time.perf_counter_ns() < deadline_value(deadline_ns):
                if cancel is not None and cancel.is_set():
                    break
                time.sleep(0.05)
            raise Failure("TIMEOUT", "DEADLINE")
        if state == "slow":
            time.sleep(0.15)  # every transaction still passes (latency < L), but samples end up further apart than gap
        return request(url, method, headers, body, deadline_ns, cancel, **kw)

    # ------------------------------------------------------------- kubectl
    def __call__(self, argv, stdin=None, timeout=None):
        assert argv[:3] == ["kubectl", "--context", "k3d-zero-door"] and argv[3].startswith("--request-timeout="), argv
        args = argv[4:]
        self.calls.append(args)
        for hook in list(self.hooks):
            hook(self, args)
        if self.fail_if and self.fail_if(self, args):
            return 1, b"", b"Unable to connect to the server"
        with self.lock:
            self.reconcile()
            out = self.dispatch(args, stdin)
            if isinstance(out, tuple):
                return out
            if isinstance(out, dict) and args[0] == "get":
                out = copy.deepcopy(out)
                if "--show-managed-fields=true" not in args:  # kubectl's default, as `kubectl get --help` says
                    for item in out.get("items", [out]):
                        item.get("metadata", {}).pop("managedFields", None)
        return 0, (out if isinstance(out, bytes) else json.dumps(out).encode()), b""

    def dispatch(self, args, stdin):
        verb = args[0]
        if args[:2] == ["config", "get-contexts"]:
            return b"k3d-zero-door\n"
        if args[:2] == ["version", "--client"]:
            return {"clientVersion": {"major": "1", "minor": "33+", "gitVersion": "v1.33.5-fake"}}
        if verb == "get":
            return self.get(args)
        if verb == "auth":
            return 1, b"no\n", b""
        if verb == "create" and "--dry-run=client" in args:
            docs = [d for d in yaml.safe_load_all(Path(args[args.index("-f") + 1]).read_text()) if d]
            # Real kubectl emits one JSON document per YAML document, rather than wrapping them in a List.
            return b"\n".join(rt.canonical(doc) for doc in docs)
        if verb == "create":
            return self.create(json.loads(stdin))
        if verb == "scale":
            return self.scale(args)
        if verb == "delete":
            assert args[1:4:2] == ["--raw", "-f"] and args[4] == "-", args  # the body comes on stdin, never from a host file
            return self.delete(args[2], json.loads(stdin))
        if verb == "exec":
            return self.exec(args)
        if verb == "logs":
            return json.dumps({"sent": 32, "ok": 32, "error": 0}).encode()
        raise AssertionError(f"unexpected kubectl {args}")

    def ns_of(self, args):
        return args[args.index("-n") + 1] if "-n" in args else None

    def pod_json(self, p):
        now = time.monotonic()
        return {"metadata": {"name": p["name"], "namespace": p["ns"], "uid": p["uid"], "labels": {"app": p["app"]},
                             "ownerReferences": [{"kind": "ReplicaSet", "name": p["app"] + "-rs", "uid": p["owner"]}]},
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True" if p["ready_at"] <= now else "False"}]}}

    def get(self, args):
        kind, ns = args[1], self.ns_of(args)
        name = args[2] if len(args) > 2 and not args[2].startswith("-") else None
        if kind == "nodes":
            return {"items": [{"metadata": {"name": "k3d-zero-door-server-0"}, "status": {"conditions": [{"type": "Ready", "status": "True"}],
                               "images": [{"names": ["docker.io/" + rt.EXEC["image"]]}]}}]}
        if kind == "deploy":
            if name:
                d = self.deploys.get((ns, name))
                return d if d else (1, b"", b'Error from server (NotFound): deployments "x" not found')
            return {"items": [d for (n, _), d in self.deploys.items() if n == ns]}
        if kind == "hpa":
            if name:
                h = self.hpas.get(name)
                if not h:
                    return 1, b"", b"Error from server (NotFound)"
                d = self.deploys[("target-app", h["spec"]["scaleTargetRef"]["name"])]
                metrics = [{"type": "Resource", "resource": {"name": "cpu", "current": {"averageUtilization": 12}}}] if self.k["metrics"] else []
                return dict(h, status={"currentMetrics": metrics, "desiredReplicas": d["spec"]["replicas"], "currentReplicas": d["spec"]["replicas"]})
            return {"items": list(self.hpas.values())}
        if kind == "apiservice":
            return {"status": {"conditions": [{"type": "Available", "status": "True" if self.k["metrics"] else "False"}]}}
        if kind == "configmap":
            if name:
                return self.cms.get((ns, name)) or (1, b"", b"Error from server (NotFound)")
            return {"items": [c for (n, _), c in self.cms.items() if n == ns]}
        if kind in ("namespaces", "namespace"):
            if name:
                n = self.namespaces.get(name)
                return {"metadata": {"name": name, "uid": n["uid"], "labels": n.get("labels") or {}}} if n else (1, b"", b"Error from server (NotFound)")
            return {"items": [{"metadata": {"name": n}} for n in self.namespaces]}
        if kind == "service":
            host, port = self.origin.rsplit(":", 1)
            return {"spec": {"clusterIP": host.split("//")[1], "ports": [{"port": int(port)}]}}
        if kind in ("pods", "pod"):
            if name == rt.AGENT_POD:
                return {"metadata": {"name": name}, "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]}}
            if name == rt.LOAD_POD:
                if not self.load or self.load.get("deleted"):
                    return 1, b"", b"Error from server (NotFound)"
                done = time.monotonic() >= self.load["t"] + self.load["s"]
                return {"metadata": {"name": name, "uid": self.load["uid"], "labels": self.load["labels"]},
                        "status": {"phase": "Succeeded" if done else "Running"}}
            app = args[args.index("-l") + 1].split("=", 1)[1]
            return {"items": [self.pod_json(p) for p in self.pods if p["ns"] == ns and p["app"] == app]}
        if kind == "events":
            return {"items": [e for e in self.events if e["metadata"]["namespace"] == ns]}
        raise AssertionError(args)

    def create(self, obj):
        meta, kind = obj["metadata"], obj["kind"]
        taken = {"Namespace": meta["name"] in self.namespaces, "ConfigMap": (meta.get("namespace"), meta["name"]) in self.cms,
                 "HorizontalPodAutoscaler": meta["name"] in self.hpas}
        if taken.get(kind):
            return 1, b"", f'Error from server (AlreadyExists): "{meta["name"]}" already exists'.encode()
        meta["uid"] = self.uid()
        if kind == "Namespace":
            self.namespaces[meta["name"]] = {"uid": meta["uid"], "labels": meta.get("labels")}
        elif kind == "ConfigMap":
            self.cms[(meta["namespace"], meta["name"])] = obj
        elif kind == "HorizontalPodAutoscaler":
            self.hpas[meta["name"]] = obj
        elif kind == "Deployment":
            self.add_deploy(meta["namespace"], meta["name"], obj["spec"]["replicas"], uid=meta["uid"])
        elif kind == "Pod" and meta["name"] == rt.AGENT_POD:
            self.agent = rt.Agent(self.tmp / ("agent-" + uuid.uuid4().hex[:6]), http=self.http)
        elif kind == "Pod" and meta["name"] == rt.LOAD_POD:
            self.load = {"t": time.monotonic(), "s": float(obj["spec"]["containers"][0]["command"][obj["spec"]["containers"][0]["command"].index("--duration") + 1]),
                         "uid": meta["uid"], "labels": meta.get("labels") or {}}
        return obj

    def scale(self, args):
        name, ns = args[1].split("/")[1], self.ns_of(args)
        opts = dict(a[2:].split("=", 1) for a in args if a.startswith("--"))
        d = self.deploys.get((ns, name))
        if d is None or str(d["spec"]["replicas"]) != opts["current-replicas"] or d["metadata"]["resourceVersion"] != opts["resource-version"]:
            return 1, b"", b"error: precondition failed"
        d["spec"]["replicas"] = int(opts["replicas"])
        d["metadata"]["resourceVersion"] = self.next_rv()
        self.own_replicas(d, self.k["scale_manager"])
        self.event(ns, "ScalingReplicaSet", "Deployment", name, "deployment-controller")
        self.reconcile()
        return b"scaled\n"

    def delete(self, path, options):
        uid = options["preconditions"]["uid"]
        parts = path.strip("/").split("/")
        name, kind = parts[-1], parts[-2]
        if self.k.get("ignore_preconditions") and kind == "configmaps" and (parts[3], name) in self.cms:
            uid = self.cms[(parts[3], name)]["metadata"]["uid"]  # a client that drops the body: deletes by name
        notfound = (1, b"", b"Error from server (NotFound)")
        conflict = (1, b"", b"Error from server (Conflict): Precondition failed: UID in precondition")
        if kind == "pods" and parts[3] == "target-app":
            p = next((p for p in self.pods if p["name"] == name), None)
            if p is None:
                return notfound
            if p["uid"] != uid:
                return conflict
            self.pods.remove(p)
            self.fault_at = time.monotonic()
            self.event("target-app", "Killing", "Pod", name, "kubelet")
            self.reconcile()
            return b"{}"
        if kind == "pods":
            if not self.load or self.load["uid"] != uid:
                return notfound
            self.load["deleted"] = True
            return b"{}"
        table = {"horizontalpodautoscalers": (self.hpas, name), "configmaps": (self.cms, (parts[3], name))}
        if kind in table:
            store, key = table[kind]
            if key not in store:
                return notfound
            if store[key]["metadata"]["uid"] != uid:
                return conflict
            del store[key]
            return b"{}"
        if kind == "namespaces":
            if self.namespaces.get(name, {}).get("uid") != uid:
                return notfound if name not in self.namespaces else conflict
            del self.namespaces[name]
            for key in [k for k in self.deploys if k[0] == name]:
                del self.deploys[key]
            self.pods = [p for p in self.pods if p["ns"] != name]
            return b"{}"
        raise AssertionError(path)

    def exec(self, args):
        tail = args[args.index("--") + 1:]
        if tail[0] == "tar":
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode="w") as archive:
                archive.add(self.agent.root / "out", arcname=".")
            return buffer.getvalue()
        command = json.loads(tail[-1])
        answer = self.agent.handle(command)
        return (0 if answer.get("ok") else 1), rt.canonical(answer), b""


class JumpClock(rt.Clock):
    """Orchestrator clock that can jump forward (budget tests); sleeps are real but short."""
    def __init__(self):
        self.offset = 0.0

    def monotonic(self):
        return time.monotonic() + self.offset


class Run:
    def __init__(self, case, plan=None, cfg_over=None, **knobs):
        self.tmp = tempfile.TemporaryDirectory()
        self.case = case
        case.addCleanup(self.close)
        server, cls, origin = serve(Boutique)
        case.addCleanup(stop, server)
        self.cluster = FakeCluster(self.tmp.name, origin, **knobs)
        self.plan = plan or scaled_plan()
        self.cfg = rt.config(self.plan, dict(OVERRIDES, **(cfg_over or {})))
        self.clock = JumpClock()
        self.kube = rt.Kube(rt.CONTEXT, runner=self.cluster, clock=self.clock)
        self.out = Path(self.tmp.name) / "out"
        self.orch = rt.Orchestrator(self.plan, self.kube, self.out, "OFFLINE-FAKE (not an approval)", cfg=self.cfg, clock=self.clock)

    def go(self):
        self.result = self.orch.run()
        self.receipt = json.loads((self.out / "receipt.json").read_text())
        return self.result

    def close(self):
        if self.cluster.agent:
            self.cluster.agent.shutdown()
        self.keep()
        self.tmp.cleanup()

    def keep(self):
        """RT1_KEEP=<dir>: copy this run's files (host out/, agent root with outboxes and archives) for a failed
        test, or for every test with RT1_KEEP_ALL=1. Files the OS keeps locked are listed, not copied."""
        target = os.environ.get("RT1_KEEP")
        # unittest resets _outcome.success while a cleanup runs; the result's lists already hold this test's failures.
        result = getattr(getattr(self.case, "_outcome", None), "result", None)
        failed = result is not None and any(getattr(t, "test_case", t) is self.case
                                            for t, _ in getattr(result, "failures", []) + getattr(result, "errors", []))
        if not target or not (failed or os.environ.get("RT1_KEEP_ALL")):
            return
        dest = Path(target) / f"{self.case.id().rsplit('.', 2)[-2]}.{self.case._testMethodName}-{uuid.uuid4().hex[:6]}"
        skipped = []
        def copy_file(src, dst, **_):
            try:
                return shutil.copy2(src, dst)
            except OSError as error:
                skipped.append(f"{src}: {type(error).__name__}")
        shutil.copytree(self.tmp.name, dest, copy_function=copy_file, dirs_exist_ok=True)
        (dest / "kept.json").write_text(json.dumps({"failed": failed, "skipped": skipped, "result": getattr(self, "result", None),
                                                    "kubectl_calls": len(self.kube.calls)}, indent=1, default=str))

    def h_events(self, prefix=""):
        path = self.out / "raw" / f"{prefix}export-H" / "H.jsonl"
        return [json.loads(line)["envelope"] for line in path.read_text().splitlines()] if path.exists() else []

    def trial_events(self, name, typ):
        trial_id = self.orch.trials[name]["trial_id"]
        return [e for e in self.h_events() if e.get("trial_id") == trial_id and e["event_type"] == typ]


class Base(unittest.TestCase):
    def assert_clean(self, run):
        """Every write is in ACTIONS, every created object is gone, every changed replica count is back."""
        c = run.cluster
        for w in run.receipt["writes"]:
            name = "frontend-*" if (w["phase"], w["kind"]) == ("P3", "Pod") else ("zd-zer11-<nonce>" if w["kind"] == "Namespace" else w["name"])
            self.assertIn((w["phase"], w["verb"], w["kind"], name), rt.WRITES)
        self.assertNotIn(run.orch.ns, c.namespaces)
        self.assertEqual({}, c.hpas)
        self.assertNotIn(("zero-door", rt.PROFILES_CM), c.cms)
        for name in ("gaia", "hephaestus"):
            self.assertEqual(1, c.deploys[("zero-door", name)]["spec"]["replicas"])
        self.assertEqual("CLEAN", run.result["cleanup"], run.receipt["cleanup_steps"])
        self.assertLessEqual(run.receipt["elapsed_s"], run.plan["caps"]["total_s"])


class Controller(Base):
    def test_controller_and_hpa_recovery_end_to_end_then_score_register_and_serve(self):
        run = Run(self, hpa="scales")
        result = run.go()
        self.assertEqual("COMPLETED", result["verdict"], run.receipt.get("abort"))
        self.assert_clean(run)
        ctrl, hpa = (run.orch.trials[n]["summary"] for n in ("B0-CTRL", "B0-HPA"))
        self.assertEqual(("a", "PLANNED"), (ctrl["stop_point"], ctrl["end_reason"]))
        self.assertEqual("CONFIRMED", ctrl["effect"]["status"])
        self.assertTrue(ctrl["audit_coverage"]["complete"])
        self.assertEqual(1, run.receipt["pod_deletes"]["frontend_pod"])
        evidence = json.loads((run.out / "cluster-evidence.json").read_text())
        self.assertEqual({"state": "UID_CHANGED_NOT_DELETED", "configmap_still_present": True}, evidence["uid_precondition_selftest"])
        # P2 decided on the host from the recorded facts; the canary's /scale owner read with managedFields (RT1-02/03).
        pc = evidence["positive_control"]
        self.assertEqual((True, "REJECTED", "MODE_VIOLATION", True),
                         (pc["valid_o_event_recorded"], pc["decision_state"], pc["decision_classification"], pc["passed"]))
        self.assertEqual([("kubectl", "scale")], [(m["manager"], m["subresource"]) for m in pc["scale_attribution"]["replica_managers"]])
        # Claims are tied to this run's objects (RT1-05): the deleted pod's ReplicaSet uid, this run's HPA uid.
        self.assertTrue(evidence["trials"]["B0-CTRL"]["identity"]["owner_uids"])
        hpa_uid = next(c["uid"] for c in run.orch.created if c["name"] == "frontend-hpa-r1")
        self.assertEqual((hpa_uid, 1), tuple(evidence["trials"]["B0-HPA"]["identity"][k] for k in ("hpa_uid", "frontend_replicas_before")))
        self.assertEqual(1, sum(1 for w in run.receipt["writes"] if w["phase"] == "P3"))
        # HPA cleanup is a cleanup: frontend back to 1 only after the HPA objects were deleted.
        restore = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "restore target replicas")
        self.assertEqual("CLEANUP_SCALED 2->1", restore["detail"]["frontend"])
        steps = [s["step"] for s in run.receipt["cleanup_steps"]]
        self.assertLess(steps.index("delete HPAs"), steps.index("restore target replicas"))
        self.assertEqual(1, run.cluster.deploys[("target-app", "frontend")]["spec"]["replicas"])
        # H evidence: one of each control event per incident, from the right sources; no DETECTED/HEAL invented.
        h = run.h_events()
        for name in ("B0-CTRL", "B0-HPA"):
            for typ, source in (("ATTACK_REQUESTED", "harness"), ("ATTACK_STOPPED", "harness"), ("EFFECT_EVALUATED", "effect_evaluator"),
                                ("RECOVERY_VERIFIED", "recovery_evaluator"), ("AUDIT_COVERAGE", "harness"), ("TRIAL_ENDED", "harness")):
                got = run.trial_events(name, typ)
                self.assertEqual(1, len(got), (name, typ))
                self.assertEqual(source, got[0]["source_component"])
        o = [json.loads(l)["envelope"] for l in (run.out / "raw/export-O/O.jsonl").read_text().splitlines()]
        self.assertEqual({"RUN_CONTEXT", "TRIAL_CONTEXT"}, {e["event_type"] for e in o})
        self.assertFalse({e["event_type"] for e in h} & {"DETECTED", "DECISION", "HEAL_STARTED", "ACTION_COMPLETED"})
        # P8: the ZER-10 CLI recomputes; trial claims need the cluster evidence too.
        p8 = result["p8"]
        self.assertEqual({"label": "RECOVERED_UNDETECTED", "claim": "CONTROLLER_RECOVERY_OBSERVED", "absence_audit_complete": True,
                          "stop_point": "a"}, p8["verdicts"]["B0-CTRL"])
        self.assertEqual(("RECOVERED_UNDETECTED", "HPA_RECOVERY_OBSERVED"),
                         (p8["verdicts"]["B0-HPA"]["label"], p8["verdicts"]["B0-HPA"]["claim"]))
        self.assertEqual(1, p8["positive_control_score"]["quarantined_mode_violations"])
        score = json.loads((run.out / "results" / p8["directory"] / "score.json").read_text())["runs"][0]
        self.assertEqual([], score["findings"]["mode_violations"])
        self.assertNotIn("CROSS_RUN_LINKS_UNCHECKED", score["run_flags"])
        for inc in score["incidents"]:
            self.assertEqual(("N/A", "N/A"), (inc["mttd"], inc["mttr"]))
            self.assertFalse(inc.get("evaluator_mismatch"), inc.get("evaluator_issues"))
        # serve-results over the produced root returns exactly that artifact.
        reader = Path(run.tmp.name) / "reader.json"
        reader.write_text(json.dumps({"id": "r", "purpose": "results-reader", "secret": "offline-rt1-reader-token-0000000000"}))
        with patch.dict(os.environ, {}):
            app, runs = verify.results_app((run.out / "results").resolve(), reader)
            from fastapi.testclient import TestClient
            client = TestClient(app)
            view = client.get(f"/api/results/runs/{score['run_id']}", headers={"Authorization": "Bearer offline-rt1-reader-token-0000000000"})
        self.assertEqual(200, view.status_code)
        self.assertEqual([score["run_id"]], [r["run_id"] for r in runs])
        self.assertEqual(p8["registered"]["sha256"], view.json()["provenance"]["sha256"])
        self.assertEqual(len(score["incidents"]), len(view.json()["incidents"]))

    def test_hpa_not_activated_is_said_so_and_no_effect_leaves_n(self):
        run = Run(self, hpa="idle")
        # Events of an earlier run's HPA of the same name are still listed by the API: they are not this trial's.
        run.cluster.event("target-app", "SuccessfulRescale", "HorizontalPodAutoscaler", "frontend-hpa-r1", "horizontal-pod-autoscaler",
                          "New size: 3; reason: cpu resource utilization above target", uid="hpa-of-an-earlier-run",
                          at_ms=time.time() * 1000 - 3_600_000)
        result = run.go()
        self.assertEqual("COMPLETED", result["verdict"], run.receipt.get("abort"))
        self.assert_clean(run)
        hpa = run.orch.trials["B0-HPA"]["summary"]
        self.assertEqual(("b", "CONFIRMED_NO_EFFECT"), (hpa["stop_point"], hpa["effect"]["status"]))
        self.assertEqual({"label": "CONFIRMED_NO_EFFECT", "claim": "HPA_NOT_ACTIVATED_NO_EFFECT", "absence_audit_complete": True,
                          "stop_point": "b"}, result["p8"]["verdicts"]["B0-HPA"])
        self.assertEqual([], run.trial_events("B0-HPA", "RECOVERY_VERIFIED"))
        events = json.loads((run.out / "cluster-evidence.json").read_text())["trials"]["B0-HPA"]["events"]
        self.assertIn("hpa-of-an-earlier-run", [e["object_uid"] for e in events])  # kept in the evidence, not counted
        restore = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "restore target replicas")
        self.assertEqual("UNCHANGED", restore["detail"]["frontend"])  # nothing to undo; never a scale "to show recovery"

    def test_gap_in_effect_window_without_failure_is_unknown_effect_not_no_effect(self):
        run = Run(self, hpa="slow")
        result = run.go()
        hpa = run.orch.trials["B0-HPA"]["summary"]
        self.assertEqual(("d", "UNKNOWN_EFFECT", "W_EFF_NOT_COVERED"), (hpa["stop_point"], hpa["effect"]["status"], hpa["effect"]["reason"]))
        self.assertTrue(result["abort"].startswith("TRIAL_INCOMPLETE"))
        self.assertEqual("UNKNOWN_EFFECT", result["p8"]["verdicts"]["B0-HPA"]["label"])  # the scorer agrees from raw samples
        effect = run.trial_events("B0-HPA", "EFFECT_EVALUATED")[0]["payload"]
        self.assertGreater(effect["evidence"]["max_gap_s"], run.plan["f01"]["gap_s"])
        self.assert_clean(run)

    def test_no_recovery_with_coverage_is_timeout_and_without_coverage_is_missing_probe(self):
        timeout = Run(self, recreate_s=10_000)
        result = timeout.go()
        ctrl = timeout.orch.trials["B0-CTRL"]["summary"]
        self.assertEqual(("c", "HORIZON"), (ctrl["stop_point"], ctrl["end_reason"]))
        self.assertEqual("TIMEOUT", result["p8"]["verdicts"]["B0-CTRL"]["label"])
        self.assertEqual("NOT_RECOVERED_WITHIN_CAP", result["p8"]["verdicts"]["B0-CTRL"]["claim"])
        # The target is still down: the HPA trial never reaches its fault (no load pod), and the run stops.
        self.assertEqual("BASELINE_UNHEALTHY (B0-HPA)", result["abort"])
        self.assertNotIn(rt.LOAD_POD, [w["name"] for w in timeout.receipt["writes"]])
        self.assert_clean(timeout)
        gap = Run(self, after_fault="hang")
        result = gap.go()
        self.assertEqual("MISSING_PROBE", result["p8"]["verdicts"]["B0-CTRL"]["label"])  # gaps never become TIMEOUT
        self.assertNotIn("TIMEOUT", json.dumps(result["p8"]["verdicts"]))
        self.assert_clean(gap)


class Faults(Base):
    def test_watcher_failure_means_no_audit_coverage_and_no_absence_claim(self):
        run = Run(self, hpa="idle")
        run.cluster.fail_if = lambda c, args: bool(c.fault_at) and args[:4] == ["get", "pods", "-n", "zero-door"] \
            and time.monotonic() - c.fault_at < 1.5
        result = run.go()
        ctrl = run.orch.trials["B0-CTRL"]["summary"]
        self.assertFalse(ctrl["audit_coverage"]["complete"])
        self.assertEqual([], run.trial_events("B0-CTRL", "AUDIT_COVERAGE"))
        self.assertEqual("RECOVERED_BUT_ABSENCE_AUDIT_INCOMPLETE", result["p8"]["verdicts"]["B0-CTRL"]["claim"])
        self.assertEqual(1, len(run.trial_events("B0-HPA", "AUDIT_COVERAGE")))  # control: the watch worked again later
        self.assert_clean(run)

    def test_zero_door_pod_in_b0_window_aborts_positive_control_for_absence(self):
        run = Run(self)
        def someone_scales_gaia(cluster, args):
            if cluster.fault_at and cluster.deploys[("zero-door", "gaia")]["spec"]["replicas"] == 0:
                cluster.deploys[("zero-door", "gaia")]["spec"]["replicas"] = 1
        run.cluster.hooks.append(someone_scales_gaia)
        result = run.go()
        self.assertEqual("ZERO_DOOR_COMPONENT_RUNNING", result["abort"])
        ctrl = run.orch.trials["B0-CTRL"]["summary"]
        self.assertEqual("d", ctrl["stop_point"])
        self.assertEqual([], run.trial_events("B0-CTRL", "AUDIT_COVERAGE"))
        self.assertEqual(1, len(run.trial_events("B0-CTRL", "ATTACK_STOPPED")))
        self.assertNotIn("B0-HPA", run.orch.trials)
        self.assert_clean(run)

    def test_h_ack_failure_stops_closes_and_cleans_up_without_scoring(self):
        run = Run(self)
        def break_h(cluster, args):
            if cluster.fault_at and cluster.agent and not cluster.agent.archives["H"].failure:
                cluster.agent.archives["H"].fail(OSError("disk"))
        run.cluster.hooks.append(break_h)
        result = run.go()
        self.assertEqual("ABORTED", result["verdict"])
        self.assertTrue(result["abort"].startswith(("PERSISTENCE", "H_ACK_STALL")), result["abort"])
        self.assertIn("export-H", result["p5"]["errors"])
        self.assertEqual("MAIN_EXPORTS_MISSING", result["p8"]["skipped"])  # nothing is scored from an export that does not exist
        receipt = json.loads((run.out / "raw" / "agent-receipt.json").read_text())
        self.assertEqual("d", receipt["trials"]["B0-CTRL"]["stop_point"])
        self.assertTrue(any(p.name.endswith(".outbox.jsonl") for p in (run.out / "raw" / "work").iterdir()))
        self.assert_clean(run)

    def test_control_ack_later_than_its_deadline_fails_closed(self):
        """N1's signature on purpose: the gateway records ATTACK_REQUESTED but answers after the control deadline
        (the client has gone: WinError 10053 on Windows). The run stops at PERSISTENCE; it is never a pass."""
        from event_pipeline.gateway import Gateway
        run = Run(self, cfg_over={"grace_s": 2})
        submit, slow = Gateway.submit, {"n": 0}
        def late(gateway, event, *args, **kwargs):
            answer = submit(gateway, event, *args, **kwargs)
            if isinstance(event, dict) and event.get("event_type") == "ATTACK_REQUESTED" and not slow["n"]:
                slow["n"] += 1
                time.sleep(run.cfg["grace_s"] + 0.5)
            return answer
        with patch.object(Gateway, "submit", late):
            result = run.go()
        self.assertTrue(result["abort"].startswith("PERSISTENCE (CONTROL_NOT_DURABLE: ATTACK_REQUESTED None after"), result["abort"])
        receipt = json.loads((run.out / "raw" / "agent-receipt.json").read_text())
        late_one = next(d for d in receipt["control_deliveries"] if d["event_type"] == "ATTACK_REQUESTED")
        self.assertIsNone(late_one["state"])
        self.assertGreaterEqual(late_one["ms"], late_one["deadline_ms"])
        self.assertTrue(all(d["ms"] < d["deadline_ms"] for d in receipt["control_deliveries"] if d is not late_one and d["state"]))
        self.assertEqual("d", receipt["trials"]["B0-CTRL"]["stop_point"])
        self.assertEqual(0, run.receipt["pod_deletes"]["frontend_pod"])  # no fault after an unacknowledged request
        self.assert_clean(run)

    def test_target_uid_changed_is_never_overwritten(self):
        run = Run(self, hpa="scales")
        def redeploy(cluster, args):
            if cluster.load and not cluster.load.get("redeployed"):
                cluster.load["redeployed"] = True
                cluster.add_deploy("target-app", "frontend", 2)  # someone else recreated it: new uid
        run.cluster.hooks.append(redeploy)
        result = run.go()
        restore = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "restore target replicas")
        self.assertEqual("FAILED", restore["status"])
        self.assertIn("REFUSED_UID_CHANGED", restore["detail"])
        self.assertEqual(2, run.cluster.deploys[("target-app", "frontend")]["spec"]["replicas"])
        self.assertFalse([w for w in run.receipt["writes"] if w["phase"] == "P7" and w["name"] == "frontend"])
        self.assertEqual("UID_CHANGED", result["final_diff"]["deployments"]["target-app/frontend"])
        self.assertEqual("INCOMPLETE", result["cleanup"])
        self.assertNotIn(run.orch.ns, run.cluster.namespaces)  # the rest of the cleanup still ran

    def test_interrupt_in_trial_and_in_cleanup(self):
        run = Run(self)
        state = {"trial": False, "cleanup": False}
        def interrupt(cluster, args):
            if cluster.fault_at and not state["trial"] and args[0] == "exec" and '"status"' in args[-1]:
                state["trial"] = True
                raise KeyboardInterrupt
            if run.orch.cleaning and not state["cleanup"] and args[0] == "scale":
                state["cleanup"] = True
                raise KeyboardInterrupt
        run.cluster.hooks.append(interrupt)
        result = run.go()
        self.assertEqual(("ABORTED", "INTERRUPTED"), (result["verdict"], result["abort"]))
        self.assertTrue(state["cleanup"])
        restore = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "restore gaia/hephaestus replicas")
        self.assertEqual(("DONE", 2), (restore["status"], restore["attempts"]))
        ctrl = json.loads((run.out / "raw" / "agent-receipt.json").read_text())["trials"]["B0-CTRL"]
        self.assertEqual(("d", "ABORTED"), (ctrl["stop_point"], ctrl["end_reason"]))
        self.assertIn(result["p8"]["verdicts"]["B0-CTRL"]["label"], {"UNKNOWN_EFFECT", "MISSING_PROBE", "RECOVERED_UNDETECTED"})
        self.assertNotEqual("TIMEOUT", result["p8"]["verdicts"]["B0-CTRL"]["label"])
        self.assert_clean(run)


class Budget(Base):
    def test_total_cap_stops_the_run_and_cleanup_fits_in_the_reserve(self):
        run = Run(self)
        def jump(cluster, args):
            if cluster.fault_at and not getattr(run, "jumped", False):
                run.jumped = True
                # Main window used up: everything later must fit in the P7 reserve of the same cap.
                run.clock.offset = run.orch.main_deadline - time.monotonic() + 0.1
        run.cluster.hooks.append(jump)
        result = run.go()
        self.assertEqual("TOTAL_CAP", result["abort"])
        self.assert_clean(run)
        self.assertNotIn("B0-HPA", run.orch.trials)

    def test_probe_sample_cap_stops_at_d_and_scores_missing_probe(self):
        plan = scaled_plan()
        run = Run(self, plan=plan, recreate_s=10_000)
        run.cfg["budgets"]["B0-CTRL"]["max_samples"] = 12
        result = run.go()
        self.assertTrue(result["abort"].startswith("TRIAL_INCOMPLETE"))
        ctrl = run.orch.trials["B0-CTRL"]["summary"]
        self.assertEqual("d", ctrl["stop_point"])
        self.assertEqual("MAX_SAMPLES", ctrl["probe"]["stop_reason"])
        self.assertLessEqual(ctrl["samples"], 12)
        self.assertIn(result["p8"]["verdicts"]["B0-CTRL"]["label"], {"MISSING_PROBE", "UNKNOWN_EFFECT"})
        self.assert_clean(run)

    def test_budgets_match_plan_check_and_pod_delete_cap(self):
        matrix = verify.plan_matrix()
        for name, t in matrix["trials"].items():
            b = rt.trial_budget(verify.RT1, name)
            self.assertEqual((t["probe_max_duration_s"], t["probe_max_samples"], t["probe_max_requests"]),
                             (b["max_duration_s"], b["max_samples"], b["max_requests"]))
        self.assertEqual(1, sum(1 for a in rt.ACTIONS if a[:3] == ("P3", "delete", "Pod")))
        orch = Run(self).orch
        orch.deletes["frontend_pod"] = 1
        orch.main_deadline = time.monotonic() + 30
        with self.assertRaises(rt.Abort) as caught:
            orch.fault("B0-CTRL")
        self.assertEqual("POD_DELETE_CAP", caught.exception.reason)


class Findings(Base):
    """rt1-fix-01: one regression per finding of docs/evidence/ZER-11/codex-rt1-review.md, expected-fixed."""

    @staticmethod
    def lose_answer(run, match):
        """The API server performs the first matching create but its answer never reaches the harness."""
        real, state = run.cluster, {"fired": False}
        def cli(argv, stdin=None, timeout=None):
            answer = real(argv, stdin, timeout)
            if not state["fired"] and argv[4] == "create" and stdin and match(json.loads(stdin)):
                state["fired"] = True
                return None, b"", b"TIMEOUT"
            return answer
        run.kube.runner = cli
        return state

    @staticmethod
    def host_disk(run, when):
        """ENOSPC for every host-side file write under the run's out/ directory once `when()` holds."""
        real = {n: getattr(Path, n) for n in ("write_bytes", "write_text", "mkdir", "rename")}
        def wrap(name):
            def fn(path, *args, **kwargs):
                if (path == run.out or run.out in path.parents) and when():
                    raise OSError(errno.ENOSPC, "No space left on device")
                return real[name](path, *args, **kwargs)
            return fn
        return [patch.object(Path, n, wrap(n)) for n in real]

    def assert_cluster_restored(self, run):
        c = run.cluster
        for ns, name in (("zero-door", "gaia"), ("zero-door", "hephaestus"), ("target-app", "frontend"), ("target-app", "cartservice")):
            self.assertEqual(1, c.deploys[(ns, name)]["spec"]["replicas"], name)
        self.assertNotIn(run.orch.ns, c.namespaces)
        self.assertEqual({}, c.hpas)
        self.assertNotIn(("zero-door", rt.PROFILES_CM), c.cms)
        restored = {(w["name"], w["exit"]) for w in run.orch.writes if (w["phase"], w["verb"]) == ("P7", "scale")}
        self.assertTrue({("gaia", 0), ("hephaestus", 0)} <= restored, restored)

    # ---------------------------------------------------------------- RT1-01
    def test_rt1_01_host_disk_full_in_main_phase_still_runs_every_cleanup_step(self):
        run = Run(self, hpa="scales")
        gaia = run.cluster.deploys[("zero-door", "gaia")]["spec"]
        patches = self.host_disk(run, lambda: gaia["replicas"] == 0 or run.orch.cleaning)
        for p in patches:
            p.start()
        try:
            result = run.orch.run()  # returns; never raises past P7
        finally:
            for p in patches:
                p.stop()
        self.assertEqual("ABORTED", result["verdict"])
        self.assertTrue(result["abort"].startswith("UNEXPECTED (OSError"), result["abort"])
        self.assert_cluster_restored(run)
        steps = {s["step"]: s for s in run.orch.cleanup_log}
        self.assertEqual(7, len(steps))
        self.assertEqual("FAILED", steps["pull evidence"]["status"])  # said, not hidden as DONE
        for name in ("delete HPAs", "restore target replicas", "restore gaia/hephaestus replicas", "delete profiles ConfigMap",
                     "delete namespace", "final diff against P0"):
            self.assertEqual("DONE", steps[name]["status"], steps[name])
        self.assertEqual("INCOMPLETE", result["cleanup"])
        self.assertIn("RECEIPT_NOT_WRITTEN:receipt.json:OSError", result["errors"])
        self.assertFalse((run.out / "receipt.json").exists())
        self.assertEqual("MAIN_EXPORTS_MISSING", result["p8"]["skipped"])

    def test_rt1_01_host_disk_full_from_cleanup_on_and_a_failing_first_step(self):
        run = Run(self)
        state = {"trial": False}
        def interrupt(cluster, args):
            if cluster.fault_at and not state["trial"] and args[0] == "exec" and '"status"' in args[-1]:
                state["trial"] = True
                raise KeyboardInterrupt
        run.cluster.hooks.append(interrupt)
        patches = self.host_disk(run, lambda: run.orch.cleaning)
        for p in patches:
            p.start()
        try:
            result = run.orch.run()
        finally:
            for p in patches:
                p.stop()
        self.assertEqual(("ABORTED", "INTERRUPTED"), (result["verdict"], result["abort"]))
        self.assertIn("SALVAGE_EXPORT:OSError", result["errors"])
        steps = {s["step"]: s for s in run.orch.cleanup_log}
        self.assertEqual("FAILED", steps["pull evidence"]["status"])
        self.assertIn("EVIDENCE_NOT_PULLED", steps["pull evidence"]["detail"])
        self.assertEqual("DONE", steps["restore gaia/hephaestus replicas"]["status"])
        self.assert_cluster_restored(run)
        self.assertEqual("MATCHES_P0", steps["final diff against P0"]["detail"])

    def test_rt1_01_unexpected_error_in_a_trial_or_a_cleanup_step_never_skips_the_rest(self):
        run = Run(self, hpa="scales")
        state = {"json": False, "delete": False}
        def garbage(cluster, args):
            if cluster.fault_at and not state["json"] and args[:2] == ["get", "nodes"]:
                state["json"] = True
                raise ValueError("Expecting value: line 1 column 1 (char 0)")  # what json.loads raises on a truncated answer
        run.cluster.hooks.append(garbage)
        result = run.go()
        self.assertTrue(result["abort"].startswith("UNEXPECTED (ValueError"), result["abort"])
        self.assertEqual("d", run.orch.trials["B0-CTRL"]["summary"]["stop_point"])
        self.assert_clean(run)
        # A cleanup step that raises something unexpected (kubectl gone, OSError) is FAILED; the next steps still run.
        run = Run(self, hpa="scales")
        real = run.cluster
        def cli(argv, stdin=None, timeout=None):
            if run.orch.cleaning and not state["delete"] and argv[4:6] == ["delete", "--raw"] and "horizontalpodautoscalers" in argv[6]:
                state["delete"] = True
                raise OSError(errno.ENOENT, "kubectl: No such file or directory")
            return real(argv, stdin, timeout)
        run.kube.runner = cli
        result = run.go()
        hpas = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "delete HPAs")
        self.assertEqual("FAILED", hpas["status"])
        self.assertIn('"cartservice-hpa-r1": "DELETED"', hpas["detail"])  # the other HPA was still removed
        self.assertEqual(["frontend-hpa-r1"], result["final_diff"]["hpas_left"])
        self.assertEqual("INCOMPLETE", result["cleanup"])
        for name in ("gaia", "hephaestus"):
            self.assertEqual(1, real.deploys[("zero-door", name)]["spec"]["replicas"])
        self.assertNotIn(run.orch.ns, real.namespaces)

    # ---------------------------------------------------------------- RT1-02
    def test_rt1_02_ownership_reads_ask_for_managed_fields_and_a_wrong_manager_still_fails(self):
        run = Run(self, scale_manager="argocd-application-controller")
        result = run.go()
        self.assertEqual("ATTRIBUTION_CONTROL_FAILED", result["abort"])
        attribution = json.loads((run.out / "cluster-evidence.json").read_text())["positive_control"]["scale_attribution"]
        self.assertIn("argocd-application-controller", [m["manager"] for m in attribution["replica_managers"]])
        self.assertFalse([w for w in run.receipt["writes"] if w["phase"] in ("P3", "P4")])
        canary_reads = [c for c in run.cluster.calls if c[:3] == ["get", "deploy", rt.CANARY]]
        self.assertTrue(canary_reads and all("--show-managed-fields=true" in c for c in canary_reads))
        self.assert_clean(run)

    # ---------------------------------------------------------------- RT1-03
    def test_rt1_03_positive_control_failure_is_decided_by_the_host_and_stops_before_the_target(self):
        from measurement.sink import HttpHSink, Retry
        original = HttpHSink.deliver
        cases = {"decision ack lost": lambda: (_ for _ in ()).throw(Retry("injected decision-only ACK outage")),
                 "wrong classification": lambda: ("REJECTED", "SCHEMA_INVALID"),
                 "decision admitted": lambda: ("DELIVERED", "RECORDED")}
        for name, answer in cases.items():
            with self.subTest(name):
                def deliver(sink, event, deadline_ns=None):
                    if event["event_type"] == "DECISION":
                        return answer()
                    return original(sink, event, deadline_ns)
                run = Run(self)
                with patch.object(HttpHSink, "deliver", deliver):
                    result = run.go()
                self.assertTrue(result["abort"].startswith("POSITIVE_CONTROL_FAILED"), result["abort"])
                pc = json.loads((run.out / "cluster-evidence.json").read_text())["positive_control"]
                self.assertIs(False, pc["passed"])
                self.assertTrue(pc["valid_o_event_recorded"])
                self.assertFalse([w for w in run.receipt["writes"] if w["phase"] in ("P2", "P3", "P4")])
                self.assert_clean(run)
        # The agent's dispatch "ok" can no longer be overwritten by, or overwrite, a command's own outcome.
        with tempfile.TemporaryDirectory() as tmp:
            agent = rt.Agent(Path(tmp))
            agent.cmd_hello = lambda command: {"ok": False}
            self.assertEqual({"ok": False, "error": "RESULT_SHADOWS_OK", "detail": "hello"}, agent.handle({"action": "hello"}))
        self.assertFalse(rt.control_passed({"valid_o_event_recorded": True, "decision_state": None, "decision_classification": None,
                                            "passed": True}))

    # ---------------------------------------------------------------- RT1-04
    def test_rt1_04_lost_create_answers_are_reconciled_by_label_and_removed_by_uid(self):
        with self.subTest("namespace"):
            run = Run(self)
            lost = self.lose_answer(run, lambda o: o["kind"] == "Namespace")
            result = run.go()
            self.assertTrue(lost["fired"])
            self.assertTrue(result["abort"].startswith("WRITE_FAILED (create Namespace"), result["abort"])
            record = run.orch.created[0]
            self.assertEqual(("Namespace", "RECONCILED"), (record["kind"], record["state"]))
            self.assertTrue(record["uid"])
            delete = [w for w in run.orch.writes if (w["verb"], w["kind"]) == ("delete", "Namespace")]
            self.assertEqual(1, len(delete))
            self.assertNotIn(run.orch.ns, run.cluster.namespaces)
            self.assertFalse(result["final_diff"]["namespace_left"])
            self.assertEqual("CLEAN", result["cleanup"])
        with self.subTest("namespace, read-back also fails at first: P7 asks again"):
            run = Run(self)
            self.lose_answer(run, lambda o: o["kind"] == "Namespace")
            run.cluster.fail_if = lambda c, args: args[:2] == ["get", "namespace"] and not run.orch.cleaning
            result = run.go()
            self.assertEqual("RECONCILED", run.orch.created[0]["state"])
            self.assertNotIn(run.orch.ns, run.cluster.namespaces)
            self.assertEqual("CLEAN", result["cleanup"])
        for what, match, knobs in (("HPA", lambda o: o["kind"] == "HorizontalPodAutoscaler", {"hpa": "scales"}),
                                   ("load pod", lambda o: o["metadata"]["name"] == rt.LOAD_POD, {"hpa": "scales"}),
                                   ("profiles ConfigMap", lambda o: o["metadata"]["name"] == rt.PROFILES_CM, {})):
            with self.subTest(what):
                run = Run(self, **knobs)
                self.lose_answer(run, match)
                result = run.go()
                self.assertTrue(result["abort"].startswith("WRITE_FAILED"), result["abort"])
                record = next(c for c in run.orch.created if match({"kind": c["kind"], "metadata": {"name": c["name"]}}))
                self.assertEqual("RECONCILED", record["state"])
                self.assert_clean(run)
                if what == "load pod":
                    self.assertTrue(run.cluster.load["deleted"])  # stopped by uid, not left running in the trial

    def test_rt1_04_an_object_that_is_not_ours_is_never_deleted_and_cleanup_says_incomplete(self):
        with self.subTest("namespace name held by an object without the run label"):
            run = Run(self)
            def squat(cluster, args):
                if args[0] == "create" and run.orch.ns not in cluster.namespaces and run.orch.phases[-1]["phase"] == "P1":
                    cluster.namespaces[run.orch.ns] = {"uid": cluster.uid(), "labels": {}}
            run.cluster.hooks.append(squat)
            result = run.go()
            other = run.cluster.namespaces.get(run.orch.ns)
            self.assertIsNotNone(other)  # left alone
            self.assertEqual("NAME_HELD_BY_OTHER_OBJECT", run.orch.created[0]["state"])
            self.assertFalse([w for w in run.orch.writes if (w["verb"], w["kind"]) == ("delete", "Namespace")])
            self.assertTrue(result["final_diff"]["namespace_left"])
            self.assertEqual("INCOMPLETE", result["cleanup"])
        with self.subTest("profiles ConfigMap replaced by another uid during the run"):
            run = Run(self)
            def replace(cluster, args):
                key = ("zero-door", rt.PROFILES_CM)
                if cluster.fault_at and key in cluster.cms and not getattr(run, "replaced", False):
                    run.replaced = True
                    cluster.cms[key] = copy.deepcopy(cluster.cms[key])
                    cluster.cms[key]["metadata"]["uid"] = cluster.uid()
            run.cluster.hooks.append(replace)
            result = run.go()
            step = next(s for s in run.receipt["cleanup_steps"] if s["step"] == "delete profiles ConfigMap")
            self.assertEqual("FAILED", step["status"])
            self.assertIn("UID_CHANGED_NOT_DELETED", step["detail"])
            self.assertIn(("zero-door", rt.PROFILES_CM), run.cluster.cms)
            self.assertEqual([rt.PROFILES_CM], result["final_diff"]["profiles_left"])
            self.assertEqual("INCOMPLETE", result["cleanup"])

    # ---------------------------------------------------------------- RT1-05
    def test_controller_claim_requires_trial_time_window_before_recovery(self):
        """A matching replacement seen later cannot explain an earlier business recovery."""
        t = 1_800_000_000_000
        base = {"identity": {"t_req": iso(t), "owner_uids": ["rs-1"], "pods_before": ["old"]},
                "frontend_pods_after": [{"name": "frontend-new", "uid": "new", "ready": True,
                                         "owner": [{"uid": "rs-1"}]}],
                "events": [{"reason": "SuccessfulCreate", "source": "replicaset-controller",
                            "object_uid": "rs-1", "message": "Created pod: frontend-new", "t_ms": t + 1000}]}
        cases = (("valid", t + 1000, iso(t), t + 20000, True),
                 ("same second floored", t - 400, iso(t), t + 20000, True),
                 ("before trial", t - 60000, iso(t), t + 20000, False),
                 ("full second before trial", t - 1000, iso(t), t + 20000, False),
                 ("event time missing", None, iso(t), t + 20000, False),
                 ("request time missing", t + 1000, None, t + 20000, False),
                 ("request time invalid", t + 1000, "invalid", t + 20000, False),
                 ("recovery time missing", t + 1000, iso(t), None, False),
                 ("one second before recovery", t + 19000, iso(t), t + 20000, False),
                 ("overlaps recovery second", t + 19500, iso(t), t + 20000, False),
                 ("at recovery", t + 20000, iso(t), t + 20000, False),
                 ("after recovery", t + 25000, iso(t), t + 20000, False))
        for why, event_at, requested_at, recovered_at, accepted in cases:
            with self.subTest(why):
                ev = copy.deepcopy(base)
                ev["identity"]["t_req"] = requested_at
                ev["events"][0]["t_ms"] = event_at
                run = {"incidents": [{"trial_id": "trl-1", "label": "RECOVERED_UNDETECTED",
                                      "milestones": {"t_rec": {"t_ms": recovered_at}}}]}
                receipt = {"trials": {"B0-CTRL": {"trial_id": "trl-1", "audit_coverage": {"complete": True},
                                                 "stop_point": "a"}}}
                result = rt.interpret(run, receipt, {"trials": {"B0-CTRL": ev}})["B0-CTRL"]
                self.assertEqual("RECOVERED_UNDETECTED", result["label"])
                self.assertEqual("CONTROLLER_RECOVERY_OBSERVED" if accepted else "RECOVERED_CONTROLLER_EVIDENCE_MISSING",
                                 result["claim"])

    def test_rt1_05_controller_and_hpa_claims_need_this_trials_objects(self):
        from measurement.clock import stamp
        t = 1_800_000_000_000
        incident = lambda label: {"incidents": [{"trial_id": "trl-1", "label": label,
                                                 "milestones": {"t_rec": {"t_ms": t + 20_000}, "t_stop": {"t_ms": t + 30_000}}}]}
        receipt = lambda name: {"trials": {name: {"trial_id": "trl-1", "audit_coverage": {"complete": True}, "stop_point": "a"}}}
        def claim(name, ev, label="RECOVERED_UNDETECTED"):
            return rt.interpret(incident(label), receipt(name), {"trials": {name: ev}})[name]["claim"]
        created = lambda rs, pod: {"reason": "SuccessfulCreate", "object": "ReplicaSet/frontend-rs", "object_uid": rs,
                                   "source": "replicaset-controller", "t_ms": t + 1000, "message": f"Created pod: {pod}"}
        pod = lambda name, rs, ready=True: {"name": name, "uid": "uid-" + name, "ready": ready, "owner": [{"kind": "ReplicaSet", "uid": rs}]}
        ctrl = {"identity": {"t_req": stamp(t), "deleted_uid": "uid-frontend-old", "owner_uids": ["rs-1"], "pods_before": ["uid-frontend-old"]},
                "events": [created("rs-1", "frontend-new")], "frontend_pods_after": [pod("frontend-new", "rs-1")]}
        self.assertEqual("CONTROLLER_RECOVERY_OBSERVED", claim("B0-CTRL", ctrl))
        for why, change in (("historical event, no replacement pod", {"frontend_pods_after": []}),
                            ("replacement from another ReplicaSet", {"frontend_pods_after": [pod("frontend-new", "rs-9")]}),
                            ("event of another ReplicaSet object", {"events": [created("rs-old", "frontend-new")]}),
                            ("event names another pod", {"events": [created("rs-1", "frontend-older")]}),
                            ("pod existed before the delete", {"frontend_pods_after": [pod("frontend-old", "rs-1")]}),
                            ("replacement not Ready", {"frontend_pods_after": [pod("frontend-new", "rs-1", ready=False)]})):
            with self.subTest(why):
                self.assertEqual("RECOVERED_CONTROLLER_EVIDENCE_MISSING", claim("B0-CTRL", dict(ctrl, **change)))
        # Codex's replay: an old SuccessfulCreate, no identity recorded.
        self.assertEqual("RECOVERED_CONTROLLER_EVIDENCE_MISSING", claim("B0-CTRL", {"events": [created(None, "x")], "frontend_pods_after": []}))
        rescale = lambda uid, size, at, source="horizontal-pod-autoscaler": {
            "reason": "SuccessfulRescale", "object": "HorizontalPodAutoscaler/frontend-hpa-r1", "object_uid": uid, "source": source,
            "t_ms": at, "message": f"New size: {size}; reason: cpu resource utilization above target"}
        hpa = {"identity": {"t_req": stamp(t), "hpa_uid": "hpa-2", "frontend_replicas_before": 1}, "events": [rescale("hpa-2", 2, t + 5000)],
               "frontend_pods_after": []}
        self.assertEqual("HPA_RECOVERY_OBSERVED", claim("B0-HPA", hpa))
        for why, events, expected in (
                ("older HPA object of the same name", [rescale("hpa-1", 2, t + 5000)], "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"),
                ("downscale only", [rescale("hpa-2", 1, t + 5000)], "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"),
                ("scale-up before T_req", [rescale("hpa-2", 2, t - 5000)], "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"),
                ("scale-up a full second before T_req", [rescale("hpa-2", 2, t - 1000)], "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"),
                ("scale-up stamped in T_req's second (floored)", [rescale("hpa-2", 2, t - 400)], "HPA_RECOVERY_OBSERVED"),
                ("undated", [rescale("hpa-2", 2, None)], "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"),
                ("scale-up at recovery", [rescale("hpa-2", 2, t + 19_500)], "RESCALE_ORDER_AMBIGUOUS_OR_AFTER_RECOVERY"),
                ("not by the HPA controller", [rescale("hpa-2", 2, t + 5000, "kubectl")], "RESCALE_NOT_BY_HPA"),
                ("no rescale event at all", [], "RECOVERED_WITHOUT_HPA_RESCALE")):
            with self.subTest(why):
                self.assertEqual(expected, claim("B0-HPA", dict(hpa, events=events)))
        self.assertEqual("RECOVERED_HPA_EVIDENCE_MISSING", claim("B0-HPA", {"events": [rescale(None, 1, 1000)], "frontend_pods_after": []}))
        self.assertEqual("RECOVERED_HPA_EVIDENCE_MISSING", claim("B0-HPA", {"events_error": "KUBECTL_FAILED", "identity": hpa["identity"]}))
        # No effect: "HPA not activated" only when this trial's HPA did not scale up, and only with the evidence.
        self.assertEqual("HPA_NOT_ACTIVATED_NO_EFFECT", claim("B0-HPA", dict(hpa, events=[rescale("hpa-1", 3, t + 5000)]), "CONFIRMED_NO_EFFECT"))
        self.assertEqual("NO_EFFECT", claim("B0-HPA", hpa, "CONFIRMED_NO_EFFECT"))
        self.assertEqual("NO_EFFECT", claim("B0-HPA", {"events": []}, "CONFIRMED_NO_EFFECT"))


class Boundaries(unittest.TestCase):
    def test_preflight_ignores_untagged_node_images_but_still_requires_the_image(self):
        for image_present in (True, False):
            with self.subTest(image_present=image_present):
                run = Run(self)
                run.orch.main_deadline = time.monotonic() + 30
                read = run.kube.json
                def nodes_with_untagged_images(args, *a, **kw):
                    obj = read(args, *a, **kw)
                    if args == ["get", "nodes"]:
                        for node in obj["items"]:
                            node["status"]["images"] = [{"names": None, "sizeBytes": 38746964}]
                            if image_present:
                                node["status"]["images"].append({"names": ["docker.io/" + run.cfg["image"]]})
                    return obj
                with patch.object(run.kube, "json", side_effect=nodes_with_untagged_images):
                    if image_present:
                        run.orch.p0()
                        self.assertTrue(run.orch.preflight["image_present"])
                    else:
                        with self.assertRaises(rt.Abort) as caught:
                            run.orch.p0()
                        self.assertEqual("IMAGE_ABSENT", caught.exception.reason)
                self.assertEqual([], run.orch.writes)

    def test_offline_entrypoints_never_run_kubectl(self):
        with patch("subprocess.run", side_effect=AssertionError("subprocess")):
            self.assertEqual(0, verify.main(["rt1"]))
            self.assertEqual(2, verify.main(["rt1", "--execute"]))
            self.assertEqual(2, verify.main(["rt1", "--execute", "--runtime-approval", "x", "--context", "other"]))
        with self.assertRaises(rt.HarnessError):
            rt.Kube("k3d-other")

    def test_uid_precondition_not_honoured_stops_before_the_target(self):
        run = Run(self, ignore_preconditions=True)
        result = run.go()
        self.assertTrue(result["abort"].startswith("UID_PRECONDITION_SELFTEST_FAILED"), result["abort"])
        self.assertFalse([w for w in run.receipt["writes"] if w["phase"] in ("P2", "P3", "P4")])
        self.assertNotIn(run.orch.ns, run.cluster.namespaces)

    def test_writes_outside_actions_are_refused(self):
        run = Run(self)
        run.orch.main_deadline = time.monotonic() + 30
        with self.assertRaises(rt.HarnessError) as caught:
            run.orch.write("P3", "delete", "Deployment", "frontend", ["delete", "deploy", "frontend"], run.orch.main_deadline)
        self.assertEqual("WRITE_NOT_IN_ACTIONS", caught.exception.reason)
        for kind, name in (("Pod", "cartservice-abc12"), ("Namespace", "target-app")):  # right verb, wrong object
            with self.assertRaises(rt.HarnessError):
                run.orch.write("P3" if kind == "Pod" else "P7", "delete", kind, name, ["delete", "x"], run.orch.main_deadline)
        self.assertEqual([], run.cluster.calls)

    def test_unsafe_tar_member_is_refused(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            info = tarfile.TarInfo("../escape")
            info.size = 1
            archive.addfile(info, io.BytesIO(b"x"))
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(rt.HarnessError):
            rt.extract(buffer.getvalue(), Path(tmp) / "raw")

    def test_fake_hang_honours_the_live_deadline_of_a_cleanup_request(self):
        """N1 (rt1-fix-01): when the fault lands after the probe's transaction has filled the cart, its cleanup
        (POST /cart/empty) carries a callable deadline. The fake's hang used to compare it as a number, raise
        TypeError and kill the probe (trial stopped at (d), UNKNOWN_EFFECT instead of MISSING_PROBE)."""
        with tempfile.TemporaryDirectory() as tmp:
            cluster = FakeCluster(tmp, "http://127.0.0.1:9", after_fault="hang")
            cluster.fault_at = time.monotonic()
            end = time.perf_counter_ns() + int(0.3e9)
            started = time.perf_counter_ns()
            with self.assertRaises(Failure) as caught:
                cluster.http("http://127.0.0.1:9/cart/empty", "POST", (), b"", deadline_ns=lambda: end)
            self.assertEqual(("TIMEOUT", "DEADLINE"), (caught.exception.detail, caught.exception.reason))
            self.assertGreaterEqual(time.perf_counter_ns(), end)
            self.assertLess(time.perf_counter_ns() - started, int(2e9))

    def test_load_generator_honours_its_request_cap(self):
        server, cls, origin = serve(Boutique)
        self.addCleanup(stop, server)
        out = io.StringIO()
        with patch("sys.stdout", out):
            rt.run_load(origin, rps=200, connections=4, duration_s=2, max_requests=25)
        counts = json.loads(out.getvalue())
        self.assertEqual(25, counts["sent"])
        self.assertEqual(25, sum(1 for method, path, *_ in cls.log if path == "/"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
