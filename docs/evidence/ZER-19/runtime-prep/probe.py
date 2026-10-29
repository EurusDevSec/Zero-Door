"""A single fixed benign catalog request, executed only inside owned Nemesis Pod."""
from datetime import datetime, timezone
import json
import sys
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import uuid

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("REDIRECT_REFUSED")

stage = sys.argv[1]
if stage not in {"before", "after"}:
    raise RuntimeError("PROBE_SCOPE")
correlation = "zer19-" + stage + "-" + uuid.uuid4().hex
request = Request("http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search?category=apparel",
                  headers={"X-Correlation-Id": correlation})
with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=3) as response:
    raw = response.read(262145)
    if len(raw) > 262144:
        raise RuntimeError("BODY_LIMIT")
    body = json.loads(raw)
    if response.status != 200 or sorted(x["sku"] for x in body["results"]) != ["PUB-APP-001", "PUB-APP-002"]:
        raise RuntimeError("BENIGN_RESULT")
    print(json.dumps({"status": response.status, "body": body, "request_id": response.headers.get("X-Request-Id"),
                      "correlation_id": correlation, "observed_at": datetime.now(timezone.utc).isoformat()}))
