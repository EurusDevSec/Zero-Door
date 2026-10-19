"""Offline checks that pin/guard/mode gates cannot disappear from the publication path."""
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest
import yaml
from check_guard_manifests import check as check_openapi

ROOT = Path(__file__).resolve().parents[1]


def check_workflow(workflow):
    jobs = workflow["jobs"]
    required = {"bash-tooling", "r1-agent-http", "r1-production-http", "r1-image-build", "helm-lint", "python-build", "go-build", "iac-scan"}
    if not required <= set(jobs) or not required <= set(jobs["publish-images"]["needs"]):
        raise ValueError("missing publication gate")
    steps = jobs["r1-agent-http"]["steps"]
    runs = {line.strip() for step in steps for line in step.get("run", "").splitlines()}
    for test in ("tests/test_command_guards.py", "tests/test_command_modes.py", "tests/test_command_guard_integration.py",
                 "tests/test_command_guard_ci.py", "docs/evidence/ZER-37/verify_release.py", "tests/test_event_agents.py"):
        if "python -B " + test not in runs:
            raise ValueError("missing gate: " + test)
    for job in jobs.values():
        for step in job.get("steps", []):
            if step.get("uses") and not re.fullmatch(r"[^@]+@[0-9a-f]{40}", step["uses"]):
                raise ValueError("mutable action")
            if "@latest" in step.get("run", ""):
                raise ValueError("mutable tool")
    if not any("go test -race ./..." in step.get("run", "") for step in jobs["go-build"]["steps"]):
        raise ValueError("missing Go race test")
    if {v["image"] for v in jobs["r1-image-build"]["strategy"]["matrix"]["include"]} != {"events", "gaia", "hephaestus", "nemesis", "chaos-worker"}:
        raise ValueError("missing image import smoke")
    production = jobs["r1-production-http"]
    if set(production["strategy"]["matrix"]["agent"]) != {"nemesis", "hephaestus"}:
        raise ValueError("missing production dependency matrix")
    production_runs = "\n".join(step.get("run", "") for step in production["steps"])
    for required_run in ("--require-hashes -r tests/requirements-command-${{ matrix.agent }}.lock",
                         "tests/check_agent_dependencies.py ${{ matrix.agent }}",
                         "python -B tests/check_guard_manifests.py",
                         "python -B tests/test_command_guard_integration.py"):
        if required_run not in production_runs:
            raise ValueError("missing production entrypoint gate")
    for job in ("bash-tooling", "helm-lint"):
        if not any("--require-hashes -r tests/requirements-yaml.lock" in s.get("run", "") for s in jobs[job]["steps"]):
            raise ValueError("unhashed tooling dependencies")


def effective_guard_environment(documents, agent):
    """Focused, offline check of the guard's env and mounted file sources."""
    metadata_fields = {"name", "namespace", "labels", "annotations", "generateName", "finalizers", "ownerReferences"}
    for obj in documents:
        if set(obj.get("metadata", {})) - metadata_fields:
            raise ValueError("unknown resource metadata field")
    deployment = next(d for d in documents if d["kind"] == "Deployment")
    namespace = deployment["metadata"].get("namespace", "default")
    spec = deployment["spec"]["template"]["spec"]
    configmaps = {(d["metadata"].get("namespace", "default"), d["metadata"]["name"]): d
                  for d in documents if d["kind"] == "ConfigMap"}
    container = next(c for c in spec["containers"] if c["name"] == agent)
    env = {}
    for ref in container.get("envFrom", []):
        if ref.get("prefix"):
            raise ValueError("prefixed envFrom is outside the guard wiring profile")
        if "configMapRef" in ref:
            cm = configmaps.get((namespace, ref["configMapRef"]["name"]))
            if cm is None:
                raise ValueError("missing ConfigMap in deployment namespace")
            env.update(cm.get("data", {}))
        elif "secretRef" in ref:
            secret = next((d for d in documents if d["kind"] == "Secret"
                           and d["metadata"].get("namespace", "default") == namespace
                           and d["metadata"]["name"] == ref["secretRef"]["name"]), None)
            if secret is None or any(k.startswith("ZD_") for field in ("data", "stringData")
                                     for k in secret.get(field, {})):
                raise ValueError("unverifiable or shadowing Secret envFrom")
    for value in container.get("env", []):
        if value["name"].startswith("ZD_") and "valueFrom" in value:
            raise ValueError("dynamic guard env override")
        if "value" in value:
            env[value["name"]] = value["value"]
    required = {"ZD_COMMAND_POLICY_FILE": ("/command-policy/policy.json", "command-policy", "configMap", "zd-command-policy")}
    if agent != "chaos-worker":
        required["ZD_OPERATOR_TOKEN_FILE"] = ("/command-operator/key.json", "command-operator", "secret",
                                               "zd-heal-operator" if agent == "hephaestus" else "zd-command-operator")
    if agent != "hephaestus":
        required["ZD_COMMAND_SIGNER_FILE"] = ("/command-fault/key.json", "command-fault", "secret", "zd-command-fault")
        required["ZD_COMMAND_LEDGER_DIR" if agent == "chaos-worker" else "ZD_COMMAND_LEDGER_FILE"] = (
            "/command-ledger" if agent == "chaos-worker" else "/command-ledger/claims.sqlite",
            "command-ledger", "persistentVolumeClaim", agent + "-command-ledger")
        if deployment["spec"].get("strategy", {}).get("type") != "Recreate":
            raise ValueError("ledger owner requires sequential Recreate rollout")
    mounts = container["volumeMounts"]
    volumes = {v["name"]: v for v in spec["volumes"]}
    for key, (value, name, kind, source) in required.items():
        if env.get(key) != value:
            raise ValueError("missing effective guard env: " + key)
        covering = [m for m in mounts if value == m["mountPath"] or value.startswith(m["mountPath"] + "/")]
        if len(covering) != 1:
            raise ValueError("missing or shadowed guard mount: " + key)
        mount = covering[0]
        if mount["name"] != name or mount["mountPath"] != "/" + name or "subPath" in mount or "subPathExpr" in mount:
            raise ValueError("unexpected guard mount source: " + key)
        volume = volumes.get(name, {})
        if set(volume) != {"name", kind}:
            raise ValueError("unexpected guard volume type: " + key)
        source_key = {"configMap": "name", "secret": "secretName", "persistentVolumeClaim": "claimName"}[kind]
        if volume[kind].get(source_key) != source or "items" in volume[kind]:
            raise ValueError("unexpected guard volume reference: " + key)
        if kind == "persistentVolumeClaim":
            if mount.get("readOnly", False) or volume[kind].get("readOnly", False):
                raise ValueError("ledger must be writable")
        elif mount.get("readOnly") is not True:
            raise ValueError("credential/policy mount must be readOnly")
    return env


