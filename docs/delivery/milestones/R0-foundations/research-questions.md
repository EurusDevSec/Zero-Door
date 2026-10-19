# Issue — Khóa câu hỏi nghiên cứu và thiết kế đối chứng

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung). Nguồn đối chiếu: `R0-T04`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T04-S01 | Chốt RQ1–RQ3, đóng góp dự kiến và giới hạn claim. | AC của [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung) |
| R0-T04-S02 | Khóa B0/B1/B2, giữ BM; quyết định phạm vi B3 và budget. | AC của [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung) |
| R0-T04-S03 | Chốt ground truth, tập action đúng và ranh giới dữ liệu không lộ đáp án. | AC của [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T04-S01

Bảng câu hỏi → metric → claim; tách đạt chức năng/KPI với chứng minh giá trị nghiên cứu.

### R0-T04-S02

Ma trận đối chứng và điều kiện B3; nếu bỏ B3 thì bỏ claim ưu thế nhiều tác tử, không bỏ cam kết gốc.

### R0-T04-S03

Định nghĩa nhãn, mẫu số metric và schema evidence; bên chữa lỗi không nhận case/attack label hoặc đáp án.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## Gói Claude — ZER-8 và đối chiếu ZER-5 — 19/10/2026, 07:42 +07:00

### Mục tiêu, baseline và quyền

Hoàng yêu cầu soạn công việc tiếp theo cho Claude để khép R0. Gói chính là ZER-8: chuẩn bị thiết kế nghiên cứu đủ review và nghiệm thu; kèm đối chiếu AC ZER-5 từ bằng chứng đã được chấp nhận. Không chuyển trọng tâm sang R1. ZER-8 không bị chặn chỉ vì issue cha ZER-5 chưa đổi trạng thái: prerequisite trực tiếp ZER-32 đã Done.

Codex đã đọc Linear Zero Door ở lượt chuẩn bị ngày 19/10: ZER-32/33/34/35 và ZER-6 Done; ZER-5/8/36/7 Backlog. Đây là snapshot, Claude đọc lại AC sống ZER-8 và ZER-5 khi bắt đầu; chỉ dùng kết nối linear_zero_door. Nếu không truy cập được, dùng AC đã chép trong ghi chú và gói này để chuẩn bị, ghi rõ chưa xác minh live, không giả là Done.

Baseline kiểm lại 07:42 +07:00: HEAD 968cc50f3797c243b8fa26e5327db647a8644802, nhánh zer-34-lab-acceptance. Dirty có sẵn: AGENTS.md, docs/delivery/NOW.md, README.md, WORKFLOW.md và WORKING-AGREEMENT.md untracked (bốn tên sau thuộc docs/delivery). Codex chỉ bổ sung gói vào ghi chú này và con trỏ NOW; Claude chụp lại HEAD/status và hash trước khi làm, phân biệt phần đó với thay đổi mới. Không reset/stash/checkout để làm sạch, không ghi đè công việc ngoài gói. Nhánh publication dự kiến zer-8-research-design, tạo khi publication được giao; gói này không cần đổi nhánh để viết tài liệu.

Claude nhận quyền ghi trong allowlist khi Hoàng chuyển yêu cầu. Được đọc nguồn, viết tài liệu, kiểm offline và tự sửa trong gói đến khi đủ review. Không chạy lab/chaos/heal, gọi API/model, chi tiền, cài framework, sửa source/runtime/config, commit/push/PR/merge, sửa Linear hoặc gửi tin. Codex nhận lại writer sau bàn giao để review cả gói. Quyền nghiệm thu/claim/budget cuối vẫn thuộc Hoàng; không ghi đề xuất thành quyết định đã duyệt.

### Nguồn và file được sửa

Đọc README → WORKING-AGREEMENT → NOW, AC sống hai issue, SCOPE và nguồn thuyết minh/bản trích được SCOPE dẫn; WORKFLOW phần phối hợp/Done. Đọc reference/research-design.md, phần cần thiết của reference/verification.md và artifact ZER-32 đã nghiệm thu. Chỉ tra source hoặc note downstream khi cần xác minh một trường/schema cụ thể; không audit lại toàn repo hay chạy lab để lấy bối cảnh.

Allowlist (đường dẫn tương đối từ repo):

- Tạo docs/evidence/ZER-8/research-design.md: artifact chính, thiết kế đề xuất hoàn chỉnh và AC → evidence → verdict.
- docs/delivery/milestones/R0-foundations/research-questions.md: nối bàn giao/nguồn/quyết định vào cuối, giữ yêu cầu và gói hiện có.
- docs/delivery/milestones/R0-foundations/scope-and-criteria.md: chỉ nối phần đối chiếu ZER-5, không sửa các receipt/handoff 32/33.
- docs/delivery/NOW.md: thêm một con trỏ ngắn về kết quả gói, giữ lịch sử.
- scratch/zer8/: file tạm/bộ tính ví dụ offline nếu cần; không ghi đè file có sẵn. Không bắt buộc tạo checker nếu bảng tính tay có thể kiểm rõ ràng.

Giữ nguyên SCOPE, reference/research-design.md, mọi evidence/review ZER-32/33/34/35 và raw CSV. Artifact mới dẫn nguồn canonical; tránh chép toàn bộ đặc tả thành hai bản. Nếu thấy mâu thuẫn nguồn, ghi vị trí và đề xuất xử lý trong artifact, không tự thay nguồn đã được nghiệm thu.

### ZER-8: đầu ra theo ba AC

**AC-01 — RQ → metric → claim.** Giữ nghĩa RQ1 giá trị LLM, RQ2 giá trị chia vai trò, RQ3 giới hạn guard/fallback của research-design. Với từng RQ, ghi phép so sánh, đơn vị phân tích, metric chính/phụ, dữ liệu tối thiểu, kết luận được phép và kết luận chưa được phép. Tách đạt chức năng/KPI theo thuyết minh khỏi bằng chứng đóng góp nghiên cứu; không bắt buộc AI thắng. Không khẳng định mới/đầu tiên/vượt trội khi chưa có nghiên cứu liên quan và dữ liệu tương ứng. Xác định trước cách báo chênh lệch, failure và độ bất định; số lượt/ước lượng power formal chờ pilot và ZER-53, không tự khóa số đẹp hay tuyên bố đủ mẫu.

**AC-02 — đối chứng và phạm vi B3.** Lập ma trận B0 K8s/controller, B1 RULES, B2 MULTI_LLM, BM MANUAL và phương án B3 SINGLE_LLM. Ghi ai phát hiện/quyết định/thực thi, guard/probe/HPA profile, đầu vào và cost boundary từng nhóm. B0 không có quyết định LLM thì metric LLM là N/A, không gán latency/token 0 như một lượt LLM đúng. B1/B2 dùng cùng nguồn evidence, executor, action budget, guard và probe. B3 nếu thực hiện giữ cùng model/evidence/tools/trần tài nguyên với B2; ghi overhead gọi/token thực tế, không ép số call bằng nhau để che chi phí phối hợp. BM giữ trong cam kết, không lược bỏ để nhường B3.

Benchmark phục hồi replay cùng fault/workload/seed, intensity/duration và profile HPA; xen kẽ thứ tự, xác minh reset, tách pilot khỏi formal, khóa rules/prompt/model trước formal. Nemesis không tự chọn case dễ hơn riêng cho B2. Chức năng lập kế hoạch thích nghi kiểm riêng, không suy lợi ích toàn bộ ba tác tử từ B2 so với B3 chỉ khác Gaia/Hephaestus.

B3/claim/budget chưa có quyết định mới từ Hoàng. Viết một phiếu quyết định ngắn với hai lựa chọn và khuyến nghị có lý do: (a) giữ phép thử B3 để trả lời RQ2 sau khi chốt nguồn lực; (b) không thực hiện B3 thì giới hạn RQ2 thành mô tả phối hợp, bỏ claim ưu thế chia vai trò, giữ mọi cam kết gốc. Định lượng nhu cầu bằng số nhóm × case × lượt × trần call/token và công thức chi phí, không bịa quota/giờ làm/đơn giá/model đã duyệt. Có thể đưa giả định minh họa nhưng gắn nhãn, tách khỏi ngân sách được cấp. Người dùng báo khoảng 300 USD credit OpenAI API; chưa xác minh số dư/quyền model, chưa duyệt dùng hết. Trần 1 USD đang được Codex đề xuất chỉ cho kiểm backend R0, chưa được duyệt và không phải ngân sách formal/B3. Gom quyết định thật còn thiếu để Hoàng chốt một lần sau review; phần này pending acceptance, không tự đánh AC-02 hoàn tất vì đã có bảng.

**AC-03 — ground truth, chấm quyết định và evidence.** Định nghĩa tối thiểu các nhóm C0 tải lành ổn định, C1 tải hợp lệ tăng, C2 DDoS L7, C3 release lỗi/rollback, C4 exhaustion, C5 SQLi fixture. Đây là thiết kế nhãn/phép chấm, không thực hiện vector hoặc dựng catalog runtime ZER-45. Action đúng là tập có điều kiện tiền đề/hậu điều kiện, có thể có nhiều hành động hợp lệ; tránh một đáp án cho mọi CPU/5xx. Giữ scale down, benign traffic, TTL/cleanup và rollback known-good trong yêu cầu gốc; SQLi fixture và uptime Boutique báo tách.

Tách ba mặt dữ liệu trong schema tài liệu: harness/evaluator giữ nguyên nhân, label, effect và tập action chấp nhận; bên chữa lỗi chỉ thấy telemetry/lịch sử vận hành được cấp; người chấm ghép nhờ ID trung tính sau run. Chỉ rõ field, quyền thấy, nguồn, timestamp, thiếu dữ liệu và liên kết evidence. Label/case name/attack command/expected_action không được rò qua prompt, topic truy vấn, đường dẫn file hoặc ID có nghĩa; log vận hành thật như release history/request/IP vẫn được dùng. Đây là contract đề xuất cho ZER-9/37, chưa là schema runtime đã triển khai/khóa.

Khóa định nghĩa mẫu số riêng cho: độ đúng quyết định đầu tiên trước guard; can thiệp thừa/false alarm trong cửa sổ benign; recovery và KPI thời gian. Ghi quy tắc dedup/đơn vị cửa sổ/trigger; phân biệt NO_ACTION/ABSTAIN hợp lệ với im lặng, timeout, schema sai, thiếu telemetry. Missed detection phải hiện trong coverage và kết quả đầu-cuối, không chọn chỉ lượt đã trigger để tuyên bố chất lượng chung. Guard chặn đề xuất sai không biến nó thành quyết định đúng; fallback RULES không nhận nhãn thành công LLM. Unknown ground truth phải hiện và giới hạn claim, không âm thầm loại lượt. Có thể báo metric có điều kiện nếu công bố mẫu số và coverage đầy đủ.

Đối chiếu trực tiếp ZER-32 bản accepted: ngưỡng <60 s, <120/<180 s, ≥99,9%; D-01…D-05 đã chấp nhận; UNKNOWN_EFFECT ở lại N; chỉ CONFIRMED_NO_EFFECT có chứng cứ đủ mới rời N KPI; EMPTY/NO_ELIGIBLE không PASS; probe thiếu không tự up; recovery sau dừng fault báo riêng. Không dùng mẫu số incident cho cửa sổ benign hoặc ép mọi metric dùng cùng N. Giữ F-01…F-09 còn mở đúng ownership; phần ZER-8 đóng semantics và quy tắc phân tích, không bịa effect window/tham số protocol/số lượt formal.

### Đối chiếu ZER-5 trong cùng lượt

Nối vào scope-and-criteria.md bảng ba AC ZER-5 → nguồn/phần/file/revision → bằng chứng chấp nhận → kết luận và khoảng trống. AC-01 đối chiếu SCOPE và nguồn người dùng; AC-02 dùng artifact/review/receipt ZER-32; AC-03 dùng artifact/review/receipt ZER-33. Kiểm đúng file/link/hash và các cam kết Python/Go, Boutique, ba vector, microservices/KPI/sản phẩm/bài được chấp nhận. Không làm lại baseline/ledger đã nghiệm thu hoặc sửa lịch sử để khớp HEAD mới. Nêu riêng phần technical ready với publication/nghiệm thu cha còn chờ; trạng thái con Done không tự đóng cha. Nếu đủ căn cứ, đề nghị Codex/Hoàng nghiệm thu ZER-5, không đổi Linear.

### Tự kiểm và bàn giao một lượt

Tự review toàn bộ artifact và nguồn trực tiếp trước khi trả. Dùng ví dụ giả định ghi rõ OFFLINE để chứng minh cách chấm, không gọi đó là kết quả nghiên cứu. Tối thiểu bao phủ: hai action đều hợp lệ có điều kiện; đề xuất sai bị guard chặn; LLM timeout rồi RULES phục hồi; NO_ACTION hợp lệ so với không có phản hồi; missed detection; UNKNOWN_EFFECT/NO_EFFECT; N=0; khoảng benign có nhiều alert trùng; thiếu nhãn và nguy cơ rò đáp án qua metadata. Với mỗi ca ghi input → expected → kết quả suy ra, tử/mẫu số và giới hạn; ít case rõ ràng có giá trị hơn nhiều assertion lặp nội dung. Nếu viết checker, kiểm một đối chứng sạch và ca lỗi thật để tránh checker luôn PASS/FAIL.

Kiểm đường dẫn/tables/ID, tính nhất quán với ZER-32 và reference, bảo toàn hash nguồn ngoài gói; git diff --check và status cuối. Không chạy lại lab hoặc bộ kiểm cũ phụ thuộc HEAD để tăng số PASS. Mọi ví dụ, giả định cost và pending decision phải phân biệt với runtime/approval.

Bàn giao nối cuối ghi chú này: HEAD/dirty trước và sau, file/hash artifact, thay đổi, AC → kiểm → kết quả, lỗi tự phát hiện/đã sửa, UNKNOWN và quyết định cần Hoàng. Bàn giao ZER-5 nằm trong note của nó; NOW chỉ trỏ hai chỗ. Nếu thiếu quyết định B3 thì trả thiết kế hoàn chỉnh với quyết định pending cụ thể, không để các phần độc lập dang dở hoặc ghi toàn gói Done. Không cần xin phép lại từng bảng/sửa nhỏ đã nằm trong scope. Sau bàn giao nhường writer cho Codex để review cả hai phần; không commit/push/đổi Linear.

## Bàn giao Claude — ZER-8 và đối chiếu ZER-5 — 19/10/2026, 08:00 +07:00

**Kết quả: gói đủ để Codex review cả hai phần.** Claude nhường quyền ghi checkout cho Codex. Không tự đóng ZER-8/ZER-5, không đổi Linear, không commit/push.

**Artifact.** [docs/evidence/ZER-8/research-design.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md), SHA-256 `51ee6e1199a63fdef388ebbbe0857737ae0d146c5ef38742d30b51ff0ec1adfd`, 476 dòng. Đối chiếu ZER-5 nằm ở mục “Đối chiếu nghiệm thu ZER-5 — Claude” cuối [scope-and-criteria.md](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

**Baseline.**
- Trước: 07:45:22 +07:00, nhánh zer-34-lab-acceptance, HEAD 968cc50f3797c243b8fa26e5327db647a8644802, staged rỗng. Dirty có sẵn: AGENTS.md, NOW.md, README.md, WORKFLOW.md, research-questions.md (M) và WORKING-AGREEMENT.md (untracked).
- Sau: HEAD và staged không đổi. Thêm đúng các thay đổi trong allowlist: artifact mới (untracked), scope-and-criteria.md (M, chỉ nối cuối), research-questions.md và NOW.md (chỉ nối/chèn phần mới, giữ phần có sẵn).
- AC sống: Claude không đọc được vì phiên không có linear_zero_door. Dùng snapshot là checklist R0-T04/R0-T01 trong mapping và gói 07:42. Codex cần đối chiếu AC sống.

**AC → kiểm → kết quả.**

| AC | Kiểm | Kết quả |
| --- | --- | --- |
| ZER-8 AC-01 | Bảng RQ → so sánh → đơn vị → metric chính/phụ → dữ liệu tối thiểu → claim được/chưa được (mục 3.1); quy tắc chênh lệch và bất định (3.2); thang claim (3.3) | Đủ để review; metric chính M1 là đề xuất chờ chấp nhận |
| ZER-8 AC-02 | Ma trận B0/B1/B2/B3/BM (4.1); bất biến công bằng (4.2); phiếu B3 có hai lựa chọn, khuyến nghị và công thức nhu cầu (4.4) | **PARTIAL**: thiết kế đủ, quyết định B3/budget PENDING Hoàng |
| ZER-8 AC-03 | Ground truth và tập action có điều kiện C0–C5 (5.1–5.3); kết quả quyết định và mẫu số từng metric (5.4–5.5); ba mặt dữ liệu và kênh rò (5.6–5.7); khớp ZER-32 (5.8) | Đủ để review; là contract đề xuất cho ZER-9/37 |
| ZER-5 AC-01…AC-03 | SCOPE dòng 7–13 và bản trích; hash file và blob ZER-32 tại 8e7b74f, ZER-33 tại 10a26b0; link; ls-remote | Có căn cứ nghiệm thu cả ba; đề nghị Codex/Hoàng nghiệm thu |

**Kiểm offline.**
- `scratch/zer8/score.py` (SHA-256 cb2338666298eb58b052bbcfd9b5136216689511defabc0ac3713ff413246436): 32 OK / 0 FAIL trên 11 incident giả định và cửa sổ benign; mutant 6/6 (đối chứng sạch khớp, năm lỗi mẫu số đều bị bắt).
- `scratch/zer8/check.py`: selftest 6/6 (đối chứng sạch qua; link hỏng, bảng lệch, placeholder, khoảng trắng cuối dòng và hash rút gọn sai đều bị bắt). Kiểm chính gồm 71 nguồn được bảo vệ (62 file docs/delivery và docs/evidence ngoài allowlist, 9 CSV), dirty ngoài phạm vi, append-only, link, bảng, hash rút gọn, git status/HEAD/staged và git diff --check. Kết quả cuối ghi ở lời bàn giao trong chat, vì chạy sau khi nối mục này.
- Scratch bị Git bỏ qua; không phải artifact đã xuất bản.

**Lỗi tự phát hiện và đã sửa trước bàn giao.**
- Hai hash rút gọn trong bảng nguồn sai đuôi (scenario-design, ai-provider) và một hash thiếu ký tự (bản trích). Đã sửa, và thêm kiểm hash rút gọn vào checker.
- Bản nháp xếp P179 vào nhóm KPI báo trên B2. P179 là KPI hiệu lực tấn công, đo trước phòng thủ hoặc trong B0 theo F-06; đã tách.
- Link ZER-56 thiếu slug; đã dùng URL trong mapping.
- Khoảng tin cậy Wilson không áp được cho trung bình macro; đã ghi dùng bootstrap theo khối.

**UNKNOWN và giới hạn.** AC sống; đơn giá, model, quota và số dư credit (ZER-36); quỹ giờ; thời lượng trial thật; tiêu chí effect từng vector (F-05); enum action thật (ZER-50). Ví dụ budget và ví dụ chấm là ILLUSTRATIVE/OFFLINE. Không chạy lab/chaos/heal/API/model, không gọi Docker/Kubernetes, không chi tiền. Build/CI/runtime/merge N/A cho gói tài liệu.

**Quyết định cần Hoàng** (gộp một lần sau review; chi tiết mục 8 artifact):
1. B3 và claim RQ2: khuyến nghị giữ có điều kiện, chốt tại ZER-22 sau pilot ZER-51; hoặc bỏ ngay và giới hạn RQ2.
2. Trần USD cho pilot từ credit API (sau ZER-36), tách khỏi đề xuất 1 USD kiểm R0; quỹ giờ lab và giờ người.
3. Ai vận hành BM và cách che lịch case.
4. Chấp nhận các đề xuất phương pháp: M1 là metric chính RQ1/RQ2, B2 là cấu hình báo KPI phục hồi, R(t) từ effect để so nhóm, quy tắc slot/episode, xử lý trial bị lộ.

**Tiếp theo.** Codex review toàn artifact, đối chiếu AC sống ZER-8/ZER-5, kiểm lại mẫu số, ví dụ OFFLINE và căn cứ nghiệm thu ZER-5; sau đó Hoàng quyết định. Nhánh publication dự kiến zer-8-research-design, tạo khi publication được giao.


## Phạm vi Codex review/fix — ZER-8/ZER-5 — 19/10/2026

Nhận writer từ Claude, baseline HEAD 968cc50f3797c243b8fa26e5327db647a8644802 trên zer-34-lab-acceptance, staged rỗng; artifact nhận SHA-256 51ee6e1199a63fdef388ebbbe0857737ae0d146c5ef38742d30b51ff0ec1adfd. AC sống ZER-8/ZER-5 đã đọc qua linear_zero_door, khớp snapshot; ZER-8 Backlog, ZER-5 In Progress tại lúc đọc.

Phạm vi sửa gọn sau review: artifact docs/evidence/ZER-8/research-design.md; nối review/retest vào ghi chú ZER-8 hiện tại và scope-and-criteria.md; con trỏ NOW; scratch/zer8/codex/ cho baseline, phản ví dụ và kiểm độc lập offline. Giữ nguyên hai script tác giả score.py/check.py, nguồn canonical, evidence 32/33/34/35 và raw; không lab/API/model/cost/publication/Linear. Đã tái lập 32 phép kiểm, 5 mutant và đối chứng sạch, selftest 6/6, kiểm gói 31/31. Phản ví dụ độc lập phát hiện cửa sổ 30 s gây chia 0, cửa sổ 61 s cho tỷ lệ slot 200%, alert ngoài cửa sổ vẫn tăng episode, và guard thiếu ground truth bị coi là chặn nhầm; sẽ sửa ngữ nghĩa và retest cả ranh giới liên quan trước kết luận.


## Codex review/fix và bàn giao — ZER-8/ZER-5 — 19/10/2026, 08:08 +07:00

Đã review toàn gói và tự sửa gom RV8-01…RV8-05 trong artifact; [báo cáo mục 11](../../../evidence/ZER-8/research-design.md). Artifact cuối SHA-256 bb27ff8839b35cac1343f5a57eaaf5db39b3975662df56f2d8075436f93459a5. Không cần gửi lại Claude sửa các lỗi này. AC sống ZER-8/ZER-5 khớp snapshot; trạng thái lúc đọc ZER-8 Backlog, ZER-5 In Progress. ZER-32/33 Done đã đọc receipt.

Kỹ thuật thiết kế đề xuất PASS sau sửa; ZER-8 AC-02 vẫn PARTIAL vì B3/claim/budget chờ Hoàng. ZER-5 đủ căn cứ cả ba AC, chờ Hoàng nghiệm thu riêng. Khuyến nghị giữ B3 có điều kiện trong thiết kế, chấp nhận hướng M1/macro và B2 báo KPI; nguồn lực pilot/formal và cách che lịch BM cần chốt, chưa được cấp từ gói review. Không tự suy thiếu quyết định thành lỗi implementation hay G0 đạt.

Retest độc lập 45/45 OFFLINE; checker selftest 6/6 và kiểm gói cuối 31/31, gồm link/bảng/allowlist sau nối report. Suite tác giả 32/32 và năm mutant/đối chứng sạch giữ nguyên; hai script tác giả bảo toàn hash. 71 nguồn (9 CSV) không đổi; năm blob SCOPE/artifact/review được đối chiếu Git. Phản ví dụ và kết quả nằm scratch/zer8/codex/, chỉ tính giả định. Không source/config/lab/API/cost/commit/push/Linear. HEAD vẫn 968cc50, staged rỗng.


## Hoàng chấp nhận hướng thiết kế ZER-8 — 19/10/2026, 08:14 +07:00

Hoàng đã trả lời “được”: nghiệm thu ZER-5 và chấp nhận hướng giữ B3 có điều kiện, M1 làm metric chính, B2 báo KPI phục hồi. Receipt ở [artifact mục 12](../../../evidence/ZER-8/research-design.md); SHA-256 sau receipt 43715562f431ed1c5cf60747e15d73304cc85508c6e0a6da95936e88e3c8f4b5. Hash bb27ff88…3459a5 trước đó là bản review, không bị phủ nhận bởi thêm receipt này.

Chưa chốt ngân sách/giờ pilot-formal và tổ chức BM; trần 1 USD kiểm backend chưa được duyệt. AC-02 vẫn PARTIAL, không tự đóng ZER-8 hoặc G0. Bước kế tiếp ưu tiên ZER-36/ZER-7 để cụ thể hóa backend, giới hạn và phép thử inference thật trước khi xin quyền chạy/chi tiền. Không hỏi lại B3/M1/B2 đã được chấp nhận. Chỉ sửa receipt/con trỏ, không commit/push/đổi Linear hay chạy lab/API.

### Phạm vi chốt nguồn lực R0 — 19/10/2026, 11:26 +07:00

HEAD df5d542aaf726e62ea8ccb17a94490cd88322ee0 trên zer-5-scope-acceptance, staged rỗng, dirty giữ nguyên theo baseline ZER-36. Hoàng vừa trả lời “Đồng ý gói đề xuất” cho trần pilot/cách tổ chức BM trong chat. File/action scope: cập nhật tóm tắt và nối receipt quyết định vào docs/evidence/ZER-8/research-design.md; nối ghi chú này, gói Claude vào llm-backend.md và con trỏ NOW. Không sửa phương pháp đã review, code/receipt backend, raw 32/33/34/35, SCOPE hoặc dirty quy ước. Không API/lab/publication/Linear. SHA-256 thiết kế trước quyết định 43715562f431ed1c5cf60747e15d73304cc85508c6e0a6da95936e88e3c8f4b5.

### Receipt nguồn lực và tổ chức BM — 19/10/2026, 11:26 +07:00

Đã ghi quyết định trực tiếp của Hoàng ở mục 13 artifact research-design.md, SHA-256 452493abc947a3a78176c33674a6a7d0cb1cf103dc036bfacd6d0e619034aefc. Pilot vòng đầu tối đa 5 USD API, 2 giờ/phiên, 8 giờ lab tổng cộng; Hoàng chạy BM với harness che thứ tự/onset, ghi giới hạn biết thiết kế; trần này không dự báo đủ pilot. Formal khóa sau pilot/ZER-53, B3/M1/B2 đã chấp nhận giữ nguyên. Không tự tăng hard limit project 1 USD hoặc suy quyền chạy lab/API từ quyết định kế hoạch. AC-02 đủ ở mức thiết kế sau quyết định, cả gói chờ nghiệm thu/publication; không đổi Linear. Review nguồn lực và tích hợp G0 được gộp trong gói Claude cuối llm-backend.md.

### RV8-06 sửa và retest sau Claude — 19/10/2026, 11:49 +07:00

Mục5.1 làm rõ Hoàng/Hòa chỉ rà nhãn/A theo variant; harness sinh và niêm phong thứ tự/seed/onset sau đó. Hoàng BM không xem lịch trước/trongtrial; có thểrà sau trial, Hòa rà mức trial nếu cần. Mục5.7 trỏ13 và thêm cờ người vận hành đã thấy lịch/auditUNKNOWN choZER9. AC01/bối cảnhngânsách cậpnhậtcon trỏ P3; quyết địnhB3/M1/B2/pilotgiữnguyên. SHA-256thiếtkế cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8. Không harnessruntime,mãproduction hoặc quyềnpilotmới. Gói đủ kỹ thuật sau sửa,chờ nghiệmthu/publication,gateđối chiếu tại docs/evidence/R0/g0-acceptance.md.

## Receipt nghiệm thu ZER-8 và G0 — 19/10/2026

Hoàng đã chấp nhận bản thiết kế sau RV8-06 và cho phép publication. PR #21 merge250d385, artifact hash cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8 đã đọc lại trên main; CI thành công. Linear read-back ZER-8 Done, ba AC checked, completedAt2026-10-19T05:02:01.802Z. [Receipt G0](../../../evidence/R0/g0-acceptance.md) giữ đối chiếu tích hợp và giới hạn; chưa có quyền chạy pilot hoặc nâng hardlimit.
