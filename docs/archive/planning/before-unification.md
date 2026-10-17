# Tài liệu trước khi thống nhất cấu trúc

Snapshot 17/10/2026, chỉ để truy vết. Nội dung từng file bên dưới được giữ nguyên văn; đường dẫn cũ tra organization.json. Không cập nhật tiến độ tại đây.


<!-- SOURCE: docs/plans/2026-10-09-research-recovery-roadmap.md -->

## Nguồn `docs/plans/2026-10-09-research-recovery-roadmap.md`

# Roadmap ZERO DOOR đã được tổ chức lại

Kế hoạch hiện hành nằm tại [docs/recovery/README.md](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md). Mở [NOW.md — việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md) để bắt đầu phiên, rồi mở đúng file task.

Mỗi phase có thư mục riêng, mỗi task có file riêng; không đặt ngày ở đầu tên file kế hoạch đang làm. Giữ nguyên **8 phase, 27 task, 92 subtask**, ID, lịch và tiêu chí nghiệm thu.

[Bản đầy đủ trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md) được giữ nguyên làm lịch sử, gồm ngày gốc và lịch điều chỉnh 17/10/2026. Không cập nhật tiến độ trong bản snapshot hoặc file dẫn đường này.

Đường dẫn này được giữ để các trao đổi/link cũ vẫn tìm được kế hoạch.

<!-- END SOURCE: docs/plans/2026-10-09-research-recovery-roadmap.md -->


<!-- SOURCE: docs/plans/README.md -->

## Nguồn `docs/plans/README.md`

# Kế hoạch ZERO DOOR

Delivery tracking: [Linear Zero Door](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md).

Scope và technical checkpoint: [Recovery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md).

Việc tiếp theo: [NOW](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md), rồi mở file task tương ứng. Mỗi phase/task có tên theo ID và chức năng, không đặt ngày ở đầu.

File roadmap có ngày trong thư mục này là đường dẫn tương thích cho các trao đổi cũ; bản đầy đủ trước khi tách được giữ trong `docs/recovery/archive/`. Không cập nhật hai kế hoạch song song.

<!-- END SOURCE: docs/plans/README.md -->


<!-- SOURCE: docs/recovery/NOW.md -->

## Nguồn `docs/recovery/NOW.md`

# Checkpoint và việc tiếp theo

[Delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md) · [Tổng quan repo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

## Checkpoint hiện tại — 17/10/2026

- Đã đọc canonical Linear Project Kit theo đúng thứ tự, đối chiếu scope và Git; giữ nguyên 8 gate, 27 task, 92 ID subtask nguồn.
- Hoàng chọn sub-issue độc lập; issue sửa mã cần review + kiểm chứng + merge + Hoàng chấp nhận để Done.
- Đã chuẩn bị mapping, template, QA policy và một issue inventory đầy đủ để review. Metadata Markdown được đóng băng thành snapshot; không là board sống.
- **Kết nối đã xác minh:** linear_zero_door đọc đúng workspace zero-door/team ZER, Hoàng và Hòa thuộc team. Danh sách project hiện rỗng; có 4 issue hướng dẫn ban đầu, chưa có backlog nghiên cứu được nhập. Chưa create/update/assign milestone hoặc issue; chưa gửi Slack. Xem [CONNECTION](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/CONNECTION.md).

## Việc tiếp theo cho delivery setup

1. Kết nối đã nạp và đúng workspace; dùng lại linear_zero_door, không tạo lại. Review project outcome/import plan và phạm vi tạo dữ liệu ở workspace Zero Door trước khi apply. Chưa có project ID vì truy vấn hiện không có project.
2. Đọc project/milestone/issue bodies/relations hiện có, review duplicate và actual workflow; chốt evidence sharing, metadata cần áp và phạm vi publish. Không cần lặp lại quyết định sub-issue/Done đã chốt.
3. Apply theo [import plan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/IMPORT_PLAN.md) khi đủ quyền, rồi read back ID/URL/parent/milestone/dependencies. Cập nhật live metadata ở Linear, mapping chỉ lưu alias/ID/URL.

## Đầu việc kỹ thuật nguồn, chưa khởi chạy

- Inventory chỉ đọc: [R0-T02 / S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T02-local-lab.md).
- Baseline/source ledger: [R0-T01 / S03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md).
- Draft event contract: [R1-T01 / S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T01-event-contract.md), có thể chuẩn bị trước lab/LLM.

Đây là pointer tới kế hoạch nguồn, không tuyên bố các issue đã Ready trên Linear. Chưa mở lab, gọi model, triển khai feature, commit/push/deploy hoặc dùng tiền trong lượt thiết lập tracking. Không tự gửi task sang phiên Claude. Khi triển khai, checkpoint kỹ thuật ở file task; trạng thái và AC delivery sống ở Linear.

<!-- END SOURCE: docs/recovery/NOW.md -->


<!-- SOURCE: docs/recovery/README.md -->

## Nguồn `docs/recovery/README.md`

# ZERO DOOR — Kế hoạch hoàn thiện

**Theo dõi delivery:** [Linear Zero Door — thiết lập và mapping](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Bắt đầu mỗi phiên bằng [NOW — checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md), rồi issue Linear được giao và file kỹ thuật liên quan. Đọc [SCOPE — cam kết nghiên cứu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/SCOPE.md) khi cần kiểm scope; [WORKFLOW — cách cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) quy định owner/evidence/bàn giao.

Đây là đầu mối kế hoạch hiện hành, tách từ roadmap đã cập nhật 17/10/2026. Giữ nguồn **8 phase, 27 task, 92 subtask** và toàn bộ ID/tiêu chí để trace. Chuyển thành milestone/issue và sub-issue chọn lọc; các bước nhỏ giữ AC/checklist. Linear là live issue/state/AC SSOT; các file task là nguồn nhập và technical checkpoint, metadata cũ đã đóng băng. Kết nối linear_zero_door đã xác minh đúng workspace/team; danh sách project hiện rỗng nên chưa có project ID hoặc backlog được nhập. Chưa có đối tượng mới được tạo.

## Nguồn milestone / issue

| Phase | Nội dung |
| --- | --- |
| [R0](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/README.md) | Nền tảng và phạm vi |
| [R1](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/README.md) | Sự kiện và phép đo |
| [R2](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/README.md) | Ba kịch bản Chaos |
| [R3](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/README.md) | Phục hồi và block IP |
| [R4](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/README.md) | Tác tử và LLM |
| [R5](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/README.md) | Tích hợp và pilot |
| [R6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/README.md) | Thực nghiệm và bài báo |
| [R7](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/README.md) | Phản biện và nghiệm thu |

## Các mốc nguồn để đối chiếu, chưa áp metadata Linear

- **31/10/2026:** mục tiêu kỹ thuật/pilot, lịch đang rất sát và chưa có dự báo công sức bảo đảm.
- **14/11/2026:** mục tiêu nội bộ nộp paper đầu; phụ thuộc đợt nhận bài.
- **31/12/2026:** hạn Hoàng cung cấp; cần đối chiếu hồ sơ trường. Bài nộp và bài được chấp nhận là hai mốc riêng.

Ngày trong phase/task là snapshot lịch nguồn; dates delivery sống thuộc Linear sau khi metadata được xác nhận. Ngày gốc 09/10 và điều chỉnh 17/10 được bảo toàn trong [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Không thay tiêu chí hoặc ghi DONE để kịp lịch.

## Tra cứu khi cần

- [Thiết kế nghiên cứu, RQ và đối chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/research-design.md)
- [Phép đo và kiểm chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/verification.md)
- [AI và provider](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/ai-provider.md)
- [Audit/handoff và các đính chính](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/audit-findings.md)
- [Các gói sửa W0–W6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/work-packages.md)
- [Paper/báo cáo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/publication.md)
- [Mốc kiểm soát khi lệch lịch](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/reference/checkpoints.md)

Các phase tháng 7 trong docs/phases và các file handoff/audit có ngày là tài liệu lịch sử, không phải kế hoạch thực thi hiện hành. Claude Code là cộng tác viên phát triển; backend LLM trong ZERO DOOR chưa được chọn chỉ vì dùng Claude.

<!-- END SOURCE: docs/recovery/README.md -->


<!-- SOURCE: docs/recovery/SCOPE.md -->

## Nguồn `docs/recovery/SCOPE.md`

# Phạm vi và tiêu chí nghiên cứu

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

## Phạm vi đã được người dùng chốt

- Bản thuyết minh đã cung cấp là bản đăng ký chính thức, không có bản điều chỉnh khác. Người dùng xác nhận thầy đã cho đổi sang Python/Go và Google Online Boutique được đề xuất từ ban đầu. Không yêu cầu quay lại Java/Spring AI chỉ để khớp tài liệu cũ; ghi rõ lựa chọn được xác nhận này trong báo cáo.
- **Nguồn thời hạn:** DOCX được cung cấp ghi thời gian từ tháng 01 đến tháng 06/2026, ngày trên văn bản 04/01/2026; hạn 31/12/2026 là xác nhận mới nhất của Hoàng với Codex. Giữ lịch tháng 12 để điều phối, đồng thời ghi khoảng trống nguồn giải thích khác biệt tại R0-T01-S03 và đối chiếu hồ sơ tại R7-T02-S05. Không coi ngày trên tài liệu là ngày ký/nộp/duyệt đã được chứng minh, cũng không tự kết luận có hay không có gia hạn.
- Vẫn phải hoàn thành SQL Injection, DDoS tầng ứng dụng, Resource Exhaustion; scale up/down, block IP và rollback; MTTD <60s, MTTR <2–3 phút, uptime ≥99,9% theo phạm vi thực nghiệm đã định nghĩa.
- **Xác nhận hiện hành 17/10:** Hoàng quyết định trước hết vẫn làm cả ba vector dù đã trao đổi việc thầy khuyên thu hẹp và chọn SQLi. Không dùng SQLi-only làm scope hiện tại, cũng không tự ghi thầy vừa phê duyệt lại cả ba. Phản hồi của thầy về block IP được phản ánh vào R3-T02: phải chặn được nguồn thay vì phát hiện/phục hồi lặp mãi.
- **Đối chiếu DOCX trực tiếp ngày 17/10:** ngoài KPI tổng, P179 có CPU của target app >80%, P187 có phản ứng <1 phút; P100 yêu cầu cô lập và hồi phục không cần can thiệp, P109 dashboard thời gian thực, P176 tích hợp LLM; sản phẩm gồm source/manifests, video, bảng đo, báo cáo, slide/poster. Các mốc phản ứng/phát hiện/hồi phục và mẫu số CPU phải được định nghĩa riêng tại R0-T01-S02/R1, không tự đồng nhất. Xem [bản trích có hash/vị trí đoạn](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md).
- Bài cần được chấp nhận đăng trong kỷ yếu trường trước nghiệm thu. Tên kỷ yếu, thông báo nhận bài, mẫu bài và lịch nhận bài chưa có; người dùng chọn chốt sau. Các mốc nộp bài dưới đây là mục tiêu nội bộ, không phải lịch do trường xác nhận.
- Người đang trao đổi là **Lê Văn Hoàng**, phụ trách kỹ thuật. **Nguyễn Ngọc Hòa** phụ trách báo cáo Word. Nội dung và kết luận khoa học cần hai người cùng đối chiếu với dữ liệu và giảng viên hướng dẫn.
- Hoàng trước đây nói khoảng 10 giờ/tuần, sau đó ngày 17/10 muốn tăng cường làm việc có kiểm soát cho ZERO DOOR và Zero-D-Rift. Chưa có quỹ giờ mới được xác nhận; không tiếp tục coi “30h còn lại trong tháng” của lịch 09/10 là nguồn lực hiện có. Lịch mới là mục tiêu theo phụ thuộc, không phải cam kết đủ người/giờ. Codex/Claude hỗ trợ thực hiện và review theo task; Hoàng giữ quyết định kỹ thuật, provider/chi phí và các thay đổi lab có hệ quả.
- Cloud cũ đã tắt. Hạ tầng cloud và dùng credit Azure cho compute được hoãn; lab chạy trên máy hiện tại. Có Azure for Students khoảng 100 USD theo người dùng, nhưng chưa kiểm tra số dư, quyền model, quota hoặc endpoint của subscription.

[Rà soát nguồn và dữ liệu](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-research-alignment-audit.md) là căn cứ cho các gói sửa. Những nhận xét trong bản rà soát về việc phải xác nhận đổi stack đã được giải quyết bằng thông tin trực tiếp của người dùng ở trên. Các phát hiện về SQLi, rollback, telemetry và dữ liệu chưa thay đổi.

## Việc hoãn và thứ tự bắt đầu

Hoãn triển khai Azure compute/cloud cũ, SaaS đa khách hàng, framework agent lớn, RAG/vector DB, training/RL, nhiều LLM, so sánh cloud–local và viết lại Boutique. Không xem việc có credit là lý do mở rộng hạ tầng.

Gói đầu tiên là **inventory/baseline W0 và bản nháp W1** theo hàng đợi 17/10. Provider được chốt/test theo R0-T03; không buộc bản nháp contract hoặc mọi test rules chờ LLM. Sau contract review và preflight, mở task mã với đường dẫn/test cụ thể, sửa phép đo/guard rồi vector/healer, sau đó AI và thực nghiệm đối chứng. Lượt cập nhật này chỉ sửa roadmap; chưa tạo artifact của hàng đợi, sửa ứng dụng, chạy lab/test/LLM, cài model hoặc tạo tài nguyên trả phí.

Các lịch trong Markdown là snapshot nguồn; lịch delivery sống thuộc Linear sau khi xác minh đúng project. Repo giữ scope/tiêu chí nghiên cứu và bằng chứng; issue AC phải phù hợp các cam kết này, không tự thay scope. Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md).

<!-- END SOURCE: docs/recovery/SCOPE.md -->


<!-- SOURCE: docs/recovery/WORKFLOW.md -->

## Nguồn `docs/recovery/WORKFLOW.md`

# Cách làm việc với Linear và repo

[Delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md) · [Checkpoint phiên](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

## Nguồn chuẩn

Linear Zero Door giữ live outcome/AC, status, assignee, priority, estimate, dates, parent/milestone và dependencies. Git/repo giữ code/revision/PR/CI/merge, scope nghiên cứu, thiết kế, file plan và bằng chứng. Slack chỉ phối hợp theo yêu cầu. Bản task/phase Markdown hiện là nguồn migration và technical checkpoint, không duy trì live board thứ hai.

Kết nối linear_zero_door đã xác minh workspace zero-door, team ZER; hiện không có project truy cập được. Không lấy snapshot làm live issue state hoặc lấy S-cool/EUR làm đích thay thế. Project/backlog chưa được tạo trong lượt kiểm tra kết nối. Xem DISCOVERY.md trong thư mục linear để biết các quyết định OPEN.

## Đầu một phiên

1. Đọc NOW.md, mở issue Linear được giao và đúng technical checkpoint. Chỉ đọc reference cần thiết; không hydration lại toàn repo.
2. Xác minh Linear ID/URL và phiên bản AC/timestamp truy xuất; kiểm dependency thật, HEAD/dirty và phạm vi file/thao tác, kể cả file test/probe mới. Linear ID là delivery key; R0-T02-S01 là alias provenance.
3. Khi không có quyền truy cập Linear, có thể dùng handoff tự đủ bối cảnh với AC snapshot có ngày, scope, dependency revision, verification và quyền. Ghi live state unverified; không coi snapshot là AC/status mới nhất hoặc tự đóng issue.

## Khi thực hiện và bàn giao

- Một bên ghi/Git mutation trên một checkout tại một thời điểm; bên kia review/đọc. Worktree riêng cần bố trí và bàn giao rõ trước khi chạy đồng thời. Giữ dirty work ngoài scope, không git add toàn bộ.
- Checkpoint ghi file plan, actual HEAD/dirty, command/scenario, time/timezone, environment, result/limits, durable evidence và next action. Không copy toàn issue hoặc duy trì status/due/assignee trong Markdown.
- Chỉ cập nhật Linear field/comment/assignment trong phạm vi được giao; không tự gửi Slack. Tên người/agent không thay metadata trong technical issue body. Việc Hòa tham gia workspace không tự gán Hòa vào issue.
- File local R: chưa đủ để reviewer khác truy cập; dùng shared artifact/URL đã duyệt, gắn revision và che dữ liệu nhạy cảm. Docs dirty chưa có link GitHub blob hợp lệ.

## Ready / Done / milestone

Ready khi outcome, scope, AC, quyết định bắt buộc, dependencies, metadata và verification đủ rõ. Workflow mapping theo status thật của Zero Door còn OPEN; không đổi tên/status team. Draft contract có thể chuẩn bị trước lab/LLM, nhưng triển khai consumer vẫn chờ contract khóa. Ngày/milestone order hoặc staffing order không tự thành blocked-by.

Issue sửa mã Done khi review, kiểm chứng, merge và Hoàng chấp nhận. Quy tắc đó không cấp quyền commit/push/merge. Issue report/research/documentation nghiệm thu theo AC/evidence phù hợp; N/A có lý do. Report QA có thể hoàn tất với product case fail, nhưng product/milestone gate không tự pass.

Milestone cần integrated acceptance và evidence riêng; progress 100%/child Done không đủ. G5 và G7 vẫn giữ yêu cầu nguồn trong repo. Scope/KPI không tự thay vì sửa một issue, hết hạn hoặc số liệu chưa đẹp. Nộp bài, chấp nhận đăng và nghiệm thu là các mốc riêng.

## Lịch, năng lực và phát sinh

Lịch 17/10 trong task/phase là snapshot nguồn. Chưa tự áp due/estimate/cycle hay tạo ngày mới trên Linear; capacity tăng cường chưa có số giờ xác nhận. Giữ 31/10 kỹ thuật, 14/11 paper và 31/12 nghiệm thu như mốc nguồn với giới hạn đã nêu trong SCOPE, không suy thành lịch trường đã chốt.

Khi được phép đổi lịch, giữ provenance, lý do, ảnh hưởng và metadata mới trên Linear; không âm thầm dời ngày hoặc dựng một bảng lịch sống khác trong repo. Defect phát sinh có scope, AC, evidence/repro và retest; không tạo issue sửa lỗi chung chung chỉ để lấp chỗ.

## Quy ước cấu trúc

- Không đặt ngày đầu tên file kế hoạch hiện hành. Giữ folders R0–R7 và file task để tìm nhanh source/checkpoint; mã Linear được liên kết sau xác minh/apply.
- Chỉ tách sub-issue có đầu ra/acceptance riêng; checkbox nhỏ nằm trong AC. Mapping giữ đủ 92 ID nguồn, không phải 92 ticket bắt buộc.
- README dẫn đường, NOW ghi checkpoint/next action, SCOPE giữ cam kết, reference giữ phương pháp. Metadata task cũ đóng băng, archive giữ lịch sử; không sửa snapshot thành live board.
- Canonical kit là nguồn mẫu dùng chung, không là workflow live. Không sửa master hoặc áp ngoại lệ/nhân sự/stack S-cool.

Bản workflow trước migration được giữ ở [archive](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/workflow-before-linear.md). [QA/Done](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/QA_AND_DONE.md) quy định chứng cứ; [import plan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/IMPORT_PLAN.md) quy định bước apply/read-back khi đúng đích và đủ quyền.

<!-- END SOURCE: docs/recovery/WORKFLOW.md -->


<!-- SOURCE: docs/recovery/linear/CONNECTION.md -->

## Nguồn `docs/recovery/linear/CONNECTION.md`

# Kết nối Linear Zero Door

## Dùng lại ở các phiên sau

| Yêu cầu của Hoàng | Kết nối chọn | Mức xác minh hiện tại |
| --- | --- | --- |
| ZERO DOOR / workspace zero-door | MCP `linear_zero_door` đã lưu trong cấu hình global Codex | Đã xác minh workspace zero-door/team ZER và thành viên; project list hiện rỗng |
| S-cool / workspace eurusdevsec | Connector Linear có sẵn của Apps | Đã quan sát trả team EurusDevSec và project S-cool trong discovery trước |

Đây là định tuyến sử dụng lại, không phải yêu cầu tạo kết nối mỗi lần. Cấu hình global được lưu trên máy; sau khi nạp và xác minh xong, các phiên sau chọn kết nối hiện có theo workspace được yêu cầu. Trước mutation kiểm đúng workspace/project ID; không đổi token hoặc tạo server mới chỉ vì đổi repo/project.

Nếu một workspace mới chưa từng cấp quyền, cần setup/xác thực riêng lần đầu. Nếu quyền bị thu hồi hoặc phiên xác thực cần đăng nhập lại, xử lý đúng connection đó; không thể cam kết không bao giờ phải re-authenticate. Nếu chỉ thiếu tool trong chat cũ, nạp lại client trước, không coi đó là mất cấu hình. Codex và Claude Code dùng cấu hình/auth riêng theo từng client.

## Checkpoint 17/10/2026

- Đã thêm MCP riêng `linear_zero_door` vào cấu hình Codex của máy hiện tại bằng CLI có sẵn.
- Transport: Streamable HTTP; endpoint chính thức `https://mcp.linear.app/mcp`.
- CLI báo `Successfully logged in.` và cấu hình đọc lại có `enabled: true`.
- Giữ connector Linear/EurusDevSec đang dùng cho S-cool; không sửa hoặc gỡ connector đó.
- Cấu hình trước thay đổi được sao lưu ở `C:/Users/ACER/.codex/config.toml.before-linear-zero-door.bak`. Không đưa nội dung cấu hình hoặc credential vào Git/evidence.
- Chưa tạo/sửa milestone, issue, assignment, workflow hoặc Slack. Việc cấp OAuth không đồng nghĩa đã xác minh workspace Zero Door.

## Read-back sau restart — 17/10/2026

- Tools `mcp__linear_zero_door__*` đã nạp và hoạt động.
- `list_teams`: một team Zero-Door, key **ZER**, ID `865d41a7-ef26-474c-a9f8-36e781569fc8`.
- URL issue trả về thuộc `https://linear.app/zero-door/issue/`, xác minh đúng workspace đích.
- `get_user me`: Lê Văn Hoàng, ID `99fe281d-6b71-41a3-8c8e-76be59884dc7`, active, thuộc team ZER.
- Hòa: tài khoản Hoa8001, ID `95925f55-11a6-4a02-ae0c-70e823f50d5f`, active, thuộc team ZER. Cả hai profile hiện có cờ admin; chỉ quan sát, không sửa role hoặc assignment.
- `list_projects` có `includeArchived: true`, limit 10: trả rỗng, hasNextPage false. Chưa có project ID truy cập được, không suy thành project đã được tạo.
- `list_issues` team ZER: ZER-1 đến ZER-4 là các issue hướng dẫn ban đầu, không có project; không sửa/xóa chúng.
- Status catalog hiện có: Backlog, Todo, In Progress, In Review, Done, Canceled, Duplicate. `Todo` chỉ tương ứng Ready sau quality gate; không tạo status READY mới. ID đã lưu trong mapping, không copy live trạng thái từng issue.
- Lần list project đầu yêu cầu nested fields quá nhiều bị complexity 400; retry với fields tối thiểu đã thành công. Không phải lỗi OAuth hoặc sai workspace.
- Đây là kiểm tra quyền đọc. Chưa thử ghi, tạo project/milestone/issue, gán người hoặc gửi Slack.

## Bước tiếp theo

1. Dùng lại `linear_zero_door`; không cần tạo kết nối hoặc đăng nhập lại cho các lần truy cập thông thường khi quyền còn hiệu lực.
2. Khi mở bước import, review outcome/project mới và object mapping, đọc labels/templates cần dùng và duplicate check lại. Project hiện chưa có ID, không tự mượn project S-cool để điền.
3. Nếu kết nối mới vẫn thấy workspace cũ, xử lý riêng ngữ cảnh xác thực của kết nối mới theo hướng dẫn chính thức; không xóa toàn bộ credential hoặc gỡ kết nối S-cool.
4. Cập nhật mapping chỉ khi đã đọc được ID/URL thực tế. OAuth thành công chưa là kiểm chứng project, permission hoặc publish.

Tham khảo: [Linear MCP — authentication theo workspace](https://linear.app/docs/mcp#faq), [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp). Đây là cấu hình local máy hiện tại; Claude Code cần cấu hình trong client của nó nếu muốn dùng MCP trực tiếp, không tự thừa hưởng auth của Codex.

<!-- END SOURCE: docs/recovery/linear/CONNECTION.md -->


<!-- SOURCE: docs/recovery/linear/DISCOVERY.md -->

## Nguồn `docs/recovery/linear/DISCOVERY.md`

# Discovery trước khi chuyển Linear

## Baseline và nguồn

- Repo `https://github.com/EurusDevSec/Zero-Door`, branch `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`. Nhiều tài liệu dirty/untracked; không commit/push hoặc đụng mã ứng dụng trong lượt này.
- Scope Python/Go + Boutique, ba vector, recovery/KPI/paper theo SCOPE. Không kế thừa claim Complete hoặc kết quả tháng 7 làm runtime proof.
- Nguồn kế hoạch: 8 phase/gate, 27 task, 92 subtask. Giữ mã R0–R7 để truy vết; Linear ID sau khi tạo là định danh delivery chuẩn.
- Kit v1.0 đã đọc đủ năm file theo thứ tự. Hash bốn nội dung khớp manifest trong entrypoint. Không sao chép backlog, nhân sự, dates hoặc ngoại lệ S-cool.

## Discovery connector — chỉ đọc

- Hoàng xác nhận đích `https://linear.app/zero-door/projects/all`.
- Connector chỉ trả team EurusDevSec (EUR), ID `397fd69e-4035-4653-9466-458490f18a9c`, và hai project S-cool. Tìm project `zero` không có kết quả trong connection này.
- Tìm email Hòa được cung cấp không có kết quả trong connection này. Không suy ra Hòa chưa được mời vào Zero Door; membership workspace đích chưa được kiểm chứng.
- Các statuses, labels và templates đọc được thuộc EurusDevSec. Không dùng chúng làm mapping chính thức cho Zero Door, không tái dùng ID EUR hoặc label chuyên S-cool.
- Chưa đọc được đúng project/milestones/issues/members/relations ở Zero Door. Duplicate check chưa hoàn tất; không kết luận target trống hoặc phải tạo project mới.

## Xung đột đã báo trước khi viết

| Xung đột | Cách thích nghi |
| --- | --- |
| Markdown đang là live status/due/assignment SSOT | Đóng băng metadata nguồn; Linear giữ live issue/state/AC, repo giữ scope và technical checkpoint |
| 92 subtask gồm cả checkbox và việc độc lập | Chỉ đề xuất sub-issue cho đầu ra riêng; giữ đủ 92 ID trong mapping, phần nhỏ thành AC của parent |
| Owner agent ở kế hoạch cũ có thể bị hiểu là assignee | Giữ dưới nhãn snapshot; mọi assignment thật vẫn chưa đặt, phải xác minh user ID và quyền được giao |
| Dates nguồn chưa có capacity mới | Giữ provenance, không thêm ngày hay tự áp due/cycle/estimate trong Linear |
| Evidence hiện chỉ có đường dẫn máy và tài liệu chưa push | Chốt chỗ chia sẻ để Hòa truy cập; không tạo link GitHub cho file chưa tồn tại remote, không tự upload DOCX cá nhân |

## Quyết định đã xác nhận trong lượt này

- Workspace đích: `zero-door`; URL cung cấp là danh sách project, không phải project ID.
- Chỉ tạo sub-issue có đầu ra/nghiệm thu độc lập; các bước nhỏ giữ checklist AC.
- Issue sửa mã cần **review + kiểm chứng + merge + Hoàng chấp nhận** để Done.
- Trước hết thích nghi Markdown; không mở rộng sang feature, workflow mutation, assignment, commit/push/deploy, chi phí hoặc gửi Slack.

## Còn OPEN trước apply / Ready

1. Cập nhật sau restart: workspace/team/members và statuses đã xác minh qua linear_zero_door (xem CONNECTION.md); project list rỗng. Trước apply vẫn cần xác minh labels/templates, review tạo project/import và duplicate lại khi có đích cụ thể.
2. Duyệt mapping đối tượng cụ thể và duplicate/reuse; phân công và quyền cập nhật status chỉ áp trong phạm vi được giao, không suy từ việc Hòa tham gia workspace.
3. Chọn nơi evidence dùng chung và cách công bố docs chưa push; đường dẫn `R:` không chứng minh Hòa xem được.
4. Xác nhận việc đưa các ngày nguồn vào metadata sau kiểm capacity. Không bịa dates/estimate hoặc mặc định thời gian phản biện.

Các mục này không cản soạn contract hoặc kiểm nguồn; chúng cản tự tuyên bố đã setup Linear, đã gán người hoặc issue đã Ready khi thiếu điều kiện.

<!-- END SOURCE: docs/recovery/linear/DISCOVERY.md -->


<!-- SOURCE: docs/recovery/linear/IMPORT_PLAN.md -->

## Nguồn `docs/recovery/linear/IMPORT_PLAN.md`

# Kế hoạch milestone / issue / sub-issue

**DRAFT — chưa apply.** Giữ sequence R0–R7, không thêm M1–M8 cạnh tranh. Các gate đã có outcome/exit criteria, được dùng làm nền cho milestone.

## Cấu trúc cụ thể để review

| Cấp | Đối tượng đề xuất | Quy tắc |
| --- | --- | --- |
| 8 phase R0–R7 | 8 milestone | Outcome, included issues, exit criteria, actual dependencies và evidence/gaps |
| 27 task | 27 issue | Outcome tích hợp và acceptance riêng; parent không tự Done vì các con Done |
| Đầu ra độc lập | 34 sub-issue thông thường | Có thể giao và review riêng, không phải mỗi checkbox một ticket |
| Việc có điều kiện | 3 sub-issue dự phòng | B3 khi giữ claim RQ2; hai vòng phản biện chỉ khi nhận yêu cầu thật |
| 53 subtask còn lại | AC/checklist trong parent | Giữ ID nguồn và toàn bộ tiêu chí, không tạo ticket để tăng progress |

37 sub-issue candidates phủ 39 subtask nguồn: R3-T02-S01+S02 gộp thành một outcome block IP; S03+S04 gộp thành một outcome rollback. 39 + 53 = đủ 92 subtask. Tối đa 64 issue/sub-issue candidates; ba conditional không tự tạo trước khi điều kiện phát sinh. Đây là đề xuất, chưa là backlog đã đăng.

[mapping.json](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/mapping.json) liệt kê từng milestone, parent, sub-issue, nguồn và coverage. Chỉ giữ alias/remote ID sau apply; không chứa bản sao live status/assignee/due. Bản đầy đủ để xem scope nằm trong các file task hiện có, không tạo thêm 27 bản issue Markdown trùng nội dung.

## Workflow và dependencies

- Zero Door workflow mapping hiện **OPEN**; chưa dùng các ID/status của EurusDevSec. Khi có đúng team, map nghĩa Backlog/Ready/In Progress/In Review/Done/Canceled/Duplicate vào trạng thái đang tồn tại, không đổi workflow.
- `Todo` không tự chứng minh Ready. Dùng quy ước blocked/external của team nếu có; nếu chưa có thì đề xuất, không tự tạo status/label.
- Dependencies trong task là nguồn candidate, cần xem lại ở mức contract/evidence. Không tạo blocked-by chỉ vì cùng owner, thứ tự milestone hoặc chờ người làm.
- Contract draft R1 có thể chuẩn bị sớm; phần sửa consumer chờ contract khóa. B3 và phản biện có điều kiện, không biến thành dependency vô điều kiện làm nghẽn toàn project.
- S01 phạm vi đã ghi nhận trước đây không tự import Done/backdate. Ghi ngày tạo thực tế, provenance cũ và evidence/acceptance còn lại riêng.
- Assignee/priority/estimate/cycle/due mới chưa đặt; thông tin cũ trong repo là snapshot, không là quyền gán người hay metadata đã được duyệt.

## Thứ tự apply khi đúng đích và đủ quyền

1. Xác minh workspace/project/team/member; đọc milestones/issues/bodies/relations liên quan để tránh trùng. Không tạo project mới chỉ vì search ở connection khác không thấy.
2. Review object mapping, body/AC và metadata. Match bằng project + outcome + scope; reusable IDs phải đến từ read-back thực tế.
3. Reuse/tạo milestone, rồi parent và sub-issue cần thiết; gắn theo returned IDs. Conditional chưa phát sinh thì skip. Không tạo initiative hoặc native template mặc định.
4. Gắn dependencies thật, kiểm DAG và cả hai chiều relations. Không xóa valid objects để giả rollback; partial failure lưu successful IDs + lỗi rồi đọc lại trước retry.
5. Đọc lại mọi object/metadata/gate, lưu Linear URL/ID vào mapping/checkpoint. Report Created / Reused / Updated / Failed / Skipped và next issue thật sự Ready.

Chưa có mutation nào được thực hiện. Đăng issue không đồng nghĩa được phép commit/push/merge/deploy hoặc gửi Slack. Khi connector đúng đích sẵn sàng, đối chiếu phạm vi yêu cầu hiện hành trước apply; không hỏi lại những quyền đã được xác nhận rõ.

<!-- END SOURCE: docs/recovery/linear/IMPORT_PLAN.md -->


<!-- SOURCE: docs/recovery/linear/INVENTORY_ISSUE.md -->

## Nguồn `docs/recovery/linear/INVENTORY_ISSUE.md`

# Issue đã điền để review — Inventory lab có provenance

**DRAFT, chưa tạo trên Linear; chưa đánh dấu Ready.** Mã nguồn R0-T02-S01; parent candidate R0-T02, milestone R0. Đích project và evidence sharing chưa xác minh; không áp assignment/date/status thật.

## Outcome

Có inventory môi trường local và lỗi cản truy cập, đủ để đề xuất bước phục hồi dựa trên bằng chứng mà không thay đổi cluster hoặc dữ liệu.

## Scope / workflow / contracts

Includes: Git HEAD/dirty, Docker context/containers/volumes/ports/resources, Kubernetes context/API metadata; phiên bản/args K3s nếu truy cập được. Excludes: start/recreate/delete, thay context hiện hành, build/deploy, attack/heal, LLM, secret hoặc chi phí.

Đọc metadata → ghi command/time/result hoặc lỗi → phân loại observed/inference/unknown → report có provenance. Nguồn scope: SCOPE.md, checkpoint R0-T02 và runbook legacy. CLI có timeout hữu hạn; chỉ dừng tiến trình do phiên này tạo, không kill mọi kubectl. Connection refused không đồng nghĩa không có cluster.

## Acceptance criteria

- [ ] AC-01: Report ghi branch, HEAD, dirty snapshot, timestamp/timezone và từng command thực tế; không gán commit chưa tồn tại.
- [ ] AC-02: Docker context/inventory có output rút gọn; lỗi/exit/timeout và phần chưa xác minh được giữ riêng, không trình bày query lỗi như inventory rỗng thành công.
- [ ] AC-03: K8s context, kết nối API, version/args đọc được được ghi riêng. Không đọc được thì ghi lỗi/UNKNOWN và ảnh hưởng; không suy NetworkPolicy bị bỏ qua chỉ từ Flannel.
- [ ] AC-04: Phiên chỉ đọc, không đổi workload/context, mở secret hoặc chạy script có tác dụng phụ; không POST attack/heal hay gọi LLM để health check.
- [ ] AC-05: Kết luận phân biệt quan sát/giả thuyết và bước cần quyết định. Report có thể đạt dù lab chưa truy cập được; parent khôi phục lab chưa tự hoàn tất.
- [ ] AC-06: Reviewer truy cập được artifact ở vị trí chia sẻ đã duyệt; report có AC/case mapping, limits và review result.

## Dependencies

Blocked by: quyền đọc local thật nếu công cụ chặn; xác minh metadata target và cách chia sẻ trước Ready delivery. Không cần backend LLM/G0 toàn phần để chuẩn bị inventory. Blocks: lựa chọn restore/recreate có căn cứ. Related: baseline/source ledger và draft contract, không mặc định chúng chặn nhau.

## Verification plan

Chạy lệnh metadata chỉ đọc, bounded theo task/runbook và công cụ đang có; report ghi exact commands thực tế. Không tạo fault để kiểm việc ghi lỗi và không thêm test chỉ mirror Markdown. Automated build/remote CI/merge: N/A nếu issue thực sự chỉ giao report và không sửa mã. Điều kiện API/CLI thất bại phải được ghi trung thực, không được thay bằng dữ liệu giả.

## Evidence

Candidate/execution/AC mapping/review: **Pending**, chưa chạy inventory. File output dự kiến `docs/evidence/R0-T02-S01/inventory.md`, chưa tạo. Shared artifact URL chưa chốt; local path không chứng minh Hòa đã xem. Không pre-check AC từ hydration cũ.

## Metadata dự kiến — chưa áp

Project/team chưa xác minh ở workspace zero-door. Parent/milestone resolve bằng ID thật sau duplicate check. Assignee unassigned; priority/estimate/cycle/due chưa đặt. Lịch nguồn chỉ là provenance, không tự là due metadata. Done authority theo QA_AND_DONE; report-only không sửa mã không tự chịu yêu cầu merge dành cho issue sửa mã.

<!-- END SOURCE: docs/recovery/linear/INVENTORY_ISSUE.md -->


<!-- SOURCE: docs/recovery/linear/ISSUE_TEMPLATE.md -->

## Nguồn `docs/recovery/linear/ISSUE_TEMPLATE.md`

# Mẫu issue cho ZERO DOOR

Thích nghi canonical kit v1.0; thay mọi placeholder trước Ready. Giữ ngắn theo outcome; không sao chép ví dụ UI/backlog S-cool.

## Outcome

Actor/result/context và dấu hiệu quan sát được để nghiệm thu đầu ra.

## Scope / workflow / contracts

Includes, excludes; flow từ đầu vào tới kết quả; nguồn scope/design/setup; schema/API/data consumers và compatibility; invariant, validation và shared boundaries. Quyết định ghi CONFIRMED/PROPOSED/OPEN. Tên người/agent không đặt trong technical body để thay cho metadata phân công.

## Acceptance criteria

- [ ] AC-01: Given bối cảnh/đầu vào cụ thể, when hành động được phép, then kết quả quan sát và artifact kiểm tra được.
- [ ] AC-02: Given input/target/state không hợp lệ, hệ thống từ chối và giữ invariant được chỉ rõ.
- [ ] AC-03: Given failure/timeout/retry/missing/cleanup error, ghi trạng thái trung thực, không tạo recovery/KPI giả.
- [ ] AC-04: Review/handoff và checks cần thiết khớp candidate cuối; consumer bị ảnh hưởng được kiểm tra.

Điều chỉnh số AC theo outcome; không giữ ví dụ không liên quan chỉ để đủ bốn mục. Không pre-check từ hydration, code inspection hoặc trạng thái snapshot.

## Dependencies / failure cases

Blocked by: prerequisite contract/evidence hoặc None. Blocks: consumer/điểm bàn giao thật. Related: phối hợp không chặn. Liệt kê authorization/privacy/input, retry/cleanup, provider/cost và research integrity phù hợp; không bịa tenant hoặc browser matrix.

## Verification / evidence

Automated/manual/integration phù hợp rủi ro; environment/synthetic data, success/negative/failure cases và retest consumers. Exact commands chỉ khi biết từ repo. Ghi revision/dirty diff, time/timezone, môi trường, AC → case → result → shared artifact; Pending/Pass/Fail/Blocked/Not verified/N/A có lý do. Review/CI/merge và remaining gaps tách riêng.

## Metadata — nhập bằng field Linear

Project/team/milestone/parent theo ID thật. Assignee/priority/estimate/due/cycle chỉ theo quyền và quyết định tương ứng. Mã R*-T*-S* là alias provenance; Linear ID là định danh delivery chuẩn. Không lặp tên/ngày/status trong technical body như một bản metadata khác.

Ready khi contract/AC/prerequisite/metadata/verification đủ rõ và thực thi được trong quyền hiện có. Quyết định bắt buộc còn OPEN thì Backlog, hoặc chỉ mở phần chuẩn bị có boundary rõ. Done theo [QA và Done](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/QA_AND_DONE.md).

<!-- END SOURCE: docs/recovery/linear/ISSUE_TEMPLATE.md -->


<!-- SOURCE: docs/recovery/linear/QA_AND_DONE.md -->

## Nguồn `docs/recovery/linear/QA_AND_DONE.md`

# QA, Done và gate nghiên cứu

## Chính sách đã xác nhận

Issue sửa mã chỉ Done khi **review + kiểm chứng + merge + Hoàng chấp nhận**. Yêu cầu merge không tự cấp quyền commit/push/merge. Candidate/evidence phải gắn revision cuối; thay mã thì retest phần bị ảnh hưởng và consumer liên quan, giữ report cũ như lịch sử.

Issue tài liệu/nghiên cứu nghiệm thu theo output/AC và review/chấp nhận phù hợp; không bắt build/browser checks vô căn cứ. N/A có lý do. Quyền cập nhật status và assignment trên Linear vẫn theo phạm vi được giao.

## Kiểm chứng phù hợp ZERO DOOR

- Đường thật: attack effect → Gaia detect → transport → healer action → probe độc lập. Inject alert là test thành phần, không thay proof toàn pipeline.
- Tách API_ACCEPTED/ACTION_COMPLETED/RECOVERY_VERIFIED; FAILED/PARTIAL/timeout/missing không thành recovery hoặc uptime 100%.
- Ba vector, scale up/down/block IP/rollback, benign traffic, known-good release, cleanup/restart/HPA có evidence theo scope.
- Legacy/pilot/formal tách nhau; giữ failure, ground-truth boundary, model/prompt/config/version, usage/cost và đối chứng. Không bắt AI thắng để nghiệm thu báo cáo hợp lệ.
- Dashboard kiểm role/state/viewport/keyboard phù hợp thay đổi thực tế; không nhân sáu QA package hoặc ma trận đa tenant/browser không có trong scope.

## Báo cáo, defect và retest

Report: Case ID | AC | state/context | steps/data | expected | actual | result | artifact | defect | retest revision/result.

Report QA có thể Done dù case sản phẩm fail nếu report đạt AC của nó; product/milestone acceptance vẫn mở khi yêu cầu cốt lõi chưa đạt. Defect có candidate/env, tái hiện, expected/actual, impact, scope, AC và regression/retest. Dùng conventions của đúng team; fix commit chưa phải retest độc lập.

## Chia sẻ bằng chứng

Vị trí repo dự kiến `docs/evidence/<legacy-or-issue-id>/`; chưa tạo report mới. Cần chốt kênh bền để Hòa truy cập: đường dẫn `R:` chỉ là local. Tài liệu đang dirty chưa có blob/commit URL hợp lệ trên GitHub. Khi được phép công bố, dùng revision/PR/artifact URL hoặc attachment bền được duyệt; loại secret và dữ liệu cá nhân. Không tự upload DOCX cá nhân.

## Gate, paper và nghiệm thu

Milestone cần integrated acceptance riêng, không chỉ tổng số child Done. Yêu cầu gate/research trong repo là nguồn scope, Linear giữ verdict delivery và links evidence. G5 có thể ghi pilot KPI chưa đạt theo điều kiện nguồn nhưng không biến thành nghiên cứu hoàn tất. G7 cần đủ sản phẩm và chấp nhận đăng theo xác nhận hiện có. Nộp paper, được chấp nhận và báo cáo hội đồng là ba sự kiện riêng. Deploy/cloud luôn là hành động riêng.

<!-- END SOURCE: docs/recovery/linear/QA_AND_DONE.md -->


<!-- SOURCE: docs/recovery/linear/README.md -->

## Nguồn `docs/recovery/linear/README.md`

# Delivery tracking — Linear Zero Door

Đích Hoàng cung cấp: [workspace Zero Door](https://linear.app/zero-door/projects/all). MCP riêng `linear_zero_door` đã đọc được đúng workspace zero-door/team Zero-Door (ZER), cả Hoàng và Hòa thuộc team. Danh sách project hiện rỗng; chưa có project ID/backlog để nhập. Connector EurusDevSec/S-cool giữ nguyên. Xem [checkpoint kết nối](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/CONNECTION.md). **Chưa tạo hoặc sửa đối tượng Linear/Slack.**

## Nguồn chuẩn

| Nội dung | Nguồn chuẩn |
| --- | --- |
| Outcome/AC, status, assignee, priority, estimate, dates, relations và milestone delivery | Linear Zero Door; workspace/team đã xác minh, project/backlog chưa được thiết lập |
| Scope và cam kết nghiên cứu | [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/SCOPE.md), DOCX và xác nhận đã dẫn nguồn |
| Code, revision, PR, review, CI, merge | Git / repository host |
| File plan, technical checkpoint, evidence và next action của phiên | File task hiện có và vị trí evidence được duyệt |
| Slack | Phối hợp khi được yêu cầu; không là board trạng thái thứ hai |

Metadata trong các file task đã được đóng băng thành snapshot để chuyển đổi. Không tiếp tục cập nhật chúng như live board, cũng không coi snapshot hoặc connector EurusDevSec là trạng thái Zero Door đã xác minh.

## Mở tài liệu nào

- [Discovery và các quyết định](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/DISCOVERY.md).
- [Cấu trúc và kế hoạch import](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/IMPORT_PLAN.md).
- [Mapping giữ đủ 92 ID nguồn](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/mapping.json).
- [Mẫu issue](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/ISSUE_TEMPLATE.md).
- [Issue inventory đã điền để review](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/INVENTORY_ISSUE.md).
- [QA và chính sách Done](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/QA_AND_DONE.md).

Canonical kit v1.0: [00_CANONICAL_ENTRYPOINT.md](R:/_Dev_tools/obsidian/oBsidianFolder/Eurus_Vault/99_System/01_Templates/Linear_Project_Kit/00_CANONICAL_ENTRYPOINT.md). Đã đọc theo đúng thứ tự yêu cầu; không sửa master, không áp stack/workflow hoặc số milestone của S-cool.

<!-- END SOURCE: docs/recovery/linear/README.md -->


<!-- SOURCE: docs/recovery/linear/mapping.json -->

## Nguồn `docs/recovery/linear/mapping.json`

{
  "schemaVersion": 1,
  "mode": "PROPOSAL_NOT_APPLIED",
  "sourceDate": "2026-10-17",
  "targetWorkspaceUrl": "https://linear.app/zero-door/projects/all",
  "targetProjectId": null,
  "targetTeamId": "865d41a7-ef26-474c-a9f8-36e781569fc8",
  "liveState": "WORKSPACE_VERIFIED_NO_ACCESSIBLE_PROJECT",
  "assignees": "UNASSIGNED_UNTIL_EXPLICITLY_APPROVED",
  "dates": "SOURCE_SCHEDULE_SNAPSHOT_NOT_PUBLISHED_METADATA",
  "milestones": [
    {
      "legacyId": "R0",
      "title": "Nền tảng và phạm vi",
      "source": "docs/recovery/phases/R0-foundations/README.md",
      "linearId": null,
      "gate": "**Gate G0:** Lab có giao dịch kiểm chứng được, một backend LLM trả kết quả thật; phạm vi, RQ, đối chứng và ranh giới nhãn/evidence được khóa."
    },
    {
      "legacyId": "R1",
      "title": "Sự kiện và phép đo",
      "source": "docs/recovery/phases/R1-measurement/README.md",
      "linearId": null,
      "gate": "**Gate G1:** Một sự cố có ID xuyên suốt, metric hồi phục/quyết định tái tính được; evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động."
    },
    {
      "legacyId": "R2",
      "title": "Ba kịch bản Chaos",
      "source": "docs/recovery/phases/R2-chaos-scenarios/README.md",
      "linearId": null,
      "gate": "**Gate G2:** SQLi, DDoS L7 và resource exhaustion gây được tác động đúng mục tiêu, có dấu vết và cleanup; chạy phối hợp vẫn giữ giới hạn."
    },
    {
      "legacyId": "R3",
      "title": "Phục hồi và block IP",
      "source": "docs/recovery/phases/R3-recovery/README.md",
      "linearId": null,
      "gate": "**Gate G3:** Scale up/down, block IP và rollback có tác động thật; phân biệt API chấp nhận với hồi phục; có kiểm tra restart, HPA và trạng thái thất bại."
    },
    {
      "legacyId": "R4",
      "title": "Tác tử và LLM",
      "source": "docs/recovery/phases/R4-ai-agents/README.md",
      "linearId": null,
      "gate": "**Gate G4:** Ba agent có trace thật, guard/fallback hoạt động; pilot B0/B1/B2 hợp lệ và quyết định B3 có bằng chứng hoặc giới hạn claim; không yêu cầu AI thắng."
    },
    {
      "legacyId": "R5",
      "title": "Tích hợp và pilot",
      "source": "docs/recovery/phases/R5-integration/README.md",
      "linearId": null,
      "gate": "**Gate G5:** Core/phép đo qua kiểm chứng; có dataset pilot/runbook và protocol đối chứng đã khóa. KPI chưa đạt phải giữ kết quả và mở task sửa; chưa coi nghiên cứu hoàn tất."
    },
    {
      "legacyId": "R6",
      "title": "Thực nghiệm và bài báo",
      "source": "docs/recovery/phases/R6-paper/README.md",
      "linearId": null,
      "gate": "**Gate G6:** Có dataset đủ protocol, paper trả lời RQ và claim khớp đối chứng đã đo, cùng biên nhận nộp đúng nơi. Biên nhận chưa phải chấp nhận đăng."
    },
    {
      "legacyId": "R7",
      "title": "Phản biện và nghiệm thu",
      "source": "docs/recovery/phases/R7-acceptance/README.md",
      "linearId": null,
      "gate": "**Gate G7:** Có bằng chứng chấp nhận đăng, đủ sản phẩm cam kết và hồ sơ/kết quả nghiệm thu theo lịch trường trước 31/12; các mốc bên ngoài cần xác nhận."
    }
  ],
  "issues": [
    {
      "legacyId": "R0-T01",
      "title": "Khóa phạm vi và tiêu chí đánh giá",
      "source": "docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md",
      "milestoneLegacyId": "R0",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R0-T01-S02",
          "sourceSubtasks": [
            "R0-T01-S02"
          ],
          "title": "Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R0-T01-S03",
          "sourceSubtasks": [
            "R0-T01-S03"
          ],
          "title": "Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R0-T01-S01",
          "title": "Ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI và bài được chấp nhận đăng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T01"
        },
        {
          "sourceId": "R0-T01-S02",
          "title": "Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số.",
          "representation": "subissue",
          "targetLegacyKey": "R0-T01-S02"
        },
        {
          "sourceId": "R0-T01-S03",
          "title": "Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08.",
          "representation": "subissue",
          "targetLegacyKey": "R0-T01-S03"
        }
      ],
      "dependencyCandidates": []
    },
    {
      "legacyId": "R0-T02",
      "title": "Khôi phục môi trường local",
      "source": "docs/recovery/phases/R0-foundations/R0-T02-local-lab.md",
      "milestoneLegacyId": "R0",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R0-T02-S01",
          "sourceSubtasks": [
            "R0-T02-S01"
          ],
          "title": "Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R0-T02-S02",
          "sourceSubtasks": [
            "R0-T02-S02"
          ],
          "title": "Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R0-T02-S01",
          "title": "Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới.",
          "representation": "subissue",
          "targetLegacyKey": "R0-T02-S01"
        },
        {
          "sourceId": "R0-T02-S02",
          "title": "Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại.",
          "representation": "subissue",
          "targetLegacyKey": "R0-T02-S02"
        },
        {
          "sourceId": "R0-T02-S03",
          "title": "Kiểm tra Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T02"
        }
      ],
      "dependencyCandidates": []
    },
    {
      "legacyId": "R0-T03",
      "title": "Xác nhận một backend LLM thật",
      "source": "docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md",
      "milestoneLegacyId": "R0",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R0-T03-S01",
          "sourceSubtasks": [
            "R0-T03-S01"
          ],
          "title": "Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R0-T03-S01",
          "title": "Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy.",
          "representation": "subissue",
          "targetLegacyKey": "R0-T03-S01"
        },
        {
          "sourceId": "R0-T03-S02",
          "title": "Gọi LLM bằng đầu vào nghiên cứu và kiểm tra đầu ra theo schema.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T03"
        },
        {
          "sourceId": "R0-T03-S03",
          "title": "Thử timeout, retry có giới hạn và fallback; ghi rõ khi dùng RULES thay AI.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T01",
          "targetLegacyKey": "R0-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R0-T04",
      "title": "Khóa câu hỏi nghiên cứu và thiết kế đối chứng",
      "source": "docs/recovery/phases/R0-foundations/R0-T04-research-questions.md",
      "milestoneLegacyId": "R0",
      "linearId": null,
      "subissues": [],
      "sourceCoverage": [
        {
          "sourceId": "R0-T04-S01",
          "title": "Chốt RQ1–RQ3, đóng góp dự kiến và giới hạn claim.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T04"
        },
        {
          "sourceId": "R0-T04-S02",
          "title": "Khóa B0/B1/B2, giữ BM; quyết định phạm vi B3 và budget.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T04"
        },
        {
          "sourceId": "R0-T04-S03",
          "title": "Chốt ground truth, tập action đúng và ranh giới dữ liệu không lộ đáp án.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R0-T04"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T01",
          "targetLegacyKey": "R0-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R1-T01",
      "title": "Thống nhất hợp đồng sự kiện và lưu dấu vết",
      "source": "docs/recovery/phases/R1-measurement/R1-T01-event-contract.md",
      "milestoneLegacyId": "R1",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R1-T01-S01",
          "sourceSubtasks": [
            "R1-T01-S01"
          ],
          "title": "Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R1-T01-S01",
          "title": "Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi.",
          "representation": "subissue",
          "targetLegacyKey": "R1-T01-S01"
        },
        {
          "sourceId": "R1-T01-S02",
          "title": "Truyền ID qua Kafka/HTTP và lưu sự kiện gốc phục vụ tái tính.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T01"
        },
        {
          "sourceId": "R1-T01-S03",
          "title": "Tách ground truth/log điều khiển khỏi evidence dành cho bên chữa lỗi.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T01",
          "targetLegacyKey": "R0-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R0-T04-S03",
          "targetLegacyKey": "R0-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R1-T02",
      "title": "Đo sức khỏe và thời gian độc lập",
      "source": "docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md",
      "milestoneLegacyId": "R1",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R1-T02-S01",
          "sourceSubtasks": [
            "R1-T02-S01"
          ],
          "title": "Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R1-T02-S01",
          "title": "Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture.",
          "representation": "subissue",
          "targetLegacyKey": "R1-T02-S01"
        },
        {
          "sourceId": "R1-T02-S02",
          "title": "Tính MTTD/MTTR từ mốc sự kiện và xác nhận hồi phục bằng probe.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T02"
        },
        {
          "sourceId": "R1-T02-S03",
          "title": "Xử lý thiếu dữ liệu, timeout, FAILED/PARTIAL và FPR có mẫu số rõ ràng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T02"
        },
        {
          "sourceId": "R1-T02-S04",
          "title": "Bổ sung metric quyết định, phục hồi theo lượt và usage/cost theo run.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T02"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R1-T01",
          "targetLegacyKey": "R1-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R0-T02",
          "targetLegacyKey": "R0-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R1-T03",
      "title": "Sửa dashboard và các chế độ đối chứng",
      "source": "docs/recovery/phases/R1-measurement/R1-T03-dashboard-and-baselines.md",
      "milestoneLegacyId": "R1",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R1-T03-S04",
          "sourceSubtasks": [
            "R1-T03-S04"
          ],
          "title": "Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R1-T03-S01",
          "title": "Bỏ số ngẫu nhiên và nội dung mô phỏng khỏi phần được trình bày là kết quả thực.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T03"
        },
        {
          "sourceId": "R1-T03-S02",
          "title": "Cho dashboard và bộ xuất dữ liệu dùng chung phép đo.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T03"
        },
        {
          "sourceId": "R1-T03-S03",
          "title": "Tách MANUAL, RULES và AI; MANUAL không tự kích hoạt healer.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T03"
        },
        {
          "sourceId": "R1-T03-S04",
          "title": "Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi.",
          "representation": "subissue",
          "targetLegacyKey": "R1-T03-S04"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R1-T02",
          "targetLegacyKey": "R1-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R1-T04",
      "title": "Giới hạn tác động, kiểm soát lệnh và CI",
      "source": "docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md",
      "milestoneLegacyId": "R1",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R1-T04-S03",
          "sourceSubtasks": [
            "R1-T04-S03"
          ],
          "title": "Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R1-T04-S01",
          "title": "Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T04"
        },
        {
          "sourceId": "R1-T04-S02",
          "title": "Kiểm soát truy cập lệnh, sự kiện trùng và payload sai.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R1-T04"
        },
        {
          "sourceId": "R1-T04-S03",
          "title": "Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI.",
          "representation": "subissue",
          "targetLegacyKey": "R1-T04-S03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T01",
          "targetLegacyKey": "R0-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R2-T01",
      "title": "Fixture và executor SQL injection",
      "source": "docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md",
      "milestoneLegacyId": "R2",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R2-T01-S02",
          "sourceSubtasks": [
            "R2-T01-S02"
          ],
          "title": "Triển khai fixture/database nhẹ và đường ingress quan sát được.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R2-T01-S03",
          "sourceSubtasks": [
            "R2-T01-S03"
          ],
          "title": "Bổ sung executor SQLi bằng template và giới hạn đã chốt.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R2-T01-S01",
          "title": "Chốt fixture nghiệp vụ giả lập, dữ liệu giả, route vulnerable/safe và nguồn IP.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R2-T01"
        },
        {
          "sourceId": "R2-T01-S02",
          "title": "Triển khai fixture/database nhẹ và đường ingress quan sát được.",
          "representation": "subissue",
          "targetLegacyKey": "R2-T01-S02"
        },
        {
          "sourceId": "R2-T01-S03",
          "title": "Bổ sung executor SQLi bằng template và giới hạn đã chốt.",
          "representation": "subissue",
          "targetLegacyKey": "R2-T01-S03"
        },
        {
          "sourceId": "R2-T01-S04",
          "title": "Chứng minh tác động SQLi, log và phân biệt lưu lượng tấn công với benign.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R2-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T02",
          "targetLegacyKey": "R0-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R1-T01",
          "targetLegacyKey": "R1-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R1-T04-S01",
          "targetLegacyKey": "R1-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R2-T02",
      "title": "DDoS L7 và cạn tài nguyên đúng mục tiêu",
      "source": "docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md",
      "milestoneLegacyId": "R2",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R2-T02-S01",
          "sourceSubtasks": [
            "R2-T02-S01"
          ],
          "title": "Cho HTTP flood đi qua route/cổng được giám sát, có RPS và thời lượng giới hạn.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R2-T02-S02",
          "sourceSubtasks": [
            "R2-T02-S02"
          ],
          "title": "Tạo CPU exhaustion trên workload mục tiêu, giới hạn tài nguyên rõ ràng.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R2-T02-S04",
          "sourceSubtasks": [
            "R2-T02-S04"
          ],
          "title": "Chuẩn bị tải C0/C1 cùng biến thể C2/C4 có triệu chứng chồng lấp.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R2-T02-S01",
          "title": "Cho HTTP flood đi qua route/cổng được giám sát, có RPS và thời lượng giới hạn.",
          "representation": "subissue",
          "targetLegacyKey": "R2-T02-S01"
        },
        {
          "sourceId": "R2-T02-S02",
          "title": "Tạo CPU exhaustion trên workload mục tiêu, giới hạn tài nguyên rõ ràng.",
          "representation": "subissue",
          "targetLegacyKey": "R2-T02-S02"
        },
        {
          "sourceId": "R2-T02-S03",
          "title": "Kiểm tra cleanup, traffic bình thường và memory variant nếu đưa vào protocol.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R2-T02"
        },
        {
          "sourceId": "R2-T02-S04",
          "title": "Chuẩn bị tải C0/C1 cùng biến thể C2/C4 có triệu chứng chồng lấp.",
          "representation": "subissue",
          "targetLegacyKey": "R2-T02-S04"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T02",
          "targetLegacyKey": "R0-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R1-T01",
          "targetLegacyKey": "R1-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R1-T04-S01",
          "targetLegacyKey": "R1-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R0-T04",
          "targetLegacyKey": "R0-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R2-T03",
      "title": "Chạy phối hợp và dừng có kiểm soát",
      "source": "docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md",
      "milestoneLegacyId": "R2",
      "linearId": null,
      "subissues": [],
      "sourceCoverage": [
        {
          "sourceId": "R2-T03-S01",
          "title": "Điều phối ba executor đồng thời theo budget chung.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R2-T03"
        },
        {
          "sourceId": "R2-T03-S02",
          "title": "Thử start, stop, cancel và cleanup khi một executor lỗi.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R2-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R2-T01",
          "targetLegacyKey": "R2-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R2-T02",
          "targetLegacyKey": "R2-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R1-T04",
          "targetLegacyKey": "R1-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R3-T01",
      "title": "Trạng thái hồi phục và scale",
      "source": "docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md",
      "milestoneLegacyId": "R3",
      "linearId": null,
      "subissues": [],
      "sourceCoverage": [
        {
          "sourceId": "R3-T01-S01",
          "title": "Tách API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T01"
        },
        {
          "sourceId": "R3-T01-S02",
          "title": "Kiểm chứng scale up tăng capacity và sức khỏe dịch vụ.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T01"
        },
        {
          "sourceId": "R3-T01-S03",
          "title": "Kiểm chứng scale down có hysteresis và quyền điều khiển rõ với HPA.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R1-T02",
          "targetLegacyKey": "R1-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R3-T02",
      "title": "Block IP thực thi được và rollback đúng phiên bản",
      "source": "docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md",
      "milestoneLegacyId": "R3",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R3-T02-S02",
          "sourceSubtasks": [
            "R3-T02-S01",
            "R3-T02-S02"
          ],
          "title": "Block IP có nguồn tin cậy, TTL và benign verification",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R3-T02-S04",
          "sourceSubtasks": [
            "R3-T02-S03",
            "R3-T02-S04"
          ],
          "title": "Rollback từ bản lỗi về known-good có probe",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R3-T02-S01",
          "title": "Chốt enforcement point và nguồn IP; xử lý NAT/header tin cậy.",
          "representation": "subissue",
          "targetLegacyKey": "R3-T02-S02"
        },
        {
          "sourceId": "R3-T02-S02",
          "title": "Chặn attacker, giữ traffic benign, có TTL và gỡ chặn.",
          "representation": "subissue",
          "targetLegacyKey": "R3-T02-S02"
        },
        {
          "sourceId": "R3-T02-S03",
          "title": "Tạo phiên bản lỗi/known-good và case C3 có kiểm soát, tách nhãn đáp án khỏi telemetry.",
          "representation": "subissue",
          "targetLegacyKey": "R3-T02-S04"
        },
        {
          "sourceId": "R3-T02-S04",
          "title": "Khôi phục image/config/revision thật và xác minh rollout lẫn probe.",
          "representation": "subissue",
          "targetLegacyKey": "R3-T02-S04"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R1-T02",
          "targetLegacyKey": "R1-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R2-T01",
          "targetLegacyKey": "R2-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R3-T03",
      "title": "Consumer, retry và tương tác controller",
      "source": "docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md",
      "milestoneLegacyId": "R3",
      "linearId": null,
      "subissues": [],
      "sourceCoverage": [
        {
          "sourceId": "R3-T03-S01",
          "title": "Sửa blocking consumer, ack, dedup, cooldown và retry có giới hạn.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T03"
        },
        {
          "sourceId": "R3-T03-S02",
          "title": "Thử restart, nhiều replica, PodKill và tương tác HPA.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T03"
        },
        {
          "sourceId": "R3-T03-S03",
          "title": "Thử worker/healer restart và mất telemetry.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R3-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R1-T04",
          "targetLegacyKey": "R1-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R3-T01",
          "targetLegacyKey": "R3-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R4-T01",
      "title": "LLM adapter chung và Nemesis",
      "source": "docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md",
      "milestoneLegacyId": "R4",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R4-T01-S01",
          "sourceSubtasks": [
            "R4-T01-S01"
          ],
          "title": "Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R4-T01-S01",
          "title": "Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout.",
          "representation": "subissue",
          "targetLegacyKey": "R4-T01-S01"
        },
        {
          "sourceId": "R4-T01-S02",
          "title": "Nối observation → kế hoạch Nemesis → executor → kết quả.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T01"
        },
        {
          "sourceId": "R4-T01-S03",
          "title": "Thêm start/stop, max rounds/calls và điều kiện dừng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T03",
          "targetLegacyKey": "R0-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R2-T01",
          "targetLegacyKey": "R2-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R2-T03",
          "targetLegacyKey": "R2-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R4-T02",
      "title": "Gaia và Hephaestus có quyết định LLM được giới hạn",
      "source": "docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md",
      "milestoneLegacyId": "R4",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R4-T02-S01",
          "sourceSubtasks": [
            "R4-T02-S01"
          ],
          "title": "Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R4-T02-S02",
          "sourceSubtasks": [
            "R4-T02-S02"
          ],
          "title": "Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R4-T02-S01",
          "title": "Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM.",
          "representation": "subissue",
          "targetLegacyKey": "R4-T02-S01"
        },
        {
          "sourceId": "R4-T02-S02",
          "title": "Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục.",
          "representation": "subissue",
          "targetLegacyKey": "R4-T02-S02"
        },
        {
          "sourceId": "R4-T02-S03",
          "title": "Thử JSON sai, timeout, 429 và thiếu bằng chứng; fallback được đánh dấu.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T02"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R4-T01-S01",
          "targetLegacyKey": "R4-T01-S01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R3-T02",
          "targetLegacyKey": "R3-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R3-T03",
          "targetLegacyKey": "R3-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R4-T03",
      "title": "Chứng minh vòng multi-agent và đối chứng RULES",
      "source": "docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md",
      "milestoneLegacyId": "R4",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R4-T03-S02",
          "sourceSubtasks": [
            "R4-T03-S02"
          ],
          "title": "Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R4-T03-S01",
          "title": "Chạy một vòng có trace observation–decision–result cho cả ba agent.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T03"
        },
        {
          "sourceId": "R4-T03-S02",
          "title": "Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage.",
          "representation": "subissue",
          "targetLegacyKey": "R4-T03-S02"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R4-T01",
          "targetLegacyKey": "R4-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R4-T02",
          "targetLegacyKey": "R4-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R3-T03",
          "targetLegacyKey": "R3-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R0-T04",
          "targetLegacyKey": "R0-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R4-T04",
      "title": "Đối chứng single-agent cho claim chia vai trò",
      "source": "docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md",
      "milestoneLegacyId": "R4",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R4-T04-S03",
          "sourceSubtasks": [
            "R4-T04-S03"
          ],
          "title": "Nếu giữ RQ2, pilot B2/B3 sau khi R4-T02-S02 hoàn tất, trên cùng case và kiểm tra dữ liệu.",
          "condition": "only_if_RQ2_claim_retained",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R4-T04-S01",
          "title": "Xác nhận giữ RQ2 hay giới hạn claim theo budget pilot.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T04"
        },
        {
          "sourceId": "R4-T04-S02",
          "title": "Nếu giữ RQ2, cấu hình SINGLE_LLM gộp phân tích và chọn action.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R4-T04"
        },
        {
          "sourceId": "R4-T04-S03",
          "title": "Nếu giữ RQ2, pilot B2/B3 sau khi R4-T02-S02 hoàn tất, trên cùng case và kiểm tra dữ liệu.",
          "representation": "subissue",
          "targetLegacyKey": "R4-T04-S03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T04",
          "targetLegacyKey": "R0-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R4-T01-S01",
          "targetLegacyKey": "R4-T01-S01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R3-T03",
          "targetLegacyKey": "R3-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R5-T01",
      "title": "Chạy đầy đủ đường tấn công–phát hiện–hồi phục",
      "source": "docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md",
      "milestoneLegacyId": "R5",
      "linearId": null,
      "subissues": [],
      "sourceCoverage": [
        {
          "sourceId": "R5-T01-S01",
          "title": "Chụp phiên bản image/config/model/prompt và workload của đợt tích hợp.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T01"
        },
        {
          "sourceId": "R5-T01-S02",
          "title": "Chạy từng vector qua toàn pipeline và đo bằng probe độc lập.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T01"
        },
        {
          "sourceId": "R5-T01-S03",
          "title": "Thử bad release, benign traffic, thất bại và cleanup.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R4-T03",
          "targetLegacyKey": "R4-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R4-T04",
          "targetLegacyKey": "R4-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R5-T02",
      "title": "Pilot, khóa protocol và War Game",
      "source": "docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md",
      "milestoneLegacyId": "R5",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R5-T02-S01",
          "sourceSubtasks": [
            "R5-T02-S01"
          ],
          "title": "Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R5-T02-S02",
          "sourceSubtasks": [
            "R5-T02-S02"
          ],
          "title": "Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R5-T02-S03",
          "sourceSubtasks": [
            "R5-T02-S03"
          ],
          "title": "Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R5-T02-S01",
          "title": "Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo.",
          "representation": "subissue",
          "targetLegacyKey": "R5-T02-S01"
        },
        {
          "sourceId": "R5-T02-S02",
          "title": "Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI.",
          "representation": "subissue",
          "targetLegacyKey": "R5-T02-S02"
        },
        {
          "sourceId": "R5-T02-S03",
          "title": "Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt.",
          "representation": "subissue",
          "targetLegacyKey": "R5-T02-S03"
        },
        {
          "sourceId": "R5-T02-S04",
          "title": "Tái tính KPI; phân loại pass/fail, thiếu dữ liệu và nguyên nhân.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T02"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R5-T01",
          "targetLegacyKey": "R5-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R5-T03",
      "title": "Chốt kỹ thuật và bàn giao cho Hòa",
      "source": "docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md",
      "milestoneLegacyId": "R5",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R5-T03-S02",
          "sourceSubtasks": [
            "R5-T03-S02"
          ],
          "title": "Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R5-T03-S01",
          "title": "Sửa lỗi cốt lõi phát hiện trong pilot và chạy lại phép thử bị ảnh hưởng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T03"
        },
        {
          "sourceId": "R5-T03-S02",
          "title": "Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ.",
          "representation": "subissue",
          "targetLegacyKey": "R5-T03-S02"
        },
        {
          "sourceId": "R5-T03-S03",
          "title": "Bàn giao sơ đồ, protocol, câu hỏi/claim, bảng/plot và giới hạn kết quả cho Hòa.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R5-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R5-T02",
          "targetLegacyKey": "R5-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R6-T01",
      "title": "Chuẩn bị bài báo trong lúc hoàn thiện kỹ thuật",
      "source": "docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md",
      "milestoneLegacyId": "R6",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R6-T01-S02",
          "sourceSubtasks": [
            "R6-T01-S02"
          ],
          "title": "Đối chiếu tài liệu gốc, gồm AIOpsLab/ITBench; chốt đóng góp và giới hạn tính mới.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R6-T01-S03",
          "sourceSubtasks": [
            "R6-T01-S03"
          ],
          "title": "Chốt kỷ yếu/đợt nhận bài, template, hạn và điều kiện chấp nhận đăng với thầy.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R6-T01-S01",
          "title": "Lập introduction/method quanh RQ1–RQ3 và bỏ khẳng định kết quả cũ chưa kiểm chứng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T01"
        },
        {
          "sourceId": "R6-T01-S02",
          "title": "Đối chiếu tài liệu gốc, gồm AIOpsLab/ITBench; chốt đóng góp và giới hạn tính mới.",
          "representation": "subissue",
          "targetLegacyKey": "R6-T01-S02"
        },
        {
          "sourceId": "R6-T01-S03",
          "title": "Chốt kỷ yếu/đợt nhận bài, template, hạn và điều kiện chấp nhận đăng với thầy.",
          "representation": "subissue",
          "targetLegacyKey": "R6-T01-S03"
        },
        {
          "sourceId": "R6-T01-S04",
          "title": "Hoàn thiện sơ đồ và mô tả phương pháp theo triển khai thực tế.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R0-T01-S01",
          "targetLegacyKey": "R0-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R0-T04-S01",
          "targetLegacyKey": "R0-T04",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R6-T02",
      "title": "Thực nghiệm chính thức và khóa dữ liệu",
      "source": "docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md",
      "milestoneLegacyId": "R6",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R6-T02-S02",
          "sourceSubtasks": [
            "R6-T02-S02"
          ],
          "title": "Chạy đủ số lặp B0/B1/B2/BM và B3 nếu giữ claim RQ2, kể cả manual có thao tác thật.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R6-T02-S03",
          "sourceSubtasks": [
            "R6-T02-S03"
          ],
          "title": "Phân tích tỷ lệ phục hồi, action đúng/sai/thừa, KPI, độ bất định và overhead/cost theo RQ.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R6-T02-S01",
          "title": "Kiểm tra gate, protocol, nhãn không lộ đáp án và các lỗi/KPI chưa đạt trước formal run.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T02"
        },
        {
          "sourceId": "R6-T02-S02",
          "title": "Chạy đủ số lặp B0/B1/B2/BM và B3 nếu giữ claim RQ2, kể cả manual có thao tác thật.",
          "representation": "subissue",
          "targetLegacyKey": "R6-T02-S02"
        },
        {
          "sourceId": "R6-T02-S03",
          "title": "Phân tích tỷ lệ phục hồi, action đúng/sai/thừa, KPI, độ bất định và overhead/cost theo RQ.",
          "representation": "subissue",
          "targetLegacyKey": "R6-T02-S03"
        },
        {
          "sourceId": "R6-T02-S04",
          "title": "Khóa dataset và đối chiếu từng claim với RQ, nhóm đo và phạm vi kết luận.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T02"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R5-T03",
          "targetLegacyKey": "R5-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R6-T03",
      "title": "Hoàn thiện và nộp bản paper đầu",
      "source": "docs/recovery/phases/R6-paper/R6-T03-paper-submission.md",
      "milestoneLegacyId": "R6",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R6-T03-S02",
          "sourceSubtasks": [
            "R6-T03-S02"
          ],
          "title": "Hai người rà số liệu, đối chứng, claim tính mới/giá trị AI và xin góp ý thầy.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R6-T03-S01",
          "title": "Viết results/discussion/limitations trả lời RQ từ dữ liệu đã khóa.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T03"
        },
        {
          "sourceId": "R6-T03-S02",
          "title": "Hai người rà số liệu, đối chứng, claim tính mới/giá trị AI và xin góp ý thầy.",
          "representation": "subissue",
          "targetLegacyKey": "R6-T03-S02"
        },
        {
          "sourceId": "R6-T03-S03",
          "title": "Soát template, hình/bảng, trích dẫn và hồ sơ nộp.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T03"
        },
        {
          "sourceId": "R6-T03-S04",
          "title": "Nộp khi có đợt nhận bài hợp lệ và lưu biên nhận.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R6-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R6-T01",
          "targetLegacyKey": "R6-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R6-T02",
          "targetLegacyKey": "R6-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R7-T01",
      "title": "Theo dõi bài và xử lý phản biện",
      "source": "docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md",
      "milestoneLegacyId": "R7",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R7-T01-S02",
          "sourceSubtasks": [
            "R7-T01-S02"
          ],
          "title": "Xử lý vòng phản biện đầu nếu đã nhận; phản hồi trong 3 ngày làm việc.",
          "condition": "only_after_review_received",
          "linearId": null
        },
        {
          "legacyKey": "R7-T01-S03",
          "sourceSubtasks": [
            "R7-T01-S03"
          ],
          "title": "Xử lý vòng tiếp theo nếu có, bổ sung phép đo khi reviewer yêu cầu.",
          "condition": "only_after_additional_review_received",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R7-T01-S01",
          "title": "Theo dõi tình trạng bài, lập bảng phản biện → việc sửa → bằng chứng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T01"
        },
        {
          "sourceId": "R7-T01-S02",
          "title": "Xử lý vòng phản biện đầu nếu đã nhận; phản hồi trong 3 ngày làm việc.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T01-S02"
        },
        {
          "sourceId": "R7-T01-S03",
          "title": "Xử lý vòng tiếp theo nếu có, bổ sung phép đo khi reviewer yêu cầu.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T01-S03"
        },
        {
          "sourceId": "R7-T01-S04",
          "title": "Đạt mốc mục tiêu có xác nhận chấp nhận đăng.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T01"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R6-T03",
          "targetLegacyKey": "R6-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R7-T02",
      "title": "Hoàn thiện Word và các sản phẩm nghiệm thu",
      "source": "docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md",
      "milestoneLegacyId": "R7",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R7-T02-S01",
          "sourceSubtasks": [
            "R7-T02-S01"
          ],
          "title": "Viết báo cáo Word bằng phương pháp và dữ liệu mới đã kiểm chứng.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R7-T02-S02",
          "sourceSubtasks": [
            "R7-T02-S02"
          ],
          "title": "Chuẩn bị video demo, slide/poster theo danh mục sản phẩm phải nộp.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R7-T02-S03",
          "sourceSubtasks": [
            "R7-T02-S03"
          ],
          "title": "Đóng gói source, manifest, runbook, dataset và Word/PDF.",
          "condition": "always",
          "linearId": null
        },
        {
          "legacyKey": "R7-T02-S05",
          "sourceSubtasks": [
            "R7-T02-S05"
          ],
          "title": "Đối chiếu thời hạn hồ sơ với nguồn của trường/thầy trước khi nộp nghiệm thu.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R7-T02-S01",
          "title": "Viết báo cáo Word bằng phương pháp và dữ liệu mới đã kiểm chứng.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T02-S01"
        },
        {
          "sourceId": "R7-T02-S02",
          "title": "Chuẩn bị video demo, slide/poster theo danh mục sản phẩm phải nộp.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T02-S02"
        },
        {
          "sourceId": "R7-T02-S03",
          "title": "Đóng gói source, manifest, runbook, dataset và Word/PDF.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T02-S03"
        },
        {
          "sourceId": "R7-T02-S04",
          "title": "Đối chiếu chéo số liệu và sản phẩm giữa paper, Word, demo và dữ liệu.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T02"
        },
        {
          "sourceId": "R7-T02-S05",
          "title": "Đối chiếu thời hạn hồ sơ với nguồn của trường/thầy trước khi nộp nghiệm thu.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T02-S05"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R5-T03",
          "targetLegacyKey": "R5-T03",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R6-T02",
          "targetLegacyKey": "R6-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    },
    {
      "legacyId": "R7-T03",
      "title": "Nộp hồ sơ và thực hiện nghiệm thu",
      "source": "docs/recovery/phases/R7-acceptance/R7-T03-acceptance-submission.md",
      "milestoneLegacyId": "R7",
      "linearId": null,
      "subissues": [
        {
          "legacyKey": "R7-T03-S01",
          "sourceSubtasks": [
            "R7-T03-S01"
          ],
          "title": "Chạy thử demo và tập báo cáo nghiệm thu.",
          "condition": "always",
          "linearId": null
        }
      ],
      "sourceCoverage": [
        {
          "sourceId": "R7-T03-S01",
          "title": "Chạy thử demo và tập báo cáo nghiệm thu.",
          "representation": "subissue",
          "targetLegacyKey": "R7-T03-S01"
        },
        {
          "sourceId": "R7-T03-S02",
          "title": "Xác minh bằng chứng chấp nhận đăng rồi nộp bộ hồ sơ nghiệm thu.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T03"
        },
        {
          "sourceId": "R7-T03-S03",
          "title": "Báo cáo hội đồng và xử lý yêu cầu chỉnh sửa theo lịch được xác nhận.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T03"
        },
        {
          "sourceId": "R7-T03-S04",
          "title": "Đối chiếu kết quả nghiệm thu, sản phẩm còn thiếu và lưu hồ sơ cuối.",
          "representation": "parent_acceptance_checklist",
          "targetLegacyKey": "R7-T03"
        }
      ],
      "dependencyCandidates": [
        {
          "sourceRef": "R7-T01",
          "targetLegacyKey": "R7-T01",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        },
        {
          "sourceRef": "R7-T02",
          "targetLegacyKey": "R7-T02",
          "reviewRequired": true,
          "reason": "Source prerequisite candidate; resolve exact contract/evidence before creating blocked-by"
        }
      ]
    }
  ],
  "connection": "linear_zero_door",
  "targetWorkspaceSlug": "zero-door",
  "targetTeamKey": "ZER",
  "verificationDate": "2026-10-17",
  "projectDiscovery": {
    "count": 0,
    "hasNextPage": false,
    "includeArchived": true
  },
  "verifiedMembers": [
    {
      "id": "99fe281d-6b71-41a3-8c8e-76be59884dc7",
      "name": "Lê Văn Hoàng"
    },
    {
      "id": "95925f55-11a6-4a02-ae0c-70e823f50d5f",
      "name": "Hoa8001"
    }
  ],
  "observedStatusCatalog": {
    "Backlog": "4f6bdf4b-5cb4-4778-8716-29d382681d7b",
    "Todo": "58e883f0-b147-497f-b574-ecb03d00875d",
    "In Progress": "b64c7b34-0852-4fa7-a738-9987a0c9e35b",
    "In Review": "27ed5c1c-b357-4d45-ae5d-9ba89c5f240d",
    "Done": "bc69a74e-64ee-484d-b83a-ac2a6bcee00d",
    "Canceled": "fe1483c4-268b-4e76-927a-7c3bac2f9e2e",
    "Duplicate": "d46889d6-ee6e-445c-99d9-1545b358d4a2"
  }
}

<!-- END SOURCE: docs/recovery/linear/mapping.json -->


<!-- SOURCE: docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md -->

## Nguồn `docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md`

# R0-T01 — Khóa phạm vi và tiêu chí đánh giá

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R0](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** IN_PROGRESS
- **Owner đề xuất trong snapshot:** Codex lập ma trận/source ledger; Hoàng quyết định, Hòa đối chiếu
- **Reviewer đề xuất trong snapshot:** Claude đối chiếu; Hoàng + Hòa chốt phạm vi, tiêu chí và nguồn
- **Bắt đầu trong lịch nguồn:** 2026-10-17
- **Due trong lịch nguồn:** 2026-10-18 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** Không có.

## Phạm vi phiên này

Bước S03 đã có đầu ra dự kiến duy nhất: `docs/evidence/R0-T01-S03/baseline-source-ledger.md`. Không sửa dữ liệu gốc. S02 là việc lập ma trận/định nghĩa, chưa chốt đường dẫn đầu ra. Không dùng phạm vi S03 để sửa toàn task.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R0-T01-S01 | Ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI và bài được chấp nhận đăng. | 2026-10-09 | 2026-10-09 | DONE |
| R0-T01-S02 | Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số. | 2026-10-17 | 2026-10-18 | TODO |
| R0-T01-S03 | Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08. | 2026-10-17 | 2026-10-18 | READY |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R0-T01-S01

Các xác nhận của người dùng đã được ghi trong file SCOPE.md của recovery.

- Bằng chứng / ngày hoàn tất thực tế: [Phạm vi đã ghi nhận](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/SCOPE.md); DONE kế thừa từ roadmap trước khi tách, chưa có ngày hoàn tất riêng được ghi.

### R0-T01-S02

Ma trận truy vết; cách đánh giá MTTR 120/180 giây theo thuyết minh, MTTD <60 giây và uptime ≥99,9%, không hạ ngưỡng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T01-S03

HEAD/dirty files, hash và số dòng từng CSV, timestamp lưu trong dữ liệu tách khỏi timeline Git; nguồn DOCX/xác nhận mới/IDE/chat được phân loại, path được kiểm tra. Giữ nguyên raw/handoff; thiếu lịch sử hoặc danh tính thì UNKNOWN.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md -->


<!-- SOURCE: docs/recovery/phases/R0-foundations/R0-T02-local-lab.md -->

## Nguồn `docs/recovery/phases/R0-foundations/R0-T02-local-lab.md`

# R0-T02 — Khôi phục môi trường local

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R0](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** READY
- **Owner đề xuất trong snapshot:** Codex thực hiện; Claude review; Hoàng chốt nếu cần thay đổi hoặc xóa lab
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-17
- **Due trong lịch nguồn:** 2026-10-19 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** Không có.

## Phạm vi phiên này

Bước S01 chỉ đọc môi trường; file đầu ra: `docs/evidence/R0-T02-S01/inventory.md`. Không start/recreate/delete hoặc đọc secret trong bước này. S02/S03 chỉ mở sau inventory và phạm vi thao tác được chốt; không chạy mù start-demo/recreate.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R0-T02-S01 | Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới. | 2026-10-17 | 2026-10-18 | READY |
| R0-T02-S02 | Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại. | 2026-10-18 | 2026-10-19 | TODO |
| R0-T02-S03 | Kiểm tra Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique. | 2026-10-19 | 2026-10-19 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R0-T02-S01

Inventory có timestamp/kết quả hoặc lỗi rõ, context/Git/containers/volumes/ports/resources và phiên bản/args K3s khi truy cập; xác định nguyên nhân API không truy cập được. Truy vấn lỗi/bị ngắt không được coi là inventory rỗng hoặc container exited.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T02-S02

Kubernetes API truy cập; dữ liệu cần giữ được bảo toàn; lệnh dựng và profile tài nguyên được ghi. Kiểm tra script đúng chức năng; start-demo.ps1 hiện dừng mọi kubectl và dùng context hiện hành nên không chạy mù; rebuild-nemesis.ps1 build/import/rollout, không tạo cluster. Giữ volume/dữ liệu và ghi phạm vi thao tác.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T02-S03

Log/message truy vết, truy vấn metric và giao dịch mẫu; trạng thái Running riêng lẻ chưa đủ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R0-foundations/R0-T02-local-lab.md -->


<!-- SOURCE: docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md -->

## Nguồn `docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md`

# R0-T03 — Xác nhận một backend LLM thật

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R0](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex tích hợp/test; Hoàng chọn provider, credential và ngân sách; Claude review
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-18
- **Due trong lịch nguồn:** 2026-10-20 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R0-T03-S01 | Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy. | 2026-10-18 | 2026-10-19 | TODO |
| R0-T03-S02 | Gọi LLM bằng đầu vào nghiên cứu và kiểm tra đầu ra theo schema. | 2026-10-19 | 2026-10-20 | TODO |
| R0-T03-S03 | Thử timeout, retry có giới hạn và fallback; ghi rõ khi dùng RULES thay AI. | 2026-10-20 | 2026-10-20 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R0-T03-S01

Quyết định provider có căn cứ và cấu hình giới hạn; không suy ra quyền API từ credit Azure.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T03-S02

Bằng chứng lượt gọi mới có timestamp/run_id, request ID khi backend hỗ trợ, tên/phiên bản model, latency/usage khả dụng và kết quả che bí mật; ghi trường không được provider trả. SDK/manifest/evaluation_report không thay log lượt gọi.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T03-S03

Log tình huống lỗi và kiểm chứng fallback không bị ghi nhãn là quyết định LLM.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md -->


<!-- SOURCE: docs/recovery/phases/R0-foundations/R0-T04-research-questions.md -->

## Nguồn `docs/recovery/phases/R0-foundations/R0-T04-research-questions.md`

# R0-T04 — Khóa câu hỏi nghiên cứu và thiết kế đối chứng

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R0](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex chuẩn bị; Hoàng + Hòa khóa thiết kế nghiên cứu; Claude review kỹ thuật
- **Reviewer đề xuất trong snapshot:** Claude đối chiếu kỹ thuật; Hoàng + Hòa khóa RQ/đối chứng/claim
- **Bắt đầu trong lịch nguồn:** 2026-10-18
- **Due trong lịch nguồn:** 2026-10-19 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R0-T04-S01 | Chốt RQ1–RQ3, đóng góp dự kiến và giới hạn claim. | 2026-10-18 | 2026-10-18 | TODO |
| R0-T04-S02 | Khóa B0/B1/B2, giữ BM; quyết định phạm vi B3 và budget. | 2026-10-18 | 2026-10-19 | TODO |
| R0-T04-S03 | Chốt ground truth, tập action đúng và ranh giới dữ liệu không lộ đáp án. | 2026-10-19 | 2026-10-19 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R0-T04-S01

Bảng câu hỏi → metric → claim; tách đạt chức năng/KPI với chứng minh giá trị nghiên cứu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T04-S02

Ma trận đối chứng và điều kiện B3; nếu bỏ B3 thì bỏ claim ưu thế nhiều tác tử, không bỏ cam kết gốc.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R0-T04-S03

Định nghĩa nhãn, mẫu số metric và schema evidence; bên chữa lỗi không nhận case/attack label hoặc đáp án.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R0-foundations/R0-T04-research-questions.md -->


<!-- SOURCE: docs/recovery/phases/R0-foundations/README.md -->

## Nguồn `docs/recovery/phases/R0-foundations/README.md`

# R0 — Nền tảng và phạm vi

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-17 → 2026-10-20, due 21:00 Asia/Saigon.

**Gate G0:** Lab có giao dịch kiểm chứng được, một backend LLM trả kết quả thật; phạm vi, RQ, đối chứng và ranh giới nhãn/evidence được khóa.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R0-T01 — Khóa phạm vi và tiêu chí đánh giá](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md)
- [R0-T02 — Khôi phục môi trường local](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T02-local-lab.md)
- [R0-T03 — Xác nhận một backend LLM thật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md)
- [R0-T04 — Khóa câu hỏi nghiên cứu và thiết kế đối chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R0-foundations/README.md -->


<!-- SOURCE: docs/recovery/phases/R1-measurement/R1-T01-event-contract.md -->

## Nguồn `docs/recovery/phases/R1-measurement/R1-T01-event-contract.md`

# R1-T01 — Thống nhất hợp đồng sự kiện và lưu dấu vết

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R1](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude soạn contract và sửa producer/consumer theo task được mở; Codex review, Hoàng chốt ngữ nghĩa
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-17
- **Due trong lịch nguồn:** 2026-10-20 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md), [R0-T04-S03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md) (subtask trong file).

## Phạm vi phiên này

Bước soạn draft S01 chỉ ghi `docs/design/r1-event-contract.md`; draft mục tiêu 18/10/2026 21:00, bản khóa 19/10/2026 21:00. Có thể soạn khi lab/LLM chưa sẵn sàng; khóa schema/DONE vẫn chờ phụ thuộc R0. S02/S03 chưa mở allowlist mã, test hoặc schema dùng chung.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R1-T01-S01 | Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi. | 2026-10-17 | 2026-10-19 | TODO |
| R1-T01-S02 | Truyền ID qua Kafka/HTTP và lưu sự kiện gốc phục vụ tái tính. | 2026-10-19 | 2026-10-20 | TODO |
| R1-T01-S03 | Tách ground truth/log điều khiển khỏi evidence dành cho bên chữa lỗi. | 2026-10-19 | 2026-10-20 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R1-T01-S01

Schema/version và ví dụ; mốc attack effect/detect/action/recovery/stop có nguồn ghi riêng. Terminal action SUCCESS/FAILED/PARTIAL được tách khỏi RECOVERY_VERIFIED.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T01-S02

Một chuỗi sự kiện xuyên thành phần; bản ghi bền vững có thể xuất và đối chiếu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T01-S03

Phép thử kiểm tra prompt/query không lộ case label, attack command hoặc đáp án; ID trung tính vẫn truy vết được ở harness.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R1-measurement/R1-T01-event-contract.md -->


<!-- SOURCE: docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md -->

## Nguồn `docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md`

# R1-T02 — Đo sức khỏe và thời gian độc lập

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R1](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex làm probe/runner/analysis; Claude review
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-20
- **Due trong lịch nguồn:** 2026-10-22 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T01-event-contract.md), [R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T02-local-lab.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R1-T02-S01 | Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture. | 2026-10-20 | 2026-10-21 | TODO |
| R1-T02-S02 | Tính MTTD/MTTR từ mốc sự kiện và xác nhận hồi phục bằng probe. | 2026-10-21 | 2026-10-22 | TODO |
| R1-T02-S03 | Xử lý thiếu dữ liệu, timeout, FAILED/PARTIAL và FPR có mẫu số rõ ràng. | 2026-10-21 | 2026-10-22 | TODO |
| R1-T02-S04 | Bổ sung metric quyết định, phục hồi theo lượt và usage/cost theo run. | 2026-10-21 | 2026-10-22 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R1-T02-S01

Timestamp, chu kỳ probe, tiêu chí healthy và ví dụ lỗi được quan sát thật.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T02-S02

Tái tính incident từ raw: MTTD effect→detector detect, MTTR detect→recovery xác minh, total recovery effect→recovery. Không lấy heal history/replica tăng làm detect; ghi chu kỳ probe và độ phân giải thời gian.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T02-S03

Phép thử có action thất bại nhưng chưa recovery, timeout và missing; chưa xác minh recovery thì MTTR chưa xác định/censored theo protocol, không điền 0 hoặc 1s. Giữ mọi run trong mẫu số, báo riêng phân phối lượt recovered và tỷ lệ failure; thiếu dữ liệu không thành uptime 100%.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T02-S04

Định nghĩa mẫu số; lưu đề xuất trước guard, action thực thi, false action, recovery/failure và số call/token kể cả retry.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md -->


<!-- SOURCE: docs/recovery/phases/R1-measurement/R1-T03-dashboard-and-baselines.md -->

## Nguồn `docs/recovery/phases/R1-measurement/R1-T03-dashboard-and-baselines.md`

# R1-T03 — Sửa dashboard và các chế độ đối chứng

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R1](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex sửa dashboard/profile; Claude review API và cách tắt healer
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-22
- **Due trong lịch nguồn:** 2026-10-23 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R1-T03-S01 | Bỏ số ngẫu nhiên và nội dung mô phỏng khỏi phần được trình bày là kết quả thực. | 2026-10-22 | 2026-10-22 | TODO |
| R1-T03-S02 | Cho dashboard và bộ xuất dữ liệu dùng chung phép đo. | 2026-10-22 | 2026-10-23 | TODO |
| R1-T03-S03 | Tách MANUAL, RULES và AI; MANUAL không tự kích hoạt healer. | 2026-10-23 | 2026-10-23 | TODO |
| R1-T03-S04 | Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi. | 2026-10-23 | 2026-10-23 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R1-T03-S01

Dashboard hiển thị trạng thái không có dữ liệu và nguồn của số liệu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T03-S02

Cùng run_id cho ra cùng KPI; phản ánh lỗi và độ trễ cập nhật.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T03-S03

Log ba chế độ và phép thử chứng minh đối chứng manual không bị auto-heal.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T03-S04

Cấu hình HPA/guard/probe được ghi rõ; chứng minh ZERO DOOR không phát lệnh heal trong B0, vẫn có đo độc lập.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R1-measurement/R1-T03-dashboard-and-baselines.md -->


<!-- SOURCE: docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md -->

## Nguồn `docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md`

# R1-T04 — Giới hạn tác động, kiểm soát lệnh và CI

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R1](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude sửa guard/worker/CI; Codex review
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-18
- **Due trong lịch nguồn:** 2026-10-21 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R1-T04-S01 | Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải. | 2026-10-18 | 2026-10-20 | TODO |
| R1-T04-S02 | Kiểm soát truy cập lệnh, sự kiện trùng và payload sai. | 2026-10-20 | 2026-10-21 | TODO |
| R1-T04-S03 | Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI. | 2026-10-21 | 2026-10-21 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R1-T04-S01

Cấu hình allowlist cùng phép thử host, port, protocol, redirect và budget; trần thời lượng hiệu dụng không vượt trần vận hành dù maxDuration trong command lớn hơn. Phân biệt duration, executor và attack_effect.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T04-S02

Phép thử lệnh bị từ chối, schema lỗi và duplicate; log lý do.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R1-T04-S03

Phiên bản dependency/image và kết quả CI cho các hành vi cần bảo vệ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md -->


<!-- SOURCE: docs/recovery/phases/R1-measurement/README.md -->

## Nguồn `docs/recovery/phases/R1-measurement/README.md`

# R1 — Sự kiện và phép đo

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-17 → 2026-10-23, due 21:00 Asia/Saigon.

**Gate G1:** Một sự cố có ID xuyên suốt, metric hồi phục/quyết định tái tính được; evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R1-T01 — Thống nhất hợp đồng sự kiện và lưu dấu vết](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T01-event-contract.md)
- [R1-T02 — Đo sức khỏe và thời gian độc lập](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md)
- [R1-T03 — Sửa dashboard và các chế độ đối chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T03-dashboard-and-baselines.md)
- [R1-T04 — Giới hạn tác động, kiểm soát lệnh và CI](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R1-measurement/README.md -->


<!-- SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md -->

## Nguồn `docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md`

# R2-T01 — Fixture và executor SQL injection

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R2](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude triển khai fixture/executor theo thiết kế được chốt; Codex review
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-21
- **Due trong lịch nguồn:** 2026-10-24 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T02-local-lab.md), [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T01-event-contract.md), [R1-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md) (subtask trong file).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R2-T01-S01 | Chốt fixture nghiệp vụ giả lập, dữ liệu giả, route vulnerable/safe và nguồn IP. | 2026-10-21 | 2026-10-21 | TODO |
| R2-T01-S02 | Triển khai fixture/database nhẹ và đường ingress quan sát được. | 2026-10-21 | 2026-10-22 | TODO |
| R2-T01-S03 | Bổ sung executor SQLi bằng template và giới hạn đã chốt. | 2026-10-22 | 2026-10-23 | TODO |
| R2-T01-S04 | Chứng minh tác động SQLi, log và phân biệt lưu lượng tấn công với benign. | 2026-10-23 | 2026-10-24 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R2-T01-S01

Thiết kế fixture, tiêu chí tác động SQLi và cách liên hệ với luồng microservices.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T01-S02

Fixture hoạt động, route/query/log được kiểm chứng; phiên bản đóng gói.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T01-S03

Payload hợp lệ chạy được; tham số ngoài phạm vi bị từ chối.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T01-S04

Kết quả trước/sau, truy vết request, IP đáng tin cậy và traffic đối chứng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md -->


<!-- SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md -->

## Nguồn `docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md`

# R2-T02 — DDoS L7 và cạn tài nguyên đúng mục tiêu

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R2](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude sửa executor/đường tác động; Codex review phép đo
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-21
- **Due trong lịch nguồn:** 2026-10-25 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T02-local-lab.md), [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T01-event-contract.md), [R1-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md) (subtask trong file), [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R2-T02-S01 | Cho HTTP flood đi qua route/cổng được giám sát, có RPS và thời lượng giới hạn. | 2026-10-21 | 2026-10-22 | TODO |
| R2-T02-S02 | Tạo CPU exhaustion trên workload mục tiêu, giới hạn tài nguyên rõ ràng. | 2026-10-22 | 2026-10-23 | TODO |
| R2-T02-S03 | Kiểm tra cleanup, traffic bình thường và memory variant nếu đưa vào protocol. | 2026-10-23 | 2026-10-24 | TODO |
| R2-T02-S04 | Chuẩn bị tải C0/C1 cùng biến thể C2/C4 có triệu chứng chồng lấp. | 2026-10-24 | 2026-10-25 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R2-T02-S01

Metric và log trên đúng đường giao dịch; tác động latency/error có thể tái hiện.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T02-S02

CPU/latency/error của chính dịch vụ bị tác động; KPI CPU target >80% (DOCX P179) có mẫu số, cửa sổ và attribution rõ; không suy từ pod stress riêng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T02-S03

Target trở lại baseline; cleanup có return code và kiểm tra tài nguyên còn sót, không giữ SUCCESS khi cleanup lỗi mà giấu lỗi. Memory variant có bằng chứng hoặc quyết định loại khỏi protocol.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T02-S04

Case catalog, ground truth/action set và seed/tải tái lập; tách biến thể pilot với đánh giá, không giả lập metric.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md -->


<!-- SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md -->

## Nguồn `docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md`

# R2-T03 — Chạy phối hợp và dừng có kiểm soát

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R2](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude thực hiện; Codex review điều phối/cleanup
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-25
- **Due trong lịch nguồn:** 2026-10-25 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md), [R2-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md), [R1-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R2-T03-S01 | Điều phối ba executor đồng thời theo budget chung. | 2026-10-25 | 2026-10-25 | TODO |
| R2-T03-S02 | Thử start, stop, cancel và cleanup khi một executor lỗi. | 2026-10-25 | 2026-10-25 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R2-T03-S01

Ba vector có event riêng cùng run_id; không phát một loại COMBINED mà worker không hỗ trợ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R2-T03-S02

Không còn tác động sau stop; trạng thái và tài nguyên được đối chiếu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md -->


<!-- SOURCE: docs/recovery/phases/R2-chaos-scenarios/README.md -->

## Nguồn `docs/recovery/phases/R2-chaos-scenarios/README.md`

# R2 — Ba kịch bản Chaos

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-21 → 2026-10-25, due 21:00 Asia/Saigon.

**Gate G2:** SQLi, DDoS L7 và resource exhaustion gây được tác động đúng mục tiêu, có dấu vết và cleanup; chạy phối hợp vẫn giữ giới hạn.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R2-T01 — Fixture và executor SQL injection](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md)
- [R2-T02 — DDoS L7 và cạn tài nguyên đúng mục tiêu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T02-ddos-and-resource-exhaustion.md)
- [R2-T03 — Chạy phối hợp và dừng có kiểm soát](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R2-chaos-scenarios/README.md -->


<!-- SOURCE: docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md -->

## Nguồn `docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md`

# R3-T01 — Trạng thái hồi phục và scale

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R3](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude sửa healer; Codex review hậu điều kiện/probe
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-23
- **Due trong lịch nguồn:** 2026-10-24 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R3-T01-S01 | Tách API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED. | 2026-10-23 | 2026-10-23 | TODO |
| R3-T01-S02 | Kiểm chứng scale up tăng capacity và sức khỏe dịch vụ. | 2026-10-23 | 2026-10-24 | TODO |
| R3-T01-S03 | Kiểm chứng scale down có hysteresis và quyền điều khiển rõ với HPA. | 2026-10-24 | 2026-10-24 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R3-T01-S01

State machine/timeout và log đối chiếu probe; API nhận lệnh hoặc terminal FAILED/PARTIAL không đóng recovery. Phân biệt hồi phục nhờ controller/hết fault với bằng chứng tác động healer; restart phải xác minh pod thay thế và nghiệp vụ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T01-S02

Replica ready, metric capacity và probe trước/sau.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T01-S03

Không dao động; phục hồi replica baseline không bị tính thành heal nếu dịch vụ chưa khỏe.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md -->


<!-- SOURCE: docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md -->

## Nguồn `docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md`

# R3-T02 — Block IP thực thi được và rollback đúng phiên bản

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R3](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude triển khai block/rollback; Codex review IP, release và traffic đối chứng
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-24
- **Due trong lịch nguồn:** 2026-10-26 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T02-probes-and-metrics.md), [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R3-T02-S01 | Chốt enforcement point và nguồn IP; xử lý NAT/header tin cậy. | 2026-10-24 | 2026-10-24 | TODO |
| R3-T02-S02 | Chặn attacker, giữ traffic benign, có TTL và gỡ chặn. | 2026-10-24 | 2026-10-25 | TODO |
| R3-T02-S03 | Tạo phiên bản lỗi/known-good và case C3 có kiểm soát, tách nhãn đáp án khỏi telemetry. | 2026-10-25 | 2026-10-25 | TODO |
| R3-T02-S04 | Khôi phục image/config/revision thật và xác minh rollout lẫn probe. | 2026-10-25 | 2026-10-26 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R3-T02-S01

Sơ đồ request, selector/nhãn pod và thử xác nhận IP; không dùng IP mặc định 0.0.0.0. Đối chiếu controller K3s/args thực tế; không suy Flannel bỏ policy hoặc thay CNI khi chưa có bằng chứng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T02-S02

Request bị chặn/được phép đúng đối tượng; hiệu lực và hết hạn được kiểm tra sau restart. Không dựa duy nhất vào threading.Timer; tách endpoint reset (không xóa policy), runner reset (có lệnh xóa theo nhãn) và TTL; hậu điều kiện cleanup phải đo được.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T02-S03

Image/config/revision, triệu chứng và ground truth có danh tính rõ; bên chữa lỗi nhận lịch deploy/log thật, không nhận đáp án rollback.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T02-S04

Danh tính trước/sau và dịch vụ hồi phục; thay annotation riêng lẻ không đủ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md -->


<!-- SOURCE: docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md -->

## Nguồn `docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md`

# R3-T03 — Consumer, retry và tương tác controller

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R3](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude sửa consumer/state; Codex review failure/restart/HPA
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-24
- **Due trong lịch nguồn:** 2026-10-27 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R1-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R1-measurement/R1-T04-guards-and-ci.md), [R3-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R3-T03-S01 | Sửa blocking consumer, ack, dedup, cooldown và retry có giới hạn. | 2026-10-24 | 2026-10-25 | TODO |
| R3-T03-S02 | Thử restart, nhiều replica, PodKill và tương tác HPA. | 2026-10-25 | 2026-10-26 | TODO |
| R3-T03-S03 | Thử worker/healer restart và mất telemetry. | 2026-10-26 | 2026-10-27 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R3-T03-S01

Một action cho một event hiệu lực; lỗi không kẹt consumer hoặc lặp lệnh vô hạn.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T03-S02

Log tác nhân gây hồi phục; phân biệt hiệu ứng Kubernetes/HPA với healer.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R3-T03-S03

Run dở có trạng thái rõ; dữ liệu thiếu không sinh kết luận thành công.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md -->


<!-- SOURCE: docs/recovery/phases/R3-recovery/README.md -->

## Nguồn `docs/recovery/phases/R3-recovery/README.md`

# R3 — Phục hồi và block IP

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-23 → 2026-10-27, due 21:00 Asia/Saigon.

**Gate G3:** Scale up/down, block IP và rollback có tác động thật; phân biệt API chấp nhận với hồi phục; có kiểm tra restart, HPA và trạng thái thất bại.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R3-T01 — Trạng thái hồi phục và scale](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T01-recovery-state-and-scaling.md)
- [R3-T02 — Block IP thực thi được và rollback đúng phiên bản](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md)
- [R3-T03 — Consumer, retry và tương tác controller](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R3-recovery/README.md -->


<!-- SOURCE: docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md -->

## Nguồn `docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md`

# R4-T01 — LLM adapter chung và Nemesis

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R4](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex làm adapter/Nemesis; Claude review; bàn giao file sau R2
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-26
- **Due trong lịch nguồn:** 2026-10-28 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T03-llm-backend.md), [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T01-sqli-fixture.md), [R2-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R2-chaos-scenarios/R2-T03-combined-run-and-cleanup.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R4-T01-S01 | Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout. | 2026-10-26 | 2026-10-26 | TODO |
| R4-T01-S02 | Nối observation → kế hoạch Nemesis → executor → kết quả. | 2026-10-26 | 2026-10-27 | TODO |
| R4-T01-S03 | Thêm start/stop, max rounds/calls và điều kiện dừng. | 2026-10-27 | 2026-10-28 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R4-T01-S01

Interface và trace thật; quota/cost được cộng theo run.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T01-S02

LLM chọn kế hoạch trong registry hợp lệ; kế hoạch được kiểm tra trước khi thực thi.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T01-S03

Một phiên tự kết thúc trong budget; log stop/cancel và số gọi model.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md -->


<!-- SOURCE: docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md -->

## Nguồn `docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md`

# R4-T02 — Gaia và Hephaestus có quyết định LLM được giới hạn

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R4](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Claude nối Gaia/Hephaestus với adapter; Codex review
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-27
- **Due trong lịch nguồn:** 2026-10-29 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R4-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md) (subtask trong file), [R3-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T02-block-ip-and-rollback.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R4-T02-S01 | Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM. | 2026-10-27 | 2026-10-28 | TODO |
| R4-T02-S02 | Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục. | 2026-10-28 | 2026-10-28 | TODO |
| R4-T02-S03 | Thử JSON sai, timeout, 429 và thiếu bằng chứng; fallback được đánh dấu. | 2026-10-28 | 2026-10-29 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R4-T02-S01

Incident có metric/log đầu vào, diagnosis và latency; MTTD không bị định nghĩa lại.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T02-S02

Trace đề xuất, action, lý do chấp nhận/từ chối, decision latency và probe kết quả; không chữa thừa ở case lành tính.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T02-S03

Các trường hợp lỗi không tạo action ngoài allowlist và không bị ghi nhãn AI thành công.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md -->


<!-- SOURCE: docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md -->

## Nguồn `docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md`

# R4-T03 — Chứng minh vòng multi-agent và đối chứng RULES

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R4](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex chạy/đối chiếu pilot; Claude review trace
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-29
- **Due trong lịch nguồn:** 2026-10-29 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R4-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md), [R4-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md), [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R4-T03-S01 | Chạy một vòng có trace observation–decision–result cho cả ba agent. | 2026-10-29 | 2026-10-29 | TODO |
| R4-T03-S02 | Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage. | 2026-10-29 | 2026-10-29 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R4-T03-S01

Trace có ID liên kết và backend/model thật; phân biệt rõ quyết định rule và LLM.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T03-S02

Bảng đối chứng controller/rules/multi-LLM; cùng evidence cho B1/B2, guard/probe/profile HPA cố định; không mặc định AI tốt hơn.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md -->


<!-- SOURCE: docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md -->

## Nguồn `docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md`

# R4-T04 — Đối chứng single-agent cho claim chia vai trò

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R4](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex chuẩn bị đối chứng; Hoàng + Hòa quyết định claim; Claude review
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-27
- **Due trong lịch nguồn:** 2026-10-29 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md), [R4-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md) (subtask trong file), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R3-recovery/R3-T03-consumer-and-controller.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R4-T04-S01 | Xác nhận giữ RQ2 hay giới hạn claim theo budget pilot. | 2026-10-27 | 2026-10-27 | TODO |
| R4-T04-S02 | Nếu giữ RQ2, cấu hình SINGLE_LLM gộp phân tích và chọn action. | 2026-10-27 | 2026-10-28 | TODO |
| R4-T04-S03 | Nếu giữ RQ2, pilot B2/B3 sau khi R4-T02-S02 hoàn tất, trên cùng case và kiểm tra dữ liệu. | 2026-10-28 | 2026-10-29 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R4-T04-S01

Quyết định ghi rõ thời lượng/call budget; không đủ nguồn lực thì bỏ claim ưu thế chia vai trò.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T04-S02

Cùng model/evidence/tools/guard với B2; harness tấn công giống nhau. Không giữ claim thì đóng bằng quyết định loại claim.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R4-T04-S03

Trace/cost/action/recovery đối chiếu; nếu B3 chưa chạy thì chưa đủ bằng chứng claim RQ2. Nếu loại claim, ghi rõ phạm vi còn lại.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md -->


<!-- SOURCE: docs/recovery/phases/R4-ai-agents/README.md -->

## Nguồn `docs/recovery/phases/R4-ai-agents/README.md`

# R4 — Tác tử và LLM

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-26 → 2026-10-29, due 21:00 Asia/Saigon.

**Gate G4:** Ba agent có trace thật, guard/fallback hoạt động; pilot B0/B1/B2 hợp lệ và quyết định B3 có bằng chứng hoặc giới hạn claim; không yêu cầu AI thắng.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R4-T01 — LLM adapter chung và Nemesis](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T01-llm-adapter-and-nemesis.md)
- [R4-T02 — Gaia và Hephaestus có quyết định LLM được giới hạn](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T02-gaia-and-hephaestus.md)
- [R4-T03 — Chứng minh vòng multi-agent và đối chứng RULES](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md)
- [R4-T04 — Đối chứng single-agent cho claim chia vai trò](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R4-ai-agents/README.md -->


<!-- SOURCE: docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md -->

## Nguồn `docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md`

# R5-T01 — Chạy đầy đủ đường tấn công–phát hiện–hồi phục

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R5](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex điều phối tích hợp; Claude review và sửa theo task con; Hoàng kiểm chứng
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-29
- **Due trong lịch nguồn:** 2026-10-30 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R4-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T03-multi-agent-evidence.md), [R4-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R4-ai-agents/R4-T04-single-agent-baseline.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R5-T01-S01 | Chụp phiên bản image/config/model/prompt và workload của đợt tích hợp. | 2026-10-29 | 2026-10-29 | TODO |
| R5-T01-S02 | Chạy từng vector qua toàn pipeline và đo bằng probe độc lập. | 2026-10-29 | 2026-10-30 | TODO |
| R5-T01-S03 | Thử bad release, benign traffic, thất bại và cleanup. | 2026-10-30 | 2026-10-30 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R5-T01-S01

Manifest/version/run metadata đủ dựng lại.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T01-S02

Ba incident có trace đầy đủ; không dùng /heal/trigger làm đường đo chính.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T01-S03

Mỗi tình huống có verdict và log; failure được giữ trong dữ liệu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md -->


<!-- SOURCE: docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md -->

## Nguồn `docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md`

# R5-T02 — Pilot, khóa protocol và War Game

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R5](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Codex chạy/đóng gói phép đo; Hoàng khóa protocol và giám sát; Claude review
- **Reviewer đề xuất trong snapshot:** Claude; Hoàng chốt quyết định/kết quả cần thiết
- **Bắt đầu trong lịch nguồn:** 2026-10-30
- **Due trong lịch nguồn:** 2026-10-31 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R5-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R5-T02-S01 | Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo. | 2026-10-30 | 2026-10-30 | TODO |
| R5-T02-S02 | Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI. | 2026-10-30 | 2026-10-30 | TODO |
| R5-T02-S03 | Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt. | 2026-10-31 | 2026-10-31 | TODO |
| R5-T02-S04 | Tái tính KPI; phân loại pass/fail, thiếu dữ liệu và nguyên nhân. | 2026-10-31 | 2026-10-31 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R5-T02-S01

Dữ liệu pilot nguyên bản cho B0/B1/B2 và B3 nếu giữ RQ2; căn cứ chọn số lặp và đánh giá lại thời lượng trong trần nguồn lực.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T02-S02

Protocol cố định trước formal run; B0/B1/B2/BM, quyết định B3/claim RQ2, profile HPA, biến thể đánh giá và ranh giới không lộ đáp án.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T02-S03

Timeline/probe raw, giới hạn tác động và bố trí giám sát; ghi rõ nếu run bị dừng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T02-S04

Bảng kết quả tái tính; không lọc failure hoặc sửa số để đạt ngưỡng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md -->


<!-- SOURCE: docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md -->

## Nguồn `docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md`

# R5-T03 — Chốt kỹ thuật và bàn giao cho Hòa

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R5](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Owner file sửa lỗi theo task con; Codex tổng hợp; Hoàng + Hòa nhận bàn giao
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-31
- **Due trong lịch nguồn:** 2026-10-31 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R5-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R5-T03-S01 | Sửa lỗi cốt lõi phát hiện trong pilot và chạy lại phép thử bị ảnh hưởng. | 2026-10-31 | 2026-10-31 | TODO |
| R5-T03-S02 | Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ. | 2026-10-31 | 2026-10-31 | TODO |
| R5-T03-S03 | Bàn giao sơ đồ, protocol, câu hỏi/claim, bảng/plot và giới hạn kết quả cho Hòa. | 2026-10-31 | 2026-10-31 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R5-T03-S01

Danh sách lỗi, bản sửa và kết quả kiểm chứng; nếu chưa qua, gate G5 chưa đóng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T03-S02

Phiên bản dựng lại được; dataset manifest có method version/hash/run IDs, legacy/pilot/formal tách riêng; analysis đọc danh sách dữ liệu đã khóa thay vì gộp mọi CSV. Run lỗi/loại khỏi phân tích có lý do theo protocol, vẫn được lưu và thống kê.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R5-T03-S03

Ma trận RQ → cấu hình → metric → claim khớp log/code; source ledger/path tra được, phân biệt lịch sử với bằng chứng mới. Giữ vấn đề/KPI chưa đạt và ghi kết quả xử lý H01–H08 còn mở.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md -->


<!-- SOURCE: docs/recovery/phases/R5-integration/README.md -->

## Nguồn `docs/recovery/phases/R5-integration/README.md`

# R5 — Tích hợp và pilot

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-29 → 2026-10-31, due 21:00 Asia/Saigon.

**Gate G5:** Core/phép đo qua kiểm chứng; có dataset pilot/runbook và protocol đối chứng đã khóa. KPI chưa đạt phải giữ kết quả và mở task sửa; chưa coi nghiên cứu hoàn tất.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R5-T01 — Chạy đầy đủ đường tấn công–phát hiện–hồi phục](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T01-end-to-end-pipeline.md)
- [R5-T02 — Pilot, khóa protocol và War Game](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T02-pilot-and-war-game.md)
- [R5-T03 — Chốt kỹ thuật và bàn giao cho Hòa](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R5-integration/README.md -->


<!-- SOURCE: docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md -->

## Nguồn `docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md`

# R6-T01 — Chuẩn bị bài báo trong lúc hoàn thiện kỹ thuật

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hòa chủ trì; Hoàng duyệt kỹ thuật; Codex hỗ trợ source/đối chiếu
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-10-18
- **Due trong lịch nguồn:** 2026-10-29 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R0-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T01-scope-and-criteria.md) (subtask trong file), [R0-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R0-foundations/R0-T04-research-questions.md) (subtask trong file).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R6-T01-S01 | Lập introduction/method quanh RQ1–RQ3 và bỏ khẳng định kết quả cũ chưa kiểm chứng. | 2026-10-18 | 2026-10-21 | TODO |
| R6-T01-S02 | Đối chiếu tài liệu gốc, gồm AIOpsLab/ITBench; chốt đóng góp và giới hạn tính mới. | 2026-10-19 | 2026-10-24 | TODO |
| R6-T01-S03 | Chốt kỷ yếu/đợt nhận bài, template, hạn và điều kiện chấp nhận đăng với thầy. | 2026-10-18 | 2026-10-24 | TODO |
| R6-T01-S04 | Hoàn thiện sơ đồ và mô tả phương pháp theo triển khai thực tế. | 2026-10-28 | 2026-10-29 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R6-T01-S01

Outline tách tuân thủ thuyết minh với giá trị LLM/phối hợp; RQ2 có điều kiện B3. Bỏ claim RAM/ưu thế chưa đo và động cơ/lời chấp thuận thiếu nguồn; không biến plan/ghi chú thành runtime hoặc kết quả.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T01-S02

Ma trận công trình → phương pháp → đối chứng → giới hạn → khác biệt; đọc nguồn liên quan đủ sâu, không lấy ghép công nghệ làm điểm mới.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T01-S03

Thông báo/đầu mối nhận bài xác định; đây là hạn nội bộ, không tự đặt lịch của trường.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T01-S04

Method/architecture khớp phiên bản đang triển khai; kết quả chưa có được để trống có chú thích.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md -->


<!-- SOURCE: docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md -->

## Nguồn `docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md`

# R6-T02 — Thực nghiệm chính thức và khóa dữ liệu

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hoàng chủ trì thực nghiệm; Codex hỗ trợ chạy/phân tích; Claude review; Hòa tổng hợp
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-11-01
- **Due trong lịch nguồn:** 2026-11-08 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R5-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R6-T02-S01 | Kiểm tra gate, protocol, nhãn không lộ đáp án và các lỗi/KPI chưa đạt trước formal run. | 2026-11-01 | 2026-11-01 | TODO |
| R6-T02-S02 | Chạy đủ số lặp B0/B1/B2/BM và B3 nếu giữ claim RQ2, kể cả manual có thao tác thật. | 2026-11-01 | 2026-11-06 | TODO |
| R6-T02-S03 | Phân tích tỷ lệ phục hồi, action đúng/sai/thừa, KPI, độ bất định và overhead/cost theo RQ. | 2026-11-06 | 2026-11-07 | TODO |
| R6-T02-S04 | Khóa dataset và đối chiếu từng claim với RQ, nhóm đo và phạm vi kết luận. | 2026-11-07 | 2026-11-08 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R6-T02-S01

G5 PASS, protocol khóa theo R5-T02-S02 (mục tiêu điều chỉnh 30/10) và checklist đo hợp lệ; thiếu core/phép đo/đối chứng cần thiết thì BLOCKED, sửa và cập nhật lịch.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T02-S02

Raw run/failure, seed/fault/tải tương ứng và thứ tự xen kẽ; reset có xác nhận, cùng version/evidence/budget, không chỉnh rules/prompt theo case formal.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T02-S03

Bảng/plot cùng mẫu số; báo AI thực/fallback, failure/timeout, độ đúng trước guard; B2/B3 chỉ kết luận nếu đã đo, không chọn riêng case AI thắng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T02-S04

Hash/version và ma trận claim → RQ/cấu hình/metric/trace; bỏ claim ưu thế phối hợp nếu thiếu B3, phân tích trung thực khi AI không tốt hơn rules.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md -->


<!-- SOURCE: docs/recovery/phases/R6-paper/R6-T03-paper-submission.md -->

## Nguồn `docs/recovery/phases/R6-paper/R6-T03-paper-submission.md`

# R6-T03 — Hoàn thiện và nộp bản paper đầu

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hòa chủ trì; Hoàng kiểm chứng và duyệt bản nộp; Codex/Claude review theo phạm vi
- **Reviewer đề xuất trong snapshot:** Codex; Hoàng/Hòa chốt phần nghiên cứu hoặc hồ sơ
- **Bắt đầu trong lịch nguồn:** 2026-11-09
- **Due trong lịch nguồn:** 2026-11-14 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R6-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md), [R6-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R6-T03-S01 | Viết results/discussion/limitations trả lời RQ từ dữ liệu đã khóa. | 2026-11-09 | 2026-11-10 | TODO |
| R6-T03-S02 | Hai người rà số liệu, đối chứng, claim tính mới/giá trị AI và xin góp ý thầy. | 2026-11-11 | 2026-11-12 | TODO |
| R6-T03-S03 | Soát template, hình/bảng, trích dẫn và hồ sơ nộp. | 2026-11-12 | 2026-11-13 | TODO |
| R6-T03-S04 | Nộp khi có đợt nhận bài hợp lệ và lưu biên nhận. | 2026-11-14 | 2026-11-14 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R6-T03-S01

Paper chỉ kết luận phần đã đo; báo lợi ích và đánh đổi, trường hợp rules tốt hơn, giới hạn mẫu/lab/fixture/model và mức độ mới đã đối chiếu.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T03-S02

Checklist claim–evidence, fairness/answer leakage và nguồn gốc tài liệu; xử lý góp ý hoặc ghi rõ còn chờ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T03-S03

Bản nộp đáp ứng hướng dẫn của nơi nhận bài đã xác định.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R6-T03-S04

Biên nhận/mã bài và bản đã nộp. 14/11 là mục tiêu nội bộ; nếu call không phù hợp phải cập nhật lịch.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R6-paper/R6-T03-paper-submission.md -->


<!-- SOURCE: docs/recovery/phases/R6-paper/README.md -->

## Nguồn `docs/recovery/phases/R6-paper/README.md`

# R6 — Thực nghiệm và bài báo

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-10-18 → 2026-11-14, due 21:00 Asia/Saigon.

**Gate G6:** Có dataset đủ protocol, paper trả lời RQ và claim khớp đối chứng đã đo, cùng biên nhận nộp đúng nơi. Biên nhận chưa phải chấp nhận đăng.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R6-T01 — Chuẩn bị bài báo trong lúc hoàn thiện kỹ thuật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T01-paper-preparation.md)
- [R6-T02 — Thực nghiệm chính thức và khóa dữ liệu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md)
- [R6-T03 — Hoàn thiện và nộp bản paper đầu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T03-paper-submission.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R6-paper/README.md -->


<!-- SOURCE: docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md -->

## Nguồn `docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md`

# R7-T01 — Theo dõi bài và xử lý phản biện

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R7](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hòa theo dõi; Hoàng sửa kỹ thuật/đo bổ sung; Codex/Claude hỗ trợ theo task
- **Reviewer đề xuất trong snapshot:** Hoàng + Hòa; agent còn lại đối chiếu theo phạm vi
- **Bắt đầu trong lịch nguồn:** 2026-11-15
- **Due trong lịch nguồn:** 2026-12-10 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R6-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T03-paper-submission.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R7-T01-S01 | Theo dõi tình trạng bài, lập bảng phản biện → việc sửa → bằng chứng. | 2026-11-15 | 2026-11-21 | TODO |
| R7-T01-S02 | Xử lý vòng phản biện đầu nếu đã nhận; phản hồi trong 3 ngày làm việc. | 2026-11-22 | 2026-11-28 | TODO |
| R7-T01-S03 | Xử lý vòng tiếp theo nếu có, bổ sung phép đo khi reviewer yêu cầu. | 2026-11-29 | 2026-12-05 | TODO |
| R7-T01-S04 | Đạt mốc mục tiêu có xác nhận chấp nhận đăng. | 2026-12-06 | 2026-12-10 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R7-T01-S01

Trạng thái bài và response matrix; tiếp tục rà ngày 28/11 và 05/12 khi đang chờ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T01-S02

Bản sửa/response có đối chiếu; chờ ý kiến thì WAIT_EXTERNAL. Ngày thực tế được tính lại theo ngày nhận.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T01-S03

Response và dữ liệu bổ sung; nếu đã chấp nhận không yêu cầu vòng này thì dùng xác nhận đó để đóng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T01-S04

Thông báo/văn bản chấp nhận đăng lưu được; mốc 10/12 phụ thuộc đơn vị xét bài, không phải cam kết.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md -->


<!-- SOURCE: docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md -->

## Nguồn `docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md`

# R7-T02 — Hoàn thiện Word và các sản phẩm nghiệm thu

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R7](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hòa chủ trì Word; Hoàng phụ trách demo/source/data; Codex/Claude review bằng chứng
- **Reviewer đề xuất trong snapshot:** Hoàng + Hòa; agent còn lại đối chiếu theo phạm vi
- **Bắt đầu trong lịch nguồn:** 2026-11-15
- **Due trong lịch nguồn:** 2026-12-18 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R5-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R5-integration/R5-T03-technical-handoff.md), [R6-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/R6-T02-formal-experiments.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R7-T02-S01 | Viết báo cáo Word bằng phương pháp và dữ liệu mới đã kiểm chứng. | 2026-11-15 | 2026-12-10 | TODO |
| R7-T02-S02 | Chuẩn bị video demo, slide/poster theo danh mục sản phẩm phải nộp. | 2026-11-22 | 2026-12-12 | TODO |
| R7-T02-S03 | Đóng gói source, manifest, runbook, dataset và Word/PDF. | 2026-12-13 | 2026-12-16 | TODO |
| R7-T02-S04 | Đối chiếu chéo số liệu và sản phẩm giữa paper, Word, demo và dữ liệu. | 2026-12-17 | 2026-12-18 | TODO |
| R7-T02-S05 | Đối chiếu thời hạn hồ sơ với nguồn của trường/thầy trước khi nộp nghiệm thu. | 2026-11-15 | 2026-12-16 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R7-T02-S01

Báo cáo Word có yêu cầu → sản phẩm → kết quả, bảng/plot và giới hạn.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T02-S02

Demo trên phiên bản chốt; slide/poster khớp báo cáo và dữ liệu, không dùng số mô phỏng.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T02-S03

Danh mục bàn giao có version và hướng dẫn tái lập.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T02-S04

Hai người ký nhận checklist nội bộ; mọi sai khác được xử lý hoặc nêu rõ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T02-S05

Ghi riêng thời gian DOCX tháng 01–06 và hạn 31/12 Hoàng xác nhận; lưu hồ sơ/xác nhận có thẩm quyền khi có và điều kiện nghiệm thu liên quan. Thiếu nguồn thì ghi WAIT_EXTERNAL, owner và ảnh hưởng G7; không tự viết rằng đã có gia hạn. Việc này không chặn sửa kỹ thuật.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md -->


<!-- SOURCE: docs/recovery/phases/R7-acceptance/R7-T03-acceptance-submission.md -->

## Nguồn `docs/recovery/phases/R7-acceptance/R7-T03-acceptance-submission.md`

# R7-T03 — Nộp hồ sơ và thực hiện nghiệm thu

> **Bản nguồn để chuyển Linear, không là live board.** Xem [delivery tracking](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có Linear ID; live state NOT VERIFIED. Metadata và bảng subtask dưới đây là snapshot 17/10, không cập nhật như trạng thái sống.

[Phase R7](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

- **Trạng thái snapshot:** TODO
- **Owner đề xuất trong snapshot:** Hoàng + Hòa; lịch hội đồng do trường xác nhận
- **Reviewer đề xuất trong snapshot:** Hoàng + Hòa; agent còn lại đối chiếu theo phạm vi
- **Bắt đầu trong lịch nguồn:** 2026-12-19
- **Due trong lịch nguồn:** 2026-12-31 21:00, Asia/Saigon
- **Phụ thuộc nguồn, cần review trước khi tạo relation:** [R7-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md), [R7-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md).

## Phạm vi phiên này

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

Trước thực hiện, ghi base HEAD, dirty snapshot và thao tác/file được giao. Chỉ một bên ghi trong cùng checkout; bên còn lại review. [Quy trình cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md) áp dụng cho mọi task.

## Subtask

| ID | Công việc | Bắt đầu dự kiến | Due 21:00 | Trạng thái snapshot |
| --- | --- | --- | --- | --- |
| R7-T03-S01 | Chạy thử demo và tập báo cáo nghiệm thu. | 2026-12-19 | 2026-12-20 | TODO |
| R7-T03-S02 | Xác minh bằng chứng chấp nhận đăng rồi nộp bộ hồ sơ nghiệm thu. | 2026-12-21 | 2026-12-21 | TODO |
| R7-T03-S03 | Báo cáo hội đồng và xử lý yêu cầu chỉnh sửa theo lịch được xác nhận. | 2026-12-22 | 2026-12-30 | TODO |
| R7-T03-S04 | Đối chiếu kết quả nghiệm thu, sản phẩm còn thiếu và lưu hồ sơ cuối. | 2026-12-30 | 2026-12-31 | TODO |

## Tiêu chí nguồn để soạn AC và bằng chứng kỹ thuật

### R7-T03-S01

Buổi rehearsal, checklist lỗi và phương án phục hồi demo.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T03-S02

Biên nhận hồ sơ và bằng chứng chấp nhận đăng; nếu thiếu thì BLOCKED, không ghi đã đủ điều kiện.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T03-S03

Lịch/biên bản thực tế và các chỉnh sửa; khoảng này chỉ là dự phòng điều phối nội bộ.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

### R7-T03-S04

Hồ sơ/kết quả nghiệm thu thực tế; nếu còn nghĩa vụ bắt buộc chưa xong thì chưa đánh dấu hoàn tất.

- Bằng chứng / ngày hoàn tất thực tế: Chưa ghi nhận.

## Bàn giao cuối phiên

Chưa có bàn giao thực thi mới. Khi làm: ghi Linear ID + thời điểm truy xuất, base HEAD/dirty, file đổi, kiểm tra/kết quả, evidence, việc chưa đạt và next action. AC/status/assignee/due cập nhật ở Linear theo quyền đã giao; không sửa snapshot để tạo board thứ hai.

Ngày gốc và lịch sử điều chỉnh: [snapshot trước khi tách](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/archive/roadmap-before-split.md). Trạng thái/AC delivery hiện hành thuộc issue Linear sau khi liên kết đúng; file này giữ source và checkpoint kỹ thuật, không là bản sao live issue.

<!-- END SOURCE: docs/recovery/phases/R7-acceptance/R7-T03-acceptance-submission.md -->


<!-- SOURCE: docs/recovery/phases/R7-acceptance/README.md -->

## Nguồn `docs/recovery/phases/R7-acceptance/README.md`

# R7 — Phản biện và nghiệm thu

> **Đặc tả milestone dự kiến.** Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/linear/README.md). Chưa có milestone ID; lịch và gate verdict dưới đây là snapshot, không là live status.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

**Cửa sổ trong lịch nguồn:** 2026-11-15 → 2026-12-31, due 21:00 Asia/Saigon.

**Gate G7:** Có bằng chứng chấp nhận đăng, đủ sản phẩm cam kết và hồ sơ/kết quả nghiệm thu theo lịch trường trước 31/12; các mốc bên ngoài cần xác nhận.

**Gate snapshot:** chưa đánh giá; chưa có kết quả PASS mới. Sau liên kết, milestone/issue Linear giữ acceptance/status delivery; repo giữ yêu cầu gate và evidence.

## Task

- [R7-T01 — Theo dõi bài và xử lý phản biện](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/R7-T01-peer-review.md)
- [R7-T02 — Hoàn thiện Word và các sản phẩm nghiệm thu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/R7-T02-report-and-deliverables.md)
- [R7-T03 — Nộp hồ sơ và thực hiện nghiệm thu](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/R7-T03-acceptance-submission.md)

## Khi kết thúc phase

Đối chiếu mọi task bắt buộc và bằng chứng với gate trên. Ghi báo cáo PASS/FAIL, ngày thực tế và evidence ở repo rồi liên kết từ milestone/issue Linear; verdict delivery và ảnh hưởng lịch cập nhật trên Linear theo quyền. Gate đạt không tự chứng minh mọi KPI nghiên cứu hoặc paper đã được chấp nhận.

<!-- END SOURCE: docs/recovery/phases/R7-acceptance/README.md -->


<!-- SOURCE: docs/recovery/reference/ai-provider.md -->

## Nguồn `docs/recovery/reference/ai-provider.md`

# Vai trò AI và lựa chọn provider

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

Đây là thiết kế/đề xuất đã chuyển từ roadmap 17/10, chưa phải xác nhận provider đang hoạt động. Thông tin model, quyền và chi phí phải xác minh lại khi chọn backend. Claude Code là công cụ phát triển, không mặc định là backend runtime.

## Quyết định về AI và provider

Một agent cần quan sát, giữ trạng thái mục tiêu, chọn hành động, dùng công cụ và kiểm tra kết quả. Một endpoint gọi LLM rồi trả JSON chưa đủ chứng minh vòng lặp tự trị; giao diện chat diễn giải sự kiện cũng không tự trở thành ba agent AI.

| Tác tử | Hành vi cần hoàn thành | Vai trò LLM | Phần mã kiểm soát |
| --- | --- | --- | --- |
| Nemesis | Chọn kịch bản từ trạng thái lab, thực thi, đọc kết quả và quyết định lượt tiếp theo trong phiên giới hạn | Chọn vector/intensity, sinh biến thể SQLi theo mẫu sandbox và giải thích ngắn bằng dữ kiện | Target allowlist, payload schema, request/duration/concurrency budget, start/stop và worker thực thi |
| Gaia | Thu metrics/log/probe, phát hiện sự cố và phân tích nguyên nhân có bằng chứng | Phân loại sự cố, đối chiếu log/metrics gần nhất, trả anomaly/evidence/confidence có cấu trúc | Threshold/signature/probe phát hiện nhanh, timestamp, IP nguồn, dedup; không chờ LLM mới ghi mốc phát hiện |
| Hephaestus | Chọn hành động theo sự cố và trạng thái deploy, thực thi, kiểm tra hồi phục và ghi kết quả | Xếp hạng/chọn action trong enum được phép, dùng evidence và release history | Policy gate, invariants, cooldown, hạn số lần chữa, thao tác K8s/gateway, xác nhận readiness và giao dịch nghiệp vụ |

Ba tác tử có trạng thái, nhiệm vụ và hợp đồng dữ liệu riêng; có thể dùng chung một model/API. Không cần tải ba model cùng lúc. LLM không được sinh và thực thi lệnh shell tùy ý hoặc tự sửa mã ứng dụng trong luồng chữa lỗi.

Sự cố cần phản ứng nhanh được bộ phát hiện ghi nhận ngay. Inference có timeout và retry giới hạn. Khi LLM không khả dụng, chế độ suy giảm dùng policy đã khai báo; raw event và dataset phải đánh dấu đã fallback. Một lượt không gọi được model không được ghi như lượt AI đầy đủ. Đo riêng latency inference và overhead quyết định để kiểm tra ảnh hưởng lên KPI.

**Provider đề xuất:** API là backend chính cho thực nghiệm, nhằm tránh inference trên cùng máy làm nhiễu tài nguyên của cluster. Chọn model nhỏ có structured output sau khi xác nhận endpoint/quota và một lượt test thật. Không chốt tên model từ manifest cũ, không tự nâng subscription, không tự tạo VM/GPU hoặc dịch vụ mất phí trong lượt lập kế hoạch.

**Ollama bổ sung:** nếu API chưa sẵn sàng, thử duy nhất một ứng viên nhỏ, chẳng hạn [qwen2.5:3b Q4_K_M](https://ollama.com/library/qwen2.5:3b), trước khi triển khai nhiều lựa chọn. Trang model ghi khoảng 1,9 GB weights, không phải tổng RAM/VRAM vận hành. Đặt context nhỏ cho telemetry đã tóm tắt và đo thực tế cùng lab; chỉ dùng nếu latency và memory không làm hỏng phép đo. Ollama hỗ trợ [JSON schema/structured outputs](https://docs.ollama.com/capabilities/structured-outputs); [context dài làm tăng bộ nhớ](https://docs.ollama.com/context-length). Chưa có benchmark để hứa model này đáp ứng KPI hoặc chất lượng phân loại.

Chỉ cần interface thay provider, không bắt buộc vận hành hai backend trong tháng 10. Khi đo chính thức, khóa provider/model/version/prompt; không chuyển provider âm thầm giữa các lượt. Thực nghiệm cloud/local song song và so sánh model là phần hoãn nếu làm trễ nghiệm thu.

Microsoft xác nhận [Azure for Students có credit 100 USD trong 12 tháng nhưng không áp dụng cho Marketplace offers](https://learn.microsoft.com/en-us/azure/education-hub/faq). Quyền model/quota còn phụ thuộc subscription/deployment. Trước khi dùng API Azure, kiểm tra eligibility, billing và giới hạn cụ thể; không mặc định mọi model đều dùng được credit. Đề xuất giới hạn thử nghiệm LLM ban đầu 10 USD từ credit, chỉ khi được xác nhận phương án; code có max calls, token budget, timeout và tracking usage. Budget alert của cloud không thay cho giới hạn request trong ứng dụng; chưa phát sinh chi phí trong kế hoạch này.

<!-- END SOURCE: docs/recovery/reference/ai-provider.md -->


<!-- SOURCE: docs/recovery/reference/audit-findings.md -->

## Nguồn `docs/recovery/reference/audit-findings.md`

# Audit, bàn giao và các đính chính

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

Bối cảnh đối chiếu tại 17/10/2026. Bảng H01–H08 bên dưới giữ ngày ở snapshot để truy vết; lịch/trạng thái delivery hiện hành tra Linear khi đã xác minh đúng project, không cập nhật tiến độ trong tài liệu tham khảo này. Đường dẫn roadmap cũ trong trao đổi được thay bằng index Recovery.

## Tiếp nhận bàn giao Antigravity và thứ tự xử lý

[Bản bàn giao Gemini](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md) cung cấp bối cảnh kỹ thuật; [review H01–H08](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-antigravity-handoff-review.md) xác định phần đã đối chiếu và phần còn thiếu nguồn. Roadmap dùng xác nhận trực tiếp của Hoàng cho quyết định hiện tại, mã/dataset cho hành vi được kiểm tra, log thực thi cho runtime. Kế hoạch, checkpoint và hồi tưởng không thay những loại bằng chứng này.

### Tiếp nhận Claude và các đính chính ngày 17/10

[Hydration và review E6](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-handoff.md:345), [phản hồi D8](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-d8.md) và [blockers đã kiểm tra](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-session-blockers.md:93) kết thúc bước tiếp nhận: Claude đủ nắm bối cảnh để nhận task hẹp; không cần hydration lại. Điểm 19/20 không phải phần trăm hoàn thành dự án. Đây là rà soát trọng yếu dựa trên source/dữ liệu, chưa kiểm chứng mọi trao đổi cũ của Gemini hay toàn bộ hành vi runtime.

| Điểm mới/đính chính | Task áp dụng | Yêu cầu khi thực hiện |
| --- | --- | --- |
| C01 — K3s có controller NetworkPolicy nhúng; Flannel không tự suy ra bỏ policy | R0-T02-S01; R3-T02-S01/S02 | Kiểm phiên bản/args/controller, selector và đường IP thật; đo attacker bị chặn và benign vẫn hoạt động. Chưa có căn cứ thay CNI hoặc recreate cluster. Runtime enforce còn UNKNOWN. |
| C02 — duration trong command không bảo đảm thời gian hoặc tác động thực thi | R1-T04-S01; R2-T02; R2-T03 | Kiểm theo executor; POD_KILL không chạy suốt duration. Giới hạn của command phải bị chặn bởi trần vận hành; EffectiveDuration đang ưu tiên maxDuration của lệnh khi >0, cần test. GET healthz dùng kiểm sức khỏe; không POST attack làm health check. |
| C03 — runner reset, endpoint reset và TTL là ba đường khác nhau | R0-T02-S02; R2-T02-S03; R2-T03-S02; R3-T02-S02; R5 | Runner có lệnh xóa policy theo nhãn nhưng chưa kiểm return code; endpoint không xóa policy; TTL timer mất khi healer restart. Pod stress thử cleanup nhưng lỗi vẫn có thể báo SUCCESS. Xác nhận hậu điều kiện cleanup trước run tiếp. Codex rút lại nhận xét runner không có lệnh xóa policy. |
| C04 — provenance DOCX, graph và CSV phải tách đúng | R0-T01-S03; R5-T03-S02; R6 | Bản trích DOCX có hash/đoạn, không gán thành Claude trực tiếp đọc. CSV ghi ngày 25/06; Git nhập 25/06, thêm/xóa file thử 12–13/07. GitNexus query/context dùng được; status chậm không chứng minh graph hỏng. |
| C05 — owner/file và phụ thuộc của thiết kế khác runtime | R1-T01-S01; mọi task mã | Claude Code là cộng tác viên phát triển, không phải lựa chọn Claude API. Khóa schema trước sửa producer/consumer; bản nháp không chờ lab/LLM. Mỗi file có một owner trong lượt; chốt cả đường dẫn test/probe trước triển khai. |

**Snapshot điều phối 17/10:** `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`; trước cập nhật roadmap có bốn file handoff ngày 17/10 untracked, mã tracked không đổi. GitNexus index `6337b31` chậm một commit chỉ gồm docs/chỉ dẫn/cấu hình; dùng graph để định vị rồi đọc source hiện tại. Chưa lấy inventory Docker/K8s mới, chưa chạy lab, model hoặc thực nghiệm mới. Ghi chú Complete tháng 7 và snapshot 09/10 dưới đây là lịch sử, không thay trạng thái hiện tại.

**Bảo toàn tài liệu khi công cụ gián đoạn:** task nhỏ, lưu/đọc lại từng phần; không thay tiêu đề bảo vệ bằng một khối dài. Khi Claude bị classifier chặn, ghi thao tác và phần đã lưu, không retry liên tục hoặc sửa quyền rộng để bỏ qua. Dùng bản trích đúng phạm vi cho DOCX. GitNexus status chậm thì đọc MCP context hoặc meta/HEAD/diff và dirty files; không clean index/xóa lock của tiến trình khác. Các cách này giảm mất dữ liệu, không bảo đảm hết chặn từ nhà cung cấp.

### Các phát hiện H01–H08 và lịch điều chỉnh

| Phát hiện | Task tiếp nhận/xử lý | Due gốc 21:00 | Due điều chỉnh 21:00 (Asia/Saigon) | Điều kiện đóng liên quan |
| --- | --- | --- | --- | --- |
| H01 — Lý do và lời chấp thuận thiếu chat gốc | R0-T01-S03; R6-T01-S01 | 2026-10-10; 2026-10-14 | 2026-10-18; 2026-10-21 | Source ledger phân biệt chat gốc/nhớ lại/suy luận; không gán động cơ hoặc lời duyệt cho Hoàng từ code/commit. Thiếu chat được giữ UNKNOWN, không chặn sửa kỹ thuật. |
| H02 — Nguồn thời hạn khác nhau | R0-T01-S03; R7-T02-S05 | 2026-10-10; 2026-12-16 | 2026-10-18; 2026-12-16 | Ghi riêng tháng 01–06 trong DOCX và 31/12 do Hoàng xác nhận; hồ sơ cuối có kết quả đối chiếu và nguồn có thẩm quyền hoặc rủi ro đang chờ xác nhận. |
| H03 — Sai inventory/timeline dữ liệu | R0-T01-S03; R5-T03-S02 | 2026-10-10; 2026-10-31 | 2026-10-18; 2026-10-31 | Inventory đúng 8 CSV/40 dòng, 5 lượt/file; timestamp attack_start ghi 25/06/2026 tách khỏi ngày nhập Git/phân tích. Legacy không được trộn vào pilot/formal mới. |
| H04 — Mốc MTTR và terminal status không chứng minh recovery | R1-T01; R1-T02; R3-T01-S01 | 2026-10-13; 2026-10-15; 2026-10-17 | 2026-10-20; 2026-10-22; 2026-10-23 | Detect do detector ghi, recovery do probe xác nhận; FAILED/PARTIAL không tự tạo MTTR thành công; timeout/missing/failure có mẫu số và giới hạn quan sát rõ. |
| H05 — Runtime suy từ plan/ghi chú | R0-T01-S03; R0-T02-S03; R0-T03-S02 | 2026-10-10; 2026-10-12; 2026-10-11 | 2026-10-18; 2026-10-19; 2026-10-20 | Phân biệt báo cáo tự đánh giá với log thực thi; có evidence lab/model mới để đóng gate. Cloud tắt ghi theo Hoàng, không tự xác nhận thao tác/tài nguyên/ngày tắt cụ thể. |
| H06 — Sai hướng dẫn phục hồi cluster | R0-T02-S01; R0-T02-S02 | 2026-10-10; 2026-10-11 | 2026-10-18; 2026-10-19 | Inventory quyết định start hay recreate; lệnh/script dựng cluster được kiểm tra đúng chức năng. rebuild-nemesis.ps1 chỉ build/import/rollout Nemesis, không dùng thay bước tạo cluster. |
| H07 — Claim tài nguyên/ưu thế chưa có đối chứng | R0-T04-S01; R4-T04; R6-T01-S01; R6-T02-S04 | 2026-10-10; 2026-10-25; 2026-10-14; 2026-11-08 | 2026-10-18; 2026-10-29; 2026-10-21; 2026-11-08 | Giữ RAM <100MB, giảm 88%, tổng 157MB và nhận xét vượt AIOps ở mức claim cũ chưa xác minh; bỏ khỏi kết luận nếu không đo. Claim lợi ích chia vai trò cần B3; không mở benchmark RAM bắt buộc chỉ để giữ claim cũ. |
| H08 — Path, danh tính và nguồn chưa chuẩn hóa | R0-T01-S03; R5-T03-S03 | 2026-10-10; 2026-10-31 | 2026-10-18; 2026-10-31 | Dùng path thật, nguồn IDE có đường dẫn/loại nguồn; không suy hp8001 là Hòa. Thông tin nơi nhận bài vẫn chốt tại R6-T01-S03, không hỏi lại như blocker tiếp nhận. |

**Thứ tự bắt đầu:** chụp baseline/source ledger và preflight lab → khóa event/probe/phép đo → kiểm chứng vector và healer → tích hợp LLM → pilot đối chứng → formal dataset và paper. Chỉ các mô tả kỹ thuật đã đối chiếu được dùng làm đầu vào sửa; lịch sử chưa xác minh không quyết định thiết kế hoặc trách nhiệm cá nhân.

**Dataset cũ:** review ghi nhận 8 CSV với 40 dòng, trong đó E3 AUTO có 4/5 lượt FAILED nhưng vẫn mang MTTR khoảng 1,01–1,02s. Điều này minh họa lỗi phương pháp, chưa xác định nguyên nhân runtime của từng thất bại. Không diễn giải khoảng 1s là latency K8s API hoặc tốc độ hồi phục nghiệp vụ; 9,24s là P95 MTTD E3 AUTO trong summary, không phải max 11,26s trong raw. Giữ nguyên dữ liệu, hình và báo cáo cũ để truy vết; bản viết mới phải nêu giới hạn và dùng dataset mới hợp lệ.

## Snapshot kiểm tra ngày 09/10/2026 và giới hạn xác nhận

Mã ứng dụng tại HEAD `6337b319b075bf389d484a6be13a4bc094f94a82` chưa được sửa trong lượt này. Metadata GitNexus có cùng commit, 96 files, 1.409 nodes, 44 processes; dùng graph để xác định hàm LLM và đọc mã thật để xác nhận, không dùng graph làm bằng chứng vận hành.

- Máy: Intel i7-11800H, 8 cores/16 threads, RAM khoảng 15,8 GiB; GPU RTX 3050 Laptop, VRAM 4.096 MiB. Docker báo được cấp khoảng 6,77 GiB RAM, 4 CPU.
- Trong lần lập kế hoạch ban đầu, Docker daemon trả lời truy vấn thông tin; context Kubernetes là `k3d-zero-door`, API `127.0.0.1:58117` từ chối kết nối và truy vấn container tên `k3d-zero-door` không trả container. Lượt review handoff sau đó chưa lấy được snapshot lifecycle mới do truy vấn Docker lỗi quyền rồi treo và được ngắt. Các quan sát này không chứng minh container hiện exited hoặc cluster còn tồn tại; R0-T02-S01 phải lấy inventory mới. Chưa khởi động, tái tạo cluster hoặc xóa volume.
- Không thấy lệnh Ollama trên PATH; API localhost:11434 không trả lời. Chưa chứng minh có local inference server đang hoạt động ở endpoint khác.
- [Nemesis](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/nemesis/main.py:276) có mã gọi OpenAI-compatible API, Gemini và Ollama. [Manifest](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/nemesis-deployment.yaml:17) chọn Gemini, có cấu hình Ollama/OpenAI nhưng secret mẫu để trống. Không đọc được trạng thái Secret đang triển khai do cluster chưa kết nối; không thể kết luận từ manifest rằng trước đây chưa từng có API key.
- Chưa chạy một lượt gọi LLM, tải model, tạo tài nguyên Azure, chạy attack hoặc healing trong lượt này. Có mã tích hợp LLM không đồng nghĩa agent hiện hoạt động với LLM.

<!-- END SOURCE: docs/recovery/reference/audit-findings.md -->


<!-- SOURCE: docs/recovery/reference/checkpoints.md -->

## Nguồn `docs/recovery/reference/checkpoints.md`

# Mốc kiểm soát và xử lý lệch lịch

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Quy trình](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/WORKFLOW.md)

### Mốc quyết định khi có lệch lịch

| Mốc kiểm soát | Điều kiện phải kiểm tra | Cách xử lý khi chưa đạt |
| --- | --- | --- |
| 2026-10-18 — đầu ra khởi động | Có inventory/baseline hoặc lỗi chính xác; draft contract có nội dung | Nếu lab không truy cập, xác định phương án trước thay đổi. Draft vẫn làm được; không chờ LLM để đọc nguồn/thiết kế. Chưa đủ thông tin thì cập nhật dự báo G0/G1. |
| 2026-10-20 — G0 (gốc 12/10) | Lab và một backend LLM thật hoạt động, RQ/đối chứng/evidence được khóa | Sửa đầu vào, không thay mock rồi ghi AI đã chạy. Rules/đo đạc không phụ thuộc LLM vẫn tiếp tục; đường AI chờ backend thật. Không mở so sánh hai backend trong core. |
| 2026-10-23 — G1 (gốc 16/10) | Event/probe/metric, guard và cấu hình đối chứng qua kiểm chứng | Nếu chưa đạt, không tạo dataset chính thức bằng runner cũ; lập lại lịch G2–G5 và dự báo 31/10 ngay. |
| 2026-10-25 — G2 (gốc 19/10) | Đủ SQLi, DDoS L7 và resource exhaustion đúng mục tiêu | Giữ task còn thiếu trên đường găng, không thay SQLi bằng PodKill. Nếu trễ, mốc G4/G5 phải được dự báo lại; không dồn thêm giờ giả định. |
| 2026-10-27 — G3 (gốc 22/10) | Healer có tác động và recovery được probe xác nhận | Giữ lỗi hở thành BLOCKED cho đường thử cần healer đó; không tính API chấp nhận là thành công. |
| 2026-10-24 — đầu vào paper | Có nơi/đợt nhận bài và điều kiện đăng cụ thể | Hòa làm rõ với thầy, cập nhật mục tiêu nộp 14/11; tiếp tục kỹ thuật và phương pháp không phụ thuộc template. |
| 2026-10-29 — G4 (gốc 25/10) | Trace thật, pilot B0/B1/B2 và quyết định B3/claim RQ2 | Thiếu đối chứng tối thiểu thì chỉ chạy chẩn đoán sửa lỗi. Thiếu B3 thì bỏ claim ưu thế chia vai trò hoặc cập nhật lịch đo; không suy ưu thế từ việc có ba agent. |
| 2026-10-30 21:00 — sẵn sàng War Game | R5-T01 và pilot/protocol R5-T02-S01/S02 đủ bằng chứng, có người giám sát và budget | Chưa đủ thì không chạy cho kịp lịch bằng cách bỏ qua reset/probe/guard. Dời War Game, giữ G5 mở và cập nhật formal run/paper. Ngày 31/10 đang gộp đo dài, phân tích, sửa lỗi và bàn giao, không có dự phòng đã chứng minh. |
| 2026-10-31 — G5 | Core + phép đo + dataset pilot + runbook | Nếu core/phép đo lỗi: chưa đóng kỹ thuật. Nếu phép đo hợp lệ nhưng KPI fail: giữ kết quả, mở task cải thiện và dời formal run khi cần. |
| 2026-11-08 — khóa dataset | Đủ số lặp/nhóm theo protocol, không lộ đáp án, metric và claim tái tính được | Không lấp run thiếu hoặc chỉ chọn case AI thắng; bổ sung phép đo/giới hạn claim và cập nhật ảnh hưởng mốc nộp. |
| 2026-11-14 — G6 | Bản nộp đúng đợt và có biên nhận | Nếu đợt nhận bài chưa phù hợp, ghi WAIT_EXTERNAL và cập nhật theo lịch thật; không tự đổi nơi nộp. |
| 2026-12-10 — mục tiêu chấp nhận đăng | Có thông báo chấp nhận đăng | Nếu chưa có, review rủi ro với thầy vào 2026-12-12; xác nhận phương án và lịch có thẩm quyền, giữ blocker. |
| 2026-12-21 — hồ sơ nghiệm thu | Đủ sản phẩm và bằng chứng chấp nhận đăng | Thiếu chấp nhận đăng thì chưa đủ điều kiện theo thông tin người dùng; không ghi đã nộp hồ sơ hợp lệ. |
| 2026-12-31 — G7 | Kết quả/hồ sơ nghiệm thu thực tế, mọi tiêu chí/sản phẩm bắt buộc được đối chiếu | Nếu còn thiếu thì ghi chưa hoàn tất, nguyên nhân và việc tồn; không tự đóng vì hết hạn. |

Mốc này được chuyển từ lịch 17/10. Khi thay lịch delivery được phép, cập nhật metadata tại Linear và ghi provenance vào checkpoint nếu cần; không tiếp tục cập nhật lịch sống trong bản nguồn này; không tự dời hạn của trường hoặc ngày chấp nhận đăng.

<!-- END SOURCE: docs/recovery/reference/checkpoints.md -->


<!-- SOURCE: docs/recovery/reference/publication.md -->

## Nguồn `docs/recovery/reference/publication.md`

# Bàn giao báo cáo và bài báo

[Phase R6](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R6-paper/README.md) · [Phase R7](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/phases/R7-acceptance/README.md)

## Bàn giao cho Hòa và hướng bài báo

Hòa có thể bắt đầu sửa phần giới thiệu, kiến trúc, phạm vi và phương pháp ngay, nhưng không giữ các kết luận “MTTR 1,01s”, “uptime 100%”, “triệt tiêu CVE” từ bộ dữ liệu cũ. Hoàng bàn giao cho mỗi milestone: sơ đồ, định nghĩa metrics, config/commit, event mẫu, dữ liệu/biểu đồ, kết quả chưa đạt và giới hạn.

Bài báo dùng RQ1–RQ3 và ma trận đối chứng trong phần Giá trị nghiên cứu; Hòa nhận câu hỏi/giới hạn claim ở R0-T04, protocol chốt ở R5-T02-S02 và dữ liệu chính thức ở R6-T02. Mô tả kiến trúc ba tác tử tách khỏi claim chứng minh lợi ích chia vai trò; không có B3 thì không kết luận tốt hơn single-agent. Không hứa kết quả vượt trội hoặc đồng nhất phục hồi availability với vá mọi lỗ hổng/“không cửa hậu”.

Paper nên có introduction/related work, architecture/method, experimental setup, results, discussion/limitations và conclusion theo mẫu nơi nhận bài. Không biến sáu chương báo cáo thành paper bằng cách rút ngắn cơ học. Khi có kỷ yếu cụ thể, kiểm tra scope, độ dài, format, lịch và cách nộp trước bản gửi chính thức.

<!-- END SOURCE: docs/recovery/reference/publication.md -->


<!-- SOURCE: docs/recovery/reference/research-design.md -->

## Nguồn `docs/recovery/reference/research-design.md`

# Thiết kế nghiên cứu và đối chứng

[Phạm vi](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/SCOPE.md) · [Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

## Giá trị nghiên cứu và cách chứng minh

**Đánh giá trước thực nghiệm:** ZERO DOOR có tiềm năng làm đề tài ứng dụng, nhưng sửa cho đúng chức năng rồi trình diễn “gây lỗi → phát hiện → tự sửa” chưa đủ chứng minh giá trị nghiên cứu. Phần còn yếu là bằng chứng trả lời vì sao cần LLM và vì sao cần chia tác tử; đây là nhận xét về thiết kế đánh giá hiện tại, chưa phải kết luận đề tài yếu hoặc lời hứa bài sẽ được chấp nhận.

Cần theo dõi riêng hai điều kiện: **đáp ứng thuyết minh** bằng chức năng/KPI/sản phẩm đã cam kết, và **trả lời câu hỏi nghiên cứu** bằng đối chứng có thể tái lập. Hai điều kiện bổ sung cho nhau. Một kết quả AI không tốt hơn quy tắc vẫn có giá trị phân tích nếu thực nghiệm hợp lệ, nhưng không tự giải quyết các tiêu chí nghiệm thu còn thiếu.

### Công trình liên quan và đóng góp dự kiến

[AIOpsLab](https://arxiv.org/abs/2501.06706) mô tả môi trường microservices, fault injection, workload, telemetry và giao diện đánh giá agent vận hành. [ITBench](https://research.ibm.com/publications/itbench-evaluating-ai-agents-across-diverse-real-world-it-automation-tasks) đưa ra phương pháp benchmark agent cho tác vụ IT, gồm SRE. Đã đối chiếu mô tả/abstract từ nguồn gốc ngày 2026-10-09; chưa hoàn tất tổng quan toàn văn. Từ đó, nhận định làm việc là không lấy riêng việc ghép AI agent, Chaos Engineering và microservices làm bằng chứng điểm mới. R6-T01-S02 phải mở rộng đối chiếu tài liệu trước khi chốt claim.

Đóng góp hướng tới là **một cơ chế phối hợp tác tử với hành động có giới hạn, bằng chứng vận hành và xác minh hồi phục nghiệp vụ**, cùng dữ liệu đối chứng cho biết khi nào LLM hữu ích, khi nào quy tắc đủ tốt, và mức đánh đổi về latency/chi phí. Đây là đóng góp dự kiến; không dùng các từ “đầu tiên”, “vượt trội” hoặc “mới” khi chưa có căn cứ. Giữ Python/Go, Boutique và mọi cam kết ban đầu; ưu tiên chất lượng thực nghiệm thay vì thêm framework/model/cloud.

### Câu hỏi nghiên cứu và giới hạn kết luận

- **RQ1 — giá trị LLM:** với các sự cố có triệu chứng dễ nhầm lẫn, multi-agent dùng LLM có chọn hành động phục hồi phù hợp và phục hồi nghiệp vụ tốt hơn cơ chế quy tắc không? Mức đánh đổi về thời gian quyết định, latency hồi phục, token và chi phí là bao nhiêu?
- **RQ2 — giá trị chia vai trò:** việc tách phân tích sự cố và lựa chọn hành động có cải thiện kết quả so với một agent vận hành dùng cùng model, dữ liệu và công cụ không? Chỉ kết luận về lợi ích phối hợp khi đã chạy đối chứng tương ứng.
- **RQ3 — giới hạn vận hành:** cơ chế guard/fallback kiểm soát quyết định sai hoặc thiếu bằng chứng ra sao, và các tác động nào còn làm hỏng KPI hay traffic lành tính?

Giả thuyết cần kiểm tra là LLM có thể hữu ích hơn ở trường hợp cần kết hợp nhiều bằng chứng, trong khi quy tắc có thể nhanh/rẻ hơn ở trường hợp đơn giản. Khóa câu hỏi, metric chính và cách chấm trước formal run; không chọn lại giả thuyết hoặc bỏ case thất bại sau khi thấy kết quả. Không bắt buộc AI thắng để đóng task thực nghiệm; bắt buộc kết luận khớp dữ liệu và nêu độ bất định.

### Cấu hình đối chứng

| Mã | Cấu hình | Điều được kiểm tra |
| --- | --- | --- |
| B0 — K8S_BASELINE | Kubernetes và controller mặc định; profile HPA được ghi rõ; ZERO DOOR không phát lệnh heal | Hạ tầng tự phục hồi được đến đâu |
| B1 — RULES | Bộ phát hiện/evidence và policy quy tắc, cùng executor/healer/guard/probe với B2 | Giá trị của cách đơn giản hơn; rules được hiệu chỉnh bằng pilot rồi khóa |
| B2 — MULTI_LLM | Gaia phân tích, Hephaestus chọn hành động bằng LLM trong giới hạn chung | Giá trị thêm của LLM so với B1 và B0 |
| B3 — SINGLE_LLM | Một agent vận hành gộp phân tích và lựa chọn hành động; cùng model, evidence, tools và giới hạn như B2 | Bắt buộc nếu claim rằng chia vai trò giúp cải thiện kết quả; có thể bỏ claim này nếu không đủ nguồn lực |
| BM — MANUAL | Người vận hành xử lý thật, giữ log thao tác; ZERO DOOR không tự chữa | Giữ theo protocol/cam kết hiện có và khi kết luận nhanh/tốt hơn thủ công |

B0/B1/B2 là đối chứng tối thiểu của câu hỏi chính. BM vẫn nằm trong kế hoạch formal hiện có; không xóa đối chứng hoặc cam kết ban đầu để nhường chỗ cho B3. Nếu B3 không thực hiện, vẫn xây kiến trúc ba tác tử theo thuyết minh nhưng chỉ mô tả cách phối hợp, không khẳng định kiến trúc nhiều tác tử tốt hơn một tác tử.

Trong phép so sánh phục hồi, **Nemesis/chaos harness dùng kế hoạch tải/fault đã khóa, được phát lại giống nhau cho mọi cấu hình**. Không cho B2 tự chọn sự cố dễ hơn nhóm khác. Khả năng chọn kịch bản thích nghi của Nemesis được kiểm chứng chức năng riêng; chưa suy ra giá trị của khả năng đó từ benchmark phục hồi. B3 so sánh cách chia vai trò vận hành Gaia/Hephaestus, không tự chứng minh lợi ích của toàn bộ ba tác tử hoặc riêng Nemesis.

### Case dễ nhầm lẫn và ngăn lộ đáp án

| Case | Triệu chứng/bằng chứng cần quan sát | Cách chấm được khóa trước chạy |
| --- | --- | --- |
| C0 — tải lành tính ổn định | Giao dịch bình thường, không có sự cố | Không can thiệp thừa; đo false alarm và false action |
| C1 — lượng khách hợp lệ tăng | CPU/latency tăng, mẫu request và lịch deploy bình thường | Scale hoặc không can thiệp theo điều kiện case; không chặn khách hợp lệ |
| C2 — DDoS L7 | Có thể cùng CPU/latency cao như C1; pattern nguồn/request khác | Hành động containment/scale thuộc tập phù hợp đã định; kiểm tra traffic benign |
| C3 — phiên bản lỗi | Error/latency tăng sau thay đổi release; lịch deploy và log lỗi | Rollback về release tốt hoặc tập hành động phù hợp đã định; không suy rollback từ mọi 5xx |
| C4 — resource exhaustion | Tài nguyên mục tiêu/throttling/sức khỏe dịch vụ suy giảm | Hành động phù hợp phải được probe xác minh, phân biệt thiếu capacity với nguyên nhân khác |
| C5 — SQLi trên fixture | Request/log/query bất thường tại fixture riêng | Chấm containment trên fixture; availability mua hàng Boutique báo riêng |

C0/C1 là đối chứng lành tính; C3 là case rollback đã có trong kế hoạch. Chúng bổ sung thiết kế đánh giá, không thay ba vector SQLi/DDoS/resource đã đăng ký. Chọn các mức tải để triệu chứng có thể chồng lấp nhưng phải xác minh nguyên nhân thật; không giả tạo metric giống nhau bằng dữ liệu mô phỏng.

Harness giữ **ground truth** gồm nguyên nhân, thời điểm fault và tập hành động chấp nhận được cho mỗi case; Hoàng/Hòa rà tập này trước formal run. Gaia/Hephaestus/single-agent chỉ nhận telemetry và lịch sử vận hành theo quyền vai trò. Không đưa tên case, loại attack từ command, đáp án hoặc gợi ý “hãy rollback” vào prompt/alert của bên chữa lỗi; dùng ID trung tính. Giữ bằng chứng vận hành thật như release history, log request và IP quan sát được, không che dấu vết cần để chẩn đoán. Dữ liệu ground truth và log điều khiển Nemesis/worker phải được tách khỏi nguồn truy vấn dành cho bên chữa lỗi.

### Metric, công bằng thực nghiệm và bằng chứng để viết bài

- Giữ MTTD/MTTR/uptime và ngưỡng gốc; thêm **tỷ lệ phục hồi được probe nghiệp vụ xác nhận trên tổng lượt sự cố**. Failure/timeout vẫn nằm trong mẫu số; MTTR của lượt thành công phải báo cùng tỷ lệ thất bại, không dùng trung bình đã bỏ failure để tuyên bố tốt hơn.
- Đo **độ đúng của hành động đầu tiên** so với tập hành động chấp nhận được đã khóa trên tổng lượt case yêu cầu quyết định; sai schema/không phản hồi sau trigger/timeout vẫn được tính là lượt không có quyết định đúng, không tự gán thành NO_ACTION. Đo riêng hành động thừa ở C0/C1 và đề xuất bị guard từ chối. Ghi đề xuất trước guard, action thực thi và kết quả; guard chặn sai không biến quyết định sai thành đúng. NO_ACTION/ABSTAIN chỉ đúng khi case cho phép, với quy ước ghi nhận được khóa trước chạy.
- Đo decision latency, số call/token, retry/fallback và chi phí theo run, có breakdown theo tác tử; ghi nguồn/ngày đơn giá khi tính tiền. Chi phí tạo kế hoạch Nemesis/harness dùng chung được ghi riêng với chi phí quyết định phục hồi để tránh quy sai overhead giữa B0/B1/B2/B3. Tách quyết định AI thật với fallback RULES; không gộp rồi gán toàn bộ lợi ích cho LLM.
- Giữ workload, fault intensity/duration, image/config, probe, executor, action budget và profile HPA tương đương giữa các nhóm; replay cùng case/seed, reset có xác nhận và xen kẽ thứ tự chạy. Giữ riêng biến thể dùng phát triển/pilot với biến thể đánh giá; khóa rules/prompt/model trước formal run.
- Với B3, giữ cùng evidence, công cụ và trần tài nguyên; ghi chênh lệch số lần gọi/token thực tế thay vì ép số call bằng nhau và che mất overhead phối hợp. Nếu rút gọn/bỏ thành phần theo kiểu ablation, chỉ kết luận đúng phần đã thay đổi.
- Đo lặp theo protocol chốt sau pilot; báo chênh lệch hiệu quả và độ bất định, không lấy một demo hoặc mẫu nhỏ làm kết luận ưu thế. Kiểm tra dịch vụ khỏe trong cửa sổ đã định và ghi thời điểm dừng fault, để không quy hồi phục tự nhiên sau khi dừng tải thành công của healer.

**Điều kiện sẵn sàng về thiết kế nghiên cứu:** R0-T04 khóa câu hỏi/đối chứng/nhãn; R1 lưu evidence không lộ đáp án và metric quyết định; R4-T03 có pilot B0/B1/B2; R4-T04 chốt và thử B3 nếu giữ claim RQ2; R5-T02-S02 khóa protocol; R6-T02 chạy và phân tích đầy đủ; R6-T03 đối chiếu claim với dữ liệu. Đây là yêu cầu về chất lượng bằng chứng, không phải lời đảm bảo được duyệt bài.

**Ngân sách và ưu tiên:** chốt công sức theo quỹ giờ Hoàng thực sự bố trí; mức 10h/tuần là thông tin cũ, chưa có con số mới. Không tự cộng giờ hoặc mở nhiều model/framework để làm B3. Khi pilot cho thấy thiếu nguồn lực, giữ B0/B1/B2 và mọi cam kết gốc, giảm claim về lợi ích chia vai trò; ghi lý do, ảnh hưởng và cập nhật lịch. Các gate đánh giá thực nghiệm hợp lệ, không yêu cầu kết quả thuận lợi cho AI.

<!-- END SOURCE: docs/recovery/reference/research-design.md -->


<!-- SOURCE: docs/recovery/reference/verification.md -->

## Nguồn `docs/recovery/reference/verification.md`

# Phép đo và kiểm chứng

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

## Kiểm chứng và thiết kế thực nghiệm

Các tiêu chí hoàn thành là điều kiện phải kiểm tra, chưa phải kết quả đã đạt:

1. **Đường đo thật:** attack có hiệu lực; Gaia tự ghi detect; Kafka chuyển đúng ID; healer xử lý; probe xác nhận recovery. Inject alert chỉ dành unit/integration test của healer và đánh dấu riêng, không nằm trong bộ dữ liệu chính.
2. **Thời gian:** lưu attack_effect_started, detected, published/consumed, heal_started, action_completed, recovery_verified và attack_stopped. Báo MTTD từ effect đến detect, MTTR từ detect đến recovery, thêm total recovery từ effect. Không đổi định nghĩa sau khi thấy kết quả.
3. **KPI:** báo cả tỉ lệ MTTR dưới 120s và 180s vì thuyết minh dùng khoảng 2–3 phút; mục tiêu MTTD <60s, uptime ≥99,9%. Khóa mẫu số lượt sự cố đủ điều kiện trước formal run; timeout/không recovery không tính đạt ngưỡng, missing báo riêng và không tự tính pass. Phân phối MTTR của lượt recovered phải đi cùng tỷ lệ recovery/failure trên tổng lượt để không che thất bại. Chốt threshold đánh giá trước formal run; mọi case chưa đạt được ghi đủ.
4. **Availability:** client độc lập đo phản hồi đúng nội dung và latency cho route/giao dịch đã định; tách time-based availability và request success rate. Chọn cửa sổ warmup/trial/recovery trước khi chạy. Không dùng scrape `up`, thiếu dữ liệu hoặc API patch để suy ra phục hồi.
5. **Downtime budget:** nếu dùng War Game 4h theo kế hoạch repo, uptime 99,9% theo thời gian chỉ cho 14,4s downtime. Cần replicas khỏe phục vụ trong lúc recovery; kiểm tra resource quota/scheduling và budget của máy trước khi tăng replicas.
6. **Đối chứng:** giữ tự phục hồi Kubernetes trong mọi nhóm. Tối thiểu B0 Kubernetes/controller, B1 RULES và B2 MULTI_LLM chạy cùng workload/fault; B1/B2 dùng cùng pipeline/evidence/guard/probe. Profile HPA và quyền scale được cố định/ghi rõ ở mỗi nhóm để quy đúng đóng góp. B3 SINGLE_LLM bắt buộc nếu kết luận lợi ích chia vai trò vận hành; không chạy B3 thì giới hạn claim. Giữ BM manual thật theo protocol/cam kết hiện có và khi kết luận tốt hơn thủ công; lưu alert/thao tác/recovery, tắt mọi auto-heal của ZERO DOOR. Nemesis/harness replay kế hoạch chung, không cấp đáp án cho bên chữa lỗi.
7. **Chất lượng AI:** đánh giá schema validity, action đầu tiên đúng/sai/thừa, phục hồi xác minh trên tổng lượt sự cố, latency, token/call/cost, fallback/refusal và đề xuất bị guard chặn. Khóa mẫu số/ground truth trước formal run, giữ timeout/failure; JSON đúng không tự là hành động chữa lỗi đúng. Lưu model/version/prompt/temperature và evidence không lộ đáp án; không trình bày chat tổng hợp như log quyết định thật. Chỉ kết luận ưu thế LLM/phối hợp khi có nhóm đối chứng và độ bất định tương ứng.
8. **Mẫu và thống kê:** pilot vài lượt mỗi case để xác định độ biến thiên; khóa số lặp formal trước khi đo. Dùng thứ tự xen kẽ/ghép cặp workload hợp lý, reset có xác nhận và cùng budget. Báo mean/median/distribution/confidence, đủ failure/timeout. P95/P99 từ mẫu nhỏ chỉ là thăm dò, không khẳng định ổn định.
9. **Normal windows:** có tải lành tính để đo false alarms và tác động lên người dùng hợp lệ; định nghĩa nhãn và mẫu số FPR. Không hardcode 0 hoặc chia FP cho số tấn công mà gọi là FPR.
10. **Reproducibility:** khóa image/config/dependencies; dataset mới lưu riêng theo method version và run ID. Dùng dataset manifest/hash để chọn đầu vào analysis, tách legacy/pilot/formal; các lượt bị loại có lý do theo protocol và vẫn được lưu/thống kê. Giữ nguyên raw CSV cũ, ghi giới hạn như dữ liệu chẩn đoán lịch sử; timestamp trong CSV không tự chứng minh ngày chạy độc lập, không trộn legacy với formal.

### Các test hành vi ưu tiên

| Tình huống | Kết quả phải kiểm chứng |
| --- | --- |
| LLM output sai schema, service ngoài allowlist, tham số vượt budget | Bị từ chối trước thao tác; có event lỗi; không gọi shell/K8s ngoài phạm vi |
| LLM timeout/429 hoặc mất mạng | Timeout/retry hữu hạn; fallback rõ hoặc skip; không treo consumer, không giả ghi AI thành công |
| Thiếu Prometheus/Elasticsearch/probe series | Health suy giảm/missing; không báo 100% uptime hoặc false success |
| Action FAILED/PARTIAL hoặc timeout trong khi probe vẫn lỗi | Không tạo RECOVERY_VERIFIED hoặc MTTR thành công; failure/censored và mẫu số được xuất đúng; các mốc polling không thay timestamp detector |
| Alert/command bị gửi trùng | Không nhân đôi attack/heal ngoài phiên cho phép; event vẫn truy nguyên được |
| Restart nhiều replicas | Không lấy pod cũ đang Ready làm bằng chứng pod thay thế; nghiệp vụ được kiểm tra |
| Deploy bản lỗi và rollback | Template/image/config thực trở lại release tốt; giao dịch phục hồi trong cửa sổ định trước |
| Chặn attacker và chạy benign client | Attacker bị chặn; benign traffic tiếp tục; TTL/cleanup sau restart được xử lý |
| Attack bị hủy hoặc worker dừng | Tải/fault còn lại được cleanup; không để pod stress/policy tồn dư không ghi nhận |
| Hai vector đồng thời và HPA/healer | Giới hạn tải tổng, quyền scale rõ, không bão lệnh hoặc cooldown làm mất toàn bộ phục hồi |

<!-- END SOURCE: docs/recovery/reference/verification.md -->


<!-- SOURCE: docs/recovery/reference/work-packages.md -->

## Nguồn `docs/recovery/reference/work-packages.md`

# Các gói sửa và mô hình thực nghiệm

> Phân công/ngày trong nội dung là snapshot thiết kế nguồn, không là assignment hoặc live metadata Linear.

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md)

## Các gói sửa và bằng chứng phải bàn giao

| Gói | Nội dung sửa | Bằng chứng hoàn thành | Người phụ trách |
| --- | --- | --- | --- |
| W0 Lab và cấu hình | Kiểm tra Docker/context/containers/volumes; khôi phục hoặc dựng lab sau khi xác định trạng thái; chọn một đường setup và profile tài nguyên; kiểm tra telemetry dependencies; làm một lượt LLM có schema | Inventory trước/sau; API K8s truy cập; ít nhất 5 dịch vụ phục vụ luồng nghiệp vụ; Kafka/Prom/log hoạt động; model health và response hợp lệ được lưu | Codex thực hiện, Claude review; Hoàng chốt thay đổi lab/provider/chi phí |
| W1 Event và phép đo | Hợp đồng run/command/alert/heal IDs; timestamp và interval nhất quán; event lưu bền; probe HTTP độc lập; bỏ KPI ngẫu nhiên/fallback; tách manual/rules/AI | Tái tính MTTD/MTTR từ raw events; FAILED/PARTIAL không tự thành recovery; mất telemetry là missing; MANUAL không được healer can thiệp; dashboard và analysis dùng chung dữ liệu | Claude contract/agent, Codex phép đo/dashboard; review chéo; Hoàng chốt ngữ nghĩa |
| W2 Tấn công trong scope | SQLi fixture, HTTP L7 cùng đường đo, resource stress tác động đúng target; kiểm tra payload và target; phiên tấn công tự động giới hạn có start/stop | Cả 3 vector có attack_effect evidence; SQLi phân biệt payload và request bình thường; resource cao/suy giảm nằm ở target thật; cleanup được kiểm chứng | Claude thực hiện, Codex review; Hoàng chốt protocol |
| W3 Chữa lỗi đúng nghĩa | Scale up/down có hysteresis, block nguồn thật tại điểm enforce, rollback về release tốt, không tranh chấp với controller/HPA; hậu điều kiện và timeout | Image/config trước/sau rollback; attacker bị chặn nhưng benign client còn hoạt động; replicas sẵn sàng; giao dịch đã phục hồi ổn định; không chữa lặp vô hạn | Claude thực hiện, Codex review; Hoàng đánh giá kết quả |
| W4 Ba agent và LLM | Adapter dùng chung, role schemas, bounded autonomous session; Gaia evidence analysis và Hephaestus lựa chọn tool; latency/usage/fallback audit | Trace cho mỗi agent: observed state → structured decision → action/result; policy chặn output sai; đối chứng cùng hệ thống khi tắt LLM | Codex adapter/Nemesis, Claude Gaia/Hephaestus; bàn giao file theo R4; Hoàng chốt backend |
| W5 Kiểm thử và đo lại | Tests hành vi và lỗi; integration toàn pipeline không inject alert trực tiếp; workload, baseline và thứ tự đo; pilot, formal repetitions và War Game | Raw dataset mới, configs/commit/model/prompt, full failure accounting, probe timeline, bảng KPI và uncertainty tái sinh được | Codex điều phối/chạy theo task; Claude review; Hoàng chủ trì protocol, Hòa đối chiếu |
| W6 Paper và hồ sơ | Sửa chương phương pháp/kết quả, chọn claim đủ bằng chứng, đối chiếu nguồn tham khảo, video/slide, paper và Word/PDF; phản hồi reviewer | Paper nhất quán với dataset và scope; bảng traceability đủ; video thực; minh chứng chấp nhận đăng trước nghiệm thu | Hòa viết Word; Hoàng viết nội dung kỹ thuật/kiểm tra số liệu |

### SQLi với Google Online Boutique

Không giả định Boutique hiện có SQL database hoặc endpoint dễ bị SQLi. Để giữ hệ thống mục tiêu được thầy chấp thuận, đề xuất bổ sung một dịch vụ tìm kiếm/catalog thử nghiệm với dữ liệu e-commerce giả lập, database nhẹ như SQLite và route qua ingress lab. Có bản dễ tổn thương phục vụ phép thử và bản dùng truy vấn tham số; tất cả giới hạn trong namespace nghiên cứu, không công khai ra Internet. Đây là phần bổ sung mô hình thực nghiệm, phải ghi rõ trong kiến trúc/paper, không mô tả như lỗ hổng sẵn có của Google Boutique.

Giữ Boutique và luồng mua hàng làm đối tượng availability; dùng fixture để kiểm chứng vector SQLi và containment. Nếu kết luận về availability áp dụng cho cả hai, định nghĩa hai luồng probe và báo kết quả riêng, không gộp để che luồng thất bại. Không cần viết lại toàn bộ ứng dụng thương mại điện tử hoặc thêm PostgreSQL để có phép thử SQLi.

### Mô hình chữa lỗi cần hợp lý với nguyên nhân

- CPU/resource quá tải: gây tải vào workload target thật; kiểm tra scale có giảm latency/error hoặc throttling. Pod stress riêng chỉ dùng nếu nghiên cứu đúng tranh chấp node và có bằng chứng tác động, không ánh xạ mức CPU của attacker thành CPU của app.
- SQLi: ghi nguồn từ kết nối/ingress tin cậy, không lấy một X-Forwarded-For bất kỳ do client khai. Chặn tại điểm nhìn thấy nguồn trước NAT hoặc gateway phù hợp. Không coi IP `0.0.0.0` và NetworkPolicy tạo được là bằng chứng containment.
- Bad release: fault phiên bản ứng dụng/config và rollback về release tốt đã biết. Error rate cao do flood không tự là bằng chứng bản deploy sai; không rollback mọi 5xx.
- Scale-down: chỉ sau cửa sổ tải thấp/khỏe đủ dài, giới hạn min/max và tránh HPA giành quyền replicas. Reset thí nghiệm tách khỏi logic hồi phục.
- Pod Kill: giữ như phép thử bổ sung để đánh giá controller mặc định và xem healer có can thiệp thừa; không dùng thay SQLi.

### Đối chiếu với các gói sửa W0–W6

R0-T04 là thiết kế nghiên cứu dùng xuyên W1/W4/W5/W6; R1/R2 chuẩn bị metric/evidence và case, không chỉ phục vụ demo.

| Gói trong phần trên | Phase/task triển khai |
| --- | --- |
| W0 — môi trường và LLM | R0 |
| W1 — phép đo và dữ liệu | R1 |
| W2 — ba vector | R2 |
| W3 — healer | R3 |
| W4 — multi-agent AI | R4, gồm quyết định/đối chứng B3 tại R4-T04 |
| W5 — tích hợp và thực nghiệm | R5; R6-T02 |
| W6 — paper, báo cáo và nghiệm thu | R6-T01, R6-T03; R7 |

Các tiêu chí kiểm chứng chi tiết ở phần tiếp theo vẫn là điều kiện bắt buộc. Lịch không thay thế những tiêu chí này và chưa phải kết quả đã đạt.

<!-- END SOURCE: docs/recovery/reference/work-packages.md -->
