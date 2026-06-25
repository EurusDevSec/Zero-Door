# 💾 SESSION_MEMORY.md — Trạng Thái Hiện Tại
> *Last updated: 2026-06-25 22:58 ICT | Phase 5 COMPLETE*

---

## 🎯 Trạng thái ngay lúc này

**Phase đang làm**: Phase 6 — Cloud Deployment & Final Report (CHƯA BẮT ĐẦU)

**Phase vừa hoàn thành**: Phase 5 — War Game Experiments ✅

**Git branch**: `main`  
**Last commit**: `ccf0492` — docs(phase5): update runbook with actual experiment results

---

## 📌 Cluster State (K3d Local)

```
Cluster name : zero-door
Docker Desktop: Required (phải bật trước khi làm việc)
```

### Namespaces & Pods:
```
zero-door   : gaia, nemesis, hephaestus, kafka-controller-0, chaos-worker
target-app  : frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart
monitoring  : prometheus-operated, grafana, elasticsearch, fluent-bit
```

---

## 📂 Files Quan Trọng Nhất

| File | Mục đích | Ghi chú |
|------|----------|---------|
| `agent-orchestrator/hephaestus/main.py` | Defender agent | Có `/heal/history`, `/experiment/reset` (mới) |
| `agent-orchestrator/gaia/main.py` | Observer agent | Poll 15s, threshold 80% CPU |
| `agent-orchestrator/nemesis/main.py` | Attacker agent | REST orchestrator |
| `infrastructure/scripts/experiment_runner_direct.py` | Phase 5 runner | **Dùng cái này** cho K3d |
| `infrastructure/scripts/analysis.py` | Chart generation | Path: `.parent.parent.parent` |
| `docs/experiments/raw_data/` | Raw CSVs | E1–E4, AUTO+MANUAL, 5 runs |
| `docs/experiments/analysis/` | Charts | 5 PNG + summary_statistics.csv |
| `docs/runbooks/phase5_runbook.md` | Phase 5 runbook | Kết quả đầy đủ |
| `.github/workflows/ci.yml` | CI/CD | Python matrix + Go |

---

## 🚀 Phase 6 — Checklist

- [ ] **6.1** Chọn cloud: GKE hoặc EKS Spot
- [ ] **6.2** Build & push Docker images lên registry
- [ ] **6.3** Provision cluster (1 node, 4vCPU/8GB min)
- [ ] **6.4** Helm install full stack
- [ ] **6.5** Re-run E1–E4 trên cloud (15 runs/scenario)
- [ ] **6.6** So sánh K3d local vs Cloud metrics
- [ ] **6.7** `docs/runbooks/phase6_runbook.md`
- [ ] **6.8** Final thesis report
- [ ] **6.9** Demo video
- [ ] **6.10** Defense slides

---

## 📊 Phase 5 Experiment Results

```
E1 CPU Stress  (cartservice): MTTD=25.6s, MTTR=1.01s, OK=100% ✅
E2 HTTP Flood  (frontend)   : MTTD=1.01s, MTTR=1.01s, OK=100% ✅
E3 Pod Kill    (frontend)   : MTTD=3.15s, MTTR=1.01s, OK=20%  ⚠️ (race condition, not a bug)
E4 Combined                 : MTTD=5.60s, MTTR=1.01s, OK=100% ✅
SLAs: MTTD<60s ✅ | MTTR<180s ✅ | Uptime≥99% ✅
```

---

## 🧩 Agent Communication Flow

```
Prometheus → Gaia ──kafka:monitoring.alerts──→ Hephaestus → K8s API (heal)
Nemesis ──kafka:attack.commands──→ ChaosWorker → target-app namespace
```
