# Phép đo và kiểm chứng

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Kiểm chứng và thiết kế thực nghiệm

Các tiêu chí hoàn thành là điều kiện phải kiểm tra, chưa phải kết quả đã đạt:

1. **Đường đo thật:** attack có hiệu lực; Gaia tự ghi detect; Kafka chuyển đúng ID; healer xử lý; probe xác nhận recovery. Inject alert chỉ dành unit/integration test của healer và đánh dấu riêng, không nằm trong bộ dữ liệu chính.
2. **Thời gian:** lưu attack_effect_started, detected, published/consumed, heal_started, action_completed, recovery_verified và attack_stopped. Báo MTTD từ effect đến detect, MTTR từ detect đến recovery, thêm total recovery từ effect. Không đổi định nghĩa sau khi thấy kết quả.
3. **KPI:** báo cả tỉ lệ MTTR dưới 120s và 180s vì thuyết minh dùng khoảng 2–3 phút; mục tiêu MTTD <60s, uptime ≥99,9%. Khóa mẫu số lượt sự cố đủ điều kiện trước formal run; timeout/không recovery không tính đạt ngưỡng, missing báo riêng và không tự tính pass. Phân phối MTTR của lượt recovered phải đi cùng tỷ lệ recovery/failure trên tổng lượt để không che thất bại. Chốt threshold đánh giá trước formal run; mọi case chưa đạt được ghi đủ.
4. **Availability:** client độc lập đo phản hồi đúng nội dung và latency cho route/giao dịch đã định; tách time-based availability và request success rate. Chọn cửa sổ warmup/trial/recovery trước khi chạy. Không dùng scrape `up`, thiếu dữ liệu hoặc API patch để suy ra phục hồi.
5. **Downtime budget:** nếu dùng War Game 4h theo kế hoạch repo, uptime 99,9% theo thời gian chỉ cho 14,4s downtime. Cần replicas khỏe phục vụ trong lúc recovery; kiểm tra resource quota/scheduling và budget của máy trước khi tăng replicas.
6. **Đối chứng:** giữ tự phục hồi Kubernetes trong mọi nhóm. Tối thiểu B0 Kubernetes/controller, B1 RULES và B2 MULTI_LLM chạy cùng workload/fault; B1/B2 dùng cùng pipeline/evidence/guard/probe. Profile HPA và quyền scale được cố định/ghi rõ ở mỗi nhóm để quy đúng đóng góp. B3 SINGLE_LLM bắt buộc nếu kết luận lợi ích chia vai trò vận hành; không chạy B3 thì giới hạn claim. Giữ BM manual thật theo protocol/cam kết hiện có và khi kết luận tốt hơn thủ công; lưu alert/thao tác/recovery, tắt mọi auto-heal của ZERO DOOR. Nemesis/harness replay kế hoạch chung, không cấp đáp án cho bên chữa lỗi.
7. **Chất lượng AI:** đánh giá schema validity, action đầu tiên đúng/sai/thừa, phục hồi xác minh trên tổng lượt sự cố, latency, token/call/cost, fallback/refusal và đề xuất bị guard chặn. Khóa mẫu số/ground truth trước formal run, giữ timeout/failure; JSON đúng không tự là hành động chữa lỗi đúng. Lưu model/version/prompt/temperature và evidence không lộ đáp án; không trình bày chat tổng hợp như log quyết định thật. Chỉ kết luận ưu thế LLM/phối hợp khi có nhóm đối chứng và độ bất định tương ứng.
8. **Mẫu và thống kê:** pilot vài lượt mỗi case để xác định độ biến thiên; khóa số lặp formal trước khi đo. Dùng thứ tự xen kẽ/ghép cặp workload hợp lý, reset có xác nhận và cùng budget. Báo mean/median/distribution/confidence, đủ failure/timeout. P95/P99 từ mẫu nhỏ chỉ là thăm dò, không khẳng định ổn định.
9. **Normal windows:** có tải lành tính để đo false alarms và tác động lên người dùng hợp lệ; định nghĩa nhãn và mẫu số FPR. Không hardcode 0 hoặc chia FP cho số tấn công mà gọi là FPR.
10. **Reproducibility:** khóa image/config/dependencies; dataset mới lưu riêng theo method version và run ID. Dùng dataset manifest/hash để chọn đầu vào analysis, tách legacy/pilot/formal; các lượt bị loại có lý do theo protocol và vẫn được lưu/thống kê. Giữ nguyên raw CSV cũ, ghi giới hạn như dữ liệu chẩn đoán lịch sử; timestamp trong CSV không tự chứng minh ngày chạy độc lập, không trộn legacy với formal.

### Các test hành vi ưu tiên

| Tình huống | Kết quả phải kiểm chứng |
| --- | --- |
| LLM output sai schema, service ngoài allowlist, tham số vượt budget | Bị từ chối trước thao tác; có event lỗi; không gọi shell/K8s ngoài phạm vi |
| LLM timeout/429 hoặc mất mạng | Timeout/retry hữu hạn; fallback rõ hoặc skip; không treo consumer, không giả ghi AI thành công |
| Thiếu Prometheus/Elasticsearch/probe series | Health suy giảm/missing; không báo 100% uptime hoặc false success |
| Action FAILED/PARTIAL hoặc timeout trong khi probe vẫn lỗi | Không tạo RECOVERY_VERIFIED hoặc MTTR thành công; failure/censored và mẫu số được xuất đúng; các mốc polling không thay timestamp detector |
| Alert/command bị gửi trùng | Không nhân đôi attack/heal ngoài phiên cho phép; event vẫn truy nguyên được |
| Restart nhiều replicas | Không lấy pod cũ đang Ready làm bằng chứng pod thay thế; nghiệp vụ được kiểm tra |
| Deploy bản lỗi và rollback | Template/image/config thực trở lại release tốt; giao dịch phục hồi trong cửa sổ định trước |
| Chặn attacker và chạy benign client | Attacker bị chặn; benign traffic tiếp tục; TTL/cleanup sau restart được xử lý |
| Attack bị hủy hoặc worker dừng | Tải/fault còn lại được cleanup; không để pod stress/policy tồn dư không ghi nhận |
| Hai vector đồng thời và HPA/healer | Giới hạn tải tổng, quyền scale rõ, không bão lệnh hoặc cooldown làm mất toàn bộ phục hồi |
