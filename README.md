# 🚪 ZERO DOOR — AI-Powered Self-Healing Microservices

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Phase](https://img.shields.io/badge/Phase-1%20Setup%20%26%20Research-blue)
![License](https://img.shields.io/badge/License-Academic%20Research-green)
![Java](https://img.shields.io/badge/Java-17+-orange)
![Go](https://img.shields.io/badge/Go-1.21+-00ADD8)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5)

---

## 🔍 What is ZERO DOOR?

**ZERO DOOR** là hệ thống **Proactive Defense** (phòng thủ chủ động) cho kiến trúc Microservices, kết hợp **Multi-Agent AI** với **Chaos Engineering** để xây dựng cơ chế **Self-Healing** tự động. Hệ thống hoạt động theo vòng lặp kín **Attack → Detect → Heal** bởi 3 AI Agents chuyên biệt, cho phép *tự tấn công để tìm lỗ hổng* và *tự vá lỗi* trước khi triển khai thực tế — giống như hệ miễn dịch sinh học của cơ thể.

**Mục tiêu:** Đạt MTTD < 1 phút, MTTR < 3 phút trong môi trường sandbox, chứng minh tính khả thi so với phản ứng thủ công.

---

## 🏗️ Architecture

Hệ thống gồm 3 Agents tự trị giao tiếp qua Apache Kafka:

| Agent | Vai trò | Nhiệm vụ chính |
|---|---|---|
| 🔴 **Nemesis** (Red Team) | Attacker | Tự động sinh attack payload bằng GenAI + Go Chaos Worker |
| 🟢 **Gaia** (Observer) | Monitor | Giám sát metrics (Prometheus), phát hiện anomaly real-time |
| 🔵 **Hephaestus** (Blue Team) | Defender | Tự động heal qua Kubernetes API (scale, block IP, rollback, restart) |

> 📐 Chi tiết kiến trúc: xem [docs/architecture.md](docs/architecture.md)

---

## ⚙️ Tech Stack

| Layer | Công nghệ | Lý do lựa chọn |
|---|---|---|
| **Infrastructure** | Docker, Kubernetes (K3s) | Industry standard, dễ mở rộng |
| **Backend Core** | Java Spring Boot 3.x | Mature ecosystem, Spring AI support |
| **Chaos Worker** | Go (Golang) | Hiệu năng cao, lightweight, phù hợp CLI/Worker |
| **AI Integration** | Spring AI + OpenAI/Ollama | Linh hoạt Cloud/Local LLM |
| **Message Broker** | Apache Kafka | High throughput, reliable messaging |
| **Monitoring** | Prometheus + Grafana | De-facto standard observability |
| **Logging** | ELK Stack | Centralized log analysis |

> 🔧 Dự án sử dụng **Polyglot Architecture**: Java cho orchestration/AI logic, Go cho chaos worker hiệu năng cao.

---

## 🚀 Getting Started

### Prerequisites

Đảm bảo bạn đã cài đặt các công cụ sau:

| Công cụ | Phiên bản yêu cầu | Lệnh kiểm tra |
|---|---|---|
| **Java (OpenJDK/Corretto)** | 17+ | `java --version` |
| **Maven** | 3.8+ | `mvn -version` |
| **Go** | 1.21+ | `go version` |
| **Docker Desktop** | Latest | `docker --version` |
| **Kubectl** | Latest | `kubectl version --client` |
| **Helm** | 3.x | `helm version` |
| **Git** | Latest | `git --version` |

#### Verification — Chạy các lệnh sau để kiểm tra môi trường

```bash
# Java
java --version
# Expected: openjdk 17.x.x hoặc cao hơn

# Maven
mvn -version
# Expected: Apache Maven 3.8.x+

# Go
go version
# Expected: go1.21.x hoặc cao hơn

# Docker
docker --version
docker ps
# Expected: Docker Desktop đang chạy, không có lỗi permission

# Kubernetes
kubectl version --client
# Expected: Client Version v1.x.x

# Helm
helm version
# Expected: version.BuildInfo{Version:"v3.x.x" ...}
```

### IDE Setup — VS Code Extensions

Cài đặt các extensions sau trong VS Code:

| Extension | ID | Mục đích |
|---|---|---|
| **Java Extension Pack** | `vscjava.vscode-java-pack` | Java development (IntelliSense, debugging, Maven) |
| **Spring Boot Extension Pack** | `vmware.vscode-boot-dev-pack` | Spring Boot support |
| **Go** | `golang.go` | Go development |
| **Kubernetes** | `ms-kubernetes-tools.vscode-kubernetes-tools` | K8s cluster management |
| **Docker** | `ms-azuretools.vscode-docker` | Docker container management |
| **YAML** | `redhat.vscode-yaml` | YAML syntax for K8s manifests |
| **GitLens** | `eamodio.gitlens` | Git history & blame |

### Installation

1. **Clone repository:**

```bash
git clone https://github.com/hp8001/Zero-Door-hp8001-.git
cd Zero-Door-hp8001-
```

2. **Setup Infrastructure** *(đang phát triển — Helm Charts sẽ có trong Sprint 2):*

```bash
# Tạo K8s namespaces
kubectl create namespace zero-door
kubectl create namespace monitoring
kubectl create namespace target-app

# Install Kafka via Helm (Sprint 2)
# helm install kafka bitnami/kafka -n zero-door

# Install Prometheus + Grafana (Sprint 2)
# helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

3. **Build projects:**

```bash
# Java — Spring Boot (sau khi có project skeleton)
# cd agent-orchestrator && mvn clean compile

# Go — Chaos Worker
cd chaos-worker && go build ./...
```

---

## 📁 Project Structure

```
Zero-Door/
├── docs/                          # Tài liệu dự án
│   ├── architecture.md            # Kiến trúc hệ thống chi tiết
│   ├── plan.md                    # Đề cương nghiên cứu
│   ├── references.md              # Tài liệu tham khảo
│   ├── research/                  # Tóm tắt papers nghiên cứu
│   │   └── ADARMA_SUMMARY.md     # Tóm tắt paper ADARMA
│   └── guides/                    # Hướng dẫn setup
│
├── agent-orchestrator/            # [Planned] Java Spring Boot — 3 AI Agents
│   ├── pom.xml
│   ├── src/main/java/
│   │   └── com/zerodoor/
│   │       ├── ZeroDoorApplication.java
│   │       ├── nemesis/           # Agent Nemesis (Red Team)
│   │       ├── gaia/              # Agent Gaia (Observer)
│   │       └── hephaestus/        # Agent Hephaestus (Blue Team)
│   └── src/main/resources/
│       └── application.yml
│
├── chaos-worker/                  # Go — Chaos Worker (attack executor)
│   ├── go.mod
│   ├── cmd/                       # CLI commands
│   ├── internal/
│   │   ├── attack/                # Attack executors (HTTP flood, stress)
│   │   ├── config/                # Configuration
│   │   └── worker/                # Kafka consumer + worker logic
│   └── Dockerfile
│
├── tasks/                         # Task tracking files (per sprint)
├── .github/                       # GitHub templates & workflows
├── README.md                      # ← Bạn đang đọc file này
└── LICENSE
```

---

## 📊 Key Performance Indicators (KPIs)

Target metrics trong môi trường Sandbox:

| Metric | Target | Giải thích |
|---|---|---|
| **MTTD** (Mean Time To Detect) | < 1 phút | Thời gian từ khi attack xảy ra → Gaia phát hiện |
| **MTTR** (Mean Time To Recover) | < 3 phút | Thời gian từ khi phát hiện → Hephaestus khắc phục xong |
| **Uptime** | ≥ 99% | Tỷ lệ hoạt động trong khi bị tấn công |

---

## 👥 Team

| Thành viên | Vai trò | Trách nhiệm chính |
|---|---|---|
| 🔴 **EurusDevSec (Hoàng)** | SM, PO, Lead Dev | Architecture, Core Logic (Java/Go), Infrastructure, K8s |
| 🟡 **hp8001** | Support, Dev Team | Research papers, Testing, Dashboards, Documentation |

---

## 📄 License

Dự án được thực hiện phục vụ mục đích **nghiên cứu khoa học** tại **Trường Đại học Thủ Dầu Một**.

Xem chi tiết tại [LICENSE](LICENSE).

---

## 📚 References

- [plan.md](docs/plan.md) — Đề cương nghiên cứu đầy đủ
- [architecture.md](docs/architecture.md) — Kiến trúc hệ thống
- [references.md](docs/references.md) — Tài liệu tham khảo (26 papers)
- [ADARMA Summary](docs/research/ADARMA_SUMMARY.md) — Tóm tắt paper ADARMA
