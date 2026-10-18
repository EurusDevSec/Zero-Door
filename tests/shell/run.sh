#!/usr/bin/env bash
# Offline behavioral checks: every Docker/Kubernetes/Helm/curl command is mocked.
set -euo pipefail
TASK_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
mkdir -p -- "$TASK_ROOT/scratch"
task_temp=$(mktemp -d "$TASK_ROOT/scratch/bash-tests.XXXXXX")
task_supervisor=
task_unrelated=
cleanup() {
    [[ -z $task_supervisor ]] || kill "$task_supervisor" 2>/dev/null || true
    [[ -z $task_supervisor ]] || wait "$task_supervisor" 2>/dev/null || true
    [[ -z $task_unrelated ]] || kill "$task_unrelated" 2>/dev/null || true
    [[ -z $task_unrelated ]] || wait "$task_unrelated" 2>/dev/null || true
    # Only this mktemp-created workspace is eligible for recursive cleanup.
    case $task_temp in "$TASK_ROOT"/scratch/bash-tests.?*) rm -rf -- "$task_temp" ;; *) return 1 ;; esac
}
trap cleanup EXIT
task_fixture="$task_temp/checkout with spaces"
mkdir -p "$task_fixture/infrastructure/scripts/lib" "$task_fixture/infrastructure/manifests" \
    "$task_fixture/infrastructure/helm-values" "$task_temp/bin" "$task_temp/home/.kube"
for script in start-demo rebuild-nemesis; do cp "$TASK_ROOT/$script.sh" "$task_fixture/"; done
for script in setup-phase1 setup-phase3 setup-phase4 setup-phase5 setup-local-apps recreate-cluster verify-local-lab; do
    cp "$TASK_ROOT/infrastructure/scripts/$script.sh" "$task_fixture/infrastructure/scripts/"
done
cp "$TASK_ROOT/infrastructure/scripts/lib/common.sh" "$task_fixture/infrastructure/scripts/lib/"
mkdir -p "$task_fixture/infrastructure/helm-postrenderers/kafka-jmx"
cp "$TASK_ROOT/infrastructure/helm-postrenderers/kafka-jmx/plugin.yaml" "$TASK_ROOT/infrastructure/helm-postrenderers/kafka-jmx/render.py" "$task_fixture/infrastructure/helm-postrenderers/kafka-jmx/"
cp "$TASK_ROOT/infrastructure/manifests/nemesis-deployment.yaml" "$task_fixture/infrastructure/manifests/"
cp "$TASK_ROOT/infrastructure/manifests/target-app.yaml" "$TASK_ROOT/infrastructure/manifests/target-app-addons.yaml" "$task_fixture/infrastructure/manifests/"
# verify-local-lab.sh --check consumers reads the agents' PromQL from source (zd_agent_queries).
for agent in gaia nemesis; do
    mkdir -p "$task_fixture/agent-orchestrator/$agent"
    cp "$TASK_ROOT/agent-orchestrator/$agent/main.py" "$task_fixture/agent-orchestrator/$agent/"
done
task_versions="$task_fixture/infrastructure/helm-values/chart-versions.yaml"
cp "$TASK_ROOT/infrastructure/helm-values/chart-versions.yaml" "$task_temp/chart-versions.orig"
printf 'ORIGINAL KUBECONFIG\n' >"$task_temp/home/.kube/config"
export HOME="$task_temp/home"
export MOCK_LOG="$task_temp/commands.log" MOCK_PIDS="$task_temp/pids" MOCK_APPLIED="$task_temp/applied.yaml"
export MOCK_SCRAPES="$task_temp/scrapes"
export PATH="$task_temp/bin:$PATH"
export MOCK_SECRET=present
unset KUBECONFIG

