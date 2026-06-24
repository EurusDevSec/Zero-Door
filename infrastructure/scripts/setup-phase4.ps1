#!/usr/bin/env pwsh
# =============================================================================
# Zero Door — Phase 4 Setup Script
# Builds and deploys: Agent Hephaestus (Blue Team / Self-Healing)
# =============================================================================
# Prerequisites: Phase 1 + 2 + 3 must be running
# Usage: pwsh -ExecutionPolicy Bypass -File setup-phase4.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$ROOT             = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$HEPHAESTUS_DIR   = "$ROOT\agent-orchestrator\hephaestus"
$MANIFESTS_DIR    = "$ROOT\infrastructure\manifests"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ZERO DOOR — Phase 4: Agent Hephaestus (Blue Team)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ---- Step 0: Prerequisites Check ----
Write-Host "[Step 0] Checking prerequisites..." -ForegroundColor Yellow

foreach ($tool in @("docker", "kubectl", "k3d")) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] '$tool' not found in PATH." -ForegroundColor Red
        exit 1
    }
}

$nodes = kubectl get nodes --no-headers 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] K3d cluster not reachable. Run setup-phase1.ps1 first." -ForegroundColor Red
    exit 1
}

$phase3Pods = kubectl get pods -n zero-door -l phase=3 --no-headers 2>&1
if ($phase3Pods -notmatch "Running") {
    Write-Host "[WARN] Phase 3 pods may not be running. Continuing anyway..." -ForegroundColor Yellow
}
Write-Host "[OK] Prerequisites satisfied." -ForegroundColor Green
Write-Host ""

# ---- Step 1: Build Docker image ----
Write-Host "[Step 1/3] Building Hephaestus Docker image..." -ForegroundColor Yellow

Push-Location $HEPHAESTUS_DIR
try {
    docker build -t hephaestus:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker build failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] hephaestus:latest built." -ForegroundColor Green
}
finally { Pop-Location }

Write-Host ""

# ---- Step 2: Import image into K3d ----
Write-Host "[Step 2/3] Importing image into K3d cluster..." -ForegroundColor Yellow
k3d image import hephaestus:latest -c zero-door
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to import image." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Image imported." -ForegroundColor Green
Write-Host ""

# ---- Step 3: Deploy manifests ----
Write-Host "[Step 3/3] Deploying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f "$MANIFESTS_DIR\hephaestus-deployment.yaml"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to apply hephaestus-deployment.yaml." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Manifests applied." -ForegroundColor Green
Write-Host ""

# Wait for rollout
Write-Host "Waiting for Hephaestus pod to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/hephaestus -n zero-door --timeout=120s

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Phase 4 Status" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
kubectl get pods -n zero-door
Write-Host ""

# RBAC Verification
Write-Host "Verifying RBAC (cross-namespace access)..." -ForegroundColor Yellow
$canTarget = kubectl auth can-i --as=system:serviceaccount:zero-door:hephaestus-sa delete pods -n target-app 2>&1
$canSystem = kubectl auth can-i --as=system:serviceaccount:zero-door:hephaestus-sa delete pods -n kube-system 2>&1
Write-Host "  target-app delete pods: $canTarget" -ForegroundColor $(if ($canTarget -eq "yes") { "Green" } else { "Red" })
Write-Host "  kube-system delete pods: $canSystem" -ForegroundColor $(if ($canSystem -eq "no") { "Green" } else { "Red" })
Write-Host ""

Write-Host "Quick test commands:" -ForegroundColor Cyan
Write-Host "  # Health check:" -ForegroundColor Gray
Write-Host "  curl http://localhost:8080/hephaestus/healthz" -ForegroundColor White
Write-Host ""
Write-Host "  # Manual SCALE_UP trigger:" -ForegroundColor Gray
Write-Host "  curl -X POST http://localhost:8080/hephaestus/heal/trigger \" -ForegroundColor White
Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor White
Write-Host "    -d '{""alertType"":""HIGH_CPU"",""severity"":""WARNING"",""affectedService"":""frontend""}'" -ForegroundColor White
Write-Host ""
Write-Host "  # Watch healing.actions topic:" -ForegroundColor Gray
Write-Host "  kubectl exec -n zero-door -it `$(kubectl get pod -n zero-door -l app.kubernetes.io/name=kafka -o name | Select-Object -First 1) -- kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic healing.actions --from-beginning" -ForegroundColor White
Write-Host ""
Write-Host "Phase 4 setup complete!" -ForegroundColor Green
