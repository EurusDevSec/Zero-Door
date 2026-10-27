"""ZER-42 SQLi admission parity (Nemesis side). Offline: no clients, broker, threads or effects — only the
pure CommandGuard.sqli_command path and SQLi policy validation. The produced command shape must be the one the
Go guard re-admits (see chaos-worker/internal/guard/sqli_test.go)."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "infrastructure" / "scripts"))
from nemesis.command_guard import CommandGuard, Refused, SQLI_TEMPLATE_IDS, sqli_endpoint_valid  # noqa: E402
import sqli_executor_runtime as runtime  # noqa: E402
from event_pipeline import contract  # noqa: E402
from measurement import scorer  # noqa: E402

FIXTURE = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())
CANON = json.loads((ROOT / "tests/fixtures/zer42/catalog-ids.json").read_text())
ENDPOINT = "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"


def sqli_policy():
    policy = deepcopy(FIXTURE["policy"])
    policy["sqli"] = {"enabled": True, "endpoint": ENDPOINT, "maxSends": 20, "maxCommandSec": 30}
    return policy


class CatalogParity(unittest.TestCase):
    def test_template_ids_match_canonical_source(self):
        self.assertEqual(set(SQLI_TEMPLATE_IDS), set(CANON["template_ids"]))
        self.assertIn(CANON["injection_id"], SQLI_TEMPLATE_IDS)


class EndpointValidation(unittest.TestCase):
    def test_exact_endpoint_only(self):
        self.assertEqual(ENDPOINT, sqli_endpoint_valid(ENDPOINT))
        with self.assertRaises(Refused):
            sqli_endpoint_valid(ENDPOINT.replace(":8000/", ":8001/"))
        for bad in ["https://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search", ENDPOINT + "?category=x",
                    ENDPOINT + "#f", ENDPOINT + "/",
                    "http://user:pw@zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search",
                    "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/orders",
                    "http://TRAEFIK.kube-system.svc.cluster.local/fixture/catalog/search",
                    "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000:0/fixture/catalog/search",
                    "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000:99999/fixture/catalog/search",
                    "ftp://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search",
                    "http:///fixture/catalog/search", ENDPOINT + "%20",
                    # ZR42-04: IP literals (public/loopback/private) and bare hosts are not an ingress DNS name.
                    "http://203.0.113.10/fixture/catalog/search", "http://127.0.0.1/fixture/catalog/search",
                    "http://10.1.2.3/fixture/catalog/search", "http://host.local/fixture/catalog/search",
                    "http://traefik.svc.cluster.local/fixture/catalog/search",  # missing namespace label
                    # ZR42-04: the fixture Service directly bypasses the ingress observation point.
                    "http://sqli-fixture.zd-sqli-lab.svc.cluster.local/fixture/catalog/search"]:
            with self.subTest(bad=bad), self.assertRaises(Refused):
                sqli_endpoint_valid(bad)


class SqliCommand(unittest.TestCase):
    def setUp(self):
        self.guard = CommandGuard(sqli_policy())
        self.body = dict(attackType="SQLI", template="disclose-restricted")

    def test_valid_command_shape(self):
        cmd = self.guard.command(self.body, str(uuid.uuid4()))
        self.assertEqual("SQLI", cmd["attackType"])
        self.assertEqual({"namespace": "zd-sqli-lab", "service": "sqli-fixture", "url": ENDPOINT}, cmd["target"])
        self.assertEqual(1, cmd["parameters"]["concurrency"])
        self.assertEqual("LOW", cmd["parameters"]["intensity"])
        self.assertEqual({"template": "disclose-restricted"}, cmd["parameters"]["customParams"])
        self.assertEqual(["zd-sqli-lab"], cmd["safetyLimits"]["allowedNamespaces"])
        self.assertLessEqual(cmd["parameters"]["duration"], 30)
        self.assertEqual(self.guard.policy["context"], cmd["context"])
        # benign control admits too
        self.assertEqual("benign-apparel",
                         self.guard.command(dict(self.body, template="benign-apparel"), str(uuid.uuid4()))["parameters"]["customParams"]["template"])

    def test_duration_clamped_to_capability(self):
        guard = CommandGuard(dict(sqli_policy(), sqli={"enabled": True, "endpoint": ENDPOINT, "maxSends": 20, "maxCommandSec": 10}))
        self.assertEqual(10, guard.command(self.body, str(uuid.uuid4()))["parameters"]["duration"])
        with self.assertRaises(Refused):
            guard.command(dict(self.body, durationSec=11), str(uuid.uuid4()))

    def test_rejections(self):
        disabled = CommandGuard(dict(sqli_policy(), sqli={"enabled": False, "endpoint": ENDPOINT, "maxSends": 20, "maxCommandSec": 30}))
        with self.assertRaises(Refused):
            disabled.command(self.body, str(uuid.uuid4()))
        no_cap = CommandGuard(deepcopy(FIXTURE["policy"]))
        with self.assertRaises(Refused):
            no_cap.command(self.body, str(uuid.uuid4()))
        for change in [dict(template="drop-tables"), dict(template=1), {"extra": "x"},
                       dict(durationSec=0), dict(durationSec=True), dict(durationSec=31)]:
            with self.subTest(change=change), self.assertRaises(Refused):
                self.guard.command(dict(self.body, **change), str(uuid.uuid4()))
        # a missing required key is refused
        with self.assertRaises(Refused):
            self.guard.command({"attackType": "SQLI"}, str(uuid.uuid4()))

    def test_legacy_still_rejects_customparams_and_sqli_target(self):
        # A legacy command cannot carry customParams, including the SQLi template key.
        with self.assertRaises(Refused):
            self.guard.command(dict(attackType="HTTP_FLOOD", targetService="frontend", customParams={"template": "disclose-restricted"}),
                               str(uuid.uuid4()))
        # A legacy command cannot target the fixture service (not in the policy targets).
        with self.assertRaises(Refused):
            self.guard.command(dict(attackType="HTTP_FLOOD", targetService="sqli-fixture"), str(uuid.uuid4()))


class SqliPolicyValidation(unittest.TestCase):
    def test_invalid_sqli_policy_fails_closed(self):
        for sqli in [{"enabled": True, "endpoint": "https://h/fixture/catalog/search", "maxSends": 20, "maxCommandSec": 30},
                     {"enabled": True, "endpoint": ENDPOINT + "?x=1", "maxSends": 20, "maxCommandSec": 30},
                     {"enabled": True, "endpoint": ENDPOINT, "maxSends": 21, "maxCommandSec": 30},
                     {"enabled": True, "endpoint": ENDPOINT, "maxSends": 0, "maxCommandSec": 30},
                     {"enabled": True, "endpoint": ENDPOINT, "maxSends": 20, "maxCommandSec": 31},
                     {"enabled": "yes", "endpoint": ENDPOINT, "maxSends": 20, "maxCommandSec": 30},
                     {"enabled": True, "endpoint": ENDPOINT, "maxSends": 20}]:
            with self.subTest(sqli=sqli), self.assertRaises(Refused):
                CommandGuard(dict(deepcopy(FIXTURE["policy"]), sqli=sqli))


ORACLE = frozenset({"RES-APP-900", "RES-INT-001", "RES-INT-002"})
WINDOW_START = "2026-10-26T00:00:00.000Z"


def at(sec):
    """An observedAt stamp `sec` seconds after the window start (sec in 0..59)."""
    return "2026-10-26T00:00:%02d.000Z" % sec


def clean(sec, *, rows=2, restricted=0, skus=None):
    s = {"seq": sec + 1, "status": 200, "rows": rows, "restrictedRows": restricted, "observedAt": at(sec),
         "startedAt": at(sec), "requestId": "cmd/%d" % (sec + 1)}
    if skus is not None:
        s["restrictedSkus"] = skus
    return s


def executor_result(sends, status="SUCCESS", window_start=WINDOW_START, clock_id="chaos-worker-local",
                    clock_source="UNKNOWN"):
    sqli = {"templateId": "t", "kind": "injection", "clockId": clock_id, "clockSource": clock_source,
            "windowStart": window_start, "sends": sends}
    return {"status": status, "commandId": "11111111-1111-4111-8111-111111111111", "duration": 1000,
            "timestamp": window_start, "details": {"sqli": sqli}}


def h_context():
    return {"run_id": contract.new_id("run"), "trial_id": contract.new_id("trl"), "incident_id": contract.new_id("inc"),
            "group": "B1", "method_version": "m1", "config_ref": "sha256:" + "a" * 64}


CLOCK = {"clock_id": "chaos-worker-local", "clock_source": "UNKNOWN", "resolution_ms": 1}
# A clean stream that covers [T_req, T_req + 5s] at 1 rps (so CONFIRMED_NO_EFFECT is reachable).
COVER5 = [clean(i) for i in range(0, 6)]


class EffectEvaluator(unittest.TestCase):
    def test_oracle_matches_zer41(self):
        self.assertEqual(ORACLE, runtime.oracle_restricted())

    def test_confirmed_stamps_the_disclosing_send_not_command_start(self):
        # Disclosure observed at +4s (not at window start): t_eff must be that send's observed instant.
        sends = [clean(i) for i in range(0, 4)] + [clean(4, rows=4, restricted=3, skus=sorted(ORACLE))]
        p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        self.assertEqual("CONFIRMED", p["status"])
        self.assertEqual(at(4), p["t_eff"])
        self.assertNotEqual(WINDOW_START, p["t_eff"])
        ev = runtime.build_event(h_context(), p, CLOCK)
        self.assertEqual(("EFFECT_EVALUATED", "H", "effect_evaluator"),
                         (ev["event_type"], ev["plane"], ev["source_component"]))

    def test_disclosure_without_time_or_clock_is_unknown(self):
        sends = [{"status": 200, "rows": 4, "restrictedRows": 3, "restrictedSkus": sorted(ORACLE)}]  # no observedAt
        p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])
        self.assertIsNone(p["t_eff"])

    def test_confirmed_no_effect_needs_full_window_coverage(self):
        p = runtime.evaluate_effect(executor_result(COVER5), oracle=ORACLE, min_clean_sends=3, w_eff_s=5)
        self.assertEqual("CONFIRMED_NO_EFFECT", p["status"])
        self.assertIsNone(p["t_eff"])
        runtime.build_event(h_context(), p, CLOCK)  # validates

    def test_single_clean_sample_does_not_cover_a_long_window(self):
        p = runtime.evaluate_effect(executor_result([clean(0)]), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])  # one sample, 5s window -> coverage gap

    def test_error_inside_window_contradicts_no_effect(self):
        sends = [clean(0), {"seq": 2, "status": 0, "error": "TRANSPORT", "observedAt": at(1)}] + [clean(i) for i in range(2, 6)]
        p = runtime.evaluate_effect(executor_result(sends, status="SUCCESS"), oracle=ORACLE, min_clean_sends=2, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_malformed_200_in_window_is_not_clean(self):
        # restrictedRows > rows is not usable evidence; it must not satisfy coverage.
        sends = [clean(0), {"seq": 2, "status": 200, "rows": 1, "restrictedRows": 2, "observedAt": at(1)}] + [clean(i) for i in range(2, 6)]
        p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=2, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_invalid_eval_params_never_become_no_effect(self):
        for kwargs in ({"min_clean_sends": 0, "w_eff_s": 5}, {"min_clean_sends": 1, "w_eff_s": 0},
                       {"min_clean_sends": 1, "w_eff_s": 5, "gap_s": float("inf")}):
            with self.subTest(kwargs=kwargs):
                p = runtime.evaluate_effect(executor_result(COVER5), oracle=ORACLE, **kwargs)
                self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_missing_or_contradictory_raw_is_unknown(self):
        bad_sets = [
            COVER5 + [None],
            COVER5 + [{"seq": 7, "status": 0, "error": "TRANSPORT", "startedAt": at(5)}],
            [clean(i) for i in range(5)] + [{"seq": 6, "status": 200, "rows": 1, "restrictedRows": 1,
                                             "startedAt": at(5), "observedAt": at(5)}],
        ]
        for sends in bad_sets:
            with self.subTest(sends=sends):
                p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
                self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_missing_clock_is_unknown(self):
        p = runtime.evaluate_effect(executor_result(COVER5, clock_id=None), oracle=ORACLE, min_clean_sends=3, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_all_errored_is_unknown(self):
        sends = [{"status": 0, "error": "TRANSPORT", "observedAt": at(0)}, {"status": 503, "observedAt": at(1)}]
        p = runtime.evaluate_effect(executor_result(sends, status="FAILED"), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_restricted_outside_oracle_is_unknown(self):
        sends = [clean(0, rows=1, restricted=1, skus=["RES-GHOST-999"])]
        p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        self.assertEqual("UNKNOWN_EFFECT", p["status"])

    def test_evidence_carries_no_oracle_or_seed_keys(self):
        sends = [clean(4, rows=4, restricted=3, skus=sorted(ORACLE))]
        p = runtime.evaluate_effect(executor_result(sends), oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
        ev = runtime.build_event(h_context(), p, CLOCK)
        blob = json.dumps(ev)
        for forbidden_name in ("seed", "variant_id", "expected_action", "canary_token", "onset_offset_ms"):
            self.assertNotIn('"%s"' % forbidden_name, blob)


class EmitEvidence(unittest.TestCase):
    """ZR42-05: the offline entrypoint threads one executor result into a FAULT_EXECUTOR_RESULT and a
    causally-linked EFFECT_EVALUATED through a plain sink — no broker."""

    def test_entrypoint_emits_two_linked_events(self):
        captured = []
        sends = [clean(i) for i in range(0, 4)] + [clean(4, rows=4, restricted=3, skus=sorted(ORACLE))]
        fault, effect = runtime.emit_evidence(executor_result(sends), h_context(), sink=captured.append,
                                              min_clean_sends=1, w_eff_s=5)
        self.assertEqual(2, len(captured))
        self.assertEqual(("FAULT_EXECUTOR_RESULT", "H", "fault_executor"),
                         (fault["event_type"], fault["plane"], fault["source_component"]))
        self.assertEqual(("EFFECT_EVALUATED", "H", "effect_evaluator"),
                         (effect["event_type"], effect["plane"], effect["source_component"]))
        self.assertEqual(fault["event_id"], effect["causation_id"])  # causal link
        self.assertEqual("CONFIRMED", effect["payload"]["status"])
        self.assertEqual("SUCCESS", fault["payload"]["executor_status"])
        self.assertEqual(1000, fault["payload"]["duration_ms"])
        self.assertEqual(runtime.digest(executor_result(sends)), fault["payload"]["raw_result_sha256"])
        self.assertEqual(executor_result(sends), fault["payload"]["raw_result"])

    def test_entrypoint_leaks_no_seed(self):
        sends = [clean(4, rows=4, restricted=3, skus=sorted(ORACLE))]
        blob = json.dumps(runtime.emit_evidence(executor_result(sends), h_context(), min_clean_sends=1, w_eff_s=5))
        for forbidden_name in ("seed", "variant_id", "expected_action", "canary_token", "onset_offset_ms"):
            self.assertNotIn('"%s"' % forbidden_name, blob)

    def test_bundle_archive_export_replay_and_recheck(self):
        context = h_context()
        result = executor_result([clean(i) for i in range(0, 4)] +
                                 [clean(4, rows=4, restricted=3, skus=sorted(ORACLE))])
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bundle_path = tmp / "bundle.json"
            bundle = runtime.prepare_bundle(result, context, bundle_path, oracle=ORACLE, w_eff_s=5)
            self.assertEqual(bundle, runtime.prepare_bundle(result, context, bundle_path, oracle=ORACLE, w_eff_s=5))
            first = runtime.archive_bundle(bundle, tmp / "archive", tmp / "export-1", oracle=ORACLE)
            second = runtime.archive_bundle(bundle, tmp / "archive", tmp / "export-2", oracle=ORACLE)
            self.assertEqual("CONFIRMED", first["checked"][0]["status"])
            self.assertEqual(first["checked"][0]["raw_result_sha256"], second["checked"][0]["raw_result_sha256"])
            self.assertEqual(first, runtime.recheck_export(tmp / "export-1", oracle=ORACLE))
            with self.assertRaises(ValueError):
                runtime.prepare_bundle(dict(result, status="FAILED"), context, bundle_path, oracle=ORACLE, w_eff_s=5)

    def test_archive_no_effect_remains_unknown_without_probe_samples(self):
        context = h_context()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bundle = runtime.prepare_bundle(executor_result(COVER5), context, tmp / "bundle.json",
                                            oracle=ORACLE, min_clean_sends=3, w_eff_s=5)
            receipt = runtime.archive_bundle(bundle, tmp / "archive", tmp / "export", oracle=ORACLE)
            self.assertEqual("UNKNOWN_EFFECT", receipt["checked"][0]["status"])


def verify_go_result(path):
    """Actual Go JSON -> evaluator -> contract -> scorer semantic bridge used by CI."""
    result = json.loads(Path(path).read_text())
    payload = runtime.evaluate_effect(result, oracle=ORACLE, min_clean_sends=1, w_eff_s=5)
    event = runtime.build_event(h_context(), payload, runtime.executor_clock(result))
    if payload["status"] != "CONFIRMED" or scorer.semantic(event, None) is not None:
        raise AssertionError((payload, scorer.semantic(event, None)))
    if not contract.STAMP.fullmatch(payload["t_eff"]):
        raise AssertionError(payload["t_eff"])


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--verify-go-result":
        verify_go_result(sys.argv[2])
    else:
        unittest.main()
