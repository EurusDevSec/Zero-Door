#!/usr/bin/env bash
# Repeat only the hang/timeout test on <tree>, <par> in parallel per round, keeping failing runs' files.
set -u
py=$1; tree=$2; out=$3; rounds=$4; par=$5
mkdir -p "$out"
for r in $(seq 1 "$rounds"); do
  for p in $(seq 1 "$par"); do
    ( cd "$tree" && RT1_KEEP="$out/kept/r$r-p$p" "$py" -B tests/test_dashboard_baseline_runtime.py \
        Controller.test_no_recovery_with_coverage_is_timeout_and_without_coverage_is_missing_probe > "$out/r$r-p$p.log" 2>&1
      echo "r$r-p$p exit $?" >> "$out/exits.txt" ) &
  done
  wait
done
echo DONE >> "$out/exits.txt"
