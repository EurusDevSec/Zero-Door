"""H-RT1 mutants: each breaks one invariant the harness must keep; the full offline suite must fail for each.

Runs on a temporary copy of the needed tree (the working tree is never edited). Also runs the unmodified
copy as a control (must pass) and the suite against the pre-package snapshot (fail-before: the harness and
the rt1 subcommand do not exist there). Offline: no cluster, Docker or model.

  python -B check_mutants.py --python <pinned interpreter> --out <new json>
"""
import argparse
import json
import shutil
import subprocess  # nosec B404 - fixed argv, no shell
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = "infrastructure/scripts/r1_baseline_runtime.py"
SUITE = "tests/test_dashboard_baseline_runtime.py"
COPY = ["agent-orchestrator", "infrastructure/scripts", "infrastructure/manifests", "tests", "docs/runbooks"]
MUTANTS = {
    "AUDIT_IGNORES_FAILED_TICKS": ('ok = bool(ticks) and all(x["ok"] for x in ticks) and', 'ok = bool(ticks) and'),
    "ZERO_DOOR_POD_NOT_ABORTED": ('raise Abort("ZERO_DOOR_COMPONENT_RUNNING")', 'pass'),
    "RESTORE_IGNORES_UID": ('elif dep["metadata"]["uid"] != base["uid"]:', 'elif False:'),
    "UID_SELFTEST_NOT_ENFORCED": ('raise Abort("UID_PRECONDITION_SELFTEST_FAILED", state)', 'pass'),
    "WRITES_NOT_GUARDED": ('if (phase, verb, kind, key_name) not in WRITES or not allowed_name:', 'if False:'),
    "WRITE_NAME_NOT_CHECKED": ('if (phase, verb, kind, key_name) not in WRITES or not allowed_name:', 'if (phase, verb, kind, key_name) not in WRITES:'),
    "CLEANUP_STEP_NOT_RETRIED": ('for attempt in (1, 2):', 'for attempt in (1,):'),
    "ABORT_SKIPS_EXPORT": ('("export", lambda: self.pulled or self.p5("ABORTED"))', '("export", lambda: True)'),
    "TOTAL_CAP_NOT_CHECKED_IN_TRIAL": ('''            if self.now() >= self.main_deadline:
                raise DeadlineExceeded("DEADLINE", name)
''', ''),
    "SCORES_WITHOUT_BOTH_EXPORTS": ('if not (self.pulled and {"export-H", "export-O"} <= set(exports)):', 'if not self.pulled:'),
    "PROBE_BUDGET_NOT_PLAN_CHECK": ('samples = int(math.floor(duration / f["delta_s"] + 1e-9))', 'samples = int(math.floor(duration / f["delta_s"] + 1e-9)) * 2'),
    "NO_EFFECT_WITHOUT_COVERAGE": ('status, t_eff = ("CONFIRMED_NO_EFFECT", None) if covered else ("UNKNOWN_EFFECT", None)',
                                   'status, t_eff = ("CONFIRMED_NO_EFFECT", None)'),
}


def tree(destination, source_root=ROOT):
    for name in COPY:
        shutil.copytree(source_root / name, destination / name, ignore=shutil.ignore_patterns("__pycache__"))


def suite(python, where):
    done = subprocess.run([python, "-B", SUITE], cwd=where, capture_output=True, text=True, timeout=1800)  # nosec B603
    lines = (done.stdout + done.stderr).splitlines()
    tail = [l for l in lines if l.startswith(("Ran ", "OK", "FAILED"))]
    failed = sorted({l.split(" (")[0].split(": ", 1)[1] for l in lines if l.startswith(("FAIL: ", "ERROR: "))})
    return {"exit": done.returncode, "summary": " ".join(tail) or " | ".join(lines[-2:]), "failed_tests": failed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit("output exists")
    result = {"control": None, "fail_before": None, "mutants": {}}
    with tempfile.TemporaryDirectory(prefix="zd-rt1-mut-") as tmp:
        base = Path(tmp) / "base"
        tree(base)
        result["control"] = suite(args.python, base)
        # Fail-before: the snapshot's verify script and runbook, no harness module; the current suite.
        before = Path(tmp) / "before"
        tree(before)
        snap = ROOT / "scratch/zer11/claude-rt1/before"
        for name in ("infrastructure/scripts/verify-dashboard-baselines.py", "docs/runbooks/dashboard-and-baselines.md"):
            shutil.copy2(snap / name, before / name)
        (before / MODULE).unlink()
        result["fail_before"] = suite(args.python, before)
        for name, (old, new) in MUTANTS.items():
            work = Path(tmp) / name
            shutil.copytree(base, work)
            path = work / MODULE
            text = path.read_bytes().decode()
            if text.count(old) != 1:
                result["mutants"][name] = {"error": "pattern not found exactly once"}
                continue
            path.write_bytes(text.replace(old, new).encode())
            run = suite(args.python, work)
            result["mutants"][name] = dict(run, killed=run["exit"] != 0)
            shutil.rmtree(work)
    result["killed"] = sum(1 for m in result["mutants"].values() if m.get("killed"))
    result["total"] = len(MUTANTS)
    result["control_ok"] = result["control"]["exit"] == 0
    result["fail_before_fails"] = result["fail_before"]["exit"] != 0
    out.write_bytes((json.dumps(result, indent=1, sort_keys=True) + "\n").encode())
    print(json.dumps({k: result[k] for k in ("control_ok", "fail_before_fails", "killed", "total")}))
    return 0 if result["control_ok"] and result["fail_before_fails"] and result["killed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
