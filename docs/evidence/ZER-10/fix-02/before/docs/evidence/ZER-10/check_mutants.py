"""ZER-10 mutant check: each mutant breaks exactly one measurement rule; the offline suites must fail.

Run from the repository root: python -B docs/evidence/ZER-10/check_mutants.py [--json OUT_NEW_FILE]
A clean control run must pass. Offline only (loopback fakes owned by the tests).
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))

import event_pipeline.contract as contract  # noqa: E402
import measurement.clock as clock  # noqa: E402
import measurement.flows as flows  # noqa: E402
import measurement.metrics as metrics  # noqa: E402
import measurement.output as output  # noqa: E402
import measurement.recovery as recovery  # noqa: E402
import measurement.scorer as scorer  # noqa: E402
import measurement.sink as sink  # noqa: E402


def t_rec_from_verified_at():
    original = scorer.evaluate

    def wrong(*args, **kwargs):
        result = original(*args, **kwargs)
        if result["verified"]:
            result["verified"]["t_rec"] = result["verified"]["recovery_verified_at"]
        return result
    return patch.object(scorer, "evaluate", wrong)


def unknown_effect_leaves_n():
    original = metrics.base_counts

    def wrong(incidents):
        return original([r for r in incidents if r["effect"] != "UNKNOWN_EFFECT"])
    return patch.object(metrics, "base_counts", wrong)


def missing_counts_as_pass():
    original = metrics.threshold_metric

    def wrong(eligible, counts, value_of, threshold_s, missing_of, unobserved_of, mean_pool=None):
        return original(eligible, counts, value_of, threshold_s, lambda r: False, unobserved_of, mean_pool)
    return patch.object(metrics, "threshold_metric", wrong)


def h_into_o():
    sources = dict(contract.SOURCES, PROBE_SAMPLE=("O", {"probe"}), PROBE_HEARTBEAT=("O", {"probe"}))
    return patch.object(contract, "SOURCES", sources)


def gap_counts_as_up():
    original = metrics.flow_intervals

    def wrong(*args):
        result = original(*args)
        result["U"] = []
        return result
    return patch.object(metrics, "flow_intervals", wrong)


def lost_sequence_ignored():
    return patch.object(recovery, "joined", lambda a, b, gap_ms: b["t"] - a["t"] <= gap_ms)


def http_status_only():
    return patch.object(flows.Flow, "assertions", lambda self, *args: None)


def cancel_as_failure():
    original = flows.Flow.run

    def wrong(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        if result["detail"] == "CANCELLED":
            result["detail"], result["reason"] = "TIMEOUT", "TRANSACTION_DEADLINE"
        return result
    return patch.object(flows.Flow, "run", wrong)


def no_effect_without_coverage():
    return patch.object(scorer.Scorer, "no_effect", lambda self, inc, p: "CONFIRMED_NO_EFFECT")


def unsynced_clock_trusted():
    return patch.object(clock.ClockModel, "state", lambda self, clock_id: (True, []))


def evaluator_trusted():
    def wrong(self, inc, r, result, probe_clock):
        r["evaluator_mismatch"], r["evaluator_issues"] = False, []
    return patch.object(scorer.Scorer, "compare_evaluator", wrong)


def lost_request_dropped():
    """ZR10-01 reverted: an unusable ATTACK_REQUESTED leaves the cohort and nothing says so."""
    def wrong(self, gts):
        self.cohort = {"complete": True, "problems": []}
    return patch.object(scorer.Scorer, "lost_requests", wrong)


def unplaced_detect_skipped():
    """ZR10-02 reverted: a DETECTED that cannot be compared with T_req is dropped, so the incident looks MISSED."""
    original = scorer.Scorer.score_incident

    def wrong(self, inc):
        keep = []
        for event in inc["detected"]:
            t = self.stamp_of(event)
            if t is not None and inc["t_req"] is not None and t.comparable(inc["t_req"]):
                keep.append(event)
        inc["detected"] = keep
        return original(self, inc)
    return patch.object(scorer.Scorer, "score_incident", wrong)


def unplaced_success_ignored():
    """ZR10-02 (executor) reverted: a SUCCESS on an unverified clock is ignored, so reaction becomes NO_SUCCESS."""
    original = scorer.Scorer.score_incident

    def wrong(self, inc):
        for attempt in inc["actions"].values():
            done = attempt.get("ACTION_COMPLETED", [])
            attempt["ACTION_COMPLETED"] = [c for c in done if self.stamp_of(c) is not None and self.stamp_of(c).verified
                                           or c["clock"]["clock_source"] == "HOST_SHARED"]
        return original(self, inc)
    return patch.object(scorer.Scorer, "score_incident", wrong)


def episodes_unkeyed():
    """ZR10-03 reverted: every alert joins one episode stream, whatever its signature/service."""
    return patch.object(metrics, "episode_key", lambda event: ("all", "all"))


def stream_from_slots():
    """ZR10-03 reverted: a rate per hour is reported whenever every slot is known, coverage or not."""
    original = metrics.m5

    def wrong(scorer_, trial_id, model, start, w0, w1, slot_s, episode_gap_s, cfg):
        row = original(scorer_, trial_id, model, start, w0, w1, slot_s, episode_gap_s, cfg)
        if row["unknown"] == 0:
            row.update(episodes_per_hour=round(row["episodes_observed"] / ((w1 - w0) / 3.6e6), 6),
                       episode_verdict="OK", verdict="OK")
        return row
    return patch.object(metrics, "m5", wrong)


def m6_from_completed():
    """ZR10-04 reverted: M6 counts ACTION_COMPLETED in W, so a started action without terminal is 0."""
    original = metrics.m6

    def wrong(scorer_, trial_id, model, start, w0, w1, cfg):
        row = original(scorer_, trial_id, model, start, w0, w1, cfg)
        if "M6" not in row:
            done = [e for e in scorer_.of("ACTION_COMPLETED", trial_id)
                    if w0 <= metrics.placed_ms(model, start, e) < w1]
            row["M6_actions_executed"] = row["M6_actions_observed"] = len(done)
            row["M6_terminal"] = dict(row["M6_terminal"], MISSING=0)
        return row
    return patch.object(metrics, "m6", wrong)


def usage_from_valid_only():
    """ZR10-05 reverted: only valid LLM_CALL records count; no coverage from decisions or invalid records."""
    stack = contextlib.ExitStack()
    stack.enter_context(patch.object(metrics, "unusable", lambda scorer_, typ: []))
    stack.enter_context(patch.object(metrics, "LLM_SOURCES", set()))
    return stack


def gt_unchecked():
    """ZR10-06 reverted: ground-truth constraints are used without a type/range check."""
    return patch.object(metrics, "constraint_problem", lambda action, rule: None)


def first_guard_wins():
    """ZR10-07 reverted: no cardinality check, so the first verdict in ingest order decides."""
    return patch.object(scorer.Scorer, "cardinality", lambda self: None)


def cart_item_only():
    """ZR10-08 reverted: the cart check only looks for the product id, not one line with quantity 1."""
    original = flows.Flow.assertions

    def wrong(self, step, response, env, state, memory):
        if step["name"] == "cart":
            step = {k: v for k, v in step.items() if k not in ("count", "capture")}
            step["contains"] = ["{product_id}"]
        return original(self, step, response, env, state, memory)
    return patch.object(flows.Flow, "assertions", wrong)


def step_deadline_ignored():
    """ZR10-09 reverted: steps only see the transaction deadline."""
    original = flows.Flow.deadline
    return patch.object(flows.Flow, "deadline", staticmethod(lambda bounds, began: original(dict(bounds, step_s=None), began)))


def run_cap_ignored():
    """ZR10-09 reverted: the run cap does not cut a transaction in flight."""
    original = flows.Flow.deadline
    return patch.object(flows.Flow, "deadline", staticmethod(lambda bounds, began: original(dict(bounds, run=flows.NEVER), began)))


def ownership_from_status():
    """ZR10-10 reverted: a sent create request (a 201) is taken as ownership, so cleanup deletes what it got back."""
    original = flows.Flow.cleanup

    def wrong(self, env, state, http, cleanup_ns=None):
        state["owned"] |= state["claimed"]
        return original(self, env, state, http, cleanup_ns)
    return patch.object(flows.Flow, "cleanup", wrong)


def cleanup_skipped_on_interrupt():
    """ZR10-10 reverted: an interrupt leaves the transaction before its cleanup."""
    hit = {"interrupted": False}
    run, cleanup = flows.Flow.run, flows.Flow.cleanup

    def wrong_run(self, deadline_ns, cancel, memory, http=flows.request, **kwargs):
        def watch(*args):
            try:
                return http(*args)
            except KeyboardInterrupt:
                hit["interrupted"] = True
                raise
        hit["interrupted"] = False
        return run(self, deadline_ns, cancel, memory, http=watch, **kwargs)

    def wrong_cleanup(self, *args, **kwargs):
        return {} if hit["interrupted"] else cleanup(self, *args, **kwargs)
    stack = contextlib.ExitStack()
    stack.enter_context(patch.object(flows.Flow, "run", wrong_run))
    stack.enter_context(patch.object(flows.Flow, "cleanup", wrong_cleanup))
    return stack


def sink_follows_redirect_and_proxy():
    """ZR10-11 reverted: the default urllib opener (redirects, environment proxies) carries the token."""
    from urllib.request import build_opener
    original = sink.HttpHSink.__init__

    def wrong(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self.opener = build_opener()
    return patch.object(sink.HttpHSink, "__init__", wrong)


def any_ack_accepted():
    """ZR10-11 reverted: any answer naming the event is an ACK, whatever its status or origin."""
    original = sink.HttpHSink.deliver

    def wrong(self, event):
        try:
            return original(self, event)
        except sink.SinkRefused:
            return "DELIVERED", "RECORDED"
    return patch.object(sink.HttpHSink, "deliver", wrong)


def output_ignores_other_exports():
    """ZR10-N1 reverted: only the primary H/O exports bound the output location."""
    original = output.write
    return patch.object(output, "write", lambda destination, document, inputs: original(destination, document, list(inputs)[:2]))


MUTANTS = {
    "T_REC_FROM_VERIFIED_AT": (t_rec_from_verified_at, ["test_measurement_scorer"]),
    "UNKNOWN_EFFECT_LEAVES_N": (unknown_effect_leaves_n, ["test_measurement_scorer"]),
    "MISSING_COUNTS_AS_PASS": (missing_counts_as_pass, ["test_measurement_scorer", "test_measurement_metrics"]),
    "H_INTO_O": (h_into_o, ["test_measurement_probe"]),
    "GAP_COUNTS_AS_UP": (gap_counts_as_up, ["test_measurement_metrics"]),
    "LOST_SEQUENCE_IGNORED": (lost_sequence_ignored, ["test_measurement_recovery"]),
    "HTTP_STATUS_ONLY": (http_status_only, ["test_measurement_probe"]),
    "CANCEL_AS_FAILURE": (cancel_as_failure, ["test_measurement_probe"]),
    "NO_EFFECT_WITHOUT_COVERAGE": (no_effect_without_coverage, ["test_measurement_scorer"]),
    "UNSYNCED_CLOCK_TRUSTED": (unsynced_clock_trusted, ["test_measurement_scorer"]),
    "EVALUATOR_TRUSTED": (evaluator_trusted, ["test_measurement_scorer"]),
    # fix-01: each mutant restores one behaviour Codex found (ZR10-01..11, N1); the new regressions must fail.
    "FIX01_LOST_REQUEST_DROPPED": (lost_request_dropped, ["test_measurement_scorer.Fix01Cohort"]),
    "FIX01_UNPLACED_DETECT_SKIPPED": (unplaced_detect_skipped, ["test_measurement_scorer.Fix01Clocks"]),
    "FIX01_UNPLACED_SUCCESS_IGNORED": (unplaced_success_ignored, ["test_measurement_scorer.Fix01Clocks"]),
    "FIX01_EPISODES_UNKEYED": (episodes_unkeyed, ["test_measurement_metrics.Fix01Benign"]),
    "FIX01_STREAM_FROM_SLOTS": (stream_from_slots, ["test_measurement_metrics.Fix01Benign"]),
    "FIX01_M6_FROM_COMPLETED": (m6_from_completed, ["test_measurement_metrics.Fix01Benign"]),
    "FIX01_USAGE_FROM_VALID_ONLY": (usage_from_valid_only, ["test_measurement_metrics.Fix01Usage"]),
    "FIX01_GT_UNCHECKED": (gt_unchecked, ["test_measurement_metrics.Fix01GroundTruthAndOrder"]),
    "FIX01_FIRST_GUARD_WINS": (first_guard_wins, ["test_measurement_metrics.Fix01GroundTruthAndOrder"]),
    "FIX01_CART_ITEM_ONLY": (cart_item_only, ["test_measurement_probe.Fix01Transaction"]),
    "FIX01_STEP_DEADLINE_IGNORED": (step_deadline_ignored, ["test_measurement_probe.Fix01Transaction"]),
    "FIX01_RUN_CAP_IGNORED": (run_cap_ignored, ["test_measurement_probe.Fix01Transaction"]),
    "FIX01_OWNERSHIP_FROM_STATUS": (ownership_from_status, ["test_measurement_probe.Fix01Transaction"]),
    "FIX01_CLEANUP_SKIPPED_ON_INTERRUPT": (cleanup_skipped_on_interrupt, ["test_measurement_probe.Fix01Transaction"]),
    "FIX01_SINK_FOLLOWS_REDIRECT_AND_PROXY": (sink_follows_redirect_and_proxy, ["test_measurement_probe.Fix01HSink"]),
    "FIX01_ANY_ACK_ACCEPTED": (any_ack_accepted, ["test_measurement_probe.Fix01HSink"]),
    "FIX01_OUTPUT_IGNORES_OTHER_EXPORTS": (output_ignores_other_exports, ["test_measurement_cli"]),
}


def run(modules, mutant=None):
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules)
    stream = io.StringIO()
    with (mutant() if mutant else contextlib.nullcontext()):
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    return {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
            "failed_tests": sorted({str(t).split(" ")[0] for t, _ in result.failures + result.errors})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", help="new file for the results")
    args = parser.parse_args()
    modules = sorted({m.split(".")[0] for _, ms in MUTANTS.values() for m in ms})
    report = {"control": run(modules), "mutants": {}}
    for name, (factory, targets) in MUTANTS.items():
        outcome = run(targets, factory)
        outcome["caught"] = outcome["failures"] + outcome["errors"] > 0
        report["mutants"][name] = outcome
        print(f"{name:28} caught={outcome['caught']} failed={outcome['failures'] + outcome['errors']}/{outcome['run']}")
    control_ok = report["control"]["failures"] + report["control"]["errors"] == 0
    report["verdict"] = "PASS" if control_ok and all(m["caught"] for m in report["mutants"].values()) else "FAIL"
    print(f"control: {report['control']['run']} tests, failures {report['control']['failures']}, errors {report['control']['errors']}")
    print("verdict:", report["verdict"])
    if args.json:
        with open(args.json, "x") as handle:
            json.dump(report, handle, indent=1, sort_keys=True)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
