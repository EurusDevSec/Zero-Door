"""Offline tests for the ZER-41 SQLi catalog fixture (services/sqli-fixture/app.py).

Everything runs on loopback against a real SQLite database in a temp directory: no cluster, no Docker, no
network beyond 127.0.0.1. Expected values are locked in tests/fixtures/zer41/expected.json, computed from
the seed before these assertions were written; stdout "ok" is never the oracle.

The app under test is services/sqli-fixture/app.py, or the path in ZD_SQLI_APP (so the same suite can be run
against the pre-fix snapshot to demonstrate fail-before).

  python -B tests/test_sqli_fixture.py
"""
import importlib.util
import io
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "agent-orchestrator")]
from measurement.flows import Flow, Memory, fixture_spec, request  # noqa: E402

FIXTURES = ROOT / "tests/fixtures/zer41"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text())


APP_PATH = os.environ.get("ZD_SQLI_APP") or str(ROOT / "services/sqli-fixture/app.py")


def load_app():
    path = APP_PATH
    spec = importlib.util.spec_from_file_location("zer41_app_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


app = load_app()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Service:
    """A fixture service on loopback with its own temp DB, for one profile/topology."""
    def __init__(self, profile="safe", trusted="", topology="direct", db_dir=None):
        self.dir = None if db_dir else tempfile.TemporaryDirectory()
        where = db_dir or self.dir.name
        env = {"ZD_SQLI_PROFILE": profile, "ZD_SQLI_DB_DIR": where, "ZD_SQLI_PORT": str(free_port()),
               "ZD_SQLI_SEED": str(FIXTURES / "seed.json"), "ZD_SQLI_TRUSTED_PROXIES": trusted,
               "ZD_SQLI_TOPOLOGY": topology}
        self.config = app.Config(env)
        self.out, self.err = io.StringIO(), io.StringIO()
        with redirect_stdout(self.out), redirect_stderr(self.err):
            self.httpd, self.store, self.seed_id, self.rows = app.build_server(self.config)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.origin = f"http://127.0.0.1:{self.port}"

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        if self.dir:
            self.dir.cleanup()

    def get_json(self, path, headers=None):
        with redirect_stdout(self.out):
            with urlopen(Request(self.origin + path, headers=headers or {}), timeout=5) as response:
                return response.status, json.loads(response.read())

    def skus(self, category):
        with redirect_stdout(self.out):
            status, body = self.get_json("/fixture/catalog/search?category=" + quote(category, safe=""))
        return status, [r["sku"] for r in body.get("results", [])], body


class Seed(unittest.TestCase):
    def test_service_and_test_seed_do_not_drift(self):
        self.assertEqual((ROOT / "services/sqli-fixture/seed.json").read_bytes(),
                         (FIXTURES / "seed.json").read_bytes())

    def test_expected_matches_seed(self):
        seed = json.loads((FIXTURES / "seed.json").read_text())
        catalog = seed["catalog"]
        self.assertEqual(seed["seed_id"], EXPECTED["seed_id"])
        self.assertEqual(len(catalog), EXPECTED["catalog_rows"])
        self.assertEqual(sum(1 for r in catalog if r["visibility"] == "restricted"), EXPECTED["restricted_rows"])

    def test_build_db_is_reproducible(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
            def rows(where):
                config = app.Config({"ZD_SQLI_DB_DIR": where, "ZD_SQLI_SEED": str(FIXTURES / "seed.json")})
                seed_id, n = app.build_db(config)
                db = sqlite3.connect(config.db_path)
                try:
                    return seed_id, n, db.execute("SELECT count(*) FROM catalog").fetchone()[0]
                finally:
                    db.close()
            self.assertEqual(rows(one), rows(two))
            self.assertEqual(rows(one), (EXPECTED["seed_id"], EXPECTED["catalog_rows"], EXPECTED["catalog_rows"]))


class Search(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.safe = Service("safe")
        cls.vuln = Service("vulnerable")

    @classmethod
    def tearDownClass(cls):
        cls.safe.close()
        cls.vuln.close()

    def test_benign_categories_are_equivalent_on_both_profiles(self):
        for category, expected in EXPECTED["benign"].items():
            s_status, s_skus, _ = self.safe.skus(category)
            v_status, v_skus, body = self.vuln.skus(category)
            self.assertEqual((s_status, v_status), (200, 200), category)
            self.assertEqual(sorted(s_skus), sorted(expected), f"safe {category}")
            self.assertEqual(sorted(v_skus), sorted(expected), f"vulnerable {category}")
            self.assertFalse([r for r in body["results"] if r["visibility"] != "public"], category)

    def test_injection_leaks_restricted_rows_only_on_the_vulnerable_profile(self):
        payload = EXPECTED["injection"]["category"]
        v_status, v_skus, v_body = self.vuln.skus(payload)
        s_status, s_skus, _ = self.safe.skus(payload)
        self.assertEqual((v_status, s_status), (200, 200))
        self.assertEqual(sorted(v_skus), sorted(EXPECTED["injection"]["vulnerable_returns_restricted"]))
        self.assertTrue([r for r in v_body["results"] if r["visibility"] == "restricted"])
        self.assertEqual(s_skus, EXPECTED["injection"]["safe_returns"])

    def test_stacked_statement_injection_is_rejected_not_executed(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.vuln.origin + "/fixture/catalog/search?category="
                    + quote("apparel'; DELETE FROM catalog WHERE visibility='public' --", safe=""), timeout=5)
        self.assertEqual(caught.exception.code, 400)
        _status, skus, _body = self.vuln.skus("apparel")
        self.assertEqual(sorted(skus), sorted(EXPECTED["benign"]["apparel"]))

    def test_blob_union_result_is_rejected_not_crashed(self):
        # An injected UNION returning a non-text value must be a clean 4xx, never a serialization crash.
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.vuln.origin + "/fixture/catalog/search?category="
                    + quote("zzz' UNION SELECT randomblob(2048),'n','c','public',1 --", safe=""), timeout=5)
        self.assertEqual(caught.exception.code, 422)

    def test_category_over_length_is_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.vuln.origin + "/fixture/catalog/search?category=" + "a" * (app.MAX_Q + 1), timeout=5)
        self.assertEqual(caught.exception.code, 400)


class Failures(unittest.TestCase):
    def test_missing_db_is_503_with_a_record_not_a_disconnect(self):
        svc = Service("safe")
        try:
            svc.config.db_path.unlink()  # the DB vanishes under a running service
            with self.assertRaises(HTTPError) as caught:
                urlopen(svc.origin + "/fixture/catalog/search?category=home", timeout=5)
            self.assertEqual(caught.exception.code, 503)
            self.assertEqual(json.loads(caught.exception.read())["error"], "DB_UNAVAILABLE")
        finally:
            svc.httpd.shutdown(); svc.httpd.server_close(); svc.dir.cleanup()

    def test_locked_db_on_a_benign_category_is_503_not_a_client_error(self):
        svc = Service("safe")
        locker = sqlite3.connect(svc.config.db_path, isolation_level=None)
        locker.execute("BEGIN EXCLUSIVE")
        try:
            with self.assertRaises(HTTPError) as caught:
                urlopen(svc.origin + "/fixture/catalog/search?category=home", timeout=5)
            self.assertEqual(caught.exception.code, 503)  # availability failure, not bad client SQL
        finally:
            locker.execute("ROLLBACK"); locker.close()
            svc.close()


class Crud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc = Service("safe")

    @classmethod
    def tearDownClass(cls):
        cls.svc.close()

    def run_flow(self, http=request):
        flow = Flow(fixture_spec(item="zer41-benign-item"), self.svc.origin, [self.svc.origin])
        now = time.perf_counter_ns()
        with redirect_stdout(self.svc.out):
            return flow.run(now + int(5e9), None, Memory(), http=http, step_s=4, cleanup_ns=now + int(6e9), grace_s=2)

    def test_owned_order_round_trip_then_cleanup(self):
        result = self.run_flow()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["cleanup"].get("order"), "DONE")

    def test_delete_is_scoped_to_one_ref_and_is_parameterised(self):
        a = self.svc.store.create_order("item-a", "nonce-a")
        b = self.svc.store.create_order("item-b", "nonce-b")
        self.assertEqual(self.svc.store.delete_order("' OR '1'='1"), 0)
        self.assertEqual(self.svc.store.delete_order(a["order_ref"]), 1)
        self.assertIsNotNone(self.svc.store.read_order(b["order_ref"]))
        self.assertIsNone(self.svc.store.read_order(a["order_ref"]))

    def test_unproven_ownership_is_not_cleaned(self):
        def tamper(url, method="GET", headers=(), body=b"", deadline_ns=0, cancel=None, **kw):
            response = request(url, method, headers, body, deadline_ns, cancel, **kw)
            if method == "POST":
                document = json.loads(response.body)
                document["note"] = "not-the-nonce"
                response.body = json.dumps(document).encode()
            return response
        result = self.run_flow(http=tamper)
        self.assertFalse(result["ok"])
        self.assertEqual(result["cleanup"].get("order"), "UNRESOLVED_OWNERSHIP")

    def test_oversized_body_is_refused(self):
        big = json.dumps({"item": "x", "note": "y" * (app.MAX_BODY + 10)}).encode()
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.svc.origin + "/fixture/orders", data=big,
                            headers={"Content-Type": "application/json"}), timeout=5)
        self.assertEqual(caught.exception.code, 413)

    def test_malformed_body_is_refused(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.svc.origin + "/fixture/orders", data=b"{not json",
                            headers={"Content-Type": "application/json"}), timeout=5)
        self.assertEqual(caught.exception.code, 400)

    def test_explicit_reset_removes_orders_only(self):
        self.svc.store.create_order("keep-cat", "n")
        before = self.svc.store.search("apparel", time.monotonic() + 2)
        self.svc.store.reset_orders()
        after = self.svc.store.search("apparel", time.monotonic() + 2)
        self.assertEqual(before, after)  # catalog intact
        db = sqlite3.connect(self.svc.config.db_path)
        try:
            self.assertEqual(db.execute("SELECT count(*) FROM orders").fetchone()[0], 0)
        finally:
            db.close()


