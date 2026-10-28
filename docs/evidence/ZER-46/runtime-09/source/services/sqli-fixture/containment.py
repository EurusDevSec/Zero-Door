"""Opt-in SQLi containment at the trusted-client boundary, not at the proxy's TCP IP.

Read a projected ConfigMap file on every request (no subPath, cache or Timer). Kubernetes owns durability;
an absolute expiry makes unblock independent of the healer being alive. No mutation or management HTTP
endpoint exists here. Invalid/missing state is unavailable, never an implicit empty policy.
"""
import hashlib
import ipaddress
import json
import re
import time
from pathlib import Path

VERSION = "zer46-containment/1"
MAX_BYTES = 32768
MAX_RULES = 32
MAX_TTL = 300
SCOPE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class PolicyError(ValueError):
    pass


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError("DUPLICATE_KEY")
        result[key] = value
    return result


def private_ip(value):
    if not isinstance(value, str) or "%" in value:
        raise PolicyError("SOURCE_IP")
    try:
        ip = ipaddress.ip_address(value)
    except ValueError as error:
        raise PolicyError("SOURCE_IP") from error
    if (ip.version != 4 or not ip.is_private or ip.is_loopback or ip.is_link_local or
            ip.is_multicast or ip.is_unspecified or ip.is_reserved or str(ip) != value):
        raise PolicyError("SOURCE_IP")
    return value


def decode(raw, scope, now=None):
    now = time.time() if now is None else now
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise PolicyError("POLICY_SIZE")
    try:
        p = json.loads(raw, object_pairs_hook=unique)
        if (type(p) is not dict or set(p) != {"version", "scope", "run_id", "trial_id", "rules"} or
                p["version"] != VERSION or p["scope"] != scope or not SCOPE.fullmatch(scope) or
                not isinstance(p["run_id"], str) or not re.fullmatch(r"run_[0-9a-f]{32}", p["run_id"]) or
                not isinstance(p["trial_id"], str) or not re.fullmatch(r"trl_[0-9a-f]{32}", p["trial_id"]) or
                type(p["rules"]) is not list or len(p["rules"]) > MAX_RULES):
            raise PolicyError("POLICY_SCHEMA")
        seen = set()
        for rule in p["rules"]:
            if (type(rule) is not dict or set(rule) != {"action_id", "client_ip", "created_at", "expires_at", "request_id"} or
                    not isinstance(rule["action_id"], str) or not re.fullmatch(r"act_[0-9a-f]{32}", rule["action_id"]) or
                    rule["action_id"] in seen or not isinstance(rule["request_id"], str) or
                    not re.fullmatch(r"[0-9a-f]{32}", rule["request_id"]) or
                    type(rule["created_at"]) is not int or type(rule["expires_at"]) is not int or
                    not 0 < rule["expires_at"] - rule["created_at"] <= MAX_TTL or
                    rule["created_at"] > now + 5):
                raise PolicyError("RULE_SCHEMA")
            private_ip(rule["client_ip"])
            seen.add(rule["action_id"])
        return p
    except (ValueError, TypeError, KeyError, UnicodeError) as error:
        raise PolicyError("POLICY_INVALID") from error


class FilePolicy:
    def __init__(self, path, scope):
        if not SCOPE.fullmatch(scope):
            raise PolicyError("POLICY_SCOPE")
        self.path, self.scope = Path(path), scope

    def snapshot(self, now=None):
        now = time.time() if now is None else now
        try:
            # A single open follows the projected-volume symlink to one atomic revision.
            with self.path.open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
            policy = decode(raw, self.scope, now)
        except (OSError, PolicyError) as error:
            raise PolicyError("CONTAINMENT_STATE_UNAVAILABLE") from error
        return policy, hashlib.sha256(raw).hexdigest()

    def check(self, source, now=None):
        now = time.time() if now is None else now
        policy, digest = self.snapshot(now)
        if (source.get("confidence"), source.get("method")) not in {
                ("OBSERVED_PEER", "DIRECT_PEER"), ("PROXY_CHAIN", "XFF_AFTER_TRUSTED")}:
            raise PolicyError("CONTAINMENT_SOURCE_UNKNOWN")
        ip = private_ip(source.get("client_ip"))
        matches = [r for r in policy["rules"] if r["client_ip"] == ip and now < r["expires_at"]]
        return {"enforcement_point": "sqli-fixture/trusted-client", "policy_sha256": digest,
                "blocked": bool(matches), "action_ids": [r["action_id"] for r in matches]}
