"""Scorer end to end on sealed ZER-9 exports: milestones, labels, clocks, linking, invalid data.

Traces are SYNTHETIC (tests/fixtures/zer10/builder.py); expected values are hand-computed in
tests/fixtures/zer10/expected.json. Offline: temporary archives only, no network.
"""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))
from builder import PROBE, Trace, e01  # noqa: E402
from event_pipeline.contract import new_id  # noqa: E402
from measurement.metrics import kpi, run_metrics  # noqa: E402
from measurement.raw import RawError, load  # noqa: E402
from measurement.scorer import Scorer  # noqa: E402

EXPECTED = json.loads((ROOT / "tests/fixtures/zer10/expected.json").read_text())


def score(trace, options=None, order=None, after_seal=()):
    with tempfile.TemporaryDirectory() as tmp:
        h, o, rejected = trace.seal(tmp, order=order, after_seal=after_seal)
        scorer = Scorer(*load(h, o), options or {})
        result = scorer.run()
        result["metrics"] = run_metrics(scorer, result, options or {})
        result["_rejected"] = rejected
        result["_scorer"] = scorer
        return result


def one(result):
    assert len(result["incidents"]) == 1, result["incidents"]
    return result["incidents"][0]


def custom(pattern, end=300, group="B2", detect=131, action=("SUCCESS", 150), stop=240, effect=True, rv=None,
           syncs=((10, None, 20),), decision_kind="ACTION"):
    tr = Trace(group)
    tr.run_started()
    tr.ground_truth()
    tr.trial_started(end=end)
    tr.manifest()
    for t, off, unc in syncs:
        tr.sync(t, off, unc)
    tr.sync(end, None, 20)
    tr.probe_run(pattern)
    tr.attack()
    if detect is not None:
        alert = tr.detected(detect)
        dec = tr.decision(133, alert, received=detect + 0.4, kind=decision_kind)
        if action:
            tr.action(dec, started=133.5, api=134, done=action[1], status=action[0])
    if effect:
        tr.effect()
    if rv:
        tr.recovery_verified(*rv)
    if stop is not None:
        tr.stop(stop)
    tr.trial_ended(end)
    return tr


