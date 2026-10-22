"""Fail-before for ZER-11/39: the new behaviour tests run on the pre-change sources and on the current tree.

The pre-change sources are the byte snapshot scratch/zer11/claude/before/ (hashes in before.json, HEAD
1694133). A temporary tree gets the CURRENT tests and the BEFORE sources (files absent before are
removed), so each NEGATIVE test must fail there and pass on the current tree; each CONTROL test must
pass on both. Tests of the new results adapter cannot run before it exists; they are covered by
check_mutants.py instead. Runs offline with the production-pin interpreters given on the command line.

  python fail_before.py --nemesis <python> --hephaestus <python> [--json out.json]
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "scratch/zer11/claude"
COPY = ["agent-orchestrator", "tests", "infrastructure/manifests"]
# (module, test id, interpreter role, class)
TESTS = [
    ("test_dashboard_measurement", "Http.test_status_reports_no_data_and_source_error_not_zero", "nemesis", "NEGATIVE"),
    ("test_dashboard_measurement", "Http.test_heal_history_and_logs_report_upstream_failure", "nemesis", "NEGATIVE"),
    ("test_dashboard_measurement", "Http.test_chat_generates_no_reasoning", "nemesis", "NEGATIVE"),
    ("test_dashboard_measurement", "StaticPages.test_console_has_no_kpi_path_or_synthetic_numbers", "nemesis", "NEGATIVE"),
    ("test_dashboard_modes", "ConsumerModes.test_only_b1_auto_decides_through_the_real_consumer", "hephaestus", "NEGATIVE"),
    ("test_dashboard_modes", "ManualTrigger.test_bm_operator_decision_is_admitted_but_production_executor_stays_disabled", "hephaestus", "NEGATIVE"),
    ("test_dashboard_modes", "ManualTrigger.test_positive_control_one_action_per_operator_decision", "hephaestus", "NEGATIVE"),
    ("test_dashboard_modes", "ManualTrigger.test_mode_refusals_hold_even_with_an_executor", "hephaestus", "NEGATIVE"),
    ("test_dashboard_modes", "ManualTrigger.test_b0_with_a_forged_operator_decision_is_still_refused", "hephaestus", "CONTROL"),
    ("test_dashboard_modes", "ManualTrigger.test_trigger_needs_the_trusted_context_and_heal_operator", "hephaestus", "CONTROL"),
    ("test_command_modes", "ModeTests", "hephaestus", "CONTROL"),
    ("test_command_guard_integration", "EntrypointTests", "nemesis", "CONTROL"),
    ("test_event_agents", "AgentHttpTests", "hephaestus", "CONTROL"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(dest, before):
    for part in COPY:
        shutil.copytree(ROOT / part, dest / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if not before:
        return
    recorded = json.loads((SNAPSHOT / "before.json").read_text())["files"]
    for name, digest in recorded.items():
        if name.startswith("tests/") or not any(name.startswith(p + "/") for p in COPY):
            continue  # current tests on old sources; docs/CI are not code under test
        target = dest / name
        if digest is None:
            if target.exists():
                target.unlink()
            continue
        source = SNAPSHOT / "before" / name
        if sha(source) != digest:
            raise SystemExit(f"snapshot hash differs: {name}")
        shutil.copyfile(source, target)


def run(dest, python, module, test):
    done = subprocess.run([python, "-B", "-m", "unittest", f"{module}.{test}"], cwd=dest / "tests",
                          capture_output=True, text=True, timeout=600)
    tail = [line for line in done.stderr.splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    return {"exit": done.returncode, "summary": " ".join(tail)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nemesis", required=True)
    parser.add_argument("--hephaestus", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    # Absolute: the suites run with the temporary tree as working directory.
    pythons = {"nemesis": str(Path(args.nemesis).resolve()), "hephaestus": str(Path(args.hephaestus).resolve())}
    results, ok = [], True
    with tempfile.TemporaryDirectory() as tmp:
        trees = {}
        for name, before in (("before", True), ("after", False)):
            trees[name] = Path(tmp) / name
            trees[name].mkdir()
            tree(trees[name], before)
        for module, test, role, kind in TESTS:
            row = {"test": f"{module}.{test}", "class": kind, "python": role,
                   "before": run(trees["before"], pythons[role], module, test),
                   "after": run(trees["after"], pythons[role], module, test)}
            expected_before = 0 if kind == "CONTROL" else "nonzero"
            row["pass"] = row["after"]["exit"] == 0 and ((row["before"]["exit"] == 0) if kind == "CONTROL" else row["before"]["exit"] != 0)
            ok &= row["pass"]
            results.append(row)
            print(("PASS " if row["pass"] else "FAIL ") + kind.ljust(8), row["test"], "| before:", row["before"]["summary"],
                  "| after:", row["after"]["summary"], flush=True)
    summary = {"snapshot_head": json.loads((SNAPSHOT / "before.json").read_text())["head"], "verdict": "PASS" if ok else "FAIL",
               "negative": sum(r["class"] == "NEGATIVE" for r in results), "control": sum(r["class"] == "CONTROL" for r in results),
               "results": results}
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=1, sort_keys=True)
    print("VERDICT", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
