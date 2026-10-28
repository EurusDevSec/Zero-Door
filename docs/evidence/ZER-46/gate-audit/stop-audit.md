# ZER-46 — kết luận audit sau lượt08

28/10/2026. **NO_GO cho lượt runtime tiếp theo.** Gói audit offline đã hoàn tất; ba lỗi runner được sửa và kiểm. Đây chưa phải bản sửa hoàn chỉnh nguyên nhân lab, chưa là AC PASS hoặc sẵn sàng publication. Không chuẩn bị, duyệt hay chạy lượt09.

## 1. Khép lượt08

Đối chiếu lại toàn bộ raw bằng reconcile_runtime08_stop.py, chặn ghi output và chặn subprocess: kết quả đúng bằng receipt đã lưu; không ghi lại artifact runtime08. Namespace UID 096728fe-7e47-497b-bf01-bb2a8043a548 đã xóa và đọc lại absent trong lượt08; shared spec/UID/restart/3PVC giữ nguyên, không writer được khởi động. Đây là xác minh từ evidence đã thu, không phải một phép đo live mới.

Raw runtime-08/raw/0070.json ghi dispatch remote exec từ zer46-source-a lúc1793165099.8488665 để thực hiện GET /fixture/catalog/search?category=electronics; correlation e29ae6606f7c46a0b0ebbf9c4bb16408. Guard hủy lệnh, raw không có response/exit receipt; log fixture đã thu không có correlation này. **HTTP UNKNOWN**: biết client exec đã dispatch; không biết request HTTP đã được gửi tới đâu hoặc đã trả gì. Không ghi “0 request sent” hoặc “request thất bại chức năng”. Counter fixture=1 là admission, không là response count.15 Boutique script HTTP là observer, không KPI/R1 PASS.

## 2. Phân loại nguyên nhân

| Lớp | Điều đã xác minh | Kết luận / giới hạn |
| --- | --- | --- |
| Collector06 | docker top thiếu trường PID; sửa pid,args có read-back thành công | Lỗi chuẩn bị của Codex; không phải lỗi containment |
| Collector07 | logs Deployment chọn Pod cũ, request16 HTTP403 thiếu join | Pod/UID collector đã sửa và kiểm mock; partial trước replacement giữ riêng |
| Tài nguyên08 | PSI16,37 >5; sourceA snapshot48,64, ba Pod khác0; host3,29GiB/WSL2,23GiB; không OOM/max event | Dừng guard đúng. Chưa chứng minh CPU, dung lượng RAM, import Python, filesystem hay remote exec là nguyên nhân gốc; snapshot sau stop không thay delta trước/sau |
| Chức năng |07 có block A403, benign B200+CRUD trước replacement;08 chưa tới writer/rule | Không có bằng chứng08 làm sai block/TTL; cũng chưa đủ bằng chứng chức năng đạt đầy đủ |
| Thiết kế phép thử | source Pod chỉ sleep900 và Ready; CLIENT import urllib/khởi tạo opener trước begin timestamp; preflight đo lúc client còn chưa chạy | Ready hiện tại không chứng minh client sẵn sàng làm request.35 test cũ không kiểm độ sẵn sàng tài nguyên này |

Không cộng partial07 và08 thành một lượt PASS. Không yêu cầu Hoàng giải phóng thêm RAM từ dữ liệu hiện có.

## 3. Phạm vi audit và sửa gom

HEAD9567830020954bf3f30fd5a74240747be0c8ec1c, branch zer-42-bounded-sqli; Codex là writer. Đọc toàn bộ chuỗi entrypoint08 → agent → cached → fixture-only → component → preflight; renderer, writer RPC, full verifier và stopped08 verifier; đọc năm suite cũ, TTL writer/reader và đoạn HTTP/log trực tiếp liên quan. Source/hash trong stop-audit-verification.json. GitNexus context incomplete-in-progress, FTS missing, index27/10: dùng source trực tiếp, không refresh index gây thêm áp lực. Đây là self-audit có kiểm độc lập từ raw, chưa là review bởi người/agent khác; không audit lại toàn production pipeline.

| Finding | Vị trí | Sửa / kiểm |
| --- | --- | --- |
| P1 — mất output lúc cancel | run_component.py, Lab.command | Giữ partial stdout/stderr, PID, returncode nếu biết, cancelled và ended_at; redaction ở cả hai stream. Không biến partial bytes thành HTTP success |
| P1 — lỗi stop writer ngăn cleanup | run_component.py, Lab.cleanup | Ghi lỗi dừng writer nhưng vẫn thực hiện UID-pinned namespace delete và giữ final receipt; lỗi writer vẫn làm cleanup INCOMPLETE |
| P1 — guard đến muộn bị bỏ sót ở terminal verdict | run_component.py/main và run_fixture_only.py/main | Sau cleanup, failure list của watchdog luôn veto thành NOT_MET; lưu guard history. Không dùng validated đơn lẻ để kết luận |

