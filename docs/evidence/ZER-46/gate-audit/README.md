# ZER-46 — chẩn đoán policy gate, 28/10/2026

**READ_ONLY_DIAGNOSIS / OFFLINE_HARNESS_VERIFIED / NO_NEW_ATTEMPT.** HEAD9567830020954bf3f30fd5a74240747be0c8ec1c, dirty; một writer Codex. Scope tại scratch/zer46/gate-audit/scope.json.

## Điều đã quan sát

Runtime05 có Pod fixture hostIP172.19.0.5/podIP10.42.1.42 trên server-0; 32 grep rule đều exit1, không stdout/stderr. Sau cleanup, cả legacy/nft trên server không có KUBE-POD-FW; top-level KUBE-ROUTER và policy chains/ipsets vẫn có. Controller có log khởi động v2.2.1, không thấy lỗi netpol trong tập log đã lọc; đây không chứng minh không có mọi lỗi.

Log startup02:56:15Z ghi retrieved node IP172.19.0.3 trong khi kubelet có --node-ip172.19.0.5. Netpol khởi động02:56:17Z trước registered-node02:56:18Z; metadata/interface hiện tại là172.19.0.5. Đây là dấu hiệu stale node identity tại startup. Chưa đọc được trực tiếp giá trị npc.nodeIPs trong bộ nhớ, nên nguyên nhân này là **giả thuyết có căn cứ**, chưa causal proof.

Node agent-0 có IP172.19.0.4 và các KUBE-POD-FW. Snapshot rule/Pod hiện hữu đối chiếu parser mới: **18/18 Pod Running không hostNetwork có hook đúng IP/name/namespace, chain có REJECT và FORWARD nối KUBE-ROUTER**. Đây chỉ là kiểm cấu trúc rule hiện hữu; không thay proof isolation/attribution của fixture sắp chạy. Cache trên agent có đúng fixture config d85cb460… và proxy digest575fa15b… từ import04.

## Đối chiếu nguồn chính thức

[K3s kube-router v2.2.1 constructor](https://raw.githubusercontent.com/k3s-io/kube-router/v2.2.1/pkg/controllers/netpol/network_policy_controller.go) đọc Node IP khi tạo controller. [getLocalPods và rule generation](https://raw.githubusercontent.com/k3s-io/kube-router/v2.2.1/pkg/controllers/netpol/pod.go) chọn Pod bằng HostIP trùng IP đó, sinh firewall/hook theo Pod; không yêu cầu Pod Ready. Vì vậy không mở ứng dụng sớm hoặc bỏ gate để xử lý thiếu chain. Có policy object/ipset chưa đủ chứng minh traffic đã đi qua firewall của Pod.

## Sửa offline và phương án

Giữ default server-0 cho runner cũ, thêm pin duy nhất agent-0 cho profile mới; cả 4 workload riêng cùng node, giữ selector/policy/private route/resource envelope. Cache inspection, gate và cgroup diagnostic theo đúng node được pin. Không thay app image, shared server, CNI, DNS, resources hoặc production executor.

Profile mới kiểm hook của Pod hiện hữu trước namespace creation, rồi kiểm hook riêng của fixture trước release và sau fixture replacement. Chain/comment đơn lẻ, sai node/IP/namespace, thiếu top-level jump hoặc thiếu mark-negated REJECT đều không đủ. Giữ các TCP negative controls, anti-spoof và mọi AC block/benign/TTL/restart/cleanup.

31 harness regressions đạt offline (8 component/5 fixture-only/5 cached/9 agent/4 preflight). Bandit theo ngưỡng high severity + high confidence không phát hiện finding; không claim đã kiểm toàn bộ low/medium findings. GitNexus query báo thiếu FTS, index27/10 stale; không dùng làm căn cứ runtime hoặc cố refresh bộ nhớ lớn. Source và direct consumers đã đối chiếu trực tiếp.

[Proposal node agent](../runtime-prep/agent-fixture-proposal.md) đã chuẩn bị, **NOT_APPROVED / NOT_RUN**. Attempt05 kết thúc; gói mới cần quyền riêng vì pin node thay đổi và giới hạn một attempt cũ đã dùng. Không restart/recreate shared infrastructure.

## Cập nhật sau runtime06

Owner đã duyệt profile agent và lượt06 đã kết thúc. Fixture có hooked firewall và Ready thật trên agent; vấn đề gate thiếu rule không tái hiện ở placement này. Điều đó không tự chứng minh stale IP là nguyên nhân duy nhất của server. Lượt dừng trước HTTP vì collector docker top thiếuPID; sửa pid,args được chạy chỉ đọc thành công, source future đã chỉnh. Không đổi raw06 hoặc guard, không tựretry. Xem runtime-06/README.md và gói agent-retry-proposal.md NOT_APPROVED/NOT_RUN.