cat >"$task_temp/bin/mock-cli" <<'MOCK'
#!/usr/bin/env bash
set -eu
tool=${0##*/}
{ printf '%s' "$tool"; printf ' <%s>' "$@"; printf '\n'; } >>"$MOCK_LOG"
flat="$*"
if [[ -n ${MOCK_FAIL:-} && "$tool $flat" == *"$MOCK_FAIL"* ]]; then
    printf 'Simulated failure: %s\n' "$MOCK_FAIL" >&2
    exit 7
fi
case $tool in
    kubectl)
        [[ ${1:-} == --context=k3d-zero-door ]] || { printf 'WRONG CONTEXT\n' >&2; exit 90; }
        case $flat in
            *config\ view*cluster.server*) printf '%s' "${MOCK_SERVER:-https://127.0.0.1:7356}" ;;
            *config\ view*clusters*) printf k3d-zero-door ;;
            *config\ view*) printf 'apiVersion: v1\ncurrent-context: k3d-zero-door\n' ;;
            # Prometheus through the API-server service proxy (verify-local-lab.sh --check telemetry).
            *get\ --raw*/-/ready*) printf 'Prometheus Server is Ready.\n' ;;
            *get\ --raw*/api/v1/targets*) printf '{"status":"success","data":{"activeTargets":[%s]}}' "${MOCK_TARGETS:-}" ;;
            *get\ --raw*/api/v1/query*kafka*) printf '{"status":"success","data":{"result":[{"metric":{},"value":[0,"1"]}]}}' ;;
            *get\ --raw*/api/v1/labels*) printf '{"status":"success","data":["__name__","code","method","protocol","service"]}' ;;
            *get\ --raw*/proxy/healthz*) printf '{"status":"ok","kafka_connected":true}' ;;
            # Agent queries: rate() has frontend data only once two scrapes differ (MOCK_CONSUMERS=stale: never).
            *get\ --raw*/api/v1/query*rate%28*)
                value=0.02
                [[ ${MOCK_CONSUMERS:-} != stale && $(sort -u "$MOCK_SCRAPES" | wc -l) -ge 2 ]] || value=0
                [[ $flat != *histogram_quantile* || $value != 0 ]] || value=NaN
                printf '{"status":"success","data":{"result":[{"metric":{"service":"frontend"},"value":[0,"%s"]}]}}' "$value" ;;
            # Frontend counters. scrape: a query sees the last scrape, then a scrape takes every request sent to
            # host :8080 so far (no series before the first request). idle: a constant 3, as after an early burst.
            *get\ --raw*/api/v1/query*traefik_service_request*)
                if [[ ${MOCK_COUNTER:-} == idle ]]; then
                    value=3
                else
                    value=$(tail -1 "$MOCK_SCRAPES")
                    if [[ $flat == *requests_total* ]]; then
                        sent=$(grep -c '^curl.*127\.0\.0\.1:8080' "$MOCK_LOG" || true)
                        (( sent == 0 )) || printf '%s\n' "$sent" >>"$MOCK_SCRAPES"
                    fi
                fi
                if [[ -n $value ]]; then
                    printf '{"status":"success","data":{"result":[{"metric":{},"value":[0,"%s"]}]}}' "$value"
                else
                    printf '{"status":"success","data":{"result":[]}}'
                fi ;;
            *get\ --raw*/api/v1/query*) printf '{"status":"success","data":{"result":[{"metric":{},"value":[0,"9"]}]}}' ;;
            *get\ deployment*go-template*) printf 'app=mock,' ;;
            *get\ pods*go-template*) printf 'docker.io/library/mock@%s\n' "${MOCK_RUNNING_ID:-sha256:built}" ;;
            *get\ pods\ -n\ target-app\ -o\ json*)
                if [[ -n ${MOCK_TARGET_PODS:-} ]]; then printf '%s\n' "$MOCK_TARGET_PODS";
                else printf '%s\n' '{"items":[]}'; fi ;;
            *get\ secret*) [[ ${MOCK_SECRET:-} != present ]] || printf 'secret/nemesis-secrets\n' ;;
            *logs\ deployment/gaia*) printf '%s\n' "${MOCK_GAIA_LOG:-INFO Gaia polling cycle complete}" ;;
            *apply\ -f*)
                file=${@: -1}
                if command -v cygpath >/dev/null; then file=$(cygpath -u "$file"); fi
                if [[ -f $file ]]; then
                    cat "$file" >>"$MOCK_APPLIED"
                    printf '\n---\n' >>"$MOCK_APPLIED"
                    # Record actual objects, not filenames: a bulk apply must fail the ordering test.
                    python_file=$file; python_log=$MOCK_LOG
                    if command -v cygpath >/dev/null; then
                        python_file=$(cygpath -m "$python_file"); python_log=$(cygpath -m "$python_log")
                    fi
                    "${PYTHON:-python}" - "$python_file" "$python_log" <<'PY'
import pathlib, sys, yaml
with pathlib.Path(sys.argv[2]).open("a", encoding="utf-8") as log:
    for doc in yaml.safe_load_all(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")):
        if not doc:
            continue
        for obj in doc.get("items", []) if doc.get("kind") == "List" else [doc]:
            if obj.get("kind") == "Deployment":
                log.write(f"mock-deployment <{obj['metadata']['name']}>\n")
PY
                fi ;;
            *auth\ can-i*)
                if [[ $flat == *'-n target-app' || ${MOCK_ALLOW_SYSTEM:-0} == 1 ]]; then printf 'yes\n'; else printf 'no\n'; exit 1; fi ;;
            *port-forward*)
                [[ ${MOCK_PORT_BUSY:-0} != 1 ]] || { printf 'address already in use\n' >&2; exit 8; }
                printf '%s\n' "$$" >>"$MOCK_PIDS"
                trap 'exit 0' TERM INT
                while :; do sleep 0.1; done ;;
        esac ;;
    k3d)
        case $flat in
            'cluster list -o json')
                if [[ ${MOCK_BAD_JSON:-0} == 1 ]]; then printf INVALID;
                elif [[ ${MOCK_CLUSTER_PRESENT:-1} == 1 ]]; then printf '[{"name":"zero-door"}]';
                else printf '[]'; fi ;;
        esac ;;
    docker)
        case $flat in
            'port k3d-zero-door-serverlb 6443/tcp') printf '0.0.0.0:7356\n' ;;
            'context show') printf '%s\n' "${MOCK_DOCKER_CONTEXT:-desktop-linux}" ;;
            image\ inspect*) printf 'sha256:built\n' ;;
            save\ *)
                # Minimal OCI export: only manifest.json, as read by zd_verify_image.
                export_dir=$(mktemp -d)
                printf '[{"Config":"blobs/sha256/%s","RepoTags":["mock"]}]' "${MOCK_CONFIG_ID:-0000}" >"$export_dir/manifest.json"
                tar -cf - -C "$export_dir" manifest.json
                rm -rf -- "$export_dir" ;;
        esac ;;
    helm)
        printf 'helm-env cache=%s\n' "${HELM_CACHE_HOME:-unset}" >>"$MOCK_LOG"
        printf 'helm-env plugins=%s\n' "${HELM_PLUGINS:-unset}" >>"$MOCK_LOG"
        if [[ $flat == *'version --template'* ]]; then printf '%s\n' "${MOCK_HELM_VERSION:-v4.2.2}"; exit 0; fi
        [[ $flat == repo* || ${1:-} == --kube-context=k3d-zero-door ]] || exit 91 ;;
    curl) printf '%s' "${MOCK_HTTP_CODE:-}" ;;
    *) exit 92 ;;
