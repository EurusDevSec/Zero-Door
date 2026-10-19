# Issue — Xác nhận một backend LLM thật

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that). Nguồn đối chiếu: `R0-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T03-S01 | Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy. | [ZER-36](https://linear.app/zero-door/issue/ZER-36/chon-backend-llm-va-gioi-han-su-dung) |
| R0-T03-S02 | Gọi LLM bằng đầu vào nghiên cứu và kiểm tra đầu ra theo schema. | AC của [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that) |
| R0-T03-S03 | Thử timeout, retry có giới hạn và fallback; ghi rõ khi dùng RULES thay AI. | AC của [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T03-S01

Quyết định provider có căn cứ và cấu hình giới hạn; không suy ra quyền API từ credit Azure.

### R0-T03-S02

Bằng chứng lượt gọi mới có timestamp/run_id, request ID khi backend hỗ trợ, tên/phiên bản model, latency/usage khả dụng và kết quả che bí mật; ghi trường không được provider trả. SDK/manifest/evaluation_report không thay log lượt gọi.

### R0-T03-S03

Log tình huống lỗi và kiểm chứng fallback không bị ghi nhãn là quyết định LLM.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

## Phạm vi phiên Codex — 19/10/2026, 11:09 +07:00

- Đọc AC sống ZER-36 và ZER-7 qua linear_zero_door ngày 19/10; cả hai In Progress. Baseline HEAD df5d542aaf726e62ea8ccb17a94490cd88322ee0, nhánh zer-5-scope-acceptance; dirty có sẵn AGENTS, NOW, README, WORKFLOW, research-questions; untracked WORKING-AGREEMENT và ZER-8. Giữ nguyên ngoài phạm vi. Codex là writer cho probe hướng dẫn Hoàng chạy.
- Nguồn người dùng: key lưu Doppler, GET /v1/models trả HTTP 200; gpt-6-luna hiển thị 180.000.000 TPM / 30.000 RPM; project đã đặt 1 USD và bật hard limit. Đây là báo cáo của Hoàng, chưa phải Codex đọc trực tiếp hay inference receipt. Chấp nhận cấu hình kiểm R0 trong ngữ cảnh hướng dẫn; không suy thành ngân sách pilot/formal.
- File/action allowlist: tạo infrastructure/scripts/verify-llm-backend.py và verify-llm-backend.sh; docs/evidence/ZER-36/test_probe.py và README.md; nối ghi chú này và cập nhật NOW. Scratch zer36 giữ baseline/offline receipts và các lượt chạy JSON. Chỉ probe độc lập, không sửa agent, triển khai hoặc gọi lab. Codex chuẩn bị và kiểm offline; Hoàng gọi live qua Doppler bằng một lệnh sau khi nhận probe. Không commit/push/merge hoặc ghi Linear trong gói này.
- Cố định endpoint OpenAI Responses, model gpt-6-luna, fixture tổng hợp HIGH_CPU theo trường alert Gaia hiện có; schema probe R0 riêng, không khóa event contract R1. Tối đa 2 HTTP attempts/lần chạy (kể cả retry), 512 output tokens/attempt, timeout cứng mỗi tiến trình curl 35 s (curl max-time 30 s), chờ retry 1 s. Không tools, không hành động phục hồi. Fallback RULES luôn degraded, exit khác 0; thiếu usage/refusal/incomplete/sai schema không PASS.
- Dừng nếu auth/quota/budget/config lỗi; không tự đổi model, quyền hay hạn mức. Retry chỉ transport timeout/network và 429 tạm thời/5xx; quota/budget 429 không retry. Bằng chứng lỗi mô phỏng tách OFFLINE; live chưa có receipt.

### Bàn giao probe — 19/10/2026, 11:12 +07:00

- Đã tạo probe + entrypoint Bash, hướng dẫn docs/evidence/ZER-36/README.md, test offline docs/evidence/ZER-36/test_probe.py. 8 nhóm test đạt; bash -n, --help và git diff --check đạt. Receipt kiểm offline ở scratch/zer36/offline-receipt.json. SHA-256 probe Python 37de4d63ca72e4b690b5dbc256c3af6819ce16a3235967928e771188641e9c52.
- 10 file được bảo vệ giữ nguyên SHA-256 từ baseline, gồm dirty quy ước, research-questions/ZER-8 và ba agent. Không sửa lab hoặc mã production. GitNexus lùi một commit tài liệu so với HEAD; đọc source Gaia hiện tại xác nhận các trường, không dùng graph làm bằng chứng hoàn chỉnh.
- Mọi ca timeout/retry/fallback vừa kiểm là OFFLINE_SIMULATED, không log inference thật. Codex chưa gọi Doppler hoặc API; lượt live chờ Hoàng chạy `doppler run -- bash infrastructure/scripts/verify-llm-backend.sh --live`. Tối đa 2 HTTP attempts/512 output tokens mỗi attempt; không chạy lại tự động ngoài giới hạn.
- Receipt mỗi lượt ở scratch/zer36/runs/run-<uuid>/receipt.json, đã che key. Sau khi Hoàng báo kết quả, Codex đọc receipt, xác minh model/schema/request ID/usage/latency rồi đối chiếu đủ AC; chưa Done, chưa commit/push/merge/ghi Linear. Metadata RPM/TPM và hard limit vẫn là nguồn người dùng, không giả thành API read-back.

- GitNexus analyze --index-only đã khởi chạy sau probe; exec session 19594 còn chạy lúc kiểm 11:12 +07, chưa có receipt hoàn tất. Không coi index là đã cập nhật hoặc khởi chạy trùng trước khi kiểm phiên/meta.

### Phạm vi lưu evidence sau lượt live — 19/10/2026, 11:22 +07:00

Đọc lại AC sống ZER-36/ZER-7: cả hai In Progress, không thay body/state. HEAD/dirty giữ nguyên baseline probe. Bổ sung allowlist evidence: docs/evidence/ZER-36/live-receipt.json (bản đã che bí mật, sao chép nguyên byte receipt vừa được Hoàng chạy), offline-cases.json (fault injection, tuyệt đối không inference), verification.md (đối chiếu AC); cập nhật README, ghi chú này và NOW. Không sửa probe đã chạy, không gọi thêm API/đọc Doppler, không publication/Linear.

### Bàn giao sau lượt inference thật — 19/10/2026, 11:22 +07:00

- Hoàng chạy live thành công: run zer36-502a6f48-9bee-4a1a-89a9-a13481898cc9, một HTTP 200 completed, gpt-6-luna, 2969 ms; usage 259 input/68 output/327 total; estimate 0,0000599 USD. Header xác nhận 30.000 RPM/180.000.000 TPM. Hard limit 1 USD vẫn là xác nhận người dùng, không dashboard read-back.
- Raw đã che bí mật sao nguyên byte vào docs/evidence/ZER-36/live-receipt.json SHA-256 688efc5d1b79a9ad68ce34cfc2aca6640a2921621341ad7779c6cc7791035e76. Retest chỉ đọc khớp probe/request hash, schema/expected/usage/cost và nguồn LLM. Không sửa probe, không API trả phí mới.
- Báo cáo docs/evidence/ZER-36/verification.md; offline-cases.json giữ rõ fault injection, không đổi lỗi thành inference thật. AC-01 đủ evidence lựa chọn R0, AC-02 PASS kỹ thuật fixture tổng hợp, AC-03 PASS thành phần bằng fault injection; không là kiểm agent runtime/provider outage. Gói chờ review độc lập và nghiệm thu; chưa commit/push/merge hoặc Linear. 10 file protected giữ nguyên.
- GitNexus phiên 19594 đã hoàn tất exit 0, indexed successfully 2973 nodes/3598 edges/29 clusters/48 flows, cảnh báo field timestamp xuyên ngôn ngữ. Không khởi chạy trùng.

## Gói Claude — review độc lập ZER-36/ZER-7 và đối chiếu G0 — 19/10/2026, 11:28 +07:00

### Kết quả cần trả và quyền

Hoàng muốn khép R0 trước R1. Codex đã viết probe và hướng dẫn Hoàng chạy; Claude nhận **review độc lập** toàn bộ gói backend, phần quyết định mới ZER-8 và gate G0 trong một lượt. Đây không phải yêu cầu dựng adapter R4 hay thực hiện pilot. Codex chỉ nhường quyền ghi sau khi Hoàng chuyển prompt gói này cho Claude; chưa gửi tự động.

Baseline HEAD df5d542aaf726e62ea8ccb17a94490cd88322ee0, nhánh zer-5-scope-acceptance, staged rỗng. Dirty có sẵn: AGENTS.md, NOW.md, README.md, WORKFLOW.md, research-questions.md, llm-backend.md; untracked WORKING-AGREEMENT.md, ZER-8, ZER-36, hai entrypoint probe. Chụp lại Git/hash khi nhận; không reset/gom/commit dirty. Snapshot list R0 vừa đọc trực tiếp Linear: 5/6/32/33/34/35 Done; 36/7 In Progress; 8 Todo. Không suy live status từ đoạn này sau khi bắt đầu.

**Ghi được:** tạo duy nhất docs/evidence/ZER-36/claude-review.md; nối bàn giao vào cuối ghi chú llm-backend.md này, cập nhật con trỏ NOW; scratch/zer36/claude/ cho kiểm riêng. Source probe/test/evidence hiện có chỉ đọc trong lượt review; Codex sẽ sửa gom finding và retest, tránh reviewer tự đổi tác giả rồi coi đó là review độc lập. Không sửa quy ước, SCOPE, ZER-8, evidence 32/33/34/35 hoặc raw receipts. Không Git publication/branch/merge, không Linear write, không API/Doppler/secrets, không Docker/kubectl/lab/cloud. Không cài gói hoặc re-auth MCP chỉ để review. Bash/Git Bash cho mọi terminal command.

### Nguồn phải đọc, theo nhu cầu

1. Delivery README → WORKING-AGREEMENT → NOW, WORKFLOW và R0 README (gate G0); không hydration lại cả repo. Đọc SCOPE khi đối chiếu cam kết.
2. Live ZER-36 + cha ZER-7 và ZER-8 qua linear_zero_door; chỉ kết nối này, xác minh URL zero-door. Nếu không có tools thì dùng snapshot AC trong ghi chú/verification và nguyên văn AC dưới đây, ghi rõ live UNKNOWN; không thêm connector.
3. Toàn bộ hai entrypoint probe, test, README, verification, live-receipt và offline-cases trong bảng hash; ghi chú ai đã làm gì. Không tin mỗi dòng PASS của tác giả.
4. ZER-8 research-design mục 11 (review đã sửa), 12 (B3/M1/B2 đã được Hoàng chấp nhận), 13 (quyết định nguồn lực mới) và bảng AC. Chỉ review tính nhất quán delta quyết định; không yêu cầu chọn lại hướng đã chốt hoặc lặp 45 test cũ nếu không có lý do.
5. Nghiệm thu lab ở cuối local-lab.md và docs/evidence/ZER-34/claude-review.md mục 9; receipt phạm vi/KPI/ledger cuối scope-and-criteria.md và evidence32/33. Chỉ mở raw nguồn được báo cáo dẫn đến khi cần xác minh một khẳng định. Không chạy lại lab để có cùng bằng chứng.

### Snapshot AC và quyết định thật

- ZER-36/7 AC-01: chọn provider/model; xác minh access, quota, token limit, cost mỗi run; quyết định có căn cứ và caps.
- ZER-7 AC-02: lượt mới bằng đầu vào nghiên cứu theo schema; timestamp/run_id/request ID nếu có, model/version/latency/usage khả dụng, che bí mật, khai báo trường provider không trả.
- ZER-7 AC-03: thử timeout/retry giới hạn/fallback; log lỗi, fallback RULES không nhận là LLM. Đánh giá mức fault injection transport có đủ cho **probe R0 độc lập**; không ép mở adapter/agent runtime R4 hoặc ép provider outage thật. Nếu coverage chưa đủ, nêu test offline bắt được hành vi thiếu thay vì kết luận PASS từ tên test.
- ZER-8 AC-01: RQ1–3, đóng góp và claim/metric; AC-02: B0/B1/B2, giữ BM, B3/budget; AC-03: GT, action sets, mẫu số và không lộ đáp án. B3 có điều kiện/M1 chính/B2 báo KPI đã chấp nhận. Quyết định mới: pilot vòng đầu ≤5 USD API, ≤2 giờ/phiên, ≤8 giờ lab tổng; Hoàng BM, harness giấu thứ tự/onset, vẫn biết thiết kế case. Trần không dự báo đủ mẫu/pilot. Formal chưa có budget, khóa ZER-53 sau pilot. Không cần chạy pilot/formal để khóa thiết kế R0.
- Project hiện theo Hoàng đã đặt hard limit 1 USD cho backend; chưa dashboard read-back, không tự tăng thành 5. 300 USD chỉ là nguồn người dùng/screenshot trước, không ngân sách toàn phần. Phân biệt model limits công bố, header rate limit, remaining quota và số dư.

### Review có trọng tâm, rồi bàn giao một lần

- Trace từ Bash wrapper tới HTTP request và validation → labels/fallback/receipt/exit. Soát cap attempts kể cả retry ẩn, timeout thực ở transport, không retry auth/quota, không biến HTTP 200/refusal/incomplete/missing thành success, chi phí thiếu usage không thành zero/complete, secret qua argv/stdout/files, path/temp/overwrite, curlrc/redirect/endpoint.
- Receipt thật: một attempt completed gpt-6-luna, 2969 ms, 259 input +68 output=327, cached/cache-write/reasoning=0, estimated 0,0000599 USD; headers RPM30k/TPM180M; request ID có. Tự kiểm hash/request/schema/usage/timestamps, giá chỉ theo nguồn OpenAI chính thức nếu cần tra lại. Model trả alias, immutable revision UNKNOWN đã khai báo; fixture CPU tổng hợp không chứng minh LLM phát hiện sự cố thật hoặc KPI.
- Offline: chạy python docs/evidence/ZER-36/test_probe.py, bash -n entrypoint; có thể tạo thêm boundary cases trong scratch riêng nếu nhằm bắt lỗi thật. Không lặp test chỉ để tăng số kiểm. Raw offline đánh dấu OFFLINE_SIMULATED, không trộn với LIVE_OPENAI_SYNTHETIC_INPUT.
- G0: lập bảng gate → source/revision → bằng chứng → giới hạn → technical verdict. Lab có giao dịch từ nghiệm thu lịch sử18/10 và mã lab đã merge PR #19; scope/KPI/ledger đã nghiệm thu; backend có receipt mới; RQ/control/GT có review/acceptance và delta nguồn lực mục13. Khác cửa sổ thời gian phải ghi rõ, không tự nhận tất cả đang chạy đồng thời hoặc lab hiện tại đã kiểm lại. Không suy R0 từ số issue Done; chỉ kết luận technical readiness và các bước review/acceptance/publication còn thiếu.
- Kiểm link local, Markdown, hashes bảo toàn và git diff --check. Report tách finding chặn thật với cải tiến không chặn. Finding theo severity, path:line, repro/counterexample, impact, fix đề xuất và retest cần. Không biến giới hạn đã khai báo thành lỗi giả, không bỏ lỗi thật để kịp hôm nay.
- Kết luận riêng ZER-36, ZER-7, ZER-8 và G0; nêu rõ đây là review, chưa Hoàng nghiệm thu hoặc publication. Mã probe mới là code: Done vẫn cần review/verify/merge/accept, không gắn N/A merge vì source nằm ngoài agent. Tài liệu ZER-8 có thể N/A code CI/merge mới nếu đúng phạm vi, không N/A sharing.
- Sau tự kiểm, nối handoff vào note này (report SHA, baseline/diff, checks và giới hạn), NOW chỉ trỏ kết quả, trả một báo cáo để Codex sửa gom/retest. Không tự nhắn chat khác hoặc gọi model mới.

### Hash nguồn lúc giao

| File | SHA-256 |
| --- | --- |
| infrastructure/scripts/verify-llm-backend.py | 37de4d63ca72e4b690b5dbc256c3af6819ce16a3235967928e771188641e9c52 |
| infrastructure/scripts/verify-llm-backend.sh | 7850b18a49783cb22353e4c63235585718484464479df6abc44bc23ce82e777d |
| docs/evidence/ZER-36/test_probe.py | 1564179054f484766a10ffe12d9b9f5e9795ed5ae4564e724ed558b57df99f98 |
| docs/evidence/ZER-36/README.md | 2a9f9d741501542c9786dcbe5082d39bca139eb342ebe63ab4d9e2224ae34cd1 |
| docs/evidence/ZER-36/verification.md | f5a404ef6e8368bc5de592095295b01ea151844661ff8a113ff5d3bf45f143ed |
| docs/evidence/ZER-36/live-receipt.json | 688efc5d1b79a9ad68ce34cfc2aca6640a2921621341ad7779c6cc7791035e76 |
| docs/evidence/ZER-36/offline-cases.json | 0511ad7f7f35fb46768ce41a4c2e179b96096e4c8f05f752056dda197df4ba59 |
| docs/evidence/ZER-8/research-design.md | 452493abc947a3a78176c33674a6a7d0cb1cf103dc036bfacd6d0e619034aefc |

## Bàn giao Claude — review độc lập ZER-36/ZER-7, ZER-8 và G0 — 19/10/2026, 11:40 +07:00

**Báo cáo:** [claude-review.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/claude-review.md), SHA-256 8413a2ab834b606f537b6a7f3e36cdf1a031b5b5bb21f45b5f480112a56fcfbe. Review-only; chưa phải Hoàng nghiệm thu hay publication. Quyền ghi trả lại Codex.

- **Baseline:** HEAD df5d542aaf726e62ea8ccb17a94490cd88322ee0, nhánh zer-5-scope-acceptance, staged rỗng. Tám hash của gói khớp lúc nhận và không đổi sau review. Delta của Claude: tạo báo cáo, nối mục này, chèn con trỏ NOW. Scratch kiểm riêng ở scratch/zer36/claude/.
- **AC sống UNKNOWN với Claude:** không có linear_zero_door, không dùng connector thay thế. Review dựa trên snapshot AC trong gói.
- **Kiểm đã chạy, đều offline:**
  - test_probe 8/8 và `bash -n` đạt.
  - Tái kiểm receipt thật: trùng byte với raw, request/probe hash, validate, usage/cost và timestamp khớp.
  - Đối chiếu giá và giới hạn với trang gpt-6-luna chính thức: khớp; chỉ có snapshot `gpt-6-luna`.
  - Mutation 14 bản probe sửa một chỗ: đối chứng sạch đạt, 7 bị bắt, 7 sống sót.
  - Boundary 10 ca transport giả.
  - check.py của review: selftest 4/4 và kiểm gói, kết quả ghi ở NOW.
  - Không gọi API, Doppler, lab, Git publication hay Linear.
- **Findings P2, nên sửa trước nghiệm thu:**
  - RV36-01: test và log lỗi chưa bảo vệ đường timeout thật `curl_exit_28/6/7` và `--retry 0`. Chỉ sửa test, không sửa probe, để receipt live vẫn khớp revision 37de4d63.
  - RV8-06: mục 5.1 cho Hoàng rà ground truth từng trial (có seed/onset), mâu thuẫn mục 13 Hoàng chạy BM với thứ tự/onset bị giấu. Cần một đoạn làm rõ rà theo variant và niêm phong lịch trial.
- **P3 không chặn:** RV36-02…05, RV8-07, RV8-08, G0-01. Xem báo cáo mục 4.2. Khuyến nghị không sửa mã probe R0 vì P3; chuyển sang adapter R4.
- **Kết luận:**
  - ZER-36: PASS kỹ thuật AC-01.
  - ZER-7: AC-02 PASS; AC-03 PASS về hành vi, cần RV36-01 cho bằng chứng hồi quy.
  - ZER-8: delta nhất quán trừ RV8-06.
  - G0: chưa đóng. Lab và phạm vi đạt; backend đạt kỹ thuật; ZER-8 đạt sau RV8-06. Còn sửa và retest, Hoàng nghiệm thu 36/7/8, commit/PR/CI/merge probe, chia sẻ tài liệu, Linear và receipt G0 riêng.
- **G0-01:** main trên remote là ab80005 (merge PR #20), cây trùng df5d542. Repo chưa ghi sự kiện này.
- **Bước tiếp:** Codex gom sửa RV36-01 và RV8-06 (P3 tùy chọn), chạy lại test và `python -I -B scratch/zer36/claude/mutants.py`, rồi trình Hoàng nghiệm thu. Claude không nhắn chat khác.

## Codex sửa gom và retest — phạm vi 19/10/2026, 11:47 +07:00

Nhận quyền ghi lại từ Claude. HEAD df5d542, staged rỗng; dirty/untracked giữ nguyên như lúc giao review, thêm báo cáo Claude 8413a2ab…6fcfbe. AC sống ZER-7/ZER-8 đã đọc lại, không đổi nội dung; trạng thái cả hai In Progress. Phạm vi sửa: docs/evidence/ZER-36/test_probe.py (RV36-01), .github/workflows/ci.yml (thêm một bước chạy suite offline vào job Bash hiện có), docs/evidence/ZER-8/research-design.md (RV8-06 và các con trỏ P3 liên quan), docs/evidence/ZER-36/README.md và verification.md (giới hạn/provenance); tạo docs/evidence/ZER-36/retest.json để giữ các ca lỗi bổ sung và kết quả mutant; nối handoff vào note này/research-questions và NOW; tạo docs/evidence/R0/g0-acceptance.md làm bản đối chiếu kỹ thuật chờ nghiệm thu, không tự tuyên G0 đạt delivery. Scratch riêng codex-fix giữ baseline/log. Không sửa probe Python/Bash, receipt live, offline log gốc hoặc báo cáo reviewer, không chạy API/lab/publication/Linear. Giới hạn P3 code còn lại ghi cho R1/R4, không mở rộng adapter trong R0.

### Kết quả Codex sửa/retest — 19/10/2026, 11:49 +07:00

Hai P2 đã xử lý: RV36-01 bổ sung test + CIoffline;12/12 test và14/14 mutant của Claude bị bắt, đối chứng sạch đạt. RV8-06 sửa GT theo variant/niêm phong lịch trial trướcBM,5.7/13 nhất quán. Các P3 nội dung/provenance đã bổ sung verification; ba P3code giữ rõ choR1/R4. Probe37de4d63,live receipt688efc5d,báo cáoClaude8413a2ab vàoffline raw giữ nguyên. Retest JSON SHA-256 cf51cbb525e579085cbf21312167c2765486a939f5577414256ee5f6f8b9a4fb. Thiết kế ZER8 SHA-256 cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8. Không API/lab mới.

GitHub PR #20 merged được Codex xác minh: merge ab800056, head df5d542, tree cùng 3c835858;mainls-remotekhớp. Không sửa checkpointpublication lịch sử. Bản đối chiếu gate ở docs/evidence/R0/g0-acceptance.md: bốn vế đủ ở mức kỹ thuật, delivery còn chờ Hoàng nghiệm thu36/7/8 và quyền publication/merge/Linear. Không gọi đó là G0đãđóng; chưacommit/push/PR/CIremote/mergegóimới.

Kiểm cuối 11:52 +07: 14 file publication không có link local hỏng hoặc khoảng trắng cuối dòng, git diff --check sạch. Nhánh dự kiến zer-36-r0-acceptance; staged vẫn rỗng. Nội dung PR đã soạn trong scratch/zer36/codex-fix/pr-body.md, chưa gửi. Gói sẵn sàng trình Hoàng nghiệm thu và cấp quyền commit/push/PR/merge/Linear; job publish-images trên main là hành vi hiện có cần lưu ý khi merge. GitNexus index-only session 95836 còn chạy; không khởi chạy trùng.

## Receipt publication và nghiệm thu — 19/10/2026

Hoàng đã nghiệm thu và cho phép hoàn tất G0. PR #21 merge250d385, CI PR7/7 và main8/8 success, hash probe/live/review giữ nguyên. Linear read-back ZER-36 Done AC1 và ZER-7 Done AC1–3. Chi tiết revision, timestamp, giới hạn và gate tích hợp ở [receipt G0](../../../evidence/R0/g0-acceptance.md). Không gọi thêm API/lab.
