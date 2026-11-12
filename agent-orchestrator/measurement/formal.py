"""Offline scoring and evidence checks for the locked ZER-53 method."""
import hashlib
import json
from pathlib import Path

from event_pipeline.audit import audit
from event_pipeline.formal_capture import METHOD, is_sha256, parameters

from .clock import duration, parse
from .metrics import first_decision, ratio
from .recovery import joined

PROTOCOL_SHA256 = "c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8"
NOT_EVALUABLE = "NOT_EVALUABLE_BY_DESIGN"
F01 = {"delta_s": 5, "gap_s": 10, "k": 3, "s_s": 30, "l_ms": 2000,
       "eps_s": 1, "cap_det_s": 150, "cap_rec_s": 270}
WINDOW_MS = 330_000
INTERVAL_MS = 5_000
AUDIT_SURFACES = frozenset(("topics", "pod_names", "labels", "paths", "prompts", "logs",
                            "dashboards", "query_results"))


class FormalEvidenceError(ValueError):
    pass


def read_evidence(path, h, o, *, audit_directory=None):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("method_version") != METHOD or data.get("protocol_sha256") != PROTOCOL_SHA256:
        raise FormalEvidenceError("expected evidence for the locked ZER-53 protocol")
    if o is None or data.get("h_export_json_sha256") != h.meta_sha256 or data.get("o_export_json_sha256") != o.meta_sha256:
        raise FormalEvidenceError("evaluator evidence does not match both sealed exports")
    trials = data.get("trials")
    if not isinstance(trials, dict) or not trials:
        raise FormalEvidenceError("expected a nonempty evaluator trial map")
    for trial_id, entry in trials.items():
        if (not isinstance(entry, dict) or entry.get("case") not in ("C0", "C5")
                or type(entry.get("decision_coverage")) is not bool
                or not isinstance(entry.get("continuous_flow"), str) or not entry["continuous_flow"]):
            raise FormalEvidenceError(f"invalid evaluator entry for trial {trial_id}")
    resolver = data.get("resolver_sha256")
    if resolver is not None and not is_sha256(resolver):
        raise FormalEvidenceError("invalid resolver pin")
    directory = Path(audit_directory) if audit_directory else None
    normalized = {}
    for trial_id, entry in trials.items():
        artifacts, material = read_audit_artifacts(entry.get("audit_review"), directory, h.run_id, trial_id)
        normalized[trial_id] = dict(entry, resolver_sha256=resolver, audit_artifacts=artifacts,
                                    audit_material=material)
    return normalized, hashlib.sha256(raw).hexdigest()


def read_audit_artifacts(review, directory, run_id, trial_id):
    """Read the exact hashed bytes used in the audit and bind them to their review scope."""
    references = review.get("surface_evidence_sha256") if isinstance(review, dict) else None
    if not isinstance(references, dict):
        return {}, []
    surfaces = AUDIT_SURFACES & references.keys()
    if review.get("run_id") != run_id or review.get("trial_id") != trial_id:
        return dict.fromkeys(surfaces, "SCOPE_MISMATCH"), []
    verdicts, material = {}, []
    for surface in sorted(surfaces):
        digest = references[surface]
        if not is_sha256(digest):
            verdicts[surface] = "INVALID_REFERENCE"
            continue
        artifact = directory / digest if directory is not None else None
        try:
            if artifact is None or artifact.is_symlink() or not artifact.is_file():
                verdicts[surface] = "MISSING"
                continue
            raw = artifact.read_bytes()
        except OSError:
            verdicts[surface] = "UNREADABLE"
            continue
        if hashlib.sha256(raw).hexdigest() != digest:
            verdicts[surface] = "HASH_MISMATCH"
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            verdicts[surface] = "INVALID_CONTENT"
            continue
        if not isinstance(record, dict) or not isinstance(record.get("entries"), list):
            verdicts[surface] = "INVALID_CONTENT"
            continue
        if record.get("surface") != surface or any(
            record.get(key) != review.get(key) for key in ("run_id", "trial_id", "clock_id", "from", "to")
        ):
            verdicts[surface] = "SCOPE_MISMATCH"
            continue
        entries = record["entries"]
        if not all(isinstance(entry, dict) and all(isinstance(entry.get(key), str)
                   for key in ("source_component", "field", "text"))
                   and ("sha256" not in entry or isinstance(entry["sha256"], str)) for entry in entries):
            verdicts[surface] = "INVALID_CONTENT"
            continue
        verdicts[surface] = "VERIFIED"
        material.extend(entries)
    return verdicts, material


