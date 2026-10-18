# Công cụ vận hành bằng Bash

Từ 18/10/2026, các entry point local dùng Bash; Windows dùng Git Bash, Linux dùng Bash. Không cần quyền Administrator để chạy những entry point này. Docker, K3d, kubectl, Helm và Python phải có trong PATH theo chức năng sử dụng. `--help` chỉ in hướng dẫn, không truy cập Docker/Kubernetes hoặc cài gói.

```bash
cd /r/_Projects/Eurus_Workspace/zero_door
bash start-demo.sh --help
bash infrastructure/scripts/setup-phase1.sh --help
```

Tên phase trong tên file giữ tương thích với runbook kỹ thuật cũ; delivery vẫn dùng Linear milestone/issue/sub-issue.

## Entry point

| Bash hiện hành | Chức năng | Lưu ý |
| --- | --- | --- |
| `bash start-demo.sh` | Kiểm tra HTTP, giữ 4 port-forward cho Nemesis, Hephaestus, Prometheus, Grafana | Lab phải được triển khai trước; giữ terminal mở, Ctrl+C dừng đúng child process của script |
| `bash rebuild-nemesis.sh --no-forward` | Build không cache, import, restart và đợi Nemesis rollout | Không tạo cluster, không sửa Secret; bỏ `--no-forward` để mở tunnel Nemesis trong terminal sau rollout |
| `bash infrastructure/scripts/setup-phase1.sh` | Dựng lại hạ tầng legacy theo cấu hình repo | Mặc định `all`; ưu tiên `--component` để đo và xử lý từng nhóm |
| `bash infrastructure/scripts/setup-phase3.sh` | Build/import/deploy worker và Nemesis | Giữ Secret đã có, không chạy `go mod tidy` hoặc attack |
| `bash infrastructure/scripts/setup-phase4.sh` | Build/import/deploy Hephaestus, kiểm tra rollout/RBAC | Không gọi healer để kiểm tra sức khỏe |
| `bash infrastructure/scripts/setup-phase5.sh` | HTTP health check và port-forward trong terminal | Mặc định không attack, không cài dependency |
| `bash infrastructure/scripts/setup-local-apps.sh` | Online Boutique nền (9 dịch vụ, 1 replica, không HPA/loadgenerator) cùng PrometheusRule; build/import/restart Gaia và kiểm image ID | Cần namespaces + monitoring (CRD); Gaia cần thêm logging và Kafka. `target` apply cả Ingress frontend (class `traefik`); Ingress chỉ có hiệu lực sau `setup-phase1.sh --component ingress` |
| `bash infrastructure/scripts/verify-local-lab.sh` | Probe không gây chaos: mua hàng mẫu, Prometheus/cAdvisor/Kafka JMX, log sentinel qua Elasticsearch, Kafka round-trip, `/healthz` agent, hiệu lực NetworkPolicy, đường host `:8080` qua Traefik (route, rewrite, access log, metric, IP nguồn), query consumer của agent | Không gọi attack/heal/reset/LLM, không tạo tải (check `consumers` gửi tối đa 12 request lành). Tạo một pod busybox tạm (`--rm`) trong `target-app` cho check `policies` |
| `bash infrastructure/scripts/recreate-cluster.sh --help` | Giải thích nhánh xóa cluster rồi cài lại hạ tầng | Chỉ xóa khi có cờ xác nhận riêng; mất dữ liệu cluster, không khôi phục app/agent/dữ liệu cũ |

`infrastructure/scripts/deploy.sh` đã là Bash cho máy cloud Linux; không thuộc luồng local. Chuyển đổi này không kiểm chứng hoặc cho phép triển khai cloud.

## Cluster và khôi phục từng nhóm

Kiểm kê trước để chọn start hay tạo mới. Không recreate chỉ vì kubeconfig lỗi.

```bash
docker context show
docker ps -a
docker volume ls
k3d cluster list
```

Khi đã chốt cần khôi phục, chỉ chạy một nhóm rồi đo trước khi tiếp tục:

