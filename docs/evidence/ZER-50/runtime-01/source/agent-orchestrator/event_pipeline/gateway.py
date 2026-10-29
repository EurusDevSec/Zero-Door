"""Plane-scoped HTTP ingress and Kafka recorder. One process owns one archive.

H and O MUST run as separate identities with different roots and key files.
There is intentionally no raw file/path/query/export endpoint.
"""
import argparse
import hashlib
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .contract import canonical, new_id, validate, valid_id
from .store import Archive, ArchiveFailure, Rejected, decode, too_deep

SEAL_TIMEOUT = 10.0


class SealPending(RuntimeError):
    """Acknowledged events for the run are not yet durable; the run is NOT sealed."""


class Gateway:
    def __init__(self, archive, credentials, kafka=None, telemetry=None):
        self.archive, self.credentials, self.kafka = archive, credentials, kafka
        self.telemetry = telemetry
        # Seal fence: HTTP submissions between check and Kafka ack, runs being sealed, acked offsets.
        self.fence = threading.Condition()
        self.inflight, self.sealing, self.acked = {}, set(), {}

    def principal(self, token):
        for role, secret in self.credentials.items():
            if isinstance(secret, str) and len(secret) >= 32 and hmac.compare_digest(token, secret):
                return role
        return None

    def check(self, event, source, transport, raw=None):
        """Validate and bind under the archive lock; every rejection is stored before it is raised."""
        with self.archive.lock:
            self.archive.usable()
            # Depth first: the validator and binding recurse; too-deep input is INVALID, kept as bytes.
            error = ("INVALID" if too_deep(event) else None) or validate(event, self.archive.plane, source)
            if not error:
                try:
                    self.binding(event)
                except ValueError as failure:
                    error = str(failure)
            if error:
                self.archive.reject(error, transport, source, event=event, raw=raw)

    def admit(self, event, source, transport, raw=None):
        """Binding and append are one transaction, so concurrent contexts cannot both pass."""
        with self.archive.lock:
            self.check(event, source, transport, raw)
            return self.archive.ingest(event, transport, source)

    def submit(self, event, source, request_id, raw=None, error=None):
        transport = {"kind": "http", "request_id": request_id}
        if error:
            self.archive.reject(error, transport, source, raw=raw)
        run = event.get("run_id") if isinstance(event, dict) else None
        if not self.kafka or not valid_id(run, "run"):
            return self.admit(event, source, transport, raw)
        deadline = time.monotonic() + SEAL_TIMEOUT
        with self.fence:
            while run in self.sealing:
                if not self.fence.wait(max(0.0, deadline - time.monotonic())):
                    raise SealPending("SEAL_IN_PROGRESS")
            self.inflight[run] = self.inflight.get(run, 0) + 1
        try:
            with self.archive.lock:
                if self.archive.sealed(run):
                    return self.admit(event, source, transport, raw)  # stored as LATE_INGEST, then raised
                self.check(event, source, transport, raw)
            metadata = self.kafka.publish(event, request_id)
            with self.fence:
                offsets = self.acked.setdefault(run, {})
                offsets[metadata.partition] = max(offsets.get(metadata.partition, 0), metadata.offset + 1)
            return {"status": "KAFKA_ACKNOWLEDGED", "event_id": event["event_id"]}
        finally:
            with self.fence:
                self.inflight[run] -= 1
                if not self.inflight[run]:
                    del self.inflight[run]
                self.fence.notify_all()

    def seal(self, run, timeout=None):
        """Seal only after every event this process acknowledged for the run is durable.

        Events acknowledged before a restart are covered by recorder readiness: it is not ready
        until it has handled the topic end offsets observed at startup.
        """
        if not valid_id(run, "run"):
            raise ValueError("invalid run")
        if not self.kafka:
            return self.archive.seal(run)
        deadline = time.monotonic() + (SEAL_TIMEOUT if timeout is None else timeout)
        with self.fence:
            if run in self.sealing:
                raise SealPending("SEAL_IN_PROGRESS")
            self.sealing.add(run)
        try:
            with self.fence:
                while self.inflight.get(run):
                    if not self.fence.wait(max(0.0, deadline - time.monotonic())):
                        raise SealPending("SEAL_PENDING")
                targets = dict(self.acked.get(run, {}))
            if not self.kafka.wait_for(targets, max(0.0, deadline - time.monotonic())):
                raise SealPending("SEAL_PENDING")
            return self.archive.seal(run)
        finally:
            with self.fence:
                self.sealing.discard(run)
                self.fence.notify_all()

    def readiness(self):
        if self.archive.failure:
            return {"ready": False, "reason": "ARCHIVE_FAILED:" + self.archive.failure}
        if self.kafka:
            return self.kafka.status()
        return {"ready": True, "reason": None}

    def binding(self, event):
        if self.archive.plane == "O":
            source = event["source_component"]
            if source == "harness" and event["event_type"] not in {"RUN_CONTEXT", "TRIAL_CONTEXT"}:
                raise ValueError("SOURCE_VIOLATION")
            run = event["run_id"]
            if event["event_type"] != "RUN_CONTEXT":
                context = self.archive.context(run)
                if not context:
                    raise ValueError("RUN_CONTEXT_MISSING")
                if any(event[k] != context[k] for k in ("group", "method_version", "config_ref")):
                    raise ValueError("LINK_CONFLICT")
            if event["event_type"] not in {"RUN_CONTEXT", "TRIAL_CONTEXT"}:
                trial = self.archive.context(run, event["trial_id"])
                if not trial:
                    raise ValueError("TRIAL_CONTEXT_MISSING")
                if event.get("incident_id") != trial.get("incident_id"):
                    raise ValueError("LINK_CONFLICT")
            if event["event_type"] in {"RUN_CONTEXT", "TRIAL_CONTEXT"}:
                prior = self.archive.context(run, None if event["event_type"] == "RUN_CONTEXT" else event["trial_id"])
                if prior and canonical(prior) != canonical(event):
                    raise ValueError("CONTEXT_IMMUTABLE")