esac
MOCK
for tool in docker k3d kubectl helm curl; do cp "$task_temp/bin/mock-cli" "$task_temp/bin/$tool"; chmod +x "$task_temp/bin/$tool"; done

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1" >&2; cat "$task_temp/output" >&2 2>/dev/null || true; exit 1; }
reset_case() {
    : >"$MOCK_LOG"; : >"$MOCK_PIDS"; : >"$MOCK_APPLIED"; : >"$MOCK_SCRAPES"
    unset MOCK_FAIL MOCK_SERVER MOCK_PORT_BUSY MOCK_BAD_JSON MOCK_CLUSTER_PRESENT MOCK_ALLOW_SYSTEM MOCK_TARGETS
    unset MOCK_GAIA_LOG MOCK_HTTP_CODE MOCK_COUNTER MOCK_CONSUMERS ZD_VERIFY_POLL
    unset MOCK_TARGET_PODS
    unset MOCK_DOCKER_CONTEXT MOCK_RUNNING_ID MOCK_CONFIG_ID DOCKER_HOST ZD_DOCKER_CONTEXT MOCK_HELM_VERSION HELM_PLUGINS
    cp "$task_temp/chart-versions.orig" "$task_versions"
    export MOCK_SECRET=present
}
run_ok() { /usr/bin/timeout 15s bash "$task_fixture/$1" "${@:2}" >"$task_temp/output" 2>&1 || fail "$1 should succeed"; }
run_fail() { if /usr/bin/timeout 15s bash "$task_fixture/$1" "${@:2}" >"$task_temp/output" 2>&1; then fail "$1 should fail"; fi; }
contains() { grep -Fq -- "$1" "$2" || fail "Missing $1 in $2"; }
absent() { if grep -Fq -- "$1" "$2"; then fail "Unexpected $1 in $2"; fi; }
start_supervisor() {
    bash "$task_fixture/$1" "${@:2}" >"$task_temp/output" 2>&1 &
    task_supervisor=$!
    for (( attempt=0; attempt<60; attempt++ )); do
        if grep -Fq 'Keep this terminal open.' "$task_temp/output"; then return; fi
        kill -0 "$task_supervisor" 2>/dev/null || fail 'Supervisor exited before readiness'
        sleep 0.1
    done
    fail 'Supervisor did not become ready'
}
stop_supervisor() {
    kill -TERM "$task_supervisor"
    wait "$task_supervisor" 2>/dev/null || true
    task_supervisor=
    while IFS= read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then fail 'Owned port-forward survived cleanup'; fi
    done <"$MOCK_PIDS"
}

reset_case
for script in start-demo.sh rebuild-nemesis.sh infrastructure/scripts/{setup-phase1,setup-phase3,setup-phase4,setup-phase5,setup-local-apps,recreate-cluster,verify-local-lab}.sh; do
    run_ok "$script" --help
done
[[ ! -s $MOCK_LOG ]] || fail '--help called an external CLI'
pass 'All nine --help paths have no CLI side effects, including a checkout path with spaces'

reset_case
run_fail infrastructure/scripts/recreate-cluster.sh
run_fail infrastructure/scripts/recreate-cluster.sh --confirm-delete-other-project
[[ ! -s $MOCK_LOG ]] || fail 'Deletion guard called a CLI'
pass 'Recreate refuses deletion without the exact explicit flag'

reset_case
export MOCK_FAIL='docker build'
run_fail rebuild-nemesis.sh --no-forward
absent 'k3d <image>' "$MOCK_LOG"
absent '<rollout>' "$MOCK_LOG"
pass 'Build failure prevents import and rollout'

reset_case
export MOCK_FAIL='rollout status'
run_fail rebuild-nemesis.sh --no-forward
absent 'rollout completed' "$task_temp/output"
pass 'Rollout failure is not reported as success'

