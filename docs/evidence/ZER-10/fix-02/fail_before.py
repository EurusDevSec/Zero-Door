"""fix-02 fail-before / pass-after: the new regressions and Codex's retest01 counterexamples, run on the
byte snapshot taken before any fix-02 edit (fix-02/before/) and on the current tree.

Run from the repository root: python -B docs/evidence/ZER-10/fix-02/fail_before.py [--json NEW_FILE]

Each side runs in its own temporary tree: event_pipeline from the repository (outside the package,
unchanged), measurement + fixtures from the snapshot (before) or the repository (after), and the same
NEW test files and Codex scripts on both sides. Offline only: loopback fakes the tests start themselves.
Codex's evidence is only read; the repository is not written except the --json file (mode "x").
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess  # nosec B404 - runs this repository's own tests/scripts with the current interpreter
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / "docs/evidence/ZER-10/fix-02"
BEFORE = HERE / "before"
CODEX = ROOT / "docs/evidence/ZER-10/codex-retest01"

# test id -> NEGATIVE (must fail before, pass after) or CONTROL (must pass after; before is only recorded).
TESTS = {
    "test_measurement_probe.Fix02Cleanup.test_switched_cookie_in_the_answer_or_a_later_page": "NEGATIVE",
    "test_measurement_probe.Fix02Cleanup.test_followed_redirect_that_switches_the_cookie": "NEGATIVE",
    "test_measurement_probe.Fix02Cleanup.test_recaptured_identifier_cannot_retarget_the_cleanup": "NEGATIVE",
    "test_measurement_probe.Fix02Cleanup.test_failure_before_or_after_the_answer": "CONTROL",
    "test_measurement_probe.Fix02Cleanup.test_control_released_cart_needs_no_cleanup": "CONTROL",
    "test_measurement_probe.Fix02Deadlines.test_slow_or_dripping_ack_ends_at_the_flush_deadline": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_no_request_starts_after_the_deadline": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_slot_wait_is_capped_by_the_run": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_early_stop_cleanup_uses_its_own_grace": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_stop_request_bounds_the_wind_down": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_h_writes_after_the_grace_stay_pending": "NEGATIVE",
    "test_measurement_probe.Fix02Deadlines.test_clock_reading_is_bounded_and_never_redirected": "NEGATIVE",
    "test_measurement_probe.Fix02Journal.test_cancelled_sample_cleanup_is_journaled_on_disk": "NEGATIVE",
    "test_measurement_probe.Fix02Journal.test_journal_failure_refuses_before_any_request": "NEGATIVE",
    "test_measurement_probe.Fix02Journal.test_control_run_journal": "CONTROL",
    "test_measurement_scorer.Fix02TrialMetadata.test_missing_trial_bounds_are_missing_for_every_branch": "NEGATIVE",
    # TRIAL_ENDED still builds a clock model for the trial here, so fix-01 already labelled it MISSING: a control.
    "test_measurement_scorer.Fix02TrialMetadata.test_invalid_or_duplicate_trial_start": "CONTROL",
    "test_measurement_scorer.Fix02TrialMetadata.test_other_trials_keep_their_result": "NEGATIVE",
    "test_measurement_scorer.Fix02TrialMetadata.test_control_e01": "CONTROL",
    "test_measurement_metrics.Fix02Usage.test_conflict_reaches_every_bucket": "NEGATIVE",
    "test_measurement_metrics.Fix02Usage.test_conflicting_record_naming_another_model_marks_it_too": "NEGATIVE",
    "test_measurement_metrics.Fix02Usage.test_control_without_conflict": "CONTROL",
}

RUNNER = r"""
import json, sys, unittest
ids = json.loads(sys.argv[1])
out = {}
for test_id in ids:
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromName(test_id).run(result)
    problems = result.failures + result.errors
    kind = "error" if result.errors else ("fail" if result.failures else "pass")
    first = problems[0][1].strip().splitlines()[-1] if problems else None
    out[test_id] = {"outcome": kind, "detail": first}
print(json.dumps(out))
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_problems():
    record = json.loads((HERE / "before.json").read_text(encoding="utf-8"))
    fix01 = json.loads((ROOT / record["source_manifest"]).read_text(encoding="utf-8"))["files"]
    problems = [rel for rel, want in record["files"].items() if sha(BEFORE / rel) != want or fix01.get(rel) != want]
    if sha(ROOT / record["source_manifest"]) != record["source_manifest_sha256"]:
        problems.append(record["source_manifest"])
    return problems


