# ZER-34 và ZER-6 — Claude review độc lập inventory và đối chiếu nghiệm thu lab

**Kết luận:**
- **ZER-34:** inventory đạt AC-01–AC-05; không có lỗi số liệu hay khẳng định sai, nên không cần đính chính. AC-06 còn **pending**. Inventory đã nằm trên `main` công khai, nhưng chính báo cáo review này mới ở checkout local, chưa được Codex review và chưa được duyệt chia sẻ.
- **ZER-6:** cả ba AC **đạt về kỹ thuật** dựa trên bằng chứng lịch sử của ZER-35 ngày 18/10.
  - AC-01 phụ thuộc việc nghiệm thu ZER-34.
  - AC-02: sau kiểm bổ sung của Codex lúc 00:42 ngày 19/10, cả 5 container và 5 volume có sẵn vẫn hiện diện. Nhánh create/start tự động vẫn chỉ có mock; đây là giới hạn coverage, không phải yêu cầu phải xóa/dựng lại lab để đạt AC (xem mục 9).
  - AC-03 đủ năm tiêu chí trong raw cuối.
- Không có finding chặn. Không tự đóng issue nào. G0 và R0 không được chốt từ gói này.

Người thực hiện: Claude Code. Người review: Codex. Người nghiệm thu: Hoàng. Phạm vi: mục "Gói Claude — ZER-34 và đối chiếu nghiệm thu ZER-6 — 19/10/2026, 00:06 +07:00" trong [ghi chú local-lab](../../delivery/milestones/R0-foundations/local-lab.md). Thời gian: 19/10/2026, 00:11–00:22 +07:00.

## 1. Baseline, quyền và giới hạn đọc

- **Git:** branch `zer-33-baseline-source-ledger`, HEAD `10a26b0a0001046b23f57f667a3cb7be33e69090` (bằng upstream `origin/zer-33-baseline-source-ledger`). Staged rỗng lúc 00:11:04.
- **Dirty có sẵn, giữ nguyên:** ` M` AGENTS.md, docs/delivery/NOW.md, docs/delivery/README.md, docs/delivery/WORKFLOW.md, docs/delivery/milestones/R0-foundations/local-lab.md; `??` docs/delivery/WORKING-AGREEMENT.md.
- **Nhánh:** không tạo `zer-34-lab-acceptance`. Gói chỉ cho phép tạo nhánh khi cần, và gói này không commit. Đổi nhánh là thao tác checkout mà gói không đòi hỏi. Nhánh nên được tạo ở bước publication, từ đúng HEAD đã kiểm.
- **Linear chưa đọc live.** Phiên Claude không có kết nối `linear_zero_door`. Connector Linear khác trỏ workspace khác nên không dùng. AC được lấy theo snapshot trong gói (Codex đọc live đầu ngày 19/10: ZER-34 và ZER-6 In Progress, ZER-35 Done) và theo snapshot ZER-6 AC-03 trong [handoff ZER-35](../../handoff/claude-lab-review-and-sizing.md), dòng 61–64. Codex cần đối chiếu từng verdict dưới đây với AC sống.
- **Thao tác:** chỉ đọc source, config, Git, evidence và raw trong `scratch/zer35-*`, cùng truy vấn GitHub chỉ đọc (`gh pr view`, `gh api`, `git ls-remote`).
  - Không chạy Docker, kubectl hay script lab, kể cả lệnh chỉ đọc, vì gói giới hạn nguồn đọc ở source/config/Git/evidence.
  - Không start/stop/recreate/build/rollout, không chạy `verify-local-lab.sh`, không đọc Secret, không gọi LLM.
  - Không commit/push/PR/merge, không đổi Linear, không gửi tin.
- **Phạm vi ghi:** báo cáo này; mục kết luận nối cuối ghi chú local-lab; con trỏ đầu NOW.md; dữ liệu kiểm tạm ở `scratch/zer34/` (đã gitignore). Inventory không cần đính chính nên giữ nguyên.

## 2. Receipt publication ZER-35 (kiểm lại)

