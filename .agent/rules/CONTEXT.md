# 🧱 CONTEXT.md — Zero Door Project Architecture
> *Last updated: 2026-06-18 | Env: K3d (Local Dev Sandbox) & K3s on AWS EC2 Spot Instance (Cloud Production)*

---

## 🛠️ Core Tech Stack & Infrastructure

| Layer | Technology | Deployment Strategy (Local vs. Cloud) |
|---|---|---|
| **Container Orchestration** | Kubernetes (K3d for local / K3s for cloud) | **Local**: k3d running on dev machine (0$). <br>**Cloud**: Single AWS EC2 Spot Instance (t3.medium/t3.large, ~$15/mo) running lightweight K3s. |
| **Agent Core (Nemesis/Gaia/Hephaestus)** | Java 17+, Spring Boot 3.x, Spring AI | Containerized in `zero-door` namespace. Spring AI manages connections to LLMs. |
| **Chaos Worker** | Go (Golang 1.21+) | High-performance, low-memory worker container executing attacks on target app namespace. |
| **AI Integration** | OpenAI API / Local Ollama | **Local**: Ollama (local model) to save API costs. <br>**Cloud**: OpenAI API (with budget limiters). |
| **Message Broker** | Apache Kafka (Bitnami Helm Chart) | Self-managed Kafka running inside Kubernetes (Strimzi or Bitnami). 5 core topics for Agent communication. |
| **Observability (O11y)** | Prometheus + Grafana | Prometheus scrapes target-app endpoints. Grafana displays metrics (CPU, RAM, HTTP Error Rate, Latency). |
| **Logging** | Fluent Bit + Elasticsearch | Fluent Bit collects container stdout/stderr logs and pushes to Elasticsearch for query. |
| **DevOps & IaC** | Helm, GitHub Actions | Helm Charts packaging the whole stack. GitHub Actions pipeline runs build/test, Trivy container scanning. |

---

## 📁 Repository Directory Structure

```
Zero-Door/
├── .agent/                      # AI Agent session persistence & instructions
│   ├── rules/                   # Project rules (CONTEXT.md, ORCHESTRATOR.md, PLAN.md)
│   ├── skills/                  # Domain-specific skill guides (save_checkpoint.md, anti_rationalization.md)
│   └── workflows/               # Session memory (session_memory.md)
├── docs/                        # Project documentation (plan.md, architecture.md, references.md)
├── agent-orchestrator/          # Java Spring Boot — Nemesis (Red), Gaia (Observer), Hephaestus (Blue)
│   ├── pom.xml
│   └── src/main/java/com/zerodoor/
├── chaos-worker/                # Go — Chaos Worker (attack executor)
│   ├── cmd/
│   ├── internal/
│   └── Dockerfile
├── infrastructure/              # K3d config & Helm charts for Kafka, Prometheus, Fluent Bit, App
└── README.md                    # Main readme
```

---

## 📏 System Rules & Security Guidelines

- **Blast Radius Control**: Chaos experiments must be strictly limited to the `target-app` namespace. The `zero-door` and `monitoring` namespaces must be protected against failure injection.
- **Least Privilege RBAC**: 
  - Hephaestus and Chaos Worker must use custom Kubernetes ServiceAccounts.
  - Do NOT grant Cluster-wide admin permissions. Use namespaced `Role` and `RoleBinding` targeting the `target-app` namespace.
- **Environment & Configuration Isolation**:
  - Code must be **12-Factor/Cloud-Agnostic**. All configuration URLs (Kafka Brokers, LLM Endpoints, API keys) must be loaded from Environment Variables via ConfigMaps and Secrets.
  - API Keys must be managed securely through K8s Secrets (Base64 in local dev, managed using Local Env files). Never commit secrets to Git.
- **Autoscaling vs. Healing Conflict**:
  - When Chaos Worker injects failure, ensure the interaction between HPA (Autoscaling) and Hephaestus's Healing actions (e.g. Restart/Rollback) is decoupled and coordinated through Kafka topics.

---

## 🚦 Engineering Discipline & Workflows
To avoid quality degradation and spoon-feeding, you must adhere to the engineering workflows defined in:
1.  **[Anti-Rationalization Guardrails](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/skills/anti_rationalization.md)**: Strictly counters shortcuts like skipping local testing, over-privileging K8s ServiceAccounts, and omitting resource quotas.
2.  **[Slash Commands Lifecycle](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/skills/addy_commands.md)**: Operates under command-driven gates (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`) to enforce step-by-step SDLC compliance.
