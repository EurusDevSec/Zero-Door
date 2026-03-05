# 📖 HƯỚNG DẪN CHI TIẾT TASK S2: K8S CLUSTER SETUP

> **Dành cho**: Lê Văn Hoàng — người chưa có nhiều kinh nghiệm Kubernetes, học qua thực hành  
> **Triết lý**: Mỗi bước không chỉ hướng dẫn **làm gì** mà giải thích **tại sao làm vậy**  
> **Trạng thái**: ⬜ NOT STARTED  
> **Timeline**: Sprint 1 (Tuần 1-2)  
> **Tiền đề**: Task S1 Infra Setup ✅ DONE (cần có repo + môi trường trước)  
> **Tham chiếu**: [TASK_S2_K8S_CLUSTER.md](../../tasks/TASK_S2_K8S_CLUSTER.md) | [docs/plan.md](../plan.md) Section 5.1

---

## 📋 Mục lục

- [Bức tranh tổng thể: K8s Cluster nằm ở đâu?](#bức-tranh-tổng-thể-k8s-cluster-nằm-ở-đâu)
- [Tại sao cần Kubernetes?](#tại-sao-cần-kubernetes)
- [Kiến thức nền: Kubernetes là gì?](#kiến-thức-nền-kubernetes-là-gì)
- [Kiến thức nền: K3s vs Minikube vs Kind](#kiến-thức-nền-k3s-vs-minikube-vs-kind)
- [Kiến thức nền: Helm là gì?](#kiến-thức-nền-helm-là-gì)
- [Kiến thức nền: Namespace là gì?](#kiến-thức-nền-namespace-là-gì)
- [Bước 0: Chuẩn bị Git branch](#bước-0-chuẩn-bị-git-branch)
- [Bước 1: Cài đặt K3s trên Windows (Docker Desktop backend)](#bước-1-cài-đặt-k3s-trên-windows-docker-desktop-backend)
- [Bước 2: Cài đặt kubectl + cấu hình kubeconfig](#bước-2-cài-đặt-kubectl--cấu-hình-kubeconfig)
- [Bước 3: Cài đặt Helm 3.x](#bước-3-cài-đặt-helm-3x)
- [Bước 4: Tạo 3 Namespaces](#bước-4-tạo-3-namespaces)
- [Bước 5: Cài đặt Ingress Controller](#bước-5-cài-đặt-ingress-controller)
- [Bước 6: Deploy test pod và verify cluster](#bước-6-deploy-test-pod-và-verify-cluster)
- [Bước 7: Viết documentation cho team](#bước-7-viết-documentation-cho-team)
- [Bước 8: Commit & PR](#bước-8-commit--pr)
- [Checklist hoàn thành](#checklist-hoàn-thành)
- [Troubleshooting](#troubleshooting)

---

## Bức tranh tổng thể: K8s Cluster nằm ở đâu?

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      ZERO DOOR — SPRINT 1 (Phase 1)                       │
│                                                                           │
│  Task S1  Infra Setup (GitHub repo, CI/CD, board)                        │
│                                                                           │
│  ► Task S2  K8S CLUSTER  ◄◄◄  BẠN ĐANG Ở ĐÂY                           │
│    │                                                                      │
│    │  Đây là "sân khấu" — nơi TẤT CẢ thành phần của dự án sẽ chạy.     │
│    │  Không có K8s → không deploy được gì → toàn bộ code vô nghĩa.      │
│    │                                                                      │
│    │  Assignee: Hoàng (chính)                                            │
│    │  Target:   Sprint 1 (Tuần 1-2)                                      │
│    │                                                                      │
│    ├───► Task S3  Dev Environment (setup IDE, SDK cho các agents)        │
│    │                                                                      │
│    ├───► Task S5  Kafka Setup (Kafka chạy TRÊN K8s cluster này)          │
│    │                                                                      │
│    ├───► Task S6  Observability (Prometheus/Grafana chạy TRÊN K8s)       │
│    │                                                                      │
│    ├───► Task S7  Deploy Target App (Online Boutique chạy TRÊN K8s)      │
│    │                                                                      │
│    └───► Tất cả agents S8/S9/S10/S11 đều deploy lên cluster này         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

**Tóm lại:** Task S2 là **nền móng của nền móng**. Sau khi xong S2, toàn bộ team có thể deploy bất kỳ thứ gì lên cluster và bắt đầu làm việc thật sự.

---

## Tại sao cần Kubernetes?

Câu hỏi hợp lý: "Tại sao không dùng Docker Compose cho đơn giản?"

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DOCKER COMPOSE vs KUBERNETES — So sánh thực tế cho ZERO DOOR          │
│                                                                         │
│  Vấn đề ZERO DOOR cần giải quyết:                                      │
│  ─────────────────────────────────────────────────────────────────────  │
│  1. Hephaestus phải RESTART pods khi phát hiện lỗi → cần K8s API      │
│  2. Gaia phải đọc Kubernetes events/metrics → cần K8s API             │
│  3. Nemesis phải inject chaos VÀO pods → cần K8s API                  │
│  4. Target app: Google Online Boutique = K8s-native app                │
│                                                                         │
│  Docker Compose: Chỉ chạy containers, KHÔNG có K8s API                │
│  Kubernetes: Có đầy đủ API, self-healing primitives, namespacing        │
│                                                                         │
│  ⟹ Docker Compose: KHÔNG đáp ứng được yêu cầu cốt lõi                 │
│  ⟹ Kubernetes: Bắt buộc — agents PHẢI gọi K8s API để hoạt động       │
└─────────────────────────────────────────────────────────────────────────┘
```

**Ngoài ra:** Hội đồng nghiên cứu đánh giá cao khi đề tài dùng công nghệ thực tế (production-grade). Kubernetes = trình bày được rằng hệ thống có thể scale ra production.

---

## Kiến thức nền: Kubernetes là gì?

Đừng sợ Kubernetes. Hiểu đơn giản nhất:

```
┌──────────────────────────────────────────────────────────────────────┐
│  BẠN CÓ THỂ HIỂU KUBERNETES NHƯ SAU:                                │
│                                                                      │
│  Docker:     "Tôi chạy 1 container"                                  │
│  Kubernetes: "Tôi quản lý 100 containers — tự restart khi crash,    │
│               tự cân bằng tải, tự scale khi cần"                    │
│                                                                      │
│  Các khái niệm cần biết cho dự án này:                              │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────────┐   │
│  │  Node    │ →  │  Pod     │ →  │  Container (ứng dụng thực)   │   │
│  │(máy vật  │    │(1+ cont- │    │                              │   │
│  │ lý/VM)   │    │ainers)   │    └──────────────────────────────┘   │
│  └──────────┘    └──────────┘                                        │
│                                                                      │
│  Deployment:  Quản lý N bản sao của Pod (rolling update, rollback)  │
│  Service:     Networking — expose pod ra ngoài có địa chỉ ổn định   │
│  Namespace:   "Folder ảo" — cô lập tài nguyên theo nhóm            │
│  Ingress:     "Cổng vào" — routing HTTP traffic vào đúng service    │
│  ConfigMap:   Lưu config (non-secret) cho pods                      │
│  Secret:      Lưu config nhạy cảm (passwords, tokens)              │
└──────────────────────────────────────────────────────────────────────┘
```

**Với ZERO DOOR, bạn cần biết:**

| Khi Hephaestus...   | Nó gọi K8s API để...                                          |
| ------------------- | ------------------------------------------------------------- |
| Restart pod bị lỗi  | `DELETE /api/v1/namespaces/{ns}/pods/{name}` → K8s tự tạo lại |
| Scale up service    | `PATCH .../deployments/{name}` → tăng `replicas`              |
| Rollback deployment | `POST .../deployments/{name}/rollback`                        |

| Khi Gaia...        | Nó đọc từ...                         |
| ------------------ | ------------------------------------ |
| Lấy danh sách pods | `GET /api/v1/namespaces/{ns}/pods`   |
| Xem events anomaly | `GET /api/v1/namespaces/{ns}/events` |
| Đọc resource usage | Prometheus scrape → metrics endpoint |

---

## Kiến thức nền: K3s vs Minikube vs Kind

Ba lựa chọn phổ biến để chạy Kubernetes local trên Windows:

```
┌───────────────┬──────────────────────────────┬──────────────────────────┐
│               │ K3s (qua k3d)                 │ Minikube                 │
├───────────────┼──────────────────────────────┼──────────────────────────┤
│ Cách chạy     │ Docker containers (k3d)       │ VM hoặc Docker driver    │
│ Tốc độ start  │ ~30 giây                      │ ~2-3 phút                │
│ RAM cần       │ ~512MB                        │ ~2GB mặc định            │
│ Production    │ ✅ K3s là distro production   │ ❌ Dev-only               │
│ Multi-node    │ ✅ Dễ dàng                    │ ⚠️ Phức tạp hơn          │
│ Windows       │ ✅ Qua Docker Desktop         │ ✅ Chính thức hỗ trợ     │
│ Ingress       │ ✅ Traefik built-in           │ ⚠️ Cần addon riêng       │
│ Recommend     │ ⭐⭐⭐ Nhẹ, nhanh, gần production│ ⭐⭐ OK fallback           │
└───────────────┴──────────────────────────────┴──────────────────────────┘

Kind:
- Nhẹ nhất (pure Docker)
- Networking setup phức tạp hơn trên Windows
- Dùng khi K3s và Minikube đều fail
```

**Quyết định cho ZERO DOOR:** Dùng **k3d** (K3s-in-Docker) vì:

1. Nhẹ nhất — quan trọng vì còn phải chạy target app + 3 agents + Kafka + Prometheus cùng lúc
2. Production-like — K3s là K8s distribution thật, không phải mock
3. Multi-node support — thử nghiệm distributed failure scenarios
4. Traefik ingress built-in — tiết kiệm 1 bước setup

> **Lưu ý:** Nếu máy gặp vấn đề với k3d, fallback sang Minikube. Hướng dẫn fallback ở phần [Troubleshooting](#troubleshooting).

---

## Kiến thức nền: Helm là gì?

```
┌──────────────────────────────────────────────────────────────────────┐
│  Vấn đề khi deploy K8s không có Helm:                               │
│                                                                      │
│  Kafka cần: StatefulSet + 3 Services + ConfigMap + Secret +          │
│             PersistentVolumeClaim + NetworkPolicy + ...              │
│             → Phải viết 500+ dòng YAML!                              │
│                                                                      │
│  Với Helm:                                                           │
│  helm install kafka bitnami/kafka --namespace zero-door              │
│  → 1 lệnh, tất cả đã setup!                                          │
│                                                                      │
│  Helm = "Package manager" cho Kubernetes                             │
│  Giống như: apt (Linux), pip (Python), npm (Node.js)                 │
│                                                                      │
│  Những gì sẽ dùng Helm trong ZERO DOOR:                             │
│  • bitnami/kafka (Task S5)                                           │
│  • prometheus-community/kube-prometheus-stack (Task S6)              │
│  • Online Boutique có thể có Helm chart (Task S7)                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Kiến thức nền: Namespace là gì?

Namespace = "Folder ảo" để cô lập tài nguyên:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Cluster ZERO DOOR sẽ có 3 namespaces:                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  namespace: zero-door                                        │   │
│  │  → Agent Nemesis, Gaia, Hephaestus chạy ở đây               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  namespace: target-app                                       │   │
│  │  → Google Online Boutique (target bị tấn công) chạy ở đây   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  namespace: monitoring                                       │   │
│  │  → Prometheus, Grafana, Alertmanager chạy ở đây             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Tại sao cô lập?                                                    │
│  1. RBAC: Hephaestus chỉ có quyền restart pods trong target-app     │
│  2. Resource quotas: giới hạn RAM/CPU theo namespace               │
│  3. Network policies: Gaia có thể scrape monitoring nhưng          │
│     Nemesis không được đọc config secrets của Hephaestus           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 0: Chuẩn bị Git branch

Trước khi bắt tay làm, tạo branch riêng cho task này:

```bash
# Đảm bảo đang ở thư mục project
cd R:/_Projects/Eurus_Workspace/zero_door

# Chuyển về main và pull mới nhất
git checkout main
git pull origin main

# Tạo branch mới cho K8s setup
git checkout -b infra/k8s-cluster-setup

# Verify branch
git branch --show-current
# Output: infra/k8s-cluster-setup
```

> **Convention check:** Branch dùng prefix `infra/` (không phải `feat/`) vì đây là infrastructure setup, không phải feature của ứng dụng.

---

## Bước 1: Cài đặt K3s trên Windows (Docker Desktop backend)

### Prerequisites

Trước khi bắt đầu, đảm bảo:

- Docker Desktop đã cài và đang chạy (icon Docker ở taskbar)
- Docker Desktop bật WSL2 backend hoặc Hyper-V
- Ít nhất 8GB RAM free

### Bước 1.1: Cài k3d (K3s in Docker)

k3d là tool chạy K3s cluster BÊN TRONG Docker containers — không cần VM.

```bash
# Cài k3d qua Chocolatey (nếu đã có choco)
choco install k3d

# HOẶC cài thủ công (PowerShell as Administrator):
winget install k3d

# HOẶC download binary trực tiếp:
# 1. Vào https://github.com/k3d-io/k3d/releases/latest
# 2. Download k3d-windows-amd64.exe
# 3. Rename thành k3d.exe
# 4. Copy vào C:\Windows\System32\ (hoặc thêm vào PATH)

# Verify cài đặt
k3d version
# Output: k3d version v5.x.x
#         k3s version v1.x.x (default)
```

### Bước 1.2: Tạo K3s cluster

```bash
# Tạo cluster tên "zero-door" với:
# --servers 1: 1 control plane node
# --agents 2: 2 worker nodes (để simulate multi-node deployment)
# -p "8080:80@loadbalancer": expose port 80 của Ingress ra localhost:8080
# -p "8443:443@loadbalancer": expose HTTPS ra localhost:8443
k3d cluster create zero-door \
  --servers 1 \
  --agents 2 \
  -p "8080:80@loadbalancer" \
  -p "8443:443@loadbalancer" \
  --k3s-arg "--disable=traefik@server:0"

# Lưu ý: --disable=traefik vì ta sẽ cài Nginx Ingress riêng
# (Nginx có nhiều docs/examples hơn cho việc debug)

# Verify cluster đang chạy
k3d cluster list
# Output:
# NAME        SERVERS   AGENTS   LOADBALANCER
# zero-door   1/1       2/2      true
```

> **Tại sao 2 agents?** Project ZERO DOOR sẽ chạy nhiều workloads cùng lúc:
>
> - Node 1: Target app (Online Boutique ~10 microservices)
> - Node 2: Agents + Kafka + Prometheus
>
> Nếu chỉ 1 node, tất cả chen vào cùng 1 chỗ → tranh giành RAM → crash.

> ⚠️ **Windows-specific:** Nếu gặp lỗi `Error response from daemon: network interface not found`, restart Docker Desktop rồi thử lại.

---

## Bước 2: Cài đặt kubectl + cấu hình kubeconfig

### kubectl là gì?

`kubectl` = command-line tool để nói chuyện với Kubernetes API. Giống như `git` là tool để nói chuyện với GitHub.

### Bước 2.1: Cài kubectl

```bash
# Cài qua Chocolatey
choco install kubernetes-cli

# HOẶC qua winget
winget install Kubernetes.kubectl

# Verify
kubectl version --client
# Output: Client Version: v1.x.x
```

### Bước 2.2: Cấu hình kubeconfig

k3d tự động merge kubeconfig khi tạo cluster. Verify:

```bash
# Xem context hiện tại
kubectl config current-context
# Output: k3d-zero-door

# Xem tất cả contexts (nếu có nhiều cluster)
kubectl config get-contexts

# Đảm bảo đang dùng zero-door context
kubectl config use-context k3d-zero-door
```

### Bước 2.3: Verify cluster hoạt động

```bash
# Lệnh quan trọng nhất — 1 trong Acceptance Criteria
kubectl get nodes
# Output mong đợi:
# NAME                      STATUS   ROLES                  AGE   VERSION
# k3d-zero-door-server-0    Ready    control-plane,master   2m    v1.x.x
# k3d-zero-door-agent-0     Ready    <none>                 2m    v1.x.x
# k3d-zero-door-agent-1     Ready    <none>                 2m    v1.x.x
```

> ✅ **STATUS = Ready** nghĩa là cluster đang hoạt động. Nếu thấy `NotReady`, chờ thêm 30 giây rồi thử lại.

```bash
# Xem hệ thống pods (K8s tự tạo)
kubectl get pods -n kube-system
# Bạn sẽ thấy: coredns, local-path-provisioner, metrics-server
# Tất cả phải Running
```

---

## Bước 3: Cài đặt Helm 3.x

### Bước 3.1: Cài Helm

```bash
# Cài qua Chocolatey
choco install kubernetes-helm

# HOẶC qua winget
winget install Helm.Helm

# Verify
helm version
# Output: version.BuildInfo{Version:"v3.x.x", ...}
```

### Bước 3.2: Thêm Helm repositories cần dùng

Thêm luôn các repos sẽ dùng trong project — tiết kiệm thời gian sau này:

```bash
# Bitnami (Kafka, PostgreSQL, Redis, v.v.)
helm repo add bitnami https://charts.bitnami.com/bitnami

# Prometheus community (Prometheus + Grafana stack)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# Update tất cả repos
helm repo update

# Verify
helm repo list
# Output:
# NAME                 URL
# bitnami              https://charts.bitnami.com/bitnami
# prometheus-community https://prometheus-community.github.io/helm-charts
# ingress-nginx        https://kubernetes.github.io/ingress-nginx
```

---

## Bước 4: Tạo 3 Namespaces

```bash
# Tạo 3 namespaces
kubectl create namespace zero-door
kubectl create namespace monitoring
kubectl create namespace target-app

# Verify
kubectl get namespaces
# Output phải thấy 3 namespaces mới + default + kube-system + kube-public
```

### Label namespaces (best practice)

Labels giúp filter và áp dụng policies sau này:

```bash
kubectl label namespace zero-door \
  project=zero-door \
  environment=development \
  team=agents

kubectl label namespace monitoring \
  project=zero-door \
  environment=development \
  team=observability

kubectl label namespace target-app \
  project=zero-door \
  environment=development \
  team=target
```

> **Tại sao label?** Khi viết Network Policies hoặc RBAC rules, bạn target theo label — không phải hardcode namespace name. Ví dụ: "Gaia chỉ được đọc pods trong namespace có label `project=zero-door`".

---

## Bước 5: Cài đặt Ingress Controller

Ingress Controller là "cổng vào" cluster — nhận HTTP requests từ bên ngoài và route vào đúng service bên trong.

```
Internet → localhost:8080 → Ingress Controller → Service A hoặc B hoặc C
```

### Cài Nginx Ingress Controller qua Helm

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Verify cài đặt (chờ ~60 giây)
kubectl get pods -n ingress-nginx
# Output mong đợi:
# NAME                                        READY   STATUS    RESTARTS   AGE
# ingress-nginx-controller-xxx-xxx            1/1     Running   0          60s

# Xem service
kubectl get svc -n ingress-nginx
# Output:
# NAME                       TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)
# ingress-nginx-controller   LoadBalancer   10.x.x.x      localhost     80:30080/TCP,443:30443/TCP
```

> ✅ **EXTERNAL-IP = localhost** nghĩa là Ingress đang lắng nghe tại `localhost:8080` (port đã map ở Bước 1.2).

---

## Bước 6: Deploy test pod và verify cluster

**Mục đích:** Xác nhận toàn bộ stack (K3s + kubectl + Helm + Namespace + Ingress) hoạt động end-to-end trước khi đóng task.

### Bước 6.1: Tạo file test manifest

Tạo file `infra/test/nginx-test.yaml`:

```yaml
# infra/test/nginx-test.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-test
  namespace: zero-door
  labels:
    app: nginx-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-test
  template:
    metadata:
      labels:
        app: nginx-test
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-test
  namespace: zero-door
spec:
  selector:
    app: nginx-test
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-test
  namespace: zero-door
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: nginx-test.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-test
                port:
                  number: 80
```

### Bước 6.2: Deploy và verify

```bash
# Tạo thư mục infra nếu chưa có
mkdir -p infra/test

# Lưu file yaml rồi apply
kubectl apply -f infra/test/nginx-test.yaml

# Chờ pod Running
kubectl get pods -n zero-door -w
# Ctrl+C khi thấy STATUS = Running

# Test qua port-forward (không cần Ingress)
kubectl port-forward -n zero-door deployment/nginx-test 9090:80
# Mở browser hoặc chạy: curl http://localhost:9090
# Phải thấy "Welcome to nginx!"

# Ctrl+C để dừng port-forward
```

> **Test Ingress (optional):** Thêm `nginx-test.local` vào Windows hosts file (`C:\Windows\System32\drivers\etc\hosts`):
>
> ```
> 127.0.0.1  nginx-test.local
> ```
>
> Sau đó mở `http://nginx-test.local:8080` trong browser.

### Bước 6.3: Clean up test resources

```bash
kubectl delete -f infra/test/nginx-test.yaml
# Giữ file yaml lại trong repo để reference
```

---

## Bước 7: Viết documentation cho team

### Tạo file `docs/guides/GUIDE_K8S_SETUP.md`

File này khác với file guide này — nó là **quick reference** cho team khi cần rebuild hoặc khi hpt8001 muốn setup môi trường riêng. Nội dung tối giản:

```markdown
# ZERO DOOR — K8s Cluster Quick Setup

## Prerequisites

- Docker Desktop đang chạy
- k3d, kubectl, helm đã cài

## Tạo lại cluster (nếu bị xóa)

\`\`\`bash
k3d cluster create zero-door \
 --servers 1 --agents 2 \
 -p "8080:80@loadbalancer" \
 -p "8443:443@loadbalancer" \
 --k3s-arg "--disable=traefik@server:0"

kubectl create namespace zero-door
kubectl create namespace monitoring
kubectl create namespace target-app

helm install ingress-nginx ingress-nginx/ingress-nginx \
 --namespace ingress-nginx --create-namespace \
 --set controller.service.type=LoadBalancer
\`\`\`

## Verify

\`\`\`bash
kubectl get nodes # Phải thấy 3 nodes Ready
kubectl get namespaces # Phải thấy zero-door, monitoring, target-app
kubectl get pods -n ingress-nginx # Phải thấy controller Running
\`\`\`

## Xóa cluster (khi không dùng để tiết kiệm RAM)

\`\`\`bash
k3d cluster stop zero-door # Dừng (vẫn giữ data)
k3d cluster delete zero-door # Xóa hoàn toàn
\`\`\`
```

---

## Bước 8: Commit & PR

```bash
# Stage tất cả files liên quan
git add infra/test/nginx-test.yaml
git add docs/guides/GUIDE_K8S_SETUP.md

# Commit theo convention
git commit -m "infra(k8s): setup k3d cluster with namespaces and ingress

- Create k3d cluster 'zero-door' (1 server, 2 agents)
- Create namespaces: zero-door, monitoring, target-app
- Install NGINX Ingress Controller via Helm
- Add Helm repos: bitnami, prometheus-community, ingress-nginx
- Add test nginx deployment manifest for cluster verification
- Add GUIDE_K8S_SETUP.md for cluster rebuild reference"

# Push branch
git push -u origin infra/k8s-cluster-setup

# Tạo PR trên GitHub:
# Title: "infra(k8s): K8s cluster setup with namespaces and ingress [S2]"
# Description: Link đến Task S2, screenshot của kubectl get nodes
```

### Checklist PR

Trước khi tạo PR, đảm bảo:

- [ ] `kubectl get nodes` → 3 nodes Ready (chụp screenshot, attach vào PR)
- [ ] `kubectl get namespaces` → thấy 3 namespaces
- [ ] `kubectl get pods -n ingress-nginx` → controller Running
- [ ] Test nginx pod accessible qua port-forward
- [ ] `GUIDE_K8S_SETUP.md` đã viết

---

## Checklist hoàn thành

Đây là checklist gương task `TASK_S2_K8S_CLUSTER.md` — tick khi xong:

- [ ] **1.2.1** K3s (k3d) cluster tạo thành công, 3 nodes
- [ ] **1.2.2** `kubectl get nodes` → tất cả nodes STATUS = **Ready**
- [ ] **1.2.3** Helm 3.x cài đặt, `helm version` thành công
- [ ] **1.2.4** `helm repo list` → thấy bitnami + prometheus-community + ingress-nginx
- [ ] **1.2.5** 3 namespaces tạo: `zero-door`, `monitoring`, `target-app`
- [ ] **1.2.6** Ingress controller (NGINX) chạy trong namespace `ingress-nginx`
- [ ] **1.2.7** Deploy nginx test pod → accessible qua `kubectl port-forward`
- [ ] **1.2.8** `docs/guides/GUIDE_K8S_SETUP.md` viết xong
- [ ] **1.2.9** Branch `infra/k8s-cluster-setup` pushed, PR tạo với screenshot
- [ ] **1.2.10** `docs/context.md` cập nhật status S2 = ✅ Done

---

## Troubleshooting

### Lỗi: "Cannot connect to Docker daemon"

```
Error: failed to create cluster: failed to create nodes: failed to create node ...
Error response from daemon: Cannot connect to the Docker daemon
```

**Nguyên nhân:** Docker Desktop chưa chạy hoặc chưa sẵn sàng

**Giải pháp:**

1. Mở Docker Desktop
2. Chờ đến khi taskbar icon không còn animation (khoảng 30-60 giây)
3. Thử lại lệnh k3d

---

### Lỗi: "Network interface not found" (Windows)

```
Error response from daemon: network interface "k3d-zero-door" not found
```

**Giải pháp:**

```bash
# Xóa cluster cũ nếu có
k3d cluster delete zero-door

# Restart Docker Desktop
# Sau đó tạo lại cluster
k3d cluster create zero-door ...
```

---

### Lỗi: kubectl context không đúng

```
The connection to the server localhost:8080 was refused
```

**Nguyên nhân:** kubectl đang dùng sai context

**Giải pháp:**

```bash
# Xem tất cả contexts
kubectl config get-contexts

# Switch sang context đúng
kubectl config use-context k3d-zero-door

# Verify
kubectl cluster-info
```

---

### Fallback: Dùng Minikube thay vì k3d

Nếu k3d không chạy được (thường do WSL2 issues), dùng Minikube:

```bash
# Cài Minikube
winget install Kubernetes.minikube

# Start với Docker driver
minikube start --driver=docker --memory=6144 --cpus=4

# Bật Ingress addon
minikube addons enable ingress

# Verify
kubectl get nodes
# OUTPUT:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.x.x

# Tạo namespaces như bình thường
kubectl create namespace zero-door
kubectl create namespace monitoring
kubectl create namespace target-app
```

> ⚠️ **Lưu ý Minikube:** Chỉ có 1 node, không multi-node. Về chức năng vẫn đủ cho dự án. Ghi chú vào context.md nếu dùng Minikube để team biết.

---

### Node stuck ở "NotReady"

```
NAME                      STATUS     ROLES                  AGE
k3d-zero-door-server-0    NotReady   control-plane,master   30s
```

**Giải pháp:** Chờ 1-2 phút — control plane khởi động cần thời gian. Nếu sau 3 phút vẫn NotReady:

```bash
# Xem chi tiết
kubectl describe node k3d-zero-door-server-0

# Xem system pod logs
kubectl get pods -n kube-system
kubectl logs -n kube-system <pod-name-bị-lỗi>
```

---

### Ingress EXTERNAL-IP stuck ở `<pending>`

```
NAME                       TYPE           CLUSTER-IP   EXTERNAL-IP   PORT(S)
ingress-nginx-controller   LoadBalancer   10.x.x.x    <pending>      80:...
```

**Nguyên nhân:** k3d cần thêm thời gian để assign IP qua load balancer

**Giải pháp:** Chờ 2-3 phút. Với k3d, EXTERNAL-IP sẽ là `localhost` (do port mapping). Nếu vẫn pending sau 5 phút:

```bash
# Kiểm tra k3d loadbalancer container
docker ps | grep k3d

# Nếu không thấy loadbalancer, tạo lại cluster với đúng flag -p
```

---

_Tài liệu này tham chiếu: [TASK_S2_K8S_CLUSTER.md](../../tasks/TASK_S2_K8S_CLUSTER.md) | [docs/plan.md](../plan.md) | [K3s Docs](https://docs.k3s.io) | [k3d Docs](https://k3d.io)_

_Last updated: 05/03/2026_