| Mục | Nguồn kiểm | Kết quả |
| --- | --- | --- |
| PR #19 | `gh pr view 19 --repo EurusDevSec/Zero-Door` | `MERGED` lúc 2026-10-18T14:02:48Z (21:02:48 +07:00). Head `codex/zer-35-local-lab` = `a224ce54fc0e742bbb647c61e6e9201094a9de25`; merge commit `5471b587b57dec53c3847aba9ae898d0f9fca956`; base `main` |
| CI của PR | `statusCheckRollup` | 7 job `SUCCESS` (Bash syntax và CLI tests, Helm lint, build ba agent, build chaos worker, scan manifest); job publish image `SKIPPED` |
| Merge commit | `git log -1 5471b58` | Parents `1f43ff1` và `a224ce5`; tác giả GitHub của Hoàng (`EurusDevSec`); cây giống hệt `a224ce5` (`git diff a224ce5 5471b58` rỗng) |
| Remote | `git ls-remote origin`, khoảng 00:12 | `refs/heads/main` = `5471b58…`; `refs/pull/19/head` = `a224ce5…`; nhánh ZER-33 = `10a26b0…` |
| Repo | `gh repo view` | `PUBLIC`, default branch `main` |
| Inventory trên remote | `gh api …/contents/docs/evidence/R0-T02-S01/inventory.md?ref=main` | Blob `a2dd9cc22a644ba6bde68421ff9f3269e04ccc17`, bằng blob trong `a224ce5`, `10a26b0` và `git hash-object` của file local |
| Mã đã review = mã đã merge | Gộp ledger `scratch/zer35-final/final-file-ledger.json` và `scratch/zer35-cl-final/final-file-ledger.json` (bản Claude review PASS lúc 20:50), so với working tree | 20/20 mục ledger khớp: 19 file mã, test và runbook trùng SHA-256; `target-app-monitor.yaml` vắng đúng như ledger ghi. `git status` sạch trên các đường dẫn đó; `git diff a224ce5 HEAD` trên infrastructure/tests/agent-orchestrator/.github/runbooks rỗng |

Receipt merge đã được xác minh trực tiếp. Câu "chờ merge" trong các đoạn bàn giao lịch sử chỉ là trạng thái tại thời điểm viết, không phủ nhận receipt này. ZER-35 Done trên Linear là theo lần đọc của Codex; Claude chưa đọc lại được. Child Done không làm parent ZER-6 tự đạt.

## 3. ZER-34 — review inventory

Đối tượng: [inventory.md](../R0-T02-S01/inventory.md), SHA-256 `fcbabf54001d5e3f6f56984f07d0a65e97d03b7108dfb4f4003c7d5f240cd030`, 133 dòng, được thêm ở `a224ce5`. Chưa có commit nào sửa file sau đó. Các lệnh PowerShell trong inventory là provenance lịch sử; review này không chạy lại.

### 3.1 Khẳng định tĩnh đối chiếu revision `1f43ff1`

| Dòng inventory | Khẳng định | Nguồn tại `1f43ff1` | Kết quả |
| --- | --- | --- | --- |
| 42 | k3d 1 server + 1 agent, tắt Traefik, không có giới hạn RAM theo node | `infrastructure/k3d-config.yaml`: `servers: 1`, `agents: 1`, `--disable=traefik`; không có khóa memory | Khớp |
| 43 | Prometheus: Alertmanager off, scrape/evaluation 30s, retention 3d, request 512Mi/limit 1Gi; Grafana 256Mi/512Mi; chú thích ~800MB | `prometheus-values.yaml` dòng 4, 19, 32–42, 54–59, 72–73 | Khớp. 512Mi/1Gi thuộc `prometheusSpec.resources`, không nhầm với storage 2Gi |
| 44 | Kafka 1 controller, 0 broker, 256Mi/768Mi | `kafka-values.yaml` dòng 23–39 | Khớp |
| 45 | Elasticsearch 1 replica, Xms256m/Xmx512m, 512Mi/1Gi | `logging/elasticsearch.yaml` dòng 17, 38, 47, 50 | Khớp |
| 46 | Tổng request 1536Mi, tổng limit 3328Mi | 512+256+256+512; 1024+512+768+1024 | Khớp |
| 47 | Quota monitoring requests.memory 6Gi, limits.memory 10Gi | `resource-quotas/monitoring-quota.yaml` dòng 15, 17 | Khớp |
| 48 | Loadgenerator 1 replica trong `target-app-raw.yaml` | Deployment `loadgenerator`, `replicas: 1` | Khớp |
| 49 | HPA frontend/cartservice 1–3 | `target-app-hpa.yaml` dòng 11–12, 31–32 | Khớp |
| 55 | `start-demo.ps1` không tạo cluster, chỉ mở port-forward và dừng mọi kubectl | `start-demo.ps1` (gốc repo) dòng 12–20 chỉ kiểm node; 30–32 `Get-Process kubectl \| Stop-Process`; 43–55 `port-forward` | Khớp |
| 57 | setup-phase1 không pin chart Prometheus/Ingress; phase3 có `go mod tidy`; runbook legacy có phần E | `setup-phase1.ps1` dòng 147–150 và 174–177 không có `--version` (Kafka có `29.3.2`); `setup-phase3.ps1` dòng 54–58; runbook 2026-10-09 dòng 171 | Khớp |
| 19, 53 | 15,78 GiB; trống 4,55; dùng 11,23; khoảng 71% | 15,78 − 4,55 = 11,23; 11,23/15,78 = 71,2% | Khớp số học |
| 85, 113–118 | `MemTotal` 7271460864 B = 6,77 GiB; bảng `/proc/meminfo` | 7101036 KiB × 1024 = 7271460864; các cột GiB làm tròn đúng | Khớp số học |
| 100–101, 125 | Windows còn trống 1,5–1,7 GiB | Mẫu 1,49 / 1,66 / 1,63 / 1,62 | Khớp |

