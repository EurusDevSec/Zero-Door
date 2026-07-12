# 💾 SESSION_MEMORY.md — Trạng Thái Hiện Tại
> *Last updated: 2026-07-12 17:45 GMT+7 | Phase 6 COMPLETED — Visual Proofs & Automations Added | Next: Phase 7 Cloud*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Phase 6 hoàn thành 100%. Đã bổ sung các minh chứng đồ thị trực quan và các kịch bản thực nghiệm tự phục hồi. Chuẩn bị chuyển giao sang Phase 7 (Cloud Deployment).

**Phase vừa hoàn thành**:
1.  **Hạ tầng Ingress**: Expose dịch vụ `frontend` (Target App) qua Nginx Ingress trên cổng 8080 của host.
2.  **Hardening Container (T6.4)**: Cấu hình multi-stage build và gcr.io/distroless/python3-debian12:nonroot cho toàn bộ Python Agents.
3.  **Tích hợp SAST Scans & IaC Scans (T6.5–T6.6)**: Tích hợp bandit, gosec và Trivy scanner vào CI/CD pipeline.
4.  **Minh chứng Đồ thị Trực quan (Mới)**:
    - Bổ sung **SRE SLOs Monitor Card** tự động tính toán MTTD, MTTR, Uptime và Success Rate từ Hephaestus API history.
    - Tích hợp **Real-time Telemetry Line Chart (Chart.js)** vẽ biểu đồ tải CPU động đổi màu cảnh báo đỏ khi bị stress.
5.  **Kịch bản Tự động hóa**: Viết script [rebuild-nemesis.ps1](file:///r:/_Projects/Eurus_Workspace/zero_door/rebuild-nemesis.ps1) giúp tự động hoá no-cache build và khôi phục cổng port-forward 9092.

**Git branch**: `main` (Sạch sẽ, đã commit và push thành công lên GitHub).

---

## ⚡ Những việc ĐÃ HOÀN THÀNH trong session này (2026-07-12)

### ⚙️ Hạ tầng, SRE & Dashboard
- **Tích hợp Chart.js Telemetry Chart**: Thay thế panel Insights trùng lặp bằng biểu đồ đường biểu diễn CPU usage của service đang được chọn trong 60 giây gần nhất, tự động đổi màu khi bị tấn công.
- **Tích hợp SRE SLOs Card**: Thêm card hiển thị động các KPIs đo đạc từ Hephaestus API (MTTD, MTTR, Success Rate, Uptime SLO) giúp hội đồng dễ theo dõi.
- **Viết API Proxy `/api/heal-history`**: Thêm endpoint vào Nemesis API để giải quyết triệt để lỗi kết nối chéo origin (CORS) từ frontend.
- **Tạo script rebuild-nemesis.ps1**: Tự động hoá các bước build --no-cache, import image, rollout restart và vá tự động port-forward 9092 bị đứt.
- **Chạy thực nghiệm E2**: Xác thực kịch bản HTTP Flood chạy thành công với MTTD 1.0s và MTTR 1.0s.
- **Sửa lỗi CrashLoopBackOff của Prometheus & Grafana**: Phát hiện và vá thành công lỗi sập do quá hạn ngạch ResourceQuota ở namespace `monitoring`. Tăng quota của namespace từ `6 CPU / 6Gi RAM` lên `10 CPU / 10Gi RAM` và nâng cấp giới hạn tài nguyên của Prometheus (`1.5 CPU / 1Gi RAM`) và Grafana (`1 CPU / 512Mi RAM`) chạy siêu mượt.

### 📝 Tài liệu
- **PLAN.md & LESSONS_LEARNED.md**: Cập nhật bài học về lỗi cache static file của Docker build và lỗi đứt port-forward sau rollout restart.

---

## 🧠 Semantic Context Essence

- **Port-forward pattern**: Dashboard Nemesis (9092), Hephaestus (9091), Prometheus (9090). Target App truy cập trực tiếp qua `http://localhost:8080/` (không cần port-forward nhờ Ingress).
- **Docker Build Cache**: Luôn chạy `.\rebuild-nemesis.ps1` khi sửa code HTML/CSS/JS của dashboard để tránh việc Docker dùng cache cũ làm mất thay đổi static files.
- **ResourceQuota Limits**: Namespace `target-app` bị giới hạn CPU limits ở mức `3 cores` (`target-app-quota`). Cần gọi `Reset System` trước khi chạy attack để giải phóng quota.
- **Monitoring Namespace Quota**: Namespace `monitoring` có ResourceQuota giới hạn `10 CPU / 10Gi RAM` để đủ dung lượng cho Prometheus/Grafana chạy mượt mà.

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------| 
| `rebuild-nemesis.ps1` | **MỚI** — Script 1-click rebuild & PF | Build no-cache, restart deployment & PF |
| `agent-orchestrator/nemesis/static/index.html` | Dashboard UI | Thêm SRE SLOs card và canvas Chart.js |
| `agent-orchestrator/nemesis/static/app.js` | Dashboard logic | Thêm logic vẽ chart và parser SLOs |
| `agent-orchestrator/nemesis/main.py` | Attacker API | Thêm proxy API `/api/heal-history` |
| `infrastructure/helm-values/prometheus-values.yaml` | Cấu hình Helm Prometheus/Grafana | Nâng giới hạn tài nguyên CPU/RAM |
| `infrastructure/resource-quotas/monitoring-quota.yaml` | Hạn ngạch tài nguyên namespace monitoring | Nâng giới hạn CPU/RAM quota lên 10 |
| `.agent/rules/LESSONS_LEARNED.md` | Tài liệu bài học | Cập nhật lỗi cache và port-forward |

---

## 🔜 Next Steps (ưu tiên tiếp theo)

- [ ] **Phase 7 Cloud**: Deploy Helm charts lên cụm Kubernetes Cloud thực tế (AWS EKS hoặc DigitalOcean Kubernetes) và lập bảng so sánh hiệu năng.
- [ ] **SaaS Agent Architecture**: Thiết kế và triển khai WebSocket client cho Hephaestus để phục vụ kết nối Outbound bảo mật từ cụm của khách hàng.
- [ ] **DevSecOps Integration**: Hoàn thiện các bộ quét tĩnh SAST (`gosec`/`bandit`) và K8s manifest scanning (`trivy`/`checkov`) vào file `ci.yml`.
