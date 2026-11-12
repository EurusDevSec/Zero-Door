"""ZER-53 formal B2 wiring: durable budget claims, Gaia-then-Hephaestus order and call records.

Nothing here opens a provider, a cluster or the archive by itself. The caller passes the two
agents, their shared traced adapter and the role-bound O writers. Limits are the locked protocol
rows (section 3, Model). The per-trial token and cost caps are an allocation derived from them.
"""
import asyncio
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import time

from .client import Client
from .contract import canonical, valid_id, validate
from .formal_capture import METHOD, DecisionArchiveError, archive_decision
from .formal_config import CONTEXT_FIELDS, MAX_OBSERVATION_BYTES
from .llm import MAX_BYTES, RunBudget

CALL_TOKENS = 15_000
TRIAL = {"calls": 2, "tokens": 2 * CALL_TOKENS, "usd": Decimal("0.015")}
BLOCK = {"calls": 4, "tokens": 60_000, "usd": Decimal("0.03")}
TOTAL = {"calls": 20, "tokens": 300_000, "usd": Decimal("0.15")}
WORK_S = 900
SHA256 = re.compile(r"[0-9a-f]{64}")
HTTP_STATUS = re.compile(r"HTTP_[1-5][0-9]{2}")
ROW_KEYS = {"CLAIM": {"kind", "schedule_sha256", "block", "run_id", "trial_id"},
            "SETTLE": {"kind", "schedule_sha256", "block", "run_id", "trial_id", "calls", "reserved_tokens",
                       "reserved_usd", "unknown_usage_attempts", "blocked", "call_coverage"},
            "RECONCILE": {"kind", "schedule_sha256", "block", "run_id", "trial_id", "calls", "reserved_tokens",
                          "reserved_usd", "approved_by", "usage_receipt_sha256"}}


class TraceArchiveError(RuntimeError):
    """A finished model call has no matching durable O receipt."""


def trial_budget(run_id, *, clock=time.monotonic):
    """One budget object per trial. Block and total limits live in the durable ledger."""
    return RunBudget(run_id, max_calls=TRIAL["calls"], max_reserved_tokens=TRIAL["tokens"],
                     max_estimated_usd=TRIAL["usd"], duration_s=WORK_S, clock=clock)


def call_reserve_bound(limits):
    """Largest reservation one call can make: request bytes, fixed overhead and the output cap."""
    return MAX_BYTES + 1024 + limits.max_output_tokens


def preflight(adapter):
    """Refuse a trial whose adapter could retry or reserve more than the protocol allows."""
    budget, limits = adapter.budget, adapter.limits
    problems = []
    if limits.attempts != 1:
        problems.append("RETRY_ENABLED")
    if call_reserve_bound(limits) > CALL_TOKENS:
        problems.append("CALL_RESERVATION_ABOVE_LIMIT")
    if (budget.max_calls != TRIAL["calls"] or budget.max_tokens != TRIAL["tokens"]
            or budget.max_cost != TRIAL["usd"] or budget.duration > WORK_S):
        problems.append("TRIAL_BUDGET_NOT_PINNED")
    if budget.calls or budget.unknown or budget.blocked:
        problems.append("TRIAL_BUDGET_NOT_FRESH")
    return problems


# --------------------------------------------------------------------------- durable budget ledger
def read_ledger(path):
    """Rows in file order. A row that cannot be trusted makes the whole ledger unusable.

    Every row is exactly the bytes `_row_bytes` wrote, newline included. A last row without its
    newline is a torn or edited write even when its JSON parses, so the ledger is refused.
    """
    path = Path(path)
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("FORMAL_B2_LEDGER_INVALID")
    rows = []
    for line in raw.split(b"\n")[:-1]:
        try:
            row = json.loads(line)
            keys = ROW_KEYS[row["kind"]]
            if _row_bytes(row) != line + b"\n":
                raise ValueError
            amounts = [row[key] for key in ("calls", "reserved_tokens", "unknown_usage_attempts") if key in keys]
            valid = (set(row) == keys and type(row["block"]) is int and row["block"] >= 1
                     and SHA256.fullmatch(row["schedule_sha256"]) and valid_id(row["run_id"], "run")
                     and valid_id(row["trial_id"], "trl")
                     and all(type(value) is int and value >= 0 for value in amounts)
                     and ("reserved_usd" not in keys or (Decimal(row["reserved_usd"]).is_finite()
                                                         and Decimal(row["reserved_usd"]) >= 0))
                     and ("blocked" not in keys or type(row["blocked"]) is bool)
                     and ("call_coverage" not in keys or row["call_coverage"] in ("RECORDED", "UNVERIFIED"))
                     and ("approved_by" not in keys or (isinstance(row["approved_by"], str)
                                                        and row["approved_by"].strip()
                                                        and SHA256.fullmatch(row["usage_receipt_sha256"]))))
        except (ValueError, KeyError, TypeError, ArithmeticError):
            valid = False
        if not valid:
            raise ValueError("FORMAL_B2_LEDGER_INVALID")
        rows.append(row)
    return rows


