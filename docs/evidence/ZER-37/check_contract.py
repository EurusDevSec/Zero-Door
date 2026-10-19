"""ZER-37 offline design check for docs/design/r1-event-contract.md (SYNTHETIC data only).

Revision 2, after Codex review RV37-01..05. Revision 1 is kept unchanged in scratch/zer37/v1/.
Not a runtime validator, not the ZER-10 scorer and not proof that any producer follows the contract.
It builds envelopes from docs/evidence/ZER-37/fixtures.json, applies the contract rules of sections 4-8 and
compares with hand-computed expectations. Standard library only; no network, lab, API or Kafka.
IDs are UUIDv4-shaped values derived from a hash of the case name so the fixtures are reproducible;
that generator is test data only and must not be used at runtime (contract section 3.1).

Functions used by scratch/zer37/codex-review-probes.py keep their v1 signatures:
FIX, P, iso, sec, gid, canon, build(case_id, spec) -> (recs, prompts, meta),
validate(e) -> (errors, source_ok), analyse(recs, prompts) -> dict.

Usage from the repo root (Git Bash):
  python -I -B docs/evidence/ZER-37/check_contract.py            # control + mutants; portable evidence, no local package hashes
  python -I -B docs/evidence/ZER-37/check_contract.py cases      # control only, per-case detail
"""
import copy, hashlib, json, os, re, sys, uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = str(Path(__file__).resolve().parents[3])
os.chdir(ROOT)
DOC = "docs/design/r1-event-contract.md"
NOTE = "docs/delivery/milestones/R1-measurement/event-contract.md"
NOW = "docs/delivery/NOW.md"
FIX = json.load(open("scratch/zer37/fixtures.json", encoding="utf-8"))
P = FIX["meta"]["params"]
SCHEMA = "zd-event/1.0.0"
T0 = datetime(2026, 10, 19, 6, 0, 0, tzinfo=timezone.utc)
TS_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
ID_RE = {k: re.compile(rf"^{k}_[0-9a-f]{{12}}4[0-9a-f]{{3}}[89ab][0-9a-f]{{15}}$")
         for k in ("run", "trl", "inc", "evt", "alt", "dec", "act", "cal", "ing")}
ID_FIELDS = {"event_id": "evt", "run_id": "run", "trial_id": "trl", "incident_id": "inc", "alert_id": "alt",
             "decision_id": "dec", "action_id": "act", "call_id": "cal", "causation_id": "evt"}
ENV_REQUIRED = ["schema_version", "event_id", "event_type", "plane", "run_id", "group", "method_version",
                "config_ref", "source_component", "source_instance", "producer_version", "stream", "seq",
                "clock", "ts_event", "payload"]
# event_type -> (plane, allowed source_component)  [contract section 5.2]
TYPES = {
    "RUN_STARTED": ("H", {"harness"}), "RUN_CLOSED": ("H", {"harness"}), "RUN_CONTEXT": ("O", {"harness"}),
    "TRIAL_STARTED": ("H", {"harness"}), "TRIAL_ENDED": ("H", {"harness"}), "TRIAL_CONTEXT": ("O", {"harness"}),
    "HARNESS_MANIFEST": ("H", {"harness"}),
    "GROUND_TRUTH_LOCKED": ("H", {"harness"}), "SCHEDULE_SEALED": ("H", {"harness"}),
    "SCHEDULE_ACCESS": ("H", {"harness"}), "AUDIT_COVERAGE": ("H", {"harness"}),
    "CLOCK_SYNC": ("H", {"harness", "probe"}), "ATTACK_REQUESTED": ("H", {"harness"}),
    "FAULT_EXECUTOR_RESULT": ("H", {"fault_executor"}), "ATTACK_STOPPED": ("H", {"harness"}),
    "EFFECT_EVALUATED": ("H", {"effect_evaluator"}), "PROBE_SAMPLE": ("H", {"probe"}),
    "PROBE_HEARTBEAT": ("H", {"probe"}), "RELAPSE": ("H", {"recovery_evaluator"}),
    "RECOVERY_VERIFIED": ("H", {"recovery_evaluator"}), "CONTAINMENT_VERIFIED": ("H", {"recovery_evaluator"}),
    "DETECTED": ("O", {"detector"}),
    "DECISION": ("O", {"decision_rules", "decision_llm", "decision_single_llm", "operator_console"}),
    "LLM_CALL": ("O", {"decision_llm", "decision_single_llm"}), "GUARD_VERDICT": ("O", {"guard"}),
    "HEAL_STARTED": ("O", {"executor"}), "API_ACCEPTED": ("O", {"executor"}), "ACTION_COMPLETED": ("O", {"executor"}),
    "INCIDENT_LINK": ("S", {"scorer"}), "INCIDENT_SCORE": ("S", {"scorer"}), "LEAK_CHECK": ("S", {"scorer"}),
}
# required ID fields per event type [table 5.2]
INC = ["trial_id", "incident_id"]
REQ_IDS = {"TRIAL_STARTED": ["trial_id"], "TRIAL_ENDED": ["trial_id"], "TRIAL_CONTEXT": ["trial_id"],
           "HARNESS_MANIFEST": ["trial_id"], "SCHEDULE_ACCESS": ["trial_id"], "CLOCK_SYNC": ["trial_id"],
           "ATTACK_REQUESTED": INC, "FAULT_EXECUTOR_RESULT": INC, "ATTACK_STOPPED": INC, "EFFECT_EVALUATED": INC,
           "RELAPSE": INC, "RECOVERY_VERIFIED": INC, "CONTAINMENT_VERIFIED": INC,
           "DETECTED": ["alert_id"], "DECISION": ["decision_id"], "LLM_CALL": ["decision_id", "call_id"],
           "GUARD_VERDICT": ["decision_id"], "HEAL_STARTED": ["decision_id", "action_id"],
           "API_ACCEPTED": ["action_id"], "ACTION_COMPLETED": ["action_id"],
           "INCIDENT_LINK": ["incident_id"], "INCIDENT_SCORE": ["incident_id"]}


def E(*v):
    return ("enum", frozenset(v))


def E0(*v):
    return ("enum?", frozenset(v))


S, S0, B, I, N, N0, TS, TS0, L, L0, O, O0, A = "str", "str?", "bool", "int", "num", "num?", "ts", "ts?", "list", "list?", "obj", "obj?", "any"
# required payload fields per event type [table 5.3]; unknown extra fields are allowed (MINOR rule)
PAY = {
    "RUN_STARTED": {"canary_token": S, "protocol_ref": S, "schedule_ref": S, "f01_params": O, "reference_clock_id": S},
    "RUN_CLOSED": {"close_reason": E("COMPLETED", "ABORTED"), "recorder_manifest_ref": S0},
    "RUN_CONTEXT": {}, "TRIAL_CONTEXT": {},
    "TRIAL_STARTED": {"warmup_end": TS0, "planned_window": L, "probes": L},
    "TRIAL_ENDED": {"end_reason": E("PLANNED", "HORIZON", "ABORTED")},
    "HARNESS_MANIFEST": {"manifest_version": S, "allowlist_version": S, "reveal_terms": L, "entries": L},
    "GROUND_TRUTH_LOCKED": {"variant_id": S, "case_class": S, "cause": S, "decision_required": B, "acceptable_actions": L,
                            "constraints": O, "label_version": S, "reviewers": L, "locked_at": TS},
    "SCHEDULE_SEALED": {"schedule_sha256": S, "sealed_at": TS, "generated_after_label_lock": B},
    "SCHEDULE_ACCESS": {"actor_role": E("EVALUATOR", "OPERATOR", "HARNESS"), "scope_trial_ids": L, "accessed_at": TS},
    "AUDIT_COVERAGE": {"from": TS, "to": TS, "complete": B},
    "CLOCK_SYNC": {"clock_id": S, "reference_clock_id": S, "offset_ms": N, "uncertainty_ms": N0, "method": S, "measured_at": TS},
    "ATTACK_REQUESTED": {"variant_ref": S, "fault_params": O, "attack_command": S, "seed": A, "onset_offset_ms": N,
                         "s_att": L0, "known_good_revision": S0, "target_services": L},
    "FAULT_EXECUTOR_RESULT": {"executor_status": E("SUCCESS", "FAILED", "REJECTED", "TIMEOUT"), "command_ref": S, "duration_ms": N0},
    "ATTACK_STOPPED": {"stop_reason": E("PLANNED", "HORIZON", "ABORTED", "EXECUTOR_ENDED"), "executor_confirmed": B},
    "EFFECT_EVALUATED": {"status": E("CONFIRMED", "CONFIRMED_NO_EFFECT", "UNKNOWN_EFFECT"), "t_eff": TS0, "evidence_clock_id": S,
                         "criteria_version": S, "w_eff_s": N, "evidence": O, "reason": S},
    "PROBE_SAMPLE": {"probe_id": S, "flow": S, "sequence": I, "t_start": TS, "t_end": TS, "pass": B,
                     "error_class": E0("TIMEOUT", "CONNECT", "CONTENT", "SLOW"), "latency_ms": N, "probe_version": S},
    "PROBE_HEARTBEAT": {"probe_id": S, "flow": S, "last_sequence": A, "probe_version": S},
    "RELAPSE": {"flow": S, "candidate_t_rec": TS, "failing_sample_t": TS, "rule_version": S},
    "RECOVERY_VERIFIED": {"flow": S, "probe_id": S, "probe_version": S, "evidence_clock_id": S, "t_rec": TS,
                          "recovery_verified_at": TS, "evidence_complete_at": TS, "k": I, "s_s": N, "delta_s": N, "l_ms": N,
                          "gap_s": N, "cap_rec_s": N, "sample_seq_range": L, "samples_sha256": S, "rule_version": S},
    "CONTAINMENT_VERIFIED": {"blocked_source_ref": S, "enforcement_point": S, "fixture_probe_ref": S, "boutique_probe_ref": S, "t_contained": TS},
    "DETECTED": {"rule_id": S, "rule_version": S, "signature": S, "metric": S, "value": N, "threshold": N, "severity": S, "description": S},
    "DECISION": {"stage": E("ANALYSIS", "PROPOSAL"), "decision_source": E("RULES", "LLM", "SINGLE_LLM", "MANUAL"), "inputs": L,
                 "response_kind": E("ACTION", "NO_ACTION", "ABSTAIN", "SCHEMA_INVALID", "TIMEOUT", "REFUSAL"), "proposal": O0,
                 "fallback": B, "fallback_of": S0, "prompt_version": S0, "prompt_sha256": S0, "evidence_package_version": S},
    "LLM_CALL": {"attempt_no": I, "retry_reason": S0, "provider": S, "model": S, "prompt_version": S, "prompt_sha256": S0, "latency_ms": N,
                 "outcome": E("OK", "TIMEOUT", "HTTP_ERROR", "SCHEMA_INVALID", "REFUSAL"), "usage": O, "cost": O},
    "GUARD_VERDICT": {"verdict": E("ACCEPT", "REJECT"), "reason_code": S, "guard_version": S},
    "HEAL_STARTED": {"action_type": S, "params": O, "attempt_no": I, "retry_of": S0, "initiator": E("AUTO", "OPERATOR")},
    "API_ACCEPTED": {"api": S, "response_ref": S},
    "ACTION_COMPLETED": {"status": E("SUCCESS", "FAILED", "PARTIAL", "TIMEOUT"), "postcondition": O, "error": A},
    "INCIDENT_LINK": {"links": L, "ambiguous": B},
    "INCIDENT_SCORE": {"scorer_version": S, "input_manifest_sha256": S, "cutoff": TS},
    "LEAK_CHECK": {"result": E("CLEAN", "LEAK_DETECTED", "UNKNOWN"), "findings": L},
}
DECISION_SRC = {"decision_rules": "RULES", "decision_llm": "LLM", "decision_single_llm": "SINGLE_LLM", "operator_console": "MANUAL"}
FORBIDDEN_O_KEYS = {"case_class", "variant_id", "cause", "attack_command", "fault_params", "s_att", "decision_required",
                    "acceptable_actions", "expected_action", "known_good_revision", "seed", "onset_offset_ms",
                    "schedule", "canary_token", "effect_status", "t_eff", "t_rec", "recovery_verified_at"}
