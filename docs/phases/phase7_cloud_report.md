# Phase 7: Cloud Transition & Final Scientific Report

> **Timeline:** Week 25-28 (Sprint 13-14)
> **Owner:** EurusDevSec (Cloud Deploy & Demo) + hp8001 (Report Writing & Slides)
> **Milestone:** M7 (Defense Ready)
> **Prerequisite:** Phase 6 hoàn thành (CI/CD Pipeline & DevOps Optimization ready)

---

## 🟢 DEPLOYMENT STATUS: IaC (Terraform + deploy.sh)

> **Phương pháp chính thức:** Terraform quản lý hạ tầng DO + `deploy.sh` tự động hóa K3s stack.
> Deploy lần 1 (manual) đã thành công → đã học được lessons → Rebuild sạch bằng IaC.
>
> | Endpoint | URL | Status |
> |---|---|---|
> | 🛒 Google Boutique (Frontend) | `http://<DROPLET_IP>/` | ✅ Verified HTTP 200 |
> | 📊 Zero-Door Dashboard | `http://<DROPLET_IP>/nemesis/dashboard/` | ✅ Verified HTTP 200 |
> | 🤖 Nemesis API | `http://<DROPLET_IP>/nemesis/healthz` | ✅ UP, kafka_connected=true |
> | 🛡️ Hephaestus API | `http://<DROPLET_IP>/hephaestus/healthz` | ✅ UP, k8s_connected=true |
> | 📈 Grafana | Internal (port-forward :3000) | ✅ Running (admin/zerodoor123) |

---

## 1. Mục tiêu Phase

Hoàn thiện 2 deliverables cuối cùng: (1) Deploy hệ thống lên DigitalOcean Cloud để chứng minh tính khả thi ở môi trường production-like, và (2) Hoàn thành báo cáo nghiên cứu khoa học + demo video + bài thuyết trình để bảo vệ trước Hội đồng Khoa học Trường Đại học Thủ Dầu Một.

---

## 2. Tasks

### 2.1. Cloud Deployment — DigitalOcean (FinOps Strategy)

- [x] **T7.1** Triển khai cụm Kubernetes trên DigitalOcean Droplet:
  - **Thực tế:** K3s v1.36.2+k3s1 trên Droplet Regular AMD 4vCPU/8GB RAM/160GB SSD ($48/tháng).
  - **Lý do chọn Droplet thay vì DOKS:** DOKS charge phí LB riêng (~$12/tháng). Single-node Droplet + K3s dùng Klipper LB built-in → tiết kiệm hơn cho môi trường demo/research.

- [x] **T7.2** Cấu hình Cloud Firewall trên DigitalOcean:
  - SSH (22): mở cho IP cá nhân.
  - HTTP (80): mở cho internet (truy cập Boutique & Agents API).
  - ⚠️ **Lưu ý thực tế:** Cổng K8s API (6443) bị chặn bởi DO Firewall → không thể dùng `kubectl` từ local. Giải pháp: deploy trực tiếp trên Droplet qua SSH.

- [x] **T7.3** Cài đặt Nginx Ingress Controller:
  - **Thực tế:** Disable Traefik (K3s default) bằng flag `--disable traefik`, xóa HelmCharts cũ, cài Nginx Ingress Controller v1.8.2 qua official manifest.
  - **Kết quả:** Nginx Ingress listening trên cổng 80 của host thông qua Klipper LoadBalancer built-in.

- [x] **T7.4** Deploy full stack lên Cloud:
  - **Phương pháp chính thức (IaC):** Terraform + `deploy.sh` + `patch_manifests.py`
    - `infrastructure/terraform/main.tf` → tạo Droplet + Firewall
    - `infrastructure/terraform/cloud-init.yaml` → auto-run `deploy.sh` khi boot
    - `infrastructure/scripts/deploy.sh` → cài K3s, Helm, deploy toàn bộ stack
    - `infrastructure/scripts/patch_manifests.py` → patch GHCR image + imagePullSecrets
  - **3 Namespaces:** `zero-door`, `target-app`, `monitoring`
  - **1 lệnh deploy:** `terraform apply -var="do_token=xxx" -var="github_pat=xxx"`

- [x] **T7.5** Verify hệ thống hoạt động trên cloud:

```
=== ZERO-DOOR (Agents) ===
chaos-worker   1/1  Running  ✅
gaia           1/1  Running  ✅  (ghcr.io image pulled)
hephaestus     1/1  Running  ✅  (ghcr.io image pulled)
kafka          2/2  Running  ✅  (KRaft mode, topics provisioned)
nemesis        1/1  Running  ✅  (ghcr.io image pulled)

=== TARGET-APP (Boutique) ===
cartservice          1/1  Running  ✅
checkoutservice      1/1  Running  ✅
currencyservice      1/1  Running  ✅
emailservice         0/1  CrashLoop ⚠️  (gRPC startup slow → probe timeout)
frontend             1/1  Running  ✅
paymentservice       1/1  Running  ✅
productcatalogservice 1/1 Running  ✅
redis-cart           1/1  Running  ✅
shippingservice      1/1  Running  ✅

=== MONITORING ===
prometheus-grafana              3/3  Running  ✅
prometheus-operator             1/1  Running  ✅
prometheus-kube-state-metrics   1/1  Running  ✅
prometheus (main)               2/2  Running  ✅
node-exporter                   1/1  Running  ✅
```

> ⚠️ `emailservice` CrashLoopBackOff: Dịch vụ email của Google Boutique sử dụng gRPC khởi động chậm trên node đơn. Đây là known issue của demo app, **không ảnh hưởng tới core Zero-Door system**. Frontend vẫn hoạt động bình thường.

### 2.2. Domain & SSL (Tùy chọn)

