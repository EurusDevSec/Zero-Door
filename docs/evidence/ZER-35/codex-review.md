# ZER-35 — Codex review báo cáo Claude

> Retest 18/10/2026 11:49 +07:00: **đủ cơ sở chuẩn bị thực thi riêng bước namespace/quota; chưa chấp nhận kế hoạch full stack hoặc cấp quyền mutation từ tài liệu này.** Xem mục retest cuối file.

## Kết luận và phạm vi

**NEEDS DISCUSSION / cần chỉnh báo cáo trước khi dùng B.5 như runbook triển khai đầy đủ.** Báo cáo có giá trị làm đầu vào sizing; chưa là cấu hình đã chứng minh vừa máy hoặc lab đã hoàn tất. Chưa chấp nhận mọi finding của phần A là defect đã tái hiện.

Ngày review: 18/10/2026, Asia/Saigon. Người review: Codex. Target: docs/evidence/ZER-35/claude-review-and-resource-profile.md, bản hoàn tất 11:13:16 +07:00, cùng source/config dùng để đối chiếu. HEAD vừa kiểm tra: 1f43ff1461c2199bc99e9962483956c3df0fa975, main; staged diff rỗng. Working tree có migration Bash và evidence/handoff chưa commit; Claude report untracked. Không suy số dòng dưới đây từ HEAD đã commit: các dòng thuộc working tree được đọc lúc review.

Phạm vi lượt này: đọc báo cáo và nguồn liên quan, đọc metadata Git/GitNexus, truy cập tài liệu upstream, probe Python tĩnh trên YAML; ghi file review này và nối con trỏ bàn giao vào NOW/local-lab. Không sửa báo cáo Claude, source/config vận hành, không chạy lab hoặc đổi Linear/Git publication.

## Findings cần Claude xử lý

### CR-01 — HIGH — hướng dẫn gỡ nhóm có thể xóa PVC

Anchor: báo cáo Claude:224. B.5 gợi ý kubectl delete -f <file> khi thiếu tài nguyên, đồng thời nói xóa PVC cần quyết định riêng. Hai hướng dẫn mâu thuẫn với cấu trúc file thực tế.

Probe tĩnh YAML cho infrastructure/logging/elasticsearch.yaml trả:
- Deployment/elasticsearch
- PersistentVolumeClaim/elasticsearch-data (nguồn :67–78)
- Service/elasticsearch

Nếu thay <file> bằng file log vừa apply, lệnh sẽ yêu cầu xóa cả PVC. Chưa chạy lệnh xóa; tác động tới dữ liệu thực phụ thuộc PV/reclaim policy. Kubernetes mô tả Delete reclaim policy có thể xóa tài sản lưu trữ phía dưới: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#delete.

Yêu cầu: bỏ rollback tổng quát bằng file chứa nhiều loại tài nguyên; nêu rõ allowlist workload/release, kiểm tra inventory/PVC/reclaim trước, phân biệt tài nguyên mới tạo với tài nguyên có trước. Khi pressure/lỗi: dừng thêm nhóm, giữ evidence; chỉ dừng/gỡ workload đã chốt phạm vi. Không tự uninstall chart hoặc delete namespace/config/PVC như cleanup mặc định. Muốn giữ dữ liệu thì kế hoạch rollback phải chỉ rõ loại/tên tài nguyên, không chỉ câu cảnh báo.

### CR-02 — MEDIUM — ngân sách chart chưa đủ làm căn cứ admission

Anchor: báo cáo Claude:115–140,154–156,191–193,273.

JMX được tạm tính theo LimitRange, monitoring còn chart default chưa biết nhưng dùng dấu ≤ như một cận trên. Chưa render chart nên chưa biết đầy đủ sidecar/init/hook/provisioning job, effective Pod requests/limits, replica và quy tắc min/max của LimitRange. Vì vậy chưa đủ cơ sở khẳng định quota zero-door đủ cho cài Kafka và rollout, hoặc khẳng định scheduler sẽ nhận toàn bộ stack. Scheduler còn xét từng node, affinity và các ràng buộc khác; tổng capacity bị báo gấp đôi không loại bỏ mọi kiểm tra scheduling.

Repo bật provisioning.enabled và metrics.jmx.enabled (kafka-values.yaml:51–52,85–94). Upstream chart 29.3.2 đặt metrics.jmx.resourcesPreset và provisioning.resourcesPreset là micro; không mặc nhiên nhận defaultRequest 64Mi của namespace. Values upstream còn đặt cả heapOpts và controller.heapOpts thành -Xmx1024m -Xms1024m, trong khi limit controller ở repo là 768Mi. Đây là xung đột cấu hình cần giải quyết trước Kafka; chưa khẳng định đã quan sát OOM thật.

Nguồn version cụ thể: https://raw.githubusercontent.com/bitnami/charts/kafka/29.3.2/bitnami/kafka/values.yaml. Effective init/app resource semantics: https://kubernetes.io/docs/concepts/workloads/pods/init-containers/#resource-sharing-within-containers.

Yêu cầu: đổi tổng chưa biết thành estimate/UNKNOWN, không cận trên chắc chắn. Trước cài từng chart, chọn version cụ thể, đọc dependency/default, render bằng values của repo và kiểm tài nguyên hiệu dụng + LimitRange/quota + hooks. Ghi cả artifact/version/digest khi có. Đặt đúng key controller.heapOpts sau đối chiếu template; chọn heap chừa native/off-heap, không chỉ nhỏ hơn limit trên giấy. Chưa tải/cài chart trong lượt review này; template fetch qua web bị cache miss nên hiệu lực render cuối vẫn cần xác minh. Tổng 3,2–4,9 GiB tiếp tục là estimate để tổ chức đo, không là acceptance.

### CR-03 — MEDIUM — topology tính quota khác topology trong kế hoạch triển khai

Anchor: báo cáo Claude:124,149–154,232,236.

B.3 giả định frontend/cart có HPA 1–3, nhưng B.5 bước Boutique thiếu infrastructure/manifests/target-app-hpa.yaml. Runbook legacy mà bước này dựa vào cũng thiếu lệnh apply HPA trong nhánh dựng mới. Nếu chạy đúng danh sách B.5 trên cluster trống, không tạo hai HPA dùng trong phép tính. Bảng 1425m nền / 2225m HPA tối đa là đúng theo manifest; thêm stress 1000m = 3225m, thêm một surge 200m = 3425m, vượt quota 3000m hiện tại.

Yêu cầu: ghi rõ HPA thuộc profile nào, lệnh apply và kiểm chứng nếu bật; nêu tương tác HPA với healer và cấu hình đối chứng. Không tự bật/tắt HPA để làm kết quả đẹp. Nếu chỉ khôi phục nền trước, ghi HPA deferred và không gọi topology đó là profile thí nghiệm đã khóa. Gaia dùng mutable image với imagePullPolicy Never (gaia-deployment.yaml:27–28); đường dựng lặp lại cần bước cập nhật image thực sự khi Deployment không đổi (restart/immutable tag thích hợp), timeout rollout và image identity. Đây là thiếu sót kế hoạch, chưa có rollout mới nào bị lỗi thực tế trong review này.

### CR-04 — MEDIUM — mẫu số KPI đang được chọn thay cho quyết định nghiên cứu

Anchor: báo cáo Claude:158.

P179 trong bản trích chỉ ghi CPU target app tăng >80%, không chỉ rõ mẫu số là limit. Gaia hiện hardcode 0.200 (redis 0.125) tại gaia/main.py:149–169, nhưng implementation cũ không có thẩm quyền định nghĩa lại KPI. HPA đang dùng CPU Utilization theo request tại target-app-hpa.yaml:14–19,34–39; hai đại lượng khác nhau.

Yêu cầu: sửa phải là limit thành đề xuất định nghĩa cần khóa tại issue scope/measurement; ghi CPU cores, request, limit và công thức % riêng, áp vào đúng container mục tiêu. Giữ nguyên yêu cầu không tính CPU của stress pod thay CPU app và không chỉnh limit chỉ để đạt KPI. Không mở rộng lượt này thành sửa detector.

### CR-05 — MEDIUM — kết luận độ phân giải MTTD bỏ qua độ trễ cửa sổ CPU

Anchor: báo cáo Claude:195; nguồn gaia/main.py:149 dùng rate(...[2m]).

30s scrape và 15s poll chỉ là hai thành phần của độ trễ. Cửa sổ trung bình 120s có thể làm vượt ngưỡng chậm đáng kể. Ví dụ lý tưởng CPU từ 0 lên 100% limit, để trung bình cửa sổ đạt >80% cần hơn 96s; đây là ví dụ toán học, không phải kết quả đo Prometheus thật (thực tế còn sampling/extrapolation/phase). Vì vậy câu vẫn đo được ngưỡng <60s cần tách khỏi claim đạt ngưỡng hoặc chỉ bị giới hạn vài chục giây.

Yêu cầu: ghi feasibility MTTD chưa xác minh; định nghĩa onset/detect và đo end-to-end độc lập trước khi chọn window/cadence. Không hứa đạt <60s từ giá trị cấu hình hiện tại và không đổi window trong loạt thí nghiệm mà thiếu protocol/revision.

## Đánh giá lại A-F1 đến A-F9

| Mục Claude | Nhận xét Codex |
| --- | --- |
| A-F1 | Có căn cứ: common.sh:90 không tắt switch-context; k3d mặc định true. Sửa trước lần tạo mới; không cần recreate cluster hiện có để sửa điểm này. Nguồn: https://k3d.io/v5.8.3/usage/commands/k3d_cluster_create/. |
| A-F2 | Có bằng chứng upstream trực tiếp với kafka-python 2.0.2/Python 3.12. Chưa chạy lại venv host này. Pin bản đã kiểm chứng import/API dùng trong runner; không trộn kafka-python và kafka-python-ng trong cùng env vì cùng namespace import. Không cần buộc pin mọi package như một fix bắt buộc để giải quyết riêng lỗi import này. Nguồn: https://github.com/dpkp/kafka-python/issues/2412. |
| A-F3 | Thiếu entry point tự động không tự chứng minh vi phạm AC: lệnh tay được ghi đầy đủ và kiểm chứng vẫn có thể tái lập. Là đề xuất cải thiện đường dựng; thiếu restart/identity Gaia và HPA trong kế hoạch là vấn đề cụ thể cần sửa. Không cần chờ script mới mới được chuẩn bị namespace. |
| A-F4 | Guard Docker context hữu ích trước mutation; chọn chính sách rõ cho desktop-linux và custom context, không tự chuyển context. Không trì hoãn kiểm đúng daemon chỉ vì đã đúng Kubernetes context. |
| A-F5 | Log tạm giữ lại không tự là defect bảo mật; kubeconfig raw sót sau kill cứng là rủi ro cần ownership/ACL/cleanup rõ. Trap không thể bảo đảm cleanup SIGKILL. Chưa chứng minh user khác đọc được file trên máy này. |
| A-F6 | Pin/record chart version là việc trước cài chính chart đó, không làm sau khi đã dựa vào resource budget/default. Helm repo mutation phải nằm trong action scope. |
| A-F7 | Kiểm đúng binary/dispatch behavior và version thực khi chạy để đánh giá skew; không tự đổi PATH/cài kubectl. |
| A-F8 | Fail-fast khi health không đạt là hành vi chủ ý, chưa tái hiện timeout bất hợp lý; không tính như bug đã xác nhận. Có thể cải thiện timeout/diagnostic nếu có repro. |
| A-F9 | Phần giải thích đúng về giới hạn; tiêu đề sẽ có hiệu lực vẫn mạnh hơn bằng chứng. Chỉ xác nhận controller khởi động; cần probe allowed/denied thực để kết luận enforcement. |

