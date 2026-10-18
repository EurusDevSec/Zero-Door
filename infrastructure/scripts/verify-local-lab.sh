#!/usr/bin/env bash
set -euo pipefail
checks=all
expect_es=blocked
while (( $# )); do
    case $1 in
        --help|-h)
            printf '%s\n' 'Usage: bash infrastructure/scripts/verify-local-lab.sh [--check NAME] [--expect-open]' \
                'NAME: purchase, telemetry, logs, kafka, agents, policies, ingress, consumers, all (default).' \
                'Non-chaos probes of the local lab in k3d-zero-door:' \
                '  purchase  : home, product, add to cart, cart, checkout with demo data through a loopback tunnel' \
                '  telemetry : Prometheus ready, no down targets, cAdvisor CPU series for target-app' \
                '              (all down targets, including obsolete frontend /metrics targets, fail)' \
                '  logs      : a unique frontend request path reaches Elasticsearch via Fluent Bit' \
                '  kafka     : produce/consume a correlation ID on the separate topic zd.verify.restore' \
                '  agents    : GET /healthz of gaia, nemesis, hephaestus, chaos-worker rollout, and no Prometheus' \
                '              query error in the Gaia log of the last 10 minutes (a log that cannot be read fails)' \
                '  policies  : a short-lived busybox pod in target-app must reach frontend but not Elasticsearch' \
                '              (--expect-open checks the same flow before network-policies.yaml is applied)' \
                '  ingress   : host :8080 through Traefik (frontend, /nemesis and /hephaestus rewrites), the request' \
                '              in the Traefik access log and Elasticsearch, a Traefik service counter in Prometheus,' \
                '              and the client address Traefik records for the host and for an in-cluster pod;' \
                '              the ServiceMonitor keeps the backend label (honorLabels); then the consumers check' \
                '  consumers : rounds of 3 healthy GET /_healthz through host :8080, each followed by a Prometheus' \
                '              scrape that holds them (at most 4 rounds, 12 requests); right after the second such' \
                '              scrape the Gaia/Nemesis queries read from source must return frontend data above 0' \
                '              (an empty 5xx numerator means "no 5xx yet"); no exported_* label on traefik_service_*' \
                'Never calls attack, heal, reset or LLM endpoints and never generates load.' \
                'Exit 0: every probe passed. Exit 1: any failed probe.'
            exit 0 ;;
        --check) [[ $# -ge 2 ]] || { printf 'Missing check\n' >&2; exit 2; }; checks=$2; shift 2 ;;
        --expect-open) expect_es=open; shift ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
case $checks in purchase|telemetry|logs|kafka|agents|policies|ingress|consumers|all) ;; *) printf 'Invalid check\n' >&2; exit 2 ;; esac
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_require curl
zd_preflight >/dev/null
run_id="zd$(date +%Y%m%d%H%M%S)$$"
failures=0
ok() { zd_log "PASS $1"; }
bad() { zd_log "FAIL $1"; failures=$((failures + 1)); }
want() { [[ $checks == all || $checks == "$1" ]]; }
# Read-only GET through the API server service proxy; no local tunnel needed.
proxy_get() { zd_kubectl get --raw "/api/v1/namespaces/$1/services/$2/proxy$3" --request-timeout=20s; }
python_json() { zd_python; "$ZD_PYTHON" -c "$1"; }
urlencode() { zd_python; "$ZD_PYTHON" -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"; }
# Instant query; prints the result vector as JSON lines {"labels": {...}, "value": "..."}.
prom_query() {
    proxy_get monitoring prometheus-operated:9090 "/api/v1/query?query=$(urlencode "$1")" |
        python_json 'import json,sys
for r in json.load(sys.stdin)["data"]["result"]:
    m = r["metric"]; m.pop("__name__", None); print(json.dumps({"labels": m, "value": r["value"][1]}))'
}
es_ready=0
es_tunnel() {
    (( es_ready )) || { zd_forward monitoring elasticsearch 19200:9200; zd_wait_http http://127.0.0.1:19200/_cluster/health; es_ready=1; }
}
# Documents in zero-door-logs-* whose message contains the phrase, optionally limited to one container.
es_count() {
    local q="message:\"$1\""
    [[ -z ${2:-} ]] || q="$q AND kubernetes.container_name:$2"
    curl --silent --show-error --max-time 10 -G 'http://127.0.0.1:19200/zero-door-logs-*/_count' --data-urlencode "q=$q" |
        python_json 'import json,sys; print(json.load(sys.stdin).get("count",0))' || printf 0
}
# Host path: 127.0.0.1:8080 -> k3d serverlb -> K3s servicelb -> Service kube-system/traefik:80 -> Ingress.
lb=http://127.0.0.1:8080
lbget() { curl --silent --show-error --max-time 10 -o "$(zd_path "$ZD_FORWARD_DIR/ingress.out")" -w '%{http_code}' "$@" || printf 000; }
frontend_backend='service="target-app-frontend-80@kubernetes"'
# First value of an instant query, or "absent".
scalar() { prom_query "$1" | python_json 'import json,sys; v=[json.loads(l)["value"] for l in sys.stdin if l.strip()]; print(v[0] if v else "absent")'; }
# True when $1 is a finite number above $2 ("absent" counts as below any value; NaN is never above).
above() {
    zd_python
    "$ZD_PYTHON" -c 'import math,sys; a,b=sys.argv[1:3]; sys.exit(0 if a not in ("absent","") and math.isfinite(float(a)) and float(a) > (float(b) if b!="absent" else -1) else 1)' "$1" "$2"
}
want_consumers() { want consumers || want ingress; }

if want purchase || want logs || want ingress || want consumers; then zd_forwards_init; fi
if want purchase || want logs; then
    zd_forward target-app frontend 18080:80
    zd_wait_http http://127.0.0.1:18080/_healthz
    # curl is a native Windows binary under Git Bash and MSYS path conversion is off: convert host paths.
    jar=$(zd_path "$ZD_FORWARD_DIR/cookies.txt")
    body=$(zd_path "$ZD_FORWARD_DIR/body.html")
    shop() { curl --silent --show-error --max-time 20 -b "$jar" -c "$jar" "$@"; }
    status() { shop -o "$body" -w '%{http_code}' "$@"; }
fi

if want purchase; then
    product=OLJCESPC7Z
    code=$(status http://127.0.0.1:18080/)
    [[ $code == 200 ]] && ok "home page HTTP $code" || bad "home page HTTP $code"
    code=$(status "http://127.0.0.1:18080/product/$product")
    [[ $code == 200 ]] && ok "product page HTTP $code" || bad "product page HTTP $code"
    code=$(status -d "product_id=$product" -d quantity=1 http://127.0.0.1:18080/cart)
    [[ $code == 302 || $code == 200 ]] && ok "add to cart HTTP $code" || bad "add to cart HTTP $code"
    if shop http://127.0.0.1:18080/cart | grep -q "$product"; then ok 'cart lists the product'; else bad 'cart does not list the product'; fi
    # Demo values only: the Boutique form's own sample card, local mock payment service, no external target.
    order=$(shop -L -d email=lab-check@example.com -d street_address='1 Lab Road' -d zip_code=10000 \
        -d city=Local -d state=LC -d country=Lab -d credit_card_number=4432801561520454 \
        -d credit_card_expiration_month=1 -d credit_card_expiration_year=2030 -d credit_card_cvv=672 \
        http://127.0.0.1:18080/cart/checkout)
    if grep -qi 'order is complete' <<<"$order"; then
        confirmation=$(tr -d '
' <<<"$order" | grep -o -i -E 'Confirmation.{0,400}' |
            grep -o -E '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1 || true)
        ok "checkout completed (order ${confirmation:-id not parsed})"
    else
        bad 'checkout page has no completion message'
    fi
    if zd_kubectl logs deployment/checkoutservice -n target-app --since=2m | grep -q 'payment went through'; then
        ok 'checkoutservice logged the mock payment'
    else
        bad 'checkoutservice did not log a payment in the last 2 minutes'
    fi
fi

if want telemetry; then
    if [[ $(proxy_get monitoring prometheus-operated:9090 /-/ready) == *Ready* ]]; then ok 'Prometheus ready'; else bad 'Prometheus not ready'; fi
    # One "job<TAB>namespace<TAB>lastError" line per target whose last scrape failed.
    down=$(proxy_get monitoring prometheus-operated:9090 '/api/v1/targets?state=active' |
        python_json 'import json,sys
for t in json.load(sys.stdin)["data"]["activeTargets"]:
    if t.get("health") == "down":
        l = t.get("labels", {})
        print(l.get("job", "?"), l.get("namespace", "?"), " ".join((t.get("lastError") or "no error").split()), sep="\t")')
    [[ -n $down ]] || ok 'no scrape target is down'
    while IFS=$'\t' read -r job namespace error; do
        [[ -n $job ]] || continue
        bad "scrape target $namespace/$job down: $error"
    done <<<"$down"
    kafka_up=$(proxy_get monitoring prometheus-operated:9090 '/api/v1/query?query=up%7Bjob%3D%22kafka-jmx-metrics%22%7D' |
        python_json 'import json,sys; r=json.load(sys.stdin)["data"]["result"]; print(r[0]["value"][1] if r else "absent")')
    [[ $kafka_up == 1 ]] && ok 'Kafka JMX metrics scraped' || bad "Kafka JMX target: $kafka_up"
    series=$(proxy_get monitoring prometheus-operated:9090 \
        '/api/v1/query?query=count(rate(container_cpu_usage_seconds_total%7Bnamespace%3D%22target-app%22%2Ccontainer!%3D%22%22%7D%5B2m%5D))' |
        python_json 'import json,sys; r=json.load(sys.stdin)["data"]["result"]; print(int(float(r[0]["value"][1])) if r else 0)')
    (( series >= 5 )) && ok "target-app CPU series from cAdvisor: $series containers" || bad "target-app CPU series: $series"
fi

if want logs; then
    # Elasticsearch queries go through a loopback tunnel: the API-server service proxy rejected
    # every Elasticsearch URL with a query string during restoration (raw error in evidence).
    es_tunnel
    sentinel="zd-log-sentinel-$run_id"
    status "http://127.0.0.1:18080/$sentinel" >/dev/null || true
    found=0
    for (( attempt=1; attempt<=12; attempt++ )); do
        sleep 5
        found=$(es_count "$sentinel")
        (( found > 0 )) && break
    done
    (( found > 0 )) && ok "log sentinel $sentinel found in Elasticsearch ($found docs)" || bad "log sentinel $sentinel not found within 60s"
fi

if want kafka; then
    topic=zd.verify.restore
    # CLI tools inside the broker container must not inherit the broker JMX port or its 384m heap:
    # they would fail to bind 5555 or push the shared 768Mi container limit towards OOM.
    cli_env=(env -u JMX_PORT -u KAFKA_JMX_OPTS "KAFKA_HEAP_OPTS=-Xms32m -Xmx128m")
    kafka() { zd_kubectl exec -i -n zero-door kafka-controller-0 -c kafka -- "${cli_env[@]}" "$@"; }
    kafka /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists \
        --topic "$topic" --partitions 1 --replication-factor 1 >/dev/null </dev/null
    printf '%s\n' "$run_id" | kafka /opt/bitnami/kafka/bin/kafka-console-producer.sh \
        --bootstrap-server localhost:9092 --topic "$topic"
    if kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic "$topic" \
        --from-beginning --timeout-ms 15000 </dev/null 2>/dev/null | grep -qx "$run_id"; then
        ok "Kafka round trip on $topic (correlation $run_id)"
    else
        bad "Kafka round trip on $topic"
    fi
    existing=$(kafka /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list </dev/null)
    for required in attack.commands attack.results monitoring.alerts healing.actions system.logs; do
        grep -qx "$required" <<<"$existing" && ok "topic $required exists" || bad "topic $required missing"
    done
fi

if want agents; then
    for agent in gaia nemesis hephaestus; do
        body=$(proxy_get zero-door "$agent:8000" /healthz || true)
        if [[ $body == *'"kafka_connected":true'* ]]; then ok "$agent /healthz $body"; else bad "$agent /healthz ${body:-no response}"; fi
    done
    if zd_kubectl rollout status deployment/chaos-worker -n zero-door --timeout=10s >/dev/null; then
        ok 'chaos-worker rollout complete'
    else
        bad 'chaos-worker rollout incomplete'
    fi
    # /healthz does not run any query; the polling loop logs these lines when Prometheus rejects or fails one.
    # The log is read first and its exit checked: a log that cannot be read is a failure, not "no error".
    if gaia_log=$(zd_kubectl logs deployment/gaia -n zero-door --since=10m 2>&1); then
        gaia_errors=$({ grep -E 'Error querying Prometheus|Prometheus query returned status' <<<"$gaia_log" || [[ $? == 1 ]]; } | tail -3)
        if [[ -z $gaia_errors ]]; then
            ok 'Gaia log read; no Prometheus query error in the last 10 minutes'
        else
            bad "Gaia Prometheus query errors: ${gaia_errors//$'\n'/ | }"
        fi
    else
        gaia_log=$(tail -2 <<<"$gaia_log")
        bad "cannot read the Gaia log, query errors unknown: ${gaia_log//$'\n'/ | }"
    fi
fi

if want policies; then
    # The pod uses the namespace LimitRange defaults and is removed by --rm when the command ends.
    result=$(zd_kubectl run "zd-np-probe-$$" -n target-app --rm -i --restart=Never --quiet \
        --image=busybox:1.36 --pod-running-timeout=120s --command -- sh -c \
        'sleep 3; c=CONTROL_FAIL; e=ES_BLOCKED;
         wget -T 5 -qO /dev/null http://frontend.target-app.svc.cluster.local/_healthz 2>/dev/null && c=CONTROL_OK;
         wget -T 5 -qO /dev/null http://elasticsearch.monitoring.svc.cluster.local:9200/ 2>/dev/null && e=ES_OPEN;
         echo "RESULT $c $e"' \
        2>&1 </dev/null || true)
    result=${result//$'\n'/ }
    [[ $result == *CONTROL_OK* ]] && ok 'probe pod reaches frontend (control flow)' || bad "control flow failed: $result"
    if [[ $expect_es == blocked ]]; then
        [[ $result == *ES_BLOCKED* ]] && ok 'target-app to Elasticsearch:9200 is blocked' || bad "target-app reached Elasticsearch: $result"
    else
        [[ $result == *ES_OPEN* ]] && ok 'target-app to Elasticsearch:9200 is open (pre-policy baseline)' || bad "pre-policy baseline: $result"
    fi
fi

if want ingress; then
    if zd_kubectl rollout status deployment/traefik -n kube-system --timeout=30s >/dev/null; then
        ok 'Traefik rollout complete'
    else
        bad 'Traefik rollout incomplete'
    fi
    # One access-log entry of the Traefik pod whose RequestPath contains $1, as "ClientHost ClientAddr RequestPath ServiceName status".
    # A log that cannot be read is reported as such instead of "entry missing".
    traefik_entry() {
        local logs line= attempt
        for (( attempt=1; attempt<=6; attempt++ )); do
            logs=$(zd_kubectl logs deployment/traefik -n kube-system --since=3m 2>&1) ||
                { printf 'cannot read the Traefik log: %s' "$(tail -1 <<<"$logs")"; return 1; }
            line=$({ grep -F "$1" <<<"$logs" || [[ $? == 1 ]]; } | tail -1)
            [[ -z $line ]] || break
            sleep 2
        done
        [[ -n $line ]] || return 1
        python_json 'import json,sys; d=json.loads(sys.stdin.read()); print(d.get("ClientHost"), d.get("ClientAddr"), d.get("RequestPath"), d.get("ServiceName"), d.get("DownstreamStatus"))' <<<"$line"
    }
    code=$(lbget "$lb/_healthz")
    [[ $code == 200 ]] && ok "host :8080 frontend /_healthz HTTP $code" || bad "host :8080 frontend /_healthz HTTP $code"
    for agent in nemesis hephaestus; do
        code=$(lbget "$lb/$agent/healthz")
        if [[ $code == 200 ]] && grep -q '"kafka_connected"' "$ZD_FORWARD_DIR/ingress.out"; then
            ok "/$agent/healthz is rewritten to $agent /healthz"
        else
            bad "/$agent/healthz HTTP $code"
        fi
    done
    # The encoded space shows whether RequestPath is logged raw or decoded; frontend answers 404, which is expected.
    # 192.0.2.10 (TEST-NET-1) is a forged client header: untrusted X-Forwarded-For must not become ClientHost.
    sentinel="zd-ingress-sentinel-$run_id"
    lbget -H 'X-Forwarded-For: 192.0.2.10' "$lb/$sentinel%20probe?run=$run_id" >/dev/null
    if entry=$(traefik_entry "$sentinel"); then
        ok "Traefik access log (ClientHost ClientAddr RequestPath ServiceName status): $entry"
        [[ $entry == *'@kubernetes'* ]] && ok 'host request was routed by the Kubernetes Ingress provider' ||
            bad "host request was not served by an Ingress route: $entry"
        [[ ${entry%% *} != *192.0.2.10* ]] && ok 'forged X-Forwarded-For is not recorded as ClientHost' ||
            bad "forged X-Forwarded-For became ClientHost: ${entry%% *}"
    else
        bad "host request $sentinel is not in the Traefik access log${entry:+ ($entry)}"
    fi
    es_tunnel
    found=0
    for (( attempt=1; attempt<=12; attempt++ )); do
        sleep 5
        found=$(es_count "$sentinel" traefik)
        (( found > 0 )) && break
    done
    (( found > 0 )) && ok "Traefik access log reached Elasticsearch ($found docs)" || bad "Traefik access log for $sentinel not in Elasticsearch within 60s"
    # In-cluster client: Traefik should record the pod's own address (no SNAT on pod-to-Service traffic).
    pod_sentinel="zd-ingress-pod-$run_id"
    probe=$(zd_kubectl run "zd-ingress-probe-$$" -n target-app --rm -i --restart=Never --quiet \
        --image=busybox:1.36 --pod-running-timeout=120s --command -- sh -c \
        "sleep 3; wget -T 5 -qO /dev/null http://traefik.kube-system.svc.cluster.local/$pod_sentinel 2>/dev/null; echo \"PODIP \$(hostname -i)\"" \
        2>&1 </dev/null || true)
    pod_ip=$(grep -o -E 'PODIP [0-9.]+' <<<"$probe" | cut -d' ' -f2 || true)
    if entry=$(traefik_entry "$pod_sentinel") && [[ -n $pod_ip && ${entry%% *} == "$pod_ip" ]]; then
        ok "in-cluster client address preserved: pod $pod_ip, Traefik ClientHost ${entry%% *}"
    else
        bad "in-cluster client address: pod ${pod_ip:-unknown}, Traefik entry ${entry:-missing}"
    fi
    # Label contract: Traefik's backend must stay in service. Without honorLabels the Operator's target label
    # service=traefik-metrics wins and the backend moves to exported_service, which every rule and agent query misses.
    honor=$(zd_kubectl get servicemonitor traefik -n kube-system -o 'jsonpath={.spec.endpoints[*].honorLabels}' || true)
    [[ $honor == true ]] && ok 'ServiceMonitor kube-system/traefik keeps backend labels (honorLabels: true)' ||
        bad "ServiceMonitor kube-system/traefik honorLabels: '${honor:-unset}'"
fi

if want_consumers; then
    # rate() and histogram_quantile() need two different samples inside the query window. Requests that all end
    # before the first scrape of a new series, or traffic older than the window (e.g. after the Elasticsearch and
    # pod waits above), leave rate 0 and P99 NaN although routing and scraping work. So this runs last, and each
    # round sends 3 healthy requests and waits for a scrape that holds them; the agents' queries run right after
    # the second such scrape, while both samples are inside Gaia's 1m window. Bounded: 4 rounds, 12 requests.
    poll=${ZD_VERIFY_POLL:-5}
    zd_python
    # "requests histogram_count" of the frontend backend at the latest scrape ("absent" before its first request).
    counts() {
        printf '%s %s' "$(scalar "sum(traefik_service_requests_total{$frontend_backend})" || printf absent)" \
            "$(scalar "sum(traefik_service_request_duration_seconds_count{$frontend_backend})" || printf absent)"
    }
    # 3 requests; prints the first non-200 status and fails.
    batch() {
        local i code
        for (( i=1; i<=3; i++ )); do
            code=$(lbget "$lb/_healthz")
            [[ $code == 200 ]] || { printf '%s' "$code"; return 1; }
        done
    }
    # Polls (at most 9 times, every $poll seconds) for a scrape with both counters above the sample in $1.
    next_sample() {
        local attempt
        for (( attempt=1; attempt<=9; attempt++ )); do
            sample=$(counts)
            above "${sample% *}" "${1% *}" && above "${sample#* }" "${1#* }" && return 0
            sleep "$poll"
        done
        return 1
    }
    frontend_value() { tr ' ' '\n' <<<"$1" | sed -n 's/^frontend=//p' | head -1; }
    services() { prom_query "$1" | python_json 'import json,sys; print(" ".join(sorted(json.loads(l)["labels"].get("service","?")+"="+json.loads(l)["value"] for l in sys.stdin if l.strip())))'; }
    # The agents' own PromQL, read from source; the build scripts already tied the running images to that source.
    queries=$(zd_agent_queries)
    agent_query() { "$ZD_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])[sys.argv[2]])' "$queries" "$1"; }
    # Gaia's error rate is "5xx by service / all by service": the denominator proves the backend metric exists,
    # an empty numerator only means no 5xx in the window (healthy traffic is not expected to produce one).
    error_query=$(agent_query gaia.error_rate_query)
    latency_query=$(agent_query gaia.latency_query)
    rps_query=$(agent_query nemesis.http_rps)
    [[ $error_query == *' / '* ]] || bad 'Gaia error-rate query is not a ratio'
    numerator=${error_query%% / *}
    denominator=${error_query#* / }
    previous=$(counts)
    history=$previous
    samples=0 sent=0 consumers=0 refused= backends= latency= rps=
    for (( round=1; round<=4; round++ )); do
        if ! refused=$(batch); then break; fi
        sent=$((sent + 3))
        next_sample "$previous" || break
        previous=$sample
        history="$history -> $sample"
        samples=$((samples + 1))
        (( samples >= 2 )) || continue
        backends=$(services "$denominator" || true)
        latency=$(services "$latency_query" || true)
        rps=$(scalar "$rps_query" || printf absent)
        if above "$(frontend_value "$backends")" 0 && above "$(frontend_value "$latency")" 0 && above "$rps" 0; then
            consumers=1
            break
        fi
    done
    [[ -z $refused ]] || bad "healthy request GET $lb/_healthz answered HTTP $refused"
    if (( samples >= 2 )); then
        ok "frontend requests/histogram count across $samples confirmed scrapes ($sent requests): $history"
    else
        bad "frontend counters did not grow across two confirmed scrapes ($sent requests): $history"
    fi
    labels=$(proxy_get monitoring prometheus-operated:9090 \
        "/api/v1/labels?match%5B%5D=$(urlencode '{__name__=~"traefik_service_.+"}')" |
        python_json 'import json,sys; print(" ".join(sorted(json.load(sys.stdin)["data"])))' || true)
    if [[ " $labels " == *' service '* && $labels != *exported_* ]]; then
        ok "traefik_service_* label names: $labels"
    else
        bad "traefik_service_* label names: ${labels:-none} (backend must be in service, no exported_* label)"
    fi
    if (( consumers )); then
        ok "Gaia error-rate denominator (1m) by service: $backends"
        ok "Gaia P99 latency (1m) by service: $latency"
        ok "Nemesis http_rps (2m): $rps"
    elif (( samples >= 2 )); then
        bad "agent queries lack frontend data after the confirmed scrapes: denominator '${backends:-}', latency '${latency:-}', Nemesis http_rps '${rps:-absent}'"
    else
        bad 'agent queries not evaluated: no two confirmed scrapes with fresh requests (rate would be 0, P99 NaN)'
    fi
    fives=$(services "$numerator" || true)
    ratio=$(services "$error_query" || true)
    nemesis_errors=$(scalar "$(agent_query nemesis.error_rate)" || printf absent)
    ok "5xx in window: Gaia numerator '${fives:-none}', ratio '${ratio:-none}', Nemesis error_rate '$nemesis_errors' (empty = no 5xx)"
fi

zd_log "Run $run_id finished with $failures failure(s)."
zd_log 'PASS here is a probe result, not research acceptance.'
(( failures > 0 )) || exit 0
exit 1
