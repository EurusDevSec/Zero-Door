# Issue — Chứng minh vòng multi-agent và đối chứng RULES

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-21](https://linear.app/zero-door/issue/ZER-21/chung-minh-vong-multi-agent-va-djoi-chung-rules). Nguồn đối chiếu: `R4-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T03-S01 | Chạy một vòng có trace observation–decision–result cho cả ba agent. | AC của [ZER-21](https://linear.app/zero-door/issue/ZER-21/chung-minh-vong-multi-agent-va-djoi-chung-rules) |
| R4-T03-S02 | Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage. | [ZER-51](https://linear.app/zero-door/issue/ZER-51/pilot-djoi-chung-b0-b1-va-b2-cung-djieu-kien) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T03-S01

Trace có ID liên kết và backend/model thật; phân biệt rõ quyết định rule và LLM.

### R4-T03-S02

Bảng đối chứng controller/rules/multi-LLM; cùng evidence cho B1/B2, guard/probe/profile HPA cố định; không mặc định AI tốt hơn.

## Phụ thuộc cần đối chiếu

[R4-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/llm-adapter-and-nemesis.md), [R4-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/gaia-and-hephaestus.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md), [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
