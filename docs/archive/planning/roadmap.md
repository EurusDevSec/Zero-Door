# Kế hoạch hoàn thiện ZERO DOOR để nộp bài và nghiệm thu

> Cập nhật công cụ 18/10/2026: tên script `.ps1`, số dòng và hành vi được ghi dưới đây thuộc revision cũ, trước chuyển đổi Bash. Không quy các nhận xét đó cho script `.sh` mới. Vận hành hiện tại theo [Bash tooling](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md); mã cũ tra Git revision `1f43ff1461c2199bc99e9962483956c3df0fa975`.

Ngày lập: 09/10/2026. Mốc mục tiêu kỹ thuật: 31/10/2026. Hạn hoàn thành đề tài do người dùng xác nhận: 31/12/2026, bao gồm thời gian phản biện và chỉnh sửa bài. Đây là kế hoạch nghiên cứu và các gói sửa, chưa phải báo cáo triển khai hoàn tất hoặc cam kết bài được chấp nhận vào một ngày cụ thể.

Cập nhật ngày 09/10/2026: bổ sung câu hỏi nghiên cứu, đối chứng và giới hạn kết luận để đánh giá giá trị LLM/phối hợp tác tử; gắn vào task, subtask và gate hiện có. Các yêu cầu gốc và mốc mục tiêu được giữ nguyên.

Cập nhật tiếp ngày 09/10/2026 sau review bàn giao Antigravity: ánh xạ H01–H08 vào task và điều kiện kiểm chứng; làm rõ provenance dữ liệu cũ, terminal status, cách tiếp nhận lab và nguồn thời hạn. Giữ 8 phase, 27 task; hiện có 92 subtask, gồm một subtask bổ sung đối chiếu hồ sơ thời hạn trước nghiệm thu. Chưa triển khai mã hoặc chạy thực nghiệm mới.

**Cập nhật điều phối 17/10/2026:** tiếp nhận kết quả hydration Claude (D + D8: 19/20), đính chính kết luận NetworkPolicy/reset, bổ sung tiêu chí từ DOCX và lập lại lịch từ 17/10. Giữ 8 phase, 27 task, 92 subtask và toàn bộ cam kết gốc. Ngày gốc được giữ để truy vết; cột ngày điều chỉnh là lịch đang dùng. Chỉ R0-T01-S01 đã DONE về ghi nhận phạm vi; hydration đạt không đóng các task lab, mã hoặc thực nghiệm. Mục tiêu 31/10 vẫn được giữ nhưng đang có rủi ro cao, chưa có ước lượng công sức mới chứng minh khả thi.

Roadmap này là đầu mối điều phối; audit, handoff, thiết kế và evidence được liên kết từ đây. Mỗi việc triển khai phải gắn task/subtask của roadmap, owner, phạm vi file và điều kiện đóng; không tách thêm một roadmap cạnh tranh. Lượt cập nhật này chỉ sửa kế hoạch, chưa giao lệnh cho phiên Claude hoặc chạy task kỹ thuật.

Kết luận: giữ Python/Go và Google Online Boutique; sửa vòng lặp tự phục hồi cùng phép đo trước khi mở rộng triển khai. Đề xuất một API LLM làm backend chính cho thực nghiệm trên lab local; thiết kế giao diện thay được sang Ollama. Không đưa việc chạy đồng thời hai backend hoặc so sánh nhiều model vào đường bắt buộc của tháng 10.

## Phạm vi đã được người dùng chốt

- Bản thuyết minh đã cung cấp là bản đăng ký chính thức, không có bản điều chỉnh khác. Người dùng xác nhận thầy đã cho đổi sang Python/Go và Google Online Boutique được đề xuất từ ban đầu. Không yêu cầu quay lại Java/Spring AI chỉ để khớp tài liệu cũ; ghi rõ lựa chọn được xác nhận này trong báo cáo.
- **Nguồn thời hạn:** DOCX được cung cấp ghi thời gian từ tháng 01 đến tháng 06/2026, ngày trên văn bản 04/01/2026; hạn 31/12/2026 là xác nhận mới nhất của Hoàng với Codex. Giữ lịch tháng 12 để điều phối, đồng thời ghi khoảng trống nguồn giải thích khác biệt tại R0-T01-S03 và đối chiếu hồ sơ tại R7-T02-S05. Không coi ngày trên tài liệu là ngày ký/nộp/duyệt đã được chứng minh, cũng không tự kết luận có hay không có gia hạn.
- Vẫn phải hoàn thành SQL Injection, DDoS tầng ứng dụng, Resource Exhaustion; scale up/down, block IP và rollback; MTTD <60s, MTTR <2–3 phút, uptime ≥99,9% theo phạm vi thực nghiệm đã định nghĩa.
- **Xác nhận hiện hành 17/10:** Hoàng quyết định trước hết vẫn làm cả ba vector dù đã trao đổi việc thầy khuyên thu hẹp và chọn SQLi. Không dùng SQLi-only làm scope hiện tại, cũng không tự ghi thầy vừa phê duyệt lại cả ba. Phản hồi của thầy về block IP được phản ánh vào R3-T02: phải chặn được nguồn thay vì phát hiện/phục hồi lặp mãi.
- **Đối chiếu DOCX trực tiếp ngày 17/10:** ngoài KPI tổng, P179 có CPU của target app >80%, P187 có phản ứng <1 phút; P100 yêu cầu cô lập và hồi phục không cần can thiệp, P109 dashboard thời gian thực, P176 tích hợp LLM; sản phẩm gồm source/manifests, video, bảng đo, báo cáo, slide/poster. Các mốc phản ứng/phát hiện/hồi phục và mẫu số CPU phải được định nghĩa riêng tại R0-T01-S02/R1, không tự đồng nhất. Xem [bản trích có hash/vị trí đoạn](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md).
- Bài cần được chấp nhận đăng trong kỷ yếu trường trước nghiệm thu. Tên kỷ yếu, thông báo nhận bài, mẫu bài và lịch nhận bài chưa có; người dùng chọn chốt sau. Các mốc nộp bài dưới đây là mục tiêu nội bộ, không phải lịch do trường xác nhận.
- Người đang trao đổi là **Lê Văn Hoàng**, phụ trách kỹ thuật. **Nguyễn Ngọc Hòa** phụ trách báo cáo Word. Nội dung và kết luận khoa học cần hai người cùng đối chiếu với dữ liệu và giảng viên hướng dẫn.
- Hoàng trước đây nói khoảng 10 giờ/tuần, sau đó ngày 17/10 muốn tăng cường làm việc có kiểm soát cho ZERO DOOR và Zero-D-Rift. Chưa có quỹ giờ mới được xác nhận; không tiếp tục coi “30h còn lại trong tháng” của lịch 09/10 là nguồn lực hiện có. Lịch mới là mục tiêu theo phụ thuộc, không phải cam kết đủ người/giờ. Codex/Claude hỗ trợ thực hiện và review theo task; Hoàng giữ quyết định kỹ thuật, provider/chi phí và các thay đổi lab có hệ quả.
- Cloud cũ đã tắt. Hạ tầng cloud và dùng credit Azure cho compute được hoãn; lab chạy trên máy hiện tại. Có Azure for Students khoảng 100 USD theo người dùng, nhưng chưa kiểm tra số dư, quyền model, quota hoặc endpoint của subscription.

[Rà soát nguồn và dữ liệu](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-research-alignment-audit.md) là căn cứ cho các gói sửa. Những nhận xét trong bản rà soát về việc phải xác nhận đổi stack đã được giải quyết bằng thông tin trực tiếp của người dùng ở trên. Các phát hiện về SQLi, rollback, telemetry và dữ liệu chưa thay đổi.

## Tiếp nhận bàn giao Antigravity và thứ tự xử lý

[Bản bàn giao Gemini](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md) cung cấp bối cảnh kỹ thuật; [review H01–H08](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-antigravity-handoff-review.md) xác định phần đã đối chiếu và phần còn thiếu nguồn. Roadmap dùng xác nhận trực tiếp của Hoàng cho quyết định hiện tại, mã/dataset cho hành vi được kiểm tra, log thực thi cho runtime. Kế hoạch, checkpoint và hồi tưởng không thay những loại bằng chứng này.

### Tiếp nhận Claude và các đính chính ngày 17/10

[Hydration và review E6](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-handoff.md:345), [phản hồi D8](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-d8.md) và [blockers đã kiểm tra](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-session-blockers.md:93) kết thúc bước tiếp nhận: Claude đủ nắm bối cảnh để nhận task hẹp; không cần hydration lại. Điểm 19/20 không phải phần trăm hoàn thành dự án. Đây là rà soát trọng yếu dựa trên source/dữ liệu, chưa kiểm chứng mọi trao đổi cũ của Gemini hay toàn bộ hành vi runtime.

| Điểm mới/đính chính | Task áp dụng | Yêu cầu khi thực hiện |
| --- | --- | --- |
| C01 — K3s có controller NetworkPolicy nhúng; Flannel không tự suy ra bỏ policy | R0-T02-S01; R3-T02-S01/S02 | Kiểm phiên bản/args/controller, selector và đường IP thật; đo attacker bị chặn và benign vẫn hoạt động. Chưa có căn cứ thay CNI hoặc recreate cluster. Runtime enforce còn UNKNOWN. |
| C02 — duration trong command không bảo đảm thời gian hoặc tác động thực thi | R1-T04-S01; R2-T02; R2-T03 | Kiểm theo executor; POD_KILL không chạy suốt duration. Giới hạn của command phải bị chặn bởi trần vận hành; EffectiveDuration đang ưu tiên maxDuration của lệnh khi >0, cần test. GET healthz dùng kiểm sức khỏe; không POST attack làm health check. |
| C03 — runner reset, endpoint reset và TTL là ba đường khác nhau | R0-T02-S02; R2-T02-S03; R2-T03-S02; R3-T02-S02; R5 | Runner có lệnh xóa policy theo nhãn nhưng chưa kiểm return code; endpoint không xóa policy; TTL timer mất khi healer restart. Pod stress thử cleanup nhưng lỗi vẫn có thể báo SUCCESS. Xác nhận hậu điều kiện cleanup trước run tiếp. Codex rút lại nhận xét runner không có lệnh xóa policy. |
| C04 — provenance DOCX, graph và CSV phải tách đúng | R0-T01-S03; R5-T03-S02; R6 | Bản trích DOCX có hash/đoạn, không gán thành Claude trực tiếp đọc. CSV ghi ngày 25/06; Git nhập 25/06, thêm/xóa file thử 12–13/07. GitNexus query/context dùng được; status chậm không chứng minh graph hỏng. |
| C05 — owner/file và phụ thuộc của thiết kế khác runtime | R1-T01-S01; mọi task mã | Claude Code là cộng tác viên phát triển, không phải lựa chọn Claude API. Khóa schema trước sửa producer/consumer; bản nháp không chờ lab/LLM. Mỗi file có một owner trong lượt; chốt cả đường dẫn test/probe trước triển khai. |

**Snapshot điều phối 17/10:** `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`; trước cập nhật roadmap có bốn file handoff ngày 17/10 untracked, mã tracked không đổi. GitNexus index `6337b31` chậm một commit chỉ gồm docs/chỉ dẫn/cấu hình; dùng graph để định vị rồi đọc source hiện tại. Chưa lấy inventory Docker/K8s mới, chưa chạy lab, model hoặc thực nghiệm mới. Ghi chú Complete tháng 7 và snapshot 09/10 dưới đây là lịch sử, không thay trạng thái hiện tại.

**Bảo toàn tài liệu khi công cụ gián đoạn:** task nhỏ, lưu/đọc lại từng phần; không thay tiêu đề bảo vệ bằng một khối dài. Khi Claude bị classifier chặn, ghi thao tác và phần đã lưu, không retry liên tục hoặc sửa quyền rộng để bỏ qua. Dùng bản trích đúng phạm vi cho DOCX. GitNexus status chậm thì đọc MCP context hoặc meta/HEAD/diff và dirty files; không clean index/xóa lock của tiến trình khác. Các cách này giảm mất dữ liệu, không bảo đảm hết chặn từ nhà cung cấp.

### Các phát hiện H01–H08 và lịch điều chỉnh

