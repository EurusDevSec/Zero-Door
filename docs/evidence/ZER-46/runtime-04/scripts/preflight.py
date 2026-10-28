"""Approved ZER-46 first gate. Read-only lab preflight; no build/apply/restart/fixture traffic.

On failure this attempt ends with independent cleanup/readback; no subsequent phase may run. On success
the same 20-minute window remains open for the approved component phase, not a new authorization window.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-01"
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from measurement.flows import Flow, Memory, boutique_spec  # noqa: E402


class Lab:
    def __init__(self):
        self.started, self.deadline = time.time(), time.monotonic() + 1200
        self.work_end = self.deadline - 300
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.seq, self.requests = 0, 0
        self.failure, self.samples = [], []
        self.env = dict(os.environ, MSYS_NO_PATHCONV="1", PYTHONDONTWRITEBYTECODE="1")
        args = json.loads((ROOT / "tests/fixtures/zer10/plan-synthetic-boutique.json").read_text())["flow_spec"]["args"]
        args["product_marker"] = "Sunglasses"
        self.flow = Flow(boutique_spec(**args), "http://127.0.0.1:8080", ["http://127.0.0.1:8080"])
        self.memory = Memory()

    def save(self, name, obj):
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".writing")
        temp.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding="utf8")
        temp.replace(path)

    def command(self, args, timeout=15, allowed=(0,)):
        if time.monotonic() >= self.deadline:
            raise RuntimeError("GLOBAL_BUDGET")
        with self.lock:
            self.seq += 1
            seq = self.seq
        receipt = {"at": time.time(), "args": args}
        try:
            result = subprocess.run(args, capture_output=True, timeout=min(timeout, self.deadline - time.monotonic()),
                                    env=self.env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            # Do not publish a k3s token if an existing node happened to carry it on its command line.
            text = result.stdout.decode(errors="replace").replace("\x00", " ")
            text = re.sub(r"(?i)(--(?:agent-)?token(?:=|\s+))\S+", r"\1[REDACTED]", text)
            receipt.update(returncode=result.returncode, stdout=text, stderr=result.stderr.decode(errors="replace"))
            if result.returncode not in allowed:
                raise RuntimeError("COMMAND_FAILED:" + " ".join(args[:7]))
            return result
        except Exception as error:
            receipt["error"] = type(error).__name__ + ":" + str(error)
            raise
        finally:
            self.save("raw/%04d.json" % seq, receipt)

    def kube(self, *args):
        return self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", *args])

    def snapshot(self, label):
        result = json.loads(self.kube("get", "deploy,pod,pvc", "-A", "-o", "json").stdout)
        self.save(label + ".json", result)
        return result

    @staticmethod
    def specs(snapshot):
        return {x["kind"] + "/" + x["metadata"]["namespace"] + "/" + x["metadata"]["name"]:
                {"uid": x["metadata"]["uid"], "spec": x["spec"]} for x in snapshot["items"]
                if x["kind"] in {"Deployment", "PersistentVolumeClaim"}}

    @staticmethod
    def restarts(snapshot):
        return {x["metadata"]["uid"] + "/" + c["name"]: c["restartCount"] for x in snapshot["items"]
                if x["kind"] == "Pod" for c in x.get("status", {}).get("containerStatuses", [])}

    def resources(self):
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (x, ctypes.c_ulonglong) for x in ("totalPhys", "availPhys", "totalPage", "availPage",
                                                 "totalVirtual", "availVirtual", "availExtended")]
        mem = MemoryStatus()
        mem.length = ctypes.sizeof(mem)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
            raise RuntimeError("HOST_MEMORY_MISSING")
        raw = self.command(["docker", "--context", "desktop-linux", "exec", "k3d-zero-door-server-0", "cat",
                            "/proc/meminfo", "/proc/pressure/memory"], timeout=4).stdout.decode()
        avail = re.search(r"MemAvailable:\s+(\d+)", raw)
        psi = re.search(r"some avg10=([0-9.]+)", raw)
        if not avail or not psi:
            raise RuntimeError("VM_MEMORY_MISSING")
        row = {"at": time.time(), "hostAvailable": mem.availPhys,
               "wslAvailableKiB": int(avail[1]), "memoryPsiAvg10": float(psi[1])}
        with self.lock:
            self.samples.append(row)
            self.save("resource-samples.json", self.samples)
        if row["hostAvailable"] < 1073741824 or row["wslAvailableKiB"] < 1048576 or row["memoryPsiAvg10"] > 5:
            raise RuntimeError("MEMORY_STOP")

    def watch(self):
        due = time.monotonic() + 5
        while not self.stop.wait(max(0, due - time.monotonic())):
            try:
                self.resources()
            except Exception as error:
                self.failure.append(str(error))
                self.stop.set()
            due += 5

    def wait(self, until):
        while time.monotonic() < until:
            if self.stop.is_set() or time.monotonic() >= self.work_end:
                raise RuntimeError("GUARD_OR_WORK_BUDGET:" + str(self.failure))
            self.stop.wait(min(.2, until - time.monotonic()))

    def probe(self):
        if self.requests + self.flow.per_sample_requests > 32:
            raise RuntimeError("BOUTIQUE_REQUEST_BUDGET")
        if self.stop.is_set():
            raise RuntimeError("GUARD_STOP")
        result = self.flow.run(time.perf_counter_ns() + 8_000_000_000, self.stop, self.memory, step_s=3,
                               cleanup_ns=time.perf_counter_ns() + 10_000_000_000)
        self.requests += result["requests"]
        row = {"at": time.time(), "healthy": result["ok"] and result["elapsed_ms"] <= 2000, "result": result}
        self.save("business-%02d.json" % self.requests, row)
        if any(value != "DONE" for value in result["cleanup"].values()):
            raise RuntimeError("BUSINESS_CLEANUP_UNRESOLVED")
        return row

    def execute(self):
        if os.environ.get("DOCKER_HOST"):
            raise RuntimeError("DOCKER_HOST_FORBIDDEN")
        if self.command(["git", "rev-parse", "HEAD"]).stdout.decode().strip() != "9567830020954bf3f30fd5a74240747be0c8ec1c":
            raise RuntimeError("HEAD_DRIFT")
        pins = json.loads((ROOT / "docs/evidence/ZER-46/source-hashes.json").read_text())
        for path, expected in pins["source"].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise RuntimeError("SOURCE_DRIFT:" + path)
        self.save("started.json", {"at": self.started, "deadline_epoch": self.started + 1200,
                                  "work_deadline_epoch": self.started + 900, "maximum_seconds": 1200})
        if self.command(["docker", "context", "show"]).stdout.decode().strip() != "desktop-linux":
            raise RuntimeError("DOCKER_CONTEXT")
        nodes = json.loads(self.kube("get", "nodes", "-o", "json").stdout)
        self.save("nodes-before.json", nodes)
        if {n["metadata"]["name"] for n in nodes["items"]} != {"k3d-zero-door-server-0", "k3d-zero-door-agent-0"}:
            raise RuntimeError("NODE_PROFILE_DRIFT")
        if any(not any(c["type"] == "Ready" and c["status"] == "True" for c in n["status"]["conditions"]) for n in nodes["items"]):
            raise RuntimeError("NODE_NOT_READY")
        namespace = self.kube("get", "namespace", "zd-sqli-lab", "--ignore-not-found", "-o", "name").stdout.strip()
        if namespace:
            raise RuntimeError("NAMESPACE_ALREADY_EXISTS")
        self.before = self.snapshot("before")
        deployments = [x for x in self.before["items"] if x["kind"] == "Deployment"]
        target = [x for x in deployments if x["metadata"]["namespace"] == "target-app"]
        expected = {"cartservice", "checkoutservice", "currencyservice", "emailservice", "frontend", "paymentservice",
                    "productcatalogservice", "redis-cart", "shippingservice"}
        if {x["metadata"]["name"] for x in target} != expected:
            raise RuntimeError("TARGET_PROFILE_DRIFT")
        if any(x["spec"]["replicas"] != 1 or x.get("status", {}).get("availableReplicas", 0) != 1 for x in target):
            raise RuntimeError("TARGET_NOT_READY")
        if any(x["spec"]["replicas"] != 0 for x in deployments if x["metadata"]["namespace"] == "zero-door"):
            raise RuntimeError("SHARED_AGENT_ACTIVE")
        pvcs = [x for x in self.before["items"] if x["kind"] == "PersistentVolumeClaim"]
        if len(pvcs) != 3 or any(x.get("status", {}).get("phase") != "Bound" for x in pvcs):
            raise RuntimeError("PVC_PROFILE_DRIFT")
        self.kube("-n", "target-app", "get", "ingress", "frontend-ingress", "-o", "json")
        self.command(["docker", "--context", "desktop-linux", "exec", "k3d-zero-door-server-0", "cat", "/proc/1/cmdline"])
        print("PREFLIGHT_PRESSURE_120S", flush=True)
        start = time.monotonic()
        for i in range(25):
            self.wait(start + i * 5)
            self.resources()
        self.thread = threading.Thread(target=self.watch, daemon=True)
        self.thread.start()
        self.ensure_cache()
        self.check_business_baseline()
        after = self.snapshot("after-preflight")
        if self.specs(after) != self.specs(self.before) or self.restarts(after) != self.restarts(self.before):
            raise RuntimeError("PREFLIGHT_INVENTORY_DRIFT")
        self.save("preflight.json", {"status": "GATE_PASSED_NOT_ISSUE_PASS", "at": time.time(),
                                    "requests": self.requests, "resources": len(self.samples)})

    def check_business_baseline(self):
        print("BUSINESS_BASELINE_START", flush=True)
        start = time.monotonic()
        first = self.probe()
        if not first["healthy"]:
            raise RuntimeError("BUSINESS_WARMUP_FAILED")
        self.wait(start + 120)
        if not self.probe()["healthy"]:
            raise RuntimeError("BUSINESS_BASELINE_FAILED")

    def ensure_cache(self):
        for image in ("gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61",
                      "docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c"):
            self.command(["docker", "--context", "desktop-linux", "image", "inspect", image, "--format", "{{.Id}}"])

    def cleanup_failed_preflight(self):
        self.stop.set()
        if hasattr(self, "thread"):
            self.thread.join(timeout=15)
        result = {"at": time.time(), "namespace_created": False, "image_built": False, "mutations": 0,
                  "fixture_http": 0, "errors": [], "resource_cleanup": "CLEAN_NO_OWNED_LAB_RESOURCES_CREATED"}
        try:
            after = self.snapshot("after")
            result["specs_preserved"] = hasattr(self, "before") and self.specs(after) == self.specs(self.before)
            result["restarts_preserved"] = hasattr(self, "before") and self.restarts(after) == self.restarts(self.before)
            result["namespace_absent"] = not self.kube("get", "namespace", "zd-sqli-lab", "--ignore-not-found", "-o", "name").stdout.strip()
            self.resources()
            self.stop.clear()
            business = [self.probe(), self.probe()]
            result["business_2_of_2"] = all(x["healthy"] for x in business)
        except Exception as error:
            result["errors"].append(str(error))
        finally:
            self.stop.set()
        result["boutique_http"] = self.requests
        result["verdict"] = "CLEAN" if not result["errors"] and all(result.get(k) for k in
            ("specs_preserved", "restarts_preserved", "namespace_absent", "business_2_of_2")) else "INCOMPLETE"
        self.save("cleanup.json", result)
        return result


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-preflight", action="store_true")
    parser.add_argument("--attempt", choices=("runtime-01", "runtime-02"), default="runtime-01")
    args = parser.parse_args()
    if not args.execute_preflight:
        parser.error("explicit approved execution required")
    OUT = ROOT / "docs/evidence/ZER-46" / args.attempt
    if (OUT / "started.json").exists():
        parser.error("one attempt only; no replay of this run")
    lab = Lab()
    try:
        lab.execute()
    except Exception as error:
        lab.save("failure.json", {"at": time.time(), "reason": str(error), "stage": "PREFLIGHT", "attempt_ended": True})
        cleanup = lab.cleanup_failed_preflight()
        lab.save("acceptance.json", {"verdict": "NOT_MET", "stage": "PREFLIGHT", "runtime_component": "NOT_STARTED",
            "cleanup": cleanup["verdict"], "publication": "NOT_READY", "attempt_ended": True,
            "elapsed_seconds": time.time() - lab.started})
        print("PREFLIGHT_STOP", str(error), "CLEANUP", cleanup["verdict"], flush=True)
        return 1
    finally:
        lab.stop.set()
        if hasattr(lab, "thread"):
            lab.thread.join(timeout=15)
    print("PREFLIGHT_GATE_PASSED_SAME_WINDOW_REMAINS_OPEN", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
