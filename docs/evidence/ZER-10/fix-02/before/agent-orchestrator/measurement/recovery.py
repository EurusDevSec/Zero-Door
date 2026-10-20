"""Recovery evaluation (ZER-32 D-04, contract 7.5) on one probe stream, on the probe clock's own readings.

Shared by the H recovery evaluator (which emits RELAPSE / RECOVERY_VERIFIED) and the scorer (which
recomputes from raw samples and never trusts RECOVERY_VERIFIED). Test oracles are computed by hand,
not with this module.

Samples: dicts {t, end, ok, seq, event_id, probe_id, probe_version, flow}, times in local ms.
A missing sequence number inside a stream is treated like a time gap: a sample that was taken but
whose result was lost is unknown, never a pass.
"""
import hashlib

from event_pipeline.contract import canonical

from .clock import stamp

RULE_VERSION = "zer32-d04/zd-measurement-0"


def samples_sha256(event_ids):
    return "sha256:" + hashlib.sha256(canonical(list(event_ids))).hexdigest()


def joined(a, b, gap_ms):
    """Consecutive samples of one stream with no lost sequence and no spacing above gap."""
    return b["t"] - a["t"] <= gap_ms and b["seq"] == a["seq"] + 1


def evaluate(samples, t_eff, k, s_ms, gap_ms, cap_ms):
    """Return a dict: verified (or None), relapses, unverifiable, covered, gap_before, first_fail."""
    stream = sorted(samples, key=lambda x: (x["t"], x["seq"]))
    after = [x for x in stream if x["t"] >= t_eff]
    out = {"verified": None, "relapses": [], "unverifiable": [], "covered": False, "gap_before": False,
           "first_fail": None}
    first_fail = next((i for i, x in enumerate(after) if not x["ok"]), None)
    if first_fail is not None:
        out["first_fail"] = after[first_fail]["t"]
    i = len(after) if first_fail is None else first_fail + 1
    while i < len(after):
        if not after[i]["ok"]:
            i += 1
            continue
        run, j = [after[i]], i + 1
        while len(run) < k and j < len(after) and after[j]["ok"] and joined(after[j - 1], after[j], gap_ms):
            run.append(after[j])
            j += 1
        if len(run) < k:
            i = j  # j > i: restart at the sample that broke the run (a fail is skipped next turn)
            continue
        t_rec = run[-1]["t"]
        if t_rec > t_eff + cap_ms:
            break  # a candidate after the cap is never considered (one exactly at the cap is)
        m, reached, relapse, broken = j, None, None, False
        prev = run[-1]
        if s_ms == 0:
            reached = j - 1  # the K-th sample itself is the first sample at or after T_rec + S
        while reached is None and m < len(after):
            x = after[m]
            if not joined(prev, x, gap_ms):
                broken = True
                break
            if x["t"] <= t_rec + s_ms and not x["ok"]:
                relapse = x
                break
            if x["t"] >= t_rec + s_ms:
                reached = m
                break
            prev = x
            m += 1
        if relapse is not None:
            out["relapses"].append({"candidate_t_rec": t_rec, "failing_sample_t": relapse["t"],
                                    "failing_event_id": relapse["event_id"]})
            i = m
            continue
        if reached is None:
            # Missing evidence in S (gap, lost sequence or end of data): not verifiable; search after it.
            out["unverifiable"].append({"candidate_t_rec": t_rec, "reason": "GAP_IN_S" if broken else "DATA_ENDS_IN_S"})
            i = m if broken else len(after)
            continue
        used = after[i:reached + 1]
        before = [x for x in after if x["t"] <= t_rec]
        out["gap_before"] = any(not joined(a, b, gap_ms) for a, b in zip(before, before[1:]))
        out["verified"] = {
            "t_rec": t_rec, "recovery_verified_at": t_rec + s_ms,
            "evidence_complete_at": max(x["end"] for x in used),
            "sample_seq_range": [used[0]["seq"], used[-1]["seq"]],
            "event_ids": [x["event_id"] for x in used],
            "samples_sha256": samples_sha256(x["event_id"] for x in used),
            "probe_ids": sorted({x["probe_id"] for x in used}),
            "probe_versions": sorted({x["probe_version"] for x in used}),
            "flows": sorted({x["flow"] for x in used}),
        }
        out["covered"] = True
        return out
    horizon = [x for x in after if x["t"] <= t_eff + cap_ms]
    horizon += [x for x in after if x["t"] > t_eff + cap_ms][:1]
    out["covered"] = bool(horizon) and horizon[0]["t"] - t_eff <= gap_ms and horizon[-1]["t"] >= t_eff + cap_ms \
        and all(joined(a, b, gap_ms) for a, b in zip(horizon, horizon[1:]))
    return out


