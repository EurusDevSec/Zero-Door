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

---

## 4.6. Quy trình vận hành và Giao diện minh chứng thực tế

Để chứng minh tính thực tiễn và khả năng vận hành khép kín của hệ thống, phần này mô tả chi tiết quy trình chạy thử nghiệm, các chốt chặn tự động hóa và giao diện tương tác thực tế của các thành phần trong dự án.

### 4.6.1. Quy trình Tích hợp và Đóng gói thực tế (CI/CD & GHCR)
Mỗi thay đổi mã nguồn trên kho lưu trữ GitHub được tự động hóa kiểm thử tĩnh và đóng gói qua pipeline GitHub Actions:
*   **Kết quả chạy CI Pipeline:** Khi nhà phát triển thực hiện lệnh push, hệ thống kích hoạt workflow tích hợp liên tục. Pipeline thực hiện quét tĩnh mã nguồn Python (bằng Bandit) và Go (bằng Gosec) để phát hiện lỗ hổng sớm, đồng thời quét lỗi bảo mật cấu hình K8s Manifests (bằng Trivy). Khi tất cả các kiểm thử vượt qua thành công, GitHub Actions sẽ hiển thị trạng thái hoàn thành màu xanh lá cây (`Success`).
    
    *(Hình 4.2: Minh chứng kết quả chạy thành công và vượt qua các chốt chặn kiểm tra an toàn trên GitHub Actions)*

*   **Lưu trữ Container Image trên GHCR:** Sau khi build thành công, các Docker image tối ưu (sử dụng base image Distroless bảo mật) được tự động đẩy (push) trực tiếp lên kho chứa private **GitHub Container Registry (GHCR)** dưới dạng các gói Package tương ứng với từng Agent: `gaia-agent`, `nemesis-agent`, `hephaestus-agent`, và `chaos-worker`.
    
    *(Hình 4.3: Danh sách các gói Container Image được lưu trữ và lập phiên bản trên GitHub Container Registry - GHCR)*

### 4.6.2. Trạng thái Container chạy thực tế trên Kubernetes
Sau khi được tự động deploy hoặc chạy lệnh triển khai bằng Terraform/Cloud-init, toàn bộ các thành phần của hệ thống được lập lịch và chạy ổn định trên cụm Kubernetes cục bộ (K3d) hoặc cloud. Trạng thái các container hoạt động bình thường (Healthy) trong 3 namespaces cốt lõi được biểu diễn dưới dạng:

*   **Namespace `zero-door` (Các Agent điều phối):** Các pod `gaia`, `nemesis`, `hephaestus`, `chaos-worker`, và cụm `kafka-controller-0` đều ở trạng thái `Running` và sẵn sàng nhận kết nối.
*   **Namespace `target-app` (Ứng dụng mục tiêu):** Các microservices của Online Boutique (như `frontend`, `cartservice`, `checkoutservice`, `redis-cart`, v.v.) hoạt động bình thường ở trạng thái ổn định (steady-state) với 1 bản sao (replica).
*   **Namespace `monitoring` (Hệ thống quan sát):** Pod `prometheus`, `grafana`, `elasticsearch`, và `fluent-bit` hoạt động ổn định nhờ cấu hình mở rộng ResourceQuota.

*(Hình 4.4: Danh sách các Pods chạy thực tế trong cụm Kubernetes hiển thị trạng thái Running)*

### 4.6.3. Giao diện các thành phần vận hành thực tế
Quy trình thử nghiệm hệ thống yêu cầu sự phối hợp nhịp nhàng giữa 4 giao diện điều khiển chính:

1.  **Giao diện Ứng dụng mục tiêu Online Boutique (`http://localhost:8080`):** 
    Đây là ứng dụng thương mại điện tử microservices giả lập của Google. Người dùng và các công cụ stress test truy cập trực tiếp qua cổng 8080 thông qua Ingress Gateway. Khi cuộc tấn công HTTP Flood hoặc Pod Kill xảy ra, trang web này sẽ ghi nhận độ trễ tăng cao hoặc lỗi tạm thời (502/503), làm căn cứ đo lường thời gian gián đoạn dịch vụ thực tế.
    
    *(Hình 4.5: Giao diện trang chủ cửa hàng giả lập Google Online Boutique phục vụ kiểm thử)*

