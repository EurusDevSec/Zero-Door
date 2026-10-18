"""Execute the real consumer coroutine with a slow, offline Kafka test double."""
import ast
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
import unittest


class ConsumerLoopTest(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, fail_first_connect=False, fail_first_poll=False):
        messages, errors, threads, consumers = [], [], [], []
        attempts = 0

        class Consumer:
            def __init__(self):
                self.closed = False
                self.delivered = False
                self.failed = False

            def poll(self, **kwargs):
                threads.append(threading.get_ident())
                time.sleep(0.3)  # A network wait must not stall FastAPI's event loop.
                if fail_first_poll and not self.failed:
                    self.failed = True
                    raise RuntimeError("offline poll failure")
                if self.delivered:
                    return {}
                self.delivered = True
                return {0: [SimpleNamespace(value={"status": "SUCCESS", "commandId": "offline-result", "attackType": "TEST"})]}

            def __iter__(self):  # Also runs against the pre-fix implementation.
                return iter(self.poll().get(0, []))

            def close(self):
                threads.append(threading.get_ident())
                self.closed = True

        def factory(*args, **kwargs):
            nonlocal attempts
            attempts += 1
            threads.append(threading.get_ident())
            time.sleep(0.3)
            if fail_first_connect and attempts == 1:
                raise RuntimeError("offline broker not ready")
            consumer = Consumer()
            consumers.append(consumer)
            return consumer

        source = Path(os.environ.get("NEMESIS_TEST_SOURCE", Path(__file__).resolve().parents[1] / "agent-orchestrator/nemesis/main.py"))
        tree = ast.parse(source.read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "consume_results_loop")
        namespace = dict(asyncio=asyncio, threading=threading, json=json, KafkaConsumer=factory,
                         KAFKA_RESULTS_TOPIC="offline.results", KAFKA_BOOTSTRAP_SERVERS="offline:9092", KAFKA_GROUP_ID="offline",
                         logger=SimpleNamespace(info=messages.append, warning=messages.append, error=errors.append))
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
        previous = time.monotonic()
        task = asyncio.create_task(namespace["consume_results_loop"]())
        gaps = []
        try:
            deadline = previous + 5
            while time.monotonic() < deadline:
                await asyncio.sleep(0.02)
                current = time.monotonic()
                gaps.append(current - previous)
                previous = current
                if any("offline-result" in m for m in messages):
                    break
            self.assertTrue(any("offline-result" in m for m in messages), "result delivery did not recover")
            self.assertLess(max(gaps), 0.2, "blocking Kafka work stalled the event loop")
            self.assertNotIn(threading.get_ident(), threads, "Kafka API ran on the event loop thread")
            self.assertEqual(len(set(threads)), 1, "one worker must own the non-thread-safe consumer")
            if fail_first_connect or fail_first_poll:
                self.assertTrue(errors, "failure must remain visible")
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=3)
        self.assertTrue(consumers and all(c.closed for c in consumers), "cancel must stop and close the worker")

    async def test_slow_poll_keeps_event_loop_responsive(self):
        await self.exercise()

    async def test_broker_startup_failure_retries_without_blocking(self):
        await self.exercise(fail_first_connect=True)

    async def test_poll_failure_remains_visible_and_recovers(self):
        await self.exercise(fail_first_poll=True)


if __name__ == "__main__":
    # asyncio's executor shutdown can hang after a broken cancellation path.
    # Bound the entire worker process, not just the coroutine's wait_for().
    if sys.argv[1:2] == ["--consumer-test-worker"]:
        del sys.argv[1]
        unittest.main()
    else:
        try:
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--consumer-test-worker", *sys.argv[1:]],
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            print("FAIL: consumer tests exceeded the 30s process deadline; worker terminated", file=sys.stderr)
            sys.exit(1)
        sys.exit(result.returncode)
