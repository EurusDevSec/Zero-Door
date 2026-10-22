#!/usr/bin/env bash
# FX41-R1..R3 behavioural fail-before / after. The updated suites and the adapted edge replay run against the
# fix01 snapshot Codex kept (scratch/zer13/codex-retest01/before/app.py) — the new regressions FAIL there
# while every older case still passes — and against the current service, where everything passes. Offline.
#   NEMESIS=<python> bash docs/evidence/ZER-41/fix02/fail_before.sh <new results dir>
set -uo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
out=$(realpath -m "${1:?results dir}"); mkdir -p "$out"
N=${NEMESIS:?set NEMESIS to the production-pinned python}
cd "$root"
before="$root/scratch/zer13/codex-retest01/before/app.py"
current="$root/services/sqli-fixture/app.py"
suite () {  # <label> <app> <test file>
  ZD_SQLI_APP="$2" "$N" -B "$3" -v > "$out/$1.txt" 2>&1
  local code=$?
  echo "$1 | exit $code | $(grep -E '^(Ran |OK|FAILED)' "$out/$1.txt" | tr '\n' ' ')"
  grep -E '\.\.\. (FAIL|ERROR)$' "$out/$1.txt" | sed 's/^ *//; s/ (__main__[^)]*)//' > "$out/$1.failing.txt"
}
{
  echo "== fail-before: fix01 snapshot (expect only the new FX41 regressions to fail) =="
  suite before-main "$before" tests/test_sqli_fixture.py
  suite before-http "$before" tests/test_sqli_fixture_http.py
  "$N" -B docs/evidence/ZER-41/fix02/edges_replay.py "$before" "$out/before-edges.json" > /dev/null 2>&1
  echo "before-edges | $("$N" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['dribbling_body']['elapsed_s'],d['dribbling_body']['status_line'],'|',d['unhandled_method']['status_line'],'| canary',d['startup_failure_process']['canary_on_streams'],'traceback',d['startup_failure_process']['traceback_on_streams'])" "$out/before-edges.json")"
  echo "== after: current service (expect OK) =="
  suite after-main "$current" tests/test_sqli_fixture.py
  suite after-http "$current" tests/test_sqli_fixture_http.py
  "$N" -B docs/evidence/ZER-41/fix02/edges_replay.py "$current" "$out/after-edges.json" > /dev/null 2>&1
  echo "after-edges | $("$N" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['dribbling_body']['elapsed_s'],d['dribbling_body']['status_line'],'|',d['unhandled_method']['status_line'],'| canary',d['startup_failure_process']['canary_on_streams'],'traceback',d['startup_failure_process']['traceback_on_streams'])" "$out/after-edges.json")"
} | tee "$out/summary.txt"