```bash
# Tạo nếu chưa có; start nếu đã có; không xóa cluster
bash infrastructure/scripts/setup-phase1.sh --component cluster

# Áp namespace và quota hiện có trong repo
bash infrastructure/scripts/setup-phase1.sh --component namespaces

# Các lựa chọn độc lập; không chạy cả khối nếu chưa chốt profile tài nguyên
bash infrastructure/scripts/setup-phase1.sh --component monitoring
bash infrastructure/scripts/setup-phase1.sh --component kafka
bash infrastructure/scripts/setup-phase1.sh --component ingress
bash infrastructure/scripts/setup-phase1.sh --component logging
bash infrastructure/scripts/setup-phase1.sh --component policies
```

Sau mỗi nhóm:

```bash
kubectl --context k3d-zero-door get pods -A
kubectl --context k3d-zero-door top nodes
docker stats --no-stream
```

Các namespace phải được tạo trước những nhóm phụ thuộc. Quota/requests/limits vẫn là cấu hình hiện có; chuyển Bash chưa phải tối ưu tài nguyên hoặc sửa các lỗi nghiên cứu.

### Version chart và trạng thái Helm

- Version chart lấy từ một nguồn duy nhất: `infrastructure/helm-values/chart-versions.yaml` (kube-prometheus-stack 92.10.1, Kafka 29.3.2). Script cài chart bằng `--repo`/OCI kèm `--version`, không gọi `helm repo add/update`.
- Trạng thái Helm (cache, repo, registry) nằm trong `scratch/helm/` của checkout (đã gitignore), không sửa Helm của user. Đặt `ZD_HELM_HOME` nếu muốn thư mục khác.
- Thiếu pin thì component đó dừng trước preflight, không cài bản mới nhất.
- Ingress là Traefik (chart `traefik` 42.0.0, app v3.7.14), thay ingress-nginx đã dừng bảo trì; lý do và bằng chứng ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md). `--component ingress` cài release `traefik` vào `kube-system` với `--skip-crds`, nên phải chạy sau `monitoring` (values tạo ServiceMonitor). Không tạo CRD `traefik.io`; rewrite `/nemesis` và `/hephaestus` nằm trong file provider của values.

### JMX heap và profile probe local

