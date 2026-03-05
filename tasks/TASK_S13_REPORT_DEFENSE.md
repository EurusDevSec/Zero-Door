## 💡 Context

> **Task ID**: S13  
> **Phase**: Phase 6 - Closing  
> **Sprint**: Sprint 11-12  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 11-12 (Tuần 21-24)  
> **Assignee**: 🔴 Hoàng (Ch3-4-5, Review) + 🟡 hpt8001 (Ch1-2, Slides, Poster)  
> **Blocked by**: S12 (experiment results needed for report)  
> **Blocks**: Defense date

> Viết báo cáo khoa học, tạo slides, chuẩn bị bảo vệ trước hội đồng.
> Tập trung vào quality — đây là sản phẩm cuối cùng "bán" cho "khách hàng" (hội đồng).

---

## 🤖 AI Refined

> **User Story:**

> As a **Research Team**, I want to **write a comprehensive scientific report, prepare defense slides, and package all deliverables** so that **the academic board has everything needed to evaluate our work and we can present confidently.**

**Acceptance Criteria:**

- [ ] Báo cáo khoa học hoàn chỉnh (5 chương, format theo mẫu trường)
- [ ] Slides bảo vệ (15-20 slides)
- [ ] Video demo (5-10 phút, narrated)
- [ ] Source code đóng gói sạch (README, .gitignore, no secrets)
- [ ] Q&A preparation (20 câu hỏi dự đoán + trả lời)
- [ ] Dry run defense (tập thuyết trình ≥ 2 lần)

---

## 🛠️ Implementation

### Subtasks — 🟡 hpt8001 (Chương 1-2)

- [ ] 11.1.1 Viết Chương 1: Mở đầu
    - 1.1 Lý do chọn đề tài
    - 1.2 Mục tiêu nghiên cứu
    - 1.3 Phạm vi nghiên cứu
    - 1.4 Phương pháp nghiên cứu (overview)
- [ ] 11.1.2 Viết Chương 2: Cơ sở lý thuyết
    - 2.1 Microservices Architecture
    - 2.2 Chaos Engineering
    - 2.3 Multi-Agent Systems
    - 2.4 Self-Healing Systems
    - 2.5 Các công trình liên quan
- [ ] 11.1.3 Gửi Hoàng review Chương 1-2

### Subtasks — 🔴 Hoàng (Chương 3-4-5)

- [ ] 11.1.4 Viết Chương 3: Phương pháp và Xây dựng hệ thống
    - 3.1 Kiến trúc tổng thể
    - 3.2 Agent Nemesis (Red Team)
    - 3.3 Agent Gaia (Observer)
    - 3.4 Agent Hephaestus (Blue Team)
    - 3.5 Communication Protocol (Kafka)
    - 3.6 Observability Stack
- [ ] 11.1.5 Viết Chương 4: Kết quả thực nghiệm
    - 4.1 Thiết lập thí nghiệm
    - 4.2 Kết quả Baseline (Manual)
    - 4.3 Kết quả Self-Healing (Auto)
    - 4.4 So sánh và Phân tích
    - 4.5 Bảng, biểu đồ, hình ảnh
- [ ] 11.1.6 Viết Chương 5: Kết luận
    - 5.1 Tóm tắt kết quả
    - 5.2 Đóng góp
    - 5.3 Giới hạn
    - 5.4 Hướng phát triển tương lai
- [ ] 11.1.7 Merge Chương 1-2 của hpt8001 + Format theo mẫu trường

### Subtasks — 🟡 hpt8001 (Slides + Support)

- [ ] 11.1.8 Tạo slides bảo vệ (PowerPoint/Google Slides):
    - Slide 1: Title
    - Slide 2-3: Problem & Motivation
    - Slide 4-5: Research Questions & Objectives
    - Slide 6-8: System Architecture (diagrams)
    - Slide 9-12: Implementation (3 Agents)
    - Slide 13-15: Experiment Results (charts/tables)
    - Slide 16: Conclusion
    - Slide 17: Future Work
    - Slide 18: Q&A
- [ ] 11.1.9 Chuẩn bị ảnh test cho video demo
- [ ] 11.1.10 Làm poster (nếu cần)

### Subtasks — 🔴 Hoàng (Final)

- [ ] 11.1.11 Review + chỉnh sửa toàn bộ báo cáo
- [ ] 11.1.12 Đóng gói source code (clean, remove secrets, README updated)
- [ ] 11.1.13 Quay video demo (screen record War Game with narration)
- [ ] 11.1.14 Chuẩn bị Q&A (20 câu hỏi dự đoán từ hội đồng)
- [ ] 11.1.15 Dry run defense x2 (tập thuyết trình, time: 15-20 phút)

### Branch & PR

- [ ] Branch: `docs/final-report`
- [ ] PR Created
- [ ] Report reviewed by GVHD (nếu có)
- [ ] All deliverables packaged

---

## 📝 Notes

> **Q&A Dự đoán (TOP 10):**
>
> 1. "Sản phẩm cụ thể là gì?" → Backend Platform/Framework (see plan.md 10.0)
> 2. "Có áp dụng được cho production không?" → Sandbox only, nhưng architecture pluggable
> 3. "Tại sao chọn 3 attack types?" → Proof-of-concept, cover OWASP Top 3
> 4. "AI ở đâu trong project?" → Spring AI sinh payload, anomaly detection ML
> 5. "So sánh với Gremlin/LitmusChaos?" → ZERO DOOR thêm AI + self-healing
> 6. "MTTD < 1 phút có thực tế không?" → Prometheus 15s scrape + instant alert
> 7. "Đạo đức tấn công?" → Sandbox only, no real data, responsible disclosure
> 8. "Có thể mở rộng?" → Yes: pluggable architecture, Helm chart configurable
> 9. "Team chỉ 2 người mà làm được?" → Lead 70% (core), Partner 30% (support)
> 10. "Giới hạn nghiên cứu?" → See plan.md Section 9.4 (7 limitations)

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) — Master plan
> - [workflow.md](../docs/workflow.md) Section 6.2 Sprint 11-12
> - [slides.md](../docs/slides.md) — Existing slide draft
