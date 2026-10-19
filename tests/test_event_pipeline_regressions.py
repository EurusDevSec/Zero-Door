"""ZER-9 fix-01/fix-02/fix-03 regressions: recorder failure paths, quarantine/seal/export, auth, audit,
DSL, depth limit, sticky archive failure on writes and on source reads.

Offline only: temp archives, loopback HTTP, an in-memory fake of the kafka module (no broker).
Tests drive public behaviour (HTTP, Archive.ingest, audit, Client) so the same file also runs
against the pre-fix sources and shows which assertions failed there (docs/evidence/ZER-9/fix-01,
fix-02, fix-03).
"""
import ast
import builtins
import contextlib
import copy
import errno
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import threading
import time
import types
import unittest
from collections import namedtuple
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline import gateway as gateway_module, store
from event_pipeline.contract import Producer, canonical, new_id, now, valid_id, validate
from event_pipeline.store import Archive
from event_pipeline.gateway import Gateway, KafkaBridge, server
from event_pipeline.audit import audit
from event_pipeline.telemetry import Telemetry
from event_pipeline.client import Client
from event_pipeline.adapters import Detector, RulesConsumer

# The pre-fix module has no ArchiveFailure; it raised ValueError for the same conditions.
ArchiveFailure = getattr(store, "ArchiveFailure", ValueError)
CLOCK = {"clock_id": "clk_test", "clock_source": "UNKNOWN", "resolution_ms": None}
TOPIC = "zd.events.o.test"
ROLES = ("harness", "detector", "decision_rules", "reader", "evaluator")
TP = namedtuple("TopicPartition", "topic partition")
Meta = namedtuple("RecordMetadata", "topic partition offset")


def eventually(predicate, timeout=5.0):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        if predicate():
            return True
        time.sleep(0.02)
    return bool(predicate())


def context(group="B1"):
    return {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
            "group": group, "method_version": "regression-not-kpi", "config_ref": "sha256:" + "1" * 64}


def contexts(ctx):
    producer = Producer("harness", "test", CLOCK)
    run = dict(ctx, trial_id=None)
    run.pop("incident_id", None)
    return [producer.event(run, "RUN_CONTEXT", {}, "o.context"), producer.event(ctx, "TRIAL_CONTEXT", {}, "o.context")]


def detected(ctx, value=0.9, producer=None):
    return (producer or Producer("detector", "test", CLOCK)).event(ctx, "DETECTED", {
        "rule_id": "HIGH_CPU", "rule_version": "test", "signature": "HIGH_CPU/frontend", "metric": "cpu",
        "value": value, "threshold": 0.8, "severity": "WARNING", "description": "Observed CPU above threshold"},
        "o.alert", target={"namespace": "target-app", "service": "frontend", "flow": None}, alert_id=new_id("alt"))


def lines(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_bytes().splitlines()] if path.exists() else []


# ---------------------------------------------------------------- fake kafka module
class Message:
    def __init__(self, partition, offset, value, headers):
        self.topic, self.partition, self.offset, self.value, self.headers = TOPIC, partition, offset, value, headers


class Broker:
    """Partition logs plus the group's committed offsets; survives recorder restarts."""
    def __init__(self, partitions=1):
        self.logs = {p: [] for p in range(partitions)}
        self.committed = {p: 0 for p in range(partitions)}
        self.gates = {p: threading.Event() for p in range(partitions)}
        for gate in self.gates.values():
            gate.set()
        self.lock = threading.Lock()
        self.commit_error = None
        self.on_commit = None  # sees the positions about to be committed

    def append(self, partition, value, headers=None):
        with self.lock:
            offset = len(self.logs[partition])
            self.logs[partition].append(Message(partition, offset, value, headers or []))
            return offset

    def partition(self, key):
        return int(hashlib.sha256(key).hexdigest(), 16) % len(self.logs)


class Consumer:
    """Iterator semantics of kafka-python: position advances per yielded record; idle returns."""
    def __init__(self, broker):
        self.broker = broker
        self.positions = dict(broker.committed)

    def __iter__(self):
        yielded = False
        for partition in sorted(self.positions):
            while self.broker.gates[partition].is_set() and self.positions[partition] < len(self.broker.logs[partition]):
                message = self.broker.logs[partition][self.positions[partition]]
                self.positions[partition] += 1
                yielded = True
                yield message
        if not yielded:
            time.sleep(0.005)

    def commit(self):
        if self.broker.commit_error:
            raise self.broker.commit_error
        if self.broker.on_commit:
            self.broker.on_commit(dict(self.positions))
        self.broker.committed.update(self.positions)

    def assignment(self):
        return {TP(TOPIC, p) for p in self.positions}

    def end_offsets(self, partitions):
        return {tp: len(self.broker.logs[tp.partition]) for tp in partitions}

    def position(self, tp):
        return self.positions[tp.partition]

    def close(self):
        pass


class Future:
    def __init__(self, value):
        self.value = value

    def get(self, timeout=None):
        return self.value


class ProducerFake:
    def __init__(self, broker):
        self.broker = broker

    def send(self, topic, value, key=None, headers=None):
        partition = self.broker.partition(key)
        return Future(Meta(topic, partition, self.broker.append(partition, value, headers)))

    def close(self, timeout=None):
        pass


def signed(event, keys):
    data = canonical(event)
    return data, [("request_id", b"ing_test"),
                  ("signature", hmac.new(keys[event["source_component"]].encode(), data, hashlib.sha256).hexdigest().encode())]


