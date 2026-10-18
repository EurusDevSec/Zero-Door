#!/usr/bin/env bash
set -euo pipefail
component=all
while (( $# )); do
    case $1 in
        --help|-h)
            printf '%s\n' 'Usage: bash infrastructure/scripts/setup-local-apps.sh [--component target|gaia|all]' \
                'Deploys the local baseline apps in k3d-zero-door: Online Boutique (9 services, 1 replica,' \
                'no HPA, no load generator) with its PrometheusRule, then builds Gaia,' \
                'imports it, restarts it and checks that the running pod uses the image just built.' \
                'Requires setup-phase1 namespaces + monitoring (CRDs); gaia also needs logging and kafka.' \
                'target also applies the frontend Ingress (class traefik, inert until setup-phase1 --component ingress).' \
                'Does not apply HPA, attacks or healing actions.'
            exit 0 ;;
        --component) [[ $# -ge 2 ]] || { printf 'Missing component\n' >&2; exit 2; }; component=$2; shift 2 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
case $component in target|gaia|all) ;; *) printf 'Invalid component\n' >&2; exit 2 ;; esac
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_preflight
if [[ $component == all || $component == target ]]; then
    # ServiceMonitor/PrometheusRule need the CRDs installed by the monitoring component.
    zd_kubectl get crd servicemonitors.monitoring.coreos.com prometheusrules.monitoring.coreos.com >/dev/null
    # Apply Services/ServiceAccounts first, then one Deployment at a time.
    # Applying both multi-document files up front starts concurrent surges.
    zd_python
    mkdir -p -- "$ZD_ROOT/scratch"
    target_work=$(mktemp -d "$ZD_ROOT/scratch/target-rollout.XXXXXX")
    trap 'case $target_work in "$ZD_ROOT"/scratch/target-rollout.?*) rm -rf -- "$target_work" ;; esac' EXIT
    deployments=(redis-cart currencyservice productcatalogservice shippingservice emailservice paymentservice cartservice checkoutservice frontend)
    "$ZD_PYTHON" - "$(zd_path "$ZD_INFRA/manifests")" "$(zd_path "$target_work")" "${deployments[@]}" <<'PY'
import json, pathlib, sys, yaml
source, work = map(pathlib.Path, sys.argv[1:3])
order = sys.argv[3:]
objects = [d for name in ("target-app", "target-app-addons")
           for d in yaml.safe_load_all((source / f"{name}.yaml").read_text(encoding="utf-8")) if d]
deploys, resources = {}, []
for obj in objects:
    if obj["metadata"].get("namespace") != "target-app":
        raise ValueError("Unexpected namespace in target manifests")
    if obj["kind"] == "Deployment":
        name = obj["metadata"]["name"]
        if name in deploys:
            raise ValueError(f"Duplicate Deployment: {name}")
        deploys[name] = obj
    elif obj["kind"] in ("Service", "ServiceAccount"):
        resources.append(obj)
    else:
        raise ValueError(f"Unexpected target resource: {obj['kind']}")
if set(order) != set(deploys) or len(order) != len(deploys):
    raise ValueError("Review the deployment order when the target topology changes")
(work / "resources.json").write_text(json.dumps({"apiVersion": "v1", "kind": "List", "items": resources}) + "\n", encoding="utf-8")
for name in order:
    (work / f"deployment-{name}.json").write_text(json.dumps(deploys[name]) + "\n", encoding="utf-8")
PY
    zd_apply "$target_work/resources.json"
    for deployment in "${deployments[@]}"; do
        zd_apply "$target_work/deployment-$deployment.json"
        zd_kubectl rollout status "deployment/$deployment" -n target-app --timeout=300s
        # A successful rollout may still have terminating old pods charged to quota.
        zd_kubectl get pods -n target-app -o json >"$target_work/pods.json"
        "$ZD_PYTHON" - "$(zd_path "$target_work/pods.json")" >"$target_work/terminating" <<'PY'
import json, pathlib, sys
for pod in json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["items"]:
    if pod["metadata"].get("deletionTimestamp"):
        print(pod["metadata"]["name"])
PY
        while IFS= read -r pod; do
            pod=${pod%$'\r'}  # Native Windows Python writes CRLF stdout.
            zd_kubectl wait --for=delete "pod/$pod" -n target-app --timeout=300s
        done <"$target_work/terminating"
    done
    for manifest in prometheus-rules target-app-ingress; do
        zd_apply "$ZD_INFRA/manifests/$manifest.yaml"
    done
    # This obsolete lab monitor scrapes a nonexistent frontend endpoint.
    # HTTP metrics come from Traefik; CPU metrics still come from cAdvisor.
    zd_kubectl delete servicemonitor frontend-monitor -n target-app --ignore-not-found
fi
if [[ $component == all || $component == gaia ]]; then
    zd_build_import zero-door/gaia:latest "$ZD_ROOT/agent-orchestrator/gaia"
    zd_apply "$ZD_INFRA/manifests/gaia-deployment.yaml"
    # The tag is mutable and the manifest may be unchanged: restart so the imported image is used.
    zd_kubectl rollout restart deployment/gaia -n zero-door
    zd_kubectl rollout status deployment/gaia -n zero-door --timeout=180s
    zd_verify_image zero-door/gaia:latest zero-door gaia
fi
zd_kubectl get pods -n target-app -o wide
zd_log "Local apps completed: $component. Ready pods do not prove the purchase flow; run verify-local-lab.sh."
