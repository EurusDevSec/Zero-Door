# 🎯 PLAN.md — Zero Door Roadmap & Status
> *Last updated: 2026-06-18 | Focus: Local-First Sandbox & Multi-Agent Architecture*

---

## 👥 Team Roles & Risks Management

- **EurusDevSec (Lead Dev, DevOps, Cloud)**: Kubernetes cluster design (K3d/K3s), Helm charts packaging, Kafka setup, CI/CD pipeline, agent orchestration development, security (RBAC, NetworkPolicies), and architecture.
- **hp8001 (Research, Testing, Dashboards)**: Academic paper contributions, data collection from chaos scenarios, Prometheus/Grafana dashboard setups, ELK logging analysis, and testing validation.

---

## 📅 IMPLEMENTATION STATUS & ROADMAP

### Phase 1: Foundation — Infrastructure & Observability (Week 1 - 4) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase1_foundation.md)
- [x] Define DevOps-focused Research Plan in [docs/plan.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/plan.md).
- [x] Configure local Kubernetes sandbox template via [infrastructure/k3d-config.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/k3d-config.yaml).
- [ ] Deploy Apache Kafka on K3d via Helm (Bitnami or Strimzi Operator) with 5 core topics.
- [ ] Set up Prometheus + Grafana stack for scraping Kubernetes metrics.
- [ ] Set up Fluent Bit + Elasticsearch stack for gathering pod container logs.

### Phase 2: Target App & Gaia (Observer Agent) (Week 5 - 8) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase2_target_gaia.md)
- [ ] Deploy Google Online Boutique microservices to `target-app` namespace.
- [ ] Configure HPA (Autoscaling) and Prometheus ServiceMonitors for the Boutique services.
- [ ] Create Java Spring Boot skeleton for Gaia (Observer Agent).
- [ ] Implement anomaly detection logic in Gaia (scrapes Prometheus/ES alerts, publishes to Kafka topic `monitoring.alerts`).

### Phase 3: Nemesis (Attacker) & Go Chaos Worker (Week 9 - 12) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase3_nemesis_chaos.md)
- [ ] Create Go skeleton for Chaos Worker. Implement attack executors (CPU stress, HTTP Flood, Pod delete).
- [ ] Create Java Spring Boot skeleton for Nemesis (Red Team).
- [ ] Integrate Spring AI (OpenAI API / Local Ollama) into Nemesis to dynamically synthesize attack payloads based on system metrics.
- [ ] Establish communication via Kafka topic `attack.commands` and `attack.results`.

### Phase 4: Hephaestus (Defender Agent) & Closed-Loop Healing (Week 13 - 16) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase4_hephaestus_loop.md)
- [ ] Create Java Spring Boot skeleton for Hephaestus (Blue Team).
- [ ] Configure ServiceAccount and RBAC (Roles & RoleBindings) in `target-app` namespace for Hephaestus.
- [ ] Implement healing action execution (using official Kubernetes Java Client) triggered by Gaia's alerts.
- [ ] End-to-end integration: Run the full Attack → Detect → Heal loop.

### Phase 5: Chaos Experiments & Data Collection (Week 17 - 20) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase5_experiments.md)
- [ ] Design chaos scenarios (SQL injection, HTTP flood, resource OOM).
- [ ] Run automated chaos test suites and measure MTTD, MTTR, and Uptime KPIs.
- [ ] Export Grafana metrics, export event logs from Elasticsearch, and format data to CSV for analysis.

### Phase 6: Cloud Transition & Final Scientific Report (Week 21 - 24) — [Specs](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/phases/phase6_cloud_report.md)
- [ ] Deploy the Helm stack on a single AWS EC2 instance running K3s (FinOps Spot Instance).
- [ ] Verify security, Network Policies, and Pod permissions using EKS Pod Identity / AWS IAM Roles if migrating to EKS.
- [ ] Finish scientific thesis writing, record demo video, and prepare slides for the university council defense.