# Issue — Khôi phục môi trường local

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local). Nguồn đối chiếu: `R0-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước S01 chỉ đọc môi trường; file đầu ra: `docs/evidence/R0-T02-S01/inventory.md`. Không start/recreate/delete hoặc đọc secret trong bước này. S02/S03 chỉ mở sau inventory và phạm vi thao tác được chốt; không chạy mù start-demo/recreate.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T02-S01 | Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới. | [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc) |
| R0-T02-S02 | Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại. | [ZER-35](https://linear.app/zero-door/issue/ZER-35/khoi-phuc-lab-tu-inventory-dja-kiem-chung) |
| R0-T02-S03 | Kiểm tra Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique. | AC của [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T02-S01

Inventory có timestamp/kết quả hoặc lỗi rõ, context/Git/containers/volumes/ports/resources và phiên bản/args K3s khi truy cập; xác định nguyên nhân API không truy cập được. Truy vấn lỗi/bị ngắt không được coi là inventory rỗng hoặc container exited.

### R0-T02-S02

Kubernetes API truy cập; dữ liệu cần giữ được bảo toàn; lệnh dựng và profile tài nguyên được ghi. Kiểm tra script đúng chức năng; `bash start-demo.sh` chỉ mở/giám sát tunnel cho lab đã có, còn `bash rebuild-nemesis.sh --no-forward` build/import/rollout Nemesis, không tạo cluster. Bản Bash đã thay script cũ ngày 18/10; xem evidence migration để đối chiếu AC lịch sử trên Linear. Giữ volume/dữ liệu và ghi phạm vi thao tác.

### R0-T02-S03

Log/message truy vết, truy vấn metric và giao dịch mẫu; trạng thái Running riêng lẻ chưa đủ.

## Phụ thuộc cần đối chiếu

Không có.

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

Inventory đã có sáu AC đầy đủ tại [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc); không tiếp tục duy trì checklist sống thứ hai ở ghi chú này. Đầu ra dự kiến vẫn là `docs/evidence/R0-T02-S01/inventory.md`.

### Bàn giao 18/10/2026 — kiểm tra tài nguyên trước khôi phục

Theo yêu cầu Hoàng, đã kiểm tra chỉ đọc host/Docker/WSL/context/API và đối chiếu manifest tại HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`, branch main, working tree sạch trước phiên. Phạm vi ghi chỉ gồm ghi chú này và [inventory một phần](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T02-S01/inventory.md). Engine không truy cập, WSL docker-desktop Stopped, API từ chối kết nối; không có số đo tài nguyên pod hoặc inventory volume thành công. Hoàng xác nhận đã reset Docker làm mất container cũ và đang tắt Docker. Chưa xác minh phần volume/image còn lại.

Repo có cấu hình giảm tải nhưng chưa chứng minh tối ưu runtime. Host còn khoảng 4,55/15,78 GiB RAM khi Engine tắt; cấu hình WSL trên đĩa là 7GB/4 CPU/2GB swap. Chi tiết lệnh/kết quả/giới hạn và khoảng trống review ở artifact. Không start/stop/recreate/apply/build, gọi model/attack/heal, sửa cấu hình hoặc cập nhật Linear/Git publication. Tiếp theo: Hoàng mở Docker, kiểm kê lại Engine/container/volume/cluster; xác nhận nhánh start hay dựng mới, đo cluster nền trước khi khôi phục từng nhóm workload theo ZER-35. Không dùng hướng dẫn cũ hoặc báo cáo này như bằng chứng demo đã hoạt động.

### Kiểm tra lại 18/10, 09:45–09:46 +07:00

Hoàng đã mở Docker và yêu cầu kiểm tra. Engine desktop-linux trả lời thành công, thấy 4 CPU/~6,77 GiB RAM; không có container đang chạy và `k3d cluster list` rỗng. Inventory có 5 container S-cool đã dừng và 5 volume S-cool/n8n/buildx, giữ nguyên. Context k3d-zero-door còn trên đĩa nhưng không là cluster chạy được. Host còn ~1,5–1,7 GiB RAM, vmmemWSL ~4,3 GiB; trong Linux Cached ~3,25 GiB, MemAvailable ~6,12 GiB, swap chưa dùng. CPU host 11–17% ở ba mẫu ngắn, chưa có bằng chứng bão hòa hoặc rò rỉ RAM. Dung lượng build cache 13,5GB là đĩa, không phải RAM. Chi tiết lệnh/số đo/giới hạn đã nối vào inventory cùng file. Không thay môi trường, không dựng cluster hoặc đóng issue. Bước kế tiếp là chuẩn bị sizing và dựng cluster nền trong ZER-35 khi được thực hiện, đo lại rồi mới thêm workload từng nhóm. Cập nhật NOW chỉ để sửa con trỏ artifact cũ.

