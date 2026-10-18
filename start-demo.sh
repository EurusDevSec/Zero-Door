#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf '%s\n' 'Usage: bash start-demo.sh [--nemesis-only]' \
        'Checks existing services and runs localhost port-forwards in this terminal.' \
        'Does not deploy the lab. Ctrl+C stops only its own child processes.'
    exit 0
fi
[[ $# == 0 || ( $# == 1 && $1 == --nemesis-only ) ]] || { printf 'Unknown argument\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/infrastructure/scripts/lib/common.sh"
zd_require curl
zd_preflight
zd_forwards_init
zd_forward zero-door nemesis 9092:8000
if [[ ${1:-} != --nemesis-only ]]; then
    zd_forward zero-door hephaestus 9091:8000
    zd_forward monitoring prometheus-operated 9090:9090
    zd_forward monitoring prometheus-grafana 3000:80
fi
zd_wait_http http://127.0.0.1:9092/healthz
if [[ ${1:-} != --nemesis-only ]]; then
    zd_wait_http http://127.0.0.1:9091/healthz
    zd_wait_http http://127.0.0.1:9090/-/ready
    zd_wait_http http://127.0.0.1:3000/api/health
    zd_wait_http http://127.0.0.1:8080/
    zd_log 'HTTP checks passed: Boutique :8080, Hephaestus :9091, Prometheus :9090, Grafana :3000.'
fi
zd_log 'Nemesis HTTP check passed: http://127.0.0.1:9092/dashboard/'
zd_log 'HTTP success alone does not verify Kafka, an LLM call or purchase/recovery behavior.'
zd_supervise_forwards
