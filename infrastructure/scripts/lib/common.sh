#!/usr/bin/env bash
# Shared local tooling. Source from an entry point that enables set -euo pipefail.
ZD_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
ZD_INFRA="$ZD_ROOT/infrastructure"
ZD_CLUSTER=zero-door
ZD_CONTEXT=k3d-zero-door
ZD_FORWARD_PIDS=()
ZD_FORWARD_LOGS=()
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

# Native Windows CLIs must not rewrite container paths, URLs, or --as identities.
# Convert host-side file arguments explicitly with zd_path instead.
ZD_WINDOWS=false
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) ZD_WINDOWS=true; export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' ;;
esac

zd_log() { printf '%s\n' "$*"; }
zd_die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
zd_require() {
    local tool
    for tool in "$@"; do
        command -v "$tool" >/dev/null 2>&1 || zd_die "Missing command: $tool"
    done
}
zd_path() {
    if "$ZD_WINDOWS"; then
        cygpath -m -- "$1"
    else
        printf '%s\n' "$1"
    fi
}
zd_python() {
    local candidate
    for candidate in "${PYTHON:-}" python python3; do
        [[ -n $candidate ]] || continue
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys' >/dev/null 2>&1; then
            ZD_PYTHON=$candidate
            return
        fi
    done
    zd_die 'Python 3 is required (or set PYTHON to its executable).'
}
zd_kubectl() { command kubectl --context="$ZD_CONTEXT" "$@"; }
# Helm state stays inside the checkout (gitignored scratch/) unless ZD_HELM_HOME is set,
# so chart pulls never edit the user's global repositories or cache.
zd_helm() {
    local home=${ZD_HELM_HOME:-$ZD_ROOT/scratch/helm}
    mkdir -p -- "$home/cache" "$home/config" "$home/data"
    HELM_CACHE_HOME=$(zd_path "$home/cache") HELM_CONFIG_HOME=$(zd_path "$home/config") \
        HELM_DATA_HOME=$(zd_path "$home/data") HELM_PLUGINS=$(zd_path "$home/data/plugins") \
        command helm --kube-context="$ZD_CONTEXT" "$@"
}
# Prepare the Kafka JMX renderer inside this checkout's Helm home, never globally.
zd_kafka_renderer() {
    zd_python
    "$ZD_PYTHON" -c 'import yaml' >/dev/null 2>&1 || zd_die 'Kafka rendering requires PyYAML in the selected Python environment.'
    local version home plugin
    version=$(zd_helm version --template '{{.Version}}')
    case $version in
        v4.*)
            home=${ZD_HELM_HOME:-$ZD_ROOT/scratch/helm}
            plugin="$home/data/plugins/zero-door-kafka-jmx"
            mkdir -p -- "$plugin"
            cp -- "$ZD_INFRA/helm-postrenderers/kafka-jmx/plugin.yaml" "$ZD_INFRA/helm-postrenderers/kafka-jmx/render.py" "$plugin/"
            export ZD_POSTRENDER_PYTHON="$ZD_PYTHON"
            ZD_KAFKA_RENDERER=(--post-renderer zero-door-kafka-jmx)
            ;;
        v3.*)
            ZD_KAFKA_RENDERER=(--post-renderer "$ZD_PYTHON"
                --post-renderer-args "$(zd_path "$ZD_INFRA/helm-postrenderers/kafka-jmx/render.py")")
            ;;
        *) zd_die "Unsupported Helm version for Kafka renderer: $version" ;;
    esac
}
zd_apply() { zd_kubectl apply -f "$(zd_path "$1")"; }
# The single source of chart versions is infrastructure/helm-values/chart-versions.yaml.
zd_chart_version() {
    local version
    version=$(sed -n "s/^$1:[[:space:]]*\"\{0,1\}\([^\"[:space:]]*\)\"\{0,1\}[[:space:]]*\$/\1/p" \
        "$ZD_INFRA/helm-values/chart-versions.yaml")
    [[ -n $version ]] || zd_die "No pinned chart version for $1 in helm-values/chart-versions.yaml."
    printf '%s\n' "$version"
}
# Builds/imports and kubectl use the Docker daemon selected by the current Docker context.
zd_docker_guard() {
    local expected=${ZD_DOCKER_CONTEXT:-desktop-linux} actual
    actual=$(docker context show) || zd_die 'Cannot read the Docker context.'
    [[ $actual == "$expected" ]] || \
        zd_die "Docker context is '$actual', expected '$expected'. Switch it yourself or set ZD_DOCKER_CONTEXT."
    [[ -z ${DOCKER_HOST:-} ]] || zd_die 'DOCKER_HOST overrides the Docker context; unset it first.'
}
zd_preflight() {
    zd_require docker kubectl k3d
    zd_docker_guard
    docker info >/dev/null
    zd_kubectl get nodes --request-timeout=10s
}
zd_build_import() {
    local image=$1 directory=$2
    shift 2
    docker build "$@" -t "$image" "$(zd_path "$directory")"
    k3d image import "$image" -c "$ZD_CLUSTER"
}
# A mutable tag with an unchanged manifest does not replace running pods; after the restart,
# require every running pod of the Deployment to report the image ID that was just built.
zd_verify_image() {
    local image=$1 namespace=$2 deployment=$3 expected config selector ids id
    expected=$(docker image inspect --format '{{.Id}}' "$image")
    # With Docker's containerd image store, .Id is the OCI index digest while the CRI reports the
    # config digest; read the config digest from the same export that `k3d image import` uses.
    config=$(docker save "$image" | tar -xO manifest.json |
        sed -n 's/.*"Config":"\(blobs\/sha256\/\)\{0,1\}\([0-9a-f]\{64\}\)\(\.json\)\{0,1\}".*/sha256:\2/p') || config=
    selector=$(zd_kubectl get deployment "$deployment" -n "$namespace" \
        -o 'go-template={{range $k, $v := .spec.selector.matchLabels}}{{$k}}={{$v}},{{end}}')
    # Terminating pods of the previous ReplicaSet may still be Running; skip them.
    ids=$(zd_kubectl get pods -n "$namespace" -l "${selector%,}" --field-selector=status.phase=Running \
        -o 'go-template={{range .items}}{{if not .metadata.deletionTimestamp}}{{range .status.containerStatuses}}{{.imageID}}{{"\n"}}{{end}}{{end}}{{end}}')
    [[ -n $ids ]] || zd_die "No running pod reports an image for $namespace/$deployment."
    while IFS= read -r id; do
        [[ $id == *"${expected#sha256:}" || ( -n $config && $id == *"${config#sha256:}" ) ]] ||
            zd_die "$namespace/$deployment runs $id, expected $expected (config ${config:-unknown})."
    done <<<"$ids"
    zd_log "$namespace/$deployment runs $image (image $expected, config ${config:-not read})."
}