### Bàn giao 18/10, 09:58–10:00 +07:00 — cluster nền

Hoàng đã chạy lệnh tạo cluster bằng cấu hình repo và báo hai lệnh kiểm tra lỗi. Đã xác minh cluster `zero-door` tồn tại với server/agent `1/1`. `kubectl` trỏ `host.docker.internal:7356` bị connection refused; thử `127.0.0.1:7356` thành công. Codex sao lưu kubeconfig rồi sửa duy nhất server endpoint của entry `k3d-zero-door`; không recreate, deploy hoặc sửa manifest. Sau sửa, lệnh gốc truy cập được: hai node Ready, ba pod hệ thống Running/restart 0, top nodes/pods thành công. Docker stats thành công bên Codex, chưa tái hiện lỗi của Hoàng. Baseline container khoảng 526 MiB, không là tổng RAM host/WSL.

Chi tiết revision, phạm vi, backup, lệnh, số đo và giới hạn tại [evidence ZER-35](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/cluster-baseline.md). Chưa khôi phục workload hoặc kiểm chứng luồng mua hàng, chưa đủ đóng ZER-35/ZER-6. Tiếp theo chốt profile tài nguyên, khôi phục từng nhóm dependency và đo chênh lệch. Tài liệu vẫn local/chưa review chia sẻ, không cập nhật live fields Linear hoặc commit/push.

### Bàn giao 18/10 — chuyển công cụ vận hành sang Bash

Hoàng yêu cầu đổi toàn repo sang Bash trước khi tiếp tục dựng lab. Đã thay 7 entry point bằng `.sh`, thêm helper context/path/process dùng chung, chuyển hướng dẫn/caller và thông báo dashboard, thêm CI/kiểm thử offline. Quyền sửa file và kiểm chứng đến từ yêu cầu trực tiếp này; chưa triển khai các component lab hoặc chạy thực nghiệm thật. Các AC Linear còn nhắc hành vi script cũ được đối chiếu qua [evidence migration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/bash-migration.md), không tự sửa AC sống hoặc coi issue Done.

Kiểm chứng: cú pháp shell/85 ví dụ Bash/JavaScript PASS, 21 nhóm CLI mock PASS; một tunnel CoreDNS tạm trên localhost mở rồi dọn thành công bằng native kubectl Windows. Đã thêm điều kiện xóa cluster riêng, không kill mọi kubectl, bảo toàn Secret cũ và mặc định không chạy attack trong setup thực nghiệm. Cách dùng và khác biệt: [Bash tooling](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md). Full Helm/build/import/rollout/luồng mua hàng chưa kiểm chứng; tiếp theo review bản Bash và tiếp tục chốt profile tài nguyên, dựng từng nhóm của ZER-35. Chưa commit/push/merge hoặc cập nhật Linear.

## Bàn giao 18/10/2026 — Claude review Bash và sizing

Hoàng giao Claude thực hiện bước tiếp theo, Codex review đầu ra; Hoàng theo dõi/luyện. Phạm vi tại [handoff Claude](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/claude-lab-review-and-sizing.md): review độc lập migration Bash và đề xuất profile RAM/CPU + kế hoạch dựng từng nhóm cho ZER-35. Báo cáo dự kiến docs/evidence/ZER-35/claude-review-and-resource-profile.md; chưa thực thi hoặc xác nhận kết quả. Lượt này chỉ kiểm tra offline/truy vấn lab chỉ đọc và ghi báo cáo; chưa apply/đổi cấu hình lab, sửa source vận hành hay cập nhật Linear/Git publication. Codex nhường quyền ghi checkout sau bàn giao.

### Kết quả 18/10, 10:42–11:13 +07:00 — Claude review và sizing

Báo cáo: [claude-review-and-resource-profile.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/claude-review-and-resource-profile.md). HEAD `1f43ff1`, dirty có trước giữ nguyên.

