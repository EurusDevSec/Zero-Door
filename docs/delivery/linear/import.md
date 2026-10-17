# Nhập delivery vào Linear — đã thực hiện

[Project P-ZER-1](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039) · [Kết nối và mapping](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/README.md) · [Scope](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md)

Đã thực hiện theo yêu cầu trực tiếp của người dùng ngày 17/10/2026, bằng connection linear_zero_door/team ZER. Mapping có ID/URL thật; không chạy lại như một import mới.

## Receipt lần nhập

| Kết quả | Số lượng |
| --- | --- |
| Created | 1 project, 8 milestone, 27 issue chính, 34 sub-issue — tổng 70 đối tượng |
| Reused | 0; đích chưa có project/nghiên cứu tương ứng trước import |
| Updated | 46 issue trong chính tập trên để gắn 80 prerequisite relations và link phụ thuộc thật |
| Skipped | 3 sub-issue có điều kiện; giữ yêu cầu ở AC cha |
| Failed còn tồn | 0; một lỗi transport được kiểm tra không tạo đối tượng rồi retry thành công |

Read-back lúc 14:52:40 UTC / 21:52:40 Asia/Saigon: 61 description/AC, parent/milestone và hai chiều 80 relations khớp. Đủ 92 mục nguồn; DAG không có vòng kể cả hoàn tất con → cha. Project chỉ có đúng 61 issue/sub-issue, không duplicate; onboarding ZER-1…ZER-4 giữ nguyên. Receipt cấu trúc ở importVerification trong mapping.

## Đơn vị và nguồn đã chuyển

- 8 milestone R0–R7 có exit gate tích hợp. 27 issue chính có outcome/AC riêng, không tự Done vì các con Done.
- 34 sub-issue thường lệ có đầu ra riêng, phủ 36 mục nguồn; hai cặp yêu cầu block IP/rollback gộp thành hai outcome tương ứng.
- 3 sub-issue chưa tạo: `R4-T04-S03` chỉ nếu giữ claim RQ2; `R7-T01-S02/S03` chỉ sau phản biện thật. Với 53 mục checklist ở parent, tổng coverage vẫn đủ 92.
- 50 dependency candidates cũ chỉ là provenance; lần nhập đã rà lại prerequisite theo đầu ra và gắn 80 quan hệ thật. Quan hệ sống đọc Linear, không cập nhật bản native-relation mirror trong repo.
- Không gắn assignee, due, estimate, priority/cycle hoặc kế thừa Done/Ready. Các issue được tạo Backlog theo policy nhập; không đổi workflow/label/template. Template discovery trả rỗng; không cần tạo template mới.

Linear giữ live AC/metadata. Repo giữ scope, code, ghi chú kỹ thuật và evidence. Ghi chú đã trỏ ID/link thật; inventory sáu AC xuất bản tại [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc), không duy trì checklist sống thứ hai trong Markdown. Tên sourceSubtasks và mã R*-T*-S* trong mapping chỉ là provenance.

## Còn cần xử lý trước Ready / thực thi

1. Đọc AC/prerequisite mới nhất và khóa file/action scope, bao gồm test/probe, của issue sắp thực hiện. Backlog không tự cấp quyền thao tác hoặc chứng minh Ready.
2. Chọn nơi evidence dùng chung và cách công bố tài liệu chưa push. Body issue đã tự đủ để đọc yêu cầu; artifact ở R: chưa là bằng chứng reviewer truy cập được. Không tự upload DOCX.
3. Metadata theo capacity thực, assignment/priority/estimate/dates nếu cần: vẫn chưa áp. Credential/provider/budget hoặc thay đổi cluster có hệ quả cần quyền tương ứng; không suy từ quyền tạo tracking.
4. Kỷ yếu/đợt nhận bài, mẫu bài và hồ sơ thời hạn có thẩm quyền tiếp tục làm rõ ở issue đã tạo; không chặn công việc kỹ thuật độc lập hoặc tự đổi scope ba vector.

Tracking đã thiết lập và kiểm chứng. Chưa có lab/model/formal dataset mới hoặc sản phẩm nghiên cứu được nghiệm thu chỉ từ lần nhập này. Không commit/push/merge/deploy, chi tiền hay gửi Slack.

## Khi bổ sung / tiếp tục import

1. Reuse connection và project IDs. Đọc lại milestones/issues/bodies/relations, duplicate/reuse theo outcome và scope; không lấy connector S-cool làm đích thay thế.
2. Review body/AC và field được phép đổi theo yêu cầu hiện hành. Dùng mẫu issue vừa đủ; giữ workflow có sẵn. Todo cần qua Ready gate, không tạo READY mới.
3. Reuse đối tượng đã mapping. Chỉ tạo outcome mới được phép; parent trước rồi child, conditional chỉ khi điều kiện phát sinh. Không tạo initiative/template/label mặc định.
4. Gắn prerequisite thật, kiểm DAG cả parent-completion và hai chiều relations. Partial failure lưu IDs đã thành công, đọc lại trước retry; không xóa valid objects để giả rollback.
5. Read-back ID/URL/parent/milestone/relations và field được phép. Mapping giữ danh tính/receipt; NOW ghi checkpoint và next action, không copy live board.