Số đo host, Docker và WSL của ngày 18/10 không thể đo lại. Review chỉ kiểm tính nhất quán nội tại và đối chiếu với các ghi chú cùng thời điểm (local-lab dòng 47 và 53). Không phát hiện mâu thuẫn.

### 3.2 AC → kỳ vọng → thực tế → verdict

| AC | Kỳ vọng (theo gói) | Thực tế trong inventory | Verdict |
| --- | --- | --- | --- |
| AC-01 | Branch, HEAD, dirty, thời điểm/timezone, lệnh thực tế | Dòng 5, 9–11: Asia/Saigon, `main`, `1f43ff1…`, status rỗng. Từng lệnh có giờ và exit (dòng 19–30, 80–94). Dòng 76: trạng thái dirty của lượt 09:45 | **PASS** |
| AC-02 | Context, container, volume, port, resource, exit/lỗi/timeout; tách mẫu Engine tắt 09:37 khỏi mẫu thành công 09:45–09:46 | Mẫu 09:37: lỗi pipe exit 1, ghi rõ không phải inventory rỗng (dòng 23–26). Timeout subprocess được khai báo (dòng 32, 80). Mẫu 09:45: 5 container S-cool Exited, 5 volume, `docker stats` rỗng, `system df`, CPU/RAM Engine (dòng 84–94). Hai mẫu nằm ở hai mục riêng; AC bổ sung ở dòng 133 | **PASS**, giới hạn RV34-03 |
| AC-03 | Context, endpoint, API; version/args hoặc UNKNOWN/N/A có căn cứ; không suy NetworkPolicy từ Flannel | Dòng 28–30: context `k3d-zero-door`, server `https://127.0.0.1:58117`, `get nodes` bị refused (exit 1). Dòng 89–90 và 133: không có cluster trong `k3d cluster list`, nên version/args là N/A. Dòng 133 nói không có runtime proof cho NetworkPolicy | **PASS**, ghi chú RV34-02 |
| AC-04 | Nhật ký/phạm vi chỉ đọc; nêu giới hạn xác minh lịch sử; không coi tự khai là audit hệ điều hành | Dòng 12–13 và 76: thao tác chỉ đọc, phạm vi ghi. Dòng 34: giới hạn sandbox, loại bỏ giá trị 0 do lỗi CIM, chỉ đọc trường tài nguyên/AutoStart. Không khẳng định có audit hệ điều hành | **PASS có giới hạn** (RV34-04) |
| AC-05 | Tách quan sát, xác nhận của người dùng, giả thuyết và bước quyết định; report có thể đạt dù lab chưa chạy | Các mục tách riêng: "Quan sát trực tiếp", "Nguồn người dùng" (dòng 38: Hoàng xác nhận reset Docker), "Đối chiếu repo — chưa chứng minh đã apply". Giả thuyết được gắn nhãn (exit 137 không suy là OOM; RAM WSL là page cache, không kết luận rò rỉ). Bước quyết định ở dòng 55 và 129: start nếu cluster còn, dựng mới nếu mất | **PASS** |
| AC-06 | Report review độc lập có AC → evidence → verdict; artifact truy cập được tại vị trí chia sẻ đã duyệt | Inventory có trên `main` công khai qua PR #19 do Hoàng merge; blob khớp (mục 2). Báo cáo review này có bảng AC → evidence → verdict nhưng mới ở local, chưa được Codex review và chưa được duyệt chia sẻ | **PENDING**: chờ Codex review, Hoàng duyệt publication, rồi gắn link vào Linear |

