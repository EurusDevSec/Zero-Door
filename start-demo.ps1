# =============================================================================
# ZERO DOOR -- Script khoi dong toan bo Port-Forward cho buoi Demo
# Su dung: .\start-demo.ps1
# =============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   ZERO DOOR -- Khoi dong he thong Demo (One-Click Start)   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# [1] Kiem tra K3d cluster
Write-Host "[1/6] Kiem tra K3d cluster..." -ForegroundColor Yellow
$nodes = kubectl get nodes --no-headers 2>$null
if (-not $nodes) {
    Write-Host "  FAIL: Cluster chua san sang! Hay kiem tra Docker Desktop va K3d." -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Cluster dang chay:" -ForegroundColor Green
kubectl get nodes --no-headers | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }

# [2] Kiem tra pods
Write-Host ""
Write-Host "[2/6] Pods trong zero-door namespace:" -ForegroundColor Yellow
kubectl get pods -n zero-door --no-headers | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }

# [3] Don dep port-forward cu
Write-Host ""
Write-Host "[3/6] Don dep cac ket noi port-forward cu..." -ForegroundColor Yellow
$oldKubectl = Get-Process -Name "kubectl" -ErrorAction SilentlyContinue
if ($oldKubectl) {
    $oldKubectl | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  OK: Da tat $($oldKubectl.Count) tien trinh kubectl cu." -ForegroundColor Green
} else {
    Write-Host "  OK: Khong co tien trinh cu." -ForegroundColor Green
}

# [4] Khoi dong Port-Forward
Write-Host ""
Write-Host "[4/6] Khoi dong Port-Forward cho tat ca dich vu..." -ForegroundColor Yellow

Start-Process -WindowStyle Hidden -FilePath "kubectl" -ArgumentList "port-forward svc/nemesis 9092:8000 -n zero-door"
Write-Host "  [9092] Nemesis Agent (Control Center Dashboard) - STARTED" -ForegroundColor Green

Start-Process -WindowStyle Hidden -FilePath "kubectl" -ArgumentList "port-forward svc/hephaestus 9091:8000 -n zero-door"
Write-Host "  [9091] Hephaestus Agent (Defender)             - STARTED" -ForegroundColor Green

# Online Boutique Frontend is exposed natively on host port 8080 via Nginx Ingress
Write-Host "  [8080] Online Boutique Frontend (Target App Ingress) - READY" -ForegroundColor Green

Start-Process -WindowStyle Hidden -FilePath "kubectl" -ArgumentList "port-forward svc/prometheus-operated 9090:9090 -n monitoring"
Write-Host "  [9090] Prometheus (Monitoring)                 - STARTED" -ForegroundColor Green

Start-Process -WindowStyle Hidden -FilePath "kubectl" -ArgumentList "port-forward svc/prometheus-grafana 3000:80 -n monitoring"
Write-Host "  [3000] Grafana Dashboard (Obs Visualization)    - STARTED" -ForegroundColor Green

# [5] Cho ket noi on dinh
Write-Host ""
Write-Host "[5/6] Cho 6 giay de cac ket noi on dinh..." -ForegroundColor Yellow
Start-Sleep -Seconds 6

# [6] Kiem tra Nemesis API
Write-Host ""
Write-Host "[6/6] Kiem tra ket noi Nemesis API (health check)..." -ForegroundColor Yellow
$nemesisOK = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:9092/healthz" -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            Write-Host "  OK: Nemesis API phan hoi thanh cong! (lan $i)" -ForegroundColor Green
            $nemesisOK = $true
            break
        }
    } catch {
        Write-Host "  Thu lan $i that bai, thu lai sau 3 giay..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

if (-not $nemesisOK) {
    Write-Host "  WARN: Khong ket noi duoc Nemesis. Thu kiem tra: kubectl get pods -n zero-door" -ForegroundColor Red
}

# Ket qua
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   HE THONG SAN SANG! Mo trinh duyet tai:                  " -ForegroundColor Green
Write-Host ""
Write-Host "   Control Center:  http://localhost:9092/dashboard/       " -ForegroundColor White
Write-Host "   Target App:      http://localhost:8080                  " -ForegroundColor White
Write-Host "   Prometheus:      http://localhost:9090                  " -ForegroundColor White
Write-Host "   Grafana (3000):  http://localhost:3000                  " -ForegroundColor White
Write-Host "                    (User: admin / Pass: zerodoor123)       " -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Tu dong mo trinh duyet
$openBrowser = Read-Host "Tu dong mo trinh duyet? (y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:9092/dashboard/"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:8080"
    Write-Host "  OK: Da mo trinh duyet!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Nhan Enter de thoat (cac port-forward van chay ngam)..."
Read-Host
