# ZER-46 — một phép chẩn đoán client A, chưa được duyệt

**PROPOSED / NOT_APPROVED / NOT_RUN.** Đây không phải runtime09 nghiệm thu containment. Hoàng yêu cầu khép runner và gom nguyên nhân trước retry; không tự chạy bằng quyền08 đã tiêu thụ.

## Câu hỏi cần kết luận

Trong đúng profile cached-only trên agent-0, stall xuất hiện trước marker interpreter, trong imports/request setup, hay khi gửi/đọc một GET lành? Mốc client và delta memory PSI total / CPU throttled / memory.events giúp phân biệt các pha; đồng thời giữ global memory guard. Tương quan CPU/PSI không tự chứng minh nguyên nhân. Một mẫu không tái hiện không có nghĩa lỗi đã sửa.

## Phạm vi khóa

- HEAD9567830020954bf3f30fd5a74240747be0c8ec1c, context k3d-zero-door, Docker desktop-linux; đúng hai node hiện có, cả bốn workload riêng pin k3d-zero-door-agent-0.
- Một cửa sổ tối đa20phút, dành5phút cuối cleanup; preflight120s, giám sát mỗi5s; host/WSL available≥1GiB, memory PSI some avg10≤5. Dừng ngay khi guard/inventory/owner/cache fail. Không nới guard, tài nguyên hoặc probe timeout.
- Namespace zd-sqli-lab phải absent trước tạo; một lần tạo namespace/private topology17resource, proxy+A+B khởi động tuần tự, fixture phải có policy hook và Ready. UID/run owner phải khớp khi đọc/dọn.
- Chỉ đúng image cache04: fixture tag zer46-fixture:24662046a33f (host OCI d85043c…/node config d85cb46…), proxy digest575fa15b…; exact digests/code gate trong run_cached_fixture.py. **0build/import/pull** và Never.
- **Tối đa1fixtureHTTP**: từ source A, GET /fixture/catalog/search?category=electronics qua private ingress8000; expected200+safe catalog oracle+joined access log đúngPodUID. Không warmup/replay HTTP; không payload mới, SQLi executor, load, writer, block rule, TTL, TCP control hoặc Pod replacement.
- Giữ observer Boutique trước/sau theo component hiện có, tối đa32scriptHTTP tổng, tổng HTTP≤33; ≤2RPS/concurrency1. Observer không cấp formal R1/KPI/health/AC PASS. Không sửa shared CNI/DNS/frontend/Prometheus/WSL hoặc resource limits.
- Source A cgroup snapshot trước/sau bằng đọc node, chỉ UID thuộc lượt này; marker mỗi pha CLIENT đọc tối đa4096byte/file memory.current/max/high/events/pressure/cpu.stat. Nếu guard cắt, giữ partial stderr và snapshot owned cgroups của watchdog. Không đọc process memory/credentials. Sau một response hợp lệ quan sát30s, rồi cleanup.
- Cleanup dừng watchdog, kiểm log, xóa namespace bằng UID precondition và chờ absent; đối chiếu shared spec/UID/restart/3PVC; không có host writer. Mọi thiếu/unknown/error được giữ và chặn verdict thuận lợi. Không xóa namespace lạ.

## Cấu hình và lệnh sau khi có quyền

Entrypoint Bash: client-diagnostic.sh --execute trong thư mục này; script đòi client-diagnostic-authorization.json APPROVED với hash proposal và client-diagnostic-source-manifest.json. File approval chưa được tạo. Một attempt duy nhất; started/acceptance hiện hữu chặn replay. Mọi source/config lệch hash chặn trước tạo Lab/actor. Output riêng docs/evidence/ZER-46/client-diagnostic-01/; không ghi raw01–08.

## Tiêu chí kết luận và điểm dừng

1. Giữ đúng một dispatch/HTTP result hoặc UNKNOWN; report stage durations/counter delta, Pod UID, resource samples và cleanup. Không tạo request để bù log thiếu.
2. Guard/cancellation/missing marker/counter/join → STOP_OR_INCONCLUSIVE, dừng; phân tích artifact này offline, không tự retry hoặc chạy containment.
3. Đủ marker/counter/join/guard/cleanup → NOT_REPRODUCED_ONE_SAMPLE; chỉ chứng minh sample này hoạt động. root_cause_proven=false, AC/pass/Done=false.
4. Chỉ sau khi phân tích xong và có bản sửa đúng nguyên nhân, cộng timing thực đo cho lịch TTL160s+15s reserve (5s overhead ban đầu; hạn thực tế luôn chặn theo expiry gốc), mới xem xét gói nghiệm thu đầy đủ riêng. Không tự chuyển chẩn đoán thành quyền runtime09. Nếu thiếu căn cứ/lab không đáp ứng, báo blocker cuối cùng và phần đã làm/chưa làm để Hoàng quyết định phạm vi; không mở chuỗi lượt thử may rủi.
