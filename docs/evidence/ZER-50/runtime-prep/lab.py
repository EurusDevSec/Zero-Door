"""Trusted native reader/probe for ZER-50. Import is inert; only gated child entry runs."""
import argparse
import asyncio
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import quote, urlsplit
import uuid

import run as supervisor

ROOT, OUT, PREP = supervisor.ROOT, supervisor.OUT, supervisor.PREP
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from event_pipeline.contract import Producer, new_id, validate
from event_pipeline.llm import Adapter, HttpxTransport, Limits, RunBudget
from hephaestus.recovery import Healer, Journal
from hephaestus.sqli_containment import NAME, NAMESPACE, SqliContainment


def claim_work():
    supervisor.admit(OUT / "authorization.json")
    started = json.loads((OUT / "started.json").read_bytes())
    if started.get("head") != supervisor.HEAD:
        raise ValueError("WORK_START_PIN")
    with (OUT / "work-claimed.json").open("x", encoding="utf8") as marker:
        marker.write(json.dumps({"at": time.time(), "pid": os.getpid(), "restart_allowed": False}))
        marker.flush(); os.fsync(marker.fileno())


def kube_config_pin():
    import yaml
    if os.environ.get("DOCKER_HOST"):
        raise ValueError("DOCKER_HOST_FORBIDDEN")
    path = Path(os.environ.get("KUBECONFIG") or Path.home() / ".kube/config")
    raw = yaml.safe_load(path.read_text(encoding="utf8"))
    ctx = next(c["context"] for c in raw["contexts"] if c["name"] == "k3d-zero-door")
    cluster = next(c["cluster"] for c in raw["clusters"] if c["name"] == ctx["cluster"])
    user = next(c["user"] for c in raw["users"] if c["name"] == ctx["user"])
    if (cluster["server"] != "https://127.0.0.1:7356" or cluster.get("proxy-url")
            or any(k in user for k in ("exec", "auth-provider"))):
        raise ValueError("LOCAL_STATIC_KUBE_PIN")
    return path


def load_fixture_driver():
    spec = importlib.util.spec_from_file_location("zer50_fixture_driver",
        ROOT / "docs/evidence/ZER-46/runtime-prep/run_agent_fixture.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    for module in (driver, driver.cached, driver.cached.parent,
                   driver.cached.parent.full, driver.cached.parent.full.base):
        module.OUT = OUT
    spec = importlib.util.spec_from_file_location("zer50_renderer", PREP / "render.py")
    renderer = importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)
    driver.cached.parent.full.renderer = renderer
    return driver


def project(context, detection, fixture_uid, raw, http, *, pod_uid, ref, at):
    """Bind native response to raw O access; H profile/seed answers never enter model input."""
    request, response = http["request"], http["response"]
    if (pod_uid != fixture_uid or detection["run_id"] != context["run_id"]
            or detection["trial_id"] != context["trial_id"]
            or not re.fullmatch(r"[a-f0-9]{32}", response.get("request_id") or "")
            or response["request_id"] != raw.get("request_id")
            or request["correlation"] != raw.get("correlation_id")
            or request["method"] != raw.get("method") or raw.get("method") != "GET"
            or urlsplit(request["path"]).path != raw.get("path")
            or raw.get("path") != "/fixture/catalog/search"
            or response.get("status") != raw.get("status") or raw.get("status") != 200
            or raw.get("delivered", True) is not True
            or not response["begin"] <= raw["ts"] <= response["end"] <= at
            or not 0 <= at - raw["ts"] <= 60):
        raise ValueError("NATIVE_ACCESS_JOIN")
    rows = response["body"].get("results")
    if (type(rows) is not list or response["body"].get("count") != len(rows)
            or raw.get("rows") != len(rows)
            or raw.get("restricted_rows") != sum(r.get("visibility") == "restricted" for r in rows)):
        raise ValueError("NATIVE_RESPONSE_CONTENT_JOIN")
    fields = ("request_id", "ts", "client_ip", "tcp_peer", "source_method", "source_confidence",
              "method", "path", "status", "rows", "restricted_rows")
    return {**{k: raw[k] for k in fields}, "delivered": True, "ref": ref,
        "run_id": context["run_id"], "trial_id": context["trial_id"], "fixture_uid": fixture_uid,
        "detection_event_id": detection["event_id"]}