- **Bash:** `bash -n` và 21 test mock PASS, Claude tự chạy lại; không có finding Critical. Ba finding Medium: k3d tạo cluster sẽ đổi current-context; `kafka-python==2.0.2` không hợp Python 3.12 của host; chưa có script dựng Boutique/Gaia.
- **Tài nguyên:** hai node cùng báo 4 CPU / 6,77 GiB nên scheduler thấy gấp đôi tài nguyên thật. Ước lượng full stack ổn định khoảng 3,2–4,9 GiB, chưa đo. Đề xuất giữ WSL 7GB/4 CPU, chế độ thí nghiệm giảm ứng dụng desktop, tăng `limits.cpu` của `target-app` lên 4, đặt heap Kafka tường minh.
- **Kế hoạch:** dựng 11 bước theo nhóm, mỗi bước có bộ đo và tiêu chí dừng.
- **Giới hạn:** chưa đọc Linear live, chưa dùng GitNexus. Network policy controller đang chạy nhưng chưa kiểm chứng hiệu lực từng policy.

Chờ Codex review và Hoàng chốt D1–D5; chưa thực thi bước nào.

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

### Codex review runtime — 18/10/2026, 18:03–18:07 +07:00

PASS riêng migration Traefik: mã trong pod/nhãn metrics/route/log khớp, patch đúng bản đã duyệt. [Review runtime](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md) gom LAB-01 JMX OOM, LAB-02 scrape frontend 404 và OBS-01 paymentservice restart mới lúc 18:01 (sau migration, nguyên nhân chưa biết). Claude xử lý trong scope, cập nhật kết luận lab-restoration còn cũ và trả kiểm cuối sau rollout; ZER-35 chưa được chấp nhận. Codex không mutation lab/Linear hay Git publication.

### Bàn giao Codex thực hiện gói cuối — 18/10/2026, 18:52 +07:00

Theo yêu cầu Hoàng, Codex nhận quyền ghi và đã sửa/triển khai JMX heap, scrape frontend 404, profile probe/CPU và lỗi Kafka consumer chặn event loop Nemesis; bổ sung recreate guard và CI regression. [Mục 12 của lab-restoration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md) giữ scope, từng lỗi, revision/hash, test và giới hạn. Kiểm cuối sau mọi rollout exit 0; 34 nhóm mock, 3 test consumer và real render/PromQL/quota đạt. 31 mẫu trong 15 phút 17 giây: không restart/thay pod ngoài dự kiến, Ready và 17 target đều đạt; JMX peak 141Mi; dữ liệu/PVC/quota giữ nguyên phạm vi.

Đây là gói đã tự kiểm của người thực hiện, chờ review độc lập bản cuối và publication/merge/Hoàng chấp nhận trước Done. HEAD 1f43ff1461c2199bc99e9962483956c3df0fa975, staged rỗng; không commit/push/merge hoặc cập nhật Linear. GitNexus refresh vẫn timeout, không nhận index current; không attack/LLM/cloud/KPI chính thức.

### Bàn giao publication — 18/10/2026

Hoàng đã cấp quyền commit/PR sau verdict PASS của Claude cho delta CL-01–04 (20:50). Codex chuẩn bị gói Bash/restore/Traefik và các tài liệu/evidence liên quan trên nhánh `codex/zer-35-local-lab`, base main `1f43ff1461c2199bc99e9962483956c3df0fa975`; allowlist từng file và hash ở scratch/zer35-publication. Bản đã review được đối chiếu hash trước staging; NOW và ghi chú này chỉ bổ sung quyền publication/con trỏ phiên. Không đổi mã sau review hoặc chạy thêm lab.

Kiểm đã có: 37/37 mock ở cả hai chế độ Bash, 18 kiểm render/PromQL/quota, 3/3 consumer, bốn mutant đều bị bắt; runtime integration và giới hạn ở mục 12 lab-restoration. CI remote phải đọc trên PR GitHub của nhánh này, chưa lấy PASS local làm PASS CI. Quyền publication bao gồm push nhánh để mở PR; chưa gồm merge, đóng Linear hoặc nghiệm thu. Sau publication, kiểm commit/CI trên GitHub rồi xử lý gate merge và Hoàng chấp nhận.


## Gói Claude — ZER-34 và đối chiếu nghiệm thu ZER-6 — 19/10/2026, 00:06 +07:00

### Kết quả cần bàn giao và lý do ưu tiên

