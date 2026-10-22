"""rt1-fix-01 focused regressions: run the tests written for RT1-01..05 and N1 against one tree and record, per
test, the outcome and its first failure line (JSON), so fail-before and expected-fixed are compared, not just
exit codes.

    python -B focused.py <tree> <mode> <out.json>

<tree> is a checkout whose harness (infrastructure/scripts/r1_baseline_runtime.py) is the one under test and
whose suite (tests/test_dashboard_baseline_runtime.py) is the rt1-fix-01 one. <mode>:
  plain              the suite as it is (the fake kubectl drops managedFields unless asked, like kubectl).
  before-compat      only for running the BEFORE harness: its DeleteOptions file (-f <path>) is handed to the
                     fake as the body it would read; nothing else changes.
  before-compat-mf   before-compat, and every `get` returns managedFields as the H-RT1 fake did, so RT1-01/03/04/05
                     are seen on their own instead of all stopping at RT1-02's P2 abort.
Offline: fake kubectl, loopback gateways; no cluster, Docker or model.
"""
import json
import sys
import unittest
from pathlib import Path

tree, mode, out = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
sys.path[:0] = [str(tree / "agent-orchestrator"), str(tree / "infrastructure/scripts"), str(tree / "tests")]
import test_dashboard_baseline_runtime as suite  # noqa: E402

TESTS = ["Findings", "Faults.test_control_ack_later_than_its_deadline_fails_closed",
         "Controller.test_controller_and_hpa_recovery_end_to_end_then_score_register_and_serve",
         "Controller.test_hpa_not_activated_is_said_so_and_no_effect_leaves_n"]

if mode.startswith("before-compat"):
    original = suite.FakeCluster.__call__

    def call(self, argv, stdin=None, timeout=None):
        argv = list(argv)
        if argv[4:6] == ["delete", "--raw"] and argv[7] == "-f" and argv[8] != "-":
            stdin, argv[8] = Path(argv[8]).read_bytes(), "-"  # kubectl reads that file as the request body
        if mode == "before-compat-mf" and argv[4] == "get" and "--show-managed-fields=true" not in argv:
            argv.append("--show-managed-fields=true")
        return original(self, argv, stdin, timeout)
    suite.FakeCluster.__call__ = call
elif mode != "plain":
    raise SystemExit("mode: plain | before-compat | before-compat-mf")


class Result(unittest.TextTestResult):
    rows = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.rows[test.id().split(".", 1)[1]] = {"outcome": "ok"}

    def record(self, test, kind, err):
        text = self._exc_info_to_string(err, test).strip().splitlines()
        last = next((line for line in reversed(text) if line.strip()), "")
        key = test.id().split(".", 1)[1] if hasattr(test, "id") else str(test)
        self.rows[key] = {"outcome": kind, "message": last[:300]}

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "FAIL", err)

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "ERROR", err)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.record(subtest, "FAIL" if issubclass(err[0], test.failureException) else "ERROR", err)


tests = unittest.TestLoader().loadTestsFromNames(TESTS, suite)
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(tests)
out.write_text(json.dumps({"tree_harness": str(tree / "infrastructure/scripts/r1_baseline_runtime.py"), "mode": mode,
                           "tests_run": result.testsRun, "results": dict(sorted(Result.rows.items()))}, indent=1) + "\n")
sys.exit(0 if result.wasSuccessful() else 1)
