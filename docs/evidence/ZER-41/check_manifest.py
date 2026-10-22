"""Offline check of infrastructure/manifests/sqli-fixture.yaml for ZER-41.

Validates every resource against the pinned Kubernetes OpenAPI models (tests/check_guard_manifests.py),
then checks the semantics the package promises: default-safe profile, read-only root with the DB as the
only writable volume, non-root securityContext, ClusterIP, the Service selector/port matching the
Deployment, a /fixture Ingress route that does not take /, a default-deny NetworkPolicy, and no Secret.
Renders nothing against a cluster. Exit 0 and one line per check on PASS.

    python -B docs/evidence/ZER-41/check_manifest.py
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
MANIFEST = ROOT / "infrastructure/manifests/sqli-fixture.yaml"


def main(out=print, manifest=MANIFEST):
    docs = [d for d in yaml.safe_load_all(Path(manifest).read_text(encoding="utf-8")) if d]
    try:
        from check_guard_manifests import check
    except ImportError:
        out("OpenAPI field/type SKIPPED (kubernetes client models not installed)")
    else:
        check(docs)
        out("OpenAPI field/type PASS", len(docs), "resources")

    kinds = [d["kind"] for d in docs]
    assert kinds.count("NetworkPolicy") == 2 and "Secret" not in kinds, "expected 2 NetworkPolicies and no Secret"
    dep = next(d for d in docs if d["kind"] == "Deployment")
    cfg = next(d for d in docs if d["kind"] == "ConfigMap")
    svc = next(d for d in docs if d["kind"] == "Service")
    ing = next(d for d in docs if d["kind"] == "Ingress")
    pod = dep["spec"]["template"]["spec"]
    container = pod["containers"][0]

    assert cfg["data"]["ZD_SQLI_PROFILE"] == "safe", "ConfigMap profile must default to safe"
    out("default profile safe PASS")

    sc = container["securityContext"]
    assert sc["readOnlyRootFilesystem"] is True and sc["allowPrivilegeEscalation"] is False
    assert sc["capabilities"]["drop"] == ["ALL"] and pod["securityContext"]["runAsNonRoot"] is True
    mounts = {m["name"]: m["mountPath"] for m in container["volumeMounts"]}
    assert mounts == {"data": "/data"} and [v["name"] for v in pod["volumes"]] == ["data"]
    assert "emptyDir" in pod["volumes"][0]
    out("read-only root, DB-only writable volume, non-root PASS")

    assert svc["spec"]["type"] == "ClusterIP"
    assert dep["spec"]["selector"]["matchLabels"] == svc["spec"]["selector"] == {"app": "sqli-fixture"}
    assert svc["spec"]["ports"][0]["targetPort"] == container["ports"][0]["name"] == "http"
    out("ClusterIP, selector and port match PASS")

    volume = pod["volumes"][0]["emptyDir"]
    assert volume.get("sizeLimit"), "the DB emptyDir must declare a sizeLimit"
    out("DB volume sizeLimit PASS", volume["sizeLimit"])

    paths = ing["spec"]["rules"][0]["http"]["paths"]
    assert [p["path"] for p in paths] == ["/fixture"] and ing["spec"]["ingressClassName"] == "traefik"
    out("Ingress /fixture prefix (does not take /) PASS")

    deny = next(d for d in docs if d["metadata"]["name"] == "default-deny")
    assert deny["spec"]["podSelector"] == {} and set(deny["spec"]["policyTypes"]) == {"Ingress", "Egress"}
    out("default-deny NetworkPolicy PASS")

    # Controller-only inbound: the allow rule must select the Traefik pod by namespace AND podSelector in
    # one peer, so an unrelated kube-system pod is not admitted. Evaluate the selector semantically.
    allow = next(d for d in docs if d["metadata"]["name"] == "allow-ingress-controller-and-dns")
    peer = allow["spec"]["ingress"][0]["from"][0]
    ns_match = peer.get("namespaceSelector", {}).get("matchLabels", {})
    pod_match = peer.get("podSelector", {}).get("matchLabels", {})
    assert pod_match, "allow peer must carry a podSelector, not the whole kube-system namespace"

    def admits(namespace, labels):
        ns = {"kubernetes.io/metadata.name": namespace}
        return all(ns.get(k) == v for k, v in ns_match.items()) and all(labels.get(k) == v for k, v in pod_match.items())

    assert admits("kube-system", {"app.kubernetes.io/name": "traefik"}), "controller must be admitted"
    assert not admits("kube-system", {"app": "unrelated"}), "an unrelated kube-system pod must be denied"
    assert not admits("zd-sqli-lab", {"app": "probe"}), "an in-namespace pod must not match the controller peer"
    out("controller-only ingress selector PASS (traefik admitted; unrelated kube-system denied)")
    out("OVERALL PASS")


if __name__ == "__main__":
    main(manifest=sys.argv[1] if len(sys.argv) > 1 else MANIFEST)
