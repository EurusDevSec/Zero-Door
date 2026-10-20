"""Independent probe (ZER-38) against loopback fakes owned by the test. No lab, no real service.

Fake Boutique/fixture servers run on 127.0.0.1 with an ephemeral port. Timeouts, slow-drip bodies
and cancellation go through real sockets, not raised exceptions.
"""
import ast
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))
from event_pipeline.contract import canonical, new_id, validate  # noqa: E402
from event_pipeline.store import Archive  # noqa: E402
from measurement.clock import ProbeClock, cristian, parse, stamp  # noqa: E402
from measurement.config import ConfigError, plan as check_plan  # noqa: E402
from measurement.flows import Flow, SpecError, boutique_spec, fixture_spec  # noqa: E402
from measurement.probe import ProbeRunner  # noqa: E402
from measurement.sink import MemorySink, Outbox, PersistenceFailure, Publisher, load_probe_key  # noqa: E402

DEMO_FORM = {"email": "probe@example.invalid", "street_address": "1 Lab Road", "zip_code": "10000", "city": "Local",
             "state": "LC", "country": "Lab", "credit_card_number": "4432801561520454",
             "credit_card_expiration_month": "1", "credit_card_expiration_year": "2030", "credit_card_cvv": "672"}
PRODUCT = "OLJCESPC7Z"
OTHER = "66VCHSJNUP"