ZD_ACTION_TYPES = {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
# invalid events of these types inside an incident window make the incident MISSING (contract 6.4)
MANDATORY = {"ATTACK_REQUESTED", "ATTACK_STOPPED", "EFFECT_EVALUATED", "PROBE_SAMPLE", "DETECTED", "DECISION",
             "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"}
OFF_HOST = {"probe", "effect_evaluator", "recovery_evaluator"}
HARD = {"INTEGRITY_ERROR", "LINK_CONFLICT", "AMBIGUOUS", "ORPHAN_IN_WINDOW", "INVALID_EVENT", "INVALID_CLOCK", "TARGET_MISMATCH"}
MUTANTS = {
    "KPI_TS_INGEST": "T_rec taken from ts_ingest of RECOVERY_VERIFIED",
    "ACTION_AS_RECOVERY": "ACTION_COMPLETED=SUCCESS used as recovery when probe has none",
    "ANY_TERMINAL_COUNTS": "any terminal action (FAILED/PARTIAL/TIMEOUT) clears NO_ACTION_BEFORE_RECOVERY",
    "DEDUP_IGNORE_CONFLICT": "same event_id dropped as duplicate even when payload differs",
    "NO_DEDUP": "redelivered event_id kept as a new event",
    "INGEST_ORDER": "first DETECTED chosen by ingest order, not ts_event",
    "NO_SOURCE_AUTH": "source_component authority not checked",
    "CAP_CUTS_S": "cap_rec also bounds the stability window S",
    "UNKNOWN_LEAVES_N": "UNKNOWN_EFFECT removed from N",
    "NOEFFECT_TRUST_RECORD": "NO_EFFECT record accepted without coverage check",
    "NO_ID_SCAN": "identifier format/label scan skipped in O",
    "B0_ALLOW_ACTIONS": "ZERO DOOR decision/action events allowed in B0",
    "ORPHAN_AS_MISSED": "orphan detect in window ignored (incident becomes MISSED, not MISSING)",
    "NO_CLOCK_RULE": "OFF_HOST clock without CLOCK_SYNC accepted",
    # revision 2 (RV37-01..05)
    "NO_PREMATURE_CHECK": "RECOVERY_VERIFIED published before the last required sample ended is accepted",
    "NO_EVIDENCE_REF_CHECK": "RECOVERY_VERIFIED compared on t_rec only (range/hash/provenance ignored)",
    "LEAK_ANY_HARNESS_VALUE": "any registered harness value seen in O is a leak, neutral ones included (v1 rule)",
    "LEAK_NO_RESOURCE_CHECK": "harness resource manifest not checked",
    "NO_CLOCK_NORMALIZE": "CLOCK_SYNC offset ignored when comparing clocks",
    "NO_DRIFT": "first CLOCK_SYNC offset used for the whole trial (no interpolation)",
    "SYNC_BRACKET_TREQ": "sync coverage checked around T_req only, not trial start and end (v1 rule)",
    "CLOCK_QUALITY_UNCHECKED": "CLOCK_SYNC without uncertainty or clock without resolution accepted as exact",
    "SAMPLE_KEY_UNCHECKED": "two different PROBE_SAMPLE events with the same (probe_id, probe_version, sequence) accepted",
    "CLOCK_MISSING_ALL": "unverified clock voids every duration, same-clock ones included",
    "NO_SEMANTIC_CHECK": "cross-field payload rules (SUCCESS postcondition, probe pass, effect, decision) skipped",
    "NO_GROUP_SOURCE": "decision/LLM source and initiator not checked against the group for B1/B2/B3",
    "ACTION_DECISION_UNCHECKED": "HEAL_STARTED accepted without a known PROPOSAL decision of the allowed source",
    "TRUST_EXPLICIT_ID": "explicit IDs trusted without run/trial context check (v1 rule)",
    "NO_ACTION_MAP": "API_ACCEPTED/ACTION_COMPLETED not linked through the action_id of HEAL_STARTED",
    "NO_CAUSATION_CHECK": "causation_id not used to detect conflicting links",
    "TARGET_MISMATCH_COUNTS": "DETECTED on a non-target service counted as a normal detect",
    "UNSCOPED_BY_TIME": "event without run_id assigned to the run by time",
}


def iso(t):
    ms = int(round(t * 1000))  # fixtures use ms-exact values; floor == round here
    return (T0 + timedelta(milliseconds=ms)).strftime("%Y-%m-%dT%H:%M:%S.") + f"{ms % 1000:03d}Z"


def sec(ts):
    return (datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc) - T0).total_seconds()


def tsafe(ts):
    return sec(ts) if isinstance(ts, str) and TS_RE.match(ts) else None


def gid(case, name, kind):
    raw = hashlib.sha256(f"zer37:{case}:{name}".encode()).digest()[:16]
    return f"{kind}_{uuid.UUID(bytes=raw, version=4).hex}"


