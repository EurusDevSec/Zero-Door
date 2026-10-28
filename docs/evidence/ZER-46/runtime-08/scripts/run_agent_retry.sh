#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../../../.."
export MSYS_NO_PATHCONV=1 PYTHONDONTWRITEBYTECODE=1
exec scratch/zer12/production-nemesis/Scripts/python.exe -B docs/evidence/ZER-46/runtime-prep/run_agent_retry.py "$@"
