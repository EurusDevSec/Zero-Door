#!/usr/bin/env bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' PYTHONUTF8=1
cd /r/_Projects/Eurus_Workspace/zero_door
O=docs/evidence/ZER-41/runtime-02
K='kubectl --context k3d-zero-door --request-timeout=10s'
while IFS=$'\t' read -r name replicas; do
 timeout 30 $K -n zero-door scale deployment/"$name" --replicas="$replicas"
done < "$O/raw/agent-replicas-lf.tsv"
while IFS=$'\t' read -r name replicas; do
 timeout 130 $K -n zero-door rollout status deployment/"$name" --timeout=120s
done < "$O/raw/agent-replicas-lf.tsv"
$K get deployment,statefulset -A -o json > "$O/raw/workloads-final.json"
$K get pvc -A -o json > "$O/raw/pvc-final.json"
$K get pods -A -o json > "$O/raw/pods-final.json"
$K get namespace zd-sqli-lab --ignore-not-found -o name > "$O/raw/namespace-final.txt"
scratch/zer12/production-nemesis/Scripts/python.exe -B scratch/zer13/codex-completion/recovery_evidence.py final
