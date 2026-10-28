## Publication đã được Hoàng duyệt — 28/10/2026

Hoàng duyệt publication ZER-16 và Done khi đủ gate; [authorization](publication-authorization.json) giữ exact reply/proposal hash. Đang chuẩn bị commit/PR; remote CI/merge/Done còn chờ, không có thêm lab. Các trạng thái PREPARED/NOT_AUTHORIZED dưới đây là checkpoint trước approval.

# ZER-16 — trạng thái action và xác minh độc lập

Ngày28/10/2026, Asia/Saigon. [AC sống trên Linear](https://linear.app/zero-door/issue/ZER-16/xac-minh-trang-thai-va-ket-qua-phuc-hoi-sqli).

**READY_FOR_PUBLICATION_REVIEW.** Gói component đã qua kiểm offline và [review độc lập](independent-review.md); chưa commit/push/CI remote/merge/Done. Chỉ AC-01 còn hiệu lực theo SCOPE SQLi-only; scale/HPA nguồn vẫn chưa nghiệm thu.

## Thay đổi và ranh giới

Thêm `hephaestus/sqli_action_state.py` để theo dõi một action SQLi đã được guard chấp nhận và writer trả `API_ACCEPTED`. API acknowledgement tự nó không tạo terminal. Chỉ khi receipt độc lập chứng minh A bị403 và B catalog + create/read/delete/read-after-delete hoạt động, cùng source/proxy/action/policy digest/Pod UID và thứ tự thời gian, mới có `ACTION_COMPLETED/SUCCESS`.

Deadline bị chặn bởi TTL gốc; FAILED/PARTIAL/TIMEOUT không được nâng thành SUCCESS bởi probe đến muộn. Pod replacement cần UID khác, Pod cũ absent và bộ probe nghiệp vụ mới trên đúng UID. Action SUCCESS giữ ý nghĩa lịch sử; không tự chứng minh sức khỏe hiện tại. Module không gửi request, phát event, tải cấu hình/credential hay bật executor. Người gọi phải cung cấp quyết định đã qua guard và bằng chứng độc lập, không dùng nhãn do HTTP/model tự khai.

`RECOVERY_VERIFIED` vẫn do evaluator H-plane hiện có trong `measurement/recovery.py` và scorer tái tính từ probe; healer không tự phát trạng thái này. Probe có thể quan sát phục hồi dù action FAILED/PARTIAL/TIMEOUT, nhưng không được ghi công cho healer. Hết fault/TTL hoặc Kubernetes thay Pod không tự chứng minh healer đã phục hồi availability.

Hephaestus Dockerfile copy hai prepared component và CI kiểm import; R1 executor/consumer guard giữ disabled. Tích hợp consumer thuộc ZER-18/R5, không được báo đã triển khai từ gói này.

## AC-01 → kiểm → kết quả

| Phần AC | Kiểm chứng | Kết quả |
| --- | --- | --- |
| API_ACCEPTED khác ACTION_COMPLETED và recovery | Test API-only/forged-success; action SUCCESS chỉ sau hậu điều kiện; evaluator/scorer hiện có kiểm success không có recovery, failed/partial/timeout hoặc thiếu terminal không được ghi công. | Đạt ở component và evaluator; không giả live event stream. |
| State machine/timeout/missing | Deadline boundary, late proof, nonfinite clock, thiếu benign, sai join/IP/proxy/action/digest/content, terminal FAILED/PARTIAL/TIMEOUT. | Không tạo SUCCESS sai; thiếu hậu điều kiện tới deadline thành TIMEOUT. |
| Restart có danh tính và nghiệp vụ | Test UID/Ready/old absence và replay HTTP016–021 trên Pod mới từ raw09. | Có bằng chứng replacement + block/benign CRUD; không tạo terminal lần hai hoặc quy hiệu ứng controller thành healer recovery. |
| Log đối chiếu probe thật | [Replay](replay.json) dùng [reconcile.py](reconcile.py), kiểm SHA25645 artifact đầu vào của ZER-46/runtime09. API-only rồi action hoàn tất; replacement riêng; Boutique false/recovery chưa xác minh. | Đạt cho phép phân loại trạng thái; **đây là assessment mới từ raw cũ, không phải event lịch sử**. |

API RPC cũ không có timestamp receipt chính xác. Replay dùng thời điểm hoàn tất đọc lại đúng policy API tại raw0116 làm **cận trên acknowledgement**, không bịa T_api hoặc KPI. Deadline120s của assessment giới hạn bởi expiry gốc; không thay envelope/runtime09 hoặc sửa bằng chứng nguồn. Raw logs, writer/fixture, rules/TTL và mọi failure/UNKNOWN lịch sử giữ nguyên.

## Kiểm và provenance

- HEAD/base thực hiện `6bf7d558d569b75af8d85ab108984d1ecd96623d`, branch `codex/zer-16-recovery-state`; tạo nhánh từ merge PR31 có tree giống HEAD73ebead ban đầu. Dirty ZER-17 bảo toàn; intake/hash ở `scratch/zer16/scope.json`.
- State14 + containment24 trên mỗi environment production Nemesis/Hephaestus; recovery12 + scorer37 + CI guard6: **131 lượt test đạt**. [Log](results/). Ban đầu system Python thiếu Kubernetes ở regression; chuyển sang environment đã khóa sẵn, không cài gói hoặc đổi test.
- Packaging kiểm import hai module trong thư mục tạm mô phỏng COPY, cùng wiring CI/import smoke; **chưa build/chạy Docker image mới**. Remote image build/import smoke sẽ chạy sau quyền publication.
- [Review độc lập](independent-review.md) đọc source/test/replay/packaging và kết quả; không chạy lab. [Source hashes](source-hashes.json) khóa đúng bytes được review.
- GitNexus đang index primary9567830/incomplete incremental-in-progress, thiếu FTS/PDG phù hợp; query/context không tìm được symbol, detect_changes không map untracked source. Không dùng zero hits/risk low làm bằng chứng; review căn cứ source/diff/test, không claim graph-backed coverage.

## Giới hạn và bước cuối

Không có request lab, build/import/pull, Kubernetes/shared mutation hoặc inference mới. Boutique business **NOT_MET**, chưa có continuous formal recovery stream; không `RECOVERY_VERIFIED`, MTTR/KPI, production healer/LLM/end-to-end hoặc gate R3 PASS. Component này có thể ghi action hậu điều kiện đạt trong khi recovery độc lập chưa đạt — đó là kết quả đúng, không phải hạ AC.

Theo [WORKFLOW](../../delivery/WORKFLOW.md), còn quyền publication và các gate CI/review/merge/Hoàng acceptance trước Done. [Gói publication](publication-package.md) chỉ gồm ZER-16, không kéo dirty ZER-17 hoặc primaryR. Không mở issue khác trong gói này.
