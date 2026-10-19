# ZER-12 + ZER-40 — kiểm chứng gói Codex

Trạng thái: **READY_FOR_CLAUDE_REVIEW — OFFLINE_PASS**, chưa phải nghiệm thu/Done. Codex triển khai theo quyền Hoàng đồng ý đổi vai; Claude chưa review source này. Không commit/push/PR/merge, không ghi Linear, không lab/Docker/model hoặc đọc secret thật.

## Baseline và nguồn

- HEAD c09452ac975ec581bbc2ff1f0fb5ca94f58b5267, nhánh zer-12-command-guards, staged rỗng. Source mới là working tree; [source manifest](source-manifest.json) định danh bytes cuối, không dùng HEAD cũ làm bằng chứng mã mới.
- AC sống đã đọc qua linear_zero_door, đúng workspace zero-door. [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci) và [ZER-40](https://linear.app/zero-door/issue/ZER-40/khoa-dependency-va-djua-guardcontract-checks-vao-ci) đều In Progress lúc nhận. Child chỉ bao phủ AC-03 cha; không tự đóng cha.
- Gói kỹ thuật và điều chỉnh outcome ở [issue note](../../delivery/milestones/R1-measurement/guards-and-ci.md). Snapshot nhận nằm scratch/zer12/codex/intake-baseline.json: 208 nguồn candidate/protected khớp trước sửa; 8 dirty tài liệu có sẵn được ghi riêng.
- Hợp đồng event zd-event/1.0.0 và evidence ZER-9/37 lịch sử không sửa. Ngoại lệ được phép trong tập bảo vệ: event_pipeline/Dockerfile chỉ pin base image và dùng requirements.lock; logic client/adapter/contract/store/gateway/audit không đổi.

## Map AC → triển khai → kiểm

| Issue / AC | Đầu ra đã triển khai | Kiểm / bằng chứng |
| --- | --- | --- |
| ZER-12 AC-01 | Exact parsed namespace/service/host/protocol/port/route, URL dựng cũng kiểm, cấm redirect; min duration theo trần operator, concurrency/RPS/attempt/admission chung; cancel, deadline và UID cleanup | Go validation/attack/config/main tests; test_command_guards và test_command_guard_integration; fail-before 3 lỗi thực tế |
| ZER-12 AC-02 | Token operator riêng, MAC purpose/expiry/toàn payload, strict JSON, context tin cậy, claim bền trước model/publish/dispatch, duplicate/conflict/restart/unknown, ack Kafka sau kết quả | Vector Python–Go public; Go guard/kafka tests và Python entrypoint/ledger tests, gồm đối chứng hợp lệ và side-effect counter |
| ZER-12 AC-03 = ZER-40 AC-01 | Lock transitive + hashes, base/stress image digest, actions SHA và tool versions; CI giữ các gate cũ, thêm guard/mode/contract/race và image smoke Nemesis | test_command_guard_ci; pin-metadata; lockfiles; CI workflow. Thực thi CI/build image từ xa còn là bước QA/publication sau review |

Cả ba phần đã có implementation và test; không mặc định bỏ mode để chờ ZER-11. Các PASS offline không thay CI, merge, Hoàng chấp nhận hoặc gate G1.

## Phạm vi thay đổi

- Worker nhận envelope zd-command/1 ở mặt điều khiển H, độc lập schema event O. Xác thực trước parse/policy; role không lấy từ source tự khai. Command chỉ thu hẹp trần server. Một dispatcher tuần tự; admission tối thiểu 6 giây giữ qua ledger, không nhân ngân sách bằng nhiều command.
- HTTP dùng một ticker chung, đếm cả request lỗi, cấm redirect và không retry ngầm. Pod kill chỉ một UID đúng service. Stress cleanup có context mới 5 giây và UID precondition; cleanup lỗi là FAILED, không tạo bằng chứng effect/recovery.
- API xác thực trước model/Kafka. Idempotency gắn endpoint/body/policy/context; model plan bị từ chối chắc chắn được lưu terminal, duplicate không gọi model lại. Publish/ack không rõ để lại claim UNKNOWN; không tự chạy lại. Reset và legacy healer không đi vòng.
- Mode theo locked contract: B0 không decision/LLM/guard/heal của ZERO DOOR nhưng không cấm harness fault; BM chỉ proposal MANUAL của operator_console cùng context; B1 RULES; B2/B3 đúng producer/fallback có tham chiếu lỗi hợp lệ. Production healer R1 vẫn không có executor. Các đối chứng thực thi dùng fake executor.
- Đường GET có nhật ký fault và mọi POST Nemesis cần token operator; không gửi token vào browser. Key model bỏ khỏi URL/log, không ghi raw response/plan vào dashboard buffer. Không gọi model thật để kiểm thay đổi này.
- [Runbook](../../runbooks/r1-command-guards.md) giữ cấu hình, định dạng chữ ký, giới hạn ledger, cách xử lý UNKNOWN và ranh giới rollout. Template policy disabled; không có secret thật hay PVC được tạo.

## Kết quả và môi trường

Môi trường chính: Python 3.11.9 với tests/requirements-command-guards.lock universal; runtime/venv/cache riêng dưới scratch/zer12. Môi trường ZER-9 cũ Python 3.12.4 có dependency khác chỉ là kiểm sơ bộ; không dùng nó để khẳng định đúng lock CI. Image production có requirements.lock Linux/Python 3.11 riêng. Phiên bản thực ở [environment](results/pinned-environment.txt).

| Kiểm | Kết quả | Artifact |
| --- | --- | --- |
| Python guard/schema/MAC/ledger | 7/7 | [log](results/pinned-command_guards.txt) |
| Mode B0/BM/B1/B2/B3, fallback, no side effect | 3/3 | [log](results/pinned-command_modes.txt) |
| HTTP entrypoint/model/Kafka fake | 10/10 | [log](results/pinned-command_guard_integration.txt) |
| Pin/CI/manifest + counterexamples thiếu gate | 4/4 | [log](results/pinned-command_guard_ci.txt) |
| Gaia/Hephaestus qua HTTP loopback | 4/4 | [log](results/pinned-event_agents.txt) |
| Core event / regression | 22/22 và 42/42 | [core](results/pinned-event_pipeline.txt), [regression](results/pinned-event_pipeline_regressions.txt) |
| Actor verifier / Nemesis consumer | 4/4 và 3/3 | [verifier](results/pinned-event_actor_verifier.txt), [consumer](results/pinned-nemesis_consumer.txt) |
| Locked contract release | Các focused case và link PASS | [JSON](results/pinned-contract-release.txt) |
| Go unit / vet / Linux build | 17/17 top-level, vet PASS, Linux build PASS trên Go 1.21.13 | [summary](result-summary.json) |
| Bash behavioral hồi quy | PASS, không CLI lab thật | [log](results/shell.txt) |
| Bandit 1.7.9 | 0 issue ở ngưỡng CI | [log](results/bandit.txt) |
| Gosec v2.19.0, Go 1.21.13 | 0 issue actionable; 4 chú thích G304 theo đường dẫn | [log](results/gosec.txt) |

Gosec ban đầu bắt 4 cảnh báo dynamic file path: policy/key chỉ đọc từ trusted process config; ledger dùng basename cố định dưới thư mục riêng, regular-file check và exclusive owner lock. Mỗi callsite có chú thích G304 kèm lý do; không tắt rule/job toàn cục. Gosec cũ không build bằng Go 1.25.6 do x/tools, nên đã chạy đúng Go 1.21.13 được khóa trong CI; toolchain/cache cục bộ, không cài PATH toàn máy.

Tổng 99 test Python (24 test guard/mode/entrypoint/CI mới), 17 test Go top-level. Ba fail-before đều FAIL đúng lý do, valid control PASS. Log chuẩn hóa LF khi copy; bản gốc ở scratch.

Các lỗi tự bắt và sửa: SQLite connection chưa đóng; thông báo/annotation endpoint chưa tương thích hai test AST cũ; copy mutex trong test bị vet bắt; known model refusal cần terminal thay vì bỏ claim mơ hồ; mọi command mới phải dừng khi còn claim UNKNOWN; cleanup status phải giữ enum fault executor; targetURL rỗng sai kiểu phải bị chặn trước publish (không được coi false/null/list là URL bị bỏ trống). Các test lịch sử không bị sửa để làm xanh.

## Fail-before và đối chứng

[Probe baseline](results/fail-before.jsonl) dùng API đã có ở HEAD, không phụ thuộc helper mới. Ba ca phải FAIL trên bản gốc: URL bên ngoài chứa suffix ở path, message maxDuration vượt global cap, JSON trùng key. Valid URL + duration 1 giây vẫn PASS. Những hành vi đó được kiểm trên source mới bằng Go unit tests. Không tính compile/import error là fail-before thành công.

## Giới hạn và bước nghiệm thu

- Go race chưa chạy local: Windows không có C compiler, CGO_ENABLED=0. CI Linux có go test -race ./..., chưa có kết quả job từ xa.
- Build Linux ở đây là biên dịch binary, không chạy binary và không build/pull/run Docker. CI sẽ build/import smoke image production, gồm cả Nemesis. Python local đúng lock test, không chứng minh ABI/image Linux.
- Metadata base image/stress image lấy trực tiếp registry, action SHA/release từ GitHub và package version từ PyPI: [receipt](pin-metadata.json). Không nâng phiên bản nghiệp vụ lớn; giữ input trực tiếp hiện hữu, khóa transitive. Không coi resolve lock là đã chạy mọi platform.
- Deployment legacy còn tag local :latest. Source mới chưa có application image digest; chỉ seal digest của revision cuối sau review/build/publication rồi mới rollout được duyệt. CI publish đổi application tag sang Git SHA. Không giả digest application chưa build, không apply template để thử.
- Chưa kiểm PVC thật, storage corruption/power loss, clock skew thật, firewall/CNI, nhiều replica hoặc actual fault effect/KPI. File lỗi/fsync/unknown dùng fake/patch và temporary storage. Ledger không tự prune; operator phải đối chiếu trước khôi phục.
- Legacy stress pod vẫn là cách mô phỏng cũ; mục tiêu CPU thực và rò nhãn telemetry của vector thuộc việc sau. Gói không chứng minh profile nghiên cứu H/O runtime hay tính đúng fault effect. ZER-11/39, R2 và G1 không được đóng từ các kết quả này.
- Chờ Claude review độc lập cả cha/con, Codex sửa gom/retest; publication/CI/merge/nghiệm thu theo quyền riêng. Chưa có quyền các bước đó trong gói triển khai hiện tại.

## Chạy lại kiểm gói

    python -B docs/evidence/ZER-12/verify_package.py

Script chỉ đọc source/evidence và kiểm hash/kết quả, không gọi dịch vụ hay chạy executor. Các lệnh test từng phần ở runbook; CI workflow giữ lệnh cài dependency có hashes cho môi trường mới.
