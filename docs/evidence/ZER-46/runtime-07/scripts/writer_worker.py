"""Owned component writer process, JSON-lines RPC; no network until the explicit main entry point.
This never enables the production Hephaestus executor or creates credentials.
"""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from hephaestus.sqli_containment import SqliContainment  # noqa: E402


def main():
    import yaml
    from kubernetes import client, config
    parser = argparse.ArgumentParser()
    parser.add_argument("--pins", type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(args.pins.read_text())
    path = Path(os.environ.get("KUBECONFIG") or Path.home() / ".kube/config")
    raw = yaml.safe_load(path.read_text())
    ctx = next(c["context"] for c in raw["contexts"] if c["name"] == "k3d-zero-door")
    cluster = next(c["cluster"] for c in raw["clusters"] if c["name"] == ctx["cluster"])
    user = next(c["user"] for c in raw["users"] if c["name"] == ctx["user"])
    url = urlsplit(cluster["server"])
    if url.scheme != "https" or url.hostname != "127.0.0.1" or url.port != 7356:
        raise ValueError("KUBE_SERVER_PIN")
    if "exec" in user or "auth-provider" in user:
        raise ValueError("DYNAMIC_AUTH_NOT_IN_SCOPE")
    config.load_kube_config(config_file=str(path), context="k3d-zero-door")
    api = client.CoreV1Api()
    backend = SqliContainment(api, **pins["target"])
    for line in sys.stdin:
        command = {}
        try:
            command = json.loads(line)
            if command == {"op": "cleanup"}:
                result = backend.cleanup(expired_only=False)
            elif command == {"op": "block"}:
                result = backend.block(action_id=pins["action_id"], evidence=pins["evidence"], ttl_sec=180)
            else:
                raise ValueError("RPC_OPERATION")
            reply = {"ok": True, "op": command["op"], "pid": os.getpid(), "result": result}
        except Exception as error:
            reply = {"ok": False, "op": command.get("op"), "pid": os.getpid(), "error_type": type(error).__name__,
                     "reason": str(error) if isinstance(error, ValueError) else "API_OR_TRANSPORT_FAILURE"}
        print(json.dumps(reply), flush=True)


if __name__ == "__main__":
    main()
