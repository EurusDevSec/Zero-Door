## 💡 Context

> **Task ID**: S1-003  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 1 - Foundation  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 1 (Tuần 1-2)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 hp8001 (Research)  
> **Blocked by**: S1-001  
> **Blocks**: S5-001 (Go worker cần Go env), S5-002 (Nemesis cần Java env)

> Thiết lập môi trường phát triển đầy đủ cho cả 2 ngôn ngữ chính (Java + Go)
> và các công cụ hỗ trợ. hp8001 đọc + tóm tắt papers nghiên cứu.

---

## 🤖 AI Refined

> **User Story:**

> As a **Developer**, I want to **have Java 17+, Go 1.21+, Docker, and all required tooling installed and configured** so that **I can immediately start coding agents and chaos worker without setup delays.**

**Acceptance Criteria:**

- [ ] Java 17+ installed: `java --version` ✅
- [ ] Maven/Gradle configured: `mvn --version` hoặc `gradle --version` ✅
- [ ] Go 1.21+ installed: `go version` ✅
- [ ] Docker Desktop running: `docker ps` ✅
- [ ] VS Code extensions: Java Extension Pack, Go, Kubernetes, Docker
- [ ] Spring Boot project skeleton created (Maven, Spring Web, Spring AI, Kafka)
- [ ] Go module initialized (`go mod init github.com/yourorg/chaos-worker`)
- [ ] 🟡 hp8001: Đọc + tóm tắt paper ADARMA (1-2 trang)
- [ ] 🟡 hp8001: Viết README v1 cho project

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 1.3.1 Cài Java 17+ (OpenJDK hoặc Amazon Corretto)
- [ ] 1.3.2 Cài Maven/Gradle
- [ ] 1.3.3 Tạo Spring Boot project skeleton (start.spring.io)
    - Dependencies: Spring Web, Spring Kafka, Spring AI, Actuator, Lombok
- [ ] 1.3.4 Cài Go 1.21+
- [ ] 1.3.5 Tạo Go module cho chaos-worker
- [ ] 1.3.6 Verify: `mvn clean compile` (Java) + `go build ./...` (Go) cả 2 pass
- [ ] 1.3.7 Cài VS Code extensions

### Subtasks — 🟡 hp8001

- [ ] 1.3.8 Đọc paper ADARMA (link: [ACM](https://dl.acm.org/doi/abs/10.5555/3615924.3615949))
- [ ] 1.3.9 Viết tóm tắt ADARMA (1-2 trang): mục tiêu, methodology, kết quả, relevance cho ZERO DOOR
- [ ] 1.3.10 Viết README.md v1 theo template (Hoàng cung cấp outline)

### Branch & PR

- [ ] Branch: `feat/s1/dev-environment`
- [ ] PR Created
- [ ] All tools verified (screenshot)
- [ ] Both projects compile successfully

---

## 📝 Notes

> **Spring Boot Project Structure:**
> ```
> agent-orchestrator/     # Hoặc tách riêng: agent-nemesis/, agent-gaia/, agent-hephaestus/
> ├── pom.xml
> ├── src/main/java/
> │   └── com/zerodoor/
> │       ├── ZeroDoorApplication.java
> │       ├── nemesis/
> │       ├── gaia/
> │       └── hephaestus/
> └── src/main/resources/
>     └── application.yml
> ```

> **Go Chaos Worker Structure:**
> ```
> chaos-worker/
> ├── go.mod
> ├── go.sum
> ├── main.go
> ├── cmd/
> ├── internal/
> │   ├── attack/
> │   ├── config/
> │   └── worker/
> └── Dockerfile
> ```

> **Template cho hp8001 — README outline:**
> 1. Project Name + Badge
> 2. What is ZERO DOOR? (2-3 sentences)
> 3. Architecture Diagram (link to architecture.md)
> 4. Tech Stack table
> 5. Getting Started (Prerequisites, Installation)
> 6. Team
> 7. License

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.1 — Tech Stack
> - [references.md](../docs/references.md) — Paper ADARMA
