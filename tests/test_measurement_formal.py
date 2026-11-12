"""Locked ZER-53 scoring with sealed synthetic exports and no network."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from test_measurement_cli import no_network, run
from builder import HOST, Trace, iso
from event_pipeline.contract import new_id
from event_pipeline.formal_capture import prepare_decision
from measurement.formal import AUDIT_SURFACES, F01, METHOD, NOT_EVALUABLE, PROTOCOL_SHA256
from measurement.raw import load


RESOLVER_PIN = "1" * 64


class FormalScore(unittest.TestCase):
    def fixture(self, directory, *, response="ACTION", change=None, gap=False, failure=False,
                decision=True, detector=True, audit="CLEAN", group="B2", stage="PROPOSAL",
                terminal=False, receipt_change=None, containment_event=False, c0_effect=None):
        trace = Trace(group, f01=F01)
        trace.run_started()
        trace.events[0][1]["payload"]["protocol_ref"] = "sha256:" + PROTOCOL_SHA256
        trace.ground_truth(case_class="C5", acceptable=("BLOCK_IP",))
        trace.trial_started(end=450)
        trace.manifest()
        trace.sync(10)
        trace.sync(450)
        trace.attack(s_att=["192.0.2.1"])
        trace.effect(w_eff=30)
        trace.stop(102)
        trace.trial_ended(450)
        for t in range(100, 430, 5):
            if not gap or t != 105:
                trace.sample(t, not failure or t != 110, (t - 100) // 5, 250, 0.25, "prb-0", "p0", "checkout")
        if containment_event:
            trace.env("CONTAINMENT_VERIFIED", "H", "recovery_evaluator", 140, {
                "blocked_source_ref": "unjoined-block", "enforcement_point": "reported-policy",
                "fixture_probe_ref": "unjoined-fixture", "boutique_probe_ref": "unjoined-boutique",
                "t_contained": iso(140)})
        first = None
        fields = {"source": "192.0.2.1", "fixture_uid": "synthetic-fixture", "ttl_s": 180}
        prompt = {"source_component": "decision_llm", "field": "prompt", "text": "Synthetic observation"}
        prompt["sha256"] = hashlib.sha256(prompt["text"].encode()).hexdigest()
        if detector:
            alert = trace.detected()
            if decision:
                first = trace.decision(133, alert, received=131.4, kind=response, action="BLOCK_IP",
                                       params={"service": "fixture", "ttl_sec": 180}, stage=stage)
        for _, event in trace.events:
            event["method_version"] = METHOD
        if first:
            if group == "B2":
                first["payload"]["prompt_sha256"] = prompt["sha256"]
            resolution = dict(fields, status="RESOLVED") if response == "ACTION" else None
            recorded = prepare_decision(first, terminal_abstain=terminal, resolution=resolution,
                                        resolver_sha256=RESOLVER_PIN)
            self.assertNotIn("pre_guard", first["payload"])
            if receipt_change:
                recorded["payload"]["pre_guard"].update(receipt_change)
            trace.events[-1] = ("O", recorded)
        c5_trial = trace.trial
        if c0_effect is not None:
            start = len(trace.events)
            trace.trial, trace.incident = new_id("trl"), new_id("inc")
            trace.ground_truth(variant="var-control", case_class="C0", acceptable=(), required=False)
            trace.trial_started(t=460, warmup=520, end=910)
            trace.attack(t=550, variant="var-control")
            trace.effect(t=610, status=c0_effect, t_eff=551 if c0_effect == "CONFIRMED" else None, w_eff=30)
            trace.trial_ended(910)
            for _, event in trace.events[start:]:
                event["method_version"] = METHOD
        h, o, rejected = trace.seal(directory)
        self.assertEqual([], rejected)
        exports = load(h, o)
        entry = {"case": "C5", "decision_coverage": True, "continuous_flow": "checkout", "expected": fields}
        if audit == "CLEAN":
            originals = directory.parent / "audit-originals"
            originals.mkdir()
            review = {
                "run_id": trace.run, "trial_id": c5_trial, "evaluator": "synthetic evaluator",
                "from": iso(10), "to": iso(450), "clock_id": HOST["clock_id"],
                "surface_evidence_sha256": {},
            }
            for surface in AUDIT_SURFACES:
                entries = [prompt] if surface == "prompts" and first and group == "B2" else []
                self.write_audit(originals, review, surface, entries)
            entry["audit_review"] = review
        if change:
            change(entry)
        evidence = {"method_version": METHOD, "protocol_sha256": PROTOCOL_SHA256, "resolver_sha256": RESOLVER_PIN,
                    "h_export_json_sha256": exports[0].meta_sha256,
                    "o_export_json_sha256": exports[1].meta_sha256, "trials": {c5_trial: entry}}
        if c0_effect is not None:
            evidence["trials"][trace.trial] = {"case": "C0", "decision_coverage": False, "continuous_flow": "checkout"}
        return h, o, evidence

    @staticmethod
    def write_audit(directory, review, surface, material, **changes):
        record = {key: review[key] for key in ("run_id", "trial_id", "clock_id", "from", "to")}
        record.update(surface=surface, entries=material)
        record.update(changes)
        raw = json.dumps(record).encode()
        digest = hashlib.sha256(raw).hexdigest()
        (directory / digest).write_bytes(raw)
        review["surface_evidence_sha256"][surface] = digest

    def score(self, root, fixture, *, evidence=True, audit_artifacts=True, output=None):
        h, o, data = fixture
        output = output or root / "score"
        args = ["score", "--h-export", str(h), "--o-export", str(o), "--output", str(output)]
        if evidence:
            evidence_file = root / "eval.json"
            evidence_file.write_text(json.dumps(data), encoding="utf-8")
            args.extend(("--formal-evidence", str(evidence_file)))
            if audit_artifacts:
                args.extend(("--formal-audit-dir", str(root / "audit-originals")))
        with no_network():
            code, _, err = run(args)
        if code:
            self.assertFalse(output.exists())
            return code, err
        return code, json.loads((output / "score.json").read_text(encoding="utf-8"))

    def scored(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, document = self.score(root, self.fixture(root / "raw", **kwargs))
            self.assertEqual(0, code, document)
            self.assertIn("formal_evidence_sha256", document["inputs"])
            return document["runs"][0]

    def test_no_outage_removes_recovery_without_dropping_the_trial(self):
        scored = self.scored()
        incident, = scored["incidents"]
        self.assertEqual("CONFIRMED", incident["label"])
        self.assertEqual("NO_OUTAGE_OBSERVED", incident["business_probe"]["checkout"]["status"])
        self.assertNotIn("t_rec", incident["milestones"])
        self.assertEqual(NOT_EVALUABLE, incident["mttr"])
        kpi = scored["metrics"]["kpi"]
        self.assertEqual({"MTTR": NOT_EVALUABLE, "TotalRecovery": NOT_EVALUABLE,
                          "M7": NOT_EVALUABLE, "M8": NOT_EVALUABLE}, kpi["recovery"])
        self.assertTrue({"mttr_120", "r_t", "failure_rate"}.isdisjoint(kpi))
        for key in ("mttd", "reaction"):
            self.assertEqual(1, kpi[key]["N"])
        self.assertEqual(1, scored["metrics"]["M12_containment"]["N"])
        self.assertNotIn("recovered", scored["metrics"]["M2_funnel"])
        self.assertEqual({"status": "NOT_MEASURED"}, scored["metrics"]["uptime"])

    def test_formal_m12_retains_an_unjoined_claim_without_scoring_it(self):
        result = self.scored(containment_event=True)["metrics"]["M12_containment"]
        self.assertEqual(("UNVERIFIED", 1, 0, 1),
                         (result["status"], result["N"], result["numerator"], result["unknown"]))
        self.assertEqual({"status": "MISSING"}, result["rate"])
        row, = result["rows"]
        self.assertEqual(1, len(row["containment_event_ids"]))

    def test_formal_incident_metrics_keep_c0_out_of_c5_denominators(self):
        scored = self.scored(c0_effect="UNKNOWN_EFFECT")
        self.assertEqual(2, len(scored["incidents"]))
        metrics = scored["metrics"]
        self.assertEqual(1, metrics["kpi"]["mttd"]["N"])
        self.assertEqual(1, metrics["kpi"]["reaction"]["N"])
        self.assertEqual(1, metrics["M2_funnel"]["requested"])
        self.assertEqual(1, metrics["M12_containment"]["N"])

    def test_confirmed_fault_effect_in_c0_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, error = self.score(root, self.fixture(root / "raw", c0_effect="CONFIRMED"))
            self.assertEqual(3, code)
            self.assertIn("C0 trial contains a confirmed fault effect", error)

    def test_terminal_model_failures_are_incorrect_not_unknown(self):
        for response in ("TIMEOUT", "SCHEMA_INVALID", "REFUSAL"):
            with self.subTest(response=response):
                metrics = self.scored(response=response)["metrics"]["decisions"]
                row, = metrics["rows"]
                self.assertEqual(("INCORRECT", response), (row["M1"], row["reason"]))
                self.assertEqual([0, 0], metrics["M1"]["bounds"])

    def test_b1_explicit_missing_observation_is_incorrect(self):
        result = self.scored(group="B1", receipt_change={"status": "OBSERVATION_MISSING"})
        metrics = result["metrics"]["decisions"]
        row, = metrics["rows"]
        self.assertEqual(("INCORRECT", "CORRECT", "OBSERVATION_MISSING"),
                         (row["M1"], row["M1_enum"], row["reason"]))
        self.assertEqual([0, 0], metrics["M1"]["bounds"])

    def test_coverage_and_observed_failure_are_independent(self):
        for gap, failure, status in ((True, False, "INSUFFICIENT_COVERAGE"),
                                     (True, True, "BUSINESS_FAILURE_OBSERVED")):
            with self.subTest(status=status):
                incident, = self.scored(gap=gap, failure=failure)["incidents"]
                observation = incident["business_probe"]["checkout"]
                self.assertEqual(status, observation["status"])
                self.assertFalse(observation["coverage_complete"])
                self.assertEqual(NOT_EVALUABLE, incident["mttr"])

    def test_m1_uses_only_joined_pre_guard_fields(self):
        for changes, expected, reason in (
                ({}, "CORRECT", None),
                ({"source": "192.0.2.2"}, "INCORRECT", "WRONG_PARAMETERS"),
                ({"fixture_uid": "different"}, "INCORRECT", "WRONG_PARAMETERS"),
                ({"ttl_s": 181}, "INCORRECT", "WRONG_PARAMETERS"),
                ({"status": "RESOLVER_ERROR"}, "INCORRECT", "RESOLVER_ERROR"),
                ({"decision_event_id": "different"}, "UNKNOWN", "PRE_GUARD_RECORD_MISSING"),
                ({"fixture_uid": None}, "UNKNOWN", "PRE_GUARD_FIELDS_UNVERIFIED"),
                ({"resolver_sha256": "3" * 64}, "UNKNOWN", "RESOLVER_PIN_UNVERIFIED")):
            with self.subTest(changes=changes):
                scored = self.scored(receipt_change=changes)
                metrics = scored["metrics"]["decisions"]
                row, = metrics["rows"]
                self.assertEqual((expected, "CORRECT", reason), (row["M1"], row["M1_enum"], row["reason"]))
                self.assertEqual(1, metrics["M1"]["N"])
                self.assertEqual(1, metrics["M1_enum"]["numerator"])
                if expected == "UNKNOWN":
                    self.assertEqual([0, 1], metrics["M1"]["bounds"])

    def test_abstain_and_no_trigger_fail_but_missing_decision_is_unknown(self):
        for options, expected in (({"response": "ABSTAIN"}, "INCORRECT"),
                                  ({"detector": False}, "INCORRECT"),
                                  ({"decision": False}, "UNKNOWN")):
            with self.subTest(options=options):
                row, = self.scored(**options)["metrics"]["decisions"]["rows"]
                self.assertEqual(expected, row["M1"])

    def test_missing_audit_does_not_enter_the_m1_denominator(self):
        decisions = self.scored(audit="UNVERIFIED")["metrics"]["decisions"]
        self.assertEqual(0, decisions["M1"]["N"])
        self.assertTrue(decisions["rows"][0]["attempted"])

    def test_gaia_terminal_abstain_is_a_first_decision(self):
        for terminal, expected in ((True, "INCORRECT"), (False, "UNKNOWN")):
            with self.subTest(terminal=terminal):
                scored = self.scored(response="ABSTAIN", stage="ANALYSIS", terminal=terminal)
                row, = scored["metrics"]["decisions"]["rows"]
                self.assertEqual(expected, row["M1"])
                self.assertEqual("ABSTAIN" if terminal else "FIRST_DECISION_MISSING", row["reason"])

    def test_access_review_needs_trial_scope_window_and_every_surface(self):
        for change in (
                lambda entry: entry.update(audit="CLEAN", audit_review=None),
                lambda entry: entry["audit_review"].update(trial_id="different"),
                lambda entry: entry["audit_review"].update(to=iso(449)),
                lambda entry: entry["audit_review"]["surface_evidence_sha256"].pop("dashboards")):
            with self.subTest(change=change):
                result = self.scored(change=change)
                self.assertEqual("UNKNOWN", next(iter(result["leak"].values()))["result"])
                self.assertEqual(0, result["metrics"]["decisions"]["M1"]["N"])

    def test_evaluator_cannot_replace_the_sealed_resolver_receipt(self):
        def replace(entry):
            entry["pre_guard"] = dict(entry["expected"], status="RESOLVED")

        result = self.scored(group="B1", receipt_change={"source": "192.0.2.2"}, change=replace)
        row, = result["metrics"]["decisions"]["rows"]
        self.assertEqual(("INCORRECT", "WRONG_PARAMETERS"), (row["M1"], row["reason"]))

    def test_audited_surface_leak_excludes_the_trial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self.fixture(root / "raw")
            h, _ = load(fixture[0], fixture[1])
            canary = next(r["envelope"]["payload"]["canary_token"] for r in h.records
                          if r["envelope"]["event_type"] == "RUN_STARTED")
            entry, = fixture[2]["trials"].values()
            self.write_audit(root / "audit-originals", entry["audit_review"], "query_results", [
                {"source_component": "reader", "field": "query_result", "text": canary}])
            code, document = self.score(root, fixture)
            self.assertEqual(0, code, document)
            result, = document["runs"]
            self.assertEqual("LEAK_DETECTED", next(iter(result["leak"].values()))["result"])
            self.assertEqual(0, result["metrics"]["decisions"]["M1"]["N"])

    def test_audit_checks_original_files_before_allowing_m1(self):
        for damage, expected in (("missing", "MISSING"), ("tampered", "HASH_MISMATCH"),
                                 ("no_directory", "MISSING"), ("none", "VERIFIED")):
            with self.subTest(damage=damage), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixture = self.fixture(root / "raw")
                entry, = fixture[2]["trials"].values()
                entry["audit_artifacts"] = {name: "VERIFIED" for name in AUDIT_SURFACES}
                digest = entry["audit_review"]["surface_evidence_sha256"]["topics"]
                original = root / "audit-originals" / digest
                if damage == "missing":
                    original.unlink()
                elif damage == "tampered":
                    original.write_bytes(b"changed")
                code, document = self.score(root, fixture, audit_artifacts=damage != "no_directory")
                self.assertEqual(0, code, document)
                result, = document["runs"]
                audit_result, = result["leak"].values()
                self.assertEqual(expected, audit_result["artifacts"]["topics"])
                clean = expected == "VERIFIED"
                self.assertEqual("CLEAN" if clean else "UNKNOWN", audit_result["result"])
                self.assertEqual(int(clean), result["metrics"]["decisions"]["M1"]["N"])

    def test_audit_files_must_match_surface_and_trial(self):
        for changes, expected in (({"trial_id": "another-trial"}, "SCOPE_MISMATCH"),
                                  ({"entries": [{"field": "prompt", "text": "x",
                                                 "source_component": "reader", "sha256": []}]}, "INVALID_CONTENT")):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixture = self.fixture(root / "raw")
                entry, = fixture[2]["trials"].values()
                self.write_audit(root / "audit-originals", entry["audit_review"], "prompts", [], **changes)
                code, document = self.score(root, fixture)
                self.assertEqual(0, code, document)
                audit_result, = document["runs"][0]["leak"].values()
                self.assertEqual(expected, audit_result["artifacts"]["prompts"])
                self.assertEqual("UNKNOWN", audit_result["result"])

    def test_unbound_prompt_copy_does_not_fill_the_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self.fixture(root / "raw")
            entry, = fixture[2]["trials"].values()
            review = entry["audit_review"]
            original = root / "audit-originals" / review["surface_evidence_sha256"]["prompts"]
            review["surfaces"] = json.loads(original.read_bytes())["entries"]
            self.write_audit(root / "audit-originals", review, "prompts", [])
            code, document = self.score(root, fixture)
            self.assertEqual(0, code, document)
            audit_result, = document["runs"][0]["leak"].values()
            self.assertEqual("UNKNOWN", audit_result["result"])
            self.assertIn("PROMPT_MISSING", audit_result["unknown"])

    def test_formal_output_cannot_be_written_inside_audit_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self.fixture(root / "raw")
            code, error = self.score(root, fixture, output=root / "audit-originals" / "score")
            self.assertEqual(4, code)
            self.assertIn("must not be inside an input", error)

    def test_formal_run_requires_matching_evaluator_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self.fixture(root / "raw")
            self.assertIn("require evaluator evidence", self.score(root, fixture, evidence=False)[1])
            fixture[2]["o_export_json_sha256"] = "0" * 64
            self.assertIn("does not match both sealed exports", self.score(root, fixture)[1])
