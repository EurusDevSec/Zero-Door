# ZER-19 runtime-03 — NOT_MET, cleanup CLEAN

Hoàng duyệt đúng một lượt theo [proposal](../acceptance-03-proposal.md); [authorization](../acceptance-03-authorization.json) và27 source pins khớp started/invocation manifest. Lượt bắt đầu 2026-10-29T03:16:47.026Z, kết thúc khoảng 2026-10-29T03:22:44.228Z (UTC; giờ Việt Nam +7), **357.201 giây**. Không chạy runtime-04.

**Blocker: POLICY_HOOK_MISSING**, chưa tới inference/executor. Preflight25 mẫu/120s đạt và shared inventory không đổi. Sau khi tạo proxy và gated safe fixture trên node agent,80 lệnh đọc iptables-save qua179.039s đều thành công nhưng không thấy tên/IP fixture b3fd1113-36b1-4f09-97d3-d25b3db7d0c8 /10.42.0.214. Rules policy namespace có mặt, song không đủ chứng minh hook của Pod này. Runner không release fixture hoặc bỏ qua gate để tiếp tục. Không suy đây là lỗi chức năng model/Nemesis/SQLi.

Trong61 mẫu guard: host available thấp nhất2,243,510,272bytes; WSL2,457,208KiB; memory PSI avg10 cao nhất0; CPU/IO PSI diagnostic max15.78/0.14; lệnh đọc memory chậm nhất0.172s. Không guard failure. Đợt stall lượt02 không lặp qua các mẫu quan sát ở lượt này; **không kết luận đã chữa vĩnh viễn nguyên nhân cũ**.

Raw cho thấy firewall đọc trong Docker agent container có comment của3 Pod được Kubernetes xếp trên server. Chỉ hai lệnh inventory chỉ đọc sau đóng lượt được thêm ở [node identity](node-identity-readonly.json): Docker IP agent172.19.0.3/server172.19.0.4 khớp Node InternalIP. Vì vậy hiện tại không có bằng chứng IP bị hoán đổi đơn giản. Nguyên nhân controller/programming/dataplane chưa được xác định; không tự sửa hoặc restart CNI/shared node.

## Cleanup và hoạt động thực

- Namespace UID7cda8172-90b2-469d-8f55-ba99452cad6e đã UID-delete; raw0196/0197 xác nhận absent. Shared Deployment/PVC spec+UID và Pod restart giữ nguyên;3PVC Bound. **Cleanup CLEAN**.
- Chỉ2 workload private được start. **0 model call,0 fixture HTTP,0 TCP control,0 topic,0 private Secret,0 worker/Nemesis Pod,0 build/import/pull**. Câu provider_credentials_scope chung trong raw cleanup không có nghĩa đã tạo/xóa3Secret: bước tạo Secret chưa tới.
- Harvest PARTIAL vì Nemesis/worker chưa tồn tại: không có session receipt/log để thu. Giữ đúng PARTIAL, không gọi đó là trace đầy đủ hoặc bỏ raw errors.
-9 product pins và27 invocation pins khớp; không sửa sản phẩm sau review. [Phân tích tái lập](analyze.py) → [analysis](analysis.json), [acceptance](acceptance.json), [cleanup](cleanup.json).

**Chưa đạt AC02/03; ZER-19 chưa Done.** Publication có điều kiện không được kích hoạt; không commit/push/PR/merge hoặc đổi Done, không mở issue khác. Lượt01/02 và mọi failure/UNKNOWN giữ nguyên.

Bước cần quyết định tiếp theo là xử lý đúng blocker NetworkPolicy/dataplane trên node agent bằng một gói hạ tầng riêng có phạm vi và rollback rõ, trước bất kỳ proposal nghiệm thu mới nào. Không thử lại model, tăng timeout gate, bỏ kiểm cô lập hoặc lặp runtime04 để dò. Phần hiện tại khép với kết luận blocker có bằng chứng và cleanup đã xác minh.