class Startup(unittest.TestCase):
    def test_normal_reopen_preserves_orders(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            one = Service("safe", db_dir=tmp)
            order = one.store.create_order("owned", "nonce")
            one.close()
            two = Service("safe", db_dir=tmp)  # restart on the same directory
            try:
                self.assertIsNotNone(two.store.read_order(order["order_ref"]))
            finally:
                two.close()

    def test_invalid_config_refuses_before_any_mutation(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            svc = Service("safe", db_dir=tmp)
            order = svc.store.create_order("owned", "nonce")
            svc.close()
            # An out-of-range port is refused by Config, before build_server can touch the DB.
            with self.assertRaises(app.ConfigError):
                app.Config({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json"),
                            "ZD_SQLI_PORT": "70000"})
            # A fresh Store still sees the order: nothing was erased.
            store = app.Store(app.Config({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json")}))
            self.assertIsNotNone(store.read_order(order["order_ref"]))

    def test_foreign_db_refuses_start_without_erasing(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            foreign = Path(tmp) / "fixture.sqlite"
            db = sqlite3.connect(foreign)
            db.execute("CREATE TABLE keep (x)")
            db.execute("INSERT INTO keep VALUES (1)")
            db.commit(); db.close()
            config = app.Config({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json")})
            with self.assertRaises(app.ConfigError):
                app.open_or_create(config)
            db = sqlite3.connect(foreign)
            self.assertEqual(db.execute("SELECT x FROM keep").fetchone()[0], 1)  # untouched
            db.close()


class Source(unittest.TestCase):
    """Source-IP decision logic (offline). Trusting a client-declared header is the failure these guard."""
    LAB = app.parse_networks("10.42.0.0/16")

    def test_direct_topology_peer_is_source_and_forged_header_ignored(self):
        record = app.resolve_source("203.0.113.9", "192.0.2.10", [], "direct")
        self.assertEqual(record["client_ip"], "203.0.113.9")
        self.assertEqual(record["method"], "DIRECT_PEER")
        self.assertEqual(record["forwarded_for_seen"], "192.0.2.10")  # kept as evidence, not used

    def test_proxied_ingress_without_trusted_proxy_is_unknown(self):
        # The actual manifest default: behind Traefik, no trusted proxy configured -> client UNKNOWN.
        record = app.resolve_source("10.42.0.7", "198.51.100.9", [], "proxied")
        self.assertIsNone(record["client_ip"])
        self.assertEqual((record["method"], record["confidence"]), ("PEER_NOT_TRUSTED_PROXY", "UNKNOWN"))
        self.assertEqual(record["tcp_peer"], "10.42.0.7")  # observed peer still recorded

    def test_proxied_trusted_proxy_with_forwarded_client(self):
        record = app.resolve_source("10.42.1.1", "198.51.100.7", self.LAB, "proxied")
        self.assertEqual(record["client_ip"], "198.51.100.7")
        self.assertEqual((record["method"], record["confidence"]), ("XFF_AFTER_TRUSTED", "PROXY_CHAIN"))

    def test_proxied_trusted_proxy_without_forward_is_unknown(self):
        record = app.resolve_source("10.42.1.1", None, self.LAB, "proxied")
        self.assertIsNone(record["client_ip"])
        self.assertEqual(record["method"], "PROXY_NO_FORWARD")

    def test_proxied_malformed_forward_is_unknown(self):
        record = app.resolve_source("10.42.1.1", "not-an-ip", self.LAB, "proxied")
        self.assertIsNone(record["client_ip"])
        self.assertEqual(record["method"], "PROXY_BAD_FORWARD")

    def test_proxied_all_hops_trusted_is_unknown(self):
        record = app.resolve_source("10.42.1.1", "10.42.1.2, 10.42.1.3", self.LAB, "proxied")
        self.assertIsNone(record["client_ip"])
        self.assertEqual(record["method"], "PROXY_ALL_TRUSTED")

    def test_proxied_multi_hop_takes_first_untrusted_from_the_right(self):
        record = app.resolve_source("10.42.1.1", "198.51.100.7, 10.42.1.9", self.LAB, "proxied")
        self.assertEqual(record["client_ip"], "198.51.100.7")


class ConfigGuards(unittest.TestCase):
    def base(self, **over):
        env = {"ZD_SQLI_DB_DIR": tempfile.gettempdir(), "ZD_SQLI_SEED": str(FIXTURES / "seed.json")}
        env.update(over)
        return env

    def test_default_profile_is_safe_and_topology_proxied(self):
        config = app.Config(self.base())
        self.assertEqual((config.profile, config.topology), ("safe", "proxied"))

    def test_unknown_profile_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_PROFILE="sneaky"))

    def test_unknown_topology_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_TOPOLOGY="sideways"))

    def test_missing_db_dir_refuses_start(self):
        env = self.base()
        del env["ZD_SQLI_DB_DIR"]
        with self.assertRaises(app.ConfigError):
            app.Config(env)

    def test_nonexistent_db_dir_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_DB_DIR=str(ROOT / "no-such-dir-zer41")))

    def test_bad_trusted_proxy_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_TRUSTED_PROXIES="not-a-cidr"))

    def test_out_of_range_port_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_PORT="70000"))

    def test_missing_seed_refuses_start(self):
        with self.assertRaises(app.ConfigError):
            app.Config(self.base(ZD_SQLI_SEED=str(ROOT / "no-such-seed.json")))


