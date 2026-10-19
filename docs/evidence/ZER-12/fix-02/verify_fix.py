"""Read-only hashes/log consistency; not execution or owner acceptance."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "delta-manifest.json").read_text(encoding="utf-8"))
count = 0
for group in ("sources", "evidence", "before_sources", "prior_evidence", "protected", "unchanged_dirty"):
    for name, expected in m[group].items():
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise AssertionError((name, "missing/symlink"))
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError((name, actual, expected))
        count += 1
for agent in ("nemesis", "hephaestus"):
    for test, n in {"command_guards": 7, "command_modes": 3, "command_guard_integration": 13,
                    "command_guard_ci": 6, "event_agents": 4}.items():
        text = (HERE / "results" / (agent + "-" + test + ".txt")).read_text(encoding="utf-8")
        assert "Ran " + str(n) + " tests" in text and text.rstrip().endswith("OK"), (agent, test)
text = (HERE / "results/fail-before-portable.txt").read_text(encoding="utf-8")
assert "24/24" in text and "regression fails on response LEDGER_UNAVAILABLE as expected" in text
assert "20/20 independent Claude mutants caught; 3/3 clean controls PASS" in (HERE / "results/claude-mutants.txt").read_text(encoding="utf-8")
assert not (HERE / "results/diff-check.txt").read_text(encoding="utf-8").strip()
print(json.dumps({"verdict": "PASS", "hashed_file_checks": count, "python_unique_methods": 36,
                  "python_method_runs": 69, "limits": "Offline hash/log consistency; no CI/runtime/Done verdict"}, indent=2))
