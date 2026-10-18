#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf '%s\n' 'Usage: bash infrastructure/scripts/recreate-cluster.sh --confirm-delete-zero-door' \
        'DESTRUCTIVE: deletes cluster zero-door and its cluster-local data; then installs legacy infrastructure.' \
        'Does not restore Boutique, agents or lost data. Back up required data first.'
    exit 0
fi
[[ $# == 1 && $1 == --confirm-delete-zero-door ]] || {
    printf 'Refusing deletion. Read --help and supply --confirm-delete-zero-door only after backing up data.\n' >&2
    exit 2
}
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_require docker k3d kubectl helm
zd_docker_guard
docker info >/dev/null
k3d cluster delete "$ZD_CLUSTER"
bash "$ZD_INFRA/scripts/setup-phase1.sh"
