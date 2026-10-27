"""ZER-42 SQLi executor offline / runtime-prep harness. OFFLINE ONLY: this never sends a request and never
runs a lab; `--help` and import have no side effect beyond adding the repo's agent-orchestrator to sys.path.

It holds the H-plane effect evaluator, kept strictly separate from the Go executor. The evaluator reads the
executor's raw FAULT_EXECUTOR_RESULT observation (AttackResult.details.sqli) plus the ZER-41 oracle, and
produces an EFFECT_EVALUATED payload/event per the locked contract. Rules (Hoàng-locked):
  * CONFIRMED only when a clean, well-formed send actually returned a restricted seed row — never on HTTP 200
    alone, never on a malformed body, never on a log line containing "SQL". t_eff is the observed instant of
    that disclosing send (not the command start), on the executor's named clock.
  * CONFIRMED_NO_EFFECT only when clean, well-formed sends cover the evaluation window [T_req, T_req + W_eff]
    with no gap and no errored/malformed send inside it — and only with a verified clock and valid parameters.
  * otherwise UNKNOWN_EFFECT (errors/timeouts/thin coverage/missing time/invalid params never collapse to "no
    effect").
emit_evidence threads one executor result into plane-H evidence end to end: a FAULT_EXECUTOR_RESULT and a
causally-linked EFFECT_EVALUATED, each validated by the locked contract and handed to a plain sink callable
(no broker, no Kafka). It emits no O-plane event and never copies the seed, the oracle, the template label or
any expected answer into an event payload; evidence carries only what was actually observed.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline import contract  # noqa: E402
from event_pipeline.store import Archive, fsync_dir  # noqa: E402
from measurement.raw import Export  # noqa: E402

EXPECTED = ROOT / "tests/fixtures/zer41/expected.json"
CRITERIA_VERSION = "zer41-restricted/1"
DEFAULT_GAP_S = 2  # window-coverage gap tolerance (s): a 1-rps clean stream joins; a sparse window does not

_STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$")


def oracle_restricted():
    """The restricted seed SKUs an injection discloses on the vulnerable profile (the H-side oracle)."""
    data = json.loads(EXPECTED.read_text())
    return frozenset(data["injection"]["vulnerable_returns_restricted"])


def _epoch_ms(stamp):
    """RFC3339/ISO-8601 stamp -> epoch milliseconds, or None if absent/unparseable. Nanosecond fractions are
    truncated to microseconds so a Go RFC3339Nano stamp parses with the stdlib."""
    if not isinstance(stamp, str):
        return None
    m = _STAMP.match(stamp)
    if not m:
        return None
    frac = (m.group(3) or "")[:6].ljust(6, "0")
    offset = "+00:00" if m.group(4) == "Z" else m.group(4)
    try:
        instant = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}.{frac}{offset}")
        delta = instant - datetime(1970, 1, 1, tzinfo=timezone.utc)
        return (delta.days * 86400 + delta.seconds) * 1000 + delta.microseconds // 1000
    except ValueError:
        return None


def _is_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _usable(send):
    """A send is usable evidence only if it is a well-formed clean 200: no error, integer non-negative rows and
    restrictedRows with restrictedRows <= rows, and a restrictedSkus list whose length matches restrictedRows.
    A malformed 200 (the Go executor marks it error=SCHEMA, but we re-check independently) is not usable."""
    if not isinstance(send, dict) or send.get("error") or type(send.get("status")) is not int or send["status"] != 200:
        return False
    rows, restricted = send.get("rows"), send.get("restrictedRows")
    if type(rows) is not int or type(restricted) is not int or rows < 0 or restricted < 0 or restricted > rows:
        return False
    skus = send.get("restrictedSkus")
    if skus is None:
        return restricted == 0  # Go omits the empty list, never the positive evidence.
    if not isinstance(skus, list) or len(skus) != restricted or any(not isinstance(s, str) or not s for s in skus):
        return False
    return True


def evaluate_effect(result, *, oracle, min_clean_sends, w_eff_s, evidence_clock_id=None,
                    gap_s=DEFAULT_GAP_S, criteria_version=CRITERIA_VERSION):
    """Pure effect decision from one executor result. Returns an EFFECT_EVALUATED payload dict."""
    result = result if isinstance(result, dict) else {}
    details = result.get("details")
    details = details if isinstance(details, dict) else {}
    sqli = details.get("sqli")
    sqli = sqli if isinstance(sqli, dict) else {}
    raw_sends = sqli.get("sends")
    sends = raw_sends if isinstance(raw_sends, list) else []
    clock_id = sqli.get("clockId") or evidence_clock_id
    clock_source = sqli.get("clockSource")
    t_req = _epoch_ms(sqli.get("windowStart"))

    clean = [s for s in sends if _usable(s)]
    disclosing = [s for s in clean if set(s.get("restrictedSkus") or []) & oracle]
    restricted_seen = set()
    for s in clean:
        restricted_seen |= set(s.get("restrictedSkus") or [])
    evidence = {"sends": len(sends), "clean_sends": len(clean), "disclosing_sends": len(disclosing),
                "restricted_rows_seen": sorted(restricted_seen), "clock_source": clock_source,
                "executor_status": result.get("status")}

    def payload(status, t_eff, reason):
        return {"status": status, "t_eff": t_eff, "evidence_clock_id": clock_id,
                "criteria_version": criteria_version, "w_eff_s": w_eff_s if _is_number(w_eff_s) else None,
                "evidence": evidence, "reason": reason}

    # No cross-host assertion is made here: all raw stamps must use this observation's
    # named executor clock. UNKNOWN clock_source does not invalidate same-clock spans.
    if type(min_clean_sends) is not int or min_clean_sends < 1 or not _is_number(w_eff_s) or w_eff_s <= 0 \
            or not _is_number(gap_s) or gap_s <= 0 or not isinstance(clock_id, str) or not clock_id:
        return payload("UNKNOWN_EFFECT", None, "invalid evaluation parameters or missing clock")
    if not isinstance(raw_sends, list) or not sends or len(sends) > 20:
        return payload("UNKNOWN_EFFECT", None, "missing or malformed send collection")
    sequences = set()
    for send in sends:
        if not isinstance(send, dict):
            return payload("UNKNOWN_EFFECT", None, "malformed send entry")
        seq = send.get("seq")
        if type(seq) is not int or seq < 1 or seq in sequences:
            return payload("UNKNOWN_EFFECT", None, "missing or duplicate send sequence")
        sequences.add(seq)
        started, observed = _epoch_ms(send.get("startedAt")), _epoch_ms(send.get("observedAt"))
        if started is None or observed is None or observed < started:
            return payload("UNKNOWN_EFFECT", None, "send evidence time missing or inconsistent")

    if disclosing:
        # t_eff is the observed instant of the earliest disclosing send; a disclosure without a parseable time or
        # a named clock cannot be stamped, so it is UNKNOWN rather than a CONFIRMED with an invented time.
        dated = sorted((s for s in disclosing if _epoch_ms(s.get("observedAt")) is not None),
                       key=lambda s: _epoch_ms(s.get("observedAt")))
        if not dated or not clock_id:
            return payload("UNKNOWN_EFFECT", None, "disclosure observed but no verified evidence time or clock")
        instant = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=_epoch_ms(dated[0]["observedAt"]))
        return payload("CONFIRMED", instant.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                       "restricted seed rows returned by a clean send")
    if restricted_seen:
        # A restricted row that is not a known oracle row is anomalous; never call that a clean "no effect".
        return payload("UNKNOWN_EFFECT", None, "restricted rows observed that are outside the oracle")

    # CONFIRMED_NO_EFFECT needs a verified clock, valid parameters, and clean coverage of the whole window with no
    # errored/malformed send inside it (mirrors measurement.scorer.no_effect's raw-sample coverage check).
    if type(min_clean_sends) is not int or isinstance(min_clean_sends, bool) or min_clean_sends < 1 \
            or not _is_number(w_eff_s) or w_eff_s <= 0 or t_req is None or not clock_id:
        return payload("UNKNOWN_EFFECT", None, "insufficient parameters or clock to evaluate the window")
    end, gap = t_req + w_eff_s * 1000, gap_s * 1000
    in_window = [s for s in sends
                 if _epoch_ms(s.get("observedAt")) is not None and t_req <= _epoch_ms(s.get("observedAt")) <= end]
    if any(not _usable(s) for s in in_window):
        return payload("UNKNOWN_EFFECT", None, "an errored or malformed send falls inside the evaluation window")
    window = sorted((s for s in clean
                     if _epoch_ms(s.get("observedAt")) is not None and t_req <= _epoch_ms(s.get("observedAt")) <= end),
                    key=lambda s: _epoch_ms(s.get("observedAt")))
    times = [_epoch_ms(s.get("observedAt")) for s in window]
    covered = bool(window) and len(window) >= min_clean_sends and times[0] - t_req <= gap and end - times[-1] <= gap \
        and all(b - a <= gap for a, b in zip(times, times[1:]))
    if not covered:
        return payload("UNKNOWN_EFFECT", None, "clean coverage does not span the evaluation window")
    return payload("CONFIRMED_NO_EFFECT", None, "clean coverage spans the window, no restricted row returned")


def build_event(context, payload, clock, producer_version="zer42-eval/0.1", **ids):
    """Build and validate a well-formed EFFECT_EVALUATED (plane H, source effect_evaluator) from a payload."""
    producer = contract.Producer("effect_evaluator", producer_version, clock)
    return producer.event(context, "EFFECT_EVALUATED", payload, stream="h-effect", **ids)


def build_fault_result(context, result, clock, producer_version="zer42-exec/0.1"):
    """Build and validate a FAULT_EXECUTOR_RESULT (plane H, source fault_executor) from the executor result.
    Carries the complete bounded executor observation plus its canonical hash. The raw observation is evidence,
    not an effect verdict; the H evaluator owns that decision and the oracle never enters this event."""
    payload = {"executor_status": (result or {}).get("status"),
               "command_ref": (result or {}).get("commandId"),
               "duration_ms": (result or {}).get("duration"),
               "raw_result": deepcopy(result), "raw_result_sha256": digest(result)}
    producer = contract.Producer("fault_executor", producer_version, clock)
    return producer.event(context, "FAULT_EXECUTOR_RESULT", payload, stream="h-fault")


def executor_clock(result):
    """The clock dict for the producer, taken from the executor's declared clock (contract clock_source enum)."""
    sqli = ((result or {}).get("details") or {}).get("sqli") or {}
    return {"clock_id": sqli.get("clockId") or "chaos-worker-local",
            "clock_source": sqli.get("clockSource") if sqli.get("clockSource") in {"HOST_SHARED", "OFF_HOST", "UNKNOWN"} else "UNKNOWN",
            "resolution_ms": None}


