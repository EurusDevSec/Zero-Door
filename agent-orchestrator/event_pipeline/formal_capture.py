"""Passive capture for the ZER-53 decision producer, before its first archive write."""
import asyncio
from copy import deepcopy
import re

from .contract import FORMAL_METHOD as METHOD, validate

# Named refusals the model adapter raises before any request is sent. Both B2 agents record these
# as SCHEMA_INVALID / INPUT_REJECTED. Any other error stays an internal failure with no decision.
ADAPTER_INPUT_REJECTIONS = frozenset(("LLM_INPUT_OR_MODE_INVALID", "LLM_REQUEST_TOO_LARGE"))

def is_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def parameters(record):
    if not isinstance(record, dict):
        return None
    source, uid, ttl = (record.get(key) for key in ("source", "fixture_uid", "ttl_s"))
    if isinstance(source, str) and source and isinstance(uid, str) and uid and type(ttl) is int:
        return source, uid, ttl
    return None


def prepare_decision(event, *, terminal_abstain=False, resolution=None, resolver_sha256=None):
    """Prepare one unrecorded O event. The caller supplies its already observed resolver result."""
    if (validate(event, "O") or event["method_version"] != METHOD or event["event_type"] != "DECISION"
            or (event["group"], event["source_component"]) not in
            {("B1", "decision_rules"), ("B2", "decision_llm")}):
        raise ValueError("expected a formal B1/B2 decision from the original producer")
    captured = deepcopy(event)
    payload = captured["payload"]
    if "pre_guard" in payload:
        raise ValueError("decision already contains a pre-guard receipt")
    if terminal_abstain:
        if (event["group"] != "B2" or payload["stage"] != "ANALYSIS"
                or payload["response_kind"] != "ABSTAIN"):
            raise ValueError("terminal abstain requires an ending B2 analysis abstain")
        payload["stage"] = "PROPOSAL"
    if resolution is not None:
        proposal = payload["proposal"] or {}
        if (payload["stage"] != "PROPOSAL" or not isinstance(proposal, dict)
                or proposal.get("action_type") != "BLOCK_IP"
                or not isinstance(resolution, dict) or not is_sha256(resolver_sha256)):
            raise ValueError("expected a resolver result and pin for a BLOCK_IP proposal")
        status = resolution.get("status")
        resolved = parameters(resolution)
        receipt = {"decision_event_id": event["event_id"], "resolver_sha256": resolver_sha256, "status": status}
        if status == "RESOLVED" and resolved is not None:
            receipt.update(zip(("source", "fixture_uid", "ttl_s"), resolved))
        elif status not in ("RESOLVER_ERROR", "OBSERVATION_MISSING"):
            raise ValueError("invalid resolver outcome")
        payload["pre_guard"] = receipt
    if validate(captured, "O"):
        raise ValueError("invalid captured decision")
    return captured


def terminal_model_decision(producer, context, detected, decision_id, received, *,
                            kind, reason, prompt_version, traces, evidence_version):
    """Capture a terminal outcome tied to an admitted detection, without a proposal."""
    prompt = next((event["payload"]["prompt_sha256"] for event in reversed(traces)
                   if event.get("event_type") == "LLM_CALL" and event.get("decision_id") == decision_id), None)
    return producer.event(context, "DECISION", {
        "stage": "PROPOSAL", "decision_source": "LLM",
        "inputs": [{"event_id": detected["event_id"], "received_at": received}],
        "response_kind": kind, "proposal": None, "fallback": False, "fallback_of": None,
        "prompt_version": prompt_version if prompt else None, "prompt_sha256": prompt,
        "evidence_package_version": evidence_version, "reason_code": reason,
    }, "o.decision", target=detected["target"], decision_id=decision_id,
        causation_id=detected["event_id"])


class DecisionArchiveError(RuntimeError):
    """A formal decision did not receive a matching durable O receipt."""


async def archive_decision(sink, event):
    """Await the original producer's durable archive receipt before the caller proceeds."""
    writer = asyncio.create_task(asyncio.to_thread(sink, deepcopy(event)))
    try:
        receipt = await asyncio.shield(writer)
    except asyncio.CancelledError:
        try:
            await writer
        except Exception as error:
            raise asyncio.CancelledError from error
        raise
    except Exception as error:
        raise DecisionArchiveError("FORMAL_DECISION_ARCHIVE_UNVERIFIED") from error
    if (not isinstance(receipt, dict) or receipt.get("event_id") != event["event_id"]
            or receipt.get("status") not in ("RECORDED", "DUPLICATE")):
        raise DecisionArchiveError("FORMAL_DECISION_ARCHIVE_UNVERIFIED")
    return receipt
