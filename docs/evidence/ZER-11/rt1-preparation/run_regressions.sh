#!/usr/bin/env bash
# H-RT1 offline regressions: the new suite and the suites that read what this package changed (runbook,
# verify script, CI workflow), on each pinned production interpreter; plan-check and the rt1 matrix;
# Bandit on the Python this package adds or changes; whitespace. No cluster, Docker or model.
#   NEMESIS=<python> HEPHAESTUS=<python> BANDIT=<python with bandit> bash run_regressions.sh <new log>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
log=$(realpath -m "${1:?log file}")
[ -e "$log" ] && { echo "log exists" >&2; exit 2; }
cd "$root"
status=0
step() {
  local name=$1; shift
  local out code
  out=$("$@" 2>&1); code=$?
  # A failed step keeps its whole output next to the log (the summary line alone cannot name a failing test).
  [ "$code" -eq 0 ] || { status=1; printf '%s\n' "$out" > "$log.$(printf '%s' "$name" | tr -c 'A-Za-z0-9._-' '_').failed.txt"; }
  printf '%s | exit %s | %s\n' "$name" "$code" "$(printf '%s\n' "$out" | grep -E '^(Ran |OK|FAILED)|PASS$|problems|"verdict"|No issues|Issue' | tail -2 | tr '\n' ' ' | sed 's/ *$//')" >> "$log"
}
for py in NEMESIS HEPHAESTUS; do
  for suite in tests/test_dashboard_baseline_runtime.py tests/test_dashboard_measurement.py tests/test_dashboard_modes.py; do
    step "$py $suite" "${!py}" -B "$suite"
  done
done
step "HEPHAESTUS tests/check_r1_baselines.py" "$HEPHAESTUS" -B tests/check_r1_baselines.py
step "NEMESIS tests/test_command_guard_ci.py" "$NEMESIS" -B tests/test_command_guard_ci.py
step "plan-check" "$NEMESIS" -B infrastructure/scripts/verify-dashboard-baselines.py plan-check
step "rt1 matrix (offline)" "$NEMESIS" -B -c '
import json, subprocess, sys
out = subprocess.run([sys.executable, "-B", "infrastructure/scripts/verify-dashboard-baselines.py", "rt1"], capture_output=True, text=True)
m = json.loads(out.stdout); print(len(m["writes"]), "writes,", m["image"]["image"]); sys.exit(out.returncode)'
step "rt1 --execute without approval is refused" bash -c '! "$0" -B infrastructure/scripts/verify-dashboard-baselines.py rt1 --execute' "$NEMESIS"
step "bandit harness + verify" "$BANDIT" -m bandit -q infrastructure/scripts/r1_baseline_runtime.py infrastructure/scripts/verify-dashboard-baselines.py
snap=scratch/zer11/claude-rt1/before
for f in infrastructure/scripts/verify-dashboard-baselines.py docs/runbooks/dashboard-and-baselines.md .github/workflows/ci.yml; do
  step "diff --check $f" bash -c '! git diff --no-index --check "$0" "$1" | grep -q .' "$snap/$f" "$f"
done
for f in infrastructure/scripts/r1_baseline_runtime.py tests/test_dashboard_baseline_runtime.py; do
  step "no trailing whitespace/CR $f" bash -c '! grep -nP "[ \t\r]$" "$0"' "$f"
done
echo "OVERALL exit $status" >> "$log"
sed -i 's/[[:space:]]*$//' "$log"
exit $status
