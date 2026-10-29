#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf '%s\n' 'Usage: bash rebuild-nemesis.sh [--no-forward]' \
        'Builds without cache, imports into zero-door, restarts Nemesis and waits for rollout.' \
        'By default, then supervises its Nemesis port-forward until Ctrl+C.'
    exit 0
fi
[[ $# == 0 || ( $# == 1 && $1 == --no-forward ) ]] || { printf 'Unknown argument\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/infrastructure/scripts/lib/common.sh"
zd_preflight
zd_build_import nemesis:latest "$ZD_ROOT/agent-orchestrator" -f "$(zd_path "$ZD_ROOT/agent-orchestrator/nemesis/Dockerfile")" --no-cache
zd_kubectl rollout restart deployment/nemesis -n zero-door
zd_kubectl rollout status deployment/nemesis -n zero-door --timeout=90s
zd_verify_image nemesis:latest zero-door nemesis
zd_log 'Nemesis rollout completed.'
if [[ ${1:-} != --no-forward ]]; then bash "$ZD_ROOT/start-demo.sh" --nemesis-only; fi
