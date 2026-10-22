"""Summarise N1 timing files: per run directory, exit codes, failing tests, and latency distributions of the
gateway's submit, the archive's append+fsync and the client's deliver (control events vs probe events), with
the client attempts that ended in Retry and their remaining budget. Usage: python n1_analyse.py <dir>..."""
import json
import sys
from pathlib import Path


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))] if values else None


def stats(values):
    return {"n": len(values), "p50": pct(values, 0.5), "p99": pct(values, 0.99), "max": max(values) if values else None,
            "over_1000ms": sum(1 for v in values if v > 1000), "over_2000ms": sum(1 for v in values if v > 2000)}


INJECTED = "Faults.test_control_ack_later_than_its_deadline_fails_closed"
out = {}
for d in map(Path, sys.argv[1:]):
    rows, summaries = [], []
    for f in sorted(d.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            r["file"] = f.stem
            if r.get("test") == INJECTED and r["kind"] != "summary":
                continue  # the negative control delays an ACK on purpose; it is not a host measurement
            rows.append(r)
    exits = (d / "exits.txt").read_text().split("\n") if (d / "exits.txt").exists() else []
    failing = [r for r in rows if r["kind"] == "summary" and (r["failures"] or r["errors"])]
    control = [r for r in rows if r["kind"] == "deliver" and r.get("type") != "PROBE_SAMPLE" and r.get("type") != "PROBE_HEARTBEAT"]
    probe = [r for r in rows if r["kind"] == "deliver" and r.get("type") in ("PROBE_SAMPLE", "PROBE_HEARTBEAT")]
    retries = [r for r in rows if r["kind"] == "deliver" and str(r.get("outcome", "")).startswith("Retry")]
    out[str(d)] = {
        "runs": sum(1 for r in rows if r["kind"] == "summary"), "exits": [e for e in exits if e],
        "failing_runs": [{"file": r["file"], "failures": r["failures"], "errors": r["errors"]} for r in failing],
        "submit_ms": stats([r["ms"] for r in rows if r["kind"] == "submit"]),
        "append_fsync_ms": stats([r["ms"] for r in rows if r["kind"] == "append"]),
        "deliver_control_ms": stats([r["ms"] for r in control]),
        "deliver_probe_ms": stats([r["ms"] for r in probe]),
        "retries": [{k: r.get(k) for k in ("file", "test", "type", "outcome", "ms", "budget_ms")} for r in retries][:40],
        "slowest_control": sorted(({k: r.get(k) for k in ("file", "test", "type", "ms", "budget_ms", "outcome")} for r in control),
                                  key=lambda r: -r["ms"])[:8],
        "slowest_append": sorted(({k: r.get(k) for k in ("file", "test", "ms")} for r in rows if r["kind"] == "append"),
                                 key=lambda r: -r["ms"])[:8],
    }
print(json.dumps(out, indent=1))
