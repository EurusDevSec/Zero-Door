# ZER-19 — một lượt nghiệm thu sau sửa NetworkPolicy (runtime-04)

Ngày 29/10/2026. **PREPARED — chưa được duyệt/chưa chạy.** Gói này xin đúng một lượt observation → model → executor → result; không cấp quyền thử lại vô hạn. ZER-19 AC02/03 chưa đạt. AC01 dùng evidence ZER-48/PR34 đã nghiệm thu.

## Căn cứ và phần chưa biết

Hoàng giao Claude điều tra/sửa hạ tầng rồi chuyển kết quả cho Codex. Audit offline của Codex ở [acceptance04-prep/verification.json](acceptance04-prep/verification.json), dựa trên [repair evidence](networkpolicy-repair/README.md): cả 9 checksum khớp, README SHA256 3ddaa0c5a80069304c7357be5cf4ffc86b1e06f9b10f82c667e6473bea7a836c. Snapshot trước sửa có startup log IP agent .4/server .5, trong khi Docker/Node hiện là .3/.4; firewall map sai node. Sau restart từng node, snapshot cuối có agent19/19 và server3/3, missing/foreign đều rỗng, 24 Pod Running/Ready, 3 PVC Bound và 26 workload UID giữ nguyên.

Các snapshot chứng minh tương quan IP khởi động và firewall map rồi phục hồi sau restart. Chưa xác định nguồn IP cũ trong k3s, chưa có traffic denial/allow proof mới; không khẳng định đã phòng ngừa vĩnh viễn hay mọi NetworkPolicy từng mất hiệu lực. Không cần truy tìm sâu thêm để nghiệm thu nếu các gate dưới đạt.

runtime-03 giữ NOT_MET/POLICY_HOOK_MISSING, cleanup CLEAN; 0 provider/HTTP/TCP/topic/Secret. Evidence và quyền cũ giữ nguyên. runtime-02 giữ NOT_MET/cleanup INCOMPLETE; không sửa lịch sử thành PASS. Restart do Claude thực hiện nằm ngoài cửa sổ nghiệm thu mới; baseline mới phải lấy sau sửa, không yêu cầu restartCount quay về số cũ.

## File/action scope đã chuẩn bị

HEAD 093e924000861da3096185427994d9ea736df36d, branch codex/zer-19-nemesis-session. Delta helper chỉ thêm admission runtime-04 và kiểm map NetworkPolicy hai node bằng các lệnh đọc có timeout; 9 pin sản phẩm, config, image và manifest disabled không đổi. Scope/bytes helper cũ tại acceptance04-prep/. GitNexus primary index cũ/FTS thiếu, không tìm thấy helper; kiểm source trực tiếp, không reindex nặng.

Source lock: runtime-prep/source-manifest-04.json; giữ manifest/authorization/raw01–03. Thiếu acceptance-04-authorization.json APPROVED đúng attempt/proposal hash/source-manifest hash/original authorization hash/max_attempts1 thì dừng trước tạo output directory/Lab. Chỉ tạo authorization sau câu trả lời trực tiếp của Hoàng. OUT runtime-04 tạo exclusive; directory đã tồn tại thì không chạy lại. Không có runtime-05 trong CLI/admission.

## Envelope xin duyệt — giữ protocol cũ

