#!/usr/bin/env bash
# Real (non-mocked) regression for the Traefik ingress contract. Reads no cluster state and changes nothing:
#   1. pinned chart: pull, SHA-256, render with the repo values; ServiceMonitor keeps backend labels
#      (honorLabels), no CRD, file-provider rewrites, IngressClass, args; the port-80 rollback render.
#   2. PromQL consumers: promtool evaluates the PrometheusRule alerts and the Gaia/Nemesis queries, read from
#      source, on synthetic Traefik series (frontend, a hyphenated service, another namespace, 5xx, latency,
#      healthy traffic without 5xx, and the exported_service shape a scrape without honorLabels would store),
#      plus the consumer gate on a cold-start burst (one sample: never passes) and on two confirmed scrapes.
#   3. Kafka heap postrenderer (real Helm), fail-closed contract and target rollout quota budget.
set -euo pipefail
case ${1:-} in
    --help|-h)
        printf '%s\n' 'Usage: bash tests/shell/test-local-restore.sh' \
            'Needs helm, Python 3 with PyYAML, network access to https://traefik.github.io/charts, and promtool' \
            '(on PATH or ZD_PROMTOOL; the Prometheus release the lab runs, 3.15.0). No kubectl, Docker or lab access.'
        exit 0 ;;
    '') ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
esac
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)/infrastructure/scripts/lib/common.sh"
zd_require helm
zd_python
promtool=${ZD_PROMTOOL:-$(command -v promtool || true)}
[[ -n $promtool && -x $promtool ]] || zd_die 'promtool not found: put it on PATH or set ZD_PROMTOOL.'
work=$(mktemp -d "$ZD_ROOT/scratch/restore-tests.XXXXXX")
cleanup() { case $work in "$ZD_ROOT"/scratch/restore-tests.?*) rm -rf -- "$work" ;; esac; }
trap cleanup EXIT
failures=0
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1" >&2; failures=$((failures + 1)); }

# 1. Chart render contract.
version=$(zd_chart_version traefik)
expected=$(grep -B3 '^traefik:' "$ZD_INFRA/helm-values/chart-versions.yaml" | grep -o -E 'sha256 [0-9a-f]{64}' | cut -d' ' -f2 || true)
[[ -n $expected ]] || zd_die 'chart-versions.yaml has no full sha256 comment above traefik.'
zd_helm pull traefik --repo https://traefik.github.io/charts --version "$version" --destination "$(zd_path "$work")" >/dev/null
tgz="$work/traefik-$version.tgz"
actual=$(sha256sum "$tgz" | cut -d' ' -f1)
if [[ $actual == "$expected" ]]; then pass "traefik $version chart SHA-256 matches chart-versions.yaml"; else fail "traefik chart SHA-256 $actual"; fi
# Same flags as setup-phase1.sh; kube-version is the lab's K3s.
render() {
    zd_helm template traefik "$(zd_path "$tgz")" -n kube-system --kube-version 1.31.5 \
        --api-versions monitoring.coreos.com/v1 --skip-crds \
        -f "$(zd_path "$ZD_INFRA/helm-values/traefik-values.yaml")" "$@"
}
render >"$work/render.yaml"
# Rollback step that frees node port 80 without removing the release (traefik-migration.md, rollback).
render --set service.spec.type=ClusterIP >"$work/render-rollback.yaml"
if ! "$ZD_PYTHON" - "$(zd_path "$work/render.yaml")" "$(zd_path "$work/render-rollback.yaml")" <<'PY'; then
import sys, yaml
failed = False
def check(condition, message):
    global failed
    print(("PASS: " if condition else "FAIL: ") + message)
    failed = failed or not condition
def load(path):
    docs = {}
    for doc in yaml.safe_load_all(open(path, encoding="utf-8")):
        if doc:
            docs.setdefault(doc["kind"], []).append(doc)
    return docs
docs, rollback = load(sys.argv[1]), load(sys.argv[2])
monitors = docs.get("ServiceMonitor", [])
endpoints = monitors[0]["spec"]["endpoints"] if len(monitors) == 1 else []
check(bool(endpoints) and all(e.get("honorLabels") is True for e in endpoints),
      "ServiceMonitor keeps the Traefik backend label (honorLabels: true on every endpoint)")
check("CustomResourceDefinition" not in docs, "render creates no CRD")
classes = docs.get("IngressClass", [])
check([c["metadata"]["name"] for c in classes] == ["traefik"]
      and classes[0]["metadata"].get("annotations", {}).get("ingressclass.kubernetes.io/is-default-class") != "true",
      "one IngressClass traefik, not the default class")