2.  **Giao diện Dashboard Điều khiển Zero-Door (`http://localhost:9092/dashboard/`):**
    Giao diện AWS Cloudscape Light Theme tối giản giúp người vận hành thực hiện wargame:
    *   **Bản đồ Topology:** Thể hiện luồng kết nối giữa các microservices của Online Boutique.
    *   **Đồ thị CPU Telemetry (Chart.js):** Vẽ biểu đồ tải CPU theo thời gian thực (rolling 60s), tự động đổi màu đỏ khi có tải cao bất thường (stress-test) và chuyển tím/xanh sau khi Hephaestus kích hoạt tự phục hồi.
    *   **SRE SLOs Monitor Card:** Hiển thị trực tiếp các chỉ số đo đạc hiệu năng tự phục hồi trung bình gồm MTTD, MTTR, tỷ lệ tự vá thành công (Heal Success Rate), và tỷ lệ Uptime.
    *   **Khung tương tác Red/Blue Team:** Cho phép chọn microservice mục tiêu và kích hoạt tấn công thủ công hoặc tự động qua mô hình AI suy luận.
    
    *(Hình 4.6: Giao diện Zero-Door Control Dashboard hiển thị các biểu đồ Telemetry và SRE SLOs)*

3.  **Giao diện Prometheus (`http://localhost:9090`):**
    Hệ thống lưu trữ cơ sở dữ liệu chuỗi thời gian (TSDB). Người vận hành sử dụng trang này để kiểm tra trực quan các Alert Rules đang hoạt động và truy vấn trực tiếp các biểu đồ tài nguyên thô bằng ngôn ngữ PromQL (ví dụ: truy vấn CPU limits, rate request).
    
    *(Hình 4.7: Giao diện Prometheus Alerting hiển thị các luật giám sát trạng thái tài nguyên hệ thống)*

4.  **Giao diện Grafana (`http://localhost:3000`):**
    Trực quan hóa các bảng điều khiển (Dashboards) quản trị tài nguyên nâng cao của Kubernetes Cluster và theo dõi chi tiết hoạt động của các pod.
    
    *(Hình 4.8: Bảng điều khiển Grafana hiển thị thông số chi tiết của cụm Kubernetes)*

### 4.6.4. Các bước khởi động và phối hợp kiểm thử (How to Run & Test)
Để chạy thử nghiệm khép kín trên môi trường cục bộ, người vận hành thực hiện quy trình sau:
1.  **Khởi động các cổng kết nối ngầm (Port-Forward):** Thực thi script `start-demo.ps1` để tự động dọn dẹp các tiến trình cũ và mở luồng kết nối cho Dashboard (9092), Hephaestus (9091), Prometheus (9090) và Grafana (3000).
2.  **Kích hoạt War Game:** Trên Dashboard Zero-Door, người vận hành nhấn **Reset System** để đưa cụm về Steady-State (1 pod, xóa mọi IP block). Sau đó, chọn một dịch vụ (ví dụ: `cartservice`) và loại tấn công (ví dụ: `CPU_STRESS` mức `HIGH`), rồi bấm **Execute Attack**.
3.  **Vòng lặp Closed-Loop tự động:**
    *   **Tấn công:** Chaos Worker nhận lệnh qua Kafka và tạo stress pod gây quá tải CPU của `cartservice`.
    *   **Phát hiện:** Biểu đồ Telemetry trên Dashboard đổi màu đỏ cảnh báo. Prometheus phát hiện CPU vượt ngưỡng, Gaia cào metric và gửi alert sự cố lên Kafka.
    *   **Tự động vá lỗi:** Hephaestus nhận alert từ Kafka, tra cứu Decision Matrix đưa ra quyết định phục hồi `SCALE_UP` (hoặc `RESTART` nếu quá nặng). Hephaestus gọi Kubernetes API nhân đôi số replica của `cartservice` lên 2 để chia tải.
    *   **Ổn định:** Sau khi scale up thành công, tải CPU giảm xuống, biểu đồ Telemetry trên Dashboard chuyển xanh trở lại, hoàn thành chu kỳ tự phục hồi khép kín. Các chỉ số MTTD và MTTR của đợt vá lỗi được cập nhật trực tiếp lên card SRE SLOs.
