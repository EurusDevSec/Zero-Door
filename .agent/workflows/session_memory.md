# 💾 SESSION_MEMORY.md — Trạng Thái Hiện Tại
> *Last updated: 2026-07-14 21:58 GMT+7 | Phase 6 COMPLETED — Visual Proofs, Chapter 4 & 5 Integrated | Next: Phase 7 Cloud*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Phase 6 hoàn thành 100%. Đã chèn đầy đủ tất cả các hình ảnh thực tế, biểu đồ phân tích thực nghiệm và sửa đổi các chương báo cáo khoa học (Chương 1 đến Chương 6) khớp hoàn toàn với số liệu của dự án. Chuẩn bị chuyển giao sang Phase 7 (Cloud Deployment).

**Phase vừa hoàn thành**:
1.  **Chèn hình ảnh Docker Desktop (Hình 4.4)**: Thêm minh chứng trực quan ảo hóa cụm K3d từ các container vật lý trên Docker Desktop và tịnh tiến số thứ tự hình tiếp theo.
2.  **Chèn 4 biểu đồ thực nghiệm Chương 5 (Hình 5.1 - 5.4)**: Tích hợp các đồ thị phân phối MTTD (Boxplot), so sánh MTTR trung bình, tỷ lệ Uptime E4 và Heal Success Rate.
3.  **Lọc dữ liệu thô thực nghiệm**: Loại bỏ tệp test chạy thử đơn lẻ `results_20260712T100633.csv` trong namespace `e2_http_flood` (lưu trữ vào `scratch/`).
4.  **Chạy lại và Tái sinh Phân tích**: Thực thi thành công `analysis.py` trên tập dữ liệu chuẩn 40 lượt chạy (5 lượt chạy cho mỗi kịch bản/chế độ). Giúp khôi phục Uptime kịch bản E2 AUTO về đúng **100%** và số lượt chạy về đúng **5 lượt**, đồng bộ hoàn hảo với báo cáo.
5.  **Rà soát định dạng chú thích**: Loại bỏ toàn bộ dấu ngoặc đơn/ngoặc vuông và ký tự in nghiêng ở toàn bộ các hình ảnh từ Chương 1 đến Chương 5.

**Git branch**: `main` (Sạch sẽ, đã commit và push thành công lên GitHub).

---

## ⚡ Những việc ĐÃ HOÀN THÀNH trong session này (2026-07-14)

### 📝 Đánh giá Kiến trúc & Thiết kế
- **Đánh giá Đề xuất LAB của Thầy (AIOps)**: So sánh hệ thống Zero-Door (Closed-Loop, LLM Multi-Agent, FinOps 157MB RAM) với đề xuất AIOps truyền thống của Thầy (Open-Loop, Log NLP, BERT, yêu cầu 32-64GB RAM). Khẳng định Zero-Door đáp ứng trọn vẹn và tối ưu hơn về mặt tài nguyên và tự động hóa khắc phục.
- **Thiết kế Tích hợp Ansible**: Tư vấn kiến trúc tích hợp Ansible kết hợp cùng Terraform cho Phase 7. Cấu trúc thư mục playbook (`inventory`, `group_vars`, các roles `common`, `docker`, `k3s`, `zero-door`) thay thế Bash scripts/Cloud-init để đảm bảo tính lũy đẳng (idempotency) và tự động hóa chuẩn DevOps.

---

## 🧠 Semantic Context Essence

- **Clean Dataset Rule**: Tránh đưa các lượt test đơn lẻ vào thư mục `docs/experiments/raw_data/` vì `analysis.py` sẽ tự động gộp tất cả tệp CSV và làm sai lệch thống kê 5 lần chạy chính thức.
- **Port-forward pattern**: Dashboard Nemesis (9092), Hephaestus (9091), Prometheus (9090). Target App truy cập trực tiếp qua `http://localhost:8080/` (không cần port-forward nhờ Ingress).
- **Docker Build Cache**: Luôn chạy `.\rebuild-nemesis.ps1` khi sửa code HTML/CSS/JS của dashboard để tránh việc Docker dùng cache cũ làm mất thay đổi static files.
- **ResourceQuota Limits**: Namespace `target-app` bị giới hạn CPU limits ở mức `3 cores` (`target-app-quota`). Cần gọi `Reset System` trước khi chạy attack để giải phóng quota.
- **Monitoring Namespace Quota**: Namespace `monitoring` có ResourceQuota giới hạn `10 CPU / 10Gi RAM` để đủ dung lượng cho Prometheus/Grafana chạy mượt mà.

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------| 
| `docs/research/chapter4.md` | Chương 4 của báo cáo | Bổ sung Hình 4.4, chuẩn hóa số thứ tự và định dạng chú thích |
| `docs/research/chapter5.md` | Chương 5 của báo cáo | Bổ sung Hình 5.1 đến Hình 5.4, chuẩn hóa chú thích hình |
| `docs/experiments/analysis/` | Các biểu đồ thực nghiệm | Biểu đồ MTTD, MTTR, Uptime, Success Rate chuẩn |
| `infrastructure/scripts/analysis.py` | Script sinh biểu đồ | Chạy qua UTF-8 để tránh lỗi unicode trên Windows |
| `scratch/results_20260712T100633.csv` | Tệp test cũ | Đã được di chuyển khỏi thư mục dữ liệu thô |

---

## 🔜 Next Steps (ưu tiên tiếp theo)

- [ ] **Phase 7 Cloud**: Deploy Helm charts lên cụm Kubernetes Cloud thực tế (AWS EKS hoặc DigitalOcean Kubernetes) và lập bảng so sánh hiệu năng.
- [ ] **SaaS Agent Architecture**: Thiết kế và triển khai WebSocket client cho Hephaestus để phục vụ kết nối Outbound bảo mật từ cụm của khách hàng.
- [ ] **DevSecOps Integration**: Hoàn thiện các bộ quét tĩnh SAST (`gosec`/`bandit`) và K8s manifest scanning (`trivy`/`checkov`) vào file `ci.yml`.
