"""ZER-53 M12: join one containment claim to source, fixture UID, policy and probes.

Prepared method only. The formal scorer does not call this module, so M12 stays UNVERIFIED until
the H artifact format and the time conditions (window, clock bound, observation to end of S, TTL
or cleanup) are approved. Nothing here evaluates time.

A CONTAINMENT_VERIFIED event names four artifacts by "sha256:<digest>": the enforcement policy
(enforcement_point), the probe from the blocked source (blocked_source_ref), a benign fixture
probe from the pinned benign source (fixture_probe_ref) and a Boutique probe (boutique_probe_ref).
Each artifact is a JSON file named by the SHA-256 of its bytes, written by H during the trial.

  VERIFIED      every artifact is present, well typed, and every check joins
  NOT_VERIFIED  the evidence is complete and well typed, and at least one check fails
  UNVERIFIED    evidence is missing, unreadable or wrongly typed, so the outcome is unknown
  CONTROL       B0: the same-source probe is reported, never counted
"""
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile

from event_pipeline.contract import canonical, valid_id

from .clock import parse

REFS = {"policy": "enforcement_point", "blocked_source_probe": "blocked_source_ref",
        "benign_fixture_probe": "fixture_probe_ref", "boutique_probe": "boutique_probe_ref"}
EXPECTED = ("source", "fixture_uid", "policy_uid", "policy_scope", "benign_source", "boutique_flow")
COMMON = {"run_id", "trial_id", "kind", "clock_id", "observed_at"}
MAX_BYTES = 65536
DIGEST = re.compile(r"sha256:([0-9a-f]{64})")


def text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 256


def address(value):
    if not text(value):
        return False
    try:
        return str(ipaddress.ip_address(value)) == value
    except ValueError:
        return False


def integer(value):
    return type(value) is int


def http_status(value):
    return integer(value) and 100 <= value <= 599


def number(value):
    return type(value) in (int, float) and value == value and abs(value) != float("inf")


def rule(value):
    return (isinstance(value, dict) and text(value.get("action_id")) and address(value.get("client_ip"))
            and number(value.get("created_at")) and number(value.get("expires_at")))


# Every field of every artifact has one type check. A field that fails it is not evidence.
FIELDS = {
    "policy": {"policy_uid": text, "scope": text, "fixture_uid": text,
               "rules": lambda value: isinstance(value, list) and all(rule(item) for item in value)},
    "blocked_source_probe": {"source": address, "fixture_uid": text, "status": http_status,
                             "error": lambda value: value is None or text(value),
                             "action_ids": lambda value: isinstance(value, list) and all(text(i) for i in value)},
    "benign_fixture_probe": {"source": address, "fixture_uid": text, "status": http_status,
                             "restricted_rows": lambda value: integer(value) and value >= 0},
    "boutique_probe": {"flow": text, "ok": lambda value: type(value) is bool},
}


def artifact_problem(document, kind):
    if (kind not in FIELDS or not isinstance(document, dict)
            or set(document) != COMMON | set(FIELDS[kind]) or document["kind"] != kind):
        return "ARTIFACT_SCHEMA"
    if (not valid_id(document["run_id"], "run") or not valid_id(document["trial_id"], "trl")
            or not text(document["clock_id"])
            or any(not check(document[field]) for field, check in FIELDS[kind].items())):
        return "ARTIFACT_FIELD_TYPE"
    try:
        parse(document["observed_at"])
    except ValueError:
        return "ARTIFACT_FIELD_TYPE"
    return None


def write_artifact(directory, document, *, run_id, trial_id):
    """Store one validated H observation in the caller's private evidence directory."""
    kind = document.get("kind") if isinstance(document, dict) else None
    if not isinstance(kind, str) or artifact_problem(document, kind):
        raise ValueError("invalid containment artifact")
    if (document["run_id"], document["trial_id"]) != (run_id, trial_id):
        raise ValueError("containment artifact belongs to another trial")
    raw = canonical(document)
    if len(raw) > MAX_BYTES:
        raise ValueError("containment artifact is too large")
    digest = hashlib.sha256(raw).hexdigest()
    path = Path(directory) / (digest + ".json")
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("invalid containment artifact path")
    if path.exists():
        with path.open("rb") as stream:
            if stream.read(MAX_BYTES + 1) != raw:
                raise ValueError("containment artifact differs from its digest")
        return "sha256:" + digest

    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=".containment-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return "sha256:" + digest


def read_artifact(directory, ref, *, kind, run_id, trial_id):
    """Return (document, problem). The content comes from the bytes that match the digest."""
    match = DIGEST.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        return None, "REFERENCE_NOT_A_DIGEST"
    path = Path(directory) / (match.group(1) + ".json")
    try:
        if path.is_symlink() or not path.is_file():
            return None, "ARTIFACT_UNREADABLE" if path.is_symlink() else "ARTIFACT_MISSING"
        with path.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    except OSError:
        return None, "ARTIFACT_UNREADABLE"
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != match.group(1):
        return None, "ARTIFACT_DIGEST_MISMATCH"
    try:
        document = json.loads(raw)
    except (ValueError, RecursionError):
        return None, "ARTIFACT_UNREADABLE"
    problem = artifact_problem(document, kind)
    if problem:
        return None, problem
    if (document["run_id"], document["trial_id"]) != (run_id, trial_id):
        return None, "ARTIFACT_OTHER_TRIAL"
    return document, None


