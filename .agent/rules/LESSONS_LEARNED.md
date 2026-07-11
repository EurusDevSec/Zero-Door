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

### 6. Gaia Không Detect CPU Stress trên K3d (ĐÃ KHẮC PHỤC)
**LỖI**: Prometheus cào metrics mỗi 30s. Sử dụng range vector `[30s]` hoặc `[1m]` trong query rate CPU khiến Prometheus trả về `0.000` do lệch chu kỳ.
**FIX**:
1. Đổi range vector CPU query sang **`[2m]`** ở cả Gaia và Nemesis để Prometheus luôn có tối thiểu 2 điểm dữ liệu để tính toán rate.
2. Ép buộc thời gian tấn công tối thiểu là **90 giây** để stress pod tồn tại đủ lâu qua nhiều chu kỳ cào.
**RULE**: Luôn dùng range vector `[2m]` cho rate query CPU trên K3d.

---

### 7. Stress Pod bị OOMKilled ở Cường độ HIGH (ĐÃ KHẮC PHỤC)
**LỖI**: Khi attack cường độ HIGH, Chaos Worker gọi stress-ng đòi cấp phát $> 256$MB RAM, vượt limits `256Mi` mặc định làm pod bị K8s giết ngầm ngay khi chạy.
**FIX**: Nâng resource limits của stress container trong `chaos-worker/internal/attack/cpu_stress.go` lên `1000m` CPU và `512Mi` Memory.
**RULE**: Giới hạn RAM của stress pod tối thiểu phải là `512Mi` để chịu tải HIGH.

---

### 8. Lỗi Reset không khôi phục số lượng Pods về 1 (ĐÃ KHẮC PHỤC)
**LỖI**: Hephaestus `/experiment/reset` ban đầu chỉ clear cooldown/history. Số replicas đã scale up vẫn giữ ở 2, làm hỏng kịch bản demo tiếp theo.
**FIX**: Tích hợp logic gọi Kubernetes Python Client `patch_namespaced_deployment_scale` vào trong API reset của Hephaestus để scale down toàn bộ target deployments về đúng **1 replica**.
**RULE**: Bắt buộc scale-down deployments về 1 khi bấm Reset để khôi phục Steady State.

---

### 9. Lỗi API Key Rate Limit Gemini (ĐÃ KHẮC PHỤC)
**LỖI**: Cơ chế Round Robin cũ xoay key thụ động qua mỗi request. Nếu key được chọn bị Rate Limit, request đó lập tức thất bại.
**FIX**: Viết logic loop qua danh sách tất cả API keys có sẵn trong cùng một request. Nếu một key lỗi, tự động chuyển sang thử tiếp key thứ 2 (Auto-failover).
**RULE**: Luôn gọi LLM qua loop retry/failover để tránh lỗi 500 khi một key bị Rate Limit.

---

### 10. Lỗi nghẽn Port-Forward trên Windows (ĐÃ KHẮC PHỤC)
**LỖI**: Polling rate của Dashboard quá nhanh (3s/lần) làm Windows TCP stack bị quá tải, gây lỗi `net::ERR_CONNECTION_REFUSED`.
**FIX**: Tăng chu kỳ polling của Dashboard lên **5 giây** và tích hợp banner nhấp nháy đỏ báo mất kết nối nếu API thất bại liên tiếp 2 lần.
**RULE**: Polling rate qua Windows port-forward tối thiểu phải là 5s.

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

---

### 11. Dashboard UI — Tailwind vs Custom CSS Conflict (2026-07-10)
**LỖI**: Dùng Tailwind utility classes trực tiếp trong `updateWorkflowGraph()` (JS) để reset node classes → khi thay CSS architecture, mọi Tailwind class trong JS bị vô hiệu hóa, gây mất style node.

**FIX**: Tách ra 2 lớp CSS rõ ràng:
- Semantic classes trong `style.css` (`topo-node`, `topo-node-sub`, `node-healthy`, `node-danger`, `node-active`)
- JS chỉ toggle semantic classes, không hardcode Tailwind utilities

**RULE**: Không hardcode Tailwind utility classes trong JavaScript. Dùng CSS custom classes có tên rõ ràng.

---

