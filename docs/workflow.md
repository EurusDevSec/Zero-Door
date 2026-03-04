# QUY TRÌNH LÀM VIỆC SCRUMBAN — ZERO DOOR

## Mô phỏng Môi trường Doanh nghiệp cho Nhóm 2 Người

---

## 1. Tại sao Scrumban? (Không phải Scrum hay Kanban thuần)

### 1.1. So sánh 3 phương pháp

| Tiêu chí              | Scrum                        | Kanban                      | **Scrumban (Chọn)**                  |
| --------------------- | ---------------------------- | --------------------------- | ------------------------------------ |
| Sprint cố định?       | ✅ Có (2-4 tuần)             | ❌ Không                    | ✅ Có nhưng linh hoạt (2 tuần)       |
| WIP Limit?            | ❌ Không rõ ràng             | ✅ Có                       | ✅ Có                                |
| Planning?             | Sprint Planning lớn          | Khi cần (on-demand)         | Planning nhẹ đầu sprint              |
| Review/Retro?         | Cuối mỗi Sprint              | Khi cần                     | Cuối mỗi Sprint (nhẹ)               |
| Phù hợp team nhỏ?    | ⚠️ Nhiều ceremony quá        | ⚠️ Thiếu kỷ luật           | ✅ Cân bằng                          |
| Phù hợp 2 người?     | ❌ Quá nặng                  | ⚠️ Dễ lười                  | ✅ Vừa đủ áp lực                    |

### 1.2. Lý do chọn Scrumban cho ZERO DOOR

```
Scrum cho bạn: KỶ LUẬT (Sprint, Review, Deadline)
   +
Kanban cho bạn: LINH HOẠT (WIP limit, visual flow, pull-based)
   =
Scrumban: VỪA ĐỦ ÁP LỰC + KHÔNG QUÁ CỨNG NHẮC
```

**Cụ thể cho nhóm 2 người:**
- Sprint 2 tuần → tạo deadline nhỏ, không bị "để dành cuối kỳ"
- WIP Limit = 2-3 tasks → focus, không lan man
- Daily standup 5 phút → accountability hàng ngày
- Review cuối sprint → giả lập báo cáo cho "khách hàng" (hội đồng)

---

## 2. Mindset: Hội đồng = Khách hàng

### 2.1. Mapping vai trò

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MÔ PHỎNG DOANH NGHIỆP                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  THỰC TẾ DOANH NGHIỆP          ZERO DOOR PROJECT                  │
│  ─────────────────────          ──────────────────                  │
│                                                                     │
│  Product Owner (PO)         →   BẠN (Lead Developer)               │
│  → Hiểu yêu cầu khách hàng     → Hiểu yêu cầu hội đồng           │
│  → Quyết định priorities        → Quyết định làm gì trước          │
│  → Demo cho stakeholders        → Demo cho giảng viên              │
│                                                                     │
│  Tech Lead / Senior Dev     →   BẠN (Main Developer)              │
│  → Thiết kế kiến trúc           → Code chính, review code          │
│  → Code features phức tạp       → Agents, K8s, AI integration      │
│  → Mentor junior                → Hướng dẫn teammate               │
│                                                                     │
│  Junior Developer           →   TEAMMATE (Support)                 │
│  → Tasks đơn giản               → Docs, testing, UI, configs       │
│  → Học hỏi từ Senior            → Học từ bạn                       │
│  → Follow coding standards      → Theo template có sẵn             │
│                                                                     │
│  Khách hàng (Client)        →   HỘI ĐỒNG (Academic Board)         │
│  → Đặt yêu cầu sản phẩm        → Đặt yêu cầu đề tài              │
│  → Review demos                 → Review tiến độ                   │
│  → Nghiệm thu sản phẩm         → Chấm điểm bảo vệ                │
│                                                                     │
│  Project Manager            →   BẠN (kiêm nhiệm)                  │
│  → Track tiến độ                → Quản lý board, deadline          │
│  → Report cho stakeholders      → Báo cáo giảng viên              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2. "Sản phẩm" giao cho "Khách hàng"