def access_covers_trial(h_events, trial_id, review):
    """Check the scope of the evaluator's access review and references to its source evidence."""
    starts = [e for e in h_events if e["event_type"] == "TRIAL_STARTED" and e["trial_id"] == trial_id]
    ends = [e for e in h_events if e["event_type"] == "TRIAL_ENDED" and e["trial_id"] == trial_id]
    runs = [e for e in h_events if e["event_type"] == "RUN_STARTED"]
    if len(starts) != 1 or len(ends) != 1 or len(runs) != 1:
        return False
    start, end, run = starts[0], ends[0], runs[0]
    clock = run["payload"]["reference_clock_id"]
    references = review.get("surface_evidence_sha256")
    evaluator = review.get("evaluator")
    if (review.get("run_id") != run["run_id"] or review.get("trial_id") != trial_id
            or not isinstance(evaluator, str) or not evaluator.strip()
            or review.get("clock_id") != clock
            or any(e["clock"]["clock_id"] != clock or e["clock"]["clock_source"] == "UNKNOWN" for e in (start, end))
            or not isinstance(references, dict) or references.keys() != AUDIT_SURFACES
            or not all(is_sha256(digest) for digest in references.values())):
        return False
    try:
        return parse(review.get("from")) <= parse(start["ts_event"]) < parse(end["ts_event"]) <= parse(review.get("to"))
    except ValueError:
        return False


def audit_trial(h_events, o_events, trial_id, review, artifacts, material):
    """Derive a trial verdict from sealed events and scoped, digest-checked audit material."""
    review = review if isinstance(review, dict) else {}
    artifacts_complete = (artifacts.keys() == AUDIT_SURFACES and
                          all(status == "VERIFIED" for status in artifacts.values()))
    result = audit(h_events, o_events, surfaces=material,
                   access_complete=artifacts_complete and access_covers_trial(h_events, trial_id, review))
    return dict(result, artifacts=artifacts)


def verify_run(scorer):
    starts = scorer.of("RUN_STARTED")
    is_formal = any(e.get("method_version") == METHOD for _, e in scorer.events)
    if not is_formal and scorer.formal_trials is None:
        return
    if scorer.formal_trials is None:
        raise FormalEvidenceError("formal runs require evaluator evidence")
    if (len(starts) != 1 or starts[0].get("method_version") != METHOD
            or any(event["method_version"] != METHOD for event in scorer.used)
            or starts[0]["payload"].get("protocol_ref") != "sha256:" + PROTOCOL_SHA256
            or scorer.group not in ("B0", "B1", "B2", "BM")
            or scorer.f01 is None or any(scorer.f01.get(k) != v for k, v in F01.items())):
        raise FormalEvidenceError("run does not match the locked method, protocol and measurement parameters")
    if set(scorer.formal_trials) != set(scorer.trial):
        raise FormalEvidenceError("evaluator trials do not match the trace trial IDs")
    for inc in scorer.inc.values():
        gt = inc["gt"]
        entry = scorer.formal_trials.get(inc["trial"])
        if entry is None or (gt is not None and gt.get("case_class") != entry["case"]):
            raise FormalEvidenceError("incident does not match the evaluator trial and case")
    for event in scorer.of("EFFECT_EVALUATED"):
        entry = scorer.formal_trials.get(event["trial_id"])
        if entry is not None and entry["case"] == "C0" and event["payload"]["status"] == "CONFIRMED":
            raise FormalEvidenceError("C0 trial contains a confirmed fault effect")


def bounded_duration(start, end):
    elapsed = duration(start, end)
    if elapsed is not None and elapsed[1] is not None and (start.clock_id == end.clock_id or elapsed[1] <= 500):
        return elapsed
    return None


