"""Owned private ZER-42 acceptance turn. Requires the direct 26/10 owner lab authorization.

Invoke from the Bash entry point. All operations are bounded by one 45-minute
deadline, with the last ten minutes reserved for cleanup. No existing deployment
or PVC is modified. A failure is retained and still triggers owned cleanup.
"""
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import uuid

import yaml

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from render import render

K = ["kubectl", "--context", "k3d-zero-door", "--request-timeout=15s"]
NS = "zd-sqli-lab"
RUN = "zer42-" + uuid.uuid4().hex[:12]
OUT = ROOT / "docs/evidence/ZER-42/runtime-01" / RUN
START = time.monotonic()
AUTH_EPOCH = time.time()
PARENT = None
RECOVERY = len(sys.argv) == 3 and sys.argv[1] == "--recovery-from"
CONTINUE_RECOVERY = len(sys.argv) == 3 and sys.argv[1] == "--continue-recovery-from"
MAX_SECONDS = 2100 if RECOVERY or CONTINUE_RECOVERY else 2700
if len(sys.argv) == 3 and sys.argv[1] in {"--resume-from", "--recovery-from", "--continue-recovery-from"}:
    PARENT = Path(sys.argv[2]).resolve()
    if PARENT.parent != (ROOT / ("docs/evidence/ZER-42/runtime-02" if CONTINUE_RECOVERY else "docs/evidence/ZER-42/runtime-01")).resolve():
        raise ValueError("INVALID_RESUME_PARENT")
    prior = json.loads((PARENT / "process-receipt.json").read_bytes())
    if prior["cleanup_problems"] or (PARENT / "commands.json").exists() or list((PARENT / "raw").glob("*-topic-create.json")):
        raise ValueError("RESUME_REQUIRES_CLEAN_PRE_COMMAND_ATTEMPT")
    if RECOVERY or CONTINUE_RECOVERY:
        OUT = ROOT / "docs/evidence/ZER-42/runtime-02" / RUN
        if CONTINUE_RECOVERY:
            AUTH_EPOCH = json.loads((PARENT / "authority.json").read_bytes())["authorization_start_epoch"]
    else:
        AUTH_EPOCH = (PARENT / "authority.json").stat().st_ctime
elif len(sys.argv) != 1:
    raise ValueError("INVALID_ARGUMENTS")
END = START + max(0, AUTH_EPOCH + MAX_SECONDS - time.time())
WORK_END = END - 600
namespace_uid = None
namespace_creation_attempted = False
topics_created = []
sequence = 0


def save(name, value):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2)
    with p.open("x", encoding="utf8", newline="\n") as handle:
        handle.write(text + "\n")


def command(args, *, timeout=90, stdin=None, check=True, label="command", cleanup=False, cwd=ROOT):
    global sequence
    remaining = (END if cleanup else WORK_END) - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("TURN_DEADLINE")
    sequence += 1
    result = subprocess.run(args, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=max(1, min(timeout, remaining)), cwd=cwd)
    # stdin can contain ephemeral keys. It is never logged.
    stdout_log = result.stdout.decode("utf8", "replace")
    if label == "deployments" and result.returncode == 0:
        # Existing app environments are unnecessary for replica/generation comparison.
        document = json.loads(stdout_log)
        stdout_log = json.dumps({"items": [{"metadata": {k: d["metadata"].get(k) for k in
            ("namespace", "name", "uid", "generation")}, "spec": {"replicas": d["spec"].get("replicas", 1)}}
            for d in document["items"]]})
    save(f"raw/{sequence:03}-{label}.json", {"args": args, "returncode": result.returncode,
        "stdout": stdout_log, "stderr": result.stderr.decode("utf8", "replace")})
    if check and result.returncode:
        raise RuntimeError(f"{label} exit {result.returncode}: {result.stderr.decode('utf8', 'replace')[-800:]}")
    return result


def kube(*args, **kwargs):
    return command(K + list(args), **kwargs)


def get(*args, **kwargs):
    return json.loads(kube(*args, "-o", "json", **kwargs).stdout)


def apply(docs):
    # Secret values travel only through stdin and the API, never retained in raw/evidence.
    return kube("create", "-f", "-", stdin=yaml.safe_dump_all(docs, sort_keys=False).encode(), label="create")


