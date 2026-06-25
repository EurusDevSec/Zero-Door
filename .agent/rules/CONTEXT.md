# 🧱 CONTEXT.md — Zero Door Project Architecture
> *Last updated: 2026-06-25 | Phases 1–5 COMPLETE | Next: Phase 6 Cloud*

---

## ⚡ TL;DR — Đọc ngay cho agent mới

**Zero Door** = Multi-agent cybersecurity system trên Kubernetes:
- **Nemesis** (Red Team attacker) → **Gaia** (Observer/detector) → **Hephaestus** (Blue Team healer)
- Target: Google Online Boutique microservices trên K3d local cluster
- **QUAN TRỌNG**: Tất cả agents dùng **Python FastAPI** — KHÔNG phải Java/Spring Boot

---

## 🛠️ Tech Stack Thực Tế (Sau Migration)

| Layer | Technology | Ghi chú |
|---|---|---|
| **Container Orch.** | K3d (local) / K3s hoặc GKE (cloud) | Cluster name: `zero-door` |
| **Agents** | **Python 3.11 + FastAPI** | Gaia (:8000), Nemesis (:8000), Hephaestus (:8000) |
| **Chaos Worker** | Go 1.21 | Binary: `chaos-worker-bin` (không phải `chaos-worker`) |
| **Message Broker** | Apache Kafka (Strimzi) | Namespace: `zero-door` |
| **Observability** | Prometheus + Grafana | Namespace: `monitoring` |
| **Logging** | Fluent Bit + Elasticsearch | Namespace: `monitoring` |
| **LLM** | Ollama (local) / OpenAI API | Dùng Ollama để tiết kiệm cost |
| **CI/CD** | GitHub Actions | Python matrix build, bỏ Java/Maven |

---

## 📁 Repository Structure (Thực Tế)

```
zero_door/
├── .agent/                          # AI session memory — ĐỌC TRƯỚC
│   ├── rules/CONTEXT.md             # File này
│   ├── rules/PLAN.md                # Phase status & roadmap
│   ├── rules/ORCHESTRATOR.md        # Agent behavior rules
│   └── skills/                      # Skill guides
├── agent-orchestrator/
│   ├── gaia/main.py                 # Observer: Prometheus polling + Kafka publish
│   ├── nemesis/main.py              # Attacker: REST API + LLM planning
│   └── hephaestus/main.py           # Defender: Kafka consume + K8s heal
├── chaos-worker/
│   └── cmd/main.go                  # Go chaos executor
├── infrastructure/
│   ├── k8s/                         # Kubernetes manifests
│   ├── helm/                        # Helm charts
│   └── scripts/
│       ├── experiment_runner_direct.py  # Phase 5 experiment runner
│       ├── experiment_runner_k3d.py     # Alternative runner
│       └── analysis.py                 # Chart generation
├── docs/
│   ├── experiments/
│   │   ├── raw_data/e{1-4}_*/       # Experiment CSVs
│   │   └── analysis/                # Charts + summary_statistics.csv
│   ├── runbooks/                    # Phase runbooks
│   └── phases/                     # Phase specs
└── .github/workflows/ci.yml         # Python CI (NOT Java)
```

---

## 🌐 Namespaces & Services

| Namespace | Services |
|---|---|
| `zero-door` | gaia, nemesis, hephaestus, kafka, chaos-worker |
| `target-app` | frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart |
| `monitoring` | prometheus-operated, grafana, elasticsearch, fluent-bit |

---

## 🔌 Port Forwards (Local Dev)

```powershell
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door
kubectl port-forward svc/nemesis 9092:8000 -n zero-door
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring
# Kafka port-forward KHÔNG hoạt động từ ngoài K3d (advertised listener issue)
```

---

## 🤖 Agent APIs

### Hephaestus (:9091)
- `GET  /healthz` — health check (k8s_connected, kafka_connected)
- `GET  /cooldowns` — active healing cooldowns
- `POST /heal/trigger` — inject alert trực tiếp (bypass Kafka) — dùng trong experiments
- `GET  /heal/history` — audit log healing events (in-memory, newest first)
- `POST /experiment/reset` — **[MỚI Phase 5]** clear cooldowns + heal_history
- `GET  /network-policies` — list managed NetworkPolicies

### Nemesis (:9092)
- `GET  /healthz`
- `POST /attack/trigger` — trigger attack → Kafka → Chaos Worker
- `POST /attack/llm-plan` — LLM-based attack planning
- `GET  /attack/status`

### Gaia (:8000 — in-cluster only)
- `GET  /healthz`
- Polls Prometheus every 15s, publishes to `monitoring.alerts` topic

---

## 📊 Kafka Topics

| Topic | Publisher | Consumer |
|---|---|---|
| `monitoring.alerts` | Gaia | Hephaestus |
| `healing.actions` | Hephaestus | - |
| `attack.commands` | Nemesis | Chaos Worker |
| `attack.results` | Chaos Worker | Nemesis |
| `system.logs` | All agents | - |

---

## 🏥 Hephaestus Decision Matrix

```python
DECISION_MATRIX = {
    ("HIGH_CPU",        "WARNING"):  "SCALE_UP",
    ("HIGH_CPU",        "CRITICAL"): "RESTART",
    ("HIGH_MEMORY",     "WARNING"):  "RESTART",
    ("HIGH_ERROR_RATE", "WARNING"):  "SCALE_UP",
    ("HIGH_ERROR_RATE", "CRITICAL"): "ROLLBACK",
    ("POD_CRASH",       "WARNING"):  "RESTART",
    ("POD_CRASH",       "CRITICAL"): "RESTART",
    ("HIGH_LATENCY",    "WARNING"):  "SCALE_UP",
    ("SUSPICIOUS_LOG",  "CRITICAL"): "BLOCK_IP",
}
HEALING_COOLDOWN_SEC = 90  # per (service, action) pair
```

---

## 📏 Security Rules

- Chaos chỉ vào `target-app` namespace
- Hephaestus dùng `hephaestus-sa` ServiceAccount với namespaced Role (không phải ClusterRole)
- Không commit secrets vào Git
- NetworkPolicy TTL = 300s (auto-expire)
