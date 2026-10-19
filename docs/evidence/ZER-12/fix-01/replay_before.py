"""Discriminating offline probes, never swap source in the working checkout.

Use a per-agent test environment. Go mode also needs pinned Go 1.21.13 in env.
All network/model/Kubernetes transports in the ASGI suite are fake.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def python_replay():
    with tempfile.TemporaryDirectory(prefix="zer12-before-", dir=ROOT / "scratch/zer12") as tmp:
        temp = Path(tmp)
        for component in ("nemesis", "hephaestus", "event_pipeline"):
            target = temp / "agent-orchestrator" / component
            target.mkdir(parents=True)
            for source in (ROOT / "agent-orchestrator" / component).glob("*.py"):
                old = HERE / "before" / (str(source.relative_to(ROOT)) + ".txt")
                shutil.copyfile(old if old.exists() else source, target / source.name)
        tests = temp / "tests"
        shutil.copytree(ROOT / "tests/fixtures/zer12", tests / "fixtures/zer12")
        for name in ("test_command_guard_integration.py", "test_command_modes.py"):
            shutil.copyfile(ROOT / "tests" / name, tests / name)
        # A child interpreter guarantees no current guard module leaks from sys.modules.
        code = '''import sys,unittest
sys.path.insert(0,sys.argv[1])
from test_command_guard_integration import EntrypointTests
names=["test_unavailable_producer_is_terminal_and_does_not_poison_admission",
       "test_benchmark_model_scenario_generation_is_blocked_in_all_groups",
       "test_bad_schema_target_and_id_no_effects",
       "test_native_model_key_is_not_in_url_or_response_log"]
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(EntrypointTests(n) for n in names))
assert not r.errors, "runtime/import errors do not count as detecting a bug"
assert {t._testMethodName for t,_ in r.failures}==set(names[:2]), "wrong baseline failures"
print("EXPECTED_BASELINE_FAILURES=2 CLEAN_CONTROLS=2")
'''
        subprocess.run([sys.executable, "-B", "-c", code, str(tests)], check=True, cwd=ROOT)


def manifest_replay():
    sys.path.insert(0, str(ROOT / "tests"))
    import yaml
    from check_guard_manifests import check
    from test_command_guard_ci import effective_guard_environment
    for agent in ("chaos-worker", "nemesis", "hephaestus"):
        name = agent + ".yaml" if agent == "chaos-worker" else agent + "-deployment.yaml"
        for validator in (check, lambda docs: effective_guard_environment(docs, agent)):
            docs = list(yaml.safe_load_all((HERE / "before/infrastructure/manifests" / (name + ".txt")).read_text()))
            try:
                validator(docs)
            except ValueError as error:
                print(agent, "baseline rejected", str(error))
            else:
                raise AssertionError("baseline manifest defect not detected")
        docs = list(yaml.safe_load_all((ROOT / "infrastructure/manifests" / name).read_text()))
        check(docs)
        effective_guard_environment(docs, agent)
        print(agent, "fixed valid control PASS")


def go_replay():
    with tempfile.TemporaryDirectory(prefix="zer12-go-before-", dir=ROOT / "scratch/zer12") as tmp:
        replace = {}
        for name in ("internal/guard/auth.go", "internal/guard/dispatch.go", "internal/guard/ledger.go", "internal/attack/executor.go"):
            replace[str(ROOT / "chaos-worker" / name)] = str(HERE / "before/chaos-worker" / (name + ".txt"))
        overlay = Path(tmp) / "overlay.json"
        overlay.write_text(json.dumps({"Replace": replace}))
        env = dict(os.environ, GOTOOLCHAIN="go1.21.13")
        result = subprocess.run(["go", "test", "-p", "1", "-count=1", "-json", "-overlay", str(overlay), "./internal/guard",
                                 "-run", "TestReview|TestPolicyCapsAndTargets"], cwd=ROOT / "chaos-worker", env=env,
                                capture_output=True, text=True)
        print(result.stdout, end="")
        print(result.stderr, file=sys.stderr, end="")
        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
        failed = {e.get("Test") for e in events if e["Action"] == "fail" and e.get("Test")}
        assert result.returncode == 1 and failed == {
            "TestReviewExactJSONTagsAtEveryBoundary", "TestReviewClockLeadBoundAndExpiry",
            "TestReviewExpiredRedeliveryKeepsOutcomeWithoutEffect", "TestReviewExpiredPendingIsStillUnknown"}
        assert any(e["Action"] == "pass" and e.get("Test") == "TestPolicyCapsAndTargets" for e in events)


if __name__ == "__main__":
    (ROOT / "scratch/zer12").mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("python", "manifest", "go"))
    mode = parser.parse_args().mode
    {"python": python_replay, "manifest": manifest_replay, "go": go_replay}[mode]()
