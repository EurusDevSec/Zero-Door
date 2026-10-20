"""SYNTHETIC zd-event/1.0.0 traces for ZER-10 tests, sealed and exported through the real ZER-9 Archive.

Times are seconds from T0 = 2026-10-19T06:00:00.000Z, as in contract section 10. A probe clock can
carry an offset/drift: its readings are true time + offset(true). Expected values are written by hand
in expected.json; nothing here calls the production scorer or recovery code.
"""
import copy
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import new_id  # noqa: E402
from event_pipeline.store import Archive, Rejected  # noqa: E402

T0 = datetime(2026, 10, 19, 6, 0, 0, tzinfo=timezone.utc)
HOST = {"clock_id": "clk_host_lab", "clock_source": "HOST_SHARED", "resolution_ms": 1}
PROBE = {"clock_id": "clk_probe_ext", "clock_source": "OFF_HOST", "resolution_ms": 16}
# Illustrative ZER-32 3.6 values (not locked formal parameters).
F01 = {"delta_s": 1, "k": 3, "s_s": 30, "l_ms": 2000, "gap_s": 2, "eps_s": 1, "cap_det_s": 300, "cap_rec_s": 600}
STREAMS = {"PROBE_SAMPLE": "h.probe", "PROBE_HEARTBEAT": "h.probe", "CLOCK_SYNC": "h.probe",
           "EFFECT_EVALUATED": "h.eval", "RECOVERY_VERIFIED": "h.eval", "RELAPSE": "h.eval", "CONTAINMENT_VERIFIED": "h.eval",
           "DETECTED": "o.alert", "DECISION": "o.decision", "LLM_CALL": "o.decision", "GUARD_VERDICT": "o.decision",
           "HEAL_STARTED": "o.action", "API_ACCEPTED": "o.action", "ACTION_COMPLETED": "o.action",
           "RUN_CONTEXT": "o.context", "TRIAL_CONTEXT": "o.context"}
