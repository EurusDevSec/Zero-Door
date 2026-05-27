# Tóm tắt Nghiên cứu: ADARMA — Auto-Detection and Auto-Remediation of Microservice Anomalies

> **Paper gốc:** Sarda, K., Namrud, Z., et al. (2023). *"ADARMA: Auto-Detection and Auto-Remediation of Microservice Anomalies by Leveraging Large Language Models."* ACM ISSTA 2023.
>
> **Paper mở rộng (nghiên cứu chính dùng cho tóm tắt này):** Sarda, K., Namrud, Z., Litoiu, M., Shwartz, L., & Watts, I. (2024). *"Leveraging Large Language Models for the Auto-remediation of Microservice Applications: An Experimental Study."* ESEC/FSE 2024, Porto de Galinhas, Brazil. — IBM Research.
>
> **Người thực hiện tóm tắt:** hp8001
> **Ngày:** 08/03/2026

---

## 1. Introduction — Vấn đề trong Microservices

### 1.1. Bối cảnh

Kiến trúc Microservices đang trở thành tiêu chuẩn cho các ứng dụng phân tán hiện đại. Tuy nhiên, sự phức tạp ngày càng tăng khi hệ thống mở rộng lên hàng chục, hàng trăm services đã tạo ra những thách thức nghiêm trọng trong vận hành:

- **Network failures** — Lỗi kết nối giữa các services, timeout, DNS resolution failures
- **Resource constraints** — Thiếu CPU, memory, hoặc disk space trên các node/pod
- **Configuration errors** — Sai cấu hình environment variables, secrets, hoặc service mesh
- **Application bugs** — Lỗi logic ở runtime chỉ xuất hiện khi các services tương tác với nhau

### 1.2. Hạn chế của các phương pháp hiện tại

| Phương pháp | Hạn chế |
|---|---|
| **Manual remediation** | Phụ thuộc vào con người, chậm (đặc biệt ngoài giờ làm việc), không phù hợp khi quản lý hàng trăm microservices |
| **Autonomic computing truyền thống** | Dựa trên rules cứng (if-then), không thích ứng được với các lỗi mới hoặc kết hợp nhiều lỗi phức tạp |
| **Script-based automation** | Cần viết script riêng cho từng loại lỗi, tốn công bảo trì, khó tổng quát hóa |

> **Vấn đề cốt lõi:** Độ phức tạp của các microservice deployments hiện đại đã *vượt quá khả năng* của cả remediation thủ công lẫn các phương pháp autonomic computing hiện có.

---

## 2. Proposed Solution — Cách dùng LLM cho Auto-Detection & Auto-Remediation

### 2.1. Ý tưởng chính

Nhóm tác giả (IBM Research) đề xuất sử dụng **Large Language Models (LLMs)** để tự động sinh và thực thi **Ansible playbooks** — một ngôn ngữ markup được sử dụng rộng rãi trong tự động hóa IT — nhằm khắc phục các sự cố trong môi trường microservices.

### 2.2. Kiến trúc — MAPE-K Loop

Hệ thống hoạt động theo vòng lặp **MAPE-K** (Monitor → Analyze → Plan → Execute → Knowledge):

