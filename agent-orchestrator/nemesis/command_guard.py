"""Admission controls shared by the agents. No clients, threads or effects at import.

The command MAC signs exact payload bytes, not cross-language JSON reserialization.
The operator token and the fault signing key must be separate from O event credentials.
"""
from contextlib import contextmanager
import base64
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
from urllib.parse import urlsplit
import uuid


class Refused(ValueError):
    def __init__(self, reason, status=400):
        super().__init__(reason)
        self.reason, self.status = reason, status


def strict_json(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 32768:
        raise Refused("PAYLOAD_SIZE")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Refused("DUPLICATE_KEY")
            result[key] = value
        return result
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refused("NONFINITE")))
        def depth(v, level=0):
            if type(v) is float and not math.isfinite(v):
                raise Refused("NONFINITE")
            if level > 16:
                raise Refused("PAYLOAD_DEPTH")
            for child in (v.values() if isinstance(v, dict) else v if isinstance(v, list) else ()):
                depth(child, level + 1)
        depth(value)
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Refused("INVALID_JSON") from error


def fields(obj, required, optional=()):
    if type(obj) is not dict or not set(required) <= set(obj) or set(obj) - set(required) - set(optional):
        raise Refused("SCHEMA_FIELDS")


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise Refused("INTEGER_RANGE")
    return value


def identifier(value):
    try:
        if str(uuid.UUID(value, version=4)) != value or uuid.UUID(value).version != 4:
            raise ValueError()
    except (ValueError, AttributeError, TypeError):
        raise Refused("COMMAND_ID")
    return value


def context_valid(context):
    fields(context, {"run_id", "trial_id", "group"})
    if not re.fullmatch(r"run_[0-9a-f]{32}", str(context["run_id"])) or not re.fullmatch(r"trl_[0-9a-f]{32}", str(context["trial_id"])) or type(context["group"]) is not str or context["group"] not in {"B0", "BM", "B1", "B2", "B3"}:
        raise Refused("RUN_CONTEXT")
    return context


SERVICES = {"frontend", "cartservice", "productcatalogservice", "currencyservice", "checkoutservice", "redis-cart", "shippingservice", "paymentservice", "emailservice"}


def url_valid(raw):
    try:
        u = urlsplit(raw)
        if (not isinstance(raw, str) or any(c in raw for c in "\\%\r\n\t ?#") or u.scheme != "http" or
                u.username is not None or u.password is not None or u.hostname != "frontend.target-app.svc.cluster.local" or
                u.port not in (None, 80) or u.path not in ("", "/") or u.query or u.fragment):
            raise ValueError()
        # Reject noncanonical authorities (e.g. a trailing colon).
        if u.netloc not in {"frontend.target-app.svc.cluster.local", "frontend.target-app.svc.cluster.local:80"}:
            raise ValueError()
        return "http://frontend.target-app.svc.cluster.local/"
    except (ValueError, TypeError, AttributeError):
        raise Refused("TARGET_URL")


def read_key(path, purpose):
    try:
        value = strict_json(Path(path).read_bytes())
        fields(value, {"id", "secret", "purpose"})
        if value["purpose"] != purpose or type(value["secret"]) is not str or len(value["secret"].encode()) < 32 or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value["id"]):
            raise Refused("KEY_CONFIG", 503)
        return value
    except (OSError, KeyError, TypeError) as error:
        raise Refused("KEY_CONFIG", 503) from error


