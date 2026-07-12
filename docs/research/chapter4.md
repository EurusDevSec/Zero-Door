# CHƯƠNG 4: HIỆN THỰC HÓA VÀ TRIỂN KHAI HỆ THỐNG

## 4.1. Hiện thực hóa các Tác tử AI và Worker (Python & Go)

### 4.1.1. Tác tử AI Gaia, Nemesis, Hephaestus (Python FastAPI)
Các tác tử giám sát, lên kịch bản tấn công và tự vá lỗi được hiện thực hóa bằng ngôn ngữ Python 3.11, sử dụng framework FastAPI để cung cấp các REST API phục vụ cho việc kiểm thử và theo dõi trạng thái. Các thư viện cốt lõi bao gồm:
*   `kafka-python-ng`: Kết nối phi đồng bộ, thực hiện việc consume các sự cố và publish các bản tin hành động.
*   `kubernetes`: Thư viện client chính thức của Kubernetes để tương tác trực tiếp với API Server của cụm.
*   `openai`: Gọi các mô hình ngôn ngữ lớn tương thích với chuẩn API của OpenAI (như Gemini 3.1 Flash Lite qua proxy hoặc OpenAI GPT-4o-mini).

Đặc biệt, tác tử Nemesis thực hiện xoay vòng khóa API (Round-Robin) bằng cách lưu trữ danh sách khóa trong biến môi trường `GEMINI_API_KEYS`, phân tách bằng dấu phẩy. Mỗi yêu cầu lập kế hoạch tấn công mới sẽ sử dụng khóa có số thứ tự tăng dần theo chu kỳ:
```python
def get_next_gemini_key() -> str:
    global gemini_key_index
    with gemini_keys_lock:
        key = GEMINI_API_KEYS[gemini_key_index]
        gemini_key_index = (gemini_key_index + 1) % len(GEMINI_API_KEYS)
        return key
```

### 4.1.2. Chaos Worker (Go Binary)
Chaos Worker được viết bằng ngôn ngữ Go (phiên bản 1.21), sử dụng thư viện `confluent-kafka-go` (dựa trên thư viện C mã nguồn mở `librdkafka` để đạt hiệu năng truyền nhận tối đa). 

Worker được biên dịch thành một file nhị phân duy nhất (single binary), chạy vòng lặp nhận tin nhắn từ topic `attack.commands`. Khi có lệnh tấn công, worker khởi tạo một `context.WithTimeout` tương ứng với thời gian quy định của đợt tấn công để tự động hủy bỏ tiến trình (Circuit Breaker) nếu hết thời gian mà chưa hoàn thành.

---

## 4.2. Bảo mật Container và Quy trình CI/CD Pipeline

### 4.2.1. Đóng gói bảo mật bằng Multi-stage và Distroless
Để triệt tiêu các nguy cơ an ninh liên quan đến lỗ hổng CVE trong các container image của các tác tử, hệ thống áp dụng kỹ thuật đóng gói đa phân đoạn (**Multi-stage Build**) kết hợp với image gốc siêu nhỏ **Google Distroless** (`gcr.io/distroless/python3-debian12:nonroot`).
*   **Phân đoạn 1 (Builder stage):** Sử dụng image `python:3.11-slim` đầy đủ để tải và biên dịch các thư viện dependency vào thư mục `/install`. Phân đoạn này chứa các công cụ dịch và compiler cần thiết nhưng sẽ bị loại bỏ hoàn toàn ở sản phẩm cuối.
*   **Phân đoạn 2 (Runtime stage):** Sử dụng distroless image chỉ chứa bộ dịch Python tối thiểu, không chứa shell (`/bin/sh`, `/bin/bash`), không chứa package manager (`apt`, `pip`), không chứa các coreutils cơ bản. Chỉ sao chép thư mục `/install` sạch và mã nguồn ứng dụng từ Phân đoạn 1. Container chạy dưới quyền người dùng không có đặc quyền root (`nonroot`). Điều này làm giảm kích thước image từ ~400MB xuống chỉ còn **~78MB**, ngăn chặn kẻ tấn công thực thi các lệnh shell hoặc leo thang đặc quyền kể cả khi mã nguồn ứng dụng bị xâm nhập.

### 4.2.2. Quy trình kiểm tra tĩnh tự động (CI/CD Pipeline)
Tệp cấu hình workflow GitHub Actions `.github/workflows/ci.yml` tự động kích hoạt khi có sự kiện đẩy mã nguồn lên nhánh `main`. Quy trình bao gồm 5 jobs kiểm tra độc lập:
1.  **Helm Chart & Manifests Lint:** Quét cú pháp tất cả tệp cấu hình YAML sử dụng parser Python để đảm bảo không tồn tại lỗi định dạng trước khi apply.
2.  **Python Build & Bandit Scan:** Chạy công cụ **Bandit** quét mã nguồn của Gaia, Nemesis, Hephaestus để tìm lỗi an ninh và hardcoded secrets.
3.  **Go Build & Gosec Scan:** Thực hiện biên dịch mã nguồn Go và chạy công cụ **Gosec** quét các lỗi bộ nhớ không an toàn.
4.  **Trivy IaC Scan:** Chạy công cụ **Trivy** quét toàn bộ thư mục `infrastructure/manifests` phát hiện các vi phạm cấu hình K8s. Pipeline sẽ tự động bị block (exit code 1) nếu phát hiện lỗi mức độ `CRITICAL`.
5.  **Publish Images:** Sau khi tất cả các bước trên thành công, pipeline tiến hành đóng gói Docker image và đẩy lên GitHub Container Registry (GHCR).

