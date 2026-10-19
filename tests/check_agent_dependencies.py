"""Assert the tests load every version shipped by an agent, plus test-only imports.

No network or startup hooks. Windows skips only uvloop (Linux image uses it).
Run in the per-agent test environment BEFORE the ASGI/guard suites.
"""
import importlib.metadata
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(agent):
    if agent not in {"nemesis", "hephaestus"}:
        raise ValueError("unsupported production agent")
    lock = (ROOT / "agent-orchestrator" / agent / "requirements.lock").read_text()
    checked = {}
    for name, version in re.findall(r"^([a-zA-Z0-9_.-]+)==([^\s;\\]+)", lock, re.M):
        if name == "uvloop" and sys.platform == "win32":
            continue
        actual = importlib.metadata.version(name)
        if actual != version:
            raise AssertionError((agent, name, version, actual))
        checked[name] = actual
    if not checked:
        raise AssertionError("empty production version check")
    return checked


if __name__ == "__main__":
    import json
    print(json.dumps({"agent": sys.argv[1], "versions": check(sys.argv[1]),
                      "python": sys.version, "executable": sys.executable,
                      "platform": sys.platform, "uvloop_skipped": sys.platform == "win32",
                      "limits": "Dependency equality only; not a Docker/runtime receipt"}, indent=2))
