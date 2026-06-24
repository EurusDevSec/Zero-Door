# ============================================================
# Zero Door - Recreate Cluster & Infrastructure Helper Script
# ============================================================
# This script completely deletes the existing K3d cluster
# and redeploys the Phase 1 environment from scratch.
# Use this script when Docker restarts and node IP shifts
# cause internal cluster TLS validation errors.
# ============================================================

$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SETUP_SCRIPT = "$PSScriptRoot\setup-phase1.ps1"

Write-Host "========================================" -ForegroundColor Red
Write-Host " ZERO DOOR - Recreating Cluster from Scratch" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "[Step 1/2] Deleting existing K3d cluster..." -ForegroundColor Yellow
k3d cluster delete zero-door

Write-Host ""
Write-Host "[Step 2/2] Triggering full Phase 1 setup..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File $SETUP_SCRIPT

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Cluster Recreated and Reprovisioned!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