def emit_evidence(result, context, clock=None, *, oracle=None, min_clean_sends=1, w_eff_s=5,
                  gap_s=DEFAULT_GAP_S, sink=None):
    """Thread one executor result into plane-H evidence: a FAULT_EXECUTOR_RESULT, then a causally-linked
    EFFECT_EVALUATED (causation_id = the fault result's event_id). Each validated event is handed to `sink`
    (a plain callable; no broker/Kafka). Returns (fault_result, effect_evaluated). This is the offline
    entrypoint the SQLi tests exercise end to end — not a live path."""
    if oracle is None:
        oracle = oracle_restricted()
    if clock is None:
        clock = executor_clock(result)
    sink = sink or (lambda event: None)
    fault = build_fault_result(context, result, clock)
    fault["payload"]["evaluation"] = {"min_clean_sends": min_clean_sends, "w_eff_s": w_eff_s,
                                      "gap_s": gap_s, "oracle_sha256": digest(sorted(oracle))}
    sink(fault)
    payload = archive_payload(fault, oracle)
    effect = build_event(context, payload, clock, causation_id=fault["event_id"])
    sink(effect)
    return fault, effect


def digest(value):
    return hashlib.sha256(contract.canonical(value)).hexdigest()


def archive_payload(fault, oracle):
    """Executor raw is retained as executor evidence, never relabeled an independent probe.

    The local NO_EFFECT candidate cannot yet be recomputed by scorer.no_effect without
    independent PROBE_SAMPLE coverage. Keep this archive output UNKNOWN until that
    harness integration exists; the pure evaluator's local assessment remains visible.
    """
    p, params = fault["payload"], fault["payload"]["evaluation"]
    if params["oracle_sha256"] != digest(sorted(oracle)):
        raise ValueError("ORACLE_VERSION_MISMATCH")
    payload = evaluate_effect(p["raw_result"], oracle=oracle, min_clean_sends=params["min_clean_sends"],
                              w_eff_s=params["w_eff_s"], gap_s=params["gap_s"])
    payload["evidence"].update(raw_event_id=fault["event_id"], raw_result_sha256=p["raw_result_sha256"],
                                observation_source="fault_executor")
    if payload["status"] == "CONFIRMED_NO_EFFECT":
        payload["evidence"]["executor_assessment"] = "CONFIRMED_NO_EFFECT"
        payload["status"] = "UNKNOWN_EFFECT"
        payload["reason"] = "independent probe coverage required for scorer NO_EFFECT; executor raw retained"
    return payload


