"""Offline raw reconciliation of stopped runtime07; never calls Docker, API or HTTP."""
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-07"
spec = importlib.util.spec_from_file_location("zer46_raw_helpers", Path(__file__).with_name("reconcile_runtime03.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def read(name): return json.loads((OUT / name).read_text())


def main():
    raw = [json.loads(p.read_text()) for p in sorted((OUT / "raw").glob("*.json"))]
    assert not any(r["args"][:4] in (["docker", "--context", "desktop-linux", op] for op in ("build", "pull")) or
                   r["args"][:3] == ["k3d", "image", "import"] for r in raw)
    assert len(list(OUT.glob("http-*.json"))) == 16 and len(list(OUT.glob("join-*.json"))) == 15
    assert (OUT / "writer-1.json").exists() and not (OUT / "writer-2.json").exists()
    assert sum(".policy-release" in " ".join(r["args"]) for r in raw) == 2
    profile_spec = importlib.util.spec_from_file_location("zer46_current_policy_parser", Path(__file__).with_name("run_agent_fixture.py"))
    profile = importlib.util.module_from_spec(profile_spec); profile_spec.loader.exec_module(profile)
    pod = read("fixture-initial.json")
    assert pod["spec"]["nodeName"] == "k3d-zero-door-agent-0"
    assert any(c["type"] == "Ready" and c["status"] == "True" for c in pod["status"]["conditions"])
    tables = [r for r in raw if "iptables-save" in r["args"] and r["returncode"] == 0]
    gates = [r for r in tables if profile.hooked_policy(r["stdout"], pod)]
    assert gates
    replacement = read("fixture-after-replacement.json")
    assert replacement["metadata"]["uid"] != pod["metadata"]["uid"]
    assert any(profile.hooked_policy(r["stdout"], replacement) for r in tables)
    request = read("http-016.json")
    assert request["response"]["status"] == 403 and request["response"]["body"] == {"error": "SOURCE_BLOCKED"}
    wrong_log = [r for r in raw if "logs" in r["args"] and "Found 2 pods" in r.get("stderr", "")]
    assert wrong_log and all(pod["metadata"]["name"] in r["stderr"] for r in wrong_log)
    assert all(request["response"]["request_id"] not in r["stdout"] for r in wrong_log)
    rule = read("original-rule.json")
    assert rule["expires_at"] - rule["created_at"] == 180
    assert read("writer-1-block.json")["result"]["rule"] == rule
    for n in range(1, 16):
        http, join = read("http-%03d.json" % n), read("join-%03d.json" % n)
        assert http["response"]["request_id"] == join["request_id"]
        assert http["response"]["status"] == join["status"]
    assert [read("http-%03d.json" % n)["response"]["status"] for n in range(9,16)] == [403,200,201,200,200,404,403]
    created, deleted = read("namespace-created.json"), read("namespace-delete-options.json")
    assert deleted["preconditions"]["uid"] == created["metadata"]["uid"]
    absent = [r for r in raw if r["args"][0] == "kubectl" and "namespace" in r["args"] and "--ignore-not-found" in r["args"]]
    assert absent and all(r["returncode"] == 0 and not r["stdout"].strip() for r in absent)
    before, after = read("before.json"), read("after.json")
    assert h.identity(before) == h.identity(after) and h.restarts(before) == h.restarts(after)
    assert len([x for x in after["items"] if x["kind"] == "PersistentVolumeClaim"]) == 3
    samples = read("resource-samples.json")
    assert len(samples) >= 25 and samples[24]["at"] - samples[0]["at"] >= 119
    assert all(x["hostAvailable"] >= 1073741824 and x["wslAvailableKiB"] >= 1048576 and x["memoryPsiAvg10"] <= 5 for x in samples)
    cache = read("cache-admission.json")
    assert cache["builds"] == cache["imports"] == cache["pulls"] == 0
    for filename in ("bootstrap.yaml", "fixture.yaml"):
        for doc in yaml.safe_load_all((OUT / filename).read_text()):
            if doc["kind"] == "Deployment": pod = doc["spec"]["template"]["spec"]
            elif doc["kind"] == "Pod": pod = doc["spec"]
            else: continue
            assert all(c["imagePullPolicy"] == "Never" for c in pod["containers"])
    for original, expected in read("source-manifest.json")["scripts"].items():
        assert hashlib.sha256((OUT / "scripts" / Path(original).name).read_bytes()).hexdigest() == expected
    probes = [json.loads(p.read_text()) for p in sorted(OUT.glob("business-*.json"))]
    assert sum(x["result"]["requests"] for x in probes) == 16
    assert read("failure.json")["reason"] == "ACCESS_JOIN"
    result = {"status": "NOT_MET_POST_REPLACEMENT_ACCESS_JOIN", "reconciled_from_raw": True,
        "fixture_http": 16, "joined": 15, "boutique_http": 16, "writer_processes": 1, "builds": 0, "imports": 0, "pulls": 0,
        "fixture_application_released": True, "fixture_ready": True, "policy_hook_tables": len(gates), "collector_error": "deployment log selector chose old terminating Pod; request16 unjoined",
        "namespace_uid": created["metadata"]["uid"], "namespace_uid_delete_verified_absent": True,
        "shared_spec_uid_restart_pvc_preserved": True, "pvc_count": 3,
        "guard": {"samples": len(samples), "host_min_bytes": min(x["hostAvailable"] for x in samples),
            "wsl_min_kib": min(x["wslAvailableKiB"] for x in samples), "max_psi_avg10": max(x["memoryPsiAvg10"] for x in samples)},
        "owned_resource_cleanup": "CLEAN_RAW_READBACK", "boutique_health": "NOT_MET",
        "ac01": "BASELINE_IP_SPOOF_ISOLATION_OBSERVED; POST_REPLACEMENT_TRACE_MISSING", "ac02": "BLOCK_AND_BENIGN_BEFORE_REPLACEMENT_OBSERVED; WRITER_REPLAY_EXPIRY_NOT_EXERCISED", "kpi_pass": False, "issue_done": False}
    (OUT / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    print(json.dumps(result))


if __name__ == "__main__": main()
