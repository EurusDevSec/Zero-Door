# Issue — Consumer, retry và tương tác controller

[Milestone R3](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller). Nguồn đối chiếu: `R3-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R3-T03-S01 | Sửa blocking consumer, ack, dedup, cooldown và retry có giới hạn. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |
| R3-T03-S02 | Thử restart, nhiều replica, PodKill và tương tác HPA. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |
| R3-T03-S03 | Thử worker/healer restart và mất telemetry. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R3-T03-S01

Một action cho một event hiệu lực; lỗi không kẹt consumer hoặc lặp lệnh vô hạn.

### R3-T03-S02

Log tác nhân gây hồi phục; phân biệt hiệu ứng Kubernetes/HPA với healer.

### R3-T03-S03

Run dở có trạng thái rõ; dữ liệu thiếu không sinh kết luận thành công.

## Phụ thuộc cần đối chiếu

[R1-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md), [R3-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/recovery-state-and-scaling.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