class Milestones(unittest.TestCase):
    def check(self, r, expected, keys=("label", "mttd", "mttr", "total", "reaction")):
        for key in keys:
            if key in expected:
                self.assertEqual(expected[key], r[key], f"{key}: {r}")

    def test_e01_hand_values_and_uncertainty(self):
        r = one(score(e01()))
        self.check(r, EXPECTED["E01"])
        self.assertEqual(EXPECTED["E01"]["uncertainty_ms"], r["uncertainty_ms"])
        self.assertEqual([], r["flags"])
        self.assertFalse(r["evaluator_mismatch"], r["evaluator_issues"])

    def test_ingest_order_and_late_receipt_do_not_move_milestones(self):
        tr = e01()
        late_first = list(reversed(tr.events))
        r = one(score(tr, order=late_first))
        self.check(r, EXPECTED["E01"])
        # RECOVERY_VERIFIED arriving after seal is LATE_INGEST: excluded, counted; KPI recomputed from samples.
        tr = e01(rv=False)
        rv = tr.recovery_verified(222, 191, 189, 221)
        tr.events.remove(("H", rv))
        res = score(tr, after_seal=[("H", rv)])
        r = one(res)
        self.check(r, EXPECTED["E01"])
        self.assertEqual(1, res["findings"]["late_ingest"])
        self.assertIn("RECOVERY_VERIFIED_ABSENT", r["evaluator_issues"])

    def test_action_success_is_not_recovery_e02(self):
        tr = custom([(20, 100, True), (101, 760, False)], end=800, stop=760)
        r = one(score(tr))
        self.check(r, EXPECTED["E02"])

    def test_failed_partial_timeout_or_no_action_can_still_recover_without_credit(self):
        pattern = [(20, 100, True), (101, 140, False), (141, 260, True)]
        for status in ("FAILED", "PARTIAL", "TIMEOUT"):
            r = one(score(custom(pattern, action=(status, 138))))
            self.check(r, EXPECTED["E03"])
            self.assertIn("NO_ACTION_BEFORE_RECOVERY", r["flags"])
        r = one(score(custom(pattern, action=None, decision_kind="NO_ACTION")))
        self.check(r, EXPECTED["E03"])
        # Terminal missing (HEAL_STARTED + API_ACCEPTED only).
        tr = custom(pattern, action=None)
        dec = [e for _, e in tr.events if e["event_type"] == "DECISION"][0]
        tr.action(dec, done=None)
        r = one(score(tr))
        self.assertEqual("RECOVERED", r["label"])
        self.assertIn("ACTION_TERMINAL_MISSING", r["flags"])
        self.assertEqual("NO_SUCCESS", r["reaction"])

    def test_relapse_missing_probe_cap_and_stop(self):
        self.check(one(score(custom([(20, 100, True), (101, 140, False), (141, 150, True), (151, 160, False), (161, 260, True)]))), EXPECTED["E05"])
        self.check(one(score(custom([(20, 100, True), (101, 140, False), (141, 150, True)]))), EXPECTED["E06"])
        self.check(one(score(custom([(20, 100, True), (101, 698, False), (699, 800, True)], end=820, stop=800))), EXPECTED["E07"])
        self.check(one(score(custom([(20, 100, True), (101, 699, False), (700, 800, True)], end=820, stop=800))), EXPECTED["E08"])
        self.check(one(score(custom([(20, 100, True), (101, 140, False), (141, 260, True)], stop=160))), EXPECTED["E09"])

    def test_early_detect_and_invalid_clock(self):
        tr = e01(detect=100.5)
        r = one(score(tr))
        self.check(r, EXPECTED["E20"])
        self.assertIn("EARLY_DETECT", r["flags"])
        tr = Trace()
        tr.run_started(), tr.ground_truth(), tr.trial_started(), tr.sync(10), tr.sync(300)
        tr.probe_run([(20, 100, True), (101, 188, False), (189, 260, True)])
        tr.attack()
        alert = tr.detected(131)
        tr.decision(133, alert, received=128)  # T_con before T_pub 131.2 - eps
        tr.effect(), tr.stop(), tr.trial_ended()
        r = one(score(tr))
        self.assertEqual("MISSING", r["label"])
        self.assertIn("INVALID_CLOCK", r["missing_reasons"])
        self.assertEqual("MISSING", r["mttd"])

    def test_redelivery_vs_retry_and_out_of_order(self):
        tr = Trace()
        tr.run_started(), tr.ground_truth(), tr.trial_started(), tr.sync(10), tr.sync(300)
        tr.probe_run([(20, 100, True), (101, 188, False), (189, 260, True)])
        tr.attack()
        alert = tr.detected(131)
        dec = tr.decision(133, alert, received=131.4)
        first = tr.action(dec, started=133.5, api=134, done=140, status="FAILED")
        tr.action(dec, started=141, api=142, done=155, status="SUCCESS", attempt=2, retry_of=first["action_id"])
        tr.effect(), tr.stop(), tr.trial_ended()
        tr.events.append(("O", copy.deepcopy(alert)))  # Kafka redelivery: same event_id and bytes
        res = score(tr)
        r = one(res)
        self.check(r, EXPECTED["E13"], keys=("reaction", "label"))
        self.assertEqual(2, r["action_attempts"])
        self.assertEqual(1, res["findings"]["duplicates"])
        tr = e01()
        second = tr.detected(140)
        order = [x for x in tr.events if x[1] is not second]
        early = next(x for x in order if x[1]["event_type"] == "DETECTED")
        order.remove(early)
        order.insert(0, ("O", second))
        order.append(early)
        self.assertEqual(EXPECTED["E14"]["mttd"], one(score(tr, order=order))["mttd"])


