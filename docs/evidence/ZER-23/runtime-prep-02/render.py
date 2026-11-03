"""Private ZER-21 topology. Rendering and importing perform no native operations."""
from copy import deepcopy
import importlib.util
import json
import run as supervisor
import yaml

ROOT = supervisor.ROOT
spec = importlib.util.spec_from_file_location("zer21_fixture_renderer",
    ROOT / "docs/evidence/ZER-50/runtime-prep/render.py")
fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
# runtime-03 Source B had sustained throttling and an anomalous CPU charge at 50m.
# 500m is a mitigation; the origin of that charge and incident-path efficacy remain unproven.
# Evidence: docs/evidence/ZER-21/runtime-03-investigation/exec-cpu-diagnostic/README.md
SOURCE_CPU_LIMIT = "500m"


def render(scope, run_id, trial_id, proxy_ip, node="k3d-zero-door-agent-0"):
    docs = fixture.render(scope, run_id, trial_id, proxy_ip, node=node)
    sources = [d for d in docs if d["kind"] == "Pod" and d["metadata"]["name"] in {"zer46-source-a", "zer46-source-b"}]
    if len(sources) != 2:
        raise ValueError("SOURCE_PODS")
    for pod in sources:
        next(c for c in pod["spec"]["containers"] if c["name"] == "source")["resources"]["limits"]["cpu"] = SOURCE_CPU_LIMIT
    next(p for p in sources if p["metadata"]["name"] == "zer46-source-a")["metadata"]["labels"]["zero-door.io/kafka-client"] = scope
    proxy = next(d for d in docs if (d["kind"], d["metadata"]["name"]) ==
        ("Service", "zer46-private-ingress"))
    alias = deepcopy(proxy)
    # Preserve the endpoint hardcoded in both guards/Go image; no endpoint weakening.
    alias["metadata"]["name"] = "zer41-private-ingress"
    docs.append(alias)
    return docs


