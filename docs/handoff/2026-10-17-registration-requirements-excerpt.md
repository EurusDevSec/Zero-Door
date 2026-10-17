# Trích yêu cầu nghiên cứu từ DOCX gốc — 17/10/2026

Người trích: Codex. Đọc trực tiếp đúng file Hoàng cung cấp bằng ZIP/XML, không quét Downloads hoặc sửa DOCX. Chỉ trích các đoạn liên quan yêu cầu, thời gian, sản phẩm; không trích thông tin liên hệ, mã sinh viên, chữ ký hay hồ sơ cá nhân.

Nguồn: `C:\Users\ACER\Downloads\HĐ5_Nguyễn Ngọc Hòa_Ứng dụng kiến trúc Multi-Agent AI và Kỹ thuật Chaos Engineering xây dựng cơ chế Tự phục hồi cho Hệ thống Microservices.docx`.

SHA-256 của DOCX: `0FAA8794F6B5175BE94EB9F26DB2A4A15A588A361FE25D33901D20FF241CD964`.

Vị trí Pn là đoạn thứ n, đếm từ 1 theo XPath `//w:body//w:p` trong `word/document.xml`, gồm các đoạn trong bảng và đoạn rỗng. Đây không phải số trang của Word. Nối các text run trong từng đoạn, giữ nội dung, không tự sửa câu chữ.

Claude dùng bản này cần ghi: “Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX.” Không gán quyền truy cập của Codex cho phiên Claude.

## Đoạn trích

- **P35:** Thành phố Hồ Chí Minh, ngày  04 tháng 01 năm 2026
- **P55:** 4. Thời gian thực hiện: 6 tháng
- **P56:**             Từ tháng 01 năm  2026 đến tháng  06 năm 2026
- **P98:** 9. Mục tiêu đề tài:
- **P100:** Mục tiêu tổng quát: Xây dựng thành công hệ thống DevSecOps tự trị trên nền tảng Kubernetes, bao gồm 3 Agent AI (Nemesis, Hephaestus, Gaia) có khả năng tự phát hiện tấn công, cô lập mối nguy và tự phục hồi dịch vụ mà không cần con người can thiệp.
- **P102:** Mục tiêu cụ thể (KPI):
- **P104:** Kiến trúc: Triển khai thành công Cluster Kubernetes với tối thiểu 5 microservices mẫu.
- **P105:** Tác tử Nemesis (Tấn công): Thực hiện thành công ít nhất 3 loại tấn công tự động: SQL Injection, DDoS (Application Layer), và Resource Exhaustion.
- **P106:** Tác tử Hephaestus (Phòng thủ): Tự động thực hiện các hành động: Scale up/down, Block IP, Rollback phiên bản lỗi.
- **P107:** Hiệu năng tự phục hồi: Thời gian phát hiện sự cố (MTTD) < 1 phút; Thời gian phục hồi dịch vụ (MTTR) < 2-3 phút.
- **P108:** Độ sẵn sàng: Hệ thống mục tiêu duy trì Uptime ≥ 99.9% dưới áp lực tấn công liên tục của Nemesis.
- **P109:** Minh bạch: Dashboard (Gaia) hiển thị trực quan trạng thái "Chiến tranh AI" (Attack vs Defense logs) thời gian thực.
- **P173:** Tháng 03/2026
- **P174:** - Phát triển Agent Nemesis (Module tấn công).
- **P176:** - Tích hợp LLM để sinh kịch bản tấn công.
- **P177:** - Nemesis thực hiện được SQL Injection và Stress Test.
- **P179:** - KPI: CPU target app tăng > 80%.
- **P181:** Tháng 04/2026
- **P182:** - Phát triển Agent Hephaestus (Module phòng thủ).
- **P184:** - Lập trình logic tự động Scale và Block IP.
- **P185:** - Hephaestus tự động Scale pod khi CPU cao.
- **P187:** - KPI: Thời gian phản ứng < 1 phút.
- **P189:** Tháng 05/2026
- **P190:** - Tích hợp toàn hệ thống (War Games).
- **P192:** - Chạy thử nghiệm và đo đếm thông số.
- **P193:** - Video demo quá trình Tấn công - Tự phục hồi.
- **P195:** - Bảng số liệu MTTR/MTTD.
- **P197:** Tháng 06/2026
- **P198:** - Viết báo cáo tổng kết.
- **P200:** - Đóng gói sản phẩm.
- **P201:** - Báo cáo toàn văn.
- **P203:** - Slide thuyết trình, Poster.
- **P206:** 13. Sản phẩm và khả năng ứng dụng:
- **P207:** 13.1. Danh mục sản phẩm bàn giao (Hồ sơ nghiệm thu)
- **P208:** Bộ mã nguồn (Source Code) đầy đủ của hệ thống Zero Door (Java Spring Boot).
- **P209:** File cấu hình Kubernetes (Manifests/Helm Charts).
- **P210:** Video Demo kịch bản tự phục hồi thực tế.
- **P211:** Báo cáo khoa học chi tiết.

## Phân biệt nguồn gốc và quyết định hiện hành

Các đoạn trên giữ nguyên yêu cầu và stack ghi trong DOCX. Hoàng đã xác nhận thầy cho đổi Java/Spring sang Python/Go; không coi P208 là yêu cầu quay lại Java. Hạn 31/12/2026 là xác nhận của Hoàng, khác khoảng tháng 01–06 ghi ở P55–P56. Ngày ở P35 không tự chứng minh ngày ký, nộp hoặc duyệt. Xem roadmap và phần B của hydration để đối chiếu các quyết định này; không sửa câu trích cho khớp kế hoạch hiện tại.
