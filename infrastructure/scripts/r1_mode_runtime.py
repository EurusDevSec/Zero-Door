"""RT2 preparation and in-pod O boundary checks; never mutates Kubernetes or builds images.

prepare creates a fresh, private bundle. The image is built from the unchanged production
Hephaestus Dockerfile/context, then imported ONLY after separate lab approval. The driver
and actors are separate pods with separate key projections and no service-account tokens.
BM observes real HTTP availability; B1/B2/B3 use explicitly synthetic transport controls
in different runs. None of these runs is a recovery-performance dataset.
"""
import argparse
import hashlib
import ipaddress
import json
import math
from pathlib import Path
import re
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

_PARENTS = Path(__file__).resolve().parents
ROOT = _PARENTS[2] if len(_PARENTS) >= 3 else Path("/")
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
GROUPS = ("BM", "B1", "B2", "B3")
TARGET = "http://frontend.target-app.svc.cluster.local/"
CLOCK = {"clock_id": "clk-rt2-o", "clock_source": "UNKNOWN", "resolution_ms": None}
FORBIDDEN = {"HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED", "GUARD_VERDICT", "LLM_CALL"}
LIMITS = {"total_s": 2700, "cleanup_reserve_s": 300, "monitor_s": 180,
          "max_gets": 360, "interval_s": 0.5, "request_timeout_s": 1,
          "frontend_pod_deletes": 1, "paid_api_calls": 0}


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    Path(path).write_bytes(encoded(value) + b"\n")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http(url, body=None, token=None, timeout=2):
    """No proxy/redirect: the explicit in-cluster endpoint is the only destination."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url, data=encoded(body) if body is not None else None, headers=headers)
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read(2 * 1024 * 1024)
    except HTTPError as error:
        return error.code, error.read(2 * 1024 * 1024)


def specification():
    return {"id": "G-ZER11-RT2", "context": "k3d-zero-door", "limits": LIMITS,
            "image": "unchanged production Hephaestus Dockerfile; unique source-digest tag, pull Never",
            "source": "BM detector=rt2-http-availability/1, NOT Gaia. B1/B2/B3 are transport controls only.",
            "writes": ["build/import ONE new local Hephaestus image after approval",
                       "create one zd-zer11-rt2-<8hex> namespace and its labelled bundle resources",
                       "temporarily scale existing zero-door/gaia and zero-door/hephaestus to zero",
                       "delete exactly one existing target-app/frontend pod by UID",
                       "restore original Gaia/Hephaestus replicas with UID/spec/resourceVersion checks",
                       "delete only run-created namespace/resources by UID; read back absence"],
            "excluded": ["target replica/quota changes", "HPA", "paid model", "legacy healer",
                         "performance/KPI claims", "human-blind BM claim", "publication/Linear"],
            "stop": ["wrong context or node NotReady", "foreign HPA on frontend",
                     "source/image mismatch", "BM auto-decision/action", "archive failure",
                     "request/time cap", "ownership/spec drift", "interruption"],
            "completion": "BM must have an observed failed GET, live consumer audit, valid manual refusal, no action; controls and cleanup must pass"}


def source_files():
    base = ROOT / "agent-orchestrator"
    files = [base / "hephaestus" / name for name in ("Dockerfile", "requirements.lock", "main.py", "command_guard.py")]
    files += [base / "nemesis" / "command_guard.py"]
    files += sorted(p for p in (base / "event_pipeline").rglob("*.py") if "__pycache__" not in p.parts)
    return base, files


def pod(name, namespace, image, role, mounts, volumes, env=None, command=None):
    container = {"name": "main", "image": image, "imagePullPolicy": "Never",
                 "env": [{"name": k, "value": str(v)} for k, v in (env or {}).items()],
                 "resources": {"requests": {"cpu": "50m", "memory": "96Mi"},
                               "limits": {"cpu": "250m", "memory": "192Mi"}},
                 "securityContext": {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True,
                                     "capabilities": {"drop": ["ALL"]}}, "volumeMounts": mounts}
    if command:
        container["command"] = command
    return {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": name, "namespace": namespace,
             "labels": {"zero-door.io/run": namespace, "rt2-role": role}},
            "spec": {"nodeName": "k3d-zero-door-server-0", "restartPolicy": "Never",
                     "automountServiceAccountToken": False, "activeDeadlineSeconds": LIMITS["total_s"],
                     "securityContext": {"runAsNonRoot": True, "runAsUser": 65532, "runAsGroup": 65532,
                                         "fsGroup": 65532, "seccompProfile": {"type": "RuntimeDefault"}},
                     "containers": [container], "volumes": volumes}}


def prepare(output, namespace):
    if not re.fullmatch(r"zd-zer11-rt2-[0-9a-f]{8}", namespace):
        raise ValueError("namespace must be fresh zd-zer11-rt2-<8 hex>")
    from event_pipeline.contract import new_id
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    base, files = source_files()
    manifest = {}
    for source in files:
        rel = source.relative_to(base)
        destination = out / "build" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        destination.write_bytes(data)
        manifest[str(rel).replace("\\", "/")] = digest(data)
    source_hash = digest(encoded(manifest))
    image = "zero-door/hephaestus:zer11-rt2-" + source_hash[:16]
    cfg = {"version": "zd-rt2/1", "profile": "RUNTIME_PENDING", "target": TARGET, "namespace": namespace, "image": image,
           "source_files": manifest, "driver_sha256": digest(Path(__file__).read_bytes()),
           "source_sha256": source_hash, "contexts": {g: {"run_id": new_id("run"), "trial_id": new_id("trl"),
             "incident_id": new_id("inc"), "group": g, "config_ref": "sha256:" + source_hash,
             "method_version": "rt2-mode-boundary/1; " + ("LIVE_HTTP_NOT_GAIA" if g == "BM" else "SYNTHETIC_TRANSPORT_CONTROL")}
             for g in GROUPS}}
    roles = ("harness", "detector", "decision_rules", "operator_console", "reader")
    keys = {role: secrets.token_hex(32) for role in roles}
    operator = {"id": "rt2-heal-operator", "purpose": "heal-operator", "secret": secrets.token_hex(32)}
    secret_data = {"gateway.json": json.dumps(keys),
                   "rules.json": json.dumps({k: keys[k] for k in ("decision_rules", "reader")}),
                   "operator.json": json.dumps({k: keys[k] for k in ("operator_console", "reader")}),
                   "heal-operator.json": json.dumps(operator)}
    for group in GROUPS:
        secret_data["policy-" + group + ".json"] = json.dumps({"version": "zd-guard/1", "enabled": True,
            "context": {k: cfg["contexts"][group][k] for k in ("run_id", "trial_id", "group")},
            "targets": [{"namespace": "target-app", "service": "frontend", "url": TARGET}],
            "maxDurationSec": 1, "maxConcurrency": 1, "rps": 1})
    meta = lambda name: {"name": name, "namespace": namespace, "labels": {"zero-door.io/run": namespace}}
    docs = [{"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": namespace,
              "labels": {"zero-door.io/run": namespace}}},
            {"apiVersion": "v1", "kind": "Secret", "metadata": meta("rt2-keys"), "type": "Opaque", "stringData": secret_data},
            {"apiVersion": "v1", "kind": "ConfigMap", "metadata": meta("rt2-code"),
             "data": {"r1_mode_runtime.py": Path(__file__).read_text(encoding="utf-8"), "config.json": json.dumps(cfg)}}]
    cm = {"name": "code", "configMap": {"name": "rt2-code"}}
    work = {"name": "work", "emptyDir": {}}
    code_mount = {"name": "code", "mountPath": "/rt2", "readOnly": True}
    work_mount = {"name": "work", "mountPath": "/work"}
    def secret(items):
        return {"name": "keys", "secret": {"secretName": "rt2-keys", "defaultMode": 288,
                "items": [{"key": key, "path": path} for key, path in items]}}
    key_mount = {"name": "keys", "mountPath": "/keys", "readOnly": True}
    python_env = {"PYTHONPATH": "/:/app:/usr/local/lib/python3.11/site-packages", "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": "/work"}
    docs.append(pod("rt2-driver", namespace, image, "gateway", [code_mount, work_mount, key_mount],
                    [cm, work, secret([("gateway.json", "gateway.json")])], python_env,
                    ["/usr/bin/python3", "-B", "/rt2/r1_mode_runtime.py", "driver", "--root", "/work", "--config", "/rt2/config.json", "--keys", "/keys/gateway.json"]))
    docs.append({"apiVersion": "v1", "kind": "Service", "metadata": meta("rt2-o"), "spec": {
        "selector": {"rt2-role": "gateway", "zero-door.io/run": namespace}, "ports": [{"port": 9141, "targetPort": 9141}]}})
    for group in GROUPS:
        # ZD_OPERATOR_TOKEN_FILE below is a mounted path; the random token is never in an env value.
        env = dict(python_env, ZD_EVENT_URL="http://rt2-o:9141", ZD_O_KEYS_FILE="/keys/rules.json",  # nosec B106
                   ZD_COMMAND_POLICY_FILE="/keys/policy.json", ZD_OPERATOR_TOKEN_FILE="/keys/heal-operator.json",
                   ZD_COMMAND_LEDGER_FILE="/work/claims.sqlite", ZD_PRODUCER_VERSION="rt2-image-" + source_hash[:16],
                   ZD_CLOCK_ID="clk-rt2-heph", ZD_CLOCK_SOURCE="UNKNOWN",
                   ZD_RUN_ID=cfg["contexts"][group]["run_id"], ZD_TRIAL_ID=cfg["contexts"][group]["trial_id"])
        docs.append(pod("rt2-" + group.lower(), namespace, image, "actor", [code_mount, work_mount, key_mount],
                        [cm, work, secret([("rules.json", "rules.json"), ("policy-" + group + ".json", "policy.json"),
                                       ("heal-operator.json", "heal-operator.json")])], env))
    docs.append(pod("rt2-console", namespace, image, "console", [code_mount, work_mount, key_mount],
                    [cm, work, secret([("operator.json", "operator.json"), ("heal-operator.json", "heal-operator.json")])],
                    python_env, ["/usr/bin/python3", "-c", "import time; time.sleep(2700)"]))
    docs.append({"apiVersion": "networking.k8s.io/v1", "kind": "NetworkPolicy", "metadata": meta("rt2-ingress"),
                 "spec": {"podSelector": {}, "policyTypes": ["Ingress"], "ingress": [
                     {"from": [{"podSelector": {"matchLabels": {"rt2-role": "actor"}}},
                               {"podSelector": {"matchLabels": {"rt2-role": "console"}}}],
                      "ports": [{"protocol": "TCP", "port": 9141}, {"protocol": "TCP", "port": 8000}]}]}})
    # Private manifests contain fresh test credentials: never copy these into public evidence.
    save(out / "private-resources.json", {"apiVersion": "v1", "kind": "List", "items": docs})
    save(out / "config.json", cfg)
    save(out / "source-manifest.json", {"files": manifest, "source_sha256": source_hash, "image": image,
         "driver_sha256": digest(Path(__file__).read_bytes()), "built": False, "runtime": "NOT_RUN"})
    save(out / "plan.json", specification())
    return {"output": str(out), "image": image, "source_sha256": source_hash, "built": False, "runtime": "NOT_RUN"}


class Driver:
    def __init__(self, root, cfg, keys, bind="127.0.0.1", port=0):
        from event_pipeline.contract import Producer
        from event_pipeline.gateway import Gateway, server
        from event_pipeline.store import Archive
        self.root, self.cfg, self.keys = Path(root), cfg, keys
        self.interval = cfg.get("interval_s", LIMITS["interval_s"])
        self.get_cap = cfg.get("max_gets", LIMITS["max_gets"])
        if (type(self.interval) not in (int, float) or not math.isfinite(self.interval) or not .5 <= self.interval <= 10 or
                type(self.get_cap) is not int or not 1 <= self.get_cap <= LIMITS["max_gets"]):
            raise ValueError("RT2 request budget may only be tightened")
        if self.root.exists():
            # Kubernetes /work exists; require this run's archive and outputs to be fresh.
            if any((self.root / p).exists() for p in ("archive-O", "observations.json", "exports")):
                raise ValueError("RT2 root is not fresh")
        self.root.mkdir(parents=True, exist_ok=True)
        self.archive = Archive(self.root / "archive-O", "O")
        self.gateway = Gateway(self.archive, keys)
        self.http = server(self.gateway, (bind, port))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.http.server_port)
        harness = Producer("harness", "rt2-boundary/1", CLOCK)
        for ctx in cfg["contexts"].values():
            for event in (harness.event(dict(ctx, trial_id=None), "RUN_CONTEXT", {}, "o.context"),
                          harness.event(ctx, "TRIAL_CONTEXT", {}, "o.context")):
                self.gateway.submit(event, "harness", "rt2-start")
        self.samples, self.failure, self.detected, self.monitor = [], None, None, None
        self.started, self.finished = None, False
        self.monitor_end, self.monitor_reason = None, None
        self.stop = threading.Event()
        self.lock = threading.Lock()

    def detection(self, group, rule, metric, value, threshold, description):
        from event_pipeline.client import Client
        from event_pipeline.contract import Producer, new_id
        ctx = self.cfg["contexts"][group]
        version = "rt2-http-availability/1" if group == "BM" else "rt2-synthetic-transport-control/1"
        client = Client(self.url, self.keys["detector"], self.keys["reader"], ctx["run_id"], ctx["trial_id"],
                        Producer("detector", version, CLOCK))
        # Gaia's adapter has a Gaia-specific rule_version. Do not mislabel this diagnostic observer as Gaia.
        event = client.producer.event(client.context(), "DETECTED", {"rule_id": rule, "rule_version": version,
            "signature": rule + "/frontend", "metric": metric, "value": value, "threshold": threshold,
            "severity": "WARNING", "description": description}, "o.alert",
            target={"namespace": "target-app", "service": "frontend", "flow": None}, alert_id=new_id("alt"))
        client.publish(event)
        return event

    def observe(self, request=http):
        with self.lock:
            if self.finished or len(self.samples) >= self.get_cap:
                raise ValueError("monitor is closed or request cap reached")
            at, mono = time.time(), time.monotonic()
            try:
                code, _ = request(TARGET, timeout=LIMITS["request_timeout_s"])
                sample = {"at": at, "status": code, "ok": code == 200}
            except (OSError, TimeoutError) as error:
                sample = {"at": at, "status": None, "ok": False, "error": type(error).__name__}
            self.samples.append(sample)
            sample["monotonic_s"] = mono
            save(self.root / "observations.json", self.samples)
            if not sample["ok"] and self.detected is None:
                self.detected = self.detection("BM", "HIGH_ERROR_RATE", "rt2_http_unavailable", 1, 0,
                    "Observed failed GET; availability boundary only, not Gaia or business recovery")
            return sample

    def start_monitor(self):
        with self.lock:
            if self.monitor or self.finished:
                raise ValueError("monitor already started or closed")
            self.started = time.monotonic()
            def run():
                try:
                    while not self.stop.is_set() and time.monotonic() - self.started < LIMITS["monitor_s"]:
                        if len(self.samples) >= self.get_cap:
                            self.monitor_reason = "REQUEST_CAP"
                            return
                        self.observe()
                        if self.stop.wait(self.interval):
                            break
                    self.monitor_reason = "STOP_REQUESTED" if self.stop.is_set() else "WINDOW_COMPLETE"
                except Exception as error:
                    self.failure = type(error).__name__
                    self.monitor_reason = "EXCEPTION"
                finally:
                    self.monitor_end = time.monotonic()
            self.monitor = threading.Thread(target=run, daemon=True)
            self.monitor.start()

    def controls(self):
        if self.finished:
            raise ValueError("closed")
        for group in ("B1", "B2", "B3"):
            events = self.events(group)
            if not any(e["event_type"] == "DETECTED" for e in events):
                self.detection(group, "HIGH_CPU", "SYNTHETIC_TRANSPORT_ONLY", 90, 80,
                    "SYNTHETIC positive control; never recovery evidence or scored cohort")

    def events(self, group):
        return [r["envelope"] for r in self.archive.records(self.cfg["contexts"][group]["run_id"])]

    def summary(self):
        return {"contexts": self.cfg["contexts"], "samples": list(self.samples), "failure": self.failure,
                "interval_s": self.interval, "max_gets": self.get_cap,
                "profile": self.cfg.get("profile"), "monitor_reason": self.monitor_reason,
                "monitor_duration_s": self.monitor_end - self.started if self.started is not None and self.monitor_end is not None else None,
                "monitor_alive": bool(self.monitor and self.monitor.is_alive()),
                "finished": self.finished, "events": {g: self.events(g) for g in GROUPS}}

    def finish(self):
        self.stop.set()
        if self.monitor:
            self.monitor.join(3)
            if self.monitor.is_alive():
                raise RuntimeError("MONITOR_NOT_STOPPED")
        self.finished = True
        exports = self.root / "exports"
        exports.mkdir(exist_ok=False)
        for group, ctx in self.cfg["contexts"].items():
            self.gateway.seal(ctx["run_id"])
            self.archive.export(ctx["run_id"], exports / group)
        answer = self.summary()
        save(self.root / "summary.json", answer)
        return answer

    def close(self):
        self.stop.set()
        if self.monitor:
            self.monitor.join(3)
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(2)
        self.archive.close()


def operator(cfg, keys, token, url, heal_url):
    """Scripted operator control, O-only. This is NOT a blinded human BM trial."""
    from event_pipeline.client import Client
    from event_pipeline.contract import Producer, new_id, now
    if set(keys) != {"operator_console", "reader"}:
        raise ValueError("operator has unexpected roles")
    target = urlsplit(heal_url)
    if target.scheme != "http" or target.username or target.password or target.path not in ("", "/") \
            or target.query or target.fragment or not target.hostname:
        raise ValueError("invalid explicit heal endpoint")
    # Both an explicitly read pod IP and loopback used by offline integration are accepted.
    try:
        if not ipaddress.ip_address(target.hostname).is_private:
            raise ValueError("heal endpoint is not private")
    except ValueError:
        raise ValueError("explicit private pod IP required") from None
    ctx = cfg["contexts"]["BM"]
    client = Client(url, keys["operator_console"], keys["reader"], ctx["run_id"], ctx["trial_id"],
                    Producer("operator_console", "rt2-scripted-operator/1", CLOCK))
    actual = client.context()
    if any(actual.get(k) != ctx[k] for k in ("run_id", "trial_id", "group")):
        raise ValueError("operator context mismatch")
    alerts = [r["envelope"] for r in client.records() if r["envelope"]["event_type"] == "DETECTED"]
    if len(alerts) != 1 or alerts[0]["producer_version"] != "rt2-http-availability/1":
        raise ValueError("one live BM observation required")
    alert = alerts[0]
    event = client.producer.event(actual, "DECISION", {"stage": "PROPOSAL", "decision_source": "MANUAL",
        "inputs": [{"event_id": alert["event_id"], "received_at": now()}], "response_kind": "ACTION",
        "proposal": {"action_type": "SCALE_UP", "params": {"service": "frontend"}},
        "fallback": False, "fallback_of": None, "prompt_version": None, "prompt_sha256": None,
        "evidence_package_version": "o-envelope/1.0.0"}, "o.decision", target=alert["target"],
        decision_id=new_id("dec"), causation_id=alert["event_id"])
    client.publish(event)
    status, raw = http(heal_url.rstrip("/") + "/heal/trigger", {"decision_id": event["decision_id"]}, token["secret"], timeout=10)
    return {"scripted_operator_control": True, "decision_id": event["decision_id"], "status": status, "body": json.loads(raw)}


def assess(summary, logs, manual):
    """Boundary evidence only. Host image/cleanup/source checks remain separately required."""
    errors = []
    if summary.get("failure") or summary.get("monitor_alive") or not summary.get("finished"):
        errors.append("MONITOR_INCOMPLETE")
    offline = summary.get("profile") == "OFFLINE_TEST_ONLY"
    if not offline and (summary.get("monitor_reason") != "WINDOW_COMPLETE" or
                        (summary.get("monitor_duration_s") or 0) < LIMITS["monitor_s"]):
        errors.append("BM_OBSERVATION_WINDOW_INCOMPLETE")
    samples = summary.get("samples", [])
    if not samples or not any(s.get("ok") is False for s in samples) or len(samples) > LIMITS["max_gets"]:
        errors.append("BM_LIVE_FAILURE_NOT_OBSERVED")
    if not any(s.get("ok") is True for s in samples):
        errors.append("BM_HEALTHY_CONTROL_MISSING")
    failed = [i for i, sample in enumerate(samples) if sample.get("ok") is False]
    if failed and not any(s.get("ok") is True for s in samples[:failed[0]]):
        errors.append("BM_HEALTHY_BASELINE_MISSING")
    for group in GROUPS:
        events = summary["events"][group]
        if any(e["event_type"] in FORBIDDEN for e in events):
            errors.append(group + "_FORBIDDEN_EVENT")
        detections = [e for e in events if e["event_type"] == "DETECTED"]
        expected_version = "rt2-http-availability/1" if group == "BM" else "rt2-synthetic-transport-control/1"
        if len(detections) != 1 or detections[0]["producer_version"] != expected_version or detections[0]["payload"]["rule_version"] != expected_version:
            errors.append(group + "_DETECTION_MISSING_OR_WRONG_SOURCE")
        decisions = [e for e in events if e["event_type"] == "DECISION"]
        expected_kind = {"BM": "MANUAL", "B1": "RULES"}.get(group)
        if expected_kind:
            source = "operator_console" if group == "BM" else "decision_rules"
            if len(decisions) != 1 or decisions[0]["payload"]["decision_source"] != expected_kind or decisions[0]["source_component"] != source:
                errors.append(group + "_DECISION_BOUNDARY")
            elif len(detections) == 1 and decisions[0]["causation_id"] != detections[0]["event_id"]:
                errors.append(group + "_DECISION_CAUSATION")
        elif decisions:
            errors.append(group + "_UNEXPECTED_AUTO_DECISION")
        if group != "B1":
            audit = []
            for line in logs.get(group, "").splitlines():
                if "MODE_AUDIT " in line:
                    try:
                        audit.append(json.loads(line.split("MODE_AUDIT ", 1)[1]))
                    except ValueError:
                        errors.append(group + "_MALFORMED_AUDIT")
            ctx = {k: summary["contexts"][group][k] for k in ("run_id", "trial_id", "group")}
            if not any(a.get("reason") == "AUTO_DECISION_DISABLED_FOR_GROUP" and a.get("route") == "consumer" and a.get("context") == ctx for a in audit):
                errors.append(group + "_CONSUMER_AUDIT_MISSING")
            if group == "BM" and not any(a.get("reason") == "R1_EXECUTOR_DISABLED" and a.get("route") == "/heal/trigger" and a.get("context") == ctx for a in audit):
                errors.append("BM_MANUAL_REFUSAL_AUDIT_MISSING")
    if (manual.get("status"), manual.get("body")) != (409, {"detail": "R1_EXECUTOR_DISABLED"}):
        errors.append("MANUAL_EXECUTOR_REFUSAL_MISSING")
    bm_decisions = [e for e in summary["events"]["BM"] if e["event_type"] == "DECISION"]
    if not bm_decisions or manual.get("decision_id") != bm_decisions[0]["decision_id"]:
        errors.append("MANUAL_RECEIPT_DECISION_MISMATCH")
    return {"verdict": ("PASS_BOUNDARY_OFFLINE" if offline else "PASS_BOUNDARY_ONLY") if not errors else "CHANGES_REQUIRED", "errors": errors,
            "runtime_host_acceptance": "REQUIRES_IMAGE_SOURCE_PREFLIGHT_AND_CLEANUP_RECEIPTS",
            "gaia": "NOT_TESTED", "MTTD_MTTR": "NOT_SCORED", "LLM": "NOT_CALLED"}


def attest(cfg):
    """Run inside each pod: verify actual runtime files, not just a tag or image existence."""
    actual, errors = {}, []
    for rel, expected in cfg["source_files"].items():
        if rel in {"hephaestus/Dockerfile", "hephaestus/requirements.lock"}:
            continue  # build inputs are pinned by the host build-context manifest, not copied by the image
        path = Path("/app/main.py") if rel == "hephaestus/main.py" else Path("/") / rel
        try:
            actual[rel] = digest(path.read_bytes())
        except OSError:
            errors.append(rel + ":MISSING")
            continue
        if actual[rel] != expected:
            errors.append(rel + ":SOURCE_MISMATCH")
    if digest(Path(__file__).read_bytes()) != cfg["driver_sha256"]:
        errors.append("DRIVER_MISMATCH")
    return {"python": sys.version, "files": actual, "errors": errors, "source_sha256": cfg["source_sha256"]}


def driver_server(driver):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if self.path != "/control" or not 0 < length <= 16384:
                    raise ValueError("invalid control")
                command = json.loads(self.rfile.read(length))
                action = command.get("action")
                if action == "monitor":
                    driver.start_monitor()
                    answer = {"started": True}
                elif action == "controls":
                    driver.controls()
                    answer = {"seeded": True}
                elif action == "status":
                    answer = driver.summary()
                elif action == "finish":
                    answer = driver.finish()
                else:
                    raise ValueError("unsupported control")
                data, code = encoded(answer), 200
            except Exception as error:
                data, code = encoded({"error": type(error).__name__}), 409
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    # Control is loopback-only; access through kubectl exec, never through the O Service.
    return ThreadingHTTPServer(("127.0.0.1", 9140), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan")
    prep = commands.add_parser("prepare")
    prep.add_argument("--output", required=True)
    prep.add_argument("--namespace", required=True)
    srv = commands.add_parser("driver")
    for name in ("root", "config", "keys"):
        srv.add_argument("--" + name, required=True)
    call = commands.add_parser("call")
    call.add_argument("action", choices=("monitor", "controls", "status", "finish"))
    att = commands.add_parser("attest")
    att.add_argument("--config", required=True)
    op = commands.add_parser("operator")
    for name in ("config", "keys", "token", "url", "heal-url", "output"):
        op.add_argument("--" + name, required=True)
    check = commands.add_parser("assess")
    for name in ("summary", "logs", "manual", "output"):
        check.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    load = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
    if args.command == "plan":
        print(json.dumps(specification(), indent=2))
    elif args.command == "prepare":
        print(json.dumps(prepare(args.output, args.namespace)))
    elif args.command == "driver":
        # O is authenticated and reachable only through the temporary namespace's ingress policy;
        # the unauthenticated control endpoint below remains loopback-only, reached via kubectl exec.
        driver = Driver(args.root, load(args.config), load(args.keys), bind="0.0.0.0", port=9141)  # nosec B104
        control = driver_server(driver)
        try:
            control.serve_forever()
        finally:
            control.server_close()
            driver.close()
    elif args.command == "call":
        code, body = http("http://127.0.0.1:9140/control", {"action": args.action}, timeout=30)
        print(body.decode())
        return 0 if code == 200 else 1
    elif args.command == "attest":
        answer = attest(load(args.config))
        print(json.dumps(answer))
        return 0 if not answer["errors"] else 1
    elif args.command == "operator":
        answer = operator(load(args.config), load(args.keys), load(args.token), args.url, args.heal_url)
        save(args.output, answer)
        print(json.dumps(answer))
    else:
        answer = assess(load(args.summary), load(args.logs), load(args.manual))
        save(args.output, answer)
        print(json.dumps(answer))
        return 0 if not answer["errors"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
