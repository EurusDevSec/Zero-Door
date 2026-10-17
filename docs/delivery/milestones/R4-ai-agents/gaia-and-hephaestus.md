# Issue — Gaia và Hephaestus có quyết định LLM được giới hạn

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-20](https://linear.app/zero-door/issue/ZER-20/gaia-va-hephaestus-co-quyet-djinh-llm-djuoc-gioi-han). Nguồn đối chiếu: `R4-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T02-S01 | Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM. | [ZER-49](https://linear.app/zero-door/issue/ZER-49/noi-evidence-vao-chan-djoan-llm-cua-gaia) |
| R4-T02-S02 | Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục. | [ZER-50](https://linear.app/zero-door/issue/ZER-50/noi-quyet-djinh-llm-cua-hephaestus-qua-policy-guard) |
| R4-T02-S03 | Thử JSON sai, timeout, 429 và thiếu bằng chứng; fallback được đánh dấu. | AC của [ZER-20](https://linear.app/zero-door/issue/ZER-20/gaia-va-hephaestus-co-quyet-djinh-llm-djuoc-gioi-han) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T02-S01

Incident có metric/log đầu vào, diagnosis và latency; MTTD không bị định nghĩa lại.

### R4-T02-S02

Trace đề xuất, action, lý do chấp nhận/từ chối, decision latency và probe kết quả; không chữa thừa ở case lành tính.

### R4-T02-S03

Các trường hợp lỗi không tạo action ngoài allowlist và không bị ghi nhãn AI thành công.

## Phụ thuộc cần đối chiếu

[R4-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/llm-adapter-and-nemesis.md) (mục nguồn trong ghi chú), [R3-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/block-ip-and-rollback.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
