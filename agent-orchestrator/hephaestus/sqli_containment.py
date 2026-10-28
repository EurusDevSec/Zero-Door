"""Prepared SQLi containment backend; not wired into production R1 execution.

Caller must first admit an authenticated decision through ModeGate and bind the evidence to the trusted
observation. This module does not turn an HTTP body or a model-proposed IP into trusted evidence. A bounded
component harness may supply its independently joined access record and approved target pins.

Only replace a precreated, UID/scope-pinned ConfigMap in zd-sqli-lab. No create/delete, cluster discovery,
background thread, networking initialization, or configuration/credential loading happens on import.
"""
import copy
import ipaddress
import json
import re
import time

NAMESPACE = "zd-sqli-lab"
NAME = "zer46-sqli-containment"
OWNER = "zero-door.io/containment-scope"
VERSION = "zer46-containment/1"
MAX_BYTES, MAX_RULES, MAX_TTL = 32768, 32, 300


class Refused(ValueError):
    pass


def ip(value):
    try:
        address = ipaddress.ip_address(value)
    except (ValueError, TypeError) as error:
        raise Refused("SOURCE_IP") from error
    if (not isinstance(value, str) or "%" in value or address.version != 4 or not address.is_private or
            address.is_loopback or address.is_link_local or address.is_multicast or address.is_unspecified or
            address.is_reserved or str(address) != value):
        raise Refused("SOURCE_IP")
    return value


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused("STATE_INVALID")
        result[key] = value
    return result