### 12. Port-Forward Tự Ngắt Sau Mỗi `kubectl rollout restart` (Pattern cố định)
**HÀNH VI**: Sau khi `kubectl rollout restart deployment/nemesis`, port-forward process tự chết do pod cũ terminate → namespace closed error.

**PATTERN ĐÃ BIẾT**: Đây là hành vi bình thường — KHÔNG phải lỗi. Sau mỗi rollout, phải re-run:
```powershell
kubectl port-forward -n zero-door svc/nemesis 9092:8000 --address 127.0.0.1
```

**RULE**: Luôn restart port-forward sau mỗi `kubectl rollout restart`. Có thể dùng `start-demo.ps1` thay vì chạy tay.

---

### 13. Docker Build Với Static Files — Cần `--no-cache`
**LỖI**: `docker build` bình thường sẽ cache layer `COPY static ./static` → static files mới KHÔNG được đưa vào image.

**FIX**: Luôn dùng `docker build --no-cache` khi thay đổi `static/` files.

**RULE**: Mọi thay đổi HTML/CSS/JS của dashboard cần `docker build --no-cache` mới có hiệu lực.

---

### 14. Sập Port-Forward Frontend khi chạy POD_KILL (Đfixed)
**LỖI**: Chạy `kubectl port-forward svc/frontend 8080:80` kết nối trực tiếp đến Pod. Khi Pod bị giết (`POD_KILL`), client CLI mất kết nối và dừng hẳn port-forward, làm mất kết nối vĩnh viễn trên trình duyệt của người dùng.

**FIX**: Tạo một Kubernetes Ingress resource [target-app-ingress.yaml](file:///r:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/target-app-ingress.yaml) để map `/` vào frontend thông qua Nginx Ingress Controller có sẵn của cụm K3d. Truy cập thông qua cổng 8080 của Ingress. Khi Pod bị giết, Ingress trả về `502/503` tạm thời và tự động kết nối lại khi Pod mới READY.

**RULE**: Không bao giờ port-forward frontend trên local dev. Sử dụng Ingress native để kiểm chứng downtime thực tế.

---

### 15. Tấn công HTTP_FLOOD sai cổng dịch vụ gRPC (Đã hiểu)
**LỖI**: Chạy `HTTP_FLOOD` nhắm vào `productcatalogservice` hay `cartservice` bị treo luồng, chỉ gửi được 900 requests/90s và Gaia không phát cảnh báo.

**NGUYÊN NHÂN**: Các backend services chạy bằng giao thức gRPC trên cổng riêng biệt (ví dụ: `3550`), không chạy HTTP trên cổng `80`. Chaos Worker gửi HTTP requests vào cổng `80` mặc định nên bị timeout làm nghẽn các goroutines.

**RULE**: Chỉ dùng `HTTP_FLOOD` cho dịch vụ HTTP `frontend`. Các dịch vụ nội bộ (backend) bắt buộc phải dùng `CPU_STRESS` hoặc `POD_KILL`.

---

### 16. Kịch bản attack bị chặn do quá hạn ngạch (ResourceQuota Exceeded)
**LỖI**: Chạy `CPU_STRESS` cường độ `HIGH` (yêu cầu 1 core) báo lỗi `exceeded quota: target-app-quota, requested: limits.cpu=1, used: limits.cpu=2225m, limited: limits.cpu=3`.

**NGUYÊN NHÂN**: Do scale up pods trước đó chưa được thu hồi làm chiếm hết quota CPU limits của namespace `target-app` (tối đa 3 cores).

**RULE**: Luôn gọi `RESET SYSTEM` để giải phóng các Pod dư thừa về mức Steady State (1 pod) trước khi kích hoạt cuộc tấn công mới.

---

### 17. GitHub Actions Setup Python Cache Post-run Failure
**LỖI**: Job `Build Python Agent Orchestrator` liên tục bị đỏ/thất bại ở bước `Post Set up Python` khi lưu cache pip.

**NGUYÊN NHÂN**: Matrix builds chạy song song cho 3 agents ghi trùng cache key hoặc gặp lỗi ghi từ phía GitHub actions cache storage.

**RULE**: Tắt hoàn toàn cấu hình `cache: 'pip'` trong file `ci.yml` đối với các dự án dependencies dung lượng nhỏ để đảm bảo pipeline luôn chạy nhanh và xanh ổn định.

