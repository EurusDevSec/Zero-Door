# ZER-10 + ZER-38 — Verification offline

[Thiết kế](../../design/r1-measurement.md) · [Runbook](../../runbooks/independent-measurement.md) · [Ghi chú issue](../../delivery/milestones/R1-measurement/probes-and-metrics.md)

**Verdict hiện tại: READY_FOR_CODEX_RETEST_OFFLINE** (fix-02, mục 8, sau Codex retest01 CHANGES_REQUIRED_OFFLINE; fix-01 ở mục 7 sau Codex review CHANGES_REQUIRED). Verdict lần bàn giao đầu là READY_FOR_CODEX_REVIEW_OFFLINE. ZER-38 = ZER-10 AC-01 vẫn **PARTIAL**, vì chưa có fixture thật (ZER-41 Backlog) và chưa quan sát được lỗi thật. AC-02/03/04 đạt ở mức offline trên dữ liệu SYNTHETIC. Đây không phải runtime PASS, chưa Done, chưa qua CI từ xa, chưa merge và chưa được Hoàng nghiệm thu.

## 1. Baseline, phạm vi và AC

- Người thực hiện: Claude, ngày 20/10/2026. Gói giao nằm cuối [ghi chú issue](../../delivery/milestones/R1-measurement/probes-and-metrics.md).
- Nhánh `zer-10-independent-measurement` tạo từ merge `55200c9143565c1773cbff57553a9ce858ffe858`. `git diff 0babf90 55200c9` rỗng, nên cây mã giống hệt HEAD bàn giao. Staged rỗng. Chín file dirty có sẵn được giữ nguyên.
- Hash mọi nguồn read-only, cùng note/NOW tại lúc nhận, đều khớp snapshot `scratch/zer10/intake-baseline.json`. Intake và scope ghi ở `scratch/zer10/claude/intake.json`; phần evidence cần cho review đã được chép vào `check_package.py`.
- **AC sống: UNKNOWN phía Claude**, vì phiên này không có connector `linear_zero_door`. Bảng dưới dùng snapshot AC do Codex đọc trong gói giao ngày 20/10/2026.
- GitNexus chỉ có oracle ZER-37, không có probe hay scorer production. `rg` cũng không tìm thấy fixture app/DB nào: chưa có fixture thật để kiểm.

## 2. AC → case → expected/actual → artifact

Expected được tính tay **trước khi** chạy scorer và ghi trong [expected.json](../../../tests/fixtures/zer10/expected.json). "Đạt" nghĩa là test so đúng giá trị đó.

