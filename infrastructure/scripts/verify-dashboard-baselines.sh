#!/usr/bin/env bash
# ZER-11/ZER-39 dashboard and baseline verification. Default commands are offline; see --help.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root"
exec "${ZD_PYTHON:-python}" -B infrastructure/scripts/verify-dashboard-baselines.py "$@"
