"""Bounded functional Gaia diagnosis from saved O-only evidence. PLAN_ONLY by default.

--live makes only the explicitly configured model request. No lab, broker or healer.
An exclusive run directory prevents replay after success, failure or unknown outcome.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path

from event_pipeline.contract import canonical, valid_id, new_id, Producer
from event_pipeline.llm import Adapter, HttpxTransport, Limits, RunBudget, strict_json
from gaia.diagnosis import Diagnoser, PURPOSE, observation_valid


def read_json(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(32769)
    if len(raw) > 32768:
        raise ValueError("GAIA_FILE_TOO_LARGE")
    return strict_json(raw)


def config_valid(config):
    if (not isinstance(config, dict) or set(config) != {"purpose", "benchmark_eligible", "context",
            "max_calls", "max_reserved_tokens", "max_estimated_usd", "duration_s"}
            or config["purpose"] != PURPOSE or config["benchmark_eligible"] is not False
            or not isinstance(config["context"], dict)
            or set(config["context"]) != {"run_id", "trial_id", "incident_id", "group", "method_version", "config_ref"}
            or config["context"]["group"] != "B2"
            or any(not valid_id(config["context"][k], kind) for k, kind in
                   (("run_id", "run"), ("trial_id", "trl"), ("incident_id", "inc")))
            or type(config["max_calls"]) is not int or not 1 <= config["max_calls"] <= 3
            or type(config["max_reserved_tokens"]) is not int or not 1 <= config["max_reserved_tokens"] <= 30000
            or type(config["max_estimated_usd"]) not in (int, float) or not 0 < config["max_estimated_usd"] <= .005
            or type(config["duration_s"]) not in (int, float) or not 0 < config["duration_s"] <= 600):
        raise ValueError("GAIA_CONFIG_INVALID")
    # Validate remaining context fields using the same contract, before reserving a directory.
    Producer("detector", "config-check", {"clock_id": "gaia", "clock_source": "UNKNOWN", "resolution_ms": None}).event(
        config["context"], "DETECTED", {"rule_id": "CONFIG_CHECK", "rule_version": "1", "signature": "check",
        "metric": "check", "value": 1, "threshold": 0, "severity": "WARNING", "description": "config validation"},
        "o.alert", target={"namespace": "target-app", "service": "fixture", "flow": None}, alert_id=new_id("alt"))


class Journal:
    def __init__(self, output, config):
        self.directory = Path(output) / config["context"]["run_id"]
        self.directory.mkdir()  # Parent chosen by owner; never exist_ok/replay.
        (self.directory / "started.json").write_bytes(canonical({"config": config, "restart_allowed": False}) + b"\n")
        self.stream = (self.directory / "events.jsonl").open("xb")

    def __call__(self, item):
        self.stream.write(canonical(item) + b"\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def close(self):
        self.stream.close()


def open_diagnoser(config, output):
    config_valid(config)
    budget = RunBudget(config["context"]["run_id"], max_calls=config["max_calls"],
        max_reserved_tokens=config["max_reserved_tokens"], max_estimated_usd=config["max_estimated_usd"],
        duration_s=config["duration_s"])
    adapter = Adapter(HttpxTransport(os.environ.get("OPENAI_API_KEY", "")), budget,
        limits=Limits(attempts=1, timeout_s=20, deadline_s=25, retry_delay_s=0, max_output_tokens=256))
    journal = Journal(output, config)
    return Diagnoser(adapter, config["context"], journal), journal


async def live(args):
    config, observation = read_json(args.config), read_json(args.observation)
    config_valid(config)
    if not isinstance(observation, dict) or set(observation) != {"detection", "evidence"}:
        raise ValueError("GAIA_OBSERVATION_INVALID")
    observation_valid(observation["detection"], observation["evidence"])
    if any(observation["detection"].get(k) != v for k, v in config["context"].items()):
        raise ValueError("GAIA_CONTEXT_MISMATCH")
    engine, journal = open_diagnoser(config, args.output)
    try:
        receipt = await asyncio.wait_for(engine.analyze(observation["detection"], observation["evidence"]), 30)
        (journal.directory / "receipt.json").write_bytes(canonical(receipt) + b"\n")
    finally:
        journal.close()
    print(json.dumps({"status": receipt["status"], "receipt": str(journal.directory / "receipt.json")}))
    return 0 if receipt["status"] == "OK" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--observation")
    parser.add_argument("--output")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"status": "PLAN_ONLY", "provider_calls": 0, "executor_dispatches": 0}))
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
