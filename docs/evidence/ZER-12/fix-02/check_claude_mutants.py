from pathlib import Path
import importlib.util
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
p = Path(__file__).parent / "claude-manifest-mutants.py"
spec = importlib.util.spec_from_file_location("claude_manifest_mutants", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
count = 0
for agent in ("chaos-worker", "nemesis", "hephaestus"):
    m.effective_guard_environment(m.docs(agent), agent)
    for mutant in m.MUTANTS:
        if agent == "hephaestus" and mutant is m.m_ledger_readonly:
            continue
        documents = m.docs(agent)
        mutant(documents)
        try:
            m.effective_guard_environment(documents, agent)
        except ValueError as error:
            print(agent, mutant.__name__, "CAUGHT", str(error))
            count += 1
        else:
            raise AssertionError((agent, mutant.__name__, "missed"))
assert count == 20, count
print("20/20 independent Claude mutants caught; 3/3 clean controls PASS")
