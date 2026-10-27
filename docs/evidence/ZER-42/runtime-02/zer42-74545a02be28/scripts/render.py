"""Render the private ZER-42 acceptance topology offline; never contacts Docker/Kubernetes.

The default policy is disabled. Real IPs, trust configuration, ephemeral keys and
enablement are set only inside an approved runtime turn after preflight.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())
NS = "zd-sqli-lab"
NODE = "k3d-zero-door-agent-0"
SECURITY = {"runAsNonRoot": True, "runAsUser": 65532, "runAsGroup": 65532,
            "fsGroup": 65532, "seccompProfile": {"type": "RuntimeDefault"}}
CONTAINER_SECURITY = {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True,
                      "capabilities": {"drop": ["ALL"]}}


def render(run, fixture_image, proxy_image, worker_image, nemesis_image, topic_prefix=None):
    topic_prefix = topic_prefix or run
    if not re.fullmatch(r"zer42-[a-f0-9]{12}", run):
        raise ValueError("invalid run ID")
    for image, pattern in ((fixture_image, r"zer41-fixture:[a-f0-9]{12}"),
                           (proxy_image, r"(?:docker.io/)?(?:library/)?traefik@sha256:[a-f0-9]{64}"),
                           (worker_image, r"zer42-worker:[a-f0-9]{12}"),
                           (nemesis_image, r"zer42-nemesis:[a-f0-9]{12}")):
        if not re.fullmatch(pattern, image):
            raise ValueError("expected source-specific local image or observed proxy digest")
    owner = {"zero-door.io/run": run}
    docs = [d for d in yaml.safe_load_all((ROOT / "infrastructure/manifests/sqli-fixture.yaml").read_text())
            if d and d["kind"] != "Ingress"]
    for doc in docs:
        doc["metadata"].setdefault("labels", {}).update(owner)

    def find(kind, name):
        return next(d for d in docs if d["kind"] == kind and d["metadata"]["name"] == name)

    def add(kind, name, spec=None, **extra):
        version = "apps/v1" if kind == "Deployment" else "networking.k8s.io/v1" if kind == "NetworkPolicy" else "v1"
        doc = {"apiVersion": version, "kind": kind, "metadata": {
            "name": name, "namespace": NS, "labels": dict(owner)}, **extra}
        if spec is not None:
            doc["spec"] = spec
        docs.append(doc)
        return doc

    def peer(app):
        return {"podSelector": {"matchLabels": {"app": app}}}

    dns = {"to": [{"namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": "kube-system"}},
                    "podSelector": {"matchLabels": {"k8s-app": "kube-dns"}}}],
           "ports": [{"protocol": "UDP", "port": 53}, {"protocol": "TCP", "port": 53}]}
    kafka = {"to": [{"namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": "zero-door"}},
                      "podSelector": {"matchLabels": {"app.kubernetes.io/name": "kafka",
                                                       "app.kubernetes.io/instance": "kafka"}}}],
             "ports": [{"protocol": "TCP", "port": 9092}]}

    fixture = find("Deployment", "sqli-fixture")
    fixture["spec"]["strategy"] = {"type": "Recreate"}
    fixture["spec"]["template"]["metadata"]["labels"].update(owner)
    pod = fixture["spec"]["template"]["spec"]
    pod["nodeSelector"] = {"kubernetes.io/hostname": NODE}
    container = pod["containers"][0]
    container.update(image=fixture_image, imagePullPolicy="Never")
    # Finite checks are driven by the harness; no unbounded kubelet HTTP probes.
    container.pop("livenessProbe", None)
    container.pop("readinessProbe", None)
    # Keep the Pod Running while the application remains unbound. kube-router
    # may not attach per-Pod policy chains while a Pod is held in init.
    container["command"] = ["/usr/bin/python3", "-c",
        "import os,time; from pathlib import Path; p=Path('/data/.policy-release'); "
        "exec(\"while not p.exists(): time.sleep(0.2)\"); "
        "os.execv('/usr/bin/python3',['/usr/bin/python3','/app/app.py'])"]
    find("Service", "sqli-fixture")["spec"]["ports"][0]["port"] = 9140
    find("ConfigMap", "sqli-fixture-config")["data"]["ZD_SQLI_TOPOLOGY"] = "proxied"
    allow = find("NetworkPolicy", "allow-ingress-controller-and-dns")
    allow["spec"]["ingress"][0]["from"] = [peer("zer41-private-ingress")]
    allow["spec"]["egress"] = [deepcopy(dns)]
    dynamic = {"http": {"routers": {"fixture": {"entryPoints": ["web"], "rule": "PathPrefix(`/fixture`)",
                    "service": "fixture"}}, "services": {"fixture": {"loadBalancer": {
                    "servers": [{"url": "http://sqli-fixture:9140"}]}}}}}
    add("ConfigMap", "zer41-private-ingress", data={"dynamic.yaml": yaml.safe_dump(dynamic, sort_keys=False)})
    proxy = {"automountServiceAccountToken": False, "securityContext": deepcopy(SECURITY),
             "nodeSelector": {"kubernetes.io/hostname": NODE}, "containers": [{
        "name": "traefik", "image": proxy_image, "imagePullPolicy": "Never",
        "args": ["--global.checkNewVersion=false", "--global.sendAnonymousUsage=false",
                 "--entrypoints.web.address=:8000", "--providers.file.filename=/config/dynamic.yaml",
                 "--accesslog.fields.headers.defaultmode=drop",
                 "--accesslog.fields.headers.names.X-Correlation-Id=keep",
                 "--accesslog.fields.headers.names.X-Request-Id=keep",
                 "--accesslog=true", "--accesslog.format=json", "--log.format=json", "--log.level=ERROR"],
        "ports": [{"name": "web", "containerPort": 8000}], "securityContext": deepcopy(CONTAINER_SECURITY),
        "resources": {"requests": {"cpu": "25m", "memory": "32Mi"}, "limits": {"cpu": "150m", "memory": "96Mi"}},
        "volumeMounts": [{"name": "config", "mountPath": "/config", "readOnly": True}]}],
        "volumes": [{"name": "config", "configMap": {"name": "zer41-private-ingress"}}]}
    add("Deployment", "zer41-private-ingress", {"replicas": 1, "strategy": {"type": "Recreate"},
        "selector": {"matchLabels": {"app": "zer41-private-ingress"}},
        "template": {"metadata": {"labels": {"app": "zer41-private-ingress", **owner}}, "spec": proxy}})
    add("Service", "zer41-private-ingress", {"type": "ClusterIP", "selector": {"app": "zer41-private-ingress"},
        "ports": [{"name": "web", "port": 8000, "targetPort": "web"}]})
    for label, image in (("zer42-worker", worker_image), ("zer42-nemesis", nemesis_image),
                         ("zer42-source-a", fixture_image), ("zer42-source-b", fixture_image)):
        actor = label in {"zer42-worker", "zer42-nemesis"}
        p = {"restartPolicy": "Never", "activeDeadlineSeconds": 2100,
             "automountServiceAccountToken": label == "zer42-worker", "securityContext": deepcopy(SECURITY),
             "nodeSelector": {"kubernetes.io/hostname": NODE}, "containers": [{
            "name": "main", "image": image, "imagePullPolicy": "Never", "securityContext": deepcopy(CONTAINER_SECURITY),
            "resources": {"requests": {"cpu": "50m" if actor else "5m", "memory": "64Mi" if actor else "16Mi"},
                          "limits": {"cpu": "200m" if actor else "50m", "memory": "192Mi" if label == "zer42-nemesis" else "128Mi" if actor else "48Mi"}}}]}
        c = p["containers"][0]
        if actor:
            c["env"] = [{"name": k, "value": v} for k, v in {
                "KAFKA_BOOTSTRAP_SERVERS": "kafka.zero-door.svc.cluster.local:9092",
                "KAFKA_COMMANDS_TOPIC": topic_prefix + ".commands", "KAFKA_RESULTS_TOPIC": topic_prefix + ".results",
                "KAFKA_GROUP_ID": run + (".worker" if label == "zer42-worker" else ".nemesis"),
                "ZD_COMMAND_POLICY_FILE": "/policy/policy.json", "ZD_COMMAND_SIGNER_FILE": "/fault/key.json",
                "ZD_COMMAND_LEDGER_DIR": "/ledger"}.items()]
            if label == "zer42-worker":
                c["env"].append({"name": "ZD_SQLI_INGRESS_IP", "value": ""})
            else:
                c["env"].append({"name": "ZD_OPERATOR_TOKEN_FILE", "value": "/operator/key.json"})
                c["env"].append({"name": "ZD_COMMAND_LEDGER_FILE", "value": "/ledger/nemesis.sqlite3"})
            c["volumeMounts"] = [{"name": "policy", "mountPath": "/policy", "readOnly": True},
                                  {"name": "fault", "mountPath": "/fault", "readOnly": True},
                                  {"name": "ledger", "mountPath": "/ledger"}]
            p["volumes"] = [{"name": "policy", "configMap": {"name": "zer42-policy"}},
                            {"name": "fault", "secret": {"secretName": "zer42-fault", "defaultMode": 288}},
                            {"name": "ledger", "emptyDir": {"sizeLimit": "16Mi"}}]
            if label == "zer42-nemesis":
                c["volumeMounts"].append({"name": "operator", "mountPath": "/operator", "readOnly": True})
                p["volumes"].append({"name": "operator", "secret": {"secretName": "zer42-operator", "defaultMode": 288}})
        else:
            c["command"] = ["/usr/bin/python3", "-c", "import time; time.sleep(2100)"]
        resource = add("Pod", label, p)
        resource["metadata"]["labels"]["app"] = label
    policy = yaml.safe_load((ROOT / "infrastructure/manifests/sqli-executor-lab.yaml").read_text())["data"]
    data = json.loads(policy["policy.json"])
    token = run.removeprefix("zer42-").ljust(32, "0")
    data["context"] = {"run_id": "run_" + token, "trial_id": "trl_" + token, "group": "B0"}
    data["sqli"].update(maxSends=3, maxCommandSec=5)
    add("ConfigMap", "zer42-policy", data={"policy.json": json.dumps(data, indent=2)})
    add("Service", "zer42-nemesis", {"type": "ClusterIP", "selector": {"app": "zer42-nemesis"},
        "ports": [{"port": 8000, "targetPort": 8000}]})
    clients = [peer("zer42-source-a"), peer("zer42-source-b"), peer("zer42-worker")]
    add("NetworkPolicy", "private-proxy", {"podSelector": {"matchLabels": {"app": "zer41-private-ingress"}},
        "policyTypes": ["Ingress", "Egress"], "ingress": [{"from": clients, "ports": [{"protocol": "TCP", "port": 8000}]}],
        "egress": [{"to": [peer("sqli-fixture")], "ports": [{"protocol": "TCP", "port": 9140}]}, deepcopy(dns)]})
    for app in ("zer42-source-a", "zer42-source-b", "zer42-worker", "zer42-nemesis"):
        egress = [deepcopy(dns)]
        if app != "zer42-nemesis":
            egress.append({"to": [peer("zer41-private-ingress")], "ports": [{"protocol": "TCP", "port": 8000}]})
        if app.startswith("zer42-source"):
            # Explicit egress allows the direct-denial test to exercise fixture INGRESS policy.
            egress += [{"to": [peer("sqli-fixture")], "ports": [{"protocol": "TCP", "port": 9140}]},
                       {"to": [peer("zer42-nemesis")], "ports": [{"protocol": "TCP", "port": 8000}]}]
        else:
            egress.append(deepcopy(kafka))
        spec = {"podSelector": {"matchLabels": {"app": app}}, "policyTypes": ["Ingress", "Egress"],
                "egress": egress, "ingress": []}
        if app == "zer42-nemesis":
            spec["ingress"] = [{"from": [peer("zer42-source-a"), peer("zer42-source-b")],
                                "ports": [{"protocol": "TCP", "port": 8000}]}]
        add("NetworkPolicy", app, spec)
    sys.path.insert(0, str(ROOT / "tests"))
    from check_guard_manifests import check
    check(docs)
    assert len([d for d in docs if d["kind"] == "Pod"]) == 4
    assert len([d for d in docs if d["kind"] == "Deployment"]) == 2
    assert not any(d["kind"] in {"Ingress", "Role", "RoleBinding", "ClusterRole", "PersistentVolumeClaim", "Secret"} for d in docs)
    assert all(d["spec"].get("type") == "ClusterIP" for d in docs if d["kind"] == "Service")
    assert data["enabled"] is False and data["sqli"]["enabled"] is False
    assert find("ConfigMap", "sqli-fixture-config")["data"]["ZD_SQLI_PROFILE"] == "safe"
    return docs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", required=True)
    for name in ("fixture", "proxy", "worker", "nemesis"):
        p.add_argument("--" + name + "-image", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    docs = render(a.run_id, a.fixture_image, a.proxy_image, a.worker_image, a.nemesis_image)
    with a.output.open("x", encoding="utf8", newline="\n") as out:
        yaml.safe_dump_all(docs, out, sort_keys=False)
    print("OFFLINE_RENDER_PASS", len(docs), "resources; six pods; policy disabled; safe fixture")


if __name__ == "__main__":
    main()

