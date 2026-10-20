## Con trỏ mới — ZER-10/38: fix-03 + runtime PASS, chuẩn bị PR — 20/10/2026

[Fix-03](../evidence/ZER-10/fix-03/README.md):134test/178crosscheck/29replay,40mutantcaught (resumed),Bandit0; hai reviewlens không cònP1/P2. [Runtime](../evidence/ZER-10/runtime-01/README.md):8phase/24sample/66raw,healthy/failure/recovery Boutique+SQLite thật; replica1/3 và3namespace đã cleanup, rawauditPASS. AC01 córuntime,AC02–04 cócontrolledrawverification; khôngclaimKPIformal hayZER41Done. Hoàng cấp commit/push/mởPR; chờCI/merge/owneracceptance, chưaLinearDone. Handoff cuối [note](milestones/R1-measurement/probes-and-metrics.md).

## Con trỏ mới — PR25 ZER-12/40: sửa đường fixture CI — 20/10/2026

[PR25](https://github.com/EurusDevSec/Zero-Door/pull/25), implementation c2edee8 đã push. Run đầu14 job đạt,1 contract gate thiếu scratch fixture; [ci-01](../evidence/ZER-12/ci-01/README.md) dùng fixture đã commit, clean archive replay+test đạt, chuẩn bị push delta CI và chờ run mới. Không đổi contract/history. Chưa merge/Linear/Done. Handoff cuối [note](milestones/R1-measurement/guards-and-ci.md).

## Con trỏ mới — Codex khép N1–N4 ZER-12/40 — 20/10/2026,00:05 +07

[fix-02](../evidence/ZER-12/fix-02/README.md) khép bốn ghi chú P3 sau Claude RETEST_PASS_OFFLINE. 36 method/69 lượt trên hai production graphs + consumer đạt;24 fail-before subcase,20 mutant Claude,OpenAPI/Bandit đạt. Source seal79; evidence cũ giữ nguyên. F9 residual vẫn ghi rõ. Chờ quyền publication cho commit/push/PR/CI, rồi owner acceptance/merge; chưa Done, chưa lab/model/Docker/Linear write. Handoff cuối [note](milestones/R1-measurement/guards-and-ci.md).

## Con trỏ mới — Claude retest fix-01 ZER-12 + ZER-40: PASS offline — 19/10/2026

[Báo cáo retest](../evidence/ZER-12/claude-retest.md): F1–F8 và F10 đã sửa, kiểm độc lập trên Go 1.21.13 và hai pin production; F9 vẫn là residual như đã ghi. Không còn P1/P2. Có 4 ghi chú P3 không chặn: N1 gate manifest còn bỏ lọt vài mutant wiring, N2 thông điệp UNKNOWN, N3 hai Secret operator phải khác giá trị, N4 nên dùng strategy Recreate. AC-01, AC-02 và AC-03 = ZER-40 PASS offline, chưa Done: còn CI từ xa (race, image) và owner acceptance. Handoff ở cuối [note](milestones/R1-measurement/guards-and-ci.md). Writer trả Codex/Hoàng.

## Con trỏ mới — Codex sửa gom ZER-12/40, chờ Claude retest — 19/10/2026, 23:28 +07

[fix-01](../evidence/ZER-12/fix-01/README.md): F1–F8/F10 đã sửa và retest offline, F9 residual AUTO/healer disabled ghi rõ.102 method Python riêng biệt/133 lượt trên production pins + hồi quy,22 Go/vet/Linux/SAST đạt; before replay bắt đúng lỗi. Gói Claude retest ở cuối [note](milestones/R1-measurement/guards-and-ci.md), source đóng băng. Evidence/manifest v1 giữ lịch sử; dùng fix-01/verify_fix.py cho checksum mới. Chưa remote CI/Docker/lab/model/publication/Linear/Done; HEAD c09452a,staged rỗng.

## Con trỏ mới — Claude review ZER-12 + ZER-40: CHANGES_REQUIRED — 19/10/2026

[Báo cáo gom](../evidence/ZER-12/claude-review.md): 1 P1 (key ZD_* nằm trong metadata, không tới được container), 4 P2 (claim UNKNOWN khi chưa publish; redelivery sau expiry; llm-plan gate theo B2/B3; test chạy trên dependency khác image), 5 P3. Cả AC-01/02/03 = ZER-40 đều CHANGES_REQUIRED, không Done. Kiểm offline, không sửa source. Handoff ở cuối [note](milestones/R1-measurement/guards-and-ci.md). Writer trả Codex; Hoàng cần chốt F4.

## Con trỏ mới — Codex triển khai trọn ZER-12 + ZER-40, chờ Claude review — 19/10/2026

[Verification](../evidence/ZER-12/verification.md): OFFLINE_PASS, 99 test Python/17 test Go, vet/build Linux/SAST/hồi quy đạt; manifest khóa source hiện tại. [Gói review Claude](milestones/R1-measurement/guards-and-ci.md) ở cuối note: review cả ba AC cha và child AC-01, một báo cáo gom, không sửa source hay vận hành. Healer R1 disabled; remote CI/Docker/runtime/merge/owner acceptance chưa có. HEAD c09452a, branch zer-12-command-guards, staged rỗng, dirty ngoài gói giữ nguyên. Codex đóng băng source tới khi nhận review; writer báo cáo chuyển khi Hoàng gửi yêu cầu cho Claude.

# Checkpoint phiên

## Con trỏ mới — Điều chỉnh gói trọn ZER-12 + ZER-40 — 19/10/2026, 21:05 +07

Hoàng yêu cầu làm trọn cha/con. [Điều chỉnh cuối note](milestones/R1-measurement/guards-and-ci.md#điều-chỉnh-gói--thực-hiện-trọn-zer-12-và-zer-40--19102026-2105-07) thay giới hạn gói 20:47: Claude triển khai AC-01/02 của ZER-12 và đầy đủ AC-03 = ZER-40, gồm mode guard/CI theo contract đã khóa; không mặc định chờ toàn bộ ZER-11. Dashboard/KPI/profile B0 thật vẫn thuộc ZER-11/39. Một gói review cho cả cha/con, giữ quyền offline và dirty/evidence; không tự lab/model/publication/Linear/Done. Khi nhận đọc cả gói 20:47 và điều chỉnh này, chụp baseline hiện hành, writer chuyển Claude khi Hoàng gửi prompt.

## Con trỏ mới — Gói Claude ZER-12 guard và CI — 19/10/2026, 20:47 +07

Hoàng yêu cầu chuẩn bị Claude thực hiện; [gói cuối note](milestones/R1-measurement/guards-and-ci.md#gói-claude-thực-hiện-zer-12--19102026-2047-07) khóa scope guard/auth/schema/dedup/budget và phần CI ZER-40 làm được ngay. Baseline HEAD4bec8ce, origin/main c09452a cùng cây mã; staged rỗng, dirty quy ước giữ nguyên. Claude nhận writer khi Hoàng gửi prompt, tạo/reuse nhánh zer-12-command-guards, triển khai và tự kiểm offline rồi trả Codex review một gói. Không lab/model/Git publication/Linear write; mode còn thiếu đối chiếu ZER-11, không tự đóng ZER-12/40 hay G1. ZER-9 đã hoàn tất, không mở lại evidence cũ. Snapshot chuẩn bị/bàn giao ở scratch/zer12/.

## Con trỏ mới — ZER-9: gói cuối và publication — 19/10/2026

[Evidence](../evidence/ZER-9/actor-runtime/README.md): runtime10/10, đối chiếu độc lập68/68, verifier4/4. Nguồn cuối fix-03 đã chạy bằng pod actor production; cleanup nonce hoàn tất. Commit implementation b47e77d và [PR24](https://github.com/EurusDevSec/Zero-Door/pull/24) giữ package; trạng thái CI/merge xem trực tiếp tại PR, nghiệm thu/Done xem [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet). Hoàng yêu cầu hoàn tất và cho phép publication/cập nhật Done sau đủ kiểm. Gói này không đóng G1. Dirty quy ước ngoài ZER-9 giữ nguyên.

## Con trỏ mới — Codex retest fix-03 ZER-9: READY_OFFLINE — 19/10/2026

[Review](../evidence/ZER-9/codex-fix03-review/README.md): không còn finding chặn fix-03; core22/regression42/agentHTTP4,30subcase fail-before,bốn probe cũ và6probe độc lập đạt. Hash nguồn/bằng chứng cũ khớp phạm vi. [Runtime đề xuất](../evidence/ZER-9/codex-fix03-review/runtime-scope.md) cho source cuối trên pod Gaia/Hephaestus, chưa được chạy; không dùng live11 host-process thay proof actor. HEAD2af4d33, staged rỗng; Linear In Review, không ghi. Codex writer; chưa lab/API/publication/CI/merge/nghiệm thu. Bàn giao nối cuối [issue note](milestones/R1-measurement/event-contract.md).

## Con trỏ mới — Claude fix-03 ZER-9 (FX02-R1 lỗi đọc nguồn): READY_FOR_CODEX_RETEST — 19/10/2026, 19:45 +07:00

Claude đã khép FX02-R1 chỉ bằng `store.py`, cùng regression, runbook và verification; gateway không đổi. [fix-03](../evidence/ZER-9/fix-03/README.md) có ma trận nguồn/đích, finding→fix→test→hash và kiểm bảo vệ.
- Mọi đọc nguồn archive (stat/open/read/hash/copy-đọc) lỗi đều thành ArchiveFailure và sticky: `GET /events` 503, readyz 503, request sau 503, không thêm byte; H/O trực tiếp và Kafka. File vắng là trống, EIO/quyền không bao giờ thành trống.
- Lỗi đích export (ENOSPC, bản sao lệch, chmod, fsync) chỉ làm export thất bại; nguồn Ready. Trước đây bản sao lệch làm dừng nguồn khỏe.
- Regression 42/42. Trên snapshot fix-02: 4 method mới fail (30 subtest đúng lý do), control đạt. Bốn probe Codex chạy nguyên bản và assert theo giá trị đều đạt. Core 22/22, agent 4/4, `reconcile_raw` 57/58 như trước.
- Source chưa chạy live, CI chưa chạy. Codex retest độc lập; Hoàng giữ quyền nghiệm thu.

Bàn giao cuối [issue note](milestones/R1-measurement/event-contract.md). HEAD 2af4d33, không commit/Linear. **Writer trả Codex.**

## Con trỏ mới — Codex retest fix-02 ZER-9: còn một P2 nhánh đọc nguồn FX02 — 19/10/2026

[Báo cáo](../evidence/ZER-9/codex-fix02-review/README.md): core22/regression38/agentHTTP4/Bash37/Nemesis3/release9 đạt; cả hai phản ví dụ cũ đã sửa đúng. Probe mới: nguồn raw EIO khiến HTTP ngắt, readyz200/POSTsau201; export đọc late/global cũng không sticky. Một P2 FX02-R1, chưa nghiệm thu. Gói Claude fix-03 nối cuối [issue note](milestones/R1-measurement/event-contract.md): hoàn tất ranh giới lỗi nguồn/đích, offline only. Source fix-02 khớp hash; raw/receipt cũ giữ nguyên. HEAD2af4d33, staged rỗng; Linear đọc In Review, không ghi. Không lab/API/Git publication. Writer Codex tới khi Hoàng chuyển prompt cho Claude.

## Con trỏ mới — Claude fix-02 ZER-9 (FX01/FX02): READY_FOR_CODEX_RETEST — 19/10/2026, 18:50 +07:00

Claude đã sửa hai P2 của Codex retest trong allowlist (gateway/store/audit, regression, runbook, verification) và kiểm offline. [fix-02](../evidence/ZER-9/fix-02/README.md) có finding→fix→test→hash, kiểm bảo vệ và giới hạn.
- FX01: JSON lồng quá 32 tầng là INVALID trước validator. Quarantine giữ bytes/hash rồi mới commit; event kế tiếp được ghi; restart không gặp lại poison.
- FX02: lỗi ghi/fsync/đọc toàn vẹn làm archive H/O dừng hẳn. `/readyz` 503, request sau 503, không thêm byte; mở lại từ chối dòng bị cắt. Không tự sửa file; phục hồi là restart process, do operator làm.
- Retest: core 22/22, regression 38/38. Trên snapshot fix-01: 8 test mới/sửa fail, control đạt. Hai probe Codex chạy nguyên bản ra hành vi mới. Agent HTTP 4/4, Bash/Nemesis/ZER-37 đạt. `reconcile_raw` 57/58 như trước.
- Source mới chưa chạy live, CI chưa chạy. Codex retest độc lập; Hoàng giữ quyền nghiệm thu và quyết định bằng chứng trên actor.

Bàn giao cuối [issue note](milestones/R1-measurement/event-contract.md). HEAD 2af4d33, không commit/Linear. **Writer trả Codex.**

## Con trỏ mới — Codex retest fix-01 ZER-9: còn hai lỗi P2 — 19/10/2026

[Báo cáo](../evidence/ZER-9/codex-fix01-review/README.md): test cũ core22/regression30/agentHTTP4/Bash37/Nemesis3/release9 đạt; hai phản ví dụ độc lập vẫn fail: deep JSON thoát quarantine/poison recorder và H vẫn Ready/nhận201 sau ghi raw dở. Gói Claude fix-02 đã nối cuối [issue note](milestones/R1-measurement/event-contract.md), phạm vi gateway/store/tests và offline retest, không đổi contract. Codex không sửa sản phẩm; writer chỉ chuyển Claude khi Hoàng gửi prompt. Raw/receipt lịch sử giữ nguyên, source hiện tại chưa live/CI/merge/Hoàng nghiệm thu; Linear ZER-9 read-back In Progress. Không lab/API/publication/Linear write.

## Con trỏ mới — Claude sửa gom ZER-9 (fix-01): READY_FOR_CODEX_RETEST — 19/10/2026, 17:00 +07:00

Claude đã sửa ZR9-01…14 trong allowlist và kiểm offline; [fix-01](../evidence/ZER-9/fix-01/README.md) có bảng finding, AC→test, hash và giới hạn.
- Blocker đã sửa: recorder quarantine rồi commit, lỗi I/O thì dừng và `/readyz` 503; seal chờ offset đã ack, chưa xong thì 409; late/rejection/archive-scope vào export; audit so theo token, đủ `attack_type`/`reveal_terms`.
- Retest: core 22/22, regression mới 30/30 (trên source cũ 29/30 fail), agent HTTP 4/4, Bash/Nemesis/ZER-37 đạt. `reconcile_raw` 57/58: chỉ lệch hash source vì đã sửa.
- Live-11 giữ nguyên, là bằng chứng của source cũ. Source mới chưa chạy live, CI chưa chạy.
- Codex retest độc lập. Hoàng quyết có cần kiểm trên chính actor ([plan](../evidence/ZER-9/fix-01/runtime-plan.md)) trước Done.

Bàn giao cuối [issue note](milestones/R1-measurement/event-contract.md). HEAD 2af4d33, không commit/Linear. **Writer trả Codex.**

## Con trỏ mới — giao Claude sửa gom ZER-9 sau review — 19/10/2026

Codex xác nhận các blocker recorder/quarantine/audit bằng source và replay offline;10/10 phản ví dụ còn lệch, raw live-11 đối chiếu58/58. AC sống ZER-9 vẫn In Progress. [Gói sửa Claude](milestones/R1-measurement/event-contract.md#gói-claude-sửa-gom-zer-9-sau-review--19102026) cuối note có allowlist, retest và yêu cầu bảo toàn receipt cũ. Claude nhận writer sửa offline khi Hoàng chuyển prompt; cuối gói trả Codex. Không lab/API/install/publication/Linear; không nhận host+observer là bằng chứng quyền actor thật. Sau sửa mới retest và chốt kiểm tích hợp cần thiết trước nghiệm thu.

## Con trỏ mới — Claude review ZER-9: NOT_READY — 19/10/2026, 16:14 +07:00

[Claude review](../evidence/ZER-9/claude-review.md) (SHA-256 `86fc9238…1403c4`) có 3 P1 chặn: recorder Kafka chết vĩnh viễn khi gặp message lỗi, seal lúc còn event in-flight hoặc lỗi binding (ZR9-01); rejection/LATE_INGEST không được lưu hoặc không vào export (ZR9-02); audit so nhãn sai, báo rò nhầm trên trace sạch C0–C5 và bỏ sót `reveal_terms`/`attack_type` (ZR9-03). Raw live-11 đối chiếu độc lập đạt 58/58; test offline đều xanh. AC-01 PASS; AC-02/03 FAIL đến khi sửa. Gói sửa hợp nhất cho Codex nằm cuối [issue note](milestones/R1-measurement/event-contract.md). Không lab/API, commit/push hay Linear; HEAD 2af4d33. **Writer trả Codex.**

## Con trỏ mới — ZER-9 triển khai và kiểm live xong, chờ Claude xác nhận — 19/10/2026

Nhánh zer-9-event-pipeline, HEAD2af4d33, chưa commit/stage. [Verification](../evidence/ZER-9/verification.md): core22/22, source-agentHTTP2/2, live-11 **18/18 PASS**; raw H/O seal/hash và cleanup read-back đạt. Lỗi enforcement theo node được giữ đầy đủ: agent0 không có pod firewall chains; profile cuối khóa toàn bộ vào server và gate quyền trước data. Chỉ chứng minh transport với payload synthetic, không phải fault/KPI/rollout legacy. Hoàng đã duyệt namespace/PVC/topic tạm và rule ES tạm; tất cả tài nguyên tạm đã dọn, không thay node/firewall/lab cũ hay gọi API model. [Gói Claude xác nhận](milestones/R1-measurement/event-contract.md#claude-xác-nhận-zer-9--gói-cuối-19102026) cuối issue note giữ scope/source/hash và các điểm review. Codex chốt writer; Claude chỉ nhận review writer sau khi Hoàng chuyển prompt. Chưa Claude review, nghiệm thu, CI/publication/merge hoặc Linear write; ZER-9 read-back In Progress, G1 chưa đóng. Dirty quy ước giữ nguyên.

## Con trỏ mới — ZER-9 triển khai, chờ quyền kiểm live — 19/10/2026

Writer Codex trên zer-9-event-pipeline, HEAD2af4d33. [Verification](../evidence/ZER-9/verification.md): core22/22, source Gaia/Hephaestus thật qua HTTP loopback2/2, Bash/Nemesis/contract hồi quy đạt. [Runbook](../runbooks/r1-event-pipeline.md) và cuối [issue note](milestones/R1-measurement/event-contract.md) có phạm vi, lệnh và handoff. Chưa Done/chuyển Claude vì chưa có runtime Kafka/PVC/quyền thật; automatic approval review chặn verifier live do thiếu phê duyệt trực tiếp cho tạo/dọn namespace/topic/PVC tạm. Chưa chạy lại, chưa lab mutation, commit/push/merge hoặc Linear write. Bước kế: Hoàng cho phép gói live cụ thể; Codex chạy/sửa gom rồi mới giao Claude xác nhận cả gói. ZER-37 giữ Done/contract1.0.0; G1 chưa đóng.

## Con trỏ mới — ZER-37 hoàn tất ngày19/10/2026

**ZER-37 Done đã read-back trên Linear Zero Door; contract khóa zd-event/1.0.0, Hoàng đã nghiệm thu.** [PR#23](https://github.com/EurusDevSec/Zero-Door/pull/23) merge2af4d33bf02c59d7802901d523b1bb2eb39f05a3; [PR CI7/7](https://github.com/EurusDevSec/Zero-Door/actions/runs/39215988500), [main CI8/8](https://github.com/EurusDevSec/Zero-Door/actions/runs/39216183044) SUCCESS gồm GHCR. Main khớp7file đã review/test. Commit publication5644939, nhánh zer-37-event-contract. [Contract immutable](https://github.com/EurusDevSec/Zero-Door/blob/2af4d33bf02c59d7802901d523b1bb2eb39f05a3/docs/design/r1-event-contract.md) SHAfe09beb5; [verification](../evidence/ZER-37/verification.md)238/238,32/32mutant,10/10independent,9/9release.

Không lab/API hoặc production implementation mới. Dirty quy ước/NOW giữ riêng; ZER-9 read-back In Progress, AC-02/03 và G1 chưa hoàn thành; lượt này không có lệnh riêng đổi trạng thái cha. Chưa tự mở issue/gói implementation tiếp theo. Writer Codex kết thúc publication; không agent nào đang ghi.

## Con trỏ mới — 19/10/2026, 14:19 +07:00

**ZER-37 audit cuối READY_FOR_ACCEPTANCE.** [Báo cáo](milestones/R1-measurement/event-contract.md#codex-audit-cuối-zer-37--19102026-1419-0700): 238/238,32/32 mutant,10/10 phản ví dụ,9/9 delta,33/33 đóng gói. Contract DRAFT0.2.0 SHA469a081d, không còn finding chặn, không cần trả Claude. Chờ Hoàng nghiệm thu PROP và quyền publication để khóa1.0.0/đóng ZER-37. Live37InProgress,9Todo; cha9 và G1 chưa đóng. Không lab/API/publication/Linear writes. HEAD42af1c1, dirty ngoài scope giữ nguyên.

## Con trỏ mới — 19/10/2026, 14:10 +07:00

**Claude đã sửa gom RV37-01…05 của ZER-37; writer trả Codex retest.** [Contract](../design/r1-event-contract.md) vẫn DRAFT_FOR_REVIEW, `zd-event/0.2.0`, SHA-256 `5c30a324…3b04da`. Bàn giao cuối [event-contract](milestones/R1-measurement/event-contract.md) có bảng từng finding.
- Kiểm offline: 238/238 kỳ vọng; 32/32 mutant; kiểm gói 33/33.
- 10/10 ca của script Codex đạt; chạy trên bản sao chỉ đổi đường dẫn kết quả, không sửa tệp Codex.

Hai lựa chọn của Hoàng (`incident_id` ở O, CLOCK_UNVERIFIED) chờ sau retest. Không chạy lab/API, commit/push hoặc đổi Linear. HEAD 42af1c1; dirty ngoài phạm vi giữ nguyên.

## Con trỏ mới — 19/10/2026, 13:34 +07:00

**Codex review ZER-37: NOT READY, gom RV37-01…05 để Claude sửa một lượt.** Báo cáo và gói sửa ở cuối [event-contract](milestones/R1-measurement/event-contract.md). Contract gốc SHA7409c1a1 giữ nguyên; helper gốc129/129 và14/14 mutant đạt nhưng9 phản ví dụ độc lập còn lọt (clock, proof recovery, semantic validation/mode, linking); quy tắc rò tài nguyên quá rộng cần sửa. Không chạy lab/API, commit/push hoặc sửa Linear. Hai PROP cần Hoàng chấp nhận giữ chờ bản sửa/retest. Codex kết thúc ghi review; Claude nhận writer khi Hoàng chuyển gói, trả Codex sau tự kiểm.

## Con trỏ mới — 19/10/2026, 13:05 +07:00

**Claude đã hoàn thành bản contract ZER-37 để Codex review; quyền writer trả Codex.** [docs/design/r1-event-contract.md](../design/r1-event-contract.md) (DRAFT_FOR_REVIEW, `zd-event/0.1.0`), SHA-256 7409c1a1…94e21c. Bàn giao cuối [event-contract](milestones/R1-measurement/event-contract.md): ví dụ OFFLINE khớp 129/129 expectation, 14/14 mutant bị bắt, kiểm gói 24/24. Hai điểm cần Hoàng quyết sau review: `incident_id` ở O chỉ cấp trước onset; CLOCK_UNVERIFIED thành MISSING. Chưa sửa producer/consumer, chạy lab/API, commit/push hoặc đổi Linear; AC sống UNKNOWN với Claude. HEAD 42af1c1, dirty ngoài phạm vi giữ nguyên.

## Con trỏ mới — 19/10/2026, 12:43 +07:00

Hoàng yêu cầu bắt đầu R1: Codex đã lập [gói ZER-37 cho Claude](milestones/R1-measurement/event-contract.md#gói-zer-37-cho-claude--19102026-1243-0700) trên HEAD 42af1c1. Đầu ra là docs/design/r1-event-contract.md có version, ví dụ và ranh giới H/O/S theo ZER-32/8; chỉ tài liệu/kiểm offline. Claude nhận writer khi Hoàng chuyển prompt; Codex đã kết thúc ghi gói, chờ review tổng hợp, Hoàng nghiệm thu sau review. Giữ dirty work ngoài allowlist; chưa mở producer/consumer, lab/API, publication hoặc đổi Linear.

## Con trỏ mới — 19/10/2026, 12:33 +07:00

**Audit điều phối R1: điểm bắt đầu là ZER-37 trong ZER-9.** Đã đối chiếu Linear Zero Door (9/9 issue R0 Done và receipt G0 PASS), AC/relations của bốn cha ZER-9–12, bốn con ZER-37–40 và fixture ZER-41/13. Trình tự kỹ thuật và phần AC cha còn lại ghi tại [README R1](milestones/R1-measurement/README.md#trình-tự-triển-khai-theo-phụ-thuộc): khóa contract → truyền/lưu ID và tách evidence → chuẩn bị/kiểm guard trước thao tác có tác động → probe và phép đo → dashboard/mode/B0 → hoàn tất CI/guard và nghiệm thu G1. Các phần độc lập được chuẩn bị theo prerequisite thật, không thêm chuỗi blocked-by giả.

Probe fixture của ZER-38/10 còn phụ thuộc đầu ra R2 ZER-41/13; nếu chưa có fixture thật phải giữ phần runtime chưa đạt và báo quyết định scope trước khi đóng, không tự mở R2 hoặc thay AC. ZD2 đã audit/read-back, xác nhận thứ tự và yêu cầu chuẩn bị mode checks ZER-11 sớm để tránh vòng phụ thuộc fixture/CI; README đã bổ sung. Writer ZD1 cho README R1/NOW kết thúc sau kiểm cuối. Baseline checkout zer-36-g0-receipt HEAD42af1c1, dirty quy ước ngoài scope được bảo toàn. Lượt này chỉ điều phối/tài liệu, không mở implementation, chạy lab/API, sửa Linear hoặc publication; gói thực thi tiếp cần scope/quyền theo WORKFLOW.

## Con trỏ mới — 19/10/2026, 12:10 +07:00

**R0 đã nghiệm thu, G0 PASS.** PR [#21](https://github.com/EurusDevSec/Zero-Door/pull/21) merge250d385 (probe/design), PR [#22](https://github.com/EurusDevSec/Zero-Door/pull/22) merge2fc75d5 (receipt cuối). CI mỗi PR7/7; hai pipeline main8/8 gồmGHCR success, [run cuối](https://github.com/EurusDevSec/Zero-Door/actions/runs/39202786186). Linear read-back9/9issueR0Done; ZER-36/7/8 đủ1/3/3AC, milestone có verdict G0PASS và link immutable [receipt](../evidence/R0/g0-acceptance.md), SHA81723b19267afbd58baaaa0961b21dcaa97a20541d5df8031288c2ba71749df9. Không thêm API/lab, không nâng hardlimit;10nguồn protected giữ nguyên hash. Dirty quy ước/AGENTS/README/WORKFLOW/WORKING-AGREEMENT giữ riêng, NOW là con trỏ local. Writer Codex; không giao agent hoặc tự mở R1. Khi chọn tiếp, rà gate/AC cha-con/prerequisite R1 trước. GitNexus session95836 hoàn tất exit0 (3033nodes/3693edges), thay đổi sau đó chỉ publication/docs.

## Con trỏ mới — 19/10/2026, 11:52 +07:00

**Gói sửa hai P2 đã đạt retest và đang trình Hoàng nghiệm thu/publication.** [Bản đối chiếu G0](../evidence/R0/g0-acceptance.md) ghi rõ 14 file dự kiến publication và các giới hạn. Suite 12/12, 14/14 mutant bị bắt, đối chứng sạch đạt; probe và receipt thật giữ nguyên hash. CI mới thêm một bước kiểm offline, chưa có CI remote. Không gọi API/lab hoặc commit/push/PR/merge/ghi Linear. Cần Hoàng chấp nhận ZER-36/ZER-7/ZER-8 và cấp quyền publication; merge/cập nhật Done chỉ sau CI đạt ở head cuối. Workflow main hiện có job đẩy image GHCR. GitNexus index-only session 95836 còn chạy lúc kiểm 11:51:45 +07; kiểm session/meta trước khi khởi chạy lại.

## Con trỏ mới — 19/10/2026, 11:49 +07:00

**Codex đã sửa hai P2 và retest12/12 +14/14 mutant, probe/raw/review giữ nguyên.** [Gate G0 đang trình](../evidence/R0/g0-acceptance.md), [retest](../evidence/ZER-36/retest.json), handoff cuối [llm-backend](milestones/R0-foundations/llm-backend.md). RV36-01 đã thêmcoverage curl28/6/7,retryẩn và mộtstepCIoffline; RV8-06 đã tách ràvariant khỏi lịchtrialniêmphong choBM. PR #20 đãmerge main ab800056 tree khớp df5d542. ZER36/7/8 sốngđềuInProgress;góiđủkỹthuật,chờHoàngnghiệmthu/quyềncommit-push-PR-CI-merge/Linear. KhôngAPI/labmới,khôngpublication/Linear. Dựkiếnnhánhzer-36-r0-acceptance,giữdirtyngoàiscope.

## Con trỏ mới — 19/10/2026, 11:40 +07:00

**Claude đã review độc lập ZER-36/ZER-7, delta ZER-8 và G0; quyền ghi trả Codex.** [Báo cáo](../evidence/ZER-36/claude-review.md) SHA-256 8413a2ab…6fcfbe; bàn giao cuối [llm-backend](milestones/R0-foundations/llm-backend.md). Hai P2 cần sửa trước nghiệm thu: RV36-01 (test chưa phủ timeout curl exit 28/6/7 và `--retry 0`; chỉ sửa test, giữ probe 37de4d63) và RV8-06 (ground truth từng trial do Hoàng rà mâu thuẫn che thứ tự/onset cho BM). ZER-36 AC-01 PASS kỹ thuật; ZER-7 AC-02 PASS, AC-03 PASS hành vi. G0 chưa đóng: còn sửa/retest, Hoàng nghiệm thu 36/7/8, commit/PR/CI/merge probe, chia sẻ tài liệu, Linear và receipt G0. AC sống UNKNOWN với Claude. Không API/lab/commit/push/Linear.

## Con trỏ mới — 19/10/2026, 11:28 +07:00

**R0 còn 36/7/8 trên Linear; gói review độc lập backend + G0 đã soạn cho Claude** ở mục “Gói Claude — review độc lập ZER-36/ZER-7 và đối chiếu G0” cuối [llm-backend](milestones/R0-foundations/llm-backend.md), chờ Hoàng chuyển. ZER-8 [mục13](../evidence/ZER-8/research-design.md) ghi quyết định Hoàng: pilot ≤5 USD API, ≤2 giờ/phiên, ≤8h lab tổng; Hoàng BM, harness giấu thứ tự/onset, ghi giới hạn biết thiết kế. Formal khóa sau pilot, B3/M1/B2 đã chốt giữ nguyên. Không tăng hard limit project1 USD, không chạy lab/API hoặc publication/Linear. Codex nhường writer khi Hoàng chuyển gói; Claude review-only, Codex sửa finding/retest. Chưa chốt G0 hoặc Done, chưa review độc lập/publication gói backend.

## Con trỏ mới — 19/10/2026, 11:22 +07:00

**ZER-36/ZER-7 có receipt inference thật và Codex retest PASS.** [Xác minh](../evidence/ZER-36/verification.md), [receipt](../evidence/ZER-36/live-receipt.json), handoff cuối [llm-backend](milestones/R0-foundations/llm-backend.md). Một call gpt-6-luna, 2969 ms, 259+68 token, estimate 0,0000599 USD; quota header 30k RPM/180M TPM. Schema/usage/hash khớp; model snapshot bất biến UNKNOWN. Timeout/retry/fallback chỉ fault injection OFFLINE có log riêng. Gói chờ review độc lập/nghiệm thu/publication; không thêm API, không commit/push/merge hoặc đổi Linear. G0 chưa nghiệm thu. GitNexus session 19594 đã hoàn tất exit 0, không chạy trùng.

## Con trỏ mới — 19/10/2026, 11:12 +07:00

**ZER-36/ZER-7: probe đã chuẩn bị và kiểm offline 8/8; chờ Hoàng chạy live qua Doppler.** Hướng dẫn [ZER-36](../evidence/ZER-36/README.md), handoff cuối [llm-backend](milestones/R0-foundations/llm-backend.md). Nguồn Hoàng: /models HTTP 200, gpt-6-luna 180M TPM/30k RPM, đã đặt 1 USD và hard limit; không phải Codex đọc dashboard. Lệnh: `doppler run -- bash infrastructure/scripts/verify-llm-backend.sh --live`; tối đa 2 attempts, 512 output token/attempt, fixture tổng hợp không lab. Receipt scratch/zer36/runs/run-<uuid>/receipt.json. Live còn PENDING, lỗi/fallback chỉ kiểm mô phỏng; G0 chưa nghiệm thu. Giữ dirty ngoài scope, không commit/push/Linear.

## Con trỏ mới — 19/10/2026, 08:24 +07:00

**ZER-5 đã nghiệm thu và publication hoàn tất.** Commit [df5d542](https://github.com/EurusDevSec/Zero-Door/commit/df5d542aaf726e62ea8ccb17a94490cd88322ee0), nhánh `zer-5-scope-acceptance`, đúng một file [scope-and-criteria](milestones/R0-foundations/scope-and-criteria.md); remote đọc lại khớp HEAD. Linear Zero Door đã read-back ZER-5 Done, ba AC checked, completedAt 2026-10-19T01:23:25.456Z. Nguồn SCOPE và artifact/review 32/33 giữ nguyên hash/byte; dirty ZER-8 và quy ước được bảo toàn, không gom vào commit. NOW là con trỏ local chưa commit. Kế tiếp vẫn ZER-36/ZER-7; ZER-8 còn nguồn lực/BM, trần kiểm backend 1 USD chưa duyệt; G0 chưa nghiệm thu.

## Con trỏ mới — 19/10/2026, 08:14 +07:00

**Hoàng đã nghiệm thu ZER-5 và chấp nhận hướng thiết kế ZER-8** trong chat: giữ B3 có điều kiện, M1 metric chính, B2 báo KPI phục hồi. Receipt cuối [scope-and-criteria](milestones/R0-foundations/scope-and-criteria.md), [research-questions](milestones/R0-foundations/research-questions.md) và [artifact mục 12](../evidence/ZER-8/research-design.md), SHA-256 43715562f431ed1c5cf60747e15d73304cc85508c6e0a6da95936e88e3c8f4b5. Ngân sách/giờ pilot-formal và tổ chức BM chưa chốt, nên ZER-8 AC-02 còn PARTIAL; trần 1 USD kiểm backend vẫn chưa duyệt. Chưa commit/push hoặc đổi Linear, chưa gọi API/chi tiền. Kế tiếp ZER-36/ZER-7: chuẩn bị backend và phép thử có giới hạn; không chọn lại B3/M1/B2. G0 chưa nghiệm thu.

## Con trỏ mới — 19/10/2026, 08:08 +07:00

**ZER-8/ZER-5 đã được Codex review và sửa gọn**, không cần gửi Claude thêm vòng cho RV8-01…RV8-05. [Artifact và review mục 11](../evidence/ZER-8/research-design.md), SHA-256 bb27ff8839b35cac1343f5a57eaaf5db39b3975662df56f2d8075436f93459a5; handoff cuối [research-questions](milestones/R0-foundations/research-questions.md), đối chiếu cha cuối [scope-and-criteria](milestones/R0-foundations/scope-and-criteria.md). ZER-5 PASS kỹ thuật cả ba AC, chờ Hoàng nghiệm thu. ZER-8 thiết kế đề xuất PASS sau sửa; AC-02 còn PARTIAL chờ chốt B3/claim/nguồn lực và phương pháp. 45/45 OFFLINE retest, 71 nguồn bảo toàn, không runtime mới. HEAD 968cc50, chưa commit/push/đổi Linear hoặc chi tiền. G0 chưa đạt: backend thật ZER-36/ZER-7 chưa có evidence mới.

## Con trỏ mới — 19/10/2026, 08:00 +07:00

**ZER-8 + đối chiếu ZER-5 đã bàn giao để Codex review.** Claude nhường quyền ghi cho Codex.

- [Artifact ZER-8](../evidence/ZER-8/research-design.md) SHA-256 51ee6e11…f0ec1adfd. Bàn giao ở mục “Bàn giao Claude — ZER-8 và đối chiếu ZER-5” cuối [research-questions.md](milestones/R0-foundations/research-questions.md); đối chiếu ZER-5 ở cuối [scope-and-criteria.md](milestones/R0-foundations/scope-and-criteria.md).
- **Kết quả:** ZER-8 AC-01 và AC-03 đủ để review; AC-02 PARTIAL vì quyết định B3/budget còn PENDING. ZER-5 có căn cứ nghiệm thu cả ba AC từ ZER-32/33 đã chấp nhận.
- **Cần Hoàng quyết sau review:** B3 và claim RQ2; trần USD pilot và quỹ giờ; người vận hành BM; chấp nhận các đề xuất phương pháp.
- AC sống chưa đọc (không có linear_zero_door). Không lab/API/chi tiền, không commit, không đổi Linear. Đoạn 07:42 bên dưới là trạng thái trước khi thực hiện.

## Con trỏ mới — 19/10/2026, 07:42 +07:00

Gói kế tiếp đã soạn cho Claude: **ZER-8 và đối chiếu ZER-5**, ở mục “Gói Claude — ZER-8 và đối chiếu ZER-5 — 19/10/2026, 07:42 +07:00” cuối [research-questions.md](milestones/R0-foundations/research-questions.md). Đầu ra chính dự kiến docs/evidence/ZER-8/research-design.md; chưa thực hiện. Baseline 968cc50 trên zer-34-lab-acceptance, giữ dirty có sẵn. Claude nhận writer khi Hoàng chuyển yêu cầu; Codex review cả gói sau tự kiểm/bàn giao. Chỉ tài liệu và offline, không lab/API/cost/publication/Linear. B3/claim/budget là đề xuất cần chốt sau review; 300 USD credit là nguồn người dùng, trần 1 USD kiểm backend chưa được duyệt. G0 chưa đạt, còn ZER-36/ZER-7 về backend thật.

## Con trỏ mới — 19/10/2026, 00:49 +07:00

**ZER-34 và ZER-6 đã được Hoàng nghiệm thu, commit/push và hoàn tất Linear.** Commit [968cc50f3797c243b8fa26e5327db647a8644802](https://github.com/EurusDevSec/Zero-Door/commit/968cc50f3797c243b8fa26e5327db647a8644802) trên nhánh zer-34-lab-acceptance đã push origin và ls-remote khớp. Hai file trong commit: báo cáo review ZER-34 và ghi chú local-lab; dirty quy ước/README/AGENTS/WORKFLOW/WORKING-AGREEMENT/NOW giữ riêng. Báo cáo SHA-256 d7e758476c7567ff5229f6c7a3d97751cda3c819ade2f979c65cb0ee68dd5a0c; inventory/report/note GitHub đã đọc lại khớp local tại đúng commit.

Read-back qua linear_zero_door: [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc) Done, 6 AC checked, completedAt 2026-10-18T17:48:57.910Z; [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local) Done, 3 AC checked, completedAt 2026-10-18T17:49:24.447Z. Cả hai có receipt nghiệm thu, link immutable và giới hạn. Không đổi assignment/dates/relations hoặc các issue khác. Không PR/merge mới cho gói tài liệu; source lab đã merge ở PR #19.

Nhóm lab đã nghiệm thu theo bằng chứng lịch sử 18/10 và metadata Docker chỉ đọc 19/10; không nhận KPI nghiên cứu hoặc toàn bộ lab hiện tại đã đo lại. G0 chưa nghiệm thu: kế tiếp đối chiếu ZER-5 từ 32/33 đã được chấp nhận, rồi ZER-8 và ZER-36/ZER-7 theo phụ thuộc thật. Nguồn người dùng: 300 USD credit OpenAI API; đề xuất trần 1 USD kiểm R0 chưa được duyệt, chưa gọi API.

Công cụ local: GitNexus analyze --index-only được khởi chạy sau commit (session 81802); lúc đọc 00:49 vẫn chỉ có banner, chưa có receipt hoàn tất. Không khởi chạy trùng; kiểm session/meta trước dùng graph. Không ảnh hưởng receipt Git/Linear ở trên.

## Con trỏ mới — 19/10/2026, 00:43 +07:00

**ZER-34/ZER-6 Codex review PASS kỹ thuật; chờ Hoàng nghiệm thu/publication/tracking.** [Báo cáo mục 9](../evidence/ZER-34/claude-review.md) SHA-256 d7e758476c7567ff5229f6c7a3d97751cda3c819ade2f979c65cb0ee68dd5a0c; handoff cuối [local-lab.md](milestones/R0-foundations/local-lab.md). AC sống đã đối chiếu; Docker chỉ đọc xác nhận năm container/năm volume có sẵn vẫn hiện diện, không kiểm nội dung. Giữ giới hạn create/start chỉ có mock; không cần wipe hoặc chạy lại lab cho AC hiện hành. Chưa commit/push hoặc đổi Linear. Không cần gửi Claude thêm vòng. R0 còn ZER-5, ZER-8 và ZER-36/ZER-7, G0 chưa được nghiệm thu.

## Con trỏ mới — 19/10/2026, 00:22 +07:00

**ZER-34 + đối chiếu ZER-6 đã bàn giao để Codex review.** Claude review xong inventory và đối chiếu bằng chứng ZER-35. [Báo cáo](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-34/claude-review.md) SHA-256 4107dcdf…5cf0bf. Tóm tắt ở mục “Bàn giao Claude — ZER-34 và đối chiếu ZER-6” cuối [local-lab.md](milestones/R0-foundations/local-lab.md).

- **Kết quả:** ZER-34 AC-01–05 PASS; AC-06 pending vì báo cáo review chưa được chia sẻ. ZER-6 AC-01–03 PASS kỹ thuật dựa trên bằng chứng lịch sử ngày 18/10; receipt PR #19 đã được kiểm lại.
- **Cần Hoàng quyết:** RV6-01 (nhánh create/start cluster bằng script chỉ có mock) và RV6-02 (chưa kiểm kê lại dữ liệu Docker có sẵn sau khôi phục): chấp nhận giới hạn hay giao bổ sung.
- Linear chưa đọc live; không commit/push, không đổi Linear, không chạy lab. Codex nhận quyền ghi để review. Đoạn 00:06 bên dưới là trạng thái trước khi thực hiện.

## Con trỏ mới — 19/10/2026, 00:06 +07:00

Ưu tiên theo yêu cầu Hoàng: khép R0 hôm nay, chưa chuyển trọng tâm R1. Gói kế tiếp cho Claude là **ZER-34 + đối chiếu nghiệm thu ZER-6** ở mục “Gói Claude — ZER-34 và đối chiếu nghiệm thu ZER-6 — 19/10/2026” cuối [local-lab.md](milestones/R0-foundations/local-lab.md). Chuẩn bị xong, chưa có kết quả thực thi gói mới. Codex nhường quyền ghi sau bàn giao; không mutation lab/Linear/Git publication. Baseline 10a26b0, giữ dirty quy ước có sẵn.

Rà Linear đầu ngày: 32/33/35 Done; 34/6 In Progress; 5/8/36/7 còn Backlog. Nhóm việc tiếp sau là đối chiếu nghiệm thu ZER-5 từ 32/33, khóa RQ/đối chứng ZER-8, chọn backend/budget và kiểm inference thật ZER-36/ZER-7; đây là ưu tiên, không thêm dependency nối tuần tự giả. G0 chưa đạt chỉ từ số issue Done.

Hoàng vừa cung cấp có khoảng 300 USD credit OpenAI API; đây là nguồn người dùng, chưa xác minh số dư/expiry/quyền model/quota. Codex đề xuất trần 1 USD cho kiểm chứng R0, chưa được duyệt, chưa gọi API; không ghi thành ngân sách đã chấp thuận.

Công cụ local: phiên GitNexus analyze --index-only cũ đã trả exit 0, indexed successfully (2.834 nodes/3.410 edges/26 clusters/44 flows); không cần khởi chạy trùng. Đây không là runtime proof.


## Con trỏ mới — 18/10/2026, 23:58 +07:00

**ZER-33 đã được Hoàng nghiệm thu, commit/push và hoàn tất tracking.** Commit [10a26b0a0001046b23f57f667a3cb7be33e69090](https://github.com/EurusDevSec/Zero-Door/commit/10a26b0a0001046b23f57f667a3cb7be33e69090) đã push lên origin/zer-33-baseline-source-ledger và ls-remote khớp local. Nhánh cũng chứa commit ZER-32 8e7b74f. [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) đã đọc lại Done, AC-01 checked, completedAt 2026-10-18T16:58:27.655Z; receipt có link artifact/review tại revision đã push. Artifact SHA-256 cbbd334caaeb3e03513939f1ab3563883073d48f38b487087e68ae67a0bb029d giữ nguyên. Chỉ 3 file ZER-33 trong commit; dirty quy ước/README/AGENTS/NOW được giữ riêng. Chưa tạo PR hoặc merge. G0 và issue cha ZER-5 chưa được đóng.

**Công cụ local:** đã gọi gitnexus analyze --index-only sau commit; chưa có receipt hoàn tất, meta lúc kiểm vẫn ở 8e7b74f. Không dùng graph như index đã cập nhật; kiểm tiến trình/meta trước khi khởi chạy lại. Việc này không chặn receipt commit/push và nghiệm thu tài liệu đã xác minh ở trên.

### Lịch sử review — 23:42

**ZER-33 review PASS sau Codex sửa gọn RV-01; chờ Hoàng nghiệm thu.** Đã đối chiếu AC sống ZER-33/ZER-5. [Review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/codex-review.md), artifact cuối SHA-256 cbbd334caaeb3e03513939f1ab3563883073d48f38b487087e68ae67a0bb029d. Sửa đúng 2 hàng dẫn nguồn tạo/start so với recreate; offline 128 OK, selftest 10/10, 42 nguồn bảo toàn. Không cần gửi thêm vòng Claude; chưa đổi Linear hoặc commit gói ZER-33. Không có bằng chứng runtime/G0 mới.

### Bàn giao Claude trước review — 23:30

**ZER-33 đã bàn giao để Codex review — 23:30.** Claude hoàn tất baseline và source ledger. [Artifact](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/baseline-source-ledger.md) SHA-256 383d0b6c…fa79d5. Bàn giao ở mục “Bàn giao Claude — ZER-33” cuối [ghi chú issue](milestones/R0-foundations/scope-and-criteria.md).

- **Kết quả:** 8 raw CSV/40 bản ghi ngày 25/06. Ledger L01–L30 phủ H01–H08. Kiểm offline 128 OK, 0 FAIL; 42 nguồn không đổi.
- **Còn lại:** AC sống chưa đọc; Codex cần đối chiếu khi review. Codex nhận quyền ghi để review, rồi Hoàng quyết định nghiệm thu.
- Không đổi Linear, không commit. Các đoạn 22:50/23:10 bên dưới là trạng thái trước khi thực hiện.

**ZER-32 đã được Hoàng nghiệm thu, gồm D-01…D-05.** [Artifact](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md) SHA-256 a5579b90…ba3a24c; [review và receipt](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md). Kiểm OFFLINE 190/190, 18/18 mutant bị bắt; không có KPI runtime mới. Receipt cập nhật tracking đã được đọc lại tại [ZER-32](https://linear.app/zero-door/issue/ZER-32/lap-ma-tran-yeu-cau-va-djinh-nghia-kpi); trạng thái sống đọc Linear. Gói ZER-32 đã commit local thành 8e7b74f1cacc87387e5f35d078e5b1bb48c318fe trên nhánh zer-32-requirements-kpi ngày 18/10/2026, 23:08 +07:00 (3 file: artifact, review và ghi chú issue); chưa push/PR/merge cho commit này.

**Gói giao ZER-33 — 18/10/2026, 23:10 +07:00:** Hoàng yêu cầu soạn gói cho Claude sau commit ZER-32. Chi tiết/allowlist/kiểm cuối ở mục “Gói giao Claude — ZER-33” cuối [ghi chú issue](milestones/R0-foundations/scope-and-criteria.md). Checkout đang ở zer-33-baseline-source-ledger, HEAD 8e7b74f; artifact ZER-33 chưa tạo. Claude thực hiện khi Hoàng chuyển yêu cầu, Codex nhường writer và sẽ review cả gói sau bàn giao. Không chạy lab/model hoặc tự sửa Linear/publication.

**Ưu tiên tiếp theo — điều chỉnh sau Hoàng nhắc backlog R0:** ZER-33 — chụp baseline và lập source ledger — để hoàn tất phần còn lại của ZER-5 sau ZER-32. Đầu ra theo AC: `docs/evidence/R0-T01-S03/baseline-source-ledger.md`; chưa bắt đầu thực hiện. Rà tiếp bằng chứng/nghiệm thu ZER-34/ZER-6, rồi các gói backend LLM ZER-36/ZER-7 và thiết kế nghiên cứu ZER-8. Đây là các nhóm cần khép R0, không tự áp chuỗi phụ thuộc cứng giữa mọi nhóm. Không coi R0 đã qua G0 chỉ vì ZER-32/ZER-35 hoàn tất. ZER-37 có thể chuẩn bị bản nháp độc lập theo dependency nhưng chưa là gói ưu tiên hiện tại; chưa khởi chạy hoặc thay trạng thái của nó. Khóa event/evidence còn cần ranh giới ground truth/đối chứng của ZER-8 theo contract issue cha ZER-9. Trước khi giao gói mới, theo mục “Chọn issue tiếp theo và kiểm gate milestone” trong [WORKFLOW](WORKFLOW.md). F-01…F-09 vẫn ở protocol trước formal run.

**Lịch sử 22:18:** ZER-32 đã review, cần Claude sửa gom RV-01…RV-03 rồi Codex retest. [Báo cáo và gói sửa](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md); [artifact](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md). Nguyên bộ kiểm Claude 112/112 OFFLINE đạt; kiểm độc lập xác nhận lỗi hợp khoảng uptime, loại nhầm UNKNOWN_EFFECT và N=0. D-01…D-05 chờ chấp nhận sau khi sửa logic. Handoff ở cuối [ghi chú issue](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md). Chưa Done; không đổi Linear. Codex nhường ghi cho Claude khi Hoàng chuyển gói sửa.

**Lịch sử 21:25:** Hoàng đã giao Claude thực hiện trọn **ZER-32**, Codex review tổng hợp sau khi Claude tự kiểm/sửa xong. [Gói giao việc và allowlist](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md) nằm ở mục “Gói giao Claude — ZER-32” trong ghi chú issue hiện hữu; đầu ra chốt `docs/evidence/ZER-32/requirements-and-kpi.md`. Codex nhường quyền ghi checkout cho Claude sau bước soạn này. Chưa thực hiện artifact hoặc review ZER-32; không tự đổi field Linear. Phần ZER-35 và checkpoint bên dưới là lịch sử, không là hàng đợi hiện tại; publication/merge đọc GitHub, trạng thái issue đọc Linear.

**Checkpoint ZER-35 trước bàn giao ZER-32 (lịch sử):** Gói ZER-35 đã qua review độc lập baseline và delta CL-01–04, đều PASS (Claude chốt 20:50), không còn finding cần sửa trước publication. Hoàng đã cấp quyền **commit/PR**. Nhánh publication: `codex/zer-35-local-lab`, base `main` tại `1f43ff1461c2199bc99e9962483956c3df0fa975`. Tìm PR của nhánh này trên GitHub để đối chiếu commit và CI; trạng thái publication/CI đọc GitHub, không suy từ PASS offline. Bằng chứng ở [lab-restoration](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/lab-restoration.md) và mục cuối [codex-review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-35/codex-review.md). Quyền này chưa gồm merge hoặc đổi Linear; Done còn cần merge và Hoàng chấp nhận. Không áp lại patch Traefik lịch sử.

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
