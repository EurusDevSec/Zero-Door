# ZER-33 — Baseline và source ledger (R0-T01-S03)

[Ghi chú issue](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md) · [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) · issue cha [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia)

Người thực hiện: Claude, theo “Gói giao Claude — ZER-33 — 18/10/2026, 23:10 +07:00”. Thời gian thực hiện: 18/10/2026, 23:12–23:30 +07:00 (Asia/Saigon). Codex review độc lập sau bàn giao.

Đây là ảnh chụp tài liệu, Git và dữ liệu đã lưu tại thời điểm đọc. Gói không chạy lab, model, runner, analysis hay benchmark. Mọi hash chỉ chứng minh nội dung byte đã đọc, không chứng minh cấu hình đang chạy hay kết quả thí nghiệm đúng.

## 0. Kết quả

**Đủ để Codex review; đạt theo snapshot AC trong gói giao.** Claude chưa đọc AC sống vì không có kết nối Linear được phép dùng (mục A.2). UNKNOWN dưới đây là khoảng trống nguồn được ghi đúng, không phải phần bỏ sót.

- **Baseline:** nhánh `zer-33-baseline-source-ledger`, HEAD `8e7b74f1cacc87387e5f35d078e5b1bb48c318fe`. Staged rỗng. Có 5 file modified và 1 untracked từ trước, đều ngoài delta Claude. 47 file cấu hình/pin sạch, khớp HEAD.
- **Dữ liệu legacy:** 8 raw CSV, 48 dòng vật lý, 40 bản ghi, mỗi file 5 bản ghi. Không lỗi parse, không trường multiline. Toàn bộ 40 `attack_start` nằm trong 25/06/2026, 15:30:27–15:54:22 UTC. Summary là dữ liệu dẫn xuất: 8 nhóm, tính lại theo quy tắc `analysis.py`, chênh tối đa 0,004. File thử 12/07 được tách riêng, không thuộc mẫu.
- **Đối chiếu H03:** đúng 8 file/40 bản ghi (handoff ghi “40 files”). 40 lượt có timestamp 25/06, không phải 12–13/07. E3 AUTO có 4/5 FAILED vẫn mang MTTR 1,01–1,02 s. 9,24 s là P95 nội suy tuyến tính, max là 11,26 s.
- **Phát hiện mới, cần review:**
  - Không tính lại được MTTD/MTTR từ các cột timestamp; chênh tới khoảng 3,3 s (B.5).
  - `run_id` lặp giữa AUTO và MANUAL ở E1/E2.
  - 40 lượt chỉ trải trong khoảng 24 phút, trái với lý do “mỗi lượt khoảng 2 phút” trong báo cáo tự đánh giá.
  - Mục CHECKPOINT trong transcript IDE có bản tóm tắt yêu cầu người dùng do IDE sinh, bị cắt cụt. Review 09/10 chỉ nói các mục này không có chat cũ.
- **Source ledger:** 30 mục L01–L30 bao phủ H01–H08 (mục C.4).
  - Còn UNKNOWN: chat gốc và lời duyệt, hồ sơ gia hạn, danh tính `hp8001`, log cloud/LLM và nguyên nhân E3 FAILED.
  - Còn UNKNOWN: code thực sự chạy tháng 6 và chất lượng đồng hồ.
- **Kiểm chứng:** script offline `scratch/zer33/ledger_check.py` đạt; selftest bắt được thiếu file, đổi hash và lỗi parse. Nguồn được bảo vệ không đổi trước/sau. Diff nằm trong allowlist. Kết quả chi tiết ở mục D.

## A. Baseline có thời điểm

### A.1 Git

Chụp lúc 18/10/2026 23:12:07 +07:00, trước khi ghi file nào, bằng `git rev-parse HEAD`, `git status --porcelain=v1 -uall`, `git diff --cached --name-status`, `git diff --name-status` và `sha256sum`.

- Nhánh `zer-33-baseline-source-ledger`, HEAD `8e7b74f1cacc87387e5f35d078e5b1bb48c318fe` (commit 18/10/2026 23:08:05 +07:00, `docs(ZER-32): record accepted requirements and KPI definitions`). Một worktree; `git stash list` rỗng.
- **Staged:** rỗng.
- **Unstaged có sẵn trước gói:** không do Claude tạo trong gói này; giữ nguyên.

| Path | Trạng thái | SHA-256 lúc bắt đầu |
| --- | --- | --- |
| `AGENTS.md` | M | `fe18d0003c865a021eb7eb8a2432ea290b034deec5cad3cb5c1cd338be88d50e` |
| `docs/delivery/NOW.md` | M | `6351afdf9609b73240609bf32ad3f86a77873e0df430aecfcecd7df6f8a40eab` |
| `docs/delivery/README.md` | M | `c7b9f0f8673359cce4be9d3bb0a4517925060b4b98345de1d8f5edc3f0a220b4` |
| `docs/delivery/WORKFLOW.md` | M | `ded0fdee2473ce8cac32f994f4139ee59e241e13fc48528b0fe42c026ef15ffb` |
| `docs/delivery/milestones/R0-foundations/scope-and-criteria.md` | M | `cf7d938eba8ee05004ab0f1d93db81c63956687c8f86156076c735b4af9ed7bf` |
| `docs/delivery/WORKING-AGREEMENT.md` | ?? | `fc34c9ae5fc3f6edfd1197c79b5bee380c0b9ec1b3a365df363405084264bc87` |

- **Delta Claude theo allowlist:** tạo artifact này; nối bàn giao cuối ghi chú issue; sửa con trỏ đầu `NOW.md`. Ngoài repo chỉ ghi `scratch/zer33/` (gitignored). Hash cuối ở mục D.4.
- Timeline Git dùng `%ci`/`%cI` (committer date, +07:00). Đây là metadata do máy commit ghi, không phải đồng hồ được kiểm chứng độc lập. Mọi commit liên quan có tác giả `LeganSar44`; tên trong Git config không chứng minh danh tính người chạy thí nghiệm.

### A.2 AC dùng để kiểm

Claude không đọc AC sống. Kết nối Linear trong phiên Claude không phải `linear_zero_door` đã xác minh. Quy tắc phiên cấm dùng connector thay thế hoặc cài lại MCP. Gói dùng snapshot Codex đọc lúc khoảng 23:07 +07:00, 18/10/2026: AC-01 ZER-33 / AC-03 ZER-5 yêu cầu:

- HEAD/dirty/cấu hình.
- Inventory legacy và ledger H01–H08.
- Hash/số dòng từng CSV.
- Timestamp dữ liệu tách khỏi timeline Git.
- Phân loại DOCX/xác nhận mới/IDE/chat.
- Kiểm path, giữ nguyên raw/handoff.
- Lịch sử hoặc danh tính thiếu nguồn ghi UNKNOWN.

Snapshot không chép nguyên văn AC; Codex cần đối chiếu AC sống khi review.

### A.3 Cấu hình và pin trong Git

Dưới đây là cấu hình trong Git. Cấu hình đang triển khai trong cluster chưa được truy vấn: gói cấm Docker/Kubernetes, và hash file không chứng minh bản đang chạy. Không đọc hoặc đưa giá trị Secret vào báo cáo. `nemesis-deployment.yaml` có khối `kind: Secret` với giá trị mẫu để trống; gói chỉ hash file.

Pin chính, trích từ file dưới đây:

| Thành phần | Giá trị trong Git | Nguồn | Ghi chú |
| --- | --- | --- | --- |
| Helm chart | kube-prometheus-stack 92.10.1; kafka 29.3.2; traefik 42.0.0 | `infrastructure/helm-values/chart-versions.yaml` | Digest chart được ghi trong comment, trỏ evidence ZER-35 |
| K3d/K3s | 1 server + 1 agent, `--disable=traefik`; **không pin image k3s** | `infrastructure/k3d-config.yaml` | Bản k3s phụ thuộc phiên bản k3d cài trên máy. Evidence ZER-35 đã lưu ghi 2 node `v1.31.5+k3s1` lúc 18/10 13:16; gói không truy vấn lại |
| Online Boutique | image `…/microservices-demo/*:v0.10.5` | `infrastructure/manifests/target-app*.yaml` | `redis:alpine`, `busybox:latest` không pin phiên bản |
| Agent/worker | `gaia`, `hephaestus`, `nemesis`, `chaos-worker` tag `:latest`, build local | manifests tương ứng | Tag không xác định nội dung image |
| Logging | Elasticsearch 8.13.0; fluent-bit 3.0 | `infrastructure/logging/*.yaml` |  |
| Python agent | base `python:3.11-slim` → distroless; FastAPI 0.110.0/0.111.0, kafka-python 2.0.2, kubernetes 28.1.0, openai 1.35.5… | `agent-orchestrator/*/Dockerfile`, `requirements.txt` | Gaia `elasticsearch>=8.13.0,<9.0.0` là khoảng, không pin |
| Go worker | Go 1.21; k8s client v0.28.3; kafka-go v0.4.47 | `chaos-worker/go.mod`, `go.sum` |  |
| Runner/analysis | `requests>=2.31.0`, `pandas>=2.0.0`, `matplotlib>=3.7.0`… | `infrastructure/scripts/requirements-experiments.txt` | Khoảng `>=`, không đủ tái lập môi trường analysis tháng 6 |

Hash từng file (tính lúc 23:18 +07:00; cả 47 file sạch và trùng blob HEAD):