class StartupFailure(unittest.TestCase):
    """The real CLI, as the container runs it: a failed startup must exit nonzero, leave an existing DB
    intact, and print only a neutral reason code on BOTH streams (Fluent Bit collects stdout and stderr) —
    no traceback, path, stored or expected seed id, profile or attempted value."""
    CANARY = "hidden-seed-canary-zr41"

    def run_cli(self, env):
        full = {k: v for k, v in os.environ.items() if not k.startswith("ZD_SQLI_")}
        full.update(env)
        return subprocess.run([sys.executable, "-B", APP_PATH], env=full, capture_output=True, text=True,
                              timeout=20)

    def assert_neutral(self, result, *secrets):
        streams = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, streams)
        self.assertNotIn("Traceback", streams)
        for secret in secrets:
            self.assertNotIn(secret, streams)
        lines = [l for l in result.stderr.splitlines() if l.strip()]
        self.assertEqual(len(lines), 1, streams)
        record = json.loads(lines[0])
        self.assertEqual(record["event"], "startup_failed")
        self.assertLessEqual(set(record), {"event", "reason", "setting"})
        return record

    def test_mismatched_seed_db_fails_neutrally_and_is_kept(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            config = app.Config({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json")})
            app.open_or_create(config)
            db = sqlite3.connect(config.db_path)
            db.execute("UPDATE meta SET value=? WHERE key='seed_id'", (self.CANARY,))
            db.commit()
            db.close()
            before = config.db_path.read_bytes()
            result = self.run_cli({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json"),
                                   "ZD_SQLI_PORT": "0", "ZD_SQLI_PROFILE": "vulnerable"})
            record = self.assert_neutral(result, self.CANARY, EXPECTED["seed_id"], tmp, "vulnerable")
            self.assertEqual(record["reason"], "DB_INCOMPATIBLE")
            self.assertEqual(config.db_path.read_bytes(), before)  # the existing DB is not touched

    def test_foreign_file_fails_neutrally_and_is_kept(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            foreign = Path(tmp) / "fixture.sqlite"
            foreign.write_bytes(b"not a database " + self.CANARY.encode())
            result = self.run_cli({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json"),
                                   "ZD_SQLI_PORT": "0"})
            self.assert_neutral(result, self.CANARY, tmp)
            self.assertEqual(foreign.read_bytes(), b"not a database " + self.CANARY.encode())

    def test_ill_formed_seed_fails_neutrally(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            seed = Path(tmp) / "seed.json"
            seed.write_text("{not json " + self.CANARY, encoding="utf-8")
            result = self.run_cli({"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(seed), "ZD_SQLI_PORT": "0"})
            record = self.assert_neutral(result, self.CANARY, tmp)
            self.assertEqual(record["reason"], "SEED_INVALID")

    def test_invalid_settings_fail_neutrally_without_echoing_values(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            base = {"ZD_SQLI_DB_DIR": tmp, "ZD_SQLI_SEED": str(FIXTURES / "seed.json"), "ZD_SQLI_PORT": "0"}
            for key, value in (("ZD_SQLI_PROFILE", "variant-" + self.CANARY),
                               ("ZD_SQLI_TRUSTED_PROXIES", "cidr-" + self.CANARY),
                               ("ZD_SQLI_SEED", str(Path(tmp) / ("missing-" + self.CANARY)))):
                with self.subTest(setting=key):
                    record = self.assert_neutral(self.run_cli(dict(base, **{key: value})), self.CANARY, tmp)
                    self.assertEqual(record.get("setting"), key)

    def test_handler_error_writes_no_traceback(self):
        # A request-thread crash outside the handler's own guard is reported by the server; its default
        # prints a traceback with source lines and messages to stderr.
        err = io.StringIO()
        with redirect_stderr(err):
            try:
                raise RuntimeError("secret detail " + self.CANARY)
            except RuntimeError:
                app.FixtureServer.handle_error(object(), None, ("127.0.0.1", 1))
        self.assertNotIn("Traceback", err.getvalue())
        self.assertNotIn(self.CANARY, err.getvalue())


class Logs(unittest.TestCase):
    def test_no_container_stream_discloses_the_profile(self):
        # Fluent Bit tails stdout AND stderr; the profile/variant is an H fact and must appear on neither,
        # at startup, on a request, or on a failure.
        svc = Service("vulnerable")
        # Response bytes may arrive before the request thread emits its terminal record. Keep capture
        # active through a bounded wait and shutdown instead of racing stdout restoration.
        with redirect_stdout(svc.out), redirect_stderr(svc.err):
            try:
                svc.get_json("/fixture/catalog/search?category=home", headers={"X-Correlation-Id": "trace-123"})
                try:
                    urlopen(svc.origin + "/fixture/catalog/search?category=" + "a" * (app.MAX_Q + 1), timeout=5)
                except HTTPError:
                    pass
                deadline = time.monotonic() + 2.0
                while True:
                    records = [json.loads(x) for x in svc.out.getvalue().splitlines() if x.strip()]
                    accesses = [r for r in records if r.get("path") == "/fixture/catalog/search"]
                    if len(accesses) >= 2 or time.monotonic() >= deadline:
                        break
                    time.sleep(0.01)
                self.assertCountEqual([r["status"] for r in accesses], [200, 400])
            finally:
                svc.close()
            streams = svc.out.getvalue() + svc.err.getvalue()
        self.assertNotIn("vulnerable", streams)
        self.assertNotIn("profile", streams)
        lines = [json.loads(x) for x in svc.out.getvalue().splitlines() if x.strip()]
        search = next(l for l in lines if l["path"] == "/fixture/catalog/search" and l["status"] == 200)
        self.assertEqual(search["correlation_id"], "trace-123")
        self.assertNotEqual(search["request_id"], "trace-123")
        self.assertEqual(len(search["request_id"]), 32)

    def test_ill_formed_correlation_ids_are_dropped(self):
        self.assertEqual(app.valid_correlation("trace-123"), "trace-123")
        self.assertIsNone(app.valid_correlation("a\r\ninjected"))
        self.assertIsNone(app.valid_correlation("x" * 129))
        self.assertIsNone(app.valid_correlation("café"))
        self.assertIsNone(app.valid_correlation(None))


class Readiness(unittest.TestCase):
    def test_health_is_process_only_and_ready_checks_the_db(self):
        svc = Service("safe")
        try:
            self.assertEqual(svc.get_json("/health"), (200, {"http_process": "UP"}))
            status, body = svc.get_json("/ready")
            self.assertEqual((status, body), (200, {"db": "READY"}))
        finally:
            svc.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
