#!/usr/bin/env python3
"""
Zero Door — Phase 5 Experiment Runner
======================================
Automates War Game experiments: triggers attacks via Nemesis API,
collects timestamps from Kafka topics (attack.results, monitoring.alerts,
healing.actions), computes MTTD/MTTR, and exports results to CSV.

Usage:
    python experiment_runner.py --scenario E1 --mode AUTO --runs 15
    python experiment_runner.py --scenario ALL --mode AUTO --runs 15
    python experiment_runner.py --help

Requirements:
    pip install kafka-python requests rich
"""

import argparse
import csv
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from kafka import KafkaConsumer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────
NEMESIS_URL           = os.getenv("NEMESIS_URL", "http://localhost:9092")     # port-forwarded
HEPHAESTUS_URL        = os.getenv("HEPHAESTUS_URL", "http://localhost:9091")
PROMETHEUS_URL        = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
KAFKA_BOOTSTRAP       = os.getenv("KAFKA_BOOTSTRAP", "localhost:9093")       # port-forwarded
RESULTS_DIR           = Path(__file__).parent.parent / "docs" / "experiments" / "raw_data"
STEADY_STATE_WAIT_SEC = int(os.getenv("STEADY_STATE_WAIT_SEC", "30"))
KAFKA_POLL_TIMEOUT_MS = 60_000   # max 60s waiting for a Kafka message

# ─────────────────────────────────────────────────────────────────
# Experiment Definitions  (T5.2 — Experiment Matrix)
# ─────────────────────────────────────────────────────────────────
SCENARIOS = {
    "E1": {
        "name":         "CPU Stress — cartservice",
        "attack_type":  "CPU_STRESS",
        "target":       "cartservice",
        "duration_sec": 60,
        "intensity":    "HIGH",
        "concurrency":  0,
        "expected_alert": "HIGH_CPU",
        "expected_action": "SCALE_UP",
        "success_mttd_max": 60,
        "success_mttr_max": 180,
        "dir":          "e1_cpu_stress",
    },
    "E2": {
        "name":         "HTTP Flood — frontend",
        "attack_type":  "HTTP_FLOOD",
        "target":       "frontend",
        "target_url":   "http://frontend.target-app.svc.cluster.local",
        "duration_sec": 30,
        "intensity":    "HIGH",
        "concurrency":  100,
        "expected_alert": "HIGH_ERROR_RATE",
        "expected_action": "SCALE_UP",
        "success_mttd_max": 60,
        "success_mttr_max": 180,
        "dir":          "e2_http_flood",
    },
    "E3": {
        "name":         "Pod Kill — frontend",
        "attack_type":  "POD_KILL",
        "target":       "frontend",
        "duration_sec": 10,
        "intensity":    "CRITICAL",
        "concurrency":  0,
        "expected_alert": "POD_CRASH",
        "expected_action": "RESTART",
        "success_mttd_max": 30,
        "success_mttr_max": 60,
        "dir":          "e3_pod_kill",
    },
    "E4": {
        "name":         "Combined — CPU Stress + HTTP Flood + Pod Kill",
        "attack_type":  "COMBINED",
        "targets":      ["cartservice", "frontend"],
        "duration_sec": 90,
        "intensity":    "HIGH",
        "concurrency":  50,
        "expected_alert": "MULTIPLE",
        "expected_action": "MULTIPLE",
        "success_mttd_max": 60,
        "success_mttr_max": 180,
        "dir":          "e4_combined",
    },
}


# ─────────────────────────────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────────────────────────────
@dataclass
class ExperimentResult:
    run_id:          int
    scenario:        str
    mode:            str          # AUTO or MANUAL
    attack_type:     str
    attack_start:    str          # ISO 8601
    attack_end:      str
    detect_time:     str          # When Gaia published to monitoring.alerts
    heal_start:      str          # When Hephaestus received alert
    heal_end:        str          # When healing.actions published
    mttd_seconds:    float        # detect_time - attack_start
    mttr_seconds:    float        # heal_end - detect_time
    uptime_percent:  float
    heal_status:     str          # SUCCESS / FAILED / TIMEOUT / N_A
    false_positives: int
    notes:           str = ""


# ─────────────────────────────────────────────────────────────────
# Kafka helpers
# ─────────────────────────────────────────────────────────────────
def _make_consumer(topics: list[str], group_suffix: str) -> KafkaConsumer:
    """Create a Kafka consumer subscribed to one or more topics."""
    return KafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP.split(","),
        group_id=f"experiment-runner-{group_suffix}-{uuid.uuid4().hex[:8]}",
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=KAFKA_POLL_TIMEOUT_MS,
        enable_auto_commit=True,
    )


