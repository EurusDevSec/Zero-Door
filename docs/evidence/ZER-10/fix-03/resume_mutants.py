"""Resume only mutations not reached after an obsolete selector stopped the first gate.

The first log is immutable evidence, not a PASS for the aborted command. Baseline134 and the
remaining registered mutations are rerun by the same checker. CI still runs the normal full gate.
"""
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_mutants


if __name__ == "__main__":
    text = (HERE / "mutants-attempt1.txt").read_text()
    completed = {}
    for name, failed, count in re.findall(r"^([A-Z0-9_]+)\s+caught=True failed=(\d+)/(\d+)", text, flags=re.M):
        assert int(failed) > 0 and int(count) > 0
        completed[name] = {"caught": True, "failed": int(failed), "run": int(count), "evidence": "mutants-attempt1.txt"}
    registered = dict(check_mutants.MUTANTS)
    assert len(completed) == 31 and set(completed) < set(registered)
    check_mutants.MUTANTS = {name: value for name, value in registered.items() if name not in completed}
    sys.argv = [__file__, "--json", str(HERE / "mutants-remaining.json")]
    code = check_mutants.main()
    result = json.loads((HERE / "mutants-remaining.json").read_text())
    all_mutants = dict(completed, **result["mutants"])
    baseline = json.loads((HERE / "offline" / "offline-summary.json").read_text())
    passed = code == 0 and baseline["verdict"] == "OFFLINE_PASS" and set(all_mutants) == set(registered)
    report = {"verdict": "PASS_RESUMED" if passed else "FAIL", "mutants": all_mutants,
              "count": len(all_mutants), "baseline": baseline,
              "remaining_control": result["control"],
              "scope": "31 unchanged mutants already caught; 9 remaining with corrected selector; not a single full-command run"}
    (HERE / "mutants.json").write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(0 if passed else 1)