| AC | Case (test) | Expected (tay) | Actual |
| --- | --- | --- | --- |
| ZER-38 / AC-01 probe | Boutique pass, session mới mỗi mẫu, không lưu cookie/thẻ (`test_business_pass_…`) | 3 mẫu đạt, 3 session khác nhau, event H hợp lệ, O từ chối (PLANE_VIOLATION) | Đạt |
| | Business 200 sai nội dung: home thiếu link, checkout không xác nhận, không cấp session, redirect ra ngoài allowlist (`test_wrong_business_content…`) | CONTENT kèm reason cụ thể; giỏ của mẫu được làm trống bằng cùng session | Đạt |
| | Session cũ, response (mã đơn) phát lại (`test_stale_session…`) | Mẫu 2 lỗi STALE_SESSION / STALE_RESPONSE | Đạt |
| | Timeout thật qua socket, body nhỏ giọt, SLOW (`test_real_timeout…`); connect bị từ chối (`test_connect_failure`) | TIMEOUT tại deadline 2 s (server trễ 3 s); SLOW khi > L; CONNECT | Đạt |
| | Cancel giữa giao dịch; overrun; budget request (`test_cancel…`, `test_overrun…`, `test_request_budget…`) | Không phát mẫu, không tiêu sequence, vẫn dọn giỏ; bỏ slot chứ không chạy dồn; dừng MAX_REQUESTS | Đạt |
| | Sink lỗi, outbox lỗi, khởi động lại (`Delivery.*`) | Không mất raw; gửi lại đúng envelope; outbox lỗi → PERSISTENCE_FAILED | Đạt |
| | Fixture SYNTHETIC: round-trip, note sai, status 200, đọc bản cũ, reference độc hại (`FixtureFlow`) | Đạt / WRONG_RESULT / STATUS_200 / WRONG_RESULT / mã hóa thành một segment, không chèn header | Đạt |
| | Probe → H Archive → scorer (`ProbeToScorer`) | Event thật của probe được H nhận và chấm (B0: RECOVERED_UNDETECTED) | Đạt |
| | **Lỗi quan sát thật trên Boutique và fixture** | Cần runtime và ZER-41 | **PARTIAL — chưa có** |
| ZER-10 AC-02 mốc | E01 (`test_e01_hand_values…`) | MTTD 30, MTTR 60, total 90, reaction 19; sai số 37/37/32/2 ms | Đạt |
| | Thứ tự ingest đảo; RV đến sau seal (`test_ingest_order…`) | Mốc không đổi; LATE_INGEST được đếm; EVALUATOR_MISMATCH vì thiếu RV | Đạt |
| | Offset +10 s, drift 10 ms/s, sync không phủ, sync không có uncertainty/resolution, HOST_SHARED (`Clocks.*`) | 30/60/90 sau chuẩn hóa; CLOCK_UNVERIFIED → MISSING, total 90 và reaction 19 vẫn báo | Đạt |
| | EARLY_DETECT; INVALID_CLOCK; redelivery khác retry; DETECTED đến sau (`test_early…`, `test_redelivery…`) | MTTD 0 và MTTR 90,5; MISSING; reaction 24 với 2 lần thử; T_det 131 | Đạt |
| | War Game tách được, War Game chồng lấn (`test_war_game…`) | Hai incident đều RECOVERED; AMBIGUOUS → cả hai MISSING | Đạt |
| AC-03 thiếu dữ liệu và mẫu số | SUCCESS nhưng probe lỗi; FAILED/PARTIAL/TIMEOUT hay không action mà vẫn phục hồi; thiếu terminal (`test_action_success…`, `test_failed_partial…`) | TIMEOUT; RECOVERED + NO_ACTION_BEFORE_RECOVERY, reaction NO_SUCCESS | Đạt |
| | Biên K/S, relapse, ứng viên đúng/sau cap, stop giữa T_rec và S, thiếu mẫu, `t_end` muộn, mất sequence (`test_measurement_recovery`, `test_relapse…`) | Theo E05–E09 của §7.5 | Đạt |
| | UNKNOWN ở lại N, NO_EFFECT đủ/thiếu phủ, EMPTY/NO_ELIGIBLE/ALL_UNKNOWN (`test_effect_states…`) | A1 = 2/1/1/N 1; EMPTY; NO_ELIGIBLE; N 2 với cận [0, 1] | Đạt |
| | INVALID/INTEGRITY/SOURCE_VIOLATION/LINK_CONFLICT/TARGET_MISMATCH/ORPHAN/UNSCOPED/liên run (`Evidence.*`) | MISSING (không phải MISSED); vi phạm nguồn chỉ được lưu; UNSCOPED chỉ đếm | Đạt |
| | Uptime hai luồng, gap chồng outage (`Uptime.*`) | D_lower 128 s (không đếm trùng); A_lower 0,539568; FAIL; luồng thiếu thành U | Đạt |
| | Benign thiếu coverage (`Benign`) | Cận [0,2; 1,0], UNKNOWN, không phải 0; đủ coverage thì 12,94964 episode/giờ | Đạt |
| AC-04 quyết định và usage | Đề xuất sai bị guard chặn; đúng; không trigger; fallback; thiếu GT (`Decisions.*`) | INCORRECT + chặn đúng; CORRECT; NO_TRIGGER vẫn ở mẫu số; FALLBACK_RULES; UNKNOWN_COHORT với cận [0, 1] | Đạt |
| | Action thực thi và false action (`test_false_action…`) | Thực thi 1, false 1 | Đạt |
| | Retry LLM, redelivery, usage/cost thiếu, B1/B0 N/A (`Usage.*`, `test_b0…`) | 2 call, 1 retry, 1100/100 token, 0,011 USD; MISSING là cận dưới; N/A | Đạt |
| | Verdict D-01, R(t), dấu `<` nghiêm ngặt (`Aggregates`) | PASS/NOT_PASS/UNKNOWN; cận R(t); 60,0 không đạt | Đạt |
| Raw và output | Raw bị sửa, export sai plane, scorer không sửa raw, output đã tồn tại hoặc nằm trong export, help offline, checkout sạch (`RawIntegrity`, `test_measurement_cli`) | RawError hoặc exit 3; exit 4; byte raw không đổi; không mở kết nối mạng | Đạt |

## 3. Chạy kiểm và kết quả

Môi trường: Windows 11, Git Bash. Python 3.11.9 (interpreter tương đương CI, chỉ dùng thư viện chuẩn) và 3.12.4. Không có lab, Docker, Kubernetes, Kafka, model hay mạng ngoài; chỉ có server loopback do test tự tạo.

| Lệnh | Kết quả | Artifact |
| --- | --- | --- |
| `bash infrastructure/scripts/verify-measurement.sh --offline` (3.11.9 và 3.12.4) | 71/71 test, E01 tái tính khớp số tay, `OFFLINE_PASS` | [3.11.9](results/offline-py3.11.9/offline-summary.json), [3.12.4](results/offline-py3.12.4/offline-summary.json) |
| `python -B docs/evidence/ZER-10/check_mutants.py` | Đối chứng 66 test sạch; 11/11 mutant bị bắt | [mutants.json](results/mutants.json) |
| `python -B docs/evidence/ZER-10/crosscheck_zer37.py` | 62 ca §10, 178/178 trường khớp expected tay của ZER-37 | [crosscheck-zer37.json](results/crosscheck-zer37.json) |
| Bandit 1.7.9 (pin ZER-12) `-lll -iii` trên package, entry point và evidence | Không có issue (2 B310 đã xử lý bằng giới hạn scheme) | [bandit.txt](results/bandit.txt) |
| Hồi quy ZER-9/ZER-37 (3.11.9) | 22 + 42 + 4 test OK; ZER-37 238/238, mutant 32/32 | [regressions.txt](results/regressions.txt) |
| `bash -n` mọi `.sh`, YAML CI parse | Đạt; job mới `r1-measurement-offline` | [ci.diff](results/ci.diff) |
| Clean checkout mô phỏng: `git archive HEAD` + 37 file gói, không có `scratch/` và venv | `--offline` 71/71, mutant 11/11, đối chiếu 178/178 | Lệnh như trên, chạy trong thư mục tạm |
| `python -B docs/evidence/ZER-10/check_package.py --check` | Hash gói, nguồn bảo vệ, append-only note/NOW và phạm vi Git | `manifest.json`; hash ghi ở handoff |

