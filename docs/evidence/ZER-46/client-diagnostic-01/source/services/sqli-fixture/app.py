"""ZER-41 SQLi catalog fixture: a small internal test service (Python stdlib + SQLite).

Deliberately contains one opt-in vulnerable query profile so the SQLi vector can be exercised against a
fixture we own, with fully synthetic e-commerce data. This is an added experimental component, not a flaw
of Google Online Boutique, and it never talks to any service outside the lab. The default profile is safe
(parameter binding); the vulnerable profile must be turned on explicitly and only serves local testing.

Surface (all read-only against synthetic rows, except the owned-order CRUD probe):
  GET  /health                     process liveness only (does not prove the DB works)
  GET  /ready                      readiness: runs a trivial SELECT against the DB
  GET  /fixture/catalog/search     search the synthetic catalog; returns only rows the query grants
  POST /fixture/orders             create one owned order (parameterised), read back on a new connection
  GET  /fixture/orders/{ref}       read one order
  DELETE /fixture/orders/{ref}     delete one order by its ref (parameterised)

H-plane facts (profile/variant, seed answer table) never reach any container stream (stdout or stderr):
Fluent Bit tails both. The access log is structured JSON to stdout with a per-request id; it carries no
profile, cookies, auth or full headers. One request = one connection (Connection: close), so request
identity and timing are per request and an unread body can never become a second request.
"""
import io
import ipaddress
import json
import os
import re
import socket
import sqlite3
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from containment import FilePolicy, PolicyError  # noqa: E402
MAX_BODY = 4096            # request body cap for the order probe
MAX_RESPONSE = 256 * 1024  # serialized response cap
MAX_ROWS = 200             # catalog rows returned at most (injection cannot raise this; we fetch MAX_ROWS+1)
MAX_Q = 120                # search term length cap
QUERY_MS = 500             # wall-clock budget for one catalog query, once it is admitted
REQUEST_BUDGET_S = 3.0     # absolute, from request start: receive the whole request (line, headers, body) and
                           # reach a decision, including any wait for a DB slot. Progress does not extend it.
SEARCH_CONCURRENCY = 16    # concurrent catalog queries
WRITE_CONCURRENCY = 8      # concurrent order writes
MAX_CONNECTIONS = 64       # concurrent accepted connections (admission limit)
TRANSPORT_DEADLINE_S = 5.0  # absolute per connection, including writing the response; never extended by progress
SQLITE_MAX_LEN = 64 * 1024  # cap a single SQLite value/row length so one query cannot allocate without bound
CONTROL = re.compile(r"[\x00-\x1f\x7f]")
LOG = None  # access-log sink; None means the container's stdout (tests may redirect it)
CATALOG_COLUMNS = ("sku", "name", "category", "visibility", "price_cents")
SCALAR = (str, int, float)
# SQLite error names that mean the database is unavailable/contended (503), not bad client SQL (4xx).
DB_UNAVAILABLE = {"SQLITE_CANTOPEN", "SQLITE_IOERR", "SQLITE_NOTADB", "SQLITE_CORRUPT", "SQLITE_PERM", "SQLITE_READONLY"}
DB_BUSY = {"SQLITE_BUSY", "SQLITE_LOCKED", "SQLITE_PROTOCOL"}


class ConfigError(Exception):
    """A startup refusal. `code` and `setting` are neutral and may be shown on container streams; `detail`
    (paths, seed ids, attempted values) is for in-process callers only and is never printed by main()."""
    def __init__(self, code, setting=None, detail=""):
        super().__init__(detail or code)
        self.code, self.setting, self.detail = code, setting, detail


class Failure(Exception):
    """A classified terminal outcome: an HTTP status and a short machine reason."""
    def __init__(self, status, reason):
        super().__init__(reason)
        self.status, self.reason = status, reason


