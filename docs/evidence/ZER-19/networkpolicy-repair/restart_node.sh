#!/usr/bin/env bash
# Restart exactly one k3d node container, wait (max 300s) until netpol has synced
# and the node's pods are back, then take a snapshot. Usage: restart_node.sh agent|server <label>
set -u
n="$1"; label="$2"; S="$(dirname "$0")"
D="docker --context desktop-linux"
K="kubectl --context k3d-zero-door --request-timeout=8s"
c="k3d-zero-door-$n-0"
log="$S/netpol/$label.log"; mkdir -p "$S/netpol"
echo "restart $c at $(date -u +%FT%TZ)" | tee "$log"
$D restart "$c" >>"$log" 2>&1 || { echo "RESTART_FAILED" | tee -a "$log"; exit 1; }
since="$($D inspect -f '{{.State.StartedAt}}' "$c")"
echo "started_at $since ip $($D inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$c")" | tee -a "$log"
deadline=$((SECONDS + 300)); state=TIMEOUT
while [ $SECONDS -lt $deadline ]; do
  if $D logs --since "$since" "$c" 2>&1 | grep -q 'network policy controller full sync goroutine' \
     && [ "$($K get node "$c" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)" = True ] \
     && ! $K get pods -A --field-selector "spec.nodeName=$c" --no-headers 2>/dev/null \
          | awk '{split($3,a,"/"); if (($4!="Running" && $4!="Completed") || ($4=="Running" && a[1]!=a[2])) bad=1} END{exit !bad}'; then
    state=READY; break
  fi
  sleep 5
done
echo "wait_state $state after $SECONDS s at $(date -u +%FT%TZ)" | tee -a "$log"
# one extra full-sync interval margin is not needed: chains are created on pod events; snapshot now
bash "$S/snap.sh" "$label" | tee -a "$log"
