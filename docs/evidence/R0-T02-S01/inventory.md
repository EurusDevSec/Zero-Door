# ZER-34 — Inventory local và kiểm tra tài nguyên

> Cập nhật công cụ 18/10/2026: tên script `.ps1`, số dòng và hành vi được ghi dưới đây thuộc revision cũ, trước chuyển đổi Bash. Không quy các nhận xét đó cho script `.sh` mới. Vận hành hiện tại theo [Bash tooling](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md); mã cũ tra Git revision `1f43ff1461c2199bc99e9962483956c3df0fa975`.

Phiên 18/10/2026, Asia/Saigon. Kiểm tra theo yêu cầu Hoàng trước khi khôi phục lab. Đây là **báo cáo một phần**, chưa đủ để kết luận lab đã tối ưu hay sẵn sàng chạy nghiên cứu.

## Phạm vi và revision

- Issue/AC đọc live: [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc), ngày 18/10/2026, khoảng 09:37 +07:00.
- Branch `main`; HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`.
- `git -c core.fsmonitor=false status --short` trước kiểm tra: rỗng.
- Thao tác: đọc cấu hình, Git, số đo host và truy vấn Docker/WSL/Kubernetes. Không start/stop/recreate, apply, build, inference, đọc secret hoặc đổi context.
- Phạm vi ghi: báo cáo này và phần bàn giao trong `docs/delivery/milestones/R0-foundations/local-lab.md`. Không commit/push hoặc cập nhật Linear.

## Quan sát trực tiếp

| Truy vấn thực tế | Kết quả |
| --- | --- |
| `Get-CimInstance Win32_OperatingSystem` và `Win32_Processor` | 09:37:54 +07:00: RAM vật lý khả dụng cho OS 15,78 GiB; FreePhysicalMemory 4,55 GiB; khoảng 11,23 GiB đang dùng. i7-11800H, 16 logical processors; LoadPercentage 24% tại mẫu này. Không phải tải trung bình dài hạn. |
| `Get-Process`, gom theo ProcessName và cộng WorkingSet64 | Mẫu sau: Chrome 15 process / 2,68 GiB; claude 12 / 2,31 GiB; ChatGPT 14 / 1,75 GiB. Working set có phần trang chia sẻ, không cộng thành RAM vật lý độc quyền hoặc suy số phiên đang mở. |
| Đọc `C:\Users\ACER\.wslconfig` | `[wsl2] memory=7GB`, `processors=4`, `swap=2GB`. Đây là cấu hình trên đĩa, chưa xác minh effective limits của VM đang chạy. |
| `docker context show` | Exit 0: `desktop-linux`. |
| `docker info --format '{{json .NCPU}} {{json .MemTotal}}'` | Exit 1: named pipe `dockerDesktopLinuxEngine` không tồn tại. Output `0 0` là kết quả lỗi, **không phải** tài nguyên Engine đo được. |
| `docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'` | Exit 1, cùng lỗi pipe. Chưa biết inventory container/port; không coi là danh sách rỗng. |
| `docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}'` | Exit 1, cùng lỗi pipe. Chưa có số đo workload. |
| `k3d cluster list` | Exit 1 do Engine không truy cập được; chưa chứng minh cluster còn hay mất. |
| `wsl --list --verbose` | Exit 0: `docker-desktop`, trạng thái `Stopped`, version 2. |
| `kubectl config current-context` | Exit 0: `k3d-zero-door`. Context lưu trên đĩa không chứng minh cluster tồn tại. |
| `kubectl config view --minify -o jsonpath={.clusters[0].cluster.server}` | Exit 0: `https://127.0.0.1:58117`. Chỉ xuất server URL, không xuất kubeconfig/credential. |
| `kubectl --context k3d-zero-door --request-timeout=5s get nodes -o wide` | 09:38:41 +07:00, exit 1: connection refused. Chưa biết node version/args hoặc tài nguyên pod. |

Các CLI Docker/k3d/WSL có timeout subprocess 22 giây; truy vấn kubectl node có request timeout 5 giây và subprocess timeout 12 giây. Không có lệnh timeout trong các kết quả trên.

Trong sandbox, CIM bị từ chối và Get-Process chỉ thấy vài process của sandbox. Các giá trị RAM bằng 0 sinh ra từ lỗi CIM đã bị loại khỏi kết luận. Mẫu host trong bảng là lần đọc ngoài sandbox được công cụ cho phép. Đọc Docker settings chỉ lấy trường tài nguyên/AutoStart, không xuất toàn bộ JSON; chỉ tìm được AutoStart=false, không suy giá trị RAM/CPU từ các trường không có.

