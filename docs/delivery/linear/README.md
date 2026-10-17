# Linear Zero Door — Kết nối và mapping

[Delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md) · [Import / receipt](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/import.md) · [Mapping](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/mapping.json) · [Mẫu issue](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/issue-template.md)

**Project đã thiết lập:** [ZERO DOOR — Nghiên cứu và nghiệm thu](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039), mã `P-ZER-1`, ID `f6343559-080f-465f-aa7a-eda6074de51f`. Dùng project này, không tạo lại khi chuyển phiên.

## Định tuyến cố định

| Workspace | Connection | Quy tắc |
| --- | --- | --- |
| `zero-door` — ZERO DOOR | MCP `linear_zero_door` | Kiểm URL `linear.app/zero-door/` và team/project ID trước khi ghi |
| `eurusdevsec` — S-cool | Linear connector của Apps đã có | Giữ riêng; không dùng metadata S-cool thay cho ZERO DOOR |

Dùng lại connection đã lưu, không `mcp add`, tạo server trùng hoặc đổi OAuth mỗi lần đổi project. Chỉ workspace mới cần setup riêng lần đầu; quyền hết hạn/thu hồi thì xử lý đúng connection. Thiếu tool trong phiên cũ thì nạp lại client trước. Codex và Claude Code có cấu hình/auth riêng; Claude không tự thừa hưởng auth Codex. Không lưu token vào repo.

## Read-back sau import — 17/10/2026, 14:52:40 UTC

- Workspace đúng `linear.app/zero-door/`; team Zero-Door, key ZER, ID `865d41a7-ef26-474c-a9f8-36e781569fc8`. Hoàng và Hòa/Hoa8001 active, thuộc team; IDs đã xác minh nằm trong mapping, không suy thành assignment.
- Đã tạo/read-back đúng project trên, **8 milestone, 27 issue chính và 34 sub-issue**. Trước import project list rỗng; không còn dùng kết quả cũ đó để kết luận hiện chưa có project.
- Đọc đủ 61 body/AC, cha–con và milestone: khớp. Đủ 92 mục yêu cầu nguồn; 80 prerequisite relations khớp hai chiều, DAG không có chu trình kể cả hoàn tất con → cha. Project có đúng 61 issue/sub-issue, không duplicate.
- Mapping là `APPLIED_VERIFIED`. Ba sub-issue có điều kiện chưa tạo; yêu cầu vẫn ở AC issue cha. Bốn issue onboarding ZER-1…ZER-4 ngoài project giữ nguyên.
- Chính sách lúc tạo: Backlog, chưa gán người, đặt due/estimate/priority/cycle hoặc backdate Done. Đây là receipt lần nhập, **trạng thái sống đọc Linear**. Không sửa workflow, template hoặc label.
- Lệnh tạo project đầu lỗi transport; đọc lại xác nhận chưa tạo rồi retry thành công. Không có lỗi đối tượng còn tồn hoặc project trùng. Không cần đổi OAuth. Truy vấn quá nhiều nested fields cũng có thể lỗi complexity; dùng fields tối thiểu trước.

Các lần sau đọc project/issues/bodies/relations trước cập nhật, reuse IDs đã mapping. Không gửi Slack, chạy lab/LLM hoặc Git publication chỉ vì tracking đã sẵn sàng. Nơi evidence dùng chung, provider/chi phí, metadata chưa chốt và các điều kiện Ready/thực thi tiếp tục xử lý trong issue tương ứng.

Mapping giữ alias/ID/URL, nguồn và receipt, không copy live state. Ready/Done và QA theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); bổ sung/resume theo import.md. Chưa có artifact nghiên cứu mới được nghiệm thu trong lần thiết lập.

Canonical template: [Linear Project Kit](R:/_Dev_tools/obsidian/oBsidianFolder/Eurus_Vault/99_System/01_Templates/Linear_Project_Kit/00_CANONICAL_ENTRYPOINT.md), v1.0; đã đọc đủ năm file theo thứ tự, không sửa master. Kết nối chính thức: [Linear MCP](https://linear.app/docs/mcp#faq), [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp).