def snapshot(cleanup=False):
    deps = get("get", "deployments", "-A", label="deployments", cleanup=cleanup)
    pvcs = get("get", "pvc", "-A", label="pvcs", cleanup=cleanup)
    return {"deployments": {d["metadata"]["namespace"] + "/" + d["metadata"]["name"]: {
                "uid": d["metadata"]["uid"], "replicas": d["spec"].get("replicas", 1),
                "generation": d["metadata"]["generation"]} for d in deps["items"] if d["metadata"]["namespace"] != NS},
            "pvcs": {p["metadata"]["namespace"] + "/" + p["metadata"]["name"]: {
                "uid": p["metadata"]["uid"], "volume": p["spec"].get("volumeName")} for p in pvcs["items"]}}


def wait_pod(name, timeout=90):
    kube("-n", NS, "wait", "--for=condition=Ready", "pod/" + name,
         "--timeout=" + str(timeout) + "s", timeout=timeout + 10, label="wait-" + name)


def remote(pod, mode, *args):
    result = kube("-n", NS, "exec", "-i", pod, "--", "/usr/bin/python3", "-", mode, *args,
                  stdin=(HERE / "remote.py").read_bytes(), timeout=40, label="remote-" + mode)
    return json.loads(result.stdout)


def topic(operation, name, cleanup=False):
    args = ["-n", "zero-door", "exec", "kafka-controller-0", "-c", "kafka", "--",
            "/opt/bitnami/kafka/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092",
            "--" + operation, "--topic", name]
    if operation == "create":
        args += ["--partitions", "1", "--replication-factor", "1", "--config", "retention.ms=3600000"]
    return kube(*args, timeout=60, cleanup=cleanup, label="topic-" + operation)


def fixture_gate(profile):
    pod = None
    for _ in range(70):
        pods = get("-n", NS, "get", "pods", "-l", "app=sqli-fixture", label="gate-pods")
        found = [p for p in pods["items"] if not p["metadata"].get("deletionTimestamp") and
                 p["status"].get("podIP") and any(s.get("state", {}).get("running")
                     for s in p["status"].get("initContainerStatuses", []))]
        if len(found) == 1:
            pod = found[0]
            break
        time.sleep(1)
    if pod is None:
        raise RuntimeError("POLICY_GATE_POD_NOT_READY")
    name = pod["metadata"]["name"]
    gate_end = min(WORK_END, time.monotonic() + 150)
    while time.monotonic() < gate_end:
        try:
            raw = command(["docker", "exec", "k3d-zero-door-server-0", "iptables-save", "-t", "filter"],
                          label="policy", timeout=min(45, gate_end - time.monotonic()))
        except subprocess.TimeoutExpired:
            save("policy-timeout-" + str(sequence) + ".json", {"profile": profile, "terminal": False})
            continue
        needle = "POD name:" + name + " namespace: " + NS
        if needle in raw.stdout.decode("utf8", "replace"):
            kube("-n", NS, "exec", "-c", "policy-gate", name, "--", "/usr/bin/python3", "-c",
                 "from pathlib import Path; Path('/data/.policy-release').write_text('policy observed')", label="release-gate")
            break
        time.sleep(1)
    else:
        raise RuntimeError("POLICY_RULE_MISSING")
    kube("-n", NS, "rollout", "status", "deployment/sqli-fixture", "--timeout=100s", timeout=110,
         label="fixture-rollout-" + profile)
    # Pod Ready without HTTP probes is not readiness; finite proxy controls below prove the real path.
    return name


def logs(profile):
    for app in ("sqli-fixture", "zer41-private-ingress", "zer42-worker", "zer42-nemesis"):
        kube("-n", NS, "logs", "-l", "app=" + app, "--tail=500", "--prefix=false", "--timestamps=false",
             label="logs-" + profile + "-" + app)


