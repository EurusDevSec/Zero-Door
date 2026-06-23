# Phase 2: Target App Deployment + Agent Gaia (Observer)

> **Timeline:** Week 5-8 (Sprint 3-4)  
> **Owner:** EurusDevSec (Lead DevOps/Cloud) + hp8001 (Dashboard & Testing)  
> **Milestone:** M2 (Observability Live) + M3 (Detect Loop)  
> **Prerequisite:** Phase 1 hoàn thành (K3d cluster + Kafka + Prometheus + Elasticsearch running)

---

## 1. Mục tiêu Phase

Deploy ứng dụng mục tiêu (Google Online Boutique) lên K8s cluster và xây dựng Agent Gaia — hệ thống giám sát và phát hiện bất thường. Phase này kết thúc khi Gaia có thể tự động phát hiện anomaly từ metrics/logs và publish alert vào Kafka topic `monitoring.alerts`.

---

## 2. Tasks

### 2.1. Google Online Boutique Deployment

- [ ] **T2.1** Clone repository Google Online Boutique: `https://github.com/GoogleCloudPlatform/microservices-demo`
- [ ] **T2.2** Deploy lên namespace `target-app` sử dụng Kubernetes manifests.
  - Chỉ deploy các services cốt lõi để tiết kiệm RAM local:
    - `frontend` — Web UI
    - `cartservice` — Giỏ hàng (gRPC)
    - `productcatalogservice` — Danh mục sản phẩm
    - `currencyservice` — Chuyển đổi tiền tệ
    - `checkoutservice` — Thanh toán
    - `redis-cart` — Redis cho giỏ hàng
  - Tùy chọn tắt: `emailservice`, `paymentservice`, `shippingservice`, `adservice`, `recommendationservice` (nếu RAM < 12GB)
- [ ] **T2.3** Cấu hình `resources.requests` và `resources.limits` cho mỗi pod (target nhẹ nhất có thể):
  - Request: `cpu: 50m, memory: 64Mi`
  - Limit: `cpu: 200m, memory: 256Mi`
- [ ] **T2.4** Verify ứng dụng hoạt động: Port-forward frontend service và truy cập UI trên trình duyệt.
- [ ] **T2.5** Cấu hình `HPA (Horizontal Pod Autoscaler)` cho `frontend` và `cartservice`:
  - Min replicas: 1, Max replicas: 3
  - Target CPU utilization: 70%

### 2.2. Prometheus ServiceMonitor cho Target App

- [ ] **T2.6** Tạo `ServiceMonitor` resource để Prometheus scrape metrics từ các services trong `target-app` namespace.
- [ ] **T2.7** Cấu hình các PromQL alert rules cơ bản trong `PrometheusRule`:

  | Alert Name | Condition | Severity |
  |---|---|---|
  | `HighCPUUsage` | `container_cpu_usage_seconds_total` > 80% sustained 30s | warning |
  | `HighMemoryUsage` | `container_memory_working_set_bytes` > 80% of limit sustained 30s | warning |
  | `HighErrorRate` | HTTP 5xx rate > 5% sustained 15s | critical |
  | `PodCrashLooping` | `kube_pod_container_status_restarts_total` increase > 3 in 5m | critical |
  | `HighLatency` | HTTP P99 latency > 1000ms sustained 30s | warning |

- [ ] **T2.8** Tạo Grafana Dashboard chuyên biệt cho `target-app`:
  - HTTP Request Rate (req/s) per service
  - HTTP Error Rate (%) per service
  - P50/P95/P99 Latency per service
  - Pod CPU/Memory usage per service
  - Pod restart count

### 2.3. Agent Gaia — Java Spring Boot Project

- [ ] **T2.9** Khởi tạo project Java Spring Boot 3.x cho Gaia trong thư mục `agent-orchestrator/`:
  - Dependencies: `spring-boot-starter-web`, `spring-kafka`, `spring-boot-starter-actuator`
  - Package: `com.zerodoor.gaia`
- [ ] **T2.10** Cấu hình Kafka Consumer trong Gaia:
  - Subscribe topic `attack.results` (nhận kết quả tấn công từ Chaos Worker)
  - Consumer Group: `gaia-observer-group`
- [ ] **T2.11** Cấu hình Kafka Producer trong Gaia:
  - Publish topic `monitoring.alerts` (gửi alert cho Hephaestus)
  - Publish topic `system.logs` (gửi log hoạt động cho Dashboard)

### 2.4. Gaia — Anomaly Detection Logic

- [ ] **T2.12** Implement module **Prometheus Query Client** trong Gaia:
  - Sử dụng Spring `WebClient` hoặc `RestTemplate` để gọi Prometheus HTTP API (`/api/v1/query`)
  - Viết các PromQL query để kiểm tra: CPU spike, Memory spike, Error Rate spike, Latency spike
  - Polling interval: mỗi 10-15 giây
- [ ] **T2.13** Implement module **Elasticsearch Log Analyzer** trong Gaia:
  - Query logs từ Elasticsearch REST API (`/_search`)
  - Tìm kiếm pattern: `ERROR`, `Exception`, `OOMKilled`, `CrashLoopBackOff`, các SQL injection signatures
