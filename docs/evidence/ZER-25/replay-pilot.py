"""Verify the R5 dataset manifest and replay its sealed descriptive pilot."""
import argparse
import csv
import hashlib
import io
import json
import runpy
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked(root, pin):
    path = (root / pin["path"]).resolve()
    require(path.is_relative_to(root) and path.is_file(), f"Missing/outside root: {pin['path']}")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == pin["sha256"], f"SHA-256 mismatch: {path}")
    return data


def load(root, pin):
    return json.loads(checked(root, pin))


def verify(manifest_sha256, evidence_root):
    manifest = load(HERE, {"path": "dataset-manifest.json", "sha256": manifest_sha256})
    require(manifest["schema"] == "zer25-dataset/1", "Unsupported manifest")
    formal = manifest["formal"]
    checked(REPO, formal["protocol"])
    checked(REPO, formal["protocol_erratum"])
    require(formal["kind"] == "FORMAL_HOLD" and not formal["runs"], "Formal data outside R5 replay")
    legacy_rows = 0
    for pin in manifest["legacy"]["files"]:
        text = checked(REPO, pin).decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        require([row["run_id"] for row in rows] == pin["run_ids"], "Legacy run IDs drifted")
        require(all(row["attack_start"].startswith(manifest["legacy"]["date_from_attack_start"])
                    for row in rows), "Legacy timestamp date drifted")
        legacy_rows += len(rows)

    pilot = manifest["pilot"]
    batch = (evidence_root / pilot["batch"]).resolve()
    require(batch.is_relative_to(evidence_root), "Batch outside evidence root")
    seal = load(evidence_root, pilot["seal"])
    source = load(evidence_root, pilot["source_manifest"])
    prepared_source = load(evidence_root, pilot["prepared_source_manifest"])
    protocol = load(evidence_root, pilot["protocol"])
    reference = load(evidence_root, pilot["reference"])
    terminal = load(evidence_root, pilot["terminal"])
    idle = load(evidence_root, pilot["idle_55"])
    checked(evidence_root, pilot["adjudication_source"])
    require(terminal["shutdown"] == "OFFLINE" and terminal["runner_exit_code"] == 0,
            "Terminal did not confirm successful offline finish")
    require(seal["analysis_sha256"] == pilot["reference"]["sha256"]
            and seal["terminal_sha256"] == pilot["terminal"]["sha256"],
            "Terminal or analysis differs from the original seal")
    require(source["head"] == pilot["source_base"] and source["sha256"] == prepared_source["sha256"],
            "Retained source differs from preparation")
    require(seal["source_pins"] == len(source["sha256"]), "Source count differs from seal")
    for path, sha256 in source["sha256"].items():
        require(seal["raw_sha256"].get(f"source/{path}") == sha256, f"Unsealed source: {path}")
    for path, sha256 in seal["raw_sha256"].items():
        checked(batch, {"path": path, "sha256": sha256})

    batch_receipt = load(batch, {"path": "acceptance.json", "sha256": seal["raw_sha256"]["acceptance.json"]})
    require(batch_receipt["status"] == pilot["original_status"], "Original batch status differs")
    images = pilot["build_snapshot"]["recorded_images"]
    trials = pilot["trials"]
    require(pilot["build_snapshot"]["image_cache_receipts"] == len(trials), "Image receipt count differs")
    keys = ("index", "block", "group", "case")
    require([{key: trial[key] for key in keys} for trial in trials] == protocol["schedule"],
            "Trial list differs from the sealed schedule")
    require(protocol["version"] == pilot["method_version"], "Pilot method differs")
    run_ids = set()
    for trial in trials:
        expected_dir = f"trial-{trial['index'] + 1:02}"
        require(trial["trial"] == expected_dir, "Trial path differs from the scheduled slot")
        path = f"{expected_dir}/pilot-cell.json"
        receipt = load(batch, {"path": path, "sha256": seal["raw_sha256"][path]})
        require(receipt["cell"] == {key: trial[key] for key in keys}, "Pilot cell assignment differs")
        context = receipt["context"]
        require(all(context[key] == trial[key] for key in ("run_id", "trial_id", "config_ref"))
                and context["method_version"] == pilot["method_version"]
                and context["config_ref"] == f"sha256:{pilot['prepared_source_manifest']['sha256']}",
                "Pilot run identity or method drifted")
        require(context["run_id"] not in run_ids, "Duplicate run ID")
        run_ids.add(context["run_id"])
        cache_path = f"{expected_dir}/cache-admission.json"
        cache = load(batch, {"path": cache_path, "sha256": seal["raw_sha256"][cache_path]})
        require(cache["host_image_id"] == images["fixture_host_image_id"]
                and cache["fixture_node_image"]["id"] == images["fixture_node_image_id"]
                and cache["proxy_node_image"]["id"] == images["proxy_node_image_id"]
                and images["proxy_registry_digest"] in cache["proxy_node_image"]["repoDigests"],
                "Observed fixture or proxy image identity differs")
        worker_path = f"{expected_dir}/worker-cache-admission.json"
        worker = load(batch, {"path": worker_path, "sha256": seal["raw_sha256"][worker_path]})
        worker_pin = worker["provenance"]["artifact_pin"]
        require(worker_pin["host_id"] == images["worker_host_image_id"]
                and worker_pin["node_id"] == images["worker_node_image_id"],
                "Observed worker image identity differs")
        nemesis_pins = [pin for pin in worker["pins"] if pin["name"] == "zer42-nemesis"]
        require(len(nemesis_pins) == 1
                and nemesis_pins[0]["host_id"] == images["nemesis_host_image_id"]
                and nemesis_pins[0]["node_id"] == images["nemesis_node_image_id"],
                f"Observed Nemesis image identity differs: {expected_dir}")

    stopped = []
    for entry in pilot["excluded_batches"]:
        if "receipt" in entry:
            receipt = load(evidence_root, entry["receipt"])
            require(receipt["status"] == entry["status"] and receipt["error"] == entry["source_error"]
                    and not entry["rows"],
                    "Pre-claim status differs from receipt")
            stopped.append({"batch": entry["batch"], "status": entry["status"], "claimed": 0})
            continue
        receipt = load(evidence_root, entry["acceptance"])
        load(evidence_root, entry["protocol"])
        if "reconciliation" in entry:
            reconciliation = load(evidence_root, entry["reconciliation"])
            require(reconciliation["status"] == entry["reconciliation"]["expected_status"]
                    and reconciliation["all_trial_topics_absent"] is True
                    and reconciliation["original_cleanup_unchanged"] is True,
                    "Cleanup reconciliation differs from its receipt")
        fields = ("index", "group", "case", "status")
        raw_rows = [
            {**{key: row[key] for key in fields}, "work": (row.get("work") or {}).get("status"),
             "cleanup": (row.get("cleanup") or {}).get("verdict"),
             "work_error": (row.get("work") or {}).get("error"),
             "guard_failures": (row.get("work") or {}).get("guard_failures", [])}
            for row in receipt["rows"]
        ]
        require(receipt["status"] == entry["status"]
                and raw_rows == [{key: value for key, value in row.items() if key not in ("run_id", "run_id_source")}
                                 for row in entry["rows"]],
                "Excluded attempt differs from its original receipt")
        for row in entry["rows"]:
            pin = row["run_id_source"]
            if pin is None:
                require(row["run_id"] is None, "Excluded run ID has no source")
                continue
            origin = load(evidence_root, pin)
            require(origin.get("context", origin).get("run_id") == row["run_id"], "Excluded run ID differs")
        not_run = sum(row["status"] == "NOT_RUN" for row in raw_rows)
        stopped.append({"batch": entry["batch"], "status": entry["status"],
                        "planned": len(raw_rows), "not_run": not_run,
                        "observed_pending_review": sum(row["work"] == "OBSERVED_PENDING_REVIEW"
                                                       for row in raw_rows)})

    checked(HERE, pilot["analyzer"])
    analyzer = runpy.run_path(str(HERE / pilot["analyzer"]["path"]))
    result = analyzer["reconcile"](batch, protocol)
    require(result == reference and result["analysis_version"] == pilot["analyzer_version"],
            "Replayed statistics differ from the retained analysis")
    require([row["model_budget"]["run_id"] for row in result["rows"]]
            == [trial["run_id"] for trial in trials], "Analyzer returned a different cohort")
    return result, {
        "result": "PASS",
        "legacy_files": len(manifest["legacy"]["files"]),
        "legacy_rows": legacy_rows,
        "pilot_rows": len(trials),
        "pilot_original_status": pilot["original_status"],
        "pilot_adjudication": pilot["adjudication"],
        "image_cache_receipts": len(trials),
        "source_pins": len(source["sha256"]),
        "sealed_batch_files": len(seal["raw_sha256"]),
        "reproduced_reference_sha256": pilot["reference"]["sha256"],
        "stopped_attempts": stopped,
        "formal_runs": len(formal["runs"]),
        "formal_gate": formal["kind"],
        "resource_validation": {"5.5_GiB": idle["status"], "6_GiB": "RUNTIME07_PILOT"},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--analysis-output", type=Path)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 11):
        parser.exit(1, "Replay requires Python 3.11. On Windows, use py -3.11 -B.\n")
    try:
        result, summary = verify(args.manifest_sha256, args.evidence_root.resolve())
        if args.analysis_output is not None:
            with args.analysis_output.open("x", encoding="utf-8") as output:
                json.dump(result, output, indent=2, allow_nan=False)
                output.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Verification failed: {error}\n")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