class Boutique(BaseHTTPRequestHandler):
    """Online Boutique shaped fake. `mode` changes one behaviour; `log` keeps (method, path, cookie)."""
    mode, delay, log, sessions, order_seq = "ok", {}, [], {}, [0]

    def log_message(self, *args):
        pass

    def session(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            if part.strip().startswith("shop_session-id="):
                return part.strip().split("=", 1)[1]
        return None

    def send(self, code, body=b"", headers=()):
        self.send_response(code)
        for k, v in headers:
            self.send_header(k, v)
        if self.mode == "drip" and self.path == "/cart/checkout":
            self.end_headers()
            try:
                for byte in body:
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(0.3)
            except OSError:
                pass  # the probe gave up at its deadline and closed the socket
            return
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_any(self, method):
        cls = type(self)
        length = int(self.headers.get("Content-Length", "0") or 0)
        self.rfile.read(length)
        sid = self.session()
        cls.log.append((method, self.path, sid))
        time.sleep(cls.delay.get(f"{method} {self.path}", 0))
        headers = []
        if sid is None and cls.mode != "no_cookie":
            sid = "fixed-session" if cls.mode == "same_cookie" else uuid.uuid4().hex
            headers.append(("Set-Cookie", f"shop_session-id={sid}; Path=/"))
        cart = cls.sessions.setdefault(sid, [])
        if method == "GET" and self.path == "/":
            body = b"<html>home</html>" if cls.mode == "home_wrong" else f'<a href="/product/{PRODUCT}">Sunglasses</a>'.encode()
            return self.send(200, body, headers)
        if method == "GET" and self.path == f"/product/{PRODUCT}":
            return self.send(200, f'<form><input name="product_id" value="{PRODUCT}"></form>Sunglasses'.encode(), headers)
        if method == "POST" and self.path == "/cart":
            # duplicate: the add lands twice; extra_item: another product joins; wrong_item: only another one.
            cart += {"duplicate": [PRODUCT, PRODUCT], "extra_item": [PRODUCT, OTHER], "wrong_item": [OTHER]}.get(cls.mode, [PRODUCT])
            location = "http://evil.invalid/cart" if cls.mode == "redirect_out" else "/cart"
            return self.send(302, b"", headers + [("Location", location)])
        if method == "GET" and self.path == "/cart":
            # Shaped like the upstream cart template: one line per product with its SKU and quantity.
            lines = "".join(f'<div class="row"><a href="/product/{p}">x</a><div>SKU #{p}</div><div>Quantity: {cart.count(p)}</div></div>'
                            for p in dict.fromkeys(cart))
            return self.send(200, lines.encode(), headers)
        if method == "POST" and self.path == "/cart/empty":
            cart.clear()
            return self.send(302, b"", headers + [("Location", "/")])
        if method == "POST" and self.path == "/cart/checkout":
            if cls.mode == "checkout_unconfirmed" or not cart:
                return self.send(200, b"Your shopping cart is empty", headers)
            cart.clear()
            cls.order_seq[0] += 1
            order = "00000000-0000-4000-8000-000000000001" if cls.mode == "replay_order" else str(uuid.uuid4())
            return self.send(200, f"Your order is complete! Confirmation # {order}".encode(), headers)
        return self.send(404, b"not found", headers)

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")


class Fixture(BaseHTTPRequestHandler):
    """SYNTHETIC fixture fake: a benign order round trip through an in-memory table."""
    mode, log, table, last = "ok", [], {}, [None]

    def log_message(self, *args):
        pass

    def reply(self, code, value=None):
        body = json.dumps(value).encode() if value is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        cls = type(self)
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ref = uuid.uuid4().hex
        record = {"order_ref": ref, "item": data["item"], "note": data["note"], "status": "STORED"}
        if cls.mode == "wrong_note":
            record["note"] = "0" * 32
        if cls.mode == "inject_ref":
            record["order_ref"] = ref = "x\r\nX-Injected: 1/../../admin"
        cls.table[ref] = record
        cls.log.append(("POST", self.path))
        self.reply(200 if cls.mode == "status_200" else 201, record)

    def do_GET(self):
        cls = type(self)
        ref = self.path.rsplit("/", 1)[1]
        cls.log.append(("GET", self.path))
        record = cls.table.get(ref)
        if cls.mode == "stale_read" and cls.last[0]:
            record = cls.last[0]
        cls.last[0] = record
        self.reply(200 if record else 404, record)

    def do_DELETE(self):
        cls = type(self)
        cls.log.append(("DELETE", self.path))
        cls.table.pop(self.path.rsplit("/", 1)[1], None)
        self.reply(204)


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # the probe closing at its deadline or on cancel is expected here


def stop(server):
    server.shutdown()
    server.server_close()


def serve(handler, **attrs):
    cls = type("Fake" + handler.__name__, (handler,), dict({"log": [], "sessions": {}, "table": {}, "delay": {},
                                                             "order_seq": [0], "last": [None]}, **attrs))
    server = QuietServer(("127.0.0.1", 0), cls)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, cls, f"http://127.0.0.1:{server.server_address[1]}"


def make_plan(origin, flow="checkout", **over):
    plan = {"plan_version": "zd-measurement-plan/0", "provenance": "SYNTHETIC",
            "f01": {"delta_s": 0.2, "k": 3, "s_s": 1, "l_ms": 1500, "gap_s": 0.4, "eps_s": 1, "cap_det_s": 300, "cap_rec_s": 600},
            "probe": {"probe_id": "prb-0", "probe_version": "p0", "flow": flow, "clock_id": "clk-host", "clock_source": "HOST_SHARED"},
            "timeouts": {"step_s": 2, "transaction_s": 2},
            "budget": {"max_duration_s": 30, "max_samples": 3, "max_requests": 500, "grace_s": 5},
            "heartbeat_s": 1, "target": {"origin": origin, "allowed_origins": [origin]}}
    for key, value in over.items():
        plan[key] = dict(plan[key], **value) if isinstance(value, dict) and key in plan else value
    return check_plan(plan)


CONTEXT = {"run_id": new_id("run"), "trial_id": new_id("trl"), "group": "B1", "method_version": "m",
           "config_ref": "sha256:" + "0" * 64}


def run_probe(plan, flow, outbox_dir, sink=None, cancel=None, reference=None, journal=None):
    sink = sink or MemorySink()
    outbox = Outbox(Path(outbox_dir) / f"outbox-{uuid.uuid4().hex}.jsonl")
    clock = ProbeClock(plan["probe"]["clock_id"], plan["probe"]["clock_source"])
    runner = ProbeRunner(plan, flow, CONTEXT, clock, Publisher(outbox, sink), journal=journal, reference=reference, cancel=cancel)
    summary = runner.run()
    return summary, sink, outbox, runner


def samples(sink):
    return [e for e in sink.events if e["event_type"] == "PROBE_SAMPLE"]


class BoutiqueFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def probe(self, mode="ok", delay=None, samples_n=3, **plan_over):
        server, cls, url = serve(Boutique, mode=mode, delay=delay or {})
        self.addCleanup(stop, server)
        budget = dict({"max_samples": samples_n}, **plan_over.pop("budget", {}))
        plan = make_plan(url, budget=budget, **plan_over)
        flow = Flow(boutique_spec(PRODUCT, "Sunglasses", DEMO_FORM), url, [url])
        summary, sink, outbox, runner = run_probe(plan, flow, self.tmp.name)
        return summary, sink, cls, runner

    def test_business_pass_uses_a_new_session_every_sample_and_keeps_no_secrets(self):
        summary, sink, cls, _ = self.probe()
        got = samples(sink)
        self.assertEqual([0, 1, 2], [e["payload"]["sequence"] for e in got])
        self.assertTrue(all(e["payload"]["pass"] and e["payload"]["error_class"] is None for e in got))
        sessions = {sid for _, path, sid in cls.log if path == "/cart" and sid}
        self.assertEqual(3, len(sessions))
        blob = b"".join(canonical(e) for e in sink.events)
        for secret in list(sessions) + [DEMO_FORM["credit_card_number"]]:
            self.assertNotIn(secret.encode(), blob)
        for e in sink.events:
            self.assertIsNone(validate(e, "H", "probe"))
            self.assertEqual("PLANE_VIOLATION", validate(e, "O"))  # H evidence can never be ingested on O
            p = e["payload"]
            if e["event_type"] == "PROBE_SAMPLE":
                self.assertGreaterEqual(parse(p["t_end"]), parse(p["t_start"]))
        self.assertGreaterEqual(summary["heartbeats"], 2)
        self.assertEqual(0, summary["undelivered"])

    def test_wrong_business_content_fails_even_with_http_200(self):
        cases = {"home_wrong": ("CONTENT", "CONTENT_MISSING"), "checkout_unconfirmed": ("CONTENT", "CONTENT_MISSING"),
                 "no_cookie": ("CONTENT", "SESSION_NOT_ISSUED"), "redirect_out": ("CONTENT", "UNEXPECTED_REDIRECT")}
        for mode, (error, reason) in cases.items():
            _, sink, cls, _ = self.probe(mode, samples_n=1)
            p = samples(sink)[0]["payload"]
            self.assertEqual((False, error, reason), (p["pass"], p["error_class"], p["detail"]["reason"]), mode)
        # The failed checkout left a probe-owned cart: it is emptied with the same session, nothing else.
        _, sink, cls, _ = self.probe("checkout_unconfirmed", samples_n=1)
        added = [sid for m, path, sid in cls.log if (m, path) == ("POST", "/cart")]
        emptied = [sid for m, path, sid in cls.log if (m, path) == ("POST", "/cart/empty")]
        self.assertEqual(added, emptied)
        self.assertEqual({"cart": "DONE"}, samples(sink)[0]["payload"]["detail"]["cleanup"])

    def test_stale_session_and_replayed_response_are_failures(self):
        _, sink, _, _ = self.probe("same_cookie", samples_n=2)
        got = [e["payload"] for e in samples(sink)]
        self.assertTrue(got[0]["pass"])
        self.assertEqual("STALE_SESSION", got[1]["detail"]["reason"])
        _, sink, _, _ = self.probe("replay_order", samples_n=2)
        got = [e["payload"] for e in samples(sink)]
        self.assertTrue(got[0]["pass"])
        self.assertEqual("STALE_RESPONSE", got[1]["detail"]["reason"])

    def test_real_timeout_slow_drip_and_slow(self):
        start = time.monotonic()
        _, sink, _, _ = self.probe(delay={"GET /cart": 3.0}, samples_n=1)
        p = samples(sink)[0]["payload"]
        self.assertEqual(("TIMEOUT", "TRANSACTION_DEADLINE"), (p["error_class"], p["detail"]["reason"]))
        self.assertLess(p["latency_ms"], 2600)  # ended at the 2 s deadline, not after the 3 s server delay
        self.assertEqual("cart", p["detail"]["steps"][-1]["name"])
        _, sink, _, _ = self.probe("drip", samples_n=1)
        self.assertEqual("TIMEOUT", samples(sink)[0]["payload"]["error_class"])
        _, sink, _, _ = self.probe(delay={"GET /cart": 1.6}, samples_n=1)
        p = samples(sink)[0]["payload"]
        self.assertEqual((False, "SLOW", "LATENCY_ABOVE_L"), (p["pass"], p["error_class"], p["detail"]["reason"]))
        self.assertLess(time.monotonic() - start, 30)

    def test_connect_failure(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        # Windows answers a refused loopback connect after ~2 s of SYN retries: give it time to refuse.
        plan = make_plan(url, budget={"max_samples": 1}, timeouts={"step_s": 6, "transaction_s": 6})
        _, sink, _, _ = run_probe(plan, Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), self.tmp.name)
        p = samples(sink)[0]["payload"]
        self.assertEqual(("CONNECT", "CONNECT_REFUSED_OR_UNREACHABLE"), (p["error_class"], p["detail"]["reason"]))

    def test_cancel_mid_transaction_emits_no_sample_and_cleans_up(self):
        server, cls, url = serve(Boutique, delay={"GET /cart": 3.0})
        self.addCleanup(stop, server)
        plan = make_plan(url, budget={"max_samples": 5})
        cancel, journal = threading.Event(), []
        threading.Timer(0.6, cancel.set).start()
        summary, sink, _, runner = run_probe(plan, Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), self.tmp.name,
                                             cancel=cancel, journal=journal)
        self.assertEqual([], samples(sink))
        self.assertEqual(0, runner.sequence)
        self.assertEqual(1, summary["cancelled"])
        self.assertEqual("SAMPLE_CANCELLED", journal[0]["kind"])
        self.assertEqual({"cart": "DONE"}, journal[0]["cleanup"])
        self.assertIn(("POST", "/cart/empty"), [(m, p) for m, p, _ in cls.log])

    def test_overrun_skips_slots_instead_of_bursting(self):
        server, cls, url = serve(Boutique, delay={"GET /": 0.5})
        self.addCleanup(stop, server)
        plan = make_plan(url, budget={"max_samples": 4})
        summary, sink, _, _ = run_probe(plan, Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), self.tmp.name)
        starts = [parse(e["payload"]["t_start"]) for e in samples(sink)]
        self.assertGreater(summary["skipped_slots"], 0)
        self.assertTrue(all(b - a >= 450 for a, b in zip(starts, starts[1:])), starts)

    def test_request_budget_is_a_hard_stop(self):
        summary, sink, cls, _ = self.probe(samples_n=50, budget={"max_requests": 20, "max_samples": 50})
        self.assertEqual("MAX_REQUESTS", summary["stop_reason"])
        self.assertLessEqual(len(cls.log), 20)


