# Audit, bàn giao và các đính chính

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

Bối cảnh đối chiếu tại 17/10/2026. Bảng H01–H08 bên dưới giữ phát hiện và điều kiện kiểm chứng; lịch nguồn đã chuyển vào archive; lịch/trạng thái delivery hiện hành tra Linear khi đã xác minh đúng project, không cập nhật tiến độ trong tài liệu tham khảo này. Đường dẫn roadmap cũ trong trao đổi được thay bằng index Delivery.

## Tiếp nhận bàn giao Antigravity và thứ tự xử lý

[Bản bàn giao Gemini](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md) cung cấp bối cảnh kỹ thuật; [review H01–H08](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-antigravity-handoff-review.md) xác định phần đã đối chiếu và phần còn thiếu nguồn. Roadmap dùng xác nhận trực tiếp của Hoàng cho quyết định hiện tại, mã/dataset cho hành vi được kiểm tra, log thực thi cho runtime. Kế hoạch, checkpoint và hồi tưởng không thay những loại bằng chứng này.

### Tiếp nhận Claude và các đính chính ngày 17/10

[Hydration và review E6](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-handoff.md:345), [phản hồi D8](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-hydration-d8.md) và [blockers đã kiểm tra](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-claude-code-session-blockers.md:93) kết thúc bước tiếp nhận: Claude đủ nắm bối cảnh để nhận issue hẹp; không cần hydration lại. Điểm 19/20 không phải phần trăm hoàn thành dự án. Đây là rà soát trọng yếu dựa trên source/dữ liệu, chưa kiểm chứng mọi trao đổi cũ của Gemini hay toàn bộ hành vi runtime.

| Điểm mới/đính chính | Issue / nguồn áp dụng | Yêu cầu khi thực hiện |
| --- | --- | --- |
| C01 — K3s có controller NetworkPolicy nhúng; Flannel không tự suy ra bỏ policy | R0-T02-S01; R3-T02-S01/S02 | Kiểm phiên bản/args/controller, selector và đường IP thật; đo attacker bị chặn và benign vẫn hoạt động. Chưa có căn cứ thay CNI hoặc recreate cluster. Runtime enforce còn UNKNOWN. |
| C02 — duration trong command không bảo đảm thời gian hoặc tác động thực thi | R1-T04-S01; R2-T02; R2-T03 | Kiểm theo executor; POD_KILL không chạy suốt duration. Giới hạn của command phải bị chặn bởi trần vận hành; EffectiveDuration đang ưu tiên maxDuration của lệnh khi >0, cần test. GET healthz dùng kiểm sức khỏe; không POST attack làm health check. |
| C03 — runner reset, endpoint reset và TTL là ba đường khác nhau | R0-T02-S02; R2-T02-S03; R2-T03-S02; R3-T02-S02; R5 | Runner có lệnh xóa policy theo nhãn nhưng chưa kiểm return code; endpoint không xóa policy; TTL timer mất khi healer restart. Pod stress thử cleanup nhưng lỗi vẫn có thể báo SUCCESS. Xác nhận hậu điều kiện cleanup trước run tiếp. Codex rút lại nhận xét runner không có lệnh xóa policy. |
| C04 — provenance DOCX, graph và CSV phải tách đúng | R0-T01-S03; R5-T03-S02; R6 | Bản trích DOCX có hash/đoạn, không gán thành Claude trực tiếp đọc. CSV ghi ngày 25/06; Git nhập 25/06, thêm/xóa file thử 12–13/07. GitNexus query/context dùng được; status chậm không chứng minh graph hỏng. |
| C05 — owner/file và phụ thuộc của thiết kế khác runtime | R1-T01-S01; mọi issue mã | Claude Code là cộng tác viên phát triển, không phải lựa chọn Claude API. Khóa schema trước sửa producer/consumer; bản nháp không chờ lab/LLM. Mỗi file có một owner trong lượt; chốt cả đường dẫn test/probe trước triển khai. |

**Snapshot điều phối 17/10:** `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`; trước cập nhật roadmap có bốn file handoff ngày 17/10 untracked, mã tracked không đổi. GitNexus index `6337b31` chậm một commit chỉ gồm docs/chỉ dẫn/cấu hình; dùng graph để định vị rồi đọc source hiện tại. Chưa lấy inventory Docker/K8s mới, chưa chạy lab, model hoặc thực nghiệm mới. Ghi chú Complete tháng 7 và snapshot 09/10 dưới đây là lịch sử, không thay trạng thái hiện tại.

**Bảo toàn tài liệu khi công cụ gián đoạn:** issue nhỏ, lưu/đọc lại từng phần; không thay tiêu đề bảo vệ bằng một khối dài. Khi Claude bị classifier chặn, ghi thao tác và phần đã lưu, không retry liên tục hoặc sửa quyền rộng để bỏ qua. Dùng bản trích đúng phạm vi cho DOCX. GitNexus status chậm thì đọc MCP context hoặc meta/HEAD/diff và dirty files; không clean index/xóa lock của tiến trình khác. Các cách này giảm mất dữ liệu, không bảo đảm hết chặn từ nhà cung cấp.

### Các phát hiện H01–H08

