# Phạm vi và tiêu chí nghiên cứu

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Quyết định hiện hành — SQLi-only, Hoàng xác nhận 28/10/2026

Hoàng yêu cầu **thu hẹp về một phương thức SQL Injection**, hoàn thành phần kỹ thuật và bộ báo cáo trong tuần này. Quyết định này **thay lựa chọn ba vector ngày 17/10**, quay về hướng thu hẹp mà Hoàng cho biết thầy đã khuyên trước đó. Nguồn là yêu cầu trực tiếp trong chat; chưa có văn bản điều chỉnh thuyết minh hay xác nhận mới của trường. Giữ bản đăng ký gốc và mọi khoảng trống tuân thủ; không ghi rằng đã hoàn thành ba vector.

### Phần bắt buộc của đợt bàn giao

- Dùng lại SQLi fixture/executor đã nghiệm thu ở ZER-13/41/42: dữ liệu giả, template cố định, private local profile, safe/benign controls. Không tạo payload hay mục tiêu mới.
- Chạy đường **SQLi effect → Gaia phát hiện → transport → Hephaestus containment → probe độc lập**. Chặn đúng nguồn đã chứng minh danh tính, giữ khách lành, kiểm TTL/gỡ chặn/cleanup và trạng thái lỗi. Containment không đồng nghĩa vá SQLi; availability Boutique và nghiệp vụ fixture báo riêng.
- Giữ ba tác tử và một backend LLM thật trong allowlist/guard, trace observation–decision–result, timeout/call budget, schema validation và fallback có nhãn. Mock hoặc API nhận lệnh không thay inference/action/recovery thật.
- Pilot và protocol chỉ cho SQLi + case lành tính C0, dùng control hiện có. Đối chứng B0/B1/B2 cùng workload/evidence/guard; BM theo cam kết/protocol. Không B3; bỏ claim RQ2 “chia vai trò tốt hơn single-agent”, cũng không suy từ một fixture thành năng lực chẩn đoán nhiều loại sự cố.
- Khóa số lặp/thứ tự/mẫu số/ngưỡng trước formal theo pilot, giữ toàn bộ failure/timeout/UNKNOWN và trace/cost. Bàn giao source/manifests/runbook/dataset, bảng/plot, bản paper/Word và video/slide/poster theo yêu cầu nơi nhận.

### Cắt công việc bằng issue hiện có

| Nhóm issue | Quyết định phạm vi, không phải bảng trạng thái sống |
| --- | --- |
| ZER-14/43/44/45, ZER-15 | HTTP flood, CPU/resource exhaustion, catalog nhiều sự cố và phối hợp ba vector chuyển **bổ sung**. Dừng ZER-43; không chạy phiên chẩn đoán 60 phút từng đề xuất. |
| ZER-16/18 | Giữ state machine, bounded retry/dedup/cooldown, lỗi/mất telemetry và restart liên quan SQLi. Scale up/down, HPA và ma trận nhiều replica/PodKill chuyển bổ sung. |
| ZER-17/46; ZER-47 | **Ưu tiên tiếp theo là ZER-46** block IP/TTL/benign cho SQLi. Bad release/known-good rollback ZER-47 chuyển bổ sung; không là prerequisite SQLi. |
| ZER-19/48, ZER-20/49/50, ZER-21/51 | Giữ LLM thật, guard/fallback và đối chứng trong phạm vi SQLi. Gỡ prerequisite ba-vector ZER-15 khỏi ZER-19; không bỏ contract SQLi/probe. |
| ZER-22 | Dùng nhánh quyết định không giữ claim RQ2 đã có trong AC; không xây B3. Review quyết định rồi nghiệm thu tài liệu phù hợp, không tự Done vì đổi scope. |
| ZER-23, ZER-24/52/53, ZER-25/55 | End-to-end SQLi, pilot/protocol và đóng băng/bàn giao. War Game4h ZER-54 chuyển bổ sung; run ngắn không thay PASS4h. |
| ZER-26/56/57, ZER-27/58/59, ZER-28/60 | Giữ method/related work, protocol, dữ liệu và bản bài; kết luận giới hạn SQLi, không claim ba vector/AI vượt trội khi thiếu bằng chứng. |
| ZER-30/61/62/63/64, ZER-31/65, ZER-29 | Giữ bộ sản phẩm, rehearsal và điều kiện hồ sơ/acceptance thật. Phản biện/chấp nhận đăng/hội đồng phụ thuộc bên ngoài, không phải việc thừa để xóa. |