Mutant bị bắt: T_rec lấy `recovery_verified_at`; UNKNOWN_EFFECT rời N; missing tính là PASS; PROBE_SAMPLE/HEARTBEAT thành O; gap tính là up; bỏ kiểm sequence; chỉ xét status 200; cancel thành lỗi; NO_EFFECT không cần phủ; đồng hồ chưa sync vẫn tin; tin RECOVERY_VERIFIED. Phép đối chiếu ZER-37 có hai điều chỉnh harness đã ghi trong script: thêm khóa `trial_id: null` mà oracle bỏ, và đổi tên `f01_params` sang tên có đơn vị.

## 4. Lỗi tự tìm và đã sửa trong gói

1. Luật cửa sổ ghép DETECTED trước khi lan truyền lại chuỗi nhân quả, nên ACTION phía sau thành ORPHAN. Đã sửa: lan truyền lại sau luật cửa sổ.
2. Mọi bản ghi quarantine bị coi là INVALID. Đã sửa: SOURCE_VIOLATION chỉ được lưu, LINK_CONFLICT/MODE_VIOLATION/LEAK đi đúng nhánh.
3. ORPHAN có `incident_id` lạ không được xét "ORPHAN trong cửa sổ". Đã sửa.
4. LINK_CONFLICT liên run (ca X1 của ZER-37) không thấy được trong export một run. Đã sửa: thêm `--other-export`, thiếu thì gắn cờ `CROSS_RUN_LINKS_UNCHECKED`.
5. Giá trị server trả về được chèn vào path hoặc request line. Đã sửa: percent-encode, từ chối ký tự điều khiển và non-ASCII trước khi kết nối.
6. Regex tên trung tính từ chối `clk_host_lab` (ví dụ của chính contract). Đã sửa.
7. Bandit B310: `urlopen` không giới hạn scheme. Đã giới hạn http(s).
8. Clean checkout làm hỏng bước đối chiếu chéo trong CI, vì oracle ZER-37 đọc `scratch/zer37/fixtures.json`. Đã sửa: script tự chép bản fixtures đã seal (như bootstrap CI hiện có) và từ chối chạy nếu bản ở scratch khác.

Hai expected test do tôi viết sai và đã được sửa sau khi tính lại tay: ca War Game (stop 400 ≥ verified_at 173 nên là RECOVERED) và ca reference độc hại (fake server trả 404).

## 5. Quyết định cần Codex review

1. Lỗ sequence trong chuỗi K hoặc cửa sổ S được coi là khoảng trống. Chặt hơn oracle, nhưng không đổi ca nào trong §10.
2. MODE_VIOLATION làm incident MISSING (vẫn ở lại N) thay vì bỏ khỏi nhóm.
3. Tên khóa `f01_params` (`*_s`, `l_ms`); harness phải phát đúng các tên này.
4. `payload.detail` và đề xuất MINOR `zd-event/1.1.0`; ánh xạ lớp lỗi sang bốn giá trị đã khóa.
5. `zd-gt-constraints/0` cho kiểm tham số action (ZER-50 OPEN).
6. Cutoff hiện là seal (`ingest_grace` OPEN); C0, `slot_s`, `episode_gap_s` và coverage detector là input tường minh.

## 6. Giới hạn và phần chưa kiểm

- **Không có runtime:** chưa probe Boutique thật, chưa có fixture thật, chưa có H gateway hay đồng hồ tham chiếu trong lab, chưa có harness phát ATTACK/EFFECT/TRIAL thật. Runtime plan gom nằm ở [runbook §3](../../runbooks/independent-measurement.md).
- Chưa chạy trên Linux hay CI từ xa. Job mới chỉ được kiểm cú pháp YAML và chạy cùng lệnh trên Windows. Trên Linux, kết nối bị từ chối trả lỗi ngay, nên ca CONNECT dùng deadline 6 s cho Windows.
- Marker Boutique (tên sản phẩm, trang giỏ/checkout) lấy theo hình dạng của `verify-local-lab.sh`, chưa quan sát trực tiếp trong gói này.
- CPU P179, request success rate benign và coverage detector cho M5/M6 chưa có trong export, nên là MISSING có lý do.
- Phép kiểm rò dùng `event_pipeline.audit` với `access_complete=False`, nên kết quả là UNKNOWN cho tới khi có bằng chứng quyền runtime (ZER-9 AC-03).
- Không commit, push, tạo PR, ghi Linear, nhắn agent khác, chạy lab, Docker, model hay cloud.

## 7. fix-01 — sửa gom theo Codex review (20/10/2026)

**Verdict: READY_FOR_CODEX_RETEST_OFFLINE.** Codex review ([codex-review.md](codex-review.md), NOT_READY_OFFLINE / CHANGES_REQUIRED) nêu một P1, mười P2 và một P3. Tôi đã sửa cả mười hai, cùng các nhánh chung nguyên nhân bên dưới. ZER-38/AC-01 vẫn **PARTIAL**: chưa có fixture thật và chưa quan sát runtime. Chưa Done, chưa CI từ xa, chưa merge, chưa được Hoàng nghiệm thu. Mục 1–6 phía trên ghi lại lần bàn giao đầu và giữ nguyên làm lịch sử.

### 7.1 Baseline

- Nhánh `zer-10-independent-measurement`, HEAD `55200c9`, staged rỗng. Gốc so sánh là manifest bàn giao đầu `manifest.json` (SHA-256 `b3a33293…9292`). Lúc nhận không có drift so với manifest này. Intake ghi ở `scratch/zer10/claude/fix-01/intake.json`.
- **Chỉ đọc**, kiểm bằng hash trong `fix-01/manifest.json`: báo cáo và toàn bộ bằng chứng của Codex (`codex-review.md`, `codex-review/`, 14 file), `docs/detail_zero-door.md` (ngoài gói, có từ trước), event_pipeline, contract LOCKED, agents/worker/manifests và evidence đã seal.
- Note và NOW chỉ nối thêm: nội dung lúc intake (25.690 và 67.106 byte) vẫn là tiền tố của note và hậu tố của NOW.
- Delta so với gốc: `python -B docs/evidence/ZER-10/check_package.py --check` (danh sách changed/added nằm trong `fix-01/manifest.json`).

### 7.2 Finding → nguyên nhân → sửa → regression

| Finding | Nguyên nhân gốc | Sửa (nhánh chung nguyên nhân) | Regression (tên test) |
| --- | --- | --- | --- |
| **ZR10-01 P1** request INVALID mất khỏi N | Incident chỉ dựng từ ATTACK_REQUESTED hợp lệ | Lượt requested được dựng lại từ mọi ATTACK_REQUESTED không dùng được: INVALID ở scorer, quarantine, **late**, UNSUPPORTED, archive scope. Incident MISSING (`REQUEST_INVALID`/`REQUEST_LATE`, `TARGETS_UNKNOWN`); chỉ đọc ID, không đoán target/flow/thời gian. Không tạo được ID tin cậy, hoặc có quarantine không envelope, thì cohort `INCOMPLETE` và mọi verdict KPI là UNKNOWN (`COHORT_INCOMPLETE`). SOURCE/PLANE_VIOLATION không phải request; C0 không có incident giả | `Fix01Cohort` (5 test: một request lỗi, hai trial lỗi/sạch kèm đối chứng, request late, không gán được ID, C0 và nguồn giả) |
| **ZR10-02** detect có đồng hồ chưa xác minh thành MISSED | `continue` làm mất bằng chứng không so được | `t_det_status = CLOCK_UNVERIFIED`: MTTD/MTTR/reaction MISSING, nhãn họ RECOVERED → MISSING, total vẫn báo. Cùng nguyên nhân ở executor (SUCCESS không xếp được làm reaction MISSING, không phải NO_SUCCESS), decision (M1 `MISSING_ORDER`, M10 dùng `duration` có kiểm đồng hồ, đếm `clock_missing`), M2 `trigger_unknown`, M4 | `Fix01Clocks` (4 test: detector, executor, decision; đối chứng E01/undetected) |
| **ZR10-03** M5 gộp episode, suy coverage từ slot | Mất khóa episode; `full = unknown == 0` | Khóa (signature hoặc rule; service). Coverage của **toàn stream** tách khỏi slot: `slot_verdict` và `episode_verdict`; episode/giờ chỉ có khi coverage phủ cả W và không có alert không xếp được hoặc INVALID. Alert không xếp được làm slot chưa hit thành unknown. B0 không có DETECTED thì M5 N/A | `Fix01Benign` (khóa, thiếu coverage, alert không xếp được, B0) |
| **ZR10-04** M6 bỏ action thiếu terminal | Đếm ACTION_COMPLETED | Đếm action_id có HEAL_STARTED trong W. Terminal (thiếu, xung đột), harm (UNKNOWN khi có action) và coverage log được báo tách nhau. Action không xếp được hoặc bản ghi action INVALID làm `M6_verdict` UNKNOWN. B0 thì N/A | `Fix01Benign.test_m6_counts_started_actions_in_w` (thiếu terminal, kết thúc sau W, bắt đầu trước W) |
| **ZR10-05** thiếu hoặc INVALID LLM_CALL vẫn COMPLETE | Coverage chỉ dựa trên bản ghi hợp lệ | Coverage bắt đầu từ DECISION của tác tử LLM. LLM_CALL/DECISION INVALID, quarantine hoặc late, và `call_id` xung đột làm call/usage/cost MISSING ở run và trial/incident/tác tử liên quan; tổng là cận dưới; bản ghi hỏng không được đếm thành call (`raw_call_records` báo riêng); retry của call_id xung đột là unknown | `Fix01Usage` (3 test, có đối chứng COMPLETE) |
| **ZR10-06** GT hỏng kiểu làm crash | So sánh trước khi kiểm kiểu | `gt_view`/`constraint_problem` kiểm kiểu và phạm vi mọi trường GT một lần. Hỏng thì UNKNOWN_GT/UNKNOWN_COHORT kèm `reason`, không mặc định. Cùng nguyên nhân: params/sources/service không phải chuỗi hay không hash được, proposal không phải object (SCHEMA_INVALID), `case_class` hỏng | `Fix01GroundTruthAndOrder.test_malformed_ground_truth_is_unknown_not_a_crash` (7 biến thể + đối chứng) |
| **ZR10-07** guard mâu thuẫn chọn theo thứ tự ingest | `verdicts[...][0]` | Kiểm cardinality §3.2 sau dedup `event_id`: DECISION/`decision_id`, GUARD_VERDICT/`decision_id`, API_ACCEPTED/`action_id` → `cardinality_violations`, M3 `conflicting_verdicts` (không chấm). Cùng nguyên nhân: hai ACTION_COMPLETED là terminal `CONFLICT`; hai proposal cùng thời điểm sớm nhất là `MISSING_ORDER`; DECISION trùng không còn bị chấm hai lần | `test_conflicting_guard_verdicts_do_not_depend_on_order` (ba thứ tự), `test_tied_first_proposals_and_m4_trigger` |
| **ZR10-08** giỏ sai số lượng vẫn PASS | Chỉ kiểm có product id | Giỏ phải có đúng một dòng, đúng sản phẩm, quantity = 1 (`count` hai marker + capture có `equals`). Marker là OBSERVED-SHAPE theo template upstream, có thể thay qua plan, chưa khóa. Fake Boutique giờ render giỏ theo hình dạng thật. `templates()` kiểm cả key của `count` | `Fix01Transaction.test_cart_must_hold_exactly_the_requested_item` (duplicate, extra, wrong + đối chứng) |
| **ZR10-09** bỏ qua `step_s`, trần run không cắt giao dịch | Chỉ có deadline giao dịch | Mỗi bước dừng ở mốc sớm nhất: giao dịch, `step_s`, trần run. Reason `STEP_DEADLINE`/`TRANSACTION_DEADLINE`. Trần run cắt giao dịch thành CANCELLED `RUN_BUDGET` (journal, không phát). `budget.grace_s` bắt buộc (0, 60] giới hạn cleanup và lần gửi outbox cuối; summary báo `max_duration_s`, `grace_s`, `wall_s` | `test_step_deadline_is_enforced_below_the_transaction_deadline`, `test_run_cap_cuts_the_transaction_and_bounds_the_cleanup` |
| **ZR10-10** cleanup suy sở hữu từ 201; Ctrl+C bỏ cleanup | Đánh `owned` theo status; cleanup ngoài `finally` | `owns` bắt buộc kèm bằng chứng `ownership`: session mới của mẫu, hoặc echo nonce. Chưa chứng minh thì `UNRESOLVED_OWNERSHIP`, không xóa. Cleanup chạy trong `finally`; KeyboardInterrupt và SIGINT/SIGTERM ở CLI đi đường cancel (`INTERRUPTED`): journal, không phát mẫu, dọn trong grace, run dừng có summary | `test_cleanup_never_deletes_a_record_it_did_not_create`, `test_interrupt_takes_the_cancel_path_and_cleans_up`, `test_interrupt_after_the_add_request_still_owns_the_session_cart`, `test_ownership_proof_is_mandatory_in_specs` |
| **ZR10-11** H sink theo redirect, mang bearer sang origin khác | `urlopen` mặc định | Opener riêng: không redirect, bỏ qua proxy môi trường (cùng nguyên nhân: token đi nơi khác). Chỉ nhận 201 + status hợp lệ + đúng `event_id` + đúng URL. 3xx hoặc ACK lạ là `SinkRefused`, probe dừng `SINK_REFUSED` (exit 5), outbox giữ event. 202 là chưa bền nên gửi lại | `Fix01HSink` (301/302/303/307/308, ACK 200/sai status/202, proxy môi trường, probe dừng và outbox còn nguyên) |
| **ZR10-N1 P3** output nằm trong other export | CLI chỉ truyền H/O chính | Mọi input, kể cả `--other-export`, nằm trong vùng cấm | `test_output_inside_any_input_export_is_refused` |
| Nhánh chung khác | — | PROBE_SAMPLE `latency_ms < 0` là SEMANTIC (thấy trong `scorer-probes.json:negative_latency`). `crosscheck_zer37.py` dùng argparse và không ghi đè file kết quả (trước đây `--help` bị hiểu là tên file) | `Fix01Clocks.test_controls_and_negative_latency` |

Sửa test cũ duy nhất là ca fixture `wrong_note`/`status_200`: kỳ vọng cũ là xóa bản ghi sai, kỳ vọng mới là `UNRESOLVED_OWNERSHIP` và không xóa. Đây là hệ quả trực tiếp của ZR10-10, không nới assert.

### 7.3 Kết quả kiểm

| Lệnh | Kết quả | Artifact |
| --- | --- | --- |
| `bash infrastructure/scripts/verify-measurement.sh --offline` (3.11.9 và 3.12.4) | 103/103 test (71 cũ + 32 mới), E01 30/60/90/19, `OFFLINE_PASS` | [3.11.9](fix-01/results/offline-py3.11.9/offline-summary.json), [3.12.4](fix-01/results/offline-py3.12.4/offline-summary.json) |
| `python -B docs/evidence/ZER-10/fix-01/retest_counterexamples.py` | Mọi phản ví dụ Codex ra đúng expected của review: 29/29 kiểm | [counterexamples-retest.json](fix-01/results/counterexamples-retest.json) |
| `python -B docs/evidence/ZER-10/check_mutants.py` | Đối chứng 103 test sạch; 28/28 mutant bị bắt: 11 cũ và 17 `FIX01_*`, mỗi mutant khôi phục một hành vi Codex chỉ ra | [mutants.json](fix-01/results/mutants.json), [mutants.txt](fix-01/results/mutants.txt) |
| `python -B docs/evidence/ZER-10/crosscheck_zer37.py` | 62 ca, 178/178 trường khớp | [crosscheck-zer37.json](fix-01/results/crosscheck-zer37.json) |
| Bandit 1.7.9 trên package, entry point và script evidence | Package và entry point: 0 issue. Script evidence: chỉ subprocess có lý do ghi trong code (`nosec B404/B603/B607`: interpreter cố định, script/git cố định, không shell) | [bandit.txt](fix-01/results/bandit.txt) |
| Hồi quy ZER-9/ZER-37 (3.11.9) | 22 + 42 + 4 OK; ZER-37 238/238, mutant 32/32 | [regressions.txt](fix-01/results/regressions.txt) |
| Clean checkout mô phỏng (`git archive HEAD` + file gói + bằng chứng Codex, không `scratch/`, không venv) | `--offline` 103/103, đối chiếu 178/178, retest 29/29, mutant 28/28 với đối chứng 103 | Chạy trong thư mục tạm |
| `python -B docs/evidence/ZER-10/check_package.py --check` | Hash gói, delta so với gốc, bằng chứng Codex chỉ đọc, append-only, phạm vi Git | [fix-01/manifest.json](fix-01/manifest.json) |

