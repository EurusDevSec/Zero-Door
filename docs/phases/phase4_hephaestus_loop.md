# Phase 4: Agent Hephaestus (Blue Team) + Closed-Loop Integration

> **Timeline:** Week 13-16 (Sprint 7-8)  
> **Owner:** EurusDevSec (Lead DevOps/Cloud)  
> **Milestone:** M5 (Heal Loop) + M6 (Full Loop)  
> **Prerequisite:** Phase 2-3 hoàn thành (Gaia detecting + Nemesis/ChaosWorker attacking)

---

## 1. Mục tiêu Phase

Xây dựng Agent Hephaestus — "Bác sĩ phẫu thuật" của hệ thống — có khả năng nhận cảnh báo từ Gaia, phân tích nguyên nhân, ra quyết định hành động phục hồi, và trực tiếp tác động lên Kubernetes API để chữa trị hệ thống. 

Phase này là **phase quan trọng nhất** vì nó đóng vòng lặp Attack → Detect → **Heal**, biến hệ thống thành Self-Healing hoàn chỉnh.

---

## 2. Tasks

### 2.1. Agent Hephaestus — Python

- [ ] **T4.1** Khởi tạo Hephaestus project trong `agent-orchestrator/hephaestus/`:
  - Thư viện cần thiết: `kubernetes` (Official Kubernetes Python Client), `kafka-python`
- [ ] **T4.2** Cấu hình Kafka Consumer:
  - Subscribe topic `monitoring.alerts` (nhận alert từ Gaia)
  - Consumer Group: `hephaestus-defender-group`
- [ ] **T4.3** Cấu hình Kafka Producer:
  - Publish topic `healing.actions` (log hành động phục hồi đã thực hiện)
  - Publish topic `system.logs` (log hoạt động chung)

### 2.2. Healing Decision Engine

- [ ] **T4.4** Implement **Healing Decision Matrix** — Logic ánh xạ loại anomaly sang hành động phục hồi:

  | Alert Type | Severity | Healing Action | Mô tả |
  |---|---|---|---|
  | `HIGH_CPU` | WARNING | `SCALE_UP` | Tăng replica count qua HPA hoặc manual scale |
  | `HIGH_CPU` | CRITICAL | `RESTART` | Restart pod bị ảnh hưởng (rolling restart) |
  | `HIGH_MEMORY` | CRITICAL | `RESTART` | Restart pod để giải phóng memory leak |
  | `HIGH_ERROR_RATE` | CRITICAL | `ROLLBACK` | Rollback deployment về revision trước |
  | `POD_CRASH` | CRITICAL | `RESTART` | Force delete pod, để Deployment tạo lại |
  | `SUSPICIOUS_LOG` (SQLi pattern) | CRITICAL | `BLOCK_IP` | Tạo NetworkPolicy chặn source IP |
  | `HIGH_LATENCY` | WARNING | `SCALE_UP` | Scale up để phân tải |

- [ ] **T4.5** (Tùy chọn nâng cao) Implement **AI-Assisted Decision Making**:
  - Gửi context (alert details + system state) cho LLM (OpenAI Python SDK / LangChain)
  - LLM phân tích và đề xuất healing action phù hợp nhất
  - Có fallback về rule-based matrix (T4.4) nếu LLM không khả dụng

### 2.3. Healing Action Executors (Kubernetes Python Client)

- [ ] **T4.6** Implement **Scale Up Action**:
  - Gọi Kubernetes API: `PATCH /apis/apps/v1/namespaces/target-app/deployments/{name}/scale`
  - Tăng replica count lên `currentReplicas + 1` (giới hạn max = HPA max replicas)
- [ ] **T4.7** Implement **Restart Pod Action**:
  - Gọi Kubernetes API: `DELETE /api/v1/namespaces/target-app/pods/{podName}`
  - Deployment controller sẽ tự tạo pod mới thay thế
  - Chờ pod mới `Ready` trước khi đánh dấu heal thành công
