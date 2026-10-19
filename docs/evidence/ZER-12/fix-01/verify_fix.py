"""Read-only consistency check of final source, preserved evidence and test receipts.

This does not execute tests or establish independent review/CI/runtime acceptance.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def local(name):
    path = (ROOT / name).resolve()
    path.relative_to(ROOT.resolve())
    return path


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read(name):
    return (HERE / "results" / name).read_text(encoding="utf-8")


def go_events(name):
    return [json.loads(line) for line in read(name).splitlines() if line.startswith("{")]


def main():
    manifest = json.loads((HERE / "delta-manifest.json").read_text())
    total = 0
    for group in ("sources", "evidence", "before_sources", "historical", "protected", "unchanged_dirty"):
        for name, expected in manifest[group].items():
            assert digest(local(name).read_bytes()) == expected, (group, name)
            total += 1
    for name, boundary in manifest["boundaries"].items():
        content = local(name).read_bytes()
        old = content[:boundary["bytes"]] if boundary["kind"] == "prefix" else content[-boundary["bytes"]:]
        assert digest(old) == boundary["sha256"], ("append/prepend boundary", name)
    old_manifest = json.loads(local("docs/evidence/ZER-12/source-manifest.json").read_text())
    for name, old_hash in old_manifest["sources"].items():
        prior = "docs/evidence/ZER-12/fix-01/before/" + name + ".txt"
        witness = local(prior) if prior in manifest["before_sources"] else local(name)
        assert digest(witness.read_bytes()) == old_hash, ("pre-fix source witness", name)
    summary = json.loads((HERE / "result-summary.json").read_text())
    runs = 0
    for agent in ("nemesis", "hephaestus"):
        for group, count in summary["python"]["groups"].items():
            log = read(agent + "-" + group + ".txt")
            assert re.search(r"Ran " + str(count) + r" tests? in ", log), (agent, group)
            assert re.search(r"\nOK\s*$", log), (agent, group)
            runs += count
        dependencies = json.loads(read("dependencies-" + agent + ".json"))
        assert dependencies["python"].startswith("3.11.9 ")
        for name, version in re.findall(r"^([a-zA-Z0-9_.-]+)==([^\s;\\]+)", local("agent-orchestrator/" + agent + "/requirements.lock").read_text(), re.M):
            if name == "uvloop" and dependencies["uvloop_skipped"]:
                continue
            assert dependencies["versions"][name] == version, (agent, name)
        assert read("openapi-" + agent + ".txt").count("OpenAPI field/type PASS") == 4
    for group, count in summary["python"]["regression"].items():
        log = read(group + ".txt")
        assert re.search(r"Ran " + str(count) + r" tests? in ", log) and re.search(r"\nOK\s*$", log), group
        runs += count
    assert runs == 133
    events = go_events("go-tests.jsonl")
    assert not any(e["Action"] == "fail" for e in events)
    tests = {e["Test"] for e in events if e["Action"] == "pass" and e.get("Test") and "/" not in e["Test"]}
    assert len(tests) == 22 and tests == set(summary["go"]["top_level_tests"])
    for name in ("go-vet.txt", "go-linux-build.txt", "diff-check.txt", "staged.txt"):
        assert not read(name).strip(), name
    assert read("head.txt").strip() == manifest["baseline_head"]
    assert "Issues : 0" in read("gosec.txt")
    assert "No issues identified." in read("bandit.txt")
    before = go_events("package-go-before.jsonl")
    failed = {e["Test"] for e in before if e["Action"] == "fail" and e.get("Test")}
    assert failed == {"TestReviewExactJSONTagsAtEveryBoundary", "TestReviewClockLeadBoundAndExpiry",
                      "TestReviewExpiredRedeliveryKeepsOutcomeWithoutEffect", "TestReviewExpiredPendingIsStillUnknown"}
    assert any(e["Action"] == "pass" and e.get("Test") == "TestPolicyCapsAndTargets" for e in before)
    assert "EXPECTED_BASELINE_FAILURES=2 CLEAN_CONTROLS=2" in read("package-python-before.txt")
    assert read("package-manifest-before.txt").count("baseline rejected") == 6
    assert read("package-manifest-before.txt").count("fixed valid control PASS") == 3
    contract = json.loads(read("contract-release.json"))
    assert contract["links"] == "PASS" and all(v["passed"] for v in contract["focused_cases"])
    print(json.dumps({"verdict": "PASS", "hashed_file_checks": total,
                      "python_unique_methods": 102, "python_method_runs": runs,
                      "go_top_level_tests": len(tests), "go_fail_before": len(failed),
                      "python_fail_before": 2, "limits": "Offline consistency only; no independent/CI/runtime/Done verdict"}, indent=2))


if __name__ == "__main__":
    main()