def observe_flow(scorer, inc, flow):
    """Measure the scheduled continuous benign flow from T_req, independently of effect."""
    context = dict(inc, flow=flow, missing=set(), flags=set())
    stream, clock_id = scorer.stream(context)
    start = scorer.local(inc, inc["t_req"], clock_id) if stream else None
    if start is None:
        return {"status": "INSUFFICIENT_COVERAGE", "coverage_complete": False}
    request = inc["t_req"]
    probe_at_start = scorer.trial[inc["trial"]]["clock"].at(clock_id, start)
    if bounded_duration(request, probe_at_start) is None:
        return {"status": "INSUFFICIENT_COVERAGE", "coverage_complete": False}
    window = [sample for sample in stream if start <= sample["t"] < start + WINDOW_MS]
    slots = {(sample["t"] - start) // INTERVAL_MS for sample in window}
    expected = WINDOW_MS // INTERVAL_MS
    failures = [sample["event_id"] for sample in window if not sample["ok"]]
    complete = (len(slots) == len(window) == expected and not context["missing"]
                and "INVALID_EVENT" not in inc["missing"]
                and all(joined(a, b, 10_000) for a, b in zip(window, window[1:])))
    status = "BUSINESS_FAILURE_OBSERVED" if failures else (
        "NO_OUTAGE_OBSERVED" if complete else "INSUFFICIENT_COVERAGE")
    return {"status": status, "coverage_complete": complete, "observed_slots": len(slots),
            "expected_slots": expected, "failed_sample_ids": failures}


def score_decision(scorer, inc, row, entry):
    if row["label"] == "MISSING" or row["t_det_status"] == "CLOCK_UNVERIFIED":
        return "UNKNOWN", "UNKNOWN", "EVIDENCE_MISSING"
    decision, issue = first_decision(scorer, inc, row)
    if issue or not entry["decision_coverage"]:
        return "UNKNOWN", "UNKNOWN", issue or "DECISION_COVERAGE_MISSING"
    if row["t_det_status"] == "NONE":
        return "INCORRECT", "INCORRECT", "NO_TRIGGER"
    if decision is None:
        return "UNKNOWN", "UNKNOWN", "FIRST_DECISION_MISSING"
    if bounded_duration(inc["t_det"], scorer.stamp_of(decision)) is None:
        return "UNKNOWN", "UNKNOWN", "DECISION_CLOCK_UNVERIFIED"
    payload = decision["payload"]
    if payload["fallback"]:
        return "INCORRECT", "INCORRECT", "RULES_FALLBACK"
    if payload["response_kind"] != "ACTION":
        return "INCORRECT", "INCORRECT", payload["response_kind"]
    if payload["proposal"]["action_type"] != "BLOCK_IP":
        return "INCORRECT", "INCORRECT", "WRONG_ACTION"
    receipt = payload.get("pre_guard")
    if not isinstance(receipt, dict) or receipt.get("decision_event_id") != decision["event_id"]:
        return "UNKNOWN", "CORRECT", "PRE_GUARD_RECORD_MISSING"
    pin = entry.get("resolver_sha256")
    if not is_sha256(pin) or receipt.get("resolver_sha256") != pin:
        return "UNKNOWN", "CORRECT", "RESOLVER_PIN_UNVERIFIED"
    if receipt.get("status") in ("RESOLVER_ERROR", "OBSERVATION_MISSING"):
        return "INCORRECT", "CORRECT", receipt["status"]
    expected, actual = parameters(entry.get("expected")), parameters(receipt)
    if receipt.get("status") != "RESOLVED" or expected is None or expected[2] != 180 or actual is None:
        return "UNKNOWN", "CORRECT", "PRE_GUARD_FIELDS_UNVERIFIED"
    return ("CORRECT", "CORRECT", None) if actual == expected else ("INCORRECT", "CORRECT", "WRONG_PARAMETERS")


def counts(rows, key):
    n = len(rows)
    if not n:
        return {"status": "NO_ELIGIBLE", "N": 0}
    good = sum(row[key] == "CORRECT" for row in rows)
    unknown = sum(row[key] == "UNKNOWN" for row in rows)
    return {"status": "OK", "N": n, "numerator": good, "unknown": unknown,
            "bounds": [ratio(good, n), ratio(good + unknown, n)]}


def decision_summary(scorer, scored):
    if scorer.group not in ("B1", "B2"):
        return {key: {"status": "N/A"} for key in ("M1", "M1_enum", "M1c")}
    incidents = {}
    for row in scored["incidents"]:
        incidents.setdefault(row["trial_id"], []).append(row)
    rows = []
    for trial_id, entry in scorer.formal_trials.items():
        if entry["case"] != "C5":
            continue
        trial_rows = incidents.get(trial_id, [])
        row = trial_rows[0] if len(trial_rows) == 1 else None
        trial = scorer.trial[trial_id]
        clean = scored["leak"].get(trial_id, {}).get("result") == "CLEAN"
        base = {"trial_id": trial_id, "attempted": bool(trial["start"]), "audit_clean": clean,
                "incident_id": row and row["incident_id"]}
        if not base["attempted"] or not clean or (row and row["label"] == "CONFIRMED_NO_EFFECT"):
            rows.append(dict(base, eligible=False))
            continue
        inc = scorer.inc[row["incident_id"]] if row else None
        primary, enum, reason = (score_decision(scorer, inc, row, entry) if row else
                                 ("UNKNOWN", "UNKNOWN", "INCIDENT_NOT_UNIQUE"))
        triggered = bool(row and row["t_det_status"] == "OBSERVED" and row["label"] != "MISSING")
        rows.append(dict(base, eligible=True, M1=primary, M1_enum=enum, reason=reason, triggered=triggered,
                         confirmed=bool(row and row["effect"] == "CONFIRMED")))
    eligible = [row for row in rows if row["eligible"]]
    triggered = [row for row in eligible if row["triggered"]]
    clear = [row for row in triggered if row["confirmed"]]
    m1c = counts(clear, "M1") if clear else {"status": "N/A", "N": 0}
    return {"rows": rows, "M1": counts(eligible, "M1"), "M1_enum": counts(eligible, "M1_enum"),
            "M1c": dict(m1c, triggered=len(triggered), cohort_N=len(eligible),
                        scorable=sum(row["M1"] != "UNKNOWN" for row in clear))}
