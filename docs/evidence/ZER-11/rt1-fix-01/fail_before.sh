#!/usr/bin/env bash
# rt1-fix-01 fail-before / expected-fixed: two clean trees (git archive HEAD + the ZER-11/39 package files, no
# scratch/), identical except for the harness: BEFORE from the snapshot taken before this package, AFTER from the
# working tree. Both use the rt1-fix-01 suite. Runs focused.py in each mode and writes one JSON per run.
#   NEMESIS=<python> bash fail_before.sh <snapshot dir with the before harness> <results dir (new)>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
before=$(realpath "${1:?snapshot dir}"); results=$(realpath -m "${2:?results dir}")
[ -e "$results" ] && { echo "results dir exists" >&2; exit 2; }
mkdir -p "$results"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$root"
files=(agent-orchestrator/nemesis/main.py agent-orchestrator/nemesis/measurement_view.py agent-orchestrator/nemesis/Dockerfile
       agent-orchestrator/nemesis/static/app.js agent-orchestrator/nemesis/static/index.html agent-orchestrator/nemesis/static/style.css
       agent-orchestrator/nemesis/static/results.html agent-orchestrator/nemesis/static/results.js
       agent-orchestrator/hephaestus/main.py agent-orchestrator/hephaestus/command_guard.py .github/workflows/ci.yml
       tests/test_command_guard_integration.py tests/test_dashboard_measurement.py tests/test_dashboard_modes.py tests/check_r1_baselines.py
       tests/results_page_vm.cjs tests/fixtures/zer11/cases.py tests/fixtures/zer11/expected.json infrastructure/manifests/r1-baselines.yaml
       infrastructure/scripts/verify-dashboard-baselines.py infrastructure/scripts/verify-dashboard-baselines.sh
       docs/runbooks/dashboard-and-baselines.md infrastructure/scripts/r1_baseline_runtime.py tests/test_dashboard_baseline_runtime.py)
for side in before after; do
  mkdir -p "$work/$side"
  git archive HEAD | tar -x -C "$work/$side"
  for f in "${files[@]}"; do mkdir -p "$work/$side/$(dirname "$f")"; cp "$f" "$work/$side/$f"; done
done
cp "$before/infrastructure/scripts/r1_baseline_runtime.py" "$work/before/infrastructure/scripts/r1_baseline_runtime.py"
{
  echo "HEAD $(git rev-parse --short HEAD); scratch/ in trees: $([ -e "$work/after/scratch" ] && echo yes || echo no)"
  for side in before after; do echo "$side harness sha256 $(sha256sum "$work/$side/infrastructure/scripts/r1_baseline_runtime.py" | cut -c1-64)"; done
  echo "suite sha256 $(sha256sum tests/test_dashboard_baseline_runtime.py | cut -c1-64)"
} > "$results/trees.txt"
run() {  # <side> <mode> <name>
  "$NEMESIS" -B "$here/focused.py" "$work/$1" "$2" "$results/$3.json" > "$results/$3.log" 2>&1
  echo "$3 exit $?" >> "$results/exits.txt"
}
run before before-compat-mf fail-before-isolated
run before before-compat fail-before-kubectl-default
run after plain expected-fixed
cat "$results/exits.txt"