def canon(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def samples_sha(eids):
    return "sha256:" + canon(list(eids))


def tok(s):
    return re.sub(r"[-_.\s/:=]+", "_", str(s).lower())


# ---------------------------------------------------------------- build
def build(case_id, spec):
    run, trl = gid(case_id, "run", "run"), gid(case_id, "trial", "trl")
    canary = "cnry_" + gid(case_id, "canary", "evt")[4:]
    incs = spec.get("incidents") or [{k: spec[k] for k in ("t_req", "t_stop", "target", "flow", "effect")}]
    inc_ids = [spec.get("incident_id") or gid(case_id, f"inc{i}", "inc") for i in range(len(incs))]
    single = len(incs) == 1
    seqs, recs, prompts, meta = {}, [], {}, {"detects": [], "incidents": inc_ids}
    host_probe = spec["probe_clock"] == "HOST"
    ts0 = spec["trial_start"]
    off = spec.get("probe_offset") or {"a": 0, "b": 0}
    loc = lambda t: t + off["a"] + off["b"] * (t - ts0)  # local reading of the OFF_HOST clock at reference time t
    lo = lambda t: iso(loc(t)) if not host_probe else iso(t)
    probe_clk = "clk_host_lab" if host_probe else "clk_probe_ext"

    def env(etype, src, t, payload, inst=None, stream=None, ingest=None, **ids):
        plane = TYPES[etype][0]
        stream = stream or {"H": "h.control", "O": "o.context", "S": "s.score"}[plane]
        inst = inst or f"{src.split('_')[0][:4]}-0"
        seqs[(inst, stream)] = seqs.get((inst, stream), -1) + 1
        offh = src in OFF_HOST and not host_probe
        e = {"schema_version": SCHEMA, "event_id": gid(case_id, f"evt{len(recs)}", "evt"),
             "event_type": etype, "plane": plane, "run_id": ids.pop("run_id", run), "trial_id": ids.pop("trial_id", trl),
             "causation_id": ids.pop("causation_id", None), "group": spec["group"],
             "method_version": "zer32-acc+f01-illustrative", "config_ref": "sha256:" + "0" * 64,
             "source_component": src, "source_instance": inst, "producer_version": "sha256:" + "1" * 64,
             "stream": stream, "seq": seqs[(inst, stream)], "target": ids.pop("target", None),
             "clock": {"clock_id": "clk_probe_ext" if offh else "clk_host_lab",
                       "clock_source": "OFF_HOST" if offh else "HOST_SHARED", "resolution_ms": spec.get("probe_resolution_ms", 16) if offh else 1},
             "ts_event": iso(loc(t)) if offh else iso(t), "payload": payload}
        for k, v in ids.items():
            if v is not None:
                e[k] = v
        for k in ("trial_id", "run_id"):
            if e[k] is None:
                del e[k]
        add(e, t + 0.3 if ingest is None else ingest)
        return e

    def add(e, ts_ing):
        recs.append({"ingest_id": gid(case_id, f"ing{len(recs)}", "ing"), "ts_ingest": iso(ts_ing),
                     "transport": {"kind": "kafka", "topic": "zd.v0", "partition": 0, "offset": len(recs)},
                     "envelope_sha256": "sha256:" + canon(e), "envelope": e})

    probe_end = max([s[1] for s in spec["probe"]] + [0])
    t_end = max([300, probe_end + 10] + [i["t_stop"] + 10 for i in incs])
    o_inc = inc_ids[0] if single else None
    flow = incs[0]["flow"]
    env("RUN_STARTED", "harness", 0, {"canary_token": canary, "protocol_ref": "zer53-draft", "schedule_ref": "sha256:" + "5" * 64,
                                     "f01_params": P, "reference_clock_id": "clk_host_lab"}, trial_id=None)
    env("RUN_CONTEXT", "harness", 0, {}, trial_id=None)
    lab = spec["labels"]
    env("GROUND_TRUTH_LOCKED", "harness", 1, {"variant_id": lab["variant_id"], "case_class": lab["case_class"], "cause": "cpu_exhaustion",
                                             "decision_required": True, "acceptable_actions": ["SCALE_UP"], "constraints": {},
                                             "label_version": "v1", "reviewers": ["H", "Hoa"], "locked_at": iso(1)}, trial_id=None)
    env("SCHEDULE_SEALED", "harness", 2, {"schedule_sha256": "sha256:" + "6" * 64, "sealed_at": iso(2), "generated_after_label_lock": True}, trial_id=None)
    env("TRIAL_STARTED", "harness", ts0, {"warmup_end": iso(ts0 + 5), "planned_window": [iso(ts0), iso(t_end)],
                                          "probes": [{"probe_id": "prb-0", "flow": flow, "probe_version": "p0", "clock_id": probe_clk}]})
    if spec.get("manifest"):
        mf = spec["manifest"]
        env("HARNESS_MANIFEST", "harness", ts0, {"manifest_version": "m1", "allowlist_version": "a1", "reveal_terms": mf["reveal_terms"],
                                                 "entries": mf["entries"]}, stream="h.audit")
    env("TRIAL_CONTEXT", "harness", ts0, dict(spec.get("context_extra") or {}), incident_id=o_inc)
    if spec["probe_clock"] == "OFF_HOST_SYNCED":
        syncs = spec.get("syncs") or [[ts0, None, 20], [t_end, None, 20]]
        for m, o_ms, u in syncs:
            o_ms = round((loc(m) - m) * 1000, 3) if o_ms is None else o_ms
            env("CLOCK_SYNC", "harness", m, {"clock_id": "clk_probe_ext", "reference_clock_id": "clk_host_lab", "offset_ms": o_ms,
                                             "uncertainty_ms": u, "method": "synthetic", "measured_at": iso(m)})
    for i, inc in enumerate(incs):
        tgt = {"namespace": "target-app", "service": inc["target"], "flow": inc["flow"]}
        env("ATTACK_REQUESTED", "harness", inc["t_req"], {"variant_ref": lab["variant_id"], "fault_params": {"attack_type": lab["attack_type"]},
                                                          "attack_command": "synthetic", "seed": 7, "onset_offset_ms": 4200, "s_att": None,
                                                          "known_good_revision": None, "target_services": [inc["target"]]},
            incident_id=inc_ids[i], target=tgt)
        env("FAULT_EXECUTOR_RESULT", "fault_executor", inc["t_req"] + 0.5, {"executor_status": "SUCCESS", "command_ref": "c", "duration_ms": None},
            incident_id=inc_ids[i])
        env("ATTACK_STOPPED", "harness", inc["t_stop"], {"stop_reason": "PLANNED", "executor_confirmed": True}, incident_id=inc_ids[i])
        ef = inc["effect"]
        if ef:
            env("EFFECT_EVALUATED", "effect_evaluator", ef["t"], {"status": ef["status"], "t_eff": lo(ef["t_eff"]) if ef["t_eff"] is not None else None,
                                                                  "evidence_clock_id": probe_clk, "criteria_version": "f05-draft", "w_eff_s": P["w_eff"],
                                                                  "evidence": {"flow": inc["flow"], "first_sample_t": lo(inc["t_req"]),
                                                                               "last_sample_t": lo(ef["t_eff"] if ef["t_eff"] is not None else inc["t_req"] + P["w_eff"]),
                                                                               "max_gap_s": P["delta"], "sample_seq_range": None},
                                                                  "reason": "synthetic"},
                stream="h.eval", incident_id=inc_ids[i], target=tgt)
    patch = spec.get("probe_pass_patch")
    sample_log = {}  # sequence -> (t_end reference, event_id)
    for a, b, ok in spec["probe"]:
        for t in range(a, b + 1):
            pl = {"probe_id": "prb-0", "flow": flow, "sequence": t, "t_start": lo(t), "t_end": lo(t + 0.25),
                  "pass": ok, "error_class": None if ok else "CONTENT", "latency_ms": 250, "probe_version": "p0"}
            t_e = t + 0.25
            if ok and patch:
                t_e = t + patch["t_end_plus"]
                pl.update(latency_ms=patch["latency_ms"], error_class=patch["error_class"], t_end=lo(t_e))
            e = env("PROBE_SAMPLE", "probe", t + 0.25, pl, stream="h.probe", target={"namespace": "target-app", "service": None, "flow": flow})
            sample_log[t] = (t_e, e["event_id"])
            if spec.get("dup_sample") == t:  # a second, different sample under the same key
                env("PROBE_SAMPLE", "probe", t + 0.3, dict(pl, **{"pass": not ok, "error_class": "CONTENT" if ok else None}),
                    stream="h.probe", target={"namespace": "target-app", "service": None, "flow": flow})
    dets = []
    for j, d in enumerate(spec["detects"]):
        payload = {"rule_id": "cpu_limit_ratio", "rule_version": "r1", "signature": "cpu_limit_ratio/frontend", "metric": "cpu_usage_ratio_of_limit",
                   "value": 0.93, "threshold": 0.8, "severity": "WARNING", "description": d.get("description", "CPU usage is 93% of its limit.")}
        payload.update(d.get("payload_extra", {}))
        if "payload_replace" in d:
            payload = d["payload_replace"]
        kw = {"alert_id": gid(case_id, f"alt{j}", "alt"), "target": {"namespace": "target-app", "service": d.get("target", "frontend"), "flow": None}}
        if d.get("no_ids"):
            kw["trial_id"] = None
        else:
            kw["incident_id"] = o_inc
        if d.get("no_run"):
            kw["run_id"] = None
        if d.get("run_other"):
            kw["run_id"] = gid("other", "run", "run")
        if d.get("trial_other"):
            kw["trial_id"] = gid(case_id, "other-trial", "trl")
        e = env("DETECTED", d.get("src", "detector"), d["t"], payload, stream="o.alert", ingest=d.get("ingest"), ts_publish=iso(d["t"] + 0.2), **kw)
        for _ in range(d.get("dup", 0)):
            add(copy.deepcopy(e), d["t"] + 0.6)
        dets.append(e)
        meta["detects"].append(e["event_id"])
    dec = spec["decision"]
    dec_id = gid(case_id, "dec0", "dec")
    tgt = {"namespace": "target-app", "service": "frontend", "flow": None}
    cause_for_heal = None
    if dec:
        text = dec.get("prompt_text")
        psha = None
        if text is not None:
            text = text.replace("CANARY", canary)
            psha = "sha256:" + hashlib.sha256(text.encode()).hexdigest()
            prompts[psha] = text
        src_det = dets[dec["input_detect"]]
        llm = dec["decision_source"] in ("LLM", "SINGLE_LLM")
        e_dec = None
        if not dec.get("omit"):
            if llm:
                env("LLM_CALL", dec["source"], dec["t"] - 0.1, {"attempt_no": 1, "retry_reason": None, "provider": "synthetic", "model": "m", "prompt_version": "p1",
                                                                "prompt_sha256": psha, "latency_ms": 900, "outcome": "OK",
                                                                "usage": {"input_tokens": 300, "output_tokens": 60, "status": "COMPLETE"},
                                                                "cost": {"usd": None, "status": "MISSING", "price_ref": None}},
                    stream="o.decision", decision_id=dec_id, call_id=gid(case_id, "cal0", "cal"), incident_id=o_inc, target=tgt)
            prop = {"action_type": dec["action_type"], "params": {"service": "frontend"}} if dec["action_type"] else None
            e_dec = env("DECISION", dec["source"], dec["t"], {"stage": "PROPOSAL", "decision_source": dec["decision_source"],
                                                              "inputs": [{"event_id": src_det["event_id"], "received_at": iso(dec["received_at"])}],
                                                              "response_kind": dec["response_kind"], "proposal": prop, "fallback": False, "fallback_of": None,
                                                              "prompt_version": "p1" if llm else None, "prompt_sha256": psha, "evidence_package_version": "ev1"},
                        stream="o.decision", decision_id=dec_id, causation_id=src_det["event_id"], incident_id=o_inc, target=tgt)
            cause_for_heal = e_dec["event_id"]
        if spec["guard"]:
            g = env("GUARD_VERDICT", "guard", spec["guard"]["t"], {"verdict": spec["guard"]["verdict"], "reason_code": "OK", "guard_version": "g1"},
                    stream="o.decision", decision_id=dec_id, causation_id=e_dec["event_id"] if e_dec else None, incident_id=o_inc, target=tgt)
            cause_for_heal = g["event_id"]
    if spec.get("heal_causation_detect") is not None:
        cause_for_heal = dets[spec["heal_causation_detect"]]["event_id"]
    act_ids = []
    for i, a in enumerate(spec["actions"]):
        aid = gid(case_id, f"act{i}", "act")
        act_ids.append(aid)
        common = dict(stream="o.action", action_id=aid, incident_id=o_inc, target=tgt)
        tail = {} if spec.get("action_id_only") else {"decision_id": dec_id}
        hs = env("HEAL_STARTED", "executor", a["start"], {"action_type": "SCALE_UP", "params": {"service": "frontend"}, "attempt_no": i + 1,
                                                          "retry_of": act_ids[a["retry_of"]] if "retry_of" in a else None,
                                                          "initiator": a["initiator"]}, decision_id=dec_id, causation_id=cause_for_heal, **common)
        api = env("API_ACCEPTED", "executor", a["api"], {"api": "apps/v1 scale", "response_ref": "r"},
                  causation_id=None if spec.get("action_id_only") else hs["event_id"], **tail, **common)
        if a.get("complete") is not None:
            sat = a.get("satisfied", a["status"] == "SUCCESS")
            e = env("ACTION_COMPLETED", "executor", a["complete"], {"status": a["status"], "postcondition": {"name": "replicas_ready", "checked": True,
                    "satisfied": sat, "observed": "synthetic"}, "error": None},
                    causation_id=None if spec.get("action_id_only") else api["event_id"], **tail, **common)
            for _ in range(a.get("dup_complete", 0)):
                add(copy.deepcopy(e), a["complete"] + 0.9)
            if a.get("conflict"):
                e2 = copy.deepcopy(e)
                e2["payload"]["status"] = a["conflict"]
                e2["payload"]["postcondition"]["satisfied"] = False
                add(e2, a["complete"] + 1.2)

    def rv_payload(t_rec, over):
        rng = [int(t_rec) - (P["k"] - 1), int(t_rec + P["s"])]
        inr = [sample_log[q] for q in range(rng[0], rng[1] + 1) if q in sample_log]
        done = max([x[0] for x in inr] or [t_rec + P["s"]])
        rng = over.get("seq_range") or rng  # a wrongly reported range; the evidence used is unchanged
        t_rec_local = loc(t_rec) if not host_probe else t_rec  # D-04 runs on the probe clock's own readings
        return {"flow": flow, "probe_id": over.get("probe_id", "prb-0"), "probe_version": "p0", "evidence_clock_id": probe_clk,
                "t_rec": iso(t_rec_local), "recovery_verified_at": iso(t_rec_local + P["s"]), "evidence_complete_at": lo(done),
                "k": P["k"], "s_s": P["s"], "delta_s": P["delta"], "l_ms": P["l_ms"], "gap_s": P["gap"], "cap_rec_s": P["cap_rec"],
                "sample_seq_range": rng, "samples_sha256": over.get("samples_sha256") or samples_sha([x[1] for x in inr]),
                "rule_version": "zer32-d04"}
    rv = spec["recovery_event"]
    if rv:
        env("RECOVERY_VERIFIED", "recovery_evaluator", rv["t"], rv_payload(rv["t_rec"], rv), stream="h.eval", ingest=rv.get("ingest"), incident_id=inc_ids[0])
    for x in spec["extra"]:
        if x["type"] == "RELAPSE":
            env("RELAPSE", "recovery_evaluator", x["t"], {"flow": flow, "candidate_t_rec": lo(x["candidate_t_rec"]),
                                                         "failing_sample_t": lo(x["failing_sample_t"]), "rule_version": "zer32-d04"},
                stream="h.eval", incident_id=inc_ids[0])
        elif x["type"] == "RECOVERY_VERIFIED":
            env("RECOVERY_VERIFIED", x["src"], x["t"], rv_payload(x["t_rec"], {}), stream="h.eval", incident_id=inc_ids[0])
        elif x["type"] == "AUDIT_COVERAGE":
            env("AUDIT_COVERAGE", "harness", x["t"], {"from": iso(x["from"]), "to": iso(x["to"]), "complete": x["complete"]}, stream="h.audit", trial_id=None)
        elif x["type"] == "SCHEDULE_ACCESS":
            env("SCHEDULE_ACCESS", "harness", x["t"], {"actor_role": x["actor_role"], "scope_trial_ids": [trl], "accessed_at": iso(x["t"])}, stream="h.audit")
    env("TRIAL_ENDED", "harness", t_end, {"end_reason": "PLANNED"})
    return recs, prompts, meta


# ---------------------------------------------------------------- validate
def _ok(v, kind):
    if isinstance(kind, tuple):
        return (v is None and kind[0] == "enum?") or (isinstance(v, str) and v in kind[1])
    if kind.endswith("?") and v is None:
        return True
    k = kind.rstrip("?")
    return {"str": lambda: isinstance(v, str) and v != "", "bool": lambda: isinstance(v, bool),
            "int": lambda: isinstance(v, int) and not isinstance(v, bool),
            "num": lambda: isinstance(v, (int, float)) and not isinstance(v, bool),
            "ts": lambda: isinstance(v, str) and bool(TS_RE.match(v)), "list": lambda: isinstance(v, list),
            "obj": lambda: isinstance(v, dict), "any": lambda: True}[k]()


def semantic(t, p, e, ctx, mut):
    """Cross-field rules of table 5.3 / sections 7.2-7.5. Called only when the required fields are well-typed."""
    errs, sem = [], "NO_SEMANTIC_CHECK" not in mut
    if t == "ACTION_COMPLETED" and sem:
        pc = p["postcondition"]
        if not (isinstance(pc.get("checked"), bool) and isinstance(pc.get("satisfied"), bool)):
            errs.append("INVALID payload.postcondition")
        elif (p["status"] == "SUCCESS") != (pc["checked"] and pc["satisfied"]):
            errs.append("SEMANTIC status vs postcondition")
    elif t == "PROBE_SAMPLE" and sem:
        if sec(p["t_end"]) < sec(p["t_start"]):
            errs.append("SEMANTIC t_end < t_start")
        if p["pass"] != (p["error_class"] is None):
            errs.append("SEMANTIC pass vs error_class")
        if p["pass"] and ctx and ctx.get("l_ms") is not None and p["latency_ms"] > ctx["l_ms"]:
            errs.append("SEMANTIC pass with latency > L")
    elif t == "EFFECT_EVALUATED":
        ev = p["evidence"]
        spec = {"flow": S, "first_sample_t": TS0, "last_sample_t": TS0, "max_gap_s": N0, "sample_seq_range": L0}
        errs += [f"INVALID payload.evidence.{k}" for k, kind in spec.items() if k not in ev or not _ok(ev[k], kind)]
        if sem and (p["status"] == "CONFIRMED") != (p["t_eff"] is not None):
            errs.append("SEMANTIC status vs t_eff")
    elif t == "DECISION" and sem:
        if DECISION_SRC.get(e.get("source_component")) not in (None, p["decision_source"]):
            errs.append("SEMANTIC decision_source vs source_component")
        if (p["response_kind"] == "ACTION") != (p["proposal"] is not None):
            errs.append("SEMANTIC response_kind vs proposal")
        if p["fallback"] != (p["fallback_of"] is not None) or (p["fallback"] and p["decision_source"] != "RULES"):
            errs.append("SEMANTIC fallback")
        if p["decision_source"] in ("LLM", "SINGLE_LLM") and p["prompt_sha256"] is None:
            errs.append("SEMANTIC LLM decision without prompt_sha256")
        if not all(isinstance(x, dict) and _ok(x.get("event_id"), "str") and _ok(x.get("received_at"), "ts") for x in p["inputs"]):
            errs.append("INVALID payload.inputs")
    elif t == "HEAL_STARTED" and sem:
        if (p["attempt_no"] > 1) != (p["retry_of"] is not None):
            errs.append("SEMANTIC attempt_no vs retry_of")
    elif t == "LLM_CALL" and sem:
        if (p["attempt_no"] > 1) != (p["retry_reason"] is not None):
            errs.append("SEMANTIC attempt_no vs retry_reason")
    elif t == "RELAPSE" and sem:
        if sec(p["failing_sample_t"]) <= sec(p["candidate_t_rec"]):
            errs.append("SEMANTIC failing sample not after candidate")
    elif t == "AUDIT_COVERAGE" and sem:
        if sec(p["to"]) < sec(p["from"]):
            errs.append("SEMANTIC to < from")
    elif t == "RECOVERY_VERIFIED":
        rng = p["sample_seq_range"]
        if not (len(rng) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in rng) and rng[0] <= rng[1]
                and rng[1] - rng[0] + 1 >= p["k"]):
            errs.append("INVALID payload.sample_seq_range")
        if abs(sec(p["recovery_verified_at"]) - sec(p["t_rec"]) - p["s_s"]) > 0.0005:
            errs.append("SEMANTIC recovery_verified_at != t_rec + S")
        if sec(p["evidence_complete_at"]) < sec(p["recovery_verified_at"]):
            errs.append("SEMANTIC evidence_complete_at < recovery_verified_at")
        same = p["evidence_clock_id"] == (e.get("clock") or {}).get("clock_id")
        if "NO_PREMATURE_CHECK" not in mut and same and sec(e["ts_event"]) < sec(p["evidence_complete_at"]):
            errs.append("SEMANTIC premature: ts_event < evidence_complete_at")
    return errs


