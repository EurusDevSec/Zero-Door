"""H-plane delivery for probe events: a durable local outbox and the H gateway sink.

Every event is appended and fsynced to the outbox BEFORE delivery is attempted, and a resend always
carries the same envelope (same event_id). A sink outage therefore delays evidence but never drops it
silently; an outbox write failure stops the probe (fail closed). This module has no O credentials or
O paths and never imports the O client.
"""
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from event_pipeline.contract import canonical

TERMINAL = {"DELIVERED", "REJECTED", "LATE"}


class PersistenceFailure(RuntimeError):
    """The outbox could not durably keep an event: raw would be lost, so the probe must stop."""


class SinkRefused(RuntimeError):
    """The H write cannot be trusted or completed by retrying (redirect, foreign ACK): stop, keep the outbox."""


class SinkUnauthorized(SinkRefused):
    """The H gateway refused the probe identity; retrying cannot help."""


class NoRedirect(HTTPRedirectHandler):
    """Never follow a redirect: the bearer token and the event go to the configured H origin only."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Retry(RuntimeError):
    """Outcome unknown (timeout, connection error, 5xx/429): resend the same envelope later."""


class Outbox:
    """Append-only JSONL: {"op":"event","event":...} then {"op":"state","event_id":...,"state":...}."""
    def __init__(self, path):
        self.path = Path(path)
        self.pending, self.states = {}, {}
        if self.path.exists():
            with open(self.path, "rb") as handle:
                for line in handle:
                    if not line.endswith(b"\n"):
                        raise PersistenceFailure("outbox ends with a partial line; keep it for the operator")
                    record = json.loads(line)
                    if record["op"] == "event":
                        self.pending.setdefault(record["event"]["event_id"], record["event"])
                    else:
                        self.states[record["event_id"]] = record["state"]
                        if record["state"] in TERMINAL:
                            self.pending.pop(record["event_id"], None)

    def append(self, record):
        try:
            with open(self.path, "ab") as handle:
                handle.write(canonical(record) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as error:
            raise PersistenceFailure("outbox write failed: " + type(error).__name__) from error

    def add(self, event):
        self.append({"op": "event", "event": event})
        self.pending[event["event_id"]] = event

    def mark(self, event_id, state, detail=None):
        self.append({"op": "state", "event_id": event_id, "state": state, "detail": detail})
        self.states[event_id] = state
        if state in TERMINAL:
            self.pending.pop(event_id, None)


def load_probe_key(path):
    """The probe's H key file holds exactly {"probe": token}; any other role is refused."""
    keys = json.loads(Path(path).read_text())
    if not isinstance(keys, dict) or set(keys) != {"probe"} or not isinstance(keys["probe"], str) or len(keys["probe"]) < 32:
        raise ValueError("H key file must hold exactly the probe role")
    return keys["probe"]


class HttpHSink:
    """POST /events on the H gateway with the probe role (event_pipeline.gateway)."""
    def __init__(self, url, token, timeout_s=5.0):
        if urlsplit(url).scheme not in {"http", "https"}:
            raise ValueError("H gateway URL must be http(s)")
        self.url, self.token, self.timeout_s = url.rstrip("/"), token, timeout_s
        # No environment proxy and no redirect: a proxy or a 30x would carry the token somewhere else.
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def deliver(self, event):
        endpoint = self.url + "/events"
        request = Request(endpoint, data=canonical(event), method="POST",
                          headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        try:
            # The scheme is restricted to http(s) in __init__ (Bandit B310).
            with self.opener.open(request, timeout=self.timeout_s) as response:  # nosec B310
                code, final = response.status, response.geturl()
                answer = json.load(response)
        except HTTPError as error:
            if 300 <= error.code < 400:
                raise SinkRefused(f"REDIRECT_{error.code}") from None
            if error.code in (401, 403):
                raise SinkUnauthorized(str(error.code)) from None
            if error.code == 422:
                return "REJECTED", _classification(error)
            if error.code == 409:
                return "LATE", _classification(error)
            raise Retry(f"HTTP {error.code}") from None
        except (URLError, OSError, ValueError) as error:
            raise Retry(type(error).__name__) from None
        if final != endpoint:
            raise SinkRefused("ANSWER_FROM_OTHER_URL")
        if code == 202:
            raise Retry("not durable yet (202)")  # e.g. a broker acknowledgement: keep the event pending
        if not isinstance(answer, dict) or code != 201 or answer.get("event_id") != event["event_id"] or \
                answer.get("status") not in {"RECORDED", "DUPLICATE", "SEALED_DUPLICATE"}:
            raise SinkRefused("UNEXPECTED_ACK")
        return "DELIVERED", answer["status"]


def _classification(error):
    try:
        return json.loads(error.read()).get("classification")
    except (ValueError, OSError, AttributeError):
        return None


class Publisher:
    """Outbox first, then delivery in order with bounded attempts per call."""
    def __init__(self, outbox, sink):
        self.outbox, self.sink = outbox, sink
        self.counts = {"delivered": 0, "rejected": 0, "late": 0, "retries": 0}

    def put(self, event):
        self.outbox.add(event)
        self.flush(max_attempts=1)

    def flush(self, max_attempts=1, deadline_ns=None):
        """Try every pending event until `deadline_ns` (perf_counter_ns); returns the number still pending.
        Never drops one: what is left stays in the outbox for the next run."""
        for event_id, event in list(self.outbox.pending.items()):
            if deadline_ns is not None and time.perf_counter_ns() >= deadline_ns:
                break
            for _ in range(max_attempts):
                try:
                    state, detail = self.sink.deliver(event)
                except Retry:
                    self.counts["retries"] += 1
                    continue
                self.outbox.mark(event_id, state, detail)
                self.counts[{"DELIVERED": "delivered", "REJECTED": "rejected", "LATE": "late"}[state]] += 1
                break
            else:
                # Keep order: a later event is not delivered ahead of an undelivered earlier one.
                break
        return len(self.outbox.pending)


class MemorySink:
    """Offline sink for tests: delivers into a list or fails as scripted."""
    def __init__(self, script=None):
        self.events, self.script = [], list(script or [])

    def deliver(self, event):
        action = self.script.pop(0) if self.script else "ok"
        if action == "retry":
            raise Retry("scripted")
        if action == "reject":
            return "REJECTED", "INVALID"
        self.events.append(event)
        return "DELIVERED", "RECORDED"
