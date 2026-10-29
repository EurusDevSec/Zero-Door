"""Explicit functional-session CLI. Default is PLAN_ONLY; live requires local files.

SIGINT/SIGTERM stops new work. An already published worker command is allowed to
expire under its existing <=5s command deadline; no remote cancel is invented.
The output directory is exclusive per run, so restart never replays a session.
"""
import argparse
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import signal
import threading
import time

from kafka import KafkaConsumer, KafkaProducer, TopicPartition

from event_pipeline.llm import Adapter, HttpxTransport, Limits, RunBudget
from nemesis.command_guard import CommandGuard, Refused, fields, read_key, sign, strict_json
from nemesis.session import PURPOSE, Session, SessionLimits


def read_json(path):
    with Path(path).open("rb") as stream:
        return strict_json(stream.read(32769))


def config_valid(raw):
    fields(raw, {"purpose", "benchmark_eligible", "context", "limits", "max_calls", "max_reserved_tokens",
                 "max_estimated_usd"})
    if raw["purpose"] != PURPOSE or raw["benchmark_eligible"] is not False:
        raise ValueError("FUNCTIONAL_SESSION_REQUIRED")
    fields(raw["limits"], {"max_rounds", "duration_s", "command_s", "allowed_templates"})
    if type(raw["limits"]["allowed_templates"]) is not list:
        raise ValueError("SESSION_TEMPLATES")
    limits = SessionLimits(**dict(raw["limits"], allowed_templates=tuple(raw["limits"]["allowed_templates"])))
    if type(raw["max_calls"]) is not int or not 1 <= raw["max_calls"] <= 3:
        raise ValueError("SESSION_CALLS")
    if type(raw["max_reserved_tokens"]) is not int or not 1 <= raw["max_reserved_tokens"] <= 30_000:
        raise ValueError("SESSION_TOKENS")
    if type(raw["max_estimated_usd"]) not in (int, float) or not 0 < raw["max_estimated_usd"] <= .005:
        raise ValueError("SESSION_COST")
    return limits


class KafkaExecutor:
    """One worker owns construct/poll/send/close. No automatic send retry.

    The worker result topic uses the existing lab trust boundary, not a new result
    authentication protocol. Matching IDs/shape are necessary, not proof of MAC.
    """
    def __init__(self, guard, key, ledger, servers, *, producer=KafkaProducer,
                 consumer=KafkaConsumer, clock=time.monotonic):
        self.guard, self.key, self.ledger = guard, key, ledger
        self.servers = servers
        # Functional sessions use their own topic pair, never formal run topics.
        prefix = "zer19-" + guard.policy["context"]["run_id"][4:16]
        self.commands_topic, self.results_topic = prefix + ".commands", prefix + ".results"
        self.producer_factory, self.consumer_factory, self.clock = producer, consumer, clock
        self.stop_requested = threading.Event()
        self.dispatch_lock = threading.Lock()

    def request_stop(self):
        # Linearize stop against the send invocation (bounded max_block_ms=2000).
        with self.dispatch_lock:
            self.stop_requested.set()

    async def __call__(self, command):
        stop = threading.Event()
        worker = asyncio.create_task(asyncio.to_thread(self._execute, deepcopy(command), stop))
        try:
            return await asyncio.shield(worker)
        except asyncio.CancelledError:
            stop.set()
            try:
                await worker  # Drain owned clients before the session returns.
            except Exception:
                pass  # Cancellation remains cancellation, not a successful receipt.
            raise

    def _execute(self, command, stop):
        self.guard.enabled()
        template = command["parameters"]["customParams"]["template"]
        admitted = self.guard.command({"attackType": "SQLI", "template": template,
            "durationSec": command["parameters"]["duration"]}, command["commandId"])
        # Guard rebuilds timestamp; compare every authority-bearing field.
        if any(command[k] != admitted[k] for k in admitted if k != "timestamp"):
            raise Refused("SESSION_COMMAND_CHANGED")
        previous = self.ledger.claim(command["commandId"], {"command": command})
        if previous is not None:
            return previous
        producer = consumer = None
        sent = False
        end = self.clock() + command["parameters"]["duration"] + 12
        try:
            consumer = self.consumer_factory(bootstrap_servers=self.servers.split(","), group_id=None,
                enable_auto_commit=False, auto_offset_reset="none", value_deserializer=None, api_version=(2, 5, 0),
                request_timeout_ms=2000, session_timeout_ms=1000, max_partition_fetch_bytes=32768,
                fetch_max_bytes=65536, max_poll_records=10)
            # kafka-python-ng 2.2.2 high-level partitions_for_topic()/position()
            # can poll indefinitely. Drive its pinned low-level metadata cache
            # in finite ticks, then use public end_offsets (request_timeout_ms).
            client = consumer._client
            client.add_topic(self.results_topic)
            setup_end = min(end, self.clock() + 5)
            partitions = None
            while not stop.is_set() and not self.stop_requested.is_set() and self.clock() < setup_end:
                partitions = client.cluster.partitions_for_topic(self.results_topic)
                if partitions:
                    break
                client.poll(timeout_ms=min(100, max(1, int((setup_end - self.clock()) * 1000))))
            if stop.is_set() or self.stop_requested.is_set():
                raise Refused("CANCELLED_BEFORE_SEND", 409)
            if not partitions:
                raise Refused("RESULT_TOPIC_UNAVAILABLE", 503)
            assigned = [TopicPartition(self.results_topic, p) for p in sorted(partitions)]
            consumer.assign(assigned)
            offsets = consumer.end_offsets(assigned)  # Finite 2000ms including retries.
            if set(offsets) != set(assigned):
                raise Refused("RESULT_OFFSETS_UNAVAILABLE", 503)
            for partition, offset in offsets.items():
                consumer.seek(partition, offset)  # Set concrete offsets BEFORE publishing.
            producer = self.producer_factory(bootstrap_servers=self.servers.split(","), acks="all", retries=0,
                api_version=(2, 5, 0), max_block_ms=2000, request_timeout_ms=3000,
                value_serializer=lambda value: json.dumps(value, allow_nan=False).encode())
            envelope = sign(command, self.key)
            with self.dispatch_lock:
                if stop.is_set() or self.stop_requested.is_set() or self.clock() + command["parameters"]["duration"] + 3 >= end:
                    raise Refused("CANCELLED_BEFORE_SEND", 409)
                sent = True  # Even an exception from send() leaves a durable UNKNOWN claim.
                pending = producer.send(self.commands_topic, envelope)
            pending.get(timeout=3)
            while not stop.is_set() and self.clock() < end:
                records = consumer.poll(timeout_ms=250)
                for batch in records.values():
                    for message in batch:
                        try:
                            value = strict_json(message.value)
                        except Refused:
                            continue
                        if type(value) is dict and value.get("commandId") == command["commandId"]:
                            from nemesis.session import result_valid
                            result_valid(value, command, self.guard.policy["sqli"]["maxSends"])
                            self.ledger.complete(command["commandId"], value)
                            return value
            raise Refused("EXECUTOR_OUTCOME_UNKNOWN", 503)
        except Exception:
            if not sent:
                self.ledger.complete(command["commandId"], {"status": "REJECTED",
                    "commandId": command["commandId"], "reason": "PRE_SEND_FAILED"})
            raise
        finally:
            try:
                if producer is not None:
                    producer.close(timeout=1)
            finally:
                if consumer is not None:
                    consumer.close(autocommit=False)


