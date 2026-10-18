# ZER-35 — Bước namespace/quota (B.5 bước 1)

**Kết quả: PASS cho phạm vi namespace/quota/LimitRange.** Ba namespace, ba ResourceQuota và ba LimitRange đã được tạo và khớp file nguồn (`kubectl diff` exit 0 cho cả 6 file). Không có workload nào được tạo, nên usage CPU/RAM gần như không đổi. Quota là trần admission, không phải RAM được cấp ngay, và chưa chứng minh full lab vừa máy. Dừng ở đây để Codex review.

Người thực hiện: Claude Code. Người review: Codex. Người chốt: Hoàng. Yêu cầu thực thi: Hoàng, 18/10/2026, theo mục "Kết luận thực thi giới hạn" trong [codex-review.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md). Kế hoạch gốc: [claude-review-and-resource-profile.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/claude-review-and-resource-profile.md) B.5 bước 1.

## 1. Phạm vi và revision

- Thời gian: 18/10/2026, 11:55:18 – 11:57:11 +07:00 (Asia/Saigon). Shell: Git Bash; không dùng PowerShell.
- `main`, HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`; staged rỗng. Working tree dirty như trước (migration Bash, evidence, handoff); không phải thay đổi của lượt này.
- Thao tác thay đổi lab duy nhất: `bash infrastructure/scripts/setup-phase1.sh --component namespaces`.
- **Không làm:** component khác hoặc `all`, Helm, tăng quota, sửa file cấu hình, recreate/xóa tài nguyên, đổi WSL/Docker/kubeconfig, commit/push, Linear.
- File ghi: file này; một đoạn bàn giao ngắn trong `docs/delivery/milestones/R0-foundations/local-lab.md` và `docs/delivery/NOW.md`.

File đầu vào (tracked, không có thay đổi chưa commit; `git status` rỗng cho hai thư mục):

| File | SHA-256 |
| --- | --- |
| `infrastructure/namespaces/zero-door.yaml` | `81f6ee38…7e20` |
| `infrastructure/namespaces/target-app.yaml` | `c0532be1…34c4` |
| `infrastructure/namespaces/monitoring.yaml` | `f4a4b9a2…bc59` |
| `infrastructure/resource-quotas/zero-door-quota.yaml` | `c1a0c040…1b94` |
| `infrastructure/resource-quotas/target-app-quota.yaml` | `0b957f96…327d` |
| `infrastructure/resource-quotas/monitoring-quota.yaml` | `61c3da94…f239` |
| `infrastructure/scripts/setup-phase1.sh` (untracked, migration) | `6cd4f2c3…b535` |
| `infrastructure/scripts/lib/common.sh` (untracked, migration) | `13da5f82…8d1b` |

## 2. Kiểm tra trước (11:55:18)

| Kiểm tra | Kết quả | Đạt |
| --- | --- | --- |
| `docker context show` | `desktop-linux` | Có |
| `docker info` | `docker-desktop`, Engine 29.8.2, 4 CPU, 7271460864 B (6,77 GiB) | Có |
| `kubectl config get-contexts k3d-zero-door` | Tồn tại; cluster `k3d-zero-door`, user `admin@k3d-zero-door`. Current-context cũng là `k3d-zero-door` | Có |
| API server của context | `https://127.0.0.1:7356` | Có |
| Node | `k3d-zero-door-server-0` và `k3d-zero-door-agent-0` Ready=True, `v1.31.5+k3s1`, tuổi 120m | Có |
| `k3d cluster list` | `zero-door` server 1/1, agent 1/1, có LB | Có |

Không có sai lệch, nên tiếp tục. Mọi truy vấn có `timeout` 15–25s và `--request-timeout=10s`; không lệnh nào timeout.

## 3. Inventory và số đo trước (11:55:39)

- Namespace: chỉ `default`, `kube-node-lease`, `kube-public`, `kube-system`. `zero-door`, `target-app`, `monitoring` chưa tồn tại.
- ResourceQuota và LimitRange toàn cluster: không có.
- Pod: chỉ `coredns`, `local-path-provisioner`, `metrics-server` trong `kube-system`, Running, 0 restart.
- PV/PVC: không có. Event Warning: không có.

Không có hiện trạng ngoài dự kiến, nên không có diff cần nêu trước khi apply.

## 4. Lệnh thực thi

```text
11:55:50  timeout 180 bash infrastructure/scripts/setup-phase1.sh --component namespaces
```

Output (đầy đủ, không có secret):

```text
NAME                     STATUS   ROLES                  AGE    VERSION
k3d-zero-door-agent-0    Ready    <none>                 120m   v1.31.5+k3s1
k3d-zero-door-server-0   Ready    control-plane,master   120m   v1.31.5+k3s1
namespace/zero-door created
resourcequota/zero-door-quota created
limitrange/zero-door-limits created
namespace/target-app created
resourcequota/target-app-quota created
limitrange/target-app-limits created
namespace/monitoring created
resourcequota/monitoring-quota created
limitrange/monitoring-limits created
NAMESPACE     NAME                                      READY   STATUS    RESTARTS   AGE
kube-system   coredns-ccb96694c-d4x4k                   1/1     Running   0          120m
kube-system   local-path-provisioner-5cf85fd84d-fr4lq   1/1     Running   0          120m
kube-system   metrics-server-5985cbc9d7-s6h86           1/1     Running   0          120m
Infrastructure component completed: namespaces. Verify its functional behavior separately.
```

Exit 0, 3 giây, kết thúc 11:55:53. Bảng node ở đầu là output của `zd_preflight`. Tất cả 9 đối tượng đều `created`, không có `configured` hay `unchanged`, khớp inventory trước.

## 5. Kiểm tra sau (11:56:04)

