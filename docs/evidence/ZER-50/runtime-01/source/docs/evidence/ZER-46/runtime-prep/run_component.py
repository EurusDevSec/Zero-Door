"""One explicitly approved runtime-03. No effect at import; only --execute starts the 20-minute window.
All app traffic is ordinary catalog/owned-order control traffic. No SQLi, load, Kafka or model call.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-03"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load("zer46_gate", Path(__file__).with_name("preflight.py"))
base.OUT = OUT
renderer = load("zer46_render", Path(__file__).with_name("render.py"))
process_observer = load("zer46_process", Path(__file__).with_name("writer_process.py"))

# Total160s +15s safety reserve, leaving5s initial evidence/action overhead.
# Unused early-phase time remains available; original expiry is never renewed.
TTL_PHASES = (("projection", 40), ("blocked_before", 35), ("writer_stop", 10),
              ("replacement", 30), ("blocked_after", 35), ("writer_replay", 10))
from measurement.flows import request as measured_request, Cancelled  # noqa: E402

BASE_IMAGE = "gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61"
PROXY_IMAGE = "docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c"
NS = "zd-sqli-lab"
CM = "zer46-sqli-containment"
ORIGIN = "http://zer46-private-ingress.zd-sqli-lab.svc.cluster.local:8000"
CLIENT = '''import sys,time
def stage(name):
 print('ZER46_STAGE '+name+' '+str(time.time()),file=sys.stderr,flush=True)
 for filename in ('memory.current','memory.max','memory.high','memory.events','memory.pressure','cpu.stat'):
  try:
   with open('/sys/fs/cgroup/'+filename) as f:value=f.read(4096)
   print('ZER46_COUNTER '+name+' '+filename+' '+repr(value),file=sys.stderr,flush=True)
  except OSError:print('ZER46_COUNTER '+name+' '+filename+' UNKNOWN',file=sys.stderr,flush=True)
stage('interpreter')
import json,urllib.request,urllib.error
stage('imports')
p=json.loads(sys.argv[1]);url="http://zer46-private-ingress.zd-sqli-lab.svc.cluster.local:8000"+p["path"]
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
data=json.dumps(p["body"]).encode() if p.get("body") is not None else None
headers={"X-Correlation-Id":p["correlation"],**p.get("headers",{})}
if data is not None:headers["Content-Type"]="application/json"
request=urllib.request.Request(url,data=data,headers=headers,method=p["method"])
begin=time.time()
stage('request_ready')
try:
 try:r=opener.open(request,timeout=3)
 except urllib.error.HTTPError as e:r=e
 with r:
  stage('headers')
  raw=r.read(262145)
  if len(raw)>262144:raise ValueError("RESPONSE_SIZE")
  stage("response_end")
  print(json.dumps({"begin":begin,"end":time.time(),"status":r.status,"request_id":r.headers.get("X-Request-Id"),"body":json.loads(raw)}))
except Exception as e:print(json.dumps({"begin":begin,"end":time.time(),"error":type(e).__name__}))
'''


def receipt_text(value):
    text = value.decode(errors="replace").replace("\x00", " ")
    return re.sub(r"(?i)(--(?:agent-)?token(?:=|\s+))\S+", r"\1[REDACTED]", text)


class Lab(base.Lab):
    node = "k3d-zero-door-server-0"

    def __init__(self):
        super().__init__()
        self.owner = "zer46-" + uuid.uuid4().hex[:12]
        self.run_id, self.trial_id = "run_" + uuid.uuid4().hex, "trl_" + uuid.uuid4().hex
        self.action = "act_" + uuid.uuid4().hex
        self.cleanup_mode, self.creation_attempted = False, False
        self.ns_uid, self.worker, self.worker_count = None, None, 0
        self.fixture_http, self.tcp_checks, self.last_http, self.pacing_idle = 0, 0, 0.0, 0.0
        self.validated, self.order_refs = False, []
        self.cm_uid, self.pins = None, None
        self.fixture_deployment_attempted = False
        self.phase_end = None; self.phase_name = None; self.phase_index = -1
        self.ttl_end = None; self.phase_receipts = []
        self.writer_handle = None; self.writer_identity = None; self.writer_instance = None
        self.writer_exits = []
        self.protocol_thread_id = threading.get_ident()

    def foreground(self):
        return threading.get_ident() == self.protocol_thread_id

    def check(self):
        if time.monotonic() >= self.deadline:
            raise RuntimeError("GLOBAL_BUDGET")
        if self.foreground() and not self.cleanup_mode and self.phase_end is not None and time.monotonic() >= self.phase_end:
            raise RuntimeError("TTL_PHASE_TIMEOUT:" + self.phase_name)
        if self.foreground() and getattr(self, 'log_read_end', None) is not None and time.monotonic() >= self.log_read_end:
            raise RuntimeError('LOG_READ_TIMEOUT')
        if not self.cleanup_mode and (self.stop.is_set() or time.monotonic() >= self.work_end):
            raise RuntimeError("GUARD_OR_CLEANUP_RESERVE:" + str(self.failure))

    def command(self, args, timeout=15, allowed=(0,)):
        self.check()
        with self.lock:
            self.seq += 1
            seq = self.seq
        receipt = {"at": time.time(), "args": args}
        try:
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                child = subprocess.Popen(args, stdout=stdout, stderr=stderr, env=self.env,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                receipt["pid"] = child.pid
                end = min(self.deadline, time.monotonic() + timeout,
                          self.phase_end if self.foreground() and self.phase_end is not None and not self.cleanup_mode else self.deadline,
                          (getattr(self, "log_read_end", None) or self.deadline) if self.foreground() else self.deadline)
                try:
                    while child.poll() is None:
                        self.check()
                        if time.monotonic() >= end:
                            raise RuntimeError("COMMAND_TIMEOUT")
                        time.sleep(.1)
                except Exception:
                    receipt["cancelled"] = True
                    try:
                        child.terminate()
                        try: child.wait(timeout=5)
                        except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=5)
                    finally:
                        # Partial bytes remain evidence, even when no response or exit is confirmed.
                        stdout.seek(0); stderr.seek(0)
                        receipt.update(returncode=child.poll(), stdout=receipt_text(stdout.read()),
                                       stderr=receipt_text(stderr.read()))
                    raise
                stdout.seek(0); stderr.seek(0)
                result = subprocess.CompletedProcess(args, child.returncode, stdout.read(), stderr.read())
            receipt.update(returncode=result.returncode, stdout=receipt_text(result.stdout),
                           stderr=receipt_text(result.stderr))
            self.check()
            if result.returncode not in allowed:
                raise RuntimeError("COMMAND_FAILED:" + " ".join(args[:7]))
            return result
        except Exception as error:
            receipt["error"] = str(error)
            raise
        finally:
            receipt["ended_at"] = time.time()
            self.save("raw/%04d.json" % seq, receipt)

    def begin_phase(self, name):
        """Reserve all successor phases before any destructive restart action."""
        self.check()
        index = next(i for i, phase in enumerate(TTL_PHASES) if phase[0] == name)
        if index != self.phase_index + 1: raise RuntimeError("TTL_PHASE_ORDER")
        now = time.monotonic()
        if index == 0:
            remaining = self.rule["expires_at"] - time.time()
            if self.rule["expires_at"] - self.rule["created_at"] != 180:
                raise RuntimeError("TTL_CHANGED")
            self.ttl_end = now + remaining
        future = sum(seconds for _, seconds in TTL_PHASES[index + 1:])
        end = min(now + TTL_PHASES[index][1], self.ttl_end - future - 15, self.work_end)
        if end <= now: raise RuntimeError("TTL_PHASE_NO_BUDGET:" + name)
        self.phase_index, self.phase_name, self.phase_end = index, name, end
        self.phase_receipts.append({"phase": name, "at": time.time(), "monotonic": now,
            "deadline_monotonic": end, "future_reserved_seconds": future, "expiry": self.rule["expires_at"]})
        self.save("ttl-phases.json", self.phase_receipts)
        self.check()

    def end_ttl_phases(self):
        self.check()
        if self.phase_index != len(TTL_PHASES) - 1: raise RuntimeError("TTL_PHASE_INCOMPLETE")
        self.save("ttl-phases-completed.json", {"at": time.time(), "expires_at": self.rule["expires_at"],
            "remaining_seconds": self.rule["expires_at"] - time.time(), "monotonic": time.monotonic()})
        self.phase_end = None; self.phase_name = None

    @staticmethod
    def shared(doc):
        return {"items": [x for x in doc["items"] if x["metadata"]["namespace"] != NS]}

    @staticmethod
    def private_restarts(doc):
        for pod in doc["items"]:
            if pod["kind"] == "Pod" and pod["metadata"]["namespace"] == NS:
                if any(c.get("restartCount", 0) for c in pod.get("status", {}).get("containerStatuses", [])):
                    raise RuntimeError("UNEXPECTED_PRIVATE_CONTAINER_RESTART")

    def watch(self):
        due, snapshot_due = time.monotonic() + 5, time.monotonic() + 15
        while not self.stop.wait(max(0, due - time.monotonic())):
            try:
                self.resources()
                if time.monotonic() >= snapshot_due:
                    observed = self.snapshot("watch-latest")
                    self.private_restarts(observed)
                    current = self.shared(observed)
                    if self.specs(current) != self.specs(self.before) or self.restarts(current) != self.restarts(self.before):
                        raise RuntimeError("SHARED_INVENTORY_DRIFT")
                    snapshot_due += 15
            except Exception as error:
                self.failure.append(str(error)); self.stop.set()
                self.capture_guard_stop()
            due += 5

    def capture_guard_stop(self):
        """Optional read-only diagnosis after stop. Must never clear the guard or start another workload."""
        return

    def pace(self, permit_cleanup=False):
        wait = max(0, self.last_http + .5 - time.monotonic())
        if wait:
            begin = time.monotonic()
            if self.cleanup_mode or permit_cleanup: time.sleep(wait)
            else: self.wait(time.monotonic() + wait)
            self.pacing_idle += time.monotonic() - begin
        if permit_cleanup:
            if time.monotonic() >= self.deadline: raise RuntimeError("GLOBAL_BUDGET")
        else: self.check()
        self.last_http = time.monotonic()

    def boutique_http(self, *args, **kwargs):
        if self.requests >= 32: raise Cancelled("BOUTIQUE_REQUEST_BUDGET")
        if not args[0].startswith("http://127.0.0.1:8080/"): raise Cancelled("BOUTIQUE_ORIGIN")
        owned_cleanup = args[0] == "http://127.0.0.1:8080/cart/empty" and args[1] == "POST"
        try: self.pace(permit_cleanup=owned_cleanup)
        except RuntimeError as error: raise Cancelled(str(error)) from error
        self.requests += 1
        try: return measured_request(*args, **kwargs)
        finally: self.last_http = time.monotonic()

    def probe(self):
        if self.requests + self.flow.per_sample_requests > 32:
            raise RuntimeError("BOUTIQUE_REQUEST_BUDGET")
        idle = self.pacing_idle
        result = self.flow.run(time.perf_counter_ns() + 8_000_000_000,
            threading.Event() if self.cleanup_mode else self.stop, self.memory, step_s=3, http=self.boutique_http,
            cleanup_ns=time.perf_counter_ns() + 10_000_000_000)
        pacing_ms = (self.pacing_idle - idle) * 1000
        active_ms = max(0, result["elapsed_ms"] - pacing_ms) if result["ok"] else None
        row = {"at": time.time(), "healthy": result["ok"] and active_ms <= 2000,
            "health_kind": "COMPONENT_FUNCTION_AND_ACTIVE_TIME_ONLY_NOT_FORMAL_R1_HEALTH",
            "wall_reference_slo_met": result["ok"] and result["elapsed_ms"] <= 2000,
            "scheduler_idle_ms": pacing_ms, "active_ms": active_ms, "result": result}
        self.save("business-%02d.json" % self.requests, row)
        if any(x != "DONE" for x in result["cleanup"].values()):
            raise RuntimeError("BUSINESS_CLEANUP_UNRESOLVED")
        return row

    def ensure_cache(self):
        for image in (BASE_IMAGE, PROXY_IMAGE):
            found = self.command(["docker", "--context", "desktop-linux", "image", "inspect", image,
                                  "--format", "{{.Id}}"], allowed=(0, 1))
            if found.returncode:
                if b"No such image" not in found.stderr:
                    raise RuntimeError("CACHE_INSPECT_UNAVAILABLE")
                print("PULL_EXACT_PIN", image.split("@")[0], flush=True)
                self.command(["docker", "--context", "desktop-linux", "pull", "--platform", "linux/amd64", image], timeout=120)
            self.command(["docker", "--context", "desktop-linux", "image", "inspect", image,
                          "--format", "{{json .RepoDigests}}"])

    def write_yaml(self, name, docs):
        path = OUT / name
        path.write_text(yaml.safe_dump_all(docs, sort_keys=False), encoding="utf8")
        return str(path)

    def pod(self, name=None):
        doc = json.loads(self.kube("-n", NS, "get", "pods", "-o", "json").stdout)
        self.save("pods-latest.json", doc)
        matches = [p for p in doc["items"] if p["metadata"]["name"] == name] if name else [
            p for p in doc["items"] if p["metadata"]["labels"].get("app") == "sqli-fixture" and not p["metadata"].get("deletionTimestamp")]
        if len(matches) != 1:
            raise RuntimeError("POD_IDENTITY")
        return matches[0]

    def policy_installed(self, pod):
        name = pod["metadata"]["name"]
        result = self.command(["docker", "--context", "desktop-linux", "exec", self.node, "sh", "-c",
            "iptables-save | grep -F 'POD name:" + name + " namespace: zd-sqli-lab'"], allowed=(0, 1))
        return result.returncode == 0 and b"KUBE-POD-FW" in result.stdout

    def release(self):
        end = min(time.monotonic() + 115, self.work_end, self.phase_end or self.work_end)
        while time.monotonic() < end:
            try: p = self.pod()
            except RuntimeError as error:
                if str(error) != "POD_IDENTITY": raise
                self.wait(time.monotonic() + 2); continue
            name = p["metadata"]["name"]
            if not p["spec"].get("nodeName"):
                self.wait(time.monotonic() + 2); continue
            if not re.fullmatch(r"sqli-fixture-[a-z0-9-]+", name) or p["spec"]["nodeName"] != self.node:
                raise RuntimeError("FIXTURE_POD_PIN")
            if any(c.get("restartCount", 0) for c in p.get("status", {}).get("containerStatuses", [])):
                raise RuntimeError("UNEXPECTED_FIXTURE_CONTAINER_RESTART")
            if not any("running" in c.get("state", {}) for c in p.get("status", {}).get("containerStatuses", [])):
                self.wait(time.monotonic() + 2); continue
            if self.policy_installed(p):
                self.kube("-n", NS, "exec", name, "--", "/usr/bin/python3", "-c",
                          "from pathlib import Path; Path('/data/.policy-release').write_text('observed-policy-rule')")
                self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", "-n", NS,
                              "wait", "--for=condition=Ready", "pod/" + name, "--timeout=30s"], timeout=35)
                return self.pod()
            self.wait(time.monotonic() + 3)
        raise RuntimeError("POLICY_GATE_NOT_ENFORCED")

    def logs(self, pod=None):
        pod = pod or self.pod()
        name, uid = pod["metadata"]["name"], pod["metadata"]["uid"]
        current = json.loads(self.kube("-n", NS, "get", "pod", name, "-o", "json").stdout)
        if (current["metadata"]["uid"] != uid or current["metadata"].get("deletionTimestamp") or
                current["metadata"].get("labels", {}).get("zero-door.io/run") != self.owner or
                current["spec"].get("nodeName") != self.node):
            raise RuntimeError("LOG_POD_IDENTITY")
        self.save("log-pod-target-%03d.json" % self.fixture_http,
                  {"name": name, "uid": uid, "node": self.node})
        raw = self.kube("-n", NS, "logs", "pod/" + name, "-c", "sqli-fixture", "--tail=500").stdout.decode()
        records = []
        for line in raw.splitlines():
            try: record = json.loads(line)
            except ValueError: continue
            if "request_id" in record: records.append(record)
        return records

    def join_access(self, target_pod, request_id):
        if not request_id: raise RuntimeError("ACCESS_REQUEST_ID_MISSING")
        end = min(time.monotonic() + 6, self.work_end if not self.cleanup_mode else self.deadline)
        self.log_read_end = end
        try:
            # Only log reads, never replay HTTP. All kubectl reads share this deadline.
            for attempt in range(3):
                self.check()
                joined = [r for r in self.logs(target_pod) if r["request_id"] == request_id]
                if len(joined) > 1: raise RuntimeError("ACCESS_JOIN_DUPLICATE")
                if len(joined) == 1: return joined[0]
                if attempt == 2 or time.monotonic() + .5 >= end: break
                if self.cleanup_mode: time.sleep(.5)
                else: self.wait(time.monotonic() + .5)
            raise RuntimeError("ACCESS_JOIN")
        finally:
            self.log_read_end = None

    def http(self, who, path="/fixture/catalog/search?category=electronics", method="GET", body=None, headers=None):
        if self.fixture_http >= 120 or who not in {"a", "b"} or not path.startswith("/fixture/") or "://" in path:
            raise RuntimeError("HTTP_BOUNDARY")
        self.pace(); self.fixture_http += 1
        target_pod = self.pod()
        payload = {"path": path, "method": method, "body": body, "headers": headers or {}, "correlation": uuid.uuid4().hex}
        try:
            result = json.loads(self.kube("-n", NS, "exec", "zer46-source-" + who, "--", "/usr/bin/python3", "-c",
                                        CLIENT, json.dumps(payload)).stdout)
        finally: self.last_http = time.monotonic()
        self.save("http-%03d.json" % self.fixture_http, {"who": who, "request": payload, "response": result})
        if "error" in result: raise RuntimeError("FIXTURE_HTTP:" + result["error"])
        record = self.join_access(target_pod, result.get("request_id"))
        if (record["client_ip"] != self.addresses[who] or record["tcp_peer"] != self.addresses["proxy"] or
                record["source_method"] != "XFF_AFTER_TRUSTED" or record["source_confidence"] != "PROXY_CHAIN" or
                record["status"] != result["status"] or record["correlation_id"] != payload["correlation"]):
            raise RuntimeError("SOURCE_OR_TRACE_MISMATCH")
        self.save("join-%03d.json" % self.fixture_http, record)
        return result, record

    def expect(self, who, status, **kwargs):
        response, record = self.http(who, **kwargs)
        if response["status"] != status: raise RuntimeError("UNEXPECTED_HTTP_STATUS")
        if status == 403 and response["body"].get("error") != "SOURCE_BLOCKED":
            raise RuntimeError("BLOCK_REASON")
        if status == 403 and (record.get("action_ids") != [self.action] or record.get("blocked") is not True):
            raise RuntimeError("BLOCK_ACTION_JOIN")
        if status == 200 and "catalog/search" in kwargs.get("path", "/fixture/catalog/search"):
            if response["body"].get("count") != 1 or [r["sku"] for r in response["body"].get("results", [])] != ["PUB-ELE-001"]:
                raise RuntimeError("BENIGN_CATALOG_ORACLE")
        return response, record

    def crud(self):
        nonce = uuid.uuid4().hex
        response, _ = self.expect("b", 201, path="/fixture/orders", method="POST", body={"item": "benign-lab-item", "note": nonce})
        ref = response["body"]["order_ref"]
        if not re.fullmatch("[a-f0-9]{32}", ref): raise RuntimeError("ORDER_REF")
        self.order_refs.append(ref)
        read, _ = self.expect("b", 200, path="/fixture/orders/" + ref)
        if read["body"].get("note") != nonce: raise RuntimeError("ORDER_OWNERSHIP")
        self.expect("b", 200, path="/fixture/orders/" + ref, method="DELETE")
        self.expect("b", 404, path="/fixture/orders/" + ref)
        self.order_refs.remove(ref)

    def isolation(self, fixture):
        for who in ("a", "b"):
            if self.tcp_checks >= 6: raise RuntimeError("TCP_BUDGET")
            self.tcp_checks += 1
            code = "import socket,json\ns=socket.socket(); s.settimeout(2)\ntry:\n s.connect(("
            code += repr(fixture["status"]["podIP"]) + ",9140)); denied=False\nexcept OSError:\n denied=True\n"
            code += "print(json.dumps({'denied':denied})); s.close()\n"
            result = json.loads(self.kube("-n", NS, "exec", "zer46-source-" + who, "--", "/usr/bin/python3", "-c", code).stdout)
            if result != {"denied": True}: raise RuntimeError("DIRECT_ACCESS_NOT_DENIED")

    def cm(self):
        doc = json.loads(self.kube("-n", NS, "get", "cm", CM, "-o", "json").stdout)
        if (doc["metadata"]["labels"].get("zero-door.io/containment-scope") != self.owner or
                (self.cm_uid and doc["metadata"]["uid"] != self.cm_uid)):
            raise RuntimeError("CM_OWNER_DRIFT")
        return doc

    def mounted(self):
        p = self.pod()
        code = "import json,hashlib; r=open('/containment/policy.json','rb').read(32769); print(json.dumps({'sha256':hashlib.sha256(r).hexdigest(),'policy':json.loads(r)}))"
        return json.loads(self.kube("-n", NS, "exec", p["metadata"]["name"], "--", "/usr/bin/python3", "-c", code).stdout)

    def wait_projection(self, expected, seconds=90):
        digest = hashlib.sha256(expected["data"]["policy.json"].encode()).hexdigest()
        end = min(time.monotonic() + seconds, self.deadline - 160 if self.cleanup_mode else self.work_end)
        while time.monotonic() < end:
            mounted = self.mounted()
            if mounted["sha256"] == digest: return mounted
            if self.cleanup_mode: time.sleep(2)
            else: self.wait(time.monotonic() + 2)
        raise RuntimeError("POLICY_PROJECTION_TIMEOUT")

    def start_worker(self):
        if self.worker_count >= 2: raise RuntimeError("WRITER_RESTART_BUDGET")
        self.worker_count += 1
        stderr = (OUT / ("writer-%d.stderr.log" % self.worker_count)).open("wb")
        self.writer_started_at = time.time()
        self.writer_instance = uuid.uuid4().hex
        self.writer_identity = None; self.writer_handle = None
        worker_env = dict(self.env, ZER46_WRITER_INSTANCE=self.writer_instance)
        self.worker = subprocess.Popen([sys.executable, "-B", str(Path(__file__).with_name("writer_worker.py")),
            "--pins", str(OUT / "writer-pins.json")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
            text=True, env=worker_env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.worker_stderr = stderr
        self.replies = queue.Queue()
        child, replies = self.worker, self.replies
        def read():
            for line in child.stdout: replies.put(line)
            replies.put(None)
        threading.Thread(target=read, daemon=True).start()
        self.save("writer-%d.json" % self.worker_count, {"pid": self.worker.pid, "at": self.writer_started_at})
        if self.rpc("hello") != {"identity_only": True}: raise RuntimeError("WRITER_HELLO")

    def rpc(self, op):
        self.check()
        self.worker.stdin.write(json.dumps({"op": op}) + "\n"); self.worker.stdin.flush()
        end = min(self.deadline, time.monotonic() + 40)
        while time.monotonic() < end:
            self.check()
            try: line = self.replies.get(timeout=.2)
            except queue.Empty: continue
            if line is None: raise RuntimeError("WRITER_EOF")
            result = json.loads(line)
            self.save("writer-%d-%s.json" % (self.worker_count, op), result)
            if (result.get("op") != op or result.get("instance") != self.writer_instance or
                    type(result.get("pid")) is not int or result["pid"] <= 0):
                raise RuntimeError("WRITER_RPC_ASSOCIATION")
            if self.writer_identity is None:
                if op != "hello": raise RuntimeError("WRITER_IDENTITY_MISSING")
                if result.get('executable') != sys.executable:
                    raise RuntimeError('WRITER_LOGICAL_EXECUTABLE_PIN')
                self.writer_handle = process_observer.WriterProcess(result["pid"], result["kernel_executable"], self.writer_started_at)
                self.writer_identity = dict(self.writer_handle.identity, instance=self.writer_instance,
                                            rpc_executable=result['executable'])
                self.save("writer-%d-identity.json" % self.worker_count, self.writer_identity)
            elif (result['pid'] != self.writer_identity['pid'] or
                    result.get('executable') != self.writer_identity['rpc_executable'] or
                    result.get('kernel_executable') != self.writer_identity['executable']):
                raise RuntimeError('WRITER_IDENTITY_DRIFT')
            if not result["ok"]: raise RuntimeError("WRITER_REFUSED:" + result.get("reason", ""))
            return result["result"]
        raise RuntimeError("WRITER_RPC_TIMEOUT")

    def stop_worker(self):
        if self.worker is None: return
        child = self.worker
        receipt = {"at": time.time(), "launcher_pid": child.pid, "writer": self.writer_identity,
                   "rpc_exit": "UNKNOWN", "launcher_exit": None}
        error = None
        try:
            try:
                child.stdin.close(); child.wait(timeout=2)
            except Exception:
                child.terminate()
                try: child.wait(timeout=2)
                except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=2)
            receipt["launcher_exit"] = child.poll()
            if self.writer_handle is None: raise RuntimeError("WRITER_IDENTITY_MISSING")
            remaining = min(3, max(0, self.deadline - time.monotonic()))
            if not self.cleanup_mode and self.phase_end is not None:
                remaining = min(remaining, max(0, self.phase_end - time.monotonic()))
            receipt["rpc_exit"] = self.writer_handle.wait_exit(remaining)
            if receipt["rpc_exit"] != "EXITED" or receipt["launcher_exit"] is None:
                raise RuntimeError("WRITER_EXIT_UNCONFIRMED")
        except Exception as failure:
            error = failure; receipt["error"] = str(failure)
        finally:
            receipt["ended_at"] = time.time()
            self.save("writer-%d-exit.json" % self.worker_count, receipt)
            self.writer_exits.append(receipt)
            if self.writer_handle is not None: self.writer_handle.close()
            self.writer_handle = None
            for stream in (child.stdin, child.stdout, self.worker_stderr):
                try: stream.close()
                except Exception: pass
            self.worker = None
        if error: raise error

    def component(self):
        pins = json.loads((ROOT / "docs/evidence/ZER-46/source-hashes.json").read_text(encoding="utf8"))
        tag = pins["fixtureCandidateTag"]
        self.prepare_fixture_image(tag)
        docs = renderer.render(self.owner, self.run_id, self.trial_id, "10.42.255.254", node=self.node)
        namespace = next(d for d in docs if d["kind"] == "Namespace")
        self.save("namespace-create.json", namespace)
        if self.kube("get", "namespace", NS, "--ignore-not-found", "-o", "name").stdout.strip():
            raise RuntimeError("NAMESPACE_ALREADY_EXISTS")
        self.creation_attempted = True
        created = json.loads(self.kube("create", "-f", str(OUT / "namespace-create.json"), "-o", "json").stdout)
        self.ns_uid = created["metadata"]["uid"]; self.save("namespace-created.json", created)
        bootstrap = [d for d in docs if d["kind"] != "Namespace" and not
            (d["metadata"]["name"] in {"sqli-fixture", "sqli-fixture-config"} and d["kind"] in {"Deployment", "ConfigMap"})]
        self.apply_bootstrap(bootstrap)
        self.run_fixture_protocol()

    def prepare_fixture_image(self, tag):
        print("BUILD_ONE_PINNED_FIXTURE", flush=True)
        self.command(["docker", "--context", "desktop-linux", "build", "--platform=linux/amd64", "--network=none", "--pull=false",
            "-t", tag, "-f", str(ROOT / "services/sqli-fixture/Dockerfile"), str(ROOT / "services/sqli-fixture")], timeout=120)
        self.command(["k3d", "image", "import", tag, "-c", "zero-door", "--mode=direct"], timeout=90)
    def apply_bootstrap(self, bootstrap):
        # Keep the full render for review, but admit only one workload startup at a time.
        self.write_yaml("bootstrap.yaml", bootstrap)
        static = [d for d in bootstrap if d["kind"] not in {"Deployment", "Pod"}]
        path = self.write_yaml("bootstrap-static.yaml", static)
        self.kube("apply", "-f", path)
        proxy = [d for d in bootstrap if d["kind"] == "Deployment"]
        if len(proxy) != 1 or proxy[0]["metadata"]["name"] != "zer46-private-ingress":
            raise RuntimeError("BOOTSTRAP_DEPLOYMENT_BOUNDARY")
        self.kube("apply", "-f", self.write_yaml("bootstrap-proxy.yaml", proxy))
        self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", "-n", NS,
            "rollout", "status", "deployment/zer46-private-ingress", "--timeout=90s"], timeout=95)
        sources = [d for d in bootstrap if d["kind"] == "Pod"]
        if {d["metadata"]["name"] for d in sources} != {"zer46-source-a", "zer46-source-b"}:
            raise RuntimeError("BOOTSTRAP_SOURCE_BOUNDARY")
        for d in sorted(sources, key=lambda x: x["metadata"]["name"]):
            name = d["metadata"]["name"]
            self.kube("apply", "-f", self.write_yaml(name + ".yaml", [d]))
            self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", "-n", NS,
                "wait", "--for=condition=Ready", "pod/" + name, "--timeout=60s"], timeout=65)

    def wait_old_pod_absent(self, name, uid):
        end = min(time.monotonic() + 45, self.work_end, self.phase_end or self.work_end)
        while time.monotonic() < end:
            raw = self.kube("-n", NS, "get", "pod", name, "--ignore-not-found", "-o", "json").stdout
            if not raw.strip(): return
            if json.loads(raw)["metadata"]["uid"] != uid:
                raise RuntimeError("DELETED_POD_UID_DRIFT")
            self.wait(time.monotonic() + 1)
        raise RuntimeError("OLD_POD_DELETE_TIMEOUT")

    def run_fixture_protocol(self):
        self.addresses = {who: self.pod("zer46-source-" + who)["status"]["podIP"] for who in ("a", "b")}
        allpods = json.loads(self.kube("-n", NS, "get", "pods", "-o", "json").stdout)
        proxy = [p for p in allpods["items"] if p["metadata"]["labels"].get("app") == "zer46-private-ingress"]
        if len(proxy) != 1: raise RuntimeError("PROXY_IDENTITY")
        self.addresses["proxy"] = proxy[0]["status"]["podIP"]
        if len(set(self.addresses.values())) != 3: raise RuntimeError("SOURCE_SEPARATION")
        self.save("source-addresses.json", self.addresses)
        final = renderer.render(self.owner, self.run_id, self.trial_id, self.addresses["proxy"], node=self.node)
        self.fixture_deployment_attempted = True
        self.kube("apply", "-f", self.write_yaml("fixture.yaml", [d for d in final if
            (d["kind"], d["metadata"]["name"]) in {("Deployment", "sqli-fixture"), ("ConfigMap", "sqli-fixture-config")}]))
        fixture = self.release(); self.save("fixture-initial.json", fixture)
        self.command(["docker", "--context", "desktop-linux", "top", self.node, "-eo", "pid,args"])
        self.expect("a", 200); self.expect("b", 200); self.crud()
        self.isolation(fixture)
        self.expect("a", 200, headers={"X-Forwarded-For": "203.0.113.77"})
        _, observed = self.expect("a", 200)
        cm = self.cm(); self.cm_uid = cm["metadata"]["uid"]
        self.pins = {"target": {"uid": self.cm_uid, "scope": self.owner, "run_id": self.run_id, "trial_id": self.trial_id,
            "attacker_ip": self.addresses["a"], "benign_ip": self.addresses["b"], "proxy_cidrs": [self.addresses["proxy"] + "/32"]},
            "action_id": self.action, "evidence": dict(observed, run_id=self.run_id, trial_id=self.trial_id)}
        self.save("writer-pins.json", self.pins)
        self.start_worker(); result = self.rpc("block")
        if result["replay"] or result["containment_verified"]: raise RuntimeError("ACTION_RESULT")
        self.rule = result["rule"]; self.save("original-rule.json", self.rule)
        self.begin_phase("projection")
        cm = self.cm(); self.save("policy-applied.json", cm); self.wait_projection(cm)
        self.begin_phase("blocked_before")
        self.expect("a", 403); self.expect("b", 200); self.crud()
        self.expect("a", 403, path="/fixture/orders", method="POST", body={"item": "benign-lab-item", "note": "blocked-control"})
        self.begin_phase("writer_stop"); self.stop_worker()
        self.begin_phase("replacement")
        old_uid, old_name = fixture["metadata"]["uid"], fixture["metadata"]["name"]
        self.save("pod-delete-options.json", {"apiVersion": "v1", "kind": "DeleteOptions", "preconditions": {"uid": old_uid}})
        self.kube("delete", "--raw", "/api/v1/namespaces/" + NS + "/pods/" + old_name, "-f", str(OUT / "pod-delete-options.json"))
        fixture = self.release(); self.save("fixture-after-replacement.json", fixture)
        if fixture["metadata"]["uid"] == old_uid: raise RuntimeError("POD_NOT_REPLACED")
        self.begin_phase("blocked_after")
        self.expect("a", 403); self.expect("b", 200); self.crud(); self.isolation(fixture)
        self.begin_phase("writer_replay")
        before_replay = self.cm(); self.start_worker(); replay = self.rpc("block"); after_replay = self.cm()
        if (not replay["replay"] or replay["rule"] != self.rule or before_replay != after_replay):
            raise RuntimeError("REPLAY_CHANGED_STATE")
        self.save("replay-readback.json", {"before": before_replay, "after": after_replay})
        self.end_ttl_phases()
        # New-Pod access joins prove restart behavior. Observe old-Pod absence during TTL idle,
        # rather than spending the bounded active block window waiting for its termination.
        self.wait_old_pod_absent(old_name, old_uid)
        self.save("old-pod-absent.json", {"at": time.time(), "name": old_name, "uid": old_uid, "absent": True})
        print("WAIT_ORIGINAL_TTL", self.rule["expires_at"], flush=True)
        while time.time() < self.rule["expires_at"] + .5:
            self.wait(time.monotonic() + .25)
        self.expect("a", 200); self.expect("b", 200); self.crud()
        stored = json.loads(self.cm()["data"]["policy.json"])["rules"]
        if stored != [self.rule]: raise RuntimeError("EXPIRY_RULE_WAS_REMOVED_OR_CHANGED")
        self.validated = True
        self.save("component-observed.json", {"at": time.time(), "status": "OBSERVED_PENDING_INDEPENDENT_RECONCILIATION",
            "rule": self.rule, "fixture_http": self.fixture_http, "tcp_checks": self.tcp_checks})

    def cleanup(self):
        self.cleanup_mode = True; self.stop.set()
        if hasattr(self, "thread"): self.thread.join(timeout=10)
        report = {"at": time.time(), "errors": [], "namespace_created": self.creation_attempted}
        if hasattr(self, "thread") and self.thread.is_alive():
            report["errors"].append("GUARD_THREAD_NOT_STOPPED")
        try:
            if self.creation_attempted:
                doc = json.loads(self.kube("get", "namespace", NS, "-o", "json").stdout)
                if doc["metadata"]["labels"].get("zero-door.io/run") != self.owner or (self.ns_uid and doc["metadata"]["uid"] != self.ns_uid):
                    raise RuntimeError("CLEANUP_NAMESPACE_OWNER")
                self.ns_uid = doc["metadata"]["uid"]
                try:
                    if self.worker is not None:
                        self.rpc("cleanup")
                        cm = self.cm(); self.save("policy-cleanup-api.json", cm)
                        if json.loads(cm["data"]["policy.json"])["rules"]: raise RuntimeError("RULE_REMAINS")
                        self.resources(); self.wait_projection(cm, seconds=45)
                        self.expect("a", 200); self.expect("b", 200)
                        report["policy_cleanup_observed"] = True
                    if self.fixture_deployment_attempted:
                        self.logs()
                    else:
                        report["fixture_log"] = "NOT_APPLICABLE_DEPLOYMENT_NOT_ATTEMPTED"
                    self.kube("-n", NS, "logs", "deployment/zer46-private-ingress", "--tail=500")
                except Exception as error: report["errors"].append("POLICY_OR_LOG_READBACK:" + str(error))
                try: self.stop_worker()
                except Exception as error: report["errors"].append("WRITER_STOP:" + str(error))
                self.save("namespace-delete-options.json", {"apiVersion": "v1", "kind": "DeleteOptions", "preconditions": {"uid": self.ns_uid}})
                self.kube("delete", "--raw", "/api/v1/namespaces/" + NS, "-f", str(OUT / "namespace-delete-options.json"))
                self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", "wait", "--for=delete",
                              "namespace/" + NS, "--timeout=150s"], timeout=155)
            report["namespace_absent"] = not self.kube("get", "namespace", NS, "--ignore-not-found", "-o", "name").stdout.strip()
        except Exception as error: report["errors"].append("NAMESPACE_CLEANUP:" + str(error))
        finally:
            try: self.stop_worker()
            except Exception as error: report["errors"].append("WRITER_STOP_FINAL:" + str(error))
        try:
            after = self.shared(self.snapshot("after"))
            report["specs_preserved"] = hasattr(self, "before") and self.specs(after) == self.specs(self.before)
            report["restarts_preserved"] = hasattr(self, "before") and self.restarts(after) == self.restarts(self.before)
            self.resources()
            probes = [self.probe(), self.probe()]
            report["business_2_of_2"] = all(p["healthy"] for p in probes)
            report["formal_r1_health_claim"] = False
        except Exception as error: report["errors"].append("SHARED_READBACK:" + str(error))
        if self.worker_count and (len(self.writer_exits) != self.worker_count or
                any(x["rpc_exit"] != "EXITED" or x["launcher_exit"] is None or x.get("error") for x in self.writer_exits)):
            report["errors"].append("WRITER_EXIT_UNCONFIRMED")
        report["writer_exit_proofs"] = self.writer_exits
        report["guard_failures"] = list(self.failure)
        if self.failure: report["errors"].append("GUARD_FAILURE_HISTORY")
        report.update(fixture_http=self.fixture_http, boutique_http=self.requests, tcp_checks=self.tcp_checks, writer_processes=self.worker_count)
        report["verdict"] = "CLEAN" if not report["errors"] and all(report.get(k) for k in
            ("namespace_absent", "specs_preserved", "restarts_preserved", "business_2_of_2")) else "INCOMPLETE"
        self.save("cleanup.json", report); print("CLEANUP", report["verdict"], flush=True)
        return report


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    if not args.execute: parser.error("explicit approved --execute required")
    if (OUT / "started.json").exists(): parser.error("one attempt only, no automatic replay")
    authorization = json.loads((ROOT / "docs/evidence/ZER-46/runtime-prep/readiness-authorization.json").read_text(encoding="utf8"))
    proposal = ROOT / authorization["proposal"]
    if hashlib.sha256(proposal.read_bytes()).hexdigest() != authorization["proposalSha256"]:
        parser.error("authorization proposal drift")
    lab = Lab(); lab.save("authorization.json", dict(authorization, readiness_reply="tôi giải phóng ram rồi"))
    error = None
    try:
        lab.execute(); lab.component()
    except Exception as failure:
        error = str(failure); lab.save("failure.json", {"at": time.time(), "reason": error})
        print("STOP", error, flush=True)
    finally:
        cleanup = lab.cleanup()
    if lab.failure:
        error = error or "GUARD_FAILURE:" + repr(lab.failure)
        lab.save("failure.json", {"at": time.time(), "reason": error, "guard_failures": list(lab.failure)})
    lab.save("acceptance.json", {"component_observed": lab.validated and not error, "error": error, "cleanup": cleanup["verdict"],
        "status": "RECONCILE_REQUIRED" if lab.validated and not error and cleanup["verdict"] == "CLEAN" else "NOT_MET",
        "issue_done": False, "elapsed_seconds": time.time() - lab.started})
    return 0 if lab.validated and not error and cleanup["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(main())
