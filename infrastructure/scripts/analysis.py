#!/usr/bin/env python3
"""
Zero Door — Phase 5 Data Analysis & Visualization
===================================================
Reads raw CSV files from docs/experiments/raw_data/, computes summary
statistics (MTTD, MTTR, uptime, FPR, heal success rate), and generates
publication-quality charts (bar, box, line).

Usage:
    python analysis.py                    # analyse all available CSVs
    python analysis.py --scenario E1      # analyse specific scenario
    python analysis.py --no-charts        # stats only, no matplotlib

Requirements:
    pip install pandas matplotlib scipy rich
"""

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for headless CI
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from rich.console import Console
from rich.table import Table

console = Console()

BASE_DIR      = Path(__file__).parent.parent.parent / "docs" / "experiments"
RAW_DIR       = BASE_DIR / "raw_data"
ANALYSIS_DIR  = BASE_DIR / "analysis"
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


SCENARIO_DIRS = {
    "E1": "e1_cpu_stress",
    "E2": "e2_http_flood",
    "E3": "e3_pod_kill",
    "E4": "e4_combined",
}

# Color palette
COLORS = {
    "AUTO":   "#4ECDC4",   # teal
    "MANUAL": "#FF6B6B",   # red
    "accent": "#FFE66D",   # yellow
    "bg":     "#1A1A2E",   # dark navy
    "grid":   "#2D2D44",
}


# ─────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────
def load_all_csvs(scenarios: Optional[list[str]] = None) -> pd.DataFrame:
    """Load all CSV files from raw_data/ and concatenate into one DataFrame."""
    dfs = []
    target_scenarios = scenarios or list(SCENARIO_DIRS.keys())
    for s in target_scenarios:
        d = RAW_DIR / SCENARIO_DIRS.get(s, s)
        if not d.exists():
            continue
        for csv_file in d.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                df["source_file"] = csv_file.name
                dfs.append(df)
            except Exception as e:
                console.print(f"[yellow]⚠ Skipping {csv_file.name}: {e}[/yellow]")
    if not dfs:
        return pd.DataFrame()
    combined = pd.concat(dfs, ignore_index=True)
    # Filter out failed triggers
    combined = combined[combined["mttd_seconds"] >= 0].copy()
    return combined


