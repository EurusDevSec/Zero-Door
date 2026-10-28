"""ZER-18: real outbox/lifecycle, offline transport; no lab, action or LLM calls."""
import ast
import asyncio
import copy
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.adapters import RulesConsumer
from event_pipeline.client import Client
from event_pipeline.contract import Producer, new_id
from event_pipeline.decision_journal import DecisionJournal
from hephaestus.command_guard import GuardedRules

CLOCK = {"clock_id": "clk_offline", "clock_source": "UNKNOWN", "resolution_ms": None}


def detection(ctx=None):
    ctx = ctx or dict(run_id=new_id("run"), trial_id=new_id("trl"), group="B1",
                      incident_id=new_id("inc"), method_version="zer18-offline", config_ref="sha256:" + "1" * 64)
    return Producer("detector", "offline", CLOCK).event(ctx, "DETECTED", {
        "rule_id": "SUSPICIOUS_LOG", "rule_version": "offline", "signature": "synthetic-log",
        "metric": "log", "value": 1, "threshold": 0, "severity": "CRITICAL", "description": "Synthetic observation"},
        "o.alert", target={"namespace": "zd-sqli-lab", "service": "sqli-fixture", "flow": None}, alert_id=new_id("alt"))


class Fake:
    def __init__(self, events, error=None, receipt="RECORDED"):
        self.events, self.error, self.receipt = events, error, receipt
        self.trial, self.run = events[0]["trial_id"], events[0]["run_id"]
        self.producer = Producer("decision_rules", "offline", CLOCK)
        self.sent = []

    def records(self):
        return [{"envelope": e} for e in self.events]

    def publish(self, event):
        self.sent.append(copy.deepcopy(event))
        if self.error:
            raise self.error
        return {"status": self.receipt, "event_id": event["event_id"]}


