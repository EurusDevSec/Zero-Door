# Phase 3: Agent Nemesis (Red Team) + Go Chaos Worker

> **Timeline:** Week 9-12 (Sprint 5-6)  
> **Owner:** EurusDevSec (Lead DevOps/Cloud)  
> **Milestone:** M4 (Attack Loop)  
> **Prerequisite:** Phase 2 hoàn thành (Target App running + Gaia detecting anomalies)

---

## 1. Mục tiêu Phase

Xây dựng khả năng tấn công chủ động (Proactive Attack) cho hệ thống. Nemesis (Python) đóng vai trò "Bộ não chiến lược" — sử dụng LLM (LangChain / OpenAI SDK / Ollama Python) để phân tích hệ thống và sinh ra kịch bản tấn công thông minh. Chaos Worker (Go) đóng vai trò "Tay chân thực thi" — nhận lệnh từ Nemesis qua Kafka và trực tiếp thực hiện hành động phá hoại lên Target App.

Phase này kết thúc khi Nemesis có thể sinh 3 loại kịch bản tấn công và Chaos Worker thực thi thành công các kịch bản đó trên Target App.

---

## 2. Tasks

### 2.1. Go Chaos Worker — Attack Executor

- [ ] **T3.1** Khởi tạo Go module trong thư mục `chaos-worker/`:
  ```
  chaos-worker/
  ├── go.mod
  ├── go.sum
  ├── cmd/
  │   └── worker/
  │       └── main.go           # Entry point
  ├── internal/
  │   ├── attack/
  │   │   ├── executor.go       # Attack execution interface
  │   │   ├── http_flood.go     # HTTP Flood (DDoS L7) implementation
  │   │   ├── cpu_stress.go     # CPU/Memory exhaustion implementation
  │   │   └── pod_kill.go       # Pod deletion via K8s API
  │   ├── kafka/
  │   │   ├── consumer.go       # Kafka consumer (attack.commands)
  │   │   └── producer.go       # Kafka producer (attack.results)
  │   ├── config/
  │   │   └── config.go         # Configuration from env vars
  │   └── validation/
  │       └── target.go         # Target URL/namespace validation (blast radius)
  └── Dockerfile
  ```
- [ ] **T3.2** Implement **Kafka Consumer** cho topic `attack.commands`:
  - Consumer Group: `chaos-worker-group`
  - Deserialize JSON message thành Go struct `AttackCommand`
- [ ] **T3.3** Implement **Kafka Producer** cho topic `attack.results`:
  - Sau mỗi lần thực thi attack, gửi kết quả (thành công/thất bại, duration, error) vào topic

### 2.2. Attack Executors (3 loại tấn công)

- [ ] **T3.4** Implement **HTTP Flood Attack** (`http_flood.go`):
  - Sử dụng Go goroutines để gửi hàng loạt HTTP requests đến target service
  - Configurable: target URL, concurrent connections, duration, requests per second
  - Giới hạn blast radius: Validate target URL phải thuộc `*.target-app.svc.cluster.local`
- [ ] **T3.5** Implement **CPU/Memory Stress Attack** (`cpu_stress.go`):
  - Gọi Kubernetes API để deploy một ephemeral stress-testing pod (ví dụ: `progrium/stress`) vào namespace `target-app`
  - Configurable: duration, cpu workers, memory allocation
  - Auto-cleanup: Xóa stress pod sau khi attack kết thúc
- [ ] **T3.6** Implement **Pod Kill Attack** (`pod_kill.go`):
  - Gọi Kubernetes API để xóa (delete) một pod cụ thể trong namespace `target-app`
  - Configurable: target pod label selector, số lượng pods cần kill
  - Safety check: Chỉ cho phép kill pods trong namespace `target-app`

### 2.3. Blast Radius Safety Controls

- [ ] **T3.7** Implement **Target Validation Module** (`validation/target.go`):
  - Whitelist namespace: Chỉ cho phép tấn công namespace `target-app`
  - Whitelist DNS pattern: `*.target-app.svc.cluster.local`
  - Reject bất kỳ target nào trỏ ra ngoài cluster hoặc sang namespace `zero-door`, `monitoring`, `kube-system`
  - Log tất cả rejected requests với severity CRITICAL
