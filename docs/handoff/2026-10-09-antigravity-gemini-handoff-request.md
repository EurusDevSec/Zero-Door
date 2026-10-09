# Yêu cầu bàn giao bối cảnh ZERO DOOR — Antigravity Gemini → Codex

Ngày tạo: 2026-10-09. Người yêu cầu: Lê Văn Hoàng. Người viết bàn giao: Antigravity Gemini đã cùng Hoàng làm dự án trước đây. Người tiếp nhận: Codex trong repo ZERO DOOR.

**Đây là yêu cầu tạo bản bàn giao, chưa phải bản bàn giao đã được Gemini viết.**

## 1. Nhiệm vụ và đầu ra

Hoàng muốn bạn tổng hợp lại bối cảnh các phiên trao đổi và quá trình làm ZERO DOOR để Codex hiểu được ý định ban đầu, lịch sử quyết định, những gì đã làm, những gì chưa làm và các vấn đề cốt lõi. Codex có thể đọc mã nhưng không có toàn bộ lịch sử trò chuyện giữa bạn và Hoàng. Thứ cần bổ sung nhất là phần bối cảnh không thể suy ra chắc chắn từ mã hoặc README.

Hãy đọc các nguồn bạn thực sự truy cập được và **tạo file `docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md`** trong repo `R:\_Projects\Eurus_Workspace\zero_door`. Viết bằng tiếng Việt, giữ tên kỹ thuật khi cần. Bản tóm tắt và phần chi tiết cùng nằm trong file này để không phân tán nguồn chuẩn.

Chỉ viết bản bàn giao; không triển khai sửa code, chạy attack/healing/benchmark, thay cấu hình cluster/cloud, chỉnh báo cáo cũ, sửa roadmap, commit hoặc push trong nhiệm vụ này. Nếu file bàn giao đích đã tồn tại, đọc trước và cập nhật có ghi ngày; giữ những thông tin lịch sử vẫn có nguồn, không xóa để làm đẹp trạng thái.

Đầu ra phải giúp người tiếp nhận trả lời được:

- Hoàng thực sự muốn đạt điều gì, ngoài danh sách công nghệ và tính năng?
- Vì sao thiết kế hiện tại trở thành như vậy; điều nào do Hoàng/thầy chốt, điều nào do bạn đề xuất?
- Bạn đã sửa/tạo/chạy những gì, vào giai đoạn nào, với bằng chứng nào?
- Những phần nào chạy thật, mới kiểm tra tĩnh, chỉ là demo/mock/placeholder hoặc còn là ý tưởng?
- Những mâu thuẫn, thất bại, giới hạn và việc còn mở nào người tiếp nhận cần biết ngay?

## 2. Nguồn và quy tắc ghi nhận

Ưu tiên lịch sử trao đổi Hoàng–Gemini mà bạn thực sự nhìn thấy, bản thuyết minh/hợp đồng, Git và artifact cụ thể. Đọc checkpoint để tìm manh mối nhưng đối chiếu nguồn; không coi nhãn Complete/100%, hình chụp hoặc câu “đã chạy thành công” tự nó là bằng chứng mọi tiêu chí đã đạt.

Đầu bản bàn giao ghi rõ phạm vi nguồn: phiên trò chuyện/giai đoạn nào còn truy cập được; những phiên nào không có; có đọc bản thuyết minh hay chưa; ngày kiểm tra repo và HEAD. Không tuyên bố nhớ hoặc đọc toàn bộ lịch sử nếu bạn chỉ còn một phần.

Dùng nhãn dưới đây cho các khẳng định quan trọng; có thể gắn nhiều nhãn nếu có nhiều nguồn:

| Nhãn | Ý nghĩa |
| --- | --- |
| USER_CONFIRMED | Có nguồn Hoàng/thầy xác nhận; nêu ai, thời điểm và nguồn. Lời thầy do Hoàng kể được ghi rõ là nguồn gián tiếp. |
| CHAT_RECALL | Nhớ/tóm tắt từ trao đổi cũ nhưng không còn đoạn gốc; không tự nâng thành xác nhận chắc chắn. |
| REPO_VERIFIED | Đối chiếu được file, cấu hình, diff hoặc commit cụ thể; đây là bằng chứng hiện vật, không tự là bằng chứng vận hành. |
| RUNTIME_EVIDENCED | Có log/run/dataset/quan sát cụ thể của lần chạy; ghi ngày và giới hạn phép thử. Lần chạy cũ không chứng minh hệ thống đang hoạt động hôm nay. |
| INFERENCE | Suy luận hoặc cách giải thích của bạn; nêu cơ sở và mức chưa chắc. |
| UNKNOWN | Chưa có nguồn/không nhớ/không kiểm chứng được; ghi điều gì còn thiếu. |

Với sự kiện và quyết định quan trọng, ghi thêm trạng thái thời gian: HISTORICAL, CURRENT_AT_<ngày>, SUPERSEDED hoặc PENDING. Nếu nguồn mâu thuẫn, trình bày cả hai cùng ngày/nguồn; không sửa lịch sử để khớp thiết kế hoặc roadmap mới.

Không sáng tác mốc thời gian, lời Hoàng/thầy, lý do kỹ thuật, lệnh đã chạy hoặc kết quả đo. Không có ngày chính xác thì ghi khoảng thời gian/không rõ. Chỉ dùng trích dẫn nguyên văn khi còn đoạn gốc; các ý nhớ lại phải được ghi là diễn giải. Không chép secret/API key/token/mật khẩu; chỉ ghi tên biến/Secret, đường dẫn cấu hình và trạng thái biết được.

## 3. Bối cảnh mới Hoàng đã xác nhận với Codex

Đây là thông tin được cung cấp trong giai đoạn tiếp nhận ngày 2026-10-09, **không mặc định là điều bạn và Hoàng đã thống nhất trong các phiên cũ**. Dùng để hiểu hướng hiện tại và ghi rõ chỗ khác với lịch sử:

- Bản thuyết minh Hoàng cung cấp là bản đăng ký chính thức, không có bản điều chỉnh khác; Hoàng cho biết thầy đã đồng ý đổi Java/Spring sang Python/Go. Google Online Boutique được đề xuất từ ban đầu.
- Vẫn giữ SQLi, DDoS L7, resource exhaustion; scale up/down, block IP, rollback; MTTD <60s, MTTR <2–3 phút, uptime ≥99,9% theo phạm vi đo đã định nghĩa.
- Hạn hoàn thành đề tài là 2026-12-31. Hoàng muốn hoàn thiện kỹ thuật trong tháng 10 để nộp bài sớm và dành thời gian phản biện; bài cần được chấp nhận đăng ở kỷ yếu trường trước nghiệm thu. Chưa có thông báo/đợt nhận bài cụ thể.
- Lê Văn Hoàng phụ trách kỹ thuật; Nguyễn Ngọc Hòa phụ trách Word/báo cáo. Hoàng cho biết khoảng 10h/tuần. Nếu tài liệu cũ có hp8001 hoặc tỷ lệ phân công khác, giải thích theo nguồn, không tự đồng nhất danh tính.
- Cloud cũ đã tắt theo Hoàng; ưu tiên hoàn thành local trước. Credit Azure Student khoảng 100 USD là thông tin Hoàng cung cấp, chưa phải bằng chứng endpoint LLM hoặc tài nguyên cloud sẵn sàng.
- Hoàng đang lo rằng sửa hệ thống cho chạy đúng vẫn chưa đủ mạnh về nghiên cứu. Roadmap mới đã thêm câu hỏi về giá trị LLM, đối chứng Kubernetes/rules/multi-agent, single-agent nếu claim lợi ích phối hợp, cùng kiểm soát lộ đáp án và tính trung thực dữ liệu.

Roadmap và audit của Codex là tài liệu tiếp nhận mới. Hãy đọc để đối chiếu, nhưng không dùng chúng để suy ngược rằng các quyết định đó đã có trong lịch sử Gemini.