class Clocks(unittest.TestCase):
    def test_unverified_probe_clock_keeps_same_clock_durations(self):
        r = one(score(e01(syncs=())))
        for key in ("label", "mttd", "mttr", "total", "reaction"):
            self.assertEqual(EXPECTED["E18"][key], r[key], key)
        self.assertIn("CLOCK_UNVERIFIED", r["flags"])

    def test_offset_and_drift_are_normalized(self):
        r = one(score(e01(offset=lambda t: 10000.0)))
        for key in ("mttd", "mttr", "total"):
            self.assertEqual(EXPECTED["C1"][key], r[key], r)
        r = one(score(e01(offset=lambda t: (t - 10) * 10.0)))
        for key in ("mttd", "mttr", "total"):
            self.assertEqual(EXPECTED["C3"][key], r[key], r)
        self.assertFalse(r["evaluator_mismatch"], r["evaluator_issues"])

    def test_sync_must_cover_trial_end_and_carry_uncertainty(self):
        r = one(score(e01(syncs=((10, None, 20), (101, None, 20)))))
        self.assertEqual(EXPECTED["C2"]["label"], r["label"])
        self.assertEqual(EXPECTED["C2"]["total"], r["total"])
        r = one(score(e01(syncs=((10, None, None), (300, None, None)))))
        self.assertEqual("MISSING", r["label"])
        clock = dict(PROBE, resolution_ms=None)
        r = one(score(e01(probe_clock=clock)))
        self.assertEqual("MISSING", r["label"])
        self.assertEqual(90.0, r["total"])

    def test_host_shared_probe_needs_no_sync(self):
        clock = {"clock_id": "clk_host_lab", "clock_source": "HOST_SHARED", "resolution_ms": 1}
        r = one(score(e01(syncs=(), probe_clock=clock)))
        self.assertEqual("RECOVERED", r["label"])
        self.assertEqual({"mttd": 2, "mttr": 2, "total": 2, "reaction": 2}, r["uncertainty_ms"])


