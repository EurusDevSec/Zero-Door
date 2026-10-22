# Issue — Fixture và executor SQL injection

[Milestone R2](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection). Nguồn đối chiếu: `R2-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R2-T01-S01 | Chốt fixture nghiệp vụ giả lập, dữ liệu giả, route vulnerable/safe và nguồn IP. | AC của [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection) |
| R2-T01-S02 | Triển khai fixture/database nhẹ và đường ingress quan sát được. | [ZER-41](https://linear.app/zero-door/issue/ZER-41/dung-sqli-fixture-va-route-quan-sat-trong-lab) |
| R2-T01-S03 | Bổ sung executor SQLi bằng template và giới hạn đã chốt. | [ZER-42](https://linear.app/zero-door/issue/ZER-42/bo-sung-executor-sqli-co-gioi-han) |
| R2-T01-S04 | Chứng minh tác động SQLi, log và phân biệt lưu lượng tấn công với benign. | AC của [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R2-T01-S01

Thiết kế fixture, tiêu chí tác động SQLi và cách liên hệ với luồng microservices.

### R2-T01-S02

Fixture hoạt động, route/query/log được kiểm chứng; phiên bản đóng gói.

### R2-T01-S03

Payload hợp lệ chạy được; tham số ngoài phạm vi bị từ chối.

### R2-T01-S04

Kết quả trước/sau, truy vết request, IP đáng tin cậy và traffic đối chứng.

## Phụ thuộc cần đối chiếu

[R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md), [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [R1-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md) (mục nguồn trong ghi chú).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## Gói tiếp theo cho Claude — ZER-13 AC-01 + ZER-41 chuẩn bị offline — 22/10/2026

### Mục tiêu và thẩm quyền

Hoàng đồng ý chuẩn bị bước R2 sau khi G1 đã nghiệm thu. Gói này cung cấp thiết kế đề xuất và phạm vi để Claude làm fixture cùng kiểm offline; không tự khóa quyết định nghiên cứu, chạy lab hoặc nghiệm thu issue. Claude làm một gói xuyên suốt, Codex review độc lập. Không giao riêng vài test rồi yêu cầu Hoàng ráp lại.

AC sống đã đọc ngày 22/10/2026 qua connection linear_zero_door, đúng project P-ZER-1. ZER-13 có AC-01 thiết kế, AC-02 fixture (ZER-41), AC-03 executor (ZER-42), AC-04 effect/benign/trace/IP. Cả ba issue đang Backlog tại lúc đọc; snapshot này không thay board. ZER-6/9/12 đã Done; R1/G1 đã PASS, [PR #28](https://github.com/EurusDevSec/Zero-Door/pull/28) đã merge. G2 còn ba vector và phối hợp/cleanup; gói này chỉ khởi đầu nhánh SQLi.

Baseline Codex lúc chuẩn bị: HEAD 4ccd6c324f0e1dbde8bff351ea808efe5361bb00, origin/main 5a87e1c487cb64ea030e17e3817321091357c607; nhánh zer-11-g1-acceptance. Có 9 file tracked dirty và 2 untracked trước gói; giữ nguyên. Baseline tại scratch/zer13/intake.json. Claude phải đọc lại Git thật trước khi viết, không coi HEAD này là bất biến. Nhánh triển khai đề xuất zer-13-sqli-fixture từ main đã xác minh; không reset/stash/xóa dirty để chuyển nhánh.

Quyền của lượt Codex chuẩn bị: chỉ nối ghi chú này, thêm pointer NOW và scratch. Khi Hoàng chuyển prompt giao việc dưới đây, phạm vi Claude là nguồn fixture mới, kiểm offline và tài liệu theo allowlist. Chưa có quyền build/import Docker, kubectl/Helm, phát Kafka, gọi agent/LLM/API trả phí, cloud, commit/push/PR/merge, đổi Linear hoặc gửi tin. Không mở lab chỉ vì fixture/test offline đạt. Hoàng giữ quyền chốt thiết kế/nghiệm thu và phạm vi runtime sau review.

### Thiết kế đề xuất để triển khai và review cùng một gói

1. **Vai trò:** một dịch vụ catalog thử nghiệm Python + SQLite, dữ liệu e-commerce giả, bổ sung bên cạnh Boutique. Boutique giữ nguyên checkout và availability. Đây là lỗ hổng cố ý trong fixture, không phải lỗ hổng của Boutique. Không gọi dịch vụ ngoài lab, dùng dữ liệu thật hay viết lại frontend Boutique.
2. **Nghiệp vụ:** seed catalog nhỏ, xác định trước, gồm hàng được phép thấy và hàng không được phép thấy theo điều kiện truy vấn. Hợp đồng query/response ổn định, có ID bản seed và baseline số hàng. Tiêu chí effect là truy vấn vượt điều kiện truy cập và trả đúng hàng giả vốn bị giới hạn; HTTP 200 hoặc xuất hiện chuỗi SQL trong log không đủ. Không cần destructive SQL, shell, arbitrary SQL endpoint, tải lớn hoặc quét target.
3. **Safe/vulnerable:** cùng giao diện GET /fixture/catalog/search và cùng seed trên hai profile cấu hình. Safe dùng tham số ràng buộc; vulnerable là đúng điểm lỗi query được mô tả rõ, chỉ bật bằng opt-in lab. Cùng input lành phải cho kết quả tương đương. Mặc định safe; cấu hình không hợp lệ phải từ chối khởi động. Không đưa tên variant, case, lịch fault hay đáp án vào header/log O để giúp detector. Giữ mapping profile trong H. Fixture không tự phát EFFECT_CONFIRMED hay CONTAINMENT_VERIFIED.
4. **Giới hạn:** đường search chỉ đọc catalog, một statement, có giới hạn kích thước request/response, số hàng, thời gian query và concurrency. Không cung cấp API chạy truy vấn tùy ý. CRUD probe dùng bảng riêng với truy vấn tham số; chặn ghi ngoài thư mục DB cấu hình. Reset chỉ cho dữ liệu fixture thuộc run, không có reset toàn cluster.
5. **Probe:** giữ POST /fixture/orders, GET /fixture/orders/{order_ref}, DELETE /fixture/orders/{order_ref} tương thích measurement.flows.fixture_spec. Response gồm order_ref/item/note/status=STORED; note echo nonce, order_ref mới; commit rồi đọc lại qua kết nối DB độc lập. Cleanup chỉ xóa record của sample đã chứng minh sở hữu; việc xóa nhầm nonce/ID khác phải bị từ chối. /health chỉ là process; readiness kiểm được DB. Không sửa measurement engine để ép fixture qua.
6. **Đóng gói:** ưu tiên Python standard library + SQLite để không thêm framework/dependency khi chưa cần. Một image recipe pin base như quy ước repo, chạy non-root, giới hạn CPU/RAM, filesystem readonly ngoại trừ volume DB. Đề xuất namespace riêng zd-sqli-lab, ClusterIP, default-deny và chỉ đường ingress/probe được chỉ định; không NodePort/LoadBalancer/public host. Namespace và tài nguyên runtime còn phải được duyệt theo inventory; không tự mở rộng command allowlist target-app của worker trong gói này.
7. **Ingress:** chuẩn bị manifest Ingress class traefik cho /fixture với Service fixture cùng namespace, không chỉnh catch-all Boutique hoặc values Traefik chung. Không giả định middleware CRD: kubernetesCRD hiện tắt. Manifest chỉ là đầu ra offline; tạo route mới vẫn cần quyền lab. Đường truy cập từ host khi chạy sau này phải giới hạn loopback/đường lab được duyệt, không công khai fixture dễ tổn thương.
8. **IP:** lưu tách TCP peer quan sát tại fixture, ClientHost của ingress, IP client suy ra, phương pháp/độ tin cậy và request ID. Không coi peer Traefik là IP attacker, không tin X-Forwarded-For/Forwarded do client tự khai. Chỉ chấp nhận metadata proxy khi peer/proxy chain được cấu hình hẹp và có kiểm chống giả mạo; thiếu căn cứ thì IP UNKNOWN. K3d/serverlb có thể NAT, nên host port-forward không chứng minh hai client riêng. Chuẩn bị phép kiểm runtime từ hai nguồn lab tách biệt: phải chứng minh nơi thực thi block sau này thấy được danh tính nguồn; không hứa NetworkPolicy sau proxy chặn riêng được client.
9. **Trace/log:** stdout JSON có server request ID duy nhất, method/path/status, thời lượng, peer/proxy trust và kết quả query có giới hạn. Không log token/cookie/auth hay toàn bộ header. Phân biệt request ID tự cấp với correlation ID client cung cấp; kiểm độ dài/định dạng, chống newline/log injection. Metadata thật quan sát được vào O theo event contract; seed/variant/expected/onset/ground truth chỉ H. Log query có thể lưu template và tham số giả có giới hạn, không lộ bảng đáp án. Pipeline Fluent Bit/ES hiện tại là consumer dự kiến, chưa chứng minh nhận namespace mới.
10. **Liên hệ R3:** chuẩn bị contract để ZER-46 kiểm nguồn thử nghiệm bị từ chối nhưng nguồn benign vẫn đọc/ghi được. SQLi containment và business availability của fixture/Boutique báo riêng. Gói này không implement block IP/healer, không claim containment, MTTD/MTTR hoặc AI tốt hơn.

Nếu khảo sát nguồn cho thấy một lựa chọn trên không phù hợp, sửa đề xuất kèm lý do trong chính mục này và gom quyết định cần Hoàng chốt khi bàn giao. Không âm thầm thay AC, mô hình effect hoặc ranh giới H/O. Thay đổi kiến trúc có hệ quả vượt phạm vi thì tiếp tục phần độc lập, báo điểm cần quyết.

### Nguồn cần đọc có trọng tâm

- [SCOPE](../../SCOPE.md), [scenario-design](../../reference/scenario-design.md), [WORKFLOW](../../WORKFLOW.md), WORKING-AGREEMENT và AGENTS hiện hành.
- [Event contract](../../../design/r1-event-contract.md), nhất là H/O, nguồn phát effect/containment; định nghĩa SQLi theo [ZER-32](../../../evidence/ZER-32/requirements-and-kpi.md) và thiết kế đối chứng ZER-8, chỉ các mục liên quan.
- agent-orchestrator/measurement/flows.py: fixture_spec và kiểm ownership; không sửa nguồn trong gói này. Interface hiện ghi SYNTHETIC; chỉ sau quan sát thật mới đổi provenance ở plan tương ứng, không sửa evidence R1.
- docs/evidence/ZER-10/runtime-01/acceptance.py: Fixture tại dòng 38–79 là tham khảo CRUD lịch sử, không được sửa/copy nguyên harness thành production service. File này tự nêu rõ không có SQLi và không hoàn thành ZER-41.
- infrastructure/helm-values/traefik-values.yaml: forwardedHeaders.trustedIPs rỗng, insecure=false; ingress CRD tắt; access log ClientHost là TCP peer mà ingress thấy. infrastructure/manifests/target-app-ingress.yaml là route hiện tại, chỉ đọc.
- GitNexus zero_door đã được tra để điều hướng, index đang chậm 4 commit; Codex đã đối chiếu trực tiếp các nguồn trên. Không dùng kết quả graph hoặc manifest render làm runtime proof.

### File/action scope của Claude

Trước sửa, ghi HEAD/dirty và danh sách file dự kiến cụ thể vào mục intake cuối ghi chú này. Phạm vi được tạo/sửa:

- services/sqli-fixture/{app.py,requirements.lock,Dockerfile,README.md}: fixture, lock nếu thực sự thêm dependency, cách chạy local; không thêm requirements rỗng cho đủ số file.
- tests/test_sqli_fixture.py và tests/fixtures/zer41/: regression, seed/expected, plan probe của fixture thật (offline provenance). Có thể tách tests/test_sqli_fixture_http.py nếu cần phép kiểm loopback độc lập.
- infrastructure/manifests/sqli-fixture.yaml: bộ Namespace/ServiceAccount/ConfigMap/Deployment/Service/NetworkPolicy/Ingress chỉ cho fixture; không Secret có giá trị thật, không apply.
- docs/runbooks/sqli-fixture.md: chạy offline, preflight và đề xuất runtime/cleanup có budget để xin một lần sau review; không biến runbook thành quyền thực thi.
- docs/evidence/ZER-41/verification.md: một báo cáo ngắn AC → kiểm → kết quả/giới hạn và danh sách source/hash của đúng gói; không làm nhiều báo cáo trùng nội dung.
- Ghi chú sqli-fixture.md này chỉ nối handoff/đính chính rõ ràng; NOW.md chỉ thêm pointer mới; scratch/zer13/claude/ cho log/test tạm.

Mọi file khác chỉ đọc, đặc biệt raw/evidence R0/R1, measurement/event pipeline, agents, chaos-worker, Traefik values và CI chung. Nếu cần consumer/CI delta thật để đạt AC, nêu diff/file scope đề xuất; chưa tự sửa ngoài gói. Không hash lại toàn bộ repo hoặc tạo framework checker mới. Bảo vệ dirty hiện có, baseline các nguồn trực tiếp dùng và source manifest đúng gói là đủ. Snapshot nguồn fixture trước sửa mỗi vòng sau để có fail-before thật, không chỉ mutant thay thế.

### Kiểm và điều kiện nghiệm thu

- Chạy HTTP loopback → SQLite thật: seed tái tạo được; benign safe/vulnerable tương đương; fixed toy case vượt điều kiện trên vulnerable nhưng safe không trả hàng bị giới hạn. Expected tính trước khi viết assertion. Không nhận stdout SUCCESS làm oracle.
- Kiểm CRUD bằng Flow/fixture_spec hiện tại: create → độc lập read/đối chiếu → owned cleanup; thêm case DB lỗi/lock, nonce sai, record người khác, request quá lớn và malformed input. Giữ lỗi thật; không retry tới xanh hoặc chỉ sửa expected theo output.
- Kiểm parser trust bằng fake peer/proxy: header giả không thành trusted client IP; proxy chain sai/không xác định ra UNKNOWN. Đây chỉ là kiểm logic offline, không chứng minh NAT/NetworkPolicy thực.
- Parse/render manifest và kiểm effective env, Service selector/port, volume/write permissions, securityContext, NetworkPolicy và route /fixture không chiếm /. Không cài công cụ mới hoặc gọi cluster để render. Dockerfile/image chưa build phải ghi NOT_BUILT, không gọi là image đã kiểm.
- Chạy các regression trực tiếp bị ảnh hưởng; không chạy lại toàn bộ R1 hoặc yêu cầu mutant/clean checkout ở mỗi thay đổi nhỏ. Cuối gói kiểm một lần từ môi trường sạch phù hợp nếu khả dụng, ghi thiếu dependency/công cụ trung thực.
- Runtime đề xuất phải có context, namespace, số tài nguyên, trần thời gian/request/storage, nguồn IP, rollback/cleanup/ownership, raw cần giữ, và stop conditions. Chưa chạy trong gói offline. Cleanup lỗi/không xác minh phải UNKNOWN/UNRESOLVED, không CLEAN.

Bàn giao một lần gồm thay đổi, lệnh kiểm/kết quả thật, failure/UNKNOWN, AC-01 thiết kế đề xuất và những quyết định còn cần chấp nhận; ZER-41 vẫn PARTIAL khi thiếu image/ingress/log/IP runtime. ZER-13 AC-03/04 và ZER-42 chưa được gói này hoàn thành. Verdict phù hợp READY_FOR_CODEX_REVIEW_OFFLINE, không Done. Codex sẽ review source cùng interface probe/ingress/H-O, tự chạy phản ví dụ rồi gom finding; sau sửa gom mới chuẩn bị một lượt lab có quyền riêng.

### Bàn giao Codex chuẩn bị

Đã đọc AC live của ZER-13/41/42 và toàn bộ các issue R2 để chọn đúng thứ tự thiết kế → fixture → executor → tác động. Chỉ thêm gói này và pointer NOW, không sửa source/lab/Linear/Git publication. Trước khi Claude viết, Hoàng chuyển prompt ở chat; Codex nhường writer trong lúc Claude thực hiện. G1 receipt và mọi giới hạn R1 được giữ nguyên.

## Intake Claude — ZER-13 AC-01 + ZER-41 offline — 22/10/2026

Đọc lại Git trước khi viết: HEAD `4ccd6c324f0e1dbde8bff351ea808efe5361bb00` (nằm trong origin/main `5a87e1c`, diff rỗng), nhánh `zer-11-g1-acceptance`, staged rỗng, 10 file tracked dirty + 2 untracked như baseline Codex; không đổi nhánh vì có dirty ngoài phạm vi. Lượt trước bị dừng không tạo file nào trong phạm vi. Hash dirty và nguồn chỉ đọc trực tiếp dùng: `scratch/zer13/claude/intake.json` (`intake.py --check` để so). Bản ghi chú/NOW trước sửa: `scratch/zer13/claude/before/`.

File dự kiến tạo: `services/sqli-fixture/{app.py,Dockerfile,README.md}` (chỉ stdlib, không `requirements.lock`), `tests/test_sqli_fixture.py`, `tests/fixtures/zer41/{seed.json,expected.json}`, `infrastructure/manifests/sqli-fixture.yaml`, `docs/runbooks/sqli-fixture.md`, `docs/evidence/ZER-41/verification.md`; ghi chú này chỉ nối, NOW chỉ thêm pointer; tạm ở `scratch/zer13/claude/`. Không build image, không kubectl/Docker/Kafka/agent/model, không commit/Linear, không làm executor ZER-42.

## Bàn giao Claude — ZER-13 AC-01 + ZER-41 — READY_FOR_CODEX_REVIEW_OFFLINE — 22/10/2026

Gói ở [docs/evidence/ZER-41/verification.md](../../../evidence/ZER-41/verification.md): AC → kiểm → kết quả, lệnh, residual, source + hash. HEAD `4ccd6c3`, staged rỗng, dirty ngoài phạm vi giữ nguyên; intake + hash `scratch/zer13/claude/intake.json`.

- **AC-01 (thiết kế, đã triển khai):** dịch vụ catalog thử nghiệm `services/sqli-fixture/app.py` (chỉ stdlib + SQLite, dữ liệu thương mại giả), bổ sung cạnh Boutique, không gọi ngoài lab. Một interface `GET /fixture/catalog/search` trên hai profile cùng seed: `safe` (parameter binding, mặc định) và `vulnerable` (nội suy chuỗi, chỉ bật bằng `ZD_SQLI_PROFILE=vulnerable`). Tiêu chí effect = trả hàng `restricted` mà truy vấn lành không bao giờ trả; HTTP 200 không phải oracle. Cả hai profile chạy trên kết nối read-only, một statement, có trần hàng/độ dài/thời gian, nên injection chỉ đọc được hàng giả.
- **Probe CRUD** tương thích `measurement.flows.fixture_spec` (không sửa flows): create → đọc lại trên kết nối độc lập → cleanup chỉ record đã chứng minh sở hữu bằng nonce; xóa theo ref tham số hóa.
- **Nguồn IP (logic):** không tin header client tự khai; peer trực tiếp là nguồn, XFF giả bị bỏ; chỉ tin forwarded qua proxy đã cấu hình hẹp, thiếu căn cứ thì UNKNOWN.
- **Log:** stdout JSON có request id tự cấp, method/path/status/thời lượng, peer + phương pháp/độ tin cậy nguồn, số hàng; không in profile/variant, cookie/auth/header đầy đủ; correlation id client bị kiểm/giới hạn chống log injection.
- **Đóng gói (offline):** `services/sqli-fixture/Dockerfile` (distroless pin digest, non-root, NOT_BUILT) và `infrastructure/manifests/sqli-fixture.yaml` (Namespace `zd-sqli-lab`/SA/ConfigMap mặc-định-safe/Deployment readonly-root + `/data` emptyDir/Service ClusterIP/NetworkPolicy default-deny + 1 allow/Ingress traefik `/fixture`, không Secret, NOT_APPLIED). Runbook `docs/runbooks/sqli-fixture.md`.
- **Kiểm:** `tests/test_sqli_fixture.py` 30/30 trên hai pin production; `docs/evidence/ZER-41/check_manifest.py` OVERALL PASS (OpenAPI pin + ngữ nghĩa cô lập); Bandit `-lll -iii` exit 0 (app.py sạch mọi mức). Expected khóa ở `tests/fixtures/zer41/expected.json` trước khi viết assertion. Consumer flows (`test_measurement_{probe,boundaries,recovery}`) vẫn đạt.
- **PARTIAL / residual:** image NOT_BUILT, manifest NOT_APPLIED; nguồn IP chỉ kiểm logic (chưa chứng minh NAT/forward Traefik/NetworkPolicy chặn nguồn, cần hai nguồn lab tách biệt); định dạng Event/log thật, HPA/containment, consumer Fluent Bit/ES nhận namespace mới đều chưa kiểm offline. ZER-13 AC-03/04 và ZER-42 không thuộc gói.
- **Cần Hoàng chốt:** duyệt budget runtime `zd-sqli-lab`; xác nhận tiêu chí effect SQLi (F-05) mà fixture mã hóa (lộ hàng restricted) trước khi khóa cho chấm điểm.

Không commit/push/PR, không build/apply, không Docker/Kube/Kafka/agent/model, không đổi Linear, không Done. Writer trả Codex review độc lập; sau sửa gom mới chuẩn bị một lượt lab có quyền riêng.


## Codex review — ZER-13/41 — CHANGES_REQUIRED offline — 22/10/2026

Đã review trọn nguồn fixture/test/manifest/recipe/runbook và consumer trực tiếp; bộ 30 test trên hai pin và checker manifest đều PASS. Phản ví dụ loopback/SQLite/policy xác nhận 8 nhóm sửa: ZR41-01 log stderr lộ profile; 02 request lifecycle/HTTP framing sai ID và thừa request; 03 giới hạn admission/transport/query; 04 lỗi DB/result/disconnect mất hoặc sai observation; 05 startup xóa DB có sẵn; 06 nhầm peer proxy thành client; 07 policy cho cả kube-system; 08 kế hoạch runtime thiếu tổng budget/ownership. Chi tiết, vị trí và regression trong [codex-review](../../../evidence/ZER-41/codex-review.md).

Gói sửa gom theo mục cuối báo cáo, trong phạm vi offline cũ; snapshot before và probe của Codex chỉ đọc tại scratch/zer13/codex-review. Không thay tiêu chí expected để ép PASS, không mở ZER-42/measurement/CI chung. Sau Claude sửa, Codex retest trọng tâm rồi mới chuẩn bị một lượt lab có quyền riêng. ZER-13 AC-01 còn đề xuất, ZER-41 PARTIAL; F-05/IP/runtime cần nghiệm thu đúng bằng chứng. Không sửa source, build, lab/model, publication hoặc Linear trong review. Writer nhường Claude sau Hoàng chuyển prompt.

## Sửa gom Claude fix01 — ZR41-01…08 — READY_FOR_CODEX_RETEST_OFFLINE — 22/10/2026

Đã sửa gom 8 finding của Codex ([codex-review.md](../../../evidence/ZER-41/codex-review.md)) trong ranh giới service/packaging; báo cáo cập nhật ở [verification.md](../../../evidence/ZER-41/verification.md) mục "Fix round fix01". HEAD `4ccd6c3`, staged rỗng, dirty ngoài phạm vi và report/probe/snapshot của Codex giữ nguyên (chỉ đọc); intake `scratch/zer13/claude-fix01/intake.json`.

- **ZR41-01:** banner khởi động trung tính, profile/seed/db không ra stdout lẫn stderr (Fluent Bit tail cả hai).
- **ZR41-02:** một request một kết nối (`Connection: close`); id/thời lượng theo từng request; thân khai báo được đọc hoặc xả nên byte thừa không tái phân tích thành request khác (chống smuggling).
- **ZR41-03:** chặn số kết nối (64), deadline transport 5s, deadline-trước-khi-chờ slot DB (bận → 503 nhanh), gate ghi riêng, cap độ dài giá trị SQLite.
- **ZR41-04:** mỗi request đã phân tích ra đúng một bản ghi kết thúc; SQL sai 4xx vs DB khóa/mất 503 (theo tên lỗi SQLite); kết quả không-vô-hướng → 422; method lạ → 405 có cấu trúc; client ngắt → bản ghi trung thực, không thành công giả.
- **ZR41-05:** `open_or_create` tái dùng DB tương thích (seed id trong bảng `meta`), không unlink trước khi bind; DB lạ từ chối khởi động; `reset_orders` tường minh, chỉ bảng orders.
- **ZR41-06:** `ZD_SQLI_TOPOLOGY`: `proxied` (mặc định) không gán peer thành client khi chưa có chuỗi proxy tin cậy → UNKNOWN; peer quan sát ghi riêng; ConfigMap đặt `proxied`.
- **ZR41-07:** NetworkPolicy allow kèm `podSelector app.kubernetes.io/name=traefik` cùng namespaceSelector trong một peer; checker kiểm ngữ nghĩa (traefik vào, pod kube-system khác bị chặn); preflight kiểm nhãn thật.
- **ZR41-08:** runbook §4 viết lại envelope runtime (context k3d-zero-door, trần thời gian/request/lưu trữ/retry, hai nguồn lab, kiểm soát profile, receipt nguồn, namespace create-if-absent + owner UID + abort nếu không sở hữu, teardown chỉ tài nguyên sở hữu; stop condition sửa lại; `emptyDir.sizeLimit: 64Mi`).

Fail-before trên chính snapshot `before/` của Codex (trùng byte app đã review): suite cập nhật FAIL ở snapshot, PASS ở bản sửa. `NEMESIS=… bash docs/evidence/ZER-41/fix01/fail_before.sh <dir>` → trước: main FAILED(6/12), http FAILED(5/3), checker fail; sau: main OK(37), http OK(8), checker OVERALL PASS. Kiểm: suite 37/37 + 8/8 trên hai pin, manifest PASS, Bandit `-lll -iii` 0, consumer flows đạt.

PARTIAL giữ nguyên: image NOT_BUILT, manifest NOT_APPLIED; nguồn IP chỉ logic (cần hai nguồn lab chứng minh NAT/forward/chặn nguồn); Event/log thật, HPA/containment, Fluent Bit nhận namespace mới chưa kiểm. AC-03/04 + ZER-42 ngoài gói. Cần Hoàng chốt envelope `zd-sqli-lab` và tiêu chí effect F-05. Chưa lab/build/model/commit/Linear. Writer trả Codex retest.


## Codex retest fix01 — ZER-13/41 — CHANGES_REQUIRED_OFFLINE — 22/10/2026

[Retest](../../../evidence/ZER-41/codex-retest01.md): main37 + HTTP8 trên cả hai pin và manifest PASS; fail-before replay đúng, 40 nguồn Codex/10 dirty được bảo toàn. Còn ba nhánh gốc cần sửa gom: FX41-R1 timeout chỉ idle nên body nhỏ giọt vượt 5s; FX41-R2 method chưa liệt kê (TRACE) rơi 501 HTML/không record; FX41-R3 startup mismatch seed in traceback ra stderr. Các sửa framing/DB reuse/proxy/selector đã đạt offline. Runbook cần chốt phase/cleanup/total-attempt cap trước xin lab. Gói sửa nhỏ trong app/test/docs hiện hữu; snapshot fix01 ở scratch/zer13/codex-retest01/before/app.py; giữ review/probe/snapshot read-only. Không source edit/lab/build/model/publication/Linear. ZER-41 PARTIAL, F-05/runtime envelope chưa nghiệm thu.

## Sửa gom Claude fix02 — FX41-R1…R3 — READY_FOR_CODEX_RETEST_OFFLINE — 22/10/2026

Sửa 3 nhánh còn lại theo [codex-retest01.md](../../../evidence/ZER-41/codex-retest01.md) và làm rõ trần runtime; chi tiết ở [verification.md](../../../evidence/ZER-41/verification.md) mục "Fix round fix02". HEAD `4ccd6c3`, staged rỗng; report/probe/snapshot Codex chỉ đọc, dirty ngoài phạm vi giữ nguyên (intake `scratch/zer13/claude-fix02/intake.json`). Không đổi manifest/checker/Dockerfile/seed.

- **FX41-R1:** ngân sách request 3 s là deadline tuyệt đối cho dòng request, header, body và phần xả; tiến độ từng byte không kéo dài được. Request đang tới dở → 408; kết nối không gửi gì → đóng, không bản ghi. Ghi response bị chặn bởi deadline transport tuyệt đối 5 s. Ngân sách đã hết khi tới DB → `503 DEADLINE_EXCEEDED`, không còn gắn nhầm BUSY.
- **FX41-R2:** một ranh giới quan sát cho mọi method không hỗ trợ (kể cả TRACE, FOO, HEAD) và mọi lỗi parser (400/414/431/505): JSON có `X-Request-Id`, đúng một bản ghi, đóng kết nối.
- **FX41-R3:** startup thất bại in một dòng trung tính `{"event":"startup_failed","reason":…,"setting":…}` và thoát khác 0; không traceback, đường dẫn, seed id hay giá trị đã thử; DB hiện có giữ nguyên. Lỗi luồng request chỉ ghi tên loại lỗi.
- **Nhánh cùng nguyên nhân tự tìm thấy:** request bị cắt giữa dòng đầu làm đường trả lời crash và mất bản ghi; đã sửa và có test.
- **Runbook §4:** phút cho từng pha, tổng 30 phút, trong đó dự trữ cleanup 7 phút; một trần tổng 4000 lượt HTTP tính mọi profile, nguồn, thao tác và retry; "3 retry" = tối đa 4 lượt; kiểm binding host chỉ đọc trước khi bật profile vulnerable.
- **Fail-before hành vi trên snapshot fix01 của Codex:** chỉ 16 ca mới hỏng (main 7, http 9), mọi ca cũ vẫn đạt.
- **Sau sửa:** main 42/42 và http 15/15 trên hai pin; replay `edges` đã thích nghi: 408 lúc 3,0 s, TRACE → 405 JSON, startup chỉ `DB_INCOMPATIBLE`. Manifest PASS, Bandit `-lll -iii` 0, consumer flows đạt.
- **Lỗi ngắt quãng đã chẩn đoán, không chạy lại cho tới xanh:** ở vòng đầu, 4/8 lượt Nemesis fail vì test đọc log trước khi server ghi bản ghi (bản ghi được ghi ngay sau response). Test giờ chờ có giới hạn và vẫn yêu cầu đúng một 408. Vòng sau 16/16 OK. Log ở `scratch/zer13/claude-fix02/runs/`.

PARTIAL giữ nguyên: image NOT_BUILT, manifest NOT_APPLIED, chưa có bằng chứng sống về NAT/CNI/Fluent Bit/nguồn; deadline phía ghi chỉ kiểm qua code (seed 8 dòng không tạo được response vượt buffer socket). AC-03/04 và ZER-42 ngoài gói; F-05 và envelope runtime chờ Hoàng chốt. Chưa lab/build/model/commit/Linear. Writer trả Codex retest.


## Codex retest fix02 — SOURCE_RETEST_PASS_OFFLINE — 22/10/2026

[Retest](../../../evidence/ZER-41/codex-retest02.md): FX41-R1…R3 đóng offline bằng probe riêng (3 giây / 405 JSON / CLI neutral + DB giữ nguyên). Nemesis42+15, Hephaestus HTTP15; main Hephaestus gặp một race trong test Logs, đã chứng minh record có sau đó; giữ log lỗi, cần đồng bộ test trước CI, không mở lại lỗi chức năng. Replay snapshot7+9 fail đúng hành vi, current42+15 pass; manifest/Bandit/diff-check đạt. Runbook30 phút/cleanup7/4000 attempts rõ. 67 evidence Codex và11 file giữ hash; không sửa source/build/lab/model/Git/Linear. ZER-41 PARTIAL: chuẩn bị một gói runtime, chờ Hoàng chốt F-05 + quyền lab; write-blocked probe chưa chặn được buffer nên không claim proof.


## Codex hoàn tất phần offline và chuẩn bị lab riêng — 22/10/2026

Hoàng giao Codex xử lý phần còn lại. HEAD `4ccd6c3`, staged rỗng; một writer, giữ dirty ngoài gói.
Đọc lại AC sống ZER-13/41 trên Linear Zero Door: vẫn cần runtime route/query/log, chưa Done.
Sửa duy nhất test `Logs.test_no_container_stream_discloses_the_profile`: giữ capture qua chờ có hạn
2 giây và shutdown, yêu cầu đúng hai access record 200/400; không giảm assertion rò profile/correlation ID.
Main42 + HTTP15 PASS trên cả pin Nemesis/Hephaestus. Control cố ý trì hoãn emit300ms tái hiện
StopIteration trên bản trước; bản sửa đạt hai lần mỗi pin. Log tại `scratch/zer13/codex-completion/`.
Manifest gốc PASS, app.py và manifest giữ nguyên hash lúc nhận. Không mở lại package chức năng.

Preflight **chỉ đọc** xác nhận context hoạt động, namespace zd-sqli-lab chưa có; host8080 nghe wildcard
IPv4/IPv6, nên dừng phương án vulnerable qua shared Traefik theo runbook. Chuẩn bị phương án thay thế
ở [runbook §6](../../../runbooks/sqli-fixture.md): Traefik riêng ClusterIP, file-provider /fixture, hai nguồn,
không tạo shared Ingress/hostPort/NodePort, không đổi host firewall/binding. Manifest render14resource
đạt pinned OpenAPI, client hữu hạn kiểm seed/CRUD/nonce/header giả đã parse syntax, **chưa chạy**.
Ảnh proxy pin digest từ controller hiện tại. Giữ30phút/cleanup7/tổng4000fixtureHTTP, không model/target-app.
Đây là profile private riêng, không chứng minh stock shared Ingress đã chạy. Raw phải ghi rõ giới hạn.

Chờ Hoàng chốt F-05 (hàng restricted giả thực trả, không phải HTTP200) + cho phép đúng lượt lab private
đã chuẩn bị. Chưa build/import/apply, chưa thay cluster, chưa commit/push/PR/Linear. ZER-41 PARTIAL;
ZER-42 và AC03/04 của cha không bị đóng theo lượt này. NEXT: duyệt rồi chạy một lượt runtime có giới hạn.


### Hoàng duyệt runtime private và F-05 — 22/10/2026

Phê duyệt trực tiếp trong chat: “Cho phép lượt lab private và chốt tiêu chí effect”. Phạm vi theo runbook §6: k3d-zero-door, 30 phút gồm cleanup7, tối đa4pod/tổng4000fixtureHTTP/12ESquery, namespace chỉ tạo nếu vắng, private Traefik ClusterIP, không shared route/host binding/firewall/target-app/model/publication/Linear. F-05 chốt actual restricted synthetic seed rows, không HTTP200. Codex nhận writer chạy đúng gói và giữ mọi failure/UNKNOWN.


### Codex runtime private — BLOCKED_RUNTIME_ISOLATION — 22/10/2026

[Receipt](../../../evidence/ZER-41/runtime-01/README.md): image build/import đạt, sourceA safe12response ghép ID/status/IP đúng và CRUD cleanup đạt; chưa nguồnB. Attempt01 lỗi private route;02 route chạy nhưng directTCP tới fixture không bị chặn;03 giữ app trong init tới khi thấy rule thực nhưng chốt hết thời gian. Vulnerable chưa bật lần nào, ES0query. Bảo toàn ba failure/script/raw; namespaceUID-conditioned cleanup3/3CLEAN, cuối13m47s tính từ đầu turn. ExacttotalHTTPUNKNOWN do logstream01timeout; không chốt AC/ngân sáchPASS. App/seed/stockmanifestkhông đổi; chưa Git/Linear.

Khoảng trống nằm ở enforcementlabhiện tại, chưa đủ chốt nguyên nhâncontroller. Đã chụp read-only Pod placement/workload/PVCUID/mounts để chuẩn bị đề xuất khôi phục; restartserver0/pauserestoreagents là ngoài quyền namespaceđã cấp và chưa làm. Phải xin gói recoverycụ thể trước hành động có ảnh hưởng. ZER-41 PARTIAL; ZER-13AC03/04/ZER-42 giữ nguyên.


### Đề xuất recovery có ảnh hưởng ngoài namespace — CHƯA ĐƯỢC PHÉP

Gói reviewable trước xin quyền: tối đa35phút,10phút cuối dànhcleanup/restore; snapshotreplica và3PVCUID/mounts đã lưu ở runtime-01/pre-repair-*.json. Tạm scale Gaia/Hephaestus về0 theo baseline, restartduynhất container k3d-zero-door-server-0 mộtlần để khởi tạo lại controllerembedded, đợiAPI/node/workloadReady và đối chiếuPVCUID; không recreatecluster/reset/xóaPVC/volume/manualiptables. Sau đó mới chạy lại privateprofile4pod/4000fixtureHTTP/12ESquery bằngimageđãbuild, chỉbậtvulnerable saukhi rulethực/directdeny/IPsafeđạt. Đếntrần hoặcPVCUIDdrift thì dừng, cleanupđúngUID/nhãn vàrestoreagentsđúngreplicabanđầu. Hiệnservercófrontend,checkout,ESvàagents nênrestartcóthểgâygiánđoạntạm; cầnHoàngduyệtriêng. Khôngcamkếtrestartchắcchắnsửađược; khôngpaidmodel/publication/Linear.


### Hoàng duyệt recovery/retest — 22/10/2026

Phê duyệt trực tiếp: “Cho phép recovery và retest trong phạm vi trên”. Gói35phút/10phútcleanup-restore; pauseGaia/Hephaestus, restartduynhấtserver0mộtlần, PVCUID/replicareadback rồiprivatefixture4pod/4000HTTP/12ESquery. Khôngrecreate/xóaPVC/manualfirewall/paidmodel/Git/Linear. Quyềnchỉdùngcho recovery/retestnày; giữfailurevàcleanupđúngUID/nhãn.


### Phạm vi chuẩn bị CI ZER-41 — 22/10/2026

Bổ sung duy nhất .github/workflows/ci.yml: jobfixtureoffline trên hai lockproductionhiệncó (42main+15HTTP+manifest), build/import-smoke imagefixturemộtmatrixlegkhôngpush. Giữ nguyên ma trận5imageR1 vàtest/libraries cũ; nối jobmới vào publishneeds. Chưa publication/quyềnCIremote; chỉ chuẩn bịdiff và kiểmworkflowcục bộ.


### Codex hoàn tất kỹ thuật ZER-41 private profile — 22/10/2026

[Runtime-02](../../../evidence/ZER-41/runtime-02/README.md) TECHNICALPASSPRIVATEPROFILE:48requestghépđộclập/twosources, safe0vsvulnerable3restricted,4CRUDownedcleanup,48ID/correlationunique, IPthật/spoof/directdenyđạt,2ESsentinels. Sau1serverrestartđượcduyệt, policygatecủađúngPodđạttrướckhibậtapp ởcảhaiprofile. NamespaceUIDcleanupđạt, exactreplica/allPVC3UIDgiữnguyên; restoreCRLFfailđãsửavàgiữlog, hoànkhôiphục496s trong35phút. MộtfrontendGET500saucartrefusedđượcgiữ, saucartcontainerrestartquan sátđượcGET200; khôngclaimuptime.

CIđãchuẩnbịjobr2-fixturehai productionpins+SAST/imagebuildsmokekhôngpush; giữma trậnR1cũ, boundary6/Bandit0/imageimportlocalđạt. Sourcetest57mỗipinđạt, app/Dockerfile/seedkhôngđổi. Pendingquyềnpublication/nghiệmthuprivateprofile, CIremotevàmerge; chưaLinearDone. ParentZER13AC03/04/ZER42chưalàm. Giữdirtyngoàigói, khôngtạoPR/commit/push/merge/chuyểnLineartronglượtnày.


### Hoàng nghiệm thu private profile và cấp quyền chốt ZER-41 — 22/10/2026

Phê duyệt trực tiếp: “Nghiệm thu và cho phép chốt ZER-41 khi CI đạt”. Commit/push đúng fixture, test, CI, runbook/evidence và note trên nhánh zer-41-sqli-fixture; mở PR, chỉ merge sau khi toàn bộ CI bắt buộc đạt, rồi cập nhật riêng ZER-41 Done kèm receipt. Giữ dirty ngoài gói. Không đóng ZER-13/ZER-42, không chạy thêm lab/model. Runtime-02 private profile là phạm vi nghiệm thu; stock shared Ingress chưa được kiểm runtime.

Publication thêm .gitattributes với pattern chỉ ZER-41, theo quy ước ZER-9/10 hiện có: giữ nguyên byte source đã build và raw evidence/checksum; whitespace trong output gốc được giữ, không sửa lịch sử để làm sạch diff.
