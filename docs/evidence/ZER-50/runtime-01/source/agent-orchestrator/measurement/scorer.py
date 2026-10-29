"""Incident scoring from verified raw H/O exports (contract 4-7, ZER-32 3.2-3.5, 4).

The scorer re-derives every milestone from raw events of their permitted source: T_req/T_stop from
the harness, T_eff from EFFECT_EVALUATED, T_det from DETECTED, actions from the executor and T_rec
from PROBE_SAMPLE (RECOVERY_VERIFIED is only compared). Missing, invalid, conflicting or
unverifiable evidence keeps an incident in N with an explicit MISSING-type label; nothing is filled
with 0, a cap or a guess.
"""
import math

from event_pipeline.contract import validate
from event_pipeline.audit import audit

from . import VERSION
from .clock import ClockModel, Instant, duration, parse
from .config import ConfigError, f01 as check_f01
from .recovery import evaluate, joined, samples_sha256

SCORER_VERSION = VERSION + "/scorer"
MANDATORY = {"ATTACK_REQUESTED", "ATTACK_STOPPED", "EFFECT_EVALUATED", "PROBE_SAMPLE", "DETECTED", "DECISION",
             "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
O_LINKED = {"DETECTED", "DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
ZD_ACTIONS = {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
ERROR_CLASSES = {"TIMEOUT", "CONNECT", "CONTENT", "SLOW"}
# Validator classes that make an event INVALID (contract 5.3/6.4). Other quarantine classes are kept
# and counted but do not make an incident MISSING by themselves (SOURCE_VIOLATION: stored, unused).
INVALID_CLASSES = {"MISSING_FIELD", "INVALID", "SEMANTIC", "INVALID_ID", "INVALID_TIMESTAMP",
                   # Gateway binding refusals: the event exists but cannot be used, so a mandatory milestone
                   # it carried is unknown (MISSING), never absent (MISSED).
                   "RUN_CONTEXT_MISSING", "TRIAL_CONTEXT_MISSING", "CONTEXT_IMMUTABLE"}
HARD = {"INVALID_CLOCK", "INTEGRITY_ERROR", "LINK_CONFLICT", "AMBIGUOUS", "INVALID_EVENT", "TARGET_MISMATCH",
        "ORPHAN_IN_WINDOW", "PARAMS_INVALID", "MODE_VIOLATION", "FLOW_UNKNOWN", "MULTIPLE_PROBES_OPEN",
        "EFFECT_CONFLICT", "INCIDENT_CONFLICT", "TRIAL_MISSING", "REQUEST_INVALID", "REQUEST_LATE"}
# Rejection classes that say the producer is not the harness: such an ATTACK_REQUESTED is stored, never a request.
NOT_A_HARNESS_REQUEST = {"SOURCE_VIOLATION", "PLANE_VIOLATION"}
# Business keys with a contract cardinality (3.2): a second distinct event for the key is never resolved by order.
CARDINALITY = {"DECISION": "decision_id", "GUARD_VERDICT": "decision_id", "API_ACCEPTED": "action_id"}
DECIDERS = {"B1": {"decision_rules"}, "B2": {"decision_llm"}, "B3": {"decision_single_llm"}, "BM": {"operator_console"}}
LLM_SOURCES = {"B2": {"decision_llm"}, "B3": {"decision_single_llm"}}


def ms(text):
    try:
        return parse(text)
    except ValueError:
        return None


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def identity(event, run_id):
    """(trial_id, incident_id) of a harness envelope whose run/trial/incident IDs can be trusted, else None.

    Only the IDs are read: a request that failed validation keeps its place in the cohort, but none of
    its other fields (targets, flow, times) is guessed.
    """
    ids = {k: event.get(k) for k in ("run_id", "trial_id", "incident_id")}
    if ids["run_id"] != run_id or event.get("source_component") not in (None, "harness"):
        return None
    for key, prefix in (("trial_id", "trl_"), ("incident_id", "inc_")):
        value = ids[key]
        if not (isinstance(value, str) and value.startswith(prefix) and 4 < len(value) <= 64 and value.isascii()):
            return None
    return ids["trial_id"], ids["incident_id"]


def semantic(event, f01):
    """Scorer checks beyond the transport validator (contract 5.3 cross-field rules). None = valid."""
    typ, p = event["event_type"], event["payload"]
    if typ == "PROBE_SAMPLE":
        if not all(isinstance(p.get(k), str) and p[k] for k in ("probe_id", "flow", "probe_version")):
            return "INVALID"
        if type(p["sequence"]) is not int or p["sequence"] < 0 or type(p["pass"]) is not bool:
            return "INVALID"
        start, end = ms(p["t_start"]), ms(p["t_end"])
        if start is None or end is None or not number(p["latency_ms"]):
            return "INVALID"
        if end < start or p["latency_ms"] < 0 or p["pass"] != (p["error_class"] is None):
            return "SEMANTIC"
        if not p["pass"] and not isinstance(p["error_class"], str):
            return "INVALID"
        if p["pass"] and f01 is not None and p["latency_ms"] > f01["l_ms"]:
            return "SEMANTIC"
    elif typ == "CLOCK_SYNC":
        if ms(p["measured_at"]) is None or not number(p["offset_ms"]) or not isinstance(p["clock_id"], str):
            return "INVALID"
        if p["uncertainty_ms"] is not None and (not number(p["uncertainty_ms"]) or p["uncertainty_ms"] < 0):
            return "INVALID"
    elif typ == "EFFECT_EVALUATED":
        if p["status"] == "CONFIRMED" and ms(p["t_eff"]) is None:
            return "INVALID"
        if not isinstance(p["evidence_clock_id"], str) or not (p["w_eff_s"] is None or number(p["w_eff_s"])):
            return "INVALID"
    elif typ == "RECOVERY_VERIFIED":
        stamps = [ms(p[k]) for k in ("t_rec", "recovery_verified_at", "evidence_complete_at")]
        rng = p["sample_seq_range"]
        if None in stamps or not (isinstance(rng, list) and len(rng) == 2 and all(type(x) is int for x in rng)) or rng[0] > rng[1]:
            return "INVALID"
        if stamps[2] < stamps[1]:
            return "SEMANTIC"
    elif typ == "RELAPSE":
        a, b = ms(p["candidate_t_rec"]), ms(p["failing_sample_t"])
        if a is None or b is None:
            return "INVALID"
        if b <= a:
            return "SEMANTIC"
    elif typ == "AUDIT_COVERAGE":
        a, b = ms(p["from"]), ms(p["to"])
        if a is None or b is None or b < a:
            return "SEMANTIC"
    elif typ == "ATTACK_REQUESTED":
        if not isinstance(p["target_services"], list) or not all(isinstance(s, str) for s in p["target_services"]):
            return "INVALID"
    elif typ == "LLM_CALL":
        usage, cost = p.get("usage"), p.get("cost")
        if not isinstance(usage, dict) or usage.get("status") not in {"COMPLETE", "MISSING", "NOT_APPLICABLE"}:
            return "INVALID"
        if usage["status"] == "COMPLETE" and not all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("input_tokens", "output_tokens")):
            return "INVALID"
        if not isinstance(cost, dict) or cost.get("status") not in {"COMPLETE", "MISSING", "NOT_APPLICABLE"}:
            return "INVALID"
        if cost["status"] == "COMPLETE" and (not number(cost.get("usd")) or cost["usd"] < 0 or not cost.get("price_ref")):
            return "INVALID"
        if type(p["attempt_no"]) is not int or p["attempt_no"] < 1 or (p["attempt_no"] > 1) != (p["retry_reason"] is not None):
            return "SEMANTIC"
    return None


class Scorer:
    """Score one run. `options`: required_flows (F-04), criteria_version (optional), benign (M5/M6).

    `others`: verified exports of the OTHER runs of the same archive. Contract 6.3 makes an event of
    another run that carries this run's incident_id/trial_id a LINK_CONFLICT; without them that check
    cannot be made and the run carries CROSS_RUN_LINKS_UNCHECKED.
    """
    def __init__(self, h, o, options=None, others=None):
        self.h, self.o, self.options = h, o, dict(options or {})
        self.others = list(others or [])
        self.findings = {"duplicates": 0, "integrity_errors": [], "invalid": [], "source_violations": [],
                         "plane_violations": [], "mode_violations": [], "orphans": [], "link_conflicts": [],
                         "ambiguous": [], "late_ingest": 0, "quarantined": {}, "archive_scope": 0,
                         "unattributable_quarantine": 0, "unsupported": 0, "unregistered_probe_samples": 0,
                         "quarantined_link_conflicts": [], "quarantined_mode_violations": [], "quarantined_leaks": [],
                         "foreign_references": [], "lost_requests": [], "cardinality_violations": []}
        self.flags = set()

    # ----------------------------------------------------------------- raw intake
    def intake(self):
        seen, self.events, self.invalid = {}, [], []
        # Every envelope kept outside the scored raw (quarantine, late, archive scope): the cohort is
        # rebuilt from these too, so a request never leaves the denominator because it was rejected.
        self.unscored = []
        planes = [("H", self.h)] + ([("O", self.o)] if self.o else [])
        for plane, export in planes:
            for record in export.records:
                event = record["envelope"]
                digest = record["envelope_sha256"]
                known = seen.get(event.get("event_id"))
                if known is not None:
                    if known == digest:
                        self.findings["duplicates"] += 1
                    else:
                        self.findings["integrity_errors"].append(event["event_id"])
                    continue
                seen[event.get("event_id")] = digest
                self.events.append((plane, event))
            for record in export.rejections:
                kind = record.get("classification", "UNKNOWN")
                self.findings["quarantined"][kind] = self.findings["quarantined"].get(kind, 0) + 1
                envelope = record.get("envelope")
                if isinstance(envelope, dict):
                    self.unscored.append((kind, envelope))
                if not isinstance(envelope, dict):
                    self.findings["unattributable_quarantine"] += 1
                elif kind == "INTEGRITY_ERROR":
                    self.findings["integrity_errors"].append(envelope.get("event_id"))
                elif kind in INVALID_CLASSES:
                    self.invalid.append((kind, envelope))
                elif kind == "LINK_CONFLICT":
                    self.findings["quarantined_link_conflicts"].append(envelope)
                elif kind == "MODE_VIOLATION":
                    self.findings["quarantined_mode_violations"].append(envelope)
                elif kind == "LEAK_DETECTED":
                    self.findings["quarantined_leaks"].append(envelope)
            for record in export.late:
                if isinstance(record.get("envelope"), dict):
                    self.unscored.append(("LATE:" + str(record.get("classification")), record["envelope"]))
                if record.get("classification") == "LATE_INGEST":
                    self.findings["late_ingest"] += 1
                else:
                    kind = record.get("classification", "UNKNOWN")
                    self.findings["quarantined"][kind] = self.findings["quarantined"].get(kind, 0) + 1
            self.findings["archive_scope"] += len(export.archive_scope)
            for record in export.archive_scope:
                if isinstance(record.get("envelope"), dict):
                    self.unscored.append(("ARCHIVE_SCOPE:" + str(record.get("classification")), record["envelope"]))
        if self.findings["unattributable_quarantine"]:
            self.flags.add("UNATTRIBUTABLE_QUARANTINE")
        self.findings["integrity_errors"] = sorted(set(self.findings["integrity_errors"]) - {None})

    def classify(self):
        """Split events into usable / invalid / source or plane violations / mode violations."""
        run_started = [e for p, e in self.events if p == "H" and e.get("event_type") == "RUN_STARTED"]
        self.f01, self.reference = None, None
        if len(run_started) == 1:
            try:
                self.f01 = check_f01(run_started[0]["payload"].get("f01_params"))
            except (ConfigError, AttributeError):
                self.f01 = None
            self.reference = run_started[0]["payload"].get("reference_clock_id")
            self.group = run_started[0].get("group")
            self.canary = run_started[0]["payload"].get("canary_token")
        else:
            self.group = None
        if self.f01 is None:
            self.flags.add("PARAMS_INVALID")
        self.used = []
        for plane, event in self.events:
            error = validate(event, plane)
            if error in {"SOURCE_VIOLATION"}:
                self.findings["source_violations"].append(event.get("event_id"))
                continue
            if error in {"PLANE_VIOLATION", "LEAK_DETECTED"}:
                self.findings["plane_violations"].append(event.get("event_id"))
                continue
            if error == "UNSUPPORTED":
                self.findings["unsupported"] += 1
                self.unscored.append(("UNSUPPORTED", event))
                continue
            if error == "MODE_VIOLATION":
                self.findings["mode_violations"].append(event.get("event_id"))
                self.used.append(event)  # valid evidence; the trial is not usable as its group (7.4)
                continue
            if error is None:
                error = semantic(event, self.f01)
            if error:
                self.invalid.append((error, event))
                self.findings["invalid"].append({"event_id": event.get("event_id"), "type": event.get("event_type"), "class": error})
                continue
            if self.group is not None and event["group"] != self.group:
                self.findings["mode_violations"].append(event["event_id"])
            self.used.append(event)
        self.by_type = {}
        for event in self.used:
            self.by_type.setdefault(event["event_type"], []).append(event)

    def of(self, typ, trial=None):
        return [e for e in self.by_type.get(typ, []) if trial is None or e.get("trial_id") == trial]

    # ----------------------------------------------------------------- clocks and incidents
    def trials(self):
        self.trial = {}
        for event in self.of("TRIAL_STARTED"):
            t = self.trial.setdefault(event["trial_id"], {"starts": [], "ends": []})
            t["starts"].append(event)
        for event in self.of("TRIAL_ENDED"):
            self.trial.setdefault(event["trial_id"], {"starts": [], "ends": []})["ends"].append(event)
        for trial_id, t in self.trial.items():
            start = t["starts"][0] if len(t["starts"]) == 1 else None
            end = t["ends"][0] if len(t["ends"]) == 1 else None
            harness_ok = lambda e: e is not None and (e["clock"]["clock_source"] == "HOST_SHARED" or e["clock"]["clock_id"] == self.reference)
            model = ClockModel(self.reference, ms(start["ts_event"]) if harness_ok(start) else None,
                               ms(end["ts_event"]) if harness_ok(end) else None)
            for event in self.used:
                if event.get("trial_id") in (trial_id, None):
                    model.see(event["clock"])
            for event in self.of("CLOCK_SYNC", trial_id):
                model.sync(event["payload"])
            t["clock"] = model
            t["probes"] = start["payload"]["probes"] if start and isinstance(start["payload"].get("probes"), list) else []
            t["start"], t["end"] = start, end

    def at(self, trial, clock_id, text):
        value = ms(text)
        if value is None or trial not in self.trial:
            return None
        return self.trial[trial]["clock"].at(clock_id, value)

    def stamp_of(self, event, field=None, envelope_field=None):
        """Instant of an event timestamp, owned by the right clock (contract 4.2)."""
        if envelope_field:
            text, clock_id = event.get(envelope_field), event["clock"]["clock_id"]
        elif field:
            text = event["payload"].get(field)
            clock_id = event["payload"].get("evidence_clock_id") or event["clock"]["clock_id"]
        else:
            text, clock_id = event["ts_event"], event["clock"]["clock_id"]
        if text is None:
            return None
        return self.at(event.get("trial_id"), clock_id, text)

    def incidents(self):
        self.inc = {}
        gts = {}
        for event in self.of("GROUND_TRUTH_LOCKED"):
            gts.setdefault(event["payload"].get("variant_id"), []).append(event["payload"])
        self.h_orphans = []
        for event in self.of("ATTACK_REQUESTED"):
            key = event["incident_id"]
            if key in self.inc:
                self.inc[key]["missing"].add("INCIDENT_CONFLICT")
                continue
            p = event["payload"]
            gt = gts.get(p.get("variant_ref"), [])
            self.inc[key] = self.new_incident(key, event["trial_id"], event, self.stamp_of(event), set(p["target_services"]),
                                              (event.get("target") or {}).get("flow"), gt)
        self.lost_requests(gts)
        self.slots = {e.get("incident_id") for e in self.of("TRIAL_CONTEXT") if e.get("incident_id")} - set(self.inc)
        for typ, field in (("ATTACK_STOPPED", "stop"), ("EFFECT_EVALUATED", "effects"), ("RECOVERY_VERIFIED", "rv"),
                           ("RELAPSE", "relapse"), ("CONTAINMENT_VERIFIED", "containment")):
            for event in self.of(typ):
                inc = self.inc.get(event["incident_id"])
                if inc is None:
                    self.findings["orphans"].append(event["event_id"])
                    if typ == "EFFECT_EVALUATED":
                        self.h_orphans.append(event)
                elif event["trial_id"] != inc["trial"]:
                    self.conflict([inc["id"]], event, "H event trial differs from incident trial")
                else:
                    inc[field].append(event)
        for inc in self.inc.values():
            if self.f01 is None:
                inc["missing"].add("PARAMS_INVALID")
            if inc["trial"] not in self.trial or self.trial[inc["trial"]]["start"] is None:
                inc["missing"].add("TRIAL_MISSING")

    @staticmethod
    def new_incident(key, trial, req, t_req, targets, flow, gt):
        return {"id": key, "trial": trial, "req": req, "t_req": t_req, "targets": targets, "flow": flow,
                "gt": gt[0] if len(gt) == 1 else None, "gt_conflict": len(gt) > 1,
                "missing": set(), "flags": set(), "stop": [], "effects": [], "detected": [], "mismatched": [],
                "decisions": [], "actions": {}, "rv": [], "relapse": [], "containment": [], "calls": []}

    def lost_requests(self, gts):
        """Requested turns whose ATTACK_REQUESTED is unusable: invalid, quarantined, late or unsupported.

        Contract 6.4 / AC-03: the turn stays in the cohort as MISSING with its reason. Only the IDs of
        such an envelope are read (targets, flow and times are never guessed from it). A request that
        cannot be attributed to a trial/incident makes the cohort incomplete, so no verdict can PASS.
        """
        self.cohort = {"complete": True, "problems": []}
        seen = set()
        for kind, event in [(k, e) for k, e in self.invalid if isinstance(e, dict)] + self.unscored:
            if event.get("event_type") != "ATTACK_REQUESTED" or kind.split(":")[-1] in NOT_A_HARNESS_REQUEST:
                continue
            eid = event.get("event_id") if isinstance(event.get("event_id"), str) else None
            if (isinstance(event.get("run_id"), str) and event["run_id"] != self.h.run_id) or (eid, kind) in seen:
                continue  # another run's request (cross-run checks are separate), or the same record twice
            seen.add((eid, kind))
            reason = "REQUEST_LATE" if kind.startswith("LATE:") else "REQUEST_INVALID"
            ids = identity(event, self.h.run_id)
            if ids is None:
                self.cohort["problems"].append({"event_id": eid, "class": kind, "why": "REQUEST_IDENTITY_UNTRUSTED"})
                continue
            trial, key = ids
            self.findings["lost_requests"].append({"event_id": eid, "incident_id": key, "class": kind})
            if key in self.inc:
                if self.inc[key]["req"].get("event_id") != eid:
                    self.inc[key]["missing"].add(reason)  # a second, unusable request for this incident
                continue
            target = event.get("target") if isinstance(event.get("target"), dict) else {}
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            variant = payload.get("variant_ref")
            flow = target.get("flow") if isinstance(target.get("flow"), str) else None
            self.inc[key] = self.new_incident(key, trial, dict(event, payload=payload), None, set(), flow,
                                              gts.get(variant, []) if isinstance(variant, str) else [])
            self.inc[key]["missing"].add(reason)
            self.inc[key]["targets_unknown"] = True
            self.inc[key]["flags"].add("TARGETS_UNKNOWN")
        if self.findings["unattributable_quarantine"]:
            self.cohort["problems"].append({"event_id": None, "class": "UNATTRIBUTABLE_QUARANTINE",
                                            "why": "a rejection of this run without an envelope may be a request"})
        if self.cohort["problems"]:
            self.cohort["complete"] = False
            self.flags.add("COHORT_INCOMPLETE")

    def conflict(self, ids, event, why):
        self.findings["link_conflicts"].append({"event_id": event.get("event_id"), "why": why, "incidents": sorted(ids)})
        for key in ids:
            if key in self.inc:
                self.inc[key]["missing"].add("LINK_CONFLICT")

    def effect(self, inc):
        """(status, T_eff Instant or None, W_eff seconds or None) per contract 7.2."""
        records = inc["effects"]
        wanted = self.options.get("criteria_version")
        if wanted:
            records = [e for e in records if e["payload"]["criteria_version"] == wanted]
        versions = {e["payload"]["criteria_version"] for e in records}
        if len(versions) > 1 or len({(e["payload"]["status"], e["payload"]["t_eff"]) for e in records}) > 1:
            inc["missing"].add("EFFECT_CONFLICT")
            return "UNKNOWN_EFFECT", None, None
        if not records:
            inc["flags"].add("EFFECT_RECORD_MISSING")
            return "UNKNOWN_EFFECT", None, None
        p = records[0]["payload"]
        inc["effect_event"] = records[0]
        if p["evidence"] and isinstance(p["evidence"], dict) and p["evidence"].get("flow") not in (None, inc["flow"]):
            inc["missing"].add("FLOW_UNKNOWN")
            inc["flags"].add("EFFECT_FLOW_DIFFERS")
        if p["status"] == "CONFIRMED":
            return "CONFIRMED", self.stamp_of(records[0], "t_eff"), p["w_eff_s"]
        if p["status"] == "CONFIRMED_NO_EFFECT":
            return self.no_effect(inc, p), None, p["w_eff_s"]
        return "UNKNOWN_EFFECT", None, p["w_eff_s"]

    def no_effect(self, inc, p):
        """NO_EFFECT leaves N only if raw probe samples cover [T_req, T_req + W_eff] with no failure."""
        stream, clock_id = self.stream(inc)
        if stream is None or not number(p["w_eff_s"]) or inc["t_req"] is None:
            inc["flags"].add("NO_EFFECT_NOT_RECOMPUTABLE")
            return "UNKNOWN_EFFECT"
        t_req = self.local(inc, inc["t_req"], clock_id)
        if t_req is None:
            inc["flags"].add("NO_EFFECT_CLOCK_UNVERIFIED")
            return "UNKNOWN_EFFECT"
        end, gap = t_req + p["w_eff_s"] * 1000, self.f01["gap_s"] * 1000
        window = [x for x in stream if t_req <= x["t"] <= end]
        covered = bool(window) and window[0]["t"] - t_req <= gap and end - window[-1]["t"] <= gap \
            and all(joined(a, b, gap) for a, b in zip(window, window[1:]))
        if not covered:
            inc["flags"].add("NO_EFFECT_COVERAGE_GAP")
            return "UNKNOWN_EFFECT"
        if any(not x["ok"] for x in window):
            inc["flags"].add("NO_EFFECT_CONTRADICTED_BY_SAMPLES")
            return "UNKNOWN_EFFECT"
        return "CONFIRMED_NO_EFFECT"

    def local(self, inc, instant, clock_id):
        """An Instant expressed on `clock_id`'s local axis, or None if that needs an unverified clock."""
        if instant is None:
            return None
        if instant.clock_id == clock_id:
            return instant.ms if not instant.verified or self.is_reference(inc, clock_id) else \
                self.trial[inc["trial"]]["clock"].to_local(clock_id, instant.ms)
        model = self.trial[inc["trial"]]["clock"]
        verified, _ = model.state(clock_id)
        if not instant.verified or not verified:
            return None
        if self.is_reference(inc, clock_id):
            return instant.ms
        return model.to_local(clock_id, instant.ms)

    def is_reference(self, inc, clock_id):
        meta = self.trial[inc["trial"]]["clock"].meta.get(clock_id, {})
        return meta.get("clock_source") == "HOST_SHARED" or clock_id == self.reference

    def stream(self, inc):
        """Samples of the registered probe for the incident's flow: (samples, clock_id) or (None, None)."""
        if inc["flow"] is None:
            inc["missing"].add("FLOW_UNKNOWN")
            return None, None
        trial = self.trial.get(inc["trial"])
        regs = [r for r in (trial["probes"] if trial else []) if isinstance(r, dict) and r.get("flow") == inc["flow"]]
        if len(regs) != 1:
            # No probe: no recovery evidence (MISSING_PROBE). Several probes on one flow is OPEN (ZER-38):
            # never mixed to fill gaps, so the incident is MISSING.
            inc["missing"].add("PROBE_NOT_REGISTERED" if not regs else "MULTIPLE_PROBES_OPEN")
            return None, None
        reg = regs[0]
        out, keys = [], {}
        for event in self.of("PROBE_SAMPLE", inc["trial"]):
            p = event["payload"]
            if p["flow"] != inc["flow"]:
                continue
            if (p["probe_id"], p["probe_version"]) != (reg.get("probe_id"), reg.get("probe_version")) or \
                    event["clock"]["clock_id"] != reg.get("clock_id"):
                self.findings["unregistered_probe_samples"] += 1
                continue
            key = p["sequence"]
            if key in keys and keys[key] != event["event_id"]:
                inc["missing"].add("INTEGRITY_ERROR")
                inc["flags"].add("SAMPLE_KEY_CONFLICT")
            keys[key] = event["event_id"]
            out.append({"t": ms(p["t_start"]), "end": ms(p["t_end"]), "ok": p["pass"], "seq": p["sequence"],
                        "event_id": event["event_id"], "probe_id": p["probe_id"], "probe_version": p["probe_version"],
                        "flow": p["flow"]})
        out.sort(key=lambda x: (x["t"], x["seq"]))
        return out, reg.get("clock_id")

    # ----------------------------------------------------------------- O linking (6.3)
    def link(self):
        o_events = [e for e in self.used if e["event_type"] in O_LINKED]
        known = set(self.inc) | self.slots
        explicit, links = {}, {e["event_id"]: set() for e in o_events}
        self.slot_events = {}
        for event in o_events:
            iid = event.get("incident_id")
            if iid is not None:
                if iid not in known:
                    self.findings["orphans"].append(event["event_id"])
                    explicit[event["event_id"]] = None
                    if event["event_type"] in {"DETECTED", "ACTION_COMPLETED"}:
                        self.orphan_in_window(event)
                    continue
                if iid in self.slots:
                    self.slot_events.setdefault(iid, []).append(event)
                    explicit[event["event_id"]] = None
                    continue
                explicit[event["event_id"]] = iid
                links[event["event_id"]].add(iid)
        decisions, actions = {}, {}
        heal_decision = {}

        def propagate():
            for _ in range(4):  # the causal chain is short; four passes reach a fixed point
                for event in o_events:
                    eid, typ = event["event_id"], event["event_type"]
                    if explicit.get(eid, 0) is None:
                        continue
                    found = set(links[eid])
                    cause = event.get("causation_id")
                    if cause in links:
                        found |= links[cause]
                    if typ == "DECISION":
                        for item in event["payload"]["inputs"]:
                            found |= links.get(item["event_id"], set())
                    if typ in {"LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED"} or (typ in {"API_ACCEPTED", "ACTION_COMPLETED"} and event.get("decision_id")):
                        found |= decisions.get(event.get("decision_id"), set())
                    if typ in {"API_ACCEPTED", "ACTION_COMPLETED"}:
                        found |= actions.get(event.get("action_id"), set())
                    links[eid] = found
                    if typ == "DECISION":
                        decisions.setdefault(event["decision_id"], set()).update(found)
                    if typ == "HEAL_STARTED":
                        actions.setdefault(event["action_id"], set()).update(found)
                        heal_decision[event["action_id"]] = event["decision_id"]
        propagate()
        # Window rule, only for DETECTED with no explicit or causal path; then the chain is propagated again.
        self.window_linked = set()
        for event in o_events:
            if event["event_type"] == "DETECTED" and not links[event["event_id"]] and explicit.get(event["event_id"], 0) is not None:
                cands = self.window_candidates(event)
                service = (event.get("target") or {}).get("service")
                if len(cands) > 1:
                    cands = [c for c in cands if service in self.inc[c]["targets"]] or cands
                if len(cands) > 1:
                    self.findings["ambiguous"].append({"event_id": event["event_id"], "incidents": sorted(cands)})
                    for c in cands:
                        self.inc[c]["missing"].add("AMBIGUOUS")
                    continue
                links[event["event_id"]] = set(cands)
                self.window_linked.add(event["event_id"])
        propagate()
        # Invariants and assignment.
        for event in o_events:
            eid = event["event_id"]
            found = links[eid]
            if explicit.get(eid, 0) is None and not found:
                continue
            if len(found) > 1:
                self.conflict(found, event, "paths reach different incidents")
                continue
            if not found:
                if event["event_type"] in {"DETECTED", "ACTION_COMPLETED"}:
                    self.findings["orphans"].append(eid)
                    self.orphan_in_window(event)
                continue
            inc = self.inc[next(iter(found))]
            if event.get("trial_id") not in (None, inc["trial"]):
                self.conflict({inc["id"]}, event, "trial differs from incident trial")
                continue
            if event["event_type"] in {"API_ACCEPTED", "ACTION_COMPLETED"} and event.get("decision_id") and \
                    event["action_id"] in heal_decision and event["decision_id"] != heal_decision[event["action_id"]]:
                self.conflict({inc["id"]}, event, "decision_id differs from HEAL_STARTED")
                continue
            self.attach(inc, event)

    def cardinality(self):
        """Contract 3.2 cardinalities after event_id dedup: one DECISION per decision_id, 0..1 GUARD_VERDICT
        per decision_id, 0..1 API_ACCEPTED per action_id. Extra distinct events are kept as evidence and the
        key is marked conflicted; metrics then report it as unknown instead of picking one by ingest order."""
        for inc in self.inc.values():
            inc["conflicted"] = set()
            pools = {"DECISION": inc["decisions"], "GUARD_VERDICT": inc.get("guards", []),
                     "API_ACCEPTED": [e for a in inc["actions"].values() for e in a.get("API_ACCEPTED", [])]}
            for typ, events in pools.items():
                by_key = {}
                for event in events:
                    by_key.setdefault(event.get(CARDINALITY[typ]), set()).add(event["event_id"])
                for key, ids in sorted(by_key.items(), key=lambda kv: str(kv[0])):
                    if len(ids) > 1:
                        inc["conflicted"].add((typ, key))
                        inc["flags"].add("CARDINALITY_VIOLATION")
                        self.findings["cardinality_violations"].append(
                            {"incident_id": inc["id"], "type": typ, "key": key, "event_ids": sorted(ids)})

    def window_end(self, inc, t_eff=None, w_eff=None):
        f = self.f01
        if t_eff is not None and inc["t_req"] is not None and t_eff.comparable(inc["t_req"]):
            return Instant(t_eff.ms + f["cap_det_s"] * 1000, t_eff.clock_id, t_eff.verified, t_eff.error_ms, t_eff.resolution_ms)
        if inc["t_req"] is not None and number(w_eff):
            r = inc["t_req"]
            return Instant(r.ms + (w_eff + f["cap_det_s"]) * 1000, r.clock_id, r.verified, r.error_ms, r.resolution_ms)
        return None

    def incident_end(self, inc):
        """End of the incident window for ORPHAN/INVALID relatedness: base + max(caps) + S; None = open."""
        _, t_eff, w_eff = self.effect_cache(inc)
        f = self.f01
        extra = (max(f["cap_det_s"], f["cap_rec_s"]) + f["s_s"]) * 1000
        if t_eff is not None and inc["t_req"] is not None and t_eff.comparable(inc["t_req"]):
            base = t_eff
        elif inc["t_req"] is not None and number(w_eff):
            r = inc["t_req"]
            base = Instant(r.ms + w_eff * 1000, r.clock_id, r.verified, r.error_ms, r.resolution_ms)
        else:
            return None
        return Instant(base.ms + extra, base.clock_id, base.verified, base.error_ms, base.resolution_ms)

    def in_window(self, inc, t):
        """True/False when decidable; None when the clocks cannot be compared."""
        if t is None or inc["t_req"] is None or not t.comparable(inc["t_req"]):
            return None
        if t.ms < inc["t_req"].ms - self.f01["eps_s"] * 1000:
            return False
        end = self.incident_end(inc)
        if end is None or not t.comparable(end):
            return True
        return t.ms <= end.ms

    def window_candidates(self, event):
        if self.f01 is None:
            return []
        t = self.stamp_of(event)
        out = []
        for inc in self.inc.values():
            if inc["trial"] != event.get("trial_id") or inc["t_req"] is None or t is None:
                continue
            status, t_eff, w_eff = self.effect_cache(inc)
            end = self.window_end(inc, t_eff, w_eff)
            if end is None or not t.comparable(inc["t_req"]) or not t.comparable(end):
                continue
            if inc["t_req"].ms - self.f01["eps_s"] * 1000 <= t.ms <= end.ms:
                out.append(inc["id"])
        return out

    def effect_cache(self, inc):
        if "effect_result" not in inc:
            inc["effect_result"] = self.effect(inc)
        return inc["effect_result"]

    def orphan_in_window(self, event):
        """A mandatory-type ORPHAN inside an incident window makes it MISSING, not MISSED (6.3)."""
        if self.f01 is None:
            return
        for inc in self.inc.values():
            if event.get("trial_id") not in (None, inc["trial"]):
                continue
            t = self.at(inc["trial"], event["clock"]["clock_id"], event["ts_event"])
            if self.in_window(inc, t) is not False:
                inc["missing"].add("ORPHAN_IN_WINDOW")

    def attach(self, inc, event):
        typ = event["event_type"]
        if typ == "DETECTED":
            service = (event.get("target") or {}).get("service")
            # A lost request's targets are unknown: its alerts are never called a target mismatch.
            (inc["detected"] if service in inc["targets"] or inc.get("targets_unknown") else inc["mismatched"]).append(event)
        elif typ == "DECISION":
            inc["decisions"].append(event)
        elif typ == "LLM_CALL":
            inc["calls"].append(event)
        elif typ == "GUARD_VERDICT":
            inc.setdefault("guards", []).append(event)
        else:
            inc["actions"].setdefault(event["action_id"], {}).setdefault(typ, []).append(event)

    # ----------------------------------------------------------------- invalid relatedness (6.4)
    def invalid_related(self):
        for kind, event in self.invalid:
            typ = event.get("event_type") if isinstance(event, dict) else None
            if typ not in MANDATORY and typ not in {"RECOVERY_VERIFIED", "RELAPSE"}:
                continue
            for inc in self.inc.values():
                if typ in {"RECOVERY_VERIFIED", "RELAPSE"}:
                    if event.get("incident_id") == inc["id"]:
                        inc["rv_invalid"] = inc.get("rv_invalid", 0) + 1
                    continue
                if self.related(inc, event, typ):
                    inc["missing"].add("INVALID_EVENT")
                    if typ == "ACTION_COMPLETED":
                        inc["flags"].add("ACTION_TERMINAL_MISSING")

    def related(self, inc, event, typ):
        if event.get("incident_id") == inc["id"]:
            return True
        if event.get("trial_id") not in (None, inc["trial"]) or inc["t_req"] is None or self.f01 is None:
            return False
        eps = self.f01["eps_s"] * 1000
        if typ == "PROBE_SAMPLE":
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            if payload.get("flow") not in (None, inc["flow"]):
                return False
            text = payload.get("t_start") if ms(payload.get("t_start")) is not None else event.get("ts_event")
            clock = (event.get("clock") or {}).get("clock_id")
            t = self.at(inc["trial"], clock, text) if isinstance(text, str) else None
            # Unreadable time: cannot be placed outside the incident, so it is related.
            return t is None or not t.comparable(inc["t_req"]) or t.ms >= inc["t_req"].ms - eps
        try:
            t = self.at(inc["trial"], event["clock"]["clock_id"], event["ts_event"])
        except (KeyError, TypeError):
            t = None
        # An invalid event that cannot be placed in time cannot be placed outside the incident either.
        return self.in_window(inc, t) is not False

    # ----------------------------------------------------------------- mode (7.4)
    def mode(self):
        group = self.group
        bad = {}
        events = [e for e in self.used if e["event_type"] in ZD_ACTIONS]
        decisions = {e["decision_id"]: e for e in events if e["event_type"] == "DECISION"}
        for event in events:
            why = None
            if group == "B0":
                why = "ZERO DOOR decision/action in B0"
            elif event["event_type"] == "DECISION":
                fallback = group in ("B2", "B3") and event["source_component"] == "decision_rules" and event["payload"]["fallback"]
                if event["source_component"] not in DECIDERS.get(group, set()) and not fallback:
                    why = "decision source not allowed for group"
            elif event["event_type"] == "LLM_CALL" and event["source_component"] not in LLM_SOURCES.get(group, set()):
                why = "LLM_CALL not allowed for group"
            elif event["event_type"] == "HEAL_STARTED":
                want = "OPERATOR" if group == "BM" else "AUTO"
                d = decisions.get(event["decision_id"])
                if event["payload"]["initiator"] != want:
                    why = "initiator not allowed for group"
                elif d is None or d["payload"]["stage"] != "PROPOSAL" or d["payload"]["response_kind"] != "ACTION":
                    why = "action without a known PROPOSAL/ACTION decision"
            if why:
                bad.setdefault(event.get("trial_id"), []).append(why)
        for eid in self.findings["mode_violations"]:
            event = next((e for e in self.used if e["event_id"] == eid), None)
            if event:
                bad.setdefault(event.get("trial_id"), []).append("group differs or validator MODE_VIOLATION")
        for event in self.findings["quarantined_mode_violations"]:
            bad.setdefault(event.get("trial_id"), []).append("quarantined MODE_VIOLATION " + str(event.get("event_type")))
        self.mode_findings = {k: sorted(set(v)) for k, v in bad.items()}
        for inc in self.inc.values():
            if inc["trial"] in self.mode_findings or (None in self.mode_findings):
                inc["missing"].add("MODE_VIOLATION")

    # ----------------------------------------------------------------- per incident
    def score_incident(self, inc):
        f = self.f01
        eps = f["eps_s"] * 1000 if f else 0
        r = {"incident_id": inc["id"], "trial_id": inc["trial"], "flow": inc["flow"], "variant_ref": inc["req"]["payload"].get("variant_ref")}
        status, t_eff, w_eff = self.effect_cache(inc) if f else ("UNKNOWN_EFFECT", None, None)
        r["effect"] = status
        flags, missing = inc["flags"], inc["missing"]
        if inc["mismatched"]:
            flags.add("TARGET_MISMATCH")
        # A milestone that cannot be built (no trial clock model, unreadable time) is unknown, never absent:
        # it is kept out of every sort/min and makes what depends on it MISSING (FX01-R3).
        stops = [self.stamp_of(e) for e in inc["stop"]]
        stop_unknown = any(s is None for s in stops) or any(not stops[0].comparable(s) for s in stops if s is not None)
        t_stop = None if stop_unknown or not stops else min(stops, key=lambda i: i.ms)
        if stop_unknown:
            flags.add("STOP_CLOCK_UNVERIFIED")
        r["t_stop_status"] = "CLOCK_UNVERIFIED" if stop_unknown else ("OBSERVED" if t_stop is not None else "NONE")
        # detect
        upper = self.window_end(inc, t_eff, w_eff) if f else None
        dets, unplaced = [], []
        for event in inc["detected"]:
            t = self.stamp_of(event)
            if t is None or inc["t_req"] is None or not t.comparable(inc["t_req"]):
                # The alert exists but its order against T_req/T_eff is unknown (contract 4.3): T_det is
                # MISSING, never "not detected". A comparable alert does not settle it either, since this
                # one may be earlier.
                unplaced.append(event["event_id"])
                continue
            if t.ms < inc["t_req"].ms - eps:
                continue  # alert firing before T_req - eps belongs to no incident
            if upper is not None and t.comparable(upper) and t.ms > upper.ms:
                continue
            dets.append((t, event))
        dets.sort(key=lambda x: x[0].ms)
        det_unknown = bool(unplaced)
        D = dets[0][0] if dets and not det_unknown else None
        if det_unknown:
            flags.add("DETECT_CLOCK_UNVERIFIED")
        r["t_det_status"] = "CLOCK_UNVERIFIED" if det_unknown else ("OBSERVED" if D is not None else "NONE")
        inc["t_det"], inc["det_unknown"] = D, det_unknown
        if inc["mismatched"] and not dets and not det_unknown:
            missing.add("TARGET_MISMATCH")
        # clock chain (INVALID_CLOCK)
        alerts = {e["event_id"]: e for e in inc["detected"] + inc["mismatched"]}
        heal = {aid: a for aid, a in inc["actions"].items()}

        def later(a, b):
            return a is not None and b is not None and a.comparable(b) and a.ms > b.ms + eps
        for d in inc["decisions"]:
            for item in d["payload"]["inputs"]:
                alert = alerts.get(item["event_id"])
                t_con = self.at(d.get("trial_id"), d["clock"]["clock_id"], item["received_at"])
                if alert:
                    t_det, t_pub = self.stamp_of(alert), self.stamp_of(alert, envelope_field="ts_publish") or self.stamp_of(alert)
                    if later(t_det, t_pub) or later(t_pub, t_con):
                        missing.add("INVALID_CLOCK")
                for a in heal.values():
                    for hs in a.get("HEAL_STARTED", []):
                        if hs["decision_id"] == d["decision_id"] and later(t_con, self.stamp_of(hs)):
                            missing.add("INVALID_CLOCK")
        for a in heal.values():
            if a.get("API_ACCEPTED") and a.get("ACTION_COMPLETED") and later(self.stamp_of(a["API_ACCEPTED"][0]), self.stamp_of(a["ACTION_COMPLETED"][0])):
                missing.add("INVALID_CLOCK")
        # actions
        r["action_attempts"] = sum(1 for a in heal.values() if a.get("HEAL_STARTED"))
        if any(a.get("HEAL_STARTED") and not a.get("ACTION_COMPLETED") for a in heal.values()):
            flags.add("ACTION_TERMINAL_MISSING")
        if any(len(a.get("HEAL_STARTED", [])) > 1 or len(a.get("ACTION_COMPLETED", [])) > 1 for a in heal.values()):
            missing.add("INTEGRITY_ERROR")
        completed = [c for a in heal.values() for c in a.get("ACTION_COMPLETED", [])]
        success_all = [self.stamp_of(c) for c in completed if c["payload"]["status"] == "SUCCESS"]
        success = sorted((s for s in success_all if s is not None), key=lambda i: i.ms)
        success_unknown = len(success) < len(success_all)  # a SUCCESS that cannot be placed may be the first one
        r["terminal"] = {s: sum(1 for c in completed if c["payload"]["status"] == s) for s in ("SUCCESS", "FAILED", "PARTIAL", "TIMEOUT")}
        # recovery (7.5): D-04 on the probe clock's own readings
        R, rec = None, None
        clock_bad = False
        if f and status == "CONFIRMED" and t_eff is not None:
            stream, probe_clock = self.stream(inc)
            if stream is not None:
                e_local = self.local(inc, t_eff, probe_clock)
                if e_local is None:
                    clock_bad = True
                    flags.add("T_EFF_NOT_ON_PROBE_CLOCK")
                else:
                    result = evaluate(stream, e_local, f["k"], f["s_s"] * 1000, f["gap_s"] * 1000, f["cap_rec_s"] * 1000)
                    rec = result
                    if result["verified"]:
                        R = self.trial[inc["trial"]]["clock"].at(probe_clock, result["verified"]["t_rec"])
                    if result["gap_before"]:
                        flags.add("PROBE_GAP")
                    r["relapses"] = len(result["relapses"])
                    r["recovery_probe"] = "VERIFIED" if result["verified"] else ("TIMEOUT" if result["covered"] and not result["unverifiable"] else "MISSING_PROBE")
                    self.compare_evaluator(inc, r, result, probe_clock)
        # label
        hard = missing & HARD
        if hard:
            label = "MISSING"
        elif status == "UNKNOWN_EFFECT":
            label = "UNKNOWN_EFFECT"
        elif status == "CONFIRMED_NO_EFFECT":
            label = "CONFIRMED_NO_EFFECT"
        elif clock_bad:
            label = "MISSING"
        elif rec is None:
            label = "MISSING_PROBE"
        elif R is not None:
            verified_at = self.trial[inc["trial"]]["clock"].at(R.clock_id, rec["verified"]["recovery_verified_at"])
            if det_unknown:
                label, clock_bad = "MISSING", True  # UNDETECTED/BEFORE_DETECT/RECOVERED all need T_det
            elif D is None:
                label = "RECOVERED_UNDETECTED"
            elif not D.comparable(R):
                label, clock_bad = "MISSING", True
            elif R.ms < D.ms:
                label = "RECOVERED_BEFORE_DETECT"
            elif stop_unknown:
                label, clock_bad = "MISSING", True  # AFTER_STOP or not needs every T_stop
            elif t_stop is not None and not t_stop.comparable(verified_at):
                label, clock_bad = "MISSING", True
            elif t_stop is not None and t_stop.ms < verified_at.ms:
                label = "RECOVERED_AFTER_STOP"
            else:
                label = "RECOVERED"
            if label.startswith("RECOVERED"):
                if not success_unknown and all(s.comparable(R) for s in success):
                    if not any(s.ms < R.ms for s in success):
                        flags.add("NO_ACTION_BEFORE_RECOVERY")
                else:
                    clock_bad = True
        else:
            label = rec and ("TIMEOUT" if rec["covered"] and not rec["unverifiable"] else "MISSING_PROBE")
        # durations (ms, uncertainty ms)
        b0_na = self.group == "B0" and not inc["detected"] and not any(self.of("DETECTED"))
        if b0_na:
            r.update(mttd="N/A", mttr="N/A", reaction="N/A", total=None)
            if R is not None:
                r["total"] = self.put(r, "total", duration(t_eff, R))
        elif hard or status != "CONFIRMED" or t_eff is None:
            # Hard MISSING (incl. INVALID_CLOCK) and every non-CONFIRMED effect: no duration at all.
            r.update(mttd="MISSING", mttr="MISSING", reaction="MISSING", total=None)
            if label == "CONFIRMED_NO_EFFECT":
                r.update(mttd="OUT_NO_EFFECT", mttr="OUT_NO_EFFECT", reaction="OUT_NO_EFFECT")
        else:
            if det_unknown:
                flags.add("CLOCK_UNVERIFIED")
                r["mttd"], r["reaction"] = "MISSING", "MISSING"
            elif D is None:
                r["mttd"], r["reaction"] = "MISSED", "NO_DETECT"
            else:
                d = duration(t_eff, D)
                if d is None:
                    clock_bad, r["mttd"] = True, "MISSING"
                else:
                    if d[0] < 0:
                        flags.add("EARLY_DETECT")
                    r["mttd"] = self.put(r, "mttd", (max(0.0, d[0]), d[1]))
                cap_base = t_eff if t_eff is not None and t_eff.comparable(D) else inc["t_req"]
                if cap_base is not t_eff:
                    flags.add("REACTION_CAP_FROM_T_REQ")
                placed = [s for s in success if s.comparable(D) and s.comparable(cap_base)]
                ok = [s for s in placed if s.ms >= D.ms and s.ms <= cap_base.ms + f["cap_rec_s"] * 1000]
                if len(placed) < len(success) or success_unknown:
                    # A SUCCESS on an unverified executor clock may be the first one: reaction unknown, not NO_SUCCESS.
                    flags.update({"CLOCK_UNVERIFIED", "ACTION_CLOCK_UNVERIFIED"})
                    r["reaction"] = "MISSING"
                else:
                    r["reaction"] = self.put(r, "reaction", duration(D, ok[0])) if ok else "NO_SUCCESS"
            if det_unknown:
                r["mttr"] = "MISSING"
            elif R is not None and D is not None:
                d = duration(D, R)
                if d is None:
                    clock_bad, r["mttr"] = True, "MISSING"
                else:
                    r["mttr"] = self.put(r, "mttr", d) if d[0] >= 0 else None
            else:
                r["mttr"] = None
            r["total"] = self.put(r, "total", duration(t_eff, R)) if R is not None and t_eff is not None else None
        if clock_bad:
            flags.add("CLOCK_UNVERIFIED")
            if label and label.startswith("RECOVERED"):
                label = "MISSING"
            if label == "MISSING" and r.get("mttd") is None:
                r.update(mttd="MISSING", mttr="MISSING")
        r["label"] = label or "MISSING_PROBE"
        r["missing_reasons"] = sorted(missing)
        r["flags"] = sorted(flags)
        r["milestones"] = {k: (None if v is None else {"t_ms": round(v.ms, 3), "clock_id": v.clock_id, "verified": v.verified})
                           for k, v in (("t_req", inc["t_req"]), ("t_eff", t_eff), ("t_det", D), ("t_rec", R), ("t_stop", t_stop))}
        r["clock_state"] = {cid: self.trial[inc["trial"]]["clock"].state(cid)[1] for cid in sorted(self.trial[inc["trial"]]["clock"].meta)} if inc["trial"] in self.trial else {}
        return r

    @staticmethod
    def put(r, name, d):
        if d is None:
            return "MISSING"
        r.setdefault("uncertainty_ms", {})[name] = d[1]
        return round(d[0] / 1000, 3)

    def compare_evaluator(self, inc, r, result, probe_clock):
        """Recompute vs RECOVERY_VERIFIED/RELAPSE on every field; differences are EVALUATOR_MISMATCH."""
        issues = []
        v = result["verified"]
        model = self.trial[inc["trial"]]["clock"]
        for event in inc["rv"]:
            p = event["payload"]
            if v is None:
                issues.append("RECOVERY_VERIFIED_WITHOUT_RECOMPUTED_RECOVERY")
                continue
            if p["evidence_clock_id"] != probe_clock:
                issues.append("evidence_clock_id")
            for field, value in (("t_rec", v["t_rec"]), ("recovery_verified_at", v["recovery_verified_at"]),
                                 ("evidence_complete_at", v["evidence_complete_at"])):
                if ms(p[field]) != math.floor(value):
                    issues.append(field)
            if p["sample_seq_range"] != v["sample_seq_range"]:
                issues.append("sample_seq_range")
            if p["samples_sha256"] != samples_sha256(v["event_ids"]):
                issues.append("samples_sha256")
            if [p["flow"]] != v["flows"] or [p["probe_id"]] != v["probe_ids"] or [p["probe_version"]] != v["probe_versions"]:
                issues.append("provenance")
            for key in ("k", "s_s", "delta_s", "l_ms", "gap_s", "cap_rec_s"):
                if p[key] != self.f01[key]:
                    issues.append("params." + key)
            published = self.stamp_of(event)
            done = model.at(probe_clock, v["evidence_complete_at"])
            if published is None or not published.comparable(done):
                issues.append("publication_time_not_comparable")
            elif published.ms < done.ms:
                issues.append("published_before_evidence_complete")
        if v is not None and not inc["rv"]:
            issues.append("RECOVERY_VERIFIED_ABSENT")
        issues += ["RECOVERY_VERIFIED_OR_RELAPSE_INVALID"] * inc.get("rv_invalid", 0)
        expected = sorted(math.floor(x["candidate_t_rec"]) for x in result["relapses"])
        seen = sorted(ms(e["payload"]["candidate_t_rec"]) for e in inc["relapse"])
        if expected != seen:
            issues.append("relapse")
        r["evaluator_mismatch"] = bool(issues)
        r["evaluator_issues"] = sorted(set(issues))
        if issues:
            inc["flags"].add("EVALUATOR_MISMATCH")

    # ----------------------------------------------------------------- leak (8.3)
    def leak(self):
        out = {}
        for trial in sorted(self.trial):
            h = [e for p, e in self.events if p == "H" and e.get("trial_id") in (trial, None)]
            o = [e for p, e in self.events if p == "O" and e.get("trial_id") == trial]
            result = audit(h, o, surfaces=self.options.get("surfaces", {}).get(trial, ()), access_complete=False)
            leaked = [e.get("event_id") for e in self.findings["quarantined_leaks"] if e.get("trial_id") == trial]
            if leaked:
                result = dict(result, result="LEAK_DETECTED", findings=sorted(set(result["findings"]) | {"QUARANTINED_O_LEAK"}))
            out[trial] = result
        return out

    def run(self):
        self.intake()
        self.classify()
        self.trials()
        self.incidents()
        if self.f01 is not None:
            for inc in self.inc.values():
                self.effect_cache(inc)
        self.cross_run()
        self.link()
        self.cardinality()
        for event in self.h_orphans:
            self.orphan_in_window(event)
        self.invalid_related()
        self.mode()
        for event_id in self.findings["integrity_errors"]:
            self.integrity_by_id(event_id)
        for event in self.findings["quarantined_link_conflicts"]:
            ids = {inc["id"] for inc in self.inc.values() if event.get("incident_id") == inc["id"] or
                   (event.get("trial_id") == inc["trial"] and self.f01 is not None and
                    self.in_window(inc, self.at(inc["trial"], (event.get("clock") or {}).get("clock_id"), event.get("ts_event"))) is not False)}
            self.conflict(ids, event, "quarantined by the gateway as LINK_CONFLICT")
        incidents = [self.score_incident(inc) for inc in sorted(self.inc.values(), key=lambda i: (i["trial"], i["id"]))]
        return {"run_id": self.h.run_id, "group": self.group, "f01": self.f01, "reference_clock_id": self.reference,
                "incidents": incidents, "findings": self.findings, "run_flags": sorted(self.flags), "cohort": self.cohort,
                "mode_findings": self.mode_findings, "leak": self.leak()}

    def cross_run(self):
        """LINK_CONFLICT for events of other runs that name this run's incidents or trials (6.3)."""
        if not self.others:
            self.flags.add("CROSS_RUN_LINKS_UNCHECKED")
            return
        for export in self.others:
            if export.run_id == self.h.run_id:
                continue
            for record in export.records + export.rejections + export.late:
                event = record.get("envelope")
                if not isinstance(event, dict):
                    continue
                hit = {i for i in self.inc if event.get("incident_id") == i} | \
                      {i for i, inc in self.inc.items() if event.get("trial_id") is not None and event.get("trial_id") == inc["trial"]}
                if hit:
                    self.findings["foreign_references"].append({"run_id": export.run_id, "event_id": event.get("event_id")})
                    self.conflict(hit, event, "event of another run names this run's incident/trial")

    def integrity_by_id(self, event_id):
        """A conflicting event_id anywhere in a trial makes that trial's incidents MISSING when the
        conflicting copies cannot be placed (contract 6.1: INTEGRITY_ERROR -> incident MISSING)."""
        holders = [e for _, e in self.events if e.get("event_id") == event_id] + \
                  [e for _, e in self.invalid if isinstance(e, dict) and e.get("event_id") == event_id]
        for event in holders:
            for inc in self.inc.values():
                if event.get("incident_id") == inc["id"] or (event.get("trial_id") == inc["trial"] and event.get("event_type") in MANDATORY):
                    inc["missing"].add("INTEGRITY_ERROR")
