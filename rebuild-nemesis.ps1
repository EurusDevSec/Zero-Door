# =============================================================================
# ZERO DOOR -- Rebuild and Refresh Nemesis UI Agent
# Usage: .\rebuild-nemesis.ps1
# =============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   ZERO DOOR -- Rebuild & Redeploy Nemesis UI (No-Cache)   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Rebuild nemesis container image
Write-Host "[1/5] Rebuilding Nemesis Docker image (no-cache)..." -ForegroundColor Yellow
docker build --no-cache -t nemesis:latest agent-orchestrator/nemesis/
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL: Docker build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Nemesis image built." -ForegroundColor Green
Write-Host ""

# 2. Import image to K3d
Write-Host "[2/5] Importing image to K3d cluster 'zero-door'..." -ForegroundColor Yellow
k3d image import nemesis:latest -c zero-door
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL: K3d image import failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Image imported." -ForegroundColor Green
Write-Host ""

# 3. Rollout restart
Write-Host "[3/5] Restarting Nemesis deployment..." -ForegroundColor Yellow
kubectl rollout restart deployment/nemesis -n zero-door
kubectl rollout status deployment/nemesis -n zero-door --timeout=90s
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL: Rollout failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Rollout completed." -ForegroundColor Green
Write-Host ""

# 4. Clean old port-forward processes on port 9092
Write-Host "[4/5] Stopping old port-forward on port 9092..." -ForegroundColor Yellow
$ports = Get-NetTCPConnection -LocalPort 9092 -ErrorAction SilentlyContinue
if ($ports) {
    foreach ($p in $ports) {
        $proc = Get-Process -Id $p.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            $proc | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Host "  OK: Terminated process $($proc.Name) (PID $($proc.Id)) on port 9092" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  OK: Port 9092 is already free." -ForegroundColor Green
}
Start-Sleep -Seconds 2
Write-Host ""

# 5. Restart port-forward
Write-Host "[5/5] Launching new port-forward tunnel for Nemesis (9092:8000)..." -ForegroundColor Yellow
Start-Process -WindowStyle Hidden -FilePath "kubectl" -ArgumentList "port-forward svc/nemesis 9092:8000 -n zero-door"
Start-Sleep -Seconds 4
Write-Host "  OK: Port-forward active." -ForegroundColor Green
Write-Host ""

# Test endpoint
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:9092/healthz" -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -eq 200) {
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "   SUCCESS: Nemesis UI updated and reconnected!            " -ForegroundColor Green
        Write-Host "   Open dashboard at: http://localhost:9092/dashboard/      " -ForegroundColor White
        Write-Host "============================================================" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  WARN: Connection test failed. You may need to run: .\start-demo.ps1" -ForegroundColor Red
}
Write-Host ""
