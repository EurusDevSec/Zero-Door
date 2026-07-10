# 💾 SESSION_MEMORY.md — Trạng Thái Hiện Tại
> *Last updated: 2026-07-10 21:47 GMT+7 | Phase 5 COMPLETED — UI Redesign (AWS Cloudscape) DONE | Next: Phase 6 Cloud*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Phase 5 UI/UX Redesign hoàn tất. Chuẩn bị Phase 6 (Cloud + Demo Video).

**Phase vừa hoàn thành**: Redesign toàn bộ giao diện Dashboard từ Dark Cyberpunk → **AWS Cloudscape-inspired Light Theme**, layout cố định không scroll, sidebar collapsible, right chat panel collapsible, topology hiển thị đầy đủ, skeleton loading.

**Git branch**: `main`

---

## ⚡ Những việc ĐÃ HOÀN THÀNH trong session này (2026-07-10)

### 🎨 UI/UX Redesign — AWS Cloudscape Light Theme
- **Viết lại hoàn toàn `style.css`** với Cloudscape color token system:
  - White/light background (`#f2f3f3`, `#ffffff`)
  - AWS blue accent (`#0073bb`), purple brand (`#6b46c1`)
  - Fixed-height viewport layout — **KHÔNG scroll** cả trang
  - 4-panel grid: `55%/45%` rows × `230px / 1fr` columns
- **Viết lại hoàn toàn `index.html`**:
  - `app-shell → top-nav → main-row → [sidebar | content | chat-panel] → footer`
  - 4 panels: Control & Simulation | War Game Topology | Microservices Status | Log Console + Agent Insights
  - Floating trigger button khi chat panel collapse
- **Refactor `app.js`**:
  - `toggleSidebar()` dùng class `.collapsed` mới
  - `toggleRightChat()` với floating trigger visible/hidden
  - `activateNavItem()` — highlight nav item active
  - `renderAgentChat()` — update cả main chat panel + "Agent Insights" preview tile
  - Topology node reset dùng semantic CSS classes thay Tailwind ad-hoc
  - Log console dùng dark terminal với `badge-attacker/defender/observer/system` classes
- **Skeleton loading**: shimmer animation cho cards khi chờ API

### ✅ Trước đó (sessions cũ — đã ổn định)
- Skeleton screen shimmer animation khi load dữ liệu
- Polling rate 5s, Connection Lost Banner
- Auto-failover API keys Gemini
- OOMKilled fix: stress pod limits 1000m/512Mi
- Reset System scale-down về 1 replica
- Prometheus range vector [2m] fix

---

## 🧠 Semantic Context Essence

- **UI Architecture**: `style.css` dùng CSS custom properties (`--clr-*`, `--sidebar-width`, `--chat-panel-width`) — không dùng Tailwind hardcode cho layout chính. Tailwind vẫn có trong HTML nhưng chỉ cho một số utility nhỏ.
- **Grid Layout**: `grid-template-rows: 55% 45%` + `grid-template-columns: 230px 1fr` trong `.page-content`. Thay đổi ở đây sẽ ảnh hưởng toàn bộ bố cục.
- **Sidebar collapse**: class `.collapsed` trên `#dashboard-sidebar` → `width: var(--sidebar-collapsed-width)` = 48px. Nav text ẩn bằng `opacity:0; width:0`.
- **Chat panel collapse**: class `.collapsed` trên `#agent-chat-drawer` → `width: 0`. Floating button `#chat-drawer-trigger` hiện ra.
- **Port-forward pattern**: Mỗi khi rollout restart pod nemesis, port-forward bị ngắt. Phải `kubectl port-forward svc/nemesis 9092:8000` lại sau mỗi lần rollout.
- **Rebuild workflow**: `docker build --no-cache → k3d image import → kubectl rollout restart → kubectl rollout status`

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------| 
| `agent-orchestrator/nemesis/static/style.css` | **REWRITTEN** — Cloudscape CSS system | CSS custom properties, no Tailwind for layout |
| `agent-orchestrator/nemesis/static/index.html` | **REWRITTEN** — 4-panel layout | AWS Cloudscape structure |
| `agent-orchestrator/nemesis/static/app.js` | **REFACTORED** — uses new CSS classes | `.collapsed` for sidebar/chat, new renderAgentChat |
| `agent-orchestrator/nemesis/main.py` | Attack agent | API key auto-failover retry + static dashboard mount |
| `agent-orchestrator/hephaestus/main.py` | Defender agent | Scale-down deployments về 1 khi reset |
| `agent-orchestrator/gaia/main.py` | Observer agent | Rate query [2m] range vector |
| `chaos-worker/internal/attack/cpu_stress.go` | Chaos Executor | Resource limits 1000m CPU / 512Mi RAM |
| `start-demo.ps1` | 1-click demo launcher | Port-forwards + open browser |

---

## 🔜 Next Steps (ưu tiên tiếp theo)

- [ ] **UI Polish**: Kiểm tra giao diện trên viewport 1920×1080, 1366×768. Fix nếu còn panels bị cắt.
- [ ] **Git commit**: Commit toàn bộ UI changes (`feat(dashboard): AWS Cloudscape light theme redesign`)
- [ ] **Demo video**: Quay theo kịch bản `docs/demo_script.md` — Attack → Detect → Heal → Reset
- [ ] **Slide thuyết trình**: Tích hợp số liệu MTTD (20-30s), MTTR (35-45s)
- [ ] **Phase 6**: `helm package` → Push images → GKE/EKS deploy
