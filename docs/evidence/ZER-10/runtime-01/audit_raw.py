"""Independent receipt audit: JSON/hash/timestamp arithmetic, no measurement scorer/helper."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
LIVE = HERE / "attempt-03" / "raw-final"
EXPORT = LIVE / "export-H"


def ms(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000


def audit():
    meta = json.loads((EXPORT / "export.json").read_text())
    hashes = {}
    for name, facts in meta["files"].items():
        path = EXPORT / name
        path.resolve().relative_to(EXPORT.resolve())
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == facts["sha256"], name
        assert len(data) == facts["bytes"], name
        hashes[name] = digest
    records = [json.loads(line) for line in (EXPORT / "H.jsonl").read_text().splitlines()]
    assert len(records) == meta["seal"]["lines"] == 66
    events = [record["envelope"] for record in records]
    assert len({e["event_id"] for e in events}) == len(events)
    assert all(e["plane"] == "H" and e["run_id"] == meta["run_id"] for e in events)
    expected_phases = {"boutique-healthy": True, "checkout-unavailable": False, "checkout-restored": True,
                       "frontend-unavailable": False, "frontend-restored": True,
                       "fixture-healthy": True, "fixture-locked": False, "fixture-restored": True}
    phases, sample_ids = {}, set()
    for name, passed in expected_phases.items():
        facts = json.loads((LIVE / (name + ".json")).read_text())
        trial = [e for e in events if e["trial_id"] == facts["trial_id"]]
        start = next(e for e in trial if e["event_type"] == "TRIAL_STARTED")
        end = next(e for e in trial if e["event_type"] == "TRIAL_ENDED")
        samples = sorted((e for e in trial if e["event_type"] == "PROBE_SAMPLE"), key=lambda e: e["payload"]["sequence"])
        assert len(samples) == 3
        assert [e["payload"]["sequence"] for e in samples] == [0, 1, 2]
        assert [e["event_id"] for e in samples] == facts["samples"]
        assert [e["payload"]["pass"] for e in samples] == [passed] * 3
        sample_ids.update(e["event_id"] for e in samples)
        for event in samples:
            p = event["payload"]
            assert ms(start["ts_event"]) <= ms(p["t_start"]) <= ms(p["t_end"]) <= ms(end["ts_event"])
            assert abs((ms(p["t_end"]) - ms(p["t_start"])) - p["latency_ms"]) <= 1.1
            assert event["clock"]["clock_id"] == start["payload"]["probes"][0]["clock_id"]
            assert (p["error_class"] is None) == passed
            if passed:
                assert p["latency_ms"] <= facts["plan"]["f01"]["l_ms"] == 2000
            assert all(step["status"] is not None for step in p["detail"]["steps"] if step["ok"])
        if name in ("checkout-unavailable", "fixture-locked"):
            assert facts["independent_home_status"] == 200
        periods = [(ms(b["payload"]["t_start"]) - ms(a["payload"]["t_start"])) / 1000 for a, b in zip(samples, samples[1:])]
        phases[name] = {"samples": 3, "pass": sum(e["payload"]["pass"] for e in samples),
                        "error_classes": [e["payload"]["error_class"] for e in samples],
                        "reasons": [e["payload"]["detail"]["reason"] for e in samples],
                        "latency_ms": [e["payload"]["latency_ms"] for e in samples],
                        "observed_start_period_s": periods, "configured_delta_s": 1,
                        "skipped_slots": facts["summary"]["skipped_slots"], "verdict": "PASS"}
    assert len(sample_ids) == 24
    receipt = json.loads((LIVE / "receipt.json").read_text())
    assert receipt["sqlite_rows_remaining"] == 0 and receipt["verdict"] == "PASS"
    assert receipt["transactions"] == {"checkout": 20, "fixture": 9}
    assert receipt["wall_s"] < 900
    before = json.loads((HERE / "attempt-03" / "deployments-before.json").read_text())
    after = json.loads((HERE / "attempt-03" / "deployments-after.json").read_text())
    initial = {d["metadata"]["name"]: d for d in before["items"]}
    final = {d["metadata"]["name"]: d for d in after["items"]}
    restored = {}
    for name in ("frontend", "checkoutservice"):
        a, b = initial[name], final[name]
        assert a["metadata"]["uid"] == b["metadata"]["uid"]
        assert a["spec"] == b["spec"], name
        assert b["status"]["availableReplicas"] == a["spec"]["replicas"]
        restored[name] = b["spec"]["replicas"]
    namespaces = json.loads((HERE / "namespaces-final.json").read_text())
    created = {re.search(r"namespace: (\S+)", (HERE / p).read_text()).group(1)
               for p in ("pod.yaml", "attempt-02/pod.yaml", "attempt-03/pod.yaml")}
    assert not created.intersection(n["metadata"]["name"] for n in namespaces["items"]), "temporary namespaces remain"
    return {"verdict": "PASS", "raw_records": len(records), "samples": len(sample_ids), "hashes": hashes,
            "phases": phases, "restored_replicas": restored, "sqlite_rows_remaining": 0,
            "temporary_namespaces_remaining": 0, "run_id": meta["run_id"],
            "scope": "AC-01 real service probe acceptance; no detector, LLM, formal KPI or ZER-41 SQLi claim"}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
