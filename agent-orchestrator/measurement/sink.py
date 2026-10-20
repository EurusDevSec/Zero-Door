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
from urllib.parse import urlsplit

from event_pipeline.contract import canonical

TERMINAL = {"DELIVERED", "REJECTED", "LATE"}


class PersistenceFailure(RuntimeError):
    """The outbox could not durably keep an event: raw would be lost, so the probe must stop."""


class SinkRefused(RuntimeError):
    """The H write cannot be trusted or completed by retrying (redirect, foreign ACK): stop, keep the outbox."""


class SinkUnauthorized(SinkRefused):
    """The H gateway refused the probe identity; retrying cannot help."""


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


class Journal(list):
    """The probe's operator journal, also kept on disk: every note is appended and fsynced as it is made,
    so what a cancelled sample left behind (cleanup, unresolved ownership) survives the process even
    though the sample itself is never emitted. A write failure stops the probe like an outbox failure."""
    def __init__(self, path):
        super().__init__()
        self.path = Path(path)

    def append(self, note):
        try:
            with open(self.path, "ab") as handle:
                handle.write(canonical(note) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as error:
            raise PersistenceFailure("journal write failed: " + type(error).__name__) from error
        super().append(note)


def load_probe_key(path):
    """The probe's H key file holds exactly {"probe": token}; any other role is refused."""
    keys = json.loads(Path(path).read_text())
    if not isinstance(keys, dict) or set(keys) != {"probe"} or not isinstance(keys["probe"], str) or len(keys["probe"]) < 32:
        raise ValueError("H key file must hold exactly the probe role")
    return keys["probe"]


class HttpHSink:
    """POST /events on the H gateway with the probe role (event_pipeline.gateway).

    The exchange uses the probe's bounded HTTP/1.1 client (flows.request): one total deadline covers
    connect, TLS, send, headers and the whole ACK body, so a gateway that answers slowly or drips its
    ACK cannot hold the probe past it (FX01-R2). That client has no proxy support and never follows a
    redirect, so the token only ever goes to the configured H origin.
    """
    MAX_ACK = 64 * 1024

    def __init__(self, url, token, timeout_s=5.0):
        if urlsplit(url).scheme not in {"http", "https"}:
            raise ValueError("H gateway URL must be http(s)")
        self.url, self.token, self.timeout_s = url.rstrip("/"), token, timeout_s

    def deliver(self, event, deadline_ns=None):
        """(state, detail) for one attempt that ends by min(now + timeout_s, deadline_ns)."""
        from .flows import Failure, bounded_deadline, request
        limit = time.perf_counter_ns() + int(self.timeout_s * 1e9)
        limit = bounded_deadline(limit, deadline_ns)
        headers = [("Authorization", "Bearer " + self.token), ("Content-Type", "application/json")]
        try:
            response = request(self.url + "/events", "POST", headers, canonical(event), limit, None, max_body=self.MAX_ACK)
        except Failure as failure:
            # Timeout, refused connection, truncated or malformed answer: outcome unknown, the same envelope is resent.
            raise Retry(f"{failure.detail}:{failure.reason}") from None
        code = response.status
        if 300 <= code < 400:
            raise SinkRefused(f"REDIRECT_{code}")
        if code in (401, 403):
            raise SinkUnauthorized(str(code))
        if code in (422, 409):
            return ("REJECTED" if code == 422 else "LATE"), _classification(response.body)
        if code == 202:
            raise Retry("not durable yet (202)")  # e.g. a broker acknowledgement: keep the event pending
        if 200 <= code < 300 and code != 201:
            raise SinkRefused("UNEXPECTED_ACK")
        if code != 201:
            raise Retry(f"HTTP {code}")  # 5xx, 429 and other answers: unknown, resend later
        try:
            answer = json.loads(response.body)
        except ValueError:
            raise SinkRefused("UNEXPECTED_ACK") from None
        if not isinstance(answer, dict) or answer.get("event_id") != event["event_id"] or \
                answer.get("status") not in {"RECORDED", "DUPLICATE", "SEALED_DUPLICATE"}:
            raise SinkRefused("UNEXPECTED_ACK")
        return "DELIVERED", answer["status"]


def _classification(body):
    try:
        value = json.loads(body)
        return value.get("classification") if isinstance(value, dict) else None
    except ValueError:
        return None


class Publisher:
    """Outbox first, then delivery in order with bounded attempts per call."""
    def __init__(self, outbox, sink):
        self.outbox, self.sink = outbox, sink
        self.counts = {"delivered": 0, "rejected": 0, "late": 0, "retries": 0}

    def put(self, event, deadline_ns=None):
        """Keep the event durably, then try to deliver within `deadline_ns` (it stays pending otherwise)."""
        self.outbox.add(event)
        self.flush(max_attempts=1, deadline_ns=deadline_ns)

    def flush(self, max_attempts=1, deadline_ns=None):
        """Try every pending event until `deadline_ns` (perf_counter_ns); returns the number still pending.
        The deadline is checked before every attempt and passed into the attempt itself, so no request
        starts, and none runs on, after it. Never drops one: what is left stays in the outbox."""
        from .flows import deadline_value
        for event_id, event in list(self.outbox.pending.items()):
            for _ in range(max_attempts):
                if deadline_ns is not None and time.perf_counter_ns() >= deadline_value(deadline_ns):
                    return len(self.outbox.pending)
                try:
                    state, detail = self.sink.deliver(event, deadline_ns)
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

    def deliver(self, event, deadline_ns=None):
        action = self.script.pop(0) if self.script else "ok"
        if action == "retry":
            raise Retry("scripted")
        if action == "reject":
            return "REJECTED", "INVALID"
        self.events.append(event)
        return "DELIVERED", "RECORDED"
