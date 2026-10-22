#!/usr/bin/env bash
# ZER-11/39 fix-01 offline regressions: the first package's run_regressions.sh unchanged (new and related
# suites on each pinned interpreter, measurement baseline, CI boundary, Bandit, whitespace), then the
# fix-01 additions: page regression, plan-check, Codex's replays. No cluster, Docker or model.
#   NEMESIS=<python> HEPHAESTUS=<python> GUARDS=<python> BANDIT=<python with bandit> bash run_regressions.sh <log>
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root=$(cd -- "$here/../../../.." && pwd)
log=$(realpath -m "${1:?log file}")
cd "$root"
bash "$here/../run_regressions.sh" "$log"
status=$?
sed -i '/^OVERALL exit/d' "$log"
echo "== fix-01 additions" >> "$log"
step() {
  local name=$1; shift
  local out
  out=$("$@" 2>&1); local code=$?
  printf '%s | exit %s | %s\n' "$name" "$code" "$(printf '%s\n' "$out" | tail -1 | cut -c1-200 | sed 's/ *$//')" >> "$log"
  [ "$code" -eq 0 ] || status=1
}
step "node results_page_vm.cjs (cases ok/total)" node -e '
const r = require("child_process").spawnSync("node", ["tests/results_page_vm.cjs"], {encoding: "utf8"});
const c = JSON.parse(r.stdout).cases; console.log(c.filter(x => x.ok).length + "/" + c.length); process.exit(r.status);'
step "plan-check (problems)" "$NEMESIS" -B -c '
import json, subprocess, sys
out = subprocess.run([sys.executable, "-B", "infrastructure/scripts/verify-dashboard-baselines.py", "plan-check"], capture_output=True, text=True)
m = json.loads(out.stdout); print(m["problems"], m["totals"]); sys.exit(out.returncode)'
step "Codex ui-counterexample replay (states)" node -e '
const r = require("child_process").spawnSync("node", ["docs/evidence/ZER-11/fix-01/replay_codex_ui.cjs"], {encoding: "utf8"});
const rows = JSON.parse(r.stdout); console.log(rows.map(x => x.http + ":" + x.state + ":" + (x.kpi ? "kpi" : "cleared")).join(" "));
process.exit(rows.every(x => (x.http === 503) === (x.state === "STALE" && x.kpi !== "")) ? 0 : 1);'
step "Codex adapter-probe (results)" "$NEMESIS" -B -c '
import json, subprocess, sys
out = subprocess.run([sys.executable, "-B", "docs/evidence/ZER-11/codex-review/adapter-probe.py"], capture_output=True, text=True)
rows = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
print(" ".join(r["case"] + ":" + r.get("detail", r["result"]) for r in rows))
sys.exit(0 if all(r["result"] in ("ResultError", "ACCEPT") for r in rows) and [r["case"] for r in rows if r["result"] == "ACCEPT"] == ["kpi_type"] else 1)'
step "bandit fix-01 python" "$BANDIT" -m bandit -q agent-orchestrator/nemesis/measurement_view.py infrastructure/scripts/verify-dashboard-baselines.py
echo "OVERALL exit $status" >> "$log"
sed -i 's/[[:space:]]*$//' "$log"  # steps with an empty summary end in "| "
exit $status
