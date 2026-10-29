"""The transport subset of zd-event/1.0.0. Never infer missing provenance."""
import copy
import json
import math
import re
import threading
import uuid
from datetime import datetime, timezone

VERSION = "zd-event/1.0.0"
ID = re.compile(r"^(run|trl|inc|evt|alt|dec|act|cal|ing)_[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}$")
STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
FORBIDDEN = frozenset((
    "case_class", "variant_id", "variant_ref", "cause", "attack_type", "attack_command",
    "fault_params", "s_att", "decision_required", "acceptable_actions", "expected_action",
    "known_good_revision", "seed", "onset_offset_ms", "schedule", "schedule_ref",
    "canary_token", "t_eff", "t_rec", "recovery_verified_at", "probe_sample", "incident_score",
))
# Source is checked against the authenticated principal as well as this table.
SOURCES = {
    "RUN_STARTED": ("H", {"harness"}), "RUN_CLOSED": ("H", {"harness"}),
    "TRIAL_STARTED": ("H", {"harness"}), "TRIAL_ENDED": ("H", {"harness"}),
    "HARNESS_MANIFEST": ("H", {"harness"}), "GROUND_TRUTH_LOCKED": ("H", {"harness"}),
    "SCHEDULE_SEALED": ("H", {"harness"}), "SCHEDULE_ACCESS": ("H", {"harness"}),
    "AUDIT_COVERAGE": ("H", {"harness"}), "CLOCK_SYNC": ("H", {"harness", "probe"}),
    "ATTACK_REQUESTED": ("H", {"harness"}), "ATTACK_STOPPED": ("H", {"harness"}),
    "FAULT_EXECUTOR_RESULT": ("H", {"fault_executor"}),
    "EFFECT_EVALUATED": ("H", {"effect_evaluator"}),
    "PROBE_SAMPLE": ("H", {"probe"}), "PROBE_HEARTBEAT": ("H", {"probe"}),
    "RELAPSE": ("H", {"recovery_evaluator"}),
    "RECOVERY_VERIFIED": ("H", {"recovery_evaluator"}),
    "CONTAINMENT_VERIFIED": ("H", {"recovery_evaluator"}),
    "RUN_CONTEXT": ("O", {"harness"}), "TRIAL_CONTEXT": ("O", {"harness"}),
    "DETECTED": ("O", {"detector"}),
    "DECISION": ("O", {"decision_rules", "decision_llm", "decision_single_llm", "operator_console"}),
    "LLM_CALL": ("O", {"decision_llm", "decision_single_llm"}),
    "GUARD_VERDICT": ("O", {"guard"}),
    "HEAL_STARTED": ("O", {"executor"}), "API_ACCEPTED": ("O", {"executor"}),
    "ACTION_COMPLETED": ("O", {"executor"}),
    "INCIDENT_LINK": ("S", {"scorer"}), "INCIDENT_SCORE": ("S", {"scorer"}),
    "LEAK_CHECK": ("S", {"scorer"}),
}
REQUIRED_O = {
    "RUN_CONTEXT": set(), "TRIAL_CONTEXT": set(),
    "DETECTED": {"rule_id", "rule_version", "signature", "metric", "value", "threshold", "severity", "description"},
    "DECISION": {"stage", "decision_source", "inputs", "response_kind", "proposal", "fallback", "fallback_of", "prompt_version", "prompt_sha256", "evidence_package_version"},
    "LLM_CALL": {"attempt_no", "retry_reason", "provider", "model", "prompt_version", "prompt_sha256", "latency_ms", "outcome", "usage", "cost"},
    "GUARD_VERDICT": {"verdict", "reason_code", "guard_version"},
    "HEAL_STARTED": {"action_type", "params", "attempt_no", "retry_of", "initiator"},
    "API_ACCEPTED": {"api", "response_ref"},
    "ACTION_COMPLETED": {"status", "postcondition", "error"},
}
REQUIRED_H = {
    "RUN_STARTED": {"canary_token", "protocol_ref", "schedule_ref", "f01_params", "reference_clock_id"},
    "RUN_CLOSED": {"close_reason", "recorder_manifest_ref"},
    "TRIAL_STARTED": {"warmup_end", "planned_window", "probes"}, "TRIAL_ENDED": {"end_reason"},
    "HARNESS_MANIFEST": {"manifest_version", "allowlist_version", "reveal_terms", "entries"},
    "GROUND_TRUTH_LOCKED": {"variant_id", "case_class", "cause", "decision_required", "acceptable_actions", "constraints", "label_version", "reviewers", "locked_at"},
    "SCHEDULE_SEALED": {"schedule_sha256", "sealed_at", "generated_after_label_lock"},
    "SCHEDULE_ACCESS": {"actor_role", "scope_trial_ids", "accessed_at"},
    "AUDIT_COVERAGE": {"from", "to", "complete"},
    "CLOCK_SYNC": {"clock_id", "reference_clock_id", "offset_ms", "uncertainty_ms", "method", "measured_at"},
    "ATTACK_REQUESTED": {"variant_ref", "fault_params", "attack_command", "seed", "onset_offset_ms", "s_att", "known_good_revision", "target_services"},
    "ATTACK_STOPPED": {"stop_reason", "executor_confirmed"},
    "FAULT_EXECUTOR_RESULT": {"executor_status", "command_ref", "duration_ms"},
    "EFFECT_EVALUATED": {"status", "t_eff", "evidence_clock_id", "criteria_version", "w_eff_s", "evidence", "reason"},
    "PROBE_SAMPLE": {"probe_id", "flow", "sequence", "t_start", "t_end", "pass", "error_class", "latency_ms", "probe_version"},
    "PROBE_HEARTBEAT": {"probe_id", "flow", "last_sequence", "probe_version"},
    "RELAPSE": {"flow", "candidate_t_rec", "failing_sample_t", "rule_version"},
    "RECOVERY_VERIFIED": {"flow", "probe_id", "probe_version", "evidence_clock_id", "t_rec", "recovery_verified_at", "evidence_complete_at", "k", "s_s", "delta_s", "l_ms", "gap_s", "cap_rec_s", "sample_seq_range", "samples_sha256", "rule_version"},
    "CONTAINMENT_VERIFIED": {"blocked_source_ref", "enforcement_point", "fixture_probe_ref", "boutique_probe_ref", "t_contained"},
}
FIELDS = {"schema_version", "event_id", "event_type", "plane", "run_id", "trial_id", "causation_id",
          "group", "method_version", "config_ref", "source_component", "source_instance",
          "producer_version", "stream", "seq", "target", "clock", "ts_event", "payload"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def new_id(kind):
    return f"{kind}_{uuid.uuid4().hex}"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def valid_id(value, kind):
    return isinstance(value, str) and value.startswith(kind + "_") and bool(ID.fullmatch(value))


def forbidden_keys(value):
    if isinstance(value, dict):
        return any(str(k).lower() in FORBIDDEN or forbidden_keys(v) for k, v in value.items())
    if isinstance(value, list):
        return any(forbidden_keys(v) for v in value)
    return False


def validate(event, plane=None, source=None):
    try:
        return _validate(event, plane, source)
    except (KeyError, TypeError, ValueError, OverflowError):
        return "INVALID"


def _validate(event, plane=None, source=None):
    """Return classification; retain rejected envelopes separately, never forward them."""
    if not isinstance(event, dict) or not FIELDS <= event.keys():
        return "MISSING_FIELD"
    try:
        canonical(event)
    except (ValueError, TypeError):
        return "INVALID"
    if event["schema_version"] != VERSION:
        return "UNSUPPORTED"
    typ = event["event_type"]
    if not isinstance(typ, str) or typ not in SOURCES:
        return "UNSUPPORTED"
    expected_plane, allowed = SOURCES[typ]
    if event["plane"] != expected_plane or (plane and event["plane"] != plane):
        return "PLANE_VIOLATION"
    if event["source_component"] not in allowed or (source and event["source_component"] != source):
        return "SOURCE_VIOLATION"
    for field, kind in (("event_id", "evt"), ("run_id", "run"), ("trial_id", "trl"),
                        ("incident_id", "inc"), ("alert_id", "alt"), ("decision_id", "dec"),
                        ("action_id", "act"), ("call_id", "cal"), ("causation_id", "evt")):
        value = event.get(field)
        if value is not None and not valid_id(value, kind):
            return "INVALID_ID"
    if not valid_id(event["event_id"], "evt") or not valid_id(event["run_id"], "run"):
        return "INVALID_ID"
    if typ not in {"RUN_STARTED", "RUN_CLOSED", "RUN_CONTEXT", "GROUND_TRUTH_LOCKED", "SCHEDULE_SEALED", "AUDIT_COVERAGE", "PROBE_HEARTBEAT", "PROBE_SAMPLE"} and not valid_id(event.get("trial_id"), "trl"):
        return "MISSING_FIELD"
    for key in ("ts_event", "ts_publish"):
        if key in event:
            value = event[key]
            if not isinstance(value, str) or not STAMP.fullmatch(value):
                return "INVALID_TIMESTAMP"
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return "INVALID_TIMESTAMP"
    if event["group"] not in {"B0", "B1", "B2", "B3", "BM"}:
        return "INVALID"
    if type(event["seq"]) is not int or event["seq"] < 0:
        return "INVALID"
    if not isinstance(event["config_ref"], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", event["config_ref"]):
        return "INVALID"
    for key in ("method_version", "source_instance", "producer_version", "stream"):
        if not isinstance(event[key], str) or not event[key]:
            return "INVALID"
    clock = event["clock"]
    if not isinstance(clock, dict) or not {"clock_id", "clock_source", "resolution_ms"} <= clock.keys():
        return "MISSING_FIELD"
    if not isinstance(clock["clock_id"], str) or clock["clock_source"] not in {"HOST_SHARED", "OFF_HOST", "UNKNOWN"}:
        return "INVALID"
    resolution = clock["resolution_ms"]
    if resolution is not None and (type(resolution) not in (int, float) or not math.isfinite(resolution) or resolution <= 0):
        return "INVALID"
    p = event["payload"]
    if not isinstance(p, dict):
        return "INVALID"
    if typ in {"RUN_CONTEXT", "RUN_STARTED", "RUN_CLOSED"} and (event["trial_id"] is not None or event.get("incident_id") is not None):
        return "SEMANTIC"
    if typ == "TRIAL_CONTEXT" and not valid_id(event.get("trial_id"), "trl"):
        return "MISSING_FIELD"
    if typ in REQUIRED_O and not REQUIRED_O[typ] <= p.keys():
        return "MISSING_FIELD"
    if typ in REQUIRED_H and not REQUIRED_H[typ] <= p.keys():
        return "MISSING_FIELD"
    if typ in {"ATTACK_REQUESTED", "ATTACK_STOPPED", "FAULT_EXECUTOR_RESULT", "EFFECT_EVALUATED", "RELAPSE", "RECOVERY_VERIFIED", "CONTAINMENT_VERIFIED"} and not valid_id(event.get("incident_id"), "inc"):
        return "MISSING_FIELD"
    if typ == "EFFECT_EVALUATED" and (p["status"] not in {"CONFIRMED", "CONFIRMED_NO_EFFECT", "UNKNOWN_EFFECT"} or ((p["status"] == "CONFIRMED") != (p["t_eff"] is not None))):
        return "SEMANTIC"
    if expected_plane == "O":
        if forbidden_keys(event):
            return "LEAK_DETECTED"
        if typ in {"RUN_CONTEXT", "TRIAL_CONTEXT"} and p:
            return "LEAK_DETECTED"
        if typ == "DETECTED" and not valid_id(event.get("alert_id"), "alt"):
            return "MISSING_FIELD"
        if typ == "DETECTED":
            if any(not isinstance(p[key], str) or not p[key] for key in ("rule_id", "rule_version", "signature", "metric", "severity", "description")):
                return "INVALID"
            if any(type(p[key]) not in (int, float) for key in ("value", "threshold")):
                return "INVALID"
            if not isinstance(event["target"], dict) or not {"namespace", "service", "flow"} <= event["target"].keys():
                return "MISSING_FIELD"
        if typ in {"DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED"} and not valid_id(event.get("decision_id"), "dec"):
            return "MISSING_FIELD"
        if typ in {"HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED"} and not valid_id(event.get("action_id"), "act"):
            return "MISSING_FIELD"
        if typ == "ACTION_COMPLETED":
            post = p.get("postcondition")
            if not isinstance(post, dict) or not {"name", "checked", "satisfied", "observed"} <= post.keys():
                return "MISSING_FIELD"
            if p["status"] not in {"SUCCESS", "FAILED", "PARTIAL", "TIMEOUT"} or type(post["checked"]) is not bool or type(post["satisfied"]) is not bool:
                return "INVALID"
            if (p["status"] == "SUCCESS") != (post["checked"] and post["satisfied"]):
                return "SEMANTIC"
        if typ == "DECISION":
            expected = {"decision_rules": "RULES", "decision_llm": "LLM", "decision_single_llm": "SINGLE_LLM", "operator_console": "MANUAL"}[event["source_component"]]
            if p["decision_source"] != expected or p["stage"] not in {"ANALYSIS", "PROPOSAL"}:
                return "SEMANTIC"
            if p["response_kind"] not in {"ACTION", "NO_ACTION", "ABSTAIN", "SCHEMA_INVALID", "TIMEOUT", "REFUSAL"}:
                return "INVALID"
            if (p["proposal"] is not None) != (p["response_kind"] == "ACTION") or type(p["fallback"]) is not bool or p["fallback"] != (p["fallback_of"] is not None):
                return "SEMANTIC"
            if p["fallback"] and expected != "RULES":
                return "SEMANTIC"
            if not isinstance(p["inputs"], list) or any(not isinstance(i, dict) or not valid_id(i.get("event_id"), "evt") or not STAMP.fullmatch(i.get("received_at", "")) for i in p["inputs"]):
                return "INVALID"
            allowed = {"B1": {"RULES"}, "B2": {"RULES", "LLM"}, "B3": {"RULES", "SINGLE_LLM"}, "BM": {"MANUAL"}, "B0": set()}
            if expected not in allowed[event["group"]]:
                return "MODE_VIOLATION"
            if expected == "RULES" and event["group"] in {"B2", "B3"} and not p["fallback"]:
                return "MODE_VIOLATION"
            if p["fallback"] and (event["group"] not in {"B2", "B3"} or not valid_id(p["fallback_of"], "dec")):
                return "MODE_VIOLATION"
            if expected in {"LLM", "SINGLE_LLM"} and not p["prompt_sha256"]:
                return "MISSING_FIELD"
        if typ == "GUARD_VERDICT" and p["verdict"] not in {"ACCEPT", "REJECT"}:
            return "INVALID"
        if typ == "LLM_CALL":
            if not valid_id(event.get("call_id"), "cal"):
                return "MISSING_FIELD"
            if (event["group"], event["source_component"]) not in {("B2", "decision_llm"), ("B3", "decision_single_llm")}:
                return "MODE_VIOLATION"
        if typ == "HEAL_STARTED" and (type(p["attempt_no"]) is not int or p["attempt_no"] < 1 or (p["attempt_no"] > 1) != (p["retry_of"] is not None)):
            return "SEMANTIC"
        if event["group"] == "B0" and typ not in {"RUN_CONTEXT", "TRIAL_CONTEXT", "DETECTED"}:
            return "MODE_VIOLATION"
        if typ == "HEAL_STARTED" and ((event["group"] == "BM") != (p["initiator"] == "OPERATOR")):
            return "MODE_VIOLATION"
    return None


class Producer:
    """A new random instance on restart prevents seq reuse under the same owner."""
    def __init__(self, source, version, clock):
        self.source, self.version, self.clock = source, version, copy.deepcopy(clock)
        self.instance = "src-" + uuid.uuid4().hex
        self.sequences = {}
        self.lock = threading.Lock()

    def event(self, context, typ, payload, stream, target=None, **ids):
        with self.lock:
            seq = self.sequences.get(stream, 0)
            self.sequences[stream] = seq + 1
        event = {k: copy.deepcopy(context[k]) for k in ("run_id", "trial_id", "group", "method_version", "config_ref")}
        if context.get("incident_id") and typ in {"TRIAL_CONTEXT", "DETECTED", "DECISION", "LLM_CALL", "GUARD_VERDICT", "HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED", "ATTACK_REQUESTED", "ATTACK_STOPPED", "FAULT_EXECUTOR_RESULT", "EFFECT_EVALUATED", "RELAPSE", "RECOVERY_VERIFIED", "CONTAINMENT_VERIFIED", "INCIDENT_LINK", "INCIDENT_SCORE"}:
            event["incident_id"] = context["incident_id"]
        event.update(schema_version=VERSION, event_id=new_id("evt"), event_type=typ, plane=SOURCES[typ][0],
                     causation_id=None, source_component=self.source, source_instance=self.instance,
                     producer_version=self.version, stream=stream, seq=seq, target=copy.deepcopy(target),
                     clock=copy.deepcopy(self.clock), ts_event=now(), payload=copy.deepcopy(payload))
        event.update(ids)
        error = validate(event)
        if error:
            raise ValueError(error)
        return event