### 3.3 Nguyên nhân API không truy cập được (yêu cầu S01)

Inventory chứa đủ dữ kiện nhưng không gom thành một câu. Chuỗi suy ra, chỉ từ chính inventory:
1. Lúc 09:37, Engine Docker chưa chạy (pipe `dockerDesktopLinuxEngine` vắng, WSL `docker-desktop` Stopped), nên không container k3d nào có thể nghe ở `127.0.0.1:58117`. Kết quả là connection refused.
2. Lúc 09:45, Engine đã chạy, nhưng `k3d cluster list` rỗng và không còn container hay volume k3d. Hoàng xác nhận lần reset Docker trước đã xóa container cũ. Vậy cluster cũ không còn tồn tại.
3. Context `k3d-zero-door` trên đĩa chỉ là cấu hình cũ.

Endpoint `host.docker.internal:7356` (lỗi sau đó) thuộc cluster mới, được tạo ngay trước lượt kiểm 09:58 của ZER-35, không thuộc inventory.

## 4. ZER-6 — đối chiếu nghiệm thu

### 4.1 AC → nguồn → verdict

| AC | Kỳ vọng | Bằng chứng | Verdict |
| --- | --- | --- | --- |
| AC-01: inventory | Dùng inventory ZER-34 | Mục 3: AC-01–05 đạt, nội dung không có lỗi | **PASS kỹ thuật**; Done phụ thuộc ZER-34 (AC-06 pending) |
| AC-02: start/create, API, tài nguyên, bảo toàn dữ liệu | Đường Bash hiện tại theo [bash-tooling](../../runbooks/bash-tooling.md), không đòi chạy lại script PowerShell cũ | **Create:** Hoàng tạo cluster bằng `k3d cluster create --config ./infrastructure/k3d-config.yaml`, cùng file config mà `zd_ensure_cluster` dùng (cluster-baseline dòng 9; `common.sh` dòng 160). Endpoint `host.docker.internal` được sửa thủ công, và lỗi này nay đã được tự động hóa trong `zd_fix_local_api` (`common.sh` dòng 127–145, có mock). **Dựng tiếp:** chạy lại các component trên cluster có sẵn đều đạt (lab-restoration dòng 30; bash-tooling dòng 83–107). **API:** 2 node Ready ở mọi bước (lab-restoration dòng 28). **Tài nguyên:** guard tối thiểu Windows 1844 MiB, WSL 2334 MiB, PSI tối đa 0,40 (41 bản ghi `guards.jsonl` 18:25:18–18:51:48, khớp lab-restoration dòng 285). **Dữ liệu:** 3 PVC giữ UID và Bound trước, sau và cuối (`pvc-before/after/final.json`); không có delete/uninstall/prune (lab-restoration dòng 199) | **PASS kỹ thuật có giới hạn** RV6-01, RV6-02 |
| AC-03: tích hợp | ≥5 microservices, giao dịch Online Boutique, Kafka message/correlation, Prometheus query, ES/log; trạng thái Running hay healthz đơn lẻ không đủ | Mục 4.2 | **PASS kỹ thuật** (bằng chứng lịch sử hữu hạn), giới hạn RV6-03 |

### 4.2 AC-03 theo từng tiêu chí, từ raw cuối

Raw `scratch/zer35-final/verify-final.out` (SHA-256 `2464ec52…d3e35405`), exit `0`; file được ghi xong lúc 18:37:51, run id `zd202610181836088801`. Lab-restoration dòng 275 ghi khoảng 18:36:07–18:37:51.

