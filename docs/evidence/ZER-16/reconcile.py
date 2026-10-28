"""Offline, derived ZER-16 state assessment of immutable ZER-46 runtime09.

Reads files only; never dispatches a command or writes to the source evidence. These are new derived
assessments, not retroactively emitted events or proof that this observer was running in runtime09.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from hephaestus.sqli_action_state import SqliActionState  # noqa: E402


def replay():
    base = ROOT / "docs/evidence/ZER-46"
    run = base / "runtime-09"
    manifest = json.loads((base / "artifact-sha256.json").read_text(encoding="utf-8"))["files"]
    read_paths = set()

    def read(name):
        path = run / name
        expected = manifest["runtime-09/" + name]
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("RAW_HASH_MISMATCH: " + name)
        read_paths.add(name)
        return json.loads(path.read_text(encoding="utf-8"))

    pins = read("writer-pins.json")["target"]
    old, new = read("fixture-initial.json"), read("fixture-after-replacement.json")
    accepted = read("writer-1-block.json")["result"]
    # Conservative acknowledgement upper bound: the first independently read-back matching API policy.
    # The RPC result has no receipt timestamp; do not invent an exact API acknowledgement time.
    ack = read("raw/0116.json")
    cm = json.loads(ack["stdout"])
    if json.loads(cm["data"]["policy.json"])["rules"] != [accepted["rule"]]:
        raise ValueError("API_RULE_MISMATCH")
    state = SqliActionState(accepted, pins, fixture_uid=old["metadata"]["uid"],
                            accepted_at=ack["ended_at"], timeout_s=120)
    api_only = state.snapshot()

    def record(n):
        http = read(f"http-{n:03}.json")
        access = read(f"join-{n:03}.json")
        target = read(f"log-pod-target-{n:03}.json")
        return {"http": http, "access": access, "pod_uid": target["uid"], "ref": f"runtime-09/http-{n:03}.json"}

    def ready(pod):
        return {"uid": pod["metadata"]["uid"], "ready": any(
            c.get("type") == "Ready" and c.get("status") == "True" for c in pod["status"]["conditions"])}

    before = [record(n) for n in range(9, 15)]
    observed_at = max(r["http"]["response"]["end"] for r in before)
    completed = state.observe(before[0], before[1:], fixture=ready(old), now=observed_at)
    old_absent = read("raw/0241.json")
    if old_absent["returncode"] != 0 or old_absent["stdout"].strip():
        raise ValueError("OLD_POD_NOT_ABSENT")
    after = [record(n) for n in range(16, 22)]
    restarted = state.observe(after[0], after[1:], fixture=ready(new), now=old_absent["ended_at"],
                              replacement={"old_uid": old["metadata"]["uid"], "new_uid": new["metadata"]["uid"],
                                           "old_absent": True})
    business = [read(name) for name in ("business-01.json", "business-03.json", "business-07.json")]
    return {"kind": "DERIVED_OFFLINE_REPLAY_NOT_HISTORICAL_EVENTS", "source_run": "ZER-46/runtime-09",
            "api_accepted_time_kind": "UPPER_BOUND_FROM_API_READBACK_NOT_EXACT_RPC_ACK",
            "api_only": api_only, "action_completed": completed, "after_replacement": restarted,
            "boutique_business_healthy": all(b["healthy"] for b in business),
            "recovery_verified": False, "recovery_reason": "NO_FORMAL_CONTINUOUS_RECOVERY_PROBE_STREAM",
            "causal_attribution": "UNPROVEN", "new_lab_requests": 0, "hash_verified_inputs": sorted(read_paths)}


if __name__ == "__main__":
    print(json.dumps(replay(), ensure_ascii=False, indent=2))