class Delivery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server, _, self.url = serve(Boutique)
        self.addCleanup(stop, server)

    def tearDown(self):
        self.tmp.cleanup()

    def flow(self):
        return Flow(boutique_spec(PRODUCT, None, DEMO_FORM), self.url, [self.url])

    def test_sink_outage_keeps_raw_and_resends_the_same_envelope(self):
        sink = MemorySink(["retry"] * 40)
        summary, sink, outbox, _ = run_probe(make_plan(self.url), self.flow(), self.tmp.name, sink=sink)
        self.assertGreater(summary["undelivered"], 0)
        kept = dict(outbox.pending)
        reopened = Outbox(outbox.path)
        self.assertEqual(kept, reopened.pending)  # survives a restart byte for byte
        fresh = MemorySink()
        Publisher(reopened, fresh).flush(max_attempts=1)
        self.assertEqual(sorted(kept), sorted(e["event_id"] for e in fresh.events))
        self.assertEqual(0, len(reopened.pending))
        ordered = [e["payload"]["sequence"] for e in fresh.events + sink.events if e["event_type"] == "PROBE_SAMPLE"]
        self.assertEqual([0, 1, 2], sorted(ordered))

    def test_outbox_failure_stops_the_probe(self):
        calls = [0]
        original = Outbox.append

        def failing(self, record):
            calls[0] += 1
            if calls[0] == 4:
                raise PersistenceFailure("outbox write failed: OSError")
            return original(self, record)
        with patch.object(Outbox, "append", failing):
            summary, _, _, _ = run_probe(make_plan(self.url, budget={"max_samples": 10}), self.flow(), self.tmp.name)
        self.assertEqual("PERSISTENCE_FAILED", summary["stop_reason"])

    def test_h_only_identity(self):
        path = Path(self.tmp.name) / "keys.json"
        path.write_text(json.dumps({"probe": "p" * 40, "detector": "d" * 40}))
        with self.assertRaises(ValueError):
            load_probe_key(path)
        path.write_text(json.dumps({"probe": "p" * 40}))
        self.assertEqual("p" * 40, load_probe_key(path))
        for name in ("probe.py", "sink.py", "flows.py", "recovery.py", "scorer.py", "metrics.py", "output.py", "raw.py"):
            tree = ast.parse((ROOT / "agent-orchestrator/measurement" / name).read_text(encoding="utf-8"))
            imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
            self.assertNotIn("event_pipeline.client", imported, name)


class FixtureFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def probe(self, mode, n=1):
        server, cls, url = serve(Fixture, mode=mode)
        self.addCleanup(stop, server)
        plan = make_plan(url, flow="fixture", budget={"max_samples": n})
        _, sink, _, _ = run_probe(plan, Flow(fixture_spec(), url, [url]), self.tmp.name)
        return [e["payload"] for e in samples(sink)], cls

    def test_synthetic_fixture_round_trip_and_wrong_results(self):
        got, cls = self.probe("ok")
        self.assertTrue(got[0]["pass"])
        self.assertIn("SYNTHETIC", got[0]["detail"]["provenance"])
        self.assertEqual({"order": "DONE"}, got[0]["detail"]["cleanup"])
        self.assertEqual({}, cls.table)  # the probe deleted only what it created
        got, cls = self.probe("wrong_note")
        self.assertEqual("WRONG_RESULT", got[0]["detail"]["reason"])
        # The record does not echo this sample's nonce: ownership is unproven, so it is reported, never deleted.
        self.assertEqual({"order": "UNRESOLVED_OWNERSHIP"}, got[0]["detail"]["cleanup"])
        self.assertEqual(1, len(cls.table))
        self.assertNotIn("DELETE", [m for m, _ in cls.log])
        got, cls = self.probe("status_200")
        self.assertEqual("STATUS_200", got[0]["detail"]["reason"])
        # Unexpected status: ownership is unknown and no reference was captured, so nothing is deleted.
        self.assertEqual({"order": "UNRESOLVED_OWNERSHIP"}, got[0]["detail"]["cleanup"])
        self.assertNotIn("DELETE", [m for m, _ in cls.log])
        got, cls = self.probe("inject_ref")
        # A hostile reference is percent-encoded into one path segment: no header injection, no traversal.
        self.assertEqual((False, "STATUS_404"), (got[0]["pass"], got[0]["detail"]["reason"]))  # never a pass
        paths = [p for m, p in cls.log if m in ("GET", "DELETE")]
        self.assertEqual(["GET", "DELETE"], [m for m, _ in cls.log if m != "POST"])
        self.assertTrue(paths and all(p.startswith("/fixture/orders/x%0D%0AX-Injected%3A%201%2F..%2F..%2Fadmin") for p in paths), paths)
        got, _ = self.probe("stale_read", n=2)
        self.assertTrue(got[0]["pass"])
        self.assertEqual("WRONG_RESULT", got[1]["detail"]["reason"])


