#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
if command -v cygpath >/dev/null 2>&1; then root=$(cygpath -m "$root"); fi
exec "${PYTHON:-python}" -B "$root/docs/evidence/ZER-19/runtime-prep/run.py" "$@"
