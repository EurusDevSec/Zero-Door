"""Run-scoped authenticated SQLi handoff; independent of model output.

This private transport is not the R1 authenticated O archive. A fresh operator
key authenticates observation bytes across Kafka. Durable claim-before-dispatch
makes ambiguous delivery non-replayable; Healer's native guards still authorize.
"""
from copy import deepcopy
import hashlib
import hmac
import json
import os
from pathlib import Path
import time
import uuid

from event_pipeline.contract import canonical
from gaia.diagnosis import CONTEXT_KEYS, observation_valid

VERSION = "sqli-handoff/1"
MAX_BYTES = 32768


def check_observation(observed, context):
    if type(observed) is not dict or set(observed) != {"detection", "evidence", "access"}:
        raise ValueError("HANDOFF_OBSERVATION")
    observation_valid(observed["detection"], observed["evidence"])
    if any(observed["detection"].get(k) != context[k] for k in CONTEXT_KEYS):
        raise ValueError("HANDOFF_CONTEXT")
    access = observed["access"]
    if (type(access) is not dict or access.get("detection_event_id") != observed["detection"]["event_id"]
            or access.get("run_id") != context["run_id"] or access.get("trial_id") != context["trial_id"]):
        raise ValueError("HANDOFF_ACCESS_JOIN")


class Handoff:
    def __init__(self, key, context, claim_path, *, clock=time.time):
        if (type(key) is not bytes or len(key) != 32 or set(context) != set(CONTEXT_KEYS)
                or context.get("group") != "B2"):
            raise ValueError("HANDOFF_CONFIG")
        self.key, self.context = key, deepcopy(context)
        self.claim_path, self.clock = Path(claim_path), clock
        self.sent = False

    def seal(self, observed):
        check_observation(observed, self.context)
        if self.sent:
            raise ValueError("HANDOFF_ALREADY_SENT")
        self.sent = True  # Never refund an ambiguous delivery attempt.
        payload = {"version": VERSION, "context": self.context, "id": uuid.uuid4().hex,
                   "observation": deepcopy(observed), "issued_at": self.clock()}
        body = canonical(payload)
        if len(body) > MAX_BYTES:
            raise ValueError("HANDOFF_SIZE")
        return {"payload": payload, "mac": hmac.new(self.key, body, hashlib.sha256).hexdigest()}

    def receive(self, packet):
        if type(packet) is not dict or set(packet) != {"payload", "mac"}:
            raise ValueError("HANDOFF_ENVELOPE")
        body = canonical(packet["payload"])
        if (len(body) > MAX_BYTES or not isinstance(packet["mac"], str)
                or not hmac.compare_digest(packet["mac"], hmac.new(self.key, body, hashlib.sha256).hexdigest())):
            raise ValueError("HANDOFF_AUTH")
        p = packet["payload"]
        if (type(p) is not dict or set(p) != {"version", "context", "id", "observation", "issued_at"}
                or p["version"] != VERSION or p["context"] != self.context
                or not isinstance(p["id"], str) or len(p["id"]) != 32
                or any(c not in "0123456789abcdef" for c in p["id"])
                or type(p["issued_at"]) not in (int, float)
                or not 0 <= self.clock() - p["issued_at"] <= 60):
            raise ValueError("HANDOFF_SCOPE_OR_FRESHNESS")
        check_observation(p["observation"], self.context)
        # A per-incident exclusive durable claim survives restart; never auto-retry.
        with self.claim_path.open("x", encoding="utf8") as stream:
            json.dump({"id": p["id"], "sha256": hashlib.sha256(body).hexdigest()}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        return deepcopy(p["observation"])