Bảy issue chuyển phần bổ sung dùng trạng thái Linear **Canceled kèm lý do đổi scope**, giữ nguyên AC và bằng chứng, có thể mở lại chính issue cũ nếu còn thời gian. Không xóa code, artifact hay lịch sử; không đánh PASS các yêu cầu được loại. Các AC còn giữ nguyên yêu cầu evidence và guard. AC ba-vector/scale/rollback/War Game đã chuyển được giữ ở phần nguồn/lịch sử để không làm mất cam kết.

### Thời hạn và điều kiện dừng

“Tuần này” là mục tiêu nội bộ của Hoàng: hướng tới đóng băng kỹ thuật 31/10 và hoàn thiện bộ bàn giao trước hết tuần 01/11/2026, **chưa là dự báo chắc chắn hoặc lịch trường**. Làm từng issue một theo phụ thuộc; nhóm cha/con không phải hai lần triển khai. Tái sử dụng evidence đủ, không chạy lại chỉ để làm đẹp checkpoint. Không mở nhánh bổ sung trước khi đường SQLi và bộ bàn giao đã ổn, còn thời gian và được giao lại.

Ưu tiên kế tiếp: chuẩn bị/review gói ZER-46 từ IP/anti-spoof và fixture đã có; khóa exact scope trước code/runtime. Nếu lab nền cần thiết cho SQLi không đạt, dừng tại guard và chốt blocker/ảnh hưởng báo cáo; không quay lại chuỗi sửa DNS/CPU của ZER-43. Không có quyền runtime/model mới từ quyết định thu hẹp này.

**Không đổi số liệu để kịp hạn.** MTTD <60s, MTTR <2–3 phút và uptime≥99,9% vẫn là ngưỡng nguồn khi áp dụng; báo kết quả/mẫu số/cửa sổ thật và phần chưa đạt. CPU target>80%, scale up/down, rollback và ba-vector thuộc cam kết gốc nay ngoài đợt SQLi: ghi “chưa đáp ứng trong phạm vi thu hẹp”, không N/A như thể trường đã miễn. Chỉ kết luận nghiên cứu trong phạm vi mới; bản nộp sẵn sàng, bài được chấp nhận và đề tài được nghiệm thu là ba mốc riêng.

## Cam kết và quyết định nguồn — đối chiếu theo quyết định 28/10 ở trên

