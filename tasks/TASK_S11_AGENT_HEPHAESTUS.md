## 💡 Context

> **Task ID**: S11  
> **Phase**: Phase 4 - Hephaestus  
> **Sprint**: Sprint 7-8  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 7-8 (Tuần 13-16)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 hpt8001 (Tests, Docs)  
> **Blocked by**: S4 (architecture), S8 (Gaia → alerts trigger healing)  
> **Blocks**: S12 (full integration needs all 3 agents)

> Phát triển Agent Hephaestus (Blue Team/Defender) — agent tự động phản ứng và khắc phục
> sự cố bằng Kubernetes API. Đây là "bàn tay chữa lành" của ZERO DOOR.

---

## 🤖 AI Refined

> **User Story:**

> As a **Blue Team Agent (Hephaestus)**, I want to **receive alerts from Gaia via Kafka, analyze the threat, and automatically execute healing actions via Kubernetes API (scale pods, block IPs, rollback deployments)** so that **the system recovers from attacks without human intervention.**

**Acceptance Criteria:**

- [ ] Spring Boot service `agent-hephaestus` runs on K8s
- [ ] Kafka consumer: listens on `monitoring.alerts` topic
- [ ] Kubernetes Java Client integrated (fabric8io/kubernetes-client)
- [ ] Healing actions implemented:
    - Scale: HPA hoặc manual scale replicas
    - Block IP: apply NetworkPolicy
    - Rollback: rollback K8s Deployment to previous revision
    - Restart: delete pod → K8s auto-recreate
- [ ] Decision engine: alert type → appropriate healing action
- [ ] State Machine: STANDBY → HEALING → VERIFYING → STANDBY
- [ ] Verification: after healing, check metrics normalized → publish `healing.actions`
- [ ] Priority: Hephaestus actions override Nemesis attacks (conflict resolution)
- [ ] 🟡 hpt8001: Test healing actions riêng lẻ (manual trigger each action)
- [ ] 🟡 hpt8001: Viết API docs cho Hephaestus endpoints

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 7.1.1 Create Spring Boot module `agent-hephaestus`
- [ ] 7.1.2 Integrate Kubernetes Java Client (fabric8io)
- [ ] 7.1.3 Implement ScaleAction: increase replicas
    ```java
    kubernetesClient.apps().deployments()
        .inNamespace("target-app")
        .withName(serviceName)
        .scale(targetReplicas);
    ```
- [ ] 7.1.4 Implement BlockIPAction: create NetworkPolicy
- [ ] 7.1.5 Implement RollbackAction: rollback deployment
- [ ] 7.1.6 Implement RestartAction: delete specific pod
- [ ] 7.1.7 Implement DecisionEngine: alert → action mapping
    ```
    CPU_SPIKE    → ScaleAction (increase replicas by 2)
    DDoS_DETECT  → BlockIPAction + ScaleAction
    OOM_KILLED   → RollbackAction
    ERROR_SPIKE  → RestartAction
    ```
- [ ] 7.1.8 Implement State Machine (STANDBY → HEALING → VERIFYING → STANDBY)
- [ ] 7.1.9 Implement verification: re-check metrics after healing
- [ ] 7.1.10 Implement Kafka producer → `healing.actions` (report what was done)
- [ ] 7.1.11 REST API: `/api/hephaestus/status`, `/api/hephaestus/actions`
- [ ] 7.1.12 RBAC: K8s ServiceAccount with required permissions
- [ ] 7.1.13 Dockerize + K8s Deployment + RBAC manifest

### Subtasks — 🟡 hpt8001

- [ ] 7.1.14 Test mỗi healing action riêng lẻ:
    - Scale: verify pod count increases
    - Block IP: verify NetworkPolicy created
    - Rollback: verify deployment revision changed
    - Restart: verify pod recreated
- [ ] 7.1.15 Viết API docs (Markdown): endpoints, request/response examples
- [ ] 7.1.16 Viết test scenarios document (10 scenarios)

### Branch & PR

- [ ] Branch: `feat/s7/agent-hephaestus`
- [ ] PR Created
- [ ] Unit tests pass
- [ ] Each healing action tested individually
- [ ] K8s RBAC configured correctly

---

## 📝 Notes

> **K8s RBAC cho Hephaestus:**
> ```yaml
> apiVersion: rbac.authorization.k8s.io/v1
> kind: ClusterRole
> metadata:
>   name: hephaestus-role
> rules:
>   - apiGroups: ["apps"]
>     resources: ["deployments", "deployments/scale"]
>     verbs: ["get", "list", "patch", "update"]
>   - apiGroups: [""]
>     resources: ["pods"]
>     verbs: ["get", "list", "delete"]
>   - apiGroups: ["networking.k8s.io"]
>     resources: ["networkpolicies"]
>     verbs: ["get", "list", "create", "delete"]
> ```

> **Healing Action Message:**
> ```json
> {
>   "id": "heal-uuid",
>   "timestamp": "2026-04-15T10:35:00Z",
>   "source": "hephaestus",
>   "alertId": "alert-uuid (from Gaia)",
>   "action": "SCALE_UP",
>   "target": {
>     "service": "frontend",
>     "namespace": "target-app",
>     "previousReplicas": 2,
>     "newReplicas": 4
>   },
>   "status": "SUCCESS",
>   "verificationResult": {
>     "metricsNormalized": true,
>     "cpuAfter": 45.2,
>     "responseTimeAfter": 200
>   }
> }
> ```

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.3.3 — Agent Hephaestus spec
> - Fabric8 K8s Client: https://github.com/fabric8io/kubernetes-client
> - K8s Java Client: https://github.com/kubernetes-client/java
