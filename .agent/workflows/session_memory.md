# 💾 SESSION MEMORY — Zero Door Project
> Last Checkpoint: 2026-06-18 | Status: Phase 1 (Foundation & Infrastructure Setup) — In Progress

---

## ⚡ Active Task Completed (Những việc ĐÃ HOÀN THÀNH trong session)
*   **Architecture Realignment (Căn chỉnh Kiến trúc & FinOps):**
    *   Thống nhất tư duy thiết kế **Local-First, Cloud-Ready** để tối ưu hóa chi phí (FinOps) và tốc độ phát triển.
    *   Quyết định chạy dự án ở local trên **K3d (k3d-config.yaml)**. Khi deploy AWS (Production), sẽ chạy lightweight **K3s trên 1 máy EC2 Spot Instance duy nhất** (t3.medium/t3.large, chi phí ~$15/tháng) thay vì dùng EKS ($73/tháng) và Amazon MSK ($100+/tháng) nhằm tránh over-engineering và lãng phí ngân sách.
    *   Phác thảo cấu trúc 5 sơ đồ kiến trúc thực tế: Sơ đồ hạ tầng (EC2/K3s), Sơ đồ logic (C4 Model Container Diagram), Sơ đồ luồng dữ liệu (Attack -> Detect -> Heal), Sơ đồ CI/CD, và Sơ đồ Observability.
    *   Tái cấu trúc và tối ưu hóa thư mục cấu hình AI Agent (`.agent/`) sang dự án Zero Door để tối ưu hóa token và chống ảo giác (hallucination) cho các session tiếp theo.

## 🧠 Semantic Context Essence (Tinh túy kiến thức & Quyết định thiết kế)
*   *FinOps Decision:* Tránh xa các managed service đắt đỏ của AWS (EKS, MSK, RDS) ở giai đoạn nghiên cứu/sandbox. Đóng gói toàn bộ cơ sở hạ tầng (Kafka, Postgres, Prometheus) vào Helm Charts và tự chạy trong cluster K3s/K3d.
*   *Security RBAC boundary:* Agent Hephaestus và Chaos Worker tuyệt đối không dùng ClusterAdmin role. Phải dùng namespace Role giới hạn quyền trong namespace `target-app`.
*   *Local-First development loop:* Toàn bộ code Java (Spring Boot) và Go (Chaos Worker) phải chạy thử nghiệm thành công và ổn định ở local K3d trước khi viết pipeline CI/CD đẩy lên AWS.

## 🔜 Next Steps (3 hành động kỹ thuật trực tiếp kế tiếp)
- [ ] **Step 1:** Khởi chạy cluster local K3d bằng file [k3d-config.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/k3d-config.yaml) và kiểm tra kết nối `kubectl cluster-info`.
- [ ] **Step 2:** Viết kịch bản Deploy Kafka Helm Chart (Bitnami) vào namespace `zero-door` và cấu hình 5 Kafka topics (`attack.commands`, `attack.results`, `monitoring.alerts`, `healing.actions`, `system.logs`).
- [ ] **Step 3:** Deploy Prometheus + Grafana (Kube-Prometheus-Stack Helm chart) vào namespace `monitoring` và cấu hình scrapers cơ bản.
