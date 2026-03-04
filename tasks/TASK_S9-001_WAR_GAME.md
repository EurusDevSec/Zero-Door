## 💡 Context

> **Task ID**: S9-001  
> **Phase**: Phase 5 - War Game  
> **Sprint**: Sprint 9-10  
> **Status**: ⬜ NOT STARTED  
> **Created**: 04/03/2026  
> **Target**: Sprint 9-10 (Tuần 17-20)  
> **Assignee**: 🔴 Hoàng (Lead) + 🟡 Teammate (Data collection, Video, Reports)  
> **Blocked by**: S3-002 (Gaia), S5-002 (Nemesis), S7-001 (Hephaestus) — tất cả 3 agents  
> **Blocks**: S11-001 (Report cần experiment data)

> Tích hợp toàn bộ 3 Agents, chạy War Game, thu thập metrics MTTD/MTTR.
> Đây là phase quan trọng nhất — chứng minh hệ thống hoạt động end-to-end.

---

## 🤖 AI Refined

> **User Story:**

> As a **Research Team**, I want to **run a full War Game with all 3 agents operating simultaneously, collect MTTD/MTTR metrics, and compare Self-Healing vs Manual baseline** so that **we have concrete evidence to present to the academic board.**

**Acceptance Criteria:**

- [ ] Tất cả 3 agents chạy đồng thời trên K8s
- [ ] Full loop hoạt động: Nemesis attack → Gaia detect → Hephaestus heal
- [ ] MTTD measured: < 60 giây trong ≥ 70% test cases
- [ ] MTTR measured: < 180 giây trong ≥ 70% test cases
- [ ] Baseline experiment: manual response (giả lập human delay 5-15 phút)
- [ ] Self-Healing experiment: auto response
- [ ] So sánh bảng: Baseline vs Self-Healing (MTTD, MTTR, Uptime)
- [ ] 3 attack scenarios tested: SQLi, DDoS, Resource Exhaustion
- [ ] 🟡 Teammate: Thu thập data (MTTD, MTTR, Uptime) vào spreadsheet
- [ ] 🟡 Teammate: Record video demo (full War Game flow, 5-10 phút)
- [ ] 🟡 Teammate: Tạo bảng so sánh Baseline vs Self-Healing (charts)
- [ ] Stress test: 3 attacks đồng thời → system survives

---

## 🛠️ Implementation

### Subtasks — 🔴 Hoàng

- [ ] 9.1.1 Integration testing: deploy 3 agents + target app + Kafka + Prometheus
- [ ] 9.1.2 Fix integration bugs (Kafka serialization, namespace, RBAC, etc.)
- [ ] 9.1.3 Create experiment script: `scripts/run_experiment.sh`
    - Start all agents
    - Trigger Nemesis (3 attack types sequentially)
    - Collect timestamps (attack_start, detect_time, heal_time, recover_time)
    - Calculate MTTD = detect_time - attack_start
    - Calculate MTTR = recover_time - detect_time
- [ ] 9.1.4 Run Experiment 1: Baseline (manual response)
    - Disable Hephaestus auto-healing
    - Manually heal (simulate 5-15 min human response)
    - Record MTTD, MTTR
- [ ] 9.1.5 Run Experiment 2: Self-Healing (auto response)
    - Enable all agents
    - Run 3 attack scenarios (5 iterations each = 15 runs)
    - Record MTTD, MTTR, Uptime
- [ ] 9.1.6 Run Stress Test: 3 concurrent attacks
- [ ] 9.1.7 Analyze data: calculate averages, p-values (if applicable)
- [ ] 9.1.8 Generate experiment report (`experiments/results/`)

### Subtasks — 🟡 Teammate

- [ ] 9.1.9 Create data collection spreadsheet template (Google Sheets/Excel):
    ```
    | Run # | Attack Type | Attack Start | Detect Time | MTTD | Heal Start | Recover Time | MTTR | Uptime | Notes |
    ```
- [ ] 9.1.10 Record MTTD, MTTR cho mỗi run (15 self-healing + 5 baseline = 20 runs)
- [ ] 9.1.11 Record video demo: full War Game flow (screen record Grafana + logs)
- [ ] 9.1.12 Tạo comparison chart: Baseline vs Self-Healing (bar chart MTTD, MTTR)
- [ ] 9.1.13 Screenshot Grafana dashboard during attack + healing

### Branch & PR

- [ ] Branch: `feat/s9/war-game`
- [ ] PR Created
- [ ] Experiment data collected (≥ 20 runs)
- [ ] Video demo recorded
- [ ] Comparison table generated

---

## 📝 Notes

> **Experiment Protocol:**
> ```
> For each attack type (SQLi, DDoS, Resource):
>   1. Ensure system is "healthy" (CPU < 30%, no alerts)
>   2. Start recording (screen capture Grafana)
>   3. Trigger Nemesis attack
>   4. Record t_attack = now()
>   5. Wait for Gaia alert → record t_detect
>   6. Wait for Hephaestus action → record t_heal
>   7. Wait for metrics normalization → record t_recover
>   8. Calculate MTTD = t_detect - t_attack
>   9. Calculate MTTR = t_recover - t_detect
>  10. Wait 5 min cooldown
>  11. Repeat 5 times
> ```

> **Expected Results (Target):**
>
> | Metric | Baseline (Manual) | Self-Healing (Auto) | Improvement |
> | --- | --- | --- | --- |
> | MTTD | 5-15 min | < 1 min | 5-15x faster |
> | MTTR | 15-30 min | < 3 min | 5-10x faster |
> | Uptime | ~90-95% | ≥ 99% | +5-10% |

> **Tham khảo:**
>
> - [plan.md](../docs/plan.md) Section 7 — KPIs
> - [plan.md](../docs/plan.md) Section 6.2 — Phase 5 War Game