Hoàng yêu cầu ưu tiên hoàn tất R0 hôm nay; mặc định Claude thực hiện, Codex review. Gói này review độc lập inventory ZER-34 do Codex lập và đối chiếu bằng chứng đã có với toàn bộ AC ZER-6. Không khôi phục lại lab chỉ để đóng tracking. Đây là phần khép nhóm lab; không thay các phần phạm vi ZER-5, RQ/đối chứng ZER-8 và backend thật ZER-36/ZER-7 của G0.

Codex đã đọc live ZER-34 và ZER-6 qua linear_zero_door, đúng URL linear.app/zero-door/, đầu ngày 19/10 +07. ZER-34 còn In Progress, sáu AC chưa checked; ZER-6 còn In Progress, ba AC chưa checked; ZER-35 Done. Đọc lại AC khi bắt đầu. Nếu Claude không truy cập đúng connection, dùng nội dung AC tóm tắt bên dưới và ghi snapshot/giới hạn, không dùng connector workspace khác.

### Baseline, ownership và file/action scope

- Baseline lúc chuẩn bị: branch zer-33-baseline-source-ledger, HEAD 10a26b0a0001046b23f57f667a3cb7be33e69090, upstream origin cùng nhánh. Dirty có sẵn: AGENTS.md, NOW.md, delivery README.md, WORKFLOW.md; WORKING-AGREEMENT.md untracked. Ghi chú local-lab.md được Codex nối chính gói này. Chụp lại HEAD/status và hash trước khi Claude viết; không coi snapshot hiện tại là bất biến.
- Codex kết thúc ghi sau bàn giao; Claude là writer tiếp theo. Khi tạo nhánh làm việc mới, dùng zer-34-lab-acceptance từ đúng HEAD đã kiểm; không stash/reset/ghi đè dirty hoặc thêm tiền tố codex. Nếu nhánh tồn tại, kiểm trước, không reset.
- Được tạo docs/evidence/ZER-34/claude-review.md làm báo cáo độc lập; nối kết luận vào ghi chú local-lab.md này; cập nhật con trỏ NOW.md. Inventory docs/evidence/R0-T02-S01/inventory.md chỉ được nối đính chính có nguồn nếu phát hiện lỗi, không sửa mất các snapshot lịch sử. Dữ liệu tạm/ledger/hash nếu cần nằm scratch/zer34/ (ignored).
- Chỉ đọc các source/config/Git/evidence liên quan. Không sửa source, script, test, manifest, raw CSV, DOCX, evidence/review ZER-32/33/35 hoặc dirty ngoài scope. Không commit/push/PR/merge, thay Linear, gọi API LLM, chi tiền hoặc gửi tin.
- Gói hiện tại không thao tác runtime: không start/stop/recreate, deploy/build/rollout, POST attack/heal/reset, chạy verify-local-lab.sh hay đọc secret. Probe này có mua hàng/sentinel/topic/pod tạm nên không gọi nó là truy vấn chỉ đọc. Nếu thật sự thiếu bằng chứng cần chạy lại, nêu chính xác AC/lệnh/tác động cần bổ sung và làm tiếp các phần độc lập; không tự mở rộng quyền.

### Nguồn và công việc phải làm trọn gói

