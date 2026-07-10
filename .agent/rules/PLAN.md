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

### ✅ Phase 5: War Game Experiments & Dashboard Integration — DONE (2026-07-10)
- 40 runs total: E1–E4 × AUTO+MANUAL × 5 runs/mode
- Results (AUTO mode):
  - **SLAs achieved**: MTTD < 60s (Gaia detects in 20-30s) ✅ | MTTR < 180s (Hephaestus recovers in 35-45s) ✅ | Uptime ≥ 99.9% ✅
- **Control Center Dashboard v1 (Cyberpunk UI)**: Real-time metrics, dynamic topology, console log buffers.
- **Control Center Dashboard v2 (AWS Cloudscape UI)** ✅ — *2026-07-10*:
  - Redesigned from dark Cyberpunk → **AWS Cloudscape Light Theme** (white, #f2f3f3, AWS blue).
  - Fixed-height viewport layout — no vertical scroll. 4-panel grid: `55%/45% rows × 230px/1fr cols`.
  - Left sidebar collapsible (48px collapsed), right chat panel collapsible with floating trigger.
  - Topology flow fully visible (Nemesis → Kafka → Boutique App → Hephaestus/Gaia).
  - Agent Insights preview tile, skeleton shimmer loading, dark terminal log console.
  - Full CSS token system using Cloudscape design tokens.
- **Failover & Stability Fixes**:
  - Auto-failover and retry over 2 Gemini API keys (preventing LLM 429 rate-limit errors).
  - Raised stress pod resource limits to 1000m CPU and 512Mi Memory in `cpu_stress.go` (fixing OOMKilled failures at HIGH intensity).
  - Configured Prometheus CPU query to `[2m]` range vector to ensure steady metrics calculation.
  - Reduced dashboard polling rate to 5s and added Connection Lost UI Banner to prevent port-forward crashes on Windows.
  - Implemented automatic target app scale-down back to 1 replica on Reset System.

### 🔲 Phase 6: Cloud Deployment & Final Report — TODO
- Deploy stack on GKE or AWS EKS (Spot Instance).
- Verify NetworkPolicies, RBAC on cloud.
- Finish scientific thesis, demo video, defense slides.
- Final report comparing local K3d vs cloud metrics.

---

## 🔑 NEXT IMMEDIATE TASKS (Phase 6)

1. Quay video demo và chuẩn bị slide thuyết trình theo [demo_script.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/demo_script.md).
2. `helm package` tất cả charts.
3. Push images lên container registry (GCR hoặc ECR).
4. Provision GKE/EKS cluster và deploy full stack trên cloud.
5. So sánh local K3d vs cloud metrics.