def worker_documents(context, scope, ingress_ip):
    """Called after the private alias Service has a native assigned ClusterIP."""
    import ipaddress
    address = ipaddress.ip_address(ingress_ip)
    if (address.version != 4 or str(address) != ingress_ip or not address.is_private
            or address.is_loopback or address.is_link_local or address.is_unspecified
            or address.is_multicast or address.is_reserved):
        raise ValueError("PRIVATE_SERVICE_IP")
    original = list(yaml.safe_load_all((ROOT / "docs/evidence/ZER-19/runtime-rendered-disabled.yaml").read_bytes()))
    policy = json.loads(next(d["data"]["policy.json"] for d in original
        if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "zer42-policy"))
    policy["context"] = {k:context[k] for k in ("run_id","trial_id","group")}
    policy["enabled"] = policy["sqli"]["enabled"] = True
    policy["maxDurationSec"] = policy["maxConcurrency"] = policy["rps"] = 1
    policy["sqli"]["maxSends"] = policy["sqli"]["maxCommandSec"] = 1
    metadata = lambda name: {"name": name, "namespace": "zd-sqli-lab", "labels": {"zero-door.io/run": scope}}
    config = {"apiVersion": "v1", "kind": "ConfigMap", "metadata": metadata("zer21-worker-policy"),
        "data": {"policy.json": json.dumps(policy, allow_nan=False)}}
    paths = ["nemesis/session.py", "nemesis/session_cli.py", "nemesis/command_guard.py",
             "event_pipeline/__init__.py", "event_pipeline/contract.py", "event_pipeline/llm.py"]
    data = {str(i) + ".py": (ROOT / "agent-orchestrator" / p).read_text(encoding="utf8") for i,p in enumerate(paths)}
    data["remote.py"] = (supervisor.PREP / "remote.py").read_text(encoding="utf8")
    data["handoff.py"] = (supervisor.PREP / "kafka_handoff.py").read_text(encoding="utf8")
    source = {"apiVersion": "v1", "kind": "ConfigMap", "metadata": metadata("zer21-transport-source"), "data": data}
    items = [{"key": str(i) + ".py", "path": p} for i,p in enumerate(paths)] + [{"key":"remote.py","path":"remote.py"},{"key":"handoff.py","path":"handoff.py"}]
    volumes = [{"name":"zer21-policy","configMap":{"name":"zer21-worker-policy"}},
        {"name":"zer21-fault","secret":{"secretName":"zer21-fault"}},
        {"name":"zer21-operator","secret":{"secretName":"zer21-operator"}},
        {"name":"zer21-source","configMap":{"name":"zer21-transport-source","items":items}},
        {"name":"zer21-worker-ledger","emptyDir":{}}, {"name":"zer21-transport-ledger","emptyDir":{}}]
    prefix = "zer19-" + context["run_id"][4:16]
    worker = deepcopy(next(d["spec"]["containers"][0] for d in original
        if d["kind"] == "Pod" and d["metadata"]["name"] == "zer42-worker"))
    worker["name"] = "zer21-worker"
    worker["imagePullPolicy"] = "Never"
    worker["resources"] = {"requests":{"cpu":"50m","memory":"32Mi"},"limits":{"cpu":"250m","memory":"192Mi"}}
    worker["env"] = [{"name":k,"value":v} for k,v in {
        "KAFKA_BOOTSTRAP_SERVERS":"kafka.zero-door.svc.cluster.local:9092",
        "KAFKA_COMMANDS_TOPIC":prefix + ".commands", "KAFKA_RESULTS_TOPIC":prefix + ".results",
        "KAFKA_GROUP_ID":scope + ".worker", "ZD_COMMAND_POLICY_FILE":"/policy/policy.json",
        "ZD_COMMAND_SIGNER_FILE":"/fault/key.json", "ZD_COMMAND_LEDGER_DIR":"/ledger",
        "ZD_SQLI_INGRESS_IP":ingress_ip}.items()]
    worker["volumeMounts"] = [{"name":"zer21-policy","mountPath":"/policy","readOnly":True},
        {"name":"zer21-fault","mountPath":"/fault","readOnly":True},
        {"name":"zer21-worker-ledger","mountPath":"/ledger"}]
    transport = {"name":"zer21-transport","image":"zer42-nemesis:e80bc554b7ef","imagePullPolicy":"Never",
        "command":["python","-B","-c","import time; time.sleep(900)"],
        "resources":{"requests":{"cpu":"25m","memory":"32Mi"},"limits":{"cpu":"150m","memory":"128Mi"}},
        "env":[{"name":k,"value":v} for k,v in {"PYTHONPATH":"/current:/usr/local/lib/python3.11/site-packages", "PYTHONDONTWRITEBYTECODE":"1",
            "ZD_COMMAND_POLICY_FILE":"/policy/policy.json", "ZD_COMMAND_SIGNER_FILE":"/fault/key.json",
            "ZD_OPERATOR_TOKEN_FILE":"/operator/key.json", "ZD_COMMAND_LEDGER_FILE":"/ledger/requests.sqlite3"}.items()],
        "securityContext":{"allowPrivilegeEscalation":False,"capabilities":{"drop":["ALL"]}},
        "volumeMounts":[{"name":n,"mountPath":p,"readOnly":ro} for n,p,ro in
            [("zer21-policy","/policy",True),("zer21-fault","/fault",True),
             ("zer21-operator","/operator",True),("zer21-source","/current",True),
             ("zer21-transport-ledger","/ledger",False)]]}
    network = {"apiVersion":"networking.k8s.io/v1","kind":"NetworkPolicy",
        "metadata":metadata("zer21-kafka-egress"), "spec":{"podSelector":{"matchLabels":{"zero-door.io/run":scope,"zero-door.io/kafka-client":scope}},
            "policyTypes":["Egress"], "egress":[{"to":[{"namespaceSelector":{"matchLabels":{"kubernetes.io/metadata.name":"zero-door"}},
                "podSelector":{"matchLabels":{"app.kubernetes.io/name":"kafka"}}}],
                "ports":[{"protocol":"TCP","port":9092}]}]}}
    return [config, source, network], [worker,transport], volumes, policy