class SpecsPlansClocks(unittest.TestCase):
    def test_status_alone_is_not_a_business_check(self):
        spec = fixture_spec()
        spec["steps"][1] = {"name": "read", "method": "GET", "path": "/x", "status": [200]}
        with self.assertRaises(SpecError):
            Flow(spec, "http://127.0.0.1:1", ["http://127.0.0.1:1"])
        spec = fixture_spec()
        spec["steps"][0]["path"] = "/fixture/{unknown}"
        with self.assertRaises(SpecError):
            Flow(spec, "http://127.0.0.1:1", ["http://127.0.0.1:1"])
        with self.assertRaises(SpecError):
            Flow(fixture_spec(), "http://127.0.0.1:1", ["http://127.0.0.1:2"])

    def test_control_characters_never_reach_the_wire(self):
        from measurement.flows import Failure, request
        with patch.object(socket, "create_connection", side_effect=AssertionError("connected")):
            for url, headers in (("http://127.0.0.1:1/a" + chr(13) + chr(10) + "X: 1", []),
                                 ("http://127.0.0.1:1/caf" + chr(233), []),
                                 ("http://127.0.0.1:1/a", [("Cookie", "a=b" + chr(10) + "X: 1")])):
                with self.assertRaises(Failure) as failure:
                    request(url, "GET", headers, b"", time.perf_counter_ns() + 10**9, None)
                self.assertEqual("INVALID_REQUEST", failure.exception.reason)

    def test_plan_bounds_are_mandatory(self):
        good = make_plan("http://127.0.0.1:1")
        for broken in ({"budget": {}}, {"provenance": "LOCKED-ish"}, {"timeouts": {"step_s": 1, "transaction_s": 1}},
                       {"probe": dict(good["probe"], clock_source="OFF_HOST")}, {"f01": dict(good["f01"], k=0)}):
            plan = json.loads(json.dumps(good))
            plan.update(broken)
            with self.assertRaises(ConfigError):
                check_plan(plan)

    def test_clock_resolution_sync_and_failed_sync(self):
        host = ProbeClock("clk-host", "HOST_SHARED")
        self.assertGreaterEqual(host.resolution_ms, 1.0)
        off = ProbeClock("clk-off", "OFF_HOST")
        a, b = off.now_ms(), off.now_ms()
        self.assertLessEqual(a, b)

        class Ref:
            def read(self):
                return {"clock_id": "clk_host_lab", "utc_ms": off.now_ms() - 5000.0, "resolution_ms": 1}
        sync = cristian(off, Ref())
        self.assertAlmostEqual(5000.0, sync["offset_ms"], delta=50)
        self.assertGreater(sync["uncertainty_ms"], off.resolution_ms)
        server, _, url = serve(Boutique)
        self.addCleanup(stop, server)

        class Down:
            def read(self):
                raise OSError("reference down")
        plan = make_plan(url, probe={"clock_source": "OFF_HOST", "clock_id": "clk-off"},
                         clock_sync={"method": "cristian-http/0", "interval_s": 60, "reference_url": "http://127.0.0.1:9/"})
        with tempfile.TemporaryDirectory() as tmp:
            summary, sink, _, _ = run_probe(plan, Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), tmp, reference=Down())
        self.assertEqual(2, summary["clock_sync_failed"])
        self.assertFalse([e for e in sink.events if e["event_type"] == "CLOCK_SYNC"])  # never a made-up offset 0
        self.assertEqual(stamp(0), "1970-01-01T00:00:00.000Z")