class Config:
    """Immutable runtime configuration; an invalid value refuses startup (never a silent safe-ish default)."""
    def __init__(self, env):
        profile = env.get("ZD_SQLI_PROFILE", "safe")
        if profile not in ("safe", "vulnerable"):
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_PROFILE", f"must be 'safe' or 'vulnerable', got {profile!r}")
        self.profile = profile
        topology = env.get("ZD_SQLI_TOPOLOGY", "proxied")
        if topology not in ("direct", "proxied"):
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_TOPOLOGY", f"must be 'direct' or 'proxied', got {topology!r}")
        self.topology = topology
        db_dir = env.get("ZD_SQLI_DB_DIR")
        if not db_dir:
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_DB_DIR", "required (the only directory the service may write)")
        self.db_dir = Path(db_dir).resolve()
        if not self.db_dir.is_dir() or not os.access(self.db_dir, os.W_OK):
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_DB_DIR", f"{self.db_dir} must be an existing writable directory")
        self.db_path = self.db_dir / "fixture.sqlite"
        self.seed_path = Path(env.get("ZD_SQLI_SEED", HERE / "seed.json")).resolve()
        if not self.seed_path.is_file():
            raise ConfigError("SEED_INVALID", "ZD_SQLI_SEED", f"seed file {self.seed_path} not found")
        self.host = env.get("ZD_SQLI_HOST", "127.0.0.1")
        try:
            self.port = int(env.get("ZD_SQLI_PORT", "9140"))
        except ValueError:
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_PORT", "must be an integer")
        if not 0 <= self.port <= 65535:
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_PORT", f"{self.port} out of range 0..65535")
        self.trusted_proxies = parse_networks(env.get("ZD_SQLI_TRUSTED_PROXIES", ""))
        self.containment = None
        policy_path = env.get("ZD_SQLI_CONTAINMENT_FILE", "")
        policy_scope = env.get("ZD_SQLI_CONTAINMENT_SCOPE", "")
        if policy_path or policy_scope:
            if not policy_path or not policy_scope or not Path(policy_path).is_absolute():
                raise ConfigError("CONFIG_INVALID", "ZD_SQLI_CONTAINMENT_FILE")
            try:
                self.containment = FilePolicy(policy_path, policy_scope)
            except PolicyError:
                raise ConfigError("CONFIG_INVALID", "ZD_SQLI_CONTAINMENT_SCOPE")


def parse_networks(raw):
    nets = []
    for token in (t.strip() for t in raw.split(",") if t.strip()):
        try:
            nets.append(ipaddress.ip_network(token, strict=False))
        except ValueError:
            raise ConfigError("CONFIG_INVALID", "ZD_SQLI_TRUSTED_PROXIES", f"entry {token!r} is not a valid IP/CIDR")
    return nets


def resolve_source(peer_ip, forwarded_for, trusted_proxies, topology):
    """Decide the request's source IP from the observed TCP peer, never from a client-declared header.

    The observed peer is always recorded separately from the *attributed* client. In `direct` topology the
    peer is the client. In `proxied` topology the peer is an ingress hop: the client is read from
    X-Forwarded-For only when the peer is a configured trusted proxy, walking right-to-left past trailing
    trusted hops; an untrusted peer, or absent/malformed/all-trusted forwarded data, leaves the client
    UNKNOWN. A forged header never promotes an unverified hop to the end client.
    """
    record = {"tcp_peer": peer_ip, "forwarded_for_seen": sanitise(forwarded_for, 256) if forwarded_for else None,
              "client_ip": None, "method": None, "confidence": "UNKNOWN", "topology": topology}
    try:
        peer = ipaddress.ip_address(peer_ip)
    except ValueError:
        record["method"] = "PEER_UNPARSEABLE"
        return record
    if topology == "direct":
        # No proxy in front: the observed peer is the end client; any X-Forwarded-For is client-declared and ignored.
        record.update(client_ip=peer_ip, method="DIRECT_PEER", confidence="OBSERVED_PEER")
        return record
    # proxied: the peer is an ingress hop, not proven to be the client.
    if not any(peer in net for net in trusted_proxies):
        record["method"] = "PEER_NOT_TRUSTED_PROXY"  # observed hop recorded; client stays UNKNOWN
        return record
    if not forwarded_for:
        record["method"] = "PROXY_NO_FORWARD"
        return record
    for hop in reversed([h.strip() for h in forwarded_for.split(",") if h.strip()]):
        try:
            address = ipaddress.ip_address(hop)
        except ValueError:
            record["method"] = "PROXY_BAD_FORWARD"  # the hop next to our trusted proxy is malformed: not trusted
            return record
        if any(address in net for net in trusted_proxies):
            continue  # another trusted hop, keep walking left
        record.update(client_ip=str(address), method="XFF_AFTER_TRUSTED", confidence="PROXY_CHAIN")
        return record
    record["method"] = "PROXY_ALL_TRUSTED"  # every hop was a trusted proxy; no client address remained
    return record


