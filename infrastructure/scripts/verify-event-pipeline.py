"""Bounded ZER-9 transport/access verification. No fault/heal/LLM is executed."""
import argparse
import ast
import asyncio
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, canonical, new_id, now
from event_pipeline.client import Client
from event_pipeline.adapters import RulesConsumer
from event_pipeline.audit import audit
from event_pipeline.store import sha


def command(args, data=None, timeout=90):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError("command failed: " + " ".join(args[:5]) + " " + result.stderr.decode(errors="replace")[-1500:])
    return result.stdout


def post(url, key, event, path="/events"):
    request = Request(url + path, data=canonical(event), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def forward(kube, namespace, service):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    proc = subprocess.Popen(kube + ["-n", namespace, "port-forward", "svc/" + service, f"{port}:8000", "--address", "127.0.0.1"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    until = time.monotonic() + 15
    while time.monotonic() < until:
        if proc.poll() is not None:
            raise RuntimeError("owned port-forward exited")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return proc, "http://127.0.0.1:" + str(port)
        except OSError:
            time.sleep(0.2)
    proc.terminate()
    proc.wait(timeout=5)
    raise TimeoutError("port-forward startup")


def wait_records(client, ids):
    until = time.monotonic() + 20
    while time.monotonic() < until:
        rows = list(client.records())
        if ids <= {r["envelope"]["event_id"] for r in rows}:
            return rows
        time.sleep(0.2)
    raise TimeoutError("durable recorder receipts missing")


def import_agent(name, keys_file):
    # Each agent loads its OWN key file at import; the client refuses a file with another actor's role.
    os.environ["ZD_O_KEYS_FILE"] = str(keys_file)
    spec = importlib.util.spec_from_file_location("zer9_" + name, ROOT / "agent-orchestrator" / name / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def actor_key_files(o_keys):
    """One Secret per O actor (ZR9-04). No file carries two producer roles, harness or evaluator."""
    return {"event-o-gaia": {k: o_keys[k] for k in ("detector", "reader")},
            "event-o-hephaestus": {k: o_keys[k] for k in ("decision_rules", "reader")},
            "event-o-observer": {"reader": o_keys["reader"]}}


def harness_manifest(namespace, topic, image, nonce):
    """Contract 8.3(4): declare every value the harness created that O may see (ZR9-13)."""
    def entry(kind, value, visible):
        return {"kind": kind, "value": value, "class": "NEUTRAL", "o_visible": visible}
    return {"manifest_version": "zer9/2", "allowlist_version": "zer9/2", "reveal_terms": ["stress"],
            "entries": [entry("namespace", namespace, True), entry("topic", topic, True),
                        entry("image", image, False), entry("nonce", nonce, True),
                        entry("pod", "o-access-probe", False), entry("pod", "topic-cleanup", False),
                        entry("pvc", "raw-o", False), entry("pvc", "raw-h", False),
                        entry("secret", "event-o-observer", False), entry("secret", "event-o-gaia", False),
                        entry("secret", "event-o-hephaestus", False), entry("configmap", "event-queries", False),
                        entry("header", "request_id", True), entry("header", "signature", True)]}


def synthetic_truth(harness, ctx):
    """In-memory only, never posted to H: exercises the label path of the audit on live O."""
    return harness.event(ctx, "GROUND_TRUTH_LOCKED", {
        "variant_id": "v1", "case_class": "C4", "cause": "cpu_exhaustion", "attack_type": "cpu-hog",
        "decision_required": True, "acceptable_actions": ["SCALE_UP"], "constraints": [],
        "label_version": "zer9-audit-control-synthetic", "reviewers": [], "locked_at": now()}, "h.label")


def leak_controls(h_events, o_events, detection, surfaces, access_complete, harness, ctx):
    """Clean trace plus three injected controls; stream/target controls are caught ONLY by the label path."""
    labelled = h_events + [synthetic_truth(harness, ctx)]
    clean = audit(labelled, o_events, surfaces=surfaces, access_complete=access_complete)
    by_id = copy.deepcopy(detection)
    by_id["incident_id"] = "inc_cpu-stress-case-1"
    by_stream = copy.deepcopy(detection)
    by_stream["stream"] = "o.alert.stress"
    by_target = copy.deepcopy(detection)
    by_target["target"]["service"] = "frontend-c4"
    return {"labels_in_memory": "GROUND_TRUTH_LOCKED synthetic, not posted to H",
            "clean": clean,
            "injected_incident_id": audit(labelled, [by_id], access_complete=True),
            "injected_stream_valid_ids": audit(labelled, [by_stream], access_complete=True),
            "injected_target_valid_ids": audit(labelled, [by_target], access_complete=True)}


def seal_with_retry(url, key, run, attempts=10):
    """409 SEAL_PENDING is not a seal. Retry within a bound, then fail."""
    history = []
    for attempt in range(attempts):
        try:
            return post(url, key, {"run_id": run}, "/seal"), history
        except HTTPError as error:
            if error.code != 409:
                raise
            history.append({"attempt": attempt, "code": 409, "at": now()})
            time.sleep(1)
    raise TimeoutError("seal still pending after bounded retries: " + json.dumps(history))


def delete_owned_topic(kube, namespace, image, topic):
    """Stop the subscribing recorder before deletion, preventing automatic topic recreation."""
    command(kube + ["-n", namespace, "scale", "deployment/events-o", "--replicas=0"])
    until = time.monotonic() + 120
    while json.loads(command(kube + ["-n", namespace, "get", "pods", "-l", "app=events-o", "-o", "json"]))["items"]:
        if time.monotonic() >= until:
            raise TimeoutError("owned recorder has not stopped; do not delete its topic")
        time.sleep(1)
    code = ("import json,time;from kafka.admin import KafkaAdminClient;"
            "c=KafkaAdminClient(bootstrap_servers='kafka.zero-door.svc.cluster.local:9092');t=" + repr(topic) + ";"
            "c.delete_topics([t]) if t in c.list_topics() else None;"
            "deadline=time.monotonic()+30\n"
            "while t in c.list_topics() and time.monotonic()<deadline:time.sleep(1)\n"
            "assert t not in c.list_topics();c.close();print(json.dumps({'topic_absent':t}))")
    pod = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "topic-cleanup", "namespace": namespace, "labels": {"app": "events-o"}},
           "spec": {"restartPolicy": "Never", "nodeSelector": {"kubernetes.io/hostname": "k3d-zero-door-server-0"}, "automountServiceAccountToken": False, "serviceAccountName": "event-observer",
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 65532, "runAsGroup": 65532},
                    "containers": [{"name": "cleanup", "image": image, "imagePullPolicy": "Never", "command": ["/usr/bin/python3", "-c", code],
                                    "securityContext": {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True, "capabilities": {"drop": ["ALL"]}},
                                    "resources": {"requests": {"cpu": "10m", "memory": "16Mi"}, "limits": {"cpu": "100m", "memory": "64Mi"}}}]}}
    command(kube + ["create", "-f", "-"], canonical(pod))
    until = time.monotonic() + 90
    while time.monotonic() < until:
        status = json.loads(command(kube + ["-n", namespace, "get", "pod", "topic-cleanup", "-o", "json"]))["status"].get("phase")
        if status in {"Succeeded", "Failed"}:
            break
        time.sleep(1)
    logs = command(kube + ["-n", namespace, "logs", "topic-cleanup"]).decode()
    if status != "Succeeded" or json.loads(logs) != {"topic_absent": topic}:
        raise RuntimeError("topic cleanup not confirmed: " + logs[-500:])
    return {"topic_absent": topic}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="create a NEW isolated namespace, two small recorders and an observer; export and remove only owned resources")
    parser.add_argument("--allow-temporary-es-ingress", action="store_true", help="separately authorized: add/delete one namespace+pod-scoped Elasticsearch ingress rule in monitoring")
    parser.add_argument("--output", default="scratch/zer9/live", help="new receipt/export directory; must not exist")
    args = parser.parse_args()
    if not __debug__:
        parser.error("verification requires assertions enabled (no -O/PYTHONOPTIMIZE)")
    if not args.live:
        parser.error("--live is required; offline checks: python -B tests/test_event_pipeline.py")
    import yaml
    output = (ROOT / args.output).resolve()
    if ROOT not in output.parents:
        parser.error("output must be inside this checkout")
    output.mkdir(parents=True, exist_ok=False)
    kube = ["kubectl", "--context", "k3d-zero-door", "--request-timeout=15s"]
    docker = ["docker", "--context", "desktop-linux"]
    nonce = secrets.token_hex(6)
    namespace, topic = "zd-zer9-" + nonce, "zd.events.o." + nonce
    checks, forwards, env_before = {}, [], dict(os.environ)
    receipt = {"started_at": now(), "kind": "LIVE_TRANSPORT_SYNTHETIC_PAYLOADS", "namespace": namespace,
               "topic": topic, "checks": checks, "verdict": "UNKNOWN"}
    try:
        # New namespace only. Never overwrite or clean up a pre-existing namespace/PVC.
        namespaces = json.loads(command(kube + ["get", "namespaces", "-o", "json"]))
        if namespace in {n["metadata"]["name"] for n in namespaces["items"]}:
            raise RuntimeError("namespace already exists")
        receipt["node_usage"] = command(kube + ["top", "nodes"]).decode()
        if any(int(line.split()[-1].strip("%")) > 80 for line in receipt["node_usage"].splitlines()[1:] if line.strip()):
            raise RuntimeError("node memory above 80%; stop before build/deploy")
        sources = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in (ROOT / "agent-orchestrator/event_pipeline").glob("*.py")}
        sources.update({str(ROOT.joinpath("agent-orchestrator", name, "main.py").relative_to(ROOT)):
                        sha((ROOT / "agent-orchestrator" / name / "main.py").read_bytes()) for name in ("gaia", "hephaestus")})
        receipt["source_hashes"] = sources
        tag = sha(canonical(sources))[:16]
        image = "zero-door/events:zer9-" + tag
        build = output / "build"
        build.mkdir()
        (build / "event_pipeline").mkdir()
        for path in (ROOT / "agent-orchestrator/event_pipeline").glob("*.py"):
            (build / "event_pipeline" / path.name).write_bytes(path.read_bytes())
        base = command(docker + ["image", "inspect", "zero-door/gaia:latest", "--format", "{{.Id}}"]).decode().strip()
        base_tag = "zero-door/events-base:zer9-" + base.removeprefix("sha256:")[:16]
        command(docker + ["tag", base, base_tag])
        receipt["base_image_id"] = base
        # BuildKit resolves a named local tag; a bare sha256 ID is parsed as a registry repository.
        # Existing nonroot image has kafka-python. COPY-only build: no dependency install.
        (build / "Dockerfile").write_text(f'FROM {base_tag}\nCOPY event_pipeline /app/event_pipeline\nENTRYPOINT ["/usr/bin/python3", "-m", "event_pipeline.gateway"]\n')
        command(docker + ["build", "--pull=false", "--network=none", "-t", image, str(build)], timeout=180)
        receipt["image"] = image
        receipt["image_id"] = command(docker + ["image", "inspect", image, "--format", "{{.Id}}"]).decode().strip()
        command(["k3d", "image", "import", "--cluster", "zero-door", image], timeout=180)
        documents = list(yaml.safe_load_all((ROOT / "infrastructure/manifests/r1-event-pipeline.yaml").read_text()))
        for document in documents:
            if document["kind"] == "Namespace":
                document["metadata"]["name"] = namespace
                document["metadata"]["labels"]["zero-door-verification"] = nonce
            else:
                document["metadata"]["namespace"] = namespace
            if document["kind"] == "Deployment":
                container = document["spec"]["template"]["spec"]["containers"][0]
                container["image"] = image
                if document["metadata"]["name"] == "events-o":
                    container["args"] += ["--topic", topic]
        command(kube + ["apply", "-f", "-"], yaml.safe_dump(documents[0]).encode())
        namespace_uid = json.loads(command(kube + ["get", "namespace", namespace, "-o", "json"]))["metadata"]["uid"]
        o_keys = {role: secrets.token_hex(32) for role in ("harness", "detector", "decision_rules", "reader", "evaluator")}
        h_keys = {role: secrets.token_hex(32) for role in ("harness", "evaluator")}
        private = output / "private"
        private.mkdir(mode=0o700)
        for name, keys in [("event-o-server", o_keys), ("event-h-server", h_keys)] + list(actor_key_files(o_keys).items()):
            path = private / (name + ".json")
            path.write_bytes(canonical(keys))
            path.chmod(0o600)
            command(kube + ["-n", namespace, "create", "secret", "generic", name, "--from-file=keys.json=" + str(path)])
        gaia_ast = ast.parse((ROOT / "agent-orchestrator/gaia/main.py").read_text())
        queries = [node.value.value for node in ast.walk(gaia_ast) if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                   and isinstance(node.value.value, str) and any(isinstance(t, ast.Name) and t.id.endswith("_query") and t.id != "query" for t in node.targets)]
        query_file = private / "queries.json"
        query_file.write_bytes(canonical(queries))
        command(kube + ["-n", namespace, "create", "configmap", "event-queries", "--from-file=queries.json=" + str(query_file)])
        command(kube + ["apply", "-f", "-"], yaml.safe_dump_all(documents[1:]).encode())
        es_policy = None
        if args.allow_temporary_es_ingress:
            es_policy = "zd-zer9-" + nonce
            policy = {"apiVersion": "networking.k8s.io/v1", "kind": "NetworkPolicy",
                      "metadata": {"name": es_policy, "namespace": "monitoring", "labels": {"zero-door-verification": nonce}},
                      "spec": {"podSelector": {"matchLabels": {"app": "elasticsearch"}}, "policyTypes": ["Ingress"],
                               "ingress": [{"from": [{"namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": namespace}},
                                                       "podSelector": {"matchLabels": {"app": "events-o"}}}],
                                            "ports": [{"protocol": "TCP", "port": 9200}]}]}}
            command(kube + ["create", "-f", "-"], canonical(policy))
            policy_uid = json.loads(command(kube + ["-n", "monitoring", "get", "networkpolicy", es_policy, "-o", "json"]))["metadata"]["uid"]
            receipt["temporary_es_policy"] = {"name": es_policy, "uid": policy_uid, "namespace": "monitoring"}
        for service in ("events-o", "events-h"):
            command(kube + ["-n", namespace, "rollout", "status", "deployment/" + service, "--timeout=120s"], timeout=130)
            proc, url = forward(kube, namespace, service)
            forwards.append(proc)
            if service == "events-o":
                o_url = url
            else:
                h_url = url
        ctx = {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"), "group": "B1",
               "method_version": "zer9-transport-verification-not-kpi", "config_ref": "sha256:" + tag * 4}
        receipt["context"] = ctx
        os.environ.update(ZD_EVENT_URL=o_url, ZD_O_KEYS_FILE=str(private / "event-o-gaia.json"),
                          ZD_RUN_ID=ctx["run_id"], ZD_TRIAL_ID=ctx["trial_id"], ZD_PRODUCER_VERSION=tag,
                          ZD_CLOCK_ID="clk_windows_transport", ZD_CLOCK_SOURCE="UNKNOWN")
        client = Client.from_env("detector")
        harness = Producer("harness", tag, {"clock_id": "clk_windows_transport", "clock_source": "UNKNOWN", "resolution_ms": None})
        run = dict(ctx, trial_id=None)
        run.pop("incident_id")
        # Reader principal cannot reach H API or arbitrary Kafka/telemetry from an O pod.
        probe = '''import json,socket,os
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
keys=json.load(open('/keys/keys.json'))
import time
# No trial data is admitted until the controller's actual access state passes three rounds.
base='http://events-o:8000'
request=Request(base+'/events?run_id=RUN_ID',headers={'Authorization':'Bearer '+keys['reader']})
history=[]
streak=0
for attempt in range(40):
 opened=[]
 try: assert urlopen(request,timeout=3).status==200
 except (URLError,TimeoutError,ConnectionError,AssertionError): opened.append('O_API_NOT_READY')
 for host,port in [('events-h',8000),('kafka.zero-door.svc.cluster.local',9092),('elasticsearch.monitoring.svc.cluster.local',9200),('prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local',9090)]:
  assert socket.getaddrinfo(host,port), 'negative control must resolve DNS'
  try:
   with socket.create_connection((host,port),timeout=2):opened.append(host)
  except (TimeoutError,ConnectionError,OSError):pass
 history.append({'attempt':attempt,'open':opened})
 streak=streak+1 if not opened else 0
 if streak==3:break
 time.sleep(2)
assert streak==3, history
for path in ['/H','/export','/raw','/events?run_id=../H','/events?run_id=RUN_ID&plane=H']:
 try: urlopen(Request(base+path,headers={'Authorization':'Bearer '+keys['reader']}),timeout=3);raise AssertionError(path)
 except HTTPError as e: assert e.code in (400,403,404)
assert not os.path.exists('/raw-h') and not os.path.exists('/raw-o')
assert not os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token')
assert set(keys)=={'reader'}, 'observer key file must hold only reader'
print(json.dumps({'history':history,'checks':{'o_api':True,'h_api_denied':True,'direct_broker_denied':True,'direct_telemetry_denied':True,'h_raw_unmounted':True,'no_h_credentials_or_kube_token':True}}))
'''.replace("RUN_ID", ctx["run_id"])
        pod = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "o-access-probe", "namespace": namespace, "labels": {"role": "observer", "plane": "O"}},
               "spec": {"restartPolicy": "Never", "nodeSelector": {"kubernetes.io/hostname": "k3d-zero-door-server-0"}, "automountServiceAccountToken": False, "serviceAccountName": "event-observer",
                        "securityContext": {"runAsNonRoot": True, "runAsUser": 65532, "runAsGroup": 65532},
                        "containers": [{"name": "probe", "image": image, "imagePullPolicy": "Never", "command": ["/usr/bin/python3", "-c", probe],
                        "resources": {"requests": {"cpu": "10m", "memory": "16Mi"}, "limits": {"cpu": "100m", "memory": "64Mi"}},
                        "securityContext": {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True, "capabilities": {"drop": ["ALL"]}},
                        "volumeMounts": [{"name": "keys", "mountPath": "/keys", "readOnly": True}]}],
                        "volumes": [{"name": "keys", "secret": {"secretName": "event-o-observer"}}]}}
        command(kube + ["apply", "-f", "-"], canonical(pod))
        until = time.monotonic() + 150
        while time.monotonic() < until:
            result = json.loads(command(kube + ["-n", namespace, "get", "pod", "o-access-probe", "-o", "json"]))
            if result["status"].get("phase") in {"Succeeded", "Failed"}:
                break
            time.sleep(1)
        assert result["status"].get("phase") == "Succeeded", command(kube + ["-n", namespace, "logs", "o-access-probe"]).decode()
        access_result = json.loads(command(kube + ["-n", namespace, "logs", "o-access-probe"]))
        receipt["access_gate_observations"] = access_result["history"]
        checks.update(access_result["checks"])
        checks["access_gate_before_trial_data"] = True
        for event in (harness.event(run, "RUN_CONTEXT", {}, "o.context"), harness.event(ctx, "TRIAL_CONTEXT", {}, "o.context")):
            post(o_url, o_keys["harness"], event)
            wait_records(client, {event["event_id"]})
        canary = "canary-" + secrets.token_hex(16)
        h_events = [harness.event(run, "RUN_STARTED", {"canary_token": canary, "protocol_ref": "transport-only",
                    "schedule_ref": "sha256:" + "0" * 64,
                    "f01_params": {"delta_s": 1, "k": 3, "s_s": 30, "l_ms": 1000, "gap_s": 2, "epsilon_s": 0.1, "cap_det_s": 60, "cap_rec_s": 180},
                    "reference_clock_id": "UNKNOWN"}, "h.control"),
                    harness.event(ctx, "HARNESS_MANIFEST", harness_manifest(namespace, topic, image, nonce), "h.audit")]
        for event in h_events:
            post(h_url, h_keys["harness"], event)
        # Boundary of this profile (ZR9-05): both agents run in THIS host process over port-forward;
        # the access gate above proves isolation for the observer pod only, not for these processes.
        receipt["agent_execution"] = "HOST_PROCESS_VIA_PORT_FORWARD; access gate subject: observer pod"
        gaia = import_agent("gaia", private / "event-o-gaia.json")
        healer = import_agent("hephaestus", private / "event-o-hephaestus.json")
        async def metrics_query():
            async with __import__("httpx").AsyncClient() as http_client:
                return await gaia.query_prometheus(http_client, queries[0])
        telemetry_attempts = []
        for attempt in range(3):
            try:
                metrics = asyncio.run(metrics_query())
                assert metrics and metrics.get("status") == "success" and metrics["data"]["result"]
                logs = post(o_url, o_keys["detector"], {"query": {"match_all": {}}, "size": 1}, "/elasticsearch/zero-door-logs-*/_search")
                telemetry_attempts.append({"attempt": attempt, "result": "SUCCESS"})
                break
            except (AssertionError, HTTPError, URLError, TimeoutError) as error:
                telemetry_attempts.append({"attempt": attempt, "result": type(error).__name__, "at": now()})
                receipt["telemetry_attempts"] = telemetry_attempts
                if attempt == 2:
                    raise
                time.sleep(2)
        receipt["telemetry_attempts"] = telemetry_attempts
        assert logs["hits"]["hits"], "positive control requires at least one target-app log"
        assert all(hit["_source"]["kubernetes"]["namespace_name"] == "target-app" for hit in logs["hits"]["hits"])
        surfaces = [{"source_component": "detector", "field": "query", "text": queries[0]},
                    {"source_component": "detector", "field": "query_result", "text": canonical(metrics).decode()},
                    {"source_component": "detector", "field": "query_result", "text": canonical(logs).decode()}]
        receipt["query_surfaces"] = surfaces
        checks["bounded_real_telemetry_queries"] = True
        try:
            post(o_url, h_keys["harness"], h_events[0])
            raise AssertionError("H token accepted by O")
        except HTTPError as error:
            assert error.code == 401
        checks["h_credential_rejected_by_o"] = True
        gaia.publish_alert("HIGH_CPU", "frontend", "transport_fixture", 90.0, 80.0,
                           "Synthetic transport verification, no workload effect", "WARNING")
        detection = next(r["envelope"] for r in client.records() if r["envelope"]["event_type"] == "DETECTED")
        rules = RulesConsumer(healer.r1_client, healer.decide_action)
        rules.poll()
        rows = list(client.records())
        decision = next(r["envelope"] for r in rows if r["envelope"]["event_type"] == "DECISION")
        assert decision["causation_id"] == detection["event_id"]
        assert decision["incident_id"] == detection["incident_id"] == ctx["incident_id"]
        assert decision["payload"]["inputs"][0]["event_id"] == detection["event_id"]
        checks["actual_gaia_to_kafka_to_hephaestus_decision"] = True
        client.publish(detection)  # Exact envelope redelivery, not a new detection.
        rules = RulesConsumer(healer.r1_client, healer.decide_action)
        rules.poll()
        rows = list(client.records())
        assert sum(r["envelope"]["event_type"] == "DECISION" for r in rows) == 1
        assert sum(r["envelope"]["event_id"] == detection["event_id"] for r in rows) == 2
        checks["redelivery_and_consumer_restart_dedup"] = True
        assert all(r["transport"]["kind"] == "kafka" for r in rows)
        assert all(r["transport"]["http_request_id"] for r in rows)
        assert not any(r["envelope"]["event_type"] in {"HEAL_STARTED", "ACTION_COMPLETED", "RECOVERY_VERIFIED"} for r in rows)
        checks["http_kafka_provenance_and_no_synthetic_recovery"] = True
        # Actual pods, separate UIDs/PVCs and no mounts of the other plane.
        receipt["pods"] = json.loads(command(kube + ["-n", namespace, "get", "pods", "-o", "json"]))
        assert all(p["spec"]["nodeName"] == "k3d-zero-door-server-0" for p in receipt["pods"]["items"])
        checks["verified_node_placement"] = True
        for dep, expected in (("events-o", "raw-o"), ("events-h", "raw-h")):
            pod_info = next(p for p in receipt["pods"]["items"] if p["metadata"].get("labels", {}).get("app") == dep)
            claims = [v["persistentVolumeClaim"]["claimName"] for v in pod_info["spec"]["volumes"] if "persistentVolumeClaim" in v]
            assert claims == [expected]
        checks["separate_pvc_and_identity"] = True
        before = {r["envelope"]["event_id"] for r in rows}
        forwards[0].terminate()
        forwards[0].wait(timeout=5)
        command(kube + ["-n", namespace, "rollout", "restart", "deployment/events-o"])
        command(kube + ["-n", namespace, "rollout", "status", "deployment/events-o", "--timeout=120s"], timeout=130)
        proc, o_url = forward(kube, namespace, "events-o")
        forwards.append(proc)
        client.url = o_url
        rows = wait_records(client, before)
        checks["recorder_restart_retains_raw"] = True
        transport = [{"source_component": "recorder", "field": "transport." + key, "text": str(r["transport"][key])}
                     for r in rows for key in ("topic", "http_request_id")]
        controls = leak_controls(h_events, [r["envelope"] for r in rows], detection, surfaces + transport,
                                 all(checks.values()), harness, ctx)
        assert controls["clean"]["result"] == "CLEAN", controls["clean"]
        assert {"INVALID_ID", "LABEL_IN_METADATA"} <= set(controls["injected_incident_id"]["findings"])
        assert controls["injected_stream_valid_ids"]["findings"] == ["LABEL_IN_METADATA"]
        assert controls["injected_target_valid_ids"]["findings"] == ["LABEL_IN_METADATA"]
        checks["clean_and_injected_label_leak_controls"] = True
        receipt["leak_audit"] = controls
        # Seal only after receipt convergence, export from privileged evaluator filesystem view.
        for plane, url, keys in (("O", o_url, o_keys), ("H", h_url, h_keys)):
            manifest, pending = seal_with_retry(url, keys["evaluator"], ctx["run_id"])
            receipt.setdefault("seal_pending", {})[plane] = pending
            directory = output / "export" / plane
            directory.mkdir(parents=True)
            code = f"import sys;sys.stdout.buffer.write(open('/raw-{plane.lower()}/{ctx['run_id']}/{plane}.jsonl','rb').read())"
            data = command(kube + ["-n", namespace, "exec", "deployment/events-" + plane.lower(), "--", "/usr/bin/python3", "-c", code])
            assert sha(data) == manifest["sha256"]
            (directory / (plane + ".jsonl")).write_bytes(data)
            (directory / "manifest.json").write_bytes(canonical(manifest) + b"\n")
            for path in directory.iterdir():
                path.chmod(0o444)
            receipt.setdefault("exports", {})[plane] = manifest
        checks["sealed_export_matches_pvc_hashes"] = True
        # Topic belongs only to this nonce. Delete after both raw exports have been verified.
        receipt["topic_cleanup"] = delete_owned_topic(kube, namespace, image, topic)
        checks["topic_cleanup_confirmed_after_export"] = True
        current = json.loads(command(kube + ["get", "namespace", namespace, "-o", "json"]))
        if current["metadata"]["uid"] != namespace_uid or current["metadata"]["labels"].get("zero-door-verification") != nonce:
            raise RuntimeError("cleanup ownership mismatch; stop")
        if es_policy:
            current_policy = json.loads(command(kube + ["-n", "monitoring", "get", "networkpolicy", es_policy, "-o", "json"]))
            if current_policy["metadata"]["uid"] != policy_uid or current_policy["metadata"]["labels"].get("zero-door-verification") != nonce:
                raise RuntimeError("temporary Elasticsearch policy ownership mismatch")
            command(kube + ["-n", "monitoring", "delete", "networkpolicy", es_policy])
            receipt["temporary_es_policy"]["deleted"] = True
        command(kube + ["delete", "namespace", namespace, "--wait=false"])
        receipt["cleanup_requested"] = True
        receipt["verdict"] = "PASS"
    except Exception as error:
        receipt["verdict"] = "FAIL"
        receipt["error"] = type(error).__name__ + ": " + str(error)
        raise
    finally:
        for proc in forwards:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
        os.environ.clear()
        os.environ.update(env_before)
        receipt["finished_at"] = now()
        # Never publish private key files or full Pod specs with accidental secret values.
        (output / "receipt.json").write_bytes(canonical(receipt) + b"\n")
        print(json.dumps({"receipt": str(output / "receipt.json"), "verdict": receipt["verdict"], "checks": len(checks)}))


if __name__ == "__main__":
    main()