- Bản thuyết minh đã cung cấp là bản đăng ký chính thức, không có bản điều chỉnh khác. Người dùng xác nhận thầy đã cho đổi sang Python/Go và Google Online Boutique được đề xuất từ ban đầu. Không yêu cầu quay lại Java/Spring AI chỉ để khớp tài liệu cũ; ghi rõ lựa chọn được xác nhận này trong báo cáo.
- **Nguồn thời hạn:** DOCX được cung cấp ghi thời gian từ tháng 01 đến tháng 06/2026, ngày trên văn bản 04/01/2026; hạn 31/12/2026 là xác nhận mới nhất của Hoàng với Codex. Giữ lịch tháng 12 để điều phối, đồng thời ghi khoảng trống nguồn giải thích khác biệt tại R0-T01-S03 và đối chiếu hồ sơ tại R7-T02-S05. Không coi ngày trên tài liệu là ngày ký/nộp/duyệt đã được chứng minh, cũng không tự kết luận có hay không có gia hạn.
- **Cam kết đăng ký gốc, không phải hàng đợi ba-vector hiện hành:** SQL Injection, DDoS tầng ứng dụng, Resource Exhaustion; scale up/down, block IP và rollback; MTTD <60s, MTTR <2–3 phút, uptime ≥99,9%. Các phần thu hẹp và khoảng trống được ghi ở quyết định 28/10; không xóa yêu cầu gốc khỏi đối chiếu hồ sơ.
- Kubernetes phải có **tối thiểu 5 microservices mẫu** theo P104 của bản trích thuyết minh; lab cần chứng minh luồng nghiệp vụ hoạt động, không chỉ đủ số pod.
- **Quyết định lịch sử 17/10, đã được thay thế ngày 28/10:** Hoàng quyết định trước hết vẫn làm cả ba vector dù đã trao đổi việc thầy khuyên thu hẹp và chọn SQLi. Tại thời điểm đó chưa dùng SQLi-only; từ 28/10 SQLi-only là phạm vi thực hiện hiện hành. Không tự ghi thầy vừa phê duyệt lại cả ba hoặc đã sửa hồ sơ. Phản hồi của thầy về block IP được phản ánh vào R3-T02: phải chặn được nguồn thay vì phát hiện/phục hồi lặp mãi.
- **Đối chiếu DOCX trực tiếp ngày 17/10:** ngoài KPI tổng, P179 có CPU của target app >80%, P187 có phản ứng <1 phút; P100 yêu cầu cô lập và hồi phục không cần can thiệp, P109 dashboard thời gian thực, P176 tích hợp LLM; sản phẩm gồm source/manifests, video, bảng đo, báo cáo, slide/poster. Các mốc phản ứng/phát hiện/hồi phục và mẫu số CPU phải được định nghĩa riêng tại R0-T01-S02/R1, không tự đồng nhất. Xem [bản trích có hash/vị trí đoạn](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md).
- Bài cần được chấp nhận đăng trong kỷ yếu trường trước nghiệm thu. Tên kỷ yếu, thông báo nhận bài, mẫu bài và lịch nhận bài chưa có; người dùng chọn chốt sau. Các mốc nộp bài dưới đây là mục tiêu nội bộ, không phải lịch do trường xác nhận.
- Người đang trao đổi là **Lê Văn Hoàng**, phụ trách kỹ thuật. **Nguyễn Ngọc Hòa** phụ trách báo cáo Word. Nội dung và kết luận khoa học cần hai người cùng đối chiếu với dữ liệu và giảng viên hướng dẫn.
- Hoàng trước đây nói khoảng 10 giờ/tuần, sau đó ngày 17/10 muốn tăng cường làm việc có kiểm soát cho ZERO DOOR. Chưa có quỹ giờ mới được xác nhận; không tiếp tục coi “30h còn lại trong tháng” của lịch 09/10 là nguồn lực hiện có. Lịch mới là mục tiêu theo phụ thuộc, không phải cam kết đủ người/giờ. Codex/Claude hỗ trợ thực hiện và review theo issue; Hoàng giữ quyết định kỹ thuật, provider/chi phí và các thay đổi lab có hệ quả.
- Cloud cũ đã tắt. Hạ tầng cloud và dùng credit Azure cho compute được hoãn; lab chạy trên máy hiện tại. Có Azure for Students khoảng 100 USD theo người dùng, nhưng chưa kiểm tra số dư, quyền model, quota hoặc endpoint của subscription.

[Rà soát nguồn và dữ liệu](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-research-alignment-audit.md) là căn cứ cho các gói sửa. Những nhận xét trong bản rà soát về việc phải xác nhận đổi stack đã được giải quyết bằng thông tin trực tiếp của người dùng ở trên. Các phát hiện về SQLi, rollback, telemetry và dữ liệu chưa thay đổi.

## Việc hoãn và thứ tự bắt đầu

Hoãn triển khai Azure compute/cloud cũ, SaaS đa khách hàng, framework agent lớn, RAG/vector DB, training/RL, nhiều LLM, so sánh cloud–local và viết lại Boutique. Không xem việc có credit là lý do mở rộng hạ tầng.

**Hàng đợi lịch sử 17/10, không phát lại:** đầu ra đầu tiên là inventory/baseline ở R0 và bản nháp event contract ở R1. Provider được chốt/test theo R0-T03; không buộc bản nháp contract hoặc mọi test rules chờ LLM. Sau contract review và preflight, mở issue mã với đường dẫn/test cụ thể, sửa phép đo/guard rồi vector/healer, sau đó AI và thực nghiệm đối chứng. Lượt lập kế hoạch này chỉ sửa tài liệu; chưa tạo artifact của hàng đợi, sửa ứng dụng, chạy lab/test/LLM, cài model hoặc tạo tài nguyên trả phí.

## Các mục tiêu thời gian đã ghi nhận

- **31/10/2026:** mục tiêu hoàn thành kỹ thuật/pilot; chưa có dự báo capacity chứng minh lịch chắc chắn đạt.
- **14/11/2026:** mục tiêu nội bộ nộp bản paper đầu, phụ thuộc nơi và đợt nhận bài; chưa là hạn trường công bố.
- **31/12/2026:** thời hạn Hoàng cung cấp; khác thời gian trong DOCX như đã ghi ở trên, còn phải đối chiếu hồ sơ có thẩm quyền.

Chi tiết lịch/assignment/status cũ chỉ ở [lịch sử](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/README.md). Lịch delivery sống thuộc Linear sau khi xác minh đúng project và được phép áp metadata. Repo giữ scope/tiêu chí nghiên cứu và bằng chứng; issue AC phải phù hợp các cam kết này, không tự thay scope. Xem [Linear delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/README.md).
