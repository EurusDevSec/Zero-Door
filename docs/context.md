# ZERO DOOR Project — Session Context

> File này lưu trữ toàn bộ context của quá trình phát triển dự án để không bị mất giữa các phiên chat.
> Cập nhật lần cuối: 2026-03-05

---

## 1. Thông tin dự án

| Mục                 | Chi tiết                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Tên dự án**       | ZERO DOOR — Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Self-Healing cho hệ thống Microservices |
| **Trường**          | Đại học Thủ Dầu Một, Viện Công nghệ Số, 2025-2026                                                                       |
| **Nhóm**            | Lê Văn Hoàng (trưởng nhóm, code chính ~70%), hpt8001 (hỗ trợ ~30%)                                                     |
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
- **WIP Limit**: IN PROGRESS = 3 (2 Lead + 1 hpt8001)
- **Communication**: Daily standup qua Discord/Zalo (5 phút)
- **Git Flow**: GitHub Flow (feature branches → PR → main)
- **GitHub Milestone** = 1 Sprint (12 milestones tổng cộng)

## 4. Task Progress

> **Task ID format**: S[số thứ tự] — tuần tự từ S1→S13
> **Sprint** ghi trong cột Target, không gắn vào Task ID

### Phase 1 — Setup & Research (Sprint 1-2)

| Task   | Tên                    | Trạng thái     | Sprint    | Ghi chú |
| ------ | ---------------------- | -------------- | --------- | ------- |
| **S1** | Infra Setup            | ⬜ Not Started | Sprint 1  |         |
| **S2** | K8s Cluster            | ⬜ Not Started | Sprint 1  |         |
| **S3** | Dev Environment        | ⬜ Not Started | Sprint 1  |         |
| **S4** | Architecture Design    | ⬜ Not Started | Sprint 2  |         |
| **S5** | Kafka Setup            | ⬜ Not Started | Sprint 2  |         |
| **S6** | Observability          | ⬜ Not Started | Sprint 2  |         |

### Phase 2 — Target + Gaia (Sprint 3-4)

| Task   | Tên                    | Trạng thái     | Sprint    | Ghi chú |
| ------ | ---------------------- | -------------- | --------- | ------- |
| **S7** | Deploy Target App      | ⬜ Not Started | Sprint 3  |         |
| **S8** | Agent Gaia             | ⬜ Not Started | Sprint 3-4 |        |

### Phase 3 — Nemesis (Sprint 5-6)

| Task    | Tên                   | Trạng thái     | Sprint    | Ghi chú |
| ------- | --------------------- | -------------- | --------- | ------- |
| **S9**  | Go Chaos Worker       | ⬜ Not Started | Sprint 5  |         |
| **S10** | Agent Nemesis         | ⬜ Not Started | Sprint 5-6 |        |

### Phase 4 — Hephaestus (Sprint 7-8)

| Task    | Tên                   | Trạng thái     | Sprint    | Ghi chú |
| ------- | --------------------- | -------------- | --------- | ------- |
| **S11** | Agent Hephaestus      | ⬜ Not Started | Sprint 7-8 |        |

### Phase 5 — War Game (Sprint 9-10)

| Task    | Tên                   | Trạng thái     | Sprint     | Ghi chú |
| ------- | --------------------- | -------------- | ---------- | ------- |
| **S12** | War Game & Experiments | ⬜ Not Started | Sprint 9-10 |        |

### Phase 6 — Closing (Sprint 11-12)

| Task    | Tên                   | Trạng thái     | Sprint      | Ghi chú |
| ------- | --------------------- | -------------- | ----------- | ------- |
| **S13** | Report & Defense      | ⬜ Not Started | Sprint 11-12 |        |

## 5. Các vấn đề đã giải quyết

_(Cập nhật trong quá trình phát triển)_

## 6. Key Decisions

| Quyết định                        | Lý do                                                      |
| --------------------------------- | ---------------------------------------------------------- |
| Polyglot: Java + Go               | Java cho orchestration/AI, Go cho high-perf chaos worker   |
| Kafka cho inter-agent comm         | Async, decoupled, fault-tolerant                           |
| Google Online Boutique target app  | Well-documented, 10+ microservices, K8s-native             |
| Scrumban workflow                  | Vừa đủ kỷ luật cho 2 người, linh hoạt hơn Scrum thuần     |
| Task ID sequential (S1→S13)       | Dễ track, không confuse với Sprint number                  |
| GitHub Milestone = Sprint          | 12 milestones, mỗi milestone = 2 tuần                     |

---

_Cập nhật: 05/03/2026_
_Version: 1.1_
