## 💡 Context

> **Task ID**: S3-002  
> **Phase**: Phase 2 - Target App + Gaia  
> **Sprint**: Sprint 3-4  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 3-4 (Tuần 5-8)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 Teammate (Grafana + Tests)  
> **Blocked by**: S2-001 (architecture), S2-002 (Kafka), S2-003 (Prometheus), S3-001 (target app)  
> **Blocks**: S5-002 (Nemesis needs Gaia online to complete loop)

> Phát triển Agent Gaia (Observer) — agent giám sát hệ thống, phát hiện bất thường,
> và gửi alert qua Kafka. Đây là "mắt thần" của ZERO DOOR.

---

## 🤖 AI Refined

> **User Story:**

> As a **Gaia Observer Agent**, I want to **continuously monitor Prometheus metrics from the target application, detect anomalies (CPU spike, error rate increase, response time degradation), and publish alerts via Kafka** so that **Hephaestus can take healing actions and the team can visualize system health in real-time.**

**Acceptance Criteria:**

- [ ] Spring Boot service `agent-gaia` runs on K8s
- [ ] Prometheus client integrated: scrapes metrics from target app via Prometheus API
- [ ] Anomaly detection: threshold-based detection cho CPU, Memory, Error Rate, Response Time
- [ ] Kafka producer: publishes `monitoring.alerts` topic khi detect anomaly
- [ ] Alert message format đúng với schema đã design (S2-001)
- [ ] State machine: MONITORING → ALERT_TRIGGERED → ANALYZING → MONITORING
- [ ] REST API: `GET /api/gaia/status` returns current state + last alert
- [ ] 🟡 Teammate: Viết test cases cho Gaia (happy path + edge cases)
- [ ] 🟡 Teammate: Customize Grafana dashboard "Gaia Alert History"
- [ ] 🟡 Teammate: Thu thập baseline metrics (CPU/Memory usage when idle)
- [ ] Docker image build thành công, deploy trên K8s `zero-door` namespace

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 3.2.1 Create Spring Boot module `agent-gaia`
- [ ] 3.2.2 Implement Prometheus client (WebClient → Prometheus HTTP API)
    ```java
    // Scrape CPU usage
    GET http://prometheus-server.monitoring:9090/api/v1/query?query=rate(container_cpu_usage_seconds_total{namespace="target-app"}[5m])
    ```
- [ ] 3.2.3 Implement MetricsCollector service (scheduled every 15s)
- [ ] 3.2.4 Implement AnomalyDetector (threshold-based):
    - CPU > 80% → alert
    - Memory > 85% → alert
    - Error rate > 5% → alert
    - Response time > 2000ms → alert
- [ ] 3.2.5 Implement Kafka producer → publish to `monitoring.alerts`
- [ ] 3.2.6 Implement State Machine (MONITORING → ALERT_TRIGGERED → ANALYZING → MONITORING)
- [ ] 3.2.7 Implement REST API: `/api/gaia/status`, `/api/gaia/alerts`
- [ ] 3.2.8 Dockerize + K8s Deployment manifest
- [ ] 3.2.9 Integration test: deploy on K8s, trigger CPU spike → verify alert published

### Subtasks — 🟡 Teammate

- [ ] 3.2.10 Viết test cases document (markdown): 10 test scenarios
- [ ] 3.2.11 Thu thập baseline metrics: CPU, Memory khi target app idle (screenshot Grafana)
- [ ] 3.2.12 Tạo Grafana dashboard "Gaia Alert History" (alert count, alert types, response time)

### Branch & PR

- [ ] Branch: `feat/s3/agent-gaia`
- [ ] PR Created
- [ ] Unit tests pass
- [ ] Kafka message received in console consumer
- [ ] Docker image builds successfully

---

## 📝 Notes

> **Gaia Alert Message Schema:**
> ```json
> {
>   "id": "alert-uuid",
>   "timestamp": "2026-02-15T10:30:00Z",
>   "source": "gaia",
>   "severity": "WARNING",
>   "type": "CPU_SPIKE",
>   "metric": {
>     "name": "cpu_usage",
>     "value": 92.5,
>     "threshold": 80.0,
>     "unit": "percent"
>   },
>   "affectedService": "frontend",
>   "namespace": "target-app",
>   "recommendation": "SCALE_UP"
> }
> ```

> **Key Design Decisions:**
>
> - **Threshold-based first** (not ML): đủ cho POC, dễ explain cho hội đồng
> - **Prometheus HTTP API** (not direct scraping): decouple from Prometheus internals
> - **15s scrape interval**: match Prometheus default, not too aggressive

> **Tham khảo:**
>
> - [architecture.md](../docs/architecture.md) — Gaia architecture
> - [plan.md](../docs/plan.md) Section 5.3.2 — Agent Gaia spec
> - Prometheus HTTP API: https://prometheus.io/docs/prometheus/latest/querying/api/
