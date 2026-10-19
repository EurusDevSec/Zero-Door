"""Restricted operational telemetry proxy; no caller-selected URL or index."""
import copy
import json
from urllib.request import Request, urlopen

from .contract import canonical

# Only the clause shapes the frozen Gaia log query needs. Lookups (terms with index/id/path),
# more_like_this, percolate, script, regexp/wildcard/prefix, query_string, nested, has_child,
# aggregations and every other clause are rejected, so no other index or costly query runs.
LEAF = {"term", "terms", "match", "match_phrase", "range", "exists", "match_all"}
BOOL = {"must", "filter", "should", "must_not"}
RANGE = {"gte", "gt", "lte", "lt", "format"}
MAX_DEPTH, MAX_CLAUSES, MAX_BYTES, MAX_TEXT = 6, 32, 8192, 512


def scalar(value):
    if isinstance(value, str):
        return len(value) <= MAX_TEXT
    return value is None or type(value) in (int, float, bool)


def field_of(clause):
    if not isinstance(clause, dict) or len(clause) != 1:
        raise ValueError("UNSUPPORTED_LOG_QUERY")
    field, value = next(iter(clause.items()))
    if not isinstance(field, str) or not field or len(field) > 128 or field.startswith("_"):
        raise ValueError("UNSUPPORTED_LOG_QUERY")
    return value


def check_query(query, depth=0, budget=None):
    budget = budget if budget is not None else [MAX_CLAUSES]
    budget[0] -= 1
    if depth > MAX_DEPTH or budget[0] < 0 or not isinstance(query, dict) or len(query) != 1:
        raise ValueError("UNSUPPORTED_LOG_QUERY")
    kind, body = next(iter(query.items()))
    if kind == "bool":
        if not isinstance(body, dict) or set(body) - BOOL - {"minimum_should_match"}:
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        if "minimum_should_match" in body and type(body["minimum_should_match"]) is not int:
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        for occurrence in BOOL & set(body):
            clauses = body[occurrence] if isinstance(body[occurrence], list) else [body[occurrence]]
            for clause in clauses:
                check_query(clause, depth + 1, budget)
        return
    if kind not in LEAF:
        raise ValueError("UNSUPPORTED_LOG_QUERY")
    if kind == "match_all":
        if body != {}:
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        return
    if kind == "exists":
        if not isinstance(body, dict) or set(body) != {"field"} or not isinstance(body["field"], str):
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        return
    value = field_of(body)
    if kind == "terms":
        # A dict here is a terms lookup into another index; only literal value lists pass.
        if not isinstance(value, list) or len(value) > 64 or not all(scalar(v) for v in value):
            raise ValueError("UNSUPPORTED_LOG_QUERY")
    elif kind == "range":
        if not isinstance(value, dict) or not value or set(value) - RANGE or not all(scalar(v) for v in value.values()):
            raise ValueError("UNSUPPORTED_LOG_QUERY")
    elif isinstance(value, dict):
        allowed = {"term": {"value"}, "match": {"query", "operator"}, "match_phrase": {"query"}}[kind]
        if set(value) - allowed or not all(scalar(v) for v in value.values()):
            raise ValueError("UNSUPPORTED_LOG_QUERY")
    elif not scalar(value):
        raise ValueError("UNSUPPORTED_LOG_QUERY")


class Telemetry:
    def __init__(self, prometheus, elasticsearch, queries):
        self.prometheus = prometheus.rstrip("/")
        self.elasticsearch = elasticsearch.rstrip("/")
        self.queries = frozenset(queries)

    @staticmethod
    def fetch(url, body=None):
        request = Request(url, data=canonical(body) if body is not None else None,
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    def metrics(self, query):
        from urllib.parse import urlencode
        if query not in self.queries:
            raise ValueError("QUERY_NOT_ALLOWLISTED")
        return self.fetch(self.prometheus + "/api/v1/query?" + urlencode({"query": query}))

    def logs(self, body):
        if not isinstance(body, dict) or set(body) - {"query", "size"}:
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        if len(canonical(body)) > MAX_BYTES or type(body.get("size", 50)) is not int:
            raise ValueError("UNSUPPORTED_LOG_QUERY")
        check_query(body.get("query", {"match_all": {}}))
        query = {"query": {"bool": {"must": [copy.deepcopy(body.get("query", {"match_all": {}}))],
                                    "filter": [{"term": {"kubernetes.namespace_name.keyword": "target-app"}}]}},
                 "size": min(max(body.get("size", 50), 0), 100)}
        result = self.fetch(self.elasticsearch + "/zero-door-logs-*/_search", query)
        # Fail closed even if the upstream index's mapping/filter is wrong.
        hits = result.get("hits", {}).get("hits", [])
        if any(hit.get("_source", {}).get("kubernetes", {}).get("namespace_name") != "target-app" for hit in hits):
            raise ValueError("UPSTREAM_NAMESPACE_VIOLATION")
        # No aggregations, stored scripts, _msearch, arbitrary indices or control logs.
        return {"took": result.get("took"), "timed_out": result.get("timed_out"),
                "hits": {"total": {"value": len(hits), "relation": "eq"}, "hits": hits}}