def ledger_state(rows):
    """Per-trial state, in claim order: OPEN, SETTLED, UNVERIFIED or RECONCILED, with its charge."""
    trials = {}
    for row in rows:
        trial = trials.get(row["trial_id"])
        if row["kind"] == "CLAIM":
            if trial is not None:
                raise ValueError("FORMAL_B2_LEDGER_INVALID")
            # An open claim is charged the whole trial allocation until it is closed.
            trials[row["trial_id"]] = dict(row, state="OPEN", calls=TRIAL["calls"],
                                           reserved_tokens=TRIAL["tokens"], reserved_usd=str(TRIAL["usd"]))
            continue
        if trial is None or any(trial[key] != row[key] for key in ("schedule_sha256", "block", "run_id")):
            raise ValueError("FORMAL_B2_LEDGER_INVALID")
        if row["kind"] == "SETTLE" and trial["state"] == "OPEN":
            unverified = row["unknown_usage_attempts"] or row["blocked"] or row["call_coverage"] != "RECORDED"
            trial.update(state="UNVERIFIED" if unverified else "SETTLED")
        elif row["kind"] == "RECONCILE" and trial["state"] in ("OPEN", "UNVERIFIED"):
            trial.update(state="RECONCILED")
        else:
            raise ValueError("FORMAL_B2_LEDGER_INVALID")
        trial.update({key: row[key] for key in ("calls", "reserved_tokens", "reserved_usd")})
    return trials


def _decide(rows, *, schedule_sha256, block, run_id, trial_id):
    trials = ledger_state(rows)

    def used(items):
        return {"calls": sum(item["calls"] for item in items),
                "tokens": sum(item["reserved_tokens"] for item in items),
                "usd": sum((Decimal(item["reserved_usd"]) for item in items), Decimal(0))}

    scopes = {"block": (used([item for item in trials.values() if item["block"] == block]), BLOCK),
              "total": (used(trials.values()), TOTAL)}
    report = {name: {key: str(value) if key == "usd" else value for key, value in spent.items()}
              for name, (spent, _) in scopes.items()}
    states = {item["state"] for item in trials.values()}
    if (type(block) is not int or block < 1 or not isinstance(schedule_sha256, str)
            or not SHA256.fullmatch(schedule_sha256) or not valid_id(run_id, "run") or not valid_id(trial_id, "trl")):
        status = "REFUSE_CLAIM_INVALID"
    elif any(item["schedule_sha256"] != schedule_sha256 for item in trials.values()):
        status = "REFUSE_SCHEDULE_MISMATCH"
    elif "OPEN" in states:
        # A claim without its settlement: an earlier process may have called the model. No retry.
        status = "HOLD_OPEN_CLAIM"
    elif "UNVERIFIED" in states:
        status = "HOLD_USAGE_UNVERIFIED"
    elif trial_id in trials:
        status = "REFUSE_TRIAL_ALREADY_RECORDED"
    elif any(spent[key] + TRIAL[key] > limit[key] for spent, limit in scopes.values() for key in TRIAL):
        status = "REFUSE_LIMIT"
    else:
        status = "ADMIT"
    return dict(report, status=status)


def _row_bytes(row):
    return (json.dumps(row, sort_keys=True) + "\n").encode()


def _append(path, row):
    """Append one whole row as exact bytes. A short write is reported, and the next read refuses it."""
    data = _row_bytes(row)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
    try:
        written = os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if written != len(data):
        raise ValueError("FORMAL_B2_LEDGER_INVALID")


