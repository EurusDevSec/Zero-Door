#!/usr/bin/env bash
set -Eeuo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' PYTHONUTF8=1
cd /r/_Projects/Eurus_Workspace/zero_door
D=scratch/zer13/codex-completion
O=docs/evidence/ZER-41/runtime-02
PY=scratch/zer12/production-nemesis/Scripts/python.exe
K='kubectl --context k3d-zero-door --request-timeout=10s'
START=$SECONDS
END=$((START+2100))
LIMIT=$((START+90))
PAUSED=0
RESTARTED=0
printf '%s\n' "start_utc=$(date -u +%FT%TZ)" > "$O/timing.txt"
date +%s > "$D/turn-start-epoch.txt"
timed() { local n=$((LIMIT-SECONDS)); if (( n<=0 )); then echo TIME_CAP >&2; return 124; fi; timeout --signal=TERM --kill-after=5 "$n" "$@"; }
restore() {
 local code=$?
 trap - EXIT INT TERM
 set +e
 LIMIT=$END
 printf '\nRESTORE elapsed=%ss prior_exit=%s\n' "$((SECONDS-START))" "$code"
 local clean=UNRESOLVED restore_state=NOT_NEEDED
 # Redundant owner/UID-checked namespace cleanup if a child was interrupted.
 timed $K get namespace zd-sqli-lab --ignore-not-found -o json > "$O/raw/namespace-restore.json"
 if [[ $? == 0 ]]; then
  if [[ -s "$O/raw/namespace-restore.json" ]]; then
   if "$PY" -B "$D/runtime_evidence.py" namespace "$O/raw/namespace-restore.json"; then
    timed $K delete --raw /api/v1/namespaces/zd-sqli-lab -f "$D/delete-options.json" > "$O/raw/extra-delete.json"
    timed $K wait --for=delete namespace/zd-sqli-lab --timeout=120s
   fi
  fi
  timed $K get namespace zd-sqli-lab --ignore-not-found -o name > "$O/raw/namespace-final.txt"
  if [[ $? == 0 && ! -s "$O/raw/namespace-final.txt" ]]; then clean=CLEAN; fi
 fi
 if (( PAUSED )); then
  while IFS=$'\t' read -r name replicas; do
   timed $K -n zero-door scale deployment/"$name" --replicas="$replicas"
  done < "$O/raw/agent-replicas.tsv"
  while IFS=$'\t' read -r name replicas; do
   timed $K -n zero-door rollout status deployment/"$name" --timeout=120s
  done < "$O/raw/agent-replicas.tsv"
 fi
 timed $K get deployment,statefulset -A -o json > "$O/raw/workloads-final.json"
 timed $K get pvc -A -o json > "$O/raw/pvc-final.json"
 timed $K get pods -A -o json > "$O/raw/pods-final.json"
 if "$PY" -B "$D/recovery_evidence.py" final; then restore_state=RESTORE_PASS; else restore_state=UNRESOLVED; code=1; fi
 [[ "$clean" == CLEAN ]] || code=1
 printf '{"exit_code":%s,"server_restarts":%s,"namespace":"%s","restore":"%s","elapsed_seconds":%s}\n' "$code" "$RESTARTED" "$clean" "$restore_state" "$((SECONDS-START))" > "$O/recovery-process.json"
 printf 'end_utc=%s\n' "$(date -u +%FT%TZ)" >> "$O/timing.txt"
 cat "$O/recovery-process.json"
 exit "$code"
}
trap restore EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
timed $K get namespace zd-sqli-lab --ignore-not-found -o name > "$O/raw/namespace-before.txt"
[[ ! -s "$O/raw/namespace-before.txt" ]] || { echo EXISTING_NAMESPACE; exit 1; }
timed $K get deployment,statefulset -A -o json > "$O/raw/workloads-before.json"
timed $K get pvc -A -o json > "$O/raw/pvc-before.json"
timed $K get pods -A -o json > "$O/raw/pods-before.json"
timed docker inspect k3d-zero-door-server-0 --format '{{json .Mounts}}' > "$O/raw/server-mounts-before.json"
"$PY" -B "$D/recovery_evidence.py" baseline
PAUSED=1
while IFS=$'\t' read -r name replicas; do timed $K -n zero-door scale deployment/"$name" --replicas=0; done < "$O/raw/agent-replicas.tsv"
timed $K -n zero-door rollout status deployment/gaia --timeout=60s
timed $K -n zero-door rollout status deployment/hephaestus --timeout=60s
LIMIT=$((START+390))
RESTARTED=1
timed docker restart --time 30 k3d-zero-door-server-0 > "$O/raw/server-restart.txt"
api_ready=0
for i in $(seq 1 40); do
 if timed kubectl --context k3d-zero-door --request-timeout=5s get --raw /readyz > "$O/raw/api-ready.txt" 2> "$O/raw/api-ready.err"; then api_ready=1; break; fi
 sleep 2
done
[[ $api_ready == 1 ]] || { echo API_NOT_READY; exit 1; }
timed $K wait --for=condition=Ready node/k3d-zero-door-server-0 --timeout=100s
timed $K -n target-app rollout status deployment/frontend --timeout=100s
timed $K -n target-app rollout status deployment/checkoutservice --timeout=100s
timed $K -n monitoring rollout status deployment/elasticsearch --timeout=100s
timed $K get pvc -A -o json > "$O/raw/pvc-after-restart.json"
"$PY" -B "$D/recovery_evidence.py" pvc
printf 'SERVER_RECOVERY_READY elapsed=%ss; starting gated private retest\n' "$((SECONDS-START))"
LIMIT=$((START+1800))
timed bash "$D/runtime-recovered.sh" > "$O/attempt-01/runner.log" 2>&1
printf 'Gated private retest passed; restore agents and verify all preserved state.\n'
