---
name: addy_commands
description: Enforce structured SDLC workflows via command triggers (/spec, /plan, /build, /test, /review, /ship) for the Antigravity agent.
---

# ⚡ Slash Commands Workflow (Addy Osmani style SDLC)

To ensure senior-level software engineering discipline, you (the Agent) will respond to and guide the user through the following slash commands during the Zero Door development lifecycle:

---

## 🛠️ Command Catalog & Quality Gates

### 1. `/spec` (Specification Gate)
*   **Trigger**: When starting a new agent or infrastructure component (e.g., Gaia Monitor Agent, Go Chaos Worker, Kafka setup).
*   **Action**: Create a specification document. Do NOT write code yet.
*   **Quality Gate**: The spec must explicitly list:
    - Component responsibility & interaction logic.
    - Kafka topics involved, message payload schemas (JSON).
    - Kubernetes resources (Deployment, Service, ServiceAccount, RBAC Roles, ConfigMaps, Secrets).
    - Security considerations (RBAC Least Privilege, Blast Radius limiters).

### 2. `/plan` (Planning Gate)
*   **Trigger**: Once the spec is approved.
*   **Action**: Update [PLAN.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/PLAN.md) (or [docs/plan.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/plan.md)) and break the feature down into small, atomic, and verifiable task lists.
*   **Quality Gate**: Each task should take less than 4 hours to build and must have a corresponding test/verification criteria.

### 3. `/build` (Implementation Gate)
*   **Trigger**: Once the plan is set.
*   **Action**: Write clean, modular, and well-commented code.
*   **Quality Gate**: Adhere strictly to [CONTEXT.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/CONTEXT.md) stack definitions (Java 17, Spring Boot, Go, K3d, Kafka). Always reference active files in commits.

### 4. `/test` (Verification Gate)
*   **Trigger**: After coding is complete or during testing phases.
*   **Action**: Run local compile tests (Maven test, Go test) and execute Helm/Kubectl validation commands.
*   **Quality Gate**: 100% pass rate. Test cover edge cases, message formats, and exception Handling (e.g., Kafka down).

### 5. `/review` (Review & Quality Gate)
*   **Trigger**: Before creating a Pull Request to `staging` or `main`.
*   **Action**: Perform a self-review of the code diff.
*   **Quality Gate**: Run static analysis, code linter, and check for hardcoded secrets, excessive resource consumption, and unhandled errors. Check that security controls (RBAC, namespace isolation) are in place.

### 6. `/ship` (Release Gate)
*   **Trigger**: When deploying from local to cloud environment.
*   **Action**: Run CI/CD build, run security container image scanning (Trivy), deploy Helm charts to the target cluster.
*   **Quality Gate**: Clean CI pipeline. Cloud environment (K3s on EC2) validated, logs visible in Elasticsearch, and dashboard showing system metrics.

---

## 📋 Standard Reply Format
When a user inputs any of these commands, you must start your response by declaring the current SDLC gate, verifying its acceptance criteria, and detailing the outcomes before proceeding.