def verify_pair(events, oracle):
    """Validate roles, context, causation, raw hash and recomputed payload before replay/export."""
    if not isinstance(events, list) or len(events) != 2:
        raise ValueError("INVALID_EVIDENCE_PAIR")
    fault, effect = events
    for event, typ, role in ((fault, "FAULT_EXECUTOR_RESULT", "fault_executor"),
                             (effect, "EFFECT_EVALUATED", "effect_evaluator")):
        if contract.validate(event, "H", role) or event["event_type"] != typ:
            raise ValueError("INVALID_EVIDENCE_EVENT")
    keys = ("run_id", "trial_id", "incident_id", "group", "method_version", "config_ref", "clock")
    if any(fault.get(k) != effect.get(k) for k in keys) or effect["causation_id"] != fault["event_id"]:
        raise ValueError("EVIDENCE_CONTEXT_CONFLICT")
    p, raw = fault["payload"], fault["payload"]["raw_result"]
    if p["raw_result_sha256"] != digest(raw) or p["command_ref"] != raw.get("commandId") \
            or p["executor_status"] != raw.get("status") or p["duration_ms"] != raw.get("duration"):
        raise ValueError("RAW_RESULT_CONFLICT")
    if effect["payload"] != archive_payload(fault, oracle):
        raise ValueError("EFFECT_RECOMPUTATION_MISMATCH")
    return fault, effect


