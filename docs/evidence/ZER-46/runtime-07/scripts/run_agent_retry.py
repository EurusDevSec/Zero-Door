"""Prepared one-attempt runtime07 after verified collector correction. No effect on import."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-07"
spec = importlib.util.spec_from_file_location("zer46_agent_retry", Path(__file__).with_name("run_agent_fixture.py"))
agent = importlib.util.module_from_spec(spec); spec.loader.exec_module(agent)
agent.OUT = OUT
agent.cached.OUT = OUT
agent.cached.parent.OUT = OUT
agent.cached.parent.full.OUT = OUT
agent.cached.parent.full.base.OUT = OUT
agent.cached.parent.AUTHORIZATION_FILE = Path(__file__).with_name("agent-retry-authorization.json")
agent.SOURCE_MANIFEST_FILE = Path(__file__).with_name("agent-retry-source-manifest.json")

if __name__ == "__main__":
    agent.verify_prepared_sources()
    sys.exit(agent.cached.parent.main())
