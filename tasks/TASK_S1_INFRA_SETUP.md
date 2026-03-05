## 💡 Context

> **Task ID**: S1  
> **Phase**: Phase 1 - Setup & Research  
> **Sprint**: Sprint 1 - Foundation  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 1 (Tuần 1-2)  
> **Assignee**: 🔴 Hoàng (Lead)  
> **Blocked by**: Không  
> **Blocks**: S2, S3, S4, S5, S6 (tất cả task Phase 1 phụ thuộc infra)

> Thiết lập toàn bộ infrastructure nền tảng cho dự án ZERO DOOR.
> Đây là task đầu tiên, phải xong trước khi bắt tay vào bất cứ development nào.

---

## 🤖 AI Refined

> **User Story:**

> As a **DevOps Engineer / Lead Developer**, I want to **set up the complete project infrastructure including GitHub repo, CI/CD pipeline, and Kubernetes cluster** so that **all subsequent development has a stable, reproducible foundation to build upon.**

**Acceptance Criteria:**

- [ ] GitHub repository tạo xong với branch protection rules (main: require PR review)
- [ ] `.gitignore` bao gồm: `.env`, `*.log`, `node_modules/`, `target/`, `bin/`
- [ ] README.md v1 với: Project overview, Tech Stack, Getting Started
- [ ] GitHub Projects board tạo xong với 6 cột (Backlog, To Do, In Progress, Review, Done, Blocked)
- [ ] Labels tạo xong: `🔴 lead-dev`, `🟡 support-dev`, `P0-critical`, `P1-high`, `P2-medium`, `type:feature`, `type:bug`, `type:docs`, `type:infra`
- [ ] Milestone "Sprint 1" tạo trên GitHub
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` có sẵn (copy từ workflow.md Section 8.4)
- [ ] Commit convention documented (`.github/CONTRIBUTING.md`)

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.1.1 Tạo GitHub repository `Zero-Door` (public hoặc private)
- [ ] 1.1.2 Setup branch protection rules cho `main` (require 1 review, no force push)
- [ ] 1.1.3 Tạo GitHub Projects board theo cấu trúc workflow.md Section 3.1
- [ ] 1.1.4 Tạo Labels + Milestones (Sprint 1 → Sprint 12)
- [ ] 1.1.5 Viết README.md v1 (project overview, architecture high-level, getting started)
- [ ] 1.1.6 Setup `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] 1.1.7 Setup `.github/CONTRIBUTING.md` (commit convention, branch naming)

### Branch & PR

- [ ] Branch: `infra/project-setup`
- [ ] PR Created
- [ ] README content reviewed
- [ ] Board functional (test: tạo 1 issue, kéo qua các cột)

---

## 📝 Notes

> **Best Practice từ project HolmHz:**
>
> - GitHub Projects board là central hub — mọi task đều là Issue
> - Labels giúp filter nhanh: ai làm? priority? loại gì?
> - Milestones = Sprints → track velocity qua từng sprint
> - PR Template enforce checklist → không miss items quan trọng

> **Tips cho hpt8001:**
>
> - Task S1 subtask 1.1.3 và 1.1.4 có thể giao cho hpt8001
> - Cung cấp screenshot hướng dẫn cách tạo board trên GitHub Projects

> **Tham khảo:**
>
> - [workflow.md](../docs/workflow.md) Section 3 — Board setup
> - [workflow.md](../docs/workflow.md) Section 8 — Git Workflow