- Kafka chart 29.3.2 hard-code `MaxRAMPercentage=100`. `setup-phase1.sh --component kafka` luôn dùng renderer của repo để đổi thành `-Xms32m -Xmx128m`, giữ limit 256Mi cho exporter. Renderer từ chối namespace/tên/argv hoặc limit khác dự kiến. Không dùng `helm upgrade` trần để tránh mất cấu hình này.
- Cần Python có PyYAML. Helm 4 dùng plugin `postrenderer/v1` được copy vào Helm home của checkout (`scratch/helm/data/plugins/zero-door-kafka-jmx`); không cài plugin toàn máy. Helm 3 dùng cùng Python renderer qua executable/args; nhánh Helm 3 được kiểm mock, Helm 4 được kiểm render và runtime. [Thay đổi API chính thức của Helm](https://helm.sh/docs/plugins/migrate/).
- Requests của target-app giữ 410m/712Mi; limits mới 2025m/1920Mi. Currency/email/payment có startup budget 120s, timeout gRPC 3s; CPU limit lần lượt 400m/300m/300m. `setup-local-apps.sh --component target` cần Python/PyYAML để tách nguyên trạng hai manifest: apply Service/ServiceAccount trước, rồi apply và chờ từng Deployment theo thứ tự dependency (Redis trước cart, checkout và frontend sau backend). Sau mỗi rollout, chờ các pod đang terminating bị xóa trước khi bắt đầu Deployment tiếp theo; lỗi/timeout dừng script. Không apply cả hai file workload một lượt: ba surge đồng thời cần 3025m, vượt quota 3000m. Test kiểm steady và một surge của cả 9 Deployment trên đủ requests/limits CPU/RAM; baseline yêu cầu resource tường minh, không tự đoán LimitRange defaults. Không tăng quota/WSL.
- Nemesis đọc Kafka results trong một worker thread: construct/poll/close cùng một owner, hủy task có stop signal và drain worker. Test offline `python tests/test_nemesis_consumer.py` kiểm event loop, retry và cleanup; không phát message/lệnh thật. Entry point này giám sát tiến trình test con: quá 30s thì kết thúc tiến trình và trả exit 1, kể cả shutdown executor bị treo; CI job có trần 10 phút. Không sửa timeout để che vòng I/O chặn event loop.
- Các thay đổi probe/resource thuộc baseline lab mới, không là bằng chứng MTTD/MTTR tốt hơn. Mọi cấu hình đối chứng phải dùng cùng baseline và bắt đầu đo sau Ready/warm-up; không trộn với dataset cũ.
- Cloud deploy legacy chưa tích hợp/kiểm chứng renderer local này; không coi lượt sửa local là xác nhận đường cloud.

### Dựng lại lab nền từ cluster có sẵn (đã kiểm 18/10/2026)

Thứ tự dưới đây đã chạy thật trên `k3d-zero-door`; số đo, lỗi và kết quả có trong [lab-restoration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md). Mọi script kiểm Docker context `desktop-linux` (đổi bằng `ZD_DOCKER_CONTEXT`) và từ chối `DOCKER_HOST`.

Delta CL-01 sau review đổi đường apply target thành tuần tự như mô tả ở trên; delta này mới được kiểm mock và budget, chưa chạy lại trên cluster. Kết quả runtime trước đó không tự chứng minh đường apply mới đã được triển khai.

```bash
bash infrastructure/scripts/setup-phase1.sh --component namespaces
bash infrastructure/scripts/setup-phase1.sh --component monitoring
bash infrastructure/scripts/setup-local-apps.sh --component target
bash infrastructure/scripts/setup-phase1.sh --component logging
bash infrastructure/scripts/setup-phase1.sh --component kafka
bash infrastructure/scripts/setup-local-apps.sh --component gaia
bash infrastructure/scripts/setup-phase3.sh
bash infrastructure/scripts/setup-phase4.sh
# Bước ingress được thêm khi chuyển sang Traefik; kết quả chạy thật ghi trong traefik-migration.md
bash infrastructure/scripts/setup-phase1.sh --component ingress
bash infrastructure/scripts/setup-phase1.sh --component policies
bash infrastructure/scripts/verify-local-lab.sh --check all
```

- Lý do thứ tự: monitoring tạo CRD cho ServiceMonitor/PrometheusRule của Boutique và Kafka. Gaia cần Prometheus, Elasticsearch và Kafka. Phase3 yêu cầu `deployment/frontend`. Policies apply sau logging để Fluent Bit và Gaia vẫn tới được Elasticsearch.
- **Build image (Gaia, phase3, phase4) khi không đo và tốt nhất trước khi Boutique chạy.** Lần dựng 18/10, build/import Gaia đẩy CPU PSI avg300 lên khoảng 9. emailservice trượt probe gRPC (timeout 1s) và bị kubelet restart một lần.
- Image tag `latest` được restart sau import; script so image ID của pod với image vừa build. Với Docker containerd image store, ID so khớp là config digest.
- Các entry point trên chạy lại an toàn: namespace/target báo `unchanged`; `--component kafka` chạy lại Job provisioning trong quota khi đã đủ agent. Kết quả `verify` là probe kỹ thuật, không phải kết quả nghiên cứu.
- Profile nền: không HPA, không loadgenerator, không recommendation/ad (frontend chỉ ghi warning, luồng mua hàng vẫn qua). Boutique được kiểm qua port-forward loopback; đường host `:8080` qua Traefik được kiểm riêng bằng `verify-local-lab.sh --check ingress`.
- Sau migration, `frontend-external` là ClusterIP: nó không còn giữ port 80 của node, nên mọi request từ host `:8080` đi qua Traefik. Check `ingress` in ra `ClientHost` mà Traefik ghi cho request từ host và từ một pod; giới hạn IP nguồn được ghi trong evidence migration.
- Check `consumers` (cũng chạy ở cuối `ingress` và `all`) kiểm metric Traefik và query của Gaia/Nemesis:
  - Mỗi vòng gửi 3 request `GET /_healthz` lành qua `:8080`, rồi chờ một lần scrape có chứa chúng.
  - Ngay sau lần scrape đã xác nhận thứ hai, query đọc từ source phải có giá trị `frontend` lớn hơn 0.
  - Giới hạn: tối đa 4 vòng (12 request), mỗi vòng chờ tối đa 9 lần poll 5s.
  - Lý do: `rate()` và P99 cần hai mẫu khác nhau trong cửa sổ 1m. Một loạt request kết thúc trước lần scrape đầu, hoặc đã cũ hơn cửa sổ, cho rate 0 và P99 NaN dù hệ khỏe.
  - Chạy lại riêng (`--check consumers`) ngay trước khi đọc kết quả, nếu lượt trước đã để cửa sổ trôi qua.
- Không đọc được log (Gaia ở `agents`, Traefik ở `ingress`) là FAIL, không bị coi là "không có lỗi".
- Rollback port 80 (bước R1 của evidence migration) dùng `bash infrastructure/scripts/setup-phase1.sh --component ingress --ingress-cluster-ip`. Lệnh đi qua cùng guard Docker/context, `--kube-context k3d-zero-door` và Helm cache trong `scratch/`. Nó chỉ `helm upgrade` release `traefik` với Service ClusterIP, không install/uninstall.
- Frontend v0.10.5 không có `/metrics`. Manifest ServiceMonitor cũ đã bỏ; `setup-local-apps.sh --component target` thu hồi riêng `target-app/frontend-monitor` nếu còn. HTTP metrics do ServiceMonitor của Traefik cung cấp, CPU do cAdvisor; không chấp nhận target 404.
- Exit code của `verify-local-lab.sh`:
  - `0`: mọi probe đạt.
  - `1`: có bất kỳ FAIL nào, gồm cả target scrape lỗi 404.

  Chỉ exit `0` là đạt. Exit `3` trong evidence cũ là kết quả trước lượt sửa cuối, không còn là ngoại lệ hiện hành.
- Kết quả cuối phải lấy từ lần `verify` chạy **sau** mọi build/rollout agent. Kết quả trước build chỉ dùng để chẩn đoán.

Hướng dẫn legacy cũ cho target/Gaia ([2026-10-09](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/2026-10-09-legacy-demo-restart.md)) chỉ còn giá trị lịch sử; dùng `setup-local-apps.sh`.

## Context, đường dẫn và tiến trình

- Các script local khóa `k3d-zero-door`, Helm dùng `--kube-context`, image import khóa cluster `zero-door`; không thay current-context của project khác.
- Script tìm root từ chính vị trí file, không phụ thuộc thư mục gọi. Các đường dẫn được quote để hỗ trợ thư mục có dấu cách.
- Git Bash có cơ chế đổi đối số đường dẫn cho chương trình native; cách kiểm soát và `cygpath` được mô tả trong [MSYS2 Filesystem Paths](https://www.msys2.org/docs/filesystem-paths/). Thư viện local tắt chuyển tự động cho CLI và đổi riêng đường dẫn file phía host bằng `cygpath -m`, giữ nguyên đường dẫn container/URL/RBAC identity. Khi chạy lệnh thủ công có đối số container như `/bin/sh` hoặc `--as=system:...`, dùng `MSYS_NO_PATHCONV=1` cho chính lệnh đó; đường dẫn file host nên tương đối hoặc dạng `R:/...`.
- Nhánh cluster sửa hostname `host.docker.internal` chỉ sau khi đối chiếu cổng Docker và thử localhost bằng TLS thành công; backup kubeconfig trước khi ghi. Custom `KUBECONFIG` được giữ nguyên và báo cần sửa riêng. Cổng API được lấy từ mapping, không hardcode số cổng của snapshot cũ.
- Port-forward chỉ bind `127.0.0.1`. Script dùng [Bash trap và signal](https://www.gnu.org/s/bash/manual/html_node/Signals.html), chạy ở foreground, ghi log từng tunnel vào thư mục tạm và giám sát PID. Không kill mọi kubectl, không chiếm cổng bằng cách dừng tiến trình lạ; cổng bận hoặc tunnel chết làm script thoát lỗi và dọn child của nó.
- Sau rollout, dừng terminal tunnel cũ bằng Ctrl+C rồi mở lại khi cần. Không chạy hai supervisor cùng giữ một bộ cổng.

## Thực nghiệm legacy là thao tác riêng

Chỉ khi được phép chạy smoke trong lab của nhóm:

```bash
# Cài dependency vào venv riêng và giữ health tunnels; không tự attack
bash infrastructure/scripts/setup-phase5.sh --install-deps

# Sau khi dừng session trên bằng Ctrl+C, chạy E1 AUTO rõ ràng
bash infrastructure/scripts/setup-phase5.sh --run-smoke --smoke-runs 2
```

Cờ cũ `-SkipExperiments` được thay bằng `--skip-experiments` (hiện cũng là mặc định); `-SmokeRuns` thay bằng `--smoke-runs`. Không truyền cờ PowerShell vào Bash.

Smoke dùng runner Kafka legacy, giữ nguyên các giới hạn về advertised listeners, cách đo và failure handling của runner đó; wrapper không chứng minh nghiên cứu đã được sửa. Child runner nhận kubeconfig tạm chỉ chứa context ZERO DOOR. CSV mới đi vào `scratch/experiments/<timestamp-pid>/raw_data/`, không gộp vào dataset cũ, không tự chạy analysis lên các CSV lịch sử. Exit 0 của runner không chứng minh từng run thành công: phải đọc CSV/log và giữ mọi failure.

## Lịch sử và kiểm chứng chuyển đổi

Bảy file `.ps1` cùng tên gốc đã được thay bằng `.sh`; không cần cài hoặc gọi PowerShell. Tên cũ trong archive/handoff/audit/ảnh báo cáo mô tả revision cũ và được giữ để truy vết. Mã cũ xem tại Git revision `1f43ff1461c2199bc99e9962483956c3df0fa975`; không đổi tên trong nhận xét lịch sử rồi quy hành vi cũ cho script mới.

```bash
bash tests/shell/run.sh
```

Kiểm thử dùng CLI giả lập, không deploy hoặc gọi Docker thật.

```bash
ZD_PROMTOOL=/path/to/promtool bash tests/shell/test-local-restore.sh
```

`test-local-restore.sh` là regression thật cho hợp đồng ingress, không mock và không gọi cluster. Script:
1. Tải chart Traefik đã pin, so SHA-256 với `chart-versions.yaml`.
2. Render với values repo và kiểm: `honorLabels`, không CRD, rewrite, args, và bản render rollback Service ClusterIP.
3. Dùng `promtool` (Prometheus 3.15.0, cùng bản lab) đánh giá PrometheusRule cùng query Gaia/Nemesis đọc từ source, trên series Traefik giả lập. Có cả cổng consumer: một loạt request trước lần scrape đầu không bao giờ đạt; hai lần scrape đã xác nhận thì đạt.

`run.sh` và `test-local-restore.sh` phải đạt cả khi môi trường đặt sẵn `MSYS_NO_PATHCONV=1` và `MSYS2_ARG_CONV_EXCL=*`. Đường dẫn đưa cho chương trình native (Python, Helm) phải đổi qua `cygpath -m` / `zd_path`.

Script cần mạng tới `traefik.github.io`, `helm` và PyYAML. Xem [evidence chuyển đổi](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/bash-migration.md) để phân biệt kiểm tra cú pháp/mock với runtime rollout đầy đủ.
