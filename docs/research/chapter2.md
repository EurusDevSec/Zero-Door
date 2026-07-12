# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ LIÊN QUAN

## 2.1. Kiến trúc Microservices và Container Orchestration

### 2.1.1. Khái niệm và nguyên lý hoạt động của Microservices
Kiến trúc dịch vụ siêu nhỏ (Microservices) phân rã một ứng dụng lớn thành một tập hợp các dịch vụ nhỏ hơn, chạy độc lập và giao tiếp với nhau qua các giao thức mạng nhẹ như HTTP REST hoặc gRPC. Mỗi dịch vụ chịu trách nhiệm xử lý một nghiệp vụ cụ thể (single responsibility) và sở hữu một cơ sở dữ liệu riêng biệt. Mô hình này giúp tăng cường khả năng phát triển song song, nâng cao tính chịu lỗi (fault isolation) và cho phép áp dụng các công nghệ khác nhau trên từng thành phần.

Tuy nhiên, tính phân tán cao của mô hình này cũng tạo ra thách thức lớn về quản trị kết nối, tính nhất quán dữ liệu và độ phức tạp trong việc giám sát trạng thái sức khỏe của các thành phần dịch vụ.

### 2.1.2. Công nghệ Container hóa (Docker)
Để giải quyết bài toán không đồng nhất về môi trường chạy giữa các nhà phát triển và môi trường Production, công nghệ Container hóa (Docker) được áp dụng. Docker đóng gói toàn bộ mã nguồn, thư viện phụ thuộc và tệp cấu hình vào một tệp Container Image duy nhất. 

Nhờ chia sẻ chung nhân hệ điều hành của máy vật lý (Host OS) thông qua cơ chế cô lập tiến trình (namespaces) và giới hạn tài nguyên (cgroups) của Linux, container có dung lượng nhẹ hơn đáng kể so với máy ảo (Virtual Machine), khởi động nhanh trong vài giây và tiêu hao rất ít tài nguyên phần cứng.

### 2.1.3. Nền tảng điều phối Container Kubernetes
Khi số lượng container trong hệ thống microservices tăng lên, việc quản lý vòng đời, phân tải và xử lý sự cố thủ công trở nên bất khả thi. Kubernetes (K8s) được phát triển như một hệ điều hành đám mây, tự động hóa các tác vụ triển khai, mở rộng quy mô và quản lý các containerized applications. Các thành phần K8s cốt lõi áp dụng trong đề tài bao gồm:
*   **Pod:** Đơn vị triển khai nhỏ nhất, chứa một hoặc nhiều container chia sẻ chung không gian mạng (Network namespace) và ổ đĩa (Storage volumes).
*   **Service:** Định nghĩa một nhóm logic các Pods và chính sách truy cập chúng, cung cấp một địa chỉ IP nội bộ ổn định và cơ chế cân bằng tải (load balancing).
*   **Ingress & Ingress Controller (Nginx):** Quản lý luồng traffic đi vào cụm từ bên ngoài ứng dụng, ánh xạ các HTTP/HTTPS routes đến dịch vụ tương ứng bên trong.
*   **NetworkPolicy:** Bộ lọc tường lửa tầng ứng dụng kiểm soát quyền truyền thông giữa các Pods dựa trên nhãn nhãn (labels) và namespaces.
*   **ResourceQuota:** Giới hạn tổng dung lượng tài nguyên tính toán (CPU, Memory, số lượng Pod) mà một namespace được phép tiêu hao, ngăn ngừa cạn kiệt tài nguyên node.

---

## 2.2. Kỹ thuật Hỗn mang (Chaos Engineering)

