"""Explicit ZER-21 native cycle, reusing the reviewed private-fixture supervisor.

Import is inert. No work without fresh exact owner approval and the parent stdin gate.
"""
import asyncio
from copy import deepcopy
from datetime import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import uuid

import run as supervisor

ROOT, PREP, OUT = supervisor.ROOT, supervisor.PREP, supervisor.OUT
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id
from event_pipeline.llm import Adapter, HttpxTransport, Limits, RunBudget
from gaia.diagnosis import Diagnoser
from hephaestus.recovery import Healer, Journal
from nemesis.command_guard import CommandGuard
from nemesis.session import PURPOSE, Session, SessionLimits
from cycle import FunctionalCycle

spec = importlib.util.spec_from_file_location("zer21_fixture_lab", ROOT / "docs/evidence/ZER-50/runtime-prep/lab.py")
fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
# The legacy module uses the current supervisor's paths/pins. Historical files remain untouched.
fixture.ROOT, fixture.PREP, fixture.OUT = ROOT, PREP, OUT
fixture_factory = fixture.make_lab
kube_config_pin = fixture.kube_config_pin
claim_work = fixture.claim_work
# Warm-up gate: 3x the largest of 285 measured benign execs (100 ms); 500m runs one in ~0.3 s.
# Evidence: docs/evidence/ZER-21/runtime-03-investigation/exec-cpu-diagnostic/README.md
SOURCE_GATE_CPU_USEC, SOURCE_GATE_WALL_S = 300_000, 5


def worker_build_provenance(root=ROOT):
    """Prove the specific cached artifact and its three recorded source pins.

    The historical receipt did not hash the complete Go build context. Do not
    promote these three pins to complete current-source reproducibility.
    """
    base = root / "docs/evidence/ZER-42/runtime-01/zer42-d042c1ab05f1"
    built = json.loads((base / "source-manifest.json").read_bytes())
    paths = ("chaos-worker/internal/attack/sqli.go", "chaos-worker/internal/validation/target.go",
             "chaos-worker/cmd/main.go")
    for relative in paths:
        if supervisor.sha(root / relative) != built[relative]:
            raise ValueError("CACHED_WORKER_SOURCE_DRIFT")
    pins = json.loads((root / "docs/evidence/ZER-19/runtime-prep/cache-pins.json").read_bytes())
    pin = next(p for p in pins if p["name"] == "zer42-worker")
    build = json.loads((base / "raw/006-build-worker.json").read_bytes())
    image = json.loads((base / "raw/008-image-worker.json").read_bytes())
    if (build["args"] != ["docker","build","--tag",pin["tag"],"chaos-worker"]
            or build["returncode"] != 0 or image["returncode"] != 0
            or image["stdout"].strip() != pin["host_id"]
            or "exporting manifest list " + pin["host_id"] not in build["stderr"]
            or "exporting config " + pin["node_id"] not in build["stderr"]):
        raise ValueError("WORKER_BUILD_PROVENANCE_MISMATCH")
    return {"source_paths":list(paths), "historical_build":str(base.relative_to(root)),
        "full_build_context_attested":False, "artifact_pin":pin}


