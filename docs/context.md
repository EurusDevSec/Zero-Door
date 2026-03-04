# ZERO DOOR Project — Session Context

> File này lưu trữ toàn bộ context của quá trình phát triển dự án để không bị mất giữa các phiên chat.
> Cập nhật lần cuối: 2026-03-04 (Khởi tạo context)

---

## 1. Thông tin dự án

| Mục                 | Chi tiết                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Tên dự án**       | ZERO DOOR — Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Self-Healing cho hệ thống Microservices |
| **Trường**          | Đại học Thủ Dầu Một, Viện Công nghệ Số, 2025-2026                                                                       |
| **Nhóm**            | Lê Văn Hoàng (trưởng nhóm, code chính ~70%), hp8001 (hỗ trợ ~30%)                                                     |
| **Công nghệ chính** | Java Spring Boot (Agents), Go (Chaos Worker), Kubernetes, Kafka, Prometheus, Spring AI                                   |
| **Mục tiêu**        | Hệ thống Self-Healing cho Microservices: Attack → Detect → Heal (3 AI Agents: Nemesis, Gaia, Hephaestus)                |

## 2. Môi trường phát triển

| Thành phần          | Phiên bản / Chi tiết                         |
| ------------------- | -------------------------------------------- |
| **OS**              | Windows, terminal Git Bash/MINGW64           |
| **Java**            | OpenJDK 17+ (Spring Boot 3.x)               |
| **Go**              | 1.21+ (Chaos Worker)                          |
| **Docker/K8s**      | Docker Desktop + K3s/Minikube                |
| **Kafka**           | Bitnami Kafka Helm chart                     |
| **IDE**             | VS Code + Extensions (Java, Go, K8s)         |

## 3. Quy trình làm việc

- **Methodology**: Scrumban (Scrum + Kanban hybrid)
- **Sprint**: 2 tuần mỗi sprint, 12 sprints tổng cộng
- **Board**: GitHub Projects (6 cột: Backlog, To Do, In Progress, Review, Done, Blocked)
- **WIP Limit**: IN PROGRESS = 3 (2 Lead + 1 hp8001)
- **Communication**: Daily standup qua Discord/Zalo (5 phút)
- **Git Flow**: GitHub Flow (feature branches → PR → main)

## 4. Task Progress

### Phase 1 — Setup (Sprint 1-2)

| Task                      | Trạng thái     | Target    | Ghi chú |
| ------------------------- | -------------- | --------- | ------- |
| **S1-001** Infra Setup    | ⬜ Not Started | Sprint 1  |         |
| **S1-002** K8s Cluster    | ⬜ Not Started | Sprint 1  |         |
| **S1-003** Dev Env Setup  | ⬜ Not Started | Sprint 1  |         |
| **S2-001** Architecture   | ⬜ Not Started | Sprint 2  |         |
| **S2-002** Kafka Design   | ⬜ Not Started | Sprint 2  |         |
| **S2-003** Observability  | ⬜ Not Started | Sprint 2  |         |

### Phase 2 — Target + Gaia (Sprint 3-4)

| Task                          | Trạng thái     | Target    | Ghi chú |
| ----------------------------- | -------------- | --------- | ------- |
| **S3-001** Deploy Target App  | ⬜ Not Started | Sprint 3  |         |
| **S3-002** Agent Gaia Core    | ⬜ Not Started | Sprint 3  |         |
| **S4-001** Gaia Anomaly       | ⬜ Not Started | Sprint 4  |         |
| **S4-002** Gaia Kafka Integ   | ⬜ Not Started | Sprint 4  |         |

### Phase 3 — Nemesis (Sprint 5-6)

| Task                           | Trạng thái     | Target    | Ghi chú |
| ------------------------------ | -------------- | --------- | ------- |
| **S5-001** Go Chaos Worker     | ⬜ Not Started | Sprint 5  |         |
| **S5-002** Agent Nemesis Core  | ⬜ Not Started | Sprint 5  |         |
| **S6-001** LLM Integration    | ⬜ Not Started | Sprint 6  |         |
| **S6-002** Attack Testing     | ⬜ Not Started | Sprint 6  |         |

### Phase 4 — Hephaestus (Sprint 7-8)

| Task                              | Trạng thái     | Target    | Ghi chú |
| --------------------------------- | -------------- | --------- | ------- |
| **S7-001** Hephaestus K8s Client  | ⬜ Not Started | Sprint 7  |         |
| **S7-002** Healing Actions        | ⬜ Not Started | Sprint 7  |         |
| **S8-001** Advanced Healing       | ⬜ Not Started | Sprint 8  |         |

### Phase 5 — War Game (Sprint 9-10)

| Task                                | Trạng thái     | Target    | Ghi chú |
| ----------------------------------- | -------------- | --------- | ------- |
| **S9-001** Full Integration         | ⬜ Not Started | Sprint 9  |         |
| **S10-001** Experiments + Metrics   | ⬜ Not Started | Sprint 10 |         |

### Phase 6 — Closing (Sprint 11-12)

| Task                           | Trạng thái     | Target     | Ghi chú |
| ------------------------------ | -------------- | ---------- | ------- |
| **S11-001** Report Writing     | ⬜ Not Started | Sprint 11  |         |
| **S12-001** Defense Prep       | ⬜ Not Started | Sprint 12  |         |

## 5. Các vấn đề đã giải quyết

_(Cập nhật trong quá trình phát triển)_

## 6. Key Decisions

| Quyết định                        | Lý do                                                      |
| --------------------------------- | ---------------------------------------------------------- |
| Polyglot: Java + Go               | Java cho orchestration/AI, Go cho high-perf chaos worker   |
| Kafka cho inter-agent comm         | Async, decoupled, fault-tolerant                           |
| Google Online Boutique target app  | Well-documented, 10+ microservices, K8s-native             |
| Scrumban workflow                  | Vừa đủ kỷ luật cho 2 người, linh hoạt hơn Scrum thuần     |

---

_Cập nhật: 04/03/2026_
_Version: 1.0_
