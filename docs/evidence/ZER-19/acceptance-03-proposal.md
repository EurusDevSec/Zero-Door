# ZER-19 — đúng một lượt nghiệm thu sau điều tra và sửa runner

PREPARED / NOT_APPROVED / NOT_RUN — 29/10/2026 (Asia/Saigon).

## Căn cứ và kết quả cần đạt

[Điều tra runtime-02](investigation/README.md) xác nhận stall Docker/K3s đồng thời với CPU/memory pressure; không chứng minh Chrome/Claude hoặc một tiến trình là tác nhân khởi phát. Không có bằng chứng lab đã hết stall. Guard đã dừng đúng, không tăng timeout hoặc đổi shared CPU/WSL để che lỗi. Bản sửa runner bổ sung receipt/CPU-I/O PSI và chặn shared drift trong preflight, không thay AC.

AC01 dùng lại ZER-48/PR34. AC02/03 vẫn cần một chuỗi thật observation → một inference qua adapter → registry template hợp lệ → existing executor → result, cùng phiên tự kết thúc và usage/stop trace. Các kiểm offline không thay bằng chứng này.

Runtime-01 và02 đã đóng, quyền từng lượt đã dùng hết. Runtime-02 có 0 model/HTTP/topic/private Secret; namespace UID66fed02a-ec50-4bfb-ab1c-ebeda976d12d đã xóa và xác minh absent. Remote release-file outcome cũ vẫn UNKNOWN, tài nguyên chứa nó đã bị xóa; không gửi lại lệnh cũ để dò. Global cleanup cũ giữ INCOMPLETE vì cart restart41→42; không đổi nó thành CLEAN. Lượt mới lấy baseline shared hiện hành, không coi lỗi lịch sử là đã được chữa.

## Envelope duy nhất xin duyệt

Giữ protocol của approved-completion-proposal.md, với admission/source lock mới dành riêng runtime-03:

- Đúng một attempt runtime-03, tối đa20 phút gồm5 phút cleanup; 0 automatic retry, không tự runtime-04. Exclusive output directory trước preflight; không reset/ghi đè attempt đã bắt đầu.
- Chỉ Docker desktop-linux/Kubernetes k3d-zero-door; private namespace zd-sqli-lab phải absent; tối đa4 cached workloads trên k3d-zero-door-agent-0. 0 build/import/pull. Không sửa/restart shared workloads, CoreDNS/CNI/Prometheus/RBAC/PVC/WSL hoặc ứng dụng khác.
- Preflight25 mẫu/120 giây: Windows và WSL available RAM≥1GiB, memory PSI some avg10≤5; sampling command timeout4 giây/nhịp5 giây/fail-closed. Cùng lệnh cat đọc thêm CPU/IO PSI để chẩn đoán, không tự đặt ngưỡng mới. Sau cửa sổ, API snapshot phải trả về và shared UID/spec/restart không đổi trước tạo fixture. Guard vẫn chạy qua setup; guard/preflight/cache/identity lệch thì NO-GO/NOT_MET rồi cleanup, không nới ngưỡng.
- Đúng4 cache image theo runtime-images.json/cache-pins.json; source/config/disabled manifest giữ pin. Namespace atomic create, UID ownership/readback; policy-release hook và fixture UID/IP phải khớp trước bind; private trusted proxy/32 và ingress IP cố định. Không adoption hoặc cleanup theo prefix rộng.
- Tối đa1 OpenAI gpt-6-luna Responses call/1 attempt/0 retry, ≤256 output token, attempt20s/call25s/session120s, max calls1/reserved tokens9472. Reservation estimate≤0.005 USD; không phải billing hard cap. API key từ Doppler hiện có, chỉ qua stdin/Secret riêng, không argv/log/artifact.
- Chỉ health observation trung tính và template benign-apparel đã có hoặc STOP; không payload/vector/target mới, không discovery/disclosure. Policy/URL/namespace không do model quyết định. STOP/refusal/schema/usage/evidence failure giữ nguyên kết quả, không gọi lại để lấy PASS.
- Tối đa1 signed existing SQLI command benign-apparel, duration1s/maxSends1/concurrency1/≤1RPS. Tổng≤3 HTTP lành tính (before/executor/after) và≤1 TCP denial control; không Boutique probes/healing/load. Không gửi lại command nếu ack/result UNKNOWN.
- Chỉ2 topic zer19-e0e0aea10613.commands và zer19-e0e0aea10613.results, absent trước tạo; consumer group riêng. Context/IDs cũ chưa dispatch provider/command, nên giữ nguyên; không reset budget đã dùng. 3 Secret tạm xóa cùng owned namespace; worker/Nemesis activeDeadlineSeconds900.

## Evidence và điều kiện kết luận

Runner phải pin proposal + authorization + source manifest trong started.json và copy source-manifest-at-invocation.json. Receipt command ghi elapsed/reason/spawn/kill/reap/exit; output lệnh có stdin được che kể cả lỗi. Kill client không biến remote outcome UNKNOWN thành known failure.

Giữ baseline/control/policy enable/one-session/post-probe như protocol gốc. Chỉ technical PASS khi đúng1 real successful model trace và usage,1 valid command/result/raw log join,1 executor send200/0restrictedRows, MAX_ROUNDS/completed_rounds1, probe trước/sau200, guard đủ và cleanup CLEAN. API accepted/STOP/refusal/timeout/missing không thay PASS. Không formal benchmark/KPI/G3/G4/end-to-end claim.

Cleanup trong cửa sổ: stop/capture owned trace trước xóa; UID-delete namespace, xác minh absent, chỉ xóa topic thực sự sở hữu khi consumers đã hết; readback shared spec/UID/restart và3PVC không đổi. Nếu thiếu inventory trước thì không gọi readback là proof preserved. Failure/UNKNOWN/raw cũ giữ nguyên; không force finalizer hoặc xóa tài nguyên khác.

Nếu stall hoặc blocker tái diễn, giữ receipt mới và chốt kết luận, không tiếp tục vòng thử. Preflight sạch không hứa phase setup sẽ sạch; đây là một phép nghiệm thu có guard, không là xác nhận đã sửa xong lab.

## Admission và publication

HEAD093e924000861da3096185427994d9ea736df36d/branch codex/zer-19-nemesis-session. Source lock: runtime-prep/source-manifest-03.json. Gói thiếu acceptance-03-authorization.json APPROVED với đúng proposal hash/source-manifest hash/max_attempts1/attempt runtime-03 thì dừng trước outputdir/Lab. Không viết authorization trước câu trả lời của Hoàng. Source-manifest và authorization lịch sử của lượt01/02 giữ nguyên.

Nếu runtime đạt: review raw/source/config rồi publication đúng scope ZER-19 (commit/push/PR/CI/review/merge), chấp nhận Done chỉ khi mọi gate đạt như WORKFLOW. Quyền publication có điều kiện của gói gốc được xác nhận lại trong gói này; giữ dirty ZER-16/17/18/R3-G3/R4 queue/ZER48 và primaryR, không git add tất cả. Nếu runtime không đạt thì không publication/Done, không mở issue khác.

Đề nghị Hoàng duyệt đúng một lượt runtime-03 theo toàn bộ envelope trên và publication có điều kiện; không cấp quyền thử không giới hạn hoặc đổi hạ tầng để lấy PASS.
