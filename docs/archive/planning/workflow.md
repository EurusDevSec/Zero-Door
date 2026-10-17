# Cách làm việc và cập nhật tiến độ

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/README.md) · [Việc tiếp theo](R:/_Projects/Eurus_Workspace/zero_door/docs/recovery/NOW.md)

## Mở một phiên làm việc

1. Đọc NOW.md rồi mở đúng một file task được giao; đọc SCOPE.md và tài liệu tham khảo liên quan khi cần. Không nạp lại mọi task/handoff vào context.
2. Kiểm tra HEAD/dirty thực tế, phụ thuộc, owner và phạm vi thao tác. File task là nguồn chuẩn cho status, due, evidence; phase giữ kết quả gate. NOW chỉ sắp thứ tự việc, không là sổ trạng thái thứ hai.
3. Khi kết thúc, cập nhật subtask, bằng chứng/ngày thực tế, bàn giao và bước tiếp theo trong task. Chỉ cập nhật NOW nếu thứ tự/việc đang làm thay đổi. Không copy lại toàn task sang NOW hoặc tạo thêm roadmap.

## Quy ước đặt tên và nơi lưu

- Kế hoạch đang làm không đặt ngày ở đầu tên. Phase: R0-foundations/...; task: R0-T02-local-lab.md. Tìm theo ID hoặc chức năng đều được.
- Subtask dùng ID R0-T02-S01 ngay trong file task, không tạo 92 file con. Giữ nguyên ID để truy vết audit/evidence.
- Evidence và thiết kế mới nằm ở đường dẫn được khóa trong task; thêm timestamp bên trong nội dung hoặc tên run khi cần provenance. Handoff/audit cũ giữ nguyên đường dẫn để không mất lịch sử.
- Snapshot roadmap cũ ở archive, không cập nhật tiến độ. README chỉ dẫn đường; NOW chỉ ghi việc ưu tiên; task ghi trạng thái; phase ghi gate; SCOPE ghi cam kết; reference chứa phương pháp/quyết định.

### Phân công, năng lực và cách đánh giá

- **Hoàng:** quyết định scope, kỹ thuật, provider/credential/ngân sách và thay đổi lab có hệ quả; đối chiếu dữ liệu và kết luận. Không mặc định phải tự gõ mọi lệnh. Agent được làm các thao tác đã nằm trong phạm vi được giao; quyền thiếu thật thì báo chính xác, không xin lại quyền chung cho mọi lần đọc.
- **Codex:** giữ roadmap và traceability, chuẩn bị inventory/baseline, chủ trì probe/runner/analysis/dashboard và một số task LLM/integration; review phần Claude theo bảng task. Không đồng nhất vai trò điều phối với việc mặc nhiên sửa toàn repo.
- **Claude Code:** hydration đã đạt; chủ trì bản nháp event contract và các task agent/worker/healer được ghi dưới đây, review phần Codex. Đây là phân công dự kiến trong kế hoạch, chưa gửi lệnh hoặc mở phiên thực hiện từ lượt cập nhật này. Không chọn Claude làm backend runtime chỉ vì dùng Claude Code để phát triển.
- **Hòa:** chủ trì bản Word và paper, tài liệu tham khảo, template, hồ sơ; Hoàng duyệt phần kỹ thuật và kết quả. Không tự giả định số giờ làm của Hòa.
- **Thầy/trường/nơi nhận bài:** xác nhận đợt nhận bài, phản biện, chấp nhận đăng và lịch nghiệm thu. Đây là phụ thuộc bên ngoài, không thể đóng bằng một mốc tự đặt.

| Cửa sổ hiện hành | Công sức cần bố trí | Đầu ra ưu tiên |
| --- | --- | --- |
| 2026-10-17 → 2026-10-18 | Chưa xác nhận quỹ giờ mới | Inventory, baseline, draft contract và ma trận yêu cầu |
| 2026-10-19 → 2026-10-25 | Ước lượng lại khi có lab và contract | G0/G1, ba vector, scale và bước block/rollback |
| 2026-10-26 → 2026-10-31 | Cần xác nhận đủ thời gian code, review, máy chạy và giám sát | G3/G4, pilot tích hợp, protocol, War Game và bàn giao G5 |
| 2026-11-01 → 2026-12-31 | Không kế thừa tự động giả định tăng giờ tháng 10 | Formal data, paper, phản biện và hồ sơ theo lịch thực tế |

**Giả định 30h + 3h dự phòng của lịch 09/10 đã được thay thế; không coi phần thời gian đã qua là công sức đã thực hiện hoặc vẫn còn sẵn.** Trước khi mở task mã, owner ước lượng riêng giờ thực hiện, review, tương tác Hoàng và thời gian máy chạy; cập nhật sau đầu ra đầu tiên. Lịch 17/10 là lịch mục tiêu nhiều phụ thuộc, chưa là dự báo hoàn thành có kiểm chứng. Không hứa cuối tháng chỉ vì có hai công cụ AI. R0-T04-S02 phải kiểm tra khả năng làm B3; R5-T02-S01 phải kiểm lại số lượt và thời lượng. Thiếu nguồn lực thì bỏ phần mở rộng/claim chưa đủ bằng chứng trước, giữ mọi cam kết gốc và ghi tác động đến mốc 31/10/14/11.

