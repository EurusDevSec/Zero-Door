# Checkpoint phiên

**Bắt đầu hiện tại:** Gói ZER-35 đã qua review độc lập baseline và delta CL-01–04, đều PASS (Claude chốt 20:50), không còn finding cần sửa trước publication. Hoàng đã cấp quyền **commit/PR**. Nhánh publication: `codex/zer-35-local-lab`, base `main` tại `1f43ff1461c2199bc99e9962483956c3df0fa975`. Tìm PR của nhánh này trên GitHub để đối chiếu commit và CI; trạng thái publication/CI đọc GitHub, không suy từ PASS offline. Bằng chứng ở [lab-restoration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md) và mục cuối [codex-review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md). Quyền này chưa gồm merge hoặc đổi Linear; Done còn cần merge và Hoàng chấp nhận. Không áp lại patch Traefik lịch sử.

**Bước phối hợp tiếp theo:** không cần thêm lượt review lặp khi mã vẫn khớp bản PASS. Theo dõi CI/PR; nếu sửa mã mới do lỗi CI hoặc finding mới thì review và retest đúng delta. Không triển khai lại lab hoặc tự nhận đã đạt LLM/vector/KPI nghiên cứu.

[Project Linear — P-ZER-1](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039) · [Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

## Checkpoint — 17/10/2026

Delivery tracking đã được tạo theo yêu cầu trực tiếp: 1 project, 8 milestone, 27 issue chính và 34 sub-issue. Read-back lúc 14:52:40 UTC / 21:52:40 Asia/Saigon: nội dung 61 issue, cha–con/milestone, đủ 92 mục nguồn và 80 prerequisite relations hai chiều đều khớp; DAG không có vòng kể cả hoàn tất con → cha. Mapping là APPLIED_VERIFIED, giữ alias/ID/URL và receipt, không là live board.

Ba sub-issue có điều kiện chưa tạo: B3 nếu giữ claim RQ2, hai vòng phản biện khi thực sự nhận. Các yêu cầu vẫn ở AC issue cha. Không đụng bốn issue onboarding. Lần nhập khởi tạo ở Backlog, không gán người/due/estimate/priority/cycle; trạng thái hiện hành đọc Linear.

Tài liệu hiện hành ở docs/delivery, lịch sử ở docs/archive/planning. Lượt này không sửa mã ứng dụng, chạy lab/model/thực nghiệm, gửi Slack hoặc commit/push.

## Đầu ra khởi động, chưa thực hiện

| Issue | Ghi chú kỹ thuật | Artifact dự kiến |
| --- | --- | --- |
| [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc) — Inventory chỉ đọc | [Lab local](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md) | `docs/evidence/R0-T02-S01/inventory.md` |
| [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) — Baseline/source ledger | [Phạm vi và tiêu chí](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md) | `docs/evidence/R0-T01-S03/baseline-source-ledger.md` |
| [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi) — Bản nháp event contract | [Event contract](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md) | `docs/design/r1-event-contract.md` |

Tại checkpoint 17/10 các artifact này chưa được tạo; xem bổ sung 18/10 bên dưới cho inventory mới. Bản nháp contract có thể chuẩn bị trước lab/LLM; khóa schema vẫn cần review ngữ nghĩa KPI/ground-truth boundary. Đây là checkpoint bước tiếp theo, không là xác nhận issue đã được giao hoặc đủ Ready.

Trước thực hiện, đọc AC mới nhất trên Linear, khóa HEAD/dirty và file/action scope; chốt cách chia sẻ artifact theo yêu cầu review. Provider/budget, lựa chọn thay đổi lab và nơi/đợt nhận bài xử lý ở issue tương ứng, không tạo lại backlog hoặc lặp hydration toàn repo.

## Bổ sung 18/10/2026 — kiểm tra tài nguyên local

Đã tạo [inventory ZER-34](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T02-S01/inventory.md) và [bàn giao lab](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md). Docker sau khi Hoàng mở đã hoạt động; kiểm kê thành công không thấy cluster k3d hay container đang chạy. Chưa dựng lại workload. Artifact còn local, chờ review/chia sẻ; không tự coi issue hoàn tất.

Bước tiếp theo: đọc evidence và chốt profile tài nguyên trước khi thực hiện nhánh dựng cluster nền của ZER-35; đo Docker/cluster rỗng rồi thêm dependency theo từng nhóm. Không chạy một lượt mọi setup cũ hoặc thay trần WSL từ kết quả mẫu ngắn. Baseline/source ledger ZER-33 và contract ZER-37 chưa được thực hiện trong phiên kiểm tra này. Trạng thái/due date/assignee vẫn đọc live Linear.

## Bổ sung 18/10/2026, 10:00 +07:00 — cluster nền truy cập được

Hoàng đã tạo cluster theo cấu hình repo. Đã sửa endpoint kubeconfig `k3d-zero-door` từ hostname không truy cập được sang localhost sau khi sao lưu; kiểm tra gốc thành công, hai node Ready và ba pod hệ thống Running. Có [baseline ZER-35](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/cluster-baseline.md), khoảng 526 MiB theo Docker stats; chưa có workload ZERO DOOR. Lỗi Docker stats người dùng báo chưa tái hiện bên Codex. Chưa đủ kết luận lab đầy đủ hoặc đóng issue. Tiếp theo chốt profile tài nguyên, thêm từng nhóm dependency và đo lại; giữ baseline làm mốc. Không chạy toàn bộ setup cũ một lượt.

## Bổ sung 18/10/2026 — công cụ Bash

Hoàng gửi kết quả terminal 10:08: cả hai lệnh nodes/stats thành công, node Ready, tổng usage container khoảng 531 MiB. Sau đó yêu cầu chuyển toàn bộ công cụ vận hành sang Bash. Đã thay 7 script, chuyển hướng dẫn/caller và thêm kiểm thử; [cách dùng Bash](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md), [evidence và giới hạn](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/bash-migration.md). 21 nhóm mock, cú pháp script/85 khối lệnh và probe tunnel native Windows qua; chưa dựng workload/attack hoặc thay status Linear. Tiếp theo review thay đổi rồi tiếp tục chốt profile, dựng từng nhóm dependency theo ZER-35. Dùng Bash cho mọi lệnh/hướng dẫn về sau.

## Bàn giao 18/10/2026 — Claude review Bash và sizing

Hoàng giao Claude thực hiện bước tiếp theo, Codex review đầu ra; Hoàng theo dõi/luyện. Phạm vi tại [handoff Claude](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/claude-lab-review-and-sizing.md): review độc lập migration Bash và đề xuất profile RAM/CPU + kế hoạch dựng từng nhóm cho ZER-35. Báo cáo dự kiến docs/evidence/ZER-35/claude-review-and-resource-profile.md; chưa thực thi hoặc xác nhận kết quả. Lượt này chỉ kiểm tra offline/truy vấn lab chỉ đọc và ghi báo cáo; chưa apply/đổi cấu hình lab, sửa source vận hành hay cập nhật Linear/Git publication. Codex nhường quyền ghi checkout sau bàn giao.

## Bổ sung 18/10/2026, 11:13 +07:00 — báo cáo Claude đã xong

[Báo cáo review Bash + profile tài nguyên](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/claude-review-and-resource-profile.md). Bước tiếp theo: Codex review, Hoàng chốt D1–D5, rồi chạy bước 1 (namespaces) kèm đo. Chưa thay đổi lab.

### Codex review báo cáo Claude — 18/10/2026

Đã đối chiếu báo cáo hoàn tất với source/config và upstream; [review riêng](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md) yêu cầu chỉnh hướng dẫn rollback có thể xóa PVC, ngân sách chart/default heap Kafka, HPA trong đường dựng và diễn giải KPI/MTTD. Chưa duyệt kế hoạch full stack để chạy nguyên văn. Claude tiếp tục sửa báo cáo theo review trước; chưa sửa source/config hoặc apply lab. Hoàng đã chọn Claude làm chính, Codex review; không cần hỏi lại vai trò. Không cập nhật Linear hoặc commit/push.

### Retest báo cáo Claude — 18/10/2026, 11:49 +07:00

Bản sửa 11:45 đã xử lý phần kế hoạch CR-01/03/04/05; CR-02 còn render/chart và đo trước nhóm tương ứng. [Retest Codex](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md) xác nhận đủ cơ sở đề xuất bước namespace/quota riêng, không cần thêm vòng sửa báo cáo để bắt đầu bước này. Chưa apply trong phiên retest; cần yêu cầu thực thi bước nhỏ từ Hoàng cho Claude. Không chấp nhận full stack hoặc tự đổi trạng thái Linear.

### Bước namespace/quota — 18/10/2026, 11:55–11:57 +07:00

Claude đã chạy riêng `bash infrastructure/scripts/setup-phase1.sh --component namespaces` (exit 0) sau khi kiểm Docker `desktop-linux`, context `k3d-zero-door` và hai node Ready. Đã tạo 3 namespace (`zero-door`, `target-app`, `monitoring`) cùng 3 ResourceQuota và 3 LimitRange; `kubectl diff` khớp cả 6 file. Giữ cấu hình hiện tại (quota `target-app` `limits.cpu` = 3). Không có workload hay PVC; RAM/CPU trước và sau gần như không đổi. [Bằng chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/namespace-bootstrap.md). Dừng để Codex review; chưa chạy component khác, Helm, commit/push hay đổi Linear.

### Codex review namespace — 18/10/2026, 12:10–12:12 +07:00

Đã đọc evidence và kiểm tra trực tiếp: 3 Namespace Active/labels khớp, 3 quota và 3 LimitRange có spec bằng YAML, hai node Ready; chưa có workload/PVC và không Warning. PASS riêng bước namespace/quota, chưa hoàn tất ZER-35/ZER-6. [Review Codex](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md) ghi phạm vi chuẩn bị ingress tiếp theo: kiểm vòng đời/compatibility, chọn version, render và ngân sách thực trước cài. ingress-nginx đã có thông báo retirement tháng 03/2026, cần đưa vào lựa chọn; chưa tự đổi controller hoặc cài chart. Codex chỉ truy vấn và ghi review, không mutation lab/Linear/Git publication.

### Giao trọn gói ZER-35 — 18/10/2026

Hoàng đã đồng ý chuyển từ bàn giao từng component sang Claude làm xuyên suốt, Codex review một gói. [Handoff hiện hành](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/claude-lab-review-and-sizing.md) đã thay quyền chỉ đọc cũ: cho phép sửa công cụ/config theo allowlist, dựng các nhóm nền, tự kiểm/sửa và probe tích hợp; giữ checkpoint tài nguyên bên trong, không xin phép từng lệnh. Quyết định ingress/ngoài scope được gom riêng, phần độc lập vẫn tiếp tục. Không cấp quyền xóa dữ liệu/recreate, chaos/LLM/cloud hoặc Git/Linear publication. Đầu ra chính dự kiến docs/evidence/ZER-35/lab-restoration.md; chưa thực hiện trong lượt cập nhật handoff này. Claude là bên ghi tiếp theo.

### Khôi phục lab trọn gói — 18/10/2026, 13:16–14:10 +07:00 (Claude)

**PARTIAL, chờ Codex review.** [lab-restoration.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md).
- Đã chạy trên `k3d-zero-door`: monitoring, Boutique 9 dịch vụ, ES/Fluent Bit, Kafka, Gaia/worker/Nemesis/Hephaestus và NetworkPolicy.
- Đã kiểm thật: giao dịch mẫu tới checkout, metric, log sentinel, Kafka round-trip, `/healthz` của agent, policy chặn đúng luồng.
- Còn mở: ingress chờ Hoàng chọn A/B ([ingress-preflight](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/ingress-preflight.md)); target frontend không có `/metrics`; guard host (RAM trống/pagefile) bị vượt trong lúc dựng.
- 14:40: Hoàng chọn Traefik. Gói phạm vi (2 patch, kiểm offline/dry-run, kế hoạch triển khai) chờ Codex review, chưa triển khai: [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md). Patch query Gaia/Nemesis nằm ngoài allowlist; Hoàng đã duyệt cùng gói. Triển khai cả hai patch sau khi Codex review đạt.
- Chưa commit/push, chưa đổi Linear.

### Codex review gói Traefik — 18/10/2026, 14:52 +07:00

**NOT READY, chưa triển khai.** [Review Codex](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md): TFM-01 HIGH về xung đột nhãn service của ServiceMonitor; TFM-02 kiểm cuối sau rebuild và phân loại FAIL đã biết; TFM-03 sửa thứ tự rollback port 80. Claude sửa cả ba trong cùng gói rồi trả retest; không hỏi lại lựa chọn Traefik/patch agent đã duyệt. Codex chạy 27 test mock trên bản sao và render độc lập; chưa áp patch thật hay đổi cluster/Linear/Git publication.

### Sửa TFM-01–03 gói Traefik — 18/10/2026, 15:15 +07:00 (Claude)

**Chờ Codex retest, chưa triển khai.** Chi tiết ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md), mục 12.
- TFM-01: thêm `honorLabels: true`.
- TFM-02: kế hoạch có cổng cho từng bước, kiểm cuối sau rebuild; `verify` exit 3 chỉ cho hai target frontend 404.
- TFM-03: rollback giải phóng port 80 trước, bằng `helm upgrade` sang ClusterIP.
- Patch hạ tầng mới SHA-256 `bd6624a7…a95c`. Patch agent giữ nguyên `b9e83cd9…a0`.
- Đã kiểm: `run.sh` 29/29, `test-local-restore.sh` (render thật và promtool) đạt, mutation bắt được lỗi, dry-run phía server. Chưa commit/push, chưa đổi Linear.

