"""Mutants for the ZER-11/39 invariants that have no pre-change version (new adapter, routes, seam).

Each mutant re-creates one plausible defect by an exact source replacement in a temporary copy of
the tree and must make the named suite fail. A replacement that does not apply exactly once is an
error, never a silently "caught" mutant. The unmutated copy must pass first (control).

  python check_mutants.py --nemesis <python> --hephaestus <python> [--json out.json]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COPY = ["agent-orchestrator", "tests", "infrastructure/manifests"]
VIEW = "agent-orchestrator/nemesis/measurement_view.py"
NEMESIS = "agent-orchestrator/nemesis/main.py"
HEAL = "agent-orchestrator/hephaestus/main.py"
GUARD = "agent-orchestrator/hephaestus/command_guard.py"
DASH, MODES = ("test_dashboard_measurement", "nemesis"), ("test_dashboard_modes", "hephaestus")

MUTANTS = {
    "HASH_NOT_CHECKED": (VIEW, 'if hashlib.sha256(data).hexdigest() != entry["sha256"][name]:', "if False:", DASH,
                         "a tampered score.json would be served as the registered artifact"),
    "SYMLINK_FOLLOWED": (VIEW, "if stat.S_ISLNK(info.st_mode):", "if False:", DASH,
                         "a run directory replaced by a symlink would be read through"),
    "EXPORT_NOT_COMPARED": (VIEW, 'if not incidents or incidents[0] != INCIDENT_COLUMNS or incidents[1:] != expected:',
                            "if not incidents:", DASH, "the page could show values that differ from incidents.csv"),
    "RUN_NOT_MATCHED": (VIEW, 'if type(run) is not dict or run.get("run_id") != entry["run_id"] or document["inputs"].get("run_id") != entry["run_id"]:',
                        "if type(run) is not dict:", DASH, "a request for run A could show run B's artifact"),
    "GROUP_NOT_MATCHED": (VIEW, 'if run.get("group") != entry["group"]:', "if False:", DASH,
                          "the registry could relabel the mode of a scored run"),
    "NONFINITE_ACCEPTED": (VIEW, "parse_float=finite, ", "", DASH, "1e999 would be shown as Infinity instead of refused"),
    "DUPLICATE_KEYS_ACCEPTED": (VIEW, "object_pairs_hook=pairs, ", "", DASH, "a duplicate KPI key would silently pick one value"),
    "OPEN_RUN_SERVED": (VIEW, 'entry["status"] != "CLOSED" or', "", DASH, "a run still in progress could be registered and read"),
    "DATA_TIME_FROM_GENERATED_AT": (VIEW, '"data_time": data_time(run),',
                                    '"data_time": {"status": "OK", "latest_ms": 0, "source": document.get("generated_at")},', DASH,
                                    "the update delay would be measured from the scorer's write time"),
    "VIEW_DROPS_BOUNDS": (VIEW, '"kpi": metrics["kpi"],',
                          '"kpi": {k: ({x: y for x, y in v.items() if x != "bounds"} if isinstance(v, dict) else v) for k, v in metrics["kpi"].items()},',
                          DASH, "the API would no longer pass KPI values (missing-data bounds) through unchanged"),
    "OPERATOR_KEY_READS_RESULTS": (NEMESIS, 'authorize_reader(request.headers.get("Authorization"))',
                                   'CommandGuard.from_env().authorize(request.headers.get("Authorization"))', DASH,
                                   "the BM operator's key would open S results"),
    "RESULTS_ACCEPT_WRITES": (NEMESIS, 'if request.method != "GET":\n            return JSONResponse({"detail": "READ_ONLY"}',
                              'if False:\n            return JSONResponse({"detail": "READ_ONLY"}', DASH,
                              "a non-GET request to the results API would reach the operator/command path"),
    "KEY_SEPARATION_REMOVED": (VIEW, 'raise Refused("KEY_SEPARATION", 503)', "pass", DASH,
                               "one shared secret would act as both operator and results reader"),
    "STATUS_DEFAULTS_ZERO": (NEMESIS, 'services_status = {name: {"replicas": None, "cpu": None} for name in DASHBOARD_SERVICES}',
                             'services_status = {name: {"replicas": 0, "cpu": 0.0} for name in DASHBOARD_SERVICES}', DASH,
                             "a Prometheus outage would look like 0 replicas / 0 CPU"),
    "HEAL_REPLAY_EXECUTES": (HEAL, "                if previous is not None:\n                    return previous\n", "", MODES,
                             "a replayed operator trigger would run a second action"),
    "CONSUMER_NOT_AUDITED": (GUARD, "        self.skipped = context[\"group\"]\n", "", MODES,
                             "a group that never auto-decides would leave no operational audit"),
    "BM_EXECUTES_RULES_DECISION": (HEAL, 'if context["group"] != "BM":\n            raise Refused("MANUAL_GROUP_REQUIRED", 409)',
                                   'if context["group"] not in {"BM", "B1"}:\n            raise Refused("MANUAL_GROUP_REQUIRED", 409)', MODES,
                                   "the manual trigger would execute an automatic RULES decision"),
}


def tree(dest):
    for part in COPY:
        shutil.copytree(ROOT / part, dest / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def suite(dest, module, python):
    done = subprocess.run([python, "-B", "-m", "unittest", module], cwd=dest / "tests", capture_output=True, text=True, timeout=900)
    tail = [line for line in done.stderr.splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    return done.returncode, " ".join(tail)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nemesis", required=True)
    parser.add_argument("--hephaestus", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    # Absolute: the suites run with the temporary tree as working directory.
    pythons = {"nemesis": str(Path(args.nemesis).resolve()), "hephaestus": str(Path(args.hephaestus).resolve())}
    rows, ok = {}, True
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        tree(clean)
        for module, role in (DASH, MODES):
            code, summary = suite(clean, module, pythons[role])
            rows["CONTROL:" + module] = {"exit": code, "summary": summary, "pass": code == 0}
            ok &= code == 0
            print("CONTROL", module, summary, flush=True)
        for name, (path, old, new, (module, role), meaning) in MUTANTS.items():
            dest = Path(tmp) / name
            tree(dest)
            source = (dest / path).read_text(encoding="utf-8")
            if source.count(old) != 1:
                raise SystemExit(f"{name}: replacement applies {source.count(old)} times")
            (dest / path).write_text(source.replace(old, new), encoding="utf-8")
            code, summary = suite(dest, module, pythons[role])
            rows[name] = {"file": path, "suite": module, "meaning": meaning, "exit": code, "summary": summary, "caught": code != 0}
            ok &= code != 0
            print("CAUGHT " if code else "SURVIVED", name, "|", summary, flush=True)
            shutil.rmtree(dest, ignore_errors=True)
    result = {"verdict": "PASS" if ok else "FAIL", "mutants": len(MUTANTS),
              "caught": sum(1 for k, r in rows.items() if not k.startswith("CONTROL") and r["caught"]), "rows": rows}
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=1, sort_keys=True)
    print("VERDICT", result["verdict"], f"{result['caught']}/{result['mutants']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