- [ ] **T2.14** Implement **Anomaly Detection Engine**:
  - So sánh metrics hiện tại với ngưỡng steady-state (đã định nghĩa ở Phase 1)
  - Nếu vượt ngưỡng → tạo Alert JSON object:
    ```json
    {
      "alertId": "uuid",
      "timestamp": "2026-01-15T10:30:00Z",
      "severity": "CRITICAL",
      "type": "HIGH_CPU",
      "source": "gaia-observer",
      "affectedService": "cartservice",
      "affectedNamespace": "target-app",
      "metric": "cpu_usage_percent",
      "currentValue": 95.2,
      "threshold": 80.0,
      "description": "CPU usage exceeded threshold for cartservice",
      "suggestedAction": "SCALE_UP or RESTART"
    }
    ```
  - Publish Alert JSON vào Kafka topic `monitoring.alerts`
- [ ] **T2.15** Implement **Deduplication Logic**: Tránh gửi cùng một alert liên tục (ví dụ: CPU cao → gửi 1 alert → chờ 60s trước khi gửi alert tương tự cho cùng service).

### 2.5. Containerization & Deployment

- [ ] **T2.16** Viết `Dockerfile` cho Gaia (Multi-stage build):
  - Stage 1: Maven build (`maven:3.9-eclipse-temurin-17`)
  - Stage 2: Runtime (`eclipse-temurin:17-jre-alpine`)
  - Target image size: < 200MB
  - Run as non-root user
- [ ] **T2.17** Viết Kubernetes manifests cho Gaia Deployment:
  - Deployment + Service + ConfigMap (Kafka bootstrap server, Prometheus URL, Elasticsearch URL)
  - Deploy vào namespace `zero-door`
  - ServiceAccount riêng (không dùng default)
- [ ] **T2.18** Deploy Gaia lên K3d cluster và verify:
  - Gaia pod Running
  - Gaia đang poll Prometheus và Elasticsearch
  - Khi manually trigger CPU stress trên target-app → Gaia publish alert vào Kafka `monitoring.alerts`

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Google Online Boutique running trên `target-app` namespace | `kubectl get pods -n target-app` — ít nhất 6 pods Running; truy cập UI qua port-forward |
| 2 | Prometheus scrape được metrics từ target-app | Prometheus Targets page → `target-app` endpoints UP |
| 3 | Grafana dashboard hiển thị metrics chi tiết của target-app | Dashboard hiển thị HTTP rate, error rate, latency, CPU/Memory per service |
| 4 | Gaia pod running trong namespace `zero-door` | `kubectl get pods -n zero-door` → gaia pod Running |
| 5 | Gaia phát hiện anomaly và publish alert vào Kafka | Simulate CPU stress trên cartservice → kiểm tra `monitoring.alerts` topic có message |
| 6 | Alert deduplication hoạt động | Cùng một anomaly chỉ gửi 1 alert trong khoảng thời gian cooldown |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Gaia nên poll Prometheus theo interval bao nhiêu giây?
> Nếu poll quá nhanh (1s) → tốn CPU. Nếu poll quá chậm (60s) → MTTD sẽ > 60s (không đạt KPI).
> _Trả lời:_

### Q2: Gaia đọc metrics từ Prometheus VÀ logs từ Elasticsearch. Hai nguồn dữ liệu này bổ sung cho nhau như thế nào?
> Ví dụ: CPU spike có thể phát hiện qua metrics, nhưng SQL injection chỉ có thể thấy trong logs. Hãy liệt kê loại anomaly nào phát hiện từ nguồn nào.
> _Trả lời:_

### Q3: Alert JSON schema ở trên có trường `suggestedAction`. Ai quyết định action này — Gaia hay Hephaestus?
> Gợi ý: Separation of Concerns — Gaia là bác sĩ chẩn đoán hay là bác sĩ điều trị?
> _Trả lời:_

### Q4: Nếu Prometheus bị down trong khi Gaia đang poll, chuyện gì xảy ra? Bạn xử lý lỗi này thế nào?
> _Trả lời:_

---

## 5. Kafka Message Schema (Đầu ra của Phase 2)

### Topic: `monitoring.alerts`

```json
{
  "alertId": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "severity": "enum: INFO | WARNING | CRITICAL",
  "type": "enum: HIGH_CPU | HIGH_MEMORY | HIGH_ERROR_RATE | HIGH_LATENCY | POD_CRASH | SUSPICIOUS_LOG",
  "source": "gaia-observer",
  "affectedService": "string (K8s service name)",
  "affectedNamespace": "string (K8s namespace)",
  "metric": "string (PromQL metric name or log pattern)",
  "currentValue": "number",
  "threshold": "number",
  "description": "string",
  "suggestedAction": "enum: SCALE_UP | RESTART | ROLLBACK | BLOCK_IP | NONE"
}
```

---

## 6. References

| Resource | Link |
|---|---|
| Google Online Boutique | https://github.com/GoogleCloudPlatform/microservices-demo |
| Prometheus HTTP API | https://prometheus.io/docs/prometheus/latest/querying/api/ |
| Spring Kafka Docs | https://docs.spring.io/spring-kafka/reference/ |
| Elasticsearch REST API | https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html |
| Kubernetes HPA | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ |
