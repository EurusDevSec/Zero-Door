## 💡 Context

> **Task ID**: S5-002  
> **Phase**: Phase 3 - Nemesis  
> **Sprint**: Sprint 5-6  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 5-6 (Tuần 9-12)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 Teammate (Attack templates, testing, logging)  
> **Blocked by**: S2-001 (architecture), S2-002 (Kafka), S5-001 (chaos worker)  
> **Blocks**: S9-001 (full integration)

> Phát triển Agent Nemesis (Red Team) — agent orchestrator tự động sinh payload tấn công
> sử dụng LLM (Spring AI) và điều phối Go Chaos Worker qua Kafka.

---

## 🤖 AI Refined

> **User Story:**

> As a **Red Team Agent (Nemesis)**, I want to **automatically generate attack payloads using LLM, select attack strategies, and orchestrate the Go Chaos Worker via Kafka** so that **the system is continuously tested against realistic attack scenarios.**

**Acceptance Criteria:**

- [ ] Spring Boot service `agent-nemesis` runs on K8s
- [ ] Spring AI integrated: generates SQLi payload variations from templates
- [ ] Attack Template Library: SQLi, DDoS, Resource Exhaustion templates
- [ ] Kafka producer: publishes `attack.commands` to Chaos Worker
- [ ] Kafka consumer: receives `attack.results` from Chaos Worker
- [ ] Attack Scheduler: configurable interval between attacks
- [ ] State Machine: IDLE → PLANNING → ATTACKING → COOLDOWN → IDLE
- [ ] REST API: `/api/nemesis/status`, `/api/nemesis/start`, `/api/nemesis/stop`
- [ ] Safety: cooldown timer, max concurrent attacks, namespace lock
- [ ] 🟡 Teammate: Tạo OWASP attack template library (10 SQLi templates)
- [ ] 🟡 Teammate: Test từng loại attack riêng lẻ + ghi log kết quả

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 5.2.1 Create Spring Boot module `agent-nemesis`
- [ ] 5.2.2 Integrate Spring AI (OpenAI/Ollama) for payload generation
- [ ] 5.2.3 Implement AttackTemplateService (load YAML templates)
- [ ] 5.2.4 Implement LLMPayloadGenerator: template → LLM → variations
- [ ] 5.2.5 Implement AttackOrchestrator: select strategy → generate payload → send to worker
- [ ] 5.2.6 Implement Kafka producer → `attack.commands`
- [ ] 5.2.7 Implement Kafka consumer → `attack.results`
- [ ] 5.2.8 Implement State Machine + CooldownManager
- [ ] 5.2.9 Implement REST API endpoints
- [ ] 5.2.10 Dockerize + K8s Deployment manifest
- [ ] 5.2.11 Integration test: Nemesis → Kafka → Worker → attack executes

### Subtasks — 🟡 Teammate

- [ ] 5.2.12 Create OWASP SQLi template library (`configs/attack-templates/sqli.yaml`):
    ```yaml
    templates:
      - id: sqli_basic_or
        payload: "' OR '1'='1"
        description: "Classic OR injection"
      - id: sqli_union
        payload: "' UNION SELECT NULL, username, password FROM users --"
        description: "UNION-based extraction"
      # ... thêm 8 templates nữa
    ```
- [ ] 5.2.13 Test từng loại attack riêng lẻ (manual trigger → observe result)
- [ ] 5.2.14 Ghi log + record kết quả attack vào `experiments/attack-logs/`

### Branch & PR

- [ ] Branch: `feat/s5/agent-nemesis`
- [ ] PR Created
- [ ] Unit tests pass
- [ ] Attack template library has ≥ 10 templates
- [ ] Integration with Chaos Worker verified

---

## 📝 Notes

> **LLM Prompt for SQLi Variation:**
> ```
> You are a security testing assistant. Given the SQL injection template below,
> generate 5 variations that test the same vulnerability but with different syntax.
>
> Template: ' OR '1'='1
>
> Requirements:
> - Must be valid SQL injection payloads
> - Vary the syntax (different quote styles, operators, comments)
> - Keep each variation under 100 characters
>
> Output format: JSON array of strings.
> ```

> **Safety Guards cho Nemesis:**
> - Cooldown: 5 phút giữa mỗi attack wave
> - Max concurrent attacks: 1 (sequential)
> - Namespace lock: chỉ attack `target-app` namespace
> - Kill switch: `/api/nemesis/stop` → immediate halt
> - Audit log: mọi attack đều có UUID + timestamp

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.3.1 — Agent Nemesis spec
> - Spring AI docs: https://docs.spring.io/spring-ai/reference/
> - OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