**Về "fail-before".** Mã nguồn trước sửa không được giữ bản sao riêng, nên tôi chứng minh theo hai cách độc lập. (1) Output đã lưu của Codex (`codex-review/*.json`, chạy trên đúng 37 hash của manifest gốc) cho thấy hành vi sai. (2) Mỗi mutant `FIX01_*` khôi phục đúng hành vi đó trên mã mới, và regression tương ứng fail. Script phản ví dụ của Codex được chạy nguyên trạng. Riêng `probe/counterexamples.py` có hai dòng chẩn đoán giả định hành vi cũ (luôn có một mẫu; sink trả status thay vì từ chối), nên harness retest chạy nó từ chính source với đúng hai chỗ thích nghi, liệt kê trong output.

### 7.4 Sáu điểm Codex đã trả lời và cách áp dụng

1–2. Lỗ sequence và MODE_VIOLATION giữ nguyên hướng. Mode vẫn làm incident MISSING, và các metric quyết định không coi trial đó là đối chứng hợp lệ.
3–4. Tên `f01_params` và `payload.detail` giữ nguyên, ánh xạ về bốn `error_class` đã khóa. MINOR 1.1.0 vẫn là DRAFT.
5. `zd-gt-constraints/0` vẫn là bộ kiểm đề xuất. GT hỏng giờ được xử lý như ZR10-06.
6. Coverage được thực thi trong code (ZR10-03/04/05), không chỉ ghi trong docs.

### 7.5 Còn mở sau fix-01

- **AC-01 PARTIAL:** cần fixture ZER-41 và quan sát runtime theo [runbook §3](../../runbooks/independent-measurement.md), gồm đối chiếu `CART_MARKERS` trên trang Boutique thật.
- **Ack 202 (Kafka) của H gateway:** hiện gửi lại; cần chốt trước runtime nếu dùng gateway Kafka.
- **Ràng buộc mặt hàng/số lượng với trang xác nhận đơn:** chưa có bằng chứng giao diện.
- `scorer-probes.json:samples_after_trial_end` (mẫu và RECOVERY sau TRIAL_ENDED) không phải finding và không đổi hành vi. Nếu Codex muốn giới hạn evidence theo cửa sổ trial thì cần quyết định contract.
- Chưa có Linux/CI từ xa và runtime. Không commit, push, PR, Linear, lab, model hay cloud.


## 8. fix-02 — sửa gom theo Codex retest01 (20/10/2026)

**Verdict: READY_FOR_CODEX_RETEST_OFFLINE.** Codex retest01 ([codex-retest01.md](codex-retest01.md), CHANGES_REQUIRED_OFFLINE) còn ba P2 (FX01-R1…R3), một P3 (FX01-N1) và residual journal của ZR10-10. Tôi đã sửa cả năm điểm cùng các nhánh chung nguyên nhân bên dưới. ZER-38/AC-01 vẫn **PARTIAL**: chưa có fixture thật và chưa quan sát runtime. Chưa Done, chưa CI từ xa, chưa merge, chưa được Hoàng nghiệm thu. Mục 1–7 giữ nguyên làm lịch sử.

### 8.1 Baseline và snapshot trước sửa

- Nhánh `zer-10-independent-measurement`, HEAD `55200c9`, staged rỗng. Gốc so sánh là `fix-01/manifest.json` (SHA-256 `9f1e3850…f08a`); `manifest.json` (`b3a33293…9292`) cũng giữ nguyên.
- **Snapshot trước sửa:** trước lần sửa đầu tiên, cả 46 file của gói fix-01 được chép nguyên byte vào [fix-02/before/](fix-02/before/), kèm [fix-02/before.json](fix-02/before.json). Mỗi hash bằng đúng hash trong `fix-01/manifest.json`; `check_package.py` kiểm lại điều này ở mọi lần chạy.
- **Chỉ đọc**, kiểm bằng hash: `codex-review.md` + `codex-review/` (14 file) và `codex-retest01.md` + `codex-retest01/` (12 file). Hash lúc nhận khớp `codex-retest01/checksums.json` của Codex (11/11) và `fix-01/manifest.json` (14/14). Intake ở `scratch/zer10/claude/fix-02/intake.json`.
- Note và NOW chỉ nối thêm: nội dung lúc intake (31.467 và 68.307 byte) vẫn là tiền tố của note và hậu tố của NOW.

