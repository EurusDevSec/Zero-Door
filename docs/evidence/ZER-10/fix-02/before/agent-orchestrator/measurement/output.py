"""Scorer artifacts (S plane): versioned JSON plus stable CSV, written once into a NEW directory.

Output never overwrites anything: the destination must not exist and must not lie inside an input
export. Files are written to a private sibling then renamed, so a failure leaves no half result at
the destination. Nothing here talks to the O gateway or archive: S artifacts do not flow back to O.
"""
import csv
import io
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "zd-measurement-score/1"
INCIDENT_COLUMNS = ["run_id", "group", "trial_id", "incident_id", "flow", "effect", "label", "mttd_s", "mttr_s",
                    "total_s", "reaction_s", "u_mttd_ms", "u_mttr_ms", "u_total_ms", "u_reaction_ms", "relapses",
                    "action_attempts", "evaluator_mismatch", "flags", "missing_reasons"]
USAGE_COLUMNS = ["level", "key", "calls", "retries", "input_tokens", "output_tokens", "usage_status", "usd", "cost_status", "price_refs"]


class OutputError(ValueError):
    pass


def cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        return "|".join(str(v) for v in value)
    return str(value)


def incident_rows(scored):
    for r in scored["incidents"]:
        u = r.get("uncertainty_ms", {})
        yield [scored["run_id"], scored["group"], r["trial_id"], r["incident_id"], r["flow"], r["effect"], r["label"],
               r.get("mttd"), r.get("mttr"), r.get("total"), r.get("reaction"), u.get("mttd"), u.get("mttr"),
               u.get("total"), u.get("reaction"), r.get("relapses"), r.get("action_attempts"),
               r.get("evaluator_mismatch"), sorted(r["flags"]), sorted(r["missing_reasons"])]


def usage_rows(usage):
    for level, groups in sorted((usage.get("by") or {}).items()):
        for key, g in sorted(groups.items()):
            yield [level, key, g["calls"], g["retries"], g["input_tokens"], g["output_tokens"], g["usage_status"],
                   g["usd"], g["cost_status"], g["price_refs"]]


def csv_bytes(columns, rows):
    text = io.StringIO()
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([cell(v) for v in row])
    return text.getvalue().encode("utf-8")


def inside(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def write(destination, document, inputs):
    """Write score.json, incidents.csv, usage.csv once. `inputs` are the export directories."""
    out = Path(destination).resolve()
    if out.exists():
        raise OutputError("output already exists; choose a new directory")
    for source in inputs:
        if source and inside(out, Path(source).resolve()):
            raise OutputError("output must not be inside an input export")
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = out.parent / f".{out.name}.partial-{uuid.uuid4().hex}"
    staging.mkdir()
    document = dict(document, schema=SCHEMA, generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    files = {
        "score.json": (json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False, default=sorted) + "\n").encode("utf-8"),
        "incidents.csv": csv_bytes(INCIDENT_COLUMNS, [row for run in document["runs"] for row in incident_rows(run)]),
        "usage.csv": csv_bytes(USAGE_COLUMNS, [row for run in document["runs"] for row in usage_rows(run["metrics"]["M11_usage"])]),
    }
    for name, data in files.items():
        with open(staging / name, "xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    os.rename(staging, out)  # fails if the destination appeared meanwhile; nothing is overwritten
    return out
