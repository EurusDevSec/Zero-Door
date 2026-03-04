# ĐỀ CƯƠNG NGHIÊN CỨU KHOA HỌC: ZERO DOOR

## Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Self-Healing cho hệ thống Microservices

---

## Tóm tắt (Abstract)

Nghiên cứu này đề xuất một hệ thống Self-Healing cho kiến trúc Microservices bằng cách kết hợp **Multi-Agent AI** với **Chaos Engineering**. Hệ thống gồm 3 agents tự trị hoạt động theo vòng lặp **Attack → Detect → Heal**: Agent Nemesis (Red Team) tự động sinh payload tấn công sử dụng GenAI, Agent Gaia (Observer) giám sát và phát hiện bất thường theo thời gian thực, và Agent Hephaestus (Blue Team) thực hiện các hành động phục hồi tự động thông qua Kubernetes API. **Mục tiêu** trong môi trường thử nghiệm (sandbox) là đạt MTTD < 1 phút, MTTR < 3 phút, chứng minh tính khả thi của kiến trúc Self-Healing so với phản ứng thủ công.

**Từ khóa:** Self-Healing Systems, Multi-Agent AI, Chaos Engineering, DevSecOps, Microservices, Kubernetes, Site Reliability Engineering

---

## 1. Thông tin Dự án

| Thông tin               | Chi tiết                                                                                                                |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Tên đề tài**          | Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Self-Healing cho hệ thống Microservices |
| **Mã dự án**            | Zero Door                                                                                                               |
| **Thời gian thực hiện** | 06 tháng (01/2026 - 06/2026)                                                                                            |
| **Ngân sách vận hành**  | 4.900.000 VNĐ                                                                                                           |

### 1.1. Phân bổ Ngân sách

| Hạng mục               | Chi phí (VNĐ) | Ghi chú              |
| ---------------------- | ------------- | -------------------- |
| Cloud Server (VPS/K8s) | 3.000.000     | 6 tháng × 500k/tháng |
| API Token (OpenAI/LLM) | 1.500.000     | ~$60 usage           |
| Domain & SSL           | 400.000       | 1 năm                |
| **Tổng cộng**          | **4.900.000** |                      |

---

## 2. Đặt vấn đề & Mục tiêu nghiên cứu

### 2.1. Bối cảnh nghiên cứu (Problem Statement)

Trong bối cảnh các cuộc tấn công mạng ngày càng tự động hóa và tinh vi, quy trình bảo mật truyền thống **Human-in-the-loop** bộc lộ những hạn chế nghiêm trọng:

- **Độ trễ phản ứng cao:** Thời gian từ phát hiện đến xử lý sự cố trung bình **30-60 phút** với đội ngũ vận hành thủ công. \_(Nguồn: IBM Cost of Data Breach Report 2023 - MTTD trung bình 204 ngày, MTTR 73 ngày cho breach;
- **Thiếu tính nhất quán:** Con người dễ mắc lỗi, đặc biệt trong các tình huống căng thẳng hoặc ngoài giờ làm việc.
- **Khó mở rộng:** Chi phí nhân sự tăng tuyến tính theo quy mô hệ thống.

### 2.1.1. Bài toán Thực tiễn (Real-world Problem)

> **Target Audience:** Các công ty/startup sử dụng Microservices trên Kubernetes với team DevOps nhỏ (1-5 người)

**Case Study tham khảo:**

| Sự kiện                         | Công ty | Thiệt hại        | Root Cause                             |
| ------------------------------- | ------- | ---------------- | -------------------------------------- |
| AWS S3 Outage (2017)            | Amazon  | $150M+           | Human error, slow rollback             |
| Facebook Outage (2021)          | Meta    | $100M/hour       | Configuration change, no auto-rollback |
| Gitlab Database Incident (2017) | Gitlab  | 6 hours downtime | Human error, slow recovery             |

**Bài toán cụ thể:**

- Startup X có 20 microservices trên K8s, team 3 DevOps
- Incident xảy ra lúc 2AM → không ai online → downtime 4 tiếng
- Mỗi giờ downtime = $10,000 revenue loss
- **ZERO DOOR giải quyết:** Tự động detect + heal 24/7, không cần human on-call

**Đối tượng hưởng lợi:**

1. **DevOps/SRE Teams:** Giảm on-call burden, giảm burnout
2. **Startups/SMEs:** Không đủ budget cho 24/7 NOC team
3. **Enterprise:** Bổ sung layer automation cho existing security stack

### 2.2. Câu hỏi nghiên cứu (Research Questions)

1. **RQ1:** Làm thế nào để thiết kế hệ thống Multi-Agent AI có khả năng phát hiện và phản ứng với các cuộc tấn công trong thời gian thực?
2. **RQ2:** Kỹ thuật Chaos Engineering có thể được tích hợp như thế nào để chủ động phát hiện lỗ hổng trước khi bị khai thác?
3. **RQ3:** Hiệu quả của hệ thống Self-Healing tự động so với phương pháp phản ứng thủ công như thế nào?

### 2.3. Mục tiêu nghiên cứu

#### Mục tiêu tổng quát

Xây dựng hệ thống **Phòng thủ chủ động (Proactive Defense)** có khả năng **Self-Healing**: tự tấn công để tìm lỗ hổng và tự vá lỗi trước khi triển khai thực tế.

#### Mục tiêu cụ thể

1. Thiết kế và triển khai kiến trúc Multi-Agent AI với 3 agents chuyên biệt.
2. Tích hợp GenAI để tự động sinh các kịch bản tấn công (Chaos Engineering).
3. Đo lường và chứng minh hiệu quả cải thiện các chỉ số MTTD, MTTR, Uptime.
4. Xây dựng bộ công cụ mã nguồn mở có thể tái sử dụng.

### 2.4. Phạm vi nghiên cứu (Scope)

#### Trong phạm vi (In Scope)

- Ứng dụng Microservices chạy trên Kubernetes
- Các loại tấn công: SQL Injection, DDoS (Layer 7), Resource Exhaustion
- Môi trường thử nghiệm: Sandbox environment (không production)

#### Ngoài phạm vi (Out of Scope)

- Tấn công cấp mạng (Layer 3-4)
- Zero-day vulnerabilities
- Triển khai trên production environment thực tế

### 2.5. Giả thuyết nghiên cứu (Hypothesis)

> **H1:** Hệ thống Multi-Agent AI Self-Healing có thể giảm MTTD xuống < 1 phút và MTTR < 3 phút, cải thiện ít nhất **90%** so với baseline phản ứng thủ công.

---

## 3. Cơ sở lý thuyết & Tổng quan nghiên cứu

### 3.1. Khung lý thuyết

#### 3.1.1. Chaos Engineering

Nguyên lý được Netflix phát triển với mục tiêu "proactively inject failures" để tăng cường khả năng chịu lỗi của hệ thống. Các nguyên tắc cốt lõi:

- Build a Hypothesis around Steady State Behavior
- Vary Real-world Events
- Run Experiments in Production (hoặc môi trường tương đương)
- Automate Experiments to Run Continuously

#### 3.1.2. Multi-Agent Systems (MAS)

Hệ thống đa tác tử là tập hợp các agents tự trị có khả năng:

- **Autonomy:** Hoạt động độc lập không cần can thiệp con người
- **Reactivity:** Phản ứng với thay đổi môi trường
- **Pro-activeness:** Chủ động thực hiện mục tiêu
- **Social ability:** Giao tiếp và phối hợp với agents khác

#### 3.1.3. Site Reliability Engineering (SRE)

Framework của Google tập trung vào các chỉ số:

- **SLI (Service Level Indicators):** Metrics đo lường chất lượng dịch vụ
- **SLO (Service Level Objectives):** Mục tiêu cho các SLIs
- **Error Budget:** Ngân sách lỗi cho phép đổi mới

### 3.2. Các nghiên cứu liên quan

| Nghiên cứu      | Tác giả/Năm    | Đóng góp chính                | Hạn chế                          |
| --------------- | -------------- | ----------------------------- | -------------------------------- |
| Chaos Monkey    | Netflix (2011) | Tiên phong Chaos Engineering  | Chỉ random termination, không AI |
| LitmusChaos     | CNCF (2019)    | Cloud-native chaos platform   | Thiếu self-healing tự động       |
| Chaos Toolkit   | Open Source    | Declarative chaos experiments | Không có AI-driven               |
| AIOps Platforms | Gartner (2023) | AI cho IT Operations          | Chưa tích hợp Red Team AI        |

### 3.3. Khoảng trống nghiên cứu (Research Gap)

> **Lưu ý:** Research Gap được xác định trong bối cảnh **open-source, accessible cho SME/Startups**, không claim "chưa ai làm".

#### 3.3.1. Phân tích các giải pháp hiện có

| Giải pháp                                | Loại                   | Hạn chế                                                   |
| ---------------------------------------- | ---------------------- | --------------------------------------------------------- |
| **Gremlin, Harness Chaos**               | Commercial             | Chi phí cao ($$$), không accessible cho startup/sinh viên |
| **Dynatrace Davis AI, IBM Watson AIOps** | Enterprise AIOps       | License đắt, closed-source, cần team chuyên gia           |
| **LitmusChaos, Chaos Toolkit**           | Open-source Chaos      | Chỉ chaos injection, THIẾU AI-driven và auto-remediation  |
| **Prometheus + Alertmanager**            | Open-source Monitoring | Chỉ alert, THIẾU auto-response                            |

#### 3.3.2. Khoảng trống được xác định

**Trong hệ sinh thái open-source và accessible cho SME:**

1. **Chưa có giải pháp tích hợp hoàn chỉnh:** Các tool hiện tại giải quyết RIÊNG LẺ từng vấn đề (chaos RIÊNG, monitoring RIÊNG, response RIÊNG)
2. **Thiếu AI-driven attack generation trong open-source:** LitmusChaos chỉ có predefined experiments, không AI sinh động
3. **Thiếu Red Team AI nội bộ dạng continuous:** Các pentest tools chạy 1 lần, không liên tục như "hệ miễn dịch"

#### 3.3.3. Định vị đề tài

> **ZERO DOOR không claim "làm cái chưa ai làm"** mà định vị là:
>
> - Một **giải pháp open-source, tích hợp hoàn chỉnh** cho SME/Startups
> - **Proof-of-Concept** cho paradigm "Self-Immune System" trong Microservices
> - **Educational platform** để học về DevSecOps, Chaos Engineering, AI integration

### 3.4. Đóng góp Khoa học (Scientific Contributions)

> **Lưu ý:** Đây là đóng góp trong bối cảnh **nghiên cứu sinh viên** và **hệ sinh thái open-source**, không claim là "đột phá" toàn cầu.

| #      | Đóng góp                              | Loại               | Mô tả chi tiết                                                                                       |
| ------ | ------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| **C1** | **Closed-Loop AI Security Framework** | Kiến trúc tích hợp | Triển khai kiến trúc Multi-Agent với vòng lặp kín Attack→Detect→Heal trong hệ sinh thái open-source  |
| **C2** | **Adversarial Self-Testing Model**    | Áp dụng mới        | Áp dụng mô hình Red Team AI nội bộ cho Microservices - lấy cảm hứng từ "vaccine/hệ miễn dịch"        |
| **C3** | **GenAI-powered Attack Synthesis**    | Tích hợp AI        | Tích hợp LLM (Spring AI) vào Chaos Engineering để sinh payload động, khác với predefined experiments |
| **C4** | **Open-source Self-Healing Platform** | Sản phẩm mới       | Xây dựng platform open-source, accessible cho SME/Startups và mục đích giáo dục                      |

#### So sánh với các hệ thống hiện có

| Tiêu chí               | Chaos Monkey   | LitmusChaos   | Datadog/PagerDuty | **ZERO DOOR**     |
| ---------------------- | -------------- | ------------- | ----------------- | ----------------- |
| Auto Attack Generation | ❌ Random only | ❌ Predefined | ❌ N/A            | ✅ AI-generated   |
| Auto Detection         | ❌             | ⚠️ Basic      | ✅                | ✅                |
| Auto Remediation       | ❌             | ❌            | ⚠️ Runbooks       | ✅ Direct K8s API |
| Closed-Loop            | ❌             | ❌            | ❌                | ✅                |
| Red Team AI            | ❌             | ❌            | ❌                | ✅                |

**Novelty Statement:** _Đề tài không chỉ "ghép nối công cụ" mà đề xuất một PARADIGM mới - hệ thống tự miễn dịch (Self-Immune System) cho Microservices, lấy cảm hứng từ hệ miễn dịch sinh học: liên tục tạo kháng nguyên (Nemesis), nhận diện (Gaia), và tiêu diệt/phục hồi (Hephaestus)._

---

## 4. Phương pháp nghiên cứu (Methodology)

### 4.1. Phương pháp tiếp cận

Nghiên cứu sử dụng phương pháp **Design Science Research (DSR)** với các giai đoạn:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Problem    │───▶│   Design    │───▶│  Develop    │───▶│  Evaluate   │
│Identification│    │  Artifacts  │    │  & Build    │    │  & Test     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 4.2. Thiết kế thực nghiệm

#### 4.2.1. Biến nghiên cứu

| Loại biến     | Tên biến         | Mô tả                                | Đơn vị đo    |
| ------------- | ---------------- | ------------------------------------ | ------------ |
| **Độc lập**   | Attack Type      | Loại tấn công (SQLi, DDoS, Resource) | Categorical  |
| **Độc lập**   | Attack Intensity | Cường độ tấn công                    | requests/sec |
| **Phụ thuộc** | MTTD             | Mean Time To Detect                  | Seconds      |
| **Phụ thuộc** | MTTR             | Mean Time To Recover                 | Seconds      |
| **Phụ thuộc** | Uptime           | Tỷ lệ hoạt động                      | %            |
| **Kiểm soát** | Infrastructure   | Cấu hình K8s cố định                 | -            |

#### 4.2.2. Kịch bản thực nghiệm

| Scenario        | Mô tả                                                 | Kỳ vọng          |
| --------------- | ----------------------------------------------------- | ---------------- |
| **Baseline**    | Hệ thống không có Self-Healing, phản ứng thủ công     | MTTD ~10-30 phút |
| **Test 1**      | SQL Injection attack → Gaia detect → Hephaestus block | MTTD < 1 phút    |
| **Test 2**      | DDoS Layer 7 → Gaia alert → Hephaestus scale          | MTTR < 3 phút    |
| **Test 3**      | Resource Exhaustion → Auto rollback                   | Uptime ≥ 99.9%   |
| **Stress Test** | 3 loại tấn công đồng thời                             | System stable    |

### 4.3. Phương pháp thu thập dữ liệu

- **Quantitative:** Prometheus metrics, logs timestamps
- **Qualitative:** Observation logs, system behavior analysis

### 4.4. Phương pháp phân tích dữ liệu

- **Thống kê mô tả:** Mean, Median, Percentile (P95, P99)
- **So sánh:** Paired t-test (Baseline vs. Self-Healing)
- **Trực quan hóa:** Time-series charts, Heatmaps

### 4.5. Đảm bảo Tính Khách quan (Validity & Objectivity)

> **Vấn đề tiềm ẩn:** "Tự tạo attack, tự phòng thủ" có thể bị bias

**Biện pháp khắc phục:**

| Threat to Validity                              | Biện pháp                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| **Internal Validity** - Attack scenarios biased | Sử dụng **OWASP Testing Guide** làm chuẩn, không tự nghĩ attack         |
| **Construct Validity** - Metrics không đúng     | Dùng **industry-standard metrics** (MTTD/MTTR từ Google SRE)            |
| **External Validity** - Không generalize được   | Test trên **nhiều target apps** (E-commerce, API Gateway, Queue Worker) |
| **Objectivity** - Tự đánh giá                   | **Blind test**: Attack scenarios được shuffle, không biết trước thứ tự  |

### 4.6. External Benchmark & Comparison

**So sánh với Existing Tools:**

| Experiment             | Setup                                       |
| ---------------------- | ------------------------------------------- |
| **Control Group 1**    | Kubernetes HPA alone (built-in autoscaling) |
| **Control Group 2**    | Prometheus + Alertmanager + Manual response |
| **Experimental Group** | ZERO DOOR (Full 3 Agents)                   |

**Metrics thu thập cho mỗi group:** MTTD, MTTR, Uptime, False Positive Rate

_Điều này đảm bảo không chỉ so với "manual" mà còn với các giải pháp automation phổ biến._

### 4.7. Scalability & Production Readiness Analysis

> **Vấn đề:** "Nếu không production được thì giá trị thực tiễn ở đâu?"

**Trả lời:**

1. **Phase hiện tại (Scope):** Proof-of-Concept trong sandbox → chứng minh tính khả thi
2. **Production Readiness Checklist:**

| Yếu tố                       | Status            | Path to Production               |
| ---------------------------- | ----------------- | -------------------------------- |
| Security (Agent credentials) | 🔴 Basic          | Cần Vault integration, RBAC      |
| Scale (1000+ pods)           | 🟡 Untested       | Cần load test, optimize Kafka    |
| Multi-cluster                | 🔴 Single cluster | Cần federation design            |
| Compliance (SOC2, ISO27001)  | 🔴 N/A            | Cần audit logging, approval flow |

3. **Giá trị của Sandbox Research:**
   - Validate architecture trước khi đầu tư production
   - Training environment cho DevOps teams
   - Academic contribution → có thể được industry adopt sau

---

## 5. Kiến trúc Hệ thống & Tech Stack

### 5.1. Tech Stack

| Layer              | Công nghệ                                   | Lý do lựa chọn                              |
| ------------------ | ------------------------------------------- | ------------------------------------------- |
| **Infrastructure** | Docker, Kubernetes (K3s)                    | Industry standard, dễ mở rộng                |
| **Backend Core**   | Java Spring Boot 3.x                        | Mature ecosystem, Spring AI support          |
| **Chaos Worker**   | Go (Golang)                                 | Hiệu năng cao, lightweight, phù hợp CLI/Worker |
| **AI Integration** | Spring AI + OpenAI/Ollama                   | Linh hoạt Cloud/Local LLM                    |
| **Message Broker** | Apache Kafka                                | High throughput, reliable messaging          |
| **Monitoring**     | Prometheus + Grafana                        | De-facto standard observability              |
| **Logging**        | ELK Stack (Elasticsearch, Logstash, Kibana) | Centralized log analysis                     |

> **Lưu ý về Polyglot Architecture:** Dự án sử dụng đa ngôn ngữ theo nguyên tắc "right tool for the right job":
> - **Java Spring Boot**: Orchestration, AI integration, business logic (Agents core)
> - **Go**: Chaos worker, attack execution, high-performance tasks (low latency, low memory footprint)

### 5.2. Kiến trúc 3 Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ZERO DOOR ARCHITECTURE                            │
│                                                                           │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │   NEMESIS    │     │    GAIA      │     │  HEPHAESTUS  │               │
│  │  (Red Team)  │     │  (Observer)  │     │ (Blue Team)  │               │
│  │              │     │              │     │              │               │
│  │ • GenAI      │     │ • Prometheus │     │ • K8s API    │               │
│  │   Payloads   │     │   Scraper    │     │   Client     │               │
│  │ • Go Chaos   │     │ • Anomaly    │     │ • Auto-scale │               │
│  │   Worker     │     │   Detection  │     │ • Block IP   │               │
│  │ • OWASP      │     │ • Log        │     │ • Rollback   │               │
│  │   Templates  │     │   Analysis   │     │ • Restart    │               │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘               │
│         │                    │                    │                       │
│         ▼                    ▼                    ▼                       │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    APACHE KAFKA                             │          │
│  │  Topics:                                                    │          │
│  │  • attack.commands   (Nemesis → Target)                     │          │
│  │  • attack.results    (Nemesis → Gaia)                       │          │
│  │  • monitoring.alerts (Gaia → Hephaestus)                    │          │
│  │  • healing.actions   (Hephaestus → Gaia)                    │          │
│  │  • system.logs       (All → Dashboard)                      │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    TARGET APPLICATION                       │          │
│  │            (Google Online Boutique - 10+ services)          │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                OBSERVABILITY STACK                           │          │
│  │        Prometheus + Grafana + ELK Stack                     │          │
│  └─────────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Agent Communication Protocol

| Kafka Topic           | Producer    | Consumer     | Message Format | Mô tả                              |
| --------------------- | ----------- | ------------ | -------------- | ----------------------------------- |
| `attack.commands`     | Nemesis     | Target App   | JSON           | Payload tấn công được sinh bởi AI  |
| `attack.results`      | Nemesis     | Gaia         | JSON           | Kết quả attack (success/fail)       |
| `monitoring.alerts`   | Gaia        | Hephaestus   | JSON           | Alert khi phát hiện anomaly         |
| `healing.actions`     | Hephaestus  | Gaia         | JSON           | Log hành động phục hồi đã thực hiện |
| `system.logs`         | All Agents  | Dashboard    | JSON           | System-wide logging                |

#### Conflict Resolution

> **Vấn đề:** Nemesis tấn công trong khi Hephaestus đang heal → xung đột?

**Cơ chế giải quyết:**
1. **Priority-based:** Hephaestus (heal) luôn có priority cao hơn Nemesis (attack)
2. **Cooldown Period:** Sau mỗi healing action, Nemesis tạm dừng 30-60 giây
3. **State Machine:** Mỗi Agent có state (IDLE, ACTIVE, COOLDOWN) được publish lên Kafka

### 5.3. Chi tiết từng Agent

#### 5.3.1. Agent Nemesis (Red Team - Attacker)

| Thuộc tính         | Mô tả                                                      |
| ------------------ | ---------------------------------------------------------- |
| **Nhiệm vụ**       | Tự động sinh và thực thi các kịch bản tấn công             |
| **AI Component**   | LLM-powered payload generation                             |
| **Attack Vectors** | SQL Injection, HTTP Flood (DDoS L7), Memory/CPU Exhaustion |
| **Output**         | Attack logs, payload history → Kafka                       |

##### Technical Approach: LLM Payload Generation

> **Vấn đề:** Các LLM thương mại (OpenAI, Claude) có safety guardrails ngăn sinh malicious code.

**Giải pháp đề xuất:**

| Approach                      | Mô tả                                                       | Pros                     | Cons                   |
| ----------------------------- | ----------------------------------------------------------- | ------------------------ | ---------------------- |
| **1. Local LLM (Primary)**    | Sử dụng Ollama với model uncensored (Mistral, CodeLlama)    | Full control, no filters | Chất lượng thấp hơn    |
| **2. Prompt Engineering**     | Frame as "security testing", "penetration testing research" | Có thể dùng cloud LLM    | Không reliable 100%    |
| **3. Hybrid: Template + LLM** | LLM sinh variations từ attack templates có sẵn              | Controlled + Creative    | Cần maintain templates |

**Approach được chọn:** **Hybrid (Option 3)**

- Xây dựng **Attack Template Library** với các pattern chuẩn (OWASP Top 10)
- LLM chỉ sinh **variations/mutations** của template → không vi phạm ethics
- Ví dụ: Template SQLi: `' OR '1'='1` → LLM sinh: `' OR 'a'='a`, `' OR ''='`, `'; DROP TABLE--`

**Attack Coverage Analysis:**

| Attack Type         | OWASP Ranking                  | Justification                     |
| ------------------- | ------------------------------ | --------------------------------- |
| SQL Injection       | #3 (Injection)                 | Classic, dễ detect, good baseline |
| DDoS Layer 7        | N/A                            | Resource-based, test auto-scaling |
| Resource Exhaustion | #5 (Security Misconfiguration) | Test K8s limits, rollback         |

_Lưu ý: Scope 3 attack types là đủ cho proof-of-concept. Có thể mở rộng thêm XSS, SSRF trong future work._

#### 5.3.2. Agent Gaia (Observer - Monitor)

| Thuộc tính            | Mô tả                                     |
| --------------------- | ----------------------------------------- |
| **Nhiệm vụ**          | Giám sát metrics, logs; phát hiện anomaly |
| **Data Sources**      | Prometheus metrics, Application logs      |
| **Detection Methods** | Threshold-based + ML anomaly detection    |
| **Output**            | Alerts, Incident reports → Kafka          |

#### 5.3.3. Agent Hephaestus (Blue Team - Defender)

| Thuộc tính      | Mô tả                                                         |
| --------------- | ------------------------------------------------------------- |
| **Nhiệm vụ**    | Tự động phản ứng và khắc phục sự cố                           |
| **Integration** | Kubernetes API, Network policies                              |
| **Actions**     | Scale pods, Block IPs, Rollback deployments, Restart services |
| **Output**      | Action logs, Recovery reports                                 |

---

## 6. Lộ trình Thực hiện (Timeline)

### 6.1. Tổng quan Timeline

```
2026
Jan            Feb            Mar            Apr            May            Jun
 |──────────────|──────────────|──────────────|──────────────|──────────────|
 │◄── PHASE 1 ──►│             │              │              │              │
 │  Setup &      │             │              │              │              │
 │  Research     │             │              │              │              │
 │◄Sprint1►│◄Sprint2►│        │              │              │              │
 │ Infra   │ Design  │        │              │              │              │
 │         │         │◄──── PHASE 2 ────►│   │              │              │
 │         │         │  Target + Gaia     │   │              │              │
 │         │         │◄Sprint3►│◄Sprint4►│   │              │              │
 │         │         │ Deploy   │ Gaia     │   │              │              │
 │         │         │         │          │◄── PHASE 3 ──►│  │              │
 │         │         │         │          │  Nemesis       │  │              │
 │         │         │         │          │◄Sprint5►│◄S6►│  │              │
 │         │         │         │          │         │     │◄── PHASE 4 ──►│
 │         │         │         │          │         │     │  Hephaestus   │
 │         │         │         │          │         │     │◄S7►│◄S8►│     │
 │         │         │         │          │         │     │    │    │◄P5──►│
 │         │         │         │          │         │     │    │    │WarGame│
 │         │         │         │          │         │     │    │    │◄S9►│◄S10►
 │         │         │◄──────────── PHASE 6 (Song song) ────────────────►│
 │         │         │  Report (hp8001 Ch1-2 từ tháng 3)               │
 │         │         │                                         │◄S11►│◄S12►│
```

> **Nguyên tắc timeline:**
>
> - **12 sprints × 2 tuần** = 24 tuần = 6 tháng
> - **Overlap** Phase 6 (Report) với các phase khác → hp8001 viết Ch1-2 song song từ tháng 3
> - Task files chi tiết: xem thư mục [`tasks/`](../tasks/)

### 6.2. Chi tiết từng Phase

---

## 📦 PHASE 1: Setup & Research (T01-T02/2026)

> **Mục tiêu Phase**: Thiết lập toàn bộ infrastructure + thiết kế kiến trúc chi tiết
> **Thời gian**: 2 tháng (01/2026 - 02/2026)
> **Hoàng**: Infra, K8s, Dev env, Architecture | **hp8001**: Research papers, Grafana, Board setup

### Sprint 1: Foundation (Tuần 1-2)

**Mục tiêu Sprint**: Setup infrastructure nền tảng — GitHub, K8s, dev environment

| Task ID | Task                     | Subtasks                                                           | Assignee         | Target   | Status |
| ------- | ------------------------ | ------------------------------------------------------------------ | ---------------- | -------- | ------ |
| S1-001  | **Infra Setup**          |                                                                    | Hoàng            | Tuần 1   | ⬜     |
|         |                          | 1.1.1 Tạo GitHub repository + branch protection                   | Hoàng            |          | ⬜     |
|         |                          | 1.1.2 Tạo GitHub Projects board (6 cột)                           | 🟡 hp8001     |          | ⬜     |
|         |                          | 1.1.3 Tạo Labels + Milestones (Sprint 1→12)                       | 🟡 hp8001     |          | ⬜     |
|         |                          | 1.1.4 Setup PR Template + CONTRIBUTING.md                         | Hoàng            |          | ⬜     |
| S1-002  | **K8s Cluster Setup**    |                                                                    | Hoàng            | Tuần 1-2 | ⬜     |
|         |                          | 1.2.1 Cài K3s/Minikube + kubectl + Helm                           | Hoàng            |          | ⬜     |
|         |                          | 1.2.2 Tạo 3 namespaces: zero-door, monitoring, target-app         | Hoàng            |          | ⬜     |
|         |                          | 1.2.3 Cài Ingress controller + test pod                           | Hoàng            |          | ⬜     |
|         |                          | 1.2.4 Viết docs/guides/GUIDE_K8S_SETUP.md                         | Hoàng            |          | ⬜     |
| S1-003  | **Dev Environment**      |                                                                    | Hoàng + hp8001 | Tuần 2   | ⬜     |
|         |                          | 1.3.1 Cài Java 17+ + Maven + Spring Boot skeleton                 | Hoàng            |          | ⬜     |
|         |                          | 1.3.2 Cài Go 1.21+ + Go module cho chaos-worker                   | Hoàng            |          | ⬜     |
|         |                          | 1.3.3 Verify: `mvn compile` + `go build` cả 2 pass                | Hoàng            |          | ⬜     |
|         |                          | 1.3.4 Đọc + tóm tắt paper ADARMA (1-2 trang)                     | 🟡 hp8001     |          | ⬜     |
|         |                          | 1.3.5 Viết README.md v1                                           | 🟡 hp8001     |          | ⬜     |

**✅ Milestone 1**: K8s cluster Ready + Dev env OK + GitHub board functional

---

### Sprint 2: Architecture & Design (Tuần 3-4)

**Mục tiêu Sprint**: Thiết kế kiến trúc chi tiết + Setup Kafka & Observability

| Task ID | Task                        | Subtasks                                                             | Assignee         | Target   | Status |
| ------- | --------------------------- | -------------------------------------------------------------------- | ---------------- | -------- | ------ |
| S2-001  | **Architecture Design**     |                                                                      | Hoàng + hp8001 | Tuần 3   | ⬜     |
|         |                             | 2.1.1 Design 5 Kafka topics + JSON message schemas                   | Hoàng            |          | ⬜     |
|         |                             | 2.1.2 Design Agent State Machines (3 agents)                         | Hoàng            |          | ⬜     |
|         |                             | 2.1.3 Design Conflict Resolution protocol                           | Hoàng            |          | ⬜     |
|         |                             | 2.1.4 Vẽ System Architecture diagram (Draw.io)                      | 🟡 hp8001     |          | ⬜     |
|         |                             | 2.1.5 Tóm tắt papers CHESS + AIOps Survey                           | 🟡 hp8001     |          | ⬜     |
| S2-002  | **Kafka Cluster Setup**     |                                                                      | Hoàng            | Tuần 3-4 | ⬜     |
|         |                             | 2.2.1 Install Kafka via Helm (Bitnami)                               | Hoàng            |          | ⬜     |
|         |                             | 2.2.2 Create 5 topics + test produce/consume                        | Hoàng            |          | ⬜     |
|         |                             | 2.2.3 Install Kafka UI (Kafdrop)                                     | Hoàng            |          | ⬜     |
| S2-003  | **Observability Stack**     |                                                                      | Hoàng + hp8001 | Tuần 3-4 | ⬜     |
|         |                             | 2.3.1 Install kube-prometheus-stack (Prometheus + Grafana)           | Hoàng            |          | ⬜     |
|         |                             | 2.3.2 Configure basic alert rules (CPU, Memory, Pod restart)        | Hoàng            |          | ⬜     |
|         |                             | 2.3.3 Customize Grafana dashboard "ZERO DOOR Overview"              | 🟡 hp8001     |          | ⬜     |
|         |                             | 2.3.4 Export dashboard JSON → commit vào infra/grafana/              | 🟡 hp8001     |          | ⬜     |

**✅ Milestone 2**: Architecture documented + Kafka messaging works + Grafana dashboard live

**📊 Phase 1 Deliverables**:

- [ ] K8s cluster ready (3 namespaces, ingress, Helm)
- [ ] Architecture document hoàn chỉnh (Kafka topics, state machines, conflict resolution)
- [ ] Kafka cluster + 5 topics operational
- [ ] Prometheus + Grafana monitoring live
- [ ] Literature review (ADARMA, CHESS, AIOps Survey summaries)

---

## 📦 PHASE 2: Target App + Agent Gaia (T02-T03/2026)

> **Mục tiêu Phase**: Deploy target app + Phát triển Agent Gaia (Observer)
> **Thời gian**: 2 tháng (02/2026 - 03/2026)
> **Hoàng**: Target deploy, Gaia core, Kafka integration | **hp8001**: Test cases, Grafana dashboards, baseline metrics

### Sprint 3: Deploy Target & Gaia Core (Tuần 5-6)

**Mục tiêu Sprint**: Deploy Google Online Boutique + bắt đầu Agent Gaia

| Task ID | Task                     | Subtasks                                                           | Assignee         | Target   | Status |
| ------- | ------------------------ | ------------------------------------------------------------------ | ---------------- | -------- | ------ |
| S3-001  | **Deploy Target App**    |                                                                    | Hoàng            | Tuần 5   | ⬜     |
|         |                          | 3.1.1 Clone + deploy Google Online Boutique lên K8s                | Hoàng            |          | ⬜     |
|         |                          | 3.1.2 Verify 10+ pods Running + shopping flow works                | Hoàng            |          | ⬜     |
|         |                          | 3.1.3 Configure ServiceMonitor cho Prometheus scraping             | Hoàng            |          | ⬜     |
|         |                          | 3.1.4 Run basic load test                                          | Hoàng            |          | ⬜     |
| S3-002  | **Agent Gaia — Core**    |                                                                    | Hoàng + hp8001 | Tuần 5-6 | ⬜     |
|         |                          | 3.2.1 Create Spring Boot module `agent-gaia`                       | Hoàng            |          | ⬜     |
|         |                          | 3.2.2 Implement Prometheus HTTP API client (WebClient)             | Hoàng            |          | ⬜     |
|         |                          | 3.2.3 Implement MetricsCollector (scheduled every 15s)             | Hoàng            |          | ⬜     |
|         |                          | 3.2.4 Implement AnomalyDetector (threshold-based: CPU, Mem, Error) | Hoàng            |          | ⬜     |
|         |                          | 3.2.5 Thu thập baseline metrics (idle state screenshots)           | 🟡 hp8001     |          | ⬜     |

### Sprint 4: Gaia Integration & Testing (Tuần 7-8)

**Mục tiêu Sprint**: Hoàn thiện Gaia — Kafka integration + deploy lên K8s

| Task ID | Task                      | Subtasks                                                          | Assignee         | Target   | Status |
| ------- | ------------------------- | ----------------------------------------------------------------- | ---------------- | -------- | ------ |
| S3-002  | **Agent Gaia — Complete** | _(tiếp tục)_                                                      |                  |          |        |
|         |                           | 3.2.6 Implement Kafka producer → `monitoring.alerts`              | Hoàng            | Tuần 7   | ⬜     |
|         |                           | 3.2.7 Implement State Machine (MONITORING → ALERT → ANALYZING)   | Hoàng            |          | ⬜     |
|         |                           | 3.2.8 Implement REST API: `/api/gaia/status`, `/api/gaia/alerts` | Hoàng            |          | ⬜     |
|         |                           | 3.2.9 Dockerize + K8s Deployment manifest                        | Hoàng            | Tuần 8   | ⬜     |
|         |                           | 3.2.10 Integration test: CPU spike → alert published             | Hoàng            |          | ⬜     |
|         |                           | 3.2.11 Viết test cases document (10 scenarios)                   | 🟡 hp8001     |          | ⬜     |
|         |                           | 3.2.12 Tạo Grafana dashboard "Gaia Alert History"                | 🟡 hp8001     |          | ⬜     |

**✅ Milestone 3**: Target app running + Gaia detects anomalies + alerts via Kafka

**📊 Phase 2 Deliverables**:

- [ ] Google Online Boutique deployed (10+ microservices running)
- [ ] Agent Gaia deployed on K8s, anomaly detection working
- [ ] Kafka `monitoring.alerts` topic receiving messages
- [ ] Gaia Grafana dashboard live
- [ ] Test cases documented

---

## 📦 PHASE 3: Agent Nemesis — Red Team (T03-T04/2026)

> **Mục tiêu Phase**: Phát triển Go Chaos Worker + Agent Nemesis orchestrator
> **Thời gian**: 2 tháng (03/2026 - 04/2026)
> **Hoàng**: Chaos Worker (Go), Nemesis core (Java), LLM integration | **hp8001**: OWASP templates, attack testing, logging

### Sprint 5: Go Chaos Worker + Nemesis Core (Tuần 9-10)

**Mục tiêu Sprint**: Build Go worker + Nemesis Spring Boot module

| Task ID | Task                     | Subtasks                                                          | Assignee         | Target    | Status |
| ------- | ------------------------ | ----------------------------------------------------------------- | ---------------- | --------- | ------ |
| S5-001  | **Go Chaos Worker**      |                                                                   | Hoàng            | Tuần 9    | ⬜     |
|         |                          | 5.1.1 Setup Go project structure (cmd + internal + Dockerfile)    | Hoàng            |           | ⬜     |
|         |                          | 5.1.2 Implement Kafka consumer (attack.commands)                  | Hoàng            |           | ⬜     |
|         |                          | 5.1.3 Implement HTTP Flood executor (goroutines)                  | Hoàng            |           | ⬜     |
|         |                          | 5.1.4 Implement CPU/Memory Stress executors                       | Hoàng            |           | ⬜     |
|         |                          | 5.1.5 Implement Kafka producer → attack.results                   | Hoàng            |           | ⬜     |
|         |                          | 5.1.6 Docker image < 20MB (multi-stage build)                     | Hoàng            |           | ⬜     |
| S5-002  | **Agent Nemesis — Core** |                                                                   | Hoàng + hp8001 | Tuần 9-10 | ⬜     |
|         |                          | 5.2.1 Create Spring Boot module `agent-nemesis`                   | Hoàng            |           | ⬜     |
|         |                          | 5.2.2 Integrate Spring AI (OpenAI/Ollama)                         | Hoàng            |           | ⬜     |
|         |                          | 5.2.3 Implement LLMPayloadGenerator (template → LLM → variations) | Hoàng            |           | ⬜     |
|         |                          | 5.2.4 Implement AttackOrchestrator + Kafka producer               | Hoàng            |           | ⬜     |
|         |                          | 5.2.5 Tạo OWASP SQLi template library (≥10 templates)            | 🟡 hp8001     |           | ⬜     |

### Sprint 6: Nemesis Complete + Attack Testing (Tuần 11-12)

**Mục tiêu Sprint**: Hoàn thiện Nemesis + test từng loại attack riêng lẻ

| Task ID | Task                         | Subtasks                                                       | Assignee         | Target    | Status |
| ------- | ---------------------------- | -------------------------------------------------------------- | ---------------- | --------- | ------ |
| S5-002  | **Agent Nemesis — Complete** | _(tiếp tục)_                                                   |                  |           |        |
|         |                              | 5.2.6 Implement State Machine (IDLE → PLANNING → ATTACKING → COOLDOWN) | Hoàng    | Tuần 11   | ⬜     |
|         |                              | 5.2.7 Implement REST API: start/stop/status                   | Hoàng            |           | ⬜     |
|         |                              | 5.2.8 Dockerize + K8s Deployment manifest                     | Hoàng            | Tuần 12   | ⬜     |
|         |                              | 5.2.9 Integration test: Nemesis → Kafka → Worker → attack     | Hoàng            |           | ⬜     |
|         |                              | 5.2.10 Test từng loại attack riêng lẻ + ghi log              | 🟡 hp8001     |           | ⬜     |
|         |                              | 5.2.11 Record kết quả attack vào experiments/attack-logs/     | 🟡 hp8001     |           | ⬜     |

**✅ Milestone 4**: Nemesis attacks target successfully + Gaia detects all attacks

**📊 Phase 3 Deliverables**:

- [ ] Go Chaos Worker Docker image (< 20MB)
- [ ] Agent Nemesis deployed on K8s
- [ ] Spring AI integrated (LLM sinh payload hoạt động)
- [ ] OWASP attack template library (≥ 10 templates)
- [ ] 3 attack types tested individually (SQLi, DDoS, Resource)
- [ ] Attack logs documented

---

## 📦 PHASE 4: Agent Hephaestus — Blue Team (T04-T05/2026)

> **Mục tiêu Phase**: Phát triển Agent Hephaestus — tự động heal qua K8s API
> **Thời gian**: 1.5 tháng (04/2026 - giữa 05/2026)
> **Hoàng**: Hephaestus core, K8s client, healing logic | **hp8001**: Test healing actions, API docs

### Sprint 7: Hephaestus Core + K8s Client (Tuần 13-14)

**Mục tiêu Sprint**: Build Hephaestus với 4 healing actions

| Task ID | Task                          | Subtasks                                                         | Assignee         | Target    | Status |
| ------- | ----------------------------- | ---------------------------------------------------------------- | ---------------- | --------- | ------ |
| S7-001  | **Agent Hephaestus — Core**   |                                                                  | Hoàng + hp8001 | Tuần 13-14 | ⬜    |
|         |                               | 7.1.1 Create Spring Boot module `agent-hephaestus`               | Hoàng            |           | ⬜     |
|         |                               | 7.1.2 Integrate Kubernetes Java Client (fabric8io)               | Hoàng            |           | ⬜     |
|         |                               | 7.1.3 Implement ScaleAction (increase replicas)                  | Hoàng            |           | ⬜     |
|         |                               | 7.1.4 Implement BlockIPAction (NetworkPolicy)                    | Hoàng            |           | ⬜     |
|         |                               | 7.1.5 Implement RollbackAction + RestartAction                   | Hoàng            |           | ⬜     |
|         |                               | 7.1.6 Implement DecisionEngine (alert → action mapping)          | Hoàng            |           | ⬜     |

### Sprint 8: Hephaestus Complete + Verification (Tuần 15-16)

**Mục tiêu Sprint**: Hoàn thiện verification loop + deploy lên K8s

| Task ID | Task                             | Subtasks                                                       | Assignee         | Target    | Status |
| ------- | -------------------------------- | -------------------------------------------------------------- | ---------------- | --------- | ------ |
| S7-001  | **Agent Hephaestus — Complete**  | _(tiếp tục)_                                                   |                  |           |        |
|         |                                  | 7.1.7 Implement State Machine (STANDBY → HEALING → VERIFYING)  | Hoàng            | Tuần 15   | ⬜     |
|         |                                  | 7.1.8 Implement verification (re-check metrics after healing)  | Hoàng            |           | ⬜     |
|         |                                  | 7.1.9 Kafka producer → `healing.actions` + RBAC manifest       | Hoàng            |           | ⬜     |
|         |                                  | 7.1.10 Dockerize + K8s Deployment                              | Hoàng            | Tuần 16   | ⬜     |
|         |                                  | 7.1.11 Test mỗi healing action riêng lẻ (manual trigger)      | 🟡 hp8001     |           | ⬜     |
|         |                                  | 7.1.12 Viết API docs + test scenarios document                 | 🟡 hp8001     |           | ⬜     |

**✅ Milestone 5**: Full loop works — Nemesis attack → Gaia detect → Hephaestus heal

**📊 Phase 4 Deliverables**:

- [ ] Agent Hephaestus deployed on K8s
- [ ] 4 healing actions working (Scale, Block IP, Rollback, Restart)
- [ ] K8s RBAC configured correctly
- [ ] Verification loop: heal → check metrics → confirm recovery
- [ ] API documentation

---

## 📦 PHASE 5: War Game & Experiments (T05/2026)

> **Mục tiêu Phase**: Tích hợp 3 Agents, chạy thực nghiệm, thu thập MTTD/MTTR metrics
> **Thời gian**: 1 tháng (05/2026)
> **Hoàng**: Integration, experiment scripts, data analysis | **hp8001**: Data collection, video demo, charts

### Sprint 9: Full Integration (Tuần 17-18)

**Mục tiêu Sprint**: 3 agents chạy đồng thời + fix integration bugs

| Task ID | Task                      | Subtasks                                                            | Assignee         | Target    | Status |
| ------- | ------------------------- | ------------------------------------------------------------------- | ---------------- | --------- | ------ |
| S9-001  | **Full Integration**      |                                                                     | Hoàng + hp8001 | Tuần 17-18 | ⬜    |
|         |                           | 9.1.1 Deploy 3 agents + target + Kafka + Prometheus trên K8s       | Hoàng            |           | ⬜     |
|         |                           | 9.1.2 Fix integration bugs (serialization, RBAC, namespace, etc.)  | Hoàng            |           | ⬜     |
|         |                           | 9.1.3 Create experiment script: `scripts/run_experiment.sh`         | Hoàng            |           | ⬜     |
|         |                           | 9.1.4 Tạo data collection spreadsheet template                     | 🟡 hp8001     |           | ⬜     |

### Sprint 10: Experiments & Data Collection (Tuần 19-20)

**Mục tiêu Sprint**: Chạy experiments, đo MTTD/MTTR, so sánh baseline

| Task ID | Task                       | Subtasks                                                          | Assignee         | Target    | Status |
| ------- | -------------------------- | ----------------------------------------------------------------- | ---------------- | --------- | ------ |
| S9-001  | **Experiments** _(tiếp)_   |                                                                   |                  |           |        |
|         |                            | 9.1.5 Run Experiment 1: Baseline (manual response, 5 runs)       | Hoàng            | Tuần 19   | ⬜     |
|         |                            | 9.1.6 Run Experiment 2: Self-Healing (3 attack types × 5 runs)   | Hoàng            |           | ⬜     |
|         |                            | 9.1.7 Run Stress Test: 3 concurrent attacks                      | Hoàng            | Tuần 20   | ⬜     |
|         |                            | 9.1.8 Analyze data: MTTD/MTTR averages, comparison table         | Hoàng            |           | ⬜     |
|         |                            | 9.1.9 Thu thập MTTD/MTTR cho mỗi run (≥20 runs)                  | 🟡 hp8001     |           | ⬜     |
|         |                            | 9.1.10 Record video demo (5-10 phút, Grafana + logs)              | 🟡 hp8001     |           | ⬜     |
|         |                            | 9.1.11 Tạo comparison chart (Baseline vs Self-Healing)            | 🟡 hp8001     |           | ⬜     |

**✅ Milestone 6**: MTTD < 60s (≥70% cases) + MTTR < 180s (≥70% cases) + Video demo recorded

**📊 Phase 5 Deliverables**:

- [ ] Experiment data (≥ 20 runs documented)
- [ ] Comparison table: Baseline vs Self-Healing (MTTD, MTTR, Uptime)
- [ ] Video demo (5-10 phút)
- [ ] Experiment report (`experiments/results/`)
- [ ] Grafana dashboard screenshots during attack + healing

---

## 📦 PHASE 6: Report & Defense (T03-T06/2026, Song song)

> **Mục tiêu Phase**: Viết báo cáo khoa học + chuẩn bị bảo vệ
> **Thời gian**: 4 tháng (bắt đầu song song từ 03/2026, tập trung 05-06/2026)
> **Hoàng**: Chương 3-4-5, Review, Q&A, Demo | **hp8001**: Chương 1-2, Slides, Poster

### Sprint 11: Report Writing (Tuần 21-22)

**Mục tiêu Sprint**: Hoàn thành bản nháp báo cáo

| Task ID | Task                        | Subtasks                                                        | Assignee          | Target    | Status |
| ------- | --------------------------- | --------------------------------------------------------------- | ----------------- | --------- | ------ |
| S11-001 | **Report — Chương 1-2** ✨  |                                                                 | 🟡 hp8001      | Tuần 21   | ⬜     |
|         |                             | 11.1.1 Chương 1: Mở đầu (lý do, mục tiêu, phạm vi, PP)        | 🟡 hp8001      |           | ⬜     |
|         |                             | 11.1.2 Chương 2: Cơ sở lý thuyết (Microservices, Chaos, MAS)   | 🟡 hp8001      |           | ⬜     |
|         |                             | 11.1.3 Gửi Hoàng review                                        | 🟡 hp8001      |           | ⬜     |
| S11-001 | **Report — Chương 3-4-5**   |                                                                 | Hoàng             | Tuần 21-22 | ⬜    |
|         |                             | 11.1.4 Chương 3: Phương pháp và Xây dựng hệ thống              | Hoàng             |           | ⬜     |
|         |                             | 11.1.5 Chương 4: Kết quả thực nghiệm (bảng, biểu đồ)          | Hoàng             |           | ⬜     |
|         |                             | 11.1.6 Chương 5: Kết luận + Hướng phát triển                   | Hoàng             |           | ⬜     |

### Sprint 12: Defense Preparation (Tuần 23-24)

**Mục tiêu Sprint**: Merge report + slides + dry run defense

| Task ID | Task                       | Subtasks                                                        | Assignee          | Target    | Status |
| ------- | -------------------------- | --------------------------------------------------------------- | ----------------- | --------- | ------ |
| S11-001 | **Final Assembly** _(tiếp)_ |                                                                |                   |           |        |
|         |                            | 11.1.7 Merge Ch1-2 + Ch3-4-5 + Format theo mẫu trường          | Hoàng             | Tuần 23   | ⬜     |
|         |                            | 11.1.8 Tạo slides bảo vệ (15-20 slides)                        | 🟡 hp8001      |           | ⬜     |
|         |                            | 11.1.9 Quay video demo (narrated)                               | Hoàng             |           | ⬜     |
|         |                            | 11.1.10 Chuẩn bị Q&A (20 câu hỏi dự đoán + trả lời)            | Hoàng             | Tuần 24   | ⬜     |
|         |                            | 11.1.11 Dry run defense ×2 (tập thuyết trình 15-20 phút)       | Hoàng + hp8001  |           | ⬜     |
|         |                            | 11.1.12 Đóng gói source code (clean, no secrets, README final)  | Hoàng             |           | ⬜     |

**✅ Milestone 7**: Báo cáo hoàn chỉnh + Slides ready + Video demo recorded + Dry run done

**📊 Phase 6 Deliverables**:

- [ ] Báo cáo khoa học hoàn chỉnh (5 chương, format trường)
- [ ] Slides bảo vệ (15-20 slides)
- [ ] Video demo (5-10 phút, narrated)
- [ ] Q&A preparation (20 câu hỏi)
- [ ] Source code đóng gói sạch
- [ ] Dry run ≥ 2 lần

---

### 6.3. Tổng hợp Task Tracking

| Phase | Sprint | Tasks | Tổng Subtasks | Target         |
| ----- | ------ | ----- | ------------- | -------------- |
| 1     | S1-S2  | 6     | 22            | T01-T02/2026   |
| 2     | S3-S4  | 2     | 12            | T02-T03/2026   |
| 3     | S5-S6  | 2     | 11            | T03-T04/2026   |
| 4     | S7-S8  | 1     | 12            | T04-T05/2026   |
| 5     | S9-S10 | 1     | 11            | T05/2026       |
| 6     | S11-S12| 1     | 12            | T03-T06/2026   |
| **Σ** |        | **13**| **80**        | **6 tháng**    |

**Legend:** ⬜ Not Started | 🔄 In Progress | ✅ Completed | ⏸️ Paused | ❌ Cancelled

### 6.4. Milestone Summary

| #  | Milestone                  | Target       | KPI                                    |
| -- | -------------------------- | ------------ | -------------------------------------- |
| M1 | Infra Ready                | Cuối Sprint 2 | K8s + Kafka + Prometheus hoạt động     |
| M2 | Architecture Documented    | Cuối Sprint 2 | Architecture.md hoàn chỉnh             |
| M3 | Gaia Detects Anomalies     | Cuối Sprint 4 | Alert published khi CPU spike          |
| M4 | Nemesis Attacks Successfully | Cuối Sprint 6 | 3 attack types work                  |
| M5 | Full Loop Works            | Cuối Sprint 8 | Attack → Detect → Heal automated      |
| M6 | Experiments Complete       | Cuối Sprint 10 | MTTD < 60s, MTTR < 180s (≥70%)       |
| M7 | Project Complete           | Cuối Sprint 12 | Report + Demo + Defense ready         |

---

## 7. Chỉ số Đánh giá Thành công (KPIs)

### 7.0. Giải thích Tính Khả thi của các con số (Trả lời Hội đồng)

> **Câu hỏi dự đoán:** "Các con số này có khả thi không? Lấy từ đâu?"

#### Tại sao MTTD < 1 phút là KHẢ THI?

| Yếu tố                     | Thời gian       | Giải thích                  |
| -------------------------- | --------------- | --------------------------- |
| Prometheus scrape interval | 15-30 giây      | Mặc định của Prometheus     |
| Threshold alert trigger    | Instant         | Khi vượt ngưỡng, alert ngay |
| Gaia processing            | 5-10 giây       | Xử lý và gửi message        |
| **Tổng**                   | **~30-50 giây** | **< 1 phút ✅**             |

#### Tại sao MTTR < 3 phút là KHẢ THI?

| Hành động               | Thời gian     | Nguồn           |
| ----------------------- | ------------- | --------------- |
| K8s scale pod           | 30-60 giây    | Kubernetes docs |
| K8s rollback deployment | 60-90 giây    | Kubernetes docs |
| NetworkPolicy apply     | ~5 giây       | Instant         |
| **Tổng (worst case)**   | **~2-3 phút** | **✅**          |

#### Uptime 99.9% - CẦN LƯU Ý:

| Mức   | Downtime cho phép | Đánh giá                                                         |
| ----- | ----------------- | ---------------------------------------------------------------- |
| 99.9% | 43 phút/tháng     | **Khó trong production, nhưng KHẢ THI trong sandbox controlled** |
| 99%   | 7.2 giờ/tháng     | Dễ đạt hơn                                                       |

> **Lưu ý quan trọng:** Các con số này là **mục tiêu trong môi trường sandbox** với:
>
> - Attack patterns đã biết (3 loại: SQLi, DDoS L7, Resource)
> - Infrastructure cố định và controlled
> - Không có yếu tố bất ngờ từ production

### 7.1. Bảng KPIs (với điều kiện)

| Chỉ số                     | Baseline (Manual)\* | Mục tiêu (Self-Healing) | Điều kiện                                         |
| -------------------------- | ------------------- | ----------------------- | ------------------------------------------------- |
| **MTTD**                   | 5-15 phút           | **30-60 giây**          | Attack patterns đã được train                     |
| **MTTR**                   | 15-30 phút          | **1-3 phút**            | Healing actions đơn giản (scale, block, rollback) |
| **Uptime** (during attack) | ~90-95%             | **≥ 99%**               | Trong sandbox, attack cường độ controlled         |
| **False Positive Rate**    | N/A                 | **< 10%**               | Threshold được tune                               |
| **Human Intervention**     | 100%                | **< 20%**               | Có edge cases cần human                           |

**(\*) Baseline là giả định cho team nhỏ 1-3 người, response trong giờ làm việc**

### 7.2. Tiêu chí nghiệm thu (Realistic)

**Mức ĐẠT (để nghiệm thu):**

- [ ] MTTD < 60 giây trong **70%** test cases (không phải 90%)
- [ ] MTTR < 180 giây trong **70%** test cases
- [ ] Uptime ≥ **99%** trong War Game (không phải 99.9%)
- [ ] Hệ thống tự phục hồi trong **đa số** trường hợp
- [ ] Demo thành công **ít nhất 2/3** kịch bản tấn công

**Mức TỐT (vượt kỳ vọng):**

- [ ] MTTD < 30 giây trong 80% test cases
- [ ] MTTR < 120 giây trong 80% test cases
- [ ] Uptime ≥ 99.5%
- [ ] Demo thành công 3/3 kịch bản

---

## 8. Phân tích Rủi ro & Kế hoạch Dự phòng

| Rủi ro                              | Xác suất   | Tác động   | Kế hoạch giảm thiểu                        |
| ----------------------------------- | ---------- | ---------- | ------------------------------------------ |
| **API Token hết quota**             | Trung bình | Cao        | Sử dụng Local LLM (Ollama) làm backup      |
| **K8s cluster không ổn định**       | Thấp       | Cao        | Có snapshot, documentation rebuild         |
| **LLM sinh payload không hiệu quả** | Trung bình | Trung bình | Fine-tune prompts, fallback rule-based     |
| **Thời gian không đủ**              | Trung bình | Cao        | Prioritize MVP features, cut scope nếu cần |
| **Chi phí vượt ngân sách**          | Thấp       | Trung bình | Monitor usage, set alerts, use free tier   |

---

## 9. Đạo đức Nghiên cứu (Ethical Considerations)

### 9.1. Nguyên tắc thực hiện

1. **Sandbox Environment Only:** Tất cả thử nghiệm chỉ thực hiện trong môi trường cô lập, KHÔNG tấn công hệ thống thực.
2. **No Real Data:** Sử dụng dữ liệu giả lập, không có thông tin cá nhân thực.
3. **Responsible Disclosure:** Nếu phát hiện lỗ hổng trong các công cụ sử dụng, sẽ báo cáo cho maintainers.
4. **Code of Conduct:** Tuân thủ các quy định về an ninh mạng của pháp luật Việt Nam.

### 9.2. Tuyên bố

> Nghiên cứu này được thực hiện với mục đích học thuật và cải thiện bảo mật hệ thống. Các kỹ thuật tấn công chỉ được áp dụng trong môi trường kiểm soát do nhóm tự xây dựng.

### 9.3. Threat Model

#### 9.3.1. OWASP Top 10 Mapping

| OWASP Category                        | Covered? | Attack Vector trong ZERO DOOR        | Priority |
| ------------------------------------- | -------- | ------------------------------------ | -------- |
| A03:2021 - Injection                  | ✅       | SQL Injection (Nemesis)              | P0       |
| A05:2021 - Security Misconfiguration  | ✅       | Resource Exhaustion (CPU/Memory)     | P0       |
| N/A - Availability                    | ✅       | DDoS Layer 7 (HTTP Flood)            | P0       |
| A01:2021 - Broken Access Control      | ❌       | Out of Scope (v1.0)                  | Future   |
| A07:2021 - XSS                        | ❌       | Out of Scope (v1.0)                  | Future   |
| A10:2021 - SSRF                       | ❌       | Out of Scope (v1.0)                  | Future   |

#### 9.3.2. Attack Flow

```
┌──────────────────────────────────────────────────────────┐
│                  ATTACK SCENARIOS                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Scenario 1: SQL Injection                               │
│  Nemesis → LLM sinh SQLi payload → HTTP Request          │
│  → Target API → Database query → Detect by Gaia          │
│  → Hephaestus block IP + alert                           │
│                                                          │
│  Scenario 2: DDoS Layer 7                                │
│  Nemesis → Go Worker sinh concurrent HTTP requests       │
│  → Target CPU/Memory spike → Prometheus alert            │
│  → Gaia detect anomaly → Hephaestus auto-scale pods      │
│                                                          │
│  Scenario 3: Resource Exhaustion                         │
│  Nemesis → Memory bomb / CPU intensive requests          │
│  → Pod OOMKilled / CrashLoopBackOff                      │
│  → Gaia detect → Hephaestus rollback deployment          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 9.4. Giới hạn Nghiên cứu (Limitations)

> **Quan trọng:** Mọi nghiên cứu đều có giới hạn. Việc nêu rõ giới hạn thể hiện tính trung thực khoa học.

| #   | Giới hạn                                  | Giải thích                                                                   | Hướng khắc phục (Future Work)          |
| --- | ----------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------- |
| L1  | **Chỉ sandbox, chưa production**          | Kết quả trong controlled environment, chưa validate ở production scale       | Pilot deployment với partner           |
| L2  | **3 attack types chỉ là subset**          | OWASP Top 10 có 10 categories, chỉ cover 3                                  | Mở rộng XSS, SSRF, CSRF               |
| L3  | **Single Kubernetes cluster**             | Chưa test multi-cluster, federation                                          | Multi-cluster support                  |
| L4  | **LLM dependency**                        | Chất lượng payload phụ thuộc LLM, có thể không stable                        | Fine-tuned domain-specific model       |
| L5  | **Thiếu long-term evaluation**            | 6 tháng chưa đủ đánh giá reliability dài hạn                                 | Extended evaluation period             |
| L6  | **Benchmark limited**                     | So sánh chủ yếu với manual, chưa so với commercial tools (Gremlin, Harness)  | Partnership với vendors                |
| L7  | **Chỉ hỗ trợ Prometheus metrics**         | App cần expose Prometheus endpoint, không hỗ trợ Datadog/CloudWatch          | Adapter pattern cho multi-source       |

---

## 10. Sản phẩm Bàn giao (Deliverables)

### 10.0. Sản phẩm Cụ thể là gì? (Trả lời Hội đồng)

> **Câu hỏi:** "Sản phẩm cụ thể của nhóm em là gì? Web, App, hay cái gì?"

**Trả lời:**

| Không phải                     | Là                                                     |
| ------------------------------ | ------------------------------------------------------ |
| ❌ Web app cho người dùng cuối | ✅ **Backend Platform/Framework** cho DevOps Engineers |
| ❌ Mobile app                  | ✅ **3 Microservices** chạy trên Kubernetes            |
| ❌ Desktop software            | ✅ **Dashboard Monitoring** (Grafana-based)            |

#### Sản phẩm gồm 4 thành phần chính:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SẢN PHẨM ZERO DOOR                         │
├────────────────┬────────────────┬───────────────┬───────────────┤
│   COMPONENT 1   │   COMPONENT 2    │  COMPONENT 3  │  COMPONENT 4  │
│                 │                  │               │               │
│  3 JAVA SPRING  │   HELM CHARTS    │   GRAFANA     │   TARGET      │
│  MICROSERVICES  │   + K8s YAML     │   DASHBOARD   │   DEMO APP    │
│                 │                  │               │               │
│  • Nemesis      │  • Deploy 1-click │  • Real-time   │  • E-commerce  │
│  • Gaia         │  • Configurable  │    metrics    │    demo       │
│  • Hephaestus   │  • Scalable      │  • War status  │  • Vulnerable  │
└────────────────┴────────────────┴───────────────┴───────────────┘
```

#### Cách sử dụng sản phẩm:

| Bước | Người dùng làm                  | Kết quả                                          |
| ---- | ------------------------------- | ------------------------------------------------ |
| 1    | `helm install zero-door ./helm` | Deploy toàn bộ hệ thống lên K8s                  |
| 2    | Mở Grafana Dashboard            | Xem trạng thái "chiến tranh AI" real-time        |
| 3    | Hệ thống tự hoạt động           | Nemesis tấn công → Gaia detect → Hephaestus heal |
| 4    | Xem logs & metrics              | Phân tích MTTD, MTTR, Uptime                     |

#### Ai sử dụng sản phẩm?

| Đối tượng                 | Mục đích sử dụng                                         |
| ------------------------- | -------------------------------------------------------- |
| **DevOps/SRE Engineers**  | Test khả năng chịu lỗi của hệ thống trước khi production |
| **Security Teams**        | Continuous security testing trong CI/CD                  |
| **Sinh viên/Researchers** | Học về Chaos Engineering, AI, Kubernetes                 |
| **Startups**              | Self-healing platform không cần 24/7 NOC team            |

### 10.1. Sản phẩm bàn giao chi tiết

| #   | Sản phẩm             | Mô tả                                   | Định dạng          |
| --- | -------------------- | --------------------------------------- | ------------------ |
| 1   | **Source Code**      | Full source code 3 Agents + Target App  | GitHub Repository  |
| 2   | **K8s Manifests**    | Helm Charts / Kubernetes YAML files     | YAML files         |
| 3   | **Documentation**    | README, API docs, Architecture diagrams | Markdown + Draw.io |
| 4   | **Video Demo**       | Recording kịch bản Attack-Detect-Heal   | MP4 (5-10 phút)    |
| 5   | **Báo cáo Khoa học** | Báo cáo toàn văn theo format yêu cầu    | PDF/Word           |
| 6   | **Presentation**     | Slides bảo vệ                           | PowerPoint/PDF     |

### 10.2. Khả năng Tái sử dụng (Reusability) - Trả lời Hội đồng

> **Câu hỏi:** "Nếu một team DevOps muốn dùng project này cho dự án của họ thì có được không? Hay chỉ chạy được với demo app của nhóm?"

#### ✅ TRẢ LỜI: CÓ THỂ TÁI SỬ DỤNG

ZERO DOOR được thiết kế theo kiến trúc **pluggable** và **configurable**, cho phép team DevOps khác áp dụng vào dự án của họ.

#### Cách một team DevOps sử dụng ZERO DOOR cho project của họ:

```
┌─────────────────────────────────────────────────────────────────┐
│              HƯỚNG DẪN ÁP DỤNG CHO DỰ ÁN KHÁC                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BƯỚC 1: Thay thế Target App                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  # values.yaml                                          │    │
│  │  targetApp:                                             │    │
│  │    name: "your-app"           # Tên app của họ          │    │
│  │    namespace: "your-namespace"                          │    │
│  │    metricsEndpoint: "/actuator/prometheus"              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  BƯỚC 2: Cấu hình Thresholds theo app của họ                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  # gaia-config.yaml                                     │    │
│  │  thresholds:                                            │    │
│  │    cpu: 80%              # Ngưỡng CPU                   │    │
│  │    memory: 85%           # Ngưỡng Memory                │    │
│  │    errorRate: 5%         # Ngưỡng Error Rate            │    │
│  │    responseTime: 2000ms  # Ngưỡng Response Time         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  BƯỚC 3: Chọn Healing Actions phù hợp                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  # hephaestus-config.yaml                               │    │
│  │  healingActions:                                        │    │
│  │    - type: SCALE          # Scale pods                  │    │
│  │      enabled: true                                      │    │
│  │    - type: RESTART        # Restart pods                │    │
│  │      enabled: true                                      │    │
│  │    - type: ROLLBACK       # Rollback deployment         │    │
│  │      enabled: false       # Tắt nếu không cần           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  BƯỚC 4: Deploy                                                 │
│  $ helm install zero-door ./helm -f your-values.yaml            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Các yếu tố Pluggable/Configurable:

| Yếu tố              | Mặc định               | Có thể thay đổi                       | Cách thay đổi            |
| ------------------- | ---------------------- | ------------------------------------- | ------------------------ |
| **Target App**      | E-commerce demo        | ✅ Bất kỳ app nào có metrics endpoint | `values.yaml`            |
| **Thresholds**      | CPU 80%, Memory 85%    | ✅ Tuỳ chỉnh theo app                 | `gaia-config.yaml`       |
| **Attack Types**    | SQLi, DDoS, Resource   | ✅ Thêm/bớt patterns                  | `nemesis-config.yaml`    |
| **Healing Actions** | Scale, Block, Rollback | ✅ Enable/disable từng action         | `hephaestus-config.yaml` |
| **LLM Provider**    | OpenAI                 | ✅ Ollama, Claude, etc.               | `application.yaml`       |
| **Monitoring**      | Prometheus + Grafana   | ✅ Datadog, New Relic (cần adapter)   | Custom integration       |

#### Yêu cầu tối thiểu để áp dụng:

| Yêu cầu                | Mô tả                                                       |
| ---------------------- | ----------------------------------------------------------- |
| **Kubernetes cluster** | K3s, Minikube, EKS, GKE, AKS đều được                       |
| **Prometheus metrics** | App phải expose metrics (Spring Actuator, Micrometer, etc.) |
| **Helm 3.x**           | Để deploy ZERO DOOR                                         |
| **App containerized**  | App phải chạy trên K8s (có Deployment/Service)              |

#### Limitations (Giới hạn hiện tại):

| Giới hạn          | Lý do                  | Hướng mở rộng (Future Work)     |
| ----------------- | ---------------------- | ------------------------------- |
| Chỉ hỗ trợ K8s    | Focus vào cloud-native | Thêm Docker Swarm, bare-metal   |
| 3 attack types    | Scope sinh viên        | Thêm XSS, SSRF, CSRF            |
| Prometheus only   | Phổ biến nhất          | Adapter cho Datadog, CloudWatch |
| Java Spring focus | Team expertise         | Thêm support Node.js, Python    |

#### Ví dụ Use Case thực tế:

> **Startup Y** có 10 microservices chạy trên GKE, muốn dùng ZERO DOOR:
>
> 1. Clone repo ZERO DOOR
> 2. Sửa `values.yaml`: trỏ đến namespace của họ
> 3. Sửa thresholds phù hợp với SLO của họ
> 4. `helm install` → Done!
> 5. ZERO DOOR sẽ tự tấn công và bảo vệ các services của họ

### 10.2. Cấu trúc Repository

```
zero_door/
├── docs/                    # Documentation
│   ├── plan.md              # This file
│   ├── architecture.md      # System architecture
│   └── api/                 # API documentation
├── src/
│   ├── target-app/          # E-commerce demo app
│   ├── agent-nemesis/       # Red Team agent
│   ├── agent-gaia/          # Observer agent
│   └── agent-hephaestus/    # Blue Team agent
├── infra/
│   ├── kubernetes/          # K8s manifests
│   ├── helm/                # Helm charts
│   └── docker/              # Dockerfiles
├── experiments/             # Experiment results & data
├── scripts/                 # Automation scripts
└── README.md
```

---

## 11. Tài liệu Tham khảo (References)

> Xem thêm chi tiết tại [docs/references.md](references.md)

### Academic Papers

1. Basiri, A., et al. (2016). "Chaos Engineering." _IEEE Software_, 33(3), 35-41.
2. Wooldridge, M. (2009). _An Introduction to MultiAgent Systems_. John Wiley & Sons.
3. Soldani, J., et al. (2022). "Automated Anomaly Detection and Root Cause Analysis for Microservices." _IEEE Transactions on Services Computing_.
4. Chen, P., et al. (2021). "AIOps: Real-World Challenges and Research Innovations." _IEEE ICSE-SEIP_.
5. Sarda, K., Namrud, Z., et al. (2023). "ADARMA: Auto-Detection and Auto-Remediation of Microservice Anomalies by Leveraging LLMs." _ACM ISSTA_. [ACM](https://dl.acm.org/doi/abs/10.5555/3615924.3615949)
6. Malik, S., Naqvi, M.A., Moonen, L. (2023). "CHESS: A Framework for Evaluation of Self-Adaptive Systems Based on Chaos Engineering." _IEEE SEAMS_. [IEEE](https://ieeexplore.ieee.org/abstract/document/10174151/)
7. Zhang, L., Jia, T., et al. (2024). "A Survey of AIOps for Failure Management in the Era of Large Language Models." _arXiv_. [arXiv](https://arxiv.org/abs/2406.11213)
8. Naqvi, M.A., Malik, S., Astekin, M. (2022). "On Evaluating Self-Adaptive and Self-Healing Systems Using Chaos Engineering." _IEEE International Conference_. [IEEE](https://ieeexplore.ieee.org/abstract/document/9935013/)

### Industry Reports (Baseline Data Sources)

9. IBM Security. (2023). "Cost of a Data Breach Report 2023." IBM. _[MTTD: 204 days, MTTR: 73 days]_
10. Splunk. (2023). "State of Security 2023." _[55% organizations: >1 hour incident response]_
11. Gartner. (2023). "Market Guide for AIOps Platforms."
12. OWASP Foundation. (2021). "OWASP Top 10:2021." https://owasp.org/Top10/

### Books

13. Google SRE Team. (2016). _Site Reliability Engineering: How Google Runs Production Systems_. O'Reilly Media.
14. Rosenthal, C., Jones, N. (2020). _Chaos Engineering: System Resiliency in Practice_. O'Reilly Media.
15. Netflix Technology Blog. (2011). "The Netflix Simian Army." Netflix.

### Technical Documentation

16. CNCF. (2023). "LitmusChaos Documentation." https://litmuschaos.io/
17. Spring AI Documentation. (2024). https://docs.spring.io/spring-ai/reference/
18. Kubernetes Official Documentation. (2024). https://kubernetes.io/docs/
19. Prometheus Documentation. (2024). https://prometheus.io/docs/
20. OWASP Testing Guide v4.2. (2023). https://owasp.org/www-project-web-security-testing-guide/
21. Go Programming Language. (2024). https://go.dev/doc/

---

## 12. Phụ lục

### Phụ lục A: Bảng thuật ngữ (Glossary)

| Thuật ngữ              | Định nghĩa                                                              |
| ---------------------- | ----------------------------------------------------------------------- |
| **MTTD**               | Mean Time To Detect - Thời gian trung bình để phát hiện sự cố           |
| **MTTR**               | Mean Time To Recover - Thời gian trung bình để khắc phục sự cố          |
| **SRE**                | Site Reliability Engineering - Kỹ thuật đảm bảo độ tin cậy hệ thống     |
| **Chaos Engineering**  | Kỹ thuật chủ động gây lỗi để tìm điểm yếu hệ thống                      |
| **Multi-Agent System** | Hệ thống gồm nhiều agents tự trị phối hợp hoạt động                     |
| **Self-Healing**       | Khả năng tự phát hiện và khắc phục lỗi mà không cần can thiệp con người |

### Phụ lục B: Checklist chuẩn bị

- [ ] Setup GitHub repository
- [ ] Đăng ký Cloud account (GCP/AWS/DigitalOcean)
- [ ] Tạo OpenAI API key
- [ ] Cài đặt development environment (Java 17+, Go 1.21+, Docker, kubectl)
- [ ] Review tài liệu Chaos Engineering
- [ ] Review Spring AI documentation
- [ ] Setup Go development environment (chaos-worker)
- [ ] Đọc kỹ ADARMA paper (closest related work)

---

_Cập nhật lần cuối: 04/03/2026_  
_Version: 3.0_