def sanitise(value, limit):
    return CONTROL.sub("�", str(value))[:limit]


def valid_correlation(value):
    """A client-supplied correlation id is accepted only if printable ASCII and bounded; else None, so it is
    never trusted as our request id and never written to the log raw (newline/log-injection guard)."""
    if value and not CONTROL.search(value) and value.isascii() and len(value) <= 128:
        return value
    return None


def create_db(path, seed):
    """Create a fresh seeded DB file. Caller guarantees the path does not already exist."""
    db = sqlite3.connect(path)
    try:
        db.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
        db.execute("CREATE TABLE catalog (sku TEXT PRIMARY KEY, name TEXT, category TEXT, "
                   "visibility TEXT, price_cents INTEGER)")
        db.execute("CREATE TABLE orders (order_ref TEXT PRIMARY KEY, item TEXT, note TEXT, status TEXT)")
        db.execute("INSERT INTO meta VALUES ('seed_id', ?)", (seed["seed_id"],))
        db.executemany("INSERT INTO catalog VALUES (:sku, :name, :category, :visibility, :price_cents)",
                       seed["catalog"])
        db.commit()
    finally:
        db.close()  # sqlite3's context manager commits but does not close; Windows then locks the file


def build_db(config):
    """Create a fresh seeded DB, replacing any existing file in the configured dir. Used by tests on an
    isolated temp dir. Startup uses open_or_create, which never erases an existing compatible DB."""
    if config.db_path.exists():
        config.db_path.unlink()
    seed = json.loads(config.seed_path.read_text(encoding="utf-8"))
    create_db(config.db_path, seed)
    return seed["seed_id"], len(seed["catalog"])


def open_or_create(config):
    """Open an existing compatible DB (keeping its orders) or create a fresh one; never erase before this.

    Returns (seed_id, catalog_rows, reused). An existing file whose meta seed_id does not match the
    configured seed, or that lacks the expected schema, refuses startup instead of being overwritten.
    """
    seed = json.loads(config.seed_path.read_text(encoding="utf-8"))
    if not config.db_path.exists():
        create_db(config.db_path, seed)
        return seed["seed_id"], len(seed["catalog"]), False
    db = sqlite3.connect(config.db_path)
    try:
        try:
            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        except sqlite3.DatabaseError:
            raise ConfigError("DB_INCOMPATIBLE", "ZD_SQLI_DB_DIR", f"{config.db_path} is not a SQLite database")
        if not {"meta", "catalog", "orders"} <= tables:
            raise ConfigError("DB_INCOMPATIBLE", "ZD_SQLI_DB_DIR",
                              f"{config.db_path} exists but is not a fixture DB (tables {sorted(tables)})")
        stored = db.execute("SELECT value FROM meta WHERE key='seed_id'").fetchone()
        if not stored or stored[0] != seed["seed_id"]:
            raise ConfigError("DB_INCOMPATIBLE", "ZD_SQLI_DB_DIR", f"{config.db_path} has seed_id "
                              f"{stored and stored[0]!r}, expected {seed['seed_id']!r}; refusing to overwrite")
        rows = db.execute("SELECT count(*) FROM catalog").fetchone()[0]
    finally:
        db.close()
    return seed["seed_id"], rows, True


