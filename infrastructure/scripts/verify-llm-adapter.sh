#!/usr/bin/env bash
# No inference unless --live is explicitly passed after budget approval.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "${PYTHON:-python}" -B "$root/infrastructure/scripts/verify_llm_adapter.py" "$@"
