# Issue — Chạy phối hợp và dừng có kiểm soát

[Milestone R2](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-15](https://linear.app/zero-door/issue/ZER-15/chay-phoi-hop-va-dung-co-kiem-soat). Nguồn đối chiếu: `R2-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R2-T03-S01 | Điều phối ba executor đồng thời theo budget chung. | AC của [ZER-15](https://linear.app/zero-door/issue/ZER-15/chay-phoi-hop-va-dung-co-kiem-soat) |
| R2-T03-S02 | Thử start, stop, cancel và cleanup khi một executor lỗi. | AC của [ZER-15](https://linear.app/zero-door/issue/ZER-15/chay-phoi-hop-va-dung-co-kiem-soat) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R2-T03-S01

Ba vector có event riêng cùng run_id; không phát một loại COMBINED mà worker không hỗ trợ.

### R2-T03-S02

Không còn tác động sau stop; trạng thái và tài nguyên được đối chiếu.

## Phụ thuộc cần đối chiếu

[R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md), [R2-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/ddos-and-resource-exhaustion.md), [R1-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