```
┌──────────────────────────────────────────────────────────────┐
│                       MAPE-K LOOP                            │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ MONITOR  │───▶│ ANALYZE  │───▶│   PLAN   │───▶│EXECUTE │ │
│  │          │    │          │    │          │    │        │ │
│  │ Thu thập │    │ Phát hiện│    │ LLM sinh │    │ Chạy   │ │
│  │ metrics, │    │ anomaly  │    │ Ansible  │    │Ansible │ │
│  │ logs     │    │          │    │ playbook │    │playbook│ │
│  └──────────┘    └──────────┘    └──────────┘    └────────┘ │
│        ▲                                             │      │
│        │           ┌──────────┐                      │      │
│        └───────────│KNOWLEDGE │◀─────────────────────┘      │
│                    │          │                              │
│                    │ Lưu trữ  │                              │
│                    │ kết quả  │                              │
│                    └──────────┘                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.3. Quy trình chi tiết

1. **Fine-tuning LLMs:** Nhóm tác giả xây dựng dataset chuyên biệt tên **KubePlaybook** — bao gồm **130 Ansible playbooks** dành riêng cho Kubernetes remediation. Dataset này được dùng để fine-tune các LLMs pre-trained.

2. **Sinh Ansible playbooks tự động:** Khi phát hiện anomaly, hệ thống mô tả vấn đề bằng natural language prompt → LLM đã fine-tune sẽ sinh ra Ansible playbook chính xác để xử lý.

3. **Thực thi tự động:** Playbook được validate và thực thi tự động, không cần can thiệp thủ công.

4. **Models thử nghiệm:** GPT-4, LLaMa-2-70B — sau khi fine-tune đều cho kết quả vượt trội so với state-of-the-art.

### 2.4. Các loại remediation được hỗ trợ

- Xử lý **network failures** (service connectivity, DNS)
- Giải quyết **resource constraints** (CPU/memory limits, scaling)
- Sửa **configuration errors** (environment variables, secrets)
- Khắc phục **application bugs** (restart, rollback)

---

## 3. Key Metrics — Chỉ số đo lường hiệu quả

### 3.1. Kết quả chính của nghiên cứu

| Chỉ số | Kết quả | Giải thích |
|---|---|---|
| **Functional Correctness** | **95.45%** | Tỷ lệ playbooks được sinh ra chạy đúng chức năng mong đợi |
| **Average Correctness** | **98.86%** | Độ chính xác trung bình của code được sinh (syntax + logic) |
| **So với SOTA** | Vượt trội | Outperform các kỹ thuật state-of-the-art hiện có |

### 3.2. So sánh với MTTD/MTTR của ZERO DOOR

| Khía cạnh | ADARMA (ESEC/FSE 2024) | ZERO DOOR |
|---|---|---|
| **Chỉ số chính** | Functional Correctness (95.45%), Average Correctness (98.86%) | MTTD < 1 phút, MTTR < 3 phút |
| **Đo gì?** | Chất lượng code remediation được LLM sinh ra | Thời gian phát hiện & khắc phục sự cố end-to-end |
| **Cách đo** | Đánh giá playbook output vs. expected output | Prometheus timestamps (attack → detect → heal) |
| **Tương quan** | ADARMA không đo trực tiếp MTTD/MTTR, nhưng auto-remediation chất lượng cao (95%+) sẽ *gián tiếp giảm MTTR* đáng kể | ZERO DOOR đo MTTD/MTTR trực tiếp trong sandbox |

> **Nhận xét:** Cả hai dự án đều hướng tới mục tiêu giảm thời gian phản ứng sự cố, nhưng đo lường bằng các chỉ số khác nhau. ADARMA tập trung vào *chất lượng* remediation code, còn ZERO DOOR tập trung vào *tốc độ* phát hiện và phục hồi end-to-end.

---

## 4. Zero Door Relevance — Bài học cho dự án ZERO DOOR

### Điểm 1: Cách thiết kế Prompt/Template cho AI (Prompt Engineering)

ADARMA sử dụng **natural language prompts** mô tả sự cố → LLM sinh remediation code. Đây là bài học trực tiếp cho **Agent Nemesis** của ZERO DOOR:

- ZERO DOOR đã chọn approach **Hybrid: Template + LLM** (OWASP templates + LLM sinh variations)
- ADARMA chứng minh LLM có thể sinh code IT automation chất lượng cao (>95%) khi được fine-tune đúng cách
- **Áp dụng:** Thiết kế prompt templates chuẩn hóa cho Nemesis, để LLM sinh attack payload variations từ OWASP templates

### Điểm 2: Fine-tuning Dataset cho Domain-Specific Tasks

ADARMA xây dựng **KubePlaybook** — dataset 130 Ansible playbooks chuyên cho Kubernetes. Bài học:

- Không dùng LLM "raw" mà phải fine-tune hoặc cung cấp context chuyên biệt
- **Áp dụng cho ZERO DOOR:** Xây dựng bộ **Attack Template Library** (≥10 OWASP SQLi templates) làm "training data" hoặc few-shot examples cho LLM trong Agent Nemesis
- Tương tự, Agent Hephaestus có thể học cách ADARMA tạo bộ remediation playbooks chuẩn

### Điểm 3: Kiến trúc MAPE-K Loop ↔ Vòng lặp Attack→Detect→Heal

Kiến trúc MAPE-K của ADARMA tương đồng với vòng lặp kín của ZERO DOOR:

| MAPE-K (ADARMA) | ZERO DOOR | Agent phụ trách |
|---|---|---|
| **Monitor** | Thu thập metrics | Agent Gaia (Prometheus scraping) |
| **Analyze** | Phát hiện anomaly | Agent Gaia (AnomalyDetector) |
| **Plan** | Quyết định hành động | Agent Hephaestus (DecisionEngine) |
| **Execute** | Thực thi remediation | Agent Hephaestus (K8s API actions) |
| **Knowledge** | Lưu trữ kết quả | Kafka topics + System logs |

- **Bài học:** ADARMA chứng minh hiệu quả của vòng lặp kín tự động. ZERO DOOR mở rộng thêm thành phần **Red Team AI** (Nemesis) mà ADARMA không có → đóng góp mới của ZERO DOOR.

### Điểm 4: Đánh giá chất lượng AI-generated Code

ADARMA đo **functional correctness** và **average correctness** cho code do LLM sinh ra. ZERO DOOR có thể áp dụng:

- Đánh giá chất lượng **attack payloads** do Nemesis (LLM) sinh: payload có thực sự khai thác được lỗ hổng không?
- Đánh giá chất lượng **healing actions** do Hephaestus thực hiện: action có thực sự khắc phục sự cố không?
- Thêm metrics: **Attack Success Rate** (Nemesis), **Healing Success Rate** (Hephaestus)

---

## Tổng kết

| Khía cạnh | ADARMA | ZERO DOOR |
|---|---|---|
| **Mục tiêu** | Auto-remediation bằng LLM-generated Ansible playbooks | Self-Healing hoàn chỉnh bằng 3 AI Agents |
| **AI Usage** | LLM sinh remediation code | LLM sinh attack payloads + AI detect anomaly |
| **Closed-Loop** | Partial (MAPE-K) | Full (Attack→Detect→Heal) |
| **Red Team** | ❌ Không có | ✅ Agent Nemesis |
| **Open-Source** | ❌ (IBM Research) | ✅ |
| **Đóng góp chính** | Chứng minh LLM sinh IT automation code chính xác >95% | Tích hợp Chaos Engineering + AI + Multi-Agent |

> **Kết luận:** ADARMA là nghiên cứu *gần nhất* với ZERO DOOR, chứng minh rằng LLM có khả năng tự động hóa remediation trong microservices với độ chính xác rất cao. ZERO DOOR mở rộng paradigm này bằng cách thêm **Red Team AI** (Nemesis) và **Multi-Agent Closed-Loop**, tạo nên hệ thống "tự miễn dịch" hoàn chỉnh.

---

*Tài liệu tham khảo:*
- Sarda, K., Namrud, Z., et al. (2023). "ADARMA: Auto-Detection and Auto-Remediation of Microservice Anomalies by Leveraging Large Language Models." ACM ISSTA 2023.
- Sarda, K., Namrud, Z., Litoiu, M., Shwartz, L., & Watts, I. (2024). "Leveraging Large Language Models for the Auto-remediation of Microservice Applications: An Experimental Study." ESEC/FSE 2024.