def receipt_ok(receipt, detected, *, positive):
    traces = receipt.get("model_events", [])
    budget = receipt["budget"]
    expected = {"ACTION_COMPLETED"} if positive else {"NO_ACTION", "ABSTAIN"}
    return (receipt["status"] in expected and receipt["decision_source"] == "LLM"
        and not receipt["fallback"] and receipt["plan"]["evidence_ids"] == [detected["event_id"]]
        and receipt["detection_event_id"] == detected["event_id"]
        and not validate(receipt["decision"]) and len(traces) == 1 and not validate(traces[0])
        and traces[0]["payload"]["outcome"] == "OK" and traces[0]["payload"]["model"] == "gpt-6-luna"
        and traces[0]["causation_id"] == detected["event_id"]
        and budget["attempts_dispatched"] == (2 if positive else 1)
        and budget["cost_estimate_complete"] and not budget["blocked"]
        and budget["unknown_usage_attempts"] == 0 and budget["reserved_estimate_usd"] <= .01
        and budget["known_output_tokens"] <= (512 if positive else 256)
        and (receipt["action_state"]["terminal"]["status"] == "SUCCESS"
             and receipt["api_result"]["replay"] is False if positive
             else receipt["api_result"] is None and receipt["action_id"] is None))


def make_lab():
    driver = load_fixture_driver()

    class Lab(driver.Lab):
        def __init__(self):
            super().__init__()
            self.deadline = time.monotonic() + 600
            self.work_end = self.deadline - 20  # Outer supervisor owns separate 5-minute cleanup.
            self.fixture_uid = None
            self.model_calls = 0
            self.probe_end = None

        def check(self):
            super().check()
            if not self.cleanup_mode and self.probe_end is not None and time.monotonic() >= self.probe_end:
                raise ValueError("NATIVE_PROBE_DEADLINE")

        def save(self, name, value):
            if getattr(self, "cleanup_mode", False) and name == "resource-samples.json":
                name = "cleanup-resource-samples.json"
            return super().save(name, value)

        def checkpoint(self):
            self.save("state.json", {k: getattr(self, k) for k in
                ("owner", "run_id", "trial_id", "creation_attempted", "ns_uid", "cm_uid",
                 "fixture_uid", "fixture_deployment_attempted", "fixture_http", "tcp_checks")})

        def pod(self, name=None):
            pod = super().pod(name)
            if self.fixture_uid is not None and (name is None or name.startswith("sqli-fixture-")):
                if pod["metadata"]["uid"] != self.fixture_uid:
                    raise ValueError("FIXTURE_UID_CHANGED")
            return pod

        def execute(self):
            supervisor.verify_sources()
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("PROVIDER_KEY_MISSING")
            # Verify endpoint and auth before kubectl or any dynamic credential/plugin invocation.
            kube_config_pin()
            if self.command(["git", "rev-parse", "HEAD"]).stdout.decode().strip() != supervisor.HEAD:
                raise ValueError("HEAD_DRIFT")
            if self.command(["docker", "context", "show"]).stdout.decode().strip() != "desktop-linux":
                raise ValueError("DOCKER_CONTEXT")
            nodes = json.loads(self.kube("get", "nodes", "-o", "json").stdout)["items"]
            if ({n["metadata"]["name"] for n in nodes} != {"k3d-zero-door-server-0", self.node}
                    or any(not any(c["type"] == "Ready" and c["status"] == "True"
                        for c in n["status"]["conditions"]) for n in nodes)):
                raise ValueError("NODE_PROFILE")
            if self.kube("get", "namespace", NAMESPACE, "--ignore-not-found", "-o", "name").stdout.strip():
                raise ValueError("NAMESPACE_ALREADY_EXISTS")
            self.before = self.snapshot("before")
            deployments = [x for x in self.before["items"] if x["kind"] == "Deployment"]
            target = [x for x in deployments if x["metadata"]["namespace"] == "target-app"]
            expected = {"cartservice", "checkoutservice", "currencyservice", "emailservice", "frontend",
                        "paymentservice", "productcatalogservice", "redis-cart", "shippingservice"}
            if ({x["metadata"]["name"] for x in target} != expected or any(x["spec"]["replicas"] != 1
                    or x.get("status", {}).get("availableReplicas", 0) != 1 for x in target)
                    or any(x["spec"]["replicas"] != 0 for x in deployments if x["metadata"]["namespace"] == "zero-door")):
                raise ValueError("SHARED_PROFILE_OR_READINESS")
            pvcs = [x for x in self.before["items"] if x["kind"] == "PersistentVolumeClaim"]
            if len(pvcs) != 3 or any(x.get("status", {}).get("phase") != "Bound" for x in pvcs):
                raise ValueError("PVC_PROFILE")
            start = time.monotonic()
            for i in range(25):
                self.wait(start + i * 5); self.resources()
            self.thread = threading.Thread(target=self.watch, daemon=True); self.thread.start()
            self.ensure_cache()  # Cached agent-node driver overrides build/import/pull.
            after = self.snapshot("after-preflight")
            if self.specs(after) != self.specs(self.before) or self.restarts(after) != self.restarts(self.before):
                raise ValueError("PREFLIGHT_DRIFT")
            self.save("preflight.json", {"status": "GATE_PASSED", "resource_samples": len(self.samples)})

        def component(self):
            self.checkpoint()
            docs = driver.cached.parent.full.renderer.render(self.owner, self.run_id, self.trial_id,
                "10.42.255.254", node=self.node)
            namespace = next(d for d in docs if d["kind"] == "Namespace")
            self.save("namespace-create.json", namespace)
            if self.kube("get", "namespace", NAMESPACE, "--ignore-not-found", "-o", "name").stdout.strip():
                raise ValueError("NAMESPACE_ALREADY_EXISTS")
            self.creation_attempted = True; self.checkpoint()  # Durable before ambiguous create.
            doc = json.loads(self.kube("create", "-f", str(OUT / "namespace-create.json"), "-o", "json").stdout)
            self.ns_uid = doc["metadata"]["uid"]; self.checkpoint()
            bootstrap = [d for d in docs if d["kind"] != "Namespace" and not
                (d["metadata"]["name"] in {"sqli-fixture", "sqli-fixture-config"} and d["kind"] in {"Deployment", "ConfigMap"})]
            self.apply_bootstrap(bootstrap)
            self.run_fixture_protocol()

        def http(self, *args, **kwargs):
            if self.fixture_http >= 9:
                raise ValueError("ZER50_HTTP_BUDGET")
            self.save("http-intent-%03d.json" % (self.fixture_http + 1), {
                "at": time.time(), "who": args[0], "request_number": self.fixture_http + 1})
            result = super().http(*args, **kwargs)
            self.checkpoint()
            return result

        def logs(self, pod=None):
            pod = pod or self.pod()
            records = super().logs(pod)  # Saves exact kubectl stdout in raw command receipt.
            after = self.pod(pod["metadata"]["name"])
            if after["metadata"]["uid"] != pod["metadata"]["uid"]:
                raise ValueError("LOG_UID_CHANGED")
            return records

        def row(self, who, **kwargs):
            before = self.pod()["metadata"]["uid"]
            response, access = self.http(who, **kwargs)
            after = self.pod()["metadata"]["uid"]
            if before != after or after != self.fixture_uid:
                raise ValueError("HTTP_FIXTURE_UID_CHANGED")
            ref = "http-%03d.json" % self.fixture_http
            http = json.loads((OUT / ref).read_bytes())
            return {"pod_uid": after, "ref": ref, "http": http, "access": access}

        def run_fixture_protocol(self):
            self.addresses = {who: self.pod("zer46-source-" + who)["status"]["podIP"] for who in ("a", "b")}
            pods = json.loads(self.kube("-n", NAMESPACE, "get", "pods", "-o", "json").stdout)["items"]
            proxy = [p for p in pods if p["metadata"]["labels"].get("app") == "zer46-private-ingress"]
            if len(proxy) != 1:
                raise ValueError("PROXY_IDENTITY")
            self.addresses["proxy"] = proxy[0]["status"]["podIP"]
            if len(set(self.addresses.values())) != 3:
                raise ValueError("SOURCE_SEPARATION")
            self.save("source-addresses.json", self.addresses)
            final = driver.cached.parent.full.renderer.render(self.owner, self.run_id, self.trial_id,
                self.addresses["proxy"], node=self.node)
            config = next(d for d in final if (d["kind"], d["metadata"]["name"]) == ("ConfigMap", "sqli-fixture-config"))
            config["data"]["ZD_SQLI_PROFILE"] = "vulnerable"  # Existing opt-in local fixture, no new payload.
            self.fixture_deployment_attempted = True; self.checkpoint()
            self.kube("apply", "-f", self.write_yaml("fixture.yaml", [d for d in final if
                (d["kind"], d["metadata"]["name"]) in {("Deployment", "sqli-fixture"), ("ConfigMap", "sqli-fixture-config")}]))
            fixture = self.release()
            self.fixture_uid = fixture["metadata"]["uid"]; self.save("fixture-initial.json", fixture)
            self.isolation(fixture)  # Exactly two direct TCP-denial probes.
            self.expect("a", 200)  # Baseline; no extra diagnostic HTTP retry.
            cm = self.cm(); self.cm_uid = cm["metadata"]["uid"]
            self.target_pins = {"uid": self.cm_uid, "scope": self.owner, "run_id": self.run_id,
                "trial_id": self.trial_id, "attacker_ip": self.addresses["a"], "benign_ip": self.addresses["b"],
                "proxy_cidrs": [self.addresses["proxy"] + "/32"]}
            self.checkpoint()
            asyncio.run(self.cases())

        def native_api(self):
            from kubernetes import client, config
            config.load_kube_config(config_file=str(kube_config_pin()), context="k3d-zero-door")
            cfg = client.Configuration.get_default_copy()
            if cfg.host != "https://127.0.0.1:7356":
                raise ValueError("API_HOST_PIN")
            cfg.retries = 0; cfg.proxy = None
            api = client.CoreV1Api(client.ApiClient(cfg))
            lab = self
            class Bounded:
                api_client = api.api_client
                writes = 0
                def read_namespaced_config_map(self, name, namespace, **kw):
                    lab.check()
                    if (name, namespace) != (NAME, NAMESPACE):
                        raise ValueError("API_TARGET")
                    return api.read_namespaced_config_map(name, namespace, **kw)
                def replace_namespaced_config_map(self, name, namespace, body, **kw):
                    lab.check()
                    if (name, namespace) != (NAME, NAMESPACE) or self.writes >= 3:
                        raise ValueError("API_WRITE_BOUND")
                    self.writes += 1
                    return api.replace_namespaced_config_map(name, namespace, body, **kw)
            return Bounded(), api.api_client

        async def probe(self, result):
            self.action = result["rule"]["action_id"]
            self.probe_end = time.monotonic() + 115
            def collect():
                # Read-only projection wait precedes six sequential functional requests.
                self.wait_projection(self.cm(), seconds=85)
                a = self.row("a")
                b = [self.row("b")]
                nonce = uuid.uuid4().hex
                b.append(self.row("b", path="/fixture/orders", method="POST",
                    body={"item": "benign-lab-item", "note": nonce}))
                ref = b[-1]["http"]["response"]["body"]["order_ref"]
                if not re.fullmatch(r"[a-f0-9]{32}", ref):
                    raise ValueError("ORDER_REF")
                for method in ("GET", "DELETE", "GET"):
                    b.append(self.row("b", path="/fixture/orders/" + ref, method=method))
                pod = self.pod()
                ready = any(c["type"] == "Ready" and c["status"] == "True" for c in pod["status"]["conditions"])
                return {"attacker": a, "benign": b, "fixture": {"uid": pod["metadata"]["uid"], "ready": ready}}
            task = asyncio.create_task(asyncio.to_thread(collect))
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                await task  # Drain owned native operations; outer Job still supplies hard bound.
                raise
            finally:
                self.probe_end = None

        async def cases(self):
            budget = RunBudget(self.run_id, max_calls=2, max_reserved_tokens=30000,
                max_estimated_usd=.01, duration_s=240)
            adapter = Adapter(HttpxTransport(os.environ["OPENAI_API_KEY"]), budget,
                limits=Limits(attempts=1, timeout_s=20, deadline_s=25, retry_delay_s=0, max_output_tokens=256))
            api, connection = self.native_api()
            try:
                for label, positive in (("C0", False), ("C1", True)):
                    self.check()
                    before = self.cm()
                    category = json.loads((ROOT / "tests/fixtures/zer41/expected.json").read_bytes())["injection"]["category"]
                    row = await asyncio.to_thread(self.row, "a" if positive else "b",
                        path="/fixture/catalog/search?category=" + quote(category if positive else "electronics", safe=""))
                    context = {"run_id": self.run_id, "trial_id": self.trial_id, "incident_id": new_id("inc"),
                        "group": "B2", "method_version": "zer50-native/1",
                        "config_ref": "sha256:" + supervisor.sha(PREP / "source-manifest.json")}
                    detected = Producer("detector", "zer50-trusted-reader/1", {
                        "clock_id": "host", "clock_source": "UNKNOWN", "resolution_ms": None}).event(context,
                        "DETECTED", {"rule_id": "SUSPICIOUS_LOG", "rule_version": "1", "signature": "SQLI/fixture",
                        "metric": "log_pattern_match", "value": int(row["access"]["restricted_rows"] > 0),
                        "threshold": 0, "severity": "WARNING",
                        "description": "Native access nominated for functional containment decision"}, "o.alert",
                        target={"namespace": NAMESPACE, "service": "sqli-fixture", "flow": None}, alert_id=new_id("alt"))
                    access = project(context, detected, self.fixture_uid, row["access"], row["http"],
                        pod_uid=row["pod_uid"], ref=row["ref"], at=time.time())
                    if bool(access["restricted_rows"]) != positive:
                        raise ValueError("CONTROL_OBSERVATION_NOT_MET")
                    self.save(label + "-input.json", {"detection": detected, "access": access,
                        "raw_join_sha256": supervisor.sha(OUT / ("join-%03d.json" % self.fixture_http)),
                        "http_sha256": supervisor.sha(OUT / row["ref"])})
                    output = OUT / label; output.mkdir()
                    journal = Journal(output, context)
                    try:
                        healer = Healer(adapter, context, api=api, pins=self.target_pins,
                            fixture_uid=self.fixture_uid, journal=journal, probe=self.probe,
                            ttl_sec=180, probe_timeout_s=120)
                        receipt = await healer.run(detected, access)
                    finally:
                        journal.close()
                        self.model_calls = budget.summary()["attempts_dispatched"]
                        self.save("model-budget.json", budget.summary())
                    self.save(label + "-receipt.json", receipt)
                    if not receipt_ok(receipt, detected, positive=positive):
                        raise ValueError(label + "_AC_NOT_MET")
                    if not positive and (api.writes != 0 or before != self.cm()):
                        raise ValueError("BENIGN_OVER_HEALING")
                self.save("functional-observed.json", {"status": "OBSERVED_PENDING_REVIEW",
                    "fixture_http": self.fixture_http, "tcp_checks": self.tcp_checks,
                    "model_budget": budget.summary(), "api_replace_attempts": api.writes})
            finally:
                connection.close()

        def cleanup_owned(self):
            self.cleanup_mode = True; self.stop.set()
            self.deadline = time.monotonic() + 265
            errors = []
            state_path = OUT / "state.json"
            state = json.loads(state_path.read_bytes()) if state_path.exists() else {}
            if state:
                for k, v in state.items():
                    setattr(self, k, v)
            self.seq = 10000  # Preserve work raw receipts.
            try:
                if state.get("creation_attempted"):
                    raw = self.kube("get", "namespace", NAMESPACE, "--ignore-not-found", "-o", "json").stdout
                    if raw.strip():
                        ns = json.loads(raw)
                        if (ns["metadata"]["labels"].get("zero-door.io/run") != state["owner"]
                                or state.get("ns_uid") and ns["metadata"]["uid"] != state["ns_uid"]):
                            raise ValueError("CLEANUP_OWNER_UID")
                        self.save("namespace-delete-options.json", {"apiVersion": "v1", "kind": "DeleteOptions",
                            "preconditions": {"uid": ns["metadata"]["uid"]}})
                        self.kube("delete", "--raw", "/api/v1/namespaces/" + NAMESPACE,
                            "-f", str(OUT / "namespace-delete-options.json"))
                        self.command(["kubectl", "--context", "k3d-zero-door", "--request-timeout=12s", "wait",
                            "--for=delete", "namespace/" + NAMESPACE, "--timeout=150s"], timeout=155)
                absent = not self.kube("get", "namespace", NAMESPACE, "--ignore-not-found", "-o", "name").stdout.strip()
                after = self.shared(self.snapshot("after"))
                before_path = OUT / "before.json"
                before = json.loads(before_path.read_bytes()) if before_path.exists() else None
                specs = before is not None and self.specs(after) == self.specs(before)
                restarts = before is not None and self.restarts(after) == self.restarts(before)
                self.resources()
            except Exception as error:
                errors.append(type(error).__name__ + ":" + str(error))
                absent = specs = restarts = False
            result = {"namespace_absent": absent, "rules_and_owned_orders_removed_by_namespace_deletion": absent,
                "shared_specs_preserved": specs, "shared_restarts_preserved": restarts, "errors": errors,
                "provider_calls": 0, "fixture_http": 0, "business_recovery_claim": False,
                "verdict": "CLEAN" if absent and specs and restarts and not errors else "INCOMPLETE"}
            self.save("cleanup.json", result)
            return result

    return Lab()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--work", action="store_true")
    group.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    if sys.stdin.buffer.readline(4) != b"GO\n":
        raise ValueError("SUPERVISOR_GATE_REQUIRED")
    if args.work:
        claim_work()  # Direct child invocation cannot bypass approval/replay admission.
    supervisor.verify_sources()
    kube_config_pin()  # Also required for the independent cleanup process.
    lab = make_lab()
    if args.cleanup:
        return 0 if lab.cleanup_owned()["verdict"] == "CLEAN" else 1
    error = None
    try:
        lab.execute(); lab.component()
    except BaseException as failure:
        error = type(failure).__name__ + ":" + str(failure) if isinstance(failure, ValueError) else type(failure).__name__
    finally:
        lab.stop.set()
        if hasattr(lab, "thread"):
            lab.thread.join(timeout=10)
        if lab.failure:
            error = error or "RESOURCE_OR_SHARED_GUARD"
        budget_path = OUT / "model-budget.json"
        budget = json.loads(budget_path.read_bytes()) if budget_path.exists() else None
        lab.save("work-result.json", {"status": "NOT_MET" if error else "OBSERVED_PENDING_REVIEW",
            "error": error, "guard_failures": lab.failure, "provider_calls": budget["attempts_dispatched"] if budget else 0,
            "fixture_http": lab.fixture_http, "tcp_checks": lab.tcp_checks, "benchmark_eligible": False})
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
