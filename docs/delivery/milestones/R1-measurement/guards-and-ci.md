# Issue — Giới hạn tác động, kiểm soát lệnh và CI

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci). Nguồn đối chiếu: `R1-T04`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T04-S01 | Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải. | AC của [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci) |
| R1-T04-S02 | Kiểm soát truy cập lệnh, sự kiện trùng và payload sai. | AC của [ZER-12](https://linear.app/zero-door/issue/ZER-12/gioi-han-tac-djong-kiem-soat-lenh-va-ci) |
| R1-T04-S03 | Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI. | [ZER-40](https://linear.app/zero-door/issue/ZER-40/khoa-dependency-va-djua-guardcontract-checks-vao-ci) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T04-S01

Cấu hình allowlist cùng phép thử host, port, protocol, redirect và budget; trần thời lượng hiệu dụng không vượt trần vận hành dù maxDuration trong command lớn hơn. Phân biệt duration, executor và attack_effect.

### R1-T04-S02

Phép thử lệnh bị từ chối, schema lỗi và duplicate; log lý do.

### R1-T04-S03

Phiên bản dependency/image và kết quả CI cho các hành vi cần bảo vệ.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