1. Đọc delivery README → WORKING-AGREEMENT → NOW → WORKFLOW, issue/note này; không audit lại toàn repo. Review inventory lịch sử ở docs/evidence/R0-T02-S01/inventory.md, đối chiếu revision 1f43ff1461c2199bc99e9962483956c3df0fa975 và các manifest tại revision đó. Các lệnh PowerShell trong lịch sử là provenance, không phải lệnh phải chạy lại; thao tác mới dùng Bash.
2. ZER-34: kiểm sáu AC. AC-01: branch/HEAD/dirty, thời điểm/timezone và lệnh thực tế. AC-02: context, container/volume/port/resource và exit/lỗi/timeout; phân biệt mẫu Engine tắt 09:37 và mẫu thành công 09:45–09:46 ngày 18/10. AC-03: context/endpoint/API, version/args hoặc UNKNOWN/N/A có căn cứ khi cluster không hiện diện; không suy NetworkPolicy từ Flannel. AC-04: kiểm nhật ký/phạm vi bằng chứng chỉ đọc, ghi giới hạn của việc xác minh lịch sử, không khẳng định từ báo cáo tự khai là audit hệ điều hành đầy đủ. AC-05: quan sát, người dùng xác nhận, giả thuyết, bước quyết định tách rõ; report có thể đạt dù lúc đó lab chưa chạy. AC-06: báo cáo review độc lập có AC→evidence→verdict và artifact reviewer truy cập được tại vị trí chia sẻ đã duyệt. Kiểm file tracked/commit/remote thực tế; link local không tự thành remote/share approval. Nếu chưa đủ căn cứ chốt AC-06, giữ pending cụ thể.
3. ZER-6: lập bảng ba AC và verdict riêng dựa vào nguồn. AC-01 dùng inventory ZER-34. AC-02 đối chiếu đường start/create hiện tại, API, tài nguyên và bảo toàn dữ liệu từ ZER-35; script Bash theo docs/runbooks/bash-tooling.md, không bắt chạy lại script PowerShell cũ chỉ vì body AC còn nhắc tên cũ. AC-03 phải có tối thiểu 5 microservices, giao dịch Online Boutique, Kafka message/correlation, Prometheus query và ES/log. Running hoặc healthz riêng không thay các tiêu chí này.
4. Nguồn trọng tâm: docs/evidence/ZER-35/lab-restoration.md mục 12, nhất là dòng 270–296; docs/evidence/ZER-35/codex-review.md phần review cuối và Claude delta CL-01–04; cluster-baseline.md, traefik-migration.md chỉ mở phần cần truy vết. Kiểm source cited ở đúng revision và mốc triển khai. Bằng chứng cuối 18/10 18:36:07–18:37:51 exit 0, có checkout/Kafka/ES/health/policy/ingress; quan sát 31 mẫu, 15 phút 17 giây. Đây là bằng chứng lịch sử hữu hạn, không phải lab hiện tại vừa đo hoặc uptime 99,9%. Checkout loopback và ingress GET được kiểm riêng; không đổi thành checkout xuyên ingress.
5. Kiểm receipt publication ZER-35: PR https://github.com/EurusDevSec/Zero-Door/pull/19, merge được ghi 5471b587b57dec53c3847aba9ae898d0f9fca956, head a224ce54fc0e742bbb647c61e6e9201094a9de25. Xác minh bằng Git/GitHub/receipt khả dụng; phần không truy cập được ghi chưa kiểm lại. Không dùng câu chờ merge trong đoạn lịch sử để phủ nhận receipt sau đó; cũng không suy child Done là parent tự đạt.
6. Bảo toàn failure/OOM/timeout trước sửa, kiểm mọi giới hạn còn mở có chặn AC thật hay chỉ chặn nghiên cứu sau. Đừng yêu cầu chạy lại toàn bộ lab vì evidence cũ hơn một ngày nếu không có thay đổi làm mất hiệu lực; nếu revision/config drift, giải thích tác động chính xác.

### Tự kiểm và bàn giao một lần

Báo cáo ghi baseline/hash đầu-cuối, nguồn/line/revision, AC→expected→actual→verdict của cả hai issue; findings có vị trí, bằng chứng, ảnh hưởng và cách xử lý; phân biệt PASS kỹ thuật, pending sharing/acceptance và UNKNOWN. Tự kiểm link, bảng, hash bảo toàn, diff --check; không thêm test sao chép nội dung tài liệu. Sửa gom lỗi trong phạm vi tài liệu được giao trước khi bàn giao. Nếu cần sửa mã/lab, mô tả phần chặn thay vì tự làm.

Nối tóm tắt review/khoảng trống vào ghi chú này, cập nhật NOW và trả một gói cho Codex. Không tự đánh dấu Done. Codex review kết luận và delta theo AC, xử lý gom finding rồi trình Hoàng nghiệm thu/publication/tracking trong quyền thực tế. G0 chỉ được đánh giá sau khi có đủ lab + phạm vi + RQ/đối chứng/nhãn + LLM thật; không chốt R0 từ riêng gói này.

### Bàn giao Claude — ZER-34 và đối chiếu ZER-6 — 19/10/2026, 00:22 +07:00

**Đã review xong, chờ Codex review; chưa đặt Done.** [Báo cáo](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-34/claude-review.md) SHA-256 `4107dcdf8456f43debec8c32ceb43bd31842cae5b3511ab5d37e2ccb9c5cf0bf`, 161 dòng. Baseline HEAD `10a26b0`, staged rỗng, giữ nguyên dirty có sẵn; không tạo nhánh mới vì gói không commit. Linear chưa đọc live (không có `linear_zero_door`); verdict dựa trên snapshot AC trong gói.

