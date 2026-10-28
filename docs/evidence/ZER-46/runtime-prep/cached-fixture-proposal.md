# ZER-46 — dùng lại image đã build/import, khởi động tuần tự

**PROPOSED / NOT_APPROVED / NOT_RUN.** 28/10/2026. Runtime04 dừng đúng memory PSI15,02; không tự retry.
Không khẳng định một lượt sau chắc chắn đạt. AC/guard không giảm; không đề nghị sửa DNS/CPU/WSL/shared app.

## Căn cứ đã có

Runtime04 build/import fixture thành công. Cache đọc lại xác nhận host index
sha256:d85043c06db6a60c98cddb53a1545f6e053b6def409d43b156179a625df55274 và server-0 fixture config
sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16 (tag zer46-fixture:24662046a33f).
Proxy digest575fa15b… cũng có trên node. Không cần tạo lại artifact này. Chưa có bằng chứng duy nhất rằng
build/import hay một Pod riêng gây PSI; gói này bỏ phần chuẩn bị dư và giảm startup đồng thời.

## Gói đề nghị, một attempt

- Một cửa sổ≤20phút gồm5phút cleanup. **0 build,0 import,0 pull**. Kiểm lại SHA nguồn app/reader/seed/
  Dockerfile so với artifact04; verify host+node cache đúng hai image trước namespace creation. Cache
  thiếu/drift thì stop, không fallback sang build/import/download. Tất cả Pod imagePullPolicy=Never.
- Chỉ desktop-linux/k3d-zero-door;2node Ready, shared agent0, Boutique spec/replica/PVC baseline như trước.
  Preflight120s; host/WSL available≥1GiB, memory PSI avg10≤5, capture mỗi5s. Không nới guard, không tự kill
  ứng dụng/scale/restart Docker/WSL/node/cluster/shared workloads, đổi resource limits/DNS/Ingress/CNI.
- Namespace zd-sqli-lab chỉ create nếu absent, owner/UID mới. Apply static resources trước; proxy Ready
  rồi sourceA Ready, rồi sourceB Ready, cuối cùng fixture. Giữ đúng requests/limits/topology/IP+NAT+
  spoof/isolation controls của gói fixture-only đã duyệt. Không warm bằng tải.
- Giữ toàn bộ block sourceA403 / benign sourceB200+owned CRUD, một TTL180s, một Pod fixture replacement,
  một writer restart/read-only replay không gia hạn; expiry/unblock/API+mount cleanup+namespace UID delete.
  ≤120fixture+32Boutique scriptHTTP, concurrency1,≤2RPS,timeout3s,≤6TCPcontrols. Không SQLi payload/load/
  Kafka/model hoặc public target. Không commit/push/merge/LinearDone.
- Boutique vẫn observer trước/sau, timeout giữ nguyên, không chặn admission fixture và không thành PASS
  Boutique/R1/KPI/end-to-end. Fixture baseline/identity/isolation hoặc guard fail vẫn stop ngay; cleanup
  xong thì đóng attempt, không tự thử lần khác. Resource-clean và business/readiness verdict tách riêng.
- Nếu guard dừng khi owned Pod đang khởi động, chỉ đọc memory.current/max/events/pressure,cpu.stat theo
  đúng PodUID của attempt để chốt thiếu sót thực tế; không dump memory/env/token và không bypass stop.

Lỗi collector04 đọc log Deployment fixture chưa tạo sẽ được sửa bằng kiểm phase: ghi N/A khi chưa từng
attempt apply fixture, không sửa raw04. Namespace04 absent và shared/PVC preserved là proof resource
cleanup độc lập; verdict04 NOT_MET vì guard vẫn giữ. Gói mới cần duyệt riêng vì attempt trước đã đóng.
