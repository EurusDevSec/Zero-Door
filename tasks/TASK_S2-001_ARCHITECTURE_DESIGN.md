## 💡 Context

> **Task ID**: S2-001  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 2 - Architecture & Design  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 2 (Tuần 3-4)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 Teammate (Diagrams)  
> **Blocked by**: S1-001, S1-003  
> **Blocks**: S3-002 (Gaia cần architecture), S5-002 (Nemesis cần architecture), S7-001 (Hephaestus)

> Thiết kế kiến trúc chi tiết cho toàn bộ hệ thống: 3 Agents, communication protocol,
> state machines, conflict resolution. Đây là blueprint cho toàn bộ development.

---

## 🤖 AI Refined

> **User Story:**

> As a **Software Architect**, I want to **design the complete system architecture including agent interactions, Kafka topics, message schemas, and conflict resolution** so that **all team members have a clear, unambiguous blueprint to implement from.**

**Acceptance Criteria:**

- [ ] Architecture document hoàn chỉnh (update `docs/architecture.md`)
- [ ] System diagram (Mermaid/Draw.io) — 3 Agents + Kafka + Target App + Observability
- [ ] Agent State Machine diagrams (mỗi agent: IDLE → ACTIVE → COOLDOWN)
- [ ] Kafka topic design: 5 topics + JSON message schema cho mỗi topic
- [ ] Conflict Resolution protocol documented (priority: Hephaestus > Nemesis)
- [ ] API contracts giữa các agents (input/output schema)
- [ ] 🟡 Teammate: Vẽ architecture diagrams trên Draw.io (theo sketch của Hoàng)
- [ ] 🟡 Teammate: Tóm tắt 3 papers quan trọng (CHESS, AIOps Survey, Netflix Chaos)

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 2.1.1 Design Kafka topics + message schemas (JSON format)
    ```
    attack.commands     — Nemesis → Chaos Worker
    attack.results      — Chaos Worker → Nemesis
    monitoring.alerts   — Gaia → all agents
    healing.actions     — Hephaestus → K8s
    system.logs         — All agents → Dashboard
    ```
- [ ] 2.1.2 Design Agent State Machines
    - Nemesis: IDLE → PLANNING → ATTACKING → COOLDOWN → IDLE
    - Gaia: MONITORING → ALERT_TRIGGERED → ANALYZING → MONITORING
    - Hephaestus: STANDBY → HEALING → VERIFYING → STANDBY
- [ ] 2.1.3 Design Conflict Resolution protocol
    - Priority: Hephaestus (heal) > Gaia (observe) > Nemesis (attack)
    - Cooldown: 5 min after healing before next attack
    - Circuit breaker: max 3 consecutive attacks without healing
- [ ] 2.1.4 Define API contracts (message schemas)
- [ ] 2.1.5 Update `docs/architecture.md` với tất cả design decisions
- [ ] 2.1.6 Review architecture với mentor/GVHD (nếu có)

### Subtasks — 🟡 Teammate

- [ ] 2.1.7 Vẽ System Architecture diagram (Draw.io) theo sketch Hoàng cung cấp
- [ ] 2.1.8 Vẽ Agent State Machine diagrams (3 diagrams)
- [ ] 2.1.9 Tóm tắt paper CHESS (Self-Healing + Chaos Engineering)
- [ ] 2.1.10 Tóm tắt paper AIOps Survey (LLM for operations)

### Branch & PR

- [ ] Branch: `docs/architecture-design`
- [ ] PR Created
- [ ] Architecture reviewed by Hoàng
- [ ] Diagrams render correctly in Markdown

---

## 📝 Notes

> **Kafka Message Schema Example:**
> ```json
> // Topic: attack.commands
> {
>   "id": "uuid",
>   "timestamp": "2026-01-15T10:30:00Z",
>   "source": "nemesis",
>   "type": "SQL_INJECTION",
>   "target": {
>     "service": "frontend",
>     "endpoint": "/api/products",
>     "method": "POST"
>   },
>   "payload": {
>     "template": "sqli_basic_or",
>     "mutation": "' OR 'a'='a"
>   },
>   "priority": "MEDIUM",
>   "correlationId": "war-game-001"
> }
> ```

> **Design Decisions Log:**
>
> | Decision | Options Considered | Chosen | Rationale |
> | --- | --- | --- | --- |
> | Agent communication | REST, gRPC, Kafka | Kafka | Async, decoupled, replay |
> | Message format | Protobuf, Avro, JSON | JSON | Simple, debug-friendly |
> | Conflict resolution | Voting, Priority, Coordinator | Priority-based | Simple, deterministic |

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.2 — Architecture
> - [architecture.md](../docs/architecture.md) — Current architecture
> - CHESS paper — Self-Healing evaluation framework
