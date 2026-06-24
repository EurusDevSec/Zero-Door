# ============================================================
# Zero Door - Phase 1 Setup Script (PowerShell / Windows)
# ============================================================
# This script automates Phase 1 infrastructure setup:
#   1. Create K3d Cluster
#   2. Create namespaces & apply quotas
#   3. Deploy Kafka (Bitnami Helm)
#   4. Deploy Prometheus + Grafana (kube-prometheus-stack)
#   5. Deploy Nginx Ingress
#   6. Deploy Elasticsearch + Fluent Bit
#   7. Apply NetworkPolicies
# ============================================================

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$INFRA = "$ROOT\infrastructure"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ZERO DOOR - Phase 1 Infrastructure Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---- Step 0: Prerequisites Check ----
Write-Host "[Step 0] Checking prerequisites..." -ForegroundColor Yellow
$tools = @("docker", "k3d", "kubectl", "helm")
foreach ($tool in $tools) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "  ERROR: '$tool' not found. Please install it first." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK: $tool found" -ForegroundColor Green
}

# Check if Docker daemon is running
Write-Host "  Checking if Docker daemon is running..." -ForegroundColor DarkYellow
try {
    $dockerCheck = docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Docker daemon is not running! Please open Docker Desktop." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK: Docker daemon is responsive." -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker daemon is not running! Please open Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check for host port conflicts for ports 8080 and 8443 (mapped in k3d-config.yaml)
Write-Host "  Checking if host ports 8080 and 8443 are free..." -ForegroundColor DarkYellow
$ports = @(8080, 8443)
foreach ($port in $ports) {
    $portUsed = $null
    try {
        $portUsed = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    } catch {}
    if ($portUsed) {
        Write-Host "  WARNING: Port $port is already in use by another process on your host!" -ForegroundColor Yellow
        Write-Host "  This may cause K3d cluster loadbalancer port conflicts. Please close the application using port $port." -ForegroundColor Yellow
    } else {
        Write-Host "  OK: Port $port is free." -ForegroundColor Green
    }
}

# ---- Step 1: Create K3d Cluster ----
Write-Host ""
Write-Host "[Step 1] Creating K3d cluster 'zero-door'..." -ForegroundColor Yellow
$clusterExists = k3d cluster list -o json 2>$null | ConvertFrom-Json | Where-Object { $_.name -eq "zero-door" }
if ($clusterExists) {
    Write-Host "  Cluster 'zero-door' already exists. Skipping creation." -ForegroundColor DarkYellow
} else {
    k3d cluster create --config "$INFRA\k3d-config.yaml"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create K3d cluster." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Cluster created successfully." -ForegroundColor Green
}

# Failsafe: Fix Docker Desktop host.docker.internal connection issues on Windows
Write-Host "  Applying Windows localhost connection failsafe..." -ForegroundColor DarkYellow
$currentServer = kubectl config view -o jsonpath='{.clusters[0].cluster.server}'
if ($currentServer -like "*host.docker.internal*") {
    $port = $currentServer.Split(":")[-1]
    kubectl config set-cluster k3d-zero-door --server="https://127.0.0.1:$port"
    Write-Host "  Updated cluster server address to 127.0.0.1:$port" -ForegroundColor Green
}

# Warmup check: Wait for API server to become ready
Write-Host "  Waiting for Kubernetes API server to become ready..." -ForegroundColor DarkYellow
$apiReady = $false
for ($i = 1; $i -le 10; $i++) {
    & kubectl get nodes >$null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $apiReady = $true
        break
    }
    Write-Host "    [Attempt $i/10] API server not ready yet. Waiting 5 seconds..." -ForegroundColor DarkYellow
    Start-Sleep -Seconds 5
}
if (-not $apiReady) {
    Write-Host "  ERROR: Kubernetes API server failed to respond. Please check Docker/WSL2 resource allocations (min 8GB RAM recommended)." -ForegroundColor Red
    exit 1
}
Write-Host "  OK: API server is ready." -ForegroundColor Green

# Verify kubectl context
kubectl cluster-info
Write-Host ""

# ---- Step 2: Create Namespaces ----
Write-Host "[Step 2] Creating Kubernetes namespaces..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\namespaces\zero-door.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to create namespaces." -ForegroundColor Red; exit 1 }
kubectl apply -f "$INFRA\namespaces\target-app.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to create namespaces." -ForegroundColor Red; exit 1 }
kubectl apply -f "$INFRA\namespaces\monitoring.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to create namespaces." -ForegroundColor Red; exit 1 }
Write-Host "  Namespaces created." -ForegroundColor Green

# ---- Step 3: Apply ResourceQuotas & LimitRanges ----
Write-Host ""
Write-Host "[Step 3] Applying ResourceQuotas and LimitRanges..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\resource-quotas\zero-door-quota.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to apply resource-quotas." -ForegroundColor Red; exit 1 }
kubectl apply -f "$INFRA\resource-quotas\target-app-quota.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to apply resource-quotas." -ForegroundColor Red; exit 1 }
kubectl apply -f "$INFRA\resource-quotas\monitoring-quota.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Failed to apply resource-quotas." -ForegroundColor Red; exit 1 }
Write-Host "  ResourceQuotas applied." -ForegroundColor Green

