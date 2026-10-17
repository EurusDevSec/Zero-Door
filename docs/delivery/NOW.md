# Checkpoint phiên

[Project Linear — P-ZER-1](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039) · [Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Checkpoint — 17/10/2026

Delivery tracking đã được tạo theo yêu cầu trực tiếp: 1 project, 8 milestone, 27 issue chính và 34 sub-issue. Read-back lúc 14:52:40 UTC / 21:52:40 Asia/Saigon: nội dung 61 issue, cha–con/milestone, đủ 92 mục nguồn và 80 prerequisite relations hai chiều đều khớp; DAG không có vòng kể cả hoàn tất con → cha. Mapping là APPLIED_VERIFIED, giữ alias/ID/URL và receipt, không là live board.

Ba sub-issue có điều kiện chưa tạo: B3 nếu giữ claim RQ2, hai vòng phản biện khi thực sự nhận. Các yêu cầu vẫn ở AC issue cha. Không đụng bốn issue onboarding. Lần nhập khởi tạo ở Backlog, không gán người/due/estimate/priority/cycle; trạng thái hiện hành đọc Linear.

Tài liệu hiện hành ở docs/delivery, lịch sử ở docs/archive/planning. Lượt này không sửa mã ứng dụng, chạy lab/model/thực nghiệm, gửi Slack hoặc commit/push.

## Đầu ra khởi động, chưa thực hiện

| Issue | Ghi chú kỹ thuật | Artifact dự kiến |
| --- | --- | --- |
| [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc) — Inventory chỉ đọc | [Lab local](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md) | `docs/evidence/R0-T02-S01/inventory.md` |
| [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) — Baseline/source ledger | [Phạm vi và tiêu chí](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md) | `docs/evidence/R0-T01-S03/baseline-source-ledger.md` |
| [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi) — Bản nháp event contract | [Event contract](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md) | `docs/design/r1-event-contract.md` |

Các artifact này chưa được tạo. Bản nháp contract có thể chuẩn bị trước lab/LLM; khóa schema vẫn cần review ngữ nghĩa KPI/ground-truth boundary. Đây là checkpoint bước tiếp theo, không là xác nhận issue đã được giao hoặc đủ Ready.

Trước thực hiện, đọc AC mới nhất trên Linear, khóa HEAD/dirty và file/action scope; chốt cách chia sẻ artifact theo yêu cầu review. Provider/budget, lựa chọn thay đổi lab và nơi/đợt nhận bài xử lý ở issue tương ứng, không tạo lại backlog hoặc lặp hydration toàn repo.
