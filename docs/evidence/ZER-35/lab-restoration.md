# ZER-35 — Khôi phục lab local trọn gói

**Kết luận hiện hành:** Đã sửa và kiểm chứng gói khôi phục lab: kiểm tích hợp sau rollout cuối exit 0 (18:37:51 +07:00), 31 mẫu quan sát 18:36:31–18:51:48 không restart/thay pod ngoài dự kiến, không mất Ready hoặc scrape target down. Kết quả và giới hạn ở mục 12. Chưa có review độc lập/merge/chấp nhận để đặt Linear Done.

**Mốc lịch sử 13:16–14:10:** PARTIAL. Stack nền đã chạy trên `k3d-zero-door` và có đường dựng lặp lại bằng Bash. Đã có kết quả thật cho giao dịch mẫu tới checkout, Prometheus/cAdvisor/Kafka JMX, log qua Fluent Bit → Elasticsearch, Kafka produce/consume, `/healthz` của ba agent và hiệu lực NetworkPolicy.

Tại mốc lịch sử này còn bốn điểm (xem mục 12 cho kết quả xử lý hiện hành):
1. Ingress chờ Hoàng chọn controller. *Cập nhật 14:40: Hoàng chọn Traefik; gói phạm vi chờ Codex review, chưa triển khai: [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md).*
2. Hai target Prometheus của frontend luôn down (frontend không có `/metrics`).
3. Guard tài nguyên phía host bị vượt trong lúc dựng mà không được phát hiện kịp.
4. Code mới cần Codex review, merge và Hoàng chấp nhận.

Không đặt Linear Done.

Người thực hiện: Claude Code. Người review: Codex. Người chấp nhận: Hoàng. Phạm vi: [handoff ZER-35 trọn gói](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/claude-lab-review-and-sizing.md). Thời gian: 18/10/2026, 13:16–14:10 +07:00.

## 1. Revision, giới hạn đọc và nhãn bằng chứng