| Sprint | "Sản phẩm" giao cho Hội đồng              | Tương đương doanh nghiệp         |
| ------ | ------------------------------------------ | -------------------------------- |
| S1-S2  | Báo cáo tiến độ + Demo K8s setup           | MVP Demo cho client              |
| S3-S4  | Demo Agent Gaia dashboard                  | Feature demo                     |
| S5-S6  | Demo Nemesis attack scenarios              | Alpha release                    |
| S7-S8  | Demo Hephaestus self-healing               | Beta release                     |
| S9-S10 | Full War Game demo + metrics               | UAT (User Acceptance Testing)    |
| S11-S12| Báo cáo + Presentation + Source code       | Production release + handover    |

---

## 3. Thiết lập Scrumban Board

### 3.1. Cấu trúc Board (Kanban Board)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ZERO DOOR SCRUMBAN BOARD                              │
├────────────┬────────────┬────────────┬────────────┬────────────┬────────────────┤
│  BACKLOG   │  TO DO     │ IN PROGRESS│  REVIEW    │   DONE     │   BLOCKED      │
│            │ (Sprint)   │ (WIP: 3)   │ (WIP: 2)   │            │                │
│            │            │            │            │            │                │
│ • Task X   │ • Task A   │ 🔴 Task B  │ • Task C   │ ✅ Task D  │ ⛔ Task E      │
│ • Task Y   │ • Task F   │ 🟡 Task G  │            │ ✅ Task H  │   (reason)     │
│ • Task Z   │            │            │            │            │                │
│ • ...      │            │            │            │            │                │
├────────────┴────────────┴────────────┴────────────┴────────────┴────────────────┤
│ 🔴 = Bạn (Lead)    🟡 = Teammate (Support)    ⛔ = Blocked (cần giải quyết)   │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2. WIP Limits (Work In Progress)

| Cột          | WIP Limit | Lý do                                             |
| ------------ | --------- | ------------------------------------------------- |
| TO DO        | 6         | Chỉ plan cho 1 sprint (2 tuần), đủ cho 2 người   |
| IN PROGRESS  | **3**     | 2 cho Bạn + 1 cho Teammate. KHÔNG được vượt quá!  |
| REVIEW       | **2**     | Không để review chồng chất                         |
| BLOCKED      | Không     | Bất cứ lúc nào blocked → ưu tiên unblock ngay     |

> **Quy tắc vàng:** Nếu IN PROGRESS đã có 3 tasks → **PHẢI finish 1 cái** trước khi kéo task mới. Đây là cách tạo áp lực focus.

### 3.3. Công cụ đề xuất

| Công cụ                    | Mục đích               | Chi phí | Ghi chú                          |
| -------------------------- | ---------------------- | ------- | -------------------------------- |
| **GitHub Projects**        | Kanban board           | Free    | ✅ Đề xuất — tích hợp với code   |
| **GitHub Issues**          | Task tracking          | Free    | Mỗi task = 1 Issue               |
| **GitHub Milestones**      | Sprint tracking        | Free    | Mỗi Sprint = 1 Milestone         |
| **GitHub Actions**         | CI/CD                  | Free    | Auto test, build                  |
| Discord / Zalo             | Daily standup (chat)   | Free    | Chat nhanh hàng ngày              |
| Notion (optional)          | Docs, meeting notes    | Free    | Nếu cần ghi chú thêm             |

---

## 4. Sprint Structure (Chu kỳ 2 tuần)

### 4.1. Lịch Sprint

```
SPRINT 2-TUẦN (14 ngày)
═══════════════════════════════════════════════════════════

Ngày 1 (Thứ 2) ─── SPRINT PLANNING (30-45 phút)
  │                  • Review backlog
  │                  • Chọn tasks cho sprint
  │                  • Phân task: Bạn vs Teammate
  │
  ├── Ngày 2-5 ──── WORKING DAYS
  │                  • Daily standup 5 phút (Discord/Zalo)
  │                  • Code, test, document
  │
  ├── Ngày 6 ─────── MID-SPRINT CHECK (15 phút)
  │                  • Xem board: có gì blocked?
  │                  • Adjust plan nếu cần
  │
  ├── Ngày 7-12 ──── WORKING DAYS
  │                  • Tiếp tục code
  │                  • Code review (bạn review teammate)
  │
  ├── Ngày 13 ────── SPRINT REVIEW (30 phút)
  │                  • Demo những gì DONE
  │                  • Record video demo (cho hội đồng)
  │
  └── Ngày 14 ────── SPRINT RETROSPECTIVE (15 phút)
                     • Cái gì tốt? Cái gì cần cải thiện?
                     • Action items cho sprint sau
```

