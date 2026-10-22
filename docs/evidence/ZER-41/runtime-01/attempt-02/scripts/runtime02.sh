#!/usr/bin/env bash
set -Eeuo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' PYTHONUTF8=1
cd /r/_Projects/Eurus_Workspace/zero_door
D=scratch/zer13/codex-completion
O=docs/evidence/ZER-41/runtime-01/attempt-02
PY=scratch/zer12/production-nemesis/Scripts/python.exe
K='kubectl --context k3d-zero-door --request-timeout=15s'
RUN=$(cat "$D/run-id.txt")
NS=zd-sqli-lab
TURN_EPOCH=$(cat "$D/turn-start-epoch.txt")
START=$((SECONDS - $(date +%s) + TURN_EPOCH))
END=$((START+1800))
WORK_END=$((START+1380))
PHASE_END=$((START+180))
CREATING=0
PROXY_LOG_PID=
FIXTURE_LOG_PID=
ES_PID=
printf '%s\n' "start_utc=$(date -u +%FT%TZ)" "run=$RUN" > "$O/timing.txt"
phase() { printf '\nPHASE %s elapsed=%ss cap=%ss\n' "$1" "$((SECONDS-START))" "$2"; PHASE_END=$((SECONDS+$2)); }
timed() {
 local remaining=$((PHASE_END-SECONDS))
 local work=$((WORK_END-SECONDS))
 if (( work < remaining )); then remaining=$work; fi
 if (( remaining <= 0 )); then printf 'TIME_CAP\n' >&2; return 124; fi
 timeout --signal=TERM --kill-after=5 "$remaining" "$@"
}
stop_owned() { local pid=$1; if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi; }
cleanup() {
 local code=$?
 trap - EXIT INT TERM
 set +e
 WORK_END=$END; PHASE_END=$END
 printf '\nCLEANUP elapsed=%ss exit=%s\n' "$((SECONDS-START))" "$code"
 local clean=NOT_CREATED
 if (( CREATING )); then
  timed $K get namespace "$NS" -o json > "$O/raw/namespace-before-delete.json"
  if [[ $? == 0 ]] && "$PY" -B "$D/runtime_evidence.py" namespace "$O/raw/namespace-before-delete.json"; then
   timed $K -n "$NS" get pods -o json > "$O/raw/pods-final.json"
   timed $K delete --raw "/api/v1/namespaces/$NS" -f "$D/delete-options.json" > "$O/raw/delete-result.json"
   local deleted=$?
   timed $K wait --for=delete namespace/"$NS" --timeout=180s > "$O/raw/cleanup-wait.txt" 2>&1
   local waited=$?
   timed $K get namespace "$NS" --ignore-not-found -o name > "$O/raw/namespace-after.txt"
   if [[ $deleted == 0 && $waited == 0 && $? == 0 && ! -s "$O/raw/namespace-after.txt" ]]; then clean=CLEAN; else clean=UNRESOLVED; code=1; fi
  else
   clean=UNRESOLVED; code=1
  fi
 fi
 stop_owned "$FIXTURE_LOG_PID"
 stop_owned "$PROXY_LOG_PID"
 stop_owned "$ES_PID"
 printf '{"run":"%s","cleanup":"%s","exit_code":%s,"elapsed_seconds":%s}\n' "$RUN" "$clean" "$code" "$((SECONDS-START))" > "$O/receipt-process.json"
 printf 'end_utc=%s\n' "$(date -u +%FT%TZ)" >> "$O/timing.txt"
 cat "$O/receipt-process.json"
 exit "$code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
phase P0 180
timed $K cluster-info > "$O/raw/cluster-info.txt"
timed $K get namespace "$NS" --ignore-not-found -o name > "$O/raw/namespace-preflight.txt"
[[ ! -s "$O/raw/namespace-preflight.txt" ]] || { echo UNOWNED_NAMESPACE; exit 1; }
timed $K get node k3d-zero-door-server-0 -o json > "$O/raw/node.json"
timed $K -n kube-system get pods -l app.kubernetes.io/name=traefik -o json > "$O/raw/shared-traefik-before.json"
timed docker port k3d-zero-door-serverlb > "$O/raw/host-binding.txt"
"$PY" -B "$D/runtime_evidence.py" prepare
printf "Reuse the one already-built/imported fixture image; no second image build.\n"
phase P2_SAFE_ROLLOUT 180
CREATING=1
timed $K create -f "$D/namespace.json" > "$O/raw/create-namespace.txt"
timed $K get namespace "$NS" -o json > "$O/raw/namespace-created.json"
"$PY" -B "$D/runtime_evidence.py" namespace "$O/raw/namespace-created.json"
timed $K apply -f "$D/bootstrap.yaml" > "$O/raw/apply.txt"
timed $K -n "$NS" rollout status deployment/zer41-private-ingress --timeout=120s
timed $K -n "$NS" wait --for=condition=Ready pod/zer41-source-a pod/zer41-source-b --timeout=60s
timed $K -n "$NS" get pods -o json > "$O/raw/pods-bootstrap.json"
"$PY" -B "$D/runtime_evidence.py" proxy "$O/raw/pods-bootstrap.json" > "$O/raw/trusted-proxy-ip.txt"
timed $K -n "$NS" patch configmap sqli-fixture-config --type=merge --patch-file "$D/trust-patch.json"
timed $K create -f "$D/fixture-deployment.json"
timed $K -n "$NS" rollout status deployment/sqli-fixture --timeout=100s
kubectl --context k3d-zero-door --request-timeout=0 -n "$NS" logs -f -l app=zer41-private-ingress --prefix=false --timestamps=false > "$O/raw/proxy.jsonl" 2> "$O/raw/proxy-stream.err" & PROXY_LOG_PID=$!
kubectl --context k3d-zero-door --request-timeout=0 -n "$NS" logs -f -l app=sqli-fixture --prefix=false --timestamps=false > "$O/raw/fixture-safe.jsonl" 2> "$O/raw/fixture-safe-stream.err" & FIXTURE_LOG_PID=$!
phase P3_SAFE 240
timed $K -n "$NS" get service,endpoints -o yaml > "$O/raw/services-safe.yaml"
timed $K -n "$NS" get pods -o json > "$O/raw/pods-safe.json"
for source in a b; do
 timed $K -n "$NS" exec --request-timeout=90s -i "zer41-source-$source" -- /usr/bin/python3 - safe "$RUN" "$source" < "$D/runtime_probe.py" > "$O/raw/window-safe-$source.jsonl" 2> "$O/raw/window-safe-$source.err"
 timed $K -n "$NS" exec "zer41-source-$source" -- /usr/bin/python3 -c 'import socket,json; s=socket.socket(); s.settimeout(2)
try:
 s.connect(("sqli-fixture.zd-sqli-lab.svc.cluster.local",9140)); print("DIRECT_ACCESS_NOT_BLOCKED"); raise SystemExit(1)
except (socket.timeout,ConnectionRefusedError): print(json.dumps({"direct_fixture":"DENIED","scope":"source-to-service"}))
finally:s.close()' > "$O/raw/direct-deny-$source.json"
done
sleep 1
"$PY" -B "$D/runtime_evidence.py" reconcile safe
phase P4_VULNERABLE_ROLLOUT 120
printf '{"data":{"ZD_SQLI_PROFILE":"vulnerable"}}' > "$D/profile-patch.json"
timed $K -n "$NS" patch configmap sqli-fixture-config --type=merge --patch-file "$D/profile-patch.json"
timed $K -n "$NS" rollout restart deployment/sqli-fixture
timed $K -n "$NS" rollout status deployment/sqli-fixture --timeout=90s
stop_owned "$FIXTURE_LOG_PID"; FIXTURE_LOG_PID=
kubectl --context k3d-zero-door --request-timeout=0 -n "$NS" logs -f -l app=sqli-fixture --prefix=false --timestamps=false > "$O/raw/fixture-vulnerable.jsonl" 2> "$O/raw/fixture-vulnerable-stream.err" & FIXTURE_LOG_PID=$!
phase P5_VULNERABLE 240
timed $K -n "$NS" get pods -o json > "$O/raw/pods-vulnerable.json"
for source in a b; do
 timed $K -n "$NS" exec --request-timeout=90s -i "zer41-source-$source" -- /usr/bin/python3 - vulnerable "$RUN" "$source" < "$D/runtime_probe.py" > "$O/raw/window-vulnerable-$source.jsonl" 2> "$O/raw/window-vulnerable-$source.err"
done
sleep 1
"$PY" -B "$D/runtime_evidence.py" reconcile vulnerable
kubectl --context k3d-zero-door --request-timeout=0 -n monitoring port-forward --address 127.0.0.1 service/elasticsearch 19241:9200 > "$O/raw/es-forward.log" 2>&1 & ES_PID=$!
sleep 2
timed "$PY" -B "$D/runtime_es.py"
timed $K -n "$NS" get all,networkpolicy,configmap -o yaml > "$O/raw/final-resources.yaml"
printf 'All requested private runtime cases completed; cleaning up.\n'