| Tiêu chí | Raw | Kết quả |
| --- | --- | --- |
| ≥5 microservices | `pods-final.json`: 9 pod `target-app` Running và Ready (frontend, productcatalog, cart, redis-cart, currency, checkout, payment, shipping, email). Checkout thành công đòi hỏi các service này phối hợp | Đạt. `cartservice` restart 1 lần lúc 15:23, trước gói cuối (codex-review dòng 399) |
| Giao dịch Online Boutique | Dòng 2–7: home 200, product 200, add-to-cart 302, giỏ có hàng, checkout order `1d82e7bc-cae8-11f1-81ad-aaf956ec8b46`, checkoutservice ghi log mock payment | Đạt, qua port-forward loopback |
| Kafka message/correlation | Dòng 13: round-trip trên `zd.verify.restore`, correlation `zd202610181836088801`; dòng 14–18: đủ 5 topic | Đạt. Đây là message probe có correlation, không phải message pipeline từ tấn công |
| Prometheus query | Dòng 8–11: Ready, không target down, có JMX và cAdvisor cho 9 container; dòng 36–41: PromQL của Traefik, Gaia và Nemesis trả giá trị | Đạt |
| ES/log | Dòng 12: sentinel có trong ES (2 doc); dòng 33: access log Traefik vào ES (1 doc) | Đạt |
| Ổn định sau kiểm | `observation.jsonl` 31 mẫu 11:36:31Z–11:51:48Z (15 phút 17 giây): mọi mẫu `unready` và `downTargets` rỗng, 17 target; đỉnh JMX 141Mi; `result-summary.json` không có thay đổi pod ngoài dự kiến, không Warning, heal total 0 | Đạt cho cửa sổ hữu hạn; không phải uptime 99,9% |

Healthz của ba agent (dòng 19–21) chỉ là phần bổ sung, không thay cho các tiêu chí trên. Checkout loopback và ingress (dòng 27–35, GET và rewrite) là hai phép kiểm riêng; không ghép thành "checkout qua ingress".

### 4.3 Độ mới bằng chứng và drift

- Mã, config và manifest ở HEAD giống hệt bản đã review và merge (mục 2). Sau mốc runtime 18:36–18:51, chỉ delta CL-01–04 đổi file. Trong đó, file duy nhất ảnh hưởng runtime là `setup-local-apps.sh` (thứ tự rollout tuần tự). Lúc 20:4x, `kubectl diff` server dry-run trên cả 10 object không ra khác biệt nào (codex-review dòng 489). `verify-local-lab.sh` và các manifest không đổi sau lần chạy cuối.
- Không có drift revision hay config làm mất hiệu lực bằng chứng, nên không cần chạy lại lab chỉ vì đã sang ngày mới (mốc kiểm cuối mới cách lượt review vài giờ).
- Trạng thái lab **hiện tại** chưa được kiểm (UNKNOWN). Nghiệm thu dựa trên bằng chứng lịch sử ngày 18/10, không phải lab vừa đo.

## 5. Findings

Không finding nào chặn AC kỹ thuật. Các mục dưới đây hoặc là giới hạn cần quyết định, hoặc là ghi chú.