def _locked(path, action, *, wait_s=2.0):
    """Run check-and-append as one step. A lock left by a dead process holds, it is never broken here."""
    lock, until = str(path) + ".lock", time.monotonic() + wait_s
    while True:
        try:
            descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= until:
                return {"status": "HOLD_LEDGER_LOCKED"}
            time.sleep(0.01)
    try:
        return action()
    finally:
        os.close(descriptor)
        os.unlink(lock)


def claim(path, *, schedule_sha256, block, run_id, trial_id, lock_wait_s=2.0):
    """Reserve one whole trial durably BEFORE its first model call. Only ADMIT writes a row."""
    def action():
        try:
            rows = read_ledger(path)
            verdict = _decide(rows, schedule_sha256=schedule_sha256, block=block, run_id=run_id, trial_id=trial_id)
            if verdict["status"] == "ADMIT":
                _append(path, {"kind": "CLAIM", "schedule_sha256": schedule_sha256, "block": block,
                               "run_id": run_id, "trial_id": trial_id})
        except (ValueError, OSError):
            # A torn, edited or unwritable ledger cannot prove what was spent or hold the claim.
            return {"status": "HOLD_LEDGER_INVALID"}
        return verdict
    return _locked(path, action, wait_s=lock_wait_s)


def settle(path, *, trial_id, summary, call_coverage):
    """Close this trial's open claim with what the adapter's budget actually reserved."""
    def action():
        trial = ledger_state(read_ledger(path)).get(trial_id)
        if trial is None or trial["state"] != "OPEN" or call_coverage not in ("RECORDED", "UNVERIFIED"):
            raise ValueError("FORMAL_B2_LEDGER_SETTLE_REFUSED")
        _append(path, {"kind": "SETTLE", "schedule_sha256": trial["schedule_sha256"], "block": trial["block"],
                       "run_id": trial["run_id"], "trial_id": trial_id,
                       "calls": summary["attempts_dispatched"], "reserved_tokens": summary["reserved_tokens"],
                       "reserved_usd": str(Decimal(str(summary["reserved_estimate_usd"]))),
                       "unknown_usage_attempts": summary["unknown_usage_attempts"],
                       "blocked": summary["blocked"], "call_coverage": call_coverage})
        return {"status": "SETTLED"}
    return _locked(path, action)


def reconcile(path, *, trial_id, approved_by, usage_receipt_sha256):
    """Record the owner's decision on an interrupted or unverified trial, with the usage receipt hash.

    The trial keeps the whole allocation as its charge: an interrupted process may have used it.
    """
    def action():
        trial = ledger_state(read_ledger(path)).get(trial_id)
        if (trial is None or trial["state"] not in ("OPEN", "UNVERIFIED")
                or not isinstance(approved_by, str) or not approved_by.strip()
                or not isinstance(usage_receipt_sha256, str) or not SHA256.fullmatch(usage_receipt_sha256)):
            raise ValueError("FORMAL_B2_LEDGER_RECONCILE_REFUSED")
        _append(path, {"kind": "RECONCILE", "schedule_sha256": trial["schedule_sha256"], "block": trial["block"],
                       "run_id": trial["run_id"], "trial_id": trial_id, "calls": TRIAL["calls"],
                       "reserved_tokens": TRIAL["tokens"], "reserved_usd": str(TRIAL["usd"]),
                       "approved_by": approved_by.strip(), "usage_receipt_sha256": usage_receipt_sha256})
        return {"status": "RECONCILED"}
    return _locked(path, action)


# --------------------------------------------------------------------------- O observation and call records
def read_access(directory, detected):
    """Read the producer-owned O access record for a detection: once, bounded, no waiting.

    Same file name and single read as the B1 resolver, so a late observation costs both groups
    the same. None means no record. An unreadable record is returned as {} for Hephaestus to reject.
    """
    path = Path(directory) / (detected["event_id"] + ".json")
    try:
        if path.is_symlink():
            return {}
        with path.open("rb") as stream:
            raw = stream.read(MAX_OBSERVATION_BYTES + 1)
        access = json.loads(raw) if len(raw) <= MAX_OBSERVATION_BYTES else {}
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        return {}
    return access if isinstance(access, dict) else {}


