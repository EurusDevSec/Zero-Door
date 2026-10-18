# Claude — ZER-35: review độc lập gói sửa cuối

## Nhiệm vụ hiện hành — review sau gói Codex ngày 18/10/2026

Hoàng đồng ý bước tiếp theo là Claude review độc lập sau khi Codex sửa và kiểm chứng gói cuối. Phần này thay nhiệm vụ thực thi ở các mục bên dưới; các mục cũ được giữ làm lịch sử phạm vi. **Lượt này Claude là reviewer, không tiếp tục triển khai.** Codex dừng ghi checkout khi bàn giao; không tự gửi tin sang phiên Claude.

### Đọc và khóa bản được review

1. Đọc AGENTS.md, delivery README/NOW/WORKFLOW, ghi chú local-lab.md; đối chiếu AC ZER-35 và phần tích hợp ZER-6 qua `linear_zero_door` nếu có. Nếu thiếu connector, ghi chưa đọc live và dùng snapshot AC bên dưới, không sửa OAuth hoặc đổi workspace.
2. Đọc `docs/evidence/ZER-35/lab-restoration.md` **mục 11–12** và mục cuối của `codex-review.md`. Các kết quả trước đó là lịch sử, không thay bản cuối.
3. Chụp HEAD, staged/unstaged/untracked và SHA-256 các file review trước khi làm. Codex vừa đọc lại HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`; working tree có nhiều thay đổi kế thừa, chưa commit. Đọc cả file untracked vì `git diff` không bao phủ chúng. Không reset/clean/stash hoặc áp lại hai patch Traefik lịch sử.
4. Nếu có `scratch/zer35-final/final-file-ledger.json`, đối chiếu hash với source hiện tại. Ledger là phạm vi gói Codex, không mô tả mọi thay đổi kế thừa. Nếu source đã khác, chỉ rõ phần lệch trước khi dùng kết quả kiểm cũ. Không cần đọc lại toàn repo.

### Phạm vi và câu hỏi review trọng tâm

| Nhóm | File cần đối chiếu | Cần kiểm tra |
| --- | --- | --- |
| Kafka JMX | `infrastructure/helm-postrenderers/kafka-jmx/{plugin.yaml,render.py}`; `infrastructure/scripts/lib/common.sh`; `setup-phase1.sh`; `infrastructure/helm-values/kafka-values.yaml` | Renderer chỉ đổi JVM args đúng container, fail khi layout/budget không khớp; Helm 4 plugin local và nhánh Helm 3; không làm đổi Secret/PVC hoặc tin biến HELM_PLUGINS bên ngoài; đường rerun thực sự dùng renderer |
| Scrape/probe | `infrastructure/scripts/setup-local-apps.sh`, `verify-local-lab.sh`, `deploy.sh`; manifest `target-app.yaml`, `target-app-addons.yaml`; việc bỏ `target-app-monitor.yaml` | Thu hồi đúng ServiceMonitor lỗi; không che target down bằng exit 3; nguồn metric còn đủ; CPU/probe thay đổi có căn cứ, tính cả rollout surge dưới quota; không làm sai baseline nghiên cứu |
| Nemesis | `agent-orchestrator/nemesis/main.py`, `tests/test_nemesis_consumer.py` | Vòng Kafka không chặn event loop; constructor/poll/close cùng worker thread; retry, cancellation/drain và shutdown đúng; test bắt được hồi quy thật; không đổi topic/group/schema hay logic attack/LLM/heal |
| Guard/test/CI | `infrastructure/scripts/recreate-cluster.sh`, `tests/shell/run.sh`, `tests/shell/test-local-restore.sh`, `.github/workflows/ci.yml` | Guard trước nhánh delete; test không chỉ phản chiếu implementation; PyYAML/plugin prerequisites, native Windows/Git Bash paths và CI wiring đúng |
| Hướng dẫn/evidence | `docs/runbooks/bash-tooling.md`, `phase2_runbook.md`, `2026-10-09-legacy-demo-restart.md`; lab-restoration mục 12 | Lệnh dựng khớp source; kết quả và giới hạn có bằng chứng; không nhận cloud/LLM/KPI/recreate đã được kiểm |

### Kiểm chứng và giới hạn của lượt review

- Chỉ dùng Bash. Được đọc source, chạy kiểm tra offline cần thiết và truy vấn runtime chỉ đọc. Chạy lại các kiểm tra bị ảnh hưởng để xác nhận độc lập; không cần nhân lại mọi phép đo đã có hoặc chờ từng component.
- Các entry point kiểm offline: `bash tests/shell/run.sh`, `python tests/test_nemesis_consumer.py`, `bash tests/shell/test-local-restore.sh`. Đọc script/prerequisites trước khi chạy; phân biệt mock với render/PromQL thật. Không ghi PASS khi lệnh lỗi, thiếu dependency hoặc thiếu dữ liệu. Không cài công cụ toàn máy/dispatch CI cloud để vượt thiếu prerequisite.
- Không tự chạy `verify-local-lab.sh --check all` như một truy vấn chỉ đọc: nó có probe tích hợp tạo dữ liệu/tài nguyên tạm. Lượt này ưu tiên đọc evidence/raw và truy vấn không thay cluster. Nếu cần retest có mutation để phân xử finding, nêu đúng lệnh, tác động và lý do trong báo cáo trước khi thực thi ở lượt được giao tiếp theo.
- Không sửa source/config hoặc thao tác apply/upgrade/build/import/rollout/delete/recreate; không gọi attack/heal/reset/LLM, stress, cloud, sửa quota/WSL, commit/push/merge hay cập nhật Linear. Không đọc/in Secret data. Được ghi duy nhất báo cáo review bên dưới và con trỏ NOW ngắn; lưu output tạm trong scratch.
- Theo GitNexus/freshness trong AGENTS; lần refresh trước timeout, index cũ không bao phủ gói mới. Dùng source trực tiếp khi graph không đủ; không lặp analyze vô hạn hoặc gỡ lock/index.

### Bằng chứng Codex bàn giao — phải tự đánh giá, không kế thừa PASS

Mục 12 ghi: 34 nhóm mock, 3 test consumer, render/PromQL/quota đạt; full verify cuối exit 0 sau rollout Nemesis. Quan sát **18:36:31–18:51:48 +07, 31 mẫu/15 phút 17 giây**, 17/17 target up, không restart/thay pod bất thường hoặc Warning mới. JMX đỉnh 141Mi/256Mi; PVC UID/volume và quota giữ nguyên. Source Nemesis trong pod khớp SHA `2e087b3c0ce4bae4700a2e8fd9d31ba989c66fda700281b6f9c5bb462577443e` tại lần kiểm đó; không coi là số đo live mới.

Giữ cả lần observation thất bại trước sửa Nemesis và các lỗi cũ trong raw. Không dùng 15 phút để chứng minh uptime 99,9%, không nhận đã có LLM/ba vector/BLOCK_IP. Host client IP vẫn có SNAT; checkout dùng loopback, ingress kiểm riêng; nhánh 5xx chỉ có synthetic test. Cloud và Helm 3 chưa được runtime kiểm. Đây là giới hạn của restore, không tự mở rộng thành các issue nghiên cứu sau.

### Đầu ra và điều kiện kết thúc

Nối một mục **Claude review độc lập gói Codex cuối** vào `docs/evidence/ZER-35/codex-review.md`, giữ nguyên review lịch sử và tự kiểm của Codex. Báo cáo gồm revision/hash được review; lệnh và kết quả tự chạy; finding có severity, file:line, repro/impact, sửa đề xuất và retest cần thiết; tách lỗi chặn AC khỏi cải tiến không chặn. Không bịa finding để đủ số lượng. Trả một kết luận tổng hợp: PASS, CHANGES REQUESTED hoặc BLOCKED do thiếu bằng chứng, nêu rõ phần nào đủ/chưa đủ.

Nếu không có finding chặn, ghi **đủ điều kiện chuẩn bị commit/merge trong quyền Hoàng cấp**, không ghi issue Done. Nếu cần sửa, gom findings thành một gói để Codex xử lý; không tự sửa trong lượt review. Merge và Hoàng chấp nhận vẫn là gate riêng; chưa có quyền publication hoặc đổi Linear từ lời đồng ý review này.

---

## Phạm vi thực thi trước đây — lưu để truy vết

## Quyền thực hiện và cách phối hợp của lượt khôi phục trước

Cập nhật 18/10/2026 theo yêu cầu Hoàng: gom phần còn lại của ZER-35 thành một gói, Claude làm xuyên suốt, Codex review cả gói; Hoàng theo dõi/luyện và chấp nhận kết quả. Hoàng đã trả lời “được vậy tiếp tục thôi” sau đề xuất giao trọn issue với phạm vi và giới hạn rõ. Không hỏi lại quyền cho mỗi component trong phạm vi dưới đây.

File này thay phạm vi **chỉ review/sizing** trước đó trong cùng file; kết quả lượt cũ vẫn giữ nguyên trong evidence. Các câu “chưa được apply/sửa source” trong báo cáo/handoff lịch sử mô tả quyền của lượt cũ, không phủ định quyền thực thi mới tại đây. Giới hạn ngoài phạm vi vẫn áp dụng.

- Issue: [ZER-35](https://linear.app/zero-door/issue/ZER-35/khoi-phuc-lab-tu-inventory-dja-kiem-chung), thuộc [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local).
- Claude là bên ghi checkout và thao tác cluster duy nhất sau bàn giao. Codex chỉ review cho tới khi Claude trả kết quả; không tự gửi tin nhắn cho agent khác. Hoàng luyện ở bản sao riêng hoặc chỉ đọc.
- Chặng kỹ thuật là checkpoint nội bộ, không phải một lượt xin phép/bàn giao. Tự chẩn đoán, sửa, kiểm tra lại và tiếp tục khi nằm trong scope. Giữ cập nhật tiến độ ngắn; không chờ người dùng nhắn “tiếp tục” sau mỗi nhóm.
- Không mở issue/milestone mới. Linear giữ AC/state; file này giữ phạm vi thực thi và verification, không là board thứ hai.

## Outcome và AC phải đối chiếu

Live ZER-35/ZER-6 được Codex đọc qua linear_zero_door ngày 18/10/2026. Nếu Claude thiếu connector, dùng snapshot sau, ghi live state chưa đọc; không sửa OAuth để lấy quyền và không coi Markdown là state mới.

- ZER-35 AC-01: chọn đường restore theo inventory, bảo toàn dữ liệu, Kubernetes API truy cập, có đường dựng lặp lại và profile tài nguyên đo được; kiểm đúng chức năng script.
- ZER-6 AC-03 liên quan tích hợp: Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique được kiểm chứng. Ít nhất 5 microservices cùng luồng nghiệp vụ thật; Running riêng lẻ không đủ.
- AC còn nhắc tên .ps1 thuộc baseline cũ; dùng bản Bash hiện tại và evidence migration để đối chiếu, không khôi phục PowerShell.
- Đích gói này: stack nền local có cách dựng rõ, dependency/agent health có evidence, telemetry và giao dịch mẫu có kết quả thật, sizing thực tế cùng giới hạn. Chưa phải hoàn thiện ba vector, healer hoặc LLM của đề tài.
- Nếu vướng quyết định ngoài scope hoặc máy không đủ, bàn giao PARTIAL/BLOCKED theo phần với lỗi và phương án cụ thể; không đổi AC hay gọi đó là PASS. Vẫn hoàn tất phần độc lập có ích. Không tự đặt Linear Done; mã còn cần Codex review, verification, merge và Hoàng chấp nhận.

## Đọc tối thiểu và baseline

Đọc AGENTS.md; delivery README/NOW, SCOPE/WORKFLOW và milestones/R0-foundations/local-lab.md. Dùng .agent/rules/CONTEXT.md và .agent/workflows/session_memory.md như lịch sử, không kế thừa claim Complete. Sau đó đọc:
- docs/evidence/ZER-35/codex-review.md, ưu tiên retest và review namespace mới nhất;
- claude-review-and-resource-profile.md, namespace-bootstrap.md và bash-migration.md cùng thư mục;
- docs/runbooks/bash-tooling.md và đúng manifest/script cần sửa. Không đọc lại toàn repo hoặc viết lại báo cáo sizing đã review.

Baseline Codex xác minh Git lúc 12:16:46 +07:00: main, HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975, staged rỗng; migration Bash và docs/evidence đang dirty/untracked. Không reset/clean/restore. Chụp lại status gồm untracked, hash file sẽ chạm và exact file/action plan trước sửa.

Baseline runtime cuối Codex kiểm tra 12:10–12:12: desktop-linux, k3d-zero-door, 2 node Ready; 3 Namespace/Quota/LimitRange khớp nguồn; chỉ 3 pod hệ thống; chưa workload/PV/PVC. Không dùng mốc này thay preflight mới. Giữ WSL 7GB/4CPU/2GB swap; Docker thấy khoảng 6,77GiB. Đây không phải dự báo stack đầy đủ vừa máy.

Dùng Git Bash cho toàn bộ terminal và hướng dẫn. Theo AGENTS cho GitNexus/freshness; index trước bị cũ và analyze đã timeout, không lặp vô hạn hoặc xóa index/lock. Graph không thay direct source/runtime; manifests/chart/Bash mới cần đọc trực tiếp.

## File scope được sửa

Ghi exact subset trước mỗi đợt sửa, giữ phần dirty không liên quan. Không hiểu allowlist là phải sửa tất cả.

| Nhóm | File được sửa/thêm phục vụ restore |
| --- | --- |
| Công cụ Bash | infrastructure/scripts/lib/common.sh; setup-phase1.sh; setup-phase3.sh; setup-phase4.sh; setup-phase5.sh; requirements-experiments.txt; start-demo.sh; rebuild-nemesis.sh |
| Đường dựng Boutique/Gaia | Được thêm infrastructure/scripts/setup-local-apps.sh cho triển khai nền nếu cần; không tạo hệ phase/task mới |
| Helm | infrastructure/helm-values/ingress-nginx-values.yaml; prometheus-values.yaml; kafka-values.yaml; được thêm infrastructure/helm-values/chart-versions.yaml làm nguồn version dùng thật trong script, tránh hai nguồn pin |
| Manifest nền | infrastructure/manifests/target-app.yaml; target-app-addons.yaml; target-app-ingress.yaml; target-app-monitor.yaml; prometheus-rules.yaml; gaia-deployment.yaml; nemesis-deployment.yaml; chaos-worker.yaml; hephaestus-deployment.yaml; network-policies.yaml |
| Log | infrastructure/logging/elasticsearch.yaml; fluent-bit.yaml |
| Verification | tests/shell/run.sh; được thêm tests/shell/test-local-restore.sh nếu cần test regression thực; được thêm infrastructure/scripts/verify-local-lab.sh cho probe không gây chaos |
| Tài liệu/evidence | docs/runbooks/bash-tooling.md; docs/evidence/ZER-35/lab-restoration.md; docs/evidence/ZER-35/ingress-preflight.md nếu cần quyết định ingress; local-lab.md và NOW.md chỉ handoff/con trỏ |

Không sửa logic agent Python/worker Go, runner/analysis hoặc báo cáo nghiên cứu để làm bài kiểm tra qua. Nếu lỗi ứng dụng chặn health, truy vết và đưa patch/phạm vi cụ thể cho Codex/Hoàng, không lấn sang issue nghiên cứu. Không sửa quota/namespace/K3d/WSL trong gói này; profile nền không HPA và không loadgenerator phải được ghi rõ. HPA là quyết định thí nghiệm sau, không bỏ khỏi scope nghiên cứu.

## Action scope được thực hiện xuyên suốt

Được truy vấn, tải chart/image/dependency miễn phí, render, build/import image repo vào cluster zero-door; apply manifest nền trong allowlist; Helm install/upgrade đúng release của lab sau kiểm chart; rollout/restart workload mình triển khai; probe metric/log/message và mua hàng mẫu. Được tạo venv trong scratch/gitignored nếu cần kiểm import; không cài Python/package/công cụ toàn máy. Chọn version theo upstream và compatibility, ghi version/digest; không dùng mirror không rõ nguồn khi image hỏng.

Mọi kubectl/Helm phải chỉ context k3d-zero-door và namespace/release tường minh. Xác minh Docker desktop-linux, API/nodes, inventory workload/release/PVC/Secret metadata trước mutation. Mismatch thì dừng nhánh liên quan, không tự chuyển daemon/context hoặc sửa kubeconfig. Helm repo/cache của phiên tách trong scratch để tránh sửa repo/cache toàn máy. Không in Secret/credential, không ghi đè Secret hiện có, không đưa token vào Git.

Trước apply/render file có nhiều kind, kiểm toàn bộ nội dung; không apply lại Secret mặc định làm mất credential. Không dùng setup-phase1 mặc định all; orchestration vẫn gọi nhóm rõ theo thứ tự dependency đã kiểm.

Cho phép tạo CRD/RBAC/ServiceAccount do chart giám sát và manifest nền yêu cầu khi đã render, liệt kê tên/ownership trước apply, không ghi đè object trùng tên thuộc stack khác. Không tăng quyền ứng dụng/agent thành cluster-admin để chữa lỗi. Không thay cluster version hoặc storage class.

## Các chặng tự làm, không cần Hoàng chuyển tiếp từng chặng

1. **Preflight và sửa blocker vận hành.** Chụp Git/context/inventory mới; bảo vệ dữ liệu cũ. Sửa context guard của Docker, hành vi k3d switch-context khi tạo mới bằng kiểm chứng mock (không tạo cluster thật), pin chart và tách helper cần thiết. Chỉ sửa dependency Python nếu đường verify thực sự dùng; kiểm import trong venv, không bắt cài đủ tool để chạy health.
2. **Khóa cấu hình thực trước nhóm tương ứng.** Pin/render chính chart sẽ cài; bao phủ default, dependency, sidecar/init/hook/provisioning job và resource hiệu dụng, min/max LimitRange, quota và từng node. Tính cả steady và rollout surge; không cộng quota thành RAM usage. Kafka phải đặt key controller.heapOpts đúng template, chừa headroom native/off-heap; giải quyết trường hợp provisioning Job + agents vượt quota bằng trình tự triển khai/lựa chọn resource có căn cứ, không tăng quota ngầm hoặc bỏ Job/topic cần thiết. Kiểm repeated rollout, không chỉ cài lần đầu.
3. **Dựng dependency và app nền.** Ingress theo quyết định bên dưới; monitoring/CRD trước ServiceMonitor/Kafka metrics; Boutique đủ dependency cho giao dịch; log; Kafka; Gaia/worker/Nemesis/Hephaestus. Thứ tự có thể điều chỉnh theo dependency/resource thực, ghi lý do. Nếu app thiếu recommendation/ad gây lỗi luồng mua hàng, được bật các dịch vụ sẵn có trong target-app-addons.yaml và tính lại ngân sách; không viết lại Boutique. Không bật traffic generator/HPA hoặc gọi endpoint attack/heal/reset. Agent baseline không đồng nghĩa AI đã hoạt động.
4. **Đo và xác minh mỗi nhóm, tự sửa trong scope.** Lưu timestamp, image identity thực và rollout status, requests/limits/usage, WSL MemAvailable/PSI, events/OOM/restarts. Không chỉ build image mutable rồi coi pod đã dùng image mới. Health check bằng GET /healthz khi phù hợp; đọc source để phân biệt route gây thay đổi. Nếu agent khởi động tự tạo hành động ngoài profile nền, dừng đúng Deployment mình vừa tạo, ghi trace; không kích hoạt liên tục để thử khả năng phục hồi.
5. **Kiểm tra tích hợp nền và đường lặp lại.** Kafka produce/consume với correlation ID ở topic kiểm tra tách khỏi attack.commands/monitoring.alerts/healing.actions; metric thực có dữ liệu app; một log sentinel truy được qua Fluent Bit/Elasticsearch; giao dịch mẫu đi đến checkout có bằng chứng. Dùng dữ liệu giả trong local, không payment/đích ngoài lab. Kiểm tunnel chỉ bind loopback và dọn đúng PID của phiên. Kiểm lại health sau lần chạy/rollout an toàn; không wipe cluster để chứng minh tái lập. Giữ raw lỗi, không đổi probe/KPI để có PASS.
6. **Bàn giao một gói.** Chạy kiểm tra offline liên quan thay đổi (bash -n, mock/regression có ý nghĩa, YAML/JS nếu sửa), git diff --check, scope/hash đầu-cuối. Ghi lab-restoration.md với AC → probe → expected/actual → artifact/verdict và phần chưa đạt; cập nhật runbook để người khác chạy được; NOW/local-lab chỉ trỏ kết quả. Trả Codex review một lần, không tự commit/push/merge hoặc sửa Linear.

### Ingress: xử lý quyết định mà không chặn mọi việc

Codex đã xác minh thông báo upstream ingress-nginx retirement tháng 03/2026; nguồn ở codex-review.md. Trước chọn version, kiểm compatibility với Kubernetes 1.31, annotation/WAF, IP nguồn/log và port K3d hiện có.

Không tự chọn controller mới hoặc âm thầm coi ingress-nginx đã hết bảo trì là lựa chọn lâu dài đã duyệt. Nếu cần lựa chọn legacy local có version cố định hay controller còn bảo trì, ghi hai phương án cụ thể trong ingress-preflight.md: khác file/hành vi/khối lượng và khuyến nghị. Gom thành một câu hỏi cho Hoàng; tiếp tục monitoring/Kafka/log/Boutique qua loopback trong lúc chờ. Không coi probe bỏ qua ingress là bằng chứng đường ingress hoạt động. Không tự mở rộng thành migration Gateway API. Có quyết định trực tiếp của Hoàng thì cập nhật scope cụ thể và thực hiện tiếp, không bắt đầu lại hydration.

## Tài nguyên và phục hồi khi có lỗi

Giữ guard trong báo cáo đã review: MemAvailable WSL <1GiB liên tục 2 phút, PSI memory some avg60 >10, OOMKilled/restart tăng, quota từ chối hoặc rollout/Helm hết timeout là lý do dừng thêm nhóm và chẩn đoán. Không retry mù. Lấy mẫu ngắn có timeout, không chờ chặn hội thoại nhiều phút; có tiến độ và checkpoint nếu cần chờ.

Lỗi quota/config/rollout không tự bắt buộc hỏi Hoàng: tự sửa trong allowlist và thử lại khi có nguyên nhân/bằng chứng. Nếu vẫn cần tăng tài nguyên/giảm scope hoặc không còn headroom thì đưa lựa chọn cụ thể, giữ kết quả PARTIAL thay vì dựng cố toàn stack. Không build image đồng thời với đo baseline; dừng load/build của chính phiên khi gây pressure.

Được scale về 0 đúng Deployment/StatefulSet do lượt này mới tạo, sau khi lưu log/events và record replicas cũ, hoặc dừng tunnel/build của chính phiên để giải áp. Không scale/dừng workload có trước hay hệ thống/S-cool. Không dùng delete -f, Helm uninstall/rollback tự động, --atomic/--cleanup-on-fail hoặc xóa DaemonSet để cleanup mặc định. Đọc hook-delete-policy trước cài: lifecycle tự dọn Job/hook tạm do chính release mới của lượt này tạo được phép nếu đã inventory, không chứa dữ liệu cần giữ và không tác động object có trước. Cơ chế xóa PVC/Secret/CRD hoặc dữ liệu khác ngoài phạm vi phải vô hiệu hoặc trình Hoàng; không xóa namespace, PVC/PV, Secret, CRD, volume/image/cache. Rollback có dữ liệu hoặc tài nguyên có trước cần Hoàng duyệt đúng danh sách.

## Chỉ hỏi Hoàng khi vượt giới hạn này

Gom các quyết định liên quan và đưa phương án/bằng chứng cụ thể; phần độc lập tiếp tục được:
- Xóa dữ liệu/volume, recreate cluster, gỡ release hay can thiệp object ngoài ownership của gói.
- Đổi controller ingress/kiến trúc có ảnh hưởng nghiên cứu; tăng quota/WSL/CPU hoặc đổi profile thí nghiệm/KPI.
- Credential/provider/model, cloud/chi phí, thay máy hoặc cài công cụ toàn hệ thống.
- Cần sửa source ngoài allowlist/logic nghiên cứu, Git publication, nộp bài hay thông báo bên ngoài.

Không coi thiếu API key, LLM hay bài báo là lý do chặn health/rules/lab độc lập. Không tạo secrets giả rồi tuyên bố LLM thành công. Không chạy chaos, attack, chủ động heal/reset, load stress, benchmark KPI hoặc dataset chính thức trong gói restore này.

## Báo cáo trả Codex

Dùng một file chính lab-restoration.md thay vì một báo cáo cho mỗi lệnh. Có: HEAD/dirty đầu-cuối; file sửa thật; chart/image versions/digests; topology và những gì deferred; resource/admission + usage trước/sau/đỉnh; lệnh/exit/failure; kiểm chức năng và bảo toàn dữ liệu; cách dựng lại không cần hỏi người viết; quyết định đã chốt và phần chờ; điều kiện còn thiếu trước Done. Raw output dài không chứa secret có thể nằm trong scratch, nhưng trích phần đủ review vào evidence bền vững, không chỉ link scratch của phiên.

Kết thúc khi có gói đã kiểm chứng để review hoặc có blocker thật vượt phạm vi cùng phương án quyết định. Đừng dừng chỉ vì đã xong một component. Codex review theo hành vi và rủi ro của diff cuối; không tự coi các PASS cũ thay kiểm chứng revision mới.