- [ ] **T7.6** Gắn domain cho Grafana dashboard và Frontend:
  - Mua domain (hoặc dùng free subdomain từ DuckDNS/nip.io).
  - Cấu hình Nginx Ingress + cert-manager cho Let's Encrypt TLS.

### 2.3. Demo Video Production

- [ ] **T7.7** Chuẩn bị kịch bản Demo Video (5-10 phút):
  - Giới thiệu đề tài, kiến trúc Multi-Agent.
  - Steady-state: mở `http://209.97.166.246/` → Google Boutique Live trên Cloud.
  - Attack Phase: Nemesis gọi Gemini sinh payload → `POST /nemesis/attack/start`.
  - Heal Phase: Hephaestus nhận alert, scale up pod tự động.
  - Chứng minh sập trang (502/503) và phục hồi khi bị Pod Kill.

- [ ] **T7.8** Quay video demo:
  - Sử dụng OBS Studio hoặc tool record màn hình.
  - Split screen: Terminal (kubectl) bên trái + Dashboard bên phải.

### 2.4. Báo cáo Nghiên cứu Khoa học

- [ ] **T7.9** Hoàn thiện cấu trúc báo cáo NCKH 6 chương.
- [ ] **T7.10** Đưa dữ liệu thí nghiệm (Phase 5) và so sánh Downtime Ingress thực tế vào Chương 5.
- [ ] **T7.11** Viết phần **Giới hạn nghiên cứu** (validate trên sandbox, 3 loại tấn công, single cluster, LLM prompt latency).
- [ ] **T7.12** Viết phần **Hướng phát triển tương lai** (mô hình SaaS Control Plane, WebSocket Agent, APM SDK).

### 2.5. Bài Thuyết trình (Defense Presentation)

- [ ] **T7.13** Chuẩn bị slide thuyết trình (15-20 slides).
- [ ] **T7.14** Chuẩn bị **câu hỏi phản biện thường gặp** từ Hội đồng và câu trả lời.

---

## 3. Definition of Done

| # | Tiêu chí | Kết quả thực tế |
|---|---|---|
| 1 | Hệ thống chạy thành công trên Cloud | ✅ `kubectl get pods -A` → 14/15 Running (1 emailservice probe issue) |
| 2 | Frontend truy cập được từ internet | ✅ `http://209.97.166.246/` → HTTP 200 |
| 3 | Agents health check pass | ✅ Nemesis UP + Kafka connected, Hephaestus UP + K8s connected |
| 4 | Demo video hoàn thành (5-10 phút) | ⏳ Chưa thực hiện |
| 5 | Báo cáo NCKH hoàn thành đầy đủ 6 chương | ⏳ Chưa thực hiện |
| 6 | Slide thuyết trình hoàn thành | ⏳ Chưa thực hiện |
| 7 | Source code commit final trên GitHub | ⏳ Cần tag `v1.0.0` |

---

## 4. Sai lệch so với Thiết kế Lý thuyết (Lessons Learned)

| Thiết kế Lý thuyết | Thực tế Triển khai | Lý do thay đổi |
|---|---|---|
| Dùng Helm chart (`cloud-values.yaml`) | Raw YAML manifests + Python patch script | Không có Helm chart trong repo; kubectl manifests sẵn có và đủ dùng |
| Deploy từ máy local qua `kubectl --kubeconfig=config-do` | Deploy trực tiếp trên Droplet qua SSH | DO Firewall chặn port 6443; SSH to Droplet → kubectl local là pattern đúng cho single-node |
| Traefik (K3s default) | Nginx Ingress Controller | Manifests dùng `ingressClassName: nginx` và nginx annotations; Nginx giữ nguyên 100% |
| `helm upgrade --install` từ máy Windows | Helm cài trực tiếp trên Droplet | Tránh vấn đề shell escaping Windows PowerShell |
| Boutique truy cập port 8080 | Boutique truy cập port 80 (tiêu chuẩn HTTP) | Nginx Ingress Controller listen mặc định trên port 80, clean hơn 8080 |
| `imagePullSecrets` thêm thủ công trong values | Python regex script tự động inject vào manifests | Không có template engine, script đơn giản và hiệu quả |

---

## 5. Hướng dẫn Truy cập Hệ thống Cloud

### Truy cập từ Browser (Public)
```
Google Boutique App:   http://209.97.166.246/
Nemesis API health:    http://209.97.166.246/nemesis/healthz
Hephaestus API health: http://209.97.166.246/hephaestus/healthz
```

### SSH vào Droplet để quản trị
```bash
ssh root@209.97.166.246
kubectl get pods -A
kubectl logs -n zero-door nemesis-<pod-id> -f
```

### Port-forward Prometheus/Grafana (từ máy local)
```bash
ssh -L 3000:localhost:3000 root@209.97.166.246 \
  "kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
# Mở browser: http://localhost:3000 (admin / zerodoor123)

ssh -L 9090:localhost:9090 root@209.97.166.246 \
  "kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring"
# Mở browser: http://localhost:9090
```

---

## 6. Budget Summary (FinOps Tổng kết)

| Hạng mục | Chi phí thực tế | Ghi chú |
|---|---|---|
| DigitalOcean Droplet (4vCPU/8GB/160GB, Regular AMD) | ~$48/tháng | Chạy 24/7 demo + test |
| Domain (tùy chọn) | 0 - $10 | DuckDNS free hoặc mua domain rẻ |
| Gemini / OpenAI API tokens | ~$10-20 | Giới hạn sử dụng |
| **Tổng Phase 7** | **~$48-78/tháng** | Trong budget nghiên cứu |

> 💡 **FinOps tip:** Destroy Droplet sau khi quay demo video xong để tiết kiệm. Snapshot lại trước khi destroy để restore nhanh khi cần.