## Quyết định và bước tiếp theo

- D1: khuyến nghị giữ cấu hình WSL hiện tại làm baseline thử nghiệm; không yêu cầu Hoàng xác nhận lại chỉ để không đổi máy. Không khẳng định full stack vừa trước khi đo.
- D2: gửi Claude chỉnh báo cáo theo CR-01–05 trước. Sửa source/config vận hành thuộc lượt triển khai sau; chưa tự cấp quyền từ review này.
- D3: tăng quota CPU 3 lên 4 là lựa chọn có căn cứ admission cho tổ hợp đã tính, không thêm CPU vật lý; chưa bắt buộc làm trước bước namespace nền. Khi chọn profile thí nghiệm phải tính lại cả HPA/surge/stress và dịch vụ bổ sung.
- D4: kiểm tra luồng mua hàng trước; thiếu recommendation/ad là nghi vấn cần probe, chưa đủ kết luận phải thêm cả hai. Không hỏi Hoàng cho phép bỏ tiêu chí nghiệp vụ.
- D5: Hoàng đã nói Claude thực hiện chính, Codex review, Hoàng luyện/theo dõi. Không cần hỏi lại ai làm chính. Quyền mutation cụ thể vẫn tách theo nhóm; một bên thao tác cluster tại một thời điểm.

**Lượt Claude tiếp theo:** sửa tài liệu báo cáo theo findings, bổ sung render/default analysis trước từng chart và allowlist rollback; chưa apply, install, sửa source hoặc config lab. Trả lại danh sách mục đã sửa với nguồn/bằng chứng. Sau đó chốt một phạm vi thực thi nhỏ: kiểm context + apply namespace/quota + đo trước/sau. Không cần đợi quyết định provider hoặc dependency recommendation/ad mới làm được bước chuẩn bị này; không cần chốt toàn bộ D1–D5 như một gate chung.

## Coverage và giới hạn

Đã đọc báo cáo A–D, các entry point liên quan, common.sh, K3d/Helm values, quota, Gaia CPU query, target/HPA, Elasticsearch và đường dựng legacy. Probe Python/PyYAML tĩnh exit 0: trích đủ 9 Deployment target, xác nhận file Elasticsearch gồm PVC và tính lại quota 1425/2225/3225/3425m. Git HEAD/status/staged/unstaged stat đọc thành công. Không lặp lại 21 nhóm mock vì không sửa code và cả hai lượt trước đã chạy; PASS do Claude báo là evidence của Claude, không giả là Codex chạy lại hôm nay.

GitNexus index chậm 2 commit so với HEAD; index 6337b31. query/context định vị poll_prometheus_metrics → monitoring_loop; đã đối chiếu nguồn trực tiếp. detect_changes all báo 127 symbol/31 file/3 flow, không bảo đảm coverage file Bash và report untracked. Không có thay đổi symbol trong lượt review tài liệu này; không chạy impact/taint/PDG cho mã mới, không claim graph-backed review đầy đủ. Không lặp analyze đã timeout hai lần từ phiên migration hoặc xóa lock/index.

Web xác minh upstream version/default và Kubernetes semantics; không tải chart vào Helm cache, không cài dependency. Lấy template/Chart.lock upstream qua web bị cache miss, ghi UNKNOWN thay vì suy ra template đã render. Số đo live 10:46–10:48 thuộc lượt Claude; Codex không đo lại Docker/WSL hoặc chứng nhận trạng thái runtime hiện tại trong lượt review này. Chưa kiểm chứng hash ledger ngoài repo của Claude do báo cáo không cung cấp vị trí artifact có thể đọc; chỉ kiểm HEAD và dirty hiện có, không tuyên bố đã tái xác minh toàn bộ hash của Claude.

## Retest bản sửa Claude — 18/10/2026, 11:49 +07:00

Target: báo cáo Claude bản kết thúc lượt sửa 11:45:43 +07:00; SHA-256 100675008fc0413c4e0a79241d07c502bd5f1d62e660d9737d655493a008d147. HEAD xác minh lúc 11:49:14 vẫn 1f43ff1461c2199bc99e9962483956c3df0fa975, main; staged rỗng, các file migration/evidence vẫn dirty/untracked. Không claim đã đối chiếu hash ledger bên ngoài repo của Claude.

| Mục | Kết quả retest tài liệu | Phần còn mở |
| --- | --- | --- |
| CR-01 | Đạt cho sửa kế hoạch: đã bỏ delete -f, tách workload/PVC/Secret và yêu cầu inventory + phạm vi gỡ riêng | Rollback từng nhóm vẫn phải khóa resource ownership và context trước khi thực thi; chưa kiểm cleanup thật |
| CR-02 | Đạt phần đính chính: bỏ cận trên monitoring, nêu chart/default/job và xung đột heap rõ hơn | Chưa đạt sizing đầy đủ: chưa render/pin đủ chart và đo; vẫn mở trước chính nhóm chart đó, không chặn namespace |
| CR-03 | Đạt phần kế hoạch: tách profile nền/HPA, bổ sung restart/image Gaia | HPA/healer protocol và image identity/runtime còn cần kiểm ở bước tương ứng |
| CR-04 | Đạt phần diễn giải: không áp implementation cũ thành định nghĩa KPI | Mẫu số khóa tại scope/measurement, chưa giải quyết bằng tài liệu sizing |
| CR-05 | Đạt phần diễn giải: đã rút claim <60s và ghi cửa sổ 120s | Onset/detect và feasibility cần pilot độc lập |

Đã đọc B.2–B.5, D/E và thay đổi A-F được Claude chỉ rõ. Probe Python tĩnh kiểm 6 file của nhánh namespaces xác nhận đúng 3 Namespace, 3 ResourceQuota, 3 LimitRange; không Deployment/Pod/PVC/Secret/chart. Đã đọc setup-phase1.sh: nhánh namespaces gọi preflight rồi chỉ apply sáu file và get pods. Đây là xác minh scope source, không phải apply đã thành công.

Phép cộng zero-door dùng preset trong báo cáo: steady 896Mi, cùng Job 1152Mi, cùng hai surge 1088Mi; đúng về số học. Tuy nhiên **1088Mi là đỉnh nếu hai surge cùng tồn tại**, không chứng minh rollout chắc chắn kẹt: chỉ surge Nemesis là 1024Mi, chỉ surge worker là 960Mi; quota có thể ép hai rollout nối tiếp khi pod cũ được giải phóng. Cần render và thử rollout trước khi kết luận timeout. Còn 1152Mi khi đủ agent + Job vẫn là admission risk có căn cứ theo giả định resource hiện tại. Không đưa các số chưa render thành assurance rằng cài lần đầu chắc chắn qua.

Hai lưu ý không chặn bước namespace:
- Ví dụ rollback mới còn vài kubectl/helm thiếu --context/--kube-context (báo cáo :308–316). Khi chuẩn bị bước gỡ thực tế phải bổ sung context, tên/namespace/ownership; không copy các ví dụ này thành lệnh chạy nguyên văn. Không chạy rollback trong bước namespace này.
- Chart cần pin/render trước **mỗi** nhóm, gồm ingress ở bước 2, không chỉ monitoring/Kafka. Default/compatibility/resource admission phải theo đúng version được chọn.

### Kết luận thực thi giới hạn

**Không yêu cầu thêm một vòng sửa báo cáo chỉ để bắt đầu namespace.** Đủ cơ sở đề xuất giao Claude thực hiện đúng bước sau khi Hoàng gửi yêu cầu thực thi:
1. Ghi HEAD/dirty, kiểm Docker desktop-linux, k3d-zero-door và node Ready bằng truy vấn mới có timeout; mismatch/lỗi thì dừng, không tự chuyển context hoặc recreate.
2. Lưu inventory và số đo trước; đọc hiện trạng 3 namespace/quota/LimitRange, nếu có thay đổi ngoài dự kiến thì nêu diff trước khi apply.
3. Chạy duy nhất bash infrastructure/scripts/setup-phase1.sh --component namespaces với các file hiện tại; không tăng quota, không đổi WSL, không Helm hoặc nhánh all.
4. Lưu kết quả sau: labels Namespace, hard quota, LimitRange và số đo CPU/RAM. Quota là admission ceiling, không RAM được cấp ngay và không proof full lab tối ưu.
5. Báo cáo trong docs/evidence/ZER-35/namespace-bootstrap.md; nối handoff ngắn vào local-lab/NOW. Không commit/push hoặc đổi Linear.

Sau bước này, chuẩn bị pin/render và guard tài nguyên cho nhóm ingress/monitoring theo thứ tự; không tự triển khai bước 2+ trong cùng quyền bước namespace. Codex không chạy mutation trong lượt retest. Báo cáo Claude giữ nguyên; chỉ cập nhật review này, NOW và ghi chú local-lab.

## Review namespace bootstrap — 18/10/2026, 12:10–12:12 +07:00

**PASS cho bước namespace/quota/LimitRange; không có finding chặn trong phạm vi này.** Chưa hoàn tất ZER-35/ZER-6 hoặc chứng minh sizing full stack. Target: namespace-bootstrap.md, SHA-256 1b2f08a8598a8f5e92cc59fdacd61c54c92381ad5de1bdd118055ae0a1eb6615. HEAD đọc mới vẫn 1f43ff1461c2199bc99e9962483956c3df0fa975, main; staged rỗng. Linear ZER-35 được đọc qua linear_zero_door đúng URL zero-door; chưa thay field/comment/AC. AC còn mô tả tên script lịch sử; đối chiếu migration Bash, không dùng script cũ.

### Kiểm chứng độc lập