- **Git:** `main`, HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975` ở đầu và cuối phiên; staged rỗng ở cả hai thời điểm. Đầu phiên: 57 dòng `git status --short --untracked-files=all`, toàn bộ là dirty có trước (migration Bash, evidence, handoff). Danh sách và SHA-256 của mọi file dirty được lưu ở `scratch/zer35/status-start.txt` và `hash-start.txt` (gitignored).
- **Linear:** chưa đọc live ZER-35/ZER-6. Phiên Claude không có connector `linear_zero_door` đã xác minh; không dùng connector Linear khác. AC lấy theo snapshot trong handoff. Live state: chưa xác minh.
- **GitNexus:** không dùng. Index cũ hơn HEAD và không bao phủ file Bash untracked. Mọi kết luận dựa trên đọc source trực tiếp, render chart và runtime.
- **Nhãn:** LIVE = đo hoặc probe trên cluster trong phiên này; RENDER = `helm template`, không phải admission; MOCK = test CLI giả lập; INFERENCE = suy luận chưa đo.

## 2. AC → probe → kết quả

| AC | Probe | Kỳ vọng | Thực tế (LIVE) | Artifact | Kết quả |
| --- | --- | --- | --- | --- | --- |
| ZER-35: Kubernetes API truy cập | Preflight của mọi script: Docker `desktop-linux`, `kubectl get nodes` | 2 node Ready, đúng context | 13:16 và ở mỗi bước: 2 node Ready, `v1.31.5+k3s1`; current-context vẫn `k3d-zero-door`, không bị đổi | `scratch/zer35/raw/measure-*.txt` | PASS |
| ZER-35: chọn đường restore theo inventory, bảo toàn dữ liệu | Inventory đầu phiên: chỉ 3 pod hệ thống, không PV/PVC/release | Dựng tiếp trên cluster có sẵn, không recreate, không xóa | Không recreate, không xóa namespace/PVC/Secret/CRD/image. Ba PVC mới (Prometheus 2Gi, Elasticsearch 5Gi, Kafka 2Gi) đều Bound | Mục 7 | PASS |
| ZER-35: đường dựng lặp lại | Chạy lại `namespaces`, `setup-local-apps --component target`, `--component kafka` (helm upgrade), `setup-phase3.sh` sau khi đã đủ stack | Không lỗi, không trôi cấu hình, quota admit | namespace/target `unchanged`; Kafka revision 2 deployed, Job provisioning admit ở 896Mi; phase3 đạt đỉnh 960Mi với hai surge, không có `FailedCreate`; image ID khớp | `rerun*.txt`, `upgrade-kafka*.txt` | PASS (không wipe cluster) |
| ZER-35: profile tài nguyên đo được | Đo sau mỗi nhóm | Có usage thật theo nhóm | Bảng ở mục 5 | `measure-00…08` | PASS có giới hạn (guard host, mục 5.3) |
| ZER-35: kiểm đúng chức năng script | `bash tests/shell/run.sh` | Mọi nhóm PASS | 26/26 PASS, 37s (MOCK) | `tests-final.txt` | PASS (MOCK) |
| ZER-6 AC-03: Online Boutique ≥5 dịch vụ và luồng mua hàng | `verify-local-lab.sh --check purchase` qua tunnel `127.0.0.1:18080` | Trang chủ, sản phẩm, thêm giỏ, giỏ, checkout hoàn tất; payment mock có log | 9 dịch vụ Running. Trang chủ 200, sản phẩm 200, thêm giỏ 302, giỏ có sản phẩm. Checkout hoàn tất (order `d603a096-cac1-11f1-81ad-aaf956ec8b46`); `payment went through (transaction_id …)`; emailservice nhận yêu cầu gửi xác nhận | `verify-all-2.txt`, `verify-purchase-3.txt` | PASS qua loopback; **đường Ingress chưa kiểm** |
| ZER-6 AC-03: Prometheus | `--check telemetry` | Ready, không target down, có metric app | Ready; 9 chuỗi CPU cAdvisor cho target-app; Kafka JMX `up=1` (1146 series). **Down: `frontend`, `frontend-external`** (HTTP 404, mục 8) | `verify-telemetry-2.txt` | PARTIAL |
| ZER-6 AC-03: Elasticsearch/log | `--check logs`: request tới path sentinel duy nhất, đếm trong `zero-door-logs-*` | Sentinel có trong ES trong 60s | Tìm thấy 2 document (trước và sau khi apply policy) | `verify-logs-2.txt`, `verify-logs-post-policy.txt` | PASS |
| ZER-6 AC-03: Kafka | `--check kafka`: produce/consume correlation ID trên `zd.verify.restore`, liệt kê topic | Round-trip đúng ID; đủ 5 topic | Round-trip đúng; `attack.commands`, `attack.results`, `monitoring.alerts`, `healing.actions`, `system.logs` đều có | `verify-kafka-3.txt` | PASS |
| Agent health (baseline) | `--check agents`: GET `/healthz` qua service proxy; rollout chaos-worker | `kafka_connected:true` | gaia: Kafka + ES true; nemesis: Kafka true, `llm_provider` gemini với Secret rỗng; hephaestus: k8s + Kafka true, 0 cooldown; worker sẵn sàng nghe `attack.commands` | `verify-agents-1.txt` | PASS (health, không phải AI hoạt động) |
| NetworkPolicy có hiệu lực | `--check policies`: pod busybox tạm trong `target-app`, trước và sau khi apply | Trước: ES mở; sau: ES bị chặn, frontend vẫn tới được | Trước: control OK, ES OPEN. Sau: control OK, ES BLOCKED (3/3 lần lặp). Fluent Bit → ES và Gaia → ES (`_search` 200) vẫn chạy | `verify-policies-*.txt` | PASS |
| Không có hành động ngoài profile nền | heal history, log Hephaestus/Gaia | Không heal tự phát | `GET /heal/history` = `{"total":0}`; Hephaestus không ghi hành động; Gaia không phát alert | `verify-agents-1.txt` | PASS |

Lần chạy tổng cuối `verify-local-lab.sh --check all` lúc 14:02: 22 PASS, 1 FAIL (target frontend down). Exit 1 được giữ nguyên; probe không bị chỉnh để thành PASS.

## 3. File đã sửa hoặc thêm (đều trong allowlist)

Các file `.sh` và `tests/shell/run.sh` là untracked từ migration, nên `git diff` không thể hiện thay đổi; cần review cả file. Ba file tracked có `git diff --stat`: 53 dòng thêm, 14 dòng bớt.

| File | Thay đổi | Lý do |
| --- | --- | --- |
| `infrastructure/scripts/lib/common.sh` | `zd_docker_guard` (`:63`): context phải là `desktop-linux` hoặc `ZD_DOCKER_CONTEXT`, từ chối `DOCKER_HOST`; gọi ở preflight và ensure-cluster. `zd_helm` (`:47`): Helm home trong `scratch/helm`. `zd_chart_version` (`:55`). `zd_verify_image` (`:84`): so image ID pod với `.Id` hoặc config digest từ `docker save`. `k3d cluster create … --kubeconfig-switch-context=false` (`:137`) | A-F4, A-F1, A-F6; CR-03 (image identity) |
| `infrastructure/scripts/setup-phase1.sh` | Bỏ `helm repo add/update`; cài bằng `--repo`/OCI với version pin; resolve version trước preflight; `--component ingress` dừng khi chưa pin; `all` bỏ qua ingress kèm cảnh báo (`:18-56`) | A-F6; tránh `recreate-cluster.sh` xóa cluster rồi mới lỗi |
| `infrastructure/scripts/setup-phase3.sh`, `setup-phase4.sh`, `rebuild-nemesis.sh` | Thêm `zd_verify_image` sau rollout | Không coi build tag mutable là pod đã dùng image mới |
| `infrastructure/scripts/setup-local-apps.sh` (mới, 41 dòng) | Target: CRD check, 4 manifest, rollout 9 Deployment. Gaia: build, import, apply, restart, rollout, verify image | A-F3 |
| `infrastructure/scripts/verify-local-lab.sh` (mới, 162 dòng) | Probe purchase, telemetry, logs, kafka, agents, policies | Kiểm tích hợp không chaos |
| `infrastructure/helm-values/chart-versions.yaml` (mới) | kube-prometheus-stack 92.10.1; kafka 29.3.2; ingress-nginx để trống | Nguồn version duy nhất |
| `infrastructure/helm-values/kafka-values.yaml` | `controller.heapOpts: -Xmx384m -Xms384m` (`:27`); resource tường minh cho provisioning (`:56`) và JMX; tắt ServiceMonitor của chart (`:115`) và thay bằng `extraDeploy` ServiceMonitor `/metrics` (`:117`) | CR-02; JMX target down (mục 6) |
| `infrastructure/helm-values/prometheus-values.yaml` | Bỏ mirror `dyrnq/kube-state-metrics:v2.19.1`, dùng image upstream mặc định của subchart (`:83`) | Không dùng mirror không rõ nguồn; registry.k8s.io truy cập được |
| `infrastructure/manifests/chaos-worker.yaml` | Bỏ exec livenessProbe (`:112`) | Image distroless không có `sh`, probe lỗi mỗi 30s và không bao giờ phát hiện gì |
| `tests/shell/run.sh` | Thêm 5 nhóm test (Docker guard, pin chart và Helm home, thiếu pin, apps không Ingress/HPA, image ID cũ hoặc config digest); cập nhật nhóm `all` | Regression cho thay đổi trên |
| `docs/runbooks/bash-tooling.md` | Entry point mới, version/Helm home, thứ tự dựng đã kiểm, cảnh báo build, profile nền | Người khác dựng lại không cần hỏi |
| `docs/evidence/ZER-35/ingress-preflight.md` (mới), file này | Evidence | — |

Không sửa: logic agent Python/Go, runner, quota, namespace, `k3d-config.yaml`, WSL, Secret và `recreate-cluster.sh` (ngoài allowlist; xem mục 9).

## 4. Version, digest và topology

**Chart** (đã pull vào `scratch/zer35/charts`, render bằng values của repo, `--kube-version 1.31.5`):

| Chart | Version | Digest | Release |
| --- | --- | --- | --- |
| kube-prometheus-stack | 92.10.1 (app v0.94.1, kubeVersion `>=1.25.0-0`) | tgz sha256 `0d16c44e941372400ee8bcdc232ebee957eefcc910f8833767d8b94145f20094` | `prometheus`/`monitoring`, rev 1 |
| kafka (bitnami OCI) | 29.3.2 | OCI `sha256:68ebd3eb944c1540009ea91460ee7814e7054863cdf35a88259d9c8e725617c0`; tgz `8d32f6b9f3e207ace675ab80453ac49c303fbacfa5dcc385fa27d38bdb36a57e` | `kafka`/`zero-door`, rev 2 |
| ingress-nginx (chưa cài) | ứng viên 4.15.1 | tgz `3eff0bd18151d6e6b1c441463410571443dda1ac78292cb189346628de784f0c` | — |

Render kube-prometheus-stack gồm:
- 10 CRD, 5 ClusterRole/Binding, MutatingWebhook và ValidatingWebhook;
- 2 hook Job admission (`before-hook-creation,hook-succeeded`, tự dọn sau khi thành công).

Trước khi cài không có CRD `monitoring.coreos.com` hay ClusterRole trùng tên. Render Kafka gồm StatefulSet, hook Job provisioning (`post-install,post-upgrade`, cùng delete policy), NetworkPolicy của chart (mở cổng client, không chặn agent) và 2 PDB.

**Image đang chạy** (imageID do CRI báo lúc 14:05):

| Image | ID |
| --- | --- |
| `docker.elastic.co/elasticsearch/elasticsearch:8.13.0` | `sha256:fcf6b29cb00f1db56921e6cb47b506e6a207fcaeae777765dfa733dc007513a6` |
| `docker.io/fluent/fluent-bit:3.0` | `sha256:121fd619dd74825408006dd894cf9e20952069ad68956a95bfb9debc35959352` |
| `docker.io/grafana/grafana:13.2.4-distroless` | `sha256:ae3d3add290adbe6a88412229f5d76fd7bb82743050881698642d3d62f277e35` |
| `quay.io/kiwigrid/k8s-sidecar:2.14.1` | `sha256:092dbe0c335fba9af414a27630ca68f34df6185784fa847d9954187e69dbfdd7` |
| `quay.io/prometheus-operator/prometheus-config-reloader:v0.94.1` | `sha256:06b52bd4dbe3ed6dd5905aadaf8b9987d9da4c31d37bb86deaadae68cee2d26b` |
| `quay.io/prometheus-operator/prometheus-operator:v0.94.1` | `sha256:7c88d4e7bae63bd8d0f8da986054337c23b4472fa8d3c6817f5bc4b8407a2d6a` |
| `quay.io/prometheus/node-exporter:v1.12.1-distroless` | `sha256:8c9bac11973b94b59be88d6e11fee4429aa743c8846cdc75d65b18db33f6a106` |
| `quay.io/prometheus/prometheus:v3.15.0-distroless` | `sha256:b2a413d5a03ea6a76782a508d1c7947440bba3b973931a25676e278431891b01` |
| `registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.20.0` | `sha256:42cfe3723a5f058171c627537fb57a3ea0f26e4380fa18555a95cb1a1b4cfc5b` |
| `docker.io/library/redis:alpine` (tag mutable, có sẵn trong manifest) | `sha256:3811787313eba226a2ef38658c6ccb91cd5e110edc89c37767de373120a0e5a0` |
| `…/microservices-demo/cartservice:v0.10.5` | `sha256:85c4fee0ddb6eada076003abcbff17ac3daf8e18dde68c7bde03b15fc8e17417` |
| `…/checkoutservice:v0.10.5` | `sha256:403f4056479bcf2d36a865bf037ba2de0f84a60408519cee1b80e705e99f622a` |
| `…/currencyservice:v0.10.5` | `sha256:1ced46aa236c5093a3cc6642f67edf50e0deccdc07262871ffacf6173fc8c6fa` |
| `…/emailservice:v0.10.5` | `sha256:c6de94237cad0708ec674085a54a52d9856be37d9bf2d6ec2ddfe7b725d02bb2` |
| `…/frontend:v0.10.5` | `sha256:50ca57c513de1ef22a97b6ef76989a73878d4a3873f85b5314bfc207853d5475` |
| `…/paymentservice:v0.10.5` | `sha256:d9bc5e83c671660ce825420fea552b0ab067f441e6387607091fa35b15dc1e1f` |
| `…/productcatalogservice:v0.10.5` | `sha256:6e0d2218e0edecf671230d54cbbb565209d3a7592215d9167aca918dcb251e14` |
| `…/shippingservice:v0.10.5` | `sha256:0d2be86f0280a0a5594de9593eecd47ca2380e90946a3434b30d956373599b44` |
| `docker.io/bitnamilegacy/jmx-exporter:1.0.1-debian-12-r2` | `sha256:ad9104f2c52a41380493c55c268766e4c079ad3099973d4ccda4fbd17d6fccd1` |
| `docker.io/bitnamilegacy/kafka:3.8.0-debian-12-r7` | `sha256:6037ad00c9d7c786875d23008dde4f75bb1835b0c4eb3439358d7ea97ce85a6f` |
| `chaos-worker:latest` (build local) | config `sha256:e9048f9fd238b88a7fa9cc043692b931b60e2972f58004652f7cad757d69c599` |
| `hephaestus:latest` (build local) | config `sha256:61dd9756affc0b19dc65d3a7284870f94145f98ce1a8b6b65d26467023397843` |
| `nemesis:latest` (build local) | config `sha256:9f6f8ff949ba1cfcd951282f38706b47d4fa572fb7c4a0d713a8974bde6b49fe` |
| `zero-door/gaia:latest` (build local) | config `sha256:cac32c0796fea071563aab53d45ca5b7df1c1e0b6cab02c50f758ee177fc0f99` |

Image local build từ working tree dirty, nên ID trên không gắn với một commit. Khi build lại phase3, index digest đổi nhưng config digest giữ nguyên. Chart Kafka in cảnh báo về image `bitnamilegacy` thay thế; đây là lựa chọn có trước trong values và chưa được đổi.

**Topology profile nền (đã khóa trong gói này):**
- Online Boutique 9 dịch vụ (currency, productcatalog, checkout, cart, redis-cart, frontend, shipping, email, payment), mỗi dịch vụ 1 replica.
- Monitoring không bật Alertmanager; ES single-node; Fluent Bit DaemonSet ×2; Kafka KRaft 1 pod; 4 agent/worker; 3 NetworkPolicy của repo.

**Deferred:**
- HPA (quyết định thí nghiệm sau);
- loadgenerator;
- recommendation/ad: không có trong repo addons. Frontend chỉ ghi warning và luồng mua hàng vẫn hoàn tất, nên không thêm;
- Ingress (mục 8);
- LLM credential: Secret Nemesis là template rỗng, không gọi LLM.

## 5. Tài nguyên: admission, usage, đỉnh

### 5.1 Quota đã dùng (LIVE, 14:03; không phải RAM)

| Namespace | requests CPU / RAM | limits CPU / RAM | Quota | Đỉnh quan sát |
| --- | --- | --- | --- | --- |
| target-app | 410m / 712Mi | 1425m / 1920Mi | 1500m / 2Gi · 3 / 4Gi | Không có HPA nên không tăng |
| zero-door | 425m / 768Mi | 1900m / 2Gi | 1 / 1Gi · 3 / 3Gi | 896Mi request khi Job provisioning chạy lại; 960Mi khi phase3 tạo hai surge đồng thời. Không bị từ chối |
| monitoring | 1500m / 2304Mi | 7400m / 6656Mi | 4 / 6Gi · 10 / 10Gi | — |

Render cho thấy Prometheus operator, kube-state-metrics, node-exporter và sidecar Grafana không khai báo resource, nên LimitRange `monitoring` gán mặc định. Số used ở trên đã gồm phần này.

### 5.2 Usage theo mốc (LIVE)

| Mốc | Giờ | WSL MemAvailable | PSI mem avg60 | PSI CPU avg60 | `docker stats` k3d | Host MemFree |
| --- | --- | --- | --- | --- | --- | --- |
| 00 baseline | 13:26 | 5,58 GiB | 0,00 | 0,18 | 544 MiB | 3,31 GiB |
| 01 monitoring | 13:28 | 4,52 | 0,06 | 7,64 | 1908 | **0,49** |
| 02 Boutique | 13:32 | 4,27 | 0,00 | 1,85 | 2455 | **0,47** |
| 03 logging | 13:36 | 3,63 | 0,10 | 3,59 | 3622 | **0,45** |
| 04 Kafka | 13:41 | 3,18 | 0,02 | 5,35 | 4433 | **0,75** |
| 05 Gaia (sau build) | 13:45 | 3,09 | 0,23 | 4,01 (avg300 9,34) | 4511 | **0,62** |
| 06 phase3 (sau build) | 13:48 | 2,94 | **2,40** | 6,95 | 4408 | **0,45** |
| 07 đủ agent | 13:54 | 2,73 | 0,64 | 4,05 | 4469 | 1,10 |
| 08 cuối, nghỉ | 14:03 | 2,42 | 0,11 | 8,40 | 4726 | 1,96 |

Usage container lúc 14:03 (`kubectl top --containers`):

| Nhóm | RAM | Ghi chú |
| --- | --- | --- |
| monitoring | 1628 Mi | ES 691Mi/1Gi limit; Grafana 331Mi; Prometheus 320Mi |
| zero-door | 1052 Mi | Kafka 593Mi/768Mi (77% limit); JMX exporter 222Mi/256Mi (87% limit); nemesis 86, hephaestus 83, gaia 55 |
| target-app | 264 Mi | cartservice lớn nhất, 75Mi |
| kube-system | 86 Mi | — |

Tổng khoảng 3,0 GiB workload; container k3d khoảng 4,6 GiB. Con số này nằm trong ước lượng 3,2–4,9 GiB của báo cáo sizing, ở nửa trên.

Heap Kafka đã xác minh trong process: `-Xmx384m -Xms384m`, RSS khoảng 321 MiB lúc mới chạy.

### 5.3 Guard và vi phạm

- Guard trong WSL **giữ suốt phiên**: MemAvailable thấp nhất 2,42 GiB (> 1 GiB); PSI memory avg60 cao nhất 2,40 (< 10); không OOMKilled; không quota rejection; không Helm/rollout timeout.
- **Guard phía host bị vượt và không được phát hiện kịp.** MemFree của Windows (đọc qua `/proc/meminfo` của Git Bash) dưới 1 GiB từ bước monitoring tới phase3. Pagefile đã dùng tăng từ khoảng 1,28 GiB (kiểm kê sáng 18/10) lên 2,62 GiB (14:05). Tiêu chí dừng "host trống < 1 GiB **và** Windows đẩy trang ra đĩa" vì vậy đã thỏa ít nhất trong một phần thời gian dựng. Bộ đo khi đó chưa ghi pagefile nên tôi không dừng. Đã sửa bộ đo trong scratch để ghi `SwapTotal`/`SwapFree`; cần đưa vào protocol đo.
  - Working set lúc 14:05: vmmemWSL 4,73 GiB; Chrome 2,22; claude 1,18; ChatGPT 0,99; codex 0,22.
  - Kết luận: **stack nền vừa trong WSL 7 GB, nhưng máy chỉ thoải mái khi đóng bớt ứng dụng desktop**, đúng như chế độ "thí nghiệm đầy đủ" ở báo cáo sizing B.4. Chưa đo trong lúc có tải tấn công.
- Build image khi Boutique đang chạy đẩy CPU PSI avg300 lên 9,34. emailservice trượt probe gRPC (timeout 1s) liên tiếp và bị kubelet restart lúc 13:43 (exit 137, không phải OOM). Đây là tác động thật, đã ghi vào runbook: build trước hoặc ngoài lúc đo.

## 6. Lệnh, exit và lỗi (đầy đủ ở `scratch/zer35/raw/`)

| Giờ | Lệnh | Exit | Ghi chú |
| --- | --- | --- | --- |
| 13:16 | Preflight Git/context/inventory | 0 | Baseline như mục 1 |
| 13:17–13:19 | Pull và render 3 chart (Helm home trong `scratch/zer35/helm`) | 0 | Lần render đầu có `--include-crds` làm PyYAML lỗi tag `=`; đã viết loader riêng |
| 13:2x | `bash tests/shell/run.sh` | 1 → 0 | Lần 1 FAIL: `recreate-cluster.sh` gọi `all`, mà `all` lỗi vì ingress chưa pin **sau khi** đã xóa cluster. Sửa `all` bỏ qua ingress kèm cảnh báo; 26/26 PASS |
| 13:26:49 | `setup-phase1.sh --component monitoring` | 0 | 95s; 15/15 target up |
| 13:28:44 | `setup-local-apps.sh --component target` | 0 | 55s; 9 rollout |
| 13:31 | `verify --check purchase` | 23 → 1 → 0 | (1) Native curl nhận `/dev/null` và cookie path dạng MSYS vì `MSYS_NO_PATHCONV=1`; sửa bằng `zd_path`. (2) Checkout 422 `Field 'CcNumber' is invalid`: frontend v0.10.5 chỉ nhận số thẻ demo không có dấu gạch; sửa dữ liệu demo |
| 13:32:16 | `setup-phase1.sh --component logging` | 0 | 130s. Fluent Bit mất vài chunk trong lúc ES khởi động (`cannot be retried`, Retry_Limit 3) |
| 13:34 | `verify --check logs` | 1 → 0 | Service proxy của API server trả `BadRequest` cho mọi URL ES có query string (nguyên nhân chưa rõ, UNKNOWN); ES qua tunnel loopback vẫn 200. Probe chuyển sang tunnel; field đúng là `message` |
| 13:36:50 | `setup-phase1.sh --component kafka` | 0 | 134s, revision 1 |
| 13:39 | `verify --check kafka` | 1 → 1 → 0 | CLI trong container broker kế thừa `JMX_PORT` (bind 5555 lỗi) và heap 384m; chạy với `env -u JMX_PORT`, `KAFKA_HEAP_OPTS=-Xmx128m`, stdin tách riêng. Broker 0 restart |
| 13:41:50 | `setup-local-apps.sh --component gaia` | 1 | Rollout OK nhưng image check báo lệch: Docker containerd store trả index digest, CRI trả config digest. Sửa `zd_verify_image`; kiểm lại PASS |
| 13:45:30 | `setup-phase3.sh` | 0 | 157s; Secret Nemesis template rỗng được tạo vì chưa có |
| 13:48:27 | `setup-phase4.sh` | 0 | 102s; RBAC đúng kỳ vọng |
| 13:51–13:52 | `verify --check policies --expect-open`, `setup-phase1.sh --component policies`, `verify --check policies` | 0 | Trước/sau đúng kỳ vọng |
| 13:53 | `verify --check telemetry` | 1 | `kafka-jmx-metrics` down: ServiceMonitor của chart dùng path `/` (HTML) và Prometheus 3 từ chối `text/html`; `/metrics` trả `text/plain`. Sửa qua `extraDeploy` |
| 13:55:03 | `setup-phase1.sh --component kafka` (upgrade) | 0 | 33s, revision 2; JMX up; workload Kafka không đổi, không restart |
| 13:56 | Apply `chaos-worker.yaml` (bỏ probe lỗi) | 0 | Rollout mới, image khớp |
| 13:58–13:59 | Chạy lại namespaces/target/phase3 | 0 | Mục 2 |
| 13:59:32 | `verify --check all` | 1 | Probe policy mất dòng control vì attach race của `kubectl run -i` khi pod chạy trên node khác; sửa bằng chờ trước rồi in một dòng kết quả; 3/3 lần lặp PASS |
| 14:02:07 | `verify --check all` | 1 | 22 PASS, 1 FAIL (frontend target, mục 8) |
| 14:06 | `bash -n`, YAML parse, CR/whitespace, `tests/shell/run.sh`, `--help` | 0 | 26/26 PASS (MOCK) |

Một lần Nemesis readiness/liveness timeout (1s) lúc khoảng 13:54, khi Job provisioning chạy; 0 restart. Ghi nhận, không sửa.

## 7. Bảo toàn dữ liệu và ownership

- Không xóa hoặc gỡ: không `delete -f`, không uninstall/rollback Helm, không `--atomic`. Không xóa namespace, PVC/PV, Secret, CRD, image, volume hay cache dùng chung.
- Tài nguyên mới thuộc lượt này:
  - release `prometheus` và `kafka`;
  - các object của `target-app*.yaml`, `elasticsearch.yaml`, `fluent-bit.yaml`, `network-policies.yaml` và manifest agent;
  - PVC `prometheus-…-db-…-0` (2Gi), `elasticsearch-data` (5Gi), `data-kafka-controller-0` (2Gi);
  - Secret `nemesis-secrets` (template rỗng);
  - topic `zd.verify.restore`.
- Đối tượng tạm duy nhất bị xóa: pod `zd-np-probe-*` qua `kubectl run --rm`, do chính probe tạo. Job hook tự dọn theo `hook-delete-policy` của chart sau khi đã inventory.
- Helm repo/cache của user không bị sửa: dùng `scratch/zer35/helm` cho phân tích và `scratch/helm` cho script.
- Không in Secret. Grafana values vẫn có mật khẩu admin dạng plaintext (có trước, không chép ra đây).

## 8. Quyết định cần Hoàng/Codex

1. **Ingress (một câu hỏi duy nhất):** A, pin ingress-nginx 4.15.1 legacy với image upstream và bật metrics, chỉ dùng local; hay B, Traefik qua một issue riêng? Chi tiết ở [ingress-preflight](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/ingress-preflight.md). Gaia/Nemesis đang query metric `nginx_ingress_controller_*`, nên quyết định này ảnh hưởng tín hiệu DDoS. Lưu ý thêm: Service `frontend-external` kiểu LoadBalancer (servicelb của K3s) có thể đã chiếm cổng 80 của LB K3d; cần kiểm khi cài controller. Chưa kiểm.
   *Cập nhật 14:40: Hoàng chọn B. Đã kiểm (chỉ đọc): `frontend-external` giữ hostPort 80 trên cả hai node, và `127.0.0.1:8080` hiện đi thẳng vào frontend. Phạm vi, patch và kế hoạch nằm ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md).*
2. **ServiceMonitor `frontend-monitor`:** frontend v0.10.5 không có `/metrics`, nên target luôn down. Chọn giữa: bỏ ServiceMonitor; hoặc giữ chờ metric từ Ingress. Tôi chưa tự gỡ.
3. **Biên RAM của JMX exporter** (87% limit) và Kafka (77%): chưa có OOM sau khoảng 30 phút. Đề xuất theo dõi trong pilot trước khi đổi limit, vì tăng limit làm giảm headroom quota khi có surge.
4. **Protocol đo host:** thêm pagefile vào tiêu chí; quyết định có đóng ứng dụng desktop trong lúc thí nghiệm hay không.

## 9. Điều kiện còn thiếu trước Done

- Codex review mã mới, cả file `.sh` untracked; merge; Hoàng chấp nhận. Linear do Hoàng hoặc Codex cập nhật.
- Ingress theo quyết định mục 8.1, rồi kiểm đường `127.0.0.1:8080` và metric ingress.
- Quyết định mục 8.2–8.4.
- `recreate-cluster.sh` (ngoài allowlist) gọi `docker info` và `k3d cluster delete` **trước** khi chạy guard Docker context. Đề xuất: thêm `zd_docker_guard` trước lệnh xóa trong lượt có quyền sửa file đó.
- Chưa wipe cluster để chứng minh dựng từ đầu (theo handoff: không wipe). `k3d cluster create` mới chỉ được kiểm bằng MOCK.
- Chưa kiểm `setup-phase5.sh`/`requirements-experiments.txt` (A-F2) vì đường verify không dùng.

## 10. Trạng thái repo cuối phiên (14:08)

- HEAD vẫn `1f43ff1461c2199bc99e9962483956c3df0fa975`; staged rỗng.
- So với 13:16, `git status` thêm:
  - ` M` `infrastructure/helm-values/kafka-values.yaml`, `prometheus-values.yaml`, `infrastructure/manifests/chaos-worker.yaml`;
  - `??` `docs/evidence/ZER-35/ingress-preflight.md`, `lab-restoration.md`, `infrastructure/helm-values/chart-versions.yaml`, `infrastructure/scripts/setup-local-apps.sh`, `verify-local-lab.sh`.
- Hash đổi trong nhóm file dirty có trước: chỉ `common.sh`, `setup-phase1/3/4.sh`, `rebuild-nemesis.sh`, `tests/shell/run.sh`, `bash-tooling.md`, cùng `local-lab.md` và `NOW.md` (con trỏ bàn giao). Mọi file dirty khác giữ nguyên hash.
- `git diff --check` exit 0 (cảnh báo CRLF `.gitignore` có từ trước). File mới: 0 CR, không có khoảng trắng cuối dòng.
- Không commit, push, merge hay cập nhật Linear.

## 11. Codex nhận lượt sửa cuối theo yêu cầu Hoàng — 18/10/2026

Hoàng yêu cầu Codex sửa trực tiếp các điểm còn mở, thay Claude làm bên ghi duy nhất. Baseline HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975, staged rỗng, 79 đường dẫn dirty/untracked; hash trước sửa ở scratch/zer35-final/hash-start.json. Scope mã/test: `infrastructure/scripts/lib/common.sh`, `infrastructure/scripts/setup-phase1.sh`, `infrastructure/scripts/setup-local-apps.sh`, `infrastructure/scripts/verify-local-lab.sh`, `infrastructure/scripts/recreate-cluster.sh`, `infrastructure/scripts/deploy.sh`, `infrastructure/helm-values/kafka-values.yaml`, `infrastructure/manifests/target-app-addons.yaml`, `infrastructure/manifests/target-app-monitor.yaml`, `infrastructure/helm-postrenderers/kafka-jmx/plugin.yaml`, `infrastructure/helm-postrenderers/kafka-jmx/render.py`, `tests/shell/run.sh`, `tests/shell/test-local-restore.sh`. Tài liệu chỉ cập nhật runbook, evidence hiện có và NOW/local-lab. Không sửa source agent/worker, Secret/PVC/quota/K3d/WSL.

Thao tác: render/chart/test offline; upgrade riêng Kafka có bảo toàn PVC và kiểm quota hook; apply riêng ba Deployment currency/email/payment được chỉnh từ manifest; thu hồi đúng ServiceMonitor target-app/frontend-monitor đã xác minh tạo hai target 404; kiểm lại probe tích hợp hữu hạn và theo dõi restart/tài nguyên. Không delete -f, recreate, uninstall hay tự rollback; không chaos/LLM/cloud, commit/push/merge hoặc Linear write. Guard giữ Windows available >=1GiB, WSL MemAvailable >=1GiB, PSI memory avg60 <=2 trước rollout. Recreate-cluster chỉ sửa guard và kiểm mock, không chạy nhánh xóa thật. Đây là kế hoạch phạm vi, chưa phải kết quả.

Bổ sung phạm vi trước sửa OBS-01: currencyservice nằm trong infrastructure/manifests/target-app.yaml (không phải addons); chỉ chỉnh Deployment currencyservice trong file đó, giữ các document khác.

Bổ sung scope tài liệu: cập nhật đúng dòng tham chiếu ServiceMonitor bị loại bỏ ở phase2_runbook.md và runbook legacy 2026-10-09; không viết lại mốc/bằng chứng lịch sử.

Bổ sung scope sau lỗi thật ở observation: Nemesis restart sau Kafka upgrade; consume_results_loop dùng KafkaConsumer đồng bộ trên event loop. Sửa tối thiểu agent-orchestrator/nemesis/main.py (chỉ vòng đọc kết quả và lifecycle worker), thêm tests/test_nemesis_consumer.py; build/import/rollout riêng Nemesis sau test và resource guard. Không đổi attack generation/routes, LLM, schema Kafka hoặc healing. Snapshot observation thất bại được giữ nguyên.

Bổ sung scope CI: .github/workflows/ci.yml cần cài PyYAML cho mock Helm renderer và chạy 3 test consumer offline mới; chỉ sửa workflow, không dispatch/push hoặc chạy CI cloud.

## 12. Gói sửa cuối do Codex thực hiện — 18/10/2026

### Quyền, baseline và vai trò

Hoàng yêu cầu trực tiếp Codex sửa để hoàn tất lượt cuối ZER-35. Codex nhận quyền ghi từ Claude; không tự nhắn sang phiên khác. HEAD vẫn 1f43ff1461c2199bc99e9962483956c3df0fa975, staged rỗng; giữ baseline dirty có trước. Scope/diễn biến bổ sung đã ghi ở mục 11; ledger và raw ở scratch/zer35-final. Mục 1–10 giữ mốc lịch sử, không là state hiện hành. Đây là kết quả người thực hiện tự kiểm và rà mã; chưa thay review độc lập của một bên khác.

### Sửa gì và kiểm đúng vấn đề nào

| Mục | Thay đổi cuối | Bằng chứng |
| --- | --- | --- |
| LAB-01: JMX OOM | Chart Kafka 29.3.2 hard-code MaxRAMPercentage=100, không có values override argv JMX. Thêm renderer giới hạn Xms32m/Xmx128m trong limit 256Mi; setup-phase1 bắt buộc dùng renderer. Helm 4 dùng plugin postrenderer/v1 trong Helm home của checkout; Helm 3 dùng executable/args. Renderer kiểm namespace/name/command/limit và từ chối layout khác, không sửa container khác | Helm render thật chỉ khác args JMX về ngữ nghĩa; các trường hợp thiếu container, đã patch hoặc memory budget khác đều bị từ chối. Kafka upgrade revision 3 thành công lúc 18:26; log JVM in Min Heap 32M, Max Heap 128M. Không tăng limit/quota/WSL |
| LAB-02: frontend scrape 404 | Bỏ manifest/caller scrape frontend không có /metrics; setup-local-apps thu hồi riêng target-app/frontend-monitor. HTTP metrics từ Traefik, CPU từ cAdvisor. Bỏ ngoại lệ exit 3 trong verify | Thu hồi đúng 1 ServiceMonitor, không delete -f. Sau sửa 17 target up, CPU có 9 container; mock chứng minh frontend 404 cũng phải exit 1, không bị che. All kiểm thực cuối exit 0 |
| OBS-01: app probe timeout | Log kubelet ghi payment/email bị restart do liveness; trạng thái Error/137, không OOMKilled. Tại 18:01 payment/currency bị throttle ~70% chu kỳ; tại 18:11 node CPU waiting ~22–28%, nhiều probe timeout. Không thấy event Kernel-Power/Power-Troubleshooter trong 4 giờ truy vấn; chưa coi đó là bằng chứng loại trừ mọi nguyên nhân host. Tăng CPU burst currency/email/payment thành 400m/300m/300m, giữ requests/RAM; startup budget 120s, timeout gRPC 3s | Target requests vẫn 410m/712Mi; limits 2025m/1920Mi. Kiểm steady + từng surge tuần tự đều dưới quota hiện hữu; dry-run server đạt; rollout từng Deployment 18:25 thành công. Không gọi kết quả này là cải thiện MTTD/MTTR |
| LAB-03: Nemesis event loop | Lần quan sát đầu bắt được Nemesis restart sau Kafka upgrade. consume_results_loop gọi KafkaConsumer đồng bộ trên FastAPI event loop. Chuyển construct/poll/close sang cùng một worker thread, có stop signal/drain khi hủy; retry connect/poll vẫn log lỗi. Giữ topic/group/schema, format log và toàn bộ attack/LLM/heal logic | Test mới chạy trên mã trước sửa FAIL (event loop stall ~0,59–0,61s, lỗi connect không hồi phục); bản sửa 3/3 PASS cho slow poll, connect retry, poll retry và cleanup/owner thread. Build có cache/import/rollout riêng Nemesis 18:34 đạt, không nới timeout probe Nemesis. SHA source trong pod 2e087b3c0ce4bae4700a2e8fd9d31ba989c66fda700281b6f9c5bb462577443e khớp source |
| Guard recreate | Thêm zd_docker_guard trước docker info/k3d delete | Mock sai Docker context và DOCKER_HOST đều dừng trước nhánh xóa; chưa chạy recreate thật |
| CI và hướng dẫn | Bash CI cài PyYAML rõ ràng, chạy 3 test consumer mới; cập nhật runbook và bỏ tham chiếu manifest bị loại | YAML/syntax kiểm local; chưa dispatch/push hoặc coi CI cloud đã chạy |

Helm 4 đổi post-renderer từ executable path sang tên plugin; đã đối chiếu [tài liệu chính thức](https://helm.sh/docs/plugins/migrate/). Plugin local không được cài vào cấu hình toàn máy. Cloud deploy legacy chưa tích hợp/kiểm renderer này; chỉ bỏ caller manifest frontend lỗi. Không nhận đường cloud đã sẵn sàng.

### Kiểm chứng cuối sau mọi rollout

- 34 nhóm Bash mock PASS, gồm renderer Helm 3/4, context/delete guard, cleanup tunnel và down-target failure; lượt cuối chạy với MSYS_NO_PATHCONV=1/MSYS2_ARG_CONV_EXCL=*. Trước đó môi trường sạch cũng đạt 34 nhóm.
- Real render + PromQL regression exit 0: chart SHA, label honorLabels, rewrite/rollback render, 5 nhóm promtool, JMX postrenderer và quota rollout. Cluster ID cố định chỉ trong test để so manifest có giá trị ngẫu nhiên; không đặt lại cluster ID lab.
- 3 test consumer offline PASS; unit không import/chạy API/LLM hoặc gửi message thật. Test hồi quy đã phân biệt mã trước/sau sửa. CI được nối test nhưng chưa có kết quả CI remote.
- verify-final.out chạy lúc 18:36:07–18:37:51, sau rollout Nemesis cuối: exit 0, 0 failure. Có checkout mẫu; Kafka correlation trên zd.verify.restore và đủ 5 topic; log sentinel trong ES; health ba agent; NetworkPolicy có control; ingress rewrite/log/IP/metric/consumer đều đạt. Không attack/heal/reset/LLM, không benchmark/dataset chính thức.
- Probe ban đầu lúc 18:27 ghi một lần Nemesis ServiceUnavailable trước khi tự hồi; không bỏ raw đó. Verify-all lúc 18:29 exit 0 vẫn chưa được chấp nhận ngay: observation bắt restart Nemesis nên đã sửa LAB-03, rồi chạy kiểm cuối lại.
- Nemesis mới: 12 GET healthz cách nhau 173ms, tất cả 200; max quan sát 4,9ms. Đây là kiểm HTTP hữu hạn, không phải latency benchmark hoặc chứng minh mọi lỗi Kafka đều đã được xử lý.

### Dữ liệu và tài nguyên

Ba PVC giữ nguyên namespace/name/UID/volume và Bound: Elasticsearch 77dd28b6-44e0-402f-aca3-0f2c8dee3b79; Prometheus ae141e1f-312f-40c3-9efd-6a69801e4848; Kafka 26544729-8428-47ee-a197-7448e1f3ac78. Không xóa/format/recreate volume. UID nemesis-secrets và kafka-kraft-cluster-id giữ nguyên; chỉ thêm sh.helm.release.v1.kafka.v3 cho revision mới. Không in/copy credential. Quota specs/namespace/WSL/K3d giữ nguyên. Kafka topic probe đã có tiếp tục round-trip sau upgrade.

Quan sát sau bản cuối: **18:36:31–18:51:48 +07:00, 31 mẫu trong 15 phút 17 giây**. Tất cả container Ready ở mọi mẫu; 17/17 target up; không restart hoặc thay pod ngoài dự kiến, không event Warning mới trong cửa sổ. Đã so UID và restartCount cuối với toàn bộ pod baseline còn hoạt động, không chỉ kiểm pod có tên trùng. JMX RAM cao nhất 141Mi trong limit 256Mi, không OOM trong cửa sổ này.

Guard xuyên các bước rollout/build và quan sát: Windows available thấp nhất 1844MiB; WSL MemAvailable thấp nhất 2334MiB; memory PSI avg60 cao nhất 0,40. Giữ nguyên ngưỡng và WSL/quota. Đây là cửa sổ quan sát hữu hạn sau sửa heap, không là soak dài hạn hoặc bằng chứng uptime 99,9%; pilot chính thức vẫn cần theo dõi trong protocol nghiên cứu. Cuối phiên Hephaestus heal/history vẫn total=0.

### Giới hạn và đường nghiệm thu

- GitNexus refresh --index-only được thử một lần có timeout 45s, exit 124, chỉ in banner; không lặp và không nhận index đã cập nhật. Index cũ chỉ hỗ trợ tìm caller; impact cũ cho consume_results_loop có startup_event, đã đối chiếu source trực tiếp. Không nhận graph/PDG coverage đầy đủ cho working tree mới.
- Không wipe cluster để chứng minh bootstrap trống. Có bằng chứng dựng tiếp/rerun trên lab đã inventory; không tự tăng scope thành recreate có mất dữ liệu.
- Health/metric không chứng minh AI/LLM đã hoạt động, BLOCK_IP, vector SQLi/DDoS/resource hay KPI nghiên cứu. Chưa tạo 5xx runtime; phép tính nhánh đó chỉ có test synthetic. Purchase dùng loopback, ingress kiểm riêng; chưa khẳng định checkout xuyên ingress.
- Probe/resource mới là baseline phải giữ đồng nhất cho các cấu hình đối chứng và warm-up trước đo; không trộn dataset cũ, không thay thuyết minh/KPI.
- Hai patch Traefik cũ vẫn là artifact lịch sử của gói trước sửa; hash đó không mô tả toàn bộ source hiện tại (Nemesis/helper/test đã đổi thêm). Đối chiếu working tree và ledger cuối khi review.
- Còn review độc lập bản sửa cuối, Git publication/merge và Hoàng chấp nhận theo workflow trước Done. Không tự commit/push/merge hoặc sửa Linear. Việc Hoàng giao Codex sửa không biến tự kiểm thành review độc lập.

**Chốt 18:52 +07:00:** đã kiểm Python AST/YAML/CI wiring, git diff --check và hash/scope. Không thay dirty work ngoài allowlist. Raw chính: verify-final.out/exit, observation.jsonl/out, result-summary.json, nemesis-before-test.out, nemesis-after-test.out, observation-before-nemesis-fix.out, guard/PVC/quota/snapshot trong scratch/zer35-final. Các kết quả thiết yếu đã trích bền vững ở trên; không phụ thuộc reviewer có scratch. Thao tác công bố/state vẫn chưa thực hiện.

### Delta CL-01–04 sau review độc lập — Codex, 18/10/2026

Hoàng chuyển giao nhiệm vụ đã ghi ở cuối `codex-review.md`: Codex sửa gộp bốn mục trước merge, Claude review lại delta. Review PASS lúc 20:15 áp dụng cho bản trước delta; không tự kế thừa PASS cho mã vừa sửa. Đã đọc lại live ZER-35/AC qua `linear_zero_door`, đúng URL workspace zero-door; không cập nhật live fields.

Baseline: HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`, staged rỗng; 85 đường dẫn dirty/untracked khi liệt kê từng file. Con số 72 trong review Claude dùng cách liệt kê khác, không dùng chênh số đếm để kết luận mất file. Hash đầu phiên và allowlist được ghi trước sửa tại `scratch/zer35-cl-final/`. Phạm vi đúng 9 file: `setup-local-apps.sh`, hai test Bash, `tests/test_nemesis_consumer.py`, `ci.yml`, header `kafka-values.yaml`, runbook Bash, evidence này và NOW. Không sửa `nemesis/main.py`, CPU/RAM/probe, quota, WSL hoặc các thay đổi dirty ngoài scope.

