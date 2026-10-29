"""Read-only S-plane result adapter for the Nemesis dashboard (ZER-11, ZER-39).

The dashboard shows scorer artifacts (measurement.output: score.json, incidents.csv, usage.csv) of
runs that were explicitly registered after the run closed, in <ZD_RESULTS_ROOT>/registry.json. It
never scores, never scans the root for datasets, never writes and never takes a filesystem path
from a request: a request names a run_id, the registry names the directory, and every file is
checked against the registered SHA-256 before it is parsed or served. KPI values are passed through
from score.json unchanged, so the API, the page and the downloaded export are the same measurement.

Results are S data (labels, ground truth). They are readable only with the separate results-reader
key, never with the operator key, so a BM operator cannot open them while a run is in progress.
"""
import hashlib
import hmac
import io
import csv
import json
import math
import os
import re
import stat
from pathlib import Path

from nemesis.command_guard import Refused, read_key

SCORE_SCHEMA = "zd-measurement-score/1"
REGISTRY_FORMAT = "zd-results-registry/1"
VIEW_FORMAT = "zd-results-view/1"
FILES = ("score.json", "incidents.csv", "usage.csv")
MAX_BYTES = 16 * 1024 * 1024
RUN_ID = re.compile(r"run_[0-9a-f]{32}")
DIR_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SHA256 = re.compile(r"[0-9a-f]{64}")
STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)")
# Contract 7.4 groups and the dashboard's mode names: MANUAL is BM, RULES is B1, AI is B2. B3 is a
# separate single-agent AI group and B0 the Kubernetes-only baseline; neither is shown as B2.
MODES = {"B0": "K8S_BASELINE", "BM": "MANUAL", "B1": "RULES", "B2": "AI", "B3": "AI_SINGLE"}
# measurement.output column order; tests/test_dashboard_measurement.py checks it never drifts.
INCIDENT_COLUMNS = ["run_id", "group", "trial_id", "incident_id", "flow", "effect", "label", "mttd_s", "mttr_s",
                    "total_s", "reaction_s", "u_mttd_ms", "u_mttr_ms", "u_total_ms", "u_reaction_ms", "relapses",
                    "action_attempts", "evaluator_mismatch", "flags", "missing_reasons"]
USAGE_COLUMNS = ["level", "key", "calls", "retries", "input_tokens", "output_tokens", "usage_status", "usd", "cost_status", "price_refs"]
# KPI entries the results page reads as objects (present for every scored run, EMPTY included).
KPI_OBJECTS = ("mttd", "mttr_120", "mttr_180", "reaction", "counts", "labels", "recovered_rate")


class ResultError(Exception):
    def __init__(self, reason, status):
        super().__init__(reason)
        self.reason, self.status = reason, status


def authorize_reader(authorization):
    """The results-reader key is its own file and must differ from the operator key (no shared role)."""
    key = read_key(os.environ.get("ZD_RESULTS_TOKEN_FILE", ""), "results-reader")
    operator_file = os.environ.get("ZD_OPERATOR_TOKEN_FILE")
    if operator_file and Path(operator_file).is_file():
        try:
            operator = read_key(operator_file, "operator")
        except Refused:
            operator = None
        if operator is not None and hmac.compare_digest(operator["secret"].encode(), key["secret"].encode()):
            raise Refused("KEY_SEPARATION", 503)
    if not isinstance(authorization, str) or not hmac.compare_digest(authorization.encode(), ("Bearer " + key["secret"]).encode()):
        raise Refused("UNAUTHORIZED", 401)
    return key["id"]


def strict_json(raw, reason):
    """JSON without duplicate keys, NaN/Infinity or overflowing numbers."""
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ResultError(reason, 422)
            out[key] = value
        return out

    def finite(text):
        value = float(text)
        if not math.isfinite(value):
            raise ResultError(reason, 422)
        return value

    def constant(_):
        raise ResultError(reason, 422)
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_float=finite, parse_constant=constant)
    except (UnicodeError, ValueError, RecursionError):
        raise ResultError(reason, 422) from None