- [ ] **T3.8** Implement **Circuit Breaker / Kill Switch**:
  - Nếu attack chạy quá thời gian tối đa (configurable, default 120s) → tự động dừng
  - Nếu Kafka mất kết nối → tạm dừng mọi attack, không thực thi tiếp

### 2.4. Agent Nemesis — Python (Attack Strategist)

- [ ] **T3.9** Khởi tạo Nemesis project trong `agent-orchestrator/nemesis/`:
  - Thư viện cần thiết: `openai`, `langchain`, `kafka-python`
- [ ] **T3.10** Cấu hình **LLM Client** cho Nemesis:
  - Primary: Gemini API (**Gemini 3.1 Flash-Lite** hoặc model tương đương) cho production.
  - Hỗ trợ cơ chế **Round-Robin API Keys & Auto-Failover**: Đọc danh sách key từ biến môi trường `GEMINI_API_KEYS` (phân tách bằng dấu phẩy). Khi gặp lỗi `429 Rate Limit` hoặc `Quota Exceeded`, tự động chuyển sang key dự phòng tiếp theo để đảm bảo luồng tấn công không bị gián đoạn.
  - Fallback: Ollama (local LLM, model `llama3` hoặc `phi3`) cho local dev.
  - Config qua environment variables: `NEMESIS_LLM_PROVIDER=gemini|ollama`.
- [ ] **T3.11** Bảo mật khóa API trên Kubernetes (K8s Secrets):
  - Khai báo biến môi trường chứa key thông qua K8s Secrets (`nemesis-secrets`).
  - Tuyệt đối không lưu plain-text key trong YAML manifest đưa lên Git. Sử dụng manifest với placeholder trống `GEMINI_API_KEYS: ""` và áp dụng trực tiếp giá trị thật vào cụm K8s (`kubectl create secret generic`) ở môi trường chạy.
- [ ] **T3.12** Implement **Attack Plan Generator** sử dụng Gemini API:
  - Input: Trạng thái hiện tại của hệ thống (metrics summary từ Prometheus).
  - Prompt Template: Yêu cầu LLM sinh kịch bản tấn công dựa trên thông tin hệ thống.
  - Output: JSON object `AttackCommand` chứa loại tấn công, target, parameters.
  - Giới hạn: Token budget per request (max 500 tokens), request limit (max 10 calls/minute).
- [ ] **T3.13** Implement **Attack Scheduler**:
  - Gửi `AttackCommand` vào Kafka topic `attack.commands`.
  - Subscribe topic `attack.results` để nhận kết quả từ Chaos Worker, ghi nhận logs phân tích.

### 2.5. Containerization & Deployment

- [ ] **T3.14** Viết `Dockerfile` cho Chaos Worker (Multi-stage build):
  - Stage 1: Go build (`golang:1.21-alpine`)
  - Stage 2: Runtime (`gcr.io/distroless/static-debian12`)
  - Target image size: < 20MB
  - Run as non-root user (UID 65534)
- [ ] **T3.15** Viết Kubernetes manifests cho Chaos Worker:
  - Deployment + Service + ConfigMap
  - ServiceAccount với `Role` và `RoleBinding` trong namespace `target-app`:
    - Quyền: `get`, `list`, `delete` trên resource `pods`
    - Quyền: `create`, `delete` trên resource `pods` (cho stress pod injection)
  - Deploy vào namespace `zero-door`
- [ ] **T3.16** Cập nhật Kubernetes manifests cho Nemesis:
  - Deployment + Service + ConfigMap + Secret (API key cho OpenAI)
  - Deploy vào namespace `zero-door`
- [ ] **T3.17** Integration test end-to-end:
  - Nemesis sinh AttackCommand → Kafka → Chaos Worker nhận → Execute → Kết quả về Kafka → Nemesis nhận

---

## 3. Definition of Done (Tiêu chí hoàn thành Phase)

