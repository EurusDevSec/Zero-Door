#!/usr/bin/env bash
# One approved lab run. Uses no paid API and never deletes anything outside its new namespace.
set -euo pipefail
export MSYS_NO_PATHCONV=1
ctx=k3d-zero-door
evidence=docs/evidence/ZER-10/runtime-01/attempt-03
ns="zer10-acceptance-225527"
image=$(cat "$evidence/image-tag.txt")
kc() { kubectl --context "$ctx" --request-timeout=10s "$@"; }
[[ $(kubectl config current-context) == "$ctx" ]]
kc get deploy frontend checkoutservice -n target-app -o json > "$evidence/deployments-complete-before.json"
read -r frontend_before checkout_before frontend_uid checkout_uid < <(python -B -c '
import json,sys
d={x["metadata"]["name"]:x for x in json.load(open(sys.argv[1]))["items"]}
print(d["frontend"]["spec"]["replicas"],d["checkoutservice"]["spec"]["replicas"],d["frontend"]["metadata"]["uid"],d["checkoutservice"]["metadata"]["uid"])
' "$evidence/deployments-complete-before.json" | tr -d '\r')
[[ $frontend_before -gt 0 && $checkout_before -gt 0 ]]
frontend_ip=$(kc get service frontend -n target-app -o jsonpath='{.spec.clusterIP}')
[[ $frontend_ip == 10.* ]]
frontend_changed=0
checkout_changed=0
created=0
finished=0
started=$SECONDS
restore_one() {
  local deployment=$1 replicas=$2 uid=$3
  [[ $(kc get deploy "$deployment" -n target-app -o jsonpath='{.metadata.uid}') == "$uid" ]] || return 1
  kc scale deploy "$deployment" -n target-app --current-replicas=0 --replicas="$replicas"
  kc rollout status deploy/"$deployment" -n target-app --timeout=90s
}
cleanup() {
  local result=$?
  trap - EXIT TERM INT
  set +e
  if [[ $frontend_changed == 1 ]]; then
    restore_one frontend "$frontend_before" "$frontend_uid" >> "$evidence/restoration.txt" 2>&1 || result=1
  fi
  if [[ $checkout_changed == 1 ]]; then
    restore_one checkoutservice "$checkout_before" "$checkout_uid" >> "$evidence/restoration.txt" 2>&1 || result=1
  fi
  kc get deploy frontend checkoutservice -n target-app -o json > "$evidence/deployments-after.json"
  if [[ $created == 1 ]]; then
    kc logs -n "$ns" probe > "$evidence/pod-final.log" 2>&1
    mkdir -p "$evidence/raw-final"
    kc exec -n "$ns" probe -- tar -C /tmp/zer10 -cf - . | tar -C "$evidence/raw-final" -xf - || result=1
    if [[ $finished == 1 && $result == 0 ]]; then
      kc delete namespace "$ns" --wait=true --timeout=60s > "$evidence/cleanup-final.txt" 2>&1 || result=1
    else
      printf 'Evidence retained; namespace %s preserved for diagnosis. No automatic retry.\n' "$ns" >> "$evidence/cleanup-final.txt"
    fi
  fi
  printf '{"namespace":"%s","wall_s":%s,"exit_code":%s,"finished":%s}\n' "$ns" "$((SECONDS-started))" "$result" "$finished" > "$evidence/host-receipt-final.json"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
check_time() { [[ $((SECONDS-started)) -lt 780 ]] || { echo 'Lab time budget exhausted' >&2; return 1; }; }
command_in_pod() {
  check_time
  kc exec -n "$ns" probe -- python -B /app/live/acceptance.py "$1"
}
phase() {
  local name=$1 origin=$2
  command_in_pod "{\"action\":\"phase\",\"name\":\"$name\",\"origin\":\"$origin\"}" > "$evidence/$name.response.json"
}

[[ $(kc get pod -n "$ns" probe -o jsonpath='{.spec.containers[0].image}') == "$image" ]]
created=1
origin="http://$frontend_ip:80"
phase frontend-restored "$origin"
phase fixture-healthy http://127.0.0.1:9132
phase fixture-locked http://127.0.0.1:9132
phase fixture-restored http://127.0.0.1:9132
command_in_pod '{"action":"finish"}' > "$evidence/finish.response.json"
finished=1
