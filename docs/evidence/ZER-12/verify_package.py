"""Read-only package consistency check. Does not execute tests, clients or services."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local(name):
    path = (ROOT / name).resolve()
    path.relative_to(ROOT.resolve())
    return path

def main():
    manifest = json.loads((HERE / "source-manifest.json").read_text(encoding="utf-8"))
    checked = 0
    for group in ("sources", "evidence", "protected"):
        for name, expected in manifest[group].items():
            assert digest(local(name)) == expected, (group, name)
            checked += 1
    for name, expected in manifest["unchanged_dirty"].items():
        assert digest(local(name)) == expected, ("existing dirty changed", name)
        checked += 1
    for name, item in manifest["append_prepend"].items():
        content = local(name).read_bytes()
        old = content[:item["bytes"]] if item["kind"] == "prefix" else content[-item["bytes"]:]
        assert hashlib.sha256(old).hexdigest() == item["sha256"], ("handoff boundary", name)
    total = 0
    for name, count in {"command_guards": 7, "command_modes": 3, "command_guard_integration": 10, "command_guard_ci": 4,
                        "event_agents": 4, "event_pipeline": 22, "event_pipeline_regressions": 42,
                        "event_actor_verifier": 4, "nemesis_consumer": 3}.items():
        text = (HERE / "results" / ("pinned-" + name + ".txt")).read_text(encoding="utf-8")
        assert re.search(r"Ran " + str(count) + r" tests? in ", text), name
        assert re.search(r"\nOK\s*$", text), name
        total += count
    assert total == 99
    events = [json.loads(line) for line in (HERE / "results/go-pinned-tests.jsonl").read_text(encoding="utf-8").splitlines()]
    assert not any(e["Action"] == "fail" for e in events)
    tests = {e["Test"] for e in events if e["Action"] == "pass" and e.get("Test") and "/" not in e["Test"]}
    summary = json.loads((HERE / "result-summary.json").read_text(encoding="utf-8"))
    assert len(tests) == 17 and tests == set(summary["go"]["tests"])
    assert not (HERE / "results/go-pinned-vet.txt").read_text(encoding="utf-8").strip()
    assert not (HERE / "results/go-pinned-linux-build.txt").read_text(encoding="utf-8").strip()
    before = [json.loads(line) for line in (HERE / "results/fail-before.jsonl").read_text(encoding="utf-8").splitlines()]
    failed = {e["Test"] for e in before if e["Action"] == "fail" and e.get("Test")}
    assert failed == {"TestURLConfusionRejected", "TestOperatorDurationCap", "TestDuplicateJSONRejected"}
    assert any(e["Action"] == "pass" and e.get("Test") == "TestValidControl" for e in before)
    contract = json.loads((HERE / "results/pinned-contract-release.txt").read_text(encoding="utf-8"))
    assert contract["links"] == "PASS" and all(v["passed"] for v in contract["focused_cases"])
    assert "Issues : 0" in (HERE / "results/gosec.txt").read_text(encoding="utf-8")
    assert "No issues identified." in (HERE / "results/bandit.txt").read_text(encoding="utf-8")
    assert "All offline Bash behavioral checks passed" in (HERE / "results/shell.txt").read_text(encoding="utf-8")
    assert not (HERE / "results/diff-check.txt").read_text(encoding="utf-8").strip()
    print(json.dumps({"verdict": "PASS", "hashed_files_checked": checked, "python_tests": total, "go_top_level_tests": len(tests),
                      "fail_before_detected": len(failed), "control": "PASS", "limits": "Offline only; independent review/CI/runtime/acceptance not inferred"}, indent=2))

if __name__ == "__main__":
    main()