reset_case
run_ok rebuild-nemesis.sh --no-forward
contains '<nemesis:latest>' "$MOCK_LOG"
contains '<--no-cache>' "$MOCK_LOG"
contains '<-c> <zero-door>' "$MOCK_LOG"
absent 'port-forward' "$MOCK_LOG"
pass 'Rebuild uses matching image/cluster/context and supports headless operation'

reset_case
run_ok infrastructure/scripts/setup-phase3.sh
contains 'kind: Deployment' "$MOCK_APPLIED"
absent 'kind: Secret' "$MOCK_APPLIED"
pass 'Phase 3 preserves existing Nemesis Secret while applying workload manifests'

reset_case
export MOCK_SECRET=absent
run_ok infrastructure/scripts/setup-phase3.sh
contains 'kind: Secret' "$MOCK_APPLIED"
pass 'Phase 3 creates the empty Secret template only when absent'

reset_case
export MOCK_FAIL='get secret'
run_fail infrastructure/scripts/setup-phase3.sh
absent 'kind: Secret' "$MOCK_APPLIED"
pass 'Secret API errors do not become permission to overwrite a Secret'

reset_case
run_ok infrastructure/scripts/setup-phase4.sh
export MOCK_ALLOW_SYSTEM=1
run_fail infrastructure/scripts/setup-phase4.sh
pass 'RBAC expectation mismatch fails the deployment script'

reset_case
run_ok infrastructure/scripts/setup-phase1.sh --component namespaces
contains 'zero-door.yaml>' "$MOCK_LOG"
absent 'helm ' "$MOCK_LOG"
absent 'k3d <cluster> <create>' "$MOCK_LOG"
pass 'Namespaces component does not install Helm releases or recreate the cluster'

reset_case
run_ok infrastructure/scripts/recreate-cluster.sh --confirm-delete-zero-door
contains 'k3d <cluster> <delete> <zero-door>' "$MOCK_LOG"
contains '<traefik> <traefik>' "$MOCK_LOG"
absent 'ingress-nginx' "$MOCK_LOG"
absent '<delete> <other' "$MOCK_LOG"
pass 'Confirmed recreation targets only the named local cluster in the mock environment'

reset_case
export MOCK_FAIL='helm --kube-context=k3d-zero-door upgrade'
run_fail infrastructure/scripts/setup-phase1.sh
contains '<kube-prometheus-stack>' "$MOCK_LOG"
absent '<kafka>' "$MOCK_LOG"
pass 'Helm failure aborts the all-components path before later dependencies'

reset_case
export MOCK_BAD_JSON=1
run_fail infrastructure/scripts/setup-phase1.sh --component cluster
absent 'k3d <cluster> <create>' "$MOCK_LOG"
pass 'Malformed inventory stops before cluster creation'

reset_case
export MOCK_CLUSTER_PRESENT=0
run_ok infrastructure/scripts/setup-phase1.sh --component cluster
contains 'k3d <cluster> <create> <--config>' "$MOCK_LOG"
contains '<--kubeconfig-switch-context=false>' "$MOCK_LOG"
absent '<delete>' "$MOCK_LOG"
pass 'Missing cluster selects create from config, never delete, and keeps current-context'

reset_case
export MOCK_DOCKER_CONTEXT=remote-builder
run_fail infrastructure/scripts/setup-phase1.sh --component namespaces
contains "Docker context is 'remote-builder'" "$task_temp/output"
absent 'kubectl' "$MOCK_LOG"
run_fail infrastructure/scripts/setup-phase1.sh --component cluster
absent 'k3d <cluster>' "$MOCK_LOG"
export ZD_DOCKER_CONTEXT=remote-builder
run_ok infrastructure/scripts/setup-phase1.sh --component namespaces
reset_case
export DOCKER_HOST=tcp://example.invalid:2375
run_fail rebuild-nemesis.sh --no-forward
absent 'docker <build>' "$MOCK_LOG"
pass 'Unexpected Docker context or DOCKER_HOST stops before kubectl, k3d or image builds'

reset_case
run_ok infrastructure/scripts/setup-phase1.sh --component monitoring
contains '<--version> <92.10.1>' "$MOCK_LOG"
contains '<--repo> <https://prometheus-community.github.io/helm-charts>' "$MOCK_LOG"
absent 'helm <repo>' "$MOCK_LOG"
grep -F 'helm-env cache=' "$MOCK_LOG" | grep -Fq 'scratch/helm/cache' || fail 'Helm cache is not session-local'
absent 'helm-env cache=unset' "$MOCK_LOG"
run_ok infrastructure/scripts/setup-phase1.sh --component kafka
contains '<--version> <29.3.2>' "$MOCK_LOG"
pass 'Charts install from pinned versions with checkout-local Helm state and no global repo edits'

