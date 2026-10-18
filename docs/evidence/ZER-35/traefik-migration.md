# ZER-35 — Gói chuyển ingress sang Traefik (phương án B): phạm vi trước triển khai

**Trạng thái: ĐÃ TRIỂN KHAI LÚC 17:15–17:27, CẢ 9 BƯỚC CỦA MỤC 9 ĐỀU ĐẠT (mục 15). Kiểm cuối exit 3, chỉ còn hai FAIL đã biết. Chờ Codex review runtime.** Lần chạy 16:42 đã dừng ở bước 0 vì RAM trống của host thấp (mục 14). Chưa commit/push; ZER-35 chưa Done.
- Hoàng đã duyệt patch agent ngày 18/10/2026, nguyên văn: “Duyệt patch agent cùng gói; triển khai cả hai patch sau khi Codex review đạt.”
- Việc triển khai (mục 9, gồm cả rebuild agent) chỉ bắt đầu khi Codex retest đạt.
- Chưa cài Traefik, chưa apply manifest, chưa sửa file nào trong working tree. Toàn bộ thay đổi nằm trong hai patch, kèm kiểm chứng offline, render thật và dry-run phía server.
- Cách sửa từng finding: TFM-01–03 ở mục 12, TFM-04–07 ở mục 13.

- Người viết: Claude Code, 18/10/2026, 14:15–14:40 +07:00. Sửa theo review: 14:55–15:15 và 16:00–16:35 +07:00.
- Review: Codex. Quyết định: Hoàng (đã chọn B lúc giao việc).
- Ràng buộc theo yêu cầu: giữ nguyên yêu cầu nghiên cứu; không dùng Gateway API; không cài ingress-nginx tạm.

## 1. Nội dung gói

| File | Vai trò |
| --- | --- |
| [traefik-migration-infra.patch](traefik-migration-infra.patch) | 15 file hạ tầng, test và runbook: +846 / −93 dòng. SHA-256 `03ab4a6c60f135acc6dc4f6b2e537a72dfd5b5e83714d3894fd775b9708ff53f`. Thay bản Codex retest lúc 15:54 (`bd6624a7…a95c`) và bản đầu (`d631abbc…`) |
| [traefik-migration-agents.patch](traefik-migration-agents.patch) | Query PromQL của Gaia và Nemesis: +9 / −8 dòng. **Nằm ngoài allowlist (logic agent); Hoàng đã duyệt cùng gói.** Không đổi so với bản Codex đã review. SHA-256 `b9e83cd9a09f3eef1814ab380ccf0c404a535eb5002fb657ed96078697ca99a0` |
| Tài liệu này | Lý do, phụ thuộc, kiểm chứng, kế hoạch triển khai, rollback |

Hai patch được tạo lại lúc 16:21, cùng tập file với lượt 15:09.
- Trước khi tạo, SHA-256 của cả 15 file gốc được so lại; không file nào đổi. Bản sao gốc trong `scratch/` cũng trùng từng byte với working tree.
- Patch agent được sinh lại bằng cùng cách và cho đúng hash cũ, nên cách sinh patch không đổi.
- `git apply --check --whitespace=error-all` đạt với cả hai.
- Khi áp hai patch lên bản sao file gốc, kết quả trùng từng byte với bản nháp đã kiểm (`diff -r` rỗng). Mọi kiểm ở mục 8.1 chạy trên chính cây round-trip đó.
- `target-app.yaml` dùng CRLF và được giữ CRLF.

Không có gì cần cài thêm trong lab:
- Chart được tải vào `scratch/zer35/charts/traefik/` bằng Helm home riêng của phiên.
- Image `docker.io/traefik:v3.7.14` sẽ được kubelet kéo khi cài.
- Regression thật cần `promtool`. Đã tải bản Prometheus 3.15.0 windows-amd64 chính thức từ GitHub release, SHA-256 zip `5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e` khớp `sha256sums.txt`. Chỉ giải nén `promtool.exe` vào `scratch/zer35/tools/promtool/`; không cài vào hệ thống.

## 2. Hiện trạng đo được (chỉ đọc, 14:20–14:32)

- `target-app/frontend-external` là Service `LoadBalancer`. K3s servicelb tạo DaemonSet `kube-system/svclb-frontend-external-ac3b98f4`, giữ hostPort 80 trên cả hai node.
  - Vì vậy `http://127.0.0.1:8080/_healthz` hiện trả **200 thẳng từ frontend, không qua ingress nào**.
  - `/nemesis/healthz` trả 404, vì đó là frontend trả lời.
  - Hệ quả: nếu cài bất kỳ controller nào với Service LoadBalancer port 80 mà không đổi Service này, svclb của controller sẽ không bind được port. Điều này đúng với cả phương án A trước đây.
- Không có IngressClass và không có CRD nào chứa `traefik`.
  - `nemesis-ingress` và `hephaestus-ingress` đang tồn tại với class `nginx` nhưng không có controller phục vụ.
  - `frontend-ingress` chưa được apply.
- `kube-system` không có ResourceQuota hay LimitRange.
- Cách log nằm trong Elasticsearch (đọc 1 document sentinel của frontend):
  - Parser `cri` đặt cả dòng log vào field `message`.
  - Filter `kubernetes` với `Merge_Log On` không tách JSON vì field không tên là `log`.
  - Do đó dòng JSON của Traefik sẽ nằm nguyên là chuỗi trong `message`, với `kubernetes.container_name=traefik` và `namespace_name=kube-system`. Đây là field mà Gaia tìm.

## 3. Chart, image và render

| Mục | Giá trị |
| --- | --- |
| Chart | `traefik/traefik` 42.0.0 từ `https://traefik.github.io/charts`. tgz SHA-256 `a6ede324662ddcca0160a5ce639b7b5b9dd40a20a475e1101e9f95b5e5d83dd5`. appVersion v3.7.14. kubeVersion `>=1.30.0-0` (lab: v1.31.5+k3s1) |
| Image | `docker.io/traefik:v3.7.14`. Index digest `sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c`. Bản linux/amd64 `sha256:5902d68e00708015736416b62faa49d23a2e1d4415649e5831d20b79ba301508`. Đọc bằng `docker buildx imagetools inspect`, không pull |
| Render | `helm template ... -n kube-system --kube-version 1.31.5 --api-versions monitoring.coreos.com/v1 --skip-crds` exit 0. 9 object: ServiceAccount, ConfigMap `traefik-file-provider`, ClusterRole, ClusterRoleBinding, Service `traefik` (LoadBalancer 80/443; `externalTrafficPolicy` để mặc định Kubernetes là `Cluster`), Service `traefik-metrics` (ClusterIP 9100), Deployment `traefik`, IngressClass `traefik` (không mặc định), ServiceMonitor `traefik` (endpoint `honorLabels: true`, xem 5.1). Không có hook hay Job |
| Tài nguyên | request 50m / 64Mi, limit 300m / 160Mi. ingress-nginx cũ là 50m / 90Mi và 300m / 150Mi. Không có quota namespace áp lên |
| Admission | `kubectl apply --dry-run=server` (không lưu gì) chấp nhận cả 9 object của bản render hiện tại (15:12). Bản render rollback (`--set service.spec.type=ClusterIP`) cũng qua; cả hai Service đều là ClusterIP, không còn `externalTrafficPolicy` |

**CRD: không tạo.** Thư mục `crds/` của chart có 25 CRD: 10 `traefik.io` và 15 `hub.traefik.io`. Gói tắt provider `kubernetesCRD` và cài với `--skip-crds`. Lý do:
- CRD là object cấp cluster.
- Quy tắc của lab cấm xóa CRD khi dọn dẹp.
- Rewrite chỉ cần hai middleware, nên định nghĩa chúng trong file provider. File provider là ConfigMap thuộc release, ví dụ `nemesis-prefix@file`.

Đánh đổi: không dùng được IngressRoute hay Middleware CRD. Nếu sau này cần, phải có scope riêng.

**RBAC:** ClusterRole có `get/list/watch` trên `secrets` toàn cluster, tức là có cả `zero-door`, nơi chứa `nemesis-secrets`. Đây là mặc định của chart và tương đương ingress-nginx. Chart cho phép `rbac.namespaced: true`, nhưng ghi rõ chế độ đó không dùng được với IngressClass. Gói giữ ClusterRole. Codex có thể yêu cầu giới hạn khác nếu thấy cần.

## 4. Thay đổi theo file

### 4.1 Patch hạ tầng (allowlist cộng thay đổi controller mà Hoàng đã chọn)

