# SLIDES THUYẾT TRÌNH: ZERO DOOR

## Hướng dẫn trình bày ngắn gọn (5-7 phút) + Q&A

---

# 📋 TỔNG QUAN SLIDES

| Slide    | Nội dung                  | Thời gian   |
| -------- | ------------------------- | ----------- |
| 1        | Tiêu đề + Nhóm            | 15 giây     |
| 2        | Vấn đề & Bài toán thực tế | 1 phút      |
| 3        | Giải pháp ZERO DOOR       | 1.5 phút    |
| 4        | Kiến trúc hệ thống        | 1.5 phút    |
| 5        | Demo / Kết quả            | 1.5 phút    |
| 6        | Kết luận + Q&A            | 30 giây     |
| **Tổng** |                           | **~6 phút** |

---

# SLIDE 1: TIÊU ĐỀ (15 giây)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                         ZERO DOOR                               │
│                                                                 │
│   Ứng dụng kiến trúc Multi-Agent AI và Chaos Engineering        │
│   xây dựng cơ chế Self-Healing cho hệ thống Microservices       │
│                                                                 │
│   ─────────────────────────────────────────────────────         │
│                                                                 │
│   Nhóm: [Tên nhóm]                                              │
│   GVHD: [Tên GVHD]                                              │
│   Thời gian: 01/2026 - 06/2026                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Nói:** "Kính chào thầy/cô và hội đồng, nhóm em xin trình bày đề tài..."

---

# SLIDE 2: VẤN ĐỀ (1 phút) ⭐ QUAN TRỌNG

## 📌 Key message: "Tại sao cần nghiên cứu này?"

```
┌─────────────────────────────────────────────────────────────────┐
│                      VẤN ĐỀ THỰC TẾ                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   😱 INCIDENT LÚC 2AM - KHÔNG AI ONLINE                         │
│                                                                 │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│   │   Attack    │────▶│   4 tiếng   │────▶│  $40,000    │       │
│   │   xảy ra    │     │  downtime   │     │   mất      │       │
│   └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
│   📊 THỐNG KÊ:                                                  │
│   • 55% tổ chức mất >1 giờ để respond (Splunk 2023)             │
│   • Facebook Outage 2021: $100M/hour                            │
│   • AWS S3 Outage 2017: $150M+ thiệt hại                        │
│                                                                 │
│   ❓ VẤN ĐỀ: Human-in-the-loop = CHẬM + KHÔNG 24/7              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Nói:**

- "Hình dung: Incident xảy ra lúc 2AM, team DevOps đang ngủ, 4 tiếng sau mới có người xử lý"
- "Theo IBM và Splunk, 55% tổ chức mất hơn 1 giờ để respond"
- "Vấn đề cốt lõi: Con người không thể online 24/7"

---

# SLIDE 3: GIẢI PHÁP (1.5 phút) ⭐ QUAN TRỌNG NHẤT

## 📌 Key message: "ZERO DOOR giải quyết như thế nào?"

```
┌─────────────────────────────────────────────────────────────────┐
│                    GIẢI PHÁP: ZERO DOOR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎯 Ý TƯỞNG: Hệ thống TỰ MIỄN DỊCH cho Microservices           │
│                                                                 │
│   Giống cơ thể người:                                           │
│   • Tạo kháng nguyên (tự tấn công) → Phát hiện → Tiêu diệt      │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐       │
│   │                                                     │       │
│   │    NEMESIS ────▶ GAIA ────▶ HEPHAESTUS             │       │
│   │   (Tấn công)   (Phát hiện)  (Phục hồi)             │       │
│   │       │                          │                  │       │
│   │       └──────────────────────────┘                  │       │
│   │              VÒNG LẶP KÍN 24/7                      │       │
│   │                                                     │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                 │
│   ✅ MỤC TIÊU (trong sandbox):                                  │
│   • MTTD: ~15 phút → 30-60 GIÂY                                 │
│   • MTTR: ~30 phút → 1-3 PHÚT                                   │
│   • Uptime: ≥ 99% trong môi trường thử nghiệm                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Nói:**

- "ZERO DOOR hoạt động như hệ miễn dịch của cơ thể người"
- "3 agents: Nemesis tấn công, Gaia phát hiện, Hephaestus phục hồi"
- "Vòng lặp kín, chạy 24/7 không cần người"
- "Kỳ vọng giảm MTTD từ 30 phút xuống dưới 1 phút"

---

# SLIDE 4: KIẾN TRÚC (1.5 phút)

## 📌 Key message: "Hệ thống được xây dựng như thế nào?"