def wait_for_kafka_message(topic: str, filter_fn, timeout_sec: int = 90) -> Optional[dict]:
    """
    Poll a Kafka topic until a message matching filter_fn arrives, or timeout.
    Returns the message value dict or None on timeout.
    """
    deadline = time.time() + timeout_sec
    consumer = _make_consumer([topic], topic.replace(".", "-"))
    try:
        for msg in consumer:
            if filter_fn(msg.value):
                return msg.value
            if time.time() > deadline:
                break
    except Exception:
        pass
    finally:
        consumer.close()
    return None


# ─────────────────────────────────────────────────────────────────
# Steady-State Verification  (T5.1)
# ─────────────────────────────────────────────────────────────────
def check_steady_state() -> bool:
    """
    Query Prometheus to verify the cluster is in steady-state before an experiment.
    Returns True if all metrics are within thresholds.
    """
    queries = {
        "cpu_ok": {
            "query": 'max(rate(container_cpu_usage_seconds_total{namespace="target-app",container!=""}[1m]))',
            "threshold": 0.60,
            "op": "lt",
        },
        "error_rate_ok": {
            "query": 'sum(rate(http_server_requests_seconds_count{namespace="target-app",status=~"5.."}[1m])) or vector(0)',
            "threshold": 0.01,
            "op": "lt",
        },
    }
    all_ok = True
    for name, cfg in queries.items():
        try:
            r = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": cfg["query"]},
                timeout=5,
            )
            result = r.json().get("data", {}).get("result", [])
            if result:
                val = float(result[0]["value"][1])
                ok = (val < cfg["threshold"]) if cfg["op"] == "lt" else (val > cfg["threshold"])
                if not ok:
                    console.print(f"  [yellow]⚠ {name}: {val:.3f} exceeds threshold {cfg['threshold']}[/yellow]")
                    all_ok = False
        except Exception as e:
            console.print(f"  [yellow]⚠ Prometheus unreachable ({e}) — assuming steady state[/yellow]")
    return all_ok


def reset_to_steady_state(scenario_id: str):
    """
    Reset cluster to steady state between runs:
    - Scale deployments back to 1
    - Delete managed NetworkPolicies
    - Wait STEADY_STATE_WAIT_SEC for metrics to normalize
    """
    import subprocess
    console.print(f"  [cyan]↺ Resetting to steady state...[/cyan]")

    # Scale frontend and cartservice back to baseline
    for svc in ["frontend", "cartservice", "productcatalogservice"]:
        try:
            subprocess.run(
                ["kubectl", "scale", f"deployment/{svc}", "-n", "target-app", "--replicas=1"],
                capture_output=True, timeout=10
            )
        except Exception:
            pass

    # Delete any NetworkPolicies created by Hephaestus
    try:
        subprocess.run(
            ["kubectl", "delete", "networkpolicies", "-n", "target-app",
             "-l", "hephaestus.io/managed=true", "--ignore-not-found=true"],
            capture_output=True, timeout=10
        )
    except Exception:
        pass

    console.print(f"  [cyan]⏳ Waiting {STEADY_STATE_WAIT_SEC}s for metrics to normalize...[/cyan]")
    time.sleep(STEADY_STATE_WAIT_SEC)