async def live(args):
    config = read_json(args.config)
    limits = config_valid(config)
    guard = CommandGuard.from_env()
    operator = read_key(os.environ.get("ZD_OPERATOR_TOKEN_FILE", ""), "operator")
    guard.authorize("Bearer " + operator["secret"])
    key, ledger = guard.signer(), guard.ledger()
    budget = RunBudget(config["context"]["run_id"], max_calls=config["max_calls"],
        max_reserved_tokens=config["max_reserved_tokens"], max_estimated_usd=config["max_estimated_usd"],
        duration_s=limits.duration_s)
    adapter = Adapter(HttpxTransport(os.environ.get("OPENAI_API_KEY", "")), budget,
        limits=Limits(attempts=1, timeout_s=20, deadline_s=25, retry_delay_s=0, max_output_tokens=256))
    async def observe():
        return read_json(args.observation)
    session = Session(purpose=config["purpose"], guard=guard, adapter=adapter, observe=observe,
        execute=KafkaExecutor(guard, key, ledger, os.environ.get("KAFKA_BOOTSTRAP_SERVERS",
                              "kafka.zero-door.svc.cluster.local:9092")),
        context=config["context"], limits=limits)
    output = Path(args.output)
    # Caller chooses a persistent parent; mkdir is the once-only run reservation.
    destination = output / budget.run_id
    destination.mkdir()  # Existing/unclosed attempt is NOT permission to replay.
    (destination / "started.json").write_text(json.dumps({"purpose": PURPOSE, "config": config,
        "process": os.getpid(), "restart_allowed": False}, indent=2) + "\n", encoding="utf-8")
    with (destination / "events.jsonl").open("x", encoding="utf-8") as stream:
        def sink(item):
            stream.write(json.dumps(item, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        session.sink = sink
        installed = []
        for name in (signal.SIGINT, signal.SIGTERM):
            installed.append((name, signal.getsignal(name)))
            signal.signal(name, lambda *_: session.stop())
        try:
            receipt = await session.start()
        finally:
            for name, handler in installed:
                signal.signal(name, handler)
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(destination / "receipt.json"), "stop_reason": receipt["stop_reason"],
                      "completed_rounds": receipt["completed_rounds"]}))
    return 0 if receipt["stop_reason"] in {"MAX_ROUNDS", "CALL_BUDGET", "MODEL_STOP", "CANCELLED"} else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--observation")
    parser.add_argument("--output")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"status": "PLAN_ONLY", "purpose": PURPOSE,
                          "provider_calls": 0, "executor_dispatches": 0}))
        return 0
    if not all((args.config, args.observation, args.output)):
        parser.error("--live requires --config, --observation and --output")
    try:
        return asyncio.run(live(args))
    except Exception as error:
        print(json.dumps({"status": "FAILED_OR_UNKNOWN", "error_type": type(error).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