- Đọc toàn bộ evidence, nhánh namespaces trong setup-phase1.sh và helper common.sh: chỉ preflight, apply 6 file namespace/quota rồi liệt kê pod; không đi vào Helm hoặc nhóm khác.
- Truy vấn mới lúc 12:10:39: Docker desktop-linux, current Kubernetes k3d-zero-door; hai node Ready, v1.31.5+k3s1.
- Probe Python/PyYAML + kubectl get JSON có timeout exit 0: cả 3 Namespace Active/labels khớp nguồn; spec của 3 ResourceQuota và 3 LimitRange bằng chính xác YAML. Quota status.used đều 0; target-app limits.cpu vẫn 3.
- Creation timestamps 04:55:51–52Z khớp lượt apply 11:55 của Claude. Trong ba namespace không có Pod/PVC/Secret/Deployment/StatefulSet/DaemonSet/Job/CronJob/Service/NetworkPolicy tại lúc review. Toàn cluster chỉ 3 pod hệ thống, không PV/PVC và không event Warning.
- Hash 6 manifest cùng 2 file Bash hiện có khớp tiền tố/hậu tố hash Claude ghi. Không có quyền truy cập ledger phiên Claude nên không khẳng định đã tái xác minh mọi file dirty trước/sau lượt của Claude. Live read-back không chứng minh toàn bộ lịch sử thao tác.
- git diff --check exit 0; có cảnh báo chuyển CRLF của .gitignore, không lỗi whitespace. Không chạy lại apply, không dùng diff server dry-run, không cài chart hay đổi context.
- Số đo RAM/CPU 11:55–11:56 được giữ là evidence Claude; Codex không chạy lại benchmark hoặc xác nhận nguyên nhân dao động. Namespace/quota không phải bằng chứng full stack đã tối ưu.

### Bước tiếp theo cho Claude: chuẩn bị ingress, chưa cài

Không cần sửa lại namespace hoặc thêm vòng report để qua bước này. Chuẩn bị một phương án ingress có thể review, ghi vào docs/evidence/ZER-35/ingress-preflight.md; chỉ nối con trỏ ngắn vào local-lab/NOW sau khi có kết quả.

Có thông tin mới cần xử lý trước khi mặc định pin ingress-nginx: Kubernetes công bố dừng bảo trì ingress-nginx tháng 03/2026. Nguồn chính thức: [Ingress NGINX retirement](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) và [joint statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/). Vì hiện tại là tháng 10/2026, không coi chọn version là đã giải quyết vòng đời. Đây không làm bước namespace thất bại; cũng không tự cho phép đổi controller hoặc mở rộng thành migration.

Phạm vi chuẩn bị đề xuất:
1. Ghi HEAD/dirty và inventory context mới; đọc values, ingress manifest, port mapping K3d và yêu cầu log/IP nguồn/WAF hiện có. Nêu compatibility với K3s/Kubernetes 1.31 và ảnh hưởng đối với nghiên cứu, phân biệt yêu cầu thực với annotation legacy.
2. Đối chiếu phương án tái lập legacy bằng version cố định với một phương án còn được bảo trì phù hợp; dùng nguồn upstream. Trình bày chênh lệch file, hành vi và công sức để Hoàng có quyết định cụ thể trước khi đổi thiết kế.
3. Nếu cần tải chart phục vụ kiểm tra, giới hạn vào thư mục scratch hoặc cache riêng của phiên; không sửa Helm repo/cache dùng chung. Ghi version/digest và render cục bộ theo values repo; phân tích cả hook/init/sidecar, RBAC/cluster-scoped objects, resource hiệu dụng và namespace thực tế. ingress hiện nhắm kube-system nên không áp quota monitoring thay cho namespace đó. Render không chứng minh API admission/runtime.
4. Chuẩn bị lệnh Bash cài/kiểm tra với --kube-context k3d-zero-door và namespace/release tường minh, đo trước/sau, tiêu chí dừng và rollback theo ownership/resource allowlist. Chưa chạy các lệnh này.

Không sửa source/config vận hành, apply/install/upgrade, thêm CRD, kéo image/build, tăng quota, đổi cluster/WSL, gọi model/attack hoặc cập nhật Linear/Git publication trong bước chuẩn bị này. Chỉ thực hiện khi Hoàng chuyển yêu cầu phạm vi này cho Claude; không tự gửi sang phiên khác.


## Review gói Traefik — 18/10/2026, 14:52 +07:00 (Codex)

**NOT READY — sửa TFM-01–03 trước triển khai.** Review hai patch chưa áp, không phải xác nhận migration chạy thật hay nghiệm thu toàn bộ restore. Hoàng đã duyệt patch agent cùng gói và triển khai sau khi Codex review đạt; không hỏi lại lựa chọn này.

### Target và provenance

- main, HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975; staged rỗng. Baseline là **working tree dirty**, gồm Bash migration/restore của Claude; không dùng HEAD sạch thay đầu vào. Review delta hai patch trên baseline đó và caller/consumer liên quan.
- Infra SHA-256 d631abbc65414f8216fd6379e7d85b84438547ec165a7c47641e8cccddc1d5a2; agents SHA-256 b9e83cd9a09f3eef1814ab380ccf0c404a535eb5002fb657ed96078697ca99a0. Khớp báo cáo; git apply --check --whitespace=error-all đạt trên working tree thật.
- Đã đọc live ZER-35 qua linear_zero_door đúng workspace zero-door (In Progress tại lúc đọc); không sửa fields/comment.
- Phạm vi ghi Codex: review này, con trỏ NOW/local-lab và bản sao/probe riêng scratch/codex-traefik-review. Không sửa patch, source/config thật hoặc lab.

### TFM-01 — HIGH: nhãn backend bị đổi thành exported_service

**Anchor:** docs/evidence/ZER-35/traefik-migration-infra.patch:117–119 (values/serviceMonitor). Consumers: agents.patch:14,25,38–39; infra.patch:454,466.

Chart render ServiceMonitor **không có honorLabels**. Mặc định Prometheus honor_labels=false. Operator gắn target label service=traefik-metrics, xung đột với nhãn backend service=target-app-frontend-80@kubernetes của Traefik; nhãn exporter thành exported_service. Mọi selector mới tìm backend trong service nên trả rỗng: Gaia bỏ qua error/latency, Nemesis thiếu HTTP context, hai rule không phát hiện; check ingress cũng FAIL dù scrape UP.

