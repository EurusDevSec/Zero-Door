# Phase 1: Foundation — Infrastructure & Observability

> **Timeline:** Week 1-4 (Sprint 1-2)  
> **Owner:** EurusDevSec (Lead DevOps/Cloud)  
> **Milestone:** M1 (Infra Ready) + M2 (Observability Live)

---

## 1. Mục tiêu Phase

Xây dựng nền tảng hạ tầng hoàn chỉnh trên **Local K3d** để toàn bộ các Phase sau có môi trường ổn định để phát triển và chạy thử nghiệm. Phase này kết thúc khi bạn có một Kubernetes cluster chạy đủ 3 namespace, Kafka messaging đang hoạt động, và Prometheus/Grafana đang hiển thị metrics của cluster.

**Nguyên tắc:** Local-First. Toàn bộ hạ tầng phải chạy ổn định trên máy cá nhân (K3d) trước khi nghĩ đến Cloud.

---

## 2. Tasks

### 2.1. Kubernetes Cluster Setup

- [ ] **T1.1** Cài đặt Docker Desktop, K3d CLI, kubectl, Helm CLI trên máy local.
- [ ] **T1.2** Tạo cluster K3d sử dụng file cấu hình [infrastructure/k3d-config.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/k3d-config.yaml).
  - Cluster name: `zero-door`
  - 1 Server node + 2 Agent nodes
  - Port mapping: `8080:80`, `8443:443` qua LoadBalancer
  - Disable Traefik (sẽ dùng Nginx Ingress thay thế)
- [ ] **T1.3** Tạo 3 Kubernetes Namespaces:
  - `zero-door` — Chứa 3 AI Agents + Kafka
  - `target-app` — Chứa Google Online Boutique (ứng dụng mục tiêu)
  - `monitoring` — Chứa Prometheus, Grafana, Elasticsearch, Fluent Bit
- [ ] **T1.4** Cấu hình `ResourceQuota` và `LimitRange` cho mỗi namespace để giới hạn tài nguyên, tránh OOM treo máy local.

### 2.2. Apache Kafka Deployment

- [ ] **T1.5** Deploy Apache Kafka vào namespace `zero-door` sử dụng Bitnami Helm Chart.
  - Cấu hình cho local: 1 broker, 1 partition/topic, replication factor = 1.
  - Enable Persistent Volume (Local Storage Class).
- [ ] **T1.6** Tạo 5 Kafka Topics:

  | Topic | Mục đích |
  |---|---|
  | `attack.commands` | Nemesis gửi lệnh tấn công cho Chaos Worker |
  | `attack.results` | Chaos Worker báo kết quả tấn công cho Gaia |
  | `monitoring.alerts` | Gaia gửi cảnh báo anomaly cho Hephaestus |
  | `healing.actions` | Hephaestus ghi log hành động phục hồi |
  | `system.logs` | Tất cả agents gửi log thống nhất cho Dashboard |

- [ ] **T1.7** Kiểm tra Kafka hoạt động bằng cách produce/consume một test message qua CLI (`kafka-console-producer.sh` / `kafka-console-consumer.sh`).

### 2.3. Observability Stack

- [ ] **T1.8** Deploy **Prometheus + Grafana** vào namespace `monitoring` sử dụng Helm Chart `kube-prometheus-stack`.
  - Prometheus scrape interval: 15s (default).
  - Grafana accessible qua NodePort hoặc port-forward.
- [ ] **T1.9** Cấu hình Prometheus scrape các K8s metrics mặc định:
  - `node_cpu_seconds_total`, `node_memory_MemAvailable_bytes`
  - `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`
  - `kube_pod_status_phase`, `kube_deployment_status_replicas`
- [ ] **T1.10** Tạo Grafana Dashboard cơ bản hiển thị:
  - CPU & Memory usage per namespace
  - Pod count & Pod status (Running/Pending/Failed)
  - Node resource utilization