class ProbeToScorer(unittest.TestCase):
    def test_probe_events_are_accepted_by_h_archive_and_scored(self):
        """Integration: real probe events -> H Archive -> seal/export -> scorer (B0, no detector)."""
        from builder import HOST
        from measurement.raw import load
        from measurement.scorer import Scorer
        server, cls, url = serve(Boutique)
        self.addCleanup(stop, server)
        ctx = dict(CONTEXT, run_id=new_id("run"), trial_id=new_id("trl"), group="B0")
        inc = new_id("inc")
        plan = make_plan(url, budget={"max_samples": 20}, probe={"clock_id": "clk_host_lab"})
        clock = ProbeClock("clk_host_lab", "HOST_SHARED")
        sink = MemorySink()
        with tempfile.TemporaryDirectory() as tmp:
            outbox = Outbox(Path(tmp) / "o.jsonl")

            def toggle():
                time.sleep(0.9)
                cls.mode = "home_wrong"
                time.sleep(0.7)
                cls.mode = "ok"
            threading.Thread(target=toggle, daemon=True).start()
            t0 = clock.now_ms()
            runner = ProbeRunner(plan, Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), ctx, clock, Publisher(outbox, sink))
            runner.run()
            got = samples(sink)
            first_fail = next(e for e in got if not e["payload"]["pass"])
            t_eff = first_fail["payload"]["t_start"]

            def harness(typ, ts, payload, incident=False, plane="H", source="harness", clock_=HOST):
                e = {"schema_version": "zd-event/1.0.0", "event_id": new_id("evt"), "event_type": typ, "plane": plane,
                     "run_id": ctx["run_id"], "trial_id": None if typ in ("RUN_STARTED", "RUN_CONTEXT") else ctx["trial_id"],
                     "causation_id": None, "group": "B0", "method_version": "m", "config_ref": ctx["config_ref"],
                     "source_component": source, "source_instance": "hrn-0", "producer_version": "t", "stream": "h.control",
                     "seq": len(events), "target": {"namespace": "t", "service": "frontend", "flow": "checkout"},
                     "clock": dict(clock_), "ts_event": ts, "payload": payload}
                if incident:
                    e["incident_id"] = inc
                events.append((plane, e))
            events = []
            harness("RUN_STARTED", stamp(t0 - 2000), {"canary_token": "c", "protocol_ref": "p", "schedule_ref": "s",
                                                       "f01_params": plan["f01"], "reference_clock_id": "clk_host_lab"})
            harness("RUN_CONTEXT", stamp(t0 - 2000), {}, plane="O")
            harness("TRIAL_STARTED", stamp(t0 - 1000), {"warmup_end": got[2]["payload"]["t_start"], "planned_window": {},
                                                         "probes": [runner.registration()]})
            harness("ATTACK_REQUESTED", stamp(parse(t_eff) - 100), {"variant_ref": "v", "fault_params": {}, "attack_command": {},
                    "seed": 1, "onset_offset_ms": 0, "s_att": None, "known_good_revision": None, "target_services": ["frontend"]}, incident=True)
            harness("EFFECT_EVALUATED", stamp(clock.now_ms()), {"status": "CONFIRMED", "t_eff": t_eff, "evidence_clock_id": "clk_host_lab",
                    "criteria_version": "c", "w_eff_s": 30, "evidence": {"flow": "checkout"}, "reason": "probe"}, incident=True,
                    source="effect_evaluator")
            harness("TRIAL_ENDED", stamp(clock.now_ms() + 10), {"end_reason": "PLANNED"})
            archives = {"H": Archive(Path(tmp) / "h", "H"), "O": Archive(Path(tmp) / "o", "O")}
            try:
                for plane, e in events + [("H", e) for e in sink.events]:
                    archives[plane].ingest(e, {"kind": "file"}, e["source_component"])
                archives["H"].export(ctx["run_id"], Path(tmp) / "xh")
                archives["O"].export(ctx["run_id"], Path(tmp) / "xo")
            finally:
                for a in archives.values():
                    a.close()
            result = Scorer(*load(Path(tmp) / "xh", Path(tmp) / "xo")).run()
        r = result["incidents"][0]
        self.assertEqual("RECOVERED_UNDETECTED", r["label"], r)
        self.assertEqual("N/A", r["mttd"])
        self.assertGreater(r["total"], 0)


