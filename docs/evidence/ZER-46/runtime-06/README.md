# ZER-46 runtime06 — fixture Ready, dừng vì collector

28/10/2026. **NOT_MET_COLLECTOR_FAILURE / OWNED_RESOURCES_CLEAN / NOT_READY_FOR_PUBLICATION.** Một attempt đã kết thúc sau199,46giây, không tựretry.

Gói agent cached-only được Hoàng duyệt.0build/import/pull,31guard samples đạt (hostmin3.576.000.512byte,WSLmin2.385.776KiB,PSImax0). Existing-pod hook admission đạt; cả4ownedworkload khởi động tuần tự trên agent-0. Fixture sqli-fixture-cbbfbc7b5-q9xf8 UID47eee699-14a5-45e5-b38a-95d3d60e52f3,IP10.42.0.173 có hook firewall đúng và Ready. Startup gate được release đúng một lần sau rule proof. Đây chưa là proof request attribution/block/benign/TTL/restart.

Lỗi do Codex để sót trong harness: raw/0068.json gọi docker top -eo args, daemon exit1: Couldn't find PID field in ps output. Lượt dừng trước fixture HTTP đầu tiên;0fixtureHTTP/0TCP/0writer. Không phải phép thử block/TTL thất bại hay PASS. Collector tương lai đổi pid,args; lệnh đúng đã được kiểm chỉ đọc và thành công tại ../gate-audit/agent-processes-fixed.txt. Không sửa scripts/raw06 để thay lịch sử.

Cleanup xóa namespace UIDe658fcc5-9387-4407-8a92-e57613dce054, đọc lại absent; shared spec/UID/restart/3PVC nguyên. Không còn owned resource/worker.9BoutiqueHTTP chưa đạt health, nên aggregate driver in INCOMPLETE giữ nguyên; receipt fixture-only tách owned-resource CLEAN với lab readiness NOT_MET.

[Raw reconciliation độc lập với runner](independent-verification.json) kiểm script SHA, hooked table, Ready/release, đúng lỗi collector,0imageoperations/request/writer,guard và cleanup UID/inventory. Chưa review bởi một người/agent khác. Raw giữ nguyên. AC01 request attribution/isolation và AC02 block/benign/TTL/restart vẫn thiếu; chưa Done/publication.

[Gói tiếp nối07](../runtime-prep/agent-retry-proposal.md) giữ mọi envelope/guard/AC, chỉ sửa collector + receipt wrapper riêng; NOT_APPROVED/NOT_RUN.
