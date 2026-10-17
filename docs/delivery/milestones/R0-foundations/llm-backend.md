# Issue — Xác nhận một backend LLM thật

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that). Nguồn đối chiếu: `R0-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T03-S01 | Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy. | [ZER-36](https://linear.app/zero-door/issue/ZER-36/chon-backend-llm-va-gioi-han-su-dung) |
| R0-T03-S02 | Gọi LLM bằng đầu vào nghiên cứu và kiểm tra đầu ra theo schema. | AC của [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that) |
| R0-T03-S03 | Thử timeout, retry có giới hạn và fallback; ghi rõ khi dùng RULES thay AI. | AC của [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T03-S01

Quyết định provider có căn cứ và cấu hình giới hạn; không suy ra quyền API từ credit Azure.

### R0-T03-S02

Bằng chứng lượt gọi mới có timestamp/run_id, request ID khi backend hỗ trợ, tên/phiên bản model, latency/usage khả dụng và kết quả che bí mật; ghi trường không được provider trả. SDK/manifest/evaluation_report không thay log lượt gọi.

### R0-T03-S03

Log tình huống lỗi và kiểm chứng fallback không bị ghi nhãn là quyết định LLM.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
