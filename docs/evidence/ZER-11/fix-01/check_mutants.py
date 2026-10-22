"""Invariant mutants for ZER-11/39 fix-01: each breaks one property the fix added; the named test must fail.

Each mutant is one exact string replacement in a temporary copy of the current tree (the replaced text
must occur exactly once). A clean control run of every named test must pass first. Offline.

  python check_mutants.py --nemesis <python> [--json out.json]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JS = "agent-orchestrator/nemesis/static/results.js"
MV = "agent-orchestrator/nemesis/measurement_view.py"
VF = "infrastructure/scripts/verify-dashboard-baselines.py"
PAGE = ("node", "tests/results_page_vm.cjs")
SHAPE = "test_dashboard_measurement.AdapterIntegrity.test_shape_of_consumed_fields_is_a_reason_code"
SERVER = "test_dashboard_measurement.ResultsServer"
PLAN = "test_dashboard_measurement.RuntimePlan"
# (name, invariant, file, old, new, check)
MUTANTS = [
    ("EVERY_ERROR_TRANSIENT", "only transport/upstream failures keep a STALE view", JS,
     "    if (error.transport === true) return true;\n    return [502, 503, 504]", "    return true;\n    return [502, 503, 504]", PAGE),
    ("CONFIG_503_TRANSIENT", "registry/key configuration 503s are fatal", JS,
     'new Set(["RESULTS_NOT_CONFIGURED", "RESULTS_ROOT_INVALID", "REGISTRY_MISSING", "REGISTRY_INVALID", "KEY_SEPARATION"])', "new Set([])", PAGE),
    ("RECONNECT_KEEPS_OLD_VIEW", "a (re)connect clears the previous key's view before reading the registry", JS,
     '    const selected = S.selected;\n    endSession();\n', "    const selected = S.selected;\n", PAGE),
    ("REFUSED_KEY_KEEPS_POLLING", "a refused key ends the session and its refresh timer", JS,
     "        if (state === \"NO_ACCESS\") {\n            endSession();\n", "        if (state === \"NO_ACCESS\") {\n", PAGE),
    # attempt1 reordered `S.view = view` before render(); it survived because a render error is already
    # fatal through transient(), so that order is defensive only. The invariant itself: an error with no
    # HTTP answer is transient only when the fetch itself failed, not when rendering did.
    ("STATUSLESS_ERROR_TRANSIENT", "an error without an HTTP answer is transient only if the fetch failed", JS,
     "    if (error.transport === true) return true;", "    if (error.transport === true || error.status === undefined) return true;", PAGE),
    ("INPUT_DIGEST_OPTIONAL", "a score must name its H/O export digests", MV,
     'raise ResultError("INPUT_DIGEST_MISSING", 422)', "pass", SHAPE),
    ("CONSUMED_SHAPE_UNCHECKED", "consumed fields of the wrong type are a 422, not a 500", MV,
     "    if not all(shape):\n", "    if False:\n", SHAPE),
    ("RESULTS_MODE_OPEN", "serve-results answers only the results page and /api/results", VF,
     'return JSONResponse({"detail": "NOT_SERVED_IN_RESULTS_MODE"}, status_code=404)', "return await call_next(request)", SERVER),
    ("RESULTS_MODE_STARTS_CONSUMER", "serve-results starts no Kafka consumer", VF,
     "    nemesis.app.router.on_startup.clear()\n", "", SERVER),
    ("RESULTS_MODE_ROOT_FROM_FIXTURE", "serve-results serves the given root, never a generated one", VF,
     "    runs = ResultsStore(root).runs()  # the registry must parse under the reader's own rules\n",
     "    root = Path(tempfile.mkdtemp()) / 'results'\n    root.mkdir()\n    runs = [{'run_id': r} for r in build_fixture_root(root, ['b1_recovered']).values()]\n", SERVER),
    ("PLAN_SAMPLE_CAP_IGNORED", "the per-trial probe budget is checked", VF,
     '        if samples > caps["probe_samples_per_trial"]:\n', "        if False:\n", PLAN),
    ("PLAN_WINDOW_SHORT_OF_CAP_REC", "a trial window covers cap_rec plus S so TIMEOUT stays scorable", VF,
     '        recovery_s = f["cap_rec_s"] + f["s_s"] + plan["stop_margin_s"]\n', '        recovery_s = 360 - plan["w_eff_s"] + f["s_s"]\n', PLAN),
]


def run(dest, python, check):
    if check == PAGE:
        argv = list(PAGE)
        cwd = dest
    else:
        argv = [python, "-B", "-m", "unittest", check]
        cwd = dest / "tests"
    done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=900)
    tail = [line for line in (done.stdout + done.stderr).splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    return done.returncode, " ".join(tail)


def copy(dest):
    for part in ("agent-orchestrator", "tests", "infrastructure/scripts", "infrastructure/manifests", "docs/runbooks"):
        shutil.copytree(ROOT / part, dest / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nemesis", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    python = str(Path(args.nemesis).resolve())
    rows, ok = [], True
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        copy(clean)
        controls = {}
        for check in sorted({m[5] for m in MUTANTS}, key=str):
            controls[str(check)] = run(clean, python, check)
            ok &= controls[str(check)][0] == 0
            print("CONTROL", "pass" if controls[str(check)][0] == 0 else "FAIL", check, flush=True)
        for name, invariant, path, old, new, check in MUTANTS:
            dest = Path(tmp) / name
            copy(dest)
            text = (dest / path).read_bytes().decode()
            if text.count(old) != 1:
                raise SystemExit(f"{name}: anchor occurs {text.count(old)} times")
            (dest / path).write_bytes(text.replace(old, new).encode())
            code, tail = run(dest, python, check)
            killed = code != 0
            ok &= killed
            rows.append({"mutant": name, "invariant": invariant, "file": path, "check": " ".join(check) if check == PAGE else check,
                         "killed": killed, "summary": tail})
            print("KILLED  " if killed else "SURVIVED", name, "|", tail, flush=True)
            shutil.rmtree(dest)
    summary = {"verdict": "PASS" if ok else "FAIL", "killed": sum(r["killed"] for r in rows), "total": len(rows),
               "controls": {k: v[0] == 0 for k, v in controls.items()}, "mutants": rows}
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=1, sort_keys=True)
    print("VERDICT", summary["verdict"], f"{summary['killed']}/{summary['total']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
