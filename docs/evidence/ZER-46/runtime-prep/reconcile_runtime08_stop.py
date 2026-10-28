"""Offline reconciliation of guard-stopped runtime08; never treats missing response as zero traffic."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-08"
spec = importlib.util.spec_from_file_location("zer46_r08_helpers", Path(__file__).with_name("reconcile_runtime03.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def read(name): return json.loads((OUT / name).read_text())


def main():
    raw = [json.loads(p.read_text()) for p in sorted((OUT / "raw").glob("*.json"))]
    assert not any(r["args"][:4] in (["docker", "--context", "desktop-linux", op] for op in ("build", "pull")) or
                   r["args"][:3] == ["k3d", "image", "import"] for r in raw)
    assert not list(OUT.glob("http-*.json")) and not list(OUT.glob("join-*.json"))
    assert not list(OUT.glob("writer-[12].json")) and not (OUT / "original-rule.json").exists()
    clients = [r for r in raw if r["args"][0] == "kubectl" and "exec" in r["args"] and
               any("urllib.request" in x for x in r["args"])]
    assert len(clients) == 1 and "MEMORY_STOP" in clients[0]["error"] and "returncode" not in clients[0]
    correlation = json.loads(clients[0]["args"][-1])["correlation"]
    log_rows = [r for r in raw if "logs" in r["args"] and any(x.startswith("pod/sqli-fixture-") for x in r["args"])]
    assert log_rows and all(correlation not in r.get("stdout", "") for r in log_rows)
    initial = read("fixture-initial.json")
    assert initial["spec"]["nodeName"] == "k3d-zero-door-agent-0"
    assert any(c["type"] == "Ready" and c["status"] == "True" for c in initial["status"]["conditions"])
    target = read("log-pod-target-001.json")
    assert target["uid"] == initial["metadata"]["uid"]
    created, deleted = read("namespace-created.json"), read("namespace-delete-options.json")
    assert deleted["preconditions"]["uid"] == created["metadata"]["uid"]
    absent = [r for r in raw if r["args"][0] == "kubectl" and "namespace" in r["args"] and "--ignore-not-found" in r["args"]]
    assert absent and all(r["returncode"] == 0 and not r["stdout"].strip() for r in absent)
    assert h.identity(read("before.json")) == h.identity(read("after.json"))
    assert h.restarts(read("before.json")) == h.restarts(read("after.json"))
    samples = read("resource-samples.json")
    assert len(samples) == 33 and samples[24]["at"] - samples[0]["at"] >= 119
    assert all(x["hostAvailable"] >= 1073741824 and x["wslAvailableKiB"] >= 1048576 for x in samples)
    violations = [x for x in samples if x["memoryPsiAvg10"] > 5]
    assert len(violations) == 1 and violations[0]["memoryPsiAvg10"] == 16.37
    assert all(x["memoryPsiAvg10"] <= 5 for x in samples[:25])
    for path, expected in read("source-manifest.json")["scripts"].items():
        assert hashlib.sha256((OUT / "scripts" / Path(path).name).read_bytes()).hexdigest() == expected
    auth = read("authorization.json")
    assert auth["status"] == "APPROVED"
    assert hashlib.sha256((ROOT / auth["proposal"]).read_bytes()).hexdigest() == auth["proposalSha256"]
    assert hashlib.sha256((OUT / "prepared-source-manifest.json").read_bytes()).hexdigest() == auth["sourceManifestSha256"]
    probes = [json.loads(p.read_text()) for p in sorted(OUT.glob("business-*.json"))]
    assert sum(x["result"]["requests"] for x in probes) == 15
    cleanup = read("cleanup.json")
    assert cleanup["component_resource_verdict"] == "CLEAN" and cleanup["namespace_absent"] and not cleanup["errors"]
    assert cleanup["fixture_http"] == 1 and cleanup["writer_processes"] == cleanup["tcp_checks"] == 0
    pods = read("pods-latest.json")["items"]
    diagnostic = read("guard-owned-cgroups.json")
    assert diagnostic["returncode"] == 0 and set(diagnostic["pod_uids"]) == {p["metadata"]["uid"] for p in pods}
    sections = {}
    for part in diagnostic["stdout"].split("@@ ")[1:]:
        path, _, value = part.partition("\n"); sections[path] = value.strip()
    cgroups = []
    for pod in pods:
        prefix = "/sys/fs/cgroup/kubepods/burstable/pod" + pod["metadata"]["uid"] + "/"
        pressure = sections[prefix + "memory.pressure"]
        some = float(re.search(r"some avg10=([0-9.]+)", pressure)[1])
        events = dict(line.split() for line in sections[prefix + "memory.events"].splitlines())
        assert events["oom"] == events["oom_kill"] == events["max"] == "0"
        cgroups.append({"name": pod["metadata"]["name"], "uid": pod["metadata"]["uid"],
            "some_avg10": some, "memory_current_bytes": int(sections[prefix + "memory.current"]),
            "memory_max_bytes": int(sections[prefix + "memory.max"]), "events": events,
            "cpu_stat": sections[prefix + "cpu.stat"]})
    hot = [x for x in cgroups if x["some_avg10"] > 5]
    assert len(hot) == 1 and hot[0]["name"] == "zer46-source-a" and hot[0]["some_avg10"] == 48.64
    result = {"status": "NOT_MET_GUARD_STOP", "attempt_ended": True, "elapsed_seconds": read("acceptance.json")["elapsed_seconds"],
        "builds": 0, "imports": 0, "pulls": 0, "fixture_ready": True,
        "fixture_counter_admission_attempts": 1, "remote_client_dispatches": 1, "fixture_client_receipts": 0,
        "first_http_result": "UNKNOWN_GUARD_CANCELLED_EXEC; no matching server record in collected cleanup log",
        "first_correlation_id": correlation, "writer_processes": 0, "containment_rule_created": False,
        "boutique_script_http": 15, "post_observer_function_active_time_health": [x["healthy"] for x in probes],
        "formal_r1_or_kpi_pass": False, "guard_samples": len(samples), "violation": violations[0],
        "host_and_wsl_available_above_minimum_all_samples": True, "owned_cgroup_snapshot": cgroups,
        "diagnosis": "Source A memory PSI concentrated at client execution; no OOM/max event. CPU throttling co-observed; no single causal root proven.",
        "namespace_uid": created["metadata"]["uid"], "namespace_uid_delete_verified_absent": True,
        "shared_spec_uid_restart_pvc_preserved": True, "owned_resource_cleanup": "CLEAN_RAW_READBACK",
        "ac01": "NO_COMPLETED_REQUEST_JOIN_IN08", "ac02": "NOT_EXERCISED_IN08", "publication": "NOT_READY", "issue_done": False}
    (OUT / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k != "owned_cgroup_snapshot"}))


if __name__ == "__main__": main()
