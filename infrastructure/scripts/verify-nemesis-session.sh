#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
export PYTHONUTF8=1
if command -v cygpath >/dev/null 2>&1; then root=$(cygpath -m "$root"); fi
export PYTHONPATH="$root/agent-orchestrator"
exec "${PYTHON:-python}" -B -m nemesis.session_cli "$@"
