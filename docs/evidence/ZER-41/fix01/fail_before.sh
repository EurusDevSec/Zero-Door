#!/usr/bin/env bash
# ZR41-01..08 fail-before / after demonstration. Runs the updated suites against the pre-fix snapshot app
# (ZD_SQLI_APP) — they FAIL — and against the current fixed service — they PASS. Also runs the updated
# manifest checker against the snapshot manifest (fails) and the current manifest (OVERALL PASS). Offline.
#   NEMESIS=<python> bash docs/evidence/ZER-41/fix01/fail_before.sh <new results dir>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
out=$(realpath -m "${1:?results dir}"); mkdir -p "$out"
N=${NEMESIS:?set NEMESIS to the production-pinned python}
cd "$root"
before="$root/scratch/zer13/claude-fix01/before/services/sqli-fixture/app.py"
before_manifest="$root/scratch/zer13/claude-fix01/before/infrastructure/manifests/sqli-fixture.yaml"
run () {  # <label> <env ZD_SQLI_APP or ->  <file>
  local label=$1 app=$2 file=$3
  if [ "$app" = - ]; then env -u ZD_SQLI_APP "$N" -B "$file" > "$out/$label.txt" 2>&1
  else ZD_SQLI_APP="$app" "$N" -B "$file" > "$out/$label.txt" 2>&1; fi
  local code=$?
  echo "$label | exit $code | $(grep -E '^(Ran |OK|FAILED)' "$out/$label.txt" | tail -2 | tr '\n' ' ')"
  return $code
}
{
  echo "== fail-before (pre-fix snapshot: expect FAILED) =="
  run before-main    "$before" tests/test_sqli_fixture.py        && echo "UNEXPECTED PASS" || true
  run before-http    "$before" tests/test_sqli_fixture_http.py   && echo "UNEXPECTED PASS" || true
  "$N" -B docs/evidence/ZER-41/check_manifest.py "$before_manifest" > "$out/before-manifest.txt" 2>&1 \
    && echo "before-manifest | OVERALL PASS (UNEXPECTED)" || echo "before-manifest | failed as expected"
  echo "== after (fixed service: expect OK / OVERALL PASS) =="
  run after-main     - tests/test_sqli_fixture.py
  run after-http     - tests/test_sqli_fixture_http.py
  "$N" -B docs/evidence/ZER-41/check_manifest.py > "$out/after-manifest.txt" 2>&1 \
    && echo "after-manifest | OVERALL PASS" || echo "after-manifest | FAILED (UNEXPECTED)"
} | tee "$out/summary.txt"
