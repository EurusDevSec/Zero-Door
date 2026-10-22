#!/usr/bin/env bash
# RT2 preparation / O-boundary tools. No command here builds or mutates Kubernetes.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root"
exec "${ZD_PYTHON:-python}" -B infrastructure/scripts/r1_mode_runtime.py "$@"
