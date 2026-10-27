"""Owner-requested cleanup of four proven ZER-42 topic identities; no new test traffic.
Run via Git Bash with --cleanup. Refuses existing namespace/actors or unknown topic names.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())
HERE = Path(__file__).resolve().parent
OUT = HERE / "acceptance-final"
K = ["kubectl", "--context", "k3d-zero-door", "--request-timeout=15s"]
OWNED = {prefix + suffix for prefix in ("zer42-c2d30a7145ff", "zer42-15ddc1ba1c91")
         for suffix in (".commands", ".results")}
END = 0
SEQ = 0


def write(name, value):
    with (OUT / name).open("x", encoding="utf8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def run(args, label, sanitize=None):
    global SEQ
    left = END - time.monotonic()
    if left <= 0:
        raise TimeoutError("CLEANUP_DEADLINE")
    result = subprocess.run(args, capture_output=True, timeout=min(35, left), cwd=ROOT)
    text = result.stdout.decode("utf8", "replace")
    if result.returncode == 0 and sanitize:
        text = json.dumps(sanitize(json.loads(text)))
    SEQ += 1
    write("live-%02d-%s.json" % (SEQ, label), {"at": datetime.now(timezone.utc).isoformat(),
          "args": args, "returncode": result.returncode, "stdout": text,
          "stderr": result.stderr.decode("utf8", "replace")})
    if result.returncode:
        raise RuntimeError(label + " failed")
    return text


def topic(op, name=None):
    args = K + ["-n", "zero-door", "exec", "kafka-controller-0", "-c", "kafka", "--",
        "env", "-u", "JMX_PORT", "-u", "KAFKA_JMX_OPTS",
        "/opt/bitnami/kafka/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--" + op]
    if name:
        args += ["--topic", name]
    return run(args, "topic-" + op)


def snapshot():
    deps = json.loads(run(K + ["get", "deployments", "-A", "-o", "json"], "deployments",
        lambda data: {"items": [{"metadata": {k: d["metadata"][k] for k in ("namespace", "name", "uid", "generation")},
                               "replicas": d["spec"].get("replicas", 1)} for d in data["items"]]}))
    pvcs = json.loads(run(K + ["get", "pvc", "-A", "-o", "json"], "pvcs",
        lambda data: {"items": [{"namespace": p["metadata"]["namespace"], "name": p["metadata"]["name"],
            "uid": p["metadata"]["uid"], "volume": p["spec"].get("volumeName")} for p in data["items"]]}))
    return {"deployments": {d["metadata"]["namespace"] + "/" + d["metadata"]["name"]:
            {"uid": d["metadata"]["uid"], "generation": d["metadata"]["generation"], "replicas": d["replicas"]}
            for d in deps["items"]}, "pvcs": {p["namespace"] + "/" + p["name"]:
            {"uid": p["uid"], "volume": p["volume"]} for p in pvcs["items"]}}


def main():
    global END
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleanup", action="store_true", required=True)
    parser.parse_args()
    OUT.mkdir(exist_ok=False)
    END = time.monotonic() + 240
    write("authority.json", {"at": datetime.now(timezone.utc).isoformat(), "maximum_seconds": 240,
          "scope": "existing local lab cleanup requested 27/10/2026; four exact owned topics only",
          "topics": sorted(OWNED), "new_test_requests": 0})
    # Prove provenance using successful creates or the historical accidental consumer read.
    proof = {}
    for prefix, marker in (("zer42-c2d30a7145ff", "topic-create"), ("zer42-15ddc1ba1c91", "remote-read")):
        attempt = HERE / ("zer42-74545a02be28" if marker == "topic-create" else prefix)
        for name in sorted(n for n in OWNED if n.startswith(prefix)):
            matches = [p for p in (attempt / "raw").glob("*-" + marker + ".json")
                       if name in json.loads(p.read_bytes())["args"] and json.loads(p.read_bytes())["returncode"] == 0]
            if not matches:
                raise ValueError("OWNERSHIP_NOT_PROVEN")
            proof[name] = [p.relative_to(ROOT).as_posix() for p in matches]
    write("topic-ownership.json", proof)
    if run(["docker", "context", "show"], "docker-context").strip() != "desktop-linux":
        raise ValueError("WRONG_DOCKER_CONTEXT")
    if run(K + ["get", "ns", "zd-sqli-lab", "--ignore-not-found", "-o", "name"], "namespace-absent").strip():
        raise ValueError("NAMESPACE_STILL_ACTIVE")
    pods = json.loads(run(K + ["get", "pods", "-A", "-o", "json"], "pods",
        lambda data: {"items": [{"namespace": p["metadata"]["namespace"], "name": p["metadata"]["name"],
            "phase": p["status"]["phase"], "run": p["metadata"].get("labels", {}).get("zero-door.io/run")}
            for p in data["items"]]}))
    if any(p["name"].startswith("zer42-") or p["run"] for p in pods["items"]):
        raise ValueError("OWNED_ACTOR_STILL_ACTIVE")
    before = snapshot()
    write("cleanup-before.json", before)
    historical = json.loads((HERE / "zer42-74545a02be28/after.json").read_bytes())
    if before != historical:
        raise ValueError("BASELINE_DRIFT_REQUIRES_REVIEW")
    initial = set(topic("list").splitlines())
    for name in sorted(OWNED & initial):
        topic("describe", name)
        topic("delete", name)
    while True:
        remaining = set(topic("list").splitlines())
        if not remaining & OWNED:
            break
        if END - time.monotonic() < 40:
            raise ValueError("TOPIC_CLEANUP_UNRESOLVED")
        time.sleep(2)
    if initial - OWNED != remaining:
        raise ValueError("UNRELATED_TOPIC_SET_CHANGED")
    after = snapshot()
    if after != before:
        raise ValueError("RESTORATION_MISMATCH")
    if run(K + ["get", "ns", "zd-sqli-lab", "--ignore-not-found", "-o", "name"], "namespace-still-absent").strip():
        raise ValueError("NAMESPACE_REAPPEARED")
    write("cleanup-receipt.json", {"status": "CLEAN", "at": datetime.now(timezone.utc).isoformat(),
          "owned_topics_absent": sorted(OWNED), "namespace_absent": True, "existing_snapshot_unchanged": True,
          "historical_after_snapshot_matches": True, "pvc_count": len(after["pvcs"]),
          "unrelated_topics_unchanged": sorted(remaining), "snapshot": after, "new_test_requests": 0})
    print("CLEAN: four exact owned topics absent; namespace absent; replicas/generations/PVC3 preserved")


if __name__ == "__main__":
    main()
