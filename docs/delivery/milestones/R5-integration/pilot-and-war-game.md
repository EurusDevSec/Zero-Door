# Issue — Pilot, khóa protocol và War Game

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-khoa-protocol-va-war-game). Nguồn đối chiếu: `R5-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T02-S01 | Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo. | [ZER-52](https://linear.app/zero-door/issue/ZER-52/pilot-lap-dje-xac-djinh-bien-thien-va-loi-djo) |
| R5-T02-S02 | Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI. | [ZER-53](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc) |
| R5-T02-S03 | Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt. | [ZER-54](https://linear.app/zero-door/issue/ZER-54/chay-war-game-co-probe-va-budget-dja-duyet) |
| R5-T02-S04 | Tái tính KPI; phân loại pass/fail, thiếu dữ liệu và nguyên nhân. | AC của [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-khoa-protocol-va-war-game) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T02-S01

Dữ liệu pilot nguyên bản cho B0/B1/B2 và B3 nếu giữ RQ2; căn cứ chọn số lặp và đánh giá lại thời lượng trong trần nguồn lực.

### R5-T02-S02

Protocol cố định trước formal run; B0/B1/B2/BM, quyết định B3/claim RQ2, profile HPA, biến thể đánh giá và ranh giới không lộ đáp án.

### R5-T02-S03

Timeline/probe raw, giới hạn tác động và bố trí giám sát; ghi rõ nếu run bị dừng.

### R5-T02-S04

Bảng kết quả tái tính; không lọc failure hoặc sửa số để đạt ngưỡng.

## Phụ thuộc cần đối chiếu

[R5-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/end-to-end-pipeline.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

### ZER-52 — Pilot Runtime07

[Hồ sơ pilot Runtime07](../../../evidence/ZER-52/README.md) lưu 12 ca, hai mẫu mỗi tổ hợp B0/B1/B2 × SQLi/C0, cùng kết quả review, cleanup và ước tính thời lượng cho ZER-53. Hồ sơ đáp ứng phần pilot AC-01 của ZER-24.

### Quy ước bàn giao

Mỗi lượt thực thi cần ghi issue Linear, thời điểm đọc AC, HEAD và thay đổi cục bộ, phạm vi file và thao tác, kết quả kiểm tra, bằng chứng, giới hạn và bước tiếp theo. Xem [quy trình bàn giao](../../WORKFLOW.md). Trạng thái, lịch và phân công cập nhật trên Linear.