| # | Tiêu chí | Cách kiểm chứng |
|---|---|---|
| 1 | Chaos Worker pod running trong `zero-door` | `kubectl get pods -n zero-door` → chaos-worker Running |
| 2 | Nemesis pod running trong `zero-door` | `kubectl get pods -n zero-door` → nemesis Running |
| 3 | HTTP Flood attack thực thi thành công | Gửi AttackCommand HTTP_FLOOD → Chaos Worker báo success → Target App CPU/Error rate tăng trên Grafana |
| 4 | CPU Stress attack thực thi thành công | Gửi AttackCommand CPU_STRESS → Stress pod xuất hiện trong `target-app` → CPU spike trên dashboard |
| 5 | Pod Kill attack thực thi thành công | Gửi AttackCommand POD_KILL → Pod bị xóa → K8s tự tạo pod mới (vì Deployment) |
| 6 | Blast radius validation hoạt động | Gửi AttackCommand với target ngoài `target-app` namespace → Chaos Worker từ chối, log CRITICAL |
| 7 | Spring AI integration hoạt động | Nemesis gọi LLM → nhận được AttackCommand JSON hợp lệ |
| 8 | Full attack loop qua Kafka | Nemesis → Kafka (attack.commands) → Chaos Worker → Kafka (attack.results) → Nemesis log kết quả |

---

## 4. Design Questions (Bạn cần tự trả lời)

### Q1: Chaos Worker cần gọi Kubernetes API để delete pods và tạo stress pods. ServiceAccount của nó cần những quyền gì chính xác?
> Viết ra YAML của Role và RoleBinding mà bạn nghĩ là đúng. Mentor sẽ review.
> _Trả lời:_

### Q2: Nếu Nemesis gọi LLM và LLM trả về một attack type mà Chaos Worker không hỗ trợ (ví dụ: "DNS Spoofing"), chuyện gì xảy ra?
> _Trả lời:_

### Q3: HTTP Flood attack gửi hàng nghìn requests. Điều này có thể ảnh hưởng đến Kafka và Prometheus (vì chúng cùng chạy trong cluster). Bạn xử lý vấn đề "collateral damage" này thế nào?
> _Trả lời:_

### Q4: Go Chaos Worker chạy goroutines cho HTTP Flood. Nếu bạn spawn 10,000 goroutines, chuyện gì xảy ra với memory và file descriptors của container?
> _Trả lời:_

---

## 5. Kafka Message Schemas

### Topic: `attack.commands` (Input cho Chaos Worker)

```json
{
  "commandId": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "source": "nemesis",
  "attackType": "enum: HTTP_FLOOD | CPU_STRESS | MEMORY_STRESS | POD_KILL",
  "target": {
    "namespace": "target-app",
    "service": "string (K8s service name)",
    "url": "string (full URL, optional for HTTP attacks)"
  },
  "parameters": {
    "duration": "int (seconds)",
    "intensity": "enum: LOW | MEDIUM | HIGH",
    "concurrency": "int (number of concurrent workers/goroutines)",
    "customParams": {}
  },
  "safetyLimits": {
    "maxDuration": "int (absolute max seconds, kill switch)",
    "allowedNamespaces": ["target-app"]
  }
}
```

### Topic: `attack.results` (Output từ Chaos Worker)

```json
{
  "resultId": "string (UUID)",
  "commandId": "string (reference to original command)",
  "timestamp": "string (ISO 8601)",
  "source": "chaos-worker",
  "status": "enum: SUCCESS | FAILED | REJECTED | TIMEOUT",
  "attackType": "enum: HTTP_FLOOD | CPU_STRESS | MEMORY_STRESS | POD_KILL",
  "duration": "int (actual execution time in ms)",
  "details": {
    "requestsSent": "int (for HTTP flood)",
    "podsKilled": "int (for pod kill)",
    "errorMessage": "string (if failed/rejected)"
  }
}
```

---

## 6. References

| Resource | Link |
|---|---|
| Spring AI Documentation | https://docs.spring.io/spring-ai/reference/ |
| Kubernetes Python Client | https://github.com/kubernetes-client/python |
| Go Kubernetes Client (client-go) | https://github.com/kubernetes/client-go |
| Ollama Local LLM | https://ollama.com/ |
| Go Concurrency Patterns | https://go.dev/blog/pipelines |
| Chaos Engineering Principles | https://principlesofchaos.org/ |