files = [c for c in docs.get("ConfigMap", []) if c["metadata"]["name"] == "traefik-file-provider"]
middlewares = yaml.safe_load(files[0]["data"]["config.yml"])["http"]["middlewares"] if files else {}
check(all(middlewares.get(f"{n}-prefix", {}).get("replacePathRegex") == {"regex": f"^/{n}(/|$)(.*)", "replacement": "/$2"}
          for n in ("nemesis", "hephaestus")), "file provider rewrites /nemesis and /hephaestus like rewrite-target /$2")
args = docs["Deployment"][0]["spec"]["template"]["spec"]["containers"][0]["args"]
for arg in ("--providers.kubernetesingress.strictPrefixMatching=true", "--accesslog.format=json",
            "--metrics.prometheus.buckets=0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10",
            "--metrics.prometheus.addServicesLabels=true", "--global.checkNewVersion=false"):
    check(arg in args, f"Traefik arg {arg}")
check(not any(a.startswith("--providers.kubernetescrd") for a in args), "Kubernetes CRD provider is off")
service = [s for s in docs["Service"] if s["metadata"]["name"] == "traefik"][0]["spec"]
check(service["type"] == "LoadBalancer" and [p["port"] for p in service["ports"]] == [80, 443],
      "Service traefik is a LoadBalancer on ports 80/443 (k3d maps host 8080/8443)")
back = [s for s in rollback["Service"] if s["metadata"]["name"] == "traefik"][0]["spec"]
check(back["type"] == "ClusterIP" and "externalTrafficPolicy" not in back,
      "rollback render: Service traefik becomes ClusterIP (frees node port 80), release kept")
check(sorted(rollback) == sorted(docs), "rollback render keeps the same object kinds")
sys.exit(1 if failed else 0)
PY
    fail 'chart render contract'
fi

# 2. PromQL consumers on synthetic series.
queries=$(zd_agent_queries)
"$ZD_PYTHON" - "$(zd_path "$ZD_INFRA/manifests/prometheus-rules.yaml")" "$queries" "$(zd_path "$work")" <<'PY'
import json, pathlib, sys, yaml
rule_crd, queries, out = sys.argv[1], json.loads(sys.argv[2]), pathlib.Path(sys.argv[3])
groups = yaml.safe_load(open(rule_crd, encoding="utf-8"))["spec"]["groups"]
(out / "rules.yaml").write_text(yaml.safe_dump({"groups": groups}, sort_keys=False), encoding="utf-8")
numerator, denominator = queries["gaia.error_rate_query"].split(" / ")
F, R = "target-app-frontend-80@kubernetes", "target-app-redis-cart-6379@kubernetes"
N, X = "zero-door-nemesis-8000@kubernetes", "target-app-cartservice-7070@kubernetes"
def requests(service, code, per_scrape, extra=""):
    return {"series": f'traefik_service_requests_total{{service="{service}",code="{code}",method="GET",protocol="http"{extra}}}',
            "values": f"1000+{per_scrape}x40"}
def buckets(service, per_scrape_by_le, extra=""):
    return [{"series": f'traefik_service_request_duration_seconds_bucket{{service="{service}",code="200",method="GET",protocol="http",le="{le}"{extra}}}',
             "values": f"1000+{n}x40"} for le, n in per_scrape_by_le]
exported = ',exported_service="%s"' % X
# Scrape interval 15s, so per-scrape increments of 60/15/30 are 4, 1 and 2 requests per second.
traffic = ([requests(F, "200", 60), requests(F, "503", 15), requests(R, "200", 30), requests(N, "500", 60),
            requests("traefik-metrics", "500", 60, exported)]
           + buckets(F, [("0.005", 0), ("0.1", 0), ("1", 0), ("2.5", 75), ("+Inf", 75)])
           + buckets(R, [("0.005", 30), ("0.1", 30), ("1", 30), ("2.5", 30), ("+Inf", 30)])
           + buckets("traefik-metrics", [("0.005", 0), ("+Inf", 60)], exported))
def sample(value, **labels):
    rendered = ",".join(f'{k}="{v}"' for k, v in labels.items())
    return {"labels": "{" + rendered + "}", "value": value}
# The consumer gate of verify-local-lab.sh: frontend value above 0 (NaN > bool 0 is 0, no sample stays no sample).
def gate(expr):
    return f"({expr}) > bool 0"