class Fix01Transaction(unittest.TestCase):
    """ZR10-08/09/10: the sample's own cart, hard step/run deadlines, proven cleanup ownership, interrupts."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def boutique(self, handler=Boutique, **attrs):
        server, cls, url = serve(handler, **attrs)
        self.addCleanup(stop, server)
        return cls, url, Flow(boutique_spec(PRODUCT, "Sunglasses", DEMO_FORM), url, [url])

    def test_cart_must_hold_exactly_the_requested_item(self):
        for mode, reason in (("duplicate", "WRONG_QUANTITY_OR_VALUE"), ("extra_item", "STALE_OR_WRONG_QUANTITY"),
                             ("wrong_item", "STALE_OR_WRONG_QUANTITY"), ("ok", None)):
            _, url, flow = self.boutique(mode=mode)
            _, sink, _, _ = run_probe(make_plan(url, budget={"max_samples": 1}), flow, self.tmp.name)
            p = samples(sink)[0]["payload"]
            self.assertEqual((mode == "ok", reason), (p["pass"], p["detail"]["reason"]), mode)
            if mode != "ok":
                self.assertEqual({"cart": "DONE"}, p["detail"]["cleanup"], mode)
        with self.assertRaises(SpecError):
            boutique_spec(PRODUCT, cart_markers={"line": "SKU #", "item": "SKU #"})

    def test_step_deadline_is_enforced_below_the_transaction_deadline(self):
        _, url, flow = self.boutique(delay={"GET /": 0.4})
        plan = make_plan(url, budget={"max_samples": 1}, timeouts={"step_s": 0.1, "transaction_s": 1}, f01={"l_ms": 900})
        _, sink, _, _ = run_probe(plan, flow, self.tmp.name)
        p = samples(sink)[0]["payload"]
        self.assertEqual((False, "TIMEOUT", "STEP_DEADLINE"), (p["pass"], p["error_class"], p["detail"]["reason"]))
        self.assertLess(p["detail"]["steps"][0]["ms"], 350)  # ended at the 0.1 s step deadline, not the 0.4 s reply

    def test_run_cap_cuts_the_transaction_and_bounds_the_cleanup(self):
        cls, url, flow = self.boutique(delay={"GET /cart": 1.0})
        plan = make_plan(url, budget={"max_samples": 10, "max_duration_s": 0.3, "grace_s": 2},
                         timeouts={"step_s": 2, "transaction_s": 2}, f01={"l_ms": 1500})
        journal = []
        started = time.monotonic()
        summary, sink, _, _ = run_probe(plan, flow, self.tmp.name, journal=journal)
        self.assertEqual(("MAX_DURATION", 0, 1), (summary["stop_reason"], summary["samples"], summary["cancelled"]))
        self.assertEqual([], samples(sink))  # a cut transaction is unknown, never a pass or a service failure
        cut = next(x for x in journal if x["kind"] == "SAMPLE_CANCELLED")
        self.assertEqual(("RUN_BUDGET", {"cart": "DONE"}), (cut["reason"], cut["cleanup"]))
        self.assertNotIn(("POST", "/cart/checkout"), [(m, p) for m, p, _ in cls.log])
        self.assertLess(time.monotonic() - started, 0.3 + 2 + 1.0)
        self.assertEqual((0.3, 2), (summary["max_duration_s"], summary["grace_s"]))

    def test_interrupt_takes_the_cancel_path_and_cleans_up(self):
        cls, url, flow = self.boutique()
        from measurement.flows import request

        def interrupting(url_, method, headers, body, deadline, cancel):
            if method == "GET" and url_.endswith("/cart"):
                raise KeyboardInterrupt()
            return request(url_, method, headers, body, deadline, cancel)
        journal, outbox = [], Outbox(Path(self.tmp.name) / "o.jsonl")
        runner = ProbeRunner(make_plan(url, budget={"max_samples": 3}), flow, CONTEXT, ProbeClock("clk-host", "HOST_SHARED"),
                             Publisher(outbox, MemorySink()), journal=journal, http=interrupting)
        summary = runner.run()
        self.assertEqual(("INTERRUPTED", 0, 1), (summary["stop_reason"], summary["samples"], summary["cancelled"]))
        cut = next(x for x in journal if x["kind"] == "SAMPLE_CANCELLED")
        self.assertEqual(("INTERRUPTED", {"cart": "DONE"}), (cut["reason"], cut["cleanup"]))
        self.assertTrue(all(not cart for cart in cls.sessions.values()))
        self.assertIn(("POST", "/cart/empty"), [(m, p) for m, p, _ in cls.log])

    def test_interrupt_after_the_add_request_still_owns_the_session_cart(self):
        cls, url, flow = self.boutique()
        from measurement.flows import Memory, request

        def interrupting(url_, method, headers, body, deadline, cancel):
            response = request(url_, method, headers, body, deadline, cancel)
            if method == "POST" and url_.endswith("/cart"):
                raise KeyboardInterrupt()  # the server added the item; the probe never saw the answer
            return response
        result = flow.run(time.perf_counter_ns() + 2 * 10**9, threading.Event(), Memory(), http=interrupting)
        self.assertEqual(("CANCELLED", "INTERRUPTED", {"cart": "DONE"}), (result["detail"], result["reason"], result["cleanup"]))
        self.assertTrue(all(not cart for cart in cls.sessions.values()))

    def test_cleanup_never_deletes_a_record_it_did_not_create(self):
        class StaleCreate(Fixture):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                type(self).log.append(("POST", self.path))
                self.reply(201, type(self).table["pre-existing-order"])
        old = {"order_ref": "pre-existing-order", "item": "benign-catalog-item", "note": "f" * 32, "status": "STORED"}
        server, cls, url = serve(StaleCreate, table={"pre-existing-order": old})
        self.addCleanup(stop, server)
        _, sink, _, _ = run_probe(make_plan(url, flow="fixture", budget={"max_samples": 1}), Flow(fixture_spec(), url, [url]), self.tmp.name)
        p = samples(sink)[0]["payload"]
        self.assertEqual((False, "WRONG_RESULT", {"order": "UNRESOLVED_OWNERSHIP"}), (p["pass"], p["detail"]["reason"], p["detail"]["cleanup"]))
        self.assertIn("pre-existing-order", cls.table)
        self.assertNotIn("DELETE", [m for m, _ in cls.log])

    def test_ownership_proof_is_mandatory_in_specs(self):
        spec = fixture_spec()
        del spec["steps"][0]["ownership"]
        with self.assertRaises(SpecError):
            Flow(spec, "http://127.0.0.1:1", ["http://127.0.0.1:1"])
        spec = fixture_spec()
        spec["steps"][0]["ownership"] = {"json_equals": {"item": "{item}"}}  # no nonce: proves nothing
        with self.assertRaises(SpecError):
            Flow(spec, "http://127.0.0.1:1", ["http://127.0.0.1:1"])
        plan = json.loads(json.dumps(make_plan("http://127.0.0.1:1")))
        del plan["budget"]["grace_s"]
        with self.assertRaises(ConfigError):
            check_plan(plan)


class GatewayFake(BaseHTTPRequestHandler):
    """H gateway shaped fake: answers POST /events as scripted; records what reached it."""
    answer, got = (201, "RECORDED"), []

    def log_message(self, *args):
        pass

    def reply(self, code, body, headers=()):
        self.send_response(code)
        for k, v in headers:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        cls = type(self)
        event = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        cls.got.append(("POST", self.path, self.headers.get("Authorization")))
        code, status = cls.answer
        if 300 <= code < 400:
            return self.reply(code, b"", [("Location", status)])
        self.reply(code, json.dumps({"status": status, "event_id": event.get("event_id")}).encode())

    def do_GET(self):
        type(self).got.append(("GET", self.path, self.headers.get("Authorization")))
        self.reply(200, json.dumps({"status": "RECORDED", "event_id": "evt_any"}).encode())


class Fix01HSink(unittest.TestCase):
    """ZR10-11: the H write never follows a redirect or a proxy and accepts only the gateway's own ACK."""

    TOKEN = "SYNTHETIC_PROBE_TOKEN_" + "0" * 20

    def gateway(self, answer):
        server, cls, url = serve(GatewayFake, answer=answer, got=[])
        self.addCleanup(stop, server)
        return cls, url

    def test_redirects_are_refused_and_the_token_stays_home(self):
        from measurement.sink import HttpHSink, SinkRefused
        other, other_url = self.gateway((200, "RECORDED"))
        for code in (301, 302, 303, 307, 308):
            _, url = self.gateway((code, other_url + "/wrong-plane"))
            with self.assertRaises(SinkRefused) as refused:
                HttpHSink(url, self.TOKEN).deliver({"event_id": "evt_" + "1" * 32})
            self.assertEqual(f"REDIRECT_{code}", str(refused.exception))
        self.assertEqual([], other.got)  # nothing, and no Authorization header, reached the other origin

    def test_only_the_gateway_ack_counts(self):
        from measurement.sink import HttpHSink, Retry, SinkRefused
        event = {"event_id": "evt_" + "2" * 32}
        _, url = self.gateway((201, "RECORDED"))
        self.assertEqual(("DELIVERED", "RECORDED"), HttpHSink(url, self.TOKEN).deliver(event))
        _, url = self.gateway((200, "RECORDED"))
        with self.assertRaises(SinkRefused):
            HttpHSink(url, self.TOKEN).deliver(event)
        _, url = self.gateway((201, "SOMETHING_ELSE"))
        with self.assertRaises(SinkRefused):
            HttpHSink(url, self.TOKEN).deliver(event)
        _, url = self.gateway((202, "KAFKA_ACKNOWLEDGED"))
        with self.assertRaises(Retry):
            HttpHSink(url, self.TOKEN).deliver(event)

    def test_environment_proxy_is_ignored(self):
        from measurement.sink import HttpHSink
        proxy, proxy_url = self.gateway((201, "RECORDED"))
        home, url = self.gateway((201, "RECORDED"))
        with patch.dict("os.environ", {"HTTP_PROXY": proxy_url, "http_proxy": proxy_url, "NO_PROXY": "", "no_proxy": ""}):
            self.assertEqual("DELIVERED", HttpHSink(url, self.TOKEN).deliver({"event_id": "evt_" + "3" * 32})[0])
        self.assertEqual([], proxy.got)
        self.assertEqual(1, len(home.got))

    def test_refusal_stops_the_probe_and_keeps_the_outbox(self):
        from measurement.sink import HttpHSink
        other, other_url = self.gateway((200, "RECORDED"))
        _, h_url = self.gateway((302, other_url + "/x"))
        _, url = serve_boutique(self)
        outbox = Outbox(Path(self.tmp_dir()) / "o.jsonl")
        runner = ProbeRunner(make_plan(url), Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]), CONTEXT,
                             ProbeClock("clk-host", "HOST_SHARED"), Publisher(outbox, HttpHSink(h_url, self.TOKEN)))
        summary = runner.run()
        self.assertEqual("SINK_REFUSED", summary["stop_reason"])
        self.assertGreater(summary["undelivered"], 0)
        self.assertEqual(summary["undelivered"], len(Outbox(outbox.path).pending))
        self.assertEqual([], other.got)

    def tmp_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name


def serve_boutique(case):
    server, cls, url = serve(Boutique)
    case.addCleanup(stop, server)
    return cls, url


if __name__ == "__main__":
    unittest.main()
