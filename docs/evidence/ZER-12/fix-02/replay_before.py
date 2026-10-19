"""Replay the two new regressions against exact fix-01 function snapshots."""
import ast
import importlib
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
import test_command_guard_ci as ci
import test_command_guard_integration as http

def old_function(relative, name, target):
    source = (Path(__file__).parent / "before" / (relative + ".txt")).read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
    fn.decorator_list = []
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "fix01-before:" + relative, "exec"), target)

old_function("tests/test_command_guard_ci.py", "effective_guard_environment", ci.__dict__)
manifest_result = unittest.TestResult()
ci.CIChecks("test_guard_wiring_mutants_and_sequential_rollout").run(manifest_result)
assert not manifest_result.errors, manifest_result.errors
assert len(manifest_result.failures) == 24, manifest_result.failures
assert all("ValueError not raised" in message for _, message in manifest_result.failures)
print("FIX01 manifest: 24/24 broken-wiring/rollout subcases missed as expected; 3 current valid controls pass")

class BeforeHTTP(http.EntrypointTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        old_function("agent-orchestrator/nemesis/main.py", "trigger_attack", self.nemesis.__dict__)
        # FastAPI has already captured the current callable; replace the route's dependent callable too.
        for route in self.nemesis.app.routes:
            if getattr(route, "path", None) == "/attack/trigger":
                route.dependant.call = self.nemesis.trigger_attack

result = unittest.TestResult()
BeforeHTTP("test_ledger_failure_after_send_reports_unknown_without_replay").run(result)
assert not result.errors, result.errors
assert len(result.failures) == 1, result.failures
assert "OUTCOME_UNKNOWN" in result.failures[0][1] and "LEDGER_UNAVAILABLE" in result.failures[0][1]
print("FIX01 HTTP: post-send ledger-error regression fails on response LEDGER_UNAVAILABLE as expected")
