# ZER-46 — chẩn đoán clientA01 đã khép, 28/10/2026

**NOT_REPRODUCED_ONE_SAMPLE; KHÔNG LÀ AC PASS.** [Raw verification](raw-verification.json) và [acceptance](acceptance.json) đối chiếu đúng một dispatch/HTTP200/access join cùng PodUID. Cửa sổ234,89giây;0build/import/pull/writer/blockrule/TTL/replacement.

39mẫu guard không vi phạm; memory PSI some avg10 max0,12, hostAvailable min4.269.891.584byte, WSL min2.297.992KiB. Một request từ sourceA qua private ingress trả200, catalog safe oracle và logjoin đúngrequest/correlation/clientIP/trustedproxy. Đã chờ30giây sau response, không có request thứhai để warmup hoặc bù evidence.9Boutique scriptHTTP không đạt business probe; không health/KPI/end-to-end PASS.

## Phân biệt pha từ dữ liệu thực

- Dispatch tới interpreter marker≈0,47giây, gồm CLI/exec/startup; không quy hết cho Python.
- Interpreter→imports3,195s; delta memory some stall1.710µs, CPU throttled2.269.039µs, memory.events max/oom_kill0.
- Request ready→headers0,106s; delta memory stall0, CPU throttled94.511µs. Đọc body≈0,0003s.

Lượt này imports chịu CPU throttle nhưng không có memory stall lớn như08. Điều đó không chứng minh throttle là nguyên nhân PSI08, cũng không xác định một causal fix. Đây là một sample hoạt động; không kết luận lỗi gián đoạn đã hết và không cộng với partial07 thành PASS.

## Cleanup và toàn vẹn

Namespace UID05ed21d1-8292-49c9-a8bf-3bbd65987557 được xóa bằng precondition và xác nhận absent. Shared Deployment/PVC spec+UID, Pod UID/restart và3PVC giữ nguyên. Component resource cleanup CLEAN; aggregate driver in INCOMPLETE vì Boutique business không đạt, trạng thái gốc giữ nguyên. Không hostwriter/actor còn hoạt động của lượt này.

Approval operative fields/proposal hash/source-manifest hash đúng; snapshot32file khớp trước chạy. Runtime đọc file authorizationUTF8 bằng locale Windowscp1258 nên chữ tiếng Việt ở display reply bị mojibake. Original authority UTF8 và receipt sai được giữ nguyên; raw reconciler chứng minh mọi trường hành động/hash giống nhau. Không sửa raw hay dựng approval mới.

Sau khi lượt đã đóng, sửa explicit UTF8 reads và thêm regression tái lập cp1258,59/59offline đạt. Sáu file nguồn hiện tại khác snapshot do bản sửa encoding/test, được liệt kê trong raw-verification.json; manifest/proposal/approval đã tiêu thụ giữ nguyên. Candidate sau sửa không được quyền cũ cho chạy.

## Kết luận và bước tiếp theo

Gói sửa runner/verifier đã có [bàn giao59test](../gate-audit/runner-complete.md), còn thiếu review độc lập, full containment AC runtime trong một lượt hợp lệ và merge/Hoàng acceptance. Nguyên nhân PSI gián đoạn chưa xác định; full runtime vẫn NO_GO theo điểm dừng Hoàng yêu cầu. Đã tiêu thụ một quyền diagnostic; không tự retry hoặc chuyển sang runtime09. Bàn giao blocker/phần đã làm–chưa làm để quyết định tiếp theo dựa trên evidence, không đề nghị tiếp chuỗi thử may rủi.