---

## 4.3. Quản trị hạ tầng Cloud tự động với Terraform (IaC)

Triển khai thực tế trên đám mây DigitalOcean (DO) được tự động hóa hoàn toàn bằng Terraform để loại bỏ sai sót vận hành thủ công:

### 4.3.1. Cấu hình Terraform (`main.tf`)
Terraform khởi tạo các tài nguyên trên DigitalOcean vùng Singapore (`sgp1`):
*   `digitalocean_ssh_key.zero_door`: Đăng ký khóa SSH công khai dùng để truy cập an toàn vào máy chủ.
*   `digitalocean_droplet.zero_door`: Khởi tạo máy ảo Droplet chạy hệ điều hành Ubuntu 22.04 LTS, cấu hình tài nguyên phù hợp cho microservices chạy trong cụm K3s (4 vCPUs, 8GB RAM, 160GB SSD).
*   `digitalocean_firewall.zero_door`: Thiết lập tường lửa đám mây bảo vệ máy ảo, chỉ mở cổng **22** (SSH), **80** (HTTP), và **443** (HTTPS) cho toàn thế giới. Cổng **6443** (Kubernetes API) được đóng hoàn toàn để bảo vệ API Server trước các cuộc tấn công từ bên ngoài.

### 4.3.2. Cấu hình tự động hóa qua `cloud-init` và `deploy.sh`
*   **`cloud-init.yaml`:** Chuyển tệp tin cấu hình và script cài đặt hệ thống vào máy ảo, thiết lập ghi nhật ký tự động vào tệp `/var/log/zero-door-deploy.log`.
*   **`deploy.sh`:** Chạy tự động ngay khi máy ảo khởi tạo thành công để thực hiện các nhiệm vụ:
    1.  Cài đặt K3s engine, tự động disable cấu hình Ingress Traefik mặc định để thay bằng Nginx Ingress.
    2.  Tải và cài đặt Helm CLI, kubectl.
    3.  Tạo 3 namespaces và cấu hình các `ResourceQuota` tương ứng.
    4.  Cài đặt Nginx Ingress Controller thông qua Helm.
    5.  Cài đặt Apache Kafka ( KRaft mode ) và các dịch vụ Observability stack.
    6.  Tự động chạy script Python `patch_manifests.py` để vá tên image từ môi trường phát triển local sang tên image trên GHCR và áp dụng `imagePullSecrets` để kéo image từ kho lưu trữ riêng tư, sau đó apply toàn bộ manifests lên K3s.

---

## 4.4. Cấu hình Nginx Ingress và Định tuyến Gateway

Để đảm bảo hệ thống có thể truy cập được từ trình duyệt bên ngoài thông qua một IP duy nhất của Droplet điện toán đám mây, Nginx Ingress được cấu hình định tuyến thông minh:
*   Đường dẫn gốc `/` được định tuyến trực tiếp vào service `frontend` của Google Online Boutique trong namespace `target-app`.
*   Đường dẫn `/nemesis/` được định tuyến vào tác tử Nemesis trong namespace `zero-door` để truy cập dashboard điều khiển. Cấu hình rewrite path được áp dụng để loại bỏ tiền tố `/nemesis` trước khi truyền request vào container của tác tử:
    ```yaml
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    ```
*   Tương tự, đường dẫn `/hephaestus/` được định tuyến vào tác tử Hephaestus để phục vụ cho các REST API kiểm thử.

---

## 4.5. Thiết kế và hiển thị Dashboard điều khiển

Giao diện quản trị tập trung (Zero-Door Control Dashboard) được hiện thực hóa bằng HTML5 và Vanilla CSS/JavaScript, được tích hợp trực tiếp trong thư mục `/static` của tác tử Nemesis và được phục vụ bởi uvicorn server.
*   **In-memory Logging Buffer:** Để hiển thị log hoạt động thời gian thực của các Agent lên giao diện web mà không cần cài đặt các hệ thống log stream phức tạp (như WebSockets hay Loki) gây quá tải RAM, Nemesis thiết lập một mảng buffer ghi log trong bộ nhớ (`NEMESIS_LOG_BUFFER`), tự động lưu trữ và xoay vòng 50 dòng log mới nhất. Giao diện frontend định kỳ gửi request GET `/api/logs` sau mỗi 3 giây để lấy dữ liệu log về hiển thị.
*   **AI Reasoning Chat Pane:** Hiển thị toàn bộ chuỗi hội thoại suy luận của AI (Nemesis phân tích tài nguyên và giải trình lý do đưa ra quyết định tấn công), giúp người vận hành theo dõi được tính minh bạch và logic của mô hình ra quyết định.
