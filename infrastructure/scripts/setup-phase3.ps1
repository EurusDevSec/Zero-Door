#!/usr/bin/env pwsh
# =============================================================================
# Zero Door — Phase 3 Setup Script
# Builds and deploys: Chaos Worker (Go) + Agent Nemesis (Python)
# =============================================================================
# Prerequisites: Phase 1 + Phase 2 must be running
# Usage: pwsh -ExecutionPolicy Bypass -File setup-phase3.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CHAOS_WORKER_DIR = "$ROOT\chaos-worker"
$NEMESIS_DIR      = "$ROOT\agent-orchestrator\nemesis"
$MANIFESTS_DIR    = "$ROOT\infrastructure\manifests"

Write-Host ""
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  ZERO DOOR — Phase 3: Nemesis + Chaos Worker" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

# ---- Step 0: Prerequisites Check ----
Write-Host "[Step 0] Checking prerequisites..." -ForegroundColor Yellow

$tools = @("docker", "kubectl", "k3d")
foreach ($tool in $tools) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Required tool '$tool' is not found in PATH." -ForegroundColor Red
        exit 1
    }
}

# Verify cluster is running
$nodes = kubectl get nodes --no-headers 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cannot reach K3d cluster. Run setup-phase1.ps1 first." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Cluster is running." -ForegroundColor Green

# Verify Phase 2 target app is running
$targetPods = kubectl get pods -n target-app --no-headers 2>&1
if ($LASTEXITCODE -ne 0 -or $targetPods -notmatch "Running") {
    Write-Host "[WARN] Target app may not be fully running. Continuing..." -ForegroundColor Yellow
}

Write-Host ""

# ---- Step 1: Build Chaos Worker Docker image ----
Write-Host "[Step 1/4] Building Chaos Worker (Go) Docker image..." -ForegroundColor Yellow

Push-Location $CHAOS_WORKER_DIR
try {
    # Download dependencies first (go mod tidy requires Go installed)
    if (Get-Command go -ErrorAction SilentlyContinue) {
        Write-Host "  Running go mod tidy..." -ForegroundColor Cyan
        go mod tidy
        if ($LASTEXITCODE -ne 0) { Write-Host "[WARN] go mod tidy failed — continuing with Docker build" -ForegroundColor Yellow }
    }

    Write-Host "  Building Docker image: chaos-worker:latest" -ForegroundColor Cyan
    docker build -t chaos-worker:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker build for chaos-worker failed." -ForegroundColor Red
        exit 1
    }

    Write-Host "  Importing image into K3d cluster..." -ForegroundColor Cyan
    k3d image import chaos-worker:latest -c zero-door
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to import chaos-worker image into K3d." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] chaos-worker:latest built and imported." -ForegroundColor Green
}
finally {
    Pop-Location
}

Write-Host ""

# ---- Step 2: Build Nemesis Docker image ----
Write-Host "[Step 2/4] Building Nemesis Agent (Python) Docker image..." -ForegroundColor Yellow

Push-Location $NEMESIS_DIR
try {
    Write-Host "  Building Docker image: nemesis:latest" -ForegroundColor Cyan
    docker build -t nemesis:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker build for nemesis failed." -ForegroundColor Red
        exit 1
    }

    Write-Host "  Importing image into K3d cluster..." -ForegroundColor Cyan
    k3d image import nemesis:latest -c zero-door
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to import nemesis image into K3d." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] nemesis:latest built and imported." -ForegroundColor Green
}
finally {
    Pop-Location
}

Write-Host ""

# ---- Step 3: Deploy Kubernetes manifests ----
Write-Host "[Step 3/4] Deploying Kubernetes manifests..." -ForegroundColor Yellow

Write-Host "  Applying Chaos Worker manifests (RBAC + Deployment)..." -ForegroundColor Cyan
kubectl apply -f "$MANIFESTS_DIR\chaos-worker.yaml"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to apply chaos-worker.yaml." -ForegroundColor Red
    exit 1
}

Write-Host "  Applying Nemesis manifests (Deployment + Service + Ingress)..." -ForegroundColor Cyan
kubectl apply -f "$MANIFESTS_DIR\nemesis-deployment.yaml"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to apply nemesis-deployment.yaml." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Manifests applied." -ForegroundColor Green
Write-Host ""

# ---- Step 4: Wait for pods to be ready ----
Write-Host "[Step 4/4] Waiting for Phase 3 pods to be ready..." -ForegroundColor Yellow

Write-Host "  Waiting for chaos-worker pod..." -ForegroundColor Cyan
kubectl rollout status deployment/chaos-worker -n zero-door --timeout=120s
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] chaos-worker rollout timed out. Check logs:" -ForegroundColor Yellow
    Write-Host "  kubectl logs -n zero-door -l app=chaos-worker --tail=50" -ForegroundColor Gray
}

Write-Host "  Waiting for nemesis pod..." -ForegroundColor Cyan
kubectl rollout status deployment/nemesis -n zero-door --timeout=120s
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] nemesis rollout timed out. Check logs:" -ForegroundColor Yellow
    Write-Host "  kubectl logs -n zero-door -l app=nemesis --tail=50" -ForegroundColor Gray
}

Write-Host ""

# ---- Final status ----
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  Phase 3 Deployment Summary" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

kubectl get pods -n zero-door -l phase=3
Write-Host ""

Write-Host "Quick test commands:" -ForegroundColor Cyan
Write-Host "  # Check Nemesis health:" -ForegroundColor Gray
Write-Host "  curl http://localhost:8080/nemesis/healthz" -ForegroundColor White
Write-Host ""
Write-Host "  # Manually trigger HTTP Flood attack:" -ForegroundColor Gray
Write-Host "  curl -X POST http://localhost:8080/nemesis/attack/trigger \" -ForegroundColor White
Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor White
Write-Host "    -d '{""attackType"":""HTTP_FLOOD"",""targetService"":""frontend"",""durationSec"":20,""intensity"":""LOW"",""concurrency"":5}'" -ForegroundColor White
Write-Host ""
Write-Host "  # LLM-powered attack plan:" -ForegroundColor Gray
Write-Host "  curl -X POST http://localhost:8080/nemesis/attack/llm-plan" -ForegroundColor White
Write-Host ""
Write-Host "  # Watch attack results in Kafka:" -ForegroundColor Gray
Write-Host "  kubectl exec -n zero-door -it \$(kubectl get pod -n zero-door -l app.kubernetes.io/name=kafka -o name | head -1) -- kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic attack.results --from-beginning" -ForegroundColor White
Write-Host ""
Write-Host "Phase 3 setup complete!" -ForegroundColor Green
