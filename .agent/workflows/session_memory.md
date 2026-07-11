# 💾 SESSION_MEMORY.md — Trạng Trạng Thái Hiện Tại
> *Last updated: 2026-07-11 17:00 GMT+7 | Phase 6 COMPLETED — Automated CI/CD & DevOps Security Optimization | Next: Phase 7 Cloud*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Phase 6 hoàn thành xuất sắc. Chuẩn bị Phase 7 (Cloud Deployment & Final Scientific Report).

**Phase vừa hoàn thành**:
1.  **Hạ tầng Ingress**: Expose dịch vụ `frontend` (Target App) qua **Nginx Ingress** trên cổng `8080` của host. Loại bỏ hoàn toàn sự phụ thuộc vào lệnh `kubectl port-forward` dễ bị đứt kết nối vĩnh viễn khi POD_KILL. Trang web sập trả về `502/503` thực sự và tự phục hồi về `200 OK` mượt mà trong **`1.34 giây`** downtime.
2.  **Sửa lỗi dịch vụ 'None'**: Cấu hình Nemesis query Prometheus cào CPU theo `by (pod)` thay vì `by (deployment)` không tồn tại, trích xuất chính xác tên dịch vụ microservice hiển thị trong bong bóng chat logic.
3.  **Ổn định CI/CD**: Loại bỏ `cache` cấu hình trong `actions/setup-python` của file `ci.yml` do bước Post-run lưu cache liên tục bị lỗi tranh chấp key làm sập build, giúp toàn bộ pipeline GitHub Actions xanh lét 100%.
4.  **Tái cấu trúc Phase**: Restructure Phase 6 thành `phase6_cicd_optimization.md` và tạo mới Phase 7 `phase7_cloud_report.md` trong thư mục `docs/phases/`.

**Git branch**: `main` (Sạch sẽ, đã commit và push thành công lên GitHub).

---

## ⚡ Những việc ĐÃ HOÀN THÀNH trong session này (2026-07-11)

### ⚙️ Hạ tầng & SRE
- **Tạo Ingress manifest cho frontend**: [target-app-ingress.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/target-app-ingress.yaml) giúp định tuyến `/` vào Boutique App thông qua Nginx Ingress.
- **Cải tiến start-demo.ps1**: Bỏ port-forward cho frontend trên cổng 8080, tận dụng Nginx Ingress, khởi động dashboard nhanh hơn và chống kẹt cổng.
- **Sửa lỗi Prometheus query trong main.py**: Sửa query CPU theo pod name và filter regex trong Nemesis API để giải quyết triệt để lỗi tên service `'None'`.
- **Tắt cache GitHub Actions**: Tối ưu hóa file [ci.yml](file:///r:/_Projects/Eurus_Workspace/zero_door/.github/workflows/ci.yml) để tránh lỗi post-run cache save.
- **Chạy thực nghiệm & Báo cáo timeline**: Viết các python test script (`test_protected_kill.py`, `test_perfect_demo.py`) để đo lường downtime/latency và tự động phục hồi.

### 📝 Tài liệu
- **README.md** và **docs/demo_script.md**: Viết lại cấu trúc tài liệu, đồng bộ hóa kịch bản chạy demo Ingress và kết quả wargame KPIs.
- **docs/phases/**: Tái cấu trúc Phase 6 và 7 để mô tả sâu sắc các tiêu chí DevOps nâng cao (Distroless, SAST scans, WebSocket Agent, APM SDK).

---

## 🧠 Semantic Context Essence

- **Port-forward pattern**: Dashboard Nemesis (9092), Hephaestus (9091), Prometheus (9090). Target App truy cập trực tiếp qua `http://localhost:8080/` (không cần port-forward nhờ Ingress).
- **Hysteresis / Data Lag**: Metrics CPU trung bình `[2m]` của Prometheus mất từ 15-30 giây để decay về zero sau khi reset. Điều này khiến Gaia/Hephaestus có thể tự động scale up lại ngay sau khi reset nếu không tắt HPA/Hephaestus tạm thời trong lúc test.
- **ResourceQuota Limits**: Namespace `target-app` bị giới hạn CPU limits ở mức `3 cores` (`target-app-quota`). Tấn công `CPU_STRESS` ở mức `HIGH` (yêu cầu 1 core) sẽ bị Kubernetes Admission Controller từ chối thẳng thừng (`exceeded quota`) nếu tổng CPU các pod đang dùng vượt quá 2 cores $\rightarrow$ Cần gọi `Reset System` trước khi chạy attack để giải phóng quota.

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------| 
| `infrastructure/manifests/target-app-ingress.yaml` | **MỚI** — Ingress rule cho frontend | Expose cổng 8080 qua Nginx |
| `agent-orchestrator/nemesis/main.py` | Attacker API | Sửa lỗi query cAdvisor `by (pod)` |
| `.github/workflows/ci.yml` | GitHub Actions CI | Tắt pip cache để ổn định build |
| `start-demo.ps1` | 1-click launcher | Bỏ port-forward 8080, dùng Ingress |
| `docs/phases/phase6_cicd_optimization.md` | **MỚI** — DevOps & CI/CD Specs | Tích hợp các đề xuất bảo mật nâng cao |
| `docs/phases/phase7_cloud_report.md` | **MỚI** — Cloud Deployment Specs | Di chuyển từ Phase 6 cũ sang |

---

## 🔜 Next Steps (ưu tiên tiếp theo)

- [ ] **DevSecOps Integration**: Tích hợp các bộ quét tĩnh SAST (`gosec`/`bandit`) và K8s manifest scanning (`trivy`/`checkov`) vào file `ci.yml`.
- [ ] **SaaS Agent Architecture**: Thiết kế và triển khai WebSocket client cho Hephaestus để phục vụ kết nối Outbound bảo mật từ cụm của khách hàng.
- [ ] **Phase 7 Cloud**: Deploy Helm charts lên cụm Kubernetes Cloud thực tế (AWS EKS hoặc DigitalOcean Kubernetes) và lập bảng so sánh hiệu năng.
