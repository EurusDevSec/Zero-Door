# ⚠️ LESSONS_LEARNED.md — Kinh Nghiệm & Lỗi Cần Tránh
> *Tổng hợp từ toàn bộ session Phase 1–5 | Đọc bắt buộc cho agent mới*

---

## 🚨 CRITICAL MISTAKES — Đã gặp, KHÔNG lặp lại

### 1. CI/CD: Java/Maven pom.xml
**LỖI**: `agent-orchestrator/pom.xml` có dependency `spring-boot-starter-kafka` thiếu version tag → Maven build fail trên CI.

**THỰC TẾ**: Tất cả agents đã được migrate sang **Python 3.11**. CI pipeline dùng Python matrix.

**RULE**: Không bao giờ thêm Java/Maven vào agents. `ci.yml` chỉ build Python + Go.

---

### 2. Go Binary Naming Conflict
**LỖI**: `go build -o chaos-worker ./cmd/` → conflict với directory name `cmd/` trên Windows.

**FIX**: `go build -o chaos-worker-bin ./cmd/main.go`

**RULE**: Luôn dùng `chaos-worker-bin` làm output binary name trong Go build.

---

### 3. Hephaestus Cooldown Blocking Experiments
**LỖI**: Cooldown 90s per (service, action) → Run #2 không được process vì run #1 chưa hết cooldown.

**FIX**: Thêm `POST /experiment/reset` endpoint để clear cooldowns + heal_history trước mỗi run.

**RULE**: Luôn gọi `/experiment/reset` trước khi inject alert trong experiment runner.

---

### 4. Kafka Port-Forward từ Windows → K3d
**LỖI**: `kubectl port-forward svc/kafka 9093:9092` không kết nối được từ Python bên ngoài cluster vì Kafka advertised listeners là internal DNS.

**THỰC TẾ**: Kafka chỉ accessible in-cluster. Experiment runner KHÔNG dùng Kafka trực tiếp — dùng REST API của Hephaestus thay thế.

**RULE**: Không port-forward Kafka cho external access. Dùng `/heal/trigger` REST API.

---

### 5. analysis.py Path Resolution
**LỖI**: `BASE_DIR = Path(__file__).parent.parent / "docs"` → resolve thành `infrastructure/docs/` (sai).

**FIX**: `BASE_DIR = Path(__file__).parent.parent.parent / "docs"` (3 levels up từ `infrastructure/scripts/`).

**RULE**: Script ở `infrastructure/scripts/` cần `.parent.parent.parent` để tới project root.

---

### 6. Gaia Không Detect CPU Stress trên K3d
**LỖI**: Gaia dùng threshold `0.8 × 200m = 160m`. K3d single-node shared → Chaos Worker CPU pod không đẩy container metric vượt ngưỡng.

**THỰC TẾ**: Gaia KHÔNG tự detect trên K3d local. Trên production cluster (GKE/EKS) mới detect tự động.

**RULE**: Trên K3d, inject alerts trực tiếp qua `/heal/trigger`. Ghi rõ trong methodology.

---

### 7. Rich Console Unicode Error trên Windows
**LỖI**: `UnicodeEncodeError: 'charmap' codec can't encode character '✓'` với CP1258 terminal.

**FIX**: Thêm vào đầu script:
```python
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```
Hoặc set env: `$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"`

---

### 8. Hephaestus `/heal/trigger` Blocking Timeout
**LỖI**: `requests.post("/heal/trigger", timeout=8)` → timeout vì RESTART action đợi pod ready (60s).

**FIX**: Gọi trong background thread:
```python
def inject_alert_via_hephaestus(...):
    t = time.time()
    def _fire():
        requests.post(f"{HEPHAESTUS_URL}/heal/trigger", json=payload, timeout=180)
    threading.Thread(target=_fire, daemon=True).start()
    return t
```

---

### 9. Port-Forward Bị Treo Sau Pod Restart
**LỖI**: Sau `kubectl rollout restart`, port-forward cũ vẫn còn process nhưng connection bị broken → port 9091 bị occupied.

