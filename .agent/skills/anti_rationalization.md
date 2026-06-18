# 🛑 Anti-Rationalization Guardrails for Antigravity Agent (Zero Door)
> *Adapted to enforce production-grade DevOps and Cloud Engineering discipline.*

AI coding agents often fail not due to coding ability, but due to **cognitive shortcutting (rationalization)**—skipping critical planning, testing, security auditing, or architecture specifications.

This document lists the common excuses you (the Agent) might make during the Zero Door project, and the strict realities/quality gates you must follow instead.

---

## 🛡️ DevOps & Cloud Rationalizations

| Rationalization (The Agent's Excuse) | Reality (The Corrective Engineering Standard) |
| :--- | :--- |
| *"I will run `kubectl edit` or make manual changes to K3d/K3s resources directly to fix it quickly, and update the Helm charts/manifests later."* | **Strictly Forbidden.** This creates "configuration drift". Any change made manually is undocumented and lost when the cluster restarts. All Kubernetes resources **must be defined in YAML manifests/Helm Charts from the beginning**. |
| *"Since this is a sandbox research project, I'll just give the Hephaestus agent `cluster-admin` ClusterRole so it can easily perform any action."* | **No. Serious Security Violation.** In an enterprise, an automated healing agent with root cluster access is a massive vulnerability. Hephaestus **must run with dedicated namespaced Roles and RoleBindings** only targeting the `target-app` namespace. |
| *"The local K3d doesn't need resource quotas, limits, or persistent volume limits. I will configure them later for the cloud."* | **Incorrect.** Kafka requires persistent volumes, and running multiple Java agents alongside a microservices app will crash the cluster if `ResourceQuotas` and `LimitRanges` are not set. Configure them locally to identify memory bottlenecks early. |
| *"I don't need to configure Network Policies on local K3d, since they are only for production security."* | **No.** One of the core scientific questions is verifying if Hephaestus can block network attacks (like SQLi/DDoS) by applying NetworkPolicies. NetworkPolicies **must be tested locally** on K3d. |

---

## 💻 Code & Message Broker Rationalizations

| Rationalization (The Agent's Excuse) | Reality (The Corrective Engineering Standard) |
| :--- | :--- |
| *"I don't need to write tests for Kafka consumers/producers, because Kafka is a reliable message broker."* | **Incorrect.** Message parsing, schema evolution, and network dropouts (e.g., Kafka container restarts during chaos) must be handled gracefully in Java and Go. Write unit tests mocking Kafka and test how the Agents behave when Kafka goes offline. |
| *"I will implement Spring AI directly in the controller without fallback logic. It'll be fine."* | **Forbidden.** OpenAI API rate limits and token costs can break Nemesis. You **must implement a local Ollama fallback config** in Spring AI so that the developer can switch to local LLMs with a single toggle in `application.yml`. |
| *"I will use standard Go slices without memory pre-allocation for the Chaos Worker HTTP flood execution, it's just a test worker."* | **No.** The Go Chaos Worker is designed for performance. If it causes OOM (Out of Memory) in its own namespace because of poor resource management, it fails its goal. Write highly efficient Go code with proper GC tuning. |

---

## 👥 Blast Radius & Safety Gatekeeping

| Rationalization (The Agent's Excuse) | Reality (The Corrective Engineering Standard) |
| :--- | :--- |
| *"I will hardcode the URL target in the Nemesis attack command because it's easier than reading it dynamically."* | **No. Critical safety risk.** Nemesis generates attack payloads. If the target URL is hardcoded or not strictly validated, a typo could direct attacks to external internet servers. **Implement strict validation regex** in Chaos Worker to ensure target hosts are strictly within the `*.target-app.svc.cluster.local` domain. |
| *"We can skip automated Trivy scanning for our custom Java/Go images because they only run locally."* | **Forbidden.** Zero Door is an automated attack/heal platform. Standard software supply chain security requires scanning all base images. Secure the Dockerfiles using distroless/nonroot base images. |
