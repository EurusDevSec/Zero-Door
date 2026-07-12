# 🎯 PLAN.md — Zero Door Roadmap & Status
> *Last updated: 2026-07-12 | Agent: Antigravity | Phases 1-6 DONE*

---

## 👥 Team Roles

- **EurusDevSec (Lead Dev)**: Kubernetes, Helm, CI/CD, agent dev, security (RBAC), cloud deployment.
- **hp8001 (Research)**: Academic paper, data collection, dashboards, testing, slides.

---

## 📅 IMPLEMENTATION STATUS

### ✅ Phase 1: Foundation — Infrastructure & Observability — DONE
- K3d cluster `zero-door` running locally.
- Kafka (Strimzi) deployed, 5 topics: `monitoring.alerts`, `healing.actions`, `attack.commands`, `attack.results`, `system.logs`.
- Prometheus + Grafana stack (`monitoring` namespace).
- Fluent Bit + Elasticsearch for log collection.
- Namespaces: `zero-door` (agents), `target-app` (boutique), `monitoring` (obs).

### ✅ Phase 2: Target App & Gaia (Observer Agent) — DONE
- Google Online Boutique deployed: frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart.
- **Gaia Agent** (Python FastAPI): polls Prometheus every 15s, Elasticsearch for logs.
- Detects: HIGH_CPU, HIGH_MEMORY, HIGH_ERROR_RATE, HIGH_LATENCY, POD_CRASH, SUSPICIOUS_LOG.
- Publishes alerts to `monitoring.alerts` Kafka topic.

### ✅ Phase 3: Nemesis (Attacker) & Go Chaos Worker — DONE
- **Nemesis Agent** (Python FastAPI): REST API orchestrator + LLM-based attack planning.
- **Chaos Worker** (Go): executes actual attacks (`chaos-worker-bin`).
- Attack types: CPU_STRESS (goroutines), HTTP_FLOOD (concurrent requests), POD_KILL (kubectl).

### ✅ Phase 4: Hephaestus (Defender) & Closed-Loop Healing — DONE
- **Hephaestus Agent** (Python FastAPI): executes K8s healing.
- Decision Matrix: HIGH_CPU/HIGH_LATENCY $\rightarrow$ SCALE_UP, HIGH_MEMORY/CRITICAL $\rightarrow$ RESTART, HIGH_ERROR_RATE/CRITICAL $\rightarrow$ ROLLBACK, SUSPICIOUS_LOG $\rightarrow$ BLOCK_IP.
- K8s RBAC: ServiceAccount `hephaestus-sa` with namespaced Role for `target-app`.

### ✅ Phase 5: War Game Experiments & Dashboard Integration — DONE
- 40 runs total: E1–E4 × AUTO+MANUAL × 5 runs/mode.
- **Control Center Dashboard v2 (AWS Cloudscape UI) & Visual Proofs**:
  - Redesigned from Cyberpunk $\rightarrow$ **AWS Cloudscape Light Theme** (white, #f2f3f3, AWS blue).
  - Fixed-height viewport layout — no vertical scroll.
  - Collapsible sidebar (290px to prevent layout squeeze) and collapsible chat drawer.
  - Auto-failover Gemini API keys retry, stress pod limit bump (1000m/512Mi), and dashboard polling (5s).
  - **SRE SLOs Monitor Card**: Displays real-time MTTD, MTTR, Uptime, and Heal Success Rate parsed dynamically from Hephaestus API history.
  - **Real-time Telemetry Line Chart (Chart.js)**: Displays rolling 60s CPU load of the selected service, changing to warning red during active stress/attacks and reverting to purple after healing.
  - **rebuild-nemesis.ps1 script**: Automates no-cache rebuilding, importing to K3d, deployment rollouts, and automatic port-forward tunnel healing for smooth local runs.

### ✅ Phase 6: Automated CI/CD & DevOps Security Optimization — DONE (2026-07-11)
- **CI/CD Pipeline Live**: Setup `.github/workflows/ci.yml` verifying Go Chaos Worker build, Python Agents compile syntax, and Helm manifests syntax.
- **Python Cache Fix**: Disabled pip cache inside actions/setup-python to prevent post-run cache save failures and ensure 100% stable runs.
- **Ingress-based Target Exposure**: Implemented Ingress manifest [target-app-ingress.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/target-app-ingress.yaml) exposing Boutique App natively on host port 8080.
- **Self-Healing Downtime Validation**: Verified HTTP 502/503 responses and automatic recovery during POD_KILL with a downtime of only **1.34s** without losing the port-forward connection.
- **Nemesis Anomaly Fix**: Corrected Prometheus query from `by (deployment)` to `by (pod)` and parsed the output regex to eliminate the service name `'None'` bug.
- **DevOps Design Specifications**: Created [phase6_cicd_optimization.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase6_cicd_optimization.md) documenting security scans (gosec, bandit, trivy), container hardening (Distroless), APM SDK, and WebSocket agent architecture.

### 🔲 Phase 7: Cloud Transition & Final Report — TODO
- Deploy stack on AWS EKS or DigitalOcean Kubernetes (DOKS).
- Verify NetworkPolicies, Ingress, and RBAC on cloud.
- Finish scientific thesis, demo video, defense slides.
- Final report comparing local K3d vs cloud metrics.

---

## 🔑 NEXT IMMEDIATE TASKS (Phase 7)

1. Triển khai cụm Kubernetes trên môi trường Cloud (Spot Instance EC2 hoặc NodePool DOKS).
2. Viết file `cloud-values.yaml` Helm để cấu hình dynamic StorageClass và Ingress Controller.
3. Quay video demo và chuẩn bị slide thuyết trình theo [demo_script.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/demo_script.md).
4. So sánh local K3d vs cloud metrics.