### Codex retest Traefik — 18/10/2026, 15:54 +07:00

**NOT READY, chưa triển khai.** [Review hiện hữu](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md): honorLabels/render và 29/29 test sạch đã đạt; còn TFM-04 (traffic probe phải qua các scrape), TFM-05 (lỗi đọc log Gaia đang thành PASS), TFM-06 (context rollback), kèm TFM-07 LOW (đường dẫn Python khi tắt MSYS conversion). Claude sửa cùng gói rồi trả Codex; không hỏi lại patch agent. Codex chỉ kiểm trên bản sao và ghi review/con trỏ, không triển khai hay đổi Linear/Git publication.

### Sửa TFM-04–07 gói Traefik — 18/10/2026, 16:35 +07:00 (Claude)

**Chờ Codex retest, chưa triển khai.** Chi tiết ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md), mục 13.
- TFM-04: check mới `consumers` (chạy cuối `ingress`/`all`): mỗi vòng 3 request lành, chờ một lần scrape chứa chúng; query agent chạy ngay sau lần scrape đã xác nhận thứ hai. Tối đa 4 vòng, 12 request.
- TFM-05: không đọc được log Gaia (và log Traefik) là FAIL.
- TFM-06: R1 là `setup-phase1.sh --component ingress --ingress-cluster-ip`, có guard và `--kube-context`; mọi lệnh mẫu mục 9–10 ghi rõ context.
- TFM-07: `run.sh` đổi đường dẫn cho Python bằng `cygpath -m`.
- Patch hạ tầng mới SHA-256 `03ab4a6c…f53f`. Patch agent giữ nguyên `b9e83cd9…a0`.
- Đã kiểm trên cây round-trip: `run.sh` 32/32 ở môi trường sạch và khi tắt path conversion; `test-local-restore.sh` exit 0 (5 nhóm promtool); mutation cho từng finding đều làm test FAIL. Chưa commit/push, chưa đổi Linear.

