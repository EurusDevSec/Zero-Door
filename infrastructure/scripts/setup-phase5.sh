#!/usr/bin/env bash
set -euo pipefail
run_smoke=false
install_deps=false
smoke_runs=2
while (( $# )); do
    case $1 in
        --help|-h)
            printf '%s\n' 'Usage: bash infrastructure/scripts/setup-phase5.sh [--install-deps] [--run-smoke] [--smoke-runs N]' \
                'Default: health checks and foreground HTTP port-forwards only; no attacks or pip install.' \
                '--install-deps creates/uses .venv-experiments, never global pip.' \
                '--run-smoke explicitly runs the legacy E1 AUTO runner; data goes to a new scratch directory.' \
                'Legacy runner/Kafka access limitations remain; this is not a formal research result.'
            exit 0 ;;
        --skip-experiments) run_smoke=false; shift ;;
        --run-smoke) run_smoke=true; shift ;;
        --install-deps) install_deps=true; shift ;;
        --smoke-runs) [[ $# -ge 2 ]] || { printf 'Missing run count\n' >&2; exit 2; }; smoke_runs=$2; shift 2 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done
[[ $smoke_runs =~ ^[1-9][0-9]*$ ]] || { printf 'Run count must be a positive integer\n' >&2; exit 2; }
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
zd_require curl
zd_preflight
if $install_deps; then
    zd_python
    "$ZD_PYTHON" -m venv "$(zd_path "$ZD_ROOT/.venv-experiments")"
fi
if $install_deps || $run_smoke; then
    if [[ -f $ZD_ROOT/.venv-experiments/Scripts/python.exe ]]; then
        ZD_PYTHON="$ZD_ROOT/.venv-experiments/Scripts/python.exe"
    elif [[ -f $ZD_ROOT/.venv-experiments/bin/python ]]; then
        ZD_PYTHON="$ZD_ROOT/.venv-experiments/bin/python"
    else
        zd_python
    fi
fi
if $install_deps; then
    "$ZD_PYTHON" -m pip install -r "$(zd_path "$ZD_INFRA/scripts/requirements-experiments.txt")"
fi
zd_forwards_init
zd_forward zero-door hephaestus 9091:8000
zd_forward zero-door nemesis 9092:8000
zd_forward monitoring prometheus-operated 9090:9090
zd_wait_http http://127.0.0.1:9091/healthz
zd_wait_http http://127.0.0.1:9092/healthz
zd_wait_http http://127.0.0.1:9090/-/ready
if $run_smoke; then
    zd_forward zero-door kafka 9093:9092
    zd_log 'Legacy Kafka advertised-listener access from the host may fail; a tunnel does not prove Kafka readiness.'
    # Python subprocesses in the old runner use kubectl without --context.
    # Give that child only the explicitly selected context, without changing the user's current-context.
    ZD_RUN_CONFIG="$ZD_FORWARD_DIR/kubeconfig"
    (umask 077; zd_kubectl config view --minify --flatten --raw >"$ZD_RUN_CONFIG")
    export KUBECONFIG
    KUBECONFIG=$(zd_path "$ZD_RUN_CONFIG")
    export NEMESIS_URL=http://127.0.0.1:9092 HEPHAESTUS_URL=http://127.0.0.1:9091
    export PROMETHEUS_URL=http://127.0.0.1:9090 KAFKA_BOOTSTRAP=127.0.0.1:9093
    export STEADY_STATE_WAIT_SEC=15 PYTHONUTF8=1 PYTHONIOENCODING=utf-8
    output="$ZD_ROOT/scratch/experiments/$(date +%Y%m%dT%H%M%S)-$$"
    mkdir -p -- "$output"
    zd_log "Legacy smoke data: $output/raw_data (separate from historical/formal data)."
    "$ZD_PYTHON" - "$(zd_path "$ZD_INFRA/scripts/experiment_runner.py")" "$(zd_path "$output/raw_data")" "$smoke_runs" <<'PY'
import importlib.util, pathlib, sys
runner, output, runs = sys.argv[1:]
spec = importlib.util.spec_from_file_location("zero_door_legacy_smoke", runner)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.RESULTS_DIR = pathlib.Path(output)
sys.argv = [runner, "--scenario", "E1", "--mode", "AUTO", "--runs", runs, "--skip-steady-state"]
module.main()
PY
    zd_check_forwards
    zd_log 'Legacy runner returned; inspect every recorded failure. No automatic analysis of historical datasets was run.'
else
    zd_log 'HTTP checks passed. No experiment was triggered.'
    zd_supervise_forwards
fi
