# ZER-46 — một lượt cached-only trên node agent đã kiểm rule

**PROPOSED / NOT_APPROVED / NOT_RUN — 28/10/2026.** Không tái sử dụng quyền runtime05 đã kết thúc.

Mục tiêu: chứng minh trọn component block IP/benign/TTL/restart/cleanup theo AC-01/02, không tạo payload, không chạy SQLi executor hoặc LLM. [Evidence nền](../gate-audit/README.md): server-0 thiếu firewall Pod, có dấu hiệu stale node IP lúc khởi động; agent-0 có hook18Pod hiện hữu và đúng cache. Không cần recovery server dùng chung để kiểm component riêng.

## Phạm vi một attempt

- Chỉ Docker context desktop-linux, Kubernetes k3d-zero-door, namespace zd-sqli-lab mới nếu absent. **Thay đổi so với runtime05: cả 4 workload riêng đặt trên k3d-zero-door-agent-0**, gate/cache/cgroup đọc đúng node này. Không chuyển hoặc sửa workload dùng chung.
- ≤20 phút tính cả preflight và **5 phút dành cleanup**. Chỉ một attempt; dừng thì đóng, không tự retry. Preflight pressure120giây, host/WSL available≥1GiB và memory PSI avg10≤5; watcher mỗi5giây, giữ kiểm shared spec/UID/restart/PVC và private restart. Không nới guard.
- **0 build/import/pull**; đúng tag zer46-fixture:24662046a33f, host index sha256:d85043c06db6a60c98cddb53a1545f6e053b6def409d43b156179a625df55274; node config sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16. Proxy digest sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c. Mọi imagePullPolicy=Never; cache/source drift thì stop, không fallback.
- Đọc hook một Pod hiện hữu trên agent trước tạo namespace. Khởi động static→proxy Ready→source A Ready→source B Ready→fixture. Fixture không mở app trước hook đúng Pod/IP/namespace/FORWARD/REJECT; giữ gate tương tự sau replacement. Không bỏ isolation vì đổi node.
- Chỉ safe fixture, HTTP catalog/owned CRUD lành tính: **≤120fixture +32Boutique HTTP, concurrency1,≤2RPS, timeout3giây,≤6TCP negative controls**. Hai nguồn IP/benign/proxy lấy mới, exact proxy/32, anti-spoof giữ nguyên.
- Một block nguồn A403, nguồn B200+owned CRUD; **một TTL180giây, một fixture Pod replacement, một writer restart/read-only replay không gia hạn**; quan sát expiry/unblock, API+mount cleanup, xóa namespace bằng UID và read-back absent. API accepted không là containment PASS.
- Boutique observer trước/sau, giữ timeout/failure; không chặn admission component khi lỗi nền, không claim Boutique/R1/KPI/end-to-end PASS. Cleanup nguồn riêng và health nền có verdict riêng. Giữ production executor/consumer disabled.
- Không restart Docker/WSL/node/shared app, không sửa CNI/DNS/CPU/limits/Ingress/Prometheus, không model/cloud/external target/Git publication/LinearDone. Khi guard dừng chỉ đọc cgroup của owned Pod UID đã biết, không tạo actor mới.

Harness offline31cases đạt; parser đối chiếu snapshot18Pod có hook thực. Image app/reader/Dockerfile/seed giữ hash của artifact04. Chuỗi component chưa chạy trên agent, nên không bảo đảm lần này PASS. Duyệt gói này chỉ cho attempt trên, không cho recovery hạ tầng nếu gate mới fail.
