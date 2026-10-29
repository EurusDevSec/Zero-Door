"""Offline-only candidate renderer, using the accepted private ZER-41 topology as provenance.

No subprocess, Kubernetes, HTTP, image build or credential loading. The historical artifact is read-only.
Runtime must verify fresh proxy/source IPs, node/controller rules and UID ownership before releasing the
fixture's startup gate. Rendering a document is not authorization to apply it.
"""
import argparse
import copy
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "docs/evidence/ZER-41/runtime-02/scripts/runtime-recovered.yaml"
sys.path.insert(0, str(ROOT / "tests"))
from check_guard_manifests import check  # noqa: E402


def render(scope, run_id, trial_id, proxy_ip, node="k3d-zero-door-server-0"):
    if node not in {"k3d-zero-door-server-0", "k3d-zero-door-agent-0"}:
        raise ValueError("node pin")
    if (not re.fullmatch(r"zer46-[a-z0-9]{12}", scope) or
            not re.fullmatch(r"run_[0-9a-f]{32}", run_id) or not re.fullmatch(r"trl_[0-9a-f]{32}", trial_id)):
        raise ValueError("context pin")
    address = ipaddress.ip_address(proxy_ip)
    if (address.version != 4 or not address.is_private or address.is_loopback or address.is_link_local or
            address.is_multicast or address.is_unspecified or address.is_reserved or str(address) != proxy_ip):
        raise ValueError("private proxy pin")
    pins = json.loads((ROOT / "docs/evidence/ZER-46/source-hashes.json").read_text())
    for path, expected in pins["source"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError("source drift: " + path)
    # Names/labels are updated together, preserving the private routing and policy selectors.
    docs = list(yaml.safe_load_all(BASE.read_text().replace("zer41-", "zer46-")))
    docs = [d for d in docs if d]
    for d in docs:
        d["metadata"].setdefault("labels", {})["zero-door.io/run"] = scope
        if d["kind"] == "Namespace":
            d["metadata"]["labels"]["zero-door.io/containment-scope"] = scope
        if d["kind"] in {"Deployment", "Pod"}:
            pod = d["spec"]["template"]["spec"] if d["kind"] == "Deployment" else d["spec"]
            pod["nodeSelector"] = {"kubernetes.io/hostname": node}
            if d["kind"] == "Deployment":
                d["spec"]["template"]["metadata"].setdefault("labels", {})["zero-door.io/run"] = scope
            else:
                pod["activeDeadlineSeconds"] = 900
                pod["containers"][0]["command"] = ["/usr/bin/python3", "-c", "import time; time.sleep(900)"]
            for container in pod["containers"]:
                container["imagePullPolicy"] = "Never"
                if container["name"] != "traefik":
                    container["image"] = pins["fixtureCandidateTag"]
                    container["imagePullPolicy"] = "Never"
    fixture = next(d for d in docs if d["kind"] == "Deployment" and d["metadata"]["name"] == "sqli-fixture")
    fixture["spec"]["strategy"] = {"type": "Recreate"}
    pod = fixture["spec"]["template"]["spec"]
    pod.pop("initContainers", None)  # Running Pod lets K3s install policy; no init/controller deadlock.
    container = pod["containers"][0]
    container["command"] = ["/usr/bin/python3", "-c",
        "import time,runpy; from pathlib import Path; end=time.monotonic()+120; "
        "exec('while not Path(\"/data/.policy-release\").exists():\\n "
        "assert time.monotonic()<end, \"POLICY_GATE_TIMEOUT\"; time.sleep(0.2)'); "
        "runpy.run_path('/app/app.py',run_name='__main__')"]
    container["startupProbe"] = {"httpGet": {"path": "/health", "port": "http"},
                                 "periodSeconds": 5, "timeoutSeconds": 1, "failureThreshold": 30}
    container["env"] = [{"name": "ZD_SQLI_CONTAINMENT_FILE", "value": "/containment/policy.json"},
                        {"name": "ZD_SQLI_CONTAINMENT_SCOPE", "value": scope}]
    container["volumeMounts"].append({"name": "containment", "mountPath": "/containment", "readOnly": True})
    pod["volumes"].append({"name": "containment", "configMap": {"name": "zer46-sqli-containment"}})
    config = next(d for d in docs if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "sqli-fixture-config")
    config["data"]["ZD_SQLI_PROFILE"] = "safe"
    config["data"]["ZD_SQLI_TOPOLOGY"] = "proxied"
    config["data"]["ZD_SQLI_TRUSTED_PROXIES"] = proxy_ip + "/32"
    addon = list(yaml.safe_load_all((ROOT / "infrastructure/manifests/sqli-containment-lab.yaml").read_text()))
    for d in addon:
        d = copy.deepcopy(d)
        d["metadata"].setdefault("labels", {}).update({"zero-door.io/run": scope, "zero-door.io/containment-scope": scope})
        if d["kind"] == "ConfigMap":
            d["data"]["policy.json"] = json.dumps({"version": "zer46-containment/1", "scope": scope,
                "run_id": run_id, "trial_id": trial_id, "rules": []}, separators=(",", ":"))
        docs.append(d)
    check(docs)
    if any(d["kind"] == "Ingress" for d in docs):
        raise ValueError("public route")
    if any(d["metadata"].get("namespace", "zd-sqli-lab") != "zd-sqli-lab" for d in docs):
        raise ValueError("namespace")
    return docs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("scope", "run-id", "trial-id", "proxy-ip", "output"):
        p.add_argument("--" + field, required=True)
    a = p.parse_args()
    documents = render(a.scope, a.run_id, a.trial_id, a.proxy_ip)
    with Path(a.output).open("x", encoding="utf8", newline="\n") as out:
        yaml.safe_dump_all(documents, out, sort_keys=False)
    print("OFFLINE_RENDERED_NOT_APPLIED", len(documents))


if __name__ == "__main__":
    main()