# ---- Step 4: Add Helm Repos ----
Write-Host ""
Write-Host "[Step 4] Adding Helm repositories..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>$null
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>$null
helm repo update
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Helm repository update failed. Verify internet connection." -ForegroundColor Yellow
} else {
    Write-Host "  Helm repos updated." -ForegroundColor Green
}

# ---- Step 5: Deploy Prometheus + Grafana ----
Write-Host ""
Write-Host "[Step 5] Deploying Prometheus + Grafana to 'monitoring' namespace..." -ForegroundColor Yellow
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack `
    -n monitoring `
    -f "$INFRA\helm-values\prometheus-values.yaml" `
    --wait --timeout 5m
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Prometheus deployment failed. If stuck, run: helm rollback prometheus -n monitoring or helm uninstall prometheus -n monitoring." -ForegroundColor Red
    exit 1
}
Write-Host "  Prometheus + Grafana deployed." -ForegroundColor Green

# ---- Step 6: Deploy Apache Kafka (Bitnami KRaft mode) ----
Write-Host ""
Write-Host "[Step 6] Deploying Apache Kafka to 'zero-door' namespace..." -ForegroundColor Yellow
helm upgrade --install kafka oci://registry-1.docker.io/bitnamicharts/kafka `
    --version "29.3.2" `
    -n zero-door `
    -f "$INFRA\helm-values\kafka-values.yaml" `
    --wait --timeout 5m
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Kafka deployment failed. If stuck, run: helm rollback kafka -n zero-door or helm uninstall kafka -n zero-door." -ForegroundColor Red
    exit 1
}
Write-Host "  Kafka deployed." -ForegroundColor Green

# ---- Step 7: Deploy Nginx Ingress Controller ----
Write-Host ""
Write-Host "[Step 7] Deploying Nginx Ingress Controller..." -ForegroundColor Yellow
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx `
    -n kube-system `
    -f "$INFRA\helm-values\ingress-nginx-values.yaml" `
    --wait --timeout 5m
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Nginx Ingress deployment failed. If stuck, run: helm rollback ingress-nginx -n kube-system or helm uninstall ingress-nginx -n kube-system." -ForegroundColor Red
    exit 1
}
Write-Host "  Nginx Ingress Controller deployed." -ForegroundColor Green

# ---- Step 8: Deploy Elasticsearch ----
Write-Host ""
Write-Host "[Step 8] Deploying Elasticsearch..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\logging\elasticsearch.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Elasticsearch apply failed." -ForegroundColor Red; exit 1 }
Write-Host "  Elasticsearch deployed." -ForegroundColor Green

# ---- Step 9: Deploy Fluent Bit ----
Write-Host ""
Write-Host "[Step 9] Deploying Fluent Bit..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\logging\fluent-bit.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Fluent Bit apply failed." -ForegroundColor Red; exit 1 }
Write-Host "  Fluent Bit deployed." -ForegroundColor Green

# ---- Step 10: Apply Network Policies ----
Write-Host ""
Write-Host "[Step 10] Applying Network Policies..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\manifests\network-policies.yaml"
if ($LASTEXITCODE -ne 0) { Write-Host "  ERROR: Network Policies apply failed." -ForegroundColor Red; exit 1 }
Write-Host "  Network Policies applied." -ForegroundColor Green

# ---- Step 11: Wait for pods ----
Write-Host ""
Write-Host "[Step 11] Waiting for pods to be ready (this may take 3-5 minutes)..." -ForegroundColor Yellow
Write-Host "  Checking kube-system namespace (Ingress)..." -ForegroundColor DarkYellow
kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=ingress-nginx -n kube-system --timeout=300s 2>$null
Write-Host "  Checking zero-door namespace..." -ForegroundColor DarkYellow
kubectl wait --for=condition=Ready pods --all -n zero-door --timeout=300s 2>$null
Write-Host "  Checking monitoring namespace..." -ForegroundColor DarkYellow
kubectl wait --for=condition=Ready pods --all -n monitoring --timeout=300s 2>$null

# ---- Step 12: Final Status Report ----
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DEPLOYMENT STATUS REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "--- Namespaces ---" -ForegroundColor White
kubectl get ns zero-door target-app monitoring

Write-Host ""
Write-Host "--- Pods (All Namespaces) ---" -ForegroundColor White
kubectl get pods -n zero-door
kubectl get pods -n monitoring
kubectl get pods -n kube-system -l app.kubernetes.io/name=ingress-nginx

Write-Host ""
Write-Host "--- ResourceQuotas ---" -ForegroundColor White
kubectl describe resourcequota -n zero-door | Select-String -Pattern "Name:|Used|Hard"
kubectl describe resourcequota -n monitoring | Select-String -Pattern "Name:|Used|Hard"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Phase 1 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Grafana:  kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
Write-Host "  -> Open: http://localhost:3000  (admin / zerodoor123)"
Write-Host "Access Prometheus: kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring"
Write-Host "  -> Open: http://localhost:9090"
Write-Host "Check Elasticsearch: kubectl port-forward svc/elasticsearch 9200:9200 -n monitoring"
Write-Host "  -> curl http://localhost:9200/_cat/health"
Write-Host "Check Kafka Topics: kubectl exec -n zero-door kafka-controller-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092"
Write-Host ""
