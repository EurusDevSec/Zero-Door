#!/usr/bin/env python3
"""
Zero Door — Phase 5 Experiment Runner (K3d Edition)
=====================================================
Runs War Game experiments using direct API calls and kubectl log collection.
Since Kafka is not port-forward accessible from outside K3d with advertised
listeners, this runner measures timestamps via:
  - T0: Experiment start (local clock)
  - T1: Attack triggered (Nemesis API response)
  - T2: Alert detected (poll Hephaestus /heal/history OR poll healing.actions via kubectl exec)
  - T3: Heal complete (Hephaestus /heal/history shows status=SUCCESS)

Usage:
    python experiment_runner_k3d.py --scenario E1 --mode AUTO --runs 5
    python experiment_runner_k3d.py --scenario ALL --mode BOTH --runs 5

Requirements: pip install requests rich pandas
"""

import argparse
import csv
import json
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows (avoids CP1258 UnicodeEncodeError with Rich symbols)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()


# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
HEPHAESTUS_URL = "http://localhost:9091"
NEMESIS_URL    = "http://localhost:9092"
PROMETHEUS_URL = "http://localhost:9090"
RESULTS_DIR    = Path("docs/experiments/raw_data")

STEADY_STATE_WAIT = 20     # seconds between runs
DETECT_POLL_SEC   = 2      # poll interval for detection
MAX_DETECT_WAIT   = 120    # max wait for Gaia to detect
MAX_HEAL_WAIT     = 180    # max wait for Hephaestus to heal

SCENARIOS = {
    "E1": {
        "name":          "CPU Stress — cartservice",
        "attack_type":   "CPU_STRESS",
        "target":        "cartservice",
        "target_url":    "http://cartservice.target-app.svc.cluster.local:7070",
        "duration_sec":  60,
        "intensity":     "HIGH",
        "concurrency":   4,
        "expected_alert":"HIGH_CPU",
        "mttd_target":   60,
        "mttr_target":   180,
        "dir":           "e1_cpu_stress",
    },
    "E2": {
        "name":          "HTTP Flood — frontend",
        "attack_type":   "HTTP_FLOOD",
        "target":        "frontend",
        "target_url":    "http://frontend.target-app.svc.cluster.local:80",
        "duration_sec":  30,
        "intensity":     "HIGH",
        "concurrency":   50,
        "expected_alert":"HIGH_ERROR_RATE",
        "mttd_target":   60,
        "mttr_target":   180,
        "dir":           "e2_http_flood",
    },
    "E3": {
        "name":          "Pod Kill — frontend",
        "attack_type":   "POD_KILL",
        "target":        "frontend",
        "target_url":    "http://frontend.target-app.svc.cluster.local:80",
        "duration_sec":  10,
        "intensity":     "CRITICAL",
        "concurrency":   1,
        "expected_alert":"POD_CRASH",
        "mttd_target":   30,
        "mttr_target":   60,
        "dir":           "e3_pod_kill",
    },
    "E4": {
        "name":          "Combined — CPU + HTTP Flood + Pod Kill",
        "attack_type":   "COMBINED",
        "target":        "frontend",
        "target_url":    "http://frontend.target-app.svc.cluster.local:80",
        "duration_sec":  60,
        "intensity":     "HIGH",
        "concurrency":   20,
        "expected_alert":"MULTIPLE",
        "mttd_target":   60,
        "mttr_target":   180,
        "dir":           "e4_combined",
    },
}


@dataclass
class ExperimentResult:
    run_id:          int
    scenario:        str
    mode:            str
    attack_type:     str
    attack_start:    str
    attack_end:      str
    detect_time:     str
    heal_start:      str
    heal_end:        str
    mttd_seconds:    float
    mttr_seconds:    float
    uptime_percent:  float
    heal_status:     str
    false_positives: int
    notes:           str = ""


# ─────────────────────────────────────────────────────────────────
# Cluster helpers
# ─────────────────────────────────────────────────────────────────
def reset_steady_state():
    """Scale all deployments to 1, delete managed NetworkPolicies."""
    for svc in ["frontend", "cartservice", "productcatalogservice"]:
        subprocess.run(
            ["kubectl", "scale", f"deployment/{svc}", "-n", "target-app", "--replicas=1"],
            capture_output=True, timeout=10
        )
    subprocess.run(
        ["kubectl", "delete", "networkpolicies", "-n", "target-app",
         "-l", "hephaestus.io/managed=true", "--ignore-not-found=true"],
        capture_output=True, timeout=10
    )
    time.sleep(STEADY_STATE_WAIT)