- [ ] **T1.11** Deploy **Fluent Bit** (DaemonSet) vào namespace `monitoring` để thu thập container logs từ tất cả nodes.
- [ ] **T1.12** Deploy **Elasticsearch** (single-node mode, cấu hình nhẹ cho local) vào namespace `monitoring`.
- [ ] **T1.13** Cấu hình Fluent Bit output đẩy logs về Elasticsearch. Kiểm tra bằng cách query log qua Elasticsearch REST API.

### 2.4. Networking & Security Foundation

- [ ] **T1.14** Cài đặt **Nginx Ingress Controller** (vì đã disable Traefik trong k3d-config).
- [ ] **T1.15** Tạo cấu hình `NetworkPolicy` cơ bản cho namespace `monitoring`:
  - Cho phép Prometheus scrape metrics từ tất cả namespaces.
  - Cho phép Fluent Bit đọc logs từ tất cả nodes.

### 2.5. Project Structure & CI Foundation

- [ ] **T1.16** Tạo cấu trúc thư mục dự án chuẩn:
  ```
  Zero-Door/
  ├── agent-orchestrator/          # Python Agents (Nemesis, Gaia, Hephaestus)
  │   ├── requirements.txt
  │   └── gaia/ (etc.)
  ├── chaos-worker/                # Go Chaos Worker
  │   ├── go.mod
  │   ├── cmd/
  │   └── internal/
  ├── infrastructure/              # Helm charts, K3d config, K8s manifests
  │   ├── k3d-config.yaml
  │   ├── namespaces/
  │   ├── charts/
  │   └── manifests/
  └── docs/
  ```
- [ ] **T1.17** Khởi tạo GitHub Actions CI Pipeline cơ bản (file `.github/workflows/ci.yml`):
  - Job: Lint Helm charts (`helm lint`)
  - Job: Placeholder cho Python check + Go build (sẽ có code ở Phase 2-3)

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | K3d cluster running với 3 namespaces | `kubectl get ns` hiển thị `zero-door`, `target-app`, `monitoring` |
| 2 | Kafka broker running và 5 topics đã tạo | `kubectl get pods -n zero-door` Kafka pod Running; `kafka-topics.sh --list` hiển thị 5 topics |
| 3 | Prometheus đang scrape metrics | `kubectl port-forward svc/prometheus-server 9090:9090 -n monitoring` → truy cập `localhost:9090/targets` thấy targets UP |
| 4 | Grafana dashboard hiển thị metrics | `kubectl port-forward svc/grafana 3000:80 -n monitoring` → đăng nhập → thấy dashboard CPU/Memory |
| 5 | Fluent Bit → Elasticsearch pipeline hoạt động | Gửi request GET tới Elasticsearch `_cat/indices` thấy index log được tạo |
| 6 | ResourceQuota đã được cấu hình | `kubectl describe resourcequota -n zero-door` hiển thị limits |

---

## 4. Design Questions (Bạn cần tự trả lời)

> Trả lời các câu hỏi này trước khi bắt tay vào triển khai. Ghi câu trả lời trực tiếp vào đây.

### Q1: Tại sao chọn K3d thay vì Minikube hoặc Kind cho local development?
> _Trả lời:_ K3d chạy K3s (bản phân phối Kubernetes siêu nhẹ của Rancher) bên trong các Docker containers. K3d khởi động cực nhanh (chỉ mất ~20-30 giây), tiêu thụ rất ít tài nguyên (chỉ khoảng 1GB RAM cho node nền), hỗ trợ mô phỏng multi-node dễ dàng và quản lý qua Docker rất mượt mà. Minikube nặng hơn do chạy qua VM, còn Kind đôi khi khởi động lâu hơn và tiêu thụ nhiều RAM hơn K3d trên môi trường Windows.

