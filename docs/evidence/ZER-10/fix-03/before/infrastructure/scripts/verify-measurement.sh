#!/usr/bin/env bash
# ZER-10/ZER-38 measurement verification. Default is offline (no lab); see --help.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root"
exec "${ZD_PYTHON:-python}" -B infrastructure/scripts/verify-measurement.py "$@"