## Nguồn người dùng

Sau khi xem kết quả, Hoàng xác nhận Docker đang tắt và lần reset Docker trước đã làm mất container cũ; yêu cầu hướng dẫn chạy lại. Đây là xác nhận của người dùng, chưa phải inventory Docker/volume đọc thành công. Chưa biết image, volume và dữ liệu nào còn; không khuyến nghị delete/prune/reset thêm.

## Đối chiếu repo — chưa chứng minh đã apply

- `infrastructure/k3d-config.yaml`: 1 server + 1 agent, disable Traefik; chưa có giới hạn RAM từng node trong file. Chưa có live node để xác nhận topology.
- `infrastructure/helm-values/prometheus-values.yaml`: Alertmanager off, scrape/evaluation 30s, retention 3 ngày. Prometheus request 512Mi / limit 1Gi; Grafana request 256Mi / limit 512Mi. Chú thích tổng ~800MB không phải số đo và không đại diện tổng limits hiện khai báo.
- `infrastructure/helm-values/kafka-values.yaml`: 1 controller, 0 broker riêng; request 256Mi / limit 768Mi.
- `infrastructure/logging/elasticsearch.yaml`: 1 replica, JVM Xms256m/Xmx512m, container request 512Mi / limit 1Gi. Heap không đại diện toàn bộ memory process.
- Tổng request bốn thành phần trên: 1536Mi; tổng limit 3328Mi. Không phải RAM thực dùng, chưa tính sidecar/exporter, Fluent Bit, app, agent hoặc node/Kubernetes overhead. Không dùng tổng này làm dự báo đầy đủ tài nguyên lab.
- `infrastructure/resource-quotas/monitoring-quota.yaml`: quota requests.memory=6Gi, limits.memory=10Gi; đây là trần khai báo namespace, không phải đang chiếm 10Gi và không tạo thêm RAM ngoài trần WSL. Chưa có sizing thống nhất được kiểm chứng cho toàn bộ lab.
- `infrastructure/manifests/target-app-raw.yaml` có loadgenerator 1 replica; chưa chứng minh nó được triển khai. Cần kiểm tra live trước khi quy CPU cao cho tải nền này.
- `infrastructure/manifests/target-app-hpa.yaml` cho frontend/cartservice 1–3 replica; chưa chứng minh HPA đang chạy hoặc đã scale.

## Kết luận và bước tiếp

1. Repo đã có một số cấu hình giảm tải, nhưng **chưa có bằng chứng tối ưu runtime**. Khi Engine tắt, RAM host đã dùng khoảng 71%; dư địa cho lab cùng ứng dụng desktop đang hẹp tại thời điểm mẫu.
2. Chưa xác định thủ phạm CPU/RAM của k3d vì không có Engine/pod metrics. Không hạ trần WSL tùy ý hoặc tắt dependency của Gaia để làm số RAM đẹp hơn.
3. Hướng dẫn Hoàng mở Docker Desktop, kiểm tra Engine rồi đọc `docker ps -a`, `docker volume ls`, `k3d cluster list`. Nếu còn cluster thì dùng start; nếu xác nhận mất cluster thì dựng lại theo cấu hình repo. Không dùng `start-demo.ps1` để tạo cluster: nó chỉ mở port-forward và còn dừng mọi kubectl trên máy.
4. Để kiểm soát tải, đo riêng Docker idle → cluster rỗng → từng nhóm dịch vụ. Truy vấn `docker stats --no-stream`, `kubectl top nodes`, `kubectl top pods -A`, replica/restart/event. Chỉ dùng top khi metrics API sẵn sàng; lỗi metrics không đồng nghĩa mức dùng bằng 0. Khôi phục đầy đủ workload thuộc ZER-35, không được coi đã chạy trong phiên này.
5. Hướng dẫn dựng đầy đủ bản cũ đang có tại `docs/runbooks/2026-10-09-legacy-demo-restart.md`, phần E. Đã đọc lại setup-phase1/3/4 trong phiên; chưa chạy thử. Setup-phase1 chưa pin chart Prometheus/Ingress; phase3 có `go mod tidy` nếu Go có trên máy. Cần giữ lỗi đầu tiên và kiểm tra Git dirty nếu dùng script.