### 4.2. Daily Standup (5 phút — qua chat)

Mỗi ngày, cả 2 người gửi vào nhóm chat (Discord/Zalo):

```markdown
## Daily Standup — [Ngày/Tháng]
**Hôm qua:** Làm xong [task gì]
**Hôm nay:** Sẽ làm [task gì]
**Blocked:** [Có gì bị chặn không?] — Không có / Có: [mô tả]
```

> **Tại sao quan trọng?** Trong doanh nghiệp, daily standup là cách team sync tiến độ. Với 2 người, chỉ cần **5 phút chat** là đủ. Không cần gọi video.

### 4.3. Sprint Planning Template

```markdown
# Sprint Planning — Sprint [X]
**Ngày:** [DD/MM/YYYY]
**Sprint Goal:** [Mục tiêu chính của sprint này]

## Tasks cho Sprint này

### 🔴 Bạn (Lead Dev) — [3-4 tasks]
| # | Task | Estimate | Priority |
|---|------|----------|----------|
| 1 | ...  | 3 ngày   | P0       |
| 2 | ...  | 2 ngày   | P1       |

### 🟡 Teammate (Support) — [2-3 tasks]
| # | Task | Estimate | Priority |
|---|------|----------|----------|
| 1 | ...  | 2 ngày   | P1       |
| 2 | ...  | 1 ngày   | P2       |

## Risks & Dependencies
- [Risk 1]: ...
- [Dependency 1]: ...
```

### 4.4. Sprint Retrospective Template

```markdown
# Sprint Retro — Sprint [X]

## 🟢 Cái gì tốt? (Keep doing)
- ...

## 🔴 Cái gì chưa tốt? (Stop doing)
- ...

## 🟡 Cái gì cần cải thiện? (Start doing)
- ...

## 📋 Action Items
| # | Action | Ai làm | Deadline |
|---|--------|--------|----------|
| 1 | ...    | Bạn    | Sprint X |
```

---

## 5. Phân chia Công việc (Task Distribution)

### 5.1. Nguyên tắc phân chia

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHÂN CHIA TASK THEO ĐỘ KHÓ                    │
│                                                                   │
│  Difficulty   ██████████████████████████████████████████████████  │
│               ◄──── TEAMMATE ────►◄──────── BẠN ──────────────► │
│               │                   │                              │
│  Level 1-3    │  Level 4-10       │                              │
│  (Simple)     │  (Medium-Hard)    │                              │
│               │                   │                              │
│  • Viết docs  │  • Code Agents    │                              │
│  • Tạo slides │  • K8s configs    │                              │
│  • Test cases │  • AI integration │                              │
│  • UI/CSS     │  • Kafka setup    │                              │
│  • Data prep  │  • Architecture   │                              │
│  • Diagrams   │  • Debug/Fix      │                              │
│               │  • Code review    │                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2. Task Matrix chi tiết

#### 🔴 Bạn (Lead Developer) — ~70% workload

| Loại công việc           | Ví dụ cụ thể                                           | Skill level |
| ----------------------- | ------------------------------------------------------- | ----------- |
| **Architecture Design** | Thiết kế kiến trúc 3 Agents, Kafka topics               | Hard        |
| **Core Development**    | Code Agent Nemesis, Gaia, Hephaestus (Java Spring Boot)  | Hard        |
| **Chaos Worker**        | Code Go chaos-worker (DDoS, stress test)                 | Hard        |
| **AI Integration**      | Spring AI + LLM, prompt engineering                      | Hard        |
| **K8s/Infra**           | Helm charts, K8s manifests, Docker configs               | Medium-Hard |
| **Kafka Setup**         | Topic design, consumer/producer code                     | Medium      |
| **Code Review**         | Review code của teammate                                 | Medium      |
| **Sprint Management**   | Planning, board management, retro                        | Medium      |
| **Report Writing**      | Phần kỹ thuật, methodology, results                     | Medium      |

#### 🟡 Teammate (Support Developer) — ~30% workload