| ID | Mức | Vị trí | Bằng chứng | Ảnh hưởng | Xử lý đề xuất |
| --- | --- | --- | --- | --- | --- |
| RV34-01 | Pending (AC-06) | Báo cáo này | Chỉ có ở checkout local | ZER-34 chưa thể Done | Codex review; Hoàng duyệt publication; gắn link remote vào Linear. Không cần sửa inventory |
| RV34-02 | Info | inventory dòng 124, 133 | Nguyên nhân API chỉ suy ra được, không có câu kết luận riêng (mục 3.3) | Người đọc phải tự ghép | Đã ghi ở mục 3.3; không sửa snapshot lịch sử |
| RV34-03 | Low | inventory dòng 86 | Port chỉ đến từ cột `Ports` của 5 container Exited; Docker không hiển thị port publish cho container đã dừng (suy luận). Không quét cổng đang nghe trên host | Không biết trước có xung đột cổng hay không. Thực tế sau đó các cổng 7356 (API), 8080→80 và 8443→443 (`k3d-config.yaml` dòng 15, 18) đều bind được: cluster-baseline dòng 24–25; verify-final dòng 27 | Không chặn. Ghi giới hạn; inventory sau này nên ghi cả cổng host đang nghe |
| RV34-04 | Info | inventory dòng 12, 34, 76 | Nhật ký chỉ đọc là tự khai của bên thực hiện; không có shell history hay audit hệ điều hành | Không xác minh độc lập được tính chỉ đọc. Mẫu 09:37 không liệt kê được container nên không có mốc trước để so | Chấp nhận như tự khai có giới hạn, đúng yêu cầu AC-04 |
| RV6-01 | Low, cần Hoàng quyết | `common.sh` dòng 147–164; lab-restoration dòng 224, 290 | Nhánh `k3d cluster create` và `k3d cluster start` của `setup-phase1.sh --component cluster` chưa chạy thật, chỉ có mock. Cluster thật do Hoàng tạo bằng cùng file config; endpoint do Codex sửa thủ công (cluster-baseline dòng 32 trở đi), còn bản tự động `zd_fix_local_api` mới có mock | Tính lặp lại chỉ được chứng minh cho bước dựng tiếp trên cluster có sẵn, chưa cho bước dựng từ đầu hoặc start bằng script | Chấp nhận như giới hạn đã ghi trong ZER-35 Done, hoặc giao bổ sung. Nhánh start: `bash infrastructure/scripts/setup-phase1.sh --component cluster` trên cluster đang chạy, tác động dự kiến thấp nhưng chưa kiểm (k3d start, sửa endpoint nếu cần, chờ node Ready). Muốn dựng lại đúng cluster zero-door từ trạng thái rỗng sẽ cần phương án bảo toàn dữ liệu và quyền riêng; kiểm create trên một cluster cô lập khác không nhất thiết phải wipe lab hiện tại, nhưng vẫn ngoài phạm vi gói này |
| RV6-02 | Đã bổ sung truy vấn metadata, xem mục 9 | inventory dòng 86, 88; lab-restoration dòng 199 | 5 container S-cool và 5 volume (S-cool MySQL, n8n, buildx) có sẵn trước khôi phục; không có `docker ps -a` hay `docker volume ls` nào sau khôi phục | Bảo toàn dữ liệu ngoài ZERO DOOR chỉ dựa vào nhật ký không-xóa | Khoảng trống inventory sau khôi phục có thể bổ sung bằng hai lệnh chỉ đọc (chỉ xác minh sự hiện diện, không chứng minh nội dung dữ liệu bất biến): `docker ps -a --format '{{.Names}}\t{{.Status}}'` và `docker volume ls --format '{{.Name}}'`. Gói này không chạy vì phạm vi chỉ cho đọc source/config/Git/evidence |
| RV6-03 | Info | verify-final dòng 6, 13, 27–35; lab-restoration dòng 291 | Kafka dùng topic probe riêng; checkout qua loopback; chưa có tấn công, heal, LLM hay KPI | Đủ cho AC tích hợp, không đủ cho nghiên cứu | Giữ cho R1/protocol; không mở rộng ZER-6 |

## 6. Failure và giới hạn được giữ nguyên

- **Failure lịch sử:**
  - Lúc 14:02 có 22 PASS, 1 FAIL (frontend `/metrics` 404).
  - JMX OOMKilled 3 lần.
  - Payment và email restart do liveness.
  - Nemesis restart sau Kafka upgrade, đã sửa ở LAB-03; lần quan sát thất bại được giữ ở `observation-before-nemesis-fix.out`.
  - OBS-02: shippingservice timeout liveness lúc 19:45:58.

  Tất cả đều được ghi trong ZER-35 và không bị thay bằng lần chạy sau.
- **Không chặn ZER-6, chỉ chặn nghiên cứu sau:** chưa chạy Helm 3 thật, chưa có đường cloud, chưa recreate thật, chưa có checkout qua ingress, chưa có nhánh 5xx runtime, chưa có LLM, tấn công, heal, BLOCK_IP hay KPI. OBS-02 thuộc protocol warm-up và pilot.
- **Kết luận cập nhật:** xem mục 9; RV6-02 đã có inventory metadata mới, RV6-01 giữ giới hạn coverage và không đòi chạy lại bootstrap cho AC hiện tại. Hoàng vẫn nghiệm thu kết quả, không cần một quyết định xóa/dựng lab.
- **UNKNOWN:** AC sống của ZER-34 và ZER-6; trạng thái Linear hiện tại; trạng thái lab hiện tại; nguyên nhân gốc OBS-01/02; cách cluster ban đầu được tạo với `host.docker.internal`.

## 7. Tự kiểm

Script kiểm: `scratch/zer34/check.py` (gitignored), SHA-256 `0608d936d08ac9646e0e00fce2182e45fa1f6340dc261bc4a6880176393d282d`.