def gate_exprs(expected):
    return [(denominator, sample(expected, service="frontend")), (queries["gaia.latency_query"], sample(expected, service="frontend")),
            (queries["nemesis.http_rps"], sample(expected))]
annotations = {
    "HighErrorRate": ("High HTTP 5xx error rate for service frontend", "HTTP 5xx error rate is above 5% on service frontend."),
    "HighLatency": ("High latency on service frontend", "99th percentile of HTTP request duration for service frontend is above 1000ms."),
}
tests = [
    {   # frontend 20% 5xx and P99 between 1s and 2.5s; redis-cart healthy; zero-door and exported_service ignored
        "interval": "15s", "input_series": traffic,
        "promql_expr_test": [
            {"expr": queries["gaia.error_rate_query"], "eval_time": "5m", "exp_samples": [sample(0.2, service="frontend")]},
            {"expr": denominator, "eval_time": "5m",
             "exp_samples": [sample(5, service="frontend"), sample(2, service="redis-cart")]},
            {"expr": queries["gaia.latency_query"], "eval_time": "5m",
             "exp_samples": [sample(2.485, service="frontend"), sample(0.00495, service="redis-cart")]},
            {"expr": queries["nemesis.http_rps"], "eval_time": "5m", "exp_samples": [sample(7)]},
            {"expr": queries["nemesis.error_rate"], "eval_time": "5m", "exp_samples": [sample(1 / 7)]},
        ],
        "alert_rule_test": [
            {"alertname": name, "eval_time": "5m", "exp_alerts": [
                {"exp_labels": {"severity": severity, "service": "frontend"},
                 "exp_annotations": {"summary": summary, "description": description}}]}
            for name, severity, (summary, description) in
            (("HighErrorRate", "critical", annotations["HighErrorRate"]), ("HighLatency", "warning", annotations["HighLatency"]))
        ],
    },
    {   # healthy traffic: backend metric present, no 5xx series, so the ratio is empty, not zero
        "interval": "15s", "input_series": [requests(F, "200", 60)] + buckets(F, [("0.005", 60), ("+Inf", 60)]),
        "promql_expr_test": [
            {"expr": denominator, "eval_time": "5m", "exp_samples": [sample(4, service="frontend")]},
            {"expr": numerator, "eval_time": "5m", "exp_samples": []},
            {"expr": queries["gaia.error_rate_query"], "eval_time": "5m", "exp_samples": []},
            {"expr": queries["nemesis.http_rps"], "eval_time": "5m", "exp_samples": [sample(4)]},
        ],
        "alert_rule_test": [{"alertname": "HighErrorRate", "eval_time": "5m", "exp_alerts": []}],
    },
    {   # what a scrape without honorLabels stores: every consumer is blind (the TFM-01 failure mode)
        "interval": "15s",
        "input_series": [requests("traefik-metrics", "503", 60, ',exported_service="%s"' % F)]
                        + buckets("traefik-metrics", [("0.005", 0), ("+Inf", 60)], ',exported_service="%s"' % F),
        "promql_expr_test": [{"expr": queries[q], "eval_time": "5m", "exp_samples": []} for q in sorted(queries)]
                            + [{"expr": denominator, "eval_time": "5m", "exp_samples": []}],
        "alert_rule_test": [{"alertname": "HighErrorRate", "eval_time": "5m", "exp_alerts": []}],
    },
    {   # cold start: every request ended before the new series' first scrape, then idle. The counter is positive
        # but never moves, so rate is 0 and P99 NaN at any time: the consumer gate must not pass on one sample.
        "interval": "15s",
        "input_series": [requests(F, "200", 0)] + buckets(F, [("0.005", 0), ("1", 0), ("+Inf", 0)]),
        "promql_expr_test": [{"expr": gate(expr), "eval_time": t, "exp_samples": [exp]}
                             for t in ("30s", "1m", "2m") for expr, exp in gate_exprs(0)],
    },
    {   # what verify-local-lab.sh --check consumers produces: 3 requests before the first scrape of the series (30s),
        # 3 more after it, a second scrape (45s) and the queries right after (50s). 65s later, without new requests,
        # Gaia's 1m window holds no increase again; Nemesis' 2m window still does.
        "interval": "15s",
        "input_series": [{"series": f'traefik_service_requests_total{{service="{F}",code="200",method="GET",protocol="http"}}',
                          "values": "_ _ 3 6 6 6 6 6 6 6 6"}]
                        + [{"series": f'traefik_service_request_duration_seconds_bucket{{service="{F}",code="200",method="GET",protocol="http",le="{le}"}}',
                            "values": values} for le, values in (("0.005", "_ _ 0 0 0 0 0 0 0 0 0"),
                                                                 ("1", "_ _ 3 6 6 6 6 6 6 6 6"), ("+Inf", "_ _ 3 6 6 6 6 6 6 6 6"))],
        "promql_expr_test": [{"expr": gate(expr), "eval_time": "50s", "exp_samples": [exp]} for expr, exp in gate_exprs(1)]
                            + [{"expr": gate(expr), "eval_time": "1m50s", "exp_samples": [exp]}
                               for expr, exp in zip((denominator, queries["gaia.latency_query"], queries["nemesis.http_rps"]),
                                                    (sample(0, service="frontend"), sample(0, service="frontend"), sample(1)))],
    },
]
# fuzzy_compare: rate() of these exact counters returns e.g. 4.999999999999999 for 5.
# evaluation_interval = scrape interval: promtool loads samples only up to its last evaluation step (default 1m),
# so a query at 1m50s would otherwise not see the samples after 60s.
(out / "traefik.test.yaml").write_text(
    yaml.safe_dump({"rule_files": ["rules.yaml"], "evaluation_interval": "15s", "fuzzy_compare": True, "tests": tests},
                   sort_keys=False),
    encoding="utf-8")
