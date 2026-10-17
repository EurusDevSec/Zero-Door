# Issue — Đo sức khỏe và thời gian độc lập

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap). Nguồn đối chiếu: `R1-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T02-S01 | Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture. | [ZER-38](https://linear.app/zero-door/issue/ZER-38/dung-probe-nghiep-vu-djoc-lap) |
| R1-T02-S02 | Tính MTTD/MTTR từ mốc sự kiện và xác nhận hồi phục bằng probe. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |
| R1-T02-S03 | Xử lý thiếu dữ liệu, timeout, FAILED/PARTIAL và FPR có mẫu số rõ ràng. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |
| R1-T02-S04 | Bổ sung metric quyết định, phục hồi theo lượt và usage/cost theo run. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T02-S01

Timestamp, chu kỳ probe, tiêu chí healthy và ví dụ lỗi được quan sát thật.

### R1-T02-S02

Tái tính incident từ raw: MTTD effect→detector detect, MTTR detect→recovery xác minh, total recovery effect→recovery. Không lấy heal history/replica tăng làm detect; ghi chu kỳ probe và độ phân giải thời gian.

### R1-T02-S03

Phép thử có action thất bại nhưng chưa recovery, timeout và missing; chưa xác minh recovery thì MTTR chưa xác định/censored theo protocol, không điền 0 hoặc 1s. Giữ mọi run trong mẫu số, báo riêng phân phối lượt recovered và tỷ lệ failure; thiếu dữ liệu không thành uptime 100%.

### R1-T02-S04

Định nghĩa mẫu số; lưu đề xuất trước guard, action thực thi, false action, recovery/failure và số call/token kể cả retry.

## Phụ thuộc cần đối chiếu

[R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