- [ ] **T4.8** Implement **Rollback Deployment Action**:
  - Gọi Kubernetes API: Rollback Deployment về revision trước
  - Kiểm tra rollback thành công bằng cách verify pod template hash thay đổi
- [ ] **T4.9** Implement **Block IP via NetworkPolicy Action**:
  - Tạo Kubernetes `NetworkPolicy` resource trong namespace `target-app`
  - Cấu hình `ingress` rule deny traffic từ source IP cụ thể
  - Có expiry mechanism: tự động xóa NetworkPolicy sau N phút (tránh block vĩnh viễn)

### 2.4. RBAC & Security Configuration

- [ ] **T4.10** Tạo **ServiceAccount** riêng cho Hephaestus: `hephaestus-sa`
- [ ] **T4.11** Tạo **Role** trong namespace `target-app` với quyền tối thiểu:

  | Resource | Verbs | Lý do |
  |---|---|---|
  | `pods` | `get`, `list`, `delete` | Restart pod, check pod status |
  | `deployments` | `get`, `list`, `patch` | Scale up, rollback |
  | `deployments/scale` | `get`, `patch` | Scale replicas |
  | `replicasets` | `get`, `list` | Check rollout status |
  | `networkpolicies` | `get`, `list`, `create`, `delete` | Block/unblock IP addresses |

- [ ] **T4.12** Tạo **RoleBinding** binding `hephaestus-sa` với Role trên.
- [ ] **T4.13** Verify RBAC: Test rằng Hephaestus ServiceAccount **KHÔNG CÓ** quyền trên các namespace khác (`zero-door`, `monitoring`, `kube-system`).

### 2.5. Healing Action Logging & Audit Trail

- [ ] **T4.14** Sau mỗi healing action, publish log vào Kafka topic `healing.actions`:
  ```json
  {
    "healingId": "string (UUID)",
    "timestamp": "string (ISO 8601)",
    "source": "hephaestus",
    "triggerAlertId": "string (reference to Gaia's alert)",
    "action": "enum: SCALE_UP | RESTART | ROLLBACK | BLOCK_IP",
    "target": {
      "namespace": "target-app",
      "resource": "string (deployment/pod/networkpolicy name)"
    },
    "status": "enum: SUCCESS | FAILED | PARTIAL",
    "details": {
      "previousState": "string",
      "newState": "string",
      "durationMs": "int",
      "errorMessage": "string (if failed)"
    }
  }
  ```
- [ ] **T4.15** Implement **Healing Cooldown**: Sau khi heal một service, chờ N giây trước khi cho phép heal lại cùng service đó (tránh thrashing loop: heal → Gaia vẫn thấy anomaly → heal lại → lặp vô tận).

### 2.6. Closed-Loop Integration Testing

- [ ] **T4.16** **End-to-End Test Scenario 1 (CPU Stress → Scale Up)**:
  1. Nemesis gửi `CPU_STRESS` attack command
  2. Chaos Worker thực thi stress trên `cartservice`
  3. Prometheus scrape CPU metric tăng vọt > 80%
  4. Gaia phát hiện → publish alert `HIGH_CPU` vào `monitoring.alerts`
  5. Hephaestus nhận alert → execute `SCALE_UP` trên cartservice
  6. `cartservice` replicas tăng → CPU per pod giảm → hệ thống ổn định
  7. **Đo MTTD** (timestamp attack → timestamp alert) và **MTTR** (timestamp alert → timestamp heal success)

- [ ] **T4.17** **End-to-End Test Scenario 2 (Pod Kill → Restart)**:
  1. Nemesis gửi `POD_KILL` attack
  2. Chaos Worker delete 1 pod `frontend`
  3. Prometheus phát hiện pod count giảm
  4. Gaia phát hiện → publish alert `POD_CRASH`
  5. Hephaestus nhận alert → verify pod đã bị xóa → đợi Deployment tự recreate → confirm pod Ready
  6. **Đo MTTD** và **MTTR**

