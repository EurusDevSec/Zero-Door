# 🎬 KỊCH BẢN DEMO BẢO VỆ ĐỀ TÀI: ZERO DOOR
> **Tài liệu hướng dẫn thuyết trình & thực hành từng bước (Phiên bản mới nhất — có Web Dashboard)**
> *Dành cho EurusDevSec & hp8001 báo cáo trước Hội đồng nghiệm thu*

---

## 🛠️ PHẦN 1: CHUẨN BỊ TRƯỚC DEMO (10 PHÚT TRƯỚC BÁO CÁO)

### 1. Khởi động Docker Desktop & Kiểm tra cụm K3d
```bash
# Kiểm tra trạng thái các node
kubectl get nodes
# Dự kiến: 3 nodes (1 server, 2 agents) trạng thái Ready

# Kiểm tra tất cả pods đang chạy ổn định
kubectl get pods -A
# Đảm bảo pods ở zero-door, target-app, monitoring đều ở trạng thái "Running"
```

### 2. Thiết lập Port-Forward kết nối các dịch vụ
Mở **5 terminal riêng biệt**, mỗi terminal chạy một lệnh sau (giữ ngầm suốt buổi demo):
```bash
# Terminal 1: Prometheus (Cổng 9090)
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring

# Terminal 2: Ứng dụng mục tiêu Online Boutique (Cổng 8080)
kubectl port-forward svc/frontend 8080:80 -n target-app

# Terminal 3: Agent Nemesis — Attacker + Dashboard (Cổng 9092)
kubectl port-forward svc/nemesis 9092:8000 -n zero-door

# Terminal 4: Agent Hephaestus — Defender (Cổng 9091)
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door

# Terminal 5 (tuỳ chọn — để debug): Theo dõi logs Hephaestus
kubectl logs -n zero-door -l app=hephaestus -f --tail=30
```

### 3. Chuẩn bị các cửa sổ trình duyệt (Tabs)
Mở trình duyệt với **3 tab**:

| Tab | URL | Mục đích |
|---|---|---|
| 1 | `http://localhost:8080` | Ứng dụng mục tiêu — Google Online Boutique |
| 2 | `http://localhost:9092/dashboard/` | ⭐ **Zero Door Control Center** (tab chính) |
| 3 | `http://localhost:9090` | Prometheus (nếu cần chứng minh nâng cao) |

> **⭐ Lưu ý quan trọng:** Tab số 2 (`http://localhost:9092/dashboard/`) chính là **trung tâm chỉ huy duy nhất** cần trình chiếu trong toàn bộ buổi demo. Mọi thao tác bắt đầu từ đây!

---

## 🚀 PHẦN 2: THỰC HÀNH DEMO & LỜI THOẠI THUYẾT TRÌNH (5 - 7 PHÚT)

---

### BƯỚC 1: GIỚI THIỆU TRẠNG THÁI BÌNH THƯỜNG (STEADY STATE) — 1 PHÚT

**Hành động trên màn hình:**
1. Mở Tab 1 (`http://localhost:8080`), click thử mua vài sản phẩm để chứng minh web bình thường.
2. Chuyển sang Tab 2 — **Zero Door Control Center Dashboard**.
3. Chỉ vào **panel "Target-App Microservices Status"**: tất cả các service đang hiển thị CPU thấp và 1 Pod/replica.
4. Chỉ vào **"Platform Status"** (góc dưới bên trái): chứng minh đã tích hợp Gemini 3.1 với Round Robin 2 API Keys và hệ thống Defender đang sẵn sàng.

**Lời thoại (Talking Points):**
> *"Kính thưa Hội đồng, đây là **Zero Door Control Center** — giao diện giám sát và điều phối tập trung của hệ thống. Ứng dụng mục tiêu là Google Online Boutique chạy trong namespace `target-app` với 9 microservice. Toàn bộ trạng thái CPU và Replicas của từng service được hiển thị trực tiếp, cập nhật mỗi 3 giây từ Prometheus.*
>
> *Agent phòng thủ Hephaestus đang ở trạng thái Active. AI Model đã sẵn sàng — Gemini 3.1 kết nối qua cơ chế Round Robin 2 API Key để tránh Rate Limiting. Hệ thống đang ở Steady State hoàn toàn bình thường."*

---

### BƯỚC 2: NEMESIS KÍCH HOẠT TẤN CÔNG BẰNG AI (ATTACK PHASE) — 1.5 PHÚT