### Q2: ResourceQuota cho namespace `zero-door` nên đặt bao nhiêu CPU và Memory?
> Gợi ý: Máy bạn có bao nhiêu RAM? Chia cho 3 namespace + system overhead thì mỗi namespace được bao nhiêu?
> _Trả lời:_ Máy có 16GB RAM, sau khi trừ đi OS (~3GB), Chrome (~2GB), IDE (~1GB) và Docker Engine (~1.5GB) thì còn khoảng 8-8.5GB RAM khả dụng cho K3d. Ta phân bổ quota hợp lý như sau để tránh OOM treo máy:
> - `zero-door`: 1 CPU / 1Gi RAM requests, 3 CPU / 3Gi RAM limits (đủ cho Kafka KRaft combined pod ~700MB và 3 Agents sau này).
> - `target-app`: 1.5 CPU / 2Gi RAM requests, 3 CPU / 4Gi RAM limits (đủ cho 10 microservices nhỏ của Online Boutique).
> - `monitoring`: 0.5 CPU / 2Gi RAM requests, 2 CPU / 4Gi RAM limits (đủ cho Prometheus, Grafana, Elasticsearch và Fluent Bit sau khi đã tối ưu hóa).

### Q3: Kafka trên local chỉ cần 1 broker, 1 partition. Nhưng khi lên Cloud, bạn sẽ thay đổi gì?
> _Trả lời:_ Khi lên Cloud (môi trường Production):
> - Triển khai tối thiểu 3 Kafka Brokers trải rộng trên 3 Availability Zones (AZs) để đảm bảo độ khả dụng cao (High Availability).
> - Tăng `replication.factor` cho các topic quan trọng lên 3 và đặt `min.insync.replicas` là 2 để tránh mất mát dữ liệu.
> - Tăng số lượng partitions (ví dụ: 3 hoặc 6 partitions mỗi topic) tương ứng với số lượng replicas của consumer group để xử lý dữ liệu song song (parallel processing).
> - Sử dụng dịch vụ managed hoàn toàn như Amazon MSK hoặc Confluent Cloud để giảm tải vận hành hạ tầng.

### Q4: StorageClass nào phù hợp cho Kafka PersistentVolume trên K3d?
> Gợi ý: Chạy `kubectl get storageclass` trên K3d để xem có sẵn gì.
> _Trả lời:_ Trên K3d, StorageClass mặc định là `local-path` (do Rancher phát triển). Nó tự động cấp phát và mount thư mục trực tiếp từ host node vào container, rất phù hợp và tiện lợi cho việc chạy thử nghiệm local mà không cần cấu hình các Cloud CSI drivers phức tạp.

### Q5: Tại sao disable Traefik mặc định của K3d và thay bằng Nginx Ingress?
> _Trả lời:_ Mặc dù Traefik được tích hợp sẵn rất tốt trong K3s, nhưng Nginx Ingress Controller là chuẩn công nghiệp thực tế và được sử dụng rộng rãi nhất ở các doanh nghiệp hiện nay. Tự tay cài đặt Nginx Ingress giúp nắm vững kiến thức cài đặt Helm, cấu hình Ingress Class, và tránh xung đột cổng 80/443 với Traefik.

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Máy dev không đủ RAM (< 8GB) để chạy full stack | K3d cluster OOM, pod Evicted | Cấu hình ResourceQuota chặt, giảm replicas về 1, tắt services không cần thiết |
| Kafka PV bị mất khi xóa cluster K3d | Mất dữ liệu test messages | Tạo external volume mount trong k3d-config hoặc accept data loss ở local |
| Prometheus scrape quá nhiều targets gây lag | Grafana chậm, metrics bị gap | Tăng scrape_interval lên 30s ở local, chỉ scrape namespace cần thiết |

---

## 6. References

| Resource | Link |
|---|---|
| K3d Documentation | https://k3d.io/ |
| Bitnami Kafka Helm Chart | https://github.com/bitnami/charts/tree/main/bitnami/kafka |
| kube-prometheus-stack | https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack |
| Fluent Bit Kubernetes | https://docs.fluentbit.io/manual/installation/kubernetes |
| Elasticsearch Single-node | https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html |
