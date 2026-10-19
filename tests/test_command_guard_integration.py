"""Actual FastAPI entrypoints through ASGI with fake Kafka/model/Kubernetes only.

No startup hooks or external services run. Each test admits at most one bounded command.
"""
import asyncio
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid
from unittest.mock import AsyncMock, Mock, patch
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from test_command_modes import decision
FIXTURE = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())


def load(name):
    spec = importlib.util.spec_from_file_location("zer12_" + name, ROOT / "agent-orchestrator" / name / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EntrypointTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        self.policy = deepcopy(FIXTURE["policy"])
        self.policy_file = self.directory / "policy.json"
        self.heal_operator = dict(id="heal-fixture", purpose="heal-operator", secret="offline-heal-operator-token-0000000000")
        self.operator = dict(id="fixture-operator", purpose="operator", secret="offline-operator-token-0000000000000000")
        for filename, value in [("operator.json", self.operator), ("signer.json", FIXTURE["key"]), ("heal-operator.json", self.heal_operator)]:
            (self.directory / filename).write_text(json.dumps(value))
        self.write_policy()
        self.environment = patch.dict(os.environ, {"ZD_COMMAND_POLICY_FILE": str(self.policy_file),
            "ZD_OPERATOR_TOKEN_FILE": str(self.directory / "operator.json"), "ZD_COMMAND_SIGNER_FILE": str(self.directory / "signer.json"),
            "ZD_COMMAND_LEDGER_FILE": str(self.directory / "claims.sqlite"), "ZD_EVENT_URL": "", "OPENAI_API_KEY": "", "GEMINI_API_KEYS": ""})
        self.environment.start()
        self.nemesis, self.healer = load("nemesis"), load("hephaestus")
        self.producer = Mock()
        self.producer.send.return_value.get.return_value = None
        self.plan = AsyncMock(return_value=dict(attackType="HTTP_FLOOD", targetService="frontend", durationSec=3600, concurrency=100))
        self.guards = [patch.object(self.nemesis, "get_kafka_producer", return_value=self.producer),
                       patch.object(self.nemesis, "generate_attack_plan_from_llm", self.plan),
                       patch.object(self.healer, "init_k8s", side_effect=AssertionError("no Kubernetes")),
                       patch.object(self.healer, "KafkaConsumer", side_effect=AssertionError("no legacy broker")),
                       patch.object(self.healer, "action_scale_up", side_effect=AssertionError("no healing"))]
        for guard in self.guards:
            guard.start()
        self.headers = {"Authorization": "Bearer " + self.operator["secret"], "Idempotency-Key": str(uuid.uuid4())}
        self.body = dict(attackType="HTTP_FLOOD", targetService="frontend", durationSec=3600)

    def write_policy(self):
        self.policy_file.write_text(json.dumps(self.policy))

    async def asyncTearDown(self):
        for guard in self.guards:
            guard.stop()
        self.environment.stop()
        self.tmp.cleanup()

    async def post(self, module, path, body=None, headers=None, raw=None):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=module.app), base_url="http://offline") as client:
            if module is self.healer:
                with patch.dict(os.environ, {"ZD_OPERATOR_TOKEN_FILE": str(self.directory / "heal-operator.json")}):
                    return await client.post(path, content=raw, json=body if raw is None else None,
                                             headers=dict(self.headers, Authorization="Bearer " + self.heal_operator["secret"]) if headers is None else headers)
            return await client.post(path, content=raw, json=body if raw is None else None, headers=self.headers if headers is None else headers)

    def no_effects(self):
        self.producer.send.assert_not_called()
        self.plan.assert_not_called()
        self.healer.action_scale_up.assert_not_called()

    async def test_missing_or_wrong_operator_before_publish_and_model(self):
        for headers in [{}, {"Authorization": "Bearer wrong"}, {"Authorization": "Bearer " + FIXTURE["key"]["secret"]}]:
            for route in ["/attack/trigger", "/attack/llm-plan", "/api/reset"]:
                response = await self.post(self.nemesis, route, {}, headers=headers)
                self.assertEqual(401, response.status_code, response.text)
        self.no_effects()

    async def test_bad_schema_target_and_id_no_effects(self):
        for raw in [b'{"attackType":"HTTP_FLOOD","attackType":"POD_KILL"}', b'{"durationSec":NaN}', b'[' * 18 + b'0' + b']' * 18, b'x' * 17000]:
            response = await self.post(self.nemesis, "/attack/trigger", raw=raw)
            self.assertIn(response.status_code, (400, 413), response.text)
        for change in [dict(targetNamespace="monitoring"), dict(targetURL="http://outside.invalid/"), dict(durationSec=0), dict(durationSec=True), dict(concurrency=1.5), dict(extra=1), dict(attackType=[]), dict(intensity={}), dict(targetService=[] ), dict(targetURL=[]), dict(targetURL=False), dict(targetURL=None), dict(attackType="CPU_STRESS", targetURL=[])]:
            response = await self.post(self.nemesis, "/attack/trigger", dict(self.body, **change))
            self.assertEqual(400, response.status_code, response.text)
        response = await self.post(self.nemesis, "/attack/trigger", self.body, headers=dict(self.headers, **{"Idempotency-Key": "short"}))
        self.assertEqual(400, response.status_code)
        self.no_effects()

    async def test_actual_route_publishes_signed_capped_command_once_after_restart(self):
        first = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(200, first.status_code, first.text)
        envelope = self.producer.send.call_args.args[1]
        import base64
        command = json.loads(base64.b64decode(envelope["payload"]))
        self.assertEqual((1, 1), (command["parameters"]["duration"], command["safetyLimits"]["maxDuration"]))
        self.assertEqual(self.policy["context"], command["context"])
        again = await self.post(load("nemesis"), "/attack/trigger", self.body)
        self.assertEqual(first.json(), again.json())
        self.assertEqual(1, self.producer.send.call_count)
        conflict = await self.post(self.nemesis, "/attack/trigger", dict(self.body, durationSec=10))
        self.assertEqual(409, conflict.status_code, conflict.text)
        self.plan.assert_not_called()
        self.policy["context"]["trial_id"] = "trl_" + "f" * 32
        self.write_policy()
        changed_context = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(409, changed_context.status_code, changed_context.text)
        self.assertEqual(1, self.producer.send.call_count)

    async def test_publish_unknown_is_not_retried(self):
        self.producer.send.return_value.get.side_effect = TimeoutError("offline ack lost")
        first = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, first.status_code)
        second = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(409, second.status_code, second.text)
        self.assertEqual(1, self.producer.send.call_count)
        self.assertIn("OUTCOME_UNKNOWN", second.text)

    async def test_send_invocation_error_stays_unknown_but_setup_error_is_terminal(self):
        with patch.object(self.nemesis, "get_kafka_producer", side_effect=RuntimeError("fixture setup")):
            setup = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, setup.status_code)
        self.assertIn("PRE_PUBLISH_FAILED", setup.text)
        retry = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(setup.json(), retry.json())
        self.producer.send.assert_not_called()
        # Separate ledger, so this control does not rely on pacing or reset claims.
        with patch.dict(os.environ, {"ZD_COMMAND_LEDGER_FILE": str(self.directory / "send-error.sqlite")}):
            self.producer.send.side_effect = RuntimeError("fixture send outcome uncertain")
            first = await self.post(self.nemesis, "/attack/trigger", self.body)
            self.assertEqual(503, first.status_code)
            self.assertIn("OUTCOME_UNKNOWN", first.text)
            retry = await self.post(self.nemesis, "/attack/trigger", self.body)
            self.assertEqual(409, retry.status_code)
            self.assertIn("OUTCOME_UNKNOWN", retry.text)
        self.assertEqual(1, self.producer.send.call_count)
        self.plan.assert_not_called()

    async def test_benchmark_model_scenario_generation_is_blocked_in_all_groups(self):
        for group in ["B2", "B3", "B0", "BM", "B1"]:
            self.policy["context"]["group"] = group
            self.write_policy()
            response = await self.post(self.nemesis, "/attack/llm-plan", {})
            self.assertEqual(409, response.status_code, response.text)
            self.assertIn("BENCHMARK_SCENARIO_LLM_DISABLED", response.text)
        self.no_effects()
        self.assertFalse((self.directory / "claims.sqlite").exists())

    async def test_unavailable_producer_is_terminal_and_does_not_poison_admission(self):
        with patch.object(self.nemesis, "get_kafka_producer", return_value=None):
            first = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, first.status_code)
        self.assertIn("PRODUCER_UNAVAILABLE", first.text)
        # Same request stays a known refusal, even after the producer recovers.
        retry = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(first.json(), retry.json())
        self.producer.send.assert_not_called()
        import time
        from nemesis.command_guard import Ledger
        claim = Ledger.claim
        later = time.time() + 7
        # claim's clock is an injectable function captured at definition time.
        def paced_claim(ledger, request_id, value):
            return claim(ledger, request_id, value, clock=lambda: later)
        with patch.object(Ledger, "claim", new=paced_claim):
            fresh = await self.post(self.nemesis, "/attack/trigger", self.body,
                                    headers=dict(self.headers, **{"Idempotency-Key": str(uuid.uuid4())}))
        self.assertEqual(200, fresh.status_code, fresh.text)
        self.assertEqual(1, self.producer.send.call_count)
        self.plan.assert_not_called()

    async def test_ledger_failure_after_send_reports_unknown_without_replay(self):
        from nemesis.command_guard import Ledger, Refused
        with patch.object(Ledger, "complete", side_effect=Refused("LEDGER_UNAVAILABLE", 503)):
            first = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, first.status_code)
        self.assertIn("OUTCOME_UNKNOWN", first.text)
        retry = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(409, retry.status_code)
        self.assertIn("OUTCOME_UNKNOWN", retry.text)
        self.assertEqual(1, self.producer.send.call_count)
        self.producer.send.return_value.get.assert_called_once_with(timeout=10)
        self.plan.assert_not_called()

    async def test_disabled_config_and_ledger_failure_no_effects(self):
        self.policy["enabled"] = False; self.write_policy()
        response = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(409, response.status_code)
        self.policy["enabled"] = True; self.write_policy()
        with patch.dict(os.environ, {"ZD_COMMAND_LEDGER_FILE": str(self.directory / "missing" / "claims")}):
            response = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, response.status_code, response.text)
        self.no_effects()

    async def test_healer_http_context_and_legacy_bypasses_cannot_execute(self):
        for group in ["B0", "BM", "B1", "B2", "B3"]:
            source, kind = ("operator_console", "MANUAL") if group == "BM" else ("decision_rules", "RULES")
            ctx, event = decision(group, source, kind)
            self.policy["context"] = ctx; self.write_policy()
            fake = SimpleNamespace(run=ctx["run_id"], trial=ctx["trial_id"], context=lambda: ctx,
                                   records=lambda: [{"envelope": event}])
            with patch.object(self.healer, "r1_client", fake):
                response = await self.post(self.healer, "/heal/trigger", {"decision_id": event["decision_id"]})
                self.assertEqual(409, response.status_code, response.text)
                if group == "BM":
                    self.assertIn("R1_EXECUTOR_DISABLED", response.text)
        with self.assertRaises(ValueError):
            self.healer.process_alert({"type": "HIGH_CPU", "affectedService": "frontend"})
        self.healer._kafka_consumer_thread()  # Legacy path returns before creating a broker client.
        asyncio_result = await self.post(self.healer, "/experiment/reset", {})
        self.assertEqual(409, asyncio_result.status_code)
        self.no_effects()

    async def test_native_model_key_is_not_in_url_or_response_log(self):
        fixture_key = "public-fixture-not-a-real-key-00000000"
        response = Mock(status_code=200)
        response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        fake = AsyncMock()
        fake.post.return_value = response
        manager = AsyncMock()
        manager.__aenter__.return_value = fake
        with patch.object(self.nemesis.httpx, "AsyncClient", return_value=manager):
            self.assertEqual("ok", await self.nemesis.call_gemini_native(fixture_key, "offline-model", "fixture", "fixture"))
            args = fake.post.call_args
            self.assertNotIn(fixture_key, args.args[0])
            self.assertNotIn("?key=", args.args[0])
            self.assertEqual(fixture_key, args.kwargs["headers"]["x-goog-api-key"])
            response.status_code = 503
            response.text = "DO_NOT_LOG_RAW_RESPONSE"
            with patch.object(self.nemesis.logger, "error") as log:
                with self.assertRaises(RuntimeError):
                    await self.nemesis.call_gemini_native(fixture_key, "offline-model", "fixture", "fixture")
                self.assertNotIn(response.text, str(log.call_args_list))
                self.assertNotIn(fixture_key, str(log.call_args_list))
        self.no_effects()

    async def test_operator_credentials_cannot_cross_fault_and_heal_roles(self):
        response = await self.post(self.healer, "/heal/trigger", {}, headers=self.headers)
        self.assertEqual(401, response.status_code, response.text)
        response = await self.post(self.nemesis, "/attack/trigger", self.body,
                                   headers=dict(self.headers, Authorization="Bearer " + self.heal_operator["secret"]))
        self.assertEqual(401, response.status_code, response.text)
        # Even if a wrong-role file is accidentally mounted, purpose is checked.
        with patch.dict(os.environ, {"ZD_OPERATOR_TOKEN_FILE": str(self.directory / "heal-operator.json")}):
            response = await self.post(self.nemesis, "/attack/trigger", self.body)
        self.assertEqual(503, response.status_code, response.text)
        with patch.dict(os.environ, {"ZD_OPERATOR_TOKEN_FILE": str(self.directory / "operator.json")}):
            from nemesis.command_guard import CommandGuard, Refused
            with self.assertRaises(Refused):
                CommandGuard(self.policy).authorize(self.headers["Authorization"], purpose="heal-operator")
        self.no_effects()

    async def test_reset_never_proxies_or_clears_state(self):
        self.nemesis.REASONING_CHAT_BUFFER.append({"keep": True})
        response = await self.post(self.nemesis, "/api/reset", {})
        self.assertEqual(409, response.status_code)
        self.assertEqual([{"keep": True}], self.nemesis.REASONING_CHAT_BUFFER)
        self.no_effects()


if __name__ == "__main__":
    unittest.main(verbosity=2)