def sign(command, key, now=None):
    if key["purpose"] != "fault":
        raise Refused("SIGNER_ROLE", 403)
    now = int(time.time()) if now is None else now
    payload = base64.b64encode(json.dumps(command, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).decode()
    result = dict(version="zd-command/1", keyId=key["id"], purpose="fault", issuedAt=now, expiresAt=now + 60, payload=payload)
    signed = "\n".join(str(result[k]) for k in ("version", "keyId", "purpose", "issuedAt", "expiresAt", "payload"))
    result["signature"] = hmac.new(key["secret"].encode(), signed.encode(), hashlib.sha256).hexdigest()
    return result


class Ledger:
    """A claim survives errors/restart. Unknown outcomes never automatically reexecute."""
    def __init__(self, path):
        self.path = Path(path)
        if self.path.is_symlink() or self.path.parent.is_symlink() or not self.path.parent.is_dir():
            raise Refused("LEDGER_PATH", 503)
        try:
            with self.connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT, created REAL NOT NULL)")
        except sqlite3.Error as error:
            raise Refused("LEDGER_UNAVAILABLE", 503) from error

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=2)
        try:
            db.execute("PRAGMA synchronous=FULL")
            with db:
                yield db
        finally:
            db.close()

    def claim(self, request_id, value, clock=time.time):
        identifier(request_id)
        digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                old = db.execute("SELECT digest,result FROM claims WHERE id=?", (request_id,)).fetchone()
                if old:
                    if old[0] != digest:
                        raise Refused("ID_CONFLICT", 409)
                    if old[1] is None:
                        raise Refused("OUTCOME_UNKNOWN", 409)
                    return json.loads(old[1])
                count, active = db.execute("SELECT count(*),sum(result IS NULL) FROM claims").fetchone()
                if count >= 10000:
                    raise Refused("LEDGER_FULL", 503)
                if active:
                    raise Refused("ACTIVE_OR_UNKNOWN_REQUEST", 409)
                # Atomic per-service admission pacing; errors don't refund the reservation.
                last = db.execute("SELECT max(created) FROM claims").fetchone()[0]
                current = clock()
                if last is not None and current - last < 6:
                    raise Refused("ADMISSION_RATE", 429)
                db.execute("INSERT INTO claims VALUES (?,?,NULL,?)", (request_id, digest, current))
                return None
        except sqlite3.Error as error:
            raise Refused("LEDGER_UNAVAILABLE", 503) from error

    def complete(self, request_id, result):
        try:
            with self.connect() as db:
                changed = db.execute("UPDATE claims SET result=? WHERE id=? AND result IS NULL",
                                     (json.dumps(result, allow_nan=False), request_id)).rowcount
                if changed != 1:
                    raise Refused("LEDGER_COMPLETION", 503)
        except sqlite3.Error as error:
            raise Refused("LEDGER_UNAVAILABLE", 503) from error


