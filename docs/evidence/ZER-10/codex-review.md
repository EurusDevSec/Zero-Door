# Codex review — ZER-10 + ZER-38 — 20/10/2026

**Verdict: NOT_READY_OFFLINE / CHANGES_REQUIRED.** Một lỗi P1 và mười lỗi P2 dưới đây cần sửa trước khi nhận gói offline. ZER-38 / AC-01 vẫn PARTIAL vì thiếu fixture thật và quan sát runtime; review này không cấp quyền runtime, publication hoặc cập nhật Linear.

## 1. Baseline và phạm vi

- HEAD/base: `55200c9143565c1773cbff57553a9ce858ffe858`, nhánh `zer-10-independent-measurement`; triển khai là dirty/untracked, staged rỗng. Không có commit mới được review thay cho dirty source.
- Review 37 file trong manifest Claude (SHA-256 `b3a33293105ee44f0e772405ca40ddea1b4820ca95cea035da93fdbc6b169292`): package measurement, tests/fixtures, CLI, CI mới và docs/evidence trực tiếp. Mã event_pipeline và contract LOCKED chỉ đọc.
- Đã đọc AC sống qua đúng connector Linear Zero Door: [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap), [ZER-38](https://linear.app/zero-door/issue/ZER-38/dung-probe-nghiep-vu-djoc-lap), cùng In Progress, AC chưa tích. AC khớp gói giao.
- File ngoài gói `docs/detail_zero-door.md` đã có lúc Codex chụp baseline. Giữ nguyên; không quy nó cho Claude. Checker gói báo đúng một vấn đề scope này, không báo drift 37 hash hoặc 27 nguồn bảo vệ.
- Một writer: Codex ghi evidence/review, không sửa nguồn Claude. Hai domain lens của skill GitNexus Review kiểm metrics và probe/transport; findings được root đối chiếu lại với source, script và output trước khi gom.

## 2. Findings chặn — theo mức độ

### ZR10-01 — P1: request INVALID làm mất incident/lượt requested khỏi mẫu số, có thể tạo PASS sai

**Anchor:** [scorer.py:263](../../../agent-orchestrator/measurement/scorer.py#L263), đặc biệt 269–295; intake quarantine 146–155 và invalid_related 575–586.

Incidents chỉ được tạo từ ATTACK_REQUESTED đã qua classify. Một request do harness phát, có run/trial/incident ID nhưng thiếu target_services, bị Archive giữ ở quarantine MISSING_FIELD. Scorer vẫn thấy dấu vết request và effect nhưng không tạo hàng incident cho nó; invalid_related không còn incident nào của trial đó để đánh MISSING.

**Phản ví dụ:** `scorer-probes.json:mixed_invalid_request` gồm hai trial: một E01 sạch và một E01 có request lỗi. Actual: requested=1, N=1, MTTR verdict=PASS. Expected: giữ hai lượt requested; lượt request lỗi MISSING/UNKNOWN có lý do, N=2 và verdict UNKNOWN. Ca chỉ có request lỗi ra EMPTY thay vì thể hiện lượt bị mất. Vi phạm contract §6.4 và AC-03 giữ mọi run/lượt trong mẫu số; không phải một lượt NO_EFFECT được phép loại.

**Sửa:** dựng cohort từ context/harness evidence của lượt requested, gồm request bị quarantine có identity đáng tin (không tạo incident tấn công giả cho C0 chỉ vì có TRIAL_STARTED); không tự đoán trường thiếu. Nếu không thể dựng đủ cohort, chặn nghiệm thu hoặc đánh cohort incomplete thay vì PASS/EMPTY sạch. Thêm cả single-invalid và mixed-valid/invalid ở hai trial; giữ invalid H raw.

### ZR10-02 — P2: DETECTED có đồng hồ chưa xác minh bị biến thành MISSED

**Anchor:** [scorer.py:663](../../../agent-orchestrator/measurement/scorer.py#L663)–673, 739–751 và 772–774.

Nhánh lọc detect dùng continue khi đồng hồ không so được với T_req. Evidence DETECTED đã tồn tại biến mất khỏi tập mốc, nên scorer xem như không phát hiện.

**Phản ví dụ:** `scorer-probes.json:detector_unsynced`: E01 dùng probe HOST_SHARED; chỉ detector đổi sang OFF_HOST, không có CLOCK_SYNC. Actual: RECOVERED_UNDETECTED, mttd=MISSED, không CLOCK_UNVERIFIED, KPI MTTD NOT_PASS với bounds [0,0]. Expected theo contract §4.3: MISSING cho phép đo/nhãn cần so xuyên đồng hồ, cờ CLOCK_UNVERIFIED; total cùng host vẫn có thể báo 90 s. Không được kết luận detector đã bỏ lỡ.

**Sửa:** phân biệt không có detect với có detect nhưng không xác định thứ tự/cửa sổ vì clock; truyền missing/uncertainty tới label, KPI và metric quyết định. Giữ control E01 và E18, thêm unverified detector/decision/executor, không chỉ probe.

### ZR10-03 — P2: M5 gộp sai episode và suy coverage từ việc mọi slot có alert

**Anchor:** [metrics.py:527](../../../agent-orchestrator/measurement/metrics.py#L527)–548. Spec ZER-8 §5.5, dòng 301–304.

Có hai đường cùng phần tổng hợp M5:

1. Alert lúc 50 ở frontend và 51 ở cartservice, hai signature/service khác nhau, coverage đầy đủ: expected 2 episode, 25,899281/h trong W=[22,300); actual 1 và 12,94964/h. Code chỉ giữ thời gian, làm mất khóa episode.
2. Alert phủ cả năm slot nhưng không có detector_coverage: cận slot [1,1] là hợp lệ, nhưng actual vẫn xuất episode/h và verdict OK. Expected episode rate UNKNOWN/null vì chưa chứng minh stream đầy đủ; missing firing có thể nối các episode quan sát.

**Sửa:** nhóm theo khóa detector/signature + service, rồi cộng; tách coverage của toàn stream khỏi số slot chưa biết. Hai repro ở `metrics/counterexamples.json`.

### ZR10-04 — P2: M6 bỏ action đã thực thi nhưng chưa có terminal

**Anchor:** [metrics.py:544](../../../agent-orchestrator/measurement/metrics.py#L544)–551. Spec ZER-8 M6 đếm action thực thi trong cửa sổ benign.

C0 có HEAL_STARTED ở 52, API_ACCEPTED ở 53, thiếu ACTION_COMPLETED. Dù khai báo log action đủ, actual M6_actions_observed=0, M6_verdict=OK. Expected executed=1, terminal thiếu và tác hại chưa rõ nếu chưa có bằng chứng riêng. Dùng completion cũng gán sai cửa sổ cho action bắt đầu và kết thúc ở hai phía biên W.

**Sửa:** đếm action_id được thực thi từ HEAL_STARTED trong W, tách terminal/harm/probe coverage. Không biến thiếu completion thành không có action. Repro `started_action_no_terminal`.

### ZR10-05 — P2: thiếu hoặc INVALID LLM_CALL vẫn cho usage đầy đủ

**Anchor:** [metrics.py:457](../../../agent-orchestrator/measurement/metrics.py#L457)–500; scorer.py:96–107 và 190–219.

- E01 còn LLM DECISION nhưng bỏ mọi LLM_CALL: actual M11 status=OK, calls=0, by={}.
- Thêm retry attempt 2 có usage sai kiểu/giá trị: scorer ghi INVALID, nhưng M11 bỏ call đó rồi vẫn báo calls=1, retries=0, usage_status=COMPLETE và cost_status=COMPLETE.

Expected: giữ cận tổng đã biết và đánh call/usage/cost coverage MISSING ở run/trial/incident liên quan. Không thể suy tổng cuộc gọi đầy đủ từ các record còn hợp lệ; khi số thật chưa biết phải ghi unknown.

**Sửa:** khởi tạo coverage từ trigger/decision có dùng LLM, đưa invalid/quarantine/conflict vào completeness, giữ sums là lower bound khi cần. Repro `llm_decision_with_no_call_records`, `invalid_second_llm_call`.

### ZR10-06 — P2: ground truth hỏng kiểu làm scorer crash

**Anchor:** [metrics.py:282](../../../agent-orchestrator/measurement/metrics.py#L282)–293, phép so ở 287.

Đổi constraints.SCALE_UP.max_replicas thành chuỗi 'four'. Schema raw vẫn nhận vì constraints đang OPEN; run_metrics ném TypeError thay vì trả output có UNKNOWN_GT. ZER-8 §5.4 yêu cầu ground truth hỏng/thiếu được phản ánh là chưa chấm được.

**Sửa:** validate kiểu/phạm vi của proposed GT constraints trước khi dùng; unsupported/malformed → UNKNOWN_GT với reason, giữ incident. Không catch toàn scorer rồi điền mặc định. Repro `metrics/extra.json:malformed_gt_constraint`.

### ZR10-07 — P2: guard verdict mâu thuẫn được chọn theo thứ tự ingest

**Anchor:** [metrics.py:392](../../../agent-orchestrator/measurement/metrics.py#L392)–406, đặc biệt 403. Contract §3.2 quy định mỗi decision_id có 0..1 GUARD_VERDICT.

Cùng proposal có ACCEPT tại 133,1 và REJECT tại 133,2, hai event ID khác nhau. Actual M3 accept_correct=1. Chỉ đảo thứ tự ingest, giữ nguyên ID/timestamp, actual đổi thành false_block=1. Cả hai vẫn báo coverage_scorable=1.

**Sửa:** kiểm cardinality theo business key sau dedup event ID; giữ bằng chứng conflict và báo không xác định/integrity phù hợp contract, không lấy phần tử đầu. Repro `metrics/extra.json:conflicting_guard_*`.

### ZR10-08 — P2: probe có thể coi giao dịch sai số lượng là healthy

**Anchor:** [flows.py:490](../../../agent-orchestrator/measurement/flows.py#L490)–496; assertion ở 405–416.

Builtin gửi quantity=1 nhưng chỉ kiểm product ID trong giỏ, thông báo hoàn tất và UUID mới. Fake server dùng session mới nhưng add hai đơn vị; checkout thực sự nhận hai sản phẩm. Actual pass=true. Đây không phải replay session/order ID; phép kiểm nội dung đang thiếu để xác nhận giao dịch yêu cầu.

**Sửa:** kiểm đúng mặt hàng/số lượng/giỏ của mẫu bằng giao diện quan sát được; bind confirmation với giao dịch khi giao diện có bằng chứng đó. Không tự khóa marker khi chưa đối chiếu Boutique thật. Thêm duplicate/extra/wrong-item negative cùng control lành. Repro `probe/counterexamples.json:duplicate_cart`.

### ZR10-09 — P2: step timeout không được dùng, run cap không chặn giao dịch đang chạy

**Anchor:** [probe.py:75](../../../agent-orchestrator/measurement/probe.py#L75)–80, 121–145; flows.py:333–362; config.py:84–91.

1. step_s=0,05, transaction_s=1; home trả sau khoảng 0,25 s vẫn PASS vì chỉ có transaction deadline.
2. max_duration_s=0,2; một mẫu khoảng 0,64 s vẫn tiếp tục bốn request nghiệp vụ sau home và PASS, rồi mới dừng MAX_DURATION.

Thiết kế mục 2.1 gọi các budget này là điểm dừng cứng. Existing tests dùng step_s bằng transaction_s nên không phân biệt hai nhánh.

**Sửa:** truyền deadline monotonic của run, transaction và từng step; dùng min còn lại trước I/O/lần gửi/bước tiếp theo. Cleanup/delivery grace phải được giới hạn và công bố riêng nếu nằm ngoài workload cap; không âm thầm gộp nghĩa. Repro `step_timeout`, `max_duration`.

### ZR10-10 — P2: cleanup chưa chứng minh sở hữu và có thể bị bỏ qua khi Ctrl+C

**Anchor:** [flows.py:366](../../../agent-orchestrator/measurement/flows.py#L366)–369, 432–438, 448–468; đường ngắt ở 300–315 và __main__.py:114–118.

Hai nhánh cần hai sửa cụ thể:

- Fake fixture mô phỏng response 201 cũ có order_ref của bản ghi có sẵn, nonce cũ; không tạo gì. Flow đánh owned từ status, capture ref, nhận WRONG_RESULT rồi DELETE bản ghi có sẵn. Actual pre_existing_still_exists=false. Không thể suy sở hữu từ 201 hoặc identifier server trả về.
- KeyboardInterrupt ngay sau add-cart thoát khỏi Flow.run trước dòng cleanup, vì cleanup không nằm trong finally. Actual giỏ còn một item, không có /cart/empty. Đây là mô phỏng đúng exception path Python SIGINT, chưa phải thử signal runtime trên lab.

**Sửa:** ràng buộc quyền cleanup với nonce/request của mẫu trước khi DELETE; khi chưa rõ sở hữu thì ghi unresolved, không xóa. Đưa stop/signal về cancel path và bảo đảm cleanup/journal có giới hạn trong finally, không biến mẫu bị ngắt thành PASS. Hai repro `fixture_stale_cleanup`, `keyboard_interrupt_cleanup`.

### ZR10-11 — P2: H sink mang bearer sang origin khác qua redirect và nhận ACK sai đích

**Anchor:** [sink.py:85](../../../agent-orchestrator/measurement/sink.py#L85)–103.

Default urllib theo 302 sang origin khác, đổi POST thành GET và chuyển tiếp Authorization. Server thứ hai trả RECORDED đúng event_id; sink trả DELIVERED dù H archive dự định chưa nhận mẫu. Repro chỉ dùng token SYNTHETIC và hai server loopback do test tạo; không đọc token thật.

**Sửa:** từ chối redirect cho H write, hoặc pin origin/POST theo policy tường minh; không chuyển Authorization qua origin khác. Redirect/ACK bất thường phải giữ event pending hoặc báo refusal rõ. Kiểm cả 302/303 và control H ack chuẩn. Repro `h_sink_redirect`.

## 3. Ghi chú P3 không chặn

**ZR10-N1 — output chưa bảo vệ other exports.** __main__.py:57 chỉ truyền H/O chính vào output.write, bỏ --other-export. Output bên trong other-H-export được tạo thành công. Không ghi đè byte raw trong repro, nên P3; khi sửa thêm mọi input export vào exclusion boundary. Repro `other_input_output`.

Bổ sung kiểm B0 detector-off M5/M6 N/A và M4 dùng trigger thực thay vì nhãn cohort khi sửa aggregator; không dùng B0 detector tắt làm tỷ lệ false alarm 0. Đây là coverage follow-up cùng module, không phải quyền mở rộng scope sang dashboard/agent.

## 4. Sáu điểm Claude đề nghị review

1. **Sequence hở:** hướng coi mất sequence là gap phù hợp missing không thành PASS. Giữ test chống trộn probe/version/trial; không cần owner quyết lại D-04.
2. **MODE_VIOLATION:** giữ evidence/lượt trong cohort và đánh không dùng như nhóm hợp lệ là hướng đúng. Không được để metric khác vẫn mô tả trial đó là đối chứng hợp lệ; formal exclusion/sensitivity theo protocol.
3. **Tên f01_params:** tên khóa chưa bị contract §5.3 khóa bằng JSON; tên có đơn vị hiện tại là giao diện triển khai được ghi rõ, không cần tự đổi LOCKED contract. Harness tương lai phải dùng cùng version/normalizer, không âm thầm mặc định hay đổi đơn vị.
4. **payload.detail:** additive object trong 1.0.0 được giữ raw và consumer cũ bỏ qua; đề xuất thêm enum TLS/HTTP/... ở 1.1.0 vẫn là DRAFT, chưa được phát như enum đã khóa. Tiếp tục ánh xạ về bốn error_class hiện có.
5. **zd-gt-constraints/0:** có thể dùng làm bộ kiểm đề xuất offline, không thay quyết định ZER-50; bắt buộc xử lý GT hỏng như ZR10-06.
6. **Seal cutoff/C0/coverage:** cấu hình tường minh và provenance phù hợp gói offline; ingest_grace, window và tham số formal vẫn OPEN theo ZER-53. Coverage phải được thực thi đúng (ZR10-03/04), không chỉ ghi trong docs.

Không điểm nào ở đây tự cấp quyền chạy fixture/lab/model hoặc chốt tham số formal.

## 5. Kiểm đã thực hiện và giới hạn

| Kiểm | Kết quả độc lập |
| --- | --- |
| verify-measurement.sh --offline, Python 3.12.4 | 71/71 OK; E01 30/60/90/19, OFFLINE_PASS |
| crosscheck_zer37.py | 62 ca, 178/178 khớp |
| Focused probe/CLI controls | 17 + 5 OK |
| Phản ví dụ mới | Giá trị sai/crash tái hiện; xem script + JSON bên dưới; exit 0 của diagnostic không phải sản phẩm PASS |
| Hash gói | 37/37 khớp; 27/27 nguồn protected khớp tại lúc nhận |
| Git | HEAD55200c9, staged rỗng; nguồn Claude không bị reviewer sửa |

**Tái lập bằng Git Bash, chỉ fake/archive tạm:**

~~~bash
python -B docs/evidence/ZER-10/codex-review/scorer-probes.py
python -B docs/evidence/ZER-10/codex-review/metrics/counterexamples.py
python -B docs/evidence/ZER-10/codex-review/metrics/extra.py
python -B docs/evidence/ZER-10/codex-review/probe/counterexamples.py
~~~

Script dùng builder/fake của gói cho envelope/transport và tự đặt phản ví dụ/expected; không patch production source. [Bằng chứng](codex-review/) có intake, output JSON, log 71 test và crosscheck. Bản counterexample portable chỉ đọc nguồn/bằng chứng và in stdout; không tự ghi đè JSON đã lưu. Critic đã kiểm lại draft, sửa hai điểm evidence (không suy raw record thành số provider call, không ghi đè JSON khi retest). Không chạy lại mutant 11/11, Bandit hay toàn bộ hồi quy ZER-9 vì nguồn cũ giữ nguyên; các số đó ở bàn giao Claude, không gọi là kết quả độc lập của lượt này. Chưa chạy Python3.11/Linux/CI từ xa/runtime.

**Giới hạn GitNexus:** index 0babf90 chậm một commit, chưa có package mới untracked. Refresh index-only/PDG đã thử nhưng không tiến sau banner và được dừng. detect_changes chỉ thấy chín tracked file, không đại diện toàn gói; context Producer xác nhận seam dùng lại, explain rỗng không chứng minh taint sạch. Review mã mới dựa trực tiếp source/caller/test và thực thi phản ví dụ; không nhận là graph/PDG coverage hoàn chỉnh.

## 6. Gói sửa gom và retest

- Sửa xuyên suốt 11 finding trong measurement cùng regression trực tiếp; giữ event_pipeline, contract LOCKED, agents/worker/manifests và evidence đã seal ở chế độ chỉ đọc.
- Giữ nguyên nguồn và bằng chứng review này. Tạo fix-01 delta/hash so với manifest Claude; sửa test cùng nguyên nhân, không chỉ hardcode phản ví dụ. Cập nhật thiết kế/runbook/verification phù hợp hành vi cuối.
- Retest 71 suite + các counterexample/negative-control mới; đối chiếu ZER-37 và affected regression. Đặc biệt N không mất lượt; clock thiếu không thành MISSED; M5/M6/M11 giữ missing; deadline/cleanup/H-origin thực sự có hiệu lực.
- Bàn giao một gói READY_FOR_CODEX_RETEST_OFFLINE. Sau khi offline đạt mới trình runtime plan cụ thể cùng fixture ZER-41. Không đóng AC-01/issue/G1 bằng dữ liệu giả.

AC-01: PARTIAL runtime và cần sửa probe. AC-02/03/04: CHANGES_REQUIRED offline. Không commit/push/PR/merge/Linear/lab/API trong lượt này.
