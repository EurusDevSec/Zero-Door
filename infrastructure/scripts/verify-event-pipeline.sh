#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root"
exec "${ZD_PYTHON:-python}" -B infrastructure/scripts/verify-event-pipeline.py "$@"