- [ ] **T4.18** **End-to-End Test Scenario 3 (HTTP Flood → Block IP)**:
  1. Nemesis gửi `HTTP_FLOOD` attack
  2. Chaos Worker flood `frontend` service
  3. Prometheus phát hiện error rate > 5%
  4. Gaia phát hiện + phân tích log tìm source IP → publish alert `HIGH_ERROR_RATE` với source IP
  5. Hephaestus nhận alert → tạo NetworkPolicy chặn source IP
  6. Error rate giảm → hệ thống ổn định
  7. **Đo MTTD** và **MTTR**

### 2.7. Containerization & Deployment

- [ ] **T4.19** Cập nhật Dockerfile cho `agent-orchestrator` (đã bao gồm cả Gaia, Nemesis, Hephaestus).
- [ ] **T4.20** Viết/cập nhật Kubernetes manifests cho Hephaestus Deployment:
  - ServiceAccount: `hephaestus-sa`
  - Mount ServiceAccount token để gọi K8s API từ bên trong pod
  - ConfigMap: Kafka bootstrap, healing cooldown duration, max replicas

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Hephaestus pod running trong `zero-door` | `kubectl get pods -n zero-door` → hephaestus Running |
| 2 | RBAC đúng: Hephaestus chỉ có quyền trên `target-app` | `kubectl auth can-i --as=system:serviceaccount:zero-door:hephaestus-sa delete pods -n target-app` → yes; `kubectl auth can-i --as=system:serviceaccount:zero-door:hephaestus-sa delete pods -n kube-system` → no |
| 3 | Scale Up healing hoạt động | CPU stress attack → Gaia alert → Hephaestus scale up → replica count tăng |
| 4 | Restart healing hoạt động | Pod kill attack → Gaia alert → Hephaestus confirm pod recreated |
| 5 | Block IP healing hoạt động | HTTP flood → Gaia alert → Hephaestus tạo NetworkPolicy → error rate giảm |
| 6 | Full loop MTTD < 60s trong ≥ 50% test runs | Chạy 10 lần scenario 1 → ≥ 5 lần MTTD < 60s |
| 7 | Full loop MTTR < 180s trong ≥ 50% test runs | Chạy 10 lần scenario 1 → ≥ 5 lần MTTR < 180s |
| 8 | Healing cooldown ngăn thrashing | Trigger alert liên tục → Hephaestus chỉ heal 1 lần trong cooldown window |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Hephaestus chạy trong namespace `zero-door` nhưng cần quyền tác động lên namespace `target-app`. Bạn dùng `Role` + `RoleBinding` hay `ClusterRole` + `ClusterRoleBinding`? Tại sao?
> Gợi ý: Đây là câu hỏi về Cross-namespace RBAC. Nghiên cứu cách bind Role ở namespace A cho ServiceAccount ở namespace B.
> _Trả lời:_

### Q2: K8s HPA (Horizontal Pod Autoscaler) cũng có thể tự scale khi CPU cao. Nếu cả HPA và Hephaestus cùng scale lên, chuyện gì xảy ra?
> _Trả lời:_

### Q3: Hephaestus tạo NetworkPolicy để block IP. Nhưng source IP trong Kubernetes cluster có thể bị thay đổi bởi kube-proxy/iptables (SNAT). Làm sao bạn lấy được "real" source IP?
> Gợi ý: Tìm hiểu `externalTrafficPolicy: Local` trên Service.
> _Trả lời:_

### Q4: Healing Cooldown nên đặt bao lâu? Quá ngắn → thrashing. Quá dài → hệ thống chịu đựng attack quá lâu mà không được heal lần thứ 2 nếu lần đầu thất bại.
> _Trả lời:_

---

## 5. References

| Resource | Link |
|---|---|
| Kubernetes Python Client | https://github.com/kubernetes-client/python |
| K8s RBAC Authorization | https://kubernetes.io/docs/reference/access-authn-authz/rbac/ |
| K8s NetworkPolicy | https://kubernetes.io/docs/concepts/services-networking/network-policies/ |
| K8s Deployment Rollback | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment |
| K8s HPA | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ |
