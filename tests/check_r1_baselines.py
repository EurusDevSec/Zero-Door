"""Offline check of the ZER-39 baseline profile (infrastructure/manifests/r1-baselines.yaml).

Renders nothing against a cluster. Checks: OpenAPI fields/types against the pinned Kubernetes client
models; the group table equals the locked contract 7.4 fixture; B0 has no ZERO DOOR decider, executor,
LLM or heal RBAC; the HPA targets exist with CPU requests and the scale limit equals Hephaestus'
MAX_REPLICAS; the live Nemesis deployment exposes no S results. Exit 0 and one line per check on PASS.
"""
from pathlib import Path
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "infrastructure/manifests"


def load(name):
    return [d for d in yaml.safe_load_all((MANIFESTS / name).read_text(encoding="utf-8")) if d]


def profile(documents):
    maps = [d for d in documents if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "zd-r1-baseline-profiles"]
    if len(maps) != 1:
        raise ValueError("profile ConfigMap missing or duplicated")
    return json.loads(maps[0]["data"]["profiles.json"])


def check(documents=None, out=print):
    documents = documents if documents is not None else load("r1-baselines.yaml")
    try:
        from check_guard_manifests import check as openapi
    except ImportError:  # kubernetes models not installed (stdlib-only run): reported, not hidden
        out("OpenAPI field/type SKIPPED (kubernetes client models not installed)")
    else:
        openapi(documents)
        out("OpenAPI field/type PASS", len(documents), "resources")
    p = profile(documents)
    groups = p["groups"]
    modes = json.loads((ROOT / "tests/fixtures/zer12/modes.json").read_text())["groups"]
    if set(groups) != set(modes):
        raise ValueError("groups differ from the contract 7.4 fixture")
    for group, rows in modes.items():
        if [list(r) for r in groups[group]["decisions"]] != [list(r) for r in rows]:
            raise ValueError(f"{group}: decision sources differ from contract 7.4")
        if groups[group]["llm_call"] != any(kind in {"LLM", "SINGLE_LLM"} for _, kind, _ in rows):
            raise ValueError(f"{group}: llm_call differs from contract 7.4")
    expected_modes = {"B0": "K8S_BASELINE", "BM": "MANUAL", "B1": "RULES", "B2": "AI", "B3": "AI_SINGLE"}
    if {g: v["mode"] for g, v in groups.items()} != expected_modes:
        raise ValueError("mode labels differ (MANUAL=BM, RULES=B1, AI=B2)")
    out("Group table equals contract 7.4 PASS")
    b0 = groups["B0"]
    if b0["decisions"] or b0["llm_call"] or b0["initiator"] is not None or b0["zero_door_components"] or \
            not {"gaia", "hephaestus"} <= set(b0["absent"]) or set(b0["recovery_by"]) != {"deployment-controller", "hpa"} or \
            set(b0["forbidden_events"]) != {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}:
        raise ValueError("B0 must have no ZERO DOOR decider/executor/LLM and name both Kubernetes recovery paths")
    if any(groups[g].get("available") is not False for g in ("B2", "B3")):
        raise ValueError("B2/B3 have no producer in R1 and must be marked unavailable")
    if any(d["kind"] in {"Role", "RoleBinding", "ClusterRole", "ClusterRoleBinding", "Deployment", "Secret", "ServiceAccount"} for d in documents):
        raise ValueError("the profile may not add workloads, secrets or RBAC")
    out("B0 has no ZERO DOOR decision/action/LLM/RBAC; profile adds no workload or RBAC PASS")

    targets = {d["metadata"]["name"]: d for d in load("target-app.yaml") if d["kind"] == "Deployment"}
    heal = next(d for d in load("hephaestus-deployment.yaml") if d["kind"] == "ConfigMap")
    limit = int(heal["data"]["MAX_REPLICAS"])
    hpas = [d for d in documents if d["kind"] == "HorizontalPodAutoscaler"]
    if sorted(h["metadata"]["name"] for h in hpas) != sorted(p["common"]["hpa_objects"]):
        raise ValueError("HPA objects differ from the profile")
    seen = set()
    legacy = {d["metadata"]["name"] for d in load("target-app-hpa.yaml")}
    for h in hpas:
        ref = h["spec"]["scaleTargetRef"]
        name = ref["name"]
        if ref["kind"] != "Deployment" or name not in targets or name in seen or h["metadata"]["namespace"] != "target-app":
            raise ValueError(f"{h['metadata']['name']}: target must be one distinct target-app Deployment")
        seen.add(name)
        if h["metadata"]["name"] in legacy:
            raise ValueError("profile HPA reuses a legacy HPA name (would edit it silently)")
        containers = targets[name]["spec"]["template"]["spec"]["containers"]
        if not all((c.get("resources") or {}).get("requests", {}).get("cpu") for c in containers):
            raise ValueError(f"{name}: CPU utilization HPA needs CPU requests on every container")
        if (h["spec"]["minReplicas"], h["spec"]["maxReplicas"]) != (p["common"]["scale_limit"]["min_replicas"], limit) or \
                p["common"]["scale_limit"]["max_replicas"] != limit:
            raise ValueError(f"{h['metadata']['name']}: scale bounds differ from Hephaestus MAX_REPLICAS={limit}")
        if "replicas" in targets[name]["spec"]:
            raise ValueError(f"{name}: a fixed spec.replicas would fight the HPA")
    out(f"HPA targets {sorted(seen)} exist with CPU requests; bounds 1..{limit} = MAX_REPLICAS PASS")

    nemesis = load("nemesis-deployment.yaml")
    text = json.dumps(nemesis)
    if "ZD_RESULTS_ROOT" in text or "ZD_RESULTS_TOKEN_FILE" in text or "results-reader" in text:
        raise ValueError("the live Nemesis deployment must not expose S results")
    out("Live Nemesis deployment mounts no results root/reader key PASS")
    return p


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "tests"))
    try:
        check()
    except (ValueError, KeyError, StopIteration) as error:
        print("FAIL", error)
        sys.exit(1)