### 2.2.1. Định nghĩa và 5 Nguyên tắc cốt lõi
Chaos Engineering là kỹ thuật thực nghiệm gây lỗi chủ động lên hệ thống trong môi trường Production hoặc Staging nhằm tìm ra các điểm yếu tiềm ẩn trước khi chúng gây ra sự cố gián đoạn dịch vụ thực sự. Khác với hoạt động phá hoại thông thường, Chaos Engineering được dẫn dắt bởi phương pháp luận khoa học chặt chẽ qua 5 bước:
1.  **Định nghĩa Trạng thái Ổn định (Steady State):** Xác định các chỉ số đo lường hiệu năng bình thường (như tỷ lệ HTTP 200, độ trễ P99, tải CPU).
2.  **Đặt Giả thuyết (Hypothesis):** Giả định hệ thống sẽ tự phục hồi hoặc duy trì trạng thái ổn định khi có lỗi xảy ra (ví dụ: *"Khi pod frontend bị xóa, HPA và Kubernetes Controller sẽ khôi phục lại dịch vụ và người dùng không nhận thấy gián đoạn"*).
3.  **Tiêm lỗi (Inject Failure):** Chủ động đưa vào các biến số lỗi (ngắt kết nối mạng, cạn kiệt CPU, xóa pod).
4.  **Kiểm chứng Giả thuyết:** So sánh trạng thái hệ thống sau khi tiêm lỗi với trạng thái ổn định ban đầu.
5.  **Thu hẹp Vùng ảnh hưởng (Minimize Blast Radius):** Thiết lập các chốt chặn an toàn để đảm bảo lỗi được kiểm soát và dễ dàng khôi phục ngay lập tức nếu thực nghiệm đi chệch hướng dự kiến.

### 2.2.2. Các dạng lỗi thường gặp ở tầng ứng dụng
Thay vì chỉ tập trung vào các lỗi hạ tầng vật lý (tắt server, mất điện nguồn), nghiên cứu này hướng đến việc giả lập các lỗi tầng ứng dụng và dịch vụ mạng:
*   **HTTP Flood (Application Layer DDoS):** Gửi lượng lớn request dồn dập đến các API endpoints nhạy cảm để kiểm tra khả năng chịu tải và cơ chế tự động co giãn.
*   **Resource Exhaustion (Cạn kiệt tài nguyên):** Sử dụng các công cụ stresser để chiếm dụng CPU/RAM của pod, kiểm tra cơ chế cảnh báo ngưỡng và tự cô lập phần tử lỗi.
*   **Pod Kill (Lỗi gián đoạn tức thời):** Xóa đột ngột pod đang phục vụ lưu lượng nhằm đánh giá độ trễ khởi động lại và khả năng duy trì session của hệ thống phân tán.

---

## 2.3. Kiến trúc Đa Tác tử (Multi-Agent Systems)

### 2.3.1. Định nghĩa Tác tử tự trị (Autonomous Agent)
Một tác tử tự trị (Agent) là một thực thể phần mềm có khả năng nhận thức môi trường (Perception), tự đưa ra quyết định dựa trên các quy luật lập trình hoặc mô hình trí tuệ nhân tạo (Decision Making), và thực thi hành động (Action) tác động ngược trở lại môi trường đó nhằm hoàn thành mục tiêu thiết kế.

### 2.3.2. Sự phối hợp hướng sự kiện trong Multi-Agent AI
Hệ thống Đa tác tử (Multi-Agent System) bao gồm nhiều tác tử chuyên biệt hóa, phối hợp hoạt động với nhau. Trong các hệ thống microservices phức tạp, việc kết nối trực tiếp (point-to-point) giữa các tác tử dễ gây ra lỗi nghẽn cổ chai và mất tính đồng bộ. 

Do đó, đề tài áp dụng mô hình kiến trúc hướng sự kiện (Event-Driven Architecture). Các Agent giao tiếp phi đồng bộ thông qua một Message Broker trung tâm. Mỗi Agent lắng nghe một số luồng thông tin cụ thể, tự xử lý độc lập và đẩy kết quả lên một luồng dữ liệu dùng chung khác, giúp hệ thống có khả năng mở rộng tối đa và không bị ảnh hưởng chéo khi một Agent gặp sự cố.

---

## 2.4. Công nghệ Truyền tin và Giám sát (Observability)

### 2.4.1. Apache Kafka dưới mô hình KRaft
Apache Kafka là nền tảng stream dữ liệu phân tán hiệu năng cao, hoạt động theo mô hình Publish-Subscribe. Từ phiên bản 3.4, Kafka chuyển đổi sang cơ chế KRaft (Kafka Raft Metadata Mode), tích hợp trực tiếp Controller vào Broker và loại bỏ hoàn toàn sự phụ thuộc vào Apache ZooKeeper. 

