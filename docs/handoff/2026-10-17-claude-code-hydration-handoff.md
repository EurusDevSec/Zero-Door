# ZERO DOOR — Bàn giao và kiểm tra hydration cho Claude Code

Ngày giao: **17/10/2026**, múi giờ Asia/Saigon. Người giao: Hoàng qua Codex. Người tiếp nhận: Claude Code.

**Trạng thái: HYDRATION ĐẠT sau review D8 — Codex: 19/20, 17/10/2026, HEAD f9623a3. Đủ tiếp nhận task hẹp; xem E6. Điểm D ban đầu 15/20 được giữ trong lịch sử.**

## A. Nhiệm vụ và đầu ra

Hoàng muốn Claude Code cùng Codex hoàn thiện đề tài ZERO DOOR. Trước khi giao triển khai, hãy kiểm tra mức hiểu dự án bằng việc đọc nguồn, truy vết mã và tự giải thích các vấn đề trọng yếu. Đây là kiểm tra khả năng tiếp nhận bối cảnh và đánh giá bằng chứng, không phải yêu cầu khẳng định dự án đã hoàn tất.

**Đầu ra duy nhất: điền phần D của chính file này.** Giữ nguyên phần A–C làm đề bài và phần E dành cho Codex. Không tạo một bản trả lời rời khiến người tiếp nhận phải tìm nhiều nơi. Cuối phiên, báo đường dẫn file và những câu còn UNKNOWN cho Hoàng.

Trong lượt hydration này, được đọc tài liệu/mã/Git, tra graph và chạy truy vấn chỉ đọc có giới hạn thời gian. Chỉ sửa file này. Không sửa ứng dụng, roadmap, báo cáo, raw data, cấu hình hoặc chỉ dẫn agent; không cài dependency, build/deploy, start/reset/recreate cluster, gọi endpoint gây tấn công/chữa lỗi, benchmark hay API LLM tốn phí. Không commit/push. Nếu cần chạy gì ngoài phạm vi này, ghi đề xuất và lý do vào phần D để xét ở lượt triển khai.

Không tự điền kết quả chạy nếu chỉ đọc mã. Không ghi secret/token/mật khẩu hoặc nội dung Secret; chỉ ghi tên biến và vị trí cấu hình. Không cần nạp toàn repo vào ngữ cảnh: dùng mục lục, graph và đọc phạm vi nguồn liên quan.

## B. Bối cảnh hiện tại do Hoàng xác nhận

Các ý dưới đây được Codex chuyển lại từ trao đổi với Hoàng; Claude không được trình bày như mình đã đọc toàn bộ hội thoại hoặc trực tiếp nghe thầy nói.

- Đây là đề tài nghiên cứu khoa học loại B tại Trường Đại học Thủ Dầu Một. Hoàng phụ trách kỹ thuật; Nguyễn Ngọc Hòa phụ trách Word/báo cáo. Antigravity Gemini đã tham gia phát triển trước Codex; handoff Gemini là nguồn lịch sử cần đối chiếu.
- Python/FastAPI, Go và Google Online Boutique được chấp nhận theo xác nhận của Hoàng; không quay lại Java/Spring chỉ để khớp mô tả cũ.
- **Quyết định mới nhất ngày 17/10: vẫn làm đủ SQLi, DDoS tầng ứng dụng và resource exhaustion.** Hoàng có kể việc thầy khuyên thu hẹp và từng trao đổi chọn SQLi, nhưng sau đó Hoàng quyết định trước hết giữ cả ba. Không lấy phương án chỉ SQLi làm phạm vi hiện hành; không tự ghi rằng thầy vừa duyệt lại cả ba.
- Giữ các hành động scale up/down, block IP, rollback và tiêu chí gốc: ít nhất 5 microservices; MTTD <60 giây, MTTR <2–3 phút, uptime ≥99,9% trong phạm vi đo được định nghĩa. Không tự hạ ngưỡng để khớp kết quả.
- Theo Hoàng, thầy đã yêu cầu block IP để tránh phát hiện rồi phục hồi lặp mãi. Cần chứng minh chặn nguồn tấn công có hiệu quả và không làm mất truy cập hợp lệ.
- **Claude ở đây là Claude Code cùng hỗ trợ lập trình, review, kiểm chứng với Codex.** Chưa có quyết định chọn Claude API làm backend LLM cho các tác tử. Công cụ AI viết mã và AI chạy trong hệ thống là hai vai trò khác nhau.
- Mục tiêu hiện tại: cố hoàn thiện kỹ thuật trong **tháng 10/2026**, viết bài song song để nộp trường sớm. Nộp bài và được chấp nhận đăng là các mốc khác nhau. Tên kỷ yếu, template, đợt nhận bài chưa chốt; không tự đặt thành lịch chính thức của trường.
- Hạn hoàn thành/nghiệm thu **31/12/2026** là thông tin Hoàng đã cung cấp. Nguồn DOCX và roadmap có phần cần đối chiếu về thời hạn; không tự kết luận có hoặc không có gia hạn.
- Hoàng trước đó nói khoảng 10h/tuần; chưa xác nhận quỹ giờ mới. Sau hơn một tuần tập trung dự án S-cool thực tập, Hoàng quay lại ZERO DOOR ngày 17/10. Không tự suy ra đã có triển khai ZERO DOOR mới trong khoảng nghỉ.
- Ưu tiên lab local. Cloud cũ đã tắt theo Hoàng; credit Azure Student khoảng 100 USD chưa được kiểm tra. Không tự bật cloud hoặc chi tiêu.
- Mối lo nghiên cứu: làm chạy demo chưa đủ để chứng minh giá trị LLM/multi-agent. Cần đối chứng, số liệu mới, ghi cả thất bại và giới hạn kết luận.

## C. Cách đọc và tiêu chuẩn trả lời

### C1. Nguồn cần tiếp nhận

Repo: `R:\_Projects\Eurus_Workspace\zero_door`.

1. Đọc `AGENTS.md`, `.agent/rules/CONTEXT.md`, `.agent/workflows/session_memory.md`. Kiểm tra Git HEAD, branch và dirty files của chính phiên mình. Nhãn Complete/100% hoặc mô tả LLM trong tài liệu cũ là các khẳng định cần xác minh.
2. Đọc `docs/plans/2026-10-09-research-recovery-roadmap.md` để biết yêu cầu và gate. Lịch được lập từ 09/10, chưa được lập lại theo phiên 17/10; quá due không có nghĩa đã DONE. Phần B ở trên bổ sung bối cảnh mới, không sửa lịch sử tài liệu.
3. Đọc yêu cầu gốc trong DOCX bên dưới nếu truy cập được; đối chiếu `docs/plan_original_v3.md`, `docs/plan.md` và `docs/research/` đúng vai trò từng nguồn.
4. Truy vết nguồn đang hoạt động: `agent-orchestrator/{nemesis,gaia,hephaestus}/`, `chaos-worker/`, manifests và script liên quan trong `infrastructure/`; dashboard, experiment runner, analysis và raw data khi trả lời câu hỏi tương ứng.
5. Sau khi đã ghi nhận truy vết riêng, đối chiếu `docs/reviews/2026-10-09-research-alignment-audit.md`, `docs/reviews/2026-10-09-antigravity-handoff-review.md` và `docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md`. Nêu điểm đồng ý/khác biệt cùng nguồn, không chép kết luận rồi gọi là kiểm chứng độc lập.
6. Đọc `docs/runbooks/2026-10-09-legacy-demo-restart.md` khi đánh giá cách khởi động lab. Chỉ đọc trong nhiệm vụ này, không chạy các bước làm thay đổi lab.

DOCX do Hoàng cung cấp:

`C:\Users\ACER\Downloads\HĐ5_Nguyễn Ngọc Hòa_Ứng dụng kiến trúc Multi-Agent AI và Kỹ thuật Chaos Engineering xây dựng cơ chế Tự phục hồi cho Hệ thống Microservices.docx`

Nếu không truy cập được nguồn, ghi rõ đường dẫn và lý do. Không coi bản tóm tắt là đã đọc DOCX. Không xuất toàn văn hoặc tạo bản chuyển đổi vào repo trong lượt này.

GitNexus: theo `AGENTS.md`, bắt đầu bằng `gitnexus://repo/zero_door/context`, kiểm tra freshness so với HEAD; dùng query → context → đọc source để xác minh. MCP không có thì dùng CLI nếu đã có. Không tự cài công cụ, bật embeddings, tạo wiki, publish hay rebuild index trong lượt hydration; index stale/unavailable thì ghi lại và dùng `rg`/source. Kafka/HTTP động và tài liệu nghiên cứu cần đối chiếu trực tiếp, graph không chứng minh runtime.

### C2. Bằng chứng

Mỗi kết luận trọng yếu dùng nhãn phù hợp:

| Nhãn | Ý nghĩa |
| --- | --- |
| USER_CONTEXT | Thông tin Hoàng được chuyển lại ở phần B; không phải xác minh mã/runtime |
| SOURCE_VERIFIED | Đã đọc nguồn cụ thể tại HEAD đang kiểm tra; chưa chứng minh vận hành |
| HISTORICAL_EVIDENCE | Log/dataset/commit cũ, có ngày/phiên bản và giới hạn |
| LIVE_READ_ONLY | Quan sát trực tiếp bằng truy vấn chỉ đọc trong phiên này; ghi timestamp/lệnh/kết quả |
| INFERENCE | Suy luận có cơ sở được nêu rõ |
| UNKNOWN | Thiếu nguồn hoặc chưa kiểm tra; nêu cách kiểm chứng tiếp |

Dẫn chứng nguồn dùng đường dẫn repo + symbol + dòng, hoặc commit/artifact cụ thể. Ghi rõ HEAD để người khác tìm lại khi số dòng đổi. Audit chỉ là nguồn kết luận trước đó, không thay source cho một tuyên bố SOURCE_VERIFIED. Graph không thấy caller không có nghĩa endpoint không được gọi. Lệnh lỗi/timeout không chứng minh inventory rỗng. API trả SUCCESS, pod Running, có NetworkPolicy hoặc có tên agent chưa đủ chứng minh kết quả nghiên cứu.

