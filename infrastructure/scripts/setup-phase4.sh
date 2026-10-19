#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf '%s\n' 'Usage: bash infrastructure/scripts/setup-phase4.sh' \
        'Builds/imports/deploys Hephaestus and verifies rollout and expected RBAC boundaries.'
    exit 0
fi
[[ $# == 0 ]] || { printf 'Unknown argument\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_preflight
zd_build_import hephaestus:latest "$ZD_ROOT/agent-orchestrator" --file "$(zd_path "$ZD_ROOT/agent-orchestrator/hephaestus/Dockerfile")"
zd_apply "$ZD_INFRA/manifests/hephaestus-deployment.yaml"
zd_kubectl rollout restart deployment/hephaestus -n zero-door
zd_kubectl rollout status deployment/hephaestus -n zero-door --timeout=120s
zd_verify_image hephaestus:latest zero-door hephaestus
for ns in target-app kube-system monitoring zero-door; do
    answer=$(zd_kubectl auth can-i --as=system:serviceaccount:zero-door:hephaestus-sa delete pods -n "$ns" || true)
    expected=no
    [[ $ns != target-app ]] || expected=yes
    [[ $answer == "$expected" ]] || zd_die "Unexpected RBAC result for $ns: $answer (expected $expected)"
done
zd_log 'Hephaestus rollout and delete-pod RBAC checks passed; healing behavior still requires verification.'