class Evidence(unittest.TestCase):
    def test_effect_states_and_denominators(self):
        no_eff = custom([(20, 400, True)], end=420, detect=None, effect=False, stop=None)
        no_eff.effect(t=410, status="CONFIRMED_NO_EFFECT", t_eff=None)
        gap = custom([(20, 200, True)], end=420, detect=None, effect=False, stop=None)
        gap.effect(t=410, status="CONFIRMED_NO_EFFECT", t_eff=None)
        unknown = custom([(20, 100, True), (101, 188, False), (189, 260, True)], effect=False)
        r11, r12, r10 = one(score(no_eff)), one(score(gap)), one(score(unknown))
        self.assertEqual(EXPECTED["E11"]["label"], r11["label"])
        self.assertEqual(EXPECTED["E12"]["label"], r12["label"])
        for key in ("label", "mttd", "mttr", "reaction"):
            self.assertEqual(EXPECTED["E10"][key], r10[key])
        f01 = no_eff.f01
        a1 = kpi([r10, r11], f01)["counts"]
        for key, value in EXPECTED["A1"].items():
            self.assertEqual(value, a1[key], key)
        self.assertEqual("EMPTY", kpi([], f01)["mttd"]["verdict"])
        self.assertEqual("NO_ELIGIBLE", kpi([r11], f01)["mttd"]["verdict"])
        both = kpi([r10, copy.deepcopy(r10)], f01)
        self.assertEqual(EXPECTED["ALL_UNKNOWN"]["N"], both["counts"]["N"])
        self.assertEqual(EXPECTED["ALL_UNKNOWN"]["mttd_verdict"], both["mttd"]["verdict"])
        self.assertEqual(EXPECTED["ALL_UNKNOWN"]["mttd_bounds"], both["mttd"]["bounds"])

    def test_invalid_and_conflicting_evidence_is_missing_not_missed(self):
        # V2: a passing sample above L is SEMANTIC, so the incident is MISSING, never RECOVERED.
        tr = e01()
        tr.sample(150.5, True, 9999, latency_ms=5000)
        r = one(score(tr))
        self.assertEqual("MISSING", r["label"])
        self.assertIn("INVALID_EVENT", r["missing_reasons"])
        # V1: SUCCESS without satisfied postcondition is quarantined by the archive.
        tr = custom([(20, 100, True), (101, 188, False), (189, 260, True)], action=None)
        dec = [e for _, e in tr.events if e["event_type"] == "DECISION"][0]
        hs = tr.action(dec, done=None)
        bad = tr.env("ACTION_COMPLETED", "O", "executor", 150, {"status": "SUCCESS", "postcondition": {"name": "x", "checked": True, "satisfied": False, "observed": "x"}, "error": None},
                     action_id=hs["action_id"], decision_id=dec["decision_id"])
        res = score(tr)
        r = one(res)
        self.assertIn(("ACTION_COMPLETED", "SEMANTIC"), res["_rejected"])
        self.assertEqual("MISSING", r["label"])
        self.assertIn("ACTION_TERMINAL_MISSING", r["flags"])
        self.assertEqual("MISSING", r["reaction"])
        del bad
        # V3 / E16: DETECTED with a null payload or without trial is quarantined; never MISSED.
        for mutate in (lambda e: e.update(payload=None), lambda e: e.update(trial_id=None, incident_id=None)):
            tr = e01()
            alert = next(e for _, e in tr.events if e["event_type"] == "DETECTED")
            mutate(alert)
            r = one(score(tr))
            self.assertEqual("MISSING", r["label"], r)
        # R5: two samples with one key; E15: one event_id with two bodies.
        tr = e01()
        tr.sample(190, False, 170)
        self.assertIn("INTEGRITY_ERROR", one(score(tr))["missing_reasons"])
        tr = e01()
        done = next(e for _, e in tr.events if e["event_type"] == "ACTION_COMPLETED")
        twin = copy.deepcopy(done)
        twin["payload"].update(status="FAILED", postcondition={"name": "x", "checked": True, "satisfied": False, "observed": "x"}, error="x")
        tr.events.append(("O", twin))
        res = score(tr)
        self.assertIn(("ACTION_COMPLETED", "INTEGRITY_ERROR"), res["_rejected"])
        self.assertEqual("MISSING", one(res)["label"])

    def test_source_violation_is_stored_not_used(self):
        tr = custom([(20, 100, True), (101, 760, False)], end=800, stop=760)
        tr.env("DETECTED", "O", "executor", 125, {"rule_id": "x", "rule_version": "r", "signature": "s", "metric": "m", "value": 1,
                                                  "threshold": 0, "severity": "W", "description": "d"},
               target={"namespace": "target-app", "service": "frontend", "flow": None}, alert_id=new_id("alt"))
        tr.env("RECOVERY_VERIFIED", "H", "executor", 160, {"flow": "checkout"})
        res = score(tr)
        r = one(res)
        self.assertEqual("TIMEOUT", r["label"])
        self.assertEqual(30.0, r["mttd"])
        self.assertEqual(2, sum(1 for _, c in res["_rejected"] if c == "SOURCE_VIOLATION"))

    def test_evaluator_mismatch_is_reported_and_recomputed(self):
        cases = {"premature": dict(emit_at=221), "sample_seq_range": dict(sample_seq_range=[150, 182]),
                 "provenance": dict(probe_id="prb-9"), "samples_sha256": dict(samples_sha256="sha256:" + "5" * 64)}
        for issue, override in cases.items():
            tr = e01(rv=False)
            emit = override.pop("emit_at", 222)
            tr.recovery_verified(222, 191, 189, 221, emit_at=emit, **override)
            r = one(score(tr))
            self.assertTrue(r["evaluator_mismatch"], issue)
            self.assertTrue(any(issue in x or (issue == "premature" and "published_before" in x) for x in r["evaluator_issues"]), (issue, r["evaluator_issues"]))
            self.assertEqual(60.0, r["mttr"])

    def test_linking_conflicts_target_mismatch_and_unscoped(self):
        tr = e01()
        alert = next(e for _, e in tr.events if e["event_type"] == "DETECTED")
        alert["trial_id"] = new_id("trl")  # explicit incident_id, wrong trial
        self.assertEqual("MISSING", one(score(tr))["label"])
        tr = e01(detect=None)
        tr.detected(131, service="cartservice")
        r = one(score(tr))
        self.assertEqual("MISSING", r["label"])
        self.assertIn("TARGET_MISMATCH", r["missing_reasons"])
        tr = e01()
        stray = tr.detected(125)
        stray.pop("run_id")
        res = score(tr)
        self.assertEqual(30.0, one(res)["mttd"])
        self.assertEqual(1, res["findings"]["archive_scope"])

    def test_window_rule_links_detect_without_ids_and_ambiguity_is_missing(self):
        tr = e01()
        alert = next(e for _, e in tr.events if e["event_type"] == "DETECTED")
        alert.pop("incident_id")
        for _, e in tr.events:
            if e["event_type"] in {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}:
                e.pop("incident_id", None)
        r = one(score(tr))
        self.assertEqual("RECOVERED", r["label"])
        self.assertEqual(19.0, r["reaction"])  # API/AC linked through the action_id map

    def war_game(self, second_req):
        tr = Trace()
        tr.run_started(), tr.ground_truth(), tr.trial_started(end=1320), tr.sync(10), tr.sync(1320)
        first, second = tr.incident, new_id("inc")
        tr.probe_run([(20, 100, True), (101, 140, False), (141, second_req, True), (second_req + 1, second_req + 40, False),
                      (second_req + 41, 1300, True)])
        tr.attack(100), tr.effect(160, t_eff=101), tr.stop(400)
        tr.incident = second
        tr.attack(second_req), tr.effect(second_req + 60, t_eff=second_req + 1), tr.stop(second_req + 300)
        tr.incident = first
        for t in (131, second_req + 31) if second_req >= 500 else (160,):
            tr.detected(t, incident=False)
        tr.trial_ended(1320)
        return tr, first, second

    def test_war_game_window_rule_and_overlap(self):
        tr, first, second = self.war_game(1000)
        res = score(tr)
        got = {r["incident_id"]: r for r in res["incidents"]}
        self.assertEqual((30.0, 30.0), (got[first]["mttd"], got[second]["mttd"]))
        # T_rec 143 / 1043; recovery_verified_at 173 <= stop 400 and 1073 <= stop 1300.
        self.assertEqual(("RECOVERED", "RECOVERED"), (got[first]["label"], got[second]["label"]))
        self.assertEqual((12.0, 12.0), (got[first]["mttr"], got[second]["mttr"]))
        tr, first, second = self.war_game(150)
        res = score(tr)
        self.assertEqual({"MISSING"}, {r["label"] for r in res["incidents"]})
        self.assertTrue(all("AMBIGUOUS" in r["missing_reasons"] for r in res["incidents"]))

    def test_orphan_with_unknown_incident_in_window_is_missing(self):
        tr = e01()
        tr.detected(140, incident=new_id("inc"))
        r = one(score(tr))
        self.assertEqual("MISSING", r["label"])
        self.assertIn("ORPHAN_IN_WINDOW", r["missing_reasons"])

    def test_event_of_another_run_naming_this_incident_is_link_conflict(self):
        from measurement.raw import Export
        first = e01()
        other = Trace()
        other.run_started()
        other.detected(131, incident=first.incident, trial=first.trial)
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = first.seal(Path(tmp) / "a")
            oh, oo, _ = other.seal(Path(tmp) / "b")
            alone = Scorer(*load(h, o)).run()
            self.assertIn("CROSS_RUN_LINKS_UNCHECKED", alone["run_flags"])
            self.assertEqual("RECOVERED", alone["incidents"][0]["label"])
            checked = Scorer(*load(h, o), others=[Export(oh, "H"), Export(oo, "O")]).run()
        r = checked["incidents"][0]
        self.assertEqual("MISSING", r["label"])
        self.assertIn("LINK_CONFLICT", r["missing_reasons"])
        self.assertNotIn("CROSS_RUN_LINKS_UNCHECKED", checked["run_flags"])

    def test_mode_rules(self):
        tr = custom([(20, 100, True), (101, 140, False), (141, 260, True)], group="B0", detect=None)
        r = one(score(tr))
        self.assertEqual("RECOVERED_UNDETECTED", r["label"])
        self.assertEqual("N/A", r["mttd"])
        self.assertEqual(42.0, r["total"])
        tr = custom([(20, 100, True), (101, 140, False), (141, 260, True)], group="B0", detect=None)
        alert = tr.detected(131)
        dec = tr.decision(133, alert, source="decision_rules")
        tr.action(dec)
        res = score(tr)
        self.assertEqual("MISSING", one(res)["label"])
        self.assertIn("MODE_VIOLATION", one(res)["missing_reasons"])

    def test_params_missing_never_default(self):
        tr = e01()
        run = next(e for _, e in tr.events if e["event_type"] == "RUN_STARTED")
        run["payload"]["f01_params"] = {"k": 3}
        res = score(tr)
        self.assertEqual("MISSING", one(res)["label"])
        self.assertIn("PARAMS_INVALID", res["run_flags"])


class RawIntegrity(unittest.TestCase):
    def test_tampered_export_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(tmp)
            raw = h / "H.jsonl"
            raw.chmod(0o644)
            data = raw.read_bytes().replace(b'"pass":true', b'"pass":false', 1)
            raw.write_bytes(data)
            with self.assertRaises(RawError):
                load(h, o)
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(tmp)
            meta = json.loads((h / "export.json").read_bytes())
            shutil.rmtree(h / "archive-scope", ignore_errors=True)
            meta["plane"] = "O"
            (h / "export.json").chmod(0o644)
            (h / "export.json").write_text(json.dumps(meta))
            with self.assertRaises(RawError):
                load(h, o)

    def test_scoring_does_not_change_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(tmp)
            before = {p: p.read_bytes() for p in list(h.rglob("*")) + list(o.rglob("*")) if p.is_file()}
            Scorer(*load(h, o)).run()
            after = {p: p.read_bytes() for p in before}
            self.assertEqual(before, after)


def lost_request(tr, how):
    """Make the trace's ATTACK_REQUESTED unusable the way a harness bug would."""
    req = next(e for _, e in tr.events if e["event_type"] == "ATTACK_REQUESTED")
    if how == "missing_targets":
        del req["payload"]["target_services"]
    elif how == "no_incident":
        del req["incident_id"]
    return req