| Phát hiện | Task tiếp nhận/xử lý | Due gốc 21:00 | Due điều chỉnh 21:00 (Asia/Saigon) | Điều kiện đóng liên quan |
| --- | --- | --- | --- | --- |
| H01 — Lý do và lời chấp thuận thiếu chat gốc | R0-T01-S03; R6-T01-S01 | 2026-10-10; 2026-10-14 | 2026-10-18; 2026-10-21 | Source ledger phân biệt chat gốc/nhớ lại/suy luận; không gán động cơ hoặc lời duyệt cho Hoàng từ code/commit. Thiếu chat được giữ UNKNOWN, không chặn sửa kỹ thuật. |
| H02 — Nguồn thời hạn khác nhau | R0-T01-S03; R7-T02-S05 | 2026-10-10; 2026-12-16 | 2026-10-18; 2026-12-16 | Ghi riêng tháng 01–06 trong DOCX và 31/12 do Hoàng xác nhận; hồ sơ cuối có kết quả đối chiếu và nguồn có thẩm quyền hoặc rủi ro đang chờ xác nhận. |
| H03 — Sai inventory/timeline dữ liệu | R0-T01-S03; R5-T03-S02 | 2026-10-10; 2026-10-31 | 2026-10-18; 2026-10-31 | Inventory đúng 8 CSV/40 dòng, 5 lượt/file; timestamp attack_start ghi 25/06/2026 tách khỏi ngày nhập Git/phân tích. Legacy không được trộn vào pilot/formal mới. |
| H04 — Mốc MTTR và terminal status không chứng minh recovery | R1-T01; R1-T02; R3-T01-S01 | 2026-10-13; 2026-10-15; 2026-10-17 | 2026-10-20; 2026-10-22; 2026-10-23 | Detect do detector ghi, recovery do probe xác nhận; FAILED/PARTIAL không tự tạo MTTR thành công; timeout/missing/failure có mẫu số và giới hạn quan sát rõ. |
| H05 — Runtime suy từ plan/ghi chú | R0-T01-S03; R0-T02-S03; R0-T03-S02 | 2026-10-10; 2026-10-12; 2026-10-11 | 2026-10-18; 2026-10-19; 2026-10-20 | Phân biệt báo cáo tự đánh giá với log thực thi; có evidence lab/model mới để đóng gate. Cloud tắt ghi theo Hoàng, không tự xác nhận thao tác/tài nguyên/ngày tắt cụ thể. |
| H06 — Sai hướng dẫn phục hồi cluster | R0-T02-S01; R0-T02-S02 | 2026-10-10; 2026-10-11 | 2026-10-18; 2026-10-19 | Inventory quyết định start hay recreate; lệnh/script dựng cluster được kiểm tra đúng chức năng. rebuild-nemesis.ps1 chỉ build/import/rollout Nemesis, không dùng thay bước tạo cluster. |
| H07 — Claim tài nguyên/ưu thế chưa có đối chứng | R0-T04-S01; R4-T04; R6-T01-S01; R6-T02-S04 | 2026-10-10; 2026-10-25; 2026-10-14; 2026-11-08 | 2026-10-18; 2026-10-29; 2026-10-21; 2026-11-08 | Giữ RAM <100MB, giảm 88%, tổng 157MB và nhận xét vượt AIOps ở mức claim cũ chưa xác minh; bỏ khỏi kết luận nếu không đo. Claim lợi ích chia vai trò cần B3; không mở benchmark RAM bắt buộc chỉ để giữ claim cũ. |
| H08 — Path, danh tính và nguồn chưa chuẩn hóa | R0-T01-S03; R5-T03-S03 | 2026-10-10; 2026-10-31 | 2026-10-18; 2026-10-31 | Dùng path thật, nguồn IDE có đường dẫn/loại nguồn; không suy hp8001 là Hòa. Thông tin nơi nhận bài vẫn chốt tại R6-T01-S03, không hỏi lại như blocker tiếp nhận. |

**Thứ tự bắt đầu:** chụp baseline/source ledger và preflight lab → khóa event/probe/phép đo → kiểm chứng vector và healer → tích hợp LLM → pilot đối chứng → formal dataset và paper. Chỉ các mô tả kỹ thuật đã đối chiếu được dùng làm đầu vào sửa; lịch sử chưa xác minh không quyết định thiết kế hoặc trách nhiệm cá nhân.

**Dataset cũ:** review ghi nhận 8 CSV với 40 dòng, trong đó E3 AUTO có 4/5 lượt FAILED nhưng vẫn mang MTTR khoảng 1,01–1,02s. Điều này minh họa lỗi phương pháp, chưa xác định nguyên nhân runtime của từng thất bại. Không diễn giải khoảng 1s là latency K8s API hoặc tốc độ hồi phục nghiệp vụ; 9,24s là P95 MTTD E3 AUTO trong summary, không phải max 11,26s trong raw. Giữ nguyên dữ liệu, hình và báo cáo cũ để truy vết; bản viết mới phải nêu giới hạn và dùng dataset mới hợp lệ.

## Snapshot kiểm tra ngày 09/10/2026 và giới hạn xác nhận

Mã ứng dụng tại HEAD `6337b319b075bf389d484a6be13a4bc094f94a82` chưa được sửa trong lượt này. Metadata GitNexus có cùng commit, 96 files, 1.409 nodes, 44 processes; dùng graph để xác định hàm LLM và đọc mã thật để xác nhận, không dùng graph làm bằng chứng vận hành.

- Máy: Intel i7-11800H, 8 cores/16 threads, RAM khoảng 15,8 GiB; GPU RTX 3050 Laptop, VRAM 4.096 MiB. Docker báo được cấp khoảng 6,77 GiB RAM, 4 CPU.
- Trong lần lập kế hoạch ban đầu, Docker daemon trả lời truy vấn thông tin; context Kubernetes là `k3d-zero-door`, API `127.0.0.1:58117` từ chối kết nối và truy vấn container tên `k3d-zero-door` không trả container. Lượt review handoff sau đó chưa lấy được snapshot lifecycle mới do truy vấn Docker lỗi quyền rồi treo và được ngắt. Các quan sát này không chứng minh container hiện exited hoặc cluster còn tồn tại; R0-T02-S01 phải lấy inventory mới. Chưa khởi động, tái tạo cluster hoặc xóa volume.
- Không thấy lệnh Ollama trên PATH; API localhost:11434 không trả lời. Chưa chứng minh có local inference server đang hoạt động ở endpoint khác.
- [Nemesis](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/nemesis/main.py:276) có mã gọi OpenAI-compatible API, Gemini và Ollama. [Manifest](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/nemesis-deployment.yaml:17) chọn Gemini, có cấu hình Ollama/OpenAI nhưng secret mẫu để trống. Không đọc được trạng thái Secret đang triển khai do cluster chưa kết nối; không thể kết luận từ manifest rằng trước đây chưa từng có API key.
- Chưa chạy một lượt gọi LLM, tải model, tạo tài nguyên Azure, chạy attack hoặc healing trong lượt này. Có mã tích hợp LLM không đồng nghĩa agent hiện hoạt động với LLM.

## Quyết định về AI và provider

Một agent cần quan sát, giữ trạng thái mục tiêu, chọn hành động, dùng công cụ và kiểm tra kết quả. Một endpoint gọi LLM rồi trả JSON chưa đủ chứng minh vòng lặp tự trị; giao diện chat diễn giải sự kiện cũng không tự trở thành ba agent AI.

| Tác tử | Hành vi cần hoàn thành | Vai trò LLM | Phần mã kiểm soát |
| --- | --- | --- | --- |
| Nemesis | Chọn kịch bản từ trạng thái lab, thực thi, đọc kết quả và quyết định lượt tiếp theo trong phiên giới hạn | Chọn vector/intensity, sinh biến thể SQLi theo mẫu sandbox và giải thích ngắn bằng dữ kiện | Target allowlist, payload schema, request/duration/concurrency budget, start/stop và worker thực thi |
| Gaia | Thu metrics/log/probe, phát hiện sự cố và phân tích nguyên nhân có bằng chứng | Phân loại sự cố, đối chiếu log/metrics gần nhất, trả anomaly/evidence/confidence có cấu trúc | Threshold/signature/probe phát hiện nhanh, timestamp, IP nguồn, dedup; không chờ LLM mới ghi mốc phát hiện |
| Hephaestus | Chọn hành động theo sự cố và trạng thái deploy, thực thi, kiểm tra hồi phục và ghi kết quả | Xếp hạng/chọn action trong enum được phép, dùng evidence và release history | Policy gate, invariants, cooldown, hạn số lần chữa, thao tác K8s/gateway, xác nhận readiness và giao dịch nghiệp vụ |

Ba tác tử có trạng thái, nhiệm vụ và hợp đồng dữ liệu riêng; có thể dùng chung một model/API. Không cần tải ba model cùng lúc. LLM không được sinh và thực thi lệnh shell tùy ý hoặc tự sửa mã ứng dụng trong luồng chữa lỗi.

Sự cố cần phản ứng nhanh được bộ phát hiện ghi nhận ngay. Inference có timeout và retry giới hạn. Khi LLM không khả dụng, chế độ suy giảm dùng policy đã khai báo; raw event và dataset phải đánh dấu đã fallback. Một lượt không gọi được model không được ghi như lượt AI đầy đủ. Đo riêng latency inference và overhead quyết định để kiểm tra ảnh hưởng lên KPI.

**Provider đề xuất:** API là backend chính cho thực nghiệm, nhằm tránh inference trên cùng máy làm nhiễu tài nguyên của cluster. Chọn model nhỏ có structured output sau khi xác nhận endpoint/quota và một lượt test thật. Không chốt tên model từ manifest cũ, không tự nâng subscription, không tự tạo VM/GPU hoặc dịch vụ mất phí trong lượt lập kế hoạch.