| Phát hiện | Issue / nguồn tiếp nhận | Điều kiện đóng liên quan |
| --- | --- | --- |
| H01 — Lý do và lời chấp thuận thiếu chat gốc | R0-T01-S03; R6-T01-S01 | Source ledger phân biệt chat gốc/nhớ lại/suy luận; không gán động cơ hoặc lời duyệt cho Hoàng từ code/commit. Thiếu chat được giữ UNKNOWN, không chặn sửa kỹ thuật. |
| H02 — Nguồn thời hạn khác nhau | R0-T01-S03; R7-T02-S05 | Ghi riêng tháng 01–06 trong DOCX và 31/12 do Hoàng xác nhận; hồ sơ cuối có kết quả đối chiếu và nguồn có thẩm quyền hoặc rủi ro đang chờ xác nhận. |
| H03 — Sai inventory/timeline dữ liệu | R0-T01-S03; R5-T03-S02 | Inventory đúng 8 CSV/40 dòng, 5 lượt/file; timestamp attack_start ghi 25/06/2026 tách khỏi ngày nhập Git/phân tích. Legacy không được trộn vào pilot/formal mới. |
| H04 — Mốc MTTR và terminal status không chứng minh recovery | R1-T01; R1-T02; R3-T01-S01 | Detect do detector ghi, recovery do probe xác nhận; FAILED/PARTIAL không tự tạo MTTR thành công; timeout/missing/failure có mẫu số và giới hạn quan sát rõ. |
| H05 — Runtime suy từ plan/ghi chú | R0-T01-S03; R0-T02-S03; R0-T03-S02 | Phân biệt báo cáo tự đánh giá với log thực thi; có evidence lab/model mới để đóng gate. Cloud tắt ghi theo Hoàng, không tự xác nhận thao tác/tài nguyên/ngày tắt cụ thể. |
| H06 — Sai hướng dẫn phục hồi cluster | R0-T02-S01; R0-T02-S02 | Inventory quyết định start hay recreate; lệnh/script dựng cluster được kiểm tra đúng chức năng. `bash rebuild-nemesis.sh --no-forward` chỉ build/import/rollout Nemesis, không dùng thay bước tạo cluster. |
| H07 — Claim tài nguyên/ưu thế chưa có đối chứng | R0-T04-S01; R4-T04; R6-T01-S01; R6-T02-S04 | Giữ RAM <100MB, giảm 88%, tổng 157MB và nhận xét vượt AIOps ở mức claim cũ chưa xác minh; bỏ khỏi kết luận nếu không đo. Claim lợi ích chia vai trò cần B3; không mở benchmark RAM bắt buộc chỉ để giữ claim cũ. |
| H08 — Path, danh tính và nguồn chưa chuẩn hóa | R0-T01-S03; R5-T03-S03 | Dùng path thật, nguồn IDE có đường dẫn/loại nguồn; không suy hp8001 là Hòa. Thông tin nơi nhận bài vẫn chốt tại R6-T01-S03, không hỏi lại như blocker tiếp nhận. |

**Thứ tự bắt đầu:** chụp baseline/source ledger và preflight lab → khóa event/probe/phép đo → kiểm chứng vector và healer → tích hợp LLM → pilot đối chứng → formal dataset và paper. Chỉ các mô tả kỹ thuật đã đối chiếu được dùng làm đầu vào sửa; lịch sử chưa xác minh không quyết định thiết kế hoặc trách nhiệm cá nhân.

**Dataset cũ:** review ghi nhận 8 CSV với 40 dòng, trong đó E3 AUTO có 4/5 lượt FAILED nhưng vẫn mang MTTR khoảng 1,01–1,02s. Điều này minh họa lỗi phương pháp, chưa xác định nguyên nhân runtime của từng thất bại. Không diễn giải khoảng 1s là latency K8s API hoặc tốc độ hồi phục nghiệp vụ; 9,24s là P95 MTTD E3 AUTO trong summary, không phải max 11,26s trong raw. Giữ nguyên dữ liệu, hình và báo cáo cũ để truy vết; bản viết mới phải nêu giới hạn và dùng dataset mới hợp lệ.

## Snapshot kiểm tra ngày 09/10/2026 và giới hạn xác nhận

Mã ứng dụng tại HEAD `6337b319b075bf389d484a6be13a4bc094f94a82` chưa được sửa trong lượt này. Metadata GitNexus có cùng commit, 96 files, 1.409 nodes, 44 processes; dùng graph để xác định hàm LLM và đọc mã thật để xác nhận, không dùng graph làm bằng chứng vận hành.

- Máy: Intel i7-11800H, 8 cores/16 threads, RAM khoảng 15,8 GiB; GPU RTX 3050 Laptop, VRAM 4.096 MiB. Docker báo được cấp khoảng 6,77 GiB RAM, 4 CPU.
- Trong lần lập kế hoạch ban đầu, Docker daemon trả lời truy vấn thông tin; context Kubernetes là `k3d-zero-door`, API `127.0.0.1:58117` từ chối kết nối và truy vấn container tên `k3d-zero-door` không trả container. Lượt review handoff sau đó chưa lấy được snapshot lifecycle mới do truy vấn Docker lỗi quyền rồi treo và được ngắt. Các quan sát này không chứng minh container hiện exited hoặc cluster còn tồn tại; R0-T02-S01 phải lấy inventory mới. Chưa khởi động, tái tạo cluster hoặc xóa volume.
- Không thấy lệnh Ollama trên PATH; API localhost:11434 không trả lời. Chưa chứng minh có local inference server đang hoạt động ở endpoint khác.
- [Nemesis](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/nemesis/main.py:276) có mã gọi OpenAI-compatible API, Gemini và Ollama. [Manifest](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/manifests/nemesis-deployment.yaml:17) chọn Gemini, có cấu hình Ollama/OpenAI nhưng secret mẫu để trống. Không đọc được trạng thái Secret đang triển khai do cluster chưa kết nối; không thể kết luận từ manifest rằng trước đây chưa từng có API key.
- Chưa chạy một lượt gọi LLM, tải model, tạo tài nguyên Azure, chạy attack hoặc healing trong lượt này. Có mã tích hợp LLM không đồng nghĩa agent hiện hoạt động với LLM.