class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "decisions.sqlite"
        self.at = [1000.0]
        self.event = detection()

    def consumer(self, fake):
        result = RulesConsumer(fake, lambda *_: "BLOCK_IP", journal_path=self.path, clock=lambda: self.at[0])
        self.addCleanup(result.close)
        return result

    def test_repeated_delivery_creates_one_decision(self):
        fake = Fake([self.event, self.event])
        consumer = self.consumer(fake)
        for _ in range(4):
            consumer.poll()
        self.assertEqual(1, len(fake.sent))
        self.assertEqual("RECORDED", consumer.journal.get(self.event["event_id"])["status"])

    def test_restart_preserves_exact_envelope_budget_and_unknown(self):
        fake = Fake([self.event], TimeoutError("ack lost"))
        for _ in range(4):
            consumer = RulesConsumer(fake, lambda *_: "BLOCK_IP", journal_path=self.path, clock=lambda: self.at[0])
            try:
                consumer.poll()
            except TimeoutError:
                pass
            finally:
                consumer.close()
        self.assertEqual(3, len(fake.sent))
        self.assertTrue(all(e == fake.sent[0] for e in fake.sent))
        journal = DecisionJournal(self.path)
        self.addCleanup(journal.close)
        row = journal.get(self.event["event_id"])
        self.assertEqual((3, "UNKNOWN"), (row["attempts"], row["status"]))
        self.assertEqual("EXTERNAL_PROBE_REQUIRED", journal.summary()["recovery_verification"])

    def test_age_and_backwards_clock_never_reset_budget(self):
        for delta in (30, -1):
            with self.subTest(delta=delta):
                event = detection()
                fake = Fake([event], TimeoutError())
                consumer = self.consumer(fake)
                with self.assertRaises(TimeoutError):
                    consumer.poll()
                self.at[0] += delta
                consumer.poll()
                self.assertEqual(1, len(fake.sent))
                self.assertEqual("UNKNOWN", consumer.journal.get(event["event_id"])["status"])
                self.at[0] = 1000

    def test_refusal_is_durable_and_other_target_is_not_starved(self):
        second = detection({k: self.event[k] for k in ("run_id", "trial_id", "group", "incident_id", "method_version", "config_ref")})
        second["target"]["service"] = "other-synthetic-service"
        fake = Fake([self.event, second], HTTPError("http://offline", 422, "refused", {}, None))
        consumer = self.consumer(fake)
        for _ in range(2):
            with self.assertRaises(HTTPError):
                consumer.poll()
        consumer.poll()
        self.assertEqual(2, len(fake.sent))
        restarted = self.consumer(fake)
        restarted.poll()
        self.assertEqual(2, len(fake.sent))

    def test_cooldown_survives_restart_and_expires_without_replaying_old_event(self):
        fake = Fake([self.event])
        self.consumer(fake).poll()
        second = detection({k: self.event[k] for k in ("run_id", "trial_id", "group", "incident_id", "method_version", "config_ref")})
        fake.events.append(second)
        self.consumer(fake).poll()
        self.assertEqual(1, len(fake.sent))
        self.at[0] += 91
        fake.events.append(detection({k: self.event[k] for k in ("run_id", "trial_id", "group", "incident_id", "method_version", "config_ref")}))
        self.consumer(fake).poll()
        self.assertEqual(2, len(fake.sent))

    def test_changed_input_same_id_is_not_a_new_effect(self):
        fake = Fake([self.event])
        consumer = self.consumer(fake)
        consumer.poll()
        fake.events[0] = copy.deepcopy(self.event)
        fake.events[0]["payload"]["value"] = 2
        with self.assertRaisesRegex(ValueError, "INPUT_CONFLICT"):
            consumer.poll()
        self.assertEqual(1, len(fake.sent))

    def test_unknown_receipt_is_not_ack_or_success(self):
        fake = Fake([self.event], receipt="API_ACCEPTED")
        consumer = self.consumer(fake)
        with self.assertRaisesRegex(TimeoutError, "RECEIPT_UNKNOWN"):
            consumer.poll()
        self.assertEqual("PENDING", consumer.journal.get(self.event["event_id"])["status"])

    def test_lost_receipt_reconciles_exact_archived_decision_without_resend(self):
        fake = Fake([self.event], TimeoutError())
        consumer = self.consumer(fake)
        with self.assertRaises(TimeoutError):
            consumer.poll()
        fake.events.append(fake.sent[0])
        consumer.poll()
        self.assertEqual(1, len(fake.sent))
        self.assertEqual("RECORDED", consumer.journal.get(self.event["event_id"])["status"])

    def test_poison_envelope_does_not_block_a_valid_event(self):
        poison = copy.deepcopy(self.event)
        poison["event_id"] = new_id("evt")
        poison["schema_version"] = "unsupported"
        fake = Fake([poison, self.event])
        consumer = self.consumer(fake)
        with self.assertRaises(ValueError):
            consumer.poll()
        self.assertEqual(1, len(fake.sent))

    def test_malformed_record_or_missing_keys_do_not_starve_later_events(self):
        for poison in (None, "bad-record", {}, {"envelope": None},
                       {"envelope": {"event_type": "DETECTED"}}):
            with self.subTest(poison=poison):
                fake = Fake([detection()])
                fake.records = lambda: [poison, {"envelope": fake.events[0]}]
                consumer = self.consumer(fake)
                with self.assertRaisesRegex(ValueError, "invalid archive envelope"):
                    consumer.poll()
                self.assertEqual(1, len(fake.sent))

    def test_native_process_restart_does_not_reset_attempts_or_ids(self):
        folder = Path(self.temp.name)
        (folder / "event.json").write_text(json.dumps(self.event))
        for _ in range(4):
            subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--restart-child", str(folder)],
                           check=True, timeout=15, capture_output=True)
        sends = [json.loads(line) for line in (folder / "sends.jsonl").read_text().splitlines()]
        self.assertEqual(3, len(sends))
        self.assertTrue(all(e == sends[0] for e in sends))
        journal = DecisionJournal(folder / "decisions.sqlite")
        self.addCleanup(journal.close)
        self.assertEqual("UNKNOWN", journal.get(self.event["event_id"])["status"])