| Mục | Sửa và điều kiện kiểm |
| --- | --- |
| CL-01 | Script dùng Python/PyYAML tách nguyên trạng Service/ServiceAccount khỏi Deployment. Apply dependency trước, rồi apply/chờ từng Deployment: Redis trước cart; checkout/frontend sau backend. Sau mỗi rollout, đợi pod đang terminating bị xóa trước Deployment tiếp theo; chỉ chờ, không phát lệnh xóa pod. JSON tạm trong scratch được dọn đúng thư mục phiên. Lỗi parse, topology ngoài dự kiến, rollout hoặc chờ pod làm script dừng. Mock đối chiếu toàn bộ object với YAML nguồn, kiểm thứ tự và dừng khi rollout/drain thất bại. Budget kiểm cả 4 chiều requests/limits CPU/RAM cho steady + surge của cả 9 Deployment; resource thiếu phải FAIL, không giả định LimitRange defaults. Ba surge đồng thời 3025m bị từ chối theo quota 3000m |
| CL-02 | Job helm-lint chọn Python 3.11 bằng actions/setup-python trước khi cài PyYAML pin; không cài vào Python hệ thống. Kiểm YAML và thứ tự setup → install; chưa có kết quả CI remote |
| CL-03 | Header Kafka chỉ dẫn entry point Bash có JMX renderer. Đối chiếu bytes header cũ dựng lại với hash snapshot, rồi so YAML trước/sau: giá trị values giữ nguyên; không Helm upgrade |
| CL-04 | Entry point test consumer chạy unittest trong tiến trình con, có deadline 30s; hết hạn kết thúc tiến trình rồi trả exit 1, bao phủ cả executor shutdown bị treo. Job bash-tooling có trần 10 phút. Không sửa vòng Kafka production |

