# Issue — Sửa dashboard và các chế độ đối chứng

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung). Nguồn đối chiếu: `R1-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T03-S01 | Bỏ số ngẫu nhiên và nội dung mô phỏng khỏi phần được trình bày là kết quả thực. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S02 | Cho dashboard và bộ xuất dữ liệu dùng chung phép đo. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S03 | Tách MANUAL, RULES và AI; MANUAL không tự kích hoạt healer. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S04 | Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi. | [ZER-39](https://linear.app/zero-door/issue/ZER-39/dung-djoi-chung-b0-kubernetescontroller) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T03-S01

Dashboard hiển thị trạng thái không có dữ liệu và nguồn của số liệu.

### R1-T03-S02

Cùng run_id cho ra cùng KPI; phản ánh lỗi và độ trễ cập nhật.

### R1-T03-S03

Log ba chế độ và phép thử chứng minh đối chứng manual không bị auto-heal.

### R1-T03-S04

Cấu hình HPA/guard/probe được ghi rõ; chứng minh ZERO DOOR không phát lệnh heal trong B0, vẫn có đo độc lập.

## Phụ thuộc cần đối chiếu

[R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/probes-and-metrics.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

## Gói thực hiện Codex giao Claude — ZER-11 + ZER-39 — 21/10/2026

Hoàng yêu cầu giao trọn phần R1 còn lại cho Claude, làm chắc theo AC. Claude là writer; Codex nhận lại cả gói để review độc lập. Tài liệu này cấp scope triển khai/offline theo yêu cầu hiện hành, không cấp quyền lab/publication/Linear.

### Baseline và nguồn chuẩn

- Checkout: R:\_Projects\Eurus_Workspace\zero_door. HEAD thực đọc: 169413303340fc01eea8597c121ce39455892af0, nhánh zer-10-independent-measurement. origin/main: 22a89db11a041faa1db797a6a9f1afee1abde647 (PR #26 đã merge, cùng cây nội dung với HEAD đã nghiệm thu).
- Trước khi sửa, tự đọc lại Git/dirty; không xem baseline trên là bất biến. Nếu main đã thay mã liên quan, đánh giá delta trước. Tạo nhánh zer-11-dashboard-baselines từ main đã xác minh khi Git cho phép giữ nguyên dirty; không reset/stash/force checkout hay thu gom việc khác.
- Dirty sẵn: AGENTS.md, NOW.md, delivery/README.md, WORKFLOW.md, R1/README.md, event-contract.md, guards-and-ci.md, probes-and-metrics.md; untracked WORKING-AGREEMENT.md và docs/detail_zero-door.md. Chi tiết scratch/zer11/intake-status.txt; 10 file ngoài gói có hash ở intake-protected-hashes.json. NOW chỉ prepend, note này chỉ append; không stage gì trong lượt Claude.
- AC sống đọc 21/10 trên đúng linear_zero_door, project P-ZER-1/team ZER. ZER-11 và ZER-39 hiện Todo, prerequisite ZER-10 đã Done. Snapshot bên dưới là nguồn dự phòng nếu Claude không đọc được đúng workspace; không dùng connector EurusDevSec/S-cool.
- Đọc README → WORKING-AGREEMENT → NOW → note này; SCOPE/WORKFLOW; contract docs/design/r1-event-contract.md (nhất là 5, 7.4, 8) và docs/design/r1-measurement.md; quyết định ZER-8 về BM/B0/fallback; evidence ZER-10/fix-03 và runtime-01; guard ZER-12 đã nghiệm thu. Không khảo sát lại toàn bộ lịch sử.
- GitNexus context đọc tại HEAD 1694133, incomplete_reasons rỗng. Query và context GuardedRules chỉ dùng điều hướng; source trực tiếp xác nhận dưới đây.

### Outcome và AC không được cắt bớt

ZER-11:
1. AC-01: bỏ số ngẫu nhiên/nội dung mô phỏng khỏi kết quả thực; hiển thị không có dữ liệu và nguồn số liệu.
2. AC-02: dashboard và bộ xuất dùng chung phép đo; cùng run_id ra cùng KPI; hiển thị lỗi và độ trễ cập nhật.
3. AC-03: tách MANUAL, RULES, AI; MANUAL không tự kích hoạt healer; có log và phép thử cho cả ba.
4. AC-04: B0 chỉ controller Kubernetes/HPA phục hồi; cấu hình HPA/guard/probe rõ, ZERO DOOR không phát lệnh heal nhưng vẫn đo độc lập.
ZER-39 AC-01 chính là ZER-11 AC-04. Hoàn thành child không thay AC-01–03 của cha.

Cần giao một sản phẩm hoạt động và kiểm được, không chỉ viết thiết kế. Runtime chưa được cấp quyền phải ghi PARTIAL/NOT_RUN riêng; không dùng offline PASS để đóng AC cần quan sát thật.

### Những bẫy đã xác minh trước khi giao

- nemesis/static/app.js updateSREStats đang ghép attack log/heal history, cộng Math.random(), chặn MTTR tối thiểu và có fallback 12.3s/100%; PARTIAL cũng tính success. Thay toàn bộ đường KPI này, không chỉ bỏ Math.random.
- nemesis/main.py có /api/status, /api/logs, /api/chat, /api/heal-history. /api/status mặc định các giá trị có thể trông như số đo khi upstream lỗi: kiểm cả backend lẫn frontend. Log/chat legacy không phải raw KPI hoặc quyết định LLM thật.
- measurement/__main__.py score đã dùng Raw.load → Scorer → run_metrics → Output.write; output/1 gồm score.json, incidents.csv, usage.csv. Tái sử dụng artifact/phép đo này. Không tạo scorer thứ hai bằng JavaScript hay suy thời gian từ heal history.
- hephaestus/command_guard.py có ModeGate và GuardedRules; main /heal/trigger không truyền executor, legacy bị khóa. Các nhánh cho phép của ModeGate hiện chưa chứng minh thành runtime heal. Không bật các executor legacy, triển khai LLM R4 hay viết lại healer R3 để làm đẹp bằng chứng R1.
- infrastructure/manifests/target-app-hpa.yaml chỉ là manifest có sẵn, không là bằng chứng HPA đang chạy. Profile nền cũ không HPA. B0 phải phân biệt Deployment controller và HPA; không được tuyên bố đã kiểm HPA nếu chỉ kiểm controller.

### Quyết định triển khai và bất biến

1. Dashboard kết quả chỉ đọc đầu ra scorer đã xác thực theo schema/version và run_id. Chọn một đường ít thay đổi nhất: adapter read-only ở Nemesis phục vụ score.json từ root S cấu hình cố định, đăng ký run rõ ràng. Chia sẻ cùng artifact với JSON/CSV export; nếu cần live preview thì ghi rõ chưa seal/provisional và dùng cùng scorer. Không ghi raw/scorer artifact hay tự động scan/gộp dataset lịch sử.
2. Phân biệt không có run, EMPTY/NO_ELIGIBLE, MISSING/UNKNOWN/CENSORED, FAILED/PARTIAL, artifact lỗi, upstream lỗi và stale. null không thành 0; không có mẫu không thành 100%; ACTION_COMPLETED không tự thành recovery. Hiển thị đơn vị, mẫu số/coverage/label, run/group, scorer/criteria version, nguồn/hash, thời điểm dữ liệu và thời điểm cập nhật. Không gọi generated_at là mốc event. Poll lỗi giữ last-good có nhãn stale/error, không tiếp tục coi là dữ liệu mới.
3. Cùng run/options/input hash thì API, màn hình và export khớp giá trị nguồn; cho phép format/làm tròn để đọc nhưng không đổi mẫu số hoặc logic. Chặn run/path traversal, symlink/root escape, artifact malformed/nonfinite, sai run/schema; không cho request chọn đường dẫn filesystem bất kỳ. Không leak đường dẫn máy, key/token, H/control/schedule.
4. Tách mặt O của operator BM khỏi báo cáo S có ground truth. Không cho BM đang chạy mở raw H, nhãn case, seed/onset/lịch chưa kết thúc qua API/dashboard/log/chat/download. Nếu dùng màn hình kết quả offline riêng, phải có ranh giới truy cập thật, không chỉ ẩn nút. Tái dùng quyền hiện có; không dựng framework auth mới. Trang kết quả read-only không được tự POST attack/heal/reset hay gọi model.
5. UI label MANUAL = BM; RULES = B1; AI = B2 (B3 chỉ khi thực có cấu hình và không giả là B2); B0 là nhóm riêng. Group/context do nguồn tin cậy phía server/run ấn định, client không tự đổi qua query/body. Log ai/nguồn quyết định/thời điểm/run/trial theo contract. Không gọi RULES hoặc fallback là AI. AI chưa có producer thật thì hiển thị unavailable, không gọi API/model hoặc tạo câu reasoning giả.
6. Kiểm mode ở entrypoint HTTP/consumer thực đang dùng, không chỉ gọi ModeGate.admit. B0 cấm toàn bộ DECISION, LLM_CALL, GUARD_VERDICT, HEAL_STARTED, API_ACCEPTED, ACTION_COMPLETED của ZERO DOOR theo contract 7.4; BM không auto-decide/auto-heal. Từ chối phải có audit vận hành thích hợp, không phát GUARD_VERDICT vào B0 trái contract. Positive control với fake executor chứng minh test không đạt giả do mọi đường đều tắt; production executor vẫn khóa. Fallback cần decision lỗi hợp lệ, đúng run/trial/source và được phân loại riêng.
7. B0 profile phải ghi controller/HPA có hay không, target/replica/resources/probe/guard/policy, thành phần observer nào chạy, quyền không phát heal. Dùng cùng điều kiện đo khi so nhóm; không thêm fault do LLM chọn theo nhóm. Nguồn H vẫn do harness/probe, observer không nhận control/ground truth.
8. Không tự đổi contract/KPI/method đã nghiệm thu. Lỗi chặn AC cùng nguyên nhân trong scope thì sửa gom; cải tiến ngoài AC ghi residual ngắn.

### File/action scope

Trước edit, Claude ghi chính xác từng file mới/sửa và lý do trong append note, chụp source before/hash (gồm file untracked sắp sửa); nhờ đó regression có fail-before thật. Danh sách dưới là scope được phép, không yêu cầu sửa hết:

- agent-orchestrator/nemesis/main.py; static/{app.js,index.html,style.css}; module mới agent-orchestrator/nemesis/measurement_view.py cho read-only result adapter.
- agent-orchestrator/hephaestus/{main.py,command_guard.py}; agent-orchestrator/nemesis/command_guard.py chỉ khi cần tích hợp trusted mode/read-only access. Không sửa body các executor gây tác động.
- tests/test_dashboard_measurement.py, tests/test_dashboard_modes.py, tests/fixtures/zer11/; static test nhỏ nếu cần. Mở rộng tests/test_command_modes.py, test_command_guard_integration.py, test_event_agents.py khi thay entrypoint liên quan.
- infrastructure/manifests/r1-baselines.yaml (profile tách biệt, không thay mặc định live); tests/check_r1_baselines.py; tests/check_guard_manifests.py nếu manifest guard bị ảnh hưởng.
- infrastructure/scripts/verify-dashboard-baselines.{py,sh} cho offline checks và harness runtime opt-in; --help/offline không chạm cluster/Docker/model. Runtime phải có approval reference thực, budget/cleanup/ownership rõ, không tự chạy.
- .github/workflows/ci.yml và Dockerfile của Nemesis/Hephaestus chỉ để đưa đúng test/module/profile vào image/CI. Dependency mới chỉ khi thật cần; ưu tiên stdlib và lock production/test hiện có, không nâng phiên bản hàng loạt.
- docs/runbooks/dashboard-and-baselines.md, docs/evidence/ZER-11/ (verification, AC mapping, fixtures tối thiểu, raw/log/hash), scratch/zer11/ (snapshot và log tạm). Dùng chung gói cho ZER-39, không nhân bản evidence.
- Note hiện tại append, NOW prepend. Có thể thêm/sửa file trực tiếp trong các nhóm trên nếu cần sửa cùng AC, ghi trước khi làm. Ngoài nhóm: chỉ báo khi thật cần scope mới, không tự mở rộng repo.
- measurement/, event_pipeline/, chaos-worker/, evidence ZER-9/10/12/37, thiết kế khóa và raw cũ là read-only. Nếu phát hiện lỗi ở đó chặn AC, đưa repro/impact vào bàn giao; không vá lén hay sửa immutable manifest để checker xanh.

### Kiểm bắt buộc, tập trung theo hành vi

- Bảng AC → case → expected → actual → artifact. Kiểm có/không dữ liệu, 0 hợp lệ vs null, failure/missing/timeout/censored, partial coverage, upstream lỗi/stale, invalid artifact, đổi run A→B khi request A trả muộn. UI không trộn số cũ/new run và không render nội dung event không tin cậy thành HTML thực thi.
- Từ raw fixture đã khóa, tái tạo output bằng CLI ZER-10; API/UI/export cùng run/options/hash khớp. Case E01 và N=0/failure/missing; so giá trị độc lập tính tay ở vài case trọng yếu. Đừng chỉ so hai consumer cùng sai.
- HTTP/consumer mode tests với fake Kafka/Kubernetes/LLM: BM auto path không decision/action, operator hợp lệ được phân biệt; B0 không có các event cấm; B1 nguồn RULES; B2/B3/fallback nguồn đúng; sai nguồn/group/run/trial bị chặn. Có negative control và positive control, duplicate/replay liên quan không tạo action lặp. Không biến fake thành claim LLM/heal runtime.
- Render/parse profile và effective env/volume/RBAC/mode wiring. Kiểm quyền ghi/thông tin H→O/S→O; giữ guard ZER-12 và executor-disabled.
- Mở dashboard bằng browser local cô lập, backend fake/fixture offline; chụp trạng thái loaded/empty/error/stale và kiểm chuyển run, không chỉ test chuỗi source. Không gọi lab/service/model thật từ trang này; nếu chưa có browser khả dụng ghi hạn chế, đừng cài framework toàn máy. Kiểm desktop 1 viewport đủ đọc, không nhân ma trận thiết bị.
- Chạy kiểm mới và hồi quy liên quan: test measurement hiện có (134 ở baseline), command modes/entrypoint/CI/manifest theo delta, event agent/pipeline nếu consumer ảnh hưởng. Dùng production pins thật cho FastAPI/Pydantic/Kafka, không test trên stack tùy ý. Security scan tương ứng và git diff --check.
- Test lỗi mới cần fail-before trên snapshot trước sửa hoặc mutant đúng invariant có giải thích; không nhân số mutant/check chỉ để tăng thống kê. Clean checkout chạy offline không lệ thuộc scratch/venv máy cá nhân. CI config cần chạy được từ checkout sạch.
- Tự review trọn diff và consumer trực tiếp; gom sửa trước khi trả. Không gửi từng checkpoint nhỏ để Codex ráp.

### Runtime và G1: chuẩn bị đầy đủ, chưa tự thực thi

Quyền lab ZER-10/38 là riêng cho lượt đã xong, không chuyển sang ZER-11/39. Gói này chưa cho phép Docker/build, kubectl apply/delete/scale, fault hay gọi provider. Offline test được phép dùng process/fake/local loopback cô lập, không truy cập dịch vụ lab thật.

Claude chuẩn bị một kế hoạch runtime cụ thể có exact context/resources/actions, trần thời gian/giao dịch, manifests và baseline/rollback theo UID; target/quota/HPA/guards trước-sau; raw/absence coverage cho không phát heal, probe độc lập và cleanup. B0 cần quan sát controller phục hồi tự nhiên sau nhiễu được duyệt; không lấy việc operator scale về hoặc tự sửa target làm bằng chứng controller tự chữa. Không nhận “không thấy log” là chứng minh không action: phải có coverage và positive control riêng. Kế hoạch nên nhỏ nhất đủ AC, không chạy pilot hay attack vectors R2/R3. Chỉ xin Hoàng quyền cho kế hoạch đã review, một lần gom, sau offline; tiếp tục xong các phần độc lập trước.

Gate G1 cần tích hợp ID xuyên pipeline, raw/export và KPI tái tính, evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động. Viết mapping evidence kế thừa ZER-9/10/12 cộng delta ZER-11/39; chỉ rõ còn thiếu, không tự tạo kết luận G1 PASS hay đòi chạy lại mọi lab cũ.

### Bàn giao một lần cho Codex

- Verdict READY_FOR_CODEX_REVIEW_OFFLINE hoặc CHANGES_REQUIRED/PARTIAL theo bằng chứng, không tự ghi Done.
- Delta manifest/hash, baseline/status và scope before/after, đường snapshot; giữ nguyên protected hashes và mọi evidence cũ.
- AC mapping, lệnh tái hiện, expected/actual, kiểm browser, log clean checkout/production pins, regression, phiên bản/config và residual/UNKNOWN.
- Runtime plan sẵn để Codex kiểm và xin quyền; không chỉ lời nhắc chung “cần chạy lab”.
- Append handoff vào note này, prepend NOW; trả writer cho Codex, dừng ghi. Không commit/push/PR/merge, đổi Linear, gửi agent khác hay chạy model. Codex sẽ review độc lập source/consumer, tự tính KPI/đối chiếu UI-export và dựng phản ví dụ; sau đó mới runtime/CI/publication/owner acceptance theo quyền.

## Claude nhận writer ZER-11 + ZER-39 — phạm vi file trước khi sửa — 21/10/2026

Đọc lại Git: HEAD `1694133` trên `zer-10-independent-measurement`, `git diff HEAD origin/main` rỗng (cùng tree `22a89db`), dirty đúng danh sách intake và 10 protected hash khớp. Không tạo nhánh `zer-11-dashboard-baselines`: quy tắc phiên Claude cấm switch branch trong checkout dùng chung; làm trên cây hiện có (cùng nội dung main), để Hoàng/Codex tạo nhánh khi publication. Snapshot trước sửa: `scratch/zer11/claude/before/` + `before.json` (16 file có sẵn, 10 file mới ghi absent).

File sẽ sửa/thêm và lý do:
- `nemesis/measurement_view.py` (mới): adapter read-only đọc `score.json`/CSV của run đã đăng ký trong registry ở root S cố định; kiểm schema, run_id, hash, symlink/traversal, nonfinite; quyền đọc riêng `results-reader`.
- `nemesis/main.py`: route `/api/results/*` dùng token đọc kết quả, tách khỏi token operator; `/api/status` trả null + trạng thái nguồn thay vì 0; `/api/chat` bỏ reasoning tổng hợp; `/api/logs`, `/api/heal-history` báo lỗi upstream thay vì danh sách rỗng.
- `nemesis/static/{app.js,index.html,style.css}`: bỏ `updateSREStats` (Math.random, fallback 12.3s/100%, PARTIAL tính success); render text an toàn; null/stale/error. Thêm `static/results.{html,js}`: trang kết quả S read-only.
- `hephaestus/main.py`: audit vận hành khi từ chối mode; dedup một action cho một decision; seam executor chỉ cho test (mặc định None, không đọc env).
- `nemesis/Dockerfile`: copy `measurement_view.py`. `.github/workflows/ci.yml`: thêm job/test mới.
- Test: `tests/test_dashboard_measurement.py`, `tests/test_dashboard_modes.py`, `tests/fixtures/zer11/`, `tests/check_r1_baselines.py`.
- Profile: `infrastructure/manifests/r1-baselines.yaml`; `infrastructure/scripts/verify-dashboard-baselines.{py,sh}` (offline + runtime opt-in bị khóa nếu thiếu approval).
- Tài liệu/evidence: `docs/runbooks/dashboard-and-baselines.md`, `docs/evidence/ZER-11/`, `scratch/zer11/claude/`. Note này append, NOW prepend.

## Claude bàn giao ZER-11 + ZER-39 — READY_FOR_CODEX_REVIEW_OFFLINE — 21/10/2026

Gói ở [docs/evidence/ZER-11](../../../evidence/ZER-11/README.md) (bảng AC → ca → expected/actual, browser, lần chạy lỗi giữ lại), runbook và runtime plan ở [dashboard-and-baselines runbook](../../../runbooks/dashboard-and-baselines.md). Delta và hash before/after: `docs/evidence/ZER-11/manifest.json`; snapshot `scratch/zer11/claude/before/`. HEAD `1694133`, không đổi nhánh, staged rỗng, 10 protected hash khớp.

- AC-01: console vận hành không còn tính KPI (bỏ Math.random, fallback 12.3s/100%, PARTIAL=success); `/api/status` null + trạng thái nguồn thay 0; `/api/chat` không ghép reasoning; render text an toàn. Trang S riêng `results.html` hiện nguồn/hash/không có dữ liệu.
- AC-02: adapter `nemesis/measurement_view.py` chỉ đọc run đã đăng ký (registry, CLOSED), kiểm hash/schema/run/group/nonfinite/khóa trùng, tự sinh lại CSV và từ chối nếu lệch; API = trang = file tải. Độ trễ cập nhật = hiển thị − mốc event đã xác minh mới nhất; `generated_at` không dùng. STALE giữ số cũ có nhãn; chuyển run bỏ câu trả lời muộn (đã kiểm browser).
- AC-03: consumer thật chỉ tự quyết ở B1 (positive control), nhóm khác có `MODE_AUDIT`; `/heal/trigger` BM admit rồi `R1_EXECUTOR_DISABLED`; seam executor chỉ test, một action/decision, replay không lặp. Quyền đọc S tách khỏi khóa operator.
- AC-04/ZER-39: `infrastructure/manifests/r1-baselines.yaml` (profile nhóm + HPA 1..3, không đổi lab mặc định) và `tests/check_r1_baselines.py`. Runtime B0/HPA **NOT_RUN**: kế hoạch G-ZER11-RT1 (context, tài nguyên, trần, pha P0–P7, positive control, rollback theo UID) chờ Codex review rồi Hoàng duyệt.

Kiểm: fail-before 8 NEGATIVE/5 CONTROL PASS; mutant 17/17; hồi quy trên 3 interpreter pin (FastAPI 0.111.0/0.110.0) và measurement 134/134; Bandit 0; `git diff --check`; clean checkout. Residual: console Nemesis vẫn hiện log tấn công H cho người giữ khóa operator (cần O-console BM riêng); console không gửi Authorization (từ ZER-12); B2/B3 chưa có producer. Writer trả Codex; không commit/push/Linear/lab/model.

## Codex review gom và gói sửa fix-01 — ZER-11 + ZER-39 — 21/10/2026

Kết luận **CHANGES_REQUIRED_OFFLINE / NOT_READY_FOR_RUNTIME**. Báo cáo [codex-review.md](../../../evidence/ZER-11/codex-review.md); proof bền vững ở [codex-review/](../../../evidence/ZER-11/codex-review/). AC sống đọc đúng Linear Zero Door, ZER-11/39 In Progress; không sửa status. HEAD1694133/branch zer-10-independent-measurement giữ nguyên; staged rỗng. Intake46hash gói và10protected khớp, source/evidence Claude không bị sửa trong review.

Hai P2: **ZR11-01** results.js giữ cached PASS khi refresh trả422 integrity (browser xác nhận),401 hoặc404 (VM replay), cần phân biệt fatal với transient503; **ZR11-02** runtime plan có năm điểm chưa nhất quán: nếu bật P6 thì Gaia vẫn0 và xóa pod thêm lần vượt tổng1; đường fixture-server đọc root thật chưa tồn tại; trial6phút/cap600s không đủ timeout coverage;30giao dịch ở nhịp1s không đủ K3+S30. N1 P3: shape artifact local trước register có thể gây500, không bypass reader/hash.

Đã chạy độc lập hai production env: mỗi env dashboard24/modes7/command_modes3/guard_integration13/event_agents4 đạt; baseline/OpenAPI/guard manifests đạt; Node syntax/Bandit0/diff-check sạch. Fixture/scorer/CSV và E01 đối chiếu; VM3fatal phản ví dụ+1transient control; browser good→hash422→STALE vẫnPASS. Không chạy lại mutant17/134measurement/clean checkout, không nhận log Claude thành lượt reviewer. GitNexus refresh PDG đã có symbols mới nhưng bị ngắt trước receipt; source/probe là bằng chứng chính. Không lab/Docker/model/publication/Linear.

### Claude sửa fix-01 một gói, sau đó Codex retest

- Trước sửa chụp snapshot/hash source hiện tại và manifest delta; giữ code/probe/report Codex chỉ đọc. Giữ10protected file ngoài scope; note chỉ append, NOW chỉ prepend.
- **ZR11-01:** sửa results.js: fatal integrity/schema,401/access và404/unregistered xóa cached view/download/state; chỉ giữ STALE last-good cho lỗi vận chuyển/upstream tạm thời. Đổi khóa/kết nối lại vô hiệu response cũ trước đọc registry; không trộn state giữa phiên/run. Regression dùng source JS thật, có good→fatal, good→transient→good, A→B late response; không dựng framework browser mới và không thêm scorer.
- **ZR11-02:** sửa runbook + verify-dashboard-baselines.py/sh nếu cần đường đọc root thật. Hoàn thiện plan nhỏ nhất đủ B0/controller/HPA và dashboard cùng export; P6 tùy chọn phải ghi có/không, nguồn Gaia thực và budget riêng trong tổng. Số thao tác, thời gian, cadence/gap, số giao dịch phải đủ K3/S30 và cap600 hoặc ghi dừng sớm incomplete đúng scorer. Không sửa criteria/scorer để biến thiếu dữ liệu thành TIMEOUT/PASS. Thêm đường serving S root thật read-only cô lập/loopback, bảo toàn registry/hash, không tự gọi Prometheus/Hephaestus/Kafka/model; kiểm không thay root thật bằng SYNTHETIC. Cho reviewer lệnh chạy được, cấu hình/UID/ownership/rollback/stop và raw/coverage/positive control rõ trước khi xin quyền runtime.
- **N1 P3:** có thể khép bằng validation nhỏ cho đúng field đang tiêu thụ trong measurement_view.py; lỗi shape thành reason-code422, input digest không được thiếu. Không schema framework/catch-all hoặc tái tính KPI. Ghi N1 đã sửa hay residual và giới hạn.
- Scope fix: nemesis/static/results.js, nemesis/measurement_view.py (N1 nếu sửa), tests/test_dashboard_measurement.py và test JS nhỏ liên quan, verify-dashboard-baselines.py/sh, runbook, evidence ZER-11/fix-01 và scratch/zer11/claude-fix01. Chỉ sửa main.py khi thật cần wiring read-only, ghi lý do trước. Measurement/event_pipeline/chaos-worker/contract/evidence cũ vẫn read-only.
- Tự review sửa gom; retest phần ảnh hưởng và entrypoint liên quan bằng đúng production pins. Fail-before trên snapshot hoặc invariant mutation có giải thích; không nhân suite/mutant không cần thiết. Trả delta manifest, expected/actual, log và plan sẵn review một lần, rồi trả writer Codex.
- **Chưa cấp quyền:** cluster/Docker/build/model/API trả phí, commit/push/PR/merge, Linear hay nhắn agent. Sau offline đạt, Codex review plan và xin Hoàng đúng gói runtime, không dùng quyền ZER-10 cũ. G1 còn cần BM/O isolation, không dùng console H làm màn hình BM; chưa yêu cầu triển khai producer R4/healer R3.

## Claude sửa fix-01 ZER-11 + ZER-39 — READY_FOR_CODEX_RETEST_OFFLINE — 21/10/2026

Gói ở [docs/evidence/ZER-11/fix-01](../../../evidence/ZER-11/fix-01/README.md) (bảng finding → sửa → kiểm, lần chạy lỗi giữ lại). Snapshot trước sửa `scratch/zer11/claude-fix01/before/` (62 file, gồm evidence gói đầu và `codex-review/`); delta và kiểm evidence cũ không đổi ở `fix-01/manifest-fix01.json`. HEAD `1694133`, không đổi nhánh, staged rỗng, 10 protected hash khớp. `main.py` không đổi.

- **ZR11-01:** `results.js` chỉ giữ STALE cho lỗi vận chuyển và 502/503/504 ngoài lý do cấu hình store. 422, 401/403, 404, 500, 503 cấu hình, câu trả lời lệch run hay view không render được thì xóa view/KPI/nút tải; khóa bị từ chối kết thúc phiên; đổi khóa xóa số cũ và vô hiệu câu trả lời cũ trước khi đọc registry. Regression `tests/results_page_vm.cjs` chạy chính `results.js` trong Node VM: 19/19 sau sửa, 12 ca fail trên snapshot. Phản ví dụ của Codex chạy lại: 503 STALE, 422/401/404 xóa KPI. Browser: hash 422 xóa số, trả byte lại thì hiện số mới, 503 STALE, khóa sai xóa hết và dừng poll.
- **ZR11-02:** thêm `verify-dashboard-baselines.py serve-results` (root S thật, chỉ đọc, loopback, chỉ trang kết quả và GET `/api/results/*`, không consumer Kafka, receipt hash root lúc đầu/cuối) và `plan-check` (ma trận budget có kiểm). Runbook mục 5 viết lại: P6 tách thành gói RT2 riêng; RT1 đúng 1 lần xóa pod; cửa sổ trial phủ W_eff 300 s và cap_rec 600 s + S; dừng sớm ra MISSING_PROBE/UNKNOWN_EFFECT, không TIMEOUT; ≤ 995 mẫu/trial; worst case 3250 s trong trần 3600 s; F-01 PILOT không đổi.
- **N1:** `check_document` đòi digest export H/O (`INPUT_DIGEST_MISSING`) và kiểm kiểu đúng các trường được dùng; `register` kiểm trước khi dựng lại CSV. 12 ca shape ra 422 khi đăng ký và khi đọc.

Kiểm: fail-before 9 NEGATIVE/24 CONTROL PASS; mutant 12/12 (attempt1 11/12 giữ lại: một mutant tương đương đã thay); hồi quy gói đầu trên 3 interpreter pin + measurement 134/134 + Bandit 0; clean checkout 22 file. **Điều kiện còn mở trước khi xin quyền RT1:** harness H-RT1 phát ATTACK/EFFECT/RECOVERY cho B0 chưa có trong repo, cần viết và review offline riêng. Residual: CSS `results.html` cuộn ngang dưới ~610 px; residual gói đầu giữ nguyên. Writer trả Codex retest; không commit/push/Linear/lab/model.

## Codex retest fix-01 — PASS_OFFLINE; chuẩn bị H-RT1 — 21/10/2026

[Báo cáo](../../../evidence/ZER-11/codex-retest01.md): ZR11-01/02 đã sửa đúng, các phản ví dụ N1 được khép; không còn P1/P2 mở trong delta. Dashboard33 đạt trên hai production environment; modes7 trên Nemesis; JS19 đạt và snapshot trước sửa fail12/control7; replay UI/adapter cũ đúng expected; Bandit hai file Python sạch. Manifest28/28, file ngoài delta trong snapshot55/55, protected10/10 khớp. HEAD1694133, staged rỗng. Không chạy lại lab/browser/model, measurement134, mutant12 hay clean checkout; không nhận log cũ thành lượt reviewer. GitNexus PDG refresh đã hoàn tất; source và phép kiểm hành vi là bằng chứng chính.

**Chưa nghiệm thu ZER-11/39:** AC-04 và phần dashboard đọc run B0 thật còn thiếu runtime. H-RT1 chưa có được ghi rõ trong runbook; đây là phần thực hiện tiếp theo, không gửi lại fix-01 để sửa các lỗi đã khép. Chưa xin quyền chạy RT1 trước khi harness có thể review được.

### Gói tiếp theo cho Claude — H-RT1 sẵn sàng review, chỉ offline

**Outcome:** biến kế hoạch RT1 trong runbook §5 thành harness chạy được và kiểm được bằng fake/clock offline; trả một gói để Codex review rồi mới xin Hoàng quyền lab. Không tạo issue mới hay mở rộng sang R2/R3/R4. Giữ RT2/BM và O-console là phần riêng đã khai báo, không dùng console H cho operator BM.

**Trước sửa:** đọc lại AC sống đúng workspace, actual HEAD/dirty và hash fix-01. Chụp snapshot nguồn sẽ sửa; ghi file/action scope. Reviewer report, replay, evidence cũ và file ngoài scope chỉ đọc; một writer trong checkout.

**Scope mã:** giữ entrypoint `infrastructure/scripts/verify-dashboard-baselines.sh`; thêm nhánh opt-in RT1 vào `verify-dashboard-baselines.py`, có thể tách đúng một module `infrastructure/scripts/r1_baseline_runtime.py` nếu giúp giữ rõ trách nhiệm. Test ở `tests/test_dashboard_baseline_runtime.py`; CI chỉ thêm lệnh test cần thiết. Cập nhật runbook §5 khi có chi tiết thực thi; bằng chứng mới ở `docs/evidence/ZER-11/rt1-preparation/`, scratch ở `scratch/zer11/claude-rt1/`. Note này append, NOW prepend. Không sửa scorer, contract, event_pipeline, chaos-worker hay fix-01 evidence để phù hợp harness.

**Phải triển khai trọn luồng:**

- Cấu hình explicit context `k3d-zero-door`, nonce/run/trial IDs, source roles, F-01 và ma trận budget hiện có. Default chỉ help/plan/offline; nhánh có hiệu lực cần cờ execute và reference quyền được cấp. Cờ đó không tự cấp quyền cho agent. Không gọi kubectl/Docker/HTTP lab khi chạy suite offline hoặc import module.
- P0–P8 như runbook: preflight, UID/spec/replica baseline và đối tượng trùng tên; tạo đúng tài nguyên do run sở hữu; xác nhận Gaia/Hephaestus 0 pod; positive control riêng; đúng một delete frontend; trial HPA/tải có trần; seal/export; luôn cleanup có deadline và kiểm sau. Lệnh/API qua argv/context rõ, không shell động và không tăng quyền mặc định.
- H-RT1 phát RUN/CONTEXT/TRIAL/ATTACK/EFFECT/RECOVERY/RELAPSE/AUDIT theo nguồn và schema đã khóa. Mốc effect/recovery phải lấy từ mẫu probe thực và `RecoveryMonitor`; controller tạo pod hay HPA scale chưa phải phục hồi nghiệp vụ. Không tự bịa DETECTED/HEAL trong B0. Event cố ý sai ở positive control phải nằm ngoài cohort chính và giữ quarantine/raw.
- Dùng probe/recorder/scorer ZER-9/10 hiện có, không viết phép đo song song. Bảo toàn RUN/TRIAL/INCIDENT correlation, hash config/source, timestamp/clock, raw lỗi, outbox/ack bền và export. Chỉ phát AUDIT_COVERAGE khi quan sát thực sự phủ cửa sổ; watcher/collector lỗi thì ghi thiếu bằng chứng, không tuyên bố không heal.
- Tự dừng theo cap/samples/requests, interrupt và timeout; deadline bao gồm lệnh đang chờ và cleanup. Cleanup chỉ đối tượng tên/nhãn/UID của run; không ghi đè tài nguyên đổi UID/spec ngoài dự kiến. Khôi phục replica sau khi bỏ HPA, ghi rõ đó là cleanup. Không dùng thao tác operator khôi phục làm bằng chứng controller tự chữa.
- Healthy recovery, confirmed-no-effect, timeout có coverage, thiếu mẫu, HPA không kích hoạt và abort phải có verdict đúng. Gaps/thiếu observation không thành TIMEOUT hoặc PASS. Sau export, tái tính bằng CLI và phục vụ đúng root qua serve-results, không sinh dữ liệu giả để thay run thật.

**Tự kiểm trước bàn giao:** fake kubectl/gateway/HTTP/clock để chạy cùng orchestration code của CLI, không một bản mô phỏng song song. Chọn ít ca có sức phân biệt: normal controller, HPA không kích hoạt, nguồn quan sát/ack lỗi, target UID đổi, Ctrl+C giữa trial và cleanup, budget chạm trần. Có positive control cho effect/absence attribution và negative control thiếu coverage. Kiểm tiêu chí dừng không chỉ chuỗi tài liệu; không nhân mutant/suite cho đẹp số. Chạy test trên production pins, hồi quy phần consumer bị ảnh hưởng, security scan và checkout sạch không phụ thuộc scratch. Test mới phải được gọi từ entrypoint/CI thích hợp.

**Bàn giao:** delta manifest/snapshot, test expected/actual và lệnh chạy, cấu hình image thực sẽ dùng (không build), exact phase/resource/action/rollback matrix, tổng ngân sách không vượt plan, residual thật và verdict READY_FOR_RUNTIME_REVIEW hoặc lý do chưa sẵn. Hoàn thành tự review/sửa gom trước khi trả writer Codex. Nếu một điều kiện không thể đáp ứng trong trần thì nêu rõ; không tự nới tiêu chí hay âm thầm tách một checkpoint dở làm gói hoàn tất.

**Giới hạn giữ nguyên:** chưa chạy cluster, Docker/build, fault/load thật, model/API trả phí; chưa commit/push/PR/merge, đổi Linear hay nhắn chat khác. Quyền lab ZER-10 không chuyển sang lượt này. Codex sẽ review harness offline và kế hoạch cụ thể trước khi xin quyền RT1 một lần gom.

## Claude bàn giao H-RT1 ZER-11 + ZER-39 — READY_FOR_RUNTIME_REVIEW (offline) — 21/10/2026

Gói ở [docs/evidence/ZER-11/rt1-preparation](../../../evidence/ZER-11/rt1-preparation/README.md): ma trận pha/thao tác ghi/khôi phục, bảng ca kiểm expected/actual, các lần chạy lỗi giữ lại, residual. Snapshot trước sửa ở `scratch/zer11/claude-rt1/before/`. Delta và kiểm file chỉ đọc ở `rt1-preparation/manifest-rt1.json`. HEAD `1694133`, không đổi nhánh, staged rỗng, 10 protected hash khớp. Không sửa scorer, contract, event_pipeline, chaos-worker, measurement_view hay evidence cũ.

- **Harness:** `infrastructure/scripts/r1_baseline_runtime.py`, chạy qua `verify-dashboard-baselines.py rt1`. Không có `--execute` thì chỉ in ma trận; có `--execute` thì phải kèm `--runtime-approval` và `--context k3d-zero-door`, và cờ này không cấp quyền.
  - Host chạy P0–P7 rồi P8 bằng kubectl argv. Mọi thao tác ghi phải nằm trong `ACTIONS` (22 mục), đúng tên. Xóa có UID precondition, có self-test ở P1. Scale có `--current-replicas`/`--resource-version`. Trần tổng 3600 s, P7 dự trữ 300 s.
  - Pod chạy từ image ZER-10 sẵn có `zero-door/measurement:zer10-574a0c3a2dad` (không build), harness mount từ ConfigMap và được kiểm SHA-256. Pod dùng gateway H/O production, ProbeRunner, `RecoveryMonitor` và bộ đánh giá effect, chỉ trên mẫu đã ack bền.
  - AUDIT_COVERAGE chỉ phát khi theo dõi phủ đủ. Positive control nằm trong run B0 riêng.
  - P8 chấm bằng CLI, `register` rồi kết luận từng trial; không chấm khi thiếu export H/O.
- **Runbook:** mục 5.9 mới; P1/P2/P5/P8 cập nhật. CI thêm `tests/test_dashboard_baseline_runtime.py` vào hai job dashboard; `offline` cũng gọi nó.
- **Kiểm:**
  - Suite H-RT1 có 17 test trên hai production pins: fake kubectl/cluster, fake target, gateway và scorer thật. Ca gồm controller/HPA phục hồi kèm chấm và `serve-results`, HPA không kích hoạt, khoảng trống trong W_eff, TIMEOUT so với MISSING_PROBE, watcher lỗi, pod Gaia xuất hiện, ack H hỏng, UID target đổi, Ctrl+C trong trial và cleanup, trần tổng, trần mẫu, precondition không được tôn trọng, ranh giới.
  - Mutant 12/12; attempt1 10/11 và attempt2 11/12 giữ lại. Fail-before: không có module thì suite không import được.
  - Hồi quy: dashboard33, modes, check_r1_baselines, CI boundary, plan-check, Bandit 0, whitespace.
  - Clean checkout 24 file đạt.
- **Lỗi thật tìm ra và đã sửa trước bàn giao:**
  - RECOVERY_VERIFIED được phát trước `evidence_complete_at`, vì `t_end` là wall cộng monotonic; scorer bắt được.
  - Salvage bỏ export khi lệnh abort lỗi.
  - Deadline tổng không được kiểm trước giới hạn riêng của trial.
  - Manager của `kubectl scale` trên Windows là `kubectl.exe`.
- **Residual:** chưa kiểm được trên cluster thật (`delete --raw -f`, Events/managedFields của k3s, thời gian kubectl, tải có kích hoạt HPA hay không); gateway H/O chạy chung một process như runtime-01; watch dựa trên poll của host; một trial dừng ở (d) thì dừng cả run. Suite có một lượt fail ngắt quãng (15/16 lượt đạt, chưa biết test nào); script hồi quy giờ lưu output khi fail, Codex nên chạy suite vài lần.

Writer trả Codex review harness offline trước khi xin Hoàng quyền RT1 một lần gom. Không lab, Docker, model, commit/push hay Linear. Live AC: connection của Claude không thấy ZER-11/39, nên dựa vào AC Codex đọc lại ngày 21/10.


## Codex review H-RT1 — CHANGES_REQUIRED trước runtime — 21/10/2026

Đã đọc lại AC sống qua linear_zero_door: ZER-11/39 In Progress, đúng workspace zero-door, AC không đổi. HEAD1694133, staged rỗng. Review đúng delta H-RT1:21/21 hash;190read-only và10protected giữ nguyên. [Báo cáo gom](../../../evidence/ZER-11/codex-rt1-review.md), bằng chứng/phản ví dụ ở [codex-rt1-review](../../../evidence/ZER-11/codex-rt1-review/README.md).

Năm lỗi đã xác nhận: **RT1-01 P1** OSError bỏ P7 khôi phục; **RT1-02 P2** kubectl bỏ managedFields theo mặc định khiến P2 abort; **RT1-03 P2** dispatcher ghi đè positive control fail thành ok; **RT1-04 P2** create đã thành công nhưng mất phản hồi để lại namespace mà CLEAN; **RT1-05 P2** dùng Event cũ/downscale để claim phục hồi hiện tại. Phản ví dụ đều offline; source các gói trước không đổi. Hai lượt full suite production đạt17/17; lượt lặp Nemesis lỗi2FAIL+1ERROR với PERSISTENCE/WinError10053, đã giữ nguyên log. Không coi đây là PASS hoặc khẳng định nguyên nhân chỉ do timing. Dashboard33,modes7,CI6,profile,Bandit đạt.

Chưa lab/Docker/model/publication/Linear. Không mở lại dashboard fix-01 đã retest. Gói này chưa sẵn sàng xin quyền RT1.

### Gói Claude sửa gom — rt1-fix-01 (offline)

**Outcome:** sửa trọn RT1-01…05 và phân loại N1 trong một lượt tự review, rồi trả READY_FOR_CODEX_RETEST_OFFLINE. Không thêm issue/R mới, không sửa AC/scorer hoặc hạ chuẩn bằng chứng để qua test. Đọc báo cáo và các script phản ví dụ trước sửa; kiểm expected/actual JSON, không chỉ exit0.

**Trước sửa:** snapshot source H-RT1 hiện tại và test/runbook, hash manifest/protected/dirty; giữ nguyên báo cáo/probe/evidence Codex cùng mọi bằng chứng Claude trước. Một writer. File được sửa: infrastructure/scripts/r1_baseline_runtime.py, tests/test_dashboard_baseline_runtime.py, docs/runbooks/dashboard-and-baselines.md (chỉ phần behavior/verification thay đổi). Chỉ sửa verify-dashboard-baselines.py nếu thực sự cần đồng bộ kết quả/gate CLI theo lỗi đã nêu; ghi lý do và delta. CI đã gọi suite, không cần mở scope khác. Evidence mới docs/evidence/ZER-11/rt1-fix-01/; scratch scratch/zer11/claude-rt1-fix01/. Note chỉ append, NOW chỉ prepend.

**Sửa và chứng minh:**

1. RT1-01: finally luôn thử P7, cả OSError/ValueError bất ngờ. Từng bước cleanup lỗi vẫn thử các bước độc lập còn lại trong deadline; receipt best effort không ngăn restore. Inject lỗi đĩa host ở pha chính và cleanup; kiểm các lệnh restore thực sự được thử.
2. RT1-02: lấy managedFields đúng bằng cờ kubectl cho các query cần ownership; fake trả đúng mặc định khi thiếu cờ. Positive control vẫn bắt manager sai, không bỏ guard.
3. RT1-03: kết quả control fail không bị dispatch success ghi đè. Host kiểm recorded O + REJECTED/MODE_VIOLATION. Retry riêng DECISION/sai classification phải dừng trước P3/P4; control hợp lệ vẫn đạt.
4. RT1-04: reconcile create đã chấp nhận nhưng mất phản hồi theo intent+tên+namespace+nhãn nonce, lấy UID trước cleanup; ownership chưa xác định thì INCOMPLETE/UNKNOWN. Không xóa theo tên, không ghi CLEAN khi còn tài nguyên. Kiểm namespace và đường create dùng chung; không viết framework riêng.
5. RT1-05: giữ/lọc time+UID trial/đối tượng; CTRL cần pod UID mới/ReplicaSet ownership; HPA cần current-trial scale-up do đúng HPA trước recovery. Event cũ/UID khác/downscale không đủ bằng chứng phải ra missing/ambiguous. Giữ scorer/contract chỉ đọc.
6. N1: lưu đầy đủ log, receipt/raw/outbox ở ca fail trước cleanup test. Ba ca cụ thể/log ở report; phân biệt lỗi hệ thống với fake/timing có căn cứ. Không bỏ assert, retry cả suite đến xanh hay nới F-01 runtime. Nếu cần đổi thang thời gian fake, giữ ca lỗi ACK thật như negative control. Nêu giới hạn còn lại chính xác.

**Verification/handoff:** regression focused cho năm lỗi chạy fail-before thật trên snapshot vừa lưu và expected-fixed trên bản mới, đối chứng thành công. Tự review toàn diff và consumer P0–P8, chạy suite mới trên hai production pins, hồi quy dashboard/modes/profile/CI liên quan, Bandit và clean checkout không scratch. Kiểm entrypoint offline không gọi kubectl. Giữ log cả lượt lỗi; không tăng mutant/check chỉ để tăng số. Handoff một gói có source delta/hash, AC map, expected/actual, lệnh chạy, residual/runtime plan đã đồng bộ. Trả writer Codex. Không chạy lab, Docker/build, model/API trả phí, commit/push/PR/merge, Linear hay nhắn agent khác. Codex retest rồi xin Hoàng quyền RT1 đã review.

## Claude sửa rt1-fix-01 ZER-11 + ZER-39 — READY_FOR_CODEX_RETEST_OFFLINE — 21/10/2026

Gói ở [docs/evidence/ZER-11/rt1-fix-01](../../../evidence/ZER-11/rt1-fix-01/README.md): sửa theo finding, fail-before/expected-fixed, phân loại N1, kiểm, residual, lệnh retest. Snapshot trước sửa ở `scratch/zer11/claude-rt1-fix01/before/` + `before.json`. Delta ở `rt1-fix-01/manifest-rt1-fix01.json`. HEAD `1694133`, không đổi nhánh, staged rỗng, 10 protected hash khớp, 246 file chỉ đọc không đổi (gồm báo cáo/probe Codex và evidence H-RT1). Không sửa scorer, contract, event_pipeline, chaos-worker, CI.

- **Đã sửa:**
  - **RT1-01:** P7 nằm trong `finally`; lỗi bất ngờ ở host là abort `UNEXPECTED (...)`; mỗi bước dọn và mỗi đối tượng được cô lập lỗi; DeleteOptions đi qua stdin (`-f -`) nên lệnh xóa không còn phụ thuộc đĩa host; kéo bằng chứng thử lại riêng, không kéo được là `FAILED`; receipt ghi best effort và ghi sau cùng.
  - **RT1-02:** đọc quyền sở hữu field kèm `--show-managed-fields=true`. Kiểm attribution được siết thêm: chỉ tính manager của subresource `scale`. Đây là gia cố, không phải lỗi đã chứng minh.
  - **RT1-03:** `ok` của agent chỉ là dispatch; host tự quyết positive control từ ba dữ kiện đã ghi.
  - **RT1-04:** ghi ý định create trước khi gửi; mất phản hồi thì đọc lại theo tên + namespace + nhãn run, xóa theo UID; tên bị đối tượng khác giữ thì để nguyên, cleanup `INCOMPLETE`; so P0 có thêm namespace.
  - **RT1-05:** claim CTRL cần pod Ready mới của đúng ReplicaSet (UID) và `SuccessfulCreate` nêu tên pod đó; claim HPA cần scale-up của đúng HPA (UID) trong [T_req − 1 s, T_rec − 1 s); thiếu hay mơ hồ thì ra `…_MISSING` / `…_AMBIGUOUS`.
  - CLI `rt1 --execute` in thêm `errors` và trả exit khác 0 khi có lỗi. Lý do: receipt có thể không ghi được.
- **Fail-before / expected-fixed:** 11/11 khớp trên hai cây sạch chỉ khác harness. BEFORE fail ở chế độ isolated và kubectl-default; AFTER đạt.
- **N1:** gồm hai loại, có số liệu:
  - (A) Nghẽn fsync/ACK của host. Đo được `Archive.append` 10,8 s, nghẽn 2,4–2,9 s gây `BASELINE_UNHEALTHY`. Đây là dấu vết `PERSISTENCE` + WinError 10053 của Codex. Harness fail closed đúng. Fake nay giữ hạn ACK ở giá trị production; negative control giữ đường hạn 2 s.
  - (B) Fake hang so deadline callable như số và ném `TypeError` ở request dọn giỏ hàng. Đã chứng minh xác định và sửa fake; runtime không đổi.
  - Clean checkout lần 1 có 1 test Hephaestus fail không truy được, vì script cũ chỉ ghi tóm tắt. Script nay giữ output và file của ca fail; lần 2 đạt.
  - Đợt cuối: tuần tự 8/8 (Nemesis 4, Hephaestus 4); song song 3 tiến trình đạt 3/6, ba ca fail cùng lúc ở cùng một lần nghẽn host (RUN_STARTED ACK hơn 10 s, append 3,7 s), là loại A, đã giữ file.
- **Kiểm:** suite 27/27 trên hai pin; dashboard 33, modes 7, CI 6, check_r1_baselines, plan-check, ma trận rt1, từ chối khi thiếu quyền, Bandit 0, whitespace: OVERALL 0. Clean checkout 24 file: OVERALL 0.
- **Residual:**
  - Cần lab mới kiểm được: `delete --raw -f -` qua stdin (có self-test P1), `subresource: scale` trong managedFields của k3s (thiếu thì fail closed), định dạng Event thật, đồng hồ pod và API server, tải có kích hoạt HPA hay không.
  - Fake vẫn nén các hạn khác ngoài ACK, nên một lần nghẽn fsync vài giây vẫn có thể làm một ca fail. Ca đó phải phân loại bằng `rt1-fix-01/n1/`.
  - Các residual H-RT1 còn nguyên.

Writer trả Codex retest offline. Sau đó mới xin Hoàng quyền RT1 cho bản đã review. Không lab, Docker, model, commit/push hay Linear.


## Codex retest rt1-fix-01 — một P2 còn mở — 21/10/2026

[Báo cáo gom](../../../evidence/ZER-11/codex-rt1-retest01.md): RT1-01…04 khép; RT1-05 còn thiếu thời gian Event ở nhánh CTRL (FXRT1-01). Phản ví dụ độc lập: Event tạo replacement sau T_rec vẫn ra CONTROLLER_RECOVERY_OBSERVED. HPA/UID đã sửa đúng. Không sửa source hay mở lại dashboard/scorer. Đề xuất sửa tối thiểu hàm CTRL/caller + regression thời gian + đoạn runbook; chưa nhắn Claude hoặc cấp quyền mới.

Manifest66/66, read-only246/246 giữ nguyên. Hai pins: Nemesis26/27 (một UNKNOWN_EFFECT thay MISSING_PROBE), Hephaestus27/27; Findings đều đạt. Ca Nemesis có raw: ATTACK_REQUESTED ACK4091.6ms vượt W_eff giả2s, không có mẫu sau T_req, trial MAX_DURATION, cleanup CLEAN. Giữ nguyên log/failure, không chạy lại tới khi xanh; không gán fsync khi lượt này chưa instrument. Dashboard33/modes7/CI6/profile/plan/Bandit đạt; tổng runner exit1. Matrix fail-before đã lưu11/11 được đối chiếu, không chạy full matrix/clean checkout lại.

AC sống ZER-11/39 In Progress qua linear_zero_door, không đổi. HEAD1694133, staged rỗng. CHANGES_REQUIRED trước RT1; chưa lab/Docker/model/publication/Linear. Bằng chứng và source Claude giữ nguyên; chỉ thêm report/probe/log review, append note, prepend NOW.


## Codex sửa trực tiếp FXRT1-01 — PASS_FOCUSED_OFFLINE — 21/10/2026

Hoàng cho phép sửa trực tiếp phần còn lại. [Báo cáo](../../../evidence/ZER-11/codex-rt1-fix02.md): CTRL kiểm đủ T_req/Event/T_rec, dung sai giây như HPA; Event trước trial, thiếu thời gian hoặc tại/sau recovery không được claim controller recovery. Giữ UID/new Ready pod/RS, nhãn scorer và KPI. Runbook đồng bộ.

Fail-before thật: regression mới12ca,10ca sai fail trên source trước sửa,2đối chứng đạt. Sau sửa2method (mới + identity/HPA cũ) đạt trên cả2pins; replay độc lập4/4; luồng fake end-to-end controller/HPA→scorer→dashboard1/1; Bandit0/diff-check sạch. Không chạy full suite tới xanh; failure timing26/27 và raw của review trước giữ nguyên. Snapshot và runner tại scratch/zer11/codex-rt1-fix02; source hash trong report.

FXRT1-01 khép offline; chưa Done. Bước kế xin quyền RT1 theo runbook§5; runtime có thể trả missing/no effect/HPA không kích hoạt. RT2 riêng. HEAD1694133, không staged/commit/push/lab/model/Linear. Writer Codex, không gửi vòng sửa mới sang Claude.


## Codex sửa trực tiếp và chạy RT1 — PASS_SCOPED_RT1 — 21/10/2026

Hoàng cho sửa trực tiếp, rồi duyệt RT1 trong 60 phút, context k3d-zero-door, một pod delete, tải 180 s và khôi phục baseline; không gọi model. Tham chiếu quyền: call_84d20afcbd014088a379b9fc172d89da. [Báo cáo runtime và delta](../../../evidence/ZER-11/runtime-01/README.md).

FXRT1-01 khép. Chạy thật phát hiện image names:null, dry-run trả JSON stream và ownership mất khi scale về 0; đã sửa trực tiếp với fail-before thật. P8 sửa receipt khi Ctrl+C và kiểm root unchanged. Scope gồm harness, CLI, hai test suite và đúng đoạn runbook; không sửa scorer/CI/worker hoặc quota.

Run 573846… hoàn tất trong 606,313 s, cluster cleanup CLEAN. Controller: RECOVERED_UNDETECTED / CONTROLLER_RECOVERY_OBSERVED, TotalRecovery 39,997 s. HPA: CONFIRMED_NO_EFFECT / NO_EFFECT sau phủ 300 s. HPA yêu cầu tăng 1→2→3 nhưng quota chặn thêm pod (2825m + 200m > 3000m); không claim HPA chữa lỗi. Tổng 468 mẫu, 2.230 request probe và 3.599 request tải; audit B0 đủ, 0 action O; positive control quarantine một vi phạm.

Đối chiếu 676 hash raw, N=1; giữ PROBE_GAP, uptime FAIL/UNKNOWN, MISSING/UNKNOWN và một cleanup cart CONNECTION_RESET. Cluster CLEAN không có nghĩa mọi dữ liệu nghiệp vụ đã dọn. Postflight 13 deployment giữ UID/spec/replicas và Ready đúng baseline; HPA/profile/namespace tạm đã vắng, Gaia/Hephaestus trở về 1.

Dashboard/API trả ba file trùng byte; receipt root_unchanged=true; có screenshot và raw. Server và khóa tạm đã dọn. Hồi quy harness 29/29 trên Nemesis; focused 5/5 và ResultsServer 5/5 trên cả hai pin; Bandit 0; 245 nguồn ngoài phạm vi giữ hash. Failure 26/27 cũ vẫn giữ nguyên. HEAD 1694133, staged rỗng; chưa publication hoặc Linear write.

ZER-11/39 chưa Done, G1 chưa đóng: AC-03 còn RT2 MANUAL/RULES runtime theo runbook §5.7 (image mới/P6, quyền riêng), rồi CI/review/merge và Hoàng nghiệm thu. AC-04 có bằng chứng B0 trong giới hạn đã ghi; chưa chứng minh HPA phục hồi. Không gửi vòng sửa mới sang Claude.


## Codex chuẩn bị RT2 trực tiếp — READY_FOR_SCOPED_RT2_REVIEW — 21/10/2026

Hoàng yêu cầu làm tiếp gói chuẩn bị/kiểm offline trước khi xin quyền lab. [Bằng chứng](../../../evidence/ZER-11/rt2-preparation/README.md), [kế hoạch RT2](../../../runbooks/dashboard-and-baselines.md#6-g-zer11-rt2--gói-kiểm-manualrules-trên-image-production). Đã thêm tool bundle/driver/console/assessment, Bash entrypoint và test; nối test vào hai job CI lock. Source production Hephaestus/guard/event_pipeline/scorer và harness RT1 không đổi. HEAD1694133, nhánh cũ giữ nguyên, staged rỗng; writer Codex.

Ba test mới trên mỗi pin đạt với4tiến trình Uvicorn thật và gateway loopback; mode cũ7/7, Bandit0/Bash/diff-check đạt. Assessment chỉ PASS_BOUNDARY_OFFLINE; không suy thành image/runtime. Các ca thiếu lỗi, thiếu audit/RULES, action cấm, guard nhận lệnh và cửa sổ runtime chưa đủ bị từ chối. Log/receipt/snapshot được gom vào reproduction.zip, không có khóa private.

RT2 đề nghị45phút gồm5phút cleanup, một image Hephaestus/namespace tạm, Gaia-Hephaestus0 tạm, một pod frontend delete, tối đa360GET; phục hồi baseline và dọn theoUID. BM dùng observer HTTP có producer/rule_version riêng, không Gaia/KPI. RULES/AI control tách run; không LLM, không human-blind BM claim. Chưa build/import/lab/publication/Linear. Cần Hoàng cấp quyền riêng đúng gói sau review; RT1 không cấp quyền cho lần xóa pod mới. ZER-11/39 chưa Done.


## Codex hoàn tất RT2 — PASS_SCOPED_RT2 / CLEAN — 22/10/2026

Hoàng duyệt call_ceeb7a350665410ab2df1b2bf7a3471b; Codex thực hiện trực tiếp, không giao vòng sửa mới sang Claude. [Báo cáo, receipt và raw](../../../evidence/ZER-11/runtime-02/README.md). Tổng thời gian chung 19 phút 52 giây từ trước build, không reset deadline; đúng một image build/import và một frontend pod delete. Hai lần chuẩn bị lỗi được giữ (digest sai kiểu, timeout kết nối trước fault). Cùng tên namespace được tạo lại sau cleanup sạch; UID mới được ghi, không thêm target hoặc fault. Cận trên GET tổng là 258/360; số thực của lần chuẩn bị lỗi chưa biết chính xác.

RT2 cuối đủ 180,386 s, 81 mẫu (14 lỗi giữ nguyên). BM observer HTTP thật, một MANUAL scripted từ O-console riêng, guard thật trả 409 và consumer có audit disabled; B1 control riêng có đúng một RULES; B2/B3 có audit disabled, không DECISION; không LLM/action. Sáu pod source/image attest đạt, bốn actor giữ source/ENTRYPOINT production; console O-only, token sai và O thiếu token đều 401, control 9140 không tới được từ console. Dừng actor trước seal, 14 envelope O; kiểm raw/causation/cleanup độc lập 98/98. Namespace vắng, 13 deployment giữ UID/full spec/replicas và Ready; quota/HPA/policy không đổi. Không claim Gaia, chất lượng AI, KPI hay human-blind BM.

Runtime delta chỉ siết interval/cap trong driver cùng regression, không nới cap/cửa sổ. Suite 4/4 trên mỗi pin, mode 7/7 trước đó; Bandit không finding, Bash/diff đạt; giữ log cảnh báo parser nosec. Hash bảy nguồn bảo vệ production/RT1 giữ nguyên. Gói chuẩn bị ba test giữ snapshot lịch sử; verification runtime ghi hash cuối. GitNexus được refresh local sau sửa.

RT1 vẫn nguyên, gồm controller recovery 39,997 s, HPA no-effect/quota, PROBE_GAP/MISSING và cleanup cart chưa xác minh. ZER-11/39 có gói kỹ thuật/runtime để nghiệm thu nhưng **chưa Done/G1**: còn quyền publication, CI/review/merge và Hoàng chấp nhận. HEAD 1694133, nhánh hiện có zer-10-independent-measurement, staged rỗng; chưa commit/push/PR/Linear. Bước kế publication đúng allowlist ZER-11/39 sau quyền riêng, giữ dirty ngoài gói.


## Publication được duyệt — ZER-11/39 — 22/10/2026

Hoàng cho phép commit/push và mở PR qua call_4e706a19074148bbb3082807c6248004; chưa cho merge hoặc đổi Linear. Nhánh zer-11-dashboard-baselines được tạo từ origin/main 22a89db, tree trùng baseline 1694133 của evidence. Chỉ stage allowlist gói này; giữ chín file dirty ngoài phạm vi. Evidence được đặt -text riêng để blob Git giữ đúng byte/hash, kể cả CRLF; whitespace trong CLI log/capture/unified diff được giữ theo precedent ZER-9/10. Credential pattern scan bao gồm ZIP lồng nhau đạt; không publication bundle private hoặc scratch. Kế tiếp PR/CI từ xa; chưa Done/G1.
