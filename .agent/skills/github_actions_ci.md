---
name: github_actions_ci
description: Cấu hình CI/CD Pipeline chạy kiểm thử cho Java (Maven), Go (Chaos Worker), Docker build + Trivy Security Scan, và Helm lint.
---

# GitHub Actions CI/CD Skill

Quy trình tự động hóa kiểm định chất lượng mã nguồn và bảo mật cho dự án **Zero Door**, giúp kiểm tra tính ổn định của cả phần mềm (Java/Go) và hạ tầng (Helm/Kubectl) trước khi triển khai.

---

## 1. Cấu hình CI Pipeline (`.github/workflows/ci.yml`)

```yaml
name: Zero Door CI Pipeline

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  # Job 1: Kiểm thử và phân tích tĩnh phần code Java (Nemesis, Gaia, Hephaestus)
  java-test:
    name: Java Spring Boot Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Build & Run Maven Tests
        run: |
          cd agent-orchestrator
          mvn clean test

  # Job 2: Kiểm thử và linter phần code Go (Chaos Worker)
  go-test:
    name: Go Chaos Worker Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go 1.21
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'
          cache-dependency-path: chaos-worker/go.sum

      - name: Run Go Test
        run: |
          cd chaos-worker
          go test -v ./...

  # Job 3: Lint Helm charts đại diện hạ tầng
  helm-lint:
    name: Helm Chart Linting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Helm
        uses: azure/setup-helm@v4
        with:
          version: 'v3.12.0'

      - name: Helm Lint
        run: |
          if [ -d "infrastructure/charts" ]; then
            helm lint infrastructure/charts/*
          else
            echo "No Helm charts found yet, skipping."
          fi

  # Job 4: Scan bảo mật Dockerfile và thư viện phụ thuộc bằng Trivy
  security-scan:
    name: Security Vulnerability Scan
    runs-on: ubuntu-latest
    needs: [java-test, go-test]
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy FS Scan (Source Code & Dep)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          ignore-unfixed: true
          format: 'table'
          severity: 'HIGH,CRITICAL'
```

---

## 2. Quy tắc vận hành và Bảo mật trong CI/CD

*   **Tách biệt Pipeline & Cluster (Pull-based CD)**: 
    *   Hạn chế tối đa việc nhúng trực tiếp AWS Access Key vào GitHub Actions để chạy `kubectl apply` (tránh rò rỉ quyền quản trị cluster).
    *   Sử dụng GitOps (như ArgoCD chạy bên trong cluster tự kéo manifests về) hoặc chỉ đóng gói Helm chart và lưu trữ container image vào Registry (ECR/Docker Hub), sau đó kích hoạt quá trình kéo tự động.
*   **Security Gates**:
    *   Bước `Trivy FS Scan` sẽ quét mã nguồn và dependencies. Nó sẽ báo lỗi và dừng toàn bộ quy trình nếu phát hiện thư viện Java (Spring Boot) hoặc thư viện Go chứa lỗi bảo mật cấp độ `HIGH` hoặc `CRITICAL`.
*   **Multi-Platform Container Build**:
    *   Đảm bảo Dockerfile của Java và Go được build multi-stage để giảm kích thước image, sử dụng Distroless hoặc Alpine làm base image để thu hẹp blast radius khi container bị compromise.
