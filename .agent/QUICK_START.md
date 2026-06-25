# 🚀 QUICK_START.md — Agent Mới Đọc Đầu Tiên
> *Đọc file này TRƯỚC, sau đó đọc CONTEXT.md, PLAN.md, LESSONS_LEARNED.md*

---

## Bước 1 — Hiểu project trong 60 giây

**Zero Door** = Hệ thống AI tự phòng thủ Kubernetes.
- 3 agents Python: **Gaia** (detect) → **Hephaestus** (heal) ← **Nemesis** (attack)
- Target: Google Online Boutique trên K3d local cluster
- Phases 1–5 **XONG**. Phase 6 (Cloud) chưa bắt đầu.

---

## Bước 2 — Kiểm tra môi trường

```powershell
# 1. Docker Desktop phải đang chạy
docker ps | Select-Object -First 3

# 2. K3d cluster
kubectl cluster-info
kubectl get nodes

# 3. Tất cả pods
kubectl get pods -A --no-headers | Where-Object { $_ -notmatch "Running|Completed" }
# Không có output = tất cả đang chạy tốt
```

---

## Bước 3 — Start Port Forwards (nếu cần làm experiments)

```powershell
# Chạy trong 3 terminal riêng hoặc background:
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door
kubectl port-forward svc/nemesis 9092:8000 -n zero-door
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring

# Verify:
Invoke-RestMethod "http://localhost:9091/healthz"  # Hephaestus
Invoke-RestMethod "http://localhost:9092/healthz"  # Nemesis
```

---

## Bước 4 — Git status

```powershell
git log --oneline -5
git status
```

---

## Bước 5 — Đọc theo thứ tự

1. `.agent/rules/PLAN.md` — Phase status & roadmap
2. `.agent/rules/LESSONS_LEARNED.md` — Lỗi cần tránh (ĐỌC KỸ)
3. `.agent/workflows/SESSION_MEMORY.md` — State hiện tại & Phase 6 checklist
4. `docs/runbooks/phase5_runbook.md` — Kết quả experiments đầy đủ

---

## Bước 6 — Nếu làm Phase 6

Xem checklist tại `.agent/workflows/SESSION_MEMORY.md` → Section "Phase 6 Checklist"

Tạo `docs/runbooks/phase6_runbook.md` tương tự format của phase5_runbook.md sau khi hoàn thành.

---

## ⚡ Commands Hay Dùng

```powershell
# Rebuild agent sau khi sửa code
docker build -t hephaestus:latest agent-orchestrator/hephaestus/
k3d image import hephaestus:latest -c zero-door
kubectl rollout restart deployment/hephaestus -n zero-door
kubectl rollout status deployment/hephaestus -n zero-door --timeout=90s

# Kill port-forwards cũ
Get-Process kubectl | Stop-Process -Force; Start-Sleep 3

# Reset experiment state
Invoke-RestMethod "http://localhost:9091/experiment/reset" -Method POST

# Run experiments
$env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"
python infrastructure/scripts/experiment_runner_direct.py --scenario ALL --mode BOTH --runs 5

# Generate charts
python infrastructure/scripts/analysis.py

# Check Hephaestus heal history
Invoke-RestMethod "http://localhost:9091/heal/history" | ConvertTo-Json -Depth 3
```

---

## 🔴 JANGAN DILAKUKAN (Không được làm)

| ❌ Sai | ✅ Đúng |
|--------|--------|
| Thêm Java/Maven vào agents | Tất cả agents là Python FastAPI |
| `go build -o chaos-worker` | `go build -o chaos-worker-bin` |
| Port-forward Kafka | Dùng `/heal/trigger` REST API |
| `requests.post(timeout=8)` cho `/heal/trigger` | Dùng background thread, timeout=180 |
| `Path(__file__).parent.parent / "docs"` trong analysis.py | `.parent.parent.parent / "docs"` |
| Quên gọi `/experiment/reset` trước run | Luôn reset trước mỗi run |
