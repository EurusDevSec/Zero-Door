"""Actual durable ledger and fake Kafka clients only; no network or provider."""
import asyncio
import base64
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
import uuid
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from nemesis.command_guard import CommandGuard, Ledger, Refused
from event_pipeline.contract import new_id
from event_pipeline.llm import Adapter, Limits, RunBudget
from nemesis.session import PURPOSE, Session
from nemesis.session_cli import KafkaExecutor, config_valid
from test_nemesis_session import Fake, observation, result


class IOTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fixture = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())
        policy = deepcopy(self.fixture["policy"])
        policy["sqli"] = {"enabled": True,
            "endpoint": "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search",
            "maxSends": 2, "maxCommandSec": 5}
        self.guard = CommandGuard(policy)
        self.command = self.guard.command({"attackType": "SQLI", "template": "benign-apparel", "durationSec": 1}, str(uuid.uuid4()))
        self.ledger_path = Path(self.tmp.name) / "ledger.sqlite"
        self.events, self.threads = [], []
        self.response = result(self.command)
        self.send_error = self.pre_error = False
        self.wrong_first = False
        self.metadata_ready = True
        self.offset_error = False
        self.closed = threading.Event()

    def tearDown(self):
        self.tmp.cleanup()

    def executor(self):
        outer = self
        class Consumer:
            def __init__(self, **kwargs):
                outer.threads.append(threading.get_ident())
                outer.events.append("consumer")
                self.count = 0
                outer.assertEqual(2000, kwargs["request_timeout_ms"])
                self._client = SimpleNamespace(add_topic=lambda _: None,
                    cluster=SimpleNamespace(partitions_for_topic=self.partitions_for_topic),
                    poll=lambda **kwargs: threading.Event().wait(.01))
            def partitions_for_topic(self, topic):
                if outer.pre_error:
                    raise RuntimeError("offline setup failure")
                return {0} if outer.metadata_ready else None
            def assign(self, partitions):
                outer.events.append("assign")
            def end_offsets(self, partitions):
                outer.events.append("end_offsets")
                if outer.offset_error:
                    raise TimeoutError("offline finite offset failure")
                return {p: 5 for p in partitions}
            def seek(self, partition, offset):
                outer.events.append("seek")
                outer.assertEqual(5, offset)
            def poll(self, **kwargs):
                outer.threads.append(threading.get_ident())
                self.count += 1
                if outer.wrong_first and self.count == 1:
                    raw = dict(outer.response, commandId=str(uuid.uuid4()))
                else:
                    raw = outer.response
                return {0: [SimpleNamespace(value=json.dumps(raw).encode())]}
            def close(self, **kwargs):
                outer.events.append("consumer_closed")
                outer.threads.append(threading.get_ident())
                outer.closed.set()
        class Producer:
            def __init__(self, **kwargs):
                outer.threads.append(threading.get_ident())
                outer.events.append("producer")
                outer.assertEqual(0, kwargs["retries"])
            def send(self, topic, envelope):
                outer.events.append("send")
                outer.assertEqual("zer19-" + outer.guard.policy["context"]["run_id"][4:16] + ".commands", topic)
                outer.assertEqual(outer.command, json.loads(base64.b64decode(envelope["payload"])))
                if outer.send_error:
                    raise RuntimeError("offline send uncertain")
                return SimpleNamespace(get=lambda **kwargs: None)
            def close(self, **kwargs):
                outer.threads.append(threading.get_ident())
                outer.events.append("producer_closed")
        return KafkaExecutor(self.guard, self.fixture["key"], Ledger(self.ledger_path), "offline-only",
                             producer=Producer, consumer=Consumer)

    async def test_real_ledger_join_signed_send_single_owner_and_durable_replay(self):
        self.wrong_first = True
        executor = self.executor()
        raw = await executor(self.command)
        self.assertEqual(self.response, raw)
        self.assertLess(self.events.index("end_offsets"), self.events.index("seek"))
        self.assertLess(self.events.index("seek"), self.events.index("send"))
        self.assertEqual(1, len(set(self.threads)))
        self.assertNotEqual(threading.get_ident(), self.threads[0])
        self.assertEqual(["producer_closed", "consumer_closed"], self.events[-2:])
        replay = await self.executor()(self.command)
        self.assertEqual(raw, replay)
        self.assertEqual(1, self.events.count("send"))

    async def test_send_invocation_error_remains_unknown_after_restart_no_repeat(self):
        self.send_error = True
        with self.assertRaises(RuntimeError):
            await self.executor()(self.command)
        self.assertTrue(self.closed.is_set())
        with self.assertRaisesRegex(Refused, "OUTCOME_UNKNOWN"):
            await self.executor()(self.command)
        self.assertEqual(1, self.events.count("send"))

    async def test_bad_matching_result_never_completed_or_repeated(self):
        self.response["details"]["sqli"]["templateId"] = "wrong"
        with self.assertRaises(ValueError):
            await self.executor()(self.command)
        with self.assertRaisesRegex(Refused, "OUTCOME_UNKNOWN"):
            await self.executor()(self.command)
        self.assertEqual(1, self.events.count("send"))

    async def test_pre_send_failure_is_terminal_and_clients_close(self):
        self.pre_error = True
        with self.assertRaises(RuntimeError):
            await self.executor()(self.command)
        self.assertNotIn("send", self.events)
        self.assertTrue(self.closed.is_set())
        replay = await self.executor()(self.command)
        self.assertEqual("REJECTED", replay["status"])
        self.assertEqual(1, self.events.count("consumer"))

    async def test_command_tampering_fails_before_ledger_clients(self):
        self.command["target"]["url"] = "http://outside.invalid/"
        with self.assertRaisesRegex(Refused, "SESSION_COMMAND_CHANGED"):
            await self.executor()(self.command)
        self.assertEqual([], self.events)

    async def test_cancel_drains_owned_thread_and_leaves_unknown(self):
        entered = threading.Event()
        executor = self.executor()
        original = executor.consumer_factory
        def consumer(**kwargs):
            instance = original(**kwargs)
            def poll(**kwargs):
                entered.set()
                threading.Event().wait(.01)
                return {}
            instance.poll = poll
            return instance
        executor.consumer_factory = consumer
        task = asyncio.create_task(executor(self.command))
        for _ in range(100):
            if entered.is_set():
                break
            await asyncio.sleep(.005)
        self.assertTrue(entered.is_set())
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(self.closed.is_set())
        with self.assertRaisesRegex(Refused, "OUTCOME_UNKNOWN"):
            await self.executor()(self.command)
        self.assertEqual(1, self.events.count("send"))

    async def test_config_cannot_claim_benchmark_or_expand_envelope(self):
        config = dict(purpose=PURPOSE, benchmark_eligible=False, context={}, max_calls=1,
                      max_reserved_tokens=10_000, max_estimated_usd=.001,
                      limits=dict(max_rounds=1, duration_s=120, command_s=1,
                                  allowed_templates=["benign-apparel"]))
        self.assertEqual((1, 0), (config_valid(config).max_rounds, config_valid(config).required_rounds))
        self.assertEqual(1, config_valid(dict(config, limits=dict(config["limits"], required_rounds=1))).required_rounds)
        for change in [dict(benchmark_eligible=True), dict(purpose="formal"), dict(max_calls=4),
                       dict(max_reserved_tokens=30_001), dict(max_estimated_usd=.006), dict(extra="x"),
                       dict(limits=dict(config["limits"], required_rounds=2)),
                       dict(limits=dict(config["limits"], required_rounds=True)),
                       dict(limits=dict(config["limits"], minimum_rounds=1))]:
            with self.subTest(change=change), self.assertRaises((ValueError, Refused)):
                config_valid(dict(config, **change))

    async def test_cancel_during_metadata_setup_closes_clients_and_never_sends(self):
        self.metadata_ready = False
        task = asyncio.create_task(self.executor()(self.command))
        for _ in range(100):
            if "consumer" in self.events:
                break
            await asyncio.sleep(.005)
        self.assertIn("consumer", self.events)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, .5)
        self.assertTrue(self.closed.is_set())
        self.assertNotIn("send", self.events)

    async def test_unavailable_metadata_has_absolute_deadline_no_dispatch(self):
        self.metadata_ready = False
        executor = self.executor()
        ticks = [0]
        def clock():
            ticks[0] += 1
            return ticks[0]
        executor.clock = clock
        with self.assertRaisesRegex(Refused, "RESULT_TOPIC_UNAVAILABLE"):
            await executor(self.command)
        self.assertTrue(self.closed.is_set())
        self.assertNotIn("send", self.events)

    async def test_offset_setup_failure_is_terminal_no_send(self):
        self.offset_error = True
        with self.assertRaises(TimeoutError):
            await self.executor()(self.command)
        self.assertTrue(self.closed.is_set())
        self.assertNotIn("send", self.events)
        replay = await self.executor()(self.command)
        self.assertEqual("REJECTED", replay["status"])

    async def test_session_stop_during_metadata_and_offsets_never_publishes(self):
        for phase in ("metadata", "offsets"):
            with self.subTest(phase=phase):
                self.events.clear()
                self.metadata_ready = phase != "metadata"
                self.ledger_path = Path(self.tmp.name) / (phase + ".sqlite")
                self.guard.policy["context"] = dict(run_id=new_id("run"), trial_id=new_id("trl"), group="B2")
                context = dict(self.guard.policy["context"], incident_id=new_id("inc"),
                               method_version="zer19-functional/1", config_ref="sha256:" + "a" * 64)
                budget = RunBudget(context["run_id"], max_calls=1, max_reserved_tokens=20_000,
                                   max_estimated_usd=.005, duration_s=120)
                adapter = Adapter(Fake(), budget, limits=Limits(attempts=1, retry_delay_s=0))
                executor = self.executor()
                entered, release = threading.Event(), threading.Event()
                if phase == "offsets":
                    original = executor.consumer_factory
                    def consumer(**kwargs):
                        instance = original(**kwargs)
                        offsets = instance.end_offsets
                        def wait_offsets(partitions):
                            entered.set()
                            if not release.wait(.5):
                                raise TimeoutError("offline bounded setup")
                            return offsets(partitions)
                        instance.end_offsets = wait_offsets
                        return instance
                    executor.consumer_factory = consumer
                async def observe():
                    return observation()
                session = Session(purpose=PURPOSE, guard=self.guard, adapter=adapter, observe=observe,
                                  execute=executor, context=context)
                task = session.start()
                for _ in range(100):
                    if (phase == "metadata" and "consumer" in self.events) or entered.is_set():
                        break
                    await asyncio.sleep(.005)
                self.assertEqual("EXECUTING", session.phase)
                session.stop()
                self.metadata_ready = True
                release.set()
                receipt = await asyncio.wait_for(task, 1)
                self.assertEqual("CANCELLED_BEFORE_SEND", receipt["stop_reason"])
                self.assertEqual(0, receipt["completed_rounds"])
                self.assertNotIn("send", self.events)
                self.assertTrue(self.closed.is_set())

    async def test_packaging_uses_shared_context_for_all_existing_build_paths(self):
        docker = (ROOT / "agent-orchestrator/nemesis/Dockerfile").read_text()
        self.assertIn("COPY event_pipeline /event_pipeline", docker)
        self.assertIn("COPY nemesis/session.py /nemesis/session.py", docker)
        for name in ["rebuild-nemesis.sh", "infrastructure/scripts/setup-phase3.sh"]:
            script = (ROOT / name).read_text()
            self.assertIn('"$ZD_ROOT/agent-orchestrator"', script)
            self.assertIn('nemesis/Dockerfile', script)
        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
        matrix = workflow["jobs"]["r1-image-build"]["strategy"]["matrix"]["include"]
        smoke = next(item for item in matrix if item["image"] == "nemesis")
        publish = next(step["with"] for step in workflow["jobs"]["publish-images"]["steps"]
                       if step["name"] == "Build & Push Nemesis Agent")
        for build in (smoke, publish):
            context = ROOT / build["context"]
            self.assertEqual("./agent-orchestrator/nemesis/Dockerfile", build["file"])
            for line in docker.splitlines():
                if line.startswith("COPY ") and not line.startswith("COPY --from="):
                    self.assertTrue((context / line.split()[1]).exists(), line)
        self.assertIn("site-packages:/", docker)


if __name__ == "__main__":
    unittest.main()
