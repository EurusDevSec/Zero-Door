"""Read-only repeatable verification of retained ZER-42 acceptance; no lab/network I/O."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())
HERE = Path(__file__).resolve().parent
OUT = HERE / "acceptance-final"
sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
import sqli_executor_runtime as runtime


def load(path):
    return json.loads(path.read_bytes())


def main():
    result = load(OUT / "acceptance.json")
    originals = load(OUT / "original-artifact-sha256.json")
    for name, digest in originals.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    assert result["original_bytes_unchanged"] and len(originals) == 160
    for name, digest in result["source_hashes_match"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    mapping = load(OUT / "id-mapping.json")
    assert mapping["raw_changed"] is False
    assert runtime.contract.valid_id(mapping["mapped_context"]["run_id"], "run")
    assert runtime.contract.valid_id(mapping["mapped_context"]["trial_id"], "trl")
    prior = HERE / result["attempt"]
    raw = {r["value"]["commandId"]: r["value"] for r in load(prior / "results-vulnerable.json")}
    assert len(raw) == len(result["cases"]) == 4
    for case in result["cases"]:
        cid = case["command_id"]
        bundle = load(OUT / (cid + "-bundle.json"))
        fault, effect = runtime.verify_pair(bundle["events"], runtime.oracle_restricted())
        assert fault["payload"]["raw_result"] == raw[cid]
        assert fault["run_id"] == mapping["mapped_context"]["run_id"]
        assert fault["trial_id"] == mapping["mapped_context"]["trial_id"]
        assert fault["incident_id"] == mapping["incidents"][cid]
        assert effect["payload"]["status"] == case["formal_effect"]
        assert runtime.recheck_export(OUT / (cid + "-export")) == load(OUT / (cid + "-receipt.json"))
    joins = load(OUT / "request-joins.json")
    assert len(joins["joins"]) == 12 and len(joins["controls"]) == 4
    assert joins["replay_extra_commands"] == joins["replay_extra_http_requests_in_retained_logs"] == 0
    cleanup = load(OUT / "cleanup-receipt.json")
    assert cleanup["status"] == "CLEAN" and cleanup["namespace_absent"] and cleanup["pvc_count"] == 3
    assert cleanup["snapshot"] == load(prior / "after.json")
    assert cleanup["snapshot"] == load(OUT / "cleanup-before.json")
    before_topics = set(load(OUT / "live-06-topic-list.json")["stdout"].splitlines())
    after_topics = set(load(OUT / "live-15-topic-list.json")["stdout"].splitlines())
    assert before_topics - set(cleanup["owned_topics_absent"]) == after_topics
    assert not after_topics.intersection(cleanup["owned_topics_absent"])
    print("RECHECK PASS: original160 unchanged; source7 match; bundles/exports4 valid; joins12; controls4; CLEAN receipt verified")


if __name__ == "__main__":
    main()
