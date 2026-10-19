"""Offline behavior checks: no Doppler access, network, or inference."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("zer36_probe", ROOT / "infrastructure/scripts/verify-llm-backend.py")
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def success():
    decision = {"classification": "HIGH_CPU", "affected_service": "frontend",
                "evidence_ids": ["cpu-01", "duration-01"], "confidence": 0.9,
                "explanation": "Synthetic CPU 88% above 80% for 75 seconds."}
    return {"http_status": 200, "transport_error": None, "headers": {"x-request-id": "offline-request"},
            "body": {"id": "offline-response", "model": probe.MODEL, "status": "completed",
                     "usage": {"input_tokens": 400, "output_tokens": 60, "total_tokens": 460},
                     "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(decision)}]}]}}


class ProbeTests(unittest.TestCase):
    def sequence(self, replies):
        sequence = iter(replies)
        calls, sleeps = [], []

        def transport(payload):
            calls.append(payload)
            return copy.deepcopy(next(sequence))

        result = probe.run_probe(transport, sleep=sleeps.append)
        self.assertEqual(result["evidence_kind"], "OFFLINE_SIMULATED")
        return result, calls, sleeps

    def test_success_and_caps(self):
        result, calls, sleeps = self.sequence([success()])
        self.assertEqual((result["verdict"], result["decision_source"], result["degraded"]), ("PASS", "LLM", False))
        self.assertEqual(len(calls), 1)
        self.assertEqual(sleeps, [])
        self.assertEqual(calls[0]["max_output_tokens"], 512)
        self.assertFalse(calls[0]["store"])
        self.assertNotIn("tools", calls[0])
        self.assertAlmostEqual(result["known_usage_cost_estimate_usd"], 0.00007)

    def test_timeout_retry_exhaustion_fallback(self):
        for error in ("process_timeout", "curl_exit_28", "curl_exit_6", "curl_exit_7"):
            with self.subTest(error=error):
                timeout = {"http_status": 0, "transport_error": error, "headers": {}, "body": {}}
                result, calls, sleeps = self.sequence([timeout, timeout])
                self.assertEqual(len(calls), 2)
                self.assertEqual(sleeps, [1])
                self.assertEqual((result["verdict"], result["decision_source"], result["degraded"]), ("FAIL", "RULES", True))
                self.assertEqual(result["unknown_usage_attempts"], [1, 2])
                self.assertFalse(result["cost_estimate_complete"])

    def test_transport_failure_then_success(self):
        for error in ("process_timeout", "curl_exit_28", "curl_exit_6", "curl_exit_7"):
            with self.subTest(error=error):
                failure = {"http_status": 0, "transport_error": error, "headers": {}, "body": {}}
                result, calls, sleeps = self.sequence([failure, success()])
                self.assertEqual(len(calls), 2)
                self.assertEqual(sleeps, [1])
                self.assertEqual((result["verdict"], result["decision_source"]), ("PASS", "LLM"))
                self.assertEqual(result["unknown_usage_attempts"], [1])

    def test_200_with_transport_timeout_is_not_a_valid_decision(self):
        reply = success()
        reply["transport_error"] = "curl_exit_28"
        result, calls, sleeps = self.sequence([reply, reply])
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [1])
        self.assertEqual((result["verdict"], result["decision_source"], result["degraded"]), ("FAIL", "RULES", True))

    def test_refusal_overrides_valid_output_text(self):
        reply = success()
        reply["body"]["output"][0]["content"].append({"type": "refusal", "refusal": "offline refusal"})
        result, calls, _ = self.sequence([reply])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["attempts"][0]["validation_error"], "provider_refusal")
        self.assertEqual((result["verdict"], result["decision_source"]), ("FAIL", "RULES"))

    def test_valid_schema_wrong_expected_class(self):
        for classification in ("NORMAL", "UNKNOWN"):
            with self.subTest(classification=classification):
                reply = success()
                part = reply["body"]["output"][0]["content"][0]
                value = json.loads(part["text"])
                value["classification"] = classification
                part["text"] = json.dumps(value)
                result, calls, _ = self.sequence([reply])
                self.assertEqual(len(calls), 1)
                self.assertEqual(result["attempts"][0]["validation_error"], "synthetic_expected_result_mismatch")
                self.assertEqual((result["verdict"], result["decision_source"]), ("FAIL", "RULES"))

    def test_transient_retry_then_success(self):
        for status in (429, 500, 502, 503, 504):
            with self.subTest(status=status):
                failure = {"http_status": status, "transport_error": None, "headers": {},
                           "body": {"error": {"code": "rate_limit_exceeded"}}}
                result, calls, sleeps = self.sequence([failure, success()])
                self.assertEqual(len(calls), 2)
                self.assertEqual(result["verdict"], "PASS")
                self.assertFalse(result["cost_estimate_complete"])

    def test_auth_budget_unknown_429_no_retry(self):
        for status, code in [(401, "invalid_api_key"), (403, None), (400, None), (429, None)] + [(429, c) for c in probe.FATAL_429]:
            with self.subTest(status=status, code=code):
                failure = {"http_status": status, "transport_error": None, "headers": {}, "body": {"error": {"code": code}}}
                result, calls, sleeps = self.sequence([failure])
                self.assertEqual(len(calls), 1)
                self.assertEqual((result["verdict"], result["decision_source"]), ("FAIL", "RULES"))
                self.assertEqual(sleeps, [])

    def test_200_bad_payload_never_passes(self):
        for kind in ("missing_usage", "empty_usage", "negative_usage", "inconsistent_usage", "incomplete", "refusal", "bad_json", "extra_key", "wrong_enum", "missing_evidence", "boolean_confidence", "wrong_model", "output_cap"):
            with self.subTest(kind=kind):
                reply = success()
                body = reply["body"]
                part = body["output"][0]["content"][0]
                if kind == "missing_usage": body.pop("usage")
                elif kind == "empty_usage": body["usage"] = {}
                elif kind == "negative_usage": body["usage"]["input_tokens"] = -1
                elif kind == "inconsistent_usage": body["usage"]["total_tokens"] = 0
                elif kind == "incomplete": body["status"] = "incomplete"
                elif kind == "refusal": part["type"] = "refusal"
                elif kind == "bad_json": part["text"] = "not json"
                elif kind == "wrong_model": body["model"] = "other-model"
                elif kind == "output_cap": body["usage"] = {"input_tokens": 400, "output_tokens": 513, "total_tokens": 913}
                else:
                    value = json.loads(part["text"])
                    if kind == "extra_key": value["shell"] = "unexpected"
                    elif kind == "wrong_enum": value["classification"] = "ATTACK"
                    elif kind == "missing_evidence": value["evidence_ids"] = []
                    elif kind == "boolean_confidence": value["confidence"] = True
                    part["text"] = json.dumps(value)
                result, calls, _ = self.sequence([reply])
                self.assertEqual((result["verdict"], result["decision_source"]), ("FAIL", "RULES"))
                self.assertEqual(len(calls), 1)
                if kind in {"missing_usage", "empty_usage", "negative_usage", "inconsistent_usage"}:
                    self.assertFalse(result["cost_estimate_complete"])

    def test_transport_timeout_and_key_not_in_argv(self):
        key = "sk-proj-offline-fake-secret"
        with patch.object(probe.subprocess, "run", side_effect=subprocess.TimeoutExpired("curl", 35)) as mock:
            result = probe.curl_transport(probe.REQUEST, key)
        args, kwargs = mock.call_args
        self.assertNotIn(key, " ".join(args[0]))
        self.assertIn(key, kwargs["input"])
        self.assertEqual(kwargs["timeout"], 35)
        self.assertIn("30", args[0])
        self.assertNotIn("--location", args[0])
        self.assertEqual(result["transport_error"], "process_timeout")
        self.assertNotIn(key, json.dumps(probe.clean({"echo": key}, key)))

    def test_invalid_key_sends_nothing(self):
        with patch.object(probe.subprocess, "run") as mock:
            for key in ("", 'bad"header', "bad\nheader"):
                with self.assertRaises(ValueError): probe.curl_transport(probe.REQUEST, key)
            mock.assert_not_called()

    def test_transport_parses_body_headers_and_http_error(self):
        for status, content, exit_code in ((200, json.dumps(success()["body"]), 0), (401, '{"error":{"code":"invalid_api_key"}}', 0), (0, "partial json", 28)):
            with self.subTest(status=status):
                def fake_run(command, **kwargs):
                    Path(command[command.index("--output") + 1]).write_text(content, encoding="utf-8")
                    Path(command[command.index("--dump-header") + 1]).write_text(
                        "HTTP/1.1 200 OK\r\nx-request-id: offline-rid\r\nSet-Cookie: not-for-receipt\r\n", encoding="utf-8")
                    self.assertEqual(command[1], "--disable")
                    self.assertEqual(command[command.index("--retry") + 1], "0")
                    self.assertEqual(command[command.index("--proto") + 1], "=https")
                    self.assertEqual(command[command.index("--connect-timeout") + 1], "10")
                    self.assertEqual(command[command.index("--max-time") + 1], "30")
                    return subprocess.CompletedProcess(command, exit_code, str(status), "ignored")
                with patch.object(probe.subprocess, "run", side_effect=fake_run):
                    reply = probe.curl_transport(probe.REQUEST, "sk-offline")
                self.assertEqual(reply["http_status"], status)
                self.assertEqual(reply["headers"], {"x-request-id": "offline-rid"})
                if status == 200: probe.validate_response(reply["body"])
                if exit_code: self.assertEqual(reply["transport_error"], "curl_exit_28")


if __name__ == "__main__":
    unittest.main(verbosity=2)