| Loại công việc          | Ví dụ cụ thể                                            | Skill level |
| ---------------------- | -------------------------------------------------------- | ----------- |
| **Documentation**      | README, API docs, user guides                            | Easy        |
| **Presentation**       | Slides, poster, demo video editing                       | Easy        |
| **Testing**            | Viết test cases, chạy test manual                        | Easy-Medium |
| **Data Collection**    | Thu thập metrics, screenshot, ghi log thực nghiệm        | Easy        |
| **UI/Dashboard**       | Customize Grafana dashboard, layout                      | Easy-Medium |
| **Report Writing**     | Phần bối cảnh, related works, tóm tắt                   | Easy-Medium |
| **Config Files**       | YAML configs (theo template bạn cung cấp)               | Easy        |
| **Diagrams**           | Vẽ sơ đồ kiến trúc (Draw.io, Mermaid)                   | Easy        |
| **Research**           | Tìm papers, tổng hợp related works                      | Easy-Medium |

### 5.3. Hướng dẫn phân task hiệu quả cho Teammate

> **Best Practice:** Không giao task mơ hồ kiểu "Làm phần docs đi". Phải cụ thể:

```
❌ SAI: "Em viết documentation cho project nhé"
✅ ĐÚNG: "Em viết file README.md theo template này [link], 
         bao gồm: Installation (copy từ setup guide), 
         Usage (xem demo video), Architecture (copy từ plan.md).
         Deadline: Thứ 6 tuần này."
```

**Checklist khi giao task cho Teammate:**
- [ ] Task có mô tả rõ ràng (WHAT)
- [ ] Có template/example để tham khảo (HOW)
- [ ] Có deadline cụ thể (WHEN)
- [ ] Có acceptance criteria rõ ràng (DONE = gì?)
- [ ] Estimate thời gian (bao lâu?)

---

## 6. Sprint Roadmap (12 Sprints × 2 tuần = 24 tuần ≈ 6 tháng)

### 6.1. Tổng quan

```
Sprint 1-2   ████░░░░░░░░░░░░░░░░░░░░  Phase 1: Setup & Research
Sprint 3-4   ░░░░████░░░░░░░░░░░░░░░░  Phase 2: Target + Gaia
Sprint 5-6   ░░░░░░░░████░░░░░░░░░░░░  Phase 3: Nemesis
Sprint 7-8   ░░░░░░░░░░░░████░░░░░░░░  Phase 4: Hephaestus
Sprint 9-10  ░░░░░░░░░░░░░░░░████░░░░  Phase 5: War Game
Sprint 11-12 ░░░░░░░░░░░░░░░░░░░░████  Phase 6: Closing
```

### 6.2. Chi tiết mỗi Sprint

---

#### Sprint 1 (Tháng 01 — Tuần 1-2): Foundation

**Sprint Goal:** _"Team có thể dev locally và K8s cluster sẵn sàng"_

| # | Task                              | Ai làm       | Est.  | Priority |
|---|-----------------------------------|--------------|-------|----------|
| 1 | Setup GitHub repo + branch rules  | 🔴 Bạn       | 1 ngày | P0       |
| 2 | Setup K8s cluster (K3s/Minikube)  | 🔴 Bạn       | 3 ngày | P0       |
| 3 | Setup GitHub Projects board       | 🟡 Teammate  | 1 ngày | P0       |
| 4 | Đọc + tóm tắt paper ADARMA       | 🟡 Teammate  | 3 ngày | P1       |
| 5 | Setup dev environment (Java, Go)  | 🔴 Bạn       | 1 ngày | P0       |
| 6 | Viết README v1                    | 🟡 Teammate  | 1 ngày | P2       |

**Demo cho "khách hàng":** K8s cluster chạy được, board setup xong, README có.

---

#### Sprint 2 (Tháng 01 — Tuần 3-4): Research & Architecture

**Sprint Goal:** _"Kiến trúc chi tiết hoàn chỉnh, literature review xong"_

| # | Task                                    | Ai làm       | Est.  | Priority |
|---|-----------------------------------------|--------------|-------|----------|
| 1 | Thiết kế kiến trúc chi tiết (diagrams)  | 🔴 Bạn       | 3 ngày | P0       |
| 2 | Design Kafka topics + message schemas   | 🔴 Bạn       | 2 ngày | P0       |
| 3 | Tóm tắt 5 papers quan trọng nhất       | 🟡 Teammate  | 4 ngày | P1       |
| 4 | Vẽ architecture diagrams (Draw.io)      | 🟡 Teammate  | 2 ngày | P1       |
| 5 | Setup Prometheus + Grafana on K8s       | 🔴 Bạn       | 2 ngày | P1       |