def open_formal_trace_sink(context, *, keys_file):
    """Bind the B2 O writer for LLM_CALL records to the role and exact trial context."""
    if (context.get("group") != "B2" or context.get("method_version") != METHOD
            or any(field not in context for field in CONTEXT_FIELDS) or not keys_file):
        raise ValueError("FORMAL_TRACE_O_CONFIGURATION")
    client = Client.from_env("decision_llm", keys_file=keys_file)
    expected = tuple(context[field] for field in CONTEXT_FIELDS)
    if client is None or (client.run, client.trial) != expected[:2]:
        raise ValueError("FORMAL_TRACE_O_CONTEXT")

    def publish(event):
        if (validate(event, "O", "decision_llm") or event["event_type"] != "LLM_CALL"
                or tuple(event.get(field) for field in CONTEXT_FIELDS) != expected):
            raise ValueError("FORMAL_TRACE_O_EVENT")
        return client.publish(event)

    return publish


class TracedAdapter:
    """The shared adapter, with every LLM_CALL record archived as soon as its call ends.

    The record is written before the agent sees the result, so it does not depend on the decision
    reaching the archive. A record without a matching receipt stops the agent before any decision,
    guard or dispatch.
    """
    def __init__(self, adapter, trace_sink):
        if isinstance(adapter, TracedAdapter) or not callable(trace_sink):
            raise ValueError("FORMAL_TRACE_ADAPTER_CONFIGURATION")
        self.inner, self.trace_sink = adapter, trace_sink
        self.archived, self.unarchived = [], []

    def __getattr__(self, name):
        return getattr(self.inner, name)

    async def _archive(self, start):
        for event in list(self.inner.events[start:]):
            try:
                await archive_decision(self.trace_sink, event)
            except DecisionArchiveError:
                self.unarchived.append(event["event_id"])
            else:
                self.archived.append(event["event_id"])

    async def call(self, context, **arguments):
        start = len(self.inner.events)
        try:
            result = await self.inner.call(context, **arguments)
        except BaseException:
            await self._archive(start)  # the adapter's own error, cancellation included, stays the outcome
            raise
        await self._archive(start)
        if self.unarchived:
            raise TraceArchiveError("FORMAL_CALL_RECORD_ARCHIVE_UNVERIFIED")
        return result

    def coverage(self):
        """RECORDED only when every dispatched attempt has exactly one archived record."""
        dispatched = self.inner.budget.summary()["attempts_dispatched"]
        complete = not self.unarchived and len(self.archived) == len(set(self.archived)) == dispatched
        return {"status": "RECORDED" if complete else "UNVERIFIED", "dispatched": dispatched,
                "archived": len(self.archived), "unarchived": len(self.unarchived)}


def call_records(events):
    """Replay model calls from O events, independent of read order.

    Joined by run, trial, call and attempt. Identical copies count once. Two different records
    for one attempt cannot both be true: the attempt stays counted as a call, but its outcome,
    usage and error leave every confirmed number and are reported as unverified.

    The adapter records outcome HTTP_ERROR both for a response with an HTTP status and for a
    request that got no response. They are counted apart: `http_errors` needs reason HTTP_<status>,
    and every other HTTP_ERROR record (NETWORK, TRANSPORT_ERROR) is a `transport_errors` entry.
    `outcomes` keeps the outcome exactly as archived.
    """
    attempts = {}
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "LLM_CALL" or validate(event, "O"):
            continue
        key = (event["run_id"], event["trial_id"], event["call_id"], event["payload"]["attempt_no"])
        attempts.setdefault(key, {})[hashlib.sha256(canonical(event)).hexdigest()] = event
    trials = {}
    for (run_id, trial_id, call_id, attempt_no), versions in sorted(attempts.items()):
        row = trials.setdefault((run_id, trial_id), {
            "calls": 0, "confirmed_calls": 0, "http_errors": 0, "transport_errors": 0,
            "unknown_usage_attempts": 0, "outcomes": {}, "reasons": {}, "unverified_attempts": []})
        row["calls"] += 1
        if len(versions) != 1:
            row["unverified_attempts"].append({"call_id": call_id, "attempt_no": attempt_no,
                                               "records": len(versions)})
            continue
        payload = next(iter(versions.values()))["payload"]
        reason = payload.get("reason_code")
        row["confirmed_calls"] += 1
        if payload["outcome"] == "HTTP_ERROR":
            answered = isinstance(reason, str) and HTTP_STATUS.fullmatch(reason)
            row["http_errors" if answered else "transport_errors"] += 1
        row["unknown_usage_attempts"] += payload["usage"].get("status") != "COMPLETE"
        row["outcomes"][payload["outcome"]] = row["outcomes"].get(payload["outcome"], 0) + 1
        if reason:
            row["reasons"][reason] = row["reasons"].get(reason, 0) + 1
    return trials


