# ZER-46 runtime08 — sửa collector theo Pod/UID, giữ nguyên giới hạn

**PROPOSED / NOT_APPROVED / NOT_RUN — 28/10/2026.** Lượt07 đã đóng; quyền trước chỉ cho một attempt.

## Căn cứ

Runtime07 có16 request fixture và15 access-log joins. NguồnA bị403 đúng action; nguồnB vẫn200 và CRUD đạt trước khi thay Pod. Sau replacement, HTTP16 trả403 nhưng collector deployment tự chọn Pod cũ khi còn hai Pod, gây ACCESS_JOIN. Chưa kiểm được writer restart, expiry và gỡ chặn; không coi checkpoint này là PASS. Namespace đã xóa đúng UID, shared spec/restart/3PVC giữ nguyên, cả PID launcher và writer thực đã thoát. Raw07 giữ nguyên.

Codex đã sửa collector ghim tên Pod+UID+owner+node; đợi Pod cũ absent với UID pin trong≤45giây trước hậu restart, không force-delete.35 kiểm thử harness offline đạt, gồm hai Pod cùng tồn tại, UID drift, already absent và timeout. Đã rà collector cleanup; không sửa app, writer backend hoặc image. Mock đạt không bảo đảm runtime PASS.

## Một attempt đề nghị

- Chỉ Docker desktop-linux / Kubernetes k3d-zero-door. Tạo namespace zd-sqli-lab nếu absent; cả4 workload riêng trên k3d-zero-door-agent-0. **Tối đa20phút, gồm5phút dành cleanup; không tự retry.**
- Preflight120giây; host/WSL available≥1GiB, memory PSI avg10≤5; watcher mỗi5giây. Giữ guard về shared spec/UID/restart/PVC và private restart. Guard/baseline/identity/isolation fail thì stop và cleanup.
- **0 build/import/pull**, mọi imagePullPolicy=Never. Fixture tag zer46-fixture:24662046a33f; host index sha256:d85043c06db6a60c98cddb53a1545f6e053b6def409d43b156179a625df55274; node config sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16. Proxy digest sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c. Cache/source drift thì stop.
- Khởi động tuần tự static→proxy→sourceA→sourceB→fixture. Giữ kiểm hook hiện hữu trước namespace creation, hook đúng Pod/IP/namespace/FORWARD/REJECT trước release app và sau replacement; exact proxy/32, header trust, spoof và TCP controls giữ nguyên.
- **≤120 fixture +32 Boutique script HTTP;≤2RPS, concurrency1, timeout3giây;≤6 TCP controls.** Chỉ safe fixture và catalog/owned CRUD lành tính. Không payload, SQLi executor, load, Kafka, model hoặc external target.
- Chứng minh A403/B200+CRUD; **một TTL180giây, một fixture Pod replacement, một writer restart/read-only replay không gia hạn**. Kiểm expiry/unblock, policy API+mount cleanup, namespace UID delete+absent và các PID writer thoát. Không bỏ trace join hoặc đổi TTL để PASS.
- Boutique vẫn observer trước/sau; giữ timeout/failure và báo health riêng, không claim R1/KPI/end-to-end PASS. Production executor/consumer vẫn disabled.
- Không restart Docker/WSL/node/shared workload; không sửa CNI/DNS/CPU/limits/Ingress/Prometheus, cloud/model/Git publication/Linear Done. Không mở lượt khác hoặc recovery hạ tầng nếu thất bại.

Entrypoint Bash run_agent_retry.sh trỏ receipt, authorization và source manifest riêng08; kiểm hash trước execute, không ghi đè07. Quyền mới chỉ dành một attempt trong giới hạn trên.