def cell(value):
    """measurement.output.cell: the CSV text of one value."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        return "|".join(str(v) for v in value)
    return str(value)


def incident_rows(run):
    for r in run["incidents"]:
        u = r.get("uncertainty_ms", {})
        yield [run["run_id"], run["group"], r["trial_id"], r["incident_id"], r["flow"], r["effect"], r["label"],
               r.get("mttd"), r.get("mttr"), r.get("total"), r.get("reaction"), u.get("mttd"), u.get("mttr"),
               u.get("total"), u.get("reaction"), r.get("relapses"), r.get("action_attempts"),
               r.get("evaluator_mismatch"), sorted(r["flags"]), sorted(r["missing_reasons"])]


def usage_rows(usage):
    for level, groups in sorted((usage.get("by") or {}).items()):
        for key, g in sorted(groups.items()):
            yield [level, key, g["calls"], g["retries"], g["input_tokens"], g["output_tokens"], g["usage_status"],
                   g["usd"], g["cost_status"], g["price_refs"]]


def csv_rows(raw):
    try:
        return list(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))
    except (UnicodeError, csv.Error):
        raise ResultError("EXPORT_MALFORMED", 422) from None


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


class ResultsStore:
    def __init__(self, root):
        root = Path(root)
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ResultError("RESULTS_ROOT_INVALID", 503)
        self.root = root.resolve()

    @classmethod
    def from_env(cls):
        root = os.environ.get("ZD_RESULTS_ROOT")
        if not root:
            raise ResultError("RESULTS_NOT_CONFIGURED", 503)
        return cls(root)

    def read(self, *parts):
        """Bytes of a regular file under the root, never through a symlink or outside the root."""
        path = self.root
        for part in parts:
            path = path / part
            try:
                info = os.lstat(path)
            except OSError:
                raise ResultError("ARTIFACT_MISSING", 404) from None
            if stat.S_ISLNK(info.st_mode):
                raise ResultError("ARTIFACT_SYMLINK", 422)
        if not stat.S_ISREG(info.st_mode):
            raise ResultError("ARTIFACT_MISSING", 404)
        if info.st_size > MAX_BYTES:
            raise ResultError("ARTIFACT_TOO_LARGE", 422)
        resolved = path.resolve()
        if resolved.parent != self.root and self.root not in resolved.parents:
            raise ResultError("ARTIFACT_OUTSIDE_ROOT", 422)
        try:
            with open(resolved, "rb") as handle:
                data = handle.read(MAX_BYTES + 1)
        except OSError:
            raise ResultError("ARTIFACT_UNREADABLE", 503) from None
        if len(data) > MAX_BYTES:
            raise ResultError("ARTIFACT_TOO_LARGE", 422)
        return data

    def registry(self):
        try:
            value = strict_json(self.read("registry.json"), "REGISTRY_INVALID")
        except ResultError as error:
            raise ResultError("REGISTRY_MISSING" if error.status == 404 else "REGISTRY_INVALID", 503) from None
        if type(value) is not dict or set(value) != {"format", "runs"} or value["format"] != REGISTRY_FORMAT or type(value["runs"]) is not list:
            raise ResultError("REGISTRY_INVALID", 503)
        runs, dirs = {}, set()
        for entry in value["runs"]:
            if type(entry) is not dict or set(entry) != {"run_id", "dir", "group", "status", "registered_at", "sha256"}:
                raise ResultError("REGISTRY_INVALID", 503)
            if type(entry["run_id"]) is not str or not RUN_ID.fullmatch(entry["run_id"]) or entry["run_id"] in runs or \
                    type(entry["dir"]) is not str or not DIR_NAME.fullmatch(entry["dir"]) or entry["dir"] in dirs or \
                    entry["group"] not in MODES or entry["status"] != "CLOSED" or \
                    type(entry["registered_at"]) is not str or not STAMP.fullmatch(entry["registered_at"]) or \
                    type(entry["sha256"]) is not dict or set(entry["sha256"]) != set(FILES) or \
                    not all(type(v) is str and SHA256.fullmatch(v) for v in entry["sha256"].values()):
                raise ResultError("REGISTRY_INVALID", 503)
            runs[entry["run_id"]] = entry
            dirs.add(entry["dir"])
        return runs

    def runs(self):
        return [{"run_id": e["run_id"], "group": e["group"], "mode": MODES[e["group"]], "registered_at": e["registered_at"],
                 "score_sha256": e["sha256"]["score.json"]} for e in self.registry().values()]

    def artifact(self, run_id):
        """(entry, {name: bytes}, document) after hash, schema and export-consistency checks."""
        if type(run_id) is not str or not RUN_ID.fullmatch(run_id):
            raise ResultError("RUN_ID_INVALID", 400)
        entry = self.registry().get(run_id)
        if entry is None:
            raise ResultError("RUN_NOT_REGISTERED", 404)
        files = {name: self.read(entry["dir"], name) for name in FILES}
        for name, data in files.items():
            if hashlib.sha256(data).hexdigest() != entry["sha256"][name]:
                raise ResultError("ARTIFACT_HASH_MISMATCH", 422)
        document = strict_json(files["score.json"], "ARTIFACT_MALFORMED")
        check_document(document, entry)
        run = document["runs"][0]
        incidents = csv_rows(files["incidents.csv"])
        expected = [[cell(v) for v in row] for row in incident_rows(run)]
        if not incidents or incidents[0] != INCIDENT_COLUMNS or incidents[1:] != expected:
            raise ResultError("EXPORT_INCONSISTENT", 422)
        usage = csv_rows(files["usage.csv"])
        expected = [[cell(v) for v in row] for row in usage_rows(run["metrics"]["M11_usage"])]
        if not usage or usage[0] != USAGE_COLUMNS or usage[1:] != expected:
            raise ResultError("EXPORT_INCONSISTENT", 422)
        return entry, files, document

    def file(self, run_id, name):
        if name not in FILES:
            raise ResultError("FILE_NOT_EXPORTED", 404)
        entry, files, _ = self.artifact(run_id)
        return files[name], entry["sha256"][name]

    def view(self, run_id):
        entry, _, document = self.artifact(run_id)
        return build_view(entry, document)


def check_document(document, entry):
    if type(document) is not dict or document.get("schema") != SCORE_SCHEMA:
        raise ResultError("SCHEMA_UNSUPPORTED", 422)
    if type(document.get("scorer_version")) is not str or type(document.get("runs")) is not list or len(document["runs"]) != 1 \
            or type(document.get("inputs")) is not dict or type(document.get("options")) is not dict:
        raise ResultError("ARTIFACT_MALFORMED", 422)
    run = document["runs"][0]
    if type(run) is not dict or run.get("run_id") != entry["run_id"] or document["inputs"].get("run_id") != entry["run_id"]:
        raise ResultError("RUN_MISMATCH", 422)
    if run.get("group") != entry["group"]:
        raise ResultError("GROUP_MISMATCH", 422)
    # The view names the H and O exports the score came from; a score without them has no provenance.
    if not all(type(document["inputs"].get(k)) is str and SHA256.fullmatch(document["inputs"][k])
               for k in ("h_export_json_sha256", "o_export_json_sha256")):
        raise ResultError("INPUT_DIGEST_MISSING", 422)
    metrics = run.get("metrics")
    if type(metrics) is not dict or type(metrics.get("kpi")) is not dict or type(run.get("incidents")) is not list \
            or type(metrics.get("M11_usage")) is not dict or type(run.get("findings")) is not dict:
        raise ResultError("ARTIFACT_MALFORMED", 422)
    # Only the fields that build_view, data_time, the CSV rows and the page consume; the values inside
    # them are passed through as scored.
    kpi, findings, leak, uptime = metrics["kpi"], run["findings"], run.get("leak"), metrics.get("uptime")
    shape = [type(kpi.get(k)) is dict for k in KPI_OBJECTS] + [optional(kpi.get(k), dict) for k in ("failure_rate", "unknown_rate")]
    shape += [optional(findings.get(k), list) for k in ("mode_violations", "quarantined_mode_violations")]
    shape += [optional(run.get("run_flags"), list), optional(run.get("mode_findings"), dict), optional(leak, dict),
              optional(metrics.get("decisions"), dict), optional(uptime, dict)]
    if type(leak) is dict:
        shape += [optional(v.get("findings"), list) and optional(v.get("unknown"), list) for v in leak.values() if type(v) is dict]
    if type(uptime) is dict:
        shape += [type(u) is dict for u in uptime.values()]
    for r in run["incidents"]:
        shape.append(type(r) is dict and type(r.get("flags")) is list and type(r.get("missing_reasons")) is list
                     and optional(r.get("milestones"), dict) and ("uncertainty_ms" not in r or type(r["uncertainty_ms"]) is dict))
    if not all(shape):
        raise ResultError("ARTIFACT_MALFORMED", 422)
    try:
        list(incident_rows(run))
        list(usage_rows(metrics["M11_usage"]))
    except (KeyError, TypeError, AttributeError):
        raise ResultError("ARTIFACT_MALFORMED", 422) from None


def optional(value, kind):
    return value is None or type(value) is kind


def data_time(run):
    """Latest event milestone that the scorer placed on the verified reference axis.

    generated_at is when the scorer wrote the artifact, not an event time; it is never used here.
    Unverified clocks are local readings of other clocks and cannot be compared with the viewer's
    clock, so they leave the data time UNKNOWN rather than guessed."""
    verified, unverified = [], 0
    for r in run["incidents"]:
        for name, m in (r.get("milestones") or {}).items():
            if type(m) is not dict or type(m.get("t_ms")) not in (int, float):
                continue
            if m.get("verified") is True:
                verified.append((m["t_ms"], name, m.get("clock_id")))
            else:
                unverified += 1
    if not verified:
        reason = "NO_VERIFIED_MILESTONE" if unverified else "NO_EVENT_MILESTONE"
        return {"status": "UNKNOWN", "reason": reason, "latest_ms": None, "unverified_milestones": unverified}
    latest = max(verified)
    return {"status": "OK", "latest_ms": int(latest[0]), "milestone": latest[1], "clock_id": latest[2],
            "unverified_milestones": unverified,
            "meaning": "latest scored event milestone (reference clock axis); update delay = display time - this"}


def build_view(entry, document):
    run = document["runs"][0]
    metrics = run["metrics"]
    findings = run["findings"]
    return {
        "format": VIEW_FORMAT,
        "run_id": run["run_id"],
        "group": run["group"],
        "mode": MODES[run["group"]],
        "provenance": {
            "schema": document["schema"], "scorer_version": document["scorer_version"],
            "sha256": dict(entry["sha256"]), "options_sha256": canonical_sha(document["options"]),
            "inputs": {k: document["inputs"].get(k) for k in ("run_id", "h_export_json_sha256", "o_export_json_sha256")},
            "registered_at": entry["registered_at"],
            "generated_at": document.get("generated_at"),
            "generated_at_meaning": "time the scorer wrote the artifact; not an event time",
        },
        "data_time": data_time(run),
        "kpi": metrics["kpi"],
        "uptime": metrics.get("uptime"),
        "decisions": metrics.get("decisions"),
        "funnel": metrics.get("M2_funnel"),
        "usage": metrics["M11_usage"],
        "containment": metrics.get("M12_containment"),
        "benign": metrics.get("M5_M6_benign"),
        "cpu_P179": metrics.get("cpu_P179"),
        "request_success_rate": metrics.get("request_success_rate"),
        "mode_violations": {"count": len(findings.get("mode_violations") or []) + len(findings.get("quarantined_mode_violations") or []),
                            "by_trial": run.get("mode_findings") or {}},
        "findings": {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in sorted(findings.items())},
        "leak": {t: {"result": v.get("result"), "findings": len(v.get("findings") or []), "unknown": v.get("unknown") or []}
                 for t, v in sorted((run.get("leak") or {}).items()) if isinstance(v, dict)},
        "cohort": run.get("cohort"),
        "run_flags": run.get("run_flags") or [],
        "incident_columns": INCIDENT_COLUMNS,
        "incidents": [[cell(v) for v in row] for row in incident_rows(run)],
    }


def register(root, directory, now=None):
    """Offline, after the run closed: check an output/1 directory against measurement.output and add it.

    Needs the measurement package (scorer host, CI), not the Nemesis image. The CSVs must equal what
    measurement.output writes from this score.json byte for byte; the registry is rewritten atomically
    and an already registered run or directory is refused, never replaced."""
    from datetime import datetime, timezone
    from measurement.output import INCIDENT_COLUMNS as columns, USAGE_COLUMNS as usage_columns, csv_bytes
    from measurement.output import incident_rows as rows_of, usage_rows as usage_of
    store = ResultsStore(root)
    if not DIR_NAME.fullmatch(directory):
        raise ResultError("RUN_DIR_INVALID", 400)
    files = {name: store.read(directory, name) for name in FILES}
    document = strict_json(files["score.json"], "ARTIFACT_MALFORMED")
    if type(document) is not dict or type(document.get("runs")) is not list or len(document["runs"]) != 1 \
            or type(document["runs"][0]) is not dict:
        raise ResultError("ARTIFACT_MALFORMED", 422)
    run = document["runs"][0]
    entry = {"run_id": run.get("run_id"), "dir": directory, "group": run.get("group"), "status": "CLOSED",
             "registered_at": now or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
             "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    if type(entry["run_id"]) is not str or not RUN_ID.fullmatch(entry["run_id"]) or entry["group"] not in MODES:
        raise ResultError("ARTIFACT_MALFORMED", 422)
    # Shape first, so measurement.output below only ever rebuilds the CSVs of a well-formed score.
    check_document(document, entry)
    if files["incidents.csv"] != csv_bytes(columns, list(rows_of(run))) or \
            files["usage.csv"] != csv_bytes(usage_columns, list(usage_of(run["metrics"]["M11_usage"]))):
        raise ResultError("EXPORT_INCONSISTENT", 422)
    try:
        registry = {"format": REGISTRY_FORMAT, "runs": list(store.registry().values())}
    except ResultError as error:
        if error.reason != "REGISTRY_MISSING":
            raise
        registry = {"format": REGISTRY_FORMAT, "runs": []}
    if any(e["run_id"] == entry["run_id"] or e["dir"] == directory for e in registry["runs"]):
        raise ResultError("ALREADY_REGISTERED", 409)
    registry["runs"].append(entry)
    target = store.root / "registry.json"
    staging = store.root / ".registry.json.partial"
    with open(staging, "xb") as handle:
        handle.write((json.dumps(registry, indent=1, sort_keys=True) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(staging, target)
    store.registry()  # the written registry must parse under the reader's own rules
    return entry