| File | Thay đổi |
| --- | --- |
| `helm-values/chart-versions.yaml` | Thêm `traefik: 42.0.0` kèm SHA-256 đầy đủ của chart (test thật đọc giá trị này). Bỏ dòng `ingress-nginx:` trống |
| `helm-values/traefik-values.yaml` (mới) | Như mục 3. Thêm: `checkNewVersion=false`; access log JSON ra stdout; giữ header `User-Agent` và `X-Forwarded-For`, các header khác (Cookie, Authorization…) bị bỏ; giữ query string; metric Prometheus với label entrypoint/service và bucket giống ingress-nginx (mục 5); ServiceMonitor 15s với **`honorLabels: true`** (TFM-01); `strictPrefixMatching: true`; hai middleware `replacePathRegex` |
| `scripts/lib/common.sh` | Thêm `zd_agent_queries`: đọc bằng AST 4 query ingress từ `gaia/main.py` và `nemesis/main.py`, in ra JSON. Probe và test dùng đúng chuỗi agent gửi, không chép tay |
| `helm-values/ingress-nginx-values.yaml` | **Xóa file.** Controller đã bỏ, image mirror `dyrnq` không rõ nguồn. File vẫn còn trong lịch sử Git |
| `scripts/setup-phase1.sh` | `ingress` cài release `traefik` vào `kube-system` bằng `--repo`, `--version` pin, `--skip-crds`, `--wait --timeout 5m`. Trước khi cài, kiểm CRD `servicemonitors`. `all` cài ingress sau monitoring và Kafka, thay cho nhánh bỏ qua cũ. Cờ `--ingress-cluster-ip` (chỉ đi với `--component ingress`) là bước rollback R1: `helm upgrade` release có sẵn (không `--install`) với `--set service.spec.type=ClusterIP`, qua cùng guard Docker/context và Helm home trong `scratch/` (TFM-06) |
| `scripts/setup-local-apps.sh` | `target` apply thêm `target-app-ingress.yaml`. Ingress không có tác dụng gì cho tới khi Traefik được cài |
| `scripts/verify-local-lab.sh` | Thêm `--check ingress` và `--check consumers`; `ingress` chạy `consumers` ở cuối, `all` gồm cả hai. Chi tiết probe ở mục 8.2. Hàm `es_tunnel`/`es_count`/`prom_query` dùng chung. `telemetry` đọc `/api/v1/targets` và chỉ gắn nhãn `FAIL (known)` cho đúng hai target `target-app/frontend` và `frontend-external` lỗi 404. Exit code: `0` khi mọi probe đạt; `3` khi chỉ còn FAIL đã biết; `1` khi có FAIL khác. `agents` kiểm thêm log Gaia 10 phút gần nhất không có lỗi query Prometheus (TFM-02); không đọc được log là FAIL (TFM-05) |
| `manifests/target-app.yaml` | `frontend-external` đổi `LoadBalancer` → `ClusterIP`. Dry-run phía server xác nhận apiserver tự bỏ `nodePort`. Sau khi apply, K3s servicelb tự gỡ DaemonSet svclb mà nó quản lý |
| `manifests/target-app-ingress.yaml` | `ingressClassName: traefik` |
| `manifests/nemesis-deployment.yaml`, `hephaestus-deployment.yaml` | Class `traefik`. Path `/nemesis` và `/hephaestus` dùng `pathType: Prefix`. Annotation `traefik.ingress.kubernetes.io/router.middlewares: <name>-prefix@file` thay `rewrite-target`/`use-regex` |
| `manifests/prometheus-rules.yaml` | `HighErrorRate` và `HighLatency` chuyển sang metric Traefik (mục 5). Ngưỡng 5% và 1s, `for` và label giữ nguyên |
| `tests/shell/run.sh` | Bỏ giả định ingress không pin. Test pin trống chuyển sang `traefik`. Test `target` yêu cầu có Ingress. Thêm 6 test (32/32): (1) ingress cài đúng chart pin vào `kube-system` với `--skip-crds`, có kiểm CRD, không còn ingress-nginx; (2) rollback R1 qua `--ingress-cluster-ip`; (3) 4 case exit code của `telemetry` qua mock Prometheus; (4) 3 case log Gaia; (5) 4 case cổng consumer với mock Prometheus có mô hình scrape; (6) hợp đồng `honorLabels` trong values. Thêm `verify-local-lab.sh` vào kiểm `--help` (9 đường). Mock có thêm `/healthz`, `/api/v1/labels` và log Gaia. Fixture chép `gaia/main.py`, `nemesis/main.py` để `zd_agent_queries` chạy được. Đường dẫn đưa cho Python được đổi qua `cygpath -m` (TFM-07) |
| `tests/shell/test-local-restore.sh` (mới, tên có trong allowlist) | Regression thật, không mock, không gọi cluster (mục 8.1): pin và SHA chart, render contract, render rollback, promtool trên series giả lập cho rule, query agent và cổng consumer (5 nhóm) |
| `docs/runbooks/bash-tooling.md` | Ghi chú chart Traefik, thứ tự dựng có bước `ingress`, `frontend-external` là ClusterIP, check `ingress` và `consumers`, log không đọc được là FAIL, lệnh rollback R1, ý nghĩa exit 0/3/1, kết quả cuối phải lấy sau build, cách chạy `test-local-restore.sh`, và yêu cầu test đạt cả khi tắt path conversion |

Codex cần xác nhận phạm vi ở hai điểm. Allowlist ghi “helm-values (ingress-nginx…)”. Gói này **thêm `traefik-values.yaml` và xóa `ingress-nginx-values.yaml`**: đó là phần thay thế trực tiếp do quyết định B, không thêm thành phần nào khác. `target-app.yaml` nằm trong allowlist, nhưng việc đổi `frontend-external` làm thay đổi topology của Boutique (xem 7.3).

### 4.2 Patch agent (ngoài allowlist, Hoàng đã duyệt; chưa áp)

| File | Thay đổi |
| --- | --- |
| `agent-orchestrator/gaia/main.py:200-224` | `error_rate_query` và `latency_query` dùng cùng biểu thức với PrometheusRule mới, có `label_replace` để `service` vẫn là tên Service Kubernetes. Ngưỡng, severity, `suggested_action` và luồng publish giữ nguyên |
| `agent-orchestrator/nemesis/main.py:194-195` | `http_rps` và `error_rate` (ngữ cảnh cho LLM) dùng `traefik_service_requests_total{service=~"target-app-.+@kubernetes"}` |

Nếu không áp patch này, Gaia và Nemesis vẫn chạy bình thường nhưng các query trên trả rỗng. Đó cũng là hành vi hiện tại, vì metric nginx chưa từng có (mục 7.1). Áp patch thì phải build lại image Gaia và Nemesis (mục 9, bước 6).

Phương án đã cân nhắc và **không đề xuất**: dùng `metricRelabelings` của ServiceMonitor để đổi tên series Traefik thành `nginx_ingress_controller_*`. Cách này giữ agent nguyên vẹn và nằm trong allowlist. Nhưng nó tạo ra dữ liệu mang tên của một controller không tồn tại, làm sai nguồn gốc số liệu nghiên cứu. Hoàng có thể chọn cách này thay cho patch agent; nếu chọn, chỉ đổi values và rule.

## 5. Metric: ánh xạ ingress-nginx → Traefik

| Khía cạnh | ingress-nginx (code agent hiện tại) | Traefik v3.7.14 (gói này) |
| --- | --- | --- |
| Counter | `nginx_ingress_controller_requests` | `traefik_service_requests_total` |
| Histogram | `nginx_ingress_controller_request_duration_seconds_bucket` | `traefik_service_request_duration_seconds_bucket` |
| Mã HTTP | label `status` | label `code` |
| Lọc namespace | `namespace="target-app"` (namespace của Ingress) | Không có label namespace. Lọc theo `service=~"target-app-.+@kubernetes"` |
| Label `service` | Tên Service backend, ví dụ `frontend` | `<namespace>-<service>-<port>@kubernetes`, ví dụ `target-app-frontend-80@kubernetes`. Nguồn: `pkg/provider/kubernetes/ingress/kubernetes.go:394` và `portString` ở dòng 1009 (tag v3.7.14). `label_replace(..., "target-app-(.+)-[^-]+@kubernetes")` đổi lại thành `frontend` |
| Bucket | Mặc định của controller (`prometheus.DefBuckets`: .005 … 10) | Đặt bằng đúng dãy đó trong values. Mặc định của Traefik là 0.1/0.3/1.2/5, khi đó P99 = 1s chỉ là nội suy giữa 0.3 và 1.2 |
| Ý nghĩa thời gian | Thời gian xử lý request của NGINX (`$request_time`) | Thời gian ở tầng service của Traefik (proxy tới backend tới khi xong response). Hai đại lượng gần nhau nhưng **không đồng nhất** |

Đã kiểm trên Prometheus thật qua `/api/v1/query` (14:30):
- Cả 6 biểu thức mới đều parse thành công: 2 rule và 4 query của agent. Kết quả rỗng vì Traefik chưa chạy.
- Thử `label_replace` với 4 nhãn mẫu:
  - `target-app-frontend-80@kubernetes` → `frontend`
  - `target-app-frontend-http@kubernetes` → `frontend`
  - `target-app-redis-cart-6379@kubernetes` → `redis-cart`
  - `zero-door-nemesis-8000@kubernetes` giữ nguyên, và selector đã loại nhãn này trước đó.
- Dry-run phía server của PrometheusRule mới qua admission đạt.

Phần kiểm trên chỉ chứng minh cú pháp và regex. Nó **không** phát hiện được TFM-01 (mục 5.1). Giá trị và cách lọc được kiểm bằng promtool trên series giả lập (mục 8.1).

### 5.1 Hợp đồng nhãn khi scrape (TFM-01)

- Operator gắn label đích `service=<tên Service bị scrape>` (`traefik-metrics`). Prometheus CR có `overrideHonorLabels=false`, theo đọc của Codex.
- Với `honor_labels=false` (mặc định), nhãn `service` của chính Traefik trùng tên với label đích. Prometheus đổi nhãn của Traefik thành `exported_service`, còn `service` thành `traefik-metrics`.
- Khi đó mọi selector `service=~"target-app-.+@kubernetes"` trả rỗng. Bị ảnh hưởng: 2 rule, 4 query agent và probe.
- Sửa: `metrics.prometheus.serviceMonitor.honorLabels: true`. Render cho ra endpoint `honorLabels: true`.
- Series `traefik_service_*` mang nhãn `code`, `method`, `protocol`, `service` (histogram thêm `le`). Series entrypoint mang thêm `entrypoint`. Ngoài `service`, không nhãn nào trùng label đích (`namespace`, `pod`, `container`, `endpoint`, `job`, `instance`). Vì vậy `honorLabels` không ghi đè nhãn định danh target nào khác.
- Không đổi tên nhãn backend, nên rule, query agent và probe giữ nguyên.

