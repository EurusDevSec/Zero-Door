#!/usr/bin/env bash
# =============================================================================
# Zero-Door Cloud Deploy Script
# Chạy tự động trên DigitalOcean Droplet (Ubuntu 22.04) khi boot lần đầu.
# Tất cả bước đã được tối ưu dựa trên kinh nghiệm deploy lần 1.
#
# Cách dùng thủ công (nếu cần):
#   GITHUB_PAT="ghp_xxxx" bash /opt/zero-door/deploy.sh
# =============================================================================
set -euo pipefail

LOG="/var/log/zero-door-deploy.log"
exec > >(tee -a "$LOG") 2>&1

GITHUB_PAT="${GITHUB_PAT:-}"
GITHUB_USER="EurusDevSec"
GITHUB_EMAIL="eurusdevsec@gmail.com"
REGISTRY="ghcr.io/eurusdevsec/zero-door"
INFRA_DIR="/opt/zero-door/infrastructure"

echo "================================================================"
echo " ZERO-DOOR CLOUD DEPLOY — $(date)"
echo "================================================================"

# ── Kiểm tra prerequisite ──────────────────────────────────────────
if [[ -z "$GITHUB_PAT" ]]; then
  echo "[ERROR] GITHUB_PAT environment variable is required!"
  exit 1
fi

# ── Cập nhật hệ thống ─────────────────────────────────────────────
echo "[1/12] Updating system packages..."
apt-get update -qq
apt-get install -y -qq curl git python3 python3-pip ca-certificates

# ── Cài K3s (disable Traefik để dùng Nginx Ingress) ───────────────
echo "[2/12] Installing K3s (--disable traefik)..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644 --disable traefik

# Chờ K3s sẵn sàng
echo "  Waiting for K3s to be ready..."
for i in $(seq 1 30); do
  if kubectl get nodes 2>/dev/null | grep -q "Ready"; then
    echo "  K3s is Ready!"
    break
  fi
  sleep 3
done

# Bài học #1: Symlink kubeconfig ngay — Helm cần file này
echo "[2b] Creating kubeconfig symlink for Helm..."
mkdir -p /root/.kube
ln -sf /etc/rancher/k3s/k3s.yaml /root/.kube/config
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# ── Cài Helm ──────────────────────────────────────────────────────
echo "[3/12] Installing Helm..."
curl -sfL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# ── Tạo Namespaces ────────────────────────────────────────────────
echo "[4/12] Creating namespaces..."
kubectl create namespace zero-door   2>/dev/null || true
kubectl create namespace target-app  2>/dev/null || true
kubectl create namespace monitoring  2>/dev/null || true

# ── Tạo imagePullSecret cho GHCR ──────────────────────────────────
# Bài học #2: Cần secret ở CẢ HAI namespace (zero-door và target-app)
echo "[4b] Creating GHCR imagePullSecret in both namespaces..."
for ns in zero-door target-app; do
  kubectl delete secret ghcr-secret -n "$ns" 2>/dev/null || true
  kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username="$GITHUB_USER" \
    --docker-password="$GITHUB_PAT" \
    --docker-email="$GITHUB_EMAIL" \
    -n "$ns"
done

# ── Xóa Traefik HelmCharts cũ (nếu còn) ──────────────────────────
echo "[4c] Removing Traefik HelmCharts if present..."
kubectl delete helmcharts.helm.cattle.io traefik traefik-crd -n kube-system 2>/dev/null || true
sleep 5

# ── Cài Nginx Ingress Controller ──────────────────────────────────
# Bài học #3: Nginx Ingress thay Traefik để compatibility 100% với manifests
echo "[5/12] Installing Nginx Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

echo "  Waiting for Nginx Ingress Controller to be ready..."
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=ingress-nginx \
  -n ingress-nginx \
  --timeout=120s

# ── Thêm Helm repos ───────────────────────────────────────────────
echo "[6/12] Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# ── Apply ResourceQuotas ──────────────────────────────────────────
echo "[6b] Applying ResourceQuotas..."
kubectl apply -f "$INFRA_DIR/resource-quotas/zero-door-quota.yaml"
kubectl apply -f "$INFRA_DIR/resource-quotas/target-app-quota.yaml"
kubectl apply -f "$INFRA_DIR/resource-quotas/monitoring-quota.yaml"