**FIX**:
```powershell
Get-Process | Where-Object { $_.ProcessName -eq "kubectl" } | Stop-Process -Force
Start-Sleep 3
# Sau đó restart tất cả port-forwards
```

---

### 10. Docker Build "Exit Code 1" Nhưng Thực Ra SUCCESS
**LỖI**: `docker build` trả về exit code 1 trong PowerShell nhưng output "DONE" → build thực sự thành công, chỉ là exit code reporting issue.

**RULE**: Kiểm tra output `naming to docker.io/library/...:latest done` — nếu có dòng này thì build OK dù exit code.

---

## ✅ BEST PRACTICES — Quy trình đúng

### Port Forwards Startup Order
```powershell
# Luôn theo thứ tự này:
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door &
kubectl port-forward svc/nemesis 9092:8000 -n zero-door &
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring &
# Kafka: KHÔNG port-forward — không cần thiết
Start-Sleep 5
# Verify
Invoke-RestMethod "http://localhost:9091/healthz"
Invoke-RestMethod "http://localhost:9092/healthz"
```

### Experiment Runner Workflow
```powershell
# 1. Reset steady state
kubectl scale deployment/frontend deployment/cartservice -n target-app --replicas=1

# 2. Reset Hephaestus state
Invoke-RestMethod "http://localhost:9091/experiment/reset" -Method POST

# 3. Chạy experiments
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
python infrastructure/scripts/experiment_runner_direct.py --scenario ALL --mode BOTH --runs 5

# 4. Generate analysis
python infrastructure/scripts/analysis.py
```

### Rebuild + Redeploy Agent
```powershell
# 1. Build Docker image
docker build -t hephaestus:latest agent-orchestrator/hephaestus/

# 2. Import vào K3d cluster
k3d image import hephaestus:latest -c zero-door

# 3. Rollout
kubectl rollout restart deployment/hephaestus -n zero-door
kubectl rollout status deployment/hephaestus -n zero-door --timeout=90s

# 4. Kill port-forwards cũ và restart
Get-Process kubectl | Stop-Process -Force
Start-Sleep 3
kubectl port-forward svc/hephaestus 9091:8000 -n zero-door
```

### Git Commit Convention
```bash
feat(phase5): description         # New feature
fix(hephaestus): description      # Bug fix
docs(phase5): description         # Documentation
refactor(ci): description         # CI/CD changes
```

---

## 🔋 Token Optimization Tips

1. **Đọc file có chọn lọc**: Chỉ view lines cần thiết, không view 500+ lines toàn bộ file mỗi lần
2. **Dùng grep_search trước view**: Tìm pattern trước, view line range sau
3. **Batch kubectl commands**: Dùng 1 command với nhiều resources thay vì nhiều commands riêng lẻ
4. **Background tasks cho long-running ops**: Experiment runner → background task, dùng `schedule` timer để check sau
5. **Không poll liên tục**: Hệ thống tự notify khi task xong — KHÔNG gọi `status` nhiều lần
6. **Commit sớm**: Sau mỗi phase milestone → commit ngay để có checkpoint
7. **Kill stuck tasks ngay**: Đừng để task timeout 90s/120s mới kill — check sau 30s nếu không có progress

---

## 🏃 Quick Cluster Health Check

```powershell
# One-liner check toàn bộ cluster
kubectl get pods -n zero-door --no-headers | ForEach-Object { Write-Host $_ }
kubectl get pods -n target-app --no-headers
kubectl get pods -n monitoring --no-headers

# Agent APIs
@("http://localhost:9091/healthz","http://localhost:9092/healthz") | ForEach-Object {
    try { $r = Invoke-RestMethod $_ -TimeoutSec 3; Write-Host "$_`: UP" -ForegroundColor Green }
    catch { Write-Host "$_`: DOWN" -ForegroundColor Red }
}
```
