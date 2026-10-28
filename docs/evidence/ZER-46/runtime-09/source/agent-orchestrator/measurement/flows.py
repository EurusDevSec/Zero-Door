"""Business transactions for the independent probe: a bounded HTTP/1.1 client and a declarative flow.

The client is a small socket implementation so that every deadline is real: connect, TLS, send and
each read slice use the time left in the transaction, a slow-drip body still ends at the deadline,
and cancellation is noticed between read slices. Each sample uses a new session (no cookie, cart
or response is reused) and checks business content, not only HTTP status.

Nothing secret is kept: samples record step names, status codes, timings and short reason codes.
Cookie values, form values and page bodies are never stored; freshness checks keep SHA-256 prefixes.
"""
import copy
import hashlib
import json
import re
import select
import socket
import ssl
import time
import uuid
from http.cookies import CookieError, SimpleCookie
from urllib.parse import quote, urlencode, urljoin, urlsplit

from .config import origin

# Detail class -> zd-event/1.0.0 PROBE_SAMPLE.error_class. The detail travels in an additive field
# (docs/design/r1-measurement.md, MINOR proposal); 1.0.0 consumers only see the four locked values.
ERROR_CLASS = {"TIMEOUT": "TIMEOUT", "CONNECT": "CONNECT", "TLS": "CONNECT", "HTTP": "CONTENT",
               "PARSE": "CONTENT", "SCHEMA": "CONTENT", "BUSINESS": "CONTENT", "SLOW": "SLOW"}
MAX_BODY = 2 * 1024 * 1024
MAX_HEADER = 64 * 1024
SLICE_S = 0.2
TEMPLATE = re.compile(r"\{([a-z_][a-z0-9_]*)\}")
CONTROL = re.compile(r"[\x00-\x20\x7f]")


class Failure(Exception):
    """A classified transaction failure (detail class + short reason code)."""
    def __init__(self, detail, reason):
        super().__init__(f"{detail}:{reason}")
        self.detail, self.reason = detail, reason


class Cancelled(Exception):
    """The probe was stopped mid-transaction: the outcome is unknown, never pass or fail."""
    def __init__(self, reason="PROBE_STOPPED"):
        super().__init__(reason)
        self.reason = reason


class SpecError(ValueError):
    pass


class Response:
    __slots__ = ("status", "headers", "body")

    def __init__(self, status, headers, body):
        self.status, self.headers, self.body = status, headers, body

    def header(self, name):
        return [v for k, v in self.headers if k == name]


def deadline_value(bound):
    """Resolve a fixed monotonic deadline or a live bound shared by an in-flight request."""
    return bound() if callable(bound) else bound


def bounded_deadline(local, shared=None):
    """Keep the shared bound live; taking min() now would lose a later stop request."""
    return local if shared is None else lambda: min(deadline_value(local), deadline_value(shared))


