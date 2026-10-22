#!/usr/bin/env bash
# N1: run the instrumented suite (n1_run.py) <rounds> times on <tree> with <python>, <par> copies in parallel per
# round (contention). RT1_KEEP keeps a failing test's files under <outdir>/kept/. Every log and timings file is kept.
#   n1_loop.sh <python> <tree> <outdir> <rounds> <par>
set -u
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
py=$1; tree=$(realpath "$2"); out=$(realpath -m "$3"); rounds=$4; par=$5
mkdir -p "$out"
for r in $(seq 1 "$rounds"); do
  for p in $(seq 1 "$par"); do
    ( RT1_KEEP="$out/kept/r$r-p$p" "$py" -B "$here/n1_run.py" "$tree" "$out/r$r-p$p.jsonl" > "$out/r$r-p$p.log" 2>&1
      echo "r$r-p$p exit $?" >> "$out/exits.txt" ) &
  done
  wait
done
echo DONE >> "$out/exits.txt"