def prepare_bundle(result, context, path, *, oracle=None, min_clean_sends=1, w_eff_s=5, gap_s=DEFAULT_GAP_S):
    """Durable local outbox, written before ingest. Retry uses the SAME saved envelopes.

    One writer per checkout/archive. Existing conflicting or partial files are refused,
    never repaired or overwritten. Creation failure preserves bytes for the operator.
    """
    oracle = oracle_restricted() if oracle is None else oracle
    binding = {"result_sha256": digest(result), "context": context, "min_clean_sends": min_clean_sends,
               "w_eff_s": w_eff_s, "gap_s": gap_s, "oracle_sha256": digest(sorted(oracle))}
    path = Path(path)
    if path.is_symlink():
        raise ValueError("UNSAFE_BUNDLE_PATH")
    try:
        saved = json.loads(path.read_bytes())
    except FileNotFoundError:
        events = list(emit_evidence(result, context, oracle=oracle, min_clean_sends=min_clean_sends,
                                    w_eff_s=w_eff_s, gap_s=gap_s))
        verify_pair(events, oracle)
        saved = {"format": "zer42-h-bundle/1", "binding": binding, "events": events}
        with open(path, "xb") as out:
            out.write(contract.canonical(saved) + b"\n")
            out.flush()
            os.fsync(out.fileno())
        fsync_dir(path.parent)
    if saved.get("format") != "zer42-h-bundle/1" or saved.get("binding") != binding:
        raise ValueError("BUNDLE_BINDING_CONFLICT")
    fault, _ = verify_pair(saved["events"], oracle)
    if fault["payload"]["raw_result_sha256"] != binding["result_sha256"] \
            or any(fault.get(k) != v for k, v in context.items()):
        raise ValueError("BUNDLE_BINDING_CONFLICT")
    return saved