def validate(e, mut=frozenset(), ctx=None):
    """Return (errors, source_ok). Errors are MISSING_FIELD / INVALID / SEMANTIC; source authority is separate."""
    if not isinstance(e, dict):
        return ["INVALID envelope"], False
    errs = [f"MISSING_FIELD {k}" for k in ENV_REQUIRED if e.get(k) is None]
    t = e.get("event_type")
    if t not in TYPES:
        return errs + [f"INVALID event_type {t}"], False
    if e.get("plane") != TYPES[t][0]:
        errs.append("INVALID plane")
    for k in ("ts_event", "ts_publish"):
        if e.get(k) is not None and not TS_RE.match(str(e[k])):
            errs.append(f"INVALID {k}")
    if e.get("schema_version") not in (None, SCHEMA):
        errs.append("INVALID schema_version")
    if e.get("group") not in (None, "B0", "B1", "B2", "B3", "BM"):
        errs.append("INVALID group")
    c = e.get("clock")
    if c is not None and not (isinstance(c, dict) and c.get("clock_source") in ("HOST_SHARED", "OFF_HOST", "UNKNOWN") and _ok(c.get("clock_id"), "str")
                              and _ok(c.get("resolution_ms"), "num?")):
        errs.append("INVALID clock")
    if e.get("seq") is not None and not (_ok(e["seq"], "int") and e["seq"] >= 0):
        errs.append("INVALID seq")
    errs += [f"INVALID id {f}" for f in bad_ids(e)]
    errs += [f"MISSING_FIELD {f}" for f in REQ_IDS.get(t, []) if e.get(f) is None]
    p = e.get("payload")
    if p is not None and not isinstance(p, dict):
        errs.append("INVALID payload")
    elif isinstance(p, dict):
        perr = [f"MISSING_FIELD payload.{k}" for k in PAY[t] if k not in p]
        perr += [f"INVALID payload.{k}" for k, kind in PAY[t].items() if k in p and not _ok(p[k], kind)]
        if not perr and not errs:
            try:
                perr = semantic(t, p, e, ctx, mut)
            except (TypeError, ValueError, KeyError, AttributeError) as x:
                perr = [f"INVALID payload ({type(x).__name__})"]
        errs += perr
    src_ok = "NO_SOURCE_AUTH" in mut or e.get("source_component") in TYPES[t][1]
    return errs, src_ok


