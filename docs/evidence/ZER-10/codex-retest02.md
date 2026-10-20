# Codex retest fix-02 — ZER-10 / ZER-38

**Verdict: CHANGES_REQUIRED_OFFLINE / NOT READY.** Hai P2 còn mở ở các nhánh cùng nguyên nhân của FX01-R1/R2; một P3 của FX01-N1. Không mở lại scorer đã đạt. Chỉ review offline; ZER-38 / AC-01 vẫn PARTIAL vì thiếu fixture và quan sát runtime.

## 1. Findings

### FX02-R1 — P2 — Follow redirect có side effect trước khi kiểm session

Anchor: [flows.py:431](../../../agent-orchestrator/measurement/flows.py#L431), nhất là 440–447. Đây là residual của ZR10-10 / FX01-R1, không phải khẳng định lỗi mới do fix-02 tạo ra.

Cleanup đã đóng băng đúng cookie. Tuy nhiên send() cập nhật jar từ Set-Cookie của response, vòng redirect gửi tiếp bằng jar đó; session() chỉ kiểm sau toàn bộ hop. 307/308 giữ POST và body. Built-in boutique_spec bật follow_redirects ở checkout nên có thể đi vào đường này qua cấu hình hiện có.

**Actual socket/loopback:** giỏ foreign-user có foreign-product. POST /cart/checkout nhận 307, Set-Cookie đổi session sang foreign-user, Location /cart/empty cùng origin allowlist. Log ghi POST /cart/empty dưới foreign-user; giỏ đó bị xóa. Sau hop tiếp theo probe mới báo BUSINESS / SESSION_CHANGED. Cleanup cuối dùng đúng session mẫu và báo DONE; không phục hồi được dữ liệu đã xóa ở redirect. 308 cũng tái hiện. Chỉ dữ liệu giả, không dữ liệu người thật.

Evidence: [script](codex-retest02/probe/redirect_identity.py), [root replay](codex-retest02/probe/redirect-confirm.json), [308](codex-retest02/probe/redirect_308.json), [same-session control](codex-retest02/probe/redirect_control.json). Control giữ session và giỏ foreign-user; CONTENT_MISSING là đúng vì endpoint giả không có xác nhận đơn.

**Cần sửa:** kiểm danh tính trước khi dùng cookie từ response để gửi request tiếp theo, gồm mỗi hop redirect. Session đổi phải dừng trước side effect; giữ credential/target cleanup đã chứng minh. Retest 307/308 foreign-session, nhiều hop và same-session hợp lệ. Kiểm cuối chỉ báo SESSION_CHANGED không ngăn được POST đã xảy ra.

### FX02-R2 — P2 — Stop không rút ngắn deadline của I/O đang chạy

Anchors: [probe.py:64](../../../agent-orchestrator/measurement/probe.py#L64), [probe.py:203](../../../agent-orchestrator/measurement/probe.py#L203), [sink.py:123](../../../agent-orchestrator/measurement/sink.py#L123), [clock.py:86](../../../agent-orchestrator/measurement/clock.py#L86), [flows.py:548](../../../agent-orchestrator/measurement/flows.py#L548).

stop() ghi thời điểm và bật cancel, nhưng grace deadline chỉ cập nhật sau khi I/O trả về. H/reference gọi HTTP với cancel=None và hạn chụp từ cap cũ. Cleanup cũng chụp deadline khi bắt đầu; signal đến trong cleanup không rút ngắn nó. Ba nhánh cùng lỗi truyền stop budget, gom một finding. Cadence wait, fixed-deadline drip ACK và cleanup khi đã cancel trước lúc bắt đầu đều được sửa đúng.

**Phản ví dụ:** cap10 s, grace0,3 s; server loopback riêng chờ1,5 s; sau khi nhận request đặt runner.stop() sau0,1 s, cùng entrypoint CLI dùng cho SIGINT/SIGTERM. Root replay đo:

| I/O đang chạy | Thời gian từ stop tới kết thúc | Expected |
| --- | ---: | --- |
| Chờ ACK H | 1,440 s | khoảng0,3 s + tối đa một lát đọc0,2 s / sai số lịch chạy |
| Đọc reference | 1,416 s | cùng grace |
| Cleanup | 1,404 s | cùng grace |

ACK muộn còn được đánh DELIVERED. Khoảng lệch lớn, không dựa vào test biên0,1 s. Control server delay0,2 s: sau stop khoảng0,302 /0,102 /0,098 s. Không truy vấn gateway/lab thật.

Evidence: [script](codex-retest02/probe/stop_io.py), [root replay](codex-retest02/probe/stop-io-confirm.json), [control script](codex-retest02/probe/stop_io_control.py), [control](codex-retest02/probe/stop-io-control.json).

**Cần sửa:** stop budget phải tác động tới I/O đã bắt đầu, thay vì số deadline chụp trước signal. Phân biệt workload cancel với cleanup được chạy trong grace; cả hai đọc mốc stop sớm nhất. H/reference/cleanup đang chờ phải dừng trong cửa sổ đó, pending/unresolved giữ trung thực. Không tăng timeout/grace hay đổi expected. Test signal sau khi mỗi server đã nhận request; gồm stop trong final flush và signal lặp không gia hạn grace.

### FX02-N1 — P3, không chặn — M11 mất bucket incident đầu khi call_id conflict xuyên incident

Anchors: [metrics.py:603](../../../agent-orchestrator/measurement/metrics.py#L603), [metrics.py:619](../../../agent-orchestrator/measurement/metrics.py#L619). incident_of[call_id] bị ghi đè bởi incident sau; call_keys() dùng lại mapping cho mọi conflicting record. Trace sealed có hai trial / hai incident, hai LLM_CALL cùng call_id chỉ tạo một bucket by.incident. Run/trial/model và tổng usage/cost vẫn MISSING, giữ P3.

Sửa association theo từng record, đánh MISSING cả hai incident mà không nhân đôi tổng call/token/cost. [Script](codex-retest02/metrics/cases.py), [results](codex-retest02/metrics/confirmed.json), key cross_incident_conflict. Same-incident/model conflict đã đạt.

## 2. Phạm vi và kết quả đạt

- HEAD55200c9143565c1773cbff57553a9ce858ffe858, nhánh zer-10-independent-measurement, staged rỗng. Target local fix-02 so với snapshot fix-01, không phải PR; không áp merge-base cho untracked package.
- Manifest fix-02 SHA256 **6c18d7c5d09c5a43859f9325ee87eb6c2c9886657161501db1b330c04dc2bc51**:57file,15đổi/11thêm/31nguyên. Checker intake problems=[], protected28, prior review26, snapshot46.
- Đọc delta7file production measurement, test, design/runbook/checker/mutant/fail-before và consumer liên quan. Thay đổi nằm trong measurement, dùng lại transport/Producer/raw Archive, không tạo pipeline song song. Không yêu cầu abstraction ngoài nhu cầu sửa.
- Python3.12.4 độc lập **125/125**,0error/fail/skip; E01 RECOVERED,30/60/90/19. [Offline log](codex-retest02/offline.txt).
- fail_before.py **PASS**: snapshot byte-identical;16NEGATIVE fail/error trước và đạt sau,6CONTROL đạt sau;7/7 phản ví dụ Codex sai trước/đúng sau. [JSON](codex-retest02/fail-before.json), [log](codex-retest02/fail-before.txt). **Giới hạn:** một số fail-before là API/signature khác;3CONTROL cũng error trước. Không coi cả16 là bằng chứng hành vi cũ. Bảy phản ví dụ cùng snapshot cung cấp đối chiếu hành vi trực tiếp.
- Replay review gốc **29/29** expected. [Log](codex-retest02/replay.txt).
- Crosscheck ZER-37 **178/178**,62case,0differ. [JSON](codex-retest02/crosscheck.json).
- FX01-R3:7test mới + ma trận độc lập **72trường hợp** bounds/request/stop/action qua Archive/seal/export/load không crash, giữ N; thiếu/INVALID/trùng start thành MISSING, trial khỏe không bị ảnh hưởng (control thiếu end có thể giữ RECOVERED nhưng uptime UNKNOWN). [Results](codex-retest02/metrics/confirmed.json).
- Credential/identifier cleanup freeze và journal CLI trên đĩa đạt các ca được sửa. Hai P2 là nhánh lân cận chưa phủ.

## 3. Giới hạn và trạng thái

Linear Zero Door đọc trực tiếp lượt này: ZER-10/38 In Progress, AC chưa tích, đúng workspace zero-door. AC-01 vẫn cần fixture ZER-41, marker Boutique thật và lỗi quan sát runtime. ACK202 Kafka, ràng buộc trang xác nhận đơn và protocol clock giữ mở như gói hiện hành, không thêm thành finding của delta.

GitNexus context ở0babf90, index một commit trước HEAD; query/detect_changes không đại diện measurement untracked. Thử analyze --index-only --pdg chỉ ra banner, không tiến, đã dừng process của review. explain/PDG rỗng trên file mới không là coverage. Review dựa direct source/diff + execution offline, không nhận graph/taint coverage cho mã mới.

Chưa độc lập chạy lại mutant40, Bandit, Python3.11, Docker/remoteCI/runtime; những kết quả đó vẫn là evidence Claude. Không chạy lại toàn bộ event_pipeline khi nguồn của nó giữ nguyên; Archive integration/scorer/crosscheck chạy trong kiểm liên quan. DNS, multi-address connect, fsync chưa chứng minh hard wall-time chung; hai P2 dùng IP loopback trực tiếp, không dựa vào giới hạn này.

## 4. Gói sửa kế tiếp — đối chiếu contract trước khi patch

Đã hai lượt sửa cùng nguyên nhân ownership/deadline. Theo WORKFLOW, chốt ngắn trong note hiện hữu: (1) chứng minh danh tính trước mọi request, gồm redirect; cleanup giữ immutable credential/target; (2) một mốc stop sớm nhất, không gia hạn grace, có hiệu lực cả I/O đang chờ. Không chỉ vá từng test hoặc tăng thời gian.

Snapshot fix-02 trước sửa; xử lý gom FX02-R1/R2 và P3N1 trong measurement/tests/docs liên quan. Manifest/snapshot/evidence Codex cũ và report này read-only. Đầu ra fix-03 có negative/control đúng contract, fail-before hành vi thật, delta/hash và regression bị ảnh hưởng. Chưa lab/API/model/publication/Linear hay gửi tin sang chat khác. Sau offline còn fixture/runtime, CI, publication và owner acceptance theo quyền riêng; chưa Done/G1.