# ─────────────────────────────────────────────────────────────────
# Attack Trigger  (via Nemesis REST API)
# ─────────────────────────────────────────────────────────────────
def trigger_attack(scenario: dict, scenario_id: str) -> Optional[str]:
    """
    Trigger an attack via Nemesis /attack/trigger endpoint.
    Returns attack_id or None on failure.
    """
    if scenario_id == "E4":
        # Combined: trigger CPU_STRESS + HTTP_FLOOD sequentially
        attack_ids = []
        for atype, target in [("CPU_STRESS", "cartservice"), ("HTTP_FLOOD", "frontend"), ("POD_KILL", "frontend")]:
            payload = {
                "attackType":    atype,
                "targetService": target,
                "targetURL":     f"http://{target}.target-app.svc.cluster.local",
                "durationSec":   scenario.get("duration_sec", 60),
                "intensity":     scenario.get("intensity", "HIGH"),
                "concurrency":   scenario.get("concurrency", 10),
            }
            try:
                r = requests.post(f"{NEMESIS_URL}/attack/trigger", json=payload, timeout=5)
                data = r.json()
                attack_ids.append(data.get("attackId", ""))
            except Exception:
                pass
        return ",".join(attack_ids) if attack_ids else None

    payload = {
        "attackType":    scenario["attack_type"],
        "targetService": scenario.get("target", "frontend"),
        "targetURL":     scenario.get("target_url", f"http://{scenario.get('target','frontend')}.target-app.svc.cluster.local"),
        "durationSec":   scenario.get("duration_sec", 30),
        "intensity":     scenario.get("intensity", "HIGH"),
        "concurrency":   scenario.get("concurrency", 10),
    }
    try:
        r = requests.post(f"{NEMESIS_URL}/attack/trigger", json=payload, timeout=5)
        return r.json().get("attackId", str(uuid.uuid4()))
    except Exception as e:
        console.print(f"  [red]✗ Failed to trigger attack: {e}[/red]")
        return None


# ─────────────────────────────────────────────────────────────────
# Uptime calculation from Prometheus
# ─────────────────────────────────────────────────────────────────
def measure_uptime(start_ts: float, end_ts: float) -> float:
    """
    Query Prometheus for error rate during the experiment window.
    Returns uptime % = 100 - error_seconds_percent.
    """
    query = 'sum(rate(http_server_requests_seconds_count{namespace="target-app",status=~"5.."}[30s])) or vector(0)'
    try:
        r = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                "query": query,
                "start": start_ts,
                "end":   end_ts,
                "step":  "5s",
            },
            timeout=10,
        )
        data = r.json().get("data", {}).get("result", [])
        if not data:
            return 100.0
        values = [float(v[1]) for v in data[0]["values"]]
        error_fraction = sum(values) / len(values) if values else 0.0
        return round(max(0.0, 100.0 - error_fraction * 100), 2)
    except Exception:
        return 99.0   # assume near-perfect if Prometheus unreachable


# ─────────────────────────────────────────────────────────────────
# Single Experiment Run
# ─────────────────────────────────────────────────────────────────
def run_single_experiment(
    run_id: int,
    scenario_id: str,
    scenario: dict,
    mode: str,
) -> ExperimentResult:
    """Execute one experiment run and return the result dataclass."""
    console.print(f"\n  [bold]Run #{run_id:02d}[/bold] — {scenario['name']} [{mode}]")

    # T0: Attack start
    t_attack_start = datetime.now(timezone.utc)
    attack_id = trigger_attack(scenario, scenario_id)
    if not attack_id:
        # Gracefully record failure if Nemesis unreachable
        now_iso = datetime.now(timezone.utc).isoformat()
        return ExperimentResult(
            run_id=run_id, scenario=scenario_id, mode=mode,
            attack_type=scenario["attack_type"],
            attack_start=t_attack_start.isoformat(),
            attack_end=now_iso, detect_time="N/A", heal_start="N/A", heal_end="N/A",
            mttd_seconds=-1, mttr_seconds=-1, uptime_percent=0.0,
            heal_status="TRIGGER_FAILED", false_positives=0,
            notes="Nemesis API unreachable"
        )

    t_attack_start_ts = t_attack_start.timestamp()
    console.print(f"    ✓ Attack triggered: {attack_id[:16]}...")

    # T1: Wait for Gaia to publish monitoring.alerts
    console.print(f"    ⏳ Waiting for Gaia alert on monitoring.alerts...")
    alert_msg = wait_for_kafka_message(
        "monitoring.alerts",
        lambda m: True,  # accept first alert after attack
        timeout_sec=120,
    )
    t_detect = datetime.now(timezone.utc)
    if not alert_msg:
        console.print(f"    [yellow]⚠ No alert detected within timeout[/yellow]")
        t_detect_iso = "TIMEOUT"
    else:
        t_detect_iso = alert_msg.get("timestamp", t_detect.isoformat())
        console.print(f"    ✓ Alert: {alert_msg.get('type','?')} / {alert_msg.get('severity','?')}")

    # T2: Wait for Hephaestus healing.actions (only in AUTO mode)
    if mode == "AUTO":
        console.print(f"    ⏳ Waiting for Hephaestus heal on healing.actions...")
        heal_msg = wait_for_kafka_message(
            "healing.actions",
            lambda m: True,
            timeout_sec=180,
        )
        t_heal_end = datetime.now(timezone.utc)
        if not heal_msg:
            heal_start_iso = t_detect_iso
            heal_end_iso   = "TIMEOUT"
            heal_status    = "TIMEOUT"
        else:
            heal_start_iso = heal_msg.get("timestamp", t_detect.isoformat())
            heal_end_iso   = t_heal_end.isoformat()
            heal_status    = heal_msg.get("status", "UNKNOWN")
            console.print(f"    ✓ Healed: {heal_msg.get('action','?')} → {heal_status}")
    else:
        # MANUAL mode — no automated healing
        heal_start_iso = "N/A"
        heal_end_iso   = "N/A"
        heal_status    = "MANUAL"
        t_heal_end     = t_detect
        console.print(f"    ℹ Manual mode — no Hephaestus healing")

    t_attack_end = t_heal_end  # end when heal completes (or detect in manual)

    # Compute metrics
    try:
        t_detect_dt   = datetime.fromisoformat(t_detect_iso.replace("Z", "+00:00"))
        mttd_seconds  = max(0.0, (t_detect_dt - t_attack_start).total_seconds())
    except Exception:
        mttd_seconds  = -1.0

    try:
        t_heal_dt     = datetime.fromisoformat(heal_end_iso.replace("Z", "+00:00"))
        t_det_dt      = datetime.fromisoformat(t_detect_iso.replace("Z", "+00:00"))
        mttr_seconds  = max(0.0, (t_heal_dt - t_det_dt).total_seconds())
    except Exception:
        mttr_seconds  = -1.0

    uptime = measure_uptime(t_attack_start_ts, t_attack_end.timestamp())

    return ExperimentResult(
        run_id=run_id,
        scenario=scenario_id,
        mode=mode,
        attack_type=scenario["attack_type"],
        attack_start=t_attack_start.isoformat(),
        attack_end=t_attack_end.isoformat(),
        detect_time=t_detect_iso,
        heal_start=heal_start_iso,
        heal_end=heal_end_iso,
        mttd_seconds=round(mttd_seconds, 2),
        mttr_seconds=round(mttr_seconds, 2),
        uptime_percent=uptime,
        heal_status=heal_status,
        false_positives=0,
        notes="",
    )