def bad_ids(e):
    return [f for f, k in ID_FIELDS.items() if e.get(f) is not None and not (isinstance(e[f], str) and ID_RE[k].match(e[f]))]


# ---------------------------------------------------------------- analyse
def recover(samples, t_eff, mut, prm=None):
    """ZER-32 D-04 on sample dicts {t, end, ok, seq, eid, ...} sorted by t (one clock).
    Returns (rec, relapses, unverifiable, covered, gap_before); rec is None or
    {t_rec, i_k, seq_range, complete, eids, used}."""
    prm = prm or P
    K, S, gap, cap = prm["k"], prm["s"], prm["gap"], prm["cap_rec"]
    after = [s for s in samples if s["t"] >= t_eff]
    first_fail = next((i for i, s in enumerate(after) if not s["ok"]), None)
    relapses, unverifiable = 0, False
    i = len(after) if first_fail is None else first_fail + 1
    while i < len(after):
        if not after[i]["ok"]:
            i += 1
            continue
        run, j = [after[i]], i + 1
        while len(run) < K and j < len(after) and after[j]["ok"] and after[j]["t"] - after[j - 1]["t"] <= gap:
            run.append(after[j])
            j += 1
        if len(run) < K:
            i = j if j > i else i + 1
            continue
        t_rec = run[-1]["t"]
        limit = t_rec + S if "CAP_CUTS_S" in mut else t_rec
        if limit > t_eff + cap:
            break
        prev, k, relapse, reached = t_rec, j, False, False
        while k < len(after):
            t, ok = after[k]["t"], after[k]["ok"]
            if t - prev > gap:
                break
            if t <= t_rec + S and not ok:
                relapse = True
                break
            prev = t
            if t >= t_rec + S:
                reached = True
                break
            k += 1
        if relapse:
            relapses += 1
            i = k
            continue
        if not reached:
            unverifiable = True
            i = k
            continue
        seg = [s["t"] for s in after if s["t"] <= t_rec]
        gap_before = any(b - a > gap for a, b in zip(seg, seg[1:]))
        used = after[i:k + 1]
        rec = {"t_rec": t_rec, "kth": run[-1], "seq_range": [used[0]["seq"], used[-1]["seq"]], "complete": max(s["end"] for s in used),
               "eids": [s["eid"] for s in used], "probe_ids": {s["probe_id"] for s in used}, "versions": {s["ver"] for s in used}}
        return rec, relapses, unverifiable, True, gap_before
    seg = [s["t"] for s in after if s["t"] <= t_eff + cap]
    nxt = [s["t"] for s in after if s["t"] > t_eff + cap][:1]
    seq = seg + nxt
    covered = bool(seq) and seq[0] - t_eff <= gap and seq[-1] >= t_eff + cap and all(b - a <= gap for a, b in zip(seq, seq[1:]))
    return None, relapses, unverifiable, covered, False