PY
if (cd "$work" && "$promtool" test rules traefik.test.yaml); then
    pass 'promtool: PrometheusRule alerts, Gaia/Nemesis queries and the consumer gate on synthetic Traefik series'
else
    fail 'promtool rule/query tests'
fi
# 3. Kafka: run the actual Helm postrenderer and verify the ONLY semantic delta.
kafka_version=$(zd_chart_version kafka)
zd_helm pull oci://registry-1.docker.io/bitnamicharts/kafka --version "$kafka_version" --destination "$(zd_path "$work")" >/dev/null
kafka_chart="$work/kafka-$kafka_version.tgz"
[[ $(sha256sum "$kafka_chart" | cut -d' ' -f1) == 8d32f6b9f3e207ace675ab80453ac49c303fbacfa5dcc385fa27d38bdb36a57e ]] || zd_die 'Kafka 29.3.2 chart SHA changed; review before use.'
kafka_render() {
    zd_helm template kafka "$(zd_path "$kafka_chart")" -n zero-door --kube-version 1.31.5 \
        -f "$(zd_path "$ZD_INFRA/helm-values/kafka-values.yaml")" \
        --set kraft.clusterId=QXRvbWljS2Fma2FUZXN0MQ "$@"
}
kafka_render >"$work/kafka-before.yaml"
zd_kafka_renderer
kafka_render "${ZD_KAFKA_RENDERER[@]}" >"$work/kafka-after.yaml"
if ! "$ZD_PYTHON" - "$(zd_path "$work")" "$(zd_path "$ZD_ROOT")" <<'PY'; then
import copy, importlib.util, pathlib, sys, yaml
sys.dont_write_bytecode = True
work, root = map(pathlib.Path, sys.argv[1:])
def load(path):
    return [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]
def identity(d):
    m = d["metadata"]
    return d["kind"], m.get("namespace", ""), m["name"]
before = {identity(d): d for d in load(work / "kafka-before.yaml")}
after = {identity(d): d for d in load(work / "kafka-after.yaml")}
key = ("StatefulSet", "zero-door", "kafka-controller")
def jmx(objects):
    return next(c for c in objects[key]["spec"]["template"]["spec"]["containers"] if c["name"] == "jmx-exporter")
