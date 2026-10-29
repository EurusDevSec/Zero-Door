"""ZER-20 parent acceptance: run existing offline suites, no new product cases."""
import datetime
import hashlib
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=False)
sys.path.insert(0, str(ROOT / "tests"))
MODULES = ["test_gaia_diagnosis", "test_hephaestus_recovery", "test_llm_adapter"]


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.observed.append({"test": test.id(), "result": "PASS"})

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.observed.append({"test": test.id(), "subtest": str(subtest),
                              "result": "PASS" if err is None else "FAIL"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.observed.append({"test": test.id(), "result": "FAIL"})

    def addError(self, test, err):
        super().addError(test, err)
        self.observed.append({"test": test.id(), "result": "ERROR"})


sources = []
for directory in ["gaia", "hephaestus", "event_pipeline"]:
    sources.extend((ROOT / "agent-orchestrator" / directory).rglob("*.py"))
sources += [ROOT / "agent-orchestrator/nemesis/command_guard.py"]
sources += [ROOT / "tests" / (name + ".py") for name in MODULES]
sources += [ROOT / "tests/test_sqli_action_state.py"]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(sources))}
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with (OUT / "tests.log").open("x", encoding="utf8") as log:
    suite = unittest.TestLoader().loadTestsFromNames(MODULES)
    with patch.object(socket.socket, "connect", side_effect=AssertionError("ZER20_OFFLINE_ONLY")):
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
assert before == {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(sources))}
receipt = {
    "issue": "ZER-20", "started_utc": started,
    "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "python": sys.executable, "version": sys.version,
    "tests_run": result.testsRun, "success": result.wasSuccessful(),
    "failures": len(result.failures), "errors": len(result.errors),
    "skipped": len(result.skipped), "results": result.observed,
    "source_sha256": before,
    "boundary": "Existing suites; fake model/API/probes; socket.connect blocked; no provider/lab calls.",
}
(OUT / "results.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")
print(json.dumps({k: receipt[k] for k in ["tests_run", "success", "failures", "errors", "skipped"]}))
raise SystemExit(0 if result.wasSuccessful() else 1)
