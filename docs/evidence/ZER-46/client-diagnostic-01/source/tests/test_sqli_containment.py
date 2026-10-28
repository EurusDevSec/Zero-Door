"""ZER-46: fake Kubernetes CAS + disposable loopback fixture; no lab, model or external network.

No SQLi payload is needed to verify source containment. All HTTP requests are ordinary public catalog
queries or owned-order probes. Proxy/XFF in these tests is simulated, not proof of a live proxy chain.
"""
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "services/sqli-fixture"))
from containment import FilePolicy, PolicyError, decode  # noqa: E402
from hephaestus.sqli_containment import SqliContainment, Refused  # noqa: E402

spec = importlib.util.spec_from_file_location("zer46_app", os.environ.get("ZD_SQLI_APP") or ROOT / "services/sqli-fixture/app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

SCOPE, RUN, TRIAL = "zer46-test", "run_" + "1" * 32, "trl_" + "2" * 32
UID = "11111111-1111-4111-8111-111111111111"
ATTACKER, BENIGN, PROXY = "10.42.1.10", "10.42.1.11", "10.42.1.12"
ACTION, REQUEST = "act_" + "3" * 32, "4" * 32


def state(rules=None):
    return {"version": "zer46-containment/1", "scope": SCOPE, "run_id": RUN, "trial_id": TRIAL, "rules": rules or []}


def source(address=ATTACKER):
    return {"client_ip": address, "confidence": "PROXY_CHAIN", "method": "XFF_AFTER_TRUSTED"}


def observation(now=1000):
    return {"client_ip": ATTACKER, "tcp_peer": PROXY, "source_method": "XFF_AFTER_TRUSTED",
            "source_confidence": "PROXY_CHAIN", "request_id": REQUEST, "ts": now,
            "run_id": RUN, "trial_id": TRIAL}


class Conflict(Exception):
    status = 409


class FakeAPI:
    def __init__(self):
        self.doc = {"apiVersion": "v1", "kind": "ConfigMap", "metadata": {
            "name": "zer46-sqli-containment", "namespace": "zd-sqli-lab", "uid": UID,
            "resourceVersion": "1", "labels": {"zero-door.io/containment-scope": SCOPE}},
            "data": {"policy.json": json.dumps(state())}}
        self.writes, self.conflicts, self.timeout_after_write = 0, 0, False

    def read_namespaced_config_map(self, name, namespace, **kwargs):
        assert (name, namespace, kwargs["_request_timeout"]) == ("zer46-sqli-containment", "zd-sqli-lab", (2, 3))
        return copy.deepcopy(self.doc)

    def replace_namespaced_config_map(self, name, namespace, body, **kwargs):
        assert (name, namespace, kwargs["_request_timeout"]) == ("zer46-sqli-containment", "zd-sqli-lab", (2, 3))
        if self.conflicts:
            self.conflicts -= 1
            raise Conflict()
        if body["metadata"]["resourceVersion"] != self.doc["metadata"]["resourceVersion"]:
            raise Conflict()
        self.writes += 1
        self.doc = copy.deepcopy(body)
        self.doc["metadata"]["resourceVersion"] = str(int(body["metadata"]["resourceVersion"]) + 1)
        if self.timeout_after_write:
            self.timeout_after_write = False
            raise TimeoutError("ambiguous response after commit")
        return copy.deepcopy(self.doc)

    def raw(self):
        return self.doc["data"]["policy.json"].encode()


def writer(api, clock=lambda: 1000, **overrides):
    args = {"uid": UID, "scope": SCOPE, "run_id": RUN, "trial_id": TRIAL,
            "attacker_ip": ATTACKER, "benign_ip": BENIGN, "proxy_cidrs": [PROXY + "/32"], "clock": clock}
    args.update(overrides)
    return SqliContainment(api, **args)


class Backend(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()

    def block(self, backend=None, **changes):
        args = {"action_id": ACTION, "evidence": observation(), "ttl_sec": 30}
        args.update(changes)
        return (backend or writer(self.api)).block(**args)

    def test_api_acceptance_is_never_containment_verification(self):
        result = self.block()
        self.assertEqual(result["status"], "API_ACCEPTED")
        self.assertIs(result["containment_verified"], False)
        self.assertEqual(decode(self.api.raw(), SCOPE, 1000)["rules"], [result["rule"]])

    def test_restart_and_retry_preserve_original_expiry(self):
        first = self.block()
        second = self.block(writer(self.api, clock=lambda: 1010))
        self.assertTrue(second["replay"])
        self.assertEqual(first["rule"], second["rule"])
        self.assertEqual(self.api.writes, 1)

    def test_timeout_after_commit_is_reconciled_with_same_action_id(self):
        self.api.timeout_after_write = True
        with self.assertRaises(TimeoutError):
            self.block()
        self.assertTrue(self.block()["replay"])
        self.assertEqual(self.api.writes, 1)

    def test_restart_can_read_replay_after_evidence_freshness_without_renewal(self):
        first = self.block(ttl_sec=180)
        replay = self.block(writer(self.api, clock=lambda: 1070), ttl_sec=180)
        self.assertTrue(replay["replay"])
        self.assertEqual(replay["rule"], first["rule"])
        self.assertEqual(self.api.writes, 1)
        self.api = FakeAPI()
        with self.assertRaisesRegex(Refused, "SOURCE_EVIDENCE"):
            self.block(writer(self.api, clock=lambda: 1070), ttl_sec=180)
        self.assertEqual(self.api.writes, 0)

    def test_cas_conflicts_bounded_and_no_blind_overwrite(self):
        self.api.conflicts = 2
        self.block()
        self.assertEqual(self.api.writes, 1)
        api2 = FakeAPI()
        api2.conflicts = 3
        with self.assertRaisesRegex(Refused, "STATE_CONFLICT"):
            self.block(writer(api2))
        self.assertEqual(api2.writes, 0)

    def test_recreated_foreign_scope_and_trial_are_refused(self):
        for field, value in [("uid", "22222222-2222-4222-8222-222222222222"),
                             ("namespace", "target-app"), ("name", "foreign")]:
            with self.subTest(field=field):
                self.api = FakeAPI()
                self.api.doc["metadata"][field] = value
                with self.assertRaises(Refused):
                    self.block()
                self.assertEqual(self.api.writes, 0)
        for field in ("scope", "run_id", "trial_id"):
            self.api = FakeAPI()
            changed = state()
            changed[field] = "foreign"
            self.api.doc["data"]["policy.json"] = json.dumps(changed)
            with self.assertRaises(Refused):
                self.block()

    def test_wrong_unknown_stale_or_forged_source_evidence_is_refused(self):
        for changes in ({"client_ip": BENIGN}, {"source_confidence": "UNKNOWN"},
                        {"source_method": "DIRECT_PEER"}, {"tcp_peer": BENIGN},
                        {"ts": 900}, {"ts": 1001}, {"ts": float("nan")}, {"request_id": "unbound"},
                        {"run_id": "foreign"}, {"trial_id": "foreign"}):
            with self.subTest(changes=changes):
                e = observation()
                e.update(changes)
                with self.assertRaises(Refused):
                    self.block(evidence=e)
        self.assertEqual(self.api.writes, 0)

    def test_no_wildcards_proxy_or_benign_as_attacker_and_bounded_ttl(self):
        for overrides in ({"attacker_ip": "0.0.0.0"}, {"attacker_ip": "8.8.8.8"},
                          {"attacker_ip": BENIGN}, {"attacker_ip": PROXY},
                          {"proxy_cidrs": ["10.42.0.0/16"]}, {"proxy_cidrs": []}):
            with self.assertRaises(Refused):
                writer(self.api, **overrides)
        for ttl in (0, 301, True, "30"):
            with self.assertRaises(Refused):
                self.block(ttl_sec=ttl)

    def test_action_conflict_and_rule_budget_do_not_change_state(self):
        self.block()
        with self.assertRaisesRegex(Refused, "ACTION_CONFLICT"):
            self.block(ttl_sec=31)
        base = json.loads(self.api.raw())["rules"][0]
        full = [dict(base, action_id="act_" + f"{i:032x}") for i in range(32)]
        self.api.doc["data"]["policy.json"] = json.dumps(state(full))
        with self.assertRaisesRegex(Refused, "RULE_BUDGET"):
            self.block()
        self.assertEqual(self.api.writes, 1)

    def test_expired_cleanup_survives_restart_without_renewing_old_observation(self):
        self.block()
        self.assertEqual(writer(self.api, clock=lambda: 1010).cleanup()["removed"], 0)
        cleanup = writer(self.api, clock=lambda: 1030).cleanup()
        self.assertEqual(cleanup["removed"], 1)
        self.assertIs(cleanup["cleanup_verified"], False)
        with self.assertRaisesRegex(Refused, "ACTION_EXPIRED"):
            self.block(writer(self.api, clock=lambda: 1030))
        self.assertEqual(json.loads(self.api.raw())["rules"], [])

    def test_runner_cleanup_is_explicit_and_foreign_uid_cannot_be_cleaned(self):
        self.block()
        self.assertEqual(writer(self.api).cleanup(expired_only=False)["removed"], 1)
        self.api.doc["metadata"]["uid"] = "foreign"
        with self.assertRaises(Refused):
            writer(self.api).cleanup(expired_only=False)

    def test_corrupt_duplicate_or_oversized_state_is_refused(self):
        for raw in ('{"version":1,"version":2}', '[]', '{', 'x' * 32769):
            self.api.doc["data"]["policy.json"] = raw
            with self.assertRaises(Refused):
                self.block()
        self.assertEqual(self.api.writes, 0)


class Enforcement(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "policy.json"
        self.api = FakeAPI()
        writer(self.api).block(action_id=ACTION, evidence=observation(), ttl_sec=30)
        self.path.write_bytes(self.api.raw())

    def tearDown(self):
        self.dir.cleanup()

    def test_exact_client_block_and_benign_share_same_proxy(self):
        p = FilePolicy(self.path, SCOPE)
        self.assertTrue(p.check(source(), now=1000)["blocked"])
        self.assertFalse(p.check(source(BENIGN), now=1000)["blocked"])

    def test_ttl_boundary_and_reader_restart_without_healer_or_timer(self):
        self.assertTrue(FilePolicy(self.path, SCOPE).check(source(), 1029.999)["blocked"])
        self.assertFalse(FilePolicy(self.path, SCOPE).check(source(), 1030)["blocked"])
        self.assertEqual(len(json.loads(self.path.read_bytes())["rules"]), 1)  # expiry != storage cleanup

    def test_file_replacement_observed_no_cache(self):
        p = FilePolicy(self.path, SCOPE)
        self.assertTrue(p.check(source(), 1000)["blocked"])
        replacement = self.path.with_suffix(".new")
        replacement.write_text(json.dumps(state()))
        replacement.replace(self.path)
        self.assertFalse(p.check(source(), 1000)["blocked"])

    def test_unknown_or_inconsistent_source_never_becomes_benign(self):
        for s in ({}, {"client_ip": ATTACKER}, dict(source(), confidence="UNKNOWN"),
                  dict(source(), method="DIRECT_PEER"), source("0.0.0.0")):
            with self.assertRaises(PolicyError):
                FilePolicy(self.path, SCOPE).check(s, 1000)

    def test_missing_invalid_wrong_scope_and_oversize_file_fail_closed(self):
        for raw in ('[]', '{', json.dumps(dict(state(), scope="other")), 'x' * 32769):
            self.path.write_text(raw)
            with self.assertRaisesRegex(PolicyError, "CONTAINMENT_STATE_UNAVAILABLE"):
                FilePolicy(self.path, SCOPE).check(source(), 1000)
        self.path.unlink()
        with self.assertRaises(PolicyError):
            FilePolicy(self.path, SCOPE).check(source(), 1000)


class HTTPBoundary(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "policy.json"
        self.path.write_text(json.dumps(state()))
        self.logs = io.StringIO()
        app.LOG = self.logs
        self.start()
        self.opener = build_opener(ProxyHandler({}))  # no host proxy / external URL is used

    def start(self, enabled=True):
        env = {"ZD_SQLI_DB_DIR": self.dir.name, "ZD_SQLI_PORT": "0", "ZD_SQLI_HOST": "127.0.0.1",
               "ZD_SQLI_PROFILE": "safe", "ZD_SQLI_TOPOLOGY": "proxied", "ZD_SQLI_TRUSTED_PROXIES": "127.0.0.1/32",
               "ZD_SQLI_SEED": str(ROOT / "tests/fixtures/zer41/seed.json")}
        if enabled:
            env.update(ZD_SQLI_CONTAINMENT_FILE=str(self.path), ZD_SQLI_CONTAINMENT_SCOPE=SCOPE)
        self.config = app.Config(env)
        with redirect_stderr(io.StringIO()):
            self.server, self.store, *_ = app.build_server(self.config)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = "http://127.0.0.1:" + str(self.server.server_address[1])

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def tearDown(self):
        self.stop()
        app.LOG = None
        self.dir.cleanup()

    def request(self, path="/fixture/catalog/search?category=electronics", address=ATTACKER, method="GET", body=None):
        headers = {} if address is None else {"X-Forwarded-For": address}
        if body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(body).encode()
        req = Request(self.origin + path, data=body, method=method, headers=headers)
        try:
            response = self.opener.open(req, timeout=4)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def install_block(self):
        now = int(time.time())
        self.path.write_text(json.dumps(state([{"action_id": ACTION, "client_ip": ATTACKER,
            "created_at": now, "expires_at": now + 30, "request_id": REQUEST}])))

    def test_blocks_all_fixture_verbs_keeps_benign_and_health(self):
        self.install_block()
        self.assertEqual(self.request()[0], 403)
        self.assertEqual(self.request("/fixture/orders", method="POST", body={"item": "x", "note": "n"})[0], 403)
        self.assertEqual(self.request("/fixture/orders/owned", method="DELETE")[0], 403)
        self.assertEqual(self.request(address=BENIGN)[0], 200)
        self.assertEqual(self.request("/health", address=None)[0], 200)
        rows = [json.loads(line) for line in self.logs.getvalue().splitlines()]
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({r["request_id"] for r in rows}), 5)
        self.assertEqual(rows[0]["action_ids"], [ACTION])
        self.assertEqual(rows[0]["enforcement_point"], "sqli-fixture/trusted-client")
        self.assertNotIn("profile", rows[0])

    def test_unknown_and_bad_state_are_503_not_block_or_success(self):
        self.assertEqual(self.request(address=None)[0], 503)
        self.path.write_text("broken")
        status, body = self.request(address=BENIGN)
        self.assertEqual((status, body["error"]), (503, "CONTAINMENT_STATE_UNAVAILABLE"))
        self.assertEqual(self.request("/ready", address=None)[0], 503)
        self.assertEqual(self.request("/health", address=None)[0], 200)

    def test_forged_leftmost_forward_does_not_switch_blocked_source(self):
        self.install_block()
        self.assertEqual(self.request(address=BENIGN + ", " + ATTACKER)[0], 403)
        self.assertEqual(self.request(address=ATTACKER + ", " + BENIGN)[0], 200)

    def test_process_restart_retains_policy_and_order_reset_does_not_clear_it(self):
        self.install_block()
        self.store.reset_orders()
        self.stop()
        self.start()
        self.assertEqual(self.request()[0], 403)
        self.assertEqual(self.request(address=BENIGN)[0], 200)
        self.path.write_text(json.dumps(state()))  # simulated observed runner cleanup projection
        self.assertEqual(self.request()[0], 200)

    def test_default_disabled_preserves_existing_fixture_behavior(self):
        self.install_block()
        self.stop()
        self.start(enabled=False)
        self.assertEqual(self.request()[0], 200)

    def test_expired_stored_rule_unblocks_after_restart_without_cleanup(self):
        now = int(time.time())
        self.path.write_text(json.dumps(state([{"action_id": ACTION, "client_ip": ATTACKER,
            "created_at": now - 40, "expires_at": now - 10, "request_id": REQUEST}])))
        self.stop()
        self.start()
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(len(json.loads(self.path.read_bytes())["rules"]), 1)


class Packaging(unittest.TestCase):
    def test_candidate_is_named_resource_rbac_and_default_fixture_stays_disabled(self):
        import yaml
        sys.path.insert(0, str(ROOT / "tests"))
        from check_guard_manifests import check
        candidate = list(yaml.safe_load_all((ROOT / "infrastructure/manifests/sqli-containment-lab.yaml").read_text()))
        check(candidate)
        cm, role, binding = candidate
        self.assertEqual([d["kind"] for d in candidate], ["ConfigMap", "Role", "RoleBinding"])
        self.assertTrue(all(d["metadata"]["namespace"] == "zd-sqli-lab" for d in candidate))
        self.assertEqual(role["rules"], [{"apiGroups": [""], "resources": ["configmaps"],
            "resourceNames": ["zer46-sqli-containment"], "verbs": ["get", "update"]}])
        self.assertEqual(binding["subjects"], [{"kind": "ServiceAccount", "name": "hephaestus-sa", "namespace": "zero-door"}])
        self.assertEqual(json.loads(cm["data"]["policy.json"])["rules"], [])
        fixture = (ROOT / "infrastructure/manifests/sqli-fixture.yaml").read_text()
        self.assertNotIn("ZD_SQLI_CONTAINMENT_FILE", fixture)
        docker = (ROOT / "services/sqli-fixture/Dockerfile").read_text()
        self.assertIn("COPY containment.py .", docker)


if __name__ == "__main__":
    unittest.main()