assert "-Xmx128m" not in jmx(before)["args"], "pre-fix case must expose the missing heap cap"
assert "-XX:MaxRAMPercentage=100" in jmx(before)["args"]
assert jmx(after)["args"][:2] == ["-Xms32m", "-Xmx128m"]
expected = copy.deepcopy(before)
args = jmx(expected)["args"]
i = args.index("-XX:MaxRAMPercentage=100")
args[i:i+1] = ["-Xms32m", "-Xmx128m"]
assert after == expected, "renderer changed an object other than JMX JVM arguments"
spec = importlib.util.spec_from_file_location("jmx_renderer", root / "infrastructure/helm-postrenderers/kafka-jmx/render.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for broken in ([], list(after.values())):
    try:
        module.render(copy.deepcopy(broken))
    except ValueError:
        pass
    else:
        raise AssertionError("unknown/already-patched layout must fail closed")
wrong = copy.deepcopy(before)
jmx(wrong)["resources"]["limits"]["memory"] = "128Mi"
try:
    module.render(list(wrong.values()))
except ValueError:
    pass
else:
    raise AssertionError("a changed JMX budget must be reviewed")
print("PASS: actual Helm renderer caps JMX heap, preserves all other objects and refuses unknown layouts")

# This baseline requires explicit resources; missing values fail, not silently
# substitute unmodeled LimitRange defaults. Check every quota dimension.
def quantity(value, scale):
    s = str(value)
    return float(s[:-1]) if s.endswith("m") else float(s) * scale
def mib(value):
    s = str(value)
    return float(s[:-2]) * (1024 if s.endswith("Gi") else 1) if s.endswith(("Mi", "Gi")) else float(s) / 1048576
target = load(root / "infrastructure/manifests/target-app.yaml") + load(root / "infrastructure/manifests/target-app-addons.yaml")
deploys = {d["metadata"]["name"]: d for d in target if d["kind"] == "Deployment"}
dimensions = ("requests.cpu", "requests.memory", "limits.cpu", "limits.memory")
def vector(resources):
    result = {}
    for key in dimensions:
        level, resource = key.split(".")
        value = resources[level][resource]  # Missing values must fail this explicit baseline.
        result[key] = quantity(value, 1000) if resource == "cpu" else mib(value)
    return result
def add(*vectors):
    return {key: sum(v[key] for v in vectors) for key in dimensions}
def fits(usage, budget):
    return all(usage[key] <= budget[key] for key in dimensions)
pods = {}
for d in deploys.values():
    spec = d["spec"]
    assert spec.get("replicas", 1) == 1, "Review quota model if replicas change"
    strategy = spec.get("strategy", {})
    assert strategy.get("type", "RollingUpdate") == "RollingUpdate"
    rolling = strategy.get("rollingUpdate", {})
    assert rolling.get("maxSurge", "25%") in (1, "25%"), "Review changed surge"
    assert rolling.get("maxUnavailable", "25%") in (0, "25%")
    pod = spec["template"]["spec"]
    assert not pod.get("initContainers") and not pod.get("overhead"), "Review effective pod resources"
    pods[d["metadata"]["name"]] = add(*(vector(c["resources"]) for c in pod["containers"]))
steady = add(*pods.values())
quota_docs = load(root / "infrastructure/resource-quotas/target-app-quota.yaml")
hard = next(d for d in quota_docs if d["kind"] == "ResourceQuota")["spec"]["hard"]
budget = vector({level: {resource: hard[f"{level}.{resource}"] for resource in ("cpu", "memory")}
                 for level in ("requests", "limits")})
assert fits(steady, budget)
for name, surge in pods.items():
    peak = add(steady, surge)
    assert fits(peak, budget), (name, peak, budget)
    for key in dimensions:
        restricted = dict(budget, **{key: peak[key] - 1})
        assert not fits(peak, restricted), f"quota check ignored {key}"
concurrent = add(steady, *(pods[n] for n in ("currencyservice", "emailservice", "paymentservice")))
assert concurrent["limits.cpu"] == 3025 and not fits(concurrent, budget)
print("PASS: concurrent three-service surge needs 3025m > 3000m; sequential surge fits all four quota dimensions for all nine Deployments")
for name in ("currencyservice", "emailservice", "paymentservice"):
    c = deploys[name]["spec"]["template"]["spec"]["containers"][0]
    startup = c["startupProbe"]
    assert 60 <= startup["periodSeconds"] * startup["failureThreshold"] <= 120
    assert startup["grpc"]["port"] == c["livenessProbe"]["grpc"]["port"]
    assert c["readinessProbe"]["timeoutSeconds"] == c["livenessProbe"]["timeoutSeconds"] == 3
print(f"PASS: target steady budget {steady['requests.cpu']:g}m/{steady['requests.memory']:g}Mi requests, {steady['limits.cpu']:g}m/{steady['limits.memory']:g}Mi limits; probes unchanged")
PY
    fail 'Kafka heap renderer / baseline admission contract'
fi
(( failures == 0 )) || { printf '%d check group(s) failed.\n' "$failures" >&2; exit 1; }
printf 'All real render and PromQL regression checks passed. No cluster command was used.\n'