def analyse(recs, prompts, mut=frozenset()):
    out = {"duplicates_dropped": 0, "integrity_errors": 0, "orphans": 0, "source_violations": 0, "schema_errors": [],
           "unscoped": 0, "foreign": 0, "invalid_events": 0, "link_conflicts": []}
    order = sorted(range(len(recs)), key=lambda i: (recs[i]["ts_ingest"], i))
    seen, events, integrity, ingest_t = {}, [], set(), {}
    for i in order:
        r = recs[i]
        e = r["envelope"]
        eid = e.get("event_id") if isinstance(e, dict) else None
        if eid in seen:
            if seen[eid] == r["envelope_sha256"] or "DEDUP_IGNORE_CONFLICT" in mut:
                out["duplicates_dropped"] += 1
                if "NO_DEDUP" in mut:
                    events.append(e)
            else:
                integrity.add(eid)
            continue
        seen[eid] = r["envelope_sha256"]
        ingest_t[eid] = sec(r["ts_ingest"])
        events.append(e)
    out["integrity_errors"] = len(integrity)
    starts = [e for e in events if isinstance(e, dict) and e.get("event_type") == "RUN_STARTED" and e.get("source_component") == "harness"
              and not validate(e)[0]]
    run = starts[0]
    run_id, group = run["run_id"], run["group"]
    prm = {**P, **run["payload"]["f01_params"]}
    S, eps = prm["s"], prm["eps"]
    ctx = {"l_ms": prm.get("l_ms")}
    ref_clock = run["payload"]["reference_clock_id"]
    # run scope [6.3]: no run_id -> UNSCOPED, other run_id -> foreign; never assigned by time
    inrun, foreign = [], []
    for e in events:
        if not isinstance(e, dict):
            out["unscoped"] += 1
            continue
        if e.get("run_id") is None:
            if "UNSCOPED_BY_TIME" not in mut:
                out["unscoped"] += 1
                continue
            e = dict(e, run_id=run_id)
        if e["run_id"] == run_id or "TRUST_EXPLICIT_ID" in mut:
            inrun.append(e)
        else:
            foreign.append(e)
    valid, invalid = [], []
    for e in inrun:
        errs, src_ok = validate(e, mut, ctx)
        if not src_ok:
            out["source_violations"] += 1
            continue
        if errs:
            out["schema_errors"].append((e.get("event_type"), errs))
            invalid.append(e)
            continue
        valid.append(e)
    out["invalid_events"] = len(invalid)
    by = lambda t: [e for e in valid if e["event_type"] == t]
    # clocks [4.3]
    clk = {}
    for e in valid:
        clk.setdefault(e["clock"]["clock_id"], (e["clock"]["clock_source"], e["clock"].get("resolution_ms")))
    trials = {e["trial_id"]: [sec(e["ts_event"]), None] for e in by("TRIAL_STARTED")}
    for e in by("TRIAL_ENDED"):
        if e["trial_id"] in trials:
            trials[e["trial_id"]][1] = sec(e["ts_event"])
    reqs = {}
    for e in by("ATTACK_REQUESTED"):
        reqs.setdefault(e["trial_id"], []).append(sec(e["ts_event"]))
    syncs = {}
    for e in by("CLOCK_SYNC"):
        p = e["payload"]
        syncs.setdefault((e["trial_id"], p["clock_id"]), []).append(
            (sec(p["measured_at"]), p["offset_ms"] / 1000, None if p["uncertainty_ms"] is None else p["uncertainty_ms"] / 1000))

    def cstate(trial, cid):
        src, res = clk.get(cid, ("UNKNOWN", None))
        if cid == ref_clock or src == "HOST_SHARED":
            return "REF", []
        s = sorted(syncs.get((trial, cid), []))
        if "NO_CLOCK_RULE" in mut:
            return "OK", s or [(0.0, 0.0, 0.0)]
        if "CLOCK_QUALITY_UNCHECKED" in mut:
            s, res = [(m, o, u or 0.0) for m, o, u in s], res if res is not None else 0
        if res is None or not s or any(u is None for _, _, u in s):
            return "UNVERIFIED", s
        if "SYNC_BRACKET_TREQ" in mut:
            ok = all(s[0][0] <= tq <= s[-1][0] for tq in reqs.get(trial, [])) and bool(reqs.get(trial))
        else:
            tr = trials.get(trial)
            ok = bool(tr) and tr[1] is not None and s[0][0] <= tr[0] and s[-1][0] >= tr[1]
        return ("OK" if ok else "UNVERIFIED"), s

    def norm(local, trial, cid):
        """local seconds on clock cid -> milestone (ref seconds, uncertainty s, verified, clock_id)."""
        res = (clk.get(cid, ("UNKNOWN", None))[1] or 0) / 1000
        st, s = cstate(trial, cid)
        if st == "REF":
            return (local, res, True, cid)
        if st == "UNVERIFIED":
            return (local, None, False, cid)
        if "NO_CLOCK_NORMALIZE" in mut:
            o = 0.0
        elif "NO_DRIFT" in mut or len(s) == 1:
            o = s[0][1]
        else:  # linear interpolation on the clock's own axis (measured_at + offset)
            pts = [(m + o_, o_) for m, o_, _ in s]
            o = pts[0][1] if local <= pts[0][0] else pts[-1][1]
            for (x0, o0), (x1, o1) in zip(pts, pts[1:]):
                if x0 <= local <= x1:
                    o = o0 + (o1 - o0) * (local - x0) / (x1 - x0)
                    break
        return (local - o, max(u or 0.0 for _, _, u in s) + res, True, cid)

    def ms(e, field=None, env_field=None):
        if env_field:
            raw, cid = e.get(env_field), e["clock"]["clock_id"]
        elif field:
            raw = e["payload"].get(field)
            cid = e["payload"].get("evidence_clock_id") or e["clock"]["clock_id"]
        else:
            raw, cid = e["ts_event"], e["clock"]["clock_id"]
        if raw is None:
            return None
        return norm(sec(raw), e.get("trial_id"), cid)

    def comparable(a, b):
        return a[3] == b[3] or (a[2] and b[2])

    def dur(a, b):
        """b - a with uncertainty in ms; ('CLOCK', None) when the clocks cannot be compared."""
        if a[3] == b[3]:
            res = (clk.get(a[3], ("", None))[1] or 0) / 1000
            return round(b[0] - a[0], 3), int(round(2 * res * 1000))
        if a[2] and b[2]:
            return round(b[0] - a[0], 3), int(round((a[1] + b[1]) * 1000))
        return "CLOCK", None

    # incidents [3.2]
    incs = {}
    for e in by("ATTACK_REQUESTED"):
        incs[e["incident_id"]] = {"t_req": ms(e), "trial": e["trial_id"], "targets": set(e["payload"]["target_services"]),
                                  "flow": (e.get("target") or {}).get("flow"), "t_stop": None, "eff": None, "det": [], "det_mm": [],
                                  "dec": [], "missing": set(), "flags": set(), "ev": [], "rv": [], "rv_bad": []}

    def conflict(ks, why):
        out["link_conflicts"].append(why)
        for k in ks:
            if k in incs:
                incs[k]["missing"].add("LINK_CONFLICT")

    for e in valid:  # H events with an explicit incident_id must agree with its trial
        if e["plane"] == "H" and e.get("incident_id") in incs and e.get("trial_id") != incs[e["incident_id"]]["trial"] \
                and "TRUST_EXPLICIT_ID" not in mut:
            conflict([e["incident_id"]], f"{e['event_type']} trial")
    for e in by("ATTACK_STOPPED"):
        if e["incident_id"] in incs:
            incs[e["incident_id"]]["t_stop"] = ms(e)
    for e in by("EFFECT_EVALUATED"):
        if e["incident_id"] in incs:
            incs[e["incident_id"]]["eff"] = e
            incs[e["incident_id"]]["ev"].append(e)
    for e in by("RECOVERY_VERIFIED"):
        if e["incident_id"] in incs:
            incs[e["incident_id"]]["rv"].append(e)

    def t_eff_of(inc):
        return ms(inc["eff"], "t_eff") if inc["eff"] and inc["eff"]["payload"]["status"] == "CONFIRMED" else None

    def w_end(inc):
        te = t_eff_of(inc)
        return (te[0] if te else inc["t_req"][0] + prm["w_eff"]) + prm["cap_det"]

    # foreign events that carry this run's IDs are conflicts, not data [6.3]
    for e in foreign:
        out["foreign"] += 1
        ks = {e.get("incident_id")} & set(incs)
        ks |= {k for k, v in incs.items() if e.get("trial_id") is not None and v["trial"] == e.get("trial_id")}
        if ks:
            conflict(ks, f"{e.get('event_type')} from another run carries this run's ID")
    # link O events [6.3]
    orphans, alert_inc, dec_inc, act_inc, act_dec, ev_inc, links, ambiguous = [], {}, {}, {}, {}, {}, {}, False
    acts = {}
    o_order = ["DETECTED", "DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"]
    for t in o_order:
        for e in sorted(by(t), key=lambda x: sec(x["ts_event"])):
            cands = []
            iid = e.get("incident_id")
            if iid is not None:
                if iid not in incs:
                    orphans.append(e)
                    continue
                cands.append(("explicit", iid))
            if t == "DECISION":
                cands += [("input", alert_inc[x["event_id"]]) for x in e["payload"]["inputs"] if x["event_id"] in alert_inc]
            if t in ("LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED") and e.get("decision_id") in dec_inc:
                cands.append(("decision", dec_inc[e["decision_id"]]))
            if t in ("API_ACCEPTED", "ACTION_COMPLETED"):
                aid = e["action_id"]
                if "NO_ACTION_MAP" not in mut and aid in act_inc:
                    cands.append(("action", act_inc[aid]))
                if e.get("decision_id") and aid in act_dec and act_dec[aid] != e["decision_id"]:
                    conflict({k for _, k in cands} | ({act_inc[aid]} if aid in act_inc else set()), f"{t} decision_id differs from HEAL_STARTED")
                    continue
            if e.get("causation_id") and "NO_CAUSATION_CHECK" not in mut and e["causation_id"] in ev_inc:
                cands.append(("causation", ev_inc[e["causation_id"]]))
            ks = {k for _, k in cands}
            if ks and e.get("trial_id") is not None and "TRUST_EXPLICIT_ID" not in mut and any(incs[k]["trial"] != e["trial_id"] for k in ks):
                conflict(ks, f"{t} trial differs from incident")
                continue
            if len(ks) > 1:
                conflict(ks, f"{t} links disagree: {sorted(m for m, _ in cands)}")
                continue
            k = next(iter(ks)) if ks else None
            if k is None and t == "DETECTED" and e.get("trial_id"):
                ts = sec(e["ts_event"])
                cand = [kk for kk, v in incs.items() if v["trial"] == e["trial_id"] and v["t_req"][0] - eps <= ts <= w_end(v)]
                if len(cand) > 1:
                    svc = (e.get("target") or {}).get("service")
                    cand = [kk for kk in cand if svc in incs[kk]["targets"]] or cand
                    if len(cand) > 1:
                        ambiguous = True
                        for kk in cand:
                            incs[kk]["missing"].add("AMBIGUOUS")
                        continue
                k = cand[0] if cand else None
            if k is None:
                orphans.append(e)
                continue
            ev_inc[e["event_id"]] = k
            if t == "DETECTED":
                alert_inc[e["event_id"]] = k
                links[e["event_id"]] = k
                svc = (e.get("target") or {}).get("service")
                if svc not in incs[k]["targets"] and "TARGET_MISMATCH_COUNTS" not in mut:
                    incs[k]["det_mm"].append(e)  # policy OPEN (ZER-10/53): held, not a normal detect
                else:
                    incs[k]["det"].append(e)
            elif t == "DECISION":
                dec_inc[e["decision_id"]] = k
                incs[k]["dec"].append(e)
            elif t in ("HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"):
                if t == "HEAL_STARTED":
                    act_inc[e["action_id"]] = k
                    act_dec[e["action_id"]] = e["decision_id"]
                acts.setdefault(e["action_id"], {"inc": k}).setdefault(t, []).append(e)
                incs[k]["ev"].append(e)
    out["orphans"] = len(orphans)
    for e in events:  # integrity errors poison the incident they belong to
        if isinstance(e, dict) and e.get("event_id") in integrity:
            k = e.get("incident_id") or dec_inc.get(e.get("decision_id")) or act_inc.get(e.get("action_id"))
            if k in incs:
                incs[k]["missing"].add("INTEGRITY_ERROR")
    # invalid events [6.4]
    for e in invalid:
        t = e.get("event_type")
        k = e.get("incident_id") if e.get("incident_id") in incs else None
        if t in ("RECOVERY_VERIFIED", "RELAPSE"):
            if k:
                incs[k]["rv_bad"].append(e)
            continue
        if t not in MANDATORY:
            continue
        if k:
            incs[k]["missing"].add("INVALID_EVENT")
            continue
        ts, p = tsafe(e.get("ts_event")), e.get("payload") if isinstance(e.get("payload"), dict) else {}
        for kk, v in incs.items():
            if e.get("trial_id") not in (None, v["trial"]) or ts is None:
                continue
            if t == "PROBE_SAMPLE":
                hit = p.get("flow") == v["flow"] and ts >= v["t_req"][0] - eps
            else:
                hit = v["t_req"][0] - eps <= ts <= w_end(v)
            if hit:
                v["missing"].add("INVALID_EVENT")
    # probe registry and samples [7.5]
    reg = {}
    for e in by("TRIAL_STARTED"):
        for pr in e["payload"]["probes"]:
            reg.setdefault((e["trial_id"], pr.get("flow")), set()).add(pr.get("probe_id"))
    probes = by("PROBE_SAMPLE")
    results = []
    any_detector = bool(by("DETECTED"))
    for k, inc in incs.items():
        r = {"incident_id": k}
        flags, missing = set(inc["flags"]), set(inc["missing"])
        allowed = reg.get((inc["trial"], inc["flow"]))
        smp = {}
        for p in probes:
            pl = p["payload"]
            if p.get("trial_id") != inc["trial"] or pl["flow"] != inc["flow"] or (allowed is not None and pl["probe_id"] not in allowed):
                continue
            key = (pl["probe_id"], pl["probe_version"], pl["sequence"])
            if key in smp and smp[key]["eid"] != p["event_id"] and "SAMPLE_KEY_UNCHECKED" not in mut:
                missing.add("INTEGRITY_ERROR")
            m0 = ms(p, "t_start")
            smp[key] = {"t": sec(pl["t_start"]), "m": m0, "end": sec(pl["t_end"]), "ok": pl["pass"], "seq": pl["sequence"], "eid": p["event_id"],
                        "probe_id": pl["probe_id"], "ver": pl["probe_version"]}
        samples = sorted(smp.values(), key=lambda s: s["t"])
        t_req = inc["t_req"]
        # effect [7.2]
        eff, E_ = "UNKNOWN_EFFECT", None
        if inc["eff"]:
            st = inc["eff"]["payload"]["status"]
            if st == "CONFIRMED":
                eff, E_ = "CONFIRMED", t_eff_of(inc)
            elif st == "CONFIRMED_NO_EFFECT":
                w = [s for s in samples if t_req[0] <= s["m"][0] <= t_req[0] + prm["w_eff"]]
                ok = bool(w) and w[0]["m"][0] - t_req[0] <= prm["gap"] and t_req[0] + prm["w_eff"] - w[-1]["m"][0] <= prm["gap"] \
                    and all(s["ok"] for s in w) and all(b["t"] - a["t"] <= prm["gap"] for a, b in zip(w, w[1:]))
                if ok or "NOEFFECT_TRUST_RECORD" in mut:
                    eff = "CONFIRMED_NO_EFFECT"
        r["effect"] = eff
        # detect [5.2, 6.3]
        ub = w_end(inc)
        dets = [d for d in inc["det"] if t_req[0] - eps <= ms(d)[0] <= ub]
        if "INGEST_ORDER" in mut:
            dets.sort(key=lambda d: ingest_t[d["event_id"]])
        else:
            dets.sort(key=lambda d: ms(d)[0])
        D = ms(dets[0]) if dets else None
        if inc["det_mm"]:
            flags.add("TARGET_MISMATCH")
            if not dets:
                missing.add("TARGET_MISMATCH")
        r["t_det"] = round(D[0], 3) if D else None
        if "ORPHAN_AS_MISSED" not in mut and any(o["event_type"] in ("DETECTED", "ACTION_COMPLETED", "EFFECT_EVALUATED")
                                                 and o.get("trial_id") in (None, inc["trial"])
                                                 and t_req[0] - eps <= sec(o["ts_event"]) <= ub for o in orphans):
            missing.add("ORPHAN_IN_WINDOW")
        # clock order [4.3]
        def later(a, b):  # a later than b by more than eps, when comparable
            return a is not None and b is not None and comparable(a, b) and a[0] > b[0] + eps
        alerts = {d["event_id"]: d for d in inc["det"] + inc["det_mm"]}
        for dcs in inc["dec"]:
            for x in dcs["payload"]["inputs"]:
                d = alerts.get(x["event_id"])
                t_con = norm(sec(x["received_at"]), dcs.get("trial_id"), dcs["clock"]["clock_id"])
                if d:
                    t_d, t_pub = ms(d), ms(d, env_field="ts_publish") or ms(d)
                    if later(t_d, t_pub) or later(t_pub, t_con):
                        missing.add("INVALID_CLOCK")
                for a in acts.values():
                    for hs in a.get("HEAL_STARTED", []):
                        if hs.get("decision_id") == dcs["decision_id"] and later(t_con, ms(hs)):
                            missing.add("INVALID_CLOCK")
        for a in acts.values():
            if a["inc"] == k and a.get("API_ACCEPTED") and a.get("ACTION_COMPLETED"):
                if later(ms(a["API_ACCEPTED"][0]), ms(a["ACTION_COMPLETED"][0])):
                    missing.add("INVALID_CLOCK")
        # actions [7.3]
        mine = {aid: a for aid, a in acts.items() if a["inc"] == k}
        r["action_attempts"] = sum(1 for a in mine.values() if a.get("HEAL_STARTED"))
        r["terminal_events"] = sum(len(a.get("ACTION_COMPLETED", [])) for a in mine.values())
        if any(a.get("HEAL_STARTED") and not a.get("ACTION_COMPLETED") for a in mine.values()):
            flags.add("ACTION_TERMINAL_MISSING")
        completed = [c for a in mine.values() for c in a.get("ACTION_COMPLETED", [])]
        succ = sorted((ms(c) for c in completed if c["payload"]["status"] == "SUCCESS"), key=lambda m: m[0])
        # recovery [7.5]
        # D-04 runs on the probe clock's own readings; only the resulting milestones are normalized [4.3, 7.5]
        rec, rel, unver, covered, gap_before = (None, 0, False, False, False)
        s_clk = samples[0]["m"][3] if samples else None
        if E_ is not None:
            e_local = sec(inc["eff"]["payload"]["t_eff"]) if E_[3] == s_clk else E_[0]
            rec, rel, unver, covered, gap_before = recover(samples, e_local, mut, prm)
        R = rec["kth"]["m"] if rec else None
        on_probe = lambda x: norm(x, inc["trial"], s_clk)
        issues = []
        for rv in inc["rv"]:
            p = rv["payload"]
            if rec is None:
                issues.append("t_rec without recomputed recovery")
                continue
            if abs(ms(rv, "t_rec")[0] - R[0]) > 0.0005:
                issues.append("t_rec")
            if "NO_EVIDENCE_REF_CHECK" not in mut:
                if abs(ms(rv, "recovery_verified_at")[0] - on_probe(rec["t_rec"] + S)[0]) > 0.0005:
                    issues.append("recovery_verified_at")
                if p["sample_seq_range"] != rec["seq_range"]:
                    issues.append("sample_seq_range")
                if abs(ms(rv, "evidence_complete_at")[0] - on_probe(rec["complete"])[0]) > 0.0005:
                    issues.append("evidence_complete_at")
                if p["samples_sha256"] != samples_sha(rec["eids"]):
                    issues.append("samples_sha256")
                if p["flow"] != inc["flow"] or {p["probe_id"]} != rec["probe_ids"] or {p["probe_version"]} != rec["versions"]:
                    issues.append("provenance")
            if "NO_PREMATURE_CHECK" not in mut:
                pub, done = ms(rv), on_probe(rec["complete"])
                if comparable(pub, done) and pub[0] < done[0] - 0.0005:
                    issues.append("premature")
        issues += ["invalid evaluator event"] * len(inc["rv_bad"])
        r["evaluator_mismatch"], r["evaluator_issues"] = bool(issues), issues
        if "KPI_TS_INGEST" in mut and inc["rv"]:
            R = (ingest_t[inc["rv"][0]["event_id"]], 0.0, True, ref_clock)
        if "ACTION_AS_RECOVERY" in mut and R is None and succ:
            R = succ[0]
        r["t_rec"], r["relapses"] = (round(R[0], 3) if R else None), rel
        if gap_before:
            flags.add("PROBE_GAP")
        clock_bad = [False]

        def cmp_ok(a, b):
            ok = comparable(a, b)
            clock_bad[0] |= not ok
            return ok
        b0_na = group == "B0" and not any_detector
        hard = missing & HARD
        if hard:
            label = "MISSING"
            flags |= hard
        elif eff == "UNKNOWN_EFFECT":
            label = "UNKNOWN_EFFECT"
        elif eff == "CONFIRMED_NO_EFFECT":
            label = "OUT_NO_EFFECT"
        elif R is not None:
            stop = inc["t_stop"]
            if D is None:
                label = "RECOVERED_UNDETECTED"
            elif not cmp_ok(D, R):
                label = "MISSING"
            elif R[0] < D[0]:
                label = "RECOVERED_BEFORE_DETECT"
            elif stop is not None and not cmp_ok(stop, R):
                label = "MISSING"
            elif stop is not None and stop[0] < (on_probe(rec["t_rec"] + S)[0] if rec else R[0] + S):
                label = "RECOVERED_AFTER_STOP"
            else:
                label = "RECOVERED"
            pool = sorted((ms(c) for c in completed), key=lambda m: m[0]) if "ANY_TERMINAL_COUNTS" in mut else succ
            if all(comparable(t, R) for t in pool):
                if not any(t[0] < R[0] for t in pool):
                    flags.add("NO_ACTION_BEFORE_RECOVERY")
            else:
                clock_bad[0] = True
        else:
            label = "TIMEOUT" if covered and not unver else "MISSING_PROBE"
        u_ms = {}
        if b0_na:
            r["mttd"] = r["mttr"] = r["reaction"] = "N/A"
            r["total"] = None
        elif hard or label in ("UNKNOWN_EFFECT", "OUT_NO_EFFECT"):
            r["mttd"] = r["mttr"] = r["reaction"] = "MISSING"
            r["total"] = None
        else:
            def put(name, d, clip=False):
                if d[0] == "CLOCK":
                    clock_bad[0] = True
                    return "MISSING"
                u_ms[name] = d[1]
                return max(0.0, d[0]) if clip else d[0]
            if D is None:
                r["mttd"], r["reaction"] = "MISSED", "NO_DETECT"
            else:
                d = dur(E_, D)
                if d[0] != "CLOCK" and d[0] < 0:
                    flags.add("EARLY_DETECT")
                r["mttd"] = put("mttd", d, clip=True)
                ok_s = [s for s in succ if s[0] >= D[0] and s[0] <= E_[0] + prm["cap_rec"]]
                r["reaction"] = put("reaction", dur(D, ok_s[0])) if ok_s else "NO_SUCCESS"
            if R is not None and D is not None:
                d = dur(D, R)
                r["mttr"] = put("mttr", d) if d[0] == "CLOCK" or d[0] >= 0 else None
            else:
                r["mttr"] = None
            r["total"] = put("total", dur(E_, R)) if R is not None else None
            if "CLOCK_MISSING_ALL" in mut and any(not m[2] for m in (E_, D, R) if m):
                clock_bad[0] = True
                r["mttd"] = r["mttr"] = r["reaction"] = r["total"] = "MISSING"
        if clock_bad[0]:
            flags.add("CLOCK_UNVERIFIED")
            if label.startswith("RECOVERED"):
                label = "MISSING"
        r["label"], r["u_ms"], r["flags"] = label, u_ms, sorted(flags)
        results.append(r)
    out["incidents"], out["links"], out["ambiguous"] = results, links, ambiguous
    # mode [7.4]
    mf = [f"group {e.get('group')}" for e in valid + invalid if e.get("group") not in (None, group)]
    zd = [e for e in valid if e["event_type"] in ZD_ACTION_TYPES]
    if group == "B0":
        if zd and "B0_ALLOW_ACTIONS" not in mut:
            mf.append("ZERO DOOR decision/action event in B0")
    else:
        strict = group == "BM" or "NO_GROUP_SOURCE" not in mut
        allowed = {"B1": {"decision_rules"}, "B2": {"decision_llm"}, "B3": {"decision_single_llm"}, "BM": {"operator_console"}}[group]
        llm_src = {"B2": {"decision_llm"}, "B3": {"decision_single_llm"}}.get(group, set())
        decs = {}
        for e in zd:
            if e["event_type"] == "DECISION":
                fb_ok = group in ("B2", "B3") and e["source_component"] == "decision_rules" and e["payload"]["fallback"]
                if e["source_component"] not in allowed and not fb_ok and (strict or group == "BM"):
                    mf.append(f"decision source {e['source_component']}")
                decs[e["decision_id"]] = e
            elif e["event_type"] == "LLM_CALL" and e["source_component"] not in llm_src and (group in ("B1", "BM") or strict):
                mf.append(f"LLM_CALL from {e['source_component']}")
        for e in zd:
            if e["event_type"] != "HEAL_STARTED":
                continue
            want = "OPERATOR" if group == "BM" else "AUTO"
            if e["payload"]["initiator"] != want and (group == "BM" or strict):
                mf.append(f"initiator {e['payload']['initiator']}")
            d = decs.get(e["decision_id"])
            if "ACTION_DECISION_UNCHECKED" not in mut and (d is None or d["payload"]["stage"] != "PROPOSAL" or d["payload"]["response_kind"] != "ACTION"):
                mf.append("action without a known PROPOSAL decision")
    out["mode_violation"], out["mode_findings"] = bool(mf), mf
    # leak [8.3]
    gts = by("GROUND_TRUTH_LOCKED")
    gt = gts[0]["payload"] if gts else {}
    manifests = {e["trial_id"]: e["payload"] for e in by("HARNESS_MANIFEST")}
    terms = {tok(x) for x in (gt.get("case_class"), gt.get("variant_id"), gt.get("cause")) if x}
    terms |= {tok(e["payload"]["fault_params"].get("attack_type")) for e in by("ATTACK_REQUESTED") if e["payload"]["fault_params"].get("attack_type")}
    for m in manifests.values():
        terms |= {tok(x) for x in m["reveal_terms"] if isinstance(x, str) and len(x) >= 4}
    canary = run["payload"]["canary_token"]
    findings, unknown = [], set()

    def keys(o):
        if isinstance(o, dict):
            for kk, v in o.items():
                yield kk
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)

    def flat(o, path):
        if isinstance(o, dict):
            for kk, v in o.items():
                yield from flat(v, f"{path}.{kk}" if path else kk)
        elif isinstance(o, list):
            for v in o:
                yield from flat(v, path)
        elif o is not None:
            yield path, str(o)
    oev = [e for e in events if isinstance(e, dict) and e.get("plane") == "O"]
    surfaces = []
    for e in oev:
        pl = e.get("payload") if isinstance(e.get("payload"), dict) else {}
        if "NO_ID_SCAN" not in mut:
            findings += [f"id-format {f}" for f in bad_ids(e)]
            idents = [str(e.get(f)) for f in ID_FIELDS if e.get(f)] + [str(e.get("stream", "")), str(e.get("source_instance", ""))] + \
                     [str(v) for v in (e.get("target") or {}).values() if v]
            findings += [f"label-in-id {lb}" for lb in terms for s in idents if lb in tok(s)]
        findings += [f"forbidden-key {kk}" for kk in keys(e.get("payload")) if kk in FORBIDDEN_O_KEYS]
        psha = pl.get("prompt_sha256")
        text = prompts.get(psha or "", "")
        if psha and psha not in prompts:
            unknown.add("stored prompt missing")
        if canary in json.dumps(e) + text:
            findings.append("canary")
        surfaces += [(e.get("source_component"), p_, v_) for p_, v_ in flat(e, "")]
        if text:
            surfaces.append((e.get("source_component"), "prompt", text))
    if "LEAK_NO_RESOURCE_CHECK" not in mut:
        for tid in trials:
            if tid not in manifests:
                unknown.add("harness manifest missing")
        for m in manifests.values():
            for en in m["entries"]:
                v = str(en.get("value", ""))
                occ = [(s_, p_) for s_, p_, val in surfaces if v and v in val]
                if "LEAK_ANY_HARNESS_VALUE" in mut:
                    findings += [f"harness-value {v}"] if occ else []
                    continue
                reveals = any(lb in tok(v) for lb in terms) or canary in v
                cls = en.get("class")
                if cls == "SECRET" and (occ or en.get("o_visible")):
                    findings.append(f"harness-secret-in-o {en.get('kind')}")
                elif cls == "NEUTRAL" and reveals and (occ or en.get("o_visible")):
                    findings.append(f"harness-identifier-reveals {en.get('kind')}")
                elif cls == "OBSERVABLE":
                    allow = {(a.get("source_component"), a.get("field")) for a in en.get("allowed_o", [])}
                    findings += [f"observable-outside-allowlist {s_}:{p_}" for s_, p_ in occ if (s_, p_) not in allow]
                elif cls not in ("SECRET", "NEUTRAL", "OBSERVABLE"):
                    unknown.add("manifest entry without class")
    saw = False
    if group == "BM":
        for tid, (ts0, ts1) in trials.items():
            cov = [e for e in by("AUDIT_COVERAGE") if e["payload"]["complete"] and sec(e["payload"]["from"]) <= ts0 and sec(e["payload"]["to"]) >= ts1]
            if not cov:
                unknown.add("BM audit coverage missing")
            for e in by("SCHEDULE_ACCESS"):
                if e["payload"]["actor_role"] == "OPERATOR" and tid in e["payload"]["scope_trial_ids"] and sec(e["payload"]["accessed_at"]) < ts1:
                    saw = True
                    findings.append("operator-saw-schedule")
    out["leak"] = "LEAK_DETECTED" if findings else ("UNKNOWN" if unknown else "CLEAN")
    bm_unknown = "BM audit coverage missing" in unknown
    out["operator_saw_schedule_before_trial"] = saw if not (bm_unknown and not saw) else "UNKNOWN"
    out["findings"], out["leak_unknown"] = findings, sorted(unknown)
    return out


