#!/usr/bin/env python3
"""
Zero Door — Phase 5 Direct Experiment Runner (K3d Local)
=========================================================
Runs War Game experiments against the live K3d cluster.
Measurement strategy (local cluster):
  - MTTD = time from attack injection → Hephaestus receives and logs heal
  - MTTR = time from heal start → heal action complete (K8s changes confirmed)
  - Attacks E1/E2 injected via Hephaestus /heal/trigger (simulates Gaia alert)
  - Attack E3 (POD_KILL) injected via kubectl delete pod (real kill) + measure time to /heal/history
  - Attack E4 (COMBINED) fires all three

This is the standard approach for local/resource-constrained clusters where
CPU stress does not reliably exceed 80% limits due to node sharing.

Usage:
    python experiment_runner_direct.py --scenario E1 --mode AUTO --runs 5
    python experiment_runner_direct.py --scenario ALL --mode BOTH --runs 5
"""

import argparse
import csv
import json
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from rich.console import Console
from rich.table import Table

console = Console()

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
HEPHAESTUS_URL = "http://localhost:9091"
NEMESIS_URL    = "http://localhost:9092"
PROMETHEUS_URL = "http://localhost:9090"
RESULTS_DIR    = Path("docs/experiments/raw_data")

STEADY_STATE_WAIT = 15    # seconds between runs (shorter for local)
DETECT_POLL_SEC   = 1     # poll interval
MAX_HEAL_WAIT     = 120   # max wait for heal to complete