### C3. Câu hỏi hydration bắt buộc

Trả lời bằng lời của mình, kèm bằng chứng. Không cần câu trả lời dài nếu một đoạn và nguồn đã đủ.

| Mã | Câu hỏi cần trả lời |
| --- | --- |
| Q01 | Mục tiêu nghiên cứu, sản phẩm, KPI và phạm vi hiện hành là gì? Đâu là xác nhận của Hoàng, cam kết DOCX, đề xuất kỹ thuật và phần còn chờ xác nhận? |
| Q02 | Truy vết một đường tấn công hiện có từ REST/UI → Nemesis → Kafka → Go worker → kết quả. Endpoint manual và endpoint LLM khác nhau ở đâu? Vì sao gọi nhầm endpoint để health-check có thể có tác dụng phụ? |
| Q03 | Truy vết đường quan sát → Gaia → alert → Hephaestus → Kubernetes → xác nhận phục hồi. Dữ liệu nào thực sự có, chỗ nào mất liên kết/ID hoặc chưa có hậu điều kiện? Phân biệt phát hiện thật với inject alert trực tiếp. |
| Q04 | Lập ma trận riêng cho SQLi, DDoS L7 và resource exhaustion: executor, target, nguồn bằng chứng tác động, detector, hành động xử lý, cleanup, phần thiếu. Boutique hiện có mục tiêu SQLi phù hợp được chứng minh không? Nếu cần fixture thì đó là đề xuất bổ sung gì? |
| Q05 | Trong mã hiện tại, block IP lấy IP từ đâu và enforce ở đâu; rollback thay đổi gì; scale up/down quyết định và xác nhận thế nào? Chỉ ra giới hạn và cách kiểm thử phân biệt API chấp nhận với tác dụng thật, kể cả NAT/proxy/HPA khi liên quan. |
| Q06 | Agent nào thực sự gọi LLM, agent nào dùng rules/template? Kiểm tra đường gọi, cấu hình, fallback và trace; tách có mã tích hợp khỏi backend đang hoạt động. Claude Code tham gia có thay đổi câu trả lời này không? |
| Q07 | MTTD/MTTR/uptime trên dashboard và experiment runner được tạo từ mốc nào? Đọc một lát dữ liệu cũ, kiểm tra số lượt, timestamp, status và khả năng tái tính; ghi phạm vi đã đọc. Có thể dùng dữ liệu đó để kết luận recovery hoặc AI tốt hơn không, vì sao? |
| Q08 | Muốn chạy lại demo cũ cần những tiền đề và script nào? Script nào chỉ rebuild, script nào thay đổi/xóa cluster, phần nào cần kiểm tra trước? Tình trạng lab hôm nay đã biết tới đâu từ bằng chứng mình thực sự có? |
| Q09 | Đề xuất một thiết kế thực nghiệm tối thiểu cho ba vector, có benign traffic và các đối chứng cần thiết. Đo gì để đánh giá LLM; khi nào cần single-agent; kiểm soát lộ đáp án, failures, repetitions và chi phí thế nào? Phân biệt containment, availability recovery và sửa lỗ hổng. |
| Q10 | Với ngày 17/10 và mục tiêu cuối tháng, ba việc nên làm đầu tiên là gì, phụ thuộc/bằng chứng hoàn thành là gì? Đề xuất cách chia Codex–Claude không sửa trùng file và cách bàn giao. Chỉ đề xuất, chưa tự nhận task hoặc triển khai. |

## D. Claude Code điền tại đây

Thay các ô CHƯA ĐIỀN bằng nội dung thực tế; UNKNOWN là câu trả lời hợp lệ nếu trung thực và có cách xác minh tiếp. Không xóa câu hỏi hoặc tự điền phần đánh giá E.

### D1. Phiên tiếp nhận và độ phủ nguồn

- Thời điểm bắt đầu/kết thúc, timezone: Bắt đầu **2026-10-17 ~16:39 Asia/Saigon (UTC+7)** (xác nhận bằng `date` LIVE_READ_ONLY); phần D hoàn tất trong cùng phiên, cùng buổi chiều. Không chạy qua đêm.
- Công cụ/model nếu biết; phạm vi hội thoại thực sự nhìn thấy: Claude Code (Opus). Chỉ nhìn thấy đúng một tin nhắn giao việc của Hoàng + AGENTS.md + context tự đính kèm trong phiên này. KHÔNG nhìn thấy hội thoại gốc Hoàng–thầy hay Hoàng–Codex; bối cảnh ở phần B được tiếp nhận như USER_CONTEXT do Codex chuyển lại, không tự nhận đã nghe trực tiếp.
- Repo, branch, HEAD; trạng thái dirty trước/sau: `main` tại HEAD **f9623a31c1062adb1ca7880041b4183cc8a7d28f** (LIVE_READ_ONLY `git rev-parse`). Trước và sau khi làm, chỉ một file untracked duy nhất là chính handoff này (`?? docs/handoff/2026-10-17-claude-code-hydration-handoff.md`); không có file tracked nào bị sửa. Toàn bộ số dòng trích dưới đây lấy ở HEAD này; commit f9623a3 chỉ thêm docs/cấu hình `.agent`, không đụng mã agent/worker nên số dòng mã trùng với các review cũ (baseline 6337b31).
- GitNexus freshness và cách tra cứu thực tế: **KHÔNG dùng được trong phiên này** — MCP `gitnexus://` không có trong bộ công cụ hiện tại và không chạy CLI (lượt hydration cấm cài/chạy ngoài phạm vi đọc). Đã thay bằng `rg`/grep + đọc trực tiếp source. Thư mục `.gitnexus/` gitignored chưa kiểm tra freshness; không coi graph là bằng chứng runtime (đúng tinh thần AGENTS.md).
- DOCX đã đọc hay không, phần đã đọc: **CHƯA ĐỌC trực tiếp.** `C:\Users\ACER\Downloads\HĐ5_...docx` nằm ngoài repo và lượt này không mở/convert tài liệu ngoài. Thông tin về DOCX (năm học 2025–2026, thời gian 01–06/2026, ngày 04/01/2026) được tiếp nhận ở mức HISTORICAL_EVIDENCE qua phần đọc `word/document.xml` ghi trong `docs/reviews/2026-10-09-research-alignment-audit.md` và `docs/handoff/2026-10-09-antigravity-handoff-review.md` (H02); chưa tự xác minh nội dung gốc.

