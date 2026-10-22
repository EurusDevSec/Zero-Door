#!/usr/bin/env bash
# Clean-checkout simulation: `git archive HEAD` plus exactly the package's changed/new files (no scratch/,
# no untracked owner files), then the new and related suites with the pinned interpreters. Offline.
#   NEMESIS=<python> HEPHAESTUS=<python> bash clean_checkout.sh <log>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
log=$(realpath -m "${1:?log file}")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$root"
git archive HEAD | tar -x -C "$work"
files=(agent-orchestrator/nemesis/main.py agent-orchestrator/nemesis/measurement_view.py agent-orchestrator/nemesis/Dockerfile
       agent-orchestrator/nemesis/static/app.js agent-orchestrator/nemesis/static/index.html agent-orchestrator/nemesis/static/style.css
       agent-orchestrator/nemesis/static/results.html agent-orchestrator/nemesis/static/results.js
       agent-orchestrator/hephaestus/main.py agent-orchestrator/hephaestus/command_guard.py .github/workflows/ci.yml
       tests/test_command_guard_integration.py tests/test_dashboard_measurement.py tests/test_dashboard_modes.py tests/check_r1_baselines.py
       tests/fixtures/zer11/cases.py tests/fixtures/zer11/expected.json infrastructure/manifests/r1-baselines.yaml
       infrastructure/scripts/verify-dashboard-baselines.py infrastructure/scripts/verify-dashboard-baselines.sh)
for f in "${files[@]}"; do mkdir -p "$work/$(dirname "$f")"; cp "$f" "$work/$f"; done
{
  echo "clean tree: git archive $(git rev-parse --short HEAD) + ${#files[@]} package files; scratch/ present: $([ -e "$work/scratch" ] && echo yes || echo no)"
  cd "$work"
  status=0
  for pair in "NEMESIS tests/test_dashboard_measurement.py" "HEPHAESTUS tests/test_dashboard_modes.py" \
              "HEPHAESTUS tests/check_r1_baselines.py" "NEMESIS tests/test_command_guard_integration.py" \
              "HEPHAESTUS tests/test_event_agents.py" "NEMESIS tests/test_command_guard_ci.py"; do
    set -- $pair; py=${!1}
    out=$("$py" -B "$2" 2>&1); code=$?
    [ "$code" -eq 0 ] || status=1
    echo "$1 $2 | exit $code | $(printf '%s\n' "$out" | grep -E '^(Ran |OK|FAILED)|PASS$' | tail -2 | tr '\n' ' ' | sed 's/ *$//')"
  done
  out=$(ZD_PYTHON="$NEMESIS" bash infrastructure/scripts/verify-dashboard-baselines.sh --help 2>&1); echo "--help | exit $? | $(printf '%s\n' "$out" | head -1)"
  echo "OVERALL exit $status"
} > "$log"
grep -q "OVERALL exit 0" "$log"