class Store:
    """DB access: a read-only path for search (bounded), a read-write path for owned orders (bounded)."""
    def __init__(self, config):
        self.config = config
        self.search_gate = threading.BoundedSemaphore(SEARCH_CONCURRENCY)
        self.write_gate = threading.BoundedSemaphore(WRITE_CONCURRENCY)

    def _connect(self, mode):
        conn = sqlite3.connect(f"file:{self.config.db_path.as_posix()}?mode={mode}", uri=True, timeout=0.2)
        conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, SQLITE_MAX_LEN)
        return conn

    @staticmethod
    def _classify(error):
        name = getattr(error, "sqlite_errorname", "") or ""
        if "INTERRUPT" in name:
            return Failure(503, "QUERY_TIMEOUT")
        if name in DB_BUSY:
            return Failure(503, "DB_BUSY")
        if name in DB_UNAVAILABLE:
            return Failure(503, "DB_UNAVAILABLE")
        return Failure(400, "QUERY_REJECTED")  # SQLITE_ERROR: bad client SQL, multiple statements, etc.

    def search(self, category, deadline):
        """Catalog search bounded by `deadline` (a monotonic time). Safe profile binds the parameter;
        vulnerable profile interpolates it (the opt-in flaw). Both run read-only, single statement, with a
        value-length cap and a row cap, so even a successful injection can only read small synthetic rows.
        The deadline covers the wait for a DB slot, so a busy service fails fast rather than queueing."""
        if len(category) > MAX_Q:
            raise Failure(400, "CATEGORY_TOO_LONG")
        wait = deadline - time.monotonic()
        if wait <= 0:
            raise Failure(503, "DEADLINE_EXCEEDED")  # budget already spent before admission: not a busy DB
        if not self.search_gate.acquire(timeout=wait):
            raise Failure(503, "BUSY")
        base = ("SELECT sku, name, category, visibility, price_cents FROM catalog "
                "WHERE visibility = 'public' AND category = ")
        try:
            try:
                conn = self._connect("ro")
            except sqlite3.Error as error:
                raise self._classify(error)
            try:
                query_end = min(deadline, time.monotonic() + QUERY_MS / 1000)
                conn.set_progress_handler(lambda: 1 if time.monotonic() >= query_end else None, 1000)
                try:
                    if self.config.profile == "safe":
                        cur = conn.execute(base + "? ORDER BY sku", (category,))
                    else:
                        # Deliberately interpolated for the SQLi fixture. One statement only: sqlite3.execute
                        # rejects multiple statements, and the read-only connection rejects any write.
                        cur = conn.execute(base + "'" + category + "' ORDER BY sku")
                    fetched = cur.fetchmany(MAX_ROWS + 1)
                except (sqlite3.OperationalError, sqlite3.ProgrammingError, sqlite3.Warning) as error:
                    raise self._classify(error) if isinstance(error, sqlite3.OperationalError) \
                        else Failure(400, "QUERY_REJECTED")
                if len(fetched) > MAX_ROWS:
                    raise Failure(400, "TOO_MANY_ROWS")
                for row in fetched:
                    if any(value is not None and not isinstance(value, SCALAR) for value in row):
                        # An injected UNION can return a non-text value (e.g. a blob); reject it explicitly
                        # rather than crash during JSON encoding.
                        raise Failure(422, "RESULT_TYPE_UNSUPPORTED")
                return [dict(zip(CATALOG_COLUMNS, row)) for row in fetched]
            finally:
                conn.close()
        finally:
            self.search_gate.release()

    def create_order(self, item, note, deadline=None):
        wait = REQUEST_BUDGET_S if deadline is None else deadline - time.monotonic()
        if wait <= 0:
            raise Failure(503, "DEADLINE_EXCEEDED")
        if not self.write_gate.acquire(timeout=wait):
            raise Failure(503, "BUSY")
        try:
            ref = uuid.uuid4().hex
            db = self._connect("rw")
            try:
                db.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (ref, item, note, "STORED"))
                db.commit()
            finally:
                db.close()
            # Read back on an independent connection so the reply reflects committed state, not a cache.
            db = self._connect("rw")
            try:
                db.row_factory = sqlite3.Row
                row = db.execute("SELECT * FROM orders WHERE order_ref = ?", (ref,)).fetchone()
            finally:
                db.close()
            return dict(row)
        finally:
            self.write_gate.release()

    def read_order(self, ref):
        db = self._connect("rw")
        try:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM orders WHERE order_ref = ?", (ref,)).fetchone()
        finally:
            db.close()
        return dict(row) if row else None

    def delete_order(self, ref):
        db = self._connect("rw")
        try:
            cur = db.execute("DELETE FROM orders WHERE order_ref = ?", (ref,))
            db.commit()
            return cur.rowcount
        finally:
            db.close()

    def reset_orders(self):
        """Explicit, scoped reset: remove order rows only. Never touches catalog, the file, or the cluster."""
        db = self._connect("rw")
        try:
            db.execute("DELETE FROM orders")
            db.commit()
        finally:
            db.close()


