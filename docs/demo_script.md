# 🎬 KỊCH BẢN DEMO BẢO VỆ ĐỀ TÀI: ZERO DOOR
> **Tài liệu hướng dẫn thuyết trình & thực hành từng bước (Phiên bản mới nhất — tích hợp Ingress & AWS Cloudscape Dashboard)**
> *Dành cho EurusDevSec & hp8001 báo cáo trước Hội đồng nghiệm thu*

---

## 🛠️ PHẦN 1: CHUẨN BỊ TRƯỚC DEMO (2 PHÚT)

Nhờ việc tối ưu hóa hạ tầng qua **Nginx Ingress** và tự động hóa bằng PowerShell, bạn không cần gõ từng dòng lệnh port-forward thủ công nữa.

### 1. Khởi động Docker Desktop & Kiểm tra cụm K3d
Đảm bảo Docker Desktop đang chạy. Mở Terminal và chạy:
```powershell
# Kiểm tra trạng thái các node
kubectl get nodes
# Dự kiến: 3 nodes (1 server, 2 agents) trạng thái Ready
```

### 2. Khởi động nhanh bằng Một Nút Bấm
Chạy script tự động hóa trong thư mục gốc của dự án:
```powershell
.\start-demo.ps1
```
**Script sẽ tự động thực hiện:**
1. Quét và dọn sạch các tiến trình `kubectl port-forward` cũ bị kẹt.
2. Khởi tạo port-forward cho các cổng dịch vụ:
   - **`9092`**: Nemesis API & Dashboard.
   - **`9091`**: Hephaestus Defender REST API.
   - **`9090`**: Prometheus Observability.
3. Không cần chạy port-forward cho `frontend` (Target App) vì nó đã được expose mặc định qua **Nginx Ingress** của cụm K3d trực tiếp trên cổng **`8080`** của host.
4. Tự động mở trình duyệt vào trang **Zero Door Control Center Dashboard** (`http://localhost:9092/dashboard/`).

### 3. Các Tabs Trình Duyệt Cần Thiết
| Tab | URL | Mục đích |
|---|---|---|
| 1 | `http://localhost:9092/dashboard/` | ⭐ **Zero Door Control Center** (Tab chính để trình chiếu) |
| 2 | `http://localhost:8080/` | Ứng dụng mục tiêu — Google Online Boutique (qua Ingress) |

---

## 🚀 PHẦN 2: THỰC HÀNH DEMO & LỜI THOẠI THUYẾT TRÌNH (5 - 7 PHÚT)

---

### BƯỚC 1: GIỚI THIỆU TRẠNG THÁI BÌNH THƯỜNG (STEADY STATE) — 1 PHÚT

**Hành động trên màn hình:**
1. Mở Tab 2 (`http://localhost:8080/`), bấm F12 chọn tab **Network** để thấy trang web load cực nhanh (chỉ từ `40ms - 80ms`).
2. Chuyển sang Tab 1 — **Zero Door Control Center Dashboard**.
3. Giới thiệu bố cục 3 cột chuẩn **AWS Cloudscape Light Theme**:
   - **Cột Trái (Sidebar)**: Cấu hình Cluster, Danh sách Microservices Status dọc 290px rõ nét.
   - **Cột Giữa**: Sơ đồ Topology tương tác thời gian thực, Control Panel, Console Log ở dưới.
   - **Cột Phải**: Agent Reasoning Chat Panel (có thể click thu gọn/mở rộng mượt mà).
4. Chỉ vào **Platform Status** ở góc dưới bên trái: chứng minh Gemini 3.1 kết nối sẵn sàng.

**Lời thoại (Talking Points):**
> *"Kính thưa Hội đồng, đây là **Zero Door Control Center** — trung tâm chỉ huy và giám sát tự trị của dự án. Hệ thống được thiết kế theo chuẩn giao diện AWS Cloudscape Light Theme tối giản, chia làm 3 cột trực quan.*
>
> *Ứng dụng mục tiêu là Google Online Boutique đang chạy ổn định trên cổng 8080 qua Nginx Ingress. Tại cột bên trái, chúng ta thấy trạng thái tài nguyên thực tế của toàn bộ microservices được cào trực tiếp từ Prometheus. Agent Hephaestus (Defender) đang ở trạng thái Active và AI Model Gemini 3.1 đã sẵn sàng để ứng phó sự cố."*

