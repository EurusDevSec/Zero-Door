#!/usr/bin/env bash
set -euo pipefail
component=all
ingress_service=LoadBalancer
while (( $# )); do
    case $1 in
        --help|-h)
            printf '%s\n' 'Usage: bash infrastructure/scripts/setup-phase1.sh [--component NAME] [--ingress-cluster-ip]' \
                'NAME: cluster, namespaces, monitoring, kafka, ingress, logging, policies, all (default).' \
                'Mutates the local lab. Use individual components to measure resource growth.' \
                'all installs the legacy infrastructure; it does not deploy Boutique or agents.' \
                'ingress installs Traefik into kube-system after monitoring (its values create a ServiceMonitor).' \
                '--ingress-cluster-ip (with --component ingress only): rollback step R1 of traefik-migration.md;' \
                '  upgrades the existing traefik release with Service type ClusterIP, which frees node port 80.' \
                '  Never installs, uninstalls or deletes anything.' \
                'Chart versions come from helm-values/chart-versions.yaml; an empty pin blocks that component.'
            exit 0 ;;
        --component) [[ $# -ge 2 ]] || { printf 'Missing component\n' >&2; exit 2; }; component=$2; shift 2 ;;
        --ingress-cluster-ip) ingress_service=ClusterIP; shift ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
case $component in cluster|namespaces|monitoring|kafka|ingress|logging|policies|all) ;; *) printf 'Invalid component\n' >&2; exit 2 ;; esac
[[ $ingress_service == LoadBalancer || $component == ingress ]] || { printf -- '--ingress-cluster-ip needs --component ingress\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
# Versions are resolved before any install, so a missing pin stops the run instead of
# reaching Helm with an empty --version (which would mean "latest").
if [[ $component == all || $component == monitoring ]]; then prometheus_chart=$(zd_chart_version kube-prometheus-stack); fi
if [[ $component == all || $component == kafka ]]; then kafka_chart=$(zd_chart_version kafka); fi
if [[ $component == all || $component == ingress ]]; then ingress_chart=$(zd_chart_version traefik); fi
if [[ $component == all || $component == cluster ]]; then zd_ensure_cluster; else zd_preflight; fi
[[ $component != cluster ]] || exit 0
if [[ $component == all || $component == namespaces ]]; then
    for ns in zero-door target-app monitoring; do
        zd_apply "$ZD_INFRA/namespaces/$ns.yaml"
        zd_apply "$ZD_INFRA/resource-quotas/$ns-quota.yaml"
    done
fi
# Charts are fetched by URL with pinned versions; no `helm repo add/update` touches global Helm state.
if [[ $component == all || $component == monitoring ]]; then
    zd_require helm
    zd_helm upgrade --install prometheus kube-prometheus-stack \
        --repo https://prometheus-community.github.io/helm-charts --version "$prometheus_chart" -n monitoring \
        -f "$(zd_path "$ZD_INFRA/helm-values/prometheus-values.yaml")" --wait --timeout 8m
fi
if [[ $component == all || $component == kafka ]]; then
    zd_require helm
    zd_kafka_renderer
    zd_helm upgrade --install kafka oci://registry-1.docker.io/bitnamicharts/kafka --version "$kafka_chart" \
        -n zero-door -f "$(zd_path "$ZD_INFRA/helm-values/kafka-values.yaml")" "${ZD_KAFKA_RENDERER[@]}" --wait --timeout 8m
fi
if [[ $component == all || $component == ingress ]]; then
    zd_require helm
    # The values create a ServiceMonitor, so the monitoring component must have installed its CRD.
    zd_kubectl get crd servicemonitors.monitoring.coreos.com >/dev/null
    # --skip-crds: the CRD provider is disabled, so none of the chart's traefik.io/hub.traefik.io CRDs is needed.
    traefik_release=(traefik traefik --repo https://traefik.github.io/charts --version "$ingress_chart" -n kube-system
        --skip-crds -f "$(zd_path "$ZD_INFRA/helm-values/traefik-values.yaml")" --wait --timeout 5m)
    if [[ $ingress_service == ClusterIP ]]; then
        # Rollback R1: only one LoadBalancer Service can hold node port 80. Plain upgrade (no --install), release kept.
        zd_helm upgrade "${traefik_release[@]}" --set service.spec.type=ClusterIP
    else
        zd_helm upgrade --install "${traefik_release[@]}"
    fi
fi
if [[ $component == all || $component == logging ]]; then
    zd_apply "$ZD_INFRA/logging/elasticsearch.yaml"
    zd_apply "$ZD_INFRA/logging/fluent-bit.yaml"
    zd_kubectl rollout status deployment/elasticsearch -n monitoring --timeout=300s
    zd_kubectl rollout status daemonset/fluent-bit -n monitoring --timeout=300s
fi
if [[ $component == all || $component == policies ]]; then zd_apply "$ZD_INFRA/manifests/network-policies.yaml"; fi
zd_kubectl get pods -A
zd_log "Infrastructure component completed: $component. Verify its functional behavior separately."