reset_case
run_ok infrastructure/scripts/setup-phase1.sh --component ingress
contains '<upgrade> <--install> <traefik> <traefik> <--repo> <https://traefik.github.io/charts> <--version> <42.0.0> <-n> <kube-system> <--skip-crds>' "$MOCK_LOG"
contains 'traefik-values.yaml>' "$MOCK_LOG"
contains '<crd> <servicemonitors.monitoring.coreos.com>' "$MOCK_LOG"
absent 'ingress-nginx' "$MOCK_LOG"
absent '<kube-prometheus-stack>' "$MOCK_LOG"
absent '<--set>' "$MOCK_LOG"
pass 'Ingress installs the pinned Traefik chart into kube-system without CRDs or ingress-nginx'

reset_case
# Rollback R1 (traefik-migration.md): free node port 80 through the guarded wrapper, never through the user's
# current kube-context or the global Helm cache, and never install or uninstall.
run_ok infrastructure/scripts/setup-phase1.sh --component ingress --ingress-cluster-ip
contains 'docker <context> <show>' "$MOCK_LOG"
contains 'helm <--kube-context=k3d-zero-door> <upgrade> <traefik> <traefik> <--repo> <https://traefik.github.io/charts> <--version> <42.0.0> <-n> <kube-system> <--skip-crds>' "$MOCK_LOG"
contains 'traefik-values.yaml> <--wait> <--timeout> <5m> <--set> <service.spec.type=ClusterIP>' "$MOCK_LOG"
absent '<--install>' "$MOCK_LOG"
absent '<uninstall>' "$MOCK_LOG"
grep -F 'helm-env cache=' "$MOCK_LOG" | grep -Fq 'scratch/helm/cache' || fail 'Rollback Helm cache is not session-local'
reset_case
export MOCK_DOCKER_CONTEXT=remote-builder
run_fail infrastructure/scripts/setup-phase1.sh --component ingress --ingress-cluster-ip
absent 'helm' "$MOCK_LOG"
reset_case
run_fail infrastructure/scripts/setup-phase1.sh --component kafka --ingress-cluster-ip
run_fail infrastructure/scripts/setup-phase1.sh --ingress-cluster-ip
[[ ! -s $MOCK_LOG ]] || fail '--ingress-cluster-ip without --component ingress reached a CLI'
pass 'Rollback R1 upgrades only release traefik to ClusterIP with the lab context, guard and local Helm cache'

reset_case
sed -i 's/^traefik:.*/traefik:/' "$task_versions"
run_fail infrastructure/scripts/setup-phase1.sh --component ingress
contains 'No pinned chart version for traefik' "$task_temp/output"
[[ ! -s $MOCK_LOG ]] || fail 'Empty ingress pin reached a CLI'
run_fail infrastructure/scripts/setup-phase1.sh
absent 'k3d' "$MOCK_LOG"
reset_case
sed -i 's/^kube-prometheus-stack:.*/kube-prometheus-stack:/' "$task_versions"
run_fail infrastructure/scripts/setup-phase1.sh --component monitoring
absent 'helm' "$MOCK_LOG"
pass 'A missing chart pin stops before preflight instead of installing the latest chart'

reset_case
export HELM_PLUGINS=/outside-checkout/plugins
run_ok infrastructure/scripts/setup-phase1.sh --component kafka
contains '<--post-renderer> <zero-door-kafka-jmx>' "$MOCK_LOG"
absent 'helm-env plugins=/outside-checkout/plugins' "$MOCK_LOG"
contains '/scratch/helm/data/plugins' "$MOCK_LOG"
export MOCK_HELM_VERSION=v3.17.0
run_ok infrastructure/scripts/setup-phase1.sh --component kafka
contains '<--post-renderer-args>' "$MOCK_LOG"
contains 'kafka-jmx/render.py>' "$MOCK_LOG"
pass 'Kafka installs always use the heap renderer for Helm 4 or Helm 3'

reset_case
export MOCK_DOCKER_CONTEXT=wrong-daemon
run_fail infrastructure/scripts/recreate-cluster.sh --confirm-delete-zero-door
absent 'docker <info>' "$MOCK_LOG"
absent 'k3d <cluster> <delete>' "$MOCK_LOG"
reset_case
export DOCKER_HOST=tcp://untrusted:2375
run_fail infrastructure/scripts/recreate-cluster.sh --confirm-delete-zero-door
absent 'docker <info>' "$MOCK_LOG"
absent 'k3d <cluster> <delete>' "$MOCK_LOG"
pass 'Recreate refuses a different Docker daemon before any destructive command'

reset_case
export MOCK_TARGET_PODS='{"items":[{"metadata":{"name":"old-target-pod","deletionTimestamp":"2026-10-18T00:00:00Z"}}]}'
run_ok infrastructure/scripts/setup-local-apps.sh --component target
for manifest in prometheus-rules target-app-ingress; do contains "$manifest.yaml>" "$MOCK_LOG"; done
absent 'target-app-monitor.yaml' "$MOCK_LOG"
contains '<delete> <servicemonitor> <frontend-monitor> <-n> <target-app> <--ignore-not-found>' "$MOCK_LOG"
absent 'target-app-hpa' "$MOCK_LOG"
contains '<deployment/paymentservice>' "$MOCK_LOG"
pass 'Baseline apps apply nine services, monitoring objects and the Traefik Ingress, without HPA'