def join(expected, action_id, claim, directory, *, run_id, trial_id, group):
    """Join one claim.

    `expected` is the evaluator's pinned record for the trial: attacker source, fixture UID, TTL,
    policy UID and scope, benign probe source and Boutique flow. `action_id` is the archived O action.
    """
    claim = claim if isinstance(claim, dict) else {}
    documents = dict.fromkeys(REFS)
    missing = []
    kinds = ("blocked_source_probe", "boutique_probe") if group == "B0" else REFS
    for kind in kinds:
        field = REFS[kind]
        document, problem = read_artifact(directory, claim.get(field), kind=kind, run_id=run_id, trial_id=trial_id)
        documents[kind] = document
        if problem:
            missing.append(f"{kind}:{problem}")
    blocked = documents["blocked_source_probe"]
    probes = {kind: None if documents[kind] is None else
              {"status": documents[kind].get("status"), "ok": documents[kind].get("ok"),
               "source": documents[kind].get("source"), "flow": documents[kind].get("flow"),
               "observed_at": documents[kind]["observed_at"], "clock_id": documents[kind]["clock_id"]}
              for kind in ("blocked_source_probe", "benign_fixture_probe", "boutique_probe")}
    row = {"probes": probes, "missing": missing, "failed": [], "action_id": action_id}
    if group == "B0":
        # B0 has no containment policy. Only attribute probe results to the pinned control.
        expected = expected if isinstance(expected, dict) else {}
        same_source = blocked is not None and (
            blocked["source"], blocked["fixture_uid"]) == (expected.get("source"), expected.get("fixture_uid"))
        boutique = documents["boutique_probe"]
        same_flow = boutique is not None and boutique["flow"] == expected.get("boutique_flow")
        if blocked is not None and not same_source:
            missing.append("blocked_source_probe:CONTROL_SCOPE_MISMATCH")
        if boutique is not None and not same_flow:
            missing.append("boutique_probe:CONTROL_FLOW_MISMATCH")
        return dict(row, status="CONTROL", same_source_blocked=blocked["status"] == 403 if same_source else None,
                    boutique_ok=boutique["ok"] if same_flow else None)
    if (not isinstance(expected, dict) or not all(text(expected.get(key)) for key in EXPECTED)
            or not address(expected["source"]) or not address(expected["benign_source"])
            or expected["source"] == expected["benign_source"]
            or type(expected.get("ttl_s")) is not int or expected["ttl_s"] <= 0):
        missing.append("expected:EVALUATOR_FIELDS")
    if not text(action_id):
        missing.append("action:NO_ARCHIVED_ACTION")
    if missing:
        return dict(row, status="UNVERIFIED")

    policy, benign, boutique = (documents[kind] for kind in ("policy", "benign_fixture_probe", "boutique_probe"))
    failed = row["failed"]
    # A 403 counts only through the pinned policy and the rule written by the archived action.
    if (policy["policy_uid"], policy["scope"]) != (expected["policy_uid"], expected["policy_scope"]):
        failed.append("POLICY_IDENTITY")
    rules = [item for item in policy["rules"] if item["action_id"] == action_id]
    if len(rules) != 1 or policy["fixture_uid"] != expected["fixture_uid"]:
        failed.append("POLICY_NOT_JOINED")
    else:
        if rules[0]["client_ip"] != expected["source"]:
            failed.append("POLICY_SOURCE")
        if rules[0]["expires_at"] - rules[0]["created_at"] != expected["ttl_s"]:
            failed.append("POLICY_TTL")
    if (blocked["source"] != expected["source"] or blocked["fixture_uid"] != expected["fixture_uid"]
            or blocked["status"] != 403 or blocked["error"] != "SOURCE_BLOCKED"):
        failed.append("BLOCKED_SOURCE_PROBE")
    elif action_id not in blocked["action_ids"]:
        failed.append("BLOCK_WITHOUT_JOINED_ACTION")
    if (benign["source"] != expected["benign_source"] or benign["fixture_uid"] != expected["fixture_uid"]
            or benign["status"] != 200 or benign["restricted_rows"] != 0):
        failed.append("BENIGN_FIXTURE_PROBE")
    if boutique["flow"] != expected["boutique_flow"] or boutique["ok"] is not True:
        failed.append("BOUTIQUE_PROBE")
    return dict(row, status="NOT_VERIFIED" if failed else "VERIFIED")


def summarize(rows):
    """Bounds over the M12 cohort. CONTROL rows are listed by the caller, not counted here."""
    counted = [row for row in rows if row["status"] != "CONTROL"]
    n = len(counted)
    if not n:
        return {"status": "NO_ELIGIBLE", "N": 0}
    verified = sum(row["status"] == "VERIFIED" for row in counted)
    unknown = sum(row["status"] == "UNVERIFIED" for row in counted)
    return {"status": "OK" if not unknown else "UNVERIFIED", "N": n, "numerator": verified, "unknown": unknown,
            "bounds": [round(verified / n, 6), round((verified + unknown) / n, 6)]}
