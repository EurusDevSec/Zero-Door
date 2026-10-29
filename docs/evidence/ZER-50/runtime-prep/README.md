# ZER-50 — runner đã review, chờ quyền runtime

[Proposal cụ thể](proposal.md) · [Source manifest](source-manifest.json) · [Review độc lập](independent-review.md).

Entry Git Bash (mặc định chỉ PLAN_ONLY, không đọc key hay gọi lab/model):

```bash
cd /c/Users/ACER/.codex/worktrees/zer-46-publication/zero_door
bash docs/evidence/ZER-50/runtime-prep/run.sh
```

`run.py` kiểm exact approved proposal/source hash và hạn≤24h, tiêu thụ output directory một lần, snapshot source/proposal, supervise physical native Python trong owned Job, rồi cleanup process riêng. `lab.py --work` còn đọc lại approval và claim marker exclusive/fsync trước client; stdin GO không phải quyền tự cấp. Cleanup giữ ownership/UID gate kể cả khi thời hạn cấp quyền bắt đầu đã hết. `authorization-template.json` cố ý false/expiry0; không có file cấp quyền được duyệt hoặc runtime-01 trong gói chuẩn bị.

Giới hạn xin quyền:≤2 model calls,9 fixture HTTP/2RPS/concurrency1,2 TCP,1 Healer dispatch,≤3 CAS replace attempts,TTL180s;600s work +285s cleanup và bounded process drain/reap. Cache-only4 workloads private;0Boutique/Kafka/shared restart/build/import/pull. Probe native phase≤115s, read-only projection≤85s, product bound120s; default20s không đổi. Xem proposal để biết nguồn/pins/preflight/điều kiện dừng chính xác.

Renderer lấy ZER-46 làm nguồn, thay whole-repo pins lịch sử bằng manifest78 file hiện hành; giữ check_guard_manifests, private topology, resources, imagePullPolicy Never và cache driver kiểm4 fixture built-source/exact image digest. Không sửa raw/harness ZER-46. C0 DETECTED là wrapper chức năng cố ý nominate benign access, không là Gaia thực. Delivered=True chỉ được project sau join HTTP thành công với raw log/request-ID/Pod UID/timestamp/response contents. Row giữ actual fixture UID; Pod thay đổi bị chặn trước dispatch.

16 test runner PASS với socket-connect guard và owned sleeping-process probes; reviewer retest16/16, test thêm native child+grandchild cùng Job và forced worker failure→cleanup riêng/no provider key.23 test Healer PASS trên hai production pins hiện có;54 regression trước đó vẫn giữ provenance, không lặp suite không liên quan. Baseline/diff/Bash syntax/default PLAN_ONLY PASS.

Windows timeout test quan sát file-handle release trễ15–20ms sau process/Job đã thoát; retry≤1s chỉ dùng để xóa temp test đã biết, không retry model/action/lab hoặc che lock kéo dài. Runtime giữ raw log, không xóa file sau timeout. Nếu supervisor/host bị kill hoặc ownership/cleanup thiếu bằng chứng, kết luận UNKNOWN/INCOMPLETE và cần reconciliation, không tự rerun.

Chưa chạy native model/API/fixture, chưa đọc key hoặc xác minh cache/lab readiness. Chưa đủ runtime AC/Done/G3/G4/availability recovery. Quyền publication/CI/merge/Linear và Hoàng nghiệm thu vẫn riêng.
