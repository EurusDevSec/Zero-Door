# ZER-19 — sửa runner sau điều tra runtime-02

**OFFLINE_FIX_VERIFIED — 30 kiểm thử đạt; chưa xác minh lại lab, chưa Done.**

Hoàng yêu cầu khắc phục theo [điều tra](../investigation/README.md). Chỉ sửa runtime-prep/run.py và check_runner.py; chín file sản phẩm Nemesis/CI giữ nguyên. HEAD 093e924000861da3096185427994d9ea736df36d, branch codex/zer-19-nemesis-session; một writer. Không có call model, HTTP/TCP fixture, thao tác Docker/Kubernetes, build/pull/import hoặc publication trong gói sửa này.

## Đã sửa và đã kiểm

| Thiếu sót đã xác định | Thay đổi | Kiểm offline |
|---|---|---|
| Timeout/cancel thiếu elapsed, exit và output sau kill | Receipt ghi timeout, elapsed, reason, trạng thái spawn/kill/reap, returncode và output đã thu. Cleanup lỗi không che nguyên nhân ban đầu. Client bị kill vẫn không kết luận thao tác từ xa thất bại: remote_outcome giữ UNKNOWN. | Child Python local: timeout, stop, nonzero được phép, spawn lỗi, cleanup mắc kẹt; không Docker/kubectl. |
| Output sau lỗi có thể echo stdin Secret | Không ghi stdin; che toàn bộ stdout/stderr của lệnh được cung cấp stdin, kể cả nhánh timeout. Caller vẫn nhận output thực trong bộ nhớ. | Sentinel secret không xuất hiện trong receipt của success/failure/timeout. |
| Mẫu guard chỉ có memory PSI | Thêm CPU/IO PSI trong cùng một Docker exec/cat, thu avg10/60/300 và total. Parse đúng format đã lưu từ lab; thiếu/malformed thì fail-closed. | Replay format thật từ evidence; dữ liệu thiếu/sai bị chặn. CPU/IO cao không tự thêm gate. |
| Preflight không phát hiện shared restart trong cửa sổ kiểm | Sau 25 mẫu/120 giây hiện có, đọc lại inventory và so shared UID/spec/restart trước khi tạo namespace/fixture. API timeout hoặc drift → NO_GO, không khởi động watcher/fixture. | Shared restart, thay Pod UID, đổi spec và timeout API đều bị chặn; steady path vẫn READY_NOT_ISSUE_PASS. |

Giữ nguyên **timeout lấy mẫu 4 giây, nhịp 5 giây, Windows/WSL available RAM ≥1GiB, memory PSI avg10 ≤5, work/cleanup deadline, fail-closed, cache-only, ownership và AC**. Snapshot cuối dùng cùng wrapper kubectl context k3d-zero-door/request-timeout=8s và deadline command hiện có. Watchdog vẫn chạy qua setup; preflight sạch không bảo đảm không có spike khi khởi động workload.

[Log cuối](offline-tests.log): 30/30 test đạt trong 4.381 giây. Test boundary chặn mọi native external client trước spawn; chỉ cho phép child Python local của các case process. Chạy default runner trả PLAN_ONLY/0 call/0 mutation; Bash syntax và git diff --check đạt; Git index trống. 15 test cũ +15 test mới, không cộng vào runtime proof.

## Review và bảo toàn bằng chứng

Self-review toàn bộ delta command/resources/preflight và consumer trực tiếp (watch/prepare/harvest/cleanup) không thấy lỗi chặn sau retest. Đây **không phải review độc lập mới**; review sản phẩm trước đó vẫn áp dụng cho chín pin sản phẩm không đổi. [Patch](delta.patch) và [verification](verification.json) khóa source/test cụ thể.

216 artifact của gói điều tra được đối chiếu; chỉ hai helper và prefix README của gói hiện hành thay đổi có chủ đích. Runtime-01/02 raw, kết luận, authorization, source-manifest-at-invocation và evidence điều tra giữ byte nguyên. Bản helper cũ được lưu before-run.py.txt/before-check_runner.py.txt để đối chiếu pin lịch sử. 26 pin lúc invocation runtime-02 vẫn mô tả **revision cũ**, không ghi đè chúng để che hai helper hiện đã đổi. Analyzer lịch sử đã chứng minh 26 pin ở thời điểm điều tra; không dùng assertion “current source unchanged” của nó như kiểm cho revision mới.

Giữ source-manifest cũ và hai authorization đã tiêu thụ; không mở lựa chọn runtime-03 hoặc làm quyền cũ dùng lại được. Gói này chưa chuẩn bị admission cho lượt mới. Không stage/commit/push/merge/Linear write; các checkpoint cũ của issue note/NOW được giữ nguyên dưới prefix mới.

## Còn thiếu trước khi kết luận issue

Đây là sửa thiếu sót runner và từ chối sớm lab đang drift; **chưa phải sửa đã chứng minh cho đợt stall Docker/K3s toàn VM**. Tác nhân khởi phát vẫn chưa rõ; không có căn cứ đổi shared CPU/WSL hoặc tăng timeout để che sự cố. Runtime-02 tiếp tục NOT_MET / cleanup INCOMPLETE do shared restart, tài nguyên riêng đã được xác minh xóa ở evidence cũ.

Bước kế tiếp là review delta và một proposal/admission có pin mới cho đúng một lượt nghiệm thu; quyền mới phải có trước khi thực thi vì gói đã duyệt trước ghi rõ không tự chạy03 nếu fail. Giữ nguyên envelope và guard; nếu stall tái diễn thì thu receipt mới rồi dừng, không tự retry hoặc gọi đó là PASS. Chưa có runtime-03, inference thật ZER-19, publication hay Done từ gói này.
