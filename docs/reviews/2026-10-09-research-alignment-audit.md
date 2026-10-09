# Rà soát ZERO DOOR theo thuyết minh nghiên cứu năm học 2025–2026

Ngày rà soát: 09/10/2026. Mã nguồn được đối chiếu tại HEAD `6337b319b075bf389d484a6be13a4bc094f94a82`.

Kết luận: repository có nền tảng triển khai prototype đáng giữ lại, nhưng chưa có bằng chứng đủ tin cậy để kết luận hoàn thành các cam kết nghiên cứu. Các việc ưu tiên là khôi phục phạm vi đã đăng ký, sửa ngữ nghĩa của hành động phục hồi và phương pháp đo, rồi thực nghiệm lại trước khi công bố kết quả.

Đây là rà soát mã, cấu hình, tài liệu và dữ liệu lưu trong repo. Chưa chạy lại cluster, tấn công, thao tác chữa lỗi, triển khai cloud hoặc kiểm chứng các endpoint cloud. Các trạng thái “Running”, “Verified”, “Complete” trong tài liệu cũ được xem là lời ghi nhận lịch sử, không phải xác nhận vận hành hiện tại. Không sửa mã ứng dụng hay dữ liệu thực nghiệm trong lượt này.

**Cập nhật sau khi người dùng xác nhận ngày 09/10/2026:** bản thuyết minh là bản đăng ký chính thức; thầy đã cho đổi Python/Go, Google Online Boutique được đề xuất từ đầu; hạn hoàn thành là cuối tháng 12/2026 và bài cần được chấp nhận đăng kỷ yếu trước nghiệm thu. Hoàng phụ trách kỹ thuật, Hòa phụ trách Word. Vì vậy các câu hỏi dưới đây về việc đổi stack đã được giải quyết bằng xác nhận trực tiếp của người dùng; không yêu cầu quay lại Java. Đánh giá chức năng, phép đo và dữ liệu vẫn giữ nguyên. Kế hoạch tiếp theo nằm ở [roadmap đã cập nhật](R:/_Projects/Eurus_Workspace/zero_door/docs/plans/2026-10-09-research-recovery-roadmap.md), với mốc mục tiêu kỹ thuật 31/10/2026 và quỹ thời gian 10h/tuần do người dùng nêu.

## Căn cứ và những điểm cần xác nhận

Nguồn ưu tiên cho các yêu cầu kỹ thuật là [bản thuyết minh do người dùng cung cấp](<C:/Users/ACER/Downloads/HĐ5_Nguyễn Ngọc Hòa_Ứng dụng kiến trúc Multi-Agent AI và Kỹ thuật Chaos Engineering xây dựng cơ chế Tự phục hồi cho Hệ thống Microservices.docx>). Tên file bắt đầu bằng HĐ5, nhưng nội dung là thuyết minh đề cương/đề tài, gồm mục 1–15; chưa đủ căn cứ để xác định đây là hợp đồng đã ký hoặc bản phê duyệt cuối cùng.

File ghi năm học 2025–2026, ngày 04/01/2026, thời gian sáu tháng từ 01–06/2026. Người dùng cho biết thời hạn thực hiện một năm và đề tài loại B. Chưa thấy mã đề tài, quyết định giao nhiệm vụ, văn bản gia hạn hoặc phê duyệt thay đổi phạm vi trong tài liệu này. Không suy ra loại B chỉ từ kinh phí dự kiến.

[Đề cương trong repo](R:/_Projects/Eurus_Workspace/zero_door/docs/plan_original_v3.md) là tài liệu triển khai bổ sung. Những ngưỡng thấp hơn trong tài liệu này, chẳng hạn uptime 99% thay cho 99,9%, không tự thay thế cam kết trong thuyết minh. Các mục ML anomaly detection, cải thiện 90%, ba nhóm đối chứng và War Game bốn giờ là nội dung kế hoạch repo; cần phân biệt với các điều khoản được trường thực sự duyệt.