| Lệnh | Kết quả |
| --- | --- |
| `python -I scratch/zer34/check.py selftest` | 5/5. Ca đối chứng sạch đạt; link hỏng, bảng lệch cột, placeholder sót và khoảng trắng cuối dòng đều bị bắt. Lần chạy đầu, ca đối chứng FAIL vì bộ kiểm nhầm chuỗi format Docker `{{.Names}}` là placeholder; đã thu hẹp mẫu rồi chạy lại |
| `python -I scratch/zer34/check.py` | **23 OK / 0 FAIL**. Gồm: 44 nguồn được bảo vệ giữ nguyên SHA-256 (35 file gồm tài liệu điều phối, evidence ZER-32/33/35, mã lab và raw ZER-35, cùng 9 CSV tracked); 4 file dirty ngoài phạm vi giữ hash baseline; ghi chú local-lab chỉ được nối thêm ở cuối; NOW giữ nguyên phần cũ; link, bảng, placeholder và CR/khoảng trắng cuối dòng của báo cáo, phần nối và con trỏ NOW; `git status` = baseline cộng báo cáo; HEAD không đổi; staged rỗng; `git diff --check` sạch |
| Soát trích dẫn bằng `grep`/`sed` trên file nguồn | Bản nháp có 5 số dòng sai (lab-restoration 28 và 30, `common.sh` 145 và 164, cluster-baseline 24–25); đã sửa trước khi chốt |

Inventory giữ SHA-256 `fcbabf54001d5e3f6f56984f07d0a65e97d03b7108dfb4f4003c7d5f240cd030` trước và sau. Không thêm test sao chép nội dung tài liệu.

## 8. Bàn giao

- **Codex:**
  - Đối chiếu từng verdict ở mục 3.2 và 4.1 với AC sống qua `linear_zero_door`.
  - Review RV6-01 và RV6-02, rồi trình Hoàng chọn chấp nhận giới hạn hay giao bổ sung.
  - Xử lý gom finding nếu có.
- **Hoàng:** nghiệm thu ZER-34 và ZER-6; quyết định publication cho báo cáo này (nhánh nên tạo là `zer-34-lab-acceptance`, từ HEAD đã kiểm). Sau đó Codex hoặc Hoàng cập nhật Linear.
- **Chưa làm:** không đánh dấu Done, không commit/push, không đổi Linear. G0 chỉ được đánh giá khi có đủ lab, phạm vi, RQ/đối chứng/nhãn và LLM thật (ZER-5, ZER-8, ZER-36/ZER-7).

## 9. Codex review và bổ sung — 19/10/2026, 00:43 +07:00

**Verdict: PASS kỹ thuật cho ZER-34 và ZER-6; chưa nghiệm thu/publication/Done.** AC-06 còn bước chia sẻ báo cáo review và ghi receipt trong quyền Hoàng cấp. Không có finding kỹ thuật chặn còn mở. Các mục 1–8 mô tả lượt Claude 00:11–00:22; các trạng thái UNKNOWN và bước tiếp trong đó là lịch sử, được kết luận mới ở đây thay thế tại đúng phạm vi đã kiểm.

### Đối chiếu độc lập

- Đọc live ZER-34/ZER-6/ZER-35 qua linear_zero_door đúng workspace zero-door. Hai issue đầu vẫn In Progress, AC chưa checked; ZER-35 Done. Snapshot AC của Claude khớp body hiện hành; không đổi Linear.
- Hash artifact đầu vào khớp 4107dcdf8456f43debec8c32ceb43bd31842cae5b3511ab5d37e2ccb9c5cf0bf. Chạy độc lập selftest 5/5 và kiểm chính 23 OK / 0 FAIL; tự tính lại raw JSON/JSONL thay vì dựa vào kết luận checker: 31 mẫu trong 916,789 giây (~15 phút 17 giây), tất cả unready/downTargets rỗng và 17 target; JMX peak 141Mi. 41 guard: Windows min 1844MiB, WSL min 2334MiB, PSI avg60 max 0,40. Chín pod Boutique Running và mọi container Ready. Ba PVC có namespace/name/UID/volume/Bound giống nhau trước/sau/cuối. Đây là metadata; không là kiểm toàn vẹn mọi byte dữ liệu.
- Đọc raw verify-final.out: checkout order, Kafka correlation, PromQL, ES sentinel và zero failure khớp mục 4.2. Đối chiếu trực tiếp manifest tại 1f43ff1: profile Prometheus/Grafana/Kafka/ES và K3d khớp; kiểm thêm quota/HPA/loadgenerator/legacy script/runbook và hai diff Git, 9/9 đạt. Nguồn bảo vệ 44/44 không đổi hash; raw không bị viết lại.
- GitHub PR #19 đọc lại MERGED, merge 5471b587b57dec53c3847aba9ae898d0f9fca956, head a224ce54fc0e742bbb647c61e6e9201094a9de25, 7 check SUCCESS và GHCR SKIPPED trên head. Hai diff Git xác nhận tree merge khớp head được review và source/config/test/runbook hiện tại không drift khỏi head này. Không nhận rằng đường apply tuần tự mới đã được runtime thử với spec thay đổi: phần đó chỉ có mock và server diff no-op như review CL-01 đã nêu.