def main():
    global namespace_uid, namespace_creation_attempted
    print("START", RUN, str(OUT), flush=True)
    baseline = snapshot()
    save("baseline.json", baseline)
    if kube("get", "ns", NS, "--ignore-not-found", "-o", "name", label="namespace-absent").stdout.strip():
        raise RuntimeError("PREEXISTING_NAMESPACE")
    nodes = get("get", "nodes", label="nodes")
    assert all(any(c["type"] == "Ready" and c["status"] == "True" for c in n["status"]["conditions"])
               and not any(c["type"] in {"MemoryPressure", "DiskPressure"} and c["status"] == "True"
                           for c in n["status"]["conditions"]) for n in nodes["items"])
    if RECOVERY:
        print("RECOVERY restart exactly k3d-zero-door-server-0 once", flush=True)
        command(["docker", "restart", "--timeout", "30", "k3d-zero-door-server-0"], timeout=100,
                label="one-approved-server-restart")
        ready_end = min(WORK_END, time.monotonic() + 240)
        while time.monotonic() < ready_end:
            try:
                current_nodes = get("get", "nodes", label="recovery-nodes")
                deployments = get("get", "deployments", "-A", label="deployments")
                pods = get("get", "pods", "-A", label="recovery-pods")
                assert all(any(c["type"] == "Ready" and c["status"] == "True"
                    for c in n["status"]["conditions"]) for n in current_nodes["items"])
                assert all(d["status"].get("readyReplicas", 0) == d["spec"].get("replicas", 1)
                           for d in deployments["items"])
                assert all(p["status"].get("phase") == "Succeeded" or all(c.get("ready")
                    for c in p["status"].get("containerStatuses", [])) and p["status"].get("phase") == "Running"
                    for p in pods["items"])
                assert snapshot() == baseline
                save("recovery-verification.json", {"verdict": "API_NODES_WORKLOADS_READY_PVC_REPLICA_MATCH",
                    "restart_count": 1, "container": "k3d-zero-door-server-0", "pvcs": baseline["pvcs"]})
                break
            except Exception:
                time.sleep(3)
        else:
            raise RuntimeError("RECOVERY_READINESS_NOT_PROVEN")
    command(["docker", "stats", "--no-stream", "--format", "{{.Name}} {{.MemUsage}} {{.CPUPerc}}"], label="docker-resources")
    # Build/import time is included in the same global turn budget.
    hashes = {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in (
        "chaos-worker/internal/attack/sqli.go", "chaos-worker/internal/validation/target.go", "chaos-worker/cmd/main.go",
        "agent-orchestrator/nemesis/main.py", "agent-orchestrator/nemesis/command_guard.py",
        "infrastructure/scripts/sqli_executor_runtime.py", "services/sqli-fixture/app.py")}
    save("source-manifest.json", hashes)
    tags = {}
    for actor, directory in (("worker", "chaos-worker"), ("nemesis", "agent-orchestrator/nemesis")):
        tag = "zer42-" + actor + ":" + hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:12]
        print("REUSE" if PARENT else "BUILD", actor, flush=True)
        if PARENT is None:
            command(["docker", "build", "--tag", tag, directory], timeout=750, label="build-" + actor)
            command(["k3d", "image", "import", "-c", "zero-door", tag], timeout=180, label="import-" + actor)
        else:
            prior_sources = json.loads((PARENT / "source-manifest.json").read_bytes())
            assert hashes == prior_sources, "SOURCE_DRIFT_ON_RESUME"
            previous_image = next((PARENT / "raw").glob("*-image-" + actor + ".json"))
            observed = command(["docker", "image", "inspect", tag, "--format", "{{.Id}}"], label="reuse-" + actor)
            assert observed.stdout.decode().strip() == json.loads(previous_image.read_bytes())["stdout"].strip()
        tags[actor] = tag
        command(["docker", "image", "inspect", tag, "--format", "{{.Id}}"], label="image-" + actor)
    docs = render(RUN, "zer41-fixture:37c7a045e098",
        "docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c",
        tags["worker"], tags["nemesis"])
    # Retain the public rendered configuration, never the ephemeral Secret values.
    save("rendered-disabled.yaml", yaml.safe_dump_all(docs, sort_keys=False))
    namespace = next(d for d in docs if d["kind"] == "Namespace")
    namespace_creation_attempted = True
    apply([namespace])
    namespace_uid = get("get", "ns", NS, label="owned-namespace")["metadata"]["uid"]
    save("namespace-owner.json", {"namespace": NS, "uid": namespace_uid, "run": RUN})
    fixture = next(d for d in docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "sqli-fixture")
    actors = [d for d in docs if d["kind"] == "Pod" and d["metadata"]["name"] in {"zer42-worker", "zer42-nemesis"}]
    bootstrap = [d for d in docs if d is not namespace and d is not fixture and d not in actors]
    apply(bootstrap)
    for name in ("zer42-source-a", "zer42-source-b"):
        wait_pod(name)
    kube("-n", NS, "rollout", "status", "deployment/zer41-private-ingress", "--timeout=90s", timeout=100, label="proxy-rollout")
    pods = get("-n", NS, "get", "pods", label="bootstrap-pods")
    proxy = next(p for p in pods["items"] if p["metadata"]["labels"].get("app") == "zer41-private-ingress")
    proxy_ip = proxy["status"]["podIP"]
    service = get("-n", NS, "get", "svc", "zer41-private-ingress", label="pinned-service")
    kube("-n", NS, "patch", "cm", "sqli-fixture-config", "--type=merge", "-p",
         json.dumps({"data": {"ZD_SQLI_TRUSTED_PROXIES": proxy_ip + "/32"}}), label="trust-proxy")
    apply([fixture])
    fixture_gate("safe")
    controls = []
    for source in ("zer42-source-a", "zer42-source-b"):
        remote(source, "direct")
        value = remote(source, "control")
        controls.append({"source": source, "value": value})
    save("source-controls-safe.json", controls)
    for name in (RUN + ".commands", RUN + ".results"):
        existing = topic("list", name).stdout.decode().strip()
        if name in existing.splitlines():
            raise RuntimeError("PREEXISTING_TOPIC")
        topics_created.append(name)
        topic("create", name)
    secrets = []
    for name, purpose in (("zer42-fault", "fault"), ("zer42-operator", "operator")):
        key = {"id": RUN + "-" + purpose, "purpose": purpose, "secret": uuid.uuid4().hex + uuid.uuid4().hex}
        secrets.append({"apiVersion": "v1", "kind": "Secret", "metadata": {"name": name,
            "namespace": NS, "labels": {"zero-door.io/run": RUN}}, "type": "Opaque",
            "stringData": {"key.json": json.dumps(key)}})
    apply(secrets)
    policy_cm = next(d for d in docs if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "zer42-policy")
    policy = json.loads(policy_cm["data"]["policy.json"])
    policy["enabled"] = True
    policy["sqli"]["enabled"] = True
    kube("-n", NS, "patch", "cm", "zer42-policy", "--type=merge", "-p",
         json.dumps({"data": {"policy.json": json.dumps(policy)}}), label="enable-policy")
    for actor in actors:
        if actor["metadata"]["name"] == "zer42-worker":
            for env in actor["spec"]["containers"][0]["env"]:
                if env["name"] == "ZD_SQLI_INGRESS_IP":
                    env["value"] = service["spec"]["clusterIP"]
    apply(actors)
    for actor in actors:
        wait_pod(actor["metadata"]["name"])
    for _ in range(20):
        state = kube("-n", "zero-door", "exec", "kafka-controller-0", "-c", "kafka", "--",
            "/opt/bitnami/kafka/bin/kafka-consumer-groups.sh", "--bootstrap-server", "localhost:9092",
            "--describe", "--state", "--group", RUN + ".worker", check=False, timeout=30, label="worker-group")
        if state.returncode == 0 and "Stable" in state.stdout.decode():
            time.sleep(3)
            break
        time.sleep(2)
    else:
        raise RuntimeError("WORKER_CONSUMER_NOT_ASSIGNED")
    for _ in range(10):
        try:
            remote("zer42-nemesis", "health")
            break
        except Exception:
            time.sleep(2)
    else:
        raise RuntimeError("NEMESIS_KAFKA_NOT_READY")
    remote("zer42-nemesis", "trigger", str(uuid.uuid4()), "invalid-control")
    ids = {}
    all_results = []
    for profile in ("safe", "vulnerable"):
        if profile == "vulnerable":
            logs("safe")
            kube("-n", NS, "patch", "cm", "sqli-fixture-config", "--type=merge", "-p",
                 json.dumps({"data": {"ZD_SQLI_PROFILE": "vulnerable"}}), label="profile-change")
            kube("-n", NS, "rollout", "restart", "deployment/sqli-fixture", label="fixture-restart")
            fixture_gate(profile)
            for source in ("zer42-source-a", "zer42-source-b"):
                remote(source, "direct")
                remote(source, "control")
        for template in ("disclose-restricted", "benign-apparel"):
            identifier = str(uuid.uuid4())
            ids[identifier] = {"profile": profile, "template": template}
            remote("zer42-nemesis", "trigger", identifier, template)
            time.sleep(5)
        records = remote("zer42-nemesis", "read", RUN + ".results")
        all_results = records
        save("results-" + profile + ".json", records)
        logs(profile)
    replay_id = next(iter(ids))
    remote("zer42-nemesis", "trigger", replay_id, ids[replay_id]["template"])
    commands = remote("zer42-nemesis", "read", RUN + ".commands")
    save("commands.json", commands)
    assert len(commands) == 4 and len(all_results) == 4, (len(commands), len(all_results))
    spec = importlib.util.spec_from_file_location("runtime", ROOT / "infrastructure/scripts/sqli_executor_runtime.py")
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    summary = []
    for record in all_results:
        result = record["value"]
        label = ids[result["commandId"]]
        sends = result["details"]["sqli"]["sends"]
        assert result["status"] == "SUCCESS" and len(sends) == 3
        expected = set(runtime.oracle_restricted()) if label == {"profile": "vulnerable", "template": "disclose-restricted"} else set()
        assert all(set(s.get("restrictedSkus", [])) == expected and not s.get("error") for s in sends)
        expected_rows = 2 if label["template"] == "benign-apparel" else len(expected)
        assert all(s["rows"] == expected_rows and s["restrictedRows"] == len(expected) for s in sends)
        context = {**policy["context"], "incident_id": runtime.contract.new_id("inc"),
            "method_version": "zer42-acceptance/1", "config_ref": "sha256:" + runtime.digest(policy)}
        bundle = runtime.prepare_bundle(result, context, OUT / (result["commandId"] + "-bundle.json"), w_eff_s=5)
        receipt = runtime.archive_bundle(bundle, OUT / (result["commandId"] + "-h-archive"),
                                         OUT / (result["commandId"] + "-export"))
        save(result["commandId"] + "-receipt.json", receipt)
        summary.append({"command_id": result["commandId"], **label, "sends": len(sends), "restricted": sorted(expected),
                        "effect": receipt["checked"][0]["status"]})
    save("cases.json", summary)
    save("pods-final.json", get("-n", NS, "get", "pods", label="pods-final"))
    logs("final")
    save("baseline-reference.json", {"baseline": "baseline.json", "pending": "independent raw/log reconciliation"})
    print("RUNTIME_COLLECTION_COMPLETE", flush=True)