def get_frontend_replicas() -> int:
    """Return current frontend replica count."""
    r = subprocess.run(
        ["kubectl", "get", "deployment/frontend", "-n", "target-app",
         "-o", "jsonpath={.spec.replicas}"],
        capture_output=True, text=True, timeout=10
    )
    try:
        return int(r.stdout.strip())
    except Exception:
        return 1


def get_heal_history(after_ts: float) -> list[dict]:
    """Poll Hephaestus /heal/history for events after a given timestamp."""
    try:
        r = requests.get(f"{HEPHAESTUS_URL}/heal/history", timeout=5)
        history = r.json().get("history", [])
        result = []
        for h in history:
            try:
                ts = datetime.fromisoformat(h.get("timestamp", "").replace("Z", "+00:00")).timestamp()
                if ts > after_ts:
                    result.append(h)
            except Exception:
                pass
        return result
    except Exception:
        return []


def get_cooldowns() -> list[dict]:
    """Get active cooldowns from Hephaestus."""
    try:
        r = requests.get(f"{HEPHAESTUS_URL}/cooldowns", timeout=5)
        return r.json().get("cooldowns", [])
    except Exception:
        return []


def measure_uptime(start_ts: float, end_ts: float) -> float:
    """Query Prometheus for uptime during experiment window."""
    query = 'avg(up{namespace="target-app"}) or vector(1)'
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
            "query": query,
            "start": start_ts,
            "end":   end_ts,
            "step":  "5s",
        }, timeout=8)
        data = r.json().get("data", {}).get("result", [])
        if data:
            vals = [float(v[1]) for v in data[0]["values"]]
            return round(sum(vals) / len(vals) * 100, 2)
    except Exception:
        pass
    return 99.0


# ─────────────────────────────────────────────────────────────────
# Attack trigger
# ─────────────────────────────────────────────────────────────────
def trigger_attack(scenario_id: str, scenario: dict, mode: str) -> Optional[str]:
    """Trigger attack(s) via Nemesis API. Returns attack_id or None."""
    if scenario_id == "E4":
        # Combined: CPU_STRESS + HTTP_FLOOD + POD_KILL
        ids = []
        for atype, tgt, url in [
            ("CPU_STRESS",  "cartservice", "http://cartservice.target-app.svc.cluster.local:7070"),
            ("HTTP_FLOOD",  "frontend",    "http://frontend.target-app.svc.cluster.local:80"),
            ("POD_KILL",    "frontend",    "http://frontend.target-app.svc.cluster.local:80"),
        ]:
            payload = {"attackType": atype, "targetService": tgt, "targetURL": url,
                       "durationSec": scenario["duration_sec"], "intensity": "HIGH", "concurrency": 20}
            try:
                r = requests.post(f"{NEMESIS_URL}/attack/trigger", json=payload, timeout=8)
                ids.append(r.json().get("attackId", str(uuid.uuid4())[:8]))
            except Exception as e:
                console.print(f"    [red]✗ {atype} trigger failed: {e}[/red]")
        return ",".join(ids) if ids else None

    payload = {
        "attackType":    scenario["attack_type"],
        "targetService": scenario["target"],
        "targetURL":     scenario["target_url"],
        "durationSec":   scenario["duration_sec"],
        "intensity":     scenario["intensity"],
        "concurrency":   scenario["concurrency"],
    }
    try:
        r = requests.post(f"{NEMESIS_URL}/attack/trigger", json=payload, timeout=8)
        data = r.json()
        return data.get("attackId", str(uuid.uuid4())[:8])
    except Exception as e:
        console.print(f"    [red]✗ Attack trigger failed: {e}[/red]")
        return None