def project_worker(context, receipt, raw, *, fixture_uid, pod_uid, source_ip, proxy_ip,
                   begin, end, at, ref):
    """Join received worker counts to raw fixture log; never fabricate an HTTP body."""
    commands = [r["command"] for r in receipt["records"] if r["event"] == "DISPATCH_INTENT"]
    results = [r["raw"] for r in receipt["records"] if r["event"] == "EXECUTOR_RESULT"]
    if len(commands) != 1 or len(results) != 1:
        raise ValueError("NATIVE_WORKER_CARDINALITY")
    command, result = commands[0], results[0]
    sends = result["details"]["sqli"]["sends"]
    if (command["context"] != {k:context[k] for k in ("run_id","trial_id","group")} or result["commandId"] != command["commandId"]
            or result["status"] != "SUCCESS" or len(sends) != 1):
        raise ValueError("NATIVE_WORKER_CONTEXT")
    send = sends[0]
    stamps = [datetime.fromisoformat(send[k].replace("Z", "+00:00")) for k in ("startedAt","observedAt")]
    if any(t.tzinfo is None for t in stamps):
        raise ValueError("WORKER_TIMESTAMP_TIMEZONE_REQUIRED")
    started, observed = (t.timestamp() for t in stamps)
    # Go isoAt truncates to milliseconds (sqli.go), so a canonical .dddZ
    # observedAt represents [observed, observed+1ms), not an exact upper instant.
    # This accounts only for representation loss, never cross-host clock skew.
    observed_resolution = 0.001 if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", send["observedAt"]) else 0
    before_observed_end = (raw["ts"] < observed + observed_resolution if observed_resolution
                           else raw["ts"] <= observed)
    if (pod_uid != fixture_uid or not re.fullmatch(r"[a-f0-9]{32}", send.get("responseId") or "")
            or send["responseId"] != raw.get("request_id")
            or send.get("requestId") != command["commandId"] + "/1"
            or raw.get("correlation_id") != send["requestId"] or send.get("seq") != 1
            or raw.get("method") != "GET" or raw.get("path") != "/fixture/catalog/search"
            or raw.get("client_ip") != source_ip or raw.get("tcp_peer") != proxy_ip
            or raw.get("source_method") != "XFF_AFTER_TRUSTED" or raw.get("source_confidence") != "PROXY_CHAIN"
            or send.get("status") != 200 or raw.get("status") != 200 or send.get("error")
            or raw.get("delivered", True) is not True
            or type(send.get("rows")) is not int or type(send.get("restrictedRows")) is not int
            or not 0 <= send["restrictedRows"] <= send["rows"]
            or raw.get("rows") != send["rows"] or raw.get("restricted_rows") != send["restrictedRows"]
            or not begin <= started <= observed <= end <= at
            or not started <= raw["ts"] or not before_observed_end
            or not 0 <= at - raw["ts"] <= 60):
        raise ValueError("NATIVE_WORKER_ACCESS_JOIN")
    detection = Producer("detector", "zer21-trusted-worker-reader/1", {
        "clock_id":"host", "clock_source":"UNKNOWN", "resolution_ms":None}).event(context, "DETECTED", {
            "rule_id":"SUSPICIOUS_LOG", "rule_version":"1", "signature":"SQLI/fixture",
            "metric":"log_pattern_match", "value":int(raw["restricted_rows"] > 0), "threshold":0,
            "severity":"WARNING", "description":"Joined delivered worker response and native fixture access"},
        "o.alert", target={"namespace":"zd-sqli-lab","service":"sqli-fixture","flow":None}, alert_id=new_id("alt"))
    fields = ("request_id","ts","client_ip","tcp_peer","source_method","source_confidence",
              "method","path","status","rows","restricted_rows")
    access = {**{k:raw[k] for k in fields}, "delivered":True, "ref":ref,
        "run_id":context["run_id"], "trial_id":context["trial_id"], "fixture_uid":fixture_uid,
        "detection_event_id":detection["event_id"]}
    evidence = {"metric":{"name":"log_pattern_match","value":detection["payload"]["value"],"threshold":0},
        "log":{"message":detection["payload"]["description"],"observed_at":None}}
    return {"detection":detection,"evidence":evidence,"access":access}


