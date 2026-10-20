# Issue — Đo sức khỏe và thời gian độc lập

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap). Nguồn đối chiếu: `R1-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T02-S01 | Dựng probe bên ngoài luồng healer cho giao dịch Boutique và fixture. | [ZER-38](https://linear.app/zero-door/issue/ZER-38/dung-probe-nghiep-vu-djoc-lap) |
| R1-T02-S02 | Tính MTTD/MTTR từ mốc sự kiện và xác nhận hồi phục bằng probe. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |
| R1-T02-S03 | Xử lý thiếu dữ liệu, timeout, FAILED/PARTIAL và FPR có mẫu số rõ ràng. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |
| R1-T02-S04 | Bổ sung metric quyết định, phục hồi theo lượt và usage/cost theo run. | AC của [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T02-S01

Timestamp, chu kỳ probe, tiêu chí healthy và ví dụ lỗi được quan sát thật.

### R1-T02-S02

Tái tính incident từ raw: MTTD effect→detector detect, MTTR detect→recovery xác minh, total recovery effect→recovery. Không lấy heal history/replica tăng làm detect; ghi chu kỳ probe và độ phân giải thời gian.

### R1-T02-S03

Phép thử có action thất bại nhưng chưa recovery, timeout và missing; chưa xác minh recovery thì MTTR chưa xác định/censored theo protocol, không điền 0 hoặc 1s. Giữ mọi run trong mẫu số, báo riêng phân phối lượt recovered và tỷ lệ failure; thiếu dữ liệu không thành uptime 100%.

### R1-T02-S04

Định nghĩa mẫu số; lưu đề xuất trước guard, action thực thi, false action, recovery/failure và số call/token kể cả retry.

## Phụ thuộc cần đối chiếu

[R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## Tiếp nhận ZER-10 + ZER-38 — 20/10/2026

Hoàng yêu cầu chuyển gói kế tiếp In Progress. Đã đọc live AC/relations cả cha ZER-10 và con ZER-38; chuyển cả hai In Progress và read-back, không tích AC. Prerequisite ZER-6/37 và nguồn event ZER-9 Done; guard/CI ZER-12/40 đã nghiệm thu sau PR25 merge55200c9,15 CI đạt trên head0babf90. Local checkout vẫn zer-12-command-guards HEAD0babf90, dirty quy ước/NOW/note còn giữ; chưa switch branch hay bắt đầu sửa code.

Thứ tự gói: probe độc lập cho Boutique+fixture (ZER-38/AC-01), rồi scorer/tái tính MTTD/MTTR và total recovery từ raw theo contract, missing/censoring/failure/mẫu số và metric decision/recovery/usage-cost (AC-02–04). Phải ghi file/action scope và actual baseline trước triển khai. Child hoàn tất không tự hoàn tất cha.

Khoảng trống cần xử lý khi chốt scope: fixture runtime nằm ở ZER-41/cha ZER-13 tại R2. Chưa thay trạng thái các issue R2, bỏ yêu cầu fixture hoặc nhận mock là nghiệm thu. Xác minh source/fixture hiện có, chốt phạm vi tối thiểu cần thiết trước runtime; tracking In Progress không cho phép lab/model/cloud/publication. ZER-11/39 và G1 chưa hoàn tất. Writer Codex chỉ cập nhật checkpoint lượt này; chưa giao/messaging Claude hoặc triển khai probe.


## Gói thực hiện Claude — ZER-10 + ZER-38 — 20/10/2026

### Outcome và writer

Hoàng yêu cầu giao Claude **cả ZER-10 và sub-issue ZER-38**. Claude nhận writer khi bắt đầu; Codex review độc lập sau một bàn giao tổng hợp. Triển khai probe, recovery evaluator, scorer và verification thành một gói tích hợp; không dừng sau child hay chỉ viết thiết kế. Tự review, sửa gom và retest lỗi liên quan trước khi trả.

AC đã đọc trực tiếp qua linear_zero_door ngày 20/10/2026, URLs thuộc linear.app/zero-door:

| Phạm vi | Đầu ra bắt buộc |
| --- | --- |
| ZER-38 = ZER-10 AC-01 | Probe ngoài healer cho Boutique **và fixture**; giao dịch nghiệp vụ, timestamp/cadence, healthy/failure/timeout, raw sample có provenance. Nghiệm thu còn cần ví dụ lỗi quan sát thật. |
| ZER-10 AC-02 | Tái tính raw: MTTD effect→detect, MTTR detect→verified recovery, total effect→recovery; cadence và clock resolution/uncertainty. Không suy từ heal history/replica. |
| ZER-10 AC-03 | Failure/PARTIAL/timeout/missing/censoring và FPR đúng mẫu số; không MTTR giả, không bỏ run thiếu dữ liệu, không uptime100%. |
| ZER-10 AC-04 | Quyết định trước guard, action thực thi/false action, recovery/failure, call/token/cost gồm retry theo trial/run; mẫu số và coverage rõ. |

ZER-10/38 đang In Progress, chưa tích AC. ZER-6/37/9 và ZER-12/40 Done. ZER-11/39 chưa xong; không đóng G1. Nếu Claude không có đúng connector, dùng snapshot trên và ghi live AC UNKNOWN ở phía mình; không dùng workspace khác, tự sửa AC/relations hay tạo issue mới.

### Baseline và nhận checkout

- Repo: R:/_Projects/Eurus_Workspace/zero_door.
- Actual HEAD lúc giao: **0babf90ef7ceb47bf420e1bde4aab8de72c2cf5e**, branch **zer-12-command-guards**, staged rỗng.
- origin/main đã kiểm: **55200c9143565c1773cbff57553a9ce858ffe858**, PR25 đã merge. Product/evidence ZER-12 khớp head đã review.
- Dirty có sẵn: AGENTS.md; docs/delivery/{NOW.md,README.md,WORKFLOW.md}; docs/delivery/milestones/R1-measurement/{README.md,event-contract.md,guards-and-ci.md,probes-and-metrics.md}; docs/delivery/WORKING-AGREEMENT.md untracked. Giữ mọi nội dung, không coi chúng là phần code mới.
- Snapshot: scratch/zer10/intake-baseline.json và head.txt, origin-main.txt, status.txt, staged.txt cùng thư mục. Snapshot hash được chụp sau khi Codex ghi gói này.
- Khi triển khai, tạo nhánh **zer-10-independent-measurement** từ merge55200c9 đã kiểm, giữ nguyên dirty. Nếu nhánh tồn tại thì kiểm trước dùng lại. Không force switch/reset/stash/clean. Dirty cản switch thì giữ dữ liệu và báo đúng nguyên nhân.
- Trước edit đầu tiên: đối chiếu lại HEAD/status/hash, ghi actual baseline, exact file/action scope gồm helper/tests/probes mới vào scratch/zer10/claude/intake.json. Drift phải giải thích, không ghi đè.
- Note này chỉ nối thêm; NOW chỉ thêm con trỏ đầu. Không hỏi Hoàng duyệt lại từng helper trong scope đã giao.

### Nguồn chuẩn và khám phá

Đọc delivery README → WORKING-AGREEMENT → NOW → note này, SCOPE/WORKFLOW và docs/runbooks/bash-tooling.md; theo AGENTS. Dùng GitNexus context/freshness → query/context rồi trực tiếp source. Index chỉ dẫn đường; không bật embeddings/wiki. Lúc giao context báo index head0babf90, runner schema4; đổi nhánh/mã thì kiểm lại.

Các nguồn đã nghiệm thu phải giữ nguyên:

1. docs/evidence/ZER-32/requirements-and-kpi.md: mục3–4, RV-01/02/03, D-01…D-05, F-01…F-05.
2. docs/evidence/ZER-8/research-design.md: mục4–5 và11–13, M1–M12, BM/ground truth và benign FPR.
3. docs/design/r1-event-contract.md: **zd-event/1.0.0 LOCKED**, mục4–9, đặc biệt7.5. docs/evidence/ZER-37 là oracle lịch sử, không copy helper thành production scorer.
4. agent-orchestrator/event_pipeline/{contract,store,gateway,audit,client,adapters}.py, docs/runbooks/r1-event-pipeline.md và bằng chứng ZER-9 cuối. client.py là **O-only**, không nhét H credentials/path vào đó.
5. infrastructure/scripts/verify-local-lab.sh phần purchase có checkout lành để tham khảo, chưa là continuous probe/scorer. verify-event-actors.py chỉ chứng minh transport, không workload effect/recovery.
6. docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md và ZER-41 để xác minh giao diện fixture, không tự kéo cả R2/ZER-13 vào gói.

### File/action scope

Cho phép triển khai và kiểm offline trong các đường sau. Ghi danh sách file nội bộ cụ thể trước sửa:

- **agent-orchestrator/measurement/**: package Python mới cho business flows/probe, clock, H sink, recovery evaluator, raw scorer và CLI. Import contract/canonical/Producer/archive sẵn có; không copy cả store/gateway.
- **infrastructure/scripts/verify-measurement.py**, **verify-measurement.sh**: entrypoint verification/recompute. Help/offline không đụng lab; runtime opt-in rõ, bounded plan/output mới, nhưng chưa chạy runtime trong gói này.
- **tests/test_measurement_*.py**, **tests/fixtures/zer10/**. Ưu tiên Python3.11/stdlib. Nếu thật sự cần thêm thư viện, chỉ thêm tests/requirements-measurement.txt và .lock có hash riêng; không đổi production locks ZER-12.
- **.github/workflows/ci.yml**: thêm kiểm measurement offline chạy được trên clean checkout; giữ các gate cũ, không thêm deploy/publication tự động.
- **docs/design/r1-measurement.md**, **docs/runbooks/independent-measurement.md**, **docs/evidence/ZER-10/**: giao diện, runbook, AC→case→result và evidence/checksum/checker.
- **scratch/zer10/claude/** cho baseline/log/thử nghiệm; evidence mà reviewer/CI cần phải có bản chọn lọc tại docs/evidence hoặc tests, không lệ thuộc scratch có sẵn.
- Note này nối handoff, NOW thêm pointer.

Read-only ngoài phạm vi: legacy runners/analysis/dashboard, Gaia/Nemesis/Hephaestus, chaos-worker, event_pipeline, manifest/RBAC/NetworkPolicy/Secrets, SCOPE, thiết kế LOCKED và evidence cũ. Thay đổi bắt buộc ngoài scope: ghi delta/tác động cụ thể và tiếp tục phần độc lập, không sửa hàng loạt consumer. Trường sample từng bước theo OPEN của ZER-37 được thiết kế additive trong tài liệu mới; nếu transport không nhận thì trình đề xuất MINOR cụ thể, chưa tự đổi contract đã khóa.

### Yêu cầu triển khai

**1. Probe nghiệp vụ độc lập — ZER-38/AC-01**

- Boutique kiểm home/product → cart bằng session riêng → checkout dữ liệu demo; xác nhận nội dung/đơn đúng. HTTP200/healthz/Ready không đủ; không tái dùng giỏ/response cũ làm PASS. Lưu status/timing/lý do lỗi từng bước, không lưu cookie/token/card đầy đủ hay dữ liệu nhạy cảm không cần thiết.
- Fixture là adapter cấu hình rõ cho **giao dịch benign với kết quả nghiệp vụ mong đợi**, không GET200 bất kỳ. Không tạo fixture dễ tổn thương/executor/payload SQLi. Nếu chưa có fixture thật, hoàn thiện giao diện và fake server offline có nhãn SYNTHETIC, kê endpoint/data/assertion cần từ ZER-41; không làm fixture flow luôn PASS.
- Độc lập với healer: không dùng heal history/ground truth để chấm healthy. Đăng ký probe_id/version/flow trong TRIAL_STARTED. PROBE_SAMPLE/HEARTBEAT/CLOCK_SYNC đi H; scorer đi S; O không đọc mẫu/kết quả/nhãn H.
- Explicit config/run manifest: cadence, timeout từng bước/toàn giao dịch, L/gap/K/S/cap/warm-up, max duration/samples/request budget. Tham số formal OPEN phải nhận input hoặc ghi cấu hình synthetic, không tự biến minh họa thành quyết định đã khóa.
- UTC cho mốc, monotonic cho elapsed/deadline; ghi resolution/uncertainty thực. OFF_HOST có CLOCK_SYNC phủ đầu/cuối, xử lý offset/drift đúng contract; ingest timestamp không thay offset.
- Phân biệt timeout/connect/TLS/HTTP/parse/schema/business/SLOW/cancel. Probe chết, skip do overrun, mất mẫu hay lỗi persistence không thành healthy. Bounded retry; resend giữ event identity, không che request failure. Stop/cancel giữ raw và dọn đúng tài nguyên test sở hữu.

**2. Recovery evaluator/scorer — AC-02/03**

- Đọc sealed exports H/O, kiểm checksum/manifest; giữ raw nguyên trạng. Invalid/late/quarantine/ORPHAN/conflict theo contract; không dùng dashboard/heal history/legacy làm nguồn chuẩn.
- Tuân thủ §7.5 đầy đủ: sau effect và mẫu lỗi; K mẫu liên tiếp/gap; T_rec là t_start mẫu thứ K; đủ S và mọi mẫu kết thúc mới xác minh; ứng viên đúng cap được xét đủ S; relapse/gap hủy ứng viên. Bind trial/flow/probe/version/sequence/samples_sha256, không trộn probe/clock để lấp gap.
- Scorer tái tính từ samples, không tin RECOVERY_VERIFIED; so mọi trường và báo EVALUATOR_MISMATCH. Có thể dùng chung hàm recovery production, nhưng oracle expected test phải tính tay độc lập.
- Đúng mốc/nguồn/clock cho MTTD, MTTR, total, reaction; gồm early detect, B0 không detect, recovery trước detect/sau stop, clock chưa xác minh. ActionSUCCESS không suy recovery; actionFAILED/PARTIAL hoặc không action vẫn có thể quan sát recovery, nhưng không gán công healer.
- requested/CONFIRMED/CONFIRMED_NO_EFFECT/UNKNOWN_EFFECT/N rõ. UNKNOWN_EFFECT/missing ở lại N; NO_EFFECT chỉ loại với coverage đủ. EMPTY/NO_ELIGIBLE không PASS. Không recovery: timeout/censored hoặc MISSING_PROBE theo coverage, không0/1s. Mean recovered chỉ mô tả, không thay tỷ lệ trên mọi eligible.
- Uptime dùng hợp outage và hợp gap của mọi flow bắt buộc theo RV-01; báo cận/coverage/giả định lấy mẫu. Gap không là downtime chắc chắn hay uptime chắc chắn.

**3. Metric quyết định/usage và giao diện consumer — AC-04**

- Đối chiếu M1–M12 ZER-8 ở phần dữ liệu liên quan; phần chưa có evidence/telemetry phải hiện MISSING/N/A có lý do. Output ghi numerator, denominator/cohort, coverage, exclusions, provenance; không bỏ metric để tránh gap.
- Tách proposal trước guard, verdict, action thực thi/terminal, fallback, recovery. M1 không chấm lại quyết định sau guard. M5 slot/episode trên benign window có coverage/cận; M6 theo giờ/cửa sổ, không false alarm chia số attack.
- Cộng mọi LLM_CALL/retry đúng một lần theo call_id, tách actor/model/run/trial. Usage/cost thiếu MISSING; nhóm không dùng LLM N/A, không0. Giá/price_ref là config có nguồn, không hardcode giá hiện tại hoặc gọi API lấy mẫu.
- Containment không suy từ availability; CPU không đủ telemetry/denominator phải ghi thiếu. Export JSON schema/version và CSV ổn định để ZER-11 dùng sau, cùng raw/config cho cùng kết quả. Artifact S không quay sang O. Chưa sửa dashboard.

### Fixture/runtime và quyền

Khảo sát đường probe/event lúc giao chưa tìm thấy fixture app/database thực dùng ngay; ZER-41 vẫn Backlog tại R2. Claude xác minh lại và ghi gap chính xác. **Không dừng cả gói:** hoàn thiện code adapter/evaluator/scorer, test/CI offline và runtime plan. Chưa nhận mock/transport cũ là AC-01 đạt; ZER-38 và phần tương ứng ZER-10 giữ PARTIAL cho đến khi có fixture và quan sát thật.

Không gọi Kubernetes/Docker/Helm, mở port-forward/namespace/policy/Secret, gửi probe vào lab, gây fault/heal/reset, inference/chi tiền hoặc cloud. Test được dùng fake/in-process/HTTP loopback do test tự tạo, không đụng dịch vụ đang có. Chưa triển khai fixture; không sửa Linear, commit/push/PR/merge hay nhắn agent khác.

Cuối gói trình **một runtime plan gom**: target/route/origin allowlist/redirect, namespace/identity, cadence/count/duration/request/resource budget, phép tạo lỗi tối thiểu cần quan sát, cleanup/stop và output. Hoàng quyết fixture/runtime sau khi có kế hoạch cụ thể; không hỏi lại từng component offline.

### Verification và bàn giao

Tính expected trước scorer, test phải phân biệt lỗi đo thật. Ít nhất có negative và control cho các nhóm:

- Business200 sai nội dung, stale session/cart, checkout chưa xác nhận, fixture fake200 sai kết quả; timeout giữa flow, cancel/overrun/gap, event sink lỗi không mất raw im lặng.
- E01 tính tay MTTD30/MTTR60/total90/reaction19; ingest muộn không đổi; SUCCESS nhưng probe lỗi; FAILED/PARTIAL nhưng phục hồi; no action/B0.
- K/S boundary, relapse, candidate đúng/sau cap, stop giữa T_rec và hết S, thiếu mẫu sau candidate, t_end muộn; CLOCK_SYNC thiếu/offset/drift; conflicting sample ID, duplicate/out-of-order.
- UNKNOWN ở lại N; NO_EFFECT thiếu coverage; EMPTY/ALL_NO_EFFECT/ALL_UNKNOWN; gap nhiều flow chồng outage không đếm trùng; benign coverage thiếu không FPR0.
- Proposal sai bị guard chặn không M1 đúng; no trigger/fallback; LLM retry/redelivery không đếm trùng/bỏ call, missingcost/N/A; unscoped/wrongtarget/orphan không ghép theo thời gian.
- Raw hash mismatch, input lỗi/seal/late/quarantine; output đã tồn tại/lỗi không ghi đè raw. Help/offline không mở lab; clean checkout không cần scratch.

Timeout test phải chạy nhánh timeout thật qua transport fake, không chỉ ném exception tự đặt. Chọn vài mutant sai mốc/loại UNKNOWN/missing=PASS/H vào O để chứng minh test bắt lỗi. Chạy focused measurement và hồi quy contract/pipeline/agents theo import/giao diện liên quan; giữ các gate cũ. Không nhân số kiểm không cần thiết.

Bàn giao một lần:

1. Code/probe/evaluator/scorer, tests/fixtures/CI, runbook tái lập offline; kê runtime còn thiếu.
2. docs/evidence/ZER-10/verification.md: AC→case→expected/actual→artifact, commands/environment/version, giới hạn. Nếu đạt, verdict **READY_FOR_CODEX_REVIEW_OFFLINE**, chưa Done/runtimePASS.
3. SHA-256 source/evidence và diff theo baseline dirty; nguồn bảo vệ giữ hash, log chọn lọc không secrets.
4. Handoff nối cuối note, NOW pointer; gom quyết định thiếu theo hệ quả (fixture/runtime). Trả writer Codex, dừng sửa source khi review.

Codex sẽ review đủ AC cha/con và consumer trực tiếp, tự tính trace/phản ví dụ, kiểm clock/gap/mẫu số/usage/H-O-S, gom finding cho một lượt sửa. Remote CI, runtime theo AC, merge và Hoàng acceptance vẫn còn trước nghiệm thu.

## Claude bàn giao ZER-10 + ZER-38 — READY_FOR_CODEX_REVIEW_OFFLINE — 20/10/2026

**Kết quả.** Gói tích hợp đã xong ở mức offline, gồm probe nghiệp vụ độc lập, recovery evaluator, scorer tái tính từ raw và metric quyết định/usage. ZER-38 = AC-01 còn **PARTIAL**: chưa có fixture thật (ZER-41) và chưa quan sát được lỗi thật. AC-02/03/04 đạt trên dữ liệu SYNTHETIC. Chưa runtime, chưa Done. Chi tiết AC → case → kết quả ở [verification](../../../evidence/ZER-10/verification.md); giao diện ở [r1-measurement](../../../design/r1-measurement.md); lệnh tái lập và runtime plan ở [runbook](../../../runbooks/independent-measurement.md).

**Baseline.** Nhánh `zer-10-independent-measurement` tạo từ merge 55200c9 (cây trùng 0babf90). Staged rỗng. Chín file dirty có sẵn giữ nguyên, hash mọi nguồn read-only khớp intake. AC sống phía Claude là UNKNOWN (không có `linear_zero_door`); bản này dùng snapshot trong gói giao.

**Đã làm.** Package `agent-orchestrator/measurement/` (12 module), `infrastructure/scripts/verify-measurement.{py,sh}`, 5 file `tests/test_measurement_*.py` và `tests/fixtures/zer10/`, job CI `r1-measurement-offline`, tài liệu thiết kế, runbook và `docs/evidence/ZER-10/`. Không sửa event_pipeline, agent, chaos-worker, manifest, contract hay evidence cũ.

**Kiểm.** 71/71 test trên cả Python 3.11.9 và 3.12.4 (`OFFLINE_PASS`, E01 khớp số tay); 11/11 mutant bị bắt; đối chiếu 62 ca §10 của ZER-37 qua Archive thật khớp 178/178 trường hand-expected; Bandit sạch; hồi quy ZER-9 22+42+4 và ZER-37 238/238 với 32/32 mutant đều đạt. `python -B docs/evidence/ZER-10/check_package.py --check` kiểm 37 file, 27 nguồn bảo vệ, note/NOW chỉ nối thêm và phạm vi Git. SHA-256 của `manifest.json`: `b3a33293105ee44f0e772405ca40ddea1b4820ca95cea035da93fdbc6b169292`.

**Codex cần review**, chi tiết ở verification §5:
1. Lỗ sequence được coi là khoảng trống.
2. MODE_VIOLATION làm incident MISSING.
3. Tên khóa `f01_params`.
4. `payload.detail` và đề xuất MINOR `zd-event/1.1.0`.
5. `zd-gt-constraints/0`.
6. Cutoff dùng seal; C0/slot/coverage là input tường minh.

Trong lúc tự review, tôi đã tìm và sửa 8 lỗi (verification §4), trong đó có LINK_CONFLICT liên run (`--other-export`), việc chèn giá trị server vào path, và bước đối chiếu chéo phụ thuộc scratch khi chạy trên clean checkout.

**Quyết định còn thiếu, gom theo hệ quả:**
- **Fixture/AC-01:** ZER-41 phải dựng fixture theo giao diện SYNTHETIC `/fixture/orders`, hoặc đổi spec theo endpoint thật. Thiếu phần này thì ZER-38 giữ PARTIAL.
- **Runtime:** Hoàng quyết theo runtime plan gom ở runbook §3, gồm target/port-forward, H gateway và danh tính `probe`, đồng hồ tham chiếu hoặc probe HOST_SHARED, budget pilot 15 phút/900 mẫu, hai lỗi tối thiểu (scale frontend về 0, dừng checkoutservice) và cleanup/output.
- **Protocol (ZER-53/F-01):** L/timeout, phương pháp sync, `ingest_grace`, w_b/g_b và bộ action thật (ZER-50).

Không lab, Docker, model, Linear, commit/push/PR hay nhắn agent khác. Writer trả Codex; source đóng băng tới khi có review gom. Còn lại: CI từ xa, runtime theo AC, merge và Hoàng nghiệm thu.


## Codex review gom — ZER-10 + ZER-38 — 20/10/2026

Đã đọc AC sống đúng Linear Zero Door, đối chiếu HEAD55200c9/nhánh zer-10-independent-measurement và 37 file manifest Claude. Báo cáo [codex-review.md](../../../evidence/ZER-10/codex-review.md), SHA-256 9f0e9b495a1af50c0ea47f96f7546cf06bbd22adbe54ac9172c106c3dafc4237. Verdict **NOT_READY_OFFLINE / CHANGES_REQUIRED**: ZR10-01 P1 mất lượt requested khi request INVALID (mixed hai trial ra N1/PASS thay vì N2/UNKNOWN); ZR10-02…11 P2 gồm clock thiếu thành MISSED, M5 episode/coverage, M6 action thiếu terminal, M11 completeness, GT hỏng crash, guard conflict theo ingest, probe sai quantity vẫn PASS, step/run deadline, cleanup ownership/interrupt và H redirect/ACK. ZR10-N1 output trong other-export là P3. Chi tiết, anchor, expected/actual và gói sửa/retest ở báo cáo.

Kiểm độc lập: 71/71 suite OFFLINE_PASS (Python3.12.4), E01 30/60/90/19; đối chiếu ZER-37 178/178 trên62case; focused17probe+5CLI OK. Phản ví dụ và log portable ở docs/evidence/ZER-10/codex-review/. 37/37 hash nguồn Claude, 27/27 protected khớp; file ngoài gói docs/detail_zero-door.md đã có lúc nhận và giữ nguyên. Checker original báo scope cho file ngoài gói đó, không có drift nguồn. Staged rỗng, không sửa source, không commit/push/PR/merge/Linear/lab/model. Graph stale/refresh không tiến đã dừng, review mã mới dùng directsource+execution, không nhận PDG coverage.

**Gói sửa tiếp theo cho Claude (khi nhận writer):** đọc cả báo cáo, xử lý gom ZR10-01…11 cùng các nhánh chung nguyên nhân trong measurement, tests, CLI/CI và docs đã cho phép. Giữ contract LOCKED/event_pipeline/agents/worker/manifests/evidence cũ và report Codex chỉ đọc; baseline mới từ manifest Claude b3a33293…9292 + actual HEAD/status. Tạo fix-01 delta/hash, test fail-before/pass-after (đặc biệt N/clock/M5/M6/M11, unequal timeout, cleanup stale ref và H redirect); không hardcode case. Retest affected behavior và regression trực tiếp, cập nhật verification/runbook, trả một gói READY_FOR_CODEX_RETEST_OFFLINE. Không mở thêm lab/model/publication/Linear quyền. ZER-38/AC01 vẫn PARTIAL tới fixture thật và lỗi quan sát runtime; không đóng issue/G1 bằng mock. Codex đã kết thúc writer review; chưa nhắn sang session Claude.

## Claude bàn giao fix-01 ZER-10 + ZER-38 — READY_FOR_CODEX_RETEST_OFFLINE — 20/10/2026

**Kết quả.** Đã sửa gom cả mười hai mục của [Codex review](../../../evidence/ZER-10/codex-review.md): ZR10-01 P1, ZR10-02…11 P2, ZR10-N1 P3, cùng các nhánh chung nguyên nhân. Mỗi finding có regression riêng. ZER-38 = AC-01 vẫn **PARTIAL** vì chưa có fixture thật (ZER-41) và chưa quan sát runtime. Chưa Done. Bảng finding → nguyên nhân → sửa → test ở [verification §7](../../../evidence/ZER-10/verification.md). Thiết kế và runbook đã cập nhật theo hành vi cuối.

**Đã sửa:**
- **ZR10-01:** request INVALID, quarantine hoặc late vẫn giữ lượt trong N dưới dạng MISSING, không đoán trường thiếu. Không gán được ID thì cohort INCOMPLETE và verdict KPI là UNKNOWN.
- **ZR10-02:** bằng chứng trên đồng hồ chưa xác minh (detector, executor, decision) cho MISSING/`MISSING_ORDER`, không thành MISSED hay NO_SUCCESS.
- **ZR10-03/04:** M5 có khóa episode và coverage toàn stream; M6 đếm từ HEAL_STARTED, báo terminal/harm riêng; B0 là N/A.
- **ZR10-05:** coverage M11 bắt đầu từ DECISION của tác tử LLM; bản ghi hỏng giữ MISSING và tổng là cận dưới.
- **ZR10-06:** GT hỏng cho UNKNOWN_GT/UNKNOWN_COHORT kèm reason, không crash.
- **ZR10-07:** kiểm cardinality §3.2; không còn chọn theo thứ tự ingest.
- **ZR10-08:** giỏ phải có đúng một dòng, đúng sản phẩm, quantity 1. Marker là OBSERVED-SHAPE, chưa khóa.
- **ZR10-09:** deadline bước, giao dịch và trần run đều có hiệu lực; `budget.grace_s` bắt buộc.
- **ZR10-10:** cleanup chỉ xóa khi chứng minh được sở hữu (session mới hoặc echo nonce), nếu không thì `UNRESOLVED_OWNERSHIP`; Ctrl+C/SIGTERM đi đường cancel và cleanup chạy trong `finally`.
- **ZR10-11:** H sink không theo redirect, bỏ qua proxy môi trường, chỉ nhận ACK 201 đúng chuẩn; nếu không thì dừng `SINK_REFUSED` và outbox giữ event.
- **ZR10-N1:** output không được nằm trong bất kỳ input export nào.

**Kiểm:**
- **Test offline:** 103/103 trên Python 3.11.9 và 3.12.4 (71 cũ + 32 mới), E01 30/60/90/19.
- **Phản ví dụ Codex:** retest đạt 29/29 kiểm theo expected của review.
- **Mutant:** 28/28 bị bắt, gồm 17 mutant `FIX01_*`, mỗi cái khôi phục đúng một hành vi Codex chỉ ra.
- **Đối chiếu ZER-37:** 178/178.
- **Bandit:** package sạch.
- **Hồi quy:** ZER-9 22+42+4 và ZER-37 238/238 với 32/32 mutant.
- **Clean checkout mô phỏng:** đạt cả bốn bộ.
- **Gói:** `python -B docs/evidence/ZER-10/check_package.py --check` không báo vấn đề. Gói có 46 file; so với manifest gốc `b3a33293…9292` có 19 file đổi và 9 file thêm. Báo cáo và 14 file bằng chứng của Codex giữ nguyên hash. SHA-256 của `fix-01/manifest.json`: `9f1e385097b417f91f0afa4cee64e58257fcb307d938eef309954c60bb82f08a`.

**Cần Codex retest:** chạy lại mọi kiểm ở verification §7.3. Script `probe/counterexamples.py` của Codex có hai dòng chẩn đoán giả định hành vi cũ, nên harness retest chạy nó với đúng hai chỗ thích nghi; hai chỗ này được ghi trong output.

**Còn mở:**
- Fixture ZER-41 và runtime theo runbook §3, gồm đối chiếu `CART_MARKERS` trên Boutique thật.
- Chốt ack 202 nếu dùng H gateway chế độ Kafka.
- Ràng buộc mặt hàng với trang xác nhận đơn.
- Trường hợp mẫu sau TRIAL_ENDED: không phải finding, chưa đổi hành vi.

Không lab, API, model, Linear, commit/push/PR hay nhắn agent khác. Writer trả Codex; source đóng băng tới khi có kết quả retest.


## Codex retest fix-01 — ZER-10 + ZER-38 — CHANGES_REQUIRED_OFFLINE — 20/10/2026

[Report](../../../evidence/ZER-10/codex-retest01.md), SHA-256 `975ab94d38d3df951894decffc0bdaa55d635f5b3d5b5658f3d7f0a32b76cf39`. Baseline55200c9, staged rỗng; fix manifest9f1e3850…f08a khớp46/46, protected28/28, review cũ14/14. Codex chạy độc lập103test/E0130-60-90-19, replay29/29 và crosscheck178/178 đều đạt; chưa chạy lại mutant/Bandit/3.11/remoteCI/runtime.

Còn ba P2: **FX01-R1** cleanup dùng cookie đã đổi có thể xóa nhầm giỏ khác (ZR10-10); **FX01-R2** cap/grace chưa chặn cadence wait, body ACK nhỏ giọt và cleanup khi ngắt sớm (ZR10-09); **FX01-R3** request hỏng được giữ cohort nhưng thiếu trial metadata làm sort None.ms crash thay vì MISSING (ZR10-01). P3FX01-N1: nested call coverage vẫn COMPLETE khi call_id conflict, dù top-level/usage/cost đã MISSING. Journal cancel CLI chưa được lưu/đưa vào output: residual sửa gom theoZR10-10.

**Gói fix-02 giao Claude:** đọc report trên, xử lýFX01-R1…R3 và N1 cùng các nhánh chung nguyên nhân, lưu snapshot before trước khi sửa; thêm regression negative/control và chạy retest liên quan. File/action scope giữ package measurement, tests/fixtures và docs/checker liên quan của fix-01; không sửa event_pipeline/contract/agent/worker hay evidence gốc. Manifest gốc, fix-01, Codex review và codex-retest01/ là read-only; delta mới để fix-02. Trả một gói READY_FOR_CODEX_RETEST_OFFLINE; note chỉ nối/NOW thêm con trỏ. Không lab/API/model/Git publication/Linear/message sang chat khác. Writer review đã kết thúc, Claude nhận writer khi bắt đầu gói.

Linear đọc lại đúngzero-door: ZER-10/38 vẫn In Progress, chưa tíchAC. ZER-38/AC01PARTIAL vì chưa fixture/runtime, G1 chưa đóng. Không coi retest cũ đạt là đã nghiệm thu; source giữ nguyên.


## Claude bàn giao fix-02 ZER-10 + ZER-38 — READY_FOR_CODEX_RETEST_OFFLINE — 20/10/2026

**Kết quả.** Đã sửa gom FX01-R1, FX01-R2, FX01-R3 (P2), FX01-N1 (P3) và residual journal của ZR10-10 theo [Codex retest01](../../../evidence/ZER-10/codex-retest01.md), cùng các nhánh chung nguyên nhân. Mỗi điểm có regression negative + control. ZER-38 = AC-01 vẫn **PARTIAL** vì chưa có fixture thật (ZER-41) và chưa quan sát runtime. Chưa Done. Bảng finding → nguyên nhân → sửa → test ở [verification §8](../../../evidence/ZER-10/verification.md). Thiết kế và runbook đã cập nhật theo hành vi cuối.

**Snapshot trước sửa.** Trước lần sửa đầu tiên, cả 46 file gói fix-01 được chép nguyên byte vào `docs/evidence/ZER-10/fix-02/before/` (`before.json`; mọi hash bằng `fix-01/manifest.json`). `fix-02/fail_before.py` chạy cùng bộ regression mới và hai script phản ví dụ của Codex trên snapshot đó và trên cây hiện tại.

**Đã sửa:**
- **FX01-R1:** cleanup dùng cookie đóng băng lúc gửi request tạo, không dùng jar hiện tại; session chỉ là sở hữu khi jar đúng session mẫu vừa được cấp. Cùng nguyên nhân: identifier đích của bản ghi chứng minh bằng nonce cũng đóng băng; path cleanup dùng biến capture sau bước chứng minh bị `SpecError`.
- **FX01-R2:** một deadline tổng xuyên chờ slot (min(slot, trần)), ghi H, đọc đồng hồ tham chiếu và cleanup. H sink và đồng hồ dùng client có giới hạn của probe (connect, header và toàn bộ body; không proxy, không redirect). Publisher kiểm deadline trước mỗi lần thử và truyền vào lần thử. Grace tính từ mốc dừng sớm nhất; cleanup của mẫu dở có grace riêng từ lúc dừng.
- **ZR10-10 residual:** CLI ghi journal ra đĩa (`--journal`, mặc định `<outbox>.journal.jsonl`, fsync từng dòng); summary in đường dẫn và `unresolved_cleanup`; journal hỏng thì exit 5 trước request đầu tiên.
- **FX01-R3:** mốc không dựng được không vào sort/min; incident MISSING `TRIAL_MISSING` ở lại N, `t_stop_status = CLOCK_UNVERIFIED`; trial khác giữ kết quả; uptime vẫn liệt kê trial thiếu (`TRIAL_BOUNDS_MISSING`).
- **FX01-N1:** mọi bản ghi của `call_id` xung đột đánh MISSING các nhóm nó nêu (`conflicting_call_records`).

**Kiểm:**
- **Test offline:** 125/125 trên Python 3.11.9 và 3.12.4 (103 của fix-01 + 22 mới), E01 30/60/90/19.
- **Fail-before thật:** `fix-02/fail_before.py` PASS. 16 test NEGATIVE fail trên snapshot và đạt sau sửa; 6 test CONTROL đạt sau. 7/7 kiểm theo expected của codex-retest01 sai trên snapshot (6,01 s chờ slot; ACK nhỏ giọt 0,30 s; CLI 0,38 s; `AttributeError`) và đúng trên cây hiện tại.
- **Phản ví dụ Codex:** hai script `codex-retest01/` chạy nguyên trạng ra đúng expected; phản ví dụ review lần đầu vẫn 29/29.
- **Mutant:** 40/40 bị bắt (11 cũ, 17 `FIX01_*`, 12 `FIX02_*`), đối chứng 125 sạch.
- **Khác:** đối chiếu ZER-37 178/178; Bandit 0 issue; hồi quy ZER-9 22+42+4 và ZER-37 238/238, 32/32; clean checkout mô phỏng đạt.
- **Gói:** `python -B docs/evidence/ZER-10/check_package.py --check` không báo vấn đề. `fix-02/manifest.json` có 57 file; so với `fix-01/manifest.json` (`9f1e3850…f08a`, giữ nguyên) có 15 file đổi và 11 file thêm. Bằng chứng Codex (26 file) và snapshot 46 file giữ nguyên hash. SHA-256 của `fix-02/manifest.json`: `6c18d7c5d09c5a43859f9325ee87eb6c2c9886657161501db1b330c04dc2bc51`.

**Cần Codex retest:** chạy lại các lệnh ở verification §8.3, đặc biệt `fix-02/fail_before.py` và hai script của `codex-retest01/` trên cây hiện tại.

**Còn mở:** fixture ZER-41 và runtime theo runbook §3 (gồm `CART_MARKERS` thật); ack 202 nếu dùng H gateway Kafka; ràng buộc trang xác nhận đơn; `samples_after_trial_end`. Test thời gian dùng biên 0,1–0,4 s trên Windows; Codex nên chạy lại trên máy mình.

Không lab, API, model, Linear, commit/push/PR hay nhắn agent khác. Writer trả Codex; source đóng băng tới khi có kết quả retest.


## Codex retest fix-02 — ZER-10 + ZER-38 — CHANGES_REQUIRED_OFFLINE — 20/10/2026

[Report](../../../evidence/ZER-10/codex-retest02.md), SHA-256 2e5e462e0da9d52ba7db7bd28ec655578bd0feb2ba5774ec06d5cb2f33fe44bb. HEAD55200c9, staged rỗng. Intake checker57file/protected28/review26/snapshot46 khớp; source giữ nguyên. Kiểm độc lập125/125 Python3.12.4, E0130/60/90/19, fail-before PASS và7/7 counterexample trước sai/sau đúng, replay29/29, crosscheck178/178. Một số fail-before là khác API/signature; không coi mọi test error trước là chứng minh lỗi hành vi. Ma trận scorer72ca không crash/giữN, FX01-R3 đạt; journal CLI bền và frozen cleanup đạt các case đã sửa.

Còn hai P2: **FX02-R1** redirect307/308 dùng cookie vừa đổi để POST trước khi kiểm session, xóa giỏ foreign-user giả trên loopback; cleanup cuối đã an toàn nhưng side effect xảy ra trước đó. **FX02-R2** stop trong H ACK/reference/cleanup không rút ngắn I/O đang chạy: grace0,3s nhưng kết thúc sau stop1,40–1,44s; control nhanh đạt. P3**FX02-N1** conflict call_id xuyên incident mất bucket incident đầu, top-level vẫn MISSING. Evidence portable trong codex-retest02/. Chưa độc lập chạy lại mutant/Bandit/3.11/remoteCI; không lab/API/model/publication/Linear write.

**Gói fix-03 khi Claude nhận writer:** trước patch, đối chiếu contract trong mục hiện hữu này vì ownership/deadline đã lặp hai lượt: (1) kiểm danh tính trước mọi request/hop, giữ cleanup immutable credential/target; (2) mốc stop sớm nhất có hiệu lực với I/O đã bắt đầu, workload cancel và cleanup/grace khác nhau, stop lặp không gia hạn. Không vá riêng biểu hiện/test hoặc tăng grace để qua kiểm. Snapshot byte-identical fix-02 trước sửa; sửa gom FX02-R1/R2 và N1 trong measurement/tests/docs liên quan; giữ event_pipeline/lockedcontract/agents/worker/CI ngoài scope trừ thay đổi test gọi API mới thật sự cần thiết. Bằng chứng/manifest/snapshot cũ và Codex report chỉ đọc, delta để fix-03. Regression negative/control với stop sau khi server nhận request (H/reference/cleanup/finalflush), foreign-session307/308/multihop và same-session, M11cross-incident. Fail-before dùng hành vi thật; chạy affected suite125/crosscheck/replay và cập nhật verification/hash. Trả READY_FOR_CODEX_RETEST_OFFLINE một gói. Chưa lab/API/model/commit/push/PR/merge/Linear/message sang chat khác.

Linear đọc đúng workspace zero-door: ZER-10/38 vẫn In Progress, AC chưa tích; AC01PARTIAL chờ fixture/runtime, G1 chưa đóng. Writer review đã kết thúc, Claude nhận writer khi bắt đầu gói được Hoàng giao.


## Codex nhận thực hiện fix-03 — 20/10/2026

Hoàng giao trực tiếp hoàn thành đúng AC sau retest fix-02; Codex nhận writer, không chuyển từng lỗi lại Claude. HEAD55200c9, nhánh zer-10-independent-measurement, staged rỗng; snapshot57file byte-identical trước sửa ở fix-03/before và before.json. Phạm vi sửa chính xác: measurement/flows.py, probe.py, sink.py, clock.py, metrics.py; regression trong tests/test_measurement_probe.py và test_measurement_metrics.py; thiết kế/runbook/verification cùng bằng chứng fix-03 mới. Không sửa contract/event_pipeline/agents/worker hoặc bằng chứng cũ. Invariant: session đã được cấp không thể đổi trước bất kỳ hop tiếp theo; stop sớm nhất rút ngắn deadline dùng chung của I/O đang chạy nhưng cleanup được phép chạy trong grace; call_id conflict đánh thiếu dữ liệu ở mọi incident liên quan, chỉ đếm một call toàn run. AC01 cần fixture và quan sát thật, không dùng mock thay; hoàn tất phần sửa/kiểm rồi xác định scope runtime cụ thể trước vận hành.

Fix-03 bổ sung scope cần thiết trước kiểm cuối: tests/test_measurement_boundaries.py (regression socket thật); infrastructure/scripts/verify-measurement.py (giữ guard offline chặn DNS trước connect khi client TCP dùng nonblocking). Deadline động cũng áp dụng TLS handshake/send; không chỉ vá nhánh recv. DNS của OS vẫn đồng bộ; runtime chỉ dùng IP literal.

## Quyền runtime của Hoàng — 20/10/2026

Hoàng trả lời trực tiếp “Cho phép lượt lab giới hạn này”: k3d-zero-door; namespace tạm cho H/probe + fixture SQLite tối thiểu; tối đa15phút,30giao dịch mỗi đích; scale frontend/checkoutservice về0 từng dịch vụ một và trả đúng replica ban đầu; chỉ dọn tài nguyên của lượt này, giữ raw/evidence; không LLM/API trả phí. Scope mới: docs/evidence/ZER-10/runtime-01/{acceptance.py,run.sh,Dockerfile,pod.yaml,source-manifest.json,receipts/raw}; fixture này chỉ là CRUD prerequisite cho AC01, không đóng ZER-41 hoặc tuyên bố SQLi. Đã đọc context đúng; frontend1,checkoutservice3, không HPA; không policy target-app cần sửa. Probe/harness/H chạy cùng pod cùng clock HOST_SHARED; H loopback file archive direct201, không Kafka202. Image build local base9ae6f5…, --network=none. Giữ baseline/UID để rollback đúng; lỗi thì khôi phục dịch vụ và bảo toàn namespace/evidence, không tự chạy lại.

Publication preparation found core.autocrlf=input. To retain accepted raw/snapshot/source hashes across Windows/Linux, scope now includes .gitattributes entries limited to the measurement package and ZER-10 artifacts (same exact-byte policy already used for ZER-9); original file saved as fix-03/gitattributes-before.txt. No code behavior changes. Root check_package.py dispatches to sealed fix-03/check.py; historical checker source is in before snapshot.

## Codex hoàn tất sửa và nghiệm thu kỹ thuật ZER-10/38 — 20/10/2026

[Fix-03](../../../evidence/ZER-10/fix-03/README.md) khép FX02-R1/R2/N1 theo invariant, snapshot57file nguyênbyte, fail-before17subcase/3controlmethods,134/134test/E0130-60-90-19,29/29replay,178/178crosscheck,40mutantcaught qua31+9resumed/control107, Bandit0. Hai lens review độc lập không cònP1/P2. Rootchecker trỏ manifestfix03; source/rawevidence cóattributes giữbyte quaGit.

[Runtime-01](../../../evidence/ZER-10/runtime-01/README.md) theo quyền Hoàng:24mẫu/8phase/66rawrecord,2đích thật Boutique vàSQLite; frontenddown/checkoutdown/DBexclusive-lock đượcprobephát hiện, healthy/recovery saukhôiphụcđạt. Auditđộclậphash/ID/seq/thờiđiểm/cadence/spec/rollbackPASS. Frontend1/1,checkout3/3;DB0row;3namespacekhôngcòn. Successfulpod321.7s;21giao dịchBoutique gồmfailedwarmups và9fixture tổngqua cáclầnchuẩnbị, dưới30/đích. Giữ coldtimeout, failedwarmup, sự cốCRLFrollbackđãkhắcphục,watchdeletehếtgiờ vàreadbackcleanup. KhôngLLM/APItrảphí.

AC01 = ZER38 cóPASSruntime;AC02–04 cóPASScontrolledrawrecomputevàmetriccases. Không gánKPIformal/detector/LLMchoacceptanceprofileN0EMPTY,khôngđóngZER41/G1. Hoàng vừa cấp publication trực tiếp:commit/push/mởPRđúnggói. CònremoteCI,mergevàHoàngchấpnhậntrướcDone;chưaLinearwrite. NOWchỉstagecon trỏmới,cácdirtyownerngoàigóigiữnguyên.
