# Issue — LLM adapter chung và Nemesis

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis). Nguồn đối chiếu: `R4-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T01-S01 | Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout. | [ZER-48](https://linear.app/zero-door/issue/ZER-48/dung-llm-adapter-va-trace-dung-chung) |
| R4-T01-S02 | Nối observation → kế hoạch Nemesis → executor → kết quả. | AC của [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis) |
| R4-T01-S03 | Thêm start/stop, max rounds/calls và điều kiện dừng. | AC của [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T01-S01

Interface và trace thật; quota/cost được cộng theo run.

### R4-T01-S02

LLM chọn kế hoạch trong registry hợp lệ; kế hoạch được kiểm tra trước khi thực thi.

### R4-T01-S03

Một phiên tự kết thúc trong budget; log stop/cancel và số gọi model.

## Phụ thuộc cần đối chiếu

[R0-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/llm-backend.md), [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md), [R2-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/combined-run-and-cleanup.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
