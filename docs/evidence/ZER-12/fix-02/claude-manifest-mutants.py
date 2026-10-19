"""Mutants against the fix-01 manifest gates (OpenAPI field/type + effective env). Offline, no cluster.

Each mutant breaks runtime wiring in a way Kubernetes would accept or the guard would fail closed on.
Reports which gate (if any) catches it. Product files are only read.
"""
from copy import deepcopy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
from check_guard_manifests import check as openapi  # noqa: E402
from test_command_guard_ci import effective_guard_environment  # noqa: E402


def docs(agent):
    name = "chaos-worker.yaml" if agent == "chaos-worker" else agent + "-deployment.yaml"
    return list(yaml.safe_load_all((ROOT / "infrastructure/manifests" / name).read_text()))


def parts(d):
    dep = next(x for x in d if x and x["kind"] == "Deployment")
    spec = dep["spec"]["template"]["spec"]
    cm = next(x for x in d if x and x["kind"] == "ConfigMap")
    return dep, spec, spec["containers"][0], cm


def m_prefix(d):  # envFrom prefix renames every variable: ZD_* never reaches the process
    parts(d)[2]["envFrom"][0]["prefix"] = "CFG_"


def m_mount_swap(d):  # /command-policy mounted from the operator/fault Secret volume
    c = parts(d)[2]
    a = next(m for m in c["volumeMounts"] if m["mountPath"] == "/command-policy")
    other = next(m for m in c["volumeMounts"] if m["mountPath"] != "/command-policy" and m["name"] != "command-ledger")
    a["name"], other["name"] = other["name"], a["name"]


def m_ledger_readonly(d):  # ledger mount read-only: claim cannot be written
    c = parts(d)[2]
    for m in c["volumeMounts"]:
        if m["name"] == "command-ledger":
            m["readOnly"] = True


def m_cm_namespace(d):  # ConfigMap lands in another namespace than the Deployment
    parts(d)[3]["metadata"]["namespace"] = "default"


def m_env_valuefrom(d):  # explicit env overrides the ConfigMap value from elsewhere
    parts(d)[2].setdefault("env", []).append(
        {"name": "ZD_COMMAND_POLICY_FILE", "valueFrom": {"configMapKeyRef": {"name": "other", "key": "p"}}})


def m_policy_volume_secret(d):  # the policy volume itself points at a Secret
    spec = parts(d)[1]
    for v in spec["volumes"]:
        if v["name"] == "command-policy":
            v.pop("configMap")
            v["secret"] = {"secretName": "zd-command-operator"}


def m_metadata_original(d):  # control: the v1 defect
    cm = parts(d)[3]
    cm["metadata"]["ZD_COMMAND_POLICY_FILE"] = cm["data"].pop("ZD_COMMAND_POLICY_FILE")


MUTANTS = [m_metadata_original, m_prefix, m_mount_swap, m_ledger_readonly, m_cm_namespace, m_env_valuefrom, m_policy_volume_secret]

if __name__ == "__main__":
    for agent in ("chaos-worker", "nemesis", "hephaestus"):
        clean = docs(agent)
        openapi(clean)
        effective_guard_environment(clean, agent)
        print(f"{agent:12} clean control: OpenAPI PASS, effective-env PASS")
        for mutant in MUTANTS:
            if agent == "hephaestus" and mutant is m_ledger_readonly:
                continue
            d = deepcopy(clean)
            mutant(d)
            caught = []
            for name, gate in (("openapi", lambda: openapi(d)), ("effective-env", lambda: effective_guard_environment(d, agent))):
                try:
                    gate()
                except Exception as error:  # noqa: BLE001 - report any gate failure
                    caught.append(f"{name}:{type(error).__name__}")
            print(f"{agent:12} {mutant.__name__:24} caught_by={caught or 'NONE'}")