---

### BƯỚC 2: NEMESIS KÍCH HOẠT TẤN CÔNG BẰNG AI (ATTACK PHASE) — 1.5 PHÚT

**Hành động trên màn hình:**
1. Vẫn ở Tab 1 Dashboard. Nhấp nút **`🧠 Trigger Gemini Attack`** (nút tím lớn).
2. Quan sát:
   - Sơ đồ Topology hiển thị luồng kết nối động: Nemesis và Gemini nhấp nháy tím.
   - Panel **Agent Reasoning Chat** bên phải lập tức hiện bong bóng phân tích của **NEMESIS (ATTACKER)** bằng Tiếng Việt:
     - *"Dịch vụ productcatalogservice thường là nút thắt cổ chai khi tải tăng cao, việc gây áp lực CPU sẽ kiểm tra khả năng phục hồi..."*
   - Log Console hiện log Chaos Worker bắt đầu kích hoạt cuộc tấn công.

**Lời thoại (Talking Points):**
> *"Em vừa kích hoạt **Agent Nemesis** ở chế độ tự động. Ngay lập tức, Nemesis gọi API Gemini 3.1, truyền vào các số liệu giám sát của cụm. Gemini phân tích và tự quyết định mục tiêu: nó phát hiện dịch vụ `productcatalogservice` (hoặc `cartservice`) là nút thắt cổ chai dễ sập nhất nếu bị quá tải.*
>
> *Gemini lập kế hoạch tấn công và gửi thông điệp vào Kafka. Chaos Worker nhận lệnh và deploy một stress container để vắt kiệt CPU của dịch vụ mục tiêu."*

---

### BƯỚC 3: GAIA PHÁT HIỆN BẤT THƯỜNG (DETECTION PHASE) — 1 PHÚT

**Hành động trên màn hình:**
1. Quan sát **Microservices Status** ở cột trái:
   - Dịch vụ mục tiêu chuyển sang màu đỏ rực, thanh CPU Usage vọt lên > 100%.
2. Sơ đồ Topology: Node **Gaia Agent** chuyển sang màu vàng nhấp nháy.
3. Panel **Agent Reasoning Chat** xuất hiện suy luận của **GAIA (OBSERVER)**:
   - *"Phát hiện bất thường hiệu năng tại dịch vụ 'productcatalogservice'. Chỉ số CPU usage thực tế đo được từ Prometheus tăng vọt, vượt xa ngưỡng cảnh báo an toàn. Gửi yêu cầu tự phục hồi tới Hephaestus."*

**Lời thoại (Talking Points):**
> *"Ngay khi cuộc tấn công diễn ra, **Agent Gaia (Observer)** liên tục cào Prometheus với chu kỳ quét 15 giây và phân tích dữ liệu range vector `[2m]` để lọc nhiễu. Gaia phát hiện CPU của dịch vụ đã vượt ngưỡng an toàn và lập tức gửi cảnh báo sự cố lên Kafka topic `monitoring.alerts`."*

---

### BƯỚC 4: HEPHAESTUS TỰ ĐỘNG VÁ LỖI (HEALING PHASE) — 1.5 PHÚT

**Hành động trên màn hình:**
1. Sơ đồ Topology: Node **Hephaestus** nhấp nháy xanh lam.
2. Panel **Agent Reasoning Chat** hiển thị log của **HEPHAESTUS (DEFENDER)**:
   - *"Phát hiện tài nguyên của dịch vụ quá tải nghiêm trọng. Thực hiện scale up tăng số lượng Pods để phân chia tải, tránh nghẽn luồng và duy trì hoạt động."*
3. Cột bên trái: Số lượng Pods của dịch vụ tự động tăng từ **1 Pod lên 3 Pods** (badge xanh cập nhật thời gian thực).

**Lời thoại (Talking Points):**
> *"Nhận được cảnh báo từ Kafka, **Agent Hephaestus (Defender)** kích hoạt quy trình tự vá lỗi. Hephaestus gọi Kubernetes API thực hiện hành động **SCALE_UP**, nâng số lượng Pods từ 1 lên 3.*
>
> *Quy trình vá lỗi này diễn ra hoàn toàn tự động chỉ trong vòng **1.01 giây** kể từ khi nhận cảnh báo. Trong vòng chưa đầy 2 giây, số Pod đã được tăng lên 3 để chia tải."*

---