### 8.2 Finding → nguyên nhân → sửa → regression

| Finding | Nguyên nhân gốc | Sửa (nhánh chung nguyên nhân) | Regression (tên test) |
| --- | --- | --- | --- |
| **FX01-R1 P2** cleanup dùng cookie đã đổi, xóa giỏ người khác | Cleanup đọc danh tính từ trạng thái sống (cookie jar) lúc dọn, không phải lúc tạo | Cookie gửi kèm request tạo được đóng băng làm credential cleanup; request cleanup gửi đúng credential đó và không cập nhật jar. Session chỉ được tính là sở hữu khi cookie trong jar đúng là session mẫu vừa được cấp. **Cùng nguyên nhân:** identifier đích (vd. `order_ref`) cũng đóng băng lúc chứng minh bằng nonce, nên capture sau đó không đổi được đích xóa; spec có path cleanup dùng biến capture sau bước chứng minh bị `SpecError`. Cleanup hết giờ báo `GRACE_EXPIRED`/`CLEANUP_TIMEOUT` | `Fix02Cleanup` (Set-Cookie ở response tạo, ở bước sau, ở redirect được theo; lỗi trước/sau response; capture lại `order_ref`; đối chứng giỏ đã release). Mỗi ca kiểm cả giỏ/bản ghi có sẵn của người khác lẫn tài nguyên của mẫu |
| **FX01-R2 P2** chờ slot, ACK nhỏ giọt, cleanup khi dừng sớm vượt cap/grace | Chỉ deadline giao dịch là tổng; các chờ/I/O khác dựa vào timeout từng lần đọc socket hoặc không có giới hạn | Một deadline tổng xuyên mọi chờ và I/O: chờ slot lấy min(slot kế, trần); H sink và đồng hồ tham chiếu dùng client HTTP/1.1 có giới hạn của probe (deadline phủ connect, header, toàn bộ body; không proxy, không redirect); Publisher kiểm deadline trước mỗi lần thử, kể cả retry, và truyền nó vào lần thử; heartbeat/sample/sync phát qua `io_deadline` (trần trong workload, cuối grace sau khi dừng). Grace tính từ mốc dừng sớm nhất (trần, mẫu bị cancel, tín hiệu); cleanup của mẫu dở bị giới hạn bởi grace từ lúc dừng | `Fix02Deadlines` (ACK chậm header và nhỏ giọt + đối chứng nhanh; nhiều event pending, không request mới sau deadline; chờ slot; dừng sớm có/không cleanup chậm; `stop()` từ tín hiệu; ghi H sau grace giữ pending; đồng hồ tham chiếu chậm/redirect + đối chứng) |
| **ZR10-10 residual** journal cancel chỉ ở RAM | Journal mặc định là list; CLI chỉ in summary | CLI ghi journal ra đĩa (`--journal`, mặc định `<outbox>.journal.jsonl`, fsync từng dòng). Summary in đường dẫn journal và `unresolved_cleanup`. Không ghi được journal thì từ chối chạy (exit 5) trước request đầu tiên; lỗi giữa chừng dừng như lỗi outbox | `Fix02Journal` (cancel có cleanup chậm, journal hỏng, đối chứng) |
| **FX01-R3 P2** thiếu trial metadata làm scorer crash | Mốc không dựng được (`None`) vẫn đi vào sort/min theo `.ms` | Mốc `None` không vào sort/min. T_stop không đặt được: `t_stop_status = CLOCK_UNVERIFIED`, AFTER_STOP MISSING. SUCCESS không đặt được: reaction MISSING. Incident giữ ở N với `TRIAL_MISSING` (kể cả request hỏng); trial khác giữ kết quả. **Cùng nguyên nhân:** uptime liệt kê cả trial chỉ biết qua TRIAL_CONTEXT/incident (`TRIAL_BOUNDS_MISSING`), thay vì để trial biến mất | `Fix02TrialMetadata` (request hợp lệ/hỏng × có/không stop × có/không SUCCESS; trial khác giữ E01; đối chứng: TRIAL_STARTED INVALID hoặc trùng khi TRIAL_ENDED vẫn dựng được mô hình đồng hồ, và E01) |
| **FX01-N1 P3** bucket con vẫn COMPLETE khi `call_id` xung đột | Cờ incomplete của bucket không xét xung đột | Mỗi bản ghi của `call_id` xung đột đánh `conflicting_call_records` cho mọi nhóm nó nêu (kể cả model chỉ có trong bản ghi xung đột); các nhóm đó MISSING; call vẫn đếm một lần | `Fix02Usage` (mọi bucket, model khác, đối chứng) |

Sửa test cũ: chỉ hai fake đồng hồ trong `test_clock_resolution_sync_and_failed_sync` nhận thêm tham số `deadline_ns` (giao diện `read` mới); assert giữ nguyên.

### 8.3 Kết quả kiểm