def outcome(result):
    """VERIFIED, TIMEOUT (covered to the cap, no verified candidate) or MISSING_PROBE."""
    if result["verified"]:
        return "VERIFIED"
    if result["covered"] and not result["unverifiable"]:
        return "TIMEOUT"
    return "MISSING_PROBE"


def evaluator_payloads(result, params, probe, evidence_clock_id):
    """RELAPSE and RECOVERY_VERIFIED payloads for the H recovery evaluator (contract 5.3, 7.5).

    `probe` = {probe_id, probe_version, flow}. Emit RECOVERY_VERIFIED only after evidence_complete_at.
    """
    events = [("RELAPSE", {"flow": probe["flow"], "candidate_t_rec": stamp(r["candidate_t_rec"]),
                           "failing_sample_t": stamp(r["failing_sample_t"]), "rule_version": RULE_VERSION})
              for r in result["relapses"]]
    v = result["verified"]
    if v:
        events.append(("RECOVERY_VERIFIED", {
            "flow": probe["flow"], "probe_id": probe["probe_id"], "probe_version": probe["probe_version"],
            "evidence_clock_id": evidence_clock_id, "t_rec": stamp(v["t_rec"]),
            "recovery_verified_at": stamp(v["recovery_verified_at"]),
            "evidence_complete_at": stamp(v["evidence_complete_at"]),
            "k": params["k"], "s_s": params["s_s"], "delta_s": params["delta_s"], "l_ms": params["l_ms"],
            "gap_s": params["gap_s"], "cap_rec_s": params["cap_rec_s"],
            "sample_seq_range": v["sample_seq_range"], "samples_sha256": v["samples_sha256"],
            "rule_version": RULE_VERSION}))
    return events


class RecoveryMonitor:
    """Incremental H evaluator: feed samples as they are recorded; each decision is emitted once.

    A RELAPSE is final once its failing sample is seen; RECOVERY_VERIFIED once the sample at or after
    T_rec + S has ended (its t_end is evidence_complete_at), never earlier.
    """
    def __init__(self, t_eff, params, probe, evidence_clock_id):
        self.t_eff, self.params, self.probe, self.clock_id = t_eff, params, probe, evidence_clock_id
        self.samples, self.sent = {}, set()

    def add(self, sample):
        key = sample["seq"]
        known = self.samples.get(key)
        if known is not None and known["event_id"] != sample["event_id"]:
            raise ValueError("INTEGRITY_ERROR: two samples with one sequence")
        self.samples[key] = sample

    def poll(self):
        p = self.params
        result = evaluate(list(self.samples.values()), self.t_eff, p["k"], p["s_s"] * 1000, p["gap_s"] * 1000,
                          p["cap_rec_s"] * 1000)
        fresh = []
        for typ, payload in evaluator_payloads(result, p, self.probe, self.clock_id):
            key = (typ, payload.get("candidate_t_rec") or payload.get("t_rec"))
            if key not in self.sent:
                self.sent.add(key)
                fresh.append((typ, payload))
        return fresh
