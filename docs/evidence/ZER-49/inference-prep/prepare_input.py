"""Generate one synthetic benign observer sample through Gaia, entirely offline."""
import asyncio
import hashlib
import importlib.util
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.adapters import Detector
from event_pipeline.contract import Producer, canonical, new_id, now
from gaia.diagnosis import PURPOSE, observation_valid
from gaia.diagnosis_cli import config_valid

HERE = Path(__file__).resolve().parent
policy = {"purpose": PURPOSE, "benchmark_eligible": False, "model": "gpt-6-luna",
          "max_calls": 1, "max_output_tokens": 256, "attempts": 1, "max_estimated_usd": .005,
          "timeout_s": 20, "deadline_s": 25, "async_overall_s": 30, "process_timeout_s": 40,
          "window_s": 300, "input_class": "SYNTHETIC_BENIGN_OBSERVER_FUNCTIONAL_ONLY"}
ctx = {"run_id": new_id("run"), "trial_id": new_id("trl"), "incident_id": new_id("inc"),
       "group": "B2", "method_version": "zer49-functional/1",
       "config_ref": "sha256:" + hashlib.sha256(canonical(policy)).hexdigest()}
config = {"purpose": PURPOSE, "benchmark_eligible": False, "context": ctx, "max_calls": 1,
          "max_reserved_tokens": 9472, "max_estimated_usd": .005, "duration_s": 60}
rows = []
stamp = now()
log = {"message": "ERROR: owned fixture diagnostic sentinel; no user request or action is being executed.",
       "observed_at": stamp}

class OClient:
    producer = Producer("detector", "zer49-functional-input/1", {
        "clock_id": "gaia-prepared-input", "clock_source": "UNKNOWN", "resolution_ms": None})
    def context(self):
        return ctx
    def publish(self, event):
        rows.append(event)  # Offline capture, NOT authenticated archive delivery.

class ES:
    def search(self, **_):
        return {"hits": {"hits": [{"_source": {"message": log["message"], "@timestamp": stamp,
            "kubernetes": {"namespace_name": "target-app", "pod_name": "fixture-offline-sentinel",
                           "container_name": "sqli-fixture"}}}]}}

async def capture():
    with patch.dict(os.environ, {}, clear=True), patch.object(socket.socket, "connect", side_effect=AssertionError("OFFLINE_ONLY")):
        spec = importlib.util.spec_from_file_location("gaia_prepare", ROOT / "agent-orchestrator/gaia/main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.r1_client, module.r1_detector = OClient(), Detector(OClient())
        with patch.object(module, "get_es_client", return_value=ES()):
            await module.poll_elasticsearch_logs()

asyncio.run(capture())
if len(rows) != 1:
    raise ValueError("ONE_DETECTION_REQUIRED")
p = rows[0]["payload"]
observation = observation_valid(rows[0], {"metric": {"name": p["metric"], "value": p["value"], "threshold": p["threshold"]}, "log": log})
config_valid(config)
for name, value in (("policy.json", policy), ("config.json", config), ("observation.json", observation),
                    ("input-origin.json", {"class": policy["input_class"], "created_at": stamp,
                     "generator": "prepare_input.py via actual Gaia.poll_elasticsearch_logs/Detector",
                     "real_telemetry": False, "archive_delivery": "OFFLINE_CAPTURE_ONLY",
                     "provider_calls": 0, "lab_calls": 0})):
    with (HERE / name).open("xb") as stream:
        stream.write(canonical(value) + b"\n")
print("PREPARED_OFFLINE_ONE_DETECTION_ZERO_PROVIDER_ZERO_LAB")