class SqliContainment:
    def __init__(self, api, *, uid, scope, run_id, trial_id, attacker_ip, benign_ip, proxy_cidrs, clock=time.time):
        self.api, self.uid, self.scope = api, uid, scope
        self.run_id, self.trial_id, self.clock = run_id, trial_id, clock
        if (not isinstance(uid, str) or not re.fullmatch(r"[0-9a-f-]{36}", uid) or
                not isinstance(scope, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", scope) or
                not isinstance(run_id, str) or not re.fullmatch(r"run_[0-9a-f]{32}", run_id) or
                not isinstance(trial_id, str) or not re.fullmatch(r"trl_[0-9a-f]{32}", trial_id)):
            raise Refused("TARGET_PIN")
        self.attacker, self.benign = ip(attacker_ip), ip(benign_ip)
        try:
            self.proxies = [ipaddress.ip_network(cidr, strict=True) for cidr in proxy_cidrs]
        except (ValueError, TypeError) as error:
            raise Refused("PROXY_PIN") from error
        if (self.attacker == self.benign or not self.proxies or
                any(net.version != 4 or net.prefixlen != 32 for net in self.proxies) or
                any(ipaddress.ip_address(value) in net for value in (self.attacker, self.benign) for net in self.proxies)):
            raise Refused("SOURCE_SEPARATION")

    def _read(self):
        cm = self.api.read_namespaced_config_map(NAME, NAMESPACE, _request_timeout=(2, 3))
        # Dictionary serialization avoids mutating the API client's shared object on failed CAS.
        doc = copy.deepcopy(cm if isinstance(cm, dict) else self.api.api_client.sanitize_for_serialization(cm))
        m = doc.get("metadata", {})
        if (m.get("uid") != self.uid or m.get("name") != NAME or m.get("namespace") != NAMESPACE or
                m.get("labels", {}).get(OWNER) != self.scope or not m.get("resourceVersion") or
                doc.get("immutable") is True or set(doc.get("data", {})) != {"policy.json"}):
            raise Refused("STATE_OWNER")
        raw = doc["data"]["policy.json"]
        try:
            if not isinstance(raw, str) or len(raw.encode()) > MAX_BYTES:
                raise Refused("STATE_SIZE")
            p = json.loads(raw, object_pairs_hook=unique)
            if (type(p) is not dict or set(p) != {"version", "scope", "run_id", "trial_id", "rules"} or
                    p["version"] != VERSION or p["scope"] != self.scope or p["run_id"] != self.run_id or
                    p["trial_id"] != self.trial_id or type(p["rules"]) is not list or len(p["rules"]) > MAX_RULES):
                raise Refused("STATE_CONTEXT")
            seen = set()
            for r in p["rules"]:
                if (type(r) is not dict or set(r) != {"action_id", "client_ip", "created_at", "expires_at", "request_id"} or
                        r["client_ip"] != self.attacker or not isinstance(r["action_id"], str) or
                        not re.fullmatch(r"act_[0-9a-f]{32}", r["action_id"]) or r["action_id"] in seen or
                        not isinstance(r["request_id"], str) or not re.fullmatch(r"[0-9a-f]{32}", r["request_id"]) or
                        type(r["created_at"]) is not int or type(r["expires_at"]) is not int or
                        not 0 < r["expires_at"] - r["created_at"] <= MAX_TTL or r["created_at"] > self.clock() + 5):
                    raise Refused("STATE_RULE")
                seen.add(r["action_id"])
        except (ValueError, KeyError, TypeError) as error:
            raise Refused("STATE_INVALID") from error
        return doc, p

    def _replace(self, doc, policy):
        raw = json.dumps(policy, separators=(",", ":"), sort_keys=True)
        if len(raw.encode()) > MAX_BYTES:
            raise Refused("STATE_SIZE")
        doc["data"] = {"policy.json": raw}
        # resourceVersion from the read is retained. Conflict => bounded reread, never blind overwrite.
        return self.api.replace_namespaced_config_map(NAME, NAMESPACE, doc, _request_timeout=(2, 3))

    def block(self, *, action_id, evidence, ttl_sec):
        if (not isinstance(action_id, str) or not re.fullmatch(r"act_[0-9a-f]{32}", action_id) or
                type(ttl_sec) is not int or not 1 <= ttl_sec <= MAX_TTL):
            raise Refused("ACTION_BOUND")
        if (type(evidence) is not dict or evidence.get("client_ip") != self.attacker or
                evidence.get("run_id") != self.run_id or evidence.get("trial_id") != self.trial_id or
                evidence.get("source_confidence") != "PROXY_CHAIN" or evidence.get("source_method") != "XFF_AFTER_TRUSTED" or
                not isinstance(evidence.get("request_id"), str) or not re.fullmatch(r"[0-9a-f]{32}", evidence["request_id"]) or
                type(evidence.get("ts")) not in {int, float} or
                not 0 <= self.clock() - evidence["ts"] < float("inf")):
            raise Refused("SOURCE_EVIDENCE")
        peer = ip(evidence.get("tcp_peer"))
        if not any(ipaddress.ip_address(peer) in net for net in self.proxies):
            raise Refused("SOURCE_PROXY")
        # Fix expiry before any CAS retry; a retry cannot extend the action's authorization window.
        # Conservative absolute window anchored to the joined source observation. Even after expired
        # entries are cleaned, replaying that observation cannot renew a block on a later restart.
        created = int(evidence["ts"])
        rule = {"action_id": action_id, "client_ip": self.attacker, "created_at": created,
                "expires_at": created + ttl_sec, "request_id": evidence["request_id"]}
        for _attempt in range(3):
            doc, p = self._read()
            previous = next((r for r in p["rules"] if r["action_id"] == action_id), None)
            if previous:
                if (previous["request_id"] != rule["request_id"] or
                        previous["expires_at"] - previous["created_at"] != ttl_sec):
                    raise Refused("ACTION_CONFLICT")
                return {"status": "API_ACCEPTED", "replay": True, "rule": previous, "containment_verified": False}
            if self.clock() - evidence["ts"] > 60:
                raise Refused("SOURCE_EVIDENCE")
            if len(p["rules"]) >= MAX_RULES:
                raise Refused("RULE_BUDGET")
            if self.clock() >= rule["expires_at"]:
                raise Refused("ACTION_EXPIRED")
            p["rules"].append(rule)
            try:
                self._replace(doc, p)
                return {"status": "API_ACCEPTED", "replay": False, "rule": rule, "containment_verified": False}
            except Exception as error:
                if getattr(error, "status", None) != 409:
                    raise  # timeout/unknown: preserve the action ID, reconcile before retrying
        raise Refused("STATE_CONFLICT")

    def cleanup(self, *, expired_only=True):
        """Explicit owned runner cleanup; endpoint reset does not call this. Never deletes the ConfigMap."""
        if type(expired_only) is not bool:
            raise Refused("CLEANUP_MODE")
        for _attempt in range(3):
            doc, p = self._read()
            kept = [r for r in p["rules"] if expired_only and self.clock() < r["expires_at"]]
            removed = len(p["rules"]) - len(kept)
            if not removed:
                return {"status": "API_ACCEPTED", "removed": 0, "cleanup_verified": False}
            p["rules"] = kept
            try:
                self._replace(doc, p)
                return {"status": "API_ACCEPTED", "removed": removed, "cleanup_verified": False}
            except Exception as error:
                if getattr(error, "status", None) != 409:
                    raise
        raise Refused("STATE_CONFLICT")