task_host_args=("$MOCK_LOG" "$MOCK_APPLIED" "$TASK_ROOT")
if command -v cygpath >/dev/null; then
    for i in "${!task_host_args[@]}"; do task_host_args[i]=$(cygpath -m "${task_host_args[i]}"); done
fi
"${PYTHON:-python}" - "${task_host_args[@]}" <<'PY' || fail 'Target Deployment applies must wait for each rollout before starting another'
import pathlib, re, sys, yaml
log, applied, root = map(pathlib.Path, sys.argv[1:])
pending, finished, drained = None, [], True
for line in log.read_text(encoding="utf-8").splitlines():
    if line.startswith("mock-deployment <"):
        name = line.split("<")[1].rstrip(">")
        assert pending is None, f"concurrent rollout: {pending} and {name}"
        assert drained, "next Deployment started before terminating pods were gone"
        pending = name
        drained = False
    elif "<rollout> <status> <deployment/" in line:
        name = re.search(r"<deployment/([^>]+)>", line)[1]
        assert pending == name, (pending, name)
        finished.append(name)
        pending = None
    elif "<wait> <--for=delete> <pod/old-target-pod>" in line:
        drained = True
assert pending is None
assert drained
expected = [d for p in ("target-app", "target-app-addons")
            for d in yaml.safe_load_all((root / f"infrastructure/manifests/{p}.yaml").read_text(encoding="utf-8")) if d]
actual = [o for d in yaml.safe_load_all(applied.read_text(encoding="utf-8")) if d
          for o in (d.get("items", []) if d.get("kind") == "List" else [d])]
key = lambda o: (o["kind"], o["metadata"]["name"])
assert {key(o): o for o in actual} == {key(o): o for o in expected}, "split apply changed or lost source objects"
assert len(finished) == 9 and set(finished) == {o["metadata"]["name"] for o in expected if o["kind"] == "Deployment"}
assert finished.index("redis-cart") < finished.index("cartservice") < finished.index("checkoutservice") < finished.index("frontend")
PY
pass 'Target rerun applies unchanged source objects and completes each of nine rollouts before the next apply'

reset_case
export MOCK_FAIL='rollout status deployment/currencyservice'
run_fail infrastructure/scripts/setup-local-apps.sh --component target
contains 'mock-deployment <currencyservice>' "$MOCK_LOG"
absent 'mock-deployment <productcatalogservice>' "$MOCK_LOG"
pass 'A failed target rollout stops before applying the next Deployment'

reset_case
export MOCK_TARGET_PODS='{"items":[{"metadata":{"name":"old-target-pod","deletionTimestamp":"2026-10-18T00:00:00Z"}}]}'
export MOCK_FAIL='wait --for=delete'
run_fail infrastructure/scripts/setup-local-apps.sh --component target
absent 'mock-deployment <currencyservice>' "$MOCK_LOG"
pass 'A terminating target pod that does not drain stops the next Deployment apply'

reset_case
run_ok infrastructure/scripts/setup-local-apps.sh --component gaia
contains 'docker <build> <-t> <zero-door/gaia:latest>' "$MOCK_LOG"
contains '<rollout> <restart> <deployment/gaia>' "$MOCK_LOG"
contains 'runs zero-door/gaia:latest (image sha256:built' "$task_temp/output"
config_id=cac32c0796fea071563aab53d45ca5b7df1c1e0b6cab02c50f758ee177fc0f99
export MOCK_RUNNING_ID="sha256:$config_id" MOCK_CONFIG_ID=$config_id
run_ok infrastructure/scripts/setup-local-apps.sh --component gaia
contains "config sha256:$config_id" "$task_temp/output"
unset MOCK_CONFIG_ID
export MOCK_RUNNING_ID=sha256:stale
run_fail infrastructure/scripts/setup-local-apps.sh --component gaia
contains 'expected sha256:built' "$task_temp/output"
run_fail infrastructure/scripts/setup-phase4.sh
pass 'A restart that leaves a stale image ID is reported as a failure'

reset_case
export MOCK_SERVER=https://host.docker.internal:7356
run_ok infrastructure/scripts/setup-phase1.sh --component cluster
contains '<--server=https://127.0.0.1:7356>' "$MOCK_LOG"
contains 'ORIGINAL KUBECONFIG' "$HOME/.kube/config"
compgen -G "$HOME/.kube/config.zero-door-backup-*" >/dev/null || fail 'Missing kubeconfig backup'
pass 'Localhost repair is tested with TLS and backs up the selected default kubeconfig'

reset_case
export MOCK_SERVER=https://host.docker.internal:7356 KUBECONFIG="$HOME/.kube/config"
run_fail infrastructure/scripts/setup-phase1.sh --component cluster
absent '<set-cluster>' "$MOCK_LOG"
unset KUBECONFIG
pass 'Custom KUBECONFIG is not silently rewritten'