### BƯỚC 5: KIỂM CHỨNG TRỰC QUAN TRÊN TRÌNH DUYỆT CỦA HỘI ĐỒNG — 1.5 PHÚT

Đây là phần thuyết phục nhất để chứng minh hệ thống tự phục hồi thực sự chứ không phải chạy giả lập.

#### Kịch bản 1: Tấn công sập mạng POD_KILL qua Ingress
1. Nhấn **`RESET SYSTEM (STEADY STATE)`** trên Dashboard để đưa hệ thống về 1 Pod.
2. Chọn thủ công: Attack Type = **`Pod Kill`**, Service = **`frontend`**, Intensity = **`High`** và nhấn **`Inject Failure Script`**.
3. **Sang Tab 2 (`http://localhost:8080/`) và nhấn F5 liên tục**:
   - Trình duyệt lập tức hiển thị màn hình lỗi trắng **`502 Bad Gateway`** hoặc **`503 Service Unavailable`** từ Nginx Ingress.
   - Chỉ trong vòng **1.34 giây (Downtime)**, Kubernetes phục hồi lại Pod mới. Ingress tự động chuyển hướng kết nối.
   - Bạn nhấn F5 tiếp $\rightarrow$ Trang web **tự động hoạt động bình thường trở lại** mà không bị mất kết nối vĩnh viễn (như khi dùng port-forward cũ).

#### Kịch bản 2: Tấn công quá tải HTTP_FLOOD gây nghẽn mạng
1. Chọn thủ công: Attack Type = **`HTTP Flood`**, Service = **`frontend`**, Intensity = **`High`** và nhấn **`Inject Failure Script`**.
2. **F5 liên tục trang Boutique App và quan sát Network Tab (F12)**:
   - Bạn sẽ thấy tổng thời gian load trang (`Load Time` ở dưới cùng) nhảy vọt lên **`3000ms (3 giây)`**, trang web load xoay vòng rất lag do nghẽn CPU.
   - Đợi 20 giây để Gaia báo động và Hephaestus scale up lên 3 Pods.
   - F5 lại trang web $\rightarrow$ Load time lập tức **tụt sâu về mức `500ms`** mượt mà (hệ thống đã tự gánh tải thành công).

---

### BƯỚC 6: TỔNG KẾT KẾT QUẢ THỰC NGHIỆM — 1 PHÚT

**Lời thoại (Talking Points):**
> *"Nhóm chúng em đã tự động hóa chạy **40 kịch bản sự cố** khác nhau để thu thập dữ liệu so sánh giữa hệ thống tự trị với vận hành thủ công (Manual SRE).*
>
> *Kết quả thực nghiệm cho thấy:*
> - *MTTD (Thời gian phát hiện) giảm từ vài phút xuống còn **dưới 25 giây**.*
> - *MTTR (Thời gian tự vá lỗi) của Hephaestus chỉ mất trung bình **1.01 giây**.*
> - *Downtime thực tế khi bị Pod Kill được khống chế ở mức cực thấp **1.34 giây** nhờ Nginx Ingress điều phối.*
>
> *Đề tài đã chứng minh sự khả thi vượt trội của mô hình Multi-Agent tự trị trong việc tối ưu hóa vận hành hệ thống DevSecOps. Em xin chân thành cảm ơn Hội đồng!"*

---

## 🔧 XỬ LÝ TÌNH HUỐNG KHẨN CẤP TRONG DEMO

| Tình huống | Nguyên nhân | Cách xử lý nhanh |
|---|---|---|
| Lỗi `exceeded quota: target-app-quota` khi chạy CPU stress | Quên chưa reset hệ thống, số Pod scale up chiếm hết hạn ngạch CPU của namespace (hạn ngạch là 3 cores). | Click ngay nút **`RESET SYSTEM (STEADY STATE)`**, đợi 10 giây cho các Pod cũ tắt đi rồi chạy lại attack. |
| HTTP Flood vào backend service không tạo log | Backend service dùng gRPC cổng `3550` chứ không nhận cổng `80` (HTTP). | Chỉ dùng `HTTP_FLOOD` cho dịch vụ `frontend`. Đối với backend, hãy dùng `CPU_STRESS` hoặc `POD_KILL`. |
| Port-forward bị sập | Tiến trình chạy ngầm bị Windows kill. | Chạy lại script một nút bấm: `.\start-demo.ps1` |
