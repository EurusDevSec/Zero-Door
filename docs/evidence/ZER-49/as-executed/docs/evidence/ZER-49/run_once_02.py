"""One approved functional inference; default only prints plan. No lab/executor."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_child(command, env, *, timeout=40):
    child = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    timed_out = False
    try:
        child.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        # Parent interruption/wait errors also own cleanup, not just timeouts.
        if child.poll() is None:
            child.kill()  # This owned native Python child creates no subprocesses.
            child.wait(timeout=5)
    return {"pid": child.pid, "exit_code": child.returncode, "timed_out": timed_out,
            "process_reaped": child.poll() is not None}


def execute(authorization):
    auth = json.loads(Path(authorization).read_text(encoding="utf-8"))
    manifest_path = HERE / "inference-prep-02/source-manifest.json"
    if (auth.get("approved") is not True or auth.get("issue") != "ZER-49"
            or auth.get("proposal_sha256") != sha(HERE / "continuation-proposal.md")
            or auth.get("source_manifest_sha256") != sha(manifest_path)):
        raise ValueError("EXACT_OWNER_APPROVAL_REQUIRED")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, digest in manifest["sha256"].items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != digest:
            raise ValueError("SOURCE_CHANGED")
    previous = json.loads((HERE / "inference-01/final-conclusion.json").read_bytes())
    if previous.get("status") != "NOT_MET" or previous.get("cleanup") != "PROCESS_REAPED" or previous.get("provider_calls") != 1:
        raise ValueError("PREVIOUS_ATTEMPT_NOT_CLOSED")
    output = HERE / "inference-02"
    output.mkdir()  # Single use, including fail/unknown. Never remove or exist_ok.
    started = time.monotonic()
    result = {"status": "NOT_MET", "provider_calls": "UNKNOWN", "cleanup": "UNKNOWN"}
    if not os.environ.get("OPENAI_API_KEY"):
        result.update(reason="DOPPLER_KEY_MISSING", provider_calls=0, cleanup="NO_CHILD_STARTED")
    else:
        env = dict(os.environ, PYTHONUTF8="1", PYTHONPATH=str(ROOT / "agent-orchestrator"))
        child = run_child([sys.executable, "-B", "-m", "gaia.diagnosis_cli", "--live",
            "--config", str(HERE / "inference-prep-02/config.json"), "--observation",
            str(HERE / "inference-prep-02/observation.json"), "--output", str(output)], env)
        result.update(child=child, cleanup="PROCESS_REAPED" if child["process_reaped"] else "UNKNOWN")
        config = json.loads((HERE / "inference-prep-02/config.json").read_bytes())
        receipt_path = output / config["context"]["run_id"] / "receipt.json"
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_bytes())
            observation = json.loads((HERE / "inference-prep-02/observation.json").read_bytes())
            budget, traces = receipt["budget"], receipt["model_events"]
            result["provider_calls"] = budget["attempts_dispatched"]
            sys.path.insert(0, str(ROOT / "agent-orchestrator"))
            from event_pipeline.contract import validate
            passed = (child["exit_code"] == 0 and not child["timed_out"] and child["process_reaped"]
                and receipt["status"] == "OK" and receipt["decision_source"] == "LLM" and not receipt["fallback"]
                and receipt["diagnosis"]["classification"] == "APPLICATION_ERROR"
                and receipt["diagnosis"]["evidence_ids"] == [observation["detection"]["event_id"]]
                and receipt["detected_at"] == observation["detection"]["ts_event"]
                and len(traces) == 1 and not validate(traces[0]) and not validate(receipt["decision"])
                and traces[0]["payload"]["outcome"] == "OK" and traces[0]["payload"]["model"] == "gpt-6-luna"
                and traces[0]["causation_id"] == observation["detection"]["event_id"]
                and budget["attempts_dispatched"] == 1 and budget["unknown_usage_attempts"] == 0
                and budget["cost_estimate_complete"] and not budget["blocked"]
                and budget["reserved_estimate_usd"] <= .005 and budget["known_output_tokens"] <= 256)
            result["status"] = "TECHNICAL_PASS_PENDING_REVIEW_PUBLICATION" if passed else "NOT_MET"
        else:
            result["reason"] = "RECEIPT_MISSING_OUTCOME_UNKNOWN"
    result["elapsed_s"] = time.monotonic() - started
    (output / "final-conclusion.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["status"] == "TECHNICAL_PASS_PENDING_REVIEW_PUBLICATION" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "PLAN_ONLY", "provider_calls": 0, "lab_calls": 0}))
        return 0
    if not args.authorization:
        parser.error("exact authorization file required")
    try:
        return execute(args.authorization)
    except Exception as error:
        print(json.dumps({"status": "NOT_MET_OR_UNKNOWN", "error_type": type(error).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
