# 💾 SESSION_MEMORY.md — Trạng Thái Hiện Tại
> *Last updated: 2026-07-13 13:25 GMT+7 | Phase 6 COMPLETED — Visual Proofs, Chapter 4 & 5 Integrated | Next: Phase 7 Cloud*

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

## ⚡ Những việc ĐÃ HOÀN THÀNH trong session này (2026-07-13)

### 📝 Báo cáo khoa học & Thực nghiệm
- **Đồng bộ hóa Báo cáo**: Sửa đổi [chapter4.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/research/chapter4.md) để thêm Hình 4.4 và sửa số thứ tự toàn bộ hình phía sau.
- **Tích hợp Biểu đồ Chương 5**: Sửa đổi [chapter5.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/research/chapter5.md) để thêm 4 biểu đồ thực nghiệm sinh bởi matplotlib.
- **Sửa lỗi Lệch số liệu**: Di chuyển tệp test lỗi `results_20260712T100633.csv` sang `scratch/` và tái tạo biểu đồ sạch bằng script `analysis.py` chạy qua môi trường UTF-8.
- **Rà soát chú thích hình**: Đồng bộ hóa toàn bộ caption hình ảnh theo quy chuẩn không để dấu ngoặc.
- **Kiểm tra Chương 6**: Đánh giá và duy trì Chương 6 ở dạng văn bản thuần để bảo đảm chuẩn mực viết luận văn khoa học.

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
