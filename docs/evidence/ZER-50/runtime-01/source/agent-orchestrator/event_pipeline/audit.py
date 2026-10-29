"""Offline H/O leak audit. A clean payload alone is never a complete access audit."""
import re
import hashlib

from .contract import forbidden_keys, validate

# Contract 8.3(4): lowercase; '-', '_', '.', whitespace, '/', ':', '=' are one separator.
SEPARATORS = re.compile(r"[-_.\s/:=]+")
# Contract 8.3(3): identifier fields of an O event scanned for case labels.
METADATA = ("event_id", "run_id", "trial_id", "incident_id", "alert_id", "decision_id", "action_id",
            "call_id", "causation_id", "stream", "source_instance", "target")


def token(value):
    return SEPARATORS.sub("-", str(value).lower())


def tokens(value):
    return tuple(part for part in SEPARATORS.split(str(value).lower()) if part)


def contains(text, label):
    """Label occurs as a whole run of tokens, never inside a token (e.g. 'c4' inside hex IDs)."""
    needle, hay = tokens(label), tokens(text)
    return bool(needle) and any(hay[i:i + len(needle)] == needle for i in range(len(hay) - len(needle) + 1))


def leaves(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, prefix + ("." if prefix else "") + key)
    elif isinstance(value, list):
        for child in value:
            yield from leaves(child, prefix)
    elif isinstance(value, str):
        yield prefix, value


def scalars(value):
    if isinstance(value, (list, tuple)):
        for child in value:
            yield from scalars(child)
    elif value is not None and not isinstance(value, (dict, bool)) and str(value):
        yield str(value)


def label_terms(h_events):
    """Every 8.3(3) term, collected before any O field is scanned."""
    labels = []
    for event in h_events:
        payload = event.get("payload") or {}
        if event.get("event_type") == "GROUND_TRUTH_LOCKED":
            for key in ("case_class", "variant_id", "cause"):
                labels.extend(scalars(payload.get(key)))
        if "attack_type" in payload:
            labels.extend(scalars(payload["attack_type"]))
        if event.get("event_type") == "HARNESS_MANIFEST":
            labels.extend(scalars(payload.get("reveal_terms", [])))
    return sorted(set(labels))


def audit(h_events, o_events, surfaces=(), access_complete=False):
    """surfaces: saved prompt/query results with source_component, field and text.

    Caller must supply actual runtime access evidence; default is UNKNOWN.
    This function never strips naturally observed IPs or request telemetry.
    """
    findings, unknown = [], []
    if len({e.get("trial_id") for e in o_events if e.get("trial_id")}) > 1:
        unknown.append("MIXED_TRIAL_SCOPE")
    manifests = [e for e in h_events if e.get("event_type") == "HARNESS_MANIFEST"]
    if not manifests:
        unknown.append("HARNESS_MANIFEST_MISSING")
    if not access_complete:
        unknown.append("ACCESS_EVIDENCE_MISSING")
    canaries = [e["payload"]["canary_token"] for e in h_events if e.get("event_type") == "RUN_STARTED"]
    labels = label_terms(h_events)
    material = []
    for event in o_events:
        error = validate(event, "O")
        if error:
            findings.append(error)
        if forbidden_keys(event):
            findings.append("FORBIDDEN_KEY")
        material.extend((event.get("source_component"), field, value) for field, value in leaves(event))
        # Each identifier field separately; no free-text telemetry keyword scan (8.3(3)).
        identifiers = [text for key in METADATA for _, text in leaves(event.get(key), key)]
        if any(contains(text, label) for text in identifiers for label in labels):
            findings.append("LABEL_IN_METADATA")
    material.extend((s["source_component"], s["field"], s["text"]) for s in surfaces)
    for _, _, value in material:
        if any(c and c in value for c in canaries):
            findings.append("CANARY")
    entries = []
    for manifest in manifests:
        entries.extend(manifest["payload"].get("entries", []))
    for entry in entries:
        value = token(entry["value"])
        matches = [(source, field) for source, field, text in material if value and value in token(text)]
        kind = entry["class"]
        if kind == "SECRET":
            # A SECRET that O never saw is a known class, not missing evidence.
            if entry.get("o_visible") or matches:
                findings.append("HARNESS_SECRET")
        elif kind == "NEUTRAL":
            # Labels by whole tokens (same cause as 8.3(3)); canary keeps its normalized substring rule.
            revealing = any(contains(entry["value"], label) for label in labels) or \
                any(c and token(c) in value for c in canaries)
            if revealing and (entry.get("o_visible") or matches):
                findings.append("REVEALING_RESOURCE")
        elif kind == "OBSERVABLE":
            allowed = {(item["source_component"], item["field"]) for item in entry.get("allowed_o", [])}
            if any(match not in allowed for match in matches):
                findings.append("OBSERVABLE_OUTSIDE_ALLOWLIST")
        else:
            unknown.append("UNKNOWN_MANIFEST_CLASS")
    # BM schedule access is evaluated per trial, without exposing it to the O service.
    for trial in {e.get("trial_id") for e in o_events if e.get("group") == "BM"}:
        ends = [e["ts_event"] for e in h_events if e.get("trial_id") == trial and e.get("event_type") == "TRIAL_ENDED"]
        starts = [e["ts_event"] for e in h_events if e.get("trial_id") == trial and e.get("event_type") == "TRIAL_STARTED"]
        coverage = [e["payload"] for e in h_events if e.get("event_type") == "AUDIT_COVERAGE"]
        if not starts or not ends or not any(c.get("complete") is True and c["from"] <= min(starts) and c["to"] >= max(ends) for c in coverage):
            unknown.append("BM_AUDIT_INCOMPLETE")
        for event in h_events:
            if event.get("event_type") == "SCHEDULE_ACCESS":
                p = event["payload"]
                if p.get("actor_role") == "OPERATOR" and trial in p.get("scope_trial_ids", []) and (not ends or p["accessed_at"] <= max(ends)):
                    findings.append("OPERATOR_SAW_SCHEDULE")
    prompts = set()
    for surface in surfaces:
        if surface.get("field") == "prompt":
            digest = hashlib.sha256(surface["text"].encode()).hexdigest()
            if surface.get("sha256") in {digest, "sha256:" + digest}:
                prompts.add(surface["sha256"])
            else:
                unknown.append("PROMPT_HASH_MISMATCH")
    if any(e.get("event_type") == "DECISION" and e["payload"].get("prompt_sha256") not in prompts for e in o_events if e.get("event_type") == "DECISION" and e["payload"].get("prompt_sha256")):
        unknown.append("PROMPT_MISSING")
    return {"result": "LEAK_DETECTED" if findings else "UNKNOWN" if unknown else "CLEAN",
            "findings": sorted(set(findings)), "unknown": sorted(set(unknown))}