reset_case
sleep 30 &
task_unrelated=$!
start_supervisor start-demo.sh --nemesis-only
stop_supervisor
kill -0 "$task_unrelated" || fail 'Unrelated process was stopped'
kill "$task_unrelated"; wait "$task_unrelated" 2>/dev/null || true; task_unrelated=
pass 'Supervisor cleans up its own tunnel on TERM and preserves an unrelated process'

reset_case
export MOCK_PORT_BUSY=1
run_fail start-demo.sh --nemesis-only
contains 'address already in use' "$task_temp/output"
pass 'Port conflict fails without killing the current port owner'

reset_case
start_supervisor infrastructure/scripts/setup-phase5.sh
contains 'No experiment was triggered.' "$task_temp/output"
absent '<kafka>' "$MOCK_LOG"
[[ ! -d $task_fixture/.venv-experiments ]] || fail 'Default created a venv'
stop_supervisor
pass 'Phase 5 default only checks HTTP/forwards; no install or smoke run'

reset_case
run_fail infrastructure/scripts/setup-phase5.sh --run-smoke --smoke-runs 0
[[ ! -s $MOCK_LOG ]] || fail 'Invalid smoke run count reached a CLI'
pass 'Invalid experiment arguments fail before touching the lab'

# Execute the Python wrapper against a harmless fixture instead of a real chaos runner.
cat >"$task_fixture/infrastructure/scripts/experiment_runner.py" <<'PY'
import os, pathlib, sys
RESULTS_DIR = pathlib.Path("SHOULD_NOT_BE_USED")
def main():
    assert sys.argv[1:] == ["--scenario", "E1", "--mode", "AUTO", "--runs", "1", "--skip-steady-state"]
    assert "k3d-zero-door" in pathlib.Path(os.environ["KUBECONFIG"]).read_text()
    assert "scratch" in str(RESULTS_DIR)
    RESULTS_DIR.mkdir(parents=True)
    (RESULTS_DIR / "fixture-only.csv").write_text("fixture_not_research\n")
PY
reset_case
run_ok infrastructure/scripts/setup-phase5.sh --run-smoke --smoke-runs 1
contains '<svc/kafka>' "$MOCK_LOG"
[[ -n $(find "$task_fixture/scratch/experiments" -name fixture-only.csv -print) ]] || fail 'Smoke output was not isolated'
while IFS= read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then fail 'Smoke left a forward running'; fi
done <"$MOCK_PIDS"
pass 'Explicit smoke passes the selected context, isolates CSV output and cleans up its forwards'

# Exit code of a fixture script, without letting set -e stop the suite. case_timeout: slower cases (default 15s).
run_code() { /usr/bin/timeout "${case_timeout:-15s}" bash "$task_fixture/$1" "${@:2}" >"$task_temp/output" 2>&1 && code=0 || code=$?; }
target() { printf '{"health":"%s","labels":{"job":"%s","namespace":"%s"},"lastError":"%s"}' "$@"; }
frontend_404="$(target down frontend target-app 'server returned HTTP status 404 Not Found'),$(target down frontend-external target-app 'server returned HTTP status 404 Not Found')"
reset_case
export MOCK_TARGETS="$(target up kafka-jmx-metrics zero-door ''),$frontend_404"
run_code infrastructure/scripts/verify-local-lab.sh --check telemetry
[[ $code == 1 ]] || fail "obsolete frontend 404 targets should exit 1, got $code"
contains 'FAIL scrape target target-app/frontend down' "$task_temp/output"
contains '2 failure(s).' "$task_temp/output"
export MOCK_TARGETS="$frontend_404,$(target down cartservice target-app 'connection refused')"
run_code infrastructure/scripts/verify-local-lab.sh --check telemetry
[[ $code == 1 ]] || fail "a new down target next to the known ones should exit 1, got $code"
contains 'FAIL scrape target target-app/cartservice down: connection refused' "$task_temp/output"
export MOCK_TARGETS="$(target down frontend target-app 'context deadline exceeded')"
run_code infrastructure/scripts/verify-local-lab.sh --check telemetry
[[ $code == 1 ]] || fail "frontend failing with another error should exit 1, got $code"
export MOCK_TARGETS="$(target up frontend target-app '')"
run_code infrastructure/scripts/verify-local-lab.sh --check telemetry
[[ $code == 0 ]] || fail "no down target should exit 0, got $code"
pass 'All down targets fail, including legacy frontend 404; healthy telemetry exits 0'

reset_case
run_code infrastructure/scripts/verify-local-lab.sh --check agents
[[ $code == 0 ]] || fail "a readable Gaia log without query errors should exit 0, got $code"
contains 'PASS Gaia log read; no Prometheus query error' "$task_temp/output"
export MOCK_GAIA_LOG='ERROR Error querying Prometheus: 400 bad_data'
run_code infrastructure/scripts/verify-local-lab.sh --check agents
[[ $code == 1 ]] || fail "a Gaia query error should exit 1, got $code"
contains 'FAIL Gaia Prometheus query errors: ERROR Error querying Prometheus: 400 bad_data' "$task_temp/output"
unset MOCK_GAIA_LOG
export MOCK_FAIL='logs deployment/gaia'
run_code infrastructure/scripts/verify-local-lab.sh --check agents
[[ $code == 1 ]] || fail "a Gaia log that cannot be read should exit 1, got $code"
contains 'FAIL cannot read the Gaia log, query errors unknown: Simulated failure' "$task_temp/output"
absent 'PASS Gaia log' "$task_temp/output"
pass 'Gaia log check: clean log passes, query errors fail, and a log that cannot be read fails instead of passing'

