# Issue — Chốt kỹ thuật và bàn giao cho Hòa

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-ban-giao-cho-hoa). Nguồn đối chiếu: `R5-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T03-S01 | Sửa lỗi cốt lõi phát hiện trong pilot và chạy lại phép thử bị ảnh hưởng. | AC của [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-ban-giao-cho-hoa) |
| R5-T03-S02 | Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ. | [ZER-55](https://linear.app/zero-door/issue/ZER-55/djong-bang-ban-dung-runbook-va-dataset-manifest) |
| R5-T03-S03 | Bàn giao sơ đồ, protocol, câu hỏi/claim, bảng/plot và giới hạn kết quả cho Hòa. | AC của [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-ban-giao-cho-hoa) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T03-S01

Danh sách lỗi, bản sửa và kết quả kiểm chứng; nếu chưa qua, gate G5 chưa đóng.

### R5-T03-S02

Phiên bản dựng lại được; dataset manifest có method version/hash/run IDs, legacy/pilot/formal tách riêng; analysis đọc danh sách dữ liệu đã khóa thay vì gộp mọi CSV. Run lỗi/loại khỏi phân tích có lý do theo protocol, vẫn được lưu và thống kê.

### R5-T03-S03

Ma trận RQ → cấu hình → metric → claim khớp log/code; source ledger/path tra được, phân biệt lịch sử với bằng chứng mới. Giữ vấn đề/KPI chưa đạt và ghi kết quả xử lý H01–H08 còn mở.

## Phụ thuộc cần đối chiếu

[R5-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/pilot-and-war-game.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
