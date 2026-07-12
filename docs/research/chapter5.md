# CHƯƠNG 5: THỰC NGHIỆM, ĐO ĐẾM VÀ ĐÁNH GIÁ KẾT QUẢ

## 5.1. Thiết lập kịch bản thực nghiệm (War Game Scenarios)

Để chứng minh tính hiệu quả và đo lường các chỉ số của cơ chế tự phục hồi, đề tài thiết lập hệ thống thực nghiệm tự động sử dụng chương trình chạy thử nghiệm chuyên biệt `experiment_runner_direct.py`. 

Thử nghiệm được thực hiện trên 4 kịch bản tấn công (Scenarios) độc lập, mỗi kịch bản chạy thử nghiệm **5 lần liên tiếp** cho cả hai chế độ: Tự động phục hồi (AUTO) và Xử lý thủ công (MANUAL - hệ thống chỉ cảnh báo mà không tự vá lỗi) để thu được số liệu trung bình chính xác nhất.

### 5.1.1. Kịch bản E1: Tấn công vắt kiệt tài nguyên (CPU Stress - cartservice)
*   **Mục tiêu chịu hại:** Dịch vụ `cartservice` (chịu trách nhiệm lưu trữ giỏ hàng, viết bằng .NET).
*   **Phương thức tấn công:** Chaos Worker tiêm một Stress Pod chạy `stress-ng` chiếm dụng CPU ở cường độ cao (`intensity: HIGH`) trong thời gian 60 giây.
*   **Hành động tự cứu hộ dự kiến:** Hephaestus nhận diện cảnh báo `HIGH_CPU`/`CRITICAL` $\rightarrow$ thực thi lệnh `RESTART` (xóa pod cartservice lâu nhất để K8s tự động tái tạo).

### 5.1.2. Kịch bản E2: Tấn công tràn ngập tầng ứng dụng (HTTP Flood - frontend)
*   **Mục tiêu chịu hại:** Dịch vụ `frontend` (chịu trách nhiệm hiển thị giao diện web, viết bằng Go).
*   **Phương thức tấn công:** Chaos Worker spawn các luồng đồng thời gửi dồn dập HTTP GET requests trực tiếp đến cổng Ingress của frontend trong thời gian 60 giây, đẩy tỷ lệ lỗi phản hồi (HTTP 5xx) tăng vọt.
*   **Hành động tự cứu hộ dự kiến:** Hephaestus nhận diện cảnh báo lỗi `HIGH_ERROR_RATE`/`CRITICAL` $\rightarrow$ thực thi lệnh `ROLLBACK` (patch annotation lên Deployment để kích hoạt trigger rolling update đưa ứng dụng về trạng thái ổn định).

### 5.1.3. Kịch bản E3: Tấn công phá hủy dịch vụ tức thời (Pod Kill - frontend)
*   **Mục tiêu chịu hại:** Dịch vụ `frontend`.
*   **Phương thức tấn công:** Chaos Worker gọi Kubernetes API trực tiếp xóa đột ngột toàn bộ các Pod đang chạy của frontend.
*   **Hành động tự cứu hộ dự kiến:** Hephaestus nhận diện cảnh báo `POD_CRASH`/`CRITICAL` $\rightarrow$ thực thi lệnh `RESTART` để đảm bảo pod mới nhanh chóng đạt trạng thái `Ready`.

### 5.1.4. Kịch bản E4: Tấn công phức hợp phối hợp (Combined Attack)
*   **Mục tiêu chịu hại:** Đồng thời tác động lên cả `frontend` và `cartservice`.
*   **Phương thức tấn công:** Chaos Worker kích hoạt đồng thời cả 3 hình thức tấn công: HTTP Flood, CPU Stress và Pod Kill để tạo ra trạng thái quá tải dây chuyền.
*   **Hành động tự cứu hộ dự kiến:** Hephaestus áp dụng nguyên tắc *"First alert wins"* — xử lý cảnh báo khẩn cấp đầu tiên nhận được từ hàng đợi Kafka (dự kiến là `HTTP_ERROR_RATE`/`CRITICAL` từ frontend) $\rightarrow$ thực thi hành động tương ứng trong khi các cảnh báo sau sẽ tạm thời rơi vào trạng thái chờ hoặc cooldown để ổn định cụm.

