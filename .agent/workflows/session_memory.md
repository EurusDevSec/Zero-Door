# 💾 SESSION_MEMORY.md — Trạng Thế Hiện Tại
> *Last updated: 2026-07-04 | Phase 5 COMPLETED & OPTIMIZED (Local Demo Ready) | Next: Phase 6 Cloud*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Chuẩn bị báo cáo & Demo local + Khởi động Phase 6 (Cloud Deployment).

**Phase vừa hoàn thành**: Khắc phục triệt để các lỗi tích hợp trên Local K3d cluster giúp vòng lặp tự vá lỗi (Nemesis -> Gaia -> Hephaestus) hoạt động tự động 100% không cần giả lập.

**Git branch**: `main`

---

## ⚡ Active Task Completed (Những việc ĐÃ HOÀN THÀNH trong session)

*   **Khắc phục giám sát Prometheus (0 targets):**
    *   Phát hiện NetworkPolicy `allow-prometheus-scraping-egress` thiếu cổng 53 (DNS), 443 (API Server) và 10250 (Kubelet/cAdvisor), chặn đứng Prometheus discovery.
    *   Đã cập nhật [network-policies.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/network-policies.yaml) cho phép Prometheus Egress hoàn toàn tự do (`- {}`). Prometheus hiện cào bình thường với **`18 active targets`**.
*   **Sửa lỗi Kafka Reconnect vô hạn ở Hephaestus:**
    *   Loại bỏ tham số `consumer_timeout_ms` trong [hephaestus/main.py](file:///r:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py) giúp Kafka consumer chạy blocking ổn định, không bị ngắt kết nối và kích hoạt rebalance liên tục nữa.
*   **Khắc phục lỗi gộp tên container (cAdvisor/Gaia overlap):**
    *   Google Boutique Microservices đều đặt tên container mặc định là `server`.
    *   Đã sửa query của Gaia trong [gaia/main.py](file:///r:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/gaia/main.py) nhóm theo cả `pod` và `container`.
*   **Giải quyết bài toán map tự động từ stress pod sang target service:**
    *   Sửa [chaos-worker/internal/attack/cpu_stress.go](file:///r:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/attack/cpu_stress.go) đặt tên stress pod theo định dạng `<targetService>-stress-xxxx` (ví dụ `cartservice-stress-xxxx`).
    *   Cấu hình Gaia tự động giải mã ngược từ tên pod stress để xác định chính xác target service bị ảnh hưởng (ví dụ: `cartservice-stress-xxxx` -> alert `HIGH_CPU` trên `cartservice`).
*   **Xác minh thành công luồng tự vá lỗi:**
    *   Đã chạy thực tế kịch bản: Nemesis trigger CPU stress -> K3d deploy pod `cartservice-stress-xxxx` -> Gaia detect CPU spike -> Hephaestus scale up `cartservice` từ 1 lên 2 replicas tự động hoàn toàn 100%.

---

## 🧠 Semantic Context Essence (Tinh túy kiến thức & Quyết định thiết kế)

*   **Quyết định NetworkPolicy:** Prometheus bắt buộc phải có quyền Egress đến CoreDNS (cổng 53), API Server (cổng 443) và Kubelet (cổng 10250) để Service Discovery và cAdvisor hoạt động.
*   **Cấu hình Kafka:** Không được đặt `consumer_timeout_ms` trong vòng lặp vô hạn ở Kafka consumer của Hephaestus nếu không muốn consumer tự recreate liên tục gây rebalance.
*   **Nhóm metrics:** Đối với Google Boutique, cAdvisor metrics group by `container` sẽ làm mất thông tin service (do tất cả đều dùng tên `server`). Phải group by `pod, container` và parse tên deployment từ pod name.

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------|
| `agent-orchestrator/hephaestus/main.py` | Defender agent | Đã sửa bug Kafka consumer timeout |
| `agent-orchestrator/gaia/main.py` | Observer agent | Đã sửa group metrics query theo pod/container |
| `chaos-worker/internal/attack/cpu_stress.go` | Chaos Executor | Đã sửa cách đặt tên pod stress theo service prefix |
| `infrastructure/manifests/network-policies.yaml` | Network Security | Đã mở Egress hoàn toàn tự do cho Prometheus |
| `docs/demo_script.md` | Hướng dẫn demo | Đã rà soát và khớp 100% với luồng tự vá lỗi thực tế |

---

## 🔜 Next Steps (3 hành động kỹ thuật trực tiếp kế tiếp)
- [ ] **Step 1:** Hỗ trợ EurusDevSec chuẩn bị slide và demo video dựa trên kịch bản [demo_script.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/demo_script.md).
- [ ] **Step 2:** Đóng gói toàn bộ charts bằng Helm (`helm package`) chuẩn bị cho Phase 6.
- [ ] **Step 3:** Bắt đầu setup và deploy hạ tầng trên cloud (GKE/EKS Spot) theo checklist Phase 6.
