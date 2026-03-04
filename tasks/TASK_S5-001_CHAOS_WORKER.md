## 💡 Context

> **Task ID**: S5-001  
> **Phase**: Phase 3 - Nemesis  
> **Sprint**: Sprint 5-6  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 5 (Tuần 9-10)  
> **Assignee**: 🔴 Hoàng (Lead)  
> **Blocked by**: S1-003 (Go env), S3-001 (target app to attack)  
> **Blocks**: S5-002 (Nemesis cần worker để execute attacks)

> Phát triển Go Chaos Worker — tool thực thi attack commands từ Nemesis.
> Worker nhận lệnh qua Kafka, execute DDoS/stress test, trả kết quả.

---

## 🤖 AI Refined

> **User Story:**

> As a **Chaos Worker**, I want to **receive attack commands from Kafka and execute high-performance stress tests (HTTP flood, CPU stress, memory bomb) against the target application** so that **Nemesis can orchestrate chaos engineering scenarios.**

**Acceptance Criteria:**

- [ ] Go project structure: `chaos-worker/` with clean architecture
- [ ] Kafka consumer: listen on `attack.commands` topic
- [ ] Attack executors implemented:
    - HTTP Flood (Layer 7 DDoS): concurrent HTTP requests
    - CPU Stress: goroutines that consume CPU
    - Memory Stress: goroutines that allocate memory
- [ ] Kafka producer: publish results to `attack.results` topic
- [ ] Graceful shutdown: SIGTERM → stop attacks → cleanup
- [ ] Configurable: concurrency, duration, target URL via config/env
- [ ] Docker image < 20MB (Go static binary)
- [ ] Unit tests for each attack executor

---

## 🛠️ Implementation

### Subtasks

- [ ] 5.1.1 Setup Go project structure:
    ```
    chaos-worker/
    ├── cmd/worker/main.go
    ├── internal/
    │   ├── attack/
    │   │   ├── http_flood.go
    │   │   ├── cpu_stress.go
    │   │   └── memory_stress.go
    │   ├── kafka/
    │   │   ├── consumer.go
    │   │   └── producer.go
    │   └── config/config.go
    ├── go.mod
    ├── Dockerfile
    └── Makefile
    ```
- [ ] 5.1.2 Implement Kafka consumer (confluent-kafka-go hoặc segmentio/kafka-go)
- [ ] 5.1.3 Implement HTTP Flood executor:
    ```go
    func HTTPFlood(target string, concurrency int, duration time.Duration) AttackResult
    ```
- [ ] 5.1.4 Implement CPU Stress executor (goroutines doing math operations)
- [ ] 5.1.5 Implement Memory Stress executor (goroutines allocating slices)
- [ ] 5.1.6 Implement Kafka producer → publish `attack.results`
- [ ] 5.1.7 Implement graceful shutdown (context.WithCancel + signal handling)
- [ ] 5.1.8 Write Dockerfile (multi-stage: golang:1.21 → scratch/distroless)
- [ ] 5.1.9 Unit tests cho mỗi executor
- [ ] 5.1.10 Integration test: send command via Kafka → verify attack executes → verify result published

### Branch & PR

- [ ] Branch: `feat/s5/chaos-worker`
- [ ] PR Created
- [ ] `go test ./...` pass
- [ ] Docker image size < 20MB
- [ ] Integration test with Kafka pass

---

## 📝 Notes

> **Tại sao Go cho Chaos Worker:**
>
> | Criteria | Go | Java |
> | --- | --- | --- |
> | Concurrency | Goroutines (lightweight) | Threads (heavy) |
> | Memory | ~10MB binary | ~200MB+ JVM |
> | startup | milliseconds | seconds |
> | HTTP perf | net/http excellent | OK |
> | Docker size | ~10-20MB | ~200-400MB |

> **Attack Result Message:**
> ```json
> {
>   "id": "result-uuid",
>   "timestamp": "2026-03-15T10:35:00Z",
>   "source": "chaos-worker",
>   "attackId": "attack-uuid (from command)",
>   "type": "HTTP_FLOOD",
>   "status": "COMPLETED",
>   "metrics": {
>     "totalRequests": 10000,
>     "successRate": 45.2,
>     "avgLatency": 2500,
>     "peakLatency": 15000,
>     "duration": 60
>   }
> }
> ```

> **Safety Guards:**
> - Max duration: 120s (hard limit)
> - Max concurrency: 100 goroutines
> - Only attack services in target namespace
> - SIGTERM → immediate graceful stop

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.1 — Go in Tech Stack
> - [go-mastery.md](../docs/go-mastery.md) — Go learning guide
