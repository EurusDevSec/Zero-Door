# Phase 6: Automated CI/CD Pipeline & DevOps Security Optimization

> **Timeline:** Week 21-24 (Sprint 11-12)  
> **Owner:** EurusDevSec (DevOps/SecOps Engineer) + hp8001 (QA & Testing)  
> **Milestone:** M6 (CI/CD Pipeline Live & Security Audited)  
> **Prerequisite:** Phase 5 hoàn thành (Steady-state experiments verified)

---

## 1. Mục tiêu Phase

Xây dựng và tích hợp một quy trình **CI/CD hoàn chỉnh (Zero Door CI)** và áp dụng các tiêu chí bảo mật nâng cao (**DevSecOps**) cho toàn bộ vòng đời sản phẩm. Tối ưu hóa Docker container, bảo mật Kubernetes manifests, thiết lập bộ quét lỗ hổng tĩnh (SAST), và chuẩn hóa kiến trúc bảo mật phục vụ định hướng SaaS Control Plane.

---

## 2. Tasks

### 2.1. Thiết lập CI/CD Pipeline tối ưu (GitHub Actions)

- [x] **T6.1** Cấu hình **Helm & Manifests Lint Job**:
  - Tự động lint và kiểm tra cú pháp tất cả các file manifest YAML trong `infrastructure/manifests/` sử dụng Helm CLI và Python YAML parser.
  - Mục tiêu: Phát hiện sớm lỗi thụt lề (indentation) và sai cấu hình YAML trước khi apply vào cluster.

- [x] **T6.2** Cấu hình **Go Chaos Worker Build Job**:
  - Cài đặt Go 1.21, tải dependencies bất đồng bộ, chạy `go build` cho binary `chaos-worker` và chạy lệnh phân tích tĩnh cú pháp `go vet` để kiểm tra lỗi logic sớm.

- [x] **T6.3** Cấu hình **Python Agents Build Job (Nemesis, Gaia, Hephaestus)**:
  - Cài đặt Python 3.11, tải dependencies song song qua Matrix build.
  - **Tối ưu hóa**: Loại bỏ tính năng `pip cache` trong `setup-python` để tránh lỗi đè cache lưu trữ gây đỏ/sập pipeline không đáng có, duy trì pipeline nhanh và ổn định.
  - Thực hiện Syntax check bằng lệnh `python -m py_compile main.py`.

### 2.2. DevOps & Cloud Security Optimization (Tiêu chí nâng cao)

Để chuyển dự án từ mức Sandbox sang chuẩn doanh nghiệp (Production-grade), các tiêu chuẩn bảo mật sau được đưa vào thiết kế và tài liệu hóa:

- [x] **T6.4** Tối ưu hóa Container Image (**Docker Multi-stage & Distroless/Alpine**):
  - Áp dụng Multi-stage build cho Go Chaos Worker và các Python Agents để giảm dung lượng file image cuối xuống dưới 50MB.
  - Sử dụng base image là `Alpine` hoặc `Distroless` (không chứa shell `/bin/sh` hoặc `/bin/bash` và các lệnh curl/wget) nhằm triệt tiêu khả năng kẻ tấn công chiếm quyền điều khiển container và leo thang đặc quyền (Blast Radius Reduction).

- [x] **T6.5** Tích hợp quét tĩnh lỗ hổng mã nguồn (**SAST - Static Application Security Testing**):
  - Thêm bước quét bảo mật code Go bằng **`gosec`** và quét code Python bằng **`bandit`** trong CI pipeline để tự động cảnh báo các lỗ hổng như SQL Injection, Command Injection, hardcoded tokens, v.v.

- [ ] **T6.6** Thẩm định cấu hình Kubernetes (**Infrastructure as Code Scanning**):
  - Thay thế vòng lặp YAML thô sơ bằng công cụ **`trivy config`** hoặc **`checkov`** để quét các file K8s manifests.
  - Mục tiêu: Tự động từ chối (Block) các pull requests chứa cấu hình sai về bảo mật (misconfigurations) như:
    - Pod chạy bằng quyền `root` (thiếu `runAsNonRoot: true`).
    - Container có quyền ghi file hệ thống (thiếu `readOnlyRootFilesystem: true`).
    - ServiceAccount được gán quyền RBAC quá lớn.

- [ ] **T6.7** Định hình kiến trúc **SaaS Control Plane & WebSocket Agent**:
  - Giải quyết bài toán bảo mật: Trong thực tế, khách hàng không bao giờ chấp nhận mở cổng Kubernetes API (port 6443) ra ngoài Internet cho Hephaestus truy cập từ xa để vá lỗi.
  - Thiết kế giải pháp: Chuyển đổi Hephaestus thành một **WebSocket Agent** chạy ngầm bên trong cụm của khách hàng. Agent này sẽ tự chủ động tạo kết nối WebSocket hướng ra ngoài (Outbound connection) đến SaaS Control Plane của Zero Door để nhận lệnh vá lỗi.
  - Lợi ích: Không cần mở bất kỳ cổng inbound nào trên Firewall của khách hàng, đảm bảo an toàn tuyệt đối.

- [ ] **T6.8** Tích hợp **Application APM SDK**:
  - Thay vì chỉ cào CPU/RAM gián tiếp từ cAdvisor của Prometheus (chỉ số phần cứng bên ngoài), định hướng thiết kế một bộ **APM SDK** cắm trực tiếp vào mã nguồn của Web App mục tiêu.
  - SDK này giúp thu thập trực tiếp các chỉ số sâu của code như: gRPC latency, Database query duration, HTTP Error rates trên từng function để Gaia phát hiện các bất thường logic tinh vi hơn.

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | GitHub Actions Workflow chạy thành công | 100% các Jobs (Helm Lint, Python Build, Go Build) hiển thị trạng thái màu xanh lá cây trên repository |
| 2 | Code của Nemesis, Gaia, Hephaestus vượt qua kiểm tra cú pháp | `conclusion: success` trong logs của CI run |
| 3 | Sơ đồ kiến trúc SaaS Control Plane và thiết kế WebSocket Agent được tài liệu hóa | Tài liệu thiết kế tích hợp vào báo cáo khoa học chương 6 |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Tại sao việc sử dụng Distroless Docker Image lại giúp hạn chế Blast Radius khi container bị hack?
> _Trả lời:_ Bởi vì Distroless image chỉ chứa duy nhất ứng dụng và các thư viện runtime cần thiết. Nó hoàn toàn không có Shell (bash/sh), trình quản lý gói (apt/apk), hay các công cụ mạng (curl/wget/nc). Nếu hacker chiếm được quyền thực thi code trong container, họ cũng không có shell để chạy lệnh, không thể tải thêm công cụ exploit về, và không thể dò quét mạng nội bộ của cụm.

### Q2: Sự khác biệt lớn nhất giữa việc giám sát phần cứng (Node/Pod CPU) và giám sát ứng dụng (APM SDK) là gì?
> _Trả lời:_ Giám sát phần cứng chỉ cho biết Pod có bị nghẽn hay không. Giám sát APM SDK cho biết chính xác dòng code nào, câu truy vấn SQL nào đang bị chậm, hoặc API cụ thể nào trả về lỗi 500, giúp định vị nguyên nhân sự cố nhanh hơn gấp nhiều lần.