**Demo:** Kiến trúc document, Prometheus/Grafana dashboard cơ bản.

---

#### Sprint 3-4 (Tháng 02): Target App + Agent Gaia

**Sprint Goal:** _"Target app chạy trên K8s, Gaia detect được metrics"_

| # | Task                                         | Ai làm       | Est.  |
|---|----------------------------------------------|--------------|-------|
| 1 | Deploy Google Online Boutique lên K8s         | 🔴 Bạn       | 2 ngày |
| 2 | Code Agent Gaia — Prometheus scraper          | 🔴 Bạn       | 5 ngày |
| 3 | Code Agent Gaia — Anomaly detection (basic)   | 🔴 Bạn       | 5 ngày |
| 4 | Customize Grafana dashboards                  | 🟡 Teammate  | 3 ngày |
| 5 | Viết test cases cho Gaia                      | 🟡 Teammate  | 2 ngày |
| 6 | Thu thập baseline metrics (before attack)     | 🟡 Teammate  | 2 ngày |
| 7 | Tích hợp Kafka — Gaia publish alerts          | 🔴 Bạn       | 3 ngày |

---

#### Sprint 5-6 (Tháng 03): Agent Nemesis

**Sprint Goal:** _"Nemesis sinh và thực thi được 3 loại attack"_

| # | Task                                         | Ai làm       | Est.  |
|---|----------------------------------------------|--------------|-------|
| 1 | Code Go chaos-worker (stress test tool)       | 🔴 Bạn       | 5 ngày |
| 2 | Code Agent Nemesis — Spring Boot service      | 🔴 Bạn       | 5 ngày |
| 3 | Tích hợp LLM (Spring AI) — payload gen       | 🔴 Bạn       | 5 ngày |
| 4 | Tạo OWASP attack template library             | 🟡 Teammate  | 3 ngày |
| 5 | Test từng loại attack riêng lẻ                | 🟡 Teammate  | 3 ngày |
| 6 | Ghi log + record kết quả attack              | 🟡 Teammate  | 2 ngày |

---

#### Sprint 7-8 (Tháng 04): Agent Hephaestus

**Sprint Goal:** _"Hephaestus tự động heal được system"_

| # | Task                                         | Ai làm       | Est.  |
|---|----------------------------------------------|--------------|-------|
| 1 | Code Agent Hephaestus — K8s API client        | 🔴 Bạn       | 5 ngày |
| 2 | Implement Scale action                        | 🔴 Bạn       | 3 ngày |
| 3 | Implement Block IP action                     | 🔴 Bạn       | 3 ngày |
| 4 | Implement Rollback action                     | 🔴 Bạn       | 3 ngày |
| 5 | Test healing actions riêng lẻ                 | 🟡 Teammate  | 3 ngày |
| 6 | Viết docs cho Hephaestus API                  | 🟡 Teammate  | 2 ngày |

---

#### Sprint 9-10 (Tháng 05): War Game + Experiment

**Sprint Goal:** _"3 Agents chạy đồng thời, có metrics MTTD/MTTR"_

| # | Task                                         | Ai làm       | Est.  |
|---|----------------------------------------------|--------------|-------|
| 1 | Tích hợp toàn bộ 3 Agents                    | 🔴 Bạn       | 5 ngày |
| 2 | Chạy experiment — Baseline (manual)           | 🔴 Bạn       | 2 ngày |
| 3 | Chạy experiment — Self-Healing (auto)         | 🔴 Bạn       | 3 ngày |
| 4 | Thu thập data: MTTD, MTTR, Uptime            | 🟡 Teammate  | 3 ngày |
| 5 | Record video demo (toàn bộ flow)              | 🟡 Teammate  | 2 ngày |
| 6 | Tạo bảng so sánh Baseline vs Self-Healing     | 🟡 Teammate  | 2 ngày |
| 7 | Chạy stress test (3 attacks đồng thời)        | 🔴 Bạn       | 3 ngày |

---

#### Sprint 11-12 (Tháng 06): Closing & Defense

**Sprint Goal:** _"Sẵn sàng bảo vệ trước hội đồng"_