### Codex retest Traefik — 18/10/2026, 16:38 +07:00

**READY cho triển khai theo mục 9, chưa phải runtime PASS hoặc ZER-35 Done.** [Review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md): TFM-01–07 đã xử lý ở mức gói; Codex chạy độc lập 32/32 ở cả hai chế độ Git Bash, chart/render và năm nhóm promtool đều đạt. Infra SHA 03ab4a6c…ff53f, agent b9e83cd9…ca99a0. Claude triển khai tiếp theo trong quyền đã duyệt, không hỏi lại lựa chọn; giữ guard tài nguyên và bằng chứng cuối sau build rồi trả Codex review. Source thật và cluster chưa bị Codex thay đổi; chưa commit/push/merge hay đổi Linear.

### Triển khai Traefik dừng ở bước 0 — 18/10/2026, 16:45 +07:00 (Claude)

**Chưa áp patch, chưa đổi cluster.** Chi tiết ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md), mục 14.
- Đầu vào khớp Codex retest 16:38: HEAD, hai hash, 15 file gốc, apply-check. Docker context và khối S đạt. WSL MemAvailable 2,30 GiB, PSI 0,18.
- Cổng RAM trống của host (≥ 1 GiB) không đạt ở cả 5 lần đo: 609–897 MiB. Pagefile đang dùng 2983 MB.
- Mốc restart cho bước 8: từ 14:03, cartservice và paymentservice restart 1 lần, jmx-exporter của Kafka bị OOMKilled 2 lần, khi lab đang để yên.
- Bước tiếp: Hoàng giải phóng RAM Windows. Sau đó Claude chạy lại mục 9 từ bước 0; không cần Codex review lại.