# ── Deploy Prometheus + Grafana ───────────────────────────────────
echo "[7/12] Deploying Prometheus + Grafana via Helm..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f "$INFRA_DIR/helm-values/prometheus-values.yaml"

# ── Deploy Kafka (Bitnami KRaft) ──────────────────────────────────
echo "[8/12] Deploying Kafka (KRaft mode) via Helm..."
helm upgrade --install kafka \
  oci://registry-1.docker.io/bitnamicharts/kafka \
  --version "29.3.2" \
  -n zero-door \
  -f "$INFRA_DIR/helm-values/kafka-values.yaml"

# ── Deploy Target App (Google Boutique) ───────────────────────────
echo "[9/12] Deploying Google Boutique (target-app)..."
kubectl apply -f "$INFRA_DIR/manifests/target-app.yaml"
kubectl apply -f "$INFRA_DIR/manifests/target-app-ingress.yaml"
kubectl apply -f "$INFRA_DIR/manifests/target-app-addons.yaml"
kubectl apply -f "$INFRA_DIR/manifests/target-app-monitor.yaml"

# ── Patch & Deploy Zero-Door Agents ──────────────────────────────
echo "[10/12] Patching agent manifests for GHCR..."
# Bài học #4: Dùng Python để patch — tránh bash sed phức tạp
python3 "$INFRA_DIR/scripts/patch_manifests.py" \
  --src "$INFRA_DIR/manifests" \
  --dst "/tmp/manifests-cloud" \
  --registry "$REGISTRY"

echo "[11/12] Deploying Zero-Door Agents..."
kubectl apply -f /tmp/manifests-cloud/chaos-worker.yaml
kubectl apply -f /tmp/manifests-cloud/gaia-deployment.yaml
kubectl apply -f /tmp/manifests-cloud/nemesis-deployment.yaml
kubectl apply -f /tmp/manifests-cloud/hephaestus-deployment.yaml

# ── Apply Policies & Rules ────────────────────────────────────────
echo "[11b] Applying Network Policies and Prometheus Rules..."
kubectl apply -f "$INFRA_DIR/manifests/network-policies.yaml"
kubectl apply -f "$INFRA_DIR/manifests/prometheus-rules.yaml"

# ── Wait for Agents to be Ready ───────────────────────────────────
echo "[12/12] Waiting for agents to be ready (max 3 minutes)..."
kubectl wait --for=condition=ready pod \
  -l app=nemesis -n zero-door --timeout=180s || true
kubectl wait --for=condition=ready pod \
  -l app=gaia -n zero-door --timeout=180s || true
kubectl wait --for=condition=ready pod \
  -l app=hephaestus -n zero-door --timeout=180s || true

# ── Final Verification ────────────────────────────────────────────
echo ""
echo "================================================================"
echo " FINAL VERIFICATION"
echo "================================================================"
kubectl get pods -A --no-headers | grep -v Completed

echo ""
echo "  Testing HTTP endpoints..."
sleep 10  # Wait for Nginx to be ready

BOUTIQUE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
NEMESIS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/nemesis/healthz || echo "000")
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/nemesis/dashboard/ || echo "000")

echo "  Boutique Frontend:       HTTP $BOUTIQUE_STATUS"
echo "  Nemesis Health API:      HTTP $NEMESIS_STATUS"
echo "  Zero-Door Dashboard:     HTTP $DASHBOARD_STATUS"

DROPLET_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || echo "unknown")

echo ""
echo "================================================================"
if [[ "$BOUTIQUE_STATUS" == "200" ]] && [[ "$NEMESIS_STATUS" == "200" ]]; then
  echo " ✅ ZERO-DOOR CLOUD DEPLOYMENT SUCCESS!"
  echo ""
  echo " 🛒 Google Boutique:      http://${DROPLET_IP}/"
  echo " 📊 Zero-Door Dashboard:  http://${DROPLET_IP}/nemesis/dashboard/"
  echo " 🤖 Nemesis API:          http://${DROPLET_IP}/nemesis/healthz"
  echo " 🛡️  Hephaestus API:       http://${DROPLET_IP}/hephaestus/healthz"
  echo " 📈 Grafana (port-fwd):   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
  echo ""
  echo " Log file: $LOG"
else
  echo " ⚠️  DEPLOYMENT COMPLETED WITH WARNINGS"
  echo " Some services may still be starting. Check: kubectl get pods -A"
  echo " Log file: $LOG"
fi
echo "================================================================"
