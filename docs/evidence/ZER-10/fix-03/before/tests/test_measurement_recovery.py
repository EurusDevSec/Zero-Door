"""D-04 recovery evaluator (contract 7.5) against hand-computed expectations; offline, stdlib only."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from measurement.recovery import RecoveryMonitor, evaluate, evaluator_payloads, outcome  # noqa: E402

EXPECTED = json.loads((ROOT / "tests/fixtures/zer10/expected.json").read_text())
K, S, GAP, CAP = 3, 30_000, 2_000, 600_000
PARAMS = {"k": 3, "s_s": 30, "delta_s": 1, "l_ms": 2000, "gap_s": 2, "cap_rec_s": 600}


def stream(pattern, skip=(), end_ms=250, seq_jump_at=None):
    """pattern [(from_s, to_s, ok)] at 1 s -> samples in ms; sequence = t - 20 unless jumped."""
    out, seq = [], 0
    for start, stop, ok in pattern:
        for t in range(start, stop + 1):
            if t in skip:
                continue
            if seq_jump_at is not None and t == seq_jump_at:
                seq += 1  # a sample taken and lost: its sequence is missing
            out.append({"t": t * 1000, "end": t * 1000 + end_ms, "ok": ok, "seq": seq, "event_id": f"evt-{t}",
                        "probe_id": "prb-0", "probe_version": "p0", "flow": "checkout"})
            seq += 1
    return out


class Recovery(unittest.TestCase):
    def run_d04(self, samples, t_eff=101_000):
        return evaluate(samples, t_eff, K, S, GAP, CAP)

    def test_e01_t_rec_is_kth_sample_start_and_evidence_ends_after_s(self):
        r = self.run_d04(stream([(20, 100, True), (101, 188, False), (189, 260, True)]))
        e = EXPECTED["E01"]
        v = r["verified"]
        self.assertEqual(e["t_rec_s"] * 1000, v["t_rec"])
        self.assertEqual(221_000, v["recovery_verified_at"])
        self.assertEqual(e["evidence_complete_s"] * 1000, v["evidence_complete_at"])
        self.assertEqual(e["sample_seq_range"], v["sample_seq_range"])
        ids = [f"evt-{t}" for t in range(189, 222)]
        self.assertEqual("sha256:" + hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest(), v["samples_sha256"])
        self.assertEqual("VERIFIED", outcome(r))

    def test_k_boundary_two_passes_are_not_a_candidate(self):
        r = self.run_d04(stream([(101, 140, False), (141, 142, True), (143, 800, False)]))
        self.assertIsNone(r["verified"])
        self.assertEqual("TIMEOUT", outcome(r))
        control = self.run_d04(stream([(101, 140, False), (141, 143, True), (144, 800, False)]))
        self.assertEqual([143_000], [x["candidate_t_rec"] for x in control["relapses"]])

    def test_relapse_cancels_candidate_e05(self):
        r = self.run_d04(stream([(101, 140, False), (141, 150, True), (151, 160, False), (161, 260, True)]))
        self.assertEqual([{"candidate_t_rec": 143_000, "failing_sample_t": 151_000, "failing_event_id": "evt-151"}], r["relapses"])
        self.assertEqual(163_000, r["verified"]["t_rec"])

    def test_missing_samples_after_candidate_is_missing_probe_e06(self):
        r = self.run_d04(stream([(101, 140, False), (141, 150, True)]))
        self.assertEqual("MISSING_PROBE", outcome(r))
        self.assertEqual("DATA_ENDS_IN_S", r["unverifiable"][0]["reason"])

    def test_candidate_at_cap_is_considered_after_cap_is_not(self):
        at_cap = self.run_d04(stream([(101, 698, False), (699, 800, True)]))
        self.assertEqual(701_000, at_cap["verified"]["t_rec"])
        after = self.run_d04(stream([(101, 699, False), (700, 800, True)]))
        self.assertIsNone(after["verified"])
        self.assertEqual("TIMEOUT", outcome(after))

    def test_gap_in_s_is_unverifiable_then_search_continues_after_gap(self):
        r = self.run_d04(stream([(101, 140, False), (141, 260, True)], skip=range(150, 156)))
        self.assertEqual("GAP_IN_S", r["unverifiable"][0]["reason"])
        self.assertEqual(158_000, r["verified"]["t_rec"])  # K-run 156,157,158 after the gap

    def test_lost_sequence_breaks_a_k_run_even_with_small_spacing(self):
        r = self.run_d04(stream([(101, 140, False), (141, 260, True)], seq_jump_at=142))
        # 141 and 142 are 1 s apart but a sequence between them was lost: the run restarts at 142.
        self.assertEqual(144_000, r["verified"]["t_rec"])
        control = self.run_d04(stream([(101, 140, False), (141, 260, True)]))
        self.assertEqual(143_000, control["verified"]["t_rec"])

    def test_gap_before_t_rec_flags_probe_gap(self):
        r = self.run_d04(stream([(101, 140, False), (141, 260, True)], skip=range(120, 126)))
        self.assertTrue(r["gap_before"])
        self.assertFalse(self.run_d04(stream([(101, 140, False), (141, 260, True)]))["gap_before"])

    def test_late_t_end_sets_evidence_complete(self):
        samples = stream([(101, 140, False), (141, 260, True)])
        for x in samples:
            if x["t"] == 160_000:
                x["end"] = 175_500
        self.assertEqual(175_500, self.run_d04(samples)["verified"]["evidence_complete_at"])

    def test_no_failure_after_effect_is_no_candidate(self):
        r = self.run_d04(stream([(101, 800, True)]))
        self.assertIsNone(r["verified"])
        self.assertEqual("TIMEOUT", outcome(r))  # covered, nothing to recover from: never a PASS

    def test_monitor_emits_relapse_then_verified_once_only_after_evidence(self):
        mon = RecoveryMonitor(101_000, PARAMS, {"probe_id": "prb-0", "probe_version": "p0", "flow": "checkout"}, "clk_probe_ext")
        all_samples = stream([(101, 140, False), (141, 150, True), (151, 160, False), (161, 260, True)])
        emitted = []
        for x in all_samples:
            mon.add(x)
            for typ, payload in mon.poll():
                emitted.append((x["t"], typ, payload))
        self.assertEqual(["RELAPSE", "RECOVERY_VERIFIED"], [e[1] for e in emitted])
        self.assertEqual(151_000, emitted[0][0])
        self.assertEqual(193_000, emitted[1][0])  # 163 + 30: only once that sample exists
        with self.assertRaises(ValueError):
            mon.add(dict(all_samples[0], event_id="other"))

    def test_payloads_carry_params_and_stamps(self):
        r = self.run_d04(stream([(20, 100, True), (101, 188, False), (189, 260, True)]))
        typ, p = evaluator_payloads(r, PARAMS, {"probe_id": "prb-0", "probe_version": "p0", "flow": "checkout"}, "clk_probe_ext")[-1]
        self.assertEqual("RECOVERY_VERIFIED", typ)
        self.assertEqual("1970-01-01T00:03:11.000Z", p["t_rec"])
        self.assertEqual([169, 201], p["sample_seq_range"])


if __name__ == "__main__":
    unittest.main()
