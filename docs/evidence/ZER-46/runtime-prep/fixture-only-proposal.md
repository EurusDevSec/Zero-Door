# ZER-46 — quyết định cần chốt: kiểm component fixture độc lập với Boutique đang lỗi

**PROPOSED / NOT_APPROVED / NOT_RUN.** 28/10/2026. Runtime03 đã kết thúc, không tự chạy lại.

## Vì sao cần đổi prerequisite của gói

AC-01/02 của ZER-46/ZER-17 nói chặn nguồn SQLi tại fixture, giữ source benign, TTL/restart/cleanup. SCOPE28/10
yêu cầu báo availability của fixture và Boutique riêng. Gói trước do Codex soạn lại bắt full purchase
Boutique khỏe trước khi thử component trong namespace khác. Runtime03 cho thấy Boutique home timeout3s,
rồi product/checkout timeout trong readback, dù RAM/PSI đạt và chưa triển khai fixture. Giữ prerequisite
này sẽ quay về blocker cũ của ZER-43; không có bằng chứng fault mới hay lỗi BLOCK_IP.

Đề xuất chỉ tách **gate component**: baseline protected fixture/sourceA+B phải khỏe và đủ IP/anti-spoof/
isolation controls trước block. Boutique vẫn được probe trước/sau và báo trạng thái thật, nhưng việc nó
đã lỗi từ trước không chặn component fixture. Không tuyên bố Boutique hồi phục, không kết luận ảnh hưởng
không tăng khi dữ liệu không đủ, không coi component là PASS end-to-end/R1 hay hoàn tất đề tài.

## Giữ đủ AC, không giảm tiêu chí

- Fresh node/controller args, Pod labels/UID, exact private proxy /32, hai IP nguồn phân biệt; direct TCP
  tới fixture bị từ chối và forged XFF không thay danh tính. Không thay CNI/route/source defaults.
- SourceA thực sự403 với action/policy hash trong access log; sourceB cùng proxy200 + owned CRUD/delete
  hậu kiểm. Một rule TTL180s, một lần thay Pod fixture, một writer restart/read-only replay không gia hạn.
  Sau expiry A/B200 và owned CRUD, policy API+mount+rỗng, cleanup UID-conditioned namespace absent.
- Guard host/WSL available≥1GiB và PSI≤5, preflight120s, capture mỗi5s. Fail fixture baseline/identity/
  isolation/guard/ownership/budget thì stop và cleanup, không cố lấy PASS.
- Một attempt≤20phút gồm5phút cleanup, một build/import fixture, cached exact base/proxy đã pull ở03;
  không pull mới.≤120fixture+32Boutique scriptHTTP, concurrency1,≤2RPS, timeout3s;≤6directTCPcontrols.
  Chỉ request lành tính, không SQLi/load/Kafka/model. Không restart/scale shared app/node/cluster/WSL,
  đổi DNS/CPU/resources/Prometheus/CNI/Ingress; không Git publication.

## Cách ghi verdict

Từng AC của component chỉ có PASS sau raw reconciliation đủ; giữ Boutique NOT_HEALTHY/UNKNOWN và giới
hạn ảnh hưởng tách riêng. Resource cleanup chỉ CLEAN khi actors/policy/namespace/tunnels do attempt tạo
đã hết và shared spec/restart/ba PVC giữ nguyên; business readback Boutique thất bại vẫn INCOMPLETE cho
lab readiness. Không sửa R1 healthy/KPI threshold, không ghi uptime/recovery của Boutique đạt, không tự
Done hay mở issue bổ sung. Review/merge/Hoàng acceptance theo workflow vẫn cần.

Nếu Hoàng chọn sửa Boutique trước, không chạy gói này; cần gói chẩn đoán/sửa nền cụ thể riêng thay vì
thêm một lần retry baseline hiện tại. Tài liệu này không tự cấp quyền bỏ gate của approval trước.