## 4. Những nguồn trong và ngoài repo cần tìm

Đọc có mục đích, ưu tiên nguồn liên quan; không cần chép toàn bộ tài liệu vào handoff:

- `AGENTS.md`; `.agent/rules/CONTEXT.md`, `PLAN.md`, `ORCHESTRATOR.md`, `LESSONS_LEARNED.md`; `.agent/workflows/session_memory.md`; các checkpoint/hội thoại Antigravity còn truy cập được.
- `docs/context.md`, `docs/plan_original_v3.md`, `docs/plan.md`, `docs/workflow.md`; `docs/phases/`, `docs/runbooks/` và tài liệu quyết định thiết kế nếu có.
- `agent-orchestrator/{nemesis,gaia,hephaestus}/`, `chaos-worker/`, `infrastructure/`, các manifest/Helm/script và `.github/workflows/`.
- `infrastructure/scripts/experiment_runner*.py`, `analysis.py`; `docs/experiments/raw_data/`, `docs/experiments/analysis/`, `scratch/` và nguồn video/hình/log đã dùng trong báo cáo nếu có.
- `docs/research/`, `docs/references.md`, demo/slide; Git log/diff/branch để xác định thay đổi và phiên bản liên quan. Không quy tất cả commit cho Gemini nếu không có nguồn về người thực hiện.
- [Recovery roadmap hiện tại](R:/_Projects/Eurus_Workspace/zero_door/docs/plans/2026-10-09-research-recovery-roadmap.md) và [audit tiếp nhận](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-research-alignment-audit.md).

Bản đăng ký chính thức Hoàng đã chỉ rõ:

`C:\Users\ACER\Downloads\HĐ5_Nguyễn Ngọc Hòa_Ứng dụng kiến trúc Multi-Agent AI và Kỹ thuật Chaos Engineering xây dựng cơ chế Tự phục hồi cho Hệ thống Microservices.docx`

Nếu không truy cập được bản này hoặc lịch sử chat, ghi rõ thiếu nguồn và dùng các nguồn còn lại có nhãn thích hợp; không dừng toàn bộ bàn giao hoặc lấp chỗ trống bằng suy đoán.

## 5. Cấu trúc bắt buộc của bản bàn giao

### A. Tóm tắt tinh túy để Codex đọc trước

Viết khoảng 1–2 trang Markdown đầu file; không giới hạn phần chi tiết nếu cần để tránh mất thông tin trọng yếu. Nêu:

- Bài toán và ý Hoàng thực sự muốn; điều gì làm dự án này thành công.
- Những quyết định lớn nhất và lý do; đâu là ràng buộc không được âm thầm thay.
- Trạng thái có bằng chứng, khoảng cách còn lại và những hiểu nhầm dễ xảy ra khi chỉ đọc repo.
- Những vấn đề nghiêm trọng nhất; điều Codex cần kiểm tra trước khi tiếp tục.

Phần đầu phải đọc được độc lập. Trỏ ID đến các mục chi tiết/nguồn phía sau thay vì nhắc lại dài dòng.

### B. Nguồn đã đọc và giới hạn trí nhớ

Liệt kê phạm vi chat, tài liệu, Git và artifact đã đọc. Nêu rõ bản nào là nguồn gốc, checkpoint cũ, bản cập nhật hoặc chưa truy cập được. Đặt mã nguồn S01, S02… để dùng xuyên tài liệu; chat cần tên phiên/ngày/đoạn nếu còn, file cần đường dẫn và phiên bản/commit khi biết.

### C. Ý định, kỳ vọng và cách Hoàng muốn làm việc

Ghi các điều Hoàng từng nhấn mạnh hoặc sửa bạn: mục tiêu học/nghiên cứu/sản phẩm, mức tự động hóa mong muốn, giới hạn máy/chi phí/thời gian, điều muốn tự hiểu/tự làm, cách phân công với Hòa/thầy và cách trình bày báo cáo. Phân biệt lời Hoàng với cách bạn diễn giải; không đưa suy đoán về tính cách hoặc thông tin đời tư không liên quan.