- **ZER-34:** AC-01–05 PASS. 13 nhóm khẳng định tĩnh khớp revision `1f43ff1`; không cần đính chính inventory. AC-06 **pending**: inventory đã ở `main` công khai (blob `a2dd9cc` khớp), báo cáo review mới ở local.
- **ZER-6:**
  - AC-01 PASS kỹ thuật, phụ thuộc ZER-34.
  - AC-02 PASS kỹ thuật có giới hạn: RV6-01, nhánh create/start cluster bằng script chỉ có mock; RV6-02, chưa kiểm kê lại container và volume S-cool/n8n sau khôi phục.
  - AC-03 PASS kỹ thuật từ raw `verify-final.out` exit 0 (checkout, Kafka correlation, PromQL, ES sentinel, 9 pod Boutique) và 31 mẫu trong 15 phút 17 giây.
- **Receipt ZER-35:** PR #19 MERGED, merge `5471b58`, head `a224ce5`, 7 job CI đạt. 20/20 mục ledger của bản đã review khớp mã đã merge và HEAD; không có drift làm mất hiệu lực bằng chứng 18/10.
- **Đã kiểm:** selftest bộ kiểm 5/5; kiểm chính 23 OK / 0 FAIL (44 nguồn được bảo vệ không đổi, 4 dirty ngoài phạm vi giữ hash, ghi chú chỉ nối thêm, link/bảng hợp lệ, `git status` = baseline cộng báo cáo, `git diff --check` sạch). Mọi số dòng trích dẫn đã được soát lại trên nguồn.
- **Không làm:** không chạy Docker/kubectl/lab, không commit/push/merge, không đổi Linear.
- **Tiếp theo:** Codex đối chiếu với AC sống và review RV6-01/02. Hoàng quyết định chấp nhận giới hạn hoặc giao bổ sung (RV6-02 chỉ cần hai lệnh Docker chỉ đọc), rồi nghiệm thu và cho publication. G0/R0 chưa được chốt từ gói này. Claude nhường quyền ghi cho Codex.

### Codex review — ZER-34/ZER-6 — 19/10/2026, 00:43 +07:00

PASS kỹ thuật, chưa nghiệm thu/publication/Done. [Báo cáo, mục 9](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-34/claude-review.md) SHA-256 d7e758476c7567ff5229f6c7a3d97751cda3c819ade2f979c65cb0ee68dd5a0c. Đã đối chiếu AC sống; selftest 5/5, checker 23 OK, tính lại raw 31 mẫu/41 guard/chín pod/ba PVC và kiểm source/Git 9/9. Docker chỉ đọc lúc 00:42 giữ đủ năm container và năm volume có sẵn; chỉ xác minh hiện diện, không nhận kiểm toàn vẹn nội dung. RV6-01 là giới hạn coverage không chặn AC hiện hành; sửa câu mọi phép kiểm create đều cần wipe lab. Không chạy wrapper start/create hoặc verify lab, không sửa mã/cấu hình/raw; không đổi Linear, không publication. Không cần thêm vòng Claude; chờ Hoàng nghiệm thu và quyền commit/push/tracking cho ZER-34/ZER-6. G0 chưa đạt từ riêng gói lab.

### Hoàng nghiệm thu và cấp quyền publication — 19/10/2026, 00:47 +07:00

Hoàng trả lời “được” cho đề nghị nghiệm thu gói ZER-34/ZER-6, commit/push nhánh zer-34-lab-acceptance và cập nhật hai issue thành Done. Kết quả review kỹ thuật và giới hạn trong báo cáo mục 9 được chấp nhận; không cần thử lại bootstrap hoặc kiểm nội dung dữ liệu ngoài lab. Phạm vi publication: docs/evidence/ZER-34/claude-review.md (SHA-256 d7e758476c7567ff5229f6c7a3d97751cda3c819ade2f979c65cb0ee68dd5a0c) và ghi chú local-lab.md này. NOW chỉ cập nhật checkpoint, không gộp dirty quy ước/README/AGENTS/WORKFLOW/WORKING-AGREEMENT.

Báo cáo tài liệu được chia sẻ tại repository GitHub hiện có trong quyền vừa cấp; AC-06 chỉ được checked sau khi push và kiểm artifact remote. Gói này không sửa source/runtime, nên không có PR/CI/merge mới cần chạy; mã lab đã có review/verification/merge ZER-35 (PR #19), còn nghiệm thu ZER-6 dựa vào đối chiếu tích hợp trong báo cáo. Quyền này không chốt G0 hoặc các issue R0 khác, không cho phép gọi LLM/chi phí.
