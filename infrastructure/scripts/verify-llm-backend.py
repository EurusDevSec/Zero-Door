"""Standalone R0 evidence probe; never imports or operates the live agents/lab."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
MODEL = "gpt-6-luna"
MAX_ATTEMPTS = 2
MAX_OUTPUT = 512
MAX_REQUEST_BYTES = 8192
FIXTURE = {
    "data_origin": "SYNTHETIC_R0_NOT_LAB",
    "alert": {"type": "HIGH_CPU", "severity": "WARNING",
              "affectedService": "frontend", "affectedNamespace": "target-app",
              "metric": "cpu_usage_over_limit_percent", "currentValue": 88.0,
              "threshold": 80.0},
    "duration_seconds": 75,
    "coverage": "complete_for_synthetic_window",
    "evidence_ids": ["cpu-01", "duration-01"],
}
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "classification": {"type": "string", "enum": ["HIGH_CPU", "NORMAL", "UNKNOWN"]},
        "affected_service": {"type": "string", "enum": ["frontend"]},
        "evidence_ids": {"type": "array", "items": {"type": "string", "enum": FIXTURE["evidence_ids"]}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "explanation": {"type": "string"},
    },
    "required": ["classification", "affected_service", "evidence_ids", "confidence", "explanation"],
}
REQUEST = {
    "model": MODEL, "store": False, "service_tier": "default",
    "reasoning": {"effort": "none"}, "max_output_tokens": MAX_OUTPUT,
    "instructions": "Classify synthetic monitoring evidence for a research backend smoke test. "
                    "HIGH_CPU means CPU strictly above 80 percent for at least 60 seconds. "
                    "Use only supplied evidence IDs. Do not infer attack cause or recovery. "
                    "No tools or actions are available. Return the required JSON.",
    "input": json.dumps(FIXTURE, sort_keys=True),
    "text": {"format": {"type": "json_schema", "name": "r0_observation_v1",
                       "strict": True, "schema": SCHEMA}},
}
FATAL_429 = {"insufficient_quota", "organization_spend_limit_exceeded",
             "project_spend_limit_exceeded", "organization_usage_limit_exceeded",
             "credit_balance_exhausted"}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def clean(value, key=""):
    """Redact before persistence, including provider errors that might echo credentials."""
    text = json.dumps(value, ensure_ascii=False)
    if key:
        text = text.replace(key, "[REDACTED]")
    return json.loads(re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED]", text))


def validate_response(body):
    if body.get("status") != "completed":
        raise ValueError("response_not_completed")
    if body.get("model") != MODEL and not str(body.get("model", "")).startswith(MODEL + "-"):
        raise ValueError("unexpected_model")
    pieces = []
    for item in body.get("output", []):
        for part in item.get("content", []):
            if part.get("type") == "refusal":
                raise ValueError("provider_refusal")
            if part.get("type") == "output_text":
                pieces.append(part["text"])
    value = json.loads("".join(pieces))
    if not isinstance(value, dict) or set(value) != set(SCHEMA["required"]):
        raise ValueError("schema_keys")
    if value["classification"] not in SCHEMA["properties"]["classification"]["enum"]:
        raise ValueError("classification_enum")
    if value["affected_service"] != "frontend":
        raise ValueError("service_enum")
    ids = value["evidence_ids"]
    if not isinstance(ids, list) or any(x not in FIXTURE["evidence_ids"] for x in ids):
        raise ValueError("evidence_enum")
    c = value["confidence"]
    if type(c) not in (int, float) or not 0 <= c <= 1:
        raise ValueError("confidence_range")
    if not isinstance(value["explanation"], str) or not value["explanation"].strip():
        raise ValueError("explanation_missing")
    if value["classification"] != "HIGH_CPU" or set(ids) != set(FIXTURE["evidence_ids"]):
        raise ValueError("synthetic_expected_result_mismatch")
    usage = body.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage_missing")
    for field in ("input_tokens", "output_tokens", "total_tokens"):
        if type(usage.get(field)) is not int or usage[field] < 0:
            raise ValueError("usage_invalid")
    if usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]:
        raise ValueError("usage_inconsistent")
    if usage["output_tokens"] > MAX_OUTPUT:
        raise ValueError("output_cap_exceeded")
    return value


def curl_transport(payload, key):
    """Key travels via stdin config, not command arguments; redirects are not followed."""
    if not key or any(ch in key for ch in '\r\n"\\'):
        raise ValueError("key_missing_or_invalid")
    with tempfile.TemporaryDirectory(prefix="zer36-") as tmp:
        directory = Path(tmp)
        request_file = directory / "request.json"
        body_file, headers_file = directory / "body.json", directory / "headers.txt"
        encoded = json.dumps(payload).encode("utf-8")
        if len(encoded) > MAX_REQUEST_BYTES:
            raise ValueError("fixed_request_size_exceeded")
        request_file.write_bytes(encoded)
        command = ["curl", "--disable", "--config", "-", "--silent", "--show-error", "--retry", "0",
                   "--proto", "=https", "--connect-timeout", "10", "--max-time", "30",
                   "--max-filesize", "1048576", "--request", "POST",
                   "https://api.openai.com/v1/responses",
                   "--header", "Content-Type: application/json",
                   "--data-binary", "@" + str(request_file),
                   "--output", str(body_file), "--dump-header", str(headers_file),
                   "--write-out", "%{http_code}"]
        try:
            proc = subprocess.run(command, input='header = "Authorization: Bearer ' + key + '"\n',
                                  capture_output=True, text=True, timeout=35)
        except subprocess.TimeoutExpired:
            return {"http_status": 0, "transport_error": "process_timeout", "body": {}, "headers": {}}
        except OSError:
            return {"http_status": 0, "transport_error": "curl_unavailable", "body": {}, "headers": {}}
        headers = {}
        if headers_file.exists():
            for line in headers_file.read_text(encoding="utf-8", errors="replace").splitlines():
                name, sep, value = line.partition(":")
                if sep and name.lower() in {"x-request-id", "x-ratelimit-limit-requests",
                                            "x-ratelimit-limit-tokens", "retry-after"}:
                    headers[name.lower()] = value.strip()
        try:
            body = json.loads(body_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            body = {}
        if not isinstance(body, dict):
            body = {}
        return {"http_status": int(proc.stdout.strip() or 0), "headers": headers,
                "transport_error": None if proc.returncode == 0 else "curl_exit_" + str(proc.returncode),
                "body": body}


def run_probe(transport, sleep=time.sleep, evidence_kind="OFFLINE_SIMULATED"):
    result = {"run_id": "zer36-" + str(uuid.uuid4()), "started_at": utc_now(),
              "evidence_kind": evidence_kind, "fixture_origin": "SYNTHETIC_R0_NOT_LAB",
              "model_requested": MODEL, "request": copy.deepcopy(REQUEST),
              "request_sha256": hashlib.sha256(json.dumps(REQUEST, sort_keys=True).encode()).hexdigest(),
              "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "max_attempts": MAX_ATTEMPTS, "attempts": [], "decision_source": "RULES",
              "degraded": True, "verdict": "FAIL", "decision": None}
    start = time.monotonic()
    for number in range(1, MAX_ATTEMPTS + 1):
        tick = time.monotonic()
        response = transport(copy.deepcopy(REQUEST))
        body = response.get("body", {})
        attempt = {"number": number, "timestamp": utc_now(),
                   "latency_ms": round((time.monotonic() - tick) * 1000, 3), **response}
        result["attempts"].append(attempt)
        if response["http_status"] == 200 and not response.get("transport_error"):
            try:
                result["decision"] = validate_response(body)
            except (ValueError, TypeError, KeyError) as exc:
                attempt["validation_error"] = str(exc)
                break
            result.update(decision_source="LLM", degraded=False, verdict="PASS")
            break
        error = body.get("error") or {}
        code = error.get("code") if isinstance(error, dict) else None
        retryable = response.get("transport_error") in {"curl_exit_28", "curl_exit_6", "curl_exit_7", "process_timeout"}
        retryable |= response["http_status"] in {500, 502, 503, 504}
        retryable |= response["http_status"] == 429 and code == "rate_limit_exceeded"
        if code in FATAL_429 or not retryable or number == MAX_ATTEMPTS:
            break
        sleep(1)
    if result["degraded"]:
        result["decision"] = {"classification": "HIGH_CPU", "affected_service": "frontend",
                              "evidence_ids": FIXTURE["evidence_ids"], "policy": "synthetic_cpu_gt80_for_60s"}
    result["elapsed_ms"] = round((time.monotonic() - start) * 1000, 3)
    result["finished_at"] = utc_now()
    def known_usage(attempt):
        u = attempt["body"].get("usage")
        return (isinstance(u, dict) and all(type(u.get(k)) is int and u[k] >= 0
                for k in ("input_tokens", "output_tokens", "total_tokens"))
                and u["total_tokens"] == u["input_tokens"] + u["output_tokens"])
    result["unknown_usage_attempts"] = [a["number"] for a in result["attempts"] if not known_usage(a)]
    # Uncached Standard rates checked 2026-10-19; estimate, not a billing receipt.
    known = [a["body"]["usage"] for a in result["attempts"] if known_usage(a)]
    result["known_usage_cost_estimate_usd"] = round(sum(
        (u.get("input_tokens", 0) * 0.10 + u.get("output_tokens", 0) * 0.50) / 1_000_000
        for u in known), 9)
    result["cost_estimate_complete"] = not result["unknown_usage_attempts"]
    result["model_revision_note"] = "Returned model is recorded per attempt; an alias is not an immutable snapshot."
    result["request_id_missing_attempts"] = [a["number"] for a in result["attempts"]
        if not a.get("headers", {}).get("x-request-id")]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send at most two paid API requests via OPENAI_API_KEY")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"mode": "PLAN_ONLY_NO_NETWORK", "request": REQUEST}, indent=2))
        return 0
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or any(ch in key for ch in '\r\n"\\'):
        print("OPENAI_API_KEY missing/invalid; no request sent.")
        return 2
    directory = ROOT / "scratch" / "zer36" / "runs" / ("run-" + str(uuid.uuid4()))
    directory.mkdir(parents=True, exist_ok=False)
    result = run_probe(lambda payload: curl_transport(payload, key), evidence_kind="LIVE_OPENAI_SYNTHETIC_INPUT")
    result = clean(result, key)
    output = directory / "receipt.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"receipt": str(output), "verdict": result["verdict"],
                      "decision_source": result["decision_source"], "attempts": len(result["attempts"]),
                      "known_usage_cost_estimate_usd": result["known_usage_cost_estimate_usd"],
                      "cost_estimate_complete": result["cost_estimate_complete"]}, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