### D. Dòng thời gian những sự kiện và bước ngoặt quan trọng

| Thời gian/phiên | Hoàng đang cần gì | Việc làm/quyết định | Người đề xuất/chốt | File/commit/run liên quan | Kết quả, nhãn nguồn và việc còn mở |
| --- | --- | --- | --- | --- | --- |

Bao gồm khởi đầu đề tài, thay stack/ứng dụng mục tiêu, lựa chọn kiến trúc và công cụ, các lần chạy/thất bại, thay cách đo hoặc xử lý dữ liệu, sửa báo cáo, triển khai/dừng cloud và các thay đổi hướng làm. Không cần kể mọi thao tác nhỏ; giữ các sự kiện giải thích được trạng thái hiện tại.

### E. Sổ quyết định và lý do thiết kế

| ID | Quyết định | Bài toán/ràng buộc lúc đó | Phương án khác đã cân nhắc và vì sao bỏ | Hoàng/thầy chốt hay Gemini đề xuất | Căn cứ | Còn hiệu lực/đã đổi/chưa chốt |
| --- | --- | --- | --- | --- | --- | --- |

Đặc biệt giải thích: Java/Spring → Python/Go; chọn Boutique; vai trò Nemesis/Gaia/Hephaestus; Kafka thay gọi trực tiếp; observability; executor Go; LLM API/local; rule fallback; lựa chọn đối chứng/metric; cách triển khai local/cloud. Nếu lý do chưa từng được trao đổi, ghi UNKNOWN thay vì viết lời giải thích hợp lý sau này.

### F. Ma trận yêu cầu gốc → thực hiện → bằng chứng

| Yêu cầu và nguồn | Cách đã định làm | Thực sự đã có | Bằng chứng/mức kiểm chứng | Phần thiếu hoặc sai khác |
| --- | --- | --- | --- | --- |

Đối chiếu tối thiểu số dịch vụ/phạm vi microservices, ba vector, các hành động healer, vai trò AI/multi-agent, KPI, thử nghiệm, tài liệu và điều kiện paper/nghiệm thu. Giải thích khác biệt giữa bản đăng ký, kế hoạch nội bộ và thực tế; một mục tiêu nội bộ thấp hơn không tự là thay đổi được duyệt.

### G. Kiến trúc và luồng thực thi thực tế

Mô tả từ attack đến probe xác nhận phục hồi: ai phát/nhận sự kiện, Kafka topic/schema, API, nguồn metric/log, namespace/target, nơi lưu trạng thái/dữ liệu và đường business request. Có thể dùng sơ đồ Mermaid ngắn. Chỉ ra đường chính, đường test/bypass, phụ thuộc bất đồng bộ, timeout/cooldown/dedup và tương tác controller/HPA.

Cho mỗi tác tử, nói rõ phần nào là LLM, threshold/signature, decision matrix hoặc nội dung giao diện; file/hàm nào thực hiện. Việc có tên agent hoặc SDK/API cấu hình không đủ để ghi tác tử đã chạy LLM.

### H. Inventory những gì bạn và Hoàng đã làm

| Thành phần/artifact | Ai làm nếu biết | File/hàm/commit | Việc thực hiện | Kiểm tra đã chạy, ngày và nguồn | Trạng thái thật/giới hạn |
| --- | --- | --- | --- | --- | --- |

Bao gồm code, hạ tầng, dashboard, CI, script thí nghiệm, raw data, phân tích, hình/video, chương Word/Markdown và tài liệu tham khảo. Tách đã viết mã, đã build/test, đã chạy tích hợp và đã đo đạt KPI. Ghi việc có trong máy nhưng chưa commit và việc chỉ nằm ngoài repo nếu biết đường dẫn.

### I. Thực nghiệm, dữ liệu và nguồn gốc số liệu

Giải thích theo bằng chứng:

- Mỗi runner dùng đường nào; có inject alert hoặc gọi /heal/trigger trực tiếp không; phép thử đó đo điều gì và không đo điều gì?
- MTTD/MTTR/uptime/heal success/FPR được định nghĩa và tính thế nào; timestamp, mẫu số, scrape/probe interval, recovery condition và cách xử lý missing/timeout/failure.
- Chế độ AUTO/MANUAL từng có ý nghĩa gì; healer/HPA/Kubernetes có còn tự can thiệp trong nhóm đối chứng không?
- Dataset gồm những run nào, thời điểm, workload, cấu hình, model/prompt, số lặp; pilot và formal có tách không; có War Game 4h thực sự không hay mới là mục tiêu?
- Dữ liệu bị chuyển sang scratch, lọc, loại hoặc đổi cách tổng hợp nào; lý do được trao đổi lúc đó, diff/script và tác động lên kết quả. Không mặc định mọi loại bỏ đều sai, cũng không tự hợp thức hóa khi thiếu nguồn.
- Các con số/khẳng định như MTTR 1,01s, uptime 100%, FPR bằng 0, tiết kiệm tài nguyên hoặc vá/triệt tiêu lỗ hổng đi từ nguồn nào đến bảng/biểu đồ/chương nào? Phần nào đủ căn cứ, phần nào chỉ là minh họa hoặc chưa kiểm chứng?

Lập bảng dataset/run → script/version → metric → hình/bảng → claim trong báo cáo. Giữ thất bại và độ bất định trong phần bàn giao; không chạy lại để thay thế dữ liệu lịch sử trong nhiệm vụ này.

### J. Các vấn đề cốt lõi, nợ kỹ thuật và mâu thuẫn

| ID | Vấn đề/mâu thuẫn | Dấu hiệu và nguồn | Ảnh hưởng chức năng/KPI/paper | Đã thử gì, kết quả | Nguyên nhân đã biết hay giả thuyết | Còn mở/đã giải quyết có bằng chứng |
| --- | --- | --- | --- | --- | --- | --- |

Làm rõ các điểm dưới đây nếu có nguồn; không giả định kết luận của audit mới đã được bạn biết từ trước:

- SQLi có executor/fixture thật hay chỉ xuất hiện trong prompt/báo cáo; nếu Boutique không có SQL target thì khi đó đã xử lý phạm vi ra sao?
- HTTP flood đi đúng ingress/route được đo không; CPU/memory stress tác động target hay một pod khác?
- Scale/rollback/block IP thực sự làm gì; thời điểm báo SUCCESS; nguồn IP, NAT/header, enforcement, TTL/cleanup và HPA tranh quyền.
- LLM có từng gọi được không, backend/model nào, giai đoạn nào; lỗi quota/key/latency/fallback; chỉ nêu trạng thái cấu hình, không tiết lộ credential.
- Metric/dashboard/chat/ảnh nào có dữ liệu giả lập hoặc fallback; mục đích ban đầu và cách đã ghi nhãn.
- Tài liệu nào ghi Complete/100% nhưng chỉ có kiểm tra tĩnh/demo; kết quả hiện tại không tái hiện được và nguyên nhân nếu biết.

Không cần tự bảo vệ các lựa chọn cũ hay quy lỗi cho ai. Cần mô tả điều đã xảy ra, căn cứ, giới hạn và phần chưa biết để Codex có thể tiếp tục đúng.

### K. Bối cảnh báo cáo, nghiên cứu và trao đổi với thầy

Ghi các góp ý/tiêu chí thầy từng đưa ra, Hoàng từng đồng ý/từ chối, yêu cầu đổi hướng, vấn đề paper/điểm mới/đối chứng và lý do chỉnh nội dung các chương. Nêu nguồn lời thầy trực tiếp hay Hoàng thuật lại. Xác định claim nào chưa đủ bằng chứng, tài liệu tham khảo nào thực sự đã đọc, nguồn hình/biểu đồ, giả thuyết nào mới là đề xuất.

Đặc biệt bàn giao câu trả lời đã từng có cho “vì sao cần AI?”, “vì sao nhiều tác tử?”, “khác rules ở đâu?”; nếu chưa từng đánh giá thì ghi chưa có thực nghiệm, không diễn giải kiến trúc thành bằng chứng ưu thế.

