# Issue — Thống nhất hợp đồng sự kiện và lưu dấu vết

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet). Nguồn đối chiếu: `R1-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước soạn draft S01 chỉ ghi `docs/design/r1-event-contract.md`. Có thể soạn khi lab/LLM chưa sẵn sàng; khóa schema và nghiệm thu vẫn chờ phụ thuộc R0. S02/S03 chưa mở allowlist mã, test hoặc schema dùng chung.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T01-S01 | Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi. | [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi) |
| R1-T01-S02 | Truyền ID qua Kafka/HTTP và lưu sự kiện gốc phục vụ tái tính. | AC của [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet) |
| R1-T01-S03 | Tách ground truth/log điều khiển khỏi evidence dành cho bên chữa lỗi. | AC của [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T01-S01

Schema/version và ví dụ; mốc attack effect/detect/action/recovery/stop có nguồn ghi riêng. Terminal action SUCCESS/FAILED/PARTIAL được tách khỏi RECOVERY_VERIFIED.

### R1-T01-S02

Một chuỗi sự kiện xuyên thành phần; bản ghi bền vững có thể xuất và đối chiếu.

### R1-T01-S03

Phép thử kiểm tra prompt/query không lộ case label, attack command hoặc đáp án; ID trung tính vẫn truy vết được ở harness.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md), [R0-T04-S03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md) (mục nguồn trong ghi chú).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
