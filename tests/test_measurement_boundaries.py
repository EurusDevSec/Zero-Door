"""Final ZER-10 boundary regressions: real owned loopback I/O, no lab or model."""
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import socketserver

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "agent-orchestrator"), str(ROOT / "tests")]
from test_measurement_probe import (Boutique, DripAck, serve, stop, make_plan, CONTEXT, PRODUCT, DEMO_FORM)
from test_measurement_scorer import two_trials, score
from measurement.clock import ProbeClock, HttpReference
from measurement.flows import Flow, Memory, boutique_spec
from measurement.probe import ProbeRunner
from measurement.sink import Publisher, Outbox, MemorySink, HttpHSink


class RedirectIdentity(unittest.TestCase):
    def check_redirect(self, code, switch, second_hop=False, issue=False):
        class Redirect(Boutique):
            def handle_any(self, method):
                route = self.path == ("/" if issue else "/cart/checkout")
                hop = self.path == "/hop"
                if route or hop:
                    self.rfile.read(int(self.headers.get("Content-Length", 0)))
                    type(self).log.append((method, self.path, self.session()))
                    sid = self.session() or "new-probe-session"
                    change = switch and (hop if second_hop else route)
                    sid = "foreign-user" if change else sid
                    target = "/hop" if route and second_hop else "/cart/empty"
                    return self.send(code, b"", [("Set-Cookie", f"shop_session-id={sid}; Path=/"), ("Location", target)])
                return super().handle_any(method)
        server, cls, url = serve(Redirect, sessions={"foreign-user": ["foreign-product"]})
        self.addCleanup(stop, server)
        result = Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url]).run(
            time.perf_counter_ns() + int(3e9), threading.Event(), Memory())
        self.assertEqual(["foreign-product"], cls.sessions["foreign-user"])
        self.assertFalse(any(s == "foreign-user" for _, _, s in cls.log), cls.log)
        if switch and not (issue and not second_hop):
            self.assertEqual("SESSION_CHANGED", result["reason"])
        # In the issue step the first session is untrusted until issued; it cannot change on a later hop.
        return result, cls

    def test_changed_session_before_any_redirect_hop(self):
        for code in (301, 302, 303, 307, 308):
            for second in (False, True):
                with self.subTest(code=code, second_hop=second):
                    self.check_redirect(code, True, second)

    def test_same_session_redirect_controls(self):
        for code in (307, 308):
            with self.subTest(code=code):
                self.check_redirect(code, False, second_hop=True)

    def test_issue_step_pins_first_session_before_later_hops(self):
        # Home needs redirects enabled to exercise issuance across a chain.
        class Issue(Boutique):
            def do_GET(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                type(self).log.append(("GET", self.path, self.session()))
                if self.path == "/":
                    return self.send(302, b"", [("Set-Cookie", "shop_session-id=probe-user; Path=/"), ("Location", "/hop")])
                return self.send(307, b"", [("Set-Cookie", "shop_session-id=foreign-user; Path=/"), ("Location", "/cart/empty")])
        server, cls, url = serve(Issue, sessions={"foreign-user": ["foreign-product"]})
        self.addCleanup(stop, server)
        spec = boutique_spec(PRODUCT, None, DEMO_FORM)
        spec["steps"][0]["follow_redirects"] = True
        result = Flow(spec, url, [url]).run(time.perf_counter_ns() + int(3e9), threading.Event(), Memory())
        self.assertEqual("SESSION_CHANGED", result["reason"])
        self.assertEqual(["/", "/hop"], [p for _, p, _ in cls.log])
        self.assertEqual(["foreign-product"], cls.sessions["foreign-user"])


class ActiveStop(unittest.TestCase):
    def run_case(self, case, delay, repeat=False):
        holder, requested = {}, []
        timers = []

        def request_stop():
            requested.append(time.perf_counter_ns())
            holder["runner"].stop()
            if repeat:
                timer = threading.Timer(0.12, holder["runner"].stop)
                timers.append(timer)
                timer.start()

        def schedule_stop():
            timer = threading.Timer(0.05, request_stop)
            timers.append(timer)
            timer.start()

        class H(DripAck):
            def do_POST(self):
                # Final flush must stop an already-open request too, with no renewed grace.
                if case != "final_flush" or len(type(self).got) == 1:
                    schedule_stop()
                    type(self).before = delay
                else:
                    type(self).before = 0
                return super().do_POST()

        class Reference(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                schedule_stop()
                time.sleep(delay)
                raw = json.dumps({"clock_id": "clk-host", "utc_ms": time.time() * 1000, "resolution_ms": 1}).encode()
                try:
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                except OSError:
                    pass

        class Cleanup(Boutique):
            def handle_any(self, method):
                if self.path == "/cart/empty":
                    schedule_stop()
                return super().handle_any(method)

        servers = []
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bs, bc, url = serve(Cleanup if case == "cleanup" else Boutique,
                                    mode="checkout_unconfirmed" if case == "cleanup" else "ok",
                                    delay={"POST /cart/empty": delay} if case == "cleanup" else {})
                servers.append(bs)
                plan = make_plan(url, budget={"max_duration_s": 10, "grace_s": 0.2, "max_samples": 1})
                flow = Flow(boutique_spec(PRODUCT, None, DEMO_FORM), url, [url])
                sink, reference = MemorySink(), None
                if case in ("H_ACK", "final_flush"):
                    hs, hc, hurl = serve(H, got=[], pause=0.0)
                    servers.append(hs)
                    sink = HttpHSink(hurl, "SYNTHETIC_" + "0" * 40, timeout_s=3)
                if case == "reference":
                    rs, _, rurl = serve(Reference)
                    servers.append(rs)
                    reference = HttpReference(rurl, timeout_s=3)
                    plan["clock_sync"] = {"method": "cristian-http/0", "interval_s": 5}
                outbox = Outbox(Path(tmp) / "outbox.jsonl")
                runner = ProbeRunner(plan, flow, CONTEXT, ProbeClock("clk-host", "HOST_SHARED"),
                                     Publisher(outbox, sink), reference=reference)
                holder["runner"] = runner
                result = runner.run()
                end = time.perf_counter_ns()
                self.assertTrue(requested, case)
                self.assertEqual("INTERRUPTED", result["stop_reason"], case)
                self.assertLess((end - requested[0]) / 1e9, 0.65, case)  # .2 grace + .2 read slice + scheduling
                self.assertEqual(result["undelivered"], len(Outbox(outbox.path).pending))
                if delay > 1 and case in ("H_ACK", "final_flush"):
                    self.assertGreater(result["undelivered"], 0)
                if case == "cleanup":
                    if delay > 1:
                        self.assertEqual([{"cart": "GRACE_EXPIRED"}], [x["cleanup"] for x in result["unresolved_cleanup"]])
                    else:
                        self.assertEqual([], result["unresolved_cleanup"])
                if repeat:
                    self.assertLessEqual(runner.stop_requested_ns, requested[0] + int(0.01e9))
                return result
        finally:
            for timer in timers:
                timer.join()
            for server in servers:
                stop(server)

    def test_stop_interrupts_active_h_reference_cleanup_and_final_flush(self):
        for case in ("H_ACK", "reference", "cleanup", "final_flush"):
            with self.subTest(case=case):
                self.run_case(case, 1.2)

    def test_fast_io_finishes_within_grace_controls(self):
        for case in ("H_ACK", "reference", "cleanup", "final_flush"):
            with self.subTest(case=case):
                self.run_case(case, 0.1)

    def test_repeated_stop_does_not_extend_active_io(self):
        self.run_case("H_ACK", 1.2, repeat=True)


class UsageIncidentBuckets(unittest.TestCase):
    def test_conflict_marks_both_incidents_and_counts_one_global_call(self):
        tr = two_trials(False)
        calls = [e for _, e in tr.events if e["event_type"] == "LLM_CALL"]
        calls[1]["call_id"] = calls[0]["call_id"]
        result = score(tr)
        usage = result["metrics"]["M11_usage"]
        self.assertEqual({x["incident_id"] for x in result["incidents"]}, set(usage["by"]["incident"]))
        self.assertEqual(1, usage["calls"])
        for bucket in usage["by"]["incident"].values():
            self.assertEqual(("MISSING", "MISSING", "MISSING"),
                             (bucket["call_coverage_status"], bucket["usage_status"], bucket["cost_status"]))
        self.assertEqual(1, next(iter(usage["by"]["run"].values()))["calls"])

    def test_distinct_calls_keep_incident_coverage_complete(self):
        result = score(two_trials(False))
        usage = result["metrics"]["M11_usage"]
        self.assertEqual(2, usage["calls"])
        self.assertEqual(2, len(usage["by"]["incident"]))
        self.assertTrue(all(x["call_coverage_status"] == "COMPLETE" for x in usage["by"]["incident"].values()))


class TransportStop(unittest.TestCase):
    def test_live_deadline_also_interrupts_tls_and_blocked_send(self):
        from measurement.flows import Failure, request
        for secure in (False, True):
            with self.subTest(secure=secure):
                bound = [time.perf_counter_ns() + int(3e9)]
                stopped = []
                def shorten():
                    stopped.append(time.perf_counter_ns())
                    bound[0] = stopped[0] + int(0.2e9)
                class Silent(socketserver.BaseRequestHandler):
                    def handle(self):
                        # Accept the connection but neither read the POST nor answer the TLS handshake.
                        timer = threading.Timer(0.05, shorten)
                        timer.start()
                        time.sleep(1.2)
                        timer.join()
                class Server(socketserver.ThreadingTCPServer):
                    daemon_threads = True
                server = Server(("127.0.0.1", 0), Silent)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = f'{"https" if secure else "http"}://127.0.0.1:{server.server_address[1]}/'
                    with self.assertRaises(Failure) as error:
                        request(url, "POST", body=b"x" * (16 * 1024 * 1024), deadline_ns=lambda: bound[0])
                    self.assertEqual("TIMEOUT", error.exception.detail)
                    self.assertTrue(stopped)
                    self.assertLess((time.perf_counter_ns() - stopped[0]) / 1e9, 0.65)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()


if __name__ == "__main__":
    unittest.main()