### Triển khai Traefik đạt mục 9 — 18/10/2026, 17:27 +07:00 (Claude)

**Đã triển khai, chờ Codex review runtime.** Chi tiết và output nguyên văn ở [traefik-migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/traefik-migration.md), mục 15.
- Chạy lại từ bước 0 sau khi Hoàng giải phóng RAM. Host còn trống 3,2 GiB; WSL 2,31 GiB; PSI 0.
- Đã áp hai patch (infra `03ab4a6c…`, agent `b9e83cd9…`). `run.sh` 32/32; `test-local-restore.sh` exit 0.
- `frontend-external` chuyển sang ClusterIP. Traefik 42.0.0 (v3.7.14) giữ port 80/443; không cài CRD. Ingress của frontend, Nemesis và Hephaestus dùng class `traefik`.
- Kiểm trước build: `--check ingress` exit 0. Gaia và Nemesis được build lại; mã trong pod trùng SHA-256 với source đã vá.
- Kiểm cuối 2 phút sau rollout: `--check all` exit 3, chỉ có hai FAIL đã biết (frontend `/metrics` 404).
- Restart chỉ khác ở các pod mới của lượt này, tất cả 0 restart. `jmx-exporter` của Kafka đã OOMKilled 3 lần từ trước bước 0.
- Chưa commit/push, chưa đổi Linear; ZER-35 chưa Done.
