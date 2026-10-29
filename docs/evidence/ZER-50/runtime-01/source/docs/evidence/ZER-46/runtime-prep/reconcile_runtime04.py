"""Offline raw check of runtime04 and physical cleanup. Preserve the original incomplete receipt."""
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-04"
spec = importlib.util.spec_from_file_location("zer46_id_helpers", Path(__file__).with_name("reconcile_runtime03.py"))
helpers = importlib.util.module_from_spec(spec); spec.loader.exec_module(helpers)


def read(name):
    return json.loads((OUT / name).read_text())


def main():
    raw = [json.loads(p.read_text()) for p in sorted((OUT / "raw").glob("*.json"))]
    builds = [r for r in raw if r["args"][:4] == ["docker", "--context", "desktop-linux", "build"]]
    imports = [r for r in raw if r["args"][:3] == ["k3d", "image", "import"]]
    assert len(builds) == len(imports) == 1 and builds[0]["returncode"] == imports[0]["returncode"] == 0
    assert "--mode=direct" in imports[0]["args"]
    assert not list(OUT.glob("http-*.json")) and not list(OUT.glob("writer-[12].json"))
    bootstrap = list(yaml.safe_load_all((OUT / "bootstrap.yaml").read_text()))
    assert not any(d["kind"] == "Deployment" and d["metadata"]["name"] == "sqli-fixture" for d in bootstrap)
    assert not (OUT / "fixture.yaml").exists()
    created = read("namespace-created.json")
    deleted = read("namespace-delete-options.json")
    assert deleted["preconditions"]["uid"] == created["metadata"]["uid"]
    namespace = [r for r in raw if r["args"][0] == "kubectl" and "namespace" in r["args"] and "--ignore-not-found" in r["args"]]
    assert namespace and all(r["returncode"] == 0 and not r["stdout"].strip() for r in namespace)
    before, after = read("before.json"), read("after.json")
    assert helpers.identity(before) == helpers.identity(after) and helpers.restarts(before) == helpers.restarts(after)
    assert len([x for x in after["items"] if x["kind"] == "PersistentVolumeClaim"]) == 3
    samples = read("resource-samples.json")
    violation = [x for x in samples if x["memoryPsiAvg10"] > 5 or x["hostAvailable"] < 1073741824 or x["wslAvailableKiB"] < 1048576]
    assert len(violation) == 1 and violation[0]["memoryPsiAvg10"] == 15.02
    assert violation[0]["hostAvailable"] >= 1073741824 and violation[0]["wslAvailableKiB"] >= 1048576
    log_failure = [r for r in raw if r.get("returncode") == 1 and "logs" in r["args"]]
    assert log_failure and b"NotFound" in log_failure[0]["stderr"].encode()
    manifest = read("source-manifest.json")
    for original, expected in manifest["scripts"].items():
        assert hashlib.sha256((OUT / "scripts" / Path(original).name).read_bytes()).hexdigest() == expected
    cache = read("node-images.json")["images"]
    fixture = [x for x in cache if "docker.io/library/zer46-fixture:24662046a33f" in x.get("repoTags", [])]
    assert len(fixture) == 1 and fixture[0]["id"] == "sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16"
    assert any("docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c" in x.get("repoDigests", []) for x in cache)
    probes = [json.loads(p.read_text()) for p in sorted(OUT.glob("business-*.json"))]
    assert sum(x["result"]["requests"] for x in probes) == 16
    verdict = {"status": "NOT_MET_GUARD_STOP", "fixture_component": "NOT_STARTED", "fixture_http": 0,
        "boutique_http": 16, "successful_builds": 1, "successful_imports": 1,
        "namespace_uid": created["metadata"]["uid"], "namespace_uid_delete_verified_absent": True,
        "shared_spec_uid_restart_pvc_preserved": True, "pvc_count": 3,
        "guard_violation": violation[0], "memory_capacity_below_minimum": False,
        "owned_resource_cleanup": "CLEAN_INDEPENDENT_RAW_READBACK",
        "original_cleanup_verdict": "INCOMPLETE_RETAINED",
        "collector_defect": "attempted log of fixture Deployment before creation; NotFound was diagnostic, not an orphan",
        "cache_confirmed_server0_after_stop": True,
        "node_side_pulls_at_start": "NOT_INDEPENDENTLY_AUDITED; old proxy IfNotPresent corrected to Never for future",
        "boutique_functional_results": [x["result"]["ok"] for x in probes],
        "boutique_wall_reference_slo": [x["wall_reference_slo_met"] for x in probes],
        "formal_r1_or_kpi_pass": False, "publication": "NOT_READY"}
    (OUT / "independent-verification.json").write_text(json.dumps(verdict, indent=2), encoding="utf8")
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
