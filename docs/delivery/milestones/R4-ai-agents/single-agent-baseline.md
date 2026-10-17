# Issue — Đối chứng single-agent cho claim chia vai trò

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-22](https://linear.app/zero-door/issue/ZER-22/djoi-chung-single-agent-cho-claim-chia-vai-tro). Nguồn đối chiếu: `R4-T04`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T04-S01 | Xác nhận giữ RQ2 hay giới hạn claim theo budget pilot. | AC của [ZER-22](https://linear.app/zero-door/issue/ZER-22/djoi-chung-single-agent-cho-claim-chia-vai-tro) |
| R4-T04-S02 | Nếu giữ RQ2, cấu hình SINGLE_LLM gộp phân tích và chọn action. | AC của [ZER-22](https://linear.app/zero-door/issue/ZER-22/djoi-chung-single-agent-cho-claim-chia-vai-tro) |
| R4-T04-S03 | Nếu giữ RQ2, pilot B2/B3 sau khi R4-T02-S02 hoàn tất, trên cùng case và kiểm tra dữ liệu. | Chưa tách; chỉ tạo khi điều kiện phát sinh |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T04-S01

Quyết định ghi rõ thời lượng/call budget; không đủ nguồn lực thì bỏ claim ưu thế chia vai trò.

### R4-T04-S02

Cùng model/evidence/tools/guard với B2; harness tấn công giống nhau. Không giữ claim thì đóng bằng quyết định loại claim.

### R4-T04-S03

Trace/cost/action/recovery đối chiếu; nếu B3 chưa chạy thì chưa đủ bằng chứng claim RQ2. Nếu loại claim, ghi rõ phạm vi còn lại.

## Phụ thuộc cần đối chiếu

[R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md), [R4-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/llm-adapter-and-nemesis.md) (mục nguồn trong ghi chú), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