Kiểm chứng offline:

- CL-01 RED: test thứ tự mới chạy trên script cũ trả exit 1: `concurrent rollout: currencyservice and productcatalogservice`. Không phải lỗi giả định từ phép cộng quota.
- `bash tests/shell/run.sh`: **exit 0, 37/37 nhóm ở cả hai chế độ** — môi trường sạch và `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL=*`.
- `bash tests/shell/test-local-restore.sh`: **exit 0, 18 PASS**, chart render thật/PromQL/JMX và đủ bốn chiều quota; steady giữ 410m/712Mi requests, 2025m/1920Mi limits. Test baseline yêu cầu một replica và resource tường minh; topology/strategy/init/overhead ngoài mô hình phải review lại, không nhận mô hình quota tổng quát.
- `python tests/test_nemesis_consumer.py`: **exit 0, 3/3 OK**, 5,403s. Chạy lại bốn mutant của Claude: cả bốn exit 1; riêng no-stop-on-cancel in `FAIL: consumer tests exceeded the 30s process deadline; worker terminated`, không chờ outer timeout 60s. Ba mutant còn lại fail assertion đúng như trước.
- Đã kiểm `bash -n`, Python AST, YAML/CI wiring và whitespace các file scope. Trong quá trình viết mock có lỗi chuyển đường dẫn POSIX cho Python native; sau đó kiểm drain phát hiện CRLF trong tên pod Windows. Cả hai đã sửa; không tính các lượt thất bại đó là PASS.

Không chạy lệnh lab, full verify, attack/heal/reset/LLM, build/import/rollout, recreate hoặc cloud. Không dùng test mock/render thay chứng minh runtime của đường tuần tự mới; runtime integration của mục 12 vẫn là mốc 18:36–18:51, chưa có lần triển khai delta này. OBS-02 giữ để theo dõi warm-up/pilot, không nới probe thêm. GitNexus context vẫn ở `6337b31`, chậm HEAD hai commit; các Bash/test mới không có coverage graph đáng tin. Không lặp refresh đã timeout; dùng source và test trực tiếp, không nhận graph hiện hành.

Raw: `scratch/zer35-cl-final/{cl01-before.out,mock-clean.out,mock-native.out,real.out,consumer.out,mutants.out}` và các file exit/hash. Kết quả thiết yếu được trích ở đây; ledger cuối tại `scratch/zer35-cl-final/final-file-ledger.json`. Bước tiếp: Claude review lại đúng 7 file mã/test/runbook và 2 file evidence/con trỏ của delta; không triển khai lại lab hoặc áp patch Traefik lịch sử. Chưa commit/push/merge hoặc thay Linear; Done vẫn cần review cuối, merge và Hoàng chấp nhận.