def server(gateway, address):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # No payloads, tokens or secrets in shared pod logs.

        def reply(self, code, value):
            data = canonical(value)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            if self.path.startswith("/elasticsearch/"):
                self.send_header("X-Elastic-Product", "Elasticsearch")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def role(self):
            auth = self.headers.get("Authorization", "")
            return gateway.principal(auth[7:]) if auth.startswith("Bearer ") else None

        def do_POST(self):
            role = self.role()
            if not role:
                return self.reply(401, {"error": "UNAUTHORIZED"})
            if self.path not in {"/events", "/seal", "/elasticsearch/zero-door-logs-*/_search"}:
                return self.reply(403, {"error": "FORBIDDEN"})
            if self.path == "/seal" and role != "evaluator":
                return self.reply(403, {"error": "FORBIDDEN"})
            if self.path == "/events" and role in {"reader", "evaluator"}:
                return self.reply(403, {"error": "FORBIDDEN"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if not 0 < size <= 1_048_576:
                return self.reply(413, {"error": "SIZE_LIMIT"})
            body = self.rfile.read(size)
            event, error = decode(body)
            if self.path == "/events":
                try:
                    result = gateway.submit(event, role, new_id("ing"), raw=body, error=error)
                    return self.reply(202 if gateway.kafka else 201, result)
                except Rejected as rejected:
                    # Durably quarantined; permanent for this envelope. 409 = run already sealed.
                    return self.reply(409 if rejected.sealed else 422,
                                      {"error": "RUN_SEALED" if rejected.sealed else "REJECTED",
                                       "classification": rejected.classification})
                except Exception:
                    # Includes recorder failure, I/O and archive corruption: never claimed as stored.
                    return self.reply(503, {"error": "NOT_DURABLE"})
            try:
                if error:
                    raise ValueError(error)
                if self.path == "/seal":
                    return self.reply(200, gateway.seal(event["run_id"]))
                if gateway.archive.plane != "O" or role != "detector" or not gateway.telemetry:
                    return self.reply(403, {"error": "FORBIDDEN"})
                return self.reply(200, gateway.telemetry.logs(event))
            except SealPending as pending:
                return self.reply(409, {"error": str(pending)})
            except ArchiveFailure:
                return self.reply(503, {"error": "NOT_DURABLE"})
            except (ValueError, KeyError, TypeError):
                return self.reply(422, {"error": "REJECTED"})
            except Exception:
                return self.reply(503, {"error": "NOT_DURABLE"})

        def do_GET(self):
            parsed = urlsplit(self.path)
            # Unauthenticated probes reveal only a state word. Liveness never reflects archive or
            # recorder failure, so a restart loop cannot hide broken evidence; readiness does.
            if parsed.path == "/livez":
                return self.reply(200, {"status": "ALIVE"})
            if parsed.path == "/readyz":
                state = gateway.readiness()
                return self.reply(200 if state["ready"] else 503,
                                  {"status": "READY" if state["ready"] else "NOT_READY", "reason": state["reason"]})
            role = self.role()
            if not role:
                return self.reply(401, {"error": "UNAUTHORIZED"})
            # H has NO remote read API. Offline evaluator opens H archive under a separate OS identity.
            if gateway.archive.plane != "O" or role not in {"reader", "detector", "decision_rules", "operator_console"}:
                return self.reply(403, {"error": "FORBIDDEN"})
            if parsed.path == "/prometheus/api/v1/query" and role == "detector" and gateway.telemetry:
                try:
                    params = parse_qs(parsed.query)
                    if set(params) != {"query"} or len(params["query"]) != 1:
                        raise ValueError("invalid query")
                    return self.reply(200, gateway.telemetry.metrics(params["query"][0]))
                except Exception:
                    return self.reply(403, {"error": "QUERY_REJECTED"})
            if parsed.path != "/events":
                return self.reply(404, {"error": "NOT_FOUND"})
            try:
                query = parse_qs(parsed.query)
                if set(query) - {"run_id", "after", "limit"}:
                    raise ValueError("invalid query")
                run = query["run_id"][0]
                if not valid_id(run, "run"):
                    raise ValueError("invalid run")
                after = int(query.get("after", ["0"])[0])
                limit = int(query.get("limit", ["100"])[0])
                if after < 0 or not 1 <= limit <= 500:
                    raise ValueError("invalid cursor")
                selected = gateway.archive.records(run, after, limit)
                return self.reply(200, {"records": selected, "next": after + len(selected)})
            except ArchiveFailure:
                return self.reply(503, {"error": "NOT_DURABLE"})
            except (ValueError, KeyError):
                return self.reply(400, {"error": "INVALID_QUERY"})

        def do_HEAD(self):
            # Elasticsearch client's ping; it reveals no cluster metadata.
            if gateway.archive.plane == "O" and self.role() == "detector" and self.path == "/elasticsearch/":
                self.send_response(200)
                self.send_header("X-Elastic-Product", "Elasticsearch")
                self.end_headers()
            else:
                self.send_response(403)
                self.end_headers()
    result = ThreadingHTTPServer(address, Handler)
    result.daemon_threads = True
    return result


class KafkaBridge:
    """Only O goes through this topic. Commit an offset only after its message is durable.

    A message is durable when appended to raw or to quarantine (both fsync). Per-message data
    errors are quarantined and committed so one bad message cannot block the partition.
    Anything else (I/O, archive corruption, Kafka/commit errors, program errors) stops the
    recorder without committing and turns readiness off; the message is redelivered after restart.
    """
    def __init__(self, brokers, topic, archive, credentials, admit, consumer=None, producer=None, start=True):
        self.archive, self.topic = archive, topic
        self.credentials, self.admit = credentials, admit
        if consumer is None or producer is None:
            from kafka import KafkaConsumer, KafkaProducer
            producer = producer or KafkaProducer(bootstrap_servers=brokers.split(","), acks="all", retries=0,
                                                 max_block_ms=5000, request_timeout_ms=10000)
            consumer = consumer or KafkaConsumer(topic, bootstrap_servers=brokers.split(","),
                                                 group_id="zd-recorder-" + hashlib.sha256(topic.encode()).hexdigest()[:16],
                                                 auto_offset_reset="earliest", enable_auto_commit=False,
                                                 consumer_timeout_ms=1000)
        self.producer, self.consumer = producer, consumer
        self.stop = threading.Event()
        self.failure = None
        self.ready = False
        self.startup_end = None
        self.done = {}
        self.checked = 0.0
        self.progress = threading.Condition()
        self.thread = threading.Thread(target=self.record, daemon=True)
        if start:
            self.thread.start()

    def publish(self, event, request_id):
        if self.failure:
            raise RuntimeError("recorder unavailable")
        data = canonical(event)
        signature = hmac.new(self.credentials[event["source_component"]].encode(), data, hashlib.sha256).hexdigest()
        return self.producer.send(self.topic, data, key=event["run_id"].encode(),
                                  headers=[("request_id", request_id.encode()), ("signature", signature.encode())]).get(timeout=10)

    def handle(self, message):
        """Record or quarantine one message; Rejected means it is durably quarantined."""
        transport = {"kind": "kafka", "topic": message.topic, "partition": message.partition,
                     "offset": message.offset}
        raw = message.value if isinstance(message.value, bytes) else b""
        try:
            headers = {key: value for key, value in (message.headers or [])}
        except (TypeError, ValueError):
            headers = {}
        event, error = decode(raw)
        if error:
            self.archive.reject(error, transport, None, raw=raw, attributable=False)
        source = event.get("source_component")
        secret = self.credentials.get(source) if isinstance(source, str) else None
        signature = headers.get("signature")
        expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest().encode() if secret else b""
        if not secret or not isinstance(signature, bytes) or not hmac.compare_digest(signature, expected):
            # Never attribute an unauthenticated broker injection to a producer or a run.
            self.archive.reject("BROKER_AUTH_FAILED", transport, None, raw=raw, attributable=False)
        request_id = headers.get("request_id")
        transport["http_request_id"] = request_id.decode("utf-8", "replace") if isinstance(request_id, bytes) else ""
        # Broker ingress is trusted only after revalidation and binding, in the same transaction as append.
        return self.admit(event, source, transport, raw)

    def record(self):
        try:
            while not self.stop.is_set():
                for message in self.consumer:
                    try:
                        self.handle(message)
                    except Rejected:
                        pass  # durably quarantined; acknowledging is safe
                    self.consumer.commit()
                    with self.progress:
                        self.done[message.partition] = max(self.done.get(message.partition, 0), message.offset + 1)
                        self.progress.notify_all()
                    if not self.ready and time.monotonic() - self.checked > 1:
                        self.check_ready()
                    if self.stop.is_set():
                        break
                self.check_ready()
        except Exception as error:
            self.failure = type(error).__name__
        finally:
            with self.progress:
                self.progress.notify_all()
            self.consumer.close()

    def check_ready(self):
        """Ready once every message present at startup (acked by a previous process) is handled."""
        self.checked = time.monotonic()
        if self.ready:
            return
        assignment = list(self.consumer.assignment())
        if not assignment:
            return
        if self.startup_end is None:
            ends = self.consumer.end_offsets(assignment)
            self.startup_end = {tp.partition: ends[tp] for tp in assignment}
        positions = {tp.partition: self.consumer.position(tp) for tp in assignment}
        if all(positions.get(partition, 0) >= offset for partition, offset in self.startup_end.items()):
            with self.progress:
                for partition, offset in positions.items():
                    self.done[partition] = max(self.done.get(partition, 0), offset)
                self.ready = True
                self.progress.notify_all()

    def status(self):
        if self.failure:
            return {"ready": False, "reason": "RECORDER_FAILED:" + self.failure}
        if not self.ready:
            return {"ready": False, "reason": "CATCHING_UP"}
        return {"ready": True, "reason": None}

    def wait_for(self, targets, timeout):
        with self.progress:
            self.progress.wait_for(lambda: self.failure or (self.ready and all(
                self.done.get(partition, 0) >= offset for partition, offset in targets.items())), timeout)
            if self.failure:
                raise RuntimeError("recorder unavailable")
            return self.ready and all(self.done.get(p, 0) >= o for p, o in targets.items())

    def close(self):
        self.stop.set()
        self.thread.join(timeout=5)
        self.producer.close(timeout=5)


# Server key files are per plane; an O gateway never holds H producer roles and vice versa.
SERVER_ROLES = {
    "O": {"harness", "detector", "decision_rules", "decision_llm", "decision_single_llm", "operator_console",
          "guard", "executor", "reader", "evaluator"},
    "H": {"harness", "evaluator", "probe", "fault_executor", "effect_evaluator", "recovery_evaluator"},
}


def load_keys(path, plane):
    keys = json.loads(Path(path).read_text())
    if not isinstance(keys, dict) or not keys or any(not isinstance(v, str) or len(v) < 32 for v in keys.values()) \
            or len(set(keys.values())) != len(keys):
        raise ValueError("unique random tokens of at least 32 characters required")
    if set(keys) - SERVER_ROLES[plane]:
        raise ValueError("key file has roles outside the " + plane + " plane")
    return keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plane", choices=["H", "O"], required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--keys", required=True, help="private JSON role -> random token file")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--brokers", default="")
    parser.add_argument("--topic", default="zd.events.o")
    args = parser.parse_args()
    try:
        keys = load_keys(args.keys, args.plane)
    except ValueError as error:
        parser.error(str(error))
    if args.plane != "O" and args.brokers:
        parser.error("H does not use the shared Kafka broker")
    archive = Archive(args.root, args.plane)
    telemetry = None
    if args.plane == "O" and os.getenv("ZD_PROM_QUERIES_FILE"):
        from .telemetry import Telemetry
        telemetry = Telemetry(os.environ["ZD_PROMETHEUS_UPSTREAM"], os.environ["ZD_ES_UPSTREAM"],
                              json.loads(Path(os.environ["ZD_PROM_QUERIES_FILE"]).read_text()))
    gateway = Gateway(archive, keys, telemetry=telemetry)
    bridge = KafkaBridge(args.brokers, args.topic, archive, keys, gateway.admit) if args.brokers else None
    gateway.kafka = bridge
    http = server(gateway, ("0.0.0.0", args.port))
    try:
        http.serve_forever()
    finally:
        http.server_close()
        if bridge:
            bridge.close()
        archive.close()


if __name__ == "__main__":
    main()
