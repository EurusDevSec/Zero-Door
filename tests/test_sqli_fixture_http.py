"""Socket-level (black-box) regressions for the ZER-41 fixture's HTTP lifecycle, admission and failure paths.

These drive a real loopback server and inspect raw wire bytes and the structured access log, so they hold
for any app that serves HTTP. The app under test is services/sqli-fixture/app.py or the path in ZD_SQLI_APP
(run against the pre-fix snapshot, these fail; against the fixed service, they pass).

  python -B tests/test_sqli_fixture_http.py
"""
import importlib.util
import io
import json
import os
import socket
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/zer41"


def load_app():
    path = os.environ.get("ZD_SQLI_APP") or str(ROOT / "services/sqli-fixture/app.py")
    spec = importlib.util.spec_from_file_location("zer41_app_http", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


app = load_app()


class Server:
    """A loopback fixture server whose stdout (the access log) and stderr are captured."""
    def __init__(self, profile="safe", max_connections=None):
        self.dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        env = {"ZD_SQLI_PROFILE": profile, "ZD_SQLI_DB_DIR": self.dir.name, "ZD_SQLI_PORT": "0",
               "ZD_SQLI_SEED": str(FIXTURES / "seed.json"), "ZD_SQLI_TOPOLOGY": "direct"}
        self.config = app.Config(env)
        self.out, self.err = io.StringIO(), io.StringIO()
        app.LOG = self.out  # capture the access log from the server thread
        with redirect_stdout(self.out), redirect_stderr(self.err):
            if max_connections is not None:
                seed_id, rows, _ = app.open_or_create(self.config)
                self.store = app.Store(self.config)
                self.httpd = app.FixtureServer((self.config.host, 0), app.make_handler(self.store),
                                               max_connections=max_connections)
            else:
                self.httpd, self.store, _, _ = app.build_server(self.config)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def logs(self):
        return [json.loads(x) for x in self.out.getvalue().splitlines() if x.strip()]

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        app.LOG = None
        self.dir.cleanup()


def send_raw(port, payload, read_timeout=2.0):
    sock = socket.create_connection(("127.0.0.1", port), timeout=read_timeout)
    sock.settimeout(read_timeout)
    try:
        sock.sendall(payload)
        chunks = []
        while True:
            try:
                part = sock.recv(65536)
            except socket.timeout:
                break
            if not part:
                break
            chunks.append(part)
        return b"".join(chunks)
    finally:
        sock.close()


def count_responses(wire):
    return wire.count(b"HTTP/1.")


class Framing(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.addCleanup(self.server.close)

    def test_one_request_one_response_then_close(self):
        wire = send_raw(self.server.port, b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n")
        self.assertEqual(count_responses(wire), 1)
        self.assertIn(b"Connection: close", wire)

    def test_pipelined_second_request_is_not_served(self):
        # Two requests sent back-to-back on one connection: the server answers the first and closes, so the
        # second is never executed (no keep-alive reuse, no shared identity).
        wire = send_raw(self.server.port,
                        b"GET /health HTTP/1.1\r\nHost: local\r\n\r\nGET /ready HTTP/1.1\r\nHost: local\r\n\r\n")
        self.assertEqual(count_responses(wire), 1)
        self.assertEqual(len(self.server.logs()), 1)

    def test_embedded_request_in_a_body_is_not_smuggled(self):
        # A POST whose body contains a full HTTP request, followed by a real request: exactly one response
        # and one access record for the one parsed request; the embedded bytes never become an operation.
        embedded = b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n"
        wire = (b"POST /no-route HTTP/1.1\r\nHost: local\r\nContent-Length: " + str(len(embedded)).encode()
                + b"\r\n\r\n" + embedded + b"GET /ready HTTP/1.1\r\nHost: local\r\n\r\n")
        response = send_raw(self.server.port, wire)
        self.assertEqual(count_responses(response), 1)
        self.assertIn(b"404", response.split(b"\r\n", 1)[0])
        logs = self.server.logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual((logs[0]["method"], logs[0]["status"]), ("POST", 404))

    def test_separate_connections_get_distinct_request_ids(self):
        send_raw(self.server.port, b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n")
        send_raw(self.server.port, b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n")
        ids = [l["request_id"] for l in self.server.logs()]
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(set(ids)), 2)


class Methods(unittest.TestCase):
    """Every rejection — an unsupported method (listed or not) or a malformed request — goes through one
    structured boundary: JSON body, X-Request-Id, exactly one access record, connection closed."""
    def setUp(self):
        self.server = Server()
        self.addCleanup(self.server.close)

    def rejected(self, payload, status):
        before = len(self.server.logs())
        wire = send_raw(self.server.port, payload)
        head, _, body = wire.partition(b"\r\n\r\n")
        self.assertEqual(count_responses(wire), 1, wire[:200])
        self.assertIn(str(status).encode(), head.split(b"\r\n", 1)[0])
        self.assertIn(b"X-Request-Id", head)           # structured, never the inherited HTML page
        self.assertIn(b"Connection: close", head)
        records = self.server.logs()[before:]
        self.assertEqual(len(records), 1, records)
        self.assertEqual(records[0]["status"], status)
        return body, records[0]

    def test_unsupported_methods_listed_or_not_are_structured_405(self):
        for method in ("PUT", "TRACE", "FOO", "OPTIONS", "PATCH"):
            with self.subTest(method=method):
                body, record = self.rejected(
                    method.encode() + b" /health HTTP/1.1\r\nHost: local\r\nContent-Length: 0\r\n\r\n", 405)
                self.assertEqual(json.loads(body)["error"], "METHOD_NOT_ALLOWED")
                self.assertEqual(record["method"], method)

    def test_head_is_rejected_without_a_body(self):
        body, record = self.rejected(b"HEAD /health HTTP/1.1\r\nHost: local\r\n\r\n", 405)
        self.assertEqual(body, b"")
        self.assertEqual(record["method"], "HEAD")

    def test_malformed_request_line_is_structured_400(self):
        # No trailing bytes after what the parser consumes, so the reply is never lost to a reset.
        body, _ = self.rejected(b"GARBAGE\r\n", 400)
        self.assertEqual(json.loads(body)["error"], "BAD_REQUEST")

    def test_unsupported_http_version_is_structured_505(self):
        body, _ = self.rejected(b"GET /health HTTP/9.9\r\n", 505)
        self.assertEqual(json.loads(body)["error"], "HTTP_VERSION_NOT_SUPPORTED")

    def test_too_many_headers_is_structured_431(self):
        headers = b"".join(b"X-H%d: v\r\n" % i for i in range(101))  # stdlib limit is 100 header lines
        body, _ = self.rejected(b"GET /health HTTP/1.1\r\n" + headers, 431)
        self.assertEqual(json.loads(body)["error"], "HEADERS_TOO_LARGE")


def dribble(sock, payload, every_s, stop):
    """Send `payload` one byte at a time, `every_s` apart, until done, stopped, or the peer closes."""
    for byte in payload:
        if stop.wait(every_s):
            return
        try:
            sock.sendall(bytes([byte]))
        except OSError:
            return


class Transport(unittest.TestCase):
    """The request budget is an absolute deadline: steady byte-by-byte progress must not extend it."""
    def setUp(self):
        self.server = Server()
        self.addCleanup(self.server.close)
        self.limit = app.REQUEST_BUDGET_S + 1.0  # the budget plus scheduling margin

    def progressive(self, head, trickle):
        stop = threading.Event()
        sock = socket.create_connection(("127.0.0.1", self.server.port), timeout=2)
        sock.settimeout(app.REQUEST_BUDGET_S + 3)
        sender = threading.Thread(target=dribble, args=(sock, trickle, 0.4, stop), daemon=True)
        start = time.monotonic()
        try:
            sock.sendall(head)
            sender.start()
            try:
                answer = sock.recv(65536)
            except socket.timeout:
                answer = None  # nothing within budget + 3 s: the deadline was not enforced
            except ConnectionResetError:
                answer = b""
            return answer, time.monotonic() - start
        finally:
            stop.set()
            sock.close()
            sender.join(2)

    def settled_records(self, expected, timeout=2.0):
        # The server writes the access record right after the response (so it knows whether it was
        # delivered); a client that reads only the first chunk can get there first. Wait, bounded, for the
        # record, then assert the exact list.
        end = time.monotonic() + timeout
        while len(self.server.logs()) < expected and time.monotonic() < end:
            time.sleep(0.02)
        return self.server.logs()

    def still_serving(self):
        wire = send_raw(self.server.port, b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n")
        self.assertIn(b"200", wire.split(b"\r\n", 1)[0])  # the timed-out connection released its slot

    def test_dribbled_body_is_cut_at_the_request_budget(self):
        body = b'{"item":"probe-item","note":"probe-note"}'
        head = b"POST /fixture/orders HTTP/1.1\r\nHost: local\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n"
        answer, elapsed = self.progressive(head, body)  # ~16 s of steady progress if never cut
        self.assertIsNotNone(answer, "no answer: progress kept extending the read")
        self.assertLessEqual(elapsed, self.limit)
        self.assertTrue(answer == b"" or b"408" in answer.split(b"\r\n", 1)[0], answer[:120])
        records = self.settled_records(1)
        self.assertEqual([(r["method"], r["status"]) for r in records], [("POST", 408)])
        # No order may have been written from a request that never fully arrived.
        db = sqlite3.connect(self.server.config.db_path)
        try:
            self.assertEqual(db.execute("SELECT count(*) FROM orders").fetchone()[0], 0)
        finally:
            db.close()
        self.still_serving()

    def test_dribbled_headers_are_cut_at_the_request_budget(self):
        answer, elapsed = self.progressive(b"GET /health HTTP/1.1\r\nHost: local\r\n", b"X-Slow: " + b"a" * 60)
        self.assertIsNotNone(answer, "no answer: header progress kept extending the read")
        self.assertLessEqual(elapsed, self.limit)
        self.assertTrue(answer == b"" or b"408" in answer.split(b"\r\n", 1)[0], answer[:120])
        self.assertEqual([r["status"] for r in self.settled_records(1)], [408])
        self.still_serving()

    def test_dribbled_request_line_is_cut_at_the_request_budget(self):
        # Progress inside the very first line: the request is not yet identified, yet bytes arrived, so it
        # still gets a 408 and one record rather than an unobserved crash.
        answer, elapsed = self.progressive(b"GET /hea", b"lth-" + b"a" * 60)
        self.assertIsNotNone(answer, "no answer: request-line progress kept extending the read")
        self.assertLessEqual(elapsed, self.limit)
        self.assertTrue(answer == b"" or b"408" in answer.split(b"\r\n", 1)[0], answer[:120])
        self.assertEqual([r["status"] for r in self.settled_records(1)], [408])
        self.still_serving()

    def test_idle_connection_is_closed_at_the_budget_without_a_record(self):
        sock = socket.create_connection(("127.0.0.1", self.server.port), timeout=2)
        sock.settimeout(app.REQUEST_BUDGET_S + 3)
        start = time.monotonic()
        try:
            try:
                closed = sock.recv(65536) == b""
            except socket.timeout:
                closed = False
            except ConnectionResetError:
                closed = True
        finally:
            sock.close()
        self.assertTrue(closed)
        self.assertLessEqual(time.monotonic() - start, self.limit)
        self.assertEqual(self.server.logs(), [])  # nothing was sent, so there is no request to record
        self.still_serving()

    def test_connection_admission_limit_refuses_excess_fast(self):
        server = Server(max_connections=2)
        self.addCleanup(server.close)
        holders = [socket.create_connection(("127.0.0.1", server.port), timeout=2) for _ in range(2)]
        try:
            # Two slots are held by idle connections; a third is refused (closed) without a response.
            extra = socket.create_connection(("127.0.0.1", server.port), timeout=2)
            extra.settimeout(2)
            try:
                extra.sendall(b"GET /health HTTP/1.1\r\nHost: local\r\n\r\n")
                try:
                    refused = extra.recv(65536) == b""   # closed with no response
                except ConnectionResetError:
                    refused = True                        # Windows surfaces the refusal as a reset
                self.assertTrue(refused)
            finally:
                extra.close()
        finally:
            for h in holders:
                h.close()


class Admission(unittest.TestCase):
    def test_search_fails_fast_when_all_db_slots_are_busy(self):
        # Deadline-before-wait: with every search slot held, a search returns 503 within the request budget
        # instead of queueing behind a freshly-started query clock.
        server = Server()
        self.addCleanup(server.close)
        for _ in range(app.SEARCH_CONCURRENCY):
            server.store.search_gate.acquire()
        try:
            start = time.monotonic()
            wire = send_raw(server.port, b"GET /fixture/catalog/search?category=home HTTP/1.1\r\nHost: local\r\n\r\n",
                            read_timeout=app.REQUEST_BUDGET_S + 3)
            elapsed = time.monotonic() - start
            self.assertIn(b"503", wire.split(b"\r\n", 1)[0])
            self.assertIn(b"BUSY", wire)
            self.assertLessEqual(elapsed, app.REQUEST_BUDGET_S + 1.5)
        finally:
            for _ in range(app.SEARCH_CONCURRENCY):
                server.store.search_gate.release()


if __name__ == "__main__":
    unittest.main(verbosity=2)