class CommandGuard:
    def __init__(self, policy):
        fields(policy, {"version", "enabled", "context", "targets", "maxDurationSec", "maxConcurrency", "rps"})
        if policy["version"] != "zd-guard/1" or type(policy["enabled"]) is not bool:
            raise Refused("POLICY_CONFIG", 503)
        context_valid(policy["context"])
        integer(policy["maxDurationSec"], 1, 600)
        integer(policy["maxConcurrency"], 1, 50)
        integer(policy["rps"], 1, 100)
        if type(policy["targets"]) is not list or not policy["targets"]:
            raise Refused("POLICY_TARGETS", 503)
        seen = set()
        for target in policy["targets"]:
            fields(target, {"namespace", "service", "url"})
            if type(target["url"]) is not str or target["namespace"] != "target-app" or type(target["service"]) is not str or target["service"] not in SERVICES or target["service"] in seen:
                raise Refused("POLICY_TARGETS", 503)
            seen.add(target["service"])
            if target["url"] and (target["service"] != "frontend" or url_valid(target["url"]) != target["url"]):
                raise Refused("POLICY_TARGETS", 503)
        self.policy = policy

    @classmethod
    def from_env(cls):
        try:
            policy = strict_json(Path(os.environ["ZD_COMMAND_POLICY_FILE"]).read_bytes())
            for env, field, high in (("MAX_ATTACK_DURATION_SEC", "maxDurationSec", 600), ("DEFAULT_CONCURRENCY", "maxConcurrency", 50), ("DEFAULT_RPS", "rps", 100)):
                if env in os.environ:
                    try:
                        raw = os.environ[env]
                        if not re.fullmatch(r"[1-9][0-9]*", raw):
                            raise ValueError()
                        cap = integer(int(raw), 1, high)
                    except (ValueError, TypeError):
                        raise Refused("POLICY_LIMIT_CONFIG", 503)
                    policy[field] = min(integer(policy[field], 1, high), cap)
            return cls(policy)
        except (OSError, KeyError) as error:
            raise Refused("POLICY_UNAVAILABLE", 503) from error

    def authorize(self, authorization, purpose="operator"):
        if purpose not in {"operator", "heal-operator"}:
            raise Refused("OPERATOR_ROLE", 403)
        key = read_key(os.environ.get("ZD_OPERATOR_TOKEN_FILE", ""), purpose)
        if not isinstance(authorization, str) or not hmac.compare_digest(authorization.encode(), ("Bearer " + key["secret"]).encode()):
            raise Refused("UNAUTHORIZED", 401)
        return key["id"]

    def enabled(self):
        if not self.policy["enabled"]:
            raise Refused("EXECUTOR_DISABLED", 409)

    def allow_model(self):
        # All supported contexts are benchmark groups. Scenario generation stays
        # outside the benchmark, independent of the treatment group.
        raise Refused("BENCHMARK_SCENARIO_LLM_DISABLED", 409)

    def command(self, body, request_id):
        fields(body, {"attackType", "targetService"}, {"targetNamespace", "targetURL", "durationSec", "intensity", "concurrency"})
        if type(body["attackType"]) is not str or body["attackType"] not in {"HTTP_FLOOD", "CPU_STRESS", "MEMORY_STRESS", "POD_KILL"}:
            raise Refused("COMMAND_TYPE")
        namespace, service = body.get("targetNamespace", "target-app"), body["targetService"]
        if type(service) is not str or type(namespace) is not str:
            raise Refused("TARGET_SERVICE")
        matches = [t for t in self.policy["targets"] if t["namespace"] == namespace and t["service"] == service]
        if len(matches) != 1:
            raise Refused("TARGET_SERVICE")
        raw = body.get("targetURL", "")
        if type(raw) is not str:
            raise Refused("TARGET_URL")
        if body["attackType"] == "HTTP_FLOOD":
            raw = url_valid(raw or f"http://{service}.{namespace}.svc.cluster.local/")
            if matches[0]["url"] != raw:
                raise Refused("TARGET_ROUTE")
        elif raw:
            raise Refused("UNEXPECTED_URL")
        duration = integer(body.get("durationSec", 30), 1, 86400)
        concurrency = integer(body.get("concurrency", 1), 1, 10000)
        intensity = body.get("intensity", "LOW")
        if type(intensity) is not str or intensity not in {"LOW", "MEDIUM", "HIGH"}:
            raise Refused("INTENSITY")
        return {"commandId": identifier(request_id), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source": "nemesis",
                "context": dict(self.policy["context"]), "attackType": body["attackType"],
                "target": {"namespace": namespace, "service": service, "url": raw},
                "parameters": {"duration": min(duration, self.policy["maxDurationSec"]), "intensity": intensity,
                               "concurrency": min(concurrency, self.policy["maxConcurrency"]), "customParams": {}},
                "safetyLimits": {"maxDuration": self.policy["maxDurationSec"], "allowedNamespaces": ["target-app"]}}

    def signer(self):
        key = read_key(os.environ.get("ZD_COMMAND_SIGNER_FILE", ""), "fault")
        operator = read_key(os.environ.get("ZD_OPERATOR_TOKEN_FILE", ""), "operator")
        if hmac.compare_digest(key["secret"], operator["secret"]):
            raise Refused("KEY_SEPARATION", 503)
        return key

    def ledger(self):
        try:
            return Ledger(os.environ["ZD_COMMAND_LEDGER_FILE"])
        except KeyError as error:
            raise Refused("LEDGER_REQUIRED", 503) from error