Sự thay đổi này mang lại lợi ích thực tiễn rất lớn cho các dự án nghiên cứu quy mô nhỏ và local development:
*   **Tối ưu bộ nhớ:** Giảm số lượng Pod cần khởi chạy từ 2 (1 Broker + 1 ZooKeeper) xuống còn 1 Pod duy nhất chạy chế độ kết hợp, tiết kiệm hơn 700MB RAM.
*   **Độ tin cậy cao hơn:** Giảm độ phức tạp cấu hình mạng nội bộ và tăng tốc độ phục hồi cụm khi xảy ra sự cố mất điện hoặc reset máy chủ vật lý.

### 2.4.2. Prometheus và Grafana (Metrics Stack)
*   **Prometheus:** Cơ sở dữ liệu chuỗi thời gian (TSDB) hoạt động theo cơ chế kéo (Pull-based). Prometheus định kỳ kéo dữ liệu metrics từ cổng `/metrics` của các Pod theo cấu hình chỉ định trong `ServiceMonitor`. Các metric chính thu thập bao gồm tài nguyên container (`container_cpu_usage_seconds_total`) và trạng thái Pod.
*   **Grafana:** Công cụ trực quan hóa dữ liệu kết nối trực tiếp với Prometheus bằng ngôn ngữ truy vấn PromQL, chuyển đổi dữ liệu thô thành các biểu đồ thời gian thực trực quan giúp người vận hành giám sát tức thời.

### 2.4.3. Elasticsearch và Fluent Bit (Logging Stack)
*   **Fluent Bit:** Bộ thu thập và xử lý log siêu nhẹ (chạy dưới dạng DaemonSet trên mỗi Node của Kubernetes, tiêu tốn chỉ khoảng 15MB RAM). Fluent Bit đọc trực tiếp tệp tin logs từ đường dẫn hệ thống `/var/log/containers/*`, gán thêm metadata của K8s (Pod name, Namespace, Labels) và đẩy về Elasticsearch.
*   **Elasticsearch:** Cơ sở dữ liệu tài liệu (Document Store) hỗ trợ tìm kiếm toàn văn (full-text search) qua REST API, lưu trữ tập trung logs từ tất cả các microservices để Gaia quét tìm mã lỗi.

---

## 2.5. Quy trình DevSecOps và Tự động hóa hạ tầng (IaC)

### 2.5.1. Hạ tầng dạng mã (Infrastructure as Code - Terraform)
Terraform là công cụ IaC nguồn mở sử dụng ngôn ngữ khai báo HCL (HashiCorp Configuration Language) để tự động hóa quy trình cấp phát tài nguyên hạ tầng điện toán đám mây. Thay vì click chuột thủ công trên web console, kỹ sư viết cấu hình hạ tầng vào các tệp tin `.tf`. 

Terraform quản lý trạng thái tài nguyên qua tệp tin `terraform.tfstate`, hỗ trợ việc tạo lập mới, cập nhật và hủy toàn bộ hạ tầng (Droplet, Cloud Firewall, SSH keys) chỉ bằng các câu lệnh tự động, đảm bảo tính nhất quán và loại bỏ cấu hình sai sót.

### 2.5.2. Công cụ quét tĩnh bảo mật (SAST) và Trivy Scan
Nhằm bảo vệ hệ thống trước khi mã nguồn được đóng gói thành container image và đưa lên hạ tầng chạy, quy trình DevSecOps tích hợp các công cụ quét tự động trong GitHub Actions:
*   **Bandit:** Phân tích cú pháp trừu tượng (AST) của mã nguồn Python để phát hiện các lỗi an ninh như hardcoded passwords, shell injection, hoặc thuật toán mã hóa yếu.
*   **Gosec:** Quét mã nguồn Go của Chaos Worker để phát hiện lỗi kiểm soát con trỏ không an toàn hoặc lỗi tràn bộ đệm.
*   **Trivy:** Quét cấu hình Kubernetes Manifests (IaC) để phát hiện các lỗi cấu hình nghiêm trọng (như chạy container dưới quyền root, thiếu cấu hình giới hạn tài nguyên) để ngăn ngừa các cuộc tấn công leo thang đặc quyền.
