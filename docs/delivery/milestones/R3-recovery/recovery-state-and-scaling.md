# Issue — Trạng thái hồi phục và scale

[Milestone R3](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-16](https://linear.app/zero-door/issue/ZER-16/trang-thai-hoi-phuc-va-scale). Nguồn đối chiếu: `R3-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R3-T01-S01 | Tách API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED. | AC của [ZER-16](https://linear.app/zero-door/issue/ZER-16/trang-thai-hoi-phuc-va-scale) |
| R3-T01-S02 | Kiểm chứng scale up tăng capacity và sức khỏe dịch vụ. | AC của [ZER-16](https://linear.app/zero-door/issue/ZER-16/trang-thai-hoi-phuc-va-scale) |
| R3-T01-S03 | Kiểm chứng scale down có hysteresis và quyền điều khiển rõ với HPA. | AC của [ZER-16](https://linear.app/zero-door/issue/ZER-16/trang-thai-hoi-phuc-va-scale) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R3-T01-S01

State machine/timeout và log đối chiếu probe; API nhận lệnh hoặc terminal FAILED/PARTIAL không đóng recovery. Phân biệt hồi phục nhờ controller/hết fault với bằng chứng tác động healer; restart phải xác minh pod thay thế và nghiệp vụ.

### R3-T01-S02

Replica ready, metric capacity và probe trước/sau.

### R3-T01-S03

Không dao động; phục hồi replica baseline không bị tính thành heal nếu dịch vụ chưa khỏe.

## Phụ thuộc cần đối chiếu

[R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/probes-and-metrics.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
