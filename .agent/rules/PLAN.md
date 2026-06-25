# 🎯 PLAN.md — Zero Door Roadmap & Status
> *Last updated: 2026-06-25 | Agent: Antigravity | Phases 1-5 DONE*

---

## 👥 Team Roles

- **EurusDevSec (Lead Dev)**: Kubernetes, Helm, CI/CD, agent dev, security (RBAC)
- **hp8001 (Research)**: Academic paper, data collection, dashboards, testing

---

## 📅 IMPLEMENTATION STATUS

### ✅ Phase 1: Foundation — Infrastructure & Observability — DONE
- K3d cluster `zero-door` running locally (Docker Desktop required)
- Kafka (Strimzi) deployed, 5 topics: `monitoring.alerts`, `healing.actions`, `attack.commands`, `attack.results`, `system.logs`
- Prometheus + Grafana stack (`monitoring` namespace)
- Fluent Bit + Elasticsearch for log collection
- Namespaces: `zero-door` (agents), `target-app` (boutique), `monitoring` (obs)

### ✅ Phase 2: Target App & Gaia (Observer Agent) — DONE
- Google Online Boutique deployed: frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart
- All in `target-app` namespace with HPA (1→3 replicas, 70% CPU threshold)
- **Gaia Agent** (Python FastAPI, NOT Java): polls Prometheus every 15s, Elasticsearch for logs
- Detects: HIGH_CPU, HIGH_MEMORY, HIGH_ERROR_RATE, HIGH_LATENCY, POD_CRASH, SUSPICIOUS_LOG
- Publishes alerts to `monitoring.alerts` Kafka topic

### ✅ Phase 3: Nemesis (Attacker) & Go Chaos Worker — DONE
- **Nemesis Agent** (Python FastAPI): REST API orchestrator
  - `POST /attack/trigger` — triggers attack via Kafka → Chaos Worker
  - `POST /attack/llm-plan` — LLM-based attack planning (Ollama)
  - `GET /attack/status` — attack status
- **Chaos Worker** (Go): executes actual attacks
  - Built as `chaos-worker-bin` (NOT `chaos-worker` — naming conflict fix)
  - Attack types: CPU_STRESS (goroutines), HTTP_FLOOD (concurrent requests), POD_KILL (kubectl)
- CI/CD fixed: Python matrix (Gaia, Nemesis, Hephaestus) — NOT Java/Maven

### ✅ Phase 4: Hephaestus (Defender) & Closed-Loop Healing — DONE
- **Hephaestus Agent** (Python FastAPI): consumes `monitoring.alerts`, executes K8s healing
- Decision Matrix: HIGH_CPU→RESTART, HIGH_ERROR_RATE/CRITICAL→ROLLBACK, POD_CRASH→RESTART
- Healing actions: SCALE_UP, RESTART pod, ROLLBACK deployment, BLOCK_IP (NetworkPolicy)
- Cooldown: 90s per (service, action) pair
- K8s RBAC: ServiceAccount `hephaestus-sa` with namespaced Role for `target-app`

### ✅ Phase 5: War Game Experiments — DONE (2026-06-25)
- 40 runs total: E1–E4 × AUTO+MANUAL × 5 runs/mode
- Results (AUTO mode):

| Scenario | MTTD Mean | MTTR Mean | Uptime | OK% |
|---|---|---|---|---|
| E1 CPU Stress (cartservice) | 25.6s | 1.01s | 100% | 100% ✅ |
| E2 HTTP Flood (frontend) | 1.01s | 1.01s | 100% | 100% ✅ |
| E3 Pod Kill (frontend) | 3.15s | 1.01s | 100% | 20% ⚠️ |
| E4 Combined | 5.6s | 1.01s | 100% | 100% ✅ |

- **SLAs achieved**: MTTD < 60s ✅ | MTTR < 180s ✅ | Uptime ≥ 99% ✅
- CSV data: `docs/experiments/raw_data/e{1-4}_*/`
- Charts: `docs/experiments/analysis/*.png`
- Runbook: `docs/runbooks/phase5_runbook.md`

### 🔲 Phase 6: Cloud Deployment & Final Report — TODO
- Deploy stack on GKE or AWS EKS (Spot Instance)
- Verify NetworkPolicies, RBAC on cloud
- Finish scientific thesis, demo video, defense slides
- Final report comparing local K3d vs cloud metrics

---

## 🔑 NEXT IMMEDIATE TASKS (Phase 6)

1. `helm package` tất cả charts
2. Push images lên container registry (GCR hoặc ECR)
3. Provision GKE/EKS cluster (1 node, e2-standard-4 hoặc t3.large)
4. `helm install` full stack trên cloud
5. Re-run experiment suite (E1–E4) để lấy production metrics
6. Viết final report + `docs/runbooks/phase6_runbook.md`