def tree(side, base):
    source = BEFORE if side == "before" else ROOT
    shutil.copytree(ROOT / "agent-orchestrator/event_pipeline", base / "agent-orchestrator/event_pipeline",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(source / "agent-orchestrator/measurement", base / "agent-orchestrator/measurement",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(source / "tests/fixtures/zer10", base / "tests/fixtures/zer10", ignore=shutil.ignore_patterns("__pycache__"))
    for test in ROOT.glob("tests/test_measurement_*.py"):
        shutil.copy2(test, base / "tests" / test.name)
    for name in ("probe/counterexamples.py", "metrics/cases.py"):
        (base / "codex" / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CODEX / name, base / "codex" / name)


def run(args, cwd):
    done = subprocess.run([sys.executable, "-B", *args], cwd=cwd, capture_output=True, text=True, timeout=900)  # nosec B603
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"exception": "NO_JSON", "returncode": done.returncode, "stderr_tail": done.stderr.strip().splitlines()[-3:]}


def codex_checks(probe, cases):
    """Expected values of codex-retest01 (section 2 and the N1 note); True means the expected behaviour."""
    def guarded(fn):
        try:
            return bool(fn())
        except (KeyError, TypeError, IndexError, StopIteration, AttributeError):
            return False
    c = probe.get("cookie_switch_cleanup", {})
    cleanup_calls = [x for x in c.get("log", []) if x[1] == "/cart/empty"]
    return {
        "R1 cookie_switch_cleanup: foreign cart kept, cleanup sent as the sample's own session": guarded(
            lambda: c["sessions"]["foreign-user"] == ["foreign-product"] and cleanup_calls and all(x[2] != "foreign-user" for x in cleanup_calls)),
        "R2 sink_deadline_drip: ends by the 0.05 s deadline (+0.2 s slack), event stays pending": guarded(
            lambda: probe["sink_deadline_drip"]["wall_s"] < 0.25 and probe["sink_deadline_drip"]["pending"] == 1
            and probe["sink_deadline_drip"]["delivered"] == 0),
        # Only meaningful when the one sample ran and the run then waited for the next slot: if the first
        # heartbeat alone outlasts the 0.1 s cap (slow fsync), the wait is never reached and this is False.
        "R2 cadence_wait_over_cap: one sample, then ends near max_duration 0.1 + grace 0.05 (+0.4 s slack)": guarded(
            lambda: probe["cadence_wait_over_cap"]["summary"]["samples"] == 1 and probe["cadence_wait_over_cap"]["wall_s"] < 0.55),
        "R2/ZR10-10 cli_cancel_journal: cleanup detail in CLI output, early stop within grace 0.05 (+0.2 s slack)": guarded(
            lambda: probe["cli_cancel_journal"]["cleanup_in_stdout_or_outbox"] and probe["cli_cancel_journal"]["wall_s"] < 0.25),
        "R3 missing_trial: scored, MISSING with TRIAL_MISSING": guarded(
            lambda: "exception" not in cases["missing_trial"] and [(r["label"], "TRIAL_MISSING" in r["missing_reasons"])
                                                                 for r in cases["missing_trial"]["result"]["incidents"]] == [("MISSING", True)]),
        "R3 invalid_request_missing_trial: scored, MISSING with REQUEST_INVALID and TRIAL_MISSING": guarded(
            lambda: "exception" not in cases["invalid_request_missing_trial"] and [
                (r["label"], {"REQUEST_INVALID", "TRIAL_MISSING"} <= set(r["missing_reasons"]))
                for r in cases["invalid_request_missing_trial"]["result"]["incidents"]] == [("MISSING", True)]),
        "N1 conflicting_call_coverage: every bucket MISSING": guarded(
            lambda: all(g["call_coverage_status"] == "MISSING" for level in cases["conflicting_call_coverage"]["by"].values()
                        for g in level.values())),
    }


def side(name):
    with tempfile.TemporaryDirectory(prefix=f"zer10-fix02-{name}-") as tmp:
        base = Path(tmp)
        tree(name, base)
        tests = run(["-c", RUNNER, json.dumps(list(TESTS))], base / "tests")
        probe = run([str(base / "codex/probe/counterexamples.py")], base)
        cases = run([str(base / "codex/metrics/cases.py")], base)
    observed = {key: {k: v for k, v in probe.get(key, {}).items() if k in ("wall_s", "pending", "delivered", "reason", "cleanup", "exit")}
                for key in ("cookie_switch_cleanup", "sink_deadline_drip", "cadence_wait_over_cap", "cli_cancel_journal")}
    observed["cadence_wait_over_cap"]["samples"] = (probe.get("cadence_wait_over_cap", {}).get("summary") or {}).get("samples")
    observed["metrics_exceptions"] = {k: v.get("exception") for k, v in cases.items() if isinstance(v, dict)}
    return {"tests": tests, "codex": codex_checks(probe, cases), "codex_observed": observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", help="new file for the results (never overwritten)")
    args = parser.parse_args()
    report = {"snapshot_problems": snapshot_problems(), "before": side("before"), "after": side("after"), "kinds": TESTS}
    problems = list(report["snapshot_problems"])
    for test_id, kind in TESTS.items():
        before = report["before"]["tests"].get(test_id, {}).get("outcome")
        after = report["after"]["tests"].get(test_id, {}).get("outcome")
        if after != "pass":
            problems.append(f"after {after}: {test_id}")
        if kind == "NEGATIVE" and before == "pass":
            problems.append(f"negative passes before: {test_id}")
    for check, ok in report["after"]["codex"].items():
        if not ok:
            problems.append(f"after not expected: {check}")
        if report["before"]["codex"][check]:
            problems.append(f"before already expected: {check}")
    report["problems"] = problems
    report["verdict"] = "PASS" if not problems else "FAIL"
    for test_id, kind in TESTS.items():
        print(f"{kind:8} before={report['before']['tests'].get(test_id, {}).get('outcome')!s:5} "
              f"after={report['after']['tests'].get(test_id, {}).get('outcome')!s:5} {test_id.split('.', 1)[1]}")
    for check in report["after"]["codex"]:
        print(f"CODEX    before={report['before']['codex'][check]!s:5} after={report['after']['codex'][check]!s:5} {check}")
    print("problems:", problems)
    print("verdict:", report["verdict"])
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=1, sort_keys=True)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