class HttpBoundsTests(unittest.TestCase):
    def client(self):
        return Client("http://offline.invalid", "unused", "unused", new_id("run"), new_id("trl"), None)

    def test_stalled_and_endless_pages_fail_closed(self):
        for stalled in (False, True):
            client = self.client()
            count = []
            def page(_):
                count.append(1)
                return {"records": [{}] * 500, "next": 0 if stalled else len(count) * 500}
            client.request = page
            with self.assertRaises((ValueError, TimeoutError)):
                list(client.records())
            self.assertLessEqual(len(count), 20)

    def test_bad_receipt_status_or_wrong_id_not_accepted(self):
        for receipt in ({}, {"status": "ACCEPTED", "event_id": "one"}, {"status": "RECORDED", "event_id": "other"}):
            client = self.client()
            client.request = lambda *_: receipt
            with self.assertRaisesRegex(TimeoutError, "PUBLISH_RECEIPT_UNKNOWN"):
                client.publish({"event_id": "one"})


class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_slow_owner_poll_does_not_block_and_cancel_joins(self):
        source = ROOT / "agent-orchestrator/hephaestus/main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and n.name in {"_kafka_consumer_thread", "alert_consumer_loop"}]
        seen, closed, threads = [], [], []
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.journal = self
                threads.append(threading.get_ident())
            def poll(self):
                threads.append(threading.get_ident())
                time.sleep(0.2)
                seen.append(1)
            def close(self):
                threads.append(threading.get_ident())
                closed.append(True)
            def summary(self):
                return {"durability": "OFFLINE"}
        class ClientStub:
            run, trial = new_id("run"), new_id("trl")
            def context(self):
                return dict(run_id=self.run, trial_id=self.trial, group="B1")
        ns = dict(threading=threading, asyncio=asyncio, os=SimpleNamespace(getenv=lambda _: "offline-only-path"), r1_client=ClientStub(),
                  RulesConsumer=Adapter, GuardedRules=GuardedRules, decide_action=lambda *_: None,
                  consumer_state={}, logger=logging.getLogger("offline"), audit_refusal=lambda *_: None)
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), ns)
        task = asyncio.create_task(ns["alert_consumer_loop"]())
        ticks = 0
        while not seen and ticks < 50:
            await asyncio.sleep(0.01)
            ticks += 1
        self.assertTrue(seen)
        self.assertGreater(ticks, 5)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, 2)
        self.assertEqual([True], closed)
        self.assertEqual(1, len(set(threads)))
        self.assertNotIn(threading.get_ident(), threads)
        self.assertEqual("STOPPED", ns["consumer_state"]["status"])

    async def test_missing_or_invalid_state_path_fails_closed_before_poll(self):
        source = ROOT / "agent-orchestrator/hephaestus/main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_kafka_consumer_thread")
        with tempfile.TemporaryDirectory() as folder:
            for path in (None, ":memory:", str(Path(folder) / "absent" / "decisions.sqlite")):
                client = Fake([detection()])
                ns = dict(threading=threading, os=SimpleNamespace(getenv=lambda _, path=path: path),
                          r1_client=client, RulesConsumer=RulesConsumer, GuardedRules=GuardedRules,
                          decide_action=lambda *_: "BLOCK_IP", consumer_state={}, logger=logging.getLogger("offline"))
                exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), ns)
                ns["_kafka_consumer_thread"]()
                self.assertEqual("FAILED", ns["consumer_state"]["status"])
                self.assertEqual([], client.sent)


def restart_child(folder):
    event = json.loads((folder / "event.json").read_text())
    class Sender(Fake):
        def publish(self, envelope):
            with (folder / "sends.jsonl").open("a") as out:
                out.write(json.dumps(envelope, sort_keys=True) + "\n")
            raise TimeoutError("synthetic missing receipt")
    consumer = RulesConsumer(Sender([event]), lambda *_: "BLOCK_IP", journal_path=folder / "decisions.sqlite")
    try:
        consumer.poll()
    except TimeoutError:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    if sys.argv[1:2] == ["--restart-child"]:
        restart_child(Path(sys.argv[2]))
    else:
        unittest.main(verbosity=2)
