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

# ---- Step 1: Create K3d Cluster ----
Write-Host ""
Write-Host "[Step 1] Creating K3d cluster 'zero-door'..." -ForegroundColor Yellow
$clusterExists = k3d cluster list -o json 2>$null | ConvertFrom-Json | Where-Object { $_.name -eq "zero-door" }
if ($clusterExists) {
    Write-Host "  Cluster 'zero-door' already exists. Skipping creation." -ForegroundColor DarkYellow
} else {
    k3d cluster create --config "$INFRA\k3d-config.yaml"
    Write-Host "  Cluster created successfully." -ForegroundColor Green
}

# Verify kubectl context
kubectl cluster-info
Write-Host ""

# ---- Step 2: Create Namespaces ----
Write-Host "[Step 2] Creating Kubernetes namespaces..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\namespaces\zero-door.yaml"
kubectl apply -f "$INFRA\namespaces\target-app.yaml"
kubectl apply -f "$INFRA\namespaces\monitoring.yaml"
Write-Host "  Namespaces created." -ForegroundColor Green

# ---- Step 3: Apply ResourceQuotas & LimitRanges ----
Write-Host ""
Write-Host "[Step 3] Applying ResourceQuotas and LimitRanges..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\resource-quotas\zero-door-quota.yaml"
kubectl apply -f "$INFRA\resource-quotas\target-app-quota.yaml"
kubectl apply -f "$INFRA\resource-quotas\monitoring-quota.yaml"
Write-Host "  ResourceQuotas applied." -ForegroundColor Green

# ---- Step 4: Add Helm Repos ----
Write-Host ""
Write-Host "[Step 4] Adding Helm repositories..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>$null
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>$null
helm repo update
Write-Host "  Helm repos updated." -ForegroundColor Green

# ---- Step 5: Deploy Apache Kafka (Bitnami KRaft mode) ----
Write-Host ""
Write-Host "[Step 5] Deploying Apache Kafka to 'zero-door' namespace..." -ForegroundColor Yellow
helm upgrade --install kafka oci://registry-1.docker.io/bitnamicharts/kafka `
    -n zero-door `
    -f "$INFRA\helm-values\kafka-values.yaml" `
    --wait --timeout 5m
Write-Host "  Kafka deployed." -ForegroundColor Green

# ---- Step 6: Deploy Prometheus + Grafana ----
Write-Host ""
Write-Host "[Step 6] Deploying Prometheus + Grafana to 'monitoring' namespace..." -ForegroundColor Yellow
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack `
    -n monitoring `
    -f "$INFRA\helm-values\prometheus-values.yaml" `
    --wait --timeout 5m
Write-Host "  Prometheus + Grafana deployed." -ForegroundColor Green

# ---- Step 7: Deploy Nginx Ingress Controller ----
Write-Host ""
Write-Host "[Step 7] Deploying Nginx Ingress Controller..." -ForegroundColor Yellow
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx `
    -n kube-system `
    -f "$INFRA\helm-values\ingress-nginx-values.yaml" `
    --wait --timeout 5m
Write-Host "  Nginx Ingress Controller deployed." -ForegroundColor Green

# ---- Step 8: Deploy Elasticsearch ----
Write-Host ""
Write-Host "[Step 8] Deploying Elasticsearch..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\logging\elasticsearch.yaml"
Write-Host "  Elasticsearch deployed." -ForegroundColor Green

# ---- Step 9: Deploy Fluent Bit ----
Write-Host ""
Write-Host "[Step 9] Deploying Fluent Bit..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\logging\fluent-bit.yaml"
Write-Host "  Fluent Bit deployed." -ForegroundColor Green

# ---- Step 10: Apply Network Policies ----
Write-Host ""
Write-Host "[Step 10] Applying Network Policies..." -ForegroundColor Yellow
kubectl apply -f "$INFRA\manifests\network-policies.yaml"
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