| # | Task                                         | Ai làm       | Est.  |
|---|----------------------------------------------|--------------|-------|
| 1 | Viết báo cáo — phần kỹ thuật + kết quả       | 🔴 Bạn       | 5 ngày |
| 2 | Viết báo cáo — phần bối cảnh + related works  | 🟡 Teammate  | 4 ngày |
| 3 | Tạo slides bảo vệ                            | 🟡 Teammate  | 3 ngày |
| 4 | Review + chỉnh báo cáo                       | 🔴 Bạn       | 3 ngày |
| 5 | Đóng gói source code (clean, docs)            | 🔴 Bạn       | 2 ngày |
| 6 | Tập bảo vệ (dry run)                         | Cả 2         | 2 ngày |
| 7 | Làm poster (nếu cần)                         | 🟡 Teammate  | 2 ngày |

---

## 7. Definition of Done (DoD)

### 7.1. Task-Level DoD

Một task chỉ được chuyển sang "DONE" khi **TẤT CẢ** điều kiện sau được thỏa mãn:

| #   | Tiêu chí                           | Mô tả                                                |
| --- | ---------------------------------- | ---------------------------------------------------- |
| D1  | **Code hoạt động**                 | Không crash, chạy được trên local/K8s                 |
| D2  | **Có test (nếu là code)**          | Ít nhất có test cơ bản (happy path)                   |
| D3  | **Code pushed lên GitHub**         | Commit rõ ràng, branch đúng                           |
| D4  | **Được review** (nếu là code)     | Lead (bạn) đã review code của Teammate               |
| D5  | **Documentation updated**          | README hoặc docs phản ánh thay đổi                    |

### 7.2. Sprint-Level DoD

Một Sprint chỉ "DONE" khi:

- [ ] Sprint Goal đạt được (hoặc giải thích tại sao không)
- [ ] Tất cả tasks trong sprint: Done hoặc moved to next sprint (có lý do)
- [ ] Demo video/screenshot saved
- [ ] Retro notes ghi lại
- [ ] Board updated, no stale tasks

---

## 8. Git Workflow

### 8.1. Branch Strategy (GitHub Flow — đơn giản cho 2 người)

```
main ─────────────────────────────────────────────── (Production-ready)
  │
  ├── feature/gaia-prometheus ─── PR ──► main        (Feature branch)
  │
  ├── feature/nemesis-sqli ─────── PR ──► main       (Feature branch)
  │
  └── docs/sprint-3-report ────── PR ──► main        (Docs branch)
```

### 8.2. Branch Naming Convention

```
feature/[agent]-[feature]     →  feature/gaia-anomaly-detection
bugfix/[issue-number]-[desc]  →  bugfix/42-kafka-timeout
docs/[what]                   →  docs/architecture-diagram
infra/[what]                  →  infra/helm-chart-setup
```

### 8.3. Commit Message Convention

```
<type>(<scope>): <description>

Ví dụ:
feat(nemesis): add SQL injection payload generator
fix(gaia): fix Prometheus scrape interval
docs(plan): update sprint 3 tasks
infra(k8s): add Grafana Helm chart
test(hephaestus): add unit test for scale action
chore: update dependencies
```

| Type     | Khi nào dùng                        |
| -------- | ----------------------------------- |
| `feat`   | Thêm feature mới                    |
| `fix`    | Sửa bug                             |
| `docs`   | Thay đổi documentation              |
| `infra`  | Infrastructure (K8s, Docker, CI/CD) |
| `test`   | Thêm/sửa tests                      |
| `chore`  | Việc lặt vặt (dependencies, clean)  |

### 8.4. Pull Request Template

```markdown
## Mô tả
[Mô tả ngắn gọn thay đổi]

## Loại thay đổi
- [ ] Feature mới
- [ ] Bug fix
- [ ] Documentation
- [ ] Infrastructure

## Checklist
- [ ] Code chạy được trên local
- [ ] Tests pass
- [ ] Docs updated
- [ ] No hardcoded secrets

## Screenshots/Video (nếu có)
[Paste ảnh/video demo]
```

---

## 9. Communication Protocol

### 9.1. Kênh giao tiếp

| Kênh                 | Mục đích                      | Tần suất        |
| -------------------- | ----------------------------- | ---------------- |
| **Discord/Zalo**     | Daily standup, quick chat     | Hàng ngày        |
| **GitHub Issues**    | Task tracking, discussion     | Khi cần           |
| **GitHub PR Review** | Code review, feedback         | Khi có PR         |
| **Gặp mặt/Call**    | Sprint Planning, Review, Retro| 2 tuần/lần        |

