"""ZER-16 action state, probe joins, terminal/deadline and immutable runtime09 replay; no network."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
from hephaestus.sqli_action_state import SqliActionState  # noqa: E402
from hephaestus.sqli_containment import Refused  # noqa: E402

POD = "11111111-1111-4111-8111-111111111111"
NEW = "22222222-2222-4222-8222-222222222222"
PINS = {"uid": "33333333-3333-4333-8333-333333333333", "scope": "zer16-test",
        "run_id": "run_" + "1" * 32, "trial_id": "trl_" + "2" * 32,
        "attacker_ip": "10.42.0.10", "benign_ip": "10.42.0.11", "proxy_cidrs": ["10.42.0.12/32"]}
RULE = {"action_id": "act_" + "3" * 32, "client_ip": PINS["attacker_ip"],
        "created_at": 1000, "expires_at": 1180, "request_id": "4" * 32}
API = {"status": "API_ACCEPTED", "rule": RULE, "containment_verified": False}


def monitor(**kw):
    return SqliActionState(copy.deepcopy(API), copy.deepcopy(PINS), fixture_uid=POD,
                           accepted_at=1001, timeout_s=60, **kw)


def probes(pod=POD, offset=0):
    order = "5" * 32
    stored = {"order_ref": order, "item": "synthetic-item", "note": "synthetic-note", "status": "STORED"}
    cases = [("GET", "/fixture/catalog/search", 403, {"error": "SOURCE_BLOCKED"}, True),
             ("GET", "/fixture/catalog/search", 200, {"count": 1, "results": [{"sku": "synthetic"}]}, False),
             ("POST", "/fixture/orders", 201, stored, False),
             ("GET", "/fixture/orders/" + order, 200, stored, False),
             ("DELETE", "/fixture/orders/" + order, 200, {"deleted": 1}, False),
             ("GET", "/fixture/orders/" + order, 404, {"error": "NOT_FOUND"}, False)]
    out = []
    for n, (method, path, status, body, blocked) in enumerate(cases, 1):
        request_id, correlation = f"{n + offset:032x}", f"{n + offset + 100:032x}"
        request = {"method": method, "path": path, "correlation": correlation,
                   "body": {"item": "synthetic-item", "note": "synthetic-note"} if method == "POST" else None}
        response = {"status": status, "body": copy.deepcopy(body), "request_id": request_id,
                    "begin": 1002 + n + offset, "end": 1002.5 + n + offset}
        access = {"request_id": request_id, "correlation_id": correlation, "method": method, "path": path,
                  "ts": 1002.2 + n + offset, "status": status, "client_ip": PINS["attacker_ip" if blocked else "benign_ip"],
                  "tcp_peer": "10.42.0.12", "source_method": "XFF_AFTER_TRUSTED", "source_confidence": "PROXY_CHAIN",
                  "enforcement_point": "sqli-fixture/trusted-client", "blocked": blocked,
                  "action_ids": [RULE["action_id"]] if blocked else [], "policy_sha256": "a" * 64}
        out.append({"http": {"request": request, "response": response}, "access": access,
                    "pod_uid": pod, "ref": f"synthetic/probe-{n + offset}"})
    return out


def observe(state, rows=None, **kw):
    rows = probes() if rows is None else rows
    return state.observe(rows[0], rows[1:], fixture={"uid": POD, "ready": True}, now=1010, **kw)


class ActionState(unittest.TestCase):
    def test_api_ack_alone_is_not_action_or_recovery(self):
        state = monitor().poll(1010)
        self.assertEqual("API_ACCEPTED", state["phase"])
        self.assertIsNone(state["terminal"])
        self.assertEqual("EXTERNAL_PROBE_REQUIRED", state["recovery_verification"])

    def test_joined_block_and_benign_crud_complete_action_not_recovery(self):
        state = observe(monitor())
        self.assertEqual("ACTION_COMPLETED", state["phase"])
        self.assertEqual("SUCCESS", state["terminal"]["status"])
        self.assertTrue(state["terminal"]["postcondition"]["satisfied"])
        self.assertEqual("UNPROVEN", state["causal_attribution"])
        self.assertEqual("EXTERNAL_PROBE_REQUIRED", state["recovery_verification"])

    def test_timeout_is_terminal_and_late_success_cannot_replace_it(self):
        mon = monitor()
        self.assertEqual("TIMEOUT", mon.poll(1061)["terminal"]["status"])
        state = mon.observe(*[probes()[0], probes()[1:]], fixture={"uid": POD, "ready": True}, now=1062)
        self.assertEqual("TIMEOUT", state["terminal"]["status"])

    def test_deadline_boundary_does_not_promote_old_good_probes(self):
        mon = monitor()
        rows = probes()
        state = mon.observe(rows[0], rows[1:], fixture={"uid": POD, "ready": True}, now=1061)
        self.assertEqual("TIMEOUT", state["terminal"]["status"])

    def test_failed_partial_and_timeout_never_promote_to_success(self):
        for status in ("FAILED", "PARTIAL", "TIMEOUT"):
            mon = monitor()
            mon.fail(status, "synthetic-failure", now=1002)
            self.assertEqual(status, observe(mon)["terminal"]["status"])

    def test_missing_benign_probe_does_not_complete(self):
        mon, rows = monitor(), probes()
        with self.assertRaises(Refused):
            mon.observe(rows[0], rows[1:4], fixture={"uid": POD, "ready": True}, now=1010)
        self.assertIsNone(mon.snapshot()["terminal"])

    def test_bad_identity_join_source_digest_or_pod_is_refused(self):
        for key, value in (("request_id", "f" * 32), ("correlation_id", "e" * 32),
                           ("client_ip", PINS["benign_ip"]), ("tcp_peer", "10.42.0.99"),
                           ("source_confidence", "UNKNOWN"), ("blocked", False), ("action_ids", []),
                           ("policy_sha256", "b" * 64), ("ts", float("nan"))):
            with self.subTest(key=key):
                rows = probes()
                rows[0]["access"][key] = value
                with self.assertRaises(Refused):
                    observe(monitor(), rows)

    def test_crud_content_cannot_be_replaced_by_status_codes(self):
        for n, body in ((2, {"order_ref": "invalid"}), (3, {"status": "STORED"}),
                        (4, {"deleted": 0}), (5, {"error": "OTHER"})):
            rows = probes()
            rows[n]["http"]["response"]["body"] = body
            with self.assertRaises(Refused):
                observe(monitor(), rows)

    def test_unready_or_same_uid_claim_is_not_verified_replacement(self):
        rows, mon = probes(NEW, 10), monitor()
        for replacement in (None, {"old_uid": NEW, "new_uid": NEW, "old_absent": True},
                            {"old_uid": POD, "new_uid": NEW, "old_absent": False}):
            with self.assertRaises(Refused):
                mon.observe(rows[0], rows[1:], fixture={"uid": NEW, "ready": True}, now=1020,
                            replacement=replacement)
        with self.assertRaises(Refused):
            mon.observe(probes()[0], probes()[1:], fixture={"uid": POD, "ready": False}, now=1010)

    def test_new_uid_old_absence_and_fresh_business_verify_restart_without_second_terminal(self):
        mon = monitor()
        first = observe(mon)
        rows = probes(NEW, 10)
        after = mon.observe(rows[0], rows[1:], fixture={"uid": NEW, "ready": True}, now=1020,
                            replacement={"old_uid": POD, "new_uid": NEW, "old_absent": True})
        self.assertEqual(first["terminal"], after["terminal"])
        self.assertEqual(first["completed_at"], after["completed_at"])
        self.assertEqual(NEW, after["restart"]["new_uid"])

    def test_expiry_or_controller_replacement_alone_does_not_complete_action(self):
        mon = monitor()
        self.assertEqual("TIMEOUT", mon.poll(1181)["terminal"]["status"])
        with self.assertRaises(Refused):
            monitor().observe(probes()[0], probes()[1:], fixture={"uid": NEW, "ready": True}, now=1010)

    def test_nonfinite_clock_and_forged_api_success_are_refused(self):
        for now in (float("nan"), float("inf"), True, 1000):
            with self.assertRaises(Refused):
                monitor().poll(now)
        for api in (dict(API, status="SUCCESS"), dict(API, containment_verified=True)):
            with self.assertRaises(Refused):
                SqliActionState(api, PINS, fixture_uid=POD, accepted_at=1001, timeout_s=60)

    def test_snapshot_and_input_mutations_do_not_change_owned_state(self):
        mon = monitor()
        state = observe(mon)
        state["terminal"]["status"] = "FAILED"
        self.assertEqual("SUCCESS", mon.snapshot()["terminal"]["status"])


class RecordedRuntime(unittest.TestCase):
    def test_real_runtime09_replay_has_containment_and_restart_without_recovery_claim(self):
        path = ROOT / "docs/evidence/ZER-16/reconcile.py"
        spec = importlib.util.spec_from_file_location("zer16_reconcile", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.replay()
        self.assertEqual("API_ACCEPTED", result["api_only"]["phase"])
        self.assertEqual("SUCCESS", result["action_completed"]["terminal"]["status"])
        self.assertTrue(result["after_replacement"]["restart"]["old_absent"])
        self.assertFalse(result["recovery_verified"])
        self.assertFalse(result["boutique_business_healthy"])
        self.assertEqual(0, result["new_lab_requests"])


if __name__ == "__main__":
    unittest.main()
