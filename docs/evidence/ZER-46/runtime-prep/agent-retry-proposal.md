# ZER-46 runtime07 — tiếp tục chuỗi component sau sửa collector

**PROPOSED / NOT_APPROVED / NOT_RUN — 28/10/2026.** Runtime06 đã kết thúc, không dùng lại quyền một attempt.

## Căn cứ và thay đổi duy nhất về hành vi

Runtime06 chứng minh cache/no-pull, pressure guard, node admission, hook firewall đúng Pod/IP và fixture Ready trên agent-0. Dừng trước fixtureHTTP vì collector docker top -eo args thiếu PID. Lỗi thuộc harness do Codex để sót; không phải block/TTL fail. [Raw reconciliation](../runtime-06/independent-verification.json) xác nhận cleanup riêng CLEAN, shared spec/UID/restart/3PVC nguyên; Boutique vẫn chưa khỏe.

Đã sửa collector thành docker top -eo pid,args; lệnh đúng được chạy chỉ đọc trên agent và thành công, có header PID.31harness regressions đạt lại. Không sửa app/reader/writer backend/image, không mở public route hoặc thay guard. Wrapper07 chỉ trỏ receipt/authorization/source-manifest riêng, không chạm raw06. Source manifest kiểm trước execute; mọi bước còn lại giữ gói agent đã duyệt.

## Một cửa sổ thực thi

- Chỉ desktop-linux/k3d-zero-door, namespace zd-sqli-lab mới nếu absent, cả4ownedworkload trên k3d-zero-door-agent-0. **Một attempt≤20phút gồm5phút dành cleanup**, preflight120giây; host/WSL available≥1GiB, memoryPSIavg10≤5, watcher5giây. Guard/baseline/identity/isolation fail thì stop và cleanup, không tựretry.
- **0build/import/pull**, tất cả imagePullPolicyNever. Fixture tag zer46-fixture:24662046a33f; host index sha256:d85043c06db6a60c98cddb53a1545f6e053b6def409d43b156179a625df55274, node config sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16. Proxy digest sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c. Thiếu/drift thì stop.
- Static→proxyReady→sourceAReady→sourceBReady→fixture. Existing-pod hook admission trước namespace creation, rồi fixture hook đúng node/Pod/IP/namespace/FORWARD/REJECT trước app release và sau replacement. Giữ private routing/NAT/header trust/exact proxy32 và anti-spoof/TCP controls.
- **≤120fixture+32BoutiqueHTTP,≤2RPS,concurrency1,timeout3giây,≤6TCPcontrols**. Chỉ safe fixture và catalog/owned CRUD lành tính, không SQLi payload/executor/load/Kafka/LLM.
- Chứng minh nguồnA403, nguồnB200+CRUD; **mộtTTL180giây, một fixturePod replacement, một writer restart/read-only replay không gia hạn**; expiry/unblock, API+mount policy cleanup, namespace UID delete+absent. API accepted chưa là action effect. Giữ error/missing/timeouts trong evidence.
- Boutique observer trước/sau, không làm giả health/KPI/R1/end-to-end PASS, cleanup riêng và lab readiness tách biệt. Production executor/consumer vẫn disabled. Không sửa/restart Docker/WSL/node/sharedworkload/CNI/DNS/limits/Ingress/Prometheus, không model/cloud/external target/Gitpublication/LinearDone.

Source manifest và Bash entrypoint của07 đã chuẩn bị; không bảo đảm runtime đạt chỉ vì harness đã sửa. Quyền mới chỉ dành một attempt trong envelope này, không cho thêm recovery hạ tầng hoặc retry khác.
