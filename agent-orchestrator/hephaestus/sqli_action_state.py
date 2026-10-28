"""SQLi action postconditions; read-only, supplied with independently joined probe receipts.

The caller must admit the decision through the existing guard and obtain the API result from
SqliContainment. Never accept model/HTTP assertions as probe evidence. This component neither sends
requests nor enables an executor. Availability RECOVERY_VERIFIED belongs to the independent H-plane
measurement evaluator, not this healer. A historical successful action does not prove current health.
"""
import copy
import math
import re
from urllib.parse import urlsplit

from hephaestus.sqli_containment import MAX_TTL, Refused, SqliContainment


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def uid(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f-]{36}", value)


class SqliActionState:
    """One accepted action: API_ACCEPTED -> ACTION_COMPLETED with an explicit terminal status.

    Replaying the same evidence reconstructs state without writing/renewing a policy. An expired
    deadline or FAILED/PARTIAL terminal cannot be turned into SUCCESS by a late probe. A successful
    action may subsequently record separately verified Pod replacement; it emits no second terminal.
    """
    def __init__(self, api_result, pins, *, fixture_uid, accepted_at, timeout_s):
        self.target = SqliContainment(None, **copy.deepcopy(pins))  # validates pins, no API call
        rule = copy.deepcopy(api_result.get("rule", {}))
        if (api_result.get("status") != "API_ACCEPTED" or api_result.get("containment_verified") is not False or
                set(rule) != {"action_id", "client_ip", "created_at", "expires_at", "request_id"} or
                not isinstance(rule.get("action_id"), str) or not re.fullmatch(r"act_[0-9a-f]{32}", rule["action_id"]) or
                not isinstance(rule.get("request_id"), str) or not re.fullmatch(r"[0-9a-f]{32}", rule["request_id"]) or
                rule["client_ip"] != self.target.attacker or
                type(rule["created_at"]) is not int or type(rule["expires_at"]) is not int or
                not 0 < rule["expires_at"] - rule["created_at"] <= MAX_TTL or
                not number(accepted_at) or not rule["created_at"] <= accepted_at < rule["expires_at"] or
                not number(timeout_s) or not 0 < timeout_s <= MAX_TTL or not uid(fixture_uid)):
            raise Refused("ACTION_RECEIPT")
        self.rule, self.fixture_uid, self.accepted_at = rule, fixture_uid, accepted_at
        self.deadline = min(accepted_at + timeout_s, rule["expires_at"])
        self.terminal, self.completed_at, self.restart = None, None, None

    def _time(self, now):
        if not number(now) or now < self.accepted_at:
            raise Refused("OBSERVATION_CLOCK")

    def snapshot(self):
        return copy.deepcopy({
            "action_id": self.rule["action_id"],
            "phase": "ACTION_COMPLETED" if self.terminal else "API_ACCEPTED",
            "api_accepted_at": self.accepted_at, "deadline": self.deadline,
            "terminal": self.terminal, "completed_at": self.completed_at, "restart": self.restart,
            "recovery_verification": "EXTERNAL_PROBE_REQUIRED", "causal_attribution": "UNPROVEN",
        })

    def poll(self, now):
        self._time(now)
        if self.terminal is None and now >= self.deadline:
            self.fail("TIMEOUT", "POSTCONDITION_TIMEOUT", now=now)
        return self.snapshot()

    def fail(self, status, error, *, now):
        self._time(now)
        if status not in {"FAILED", "PARTIAL", "TIMEOUT"} or not isinstance(error, str) or not error:
            raise Refused("ACTION_TERMINAL")
        if self.terminal is None:
            self.terminal = {"status": status, "postcondition": {
                "name": "SQLI_SOURCE_CONTAINMENT", "checked": False, "satisfied": False,
                "observed": None}, "error": error}
            self.completed_at = now
        return self.snapshot()

    def _access(self, record, source, blocked, fixture_uid, now):
        try:
            http, access = record["http"], record["access"]
            request, response = http["request"], http["response"]
            begin, end, observed = response["begin"], response["end"], access["ts"]
            if (record["pod_uid"] != fixture_uid or not isinstance(record["ref"], str) or not record["ref"] or
                    not all(number(t) for t in (begin, end, observed)) or
                    not self.accepted_at <= begin <= observed <= end <= now < self.rule["expires_at"] or
                    not isinstance(response["request_id"], str) or
                    not re.fullmatch(r"[0-9a-f]{32}", response["request_id"]) or
                    response["request_id"] != access["request_id"] or
                    not isinstance(request["correlation"], str) or
                    not re.fullmatch(r"[0-9a-f]{32}", request["correlation"]) or
                    request["correlation"] != access["correlation_id"] or
                    request["method"] != access["method"] or
                    urlsplit(request["path"]).path != access["path"] or
                    response["status"] != access["status"] or access["client_ip"] != source or
                    access["source_method"] != "XFF_AFTER_TRUSTED" or access["source_confidence"] != "PROXY_CHAIN" or
                    access["tcp_peer"] not in {str(n.network_address) for n in self.target.proxies} or
                    access["enforcement_point"] != "sqli-fixture/trusted-client" or access["blocked"] is not blocked or
                    access["action_ids"] != ([self.rule["action_id"]] if blocked else []) or
                    not isinstance(access["policy_sha256"], str) or
                    not re.fullmatch(r"[0-9a-f]{64}", access["policy_sha256"])):
                raise Refused("POSTCONDITION_EVIDENCE")
            return request, response, access
        except (KeyError, TypeError, ValueError) as error:
            raise Refused("POSTCONDITION_EVIDENCE") from error

    def observe(self, attacker, benign, *, fixture, now, replacement=None):
        self._time(now)
        self.poll(now)
        if self.terminal is not None and self.terminal["status"] != "SUCCESS":
            return self.snapshot()
        try:
            current_uid = fixture["uid"]
            if not uid(current_uid) or fixture.get("ready") is not True:
                raise Refused("POD_POSTCONDITION")
            if current_uid != self.fixture_uid:
                if (not isinstance(replacement, dict) or replacement.get("old_uid") != self.fixture_uid or
                        replacement.get("new_uid") != current_uid or replacement.get("old_absent") is not True):
                    raise Refused("POD_REPLACEMENT_UNVERIFIED")
            if type(benign) is not list or len(benign) != 5:
                raise Refused("BENIGN_PROBE_MISSING")
            a = self._access(attacker, self.target.attacker, True, current_uid, now)
            b = [self._access(row, self.target.benign, False, current_uid, now) for row in benign]
            order_ref = b[1][1]["body"]["order_ref"]
            if not isinstance(order_ref, str) or not re.fullmatch(r"[0-9a-f]{32}", order_ref):
                raise Refused("BENIGN_PROBE_CONTENT")
            order_path = "/fixture/orders/" + order_ref
            expected = [("GET", "/fixture/catalog/search", 200), ("POST", "/fixture/orders", 201),
                        ("GET", order_path, 200), ("DELETE", order_path, 200), ("GET", order_path, 404)]
            all_records = [attacker, *benign]
            if (a[1]["status"] != 403 or a[1]["body"] != {"error": "SOURCE_BLOCKED"} or
                    a[2]["path"] != "/fixture/catalog/search" or a[0]["method"] != "GET" or
                    [(q["method"], j["path"], s["status"]) for q, s, j in b] != expected or
                    b[0][1]["body"].get("count", 0) < 1 or
                    b[1][1]["body"] != b[2][1]["body"] or b[1][1]["body"].get("status") != "STORED" or
                    any(b[1][0]["body"][key] != b[1][1]["body"][key] for key in ("item", "note")) or
                    b[3][1]["body"] != {"deleted": 1} or b[4][1]["body"] != {"error": "NOT_FOUND"} or
                    any(left[1]["end"] > right[1]["begin"] for left, right in zip([a, *b], b)) or
                    len({r["http"]["response"]["request_id"] for r in all_records}) != 6 or
                    len({r["http"]["request"]["correlation"] for r in all_records}) != 6 or
                    len({j["policy_sha256"] for _, _, j in [a, *b]}) != 1):
                raise Refused("POSTCONDITION_EVIDENCE")
            observed = {"pod_uid": current_uid, "policy_uid": self.target.uid,
                        "policy_sha256": a[2]["policy_sha256"], "rule_expires_at": self.rule["expires_at"],
                        "probe_refs": [r["ref"] for r in all_records]}
            if self.terminal is None:
                self.terminal = {"status": "SUCCESS", "postcondition": {
                    "name": "SQLI_SOURCE_CONTAINMENT", "checked": True, "satisfied": True,
                    "observed": observed}, "error": None}
                self.completed_at = now
            if current_uid != self.fixture_uid:
                self.restart = {"old_uid": self.fixture_uid, "new_uid": current_uid,
                                "old_absent": True, "verified_at": now, "postcondition": observed}
            return self.snapshot()
        except (KeyError, TypeError, ValueError) as error:
            raise Refused("POSTCONDITION_EVIDENCE") from error