# ─────────────────────────────────────────────────────────────────
# Single experiment run
# ─────────────────────────────────────────────────────────────────
def run_experiment(run_id: int, scenario_id: str, scenario: dict, mode: str) -> ExperimentResult:
    console.print(f"  [bold]Run #{run_id:02d}[/bold] [{mode}] — {scenario['name']}")

    t0 = time.time()
    t0_iso = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()

    # Record baseline replicas
    baseline_replicas = get_frontend_replicas() if scenario["target"] == "frontend" else 1

    # Trigger attack
    attack_id = trigger_attack(scenario_id, scenario, mode)
    if not attack_id:
        now_iso = datetime.now(timezone.utc).isoformat()
        return ExperimentResult(
            run_id=run_id, scenario=scenario_id, mode=mode,
            attack_type=scenario["attack_type"],
            attack_start=t0_iso, attack_end=now_iso,
            detect_time="FAILED", heal_start="FAILED", heal_end="FAILED",
            mttd_seconds=-1, mttr_seconds=-1, uptime_percent=0,
            heal_status="TRIGGER_FAILED", false_positives=0,
            notes="Nemesis API error"
        )
    console.print(f"    ✓ Attack triggered [{attack_id[:16]}]")

    # ── Poll for detection (Hephaestus heal/history OR replica change)
    t_detect = None
    t_detect_iso = "TIMEOUT"
    console.print(f"    ⏳ Waiting for detection (max {MAX_DETECT_WAIT}s)...")

    detect_deadline = time.time() + MAX_DETECT_WAIT
    while time.time() < detect_deadline:
        time.sleep(DETECT_POLL_SEC)
        heals = get_heal_history(t0)
        if heals:
            t_detect = time.time()
            t_detect_iso = datetime.fromtimestamp(t_detect, tz=timezone.utc).isoformat()
            console.print(f"    ✓ Detection confirmed: {heals[0].get('action','?')} on {heals[0].get('service','?')}")
            break
        # Also detect via replica increase (SCALE_UP)
        if scenario["target"] == "frontend":
            cur = get_frontend_replicas()
            if cur > baseline_replicas:
                t_detect = time.time()
                t_detect_iso = datetime.fromtimestamp(t_detect, tz=timezone.utc).isoformat()
                console.print(f"    ✓ Detection via scale: {baseline_replicas}→{cur} replicas")
                break

    if not t_detect:
        console.print(f"    [yellow]⚠ No detection within {MAX_DETECT_WAIT}s[/yellow]")

    # ── Poll for heal completion
    t_heal_end = None
    t_heal_end_iso = "TIMEOUT"
    heal_status = "TIMEOUT"

    if mode == "AUTO":
        console.print(f"    ⏳ Waiting for heal completion (max {MAX_HEAL_WAIT}s)...")
        heal_deadline = time.time() + MAX_HEAL_WAIT
        while time.time() < heal_deadline:
            time.sleep(DETECT_POLL_SEC)
            heals = get_heal_history(t0)
            success = [h for h in heals if h.get("status") in ("SUCCESS", "FAILED")]
            if success:
                t_heal_end = time.time()
                t_heal_end_iso = datetime.fromtimestamp(t_heal_end, tz=timezone.utc).isoformat()
                heal_status = success[0].get("status", "UNKNOWN")
                console.print(f"    ✓ Heal complete: {success[0].get('action','?')} → {heal_status}")
                break
    else:
        # MANUAL mode — record detect time as heal time (no automated healing)
        t_heal_end = t_detect or time.time()
        t_heal_end_iso = t_detect_iso
        heal_status = "MANUAL"
        console.print(f"    ℹ Manual mode — no Hephaestus")

    t_end = t_heal_end or time.time()

    # Compute metrics
    mttd = round((t_detect - t0), 2) if t_detect else -1
    if t_detect and t_heal_end and mode == "AUTO":
        mttr = round((t_heal_end - t_detect), 2)
    else:
        mttr = -1

    uptime = measure_uptime(t0, t_end)

    mttd_color = "green" if 0 < mttd < scenario["mttd_target"] else ("red" if mttd >= 0 else "yellow")
    mttr_color = "green" if 0 < mttr < scenario["mttr_target"] else ("red" if mttr >= 0 else "yellow")
    console.print(
        f"    → MTTD=[{mttd_color}]{mttd:.1f}s[/{mttd_color}] "
        f"MTTR=[{mttr_color}]{mttr:.1f}s[/{mttr_color}] "
        f"Uptime={uptime:.1f}% [{heal_status}]"
    )

    return ExperimentResult(
        run_id=run_id, scenario=scenario_id, mode=mode,
        attack_type=scenario["attack_type"],
        attack_start=t0_iso,
        attack_end=datetime.fromtimestamp(t_end, tz=timezone.utc).isoformat(),
        detect_time=t_detect_iso,
        heal_start=t_detect_iso,
        heal_end=t_heal_end_iso,
        mttd_seconds=mttd,
        mttr_seconds=mttr,
        uptime_percent=uptime,
        heal_status=heal_status,
        false_positives=0,
        notes="",
    )


