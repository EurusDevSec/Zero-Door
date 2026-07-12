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

Dưới đây là mã nguồn Dockerfile chuẩn được áp dụng cho các tác tử Python (ví dụ: Gaia Agent):

```dockerfile
# Stage 1: Build stage (Lò nướng)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Cài đặt dependencies vào thư mục cô lập /install để tránh mang theo compiler
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime stage (Tủ kính trưng bày)
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
# Chỉ copy thư viện đã build sạch và mã nguồn
COPY --from=builder /install /usr/local
COPY main.py .

# Thiết lập PYTHONPATH để python interpreter trong distroless nhận diện package
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
# Chạy trực tiếp qua python uvicorn, tuyệt đối không đi qua shell wrapper
ENTRYPOINT ["/usr/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Giải thích chi tiết cấu trúc Dockerfile:**
1.  `FROM python:3.11-slim AS builder`: Khởi tạo môi trường build đầy đủ các công cụ biên dịch (pip, gcc) để tải các gói phụ thuộc từ `requirements.txt`.
2.  `--prefix=/install`: Toàn bộ các module tải về được gom gọn vào thư mục `/install` độc lập, tránh pha tạp với các file hệ thống của builder stage.
3.  `FROM gcr.io/distroless/python3-debian12:nonroot`: Chuyển sang sử dụng base image bảo mật cực hạn từ Google. Image này không có bash, sh, apt, chown hay bất kỳ binary nào khác ngoài môi trường chạy Python tối thiểu.
4.  `COPY --from=builder /install /usr/local`: Chỉ copy thư viện Python đã biên dịch sạch ở Stage 1 sang Stage 2.
5.  `ENV PYTHONPATH`: Chỉ đường dẫn cho Python tìm nạp thư viện tại `/usr/local/lib/python3.11/site-packages` do môi trường Distroless không tự động map các biến PATH như các bản phân phối Linux thông thường.
6.  `ENTRYPOINT`: Gọi trực tiếp `/usr/bin/python3 -m uvicorn` thay vì dùng file shell script `start.sh` làm trung gian, triệt tiêu hoàn toàn bề mặt tấn công shell injection.

Giải pháp này giúp giảm kích thước image từ ~400MB xuống chỉ còn **~78MB**, ngăn chặn kẻ tấn công thực thi các lệnh shell hoặc leo thang đặc quyền kể cả khi mã nguồn ứng dụng bị xâm nhập.

### 4.2.2. Quy trình kiểm tra tĩnh tự động (CI/CD Pipeline)
Tệp cấu hình workflow GitHub Actions `.github/workflows/ci.yml` tự động kích hoạt khi có sự kiện đẩy mã nguồn lên nhánh `main`. Quy trình bao gồm các cấu hình kiểm tra an ninh tự động quan trọng:

```yaml
# Trích xuất cấu hình quét bảo mật trong GitHub Actions
jobs:
  python-build:
    name: Build Python Agent
    runs-on: ubuntu-latest
    strategy:
      matrix:
        agent: [gaia, nemesis, hephaestus]
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd agent-orchestrator/${{ matrix.agent }}
          pip install --no-cache-dir -r requirements.txt
      - name: Run Bandit SAST Scan
        run: |
          pip install --no-cache-dir bandit
          cd agent-orchestrator/${{ matrix.agent }}
          bandit -r main.py -lll -iii

  go-build:
    name: Build Go Chaos Worker
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Set up Go 1.21
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'
      - name: Run Gosec SAST Scan
        run: |
          go install github.com/securego/gosec/v2/cmd/gosec@latest
          cd chaos-worker
          gosec -severity medium -confidence medium ./...

  iac-scan:
    name: Kubernetes Manifests Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Run Trivy Vulnerability Scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: 'infrastructure/manifests'
          exit-code: '1'
          severity: 'CRITICAL'
```

**Chi tiết các chốt chặn an ninh:**
*   **Bandit SAST (`bandit -r main.py -lll -iii`):** Chỉ hiển thị các cảnh báo mức độ nguy hiểm từ Trung bình trở lên với độ tin cậy cao, phát hiện sớm các lỗ hổng hardcode thông tin kết nối hoặc hàm thực thi hệ thống nguy hiểm.
*   **Gosec SAST (`gosec -severity medium -confidence medium`):** Kiểm tra mã nguồn Go của Chaos Worker để phát hiện các lỗi tràn bộ nhớ hoặc xử lý bất đồng bộ không an toàn.
*   **Trivy Config Scan (`scan-type: 'config'`):** Rà quét các tệp tin YAML trong thư mục manifests. Cấu hình `exit-code: '1'` và `severity: 'CRITICAL'` đảm bảo rằng nếu phát hiện bất kỳ cấu hình sai trái nguy hiểm nào (ví dụ: container chạy quyền root, pod mount ổ đĩa host), pipeline sẽ lập tức báo đỏ (Block Build) để kỹ sư sửa chữa trước khi cho phép deploy.

---

## 4.3. Quản trị hạ tầng Cloud tự động với Terraform (IaC)

Triển khai thực tế trên đám mây DigitalOcean (DO) được tự động hóa hoàn toàn bằng Terraform để loại bỏ sai sót vận hành thủ công.

### 4.3.1. Cấu hình Terraform (`main.tf`)
Dưới đây là mã nguồn cấu hình Terraform khởi tạo máy ảo và thiết lập tường lửa bảo vệ:

```hcl
# main.tf — DigitalOcean Provisioning
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_ssh_key" "zero_door" {
  name       = "zero-door-key"
  public_key = file(var.public_key_path)
}