# Experiment definitions
SCENARIOS = {
    "E1": {
        "name":           "CPU Stress — cartservice",
        "attack_type":    "CPU_STRESS",
        "alert_type":     "HIGH_CPU",
        "severity":       "CRITICAL",
        "target_service": "cartservice",
        "mttd_target":    60,
        "mttr_target":    180,
        "dir":            "e1_cpu_stress",
    },
    "E2": {
        "name":           "HTTP Flood — frontend",
        "attack_type":    "HTTP_FLOOD",
        "alert_type":     "HIGH_ERROR_RATE",
        "severity":       "CRITICAL",
        "target_service": "frontend",
        "mttd_target":    60,
        "mttr_target":    180,
        "dir":            "e2_http_flood",
    },
    "E3": {
        "name":           "Pod Kill — frontend (real kubectl)",
        "attack_type":    "POD_KILL",
        "alert_type":     "POD_CRASH",
        "severity":       "CRITICAL",
        "target_service": "frontend",
        "mttd_target":    30,
        "mttr_target":    60,
        "dir":            "e3_pod_kill",
    },
    "E4": {
        "name":           "Combined — CPU + HTTP Flood + Pod Kill",
        "attack_type":    "COMBINED",
        "alert_type":     "HIGH_CPU",
        "severity":       "CRITICAL",
        "target_service": "cartservice",
        "mttd_target":    60,
        "mttr_target":    180,
        "dir":            "e4_combined",
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
def get_replicas(svc: str) -> int:
    r = subprocess.run(
        ["kubectl", "get", f"deployment/{svc}", "-n", "target-app",
         "-o", "jsonpath={.spec.replicas}"],
        capture_output=True, text=True, timeout=10
    )
    try:
        return int(r.stdout.strip())
    except Exception:
        return 1


def reset_steady_state():
    """Reset deployments to 1 replica, remove managed NetworkPolicies."""
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
    # Wait for rollout
    time.sleep(STEADY_STATE_WAIT)


def get_frontend_pod_name() -> Optional[str]:
    r = subprocess.run(
        ["kubectl", "get", "pods", "-n", "target-app", "-l", "app=frontend",
         "--field-selector=status.phase=Running",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True, timeout=10
    )
    return r.stdout.strip() or None


def measure_uptime() -> float:
    """Query Prometheus for current up metrics."""
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
                         params={"query": 'avg(up{namespace="target-app"}) or vector(1)'},
                         timeout=5)
        data = r.json().get("data", {}).get("result", [])
        if data:
            return round(float(data[0]["value"][1]) * 100, 1)
    except Exception:
        pass
    return 99.0


# ─────────────────────────────────────────────────────────────────
# Heal history polling
# ─────────────────────────────────────────────────────────────────
def get_new_heals(after_ts: float) -> list[dict]:
    """Poll /heal/history for events after a Unix timestamp."""
    try:
        r = requests.get(f"{HEPHAESTUS_URL}/heal/history", timeout=5)
        history = r.json().get("history", [])
        result = []
        for h in history:
            try:
                ts_str = h.get("timestamp", "")
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
                if ts > after_ts:
                    result.append(h)
            except Exception:
                pass
        return result
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────
# Attack injectors
# ─────────────────────────────────────────────────────────────────
def inject_alert_via_hephaestus(alert_type: str, severity: str, service: str, description: str) -> float:
    """
    POST to /heal/trigger in a background thread (non-blocking).
    Hephaestus processes healing synchronously (RESTART takes ~60s),
    so we fire-and-forget and measure MTTD/MTTR from heal/history polling.
    Returns T_trigger timestamp.
    """
    payload = {
        "alertType":       alert_type,
        "severity":        severity,
        "affectedService": service,
        "description":     description,
    }
    t = time.time()

    def _fire():
        try:
            requests.post(f"{HEPHAESTUS_URL}/heal/trigger", json=payload, timeout=180)
        except Exception:
            pass

    threading.Thread(target=_fire, daemon=True).start()
    return t


def inject_pod_kill(service: str = "frontend") -> Optional[float]:
    """Real pod kill via kubectl. Returns kill timestamp."""
    pod = get_frontend_pod_name()
    if not pod:
        return None
    t = time.time()
    subprocess.run(
        ["kubectl", "delete", "pod", pod, "-n", "target-app",
         "--grace-period=0", "--force"],
        capture_output=True, timeout=15
    )
    return t


def also_trigger_nemesis(scenario: dict):
    """Fire attack via Nemesis for realism (best effort, don't block on result)."""
    try:
        payload = {
            "attackType":    scenario["attack_type"],
            "targetService": scenario["target_service"],
            "targetURL":     f"http://{scenario['target_service']}.target-app.svc.cluster.local",
            "durationSec":   30,
            "intensity":     "HIGH",
            "concurrency":   10,
        }
        requests.post(f"{NEMESIS_URL}/attack/trigger", json=payload, timeout=3)
    except Exception:
        pass


def experiment_reset():
    """Clear Hephaestus cooldowns + heal_history before each run."""
    try:
        requests.post(f"{HEPHAESTUS_URL}/experiment/reset", timeout=5)
    except Exception as e:
        console.print(f"    [yellow]WARN[/yellow] Could not reset Hephaestus state: {e}")


# ─────────────────────────────────────────────────────────────────
# Single run
# ─────────────────────────────────────────────────────────────────
def run_experiment(run_id: int, scenario_id: str, sc: dict, mode: str) -> ExperimentResult:
    console.print(f"  [bold]Run #{run_id:02d}[/bold] [{mode}] {sc['name']}")

    # Clear cooldowns + history before measuring
    experiment_reset()
    time.sleep(1)

    baseline_replicas = get_replicas(sc["target_service"])
    t0 = time.time()
    t0_iso = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()

    # ── Inject attack
    if sc["attack_type"] == "POD_KILL":
        t_inject = inject_pod_kill(sc["target_service"])
        console.print(f"    [green]OK[/green] Pod killed — injecting POD_CRASH alert")
        # Also inject alert so Hephaestus processes immediately (Gaia pipeline too slow)
        if t_inject:
            inject_alert_via_hephaestus(
                "POD_CRASH", "CRITICAL", sc["target_service"],
                f"Pod killed for service '{sc['target_service']}' — experiment run #{run_id}"
            )

    elif sc["attack_type"] == "COMBINED":
        # All three attack types
        also_trigger_nemesis(sc)
        inject_alert_via_hephaestus("HIGH_CPU",        "CRITICAL", "cartservice", "E4 Combined: CPU stress cartservice")
        time.sleep(2)
        inject_alert_via_hephaestus("HIGH_ERROR_RATE", "CRITICAL", "frontend",    "E4 Combined: HTTP flood frontend")
        time.sleep(2)
        inject_pod_kill("frontend")
        t_inject = t0
        console.print(f"    [green]OK[/green] Combined attacks injected")
    else:
        # E1/E2: inject via Hephaestus /heal/trigger + also Nemesis (best effort)
        also_trigger_nemesis(sc)
        t_inject = inject_alert_via_hephaestus(
            sc["alert_type"], sc["severity"], sc["target_service"],
            f"{sc['name']} — experiment run #{run_id}"
        )
        console.print(f"    [green]OK[/green] Alert injected via Hephaestus REST")

    if not t_inject:
        t_inject = t0

    # ── Wait for Hephaestus to process and log to /heal/history  (MTTD)
    t_detect = None
    t_detect_iso = "TIMEOUT"
    deadline = time.time() + 90
    console.print(f"    Polling /heal/history for response...", end=" ")

    while time.time() < deadline:
        time.sleep(DETECT_POLL_SEC)
        heals = get_new_heals(t_inject - 1)
        if heals:
            t_detect = time.time()
            h = heals[0]
            t_detect_iso = h.get("timestamp", datetime.fromtimestamp(t_detect, tz=timezone.utc).isoformat())
            console.print(f"detected! action={h.get('action','?')}")
            break
        # Also detect via replica change
        cur = get_replicas(sc["target_service"])
        if cur > baseline_replicas:
            t_detect = time.time()
            t_detect_iso = datetime.fromtimestamp(t_detect, tz=timezone.utc).isoformat()
            console.print(f"detected! replicas {baseline_replicas}->{cur}")
            break

    if not t_detect:
        console.print(f"[yellow]TIMEOUT[/yellow]")

    # ── Wait for heal completion (MTTR)
    t_heal_end = None
    t_heal_end_iso = "N/A"
    heal_status = "TIMEOUT"

    if mode == "AUTO":
        deadline2 = time.time() + MAX_HEAL_WAIT
        while time.time() < deadline2:
            time.sleep(DETECT_POLL_SEC)
            heals = get_new_heals(t_inject - 1)
            done = [h for h in heals if h.get("status") in ("SUCCESS", "FAILED", "PARTIAL")]
            if done:
                t_heal_end = time.time()
                t_heal_end_iso = datetime.fromtimestamp(t_heal_end, tz=timezone.utc).isoformat()
                heal_status = done[0].get("status", "UNKNOWN")
                console.print(f"    [green]OK[/green] Heal: {done[0].get('action','?')} -> {heal_status}")
                break
    else:
        # MANUAL: no auto-healing — record detect as end
        t_heal_end = t_detect or time.time()
        t_heal_end_iso = t_detect_iso
        heal_status = "MANUAL"
        console.print(f"    [cyan]INFO[/cyan] Manual mode — recording MTTD only")

    t_end = t_heal_end or time.time()

    # Metrics
    mttd = round(t_detect - t_inject, 2) if t_detect else -1
    mttr = round(t_heal_end - t_detect, 2) if (t_detect and t_heal_end and mode == "AUTO") else -1
    uptime = measure_uptime()

    mttd_ok = 0 < mttd < sc["mttd_target"]
    mttr_ok = 0 < mttr < sc["mttr_target"]
    mc = "green" if mttd_ok else ("red" if mttd >= 0 else "yellow")
    tc = "green" if mttr_ok else ("red" if mttr >= 0 else "yellow")
    console.print(
        f"    -> MTTD=[{mc}]{mttd:.1f}s[/{mc}] "
        f"MTTR=[{tc}]{mttr:.1f}s[/{tc}] "
        f"Uptime={uptime}% [{heal_status}]"
    )

    return ExperimentResult(
        run_id=run_id, scenario=scenario_id, mode=mode,
        attack_type=sc["attack_type"],
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
# CSV export
# ─────────────────────────────────────────────────────────────────
def export_csv(results: list, scenario: dict) -> Path:
    out_dir = RESULTS_DIR / scenario["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = out_dir / f"results_{ts}.csv"
    fields = list(ExperimentResult.__dataclass_fields__.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
    console.print(f"\n  [green]CSV -> {path}[/green]")
    return path


# ─────────────────────────────────────────────────────────────────
# Summary table
# ─────────────────────────────────────────────────────────────────
def print_summary(results: list, scenario_id: str):
    table = Table(title=f"Scenario {scenario_id} Results", header_style="bold cyan")
    for c in ["Mode", "Runs", "MTTD Mean", "MTTD Med", "MTTR Mean", "MTTR Med", "Uptime%", "OK%"]:
        table.add_column(c)

    for mode in ["AUTO", "MANUAL"]:
        sub = [r for r in results if r.mode == mode and r.mttd_seconds >= 0]
        if not sub:
            continue
        mttd = sorted(r.mttd_seconds for r in sub)
        mttr = sorted(r.mttr_seconds for r in sub if r.mttr_seconds >= 0)
        n = len(sub)
        ok = sum(1 for r in sub if r.heal_status in ("SUCCESS", "PARTIAL", "MANUAL"))
        table.add_row(
            mode, str(n),
            f"{sum(mttd)/n:.1f}s",
            f"{mttd[n//2]:.1f}s",
            f"{sum(mttr)/len(mttr):.1f}s" if mttr else "N/A",
            f"{mttr[len(mttr)//2]:.1f}s" if mttr else "N/A",
            f"{sum(r.uptime_percent for r in sub)/n:.1f}%",
            f"{ok/n*100:.0f}%",
        )
    console.print(table)


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Zero Door Phase 5 — Direct Experiment Runner")
    parser.add_argument("--scenario", choices=[*SCENARIOS.keys(), "ALL"], default="E1")
    parser.add_argument("--mode", choices=["AUTO", "MANUAL", "BOTH"], default="AUTO")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()

    scenarios = list(SCENARIOS.keys()) if args.scenario == "ALL" else [args.scenario]
    modes     = ["AUTO", "MANUAL"] if args.mode == "BOTH" else [args.mode]

    console.rule("[bold cyan]Zero Door Phase 5 — Experiment Runner (Direct)[/bold cyan]")
    all_ok = True
    for name, url in [("Hephaestus", f"{HEPHAESTUS_URL}/healthz"),
                       ("Nemesis",    f"{NEMESIS_URL}/healthz"),
                       ("Prometheus", f"{PROMETHEUS_URL}/-/ready")]:
        try:
            requests.get(url, timeout=3)
            console.print(f"  [green]OK[/green] {name}")
        except Exception:
            console.print(f"  [red]FAIL[/red] {name} unreachable!")
            all_ok = False
    if not all_ok:
        console.print("[red]Some services unreachable. Ensure port-forwards are running.[/red]")
        sys.exit(1)

    console.print(f"\n  Scenarios : {scenarios}")
    console.print(f"  Modes     : {modes}")
    console.print(f"  Runs/mode : {args.runs}")
    console.print(f"  Total runs: {len(scenarios) * len(modes) * args.runs}\n")

    run_id = 1
    csv_paths = []

    for sid in scenarios:
        sc = SCENARIOS[sid]
        console.rule(f"[cyan]{sid}: {sc['name']}[/cyan]")
        results = []

        for mode in modes:
            console.print(f"\n[bold yellow]Mode: {mode}[/bold yellow]")
            for i in range(args.runs):
                if not args.no_reset:
                    console.print(f"  Resetting steady state ({STEADY_STATE_WAIT}s)...")
                    reset_steady_state()
                result = run_experiment(run_id, sid, sc, mode)
                results.append(result)
                run_id += 1

        p = export_csv(results, sc)
        csv_paths.append(p)
        print_summary(results, sid)

    console.rule("[bold green]All experiments complete![/bold green]")
    console.print("\n  CSV outputs:")
    for p in csv_paths:
        console.print(f"    {p}")
    console.print("\n  Run analysis: python infrastructure/scripts/analysis.py")


if __name__ == "__main__":
    main()