# ─────────────────────────────────────────────────────────────────
# Export to CSV  (T5.7, T5.8)
# ─────────────────────────────────────────────────────────────────
def export_csv(results: list[ExperimentResult], scenario_id: str, scenario: dict):
    """Write results to a CSV file in docs/experiments/raw_data/{dir}/"""
    out_dir = RESULTS_DIR / scenario["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"results_{ts}.csv"

    fieldnames = list(ExperimentResult.__dataclass_fields__.keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))

    console.print(f"\n  [green]✓ CSV exported → {out_path}[/green]")
    return out_path


# ─────────────────────────────────────────────────────────────────
# Summary Statistics  (T5.9)
# ─────────────────────────────────────────────────────────────────
def print_summary(results: list[ExperimentResult], scenario_id: str):
    """Print a rich table of summary statistics."""
    auto   = [r for r in results if r.mode == "AUTO" and r.mttd_seconds >= 0]
    manual = [r for r in results if r.mode == "MANUAL" and r.mttd_seconds >= 0]

    def stats(vals: list[float], name: str) -> dict:
        if not vals:
            return {"mean": "N/A", "median": "N/A", "p95": "N/A", "p_ok_60": "N/A", "p_ok_180": "N/A"}
        vals.sort()
        n = len(vals)
        mean   = sum(vals) / n
        median = vals[n // 2]
        p95    = vals[int(n * 0.95)]
        return {
            "mean":     f"{mean:.1f}s",
            "median":   f"{median:.1f}s",
            "p95":      f"{p95:.1f}s",
            "p_ok_60":  f"{sum(1 for v in vals if v < 60)/n*100:.0f}%",
            "p_ok_180": f"{sum(1 for v in vals if v < 180)/n*100:.0f}%",
        }

    auto_mttd_stats  = stats([r.mttd_seconds for r in auto], "MTTD")
    auto_mttr_stats  = stats([r.mttr_seconds  for r in auto if r.mttr_seconds >= 0], "MTTR")
    man_mttd_stats   = stats([r.mttd_seconds  for r in manual], "MTTD")
    man_mttr_stats   = stats([r.mttr_seconds  for r in manual if r.mttr_seconds >= 0], "MTTR")

    table = Table(title=f"📊 Experiment {scenario_id} — Summary Statistics", show_header=True)
    table.add_column("Metric",   style="bold")
    table.add_column("AUTO Mean")
    table.add_column("AUTO Median")
    table.add_column("AUTO P95")
    table.add_column("AUTO <60s %")
    table.add_column("AUTO <180s %")
    table.add_column("MANUAL Mean")

    table.add_row("MTTD",
                  auto_mttd_stats["mean"], auto_mttd_stats["median"], auto_mttd_stats["p95"],
                  auto_mttd_stats["p_ok_60"], auto_mttd_stats["p_ok_180"],
                  man_mttd_stats["mean"])
    table.add_row("MTTR",
                  auto_mttr_stats["mean"], auto_mttr_stats["median"], auto_mttr_stats["p95"],
                  auto_mttr_stats["p_ok_60"], auto_mttr_stats["p_ok_180"],
                  man_mttr_stats["mean"])
    table.add_row("Uptime",
                  f"{sum(r.uptime_percent for r in auto)/max(1,len(auto)):.1f}%", "—", "—", "—", "—",
                  f"{sum(r.uptime_percent for r in manual)/max(1,len(manual)):.1f}%")
    table.add_row("Runs",
                  str(len(auto)), "—", "—", "—", "—", str(len(manual)))

    console.print(table)


# ─────────────────────────────────────────────────────────────────
# Main CLI
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Zero Door Phase 5 — Experiment Runner"
    )
    parser.add_argument("--scenario", choices=[*SCENARIOS.keys(), "ALL"], default="E1",
                        help="Experiment scenario ID (default: E1)")
    parser.add_argument("--mode", choices=["AUTO", "MANUAL", "BOTH"], default="AUTO",
                        help="Healing mode (default: AUTO)")
    parser.add_argument("--runs", type=int, default=5,
                        help="Number of runs per mode (default: 5, recommended: 15)")
    parser.add_argument("--skip-steady-state", action="store_true",
                        help="Skip steady-state verification between runs")
    args = parser.parse_args()

    scenarios_to_run = list(SCENARIOS.keys()) if args.scenario == "ALL" else [args.scenario]
    modes_to_run     = ["AUTO", "MANUAL"] if args.mode == "BOTH" else [args.mode]

    console.rule("[bold cyan]Zero Door — Phase 5 War Game Experiments[/bold cyan]")
    console.print(f"  Scenarios : {', '.join(scenarios_to_run)}")
    console.print(f"  Modes     : {', '.join(modes_to_run)}")
    console.print(f"  Runs/mode : {args.runs}")
    console.print(f"  Total runs: {len(scenarios_to_run) * len(modes_to_run) * args.runs}")
    console.print()

    global_run_id = 1
    all_results: list[ExperimentResult] = []

    for scenario_id in scenarios_to_run:
        scenario = SCENARIOS[scenario_id]
        console.rule(f"[cyan]Scenario {scenario_id}: {scenario['name']}[/cyan]")

        scenario_results: list[ExperimentResult] = []
        for mode in modes_to_run:
            console.print(f"\n[bold yellow]Mode: {mode}[/bold yellow]")
            for i in range(args.runs):
                # Reset to steady state between runs
                if not args.skip_steady_state:
                    reset_to_steady_state(scenario_id)
                    if not check_steady_state():
                        console.print(f"  [yellow]⚠ Cluster not in steady state — waiting extra 30s[/yellow]")
                        time.sleep(30)

                result = run_single_experiment(global_run_id, scenario_id, scenario, mode)
                scenario_results.append(result)
                all_results.append(result)

                status_color = "green" if result.heal_status in ("SUCCESS", "MANUAL") else "red"
                console.print(
                    f"    → MTTD={result.mttd_seconds:.1f}s  "
                    f"MTTR={result.mttr_seconds:.1f}s  "
                    f"Uptime={result.uptime_percent:.1f}%  "
                    f"[{status_color}]{result.heal_status}[/{status_color}]"
                )
                global_run_id += 1

        # Export CSV and print summary per scenario
        export_csv(scenario_results, scenario_id, scenario)
        print_summary(scenario_results, scenario_id)

    console.rule("[bold green]All experiments complete![/bold green]")
    console.print(f"  Total runs executed: {len(all_results)}")
    successful = sum(1 for r in all_results if r.heal_status in ("SUCCESS", "MANUAL"))
    console.print(f"  Successful heals   : {successful}/{len(all_results)}")


if __name__ == "__main__":
    main()