### 9.2. Escalation Protocol

```
Bị blocked 1 giờ?     → Hỏi Google/ChatGPT
Bị blocked 4 giờ?     → Nhờ teammate hoặc tìm workaround
Bị blocked 1 ngày?    → Flag trên board + đổi sang task khác
Bị blocked 2+ ngày?   → Cần thay đổi approach / cắt scope
```

---

## 10. Metrics & Tracking

### 10.1. Velocity Tracking

Theo dõi qua mỗi Sprint để biết team nhanh hay chậm:

```markdown
# Velocity Chart
| Sprint | Planned | Completed | Velocity |
|--------|---------|-----------|----------|
| S1     | 6       | 5         | 83%      |
| S2     | 6       | 6         | 100%     |
| S3     | 7       | 5         | 71%      |
| ...    |         |           |          |
```

### 10.2. Burndown (đơn giản)

Cuối mỗi ngày, ghi lại số tasks còn lại:

```
S3: Started = 7 tasks
Day 1: 7 remaining ██████████████
Day 3: 6 remaining ████████████
Day 5: 5 remaining ██████████
Day 7: 4 remaining ████████
Day 9: 3 remaining ██████
Day 11: 1 remaining ██
Day 14: 0 remaining ✅
```

---

## 11. Quick Reference — "Ngày đầu đi làm"

### Bước 1: Setup tất cả (1 lần duy nhất)

```bash
# 1. GitHub repo (đã có)
# 2. Mở GitHub Projects → Create board với 6 cột (Backlog, To Do, In Progress, Review, Done, Blocked)
# 3. Tạo Labels:
#    🔴 lead-dev, 🟡 support-dev
#    P0-critical, P1-high, P2-medium, P3-low
#    type:feature, type:bug, type:docs, type:infra
# 4. Tạo Milestone cho Sprint 1
```

### Bước 2: Mỗi Sprint (lặp lại)

```
Ngày 1:  📋 Sprint Planning (30-45 phút)
Ngày 2-12: 💬 Daily Standup (5 phút/ngày qua chat)
           💻 Code + Review + Test
Ngày 13: 📺 Sprint Review (30 phút) — Demo cho nhau
Ngày 14: 🔄 Sprint Retro (15 phút) — Rút kinh nghiệm
```

### Bước 3: Hàng ngày

```
Sáng:   Gửi daily standup vào chat
        Check board → kéo task "To Do" → "In Progress"
Chiều:  Code/làm task
        Commit + push lên GitHub
Tối:    (Optional) Review PR nếu có
```

---

## 12. Lời khuyên Thực tế

### 12.1. Cho Bạn (Lead)

1. **Đừng perfectionist** — Done > Perfect. Ship nhanh, iterate sau.
2. **Giao task rõ ràng** cho teammate — template + deadline + example.
3. **Review code nhanh** — đừng để PR treo >2 ngày.
4. **Khi bị stuck** — timebox 2 giờ, sau đó đổi approach.
5. **Record mọi thứ** — screenshot, video, metrics. Hội đồng thích evidence.

### 12.2. Cho Teammate

1. **Hỏi khi chưa hiểu** — tốt hơn là làm sai.
2. **Follow template** — bạn (lead) sẽ cung cấp template, cứ theo đó.
3. **Commit thường xuyên** — nhỏ, rõ ràng, không gom 1 commit lớn.
4. **Chủ động pick task** — khi xong task, tự kéo task mới từ To Do.

### 12.3. Common Pitfalls (Bẫy thường gặp)

| Bẫy                              | Cách tránh                                      |
| -------------------------------- | ----------------------------------------------- |
| "Sprint 1 làm chưa xong, để lại" | Cắt scope task, hoàn thành phần nhỏ hơn         |
| "Teammate không biết làm gì"    | Template rõ ràng + pair programming 30 phút đầu |
| "Không ai review code"          | Bạn review tất cả — chỉ cần 10 phút/PR          |
| "Board không update"            | Quy tắc: mỗi khi commit → update board          |
| "Quên retro"                    | Bắt buộc — dù chỉ 10 phút, viết 3 bullet points |

---

_Cập nhật: 04/03/2026_  
_Version: 1.0_