Ba regression tái hiện trước sửa:3 failures +1 error trên3 test methods (guard có hai entrypoint). Sau sửa, **38/38 offline** =12+5+5+9+4+3; Popen/run/HTTP bị mock, không Docker/kubectl/lab. Bandit không finding tại ngưỡng high severity/high confidence; không nói mọi mức đều0. Logs stop-audit-*.log. App/backend/image/guard/TTL không đổi. Các file raw/scripts/approval của01–08 giữ nguyên; manifest08 đã tiêu thụ không được sửa để cấp quyền cho code mới.

## 4. Những điểm còn chặn GO

1. **Nguyên nhân memory stall chưa xác định.** Cần một giả thuyết có phép phân biệt rõ và cách đo mốc client-start/import-ready/DNS-connect/request/response cùng cgroup counter delta. Hiện không có trace đủ để chọn thay đổi resource hoặc khẳng định thay client sẽ sửa được. Sửa ba lỗi runner trên không phải bằng chứng sửa PSI. Không mở containment attempt để “thử xem”.
2. **Ngân sách theo pha chưa đủ cho TTL/restart.** Sau tạo rule180s, runner cho projection90s + old-Pod-absent45s + release115s, đã250s trước overhead HTTP/log/writer. Đây là cận chờ cấu hình, không phải latency thực đo; đường nhanh có thể đạt nhưng chưa có admission theo thời gian TTL còn lại. Trước GO phải khóa lịch pha khả thi, fail sớm nếu thiếu thời gian, giữ expiry gốc/không renew/nới TTL để làm đẹp. Cleanup projection45s cũng chưa có bằng chứng đủ trên lab này; phải đưa vào cùng ngân sách cleanup300s.
3. **Full verifier chưa đủ để tự kết luận toàn chuỗi.** reconcile_completed_protocol.py kiểm raw/hashes/status/IP/replay/expiry nhưng chưa veto rõ failure history và chưa yêu cầu receipt xác nhận actual RPC writer PID đã thoát. stop_worker quản lý Popen launcher;07 đã chứng minh launcher và RPC PID khác nhau. Sửa terminal verdict mới không tự nâng verifier cũ thành đầy đủ. Cần đóng các kiểm này và kiểm tình huống thiếu/sai dữ liệu trước mọi lượt mới. Collector ghim Pod/UID vẫn cần bounded read-back khi record đến trễ; không replay HTTP để lấy log cho đẹp.

Ba mục được gom thành **một điều kiện Ready**, không thành ba lượt chạy/ba lần hỏi. Các nguy cơ theo thời gian và verifier chưa chứng minh đã gây08; chúng là khoảng trống nhìn thấy khi audit phần chưa được thực thi, phải xử lý trước khi dùng phần đó để nghiệm thu.

## 5. Điểm dừng và quyết định

**Đã làm:** enforcement/TTL source và offline checks; immutable image; partial07; cleanup08; audit runner và ba sửa có fail-before/retest. **Chưa làm đủ:** block/benign/attribution sau replacement có đầy đủ trace, writer restart/replay, expiry/unblock, policy API+mount cleanup trong một lượt hợp lệ; independent review, merge và Hoàng acceptance. Production end-to-end/LLM/KPI không được suy từ gói này.

Chỉ GO khi có một bản sửa gom xử lý nguyên nhân đã xác định, kiểm fail-before/fix-after, source/image/config hash khóa mới, protocol tái lập đủ TTL/cleanup, verifier từ chối mọi failure/UNKNOWN/missing và quyền runtime phù hợp. Đạt mock không thay xác minh lab; chưa đáp ứng thì NO_GO, không gói retry theo số thứ tự.

Quyết định kỹ thuật hiện tại: **giữ ZER-46 ở blocker nghiệm thu, dừng các lượt runtime.** Chưa đủ căn cứ kết luận máy không thể chạy SQLi; đủ căn cứ kết luận profile/runner hiện tại chưa sẵn sàng để tiêu thêm một attempt. Nếu điều kiện lab không thể được chứng minh trong thời gian còn lại, bàn giao source + partial evidence + giới hạn này để Hoàng quyết định điều chỉnh cam kết/phạm vi; không tự bỏ AC hoặc đổi thành Done. Không mở lại ZER-43, không sửa hạ tầng dùng chung hoặc chọn issue khác từ audit này.