**Hành động trên màn hình:**
1. Vẫn ở Tab 2 Dashboard.
2. Nhấp nút **`🧠 Trigger Gemini-3.1 Attack`** (nút tím lớn góc trên bên trái).
3. Quan sát:
   - Node **Nemesis** và node **Gemini** trên sơ đồ Workflow Graph bắt đầu nhấp nháy tím.
   - Cửa sổ **Integrated Agent Log Console** (cuối trang) bắt đầu xuất hiện log:
     - `[NEMESIS] Round Robin: Using Gemini API key: AQ.Ab8...`
     - `[NEMESIS] Gemini selected target: cartservice | Attack: CPU_STRESS`
   - Node **Kafka** và **Chaos Worker** bắt đầu nhấp nháy đỏ.

**Lời thoại (Talking Points):**
> *"Em vừa kích hoạt **Agent Nemesis** ở chế độ AI Planning. Ngay lập tức, Nemesis gọi API Gemini 3.1 (thế hệ model mới nhất của Google) và truyền vào toàn bộ dữ liệu metrics hệ thống từ Prometheus — bao gồm CPU, RAM, HTTP Error Rate của từng microservice.*
>
> *Gemini phân tích và **tự quyết định chiến lược tấn công**: nó xác định `cartservice` (dịch vụ giỏ hàng) đang có traffic cao nhất và giới hạn tài nguyên thấp nhất → đây là điểm yếu nhất của hệ thống. Gemini lập kế hoạch ép CPU_STRESS vào đây.*
>
> *Lệnh tấn công được đóng gói JSON và gửi vào Kafka. Chaos Worker nhận lệnh, kiểm tra an toàn (Blast Radius Validation) và deploy một pod ép CPU vào `cartservice`."*

---

### BƯỚC 3: GAIA PHÁT HIỆN BẤT THƯỜNG (DETECTION PHASE) — 1 PHÚT

**Hành động trên màn hình:**
1. Quan sát **panel "Target-App Microservices Status"** trên Dashboard:
   - Card của `cartservice` bắt đầu chuyển sang màu đỏ.
   - Thanh Progress Bar CPU nhảy vọt lên > 100%.
   - Số pod vẫn là 1 (chưa được scale).
2. Quan sát node **Gaia** trên Workflow Graph bắt đầu nhấp nháy vàng (Warning state).
3. Log Console hiện dòng:
   - `[GAIA] ALERT: CPU utilization of 'cartservice' is at 233% (limit: 0.2 cores)`

**Lời thoại (Talking Points):**
> *"Ngay khi Chaos Worker ép CPU `cartservice`, hệ thống phản ứng tức thì. **Agent Gaia** — Observer liên tục quét Prometheus mỗi vài giây — phát hiện CPU của `cartservice` đã vọt lên 233%, vượt qua ngưỡng cảnh báo 80% của giới hạn tài nguyên.*
>
> *Dashboard tự động cập nhật — Card `cartservice` chuyển sang màu đỏ và nhấp nháy cảnh báo. Đây là sự kiện anomaly được phát hiện thời gian thực (MTTD dưới 25 giây) mà không cần con người theo dõi."*

---

### BƯỚC 4: HEPHAESTUS TỰ ĐỘNG VÁ LỖI (HEALING PHASE) — 1.5 PHÚT

**Hành động trên màn hình:**
1. Quan sát node **Hephaestus** trên Workflow Graph bắt đầu nhấp nháy xanh lam (Active state).
2. Panel `cartservice` trên Dashboard: số **Pods tăng từ 1 lên 2** — hiển thị badge xanh "2 Pods".
3. Sau khoảng 60 giây, Chaos Worker dừng lại, CPU bắt đầu giảm xuống, card trở về xanh.
4. Log Console hiện ra chuỗi sự kiện:
   - `[HEPHAESTUS] Received Alert: HIGH_CPU on cartservice`
   - `[HEPHAESTUS] Decision: SCALE_UP deployment cartservice`
   - `[HEPHAESTUS] Action SCALE_UP on cartservice -> SUCCESS`

**Lời thoại (Talking Points):**
> *"Khi cảnh báo xuất hiện trên Kafka topic `monitoring.alerts`, **Agent Hephaestus** lập tức kích hoạt. Không cần con người can thiệp.*
>
> *Dựa trên Decision Matrix, với lỗi `HIGH_CPU`, Hephaestus tự động gọi Kubernetes API để **Scale Up** deployment `cartservice` từ 1 lên 2 replicas. Dashboard ngay lập tức hiển thị badge "2 Pods" trên card của `cartservice`.*
>
> *Toàn bộ quy trình Phát hiện → Ra quyết định → Vá lỗi diễn ra hoàn toàn tự động, khép kín, không cần một dòng lệnh thủ công nào. MTTR chỉ mất **dưới 2 giây** kể từ khi Hephaestus nhận được cảnh báo."*