zd_fix_local_api() {
    local server cluster port config backup
    server=$(zd_kubectl config view --minify -o 'jsonpath={.clusters[0].cluster.server}')
    [[ $server == https://host.docker.internal:* ]] || return 0
    # Only repair the known local Docker Desktop mapping after testing it with TLS.
    port=$(docker port k3d-zero-door-serverlb 6443/tcp)
    port=${port%%$'\n'*}
    port=${port##*:}
    [[ $port =~ ^[0-9]+$ ]] || zd_die 'Cannot determine published API port.'
    zd_kubectl --server="https://127.0.0.1:$port" get nodes --request-timeout=10s >/dev/null
    cluster=$(zd_kubectl config view --minify -o 'jsonpath={.clusters[0].name}')
    [[ $cluster == "$ZD_CONTEXT" ]] || zd_die 'Unexpected kubeconfig cluster entry; leaving it unchanged.'
    [[ -z ${KUBECONFIG:-} ]] || zd_die 'Custom KUBECONFIG: repair its server explicitly after backing it up.'
    config="$HOME/.kube/config"
    backup="$config.zero-door-backup-$(date +%Y%m%dT%H%M%S)-$$"
    cp -p -- "$config" "$backup"
    zd_kubectl config set-cluster "$cluster" --server="https://127.0.0.1:$port"
    zd_log "Kubeconfig backup: $backup"
}

zd_ensure_cluster() {
    local clusters exists
    zd_require docker kubectl k3d
    zd_python
    zd_docker_guard
    docker info >/dev/null
    clusters=$(k3d cluster list -o json)
    exists=$(printf '%s' "$clusters" | "$ZD_PYTHON" -c \
        'import json,sys; print(any(x["name"] == "zero-door" for x in json.load(sys.stdin)))')
    if [[ $exists == True ]]; then
        k3d cluster start "$ZD_CLUSTER"
    else
        # Add the context to the default kubeconfig without making it current for other projects.
        k3d cluster create --config "$(zd_path "$ZD_INFRA/k3d-config.yaml")" --kubeconfig-switch-context=false
    fi
    zd_fix_local_api
    zd_kubectl wait --for=condition=Ready nodes --all --timeout=120s
}

# Prints, as JSON {"gaia.error_rate_query": ..., ...}, the ingress PromQL that Gaia and Nemesis send,
# read from their source, so probes and tests evaluate exactly what the agents query.
zd_agent_queries() {
    zd_python
    "$ZD_PYTHON" - "$(zd_path "$ZD_ROOT/agent-orchestrator/gaia/main.py")" \
        "$(zd_path "$ZD_ROOT/agent-orchestrator/nemesis/main.py")" <<'PY'
import ast, json, sys
found = {}
for agent, path in (("gaia", sys.argv[1]), ("nemesis", sys.argv[2])):
    for node in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ("error_rate_query", "latency_query")
                and isinstance(node.value, ast.Constant)):
            found[f"{agent}.{node.targets[0].id}"] = node.value.value
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (isinstance(key, ast.Constant) and key.value in ("http_rps", "error_rate")
                        and isinstance(value, ast.Constant)):
                    found[f"{agent}.{key.value}"] = value.value
wanted = {"gaia.error_rate_query", "gaia.latency_query", "nemesis.http_rps", "nemesis.error_rate"}
if wanted - found.keys():
    sys.exit("Agent query not found in source: " + ", ".join(sorted(wanted - found.keys())))
print(json.dumps({name: found[name] for name in sorted(wanted)}))
PY
}
zd_apply_nemesis() {
    local existing filtered result
    # --ignore-not-found distinguishes absence from API/authentication failures.
    existing=$(zd_kubectl get secret nemesis-secrets -n zero-door --ignore-not-found -o name)
    if [[ -z $existing ]]; then
        zd_apply "$ZD_INFRA/manifests/nemesis-deployment.yaml"
        zd_log 'Created empty Nemesis Secret template; no live LLM credential is implied.'
        return
    fi
    zd_python
    filtered=$(mktemp)
    "$ZD_PYTHON" - "$(zd_path "$ZD_INFRA/manifests/nemesis-deployment.yaml")" >"$filtered" <<'PY'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
docs = re.split(r"(?m)^---\s*$", text)
print("\n---\n".join(doc for doc in docs if doc.strip() and
                      not re.search(r"(?m)^kind:\s*Secret\s*$", doc)))
PY
    if zd_apply "$filtered"; then result=0; else result=$?; fi
    rm -f -- "$filtered"
    (( result == 0 )) || return "$result"
    zd_log 'Preserved existing nemesis-secrets; applied non-Secret documents only.'
}

zd_cleanup_forwards() {
    local pid
    for pid in "${ZD_FORWARD_PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
    for pid in "${ZD_FORWARD_PIDS[@]}"; do wait "$pid" 2>/dev/null || true; done
    if [[ -n ${ZD_RUN_CONFIG:-} ]]; then rm -f -- "$ZD_RUN_CONFIG"; fi
    ZD_FORWARD_PIDS=()
    ZD_FORWARD_LOGS=()
    unset ZD_RUN_CONFIG
}
zd_forwards_init() {
    ZD_FORWARD_DIR=$(mktemp -d)
    trap zd_cleanup_forwards EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    zd_log "Port-forward logs: $ZD_FORWARD_DIR"
}
zd_forward() {
    local namespace=$1 service=$2 mapping=$3 log
    zd_kubectl get service "$service" -n "$namespace" >/dev/null
    log="$ZD_FORWARD_DIR/$service.log"
    # Start the external process directly; $! belongs only to this invocation.
    command kubectl --context="$ZD_CONTEXT" -n "$namespace" port-forward \
        "svc/$service" "$mapping" --address=127.0.0.1 >"$log" 2>&1 &
    ZD_FORWARD_PIDS+=("$!")
    ZD_FORWARD_LOGS+=("$log")
}
zd_check_forwards() {
    local i
    for (( i=0; i<${#ZD_FORWARD_PIDS[@]}; i++ )); do
        if ! kill -0 "${ZD_FORWARD_PIDS[$i]}" 2>/dev/null; then
            cat -- "${ZD_FORWARD_LOGS[$i]}" >&2
            zd_die 'Port-forward exited. Check occupied ports, service endpoints and pod readiness.'
        fi
    done
}
zd_wait_http() {
    local url=$1 attempt
    for (( attempt=1; attempt<=15; attempt++ )); do
        zd_check_forwards
        if curl --fail --silent --show-error --max-time 3 "$url" >/dev/null 2>&1; then
            zd_check_forwards
            return
        fi
        sleep 1
    done
    zd_die "HTTP health check failed: $url"
}
zd_supervise_forwards() {
    zd_log 'Keep this terminal open. Ctrl+C stops only the port-forwards started here.'
    while :; do zd_check_forwards; sleep 1; done
}