resource "digitalocean_droplet" "zero_door" {
  name               = "zero-door-k3s"
  region             = "sgp1"
  size               = "s-4vcpu-8gb"
  image              = "ubuntu-22-04-x64"
  private_networking = true
  ssh_keys           = [digitalocean_ssh_key.zero_door.id]
  user_data          = file("cloud-init.yaml")
}

resource "digitalocean_firewall" "zero_door" {
  name        = "zero-door-firewall"
  droplet_ids = [digitalocean_droplet.zero_door.id]

  # SSH Access
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Ingress Web Traffic HTTP
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Ingress Web Traffic HTTPS
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow all outbound traffic
  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
```

**Giải thích an ninh trong cấu hình Firewall:**
Quy trình Hardening đóng hoàn toàn cổng **6443** (Kubernetes API Server) đối với thế giới bên ngoài. Đây là thay đổi bảo mật tối quan trọng so với các hướng dẫn cài đặt Kubernetes cơ bản. 

Bằng cách đóng cổng này, kẻ tấn công không thể dò quét hoặc bruteforce API Server của cụm. Kỹ sư SRE chỉ có thể quản trị cụm từ xa bằng cách tạo đường truyền SSH Tunnel mã hóa thông qua cổng 22 để truy cập an toàn vào API nội bộ.

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

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: zero-door-ingress
  namespace: zero-door
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
    - http:
        paths:
          # Định tuyến vào Frontend của Google Online Boutique
          - path: /(|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
          # Định tuyến vào Dashboard quản trị Nemesis
          - path: /nemesis(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: nemesis
                port:
                  number: 8000
          # Định tuyến vào REST API của Hephaestus
          - path: /hephaestus(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: hephaestus
                port:
                  number: 8000
```

**Giải thích cơ chế hoạt động:**
*   `nginx.ingress.kubernetes.io/rewrite-target: /$2`: Sử dụng regex để bóc tách đường dẫn con. Khi người dùng truy cập `http://<IP_DROPLET>/nemesis/api/logs`, Ingress Controller sẽ rewrite lại đường dẫn và truyền đến container của Nemesis dưới dạng `/api/logs`, giúp Nemesis xử lý các API tĩnh bình thường mà không cần tự map cấu hình tiền tố phức tạp.
*   Cổng mặc định của `frontend` được ánh xạ về đường dẫn gốc `/`, tạo sự liền mạch cho người dùng trải nghiệm cửa hàng mua sắm giả lập.

---

## 4.5. Thiết kế và hiển thị Dashboard điều khiển

Giao diện quản trị tập trung (Zero-Door Control Dashboard) được hiện thực hóa bằng HTML5 và Vanilla CSS/JavaScript, được tích hợp trực tiếp trong thư mục `/static` của tác tử Nemesis và được phục vụ bởi uvicorn server.
*   **In-memory Logging Buffer:** Để hiển thị log hoạt động thời gian thực của các Agent lên giao diện web mà không cần cài đặt các hệ thống log stream phức tạp (như WebSockets hay Loki) gây quá tải RAM, Nemesis thiết lập một mảng buffer ghi log trong bộ nhớ (`NEMESIS_LOG_BUFFER`), tự động lưu trữ và xoay vòng 50 dòng log mới nhất. Giao diện frontend định kỳ gửi request GET `/api/logs` sau mỗi 3 giây để lấy dữ liệu log về hiển thị.
*   **AI Reasoning Chat Pane:** Hiển thị toàn bộ chuỗi hội thoại suy luận của AI (Nemesis phân tích tài nguyên và giải trình lý do đưa ra quyết định tấn công), giúp người vận hành theo dõi được tính minh bạch và logic của mô hình ra quyết định.
*   **Nút Reset môi trường:** Kết nối trực tiếp đến endpoint POST `/api/reset` của Nemesis, tự động phát lệnh xóa lịch sử chat, làm sạch log buffer, và gửi REST call đến Hephaestus `/experiment/reset` để dọn dẹp các NetworkPolicy đang block và scale toàn bộ Deployments về 1 replica duy nhất phục vụ đợt War Game tiếp theo.