class DeadlineReader(io.RawIOBase):
    """Raw socket reader with an absolute deadline: each recv gets only the time left, so a client that keeps
    sending a byte at a time cannot extend the request. Counts bytes so an idle connection that never sent
    anything can be told apart from a partial request."""
    def __init__(self, sock, deadline):
        self.sock, self.deadline, self.received = sock, deadline, 0

    def readable(self):
        return True

    def readinto(self, buffer):
        left = self.deadline() - time.monotonic()
        if left <= 0:
            raise TimeoutError("request deadline")
        self.sock.settimeout(left)
        count = self.sock.recv_into(buffer)
        self.received += count
        return count


REJECTION = {400: "BAD_REQUEST", 405: "METHOD_NOT_ALLOWED", 408: "REQUEST_TIMEOUT", 414: "URI_TOO_LONG",
             431: "HEADERS_TOO_LARGE", 505: "HTTP_VERSION_NOT_SUPPORTED"}


def make_handler(store):
    config = store.config

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        default_request_version = "HTTP/1.1"  # every reply, even to a malformed line, has a status line + headers
        server_version = "zd-sqli-fixture"
        sys_version = ""

        def log_message(self, *_args):
            pass  # access logging is the structured emit() below, never the default stderr line

        def log_request(self, *_args):
            pass  # stdlib's version reads self.requestline, which a request cut mid-line never got

        def setup(self):
            super().setup()
            self.read_deadline = time.monotonic() + REQUEST_BUDGET_S
            self.rfile.close()  # replace the plain socket file (closing it releases its socket reference)
            self.reader = DeadlineReader(self.connection, lambda: self.read_deadline)
            self.rfile = io.BufferedReader(self.reader)

        def handle_one_request(self):
            """One request on this connection, inside a single observation boundary: a parse error, an unknown
            method, a timeout or a disconnect each still give exactly one terminal record (stdlib's own loop
            body swallows timeouts and answers unknown methods with an HTML page and no record)."""
            self.request_id = uuid.uuid4().hex
            self.started = time.monotonic()
            self.read_deadline = self.deadline = self.started + REQUEST_BUDGET_S
            self.transport_deadline = self.started + TRANSPORT_DEADLINE_S
            self.correlation_id, self._source, self._emitted = None, None, False
            self.containment_record = {}
            # Defaults stdlib only sets inside parse_request, so a reply to a request cut mid-line still works.
            self.command, self.path, self.headers, self.requestline = None, "", None, ""
            self.request_version = "HTTP/1.1"
            self.close_connection = True  # one request per connection
            try:
                self.raw_requestline = self.rfile.readline(65537)
                if not self.raw_requestline:
                    return  # peer closed before sending anything: no request to record
                if len(self.raw_requestline) > 65536:
                    self.requestline, self.request_version, self.command = "", "HTTP/1.1", ""
                    return self.send_error(414)
                if not self.parse_request():
                    return  # parse_request answered through send_error (structured, recorded)
                handler = getattr(self, "do_" + self.command, None)
                if handler is None:
                    return self.send_error(405)
                handler()
            except TimeoutError:
                # The absolute request deadline passed while the request was still arriving. A partial request
                # is answered 408 within the transport deadline; an idle connection that sent nothing is closed.
                if not self._emitted and self.reader.received:
                    self.respond(408, {"error": "REQUEST_TIMEOUT"}, source=self._source)
            except OSError:
                if not self._emitted and self.reader.received:
                    # Client went away: record the real outcome, never a success.
                    self.emit(499, {"source": self._source or {}, "delivered": False})

        def send_error(self, code, message=None, explain=None):
            """Every stdlib rejection (bad request line/version/headers, URI too long) and every unsupported
            method goes through the same structured response and single record as our own replies."""
            status = 405 if int(code) == 501 else int(code)
            self.respond(status, {"error": REJECTION.get(status, "REQUEST_REJECTED")}, source=self.source())

        def emit(self, status, extra):
            if self._emitted:
                return
            self._emitted = True
            source = extra.pop("source", {}) or {}
            try:
                path = urlsplit(self.path or "").path
            except ValueError:
                path = self.path or ""
            record = {"ts": time.time(), "request_id": self.request_id,
                      "method": sanitise(self.command, 16) if self.command else None,
                      "path": sanitise(path, 256), "status": status,
                      "duration_ms": round((time.monotonic() - self.started) * 1000, 3),
                      "tcp_peer": source.get("tcp_peer"), "source_method": source.get("method"),
                      "source_confidence": source.get("confidence"), "client_ip": source.get("client_ip"),
                      "correlation_id": self.correlation_id, **self.containment_record, **extra}
            sink = LOG if LOG is not None else sys.stdout
            sink.write(json.dumps(record, separators=(",", ":")) + "\n")
            sink.flush()

        def respond(self, status, value, source=None, **log):
            """Send exactly one response and emit exactly one access record, then close. The write is bounded
            by the absolute transport deadline; if it cannot be delivered, the record says so."""
            self.close_connection = True
            if self._emitted:
                return
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            if len(raw) > MAX_RESPONSE:
                status, raw = 500, b'{"error":"RESPONSE_TOO_LARGE"}'
            left = self.transport_deadline - time.monotonic()
            if left <= 0:
                return self.emit(status, {"source": source or {}, "delivered": False, **log})
            try:
                self.connection.settimeout(left)
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Connection", "close")
                self.send_header("X-Request-Id", self.request_id)
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(raw)
                self.emit(status, {"source": source or {}, **log})
            except OSError:
                self.emit(status, {"source": source or {}, "delivered": False, **log})

        def declared_length(self):
            raw = self.headers.get("Content-Length")
            if raw is None:
                return 0
            try:
                return int(raw)
            except ValueError:
                return -1

        def read_body(self, length):
            """Read exactly the declared body under the request deadline (TimeoutError -> 408 upstream)."""
            if length <= 0:
                return b""
            body = self.rfile.read(length)
            if len(body) < length:
                raise Failure(400, "BODY_INCOMPLETE")
            return body

        def drain(self, length):
            # Discard an unexpected body (bounded) so the single response flushes before we close; the same
            # request deadline applies, so a dribbled unwanted body also ends in 408.
            remaining = min(max(length, 0), MAX_BODY)
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 65536))
                if not chunk:
                    break
                remaining -= len(chunk)

        def route(self):
            try:
                return urlsplit(self.path)
            except ValueError:
                raise Failure(400, "BAD_REQUEST_TARGET")

        def client_correlation(self):
            return valid_correlation(self.headers.get("X-Correlation-Id")) if self.headers is not None else None

        def source(self):
            forwarded = self.headers.get("X-Forwarded-For") if self.headers is not None else None
            return resolve_source(self.client_address[0], forwarded, config.trusted_proxies, config.topology)

        def guarded(self, handler):
            """Run one request handler, guaranteeing a single terminal record even on unexpected errors."""
            self.correlation_id = self.client_correlation()
            try:
                if config.containment and self.route().path.startswith("/fixture"):
                    self._source = self.source()
                    try:
                        verdict = config.containment.check(self._source)
                    except PolicyError as error:
                        raise Failure(503, str(error))
                    self.containment_record = verdict
                    if verdict["blocked"]:
                        self.drain(self.declared_length())
                        raise Failure(403, "SOURCE_BLOCKED")
                handler()
            except Failure as failure:
                self.respond(failure.status, {"error": failure.reason}, source=self._source)
            except TimeoutError:
                self.respond(408, {"error": "REQUEST_TIMEOUT"}, source=self._source)
            except (ConnectionError, BrokenPipeError):
                raise  # client gone; handle_one_request records it truthfully
            except Exception:  # never leak a traceback as the response; record one 500 and move on
                self.respond(500, {"error": "INTERNAL"}, source=self._source)

        def do_GET(self):
            self.guarded(self._get)

        def _get(self):
            self._source = self.source()
            length = self.declared_length()
            if length > 0:
                self.drain(length)
            route = self.route()
            if route.path == "/health":
                return self.respond(200, {"http_process": "UP"})
            if route.path == "/ready":
                try:
                    if config.containment:
                        config.containment.snapshot()
                    db = self.store_ready()
                    db.close()
                    return self.respond(200, {"db": "READY"})
                except sqlite3.Error:
                    return self.respond(503, {"db": "NOT_READY"})
                except PolicyError:
                    return self.respond(503, {"error": "CONTAINMENT_STATE_UNAVAILABLE"})
            if route.path == "/fixture/catalog/search":
                category = (parse_qs(route.query).get("category") or [""])[0]
                rows = store.search(category, self.deadline)
                restricted = sum(1 for r in rows if r["visibility"] != "public")
                return self.respond(200, {"results": rows, "count": len(rows)}, source=self._source,
                                    rows=len(rows), restricted_rows=restricted)
            if route.path.startswith("/fixture/orders/"):
                ref = route.path[len("/fixture/orders/"):]
                try:
                    row = store.read_order(ref)
                except sqlite3.Error as error:
                    raise store._classify(error)
                return self.respond(200 if row else 404, row or {"error": "NOT_FOUND"}, source=self._source)
            return self.respond(404, {"error": "NO_ROUTE"}, source=self._source)

        def store_ready(self):
            db = sqlite3.connect(f"file:{config.db_path.as_posix()}?mode=ro", uri=True, timeout=0.2)
            db.execute("SELECT 1 FROM catalog LIMIT 1").fetchone()
            return db

        def do_POST(self):
            self.guarded(self._post)

        def _post(self):
            self._source = self.source()
            length = self.declared_length()
            if self.route().path != "/fixture/orders":
                self.drain(length)
                return self.respond(404, {"error": "NO_ROUTE"}, source=self._source)
            if length == -1:
                return self.respond(400, {"error": "BAD_LENGTH"}, source=self._source)
            if not 0 < length <= MAX_BODY:
                self.drain(length)
                return self.respond(413, {"error": "BODY_SIZE"}, source=self._source)
            try:
                body = json.loads(self.read_body(length))
                item, note = str(body["item"]), str(body["note"])
            except (ValueError, KeyError, TypeError):
                return self.respond(400, {"error": "BAD_BODY"}, source=self._source)
            if len(item) > 256 or len(note) > 256:
                return self.respond(400, {"error": "FIELD_TOO_LONG"}, source=self._source)
            try:
                row = store.create_order(item, note, self.deadline)
            except sqlite3.Error as error:
                raise store._classify(error)
            return self.respond(201, row, source=self._source)

        def do_DELETE(self):
            self.guarded(self._delete)

        def _delete(self):
            self._source = self.source()
            length = self.declared_length()
            if length > 0:
                self.drain(length)
            route = self.route().path
            if not route.startswith("/fixture/orders/"):
                return self.respond(404, {"error": "NO_ROUTE"}, source=self._source)
            ref = route[len("/fixture/orders/"):]
            try:
                removed = store.delete_order(ref)
            except sqlite3.Error as error:
                raise store._classify(error)
            return self.respond(200 if removed else 404, {"deleted": removed}, source=self._source)

    return Handler