class Stack:
    """O (or H) gateway, O recorder over a fake broker, with loopback HTTP."""
    def __init__(self, directory, broker, keys, kafka=True, plane="O"):
        self.archive = Archive(Path(directory) / plane, plane)
        self.keys, self.broker = keys, broker
        self.gateway = Gateway(self.archive, keys)
        self.bridge = self.start_bridge() if kafka else None
        self.http = server(self.gateway, ("127.0.0.1", 0))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.http.server_port)

    def start_bridge(self):
        fake = types.SimpleNamespace(KafkaConsumer=lambda *a, **k: Consumer(self.broker),
                                     KafkaProducer=lambda *a, **k: ProducerFake(self.broker))
        with patch.dict(sys.modules, {"kafka": fake}):
            # Pre-fix bridge took the gateway's binding callable; the fixed one takes admit.
            bridge = KafkaBridge("fake:9092", TOPIC, self.archive, self.keys,
                                 getattr(self.gateway, "admit", None) or self.gateway.binding)
        self.gateway.kafka = bridge
        return bridge

    def restart_bridge(self):
        self.bridge.close()
        self.bridge = self.start_bridge()

    def request(self, path, role="reader", body=None, raw=None):
        data = raw if raw is not None else (canonical(body) if body is not None else None)
        request = Request(self.url + path, data=data,
                          headers={"Authorization": "Bearer " + self.keys.get(role, "x" * 40), "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=20) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def raw(self, run):
        return [r["envelope"] for r in self.archive.records(run)]

    def close(self):
        if self.bridge:
            self.bridge.close()
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(2)
        self.archive.close()


class StackCase(unittest.TestCase):
    kafka = True

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.keys = {role: hashlib.sha256(role.encode()).hexdigest() for role in ROLES}
        self.broker = Broker()
        self.stack = None

    def tearDown(self):
        if self.stack:
            self.stack.close()
        self.temp.cleanup()

    def open(self, kafka=None, seed=()):
        self.stack = Stack(self.temp.name, self.broker, self.keys, self.kafka if kafka is None else kafka)
        for event in seed:
            self.stack.archive.ingest(event, {"kind": "http", "request_id": "seed"}, "harness")
        return self.stack

    def reopen(self, **options):
        """Process restart: a new Archive re-verifies every file; the broker keeps its offsets."""
        self.stack.close()
        self.stack = None
        return self.open(**options)

    def fresh(self, plane="O"):
        """Start a subtest on an empty archive, even if the previous one failed midway."""
        if self.stack:
            self.stack.close()
            self.stack = None
        if (Path(self.temp.name) / plane).exists():
            shutil.rmtree(Path(self.temp.name) / plane)

    def scope(self):
        return lines(Path(self.temp.name) / "O" / "rejections.jsonl")

    def run_file(self, run, name):
        return lines(Path(self.temp.name) / "O" / run / name)


# ---------------------------------------------------------------- ZR9-01 recorder
class RecorderTests(StackCase):
    def test_poison_messages_are_quarantined_committed_and_not_attributed(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        stack.bridge.close()  # load the topic first, then start a fresh recorder on it
        good = detected(ctx)
        data, headers = signed(good, self.keys)
        poison = [(b"\xffnot-json", []), (b"[]", []), (b'{"x": NaN}', []), (b"1e999", []),
                  (data, [("request_id", b"ing_x"), ("signature", b"0" * 64)]), (data.replace(b"0.9", b"0.7"), headers),
                  (None, [])]
        for value, header in poison:
            self.broker.append(0, value, header)
        self.broker.append(0, data, headers)
        stack.bridge = stack.start_bridge()
        self.assertTrue(eventually(lambda: self.broker.committed[0] == len(poison) + 1), stack.bridge.failure)
        self.assertIsNone(stack.bridge.failure)
        self.assertEqual([good], [e for e in stack.raw(ctx["run_id"]) if e["event_type"] == "DETECTED"])
        quarantine = self.scope()
        self.assertEqual(len(poison), len(quarantine))
        for record in quarantine:
            self.assertIn(record["classification"], {"INVALID", "BROKER_AUTH_FAILED"})
            self.assertNotIn("envelope", record)  # unauthenticated: original bytes only, never attributed
            self.assertEqual(hashlib.sha256(bytes.fromhex(record["raw_hex"])).hexdigest(), record["raw_sha256"])
        self.assertEqual([], self.run_file(ctx["run_id"], "rejections.jsonl"))
        # Restart reads from the committed offset: the poison pill is not met again.
        stack.restart_bridge()
        time.sleep(0.2)
        self.assertIsNone(stack.bridge.failure)
        self.assertEqual(len(poison), len(self.scope()))

    def test_binding_error_in_recorder_is_quarantined_and_next_message_recorded(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx)[:1])  # RUN_CONTEXT only: TRIAL_CONTEXT missing
        orphan = detected(ctx)
        other = context()
        for event in contexts(other):
            stack.archive.ingest(event, {"kind": "http", "request_id": "seed"}, "harness")
        good = detected(other)
        for event in (orphan, good):
            self.broker.append(0, *signed(event, self.keys))
        self.assertTrue(eventually(lambda: self.broker.committed[0] == 2), stack.bridge.failure)
        self.assertIsNone(stack.bridge.failure)
        self.assertEqual(["TRIAL_CONTEXT_MISSING"], [r["classification"] for r in self.run_file(ctx["run_id"], "rejections.jsonl")])
        self.assertIn(good, stack.raw(other["run_id"]))

    def test_io_failure_is_not_acknowledged_and_turns_readiness_off(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        event = detected(ctx)
        with patch.object(Archive, "append", side_effect=OSError("disk full")):
            self.broker.append(0, *signed(event, self.keys))
            self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
        self.assertEqual(0, self.broker.committed[0])
        self.assertEqual(503, stack.request("/readyz")[0])
        self.assertEqual(200, stack.request("/livez")[0])  # liveness does not restart-loop a broken archive
        self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
        # fix-02: the archive failure is sticky, so only a process restart (which re-verifies the
        # archive; nothing was written here) resumes from the uncommitted offset.
        stack.restart_bridge()
        time.sleep(0.2)
        self.assertEqual(0, self.broker.committed[0])
        stack = self.reopen()
        self.assertTrue(eventually(lambda: self.broker.committed[0] == 1))
        self.assertEqual(1, sum(e["event_id"] == event["event_id"] for e in stack.raw(ctx["run_id"])))
        self.assertTrue(eventually(lambda: stack.request("/readyz")[0] == 200))

    def test_commit_error_stops_recorder_without_claiming_success(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        self.broker.commit_error = RuntimeError("CommitFailedError")
        self.broker.append(0, *signed(detected(ctx), self.keys))
        self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
        self.assertEqual(0, self.broker.committed[0])
        self.assertEqual("NOT_READY", stack.request("/readyz")[1]["status"])


# ---------------------------------------------------------------- ZR9-01 seal fence
class SealFenceTests(StackCase):
    def setUp(self):
        super().setUp()
        self.timeout = patch.object(gateway_module, "SEAL_TIMEOUT", 0.5, create=True)
        self.timeout.start()

    def tearDown(self):
        self.timeout.stop()
        super().tearDown()

    def test_seal_waits_for_acknowledged_event_then_includes_it(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        self.broker.gates[0].clear()  # recorder has not consumed the acked event yet
        event = detected(ctx)
        self.assertEqual(202, stack.request("/events", "detector", event)[0])
        code, body = stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})
        self.assertEqual(409, code, body)
        self.assertFalse((stack.archive.path(ctx["run_id"]) / "manifest.json").exists())
        self.broker.gates[0].set()
        self.assertTrue(eventually(lambda: stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0] == 200))
        self.assertIn(event, stack.raw(ctx["run_id"]))
        self.assertIsNone(stack.bridge.failure)

    def test_concurrent_submits_and_seal_lose_nothing(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        events = [detected(ctx) for _ in range(40)]
        outcomes = {}

        def send(chunk):
            for event in chunk:
                outcomes[event["event_id"]] = stack.request("/events", "detector", event)[0]

        threads = [threading.Thread(target=send, args=(events[i::4],)) for i in range(4)]
        for thread in threads:
            thread.start()
        time.sleep(0.05)
        with patch.object(gateway_module, "SEAL_TIMEOUT", 5, create=True):
            self.assertTrue(eventually(lambda: stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0] == 200, 10))
        for thread in threads:
            thread.join(20)
        manifest = json.loads((stack.archive.path(ctx["run_id"]) / "manifest.json").read_bytes())
        self.assertTrue(eventually(lambda: self.broker.committed[0] == len(self.broker.logs[0])))
        raw = {e["event_id"] for e in stack.raw(ctx["run_id"])}
        late = {r["envelope"]["event_id"] for r in self.run_file(ctx["run_id"], "late.jsonl")}
        acked = {k for k, v in outcomes.items() if v == 202}
        self.assertTrue(acked <= raw, "acked event missing from sealed raw")
        self.assertEqual({k for k, v in outcomes.items() if v == 409}, late)
        self.assertEqual(set(), set(outcomes) - raw - late, "submitted event neither in raw nor late")
        self.assertEqual(set(), acked & late)
        self.assertEqual(manifest["sha256"], store.file_sha(stack.archive.path(ctx["run_id"]) / "O.jsonl"))
        self.assertIsNone(stack.bridge.failure)

    def test_restart_not_ready_until_messages_acked_before_crash_are_durable(self):
        ctx = context()
        before = detected(ctx)
        self.broker.append(0, *signed(before, self.keys))  # acked by a previous process, never recorded
        self.broker.gates[0].clear()
        stack = self.open(seed=contexts(ctx))
        self.assertEqual(503, stack.request("/readyz")[0])
        self.assertEqual(409, stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0])
        self.broker.gates[0].set()
        self.assertTrue(eventually(lambda: stack.request("/readyz")[0] == 200))
        self.assertEqual(200, stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0])
        self.assertIn(before, stack.raw(ctx["run_id"]))

    def test_seal_tracks_only_the_runs_own_partition(self):
        self.broker = Broker(partitions=2)
        one, two = context(), context()
        while self.broker.partition(one["run_id"].encode()) == self.broker.partition(two["run_id"].encode()):
            two = context()
        stack = self.open(seed=contexts(one) + contexts(two))
        self.assertTrue(eventually(lambda: stack.request("/readyz")[0] == 200))
        blocked = self.broker.partition(two["run_id"].encode())
        self.broker.gates[blocked].clear()
        self.assertEqual(202, stack.request("/events", "detector", detected(one))[0])
        self.assertEqual(202, stack.request("/events", "detector", detected(two))[0])
        self.assertTrue(eventually(lambda: stack.request("/seal", "evaluator", {"run_id": one["run_id"]})[0] == 200))
        self.assertEqual(409, stack.request("/seal", "evaluator", {"run_id": two["run_id"]})[0])
        self.broker.gates[blocked].set()
        self.assertTrue(eventually(lambda: stack.request("/seal", "evaluator", {"run_id": two["run_id"]})[0] == 200))
        self.assertEqual(3, len(stack.raw(two["run_id"])))