# Order of host :8080 requests (C) and frontend counter reads (Q) in the mock log.
sequence() { awk '/^curl.*127\.0\.0\.1:8080/ { printf "C" } /^kubectl.*traefik_service_requests_total/ && !/rate%28/ { printf "Q" }' "$MOCK_LOG"; }
reset_case
# Cold start: the series appears only with the first scrape after the first requests, so a single burst gives one
# sample (rate 0, P99 NaN). The check must send more requests after that scrape and wait for the next one.
# These cases get 90s: up to 4 rounds of mocked Prometheus polls, each parsed by a new Python process.
export MOCK_HTTP_CODE=200 MOCK_COUNTER=scrape ZD_VERIFY_POLL=0
case_timeout=90s run_code infrastructure/scripts/verify-local-lab.sh --check consumers
[[ $code == 0 ]] || fail "two confirmed scrapes with fresh requests should exit 0, got $code"
contains 'PASS frontend requests/histogram count across 2 confirmed scrapes (6 requests): absent absent -> 3 3 -> 6 6' "$task_temp/output"
contains 'PASS Gaia P99 latency (1m) by service: frontend=0.02' "$task_temp/output"
contains 'PASS Nemesis http_rps (2m): 0.02' "$task_temp/output"
[[ $(sequence) == QCCCQQCCCQQ ]] || fail "requests must follow a confirmed scrape: $(sequence)"
reset_case
# Idle: the counter never moves after the requests (e.g. the burst ended before the series' first scrape).
export MOCK_HTTP_CODE=200 MOCK_COUNTER=idle ZD_VERIFY_POLL=0
case_timeout=90s run_code infrastructure/scripts/verify-local-lab.sh --check consumers
[[ $code == 1 ]] || fail "counters that never grow should exit 1, got $code"
contains 'FAIL frontend counters did not grow across two confirmed scrapes (3 requests): 3 3' "$task_temp/output"
contains 'FAIL agent queries not evaluated' "$task_temp/output"
absent 'PASS Nemesis http_rps' "$task_temp/output"
reset_case
# Counters grow but the queries never see frontend data: bounded at 4 rounds of 3 requests, then FAIL.
export MOCK_HTTP_CODE=200 MOCK_COUNTER=scrape MOCK_CONSUMERS=stale ZD_VERIFY_POLL=0
case_timeout=90s run_code infrastructure/scripts/verify-local-lab.sh --check consumers
[[ $code == 1 ]] || fail "stale agent queries should exit 1, got $code"
contains 'across 4 confirmed scrapes (12 requests)' "$task_temp/output"
contains "FAIL agent queries lack frontend data after the confirmed scrapes: denominator 'frontend=0', latency 'frontend=NaN', Nemesis http_rps '0'" "$task_temp/output"
[[ $(grep -c '^curl.*127\.0\.0\.1:8080' "$MOCK_LOG") == 12 ]] || fail 'consumer traffic exceeded 12 requests'
reset_case
export MOCK_HTTP_CODE=502 MOCK_COUNTER=scrape ZD_VERIFY_POLL=0
case_timeout=90s run_code infrastructure/scripts/verify-local-lab.sh --check consumers
[[ $code == 1 ]] || fail "a non-200 healthy request should exit 1, got $code"
contains 'FAIL healthy request GET http://127.0.0.1:8080/_healthz answered HTTP 502' "$task_temp/output"
pass 'Consumer gate: fresh requests across two confirmed scrapes; idle, stale or refused traffic never passes; at most 12 requests'

reset_case
# Label contract (TFM-01): without honorLabels the Operator's target label service=traefik-metrics replaces the
# backend label every rule and agent query selects on. tests/shell/test-local-restore.sh checks the rendered chart.
traefik_values="$TASK_ROOT/infrastructure/helm-values/traefik-values.yaml"
# Python is a native Windows program under Git Bash: pass a host path whatever MSYS path conversion is set to.
if command -v cygpath >/dev/null; then traefik_values=$(cygpath -m "$traefik_values"); fi
"${PYTHON:-python}" - "$traefik_values" <<'PY' || fail 'traefik-values.yaml must set metrics.prometheus.serviceMonitor.honorLabels: true'
import sys, yaml
monitor = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["metrics"]["prometheus"]["serviceMonitor"]
sys.exit(0 if monitor.get("enabled") is True and monitor.get("honorLabels") is True else 1)
PY
pass 'Traefik ServiceMonitor values keep the backend service label (honorLabels: true)'
printf 'All offline Bash behavioral checks passed. No real lab commands were used.\n'