### L. Trạng thái lần cuối, hạ tầng và khả năng tiếp tục

Nêu trạng thái **lần cuối bạn trực tiếp biết**, tách với snapshot repo bạn kiểm tra khi viết handoff: Git/branch/HEAD, thay đổi chưa commit, cluster/context/namespaces, cách dựng lab, tài nguyên máy, dependency, cổng/endpoint, cloud từng dùng và cái gì đã dừng theo nguồn. Có runbook nào đáng tin và lệnh kiểm tra chỉ đọc nào giúp xác nhận lại? Phần nào cần dựng lại hoặc còn thiếu file/dữ liệu?

Không kết luận tài nguyên cloud đã xóa, không còn chi phí, secret hợp lệ hoặc dịch vụ đang hoạt động chỉ từ manifest hay ký ức; ghi thời điểm/nguồn và việc cần xác minh.

### M. Những điều Codex nên giữ và việc cần xác minh trước

Nêu điều nên giữ nguyên cùng lý do/nguồn; việc cần kiểm tra/sửa trước, phụ thuộc và điểm dễ làm sai khi tiếp nhận. Đây là khuyến nghị bàn giao, không thay recovery roadmap hoặc tự mở rộng phạm vi. So sánh khác biệt quan trọng giữa hướng cũ và roadmap mới nếu có.

### N. Khoảng trống và câu hỏi còn cần Hoàng trả lời

Chỉ liệt kê những khoảng trống có ảnh hưởng đến quyết định, không hỏi lại thông tin đã có nguồn xác nhận. Với mỗi câu, ghi vì sao cần, bạn đã tìm ở đâu và nguồn nào sẽ giải quyết. Nếu thiếu chat, ghi rõ nội dung nào không thể phục hồi thay vì đòi Hoàng kể lại toàn bộ từ đầu.

### O. Sổ nguồn và phụ lục tra cứu

Liệt kê các nguồn S01… đã dùng: chat/ghi nhớ, file/line, commit, log/run, dataset, ảnh/video hoặc tài liệu ngoài repo. Gắn các sự kiện/quyết định quan trọng với nguồn tương ứng. Nguồn không còn truy cập được phải có nhãn; danh sách file dài và trích đoạn cần thiết để ở phụ lục, không làm loãng phần tinh túy.

## 6. Tiêu chí hoàn thành bàn giao

- [ ] Có tóm tắt tinh túy độc lập và đủ các mục A–O; mục thiếu nguồn được ghi rõ, không điền suy đoán.
- [ ] Ý Hoàng, quyết định thầy/nhóm và đề xuất của Gemini được tách rõ; có lý do và bối cảnh của các bước ngoặt.
- [ ] Lịch sử chat, nguồn repo và bằng chứng runtime được phân biệt; việc cũ được đặt đúng thời gian.
- [ ] Những việc đã làm, đã thử, thất bại, workaround, chưa làm và chỉ demo được ghi đầy đủ theo mức kiểm chứng.
- [ ] Claim/KPI/dataset có đường truy nguồn; các mâu thuẫn và giới hạn không bị giấu hoặc sửa hồi tố.
- [ ] Có ranh giới giữa ngữ cảnh lịch sử và những xác nhận/roadmap mới của Codex.
- [ ] Không có secret; không sửa code/hạ tầng/roadmap hoặc tạo bằng chứng runtime mới trong nhiệm vụ bàn giao.
- [ ] File được lưu đúng đường dẫn; khi trả lời Hoàng, đưa đường dẫn và các thiếu hụt nguồn trọng yếu còn lại.

**Kết quả mong muốn:** Codex đọc xong có thể giải thích đúng câu chuyện dự án, hiểu ý Hoàng và lý do của thiết kế, biết độ tin cậy từng thông tin, rồi tiếp tục rà soát/triển khai mà không phải đoán lịch sử hoặc lặp lại những vấn đề đã trao đổi.