def make_lab():
    parent = fixture_factory()

    class Lab(type(parent)):
        def __init__(self):
            super().__init__()
            self.deadline = time.monotonic() + 900
            self.work_end = self.deadline - 20
            self.context = {"run_id":self.run_id,"trial_id":self.trial_id,"incident_id":new_id("inc"),
                "group":"B2","method_version":"zer21-functional/1",
                "config_ref":"sha256:" + supervisor.sha(PREP / "source-manifest.json")}
            self.prefix = "zer19-" + self.run_id[4:16]  # Existing KafkaExecutor naming, fresh IDs.
            self.topics = [self.prefix + ".commands", self.prefix + ".results"]
            self.topic_state = {}; self.broker_uid = None
            self.executor_claimed = False
            self.worker_window = None
            self.source_uids = {}
            self.cpu_snapshot_attempted = False

        def checkpoint(self):
            super().checkpoint()
            path = OUT / "state.json"
            state = json.loads(path.read_bytes())
            state.update({"topics":self.topics, "topic_state":self.topic_state,"broker_uid":self.broker_uid,
                "source_uids":self.source_uids})
            self.save("state.json", state)

        def ensure_cache(self):
            super().ensure_cache()
            # Historical image IDs are not fresh admission; prove cached artifacts AND built Go source.
            provenance = worker_build_provenance()
            images = json.loads(self.command(["docker","--context","desktop-linux","exec",self.node,
                "crictl","images","-o","json"]).stdout)["images"]
            pins = json.loads((ROOT / "docs/evidence/ZER-19/runtime-prep/cache-pins.json").read_bytes())
            for pin in [p for p in pins if p["name"] in {"zer42-worker","zer42-nemesis"}]:
                host = self.command(["docker","--context","desktop-linux","image","inspect",pin["tag"],"--format","{{.Id}}"])
                if host.stdout.decode().strip() != pin["host_id"] or not any(
                        p["id"] == pin["node_id"] and pin["node_tag"] in p.get("repoTags",[]) for p in images):
                    raise ValueError("WORKER_TRANSPORT_CACHE_DRIFT")
            self.save("worker-cache-admission.json", {"provenance":provenance,"pins":[p for p in pins
                if p["name"] in {"zer42-worker","zer42-nemesis"}],"builds":0,"pulls":0,"imports":0})

        def kube(self, *args, timeout=15, allowed=(0,)):
            # Preserve the inherited fixed context while forwarding command bounds.
            try:
                return self.command(["kubectl", "--context", "k3d-zero-door",
                    "--request-timeout=12s", *args], timeout=timeout, allowed=allowed)
            except RuntimeError as error:
                head = list(args[:args.index("--")]) if "--" in args else list(args)
                pods = [a for a in head if a in ("zer46-source-a", "zer46-source-b")]
                if "exec" in head and pods and str(error) == "COMMAND_TIMEOUT":
                    self.exec_cpu_snapshot(pods[0], head[head.index("-c") + 1] if "-c" in head else "source")
                raise

        def container_cpu(self, pod_name, container, reads=1):
            """cpu.max plus `reads` cpu.stat reads 2 s apart, from the node's cgroup v2; read-only."""
            pod = self.pod(pod_name)
            uid = pod["metadata"]["uid"]
            cid = next(s["containerID"] for s in pod["status"]["containerStatuses"]
                       if s["name"] == container).split("://")[-1]
            if not re.fullmatch(r"[0-9a-f-]{36}", uid) or not re.fullmatch(r"[0-9a-f]{64}", cid):
                raise ValueError("CGROUP_IDENTITY")
            cg = "/sys/fs/cgroup/kubepods/*/pod%s/%s" % (uid, cid)
            script = 'set -e; d=$(ls -d %s | head -1); cat "$d/cpu.max"' % cg
            script += '; sleep 2'.join('; echo @@; cat "$d/cpu.stat"' for _ in range(reads))
            raw = self.command(["docker", "--context", "desktop-linux", "exec", self.node,
                                "sh", "-c", script], timeout=4 + 2 * reads).stdout.decode()
            parts = raw.split("@@\n")
            if len(parts) != reads + 1:
                raise ValueError("CPU_STAT_UNREADABLE")
            stat = lambda text: {k: int(v) for k, v in (line.split() for line in text.splitlines() if line.strip())}
            return {"pod_uid": uid, "container_id": cid, "cpu_max": parts[0].strip(),
                    "cpu_stat": [stat(p) for p in parts[1:]]}

        def exec_cpu_snapshot(self, pod_name, container):
            """On an exec timeout, record that container's cgroup cpu.max and two cpu.stat
            reads 2 s apart before cleanup to investigate CPU throttling.
            Read-only on the node; never replaces the original timeout."""
            doc = {"pod": pod_name, "container": container, "at": time.time()}
            if self.cpu_snapshot_attempted:
                return {**doc, "skipped": "CPU_SNAPSHOT_BUDGET_EXHAUSTED"}
            self.cpu_snapshot_attempted = True  # Reserve before any native diagnostic; never retry.
            try:
                doc.update(self.container_cpu(pod_name, container, reads=2))
            except Exception as error:
                doc["error"] = type(error).__name__ + ":" + str(error)
            self.save("%s-%s-timeout-cpu.json" % (pod_name, container), doc)
            return doc

        def source_cpu_gate(self):
            """One benign exec per source container before any TCP probe, HTTP or model call.
            A normal exec costs ~80 ms CPU (285 diagnostic execs, max 100 ms); an anomalous
            charge like runtime-03's ~1.27 s stops the run here as ValueError SOURCE_CPU_DEBT
            (kept verbatim in the receipt; cleanup still runs). No socket."""
            rows, failed = {}, False
            for who in ("a", "b"):
                name = "zer46-source-" + who
                before = self.container_cpu(name, "source")
                began = time.monotonic()
                out = self.kube("-n", "zd-sqli-lab", "exec", name, "--", "/usr/bin/python3", "-c",
                                "print('warm')").stdout
                wall = time.monotonic() - began
                after = self.container_cpu(name, "source")
                delta = {k: after["cpu_stat"][0][k] - before["cpu_stat"][0][k]
                         for k in ("usage_usec", "user_usec", "system_usec", "nr_periods", "nr_throttled")}
                ok = (out.strip() == b"warm" and delta["usage_usec"] <= SOURCE_GATE_CPU_USEC
                      and wall <= SOURCE_GATE_WALL_S)
                rows[who] = {"pod": name, "cpu_max": after["cpu_max"], "wall_s": round(wall, 3),
                             "delta": delta, "ok": ok}
                failed = failed or not ok
            self.save("source-cpu-gate.json", {"limits": {"usage_usec": SOURCE_GATE_CPU_USEC,
                      "wall_s": SOURCE_GATE_WALL_S}, "sources": rows, "verdict": "FAIL" if failed else "PASS"})
            if failed:
                raise ValueError("SOURCE_CPU_DEBT")

        def transport_dependency_gate(self):
            # Import the exact remote entrypoint without calling main, reading keys,
            # constructing Kafka clients, or sending any network/model request.
            code = "import runpy; runpy.run_path('/current/remote.py', run_name='zer21_dependency_check'); print('transport-ready')"
            try:
                result = self.kube('-n', 'zd-sqli-lab', 'exec', 'zer46-source-a', '-c',
                    'zer21-transport', '--', 'python', '-B', '-c', code, timeout=15)
                ok = result.returncode == 0 and result.stdout.strip() == b'transport-ready'
                self.save('transport-dependency-gate.json', {'verdict': 'PASS' if ok else 'FAIL',
                    'returncode': result.returncode, 'network_requests': 0, 'provider_calls': 0})
            except Exception as error:
                self.save('transport-dependency-gate.json', {'verdict': 'FAIL',
                    'error_type': type(error).__name__, 'network_requests': 0, 'provider_calls': 0})
                raise ValueError('TRANSPORT_DEPENDENCIES_NOT_READY') from error
            if not ok:
                raise ValueError('TRANSPORT_DEPENDENCIES_NOT_READY')

        def command(self, args, timeout=15, allowed=(0,)):
            # Piggyback vmstat on the existing memory guard read, not a new exec.
            memory_read = ["docker", "--context", "desktop-linux", "exec",
                           "k3d-zero-door-server-0", "cat", "/proc/meminfo", "/proc/pressure/memory"]
            if args == memory_read:
                args = [*args, "/proc/vmstat"]
            return super().command(args, timeout=timeout, allowed=allowed)

        def memory_settle_gate(self):
            # A fixed observation window after startup/import, never wait-until-pass/retry.
            start = time.monotonic()
            rows = []
            try:
                for index in range(7):
                    self.wait(start + index * 5)
                    self.resources()  # Existing host/VM minima and PSI >5 stop remain active.
                    if not self.samples:
                        raise ValueError("MEMORY_SAMPLE_MISSING")
                    row = dict(self.samples[-1])
                    rows.append(row)
                    if row["memoryPsiAvg10"] > 1:
                        raise ValueError("MEMORY_NOT_SETTLED")
                self.check()
            except Exception as error:
                self.save("memory-settle-gate.json", {"verdict":"FAIL", "samples":rows,
                    "error":type(error).__name__ + ":" + str(error), "duration_s":30,
                    "max_psi_avg10":1, "retry":False})
                raise
            self.save("memory-settle-gate.json", {"verdict":"PASS", "samples":rows,
                "duration_s":30, "max_psi_avg10":1, "retry":False})

        def isolation(self, fixture):
            self.source_cpu_gate()
            self.transport_dependency_gate()
            self.memory_settle_gate()
            return super().isolation(fixture)

        def topic(self, operation, name):
            if name not in self.topics or operation not in {"create","list","delete"}:
                raise ValueError("TOPIC_SCOPE")
            broker = json.loads(self.kube("-n","zero-door","get","pod","kafka-controller-0","-o","json").stdout)
            if self.broker_uid != broker["metadata"]["uid"] or broker["metadata"].get("deletionTimestamp"):
                raise ValueError("BROKER_UID_DRIFT")
            argument = name if operation == "create" else "^" + re.escape(name) + "$"
            args = ["-n","zero-door","exec","kafka-controller-0","-c","kafka","--","env",
                "-u","JMX_PORT","-u","KAFKA_JMX_OPTS","KAFKA_HEAP_OPTS=-Xms16m -Xmx128m","/opt/bitnami/kafka/bin/kafka-topics.sh",
                "--bootstrap-server","localhost:9092","--" + operation,"--topic",argument]
            if operation == "create":
                if name in self.topic_state:
                    raise ValueError("TOPIC_ALREADY_ATTEMPTED")
                args += ["--partitions","1","--replication-factor","1","--config","retention.ms=3600000"]
                self.topic_state[name] = "UNKNOWN"; self.checkpoint()  # Durable before create.
                result = self.kube(*args, timeout=10, allowed=(0,1))
                self.topic_state[name] = "OWNED" if result.returncode == 0 else "FOREIGN_OR_UNKNOWN"
                self.checkpoint()
                if result.returncode != 0:
                    raise ValueError("TOPIC_CREATE_NOT_OWNED")
            else:
                result = self.kube(*args, timeout=10)
            return result.stdout.decode().splitlines()

        def input_command(self, args, data, *, secret=False, timeout=20):
            # stdin never enters command args or receipts. Even rejected Secret stdout/stderr is discarded.
            self.check()
            began = time.time()
            result = None
            error = None
            try:
                result = subprocess.run(args, input=data, capture_output=True, env=self.env, timeout=timeout,
                    creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                if result.returncode != 0:
                    raise ValueError("NATIVE_INPUT_COMMAND_FAILED")
                self.check()
                return result
            except Exception as failure:
                error = type(failure).__name__
                raise
            finally:
                self.save("secret-create.json" if secret else "worker-transport-command.json",
                    {"args":args,"begin":began,"end":time.time(),"stdin_retained":False,
                     "output_redacted":secret,"timeout_s":timeout,"error_type":error,
                     "returncode":result.returncode if result else None,
                     "stdout":result.stdout[:65536].decode(errors="replace") if result and not secret else None,
                     "stderr":result.stderr[:65536].decode(errors="replace") if result and not secret else None})

        def apply_bootstrap(self, bootstrap):
            import render
            service = next(d for d in bootstrap if (d["kind"],d["metadata"]["name"]) ==
                ("Service","zer41-private-ingress"))
            self.kube("create","-f",self.write_yaml("private-service-alias.yaml",[service]))
            ingress = json.loads(self.kube("-n","zd-sqli-lab","get","svc","zer41-private-ingress","-o","json").stdout)
            broker = json.loads(self.kube("-n","zero-door","get","pod","kafka-controller-0","-o","json").stdout)
            self.broker_uid = broker["metadata"]["uid"]; self.checkpoint()
            for name in self.topics:
                self.topic("create",name)
            documents, containers, volumes, self.command_policy = render.worker_documents(
                self.context,self.owner,ingress["spec"]["clusterIP"])
            secrets = [{"apiVersion":"v1","kind":"Secret","metadata":{"name":"zer21-" + purpose,
                "namespace":"zd-sqli-lab","labels":{"zero-door.io/run":self.owner}},
                "stringData":{"key.json":json.dumps({"id":self.prefix + "-" + purpose,"purpose":purpose,
                    "secret":uuid.uuid4().hex + uuid.uuid4().hex})}} for purpose in ("fault","operator")]
            self.input_command(["kubectl","--context","k3d-zero-door","--request-timeout=12s","create","-f","-"],
                json.dumps({"apiVersion":"v1","kind":"List","items":secrets}).encode(),secret=True,timeout=15)
            a = next(d for d in bootstrap if d["kind"] == "Pod" and d["metadata"]["name"] == "zer46-source-a")
            a["spec"]["automountServiceAccountToken"] = True  # Go constructs an in-cluster client; no RBAC grants.
            a["spec"].setdefault("securityContext",{})["fsGroup"] = 65532
            a["spec"]["containers"].extend(containers); a["spec"].setdefault("volumes",[]).extend(volumes)
            a["metadata"].setdefault("annotations",{})["kubectl.kubernetes.io/default-container"] = a["spec"]["containers"][0]["name"]
            super().apply_bootstrap(bootstrap + documents)
            self.source_uids = {who:self.pod("zer46-source-" + who)["metadata"]["uid"] for who in ("a","b")}
            self.checkpoint()
            self.save("active-private-policy.json",self.command_policy)
            end = min(self.work_end,time.monotonic() + 35)
            while time.monotonic() < end:
                group = self.kube("-n","zero-door","exec","kafka-controller-0","-c","kafka","--",
                    "env","-u","JMX_PORT","-u","KAFKA_JMX_OPTS","KAFKA_HEAP_OPTS=-Xms16m -Xmx128m","/opt/bitnami/kafka/bin/kafka-consumer-groups.sh",
                    "--bootstrap-server","localhost:9092","--describe","--group",self.owner + ".worker","--state",
                    timeout=10,allowed=(0,1))
                if "Stable" in group.stdout.decode():
                    return
                self.wait(time.monotonic() + 1)
            raise ValueError("WORKER_CONSUMER_NOT_READY")

        def check_sources(self):
            for who,uid in self.source_uids.items():
                pod = self.pod("zer46-source-" + who)
                if (pod["metadata"]["uid"] != uid or pod["metadata"].get("deletionTimestamp")
                        or pod["metadata"]["labels"].get("zero-door.io/run") != self.owner
                        or pod["spec"].get("nodeName") != self.node
                        or pod["status"].get("podIP") != self.addresses[who]):
                    raise ValueError("SOURCE_POD_UID_DRIFT")

        def native_api(self):
            base,connection = super().native_api()
            lab = self
            class SingleWrite:
                api_client = base.api_client
                @property
                def writes(self): return base.writes
                def read_namespaced_config_map(self,*args,**kwargs):
                    return base.read_namespaced_config_map(*args,**kwargs)
                def replace_namespaced_config_map(self,*args,**kwargs):
                    if base.writes >= 1:
                        raise ValueError("SINGLE_API_WRITE_BOUND")
                    lab.check_sources()
                    lab.pod()  # Existing fixture UID guard, refreshed at the action boundary.
                    return base.replace_namespaced_config_map(*args,**kwargs)
            return SingleWrite(),connection

        async def execute_worker(self, command):
            if self.executor_claimed or self.fixture_http != 1:
                raise ValueError("EXECUTOR_REPLAY_OR_HTTP_BUDGET")
            self.executor_claimed = True
            self.fixture_http += 1  # Reserve before ambiguous remote execution; never refund.
            self.checkpoint()
            self.save("worker-dispatch-intent.json",{"command":command,"possible_http_sends":1,"at":time.time()})
            async def invoke():
                self.check_sources()
                begin = time.time()
                result = await asyncio.to_thread(self.input_command,
                    ["kubectl","--context","k3d-zero-door","--request-timeout=20s","-n","zd-sqli-lab",
                     "exec","-i","zer46-source-a","-c","zer21-transport","--","python","-B","/current/remote.py"],
                    json.dumps(command,allow_nan=False).encode(),timeout=22)
                self.worker_window = (begin,time.time())
                self.check_sources()
                if len(result.stdout) > 32768:
                    raise ValueError("WORKER_RESULT_SIZE")
                value = json.loads(result.stdout)
                self.save("worker-result.json",value)
                return value
            task = asyncio.create_task(invoke())
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                try: await task
                except Exception: pass
                raise

        async def observe_worker(self, receipt):
            def collect():
                result = [r["raw"] for r in receipt["records"] if r["event"] == "EXECUTOR_RESULT"][0]
                response = result["details"]["sqli"]["sends"][0]["responseId"]
                pod = self.pod()
                raw = self.join_access(pod,response)
                current = self.pod(pod["metadata"]["name"])
                self.check_sources()
                observed = project_worker(self.context,receipt,raw,fixture_uid=self.fixture_uid,
                    pod_uid=current["metadata"]["uid"],source_ip=self.addresses["a"],proxy_ip=self.addresses["proxy"],
                    begin=self.worker_window[0],end=self.worker_window[1],at=time.time(),ref="worker-native-join.json")
                self.save("worker-native-join.json",{"pod_uid":current["metadata"]["uid"],"raw_access":raw,
                    "worker_result_sha256":supervisor.sha(OUT / "worker-result.json"),"projection":observed,
                    "cross_host_clock_verified":False,"benchmark_eligible":False})
                return observed
            task = asyncio.create_task(asyncio.to_thread(collect))
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                try: await task
                except Exception: pass
                raise

        async def cases(self):
            # Existing protocol has completed isolation plus exactly one native benign baseline.
            budget = RunBudget(self.run_id,max_calls=3,max_reserved_tokens=30000,max_estimated_usd=.015,duration_s=300)
            adapter = Adapter(HttpxTransport(os.environ["OPENAI_API_KEY"]),budget,
                limits=Limits(attempts=1,timeout_s=20,deadline_s=25,retry_delay_s=0,max_output_tokens=256))
            baseline = json.loads((OUT / "http-001.json").read_bytes())
            async def health():
                self.check()
                if baseline["response"]["status"] != 200 or time.time() - baseline["response"]["end"] > 60:
                    raise ValueError("NATIVE_HEALTH_BASELINE_STALE")
                return {"observed_at":datetime.fromtimestamp(baseline["response"]["end"]).astimezone().isoformat(),
                    "evidence":[{"id":"ev-health-01","health":"HEALTHY"}]}
            api,connection = self.native_api()
            output = OUT / "cycle"; output.mkdir()
            journal = Journal(output,self.context)
            try:
                nemesis = Session(purpose=PURPOSE,guard=CommandGuard(self.command_policy),adapter=adapter,
                    observe=health,execute=self.execute_worker,context=self.context,
                    limits=SessionLimits(max_rounds=1,duration_s=90,command_s=1,required_rounds=1,
                        allowed_templates=("disclose-restricted",)))
                gaia = Diagnoser(adapter,self.context,lambda event:journal({"kind":"GAIA_EVENT","event":event}))
                healer = Healer(adapter,self.context,api=api,pins=self.target_pins,fixture_uid=self.fixture_uid,
                    journal=journal,probe=self.probe,ttl_sec=180,probe_timeout_s=120)
                cycle = FunctionalCycle(nemesis,gaia,healer,observe_result=self.observe_worker,sink=journal)
                receipt = await cycle.run()
                self.save("cycle-receipt.json",receipt)
                if (receipt["status"] != "COMPLETED_PENDING_NATIVE_REVIEW"
                        or receipt["stages"]["healer"]["status"] != "ACTION_COMPLETED"
                        or self.fixture_http != 8 or self.tcp_checks != 2 or api.writes != 1):
                    raise ValueError("NATIVE_CYCLE_NOT_MET")
                self.save("functional-observed.json",{"status":"OBSERVED_PENDING_REVIEW",
                    "fixture_http_reserved_or_dispatched":self.fixture_http,"tcp_checks":self.tcp_checks,
                    "model_budget":budget.summary(),"api_replace_attempts":api.writes,
                    "runtime_ac_verified":False,"recovery_verified":False,"benchmark_eligible":False})
            finally:
                self.save("model-budget.json",budget.summary())
                journal.close(); connection.close()

        def http(self,*args,**kwargs):
            if self.fixture_http >= 8:
                raise ValueError("ZER21_HTTP_BUDGET")
            self.check_sources()
            result = super().http(*args,**kwargs)
            self.check_sources()
            return result

        def cleanup_namespace(self):
            """Inherited ZER-50 namespace cleanup with three-valued facts.

            True/False was checked, None was not. A later failure, including the
            resource guard, is recorded but never rewrites an established fact.
            """
            self.cleanup_mode = True; self.stop.set()
            self.deadline = time.monotonic() + 265
            state_path = OUT / "state.json"
            state = json.loads(state_path.read_bytes()) if state_path.exists() else {}
            for k, v in state.items():
                setattr(self, k, v)
            self.seq = 10000  # Preserve work raw receipts.
            facts = {"namespace_absent":None,"shared_specs_preserved":None,"shared_restarts_preserved":None}
            errors, step = [], "namespace"
            try:
                if state.get("creation_attempted"):
                    raw = self.kube("get","namespace",fixture.NAMESPACE,"--ignore-not-found","-o","json").stdout
                    if raw.strip():
                        ns = json.loads(raw)
                        if (ns["metadata"]["labels"].get("zero-door.io/run") != state["owner"]
                                or state.get("ns_uid") and ns["metadata"]["uid"] != state["ns_uid"]):
                            raise ValueError("CLEANUP_OWNER_UID")
                        self.save("namespace-delete-options.json",{"apiVersion":"v1","kind":"DeleteOptions",
                            "preconditions":{"uid":ns["metadata"]["uid"]}})
                        self.kube("delete","--raw","/api/v1/namespaces/" + fixture.NAMESPACE,
                            "-f",str(OUT / "namespace-delete-options.json"))
                        self.command(["kubectl","--context","k3d-zero-door","--request-timeout=12s","wait",
                            "--for=delete","namespace/" + fixture.NAMESPACE,"--timeout=150s"],timeout=155)
                facts["namespace_absent"] = not self.kube("get","namespace",fixture.NAMESPACE,
                    "--ignore-not-found","-o","name").stdout.strip()
                step = "shared"
                after = self.shared(self.snapshot("after"))
                before_path = OUT / "before.json"
                if before_path.exists():
                    before = json.loads(before_path.read_bytes())
                    facts["shared_specs_preserved"] = self.specs(after) == self.specs(before)
                    facts["shared_restarts_preserved"] = self.restarts(after) == self.restarts(before)
                step = None
            except Exception as error:
                errors.append(type(error).__name__ + ":" + str(error))
            # Checked on its own so a namespace/snapshot failure cannot skip it; topic effects need PASS.
            try:
                self.resources()
                resource_guard = "PASS"
            except Exception as error:
                errors.append(type(error).__name__ + ":" + str(error))
                resource_guard = "FAIL"
                step = step or "resources"
            result = dict(facts,rules_and_owned_orders_removed_by_namespace_deletion=facts["namespace_absent"],
                errors=errors,failed_step=step,resource_guard=resource_guard,
                provider_calls=0,fixture_http=0,business_recovery_claim=False,
                verdict="CLEAN" if all(v is True for v in facts.values()) and not errors else "INCOMPLETE")
            self.save("cleanup.json",result)
            return result

        def cleanup_owned(self):
            result = self.cleanup_namespace()  # UID/owner namespace deletion precedes topic cleanup.
            errors = []
            if result["namespace_absent"] is not True:
                result["topic_cleanup"] = "NOT_ATTEMPTED_NAMESPACE_NOT_CONFIRMED_ABSENT"
            elif result.get("resource_guard") != "PASS":
                # The guard stops further effects; owned topics stay recorded for a separately approved resume.
                result["topic_cleanup"] = "PENDING_RESOURCE_GUARD"
            else:
                result["topic_cleanup"] = "ATTEMPTED"
                for name,state in self.topic_state.items():
                    try:
                        present = name in self.topic("list",name)
                        if present and state != "OWNED":
                            raise ValueError("TOPIC_OWNERSHIP_UNKNOWN_NOT_DELETED")
                        if present:
                            self.topic("delete",name)
                        for _ in range(3):
                            if name not in self.topic("list",name):
                                break
                            self.wait(time.monotonic() + 1)
                        else:
                            raise ValueError("TOPIC_STILL_PRESENT")
                    except Exception as error:
                        errors.append(type(error).__name__ + ":" + str(error))
            result["topic_state"] = self.topic_state
            result["topic_cleanup_errors"] = errors
            if errors:
                result["verdict"] = "INCOMPLETE"
            self.save("cleanup.json",result)
            return result

    return Lab()


def main():
    fixture.make_lab = make_lab
    return fixture.main()


if __name__ == "__main__":
    raise SystemExit(main())
