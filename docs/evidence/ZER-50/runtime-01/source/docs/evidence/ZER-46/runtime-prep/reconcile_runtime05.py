"""Offline raw reconciliation of stopped runtime05; never calls Docker, API or HTTP."""
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-05"
spec = importlib.util.spec_from_file_location("zer46_raw_helpers", Path(__file__).with_name("reconcile_runtime03.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def read(name): return json.loads((OUT / name).read_text())


def main():
    raw = [json.loads(p.read_text()) for p in sorted((OUT / "raw").glob("*.json"))]
    assert not any(r["args"][:4] in (["docker", "--context", "desktop-linux", op] for op in ("build", "pull")) or
                   r["args"][:3] == ["k3d", "image", "import"] for r in raw)
    assert not list(OUT.glob("http-*.json")) and not list(OUT.glob("writer-[12].json"))
    assert not any(".policy-release" in " ".join(r["args"]) for r in raw)
    gates = [r for r in raw if "iptables-save | grep -F" in " ".join(r["args"])]
    assert len(gates) >= 30 and all(r["returncode"] == 1 and not r["stdout"] and not r["stderr"] for r in gates)
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
    assert sum(x["result"]["requests"] for x in probes) == 9
    assert not any(x["result"]["ok"] for x in probes)
    assert read("failure.json")["reason"] == "POLICY_GATE_NOT_ENFORCED"
    result = {"status": "NOT_MET_POLICY_GATE", "reconciled_from_raw": True,
        "fixture_http": 0, "boutique_http": 9, "writer_processes": 0, "builds": 0, "imports": 0, "pulls": 0,
        "fixture_application_released": False, "policy_gate_polls": len(gates),
        "namespace_uid": created["metadata"]["uid"], "namespace_uid_delete_verified_absent": True,
        "shared_spec_uid_restart_pvc_preserved": True, "pvc_count": 3,
        "guard": {"samples": len(samples), "host_min_bytes": min(x["hostAvailable"] for x in samples),
            "wsl_min_kib": min(x["wslAvailableKiB"] for x in samples), "max_psi_avg10": max(x["memoryPsiAvg10"] for x in samples)},
        "owned_resource_cleanup": "CLEAN_RAW_READBACK", "boutique_health": "NOT_MET",
        "ac01": "NOT_VERIFIED_IN_THIS_ATTEMPT", "ac02": "NOT_EXERCISED", "kpi_pass": False, "issue_done": False}
    (OUT / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    print(json.dumps(result))


if __name__ == "__main__": main()