Theo yêu cầu trực tiếp của người dùng, bài báo và minh chứng nộp bài phải nằm trong đường đi tới nghiệm thu. Chưa xác minh được điều kiện riêng cho loại B của đợt đăng ký: chỉ cần nộp, cần chấp nhận đăng hay cần xuất bản; cũng chưa xác định đúng nơi nhận bài.

Đã tìm thấy [thông báo nghiệm thu đợt 2 năm học 2025–2026 của Viện Công nghệ số](https://vcns.tdmu.edu.vn/bai-viet/thong-bao-nghiem-thu-de-tai-nckh-sinh-vien-dot-2/2b51fc09-77e2-4e1f-acb5-5c4e3d2ea751), đăng 25/06/2026. Thông báo nêu thời gian nộp hồ sơ 23/06–04/07/2026, nghiệm thu 06–12/07/2026, hồ sơ Word và PDF ghép đủ biểu mẫu, áp dụng cho đợt 2 và đề tài đợt 1 được chấp thuận chuyển đợt. Không đủ căn cứ gán lịch này cho chính đề tài của người dùng hoặc kết luận quyền nghiệm thu/gia hạn hiện tại.

[Trang biểu mẫu sinh viên của Ban Khoa học](https://khcn.tdmu.edu.vn/Menu/ChiTietBieuMauQuyTrinh/1) có biểu mẫu báo cáo và hướng dẫn bài tham luận kỷ yếu, nhưng trang có từ 2021, chưa chứng minh điều kiện loại B năm học 2025–2026. Thông báo đăng ký năm học 2026–2027 tìm thấy khi tra cứu không được dùng làm quy định áp dụng cho đề tài này.

## Đối chiếu cam kết

| Cam kết trong thuyết minh | Bằng chứng hiện có | Đánh giá |
| --- | --- | --- |
| Mục 9: Kubernetes, tối thiểu 5 microservices mẫu | Manifest chứa frontend, cartservice, checkoutservice, currencyservice, productcatalogservice và Redis; có probe, resource limit, namespace | Có cấu hình phù hợp về số dịch vụ; chưa xác nhận đầy đủ luồng nghiệp vụ chạy thực tế |
| Mục 11.2: E-commerce backend Java Spring Boot | Dùng image Google Online Boutique; chưa thấy backend thương mại điện tử Spring Boot do nhóm triển khai | Lệch ứng dụng mục tiêu đã ghi |
| Mục 11.3, 12 và 13: Spring AI, hệ thống/source Java Spring Boot | Agents thực tế là Python FastAPI, executor Go; Java còn một lớp khởi động | Lệch công nghệ; cần xác nhận thay đổi đã được duyệt hoặc khôi phục phần Java/Spring AI phù hợp |
| Mục 9: SQL Injection | Gaia có dò một số chuỗi trong log; registry worker và prompt Nemesis không có SQLi executor | Chưa hoàn thành chuỗi tấn công SQLi thực tế |
| Mục 9: DDoS tầng ứng dụng | Worker có HTTP flood, gọi API kích hoạt qua Nemesis | Có bộ tạo tải; chưa chứng minh gây tác động, phát hiện và phục hồi qua toàn bộ pipeline; phân biệt flood một nguồn và tấn công phân tán |
| Mục 9 và tiến độ tháng 3: Resource Exhaustion, CPU target app >80% | Worker tạo pod stress riêng, Gaia ánh xạ tên pod stress thành tên target | Chưa chứng minh tải đúng ứng dụng mục tiêu hoặc suy giảm nghiệp vụ |
| Mục 9: Scale up/down | Có SCALE_UP; reset thí nghiệm đưa replicas về 1; không thấy hành động SCALE_DOWN tự động trong ma trận healer | Có một phần; reset không chứng minh tự giảm quy mô sau phục hồi |
| Mục 9: Block IP | Có tạo NetworkPolicy; Gaia chưa truyền IP nguồn vào alert | Có thao tác cấu hình; chưa chứng minh chặn đúng nguồn và giữ người dùng hợp lệ hoạt động |
| Mục 9: Rollback phiên bản lỗi | `action_rollback` chỉ đổi annotation pod template | Không thực hiện hoàn nguyên image/config/template về phiên bản tốt trước đó |
| Mục 9: MTTD <60s, MTTR <2–3 phút | CSV có số liệu nhưng runner đo lịch sử healer sau cảnh báo trực tiếp | Chưa chứng minh KPI phát hiện và phục hồi dịch vụ |
| Mục 9: uptime ≥99,9% khi tấn công liên tục | Query scrape `up` tức thời, có giá trị thay thế khi thiếu dữ liệu | Chưa có phép đo availability nghiệp vụ theo cửa sổ thời gian |
| Mục 9: dashboard Gaia hiển thị attack/defense realtime | Có dashboard Nemesis, metrics/log/chat tổng hợp | Có giao diện; KPI ước lượng và nội dung dựng lại không dùng làm bằng chứng nghiên cứu |
| Mục 13 và tiến độ tháng 6: source, manifests, video, báo cáo, slide/poster | Source/manifests, sáu chương markdown, slide/demo script | Có bản thảo; cần xác nhận sản phẩm hoàn thiện và đóng gói theo biểu mẫu |
| Bài báo trước nghiệm thu theo yêu cầu người dùng | Chưa tìm thấy bản paper hoàn chỉnh và biên nhận nộp bài trong repo | Hạng mục bắt buộc trong kế hoạch hoàn thành; điều kiện hành chính chính xác còn cần đối chiếu |

## Những điểm có thể tiếp tục sử dụng

Kiến trúc đã tách nhiệm vụ tấn công, quan sát và chữa lỗi; có Kafka topics, bộ thực thi Go, Prometheus/Elasticsearch, Kubernetes API, dashboard và script triển khai. Namespace, RBAC giới hạn namespace, resource quota, probe, nonroot container và các bước kiểm tra trong CI là nền kỹ thuật hữu ích. Nemesis đã tích hợp LLM để chọn loại tấn công, mục tiêu và tham số.

Chưa có lý do từ rà soát này để xóa toàn bộ repo hoặc viết lại tất cả. Tuy nhiên, việc giữ Python/Go làm sản phẩm cuối phải được đối chiếu với phạm vi công nghệ trong thuyết minh. “Lighter” hay “tiết kiệm RAM” không tự chứng minh thay đổi phạm vi đã được chấp thuận.

## Các phát hiện ảnh hưởng trực tiếp đến kết luận khoa học

### F01 Phép đo hiện tại bỏ qua bộ phát hiện

[Runner trực tiếp](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/experiment_runner_direct.py:267) gửi alert vào `/heal/trigger`. E1/E2 gọi Nemesis theo dạng best effort nhưng vẫn tự đưa cảnh báo cho healer. E3 xóa pod rồi tự gửi POD_CRASH để không chờ Gaia. E4 gửi COMBINED dù worker không đăng ký loại này, rồi đưa cảnh báo CPU/error và xóa pod theo trình tự.

Đây có thể là cách kiểm tra riêng phản ứng của Hephaestus, nhưng không đo đầy đủ Attack → Detect → Heal. Không thể quy toàn bộ MTTD từ script này cho Gaia hoặc gọi E4 là bằng chứng ba kiểu tấn công đã chạy đồng thời thành công.

### F02 MTTR và nhóm MANUAL chưa đo điều được công bố

Runner chờ đọc lịch sử chữa lỗi để đánh dấu “detect”, rồi chờ đọc lịch sử một lần nữa để đánh dấu “heal end”, với polling khoảng một giây. Hai mốc có thể lấy từ cùng một sự kiện đã hoàn tất. MTTD này không phải thời điểm Gaia phát hiện và MTTR 1,01 giây không phải thời gian ứng dụng phục hồi.

Nhánh MANUAL chỉ thay cách ghi kết quả sau khi đã kích hoạt cùng đường chữa lỗi; chưa tắt healer hoặc ghi thao tác và thời gian phục hồi thủ công. MTTR MANUAL là -1, không có đối chứng hợp lệ cho lợi ích so với vận hành thủ công.

Trong E3 AUTO lượt 1, CSV ghi detect `15:42:07.956944`, heal end `15:42:09.979850` nhưng MTTR 1,01 giây; khoảng cách timestamp xấp xỉ 2,02 giây. Điều này cũng cho thấy không thể tái tính KPI từ các cột timestamp theo định nghĩa hiện tại.

### F03 Availability và false positives chưa được đo

[measure_uptime](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/experiment_runner_direct.py:162) dùng `avg(up{namespace="target-app"}) or vector(1)`: metric `up` mô tả scrape Prometheus, không phải khả dụng của giao dịch người dùng. Thiếu series được thay bằng 1; exception trả 99. Cả hai làm mất dấu trạng thái “không có phép đo”. `false_positives=0` được gán cố định.

[analysis.py](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/analysis.py:65) loại các dòng MTTD âm, đếm MANUAL là chữa lỗi thành công và không đánh giá cửa sổ hoạt động bình thường có nhãn. Các chỉ số success/FPR và phân bố thời gian có nguy cơ sai mẫu số và loại bỏ thất bại.

Tập dữ liệu lưu có 40 dòng, chia 4 kịch bản × 2 chế độ × 5 lượt. [Thống kê hiện có](R:/_Projects/Eurus_Workspace/zero_door/docs/experiments/analysis/summary_statistics.csv) cho E3 AUTO success 20%, nhưng thời gian phục hồi trung bình vẫn 1,01 giây và uptime 100%. Đây là tín hiệu cần rà soát ngữ nghĩa đo; không chứng minh khả dụng 99,9% hoặc thành công hệ thống.

Giữ nguyên dữ liệu cũ làm lịch sử chẩn đoán. Không sửa số, xóa lượt bất lợi hoặc chạy lại riêng các lượt để khớp kỳ vọng. Đánh dấu giới hạn của bộ dữ liệu trong nghiên cứu, tách tập thực nghiệm mới bằng phiên bản phương pháp đo.

### F04 Dashboard pha trộn số đo và số ước lượng

[updateSREStats](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/nemesis/static/app.js:605) có cộng thời gian theo loại action bằng `Math.random()`, có giá trị fallback MTTD/MTTR và uptime ước lượng. Backend chat tái dựng câu giải thích từ metrics/lịch sử; một số câu nói chặn tại ingress trong khi mã thực hiện NetworkPolicy.

Phải tách rõ log/sự kiện thật, diễn giải suy ra và số ước lượng. Dashboard nghiên cứu cần dùng cùng nguồn sự kiện và KPI như script phân tích; thiếu dữ liệu hiển thị “chưa có dữ liệu”.

### F05 Chưa thực hiện các hành động chữa lỗi đúng nghĩa

[Rollback](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py:282) chỉ kích hoạt rollout cùng pod template bằng annotation. Cần lưu/khôi phục phiên bản tốt đã biết và kiểm tra image/config thực tế sau hoàn nguyên.

[Scale up](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py:177) báo SUCCESS khi patch API thành công; cần chờ replicas sẵn sàng và kiểm tra hồi phục ứng dụng. [Restart](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py:247) chấp nhận bất kỳ pod Ready khác pod vừa xóa, có thể là pod tồn tại từ trước; chưa chứng minh replacement hay hồi phục nghiệp vụ.

[Block IP](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py:323) tạo một chính sách cho phép toàn bộ IPv4 trừ IP chỉ định. Gaia hiện chưa gắn sourceIP; [fallback](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py:457) có thể dùng `0.0.0.0`. Cần nhận diện nguồn thật, kiểm chứng đường đi qua ingress/NAT và hiệu lực policy/CNI; API create thành công không chứng minh attacker đã bị chặn. Nhiều NetworkPolicy có thể hợp các quyền allow, cần kiểm tra tương tác khi tạo nhiều policy.

Chưa thấy SCALE_DOWN tự động trong ma trận quyết định. Reset replicas cho lần đo kế tiếp không phải hành động tự phục hồi sau khi tải giảm. Cần phân biệt API_ACCEPTED, ACTION_COMPLETED, RECOVERY_VERIFIED, FAILED, TIMEOUT, SKIPPED.

### F06 Mô hình gây lỗi và tín hiệu phát hiện không khớp

[CPU stress](R:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/attack/cpu_stress.go:51) tạo pod riêng có nhãn `app=chaos-stress`. [Gaia](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/gaia/main.py:123) ánh xạ tên `<service>-stress-*` về service. Vì vậy báo CPU cao có thể phản ánh chính công cụ stress, không phải ứng dụng. Các limit CPU trong Gaia còn được hardcode thay vì lấy cấu hình thực tế. Cần chứng minh fault/load gây suy giảm target và healing loại bỏ hoặc giảm suy giảm đó; nếu nghiên cứu tranh chấp tài nguyên node phải mô tả đúng và đo co-location/cgroup tác động.

[HTTP flood](R:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/attack/http_flood.go:35) mặc định gọi Service DNS trực tiếp; Gaia dùng metrics ingress cho lỗi HTTP và latency. Đây là nguy cơ bỏ sót do khác đường đi; cần kiểm tra cổng giao thức dịch vụ và thiết kế cùng đường quan sát với tải nghiệp vụ.

POD_KILL là fault hạ tầng bổ sung, không thay thế SQL Injection đã đăng ký. Bộ phát hiện đếm container restart không đồng nghĩa phát hiện pod bị xóa. Kubernetes tự tạo pod mới nên phải tách hiệu quả controller mặc định khỏi giá trị do Hephaestus mang lại.

### F07 Vai trò AI và tính mới chưa được chứng minh đầy đủ

Nemesis dùng LLM để chọn tấn công/tham số nhưng chưa có GenAI sinh payload SQLi như thuyết minh. Gaia dùng threshold/chữ ký; Hephaestus dùng decision matrix. Không cần mặc định biến cả ba thành ba LLM hoặc thêm reinforcement learning, nhưng phải mô tả trung thực cơ chế của từng tác tử và đo giá trị AI so với kịch bản template.

Các mệnh đề “Zero Door/không cửa hậu”, “triệt tiêu lỗ hổng”, “vá code tự động” mạnh hơn năng lực được chứng minh. Phục hồi availability bằng scale/restart không tự sửa lỗ hổng SQLi. Cần định nghĩa rõ containment, recovery, remediation và giới hạn mô hình đe dọa. Phần tổng quan/tính mới cần tra cứu lại nguồn gốc, không kết luận khoảng trống toàn lĩnh vực chỉ từ việc tích hợp ba thành phần.

### F08 Kiểm tra kỹ thuật và khả năng tái lập còn thiếu

CI có compile, Go build/vet, SAST và scan manifest; chưa tìm thấy bộ kiểm thử hành vi tự động cho chuỗi nghiên cứu. Job helm-lint hiện kiểm tra Helm có sẵn và parse YAML, chưa xác nhận Helm chart hay schema Kubernetes. Nhãn image `latest` và nhiều đường setup có thể làm lần chạy sau khác môi trường sinh dữ liệu.

Cloud deploy script không có các bước triển khai Elasticsearch/Fluent Bit như setup local, trong khi Gaia dò log qua Elasticsearch. Cần xác nhận quan sát log đủ trong profile thực nghiệm được chọn. Không lấy lời ghi cloud deployment trong báo cáo làm bằng chứng tương đương pipeline đầy đủ hoạt động hiện tại.

### F09 Giới hạn thao tác gây lỗi cần được củng cố

[ValidateURL](R:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/validation/target.go:43) kiểm tra chuỗi con của URL thay vì hostname đã parse. Suffix ở path/query có thể vượt kiểm tra; cần giới hạn host/service/port/giao thức, redirect và egress trong sandbox. [EffectiveDuration](R:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/attack/executor.go:84) dùng max từ command nếu có, chưa luôn lấy giá trị nhỏ hơn giới hạn server.

API kích hoạt/reset/heal chưa thấy lớp xác thực trong các handler đã đọc, trong khi manifest có ingress tới agents. Cần chặn public control endpoints trong profile nghiên cứu. Kiểm tra dedup theo command/alert ID, Kafka acknowledgment sau xử lý, giới hạn tổng tải đồng thời, cleanup khi hủy, nguồn sự kiện bền vững và cleanup TTL sau khi healer restart.

Đây là các lỗ hổng điều khiển ảnh hưởng đúng nhiệm vụ sandbox, không phải yêu cầu mở rộng SaaS hay xây dựng chứng nhận bảo mật production.

### F10 Báo cáo cần viết lại các kết luận vượt bằng chứng

[Chương 6](R:/_Projects/Eurus_Workspace/zero_door/docs/research/chapter6.md:8) kết luận KPI đã chứng minh từ 40 lượt; các lỗi phép đo trên làm kết luận này chưa có cơ sở. Bảng RAM Java là “dự kiến”, không phải kết quả Java chạy cùng workload: chưa đủ chứng minh cải thiện thực nghiệm 88%. Tuyên bố distroless loại bỏ hoàn toàn CVE/shell injection và không bao giờ OOM phải bỏ hoặc sửa theo bằng chứng thực tế.

E3 success 20% có thể gợi ý xung đột healer với controller, nhưng chưa đủ chứng minh nguyên nhân race condition khi không có trace để đối chiếu. Phải trình bày như giả thuyết cần kiểm tra. Tài liệu tham khảo, tác giả/năm, các bảng timestamp minh họa và log trình bày trong chương 5 cần đối chiếu với nguồn sơ cấp và raw log; không tự suy ra dữ liệu bị cố ý làm giả.

## Kế hoạch sửa và tiêu chí hoàn thành

| Bước | Công việc cụ thể | Điều kiện để chuyển bước |
| --- | --- | --- |
| P0 Chốt phạm vi đăng ký | Lập bảng yêu cầu → mã → phép thử → bằng chứng; xác nhận Java/Spring AI và target app, thời hạn/gia hạn, điều kiện/nơi nộp paper; giữ snapshot dữ liệu cũ | Có baseline duy nhất và những thay đổi được xác nhận; không âm thầm thay SQLi hoặc giảm uptime |
| P1 Sửa nền đo và điều khiển | Chuẩn hóa run/command/alert/healing IDs, timestamps UTC và thời gian đơn điệu cho interval; lưu event bền; đo HTTP nghiệp vụ từ client độc lập; bỏ KPI ngẫu nhiên/fallback; enforce sandbox, mode và tổng tải | Một run tái tính được toàn bộ mốc; thiếu telemetry được ghi missing; MANUAL không thể gọi healer; không có hành động vượt scope sandbox |
| P2 Hoàn thành chức năng đăng ký | Target Spring Boot/Spring AI theo baseline đã chốt; SQLi và GenAI payload trong sandbox; L7 load; resource fault đúng target; scale up/down, source-aware block và rollback thật | Mỗi vector có chuỗi tấn công thật → Gaia → Kafka → healer → xác nhận hồi phục; rollback trả image/config tốt, block không làm mất client hợp lệ |
| P3 Kiểm thử tích hợp và ổn định | Kiểm thử readiness/recovery, trùng thông điệp, Kafka/Prom/ES gián đoạn, LLM sai output, cleanup/restart, HPA–healer conflict; cố định version, resources, config | Một môi trường dựng lại được; có test hành vi và trace thật; lỗi/timeout không bị đếm thành success |
| P4 Thực nghiệm nghiên cứu | Chạy Kubernetes mặc định/HPA, monitor+manual và ZERO DOOR với workload/attack khớp nhau; so sánh template với LLM nếu công bố lợi ích GenAI; đảo thứ tự, reset có kiểm chứng, normal windows và War Game | Có bộ dữ liệu mới, raw events, probe results, version/config/seeds; báo đủ failure/timeout và khoảng tin cậy; kết luận theo dữ liệu |
| P5 Bài báo và hồ sơ | Viết intro/method trước; results/discussion dựa bộ dữ liệu mới; kiểm chứng references; sửa báo cáo; làm video, slide/poster, Word/PDF theo biểu mẫu; chuẩn bị nộp paper | Có paper nhất quán với mã/data, minh chứng đầu ra đáp ứng điều kiện của đề tài; demo tái lập và bộ hồ sơ đầy đủ |

Không có lịch ngày kết thúc cố định trong bản này vì chưa biết hạn mới, xác nhận đổi stack và tài nguyên thực nghiệm. Trình tự phụ thuộc là P0 → P1 → P2 → P3 → P4 → kết quả P5. Có thể viết phần giới thiệu/phương pháp và chuẩn bị biểu mẫu trong lúc sửa kỹ thuật; chưa điền kết quả nghiên cứu trước khi đo.

### Quy tắc đo đề xuất

- Lưu `attack_effect_started`, `gaia_detected`, `alert_published/consumed`, `heal_started`, `action_completed`, `recovery_verified`, `attack_stopped` và probe timeline. Mốc ghi command gửi đi chưa chứng minh attack đã có hiệu lực; action API được nhận chưa chứng minh phục hồi.
- MTTD mỗi sự cố = detect thật trừ fault/attack có hiệu lực. Chốt MTTR là detect → phục hồi ổn định hoặc incident start → phục hồi; lưu cả hai interval để tránh thay định nghĩa sau khi thấy số liệu. Thuyết minh ghi khoảng 2–3 phút; báo tỉ lệ dưới cả 120s và 180s rồi đối chiếu ngưỡng được xác nhận.
- Recovery là probe nghiệp vụ đúng nội dung, đúng latency budget trong cửa sổ ổn định đã định trước; kết hợp readiness/metrics hậu điều kiện. Không yêu cầu đo một request 200 rồi kết luận toàn hệ thống đã phục hồi.
- Availability chọn rõ định nghĩa theo thời gian hay request, workload, endpoint/giao dịch và cửa sổ. Báo latency/error cùng availability; không suy ra từ scrape `up`. Probe phải đủ phân giải để đo mục tiêu 99,9%.
- Nếu giữ War Game bốn giờ của kế hoạch repo và đo uptime theo thời gian, downtime budget 99,9% chỉ là 14,4 giây. Recovery 2–3 phút vẫn có thể đạt availability nếu có replicas khỏe tiếp tục phục vụ; một pod phục vụ duy nhất bị mất vài phút sẽ không đạt. Không hạ mục tiêu để làm biểu đồ đẹp.
- Đối chứng vẫn giữ tự phục hồi mặc định của Kubernetes. HPA phải được cấu hình rõ theo từng nhóm, tránh tác động đồng thời không ghi nhận; nhóm thủ công lưu alert, thao tác người vận hành và hồi phục thực, không giả định thời gian.
- Đăng ký trước cường độ/tổng tải/duration, số lặp theo độ biến thiên và tài nguyên; năm lượt hiện tại không đủ để khẳng định P95/P99 ổn định. Chỉ dùng paired test khi thiết kế thật sự ghép cặp và giả định phù hợp; báo hiệu ứng và độ bất định. Không loại timeout khỏi mẫu số mà không báo cáo.
- Khi đánh giá FPR, có hoạt động bình thường và nhãn lỗi thật; chốt đơn vị quyết định/cửa sổ và công thức. `FP / số lần tấn công` không tự là false positive rate.

### Phạm vi giữ tập trung

Cloud được thuyết minh cho phép là một lựa chọn thay cho cluster cục bộ, không phải bằng chứng bắt buộc thay thế thực nghiệm đúng. SaaS đa khách hàng, WebSocket outbound, thêm Ansible, mua domain hoặc mở rộng nhiều cloud chưa giúp khép các cam kết còn thiếu; chưa ưu tiên trong kế hoạch này. Không mặc định đưa ML/RL vào Gaia/Hephaestus nếu baseline được trường duyệt không yêu cầu.

Trước khi nghiệm thu hoặc công bố, phần kết quả chỉ được dùng những gì có thể đi từ bảng/biểu đồ về CSV, từ CSV về event và probe, rồi về mã/cấu hình/commit đã chạy. Các mục tiêu chưa đạt được ghi trung thực, kèm nguyên nhân đã kiểm chứng hoặc giả thuyết cần kiểm tra.
