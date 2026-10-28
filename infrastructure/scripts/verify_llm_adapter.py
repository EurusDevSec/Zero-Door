"""ZER-48 bounded adapter receipt. Default is plan-only; no agent or lab imports."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import canonical, new_id
from event_pipeline.llm import Adapter, HttpxTransport, Limits, MODEL, RunBudget

CONFIG = {"model": MODEL, "endpoint": "https://api.openai.com/v1/responses", "calls": 1, "attempts": 1,
          "max_output_tokens": 256, "max_request_bytes": 8192, "max_reserved_tokens": 9472,
          "max_estimated_usd": "0.005", "attempt_timeout_s": 20, "call_deadline_s": 25,
          "process_deadline_s": 30, "new_lab_requests": 0,
          "cost_limit_kind": "RESERVATION_ESTIMATE_NOT_PROVIDER_BILLING_CAP"}
OBSERVATION = {"data_origin": "SYNTHETIC_ADAPTER_HEALTH_NOT_LAB",
               "service": "sqli-fixture", "observed_health": "healthy", "evidence_ids": ["health-01"]}
INSTRUCTIONS = ("Summarize only supplied synthetic service health evidence. Return NORMAL for observed healthy, "
                "UNKNOWN for insufficient evidence. Cite only supplied evidence IDs. No cause attribution, "
                "tools, actions or recovery claims are available.")


class HealthSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification: Literal["NORMAL", "UNKNOWN"]
    evidence_ids: list[Literal["health-01"]] = Field(min_length=1)


def clean(value, secret):
    text = json.dumps(value, ensure_ascii=False)
    if secret:
        text = text.replace(secret, "[REDACTED]")
    return json.loads(re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED]", text))


class Capture:
    def __init__(self, transport, secret=""):
        self.transport, self.secret, self.replies = transport, secret, []

    async def send(self, payload, timeout):
        reply = await self.transport.send(payload, timeout)
        self.replies.append(clean(reply, self.secret))
        return reply


class Offline:
    async def send(self, payload, timeout):
        return {"status": 200, "request_id": "req_OFFLINE_SIMULATED",
                "body": {"id": "resp_OFFLINE_SIMULATED", "status": "completed", "model": MODEL,
                         "output": [{"type": "message", "role": "assistant", "status": "completed",
                                     "content": [{"type": "output_text", "text": json.dumps({
                                         "classification": "NORMAL", "evidence_ids": ["health-01"]})}]}],
                         "usage": {"input_tokens": 100, "output_tokens": 30, "total_tokens": 130}}}


async def verify(live=False):
    key = os.environ.get("OPENAI_API_KEY", "") if live else ""
    transport = Capture(HttpxTransport(key) if live else Offline(), key)
    context = {"run_id": new_id("run"), "trial_id": new_id("trl"), "group": "B2",
               "method_version": "zer48-adapter-smoke/1", "config_ref": "sha256:" + hashlib.sha256(canonical(CONFIG)).hexdigest()}
    budget = RunBudget(context["run_id"], max_calls=1, max_reserved_tokens=9472,
                       max_estimated_usd="0.005", duration_s=30)
    adapter = Adapter(transport, budget, limits=Limits(attempts=1, timeout_s=20, deadline_s=25,
                                                     retry_delay_s=0, max_output_tokens=256))
    receipt = {"evidence_kind": "LIVE_PROVIDER_SYNTHETIC_INPUT" if live else "OFFLINE_SIMULATED",
               "started_at": datetime.now(timezone.utc).isoformat(), "context": context, "config": CONFIG,
               "input": OBSERVATION, "prompt_version": "zer48-health/1",
               "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
                   "agent-orchestrator/event_pipeline/llm.py", "infrastructure/scripts/verify_llm_adapter.py"]}}
    try:
        result = await asyncio.wait_for(adapter.call(context, decision_id=new_id("dec"), instructions=INSTRUCTIONS,
            observation=OBSERVATION, output_model=HealthSummary, prompt_version="zer48-health/1"), timeout=30)
        expected = result.outcome == "OK" and result.value.classification == "NORMAL"
        receipt.update(outcome=result.outcome, decision_source=result.decision_source,
                       value=result.value.model_dump() if result.value else None,
                       verdict="PASS_ADAPTER_SYNTHETIC" if expected and result.budget["cost_estimate_complete"] else "NOT_MET",
                       reason=result.reason)
    except (ValueError, asyncio.TimeoutError):
        receipt.update(verdict="NOT_MET", outcome="ERROR_OR_TIMEOUT", decision_source="NONE")
    receipt.update(events=adapter.events, budget=budget.summary(), replies=transport.replies,
                   finished_at=datetime.now(timezone.utc).isoformat(),
                   limits=["No lab or agent decision integration", "Alias does not prove immutable revision",
                           "Process-local budget; no restart durability claim", "Cost is an estimate, not billing"])
    return clean(receipt, key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Use fake transport, no key/network")
    mode.add_argument("--live", action="store_true", help="One paid provider call; requires separately approved budget")
    args = parser.parse_args()
    if not args.offline and not args.live:
        print(json.dumps({"mode": "PLAN_ONLY_NO_NETWORK", "config": CONFIG, "input": OBSERVATION}, indent=2))
        return 0
    # No inference is made when credentials are missing; never print a key or provider exception.
    if args.live and not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY missing; no request sent.")
        return 2
    try:
        receipt = asyncio.run(verify(args.live))
    except ValueError:
        print("Adapter configuration invalid; no successful inference receipt.")
        return 2
    out = ROOT / "scratch" / "zer48" / "runs" / receipt["context"]["run_id"]
    out.mkdir(parents=True, exist_ok=False)
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print(json.dumps({"receipt": str(path), "evidence_kind": receipt["evidence_kind"],
                      "verdict": receipt["verdict"], "attempts": receipt["budget"]["attempts_dispatched"]}, indent=2))
    return 0 if receipt["verdict"] == "PASS_ADAPTER_SYNTHETIC" else 1


if __name__ == "__main__":
    raise SystemExit(main())