**Ollama bổ sung:** nếu API chưa sẵn sàng, thử duy nhất một ứng viên nhỏ, chẳng hạn [qwen2.5:3b Q4_K_M](https://ollama.com/library/qwen2.5:3b), trước khi triển khai nhiều lựa chọn. Trang model ghi khoảng 1,9 GB weights, không phải tổng RAM/VRAM vận hành. Đặt context nhỏ cho telemetry đã tóm tắt và đo thực tế cùng lab; chỉ dùng nếu latency và memory không làm hỏng phép đo. Ollama hỗ trợ [JSON schema/structured outputs](https://docs.ollama.com/capabilities/structured-outputs); [context dài làm tăng bộ nhớ](https://docs.ollama.com/context-length). Chưa có benchmark để hứa model này đáp ứng KPI hoặc chất lượng phân loại.

Chỉ cần interface thay provider, không bắt buộc vận hành hai backend trong tháng 10. Khi đo chính thức, khóa provider/model/version/prompt; không chuyển provider âm thầm giữa các lượt. Thực nghiệm cloud/local song song và so sánh model là phần hoãn nếu làm trễ nghiệm thu.

Microsoft xác nhận [Azure for Students có credit 100 USD trong 12 tháng nhưng không áp dụng cho Marketplace offers](https://learn.microsoft.com/en-us/azure/education-hub/faq). Quyền model/quota còn phụ thuộc subscription/deployment. Trước khi dùng API Azure, kiểm tra eligibility, billing và giới hạn cụ thể; không mặc định mọi model đều dùng được credit. Đề xuất giới hạn thử nghiệm LLM ban đầu 10 USD từ credit, chỉ khi được xác nhận phương án; code có max calls, token budget, timeout và tracking usage. Budget alert của cloud không thay cho giới hạn request trong ứng dụng; chưa phát sinh chi phí trong kế hoạch này.

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

Giả thuyết cần kiểm tra là LLM có thể hữu ích hơn ở trường hợp cần kết hợp nhiều bằng chứng, trong khi quy tắc có thể nhanh/rẻ hơn ở trường hợp đơn giản. Khóa câu hỏi, metric chính và cách chấm trước formal run; không chọn lại giả thuyết hoặc bỏ case thất bại sau khi thấy kết quả. Không bắt buộc AI thắng để đóng task thực nghiệm; bắt buộc kết luận khớp dữ liệu và nêu độ bất định.

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

## Các gói sửa và bằng chứng phải bàn giao

| Gói | Nội dung sửa | Bằng chứng hoàn thành | Người phụ trách |
| --- | --- | --- | --- |
| W0 Lab và cấu hình | Kiểm tra Docker/context/containers/volumes; khôi phục hoặc dựng lab sau khi xác định trạng thái; chọn một đường setup và profile tài nguyên; kiểm tra telemetry dependencies; làm một lượt LLM có schema | Inventory trước/sau; API K8s truy cập; ít nhất 5 dịch vụ phục vụ luồng nghiệp vụ; Kafka/Prom/log hoạt động; model health và response hợp lệ được lưu | Codex thực hiện, Claude review; Hoàng chốt thay đổi lab/provider/chi phí |
| W1 Event và phép đo | Hợp đồng run/command/alert/heal IDs; timestamp và interval nhất quán; event lưu bền; probe HTTP độc lập; bỏ KPI ngẫu nhiên/fallback; tách manual/rules/AI | Tái tính MTTD/MTTR từ raw events; FAILED/PARTIAL không tự thành recovery; mất telemetry là missing; MANUAL không được healer can thiệp; dashboard và analysis dùng chung dữ liệu | Claude contract/agent, Codex phép đo/dashboard; review chéo; Hoàng chốt ngữ nghĩa |
| W2 Tấn công trong scope | SQLi fixture, HTTP L7 cùng đường đo, resource stress tác động đúng target; kiểm tra payload và target; phiên tấn công tự động giới hạn có start/stop | Cả 3 vector có attack_effect evidence; SQLi phân biệt payload và request bình thường; resource cao/suy giảm nằm ở target thật; cleanup được kiểm chứng | Claude thực hiện, Codex review; Hoàng chốt protocol |
| W3 Chữa lỗi đúng nghĩa | Scale up/down có hysteresis, block nguồn thật tại điểm enforce, rollback về release tốt, không tranh chấp với controller/HPA; hậu điều kiện và timeout | Image/config trước/sau rollback; attacker bị chặn nhưng benign client còn hoạt động; replicas sẵn sàng; giao dịch đã phục hồi ổn định; không chữa lặp vô hạn | Claude thực hiện, Codex review; Hoàng đánh giá kết quả |
| W4 Ba agent và LLM | Adapter dùng chung, role schemas, bounded autonomous session; Gaia evidence analysis và Hephaestus lựa chọn tool; latency/usage/fallback audit | Trace cho mỗi agent: observed state → structured decision → action/result; policy chặn output sai; đối chứng cùng hệ thống khi tắt LLM | Codex adapter/Nemesis, Claude Gaia/Hephaestus; bàn giao file theo R4; Hoàng chốt backend |
| W5 Kiểm thử và đo lại | Tests hành vi và lỗi; integration toàn pipeline không inject alert trực tiếp; workload, baseline và thứ tự đo; pilot, formal repetitions và War Game | Raw dataset mới, configs/commit/model/prompt, full failure accounting, probe timeline, bảng KPI và uncertainty tái sinh được | Codex điều phối/chạy theo task; Claude review; Hoàng chủ trì protocol, Hòa đối chiếu |
| W6 Paper và hồ sơ | Sửa chương phương pháp/kết quả, chọn claim đủ bằng chứng, đối chiếu nguồn tham khảo, video/slide, paper và Word/PDF; phản hồi reviewer | Paper nhất quán với dataset và scope; bảng traceability đủ; video thực; minh chứng chấp nhận đăng trước nghiệm thu | Hòa viết Word; Hoàng viết nội dung kỹ thuật/kiểm tra số liệu |

### SQLi với Google Online Boutique

Không giả định Boutique hiện có SQL database hoặc endpoint dễ bị SQLi. Để giữ hệ thống mục tiêu được thầy chấp thuận, đề xuất bổ sung một dịch vụ tìm kiếm/catalog thử nghiệm với dữ liệu e-commerce giả lập, database nhẹ như SQLite và route qua ingress lab. Có bản dễ tổn thương phục vụ phép thử và bản dùng truy vấn tham số; tất cả giới hạn trong namespace nghiên cứu, không công khai ra Internet. Đây là phần bổ sung mô hình thực nghiệm, phải ghi rõ trong kiến trúc/paper, không mô tả như lỗ hổng sẵn có của Google Boutique.

Giữ Boutique và luồng mua hàng làm đối tượng availability; dùng fixture để kiểm chứng vector SQLi và containment. Nếu kết luận về availability áp dụng cho cả hai, định nghĩa hai luồng probe và báo kết quả riêng, không gộp để che luồng thất bại. Không cần viết lại toàn bộ ứng dụng thương mại điện tử hoặc thêm PostgreSQL để có phép thử SQLi.

### Mô hình chữa lỗi cần hợp lý với nguyên nhân

- CPU/resource quá tải: gây tải vào workload target thật; kiểm tra scale có giảm latency/error hoặc throttling. Pod stress riêng chỉ dùng nếu nghiên cứu đúng tranh chấp node và có bằng chứng tác động, không ánh xạ mức CPU của attacker thành CPU của app.
- SQLi: ghi nguồn từ kết nối/ingress tin cậy, không lấy một X-Forwarded-For bất kỳ do client khai. Chặn tại điểm nhìn thấy nguồn trước NAT hoặc gateway phù hợp. Không coi IP `0.0.0.0` và NetworkPolicy tạo được là bằng chứng containment.
- Bad release: fault phiên bản ứng dụng/config và rollback về release tốt đã biết. Error rate cao do flood không tự là bằng chứng bản deploy sai; không rollback mọi 5xx.
- Scale-down: chỉ sau cửa sổ tải thấp/khỏe đủ dài, giới hạn min/max và tránh HPA giành quyền replicas. Reset thí nghiệm tách khỏi logic hồi phục.
- Pod Kill: giữ như phép thử bổ sung để đánh giá controller mặc định và xem healer có can thiệp thừa; không dùng thay SQLi.

## Kế hoạch thực thi theo phase, task và subtask

**Phiên bản lịch đang dùng: 2026-10-17; lịch gốc: 2026-10-09.** Tất cả ngày dùng định dạng YYYY-MM-DD; due mặc định **21:00, Asia/Saigon (UTC+7)**. Cột gốc giữ lịch sử, cột điều chỉnh là mục tiêu hiện hành; không ghi ngày điều chỉnh thành ngày thực tế đã làm. Ngày bắt đầu là cửa sổ dự kiến, phụ thuộc thực tế quyết định có mở bước triển khai hay không. Các việc dùng chung một ngày phải bàn giao đầu vào trước khi việc sau bắt đầu; ngày trùng không phải bằng chứng đủ giờ để hoàn thành.

Mã **R0–R7** dành cho đợt hoàn thiện này, tách khỏi trạng thái Complete của các phase cũ. Đây là bảng theo dõi chuẩn duy nhất cho kế hoạch sửa; chưa có bằng chứng chạy mới thì không kế thừa trạng thái hoàn thành từ tài liệu cũ. Phạm vi đã được người dùng xác nhận là một subtask DONE về tài liệu; các việc triển khai và thực nghiệm còn lại chưa được xác nhận hoàn tất.

Ba mốc chính: **2026-10-31** đóng phiên bản kỹ thuật đã kiểm chứng và dataset pilot; **2026-11-14** mục tiêu nộp bản paper đầu; **2026-12-31** hạn hoàn thành/nghiệm thu theo thông tin người dùng. Mốc nộp bài, chấp nhận đăng và báo cáo hội đồng là mục tiêu điều phối nội bộ cho đến khi có lịch của trường. Không đồng nhất phiên bản chạy được, KPI đạt, bài đã nộp và bài được chấp nhận đăng.

### Tổng quan phase và gate

| Phase | Cửa sổ gốc | Cửa sổ điều chỉnh 17/10 | Mục tiêu và điều kiện qua gate | Trạng thái |
| --- | --- | --- | --- | --- |
| R0 — Khóa phạm vi, khôi phục lab và xác nhận LLM | 2026-10-09 → 2026-10-12 | 2026-10-17 → 2026-10-20 | **G0:** Lab có giao dịch kiểm chứng được, một backend LLM trả kết quả thật; phạm vi, RQ, đối chứng và ranh giới nhãn/evidence được khóa. | IN_PROGRESS về tài liệu; gate chưa đánh giá |
| R1 — Sửa phép đo, event contract và kiểm soát thử nghiệm | 2026-10-12 → 2026-10-16 | 2026-10-17 → 2026-10-23 | **G1:** Một sự cố có ID xuyên suốt, metric hồi phục/quyết định tái tính được; evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động. | TODO; draft contract có thể chuẩn bị ngay |
| R2 — Hoàn thiện ba vector Chaos theo đề tài | 2026-10-13 → 2026-10-19 | 2026-10-21 → 2026-10-25 | **G2:** SQLi, DDoS L7 và resource exhaustion gây được tác động đúng mục tiêu, có dấu vết và cleanup; chạy phối hợp vẫn giữ giới hạn. | TODO; gate chưa đánh giá |
| R3 — Sửa healer và xác minh hồi phục thật | 2026-10-16 → 2026-10-22 | 2026-10-23 → 2026-10-27 | **G3:** Scale up/down, block IP và rollback có tác động thật; phân biệt API chấp nhận với hồi phục; có kiểm tra restart, HPA và trạng thái thất bại. | TODO; gate chưa đánh giá |
| R4 — Đưa LLM vào ba agent và kiểm tra giá trị AI | 2026-10-20 → 2026-10-25 | 2026-10-26 → 2026-10-29 | **G4:** Ba agent có trace thật, guard/fallback hoạt động; pilot B0/B1/B2 hợp lệ và quyết định B3 có bằng chứng hoặc giới hạn claim; không yêu cầu AI thắng. | TODO; gate chưa đánh giá |
| R5 — Tích hợp, pilot và đóng phiên bản kỹ thuật tháng 10 | 2026-10-26 → 2026-10-31 | 2026-10-29 → 2026-10-31 | **G5:** Core/phép đo qua kiểm chứng; có dataset pilot/runbook và protocol đối chứng đã khóa. KPI chưa đạt phải giữ kết quả và mở task sửa; chưa coi nghiên cứu hoàn tất. | TODO; lịch nén, chưa có dự phòng đã chứng minh |
| R6 — Viết song song, thực nghiệm chính thức và nộp paper | 2026-10-10 → 2026-11-14 | 2026-10-18 → 2026-11-14 | **G6:** Có dataset đủ protocol, paper trả lời RQ và claim khớp đối chứng đã đo, cùng biên nhận nộp đúng nơi. Biên nhận chưa phải chấp nhận đăng. | TODO; viết có thể đi trước formal data |
| R7 — Phản biện, hoàn thiện hồ sơ và nghiệm thu | 2026-11-15 → 2026-12-31 | 2026-11-15 → 2026-12-31 | **G7:** Có bằng chứng chấp nhận đăng, đủ sản phẩm cam kết và hồ sơ/kết quả nghiệm thu theo lịch trường trước 31/12; các mốc bên ngoài cần xác nhận. | TODO; còn phụ thuộc lịch ngoài nhóm |

R6 bắt đầu sớm để Hòa chuẩn bị bài song song; thực nghiệm chính thức của R6 vẫn chờ G5. R2/R3 có thể xen kẽ khi lab, hợp đồng sự kiện và phép đo đã qua kiểm chứng. Phụ thuộc cụ thể nằm ở từng task dưới đây; kế hoạch song song không đồng nghĩa chạy đồng thời các tác động vượt budget máy.

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

### Hàng đợi bắt đầu sau cập nhật 17/10

Các hàng này là bước nhỏ của task đã có, không thêm task thứ 28 hoặc tính hydration thành subtask kỹ thuật DONE. Trong lượt hiện tại chỉ cập nhật roadmap; các bước dưới chưa được thực hiện.

| Bước | Owner / reviewer | Due điều chỉnh | Allowlist ghi khi bước được mở | Đầu ra và điều kiện đóng |
| --- | --- | --- | --- | --- |
| R0-T02-S01 — inventory chỉ đọc, READY | Codex / Claude | 2026-10-18 21:00 | `docs/evidence/R0-T02-S01/inventory.md` | Timestamp, Git/Docker/K8s context, containers/volumes/ports/resources, phiên bản/args K3s khi truy cập được; lệnh lỗi/timeout ghi đúng. Không start/recreate/delete, không đọc secret. Lỗi không biến thành kết luận không có cluster. |
| R0-T01-S03 — baseline/source ledger, READY | Codex / Claude; Hoàng đối chiếu nguồn | 2026-10-18 21:00 | `docs/evidence/R0-T01-S03/baseline-source-ledger.md` | HEAD/dirty, inventory/hash 8 CSV/40 dòng, nguồn DOCX/Gemini/hydration và các UNKNOWN; giữ dữ liệu gốc. Chỉ kết quả kiểm chứng mới được điền ngày hoàn thành. |
| R1-T01-S01 — chỉ bản nháp contract sẵn sàng soạn | Claude / Codex; Hoàng chốt ngữ nghĩa | Draft 2026-10-18 21:00; bản khóa 2026-10-19 21:00 | `docs/design/r1-event-contract.md` | ID, event/schema version, writer timestamp, action/recovery state tách riêng, PARTIAL/REJECTED/timeout/missing/censoring, công thức KPI và ví dụ failure. Có quyết định về nguồn lưu bền, probe độc lập, public API dashboard và ranh giới ground truth. Draft REVIEW chưa đóng subtask; bản khóa chờ đầu vào R0 theo task cha. |

Những đường dẫn trên là đầu ra dự kiến, chưa được tạo trong lượt sửa roadmap. Sau review contract mới khóa allowlist cho mã/test/probe của R1-T01-S02, R1-T02, R1-T03 và R1-T04; không tự dùng các mục “test tương ứng/script mới” trong D8 như quyền sửa file không giới hạn. Hòa có thể chuẩn bị outline/method theo R6-T01 sau khi RQ được chốt, không đợi có số liệu mới để bắt đầu và không viết kết quả khi chưa đo.

**Phản biện:** mục tiêu phản hồi trong **3 ngày làm việc kể từ khi nhận ý kiến**; ngày 28/11 và 05/12 dưới đây chỉ là cửa sổ dự phòng. Nếu phản biện tới muộn, cập nhật ngày thực tế và mốc liên quan. Không đánh dấu đã nhận ý kiến, đã sửa hoặc được chấp nhận đăng khi chưa có xác nhận.

### Danh sách task và subtask

### R0 — Khóa phạm vi, khôi phục lab và xác nhận LLM

**Cửa sổ gốc:** 2026-10-09 → 2026-10-12. **Cửa sổ điều chỉnh 17/10:** 2026-10-17 → 2026-10-20, due 21:00. **Gate G0:** Lab có giao dịch kiểm chứng được, một backend LLM trả kết quả thật; phạm vi, RQ, đối chứng và ranh giới nhãn/evidence được khóa.

#### R0-T01 — Khóa phạm vi và tiêu chí đánh giá

**Bắt đầu gốc:** 2026-10-09. **Due gốc:** 2026-10-10 21:00. **Phụ trách (17/10):** Codex lập ma trận/source ledger; Hoàng quyết định, Hòa đối chiếu. **Phụ thuộc:** Không có. **Trạng thái:** IN_PROGRESS. **Bắt đầu điều chỉnh:** 2026-10-17. **Due điều chỉnh:** 2026-10-18 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R0-T01-S01 | Ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI và bài được chấp nhận đăng. | 2026-10-09 | 2026-10-09 | 2026-10-09 | 2026-10-09 | DONE | Các xác nhận của người dùng đã được ghi trong phần Phạm vi của plan này. |
| R0-T01-S02 | Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số. | 2026-10-09 | 2026-10-10 | 2026-10-17 | 2026-10-18 | TODO | Ma trận truy vết; cách đánh giá MTTR 120/180 giây theo thuyết minh, MTTD <60 giây và uptime ≥99,9%, không hạ ngưỡng. |
| R0-T01-S03 | Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08. | 2026-10-10 | 2026-10-10 | 2026-10-17 | 2026-10-18 | READY | HEAD/dirty files, hash và số dòng từng CSV, timestamp lưu trong dữ liệu tách khỏi timeline Git; nguồn DOCX/xác nhận mới/IDE/chat được phân loại, path được kiểm tra. Giữ nguyên raw/handoff; thiếu lịch sử hoặc danh tính thì UNKNOWN. |

#### R0-T02 — Khôi phục môi trường local

**Bắt đầu gốc:** 2026-10-09. **Due gốc:** 2026-10-12 21:00. **Phụ trách (17/10):** Codex thực hiện; Claude review; Hoàng chốt nếu cần thay đổi hoặc xóa lab. **Phụ thuộc:** Không có. **Trạng thái:** READY. **Bắt đầu điều chỉnh:** 2026-10-17. **Due điều chỉnh:** 2026-10-19 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R0-T02-S01 | Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới. | 2026-10-09 | 2026-10-10 | 2026-10-17 | 2026-10-18 | READY | Inventory có timestamp/kết quả hoặc lỗi rõ, context/Git/containers/volumes/ports/resources và phiên bản/args K3s khi truy cập; xác định nguyên nhân API không truy cập được. Truy vấn lỗi/bị ngắt không được coi là inventory rỗng hoặc container exited. |
| R0-T02-S02 | Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại. | 2026-10-10 | 2026-10-11 | 2026-10-18 | 2026-10-19 | TODO | Kubernetes API truy cập; dữ liệu cần giữ được bảo toàn; lệnh dựng và profile tài nguyên được ghi. Kiểm tra script đúng chức năng; start-demo.ps1 hiện dừng mọi kubectl và dùng context hiện hành nên không chạy mù; rebuild-nemesis.ps1 build/import/rollout, không tạo cluster. Giữ volume/dữ liệu và ghi phạm vi thao tác. |
| R0-T02-S03 | Kiểm tra Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique. | 2026-10-11 | 2026-10-12 | 2026-10-19 | 2026-10-19 | TODO | Log/message truy vết, truy vấn metric và giao dịch mẫu; trạng thái Running riêng lẻ chưa đủ. |

#### R0-T03 — Xác nhận một backend LLM thật

**Bắt đầu gốc:** 2026-10-10. **Due gốc:** 2026-10-12 21:00. **Phụ trách (17/10):** Codex tích hợp/test; Hoàng chọn provider, credential và ngân sách; Claude review. **Phụ thuộc:** R0-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-18. **Due điều chỉnh:** 2026-10-20 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R0-T03-S01 | Chọn provider/model; xác minh quyền truy cập, quota, giới hạn token và chi phí mỗi lần chạy. | 2026-10-10 | 2026-10-10 | 2026-10-18 | 2026-10-19 | TODO | Quyết định provider có căn cứ và cấu hình giới hạn; không suy ra quyền API từ credit Azure. |
| R0-T03-S02 | Gọi LLM bằng đầu vào nghiên cứu và kiểm tra đầu ra theo schema. | 2026-10-10 | 2026-10-11 | 2026-10-19 | 2026-10-20 | TODO | Bằng chứng lượt gọi mới có timestamp/run_id, request ID khi backend hỗ trợ, tên/phiên bản model, latency/usage khả dụng và kết quả che bí mật; ghi trường không được provider trả. SDK/manifest/evaluation_report không thay log lượt gọi. |
| R0-T03-S03 | Thử timeout, retry có giới hạn và fallback; ghi rõ khi dùng RULES thay AI. | 2026-10-11 | 2026-10-12 | 2026-10-20 | 2026-10-20 | TODO | Log tình huống lỗi và kiểm chứng fallback không bị ghi nhãn là quyết định LLM. |

#### R0-T04 — Khóa câu hỏi nghiên cứu và thiết kế đối chứng

**Bắt đầu gốc:** 2026-10-10. **Due gốc:** 2026-10-12 21:00. **Phụ trách (17/10):** Codex chuẩn bị; Hoàng + Hòa khóa thiết kế nghiên cứu; Claude review kỹ thuật. **Phụ thuộc:** R0-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-18. **Due điều chỉnh:** 2026-10-19 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R0-T04-S01 | Chốt RQ1–RQ3, đóng góp dự kiến và giới hạn claim. | 2026-10-10 | 2026-10-10 | 2026-10-18 | 2026-10-18 | TODO | Bảng câu hỏi → metric → claim; tách đạt chức năng/KPI với chứng minh giá trị nghiên cứu. |
| R0-T04-S02 | Khóa B0/B1/B2, giữ BM; quyết định phạm vi B3 và budget. | 2026-10-10 | 2026-10-11 | 2026-10-18 | 2026-10-19 | TODO | Ma trận đối chứng và điều kiện B3; nếu bỏ B3 thì bỏ claim ưu thế nhiều tác tử, không bỏ cam kết gốc. |
| R0-T04-S03 | Chốt ground truth, tập action đúng và ranh giới dữ liệu không lộ đáp án. | 2026-10-11 | 2026-10-12 | 2026-10-19 | 2026-10-19 | TODO | Định nghĩa nhãn, mẫu số metric và schema evidence; bên chữa lỗi không nhận case/attack label hoặc đáp án. |

### R1 — Sửa phép đo, event contract và kiểm soát thử nghiệm

**Cửa sổ gốc:** 2026-10-12 → 2026-10-16. **Cửa sổ điều chỉnh 17/10:** 2026-10-17 → 2026-10-23, due 21:00. **Gate G1:** Một sự cố có ID xuyên suốt, metric hồi phục/quyết định tái tính được; evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động.

#### R1-T01 — Thống nhất hợp đồng sự kiện và lưu dấu vết

**Bắt đầu gốc:** 2026-10-12. **Due gốc:** 2026-10-13 21:00. **Phụ trách (17/10):** Claude soạn contract và sửa producer/consumer theo task được mở; Codex review, Hoàng chốt ngữ nghĩa. **Phụ thuộc:** R0-T01, R0-T04-S03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-17. **Due điều chỉnh:** 2026-10-20 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-T01-S01 | Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi. | 2026-10-12 | 2026-10-12 | 2026-10-17 | 2026-10-19 | TODO | Schema/version và ví dụ; mốc attack effect/detect/action/recovery/stop có nguồn ghi riêng. Terminal action SUCCESS/FAILED/PARTIAL được tách khỏi RECOVERY_VERIFIED. |
| R1-T01-S02 | Truyền ID qua Kafka/HTTP và lưu sự kiện gốc phục vụ tái tính. | 2026-10-12 | 2026-10-13 | 2026-10-19 | 2026-10-20 | TODO | Một chuỗi sự kiện xuyên thành phần; bản ghi bền vững có thể xuất và đối chiếu. |
| R1-T01-S03 | Tách ground truth/log điều khiển khỏi evidence dành cho bên chữa lỗi. | 2026-10-12 | 2026-10-13 | 2026-10-19 | 2026-10-20 | TODO | Phép thử kiểm tra prompt/query không lộ case label, attack command hoặc đáp án; ID trung tính vẫn truy vết được ở harness. |

#### R1-T02 — Đo sức khỏe và thời gian độc lập

**Bắt đầu gốc:** 2026-10-13. **Due gốc:** 2026-10-15 21:00. **Phụ trách (17/10):** Codex làm probe/runner/analysis; Claude review. **Phụ thuộc:** R1-T01, R0-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-20. **Due điều chỉnh:** 2026-10-22 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-T02-S01 | Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture. | 2026-10-13 | 2026-10-14 | 2026-10-20 | 2026-10-21 | TODO | Timestamp, chu kỳ probe, tiêu chí healthy và ví dụ lỗi được quan sát thật. |
| R1-T02-S02 | Tính MTTD/MTTR từ mốc sự kiện và xác nhận hồi phục bằng probe. | 2026-10-14 | 2026-10-15 | 2026-10-21 | 2026-10-22 | TODO | Tái tính incident từ raw: MTTD effect→detector detect, MTTR detect→recovery xác minh, total recovery effect→recovery. Không lấy heal history/replica tăng làm detect; ghi chu kỳ probe và độ phân giải thời gian. |
| R1-T02-S03 | Xử lý thiếu dữ liệu, timeout, FAILED/PARTIAL và FPR có mẫu số rõ ràng. | 2026-10-14 | 2026-10-15 | 2026-10-21 | 2026-10-22 | TODO | Phép thử có action thất bại nhưng chưa recovery, timeout và missing; chưa xác minh recovery thì MTTR chưa xác định/censored theo protocol, không điền 0 hoặc 1s. Giữ mọi run trong mẫu số, báo riêng phân phối lượt recovered và tỷ lệ failure; thiếu dữ liệu không thành uptime 100%. |
| R1-T02-S04 | Bổ sung metric quyết định, phục hồi theo lượt và usage/cost theo run. | 2026-10-14 | 2026-10-15 | 2026-10-21 | 2026-10-22 | TODO | Định nghĩa mẫu số; lưu đề xuất trước guard, action thực thi, false action, recovery/failure và số call/token kể cả retry. |

#### R1-T03 — Sửa dashboard và các chế độ đối chứng

**Bắt đầu gốc:** 2026-10-15. **Due gốc:** 2026-10-16 21:00. **Phụ trách (17/10):** Codex sửa dashboard/profile; Claude review API và cách tắt healer. **Phụ thuộc:** R1-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-22. **Due điều chỉnh:** 2026-10-23 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-T03-S01 | Bỏ số ngẫu nhiên và nội dung mô phỏng khỏi phần được trình bày là kết quả thực. | 2026-10-15 | 2026-10-15 | 2026-10-22 | 2026-10-22 | TODO | Dashboard hiển thị trạng thái không có dữ liệu và nguồn của số liệu. |
| R1-T03-S02 | Cho dashboard và bộ xuất dữ liệu dùng chung phép đo. | 2026-10-15 | 2026-10-16 | 2026-10-22 | 2026-10-23 | TODO | Cùng run_id cho ra cùng KPI; phản ánh lỗi và độ trễ cập nhật. |
| R1-T03-S03 | Tách MANUAL, RULES và AI; MANUAL không tự kích hoạt healer. | 2026-10-16 | 2026-10-16 | 2026-10-23 | 2026-10-23 | TODO | Log ba chế độ và phép thử chứng minh đối chứng manual không bị auto-heal. |
| R1-T03-S04 | Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi. | 2026-10-15 | 2026-10-16 | 2026-10-23 | 2026-10-23 | TODO | Cấu hình HPA/guard/probe được ghi rõ; chứng minh ZERO DOOR không phát lệnh heal trong B0, vẫn có đo độc lập. |

#### R1-T04 — Giới hạn tác động, kiểm soát lệnh và CI

**Bắt đầu gốc:** 2026-10-12. **Due gốc:** 2026-10-16 21:00. **Phụ trách (17/10):** Claude sửa guard/worker/CI; Codex review. **Phụ thuộc:** R0-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-18. **Due điều chỉnh:** 2026-10-21 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-T04-S01 | Chặn mục tiêu ngoài lab, redirect không hợp lệ và vượt giới hạn thời gian/tải. | 2026-10-12 | 2026-10-13 | 2026-10-18 | 2026-10-20 | TODO | Cấu hình allowlist cùng phép thử host, port, protocol, redirect và budget; trần thời lượng hiệu dụng không vượt trần vận hành dù maxDuration trong command lớn hơn. Phân biệt duration, executor và attack_effect. |
| R1-T04-S02 | Kiểm soát truy cập lệnh, sự kiện trùng và payload sai. | 2026-10-13 | 2026-10-15 | 2026-10-20 | 2026-10-21 | TODO | Phép thử lệnh bị từ chối, schema lỗi và duplicate; log lý do. |
| R1-T04-S03 | Khóa phiên bản và đưa kiểm tra hợp đồng, chế độ, guard quan trọng vào CI. | 2026-10-15 | 2026-10-16 | 2026-10-21 | 2026-10-21 | TODO | Phiên bản dependency/image và kết quả CI cho các hành vi cần bảo vệ. |

### R2 — Hoàn thiện ba vector Chaos theo đề tài

**Cửa sổ gốc:** 2026-10-13 → 2026-10-19. **Cửa sổ điều chỉnh 17/10:** 2026-10-21 → 2026-10-25, due 21:00. **Gate G2:** SQLi, DDoS L7 và resource exhaustion gây được tác động đúng mục tiêu, có dấu vết và cleanup; chạy phối hợp vẫn giữ giới hạn.

#### R2-T01 — Fixture và executor SQL injection

**Bắt đầu gốc:** 2026-10-13. **Due gốc:** 2026-10-17 21:00. **Phụ trách (17/10):** Claude triển khai fixture/executor theo thiết kế được chốt; Codex review. **Phụ thuộc:** R0-T02, R1-T01, R1-T04-S01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-21. **Due điều chỉnh:** 2026-10-24 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R2-T01-S01 | Chốt fixture nghiệp vụ giả lập, dữ liệu giả, route vulnerable/safe và nguồn IP. | 2026-10-13 | 2026-10-14 | 2026-10-21 | 2026-10-21 | TODO | Thiết kế fixture, tiêu chí tác động SQLi và cách liên hệ với luồng microservices. |
| R2-T01-S02 | Triển khai fixture/database nhẹ và đường ingress quan sát được. | 2026-10-14 | 2026-10-15 | 2026-10-21 | 2026-10-22 | TODO | Fixture hoạt động, route/query/log được kiểm chứng; phiên bản đóng gói. |
| R2-T01-S03 | Bổ sung executor SQLi bằng template và giới hạn đã chốt. | 2026-10-15 | 2026-10-16 | 2026-10-22 | 2026-10-23 | TODO | Payload hợp lệ chạy được; tham số ngoài phạm vi bị từ chối. |
| R2-T01-S04 | Chứng minh tác động SQLi, log và phân biệt lưu lượng tấn công với benign. | 2026-10-16 | 2026-10-17 | 2026-10-23 | 2026-10-24 | TODO | Kết quả trước/sau, truy vết request, IP đáng tin cậy và traffic đối chứng. |

#### R2-T02 — DDoS L7 và cạn tài nguyên đúng mục tiêu

**Bắt đầu gốc:** 2026-10-15. **Due gốc:** 2026-10-19 21:00. **Phụ trách (17/10):** Claude sửa executor/đường tác động; Codex review phép đo. **Phụ thuộc:** R0-T02, R1-T01, R1-T04-S01, R0-T04. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-21. **Due điều chỉnh:** 2026-10-25 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R2-T02-S01 | Cho HTTP flood đi qua route/cổng được giám sát, có RPS và thời lượng giới hạn. | 2026-10-15 | 2026-10-16 | 2026-10-21 | 2026-10-22 | TODO | Metric và log trên đúng đường giao dịch; tác động latency/error có thể tái hiện. |
| R2-T02-S02 | Tạo CPU exhaustion trên workload mục tiêu, giới hạn tài nguyên rõ ràng. | 2026-10-17 | 2026-10-18 | 2026-10-22 | 2026-10-23 | TODO | CPU/latency/error của chính dịch vụ bị tác động; KPI CPU target >80% (DOCX P179) có mẫu số, cửa sổ và attribution rõ; không suy từ pod stress riêng. |
| R2-T02-S03 | Kiểm tra cleanup, traffic bình thường và memory variant nếu đưa vào protocol. | 2026-10-18 | 2026-10-19 | 2026-10-23 | 2026-10-24 | TODO | Target trở lại baseline; cleanup có return code và kiểm tra tài nguyên còn sót, không giữ SUCCESS khi cleanup lỗi mà giấu lỗi. Memory variant có bằng chứng hoặc quyết định loại khỏi protocol. |
| R2-T02-S04 | Chuẩn bị tải C0/C1 cùng biến thể C2/C4 có triệu chứng chồng lấp. | 2026-10-18 | 2026-10-19 | 2026-10-24 | 2026-10-25 | TODO | Case catalog, ground truth/action set và seed/tải tái lập; tách biến thể pilot với đánh giá, không giả lập metric. |

#### R2-T03 — Chạy phối hợp và dừng có kiểm soát

**Bắt đầu gốc:** 2026-10-19. **Due gốc:** 2026-10-19 21:00. **Phụ trách (17/10):** Claude thực hiện; Codex review điều phối/cleanup. **Phụ thuộc:** R2-T01, R2-T02, R1-T04. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-25. **Due điều chỉnh:** 2026-10-25 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R2-T03-S01 | Điều phối ba executor đồng thời theo budget chung. | 2026-10-19 | 2026-10-19 | 2026-10-25 | 2026-10-25 | TODO | Ba vector có event riêng cùng run_id; không phát một loại COMBINED mà worker không hỗ trợ. |
| R2-T03-S02 | Thử start, stop, cancel và cleanup khi một executor lỗi. | 2026-10-19 | 2026-10-19 | 2026-10-25 | 2026-10-25 | TODO | Không còn tác động sau stop; trạng thái và tài nguyên được đối chiếu. |

### R3 — Sửa healer và xác minh hồi phục thật

**Cửa sổ gốc:** 2026-10-16 → 2026-10-22. **Cửa sổ điều chỉnh 17/10:** 2026-10-23 → 2026-10-27, due 21:00. **Gate G3:** Scale up/down, block IP và rollback có tác động thật; phân biệt API chấp nhận với hồi phục; có kiểm tra restart, HPA và trạng thái thất bại.

#### R3-T01 — Trạng thái hồi phục và scale

**Bắt đầu gốc:** 2026-10-16. **Due gốc:** 2026-10-19 21:00. **Phụ trách (17/10):** Claude sửa healer; Codex review hậu điều kiện/probe. **Phụ thuộc:** R1-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-23. **Due điều chỉnh:** 2026-10-24 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R3-T01-S01 | Tách API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED. | 2026-10-16 | 2026-10-17 | 2026-10-23 | 2026-10-23 | TODO | State machine/timeout và log đối chiếu probe; API nhận lệnh hoặc terminal FAILED/PARTIAL không đóng recovery. Phân biệt hồi phục nhờ controller/hết fault với bằng chứng tác động healer; restart phải xác minh pod thay thế và nghiệp vụ. |
| R3-T01-S02 | Kiểm chứng scale up tăng capacity và sức khỏe dịch vụ. | 2026-10-17 | 2026-10-18 | 2026-10-23 | 2026-10-24 | TODO | Replica ready, metric capacity và probe trước/sau. |
| R3-T01-S03 | Kiểm chứng scale down có hysteresis và quyền điều khiển rõ với HPA. | 2026-10-18 | 2026-10-19 | 2026-10-24 | 2026-10-24 | TODO | Không dao động; phục hồi replica baseline không bị tính thành heal nếu dịch vụ chưa khỏe. |

#### R3-T02 — Block IP thực thi được và rollback đúng phiên bản

**Bắt đầu gốc:** 2026-10-18. **Due gốc:** 2026-10-21 21:00. **Phụ trách (17/10):** Claude triển khai block/rollback; Codex review IP, release và traffic đối chứng. **Phụ thuộc:** R1-T02, R2-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-24. **Due điều chỉnh:** 2026-10-26 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R3-T02-S01 | Chốt enforcement point và nguồn IP; xử lý NAT/header tin cậy. | 2026-10-18 | 2026-10-18 | 2026-10-24 | 2026-10-24 | TODO | Sơ đồ request, selector/nhãn pod và thử xác nhận IP; không dùng IP mặc định 0.0.0.0. Đối chiếu controller K3s/args thực tế; không suy Flannel bỏ policy hoặc thay CNI khi chưa có bằng chứng. |
| R3-T02-S02 | Chặn attacker, giữ traffic benign, có TTL và gỡ chặn. | 2026-10-19 | 2026-10-20 | 2026-10-24 | 2026-10-25 | TODO | Request bị chặn/được phép đúng đối tượng; hiệu lực và hết hạn được kiểm tra sau restart. Không dựa duy nhất vào threading.Timer; tách endpoint reset (không xóa policy), runner reset (có lệnh xóa theo nhãn) và TTL; hậu điều kiện cleanup phải đo được. |
| R3-T02-S03 | Tạo phiên bản lỗi/known-good và case C3 có kiểm soát, tách nhãn đáp án khỏi telemetry. | 2026-10-19 | 2026-10-19 | 2026-10-25 | 2026-10-25 | TODO | Image/config/revision, triệu chứng và ground truth có danh tính rõ; bên chữa lỗi nhận lịch deploy/log thật, không nhận đáp án rollback. |
| R3-T02-S04 | Khôi phục image/config/revision thật và xác minh rollout lẫn probe. | 2026-10-20 | 2026-10-21 | 2026-10-25 | 2026-10-26 | TODO | Danh tính trước/sau và dịch vụ hồi phục; thay annotation riêng lẻ không đủ. |

#### R3-T03 — Consumer, retry và tương tác controller

**Bắt đầu gốc:** 2026-10-20. **Due gốc:** 2026-10-22 21:00. **Phụ trách (17/10):** Claude sửa consumer/state; Codex review failure/restart/HPA. **Phụ thuộc:** R1-T04, R3-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-24. **Due điều chỉnh:** 2026-10-27 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R3-T03-S01 | Sửa blocking consumer, ack, dedup, cooldown và retry có giới hạn. | 2026-10-20 | 2026-10-21 | 2026-10-24 | 2026-10-25 | TODO | Một action cho một event hiệu lực; lỗi không kẹt consumer hoặc lặp lệnh vô hạn. |
| R3-T03-S02 | Thử restart, nhiều replica, PodKill và tương tác HPA. | 2026-10-21 | 2026-10-22 | 2026-10-25 | 2026-10-26 | TODO | Log tác nhân gây hồi phục; phân biệt hiệu ứng Kubernetes/HPA với healer. |
| R3-T03-S03 | Thử worker/healer restart và mất telemetry. | 2026-10-22 | 2026-10-22 | 2026-10-26 | 2026-10-27 | TODO | Run dở có trạng thái rõ; dữ liệu thiếu không sinh kết luận thành công. |

### R4 — Đưa LLM vào ba agent và kiểm tra giá trị AI

**Cửa sổ gốc:** 2026-10-20 → 2026-10-25. **Cửa sổ điều chỉnh 17/10:** 2026-10-26 → 2026-10-29, due 21:00. **Gate G4:** Ba agent có trace thật, guard/fallback hoạt động; pilot B0/B1/B2 hợp lệ và quyết định B3 có bằng chứng hoặc giới hạn claim; không yêu cầu AI thắng.

#### R4-T01 — LLM adapter chung và Nemesis

**Bắt đầu gốc:** 2026-10-20. **Due gốc:** 2026-10-23 21:00. **Phụ trách (17/10):** Codex làm adapter/Nemesis; Claude review; bàn giao file sau R2. **Phụ thuộc:** R0-T03, R2-T01, R2-T03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-26. **Due điều chỉnh:** 2026-10-28 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R4-T01-S01 | Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout. | 2026-10-20 | 2026-10-21 | 2026-10-26 | 2026-10-26 | TODO | Interface và trace thật; quota/cost được cộng theo run. |
| R4-T01-S02 | Nối observation → kế hoạch Nemesis → executor → kết quả. | 2026-10-21 | 2026-10-22 | 2026-10-26 | 2026-10-27 | TODO | LLM chọn kế hoạch trong registry hợp lệ; kế hoạch được kiểm tra trước khi thực thi. |
| R4-T01-S03 | Thêm start/stop, max rounds/calls và điều kiện dừng. | 2026-10-22 | 2026-10-23 | 2026-10-27 | 2026-10-28 | TODO | Một phiên tự kết thúc trong budget; log stop/cancel và số gọi model. |

#### R4-T02 — Gaia và Hephaestus có quyết định LLM được giới hạn

**Bắt đầu gốc:** 2026-10-22. **Due gốc:** 2026-10-25 21:00. **Phụ trách (17/10):** Claude nối Gaia/Hephaestus với adapter; Codex review. **Phụ thuộc:** R4-T01-S01, R3-T02, R3-T03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-27. **Due điều chỉnh:** 2026-10-29 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R4-T02-S01 | Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM. | 2026-10-22 | 2026-10-23 | 2026-10-27 | 2026-10-28 | TODO | Incident có metric/log đầu vào, diagnosis và latency; MTTD không bị định nghĩa lại. |
| R4-T02-S02 | Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục. | 2026-10-23 | 2026-10-24 | 2026-10-28 | 2026-10-28 | TODO | Trace đề xuất, action, lý do chấp nhận/từ chối, decision latency và probe kết quả; không chữa thừa ở case lành tính. |
| R4-T02-S03 | Thử JSON sai, timeout, 429 và thiếu bằng chứng; fallback được đánh dấu. | 2026-10-24 | 2026-10-25 | 2026-10-28 | 2026-10-29 | TODO | Các trường hợp lỗi không tạo action ngoài allowlist và không bị ghi nhãn AI thành công. |

#### R4-T03 — Chứng minh vòng multi-agent và đối chứng RULES

**Bắt đầu gốc:** 2026-10-25. **Due gốc:** 2026-10-25 21:00. **Phụ trách (17/10):** Codex chạy/đối chiếu pilot; Claude review trace. **Phụ thuộc:** R4-T01, R4-T02, R3-T03, R0-T04. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-29. **Due điều chỉnh:** 2026-10-29 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R4-T03-S01 | Chạy một vòng có trace observation–decision–result cho cả ba agent. | 2026-10-25 | 2026-10-25 | 2026-10-29 | 2026-10-29 | TODO | Trace có ID liên kết và backend/model thật; phân biệt rõ quyết định rule và LLM. |
| R4-T03-S02 | Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage. | 2026-10-25 | 2026-10-25 | 2026-10-29 | 2026-10-29 | TODO | Bảng đối chứng controller/rules/multi-LLM; cùng evidence cho B1/B2, guard/probe/profile HPA cố định; không mặc định AI tốt hơn. |

#### R4-T04 — Đối chứng single-agent cho claim chia vai trò

**Bắt đầu gốc:** 2026-10-23. **Due gốc:** 2026-10-25 21:00. **Phụ trách (17/10):** Codex chuẩn bị đối chứng; Hoàng + Hòa quyết định claim; Claude review. **Phụ thuộc:** R0-T04, R4-T01-S01, R3-T03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-27. **Due điều chỉnh:** 2026-10-29 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R4-T04-S01 | Xác nhận giữ RQ2 hay giới hạn claim theo budget pilot. | 2026-10-23 | 2026-10-23 | 2026-10-27 | 2026-10-27 | TODO | Quyết định ghi rõ thời lượng/call budget; không đủ nguồn lực thì bỏ claim ưu thế chia vai trò. |
| R4-T04-S02 | Nếu giữ RQ2, cấu hình SINGLE_LLM gộp phân tích và chọn action. | 2026-10-23 | 2026-10-24 | 2026-10-27 | 2026-10-28 | TODO | Cùng model/evidence/tools/guard với B2; harness tấn công giống nhau. Không giữ claim thì đóng bằng quyết định loại claim. |
| R4-T04-S03 | Nếu giữ RQ2, pilot B2/B3 sau khi R4-T02-S02 hoàn tất, trên cùng case và kiểm tra dữ liệu. | 2026-10-24 | 2026-10-25 | 2026-10-28 | 2026-10-29 | TODO | Trace/cost/action/recovery đối chiếu; nếu B3 chưa chạy thì chưa đủ bằng chứng claim RQ2. Nếu loại claim, ghi rõ phạm vi còn lại. |

### R5 — Tích hợp, pilot và đóng phiên bản kỹ thuật tháng 10

**Cửa sổ gốc:** 2026-10-26 → 2026-10-31. **Cửa sổ điều chỉnh 17/10:** 2026-10-29 → 2026-10-31, due 21:00. **Gate G5:** Core/phép đo qua kiểm chứng; có dataset pilot/runbook và protocol đối chứng đã khóa. KPI chưa đạt phải giữ kết quả và mở task sửa; chưa coi nghiên cứu hoàn tất.

#### R5-T01 — Chạy đầy đủ đường tấn công–phát hiện–hồi phục

**Bắt đầu gốc:** 2026-10-26. **Due gốc:** 2026-10-28 21:00. **Phụ trách (17/10):** Codex điều phối tích hợp; Claude review và sửa theo task con; Hoàng kiểm chứng. **Phụ thuộc:** R4-T03, R4-T04. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-29. **Due điều chỉnh:** 2026-10-30 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R5-T01-S01 | Chụp phiên bản image/config/model/prompt và workload của đợt tích hợp. | 2026-10-26 | 2026-10-26 | 2026-10-29 | 2026-10-29 | TODO | Manifest/version/run metadata đủ dựng lại. |
| R5-T01-S02 | Chạy từng vector qua toàn pipeline và đo bằng probe độc lập. | 2026-10-26 | 2026-10-27 | 2026-10-29 | 2026-10-30 | TODO | Ba incident có trace đầy đủ; không dùng /heal/trigger làm đường đo chính. |
| R5-T01-S03 | Thử bad release, benign traffic, thất bại và cleanup. | 2026-10-27 | 2026-10-28 | 2026-10-30 | 2026-10-30 | TODO | Mỗi tình huống có verdict và log; failure được giữ trong dữ liệu. |

#### R5-T02 — Pilot, khóa protocol và War Game

**Bắt đầu gốc:** 2026-10-28. **Due gốc:** 2026-10-30 21:00. **Phụ trách (17/10):** Codex chạy/đóng gói phép đo; Hoàng khóa protocol và giám sát; Claude review. **Phụ thuộc:** R5-T01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-30. **Due điều chỉnh:** 2026-10-31 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R5-T02-S01 | Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo. | 2026-10-28 | 2026-10-28 | 2026-10-30 | 2026-10-30 | TODO | Dữ liệu pilot nguyên bản cho B0/B1/B2 và B3 nếu giữ RQ2; căn cứ chọn số lặp và đánh giá lại thời lượng trong trần nguồn lực. |
| R5-T02-S02 | Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI. | 2026-10-29 | 2026-10-29 | 2026-10-30 | 2026-10-30 | TODO | Protocol cố định trước formal run; B0/B1/B2/BM, quyết định B3/claim RQ2, profile HPA, biến thể đánh giá và ranh giới không lộ đáp án. |
| R5-T02-S03 | Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt. | 2026-10-29 | 2026-10-30 | 2026-10-31 | 2026-10-31 | TODO | Timeline/probe raw, giới hạn tác động và bố trí giám sát; ghi rõ nếu run bị dừng. |
| R5-T02-S04 | Tái tính KPI; phân loại pass/fail, thiếu dữ liệu và nguyên nhân. | 2026-10-30 | 2026-10-30 | 2026-10-31 | 2026-10-31 | TODO | Bảng kết quả tái tính; không lọc failure hoặc sửa số để đạt ngưỡng. |

#### R5-T03 — Chốt kỹ thuật và bàn giao cho Hòa

**Bắt đầu gốc:** 2026-10-30. **Due gốc:** 2026-10-31 21:00. **Phụ trách (17/10):** Owner file sửa lỗi theo task con; Codex tổng hợp; Hoàng + Hòa nhận bàn giao. **Phụ thuộc:** R5-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-31. **Due điều chỉnh:** 2026-10-31 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R5-T03-S01 | Sửa lỗi cốt lõi phát hiện trong pilot và chạy lại phép thử bị ảnh hưởng. | 2026-10-30 | 2026-10-31 | 2026-10-31 | 2026-10-31 | TODO | Danh sách lỗi, bản sửa và kết quả kiểm chứng; nếu chưa qua, gate G5 chưa đóng. |
| R5-T03-S02 | Lưu snapshot, runbook và dataset mới, bảo toàn dữ liệu cũ. | 2026-10-30 | 2026-10-31 | 2026-10-31 | 2026-10-31 | TODO | Phiên bản dựng lại được; dataset manifest có method version/hash/run IDs, legacy/pilot/formal tách riêng; analysis đọc danh sách dữ liệu đã khóa thay vì gộp mọi CSV. Run lỗi/loại khỏi phân tích có lý do theo protocol, vẫn được lưu và thống kê. |
| R5-T03-S03 | Bàn giao sơ đồ, protocol, câu hỏi/claim, bảng/plot và giới hạn kết quả cho Hòa. | 2026-10-31 | 2026-10-31 | 2026-10-31 | 2026-10-31 | TODO | Ma trận RQ → cấu hình → metric → claim khớp log/code; source ledger/path tra được, phân biệt lịch sử với bằng chứng mới. Giữ vấn đề/KPI chưa đạt và ghi kết quả xử lý H01–H08 còn mở. |

### R6 — Viết song song, thực nghiệm chính thức và nộp paper

**Cửa sổ gốc:** 2026-10-10 → 2026-11-14. **Cửa sổ điều chỉnh 17/10:** 2026-10-18 → 2026-11-14, due 21:00. **Gate G6:** Có dataset đủ protocol, paper trả lời RQ và claim khớp đối chứng đã đo, cùng biên nhận nộp đúng nơi. Biên nhận chưa phải chấp nhận đăng.

#### R6-T01 — Chuẩn bị bài báo trong lúc hoàn thiện kỹ thuật

**Bắt đầu gốc:** 2026-10-10. **Due gốc:** 2026-10-25 21:00. **Phụ trách (17/10):** Hòa chủ trì; Hoàng duyệt kỹ thuật; Codex hỗ trợ source/đối chiếu. **Phụ thuộc:** R0-T01-S01, R0-T04-S01. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-10-18. **Due điều chỉnh:** 2026-10-29 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R6-T01-S01 | Lập introduction/method quanh RQ1–RQ3 và bỏ khẳng định kết quả cũ chưa kiểm chứng. | 2026-10-10 | 2026-10-14 | 2026-10-18 | 2026-10-21 | TODO | Outline tách tuân thủ thuyết minh với giá trị LLM/phối hợp; RQ2 có điều kiện B3. Bỏ claim RAM/ưu thế chưa đo và động cơ/lời chấp thuận thiếu nguồn; không biến plan/ghi chú thành runtime hoặc kết quả. |
| R6-T01-S02 | Đối chiếu tài liệu gốc, gồm AIOpsLab/ITBench; chốt đóng góp và giới hạn tính mới. | 2026-10-14 | 2026-10-17 | 2026-10-19 | 2026-10-24 | TODO | Ma trận công trình → phương pháp → đối chứng → giới hạn → khác biệt; đọc nguồn liên quan đủ sâu, không lấy ghép công nghệ làm điểm mới. |
| R6-T01-S03 | Chốt kỷ yếu/đợt nhận bài, template, hạn và điều kiện chấp nhận đăng với thầy. | 2026-10-18 | 2026-10-24 | 2026-10-18 | 2026-10-24 | TODO | Thông báo/đầu mối nhận bài xác định; đây là hạn nội bộ, không tự đặt lịch của trường. |
| R6-T01-S04 | Hoàn thiện sơ đồ và mô tả phương pháp theo triển khai thực tế. | 2026-10-24 | 2026-10-25 | 2026-10-28 | 2026-10-29 | TODO | Method/architecture khớp phiên bản đang triển khai; kết quả chưa có được để trống có chú thích. |

#### R6-T02 — Thực nghiệm chính thức và khóa dữ liệu

**Bắt đầu gốc:** 2026-11-01. **Due gốc:** 2026-11-08 21:00. **Phụ trách (17/10):** Hoàng chủ trì thực nghiệm; Codex hỗ trợ chạy/phân tích; Claude review; Hòa tổng hợp. **Phụ thuộc:** R5-T03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-11-01. **Due điều chỉnh:** 2026-11-08 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R6-T02-S01 | Kiểm tra gate, protocol, nhãn không lộ đáp án và các lỗi/KPI chưa đạt trước formal run. | 2026-11-01 | 2026-11-01 | 2026-11-01 | 2026-11-01 | TODO | G5 PASS, protocol khóa theo R5-T02-S02 (mục tiêu điều chỉnh 30/10) và checklist đo hợp lệ; thiếu core/phép đo/đối chứng cần thiết thì BLOCKED, sửa và cập nhật lịch. |
| R6-T02-S02 | Chạy đủ số lặp B0/B1/B2/BM và B3 nếu giữ claim RQ2, kể cả manual có thao tác thật. | 2026-11-01 | 2026-11-06 | 2026-11-01 | 2026-11-06 | TODO | Raw run/failure, seed/fault/tải tương ứng và thứ tự xen kẽ; reset có xác nhận, cùng version/evidence/budget, không chỉnh rules/prompt theo case formal. |
| R6-T02-S03 | Phân tích tỷ lệ phục hồi, action đúng/sai/thừa, KPI, độ bất định và overhead/cost theo RQ. | 2026-11-06 | 2026-11-07 | 2026-11-06 | 2026-11-07 | TODO | Bảng/plot cùng mẫu số; báo AI thực/fallback, failure/timeout, độ đúng trước guard; B2/B3 chỉ kết luận nếu đã đo, không chọn riêng case AI thắng. |
| R6-T02-S04 | Khóa dataset và đối chiếu từng claim với RQ, nhóm đo và phạm vi kết luận. | 2026-11-07 | 2026-11-08 | 2026-11-07 | 2026-11-08 | TODO | Hash/version và ma trận claim → RQ/cấu hình/metric/trace; bỏ claim ưu thế phối hợp nếu thiếu B3, phân tích trung thực khi AI không tốt hơn rules. |

#### R6-T03 — Hoàn thiện và nộp bản paper đầu

**Bắt đầu gốc:** 2026-11-09. **Due gốc:** 2026-11-14 21:00. **Phụ trách (17/10):** Hòa chủ trì; Hoàng kiểm chứng và duyệt bản nộp; Codex/Claude review theo phạm vi. **Phụ thuộc:** R6-T01, R6-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-11-09. **Due điều chỉnh:** 2026-11-14 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R6-T03-S01 | Viết results/discussion/limitations trả lời RQ từ dữ liệu đã khóa. | 2026-11-09 | 2026-11-10 | 2026-11-09 | 2026-11-10 | TODO | Paper chỉ kết luận phần đã đo; báo lợi ích và đánh đổi, trường hợp rules tốt hơn, giới hạn mẫu/lab/fixture/model và mức độ mới đã đối chiếu. |
| R6-T03-S02 | Hai người rà số liệu, đối chứng, claim tính mới/giá trị AI và xin góp ý thầy. | 2026-11-11 | 2026-11-12 | 2026-11-11 | 2026-11-12 | TODO | Checklist claim–evidence, fairness/answer leakage và nguồn gốc tài liệu; xử lý góp ý hoặc ghi rõ còn chờ. |
| R6-T03-S03 | Soát template, hình/bảng, trích dẫn và hồ sơ nộp. | 2026-11-12 | 2026-11-13 | 2026-11-12 | 2026-11-13 | TODO | Bản nộp đáp ứng hướng dẫn của nơi nhận bài đã xác định. |
| R6-T03-S04 | Nộp khi có đợt nhận bài hợp lệ và lưu biên nhận. | 2026-11-14 | 2026-11-14 | 2026-11-14 | 2026-11-14 | TODO | Biên nhận/mã bài và bản đã nộp. 14/11 là mục tiêu nội bộ; nếu call không phù hợp phải cập nhật lịch. |

### R7 — Phản biện, hoàn thiện hồ sơ và nghiệm thu

**Cửa sổ gốc:** 2026-11-15 → 2026-12-31. **Cửa sổ điều chỉnh 17/10:** 2026-11-15 → 2026-12-31, due 21:00. **Gate G7:** Có bằng chứng chấp nhận đăng, đủ sản phẩm cam kết và hồ sơ/kết quả nghiệm thu theo lịch trường trước 31/12; các mốc bên ngoài cần xác nhận.

#### R7-T01 — Theo dõi bài và xử lý phản biện

**Bắt đầu gốc:** 2026-11-15. **Due gốc:** 2026-12-10 21:00. **Phụ trách (17/10):** Hòa theo dõi; Hoàng sửa kỹ thuật/đo bổ sung; Codex/Claude hỗ trợ theo task. **Phụ thuộc:** R6-T03. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-11-15. **Due điều chỉnh:** 2026-12-10 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R7-T01-S01 | Theo dõi tình trạng bài, lập bảng phản biện → việc sửa → bằng chứng. | 2026-11-15 | 2026-11-21 | 2026-11-15 | 2026-11-21 | TODO | Trạng thái bài và response matrix; tiếp tục rà ngày 28/11 và 05/12 khi đang chờ. |
| R7-T01-S02 | Xử lý vòng phản biện đầu nếu đã nhận; phản hồi trong 3 ngày làm việc. | 2026-11-22 | 2026-11-28 | 2026-11-22 | 2026-11-28 | TODO | Bản sửa/response có đối chiếu; chờ ý kiến thì WAIT_EXTERNAL. Ngày thực tế được tính lại theo ngày nhận. |
| R7-T01-S03 | Xử lý vòng tiếp theo nếu có, bổ sung phép đo khi reviewer yêu cầu. | 2026-11-29 | 2026-12-05 | 2026-11-29 | 2026-12-05 | TODO | Response và dữ liệu bổ sung; nếu đã chấp nhận không yêu cầu vòng này thì dùng xác nhận đó để đóng. |
| R7-T01-S04 | Đạt mốc mục tiêu có xác nhận chấp nhận đăng. | 2026-12-06 | 2026-12-10 | 2026-12-06 | 2026-12-10 | TODO | Thông báo/văn bản chấp nhận đăng lưu được; mốc 10/12 phụ thuộc đơn vị xét bài, không phải cam kết. |

#### R7-T02 — Hoàn thiện Word và các sản phẩm nghiệm thu

**Bắt đầu gốc:** 2026-11-15. **Due gốc:** 2026-12-18 21:00. **Phụ trách (17/10):** Hòa chủ trì Word; Hoàng phụ trách demo/source/data; Codex/Claude review bằng chứng. **Phụ thuộc:** R5-T03, R6-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-11-15. **Due điều chỉnh:** 2026-12-18 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R7-T02-S01 | Viết báo cáo Word bằng phương pháp và dữ liệu mới đã kiểm chứng. | 2026-11-15 | 2026-12-10 | 2026-11-15 | 2026-12-10 | TODO | Báo cáo Word có yêu cầu → sản phẩm → kết quả, bảng/plot và giới hạn. |
| R7-T02-S02 | Chuẩn bị video demo, slide/poster theo danh mục sản phẩm phải nộp. | 2026-11-22 | 2026-12-12 | 2026-11-22 | 2026-12-12 | TODO | Demo trên phiên bản chốt; slide/poster khớp báo cáo và dữ liệu, không dùng số mô phỏng. |
| R7-T02-S03 | Đóng gói source, manifest, runbook, dataset và Word/PDF. | 2026-12-13 | 2026-12-16 | 2026-12-13 | 2026-12-16 | TODO | Danh mục bàn giao có version và hướng dẫn tái lập. |
| R7-T02-S04 | Đối chiếu chéo số liệu và sản phẩm giữa paper, Word, demo và dữ liệu. | 2026-12-17 | 2026-12-18 | 2026-12-17 | 2026-12-18 | TODO | Hai người ký nhận checklist nội bộ; mọi sai khác được xử lý hoặc nêu rõ. |
| R7-T02-S05 | Đối chiếu thời hạn hồ sơ với nguồn của trường/thầy trước khi nộp nghiệm thu. | 2026-11-15 | 2026-12-16 | 2026-11-15 | 2026-12-16 | TODO | Ghi riêng thời gian DOCX tháng 01–06 và hạn 31/12 Hoàng xác nhận; lưu hồ sơ/xác nhận có thẩm quyền khi có và điều kiện nghiệm thu liên quan. Thiếu nguồn thì ghi WAIT_EXTERNAL, owner và ảnh hưởng G7; không tự viết rằng đã có gia hạn. Việc này không chặn sửa kỹ thuật. |

#### R7-T03 — Nộp hồ sơ và thực hiện nghiệm thu

**Bắt đầu gốc:** 2026-12-19. **Due gốc:** 2026-12-31 21:00. **Phụ trách (17/10):** Hoàng + Hòa; lịch hội đồng do trường xác nhận. **Phụ thuộc:** R7-T01, R7-T02. **Trạng thái:** TODO. **Bắt đầu điều chỉnh:** 2026-12-19. **Due điều chỉnh:** 2026-12-31 21:00.

| ID | Subtask | Bắt đầu gốc | Due gốc 21:00 | Bắt đầu điều chỉnh | Due điều chỉnh 21:00 | Trạng thái | Bằng chứng để đóng / link và ngày thực tế khi hoàn tất |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R7-T03-S01 | Chạy thử demo và tập báo cáo nghiệm thu. | 2026-12-19 | 2026-12-20 | 2026-12-19 | 2026-12-20 | TODO | Buổi rehearsal, checklist lỗi và phương án phục hồi demo. |
| R7-T03-S02 | Xác minh bằng chứng chấp nhận đăng rồi nộp bộ hồ sơ nghiệm thu. | 2026-12-21 | 2026-12-21 | 2026-12-21 | 2026-12-21 | TODO | Biên nhận hồ sơ và bằng chứng chấp nhận đăng; nếu thiếu thì BLOCKED, không ghi đã đủ điều kiện. |
| R7-T03-S03 | Báo cáo hội đồng và xử lý yêu cầu chỉnh sửa theo lịch được xác nhận. | 2026-12-22 | 2026-12-30 | 2026-12-22 | 2026-12-30 | TODO | Lịch/biên bản thực tế và các chỉnh sửa; khoảng này chỉ là dự phòng điều phối nội bộ. |
| R7-T03-S04 | Đối chiếu kết quả nghiệm thu, sản phẩm còn thiếu và lưu hồ sơ cuối. | 2026-12-30 | 2026-12-31 | 2026-12-30 | 2026-12-31 | TODO | Hồ sơ/kết quả nghiệm thu thực tế; nếu còn nghĩa vụ bắt buộc chưa xong thì chưa đánh dấu hoàn tất. |

### Mốc quyết định khi có lệch lịch

| Mốc kiểm soát | Điều kiện phải kiểm tra | Cách xử lý khi chưa đạt |
| --- | --- | --- |
| 2026-10-18 — đầu ra khởi động | Có inventory/baseline hoặc lỗi chính xác; draft contract có nội dung | Nếu lab không truy cập, xác định phương án trước thay đổi. Draft vẫn làm được; không chờ LLM để đọc nguồn/thiết kế. Chưa đủ thông tin thì cập nhật dự báo G0/G1. |
| 2026-10-20 — G0 (gốc 12/10) | Lab và một backend LLM thật hoạt động, RQ/đối chứng/evidence được khóa | Sửa đầu vào, không thay mock rồi ghi AI đã chạy. Rules/đo đạc không phụ thuộc LLM vẫn tiếp tục; đường AI chờ backend thật. Không mở so sánh hai backend trong core. |
| 2026-10-23 — G1 (gốc 16/10) | Event/probe/metric, guard và cấu hình đối chứng qua kiểm chứng | Nếu chưa đạt, không tạo dataset chính thức bằng runner cũ; lập lại lịch G2–G5 và dự báo 31/10 ngay. |
| 2026-10-25 — G2 (gốc 19/10) | Đủ SQLi, DDoS L7 và resource exhaustion đúng mục tiêu | Giữ task còn thiếu trên đường găng, không thay SQLi bằng PodKill. Nếu trễ, mốc G4/G5 phải được dự báo lại; không dồn thêm giờ giả định. |
| 2026-10-27 — G3 (gốc 22/10) | Healer có tác động và recovery được probe xác nhận | Giữ lỗi hở thành BLOCKED cho đường thử cần healer đó; không tính API chấp nhận là thành công. |
| 2026-10-24 — đầu vào paper | Có nơi/đợt nhận bài và điều kiện đăng cụ thể | Hòa làm rõ với thầy, cập nhật mục tiêu nộp 14/11; tiếp tục kỹ thuật và phương pháp không phụ thuộc template. |
| 2026-10-29 — G4 (gốc 25/10) | Trace thật, pilot B0/B1/B2 và quyết định B3/claim RQ2 | Thiếu đối chứng tối thiểu thì chỉ chạy chẩn đoán sửa lỗi. Thiếu B3 thì bỏ claim ưu thế chia vai trò hoặc cập nhật lịch đo; không suy ưu thế từ việc có ba agent. |
| 2026-10-30 21:00 — sẵn sàng War Game | R5-T01 và pilot/protocol R5-T02-S01/S02 đủ bằng chứng, có người giám sát và budget | Chưa đủ thì không chạy cho kịp lịch bằng cách bỏ qua reset/probe/guard. Dời War Game, giữ G5 mở và cập nhật formal run/paper. Ngày 31/10 đang gộp đo dài, phân tích, sửa lỗi và bàn giao, không có dự phòng đã chứng minh. |
| 2026-10-31 — G5 | Core + phép đo + dataset pilot + runbook | Nếu core/phép đo lỗi: chưa đóng kỹ thuật. Nếu phép đo hợp lệ nhưng KPI fail: giữ kết quả, mở task cải thiện và dời formal run khi cần. |
| 2026-11-08 — khóa dataset | Đủ số lặp/nhóm theo protocol, không lộ đáp án, metric và claim tái tính được | Không lấp run thiếu hoặc chỉ chọn case AI thắng; bổ sung phép đo/giới hạn claim và cập nhật ảnh hưởng mốc nộp. |
| 2026-11-14 — G6 | Bản nộp đúng đợt và có biên nhận | Nếu đợt nhận bài chưa phù hợp, ghi WAIT_EXTERNAL và cập nhật theo lịch thật; không tự đổi nơi nộp. |
| 2026-12-10 — mục tiêu chấp nhận đăng | Có thông báo chấp nhận đăng | Nếu chưa có, review rủi ro với thầy vào 2026-12-12; xác nhận phương án và lịch có thẩm quyền, giữ blocker. |
| 2026-12-21 — hồ sơ nghiệm thu | Đủ sản phẩm và bằng chứng chấp nhận đăng | Thiếu chấp nhận đăng thì chưa đủ điều kiện theo thông tin người dùng; không ghi đã nộp hồ sơ hợp lệ. |
| 2026-12-31 — G7 | Kết quả/hồ sơ nghiệm thu thực tế, mọi tiêu chí/sản phẩm bắt buộc được đối chiếu | Nếu còn thiếu thì ghi chưa hoàn tất, nguyên nhân và việc tồn; không tự đóng vì hết hạn. |

### Đối chiếu với các gói sửa W0–W6

R0-T04 là thiết kế nghiên cứu dùng xuyên W1/W4/W5/W6; R1/R2 chuẩn bị metric/evidence và case, không chỉ phục vụ demo.

| Gói trong phần trên | Phase/task triển khai |
| --- | --- |
| W0 — môi trường và LLM | R0 |
| W1 — phép đo và dữ liệu | R1 |
| W2 — ba vector | R2 |
| W3 — healer | R3 |
| W4 — multi-agent AI | R4, gồm quyết định/đối chứng B3 tại R4-T04 |
| W5 — tích hợp và thực nghiệm | R5; R6-T02 |
| W6 — paper, báo cáo và nghiệm thu | R6-T01, R6-T03; R7 |

Các tiêu chí kiểm chứng chi tiết ở phần tiếp theo vẫn là điều kiện bắt buộc. Lịch không thay thế những tiêu chí này và chưa phải kết quả đã đạt.

## Kiểm chứng và thiết kế thực nghiệm

Các tiêu chí hoàn thành là điều kiện phải kiểm tra, chưa phải kết quả đã đạt:

1. **Đường đo thật:** attack có hiệu lực; Gaia tự ghi detect; Kafka chuyển đúng ID; healer xử lý; probe xác nhận recovery. Inject alert chỉ dành unit/integration test của healer và đánh dấu riêng, không nằm trong bộ dữ liệu chính.
2. **Thời gian:** lưu attack_effect_started, detected, published/consumed, heal_started, action_completed, recovery_verified và attack_stopped. Báo MTTD từ effect đến detect, MTTR từ detect đến recovery, thêm total recovery từ effect. Không đổi định nghĩa sau khi thấy kết quả.
3. **KPI:** báo cả tỉ lệ MTTR dưới 120s và 180s vì thuyết minh dùng khoảng 2–3 phút; mục tiêu MTTD <60s, uptime ≥99,9%. Khóa mẫu số lượt sự cố đủ điều kiện trước formal run; timeout/không recovery không tính đạt ngưỡng, missing báo riêng và không tự tính pass. Phân phối MTTR của lượt recovered phải đi cùng tỷ lệ recovery/failure trên tổng lượt để không che thất bại. Chốt threshold đánh giá trước formal run; mọi case chưa đạt được ghi đủ.
4. **Availability:** client độc lập đo phản hồi đúng nội dung và latency cho route/giao dịch đã định; tách time-based availability và request success rate. Chọn cửa sổ warmup/trial/recovery trước khi chạy. Không dùng scrape `up`, thiếu dữ liệu hoặc API patch để suy ra phục hồi.
5. **Downtime budget:** nếu dùng War Game 4h theo kế hoạch repo, uptime 99,9% theo thời gian chỉ cho 14,4s downtime. Cần replicas khỏe phục vụ trong lúc recovery; kiểm tra resource quota/scheduling và budget của máy trước khi tăng replicas.
6. **Đối chứng:** giữ tự phục hồi Kubernetes trong mọi nhóm. Tối thiểu B0 Kubernetes/controller, B1 RULES và B2 MULTI_LLM chạy cùng workload/fault; B1/B2 dùng cùng pipeline/evidence/guard/probe. Profile HPA và quyền scale được cố định/ghi rõ ở mỗi nhóm để quy đúng đóng góp. B3 SINGLE_LLM bắt buộc nếu kết luận lợi ích chia vai trò vận hành; không chạy B3 thì giới hạn claim. Giữ BM manual thật theo protocol/cam kết hiện có và khi kết luận tốt hơn thủ công; lưu alert/thao tác/recovery, tắt mọi auto-heal của ZERO DOOR. Nemesis/harness replay kế hoạch chung, không cấp đáp án cho bên chữa lỗi.
7. **Chất lượng AI:** đánh giá schema validity, action đầu tiên đúng/sai/thừa, phục hồi xác minh trên tổng lượt sự cố, latency, token/call/cost, fallback/refusal và đề xuất bị guard chặn. Khóa mẫu số/ground truth trước formal run, giữ timeout/failure; JSON đúng không tự là hành động chữa lỗi đúng. Lưu model/version/prompt/temperature và evidence không lộ đáp án; không trình bày chat tổng hợp như log quyết định thật. Chỉ kết luận ưu thế LLM/phối hợp khi có nhóm đối chứng và độ bất định tương ứng.
8. **Mẫu và thống kê:** pilot vài lượt mỗi case để xác định độ biến thiên; khóa số lặp formal trước khi đo. Dùng thứ tự xen kẽ/ghép cặp workload hợp lý, reset có xác nhận và cùng budget. Báo mean/median/distribution/confidence, đủ failure/timeout. P95/P99 từ mẫu nhỏ chỉ là thăm dò, không khẳng định ổn định.
9. **Normal windows:** có tải lành tính để đo false alarms và tác động lên người dùng hợp lệ; định nghĩa nhãn và mẫu số FPR. Không hardcode 0 hoặc chia FP cho số tấn công mà gọi là FPR.
10. **Reproducibility:** khóa image/config/dependencies; dataset mới lưu riêng theo method version và run ID. Dùng dataset manifest/hash để chọn đầu vào analysis, tách legacy/pilot/formal; các lượt bị loại có lý do theo protocol và vẫn được lưu/thống kê. Giữ nguyên raw CSV cũ, ghi giới hạn như dữ liệu chẩn đoán lịch sử; timestamp trong CSV không tự chứng minh ngày chạy độc lập, không trộn legacy với formal.

### Các test hành vi ưu tiên

| Tình huống | Kết quả phải kiểm chứng |
| --- | --- |
| LLM output sai schema, service ngoài allowlist, tham số vượt budget | Bị từ chối trước thao tác; có event lỗi; không gọi shell/K8s ngoài phạm vi |
| LLM timeout/429 hoặc mất mạng | Timeout/retry hữu hạn; fallback rõ hoặc skip; không treo consumer, không giả ghi AI thành công |
| Thiếu Prometheus/Elasticsearch/probe series | Health suy giảm/missing; không báo 100% uptime hoặc false success |
| Action FAILED/PARTIAL hoặc timeout trong khi probe vẫn lỗi | Không tạo RECOVERY_VERIFIED hoặc MTTR thành công; failure/censored và mẫu số được xuất đúng; các mốc polling không thay timestamp detector |
| Alert/command bị gửi trùng | Không nhân đôi attack/heal ngoài phiên cho phép; event vẫn truy nguyên được |
| Restart nhiều replicas | Không lấy pod cũ đang Ready làm bằng chứng pod thay thế; nghiệp vụ được kiểm tra |
| Deploy bản lỗi và rollback | Template/image/config thực trở lại release tốt; giao dịch phục hồi trong cửa sổ định trước |
| Chặn attacker và chạy benign client | Attacker bị chặn; benign traffic tiếp tục; TTL/cleanup sau restart được xử lý |
| Attack bị hủy hoặc worker dừng | Tải/fault còn lại được cleanup; không để pod stress/policy tồn dư không ghi nhận |
| Hai vector đồng thời và HPA/healer | Giới hạn tải tổng, quyền scale rõ, không bão lệnh hoặc cooldown làm mất toàn bộ phục hồi |

## Bàn giao cho Hòa và hướng bài báo

Hòa có thể bắt đầu sửa phần giới thiệu, kiến trúc, phạm vi và phương pháp ngay, nhưng không giữ các kết luận “MTTR 1,01s”, “uptime 100%”, “triệt tiêu CVE” từ bộ dữ liệu cũ. Hoàng bàn giao cho mỗi milestone: sơ đồ, định nghĩa metrics, config/commit, event mẫu, dữ liệu/biểu đồ, kết quả chưa đạt và giới hạn.

Bài báo dùng RQ1–RQ3 và ma trận đối chứng trong phần Giá trị nghiên cứu; Hòa nhận câu hỏi/giới hạn claim ở R0-T04, protocol chốt ở R5-T02-S02 và dữ liệu chính thức ở R6-T02. Mô tả kiến trúc ba tác tử tách khỏi claim chứng minh lợi ích chia vai trò; không có B3 thì không kết luận tốt hơn single-agent. Không hứa kết quả vượt trội hoặc đồng nhất phục hồi availability với vá mọi lỗ hổng/“không cửa hậu”.

Paper nên có introduction/related work, architecture/method, experimental setup, results, discussion/limitations và conclusion theo mẫu nơi nhận bài. Không biến sáu chương báo cáo thành paper bằng cách rút ngắn cơ học. Khi có kỷ yếu cụ thể, kiểm tra scope, độ dài, format, lịch và cách nộp trước bản gửi chính thức.

## Việc hoãn và thứ tự bắt đầu

Hoãn triển khai Azure compute/cloud cũ, SaaS đa khách hàng, framework agent lớn, RAG/vector DB, training/RL, nhiều LLM, so sánh cloud–local và viết lại Boutique. Không xem việc có credit là lý do mở rộng hạ tầng.

Gói đầu tiên là **inventory/baseline W0 và bản nháp W1** theo hàng đợi 17/10. Provider được chốt/test theo R0-T03; không buộc bản nháp contract hoặc mọi test rules chờ LLM. Sau contract review và preflight, mở task mã với đường dẫn/test cụ thể, sửa phép đo/guard rồi vector/healer, sau đó AI và thực nghiệm đối chứng. Lượt cập nhật này chỉ sửa roadmap; chưa tạo artifact của hàng đợi, sửa ứng dụng, chạy lab/test/LLM, cài model hoặc tạo tài nguyên trả phí.