WITH_INCIDENT = {"ATTACK_REQUESTED", "ATTACK_STOPPED", "FAULT_EXECUTOR_RESULT", "EFFECT_EVALUATED", "RELAPSE",
                 "RECOVERY_VERIFIED", "CONTAINMENT_VERIFIED", "TRIAL_CONTEXT", "DETECTED", "DECISION", "LLM_CALL",
                 "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
INSTANCES = {"harness": "hrn-0", "probe": "prb-0", "effect_evaluator": "eff-0", "recovery_evaluator": "rec-0",
             "detector": "det-0", "decision_llm": "llm-0", "decision_rules": "rul-0", "decision_single_llm": "sgl-0",
             "operator_console": "opc-0", "guard": "grd-0", "executor": "exe-0", "fault_executor": "flt-0"}


def iso(seconds):
    whole = int(round(seconds * 1000))
    return (T0 + timedelta(milliseconds=whole)).strftime("%Y-%m-%dT%H:%M:%S.") + f"{whole % 1000:03d}Z"


def sha_list(event_ids):
    """Hand oracle for samples_sha256: SHA-256 of the canonical JSON list (contract 7.5 step 6)."""
    return "sha256:" + hashlib.sha256(json.dumps(list(event_ids), separators=(",", ":")).encode()).hexdigest()


class Trace:
    def __init__(self, group="B2", probe_clock=PROBE, f01=F01, offset=None):
        self.group, self.f01 = group, dict(f01)
        self.probe_clock = dict(probe_clock)
        self.offset = offset or (lambda t: 0.0)  # seconds -> ms the probe clock reads ahead of true time
        self.run, self.trial, self.incident = new_id("run"), new_id("trl"), new_id("inc")
        self.events, self.late, self.seq = [], [], {}
        self.samples = {}  # true t -> event
        self.config_ref = "sha256:" + "0" * 64

    def local(self, t):
        return t + self.offset(t) / 1000

    def env(self, typ, plane, source, t, payload, clock=None, trial=True, incident=True, publish=None, **ids):
        clock = clock or HOST
        stream = STREAMS.get(typ, "h.control")
        instance = INSTANCES[source]
        key = (instance, stream)
        self.seq[key] = self.seq.get(key, -1) + 1
        event = {"schema_version": "zd-event/1.0.0", "event_id": new_id("evt"), "event_type": typ, "plane": plane,
                 "run_id": self.run, "trial_id": self.trial if trial is True else trial, "causation_id": None,
                 "group": self.group, "method_version": "zer32-acc+f01-illustrative", "config_ref": self.config_ref,
                 "source_component": source, "source_instance": instance, "producer_version": "synthetic",
                 "stream": stream, "seq": self.seq[key], "target": None, "clock": copy.deepcopy(clock),
                 "ts_event": iso(t), "payload": payload}
        if typ in WITH_INCIDENT and incident:
            event["incident_id"] = self.incident if incident is True else incident
        if publish is not None:
            event["ts_publish"] = iso(publish)
        event.update(ids)
        self.events.append((plane, event))
        return event

    # -------------------------------------------------------------- harness / H
    def run_started(self, t=0):
        self.env("RUN_STARTED", "H", "harness", t, {"canary_token": "cnry-" + new_id("evt")[4:], "protocol_ref": "synthetic",
                                                    "schedule_ref": "sha256:" + "1" * 64, "f01_params": self.f01,
                                                    "reference_clock_id": HOST["clock_id"]}, trial=None, incident=False)
        self.env("RUN_CONTEXT", "O", "harness", t, {}, trial=None, incident=False)

    def trial_started(self, t=10, warmup=22, probes=None, end=300):
        probes = probes if probes is not None else [{"probe_id": "prb-0", "flow": "checkout", "probe_version": "p0",
                                                     "clock_id": self.probe_clock["clock_id"]}]
        self.env("TRIAL_STARTED", "H", "harness", t, {"warmup_end": None if warmup is None else iso(warmup),
                                                      "planned_window": {"start": iso(t), "end": iso(end)}, "probes": probes})
        self.env("TRIAL_CONTEXT", "O", "harness", t, {})

    def manifest(self, t=10):
        self.env("HARNESS_MANIFEST", "H", "harness", t, {"manifest_version": "m0", "allowlist_version": "a0",
                                                         "reveal_terms": ["stress"], "entries": []})

    def ground_truth(self, variant="var-a", case_class="C4", acceptable=("SCALE_UP",), constraints=None, required=True):
        self.env("GROUND_TRUTH_LOCKED", "H", "harness", 1, {
            "variant_id": variant, "case_class": case_class, "cause": "cpu", "decision_required": required,
            "acceptable_actions": list(acceptable), "constraints": constraints or {"SCALE_UP": {"max_replicas": 4}},
            "label_version": "l0", "reviewers": ["synthetic"], "locked_at": iso(1)}, trial=None, incident=False)

    def sync(self, t, offset_ms=None, uncertainty=20, clock_id=None):
        offset_ms = self.offset(t) if offset_ms is None else offset_ms
        self.env("CLOCK_SYNC", "H", "probe", self.local(t), {
            "clock_id": clock_id or self.probe_clock["clock_id"], "reference_clock_id": HOST["clock_id"],
            "offset_ms": offset_ms, "uncertainty_ms": uncertainty, "method": "synthetic", "measured_at": iso(t)},
            clock=self.probe_clock)

    def attack(self, t=100, targets=("frontend",), flow="checkout", variant="var-a", s_att=None, known_good=None):
        self.env("ATTACK_REQUESTED", "H", "harness", t, {
            "variant_ref": variant, "fault_params": {}, "attack_command": {}, "seed": 7, "onset_offset_ms": 0,
            "s_att": s_att, "known_good_revision": known_good, "target_services": list(targets)},
            target={"namespace": "target-app", "service": targets[0], "flow": flow})

    def stop(self, t=240):
        self.env("ATTACK_STOPPED", "H", "harness", t, {"stop_reason": "PLANNED", "executor_confirmed": True})

    def effect(self, t=160, status="CONFIRMED", t_eff=101, w_eff=300, flow="checkout", criteria="c0"):
        self.env("EFFECT_EVALUATED", "H", "effect_evaluator", t, {
            "status": status, "t_eff": None if t_eff is None else iso(self.local(t_eff)),
            "evidence_clock_id": self.probe_clock["clock_id"], "criteria_version": criteria, "w_eff_s": w_eff,
            "evidence": {"flow": flow, "first_sample_t": None, "last_sample_t": None, "max_gap_s": None, "sample_seq_range": None},
            "reason": "synthetic"})

    def probe_run(self, pattern, latency_ms=250, end_s=0.25, probe_id="prb-0", version="p0", flow="checkout", start_seq=0, skip=()):
        """pattern: list of (from_s, to_s, ok) inclusive at 1 s; `skip` drops true times (gaps)."""
        seq = start_seq
        for start, end, ok in pattern:
            t = start
            while t <= end + 1e-9:
                if t not in skip:
                    self.sample(t, ok, seq, latency_ms, end_s, probe_id, version, flow)
                    seq += 1
                t = round(t + 1, 3)
        return seq

    def sample(self, t, ok, seq, latency_ms=250, end_s=0.25, probe_id="prb-0", version="p0", flow="checkout", error=None):
        payload = {"probe_id": probe_id, "flow": flow, "sequence": seq, "t_start": iso(self.local(t)),
                   "t_end": iso(self.local(t) + end_s), "pass": ok, "error_class": None if ok else (error or "CONTENT"),
                   "latency_ms": latency_ms, "probe_version": version}
        event = self.env("PROBE_SAMPLE", "H", "probe", self.local(t) + end_s, payload, clock=self.probe_clock,
                         target={"namespace": "target-app", "service": "frontend", "flow": flow})
        self.samples.setdefault(t, event)
        return event

    def recovery_verified(self, t, t_rec, first, last, emit_at=None, **override):
        ids = [self.samples[x]["event_id"] for x in sorted(self.samples) if first <= x <= last]
        payload = {"flow": "checkout", "probe_id": "prb-0", "probe_version": "p0", "evidence_clock_id": self.probe_clock["clock_id"],
                   "t_rec": iso(self.local(t_rec)), "recovery_verified_at": iso(self.local(t_rec) + self.f01["s_s"]),
                   "evidence_complete_at": iso(self.local(last) + 0.25), "k": self.f01["k"], "s_s": self.f01["s_s"],
                   "delta_s": self.f01["delta_s"], "l_ms": self.f01["l_ms"], "gap_s": self.f01["gap_s"],
                   "cap_rec_s": self.f01["cap_rec_s"],
                   "sample_seq_range": [self.samples[first]["payload"]["sequence"], self.samples[last]["payload"]["sequence"]],
                   "samples_sha256": sha_list(ids), "rule_version": "zer32-d04"}
        payload.update(override)
        return self.env("RECOVERY_VERIFIED", "H", "recovery_evaluator", self.local(emit_at if emit_at is not None else t), payload,
                        clock=self.probe_clock, target={"namespace": "target-app", "service": "frontend", "flow": "checkout"})

    def relapse(self, t, candidate, failing):
        return self.env("RELAPSE", "H", "recovery_evaluator", self.local(t), {
            "flow": "checkout", "candidate_t_rec": iso(self.local(candidate)), "failing_sample_t": iso(self.local(failing)),
            "rule_version": "zer32-d04"}, clock=self.probe_clock)

    def trial_ended(self, t=300):
        self.env("TRIAL_ENDED", "H", "harness", t, {"end_reason": "PLANNED"})

    # -------------------------------------------------------------- O chain
    def detected(self, t=131, service="frontend", publish=None, **kw):
        return self.env("DETECTED", "O", "detector", t, {
            "rule_id": "cpu_limit_ratio", "rule_version": "r1", "signature": "cpu_limit_ratio/" + service,
            "metric": "cpu_usage_ratio_of_limit", "value": 0.93, "threshold": 0.8, "severity": "WARNING",
            "description": "CPU usage above limit ratio"}, publish=publish if publish is not None else t + 0.2,
            target={"namespace": "target-app", "service": service, "flow": None}, alert_id=new_id("alt"), **kw)

    def decision(self, t, alert, received=None, kind="ACTION", action="SCALE_UP", params=None, source=None,
                 fallback_of=None, stage="PROPOSAL", **kw):
        source = source or {"B1": "decision_rules", "B2": "decision_llm", "B3": "decision_single_llm", "BM": "operator_console"}.get(self.group, "decision_rules")
        decision_source = {"decision_rules": "RULES", "decision_llm": "LLM", "decision_single_llm": "SINGLE_LLM", "operator_console": "MANUAL"}[source]
        llm = decision_source in ("LLM", "SINGLE_LLM")
        return self.env("DECISION", "O", source, t, {
            "stage": stage, "decision_source": decision_source,
            "inputs": [{"event_id": alert["event_id"], "received_at": iso(received if received is not None else t - 1.6)}],
            "response_kind": kind, "proposal": {"action_type": action, "params": params or {"service": "frontend", "replicas": 2}} if kind == "ACTION" else None,
            "fallback": fallback_of is not None, "fallback_of": fallback_of, "prompt_version": "p1" if llm else None,
            "prompt_sha256": "sha256:" + "2" * 64 if llm else None, "evidence_package_version": "o-envelope/1.0.0"},
            decision_id=new_id("dec"), causation_id=alert["event_id"], **kw)

    def llm_call(self, t, decision, attempt=1, usage=(1000, 100), usd=0.01, outcome="OK", retry_reason=None, call_id=None):
        source = decision["source_component"]
        return self.env("LLM_CALL", "O", source, t, {
            "attempt_no": attempt, "retry_reason": retry_reason, "provider": "synthetic", "model": "model-x",
            "prompt_version": "p1", "prompt_sha256": "sha256:" + "2" * 64, "latency_ms": 900, "outcome": outcome,
            "usage": {"input_tokens": usage[0], "output_tokens": usage[1], "status": "COMPLETE"} if usage else
                     {"input_tokens": None, "output_tokens": None, "status": "MISSING"},
            "cost": {"usd": usd, "status": "COMPLETE", "price_ref": "price-table-synthetic"} if usd is not None else
                    {"usd": None, "status": "MISSING", "price_ref": None}},
            decision_id=decision["decision_id"], call_id=call_id or new_id("cal"))

    def guard(self, t, decision, verdict="ACCEPT"):
        return self.env("GUARD_VERDICT", "O", "guard", t, {"verdict": verdict, "reason_code": "R0", "guard_version": "g0"},
                        decision_id=decision["decision_id"], causation_id=decision["event_id"])

    def action(self, decision, started=133.5, api=134, done=150, status="SUCCESS", attempt=1, retry_of=None, with_decision_on_terminal=True):
        aid = new_id("act")
        initiator = "OPERATOR" if self.group == "BM" else "AUTO"
        hs = self.env("HEAL_STARTED", "O", "executor", started, {"action_type": "SCALE_UP", "params": {"service": "frontend"},
                                                                 "attempt_no": attempt, "retry_of": retry_of, "initiator": initiator},
                      decision_id=decision["decision_id"], action_id=aid, causation_id=decision["event_id"])
        extra = {"decision_id": decision["decision_id"]} if with_decision_on_terminal else {}
        if api is not None:
            self.env("API_ACCEPTED", "O", "executor", api, {"api": "apps/v1 scale", "response_ref": "r"}, action_id=aid, **extra)
        if done is not None:
            ok = status == "SUCCESS"
            self.env("ACTION_COMPLETED", "O", "executor", done, {
                "status": status, "postcondition": {"name": "replicas_ready", "checked": True, "satisfied": ok, "observed": "x"},
                "error": None if ok else "synthetic"}, action_id=aid, **extra)
        return hs

    # -------------------------------------------------------------- seal and export
    def seal(self, root, order=None, after_seal=()):
        """Ingest through Archive (rejections are real quarantine), seal, ingest late, export."""
        root = Path(root)
        planes = {"H": Archive(root / "archive-h", "H"), "O": Archive(root / "archive-o", "O")}
        rejected = []
        try:
            for plane, event in (order or self.events):
                try:
                    planes[plane].ingest(event, {"kind": "file"}, event.get("source_component"))
                except Rejected as error:
                    rejected.append((event.get("event_type"), error.classification))
            for archive in planes.values():
                archive.run_dir(self.run)
                archive.seal(self.run)
            for plane, event in after_seal:
                try:
                    planes[plane].ingest(event, {"kind": "file"}, event.get("source_component"))
                except Rejected as error:
                    rejected.append((event.get("event_type"), error.classification))
            planes["H"].export(self.run, root / "export-h")
            planes["O"].export(self.run, root / "export-o")
        finally:
            for archive in planes.values():
                archive.close()
        return root / "export-h", root / "export-o", rejected


def e01(group="B2", offset=None, syncs=((10, None, 20), (300, None, 20)), probe_clock=PROBE, detect=131,
        rv=True, action_status="SUCCESS", stop=240, pattern=None):
    """Contract 10.1 E01: effect 101, detect 131, SUCCESS 150, T_rec 191, stop 240."""
    tr = Trace(group, probe_clock=probe_clock, offset=offset)
    tr.run_started()
    tr.ground_truth()
    tr.trial_started()
    tr.manifest()
    for t, off, unc in syncs:
        tr.sync(t, off, unc)
    tr.probe_run(pattern or [(20, 100, True), (101, 188, False), (189, 260, True)])
    tr.attack()
    if detect is not None:
        alert = tr.detected(detect)
        dec = tr.decision(133, alert, received=131.4)
        tr.llm_call(132.9, dec)
        tr.guard(133.1, dec)
        if action_status is not None:
            tr.action(dec, status=action_status)
    tr.effect()
    if rv:
        tr.recovery_verified(222, 191, 189, 221)
    if stop is not None:
        tr.stop(stop)
    tr.trial_ended()
    return tr