**Namespace** (cả ba `Active`):

| Namespace | Labels |
| --- | --- |
| `zero-door` | `project=zero-door`, `component=agents`, `monitoring=enabled` |
| `target-app` | `project=zero-door`, `component=target`, `attack-target=true`, `monitoring=enabled` |
| `monitoring` | `project=zero-door`, `component=observability`, `attack-target=false`, `monitoring=enabled` |

Ngoài ra mỗi namespace có label hệ thống `kubernetes.io/metadata.name`.

**ResourceQuota** (`status.hard`; `status.used` đều bằng 0):

| Quota | requests.cpu | requests.memory | limits.cpu | limits.memory | pods | PVC |
| --- | --- | --- | --- | --- | --- | --- |
| `zero-door/zero-door-quota` | 1 | 1Gi | 3 | 3Gi | 10 | 3 |
| `target-app/target-app-quota` | 1500m | 2Gi | 3 | 4Gi | 20 | 3 |
| `monitoring/monitoring-quota` | 4 | 6Gi | 10 | 10Gi | 15 | 5 |

`target-app` vẫn có `limits.cpu` = 3, đúng yêu cầu giữ cấu hình hiện tại (không tăng lên 4).

**LimitRange** (type `Container`):

| LimitRange | default | defaultRequest | max | min |
| --- | --- | --- | --- | --- |
| `zero-door/zero-door-limits` | 300m / 256Mi | 50m / 64Mi | 1 / 1Gi | 25m / 32Mi |
| `target-app/target-app-limits` | 200m / 256Mi | 50m / 64Mi | 1 / 1Gi | 25m / 32Mi |
| `monitoring/monitoring-limits` | 500m / 512Mi | 100m / 128Mi | 3 / 3Gi | 50m / 64Mi |

**Khớp file nguồn:** `kubectl --context k3d-zero-door diff -f <file>` exit 0 (không có khác biệt) cho cả 6 file trong mục 1.

**Đối tượng trong ba namespace mới:** chỉ có quota, LimitRange và hai đối tượng Kubernetes tự tạo (`configmap/kube-root-ca.crt`, `serviceaccount/default`). Không có Pod, Deployment, Service, PVC, Secret, Role hay NetworkPolicy.

**Còn lại:** pod `kube-system` giữ nguyên (0 restart); không có PV/PVC; không có event Warning. Sau lệnh, current-context vẫn là `k3d-zero-door` và Docker context vẫn là `desktop-linux`.

## 6. Số đo trước và sau

| Số đo | Trước (11:55:39) | Sau (11:56:04) |
| --- | --- | --- |
| `kubectl top nodes`, agent | 50m / 138Mi | 49m / 136Mi |
| `kubectl top nodes`, server | 50m / 391Mi | 53m / 388Mi |
| `docker stats` (server + agent + serverlb + tools) | 391,6 + 138,7 + 7,8 + 2,5 ≈ 540,6 MiB | 389,2 + 136,4 + 8,0 + 2,5 ≈ 536,1 MiB |
| WSL `MemAvailable` | 5860468 kB (5,59 GiB) | 5827124 kB (5,56 GiB) |
| WSL `Cached` | 1906300 kB | 1906312 kB |
| WSL swap trống | 2 GiB | 2 GiB |
| PSI memory `some avg60` | 0,00 | 0,00 |
| PSI CPU `some avg60` | 0,15 | 0,17 |
| loadavg 1 phút | 0,32 | 0,19 |
| Host Windows `MemFree` | 3340604 kB (3,19 GiB) | 3301224 kB (3,15 GiB) |

Chênh lệch nằm trong mức dao động bình thường (khoảng 30–40 MiB, có thể do tiến trình khác trên máy). Bước này không tạo workload nên không có tác động tài nguyên đáng kể. Quota mới chỉ là trần admission; nó không giữ trước RAM và không nói gì về việc full stack có vừa 6,77 GiB hay không.

## 7. Trạng thái repo cuối lượt

Trước lượt, đã chụp `git status --short --untracked-files=all` và SHA-256 mọi file dirty/untracked (lưu ngoài repo, trong scratchpad của phiên). So lại lúc 11:57:11:
- HEAD vẫn `1f43ff1`; staged rỗng.
- `git status` chỉ thêm `?? docs/evidence/ZER-35/namespace-bootstrap.md`.
- Trong các file đã dirty, chỉ `docs/delivery/NOW.md` và `docs/delivery/milestones/R0-foundations/local-lab.md` đổi hash, do nối đoạn bàn giao. Mọi file khác giữ nguyên, kể cả `codex-review.md` và báo cáo Claude.
- 8 file đầu vào ở mục 1 có hash không đổi.
- `git diff --check` exit 0 (lệnh này không bao phủ file untracked). Riêng file này: 0 ký tự CR, không có khoảng trắng cuối dòng.

## 8. Kết luận và bước tiếp theo

- Đạt: 3 namespace có đúng label; 3 quota và 3 LimitRange khớp file; không có workload hay PVC; context không bị đổi.
- Chưa chứng minh: quota/LimitRange có admit đúng các chart thật hay không (mỗi chart còn phải pin/render trước, gồm cả ingress ở bước 2); sizing full stack; enforcement của NetworkPolicy (chưa apply).
- Rollback nếu cần: không thực hiện. Theo allowlist B.5, bước 1 chỉ cho phép apply lại file quota đã sửa, không xóa namespace.
- **Dừng để Codex review.** Bước tiếp theo đề xuất (chưa làm, cần quyền riêng): chuẩn bị pin version và render chart `ingress-nginx` bằng values của repo, đối chiếu resource hiệu dụng và rollback có `--kube-context`, rồi mới xin quyền chạy bước 2.