def archive_bundle(bundle, archive_root, destination, *, oracle=None):
    """Append/fsync through the existing H Archive and return only after verified export.

    On failure the saved bundle is retained. Retry it unchanged. Exact duplicate events
    remain one logical event; a sealed exact replay is accepted by the existing archive.
    The destination must be NEW; partial destinations are preserved, never overwritten.
    """
    oracle = oracle_restricted() if oracle is None else oracle
    fault, effect = verify_pair(bundle["events"], oracle)
    archive = Archive(archive_root, "H")
    try:
        for event in (fault, effect):
            archive.ingest(event, "zer42-local-bundle", event["source_component"])
        archive.export(fault["run_id"], destination)
    finally:
        archive.close()
    return recheck_export(destination, oracle=oracle)


def recheck_export(destination, *, oracle=None):
    """Use the scorer's verified export loader, then recompute from retained executor raw."""
    oracle = oracle_restricted() if oracle is None else oracle
    exported = Export(destination, "H")
    unique = {r["envelope"]["event_id"]: r["envelope"] for r in exported.records}
    checked = []
    for fault in unique.values():
        if fault["event_type"] != "FAULT_EXECUTOR_RESULT" or "raw_result" not in fault["payload"]:
            continue
        effects = [e for e in unique.values() if e["event_type"] == "EFFECT_EVALUATED"
                   and e["causation_id"] == fault["event_id"]]
        if len(effects) != 1:
            raise ValueError("EFFECT_PAIR_MISSING_OR_CONFLICTING")
        _, effect = verify_pair([fault, effects[0]], oracle)
        checked.append({"command_ref": fault["payload"]["command_ref"], "event_id": effect["event_id"],
                        "raw_result_sha256": fault["payload"]["raw_result_sha256"],
                        "status": effect["payload"]["status"]})
    if not checked:
        raise ValueError("NO_EXECUTOR_RAW_IN_EXPORT")
    return {"run_id": exported.run_id, "export_sha256": exported.meta_sha256, "checked": checked,
            "scope": "executor-result/H-export only; independent probe coverage and runtime pending"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ZER-42 SQLi executor offline / runtime-prep harness (no live effect).")
    ap.add_argument("--evaluate", metavar="RESULT_JSON",
                    help="evaluate one executor result JSON and print the EFFECT_EVALUATED payload")
    ap.add_argument("--min-clean-sends", type=int, default=1)
    ap.add_argument("--w-eff-s", type=int, default=5)
    ap.add_argument("--gap-s", type=int, default=DEFAULT_GAP_S)
    ap.add_argument("--evidence-clock-id", default=None,
                    help="fallback clock id when the result carries none (the result's own clockId wins)")
    ap.add_argument("--context", help="explicit H context JSON (needed with --bundle)")
    ap.add_argument("--bundle", help="write-once local H outbox JSON; retry this same path")
    ap.add_argument("--archive-root", help="local H Archive root; requires --bundle and --export")
    ap.add_argument("--export", help="NEW directory for the sealed H export")
    ap.add_argument("--recheck-export", help="verify and recompute an existing H export, read-only")
    args = ap.parse_args(argv)
    if args.recheck_export:
        print(json.dumps(recheck_export(args.recheck_export), indent=1))
        return 0
    if any((args.context, args.bundle, args.archive_root, args.export)):
        if not all((args.evaluate, args.context, args.bundle, args.archive_root, args.export)) or args.evidence_clock_id:
            ap.error("archive mode needs --evaluate/--context/--bundle/--archive-root/--export; no clock override")
        result = json.loads(Path(args.evaluate).read_bytes())
        bundle = prepare_bundle(result, json.loads(Path(args.context).read_bytes()), args.bundle,
                                min_clean_sends=args.min_clean_sends, w_eff_s=args.w_eff_s, gap_s=args.gap_s)
        print(json.dumps(archive_bundle(bundle, args.archive_root, args.export), indent=1))
        return 0
    if not args.evaluate:
        ap.print_help()
        return 0
    result = json.loads(Path(args.evaluate).read_text())
    payload = evaluate_effect(result, oracle=oracle_restricted(), min_clean_sends=args.min_clean_sends,
                              w_eff_s=args.w_eff_s, gap_s=args.gap_s, evidence_clock_id=args.evidence_clock_id)
    print(json.dumps(payload, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