Tham chiếu ngữ nghĩa: [Microsoft WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config), [Kubernetes resource requests/limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/). `memory` WSL là mức tối đa được cấu hình; requests/limits Kubernetes không là phép đo sử dụng.

## AC / bằng chứng còn thiếu

| AC ZER-34 | Đánh giá của báo cáo này |
| --- | --- |
| AC-01 | Có branch/HEAD/dirty, thời điểm và lệnh/kết quả phía trên. |
| AC-02 | Đã ghi lỗi Engine; container/volume/port inventory và usage đang UNKNOWN. Volume chưa truy vấn do Engine không hoạt động. |
| AC-03 | Có context/endpoint và lỗi API; node version/args chưa xác minh. |
| AC-04 | Phiên chỉ đọc môi trường; chỉ thêm tài liệu đã nêu. |
| AC-05 | Phân biệt static/live/user-reported, không tuyên bố lab phục hồi hoặc tối ưu xong. |
| AC-06 | Chưa có review độc lập hoặc artifact remote được người dùng duyệt; file chỉ ở checkout local. |

Chưa đóng issue. Chưa thay đổi ngày, trạng thái, assignment hoặc AC trên Linear.

## Kiểm tra lại sau khi Hoàng mở Docker — 18/10, 09:45–09:46 +07:00

Yêu cầu mới của Hoàng: đã bật Docker, nhờ kiểm tra. Chỉ đọc; không dựng/start/stop cluster hoặc workload. HEAD không đổi; trước lượt này working tree có đúng ghi chú local-lab đã sửa và thư mục evidence do phiên trước tạo. Phạm vi ghi mở rộng thêm `docs/delivery/NOW.md` để sửa con trỏ artifact không còn đúng. Không ghi cấu hình host.

### Lệnh và kết quả mới

Các truy vấn trong nhóm đầu bắt đầu 09:45:01 +07:00; subprocess timeout 20 giây/lệnh, không timeout. Các lệnh thành công thay thế UNKNOWN tương ứng của mẫu Engine tắt, không thay đổi lịch sử mẫu trước.

| Lệnh | Kết quả thực tế, exit 0 nếu không ghi khác |
| --- | --- |
| `docker context show` | `desktop-linux`. |
| `docker info --format '{{json .NCPU}} {{json .MemTotal}}'` | `4 7271460864`: Engine thấy 4 CPU, khoảng 6,77 GiB RAM. |
| `docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'` | 5 container S-cool đều Exited: scool_queue (137), scool_app (0), scool_mysql (0), scool_nginx (0), scool_mailpit (0). Không có container k3d. Không suy nguyên nhân exit 137 là OOM nếu chưa kiểm State.OOMKilled/events. Không khởi động/chỉnh container S-cool. |
| `docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}'` | Output rỗng, exit 0; sau đó `docker ps --format '{{.Names}}\t{{.Status}}'` cũng rỗng. Xác nhận không có container Docker đang chạy tại hai mẫu này. |
| `docker volume ls --format '{{.Name}}\t{{.Driver}}'` | 5 volume local: buildx_buildkit_default_state, n8n-youtube-automation_n8n_data, scool-eur20-audit_scool_mysql_data, scool-eur20-pr19_scool_mysql_data, scool_scool_mysql_data. Không có tên volume k3d; không đọc nội dung hay xóa volume. Không kết luận không có backup/data ở đường dẫn khác. |
| `k3d cluster list` | Chỉ header NAME / SERVERS / AGENTS / LOADBALANCER. Xác nhận không có cluster k3d được liệt kê trong Engine/context hiện tại. |
| `kubectl config current-context` | Vẫn `k3d-zero-door`, là context cũ trên đĩa; không chứng minh cluster còn. Không gọi API cũ lặp lại sau khi đã xác nhận cluster không tồn tại trong inventory này. |
| `wsl --list --verbose` | docker-desktop Running, version 2. |
| `docker system df` | 12 images / 1,889GB; 5 containers / active 0 / 54MB; 5 local volumes / 1,218GB; 120 build-cache records / 13,5GB, reclaimable 13,37GB. Đây là dung lượng **đĩa**, không phải RAM. Không prune. |
| `wsl --version` | WSL 2.7.11.0, kernel 6.18.33.2-2. Output native UTF-16 có ký tự NUL trong capture PowerShell, nội dung phiên bản đọc được; không phải CLI thất bại. |
| Đọc `.wslconfig` | Không đổi: memory=7GB, processors=4, swap=2GB. Không có khai báo autoMemoryReclaim rõ ràng trong file; không suy chức năng đang disabled. |