def remaining(deadline_ns, cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled()
    left = (deadline_value(deadline_ns) - time.perf_counter_ns()) / 1e9
    if left <= 0:
        raise Failure("TIMEOUT", "TRANSACTION_DEADLINE")
    return left


def wait_socket(sock, write, deadline_ns, cancel):
    """Re-read the live bound while connect/TLS/send wait for readiness; no implicit retry."""
    while True:
        timeout = min(SLICE_S, remaining(deadline_ns, cancel))
        reads, writes, errors = select.select([] if write else [sock], [sock] if write else [], [sock], timeout)
        remaining(deadline_ns, cancel)
        if reads or writes or errors:
            return


def connect(host, port, deadline_ns, cancel):
    """Nonblocking TCP connect under the same live deadline as all later phases.

    OS hostname resolution itself is synchronous; runtime plans use IP literal loopback origins.
    Check the bound again after resolution, before any connection can be started.
    """
    remaining(deadline_ns, cancel)
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    for family, kind, proto, _, address in addresses:
        remaining(deadline_ns, cancel)
        sock = socket.socket(family, kind, proto)
        try:
            sock.setblocking(False)
            try:
                sock.connect(address)
            except (BlockingIOError, InterruptedError):
                wait_socket(sock, True, deadline_ns, cancel)
                error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if error:
                    raise OSError(error, "connect failed")
            return sock
        except OSError:
            sock.close()
        except BaseException:
            sock.close()
            raise
    raise OSError("no address reachable")


def request(url, method="GET", headers=(), body=b"", deadline_ns=0, cancel=None, max_body=MAX_BODY, ssl_context=None):
    """One HTTP/1.1 exchange with `Connection: close`. Raises Failure/Cancelled; returns Response."""
    if CONTROL.search(url) or not url.isascii() or \
            any(CONTROL.search(str(k)) or re.search(r"[\r\n\x00]", str(v)) or not str(v).isascii() for k, v in headers):
        raise Failure("HTTP", "INVALID_REQUEST")  # no request line or header injection, whatever a server returned
    parts = urlsplit(url)
    secure = parts.scheme == "https"
    port = parts.port or (443 if secure else 80)
    path = (parts.path or "/") + ("?" + parts.query if parts.query else "")
    try:
        sock = connect(parts.hostname, port, deadline_ns, cancel)
    except socket.timeout:
        raise Failure("TIMEOUT", "CONNECT_TIMEOUT") from None
    except OSError:
        raise Failure("CONNECT", "CONNECT_REFUSED_OR_UNREACHABLE") from None
    try:
        if secure:
            try:
                sock = (ssl_context or ssl.create_default_context()).wrap_socket(
                    sock, server_hostname=parts.hostname, do_handshake_on_connect=False)
                while True:
                    remaining(deadline_ns, cancel)
                    try:
                        sock.do_handshake()
                        break
                    except ssl.SSLWantReadError:
                        wait_socket(sock, False, deadline_ns, cancel)
                    except ssl.SSLWantWriteError:
                        wait_socket(sock, True, deadline_ns, cancel)
            except socket.timeout:
                raise Failure("TIMEOUT", "TLS_TIMEOUT") from None
            except ssl.SSLError:
                raise Failure("TLS", "TLS_HANDSHAKE") from None
            except OSError:
                raise Failure("TLS", "TLS_HANDSHAKE") from None
        lines = [f"{method} {path} HTTP/1.1", f"Host: {parts.netloc}", "Connection: close",
                 "User-Agent: zd-probe", "Accept-Encoding: identity"]
        lines += [f"{k}: {v}" for k, v in headers]
        if body or method in {"POST", "PUT"}:
            lines.append(f"Content-Length: {len(body)}")
        data = ("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + body  # ASCII checked before connecting
        try:
            offset = 0
            while offset < len(data):
                remaining(deadline_ns, cancel)
                try:
                    sent = sock.send(memoryview(data)[offset:])
                    if sent == 0:
                        raise OSError("connection closed while sending")
                    offset += sent
                except ssl.SSLWantReadError:
                    wait_socket(sock, False, deadline_ns, cancel)
                except (BlockingIOError, ssl.SSLWantWriteError):
                    wait_socket(sock, True, deadline_ns, cancel)
        except socket.timeout:
            raise Failure("TIMEOUT", "SEND_TIMEOUT") from None
        except OSError:
            raise Failure("CONNECT", "SEND_FAILED") from None
        return read_response(sock, deadline_ns, cancel, max_body)
    finally:
        sock.close()


def read_response(sock, deadline_ns, cancel, max_body):
    buffer = b""
    head = None
    while True:
        remaining(deadline_ns, cancel)  # even a complete reply must arrive before the live bound
        if head is None and b"\r\n\r\n" in buffer:
            raw, buffer = buffer.split(b"\r\n\r\n", 1)
            head = parse_head(raw)
        if head is not None:
            done = complete(head, buffer, max_body)
            if done is not None:
                return Response(head[0], head[1], done)
        if len(buffer) > (max_body if head else MAX_HEADER) + 65536:
            raise Failure("PARSE", "RESPONSE_TOO_LARGE")
        sock.settimeout(min(SLICE_S, remaining(deadline_ns, cancel)))
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            continue  # remaining() raises TIMEOUT/Cancelled on the next turn
        except ssl.SSLError:
            raise Failure("TLS", "TLS_READ") from None
        except OSError:
            raise Failure("HTTP", "CONNECTION_RESET") from None
        remaining(deadline_ns, cancel)
        if not chunk:
            if head is None:
                raise Failure("HTTP", "NO_RESPONSE" if not buffer else "TRUNCATED_HEADERS")
            if dict(head[1]).get("transfer-encoding") or dict(head[1]).get("content-length"):
                raise Failure("HTTP", "TRUNCATED_BODY")
            if len(buffer) > max_body:
                raise Failure("PARSE", "RESPONSE_TOO_LARGE")
            return Response(head[0], head[1], buffer)
        buffer += chunk


def parse_head(raw):
    try:
        text = raw.decode("latin-1")
        status_line, *rest = text.split("\r\n")
        version, code, *_ = status_line.split(" ", 2)
        if not version.startswith("HTTP/1.") or not code.isdigit() or len(code) != 3:
            raise ValueError
        headers = []
        for line in rest:
            name, value = line.split(":", 1)
            headers.append((name.strip().lower(), value.strip()))
        return int(code), headers
    except ValueError:
        raise Failure("HTTP", "MALFORMED_RESPONSE") from None


def complete(head, buffer, max_body):
    """The body once fully received, else None (more bytes needed)."""
    headers = dict(head[1])
    if head[0] in (204, 304) or 100 <= head[0] < 200:
        return b""
    if "chunked" in headers.get("transfer-encoding", "").lower():
        body, rest = b"", buffer
        while True:
            if b"\r\n" not in rest:
                return None
            size_line, rest = rest.split(b"\r\n", 1)
            try:
                size = int(size_line.split(b";")[0], 16)
            except ValueError:
                raise Failure("HTTP", "MALFORMED_CHUNK") from None
            if size == 0:
                return body
            if len(rest) < size + 2:
                return None
            body += rest[:size]
            if len(body) > max_body:
                raise Failure("PARSE", "RESPONSE_TOO_LARGE")
            rest = rest[size + 2:]
    if "content-length" in headers:
        try:
            length = int(headers["content-length"])
        except ValueError:
            raise Failure("HTTP", "MALFORMED_LENGTH") from None
        if length > max_body:
            raise Failure("PARSE", "RESPONSE_TOO_LARGE")
        return buffer[:length] if len(buffer) >= length else None
    return None  # read until close


def digest(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


class Memory:
    """Probe-lifetime freshness memory: SHA-256 prefixes of session IDs and captured business IDs."""
    def __init__(self, cap=200000):
        self.cap, self.seen = cap, {}

    def fresh(self, kind, value):
        key = (kind, digest(value))
        if key in self.seen:
            return False
        if len(self.seen) >= self.cap:
            self.seen.pop(next(iter(self.seen)))
        self.seen[key] = True
        return True


STEP_KEYS = {"name", "method", "path", "status", "form", "json", "contains", "contains_ci", "absent", "count",
             "capture", "json_schema", "json_equals", "capture_json", "session", "redirect_to",
             "follow_redirects", "owns", "ownership", "releases", "fresh"}
NEVER = float("inf")
TYPES = {"str": str, "int": int, "bool": bool, "list": list, "object": dict}


class Flow:
    """A declarative business transaction (see docs/design/r1-measurement.md, flow spec).

    `run` returns a dict: ok, detail, reason, steps, requests, cleanup, captures (hashed).
    """
    def __init__(self, spec, base_origin, allowed_origins):
        self.spec = copy.deepcopy(spec)
        self.base = origin(base_origin)
        self.allowed = {origin(o) for o in allowed_origins}
        if self.base not in self.allowed:
            raise SpecError("base origin not allowlisted")
        self.check()

    def check(self):
        spec = self.spec
        if not isinstance(spec.get("flow"), str) or not isinstance(spec.get("spec_version"), str):
            raise SpecError("flow and spec_version required")
        if not isinstance(spec.get("provenance"), str) or not spec["provenance"]:
            raise SpecError("flow provenance required (OBSERVED or SYNTHETIC with source)")
        known = set(spec.get("variables", {})) | {"nonce"}
        names = set()
        steps = spec.get("steps")
        if not isinstance(steps, list) or not steps:
            raise SpecError("steps required")
        owned, owners = set(), {}
        for step in steps:
            if not isinstance(step, dict) or set(step) - STEP_KEYS:
                raise SpecError("unknown step keys")
            if step.get("name") in names or not isinstance(step.get("name"), str):
                raise SpecError("step names must be unique strings")
            names.add(step["name"])
            if step.get("method") not in {"GET", "POST", "DELETE"} or not str(step.get("path", "")).startswith("/"):
                raise SpecError(f"{step['name']}: method GET/POST/DELETE and absolute path required")
            if not step.get("status") or not all(isinstance(c, int) for c in step["status"]):
                raise SpecError(f"{step['name']}: expected status list required")
            if not any(step.get(k) for k in ("contains", "contains_ci", "count", "capture", "json_equals", "redirect_to")):
                # HTTP 200 alone is never a business result.
                raise SpecError(f"{step['name']}: needs a content/business assertion, status alone is not enough")
            for name in self.templates(step):
                if name not in known:
                    raise SpecError(f"{step['name']}: unknown template variable {name}")
            for name in list(step.get("capture", {})) + list(step.get("capture_json", {})):
                known.add(name)
            if step.get("owns"):
                proof = step.get("ownership")
                # Ownership is proven by this sample's own fresh session, or by the response echoing this
                # sample's nonce. A 201 or a server-returned identifier alone never proves it.
                by_session = proof == {"session": True} and bool(spec.get("session_cookie"))
                by_echo = isinstance(proof, dict) and set(proof) == {"json_equals"} and isinstance(proof["json_equals"], dict) \
                    and "nonce" in self.templates(proof["json_equals"]) and "capture_json" in step
                if not (by_session or by_echo):
                    raise SpecError(f"{step['name']}: owns needs an ownership proof (fresh session or nonce echo)")
                owned.add(step["owns"])
                owners[step["owns"]] = step
            elif "ownership" in step:
                raise SpecError(f"{step['name']}: ownership without owns")
        cleanup = spec.get("cleanup", {})
        for resource, step in cleanup.items():
            if resource not in owned or step.get("method") not in {"GET", "POST", "DELETE"}:
                raise SpecError(f"cleanup {resource}: only resources a step owns, with a known method")
            owner = owners[resource]
            if "json_equals" in owner["ownership"]:
                # A record proven by nonce echo is cleaned by the identifiers that proof came with, nothing later.
                allowed = set(spec.get("variables", {})) | {"nonce"} | set(owner.get("capture_json", {}))
                if self.templates(step.get("path", "")) - allowed:
                    raise SpecError(f"cleanup {resource}: its target must come from the step that proves ownership")
        self.per_sample_requests = sum(4 if s.get("follow_redirects") else 1 for s in steps) + len(cleanup)

    @staticmethod
    def templates(value):
        if isinstance(value, str):
            return set(TEMPLATE.findall(value))
        if isinstance(value, dict):  # keys too: a count marker is a template key
            return set().union(*(Flow.templates(k) | Flow.templates(v) for k, v in value.items())) if value else set()
        if isinstance(value, list):
            return set().union(*(Flow.templates(v) for v in value)) if value else set()
        return set()

    @staticmethod
    def fill(value, env):
        if isinstance(value, str):
            whole = TEMPLATE.fullmatch(value)
            if whole:
                return env[whole.group(1)]
            return TEMPLATE.sub(lambda m: str(env[m.group(1)]), value)
        if isinstance(value, dict):
            return {k: Flow.fill(v, env) for k, v in value.items()}
        if isinstance(value, list):
            return [Flow.fill(v, env) for v in value]
        return value

    def url(self, path, env):
        """Base origin + path; substituted values are percent-encoded, so a captured value stays one segment."""
        url = self.base + TEMPLATE.sub(lambda m: quote(str(env[m.group(1)]), safe=""), path)
        if origin(url) not in self.allowed:
            raise Failure("HTTP", "ORIGIN_NOT_ALLOWED")
        return url

    def run(self, deadline_ns, cancel, memory, http=request, step_s=None, stop_ns=None, cleanup_ns=None, grace_s=None,
            stop_deadline=None):
        """One transaction. Deadlines are perf_counter_ns values: `deadline_ns` (transaction), each step
        at most `step_s`, and `stop_ns` (the run's workload cap) cut the transaction; the cleanup that
        always follows is bounded by `cleanup_ns` (the cap plus the declared grace) instead.

        A stop, the run cap or an interrupt (KeyboardInterrupt/SIGINT) gives detail CANCELLED: the
        outcome is unknown, never a pass and never a failure of the service. The moment it stopped is
        returned as `stopped_ns`; with `grace_s` the cleanup also ends within grace_s of that moment,
        so an early stop does not inherit the grace of a cap that lies in the future.
        """
        env = dict(self.spec.get("variables", {}), nonce=uuid.uuid4().hex)
        state = {"cookies": {}, "session": None, "owned": set(), "claimed": set(), "credentials": {}, "targets": {},
                 "requests": 0, "steps": [], "captures": {}}
        result = {"ok": False, "detail": None, "reason": None, "interrupted": False, "stopped_ns": None}
        bounds = {"transaction": deadline_ns, "run": NEVER if stop_ns is None else stop_ns, "step_s": step_s}
        start = time.perf_counter_ns()
        try:
            for step in self.spec["steps"]:
                self.step(step, env, state, bounds, cancel, memory, http)
            result["ok"] = True
        except Failure as failure:
            result["detail"], result["reason"] = failure.detail, failure.reason
        except Cancelled as stopped:
            result["detail"], result["reason"] = "CANCELLED", stopped.reason
            now = time.perf_counter_ns()
            result["stopped_ns"] = min(now, bounds["run"]) if stopped.reason == "RUN_BUDGET" else now
        except KeyboardInterrupt:
            # Brought back to the cancel path: the cleanup below still runs and the sample is not emitted.
            result["detail"], result["reason"], result["interrupted"] = "CANCELLED", "INTERRUPTED", True
            result["stopped_ns"] = time.perf_counter_ns()
        finally:
            result["elapsed_ms"] = (time.perf_counter_ns() - start) / 1e6
            limit = cleanup_ns
            if result["stopped_ns"] is not None and grace_s is not None:
                own = result["stopped_ns"] + int(grace_s * 1e9)
                limit = own if limit is None else min(limit, own)
            limit = stop_deadline if limit is None else bounded_deadline(limit, stop_deadline)
            result["cleanup"] = self.cleanup(env, state, http, limit)
        result.update(steps=state["steps"], requests=state["requests"], captures=state["captures"])
        return result

    def send(self, http, url, method, headers, body, deadline_ns, cancel, state, cookies=None):
        """One request. The cookie jar is sent and updated, unless `cookies` (a credential frozen when a
        resource was claimed) is given: then exactly those cookies are sent and the jar is left alone."""
        jar = state["cookies"] if cookies is None else cookies
        cookie = "; ".join(f"{k}={v}" for k, v in jar.items())
        headers = list(headers) + ([("Cookie", cookie)] if cookie else [])
        state["requests"] += 1
        response = http(url, method, headers, body, deadline_ns, cancel)
        if cookies is not None:
            return response
        for value in response.header("set-cookie"):
            try:
                jar = SimpleCookie()
                jar.load(value)
            except CookieError:
                raise Failure("HTTP", "MALFORMED_COOKIE") from None
            for name, morsel in jar.items():
                state["cookies"][name] = morsel.value
        return response

    @staticmethod
    def deadline(bounds, began):
        """(deadline, name) for one step: the earliest of the transaction, the step and the run cap."""
        candidates = [(bounds["transaction"], "TRANSACTION_DEADLINE"), (bounds["run"], "RUN_BUDGET")]
        if bounds.get("step_s"):
            candidates.append((began + int(bounds["step_s"] * 1e9), "STEP_DEADLINE"))
        return min(candidates, key=lambda c: c[0])

    def step(self, step, env, state, bounds, cancel, memory, http):
        began = time.perf_counter_ns()
        record = {"name": step["name"], "status": None, "ok": False}
        state["steps"].append(record)
        deadline_ns, which = self.deadline(bounds, began)
        try:
            self.exchange(step, env, state, deadline_ns, cancel, memory, http)
            record["ok"] = True
        except Failure as failure:
            if failure.detail == "TIMEOUT" and time.perf_counter_ns() >= deadline_ns:
                if which == "RUN_BUDGET":
                    raise Cancelled("RUN_BUDGET") from None  # the probe's own cap, not the service
                raise Failure("TIMEOUT", which) from None
            raise
        finally:
            record["ms"] = round((time.perf_counter_ns() - began) / 1e6, 3)

    def exchange(self, step, env, state, deadline_ns, cancel, memory, http):
        record = state["steps"][-1]
        body, headers = b"", []
        if "form" in step:
            body = urlencode(self.fill(step["form"], env)).encode()
            headers.append(("Content-Type", "application/x-www-form-urlencoded"))
        elif "json" in step:
            body = json.dumps(self.fill(step["json"], env), separators=(",", ":")).encode()
            headers.append(("Content-Type", "application/json"))
        session_before = state["cookies"].get(self.spec.get("session_cookie"))
        url = self.url(step["path"], env)
        method = step["method"]
        if step.get("owns"):
            # From here a resource may exist. In this sample's fresh session it is ours; otherwise ownership
            # waits for the nonce echo and, if never proven, the cleanup reports it as unresolved. The
            # credential is frozen now, before the request: a later Set-Cookie (in this answer, a redirect
            # or another step) can never redirect the cleanup to someone else's session (FX01-R1).
            state["claimed"].add(step["owns"])
            state["credentials"][step["owns"]] = dict(state["cookies"])
            name = self.spec.get("session_cookie")
            if step["ownership"] == {"session": True} and state["session"] is not None and \
                    state["cookies"].get(name) == state["session"]:
                state["owned"].add(step["owns"])
        response = self.send(http, url, method, headers, body, deadline_ns, cancel, state)
        self.session(step, state, session_before, memory)
        hops = 0
        while step.get("follow_redirects") and response.status in (301, 302, 303, 307, 308) and hops < 3:
            location = response.header("location")
            if not location:
                raise Failure("HTTP", "REDIRECT_WITHOUT_LOCATION")
            url = urljoin(url, location[0])
            if CONTROL.search(url):
                raise Failure("HTTP", "MALFORMED_REDIRECT")
            if origin(url) not in self.allowed:
                raise Failure("HTTP", "REDIRECT_OUTSIDE_ALLOWLIST")
            if response.status in (301, 302, 303):
                method, body, headers = "GET", b"", []
            response = self.send(http, url, method, headers, body, deadline_ns, cancel, state)
            self.session(step, state, session_before, memory)
            hops += 1
        record["status"] = response.status
        if response.status not in step["status"]:
            raise Failure("HTTP", f"STATUS_{response.status}")
        self.assertions(step, response, env, state, memory)
        if step.get("releases"):
            state["owned"].discard(step["releases"])
            state["claimed"].discard(step["releases"])

    def session(self, step, state, before, memory):
        name = self.spec.get("session_cookie")
        if not name:
            return
        value = state["cookies"].get(name)
        if step.get("session") == "issue" and state["session"] is None:
            # A new session must come from the server for this sample, and must never repeat.
            if value is None:
                raise Failure("BUSINESS", "SESSION_NOT_ISSUED")
            if not memory.fresh("session", value):
                raise Failure("BUSINESS", "STALE_SESSION")
            state["session"] = value
        elif state["session"] is not None and value != state["session"]:
            raise Failure("BUSINESS", "SESSION_CHANGED")
        elif before is not None and value != before:
            raise Failure("BUSINESS", "SESSION_CHANGED")

    def assertions(self, step, response, env, state, memory):
        if "redirect_to" in step and response.status in (301, 302, 303, 307, 308):
            target = urlsplit(urljoin(self.base, (response.header("location") or [""])[0]))
            if target.path != self.fill(step["redirect_to"], env) or origin(f"{target.scheme}://{target.netloc}") not in self.allowed:
                raise Failure("BUSINESS", "UNEXPECTED_REDIRECT")
        needs_text = any(k in step for k in ("contains", "contains_ci", "absent", "count", "capture"))
        text = None
        if needs_text:
            try:
                text = response.body.decode("utf-8")
            except UnicodeDecodeError:
                raise Failure("PARSE", "BODY_NOT_UTF8") from None
        for needle in step.get("contains", []):
            if self.fill(needle, env) not in text:
                raise Failure("BUSINESS", "CONTENT_MISSING")
        for needle in step.get("contains_ci", []):
            if self.fill(needle, env).lower() not in text.lower():
                raise Failure("BUSINESS", "CONTENT_MISSING")
        for needle in step.get("absent", []):
            if self.fill(needle, env) in text:
                raise Failure("BUSINESS", "FORBIDDEN_CONTENT")
        for needle, times in step.get("count", {}).items():
            if text.count(self.fill(needle, env)) != times:
                raise Failure("BUSINESS", "STALE_OR_WRONG_QUANTITY")
        for name, rule in step.get("capture", {}).items():
            match = re.search(rule["regex"], text, re.IGNORECASE | re.DOTALL)
            if not match:
                raise Failure("BUSINESS", "CAPTURE_MISSING")
            self.capture(name, match.group(1), rule, env, state, memory)
            if "equals" in rule and match.group(1) != self.fill(rule["equals"], env):
                raise Failure("BUSINESS", "WRONG_QUANTITY_OR_VALUE")
        if any(k in step for k in ("json_schema", "json_equals", "capture_json")):
            try:
                document = json.loads(response.body.decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                raise Failure("PARSE", "BODY_NOT_JSON") from None
            if not isinstance(document, dict):
                raise Failure("SCHEMA", "NOT_AN_OBJECT")
            for key, kind in step.get("json_schema", {}).items():
                if key not in document or type(document[key]) is not TYPES[kind]:
                    raise Failure("SCHEMA", "FIELD_MISSING_OR_WRONG_TYPE")
            for name, key in step.get("capture_json", {}).items():
                if not isinstance(document.get(key), str) or not document[key]:
                    raise Failure("SCHEMA", "CAPTURE_MISSING")
                self.capture(name, document[key], step.get("fresh", {}).get(name, {}), env, state, memory)
            proof = (step.get("ownership") or {}).get("json_equals")
            if step.get("owns") and proof and all(document.get(k) == self.fill(v, env) for k, v in proof.items()):
                # The record echoes this sample's nonce, so this request created it: it may be deleted even when
                # another field is wrong. A stale or foreign record cannot echo the nonce. The identifiers it
                # was proven with are frozen too: a later capture cannot retarget the cleanup.
                state["owned"].add(step["owns"])
                state["targets"][step["owns"]] = dict(env)
            for key, expected in step.get("json_equals", {}).items():
                if document.get(key) != self.fill(expected, env):
                    raise Failure("BUSINESS", "WRONG_RESULT")

    @staticmethod
    def capture(name, value, rule, env, state, memory):
        env[name] = value
        state["captures"][name + "_sha256_16"] = digest(value)
        if rule.get("fresh") and not memory.fresh(name, value):
            raise Failure("BUSINESS", "STALE_RESPONSE")

    def cleanup(self, env, state, http, cleanup_ns=None):
        """Remove only resources this sample proved it owns, with the credential it created them with;
        never cancellable.

        Each request is bounded by the cleanup step's timeout_s and by `cleanup_ns` (the plan's grace).
        A resource whose creating request was sent but whose ownership was never proven is reported as
        UNRESOLVED_OWNERSHIP and left alone: deleting it could remove data the probe did not create. The
        request carries the cookies frozen when the resource was claimed, never the current jar.
        """
        done = {}
        for resource, step in self.spec.get("cleanup", {}).items():
            if resource not in state["owned"]:
                if resource in state["claimed"]:
                    done[resource] = "UNRESOLVED_OWNERSHIP"
                continue
            own_deadline = time.perf_counter_ns() + int(step.get("timeout_s", 5) * 1e9)
            deadline = bounded_deadline(own_deadline, cleanup_ns)
            if deadline_value(deadline) <= time.perf_counter_ns():
                done[resource] = "SKIPPED_NO_GRACE"
                continue
            try:
                url = self.url(step["path"], state["targets"].get(resource, env))
            except KeyError:
                done[resource] = "SKIPPED_NOT_CREATED"
                continue
            except Failure as failure:
                done[resource] = failure.reason
                continue
            try:
                response = self.send(http, url, step["method"], [], b"", deadline, None, state,
                                     cookies=state["credentials"][resource])
                done[resource] = "DONE" if response.status in step.get("status", [200, 204]) else f"STATUS_{response.status}"
            except Failure as failure:
                if failure.detail == "TIMEOUT":
                    # The resource may still exist: say which bound ended the attempt.
                    done[resource] = "GRACE_EXPIRED" if cleanup_ns is not None and deadline_value(cleanup_ns) <= own_deadline else "CLEANUP_TIMEOUT"
                else:
                    done[resource] = failure.reason
        return done


# Cart page markers in the shape of the upstream Online Boutique cart template (one line per product,
# "SKU #<id>" and "Quantity: <n>"). OBSERVED-SHAPE only: they must be confirmed on a pilot page before
# acceptance, and a plan can replace them (flow_spec.args.cart_markers) without a code change.
CART_MARKERS = {"line": "SKU #", "item": "SKU #{product_id}", "quantity_regex": r"Quantity:\s*(\d+)"}


def boutique_spec(product_id, product_marker=None, checkout_form=None, cart_markers=None):
    """Online Boutique purchase (home -> product -> cart -> checkout) on a new session.

    Markers come from the lab check (verify-local-lab.sh purchase). `product_marker` is the product
    name to expect on its page; it must be read from an observed page before acceptance. The cart step
    proves the sample's own cart: exactly one line, for the requested product, with quantity 1.
    """
    product = ["{product_id}"] + (["{product_marker}"] if product_marker else [])
    cart = dict(CART_MARKERS, **(cart_markers or {}))
    if set(cart) != set(CART_MARKERS) or not all(isinstance(v, str) and v for v in cart.values()) or cart["line"] == cart["item"]:
        raise SpecError("cart_markers need line, item (different from line) and quantity_regex")
    return {
        "flow": "checkout", "spec_version": "boutique-checkout/1",
        "provenance": "OBSERVED-SHAPE from verify-local-lab.sh purchase; markers need a pilot observation",
        "session_cookie": "shop_session-id",
        "variables": {"product_id": product_id, "product_marker": product_marker or "", "checkout_form": checkout_form or {}},
        "steps": [
            {"name": "home", "method": "GET", "path": "/", "status": [200], "session": "issue",
             "contains": ["/product/{product_id}"]},
            {"name": "product", "method": "GET", "path": "/product/{product_id}", "status": [200], "contains": product},
            {"name": "add_to_cart", "method": "POST", "path": "/cart", "status": [302, 303, 200],
             "form": {"product_id": "{product_id}", "quantity": "1"}, "redirect_to": "/cart", "owns": "cart",
             "ownership": {"session": True}},
            {"name": "cart", "method": "GET", "path": "/cart", "status": [200], "count": {cart["line"]: 1, cart["item"]: 1},
             "capture": {"cart_quantity": {"regex": cart["quantity_regex"], "equals": "1"}}},
            {"name": "checkout", "method": "POST", "path": "/cart/checkout", "status": [200], "follow_redirects": True,
             "form": "{checkout_form}", "contains_ci": ["order is complete"], "releases": "cart",
             "capture": {"order_id": {"regex": r"Confirmation.{0,400}?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
                                      "fresh": True}}},
        ],
        "cleanup": {"cart": {"method": "POST", "path": "/cart/empty", "status": [200, 302, 303]}},
    }


def fixture_spec(item="benign-catalog-item"):
    """SYNTHETIC interface for the ZER-41 fixture: one benign order round-trip through its database.

    Not an implemented fixture and not a SQLi path: the values are a fixed benign item and a random
    hex nonce. ZER-41 must provide these endpoints (or this spec is changed with its real ones).
    """
    schema = {"order_ref": "str", "item": "str", "note": "str", "status": "str"}
    return {
        "flow": "fixture", "spec_version": "fixture-order/0-synthetic",
        "provenance": "SYNTHETIC interface proposal for ZER-41; no fixture exists in the lab",
        "variables": {"item": item},
        "steps": [
            {"name": "create", "method": "POST", "path": "/fixture/orders", "status": [201],
             "json": {"item": "{item}", "note": "{nonce}"}, "json_schema": schema,
             "json_equals": {"item": "{item}", "note": "{nonce}", "status": "STORED"},
             "capture_json": {"order_ref": "order_ref"}, "fresh": {"order_ref": {"fresh": True}}, "owns": "order",
             "ownership": {"json_equals": {"note": "{nonce}", "item": "{item}"}}},
            {"name": "read", "method": "GET", "path": "/fixture/orders/{order_ref}", "status": [200],
             "json_schema": schema, "json_equals": {"order_ref": "{order_ref}", "item": "{item}", "note": "{nonce}", "status": "STORED"}},
        ],
        "cleanup": {"order": {"method": "DELETE", "path": "/fixture/orders/{order_ref}", "status": [200, 204, 404]}},
    }
