# =============================================================
# Zero Door — Phase 5 Setup Script
# War Game Experiments & Data Collection
# =============================================================
# Usage:
#   .\setup-phase5.ps1                   # Full setup + run E1 smoke test
#   .\setup-phase5.ps1 -SkipExperiments  # Setup only, no experiment runs
# =============================================================

param(
    [switch]$SkipExperiments,
    [int]$SmokeRuns = 2
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$msg) {
    Write-Host "`n[STEP] $msg" -ForegroundColor Cyan
}
function Write-OK([string]$msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}
function Write-Warn([string]$msg) {
    Write-Host "  [WARN] $msg" -ForegroundColor Yellow
}

Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  Zero Door — Phase 5: War Game Experiments" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta

# ─────────────────────────────────────────────────────────────────
# Step 1: Verify cluster and Phase 4 dependencies
# ─────────────────────────────────────────────────────────────────
Write-Step "Verifying cluster and Phase 1-4 components..."

$pods = kubectl get pods -n zero-door --no-headers 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] K3d cluster not running. Start Docker Desktop and retry." -ForegroundColor Red
    exit 1
}

foreach ($required in @("gaia","hephaestus","nemesis","kafka","chaos-worker")) {
    if ($pods | Select-String -Pattern "$required.*Running") {
        Write-OK "$required is Running"
    } else {
        Write-Warn "$required not found or not Running — Phase 4 may not be complete"
    }
}

# ─────────────────────────────────────────────────────────────────
# Step 2: Create experiment directory structure
# ─────────────────────────────────────────────────────────────────
Write-Step "Creating experiment data directories..."

$dirs = @(
    "docs/experiments/raw_data/e1_cpu_stress",
    "docs/experiments/raw_data/e2_http_flood",
    "docs/experiments/raw_data/e3_pod_kill",
    "docs/experiments/raw_data/e4_combined",
    "docs/experiments/analysis",
    "docs/experiments/screenshots"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}
Write-OK "Directory structure ready under docs/experiments/"

# ─────────────────────────────────────────────────────────────────
# Step 3: Install Python analysis requirements
# ─────────────────────────────────────────────────────────────────
Write-Step "Installing Python analysis dependencies..."

$req = @(
    "kafka-python==2.0.2",
    "requests>=2.31.0",
    "rich>=13.0.0",
    "pandas>=2.0.0",
    "matplotlib>=3.7.0",
    "scipy>=1.11.0",
    "numpy>=1.24.0"
)

foreach ($pkg in $req) {
    pip install $pkg --quiet 2>&1 | Out-Null
}
Write-OK "Python packages installed"

# ─────────────────────────────────────────────────────────────────
# Step 4: Port-forward services for experiment runner
# ─────────────────────────────────────────────────────────────────
Write-Step "Setting up port-forwards for experiment tools..."

# Kill existing port-forwards on these ports
@(9091, 9092, 9093, 9090) | ForEach-Object {
    $pid = (netstat -ano | Select-String ":$_.*LISTENING" | ForEach-Object { ($_ -split "\s+")[-1] } | Select-Object -First 1)
    if ($pid) { 
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep 2

# Port-forwards as background jobs
$pfJobs = @()
$pfJobs += Start-Job { kubectl port-forward svc/hephaestus 9091:8000 -n zero-door 2>&1 }
$pfJobs += Start-Job { kubectl port-forward svc/nemesis 9092:8000 -n zero-door 2>&1 }
$pfJobs += Start-Job { kubectl port-forward svc/kafka 9093:9092 -n zero-door 2>&1 }
$pfJobs += Start-Job { kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring 2>&1 }

Start-Sleep 5
Write-OK "Port-forwards started:"
Write-Host "    Hephaestus : http://localhost:9091" -ForegroundColor Gray
Write-Host "    Nemesis    : http://localhost:9092" -ForegroundColor Gray
Write-Host "    Kafka      : localhost:9093" -ForegroundColor Gray
Write-Host "    Prometheus : http://localhost:9090" -ForegroundColor Gray

# ─────────────────────────────────────────────────────────────────
# Step 5: Verify Nemesis API
# ─────────────────────────────────────────────────────────────────
Write-Step "Verifying Nemesis API health..."
try {
    $health = Invoke-RestMethod "http://localhost:9092/healthz" -Method GET -TimeoutSec 5
    Write-OK "Nemesis: status=$($health.status)"
} catch {
    Write-Warn "Nemesis not responding — experiment_runner.py will record TRIGGER_FAILED"
}

# ─────────────────────────────────────────────────────────────────
# Step 6: Verify Hephaestus API
# ─────────────────────────────────────────────────────────────────
Write-Step "Verifying Hephaestus API health..."
try {
    $hh = Invoke-RestMethod "http://localhost:9091/healthz" -Method GET -TimeoutSec 5
    Write-OK "Hephaestus: status=$($hh.status) | k8s=$($hh.k8s_connected) | kafka=$($hh.kafka_connected)"
} catch {
    Write-Warn "Hephaestus not responding"
}

# ─────────────────────────────────────────────────────────────────
# Step 7: Smoke test — E1, 2 runs, AUTO mode
# ─────────────────────────────────────────────────────────────────
if (-not $SkipExperiments) {
    Write-Step "Running Phase 5 smoke test (E1, AUTO, $SmokeRuns runs)..."
    Write-Warn "Full 120-run experiment takes ~2-4 hours. This is a $SmokeRuns-run smoke test."

    $env:NEMESIS_URL     = "http://localhost:9092"
    $env:HEPHAESTUS_URL  = "http://localhost:9091"
    $env:PROMETHEUS_URL  = "http://localhost:9090"
    $env:KAFKA_BOOTSTRAP = "localhost:9093"
    $env:STEADY_STATE_WAIT_SEC = "15"

    python infrastructure/scripts/experiment_runner.py `
        --scenario E1 `
        --mode AUTO `
        --runs $SmokeRuns `
        --skip-steady-state 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-OK "Smoke test complete — CSV exported to docs/experiments/raw_data/e1_cpu_stress/"
    } else {
        Write-Warn "Smoke test had errors (Kafka/Nemesis might be unreachable). Check port-forwards."
    }

    # Run analysis if CSVs exist
    Write-Step "Generating analysis from smoke test data..."
    python infrastructure/scripts/analysis.py --no-charts 2>&1
}

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
Write-Host "`n============================================================" -ForegroundColor Magenta
Write-Host "  Phase 5 Setup Complete!" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "To run the full 120-run experiment suite:" -ForegroundColor White
Write-Host "  `$env:STEADY_STATE_WAIT_SEC='30'" -ForegroundColor Gray
Write-Host "  python infrastructure/scripts/experiment_runner.py --scenario ALL --mode BOTH --runs 15" -ForegroundColor Gray
Write-Host ""
Write-Host "To generate charts from collected data:" -ForegroundColor White
Write-Host "  python infrastructure/scripts/analysis.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Port-forwards are running in background jobs. To stop:" -ForegroundColor White
Write-Host "  Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Gray
