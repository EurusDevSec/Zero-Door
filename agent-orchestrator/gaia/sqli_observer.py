"""Gaia detection from a delivered worker response joined to native fixture telemetry.

No expected case or model output enters the detector. The caller reads native
logs and pins pod/source identities; this function performs no I/O.
"""
from datetime import datetime
import re
from event_pipeline.contract import Producer, new_id


def observe_worker(context, receipt, raw, *, fixture_uid, pod_uid, source_ip, proxy_ip,
                   begin, end, at, ref):
    """Join received worker counts to raw fixture log; never fabricate an HTTP body."""
    commands = [r["command"] for r in receipt["records"] if r["event"] == "DISPATCH_INTENT"]
    results = [r["raw"] for r in receipt["records"] if r["event"] == "EXECUTOR_RESULT"]
    if len(commands) != 1 or len(results) != 1:
        raise ValueError("NATIVE_WORKER_CARDINALITY")
    command, result = commands[0], results[0]
    sends = result["details"]["sqli"]["sends"]
    if (command["context"] != {k:context[k] for k in ("run_id","trial_id","group")} or result["commandId"] != command["commandId"]
            or result["status"] != "SUCCESS" or len(sends) != 1):
        raise ValueError("NATIVE_WORKER_CONTEXT")
    send = sends[0]
    stamps = [datetime.fromisoformat(send[k].replace("Z", "+00:00")) for k in ("startedAt","observedAt")]
    if any(t.tzinfo is None for t in stamps):
        raise ValueError("WORKER_TIMESTAMP_TIMEZONE_REQUIRED")
    started, observed = (t.timestamp() for t in stamps)
    # Go isoAt truncates to milliseconds (sqli.go), so a canonical .dddZ
    # observedAt represents [observed, observed+1ms), not an exact upper instant.
    # This accounts only for representation loss, never cross-host clock skew.
    observed_resolution = 0.001 if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", send["observedAt"]) else 0
    before_observed_end = (raw["ts"] < observed + observed_resolution if observed_resolution
                           else raw["ts"] <= observed)
    if (pod_uid != fixture_uid or not re.fullmatch(r"[a-f0-9]{32}", send.get("responseId") or "")
            or send["responseId"] != raw.get("request_id")
            or send.get("requestId") != command["commandId"] + "/1"
            or raw.get("correlation_id") != send["requestId"] or send.get("seq") != 1
            or raw.get("method") != "GET" or raw.get("path") != "/fixture/catalog/search"
            or raw.get("client_ip") != source_ip or raw.get("tcp_peer") != proxy_ip
            or raw.get("source_method") != "XFF_AFTER_TRUSTED" or raw.get("source_confidence") != "PROXY_CHAIN"
            or send.get("status") != 200 or raw.get("status") != 200 or send.get("error")
            or raw.get("delivered", True) is not True
            or type(send.get("rows")) is not int or type(send.get("restrictedRows")) is not int
            or not 0 <= send["restrictedRows"] <= send["rows"]
            or raw.get("rows") != send["rows"] or raw.get("restricted_rows") != send["restrictedRows"]
            or not begin <= started <= observed <= end <= at
            or not started <= raw["ts"] or not before_observed_end
            or not 0 <= at - raw["ts"] <= 60):
        raise ValueError("NATIVE_WORKER_ACCESS_JOIN")
    detection = Producer("detector", "gaia-native-sqli-reader/1", {
        "clock_id":"host", "clock_source":"UNKNOWN", "resolution_ms":None}).event(context, "DETECTED", {
            "rule_id":"SUSPICIOUS_LOG", "rule_version":"1", "signature":"SQLI/fixture",
            "metric":"log_pattern_match", "value":int(raw["restricted_rows"] > 0), "threshold":0,
            "severity":"WARNING", "description":"Joined delivered worker response and native fixture access"},
        "o.alert", target={"namespace":"zd-sqli-lab","service":"sqli-fixture","flow":None}, alert_id=new_id("alt"))
    fields = ("request_id","ts","client_ip","tcp_peer","source_method","source_confidence",
              "method","path","status","rows","restricted_rows")
    access = {**{k:raw[k] for k in fields}, "delivered":True, "ref":ref,
        "run_id":context["run_id"], "trial_id":context["trial_id"], "fixture_uid":fixture_uid,
        "detection_event_id":detection["event_id"]}
    evidence = {"metric":{"name":"log_pattern_match","value":detection["payload"]["value"],"threshold":0},
        "log":{"message":detection["payload"]["description"],"observed_at":None}}
    return {"detection":detection,"evidence":evidence,"access":access}