class CIChecks(unittest.TestCase):
    def test_workflow_and_counterexamples(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
        check_workflow(workflow)
        missing = deepcopy(workflow)
        missing["jobs"]["publish-images"]["needs"].remove("r1-agent-http")
        with self.assertRaises(ValueError):
            check_workflow(missing)
        for test in ["tests/test_command_modes.py", "tests/test_command_guard_integration.py"]:
            missing = deepcopy(workflow)
            missing["jobs"]["r1-agent-http"]["steps"] = [s for s in missing["jobs"]["r1-agent-http"]["steps"] if test not in s.get("run", "")]
            with self.assertRaises(ValueError):
                check_workflow(missing)

    def test_docker_base_images_match_registry_receipts(self):
        pins = json.loads((ROOT / "docs/evidence/ZER-12/pin-metadata.json").read_text())
        allowed = {v["linux_amd64"] for v in pins["images"].values()}
        for path in [ROOT / "chaos-worker/Dockerfile", *[ROOT / "agent-orchestrator" / p / "Dockerfile" for p in ("gaia", "nemesis", "hephaestus", "event_pipeline")]]:
            for line in path.read_text().splitlines():
                if line.startswith("FROM "):
                    image = line.split()[1]
                    self.assertRegex(image, r"@sha256:[0-9a-f]{64}$")
                    self.assertIn(image.split("@", 1)[1], allowed)
        stress = (ROOT / "chaos-worker/internal/attack/cpu_stress.go").read_text()
        self.assertIn("progrium/stress@" + pins["images"]["progrium/stress"]["linux_amd64"], stress)

    def test_every_resolved_python_dependency_is_versioned_and_hashed(self):
        for path in [*ROOT.glob("tests/requirements-*.lock"), *[ROOT / "agent-orchestrator" / p / "requirements.lock" for p in ("gaia", "nemesis", "hephaestus", "event_pipeline")]]:
            lines = [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")]
            current = None
            hashes = 0
            for line in lines + ["__end__==0"]:
                if not line.startswith("--hash="):
                    if current is not None:
                        self.assertGreater(hashes, 0, (path, current))
                    self.assertRegex(line, r"^[a-zA-Z0-9_.-]+(?:\[[^]]+\])?==[^\s;]+")
                    current, hashes = line, 0
                else:
                    self.assertRegex(line, r"^--hash=sha256:[0-9a-f]{64}")
                    hashes += 1

    def test_guard_wiring_mutants_and_sequential_rollout(self):
        for agent in ("chaos-worker", "nemesis", "hephaestus"):
            filename = "chaos-worker.yaml" if agent == "chaos-worker" else agent + "-deployment.yaml"
            docs = list(yaml.safe_load_all((ROOT / "infrastructure/manifests" / filename).read_text()))
            effective_guard_environment(docs, agent)  # positive control
            defects = ["prefix", "swapped-mount", "namespace", "valueFrom", "policy-secret", "subPath"]
            if agent != "hephaestus":
                defects += ["ledger-readonly", "pvc-readonly", "rolling"]
            for defect in defects:
                with self.subTest(agent=agent, defect=defect):
                    broken = deepcopy(docs)
                    dep = next(d for d in broken if d["kind"] == "Deployment")
                    cm = next(d for d in broken if d["kind"] == "ConfigMap")
                    container = next(c for c in dep["spec"]["template"]["spec"]["containers"] if c["name"] == agent)
                    volumes = dep["spec"]["template"]["spec"]["volumes"]
                    policy = next(v for v in volumes if v["name"] == "command-policy")
                    if defect == "prefix":
                        container["envFrom"][0]["prefix"] = "BROKEN_"
                    elif defect == "swapped-mount":
                        a, b = container["volumeMounts"][:2]
                        a["name"], b["name"] = b["name"], a["name"]
                    elif defect == "namespace":
                        cm["metadata"]["namespace"] = "other-namespace"
                    elif defect == "valueFrom":
                        container.setdefault("env", []).append({"name": "ZD_COMMAND_POLICY_FILE", "valueFrom": {
                            "configMapKeyRef": {"name": cm["metadata"]["name"], "key": "MISSING"}}})
                    elif defect == "policy-secret":
                        policy.pop("configMap")
                        policy["secret"] = {"secretName": "zd-command-policy"}
                    elif defect == "subPath":
                        container["volumeMounts"][0]["subPath"] = "other"
                    elif defect == "rolling":
                        dep["spec"].pop("strategy", None)
                    elif defect == "ledger-readonly":
                        next(m for m in container["volumeMounts"] if m["name"] == "command-ledger")["readOnly"] = True
                    else:
                        next(v for v in volumes if v["name"] == "command-ledger")["persistentVolumeClaim"]["readOnly"] = True
                    with self.assertRaises(ValueError):
                        effective_guard_environment(broken, agent)

    def test_disabled_manifest_boundary_and_credentials(self):
        documents = list(yaml.safe_load_all((ROOT / "infrastructure/manifests/command-guard-config.yaml").read_text()))
        self.assertEqual(["ConfigMap"], [d["kind"] for d in documents])
        policy = json.loads(documents[0]["data"]["policy.json"])
        self.assertIs(False, policy["enabled"])
        for agent in ("chaos-worker", "nemesis", "hephaestus"):
            path = "chaos-worker.yaml" if agent == "chaos-worker" else agent + "-deployment.yaml"
            docs = list(yaml.safe_load_all((ROOT / "infrastructure/manifests" / path).read_text()))
            check_openapi(docs)
            effective_guard_environment(docs, agent)
            # Catch the exact original defect, an envFrom disconnect and bad mount.
            for defect in ("metadata", "envfrom", "mount"):
                broken = deepcopy(docs)
                cm = next(d for d in broken if d and d["kind"] == "ConfigMap")
                dep = next(d for d in broken if d and d["kind"] == "Deployment")
                container = dep["spec"]["template"]["spec"]["containers"][0]
                if defect == "metadata":
                    cm["metadata"]["ZD_COMMAND_POLICY_FILE"] = cm["data"].pop("ZD_COMMAND_POLICY_FILE")
                elif defect == "envfrom":
                    container["envFrom"] = []
                else:
                    container["volumeMounts"] = [m for m in container["volumeMounts"] if m["name"] != "command-policy"]
                with self.assertRaises(ValueError, msg=(agent, defect)):
                    effective_guard_environment(broken, agent)
                if defect == "metadata":
                    with self.assertRaises(ValueError, msg=(agent, "OpenAPI")):
                        check_openapi(broken)
            deployment = next(d for d in docs if d and d["kind"] == "Deployment")
            spec = deployment["spec"]["template"]["spec"]
            self.assertEqual(1, deployment["spec"]["replicas"])
            volumes = {v["name"]: v for v in spec["volumes"]}
            self.assertEqual("zd-command-policy", volumes["command-policy"]["configMap"]["name"])
            if agent == "hephaestus":
                self.assertNotIn("command-fault", volumes)
                self.assertNotIn("command-ledger", volumes)
                self.assertIs(False, spec["automountServiceAccountToken"])
                self.assertEqual("zd-heal-operator", volumes["command-operator"]["secret"]["secretName"])
            else:
                self.assertIn("persistentVolumeClaim", volumes["command-ledger"])
                self.assertNotIn("emptyDir", volumes["command-ledger"])
                self.assertNotIn("event-o", str(volumes))
                if agent == "nemesis":
                    self.assertEqual("zd-command-operator", volumes["command-operator"]["secret"]["secretName"])

    def test_production_test_lock_preserves_every_image_pin(self):
        for agent in ("nemesis", "hephaestus"):
            def pins(path):
                return dict(re.findall(r"^([a-zA-Z0-9_.-]+)==([^\s;\\]+)", path.read_text(), re.M))
            production = pins(ROOT / "agent-orchestrator" / agent / "requirements.lock")
            tested = pins(ROOT / "tests" / ("requirements-command-" + agent + ".lock"))
            for name, version in production.items():
                self.assertEqual(version, tested.get(name), (agent, name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