- Đúng 1 runtime-04, tối đa20 phút gồm5 phút cleanup. Cửa sổ guard bao gồm preflight, setup và thực hiện; không tự runtime-05 khi NO-GO/fail/UNKNOWN/STOP/refusal. Không xóa/reset attempt để chạy lại.
- Chỉ Docker desktop-linux/Kubernetes k3d-zero-door, private namespace zd-sqli-lab phải absent. Tối đa4 cached workloads trên k3d-zero-door-agent-0; dùng đúng4 image của runtime-images.json/cache-pins.json, 0 build/import/pull. Không sửa/restart hạ tầng dùng chung, node/Docker/WSL/CoreDNS/CNI/RBAC/Prometheus/PVC hoặc ứng dụng khác. Không chạy script restart_node.sh của Claude.
- Preflight25 mẫu/120 giây, Windows/WSL available RAM≥1GiB, memory PSI some avg10≤5; sampling timeout4 giây/nhịp5 giây/fail-closed. CPU/IO PSI chỉ chẩn đoán. API phải trả lời, shared UID/spec/restart giữ nguyên trong baseline mới. Guard tiếp tục qua setup.
- Sau baseline, **trước tạo namespace**, đọc Node InternalIP, Docker bridge IP và iptables trên cả2 node, timeout8 giây/lệnh. IP phải khớp, mọi Pod Running không hostNetwork phải có chain trên đúng node, không missing/foreign; không khóa cứng số19/3 vì inventory có thể đổi hợp lệ. Sai/thiếu/timeout → NOT_MET/cleanup, không tự restart. Đây là kiểm map, không thay thế fixture-specific UID/IP policy-release hook và TCP denial control đã có.
- Namespace atomic create/UID ownership, private trusted proxy /32, ingress pin và fixture UID/IP release gate giữ nguyên. Không adoption hoặc cleanup theo prefix rộng.
- ≤1 call OpenAI gpt-6-luna Responses, ≤256 output token, 0retry; attempt20s/call25s/session120s/maxcalls1/reservedtokens9472. Reservation estimate≤0.005 USD, **không phải billing hard cap**. API key từ Doppler hiện có, chỉ stdin/Secret riêng, không argv/log/artifact.
- Observation health lành tính, model chỉ chọn template benign-apparel có sẵn hoặc STOP; không tạo payload/vector/target mới/discovery. Policy/URL/namespace cố định ngoài quyết định model. STOP/refusal/schema/usage failure giữ đúng kết quả, không gọi lại để lấy PASS.
- ≤1 signed command existing SQLI benign-apparel, duration1s/maxSends1/concurrency1/≤1RPS. Tổng≤3 HTTP lành tính (before/executor/after)+≤1 TCP denial control. Không Boutique/healing/load probes, không gửi lại command nếu ack/result UNKNOWN.
- Chỉ2 topic zer19-e0e0aea10613.commands / zer19-e0e0aea10613.results (phải absent trước tạo), consumer group riêng. Context IDs giữ nguyên vì các lượt cũ chưa dispatch provider/command; admission kiểm ngân sách cũ chưa dùng và cleanup03. 3 Secret tạm chỉ trong owned namespace; worker/Nemesis activeDeadlineSeconds900.

## Điều kiện kết luận và cleanup

Technical PASS chỉ khi đúng1 model trace thành công/usage đầy đủ,1 kế hoạch được validate trước dispatch,1 command/result/raw log join, executor send1/HTTP200/restrictedRows0, MAX_ROUNDS/completed_rounds1, before/after probe200, bounded session/call/cost logs, guard đủ và cleanup CLEAN. Offline stop/cancel/error tests được dùng cùng runtime tự dừng; không bịa cancel live nếu không chạy. API_ACCEPTED hoặc thiếu trace/UNKNOWN không thành PASS; đây là functional component acceptance, không formal benchmark/KPI/G3/G4/healing end-to-end PASS.

Thu trace/log và stop owned session trước xóa; UID-delete namespace, xác minh absent; chỉ xóa topic thực sự sở hữu sau khi consumer hết. So shared spec/UID/restart và3PVC với baseline sau sửa. Mọi impact/failure/UNKNOWN giữ raw; không force finalizer/xóa object khác. Kill client không chứng minh remote operation đã thất bại.

Nếu fail: cleanup, ghi kết luận đủ căn cứ và blocker cụ thể, không tự sửa shared hoặc thử lượt05. Nếu đạt: review raw/source/config rồi publication đúng scope ZER-19 (commit/push/PR/CI/review/merge) và chấp nhận Done chỉ khi mọi gate WORKFLOW đạt. Giữ dirty ZER16/17/18/R3-G3/R4 queue/ZER48 và primary R; dùng allowlist, không git add tất cả, không mở issue tiếp.

Đề nghị Hoàng duyệt đúng một runtime-04 theo envelope trên và publication/Done có điều kiện. Quyền trước đã dùng hết và cấm tự retry; vì vậy cần duyệt riêng, không phải xin lại quyền cho bước nhỏ đã được duyệt.
