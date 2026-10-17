# Issue — Chạy đầy đủ đường tấn công–phát hiện–hồi phục

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc). Nguồn đối chiếu: `R5-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T01-S01 | Chụp phiên bản image/config/model/prompt và workload của đợt tích hợp. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |
| R5-T01-S02 | Chạy từng vector qua toàn pipeline và đo bằng probe độc lập. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |
| R5-T01-S03 | Thử bad release, benign traffic, thất bại và cleanup. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T01-S01

Manifest/version/run metadata đủ dựng lại.

### R5-T01-S02

Ba incident có trace đầy đủ; không dùng /heal/trigger làm đường đo chính.

### R5-T01-S03

Mỗi tình huống có verdict và log; failure được giữ trong dữ liệu.

## Phụ thuộc cần đối chiếu

[R4-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/multi-agent-evidence.md), [R4-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/single-agent-baseline.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
