"""Finite acceptance operations inside the owned ZER-42 pods. No arbitrary target or query input."""
import json
from pathlib import Path
import socket
import sys
import time
import uuid
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

PROXY = "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("REDIRECT_REFUSED")


def http(url, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    request = Request(url, data=data, headers=headers or {})
    try:
        response = build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=5)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read(262145)
        if len(raw) > 262144:
            raise ValueError("BODY_LIMIT")
        return {"status": response.status, "request_id": response.headers.get("X-Request-Id"),
                "body": json.loads(raw)}


def main():
    mode = sys.argv[1]
    if mode == "control":
        correlation = uuid.uuid4().hex
        result = http(PROXY + "/fixture/catalog/search?category=apparel",
                      headers={"X-Correlation-Id": correlation, "X-Forwarded-For": "203.0.113.77"})
        result["correlation_id"] = correlation
        assert result["status"] == 200 and result["request_id"]
        assert all(row["visibility"] == "public" for row in result["body"]["results"])
        assert sorted(row["sku"] for row in result["body"]["results"]) == ["PUB-APP-001", "PUB-APP-002"]
    elif mode == "direct":
        with socket.socket() as sock:
            sock.settimeout(2)
            try:
                sock.connect(("sqli-fixture.zd-sqli-lab.svc.cluster.local", 9140))
            except (socket.timeout, ConnectionRefusedError):
                result = {"direct_fixture": "DENIED"}
            else:
                raise RuntimeError("DIRECT_FIXTURE_REACHABLE")
    elif mode == "health":
        result = http("http://127.0.0.1:8000/healthz")
        assert result["status"] == 200 and result["body"]["kafka_connected"] is True
    elif mode == "trigger":
        identifier, template = sys.argv[2:]
        assert str(uuid.UUID(identifier)) == identifier
        assert template in {"disclose-restricted", "benign-apparel", "invalid-control"}
        key = json.loads(Path("/operator/key.json").read_bytes())
        result = http("http://127.0.0.1:8000/attack/trigger",
                      {"attackType": "SQLI", "template": template, "durationSec": 5},
                      {"Content-Type": "application/json", "Authorization": "Bearer " + key["secret"],
                       "Idempotency-Key": identifier})
        assert result["status"] == (400 if template == "invalid-control" else 200), result
    elif mode == "read":
        from kafka import KafkaConsumer
        topic = sys.argv[2]
        assert topic.startswith("zer42-") and topic.endswith((".commands", ".results"))
        consumer = KafkaConsumer(topic, bootstrap_servers="kafka.zero-door.svc.cluster.local:9092",
            group_id=None, enable_auto_commit=False, auto_offset_reset="earliest", consumer_timeout_ms=10000,
            request_timeout_ms=15000, session_timeout_ms=6000, api_version_auto_timeout_ms=5000)
        messages = []
        end = time.monotonic() + 25
        try:
            for message in consumer:
                messages.append({"topic": message.topic, "partition": message.partition,
                                 "offset": message.offset, "value": json.loads(message.value)})
                if len(messages) > 20 or time.monotonic() > end:
                    raise ValueError("BROKER_READ_CAP")
        finally:
            consumer.close()
        result = messages
    else:
        raise ValueError("UNKNOWN_MODE")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()