class FixtureServer(ThreadingHTTPServer):
    """ThreadingHTTPServer with a bounded number of concurrently accepted connections."""
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler, max_connections=MAX_CONNECTIONS):
        super().__init__(address, handler)
        self._slots = threading.BoundedSemaphore(max_connections)

    def process_request(self, request, client_address):
        if not self._slots.acquire(timeout=0.1):
            try:
                request.close()  # at capacity: refuse fast instead of growing threads without bound
            finally:
                return
        super().process_request(request, client_address)

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()

    def handle_error(self, request, client_address):
        # The default prints a full traceback (source lines, messages, paths) to stderr, which Fluent Bit
        # collects. Record only the error type, neutrally.
        sys.stderr.write(json.dumps({"event": "handler_error", "error": type(sys.exc_info()[1]).__name__},
                                    separators=(",", ":")) + "\n")
        sys.stderr.flush()


def build_server(config):
    # Open or create the DB without erasing an existing compatible one, then bind. A bind failure after this
    # never destroys prior order state (we only create when the file is absent).
    seed_id, rows, reused = open_or_create(config)
    store = Store(config)
    httpd = FixtureServer((config.host, config.port), make_handler(store))
    # Neutral startup line to stderr: no profile/variant, no seed answer table, no DB path. Fluent Bit tails
    # stderr too, so H-plane facts must not appear on any stream.
    sys.stderr.write(f"zd-sqli-fixture listening on {config.host}:{httpd.server_address[1]} "
                     f"(db {'reused' if reused else 'created'})\n")
    sys.stderr.flush()
    return httpd, store, seed_id, rows


def startup_failed(code, setting=None):
    """One neutral line on stderr: a reason code and, for configuration, the setting name. Never a traceback,
    path, seed id, profile or attempted value (Fluent Bit collects stderr; those details are H-side)."""
    record = {"event": "startup_failed", "reason": code}
    if setting:
        record["setting"] = setting
    sys.stderr.write(json.dumps(record, separators=(",", ":")) + "\n")
    sys.stderr.flush()


def main():
    try:
        config = Config(os.environ)
        httpd, _store, _seed, _rows = build_server(config)
    except ConfigError as error:
        startup_failed(error.code, error.setting)
        return 2
    except (ValueError, KeyError, TypeError):  # unreadable or ill-formed seed
        startup_failed("SEED_INVALID", "ZD_SQLI_SEED")
        return 1
    except sqlite3.Error:
        startup_failed("DB_ERROR", "ZD_SQLI_DB_DIR")
        return 1
    except OSError:  # bind or filesystem failure
        startup_failed("BIND_OR_IO_FAILED")
        return 1
    except Exception:
        startup_failed("STARTUP_ERROR")
        return 1
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
