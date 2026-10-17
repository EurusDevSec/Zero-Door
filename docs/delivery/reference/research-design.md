# Thiết kế nghiên cứu và đối chứng

[Phạm vi](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) · [Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Giá trị nghiên cứu và cách chứng minh

**Đánh giá trước thực nghiệm:** ZERO DOOR có tiềm năng làm đề tài ứng dụng, nhưng sửa cho đúng chức năng rồi trình diễn “gây lỗi → phát hiện → tự sửa” chưa đủ chứng minh giá trị nghiên cứu. Phần còn yếu là bằng chứng trả lời vì sao cần LLM và vì sao cần chia tác tử; đây là nhận xét về thiết kế đánh giá hiện tại, chưa phải kết luận đề tài yếu hoặc lời hứa bài sẽ được chấp nhận.

Cần theo dõi riêng hai điều kiện: **đáp ứng thuyết minh** bằng chức năng/KPI/sản phẩm đã cam kết, và **trả lời câu hỏi nghiên cứu** bằng đối chứng có thể tái lập. Hai điều kiện bổ sung cho nhau. Một kết quả AI không tốt hơn quy tắc vẫn có giá trị phân tích nếu thực nghiệm hợp lệ, nhưng không tự giải quyết các tiêu chí nghiệm thu còn thiếu.

### Công trình liên quan và đóng góp dự kiến

[AIOpsLab](https://arxiv.org/abs/2501.06706) mô tả môi trường microservices, fault injection, workload, telemetry và giao diện đánh giá agent vận hành. [ITBench](https://research.ibm.com/publications/itbench-evaluating-ai-agents-across-diverse-real-world-it-automation-tasks) đưa ra phương pháp benchmark agent cho tác vụ IT, gồm SRE. Đã đối chiếu mô tả/abstract từ nguồn gốc ngày 2026-10-09; chưa hoàn tất tổng quan toàn văn. Từ đó, nhận định làm việc là không lấy riêng việc ghép AI agent, Chaos Engineering và microservices làm bằng chứng điểm mới. R6-T01-S02 phải mở rộng đối chiếu tài liệu trước khi chốt claim.

Đóng góp hướng tới là **một cơ chế phối hợp tác tử với hành động có giới hạn, bằng chứng vận hành và xác minh hồi phục nghiệp vụ**, cùng dữ liệu đối chứng cho biết khi nào LLM hữu ích, khi nào quy tắc đủ tốt, và mức đánh đổi về latency/chi phí. Đây là đóng góp dự kiến; không dùng các từ “đầu tiên”, “vượt trội” hoặc “mới” khi chưa có căn cứ. Giữ Python/Go, Boutique và mọi cam kết ban đầu; ưu tiên chất lượng thực nghiệm thay vì thêm framework/model/cloud.

### Câu hỏi nghiên cứu và giới hạn kết luận

- **RQ1 — giá trị LLM:** với các sự cố có triệu chứng dễ nhầm lẫn, multi-agent dùng LLM có chọn hành động phục hồi phù hợp và phục hồi nghiệp vụ tốt hơn cơ chế quy tắc không? Mức đánh đổi về thời gian quyết định, latency hồi phục, token và chi phí là bao nhiêu?
- **RQ2 — giá trị chia vai trò:** việc tách phân tích sự cố và lựa chọn hành động có cải thiện kết quả so với một agent vận hành dùng cùng model, dữ liệu và công cụ không? Chỉ kết luận về lợi ích phối hợp khi đã chạy đối chứng tương ứng.
- **RQ3 — giới hạn vận hành:** cơ chế guard/fallback kiểm soát quyết định sai hoặc thiếu bằng chứng ra sao, và các tác động nào còn làm hỏng KPI hay traffic lành tính?

Giả thuyết cần kiểm tra là LLM có thể hữu ích hơn ở trường hợp cần kết hợp nhiều bằng chứng, trong khi quy tắc có thể nhanh/rẻ hơn ở trường hợp đơn giản. Khóa câu hỏi, metric chính và cách chấm trước formal run; không chọn lại giả thuyết hoặc bỏ case thất bại sau khi thấy kết quả. Không bắt buộc AI thắng để đóng issue thực nghiệm; bắt buộc kết luận khớp dữ liệu và nêu độ bất định.

### Cấu hình đối chứng

| Mã | Cấu hình | Điều được kiểm tra |
| --- | --- | --- |
| B0 — K8S_BASELINE | Kubernetes và controller mặc định; profile HPA được ghi rõ; ZERO DOOR không phát lệnh heal | Hạ tầng tự phục hồi được đến đâu |
| B1 — RULES | Bộ phát hiện/evidence và policy quy tắc, cùng executor/healer/guard/probe với B2 | Giá trị của cách đơn giản hơn; rules được hiệu chỉnh bằng pilot rồi khóa |
| B2 — MULTI_LLM | Gaia phân tích, Hephaestus chọn hành động bằng LLM trong giới hạn chung | Giá trị thêm của LLM so với B1 và B0 |
| B3 — SINGLE_LLM | Một agent vận hành gộp phân tích và lựa chọn hành động; cùng model, evidence, tools và giới hạn như B2 | Bắt buộc nếu claim rằng chia vai trò giúp cải thiện kết quả; có thể bỏ claim này nếu không đủ nguồn lực |
| BM — MANUAL | Người vận hành xử lý thật, giữ log thao tác; ZERO DOOR không tự chữa | Giữ theo protocol/cam kết hiện có và khi kết luận nhanh/tốt hơn thủ công |

B0/B1/B2 là đối chứng tối thiểu của câu hỏi chính. BM vẫn nằm trong kế hoạch formal hiện có; không xóa đối chứng hoặc cam kết ban đầu để nhường chỗ cho B3. Nếu B3 không thực hiện, vẫn xây kiến trúc ba tác tử theo thuyết minh nhưng chỉ mô tả cách phối hợp, không khẳng định kiến trúc nhiều tác tử tốt hơn một tác tử.

Trong phép so sánh phục hồi, **Nemesis/chaos harness dùng kế hoạch tải/fault đã khóa, được phát lại giống nhau cho mọi cấu hình**. Không cho B2 tự chọn sự cố dễ hơn nhóm khác. Khả năng chọn kịch bản thích nghi của Nemesis được kiểm chứng chức năng riêng; chưa suy ra giá trị của khả năng đó từ benchmark phục hồi. B3 so sánh cách chia vai trò vận hành Gaia/Hephaestus, không tự chứng minh lợi ích của toàn bộ ba tác tử hoặc riêng Nemesis.

### Case dễ nhầm lẫn và ngăn lộ đáp án

| Case | Triệu chứng/bằng chứng cần quan sát | Cách chấm được khóa trước chạy |
| --- | --- | --- |
| C0 — tải lành tính ổn định | Giao dịch bình thường, không có sự cố | Không can thiệp thừa; đo false alarm và false action |
| C1 — lượng khách hợp lệ tăng | CPU/latency tăng, mẫu request và lịch deploy bình thường | Scale hoặc không can thiệp theo điều kiện case; không chặn khách hợp lệ |
| C2 — DDoS L7 | Có thể cùng CPU/latency cao như C1; pattern nguồn/request khác | Hành động containment/scale thuộc tập phù hợp đã định; kiểm tra traffic benign |
| C3 — phiên bản lỗi | Error/latency tăng sau thay đổi release; lịch deploy và log lỗi | Rollback về release tốt hoặc tập hành động phù hợp đã định; không suy rollback từ mọi 5xx |
| C4 — resource exhaustion | Tài nguyên mục tiêu/throttling/sức khỏe dịch vụ suy giảm | Hành động phù hợp phải được probe xác minh, phân biệt thiếu capacity với nguyên nhân khác |
| C5 — SQLi trên fixture | Request/log/query bất thường tại fixture riêng | Chấm containment trên fixture; availability mua hàng Boutique báo riêng |

C0/C1 là đối chứng lành tính; C3 là case rollback đã có trong kế hoạch. Chúng bổ sung thiết kế đánh giá, không thay ba vector SQLi/DDoS/resource đã đăng ký. Chọn các mức tải để triệu chứng có thể chồng lấp nhưng phải xác minh nguyên nhân thật; không giả tạo metric giống nhau bằng dữ liệu mô phỏng.

Harness giữ **ground truth** gồm nguyên nhân, thời điểm fault và tập hành động chấp nhận được cho mỗi case; Hoàng/Hòa rà tập này trước formal run. Gaia/Hephaestus/single-agent chỉ nhận telemetry và lịch sử vận hành theo quyền vai trò. Không đưa tên case, loại attack từ command, đáp án hoặc gợi ý “hãy rollback” vào prompt/alert của bên chữa lỗi; dùng ID trung tính. Giữ bằng chứng vận hành thật như release history, log request và IP quan sát được, không che dấu vết cần để chẩn đoán. Dữ liệu ground truth và log điều khiển Nemesis/worker phải được tách khỏi nguồn truy vấn dành cho bên chữa lỗi.

### Metric, công bằng thực nghiệm và bằng chứng để viết bài

- Giữ MTTD/MTTR/uptime và ngưỡng gốc; thêm **tỷ lệ phục hồi được probe nghiệp vụ xác nhận trên tổng lượt sự cố**. Failure/timeout vẫn nằm trong mẫu số; MTTR của lượt thành công phải báo cùng tỷ lệ thất bại, không dùng trung bình đã bỏ failure để tuyên bố tốt hơn.
- Đo **độ đúng của hành động đầu tiên** so với tập hành động chấp nhận được đã khóa trên tổng lượt case yêu cầu quyết định; sai schema/không phản hồi sau trigger/timeout vẫn được tính là lượt không có quyết định đúng, không tự gán thành NO_ACTION. Đo riêng hành động thừa ở C0/C1 và đề xuất bị guard từ chối. Ghi đề xuất trước guard, action thực thi và kết quả; guard chặn sai không biến quyết định sai thành đúng. NO_ACTION/ABSTAIN chỉ đúng khi case cho phép, với quy ước ghi nhận được khóa trước chạy.
- Đo decision latency, số call/token, retry/fallback và chi phí theo run, có breakdown theo tác tử; ghi nguồn/ngày đơn giá khi tính tiền. Chi phí tạo kế hoạch Nemesis/harness dùng chung được ghi riêng với chi phí quyết định phục hồi để tránh quy sai overhead giữa B0/B1/B2/B3. Tách quyết định AI thật với fallback RULES; không gộp rồi gán toàn bộ lợi ích cho LLM.
- Giữ workload, fault intensity/duration, image/config, probe, executor, action budget và profile HPA tương đương giữa các nhóm; replay cùng case/seed, reset có xác nhận và xen kẽ thứ tự chạy. Giữ riêng biến thể dùng phát triển/pilot với biến thể đánh giá; khóa rules/prompt/model trước formal run.
- Với B3, giữ cùng evidence, công cụ và trần tài nguyên; ghi chênh lệch số lần gọi/token thực tế thay vì ép số call bằng nhau và che mất overhead phối hợp. Nếu rút gọn/bỏ thành phần theo kiểu ablation, chỉ kết luận đúng phần đã thay đổi.
- Đo lặp theo protocol chốt sau pilot; báo chênh lệch hiệu quả và độ bất định, không lấy một demo hoặc mẫu nhỏ làm kết luận ưu thế. Kiểm tra dịch vụ khỏe trong cửa sổ đã định và ghi thời điểm dừng fault, để không quy hồi phục tự nhiên sau khi dừng tải thành công của healer.

**Điều kiện sẵn sàng về thiết kế nghiên cứu:** R0-T04 khóa câu hỏi/đối chứng/nhãn; R1 lưu evidence không lộ đáp án và metric quyết định; R4-T03 có pilot B0/B1/B2; R4-T04 chốt và thử B3 nếu giữ claim RQ2; R5-T02-S02 khóa protocol; R6-T02 chạy và phân tích đầy đủ; R6-T03 đối chiếu claim với dữ liệu. Đây là yêu cầu về chất lượng bằng chứng, không phải lời đảm bảo được duyệt bài.

**Ngân sách và ưu tiên:** chốt công sức theo quỹ giờ Hoàng thực sự bố trí; mức 10h/tuần là thông tin cũ, chưa có con số mới. Không tự cộng giờ hoặc mở nhiều model/framework để làm B3. Khi pilot cho thấy thiếu nguồn lực, giữ B0/B1/B2 và mọi cam kết gốc, giảm claim về lợi ích chia vai trò; ghi lý do, ảnh hưởng và cập nhật lịch. Các gate đánh giá thực nghiệm hợp lệ, không yêu cầu kết quả thuận lợi cho AI.