| Lệnh | Kết quả | Artifact |
| --- | --- | --- |
| `bash infrastructure/scripts/verify-measurement.sh --offline` (3.11.9 và 3.12.4) | 125/125 test (103 của fix-01 + 22 mới), E01 30/60/90/19, `OFFLINE_PASS` | [3.11.9](fix-02/results/offline-py3.11.9/offline-summary.json), [3.12.4](fix-02/results/offline-py3.12.4/offline-summary.json) |
| `python -B docs/evidence/ZER-10/fix-02/fail_before.py` | Snapshot khớp fix-01. 16 test NEGATIVE: fail/error trên snapshot trước sửa, đạt trên cây hiện tại. 6 test CONTROL đạt sau. 7/7 kiểm theo expected của codex-retest01 (R1, R2 ×3, R3 ×2, N1): sai trên snapshot, đúng trên cây hiện tại | [fail-before.json](fix-02/results/fail-before.json), [fail-before.txt](fix-02/results/fail-before.txt) |
| `python -B docs/evidence/ZER-10/check_mutants.py` | Đối chứng 125 test sạch; 40/40 mutant bị bắt: 11 cũ, 17 `FIX01_*`, 12 `FIX02_*` (mỗi mutant đặt lại đúng một dòng đã sửa) | [mutants.json](fix-02/results/mutants.json), [mutants.txt](fix-02/results/mutants.txt) |
| `python -B docs/evidence/ZER-10/fix-01/retest_counterexamples.py` | Phản ví dụ của Codex review lần đầu vẫn ra đúng expected: 29/29 | [counterexamples-review-retest.json](fix-02/results/counterexamples-review-retest.json) |
| `python -B docs/evidence/ZER-10/crosscheck_zer37.py` | 62 ca, 178/178 trường khớp | [crosscheck-zer37.json](fix-02/results/crosscheck-zer37.json) |
| Bandit 1.7.9 trên package, entry point và script evidence | 0 issue. Bỏ qua có lý do ghi trong code: subprocess cố định (`B404/B603/B607`), `exec` của mutant chỉ trên mã nguồn của chính package (`B102`), urllib trong mutant khôi phục hành vi cũ (`B310`) | [bandit.txt](fix-02/results/bandit.txt) |
| Hồi quy ZER-9/ZER-37 (3.11.9) | 22 + 42 + 4 OK; ZER-37 238/238, mutant 32/32 | [regressions.txt](fix-02/results/regressions.txt) |
| Clean checkout mô phỏng (`git archive HEAD` + file gói + bằng chứng, không `scratch/`, không venv) | `--offline` 125/125; `fail_before.py` PASS (snapshot vẫn tái hiện 6,01 s chờ slot); đối chiếu 178/178; retest review 29/29 | Chạy trong thư mục tạm |
| `python -B docs/evidence/ZER-10/check_package.py --check` | Hash gói, delta so với fix-01, snapshot trước sửa, bằng chứng Codex chỉ đọc, append-only, phạm vi Git | [fix-02/manifest.json](fix-02/manifest.json) |

Phản ví dụ mới của Codex chạy lại trên cây hiện tại (`codex-retest01/probe/counterexamples.py`, `codex-retest01/metrics/cases.py`, nguyên trạng, không thích nghi): giỏ `foreign-user` còn nguyên và cleanup đi bằng session của mẫu; flush ACK nhỏ giọt dừng ở ~0,06 s với event còn pending; chờ cadence dừng ở ~0,11 s; CLI cancel kết thúc ~0,08 s, cleanup `GRACE_EXPIRED` có trong summary và journal; hai ca thiếu trial chấm được, MISSING với `TRIAL_MISSING`; mọi bucket M11 MISSING khi `call_id` xung đột.

Trên snapshot trước sửa, cùng các script đó tái hiện đúng số Codex đo: chờ slot 6,01 s, flush ACK nhỏ giọt 0,30 s và đánh DELIVERED, CLI cancel 0,38 s, `AttributeError` ở hai ca thiếu trial.

### 8.4 Giới hạn

- `fail_before.py` chạy hai bên trong cây tạm. Bên trước dùng snapshot `fix-02/before/`; event_pipeline lấy từ repo (ngoài gói, hash được bảo vệ). Test CONTROL dựa trên trường output mới (`t_stop_status`, `conflicting_call_records`, `journal`) nên fail ở bên trước; đó không phải bằng chứng hành vi.
- Ca `cadence_wait_over_cap` chỉ được tính khi mẫu đầu tiên thật sự chạy: trong một lần chạy clean checkout đầu tiên, heartbeat đầu (fsync outbox trên thư mục tạm ổ C:) đã vượt trần 0,1 s nên run dừng trước mẫu và kiểm này thành "đúng" ở bên trước. Điều kiện giờ đòi đúng một mẫu và `fail-before.json` ghi số mẫu cùng thời gian của cả hai bên.
- Test thời gian dùng biên rộng (0,1–0,4 s) để không phụ thuộc máy, nhưng vẫn là test thời gian trên Windows; Codex nên chạy lại trên máy mình.
- Dừng sớm được nhận trong tối đa một lát đọc (`SLICE_S` = 0,2 s) sau tín hiệu; cửa sổ grace tính từ lúc nhận tín hiệu.
- `success_unknown` và `stop_unknown` khi trial vẫn có mô hình đồng hồ là nhánh phòng vệ: với contract hiện tại (event O bắt buộc có `trial_id` hợp lệ, sai trial là LINK_CONFLICT) chỉ xảy ra khi trial thiếu, nên không có mutant riêng cho chúng.
- Còn mở như 7.5: AC-01 PARTIAL (fixture ZER-41, runtime, `CART_MARKERS` thật), ack 202 Kafka, ràng buộc trang xác nhận đơn, `samples_after_trial_end`. Chưa Linux/CI từ xa/runtime. Không commit, push, PR, Linear, lab, model hay cloud.
