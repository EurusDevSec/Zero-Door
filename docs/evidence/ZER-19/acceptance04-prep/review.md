# Review chuẩn bị runtime-04 — 29/10/2026

Không có finding chặn trong delta đã kiểm. **READY_TO_REQUEST_SINGLE_ATTEMPT_APPROVAL**, không phải runtime PASS.

Target: HEAD093e924000861da3096185427994d9ea736df36d/branch codex/zer-19-nemesis-session, local untracked helper changes so với bytes đã review ở acceptance04-prep/before-run.py.txt và before-check_runner.py.txt. Pin runner 1f6e6d726d09e1bbd361dc6b48997721d8656dce4131d71c497b84e215812a8a; checks 6b841783ed950a9bfebd8a3238781583bdf76a098ffea4407eb4c8987c0965a3; source manifest ff24b9463bc4302b19fd951136b30ca2d50a0ee0a3ac2da8fa486ba5eb9524ef; proposal af59bcbde66316553b1b700210d8692d4f6189ed6b6f6b0017e80f75c5d713b2.

Review kết hợp một domain: admission/quyền và snapshot NetworkPolicy, caller main→preflight→prepare, watcher/command timeout/cleanup, Python contract, tests, docs và mức sửa vừa đủ. Không đổi 9 source sản phẩm/config/image/payload/executor/guardthreshold. Không thêm dependency hoặc cơ chế restart; reuse command/get/save hiện có.

44 test offline đạt, gồm case map đúng, map sai node giống lỗi quan sát, missing/foreign/empty map, IP lệch, timeout; gate chạy trước namespace và trong lúc watcher hoạt động. Admission thiếu/sai approval/source hoặc prior ngân sách/cleanup không an toàn đều bị chặn; marker cũ chặn replay. Native kubectl/docker/Kafka/model bị chặn trước spawn trong test. CLI plan-only và Bash syntax/git diff check đạt. Không kiểm live hay diễn giải mock là enforcement proof.

Gate mới chỉ so inventory và firewall comment map trên cả2 node với Docker/Kube IP, không chứng minh controller sẽ không lệch lại; gate fixture UID/IP và TCP denial/HTTP before-after vẫn bắt buộc. Snapshot saved Claude chỉ là evidence ở các mốc đã ghi; lần mới lấy baseline sau sửa và vẫn phải qua 120s guard. Lỗi/timeout/UNKNOWN giữ NOT_MET, không tự thử05 hoặc restart node.

GitNexus context/impact không tìm thấy helper, detect_changes không cover untracked helper, PDG unresolved và primary index cũ/FTS thiếu. Không refresh nặng theo issue note; taint/PDG coverage bỏ qua vì thiếu index phù hợp, đã đọc trực tiếp diff/caller/argument lists/test. Không dùng zero hits làm proof safety. Review delta này là Codex tự kiểm; review độc lập raw/source trước publication vẫn giữ trong proposal.

Claude repair: audit snapshot/checksum tại repair-audit.json xác nhận 9 hashes, IP mismatch trước sửa và map đủ sau sửa, UID3PVC/26workload giữ nguyên. Không khẳng định biết nội bộ k3s lấy IP cũ từ đâu, mọi policy từng không được enforced hoặc restart sẽ ngăn tái diễn vĩnh viễn.
