#!/usr/bin/env bash
# ZER-11/39 offline regression run: new suites and related existing suites on each pinned interpreter,
# measurement baseline, CI boundary, manifest checks, Bandit and whitespace. No cluster, Docker or model.
#   NEMESIS=<python> HEPHAESTUS=<python> GUARDS=<python> BANDIT=<python with bandit> bash run_regressions.sh <log>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
log=${1:?log file}
: > "$log"
status=0
step() {
  local name=$1; shift
  local out
  out=$("$@" 2>&1); local code=$?
  printf '%s | exit %s | %s\n' "$name" "$code" "$(printf '%s\n' "$out" | grep -E '^(Ran |OK|FAILED|VERDICT|PASS|FAIL|.*PASS$|No issues|Total issues|\{)' | tail -3 | tr '\n' ' ' | sed 's/ *$//')" >> "$log"
  [ "$code" -eq 0 ] || status=1
}
for role in NEMESIS HEPHAESTUS GUARDS; do
  py=${!role}
  version=$("$py" -c 'import sys, fastapi, pydantic; print(sys.version.split()[0], "fastapi", fastapi.__version__, "pydantic", pydantic.__version__)')
  echo "== $role: $version" >> "$log"
  for suite in tests/test_dashboard_measurement.py tests/test_dashboard_modes.py tests/test_command_guards.py \
               tests/test_command_modes.py tests/test_command_guard_integration.py tests/test_event_agents.py; do
    step "$role $suite" "$py" -B "$suite"
  done
  step "$role tests/check_r1_baselines.py" "$py" -B tests/check_r1_baselines.py
  step "$role tests/check_guard_manifests.py" "$py" -B tests/check_guard_manifests.py
  step "$role tests/test_command_guard_ci.py" "$py" -B tests/test_command_guard_ci.py
done
step "NEMESIS check_agent_dependencies nemesis" "$NEMESIS" -B tests/check_agent_dependencies.py nemesis
step "HEPHAESTUS check_agent_dependencies hephaestus" "$HEPHAESTUS" -B tests/check_agent_dependencies.py hephaestus
step "measurement offline (ZER-10, unchanged code)" env ZD_PYTHON=python bash infrastructure/scripts/verify-measurement.sh --offline
step "verify-dashboard-baselines --help" bash infrastructure/scripts/verify-dashboard-baselines.sh --help
step "node --check app.js" node --check agent-orchestrator/nemesis/static/app.js
step "node --check results.js" node --check agent-orchestrator/nemesis/static/results.js
step "bandit (changed/new Python)" "$BANDIT" -m bandit -q agent-orchestrator/nemesis/main.py agent-orchestrator/nemesis/measurement_view.py \
  agent-orchestrator/hephaestus/main.py agent-orchestrator/hephaestus/command_guard.py infrastructure/scripts/verify-dashboard-baselines.py
step "git diff --check" git diff --check
echo "OVERALL exit $status" >> "$log"
exit $status