| Nguồn/đường dẫn | Đã đọc phần nào | Truy cập được? | Giới hạn/mâu thuẫn cần giữ |
| --- | --- | --- | --- |
| `AGENTS.md`, `.agent/rules/CONTEXT.md`, `.agent/workflows/session_memory.md` | Toàn bộ | Có | CONTEXT/session_memory cập nhật 2026-07-11/14, ghi "Phase 1–6 COMPLETE/100%" — là khẳng định cũ cần xác minh; nhãn Complete không phải bằng chứng vận hành hôm nay |
| `docs/plans/2026-10-09-research-recovery-roadmap.md` | Dòng 1–301 (phạm vi, AI, RQ, đối chứng, R0–R1); phần R2–R7 chỉ lướt | Có | Lịch lập 09/10, chưa lập lại theo phiên 17/10; quá due ≠ DONE. Quyết định mới nhất (giữ cả ba vector) ở phần B của handoff này |
| `agent-orchestrator/{nemesis,gaia,hephaestus}/main.py` | Toàn bộ | Có | SOURCE_VERIFIED tại HEAD; chưa chạy nên hành vi runtime chưa chứng minh |
| `chaos-worker/` (cmd/main.go, internal/attack/*, validation/target.go, executor.go) | Toàn bộ các file lõi | Có | Registry executor chỉ có 4 loại; không có SQLi executor |
| `infrastructure/scripts/{experiment_runner_direct.py,analysis.py}` | Toàn bộ | Có | Runner inject alert trực tiếp; phương pháp đo có khiếm khuyết (xem Q07) |
| `docs/experiments/raw_data/**` (8 CSV) + `analysis/summary_statistics.csv` | Đọc summary + sample E3; đếm file/dòng | Có | 8 CSV, 40 dòng, attack_start = 2026-06-25 |
| `infrastructure/manifests/{nemesis-deployment,network-policies}.yaml`, `k3d-config.yaml` | Toàn bộ | Có | Secret LLM để trống trong manifest; CNI mặc định Flannel bỏ qua NetworkPolicy |
| `docs/runbooks/2026-10-09-legacy-demo-restart.md` | Toàn bộ | Có | Chỉ đọc để đánh giá cách khởi động lab; không chạy bước nào |
| `docs/reviews/*` (audit + antigravity review), `docs/handoff/2026-10-09-antigravity-*` | Toàn bộ audit + review; handoff Gemini gốc chỉ tham chiếu | Có | Dùng làm nguồn kết luận trước đó để đối chiếu, không thay source cho tuyên bố SOURCE_VERIFIED |
| DOCX thuyết minh (HĐ5) | Không mở | Không (ngoài repo, ngoài phạm vi lượt này) | Chỉ có HISTORICAL_EVIDENCE qua review; nội dung gốc = UNKNOWN |
| Cluster/Docker/K8s runtime, Ollama/LLM endpoint | Không truy vấn | Không (lượt hydration không chạm lab) | Trạng thái lab hôm nay = UNKNOWN; cần inventory ở lượt sau |

### D2. Hiểu dự án bằng lời của mình

ZERO DOOR là một hệ tự phục hồi microservices chạy trên K3d local, tổ chức theo ba tác tử: **Nemesis** (red team — tạo/kích hoạt tấn công), **Gaia** (observer — phát hiện bất thường), **Hephaestus** (blue team — thực thi hành động chữa lỗi trên Kubernetes). Mục tiêu nghiên cứu là trình diễn vòng "gây lỗi → phát hiện → tự phục hồi" và đo MTTD/MTTR/uptime, đồng thời (theo roadmap) chứng minh **giá trị của LLM và của việc chia vai trò tác tử** bằng đối chứng, không chỉ chạy được demo.

Chuỗi vận hành thực tế trong mã: Nemesis (FastAPI) nhận yêu cầu REST → publish lệnh lên Kafka `attack.commands` → chaos-worker (Go) validate blast radius rồi thực thi (HTTP flood / CPU-mem stress pod / pod kill) → kết quả về `attack.results`. Song song, Gaia poll Prometheus mỗi 15s và quét log Elasticsearch, khi vượt ngưỡng/khớp chữ ký thì publish alert lên `monitoring.alerts` → Hephaestus consume, tra DECISION_MATRIX (rule thuần) chọn SCALE_UP/RESTART/ROLLBACK/BLOCK_IP và gọi K8s API, ghi `heal_history` in-memory.

Phần cốt lõi còn thiếu/yếu (đã truy vết ở Q02–Q07): (1) **không có executor SQLi** trong chaos-worker — một trong ba vector đã đăng ký; (2) **không tác tử nào gọi LLM trong vòng phát hiện/chữa lỗi** — chỉ Nemesis có mã tích hợp LLM để chọn kế hoạch tấn công, Gaia/Hephaestus hoàn toàn theo rule; (3) **ROLLBACK chỉ bump annotation** chứ không hoàn nguyên image/config; **BLOCK_IP** thường nhận IP `0.0.0.0` và chạy trên CNI Flannel vốn bỏ qua NetworkPolicy; (4) **dataset 40 lượt được tạo bằng cách inject alert trực tiếp vào Hephaestus**, MTTD/MTTR/uptime vì thế không chứng minh phát hiện thật hay phục hồi nghiệp vụ; (5) dashboard tổng hợp KPI bằng số ước lượng + `Math.random()`.

Quyết định mới nhất của Hoàng (phần B, 17/10): **giữ đủ cả ba vector SQLi + DDoS L7 + resource exhaustion**, giữ các hành động scale/block IP/rollback và KPI gốc (MTTD <60s, MTTR <2–3 phút, uptime ≥99,9%). Không thu hẹp về chỉ SQLi; không hạ ngưỡng. Claude Code ở đây là công cụ viết/kiểm mã cùng Codex, chưa phải backend LLM cho các tác tử.

### D3. Trả lời Q01–Q10

Cho mỗi câu dùng cấu trúc: **Kết luận → Nhãn bằng chứng → Nguồn cụ thể → Giới hạn/chưa biết → Cách kiểm chứng tiếp nếu cần.** Có thể thêm bảng/sơ đồ văn bản khi giúp giải thích. Không lấp UNKNOWN bằng suy đoán.

- **Q01 — Mục tiêu, sản phẩm, KPI, phạm vi hiện hành:**
  - **Kết luận:** Sản phẩm là hệ ba tác tử tự phục hồi microservices trên Kubernetes với target Google Online Boutique; phạm vi hiện hành gồm **ba vector SQLi + DDoS L7 + resource exhaustion**, các hành động scale up/down + block IP + rollback, và KPI **MTTD <60s, MTTR <2–3 phút, uptime ≥99,9%** trên ≥5 microservices. Mục tiêu nghiên cứu (theo roadmap) còn phải trả lời RQ về giá trị LLM và chia vai trò qua đối chứng, không chỉ đạt chức năng.
  - **Nhãn:** USER_CONTEXT cho quyết định phạm vi/KPI; SOURCE_VERIFIED cho phần đã có mã; HISTORICAL_EVIDENCE cho DOCX.
  - **Nguồn:** Phần B dòng 23–24 (giữ ba vector, KPI gốc) và roadmap `docs/plans/2026-10-09-research-recovery-roadmap.md:15`. Cam kết DOCX (≥5 microservices, ba vector, KPI) lấy qua `docs/reviews/2026-10-09-research-alignment-audit.md:29-39`. Đề xuất kỹ thuật (API LLM làm backend chính, fixture SQLi) ở roadmap dòng 9, 148–152.
  - **Phân biệt:** *Xác nhận của Hoàng* = giữ ba vector + Python/Go + Boutique + KPI gốc (B). *Cam kết DOCX* = mục 9/11/13 thuyết minh (qua review). *Đề xuất kỹ thuật chưa chốt* = chọn provider LLM, thêm fixture SQLi SQLite, phạm vi B3. *Chờ xác nhận* = nơi/điều kiện nhận bài kỷ yếu, nguồn thời hạn (01–06/2026 trong DOCX vs 31/12/2026 do Hoàng xác nhận).
  - **Giới hạn/kiểm chứng tiếp:** Nội dung DOCX gốc = UNKNOWN (chưa mở); cần đọc trực tiếp DOCX để chốt chính xác câu chữ mục 9.

- **Q02 — Đường tấn công REST/UI → Nemesis → Kafka → Go worker → kết quả:**
  - **Kết luận:** Có hai đường. **Manual:** `POST /attack/trigger` → `build_attack_command` → publish `attack.commands`. **LLM:** `POST /attack/llm-plan` → `generate_attack_plan_from_llm` (gọi Gemini/OpenAI/Ollama, đọc metrics Prometheus làm context) → parse JSON → publish cùng topic. Chaos-worker consume, `validator.ValidateNamespace` + `ValidateURL`, tra map executor theo `AttackType`, chạy trong goroutine, trả `attack.results`; Nemesis có loop consume results chỉ để log.
  - **Khác biệt manual vs LLM & tác dụng phụ health-check:** Manual ép `duration = max(durationSec, 90)` (`nemesis/main.py:434`); LLM kẹp `min(max(raw,90),120)` (`:477-478`). Vì cả hai **luôn chạy tối thiểu 90 giây**, gọi nhầm endpoint này để "health-check" sẽ **thực sự phát một lượt tấn công ≥90s** vào target-app, không phải thao tác đọc vô hại; `/attack/llm-plan` còn tiêu một lượt gọi LLM thật. Health-check đúng phải dùng `GET /healthz` (`:413`).
  - **Nhãn:** SOURCE_VERIFIED.
  - **Nguồn:** `agent-orchestrator/nemesis/main.py:427-510`, `chaos-worker/cmd/main.go:93-205`, `chaos-worker/internal/validation/target.go:30-74`, `chaos-worker/internal/attack/executor.go:33-54`.
  - **Giới hạn:** Chưa chạy nên không có bằng chứng runtime một lệnh đi hết chuỗi; Kafka là quan hệ động, graph không chứng minh. `ValidateURL` so khớp chuỗi con chứ không parse host (`target.go:44-58`) — lỗ hổng kiểm soát (trùng F09). Kiểm chứng tiếp: chạy một lệnh với run_id xuyên suốt và đọc log 3 thành phần.

- **Q03 — Đường quan sát → Gaia → alert → Hephaestus → Kubernetes → xác nhận phục hồi:**
  - **Kết luận:** Gaia `monitoring_loop` poll Prometheus (CPU/mem/5xx/latency/restart) + quét ES log mỗi 15s → `publish_alert` lên `monitoring.alerts` với dedup theo (service, type) trong 60s → Hephaestus `_kafka_consumer_thread` → `process_alert` → `decide_action` (DECISION_MATRIX) → executor K8s → ghi `heal_history`. **Hậu điều kiện phục hồi gần như không có:** chỉ RESTART chờ pod mới Ready tối đa 60s (`hephaestus/main.py:247-266`); SCALE_UP/ROLLBACK/BLOCK_IP trả SUCCESS ngay khi K8s API chấp nhận, **không probe giao dịch nghiệp vụ**. Vậy status "SUCCESS" = API chấp nhận/pod Ready, **không phải RECOVERY_VERIFIED**.
  - **Dữ liệu thực có vs mất liên kết:** Alert Gaia có `alertId` nhưng **không mang `commandId` của Nemesis** → không có ID xuyên suốt attack→detect→heal; `heal_history` lưu `alertId` nhưng in-memory, mất khi restart và cap 200. Với SQLi/SUSPICIOUS_LOG, Gaia đặt `service = container_name` và **không gắn `sourceIP`** (`gaia/main.py:338-346`) → mất dữ liệu nguồn cho BLOCK_IP.
  - **Phát hiện thật vs inject trực tiếp:** `POST /heal/trigger` (`:575`) tạo alert giả nạp thẳng vào `process_alert`, **bỏ qua Gaia và Kafka**. Đây chính là đường mà experiment runner dùng (xem Q07) → cái gọi là "detect" trong dataset không phải Gaia phát hiện.
  - **Nhãn:** SOURCE_VERIFIED (mã); HISTORICAL_EVIDENCE (hành vi dataset).
  - **Nguồn:** `agent-orchestrator/gaia/main.py:85-121,145-264,266-349`; `agent-orchestrator/hephaestus/main.py:89-101,104-110,415-483,575-590`.
  - **Giới hạn/kiểm chứng tiếp:** Chưa chạy nên chưa thấy một chuỗi Kafka thật; cần event bền + ID xuyên suốt + probe độc lập (R1) để phân biệt phát hiện thật.

- **Q04 — Ma trận ba vector SQLi / DDoS L7 / resource exhaustion:**

  | Vector | Executor | Target | Nguồn bằng chứng tác động | Detector | Hành động | Cleanup | Phần thiếu |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | **SQLi** | **KHÔNG CÓ** trong registry (`cmd/main.go:65-82`) | — | — | Gaia khớp chữ ký log "UNION SELECT"/"OR '1'='1'" (`gaia/main.py:292-293,326-329`) | map → BLOCK_IP nhưng không có sourceIP | — | Toàn bộ chuỗi tấn công SQLi + mục tiêu dễ tổn thương + truyền IP nguồn |
  | **DDoS L7** | `HTTPFloodExecutor` (goroutines GET) | Service DNS nội bộ `http://<svc>.<ns>.svc.cluster.local` (`http_flood.go:36-39`) | Chỉ `requestsSent`, **status luôn SUCCESS** (`:104`) | Gaia dùng metric **ingress** 5xx/latency (`gaia/main.py:203,224`) | HIGH_ERROR_RATE→SCALE_UP/ROLLBACK | ngắt theo duration | Flood đi thẳng service, **không qua ingress** → lệch đường đo detector; không phân biệt một nguồn vs phân tán |
  | **Resource exhaustion** | `CPUStressExecutor` (dùng cho CPU_STRESS và MEMORY_STRESS) | **Pod stress riêng** `progrium/stress` nhãn `app=chaos-stress` (`cpu_stress.go:51-97`) | status SUCCESS, không đo app | Gaia ánh xạ `<svc>-stress-*`→svc (`gaia/main.py:123-131`) nên CPU cao là **của chính pod stress** | HIGH_CPU→SCALE_UP/RESTART | auto-delete pod sau duration (`:124-130`) | Không chứng minh app mục tiêu bị cạn tài nguyên/suy giảm nghiệp vụ |

  - **Boutique có mục tiêu SQLi phù hợp không:** Không được chứng minh. Boutique là microservices gRPC, không có endpoint SQL rõ ràng; repo không có DB SQL hay route dễ tổn thương. **Đề xuất fixture (roadmap:148-152):** thêm một dịch vụ tìm kiếm/catalog thử nghiệm dùng SQLite, có bản dễ tổn thương + bản tham số hóa, chỉ trong namespace nghiên cứu; đo availability mua hàng Boutique riêng với containment SQLi trên fixture.
  - **Nhãn:** SOURCE_VERIFIED; trùng F06 của audit. **Giới hạn:** POD_KILL tồn tại nhưng là fault hạ tầng bổ sung, không thay SQLi.

- **Q05 — block IP / rollback / scale trong mã hiện tại:**
  - **Block IP:** `action_block_ip` (`hephaestus/main.py:323-393`) tạo NetworkPolicy allow `0.0.0.0/0` _except_ `<sourceIP>/32`. IP lấy từ `alert["sourceIP"]`, nếu rỗng thì regex tách IP từ `description`, fallback **`0.0.0.0`** (`:459-464`). Enforce tại NetworkPolicy namespace target-app, TTL 300s qua `threading.Timer` in-memory. **Giới hạn:** Gaia không gắn sourceIP nên thực tế thường là `0.0.0.0` (chặn rỗng); `k3d-config.yaml` không cài CNI hỗ trợ policy và `network-policies.yaml:4-5` ghi rõ **Flannel mặc định của K3s bỏ qua NetworkPolicy** → tạo policy thành công **≠** chặn thật.
  - **Rollback:** `action_rollback` (`:282-320`) chỉ patch annotation `hephaestus.io/rollback-triggered` vào pod template → kích hoạt rollout **cùng image/config**, **không** hoàn nguyên về revision tốt trước đó. Tên "rollback" sai nghĩa; thực chất là rolling-restart.
  - **Scale:** `action_scale_up` (`:177-212`) `+1` replica, cap `MAX_REPLICAS=3`, trả SUCCESS ngay khi patch API thành công (không chờ Ready). **Không có SCALE_DOWN trong DECISION_MATRIX** (`:89-101`); scale-down về 1 chỉ xảy ra trong `/experiment/reset` (`:629-653`) — là reset thí nghiệm, không phải tự phục hồi sau khi tải giảm. Không có hysteresis.
  - **Phân biệt API chấp nhận vs tác dụng thật & NAT/proxy/HPA:** Cần đo (a) block: client tấn công bị chặn **trong khi** benign client còn mua hàng được, kiểm tra IP nguồn trước NAT/ingress và xác nhận CNI enforce; (b) rollback: so image/config trước-sau; (c) scale: chờ replicas Ready + probe nghiệp vụ, và tránh HPA giành quyền replicas (`target-app-hpa.yaml` tồn tại — chưa đọc chi tiết, cần đối chiếu).
  - **Nhãn:** SOURCE_VERIFIED; trùng F05. **Kiểm chứng tiếp:** chạy từng action với probe độc lập + kiểm tra CNI thật của cluster.

- **Q06 — Agent nào gọi LLM, agent nào rule/template:**
  - **Kết luận:** Chỉ **Nemesis** có mã gọi LLM, và chỉ ở đường `/attack/llm-plan` để **chọn kế hoạch tấn công** (provider openai/ollama/gemini, có round-robin key Gemini, fallback giữa key). **Gaia** = threshold + chữ ký log thuần (không LLM). **Hephaestus** = DECISION_MATRIX rule thuần (không LLM). Vòng phát hiện→chữa lỗi **không có LLM nào**.
  - **Cấu hình/fallback/trace:** `nemesis-deployment.yaml:17` chọn `NEMESIS_LLM_PROVIDER=gemini`, `GEMINI_MODEL=gemini-3.1-flash-lite`, nhưng Secret `OPENAI_API_KEY`/`GEMINI_API_KEYS` để **trống** trong manifest (`:38-39`). Nếu không có key và lỗi, `generate_attack_plan_from_llm` trả None → endpoint 500; manual trigger không cần LLM. "Reasoning chat" trên dashboard (`/api/chat`) **không phải output LLM** mà là câu template cứng theo action (`nemesis/main.py:650-665`) và cảnh báo "Gaia" bịa ra bằng cách Nemesis tự đọc Prometheus (`:670-705`).
  - **Tách mã tích hợp vs backend đang hoạt động:** Có mã tích hợp LLM **≠** agent đang chạy với LLM. Trạng thái Secret runtime và một lượt gọi model thật = UNKNOWN (cluster không truy vấn; roadmap:48 ghi Ollama localhost:11434 trước đó không trả lời).
  - **Claude Code có đổi câu trả lời này không:** Không. Claude Code là công cụ viết/kiểm mã trong IDE; không phải backend LLM của các tác tử. Việc dùng Claude để code không biến Gaia/Hephaestus thành agent LLM.
  - **Nhãn:** SOURCE_VERIFIED (mã); UNKNOWN (gọi model runtime). Trùng F07/H05.

- **Q07 — MTTD/MTTR/uptime trên dashboard và runner tạo từ mốc nào:**
  - **Kết luận:** Dataset chính thức **không đo phát hiện thật cũng không đo phục hồi nghiệp vụ.** Docstring runner tự ghi: "MTTD = attack injection → Hephaestus logs heal" (`experiment_runner_direct.py:7-9`). E1/E2/E4 inject alert qua `/heal/trigger` (`:201-223,289-306`), E3 kill pod thật rồi vẫn tự inject POD_CRASH. "detect" = lần đầu thấy event trong `/heal/history`; "heal end" = lần sau thấy status ∈ SUCCESS/FAILED/PARTIAL (`:317-353`), poll 1s → **MTTR ≈ 1,01s là khoảng cách hai lần quan sát, không phải thời gian phục hồi.**
  - **Đọc lát dữ liệu (phạm vi đã đọc):** 8 CSV / 40 dòng, mọi `attack_start` = 2026-06-25 (provenance: commit `a179aad` 2026-06-25 "complete War Game experiment suite"; LIVE_READ_ONLY `git log`). Summary: E3 AUTO `heal_success_rate=20%` **nhưng** `mttr_mean=1,01s` và `uptime=100%`. Raw E3 AUTO: run#1 SUCCESS mttd=11,26 mttr=1,01; **run#2–5 FAILED vẫn ghi mttr≈1,01, uptime=100%** (`raw_data/e3_pod_kill/results_20260625T154325.csv`). Tức FAILED vẫn góp MTTR vào trung bình. `analysis.py:79` chỉ loại dòng mttd<0, giữ FAILED; `:100` đếm MANUAL là "heal thành công"; P95 summary 9,24s ≠ max raw 11,26s.
  - **Uptime:** `measure_uptime` query `avg(up{namespace="target-app"}) or vector(1)` (`:162-173`) — `up` là scrape-success của Prometheus, thiếu series → 1, exception → 99, **không phải availability nghiệp vụ**; `false_positives` gán cứng 0.
  - **Dashboard:** `updateSREStats` trong `static/app.js:652-705` tính MTTD/MTTR bằng dải cứng theo action + `Math.random()` (vd `:669,671,673,675`) và fallback cứng "25.6s"/"12.3s"/"100.00%". Đây là số ước lượng client-side, không dùng chung nguồn với runner.
  - **Dùng để kết luận recovery hay AI tốt hơn?** **Không.** Không có AI trong vòng chữa lỗi; dataset bỏ qua Gaia; MTTR/uptime là artifact đo lường; FAILED bị tính lẫn. Chỉ nên giữ làm lịch sử chẩn đoán, đo lại theo protocol mới (R1/R5).
  - **Nhãn:** SOURCE_VERIFIED + HISTORICAL_EVIDENCE. Trùng F01–F04, H03–H04.

- **Q08 — Tiền đề/script chạy lại demo cũ; rebuild vs thay đổi cluster; trạng thái lab:**
  - **Kết luận:** Theo `docs/runbooks/2026-10-09-legacy-demo-restart.md`: trước hết kiểm tra Docker/context/`k3d cluster list`/container; nếu cluster tồn tại mà dừng thì `k3d cluster start zero-door` + merge kubeconfig; mở port-forward 9091/9092/9090 + Boutique qua ingress 8080; kiểm `/healthz` rồi demo manual PodKill → HTTP Flood. Cần Docker Desktop chạy, cluster zero-door còn, image đã import, Kafka/Prom/ES/Boutique hoạt động.
  - **Script chỉ rebuild/khởi động (an toàn):** `start-demo.ps1` (kiểm tra + port-forward), `rebuild-nemesis.ps1` (build/import/rollout **chỉ** Nemesis — **không** tạo cluster), `k3d cluster start`. **Script thay đổi/xóa cluster (nguy hiểm):** `infrastructure/scripts/recreate-cluster.ps1` → **`k3d cluster delete zero-door`** rồi chỉ dựng lại Phase 1 (`recreate-cluster.ps1:20-24`); `setup-phase1.ps1` (`:72` tạo cluster mới); `experiment_runner_direct.py`/`/experiment/reset` thay đổi replicas + xóa `heal_history`/NetworkPolicy. **Cần kiểm tra trước:** inventory Docker/context/volume, giữ dữ liệu cần giữ, không `delete`/`prune`.
  - **Trạng thái lab hôm nay:** **UNKNOWN từ bằng chứng của chính phiên này** — không truy vấn Docker/K8s trong lượt hydration. HISTORICAL_EVIDENCE (roadmap:47, runbook:5): snapshot 09/10 thấy context `k3d-zero-door`, API `127.0.0.1:58117` từ chối, truy vấn Docker timeout; các quan sát đó **không** chứng minh container đã exited hay cluster còn tồn tại.
  - **Nhãn:** SOURCE_VERIFIED (script); HISTORICAL_EVIDENCE (snapshot cũ); UNKNOWN (lab hiện tại). **Kiểm chứng tiếp:** lượt sau chạy inventory chỉ đọc (R0-T02-S01).

- **Q09 — Thiết kế thực nghiệm tối thiểu cho ba vector + benign + đối chứng:**
  - **Đề xuất (INFERENCE dựa roadmap §đối chứng/case):** Với mỗi vector chạy các cấu hình **B0 (K8s/HPA mặc định, ZERO DOOR không heal)**, **B1 (RULES)**, **B2 (MULTI_LLM: Gaia+Hephaestus dùng LLM)**, tùy nguồn lực thêm **B3 (SINGLE_LLM)** và giữ **BM (MANUAL)**. Kèm case lành tính **C0 (ổn định)** và **C1 (khách hợp lệ tăng)** để đo false alarm/false action; **C2 DDoS L7**, **C4 resource exhaustion**, **C5 SQLi trên fixture**; replay cùng kế hoạch tải/fault + seed cho mọi nhóm.
  - **Đo gì để đánh giá LLM:** tỷ lệ phục hồi **được probe nghiệp vụ xác nhận**/tổng lượt; độ đúng hành động đầu tiên so tập hành động chấp nhận được (đã khóa trước chạy); decision latency, số call/token, retry/fallback, chi phí — tách chi phí tạo kế hoạch Nemesis khỏi chi phí quyết định phục hồi; false action ở C0/C1. Giữ MTTD/MTTR/uptime gốc nhưng **MTTR báo kèm tỷ lệ failure**, FAILED/timeout vẫn ở mẫu số.
  - **Khi nào cần single-agent (B3):** chỉ bắt buộc nếu muốn claim "chia vai trò tốt hơn" (RQ2); nếu thiếu nguồn lực thì bỏ claim đó, không bỏ cam kết gốc.
  - **Kiểm soát lộ đáp án/failures/lặp/chi phí:** harness giữ ground truth (nguyên nhân, thời điểm, tập action đúng) tách khỏi telemetry cấp cho bên chữa lỗi; dùng ID trung tính, không đưa tên case/loại attack/"hãy rollback" vào prompt/alert; khóa RQ/metric/prompt/model/version trước formal run; đủ số lặp cho P95, báo độ bất định; đặt max calls/token/timeout + tracking để chặn chi phí.
  - **Phân biệt:** **containment** (chặn nguồn/lan rộng, vd block IP, SQLi trên fixture) ≠ **availability recovery** (giao dịch Boutique phục hồi) ≠ **vulnerability remediation** (vá lỗ hổng — scale/restart **không** sửa SQLi). Báo ba khái niệm riêng.
  - **Nhãn:** INFERENCE/đề xuất; nền tảng là roadmap dòng 88–134.

- **Q10 — Ba việc đầu tiên tính từ 17/10 + phối hợp Codex–Claude:**
  - **Kết luận (3 việc, theo thứ tự phụ thuộc):**
    1. **Inventory + khôi phục lab (R0-T02) và xác nhận một backend LLM thật (R0-T03).** Phụ thuộc: không. Bằng chứng hoàn thành: K8s API truy cập được, ≥5 service phục vụ giao dịch Boutique, Kafka/Prom/log hoạt động, một lượt gọi LLM có schema + run_id/latency. *Là tiền đề cho mọi đo đạc.*
    2. **Sửa event contract + phép đo (R1): ID xuyên suốt attack→detect→heal, event bền, probe nghiệp vụ độc lập, bỏ KPI ngẫu nhiên/fallback, tách MANUAL/RULES/AI.** Phụ thuộc: #1. Bằng chứng: tái tính MTTD/MTTR từ raw; FAILED/PARTIAL không tự thành recovery; dashboard dùng chung nguồn với analysis.
    3. **Hoàn thiện ba vector đúng target (R2): fixture SQLi, HTTP flood đi đúng đường đo, resource stress tác động app thật, có cleanup.** Phụ thuộc: #1, #2. Bằng chứng: mỗi vector có attack_effect evidence; SQLi phân biệt payload với request thường; resource suy giảm nằm ở target thật.
  - **Phối hợp Codex–Claude (đề xuất):** một owner cho mỗi tập file mỗi lượt, giao bằng task ID + HEAD + phạm vi; bên kia review diff + bằng chứng. Gợi ý chia **không trùng file**: Claude Code → mã agent Python (`agent-orchestrator/*`) và Go worker (`chaos-worker/*`) + test; Codex → script đo/phân tích (`infrastructure/scripts/*`) + manifests/infra; tài liệu/paper do Hòa, Hoàng duyệt. Việc #1 (lab/LLM) cần Hoàng chạy vì chạm máy/credential.
  - **Nhãn:** INFERENCE/đề xuất; nền tảng roadmap R0–R2. **Giới hạn:** Đây chỉ là đề xuất, chưa tự nhận task; phân công chốt khi Hoàng duyệt.

### D4. Đối chiếu review và những điều dễ hiểu sai

**Đồng ý sau khi tự truy vết mã (không chỉ chép):**
- **F01/F02/H03/H04 — phép đo bỏ qua detector, MTTR không phải thời gian phục hồi.** Tự xác minh ở `experiment_runner_direct.py:7-9,201-223,317-353` + raw E3 (4/5 FAILED vẫn mttr≈1,01) + `analysis.py:79,100`. Đồng ý: dataset đo "inject→log heal", không chứng minh phát hiện/recovery.
- **F03 — uptime từ `up`/vector(1), FPR gán 0.** Xác minh `experiment_runner_direct.py:162-173`. Đồng ý không phải availability nghiệp vụ.
- **F04 — dashboard trộn số ước lượng + `Math.random()`.** Tự grep `static/app.js:652-705`. Đồng ý.
- **F05 — rollback chỉ bump annotation; scale SUCCESS khi API ok; block IP có thể 0.0.0.0; không có SCALE_DOWN.** Xác minh `hephaestus/main.py:282-320,177-212,323-393,89-101`. Đồng ý.
- **F06/H07 — CPU stress là pod riêng, Gaia map tên stress→service; HTTP flood đi service DNS còn detector dùng metric ingress.** Xác minh `cpu_stress.go:51`, `gaia/main.py:123-131,203,224`, `http_flood.go:36-39`. Đồng ý.
- **F07 — SQLi không có executor; chỉ Nemesis tích hợp LLM; Gaia/Hephaestus rule.** Xác minh registry `cmd/main.go:65-82` + grep SQLi chỉ thấy ở signature Gaia. Đồng ý.
- **H03 — 8 CSV/40 dòng, attack_start 2026-06-25.** Tự đếm + `git log` provenance. Đồng ý (bác con số "40 files" trong handoff Gemini).

**Bổ sung mà tôi tự thấy, review nói nhẹ hơn hoặc để ngỏ:**
- **CNI Flannel bỏ qua NetworkPolicy:** `network-policies.yaml:4-5` ghi rõ Flannel mặc định K3s bỏ qua policy, `k3d-config.yaml` không cài Calico, `setup-phase1.ps1:72` tạo cluster từ config đó. Suy ra (INFERENCE) BLOCK_IP gần như **không enforce** trên lab mặc định — mạnh hơn mức "cần kiểm chứng policy/CNI" của F05. Cần xác minh CNI runtime thật.
- **Tác dụng phụ health-check (Q02):** cả `/attack/trigger` và `/attack/llm-plan` ép tối thiểu 90s → gọi nhầm để "kiểm tra" là phát tấn công thật; đây là rủi ro vận hành review không nêu rõ.

**Chưa xác minh / để UNKNOWN:**
- Nội dung DOCX gốc (H02): chỉ có HISTORICAL_EVIDENCE qua review, chưa tự mở. Không tự kết luận có/không gia hạn; nguồn thời hạn 01–06/2026 vs 31/12/2026 vẫn là khác biệt chờ hồ sơ.
- Mọi khẳng định runtime (gọi LLM thật, cluster còn sống, benchmark RAM 157MB/giảm 88% ở H07/F10): UNKNOWN, cần log thực thi.

**Không đồng ý/điều chỉnh:** Không có mâu thuẫn lớn với hai review — chúng thận trọng và khớp mã. Chỉ nhấn rằng kết luận của review là *nguồn thứ cấp*; phần trên tôi đã đọc source trực tiếp nên nâng các mục đó lên SOURCE_VERIFIED, trừ các mục runtime vẫn UNKNOWN.

### D5. Unknowns, blockers và câu hỏi thực sự cần Hoàng

| Vấn đề | Đã tìm ở đâu | Vì sao quan trọng | Tự kiểm tra tiếp hay cần Hoàng trả lời? |
| --- | --- | --- | --- |
| Trạng thái lab hôm nay (cluster/pod/Kafka/Prom/ES còn sống?) | roadmap:47, runbook:5 (snapshot 09/10); không truy vấn trong lượt này | Quyết định start vs recreate; là tiền đề mọi đo đạc | Tự kiểm ở lượt sau bằng inventory chỉ đọc (R0-T02-S01), không cần hỏi Hoàng |
| Backend LLM nào thực sự gọi được + có key (Gemini/OpenAI/Ollama) | `nemesis-deployment.yaml:17,38-39` (secret trống); roadmap:48 (Ollama không trả lời) | Xác định đường B2/B3 có khả thi; chi phí | Cần Hoàng: cung cấp/kích hoạt key và xác nhận provider; rồi tự test một lượt có schema |
| Nội dung DOCX gốc + nguồn thời hạn (01–06/2026 vs 31/12/2026) | review audit + antigravity (đọc word/document.xml) | Ảnh hưởng mốc nghiệm thu, câu chữ cam kết mục 9 | Cần Hoàng xác nhận/đưa hồ sơ; tôi có thể đọc DOCX nếu được phép mở ở lượt sau |
| Nơi/điều kiện nhận bài kỷ yếu (nộp vs chấp nhận đăng) | roadmap:16; audit:19-23 | Mốc R6/R7, định nghĩa "hoàn thành" | Cần Hoàng/trường; đã có ở B là "chốt sau", không hỏi lại như blocker |
| CNI thật của cluster (Flannel hay Calico) | `k3d-config.yaml`, `network-policies.yaml:4-5` | Quyết định BLOCK_IP có enforce được không | Tự kiểm ở lượt sau (`kubectl get pods -n kube-system`, mô tả CNI); không cần Hoàng |
| `target-app-hpa.yaml` cấu hình HPA ra sao (tranh chấp với healer scale) | Thấy file tồn tại, chưa đọc chi tiết | Ảnh hưởng đối chứng B0 và scale up/down | Tự đọc ở lượt sau |

Không hỏi lại những quyết định đã có ở phần B. Chưa biết trạng thái máy không nhất thiết cần hỏi người dùng nếu lượt sau có thể kiểm tra bằng truy vấn phù hợp.

### D6. Ba việc đầu tiên và đề xuất phối hợp

| Thứ tự | Việc/phạm vi file dự kiến | Phụ thuộc | Đề xuất người làm | Kiểm chứng đầu ra | Ước lượng kèm giả định |
| --- | --- | --- | --- | --- | --- |
| 1 | Inventory + khôi phục lab và xác nhận 1 backend LLM thật. File/khu vực: Docker/K8s runtime, `infrastructure/scripts/setup-phase*.ps1` (chỉ đọc/chạy có kiểm soát), `nemesis-deployment.yaml` secret. (R0-T02, R0-T03) | Không | **Hoàng** chạy (chạm máy/credential); Claude/Codex hỗ trợ đọc script | K8s API truy cập; ≥5 service phục vụ giao dịch Boutique; Kafka/Prom/log hoạt động; 1 lượt LLM có schema + run_id/latency lưu lại | ~3h giao tiếp của Hoàng; giả định cluster còn hoặc dựng lại kịp, có key LLM |
| 2 | Event contract + phép đo: ID xuyên suốt, event bền, probe nghiệp vụ độc lập, bỏ KPI ngẫu nhiên/fallback, tách MANUAL/RULES/AI. File: `agent-orchestrator/*/main.py` (publish/consume + heal_history), `infrastructure/scripts/experiment_runner_direct.py`, `analysis.py`, `nemesis/static/app.js`. (R1) | #1 | **Claude Code** mã agent; **Codex** runner/analysis/dashboard — chia theo file để không trùng | Tái tính MTTD/MTTR từ raw; FAILED/PARTIAL ≠ recovery; dashboard dùng chung nguồn với analysis; probe có timeline thật | ~4h Hoàng duyệt + nhiều lượt code của Claude/Codex; giả định #1 xong |
| 3 | Hoàn thiện ba vector đúng target: fixture SQLi (SQLite, namespace nghiên cứu), HTTP flood đi đúng đường đo, resource stress tác động app thật, cleanup. File: `chaos-worker/internal/attack/*`, executor registry `cmd/main.go`, manifest fixture mới, Nemesis prompt/schema. (R2) | #1, #2 | **Claude Code** worker/agent; **Codex** manifest fixture + đường đo | Mỗi vector có attack_effect evidence; SQLi phân biệt payload vs request thường; resource suy giảm ở target thật; cleanup kiểm chứng | ~5h Hoàng; giả định #2 khóa phép đo trước |

Quy tắc phối hợp đề xuất: một owner sửa mỗi tập file trong từng lượt; giao bằng task ID, HEAD và phạm vi rõ; bên còn lại review diff và bằng chứng; đổi phạm vi phải bàn giao trước. Chưa có phân công được chốt chỉ vì bảng này có tên người làm.

### D7. Nhật ký kiểm tra và phạm vi chưa thực hiện

| Lệnh/truy vấn | Thời điểm | Kết quả rút gọn/exit code | Điều chứng minh và không chứng minh |
| --- | --- | --- | --- |
| `git rev-parse HEAD` / `branch` / `status --porcelain` | 17/10 ~16:39 | `f9623a3…`, `main`, chỉ 1 file untracked (handoff này) | Chứng minh HEAD/branch/dirty của phiên; không chứng minh gì về runtime |
| `git log --oneline -- docs/experiments/raw_data` | 17/10 | `a179aad 2026-06-25 complete War Game…` | Provenance CSV = 25/06; không chứng minh môi trường chạy |
| `cat summary_statistics.csv` + `head` raw E3 | 17/10 | E3 AUTO success 20%, mttr 1,01s, 4/5 FAILED, uptime 100% | Chứng minh khiếm khuyết phương pháp đo; không chứng minh recovery |
| `grep -rni "sqli\|union select\|SQL_INJECTION" chaos-worker agent-orchestrator` | 17/10 | Chỉ khớp signature trong `gaia/main.py`; không có executor | Chứng minh không có SQLi executor; không chứng minh Boutique thiếu/không thiếu endpoint SQL |
| `grep -n "Math.random\|fallback\|mttr\|mttd" static/app.js` | 17/10 | Thấy `Math.random()` + fallback cứng 25.6s/12.3s | Chứng minh dashboard dùng số ước lượng; không chứng minh backend KPI |
| `grep -rni "calico\|flannel\|cni" setup-phase1.ps1 k3d-config.yaml` | 17/10 | Không có cài CNI; chỉ `k3d cluster create --config`; apply network-policies | Suy ra Flannel mặc định bỏ qua NetworkPolicy (INFERENCE); chưa xác minh CNI runtime |

- File đã sửa trong lượt này: **Chỉ `docs/handoff/2026-10-17-claude-code-hydration-handoff.md` (phần D).** Không sửa mã, manifest, dữ liệu, cấu hình, roadmap hay chỉ dẫn agent. Không commit/push.
- Kiểm tra runtime/test nào chưa chạy: **Tất cả.** Không chạy cluster, attack, healing, LLM, experiment runner, test, build/deploy; không truy vấn Docker/K8s/Prometheus/Ollama; không mở DOCX; không dùng GitNexus (không khả dụng).
- Tự đánh giá:
  - *Hiểu chắc (SOURCE_VERIFIED):* kiến trúc ba tác tử + Kafka topics; hai đường attack của Nemesis; Gaia rule-based + ES signature; DECISION_MATRIX Hephaestus; bản chất rollback/scale/block IP; không có SQLi executor; chỉ Nemesis tích hợp LLM; phương pháp đo của runner/analysis và dashboard ước lượng; danh mục script lab.
  - *Cần Codex/Hoàng kiểm thêm:* mọi trạng thái runtime (lab còn sống, LLM gọi được, CNI thật, HPA), nội dung DOCX gốc, điều kiện nhận bài; benchmark RAM/claim ưu thế AIOps.
  - *Sẵn sàng nhận việc:* sau khi Hoàng xong việc #1 (lab + LLM), tôi có thể nhận phần mã agent Python/Go cho R1 (event contract/ID/probe) và R2 (vector), theo phân công không trùng file ở D6. Chưa tự nhận, chờ Hoàng chốt.

## E. Codex đánh giá — 17/10/2026

Không chấm dựa vào độ dài hoặc việc lặp lại audit. Mỗi Q01–Q10 chấm 0–2: **0** sai/bỏ trống/khẳng định không nguồn; **1** hiểu một phần hoặc UNKNOWN được giải thích đúng nhưng thiếu truy vết; **2** đúng, đủ nguồn phù hợp và nêu đúng giới hạn. Với đề xuất Q09/Q10, đánh giá tính hợp lý và gắn với nguồn, không đòi bằng chứng một triển khai chưa tồn tại.

Mốc tham khảo: 16/20 trở lên có thể giao một task hẹp khi không còn hiểu sai cốt lõi liên quan task đó; 12–15 cần bổ sung có mục tiêu; dưới 12 cần tiếp nhận lại. Điểm không tự cho phép sửa mã và không chứng minh hệ thống đạt nghiên cứu. Bịa bằng chứng runtime, nhầm phạm vi chỉ SQLi, nhầm Claude Code với backend, coi status thành recovery hoặc bỏ qua dữ liệu thất bại phải được sửa trước khi giao phần việc liên quan.

### E1. Phạm vi và kết luận

- Review tại HEAD **f9623a31c1062adb1ca7880041b4183cc8a7d28f**, nhánh `main`. Trước review chỉ có file handoff này untracked. Codex giữ nguyên phần D để bảo toàn câu trả lời đã chấm; chỉ cập nhật dòng trạng thái và phần E.
- Đã đọc phần D đầy đủ, đối chiếu mã agent/worker, runner/analysis/dashboard, script khởi động/reset, manifests, inventory CSV và Git history có liên quan. Không chạy ứng dụng, Docker/Kubernetes, tấn công, chữa lỗi hoặc API LLM; không xác nhận lab đang hoạt động.
- GitNexus báo index chậm một commit (`6337b31` → `f9623a3`). Diff hai commit chỉ có docs/chỉ dẫn/cấu hình GitNexus, không có mã agent/worker/runner được kiểm tra; dùng query/context để định vị và source hiện tại để kết luận. Không cần dựng lại index để chấm tài liệu này.
- **Kết luận: 15/20 — đã nắm phần lớn kiến trúc và những thiếu hụt nghiên cứu, nhưng cần bổ sung có mục tiêu.** Có thể tham gia kiểm tra nguồn và chuẩn bị thiết kế một task hẹp. Chưa nên giao toàn bộ Python/Go hoặc cho thay hạ tầng dựa vào kết luận CNI hiện tại. Điểm này đo chất lượng hydration, không đo độ hoàn thiện hệ thống và không chứng minh các lệnh Claude liệt kê đã thực sự được chạy; nhật ký đó là tự báo cáo, còn nội dung có thể tái kiểm tra đã được Codex đối chiếu.

### E2. Điểm từng câu

| Câu | Điểm /2 | Nhận xét |
| --- | --- | --- |
| Q01 | 1 | Đúng phạm vi ba vector, KPI và phân biệt xác nhận/đề xuất. Chưa đọc DOCX gốc; lý do “ngoài repo, ngoài phạm vi” không khớp C1 vốn yêu cầu đọc nếu truy cập được. Cần ghi đúng là chưa thử đọc hay có lỗi truy cập thật. |
| Q02 | 1 | Truy vết đúng hai endpoint, Kafka và worker; đúng là endpoint có tác dụng phụ. Nhưng duration trong command không bảo đảm mọi tấn công chạy ≥90s: POD_KILL thực hiện số lần xóa giới hạn rồi trả kết quả; lệnh cũng có thể thất bại/bị từ chối. |
| Q03 | 2 | Đúng đường Gaia → alert → Hephaestus, thiếu correlation xuyên suốt và probe; phân biệt inject alert với phát hiện thật. |
| Q04 | 2 | Ma trận chỉ ra đúng SQLi executor còn thiếu, HTTP flood mặc định bỏ qua ingress và resource stress ở pod riêng. Không biến thiếu bằng chứng tác động thành khẳng định tuyệt đối rằng không thể ảnh hưởng target. |
| Q05 | 1 | Đúng rollback chỉ đổi annotation, scale chưa chờ hậu điều kiện, thiếu scale-down và IP nguồn. Kết luận Flannel/K3s bỏ qua policy dựa trên comment repo là sai căn cứ kỹ thuật; cần sửa trước task block IP. |
| Q06 | 2 | Đúng Nemesis có đường gọi LLM, Gaia/Hephaestus dùng rules; secret trống trong manifest không chứng minh secret runtime trống. Phân biệt rõ Claude Code với backend tác tử. |
| Q07 | 2 | Đúng lỗi phép đo, FAILED vẫn có MTTR, uptime từ scrape và KPI ngẫu nhiên. Đã tái kiểm tra 8 CSV/40 dòng, ngày attack_start 25/06 và E3 AUTO 4/5 FAILED. Cần làm rõ nguồn lịch sử qua các commit, không đồng nhất ngày dữ liệu với ngày toàn bộ dataset cuối được hình thành. |
| Q08 | 1 | Đúng thứ tự inventory và nguy cơ recreate cluster. Nhưng gọi nhóm script “an toàn” quá rộng, bỏ sót Stop-Process toàn bộ kubectl; mô tả reset xóa NetworkPolicy không đúng endpoint hiện tại. |
| Q09 | 2 | Đối chứng, benign traffic, tránh lộ đáp án và phân biệt containment/recovery/remediation hợp lý; B3 gắn với claim phối hợp, không mặc định mở rộng. Số lặp/ngân sách cụ thể còn phải khóa ở protocol triển khai. |
| Q10 | 1 | Đúng ưu tiên lab/phép đo/vector và nguyên tắc owner. Phân chia agent/dashboard chưa nhất quán giữa D3 và D6; chưa khóa schema chung. Chưa có cơ sở bắt Hoàng tự chạy mọi bước lab hoặc buộc thiết kế R1 chờ backend LLM chạy thật. |
| **Tổng** | **15/20** | **Bổ sung các mục E3; không cần làm lại toàn bộ hydration.** |

### E3. Các chỉnh sửa bắt buộc cho bản bổ sung

**C01 — K3s/Flannel và NetworkPolicy (ưu tiên cao, ảnh hưởng thiết kế block IP).**

Ở D1, D2, Q05, D4 và D7, Claude đã lấy comment `infrastructure/manifests/network-policies.yaml:4-5` làm căn cứ để kết luận policy không enforce. Comment này không đủ tin cậy: [tài liệu chính thức K3s](https://docs.k3s.io/networking/networking-services#network-policy-controller) nêu K3s có Network Policy Controller tích hợp từ thư viện kube-router; tắt bằng `--disable-network-policy`. `infrastructure/k3d-config.yaml:23-27` chỉ khai báo tắt Traefik, không khai báo tắt controller policy. Vì vậy **Flannel không tự chứng minh NetworkPolicy bị bỏ qua trên K3s**. Cũng chưa có bằng chứng runtime để khẳng định lab này đang enforce đúng.

Kết luận thay thế: cơ chế block hiện có thiếu IP nguồn đáng tin và kiểm chứng hiệu lực; trạng thái controller/enforcement thực tế còn UNKNOWN. Cần kiểm tra phiên bản/args K3s, controller và đường traffic, rồi thử attacker/benign theo protocol. `kubectl get pods -n kube-system` đơn lẻ chưa đủ vì controller có thể tích hợp trong tiến trình K3s. Chưa có căn cứ yêu cầu thay CNI hoặc dựng lại cluster. Comment cũ cần sửa ở một task riêng, không nằm trong lượt review này.

**C02 — Phân biệt duration cấu hình với thời gian/tác động thực thi (Q02, D4).**

Nemesis đúng là đặt duration ≥90s ở `agent-orchestrator/nemesis/main.py:434,477-478`, nhưng `chaos-worker/internal/attack/pod_kill.go:78-115` xóa tối đa killCount pod rồi trả kết quả, không lặp suốt duration. `EffectiveDuration` ở `chaos-worker/internal/attack/executor.go:84-95` còn giới hạn thời lượng ở những executor dùng nó. Sửa “luôn thực sự tấn công ≥90s” thành “endpoint có thể phát lệnh gây tác động; duration là tham số, thời gian/tác động phải kiểm tra theo executor và kết quả”. Giữ khuyến nghị dùng GET healthz thay vì POST attack để kiểm tra sức khỏe.

**C03 — Tác dụng phụ script và cleanup/reset (Q08).**

- `start-demo.ps1:30-32` lấy mọi tiến trình tên kubectl rồi Stop-Process -Force; dòng 14 dùng context hiện hành. Không mô tả script này là an toàn vô điều kiện hoặc chỉ mở port-forward.
- `rebuild-nemesis.ps1` build/import/rollout là thay đổi workload/image, không chỉ đọc hoặc “khởi động”. Không cần chạy trong hydration.
- `/experiment/reset` ở `agent-orchestrator/hephaestus/main.py:629-653` xóa cooldown/history và scale các deployment về 1; **không có đoạn xóa NetworkPolicy**. TTL cleanup là đường riêng ở `:396-408`. **Đính chính của Codex sau phản hồi Claude:** runner direct **có** gọi `kubectl delete networkpolicies -n target-app -l hephaestus.io/managed=true --ignore-not-found=true` trong `reset_steady_state()` ở `infrastructure/scripts/experiment_runner_direct.py:143-147`. Nhánh này chưa kiểm tra return code, nên có lệnh cleanup không đồng nghĩa cleanup thành công. Nhận xét trước của Codex rằng runner không có lệnh này là sai; rút lại nhận xét đó. Không gộp runner reset, endpoint reset và TTL cleanup thành một đường.
- Pod stress có thử auto-delete ở `chaos-worker/internal/attack/cpu_stress.go:124-127`, nhưng khi xóa lỗi vẫn có thể trả SUCCESS ở `:134`. Viết “có nhánh thử cleanup”, chưa viết “cleanup đã được bảo đảm”.

**C04 — Phạm vi đọc và mức độ xác minh (D1, D5, D7).**

C1 cho phép đọc DOCX đã được Hoàng chỉ định nếu truy cập được; C1 cũng cho phép GitNexus CLI có sẵn. Không có yêu cầu xin lại chỉ vì file ngoài repo hoặc CLI là một lệnh. Claude có thể ghi chưa thử/không có công cụ, nhưng không tự đổi thành bị cấm hoặc không truy cập được khi chưa có lỗi. Codex đã kiểm tra đường dẫn DOCX tồn tại và có `gitnexus.ps1` trong PATH ở phiên review; điều đó không chứng minh tool/permission của phiên Claude giống hệt. Bổ sung nguồn trực tiếp nếu đọc được; nếu không thì báo thao tác đã thử và giới hạn thật. Không yêu cầu Hoàng cung cấp lại tài liệu đã có chỉ để lấp việc chưa đọc.

Ở D7, câu lệnh `git log --oneline` tự nó không xuất ngày. Review tái kiểm tra được commit `a179aad` ngày 25/06/2026, nhưng history của raw_data còn `54ff513` ngày 12/07 và `0b402e4` ngày 13/07; commit cuối loại một file thử. Ghi riêng ngày nằm trong dữ liệu, ngày commit đưa dữ liệu vào và ngày chỉnh inventory. Không tuyên bố một log gốc đã được kiểm chứng nếu chỉ đang tái dựng kết quả tương đương.

**C05 — Quy tắc phối hợp và phụ thuộc (Q10, D6).**

D3 giao `agent-orchestrator/*` cho Claude nhưng D6 giao `nemesis/static/app.js` cho Codex; cần dùng allowlist chính xác theo file cho từng task, thay vì hai phạm vi chồng nhau. Khóa event schema, field semantics và phép tính trước khi hai bên sửa producer/consumer; ghi owner, base HEAD, đầu ra và người review. Thiết kế contract/kiểm tra nguồn có thể làm khi lab hoặc LLM chưa sẵn sàng; integration/runtime proof mới chờ các đầu vào đó. Không mặc định Hoàng phải tự gõ mọi lệnh chỉ vì chạy trên máy hoặc có credential; phân biệt bước agent được thực hiện với đăng nhập/chọn provider/chi phí cần Hoàng quyết định. Không đưa secret vào file bàn giao.

Các ước lượng 3h/4h/5h trong D6 đang là giờ tương tác của Hoàng với nhiều giả định, chưa là tổng công sức hoặc lịch hoàn thành đã được xác nhận. Không dùng chúng làm bằng chứng kịp cuối tháng; giữ mục tiêu và lập lại lịch sau inventory/phân rã task.

### E4. Những phần đạt và bước giao việc tiếp

Claude đã nắm đúng phạm vi hiện hành, vai trò ba thành phần, thiếu SQLi executor, lệch đường đo HTTP, stress pod riêng, rollback giả nghĩa, nguồn KPI không hợp lệ và sự cần thiết của đối chứng. Các điểm đó đủ để tiếp tục hợp tác, không cần đọc lại repo từ đầu. Không có bằng chứng trong diff local hiện tại về việc sửa app ngoài phạm vi hydration.

**Bước tiếp theo đề nghị:** Claude bổ sung một mục `D8. Phản hồi review Codex` ngay trước phần E, trả lời C01–C05 với nguồn và chỉ rõ kết luận D cũ nào được thay thế; không xóa nội dung cũ để bảo toàn lịch sử chấm. Q01 cần đọc DOCX nếu công cụ cho phép hoặc ghi lỗi/giới hạn thật. Sau đó Codex chấm lại các câu liên quan.

Trong lúc bổ sung, có thể giao một việc chỉ đọc hẹp: lập inventory lab hoặc phác thảo event contract cho R1, không tự deploy/gọi model. **Đây là đề xuất chưa được giao thực thi trong lượt review này.** Task triển khai đầu tiên chỉ chốt sau khi rõ đầu vào và phạm vi file; chưa giao toàn bộ mã agent/worker hay thay CNI.

Điều kiện chấp nhận bản bổ sung: sửa được suy luận CNI; phân biệt duration/API/cleanup với tác dụng runtime; ghi đúng phạm vi đã đọc; đưa ra phân công không chồng file và phụ thuộc hợp lý. Hoàn thành hydration vẫn không đồng nghĩa lab chạy được, KPI đạt hoặc bài báo đủ điều kiện đăng.

### E5. Cập nhật cách bổ sung sau sự cố ghi file — 17/10/2026

Codex đã đọc báo cáo `docs/handoff/2026-10-17-claude-code-session-blockers.md`. Phần D hiện tại khớp SHA-256 của bản đã chấm: `7YDWKteBGwlxrlgdpGPSaJ3bjpHvB/OAtVyKLbPU9As=` (UTF-8 của đoạn sau `## D. `, trước `## E. `). Tiêu đề E và E1–E4 đầy đủ; không có D8 dở. Không có bản hash E cũ độc lập để khẳng định toàn bộ E được phục hồi byte-for-byte. Codex đã sửa chính lỗi nguồn của mình ở E3-C03 như ghi trên; điểm 15/20 là điểm bản D ban đầu, chưa phải chấm lại bản bổ sung.

**Thay quy định đầu ra ở A và yêu cầu chèn D8 ở E4 cho riêng lượt bổ sung tiếp theo:** Claude chỉ ghi bản bổ sung vào `docs/handoff/2026-10-17-claude-code-hydration-d8.md`; giữ nguyên file hydration gốc này và báo cáo blockers. Đây là file bổ sung có liên kết, không tạo một bản hydration độc lập. Codex sẽ đọc và đối chiếu trước khi cập nhật kết luận. Không yêu cầu Claude tự chèn lại vào E hoặc ghi đè bản gốc.

Viết từng mục C01–C05, lưu rồi đọc lại từng mục; khi gián đoạn chỉ tiếp tục mục chưa xong. Không ghi trạng thái COMPLETE trước khi cả năm mục có nội dung. Nguồn DOCX đã được Codex trích đúng phần cần đối chiếu tại `docs/handoff/2026-10-17-registration-requirements-excerpt.md`; Claude có thể dùng nguồn trích thứ cấp này và ghi rõ mình chưa trực tiếp đọc DOCX nếu vẫn bị chặn. Không cần xin quyền Downloads rộng hoặc đọc các tài liệu cá nhân khác.

Đây vẫn là kiểm toán tài liệu và mã của lab nghiên cứu do nhóm sở hữu. Chưa giao chạy lab, thực nghiệm, sửa ứng dụng, cấu hình quyền/model hoặc commit/push. Chi tiết xử lý B01–B04 và lệnh kiểm tra index nhẹ nằm ở phần Codex cuối báo cáo blockers.

### E6. Review bản bổ sung D8 — 17/10/2026: HYDRATION ĐẠT

Nguồn phản hồi: [D8 của Claude](2026-10-17-claude-code-hydration-d8.md), SHA-256 tại lúc review `4476DE00364BB2322A696EB57849C2F98ACDBF815A89081CC096670675314B8D`. Codex đọc toàn bộ D8, đối chiếu các chi tiết mới với source runner, executor/worker, cleanup của Hephaestus, roadmap, bản trích DOCX và Git history. HEAD vẫn `f9623a31c1062adb1ca7880041b4183cc8a7d28f`, không có thay đổi tracked. GitNexus context vẫn chậm một commit chỉ có docs/cấu hình, nên dùng để định vị và đọc mã hiện tại để kết luận.

**Kết luận: đạt yêu cầu tiếp nhận, 19/20 khi đọc D và D8 cùng nhau.** Không cần một vòng viết lại hydration. D8 thay thế các kết luận cũ mà nó chỉ rõ; D và E2 giữ nguyên như lịch sử. Điểm này không xác nhận runtime, chất lượng mã sẽ viết trong tương lai hoặc khả năng Claude không còn bị safeguard chặn.

| Câu | Trước → sau | Căn cứ cập nhật |
| --- | --- | --- |
| Q01 | 1 → 2 | C04a đối chiếu đúng nguồn trích DOCX, bổ sung CPU target >80%, dashboard, LLM và sản phẩm; ghi rõ chưa tự đọc DOCX. Nguồn thứ cấp được khai báo, không giả vờ đã vượt lỗi quyền. |
| Q02 | 1 → 2 | C02 phân biệt tham số duration, executor, REJECTED và tác động thật; PodKill không dùng duration. Nêu đúng khác biệt giữa comment và code của EffectiveDuration. |
| Q03 | 2 → 2 | Giữ kết quả trước; D8 không thay bằng kết luận runtime mới. |
| Q04 | 2 → 2 | Giữ khoảng trống ba vector; C03 bổ sung giới hạn cleanup pod stress. |
| Q05 | 1 → 2 | C01 rút suy luận Flannel, phân biệt cấu hình repo với controller/runtime; giữ vấn đề IP nguồn và hiệu lực chưa được kiểm chứng. |
| Q06 | 2 → 2 | Giữ phân biệt công cụ Claude Code và LLM trong hệ thống; không tự nhận backend đã chạy. |
| Q07 | 2 → 2 | C04c tách ngày CSV, commit nhập và chỉnh inventory; không coi timestamp CSV là log thực thi độc lập. |
| Q08 | 1 → 2 | C03 tách runner reset, endpoint reset, TTL timer và giới hạn của cleanup; ghi nhận đúng đính chính của Codex. |
| Q09 | 2 → 2 | Giữ thiết kế đối chứng và giới hạn claim từ lượt trước. |
| Q10 | 1 → 1 | Đã bỏ giao chồng thư mục, tách thiết kế và runtime. Bảng T3 vẫn dùng “file test mới tương ứng”/“script probe mới”, chưa là allowlist hoàn chỉnh để hai bên bắt đầu sửa mã. Đây là việc khóa khi giao task, không cần viết lại D8. |
| **Tổng** | **15 → 19/20** | **Đạt hydration; chuyển sang công việc có đầu ra cụ thể.** |

**Lưu ý cho task kế tiếp, không mở thêm vòng kiểm tra hydration:**

- T2 có thể nhận như task tài liệu hẹp: bản nháp `docs/design/r1-event-contract.md`, Codex review trước khi sửa producer/consumer. Phải tách trạng thái hành động khỏi trạng thái hồi phục; giữ PARTIAL, REJECTED, missing và timeout/censoring có nghĩa rõ, không biến một danh sách status đề xuất thành schema đã được khóa. Ngữ nghĩa metric và mốc attack_effect/detect/action/recovery cần khớp R1-T01-S01/R1-T02-S03/R3-T01-S01.
- T1 inventory chỉ đọc có thể tiến hành độc lập khi được giao. Không mặc định cần Hoàng gõ từng lệnh hoặc xin lại quyền đã có; nếu môi trường thực sự chặn thì báo thao tác/lỗi cụ thể. Hành động start/recreate/deploy và quyết định provider/chi phí được xét theo phạm vi giao việc riêng.
- Trước T3a/T3b, chốt đường dẫn chính xác cho test/probe/schema dùng chung, owner và base HEAD của từng task. Một checkout dùng chung thì chỉ một bên ghi tại một thời điểm; bảng file không chồng nhau chưa tự giải quyết rủi ro cùng đổi branch/index/Git. Nếu chọn chạy đồng thời, cần bố trí checkout/worktree riêng và điểm tích hợp rõ ràng trước.
- T4 có thể kiểm tra vòng rules khi backend LLM chưa sẵn sàng. Bằng chứng nhánh AI chờ backend thật, không vì vậy chặn mọi phép kiểm tra tích hợp.

Codex xác nhận D ban đầu vẫn khớp hash đã lưu và mã tracked hiện không đổi. Các lời kể “đã lưu rồi đọc lại”, “SHA trước/sau” và câu lệnh thật trong phiên Claude là tự báo cáo; không có log đầy đủ để xác nhận từng thao tác. Nội dung có thể đối chiếu đã được kiểm tra độc lập. Không cần giữ hydration mở chỉ vì thiếu transcript đó.

**Phạm vi lượt này:** chỉ cập nhật trạng thái và E6 trong file này, giữ nguyên D8. Chưa thực hiện T1–T4, chạy lab/test/build/LLM hoặc commit/push. Thứ tự tiếp theo đề xuất: inventory chỉ đọc và bản nháp contract, rồi chốt task triển khai theo kết quả; không giao toàn bộ agent/worker trong một lượt.
