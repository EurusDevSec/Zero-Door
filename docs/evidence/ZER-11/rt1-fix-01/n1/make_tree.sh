#!/usr/bin/env bash
# Frozen tree for N1 runs: git archive HEAD + the ZER-11/39 package files, with the harness and suite taken
# from <source dir> (the before/ snapshot, or the working tree). Usage: make_tree.sh <dest> <source dir for harness+suite>
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../.." && pwd)
dest=$1; src=$2
[ -e "$dest" ] && { echo "exists" >&2; exit 2; }
mkdir -p "$dest"
cd "$root"
git archive HEAD | tar -x -C "$dest"
files=(agent-orchestrator/nemesis/main.py agent-orchestrator/nemesis/measurement_view.py agent-orchestrator/nemesis/Dockerfile
       agent-orchestrator/nemesis/static/app.js agent-orchestrator/nemesis/static/index.html agent-orchestrator/nemesis/static/style.css
       agent-orchestrator/nemesis/static/results.html agent-orchestrator/nemesis/static/results.js
       agent-orchestrator/hephaestus/main.py agent-orchestrator/hephaestus/command_guard.py .github/workflows/ci.yml
       tests/test_command_guard_integration.py tests/test_dashboard_measurement.py tests/test_dashboard_modes.py tests/check_r1_baselines.py
       tests/results_page_vm.cjs tests/fixtures/zer11/cases.py tests/fixtures/zer11/expected.json infrastructure/manifests/r1-baselines.yaml
       infrastructure/scripts/verify-dashboard-baselines.py infrastructure/scripts/verify-dashboard-baselines.sh
       docs/runbooks/dashboard-and-baselines.md)
for f in "${files[@]}"; do mkdir -p "$dest/$(dirname "$f")"; cp "$f" "$dest/$f"; done
for f in infrastructure/scripts/r1_baseline_runtime.py tests/test_dashboard_baseline_runtime.py; do cp "$src/$f" "$dest/$f"; done
echo "tree $dest from $src"