# ─────────────────────────────────────────────────────────────────
# Summary Statistics  (T5.9)
# ─────────────────────────────────────────────────────────────────
def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-scenario, per-mode summary statistics."""
    rows = []
    for scenario in df["scenario"].unique():
        for mode in df["mode"].unique():
            sub = df[(df["scenario"] == scenario) & (df["mode"] == mode)]
            if sub.empty:
                continue
            mttd = sub["mttd_seconds"].dropna()
            mttr = sub["mttr_seconds"].dropna()
            mttr = mttr[mttr >= 0]
            uptime = sub["uptime_percent"].dropna()

            n = len(sub)
            heal_ok = (sub["heal_status"].isin(["SUCCESS", "MANUAL"])).sum()
            fp = sub["false_positives"].sum()

            rows.append({
                "scenario":          scenario,
                "mode":              mode,
                "runs":              n,
                "mttd_mean":         round(mttd.mean(), 2) if not mttd.empty else None,
                "mttd_median":       round(mttd.median(), 2) if not mttd.empty else None,
                "mttd_p95":          round(mttd.quantile(0.95), 2) if not mttd.empty else None,
                "mttd_lt60_pct":     round((mttd < 60).mean() * 100, 1) if not mttd.empty else None,
                "mttr_mean":         round(mttr.mean(), 2) if not mttr.empty else None,
                "mttr_median":       round(mttr.median(), 2) if not mttr.empty else None,
                "mttr_p95":          round(mttr.quantile(0.95), 2) if not mttr.empty else None,
                "mttr_lt180_pct":    round((mttr < 180).mean() * 100, 1) if not mttr.empty else None,
                "uptime_mean_pct":   round(uptime.mean(), 2) if not uptime.empty else None,
                "heal_success_rate": round(heal_ok / n * 100, 1) if n > 0 else 0,
                "false_positive_rate": round(fp / max(n, 1) * 100, 1),
            })
    return pd.DataFrame(rows)


def print_stats_table(stats_df: pd.DataFrame):
    """Pretty-print the summary statistics using rich."""
    table = Table(
        title="📊 Phase 5 — Experiment Summary Statistics",
        show_header=True, header_style="bold cyan",
    )
    cols = [
        ("Scenario", "bold"), ("Mode", ""),
        ("Runs", ""), ("MTTD Mean", ""), ("MTTD Median", ""), ("MTTD P95", ""),
        ("MTTD <60s%", "green"), ("MTTR Mean", ""), ("MTTR <180s%", "green"),
        ("Uptime%", "bold green"), ("Heal OK%", "bold"),
    ]
    for name, style in cols:
        table.add_column(name, style=style)

    for _, row in stats_df.iterrows():
        table.add_row(
            row["scenario"], row["mode"],
            str(row["runs"]),
            f"{row['mttd_mean']}s"        if row["mttd_mean"]        is not None else "N/A",
            f"{row['mttd_median']}s"      if row["mttd_median"]      is not None else "N/A",
            f"{row['mttd_p95']}s"         if row["mttd_p95"]         is not None else "N/A",
            f"{row['mttd_lt60_pct']}%"    if row["mttd_lt60_pct"]    is not None else "N/A",
            f"{row['mttr_mean']}s"        if row["mttr_mean"]         is not None else "N/A",
            f"{row['mttr_lt180_pct']}%"   if row["mttr_lt180_pct"]   is not None else "N/A",
            f"{row['uptime_mean_pct']}%"  if row["uptime_mean_pct"]  is not None else "N/A",
            f"{row['heal_success_rate']}%",
        )
    console.print(table)


# ─────────────────────────────────────────────────────────────────
# Charts  (T5.10)
# ─────────────────────────────────────────────────────────────────
def _apply_dark_style(ax, title: str, xlabel: str, ylabel: str):
    ax.set_facecolor(COLORS["bg"])
    ax.figure.patch.set_facecolor(COLORS["bg"])
    ax.set_title(title, color="white", fontsize=13, pad=12)
    ax.set_xlabel(xlabel, color="#AAAAAA", fontsize=10)
    ax.set_ylabel(ylabel, color="#AAAAAA", fontsize=10)
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.spines["left"].set_color(COLORS["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)


def chart_mttd_comparison(stats_df: pd.DataFrame, out_dir: Path):
    """Bar chart: MTTD AUTO vs MANUAL per scenario."""
    scenarios = stats_df["scenario"].unique()
    auto_vals   = []
    manual_vals = []
    for s in scenarios:
        a = stats_df[(stats_df["scenario"] == s) & (stats_df["mode"] == "AUTO")]["mttd_mean"]
        m = stats_df[(stats_df["scenario"] == s) & (stats_df["mode"] == "MANUAL")]["mttd_mean"]
        auto_vals.append(float(a.iloc[0]) if not a.empty and a.iloc[0] is not None else 0)
        manual_vals.append(float(m.iloc[0]) if not m.empty and m.iloc[0] is not None else 0)

    x = np.arange(len(scenarios))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, auto_vals,   width, label="AUTO",   color=COLORS["AUTO"],   alpha=0.9)
    bars2 = ax.bar(x + width/2, manual_vals, width, label="MANUAL", color=COLORS["MANUAL"], alpha=0.9)
    ax.axhline(60, color=COLORS["accent"], linestyle="--", linewidth=1.2, label="Target: 60s")
    ax.bar_label(bars1, fmt="%.0fs", padding=3, color="white", fontsize=9)
    ax.bar_label(bars2, fmt="%.0fs", padding=3, color="white", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    _apply_dark_style(ax, "MTTD: Automated vs Manual", "Scenario", "Seconds")
    ax.legend(facecolor="#2D2D44", labelcolor="white")
    plt.tight_layout()
    path = out_dir / "mttd_comparison.png"
    plt.savefig(path, dpi=150)
    plt.close()
    console.print(f"  ✓ Chart: {path.name}")


def chart_mttr_comparison(stats_df: pd.DataFrame, out_dir: Path):
    """Bar chart: MTTR AUTO vs MANUAL per scenario."""
    scenarios = stats_df["scenario"].unique()
    auto_vals, manual_vals = [], []
    for s in scenarios:
        a = stats_df[(stats_df["scenario"] == s) & (stats_df["mode"] == "AUTO")]["mttr_mean"]
        m = stats_df[(stats_df["scenario"] == s) & (stats_df["mode"] == "MANUAL")]["mttr_mean"]
        auto_vals.append(float(a.iloc[0]) if not a.empty and a.iloc[0] is not None else 0)
        manual_vals.append(float(m.iloc[0]) if not m.empty and m.iloc[0] is not None else 0)

    x = np.arange(len(scenarios))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, auto_vals,   width, label="AUTO",   color=COLORS["AUTO"],   alpha=0.9)
    bars2 = ax.bar(x + width/2, manual_vals, width, label="MANUAL", color=COLORS["MANUAL"], alpha=0.9)
    ax.axhline(180, color=COLORS["accent"], linestyle="--", linewidth=1.2, label="Target: 180s")
    ax.bar_label(bars1, fmt="%.0fs", padding=3, color="white", fontsize=9)
    ax.bar_label(bars2, fmt="%.0fs", padding=3, color="white", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    _apply_dark_style(ax, "MTTR: Automated vs Manual", "Scenario", "Seconds")
    ax.legend(facecolor="#2D2D44", labelcolor="white")
    plt.tight_layout()
    path = out_dir / "mttr_comparison.png"
    plt.savefig(path, dpi=150)
    plt.close()
    console.print(f"  ✓ Chart: {path.name}")


def chart_boxplot_mttd(df: pd.DataFrame, out_dir: Path):
    """Box plot: MTTD distribution across all AUTO runs."""
    scenarios = sorted(df["scenario"].unique())
    data = [df[(df["scenario"] == s) & (df["mode"] == "AUTO")]["mttd_seconds"].dropna().tolist()
            for s in scenarios]
    data = [d for d in data if d]
    if not data:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color=COLORS["accent"], linewidth=2))
    for patch in bp["boxes"]:
        patch.set_facecolor(COLORS["AUTO"])
        patch.set_alpha(0.7)
    for whisker in bp["whiskers"]:
        whisker.set_color("#AAAAAA")
    for cap in bp["caps"]:
        cap.set_color("#AAAAAA")
    for flier in bp["fliers"]:
        flier.set(marker="o", color=COLORS["MANUAL"], alpha=0.6)
    ax.axhline(60, color=COLORS["accent"], linestyle="--", linewidth=1, label="Target: 60s")
    ax.set_xticklabels(scenarios)
    _apply_dark_style(ax, "MTTD Distribution — AUTO Mode", "Scenario", "Seconds")
    ax.legend(facecolor="#2D2D44", labelcolor="white")
    plt.tight_layout()
    path = out_dir / "mttd_boxplot.png"
    plt.savefig(path, dpi=150)
    plt.close()
    console.print(f"  ✓ Chart: {path.name}")


def chart_uptime_e4(df: pd.DataFrame, out_dir: Path):
    """Line chart: Uptime % per run for E4 Combined attack."""
    e4 = df[df["scenario"] == "E4"].copy()
    if e4.empty:
        return
    auto   = e4[e4["mode"] == "AUTO"]["uptime_percent"].reset_index(drop=True)
    manual = e4[e4["mode"] == "MANUAL"]["uptime_percent"].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9, 4))
    if not auto.empty:
        ax.plot(auto.index + 1, auto.values, color=COLORS["AUTO"],   marker="o", label="AUTO",   linewidth=1.5)
    if not manual.empty:
        ax.plot(manual.index + 1, manual.values, color=COLORS["MANUAL"], marker="s", label="MANUAL", linewidth=1.5)
    ax.axhline(95, color=COLORS["accent"], linestyle="--", linewidth=1, label="Target: 95%")
    _apply_dark_style(ax, "E4 Combined Attack — Uptime % per Run", "Run #", "Uptime (%)")
    ax.set_ylim(0, 105)
    ax.legend(facecolor="#2D2D44", labelcolor="white")
    plt.tight_layout()
    path = out_dir / "uptime_e4.png"
    plt.savefig(path, dpi=150)
    plt.close()
    console.print(f"  ✓ Chart: {path.name}")


def chart_heal_success_rate(stats_df: pd.DataFrame, out_dir: Path):
    """Horizontal bar chart: Heal success rate per scenario (AUTO only)."""
    auto = stats_df[stats_df["mode"] == "AUTO"].copy()
    if auto.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    scenarios = auto["scenario"].tolist()
    rates = auto["heal_success_rate"].tolist()
    bars = ax.barh(scenarios, rates, color=COLORS["AUTO"], alpha=0.85)
    ax.bar_label(bars, fmt="%.0f%%", padding=4, color="white", fontsize=10)
    ax.axvline(70, color=COLORS["accent"], linestyle="--", linewidth=1, label="Target: 70%")
    _apply_dark_style(ax, "Heal Success Rate — AUTO Mode", "Success Rate (%)", "Scenario")
    ax.set_xlim(0, 115)
    ax.legend(facecolor="#2D2D44", labelcolor="white")
    plt.tight_layout()
    path = out_dir / "heal_success_rate.png"
    plt.savefig(path, dpi=150)
    plt.close()
    console.print(f"  ✓ Chart: {path.name}")


# ─────────────────────────────────────────────────────────────────
# Export summary CSV  (master results)
# ─────────────────────────────────────────────────────────────────
def export_summary_csv(stats_df: pd.DataFrame):
    path = ANALYSIS_DIR / "summary_statistics.csv"
    stats_df.to_csv(path, index=False)
    console.print(f"  ✓ Summary CSV: {path}")


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Phase 5 — Data Analysis & Visualization")
    parser.add_argument("--scenario", nargs="+", choices=list(SCENARIO_DIRS.keys()),
                        help="Scenarios to analyse (default: all)")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    args = parser.parse_args()

    console.rule("[bold cyan]Zero Door Phase 5 — Data Analysis[/bold cyan]")

    df = load_all_csvs(args.scenario)
    if df.empty:
        console.print("[yellow]⚠ No data found. Run experiment_runner.py first.[/yellow]")
        return

    console.print(f"  Loaded {len(df)} experiment records\n")

    stats_df = compute_stats(df)
    print_stats_table(stats_df)
    export_summary_csv(stats_df)

    if not args.no_charts:
        console.print("\n[bold]Generating charts...[/bold]")
        chart_mttd_comparison(stats_df, ANALYSIS_DIR)
        chart_mttr_comparison(stats_df, ANALYSIS_DIR)
        chart_boxplot_mttd(df, ANALYSIS_DIR)
        chart_uptime_e4(df, ANALYSIS_DIR)
        chart_heal_success_rate(stats_df, ANALYSIS_DIR)
        console.print(f"\n  All charts saved to: {ANALYSIS_DIR}")

    console.rule("[green]Analysis complete[/green]")


if __name__ == "__main__":
    main()
