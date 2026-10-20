# Codex retest fix-01 — ZER-10 + ZER-38 — 20/10/2026

**Verdict: CHANGES_REQUIRED_OFFLINE.** Các phản ví dụ cũ đều đã được sửa (29/29 điểm kiểm đạt), nhưng còn ba nhóm lỗi chặn ở các nhánh cùng nguyên nhân. ZER-38 / ZER-10 AC-01 vẫn PARTIAL vì chưa có fixture và quan sát runtime. Không phải nghiệm thu hoặc Done.

## 1. Phạm vi và baseline

- Local: nhánh `zer-10-independent-measurement`, HEAD `55200c9143565c1773cbff57553a9ce858ffe858`; staged rỗng. Target là gói chưa commit, không phải PR.
- Manifest fix-01: `docs/evidence/ZER-10/fix-01/manifest.json`; 46 file, delta 19 thay đổi + 9 thêm, 18 giữ nguyên so với manifest gốc. Không có snapshot source trước sửa nên không coi mutant đảo ngược là fail-before trên nguyên bản.
- `check_package.py --check` tại intake: 46 file / 28 protected / 14 review-read-only, problems=[]; source và bằng chứng cũ giữ nguyên trong lượt này.
- Linear đọc trực tiếp qua `linear_zero_door`: [ZER-10](https://linear.app/zero-door/issue/ZER-10/djo-suc-khoe-va-thoi-gian-djoc-lap) và [ZER-38](https://linear.app/zero-door/issue/ZER-38/dung-probe-nghiep-vu-djoc-lap) vẫn In Progress, AC chưa tích. Chỉ đọc, không cập nhật.
- Source chỉ đọc. Chỉ tạo scratch/báo cáo retest/bằng chứng, nối cuối issue note và thêm con trỏ NOW. Không lab, API, model, Docker, Kubernetes, cloud, Git publication hay gửi tin sang chat khác.

## 2. Findings còn chặn

### FX01-R1 — P2 — Cleanup vẫn có thể xóa tài nguyên của session khác (ZR10-10 chưa khép)

**Vị trí:** [flows.py:350](../../../agent-orchestrator/measurement/flows.py#L350), [flows.py:439](../../../agent-orchestrator/measurement/flows.py#L439), [flows.py:533](../../../agent-orchestrator/measurement/flows.py#L533).

Request tạo giỏ đã được đánh owned theo session ban đầu. `send()` cập nhật cookie jar ngay khi nhận Set-Cookie; sau đó `session()` phát hiện SESSION_CHANGED. Cleanup trong finally lại dùng cookie jar vừa đổi để POST /cart/empty, trong khi cờ owned thuộc session cũ.

**Phản ví dụ:** fake Boutique có sẵn giỏ `foreign-user`. POST /cart của session mới thêm đúng sản phẩm, nhưng response thay cookie sang foreign-user. Probe báo SESSION_CHANGED; cleanup vẫn báo DONE và xóa giỏ foreign-user, trong khi giỏ do mẫu tạo còn nguyên. Đây là endpoint loopback do kiểm thử tự dựng; không đụng dữ liệu người dùng/lab.

**Yêu cầu sửa:** giữ bằng chứng sở hữu cùng danh tính/session tại thời điểm tạo; cleanup chỉ dùng đúng danh tính ấy. Cookie/session chưa xác minh không được thay thế credential cleanup. Nếu không chứng minh được, giữ nguyên và ghi unresolved. Áp dụng cho redirect và nhánh lỗi trước/sau response; regression phải kiểm cả tài nguyên mẫu và tài nguyên có sẵn.

**Evidence:** [probe/counterexamples.json](codex-retest01/probe/counterexamples.json), key `cookie_switch_cleanup`.

### FX01-R2 — P2 — Trần run/grace chưa bao phủ chờ cadence và I/O của H sink (ZR10-09 chưa khép)

**Vị trí:** [probe.py:155](../../../agent-orchestrator/measurement/probe.py#L155), [probe.py:187](../../../agent-orchestrator/measurement/probe.py#L187), [sink.py:104](../../../agent-orchestrator/measurement/sink.py#L104), [sink.py:149](../../../agent-orchestrator/measurement/sink.py#L149).

Deadline giao dịch và từng bước đã hoạt động. Tuy nhiên, chờ slot chỉ tính target-now, không chặn bởi cap. Publisher chỉ kiểm deadline trước vòng giao event, không truyền deadline vào connect/read ACK hoặc kiểm lại giữa retry. `json.load(response)` có thể đọc body nhỏ giọt lâu hơn socket timeout vì đó là timeout từng lần đọc. Heartbeat/sync cũng emit qua đường không nhận deadline.

**Phản ví dụ:** ACK hợp lệ được fake server gửi mỗi 20 ms; H timeout=50 ms và flush deadline=50 ms vẫn mất khoảng 311 ms, đánh DELIVERED. Ngoài ra cadence 6 s, cap 100 ms, grace 50 ms với MemorySink tức thì vẫn mất khoảng 6.009 s chỉ vì chờ slot. MemorySink không có request H cần dung sai timeout. Ca ngắt sớm sau add-to-cart còn chờ cleanup ~0,3 s dù grace=0,05 s: cleanup_ns được tính từ cap run 30 s trong tương lai thay vì lúc dừng. Đây là các nhánh khác với test cũ chỉ trì hoãn business home.

**Yêu cầu sửa:** một deadline tổng truyền xuyên mọi wait/network operation; chờ cadence lấy min(next-slot,cap), kiểm remaining trước mỗi retry/event và giới hạn cả body ACK/reference clock. Không dựa vào timeout socket như deadline tổng. Dừng sớm/cancel phải có mốc grace riêng phù hợp; outbox chưa giao giữ pending. Kiểm control nhanh, ACK chậm/header/body nhỏ giọt, pending nhiều event, cancel và clock-sync; không phát request mới sau deadline.

**Evidence:** cùng file probe, keys `sink_deadline_drip`, `cadence_wait_over_cap`, `cli_cancel_journal`.

### FX01-R3 — P2 — Cohort khôi phục từ request hỏng vẫn làm scorer crash khi thiếu trial metadata (ZR10-01 chưa khép)

**Vị trí:** [scorer.py:367](../../../agent-orchestrator/measurement/scorer.py#L367), [scorer.py:326](../../../agent-orchestrator/measurement/scorer.py#L326), [scorer.py:755](../../../agent-orchestrator/measurement/scorer.py#L755).

Bản sửa giữ request bị quarantine trong cohort đúng hướng. Nhưng khi không có TRIAL_STARTED/TRIAL_ENDED, `at()/stamp_of()` trả None cho các mốc stop/action. Code đánh TRIAL_MISSING rồi vẫn sort theo `i.ms` trước khi áp dụng nhãn MISSING, dẫn tới AttributeError và không xuất được kết quả cho toàn run.

**Phản ví dụ:** E01 qua Archive/seal/export thật; giữ TRIAL_CONTEXT, request/effect/stop, bỏ TRIAL_STARTED và TRIAL_ENDED; request bị thiếu target_services nên bị quarantine. Trước fix-01 cohort của request này bị bỏ; hiện restored cohort chạm nhánh sort và crash `'NoneType' object has no attribute 'ms'` tại dòng755. Ca request hợp lệ thiếu cùng metadata cũng chạm lỗi tương tự: bề mặt cùng nguyên nhân rộng hơn.

**Yêu cầu sửa:** xử lý mốc không dựng được như MISSING có lý do, giữ incident/N và các incident khác; không chỉ lọc None rồi biến thành không có mốc hoặc MISSED. Rà cả sort/min/max stop, completed SUCCESS và các consumer clock/metadata trong đường restored cohort. Regression gồm trial thiếu/invalid, stop/action có/không, và control E01.

**Evidence:** [metrics/results.json](codex-retest01/metrics/results.json), keys `invalid_request_missing_trial`, `missing_trial`, kèm traceback.

## 3. Ghi chú không chặn riêng

- **FX01-N1 — P3, ZR10-05:** với hai record hợp lệ cùng call_id xung đột, M11 cấp tổng và usage/cost đã là MISSING; nhưng `by/run/actor/model/trial/incident.call_coverage_status` vẫn COMPLETE. [metrics.py:653](../../../agent-orchestrator/measurement/metrics.py#L653) chỉ xét invalid_call_records/decisions_without_call, không xét conflicts. Nên đồng bộ cờ conflict cho bucket liên quan; không coi đây là usage/cost COMPLETE. Evidence `conflicting_call_coverage`.
- Cancellation journal mặc định là list trong RAM; CLI chỉ in summary và outbox chỉ giữ event phát. Vì mẫu cancel không phát nên chi tiết cleanup/ownership của mẫu dở có thể mất khi process thoát. Đây là giới hạn cần đưa vào sửa gom ZR10-10/receipt trước runtime; chưa dùng nó làm một blocker mới riêng.
- Chưa kiểm được binding sản phẩm/số lượng trên trang xác nhận đơn thật, marker Boutique chưa quan sát runtime, ACK202 còn ghi rõ là chưa bền. Không biến các điểm OPEN thành PASS offline hoặc tự thay contract.

## 4. Retest và đối chiếu bàn giao

| Kiểm trực tiếp bởi Codex | Kết quả |
| --- | --- |
| Entrypoint offline, Python 3.12.4, stdlib | 103/103 đạt; 0 fail/error/skip; E01 label RECOVERED, MTTD30/MTTR60/total90/reaction19 |
| Replay phản ví dụ cũ | 29/29 expected; kiểm source harness thích nghi đúng hai dòng chẩn đoán, không sửa bằng chứng Codex |
| Crosscheck ZER-37 | 62 case, 178/178 giá trị khớp |
| Phản ví dụ mới | Fake loopback và raw Archive/export/load; các lỗi mục2 tái hiện được |
| Integrity | Manifest/source/review hashes giữ nguyên; xem final-integrity.json |

ZR10-02/03/04/06/07/08/11 và N1 cũ không còn phản ví dụ mở trong phạm vi đã retest. ZR10-01/09/10 đạt các phản ví dụ ban đầu nhưng còn nhánh residual mục2. ZR10-05 đạt phản ví dụ ban đầu, còn ghi chú P3 nested coverage. Không tuyên bố 12 finding đều đóng hoàn toàn.

103 test bao gồm regression mới và kiểm control. Không chạy lại toàn bộ mutant/Bandit/Python3.11/Linux/remoteCI hay hồi quy ZER-9 không đổi; số liệu những kiểm ấy trong verification là bằng chứng Claude, không phải kiểm độc lập lần này. Mutant đảo ngược không thay được snapshot source cũ.

GitNexus index còn ở0babf90, chậm1commit, chưa chứa measurement untracked. Đã thử refresh `analyze --index-only --pdg`, chỉ ra banner rồi không tiến triển nên dừng đúng process của lượt này. `context(Producer)` xác minh seam contract dùng lại; `context(score)` không có symbol; detect_changes chỉ thấy9file tracked. Không suy không có consumer từ graph rỗng; không tuyên bố đã phủ PDG/taint cho mã mới. Kiểm trực tiếp source/consumer và chạy phản ví dụ là căn cứ chính.

Bản portable của hai script đã chạy lại độc lập từ thư mục evidence, vẫn tái hiện lỗi; script chỉ in JSON, không ghi đè JSON bên cạnh. Chạy từ gốc repo: `python -B docs/evidence/ZER-10/codex-retest01/probe/counterexamples.py` và `python -B docs/evidence/ZER-10/codex-retest01/metrics/cases.py`. Các script in quan sát nên exit 0 không có nghĩa sản phẩm PASS. Reviewer mới thêm report/evidence ngoài allowlist của checker fix-01; không sửa checker hay manifest cũ để che thay đổi. Kiểm integrity riêng xác nhận 46/46 package, 28/28 protected và 14/14 review cũ khớp hash.

## 5. Gói sửa gom tiếp theo

Claude xử lý FX01-R1…R3, FX01-N1 và các nhánh cùng nguyên nhân trong measurement/scorer/flows/probe/sink, regression/plan/docs liên quan. Giữ report/bằng chứng Codex và manifest gốc/fix-01 chỉ đọc; lưu delta fix-02 riêng, có snapshot before trước khi sửa để kiểm fail-before thật. Không cần sửa event_pipeline/contract/agent/worker hay mở scope lab.

Trả một gói READY_FOR_CODEX_RETEST_OFFLINE: expected trước, negative + control, affected regressions, hash/delta và giới hạn; note append/NOW prepend. Chưa API/lab/model/publication/Linear. Sau khi offline đạt mới xử lý fixture/runtime theo quyền riêng, CI/review/merge và Hoàng nghiệm thu; chưa thể đóng ZER-38/AC-01 hoặc G1.