---

### BƯỚC 5 (TÙY CHỌN NÂNG CAO): ĐẶT LẠI & THỬ TẤN CÔNG THỦ CÔNG

**Hành động trên màn hình:**
1. Nhấn nút **`↺ Reset System (Steady State)`** (nút đỏ dưới cùng của Control Panel) để xóa cooldown của Hephaestus và buffer log.
2. Chọn thủ công từ dropdown: Attack Type = `POD_KILL`, Service = `checkoutservice`.
3. Nhấn **`⚡ Inject Failure Script`** để thấy Hephaestus xử lý Pod Restart.

**Lời thoại:**
> *"Ngoài mode AI Planning tự động, hệ thống còn hỗ trợ chế độ Simulation thủ công. Ở đây em có thể chọn bất kỳ loại tấn công nào (CPU Stress, HTTP Flood, Pod Kill) vào bất kỳ service nào trong hệ thống. Đây mô phỏng tình huống Red Team kiểm thử có kiểm soát."*

---

### BƯỚC 6: TỔNG KẾT KẾT QUẢ THỰC NGHIỆM (WAR GAME STATS) — 1 PHÚT

**Hành động trên màn hình:**
- Mở slide hoặc thư mục `docs/experiments/analysis/` hiển thị kết quả đo lường:
  - `mttd_comparison.png` — So sánh MTTD (Manual vs Auto)
  - `mttr_comparison.png` — So sánh MTTR (Manual vs Auto)

**Lời thoại (Talking Points):**
> *"Để chứng minh tính thuyết phục khoa học, nhóm em đã xây dựng script thử nghiệm tự động chạy **40 kịch bản sự cố** khác nhau và so sánh giữa tự chữa trị với vận hành thủ công (Manual SRE).*
>
> *Kết quả đo lường:*
> - *MTTD giảm từ vài phút xuống còn **dưới 25 giây**.*
> - *MTTR của hệ thống Zero Door chỉ mất **1.01 giây** — nhanh gấp hàng trăm lần so với con người.*
> - *Uptime duy trì **100%** trong suốt tất cả kịch bản tấn công.*
>
> *Đề tài chứng minh sự khả thi của mô hình Multi-Agent tự trị trong DevSecOps — hướng tới giảm thiểu chi phí vận hành SRE và loại bỏ rủi ro do yếu tố con người. Nhóm em xin chân thành cảm ơn Hội đồng, sẵn sàng nhận câu hỏi phản biện ạ!"*

---

## 🔧 XỬ LÝ TÌNH HUỐNG KHẨN CẤP TRONG DEMO

| Tình huống | Cách xử lý nhanh |
|---|---|
| Dashboard không load (`9092`) | Kiểm tra terminal port-forward Nemesis còn sống không. Nếu chết thì chạy lại: `kubectl port-forward svc/nemesis 9092:8000 -n zero-door` |
| Log Console trống | Bấm nút "Reset" rồi thử lại Trigger Attack |
| Hephaestus không scale up | Kiểm tra cooldown: `curl http://localhost:9091/healthz` — nếu cần, nhấn Reset System |
| CPU không tăng sau attack | Confirm pod stress đang chạy: `kubectl get pods -n zero-door` — phải có pod `cartservice-stress-*` |
| Gemini API timeout | Round Robin tự chuyển sang key 2, thử lại 1 lần nữa sau 5 giây |

---

## 📋 CHECKLIST CUỐI — TRƯỚC KHI BẮT ĐẦU TRÌNH BÀY

- [ ] Docker Desktop đang chạy
- [ ] K3d cluster `zero-door` đang online (`kubectl get nodes`)
- [ ] Tất cả pods ở trạng thái `Running` (`kubectl get pods -A`)
- [ ] 5 terminal port-forward đang chạy ngầm
- [ ] Tab 1: `http://localhost:8080` (Boutique) tải được
- [ ] Tab 2: `http://localhost:9092/dashboard/` (Dashboard) hiển thị đầy đủ metrics
- [ ] Slide bài thuyết trình đã mở sẵn
- [ ] Tất cả lời thoại đã được luyện tập trước ít nhất 1 lần
