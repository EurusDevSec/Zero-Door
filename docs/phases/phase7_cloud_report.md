# Phase 7: Cloud Transition & Final Scientific Report

> **Timeline:** Week 25-28 (Sprint 13-14)  
> **Owner:** EurusDevSec (Cloud Deploy & Demo) + hp8001 (Report Writing & Slides)  
> **Milestone:** M7 (Defense Ready)  
> **Prerequisite:** Phase 6 hoàn thành (CI/CD Pipeline & DevOps Optimization ready)

---

## 1. Mục tiêu Phase

Hoàn thiện 2 deliverables cuối cùng: (1) Deploy hệ thống lên AWS Cloud/DigitalOcean Cloud để chứng minh tính khả thi ở môi trường production-like, và (2) Hoàn thành báo cáo nghiên cứu khoa học + demo video + bài thuyết trình để bảo vệ trước Hội đồng Khoa học Trường Đại học Thủ Dầu Một.

---

## 2. Tasks

### 2.1. Cloud Deployment — AWS & DigitalOcean (FinOps Strategy)

- [ ] **T7.1** Triển khai cụm Kubernetes trên môi trường Cloud thực tế:
  - AWS EC2: Chạy K3s trên Instance type `t3.medium` (Spot Instance để tiết kiệm ~70%), sử dụng 30GB GP3 EBS.
  - Hoặc DigitalOcean Kubernetes (DOKS): Triển khai cụm NodePool giá rẻ để tận dụng tối đa tính portability của K8s.
  - Mục tiêu chi phí FinOps: < $20/tháng.

- [ ] **T7.2** Cấu hình **VPC, Network Firewalls & Security Groups**:
  - Hạn chế cổng quản trị SSH (22) và K8s API (6443) chỉ cho phép từ IP cá nhân.
  - Mở cổng HTTP (80) và HTTPS (443) ra Internet công cộng thông qua Cloud Load Balancer trỏ về Ingress Controller.

- [ ] **T7.3** Cài đặt và cấu hình Ingress Controller trên Cloud:
  - Sử dụng Nginx Ingress Controller làm chuẩn công nghiệp thay thế cho Traefik mặc định để quản lý traffic L7.

- [ ] **T7.4** Deploy full Helm stack lên Cloud:
  - 3 Namespaces (zero-door, target-app, monitoring).
  - Kafka, Prometheus, Grafana.
  - 3 Agents (Nemesis, Gaia, Hephaestus) + Chaos Worker.
  - Google Online Boutique (target-app) sử dụng file cấu hình riêng cho môi trường Cloud (`cloud-values.yaml`).

- [ ] **T7.5** Verify hệ thống hoạt động ổn định trên cloud:
  - Chạy lại ít nhất 5 experiment runs trên cloud.
  - So sánh MTTD/MTTR giữa local K3d và cloud K3s/DOKS.

### 2.2. Domain & SSL (Tùy chọn)

- [ ] **T7.6** Gắn domain cho Grafana dashboard và Frontend:
  - Mua domain (hoặc dùng free subdomain từ DuckDNS/nip.io).
  - Cấu hình Nginx Ingress + cert-manager cho Let's Encrypt TLS.

### 2.3. Demo Video Production

- [ ] **T7.7** Chuẩn bị kịch bản Demo Video (5-10 phút):
  - Giới thiệu đề tài, kiến trúc Multi-Agent.
  - Steady-state của target app Boutique qua Ingress port 8080.
  - Attack Phase: Nemesis gọi Gemini 3.1 sinh payload, Gaia Observer phát hiện anomalies.
  - Heal Phase: Hephaestus nhận alert, scale up pod tự động trong 1 giây.
  - Chứng minh sập trang (502/503) và phục hồi khi bị Pod Kill.

- [ ] **T7.8** Quay video demo:
  - Sử dụng OBS Studio hoặc tool record màn hình.
  - Split screen: Terminal (kubectl) bên trái + Dashboard bên phải.

### 2.4. Báo cáo Nghiên cứu Khoa học

- [ ] **T7.9** Hoàn thiện cấu trúc báo cáo NCKH 6 chương.
- [ ] **T7.10** Đưa dữ liệu thí nghiệm (Phase 5) và so sánh Downtime Ingress thực tế vào Chương 5.
- [ ] **T7.11** Viết phần **Giới hạn nghiên cứu** (validate trên sandbox, 3 loại tấn công, single cluster, LLM prompt latency).
- [ ] **T7.12** Viết phần **Hướng phát triển tương lai** (mô hình SaaS Control Plane, WebSocket Agent kết nối từ xa, APM SDK thu thập metrics trực tiếp từ code).

### 2.5. Bài Thuyết trình (Defense Presentation)

- [ ] **T7.13** Chuẩn bị slide thuyết trình (15-20 slides).
- [ ] **T7.14** Chuẩn bị **câu hỏi phản biện thường gặp** từ Hội đồng và câu trả lời.

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase — Hoàn thành dự án)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Hệ thống chạy thành công trên Cloud | `kubectl get pods -A` trên cloud cluster $\rightarrow$ all Running |
| 2 | Cloud experiment runs cho MTTD/MTTR tương đương local | Bảng so sánh local vs cloud |
| 3 | Demo video hoàn thành (5-10 phút) | File MP4 trong repo/docs |
| 4 | Báo cáo NCKH hoàn thành đầy đủ 6 chương | File PDF/Word |
| 5 | Slide thuyết trình hoàn thành | File PowerPoint/PDF |
| 6 | Source code commit final trên GitHub | Git tag `v1.0.0` |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Kubernetes API trên Cloud có cơ chế cân bằng tải (Cloud LoadBalancer) tự động. Làm thế nào để cấu hình Ingress tận dụng IP tĩnh của LoadBalancer?
> _Trả lời:_

### Q2: Hội đồng hỏi "Tại sao em lại chọn DigitalOcean để deploy thử nghiệm trước thay vì chạy thẳng lên AWS EKS?".
> _Trả lời:_

---

## 5. Budget Summary (FinOps Tổng kết)

| Hạng mục | Chi phí ước tính | Ghi chú |
|---|---|---|
| Cloud K8s cluster (DOKS hoặc EC2, 2 tháng) | ~$20-30 | Chỉ chạy khi cần demo/test |
| Domain (tùy chọn) | 0 - $10 | DuckDNS free hoặc mua domain rẻ |
| Gemini / OpenAI API tokens | ~$10-20 | Giới hạn sử dụng, dùng Ollama local khi dev |
| **Tổng Phase 7** | **< $60** | Nằm trong budget 4.9M VNĐ ban đầu |