# --------------------------------------------------------------------------- one formal B2 trial
async def run_trial(diagnoser, healer, detected, evidence, access, *, ledger, block, schedule_sha256):
    """One formal B2 trial: durable claim, Gaia once, then Hephaestus only after a usable diagnosis.

    Each agent archives its own first decision. The traced adapter archives every call record.
    A trial that raises or is killed leaves its claim open, and the ledger then holds.
    session_stop is a reason for the caller to end the session, even if budget settlement succeeds.
    """
    adapter, context = diagnoser.adapter, diagnoser.context
    if (not isinstance(adapter, TracedAdapter) or healer.adapter is not adapter or healer.context != context
            or adapter.archived or adapter.unarchived):
        raise ValueError("FORMAL_B2_TRIAL_CONFIGURATION")
    summary = {"run_id": context["run_id"], "trial_id": context["trial_id"], "block": block,
               "detection_event_id": detected.get("event_id") if isinstance(detected, dict) else None,
               "gaia": None, "hephaestus": None, "stop": None, "session_stop": None,
               "not_run": [], "claim": None}

    def finish(stop=None):
        return dict(summary, stop=stop or summary["stop"], session_stop=stop or summary["session_stop"],
                    call_coverage=adapter.coverage(),
                    budget=adapter.budget.summary())

    problems = preflight(adapter)
    if problems:
        return finish("PREFLIGHT:" + ",".join(problems))
    verdict = await asyncio.to_thread(claim, ledger, schedule_sha256=schedule_sha256, block=block,
                                      run_id=context["run_id"], trial_id=context["trial_id"])
    summary["claim"] = verdict
    if verdict["status"] != "ADMIT":
        return finish("BUDGET:" + verdict["status"])

    def step(receipt):
        return {key: receipt.get(key) for key in ("status", "reason", "decision_id")}

    try:
        gaia = await diagnoser.analyze(detected, evidence)
    except TraceArchiveError:
        summary["stop"] = summary["session_stop"] = "CALL_RECORD_ARCHIVE_UNVERIFIED"
    except DecisionArchiveError:
        summary["stop"] = summary["session_stop"] = "GAIA_DECISION_ARCHIVE_UNVERIFIED"
    else:
        summary["gaia"] = step(gaia)
        if gaia.get("status") != "OK":
            summary["stop"] = "GAIA_" + str(gaia.get("status"))
        else:
            heal = await healer.run(detected, access)
            summary["hephaestus"] = step(heal)
            if heal.get("reason") == "FORMAL_DECISION_ARCHIVE_UNVERIFIED":
                summary["stop"] = summary["session_stop"] = "HEPHAESTUS_DECISION_ARCHIVE_UNVERIFIED"
            elif adapter.unarchived:
                summary["stop"] = summary["session_stop"] = "CALL_RECORD_ARCHIVE_UNVERIFIED"
    summary["not_run"] = [name for name in ("gaia", "hephaestus")
                          if summary[name] and summary[name]["status"] == "NOT_RUN"]
    result = finish()
    coverage, budget = result["call_coverage"]["status"], result["budget"]
    try:
        settled = await asyncio.to_thread(settle, ledger, trial_id=context["trial_id"], summary=budget,
                                          call_coverage=coverage)
        settlement_status = settled["status"]
    except (OSError, ValueError):
        settlement_status = "UNVERIFIED"
    if result["session_stop"] is None:
        if settlement_status != "SETTLED":
            result["session_stop"] = "BUDGET_SETTLEMENT_UNVERIFIED"
        elif coverage != "RECORDED":
            result["session_stop"] = "CALL_RECORD_ARCHIVE_UNVERIFIED"
        elif not budget["cost_estimate_complete"] or budget["blocked"]:
            result["session_stop"] = "BUDGET_USAGE_UNVERIFIED"
    return dict(result, settle=settlement_status)