def two_trials(second_broken):
    """Contract E01 in two trials of one run; the second request is invalid when `second_broken`."""
    tr = e01(probe_clock=HOST_CLOCK)
    other = e01(probe_clock=HOST_CLOCK)
    for plane, event in other.events:
        if event["trial_id"] is None:
            continue
        event["run_id"], event["seq"] = tr.run, event["seq"] + 10000
        if second_broken and event["event_type"] == "ATTACK_REQUESTED":
            del event["payload"]["target_services"]
        tr.events.append((plane, event))
    return tr


HOST_CLOCK = {"clock_id": "clk_host_lab", "clock_source": "HOST_SHARED", "resolution_ms": 1}
UNSYNCED = {"clock_id": "clk_side_ext", "clock_source": "OFF_HOST", "resolution_ms": 16}


class Fix01Cohort(unittest.TestCase):
    """ZR10-01: a requested turn never leaves N because its request was rejected (contract 6.4, AC-03)."""

    def test_single_invalid_request_is_missing_not_empty(self):
        tr = e01(probe_clock=HOST_CLOCK)
        req = lost_request(tr, "missing_targets")
        res = score(tr)
        self.assertIn(("ATTACK_REQUESTED", "MISSING_FIELD"), res["_rejected"])  # the raw stays in H quarantine
        r = one(res)
        self.assertEqual((req["incident_id"], "MISSING"), (r["incident_id"], r["label"]))
        self.assertIn("REQUEST_INVALID", r["missing_reasons"])
        self.assertNotIn("TARGET_MISMATCH", r["missing_reasons"])  # unknown targets are not a mismatch
        counts = res["metrics"]["kpi"]["counts"]
        self.assertEqual((1, 1, "OK"), (counts["requested"], counts["N"], counts["status"]))
        for name in ("mttd", "mttr_120", "reaction"):
            self.assertEqual("UNKNOWN", res["metrics"]["kpi"][name]["verdict"], name)
        # No T_req and no targets are read from the invalid request: decisions on it are unknown, never CORRECT.
        self.assertEqual("MISSING_ORDER", res["metrics"]["decisions"]["rows"][0]["outcome"])
        self.assertEqual((0, 1), (res["metrics"]["decisions"]["M3"]["accept_correct"], res["metrics"]["decisions"]["M3"]["accept_unknown"]))

    def test_mixed_valid_and_invalid_trials_keep_both_turns(self):
        res = score(two_trials(second_broken=True))
        counts = res["metrics"]["kpi"]["counts"]
        self.assertEqual((2, 2), (counts["requested"], counts["N"]))
        self.assertEqual({"RECOVERED": 1, "MISSING": 1}, res["metrics"]["kpi"]["labels"])
        self.assertEqual("UNKNOWN", res["metrics"]["kpi"]["mttd"]["verdict"])
        self.assertEqual([0.5, 1.0], res["metrics"]["kpi"]["mttd"]["bounds"])
        control = score(two_trials(second_broken=False))
        self.assertEqual("PASS", control["metrics"]["kpi"]["mttd"]["verdict"])
        self.assertEqual(2, control["metrics"]["kpi"]["counts"]["N"])

    def test_late_request_stays_in_the_cohort(self):
        tr = e01(probe_clock=HOST_CLOCK)
        req = next(x for x in tr.events if x[1]["event_type"] == "ATTACK_REQUESTED")
        tr.events.remove(req)
        r = one(score(tr, after_seal=[req]))
        self.assertEqual(("MISSING", ["REQUEST_LATE"]), (r["label"], [m for m in r["missing_reasons"] if m.startswith("REQUEST")]))

    def test_unattributable_request_makes_the_cohort_incomplete(self):
        tr = e01(probe_clock=HOST_CLOCK)
        lost_request(tr, "no_incident")
        res = score(tr)
        self.assertEqual([], res["incidents"])
        self.assertFalse(res["cohort"]["complete"])
        self.assertIn("COHORT_INCOMPLETE", res["run_flags"])
        kpi_ = res["metrics"]["kpi"]
        self.assertEqual(("UNKNOWN", "COHORT_INCOMPLETE"), (kpi_["mttd"]["verdict"], kpi_["mttd"]["verdict_reason"]))

    def test_no_request_no_incident_and_foreign_source_is_not_a_request(self):
        tr = Trace("B1")
        tr.run_started(), tr.trial_started(), tr.sync(10), tr.sync(300), tr.trial_ended()
        res = score(tr)  # a C0 trial has TRIAL_STARTED/TRIAL_CONTEXT only: no fake attack incident
        self.assertEqual(([], True), (res["incidents"], res["cohort"]["complete"]))
        self.assertEqual("EMPTY", res["metrics"]["kpi"]["mttd"]["verdict"])
        tr = e01(probe_clock=HOST_CLOCK)
        forged = copy.deepcopy(next(e for _, e in tr.events if e["event_type"] == "ATTACK_REQUESTED"))
        forged.update(event_id=new_id("evt"), incident_id=new_id("inc"), source_component="detector", source_instance="det-0")
        tr.events.append(("H", forged))
        res = score(tr)
        self.assertIn(("ATTACK_REQUESTED", "SOURCE_VIOLATION"), res["_rejected"])
        self.assertEqual((1, "PASS"), (res["metrics"]["kpi"]["counts"]["requested"], res["metrics"]["kpi"]["mttd"]["verdict"]))


