# 🎬 KỊCH BẢN DEMO BẢO VỆ ĐỀ TÀI: ZERO DOOR
> **Tài liệu hướng dẫn thuyết trình & thực hành từng bước**  
> *Dành cho EurusDevSec & hp8001 báo cáo trước Hội đồng nghiệm thu*

---

## 🛠️ PHẦN 1: CHUẨN BỊ TRƯỚC DEMO (10 PHÚT TRƯỚC BÁO CÁO)

Đảm bảo cụm local cluster đang chạy bình thường và mở sẵn các cổng kết nối (Port-forward) để tương tác.

### 1. Khởi động Docker Desktop & Kiểm tra cụm K3d
Mở Terminal (PowerShell/CMD) và chạy lệnh:
```bash
# Kiểm tra trạng thái các node
kubectl get nodes
# Dự kiến kết quả: 3 nodes (1 server, 2 agents) trạng thái Ready

# Kiểm tra tất cả các pod đang chạy ổn định
kubectl get pods -A
# Đảm bảo toàn bộ pods ở namespaces: zero-door, target-app, monitoring đều ở trạng thái "Running"
```

### 2. Thiết lập Port-Forward kết nối các dịch vụ
Mở các Terminal riêng biệt để chạy các lệnh port-forward sau (giữ các terminal này chạy ngầm suốt buổi demo):
```bash
# Terminal 1: Kết nối Prometheus (Cổng 9090)
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring

# Terminal 2: Kết nối Grafana Dashboard (Cổng 3000)
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# Terminal 3: Kết nối Web Frontend của ứng dụng mục tiêu (Cổng 8080)
kubectl port-forward svc/frontend 8080:80 -n target-app

# Terminal 4: Kết nối Agent Nemesis - Attacker (Cổng 9092)
kubectl port-forward svc/nemesis 9092:8000 -n zero-door

# Terminal 5: Kết nối Agent Hephaestus - Defender (Cổng 9091)
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door
```

### 3. Chuẩn bị các cửa sổ trình duyệt (Tabs)
Mở sẵn trình duyệt Web với các tab sau:
1.  **Tab 1 - Ứng dụng mục tiêu:** `http://localhost:8080` (Google Online Boutique đang chạy ổn định).
2.  **Tab 2 - Biểu đồ giám sát Grafana:** `http://localhost:3000` (Đăng nhập với tài khoản: **admin** / **zerodoor123** và mở dashboard quản lý tài nguyên và lỗi của `target-app`).
3.  **Tab 3 - Prometheus targets:** `http://localhost:9090/targets` (Chứng minh các microservice đang được giám sát tốt).

---

## 🚀 PHẦN 2: THỰC HÀNH DEMO & LỜI THOẠI THUYẾT TRÌNH (5 - 7 PHÚT)

---

### BƯỚC 1: GIỚI THIỆU TRẠNG THÁI BÌNH THƯỜNG (STEADY STATE) (1 PHÚT)

*   **Hành động trên màn hình:**
    *   Mở trình duyệt, chuyển qua lại giữa Tab 1 (Google Boutique) và click mua thử sản phẩm để chứng minh web đang chạy bình thường.
    *   Chuyển sang Tab 2 (Grafana) chỉ vào các biểu đồ CPU/Memory thấp ($< 10\%$) và Error Rate ($0\%$).
    *   Mở terminal gõ lệnh: `kubectl get pods -n target-app` để hiển thị danh sách các pod.
*   **Lời thoại thuyết trình (Talking Points):**
    > *"Kính thưa Hội đồng, trước tiên em xin trình bày trạng thái hoạt động bình thường (Steady-state) của hệ thống. Ứng dụng mục tiêu ở đây là Google Online Boutique — hệ thống microservice bán hàng mô phỏng thực tế đang chạy trên namespace `target-app`. Mọi giao dịch, giỏ hàng đều hoạt động bình thường.*
    > *Thông qua Grafana Dashboard, ta thấy lượng CPU sử dụng cực kỳ thấp, tỷ lệ lỗi HTTP 5xx là 0%. Prometheus đang định kỳ cào metrics từ các service này mỗi 15 giây để làm cơ sở phát hiện anomaly."*

