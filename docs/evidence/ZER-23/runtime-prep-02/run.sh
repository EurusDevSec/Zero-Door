#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo_root=$(cd -- "$script_dir/../../../.." && pwd -P)
cd -- "$repo_root"
python=/r/_Projects/Eurus_Workspace/zero_door/scratch/zer12/production-hephaestus/Scripts/python.exe
test -f "$python" || { echo 'EXISTING_PINNED_PYTHON_MISSING' >&2; exit 1; }
runner=$(cygpath -w "$script_dir/run.py")
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
exec "$python" -B "$runner" "$@"