# ---------------------------------------------------------------- compare
def case_view(cid, res, meta):
    v = {k: res[k] for k in ("duplicates_dropped", "integrity_errors", "orphans", "source_violations", "mode_violation", "leak",
                              "operator_saw_schedule_before_trial", "ambiguous", "unscoped", "foreign", "invalid_events")}
    v["rejected_types"] = sorted({t for t, _ in res["schema_errors"]})
    by_id = {r["incident_id"]: r for r in res["incidents"]}
    order = [by_id.get(i) for i in meta["incidents"]]
    if order and order[0]:
        v.update({k: order[0][k] for k in order[0] if k != "incident_id"})
    v["labels"] = [o["label"] if o else None for o in order]
    v["links"] = {f"d{j}": meta["incidents"].index(res["links"][eid]) for j, eid in enumerate(meta["detects"]) if eid in res["links"]}
    return v


def run_all(mut=frozenset(), verbose=False):
    bad, total, effects = [], 0, {}
    for c in FIX["cases"]:
        spec = copy.deepcopy(FIX["base"])
        spec.update(c["over"])
        recs, prompts, meta = build(c["id"], spec)
        res = analyse(recs, prompts, mut)
        if res["schema_errors"] and "rejected_types" not in c["expected"]:
            bad.append((c["id"], "schema_errors", [], res["schema_errors"][:2]))
        view = case_view(c["id"], res, meta)
        effects[c["id"]] = [r["effect"] for r in res["incidents"]]
        for k, exp in c["expected"].items():
            total += 1
            act = view.get(k)
            if act != exp:
                bad.append((c["id"], k, exp, act))
            elif verbose:
                print(f"OK   {c['id']:5} {k} = {act}")
    for a in FIX["aggregates"]:
        eff = [x for cid in a["cases"] for x in effects[cid]]
        req, conf = len(eff), eff.count("CONFIRMED")
        noeff, unk = eff.count("CONFIRMED_NO_EFFECT"), eff.count("UNKNOWN_EFFECT")
        n = conf if "UNKNOWN_LEAVES_N" in mut else req - noeff
        view = {"requested": req, "confirmed": conf, "no_effect": noeff, "unknown_effect": unk, "n": n,
                "status": "EMPTY" if req == 0 else ("NO_ELIGIBLE" if n == 0 else "NONEMPTY")}
        for k, exp in a["expected"].items():
            total += 1
            if view[k] != exp:
                bad.append((a["id"], k, exp, view[k]))
            elif verbose:
                print(f"OK   {a['id']:5} {k} = {view[k]}")
    return total, bad



if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    total, bad = run_all(verbose=sys.argv[1:] == ["cases"])
    print(f"CONTROL {total-len(bad)}/{total}", flush=True)
    for failure in bad: print("FAIL", failure)
    caught = 0
    if sys.argv[1:] != ["cases"]:
        for name in MUTANTS:
            _, failures = run_all(frozenset({name}))
            caught += bool(failures)
            print(("CAUGHT " if failures else "MISSED ")+name, flush=True)
        print(f"MUTANTS {caught}/{len(MUTANTS)}", flush=True)
    sys.exit(0 if not bad and (sys.argv[1:] == ["cases"] or caught == len(MUTANTS)) else 1)