---

### BƯỚC 2: NEMESIS KÍCH HOẠT TẤN CÔNG (ATTACK PHASE) (1.5 PHÚT)

*   **Hành động trên màn hình:**
    *   Mở một Terminal mới, thực hiện cuộc tấn công **Ép quá tải CPU (CPU Stress)** vào dịch vụ giỏ hàng (`cartservice`) thông qua API của Nemesis bằng lệnh `curl`:
    ```bash
    curl -X POST http://localhost:9092/attack/trigger \
      -H "Content-Type: application/json" \
      -d '{"attackType": "CPU_STRESS", "targetService": "cartservice", "durationSec": 60, "concurrency": 4}'
    ```
    *   *Mẹo:* Bạn cũng có thể mở logs của Chaos Worker bằng lệnh sau để hội đồng thấy lệnh được nhận tức thì:
    ```bash
    kubectl logs -n zero-door -l app=chaos-worker -f
    ```
*   **Lời thoại thuyết trình (Talking Points):**
    > *"Bây giờ, em sẽ đóng vai trò Red Team bằng cách sử dụng **Agent Nemesis** để kích hoạt một cuộc tấn công vắt kiệt tài nguyên CPU (CPU Stress) vào microservice `cartservice` (dịch vụ giỏ hàng).*
    > *Lệnh tấn công được Nemesis lập kế hoạch thông qua AI (Ollama/OpenAI), đóng gói thành cấu trúc JSON chuẩn và gửi vào Kafka topic `attack.commands`.*
    > ***Go Chaos Worker** nhận lệnh này qua Kafka, thực hiện kiểm tra an toàn (Blast Radius Validation) để chắc chắn mục tiêu nằm trong vùng an toàn được phép tấn công (`target-app`), sau đó deploy một ephemeral stress pod để ép CPU của `cartservice` chạy hết công suất. Như thầy cô thấy trên logs, Chaos Worker đã nhận lệnh và bắt đầu ép CPU của cartservice."*

---

### BƯỚC 3: GAIA PHÁT HIỆN BẤT THƯỜNG (DETECTION PHASE) (1 PHÚT)

*   **Hành động trên màn hình:**
    *   Chuyển sang Tab 2 (Grafana), chỉ vào biểu đồ **CPU Utilization** của `cartservice` bắt đầu dựng cột đứng vọt lên mức $100\%$ (vượt qua ngưỡng cảnh báo $80\%$).
    *   Mở Terminal xem logs của Gaia:
    ```bash
    kubectl logs -n zero-door -l app=gaia -f --tail=30
    ```
    *   Hội đồng sẽ nhìn thấy log Gaia in ra dòng chữ phát hiện lỗi: `[WARNING] ALERT PUBLISHED to Kafka: CPU utilization of container 'cartservice' is at 100%...`.
*   **Lời thoại thuyết trình (Talking Points):**
    > *"Khi cuộc tấn công diễn ra, dịch vụ giỏ hàng bị quá tải CPU. Trên Grafana, biểu đồ sử dụng CPU của `cartservice` đã lập tức dựng cột đứng vọt lên mức tối đa 100%.*
    > *Ngay lập tức, **Agent Gaia** đang giám sát ngầm phát hiện ra bất thường này thông qua việc truy vấn định kỳ Prometheus HTTP API. Nó lập tức đóng gói thông tin sự cố thành một cảnh báo JSON gửi vào Kafka topic `monitoring.alerts` để báo cáo cho Agent phòng thủ."*

---

### BƯỚC 4: HEPHAESTUS TỰ ĐỘNG VÁ LỖI (HEALING PHASE) (1.5 PHÚT)