# ---------------------------------------------------------------- ZR9-02/12 quarantine, late, export
class QuarantineTests(StackCase):
    kafka = False

    def test_http_binding_rejections_are_stored_per_run(self):
        ctx = context()
        stack = self.open()
        stray = detected(ctx)
        self.assertEqual(422, stack.request("/events", "detector", stray)[0])  # RUN_CONTEXT_MISSING
        run_ctx, trial_ctx = contexts(ctx)
        self.assertEqual(201, stack.request("/events", "harness", run_ctx)[0])
        self.assertEqual(422, stack.request("/events", "detector", detected(ctx))[0])  # TRIAL_CONTEXT_MISSING
        self.assertEqual(201, stack.request("/events", "harness", trial_ctx)[0])
        changed = copy.deepcopy(trial_ctx)
        changed["incident_id"] = new_id("inc")
        changed["event_id"] = new_id("evt")
        self.assertEqual(422, stack.request("/events", "harness", changed)[0])  # CONTEXT_IMMUTABLE
        wrong = detected(dict(ctx, incident_id=new_id("inc")))
        self.assertEqual(422, stack.request("/events", "detector", wrong)[0])  # LINK_CONFLICT
        stored = [r["classification"] for r in self.run_file(ctx["run_id"], "rejections.jsonl")]
        self.assertEqual(["RUN_CONTEXT_MISSING", "TRIAL_CONTEXT_MISSING", "CONTEXT_IMMUTABLE", "LINK_CONFLICT"], stored)
        self.assertEqual(wrong, self.run_file(ctx["run_id"], "rejections.jsonl")[-1]["envelope"])

    def test_undecodable_bodies_keep_original_bytes(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        event = detected(ctx)
        bodies = [canonical(event).replace(b"0.9", b"NaN"), canonical(event).replace(b"0.9", b"Infinity"),
                  canonical(event).replace(b"0.9", b"1e999"), b"\xff{}", b"[]", b'"text"']
        for body in bodies:
            self.assertEqual(422, stack.request("/events", "detector", raw=body)[0])
        unhashable = copy.deepcopy(event)
        unhashable["event_id"] = {"nested": "id"}
        self.assertEqual(422, stack.request("/events", "detector", unhashable)[0])
        scoped = self.scope()
        self.assertEqual(bodies, [bytes.fromhex(r["raw_hex"]) for r in scoped])
        self.assertEqual({"detector"}, {r["principal"] for r in scoped})
        self.assertEqual("INVALID_ID", self.run_file(ctx["run_id"], "rejections.jsonl")[0]["classification"])

    def test_late_duplicate_and_conflict_after_seal_never_change_sealed_raw(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        first = detected(ctx)
        stack.archive.ingest(first, {"kind": "http", "request_id": "a"}, "detector")
        sealed = stack.archive.seal(ctx["run_id"])
        self.assertEqual("SEALED_DUPLICATE", stack.archive.ingest(first, {"kind": "http"}, "detector")["status"])
        self.assertFalse((stack.archive.path(ctx["run_id"]) / "late.jsonl").exists())
        late = detected(ctx)
        code, body = stack.request("/events", "detector", late)
        self.assertEqual((409, "LATE_INGEST"), (code, body.get("classification")))
        self.assertEqual(409, stack.request("/events", "detector", late)[0])  # same late copy: no new line
        conflict = copy.deepcopy(first)
        conflict["payload"]["value"] = 0.5
        with self.assertRaises(ValueError):
            stack.archive.ingest(conflict, {"kind": "http"}, "detector")
        stored = self.run_file(ctx["run_id"], "late.jsonl")
        self.assertEqual(["LATE_INGEST", "INTEGRITY_ERROR"], [r["classification"] for r in stored])
        self.assertEqual(late, stored[0]["envelope"])
        self.assertEqual(sealed, stack.archive.seal(ctx["run_id"]))
        output = Path(self.temp.name) / "export"
        stack.archive.export(ctx["run_id"], output)
        described = json.loads((output / "export.json").read_bytes())
        self.assertEqual(2, described["late"]["lines"])
        self.assertEqual(hashlib.sha256((output / "late.jsonl").read_bytes()).hexdigest(), described["late"]["sha256"])
        self.assertEqual(sealed["sha256"], hashlib.sha256((output / "O.jsonl").read_bytes()).hexdigest())

    def test_rejection_only_run_seals_and_exports_with_archive_scope(self):
        ctx = context()
        stack = self.open()
        self.assertEqual(422, stack.request("/events", "detector", detected(ctx))[0])
        self.assertEqual(422, stack.request("/events", "detector", raw=b"[]")[0])
        manifest = stack.archive.seal(ctx["run_id"])
        self.assertEqual((0, 1), (manifest["lines"], manifest["rejections"]["lines"]))
        output = Path(self.temp.name) / "export"
        stack.archive.export(ctx["run_id"], output)
        described = json.loads((output / "export.json").read_bytes())
        self.assertEqual("ARCHIVE_GLOBAL_NOT_ATTRIBUTED_TO_RUN", described["archive_scope_quarantine"]["scope"])
        self.assertEqual(1, described["archive_scope_quarantine"]["files"]["rejections.jsonl"]["lines"])
        self.assertTrue((output / "archive-scope" / "rejections.jsonl").exists())
        self.assertEqual(manifest["rejections"]["sha256"], described["files"]["rejections.jsonl"]["sha256"])
        with self.assertRaises(FileExistsError):
            stack.archive.export(ctx["run_id"], output)  # never overwrite an earlier export

    def test_editing_rejection_or_late_line_is_detected(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        wrong = detected(dict(ctx, incident_id=new_id("inc")))
        self.assertEqual(422, stack.request("/events", "detector", wrong)[0])
        stack.archive.seal(ctx["run_id"])
        self.assertEqual(409, stack.request("/events", "detector", detected(ctx))[0])
        stack.close()
        self.stack = None
        directory = Path(self.temp.name) / "O" / ctx["run_id"]
        for name in ("late.jsonl", "rejections.jsonl"):
            path = directory / name
            original = path.read_bytes()
            path.write_bytes(original.replace(b"Observed CPU", b"Observed GPU"))
            with self.assertRaises(ValueError):
                Archive(Path(self.temp.name) / "O", "O").close()
            path.write_bytes(original)
        Archive(Path(self.temp.name) / "O", "O").close()

    def test_conflicting_contexts_sent_concurrently_cannot_both_be_recorded(self):
        stack = self.open()
        original = Gateway.binding

        def slow(gateway, event):
            original(gateway, event)
            time.sleep(0.05)  # widen the window between binding and append

        with patch.object(Gateway, "binding", slow):
            for _ in range(5):
                ctx = context()
                stack.request("/events", "harness", contexts(ctx)[0])
                variants = [contexts(dict(ctx, incident_id=new_id("inc")))[1] for _ in range(2)]
                barrier = threading.Barrier(2)
                codes = []

                def send(event):
                    barrier.wait()
                    codes.append(stack.request("/events", "harness", event)[0])

                threads = [threading.Thread(target=send, args=(v,)) for v in variants]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(5)
                trials = [e for e in stack.raw(ctx["run_id"]) if e["event_type"] == "TRIAL_CONTEXT"]
                self.assertEqual(1, len(trials))
                self.assertEqual([201, 422], sorted(codes))
                self.assertEqual(["CONTEXT_IMMUTABLE"], [r["classification"] for r in self.run_file(ctx["run_id"], "rejections.jsonl")])

    def test_live11_raw_and_manifest_still_open_and_reseal_unchanged(self):
        export = ROOT / "docs/evidence/ZER-9/live-11/export/O"
        receipt = json.loads((ROOT / "docs/evidence/ZER-9/live-11/receipt.json").read_bytes())
        run = receipt["context"]["run_id"]
        directory = Path(self.temp.name) / "legacy" / run
        directory.mkdir(parents=True)
        for name in ("O.jsonl", "manifest.json"):
            shutil.copyfile(export / name, directory / name)
        legacy = Archive(Path(self.temp.name) / "legacy", "O")
        try:
            self.assertEqual(json.loads((export / "manifest.json").read_bytes()), legacy.seal(run))
            self.assertEqual(5, len(legacy.records(run)))
            legacy.export(run, Path(self.temp.name) / "legacy-export")
            self.assertEqual((export / "O.jsonl").read_bytes(), (Path(self.temp.name) / "legacy-export" / "O.jsonl").read_bytes())
        finally:
            legacy.close()


# ---------------------------------------------------------------- readiness and key files (ZR9-01/04)
class BoundaryRegressionTests(StackCase):
    kafka = False

    def test_probes_and_server_key_scope(self):
        stack = self.open()
        self.assertEqual((200, {"status": "ALIVE"}), stack.request("/livez", role="none"))
        self.assertEqual(200, stack.request("/readyz", role="none")[0])
        load = gateway_module.load_keys
        path = Path(self.temp.name) / "keys.json"
        for plane, extra in (("O", "probe"), ("H", "detector")):
            path.write_text(json.dumps({"evaluator": "e" * 40, extra: "x" * 40}))
            with self.assertRaises(ValueError):
                load(path, plane)

    def test_actor_key_files_and_source_binding(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        path = Path(self.temp.name) / "actor.json"
        env = {"ZD_EVENT_URL": stack.url, "ZD_O_KEYS_FILE": str(path), "ZD_RUN_ID": ctx["run_id"],
               "ZD_TRIAL_ID": ctx["trial_id"], "ZD_PRODUCER_VERSION": "test", "ZD_CLOCK_ID": "clk"}
        with patch.dict(os.environ, env):
            for source, keys, ok in (("detector", ("detector", "reader"), True),
                                     ("detector", ("detector", "decision_rules", "reader"), False),
                                     ("decision_rules", ("decision_rules", "reader"), True),
                                     ("decision_rules", ("decision_rules", "reader", "harness"), False),
                                     ("detector", ("detector",), False)):
                path.write_text(json.dumps({k: self.keys[k] for k in keys}))
                if ok:
                    self.assertEqual(self.keys[source], Client.from_env(source).token)
                else:
                    with self.assertRaises(ValueError):
                        Client.from_env(source)
        decision = Producer("decision_rules", "test", CLOCK).event(ctx, "DECISION", {
            "stage": "PROPOSAL", "decision_source": "RULES", "inputs": [], "response_kind": "NO_ACTION",
            "proposal": None, "fallback": False, "fallback_of": None, "prompt_version": None,
            "prompt_sha256": None, "evidence_package_version": "test"}, "o.decision", decision_id=new_id("dec"))
        self.assertEqual(422, stack.request("/events", "detector", decision)[0])  # detector token cannot write as rules
        self.assertEqual(201, stack.request("/events", "decision_rules", decision)[0])

    def test_r1_reset_endpoint_refuses_without_touching_state(self):
        tree = ast.parse((ROOT / "agent-orchestrator/hephaestus/main.py").read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "experiment_reset")
        function.decorator_list = []

        class Rejected(Exception):
            def __init__(self, **kw):
                self.code = kw["status_code"]

        state = {"heal_cooldowns": {"x": 1}, "heal_history": [1]}
        scope = {"r1_client": object(), "HTTPException": Rejected, **state}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual-reset", "exec"), scope)
        with self.assertRaises(Rejected) as caught:
            scope["experiment_reset"]()
        self.assertEqual(409, caught.exception.code)
        self.assertEqual({"x": 1}, state["heal_cooldowns"])


# ---------------------------------------------------------------- ZR9-08 retry policy
class RetryTests(unittest.TestCase):
    def fake(self, errors):
        class Fake:
            producer = Producer("detector", "test", CLOCK)
            sent = []

            def context(self):
                return ctx

            def publish(self, event):
                self.sent.append(copy.deepcopy(event))
                if errors:
                    raise errors.pop(0)
        ctx = context()
        return Fake()

    @staticmethod
    def http(code):
        return HTTPError("http://gateway/events", code, "test", {}, None)

    def test_permanent_refusal_drops_envelope_unknown_outcome_keeps_it(self):
        for error, same in ((self.http(422), False), (self.http(409), False), (self.http(503), True),
                            (self.http(429), True), (TimeoutError("KAFKA_ACK_WITHOUT_DURABLE_RECEIPT"), True)):
            fake = self.fake([error])
            detector = Detector(fake)
            with self.assertRaises(type(error)):
                detector.publish("HIGH_CPU", "frontend", "cpu", 0.9, 0.8, "first", "WARNING")
            detector.publish("HIGH_CPU", "frontend", "cpu", 0.99, 0.8, "later", "CRITICAL")
            self.assertEqual(same, fake.sent[0] == fake.sent[1], error)
            if not same:
                self.assertEqual((0.99, "CRITICAL"), (fake.sent[1]["payload"]["value"], fake.sent[1]["payload"]["severity"]))

    def test_rules_consumer_does_not_regenerate_a_refused_decision(self):
        ctx = context()
        attempts = []

        class Fake:
            trial = ctx["trial_id"]
            producer = Producer("decision_rules", "test", CLOCK)
            rows = [{"envelope": detected(ctx)}]

            def records(self):
                return self.rows

            def publish(self, event):
                attempts.append(event["event_id"])
                raise RetryTests.http(422)

        consumer = RulesConsumer(Fake(), lambda *_: "SCALE_UP")
        for _ in range(3):
            try:
                consumer.poll()
            except HTTPError:
                pass
        self.assertEqual(1, len(attempts))


# ---------------------------------------------------------------- ZR9-07 log DSL
class LogQueryTests(unittest.TestCase):
    GAIA = {"query": {"bool": {"must": [{"term": {"kubernetes.namespace_name.keyword": "target-app"}},
                                         {"range": {"@timestamp": {"gte": "now-30s", "lte": "now"}}}],
                               "should": [{"match_phrase": {"message": "ERROR"}}, {"match_phrase": {"message": "OR '1'='1"}}],
                               "minimum_should_match": 1}}, "size": 50}

    def setUp(self):
        self.calls = []

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(handler):
                body = handler.rfile.read(int(handler.headers["Content-Length"]))
                self.calls.append((handler.path, json.loads(body)))
                data = json.dumps({"took": 1, "timed_out": False, "hits": {"hits": [
                    {"_source": {"kubernetes": {"namespace_name": "target-app", "pod_name": "frontend-a-b"}, "message": "OOMKilled"}}]}}).encode()
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json")
                handler.send_header("Content-Length", str(len(data)))
                handler.end_headers()
                handler.wfile.write(data)

        self.upstream = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        threading.Thread(target=self.upstream.serve_forever, daemon=True).start()
        self.telemetry = Telemetry("http://127.0.0.1:1", "http://127.0.0.1:%d" % self.upstream.server_port, [])

    def tearDown(self):
        self.upstream.shutdown()
        self.upstream.server_close()

    def test_gaia_query_passes_and_lookups_scripts_and_costly_clauses_do_not(self):
        result = self.telemetry.logs(copy.deepcopy(self.GAIA))
        self.assertEqual(1, result["hits"]["total"]["value"])
        path, sent = self.calls[0]
        self.assertEqual("/zero-door-logs-*/_search", path)
        self.assertEqual("target-app", sent["query"]["bool"]["filter"][0]["term"]["kubernetes.namespace_name.keyword"])
        deep = {"match_all": {}}
        for _ in range(8):
            deep = {"bool": {"must": [deep]}}
        rejected = [
            {"terms": {"user": {"index": "any-other-index", "id": "1", "path": "secret"}}},
            {"script": {"script": {"source": "true"}}},
            {"more_like_this": {"like": [{"_index": "other", "_id": "1"}]}},
            {"percolate": {"field": "q", "index": "other", "id": "1"}},
            {"regexp": {"message": ".*"}}, {"wildcard": {"message": "*a*"}},
            {"query_string": {"query": "*"}}, {"bool": {"must": [{"match": {"message": {"query": "x", "fuzziness": 2}}}]}},
            {"term": {"_index": "zero-door-control"}}, deep,
        ]
        for query in rejected:
            with self.assertRaises(ValueError, msg=query):
                self.telemetry.logs({"query": query})
        with self.assertRaises(ValueError):
            self.telemetry.logs({"query": {"match_all": {}}, "size": "50"})
        self.assertEqual(1, len(self.calls))  # no rejected query reached the upstream


# ---------------------------------------------------------------- ZR9-03 audit
def seeded_id(rng, kind):
    value = "%032x" % rng.getrandbits(128)
    return kind + "_" + value[:12] + "4" + value[13:16] + rng.choice("89ab") + value[17:]


def manifest(reveal=("stress",), entries=()):
    return Producer("harness", "test", CLOCK).event(context(), "HARNESS_MANIFEST", {
        "manifest_version": "test", "allowlist_version": "test", "reveal_terms": list(reveal),
        "entries": list(entries)}, "h.audit")


def truth(case_class="C4", variant="v1", cause="cpu_exhaustion", attack="cpu-hog"):
    return {"event_type": "GROUND_TRUTH_LOCKED", "payload": {"case_class": case_class, "variant_id": variant,
            "cause": cause, "attack_type": attack}}


def trace(rng):
    """A clean DETECTED + DECISION pair whose identifiers are seeded, valid UUIDv4 IDs."""
    ctx = context()
    for key, kind in (("run_id", "run"), ("trial_id", "trl"), ("incident_id", "inc")):
        ctx[key] = seeded_id(rng, kind)
    alert = detected(ctx)
    alert.update(event_id=seeded_id(rng, "evt"), alert_id=seeded_id(rng, "alt"), source_instance="src-%032x" % rng.getrandbits(128))
    decision = Producer("decision_rules", "test", CLOCK).event(ctx, "DECISION", {
        "stage": "PROPOSAL", "decision_source": "RULES", "inputs": [{"event_id": alert["event_id"], "received_at": now()}],
        "response_kind": "NO_ACTION", "proposal": None, "fallback": False, "fallback_of": None, "prompt_version": None,
        "prompt_sha256": None, "evidence_package_version": "test"}, "o.decision", decision_id=seeded_id(rng, "dec"),
        causation_id=alert["event_id"])
    decision.update(event_id=seeded_id(rng, "evt"), source_instance="src-%032x" % rng.getrandbits(128))
    return [alert, decision]


class AuditTests(unittest.TestCase):
    def test_hex_ids_containing_label_characters_are_clean(self):
        hexy = "c4" * 6 + "4" + "c0a" + "b" + "abc4c0c4c0ab4c0"
        self.assertTrue(valid_id("inc_" + hexy, "inc"))
        ctx = dict(context(), incident_id="inc_" + hexy, run_id="run_" + hexy, trial_id="trl_" + hexy)
        event = detected(ctx)
        event["event_id"] = "evt_" + hexy
        for label in ("C4", "C0", "ab", "v1", "4c"):
            result = audit([manifest(), truth(case_class=label, variant="ab")], [event], access_complete=True)
            self.assertEqual("CLEAN", result["result"], (label, result))

    def test_1000_clean_traces_per_label_have_no_false_positive(self):
        rng = random.Random(20261019)
        traces = [trace(rng) for _ in range(1000)]
        for label in ("C0", "C1", "C2", "C3", "C4", "C5", "v1", "ab"):
            h = [manifest(), truth(case_class=label, variant=label)]
            positives = sum(audit(h, events, access_complete=True)["result"] != "CLEAN" for events in traces)
            self.assertEqual(0, positives, label)

    def test_labels_in_identifier_fields_with_valid_ids_are_detected_by_label_path(self):
        h = [manifest(reveal=["stress"]), truth()]
        cases = {"target.service": ("target", "service", "frontend-stress"),
                 "stream reveal_term": ("stream", None, "o.cpu-stress"),
                 "stream attack_type": ("stream", None, "o.cpu-hog"),
                 "source_instance case_class": ("source_instance", None, "src-c4-1"),
                 "stream cause": ("stream", None, "o.alert.cpu_exhaustion"),
                 "target.flow variant": ("target", "flow", "checkout:v1")}
        for name, (key, sub, value) in cases.items():
            event = detected(context())
            if sub:
                event[key][sub] = value
            else:
                event[key] = value
            self.assertIsNone(validate(event, "O"), name)
            self.assertEqual(["LABEL_IN_METADATA"], audit(h, [event], access_complete=True)["findings"], name)
        forged = detected(context())
        forged["incident_id"] = "inc_cpu-stress-case-1"
        self.assertEqual(["INVALID_ID", "LABEL_IN_METADATA"], audit(h, [forged], access_complete=True)["findings"])

    def test_other_rules_keep_their_meaning(self):
        ctx = context()
        event = detected(ctx)
        event["payload"]["description"] = "natural log: stress test C4 from 192.0.2.9"  # telemetry text, not scanned for labels
        observable = {"kind": "ip", "value": "192.0.2.9", "class": "OBSERVABLE", "o_visible": False,
                      "allowed_o": [{"source_component": "detector", "field": "payload.description"}]}
        h = [manifest(entries=[observable]), truth()]
        self.assertEqual("CLEAN", audit(h, [event], access_complete=True)["result"])
        self.assertEqual("UNKNOWN", audit(h, [event])["result"])
        self.assertEqual("UNKNOWN", audit([truth()], [event], access_complete=True)["result"])
        canary = copy.deepcopy(event)
        canary["payload"]["description"] = "x canary-77 y"
        self.assertIn("CANARY", audit(h + [{"event_type": "RUN_STARTED", "payload": {"canary_token": "canary-77"}}], [canary], access_complete=True)["findings"])
        secret = manifest(entries=[{"kind": "command", "value": "cmd-9f2", "class": "SECRET", "o_visible": False}])
        leaked = copy.deepcopy(event)
        leaked["payload"]["description"] = "saw cmd-9f2"
        self.assertIn("HARNESS_SECRET", audit([secret], [leaked], access_complete=True)["findings"])
        outside = copy.deepcopy(event)
        outside["target"]["service"] = "192.0.2.9"
        self.assertIn("OBSERVABLE_OUTSIDE_ALLOWLIST", audit(h, [outside], access_complete=True)["findings"])
        odd = manifest(entries=[{"kind": "pod", "value": "x", "class": "MAYBE", "o_visible": True}])
        self.assertIn("UNKNOWN_MANIFEST_CLASS", audit([odd], [event], access_complete=True)["unknown"])

    def test_secret_entries_clean_leaked_and_missing_evidence(self):
        event = detected(context())
        entry = {"kind": "command", "value": "cmd-9f2", "class": "SECRET", "o_visible": False}
        clean = audit([manifest(entries=[entry]), truth()], [event], access_complete=True)
        self.assertEqual(("CLEAN", [], []), (clean["result"], clean["findings"], clean["unknown"]))
        leaked = copy.deepcopy(event)
        leaked["payload"]["description"] = "saw cmd-9f2"
        self.assertEqual(["HARNESS_SECRET"], audit([manifest(entries=[entry]), truth()], [leaked], access_complete=True)["findings"])
        visible = manifest(entries=[dict(entry, o_visible=True)])
        self.assertEqual(["HARNESS_SECRET"], audit([visible, truth()], [event], access_complete=True)["findings"])
        # Missing evidence stays UNKNOWN; the fix does not turn absence into CLEAN.
        self.assertEqual(["ACCESS_EVIDENCE_MISSING"], audit([manifest(entries=[entry]), truth()], [event])["unknown"])
        self.assertEqual(["HARNESS_MANIFEST_MISSING"], audit([truth()], [event], access_complete=True)["unknown"])
        odd = manifest(entries=[dict(entry, **{"class": "MAYBE"})])
        self.assertEqual(["UNKNOWN_MANIFEST_CLASS"], audit([odd, truth()], [event], access_complete=True)["unknown"])

    def test_neutral_resource_rule_uses_whole_tokens(self):
        event = detected(context())
        clean = manifest(entries=[{"kind": "pod", "value": "wrk-ac4f9e", "class": "NEUTRAL", "o_visible": True}])
        self.assertEqual("CLEAN", audit([clean, truth()], [event], access_complete=True)["result"])
        for value in ("wrk-c4-9e", "frontend-stress-7", "cpu-hog-runner"):
            revealing = manifest(entries=[{"kind": "pod", "value": value, "class": "NEUTRAL", "o_visible": True}])
            self.assertIn("REVEALING_RESOURCE", audit([revealing, truth()], [event], access_complete=True)["findings"], value)

    def test_live11_o_is_clean_against_reconstructed_labels(self):
        """OFFLINE_RECONSTRUCTION: live-11 raw is unchanged; labels/manifest entries are synthetic."""
        live = ROOT / "docs/evidence/ZER-9/live-11"
        receipt = json.loads((live / "receipt.json").read_bytes())
        h = [r["envelope"] for r in lines(live / "export/H/H.jsonl")]
        rows = lines(live / "export/O/O.jsonl")
        surfaces = receipt["query_surfaces"] + [{"source_component": "recorder", "field": "transport.topic",
                                                 "text": r["transport"]["topic"]} for r in rows]
        entries = [{"kind": "namespace", "value": receipt["namespace"], "class": "NEUTRAL", "o_visible": True},
                   {"kind": "topic", "value": receipt["topic"], "class": "NEUTRAL", "o_visible": True}]
        for label in ("C0", "C1", "C2", "C3", "C4", "C5"):
            labelled = h + [manifest(entries=entries), truth(case_class=label)]
            result = audit(labelled, [r["envelope"] for r in rows], surfaces=surfaces, access_complete=True)
            self.assertEqual(("CLEAN", []), (result["result"], result["findings"]), label)


class VerifierTests(unittest.TestCase):
    """Offline checks of the live verifier's pure helpers; nothing here touches a cluster."""
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("zer9_verifier", ROOT / "infrastructure/scripts/verify-event-pipeline.py")
        cls.verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.verifier)

    def test_actor_secrets_hold_one_producer_role_each(self):
        o_keys = {role: role * 8 for role in ROLES}
        files = self.verifier.actor_key_files(o_keys)
        producers = {"detector", "decision_rules", "operator_console", "harness", "evaluator"}
        self.assertEqual({"detector", "reader"}, set(files["event-o-gaia"]))
        self.assertEqual({"decision_rules", "reader"}, set(files["event-o-hephaestus"]))
        self.assertEqual({"reader"}, set(files["event-o-observer"]))
        self.assertTrue(all(len(set(keys) & producers) <= 1 for keys in files.values()))

    def test_harness_manifest_declares_created_values_and_controls_use_label_path(self):
        harness = Producer("harness", "test", CLOCK)
        ctx = context()
        payload = self.verifier.harness_manifest("zd-zer9-0a1b2c3d4e5f", "zd.events.o.0a1b2c3d4e5f", "zero-door/events:zer9-x", "0a1b2c3d4e5f")
        manifest_event = harness.event(ctx, "HARNESS_MANIFEST", payload, "h.audit")
        self.assertIsNone(validate(manifest_event, "H", "harness"))
        self.assertIn({"kind": "topic", "value": "zd.events.o.0a1b2c3d4e5f", "class": "NEUTRAL", "o_visible": True}, payload["entries"])
        o_events = contexts(ctx)
        detection = detected(ctx)
        o_events.append(detection)
        controls = self.verifier.leak_controls([manifest_event], o_events, detection, [], True, harness, ctx)
        self.assertEqual("CLEAN", controls["clean"]["result"], controls["clean"])
        self.assertEqual(["INVALID_ID", "LABEL_IN_METADATA"], controls["injected_incident_id"]["findings"])
        self.assertEqual(["LABEL_IN_METADATA"], controls["injected_stream_valid_ids"]["findings"])
        self.assertEqual(["LABEL_IN_METADATA"], controls["injected_target_valid_ids"]["findings"])

    def test_seal_409_is_retried_and_never_taken_as_success(self):
        calls = []

        def post(url, key, body, path):
            calls.append(path)
            if len(calls) < 3:
                raise HTTPError(url + path, 409, "SEAL_PENDING", {}, None)
            return {"run_id": body["run_id"]}

        with patch.object(self.verifier, "post", post), patch.object(self.verifier.time, "sleep"):
            manifest, history = self.verifier.seal_with_retry("http://o", "k", "run_x")
            self.assertEqual(("run_x", 2), (manifest["run_id"], len(history)))
            calls.clear()
            with patch.object(self.verifier, "post", side_effect=HTTPError("u", 409, "SEAL_PENDING", {}, None)):
                with self.assertRaises(TimeoutError):
                    self.verifier.seal_with_retry("http://o", "k", "run_x", attempts=3)


# ---------------------------------------------------------------- fix-02 FX01 depth limit
def nest(levels, kind):
    """`levels` containers deep: [[...['x']...]] or {"a": {"a": ... "x"}}."""
    value = "x"
    for _ in range(levels):
        value = [value] if kind == "list" else {"a": value}
    return value


def deep_detected(ctx, levels, kind):
    # Built after the Producer: its own validation would hit the same recursion.
    event = detected(ctx)
    event["payload"]["extra"] = nest(levels, kind)
    return event


class DepthLimitTests(StackCase):
    """FX01: JSON that parses but nests past the validator's safe recursion is quarantined as bytes."""
    def test_deep_kafka_messages_are_quarantined_committed_and_not_replayed(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        stack.bridge.close()
        deep = [deep_detected(ctx, 520, "list"), deep_detected(ctx, 520, "dict")]
        good = detected(ctx)
        messages = [signed(event, self.keys) for event in deep + [good]]
        for data, _ in messages:
            self.assertIsNone(store.decode(data)[1])  # valid, strict JSON: not a decode error
        seen = []
        # Commit only after the message is durable: count stored lines at each commit.
        self.broker.on_commit = lambda positions: seen.append(
            (positions[0], len(self.run_file(ctx["run_id"], "rejections.jsonl")) + len(stack.archive.records(ctx["run_id"]))))
        for data, headers in messages:
            self.broker.append(0, data, headers)
        stack.bridge = stack.start_bridge()
        self.assertTrue(eventually(lambda: self.broker.committed[0] == 3), stack.bridge.failure)
        self.assertIsNone(stack.bridge.failure)
        stored_before = len(contexts(ctx))
        self.assertEqual([(1, stored_before + 1), (2, stored_before + 2), (3, stored_before + 3)], seen)
        self.broker.on_commit = None
        self.assertIn(good, stack.raw(ctx["run_id"]))
        quarantine = self.run_file(ctx["run_id"], "rejections.jsonl")
        self.assertEqual([data for data, _ in messages[:2]], [bytes.fromhex(r["raw_hex"]) for r in quarantine])
        for record in quarantine:
            # HMAC-verified, so attributed to the run and producer; kept as bytes, never parsed back.
            self.assertEqual(("INVALID", "detector"), (record["classification"], record["principal"]))
            self.assertNotIn("envelope", record)
            self.assertEqual(hashlib.sha256(bytes.fromhex(record["raw_hex"])).hexdigest(), record["raw_sha256"])
        self.assertEqual(200, stack.request("/readyz")[0])
        stack.restart_bridge()
        time.sleep(0.2)
        self.assertIsNone(stack.bridge.failure)
        self.assertEqual(2, len(self.run_file(ctx["run_id"], "rejections.jsonl")))
        stack = self.reopen()  # a new process re-reads the quarantine lines safely
        time.sleep(0.2)
        self.assertEqual((None, 3), (stack.bridge.failure, self.broker.committed[0]))

    def test_deep_http_bodies_are_rejected_with_bytes_on_both_transports(self):
        for kafka in (True, False):
            with self.subTest(kafka=kafka):
                self.fresh()
                ctx = context()
                stack = self.open(kafka=kafka, seed=contexts(ctx))
                published = len(self.broker.logs[0])
                bodies = [canonical(deep_detected(ctx, levels, kind)) for levels, kind in ((520, "list"), (520, "dict"), (31, "list"))]
                for body in bodies:
                    self.assertEqual((422, "INVALID"), (lambda r: (r[0], r[1].get("classification")))(
                        stack.request("/events", "detector", raw=body)))
                self.assertEqual(published, len(self.broker.logs[0]))  # nothing reached Kafka
                quarantine = self.run_file(ctx["run_id"], "rejections.jsonl")
                self.assertEqual(bodies, [bytes.fromhex(r["raw_hex"]) for r in quarantine])
                # Healthy control: the limit (32 levels in all) still admits normal nesting.
                ok = deep_detected(ctx, 30, "dict")
                self.assertEqual(202 if kafka else 201, stack.request("/events", "detector", ok)[0])
                self.assertTrue(eventually(lambda: ok in stack.raw(ctx["run_id"])))
                self.assertEqual(200, stack.request("/readyz")[0])

    def test_direct_ingest_of_deep_objects_never_dies_on_the_reject_path(self):
        archive = Archive(Path(self.temp.name) / "O", "O")
        try:
            ctx = context()
            for event in contexts(ctx):
                archive.ingest(event, {"kind": "test"}, "harness")
            events = [deep_detected(ctx, levels, "dict") for levels in (520, 5000)]  # 5000: past json.dumps/repr
            for event in events:
                with self.assertRaises(store.Rejected) as caught:
                    archive.ingest(event, {"kind": "test"}, "detector")
                self.assertEqual("INVALID", caught.exception.classification)
            first, second = self.run_file(ctx["run_id"], "rejections.jsonl")
            self.assertEqual(canonical(events[0]), bytes.fromhex(first["raw_hex"]))
            self.assertEqual(("canonical", "unrepresentable"), (first["raw_kind"], second["raw_kind"]))
            self.assertEqual(hashlib.sha256(bytes.fromhex(first["raw_hex"])).hexdigest(), first["raw_sha256"])
            good = detected(ctx)
            self.assertEqual("RECORDED", archive.ingest(good, {"kind": "test"}, "detector")["status"])
        finally:
            archive.close()
        Archive(Path(self.temp.name) / "O", "O").close()  # reopens: quarantine lines are shallow


# ---------------------------------------------------------------- fix-02 FX02 sticky archive failure
def partial_append(path, record):
    """An interrupted append: some bytes reach the file, then the write fails."""
    with open(path, "ab") as handle:
        handle.write(b'{"ingest_id":')
        handle.flush()
    raise OSError("simulated partial disk write")


class StickyFailureTests(StackCase):
    """FX02: after an uncertain write nothing more is acknowledged, appended, sealed or exported."""
    kafka = False

    def h_stack(self):
        self.stack = Stack(self.temp.name, self.broker, self.keys, kafka=False, plane="H")
        return self.stack

    def sizes(self):
        return {str(p): p.stat().st_size for p in Path(self.temp.name).rglob("*.jsonl")}

    def assert_refuses_everything(self, stack, run, event, plane_dir):
        before = self.sizes()
        self.assertEqual((503, "ARCHIVE_FAILED:OSError"), (lambda r: (r[0], r[1]["reason"]))(stack.request("/readyz")))
        self.assertEqual(200, stack.request("/livez")[0])
        self.assertEqual(503, stack.request("/events", "harness" if plane_dir == "H" else "detector", event)[0])
        self.assertEqual(503, stack.request("/events", "harness", raw=b"\xffbad")[0])  # cannot quarantine either
        self.assertEqual(503, stack.request("/seal", "evaluator", {"run_id": run})[0])
        with self.assertRaises(ArchiveFailure):
            stack.archive.records(run)
        with self.assertRaises(ArchiveFailure):
            stack.archive.export(run, Path(self.temp.name) / "export")
        self.assertFalse((Path(self.temp.name) / "export").exists())
        self.assertEqual(before, self.sizes())  # no byte added to the broken archive

    def test_h_and_direct_o_partial_append_is_sticky_and_reopen_refuses(self):
        for plane in ("H", "O"):
            with self.subTest(plane=plane):
                self.fresh(plane)
                ctx = context()
                if plane == "H":
                    stack, first, second = self.h_stack(), manifest(), manifest()
                    first["run_id"] = second["run_id"] = ctx["run_id"]
                    role = "harness"
                else:
                    stack, role = self.open(seed=contexts(ctx)), "detector"
                    first, second = detected(ctx), detected(ctx)
                # Healthy and invalid-input controls: a quarantined rejection does not stop the archive.
                self.assertEqual(422, stack.request("/events", role, raw=b"[]")[0])
                self.assertEqual(201, stack.request("/events", role, first)[0])
                self.assertEqual(200, stack.request("/readyz")[0])
                raw = Path(self.temp.name) / plane / ctx["run_id"] / (plane + ".jsonl")
                with patch.object(Archive, "append", side_effect=partial_append):
                    self.assertEqual(503, stack.request("/events", role, second)[0])
                broken = raw.read_bytes()
                self.assertTrue(broken.endswith(b'{"ingest_id":'))
                self.assert_refuses_everything(stack, ctx["run_id"], second, plane)
                stack.close()
                self.stack = None
                with self.assertRaises(ArchiveFailure):
                    Archive(Path(self.temp.name) / plane, plane)  # restart refuses the cut line
                self.assertEqual(broken, raw.read_bytes())  # evidence untouched, no truncation

    def test_fsync_and_quarantine_append_failures_are_sticky(self):
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        with patch.object(store.os, "fsync", side_effect=OSError("fsync EIO")):
            self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
        self.assert_refuses_everything(stack, ctx["run_id"], detected(ctx), "O")
        # The line was complete before fsync failed: restart re-verifies it and opens; the producer
        # got 503 and its retry of the same envelope is a DUPLICATE (at-least-once, nothing lost).
        stack = self.reopen()
        self.assertEqual(200, stack.request("/readyz")[0])
        self.fresh()
        ctx = context()
        stack = self.open(seed=contexts(ctx))
        with patch.object(Archive, "append", side_effect=partial_append):
            self.assertEqual(503, stack.request("/events", "detector", raw=b'{"x": NaN}')[0])  # quarantine write
        self.assert_refuses_everything(stack, ctx["run_id"], detected(ctx), "O")

    def test_kafka_recorder_partial_append_is_sticky_for_http_and_recorder(self):
        ctx = context()
        stack = self.open(kafka=True, seed=contexts(ctx))
        with patch.object(Archive, "append", side_effect=partial_append):
            self.broker.append(0, *signed(detected(ctx), self.keys))
            self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
        published = len(self.broker.logs[0])
        self.assertEqual(503, stack.request("/readyz")[0])
        self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
        self.assertEqual(published, len(self.broker.logs[0]))  # no 202: nothing new was published
        stack.restart_bridge()  # an in-process recorder restart cannot clear it
        self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
        self.assertEqual(0, self.broker.committed[0])
        stack.close()
        self.stack = None
        with self.assertRaises(ArchiveFailure):
            Archive(Path(self.temp.name) / "O", "O")

    def test_data_errors_are_not_io_failures(self):
        ctx = context()
        stack = self.open()
        for body in (detected(ctx), b"\xff", b"[]"):  # RUN_CONTEXT_MISSING, undecodable, not an object
            data = body if isinstance(body, bytes) else canonical(body)
            self.assertEqual(422, stack.request("/events", "detector", raw=data)[0])
        for event in contexts(ctx):
            self.assertEqual(201, stack.request("/events", "harness", event)[0])
        with patch.object(Archive, "ingest", side_effect=RuntimeError("program error")):
            self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
        # Nothing was written, so a program error is not an archive failure.
        self.assertEqual((None, 200), (getattr(stack.archive, "failure", None), stack.request("/readyz")[0]))
        self.assertEqual(201, stack.request("/events", "detector", detected(ctx))[0])
        self.assertEqual(200, stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0])
        # A destination problem during export is not an archive failure either.
        with self.assertRaises(FileExistsError):
            stack.archive.export(ctx["run_id"], self.temp.name)
        self.assertEqual((None, 200), (getattr(stack.archive, "failure", None), stack.request("/readyz")[0]))


# ---------------------------------------------------------------- fix-03 FX02-R1 source read failures
def eio(path):
    return OSError(errno.EIO, "simulated EIO", str(path))


class Flaky:
    """A real file handle whose reads raise EIO after `ok` successful ones; `corrupt` flips one byte."""
    def __init__(self, handle, ok=None, corrupt=False):
        self.handle, self.ok, self.corrupt = handle, ok, corrupt

    def __getattr__(self, name):
        return getattr(self.handle, name)

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.handle.close()

    def __iter__(self):
        return self

    def step(self):
        if self.ok is not None:
            if self.ok <= 0:
                raise eio(self.handle.name)
            self.ok -= 1

    def __next__(self):
        self.step()
        return next(self.handle)

    def readline(self, *args):
        self.step()
        return self.handle.readline(*args)

    def readinto(self, buffer):
        self.step()
        return self.handle.readinto(buffer)

    def read(self, *args):
        self.step()
        data = self.handle.read(*args)
        if self.corrupt and data:
            self.corrupt, data = False, bytes([data[0] ^ 1]) + data[1:]
        return data


@contextlib.contextmanager
def source_fault(target, kind, skip=0, ok=None):
    """OSError(EIO) at the OS boundary for one archive path, below every store function.

    kind 'stat': os.stat/os.lstat of the path (existence, symlink, size checks) fail.
    kind 'open': the read-mode open after `skip` earlier ones fails; with `ok`, that handle fails
    after `ok` reads instead (mid-file / mid-copy).
    """
    target, real_open = Path(target), builtins.open
    opened = [0]

    def hit(path):
        return isinstance(path, (str, os.PathLike)) and Path(path) == target

    def fake_open(path, mode="r", *args, **kwargs):
        if hit(path) and "r" in mode:
            opened[0] += 1
            if opened[0] == skip + 1:
                if ok is None:
                    raise eio(path)
                return Flaky(real_open(path, mode, *args, **kwargs), ok)
        return real_open(path, mode, *args, **kwargs)

    def failing(real):
        def call(path, *args, **kwargs):
            if hit(path):
                raise eio(path)
            return real(path, *args, **kwargs)
        return call

    with contextlib.ExitStack() as patches:
        if kind == "open":
            patches.enter_context(patch("builtins.open", fake_open))
        else:
            patches.enter_context(patch("os.stat", failing(os.stat)))
            patches.enter_context(patch("os.lstat", failing(os.lstat)))
        yield opened


class SourceReadFailureTests(StackCase):
    """FX02-R1: archive evidence that cannot be read stops the archive like an uncertain write;
    an export destination error fails only that export."""
    kafka = False
    sizes = StickyFailureTests.sizes
    assert_refuses_everything = StickyFailureTests.assert_refuses_everything

    def evidence(self, plane):
        root = Path(self.temp.name) / plane
        return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and p.name != ".owner"}

    def seeded(self, plane, sealed=False):
        """Fresh H or O archive, one run: accepted events and a quarantined invalid input (archive scope).
        With `sealed`, the run is sealed and one more event is kept as late input."""
        self.fresh(plane)
        self.stack = stack = Stack(self.temp.name, self.broker, self.keys, kafka=False, plane=plane)
        ctx = context()
        if plane == "O":
            role, events = "detector", [detected(ctx) for _ in range(3)]
            for event in contexts(ctx):
                self.assertEqual(201, stack.request("/events", "harness", event)[0])
        else:
            role, events = "harness", [dict(manifest(), run_id=ctx["run_id"]) for _ in range(3)]
        self.assertEqual(201, stack.request("/events", role, events[0])[0])
        self.assertEqual(422, stack.request("/events", role, raw=b"[]")[0])  # invalid input: archive stays healthy
        if sealed:
            self.assertEqual(200, stack.request("/seal", "evaluator", {"run_id": ctx["run_id"]})[0])
            self.assertEqual(409, stack.request("/events", role, events[1])[0])  # late.jsonl
        self.assertEqual(200, stack.request("/readyz")[0])
        return stack, ctx["run_id"], events[2]

    def targets(self, stack, run, plane):
        archive = stack.archive
        return {"raw": archive.path(run) / (plane + ".jsonl"), "run dir": archive.path(run),
                "manifest": archive.path(run) / "manifest.json", "late": archive.path(run) / "late.jsonl",
                "archive-scope": archive.root / "rejections.jsonl"}

    def assert_stops(self, plane, operation, name, kind, skip=0, ok=None):
        stack, run, following = self.seeded(plane, sealed=operation == "export")
        target = self.targets(stack, run, plane)[name]
        before = self.evidence(plane)
        with source_fault(target, kind, skip, ok) as opened:
            if operation == "records":
                with self.assertRaises(ArchiveFailure):
                    stack.archive.records(run)
            elif operation == "GET /events":
                self.assertEqual((503, {"error": "NOT_DURABLE"}), stack.request("/events?run_id=" + run))
            elif operation in {"POST /seal", "POST /events"}:
                body = {"run_id": run} if operation == "POST /seal" else following
                self.assertEqual(503, stack.request(operation[5:], "evaluator" if operation == "POST /seal"
                                                    else "harness" if plane == "H" else "detector", body)[0])
            else:
                with self.assertRaises(ArchiveFailure):
                    stack.archive.export(run, Path(tempfile.mkdtemp(dir=self.temp.name)) / "export")
        if kind == "open":
            self.assertEqual(skip + 1, opened[0])  # the fault was reached at the intended read
        self.assertEqual("OSError", getattr(stack.archive, "failure", None))
        self.assert_refuses_everything(stack, run, following, plane)
        self.assertEqual(before, self.evidence(plane))  # nothing appended, truncated or repaired
        stack.close()
        self.stack = None
        Archive(Path(self.temp.name) / plane, plane).close()  # the fault was transient: a restart reopens

    def test_source_read_errors_in_records_and_seal_are_sticky(self):
        cases = [("records", "raw", "open"), ("records", "raw", "open", 0, 1), ("POST /seal", "run dir", "stat"),
                 ("POST /seal", "raw", "open")]  # the last one already stopped the archive in fix-02 (control)
        for plane in ("H", "O"):
            for case in cases + ([("GET /events", "raw", "open"), ("GET /events", "raw", "open", 0, 1)] if plane == "O" else []):
                with self.subTest(plane=plane, case=case):
                    self.assert_stops(plane, *case)

    def test_source_read_errors_during_export_are_sticky(self):
        # skip = earlier opens of that file in export: seal re-reads raw twice; summary reads, hashes, then copies.
        cases = [("late", "stat"), ("late", "open"), ("late", "open", 1), ("late", "open", 2, 1),
                 ("archive-scope", "stat"), ("archive-scope", "open"), ("archive-scope", "open", 2, 1),
                 ("raw", "open", 4, 1)]
        for plane in ("H", "O"):
            for case in cases:
                with self.subTest(plane=plane, case=case):
                    self.assert_stops(plane, "export", *case)

    def test_source_stat_errors_on_the_write_path_are_sticky(self):
        for plane in ("H", "O"):
            with self.subTest(plane=plane, transport="direct"):
                self.assert_stops(plane, "POST /events", "manifest", "stat")
        for path in ("HTTP submit", "recorder"):
            with self.subTest(plane="O", transport="kafka", path=path):
                self.fresh()
                ctx = context()
                stack = self.open(kafka=True, seed=contexts(ctx))
                manifest_path = stack.archive.path(ctx["run_id"]) / "manifest.json"
                published = len(self.broker.logs[0])
                with source_fault(manifest_path, "stat"):
                    if path == "HTTP submit":
                        self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
                    else:
                        self.broker.append(0, *signed(detected(ctx), self.keys))
                        published += 1
                        self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
                self.assertEqual("OSError", getattr(stack.archive, "failure", None))
                self.assertEqual((503, "ARCHIVE_FAILED:OSError"), (lambda r: (r[0], r[1]["reason"]))(stack.request("/readyz")))
                self.assertEqual(503, stack.request("/events", "detector", detected(ctx))[0])
                self.assertEqual((published, 0), (len(self.broker.logs[0]), self.broker.committed[0]))
                if path == "recorder":
                    stack.restart_bridge()  # the redelivered message meets the stopped archive
                    self.assertTrue(eventually(lambda: stack.bridge.failure is not None))
                    self.assertEqual(0, self.broker.committed[0])

    def test_export_destination_errors_fail_the_export_only(self):
        def destination_fault(destination, kind):
            real_open = builtins.open

            def fake_open(path, mode="r", *args, **kwargs):
                inside = isinstance(path, (str, os.PathLike)) and Path(destination) in Path(path).parents
                if inside and kind == "no space" and ("w" in mode or "x" in mode):
                    raise OSError(errno.ENOSPC, "simulated full destination", str(path))
                if inside and kind == "copy differs" and "r" in mode:
                    return Flaky(real_open(path, mode, *args, **kwargs), corrupt=True)
                return real_open(path, mode, *args, **kwargs)
            if kind == "chmod":
                return patch.object(Path, "chmod", side_effect=PermissionError(errno.EACCES, "simulated"))
            if kind == "fsync":
                return patch.object(store.os, "fsync", side_effect=eio(destination))
            return patch("builtins.open", fake_open)

        for plane in ("H", "O"):
            with self.subTest(plane=plane):
                stack, run, following = self.seeded(plane, sealed=True)
                before = self.evidence(plane)
                existing = Path(tempfile.mkdtemp(dir=self.temp.name))
                with self.assertRaises(FileExistsError):
                    stack.archive.export(run, existing)
                for kind in ("no space", "copy differs", "chmod", "fsync"):
                    destination = Path(tempfile.mkdtemp(dir=self.temp.name)) / "export"
                    with destination_fault(destination, kind):
                        with self.assertRaises(OSError) as raised:
                            stack.archive.export(run, destination)
                    self.assertNotIsInstance(raised.exception, ArchiveFailure, kind)
                    if kind in {"no space", "copy differs"}:
                        self.assertFalse((destination / "export.json").exists(), kind)
                    self.assertEqual((None, 200), (getattr(stack.archive, "failure", None), stack.request("/readyz")[0]), kind)
                self.assertEqual(before, self.evidence(plane))
                # The healthy source keeps working: a full export, then new input is still stored (late: 409).
                destination = Path(tempfile.mkdtemp(dir=self.temp.name)) / "export"
                stack.archive.export(run, destination)
                self.assertTrue((destination / "export.json").exists())
                self.assertEqual(409, stack.request("/events", "harness" if plane == "H" else "detector", following)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