class Fix01Clocks(unittest.TestCase):
    """ZR10-02: evidence on an unverified clock is MISSING for what needs the order, never MISSED/NO_SUCCESS."""

    def move(self, tr, types, clock=UNSYNCED):
        for _, event in tr.events:
            if event["event_type"] in types:
                event["clock"] = dict(clock)
        return tr

    def test_unverified_detector_is_missing_not_missed(self):
        res = score(self.move(e01(probe_clock=HOST_CLOCK), {"DETECTED"}))
        r = one(res)
        self.assertEqual(("MISSING", "MISSING", "MISSING", "MISSING", 90.0),
                         (r["label"], r["mttd"], r["mttr"], r["reaction"], r["total"]))
        self.assertEqual("CLOCK_UNVERIFIED", r["t_det_status"])
        self.assertTrue({"CLOCK_UNVERIFIED", "DETECT_CLOCK_UNVERIFIED"} <= set(r["flags"]))
        m = res["metrics"]
        self.assertEqual(("UNKNOWN", [0.0, 1.0]), (m["kpi"]["mttd"]["verdict"], m["kpi"]["mttd"]["bounds"]))
        self.assertEqual("MISSING_ORDER", m["decisions"]["rows"][0]["outcome"])
        self.assertEqual((0, 1), (m["M2_funnel"]["triggered"], m["M2_funnel"]["trigger_unknown"]))
        self.assertEqual((0, 1), (m["decisions"]["M4"]["N"], m["decisions"]["M4"]["trigger_unknown"]))

    def test_unverified_executor_leaves_reaction_unknown(self):
        res = score(self.move(e01(probe_clock=HOST_CLOCK), {"HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}))
        r = one(res)
        self.assertEqual((30.0, "MISSING"), (r["mttd"], r["reaction"]))
        self.assertIn("ACTION_CLOCK_UNVERIFIED", r["flags"])
        self.assertEqual("UNKNOWN", res["metrics"]["kpi"]["reaction"]["verdict"])

    def test_unverified_decision_has_no_order_or_latency(self):
        res = score(self.move(e01(probe_clock=HOST_CLOCK), {"DECISION"}))
        self.assertEqual((30.0, 90.0), (one(res)["mttd"], one(res)["total"]))
        m = res["metrics"]["decisions"]
        self.assertEqual("MISSING_ORDER", m["rows"][0]["outcome"])
        self.assertEqual(0, m["M10"]["values"])

    def test_controls_and_negative_latency(self):
        r = one(score(e01(probe_clock=HOST_CLOCK)))
        self.assertEqual(("RECOVERED", 30.0, 60.0, 90.0, 19.0, "OBSERVED"),
                         (r["label"], r["mttd"], r["mttr"], r["total"], r["reaction"], r["t_det_status"]))
        r = one(score(e01(detect=None, probe_clock=HOST_CLOCK)))
        self.assertEqual(("RECOVERED_UNDETECTED", "MISSED", "NONE"), (r["label"], r["mttd"], r["t_det_status"]))
        tr = e01(probe_clock=HOST_CLOCK)
        for _, event in tr.events:
            if event["event_type"] == "PROBE_SAMPLE" and event["payload"]["pass"]:
                event["payload"]["latency_ms"] = -100
        self.assertEqual("MISSING", one(score(tr))["label"])  # a negative latency is invalid evidence


def without_trial_bounds(tr, trial=None):
    """Drop TRIAL_STARTED/TRIAL_ENDED (of one trial, or all): the trial's clock model cannot be built."""
    tr.events = [(p, e) for p, e in tr.events if e["event_type"] not in ("TRIAL_STARTED", "TRIAL_ENDED")
                 or (trial is not None and e["trial_id"] != trial)]
    return tr


class Fix02TrialMetadata(unittest.TestCase):
    """FX01-R3: milestones that cannot be built (no trial clock model) are MISSING with a reason, never a crash."""

    def test_missing_trial_bounds_are_missing_for_every_branch(self):
        for bad_request in (False, True):
            for stop in (240, None):
                for action in ("SUCCESS", None):
                    with self.subTest(bad_request=bad_request, stop=stop, action=action):
                        tr = without_trial_bounds(e01(stop=stop, action_status=action))
                        if bad_request:
                            lost_request(tr, "missing_targets")
                        res = score(tr, {"required_flows": ["checkout"]})
                        r = one(res)
                        self.assertEqual("MISSING", r["label"])
                        self.assertIn("TRIAL_MISSING", r["missing_reasons"])
                        self.assertEqual(bad_request, "REQUEST_INVALID" in r["missing_reasons"])
                        self.assertEqual(("MISSING", "MISSING", "MISSING"), (r["mttd"], r["mttr"], r["reaction"]))
                        self.assertEqual("CLOCK_UNVERIFIED" if stop else "NONE", r["t_stop_status"])
                        counts = res["metrics"]["kpi"]["counts"]
                        self.assertEqual((1, 1), (counts["requested"], counts["N"]))
                        self.assertEqual("UNKNOWN", res["metrics"]["kpi"]["mttd"]["verdict"])
                        # The trial is still reported, as unknown, instead of vanishing from uptime.
                        self.assertEqual("TRIAL_BOUNDS_MISSING",
                                         res["metrics"]["uptime"][tr.trial]["reason"])

    def test_invalid_or_duplicate_trial_start(self):
        tr = e01(probe_clock=HOST_CLOCK)
        start = next(e for _, e in tr.events if e["event_type"] == "TRIAL_STARTED")
        del start["payload"]["planned_window"]  # quarantined as MISSING_FIELD
        res = score(tr)
        self.assertIn(("TRIAL_STARTED", "MISSING_FIELD"), res["_rejected"])
        self.assertEqual(("MISSING", True), (one(res)["label"], "TRIAL_MISSING" in one(res)["missing_reasons"]))
        tr = e01(probe_clock=HOST_CLOCK)
        start = next(e for _, e in tr.events if e["event_type"] == "TRIAL_STARTED")
        tr.events.append(("H", dict(copy.deepcopy(start), event_id=new_id("evt"), seq=start["seq"] + 500)))
        r = one(score(tr))
        self.assertEqual(("MISSING", True), (r["label"], "TRIAL_MISSING" in r["missing_reasons"]))

    def test_other_trials_keep_their_result(self):
        tr = two_trials(second_broken=False)
        other = next(e["trial_id"] for _, e in tr.events if e["event_type"] == "TRIAL_STARTED" and e["trial_id"] != tr.trial)
        res = score(without_trial_bounds(tr, other))
        by_trial = {r["trial_id"]: r for r in res["incidents"]}
        self.assertEqual(("RECOVERED", 30.0, 60.0, 90.0, 19.0),
                         tuple(by_trial[tr.trial][k] for k in ("label", "mttd", "mttr", "total", "reaction")))
        self.assertEqual(("MISSING", ["TRIAL_MISSING"]), (by_trial[other]["label"], by_trial[other]["missing_reasons"]))
        self.assertEqual((2, 2), (res["metrics"]["kpi"]["counts"]["requested"], res["metrics"]["kpi"]["counts"]["N"]))

    def test_control_e01(self):
        r = one(score(e01(probe_clock=HOST_CLOCK)))
        self.assertEqual(("RECOVERED", "OBSERVED", []), (r["label"], r["t_stop_status"], r["missing_reasons"]))


if __name__ == "__main__":
    unittest.main()