*   **Hành động trên màn hình:**
    *   Mở Terminal xem logs của Hephaestus để thấy phản ứng tự động của nó:
    ```bash
    kubectl logs -n zero-door -l app=hephaestus -f --tail=30
    ```
    *   Hội đồng sẽ nhìn thấy log dạng: `[INFO] Received alert HIGH_CPU on cartservice. Executing SCALE_UP...`
    *   Chạy nhanh lệnh kiểm tra xem hệ thống đã thay đổi thế nào:
    ```bash
    # Kiểm tra số lượng pods cartservice tăng lên (Scale up từ 1 lên 2 pods)
    kubectl get pods -n target-app -l app=cartservice
    ```
    *   Hội đồng sẽ thấy xuất hiện một pod `cartservice` thứ hai đang được dựng lên để chia tải. Sau đó CPU sẽ giảm xuống và hệ thống ổn định trở lại.
*   **Lời thoại thuyết trình (Talking Points):**
    > *"Khi cảnh báo xuất hiện trên Kafka, **Agent Hephaestus** (Defender) lập tức hoạt động. Dựa trên ma trận quyết định (Decision Matrix), đối với lỗi quá tải `HIGH_CPU`, Hephaestus tự động kích hoạt hành động phòng thủ **SCALE_UP**.*
    > *Nó gọi trực tiếp đến Kubernetes API để tăng số lượng bản sao (replicas) của deployment `cartservice` lên. Như thầy cô thấy trên terminal, một pod `cartservice` thứ hai đã được tạo ra tự động để phân chia tải lượng, giúp xử lý các request giỏ hàng nhanh chóng. Sự cố đã được xử lý khép kín hoàn toàn tự động."*

---

### BƯỚC 5: TỔNG KẾT KẾT QUẢ THỰC NGHIỆM (WAR GAME STATS) (1 PHÚT)

*   **Hành động trên màn hình:**
    *   Mở slide hoặc mở trực tiếp thư mục biểu đồ kết quả `docs/experiments/analysis/` để hiển thị:
        *   Biểu đồ so sánh MTTD (Manual vs Auto): `mttd_comparison.png`
        *   Biểu đồ so sánh MTTR (Manual vs Auto): `mttr_comparison.png`
        *   Dữ liệu thống kê: `summary_statistics.csv`
*   **Lời thoại thuyết trình (Talking Points):**
    > *"Để chứng minh tính thuyết phục khoa học, tụi em đã xây dựng script thử nghiệm tự động chạy **40 kịch bản sự cố** khác nhau (CPU stress, HTTP Flood, Pod Kill, Combined) và so sánh giữa việc tự chữa trị với việc kỹ sư gõ lệnh thủ công bằng tay (Manual).*
    > *Kết quả cho thấy tốc độ vượt trội:*
    > *Thời gian phát hiện trung bình (MTTD) giảm từ vài phút xuống còn **dưới 25 giây**.*
    > *Đặc biệt, thời gian khắc phục sự cố tự động (MTTR) chỉ mất đúng **1.01 giây** – nhanh gấp hàng trăm lần so với việc con người phải đăng nhập vào hệ thống, tìm lỗi và khắc phục bằng tay.*
    > *Hệ thống duy trì độ sẵn sàng **Uptime đạt 100%** trong suốt quá trình bị tấn công, hoàn thành vượt mức mục tiêu SLA đề ra.*
    > *Đề tài của nhóm em đã chứng minh sự khả thi của mô hình tác tử thông minh tự vá lỗi, hướng tới mục tiêu giảm thiểu tối đa chi phí vận hành SRE và loại bỏ rủi ro sai sót do yếu tố con người.*
    > *Nhóm em xin chân thành cảm ơn thầy/cô Hội đồng đã lắng nghe, tụi em sẵn sàng nhận câu hỏi phản biện ạ."*