Bằng chứng độc lập:
- Render lại chart 42.0.0 từ tgz SHA a6ede324662ddcca0160a5ce639b7b5b9dd40a20a475e1101e9f95b5e5d83dd5 với values đã patch: endpoint chỉ targetPort/path/interval, không honorLabels/relabel xử lý xung đột.
- Đọc Prometheus CR hiện hành: overrideHonorLabels=false. Config Operator đang sinh cho ServiceMonitor hiện có: honor_labels=false, relabel __meta_kubernetes_service_name → service. Traefik chưa cài; không tự nhận đã thấy series Traefik thật.
- Quy tắc xung đột: [Prometheus scrape_config](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config). [Traefik service metrics](https://doc.traefik.io/traefik/reference/install-configuration/observability/metrics/#service-metrics) có nhãn service.

**Sửa:** cách nhỏ nhất với query hiện tại là metrics.prometheus.serviceMonitor.honorLabels: true; render xác nhận endpoint honorLabels:true và kiểm config scrape thực sau cài. Nếu đổi tên nhãn backend riêng phải sửa đồng bộ rule/query/probe. Giữ ngưỡng/cửa sổ/decision logic. Thêm regression cho label contract của chart render; mock argv Helm, query parse rỗng và label_replace trên nhãn giả không bắt được lỗi này.

### TFM-02 — MEDIUM: thiếu kiểm tích hợp sau rollout agent mới

**Anchor:** docs/evidence/ZER-35/traefik-migration.md:221–225.

Kế hoạch chạy ingress/all trước rebuild Gaia/Nemesis; sau rebuild chỉ healthz. Gaia healthz chỉ khởi tạo Kafka/ES và in endpoint Prometheus (agent-orchestrator/gaia/main.py:382–390), không thực hiện query. Image đúng/healthz UP vẫn có thể thiếu dữ liệu hoặc query sai service. Bộ 27 test không chạy Python query consumer. Chưa phân loại exit khác 0 đã biết của check all (hai frontend /metrics 404) với regression mới: batch fail-fast có thể dừng trước rebuild; bỏ qua toàn bộ exit lỗi lại che lỗi mới.

**Sửa:** verification cuối sau cả hai rollout: giữ image identity/healthz, kiểm label thật, counter thay đổi qua request lành tính giữa các scrape, histogram và consumer query theo cửa sổ 1m/2m. Case offline cho frontend, service có dấu gạch nối, namespace khác và dữ liệu 5xx/latency mẫu; không gọi LLM/attack/heal. Không bắt healthy traffic có sẵn series 5xx: phân biệt chưa có 5xx với thiếu toàn bộ backend metric. Giữ nguyên exit/failure của check all và chỉ phân loại đúng hai target lỗi đã biết; failure mới vẫn chặn. Kiểm nghiệp vụ/telemetry cuối sau build để phát hiện restart/regression; không dùng kết quả trước build làm bằng chứng cuối.

### TFM-03 — MEDIUM: rollback chưa giải phóng port 80

**Anchor:** docs/evidence/ZER-35/traefik-migration.md:240–241.

Rollback đề nghị apply lại frontend-external LoadBalancer rồi khẳng định :8080 trở về frontend, trong khi Traefik vẫn giữ hostPort 80 và gỡ release còn cần quyền riêng. Đây là xung đột svclb đối xứng với preflight mục 2: frontend svclb mới không bind port; revert manifest chưa phục hồi đường host. Nếu Ingress đã về class nginx, Traefik cũng không phục vụ route tạm đó.

**Sửa:** ghi thứ tự giải phóng port Traefik bằng hành động có quyền, kiểm owner/port, rồi phục hồi Service/Ingress và probe :8080. Chưa có quyền giải phóng thì rollback chưa hoàn tất; không khẳng định đã phục hồi. Không chạy rollback/uninstall trong review, không thêm tự động xóa release/PVC/Secret/CRD.

### Kiểm chứng và giới hạn

- Áp tuần tự hai patch chỉ vào bản sao scratch; không áp checkout thật. Bash syntax scripts PASS, AST parse cả hai Python PASS; bash tests/shell/run.sh trên cây patch **27/27 PASS**, mọi CLI lab được mock.
- Render độc lập exit 0: 9 object, không CRD/hook; middleware file-provider, Ingress class/prefix, bucket/tài nguyên khớp mô tả. Render không chứng minh runtime hoặc IP nguồn.
- Truy vấn mới chỉ đọc: Docker desktop-linux, chưa có Deployment Traefik, frontend-external vẫn LoadBalancer. Không cài/upgrade/restart/apply/server dry-run, không build/import, không gọi attack/heal/model.
- Đọc toàn bộ hai diff và source/helper/manifest/caller liên quan. Agent patch giữ ngưỡng/cửa sổ/publish; không thấy đổi decision logic. SQLi/block-IP/flood-bypass chưa được sửa qua migration.
- GitNexus index 6337b31, chậm HEAD hai commit, không chứa patch chưa áp/Bash mới. Dùng query/context/impact lần monitoring_loop → poll_prometheus_metrics → publish_alert và generate_attack_plan_from_llm → get_system_summary, rồi kiểm nguồn thật. Không dùng nhãn LOW của graph làm verdict. Explain báo thiếu taint layer; không có PDG/taint cho cây patch, không nhận review graph đầy đủ. Không lặp refresh đã treo trước đây để thay thế đọc delta chưa áp.
- Chưa retest toàn bộ restore, resource guard hoặc runtime migration. Cluster-wide Secret watch của chart đã được ghi nhận trong gói; review không đọc/in giá trị Secret.

### Bàn giao một lượt

Claude sửa TFM-01–03 trong cùng gói; cập nhật patch/hash, regression và kế hoạch kiểm cuối/rollback; chạy offline/render/apply-check trên bản sao rồi trả Codex retest. Giữ source thật và cluster đến review đạt. Không hỏi lại Hoàng về patch agent đã duyệt. Flood/SQLi/block-IP đã có phạm vi trong delivery, đối chiếu issue hiện hữu khi tới lượt, không tạo trùng từ ghi chú migration. Chưa commit/push/merge hay cập nhật Linear.

## Retest gói Traefik — 18/10/2026, 15:54 +07:00 (Codex)

**NOT READY — sửa ba điểm TFM-04–06 trong cùng gói, kèm lỗi tương thích test TFM-07.** Đây là retest hai patch chưa áp trên working tree dirty, không phải nghiệm thu runtime migration hay toàn bộ ZER-35.

### Target, scope và kết quả đã đạt

- HEAD vẫn 1f43ff1461c2199bc99e9962483956c3df0fa975, main; review delta hai patch trên baseline dirty hiện có. Linear ZER-35 đọc qua linear_zero_door: đúng workspace zero-door, In Progress tại lúc đọc; không cập nhật Linear.
- Infra SHA-256 bd6624a77a015a1d4c61f27b89539e899fbe8ef2671f000b43e0e575f934a95c. Agents SHA-256 b9e83cd9a09f3eef1814ab380ccf0c404a535eb5002fb657ed96078697ca99a0. Khớp bàn giao. Patch agent không đổi.
- Áp hai patch chỉ vào scratch/codex-traefik-retest/fixture, không áp source thật. Phạm vi ghi: scratch này, bổ sung review hiện hữu và con trỏ NOW/local-lab.
- Bash syntax đạt. Môi trường Git Bash sạch (bỏ MSYS_NO_PATHCONV/MSYS2_ARG_CONV_EXCL và override Helm): **run.sh 29/29 PASS**. **test-local-restore.sh exit 0**, chart SHA khớp, render ServiceMonitor honorLabels=true, rollback ClusterIP đúng; promtool SUCCESS với ba nhóm dữ liệu mẫu.
- **TFM-01: đạt ở mức gói/offline.** Sửa nhãn đúng, cần kiểm nhãn/config hiệu lực sau triển khai. **TFM-02: đạt phần thứ tự kiểm cuối, exit 0/3/1 và case PromQL, nhưng probe còn lỗi dưới đây. TFM-03: đạt thứ tự giải phóng port, còn thiếu context ở lệnh rollback mẫu.**
- Không chạy cài/upgrade/apply/server dry-run/build/rollout, attack/heal/LLM. Không commit/push/merge.

### TFM-04 — MEDIUM: probe có thể FAIL trên ingress mới và hoàn toàn khỏe

**Anchor:** docs/evidence/ZER-35/traefik-migration-infra.patch:417–419,434–469,483–520 (verify-local-lab.sh); deployment gate ở traefik-migration.md:270.

Check đọc counter trước, gửi toàn bộ request thử, rồi chỉ chờ/query. Không có request bổ sung sau khi đã xác nhận một lần scrape. Với ingress mới, nếu burst request kết thúc trước lần scrape đầu, counter/histogram lần đầu được ghi đã mang toàn bộ số request. Các scrape tiếp theo không tăng. Nhánh grew vẫn nhận absent → số dương là thành công, nhưng rate thực là 0 và histogram_quantile là NaN; consumer gate không thể PASS dù router, scrape và query đều đúng. Ngay cả hệ đã chạy, chờ ES/pod lâu cũng có thể đẩy burst ra ngoài cửa sổ Gaia 1m. Bước chẩn đoán trước build có thể dừng migration vì chính probe.

**Đã tái hiện bằng promtool 3.15.0, dùng query trích từ source đã patch:** series frontend có counter và bucket dương nhưng giữ nguyên từ lần scrape đầu, phù hợp burst trước scrape. Tại 30s, 1m và 2m: Nemesis http_rps=0; Gaia P99={service="frontend"} NaN. Output khác kỳ vọng dương/hữu hạn. Bộ test chính không bắt được vì dùng counter tăng liên tục 15s trong 5 phút.

**Sửa:** tạo traffic lành hữu hạn qua ít nhất hai scrape đã xác nhận: lấy mẫu đầu, gửi request bổ sung sau mẫu đó, đợi mẫu mới rồi kiểm rate/histogram trong cùng cửa sổ. Nếu chờ ES/pod làm mất cửa sổ thì lấy lại mẫu/request trước consumer gate. Có giới hạn request/deadline, không tạo flood, không nới query/ngưỡng cho qua test. Thêm case cold-start/idle và scrape timing, giữ case không traffic thì không tự nhận consumer PASS.

Repro nằm scratch/codex-traefik-retest/cold-start.sh và cold-start.test.yaml; đây là dữ liệu giả lập, không phải số đo lab.

### TFM-05 — MEDIUM: không đọc được log Gaia vẫn bị báo PASS

**Anchor:** docs/evidence/ZER-35/traefik-migration-infra.patch:385–391 (verify-local-lab.sh:186–192 trong cây patch).

Pipeline logs | grep | tail || true bỏ luôn lỗi kubectl logs. Khi API/permission/container trả lỗi, gaia_errors rỗng và probe in "Gaia log has no Prometheus query error" như đã đọc log thành công. Đây chính là bằng chứng consumer sau rebuild mới bổ sung cho TFM-02; lỗi lấy bằng chứng không được thành PASS.

**Repro độc lập:** chạy nguyên block agents trong bản sao, mock healthz/rollout thành công và kubectl logs trả exit 7 + Forbidden. Kết quả thực: in lỗi Forbidden rồi PASS Gaia log, failures=0, exit 0. File scratch/codex-traefik-retest/log-failure.sh. Bộ mock chính chỉ kiểm telemetry, không có case lỗi đọc log.

**Sửa:** lấy log và kiểm exit riêng; lỗi lấy log phải FAIL (hoặc UNKNOWN nhưng gate không đạt), chỉ sau khi đọc thành công mới lọc chuỗi lỗi. Phân biệt grep không tìm thấy với lệnh lấy log thất bại. Thêm regression ba case: đọc log khỏe, log có lỗi query, lấy log lỗi.

### TFM-06 — MEDIUM: lệnh rollback R1 không khóa Kubernetes context

**Anchor:** docs/evidence/ZER-35/traefik-migration.md:291.

Lệnh copy/paste R1 là helm upgrade ... -n kube-system --set service.spec.type=ClusterIP --wait, thiếu --kube-context k3d-zero-door. R7 có flag này; helper zd_helm cũng luôn thêm flag. Các script được phép giữ current-context của người dùng, nên nó có thể đang trỏ project khác. R1 khi đó không giải phóng port của lab, hoặc upgrade nhầm release traefik ở cluster khác nếu có cùng tên. Câu tổng quát "mọi lệnh dùng context" không làm lệnh mẫu tự có flag.

**Sửa:** dùng lệnh tự đủ --kube-context k3d-zero-door, hoặc wrapper đã source và kiểm guard rõ ràng. Các truy vấn port-owner/snapshot trong rollback cũng cần context rõ ràng. Không đổi current-context của người dùng. Đối chiếu lệnh rollback mẫu và kiểm argv/context, không cần chạy rollback thật.

### TFM-07 — LOW: test nhãn mới phụ thuộc chuyển path ngầm của MSYS

**Anchor:** docs/evidence/ZER-35/traefik-migration-infra.patch:769–772 (tests/shell/run.sh:386).

Test mới đưa đường dẫn /r/... thẳng cho Python native, khác helper zd_path đã xử lý đường dẫn host. Re-run với MSYS_NO_PATHCONV=1, MSYS2_ARG_CONV_EXCL=* (chế độ common.sh dùng cho native CLI): đến test cuối, Python FileNotFoundError ở /r/.../traefik-values.yaml; suite exit 1. Bỏ hai biến, cùng cây đó 29/29 PASS. Đây là lỗi tương thích của test, không phải lỗi honorLabels và không phủ nhận kết quả môi trường sạch.

**Sửa nhỏ cùng lượt:** chuyển đường dẫn đầu vào Python sang Windows path khi chạy Git Bash; kiểm suite ở cả môi trường sạch và môi trường tắt path conversion. Không sửa giá trị honorLabels để né test.

### Giới hạn và bàn giao

- GitNexus vẫn index 6337b31, chậm HEAD hai commit; context poll_prometheus_metrics xác nhận đường monitoring_loop → query_prometheus/publish_alert của mã cũ. Không có graph/PDG cho Bash mới và delta chưa áp; kiểm trực tiếp source/diff/test, không tuyên bố graph-backed review đầy đủ. Không lặp refresh đã treo từ review trước.
- Các kiểm runtime migration, IP nguồn, consumer bên trong image mới và resource guard còn chờ triển khai. Read-only snapshot không là runtime proof cho Traefik.
- Claude sửa TFM-04–07 cùng một lượt, tái tạo patch/hash và chạy regression trên cây round-trip; giữ quyết định Traefik/agent patch đã duyệt, không hỏi lại. Chưa triển khai cho tới Codex retest đạt. Không cần mở rộng phạm vi sang SQLi/healing hay tạo issue mới.

## Retest gói Traefik — 18/10/2026, 16:38 +07:00 (Codex)

**READY cho triển khai lab trong phạm vi đã duyệt, theo mục 9 của traefik-migration.md. Không có finding mới chặn triển khai.** TFM-01–07 đã được xử lý ở mức gói trước triển khai. Kết luận này thay verdict NOT READY của hai lần review trước cho đúng hai hash dưới đây; chưa xác nhận migration chạy thật và chưa đóng ZER-35.

### Target và phạm vi

- main, HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975, staged rỗng; đầu vào là working tree dirty hiện hữu, không phải checkout HEAD sạch. Giữ mọi thay đổi ngoài review, gồm WORKFLOW.md hiện cũng dirty.
- Infra SHA-256 **03ab4a6c60f135acc6dc4f6b2e537a72dfd5b5e83714d3894fd775b9708ff53f**.
- Agents SHA-256 **b9e83cd9a09f3eef1814ab380ccf0c404a535eb5002fb657ed96078697ca99a0**, không đổi từ review đầu.
- Cả hai git apply --check --whitespace=error-all đạt trên working tree thật. Chỉ áp patch vào scratch/codex-traefik-retest-r3/fixture để kiểm, không áp source thật.
- Đọc Linear qua linear_zero_door: ZER-35 đúng workspace zero-door, In Progress tại lúc đọc. Không cập nhật fields/comment hay trạng thái.

### Đối chiếu finding

| Finding | Kết quả retest |
| --- | --- |
| TFM-01 — backend service label | Values và chart render giữ honorLabels=true. Test synthetic exported_service và dữ liệu frontend/redis-cart/namespace khác đạt; nhãn thực chờ deploy |
| TFM-02 — kiểm cuối và phân loại lỗi | Kế hoạch giữ kiểm cuối sau cả hai build, có image identity và hậu kiểm restart/tài nguyên. Exit 3 chỉ dành cho frontend 404 đã biết, lỗi mới exit 1; mock đạt |
| TFM-03 — thứ tự rollback | Chuyển Traefik sang ClusterIP trước, kiểm svclb/port rồi phục hồi frontend LoadBalancer; render rollback giữ release và không CRD. Chưa chạy rollback thật |
| TFM-04 — traffic qua các scrape | Consumer check chạy sau mọi chờ ES/pod. Mỗi vòng 3 request rồi chờ cả hai counter tăng; có ít nhất hai mẫu đã xác nhận trước query, tối đa 4 vòng/12 request. Mock cold-start đạt với 6 request đúng thứ tự; idle, stale query và HTTP 502 đều FAIL. Promtool xác nhận burst trước scrape không đủ, hai scrape có tăng counter thì gate đạt; sau khi cửa sổ Gaia trôi, gate không đạt |
| TFM-05 — lỗi đọc log | Lấy log và kiểm exit riêng trước grep. Các ca đọc log sạch, log có lỗi query và kubectl logs lỗi đều cho đúng PASS/FAIL; log không đọc được không còn PASS |
| TFM-06 — rollback context | R1 dùng setup-phase1.sh --component ingress --ingress-cluster-ip, qua Docker guard và wrapper Helm khóa k3d-zero-door. Chỉ upgrade, không install/uninstall. Mock kiểm argv, context và Helm home; lệnh mẫu còn lại ghi context rõ |
| TFM-07 — Python path Git Bash | Đổi path qua cygpath -m. Toàn suite đạt ở cả môi trường sạch và tắt MSYS path conversion |

Không thay ngưỡng/cửa sổ/query agent thêm trong lượt sửa này; patch agent giữ nguyên hash. Chưa nhận các hạn chế SQLi, nguồn IP/BLOCK_IP hoặc flood bypass là đã được migration giải quyết.

### Kiểm chứng độc lập và giới hạn

- Bash syntax mọi script infrastructure/scripts và tests/shell đạt.
- **run.sh: 32/32 PASS môi trường sạch; 32/32 PASS với MSYS_NO_PATHCONV=1, MSYS2_ARG_CONV_EXCL=*.** Lưu output raw ở scratch/codex-traefik-retest-r3/mock-clean.log và mock-nopath.log.
- **test-local-restore.sh: exit 0**, 15 PASS, promtool SUCCESS cho năm nhóm. Chart SHA khớp; honorLabels, middleware, buckets, IngressClass, CRD provider và render rollback đúng. Raw output ở scratch/codex-traefik-retest-r3/real-tests.log. Tất cả chạy trên cây tạo từ chính hai patch; Helm pull/render và promtool offline không đổi cluster.
- 14 source input gốc của review trước vẫn giữ nguyên SHA. Đọc live chỉ thấy Docker desktop-linux, chưa có Deployment Traefik, frontend-external vẫn LoadBalancer. Không apply/dry-run server/install/upgrade/build/rollout, không attack/heal/reset/model.
- GitNexus index 6337b31 vẫn chậm HEAD hai commit, không có cây Bash/patch mới. Context poll_prometheus_metrics xác nhận các caller/consumer lịch sử; kết luận delta dựa source/test trực tiếp. Không nhận graph/PDG coverage đầy đủ, không lặp refresh đã treo ở các lượt trước.
- Chưa kiểm toàn bộ restore baseline độc lập, IP/log/metric thực qua Traefik, image mới, mức RAM/CPU sau migration hoặc khả năng rollback runtime. Đây là các phép kiểm cần làm khi triển khai, không phải finding mới của gói.

### Bàn giao thực thi

Claude là bên triển khai tiếp theo, **thực hiện trọn mục 9 trong quyền Hoàng đã duyệt**, không cần hỏi lại Traefik hoặc patch agent. Trước áp phải đối chiếu HEAD/dirty, hai hash và preflight/resource guard; nếu đầu vào đổi thì kiểm lại delta ảnh hưởng. Giữ bằng chứng cuối sau build, phân loại rõ exit 0/3/1, restart và tài nguyên; không dùng probe trước build làm bằng chứng cuối. Dừng/báo khi gate không đạt; không tự rollback hay xóa dữ liệu.

Sau triển khai trả output/evidence cho Codex review runtime. ZER-35 vẫn chưa Done; việc commit/push/merge, cập nhật Linear hoặc nghiệm thu không được tự cấp quyền bởi verdict này.

## Review runtime Traefik — 18/10/2026, 18:03–18:07 +07:00 (Codex)

**PASS phần migration Traefik; chưa chấp nhận toàn bộ ZER-35.** Kết quả bước 7/8 của Claude lúc 17:24–17:27 khớp raw output/snapshot. Quan sát mới lúc review phải được giữ riêng, không sửa ngược mốc lịch sử hoặc quy kết lỗi mới cho migration khi chưa có nguyên nhân.

### Phạm vi và kiểm chứng độc lập

- main, HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975; staged rỗng. Giữ toàn bộ dirty/untracked hiện hữu. Hai patch còn đúng SHA 03ab4a6c60f135acc6dc4f6b2e537a72dfd5b5e83714d3894fd775b9708ff53f và b9e83cd9a09f3eef1814ab380ccf0c404a535eb5002fb657ed96078697ca99a0. Reverse apply-check đạt; cả 16 file đích khớp từng byte với fixture đã retest 16:38. Không chạy lặp offline suite vì không có delta mã mới.
- Linear live ZER-35 vẫn In Progress, đúng workspace zero-door. AC khôi phục đường triển khai, API, bảo toàn dữ liệu và profile được đối chiếu cùng AC tích hợp của ZER-6 trong handoff. Không cập nhật Linear.
- Đọc trực tiếp: Docker desktop-linux; hai node Ready; toàn bộ container Ready ở snapshot cuối. Helm traefik revision 1 deployed/chart 42.0.0/app v3.7.14. Frontend-external là ClusterIP, Traefik là LoadBalancer, svclb-traefik 2/2; ba PVC vẫn Bound.
- Traefik image digest khớp báo cáo. SHA main.py đọc bằng Python trong pod khớp source: Gaia 79db4d1a5f62d2477a0c5c06779ca9a66fc81f57022f38e065c7f32cf43a2b02; Nemesis 2f8a92e615d3f2c9d4d2dc3ded7f2f5501090f930929b46ccc9f9df3aa326221. Lệnh sha256sum đầu tiên không có trong image; kiểm bằng Python sau đó thành công, không coi lỗi lệnh đầu là PASS.
- Live Prometheus: 19 target, 17 up; chỉ hai frontend target down vì 404. Traefik metrics up, ServiceMonitor honorLabels=true; nhãn service có target-app-frontend-80@kubernetes cùng hai backend agent, không bị thay thành tên Service metrics. Ba GET healthz đều có kafka_connected=true; Gaia ES true; log Gaia 20 phút gần nhất không có hai mẫu lỗi query được kiểm. Hephaestus heal/history total=0; health Nemesis không chứng minh LLM hoạt động.
- Log Traefik còn sentinel của bước 7: host ClientHost=10.42.1.1; request pod ClientHost=10.42.1.35; đều route tới target-app-frontend-80@kubernetes. SNAT phía host là giới hạn đã biết; chưa chứng minh BLOCK_IP.
- Raw step7-all.out khớp output bền vững: đúng hai FAIL (known), không thêm FAIL. Giao dịch mẫu, Kafka correlation, ES sentinel và NetworkPolicy được đối chiếu từ kết quả Claude; Codex không tạo lại pod/topic/giao dịch hoặc chạy tải. Bằng chứng purchase hiện qua port-forward, ingress được kiểm riêng bằng GET; không gọi là đã kiểm checkout xuyên ingress.
- Tài nguyên tại review: Windows available khoảng 1954–1967 MiB; WSL MemAvailable 2506512 KiB, PSI memory avg60=0; Traefik khoảng 39Mi. Đây là snapshot, không chứng minh ổn định dài hạn hoặc KPI nghiên cứu. GitNexus vẫn không bao phủ Bash mới/working tree; dùng source/runtime trực tiếp, không nhận graph/PDG coverage đầy đủ.

### Hai lỗi còn phải xử lý trong gói lab

| ID | Mức | Vị trí / bằng chứng | Yêu cầu sửa và nghiệm thu |
| --- | --- | --- | --- |
| LAB-01 | Medium | infrastructure/helm-values/kafka-values.yaml:97–111; live kafka-controller-0/jmx-exporter có restartCount=3, lastState=OOMKilled lúc 16:53:49 +07:00. Process args đang là java -XX:MaxRAMPercentage=100 với memory limit 256Mi; heap chưa chừa biên cho native memory. Không tăng thêm restart trong migration hoặc tại review không xóa được bằng chứng OOM có thật | Kiểm chart/image để chọn cấu hình heap/native budget có hiệu lực; render argv/env thật và tính quota cả rollout trước upgrade. Ưu tiên sửa trong trần hiện tại, không tăng quota/WSL hay đổi image ngầm. Lấy JMX up và Kafka round-trip sau rollout, đo đủ một khoảng quan sát có lý do theo nhịp OOM cũ; không dùng một scrape up làm chứng minh ổn định. Nguyên nhân OOM cần xác minh, không coi MaxRAMPercentage tự nó là kết luận đầy đủ |
| LAB-02 | Medium | infrastructure/manifests/target-app-monitor.yaml:9–18 chọn cả frontend và frontend-external nhưng image không phục vụ /metrics; live có đúng hai target 404. verify-local-lab.sh:136–146 phân loại đúng lỗi đã biết, nhưng exit 3 vẫn là kết quả còn lỗi | Ngừng cấu hình scrape endpoint không tồn tại, giữ metric HTTP từ Traefik và CPU từ cAdvisor; xử lý riêng object ServiceMonitor cũ bằng danh sách thao tác cụ thể, không delete -f hoặc gỡ dữ liệu. Nếu cần thao tác ngoài quyền hiện tại thì chuẩn bị patch/kế hoạch thu hồi đúng một object để duyệt. Kiểm không còn target 404, metric consumer vẫn có dữ liệu và all đạt exit 0; không chỉ đổi filter/expected để che lỗi |

### Quan sát mới cần làm rõ trước chấp nhận baseline

**OBS-01:** paymentservice-68b7b85888-r9xsk tăng restart 1 → 2 lúc **18:01:34 +07:00**, sau cửa sổ triển khai kết thúc 17:27. Kubelet event lúc 18:01:29 ghi container failed liveness probe; lastState Error/137, **không phải OOMKilled**. Cùng khoảng 18:01 nhiều probe của currencyservice/Prometheus/Grafana/metrics-server/node-exporter timeout; Nemesis mới có timeout lúc 18:04 nhưng chưa restart. Nguyên nhân chung chưa xác định: không quy cho Traefik, không kết luận thiếu RAM hoặc chỉ sửa timeout để giấu sự cố. Claude đối chiếu host sleep/resume, tải/pressure và lịch thao tác rồi giữ một baseline quan sát sau sửa. Nếu cần thay probe, phải nêu căn cứ và không làm lệch phép đo MTTD/MTTR sau này. Snapshot cuối tất cả Ready không phủ nhận sự kiện này.

### Bàn giao một lượt xử lý cuối

Claude xử lý gom LAB-01/02 và chẩn đoán OBS-01 trong file/action scope hiện hành; ghi chính xác phần nào cần mở rộng quyền. Không hỏi lại việc chọn Traefik hoặc patch agent. Cập nhật lab-restoration.md để phần kết luận không còn nói ingress chờ chọn/chưa triển khai, bổ sung OOM và giới hạn host; giữ nguyên mốc bằng chứng cũ và dẫn mục 15 migration. Runbook phải mô tả đúng cấu hình cuối. Đầu ra: diff/config cuối + render/quota + test liên quan + verify cuối sau mọi rollout + restart/resource comparison. Không cần dựng lại cluster, chạy lại toàn bộ hydration hoặc thử attack/LLM.

Codex chỉ ghi review và con trỏ NOW/local-lab; truy vấn runtime chỉ đọc, không apply/build/rollout/rollback, không commit/push/merge, không thay Linear. Raw kiểm độc lập ở scratch/codex-runtime-review/; các kết quả thiết yếu đã trích ở đây. Review này tiếp nhận migration; **chưa là review mã toàn bộ baseline Bash/restore hoặc chấp nhận ZER-35**. Sau gói sửa cuối, review delta và phần baseline còn thiếu trước Git publication/merge và Hoàng chấp nhận.

## Codex thực hiện gói sửa cuối — 18/10/2026, chốt 18:52 +07:00

Hoàng giao Codex sửa trực tiếp, nên mục này là **tự kiểm của người thực hiện**, không phải review độc lập. [Kết quả chính, mục 12](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md) thay trạng thái kỹ thuật còn mở ở review runtime trước: LAB-01 giới hạn heap JMX có hiệu lực; LAB-02 bỏ scrape frontend sai và ngoại lệ exit 3; OBS-01 cập nhật profile probe/CPU trong quota; thêm LAB-03 worker Kafka để sửa event loop Nemesis, có test trước sửa FAIL/sau sửa PASS. Recreate guard/CI cũng đã chỉnh trong scope.

- Kiểm cuối sau Nemesis rollout: exit 0; 34 nhóm mock PASS, 3 test consumer PASS, real Helm render/PromQL/quota PASS, AST/YAML/whitespace PASS.
- 31 mẫu 18:36:31–18:51:48: 17/17 target up, container Ready, không restart/thay pod ngoài dự kiến hoặc Warning mới; JMX peak 141Mi. PVC/UID, quota và Secret ứng dụng được đối chiếu; chỉ thêm Helm release history v3.
- HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975; staged rỗng; toàn bộ mã/evidence còn local. Giữ dirty work ngoài allowlist. SHA Nemesis live/source 2e087b3c0ce4bae4700a2e8fd9d31ba989c66fda700281b6f9c5bb462577443e. Hai patch Traefik cũ không mô tả toàn bộ delta cuối.
- GitNexus refresh timeout 45s/exit 124; không nhận graph/PDG current. Không dùng cửa sổ ngắn này làm KPI nghiên cứu, LLM hoặc attack/healing proof.

**Bàn giao:** review độc lập diff/source/test cuối theo mục 12 và ledger; sau đó mới publication/merge và Hoàng chấp nhận theo workflow. Không triển khai lại patch lịch sử. Codex chưa commit/push/merge, đổi Linear hoặc chạy cloud/LLM/attack.

## Claude review độc lập gói Codex cuối — 18/10/2026, 19:55–20:15 +07:00 (Claude)

**Kết luận: PASS. Không có finding chặn AC.** Gói này **đủ điều kiện chuẩn bị commit/merge trong quyền Hoàng cấp**. Đây không phải trạng thái Done: merge và việc Hoàng chấp nhận vẫn là hai cổng riêng. Có 4 cải tiến không chặn (CL-01 đến CL-04) và 1 quan sát (OBS-02), gom ở cuối mục để Codex xử lý trong một lượt nếu Hoàng muốn làm trước khi merge.

Ở lượt này Claude chỉ review:
- Không sửa source hay config.
- Không apply, upgrade, build, rollout hay delete.
- Không chạy `verify-local-lab.sh`.
- Không đọc dữ liệu Secret.
- Không commit, push, merge, và không đổi Linear.

### Bản được review

- `main`, HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`; staged rỗng; 72 đường dẫn dirty/untracked. Snapshot ở `scratch/claude-final-review/git-snapshot.txt`.
- **Ledger** `scratch/zer35-final/final-file-ledger.json`:
  - 23/24 mục khớp SHA-256 với source hiện tại; `target-app-monitor.yaml` đúng là không còn.
  - Mục duy nhất lệch là `docs/delivery/NOW.md`: con trỏ phiên được sửa sau khi chốt ledger. Đây là tài liệu, không thuộc mã được review.
  - Nemesis `2e087b3c…577443e`. CI `fab188d6…08a3ef`. `kafka-values.yaml` `f25cf230…c58f`. `target-app.yaml` `dbcd45e1…3bdb`. `target-app-addons.yaml` `b5efcf6c…1474`.
- **Baseline để lấy delta:**
  - Các file của gói Traefik: dùng bản round-trip đã triển khai lúc 17:16. Bản này trùng từng byte với `hash-start.json` của Codex, đúng như cây fixture r3.
  - `deploy.sh`, `target-app-addons.yaml`, `target-app-monitor.yaml`: dùng HEAD, vì sạch lúc Codex bắt đầu.
  - `ci.yml` và hai runbook đã dirty từ trước, nên tôi đọc toàn bộ diff so với HEAD.
  - Delta: 19 file, +475/−139 dòng, chưa tính file `target-app-monitor.yaml` đã xóa (`scratch/claude-final-review/delta.diff`). Có đọc cả ba file untracked mới.
- **Linear chưa đọc live.** Connector Linear của phiên Claude trả "Could not find referenced Issue" cho ZER-35, vì nó trỏ tới workspace khác. Tôi không sửa OAuth hay workspace, và đối chiếu với snapshot AC trong handoff (ZER-35 AC-01, ZER-6 AC-03).
- **GitNexus:** không dùng. Index dừng ở `6337b31`, lần refresh trước của Codex timeout. Review dựa trực tiếp trên source, test và runtime; không nhận coverage graph/PDG.

### Lệnh tự chạy và kết quả

| Lệnh / phép kiểm | Kết quả |
| --- | --- |
| `bash -n` mọi script `infrastructure/scripts`, `lib/common.sh`, `tests/shell`, `rebuild-nemesis.sh`, `start-demo.sh` | OK |
| Python AST: `nemesis/main.py`, `render.py`, `test_nemesis_consumer.py` | OK |
| `python tests/test_nemesis_consumer.py` (bản hiện tại) | exit 0, 3/3 OK |
| Cùng test, `NEMESIS_TEST_SOURCE` trỏ vào `main.py` trước sửa | exit 1: 2 failure, 1 error. Event loop bị chặn 0,594 s (ngưỡng 0,2 s) |
| 4 mutant tự tạo của bản sửa (`nemesis_mutations.py`): bỏ `stop.set()`, bỏ drain `await worker`, không `close()`, không retry khi connect lỗi | 3 mutant FAIL. Mutant bỏ `stop.set()` làm test **treo** (timeout 60 s của tôi), không FAIL. Xem CL-04 |
| `bash tests/shell/run.sh`, môi trường sạch (bỏ `ZD_HELM_HOME`, `ZD_PROMTOOL`, `MSYS_*`, `HELM_PLUGINS`) | exit 0, **34/34**, 73 s |
| `run.sh` với `MSYS_NO_PATHCONV=1`, `MSYS2_ARG_CONV_EXCL=*` | exit 0, 34/34, cùng tập dòng PASS. Lần gọi đầu của tôi sai cú pháp env (exit 127, 0 test chạy), không tính; lần chạy đúng ghi ở đây |
| `test-local-restore.sh` (Helm thật, promtool 3.15.0, Helm home trong scratch) | exit 0, **17 PASS**, 0 FAIL. Có SHA chart Kafka `8d32f6b9…a57e`, renderer, và budget 410m/712Mi requests, 2025m/1920Mi limits |
| Render Kafka 29.3.2 riêng với Helm v4.2.2, có và không có renderer (`render-kafka.sh`); quét scalar plain mà YAML 1.1 (PyYAML) và YAML 1.2 hiểu khác kiểu (`yaml_scalars.py`, bỏ qua document Secret) | 15/15 object ở cả hai bản. **0 scalar có rủi ro đổi kiểu** khi renderer load/dump lại. Phép so ngữ nghĩa của Codex dùng PyYAML cho cả hai phía nên không tự bắt được loại lỗi này; phép quét này bù vào |
| `git diff --check` cho file tracked trong scope; quét CRLF và khoảng trắng cuối dòng ở file untracked | OK. `target-app.yaml` vẫn CRLF toàn file như trước. 5 dòng khoảng trắng thừa trong `nemesis/main.py` có từ trước, nằm ngoài hunk sửa |

**Runtime chỉ đọc lúc 20:03–20:10:**
- Docker `desktop-linux`, không `DOCKER_HOST`; 2 node Ready.
- Helm: `kafka` revision 3 (18:25:44, `kafka-29.3.2`), `prometheus` revision 1, `traefik` revision 1.
- StatefulSet `kafka-controller`, container `jmx-exporter`: `command=["java"]`, args bắt đầu `-Xms32m -Xmx128m`, limit 256Mi. Container `kafka` không đổi (768Mi). **Kết quả Helm 4 trên runtime được xác nhận độc lập.**
- Không còn ServiceMonitor `target-app/frontend-monitor`. Prometheus có **17 target active, 17 up**.
- Ba PVC giữ đúng UID/volume và Bound: ES `77dd28b6…`, Prometheus `ae141e1f…`, Kafka `26544729…`.
- Quota target-app đang dùng: limits.cpu 2025m/3, limits.memory 1920Mi/4Gi, requests 410m/712Mi.
- SHA-256 `/app/main.py` trong pod Nemesis là `2e087b3c…577443e`, khớp source.
- Restart khác 0: chỉ `cartservice` r=1 (Error, 15:23, có từ trước gói).
- Pressure: WSL MemAvailable 2,40 GiB; PSI memory avg60 0,02; host `MemFree` 1,68 GiB.

Raw ở `scratch/claude-final-review/` (`tests-summary.txt`, `run-*.out`, `restore.out`, `nemesis-*.out`, `kafka/`, `ledger-check.txt`).

### Đánh giá theo nhóm

| Nhóm | Đánh giá |
| --- | --- |
| Kafka JMX | **Đạt.** Renderer chỉ chọn đúng một StatefulSet `zero-door/kafka-controller` và container `jmx-exporter`. Nó từ chối khi command/args khác dự kiến, `MaxRAMPercentage=100` không xuất hiện đúng một lần, limit khác 256Mi, hoặc đã có `-Xmx`/`-Xms`. Lỗi parse dừng Helm (exit khác 0). `zd_helm` luôn đặt `HELM_PLUGINS` vào Helm home của checkout, nên biến bên ngoài bị bỏ qua (có mock kiểm). Plugin được copy lại mỗi lần chạy. Không chạm Secret/PVC: object khác giữ nguyên ngữ nghĩa; UID PVC và Secret không đổi theo evidence, và runtime khớp. Đường rerun `setup-phase1.sh --component kafka` luôn có renderer. Nhánh Helm 3 chỉ có mock argv, chưa chạy thật; Codex đã ghi đúng giới hạn này. Cloud `deploy.sh:114` vẫn cài trần, cũng đã được nêu là giới hạn |
| Scrape/probe | **Đạt, có CL-01.** Thu hồi đúng một object theo tên, không `delete -f`. Mock kiểm lệnh xóa, kiểm manifest không còn được apply, và kiểm target 404 nay cho exit 1. Không còn ngoại lệ exit 3. Không rule hay agent nào dùng job `frontend`: HTTP lấy từ Traefik, CPU từ cAdvisor. Live có 17/17 target up. Thay đổi CPU limit và probe có căn cứ: throttle khoảng 70% và kubelet ghi lỗi liveness 137, không OOM. Requests giữ nguyên. Codex ghi rõ đây là baseline mới và không được trộn với dataset cũ |
| Nemesis | **Đạt.** Construct, poll và close đều trên cùng một worker thread; vòng chính không gọi Kafka API. Lỗi connect hoặc poll được log rồi `stop.wait(1)` và thử lại. Khi bị hủy: `shield` → `stop.set()` → chờ worker → close xong mới ném lại `CancelledError`. Uvicorn 0.30.1 chạy bằng `asyncio.run`, nên lúc shutdown task bị hủy và worker thoát trong khoảng ≤ 1 s poll. Topic, group, `auto_offset_reset` và format log giữ nguyên; không chạm attack/LLM/heal. Test bắt được hồi quy thật (bản trước sửa FAIL) và 3/4 mutant |
| Guard/test/CI | **Đạt, có CL-02 và CL-04.** `zd_docker_guard` nằm trước `docker info` và `k3d cluster delete`; mock kiểm context sai và `DOCKER_HOST`. Job `bash-tooling` dùng `setup-python` và PyYAML pin, chạy `run.sh` và test consumer; `publish-images` phụ thuộc job này. Test thật cho renderer gọi Helm thật, không phải phản chiếu implementation. CI cloud chưa chạy |
| Hướng dẫn/evidence | **Đạt, có CL-03.** `bash-tooling.md` khớp source: renderer, exit 0/1, thu hồi monitor, giới hạn Helm 3 và cloud. Phase2 và runbook legacy bỏ tham chiếu manifest đã xóa. Mục 12 của lab-restoration giữ lần quan sát thất bại và không nhận LLM, KPI, recreate, uptime 99,9% hay checkout xuyên ingress |

### Findings không chặn AC

| ID | Mức | Vị trí | Repro / tác động | Đề xuất sửa | Retest |
| --- | --- | --- | --- | --- | --- |
| CL-01 | Low | `infrastructure/scripts/setup-local-apps.sh:25-33`; `tests/shell/test-local-restore.sh:258,286-289`; `docs/runbooks/bash-tooling.md:78` | Runbook ghi "Rollout tuần tự", nhưng đường dựng lặp lại apply cả `target-app.yaml` và `target-app-addons.yaml` trong một lượt. Khi spec của currency, email và payment cùng đổi (ví dụ apply lên một lab còn cấu hình cũ), ba pod surge (`maxSurge` mặc định 1, `maxUnavailable` 0) cần limits.cpu 2025m + 400m + 300m + 300m = **3025m > quota 3000m**. Pod thứ ba bị quota từ chối (`FailedCreate`) và rollout của nó chậm lại tới khi một surge khác xong. Controller tự retry nên thường vẫn hội tụ trong 300 s. Test chỉ kiểm từng Deployment riêng, và chỉ hai chiều (limits.cpu, requests.memory). Comment dòng 258 nói có tính LimitRange default nhưng code không tính. Codex đã rollout tay từng Deployment nên runtime không gặp | Chọn một trong hai cách: (a) mô hình hóa surge đồng thời của mọi Deployment có thể đổi trong một lần apply, trên cả 4 chiều quota; hoặc (b) làm cho thứ tự tuần tự thật sự xảy ra (apply hoặc rollout theo từng Deployment), rồi sửa runbook cho khớp. Không tăng quota | `test-local-restore.sh`, `run.sh` |
| CL-02 | Low (chưa xác minh trên CI) | `.github/workflows/ci.yml:49` | Job `helm-lint` gọi `python3 -m pip install PyYAML==6.0.2` vào Python hệ thống của `ubuntu-latest`, không qua `setup-python`. Trên Ubuntu 24.04, PEP 668 có thể làm lệnh này lỗi `externally-managed-environment`. Có nguồn nói runner image đang tắt cơ chế này, nhưng tôi chưa xác minh được từ GitHub. Lỗi sẽ làm hỏng `helm-lint`, kéo theo chặn `publish-images`. Bước cũ đã `import yaml` được mà không cần cài, nên dòng này không cần thiết | Bỏ dòng cài, hoặc thêm `actions/setup-python` như job `bash-tooling` | Lần CI đầu sau khi push (cần quyền publication) |
| CL-03 | Low (tài liệu) | `infrastructure/helm-values/kafka-values.yaml:6-8` | Header của file vẫn hướng dẫn `helm install kafka … -f kafka-values.yaml` trần. Làm theo sẽ đưa lại `MaxRAMPercentage=100`, tức cấu hình đã gây OOM. Điều này mâu thuẫn với comment mới ở dòng 104-106 và với runbook | Đổi header thành `bash infrastructure/scripts/setup-phase1.sh --component kafka` | Đọc lại |
| CL-04 | Low (test) | `tests/test_nemesis_consumer.py:79-81`; `.github/workflows/ci.yml` (job không có `timeout-minutes`) | Khi bỏ `stop.set()`, thread không bao giờ dừng. `wait_for` hết hạn, nhưng lúc đóng loop phải join executor, nên test treo thay vì FAIL. Trên CI, job sẽ chờ tới timeout mặc định của GitHub | Đặt `timeout-minutes` cho job, hoặc thêm watchdog hay timeout mức process cho test | Chạy lại mutant `no-stop-on-cancel`: phải FAIL trong thời gian giới hạn |

### Quan sát mới (không chặn AC)

**OBS-02:** Lúc 19:45:58 +07:00, sau cửa sổ quan sát 18:36–18:51 của Codex, `shippingservice` (không thuộc ba service đã chỉnh) có một lần liveness gRPC timeout 1 s. Không restart, vì `failureThreshold` mặc định là 3; event có tổng `count` 2 kể từ 13:42. Từ 18:50 không có event Kernel-Power, Power-Troubleshooter hay Kernel-General trên Windows. Lúc 20:05, CPU PSI some avg60 là 2,47. Hiện tượng khớp với giả thuyết OBS-01: node có những lần stall thoáng qua, và các service còn timeout 1 s vẫn có thể lỡ probe. Nguyên nhân gốc chưa xác định. Cửa sổ 15 phút không chứng minh đã hết. Không đề xuất nới probe thêm trong ZER-35. Cần đưa việc theo dõi probe timeout và restart vào protocol warm-up và pilot, cùng baseline cho mọi cấu hình đối chứng.

### Phần đủ và chưa đủ

- **Đủ cho AC restore** (ZER-35 AC-01, phần tích hợp ZER-6 AC-03):
  - đường dựng Bash có renderer và guard;
  - dữ liệu được bảo toàn: PVC và Secret giữ UID;
  - API truy cập được;
  - telemetry 17/17 up;
  - Kafka, log và checkout có evidence của Codex, được đối chiếu raw: verify cuối exit 0, 0 failure, 41 PASS; 31 mẫu, 17/17 up, 0 pod chưa Ready;
  - profile tài nguyên đo được, có giới hạn ghi rõ.
- **Chưa kiểm:** CI cloud; Helm 3 chạy thật; đường cloud; recreate thật; checkout xuyên ingress; nhánh 5xx trên runtime; LLM, attack, heal, BLOCK_IP, KPI. Mục 12 đã nêu đúng các giới hạn này. Chúng không phải finding của gói và không mở rộng scope ZER-35.
- **Tôi không chạy lại `verify-local-lab.sh`**, vì probe đó tạo pod, topic và giao dịch tạm. Nếu Hoàng muốn có bằng chứng tích hợp mới do Claude chạy trước merge, lệnh là `bash infrastructure/scripts/verify-local-lab.sh --check all`. Tác động: tạo hai pod busybox `--rm` trong `target-app`, một đơn hàng demo, message trên topic riêng `zd.verify.restore`, một log sentinel và tối đa 12 GET. Cần giao ở lượt sau.

**Bàn giao:** CL-01–04 có thể gom thành một gói nhỏ cho Codex; cả bốn đều không chặn commit/merge. Publication, merge, cập nhật Linear và việc Hoàng chấp nhận vẫn là các cổng riêng, chưa được cấp trong lượt review này.

### Giao Codex sửa CL-01–04 trước merge — 18/10/2026 (Hoàng quyết định, Claude ghi)

Quyết định của Hoàng, nguyên văn: “Giao Codex sửa gọn CL-01–04 trong một lượt trước khi merge.” Codex là bên ghi checkout trong lượt này. Claude không ghi checkout và không thao tác cluster cho tới khi Codex bàn giao lại.

**Baseline:** HEAD `1f43ff1`, staged rỗng, ledger `scratch/zer35-final/final-file-ledger.json` (lệch duy nhất ở `NOW.md`, là tài liệu). Trước khi sửa, chụp lại hash các file sẽ chạm. Giữ mọi thay đổi dirty ngoài scope.

| ID | File được sửa | Đích cần đạt |
| --- | --- | --- |
| CL-01 | `infrastructure/scripts/setup-local-apps.sh`; `tests/shell/test-local-restore.sh`; `tests/shell/run.sh` nếu hành vi script đổi; `docs/runbooks/bash-tooling.md` | Đường dựng lặp lại và test phải nói cùng một điều về surge dưới quota `target-app`. Có hai cách. (a) Rollout thật sự tuần tự: apply và chờ từng Deployment, không apply cả file một lượt để cùng lúc đổi nhiều spec. (b) Giữ apply cả file, nhưng test mô hình hóa surge đồng thời của mọi Deployment có thể đổi trong một lần apply, và budget vẫn phải vừa. Claude nghiêng về (a), vì (b) hiện vượt 25m limits.cpu. Kiểm cả 4 chiều quota (requests/limits × cpu/memory). Sửa hoặc bỏ comment “LimitRange defaults” ở `test-local-restore.sh:258` nếu code không tính. Không tăng quota, không đổi CPU/RAM/probe đã chốt |
| CL-02 | `.github/workflows/ci.yml` (job `helm-lint`) | Không `pip install` vào Python hệ thống của runner. Bỏ dòng ở `ci.yml:49` (bước này vốn đã `import yaml` được), hoặc thêm `actions/setup-python` như job `bash-tooling` |
| CL-03 | `infrastructure/helm-values/kafka-values.yaml` (chỉ comment header, dòng 6-8) | Header chỉ tới `bash infrastructure/scripts/setup-phase1.sh --component kafka`, không còn lệnh `helm install` trần. Không đổi giá trị values, nên không cần Helm upgrade |
| CL-04 | `.github/workflows/ci.yml`; `tests/test_nemesis_consumer.py` nếu chọn watchdog trong test | Một bản Nemesis không dừng được worker phải làm test **FAIL trong thời gian có giới hạn**, không treo job. Ví dụ: `timeout-minutes` cho job, hoặc timeout mức process cho test. Không đổi `agent-orchestrator/nemesis/main.py` |

**Retest bắt buộc**, ghi lệnh, exit và số PASS:
- `bash -n` cho script đã sửa. Parse YAML của `ci.yml`.
- `bash tests/shell/run.sh` ở môi trường sạch và với `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL=*`.
- `bash tests/shell/test-local-restore.sh`.
- `python tests/test_nemesis_consumer.py`.
- Mutant `no-stop-on-cancel` (dùng lại `scratch/claude-final-review/nemesis_mutations.py`): phải FAIL hoặc bị timeout có chủ đích trong thời gian giới hạn.
- Với CL-01: thêm một case chứng minh test bắt được khi ba surge cùng lúc vượt quota (case trước sửa FAIL, sau sửa PASS); hoặc mock chứng minh thứ tự apply/rollout là tuần tự.
- `git diff --check` và ledger mới.

**Không cần thao tác lab.** Spec live đã đúng, và cả bốn mục chỉ đổi script, test, CI hoặc comment. Không apply, upgrade, build, rollout hay delete. Nếu Codex thấy cần kiểm runtime cho đường mới của CL-01, ghi rõ lệnh và tác động rồi dừng chờ Hoàng duyệt, không tự chạy.

**Ngoài phạm vi lượt này:**
- OBS-02, nguyên nhân probe timeout: ghi vào protocol warm-up/pilot sau; không nới probe trong ZER-35.
- Helm 3 chạy thật, cloud, recreate.
- Commit, push, merge, cập nhật Linear.

**Bàn giao lại:** Codex nối kết quả vào `lab-restoration.md`, mục 12 (hoặc một tiểu mục ngắn ngay sau đó), và cập nhật con trỏ NOW. Claude sẽ review lại đúng delta CL-01–04. Sau đó mới tới cổng publication/merge và Hoàng chấp nhận.

## Claude review delta CL-01–04 — 18/10/2026, 20:38–20:50 +07:00 (Claude)

**Kết luận: PASS. CL-01–04 đã đóng, không có finding mới.** Gói ZER-35 (bản review 20:15 cộng delta này) **đủ điều kiện chuẩn bị commit/merge trong quyền Hoàng cấp**. Đây không phải trạng thái Done: merge và việc Hoàng chấp nhận vẫn là hai cổng riêng.

Phạm vi lượt này: chỉ review delta và regression liên quan. Không review lại toàn gói, không dựng lại lab. Không sửa file nào ngoài mục này và con trỏ NOW. Không apply/build/rollout, không commit/push/merge, không đổi Linear.

### Bản được review

- HEAD `1f43ff1`, staged rỗng.
- Ledger `scratch/zer35-cl-final/final-file-ledger.json` có 9 file. Với cả 9 file, `beforeSha256` trùng hash trong ledger mà Claude đã review lúc 20:15, trừ `NOW.md` (con trỏ do Claude sửa sau ledger đó). Mọi `sha256` khớp source hiện tại.
- Các file mã còn lại trong ledger cũ không đổi: `nemesis/main.py`, renderer/plugin, `common.sh`, `setup-phase1.sh`, `verify-local-lab.sh`, `recreate-cluster.sh`, `deploy.sh`, ba manifest target. Chỉ `codex-review.md` đổi, do chính mục review của Claude.
- Bản đã review được dựng lại bằng cách áp `delta.diff` lên base. Bản dựng lại khớp từng hash `beforeSha256`, nên diff dưới đây đúng là delta CL: `scratch/claude-final-review/cl-delta.diff`, 7 file mã/test/runbook.

### Đối chiếu từng mục

| Mục | Thay đổi | Kiểm độc lập | Kết quả |
| --- | --- | --- | --- |
| CL-01 | `setup-local-apps.sh` dùng Python/PyYAML tách hai manifest. Script từ chối namespace khác, kind khác, Deployment trùng, hoặc danh sách Deployment khác thứ tự đã khai. Sau đó apply Service/ServiceAccount trước, rồi apply → `rollout status` → chờ mọi pod terminating bị xóa, lần lượt cho 9 Deployment. Thứ tự: Redis trước cart; checkout và frontend sau backend. Thư mục tạm trong `scratch/` được trap dọn theo đúng pattern. Test thật mô hình hóa steady cộng một surge trên đủ 4 chiều quota, có mutation kiểm từng chiều. Phép cộng ba surge đồng thời ra 3025m và bị từ chối | **RED:** test thứ tự mới chạy trên script trước sửa trong cây tạm cho exit 1, `concurrent rollout: currencyservice and productcatalogservice`. **Runtime chỉ đọc:** tạo JSON bằng chính đoạn Python của script rồi `kubectl diff` (server dry-run, không lưu) cả 10 object với lab: tất cả exit 0, 0 dòng khác. Nghĩa là đường mới trên lab hiện tại là no-op và không kích hoạt rollout. `kubectl wait --for=delete` trên pod không tồn tại trả 0 ngay, nên race giữa `get` và `wait` an toàn. Quét kiểu scalar YAML 1.1/1.2 cho hai manifest: 0 rủi ro. Không còn thư mục `scratch/target-rollout.*` sót lại | Đóng |
| CL-02 | Job `helm-lint` thêm `actions/setup-python` 3.11 trước bước cài PyYAML pin; bỏ `pip install` vào Python hệ thống | Parse YAML đạt; thứ tự setup → install → lint đúng. CI remote chưa chạy | Đóng (chờ lần CI đầu) |
| CL-03 | Header `kafka-values.yaml` chỉ tới `bash infrastructure/scripts/setup-phase1.sh --component kafka` | YAML trước và sau bằng nhau về ngữ nghĩa (`safe_load` so bằng): chỉ đổi comment, không cần Helm upgrade | Đóng |
| CL-04 | Entry point test chạy unittest trong tiến trình con, deadline 30 s, hết hạn thì exit 1. Job `bash-tooling` có `timeout-minutes: 10`. `nemesis/main.py` không đổi | Chạy lại 4 mutant: `no-stop-on-cancel` exit 1 với `FAIL: consumer tests exceeded the 30s process deadline; worker terminated` (trước đây treo); 3 mutant còn lại FAIL như trước. Bản hiện tại exit 0 (6 s) | Đóng |

### Regression liên quan (Claude chạy, 20:41–20:49)

| Lệnh | Kết quả |
| --- | --- |
| `bash -n` cho `setup-local-apps.sh`, `run.sh`, `test-local-restore.sh`; YAML parse `ci.yml`, `kafka-values.yaml` | OK |
| `python tests/test_nemesis_consumer.py` | exit 0 |
| `bash tests/shell/run.sh`, môi trường sạch | exit 0, **37/37**, 82 s |
| `run.sh` với `MSYS_NO_PATHCONV=1`, `MSYS2_ARG_CONV_EXCL=*` | exit 0, 37/37, 90 s, cùng tập dòng PASS |
| `test-local-restore.sh` (Helm thật, promtool) | exit 0, **18 PASS**, 0 FAIL |
| Whitespace/CRLF 7 file; `git diff --check` file tracked | OK |

Raw ở `scratch/claude-final-review/cl/` (`summary.txt`, `run-*.out`, `restore.out`, `consumer.out`, `mutants.out`, `red-run.out`).

### Giới hạn còn lại (không phải finding)

- **Đường apply tuần tự chưa chạy trên cluster với spec thật sự thay đổi.** Đã có bằng chứng: mock theo thứ tự/drain/lỗi, budget, RED, và `kubectl diff` no-op trên lab hiện tại. Thời gian rollout cộng drain thật chỉ biết khi có thay đổi spec. Codex và runbook đã ghi đúng giới hạn này.
- CI remote, Helm 3 chạy thật, cloud, recreate và OBS-02 giữ nguyên như review 20:15.
- **Nhận xét Info, không cần sửa trước merge:** khi thiếu PyYAML, `setup-local-apps.sh` dừng bằng traceback Python thay vì thông báo `zd_die` như `zd_kafka_renderer`. Hành vi vẫn là dừng an toàn (fail closed).
- Linear: connector của phiên Claude vẫn trỏ workspace khác, nên chưa đọc live. Codex ghi đã đọc ZER-35 qua `linear_zero_door`.

**Bàn giao:** không còn việc sửa trong ZER-35 từ phía review. Bước tiếp thuộc Hoàng: cấp quyền publication (commit/PR/merge) theo WORKFLOW, rồi chấp nhận. Lab vận hành đúng cấu hình đã kiểm ở mục 12 của lab-restoration; delta CL không đòi triển khai lại.
