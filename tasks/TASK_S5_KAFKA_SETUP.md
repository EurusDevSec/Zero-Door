## 💡 Context

> **Task ID**: S5  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 2 - Architecture & Design  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 2 (Tuần 3-4)  
> **Assignee**: 🔴 Hoàng (Lead)  
> **Blocked by**: S2 (cần K8s cluster)  
> **Blocks**: S8 (Gaia cần Kafka), S4-002 (Gaia Kafka integration)

> Setup Kafka cluster trên Kubernetes + tạo tất cả topics cần thiết cho
> inter-agent communication. Verify produce/consume hoạt động.

---

## 🤖 AI Refined

> **User Story:**

> As a **Backend Developer**, I want to **deploy Apache Kafka on Kubernetes and create all required topics** so that **agents can communicate asynchronously via event-driven messaging.**

**Acceptance Criteria:**

- [ ] Kafka cluster chạy trên K8s (Bitnami Helm chart)
- [ ] 5 topics tạo xong: `attack.commands`, `attack.results`, `monitoring.alerts`, `healing.actions`, `system.logs`
- [ ] Test produce/consume message thành công (CLI hoặc simple Java producer)
- [ ] Kafka retention config: 7 days
- [ ] Kafka UI (Kafdrop hoặc AKHQ) accessible qua port-forward
- [ ] Document: Kafka connection details, topic list, partition strategy

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.2.1 Install Kafka via Helm: `helm install kafka bitnami/kafka -n zero-door`
- [ ] 2.2.2 Wait for Kafka pods Ready (broker + zookeeper)
- [ ] 2.2.3 Create 5 topics:
    ```bash
    kafka-topics.sh --create --topic attack.commands --partitions 3 --replication-factor 1
    kafka-topics.sh --create --topic attack.results --partitions 3 --replication-factor 1
    kafka-topics.sh --create --topic monitoring.alerts --partitions 3 --replication-factor 1
    kafka-topics.sh --create --topic healing.actions --partitions 3 --replication-factor 1
    kafka-topics.sh --create --topic system.logs --partitions 3 --replication-factor 1
    ```
- [ ] 2.2.4 Install Kafka UI (Kafdrop): `helm install kafdrop ...`
- [ ] 2.2.5 Test: produce message → consume message (verify round-trip)
- [ ] 2.2.6 Configure retention, cleanup policies
- [ ] 2.2.7 Document connection string cho Spring Boot `application.yml`

### Branch & PR

- [ ] Branch: `infra/kafka-setup`
- [ ] PR Created
- [ ] `kubectl get pods -n zero-door` shows Kafka running
- [ ] Test produce/consume screenshot attached

---

## 📝 Notes

> **Spring Boot Kafka Config:**
> ```yaml
> # application.yml
> spring:
>   kafka:
>     bootstrap-servers: kafka.zero-door.svc.cluster.local:9092
>     consumer:
>       group-id: ${AGENT_NAME}
>       auto-offset-reset: earliest
>       key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
>       value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
>     producer:
>       key-serializer: org.apache.kafka.common.serialization.StringSerializer
>       value-serializer: org.apache.kafka.common.serialization.StringSerializer
> ```

> **Topic → Agent Mapping:**
>
> | Topic | Producer | Consumer |
> | --- | --- | --- |
> | `attack.commands` | Nemesis | Chaos Worker |
> | `attack.results` | Chaos Worker | Nemesis, Gaia |
> | `monitoring.alerts` | Gaia | Hephaestus, Nemesis |
> | `healing.actions` | Hephaestus | Gaia (verify), Dashboard |
> | `system.logs` | All agents | Dashboard, ELK |

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 5.2 — Communication Protocol
> - Bitnami Kafka Helm: https://github.com/bitnami/charts/tree/main/bitnami/kafka
