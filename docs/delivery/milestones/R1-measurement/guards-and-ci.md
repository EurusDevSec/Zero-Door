# Issue — Giới hạn tác động, kiểm soát lệnh và CI

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci). Nguồn đối chiếu: `R1-T04`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T04-S01 | Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải. | AC của [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci) |
| R1-T04-S02 | Kiểm soát truy cập lệnh, sự kiện trùng và payload sai. | AC của [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci) |
| R1-T04-S03 | Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI. | [ZER-40](https://linear.app/zero-door/issue/ZER-40/khoa-dependency-va-djua-guardcontract-checks-vao-ci) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T04-S01

Cấu hình allowlist cùng phép thử host, port, protocol, redirect và budget; trần thời lượng hiệu dụng không vượt trần vận hành dù maxDuration trong command lớn hơn. Phân biệt duration, executor và attack_effect.

### R1-T04-S02

Phép thử lệnh bị từ chối, schema lỗi và duplicate; log lý do.

### R1-T04-S03

Phiên bản dependency/image và kết quả CI cho các hành vi cần bảo vệ.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## Gói Claude thực hiện ZER-12 — 19/10/2026, 20:47 +07

### Mục tiêu và quyền của gói

Hoàng yêu cầu Codex chuẩn bị để Claude thực hiện ZER-12. Claude làm trọn gói guard, tự review và sửa các lỗi liên quan trước khi trả một lần cho Codex; Codex review độc lập rồi retest phần sửa. Khi Hoàng chuyển prompt, Claude nhận writer duy nhất trên checkout; Codex không sửa song song. Không gửi tin sang phiên/agent khác từ gói này.

Đầu ra: lệnh bị giới hạn tại ranh giới thực thi, caller không có quyền không tạo tác động, duplicate không nhân thao tác, và các kiểm đã triển khai chạy được trong CI. Giữ nguyên outcome/AC của ZER-12 và child ZER-40; không tự đóng hai issue hay G1. Gói ưu tiên này phủ AC-01/02 và phần AC-03 làm được ngay. Mode MANUAL/RULES/AI/B0 và nguồn KPI đầy đủ thuộc ZER-11/ZER-10; phần chưa có phải ghi rõ còn thiếu, không thêm test rỗng để nhận AC-03 đạt.

**Được làm:** sửa mã/test/config dưới allowlist, kiểm offline và loopback bằng fake transport/client, render YAML, đọc Git/Linear/metadata dependency công khai, ghi evidence và bàn giao. Được tạo nhánh local tên **zer-12-command-guards** từ origin/main sau khi kiểm baseline/cây mã và giữ dirty. Không reset/stash/clean/force; nếu nhánh đã có thì kiểm và dùng lại phù hợp. Không cần hỏi lại các sửa nhỏ trong phạm vi.

**Chưa có quyền trong gói này:** commit/push/PR/merge, sửa field/comment Linear, gọi API model/Doppler hoặc đọc secret thật, Docker build/pull/run, truy vấn hay sửa Kubernetes/Kafka/Elasticsearch/Prometheus thật, gửi tải/chaos/heal/reset thật, cài công cụ toàn máy hoặc sửa hạ tầng/cloud. Đây là triển khai và kiểm offline; quyền runtime ZER-9 cũ đã kết thúc sau cleanup. Dependency test dùng môi trường/cache riêng trong scratch; nếu cần tải dependency đã khóa thì dùng registry chính thức, ghi phiên bản; không chạy cài đặt toàn cục.

### Baseline phải đối chiếu khi nhận

Codex chụp HEAD **4bec8ced17a137cdbde446b3066e578fd8935fc4**, nhánh **zer-9-event-pipeline**, staged rỗng. origin/main **c09452ac975ec581bbc2ff1f0fb5ca94f58b5267**, cây mã bằng HEAD; PR24 đã merge và ZER-9 Done. Sau khi tạo nhánh mới từ origin/main, HEAD dự kiến là c09452a; ghi cả baseline nhận và base triển khai, không coi đổi SHA merge là đổi source.

Dirty có sẵn: AGENTS.md; docs/delivery/NOW.md; docs/delivery/README.md; docs/delivery/WORKFLOW.md; docs/delivery/milestones/R1-measurement/README.md; docs/delivery/milestones/R1-measurement/event-contract.md; WORKING-AGREEMENT.md untracked. Không ghi đè hoặc đưa chúng vào sản phẩm ZER-12. Gói Codex chỉ nối note này và thêm con trỏ NOW; staged vẫn rỗng. Snapshot chuẩn bị: scratch/zer12/preparation-baseline.json; snapshot bàn giao sau viết: scratch/zer12/handoff-baseline.json. Đây là snapshot/hashes kỹ thuật, không thay Git/live state lúc nhận. Nếu scratch không có thì tự chụp baseline từ checkout và note hiện tại, không đoán hash.

Khi nhận: đọc AGENTS, delivery README → WORKING-AGREEMENT → NOW; đọc gói này, WORKFLOW, SCOPE và bash-tooling. Đọc AC sống ZER-12/ZER-40 qua **linear_zero_door**, kiểm URL linear.app/zero-door/. Nếu không có kết nối thì dùng snapshot dưới đây, ghi live UNKNOWN và tiếp tục phần offline độc lập; không cài lại connector. Không dùng Linear S-cool/EurusDevSec. Ghi HEAD/branch/status và hash các file sẽ sửa + nguồn bảo vệ trước khi sửa.

### Snapshot AC — đọc trực tiếp Linear ngày 19/10/2026

- **ZER-12 AC-01:** Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải. Cấu hình allowlist cùng phép thử host, port, protocol, redirect và budget; trần thời lượng hiệu dụng không vượt trần vận hành dù maxDuration trong command lớn hơn. Phân biệt duration, executor và attack_effect.
- **ZER-12 AC-02:** Kiểm soát truy cập lệnh, sự kiện trùng và payload sai. Phép thử lệnh bị từ chối, schema lỗi và duplicate; log lý do.
- **ZER-12 AC-03 / ZER-40 AC-01:** Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI. Phiên bản dependency/image và kết quả CI cho các hành vi cần bảo vệ.

ZER-12 không có blockedBy trực tiếp; ZER-40 chờ ZER-37, đã Done. Đọc contract khóa zd-event/1.0.0 ở docs/design/r1-event-contract.md, phép đo ZER-32 và ranh giới H/O/S của ZER-8 khi cần. ZER-9 đã chứng minh transport/auth event, không chứng minh quyền gửi lệnh attack/heal, tác động fault hay recovery. Không sửa schema khóa hoặc lấy khóa writer event làm quyền actuator.

### Điểm nguồn Codex đã đọc — chưa phải kết quả chạy

- chaos-worker/internal/validation/target.go: ValidateURL dùng strings.Contains trên cả URL; URL rỗng được bỏ qua rồi HTTP executor tự dựng URL từ service.
- chaos-worker/internal/attack/executor.go: EffectiveDuration tin maxDuration của message nếu dương, chưa lấy min với globalMaxSec. ParseCommand chỉ Unmarshal.
- chaos-worker/internal/attack/http_flood.go: client mặc định theo redirect; vòng gửi chưa có RPS limiter dù config có DefaultRPS. Phải kiểm budget chung khi nhiều command đồng thời, không chỉ cap từng goroutine.
- chaos-worker/cmd/main.go: nhận message rồi tạo goroutine cho mỗi command; attack context tách khỏi shutdown bằng context.Background. Chưa thấy auth/dedup ở đường gọi này.
- chaos-worker/internal/kafka/client.go: commit message trước khi caller xác thực/thực thi. Cần đối chiếu trạng thái tiếp nhận/duplicate và kết quả không rõ; không tuyên bố exactly-once nhờ Kafka commit.
- Nemesis build_attack_command nâng maxDuration lên ít nhất 120; trigger_attack nâng duration lên ít nhất 90 dù manifest Nemesis là 60. llm-plan phải qua cùng policy, không là đường bypass.
- Nemesis attack/llm-plan/reset và Hephaestus heal/reset có tác động. Hephaestus R1 đã chặn heal/reset bằng 409; phải giữ. Legacy consumer process_alert có cooldown, cooldown không thay dedup theo ID hay xác thực caller.
- CPU stress cleanup dùng context có thể đã bị cancel; có slice commandId[:8]. Chỉ sửa guard/cancel/cleanup/bounds liên quan; chưa sửa thiết kế gây CPU trên đúng workload của ZER-44.

GitNexus dùng để tìm caller, source trực tiếp là căn cứ. Chỉ mục lúc đầu báo chậm 2 commit; Codex đã refresh local --pdg --index-only thành công (9.946 nodes, 26.268 edges, 130 flows); Claude kiểm freshness khi nhận. Không coi graph thiếu caller là đường không tồn tại. Đọc trực tiếp HTTP/Kafka và manifest động.

### File/action scope được sửa

Chọn một tập con của allowlist dưới đây và ghi file plan thực tế trước edit. Thêm file helper/test đúng tên dưới đây được phép; không tạo framework lớn hoặc đổi stack. File cần ngoài danh sách phải nêu lý do và ảnh hưởng, tiếp tục phần độc lập trước khi hỏi Hoàng về mở scope.

| Nhóm | Đường dẫn được sửa / tạo | Giới hạn |
| --- | --- | --- |
| Worker | chaos-worker/cmd/main.go; chaos-worker/internal/config/config.go; chaos-worker/internal/validation/target.go; chaos-worker/internal/attack/executor.go, http_flood.go, cpu_stress.go, pod_kill.go; chaos-worker/internal/kafka/client.go | Guard trước tác động, auth, schema, dedup, duration/load/cancel/cleanup; không thêm vector SQLi hoặc sửa bản chất kịch bản |
| Helper Go mới | chaos-worker/internal/guard/{auth.go,policy.go,ledger.go,dispatch.go} | Các helper nhỏ nếu cần; tách pure policy khỏi client thật để kiểm được |
| Test Go | *_test.go cùng thư mục với các file Go trong hai hàng trên | Fake executor/transport/clock và fake Kubernetes client; không nối broker/cluster |
| Producer/API | agent-orchestrator/{nemesis,hephaestus}/main.py; agent-orchestrator/gaia/main.py | Nemesis: guard/auth/idempotency trước publish và trước gọi model; Hephaestus: ingress/consumer guard; Gaia chỉ producer auth cần thiết, không đổi detector/KPI |
| Helper Python mới | agent-orchestrator/{nemesis,gaia,hephaestus}/command_guard.py | Chỉ helper auth/policy/idempotency cần tích hợp; nếu chia sẻ thì không copy secret/operator key cho mọi actor |
| Tests Python | tests/test_command_guards.py; tests/test_command_guard_integration.py; tests/fixtures/zer12/command-guards.json; tests/test_event_agents.py; tests/test_nemesis_consumer.py | Phải chạy source entrypoint thật với side effects được thay bằng fake; sửa test cũ chỉ khi behavior hợp lệ đã đổi, giữ đối chứng |
| Config render | infrastructure/manifests/{chaos-worker.yaml,nemesis-deployment.yaml,gaia-deployment.yaml,hephaestus-deployment.yaml}; infrastructure/manifests/command-guard-config.yaml mới | Policy/env/Secret reference và storage cần thiết cho ledger; render offline, không apply; không tăng RBAC/quota hoặc thêm quyền cluster-wide |
| Dependency/build | chaos-worker/{go.mod,go.sum,Dockerfile}; agent-orchestrator/{nemesis,gaia,hephaestus,event_pipeline}/{requirements.txt,Dockerfile}; .github/workflows/ci.yml | Pin những dependency/image/tool thuộc đường đã dùng, giữ build context/copy/import đúng và job ZER-9; không sửa event_pipeline logic |
| Tài liệu/kiểm | docs/runbooks/r1-command-guards.md mới; infrastructure/scripts/verify-command-guards.{py,sh} nếu cần; docs/evidence/ZER-12/**; scratch/zer12/** | Script mặc định offline, --help không tác động; evidence có manifest; không ghi receipt live giả |
| Bàn giao | docs/delivery/milestones/R1-measurement/guards-and-ci.md; docs/delivery/NOW.md | Chỉ nối cuối note, thêm con trỏ đầu NOW; giữ nguyên phần đã nhận |

AGENTS và mọi dirty ngoài hai file bàn giao là nguồn bảo vệ. Không sửa docs/design/r1-event-contract.md, docs/evidence/ZER-9/**, docs/evidence/ZER-37/** hoặc event_pipeline/{contract,client,gateway,store,audit,adapters,telemetry}.py. Nếu guard mới thực sự bắt buộc đổi contract đã khóa, dừng phần đó và báo quyết định; không lén thay semantics hoặc tái sinh raw cũ. Không sửa dashboard/static/analysis, report nghiên cứu hoặc các resource lab khác trong gói này.

### Yêu cầu thực hiện và tự review

**1. Policy và target tại ranh giới cuối.** Từ command đến tác động phải có một đường validation rõ, gồm URL được tự dựng khi request bỏ URL. Dùng parser URL; kiểm scheme/hostname/port chính xác, namespace/service hợp lệ, userinfo, host giả ở query/path/fragment, suffix nối thêm, localhost/IP ngoài policy, URL encoded và URL lỗi. Chỉ cho namespace/workload/route khai báo tường minh; field safetyLimits trong message chỉ được thu hẹp, không tự mở rộng allowlist server. Không tin source='nemesis', label hoặc chữ ký để bỏ target/budget check. Redirect bị chặn mặc định hoặc mỗi hop đều qua cùng guard; thử 30x ra ngoài phải chứng minh không có request thứ hai. Không đi qua proxy môi trường hoặc đường dial làm sai target policy; mô tả giả định DNS/cluster tin cậy và kiểm tương ứng, không nhận hậu tố DNS là bảo đảm mọi IP Internet.

**2. Budget thực, không chỉ field.** Trần hiệu dụng không vượt min của yêu cầu hợp lệ, trần command và trần operator. Không nâng duration 1s thành 90s; maxDuration message không nâng trần runtime. Số âm/0, số quá lớn/overflow, loại dữ liệu sai và config sai phải có policy rõ, không âm thầm mở rộng. Giữ trần cấu hình hiện có hoặc thu hẹp, không tự tăng chúng; ghi khác biệt 60s Nemesis/120s worker, không đổi thành ngân sách lab mới. RPS/concurrency/tổng số command đang chạy phải thực sự bị chặn trước/tại dispatch; cap mỗi command không được nhân budget vô hạn khi nhiều message. Đếm cả request lỗi/redirect/retry vào budget thích hợp. Shutdown/cancel dừng phát tác động mới; cleanup có deadline riêng và chỉ chạm resource do chính run tạo, tránh xóa nhầm khi tên được dùng lại. Executor result không chứng minh attack_effect/recovery; lỗi cleanup/timeout không báo SUCCESS sạch.

**3. Quyền và schema xuyên producer/consumer.** Lập bảng ingress → principal/role → validator → tác động: HTTP attack, llm-plan, heal/reset, proxy reset và Kafka worker/healer. Xác thực ở consumer thực thi, không chỉ UI/proxy hoặc producer. Không có cấu hình/key/role hợp lệ thì từ chối mutation; auth phải xảy ra trước gọi model/publish/Kubernetes. Read-only health có thể tiếp tục phục vụ. Dùng cơ chế auth nhỏ, tường minh; message auth phải ràng buộc toàn bộ payload được thực thi, role/purpose và ID/thời hạn, kiểm tamper/replay/cross-role; dùng fixture chung Python→Go để kiểm encoding. Không tự triển khai OAuth/TLS/Kafka ACL toàn cluster. Mỗi actor chỉ có credential cần thiết; operator, command signer và event writer không là một quyền chung. Không commit secret thật, ghi key vào browser/static/localStorage/log, hoặc nhận chuỗi token không rỗng là đã xác thực. Nếu legacy alert không được ký/xác thực an toàn thì chặn đường auto-actuation đó, không tạo bypass 'legacy'. Giữ R1 decision-only và heal/reset409; không bật executor R1 vì guard vừa có.

**4. Duplicate, retry và failure.** ID hợp lệ, payload strict đủ sâu (unknown type/field, JSON sai, duplicate key, NaN/Infinity, quá lớn/quá sâu, ID ngắn không panic). Claim ID atomically trước tác động; cùng ID/cùng payload không chạy lại, cùng ID/khác payload là conflict, concurrent duplicate không lọt. Retry/redelivery và restart không tự phát lại hành động đã nhận; cooldown theo service/action không thay ID ledger. Dùng ledger nhỏ bền vững hoặc cơ chế fail-closed có boundary được chứng minh: trạng thái đang chạy/không rõ sau crash phải chặn replay tự động, không mặc định 'chưa làm'. Trạng thái lỗi/publish result thất bại/ledger I/O lỗi phải kiểm riêng; không tự nhận exactly-once hoặc hồi phục khi chưa có bằng chứng. Bound kích thước/retention/expiry không làm command cũ còn hợp lệ lọt lại. Ghi rõ giả định single owner/replica và cách ngăn hai owner dùng cùng ledger; không tự thêm distributed service. Rejection có reason code và ID/hash phù hợp, không log raw secret hoặc đưa control/ground truth vào O.

**5. CI và pinning trong ZER-40.** Đưa test guard Go/Python và contract/event checks đã có vào CI, fail khi assertion fail, timeout hữu hạn, không nối lab/model. Tái sử dụng docs/evidence/ZER-37/verify_release.py và bộ kiểm ZER-9 phù hợp; không sửa artifact cũ để xanh. Pin các nguồn nổi thực sự dùng: ví dụ range Elasticsearch của Gaia, tool bandit/gosec@latest/trivy-action@master, base/runtime images. Lấy version/digest có căn cứ từ nguồn chính thức hoặc metadata package, ghi nguồn và nền tảng; không bịa SHA/digest hoặc nâng major hàng loạt. Nếu thay build context/module import thì kiểm đúng image copy/smoke và cập nhật caller CI tương ứng. Không bỏ job, giảm severity hoặc cho continue-on-error để nhận PASS. Mode checks đã tồn tại phải giữ; mô tả cụ thể mode behavior còn đợi ZER-11, không khai full ZER-40/AC-03 đã nghiệm thu chỉ từ YAML.

### Kiểm vừa đủ nhưng bắt lỗi thật

Viết bảng case/expected trước sửa cho các ranh giới trên, thêm đối chứng hợp lệ. Các assertion phải kiểm số side effects, target thực, trần thực và state/reason; exit 0 hoặc validator trả nil chưa đủ. Dùng fake Kubernetes/Kafka/model và fake transport/clock; không chạy process stress, xóa pod hoặc flood mạng thật. Loopback ephemeral server được phép chỉ cho HTTP/auth/redirect test nhỏ, tối đa 20 request/case; có cleanup và timeout. Mọi request tác động lab ngoài loopback đều cấm trong gói này.

Tối thiểu có phản ví dụ cho: URL nhét hậu tố hợp lệ vào path/query nhưng host ngoài lab; URL mặc định từ service xấu; redirect ra ngoài; command maxDuration lớn hơn operator; duration nhỏ bị producer nâng; không có RPS cap; command đồng thời nhân budget; unsigned/tampered/wrong-role/expired; valid producer nhưng caller không có quyền; duplicate đồng thời/restart và ID conflict; JSON lỗi/short ID; cancel rồi cleanup; lỗi publish/ledger. Lấy subset test chạy trên baseline để chứng minh fail-before đúng nguyên nhân và control vẫn đạt. Không sửa expected chỉ cho khớp implementation; chỉ dùng mutant nơi cần kiểm failure path khó chạy, ghi rõ giới hạn.

Chạy unit/integration offline liên quan và hồi quy consumer trực tiếp: core event pipeline, regression, source Gaia/Hephaestus HTTP, Nemesis consumer và contract release nếu có phụ thuộc đổi. Lệnh chuẩn Go gồm go test ./..., go test -race ./... khi toolchain hỗ trợ, go vet ./... và build; ghi N/A có lý do nếu Windows thiếu race/CGO, không gọi N/A là PASS Linux. Python dùng đúng interpreter/venv đã chốt, -B; Bash syntax và YAML parse. Không cần lặp mọi kiểm không đổi chỉ để tăng tổng số. Git diff --check và kiểm hash nguồn bảo vệ bắt buộc.

### Bàn giao một gói cho Codex

Tạo docs/evidence/ZER-12/verification.md làm đầu mối, kèm source manifest SHA-256, policy/config thực, bảng AC → case → expected/actual → artifact, lệnh/tool version/timezone/exit code và giới hạn. Log test đầy đủ có thể ở scratch; evidence chia sẻ phải đủ tái chạy, không chỉ trỏ tới scratch đã mất. Ghi test nào fail-before, đối chứng và case failure. Tách rõ offline/build/render với runtime/CI remote chưa chạy; không dùng runtime ZER-9 cũ làm proof guard source mới.

Nối cuối note này: baseline → file thật đã sửa → quyết định policy → kết quả → phần còn thiếu → hash → Codex cần kiểm gì. Thêm con trỏ NOW. So hash toàn bộ nguồn bảo vệ theo snapshot nhận; note chỉ nối, NOW chỉ prepend. Không sửa báo cáo/checker Codex hoặc evidence cũ. Trả writer Codex, không commit/push/Linear; verdict **READY_FOR_CODEX_REVIEW** hoặc **PARTIAL có lý do cụ thể**, chưa phải Done. Nếu một phần bị chặn thì hoàn tất và bàn giao phần độc lập trong cùng gói, không bỏ toàn bộ công việc.

Codex sẽ tự đối chiếu đường gọi thực, tính trần, replay/cross-language auth, race/restart/failure, source/destination I/O boundary của ledger và CI gates. Sau review và sửa gom mới chốt scope runtime/publication cần thiết với Hoàng; không hứa Done trước evidence/merge/nghiệm thu.


## Điều chỉnh gói — thực hiện trọn ZER-12 và ZER-40 — 19/10/2026, 21:05 +07

**Chỉ đạo mới nhất của Hoàng:** làm theo toàn bộ outcome của ZER-12, bao gồm child ZER-40; không chia mặc định thành gói guard trước và CI/mode để sau. Đoạn này thay thế các câu ở gói 20:47 giới hạn “AC-01/02 và phần AC-03 làm được ngay” hoặc mặc định mode phải chờ ZER-11. Các phần baseline, bảo vệ dirty/evidence, quyền offline, test failure và one-writer vẫn áp dụng. Đọc cả gói trên cùng điều chỉnh này trước triển khai; không tiếp tục dùng prompt cũ một mình.

### Bản đồ đầu ra phải làm cùng một gói

| Issue / AC | Đầu ra của Claude |
| --- | --- |
| ZER-12 AC-01 | Guard target/URL/redirect và budget thời gian/tải tại đường thực thi; test hợp lệ, từ chối và failure/cancel |
| ZER-12 AC-02 | Auth/caller role, strict schema và dedup/idempotency; kiểm cả HTTP, Kafka consumer và đường bypass liên quan |
| ZER-12 AC-03 = ZER-40 AC-01 | Khóa dependency/image/tool của đường đã dùng; tích hợp đầy đủ contract, guard và mode checks vào CI; kiểm fail gate và build/import tương ứng |

ZER-40 chỉ đại diện AC-03 của cha. Làm xong child không tự hoàn tất AC-01/02 của ZER-12; trạng thái cha cũng không tự Done. Gói review phải có verdict riêng cho cả ba AC cha và AC child, cùng nguồn bằng chứng dùng chung cho AC-03/child, không nhân bản thành hai việc khác nhau. Không tự thêm blocked-by ZER-11 cho ZER-40: relation sống của child hiện chỉ chờ ZER-37 đã Done.

### Mode checks là phần thực hiện ngay của ZER-40

Không chờ toàn bộ dashboard/probe/scorer. Triển khai policy mode ở ranh giới command/decision/dispatch mà gói guard đang sửa, rồi gọi policy đó trên các entrypoint/consumer thật. Tái dùng semantics đã khóa ở contract mục 7.4 và thiết kế ZER-8; không tạo enum hoặc một bản contract song song.

- B0: ZERO DOOR không phát DECISION/LLM_CALL/GUARD_VERDICT/action heal. Mọi đường tự động hoặc thủ công cố kích hoạt heal phải bị chặn trước side effect. Ghi rejection bằng kênh audit phù hợp; không phát GUARD_VERDICT trong B0 vì chính event đó cũng là MODE_VIOLATION. B0 vẫn có thể được harness gây fault theo kế hoạch; không cấm nhầm mọi ATTACK_REQUESTED của nhóm B0.
- BM/MANUAL: không auto-heal; chỉ chấp nhận đề xuất MANUAL từ operator_console được xác thực, thuộc cùng run/trial và có quyết định vận hành hợp lệ. Chỉ gắn initiator=OPERATOR hoặc caller gửi mode=MANUAL chưa đủ. BM không gọi LLM.
- B1/RULES: đề xuất từ decision_rules hợp lệ, không gọi LLM. B2/B3 theo đúng nguồn quyết định và fallback trong contract; không đổi AI thành RULES rồi coi là quyết định AI.
- Mode/group lấy từ context cấu hình run tin cậy, không lấy field tự khai của request làm quyền nâng cấp. Thiếu context, sai nguồn, sai run/trial, quyết định không có proposal ACTION hoặc chưa được phép thực thi phải fail closed. Unknown group/config không mặc định AUTO.
- Phân biệt nguồn phát fault với quyền heal; mode gate không làm harness fault biến thành healer và không đưa nhãn H/control vào O. Legacy API/consumer không được thành đường vòng qua mode policy.

Test phải quan sát side-effect counter ở đường gọi thật: publish/model/Kubernetes/dispatch đúng bằng 0 ở ca bị chặn. Có ca hợp lệ để chứng minh policy không phải chặn tất cả rồi xanh; với R1 chưa bật executor thì phân biệt “policy hợp lệ” và “executor disabled”, không bật tác động cluster chỉ để có đối chứng. Dùng fake executor cho kiểm dispatch đã được phép trong môi trường offline. Tái dùng contract mode examples để đối chiếu kết quả, thêm test guard khi cần; không chỉ kiểm list enum hoặc YAML có chữ MANUAL.

### Bổ sung file scope cho phần mode và CI đầy đủ

Ngoài allowlist ở gói 20:47, được tạo/sửa:

- tests/test_command_modes.py và tests/fixtures/zer12/modes.json: test policy/entrypoint/consumer B0/BM/B1/B2/B3, unknown context, giả nguồn, quyền và no-side-effect; đưa vào CI cùng guard/contract tests.
- agent-orchestrator/event_pipeline/client.py: chỉ nếu cần thêm khả năng khởi tạo Client cho source guard đã có trong contract; actor key file phải đúng role guard + reader, không mở tập role dùng chung hoặc nới auth cho detector/decision_rules. Có test cross-role và hash/source delta rõ. Các logic contract/gateway/store/audit vẫn bảo vệ như gói cũ.
- infrastructure/manifests/r1-event-pipeline.yaml và r1-event-actors.yaml: chỉ cấu hình render cần cho role guard, mode/context hoặc pin image; giữ việc tách Secret, no H key/token/PVC của actor. Không apply, không sửa raw/rendered evidence ZER-9 cũ.
- docs/evidence/ZER-40/**: được dùng nếu cần đầu ra độc lập cho child, nhưng ưu tiên dùng cùng docs/evidence/ZER-12/verification.md kèm map AC cha/con để không tạo hai gói trùng nội dung. Quyết định một đầu mối rồi liên kết rõ.

Mọi thay đổi client.py do tích hợp guard mới là source revision mới, phải kiểm lại các role/auth/event regression bị ảnh hưởng. Không sửa artifact lịch sử để hash của runtime ZER-9 có vẻ khớp revision mới. Nếu file scope cần điều chỉnh nội bộ cho cùng outcome, ghi rõ trước sửa; không kéo dashboard/UI/scorer hoặc sửa contract khóa vào gói này.

### Ranh giới với ZER-11 và điều kiện bàn giao

ZER-11/ZER-39 vẫn giữ dashboard dùng cùng KPI, bằng chứng vận hành MANUAL/RULES/AI, profile/controller B0, HPA và probe độc lập. Kiểm mode guard/CI trong gói ZER-12/40 không tự nghiệm thu những output đó. Ngược lại, chưa có dashboard hay probe không là lý do tự bỏ mode guard/CI hoặc mặc định AC-03 của ZER-12 chưa triển khai được. Phân biệt thiếu chức năng bắt buộc với thiếu bước QA/publication/runtime có quyền riêng; không tạo dependency cứng giả hoặc nhận offline là runtime.

Claude phải triển khai, tự review, chạy và sửa trọn ba phần trong quyền offline rồi trả **một gói review cho ZER-12 + ZER-40**. Bàn giao kèm dependency/image/tool pins có căn cứ, test/build/render results và workflow chính xác để Codex chạy CI sau publication được duyệt. Không lấy “chưa có quyền push” làm lý do bỏ viết/test CI; không nhận remote CI xanh khi chưa chạy. Nếu thật sự còn thiếu prerequisite để đạt AC thì chỉ rõ ca bắt buộc nào chưa làm được, bằng chứng và quyết định cần thiết; không đặt sẵn PARTIAL vì số issue cha/con hay thứ tự lịch.

Sau review/sửa gom, Codex retest và xử lý các bước kiểm chứng, publication/merge/nghiệm thu trong quyền Hoàng cấp. Claude không tự commit/push/Linear/lab; đoạn này mở rộng outcome implementation của gói, không cấp các quyền vận hành/publication cũ. Chưa đóng ZER-12/40/G1 trước đủ điều kiện. Nhánh vẫn zer-12-command-guards, scope thực tế phải ghi có cả ZER-40.


## Codex nhận triển khai trọn ZER-12/40 — 19/10/2026

Hoàng đồng ý đổi vai: Codex triển khai trong quyền offline của gói 20:47 + điều chỉnh 21:05; Claude review độc lập khi có diff. Claude trả writer, chưa có source delta. Baseline nhận: HEAD c09452ac975ec581bbc2ff1f0fb5ca94f58b5267, nhánh zer-12-command-guards, staged rỗng, 8 dirty tài liệu có sẵn; intake ở scratch/zer12/codex/intake-baseline.json. AC sống hai issue đã đọc qua linear_zero_door, đúng workspace zero-door; đều In Progress, chưa tích AC.

File/action plan trước sửa: worker cmd/main.go, internal/config/config.go, validation/target.go, attack/{executor,http_flood,cpu_stress,pod_kill}.go, kafka/client.go; helper mới internal/guard/{auth,policy,ledger,dispatch}.go và test cùng thư mục. Python: nemesis/main.py + command_guard.py (policy/auth/ledger dùng chung), hephaestus/main.py + command_guard.py (wiring mode, không bật executor); tests/test_command_{guards,guard_integration,modes}.py, fixtures/zer12/{command-guards,modes}.json. CI/pins: .github/workflows/ci.yml, Dockerfile/requirements hiện có của worker và bốn Python image, Go mod/sum chỉ nếu test fake cần dependency có sẵn; manifests chaos-worker,nemesis-deployment,hephaestus-deployment và command-guard-config.yaml (render, không apply). Runbook r1-command-guards.md; verification và source/hash manifest tại docs/evidence/ZER-12/. Note chỉ nối, NOW chỉ thêm con trỏ. Không sửa event contract/store/gateway/adapter, dashboard hoặc evidence lịch sử.

Thiết kế: exact URL/target allowlist; min(request, command cap, operator cap); worker xử lý tuần tự nên một budget hoạt động, không goroutine vô hạn; redirect cấm. Signed envelope bao phủ nguyên bytes payload cùng purpose/expiry; caller operator và signer fault tách khỏi khóa event. Claim bền trước tác động; claim mơ hồ không chạy lại, không tự xóa ledger. Trusted run context cho B0/BM/B1/B2/B3, schema nghiêm, fail closed; legacy healer và reset không được đi vòng R1. Test trực tiếp entrypoint với fake clients và đối chứng hợp lệ. Đây không bật executor R1, không chứng minh fault effect/KPI/runtime.

Bổ sung scope nội bộ cùng AC-03 trước tạo file: requirements.lock cạnh requirements.txt của gaia/nemesis/hephaestus/event_pipeline; tests/requirements-command-guards.{txt,lock}; tests/test_command_guard_ci.py. UV resolve riêng target Linux x86_64/Python 3.11 và hash mọi dependency, tránh pin mỗi package trực tiếp rồi để transitive trôi. Test CI dùng một môi trường offline riêng; image production vẫn giữ dependency riêng. Không cài tool toàn máy.

Bổ sung pin cùng AC-03: tests/requirements-command-tools.{txt,lock} khóa cả transitive của Bandit, dùng riêng cho SAST; không thay dependency production bằng môi trường test.

Môi trường kiểm cuối: test lock chuyển universal để cùng pin/hash chạy được cả Windows local và Linux CI (runtime image locks vẫn target Linux). Python 3.11.9, venv/cache/runtime managed nằm dưới scratch/zer12, không đăng ký Python/PATH toàn máy. Môi trường ZER-9 cũ có phiên bản khác nên chỉ giữ làm kết quả sơ bộ/hồi quy, không gọi là kiểm đúng lock CI.


## Codex bàn giao trọn ZER-12 + ZER-40 — 19/10/2026, 22:33 +07

**READY_FOR_CLAUDE_REVIEW — OFFLINE_PASS.** Codex đã triển khai cả ba AC cha và AC-01 child trong gói điều chỉnh 21:05. [Verification](../../../evidence/ZER-12/verification.md) map cha/con và ranh giới; [source manifest](../../../evidence/ZER-12/source-manifest.json), SHA-256 af4795b884bba7b98f2493db74d90ef0980baabe7a4ebf35493fdfe28fcc4039, khóa 69 source + 25 evidence entries. Checker chỉ đọc PASS: 99 test Python (24 test mới), 17 test Go top-level, ba fail-before đúng lỗi và valid control PASS; vet/Linux binary build bằng Go 1.21.13, Bandit/Gosec, contract release và hồi quy Bash đạt. Python 3.11.9/venv đúng test lock đã kiểm, không dựa venv cũ khác phiên bản.

153/154 nguồn bảo vệ giữ hash, ngoại lệ event_pipeline/Dockerfile đúng scope pin image/lock; không sửa logic pipeline hay evidence lịch sử. Sáu dirty ngoài gói giữ nguyên, note chỉ nối và NOW chỉ thêm đầu. HEAD c09452a, nhánh zer-12-command-guards, staged rỗng. Không commit/push/PR/Linear, không lab/Docker/model/secret thật. Local Go race N/A (CGO=0), remote CI/image smoke chưa chạy.

Tác động: MAC role/purpose/expiry trước dispatch; target/route exact; budget min và shared limiter; ledger claim trước tác động, unknown không tự replay; commit offset sau xử lý/publish; context/mode gate giữ B0/BM không auto-heal. Healer R1 vẫn disabled, lỗi cleanup không giả SUCCESS. Runbook nêu các PVC chưa tạo và application image digest cần seal sau review/build/publication; manifest không phải hướng dẫn apply. Đây không đóng ZER-11/39 hoặc G1, không phải owner acceptance.

### Gói Claude review độc lập (một báo cáo gom)

Hoàng đã đồng ý đổi vai Codex triển khai → Claude review. Khi Hoàng chuyển yêu cầu, Claude nhận writer chỉ cho báo cáo/handoff; source đóng băng tới khi review trả lại. Đọc AGENTS, delivery README/WORKING-AGREEMENT/NOW, gói 20:47 + điều chỉnh 21:05 và verification; kiểm Git/manifest, AC sống qua linear_zero_door nếu có. Không đánh đồng thiếu Docker/CI runtime với thiếu code mode guard; cũng không dùng offline PASS để nghiệm thu runtime.

Được đọc source/contract/evidence liên quan và kiểm offline. Được tạo phản ví dụ trong scratch/zer12/claude-review và docs/evidence/ZER-12/claude-review.md; chỉ nối handoff vào note, thêm pointer NOW. Không sửa product source/test/pins/receipt đã chốt, không commit/push/Linear/lab/Docker/model/secret. Mọi HTTP/Kafka/Kubernetes/model phải fake hoặc loopback có số request nhỏ, không startup client thật.

Review toàn outcome: (1) target/budget/cancel/UID ở đường gọi thật và bypass; (2) role/MAC/schema/duplicate/IO/restart/offset, known rejection vs unknown; (3) B0/BM/B1/B2/B3, proposal/fallback/context/auth provenance, zero side effect cho ca bị chặn; (4) dependency/image/tool pins và gate CI có chạy đúng production paths. Tự dựng vài phản ví dụ, không chỉ chạy checker hoặc tin số test của Codex. Bốn chú thích Gosec G304 phải được xét theo threat boundary cấu hình/volume, không mặc định là finding đã giải quyết chỉ vì SAST xanh.

Trả một bảng finding có priority, file/line, repro expected/actual, ảnh hưởng AC cha/con và hướng sửa; ghi verdict riêng từng AC, không tự Done. Nếu safeguards ngăn một phần review, báo rõ phần chưa kiểm, không giả PASS. Codex nhận findings gom, sửa/retest phần ảnh hưởng rồi mới bàn QA/publication/nghiệm thu theo quyền.

## Claude review độc lập ZER-12 + ZER-40 — 19/10/2026

**CHANGES_REQUIRED.** Báo cáo gom: [claude-review](../../../evidence/ZER-12/claude-review.md). Baseline khớp: HEAD c09452a, staged rỗng, manifest af4795b8…4039, checker PASS. Tôi chạy lại độc lập Go 1.21.13 (test + vet) và Python 3.11.9 đúng test lock, kết quả trùng số của Codex. Đã tự dựng 7 phản ví dụ offline (overlay Go, ASGI với fake); không sửa product source/test/pin/receipt.

P1 — F1: key `ZD_COMMAND_*`/`ZD_OPERATOR_TOKEN_FILE` nằm trong `metadata` của ServiceAccount/ConfigMap, không tới được container, nên đường có guard fail closed và không khởi động được; gate CI manifest bỏ lọt. P2 — F2: producer chưa sẵn sàng sau khi claim để lại UNKNOWN thay vì REFUSED; F3: redelivery sau khi envelope hết hạn trả REJECTED không có commandId, cộng với Ack dùng ctx đã hủy; F4: llm-plan chỉ mở ở B2/B3, ghép nguồn fault theo nhóm, trái với việc tách LLM khỏi benchmark; F5: test entrypoint chạy trên FastAPI/Starlette/pydantic/Kafka khác image. P3: F6–F10, xem báo cáo. Bốn chú thích G304 được chấp nhận theo biên cấu hình/volume, residual TOCTOU ghi rõ.

Verdict: AC-01, AC-02 và AC-03 = ZER-40 AC-01 đều CHANGES_REQUIRED. Chưa kiểm: race, CI từ xa, Docker, kubeconform, PVC, runtime. Linear AC sống chưa đọc lại được vì connector của Claude khác workspace. Checker vẫn PASS sau khi nối note/NOW. Writer trả Codex; Hoàng cần chốt hướng F4. Không commit/push/Linear/lab.


## Codex nhận sửa gom sau Claude review — 19/10/2026

Baseline HEAD c09452a, branch zer-12-command-guards, staged rỗng; source hash khớp manifest af4795b8…4039, Claude chỉ thêm report/note/NOW. Snapshot trước sửa ở scratch/zer12/codex-fix01/baseline.json và before/. Linear Zero Door read-back: ZER-12/40 In Progress, các AC chưa tích. Codex nhận writer cho sửa offline; không Git publication, Linear write, lab/Docker/model/secret.

Scope trước sửa: F1 manifests chaos-worker/nemesis/hephaestus + gate test effective env/schema; F2 Nemesis trigger + ASGI regression known refusal; F3 auth/dispatch/ledger/main Kafka loop + fake shutdown/replay/error regressions; F4 CommandGuard.allow_model và test chặn mọi nhóm benchmark theo contract khóa §2/ZER-8 §4.1 (không thêm context exploration hoặc đổi nghiên cứu); F5 CI matrix lock riêng theo production Nemesis/Hephaestus + dependency equality test, không đổi production dependencies. F6 strict Go exact JSON tags; F7 clock lead tolerance tối đa 2s, expiry giữ nguyên; F8 token purpose/Secret riêng cho heal và cross-role test; F9 ghi residual auto-dispatch chưa bật, không dựng runtime giả; F10 hashed YAML tooling install, build-smoke worker trên PR, disabled worker đợi signal. Có thể thêm test file cùng package, test constraints/locks/matrix checker và runbook.

Giữ nguyên báo cáo Claude, receipt/source-manifest/verification v1 và bằng chứng lịch sử; gói sửa mới dưới docs/evidence/ZER-12/fix-01/. Note chỉ nối, NOW chỉ prepend. Không sửa contract/event pipeline logic/dashboard. Retest phải bắt được failure trước sửa, có positive control, cùng production pins; source sửa cần review độc lập/CI/acceptance trước Done.


## Codex bàn giao sửa gom ZER-12/40 sau Claude — 19/10/2026, 23:28 +07

**READY_FOR_CLAUDE_RETEST — OFFLINE_PASS, chưa nghiệm thu/Done.** [fix-01](../../../evidence/ZER-12/fix-01/README.md) có finding→fix→case, before snapshots, portable fail-before và [delta manifest](../../../evidence/ZER-12/fix-01/delta-manifest.json), SHA-256 ef2ac4dd5ac25eebf020215028c1fcedc8a383e2972f258e9456aaa985ab6df5. Giữ nguyên review Claude và toàn bộ evidence/manifest/verification v1; checker v1 báo source drift là đúng, dùng fix-01/verify_fix.py cho source mới.

F1–F5 đã sửa: wiring metadata→ConfigMap data + OpenAPI/effective-env gate; terminal refusal khi chưa send, UNKNOWN từ send; MAC/schema→ledger replay trước expiry, fresh Ack context và fake main loop; llm-plan bị chặn mọi nhóm benchmark theo contract đã khóa (không thay scope nghiên cứu); CI matrix/test lock giữ toàn bộ production pin từng image. F6/F7/F8/F10 đã sửa: exact Go JSON tags, clock lead≤2s không nới expiry, token/Secret heal riêng, hashed YAML/worker PR build/disabled chờ signal. F9 residual giữ rõ: AUTO/fallback mới kiểm offline, production healer disabled, chưa tự tạo audit bền ở B0.

Kết quả cuối:102 method Python riêng biệt,133 lượt gồm31×2 production graphs +71 hồi quy;22 Go top-level,vet,Linux build,SAST đạt. Fail-before4 Go/2 Python đúng assertion + đối chứng sạch;3 manifest cũ bị cả OpenAPI/effective-env bắt và3 bản mới đạt.Toàn153 protected và6 dirty ngoài gói giữ hash; note chỉ nối,NOW chỉ prepend. HEAD c09452a,branch zer-12-command-guards,staged rỗng. Không Git publication/Linear write/lab/Docker/model. Go race và remote CI/image runtime chưa chạy.

Claude nhận writer **chỉ báo cáo** khi Hoàng gửi yêu cầu. Review delta18 source hiện có +10 file mới; đọc cả fix-01/README/runbook và source liên quan, kiểm hash trước. Được kiểm offline (fake/loopback) và tạo scratch/zer12/claude-retest; báo cáo tại docs/evidence/ZER-12/claude-retest.md, chỉ nối note/thêm pointer NOW. Không sửa product/test/pin/receipt đã chốt, không commit/push/Linear/lab/Docker/model/secret. Retest tất cả F1–F10 một lượt, tập trung known-vs-unknown, expired replay và context shutdown, exact schema/clock boundary, credential cross-role, benchmark no-model và production dependency/CI wiring. Tự dựng phản ví dụ mới, positive control; không chỉ tin checker/log. Nếu còn chặn, gom theo AC cha/con cùng reproducible expected/actual. Không nhận F9 offline là rollout hoặc tự đóng ZER-11/39/G1. Writer source Codex đóng băng tới retest trả lại.


## Claude retest độc lập fix-01 ZER-12 + ZER-40 — 19/10/2026

**RETEST_PASS_OFFLINE — không còn finding chặn (P1/P2).** Báo cáo: [claude-retest](../../../evidence/ZER-12/claude-retest.md). Baseline: HEAD c09452a, staged rỗng, `git status` 62 dòng không đổi. delta-manifest ef2ac4dd…6df5 khớp, verify_fix PASS (323 file). Checker v1 báo drift đúng dự kiến.

Tôi chạy lại độc lập:
- Go 1.21.13 offline: 22 top-level test và vet PASS.
- Python 3.11.9 trên cả hai pin production: 31 method mỗi env, cộng 71 method hồi quy.
- So lock bằng script riêng: production ⊂ test lock, cùng phiên bản, đủ hash.
- replay_before ba chế độ.

Tôi dựng thêm 10 phản ví dụ (Go overlay, ASGI với fake, mutant manifest).

Kết quả theo finding:
- **Đã sửa:** F1–F8 và F10. Riêng F6, fail-before mới cho thấy lỗ cũ rộng hơn ghi nhận: fold Unicode `rpſ` ghi đè được rps 5→100; bản mới đã chặn.
- **F9:** residual giữ nguyên như đã ghi.

Ghi chú P3 không chặn:
- **N1:** gate manifest bỏ lọt `envFrom.prefix`, đổi chéo mount↔volume, ledger readOnly, ConfigMap khác namespace và ZD_* lấy qua valueFrom. Runtime vẫn fail closed.
- **N2:** send OK rồi ledger lỗi thì response là LEDGER_UNAVAILABLE thay vì OUTCOME_UNKNOWN; trạng thái claim vẫn đúng.
- **N3:** phân vai heal/fault phụ thuộc hai Secret khác giá trị, runbook chưa ghi rõ.
- **N4:** Deployment worker/Nemesis dùng RollingUpdate mặc định với PVC RWO có owner lock; nên đổi sang Recreate.

Verdict: AC-01, AC-02 và AC-03 = ZER-40 AC-01 **PASS offline**, chưa Done. Còn lại: CI từ xa (race, `r1-production-http`, image build/smoke gồm worker) và owner acceptance; N1–N4 có thể gom vào sửa sau hoặc chấp nhận. Chưa kiểm: race, Docker, kubeconform, PVC/runtime; Gosec/Bandit chưa chạy lại; Linear AC chưa đọc lại được vì connector Claude ở workspace khác. Không sửa source, không commit/push/Linear/lab/model. Writer trả Codex/Hoàng.


## Codex nhận khép N1–N4 sau retest — 19/10/2026

Baseline HEAD c09452a, branch zer-12-command-guards, staged rỗng; verify_fix01 PASS323, Claude retest PASS offline. Writer Codex trong quyền offline đã cấp. Scope trước sửa: tests/test_command_guard_ci.py (effective namespace/env/volume wiring và mutant), tests/test_command_guard_integration.py (send thành công rồi ledger lỗi), nemesis/main.py (thông điệp unknown sau send); manifests chaos-worker/nemesis (Recreate); runbook (token operator độc lập khác giá trị và preflight so sánh không in bí mật). Không đổi executor, contract, pin, CI workflow hay evidence cũ. Gói delta mới fix-02 và scratch/zer12/codex-fix02; note chỉ nối, NOW prepend. Chỉ kiểm fake/offline, không lab/model/secret thật/Git publication/Linear write.


## Codex khép N1–N4 sau Claude retest — 20/10/2026, 00:05 +07

**OFFLINE_PASS — sẵn sàng publication/CI trong quyền Hoàng duyệt.** [fix-02](../../../evidence/ZER-12/fix-02/README.md), [delta manifest](../../../evidence/ZER-12/fix-02/delta-manifest.json) SHA-256 e6bc8ac0b2af4700ddccd5e45efcdf4bcd3c30e2d2680767364c9b16e1f5a185. Đúng sáu source trong scope: gate effective namespace/env/mount/source/PVC và mutant, Nemesis post-send error + ASGI, hai Deployment Recreate, runbook credential độc lập khác giá trị/preflight so digest không in secret. Không sửa contract/core executor/pipeline/pins/workflow.

33 method ×2 production graphs +3 consumer =36 method riêng biệt/69 lượt đạt; OpenAPI/Bandit đạt. Portable replay:24 subcase gate cũ bỏ lọt +3 đối chứng sạch, old trigger fail response;20 mutant Claude bị gate mới bắt. Toàn79 source được seal,153 protected và6 dirty ngoài gói giữ hash, evidence v1/fix-01/Claude giữ nguyên. Dùng fix-02/verify_fix.py cho source hiện tại; checker cũ drift là lịch sử, không sửa checksum cũ. Go22/vet/Linux/Gosec và hồi quy pipeline/contract không chạy lại vì file liên quan không đổi, có review độc lập fix-01.

F9 residual vẫn giữ; no real Secret/PVC/rollout, không nhận offline là runtime. HEAD c09452a,branch zer-12-command-guards,staged rỗng; Linear Zero Door đọc lại ZER-12/40 vẫn In Progress, AC chưa tích. Chưa commit/push/PR/merge/Linear write/lab/model/Docker. Bước tiếp khi có quyền: commit/push gói đúng scope, mở PR chạy remote race/production HTTP/image build-smoke, xử lý CI nếu có rồi owner acceptance và merge trong quyền tương ứng trước Done. Không cần dựng dependency giả với ZER-11/39; không đóng G1.


## Publication được Hoàng cho phép — 20/10/2026

Hoàng trả lời trực tiếp: “Cho phép commit/push và mở PR”. Codex stage đúng gói ZER-12/40 + evidence/review/note; NOW chỉ stage con trỏ ZER-12, giữ hai checkpoint ZER-9 có sẵn ở working tree. Sáu file quy ước/R1/event-contract ngoài gói giữ nguyên, không stage. Quyền này không gồm merge, Linear write hay lab/model. CI remote được chạy trên PR, publication image lên main vẫn giữ gate workflow.
