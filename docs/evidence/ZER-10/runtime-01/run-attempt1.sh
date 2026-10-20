#!/usr/bin/env bash
# One approved lab run. Uses no paid API and never deletes anything outside its new namespace.
set -euo pipefail
export MSYS_NO_PATHCONV=1
ctx=k3d-zero-door
evidence=docs/evidence/ZER-10/runtime-01
ns="zer10-acceptance-$(date +%H%M%S)"
image=$(cat "$evidence/image-tag.txt")
kc() { kubectl --context "$ctx" --request-timeout=10s "$@"; }
[[ $(kubectl config current-context) == "$ctx" ]]
kc get deploy frontend checkoutservice -n target-app -o json > "$evidence/deployments-before.json"
read -r frontend_before checkout_before frontend_uid checkout_uid < <(python -B -c '
import json
d={x["metadata"]["name"]:x for x in json.load(open("docs/evidence/ZER-10/runtime-01/deployments-before.json"))["items"]}
print(d["frontend"]["spec"]["replicas"],d["checkoutservice"]["spec"]["replicas"],d["frontend"]["metadata"]["uid"],d["checkoutservice"]["metadata"]["uid"])
')
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
    kc logs -n "$ns" probe > "$evidence/pod.log" 2>&1
    mkdir -p "$evidence/raw"
    kc exec -n "$ns" probe -- tar -C /tmp/zer10 -cf - . | tar -C "$evidence/raw" -xf - || result=1
    if [[ $finished == 1 && $result == 0 ]]; then
      kc delete namespace "$ns" --wait=true --timeout=60s > "$evidence/cleanup.txt" 2>&1 || result=1
    else
      printf 'Evidence retained; namespace %s preserved for diagnosis. No automatic retry.\n' "$ns" >> "$evidence/cleanup.txt"
    fi
  fi
  printf '{"namespace":"%s","wall_s":%s,"exit_code":%s,"finished":%s}\n' "$ns" "$((SECONDS-started))" "$result" "$finished" > "$evidence/host-receipt.json"
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
kc create namespace "$ns" > "$evidence/namespace.txt"
created=1
cat > "$evidence/pod.yaml" <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: probe
  namespace: $ns
  labels:
    app: zer10-acceptance
spec:
  nodeName: k3d-zero-door-server-0
  automountServiceAccountToken: false
  restartPolicy: Never
  activeDeadlineSeconds: 900
  securityContext:
    runAsNonRoot: true
    runAsUser: 65532
    runAsGroup: 65532
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: probe
    image: $image
    imagePullPolicy: Never
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
    readinessProbe:
      exec:
        command: [python, -c, "import socket; socket.create_connection(('127.0.0.1', 9133), 1).close()"]
      periodSeconds: 2
EOF
kc create -f "$evidence/pod.yaml"
kc wait --for=condition=Ready -n "$ns" pod/probe --timeout=90s
origin="http://$frontend_ip:80"
command_in_pod "{\"action\":\"observe\",\"origin\":\"$origin\"}" > "$evidence/observation.response.json"
phase boutique-healthy "$origin"
check_time
kc scale deploy checkoutservice -n target-app --current-replicas="$checkout_before" --replicas=0
checkout_changed=1
kc wait --for=delete pod -n target-app -l app=checkoutservice --timeout=60s
phase checkout-unavailable "$origin"
restore_one checkoutservice "$checkout_before" "$checkout_uid" >> "$evidence/restoration.txt" 2>&1
checkout_changed=0
phase checkout-restored "$origin"
check_time
kc scale deploy frontend -n target-app --current-replicas="$frontend_before" --replicas=0
frontend_changed=1
kc wait --for=delete pod -n target-app -l app=frontend --timeout=60s
phase frontend-unavailable "$origin"
restore_one frontend "$frontend_before" "$frontend_uid" >> "$evidence/restoration.txt" 2>&1
frontend_changed=0
phase frontend-restored "$origin"
phase fixture-healthy http://127.0.0.1:9132
phase fixture-locked http://127.0.0.1:9132
phase fixture-restored http://127.0.0.1:9132
command_in_pod '{"action":"finish"}' > "$evidence/finish.response.json"
finished=1