### Số đo host và Linux

`Get-CimInstance Win32_OperatingSystem`, `Win32_Processor` và `Get-Process`:

- 09:45:20: RAM host 15,78 GiB, còn 1,49 GiB; LoadPercentage 15%. vmmemWSL WorkingSet ~4,31 GiB. Tổng working set theo tên: Chrome ~2,02 GiB, claude ~1,71 GiB, ChatGPT ~1,33 GiB; có shared pages nên không cộng thành bộ nhớ độc quyền.
- Ba mẫu tiếp: 09:45:56 / 09:46:00 / 09:46:04, RAM host trống 1,66 / 1,63 / 1,62 GiB; CPU 17 / 11 / 16%; vmmemWSL 4,31 / 4,31 / 4,30 GiB. Không phải phép đo steady-state dài hạn; chưa kết luận về spike lúc build hoặc load test.

Lệnh chỉ đọc trong WSL đang chạy, timeout 18 giây, exit 0:

```text
wsl -d docker-desktop -- sh -c 'cat /proc/meminfo; cat /proc/pressure/memory; ps -o pid,comm,rss'
```

Mẫu 09:45:39:

| Trường /proc/meminfo | Giá trị kB (Linux, KiB) | Xấp xỉ GiB |
| --- | ---: | ---: |
| MemTotal | 7101036 | 6,77 |
| MemFree | 2838696 | 2,71 |
| MemAvailable | 6413184 | 6,12 |
| Cached | 3410528 | 3,25 |
| Buffers | 286884 | 0,27 |
| SwapTotal / SwapFree | 2097152 / 2097152 | 2,00 / 2,00 |

Memory pressure `some/full avg10/60/300=0.00`, total=0. Process names/RSS thấy dockerd ~108Mi, containerd ~60Mi, và các tiến trình nền initd/bootstrap. Không lấy command line/env, không đọc secret. MemAvailable gồm free và phần có thể thu hồi, không cộng thêm Cached vào nó.

### Kết luận mới và giới hạn

- Docker Engine đã hoạt động. ZERO DOOR **chưa chạy**, vì không có cluster/container k3d trong Engine hiện tại. Do đó không thể quy CPU hiện tại cho pod ZERO DOOR hoặc đo sizing của workload bằng mẫu này.
- RAM hiển thị cho WSL phần lớn tương ứng file cache Linux; không đủ bằng chứng kết luận rò rỉ. Linux có thể cấp phát khoảng 6,12 GiB ở mẫu trên, còn Windows chỉ thấy khoảng 1,5–1,7 GiB trống. Hai góc nhìn này không mâu thuẫn và không được thay thế cho nhau khi đánh giá độ mượt desktop.
- Docker docs giải thích page cache có thể giữ RAM sau build và đề cập autoMemoryReclaim: https://docs.docker.com/desktop/features/wsl/ . Microsoft hiện ghi mặc định autoMemoryReclaim=dropCache: https://learn.microsoft.com/en-us/windows/wsl/wsl-config . Chưa xác minh hiệu lực/timing reclaim trên máy; **không đề xuất thêm gradual với giả định mặc định đang tắt**, không drop_caches hay restart WSL trong phiên kiểm tra.
- Chưa có bằng chứng CPU bị bão hòa trong các mẫu ngắn. Chưa có baseline dài hoặc CPU của VM qua chu kỳ tải.
- Build cache 13,5GB là vấn đề dung lượng đĩa riêng; xóa cache không đồng nghĩa sửa được 13,5GB RAM. Volume S-cool/n8n giữ nguyên.
- Bước tiếp theo: giảm ứng dụng/tab desktop không cần bằng lựa chọn của Hoàng, rồi dựng **cluster nền** từ cấu hình repo khi thực hiện ZER-35. Đo RAM/CPU trước và sau; triển khai từng nhóm dependency thay vì chạy một lượt toàn bộ setup. Chưa thay trần 7GB/4CPU; chưa chứng minh một mức trần nhỏ hơn đủ cho toàn lab.

### Phần AC được bổ sung

AC-02 nay có inventory container/volume/port và mẫu Docker stats hợp lệ; không có container chạy nên không có pod resource usage. AC-03: cluster không hiện diện trong inventory k3d thành công, nên live node version/args N/A cho trạng thái này; không có runtime proof NetworkPolicy. AC-06 vẫn chờ review/chia sẻ được duyệt. Không tự đóng ZER-34 hoặc ZER-6; không thay live metadata.