def cleanup():
    problems = []
    for name in topics_created:
        try:
            topic("delete", name, cleanup=True)
            listed = topic("list", name, cleanup=True).stdout.decode().splitlines()
            if name in listed:
                raise RuntimeError("TOPIC_STILL_PRESENT")
        except Exception as error:
            problems.append(name + ": " + str(error))
    if namespace_creation_attempted:
        try:
            namespace = get("get", "ns", NS, cleanup=True, label="namespace-before-cleanup")
            assert namespace["metadata"]["labels"]["zero-door.io/run"] == RUN
            if namespace_uid is not None:
                assert namespace["metadata"]["uid"] == namespace_uid
            deletion = {"apiVersion": "v1", "kind": "DeleteOptions", "preconditions": {"uid": namespace["metadata"]["uid"]},
                        "propagationPolicy": "Foreground"}
            kube("delete", "--raw", "/api/v1/namespaces/" + NS, "-f", "-", stdin=json.dumps(deletion).encode(),
                 cleanup=True, label="delete-owned-namespace")
            kube("wait", "--for=delete", "namespace/" + NS, "--timeout=180s", cleanup=True,
                 timeout=190, label="wait-cleanup")
            assert not kube("get", "ns", NS, "--ignore-not-found", "-o", "name", cleanup=True,
                            label="verify-absent").stdout.strip()
        except Exception as error:
            problems.append("namespace: " + str(error))
    return problems


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=False)
    for script in ("run.py", "render.py", "remote.py"):
        save("scripts/" + script, (HERE / script).read_text())
    save("authority.json", {"user_approval": "Cho phép recovery/retest trong phạm vi này" if RECOVERY or CONTINUE_RECOVERY else "Cho phép lượt lab trong phạm vi này", "maximum_seconds": MAX_SECONDS,
         "cleanup_reserve_seconds": 600, "context": "k3d-zero-door", "run": RUN,
         "authorization_start_epoch": AUTH_EPOCH, "resume_from": str(PARENT) if PARENT else None})
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    status = "FAILED"
    error = None
    try:
        main()
        status = "COLLECTED_PENDING_RECONCILIATION"
    except BaseException as failure:
        error = type(failure).__name__ + ": " + str(failure)
        save("failure.txt", traceback.format_exc())
        print("FAILED", error, flush=True)
        if namespace_uid:
            try:
                logs("failure")
            except Exception:
                pass
    finally:
        issues = cleanup()
        try:
            after = snapshot(cleanup=True)
            save("after.json", after)
            before = json.loads((OUT / "baseline.json").read_bytes())
            if after != before:
                issues.append("EXISTING_WORKLOAD_OR_PVC_DRIFT")
        except BaseException as failure:
            issues.append("restoration check: " + str(failure))
        save("process-receipt.json", {"status": status, "error": error, "cleanup_problems": issues,
            "elapsed_seconds": time.monotonic() - START, "authorization_elapsed_seconds": time.time() - AUTH_EPOCH, "run": RUN})
        print("FINAL", status, "cleanup", issues, flush=True)
    raise SystemExit(0 if status == "COLLECTED_PENDING_RECONCILIATION" and not issues else 1)

