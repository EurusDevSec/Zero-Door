"""Fail-before for ZER-11/39 fix-01 (ZR11-01, ZR11-02 serving/plan, N1).

The pre-fix sources are the byte snapshot scratch/zer11/claude-fix01/before/ (hashes in before.json).
Two temporary trees get the CURRENT tests; the "before" tree gets the snapshot's results.js,
measurement_view.py, verify-dashboard-baselines.py and runbook. Every test of
tests/test_dashboard_measurement.py runs in both trees: each NEGATIVE test must fail before and pass
after; every other test is a CONTROL and must pass in both. The page regression
(tests/results_page_vm.cjs) is also run on both results.js files and reported per case.
Offline; the interpreter is the Nemesis production-pin venv.

  python fail_before.py --nemesis <python> [--json out.json]
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SNAPSHOT = ROOT / "scratch/zer11/claude-fix01"
COPY = ["agent-orchestrator", "tests", "infrastructure/manifests", "infrastructure/scripts", "docs/runbooks"]
SOURCES = ["agent-orchestrator/nemesis/static/results.js", "agent-orchestrator/nemesis/measurement_view.py",
           "infrastructure/scripts/verify-dashboard-baselines.py", "docs/runbooks/dashboard-and-baselines.md"]
NEGATIVE = {
    "AdapterIntegrity.test_shape_of_consumed_fields_is_a_reason_code",              # N1
    "StaticPages.test_refresh_keeps_stale_only_for_transient_failures",            # ZR11-01
    "ResultsServer.test_serves_exactly_the_given_root_and_leaves_it_unchanged",    # ZR11-02 (3): real root
    "ResultsServer.test_other_routes_and_startup_never_reach_upstreams",
    "ResultsServer.test_cli_receipt_records_the_root_at_start_and_exit",
    "ResultsServer.test_refuses_a_root_without_a_registry_or_a_relative_root",
    "RuntimePlan.test_budget_covers_timeout_no_effect_and_verification",           # ZR11-02 (1, 2, 4, 5)
    "RuntimePlan.test_the_reviewed_inconsistencies_are_rejected",
    "RuntimePlan.test_runbook_quotes_the_computed_numbers",
}
# Runs inside a tree: every test id with its outcome, subTest failures folded into their test.
RUNNER = r"""
import json, sys, unittest
sys.path.insert(0, ".")
suite = unittest.defaultTestLoader.loadTestsFromName("test_dashboard_measurement")
def flat(s):
    for t in s:
        yield from (flat(t) if isinstance(t, unittest.TestSuite) else [t])
ids = [t.id().split(".", 1)[1] for t in flat(suite)]
result = unittest.TestResult()
suite.run(result)
bad = {}
for test, trace in result.failures + result.errors:
    key = test.id().split(".", 1)[1] if "." in test.id() else test.id()
    key = next((i for i in ids if key.startswith(i)), key)
    bad.setdefault(key, trace.strip().splitlines()[-1][:300])
json.dump({"ids": ids, "bad": bad}, open(sys.argv[1], "w"))
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(dest, before):
    for part in COPY:
        shutil.copytree(ROOT / part, dest / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if not before:
        return
    recorded = json.loads((SNAPSHOT / "before.json").read_text())["files"]
    for name in SOURCES:
        source = SNAPSHOT / "before" / name
        if sha(source) != recorded[name]:
            raise SystemExit(f"snapshot hash differs: {name}")
        shutil.copyfile(source, dest / name)


def run(dest, python):
    out = dest / "outcome.json"
    subprocess.run([python, "-B", "-c", RUNNER, str(out)], cwd=dest / "tests", capture_output=True, text=True, timeout=900)
    return json.loads(out.read_text())


def page(dest):
    done = subprocess.run(["node", str(dest / "tests/results_page_vm.cjs"), str(dest / SOURCES[0])], capture_output=True, text=True, timeout=120)
    return {c["name"]: c["ok"] for c in json.loads(done.stdout)["cases"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nemesis", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    python = str(Path(args.nemesis).resolve())  # absolute: suites run with the temporary tree as cwd
    with tempfile.TemporaryDirectory() as tmp:
        outcome, cases = {}, {}
        for name, before in (("before", True), ("after", False)):
            dest = Path(tmp) / name
            dest.mkdir()
            tree(dest, before)
            outcome[name] = run(dest, python)
            cases[name] = page(dest)
    rows, ok = [], True
    for test in outcome["after"]["ids"]:
        kind = "NEGATIVE" if test in NEGATIVE else "CONTROL"
        before_ok = test in outcome["before"]["ids"] and test not in outcome["before"]["bad"]
        after_ok = test not in outcome["after"]["bad"]
        passed = after_ok and (not before_ok if kind == "NEGATIVE" else before_ok)
        ok &= passed
        rows.append({"test": test, "class": kind, "before": "pass" if before_ok else "fail: " + outcome["before"]["bad"].get(test, "absent"),
                     "after": "pass" if after_ok else "fail: " + outcome["after"]["bad"][test], "pass": passed})
        print(("PASS " if passed else "FAIL ") + kind.ljust(8), test, "| before:", rows[-1]["before"][:90], "| after:", rows[-1]["after"][:60], flush=True)
    ok &= NEGATIVE <= set(outcome["after"]["ids"])
    page_rows = [{"case": c, "before": cases["before"].get(c), "after": cases["after"][c]} for c in cases["after"]]
    ok &= all(r["after"] for r in page_rows)
    for r in page_rows:
        print("PAGE", "after" if r["after"] else "AFTER-FAIL", "before " + ("pass" if r["before"] else "fail"), r["case"])
    summary = {"snapshot": "scratch/zer11/claude-fix01/before.json", "verdict": "PASS" if ok else "FAIL",
               "negative": sum(r["class"] == "NEGATIVE" for r in rows), "control": sum(r["class"] == "CONTROL" for r in rows),
               "page_cases": {"total": len(page_rows), "fail_before": sum(not r["before"] for r in page_rows)},
               "results": rows, "page": page_rows}
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=1, sort_keys=True)
    print("VERDICT", summary["verdict"], json.dumps({k: summary[k] for k in ("negative", "control", "page_cases")}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
