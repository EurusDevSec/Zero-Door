"""Aggregates: uptime bounds (D-05/RV-01), benign M5/M6, usage/cost M11, decision M1/M3/M4, R(t).

Hand-computed expectations in tests/fixtures/zer10/expected.json. Offline only.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))
from builder import Trace, e01, iso  # noqa: E402
from measurement.metrics import flow_intervals, kpi, length, run_metrics, subtract  # noqa: E402
from measurement.raw import load  # noqa: E402
from measurement.scorer import Scorer  # noqa: E402

EXPECTED = json.loads((ROOT / "tests/fixtures/zer10/expected.json").read_text())


def scored(trace, options=None):
    with tempfile.TemporaryDirectory() as tmp:
        h, o, _ = trace.seal(tmp)
        scorer = Scorer(*load(h, o), options or {})
        result = scorer.run()
        result["metrics"] = run_metrics(scorer, result, options or {})
        return result


class Uptime(unittest.TestCase):
    def two_flows(self):
        tr = e01()
        start = next(e for _, e in tr.events if e["event_type"] == "TRIAL_STARTED")
        start["payload"]["probes"].append({"probe_id": "prb-1", "flow": "fixture", "probe_version": "f0", "clock_id": "clk_probe_ext"})
        tr.probe_run([(22, 260, True)], probe_id="prb-1", version="f0", flow="fixture", skip=set(range(150, 170)))
        return tr

    def test_union_of_gaps_and_outages_is_counted_once(self):
        result = scored(self.two_flows(), {"required_flows": ["checkout", "fixture"]})
        up = next(iter(result["metrics"]["uptime"].values()))
        for key, value in EXPECTED["UPTIME_TWO_FLOWS"].items():
            if key != "derivation":
                self.assertEqual(value, up[key], (key, up))

    def test_missing_flow_is_unobserved_not_up(self):
        result = scored(e01(), {"required_flows": ["checkout", "fixture"]})
        up = next(iter(result["metrics"]["uptime"].values()))
        self.assertEqual("FAIL", up["verdict"])
        self.assertEqual(0.0, up["A_lower"])  # the fixture flow is unobserved over all of W
        self.assertEqual({"reason": "PROBE_NOT_REGISTERED"}, up["flows"]["fixture"])

    def test_inputs_are_explicit(self):
        result = scored(e01(), {})
        self.assertEqual("NO_REQUIRED_FLOWS", next(iter(result["metrics"]["uptime"].values()))["reason"])
        tr = e01()
        next(e for _, e in tr.events if e["event_type"] == "TRIAL_STARTED")["payload"]["warmup_end"] = None
        self.assertEqual("WARMUP_NOT_REACHED", next(iter(scored(tr, {"required_flows": ["checkout"]})["metrics"]["uptime"].values()))["reason"])
        result = scored(e01(syncs=()), {"required_flows": ["checkout"]})
        self.assertEqual("CLOCK_UNVERIFIED", next(iter(result["metrics"]["uptime"].values()))["reason"])

    def test_interval_helpers(self):
        self.assertEqual([[0, 5], [8, 10]], subtract([[0, 10]], [[5, 8]]))
        self.assertEqual(10, length([[0, 5], [3, 10]]))
        f01 = {"delta_s": 1, "gap_s": 2, "k": 3}
        flat = [{"t": t * 1000, "ok": t not in (5, 7), "seq": t} for t in range(0, 20)]
        f = flow_intervals(flat, 0, 20_000, f01)
        # A lone pass at 6 inside the outage keeps it open; closed at 8 (first of 8,9,10).
        self.assertEqual([[5000, 8000]], f["point"])
        self.assertEqual([[5000, 7000]], f["min"])
        self.assertEqual([[4000, 8000]], f["max"])


class Benign(unittest.TestCase):
    def c0(self):
        tr = Trace("B1")
        tr.run_started()
        tr.trial_started()
        tr.sync(10), tr.sync(300)
        tr.probe_run([(20, 260, True)])
        tr.detected(50, incident=False)
        tr.trial_ended()
        return tr

    def test_no_coverage_is_unknown_not_zero(self):
        tr = self.c0()
        opts = {"benign": {"trial_ids": [tr.trial], "slot_s": 60, "episode_gap_s": 90, "provenance": "ILLUSTRATIVE w_b/g_b"}}
        m = scored(tr, opts)["metrics"]["M5_M6_benign"]["trials"][tr.trial]
        for key in ("N_slot", "last_slot_s", "hit", "unknown", "bounds", "verdict"):
            self.assertEqual(EXPECTED["BENIGN_NO_COVERAGE"][key], m[key], key)
        self.assertIsNone(m["episodes_per_hour"])
        opts["benign"]["detector_coverage"] = {tr.trial: [[iso(22), iso(300)]]}
        m = scored(tr, opts)["metrics"]["M5_M6_benign"]["trials"][tr.trial]
        for key in ("bounds", "episodes_observed", "episodes_per_hour", "verdict"):
            self.assertEqual(EXPECTED["BENIGN_FULL_COVERAGE"][key], m[key], key)
        self.assertEqual("MISSING", scored(tr)["metrics"]["M5_M6_benign"]["status"])


class Usage(unittest.TestCase):
    def test_retry_counted_redelivery_not(self):
        tr = e01()
        call = next(e for _, e in tr.events if e["event_type"] == "LLM_CALL")
        tr.events.remove(("O", call))
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        first = tr.llm_call(132.0, dec, attempt=1, usage=(100, 0), usd=0.001, outcome="TIMEOUT")
        second = tr.llm_call(132.9, dec, attempt=2, retry_reason="TIMEOUT")
        tr.events.append(("O", copy.deepcopy(second)))
        u = scored(tr)["metrics"]["M11_usage"]
        run = next(iter(u["by"]["run"].values()))
        for key in ("calls", "retries", "input_tokens", "output_tokens", "usd", "usage_status"):
            self.assertEqual(EXPECTED["USAGE_RETRY"][key], run[key], key)
        self.assertIn(dec["incident_id"], u["by"]["incident"])
        del first

    def test_missing_usage_stays_missing_and_b1_is_na(self):
        tr = e01()
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        tr.llm_call(133.2, dec, attempt=2, retry_reason="SCHEMA", usage=None, usd=None)
        run = next(iter(scored(tr)["metrics"]["M11_usage"]["by"]["run"].values()))
        self.assertEqual(EXPECTED["USAGE_MISSING"]["usage_status"], run["usage_status"])
        self.assertEqual(EXPECTED["USAGE_MISSING"]["input_tokens_lower_bound"], run["input_tokens"])
        self.assertIn("lower bound", run["note"])
        tr = Trace("B1")
        tr.run_started(), tr.trial_started(), tr.sync(10), tr.sync(300), tr.trial_ended()
        self.assertEqual("N/A", scored(tr)["metrics"]["M11_usage"]["status"])


class Decisions(unittest.TestCase):
    def test_wrong_proposal_blocked_by_guard_is_not_correct(self):
        tr = Trace("B1")
        tr.run_started(), tr.ground_truth(), tr.trial_started(), tr.sync(10), tr.sync(300)
        tr.probe_run([(20, 100, True), (101, 188, False), (189, 260, True)])
        tr.attack()
        alert = tr.detected(131)
        dec = tr.decision(133, alert, action="BLOCK_IP", params={"sources": ["10.0.0.9"], "ttl_s": 60})
        tr.guard(133.1, dec, verdict="REJECT")
        tr.effect(), tr.stop(), tr.trial_ended()
        d = scored(tr)["metrics"]["decisions"]
        e = EXPECTED["M1_GUARD"]
        self.assertEqual(e["outcome"], d["rows"][0]["outcome"])
        self.assertEqual(e["true_block"], d["M3"]["true_block"])
        pooled = d["M1"]["pooled_check"]
        self.assertEqual((e["M1_numerator"], e["M1_N"]), (pooled["numerator"], pooled["N"]))
        self.assertEqual("UNDETERMINED", d["M1"]["macro_C1_C4"]["status"])
        self.assertEqual(0, d["actions"]["executed"])  # blocked: nothing executed

    def test_false_action_counts_an_executed_incorrect_proposal(self):
        tr = e01(action_status=None)
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        dec["payload"]["proposal"] = {"action_type": "SCALE_UP", "params": {"service": "frontend", "replicas": 9}}
        tr.action(dec)
        actions = scored(tr)["metrics"]["decisions"]["actions"]
        self.assertEqual((1, 1, 1), (actions["executed"], actions["false_action"], actions["terminal"]["SUCCESS"]))

    def test_correct_proposal_no_trigger_and_fallback(self):
        d = scored(e01())["metrics"]["decisions"]
        self.assertEqual("CORRECT", d["rows"][0]["outcome"])
        self.assertEqual(1, d["M3"]["accept_correct"])
        self.assertEqual(2.0, d["rows"][0]["decision_latency_s"])
        d = scored(e01(detect=None))["metrics"]["decisions"]
        self.assertEqual("NO_TRIGGER", d["rows"][0]["outcome"])
        self.assertEqual(1, d["M1"]["pooled_check"]["N"])  # missed detection stays in the M1 denominator
        tr = e01(detect=None)
        alert = tr.detected(131)
        llm = tr.decision(132, alert, kind="TIMEOUT")
        tr.decision(133, alert, source="decision_rules", fallback_of=llm["decision_id"])
        d = scored(tr)["metrics"]["decisions"]
        self.assertEqual("FALLBACK_RULES", d["rows"][0]["outcome"])
        self.assertEqual(1, d["M4"]["numerator"])

    def test_missing_ground_truth_is_unknown_cohort(self):
        tr = e01()
        tr.events = [x for x in tr.events if x[1]["event_type"] != "GROUND_TRUTH_LOCKED"]
        d = scored(tr)["metrics"]["decisions"]
        self.assertEqual("UNKNOWN_COHORT", d["rows"][0]["outcome"])
        self.assertEqual([0.0, 1.0], d["M1"]["pooled_check"]["bounds"])

    def test_b0_decision_metrics_are_na(self):
        tr = Trace("B0")
        tr.run_started(), tr.ground_truth(), tr.trial_started(), tr.sync(10), tr.sync(300)
        tr.probe_run([(20, 100, True), (101, 140, False), (141, 260, True)])
        tr.attack(), tr.effect(), tr.stop(), tr.trial_ended()
        m = scored(tr)["metrics"]
        self.assertEqual("N/A", m["decisions"]["M1"]["status"])
        self.assertEqual("N/A", m["kpi"]["mttd"]["status"])
        self.assertEqual(1, m["kpi"]["recovered_rate"]["numerator"])


class Aggregates(unittest.TestCase):
    def test_d01_verdicts_and_r_of_t(self):
        f01 = e01().f01
        r = scored(e01())["incidents"][0]
        k = kpi([r], f01)
        self.assertEqual("PASS", k["mttd"]["verdict"])
        self.assertEqual("PASS", k["mttr_120"]["verdict"])
        self.assertEqual({"lower": 1.0, "upper": 1.0}, k["r_t"]["points"]["120"])
        timeout = dict(r, label="TIMEOUT", mttr=None, total=None)
        missing = dict(r, label="MISSING_PROBE", mttr=None, total=None)
        k = kpi([r, timeout], f01)
        self.assertEqual("NOT_PASS", k["mttr_120"]["verdict"])
        self.assertEqual([0.5, 0.5], k["mttr_120"]["bounds"])
        k = kpi([r, missing], f01)
        self.assertEqual("UNKNOWN", k["mttr_120"]["verdict"])
        self.assertEqual([0.5, 1.0], k["mttr_120"]["bounds"])
        self.assertEqual({"lower": 0.5, "upper": 1.0}, k["r_t"]["points"]["600"])
        self.assertEqual("<= cap_rec (needs the curve for a point value)", k["r_t"]["median"])
        self.assertEqual({"numerator": 1, "N": 2, "rate": 0.5, "labels": ["TIMEOUT"]}, kpi([r, timeout], f01)["failure_rate"])
        self.assertEqual([90.0], kpi([r, timeout], f01)["recovered_distribution"]["total_s"])
        exact = dict(r, mttd=60.0)
        self.assertEqual("FAIL", kpi([exact], f01)["mttd"]["verdict"])  # strict '<'
        self.assertEqual(0, kpi([exact], f01)["mttd"]["passed"])


def c0_trace(group="B1", alerts=(), coverage=True):
    tr = Trace(group)
    tr.run_started()
    tr.trial_started()
    tr.sync(10), tr.sync(300)
    tr.probe_run([(20, 260, True)])
    for at, service in alerts:
        tr.detected(at, service=service, incident=False)
    return tr


def benign_row(tr, coverage=True, log=True):
    tr.trial_ended()
    cfg = {"trial_ids": [tr.trial], "slot_s": 60, "episode_gap_s": 90, "action_log_complete": log}
    if coverage:
        cfg["detector_coverage"] = {tr.trial: [[iso(22), iso(300)]]}
    return scored(tr, {"benign": cfg})["metrics"]["M5_M6_benign"]["trials"][tr.trial]


class Fix01Benign(unittest.TestCase):
    """ZR10-03/04 and the B0 note: M5 keys and stream coverage, M6 from HEAL_STARTED (ZER-8 5.5)."""

    def test_episodes_are_keyed_by_signature_and_service(self):
        m = benign_row(c0_trace(alerts=[(50, "frontend"), (51, "cartservice")]))
        self.assertEqual((2, 25.899281, "OK"), (m["episodes_observed"], m["episodes_per_hour"], m["verdict"]))
        m = benign_row(c0_trace(alerts=[(50, "frontend"), (120, "frontend")]))  # same key within g_b: one episode
        self.assertEqual(1, m["episodes_observed"])
        m = benign_row(c0_trace(alerts=[(30, "frontend"), (200, "frontend")]))  # same key, gap > g_b: two
        self.assertEqual(2, m["episodes_observed"])

    def test_all_slots_hit_does_not_prove_the_stream(self):
        m = benign_row(c0_trace(alerts=[(t, "frontend") for t in (22, 82, 142, 202, 262)]), coverage=False)
        self.assertEqual((5, 0, [1.0, 1.0], "OK"), (m["hit"], m["unknown"], m["bounds"], m["slot_verdict"]))
        self.assertEqual((None, "UNKNOWN", "UNKNOWN"), (m["episodes_per_hour"], m["episode_verdict"], m["verdict"]))

    def test_unplaceable_alert_leaves_slots_unknown(self):
        tr = c0_trace(alerts=[(50, "frontend")])
        side = tr.detected(170, incident=False)
        side["clock"] = {"clock_id": "clk_side_ext", "clock_source": "OFF_HOST", "resolution_ms": 16}
        m = benign_row(tr)
        self.assertEqual((1, 4, 1, None), (m["hit"], m["unknown"], m["alerts_unplaced"], m["episodes_per_hour"]))

    def test_m6_counts_started_actions_in_w(self):
        tr = c0_trace(alerts=[(50, "frontend")])
        alert = next(e for _, e in tr.events if e["event_type"] == "DETECTED")
        tr.action(tr.decision(51, alert, incident=False), started=52, api=53, done=None)  # no terminal
        tr.action(tr.decision(280, alert, incident=False), started=290, api=295, done=310)  # ends after W
        tr.action(tr.decision(15, alert, incident=False), started=16, api=18, done=30)  # starts before W
        m = benign_row(tr)
        self.assertEqual((2, 1, 1), (m["M6_actions_executed"], m["M6_terminal"]["MISSING"], m["M6_terminal"]["SUCCESS"]))
        self.assertEqual(("MISSING", "UNKNOWN", "OK"), (m["M6_terminal_status"], m["M6_harm"]["status"], m["M6_verdict"]))
        self.assertEqual("UNKNOWN", benign_row(c0_trace(), log=False)["M6_verdict"])

    def test_b0_detector_off_is_na_not_zero(self):
        m = benign_row(c0_trace("B0"))
        self.assertEqual(("N/A", "N/A"), (m["M5"]["status"], m["M6"]["status"]))
        m = benign_row(c0_trace("B0", alerts=[(50, "frontend")]))  # B0 with an observing detector: M5 is measured
        self.assertEqual((1, "N/A"), (m["hit"], m["M6"]["status"]))


class Fix01Usage(unittest.TestCase):
    """ZR10-05: call/usage/cost coverage starts from the LLM decisions; unusable records keep it MISSING."""

    def test_llm_decision_without_call_record(self):
        tr = e01()
        tr.events = [x for x in tr.events if x[1]["event_type"] != "LLM_CALL"]
        u = scored(tr)["metrics"]["M11_usage"]
        self.assertEqual(("MISSING", "MISSING", "MISSING", "MISSING", 0), (u["status"], u["call_coverage_status"],
                         u["usage_status"], u["cost_status"], u["calls"]))
        self.assertEqual(1, len(u["decisions_without_call"]))
        self.assertEqual("MISSING", next(iter(u["by"]["incident"].values()))["usage_status"])

    def test_invalid_second_call_keeps_lower_bounds(self):
        tr = e01()
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        bad = tr.llm_call(133.1, dec, attempt=2, retry_reason="SCHEMA")
        bad["payload"]["usage"]["input_tokens"] = -1
        u = scored(tr)["metrics"]["M11_usage"]
        run = next(iter(u["by"]["run"].values()))
        self.assertEqual((1, 2, True), (u["calls"], u["raw_call_records"], u["calls_lower_bound"]))
        self.assertEqual(("MISSING", "MISSING", "MISSING"), (u["call_coverage_status"], run["usage_status"], run["cost_status"]))
        self.assertEqual((0.01, 1), (run["usd"], run["invalid_call_records"]))

    def test_complete_control(self):
        u = scored(e01())["metrics"]["M11_usage"]
        self.assertEqual(("OK", "COMPLETE", "COMPLETE", 1), (u["status"], u["call_coverage_status"], u["usage_status"], u["calls"]))


class Fix01GroundTruthAndOrder(unittest.TestCase):
    """ZR10-06/07 and M4: malformed ground truth is UNKNOWN_GT; nothing is decided by ingest order."""

    def gt(self, tr):
        return next(e for _, e in tr.events if e["event_type"] == "GROUND_TRUTH_LOCKED")["payload"]

    def test_malformed_ground_truth_is_unknown_not_a_crash(self):
        cases = [(lambda g: g["constraints"]["SCALE_UP"].update(max_replicas="four"), "UNKNOWN_GT"),
                 (lambda g: g["constraints"]["SCALE_UP"].update(max_replicas=True), "UNKNOWN_GT"),
                 (lambda g: g.update(constraints=["SCALE_UP"]), "UNKNOWN_GT"),
                 (lambda g: g.update(acceptable_actions="SCALE_UP"), "UNKNOWN_GT"),
                 (lambda g: g.update(decision_required="yes"), "UNKNOWN_COHORT"),
                 (lambda g: g.update(case_class=["C4"]), "CORRECT")]
        for change, outcome in cases:
            tr = e01()
            change(self.gt(tr))
            d = scored(tr)["metrics"]["decisions"]
            self.assertEqual(outcome, d["rows"][0]["outcome"], d["rows"][0])
            if outcome == "UNKNOWN_GT":
                self.assertTrue(d["rows"][0]["reason"])
        tr = e01()
        self.gt(tr)["constraints"] = {"BLOCK_IP": {"ttl_s_min": 600, "ttl_s_max": 60}}
        self.gt(tr)["acceptable_actions"] = ["BLOCK_IP"]
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        dec["payload"]["proposal"] = {"action_type": "BLOCK_IP", "params": {"sources": ["10.0.0.9"], "ttl_s": 300}}
        next(e for _, e in tr.events if e["event_type"] == "ATTACK_REQUESTED")["payload"]["s_att"] = ["10.0.0.9"]
        self.assertEqual("UNKNOWN_GT", scored(tr)["metrics"]["decisions"]["rows"][0]["outcome"])
        self.assertEqual("CORRECT", scored(e01())["metrics"]["decisions"]["rows"][0]["outcome"])

    def test_conflicting_guard_verdicts_do_not_depend_on_order(self):
        results = []
        for verdicts in (("ACCEPT", "REJECT"), ("REJECT", "ACCEPT"), ("ACCEPT", "ACCEPT")):
            tr = e01()
            first = next(e for _, e in tr.events if e["event_type"] == "GUARD_VERDICT")
            first["payload"]["verdict"] = verdicts[0]
            tr.guard(133.2, next(e for _, e in tr.events if e["event_type"] == "DECISION"), verdict=verdicts[1])
            res = scored(tr)
            results.append(res["metrics"]["decisions"]["M3"])
            self.assertEqual(1, len(res["findings"]["cardinality_violations"]))
        for m3 in results:
            self.assertEqual((1, 0, 0, 0.0), (m3["conflicting_verdicts"], m3["accept_correct"], m3["false_block"], m3["coverage_scorable"]))
        self.assertEqual(1, scored(e01())["metrics"]["decisions"]["M3"]["accept_correct"])

    def test_tied_first_proposals_and_m4_trigger(self):
        tr = e01()
        alert = next(e for _, e in tr.events if e["event_type"] == "DETECTED")
        tr.decision(133, alert, received=131.4, action="ROLLBACK")  # a second proposal at the same instant
        self.assertEqual("MISSING_ORDER", scored(tr)["metrics"]["decisions"]["rows"][0]["outcome"])
        tr = e01(detect=None)
        tr.events = [x for x in tr.events if x[1]["event_type"] != "GROUND_TRUTH_LOCKED"]
        d = scored(tr)["metrics"]["decisions"]
        self.assertEqual(("UNKNOWN_COHORT", 0), (d["rows"][0]["outcome"], d["M4"]["N"]))  # no trigger, not in M4


class Fix02Usage(unittest.TestCase):
    """FX01-N1: a call_id with conflicting records leaves every group it names without COMPLETE coverage."""

    def conflicting(self, model=None):
        tr = e01()
        dec = next(e for _, e in tr.events if e["event_type"] == "DECISION")
        old = next(e for _, e in tr.events if e["event_type"] == "LLM_CALL")
        new = tr.llm_call(134, dec, attempt=2, retry_reason="SCHEMA", call_id=old["call_id"])
        if model:
            new["payload"]["model"] = model
        return scored(tr)["metrics"]["M11_usage"]

    def test_conflict_reaches_every_bucket(self):
        u = self.conflicting()
        self.assertEqual(("MISSING", 1, True), (u["call_coverage_status"], u["calls"], u["calls_lower_bound"]))
        for level, groups in u["by"].items():
            for key, g in groups.items():
                self.assertEqual(("MISSING", "MISSING", "MISSING"), (g["call_coverage_status"], g["usage_status"], g["cost_status"]),
                                 f"{level}/{key}")
                self.assertGreater(g["conflicting_call_records"], 0)

    def test_conflicting_record_naming_another_model_marks_it_too(self):
        u = self.conflicting(model="model-y")
        self.assertEqual({"model-x", "model-y"}, set(u["by"]["model"]))
        self.assertEqual((1, 0), (u["by"]["model"]["model-x"]["calls"], u["by"]["model"]["model-y"]["calls"]))
        self.assertEqual("MISSING", u["by"]["model"]["model-y"]["call_coverage_status"])

    def test_control_without_conflict(self):
        u = scored(e01())["metrics"]["M11_usage"]
        for level, groups in u["by"].items():
            for key, g in groups.items():
                self.assertEqual(("COMPLETE", 0), (g["call_coverage_status"], g["conflicting_call_records"]), f"{level}/{key}")


if __name__ == "__main__":
    unittest.main()