```
┌─────────────────────────────────────────────────────────────────┐
│                    KIẾN TRÚC HỆ THỐNG                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ NEMESIS  │───▶│   GAIA   │───▶│HEPHAESTUS│───▶│  TARGET  │  │
│  │ Red Team │    │ Observer │    │Blue Team │    │   APP    │  │
│  │   🔴     │    │    👁    │    │    🛡    │    │    🎯    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │               │               │               │        │
│       │               │               │               │        │
│       └───────────────┴───────────────┴───────────────┘        │
│                           │                                     │
│                     ┌─────▼─────┐                               │
│                     │   KAFKA   │                               │
│                     │  Message  │                               │
│                     └───────────┘                               │
│                                                                 │
│  📦 TECH STACK:                                                 │
│  • Backend: Java Spring Boot + Spring AI                        │
│  • Infra: Kubernetes (K3s) + Docker                             │
│  • AI: OpenAI / Ollama (Local LLM)                              │
│  • Monitor: Prometheus + Grafana                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Nói:**

- "3 microservices giao tiếp qua Kafka"
- "Nemesis dùng AI sinh payload tấn công động"
- "Gaia giám sát metrics từ Prometheus"
- "Hephaestus tương tác trực tiếp K8s API để scale, block, rollback"

---

# SLIDE 5: DEMO / KẾT QUẢ (1.5 phút)

## 📌 Có 2 option tuỳ thời điểm bảo vệ:

### Option A: Nếu có Demo video

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEMO                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [CHÈN VIDEO HOẶC GIF DEMO Ở ĐÂY]                              │
│                                                                 │
│   Kịch bản demo:                                                │
│   1. Nemesis tấn công SQL Injection                             │
│   2. Gaia phát hiện trong 30 giây                               │
│   3. Hephaestus block IP tự động                                │
│   4. Uptime vẫn giữ 99.9%                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Option B: Nếu chưa có Demo (giữa kỳ)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIẾN ĐỘ THỰC HIỆN                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ✅ Đã hoàn thành:                                             │
│   • Setup K8s cluster                                           │
│   • Phát triển Target App                                       │
│   • Agent Gaia (Monitoring)                                     │
│                                                                 │
│   🔄 Đang thực hiện:                                            │
│   • Agent Nemesis (AI attack generation)                        │
│                                                                 │
│   📅 Sắp tới:                                                   │
│   • Agent Hephaestus                                            │
│   • Integration & War Game                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# SLIDE 6: KẾT LUẬN (30 giây)

```
┌─────────────────────────────────────────────────────────────────┐
│                        KẾT LUẬN                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎯 ZERO DOOR là:                                              │
│   • Platform Self-Healing open-source cho Microservices         │
│   • Kết hợp Multi-Agent AI + Chaos Engineering                  │
│   • Phù hợp cho SME/Startups với team DevOps nhỏ                │
│                                                                 │
│   📦 SẢN PHẨM BÀN GIAO:                                         │
│   • 3 Microservices (Java Spring Boot)                          │
│   • Helm Charts (deploy 1-click)                                │
│   • Dashboard Grafana                                           │
│   • Báo cáo + Video Demo                                        │
│                                                                 │
│   ─────────────────────────────────────────────────────         │
│                                                                 │
│              🙏 XIN CẢM ƠN THẦY/CÔ VÀ HỘI ĐỒNG                  │
│                   KÍNH MỜI HỘI ĐỒNG ĐẶT CÂU HỎI                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# 🔥 CÂU HỎI PHẢN BIỆN DỰ ĐOÁN + CÂU TRẢ LỜI

## ❓ Q0: "Con số MTTD < 1 phút, MTTR < 3 phút có khả thi không? Bốc phét không?"

**⭐ CÂU HỎI QUAN TRỌNG NHẤT - CHUẨN BỊ KỸ:**

**Trả lời:**

> "Thưa thầy/cô, các con số này **hoàn toàn khả thi về mặt kỹ thuật**, em xin giải thích:
>
> **MTTD < 1 phút - Tại sao khả thi:**
>
> - Prometheus scrape metrics mỗi 15-30 giây (cấu hình mặc định)
> - Khi vượt threshold, alert trigger ngay lập tức
> - Gaia nhận và xử lý trong 5-10 giây
> - **Tổng: ~30-50 giây**, dưới 1 phút là hợp lý
>
> **MTTR < 3 phút - Tại sao khả thi:**
>
> - Kubernetes scale pod mất 30-60 giây (theo docs chính thức)
> - Rollback deployment mất 60-90 giây
> - Block IP qua NetworkPolicy gần như instant
> - **Tổng worst case: ~2-3 phút**
>
> **Điều kiện quan trọng:**
>
> - Các con số này áp dụng trong **môi trường sandbox controlled**
> - Attack patterns là 3 loại đã biết, không phải zero-day
> - Healing actions là đơn giản (scale, block, rollback)
>
> Em đã điều chỉnh tiêu chí nghiệm thu xuống **70% test cases đạt**, không phải 100%, để realistic hơn."

---

## ❓ Q1: "Đề tài có gì MỚI?"

**Trả lời:**

> "Thưa thầy/cô, trong hệ sinh thái **open-source**, chưa có giải pháp nào **tích hợp hoàn chỉnh** 3 yếu tố: AI-driven attack, real-time detection, và auto-remediation trong một vòng lặp kín.
>
> Các tool như LitmusChaos chỉ làm chaos, Prometheus chỉ monitoring. ZERO DOOR kết hợp cả 3, tạo thành 'hệ miễn dịch' cho Microservices.
>
> Đóng góp chính: Platform open-source, accessible cho SME/Startups và mục đích giáo dục."

