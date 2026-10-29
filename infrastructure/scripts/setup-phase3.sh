#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf '%s\n' 'Usage: bash infrastructure/scripts/setup-phase3.sh' \
        'Builds/imports/deploys Chaos Worker and Nemesis in k3d-zero-door; waits for rollout.' \
        'Preserves an existing nemesis-secrets Secret; does not run attacks or go mod tidy.'
    exit 0
fi
[[ $# == 0 ]] || { printf 'Unknown argument\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_preflight
zd_kubectl get deployment frontend -n target-app >/dev/null
zd_build_import chaos-worker:latest "$ZD_ROOT/chaos-worker"
zd_build_import nemesis:latest "$ZD_ROOT/agent-orchestrator" -f "$(zd_path "$ZD_ROOT/agent-orchestrator/nemesis/Dockerfile")"
zd_apply "$ZD_INFRA/manifests/chaos-worker.yaml"
zd_apply_nemesis
zd_kubectl rollout restart deployment/chaos-worker -n zero-door
zd_kubectl rollout restart deployment/nemesis -n zero-door
zd_kubectl rollout status deployment/chaos-worker -n zero-door --timeout=120s
zd_kubectl rollout status deployment/nemesis -n zero-door --timeout=120s
zd_verify_image chaos-worker:latest zero-door chaos-worker
zd_verify_image nemesis:latest zero-door nemesis
zd_kubectl get pods -n zero-door -l phase=3
zd_log 'Worker/Nemesis rollout completed. Health-only checks are described in the Bash runbook.'