| Path | SHA-256 | Commit cuối chạm file | Trạng thái |
| --- | --- | --- | --- |
| `infrastructure/k3d-config.yaml` | `dc55cda031d04307d1126fbcec4b88fabbf7d7918878b18faf55dc092e639065` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/helm-values/chart-versions.yaml` | `f88e21521d8e5427e96deda48badedbaf5c913c9c6b24226de20f4c35383467b` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/helm-values/kafka-values.yaml` | `7255e5f42ddb47274a749147238e6f48c2c9fc81137ad42c5453d8d89525c8e3` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/helm-values/prometheus-values.yaml` | `df311e8d42fd91a60e1c36a82ae25a24213807655bb4b9e07a1a53bc003af3a6` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/helm-values/traefik-values.yaml` | `69b3fb9253ebe1cb605c82e467df23c9cb905ad29e3172596eaeb2bbdac814b1` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/helm-postrenderers/kafka-jmx/plugin.yaml` | `7cf7d4c1c0dc09b88212c576876455e5dea55c7742df5ce6064f790dfd35a83b` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/helm-postrenderers/kafka-jmx/render.py` | `69eac40e8961f05a84c196b5c4e700ec07b0c315d029550f05837d891d9c176f` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/chaos-worker.yaml` | `4348ab43e8e492858497e94bc85807432a7b03746bcb96becf813a602a50094d` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/gaia-deployment.yaml` | `83add9518dc1393f350746c4202c7798c3529677496b987bffa888cb4e34db92` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `infrastructure/manifests/hephaestus-deployment.yaml` | `79507bd4105bfb856887db06e97e808e2fd6de5f4d58ea86e96f71813af0e0d8` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/nemesis-deployment.yaml` | `35046c65e09d6a6b7d00913501c5e0044db73c2f6a60a9943e50209683fed2f9` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/network-policies.yaml` | `1d86135d1d03c541a5388b169f806218e5405f6c22bbc6e8aa7515e8cccd4ce3` | `b54b269` 2026-07-03 | sạch, = HEAD |
| `infrastructure/manifests/prometheus-rules.yaml` | `9f7415b32762b00ef4e0f4f5521702a6de78021283aaaf7fe982d1c6bb8a7e32` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/target-app-addons.yaml` | `b5efcf6c2b5bd64575542de41d187f8eaf50f948a1b4421d27b9b583e5641474` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/target-app-hpa.yaml` | `2650e0d92be71d797449c2162da0421e6be7e44c10b12d087c93a02ac297aacd` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `infrastructure/manifests/target-app-ingress.yaml` | `2911257e3795eed4ff2216f1f2029a6ac741c54ed6cb6f64ee80887294a93027` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/manifests/target-app-raw.yaml` | `3e4d7b4764a14bcf1b67251c044cdc2c72464548362413ed89c2a8613b43521f` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `infrastructure/manifests/target-app.yaml` | `dbcd45e1b74594d8787ad409148fbb438172b21b7d28dddc5de5af784bad3bdb` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/namespaces/monitoring.yaml` | `f4a4b9a2a5af2def0c5ef88312baa9787d8b0d2bb8f148ed25fa1dafed85bc59` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/namespaces/target-app.yaml` | `c0532be173564067a41013b77221e143752625038bbdc8eb26d72b121bdf34c4` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/namespaces/zero-door.yaml` | `81f6ee3899d1aeed61e9fffdf6668fca976caeab73b9459ce78a7298367e7c20` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/resource-quotas/monitoring-quota.yaml` | `61c3da945fee746f0169239297a800fc23d37028e8e36911d91f06263d2af239` | `54ff513` 2026-07-12 | sạch, = HEAD |
| `infrastructure/resource-quotas/target-app-quota.yaml` | `0b957f966a4b7852cb5cd5e700fc0789037683896d8058a9904cd0d2554f327d` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/resource-quotas/zero-door-quota.yaml` | `c1a0c04041339a5b7d5a33867e25f016144fd8930fd41f3d503c5e24680d1b94` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/logging/elasticsearch.yaml` | `86e06ea5d85700ea6d9fc82602ec0c897670c6bc6828c083c0473e91430de2cf` | `2995de7` 2026-06-23 | sạch, = HEAD |
| `infrastructure/logging/fluent-bit.yaml` | `ca535d91483fa2fbb69b4e4239662e807c10d1f3fa2a6bbe03d050c9e5c8dd2d` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `infrastructure/scripts/lib/common.sh` | `d58868794305060563c5719debd38e642c8ccefba6ca2aa768d282c78d02b304` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/scripts/recreate-cluster.sh` | `ba2ae40ab20cb883e0b66dfcdb6e26a453c6ee6293a56f82ea100e9f48c2e189` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/scripts/setup-phase1.sh` | `45f629d67f6054d49839d34392009ed7d639cae55694eb9f12651670bdd2d696` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/scripts/setup-local-apps.sh` | `d4a20e8f73ee3f6e587a31942e990de0cacf0ac7faf3772d40a564ae439921e6` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/scripts/verify-local-lab.sh` | `35ea0f1ffddd22d59c328ad1c797505285fa3fa7ddb6bcab45a256506836be59` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `infrastructure/scripts/experiment_runner_direct.py` | `b59e99a18df17aa80737b50757afeb7e13f66c03546b07bd9f124f9cb9ca2e06` | `a179aad` 2026-06-25 | sạch, = HEAD |
| `infrastructure/scripts/analysis.py` | `128f58063b6bfc3b852826c9f0ca8f9e2aadad7f80ef90e05175dbc9062b76c0` | `a179aad` 2026-06-25 | sạch, = HEAD |
| `infrastructure/scripts/requirements-experiments.txt` | `408820ed7389ad6f6e4204f4d60bef77f4f7155732c90c5d36141a6102808d7a` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `agent-orchestrator/gaia/requirements.txt` | `2e6ecb7cf5a4fb6470f5640d87529184097d9ae1e6a6a151cbc197b104ec2818` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `agent-orchestrator/hephaestus/requirements.txt` | `87150919b5a640ff27efc500637e76a16383042b8de341f699cf29bc6bfb6f54` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `agent-orchestrator/nemesis/requirements.txt` | `d1e48001704b0bcd3939d2f26a10d5e784fb2d706aea94d3a36df99c8f8f0e05` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `agent-orchestrator/gaia/Dockerfile` | `38cf636fe44a391fd9bd6b3169d947ad4eac39b64f579b4fd7b23d3a1aea0f56` | `1804986` 2026-07-11 | sạch, = HEAD |
| `agent-orchestrator/hephaestus/Dockerfile` | `4eea3bf8c0aff76940ac905723d16d3c9baadb54c822f10fe20267a95286881b` | `1804986` 2026-07-11 | sạch, = HEAD |
| `agent-orchestrator/nemesis/Dockerfile` | `93f240d669cbcea4614ed8a3ce12a402da5ea55c426fe6c90d0edc0ad43fdd03` | `1804986` 2026-07-11 | sạch, = HEAD |
| `chaos-worker/go.mod` | `4086ed2fcc62282bf8dfca00e2d9a49ad8eca99b155b7bd58a4f291dc9cbe718` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `chaos-worker/go.sum` | `ad8825dcc574238a9da95164134e6ae7366255a270c897945ebbdcd7d5d3d5ec` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `chaos-worker/Dockerfile` | `def991f37e2499b1b1802872510be7fa354674d5c58815584a30b548df58c3b8` | `e64559c` 2026-06-24 | sạch, = HEAD |
| `.github/workflows/ci.yml` | `2160711a6e0d5ebde2a6232a34ea5ae5c43ed70bfe799c9c670026308c6fc418` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `rebuild-nemesis.sh` | `1bfaedb33d3fbdcea71cd922cee890b018f4f35637bdec1436a43a02aafbae6b` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `.gitattributes` | `0e4badf2fb64b51316d43d1c27b899b60f91a12b317d532dbf41044e9fe71b76` | `a224ce5` 2026-10-18 | sạch, = HEAD |
| `.gitignore` | `10ffeb0cd0f970e46d3d34221e32947443ad768499fe3522e44fabc59b6aff5f` | `a224ce5` 2026-10-18 | sạch, = HEAD |

`experiment_runner_direct.py` và `analysis.py` chưa đổi kể từ `a179aad`, cùng commit đưa 8 CSV vào Git. Runner được thêm ở `2061837` (25/06 22:09:33). Như vậy mã ở HEAD trùng mã được commit cùng dữ liệu. Chưa có log thực thi nào chứng minh đúng bản mã này đã sinh ra CSV (L29).

## B. Inventory dữ liệu legacy

### B.1 Raw CSV

Thuật toán (`ledger_check.py`, hàm `inventory_bytes`):

- Đọc bytes gốc, tính SHA-256.
- Dòng vật lý = số `\n`, cộng 1 nếu byte cuối không phải `\n`.
- Decode UTF-8 strict; parse bằng `csv.reader` (`newline=""`, xử lý quoted/multiline).
- Bản ghi = hàng sau header không rỗng. Kiểm độ rộng từng hàng, header, số và timestamp ISO-8601.
- Tổng được đối chiếu theo hai cách: tổng bản ghi parse được, và tổng dòng vật lý trừ header (khi không có multiline).

Working tree lưu CRLF, Git index lưu LF (`core.autocrlf=input`; `git ls-files --eol` báo `i/lf w/crlf`). Vì vậy SHA-256 bytes trên đĩa khác SHA-256 nội dung trong Git. `git hash-object` của file trên đĩa trùng blob HEAD cho cả 8 file. Runner ghi bằng `csv.DictWriter`, kết thúc dòng mặc định là CRLF. CRLF trên đĩa phù hợp với định dạng runner ghi, nhưng không tự chứng minh đây là bytes nguyên thủy.

| File (dưới `docs/experiments/raw_data/`) | SHA-256 bytes trên đĩa (CRLF) | Git blob HEAD | Bytes | Dòng vật lý | Bản ghi | Scenario/mode | heal_status | run_id | attack_start UTC (+07:00) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `e1_cpu_stress/results_20260625T153348.csv` | `d6188213c2bac6c137fad74cfdd375ef8e9413caf87434ab6eb9917a404a30a7` | `bf2b1578c80f` | 1240 | 6 | 5 | E1/AUTO 5 | SUCCESS 5 | 1–5 | 15:30:27–15:33:21 (22:30:27–22:33:21) |
| `e1_cpu_stress/results_20260625T154933.csv` | `624df7c3cc9e4187b1f5a6b45bb51b18acfe8291ee8313f0872d16243a75ac52` | `f437048cba4d` | 1234 | 6 | 5 | E1/MANUAL 5 | MANUAL 5 | 1–5 | 15:46:15–15:49:07 (22:46:15–22:49:07) |
| `e2_http_flood/results_20260625T153523.csv` | `8ce7945c4a2aa066c32714392d5feaba3ce32880aba27bd31f8de1a7e4db809c` | `c6d9d6a98a19` | 1236 | 6 | 5 | E2/AUTO 5 | SUCCESS 5 | 6–10 | 15:34:04–15:35:21 (22:34:04–22:35:21) |
| `e2_http_flood/results_20260625T155104.csv` | `6e6003b9846ec726397caa1b05726f9d153ecd2df3b308bb928424d4b694beeb` | `5e495311a347` | 1231 | 6 | 5 | E2/MANUAL 5 | MANUAL 5 | 6–10 | 15:49:49–15:51:03 (22:49:49–22:51:03) |
| `e3_pod_kill/results_20260625T154325.csv` | `1c33a45c71ea6368a7a65362f16e4be3d61d57c7ce90caa9820b86e6122d2611` | `b70f5161c125` | 1222 | 6 | 5 | E3/AUTO 5 | SUCCESS 1, FAILED 4 | 1–5 | 15:41:57–15:43:22 (22:41:57–22:43:22) |
| `e3_pod_kill/results_20260625T155238.csv` | `acb392a526e3f8bf89dcc9bb123762a3ef742976d2f458b1467db564cafc4b88` | `8eceee4aab65` | 1225 | 6 | 5 | E3/MANUAL 5 | MANUAL 5 | 11–15 | 15:51:21–15:52:36 (22:51:21–22:52:36) |
| `e4_combined/results_20260625T154540.csv` | `596f880294474677572ef454ccf72b2d553ccffae3ccf1096b3282b5bb902df1` | `3a6e63658a49` | 1225 | 6 | 5 | E4/AUTO 5 | SUCCESS 5 | 1–5 | 15:44:01–15:45:34 (22:44:01–22:45:34) |
| `e4_combined/results_20260625T155428.csv` | `7e02266c2862433459950c7845a8cd73af65cdbb19a65c691da6c540bab98020` | `45e00bc52d49` | 1225 | 6 | 5 | E4/MANUAL 5 | MANUAL 5 | 16–20 | 15:52:54–15:54:22 (22:52:54–22:54:22) |

- **Schema chung (15 cột, cả 8 file giống nhau, khớp dataclass `ExperimentResult` của runner):** `run_id, scenario, mode, attack_type, attack_start, attack_end, detect_time, heal_start, heal_end, mttd_seconds, mttr_seconds, uptime_percent, heal_status, false_positives, notes`.
- **Timezone:** cả 200 giá trị timestamp (5 cột × 40 bản ghi) có offset `+00:00`. Không có `TIMEOUT`/`N/A`.
- **Lỗi đọc/parse:** không có lỗi decode, độ rộng, header hoặc số; không có hàng rỗng hay trường multiline.
- **Tổng:** 8 file; 48 dòng vật lý; 40 bản ghi (= 48 − 8 header); 5 bản ghi/file. Theo scenario/mode: E1–E4 × AUTO/MANUAL, mỗi nhóm 5. Bằng mốc lịch sử H03, nhưng mốc này chỉ để đối chiếu, không dùng ép kết quả.
- **Giá trị đáng chú ý:**
  - `uptime_percent` = 100.0 ở cả 40 bản ghi.
  - `false_positives` = 0 ở cả 40 bản ghi; runner gán cứng 0.
  - `notes` rỗng.
  - 20 bản ghi MANUAL có `mttr_seconds` = -1 và `heal_status` = MANUAL.
  - AUTO: 16 SUCCESS, 4 FAILED (đều thuộc E3).
- **`run_id`:** không trùng theo (scenario, mode, run_id), nhưng lặp giữa AUTO và MANUAL trong cùng scenario ở E1 (1–5/1–5) và E2 (6–10/6–10).
  - E3 dùng 1–5/11–15; E4 dùng 1–5/16–20.
  - Muốn định danh duy nhất phải dùng (file, run_id) hoặc (scenario, mode, run_id).
  - Lý do đánh số không có nguồn: UNKNOWN.

### B.2 Dữ liệu dẫn xuất

Các file này không cộng vào số raw trials.

- `docs/experiments/analysis/summary_statistics.csv`: SHA-256 `bfb2bb33f63896e1f4b65ab1a4d4e5e860bc82e1246363744365301519662ad5`, 9 dòng vật lý, 1 header, 8 nhóm (scenario × mode).
  - Kiểm lại theo đúng quy tắc của `analysis.py`:
    - Lọc `mttd_seconds >= 0` (analysis.py:79).
    - MTTR bỏ giá trị âm.
    - Quantile nội suy tuyến tính như mặc định pandas.
    - `heal_success_rate` tính cả SUCCESS và MANUAL là thành công (analysis.py:100).
    - Làm tròn 2 chữ số.
  - Cả 8 nhóm và 12 cột số khớp; chênh tuyệt đối lớn nhất 0,004 do làm tròn.
  - Kiểm này chỉ xác nhận summary được suy ra đúng từ 40 bản ghi theo quy tắc cũ. Nó không chứng minh quy tắc đó đúng (xem L11, L13).
- 5 PNG trong `docs/experiments/analysis/` được thêm cùng `a179aad`, Git chưa ghi thay đổi nào sau đó:
  - `heal_success_rate.png` `ed7d01790746b6c300fd20e16153722c2784342ef2ca0d61dbd532e3db524ee7`
  - `mttd_boxplot.png` `040b45e4b86f79b49202790b021c3843b704fc41227fe8c7f08c3d4db2f01948`
  - `mttd_comparison.png` `72d9ef0028e6a22a6e064b9d57398cac24141a019f1059d3e9ca5888694491a8`
  - `mttr_comparison.png` `4b033e4118fc99cfd130c06613857095465b070153b20f1c0223ee005265fdae`
  - `uptime_e4.png` `b1bd397033fde7e3a224a58031fcf83e645beef20f575cc63d11a071aaba575e`
- Hình 5.1–5.4 trong `docs/research/chapter5.md` dùng `image-25.png`…`image-28.png`.
  - Bốn ảnh này trùng byte lần lượt với `mttd_boxplot`, `mttr_comparison`, `uptime_e4` và `heal_success_rate`.
  - `mttd_comparison.png` không trùng ảnh nào trong bốn ảnh đó.

### B.3 File thử bị loại

Có một file thử được Git và nguồn chỉ tới. Nó được ghi riêng ở đây, không thuộc mẫu legacy và không được di chuyển.

| Mục | Giá trị |
| --- | --- |
| Path lịch sử | `docs/experiments/raw_data/e2_http_flood/results_20260712T100633.csv` |
| Git | Thêm ở `54ff513` (12/07/2026 20:19:45 +07:00, commit message về quota Prometheus/Grafana); xóa ở `0b402e4` (13/07/2026 13:13:24 +07:00, “remove temporary test results file to restore official 40-run dataset”) |
| Nội dung (blob `54ff513`) | SHA-256 `4ebed176e70fbd95ed518ead016db4206a1a8ec2984969c7b60d5ed9c9569e6a`, 1 bản ghi E2/AUTO/HTTP_FLOOD, `run_id` 1, `attack_start` 2026-07-12T10:06:30.140157+00:00 (17:06:30 +07:00), `uptime_percent` 0.0, `heal_status` SUCCESS, MTTD 1,03 s, MTTR 1,01 s |
| Bản sao trên đĩa | `scratch/results_20260712T100633.csv` (ignored bởi `.gitignore:44`), SHA-256 `b51ad9bbb3f0a03f517f3d2ef9be3ed2fad065cc771560257dfccbf3ada938f4`, CRLF; đổi CRLF→LF thì trùng byte blob Git. mtime 2026-07-12 17:06:33 +07:00, gần `attack_end` của lượt; mtime không phải bằng chứng |
| Nguồn ghi lý do | Commit message `0b402e4`; checkpoint repo `c191304` (13/07 13:22) ghi đã loại tệp test sang `scratch/` và chạy lại `analysis.py` |
| Cách dùng | Không thuộc 40 bản ghi legacy, không đưa vào pilot/formal. Ghi nhận là một lượt có uptime 0.0 bị loại khỏi thư mục dữ liệu; động cơ/người yêu cầu: UNKNOWN (L06) |

### B.4 Ba lớp thời gian

| Lớp | Nguồn | Mốc | Giới hạn |
| --- | --- | --- | --- |
| Dữ liệu ghi trong CSV | `attack_start` của 40 bản ghi | 2026-06-25 15:30:27–15:54:22 UTC = 22:30:27–22:54:22 +07:00. Thứ tự: E1 AUTO → E2 AUTO → E3 AUTO → E4 AUTO → E1 MANUAL → E2 MANUAL → E3 MANUAL → E4 MANUAL | Đồng hồ máy chạy runner và đồng hồ Hephaestus (nguồn `detect_time`) chưa được kiểm chứng; timestamp là giá trị được ghi, không phải log độc lập |
| Tên file | `results_YYYYMMDDTHHMMSS.csv` | Mỗi tên muộn hơn `attack_start` cuối của file 1–27 giây | Runner ở HEAD đặt tên theo `datetime.now(timezone.utc)` (runner:401). Đây là suy luận từ mã, không chứng minh thời điểm ghi file |
| Git | `git log` | Runner `2061837` 25/06 22:09:33; CSV + analysis `a179aad` 25/06 22:55:38; file thử thêm `54ff513` 12/07 20:19:45; hình Chương 5 `5597137` 13/07 13:05:57; xóa file thử `0b402e4` 13/07 13:13:24; checkpoint `c191304` 13/07 13:22:02 | Committer date do máy ghi |
| Analysis/chèn hình | Checkpoint `c191304` (`.agent/workflows/session_memory.md`); chapter5.md | Checkpoint ghi “chạy lại analysis” sau khi loại file thử; hình 5.1–5.4 chèn 13/07 | Output analysis trong Git không đổi từ 25/06. Nếu analysis có chạy lại ngày 13/07 thì đã cho ra bytes giống hệt (mtime 13:14 trên đĩa phù hợp nhưng không phải bằng chứng). Ảnh trong chương trùng PNG 25/06 |
| Báo cáo tự đánh giá | IDE S12 `evaluation_report.md`, metadata `updatedAt` 2026-07-02T13:37:17Z | Ngày 02/07 đã nêu “40 runs”, MTTD 25,6 s, MTTR khoảng 1,01 s | Tự đánh giá, không là log; nhưng cho thấy 40 lượt đã có trước 12–13/07 |

Không suy ngày thực thi hay chất lượng đồng hồ chỉ từ filename, mtime hoặc commit. Ba lớp trên nhất quán: 40 lượt được ghi ngày 25/06 và được commit vào Git khoảng 75 giây sau `attack_start` cuối. Ngày 12–13/07 chỉ có một lượt thử, việc xóa file thử và việc chèn hình.

### B.5 Đối chiếu các điểm H03

| Claim | Kiểm | Kết quả thực | Kết luận |
| --- | --- | --- | --- |
| Handoff: “40 files CSV” (L258), “1 file CSV 10 dòng” mỗi scenario (L314–318) | Đếm file/bản ghi | 8 file; mỗi file 5 bản ghi, một mode; mỗi scenario 2 file | Handoff sai; review H03 đúng |
| Handoff: chạy 40 runs ngày 12–13/07 (L138) | `attack_start`, Git, S12 | 40/40 ngày 25/06; Git 25/06; S12 ngày 02/07 đã báo 40 runs | Mâu thuẫn với nguồn trực tiếp. Lượt 12/07 là file thử 1 bản ghi |
| E3 AUTO “AUTO FAILED/MTTR” | Lọc E3/AUTO | 5 lượt: SUCCESS 1 (`run_id` 1), FAILED 4 (`run_id` 2–5), MTTR của FAILED: 1,01; 1,01; 1,02; 1,02 s. Summary: `heal_success_rate` 20.0, `mttr_mean` 1.01 gồm cả FAILED | FAILED vẫn có MTTR như thành công |
| 9,24 s là P95 hay max | MTTD E3 AUTO | Giá trị: 1,11; 1,12; 1,13; 1,14; 11,26; P95 nội suy tuyến tính 1,14 + 0,8 × (11,26 − 1,14) = 9,236 → 9,24 | 9,24 là P95, không phải max |
| “MTTD 1,13–9,24 s” trong bảng truy vết handoff (L317) | Min/max raw | Min 1,11, max 11,26 | Khoảng handoff sai cả hai đầu |
| Nguyên nhân 4 FAILED (race condition) | Tìm log tương ứng | Không có log runtime trong repo cho các lượt này | UNKNOWN |
| Cột timestamp đủ tính lại metric | `detect_time − attack_start − mttd_seconds`; `heal_end − detect_time − mttr_seconds` (AUTO) | Chênh lần lượt −3,254…+0,546 s và +0,373…+3,256 s; E4 lớn nhất | Không tính lại được MTTD/MTTR từ cột; xem L11 |
| Độ dài mỗi lượt khoảng 2 phút do cooldown 90 s (S12 dòng 35) | Khoảng `attack_start` | 40 `attack_start` trải 1.435,6 s (23 phút 55,6 giây); giữa hai lượt liên tiếp trong cùng file cách 17,7–44,1 s (32 khoảng) | Lý do “2 phút/lượt” trái với dữ liệu; số lượt là quyết định chưa có nguồn duyệt (L05) |

## C. Source ledger

### C.1 Loại nguồn và mức xác minh

**Loại nguồn:**

- `DOCX`: thuyết minh đăng ký.
- `HOANG`: xác nhận của Hoàng có vị trí lưu.
- `CODE`: mã hoặc cấu hình tại revision.
- `RAW`: CSV thô.
- `GIT`: metadata commit.
- `RUNLOG`: evidence runtime có thời điểm.
- `SELF`: báo cáo tự đánh giá, kế hoạch hoặc checkpoint trong repo/IDE.
- `IDE`: artifact, metadata hoặc transcript IDE.
- `RECALL`: hồi tưởng chat trong handoff Gemini.
- `INFER`: suy luận; ghi rõ của ai.

**Mức xác minh:**

- **TRỰC TIẾP:** Claude đọc hoặc tính trên nguồn sơ cấp trong gói này.
- **QUA TRÍCH:** qua bản trích hoặc evidence có hash/thời điểm do người khác lập; Claude kiểm hash hoặc vị trí.
- **GHI NHẬN:** nguồn có ghi câu đó, nhưng chưa chứng minh nội dung đúng.
- **MÂU THUẪN:** nguồn trực tiếp trái với claim.
- **UNKNOWN:** không có nguồn đủ để kết luận.

Nguồn tồn tại không làm claim bên trong đúng. Dòng trong handoff ghi theo revision `f9623a3` (464 dòng), khớp các vị trí review 09/10 trích. Bản hiện tại 467 dòng do thêm ghi chú công cụ ở `a224ce5`, nên lệch +2/+3 dòng. Review ghi “466 dòng”; bản nào được review không xác định được vì file chưa được track ở baseline review `6337b31`.

### C.2 Danh mục nguồn đã đọc

| ID | Nguồn | Loại · ngày | Truy cập trong gói | SHA-256 |
| --- | --- | --- | --- | --- |
| N01 | DOCX HĐ5 tại `C:\Users\ACER\Downloads\` (tên đầy đủ trong [bản trích](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md)) | DOCX · ngày ghi trên văn bản 04/01/2026; mtime file 29/01/2026 | Chỉ tính hash, không mở nội dung | `0faa8794f6b5175be94eb9f26db2a4a15a588a361fe25d33901d20ff241cd964` = hash trong bản trích |
| N02 | [Bản trích DOCX](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md) | DOCX qua trích Codex · 17/10 | Đọc toàn bộ | `819f5794f0887c2900e65d928bbd74cb44ffa668aa86de6db5a83dc93afa185d` |
| N03 | [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) | HOANG (Codex ghi) · 17/10 | Đọc toàn bộ | `f73c38d9e9658ddbdbf063ab4c94c80f90fce3faa7af4c448f157711fb4d51c2` |
| N04 | [Handoff Gemini](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md), bản `f9623a3` | RECALL/INFER/SELF · 09/10 | Các dòng H01–H08 trỏ tới | `3081a925efb5494acefe52bad39b91e9edb641e83b70629c17db0415138456ab` (bản hiện tại) |
| N05 | [Review H01–H08](R:/_Projects/Eurus_Workspace/zero_door/docs/reviews/2026-10-09-antigravity-handoff-review.md) | INFER Codex có kiểm nguồn · 09/10 | Đọc toàn bộ | `738a966acc04710a2c920e924159b220026682b959b0213a9a0a8bc8031514d4` |
| N06 | [audit-findings](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/audit-findings.md) | INFER Codex · 17–18/10 | Đọc toàn bộ | `45f3b142614feec13df2e00e4a0d864d0cc7e6eedb3f79fc54f18eb067e8eaa1` |
| N07 | Hydration/D8/blockers 17/10 (`docs/handoff/2026-10-17-claude-code-*.md`) | SELF Claude + review Codex · 17/10 | Mục được audit-findings dẫn (E6, C04, B01–B04) | Xem D.3 |
| N08 | 8 raw CSV, summary, 5 PNG | RAW / dẫn xuất · 25/06 | Parse/hash toàn bộ | Mục B |
| N09 | [Runner](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/experiment_runner_direct.py), [analysis](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/analysis.py), [Hephaestus](R:/_Projects/Eurus_Workspace/zero_door/agent-orchestrator/hephaestus/main.py), [cpu_stress.go](R:/_Projects/Eurus_Workspace/zero_door/chaos-worker/internal/attack/cpu_stress.go) | CODE · HEAD | Đoạn liên quan | Mục A.3 |
| N10 | Git history (`git log/show/ls-files/cat-file`) | GIT | Chỉ đọc | — |
| N11 | IDE S12 `evaluation_report.md` | SELF/IDE · `updatedAt` 2026-07-02T13:37:17Z | Đọc đầu file, bảng Phase 5, mục 1–2 và kết luận RQ | `d57fc4b18c3de08de92514884668ea6eb540a68ee5beab30284a9a247bbc516f` |
| N12 | IDE S13 `implementation_plan.md` | SELF/IDE · `updatedAt` 2026-07-11T13:48:18Z | Đọc dòng 1–12, 80–95 và vị trí mục | `e00367cfa94a0709733a5233d126b2444983bcce51ab43f57738ac343fc8fcb8` |
| N13 | IDE S14 `demo_script.md` | SELF/IDE · `updatedAt` 2026-07-02T13:48:51Z; mtime 03/07 22:02 | Chỉ metadata, hash | `8dafbe96d1e93214a4d14783baf1eeb21dbc8ef8b6fee431417810a157f3fc97` |
| N14 | IDE `.system_generated/logs/transcript.jsonl` | IDE · 2026-10-09T04:37:58Z–04:50:25Z | Cấu trúc 134 mục; đọc mục CHECKPOINT | `b0bebbdc70d0ade951e4560b65aa1cd7351ff8165d5c339996a571d376d2bec4` |
| N15 | [Checkpoint repo](R:/_Projects/Eurus_Workspace/zero_door/.agent/workflows/session_memory.md) qua diff `c191304`; [chapter5](R:/_Projects/Eurus_Workspace/zero_door/docs/research/chapter5.md) | SELF · 13/07 | Đoạn liên quan | Xem D.3 |
| N16 | Evidence đã lưu [ZER-35](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md), [ZER-34](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T02-S01/inventory.md) | RUNLOG · 18/10 | Chỉ mốc HEAD/node | Không gọi lại lab |

Đường dẫn IDE đầy đủ: `C:\Users\ACER\.gemini\antigravity-ide\brain\fd2083c0-a9f6-4ab7-a9fc-2cb3ffcbc375\`. Đây là artifact và metadata IDE, không phải chat gốc.

### C.3 Ledger

| ID | Claim | Nguồn, vị trí | Loại · ngày | Trực tiếp? | Mức xác minh | Mâu thuẫn / UNKNOWN | Cách dùng | H |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L01 | Thời gian thực hiện “Từ tháng 01 năm 2026 đến tháng 06 năm 2026”, 6 tháng; văn bản ghi ngày 04/01/2026 | N02 P35, P55–P56; N01 hash | DOCX · 04/01/2026 | Codex trích; Claude chưa đọc nội dung DOCX | QUA TRÍCH; hash DOCX khớp | Khác L02. Ngày trên văn bản không chứng minh ngày ký/nộp/duyệt | Ghi nguyên văn nguồn; không suy ra có hay không có gia hạn | H02 |
| L02 | Hạn hoàn thành 31/12/2026 | N03 “Nguồn thời hạn”; N04 L37 (gắn USER_CONFIRMED, S01, S04) và L443 (dẫn file HĐ5 làm nguồn) | HOANG · ghi nhận 09/10 và 17/10 | Hoàng nói với Codex | GHI NHẬN | N04 L443 gán nhầm mốc này cho DOCX; DOCX ghi 01–06/2026. Hồ sơ gia hạn: UNKNOWN | Dùng để điều phối; đối chiếu hồ sơ tại R7-T02-S05 | H02 |
| L03 | Đề cương nội bộ ghi 06 tháng (01/2026–06/2026) | `docs/archive/planning/research-plan.md:21`; trước đây `docs/plan_original_v3.md:21`, cùng SHA-256 `a8e823fc…b560b9` | SELF · 01/06/2026 (commit `f780031`) | Trực tiếp | TRỰC TIẾP | Path trong review đã đổi sau `1f43ff1` (organization.json:61) | Nguồn phụ cùng chiều với L01 | H02, H08 |
| L04 | Đổi Java/Spring sang Python/Go được thầy cho phép; Online Boutique được đề xuất từ đầu | N03; N04 L42, L133, DEC-01/02 L149–150 | HOANG · 17/10; RECALL | Hoàng nói với Codex | GHI NHẬN | N04 ghi “Gemini đề xuất, Hoàng & Thầy chốt”; vai trò Gemini đề xuất: UNKNOWN. Văn bản của thầy: UNKNOWN | Giữ quyết định theo SCOPE; không dựa vào claim RAM (L21) | H01, H07 |
| L05 | Giảm 120 xuống 40 runs: “Gemini đề xuất, Hoàng duyệt” | N04 L135, DEC-08 L156; N11 dòng 31–36 | RECALL; SELF · 02/07 | Không có chat | GHI NHẬN (S12 có lý do) | Lời duyệt của Hoàng: UNKNOWN. Lý do “mỗi lượt khoảng 2 phút” mâu thuẫn dữ liệu (B.5) | Ghi là quyết định quy mô cũ có lý do tự báo cáo; không dùng làm thiết kế mẫu mới | H01, H03 |
| L06 | Chuyển file thử vào scratch “để khớp” bản thảo; “theo yêu cầu khớp số liệu của Hoàng” | N04 L138, L307–308; Git `54ff513`, `0b402e4`; N15 `c191304`; N14 CHECKPOINT | GIT/SELF · 12–13/07; RECALL · 09/10 | Sự kiện: trực tiếp. Lời yêu cầu: không có chat | Sự kiện TRỰC TIẾP; động cơ UNKNOWN | Danh sách yêu cầu IDE (do IDE tóm tắt, cắt cụt, không ngày) có yêu cầu kiểm hình/số liệu Chương 5 và chạy lại. Trong phần đọc được, không thấy yêu cầu loại file để khớp số; phần bị cắt cụt chưa đọc được. Không đủ để quy động cơ | Chỉ ghi sự kiện và lý do commit/checkpoint đã ghi; không quy động cơ cho ai | H01, H03 |
| L07 | Bộ dữ liệu legacy 8 CSV/40 bản ghi, 5/file | N08 | RAW · 25/06 | Trực tiếp | TRỰC TIẾP | Mâu thuẫn N04 L258 (“40 files”) và L314–318 (“1 file 10 dòng”) | Inventory chuẩn cho legacy; không trộn vào pilot/formal | H03 |
| L08 | 40 lượt chạy ngày 12–13/07 | N04 L138 | RECALL · 09/10 | Không | MÂU THUẪN | `attack_start` 40/40 ngày 25/06; Git `a179aad` 25/06; S12 02/07 đã báo 40 runs. Chất lượng đồng hồ: UNKNOWN | Dùng ngày ghi trong dữ liệu (25/06) kèm giới hạn đồng hồ | H03 |
| L09 | Analysis chạy lại 13/07 và hình Chương 5 chèn sau đó | N15 `c191304`; `5597137`; hash PNG/ảnh chương | SELF/GIT · 13/07 | Trực tiếp với Git/hash | Chèn hình: TRỰC TIẾP. Chạy lại: GHI NHẬN | Output trong Git không đổi từ 25/06; ảnh chương trùng PNG 25/06; hình được commit trước khi xóa file thử 7 phút | Hình Chương 5 là sản phẩm của bộ 40 bản ghi 25/06; không dùng làm bằng chứng phục hồi | H03 |
| L10 | E3 AUTO thành công 1/5 (20%); thất bại do race condition với ReplicaSet | N08; N04 L317 | RAW · 25/06; RECALL | Tỷ lệ trực tiếp | Tỷ lệ TRỰC TIẾP; nguyên nhân UNKNOWN | Không có log từng lượt | Giữ tỷ lệ; nguyên nhân là giả thuyết | H03, H04 |
| L11 | MTTR khoảng 1,01 s là thời gian hồi phục (S12 dòng 46: “nhanh hơn gấp hàng trăm lần”) hoặc “độ trễ K8s API” (handoff) | N11 dòng 46; runner:312–365 (t_detect khi thấy heal history hoặc replica tăng; kết thúc khi gặp SUCCESS/FAILED/PARTIAL; MANUAL `mttr=-1`); N08; N04 L49, L175–176, L284 | CODE · HEAD = `a179aad`; RAW | Trực tiếp | TRỰC TIẾP với mã; MÂU THUẪN với cả hai cách hiểu | Khoảng 1 s là khoảng giữa hai mốc runner quan sát; FAILED cũng kết thúc phép đo. Câu handoff “event có SUCCESS ngay từ đầu” không đúng với 4 FAILED. Cột timestamp lệch metric tới khoảng 3,3 s. Theo mã (suy luận của Claude): `detect_time` có thể là timestamp heal history (runner:323), `attack_start` là t0 trước khi inject, còn MTTD = thời điểm poll − t_inject (runner:364) | Không dùng làm MTTR nghiên cứu; định nghĩa mới theo ZER-32 | H04 |
| L12 | Hành động restart có vòng chờ pod tối đa 60 s | `agent-orchestrator/hephaestus/main.py:247` | CODE · HEAD | Trực tiếp | TRỰC TIẾP với mã | Hành vi lúc chạy tháng 6: UNKNOWN | Không diễn giải mọi action là trả API ngay | H04 |
| L13 | Uptime 100% dưới tấn công | Runner `measure_uptime()` (Prometheus `avg(up{namespace="target-app"}) or vector(1)`; lỗi thì trả 99.0); N08 (40/40 = 100.0); N11 dòng 47 (mục tiêu “≥ 99%”) | CODE; RAW; SELF | Trực tiếp | TRỰC TIẾP với mã/dữ liệu | Không phải uptime nghiệp vụ hay probe. S12 dùng ngưỡng ≥ 99% trong khi DOCX P108 là ≥ 99,9% | Không dùng làm KPI uptime; ngưỡng giữ 99,9% theo SCOPE/ZER-32 | H04, H07 |
| L14 | Analysis tính MANUAL là thành công; MANUAL không có người thao tác | `analysis.py:79`, `:100`; runner:355–358; N08 (20/20 MANUAL, `mttr=-1`) | CODE; RAW | Trực tiếp | TRỰC TIẾP | `heal_success_rate` MANUAL 100% là hệ quả quy tắc, không phải kết quả đối chứng | Không dùng nhóm MANUAL cũ làm đối chứng | H04, H07 |
| L15 | Deploy Droplet DigitalOcean 11/07, sau đó đã tắt | N12 dòng 89 (`ssh … "shutdown now"` trong mục “Quy trình sử dụng (sau khi xong)”), mục `[NEW]` dòng 52–72, Open Questions dòng 115, Verification Plan dòng 128; N04 L137, L261, L367, L455 | SELF/IDE · 11/07; RECALL | Plan: trực tiếp | GHI NHẬN | Dòng 89 là lệnh đề xuất, không phải log. Không có log deploy, shutdown hay ID tài nguyên. Cloud đã tắt chỉ theo thông tin Hoàng (N03) | Ghi “cloud cũ đã tắt theo Hoàng”; thời điểm, tài nguyên và thao tác: UNKNOWN | H05 |
| L16 | Phase 1–5 “ĐẠT YÊU CẦU”, MTTR “vượt SLA” | N11 dòng 1–18, 46–47; metadata summary | SELF/IDE · 02/07 | Trực tiếp với báo cáo | GHI NHẬN | Báo cáo tự đánh giá, không thay log deploy/probe/model | Chỉ dùng để hiểu nguồn các claim cũ | H05 |
| L17 | Nemesis “gọi được Gemini API qua failover loop”; LLM đang hoạt động | N04 L255; `agent-orchestrator/nemesis/main.py`; `nemesis-deployment.yaml` (provider gemini, key mẫu để trống) | RECALL; CODE | Mã: trực tiếp | GHI NHẬN | Không có run ID, model, request hay log trong nguồn đã đọc. Secret đã triển khai: không truy vấn | Có mã tích hợp ≠ đã chạy; chờ R0-T03 | H05 |
| L18 | Azure Student “chưa được thiết lập endpoint hay subscription” | N04 L373; N03 (khoảng 100 USD, chưa kiểm số dư/quyền model/quota/endpoint) | RECALL; HOANG | Không | GHI NHẬN | Câu handoff mạnh hơn nguồn: “chưa xác minh” khác “chưa thiết lập” | Dùng diễn đạt của SCOPE | H05 |
| L19 | Trạng thái lab 09/10: K3d container “exited” | N04 L64, L371; N06 snapshot 09/10 (API từ chối, truy vấn container không trả kết quả); N16 (18/10 13:16: 2 node Ready) | RECALL/INFER; RUNLOG | Không gọi lại lab | GHI NHẬN | “Exited” là suy luận. Trạng thái 09/10: UNKNOWN. Evidence 18/10 thay cho snapshot cũ nhưng không được truy vấn lại | Không dùng trạng thái lab cũ; gói này không kiểm runtime | H05, H06 |
| L20 | Script khôi phục: chạy `k3d cluster start` hoặc “tái tạo cluster sạch bằng rebuild-nemesis.ps1” | N04 L406; `git show 1f43ff1:rebuild-nemesis.ps1` (build no-cache, import, rollout Nemesis); `rebuild-nemesis.sh` HEAD (build/import/rollout); `infrastructure/scripts/lib/common.sh:147–163` (`zd_ensure_cluster`: start nếu có, create nếu chưa có), được gọi từ `setup-phase1.sh --component cluster`; `recreate-cluster.sh:17` xóa cluster trước khi gọi setup | CODE · `1f43ff1`/HEAD | Trực tiếp | MÂU THUẪN | `.ps1` không còn ở HEAD; script Nemesis không tạo cluster | Sau inventory và trong quyền vận hành đã có, tạo/start theo `bash infrastructure/scripts/setup-phase1.sh --component cluster`; `recreate-cluster.sh` là nhánh xóa dữ liệu, chỉ dùng khi có quyết định và quyền xóa riêng; ledger không cấp quyền chạy | H06 |
| L21 | RAM dưới 100 MB/agent, tổng 157 MB, giảm 88% | N11 dòng 29; `docs/research/chapter5.md:150`, `:153`; `chapter1.md:100`; `chapter6.md:9`; N04 L42 | SELF · 02/07–13/07 | Trực tiếp với văn bản | GHI NHẬN | Không có dữ liệu/log benchmark trong nguồn đã đọc; gói không tìm toàn repo | Claim cũ chưa xác minh; bỏ khỏi kết luận nếu không đo | H07 |
| L22 | Zero Door “tiến xa hơn” đề xuất AIOps của thầy, “đã thống nhất giữa Hoàng và Gemini” | N04 L139, L344; N14 CHECKPOINT (yêu cầu số 6–7: nhờ đánh giá đề xuất AIOps của thầy so với dự án; “vậy bạn nghĩ thế nào”) | RECALL; IDE · ngày yêu cầu không ghi | Câu hỏi có trong tóm tắt IDE | Câu hỏi: GHI NHẬN; sự đồng thuận: UNKNOWN | Tóm tắt IDE cho thấy có hỏi, không cho thấy đồng ý | Quan điểm cũ; RQ cần đối chứng | H01, H07 |
| L23 | CPU stress làm suy giảm target; hoặc “Boutique không hề bị suy giảm” | `chaos-worker/internal/attack/cpu_stress.go:51` (tạo pod `<service>-stress-<uuid>` riêng); N04 L329 | CODE · HEAD; RECALL | Mã trực tiếp | Pod riêng: TRỰC TIẾP; ảnh hưởng gián tiếp: UNKNOWN | Không có probe/tài nguyên đo | Chưa chứng minh stress tác động workload nghiệp vụ | H07 |
| L24 | Manifests ở `infrastructure/manifests/target-app/`, `kafka/`, `monitoring/` và `infrastructure/k8s/` | N04 L133, L166, L251–253; `git cat-file` | RECALL; GIT | Trực tiếp | MÂU THUẪN | Bốn path không tồn tại ở `6337b31`, HEAD hay worktree. File thật: `infrastructure/manifests/target-app.yaml`, `infrastructure/helm-values/kafka-values.yaml`, `infrastructure/helm-values/prometheus-values.yaml` | Dùng path thật trong mục A.3 | H08 |
| L25 | Nguồn IDE S12/S13/S14 tra được | Đường dẫn đầy đủ ở C.2; hash, mtime, metadata `updatedAt` | IDE | Trực tiếp | TRỰC TIẾP (tồn tại, hash, metadata) | Nội dung là artifact IDE (tự đánh giá/kế hoạch/kịch bản), không phải chat gốc. N04 L92–94 ghi ngày lập S12 02/07, S13 11/07, S14 03/07. S12/S13 khớp metadata `updatedAt`; S14 khớp mtime 03/07, còn metadata ghi 02/07 | Trích S12–S14 kèm nhãn SELF/IDE | H08, H05 |
| L26 | Transcript IDE chỉ giữ metadata giai đoạn step 6335–6470; mục CONVERSATION_HISTORY/CHECKPOINT không có nội dung chat cũ | N05 dòng 13; N14 | IDE · 09/10 04:37–04:50Z | Trực tiếp | TRỰC TIẾP; bổ sung chi tiết | Review đúng là không có chat gốc: 134 mục, step 6335–6470, 1 USER_INPUT (yêu cầu handoff), CONVERSATION_HISTORY không có `content`. Bổ sung: CHECKPOINT (step 6336) có 3.883 ký tự tóm tắt do IDE sinh, đánh dấu cắt cụt, liệt kê yêu cầu người dùng trước đó không kèm ngày | Tóm tắt IDE là loại IDE, không phải chat gốc; dùng để biết có câu hỏi nào được nêu, không dùng làm lời duyệt | H01, H08 |
| L27 | Alias `hp8001` là Nguyễn Ngọc Hòa | N04 L123; `README.md:105`, `:138`; `.agent/rules/PLAN.md:11`; `.github/copilot-instructions.md:20`; `docs/archive/planning/*` | RECALL; SELF | Trực tiếp với văn bản | UNKNOWN | Repo dùng `hp8001` như vai trò/tài khoản GitHub; không nguồn nào gắn alias với Hòa | Không đồng nhất; giữ alias nguyên văn | H08 |
| L28 | Nơi/đợt nhận bài kỷ yếu | N03; N04 L425–433 (đặt như câu hỏi tiếp nhận) | HOANG · 17/10 | Không | GHI NHẬN | Chưa có thông báo; Hoàng chốt sau | Theo dõi tại R6-T01-S03, không là blocker tiếp nhận | H08 |
| L29 | Runner/analysis ở HEAD là mã đã sinh dữ liệu | `git log` hai file: thêm/đổi cuối ở `2061837`/`a179aad`, 25/06; dữ liệu cùng `a179aad` | GIT/CODE | Trực tiếp | GHI NHẬN | Không có log chạy hoặc hash môi trường; mã chạy thực tế: UNKNOWN | Mô tả cơ chế là “mã được commit cùng dữ liệu”, không phải “mã đã chạy” | H04, H05 |
| L30 | Tên tác giả Git và người chạy thí nghiệm | Git `%an` = `LeganSar44` ở mọi commit liên quan | GIT | Trực tiếp | GHI NHẬN | Danh tính người chạy/người duyệt: UNKNOWN | Không quy trách nhiệm/lời duyệt từ metadata commit | H01, H08 |

### C.4 Bao phủ H01–H08

Downstream lấy theo [audit-findings](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/audit-findings.md); gói không tạo relation hay issue.

| H | Đã làm rõ bằng nguồn | Còn UNKNOWN | Mục ledger | Downstream đã map |
| --- | --- | --- | --- | --- |
| H01 — Ý định/lời duyệt | Sự kiện thêm/xóa file thử và lý do commit/checkpoint; tóm tắt IDE có hỏi kiểm hình và đánh giá AIOps | Lời duyệt 40 runs, đổi stack (vai trò Gemini), động cơ loại file thử, sự đồng thuận AIOps | L04–L06, L22, L26, L30 | R6-T01-S01 |
| H02 — Thời hạn | DOCX 01–06/2026 và ngày 04/01/2026 (qua trích, hash khớp); 31/12 là xác nhận Hoàng; handoff gán nhầm nguồn | Hồ sơ gia hạn/thẩm quyền; ngày ký/nộp | L01–L03 | R7-T02-S05 |
| H03 — Inventory/timeline | 8/40/5; ngày 25/06; ba lớp thời gian; E3 4 FAILED; P95 so với max; file thử 12/07 | Nguyên nhân FAILED; chất lượng đồng hồ | L05–L10 | R5-T03-S02 |
| H04 — MTTR/terminal status | Mốc đo và terminal status theo mã; FAILED kết thúc phép đo; MANUAL; cột lệch metric | Mã chạy thực tế; thời gian xử lý trong Hephaestus | L10–L14, L29 | R1-T01; R1-T02; R3-T01-S01 (đã định nghĩa mới ở ZER-32) |
| H05 — Runtime suy từ plan | S12 tự đánh giá, S13 kế hoạch; dòng 89 là lệnh đề xuất; cloud tắt theo Hoàng | Log deploy/shutdown/LLM; trạng thái lab 09/10 | L15–L19, L25 | R0-T02-S03; R0-T03-S02 |
| H06 — Phục hồi cluster | `.ps1` cũ và `.sh` hiện tại chỉ build/import/rollout Nemesis; tạo/start qua `setup-phase1.sh --component cluster` → `zd_ensure_cluster`; `recreate-cluster.sh` xóa trước khi dựng lại, cần quyền riêng | — trong phạm vi tài liệu; lựa chọn start/recreate theo inventory | L19–L20 | R0-T02-S01/S02 (ZER-34/35) |
| H07 — Claim chưa đối chứng | Vị trí claim RAM/88%/157 MB, AIOps, stress pod riêng, ngưỡng 99% trong S12 | Số đo RAM; ảnh hưởng gián tiếp stress | L13, L14, L21–L23 | R0-T04-S01; R4-T04; R6-T01-S01; R6-T02-S04 |
| H08 — Path/danh tính/nguồn | 4 path không tồn tại; path DOCX/plan/IDE đầy đủ; nhận định transcript được bổ sung | Danh tính `hp8001`; bản handoff được review 09/10 | L03, L24–L28, L30 | R5-T03-S03; R6-T01-S03 |

H01–H08 là đầu mục audit để ledger xử lý. Gói không tuyên bố đã đóng lỗi runtime/nghiên cứu nào hay sửa thay issue khác.

## D. Kiểm chứng và giới hạn

### D.1 AC → kiểm → kết quả

| AC (snapshot) | Kiểm | Expected | Actual | Verdict |
| --- | --- | --- | --- | --- |
| HEAD/dirty có thời điểm | Lệnh A.1 trước khi ghi; lặp lại ở D.4 | Branch/HEAD đầy đủ, staged/unstaged/untracked, hash dirty có sẵn | A.1; HEAD không đổi trong gói | ĐẠT |
| Cấu hình/pin có path, hash, revision | `ledger_check.py run` → `check_config` | Mỗi file tồn tại, có SHA-256, blob HEAD = worktree, commit cuối | 47/47 OK, sạch | ĐẠT (cấu hình Git; runtime chưa truy vấn) |
| Inventory legacy, hash/số dòng từng CSV | `check_raw` với manifest hash cố định | Không thiếu/thừa file, hash đúng, không lỗi parse, tổng nhất quán hai cách | 8 file, 48 dòng, 40 bản ghi, 0 lỗi; tổng khớp | ĐẠT |
| Summary tách riêng, không cộng vào raw | `check_summary` | Tính lại theo quy tắc `analysis.py` khớp, ghi là dẫn xuất | 8 nhóm, chênh tối đa 0,004 | ĐẠT |
| Timestamp dữ liệu tách timeline Git | B.4, `check_removed_test_file` | Ba lớp có nguồn; file thử tách riêng | B.3–B.4 | ĐẠT |
| Đối chiếu H03 bằng dữ liệu | `check_h03` | 5 lượt E3 AUTO, 4 FAILED, max 11,26, P95 9,24 | Đúng | ĐẠT |
| Ledger H01–H08, phân loại nguồn | C.1–C.4 | Mỗi H có mục ledger, loại nguồn, mức xác minh, UNKNOWN | 30 mục; H01–H08 đủ | ĐẠT |
| Kiểm path | `check_paths`, `links` | Path dẫn tồn tại; path sai được xác nhận không tồn tại | Xem D.2 | ĐẠT |
| Giữ raw/handoff | `snapshot` trước/sau + `compare` | 42 nguồn không đổi | Xem D.3 | ĐẠT |
| Thiếu lịch sử/danh tính là UNKNOWN | C.3–C.4 | Không gán động cơ, lời duyệt, danh tính | Ghi UNKNOWN | ĐẠT |
| AC sống | Đọc Linear | Đọc trực tiếp | Không đọc được trong phạm vi được phép (A.2) | Dùng snapshot; Codex đối chiếu |

### D.2 Cách tái lập

Chạy từ repo root bằng Git Bash, Python 3.12.4, chỉ dùng thư viện chuẩn:

```bash
python -I scratch/zer33/ledger_check.py selftest
```

```bash
python -I scratch/zer33/ledger_check.py run --snapshot scratch/zer33/snap-after.json
```

```bash
python -I scratch/zer33/ledger_check.py compare scratch/zer33/snap-before.json scratch/zer33/snap-after.json
```

```bash
python -I scratch/zer33/ledger_check.py links docs/evidence/R0-T01-S03/baseline-source-ledger.md
```

`run` in mỗi kiểm một dòng `OK`/`FAIL`/`INFO` và trả exit 1 nếu có FAIL. Các bảng A.3, B.1 và D.3 được sinh từ `snap-before.json` bằng `scratch/zer33/render.py`, không chép tay.

**Selftest:** dữ liệu giả trong bộ nhớ và một repo Git tạm, không đụng repo thật. Script phải bắt được:

- Cột thừa.
- Header sai.
- Bytes không phải UTF-8.
- Ô số không hợp lệ.
- Trường quoted multiline (đếm 1 bản ghi dù có 3 dòng vật lý).
- Hàng rỗng.
- Giá trị `TIMEOUT`.
- Thiếu file và sai hash so với manifest.

**Kiểm path:** gồm 36 path tồn tại trên đĩa (repo, IDE, DOCX) và 6 path phải vắng: 4 path manifests/k8s cũ ở HEAD lẫn `6337b31`, cùng `rebuild-nemesis.ps1` và `docs/plan_original_v3.md` ở HEAD. Thêm 5 object Git ở revision cũ.

Lần chạy đầu bắt được 3 FAIL thật và đã sửa trong gói:

1. Khóa `(scenario, run_id)` báo trùng: đúng là `run_id` lặp giữa AUTO và MANUAL, nên khóa duy nhất được đổi thành `(scenario, mode, run_id)` và việc lặp được ghi INFO.
2. `docs/plan_original_v3.md` đã chuyển sang `docs/archive/planning/research-plan.md`.
3. `rebuild-nemesis.ps1` vẫn có ở `6337b31`; kiểm được tách thành “vắng ở HEAD” và “có ở revision cũ”.

Selftest lần đầu cũng crash ở ô số không hợp lệ; đã thêm guard.

**Kết quả kiểm cuối** (18/10/2026 23:27–23:29 +07:00; `ledger_check.py` SHA-256 `9a116a1c7f56af03978f052286feee4c5316a08cd13644c2be750d3c942148e2`; `render.py` `e66511859877490e52140425838573178d9cd3c680c03ff729f86774cba9aa9c`):

| Kiểm | Kết quả | Exit |
| --- | --- | --- |
| `selftest` | 10 OK, 0 FAIL; guard manifest bắt 4 lỗi cố ý | 0 |
| `run` | 128 OK, 0 FAIL, 24 INFO: 30 kiểm raw, 1 summary, 2 H03, 1 file thử, 47 cấu hình, 47 path/object | 0 |
| `compare` trước/sau | 42/42 nguồn không đổi | 0 |
| `links` artifact | 16/16 link nội bộ tồn tại | 0 |
| Bảng Markdown | 0 hàng lệch số cột | — |
| `git diff --check` và `git diff --no-index --check` cho file mới | Sạch | 0 |

### D.3 Bảo toàn nguồn

42 nguồn được hash trước (`snap-before.json`, 18/10 23:18:42 +07:00) và sau khi viết xong:

- raw CSV, summary, PNG và file thử trong scratch;
- 7 handoff, 2 review, audit-findings, SCOPE, WORKFLOW, WORKING-AGREEMENT, README delivery, AGENTS;
- artifact và review ZER-32;
- chapter5, session_memory;
- 7 file IDE và DOCX.

Không sửa nguồn nào. Transcript IDE nằm ngoài repo và có thể đổi nếu IDE được dùng tiếp; nếu đổi, chỉ L26 bị ảnh hưởng.

| Nguồn | SHA-256 trước |
| --- | --- |
| `docs/experiments/raw_data/e1_cpu_stress/results_20260625T153348.csv` | `d6188213c2bac6c137fad74cfdd375ef8e9413caf87434ab6eb9917a404a30a7` |
| `docs/experiments/raw_data/e1_cpu_stress/results_20260625T154933.csv` | `624df7c3cc9e4187b1f5a6b45bb51b18acfe8291ee8313f0872d16243a75ac52` |
| `docs/experiments/raw_data/e2_http_flood/results_20260625T153523.csv` | `8ce7945c4a2aa066c32714392d5feaba3ce32880aba27bd31f8de1a7e4db809c` |
| `docs/experiments/raw_data/e2_http_flood/results_20260625T155104.csv` | `6e6003b9846ec726397caa1b05726f9d153ecd2df3b308bb928424d4b694beeb` |
| `docs/experiments/raw_data/e3_pod_kill/results_20260625T154325.csv` | `1c33a45c71ea6368a7a65362f16e4be3d61d57c7ce90caa9820b86e6122d2611` |
| `docs/experiments/raw_data/e3_pod_kill/results_20260625T155238.csv` | `acb392a526e3f8bf89dcc9bb123762a3ef742976d2f458b1467db564cafc4b88` |
| `docs/experiments/raw_data/e4_combined/results_20260625T154540.csv` | `596f880294474677572ef454ccf72b2d553ccffae3ccf1096b3282b5bb902df1` |
| `docs/experiments/raw_data/e4_combined/results_20260625T155428.csv` | `7e02266c2862433459950c7845a8cd73af65cdbb19a65c691da6c540bab98020` |
| `docs/experiments/analysis/summary_statistics.csv` | `bfb2bb33f63896e1f4b65ab1a4d4e5e860bc82e1246363744365301519662ad5` |
| `docs/experiments/analysis/heal_success_rate.png` | `ed7d01790746b6c300fd20e16153722c2784342ef2ca0d61dbd532e3db524ee7` |
| `docs/experiments/analysis/mttd_boxplot.png` | `040b45e4b86f79b49202790b021c3843b704fc41227fe8c7f08c3d4db2f01948` |
| `docs/experiments/analysis/mttd_comparison.png` | `72d9ef0028e6a22a6e064b9d57398cac24141a019f1059d3e9ca5888694491a8` |
| `docs/experiments/analysis/mttr_comparison.png` | `4b033e4118fc99cfd130c06613857095465b070153b20f1c0223ee005265fdae` |
| `docs/experiments/analysis/uptime_e4.png` | `b1bd397033fde7e3a224a58031fcf83e645beef20f575cc63d11a071aaba575e` |
| `scratch/results_20260712T100633.csv` | `b51ad9bbb3f0a03f517f3d2ef9be3ed2fad065cc771560257dfccbf3ada938f4` |
| `docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md` | `3081a925efb5494acefe52bad39b91e9edb641e83b70629c17db0415138456ab` |
| `docs/handoff/2026-10-09-antigravity-gemini-handoff-request.md` | `aa8bec7ad030cdd3b8636c9c4dd7b9314da93924add2404ef40e3b5997e7e909` |
| `docs/handoff/2026-10-17-claude-code-hydration-d8.md` | `810ecb6b44d18a750673977a542a59e5a1038f7eaf920bb265ef5791827c10e2` |
| `docs/handoff/2026-10-17-claude-code-hydration-handoff.md` | `6fc645fdfb9eef328198a6e27e9138a89e8d22994564afaa3b8d6d6aa9f56254` |
| `docs/handoff/2026-10-17-claude-code-session-blockers.md` | `7ea2f50d9889e944a1a8eb028edc907b994487b1e6944939b528ae02dc7e9e21` |
| `docs/handoff/2026-10-17-registration-requirements-excerpt.md` | `819f5794f0887c2900e65d928bbd74cb44ffa668aa86de6db5a83dc93afa185d` |
| `docs/handoff/claude-lab-review-and-sizing.md` | `d0dc2b76b5b8ef189af87aca0c796c86ce17cce90de0b0886dc94c95daec0bb3` |
| `docs/reviews/2026-10-09-antigravity-handoff-review.md` | `738a966acc04710a2c920e924159b220026682b959b0213a9a0a8bc8031514d4` |
| `docs/reviews/2026-10-09-research-alignment-audit.md` | `acb930e54505c3ec4e52855a432deff212b6c3bb3d1bb2c40ae190e0365305e8` |
| `docs/delivery/reference/audit-findings.md` | `45f3b142614feec13df2e00e4a0d864d0cc7e6eedb3f79fc54f18eb067e8eaa1` |
| `docs/delivery/SCOPE.md` | `f73c38d9e9658ddbdbf063ab4c94c80f90fce3faa7af4c448f157711fb4d51c2` |
| `docs/delivery/WORKFLOW.md` | `ded0fdee2473ce8cac32f994f4139ee59e241e13fc48528b0fe42c026ef15ffb` |
| `docs/delivery/WORKING-AGREEMENT.md` | `fc34c9ae5fc3f6edfd1197c79b5bee380c0b9ec1b3a365df363405084264bc87` |
| `docs/delivery/README.md` | `c7b9f0f8673359cce4be9d3bb0a4517925060b4b98345de1d8f5edc3f0a220b4` |
| `AGENTS.md` | `fe18d0003c865a021eb7eb8a2432ea290b034deec5cad3cb5c1cd338be88d50e` |
| `docs/evidence/ZER-32/requirements-and-kpi.md` | `a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c` |
| `docs/evidence/ZER-32/codex-review.md` | `f7c2454e79b8c22d773a3c800abf1778e4be2ef408e886fc902757027098bb16` |
| `docs/research/chapter5.md` | `160bf77ac20c98b0f7b88cd7f7e1cd26343d3d52bb599b0a176dde97674b9a9e` |
| `.agent/workflows/session_memory.md` | `3cc016c7d09fd485153cf39488bc6d363e3bed492d23d704054f9c1a067afa56` |
| `IDE/evaluation_report.md` | `d57fc4b18c3de08de92514884668ea6eb540a68ee5beab30284a9a247bbc516f` |
| `IDE/implementation_plan.md` | `e00367cfa94a0709733a5233d126b2444983bcce51ab43f57738ac343fc8fcb8` |
| `IDE/demo_script.md` | `8dafbe96d1e93214a4d14783baf1eeb21dbc8ef8b6fee431417810a157f3fc97` |
| `IDE/evaluation_report.md.metadata.json` | `6b150880a3387e39a69326bb4087f902cf33a3b085cb4780fc57c33a8c532966` |
| `IDE/implementation_plan.md.metadata.json` | `38b23291a7f8ff71e645d0297a0511f4e7e8833a26e4cbd90982411c240ba200` |
| `IDE/demo_script.md.metadata.json` | `3db7a3c0e534224ba9cfebd8ec775c21bd439dbd8d2a04b0a0e8f92aeaa24b93` |
| `IDE/.system_generated/logs/transcript.jsonl` | `b0bebbdc70d0ade951e4560b65aa1cd7351ff8165d5c339996a571d376d2bec4` |
| `DOCX HĐ5 (Downloads, chỉ hash)` | `0faa8794f6b5175be94eb9f26db2a4a15a588a361fe25d33901d20ff241cd964` |

### D.4 Allowlist, diff và trạng thái cuối

Kiểm sau khi nối bàn giao và sửa NOW, lúc 23:29 +07:00:

| Kiểm | Expected | Actual |
| --- | --- | --- |
| HEAD / staged | `8e7b74f…`, staged rỗng | Giữ nguyên; staged rỗng |
| `git status --porcelain=v1 -uall` | Baseline + đúng 1 file mới | 5 M + `WORKING-AGREEMENT.md` ?? như baseline; thêm `docs/evidence/R0-T01-S03/baseline-source-ledger.md` ?? |
| Dirty ngoài phạm vi | Hash = A.1 | `AGENTS.md`, `docs/delivery/README.md`, `docs/delivery/WORKFLOW.md`, `docs/delivery/WORKING-AGREEMENT.md` đúng hash A.1 |
| Ghi chú issue | Chỉ nối cuối | 42.043 byte đầu trùng byte bản lúc bắt đầu (bản sao `scratch/zer33/base/`); chỉ thêm mục “Bàn giao Claude — ZER-33” |
| `NOW.md` | Chỉ con trỏ đầu | `diff` với bản lúc bắt đầu: 1 dòng tiêu đề đổi giờ, thêm 1 đoạn và 3 gạch đầu dòng ngay dưới tiêu đề; phần còn lại giữ nguyên |
| Ngoài repo | Chỉ `scratch/zer33/` | `scratch/` ignored bởi `.gitignore:44` |
| Line ending | LF như file gốc | Cả 3 file LF, không CRLF |

Artifact không tự chứa SHA-256 của chính nó. SHA cuối của artifact, ghi chú issue và `NOW.md` nằm trong mục bàn giao ở ghi chú issue.

### D.5 Giới hạn và N/A

- Không đọc AC sống. Claude chưa trực tiếp đọc nội dung DOCX: “Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX.” Claude chỉ kiểm hash file DOCX.
- Không truy vấn Docker/Kubernetes, cloud hay model; cấu hình đã triển khai, trạng thái lab và Secret: chưa kiểm. Evidence ZER-34/35 chỉ được dẫn như bằng chứng đã lưu.
- Không chạy runner/analysis, không sinh lại biểu đồ, không cài dependency. Summary được kiểm bằng phép tính thư viện chuẩn mô phỏng quy tắc analysis, không phải chạy pandas.
- Không tìm toàn repo hoặc toàn ổ C để tìm benchmark RAM, log cũ hay chat. Không thấy bằng chứng trong nguồn đã đọc thì ghi UNKNOWN, không kết luận “không tồn tại”.
- Đọc transcript IDE giới hạn ở cấu trúc và mục CHECKPOINT; không trích nội dung riêng tư ngoài các yêu cầu liên quan H01/H07.
- Build/test ứng dụng, CI, runtime, model, cloud: N/A vì gói chỉ tạo tài liệu. N/A không phải KPI PASS.

## E. Bước tiếp theo

- **Codex review:** đọc toàn ledger, kiểm lại inventory/hash/timeline/attribution, chạy lại 4 lệnh D.2 và đối chiếu AC sống ZER-33/ZER-5.
- **Khoảng trống cần Hoàng chỉ khi muốn đóng UNKNOWN:** chat gốc tháng 01–07, hồ sơ gia hạn, danh tính `hp8001`, log cloud/LLM. Thiếu các nguồn này không chặn AC.
- Không tự đóng ZER-33/ZER-5, không đổi Linear.
