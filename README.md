🚪 ZERO DOOR — AI-Powered Self-Healing Microservices

## Project Overview

Zero Door is an Proactive Defense System for Microservices
This Project apply Multi-Agent System combine Chaos Engineering Technique to build Mechanism Self-Healing


This System active follow Closed loop: Attack -> Detect -> Heal by 3 Agents:
- Agent Nemesis (Red Team): auto generate attack scenerio with GenAI.
- Agent Gaia (Observer): Observating and detect unusual via real time
- Agent Hephaestus (Blue Team): perform Self-Healing action via Kubernetes API

## Tech Stack

- Go
- Kubernetes
- Docker
- GenAi (OpenAI, Gemini, Others)

> This project use Polygot Architecture  model

High-Level Architecture

> Event Driven Architecture via Kafka to ensure decentralization and scalability

(more detail in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md))


Here is the professional **README.md v1** translated into English for your **ZERO DOOR** project, incorporating all the standard sections required for a high-quality repository:


## 🚀 Getting Started

### Prerequisites

To run this project locally, ensure you have the following installed:

* **Java 17+** & **Go 1.21+**
* **Docker Desktop** with **K3s/Minikube** enabled
* **Kubectl** & **Helm 3.x**
* **GitHub CLI (gh)** for task management

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/EurusDevSec/Zero-Door.git
cd Zero-Door

```


2. **Setup Infrastructure:**
*(Under development - Helm Charts coming soon)*
```bash
helm install zero-door ./infra/helm

```



## 📊 Key Performance Indicators (KPIs)

Target metrics for the Sandbox environment:

* **MTTD (Mean Time To Detect):** < 1 minute.
* **MTTR (Mean Time To Recover):** < 3 minutes.
* **Uptime:** ≥ 99% during active attack simulations.

## 👥 Team

* **🔴 EurusDevSec (SM, PO, DevTeams):** Architecture, Core Logic (Java/Go), Infrastructure.
* **🟡 hp8001 (Support, DevTeam):** Research, Testing, Dashboards.

## 📄 License

This project is conducted for scientific research purposes at **Thủ Dầu Một University**.

