"""Prepared agent-node cached-only protocol. Import is inert; exact approval and --execute required.
Private namespace placement changes only; shared server recovery and public routes remain forbidden.
"""
import hashlib
import importlib.util
import ipaddress
import json
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-06"
SOURCE_MANIFEST_FILE = Path(__file__).with_name("agent-source-manifest.json")
spec = importlib.util.spec_from_file_location("zer46_agent_cached", Path(__file__).with_name("run_cached_fixture.py"))
cached = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cached)
cached.OUT = OUT
cached.parent.OUT = OUT
cached.parent.full.OUT = OUT
cached.parent.full.base.OUT = OUT
cached.parent.AUTHORIZATION_FILE = Path(__file__).with_name("agent-fixture-authorization.json")


def hooked_policy(table, pod):
    """A comment or unhooked chain alone is insufficient. Require ingress hook and reject in same chain."""
    name, ns, ip = pod["metadata"]["name"], pod["metadata"]["namespace"], pod["status"]["podIP"]
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,252}", x) for x in (name, ns)):
        raise ValueError("policy identity")
    address = ipaddress.ip_address(ip)
    if address.version != 4 or not address.is_private or str(address) != ip:
        raise ValueError("policy address")
    chains, rules = set(), []
    for line in table.splitlines():
        if line.startswith(":KUBE-POD-FW-"): chains.add(line.split()[0][1:])
        if line.startswith("-A "):
            try: rules.append(shlex.split(line))
            except ValueError: return False
    def val(rule, key):
        try: return rule[rule.index(key) + 1]
        except (ValueError, IndexError): return None
    if not any(r[1] == "FORWARD" and val(r, "-j") == "KUBE-ROUTER-FORWARD" for r in rules):
        return False
    for rule in rules:
        chain = val(rule, "-j")
        comment = val(rule, "--comment") or ""
        if (rule[1] != "KUBE-ROUTER-FORWARD" or chain not in chains or
                not re.fullmatch(r"KUBE-POD-FW-[A-Z2-7]{16}", chain) or
                val(rule, "-d") not in {ip, ip + "/32"} or
                "POD name:" + name + " namespace: " + ns + " to chain " + chain not in comment):
            continue
        if any(r[1] == chain and val(r, "-j") == "REJECT" and
               ["!", "--mark", "0x10000/0x10000"] == r[r.index("--mark") - 1:r.index("--mark") + 2]
               for r in rules if "--mark" in r):
            return True
    return False


class Lab(cached.Lab):
    node = "k3d-zero-door-agent-0"

    def policy_installed(self, pod):
        if pod["spec"].get("nodeName") != self.node:
            raise RuntimeError("POLICY_NODE_PIN")
        table = self.command(["docker", "--context", "desktop-linux", "exec", self.node,
                              "iptables-save", "-t", "filter"]).stdout.decode()
        return hooked_policy(table, pod)

    def ensure_cache(self):
        super().ensure_cache()
        nodes = json.loads(self.kube("get", "nodes", "-o", "json").stdout)["items"]
        node = next(n for n in nodes if n["metadata"]["name"] == self.node)
        ips = [x["address"] for x in node["status"]["addresses"] if x["type"] == "InternalIP"]
        pods = json.loads(self.kube("get", "pods", "-A", "-o", "json").stdout)["items"]
        candidates = [p for p in pods if p["spec"].get("nodeName") == self.node and
            not p["spec"].get("hostNetwork") and not p["metadata"].get("deletionTimestamp") and
            p["status"].get("phase") == "Running" and p["status"].get("podIP") and
            p["status"].get("hostIP") in ips]
        if not candidates: raise RuntimeError("EXISTING_POLICY_POD_MISSING")
        pod = candidates[0]
        if not self.policy_installed(pod): raise RuntimeError("EXISTING_POLICY_HOOK_MISSING")
        self.save("node-policy-admission.json", {"node": self.node, "node_internal_ips": ips,
            "existing_pod": {"namespace": pod["metadata"]["namespace"], "name": pod["metadata"]["name"],
                "uid": pod["metadata"]["uid"], "host_ip": pod["status"]["hostIP"], "pod_ip": pod["status"]["podIP"]},
            "hooked_policy_observed": True, "fixture_policy_still_required": True})


cached.parent.Lab = Lab

def verify_prepared_sources():
    auth = json.loads(cached.parent.AUTHORIZATION_FILE.read_text())
    manifest_path = SOURCE_MANIFEST_FILE
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != auth["sourceManifestSha256"]:
        raise RuntimeError("PREPARED_MANIFEST_DRIFT")
    manifest = json.loads(manifest_path.read_text())
    for path, expected in manifest["files"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise RuntimeError("PREPARED_SOURCE_DRIFT:" + path)


if __name__ == "__main__":
    verify_prepared_sources()
    sys.exit(cached.parent.main())
