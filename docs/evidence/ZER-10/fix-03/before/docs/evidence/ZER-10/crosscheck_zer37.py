"""Cross-check: ZER-37 contract cases (historical oracle, hand-computed expected) -> real Archive -> ZER-10 scorer.

Run from the repository root: python -B docs/evidence/ZER-10/crosscheck_zer37.py [NEW_RESULT_FILE]
Two documented harness adaptations: the oracle omits a null trial_id key (the locked transport carries it),
and names f01_params without units (the scorer reads delta_s, k, s_s, l_ms, gap_s, eps_s, cap_det_s, cap_rec_s).

The oracle module is only imported to BUILD the accepted SYNTHETIC envelopes; nothing of its scoring is
reused. Envelopes are ingested in ts_ingest order through event_pipeline.store.Archive, sealed and
exported, then scored by measurement.scorer. Each expected field is compared; differences are listed.
"""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]  # docs/evidence/ZER-10/<this> -> repo root
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "docs/evidence/ZER-37"))
# The oracle reads scratch/zer37/fixtures.json, as in the existing CI bootstrap. Use the committed sealed copy
# and refuse to run on anything else.
SEALED, WORK = ROOT / "docs/evidence/ZER-37/fixtures.json", ROOT / "scratch/zer37/fixtures.json"
if not WORK.exists():
    WORK.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SEALED, WORK)
if WORK.read_bytes() != SEALED.read_bytes():
    sys.exit("scratch/zer37/fixtures.json differs from the sealed docs/evidence/ZER-37/fixtures.json")
import check_contract as oracle  # noqa: E402
from event_pipeline.store import Archive, Rejected  # noqa: E402
from measurement.raw import load  # noqa: E402
from measurement.scorer import Scorer  # noqa: E402

FIELDS = ("effect", "label", "labels", "mttd", "mttr", "total", "reaction", "t_det", "t_rec", "evaluator_mismatch", "u_ms",
          "mode_violation", "flags")


def norm(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def main(out=None):
    rows, summary = [], {"cases": 0, "compared": 0, "agree": 0, "differ": 0}
    for case in oracle.FIX["cases"]:
        spec = copy.deepcopy(oracle.FIX["base"])
        spec.update(case["over"])
        records, _, meta = oracle.build(case["id"], spec)
        records = sorted(records, key=lambda r: r["ts_ingest"])
        runs = sorted({r["envelope"].get("run_id") for r in records if r["envelope"].get("run_id")})
        main_run = meta and records[0]["envelope"].get("run_id")
        with tempfile.TemporaryDirectory() as tmp:
            planes = {"H": Archive(Path(tmp) / "h", "H"), "O": Archive(Path(tmp) / "o", "O")}
            rejected = []
            try:
                for r in records:
                    e = copy.deepcopy(r["envelope"])
                    # The oracle omits a null trial_id key; the locked transport (5.1) carries it as null.
                    e.setdefault("trial_id", None)
                    if e.get("event_type") == "RUN_STARTED":
                        # f01_params key names are not locked by 5.3; the scorer uses unit-suffixed names.
                        f = e["payload"]["f01_params"]
                        e["payload"]["f01_params"] = {"delta_s": f["delta"], "k": f["k"], "s_s": f["s"], "l_ms": f["l_ms"],
                                                      "gap_s": f["gap"], "eps_s": f["eps"], "cap_det_s": f["cap_det"],
                                                      "cap_rec_s": f["cap_rec"]}
                    plane = e.get("plane") if e.get("plane") in planes else "O"
                    if plane == "S":
                        continue
                    try:
                        planes[plane].ingest(e, {"kind": "file"}, e.get("source_component"))
                    except Rejected as error:
                        rejected.append((e.get("event_type"), error.classification))
                run_id = next(e["envelope"]["run_id"] for e in records if e["envelope"]["event_type"] == "RUN_STARTED")
                for a in planes.values():
                    a.run_dir(run_id)
                planes["H"].export(run_id, Path(tmp) / "xh")
                planes["O"].export(run_id, Path(tmp) / "xo")
                foreign = []
                for other in runs:
                    if other != run_id:
                        for plane, a in planes.items():
                            target = Path(tmp) / f"x{plane}-{other}"
                            a.run_dir(other)
                            a.export(other, target)
                            foreign.append((target, plane))
            finally:
                for a in planes.values():
                    a.close()
            from measurement.raw import Export
            others = []
            for target, plane in foreign:
                others.append(Export(target, plane))
            scorer = Scorer(*load(Path(tmp) / "xh", Path(tmp) / "xo"), others=others)
            result = scorer.run()
        by_id = {r["incident_id"]: r for r in result["incidents"]}
        order = [by_id.get(i) for i in meta["incidents"]]
        mine = dict(order[0] or {}) if order else {}
        if mine:
            mine["t_det"] = None if mine["milestones"]["t_det"] is None else round(mine["milestones"]["t_det"]["t_ms"] / 1000 - oracle.T0.timestamp(), 3)
            mine["t_rec"] = None if mine["milestones"]["t_rec"] is None else round(mine["milestones"]["t_rec"]["t_ms"] / 1000 - oracle.T0.timestamp(), 3)
            mine["u_ms"] = mine.get("uncertainty_ms", {})
            mine["mode_violation"] = "MODE_VIOLATION" in mine["missing_reasons"]
            if mine["label"] == "CONFIRMED_NO_EFFECT":
                mine["label"] = "OUT_NO_EFFECT"
        mine["labels"] = [("OUT_NO_EFFECT" if o["label"] == "CONFIRMED_NO_EFFECT" else o["label"]) if o else None for o in order]
        summary["cases"] += 1
        for key, expected in case["expected"].items():
            if key not in FIELDS:
                continue
            got = mine.get(key)
            if key == "flags":
                # The oracle lists hard MISSING reasons among flags; the scorer keeps them in missing_reasons.
                same = set(expected) <= set(got or []) | set(mine.get("missing_reasons") or [])
            elif key == "u_ms":
                same = all(norm(got.get(k)) == v for k, v in expected.items()) if isinstance(got, dict) else False
            else:
                same = norm(got) == norm(expected)
            summary["compared"] += 1
            summary["agree" if same else "differ"] += 1
            if not same:
                rows.append({"case": case["id"], "field": key, "expected": expected, "scorer": got,
                             "runs_in_case": len(runs), "rejected": rejected,
                             "missing_reasons": (order[0] or {}).get("missing_reasons") if order else None})
    report = {"summary": summary, "differences": rows}
    text = json.dumps(report, indent=1, sort_keys=True, default=str)
    if out:
        with open(out, "x", encoding="utf-8") as handle:  # a new file; never overwrites a stored result
            handle.write(text + "\n")
    print(json.dumps(summary))
    for r in rows:
        print(r["case"], r["field"], "expected", r["expected"], "scorer", r["scorer"], r["missing_reasons"], r["rejected"][:3])
    return 0 if not rows else 1  # 0 only when every compared field agrees


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("result", nargs="?", help="NEW file for the JSON result (refused if it exists)")
    sys.exit(main(parser.parse_args().result))