---

## ❓ Q2: "Tính THỰC TIỄN? Ai sẽ dùng?"

**Trả lời:**

> "Thưa thầy/cô, đối tượng chính là:
>
> 1. **Startups/SMEs** với team DevOps nhỏ, không đủ budget cho 24/7 NOC
> 2. **DevOps Engineers** cần test khả năng chịu lỗi trước khi production
> 3. **Sinh viên/Researchers** học về Chaos Engineering và AI integration
>
> Bài toán thực tế: Incident lúc 2AM, không ai online → với ZERO DOOR, hệ thống tự xử lý."

---

## ❓ Q3: "Sản phẩm cụ thể là gì? Web hay App?"

**Trả lời:**

> "Thưa thầy/cô, sản phẩm là một **Backend Platform** gồm:
>
> - **3 Microservices** Java Spring Boot chạy trên Kubernetes
> - **Helm Charts** để deploy 1-click
> - **Dashboard Grafana** để xem trạng thái real-time
> - **Target Demo App** để test
>
> Người dùng là DevOps Engineers, không phải end-user thông thường."

---

## ❓ Q4: "Chỉ test trong Sandbox, vậy giá trị production ở đâu?"

**Trả lời:**

> "Thưa thầy/cô, đây là Proof-of-Concept để validate kiến trúc. Giá trị:
>
> 1. Chứng minh tính khả thi trước khi đầu tư production
> 2. Làm training environment cho DevOps teams
> 3. Đóng góp academic có thể được industry adopt sau
>
> Trong đề cương, nhóm em đã có Production Readiness Checklist với path rõ ràng."

---

## ❓ Q5: "Team DevOps khác muốn dùng cho dự án của họ thì có được không?"

**⭐ CÂU HỎI RẤT THỰC TẾ:**

**Trả lời:**

> "Thưa thầy/cô, **hoàn toàn được ạ**. ZERO DOOR được thiết kế **pluggable và configurable**:
>
> **Cách team DevOps khác sử dụng:**
>
> 1. **Thay Target App:** Chỉ cần sửa `values.yaml`, trỏ đến app của họ
> 2. **Cấu hình Thresholds:** Tuỳ chỉnh CPU, Memory, Error Rate phù hợp SLO của họ
> 3. **Chọn Healing Actions:** Enable/disable Scale, Rollback, Block tuỳ nhu cầu
> 4. **Deploy:** `helm install zero-door ./helm -f their-values.yaml`
>
> **Yêu cầu tối thiểu:**
>
> - App chạy trên Kubernetes
> - Có Prometheus metrics endpoint (Spring Actuator, Micrometer, etc.)
>
> **Ví dụ:** Startup có 10 microservices trên GKE, chỉ cần clone repo, sửa config, helm install là xong.
>
> **Giới hạn hiện tại:** Chỉ hỗ trợ K8s và Prometheus, 3 attack types. Có thể mở rộng trong future work."

---

## ❓ Q5: "LLM có guardrails ngăn sinh malicious code, xử lý thế nào?"

**Trả lời:**

> "Thưa thầy/cô, nhóm em dùng **Hybrid approach**:
>
> 1. Xây dựng Attack Template Library từ OWASP
> 2. LLM chỉ sinh **variations** của template, không sinh từ đầu
> 3. Backup bằng Local LLM (Ollama) không có filters
>
> Ví dụ: Template `' OR '1'='1` → LLM sinh `' OR 'a'='a`"

---

## ❓ Q6: "Baseline 30-60 phút lấy từ đâu?"

**Trả lời:**

> "Thưa thầy/cô, nguồn từ:
>
> - **IBM Cost of Data Breach Report 2023:** MTTD trung bình 204 ngày
> - **Splunk State of Security 2023:** 55% tổ chức mất >1 giờ respond
>
> Nhóm em cũng so sánh với K8s HPA và Prometheus+Alertmanager, không chỉ so với manual."

---

## ❓ Q7: "Tự tấn công, tự phòng thủ, có bias không?"

**Trả lời:**

> "Thưa thầy/cô, nhóm em có các biện pháp:
>
> 1. Dùng **OWASP Testing Guide** làm chuẩn attack, không tự nghĩ
> 2. **Blind test:** Attack scenarios được shuffle ngẫu nhiên
> 3. **External benchmark:** So với K8s HPA và Prometheus+Alertmanager
> 4. Test trên **nhiều target apps** khác nhau"

---

# 💡 MẸO THUYẾT TRÌNH

1. **Đừng đọc slide** - nói tự nhiên, slide chỉ là hỗ trợ
2. **Focus vào VẤN ĐỀ và GIẢI PHÁP** - 2 slide quan trọng nhất
3. **Chuẩn bị câu trả lời phản biện** - đây là phần chính!
4. **Nếu không biết, nói thật:** "Em chưa nghiên cứu sâu phần này, em xin ghi nhận"
5. **Tự tin nhưng khiêm tốn:** "Đây là đóng góp trong phạm vi open-source và nghiên cứu sinh viên"

---

_File này dùng để chuẩn bị, KHÔNG phải slide PowerPoint cuối cùng_
