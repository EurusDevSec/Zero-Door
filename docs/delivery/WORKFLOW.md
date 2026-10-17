# Cách làm việc và nghiệm thu

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

## Nguồn chuẩn và đơn vị công việc

| Nội dung | Nguồn chuẩn |
| --- | --- |
| Milestone/issue/sub-issue, outcome/AC, status, assignee, priority, estimate, dates, relations | Linear Zero Door |
| Phạm vi, cam kết và nguồn xác nhận | SCOPE, thuyết minh/bản trích và quyết định có dẫn nguồn |
| Mã, revision, review, CI, merge | Git/repository host |
| Thiết kế, file plan, kiểm chứng và bằng chứng | Ghi chú issue, reference và artifact được duyệt |
| Checkpoint / bước tiếp theo của phiên | NOW; không là bảng trạng thái |

Mỗi milestone có gate nghiệm thu tích hợp. Issue có outcome riêng; chỉ tách sub-issue khi có thể bàn giao/kiểm chứng độc lập. Checklist nhỏ nằm trong AC. Không tiếp tục đặt phase/task/subtask làm hệ theo dõi song song; các mã R*-T*-S* trong ghi chú/mapping chỉ là provenance. Dùng mã Linear thật trong giao việc và bằng chứng mới.

## Bắt đầu và kết thúc một phiên

1. Đọc NOW, issue Linear được giao và đúng ghi chú kỹ thuật. Chỉ mở reference cần thiết; không hydration lại cả repo.
2. Ghi ID/URL issue, thời điểm đọc AC, prerequisite thật, HEAD/dirty và phạm vi chính xác gồm file mã, test/probe mới và thao tác. Chưa có issue thì ghi rõ phần chuẩn bị được người dùng cho phép, không tự tuyên bố Ready.
3. Một bên ghi trên một checkout; bên kia đọc/review. Muốn làm đồng thời cần checkout/file ownership và handoff rõ. Giữ dirty work ngoài scope; không `git add .`.
4. Kiểm chứng theo hành vi và AC. Bàn giao vào ghi chú issue: revision/dirty diff, command/scenario, time/timezone, môi trường, expected/actual, artifact, giới hạn, phần chưa đạt và next action.
5. Chỉ cập nhật field/comment/assignment Linear trong quyền đã giao; NOW chỉ trỏ bước tiếp theo. Không copy status/assignee/due trở lại ghi chú, tự gửi Slack hoặc tự giao việc sang phiên Claude.

Không truy cập được Linear thì dùng AC snapshot có ngày và handoff tự đủ bối cảnh, ghi live state chưa xác minh. Snapshot không cấp quyền đóng issue hoặc thay AC hiện hành.

## Ready và workflow

Ready khi outcome, scope, AC, quyết định bắt buộc, prerequisite, metadata và verification đủ rõ để thực hiện trong quyền hiện có. Catalogue đã đọc ở team ZER: Backlog, Todo, In Progress, In Review, Done, Canceled, Duplicate. `Todo` chỉ được dùng cho việc đã qua Ready gate; tên trạng thái không tự chứng minh đủ điều kiện. Không tạo status READY hoặc đổi workflow.

Quan hệ blocked-by phải là prerequisite contract/evidence thật, không do thứ tự milestone/ngày hay cùng người làm. Bản nháp event contract không cần chờ lab/LLM; sửa consumer chờ contract khóa. B3 và vòng phản biện chỉ phát sinh khi điều kiện tương ứng có thật.

## Done và gate

Issue sửa mã chỉ Done khi **review + kiểm chứng + merge + Hoàng chấp nhận**. Đây là điều kiện nghiệm thu, không cấp quyền commit/push/merge. Evidence phải khớp revision cuối; sửa mã sau review thì kiểm tra lại phần bị ảnh hưởng và consumer liên quan.

Issue tài liệu/nghiên cứu nghiệm thu theo output/AC và review phù hợp. Build/browser/CI/merge có thể N/A có lý do khi không sửa mã. Báo cáo QA có thể đạt AC dù phát hiện lỗi sản phẩm; issue sản phẩm và milestone vẫn chưa đạt nếu còn thiếu tiêu chí bắt buộc. Fix commit chưa tự là retest độc lập.

Milestone cần bằng chứng tích hợp riêng, không đóng vì tất cả issue con Done hoặc hết hạn. G5 có thể ghi pilot KPI chưa đạt theo điều kiện nguồn nhưng không là nghiên cứu hoàn tất. G7 cần đủ sản phẩm và chấp nhận đăng. Nộp bài, chấp nhận đăng và nghiệm thu là ba sự kiện khác nhau.

## Kiểm chứng nghiên cứu và defect

- Đường thật: attack effect → Gaia detect → transport → healer action → probe nghiệp vụ độc lập. Inject alert chỉ là kiểm tra thành phần.
- Tách API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED. FAILED/PARTIAL/timeout/missing không thành recovery hay uptime 100%.
- Ba vector, scale up/down, block IP/benign traffic, rollback release tốt và cleanup/restart/HPA cần evidence phù hợp scope.
- Tách legacy/pilot/formal; giữ mọi failure, ground truth boundary, model/prompt/config/version, usage/cost và đối chứng. Không bắt AI thắng để báo cáo đạt.
- Test/QA theo thay đổi thực tế; không nhân ma trận tenant/browser hoặc bộ checks S-cool không liên quan.

Report tối thiểu: case/AC, context, steps/data, expected, actual, result, artifact, defect và retest revision/result. Defect có repro, impact, scope và regression cụ thể; dùng convention thực tế của team. Xem [phép đo](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/verification.md) để thiết kế protocol chi tiết.

## Evidence và lịch

Artifact dự kiến tại `docs/evidence/<issue-id>/`; alias cũ chỉ giữ cho đầu ra đã được nêu trong kế hoạch. Cần chốt nơi chia sẻ để Hòa/reviewer truy cập. Đường dẫn `R:` và file dirty không chứng minh reviewer đã xem; không tạo GitHub blob URL khi chưa có revision/file remote. Không upload DOCX cá nhân, secrets hay dữ liệu nhạy cảm ngoài quyền.

Lịch và phân công cũ được giữ trong [archive](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/README.md), không tiếp tục chỉnh như lịch sống. Ngày mới/estimate/assignee/cycle chỉ áp trên Linear khi đã được xác nhận trong quyền được giao. Không bịa capacity hoặc tự dời lịch trường; khi trễ phải ghi gap, ảnh hưởng và dự báo có căn cứ.

Cloud/model/lab/triển khai là hành động riêng. Một issue trong backlog hoặc một phép thử được mô tả không tự cấp quyền chạy nó. Quyết định provider/credential/chi phí, thay đổi cluster có hệ quả và publication vẫn theo Hoàng.
