"""Independent offline reconciliation of the stopped attempt; never calls Docker/Kubernetes/HTTP."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-03"


def read(name):
    return json.loads((OUT / name).read_text())


def identity(doc):
    return {x["kind"] + "/" + x["metadata"]["namespace"] + "/" + x["metadata"]["name"]:
        {"uid": x["metadata"]["uid"], "spec": x["spec"]} for x in doc["items"]
        if x["kind"] in {"Deployment", "PersistentVolumeClaim"}}


def restarts(doc):
    return {x["metadata"]["uid"] + "/" + c["name"]: c["restartCount"] for x in doc["items"]
            if x["kind"] == "Pod" for c in x.get("status", {}).get("containerStatuses", [])}


def main():
    raw = [json.loads(p.read_text()) for p in sorted((OUT / "raw").glob("*.json"))]
    pulls = [r for r in raw if r["args"][:4] == ["docker", "--context", "desktop-linux", "pull"]]
    writes = [r for r in raw if (r["args"][0] == "kubectl" and any(x in {"apply", "create", "delete", "patch", "replace"} for x in r["args"])) or
        (r["args"][:4] == ["docker", "--context", "desktop-linux", "build"]) or r["args"][:3] == ["k3d", "image", "import"]]
    allowed = {"gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61",
        "docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c"}
    assert len(pulls) == 2 and {r["args"][-1] for r in pulls} == allowed and all(r["returncode"] == 0 for r in pulls)
    assert not writes and not list(OUT.glob("http-*.json")) and not list(OUT.glob("writer-[12].json"))
    before, after = read("before.json"), read("after.json")
    assert identity(before) == identity(after) and restarts(before) == restarts(after)
    pvc = [x for x in after["items"] if x["kind"] == "PersistentVolumeClaim"]
    assert len(pvc) == 3
    namespace = [r for r in raw if r["args"][0] == "kubectl" and "namespace" in r["args"] and "--ignore-not-found" in r["args"]]
    assert namespace and all(r["returncode"] == 0 and not r["stdout"].strip() for r in namespace)
    resources = read("resource-samples.json")
    assert len(resources) >= 25 and resources[24]["at"] - resources[0]["at"] >= 119
    assert all(r["hostAvailable"] >= 1073741824 and r["wslAvailableKiB"] >= 1048576 and r["memoryPsiAvg10"] <= 5 for r in resources)
    probes = [json.loads(p.read_text()) for p in sorted(OUT.glob("business-*.json"))]
    assert len(probes) == 3 and sum(p["result"]["requests"] for p in probes) == 9
    assert all(p["result"]["ok"] is False and p["result"]["detail"] == "TIMEOUT" for p in probes)
    assert probes[0]["result"]["steps"][0]["name"] == "home" and probes[0]["scheduler_idle_ms"] == 0
    assert probes[0]["result"]["elapsed_ms"] >= 3000
    manifest = read("source-manifest.json")
    for original, expected in manifest["scripts"].items():
        assert hashlib.sha256((OUT / "scripts" / Path(original).name).read_bytes()).hexdigest() == expected
    for path, expected in manifest["componentSource"]["source"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    verdict = {"status": "NOT_MET", "component": "NOT_STARTED", "reconciled_from_raw": True,
        "guard": {"samples": len(resources), "preflight_seconds": resources[24]["at"] - resources[0]["at"],
            "host_min_bytes": min(r["hostAvailable"] for r in resources), "wsl_min_kib": min(r["wslAvailableKiB"] for r in resources),
            "max_memory_psi": max(r["memoryPsiAvg10"] for r in resources)},
        "pinned_pulls": [{"ref": r["args"][-1], "returncode": r["returncode"]} for r in pulls],
        "resource_mutation_commands": len(writes), "fixture_http": 0, "boutique_http": 9,
        "business_timeouts": [{"wall_ms": p["result"]["elapsed_ms"], "last_step": p["result"]["steps"][-1]["name"]} for p in probes],
        "owned_cart_cleanup": "helper reported DONE; no independent after-delete cart GET in this attempt",
        "shared_spec_uid_restart_preserved": True, "pvc_count": 3, "namespace_absent": True,
        "owned_resource_cleanup": "CLEAN_NO_RESOURCES_CREATED", "overall_lab_readback": "INCOMPLETE_BUSINESS_NOT_HEALTHY",
        "kpi_claim": False, "publication": "NOT_READY"}
    (OUT / "independent-verification.json").write_text(json.dumps(verdict, indent=2), encoding="utf8")
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