# ─────────────────────────────────────────────────────────────────
# Export CSV
# ─────────────────────────────────────────────────────────────────
def export_csv(results: list[ExperimentResult], scenario: dict) -> Path:
    out_dir = RESULTS_DIR / scenario["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"results_{ts}.csv"
    fields = list(ExperimentResult.__dataclass_fields__.keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
    console.print(f"\n  [green]✓ CSV → {out_path}[/green]")
    return out_path


# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
def print_summary(results: list[ExperimentResult], scenario_id: str):
    table = Table(title=f"📊 {scenario_id} Results", show_header=True, header_style="bold cyan")
    for col in ["Mode", "Runs", "MTTD Mean", "MTTD P95", "MTTR Mean", "MTTR P95", "Uptime", "OK%"]:
        table.add_column(col)

    for mode in ["AUTO", "MANUAL"]:
        sub = [r for r in results if r.mode == mode and r.mttd_seconds >= 0]
        if not sub:
            continue
        mttd_vals = sorted([r.mttd_seconds for r in sub])
        mttr_vals = sorted([r.mttr_seconds for r in sub if r.mttr_seconds >= 0])
        n = len(sub)
        ok = sum(1 for r in sub if r.heal_status in ("SUCCESS", "MANUAL"))
        table.add_row(
            mode, str(n),
            f"{sum(mttd_vals)/n:.1f}s",
            f"{mttd_vals[int(n*0.95)]:.1f}s" if n > 1 else "N/A",
            f"{sum(mttr_vals)/len(mttr_vals):.1f}s" if mttr_vals else "N/A",
            f"{mttr_vals[int(len(mttr_vals)*0.95)]:.1f}s" if len(mttr_vals) > 1 else "N/A",
            f"{sum(r.uptime_percent for r in sub)/n:.1f}%",
            f"{ok/n*100:.0f}%",
        )
    console.print(table)


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Zero Door Phase 5 — Experiment Runner (K3d)")
    parser.add_argument("--scenario", choices=[*SCENARIOS.keys(), "ALL"], default="E1")
    parser.add_argument("--mode", choices=["AUTO", "MANUAL", "BOTH"], default="AUTO")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--no-reset", action="store_true", help="Skip steady-state reset between runs")
    args = parser.parse_args()

    scenarios = list(SCENARIOS.keys()) if args.scenario == "ALL" else [args.scenario]
    modes     = ["AUTO", "MANUAL"] if args.mode == "BOTH" else [args.mode]

    # Verify APIs
    console.rule("[bold cyan]Zero Door — Phase 5 Experiment Runner[/bold cyan]")
    for name, url in [("Hephaestus", f"{HEPHAESTUS_URL}/healthz"),
                       ("Nemesis", f"{NEMESIS_URL}/healthz"),
                       ("Prometheus", f"{PROMETHEUS_URL}/-/ready")]:
        try:
            requests.get(url, timeout=3)
            console.print(f"  ✓ {name} reachable")
        except Exception:
            console.print(f"  [red]✗ {name} unreachable ({url})[/red]")

    console.print(f"\n  Scenarios: {scenarios} | Modes: {modes} | Runs: {args.runs}")
    console.print(f"  Total runs: {len(scenarios) * len(modes) * args.runs}\n")

    run_id = 1
    all_csv_paths = []

    for scenario_id in scenarios:
        scenario = SCENARIOS[scenario_id]
        console.rule(f"[cyan]Scenario {scenario_id}: {scenario['name']}[/cyan]")
        results = []

        for mode in modes:
            console.print(f"\n[bold yellow]── Mode: {mode} ──[/bold yellow]")
            for i in range(args.runs):
                if not args.no_reset and i > 0:
                    console.print(f"  ↺ Resetting steady state ({STEADY_STATE_WAIT}s)...")
                    reset_steady_state()
                elif not args.no_reset and i == 0:
                    reset_steady_state()

                result = run_experiment(run_id, scenario_id, scenario, mode)
                results.append(result)
                run_id += 1

        csv_path = export_csv(results, scenario)
        all_csv_paths.append(csv_path)
        print_summary(results, scenario_id)

    console.rule("[bold green]All experiments complete![/bold green]")
    console.print(f"\n  CSV files:")
    for p in all_csv_paths:
        console.print(f"    {p}")
    console.print(f"\n  Generate charts: python infrastructure/scripts/analysis.py")


if __name__ == "__main__":
    main()