---

## 5.2. Kết quả đo đếm MTTD và MTTR thực tế

Dưới đây là bảng tổng hợp số liệu thực nghiệm đo đạc thực tế từ hệ thống Zero Door sau 40 lượt chạy thử nghiệm:

### Bảng 5.1: Số liệu thực nghiệm thời gian phản ứng (MTTD và MTTR)

| Scenario | Chế độ (Mode) | Số lượt chạy (Runs) | MTTD Trung bình (s) | MTTD P95 (s) | MTTR Trung bình (s) | Uptime (%) | Tỷ lệ cứu hộ thành công (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1** (CPU Stress) | AUTO | 5 | 25.60 | 25.75 | 1.01 | 100.0 | 100.0 |
| | MANUAL | 5 | 25.66 | 26.10 | N/A | 100.0 | N/A |
| **E2** (HTTP Flood) | AUTO | 5 | 1.01 | 1.02 | 1.01 | 100.0 | 100.0 |
| | MANUAL | 5 | 1.02 | 1.03 | N/A | 100.0 | N/A |
| **E3** (Pod Kill) | AUTO | 5 | 3.15 | 9.24 | 1.01 | 100.0 | **20.0** |
| | MANUAL | 5 | 2.02 | 4.69 | N/A | 100.0 | N/A |
| **E4** (Combined) | AUTO | 5 | 5.60 | 6.04 | 1.01 | 100.0 | 100.0 |
| | MANUAL | 5 | 5.61 | 6.17 | N/A | 100.0 | N/A |

### Phân tích kết quả đo lường:
1.  **Thời gian phát hiện lỗi (MTTD):** 
    *   Trong các kịch bản liên quan đến mạng và lỗi logic như **E2** (HTTP Flood) và **E3** (Pod Kill), MTTD đạt giá trị cực thấp (chỉ từ **1.01s - 3.15s**). Lý do là vì Ingress Controller và K8s API ghi nhận lỗi kết nối tức thời, giúp Gaia nhanh chóng bắt được tín hiệu.
    *   Trong kịch bản **E1** (CPU Stress), MTTD trung bình tăng lên **25.60s**. Điều này hoàn toàn phù hợp với cơ chế hoạt động thực tế của Prometheus: scrape interval được thiết lập là 15 giây, dẫn đến độ trễ tự nhiên từ 15-30 giây để Prometheus kéo số liệu mới từ cAdvisor và cập nhật vào TSDB trước khi Gaia có thể truy vấn thấy tải CPU vượt ngưỡng 80%.
2.  **Thời gian khắc phục lỗi (MTTR):**
    *   Trong chế độ tự động (AUTO), MTTR trung bình đo được từ thời điểm Hephaestus nhận alert đến khi hoàn thành gọi API K8s chỉ mất **1.01 giây** (tốc độ xử lý ở cấp độ mili-giây của mã nguồn Python).
    *   Ngược lại, ở chế độ MANUAL, hệ thống chỉ ghi nhận cảnh báo mà không can thiệp, MTTR ở trạng thái vô hạn (N/A) do hệ thống không thể tự phục hồi nếu không có kỹ sư can thiệp trực tiếp.

---

## 5.3. Kết quả Uptime và Đánh giá SLO hệ thống

Đề tài đặt ra chỉ tiêu duy trì Uptime của hệ thống dịch vụ mục tiêu $\ge$ 99.9% dưới áp lực tấn công.
*   **Kết quả đo đạc:** Tỷ lệ Uptime đạt **100%** tuyệt đối trên tất cả 4 kịch bản thực nghiệm.
*   **Giải thích thực tế:** Mặc dù Chaos Worker thực hiện các hành động phá hoại nghiêm trọng, nhưng nhờ cơ chế tự điều phối sẵn có của Kubernetes (như Kubelet tự khởi động lại container bị lỗi, ReplicaSet tự động duy trì số lượng pod) kết hợp với các hành động vá lỗi kịp thời của Hephaestus (Scale Up để chia tải khi bị DDoS, Rollback khi bản cập nhật lỗi), các dịch vụ microservices phía sau luôn duy trì ít nhất 1 pod ở trạng thái hoạt động. Do đó, người dùng cuối khi truy cập vào trang chủ E-commerce vẫn không gặp phải tình trạng mất kết nối hoàn toàn.

---

## 5.4. Đánh giá tính ổn định và Hạn chế thực tế phát hiện được

Thực nghiệm đã chỉ ra một hạn chế kỹ thuật vô cùng quan trọng (điểm yếu cốt lõi của hệ thống) trong kịch bản **E3 (Pod Kill)**:
*   **Hiện tượng:** Tỷ lệ tự cứu hộ thành công của Hephaestus trong E3 chỉ đạt **20%** (1 lượt thành công trên 5 lượt chạy).
*   **Phân tích nguyên nhân gốc (Root Cause):** 
    *   Khi Chaos Worker gọi API xóa pod của frontend, Kubernetes ReplicaSet Controller lập tức nhận diện sự thiếu hụt pod và tự động ra lệnh tạo lại pod mới. 
    *   Đồng thời, Gaia phát hiện sự kiện pod bị xóa và gửi cảnh báo về hàng đợi Kafka. Hephaestus consume cảnh báo này và kích hoạt hành động `RESTART`.
    *   Trong logic của hành động `RESTART`, Hephaestus gọi hàm `list_namespaced_pod` để tìm các pod đang chạy nhằm tiêu diệt. 
    *   Tuy nhiên, do pod cũ đã bị Chaos Worker xóa hoàn toàn, còn pod mới do ReplicaSet tạo đang ở trạng thái `Pending` hoặc `ContainerCreating` (chưa đạt trạng thái `Running`). Hàm `list_namespaced_pod` trả về danh sách rỗng $\rightarrow$ Hephaestus báo lỗi **`FAILED: No running pods found`**.
*   **Kết luận khoa học:** Đây là hiện tượng **Race Condition** (Tranh chấp tài nguyên) tự nhiên giữa bộ điều phối nội tại của Kubernetes và tác tử cứu hộ bên ngoài. Sự tranh chấp này chứng minh rằng trong một số kịch bản lỗi vật lý đơn giản, việc để Kubernetes tự phục hồi (Self-Healing tầng hạ tầng) sẽ tối ưu hơn là cấu hình cho Agent AI can thiệp chồng chéo.

---

## 5.5. Phân tích tối ưu tài nguyên (FinOps Analysis)

Để chứng minh tính hiệu quả của việc chuyển đổi ngôn ngữ lập trình của các Agent sang Python FastAPI và Go Chaos Worker, nhóm đã tiến hành đo đạc lượng tài nguyên tiêu hao thực tế (Memory RSS) trên cụm K3d:

### Bảng 5.2: So sánh tiêu hao RAM của các thành phần hệ thống

| Thành phần | Công nghệ cũ (Dự kiến) | RAM tiêu hao cũ | Công nghệ thực tế (Đã làm) | RAM tiêu hao thực tế | Tỷ lệ tiết kiệm (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Nemesis Agent** | Java Spring Boot | 350 MB | Python FastAPI | **48 MB** | 86.2% |
| **Gaia Agent** | Java Spring Boot | 350 MB | Python FastAPI | **52 MB** | 85.1% |
| **Hephaestus Agent** | Java Spring Boot | 350 MB | Python FastAPI | **45 MB** | 87.1% |
| **Chaos Worker** | Java Spring Boot | 250 MB | Go Binary | **12 MB** | 95.2% |
| **Tổng cộng** | | **1300 MB** | | **157 MB** | **87.9%** |

### Đánh giá khía cạnh FinOps:
Việc chuyển đổi tối ưu hóa ngôn ngữ lập trình giúp hệ thống tiết kiệm được **1143 MB RAM** (giảm gần 88% lượng RAM tiêu thụ cho lớp quản lý). 

Đây là yếu tố quyết định giúp hệ thống Zero Door có khả năng chạy ổn định lâu dài trên Droplet đám mây có cấu hình giới hạn (8GB RAM) mà không bao giờ gặp phải sự cố tràn bộ nhớ (OOMKilled) cho các pod giám sát, đảm bảo tính kinh tế và tính khả thi của đề tài khi ứng dụng vào doanh nghiệp nhỏ.
