"""Expected vs actual for rt1-fix-01: per finding, the regression must fail on the BEFORE harness (in the mode
named) and pass on the AFTER harness. Reads results/fail-before/*.json from fail_before.sh, writes
results/fail-before/expected-vs-actual.json (or the same in <dir>) and exits 1 on any mismatch.
    python -B check_fail_before.py [<dir written by fail_before.sh>]"""
import json
import sys
from pathlib import Path

HERE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "results" / "fail-before"
F = "Findings.test_"
EXPECT = {
    "RT1-01 host I/O error skips P7": ("isolated", [F + "rt1_01_host_disk_full_in_main_phase_still_runs_every_cleanup_step",
                                                     F + "rt1_01_host_disk_full_from_cleanup_on_and_a_failing_first_step",
                                                     F + "rt1_01_unexpected_error_in_a_trial_or_a_cleanup_step_never_skips_the_rest"]),
    "RT1-02 managedFields dropped by default": ("kubectl-default", [
        "Controller.test_controller_and_hpa_recovery_end_to_end_then_score_register_and_serve",
        F + "rt1_02_ownership_reads_ask_for_managed_fields_and_a_wrong_manager_still_fails"]),
    "RT1-03 failed control overwritten as ok": ("isolated", [F + "rt1_03_positive_control_failure_is_decided_by_the_host_and_stops_before_the_target"]),
    "RT1-04 lost create answer leaves an object, CLEAN": ("isolated", [
        F + "rt1_04_lost_create_answers_are_reconciled_by_label_and_removed_by_uid",
        F + "rt1_04_an_object_that_is_not_ours_is_never_deleted_and_cleanup_says_incomplete"]),
    "RT1-05 old/foreign events claimed": ("isolated", [F + "rt1_05_controller_and_hpa_claims_need_this_trials_objects",
                                                      "Controller.test_hpa_not_activated_is_said_so_and_no_effect_leaves_n"]),
    "N1 negative control: late control ACK fails closed (PERSISTENCE, timing recorded)": (
        "isolated", ["Faults.test_control_ack_later_than_its_deadline_fails_closed"]),
}
runs = {m: json.loads((HERE / f"{n}.json").read_text())["results"] for m, n in
        (("isolated", "fail-before-isolated"), ("kubectl-default", "fail-before-kubectl-default"), ("after", "expected-fixed"))}


def outcome(results, test):
    """Worst outcome of the test and its subtests (keys 'Class.test' and 'Class.test [subtest]')."""
    found = [v["outcome"] for k, v in results.items() if k == test or k.startswith(test + " ")]
    return "ok" if found and all(o == "ok" for o in found) else ("MISSING" if not found else "FAIL")


rows, bad = [], 0
for finding, (mode, tests) in EXPECT.items():
    for test in tests:
        before, after = outcome(runs[mode], test), outcome(runs["after"], test)
        ok = before == "FAIL" and after == "ok"
        bad += not ok
        rows.append({"finding": finding, "test": test, "before_mode": mode, "expected": "before FAIL, after ok",
                     "actual": f"before {before}, after {after}", "match": ok,
                     "before_first_failure": next((v.get("message") for k, v in sorted(runs[mode].items())
                                                   if (k == test or k.startswith(test + " ")) and v["outcome"] != "ok"), None)})
extra = sorted(k for k, v in runs["after"].items() if v["outcome"] != "ok")
out = {"rows": rows, "mismatches": bad, "after_not_ok": extra,
       "note": "isolated = before harness with a fake kubectl that returns managedFields (the H-RT1 fake), so each "
               "finding is seen on its own; kubectl-default = before harness with kubectl's real default (no managedFields)."}
(HERE / "expected-vs-actual.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"mismatches": bad, "after_not_ok": extra, "rows": len(rows)}))
sys.exit(1 if bad or extra else 0)