### RV6-01: không yêu cầu chạy lại bootstrap

AC-02 yêu cầu chọn phương án theo inventory và khôi phục một đường triển khai có thể lặp lại; không yêu cầu chứng minh mọi nhánh của wrapper hoặc wipe cluster để thử clean bootstrap. Đường đã có bằng chứng gồm lệnh create do Hoàng báo, cấu hình repo, quan sát cluster thật, sửa endpoint có backup, dựng tiếp từng component và verify cuối. Vì vậy giữ giới hạn nhánh create/start và tự động sửa endpoint mới chỉ có mock, chấp nhận mức coverage kỹ thuật này cho AC hiện hành; quyền nghiệm thu cuối vẫn thuộc Hoàng. Không nâng thành claim bootstrap trống đã thử. Codex sửa câu sai rằng mọi phép kiểm create đều buộc wipe lab; có thể thiết kế cluster cô lập khi thật sự cần, chưa thực hiện hoặc đề xuất mở scope ở đây.

### RV6-02: đã bổ sung inventory sau khôi phục

Codex chỉ chạy ba truy vấn dưới đây, timeout 20 giây mỗi lệnh, tất cả exit 0 lúc **19/10/2026, 00:42:23–00:42:24 +07:00**; không đổi context/workload hoặc đọc nội dung volume:

- docker context show → desktop-linux.
- docker ps -a --format '{{.Names}}\t{{.Status}}' → scool_queue, scool_app, scool_mysql, scool_nginx, scool_mailpit đều còn, Exited; queue exit 137, các container khác exit 0 như inventory ban đầu. Ba container k3d đang Up; không suy mọi pod hoặc giao dịch hiện tại khỏe từ trạng thái container k3d.
- docker volume ls --format '{{.Name}}' → giữ đủ buildx_buildkit_default_state, n8n-youtube-automation_n8n_data, scool-eur20-audit_scool_mysql_data, scool-eur20-pr19_scool_mysql_data, scool_scool_mysql_data; có thêm volume lab.

Đóng khoảng trống chưa có inventory metadata sau khôi phục. Tên còn hiện diện không chứng minh ID/content bất biến vì snapshot trước không có ID/checksum nội dung; không tự mở database hoặc ghi vào dữ liệu ngoài ZERO DOOR để kiểm. Kết hợp nhật ký thao tác giới hạn, không-xóa và metadata PVC nêu trên, không thấy bằng chứng vi phạm bảo toàn trong phạm vi restore. Raw mới ở scratch/zer34/codex-readonly.json; kết quả thiết yếu đã ghi bền vững tại đây.

### Sửa, kiểm cuối và bàn giao

Codex sửa gọn diễn đạt RV6-01, giới hạn RV6-02 và câu tuổi evidence trong chính báo cáo; bản Claude nguyên gốc giữ tại scratch/zer34/claude-review-before-codex.md. Không sửa inventory hoặc evidence ZER-32/33/35, source/config/test. Bổ sung này không phải lượt gọi lab verify, AI hay nghiên cứu; kết quả tích hợp vẫn là bằng chứng lịch sử 18/10. Toàn bộ trạng thái workload hiện tại vẫn chưa được kiểm.

Sau khi Hoàng nghiệm thu và cấp quyền publication/tracking, commit/push gói tài liệu trên nhánh zer-34-lab-acceptance, kiểm link remote/hash rồi hoàn tất AC-06 và cập nhật ZER-34/ZER-6. Không cần chuyển lại Claude. G0 chưa được chốt: phạm vi ZER-5, nghiên cứu ZER-8 và backend thật ZER-36/ZER-7 còn cần xử lý.
