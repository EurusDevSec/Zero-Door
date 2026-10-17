# Phạm vi và tiêu chí nghiên cứu

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Phạm vi đã được người dùng chốt

- Bản thuyết minh đã cung cấp là bản đăng ký chính thức, không có bản điều chỉnh khác. Người dùng xác nhận thầy đã cho đổi sang Python/Go và Google Online Boutique được đề xuất từ ban đầu. Không yêu cầu quay lại Java/Spring AI chỉ để khớp tài liệu cũ; ghi rõ lựa chọn được xác nhận này trong báo cáo.
- **Nguồn thời hạn:** DOCX được cung cấp ghi thời gian từ tháng 01 đến tháng 06/2026, ngày trên văn bản 04/01/2026; hạn 31/12/2026 là xác nhận mới nhất của Hoàng với Codex. Giữ lịch tháng 12 để điều phối, đồng thời ghi khoảng trống nguồn giải thích khác biệt tại R0-T01-S03 và đối chiếu hồ sơ tại R7-T02-S05. Không coi ngày trên tài liệu là ngày ký/nộp/duyệt đã được chứng minh, cũng không tự kết luận có hay không có gia hạn.
- Vẫn phải hoàn thành SQL Injection, DDoS tầng ứng dụng, Resource Exhaustion; scale up/down, block IP và rollback; MTTD <60s, MTTR <2–3 phút, uptime ≥99,9% theo phạm vi thực nghiệm đã định nghĩa.
- Kubernetes phải có **tối thiểu 5 microservices mẫu** theo P104 của bản trích thuyết minh; lab cần chứng minh luồng nghiệp vụ hoạt động, không chỉ đủ số pod.
- **Xác nhận hiện hành 17/10:** Hoàng quyết định trước hết vẫn làm cả ba vector dù đã trao đổi việc thầy khuyên thu hẹp và chọn SQLi. Không dùng SQLi-only làm scope hiện tại, cũng không tự ghi thầy vừa phê duyệt lại cả ba. Phản hồi của thầy về block IP được phản ánh vào R3-T02: phải chặn được nguồn thay vì phát hiện/phục hồi lặp mãi.
- **Đối chiếu DOCX trực tiếp ngày 17/10:** ngoài KPI tổng, P179 có CPU của target app >80%, P187 có phản ứng <1 phút; P100 yêu cầu cô lập và hồi phục không cần can thiệp, P109 dashboard thời gian thực, P176 tích hợp LLM; sản phẩm gồm source/manifests, video, bảng đo, báo cáo, slide/poster. Các mốc phản ứng/phát hiện/hồi phục và mẫu số CPU phải được định nghĩa riêng tại R0-T01-S02/R1, không tự đồng nhất. Xem [bản trích có hash/vị trí đoạn](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md).
- Bài cần được chấp nhận đăng trong kỷ yếu trường trước nghiệm thu. Tên kỷ yếu, thông báo nhận bài, mẫu bài và lịch nhận bài chưa có; người dùng chọn chốt sau. Các mốc nộp bài dưới đây là mục tiêu nội bộ, không phải lịch do trường xác nhận.
- Người đang trao đổi là **Lê Văn Hoàng**, phụ trách kỹ thuật. **Nguyễn Ngọc Hòa** phụ trách báo cáo Word. Nội dung và kết luận khoa học cần hai người cùng đối chiếu với dữ liệu và giảng viên hướng dẫn.
- Hoàng trước đây nói khoảng 10 giờ/tuần, sau đó ngày 17/10 muốn tăng cường làm việc có kiểm soát cho ZERO DOOR và Zero-D-Rift. Chưa có quỹ giờ mới được xác nhận; không tiếp tục coi “30h còn lại trong tháng” của lịch 09/10 là nguồn lực hiện có. Lịch mới là mục tiêu theo phụ thuộc, không phải cam kết đủ người/giờ. Codex/Claude hỗ trợ thực hiện và review theo issue; Hoàng giữ quyết định kỹ thuật, provider/chi phí và các thay đổi lab có hệ quả.
- Cloud cũ đã tắt. Hạ tầng cloud và dùng credit Azure cho compute được hoãn; lab chạy trên máy hiện tại. Có Azure for Students khoảng 100 USD theo người dùng, nhưng chưa kiểm tra số dư, quyền model, quota hoặc endpoint của subscription.

[Rà soát nguồn và dữ liệu](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-research-alignment-audit.md) là căn cứ cho các gói sửa. Những nhận xét trong bản rà soát về việc phải xác nhận đổi stack đã được giải quyết bằng thông tin trực tiếp của người dùng ở trên. Các phát hiện về SQLi, rollback, telemetry và dữ liệu chưa thay đổi.

## Việc hoãn và thứ tự bắt đầu

Hoãn triển khai Azure compute/cloud cũ, SaaS đa khách hàng, framework agent lớn, RAG/vector DB, training/RL, nhiều LLM, so sánh cloud–local và viết lại Boutique. Không xem việc có credit là lý do mở rộng hạ tầng.

Đầu ra đầu tiên là **inventory/baseline ở R0 và bản nháp event contract ở R1** theo hàng đợi 17/10. Provider được chốt/test theo R0-T03; không buộc bản nháp contract hoặc mọi test rules chờ LLM. Sau contract review và preflight, mở issue mã với đường dẫn/test cụ thể, sửa phép đo/guard rồi vector/healer, sau đó AI và thực nghiệm đối chứng. Lượt lập kế hoạch này chỉ sửa tài liệu; chưa tạo artifact của hàng đợi, sửa ứng dụng, chạy lab/test/LLM, cài model hoặc tạo tài nguyên trả phí.

## Các mục tiêu thời gian đã ghi nhận

- **31/10/2026:** mục tiêu hoàn thành kỹ thuật/pilot; chưa có dự báo capacity chứng minh lịch chắc chắn đạt.
- **14/11/2026:** mục tiêu nội bộ nộp bản paper đầu, phụ thuộc nơi và đợt nhận bài; chưa là hạn trường công bố.
- **31/12/2026:** thời hạn Hoàng cung cấp; khác thời gian trong DOCX như đã ghi ở trên, còn phải đối chiếu hồ sơ có thẩm quyền.

Chi tiết lịch/assignment/status cũ chỉ ở [lịch sử](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/README.md). Lịch delivery sống thuộc Linear sau khi xác minh đúng project và được phép áp metadata. Repo giữ scope/tiêu chí nghiên cứu và bằng chứng; issue AC phải phù hợp các cam kết này, không tự thay scope. Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/README.md).