Ba lớp chặn hồi quy:
1. `run.sh` kiểm `honorLabels: true` trong values.
2. `test-local-restore.sh` kiểm bản render của chart pin. Promtool cũng chứng minh dạng `exported_service` làm mọi consumer rỗng.
3. Sau khi cài, `verify --check ingress` kiểm ServiceMonitor thật có `honorLabels`, kiểm danh sách tên nhãn của `traefik_service_*` có `service` và không có `exported_*`, và kiểm query consumer có dữ liệu `frontend`.

Tên metric và label lấy từ [tài liệu metrics Traefik](https://doc.traefik.io/traefik/reference/install-configuration/observability/metrics/) và source tag v3.7.14. **Chưa thấy series thật** cho tới khi triển khai (mục 8).

## 6. Access log và phát hiện SQLi

- Traefik ghi mỗi request một dòng JSON ra stdout. Fluent Bit đưa dòng đó vào Elasticsearch (`zero-door-logs-*`, field `message`) như mọi container khác. Không cần sửa `fluent-bit.yaml` hay `elasticsearch.yaml`.
- `RequestPath` được tạo bằng `url.URL{Path, RawPath, RawQuery}.String()` (`pkg/middlewares/accesslog/logger.go:250-260`, v3.7.14), tức là **dạng đã percent-encode, kèm query string**.
  - Dòng request HTTP không thể chứa dấu cách thô, nên một payload `UNION SELECT` trên URL sẽ tới dưới dạng `UNION%20SELECT` hoặc `UNION+SELECT`.
  - Cả `match_phrase` của Gaia (`gaia/main.py:292-293`) lẫn phép `in` trong Python (dòng 326) đều **không khớp** dòng log của Traefik.
  - ingress-nginx cũng ghi request thô, nên giới hạn này không do migration gây ra.
- Log ứng dụng frontend có `http.req.path` **đã decode** (thấy trong document sentinel ở mục 2), nhưng không có query string và body.
  - Hiện tại chỉ payload nằm trong path mới có thể khớp chữ ký của Gaia, qua log frontend.
  - Payload trong query hoặc form thì không khớp, với cả hai controller.
- Gaia gán alert theo `container_name`.
  - Một hit trong log Traefik sẽ tạo alert `service=traefik`, và Hephaestus `BLOCK_IP` sẽ chọn pod `app=traefik` trong `target-app`, tức là không có pod nào.
  - Với nginx, giá trị tương ứng là `controller`. Hành vi giữ nguyên.
- Log riêng của Traefik ở mức error ghi `"level":"error"`. Nhánh ERROR/Exception của Gaia chỉ cảnh báo cho namespace `target-app`, nên log của `kube-system` không sinh alert.

Gói **không sửa** logic phát hiện. Các điểm trên được ghi lại để Hoàng quyết định ở phạm vi nghiên cứu (7.2).

## 7. IP nguồn và tính so sánh của dữ liệu nghiên cứu

### 7.1 Tín hiệu ingress trước đây chưa từng có

- Values ingress-nginx trong repo chưa bao giờ bật `controller.metrics`: `git log -S controller.metrics -- infrastructure` không ra commit nào.
- Prometheus cũng không có scrape config bổ sung cho nginx.
- Với cấu hình trong repo, các query `nginx_ingress_controller_*` của Gaia, Nemesis và PrometheusRule luôn trả rỗng.
- Các CSV của bộ 40 lần chạy (`docs/experiments/raw_data/*`) không ghi loại alert đã kích hoạt phát hiện. Vì vậy không xác định được lần chạy nào từng dựa vào tín hiệu ingress (**UNKNOWN**).

Kết luận: sau migration, `HIGH_ERROR_RATE` và `HIGH_LATENCY` là **tín hiệu mới có dữ liệu**, không phải tín hiệu cũ bị đổi định nghĩa. Lần chạy trước và sau không so sánh trực tiếp được trên hai alert này. Metadata của mỗi lần chạy nên ghi tên controller.

### 7.2 Lưu lượng tấn công không đi qua ingress

- `chaos-worker` gửi HTTP flood tới `http://<service>.target-app.svc.cluster.local` (`internal/attack/http_flood.go:35-38`).
- Validator chỉ cho phép hậu tố `.target-app.svc.cluster.local` (`internal/validation/target.go:25`).
- Lưu lượng flood vì vậy **đi vòng qua ingress**, dù controller là nginx hay Traefik. Metric ingress chỉ thấy request từ host qua `:8080` và request của probe.

Nếu kịch bản DDoS tầng ứng dụng cần đi qua ingress, phải đổi đích tấn công hoặc validator. Đó là logic Go và yêu cầu nghiên cứu, **ngoài gói này**. Gói không đổi gì ở đây.

### 7.3 IP nguồn

Đường đi từ host: `127.0.0.1:8080` → container `k3d-zero-door-serverlb` (proxy TCP L4) → port 80 của node → svclb (DNAT bằng iptables) → Service `traefik` → pod Traefik.

- **IP của client Windows mất ngay ở chặng k3d serverlb.** Proxy này không gửi PROXY protocol, và đổi cấu hình LB của k3d nằm ngoài phạm vi (không sửa K3d).
  - Request từ host sẽ được ghi với một địa chỉ nội bộ. Giá trị cụ thể sẽ do check `ingress` đo.
  - Mọi request từ host vì thế mang cùng một nguồn. Nếu block IP đó thì chặn toàn bộ lưu lượng từ host.
- `externalTrafficPolicy` giữ `Cluster`. `Local` cũng không lấy lại được IP Windows (đã mất ở chặng trước). Ngoài ra svclb chỉ nghe trên node có pod Traefik, trong khi k3d LB chia kết nối cho cả hai node.
- `forwardedHeaders` không tin nguồn nào (`trustedIPs: []`, `insecure: false`).
  - Source logger ghi `ClientHost` theo header `X-Forwarded-For` nếu header đó có mặt khi log được ghi (`logger.go:276-278`).
  - Check `ingress` gửi một header giả `X-Forwarded-For: 192.0.2.10` (dải TEST-NET-1) và yêu cầu giá trị này không trở thành `ClientHost`.
  - Nếu check FAIL, phải dùng `ClientAddr` (peer TCP) thay cho `ClientHost`. Đây là rủi ro đã nêu, chưa được chứng minh.
- Client trong cluster (pod gọi ClusterIP `traefik.kube-system`): flannel và kube-proxy không SNAT lưu lượng từ pod tới Service, nên dự kiến `ClientHost` bằng IP của pod. Check `ingress` so trực tiếp hai giá trị này.
- Liên quan tới `BLOCK_IP`:
  - Alert `SUSPICIOUS_LOG` của Gaia không có `sourceIP`.
  - Hephaestus khi đó tìm IP bằng regex trong `description` (`hephaestus/main.py:457-465`). Description không chứa IP, nên giá trị rơi về `0.0.0.0`.
  - Hiện nay `BLOCK_IP` không chặn IP client thật nào, với cả hai controller. Để IP nguồn có ý nghĩa cần sửa agent (ngoài allowlist), và với lưu lượng từ host cần một đường giữ được IP (k3d không có).

### 7.4 Tài liệu nghiên cứu

`docs/research/chapter4.md:221-274` mô tả Nginx Ingress và annotation `rewrite-target`. Gói không sửa báo cáo nghiên cứu. Chủ báo cáo cần cập nhật phần này nếu chấp nhận migration.

## 8. Kiểm chứng

### 8.1 Đã làm trong gói này

Các dòng có đánh dấu **(15:0x–15:1x)** chạy lại sau khi sửa theo review 14:52. Các dòng **(16:1x–16:3x)** chạy sau khi sửa theo retest 15:54. Cả hai lượt chạy trên cây round-trip tạo từ chính hai patch đang giao.

| Kiểm | Kết quả |
| --- | --- |
| **(16:22)** `bash tests/shell/run.sh`, môi trường sạch (bỏ `ZD_HELM_HOME`, `ZD_PROMTOOL`, `MSYS_NO_PATHCONV`, `MSYS2_ARG_CONV_EXCL`) | **exit 0, 32/32 PASS** (trước là 29), 83s |
| **(16:24)** Cùng suite với `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL=*` (TFM-07) | **exit 0, 32/32 PASS**, cùng các dòng PASS như môi trường sạch. Lượt thử đầu (cây lặp, trước khi tạo patch) có case “query luôn rỗng” bị `timeout 15s` (exit 124) khi đang in dòng cuối; logic đã cho đúng các dòng FAIL mong đợi. Bốn case consumer giờ có timeout 90s (tối đa 4 vòng poll, mỗi lần một tiến trình Python) |
| **(16:25)** `ZD_PROMTOOL=… bash tests/shell/test-local-restore.sh` | **exit 0, 15 PASS, 0 FAIL**; promtool `SUCCESS` cho 5 nhóm (3 nhóm cũ, thêm cold start/idle và hai lần scrape) |
| **(16:26–16:33)** Mutation TFM-04: chỉ gửi request ở vòng đầu (một loạt request rồi chờ, đúng dạng lỗi Codex tái hiện) | `run.sh` exit 1: `two confirmed scrapes with fresh requests should exit 0, got 1` |
| **(16:26–16:33)** Mutation TFM-05: lấy log Gaia bằng `2>/dev/null \|\| true` | `run.sh` exit 1: `a Gaia log that cannot be read should exit 1, got 0` |
| **(16:26–16:33)** Mutation TFM-06: nhánh R1 gọi `helm` trực tiếp thay cho `zd_helm` (mất `--kube-context` và Helm home riêng) | `run.sh` exit 1 (mock Helm từ chối lệnh thiếu `--kube-context=k3d-zero-door`) |
| **(16:26–16:33)** Mutation TFM-07: bỏ `cygpath -m`, chạy với path conversion tắt | `run.sh` exit 1: Python `FileNotFoundError` ở `/r/…/traefik-values.yaml`, đúng lỗi Codex báo |
| **(16:18)** Lint lệnh mẫu mục 9–10: mọi dòng `kubectl`/`helm` có context; R1 là wrapper có guard | Đạt: 11 lệnh `kubectl`/`helm` trong 3 khối lệnh và các đoạn code inline đều có context; khối R1 đúng là lệnh wrapper mà `run.sh` kiểm argv; không còn `helm upgrade` trần ở mục 9–10. Lượt lint đầu bắt được mô tả bước 3 viết `helm upgrade --install` không context, đã sửa |
| **(16:33)** `verify-local-lab.sh --check agents` của cây round-trip trên lab thật (chỉ đọc) | Exit 0. Ba `/healthz` có `kafka_connected:true`, chaos-worker rollout xong, `PASS Gaia log read; no Prometheus query error`: đường đọc log mới chạy với kubectl thật |
| **(16:34)** Hiện trạng sau lượt sửa | Source working tree trùng `base-sha256.txt`; HEAD `1f43ff1`; staging rỗng. Cluster: không có IngressClass, không ServiceMonitor Traefik, `frontend-external` vẫn LoadBalancer. Values/chart/manifest không đổi nên render và dry-run phía server lượt 15:12 vẫn áp dụng |
| Pull chart 42.0.0 vào `scratch/` (Helm home riêng) và ghi SHA | Đạt (mục 3) |
| **(15:10)** `bash tests/shell/run.sh`, chạy với môi trường sạch (không đặt `ZD_HELM_HOME`/`ZD_PROMTOOL`) | **29/29 PASS** (trước review là 27) |
| **(15:10)** `ZD_PROMTOOL=… bash tests/shell/test-local-restore.sh` | **exit 0, 15 PASS, 0 FAIL**. Gồm: SHA chart khớp `chart-versions.yaml`; render có `honorLabels: true`, 0 CRD, IngressClass không mặc định, rewrite giống `/$2`, các args chính, CRD provider tắt, Service LB 80/443; bản render rollback cho Service ClusterIP, không còn `externalTrafficPolicy`; promtool `SUCCESS` cho 3 nhóm test (bảng dưới) |
| **(15:05–15:08)** Mutation: bỏ `honorLabels` | `test-local-restore.sh` exit 1 (render contract FAIL); `run.sh` exit 1 (`traefik-values.yaml must set … honorLabels: true`) |
| **(15:05–15:08)** Mutation: regex `label_replace` của PrometheusRule bỏ phần `-<port>` | promtool FAIL (alert sai nhãn `service`) |
| **(15:05–15:08)** Mutation: trong source Nemesis, `http_rps` và mẫu số `error_rate` đổi về `nginx_ingress_controller_requests` | promtool FAIL (`exp 7`, `exp 4`, `exp 1/7`, nhận rỗng) |
| **(15:12)** Render hiện tại và render rollback, `kubectl apply --dry-run=server` | Đều được chấp nhận (mục 3) |
| **(15:01)** `verify-local-lab.sh` bản nháp, `--check telemetry` trên lab thật (chỉ đọc) | Exit **3**. Hai dòng `FAIL (known)` cho `target-app/frontend` và `frontend-external` (`server returned HTTP status 404 Not Found`); Prometheus ready, Kafka JMX, 9 series cAdvisor PASS |
| **(15:01)** cùng bản nháp, `--check agents` (chỉ đọc) | Exit 0. Ba `/healthz` có `kafka_connected:true`, chaos-worker rollout xong, log Gaia 10 phút không có lỗi query Prometheus |
| **(15:02)** `/api/v1/labels?match[]=…` qua API-server service proxy | Trả danh sách tên nhãn (ví dụ series Kafka). Với `traefik_service_.+`, kết quả rỗng vì chưa cài. Probe nhãn ở 8.2 dùng đúng đường này |
| `kubectl apply --dry-run=server`: 3 Ingress mới; `frontend-external` ClusterIP; PrometheusRule mới (14:2x) | Được chấp nhận. `frontend-external` → `ClusterIP`, không còn `nodePort` |
| Parse PromQL trên Prometheus thật, `label_replace` với 4 nhãn mẫu (14:30) | Đạt; chỉ chứng minh cú pháp và regex |
| `bash -n` mọi script đã sửa; `--help` của `verify-local-lab.sh` và `test-local-restore.sh` không gọi CLI | Đạt |
| `git apply --check --whitespace=error-all` trên working tree; round-trip | Đạt; trùng từng byte |
| Hiện trạng `:8080`, svclb, IngressClass, CRD, quota `kube-system`, định dạng document ES | Như mục 2 |

Các nhóm promtool trong `test-local-restore.sh`. Rule và query lấy thẳng từ `prometheus-rules.yaml` và source agent qua `zd_agent_queries`; scrape 15s; đánh giá tại 5m:

| Nhóm | Dữ liệu giả lập | Kỳ vọng (đều đạt) |
| --- | --- | --- |
| Có lỗi và độ trễ | frontend 4 rps mã 200 và 1 rps mã 503, mọi request rơi vào bucket 1–2.5s. `redis-cart` (tên có dấu gạch nối, port 6379) 2 rps, nhanh. `zero-door-nemesis` 4 rps mã 500. Một series dạng `exported_service` mã 500 | Gaia error rate `{service="frontend"} 0.2`; mẫu số `frontend 5`, `redis-cart 2`; P99 `frontend 2.485`, `redis-cart 0.00495`; Nemesis `http_rps 7`, `error_rate 1/7`; alert `HighErrorRate` (critical) và `HighLatency` (warning) chỉ cho `frontend`, annotation đúng. zero-door và `exported_service` bị loại |
| Lưu lượng lành | frontend chỉ có mã 200 | Mẫu số `frontend 4`, tử số rỗng, tỷ lệ rỗng (không phải 0), Nemesis `http_rps 4`, không alert. Như vậy “chưa có 5xx” khác với “thiếu metric backend” |
| Không có `honorLabels` | Chỉ có series `service="traefik-metrics", exported_service=…` | Cả 4 query agent và mẫu số đều rỗng, không alert. Đây đúng là dạng lỗi TFM-01 |
| **(16:25)** Cold start rồi idle (TFM-04) | Counter và bucket frontend dương nhưng không đổi từ mẫu đầu, như khi mọi request xong trước lần scrape đầu | Cổng consumer (`(query) > bool 0`) cho `frontend 0` ở cả mẫu số, P99 (NaN) và Nemesis `0`, tại 30s, 1m và 2m. Cổng **không** đạt |
| **(16:25)** Hai lần scrape đã xác nhận (TFM-04) | Series xuất hiện ở 30s với 3 request, lên 6 ở 45s, rồi đứng yên | Tại 50s cả ba cổng `1`. Tại 1m50s (65s không có request mới), cửa sổ 1m của Gaia hết tăng: mẫu số và P99 về `0`; cửa sổ 2m của Nemesis vẫn `1`. Vì vậy query phải chạy ngay sau lần scrape thứ hai |

Các cổng dùng `> bool 0`, đúng điều kiện của `verify --check consumers`: NaN cho `0`; không có series thì không có mẫu.

`fuzzy_compare: true` được bật vì `rate()` trên counter tuyến tính trả `4.999999999999999` cho 5. Mutation ở bảng trên chứng minh so sánh xấp xỉ vẫn bắt được sai giá trị và sai nhãn.

`evaluation_interval: 15s` (bằng chu kỳ scrape) được đặt từ lượt này. promtool chỉ nạp mẫu tới bước đánh giá cuối, mặc định mỗi 1m. Với mặc định, query lúc 1m50s không thấy mẫu sau 60s; đã kiểm bằng `timestamp()`. Ba nhóm cũ đánh giá ở 5m nên không bị ảnh hưởng, và vẫn đạt sau thay đổi.

### 8.2 Chưa chứng minh được, sẽ chạy khi triển khai (`verify-local-lab.sh --check ingress`)

1. Deployment `traefik` rollout xong.
2. `127.0.0.1:8080/_healthz` → 200 qua Traefik.
3. `/nemesis/healthz` và `/hephaestus/healthz` → 200 với `"kafka_connected"`, chứng minh rewrite hoạt động.
4. Request sentinel `zd-ingress-sentinel-<run>%20probe?run=<run>` (có header XFF giả):
   - xuất hiện trong log pod Traefik;
   - `ServiceName` có `@kubernetes`;
   - `ClientHost` không phải `192.0.2.10`;
   - in ra `ClientHost`, `ClientAddr` và `RequestPath` để ghi dạng mã hóa thực tế.
5. Sentinel đó vào Elasticsearch với `container_name:traefik` trong 60s.
6. Pod busybox tạm (`--rm`) trong `target-app` gọi `traefik.kube-system` với sentinel riêng. `ClientHost` phải bằng IP của pod.
7. **Hợp đồng nhãn (TFM-01):** ServiceMonitor thật `kube-system/traefik` có `honorLabels` = `true`. Đọc log Traefik lỗi thì in lỗi đó, không chỉ báo "không thấy entry".

Các mục 8–10 là check `consumers`. Check này chạy ở cuối `ingress` (và `all`), sau mọi lần chờ Elasticsearch và pod, nên cửa sổ query không bị trôi. Cũng chạy riêng được bằng `--check consumers`.

8. **Request lành qua hai lần scrape đã xác nhận (TFM-04):**
   - Đọc mẫu đầu của `traefik_service_requests_total` và `traefik_service_request_duration_seconds_count` cho `target-app-frontend-80@kubernetes`. Chưa có series thì ghi `absent`.
   - Mỗi vòng gửi 3 request `GET :8080/_healthz`; cả 3 phải trả 200.
   - Sau đó poll Prometheus (tối đa 9 lần, mỗi 5s) tới khi **cả hai** counter lớn hơn mẫu trước. Mẫu mới là một lần scrape đã chứa request của vòng đó.
   - Sau mẫu đã xác nhận đầu tiên mới gửi vòng tiếp theo. Như vậy luôn có hai mẫu khác nhau, cách nhau một chu kỳ scrape, và nằm trong cửa sổ 1m.
   - Giới hạn: tối đa 4 vòng, tức 12 request; thời gian chờ tối đa khoảng 3 phút.
   - Counter không tăng (idle, hoặc chỉ một loạt request trước lần scrape đầu) thì FAIL, và query consumer **không** được đánh giá.
9. **Consumer (TFM-02):** ngay sau lần scrape đã xác nhận thứ hai, chạy đúng các query đọc từ source qua `zd_agent_queries`.
   - Mẫu số error rate Gaia (1m) cho `frontend` phải > 0.
   - P99 Gaia (1m) cho `frontend` phải hữu hạn và > 0; NaN không đạt.
   - `http_rps` của Nemesis (2m) phải > 0.
   - Chưa đạt thì gửi thêm một vòng, chờ lần scrape tiếp theo rồi đánh giá lại, trong giới hạn 4 vòng.
   - Không nới query hay ngưỡng để test đạt.
   - Tử số 5xx, tỷ lệ và `error_rate` của Nemesis chỉ được in ra. Rỗng nghĩa là chưa có 5xx; check không đòi có 5xx.
10. **Tên nhãn:** `/api/v1/labels` của `traefik_service_.+` có `service` và không có nhãn `exported_*`. Kiểm sau các lần scrape ở mục 8, nên series chắc chắn đã có.

`--check agents` kiểm thêm log Gaia 10 phút gần nhất không có dòng `Error querying Prometheus` hay `Prometheus query returned status`. `/healthz` của Gaia không chạy query nào, nên log là bằng chứng consumer đã chạy. Log được lấy riêng và kiểm exit trước khi lọc (TFM-05): `kubectl logs` lỗi thì FAIL `cannot read the Gaia log, query errors unknown: …`; chỉ "đọc được và không có dòng lỗi" mới PASS.

`--check all` gồm mọi check trên. FAIL đã biết của `frontend`/`frontend-external` (frontend v0.10.5 không có `/metrics`) cho exit 3. Mọi FAIL khác cho exit 1.

Check không tạo tải, không gọi attack, heal, reset hay LLM. Tổng cộng tối đa 17 request HTTP tới ingress: 5 request kiểm route và IP (4 từ host, 1 từ pod), cộng tối đa 12 request lành cho cổng consumer. Ngoài ra chỉ có query Prometheus/Elasticsearch và 1 pod busybox.

## 9. Kế hoạch triển khai sau khi Codex retest đạt (một lượt, không hỏi từng bước)

Mọi lệnh dùng context `k3d-zero-door` với namespace và release rõ ràng. Script tự kiểm `desktop-linux` và từ chối `DOCKER_HOST`. Mỗi bước được chạy riêng và so exit với cổng của chính bước đó; không chạy theo kiểu fail-fast cả lô. Vì vậy exit 3 đã biết không làm dừng trước rebuild, nhưng cũng không bỏ qua chung chung các exit khác 0.

| Bước | Lệnh / hành động | Cổng để đi tiếp |
| --- | --- | --- |
| 0. Preflight, snapshot | Khối lệnh **S** bên dưới (chỉ đọc, context ghi rõ trong từng lệnh); `measure.sh` gồm RAM host và PSI | `docker context show` là `desktop-linux`, không có `DOCKER_HOST`; mọi lệnh S exit 0. RAM trống của host ≥ 1 GiB |
| 1. Áp patch, regression | `git apply --whitespace=error-all` patch hạ tầng rồi patch agent (Hoàng đã duyệt), sau khi so SHA-256 hai file patch với mục 1. `bash tests/shell/run.sh`. `ZD_PROMTOOL=… bash tests/shell/test-local-restore.sh` | 32/32 và exit 0. Chưa đổi gì trong cluster |
| 2. Giải phóng port 80 | `bash infrastructure/scripts/setup-local-apps.sh --component target`: apply `frontend-external` ClusterIP và `frontend-ingress` | DaemonSet `svclb-frontend-external-*` biến mất trong 2 phút (K3s gỡ). Từ đây tới bước 3, `:8080` tạm không phục vụ |
| 3. Cài Traefik | `bash infrastructure/scripts/setup-phase1.sh --component ingress` (script gọi `zd_helm`, tức `helm --kube-context=k3d-zero-door upgrade --install traefik … --skip-crds --wait`; không `--atomic`/`--cleanup-on-fail`) | Helm exit 0. Pod Ready. DaemonSet `svclb-traefik-*` Ready 2/2 |
| 4. Ingress agent | Khối lệnh **I** bên dưới: tách **chỉ document Ingress** của Nemesis và Hephaestus từ manifest đã sửa (giống file đã dry-run), rồi apply với context rõ ràng. Không apply cả `nemesis-deployment.yaml` vì có Secret | File tách có đúng 2 document `kind: Ingress`; `kubectl` exit 0 |
| 5. Chẩn đoán trước build | `verify-local-lab.sh --check ingress` (gồm `consumers` ở cuối) | Exit **0**. Check này không có FAIL đã biết. Lúc này agent còn chạy image cũ, nên bước này chỉ chứng minh dữ liệu Prometheus và query đọc từ source đúng, chưa chứng minh agent. Cổng consumer tự tạo hai lần scrape có request mới (mục 8.2), nên không phụ thuộc lưu lượng có sẵn. FAIL thì dừng, không build |
| 6. Rebuild agent | `setup-local-apps.sh --component gaia`; `rebuild-nemesis.sh --no-forward`. Hai script build, import, restart và kiểm image ID của pod bằng `zd_verify_image` | Cả hai exit 0. Không chạy khi đang đo; theo dõi PSI (lần trước build Gaia làm emailservice restart một lần) |
| 7. **Kiểm cuối (bằng chứng duy nhất được tính)** | Chờ ≥ 2 phút sau khi rollout agent xong, để có ≥ 8 vòng poll Gaia 15s và đầy cửa sổ 2m của Nemesis. Sau đó chạy `verify-local-lab.sh --check all` | Exit **0**, hoặc exit **3** mà các dòng FAIL đúng bằng hai dòng `FAIL (known) scrape target target-app/frontend…` và `…/frontend-external…`. Exit 1 thì dừng và báo |
| 8. Đối chiếu restart và tài nguyên | So số restart với snapshot bước 0; chạy lại `measure.sh` | Chỉ pod mới của chính lượt này (Traefik, Gaia, Nemesis) được khác snapshot, và đều 0 restart. Pod khác tăng restart thì ghi là regression và báo, không coi là đạt |
| 9. Ghi kết quả | Output nguyên văn của bước 5–8 vào tài liệu này hoặc `lab-restoration.md`; bàn giao Codex | — |

**Điểm dừng chung:**
- context hoặc Docker không khớp;
- RAM trống của host dưới 1 GiB;
- PSI memory avg60 trên 2;
- bất kỳ cổng nào ở bảng trên không đạt.

Khi dừng, ghi lại hiện trạng (có cả chủ sở hữu port 80, khối lệnh P ở mục 10) và báo Codex/Hoàng. Không tự rollback.

Lệnh mẫu, chạy trong Git Bash từ root checkout. Mọi lệnh `kubectl`/`helm` ghi rõ `--context`/`--kube-context k3d-zero-door`; không lệnh nào đổi current-context của người dùng (TFM-06).

```bash
# S — snapshot chỉ đọc (bước 0, R0)
docker context show
kubectl --context k3d-zero-door get svc,ingress,ingressclass,ds -A -o wide
kubectl --context k3d-zero-door get pods -A -o 'custom-columns=NS:.metadata.namespace,POD:.metadata.name,RESTARTS:.status.containerStatuses[*].restartCount'
helm --kube-context k3d-zero-door list -A
```

```bash
# I — chỉ document Ingress của agent (bước 4; R5 dùng cùng cách trên manifest đã revert, thêm target-app-ingress.yaml)
mkdir -p scratch/zer35/deploy
python -c 'import sys,yaml; docs=[d for f in sys.argv[1:] for d in yaml.safe_load_all(open(f, encoding="utf-8")) if d and d["kind"]=="Ingress"]; print(yaml.safe_dump_all(docs, sort_keys=False), end="")' \
    infrastructure/manifests/nemesis-deployment.yaml infrastructure/manifests/hephaestus-deployment.yaml \
    > scratch/zer35/deploy/agent-ingresses.yaml
grep -c '^kind: Ingress$' scratch/zer35/deploy/agent-ingresses.yaml   # phải là 2
kubectl --context k3d-zero-door apply -f scratch/zer35/deploy/agent-ingresses.yaml
```

## 10. Rollback trong giới hạn sở hữu (TFM-03)

Port 80 của node chỉ một Service LoadBalancer giữ được tại một thời điểm, qua DaemonSet svclb của K3s. Vì vậy rollback **phải giải phóng port khỏi Traefik trước**, sau đó mới trả `frontend-external` về LoadBalancer. Chưa qua bước R2 thì rollback **chưa hoàn tất**: không được báo `:8080` đã phục hồi.

| Bước | Hành động | Quyền | Cổng / kiểm |
| --- | --- | --- | --- |
| R0 | Khối S (mục 9) và khối P bên dưới. Xác định trạng thái: Service `kube-system/traefik` có tồn tại và là LoadBalancer không; DaemonSet svclb nào đang có | Chỉ đọc | — |
| R1 | Nếu Traefik đang giữ port: `bash infrastructure/scripts/setup-phase1.sh --component ingress --ingress-cluster-ip`. Wrapper này kiểm Docker `desktop-linux`, từ chối `DOCKER_HOST`, gọi `kubectl --context=k3d-zero-door get nodes`, rồi chạy `helm --kube-context=k3d-zero-door upgrade traefik traefik --repo https://traefik.github.io/charts --version 42.0.0 -n kube-system --skip-crds -f …/traefik-values.yaml --wait --timeout 5m --set service.spec.type=ClusterIP` với Helm home trong `scratch/`. Không `--install`, không uninstall. Chạy **trước** `git apply -R`, khi values file và cờ còn tồn tại. Argv được kiểm trong `run.sh`; render tương ứng nằm trong `test-local-restore.sh` và đã qua dry-run phía server | Upgrade release của chính lab: thuộc quyền đã giao | Script exit 0 |
| R2 | Khối P: không còn DaemonSet `svclb-traefik-*`, và không còn Service LoadBalancer nào khai port 80. `curl 127.0.0.1:8080` lúc này dự kiến không có phản hồi | Chỉ đọc | svclb-traefik biến mất trong 2 phút. Không đạt thì **dừng: rollback chưa hoàn tất**, báo Hoàng/Codex. Bước giải phóng tiếp theo (uninstall) cần Hoàng duyệt |
| R3 | `git apply -R --whitespace=error-all` patch agent rồi patch hạ tầng. `bash infrastructure/scripts/setup-local-apps.sh --component target`: apply `target-app.yaml`, đưa `frontend-external` về LoadBalancer | Apply manifest trong allowlist | DaemonSet `svclb-frontend-external-*` Ready 2/2 |
| R4 | Khối R4: probe `127.0.0.1:8080/_healthz` với query sentinel riêng. Đọc log Traefik (kiểm exit riêng) và xác nhận **không** có sentinel, tức request đi thẳng qua `frontend-external` | Chỉ đọc | HTTP 200, đọc được log Traefik, và log không có sentinel. Không đọc được log thì R4 chưa đạt. Chỉ từ đây mới được báo đường host đã phục hồi |
| R5 | Khối I trên manifest đã revert, thêm `target-app-ingress.yaml`: apply lại document Ingress cũ (class `nginx`, không controller) của Nemesis, Hephaestus và `frontend-ingress`, không có Secret. Làm sau R4 nên không có khoảng mất route nào phụ thuộc Traefik | Apply manifest | File tách có đúng 3 document `kind: Ingress`; `kubectl` exit 0 |
| R6 | Build lại Gaia và Nemesis từ source đã revert (`setup-local-apps.sh --component gaia`, `rebuild-nemesis.sh --no-forward`, có kiểm image ID). Rồi chạy `verify-local-lab.sh --check all` của bản đã revert | Build/rollout workload của lab | Kỳ vọng bằng trạng thái trước migration: exit khác 0 chỉ vì hai target frontend. Bản cũ chưa có exit 3, nên phải đọc từng dòng FAIL |
| R7 | Release `traefik` vẫn còn: Service ClusterIP, không giữ port, không có Ingress class `traefik`. Gỡ hẳn bằng `helm --kube-context k3d-zero-door uninstall traefik -n kube-system` **chỉ khi Hoàng duyệt**. Lệnh này xóa đúng 9 object của release | Cần Hoàng | Không cần cho việc phục hồi đường host |

- Nếu lỗi xảy ra **giữa** bước 2 và 3 (ví dụ Helm lỗi trước khi Service Traefik có port): ở R0 nếu không có `svclb-traefik-*` thì bỏ R1–R2, đi thẳng R3.
- Nếu Helm đã tạo Service LoadBalancer thì làm R1 trước.
- Không có gì khác cần dọn: không có CRD, PVC, Secret hay dữ liệu. Không đụng Traefik built-in của K3s; cluster vẫn giữ `--disable=traefik`. Không xóa image hay cache.
- Không thêm lệnh tự động xóa release, PVC, Secret hay CRD. Review này không chạy bước rollback nào.

```bash
# P — chủ sở hữu port 80 (R0, R2; cũng dùng khi dừng ở mục 9). Chỉ đọc.
kubectl --context k3d-zero-door get ds -n kube-system -o name
kubectl --context k3d-zero-door get svc -A \
    -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name} {.spec.ports[*].port}{"\n"}{end}'
# R2 đạt khi lệnh đầu không còn daemonset.apps/svclb-traefik-* và lệnh sau không có dòng nào chứa port 80.

# R1 — giải phóng port 80, giữ release (wrapper có guard; không dùng helm trần)
bash infrastructure/scripts/setup-phase1.sh --component ingress --ingress-cluster-ip

# R4 — host đi thẳng tới frontend-external, không qua Traefik
sentinel="zd-rollback-$(date +%Y%m%d%H%M%S)"
curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8080/_healthz?$sentinel"   # phải là 200
if logs=$(kubectl --context k3d-zero-door logs deployment/traefik -n kube-system --since=5m); then
    grep -c -F "$sentinel" <<<"$logs" || true   # phải là 0
else
    echo 'Không đọc được log Traefik: R4 chưa đạt'
fi
```

Thứ tự trong bảng là ràng buộc: R1 dùng cờ và values chỉ có sau khi áp patch, nên phải chạy trước R3 (`git apply -R`).

## 11. Quyết định cần Codex/Hoàng

1. **Codex retest** patch hạ tầng: TFM-04–07 (mục 13), TFM-01–03 (mục 12), cùng các điểm lượt trước:
   - thêm `traefik-values.yaml` và xóa `ingress-nginx-values.yaml`;
   - `frontend-external` sang ClusterIP;
   - không tạo CRD;
   - ClusterRole đọc Secret toàn cluster.

   Thêm `lib/common.sh` (hàm `zd_agent_queries`) và `tests/shell/test-local-restore.sh`; cả hai đều có tên trong allowlist.
2. **Đã quyết (18/10/2026):** Hoàng duyệt patch agent cùng gói. Cả hai patch triển khai sau khi Codex retest đạt. Patch agent không đổi trong lượt sửa này.
3. Flood đi vòng qua ingress (7.2), chữ ký SQLi trên URL đã encode (6) và `BLOCK_IP` thiếu IP nguồn (7.3) đã có phạm vi trong delivery, theo review Codex. Khi tới lượt sẽ đối chiếu với issue hiện có; ghi chú migration này không tạo issue trùng.

Các mục sau **không** cần quyết định: version chart, values, thứ tự triển khai, probe. Chúng nằm trong quyền vận hành đã giao và do Codex review.

## 12. Phản hồi review Codex 14:52

| Finding | Sửa | Bằng chứng |
| --- | --- | --- |
| **TFM-01 HIGH**: nhãn backend bị đổi thành `exported_service` | Values: `serviceMonitor.honorLabels: true`, có comment giải thích. Không đổi tên nhãn nên rule, query agent, probe và ngưỡng/cửa sổ/logic quyết định giữ nguyên. Regression ở 3 lớp: values (`run.sh`), render của chart pin (`test-local-restore.sh`), live (`verify --check ingress` đọc `honorLabels` của ServiceMonitor thật và tên nhãn qua `/api/v1/labels`). Promtool có nhóm dữ liệu dạng `exported_service` chứng minh mọi consumer rỗng nếu thiếu cấu hình này | Render: endpoint `honorLabels: true`; dry-run phía server đạt; mutation bỏ `honorLabels` làm cả hai test FAIL (mục 8.1) |
| **TFM-02 MEDIUM**: thiếu kiểm tích hợp sau rollout agent | Kế hoạch mục 9 có cổng cho từng bước. Kiểm cuối (bước 7) chạy **sau** cả hai rebuild và chờ đủ cửa sổ; kết quả trước build chỉ là chẩn đoán. `verify` thêm: counter và histogram phải tăng giữa các lần scrape; query consumer đọc từ source với cửa sổ 1m/2m, phân biệt “chưa có 5xx” với “thiếu metric backend”; log Gaia không có lỗi query. Exit 3 chỉ dành cho đúng hai target frontend lỗi 404; FAIL mới vẫn cho exit 1. Đối chiếu restart với snapshot. Case offline (promtool): frontend, `redis-cart` có dấu gạch nối, namespace khác, 5xx và độ trễ mẫu, lưu lượng lành. Không gọi LLM/attack/heal | `run.sh` 29/29 (gồm 4 case exit code); promtool `SUCCESS`; probe thật `telemetry` exit 3 với đúng hai dòng known, `agents` exit 0 |
| **TFM-03 MEDIUM**: rollback chưa giải phóng port 80 | Mục 10 viết lại theo thứ tự: giải phóng port bằng `helm upgrade … --set service.spec.type=ClusterIP` (thuộc quyền, không uninstall), kiểm chủ sở hữu port, rồi mới trả `frontend-external` về LoadBalancer và probe `:8080` kèm đối chiếu log Traefik. Chưa qua R2 thì không báo đã phục hồi. Uninstall vẫn cần Hoàng. Values bỏ `externalTrafficPolicy` tường minh (mặc định đã là `Cluster`), để lệnh R1 chỉ cần một `--set` | `test-local-restore.sh` kiểm render rollback (ClusterIP, không `externalTrafficPolicy`, cùng loại object); dry-run phía server của render rollback đạt |

## 13. Phản hồi retest Codex 15:54

| Finding | Sửa | Bằng chứng |
| --- | --- | --- |
| **TFM-04 MEDIUM**: probe có thể FAIL trên ingress mới và khỏe, vì một loạt request có thể kết thúc trước lần scrape đầu (rate 0, P99 NaN) | Tách phần metric thành check `consumers`, chạy ở **cuối** `ingress`/`all`, sau mọi lần chờ Elasticsearch/pod. Mỗi vòng gửi 3 request lành `GET /_healthz`, rồi poll tới khi cả counter request lẫn `_count` histogram vượt mẫu trước: đó là lần scrape đã chứa request. Chỉ sau mẫu đã xác nhận mới gửi vòng tiếp theo. Query Gaia/Nemesis đọc từ source chạy **ngay sau** lần scrape đã xác nhận thứ hai, khi cả hai mẫu còn trong cửa sổ 1m. Chưa đạt thì thêm một vòng và đánh giá lại. Giới hạn 4 vòng (12 request), 9 lần poll mỗi vòng. Cổng chặt hơn trước: mẫu số và P99 của `frontend` phải hữu hạn và > 0; `http_rps` > 0. Counter không tăng thì không đánh giá consumer. Query, ngưỡng và cửa sổ của agent giữ nguyên. Nhãn `exported_*` kiểm sau các lần scrape này | `run.sh` (mock Prometheus có mô hình scrape: query thấy lần scrape trước, scrape lấy mọi request đã gửi): cold start đạt sau đúng 2 vòng, thứ tự `QCCCQQCCCQQ` (request sau scrape đã xác nhận); idle FAIL, không đánh giá consumer; query luôn rỗng FAIL sau 12 request; request trả 502 FAIL. Promtool: nhóm cold start/idle (cổng `0` ở 30s, 1m, 2m, đúng dữ liệu Codex tái hiện) và nhóm hai lần scrape (đạt ở 50s; Gaia hết dữ liệu ở 1m50s). Mutation chỉ gửi request ở vòng đầu làm `run.sh` FAIL |
| **TFM-05 MEDIUM**: không đọc được log Gaia vẫn PASS | Lấy log riêng và kiểm exit trước khi lọc. Lỗi lấy log là FAIL `cannot read the Gaia log, query errors unknown: …`. Chỉ khi đọc được mới lọc chuỗi lỗi; grep không khớp (exit 1) khác lỗi grep. Cùng cách cho log Traefik trong `ingress`: lỗi đọc log được in ra thay vì "không thấy entry" | `run.sh` 3 case: log sạch exit 0; log có `Error querying Prometheus` exit 1; `kubectl logs` lỗi exit 1, có dòng FAIL và không có `PASS Gaia log`. Mutation `2>/dev/null \|\| true` làm `run.sh` FAIL ở đúng case thứ ba |
| **TFM-06 MEDIUM**: lệnh rollback R1 không khóa Kubernetes context | R1 không còn là lệnh `helm` trần mà là `setup-phase1.sh --component ingress --ingress-cluster-ip`. Wrapper này có cùng guard Docker/`DOCKER_HOST`, chạy `kubectl --context=k3d-zero-door get nodes`, gọi `zd_helm` với `--kube-context=k3d-zero-door` và Helm home trong `scratch/`. Lệnh là `upgrade` thường (không `--install`). Cờ đi với component khác thì exit 2 trước mọi CLI. Mọi lệnh mẫu khác ở mục 9–10 (snapshot, chủ port, tách Ingress, R4, R7) ghi rõ context; không lệnh nào đổi current-context | `run.sh`: argv R1 có `--kube-context=k3d-zero-door upgrade traefik traefik … --version 42.0.0 -n kube-system --skip-crds … --set service.spec.type=ClusterIP`, không `--install`/`uninstall`, cache trong `scratch/helm/cache`; Docker context sai thì không gọi Helm; cờ sai component không gọi CLI. Mutation gọi `helm` trực tiếp làm `run.sh` FAIL. Lint lệnh mẫu mục 9–10 đạt (mục 8.1) |
| **TFM-07 LOW**: test nhãn phụ thuộc chuyển path ngầm của MSYS | Đường dẫn values đưa cho Python được đổi bằng `cygpath -m` khi có (Git Bash), giữ nguyên trên Linux. Không đổi giá trị `honorLabels` | `run.sh` đạt ở cả môi trường sạch và khi đặt `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL=*`. Bỏ `cygpath` rồi chạy với path conversion tắt thì tái hiện đúng `FileNotFoundError` Codex báo. `test-local-restore.sh` source `common.sh`, vốn luôn bật chế độ này trên Windows, và đạt |

Ngoài phạm vi finding, không đổi: chart, values, manifest, rule, patch agent (hash giữ nguyên), quyết định Traefik và kế hoạch triển khai ngoài các lệnh mẫu. Flood/SQLi/`BLOCK_IP` vẫn theo mục 11.3; không tạo issue mới.

## 14. Lần triển khai 18/10/2026, 16:42–16:45 +07:00: dừng ở bước 0

Codex retest lúc 16:38 cho kết quả READY. Claude bắt đầu mục 9 và **dừng ở cổng bước 0**. Không áp patch, không chạy lệnh nào thay đổi cluster, không rollback.

| Kiểm | Kết quả | Cổng |
| --- | --- | --- |
| HEAD, staged | `1f43ff1461c2…`, staged rỗng | Khớp retest |
| SHA-256 hai patch | Infra `03ab4a6c…ff53f`, agent `b9e83cd9…ca99a0` | Khớp mục 1 |
| 15 file gốc | `sha256sum -c base-sha256.txt`: 15/15 OK | Đầu vào không đổi |
| `git apply --check --whitespace=error-all` | Cả hai patch đạt | Đạt |
| Docker, `DOCKER_HOST` | `desktop-linux`; không có `DOCKER_HOST` | Đạt |
| Khối S | 4 lệnh, đều exit 0. Output ở `scratch/zer35/deploy/step0-S.txt` | Đạt |
| WSL `docker-desktop` | MemAvailable 2,30 GiB; PSI memory avg60 0,18 | Đạt (≥ 1 GiB, ≤ 2) |
| **Host Windows, RAM trống** | `MemFree` của Git Bash lúc 16:42:48 là 684 MiB. Đo lại lúc 16:43:10, 16:43:41, 16:44:12, 16:44:43: 819, 823, 897, 749 MiB. CIM `FreePhysicalMemory` 609 MiB. Pagefile đang dùng 2983 MB (đỉnh 3885 MB), so với 2,62 GiB lúc 14:05 | **Không đạt (< 1 GiB ở cả 5 lần đo)** |

Snapshot đầy đủ: `scratch/zer35/raw/measure-deploy-before.txt`.

Tiến trình Windows chiếm bộ nhớ nhiều nhất (working set, gộp theo tên):

| Tiến trình | Working set |
| --- | --- |
| `vmmemWSL` | 3806 MiB |
| `chrome` (14 tiến trình) | 2544 MiB |
| `claude` | 1482 MiB |
| `ChatGPT` | 1290 MiB |
| `svchost` | 1128 MiB |
| `Zalo` | 468 MiB |
| `codex` | 418 MiB |

Claude không đóng ứng dụng nào của người dùng.

**Restart mới so với snapshot cuối của lab-restoration (14:03)**, ghi lại làm mốc cho bước 8. Lúc này chưa có thao tác triển khai nào:
- `target-app/cartservice` và `paymentservice` mỗi pod restart 1 lần, khoảng 15:23. Lần restart trước là `Error`.
- `zero-door/kafka-controller-0`: container `jmx-exporter` restart 2 lần, `OOMKilled`, khoảng 15:27.
- `emailservice` restart 1 lần như đã ghi trước đó.
- Event cảnh báo gần nhất: probe của `nemesis` và `cartservice` timeout lúc khoảng 15:58–16:09.

**Điều kiện để chạy lại:** Hoàng giải phóng RAM trên Windows sao cho `grep MemFree /proc/meminfo` (Git Bash) ổn định ≥ 1 GiB, ví dụ đóng bớt tab Chrome, ChatGPT hoặc Zalo. Khi đó Claude chạy lại mục 9 từ bước 0. Không cần Codex review lại: gói và đầu vào không đổi.

## 15. Triển khai 18/10/2026, 17:15–17:27 +07:00: mục 9 đạt toàn bộ

Hoàng giải phóng RAM Windows rồi yêu cầu chạy lại mục 9 từ bước 0 với guard giữ nguyên. Claude chạy từng bước theo đúng thứ tự, mỗi bước so với cổng của chính nó. Không có bước nào phải dừng, không rollback, không xóa gì. Đây là **kết quả probe cho Codex review runtime, chưa phải nghiệm thu nghiên cứu**; ZER-35 chưa Done.

| Bước | Giờ | Kết quả | Cổng |
| --- | --- | --- | --- |
| 0. Preflight | 17:15–17:16 | HEAD `1f43ff1`, staged rỗng; hai SHA-256 khớp mục 1; 15 file gốc OK; apply-check đạt; `desktop-linux`, không `DOCKER_HOST`; khối S 4 lệnh exit 0. Host `MemFree` 3,17–3,28 GiB (3 lần đo); WSL MemAvailable 2,31 GiB; PSI memory avg60 0,00 | Đạt |
| 1. Áp patch, regression | 17:16–17:18 | `git apply --whitespace=error-all` infra rồi agent: exit 0, exit 0. Cây làm việc trùng từng byte với cây round-trip đã kiểm (`rt47`). `run.sh` exit 0, 32/32 (65 s). `test-local-restore.sh` exit 0, 15 PASS, promtool SUCCESS | Đạt |
| 2. Giải phóng port 80 | 17:18:02 | `setup-local-apps.sh --component target` exit 0. `frontend-external` là ClusterIP; `frontend-ingress` được tạo. DaemonSet `svclb-frontend-external-*` đã biến mất ở lần kiểm đầu tiên (17:18:12) | Đạt |
| 3. Cài Traefik | 17:18:21–17:18:55 | `setup-phase1.sh --component ingress` exit 0. Release `traefik` revision 1, `deployed`, chart `traefik-42.0.0`, app v3.7.14. Pod 1/1, `svclb-traefik-*` 2/2 (port 80, 443). Image `docker.io/library/traefik@sha256:575fa15b…3fa7c`, khớp digest ở mục 3. Không có CRD nào chứa `traefik` | Đạt |
| 4. Ingress agent | 17:19 | File tách có đúng 2 document `kind: Ingress`, 0 Secret. Apply exit 0 (`configured` ×2). Cả ba Ingress đều class `traefik` | Đạt |
| 5. Chẩn đoán trước build | 17:19:17–17:20:24 | `--check ingress` exit **0**, 0 FAIL (output bên dưới) | Đạt |
| 6. Rebuild agent | 17:20:34–17:22:03 | `setup-local-apps.sh --component gaia` exit 0; `rebuild-nemesis.sh --no-forward` exit 0. `zd_verify_image` xác nhận image ID của pod. SHA-256 `/app/main.py` trong pod trùng source đã vá: Gaia `79db4d1a…2b02`, Nemesis `2f8a92e6…6221`. Guard trong lúc build: host `MemFree` thấp nhất 1,77 GiB; WSL MemAvailable 2,30–2,33 GiB; PSI memory avg60 cao nhất 0,50 | Đạt |
| 7. **Kiểm cuối** | 17:24:14–17:26:22 (2 phút 11 giây sau rollout Nemesis) | `--check all` exit **3**. Các dòng FAIL đúng bằng hai dòng `FAIL (known)` của `target-app/frontend` và `frontend-external` (output bên dưới) | Đạt |
| 8. Restart, tài nguyên | 17:26 | So với snapshot bước 0: chỉ khác ở `svclb-frontend-external` (đã gỡ) và các pod mới `svclb-traefik` ×2, `traefik`, `gaia`, `nemesis`, tất cả 0 restart. Restart cũ giữ nguyên: cartservice/emailservice/paymentservice 1, `jmx-exporter` của Kafka 3 (OOMKilled, có từ trước bước 0) | Đạt |

Tài nguyên sau triển khai (`measure-deploy-8.txt`, so với `measure-deploy-0.txt`):
- WSL MemAvailable 2,29 GiB (trước: 2,31 GiB); PSI memory avg60 0,31.
- Node agent-0: 2247 Mi, server-0: 2545 Mi (trước: 2159 Mi, 2594 Mi).
- Pod mới: Traefik 1m CPU / 53 Mi; Gaia 68 Mi; Nemesis 63 Mi; svclb ≤ 1 Mi.
- Host `MemFree` 2,35 GiB.

Event cảnh báo sau triển khai chỉ có readiness probe của pod Gaia/Nemesis **cũ** khi chúng đang dừng (`connection refused`, 17:20–17:22). Có thêm một timeout probe của Nemesis cũ lúc khoảng 17:13, trước bước 0.

Điểm cần Codex đọc khi review runtime:
- ClientHost của request đi từ host là `10.42.1.1`, tức địa chỉ SNAT của svclb/kube-proxy (`externalTrafficPolicy: Cluster`). Đây là giới hạn đã nêu ở mục 7; IP của client trong cluster vẫn được giữ (`10.42.1.35`).
- Lần scrape đã xác nhận đầu tiên ở bước 7 tăng 4 thay vì 3 (`11 → 15`), vì luồng mua hàng vừa chạy trước đó cũng gửi request qua đường đó. Cổng chỉ yêu cầu counter tăng.
- Cả hai bộ đếm 5xx đều rỗng trong cửa sổ, nên nhánh tử số lỗi chưa được kiểm trên dữ liệu thật.

Output nguyên văn ở `scratch/zer35/deploy/`: `step0-S-rerun.txt`, `step1-run.out`, `step1-restore.out`, `step2-target.out`, `step3-ingress.out`, `agent-ingresses.yaml`, `step5-ingress.out`, `step6-gaia.out`, `step6-nemesis.out`, `step7-all.out`. Snapshot tài nguyên ở `scratch/zer35/raw/measure-deploy-0.txt` và `measure-deploy-8.txt`.

Chưa commit, chưa push, chưa cập nhật Linear. Patch đang được áp trên working tree; rollback (nếu cần) theo mục 10 và phải được yêu cầu riêng.

### 15.1 Output bước 5 (`verify-local-lab.sh --check ingress`, exit 0)

```text
PASS Traefik rollout complete
PASS host :8080 frontend /_healthz HTTP 200
PASS /nemesis/healthz is rewritten to nemesis /healthz
PASS /hephaestus/healthz is rewritten to hephaestus /healthz
PASS Traefik access log (ClientHost ClientAddr RequestPath ServiceName status): 10.42.1.1 10.42.1.1:7431 /zd-ingress-sentinel-zd20261018171918675%20probe?run=zd20261018171918675 target-app-frontend-80@kubernetes 404
PASS host request was routed by the Kubernetes Ingress provider
PASS forged X-Forwarded-For is not recorded as ClientHost
PASS Traefik access log reached Elasticsearch (1 docs)
PASS in-cluster client address preserved: pod 10.42.0.20, Traefik ClientHost 10.42.0.20
PASS ServiceMonitor kube-system/traefik keeps backend labels (honorLabels: true)
PASS frontend requests/histogram count across 2 confirmed scrapes (6 requests): absent absent -> 6 6 -> 9 9
PASS traefik_service_* label names: __name__ code container endpoint instance job le method namespace pod protocol service
PASS Gaia error-rate denominator (1m) by service: frontend=0.08832000000000001
PASS Gaia P99 latency (1m) by service: frontend=0.00495
PASS Nemesis http_rps (2m): 0.04517
PASS 5xx in window: Gaia numerator 'none', ratio 'none', Nemesis error_rate 'absent' (empty = no 5xx)
Run zd20261018171918675 finished with 0 failure(s), 0 of them known (frontend /metrics 404).
PASS here is a probe result, not research acceptance.
```

### 15.2 Output bước 7 (`verify-local-lab.sh --check all`, exit 3)

```text
PASS home page HTTP 200
PASS product page HTTP 200
PASS add to cart HTTP 302
PASS cart lists the product
PASS checkout completed (order 1bf2ade4-cade-11f1-81ad-aaf956ec8b46)
PASS checkoutservice logged the mock payment
PASS Prometheus ready
FAIL (known) scrape target target-app/frontend down: server returned HTTP status 404 Not Found (frontend has no /metrics)
FAIL (known) scrape target target-app/frontend-external down: server returned HTTP status 404 Not Found (frontend has no /metrics)
PASS Kafka JMX metrics scraped
PASS target-app CPU series from cAdvisor: 9 containers
PASS log sentinel zd-log-sentinel-zd202610181724151389 found in Elasticsearch (2 docs)
PASS Kafka round trip on zd.verify.restore (correlation zd202610181724151389)
PASS topic attack.commands exists
PASS topic attack.results exists
PASS topic monitoring.alerts exists
PASS topic healing.actions exists
PASS topic system.logs exists
PASS gaia /healthz {"status":"UP","kafka_connected":true,"elasticsearch_connected":true,"prometheus_endpoint":"http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"}
PASS nemesis /healthz {"status":"UP","kafka_connected":true,"llm_provider":"gemini"}
PASS hephaestus /healthz {"status":"UP","k8s_connected":true,"kafka_connected":true,"cooldowns_active":0}
PASS chaos-worker rollout complete
PASS Gaia log read; no Prometheus query error in the last 10 minutes
PASS probe pod reaches frontend (control flow)
PASS target-app to Elasticsearch:9200 is blocked
PASS Traefik rollout complete
PASS host :8080 frontend /_healthz HTTP 200
PASS /nemesis/healthz is rewritten to nemesis /healthz
PASS /hephaestus/healthz is rewritten to hephaestus /healthz
PASS Traefik access log (ClientHost ClientAddr RequestPath ServiceName status): 10.42.1.1 10.42.1.1:2399 /zd-ingress-sentinel-zd202610181724151389%20probe?run=zd202610181724151389 target-app-frontend-80@kubernetes 404
PASS host request was routed by the Kubernetes Ingress provider
PASS forged X-Forwarded-For is not recorded as ClientHost
PASS Traefik access log reached Elasticsearch (1 docs)
PASS in-cluster client address preserved: pod 10.42.1.35, Traefik ClientHost 10.42.1.35
PASS ServiceMonitor kube-system/traefik keeps backend labels (honorLabels: true)
PASS frontend requests/histogram count across 2 confirmed scrapes (6 requests): 11 11 -> 15 15 -> 18 18
PASS traefik_service_* label names: __name__ code container endpoint instance job le method namespace pod protocol service
PASS Gaia error-rate denominator (1m) by service: frontend=0.20001333422228149
PASS Gaia P99 latency (1m) by service: frontend=0.00955
PASS Nemesis http_rps (2m): 0.08571836754131149
PASS 5xx in window: Gaia numerator 'none', ratio 'none', Nemesis error_rate 'absent' (empty = no 5xx)
Run zd202610181724151389 finished with 2 failure(s), 2 of them known (frontend /metrics 404).
PASS here is a probe result, not research acceptance.
```
