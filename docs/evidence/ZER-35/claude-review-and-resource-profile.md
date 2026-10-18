# ZER-35 — Claude review bản Bash và đề xuất profile tài nguyên lab

**Trạng thái báo cáo: bản sửa lần 1 theo [Codex review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md) CR-01–CR-05 (18/10, 11:39–). Trạng thái từng mục và bằng chứng còn thiếu ở mục E. Chờ Codex review tiếp. Chưa thực thi bước nào của kế hoạch; B.5 vẫn là kế hoạch, chưa phải runbook đã kiểm chứng.**

Người viết: Claude Code. Người review: Codex. Người chốt: Hoàng. Theo [handoff](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/claude-lab-review-and-sizing.md) cho [ZER-35](https://linear.app/zero-door/issue/ZER-35/khoi-phuc-lab-tu-inventory-dja-kiem-chung) (thuộc ZER-6).

## 0. Phạm vi, revision và giới hạn

- Bắt đầu 2026-10-18 10:42:43 +07:00 (Asia/Saigon). Shell: Git Bash 5.2.26; không dùng PowerShell.
- `main`, HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`, khớp HEAD Codex ghi trong handoff.
- Dirty đầu phiên: 31 file tracked bị sửa, 7 file `.ps1` bị xóa, 16 file untracked (gồm 7 `.sh`, `lib/common.sh`, `tests/shell/run.sh`, `.gitattributes`, `requirements-experiments.txt`, runbook Bash, ba evidence và handoff này). Toàn bộ là thay đổi có trước, không phải của Claude. Đã lưu `git status --short --untracked-files=all` và SHA-256 của mọi file dirty ra scratchpad ngoài repo để so cuối phiên.
- **Linear:** chưa đọc live ZER-35/ZER-34. Phiên Claude không có kết nối `linear_zero_door` đã cấu hình; công cụ Linear sẵn có trong phiên chưa được xác minh thuộc workspace `zero-door`, và AGENTS cấm dùng connector khác chỉ vì tên có "linear". Dùng AC snapshot trong handoff; trạng thái live = chưa xác minh.
- **GitNexus:** không dùng trong lượt này. Index ở `6337b31`, cũ hơn HEAD và chưa bao phủ các file `.sh` untracked; handoff ghi analyze từng timeout. Review dựa trên đọc trực tiếp source và kiểm thử.
- **Phạm vi ghi:** chỉ file này; sau khi xong, nối một đoạn ngắn vào `docs/delivery/milestones/R0-foundations/local-lab.md` và con trỏ vào `docs/delivery/NOW.md`. Không thêm test/probe vào `tests/shell/`. Không sửa source/config vận hành.
- **Không làm:** start/stop/recreate cluster, apply/Helm install, build/import/rollout image, prune/xóa volume, đổi WSL/Docker/kubeconfig, chạy attack/heal/reset, gọi LLM/cloud, commit/push, cập nhật Linear.

## A. Review độc lập bản chuyển Bash

### A.1 Phạm vi đã đọc và kiểm chứng

Đã đọc toàn bộ: `start-demo.sh`, `rebuild-nemesis.sh`, `infrastructure/scripts/setup-phase{1,3,4,5}.sh`, `recreate-cluster.sh`, `lib/common.sh`, `requirements-experiments.txt`, `tests/shell/run.sh`, `.gitattributes`; diff của `.github/workflows/ci.yml`, `.gitignore`, `agent-orchestrator/nemesis/static/app.js`. Đối chiếu thêm `experiment_runner.py` (cờ/env mà wrapper phase5 dùng), các manifest/values được script apply, `docs/runbooks/bash-tooling.md` và hai evidence ZER-35.

Kiểm chứng offline do Claude tự chạy (không kế thừa PASS của Codex):

| Kiểm tra | Kết quả |
| --- | --- |
| `bash -n` trên 10 file `.sh` | 10/10 exit 0 |
| CRLF/BOM trong 10 file `.sh` | 0 dòng CR, không BOM |
| `bash tests/shell/run.sh` (10:44:23) | 21/21 PASS, exit 0, 22,5s; thư mục tạm `scratch/bash-tests.*` đã tự dọn |
| `node --check agent-orchestrator/nemesis/static/app.js` | exit 0; diff chỉ đổi chuỗi cảnh báo |
| ShellCheck, yamllint | Không có trong PATH; chưa chạy, không cài |

Phần đã xác nhận đúng khi đọc code: mọi `kubectl`/`helm` trong entry point đi qua `--context=k3d-zero-door`/`--kube-context` (`lib/common.sh:44-45`); đường dẫn host đổi bằng `cygpath -m` (`:26-32`) và tắt tự đổi đối số MSYS (`:15`); Secret Nemesis có sẵn được giữ, lỗi API không bị hiểu là Secret vắng (`:96-118`); xóa cluster cần đúng cờ `--confirm-delete-zero-door` (`recreate-cluster.sh:9-12`); port-forward bind `127.0.0.1`, chỉ kill PID con của chính phiên (`:120-145`); phase5 mặc định không cài gói, không chạy thực nghiệm (`setup-phase5.sh:3-5,77-79`); smoke ghi CSV vào `scratch/experiments/`, không trộn dataset cũ (`:61-73`).

Giới hạn: mock 21 nhóm không chứng minh chart/image tải được, rollout thật, RBAC sau deploy hay luồng mua hàng. Không chạy entry point thật nào.

### A.2 Findings

Xếp theo mức độ ảnh hưởng. Không có finding mức Critical (chưa thấy đường nào xóa nhầm dữ liệu, ghi đè Secret hay kill tiến trình lạ).

**A-F1 — Medium — `k3d cluster create` đổi current-context của kubeconfig mặc định.**
- Vị trí: `infrastructure/scripts/lib/common.sh:90`; `infrastructure/k3d-config.yaml` không có khối `options.kubeconfig`.
- Trigger: `bash infrastructure/scripts/setup-phase1.sh --component cluster` (hoặc `all`, hoặc `recreate-cluster.sh`) khi cluster chưa tồn tại.
- Impact: k3d v5.8.3 mặc định `--kubeconfig-update-default=true` và `--kubeconfig-switch-context=true` (đọc `k3d cluster create --help` lúc 10:45). Lệnh tạo sẽ chuyển current-context của mọi project khác sang `k3d-zero-door`, trái với cam kết ở `docs/runbooks/bash-tooling.md:69`. Các script ZERO DOOR không bị ảnh hưởng vì luôn chỉ định context; lệnh `kubectl` không có `--context` của project khác thì có.
- Đề xuất sửa: thêm `options.kubeconfig.switchCurrentContext: false` vào `k3d-config.yaml` (hoặc truyền `--kubeconfig-switch-context=false` ở `common.sh:90`); thêm test mock kiểm cờ này.
- Bằng chứng: help output; `kubectl config current-context` hiện là `k3d-zero-door` (10:46), phù hợp với việc lần tạo cluster sáng nay đã đổi context. Chưa xác minh: context trước lần tạo là gì.

**A-F2 — Medium — `requirements-experiments.txt` pin `kafka-python==2.0.2` không hợp với Python của máy.**
- Vị trí: `infrastructure/scripts/requirements-experiments.txt:1`; venv tạo ở `setup-phase5.sh:26-29` bằng Python của host.
- Trigger: `bash infrastructure/scripts/setup-phase5.sh --install-deps` rồi `--run-smoke`.
- Impact: host là Python 3.12.4 (10:45). kafka-python 2.0.2 có lỗi import đã biết trên Python ≥3.12 (module `six` vendored). Smoke sẽ dừng ngay khi import, có báo lỗi rõ, không tạo dữ liệu sai. Gaia đã dùng `kafka-python-ng==2.2.2` (`agent-orchestrator/gaia/requirements.txt:5`); Python global của host có `kafka-python 2.3.0`.
- Đề xuất sửa: pin một bản đã kiểm chứng import và API mà runner dùng trên Python 3.12. Không cài cả `kafka-python` và `kafka-python-ng` trong cùng env, vì hai gói dùng chung namespace import `kafka`. Pin mọi gói còn lại là tùy chọn, không bắt buộc để giải quyết lỗi này (điều chỉnh theo Codex).
- Chưa xác minh: không tạo venv, không cài gói. Kết luận dựa trên lỗi upstream đã biết, cần một lần cài thử trong venv để xác nhận.

**A-F3 — Medium — Chưa có entry point cho Boutique và Gaia; phase3 phụ thuộc bước thủ công.**
- Vị trí: `setup-phase3.sh:12` yêu cầu `deployment/frontend` có sẵn; `docs/runbooks/bash-tooling.md:65` dẫn sang lệnh thủ công trong runbook legacy.
- Impact: đường dựng từ đầu không lặp lại được chỉ bằng script. Thiếu entry point tự động **không tự** vi phạm AC "lệnh dựng lặp lại": lệnh tay được ghi đủ và kiểm chứng vẫn có thể tái lập (theo Codex). Thiếu sót cụ thể là bước restart/image identity của Gaia và lệnh HPA (đã bổ sung vào B.5). Gaia dùng image `zero-door/gaia:latest` với `imagePullPolicy: Never` (`infrastructure/manifests/gaia-deployment.yaml`), không script nào build/import/restart; build lại mà quên `rollout restart` thì pod vẫn chạy image cũ.
- Đề xuất: thêm một entry point cho target app + Gaia theo cùng pattern (context, `zd_apply`, build/import, restart, rollout status), kèm test mock. Cần Hoàng chốt vì là thêm source vận hành.

**A-F4 — Low — Script không kiểm Docker context.**
- Vị trí: `lib/common.sh:47-51` (`zd_preflight`), `:79-84`; `recreate-cluster.sh:15-16`.
- Impact: build/import và `k3d cluster delete zero-door` chạy trên Docker context đang chọn. Hiện là `desktop-linux`, nhưng script không chặn nếu context khác.
- Đề xuất: so `docker context show` với giá trị kỳ vọng (cho phép override qua biến môi trường) trước mọi thao tác thay đổi.

**A-F5 — Low — Thư mục log tạm không được dọn; kubeconfig raw có thể sót khi tiến trình bị kill cứng.**
- Vị trí: `lib/common.sh:120-131`; `setup-phase5.sh:54-55`.
- Impact: mỗi phiên để lại một thư mục `/tmp/tmp.*`. Ở nhánh smoke, file kubeconfig `--raw` (có credential cluster local) chỉ bị xóa qua trap EXIT; nếu đóng terminal hoặc kill -9 thì file còn lại. `umask 077` ít tác dụng trên NTFS.
- Đề xuất: xóa thư mục khi thoát thành công, giữ lại và in đường dẫn khi lỗi; đặt kubeconfig tạm vào thư mục riêng chỉ cho user.

**A-F6 — Low — Chart chưa pin version và cập nhật repo Helm toàn cục.**
- Vị trí: `setup-phase1.sh:28-30,33,42`.
- Impact: `kube-prometheus-stack` và `ingress-nginx` lấy bản mới nhất mỗi lần cài, nên không tái lập được; `helm repo add --force-update`/`repo update` đổi cấu hình Helm của user. Host đang dùng Helm v4.2.2: đã đọc help, `--wait` không giá trị vẫn hợp lệ (strategy `watcher`), `--force-update` vẫn có.
- Đề xuất: pin version chart đã thử thành công và ghi vào evidence.

**A-F7 — Low — Lệch phiên bản kubectl.** `kubectl` trong PATH là bản Google Cloud SDK `v1.33.5-dispatcher`, server `v1.31.5+k3s1`: lệch 2 minor, ngoài mức hỗ trợ ±1. Các lệnh đọc hôm nay chạy bình thường. Đề xuất ghi phiên bản vào evidence; đổi PATH là quyết định của Hoàng.

**A-F8 — Low — Health check Grafana có thể làm sập cả phiên tunnel.** `zd_wait_http` thử 15 lần (`lib/common.sh:155-166`); Grafana cold start chậm hơn thì `start-demo.sh` thoát và đóng mọi tunnel. Chưa tái hiện. Fail-fast là hành vi chủ ý, nên mục này là đề xuất cải thiện timeout/diagnostic khi có repro, không phải bug đã xác nhận (theo Codex).

**A-F9 — Info — Network policy controller đã khởi động; enforcement chưa kiểm chứng.** (Tiêu đề bản trước, "NetworkPolicy sẽ có hiệu lực", mạnh hơn bằng chứng; đã sửa theo Codex.) Log server lúc 02:55:01Z (09:55 +07:00) ghi "Starting network policy controller version v2.2.1". Theo nội dung manifest, `infrastructure/manifests/network-policies.yaml` chỉ cho Elasticsearch nhận ingress từ Fluent Bit và namespace `zero-door`. Muốn kết luận về enforcement phải probe cả luồng được phép lẫn luồng bị chặn. Comment ở `network-policies.yaml:4-5` (Flannel bỏ qua policy) không khớp quan sát này, nên cần sửa trong task riêng. Controller chạy chưa chứng minh từng policy được enforce đúng.

**Khoảng trống test (không phải lỗi):** mock chưa kiểm cờ switch-context của k3d, Docker context, phiên bản Python của venv, chart values thật và việc build image Gaia/target app.

## B. Profile tài nguyên và kế hoạch dựng từng nhóm

### B.1 Hiện trạng đo được (LIVE_READ_ONLY, 18/10 10:46–10:48)

| Góc nhìn | Số đo |
| --- | --- |
| Docker Engine | context `desktop-linux`, Engine 29.8.2, 4 CPU, 6,77 GiB |
| k3d | `zero-door` server 1/1, agent 1/1, LB; chỉ có 3 pod hệ thống, chưa có namespace ZERO DOOR |
| `docker stats` | server 386,7 MiB, agent 138,1 MiB, serverlb 7,6 MiB, tools 2,5 MiB → ~535 MiB; CPU 0–2,5% |
| `kubectl top nodes` | agent 43m/138Mi, server 42m/387Mi |
| Capacity mỗi node | **cả hai node đều báo 4 CPU / 7101036Ki (6,77 GiB) allocatable** |
| Container k3d | `HostConfig.Memory=0`, `NanoCpus=0`: không giới hạn riêng |
| WSL `docker-desktop` | MemTotal 6,77 GiB; MemAvailable 5,56 GiB; Cached 1,81 GiB; swap 2 GiB chưa dùng; PSI memory 0; PSI CPU some avg60 0,18; loadavg 0,25 |
| Host Windows (Git Bash `/proc/meminfo`) | Tổng 15,78 GiB; free 3,23 GiB; pagefile đã dùng ~1,28 GiB |
| Working set theo tiến trình | Chrome 2,02; claude 1,79; ChatGPT 1,34; vmmemWSL 1,29; svchost 1,26; Memory Compression 1,17; codex 0,96; node 0,67 GiB (có trang dùng chung, không cộng thành RAM độc quyền) |
| `.wslconfig` | memory=7GB, processors=4, swap=2GB (không đổi) |
| Image trong Docker | Không có image ZERO DOOR, Boutique, chart hay stack giám sát; Helm cache rỗng. Mọi image phải build/pull lại |
| K3s | `v1.31.5+k3s1`; args server chỉ `--disable traefik` và hai `--tls-san`; network policy controller đang chạy |

Hệ quả quan trọng: **scheduler thấy tổng 8 CPU / 13,5 GiB** vì hai node cùng nằm trong một VM 4 CPU / 6,77 GiB. Kubernetes sẽ không chặn overcommit; giới hạn thật chỉ đến từ WSL, nên phải đo theo nhóm và có tiêu chí dừng. Eviction của kubelet trên hai node đọc cùng một vùng nhớ chung (INFERENCE).

### B.2 Bảng workload theo cấu hình mà script/runbook dùng

Nguồn là file:dòng tại HEAD. "LR" là giá trị mặc định do LimitRange của namespace gán khi container không khai báo. Usage thực chỉ có cho cluster nền và ba pod hệ thống (B.1); **mọi workload dưới đây chưa được deploy nên cột usage là "chưa đo"**. Request/limit là khai báo, không phải RAM đang dùng.

| Namespace / workload | Replica | Request CPU/RAM | Limit CPU/RAM | JVM / ghi chú | Nguồn |
| --- | --- | --- | --- | --- | --- |
| kube-system / k3s (server+agent+LB) | 2 node | — | — | Đo: ~535 MiB, CPU ~85m | B.1 |
| kube-system / coredns, local-path, metrics-server | 1 mỗi pod | — | — | Đo: 14 / 7 / 21 MiB | B.1 |
| kube-system / ingress-nginx controller | 1 | 50m / 90Mi | 300m / 150Mi | admission webhook tắt | `helm-values/ingress-nginx-values.yaml:13-19` |
| monitoring / Prometheus server | 1 (StatefulSet) | 500m / 512Mi | 1500m / 1Gi | scrape/eval 30s, retention 3d, PVC 2Gi | `helm-values/prometheus-values.yaml:19-41` |
| monitoring / Grafana | 1 | 100m / 256Mi | 1000m / 512Mi | sidecar dashboards bật; values có mật khẩu admin dạng plaintext (không chép ra đây) | `prometheus-values.yaml:45-69` |
| monitoring / operator, kube-state-metrics, node-exporter (×2 node), config-reloader, sidecar Grafana | 1 / 1 / 2 / 1 / 1–2 | **UNKNOWN** (LR 100m / 128Mi chỉ áp khi container không khai báo) | **UNKNOWN** (LR 500m / 512Mi như trên) | Chart chưa pin version nên chưa biết default, sidecar, init, hook hay job admission. Chưa render | `resource-quotas/monitoring-quota.yaml:27`+ |
| monitoring / Elasticsearch 8.13.0 | 1 | 100m / 512Mi | 1 / 1Gi | heap Xms256m/Xmx512m; init container theo LR; PVC; `vm.max_map_count`=262144 trong WSL (đo 10:48) | `logging/elasticsearch.yaml:38,44` |
| monitoring / Fluent Bit | DaemonSet ×2 | 50m / 64Mi | 200m / 256Mi | đọc mọi `/var/log/containers/*.log`, Mem_Buf_Limit 5MB | `logging/fluent-bit.yaml:30,33,90` |
| zero-door / Kafka (KRaft combined) | 1 | 100m / 256Mi | 500m / 768Mi | **Xung đột cấu hình (CR-02):** repo không đặt heap. Default upstream 29.3.2 có `heapOpts` và `controller.heapOpts` cùng là `-Xmx1024m -Xms1024m`, lớn hơn limit 768Mi. Chưa quan sát OOM thật. PVC 2Gi từ `volumeClaimTemplates`; image `bitnamilegacy` | `helm-values/kafka-values.yaml:12-35`; upstream `values.yaml:149,527` |
| zero-door / Kafka JMX exporter | sidecar | preset `micro`: 250m / 256Mi | preset `micro`: 375m / 384Mi | Preset của chart thắng LR vì container có khai báo resources (bản trước tính theo LR là sai). ServiceMonitor bật → cần CRD của Prometheus trước | `kafka-values.yaml:85-94`; upstream `values.yaml:1968`; common 2.20.2 |
| zero-door / Kafka provisioning Job | 1 pod, chạy theo hook `post-install,post-upgrade` | preset `micro`: 250m / 256Mi (ước tính hiệu dụng) | preset `micro`: 375m / 384Mi | Init `wait-for-available-kafka` và container chính đều preset `micro`; request hiệu dụng của pod = max(init, tổng app). Chạy lại mỗi lần `helm upgrade` | `kafka-values.yaml:51-52`; upstream `templates/provisioning/job.yaml:16-17,51-73` |
| zero-door / nemesis | 1 | 100m / 128Mi | 500m / 512Mi | Python | `manifests/nemesis-deployment.yaml:78` |
| zero-door / hephaestus | 1 | 100m / 128Mi | 300m / 256Mi | `MAX_REPLICAS=3` | `manifests/hephaestus-deployment.yaml:82,121` |
| zero-door / gaia | 1 | 50m / 64Mi | 200m / 128Mi | `imagePullPolicy: Never` | `manifests/gaia-deployment.yaml:43` |
| zero-door / chaos-worker | 1 | 50m / 64Mi | 200m / 128Mi | Go | `manifests/chaos-worker.yaml:105` |
| target-app / currency, productcatalog, checkout, cart, frontend | 1 mỗi dịch vụ (HPA frontend, cart 1–3) | 50m / 64Mi mỗi | 200m / 256Mi mỗi | | `manifests/target-app.yaml:49,128,216,287,488`; HPA `target-app-hpa.yaml:12,32` |
| target-app / redis-cart | 1 | 70m / 200Mi | 125m / 256Mi | | `target-app.yaml:373` |
| target-app / shipping, email, payment | 1 mỗi | 30m / 64Mi mỗi | 100m / 128Mi mỗi | | `manifests/target-app-addons.yaml:47,125,201` |
| target-app / pod tác động tài nguyên do worker tạo khi có lệnh | 0 lúc nghỉ | 100m / 64Mi | 1000m / 512Mi | chỉ tính như một bên tiêu thụ quota | `chaos-worker/internal/attack/cpu_stress.go:85-91` |

Không nằm trong đường dựng hiện tại: `recommendationservice`, `adservice`, `loadgenerator` chỉ có trong `manifests/target-app-raw.yaml` (file này không khai báo namespace). Frontend vẫn cấu hình địa chỉ hai dịch vụ đó (`target-app.yaml:463,469`). **Chưa biết luồng mua hàng có chạy được khi thiếu chúng**; phải probe trước khi coi đủ "≥5 microservices và luồng mua hàng".

**Tổng khai báo theo namespace (không phải usage):**

| Namespace | Request CPU / RAM | Limit CPU / RAM | Quota requests / limits | Nguồn quota |
| --- | --- | --- | --- | --- |
| target-app (9 dịch vụ, mỗi cái 1 replica) | 410m / 712Mi | 1425m / 1920Mi | 1500m / 2Gi · 3 / 4Gi, 20 pod | `resource-quotas/target-app-quota.yaml:13-17` |
| zero-door, lúc nghỉ (Kafka + JMX `micro` + 4 tác tử) | 650m / 896Mi | 2075m / 2176Mi | 1 / 1Gi · 3 / 3Gi, 10 pod | `zero-door-quota.yaml:18-22` |
| zero-door, khi Job provisioning chạy (thêm 1 pod `micro`) | 900m / 1152Mi | 2450m / 2560Mi | như trên | xem B.3 |
| monitoring | **UNKNOWN** — phần đã khai báo (Prometheus, Grafana, ES, Fluent Bit ×2) là 800m / 1408Mi; phần chart còn lại chưa render | **UNKNOWN** — phần đã khai báo 3,9 CPU / 3Gi | 4 / 6Gi · 10 / 10Gi, 15 pod | `monitoring-quota.yaml:13-17` |
| kube-system (ingress) | 50m / 90Mi | 300m / 150Mi | không có quota | — |

Bản trước ghi monitoring "≤1,6 CPU / ≤2,4Gi" và tổng toàn lab "~2,5 CPU / 3,9 GiB request, ~11,6 CPU / 11,1 GiB limit". Các con số đó dựa trên giả định LR cho phần chart chưa đọc, nên **không còn là cận trên** (CR-02). Hiện chỉ có thể nói: phần đã biết của lab đã có tổng limit lớn hơn RAM thật của VM (6,77 GiB); tổng đầy đủ là UNKNOWN cho tới khi render chart. Scheduler thấy 8 CPU / 13,5 GiB (B.1) nên sẽ không chặn overcommit theo tổng. Kết luận đó **không** có nghĩa mọi pod chắc chắn được xếp: scheduler vẫn xét từng node, affinity/anti-affinity, taint và port. Vì vậy phải dựa vào **usage đo được** và kết quả admission thực tế, không dựa vào quota hay limit.

### B.3 Quota có đủ cho rollout, replica dự phòng và đỉnh phục hồi không

Tính trên khai báo; đây là kiểm tra admission của quota, chưa phải RAM thật.

**Topology dùng để tính (CR-03).** Bảng dưới có hai profile khác nhau. Dòng "Nền" ứng với profile **khôi phục nền**, gồm 9 dịch vụ, mỗi dịch vụ 1 replica và **không có HPA**; đây là đúng thứ bước 4 của B.5 tạo ra. Các dòng từ "HPA" trở xuống chỉ đúng khi đã apply thêm `infrastructure/manifests/target-app-hpa.yaml`. Runbook legacy (`docs/runbooks/2026-10-09-legacy-demo-restart.md:185-193`) và bản B.5 trước đều không có lệnh này. HPA vì vậy là **deferred** trong profile khôi phục nền; profile thí nghiệm chưa được khóa. Khi chưa có quyết định HPA thì không gọi topology nền là profile thí nghiệm.

| Tình huống trong `target-app` | Limit CPU / RAM | So với quota 3 CPU / 4Gi |
| --- | --- | --- |
| Nền: 9 dịch vụ × 1 replica (profile khôi phục nền, không HPA) | 1425m / 1920Mi | Đủ |
| Chỉ khi đã apply HPA: frontend + cart lên 3 (thêm 4 pod) | 2225m / 2944Mi | Đủ |
| Thêm 1 pod surge khi rollout | 2425m / 3200Mi | Đủ |
| Thêm 1 pod tác động tài nguyên (limit 1000m / 512Mi) | **3425m** / 3712Mi | **Vượt CPU** → API từ chối tạo pod |
| Đối chiếu Codex: HPA tối đa + pod tác động, chưa có surge | 3225m / 3456Mi | Vượt CPU |
| Không HPA: nền + 1 surge + 1 pod tác động | 2625m / 2688Mi | Đủ |
| Hephaestus scale thêm dịch vụ không có HPA (tối đa 3 replica mỗi deployment) | tăng thêm | Có thể vượt sớm hơn |

Hệ quả: nếu bật HPA và HPA đã scale tối đa, pod tác động tài nguyên tiếp theo sẽ bị quota chặn. Worker ghi `FAILED` (`cpu_stress.go:108-115`) nên lỗi không bị giấu. Dù vậy, lượt thực nghiệm đó mất tác động vì quota, không phải vì hệ phòng thủ.

**HPA và healer (CR-03, INFERENCE từ cách HPA hoạt động; chưa thử).** Hephaestus xử lý `SCALE_UP` bằng cách patch `spec.replicas` của Deployment (`agent-orchestrator/hephaestus/main.py:177-197`). Nếu frontend/cart có HPA, HPA sẽ tính lại số replica theo metric và có thể ghi đè hành động của healer. Ngưỡng của hai bên cũng khác nhau, xem đoạn KPI bên dưới. Trước khi khóa profile thí nghiệm cần chốt hai điều trong protocol:
- profile có HPA hay không;
- cấu hình đối chứng (ví dụ healer bỏ qua Deployment có HPA, hoặc so sánh có/không HPA).

Không bật hoặc tắt HPA giữa các lượt chỉ để kết quả đẹp hơn.

**Quota `zero-door` (đã tính lại theo CR-02, INFERENCE tới khi render chart):**
- Bước 6 (Kafka cài khi chưa có tác tử): Kafka + JMX + Job = 600m / 768Mi request, đủ quota 1 / 1Gi.
- Lúc nghỉ, khi đủ bốn tác tử: 650m / 896Mi, đủ.
- Chạy lại `--component kafka` (tức `helm upgrade`) sau khi đã có tác tử: hook post-upgrade tạo Job, đẩy request lên 900m / 1152Mi, **vượt `requests.memory` 1Gi**. Pod Job sẽ bị từ chối và `helm --wait` có thể thất bại.
- `setup-phase3.sh:17-20` restart chaos-worker và nemesis. Nếu RollingUpdate tạo surge pod (mặc định maxSurge 25%, làm tròn lên 1), request lúc rollout khoảng 960Mi khi Gaia đã chạy. Nếu Hephaestus cũng đã chạy (chạy lại phase3 sau phase4) thì khoảng 1088Mi, **vượt 1Gi**. Khi đó rollout có thể đứng tới timeout 120s.

Bản trước ghi quota "đủ cho cài Kafka và rollout" là quá chắc, vì đã tính JMX theo LR 64Mi. Một mô hình local chạy trong `zero-door` (manifest Nemesis có biến `OLLAMA_BASE_URL` trỏ service trong namespace này) chắc chắn không vừa quota 1Gi request.

**Kafka heap (CR-02).** Đã đọc nguồn upstream qua web lúc 11:40, chỉ in ra stdout, không tải vào Helm cache:
- `values.yaml` tag `kafka/29.3.2`: `heapOpts` (dòng 149) và `controller.heapOpts` (dòng 527) đều là `-Xmx1024m -Xms1024m`.
- `templates/controller-eligible/statefulset.yaml:163-164`: biến `KAFKA_HEAP_OPTS` lấy `coalesce .Values.controller.heapOpts .Values.heapOpts`. Vì `controller.heapOpts` có giá trị mặc định khác rỗng, **chỉ đặt `heapOpts` ở cấp gốc sẽ không có tác dụng; phải đặt `controller.heapOpts`**.
- Với limit 768Mi, heap 1024m là xung đột cấu hình cần sửa trước bước 6. Chưa quan sát OOM thật.
- Giá trị heap phải chừa chỗ cho bộ nhớ native/off-heap của JVM (metaspace, thread stack, direct buffer) và page cache trong container. Không chỉ chọn "nhỏ hơn limit trên giấy". Con số cụ thể chỉ chốt sau khi render và đo; khoảng 384–512 MiB trong B.4 chỉ là điểm khởi đầu để đo.

Phần chưa kiểm được: Chart.lock ghi `common` 2.20.2 và `zookeeper` 13.4.3; chưa render toàn bộ template bằng values của repo, nên chưa có danh sách đầy đủ container/hook/resource hiệu dụng; chưa có digest của chart OCI.

**Mẫu số cho KPI "CPU target app >80%" (P179) — đề xuất định nghĩa, chưa phải quyết định (CR-04).** Bản trích P179 chỉ ghi CPU target app tăng >80%, không nói mẫu số. SCOPE yêu cầu định nghĩa mẫu số tại R0-T01-S02/R1. Bản trước viết "mẫu số phải là limit" là vượt thẩm quyền của báo cáo sizing; câu đó được rút lại. Hiện có ba đại lượng khác nhau trong repo:

| Đại lượng | Định nghĩa | Ví dụ frontend (request 50m, limit 200m) | Nguồn |
| --- | --- | --- | --- |
| CPU cores | `rate(container_cpu_usage_seconds_total[w])` của container mục tiêu | 160m | `gaia/main.py:149` (w = 2m) |
| % theo request | cores / request | 160m = 320%; HPA nhắm 70% = 35m | `target-app-hpa.yaml:14-19,34-39` |
| % theo limit | cores / limit | 160m = 80% | Gaia hardcode 0,200 (redis 0,125) tại `gaia/main.py:159-160`; đây là implementation cũ, không định nghĩa KPI |

Đề xuất để khóa tại issue scope/measurement:
- ghi đủ cả ba giá trị (cores, request, limit) và công thức % đã chọn cho từng container mục tiêu;
- áp vào đúng container của dịch vụ bị tác động; không tính CPU của pod tác động tài nguyên thay CPU app;
- không chỉnh request/limit chỉ để đạt KPI.

Lượt này không sửa detector.

**Ước lượng usage khi chạy đủ (INFERENCE, dựa trên kinh nghiệm cấu hình tương tự; phải đo lại theo B.5).** Đây là estimate để tổ chức đo, không phải acceptance và không chứng minh full stack vừa máy (CR-02):

| Nhóm | Ước lượng RAM |
| --- | --- |
| k3s nền + Docker/containerd | ~0,55 GiB (đo) + ~0,17 GiB (dockerd/containerd theo inventory 09:45) |
| Prometheus + Grafana + operator/KSM/node-exporter | 0,6 – 1,2 GiB |
| Elasticsearch + Fluent Bit | 0,7 – 1,0 GiB |
| Kafka | 0,4 – 0,77 GiB (bị chặn bởi limit) |
| ingress-nginx | 0,1 – 0,15 GiB |
| Boutique 9 dịch vụ | 0,4 – 0,7 GiB |
| Bốn tác tử + worker | 0,25 – 0,4 GiB |
| **Tổng ổn định** | **~3,2 – 4,9 GiB** trên 6,77 GiB của VM |
| Đỉnh cộng thêm | HPA/scale +0,1–0,3; pod tác động tối đa 0,5; pod surge khi rollout; **build image Go/Python có thể 1–2 GiB** (BuildKit) |

### B.4 Profile đề xuất

**Giữ nguyên WSL `memory=7GB`, `processors=4`, `swap=2GB`.** Lý do:
- Ước lượng ổn định 3,2–4,9 GiB còn chừa 1,9–3,6 GiB cho page cache, pull image và đỉnh phục hồi.
- Hạ xuống 6 GB sẽ còn quá ít chỗ khi build image hoặc khi ES/Kafka tăng.
- Tăng lên 8 GB trở lên sẽ lấn RAM của Windows: hiện desktop app đã chiếm khoảng 6–7 GiB working set (Chrome, hai ứng dụng AI, Codex, node) và Windows đã dùng Memory Compression 1,17 GiB cùng pagefile 1,28 GiB.

**Ngân sách host (15,78 GiB):** Windows và dịch vụ hệ thống ~3–3,5 GiB (INFERENCE từ svchost/Memory Compression) + WSL tối đa 7 GiB → còn khoảng 5,3–5,8 GiB cho ứng dụng desktop. Mức dùng hiện tại vượt con số này, nên khi WSL dùng gần hết trần thì Windows sẽ phải nén và đẩy trang ra đĩa.

**Hai chế độ:**

| Chế độ | Điều kiện | Không được đổi |
| --- | --- | --- |
| Chuẩn bị local (dựng, debug, build) | Desktop app mở bình thường; build image khi stack giám sát chưa lên hoặc khi đang không đo; đo sau mỗi nhóm | Giữ đủ 9 dịch vụ Boutique, giám sát, log, Kafka, ba tác tử |
| Thí nghiệm đầy đủ (pilot/formal) | Đóng ứng dụng AI desktop không dùng, giảm tab Chrome, không build image hay index IDE trong lúc chạy; host còn trống ≥2 GiB và WSL `MemAvailable` ≥1,5 GiB khi stack chạy đủ | Không đổi scrape interval, retention, limit ứng dụng hay số dịch vụ giữa các lượt; mọi thay đổi phải ghi vào protocol trước pilot |

**Thay đổi cấu hình đề xuất (chưa làm, cần Hoàng chốt):**
1. `infrastructure/resource-quotas/target-app-quota.yaml:16`: tăng `limits.cpu` từ 3 lên 4. Chỉ cần khi profile thí nghiệm bật HPA; khi đó HPA tối đa + một pod surge + một pod tác động (3425m) mới cùng được admit. Profile khôi phục nền không cần (2625m, B.3), nên không phải điều kiện của bước 1. Tăng quota **không** thêm CPU thật: VM vẫn có 4 vCPU, nên phải đo tranh chấp CPU bằng PSI. Khi khóa profile phải tính lại với HPA, surge, pod tác động và dịch vụ bổ sung (nếu có).
2. `infrastructure/helm-values/kafka-values.yaml`: đặt `controller.heapOpts` (đúng key theo template, B.3) với giá trị chừa chỗ cho native/off-heap. 384–512 MiB chỉ là điểm khởi đầu để render và đo. Cân nhắc đặt `metrics.jmx.resources` và `provisioning.resources` tường minh để quota `zero-door` không phụ thuộc preset (B.3). Mọi giá trị chỉ chốt sau khi render chart.
3. Các sửa ở A-F1, A-F2, A-F4, A-F5 và pin version chart (A-F6).

**Ảnh hưởng của sampling/retention hiện có — feasibility MTTD chưa xác minh (CR-05).** Độ trễ phát hiện CPU có ít nhất ba thành phần:
- scrape 30s (`prometheus-values.yaml:41`);
- Gaia poll 15s (`gaia-deployment.yaml:39-40`);
- **cửa sổ trung bình 120s** của `rate(...[2m])` (`gaia/main.py:149`). Bản trước bỏ sót thành phần này.

Ví dụ toán học lý tưởng (không phải số đo Prometheus): CPU nhảy từ 0 lên 100% limit thì trung bình trên cửa sổ 120s chỉ vượt 80% sau hơn 0,8 × 120 = 96s. Thực tế còn sampling, extrapolation và lệch pha giữa scrape và poll. Vì vậy câu cũ "vẫn đo được ngưỡng <60s" được rút lại. Với cấu hình hiện tại, **không thể hứa MTTD <60s** cho phát hiện CPU.

Việc cần làm trước khi chọn window/cadence:
- định nghĩa mốc onset (thời điểm tác động bắt đầu) và mốc detect (alert được publish);
- đo end-to-end độc lập trong pilot;
- nếu đổi window hay cadence thì đổi qua revision của protocol, không đổi giữa một loạt thí nghiệm.

Fluent Bit thu log mọi container và ES không có chính sách xóa index, nên dung lượng đĩa sẽ tăng dần; cần một chính sách dọn index sau này, không tắt log vì Gaia cần ES để phát hiện SQLi.

**LLM:** profile này không chừa chỗ cho inference local bên trong WSL. Một model nhỏ cỡ 3B cần khoảng 2 GiB trở lên (roadmap cũ ghi riêng weights ~1,9 GB). Nơi chạy LLM (API hay model trên host ngoài WSL) vẫn là quyết định riêng của R0-T03; không bỏ LLM khỏi scope.

**Nếu đo thực tế cho thấy không vừa:** đưa các lựa chọn sau cho Hoàng, không tự mở cloud:
- (a) giảm thêm ứng dụng desktop trong chế độ thí nghiệm;
- (b) tăng WSL lên 8 GB kèm điều kiện (a);
- (c) chuyển k3d về một node (tiết kiệm khoảng 140 MiB theo số đo agent, nhưng đổi topology và phải dựng lại cluster);
- (d) giảm heap ES (ảnh hưởng khả năng giữ log);
- (e) chạy trên cloud (đã hoãn, cần quyết định riêng về chi phí).

### B.5 Trình tự dựng từng nhóm (kế hoạch, chưa thực thi)

Cluster `zero-door` đã có và truy cập được, nên **không chạy nhánh `--component cluster` hay `recreate`**. A-F1 chỉ cần sửa trước lần tạo cluster sau.

**Bộ đo dùng sau mỗi bước** (chỉ đọc, ghi timestamp và giữ nguyên lỗi):

```bash
date -Iseconds
kubectl --context k3d-zero-door get pods -A -o wide --request-timeout=10s
kubectl --context k3d-zero-door top nodes --request-timeout=10s
kubectl --context k3d-zero-door top pods -A --request-timeout=10s
kubectl --context k3d-zero-door get events -A --field-selector type=Warning --request-timeout=10s
kubectl --context k3d-zero-door describe resourcequota -A --request-timeout=10s
docker stats --no-stream
wsl -d docker-desktop -- sh -c 'grep -E "MemAvailable|^Cached" /proc/meminfo; cat /proc/pressure/memory /proc/pressure/cpu'
grep -E "MemTotal|MemFree" /proc/meminfo
```

**Tiêu chí dừng chung:**
- WSL `MemAvailable` < 1 GiB kéo dài 2 phút;
- PSI memory `some avg60` > 10;
- có pod OOMKilled, CrashLoopBackOff hoặc số restart tăng;
- Helm `--wait` hoặc `rollout status` hết thời gian;
- quota từ chối tạo pod;
- host còn trống < 1 GiB và Windows đẩy trang ra đĩa.

**Khi dừng — chính sách gỡ có giới hạn (CR-01).** Bản trước gợi ý `kubectl delete -f <file>`. Gợi ý đó **bị rút lại**: `infrastructure/logging/elasticsearch.yaml` chứa cả PVC `elasticsearch-data` (`:66-78`). Ngoài ra:
- `nemesis-deployment.yaml` chứa Secret (`:29`);
- `fluent-bit.yaml` chứa ClusterRole/ClusterRoleBinding (`:119,128`);
- các file namespace là chính namespace.

StorageClass `local-path` có `reclaimPolicy: Delete` (đọc lúc 11:40), nên xóa PVC sẽ xóa luôn PV và dữ liệu bên dưới.

Thứ tự xử lý:
1. Dừng thêm nhóm mới.
2. Ghi số đo và lỗi đầu tiên; giữ log và events.
3. Chỉ dừng hoặc gỡ đúng workload trong allowlist dưới đây, và chỉ khi Hoàng đã chốt phạm vi đó.

Không mặc định uninstall chart, xóa namespace, ConfigMap, Secret, CRD hay PVC như một bước dọn dẹp. Không xóa cluster.

**Inventory trước và sau mỗi bước** (chỉ đọc, `-o name` không in giá trị Secret), dùng để tách tài nguyên mới tạo khỏi tài nguyên có trước:

```bash
kubectl --context k3d-zero-door get all,pvc,configmap,secret,serviceaccount,role,rolebinding,networkpolicy -n <ns> -o name --request-timeout=10s
kubectl --context k3d-zero-door get pv,storageclass --request-timeout=10s
helm --kube-context k3d-zero-door list -A
```

| Bước | Được phép khi dừng (sau khi Hoàng chốt) | Giữ lại, không gỡ mặc định |
| --- | --- | --- |
| 1 Namespace + quota | Apply lại file quota đã sửa | Namespace (xóa namespace là xóa mọi thứ bên trong) |
| 2 Ingress | `helm uninstall ingress-nginx -n kube-system`, chỉ khi `helm list` trước bước cho thấy release chưa có | Mọi thứ khác trong `kube-system` |
| 3 Giám sát | Dừng ở đây và giữ nguyên; uninstall release `prometheus` cần quyết định riêng | PVC của Prometheus, CRD (Helm không gỡ CRD), Secret/ConfigMap |
| 4 Boutique | `kubectl scale deployment/<tên> --replicas=0 -n target-app` cho đúng Deployment trong `target-app.yaml`/`target-app-addons.yaml`; các file này không có PVC (kiểm theo `kind`) | ServiceAccount, Service, Ingress, ServiceMonitor, PrometheusRule |
| 5 Log | `kubectl scale deployment/elasticsearch --replicas=0 -n monitoring`; `kubectl delete daemonset/fluent-bit -n monitoring` | **PVC `elasticsearch-data`**, ConfigMap, ClusterRole/Binding |
| 6 Kafka | Dừng ở đây; uninstall release `kafka` cần quyết định riêng | PVC của `volumeClaimTemplates` (tên thực lấy từ `get pvc`; không thấy `persistentVolumeClaimRetentionPolicy` trong template, nên retention mặc định của StatefulSet cần xác nhận khi render) |
| 7 Policy | Xóa theo tên ba NetworkPolicy: `allow-fluent-bit-to-elasticsearch`, `allow-prometheus-scraping-egress`, `allow-grafana-ingress` | — |
| 8 Gaia | `kubectl scale deployment/gaia --replicas=0 -n zero-door` | ServiceAccount, Service, image đã import |
| 9 Worker + Nemesis | Scale `deployment/chaos-worker` và `deployment/nemesis` về 0 | **Secret `nemesis-secrets`**, ConfigMap, Role/RoleBinding; tuyệt đối không `delete -f nemesis-deployment.yaml` |
| 10 Hephaestus | Scale `deployment/hephaestus` về 0 | Role/RoleBinding, ConfigMap |
| 11 Tunnel | Ctrl+C trong terminal chạy `start-demo.sh` | Mọi workload |

Đây vẫn là kế hoạch, chưa thực thi lệnh gỡ nào. Tên PVC sinh từ chart (Prometheus, Kafka) phải lấy từ inventory thật, không đoán.

| Bước | Nhóm | Lệnh Bash dự kiến | Phụ thuộc / file cần sửa trước | Kiểm chứng chức năng ngoài Ready |
| --- | --- | --- | --- | --- |
| 0 | Mốc | Bộ đo và inventory ở trên | Hoàng chốt phạm vi thực thi của bước kế tiếp (không cần chốt toàn bộ D1–D5 như một gate chung, theo Codex) | Lưu mốc để so |
| 1 | Namespace + quota | `bash infrastructure/scripts/setup-phase1.sh --component namespaces` | Kiểm trước: `docker context show` là `desktop-linux`, `kubectl config get-contexts k3d-zero-door` tồn tại (A-F4). Quota CPU 3 → 4 không cần cho profile nền (B.4) | `describe resourcequota` và `describe limitrange` khớp file; inventory trước/sau |
| 2 | Ingress | `bash infrastructure/scripts/setup-phase1.sh --component ingress` | Có mạng để tải chart/image | Service `ingress-nginx-controller` có địa chỉ; `curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/` trả 404 khi chưa có app |
| 3 | Giám sát | `bash infrastructure/scripts/setup-phase1.sh --component monitoring` | Phải đứng trước Kafka và các ServiceMonitor/PrometheusRule vì cần CRD. **Trước khi cài (CR-02):** chọn version chart cụ thể (A-F6), đọc default/dependency, render bằng `prometheus-values.yaml`, rồi lập bảng resource hiệu dụng (cả init, sidecar, hook/job) và đối chiếu LimitRange/quota `monitoring`. Ghi version/digest vào evidence | Prometheus `/-/ready`, có target scrape `up`; đo RAM Prometheus/Grafana |
| 4 | Boutique | Áp tay theo runbook legacy (chưa có script, A-F3): `kubectl --context k3d-zero-door apply -f infrastructure/manifests/target-app.yaml`, rồi `target-app-addons.yaml`, `target-app-ingress.yaml`, `target-app-monitor.yaml`, `prometheus-rules.yaml`; `kubectl --context k3d-zero-door rollout status deployment -n target-app --timeout=300s` | Bước 1–3 | **Probe luồng mua hàng** qua `http://127.0.0.1:8080/`: trang chủ, trang sản phẩm, thêm giỏ, xem giỏ, checkout. Ghi rõ có lỗi do thiếu recommendation/ad hay không. **HPA deferred (CR-03):** bước này không apply `target-app-hpa.yaml`; topology là profile khôi phục nền. Nếu profile thí nghiệm bật HPA thì đó là bước riêng: `kubectl --context k3d-zero-door apply -f infrastructure/manifests/target-app-hpa.yaml`, rồi `kubectl --context k3d-zero-door get hpa -n target-app` phải thấy TARGETS có số, không phải `<unknown>`. Bước đó cần quyết định HPA/healer ở B.3 trước |
| 5 | Log | `bash infrastructure/scripts/setup-phase1.sh --component logging` | Bước 1 | Index `zero-door-logs-*` có document mới; đo RAM ES |
| 6 | Kafka | `bash infrastructure/scripts/setup-phase1.sh --component kafka` | Bước 3 (CRD). **Trước khi cài (CR-02):** sửa `controller.heapOpts` trong `kafka-values.yaml` (bắt buộc, vì default 1024m lớn hơn limit 768Mi); render chart 29.3.2 bằng values của repo; kiểm resource hiệu dụng của controller, JMX và Job provisioning so với LimitRange/quota `zero-door` (B.3); ghi digest chart | Có đủ 5 topic; đo RAM Kafka, theo dõi OOMKilled |
| 7 | Policy | `bash infrastructure/scripts/setup-phase1.sh --component policies` | Bước 5 | Fluent Bit vẫn ghi được vào ES và Gaia (sau bước 8) vẫn query được ES. Controller đang chạy **không** chứng minh từng policy có hiệu lực đúng; phải thử cả luồng được phép lẫn luồng bị chặn |
| 8 | Gaia | Theo runbook legacy: `docker build -t zero-door/gaia:latest agent-orchestrator/gaia`, `k3d image import zero-door/gaia:latest -c zero-door`, `kubectl --context k3d-zero-door apply -f infrastructure/manifests/gaia-deployment.yaml`, `kubectl --context k3d-zero-door rollout status deployment/gaia -n zero-door --timeout=180s` | Bước 3, 5, 6 | Log Gaia không lỗi kết nối Prometheus/ES/Kafka; đo đỉnh RAM khi build. **Image identity (CR-03):** manifest dùng tag mutable `latest` với `imagePullPolicy: Never` (`gaia-deployment.yaml:27-28`). Khi Deployment đã tồn tại và manifest không đổi, `apply` không tạo pod mới; pod cũ vẫn chạy image cũ. Lần dựng lại phải có `kubectl --context k3d-zero-door rollout restart deployment/gaia -n zero-door` trước `rollout status`, hoặc tốt hơn là dùng tag không đổi (ví dụ theo commit) được cập nhật vào manifest. Ghi `docker image inspect --format '{{.Id}}' zero-door/gaia:latest` và `kubectl --context k3d-zero-door get pod -n zero-door -l app=gaia -o jsonpath='{..imageID}'` để đối chiếu. Cách so ID giữa Docker và containerd sau `k3d image import` còn cần xác nhận |
| 9 | Worker + Nemesis | `bash infrastructure/scripts/setup-phase3.sh` | Bước 4, 6; Secret Nemesis sẽ là template rỗng nếu chưa có | Rollout xong; `/healthz` có `kafka_connected`; không gọi endpoint POST |
| 10 | Hephaestus | `bash infrastructure/scripts/setup-phase4.sh` | Bước 6, 9 | Rollout và kiểm RBAC của script PASS |
| 11 | Tunnel + đo đủ stack | `bash start-demo.sh` (giữ terminal riêng) | Bước 1–10 | HTTP 200 chỉ là health. Đo mốc "stack đủ, chưa có tải" để làm baseline cho pilot |

Không chạy `setup-phase5.sh --install-deps` hay `--run-smoke` trong chuỗi này; smoke là thao tác riêng, chỉ sau khi sửa A-F2 và được Hoàng cho phép.

## C. Nhật ký lệnh

Tất cả chạy từ Git Bash, giờ +07:00 ngày 18/10/2026. Các truy vấn lab có `timeout` 15–25 giây và `--request-timeout=10s`; không lệnh nào timeout. Lượt tiếp tục lúc 11:09 không chạy lại kiểm tra; các kết quả dưới đây lấy từ output đã có trong phiên.

| Thời điểm | Lệnh (rút gọn) | Exit | Kết quả |
| --- | --- | --- | --- |
| 10:42:43 | `git rev-parse HEAD`; `git status --short --untracked-files=all`; lưu SHA-256 file dirty ra scratchpad | 0 | HEAD `1f43ff1`; dirty như mục 0 |
| 10:44:16 | `bash -n` trên 10 file `.sh`; đếm CR/BOM | 0 | 10/10 hợp lệ; không CR, không BOM |
| 10:44:16 | `command -v` các công cụ | — | Không có `shellcheck`, `python3`, `yamllint`; `curl` là alias `curl -4` trong shell tương tác (không ảnh hưởng script) |
| 10:44:23 | `bash tests/shell/run.sh` | 0 | 21/21 PASS, 22,5s; không còn thư mục test tạm |
| 10:45:24 | `k3d version`; `kubectl version --client`; `helm version --short`; `python --version`; `node --check …/app.js` | 0 | k3d v5.8.3; kubectl v1.33.5-dispatcher; Helm v4.2.2; Python 3.12.4; node v22.23.2, app.js hợp lệ |
| 10:45:24 | `k3d cluster create --help` | 0 | `--kubeconfig-switch-context` và `--kubeconfig-update-default` mặc định `true` |
| ~10:46 | `helm upgrade --help`; `helm repo add --help`; `head chaos-worker/go.mod`; `python -m pip show kafka-python kafka-python-ng` | 0 | `--wait` không giá trị = `watcher`; `--force-update` có; Go 1.21; host có kafka-python 2.3.0 |
| 10:46:56–10:47:01 | `docker context show`; `docker info`; `docker ps -a`; `docker stats --no-stream`; `k3d cluster list`; `kubectl … get nodes/ns/pods -A`; `top nodes/pods` | 0 (tất cả) | Số đo ở B.1; chỉ có pod hệ thống |
| 10:47:12 | `kubectl … get nodes -o jsonpath` (capacity, annotation `k3s.io/node-args`); `docker logs --tail 2000 k3d-zero-door-server-0 \| grep -i "network policy"`; `docker inspect` (memory/CPU) | 0 | Mỗi node 4 CPU / 7101036Ki; args như B.1; controller policy khởi động 02:55:01Z; container không giới hạn |
| 10:47:29 | `grep /proc/meminfo` (Windows); `tasklist`; đọc `.wslconfig`; `wsl -d docker-desktop -- …/proc/meminfo, pressure, nproc, loadavg` | 0 | Số đo ở B.1 |
| 10:48:11 | `helm env HELM_CACHE_HOME` + `find`; `helm repo list`; `docker images` lọc tên | 0 | Không có chart cache; hai repo Helm đã khai báo; không có image liên quan |
| ~10:48 | `grep` cấu hình ES/Fluent Bit; `wsl … cat /proc/sys/vm/max_map_count` | 0 | 262144 |
| offline | Script Python đọc YAML (đặt ngoài repo, chạy `python -I`) trích request/limit/quota và số dòng | 0 | Dữ liệu cho B.2 |
| 11:09:19 | Đọc lại báo cáo | 0 | A và B.1 còn nguyên; B.2 dừng giữa câu, đã viết tiếp |
| 11:39:07 | Lượt sửa theo Codex: `git rev-parse HEAD`; `git diff --cached --stat`; `git status --short --untracked-files=all`; lưu SHA-256 file dirty ra scratchpad | 0 | HEAD `1f43ff1`; staged rỗng; 56 dòng status (thêm `codex-review.md` untracked so với lúc 11:13) |
| 11:39–11:40 | Đọc source: `setup-phase1.sh`, `elasticsearch.yaml`, `kafka-values.yaml`, ba file quota, `target-app-hpa.yaml`, `gaia/main.py:140-175`, `gaia-deployment.yaml:20-45`, runbook legacy `:170-215`, `hephaestus/main.py`; `grep '^kind:'` trên manifest | 0 | Dữ liệu cho CR-01–CR-05 |
| 11:40:06 | `curl` upstream `kafka/29.3.2/values.yaml` với `-o /dev/stdout` | **23** | Lỗi ghi stdout trên Git Bash; chạy lại vào biến shell |
| 11:40 | `curl` (timeout 20s, chỉ stdout, không lưu file, không Helm cache): Kafka 29.3.2 `values.yaml`, `Chart.yaml`, `Chart.lock`, `templates/controller-eligible/statefulset.yaml`, `templates/provisioning/job.yaml`; common 2.20.2 `templates/_resources.tpl` | 0 (một đường dẫn đoán sai trả 404) | Heap 1024m ở `values.yaml:149,527`; `KAFKA_HEAP_OPTS` coalesce tại statefulset `:163-164`; JMX/provisioning preset `micro` = 250m/256Mi · 375m/384Mi; Job hook `post-install,post-upgrade`; common 2.20.2, zookeeper 13.4.3 |
| 11:40:34 | `kubectl … get storageclass`; `get pv,pvc -A`; `get ns` (timeout 20s, `--request-timeout=10s`) | 0 | `local-path` reclaim `Delete`, binding `WaitForFirstConsumer`; chưa có PV/PVC; chỉ 4 namespace hệ thống. Cột annotation default-class in `<none>` do cách escape tên cột; chưa kết luận gì về default class |
| ~11:41 | `ls hephaestus/*.py`; `grep` tên NetworkPolicy/namespace; `grep rollout setup-phase3/4.sh`; tên Deployment Hephaestus | 0 | Tên dùng trong allowlist B.5 |

**Không chạy:** setup thật, Helm install/template, build/import/rollout, apply, reset, attack/heal, `helm show values`/`helm pull` (sẽ tải chart), cài gói, sửa WSL/Docker/kubeconfig, gọi LLM/cloud, commit/push, cập nhật Linear.

## D. Quyết định cần Hoàng chốt và bước tiếp theo

Không hỏi lại phạm vi đã có trong SCOPE (ba vector, scale/block/rollback, KPI gốc, ≥5 dịch vụ và luồng mua hàng).

| # | Quyết định | Đề xuất của Claude | Vì sao cần chốt bây giờ |
| --- | --- | --- | --- |
| D1 | Giữ trần WSL 7GB/4 CPU/2GB swap | Giữ cấu hình hiện tại làm baseline thử nghiệm; áp chế độ "thí nghiệm đầy đủ" ở B.4 | **Đã có khuyến nghị của Codex; không cần Hoàng xác nhận lại chỉ để không đổi máy.** Chưa khẳng định full stack vừa trước khi đo |
| D2 | Sửa nào làm trước khi dựng | `controller.heapOpts` Kafka (bắt buộc trước bước 6) và render chart; A-F2 trước smoke; A-F1 trước lần tạo cluster sau; bổ sung bước restart/identity Gaia và quyết định HPA vào đường dựng; A-F4–A-F6 sau | Sửa source/config vận hành thuộc lượt triển khai sau; review không tự cấp quyền |
| D3 | Quota `target-app` `limits.cpu` 3 → 4 | Chỉ cần nếu profile thí nghiệm bật HPA; profile nền đủ ở 3 (B.3). Tính lại khi khóa profile | Không chặn bước namespace nền |
| D4 | Nếu thiếu recommendation/ad làm hỏng luồng mua hàng | Probe luồng mua hàng trước; chỉ khi probe chứng minh hỏng mới đề xuất thêm dịch vụ cụ thể cần thiết, kèm tính lại quota/RAM | Không bỏ tiêu chí nghiệp vụ; chưa đủ căn cứ để thêm cả hai |
| D5 | Ai chạy các lệnh thay đổi lab ở B.5 | **Đã rõ:** Claude thực hiện chính, Codex review, Hoàng luyện/theo dõi. Quyền mutation vẫn cấp riêng theo nhóm; một bên ghi cluster tại một thời điểm | Không cần hỏi lại |
| D6 (mới) | Profile thí nghiệm có HPA không, và cấu hình đối chứng HPA/healer | Quyết định trong protocol trước khi khóa profile (B.3) | Ảnh hưởng quota, topology và cách đọc kết quả healing |
| D7 (mới) | Mẫu số KPI CPU P179 | Chốt tại R0-T01-S02/R1 theo bảng ba đại lượng ở B.3 | Báo cáo sizing không có thẩm quyền chọn thay |

**Bước tiếp theo duy nhất (đã chỉnh theo Codex):** sau khi Codex review bản sửa này, Hoàng cấp một phạm vi thực thi nhỏ gồm: kiểm Docker/Kubernetes context, chạy `bash infrastructure/scripts/setup-phase1.sh --component namespaces` (namespace + quota + LimitRange), đo và lấy inventory trước/sau. Không cần đợi D3/D4/D6/D7 hay quyết định provider để làm bước này.

## Kết thúc phiên — 11:13:16 +07:00

HEAD vẫn `1f43ff1461c2199bc99e9962483956c3df0fa975`. So với lúc bắt đầu, `git status` chỉ thêm đúng file báo cáo này. Đối chiếu SHA-256 các file dirty có trước: chỉ `docs/delivery/NOW.md` và `docs/delivery/milestones/R0-foundations/local-lab.md` thay đổi, do nối đoạn bàn giao. Mọi file khác giữ nguyên. `git diff --check` exit 0; báo cáo không có CR hay khoảng trắng cuối dòng. Không còn thư mục test tạm.

## E. Xử lý Codex review CR-01–CR-05 (18/10, từ 11:39 +07:00)

Nguồn: [codex-review.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md). Lượt này chỉ sửa báo cáo. Không sửa source/config vận hành, không apply/install, không render hoặc tải chart vào Helm cache. Các số dòng dẫn trong báo cáo là của working tree đọc lúc 11:39–11:41.

| Mục | Trạng thái | Đã sửa ở đâu | Bằng chứng mới | Bằng chứng còn thiếu |
| --- | --- | --- | --- | --- |
| CR-01 HIGH, rollback có thể xóa PVC | Đã xử lý trong kế hoạch | B.5: rút `delete -f <file>`; thêm chính sách dừng trước, inventory trước/sau, allowlist theo bước và cột "giữ lại" | `elasticsearch.yaml:66-78` là PVC; Secret trong `nemesis-deployment.yaml:29`; ClusterRole/Binding trong `fluent-bit.yaml:119,128`; `local-path` reclaim `Delete` (LIVE_READ_ONLY 11:40:34); chưa có PV/PVC nào | Tên PVC do chart Prometheus/Kafka sinh ra; retention PVC của StatefulSet sau khi render; danh sách tài nguyên chart tạo ra (cần render/inventory thật) |
| CR-02 MEDIUM, ngân sách chart chưa đủ cho admission | Đã xử lý một phần | B.2: monitoring đổi sang UNKNOWN, bỏ dấu ≤; JMX/provisioning theo preset; tổng toàn lab không còn là cận trên. B.3: tính lại quota `zero-door`, nêu hai trường hợp có thể vượt 1Gi request. B.3/B.4/B.5: heap phải đặt qua `controller.heapOpts`; bước 3 và 6 thêm render trước khi cài. Estimate 3,2–4,9 GiB ghi rõ không phải acceptance | Upstream Kafka 29.3.2: `values.yaml:149,527,1968,2254`; `statefulset.yaml:163-164`; `provisioning/job.yaml:16-17,51-73`; `Chart.lock` (common 2.20.2); common `_resources.tpl` (preset `micro`) | Chưa render chart nào bằng values của repo; chưa có digest chart OCI; kube-prometheus-stack chưa pin version nên default hoàn toàn UNKNOWN; số admission ở B.3 là INFERENCE; chưa đo usage thật |
| CR-03 MEDIUM, topology quota khác kế hoạch | Đã xử lý | B.3: tách profile khôi phục nền (không HPA) với profile có HPA; thêm dòng 3225m và 2625m; thêm tương tác HPA/healer. B.5 bước 4: HPA deferred, lệnh apply/kiểm nếu bật. Bước 8: restart Gaia, timeout, image identity. A-F3 chỉnh theo Codex | Runbook legacy `:185-193` không có HPA; `target-app-hpa.yaml:11-19,31-39`; `hephaestus/main.py:177-197`; `gaia-deployment.yaml:27-28` | Chưa thử HPA và healer tranh replica; chưa xác nhận cách so image ID giữa Docker và containerd sau `k3d image import`; quyết định D6 |
| CR-04 MEDIUM, mẫu số KPI | Đã xử lý | B.3: rút câu "mẫu số phải là limit"; thay bằng bảng ba đại lượng (cores, % theo request, % theo limit) và đề xuất để khóa tại scope/measurement | `gaia/main.py:149,159-160`; `target-app-hpa.yaml:14-19,34-39`; `docs/delivery/SCOPE.md:12` | Quyết định D7 tại R0-T01-S02/R1; không sửa detector |
| CR-05 MEDIUM, MTTD bỏ qua cửa sổ CPU | Đã xử lý | B.4: thêm cửa sổ 120s làm thành phần độ trễ, ví dụ toán học 96s, rút câu "vẫn đo được <60s", ghi feasibility chưa xác minh và việc cần làm | `gaia/main.py:149`; `gaia-deployment.yaml:39-40`; `prometheus-values.yaml:41` | Định nghĩa onset/detect; số đo end-to-end trong pilot |

**Điều chỉnh phụ theo bảng đánh giá A-F của Codex:** A-F2 (không trộn `kafka-python` và `kafka-python-ng`; pin mọi gói là tùy chọn); A-F3 (thiếu script không tự vi phạm AC); A-F8 (fail-fast là chủ ý, chưa phải bug); A-F9 (đổi tiêu đề, enforcement chưa kiểm chứng). Mục D đã chỉnh theo phần quyết định của Codex: D1 và D5 không cần hỏi lại; thêm D6 (HPA/healer) và D7 (mẫu số KPI); bước tiếp theo không còn chờ toàn bộ D1–D5.

**Giới hạn của lượt sửa:**
- Đọc upstream qua web là đọc tài liệu nguồn, không phải render. Hiệu lực cuối của template vẫn cần `helm template` với values của repo trong lượt được cấp quyền.
- Không chạy lại 21 nhóm mock hay các kiểm tra live ở B.1; số đo B.1 vẫn là 10:46–10:48.
- Linear và GitNexus: hạn chế như mục 0, không đổi.
- Trong lượt này một phản hồi của Claude bị bộ lọc an toàn của phiên dừng sau truy vấn upstream lúc ~11:41. Không có lệnh nào trong phần bị dừng được chạy và không có sửa đổi dở dang; các sửa báo cáo bắt đầu sau đó.

## Kết thúc lượt sửa — 11:45:43 +07:00

HEAD vẫn `1f43ff1461c2199bc99e9962483956c3df0fa975`; staged rỗng. `git status --short --untracked-files=all` giống hệt lúc 11:39:07. So SHA-256 mọi file dirty/untracked với lúc 11:39: chỉ file báo cáo này thay đổi. Lượt này không nối gì thêm vào `NOW.md` hay `local-lab.md` (Codex đã nối con trỏ review). `git diff --check` exit 0 (chỉ có cảnh báo CRLF có trước của `.gitignore`; lệnh này không bao phủ file untracked). Báo cáo: 0 ký tự CR, không có khoảng trắng cuối dòng. Không apply, install, render, build hay sửa source/config vận hành.
