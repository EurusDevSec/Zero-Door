# ZER-46 — gói sửa runner hoàn chỉnh offline, 28/10/2026

**59/59 offline đạt. ZER-46 vẫn AC_PARTIAL / NOT_READY_FOR_PUBLICATION.** Gói sửa offline không tác động lab; một diagnostic riêng được Hoàng duyệt sau đó đã khép như cập nhật bên dưới. Không có runtime09. [Receipt máy đọc](runner-complete-verification.json); gói này thay tình trạng ba việc sửa runner còn mở trong stop-audit, không thay kết luận08 hoặc chứng minh nguyên nhân PSI đã hết.

## Cập nhật kết thúc gói — diagnostic đã đóng

Hoàng đã duyệt và đã chạy đúng một chẩn đoán,234,89s:1GET200+joined log,39guard samples/PSImax0,12,owned cleanup CLEAN/shared3PVC nguyên. Boutique không khỏe. PSI08 không tái hiện trong sample; chưa chứng minh causal fix. Authority display gặp UTF8/cp1258 mojibake, operative fields/hash đúng và raw giữ nguyên; đã sửa explicitUTF8 và thêm test,59/59offline đạt. [Kết luận diagnostic](../client-diagnostic-01/README.md).

Lịch TTL160s+15s reserve/native writer exit/full verifier vẫn mới kiểm offline, chưa fullAC hoặc review độc lập. Manifest/approval diagnostic cũng đã tiêu thụ, candidate sau encodingfix khác snapshot. **Dừng runtime; chưa có quyền/lượt09; ZER-46 AC_PARTIAL/NOT_READY_FOR_PUBLICATION.** Những mô tả NOT_APPROVED của proposal bên dưới là checkpoint trước khi Hoàng duyệt, không là status hiện hành.

## Những lỗi đã khép

- Lịch pha TTL theo expiry gốc180s: projection40s, block/benign trước35s, dừng writer10s, replacement30s, block/benign sau35s, writer replay10s; tổng160s, reserve15s, còn5s overhead ban đầu. Mỗi pha còn phải đủ budget cho các pha sau; command đang chạy bị hủy nếu chạm deadline. Pha quá hạn không được xóa bằng cách bước sang pha kế. TTL không tăng/renew. Những số này là giới hạn fail-fast của candidate, chưa là đo khả năng lab.
- Kiểm oldPod UID absent chuyển vào khoảng chờ TTL sau khi Pod mới đã có request/log đúngUID và replay xong. Không bỏ kiểm: vẫn poll≤45s, raw readback absent + receipt riêng bắt buộc trong verifier. Không force-delete; các request hậu restart không được join vào Pod cũ.
- Log đến chậm được đọc lại tối đa3lần trong cùng deadline6s, giữ exactPodUID; không replay HTTP để bù log. Full verifier đối chiếu join với rawlog đúngPod.
- Writer gửi hello/instance token trước block; host giữ Windows process handle với PID/creation time/executable, sau shutdown xác nhận handle báo EXITED cùng exit code launcher. Handle tránh nhầm PID được tái sử dụng. Launcher và RPC PID có thể khác. Thiếu identity, process còn sống hoặc UNKNOWN tạo receipt lỗi và làm cleanup INCOMPLETE; không ngăn UID-pinned namespace delete. Không enumerate/kill tiến trình lạ. Native API đã kiểm bằng fake API; chưa xác minh contract mới trên writer thật.
- Full verifier veto failure.json, guard/cleanup errors, canceled/unknown/nonzero command receipts, thiếu/thừa dispatch, response không khớp, thiếu writer exit proof, phase overrun và join không có raw log. Watchdog chưa dừng cũng chặn cleanup thuận lợi. Không dùng API accepted hay acceptance flag đơn lẻ làm PASS.
- Đọc evidence/config bằng UTF8 tường minh, không dựa locale Windowscp1258. Giữ receipt gốc bị sai display và canonical authority riêng, không sửa raw.
- CLIENT giữ partial stage/counter receipts tại interpreter/imports/request_ready/headers/response_end, đọc hữu hạn cgroup để phân biệt stall với socket timeout; không thay3s socket/15s outer timeout hoặc guard.

## Kiểm chứng

Các suite12+5+5+9+4+3+21=59 case; process, HTTP và native handle đều mock. So source trước sửa trên21case mới:4failures/10errors (bao gồm helper chưa tồn tại),7case vẫn đạt; đây là baseline regression, không phải21 lỗi runtime. Đường protocol được kiểm thứ tự phase/delete/restart/replay/expiry bằng clock giả.

Bandit high severity/high confidence không finding; log vẫn ghi low-severity findings, không gọi toàn bộ mức là0. Bash syntax và --help inert đạt. Raw08 reconciler chạy offline, chặn subprocess/ghi artifact cũ và đối chiếu đúng receipt hiện hữu.4.657 file ngoài scope và914file runtime01–08 nguyên hash; HEAD9567830, staged rỗng. Không refresh index GitNexus lỗiFTS/256MiB; không dựa graph làm bằng chứng.

Log riêng runner-complete-*.log ở thư mục này. Đây là self-audit và checker riêng, **chưa phải review độc lập bởi người/agent khác**. App/backend/image, shared infra, guard, AC và raw cũ không đổi. Manifest/approval08 giữ nguyên, đã tiêu thụ; không cập nhật hash cũ để hợp thức hóa patch.

## Vì sao chưa chạy nghiệm thu tiếp

Raw07 chỉ hỗ trợ planning: từ rule creation đến HTTP9blocked≈36,07s; HTTP9begin đến HTTP15end≈28,70s; HTTP15end đến HTTP16end≈15,98s. HTTP16 thiếu trace; các số này không thay AC, không chứng minh remaining phases hoặc timing mới. Không trộn07/08 thànhPASS.

PSI08 tập trung ở sourceA nhưng thiếu delta theo pha. Snapshot không có OOM và available RAM đủ; CPU throttle đồng thời chưa chứng minh causal root. Không tăng resource/guard hoặc bắt Hoàng tiếp tục đoán RAM.

Đã chuẩn bị [một chẩn đoán lành tính](../runtime-prep/client-diagnostic-proposal.md), source/config được khóa trong manifest riêng; **NOT_APPROVED / NOT_RUN**. Tối đa1fixtureGET +32Boutique observerHTTP, ≤2RPS/concurrency1,20phút gồm5cleanup,0build/import/pull, không writer/block/TTL/replacement/shared change. Chỉ sau quyền exact gói mới tạo attempt. Probe không tái hiện lỗi chỉ là một mẫu hoạt động, không chứng minh causal fix, không tự mở runtime09.

Chẩn đoán một lần đã khép. Bước tiếp theo là review gói sửa/evidence và chốt quyết định về blocker PSI/fullAC còn thiếu; không tự chạy thêm probe hoặc containment. Chưa có causal correction được chứng minh cho PSI08, nên giữ điểm dừng, không biến một sample tốt thành quyền retry. Review/merge/Hoàng acceptance vẫn cần trước Done; chưa có Git publication.
