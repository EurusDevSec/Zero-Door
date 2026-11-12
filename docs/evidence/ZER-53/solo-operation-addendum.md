# ZER-53 — Phụ lục vận hành BM bởi một người

Ngày 12/11/2026 (UTC+7). **Phương án do Hoàng chọn; chờ review kỹ thuật trước formal. FORMAL_HOLD.**

Áp dụng cùng [protocol v3](protocol.md), SHA-256 `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8`. Không sửa byte của bản đã khóa. Khi phụ lục được khóa, manifest chạy phải pin cả hai hash; không gọi một run chỉ pin protocol gốc là đã tuân thủ phụ lục.

## 1. Quyết định và phạm vi thay thế

Hoàng chọn tự vận hành trên laptop hiện tại: Hoàng trực BM; harness tự sinh, giấu và niêm phong lịch/onset; scorer tính theo quy tắc đã khóa; Codex/Claude đối chiếu bằng chứng sau chạy. Không yêu cầu bổ sung một người trực alert hay một người chấm độc lập thứ hai. Phương án này nối tiếp ZER-8 §13 ngày 19/10/2026: Hoàng trực BM, che thứ tự/onset, không tuyên bố mù hoàn toàn.

Sau review và khóa phụ lục, thay yêu cầu Hòa rà từng trial/người chấm tách vai ở câu cuối mục BM (§2) và hàng readiness BM (§5) bằng cách phân vai dưới đây. Không sửa yêu cầu BM phải có thao tác của người thật. Không biến thao tác Codex hoặc quyết định của scorer thành quyết định BM.

## 2. Vai và thời điểm được đọc bằng chứng

| Vai | Người/thành phần | Quyền trong lúc cohort đang chạy |
| --- | --- | --- |
| Vận hành BM | Hoàng | Chỉ mặt O và action menu/runbook cố định; quyết định và thao tác thật |
| Điều phối | Harness; Codex vận hành entry point | Tự sinh/seal lịch H, thực thi thứ tự đã khóa; không gợi ý thao tác BM từ H |
| Ghi ground truth/probe | Writer H tự động, tách UID/token khỏi O/operator | Ghi effect/oracle/probe, không xuất nhãn/seed/onset vào O |
| Chấm chỉ số | Scorer đã pin | Ghép H/O đã seal, theo đúng mẫu số và nhãn thiếu bằng chứng; không tự thay tiêu chí |
| Đối chiếu kỹ thuật | Codex/Claude sau cohort | Kiểm raw/hash/join/audit và chạy lại scorer; ghi ai thực sự review và có phải người viết/chạy hay không |

Trong lúc còn trial chưa khởi chạy, không hiển thị lịch tiếp theo, H/S, đáp án, kết quả chấm trial trước hoặc vị trí block trên console BM. Export H/S cho đối chiếu chỉ mở sau khi cohort kết thúc hoặc đã tuyên bố kết thúc sớm và mọi trial còn lại là NOT_RUN. Không quay lại chạy các trial NOT_RUN sau khi đã mở H/S.

Giữ tách quyền process/token/filesystem H/O/evaluator đã thiết kế. Cùng một người sở hữu quyền quản trị laptop có thể vượt tách quyền ứng dụng; không tuyên bố đã chứng minh họ không đọc H qua mọi đường Windows. Lưu phạm vi audit thực tế và phần không quan sát được. Nếu dữ liệu cho thấy lịch/nhãn bị đọc trong lúc chạy, gắn cờ leak theo protocol; không sửa hay bỏ raw.

## 3. Chấm và mức độc lập được công bố

M1 chính vẫn là B2 − B1/C5 ghép theo block, enum và tham số trước guard. Giữ nguyên 40 trial, thứ tự, seed/onset, các cap/budget, KPI, xử lý timeout/UNKNOWN, M12 và guard tài nguyên. Không thay bộ chấm bằng nhận xét chủ quan của người vận hành.

BM giữ đủ 10 lượt và chỉ báo mô tả; lượt BM thứ hai của mỗi block luôn mang UNBLINDED_BY_DESIGN. Không đưa BM vào so sánh ghép cặp chính, không dùng để kết luận hiệu quả che lịch hoặc ưu thế so với một operator độc lập.

Báo cáo phương pháp và dataset phải ghi: **một người vận hành; chấm tự động theo quy tắc đăng ký trước; hậu kiểm kỹ thuật bằng bằng chứng; không có người chấm độc lập thứ hai và không có đánh giá mù độc lập ở mức con người**. Phân biệt reviewer thực sự độc lập với tự kiểm của người viết/chạy. Chỉ ghi Claude đã review khi có receipt/review thật.

## 4. Điều kiện readiness vẫn cần chứng minh

- Console chỉ hiện O và menu cố định, không đếm ngược onset hoặc hiển thị case/block/H/S.
- Ghi alert đã hiển thị và thời điểm người vận hành nhận/xác nhận; thiếu mốc hiển thị thì phần M10 tương ứng là UNKNOWN.
- Ghi DECISION từ operator_console với decision_source MANUAL trước thực thi; giữ cả quyết định sai/ABSTAIN/không phản hồi.
- Có thao tác thật, xác nhận API và readback hậu điều kiện nếu chọn action. NO_ACTION không được biến thành một action đã thực thi.
- Probe/clock/cleanup/audit bề mặt vẫn phải có raw; thiếu proof thì HOLD phần liên quan.
- Trước formal, khóa phụ lục đã review, nguồn scorer và artifact audit. Phụ lục không tự chứng minh BM đã chạy, B2/C5 đạt tải, detector trigger trên năm variant hoặc M12 được xác minh.

## 5. Giới hạn nghiệm thu

Đây là điều chỉnh phương pháp do chủ dự án lựa chọn trước dữ liệu formal. Không phải văn bản xác nhận của trường hay bảo đảm hội đồng sẽ chấp nhận. Kết luận giới hạn theo dữ liệu thực tế; giữ nguyên cam kết nguồn và ghi rõ phần chưa đáp ứng.
