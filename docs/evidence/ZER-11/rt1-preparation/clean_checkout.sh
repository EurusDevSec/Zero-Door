#!/usr/bin/env bash
# Clean-checkout simulation for H-RT1: `git archive HEAD` plus exactly the uncommitted files the ZER-11/39
# packages (first package, fix-01, H-RT1) need, no scratch/ and no other owner files. Then the H-RT1 suite and
# the dashboard suites on the pinned interpreters, plan-check and the rt1 matrix. Offline.
#   NEMESIS=<python> HEPHAESTUS=<python> bash clean_checkout.sh <new log>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
log=$(realpath -m "${1:?log file}")
[ -e "$log" ] && { echo "log exists" >&2; exit 2; }
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$root"
git archive HEAD | tar -x -C "$work"
files=(agent-orchestrator/nemesis/main.py agent-orchestrator/nemesis/measurement_view.py agent-orchestrator/nemesis/Dockerfile
       agent-orchestrator/nemesis/static/app.js agent-orchestrator/nemesis/static/index.html agent-orchestrator/nemesis/static/style.css
       agent-orchestrator/nemesis/static/results.html agent-orchestrator/nemesis/static/results.js
       agent-orchestrator/hephaestus/main.py agent-orchestrator/hephaestus/command_guard.py .github/workflows/ci.yml
       tests/test_command_guard_integration.py tests/test_dashboard_measurement.py tests/test_dashboard_modes.py tests/check_r1_baselines.py
       tests/results_page_vm.cjs tests/fixtures/zer11/cases.py tests/fixtures/zer11/expected.json infrastructure/manifests/r1-baselines.yaml
       infrastructure/scripts/verify-dashboard-baselines.py infrastructure/scripts/verify-dashboard-baselines.sh
       docs/runbooks/dashboard-and-baselines.md
       infrastructure/scripts/r1_baseline_runtime.py tests/test_dashboard_baseline_runtime.py)
for f in "${files[@]}"; do mkdir -p "$work/$(dirname "$f")"; cp "$f" "$work/$f"; done
{
  echo "clean tree: git archive $(git rev-parse --short HEAD) + ${#files[@]} package files; scratch/ present: $([ -e "$work/scratch" ] && echo yes || echo no)"
  cd "$work"
  status=0
  for pair in "NEMESIS tests/test_dashboard_baseline_runtime.py" "HEPHAESTUS tests/test_dashboard_baseline_runtime.py" \
              "NEMESIS tests/test_dashboard_measurement.py" "HEPHAESTUS tests/test_dashboard_modes.py" "HEPHAESTUS tests/check_r1_baselines.py"; do
    set -- $pair; py=${!1}
    out=$("$py" -B "$2" 2>&1); code=$?
    [ "$code" -eq 0 ] || status=1
    echo "$1 $2 | exit $code | $(printf '%s\n' "$out" | grep -E '^(Ran |OK|FAILED)|PASS$' | tail -2 | tr '\n' ' ' | sed 's/ *$//')"
  done
  out=$("$NEMESIS" -B infrastructure/scripts/verify-dashboard-baselines.py plan-check 2>&1); code=$?; [ "$code" -eq 0 ] || status=1
  echo "plan-check | exit $code"
  out=$("$NEMESIS" -B infrastructure/scripts/verify-dashboard-baselines.py rt1 2>&1); code=$?; [ "$code" -eq 0 ] || status=1
  echo "rt1 matrix | exit $code | $(printf '%s' "$out" | grep -c '"verb"') writes"
  echo "OVERALL exit $status"
} > "$log"
grep -q "OVERALL exit 0" "$log"