**Quy tắc phối hợp:** mỗi task mở có base HEAD, dirty snapshot, owner, người review và allowlist đường dẫn cụ thể, kể cả file mới/test/probe/schema. Chỉ một bên ghi/Git mutation trong một checkout tại một thời điểm; bên kia có thể đọc hoặc chuẩn bị phương án. Các cửa sổ chồng ngày là cơ hội xen kẽ theo bàn giao, không mặc định cho hai phiên cùng ghi. Nếu muốn thực thi đồng thời, chốt worktree/branch riêng và điểm tích hợp trước; lượt cập nhật này chưa tạo worktree hoặc branch. Không `git add .`, không đụng thay đổi ngoài task; commit/push không tự được cấp quyền bởi bảng lịch.

Thời gian máy chạy thực nghiệm được ghi riêng với giờ thao tác. War Game 4h cần budget, điều kiện dừng và bố trí giám sát đã chốt, không được mặc định là 4h không cần người theo dõi. Nếu cần tăng công sức hoặc kéo dài đo để đủ độ lặp, ghi rõ tác động đến lịch; giảm phần mở rộng trước, giữ yêu cầu nghiên cứu và tính trung thực dữ liệu.

**Luồng trạng thái:** TODO → READY → IN_PROGRESS → REVIEW → DONE; dùng BLOCKED khi thiếu đầu vào bắt buộc và WAIT_EXTERNAL khi chờ phản hồi bên ngoài. READY cho bước triển khai đòi hỏi các phụ thuộc đã DONE và có bằng chứng; READY không có nghĩa đã bắt đầu hoặc được tự mở rộng phạm vi. Riêng R1-T01-S01 có thể soạn bản nháp trước các phụ thuộc để lấy review; chốt schema/DONE vẫn chờ R0-T01 và R0-T04-S03. Tương tự có thể đọc nguồn/thiết kế trước, không đóng tích hợp/runtime bằng draft. Không phải mọi task đều chờ cả phase trước đóng gate; thực nghiệm chính thức R6-T02 bắt buộc G5 PASS. REVIEW có artifact còn chờ kiểm chứng; không chuyển DONE chỉ vì đến hạn hoặc mã chạy không lỗi.

**Đóng subtask:** điền trạng thái, ngày hoàn thành thực tế và link bằng chứng ở ô cuối. Bằng chứng đề xuất lưu dưới docs/evidence/<ID>/ hoặc trỏ tới artifact hiện có; thư mục này chưa được tạo trong lượt lập lịch. Mỗi log/dataset cần run_id, version cấu hình/code/model và phép tính liên quan; dùng commit khi đã có commit thật. Không ghi key/token vào bằng chứng. Với việc có điều kiện như vòng phản biện tiếp theo, chỉ đóng khi đã xử lý hoặc có xác nhận điều kiện đó không phát sinh.

**Đóng task/phase:** task DONE khi mọi subtask bắt buộc đã DONE; phase qua gate khi các task của phase đủ bằng chứng và điều kiện gate được kiểm chứng PASS. Tiến độ công việc tính theo số subtask đã DONE/tổng subtask bắt buộc; con số này không đại diện cho độ chính xác khoa học, KPI hay điểm nghiệm thu. G5 có thể bàn giao phiên bản kỹ thuật với kết quả pilot chưa đạt KPI, nhưng phải mở task khắc phục và chưa coi nghiên cứu hoàn tất. G7 còn phải đối chiếu toàn bộ tiêu chí/sản phẩm đã đăng ký.

**Chậm tiến độ:** giữ due gốc, thêm due điều chỉnh, lý do, owner và task bị ảnh hưởng. Khi task trên đường găng chậm ≥1 ngày hoặc mất điều kiện qua gate, đánh giá lại các task phụ thuộc ngay; không kéo ngày âm thầm. Task phát sinh mang hậu tố bổ sung của task cha và phải có due/bằng chứng như các task dưới đây.

**Review nội bộ điều chỉnh:** 20 phút lúc **20:30** các ngày **2026-10-18, 2026-10-20, 2026-10-23, 2026-10-25, 2026-10-27, 2026-10-29**; review G5 lúc **20:30 ngày 2026-10-31**. Mốc 13/10 và 16/10 thuộc lịch gốc, không ghi đã diễn ra. Review nhìn vào subtask quá hạn điều chỉnh, blocker, evidence và dự báo gate sau. Sau mỗi phiên kỹ thuật cập nhật trạng thái/ngày thực tế/link và việc đầu tiên của phiên sau. Đây là lịch nội bộ, chưa tạo automation hoặc nhắn ai.

## Bàn giao ngắn

Ghi trong task: ai làm; base HEAD/dirty; file thay đổi; kiểm tra đã chạy và kết quả; điều chưa chứng minh; blocker; bước tiếp theo. Người review ghi kết luận và bằng chứng ngay tại đó. Không yêu cầu Hoàng lặp lại bối cảnh đã có. Không báo runtime pass từ static check, hoặc DONE từ một lời kể chưa đối chiếu.
