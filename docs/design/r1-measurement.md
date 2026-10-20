# ZER-10 / ZER-38 — Đo độc lập: probe nghiệp vụ, recovery evaluator, scorer raw

[Ghi chú issue](../delivery/milestones/R1-measurement/probes-and-metrics.md) · [Contract zd-event/1.0.0 (LOCKED)](r1-event-contract.md) · [Runbook](../runbooks/independent-measurement.md) · [Verification](../evidence/ZER-10/verification.md)

**Trạng thái:** giao diện triển khai của gói Claude 20/10/2026, chờ Codex review. Đây là code và kiểm thử offline, chưa phải bằng chứng runtime. Mọi ví dụ và fixture đều là SYNTHETIC. Tài liệu không đổi contract đã khóa, D-01…D-05 hay F-01…F-09. Những điểm contract để OPEN được ghi rõ là đề xuất, kèm nơi quyết định.

## 1. Ba vai và ranh giới mặt dữ liệu

| Vai | Module | Mặt | Đọc | Ghi |
| --- | --- | --- | --- | --- |
| Probe nghiệp vụ (ZER-38) | `measurement/probe.py`, `flows.py`, `clock.py`, `sink.py` | H | Chỉ target nghiệp vụ trong allowlist và đồng hồ tham chiếu | PROBE_SAMPLE, PROBE_HEARTBEAT, CLOCK_SYNC qua H gateway (vai `probe`); outbox cục bộ |
| Recovery evaluator (H) | `measurement/recovery.py` (`evaluate`, `RecoveryMonitor`, `evaluator_payloads`) | H | Mẫu probe ở H | RELAPSE, RECOVERY_VERIFIED (vai `recovery_evaluator`) |
| Scorer (S) | `measurement/raw.py`, `scorer.py`, `metrics.py`, `output.py` | S | Export sealed của H và O (cùng export các run khác khi kiểm liên run) | `score.json`, `incidents.csv`, `usage.csv` vào một thư mục mới |

- Probe không đọc heal history, ground truth, dashboard hay O. Code không import `event_pipeline.client` (O-only). File key H của probe phải chứa đúng một vai `{"probe": token}`.
- Scorer không gửi gì về O gateway hay archive. Output phải nằm ngoài các thư mục export đầu vào. Artifact S không quay sang O.
- Code tái dùng `contract.Producer/validate/canonical` và `store.Archive` của ZER-9, không chép store/gateway.

## 2. Probe nghiệp vụ

### 2.1 Plan (`zd-measurement-plan/0`)

Plan là JSON tường minh, được `config.plan` kiểm toàn bộ và báo đủ mọi lỗi cùng lúc. Code không có giá trị mặc định cho tham số đo.

| Trường | Ý nghĩa |
| --- | --- |
| `provenance` | `SYNTHETIC`, `PILOT` hoặc `LOCKED`. Chỉ protocol ZER-53 mới cấp `LOCKED`; code không tự nâng hạng. |
| `f01` | `delta_s, k, s_s, l_ms, gap_s, eps_s, cap_det_s, cap_rec_s` (mục 5.1). Yêu cầu `gap_s ≥ delta_s`. |
| `probe` | `probe_id, probe_version, flow, clock_id` (tên trung tính `^[a-z][a-z0-9_-]{0,62}$`) và `clock_source`. |
| `timeouts` | `step_s ≤ transaction_s`; `transaction_s × 1000 ≥ L`, nếu không SLOW sẽ không bao giờ quan sát được. Mỗi bước dừng ở mốc sớm nhất trong ba mốc: deadline giao dịch, `step_s` tính từ đầu bước, và trần run (fix-01). |
| `budget` | `max_duration_s`, `max_samples`, `max_requests` đều bắt buộc và là điểm dừng cứng. `max_duration_s` cắt cả giao dịch đang chạy: mẫu bị cắt là CANCELLED (`RUN_BUDGET`), chỉ ghi journal. `grace_s` (bắt buộc, trong (0, 60]) giới hạn phần chạy sau trần: cleanup của mẫu bị cắt, heartbeat cuối và gửi outbox. Mọi chờ slot, ghi H, đọc đồng hồ tham chiếu và cleanup nhận cùng một deadline tổng (fix-02): trong workload là trần; sau khi dừng là cuối cửa sổ grace, tính từ mốc dừng sớm nhất (trần, lúc mẫu bị cancel hoặc lúc nhận tín hiệu). Tổng thời gian ≤ `max_duration_s + grace_s`; dừng sớm được nhận trong một lát đọc (0,2 s). |
| `heartbeat_s` | Chu kỳ PROBE_HEARTBEAT, tối đa `10 × gap_s`. |
| `target` | `origin` phải nằm trong `allowed_origins`. Redirect ra ngoài allowlist là lỗi. |
| `clock_sync` | Bắt buộc khi đồng hồ là `OFF_HOST`/`UNKNOWN`: `method`, `interval_s`, `reference_url`. |
| `flow_spec` | `{"builtin": "boutique-checkout" \| "fixture-order-synthetic", "args": {...}}` hoặc spec đầy đủ (mục 2.2). |

### 2.2 Flow spec: giao dịch, không phải GET 200

Mỗi bước có `method`, `path`, danh sách `status` mong đợi và **ít nhất một kiểm nghiệp vụ** (`contains`, `contains_ci`, `count`, `capture`, `json_equals`, `redirect_to`). Spec chỉ có status sẽ bị `SpecError`, vì HTTP 200, `/healthz` hay Ready không đủ làm bằng chứng nghiệp vụ.

- **Phiên mới mỗi mẫu.** Cookie jar trống. Bước `session: "issue"` đòi server cấp session mới, chưa từng thấy trong bộ nhớ của probe. Nếu không, mẫu bị đánh `SESSION_NOT_ISSUED` hoặc `STALE_SESSION`; session đổi giữa luồng là `SESSION_CHANGED`.
- **Không tái dùng giỏ hay response cũ.** Giá trị `capture` đánh `fresh` (như mã đơn) phải mới, nếu không là `STALE_RESPONSE`. Fixture còn ghi một nonce ngẫu nhiên vào bản ghi và đọc lại để so.
- **Template an toàn.** Biến phải được khai báo hoặc capture ở bước trước. Giá trị thế vào path được percent-encode thành đúng một segment. URL hay header có ký tự điều khiển bị từ chối (`INVALID_REQUEST`, `MALFORMED_REDIRECT`), nên server trả gì cũng không chèn được request line hay header.
- **Tài nguyên sở hữu và dọn dẹp (fix-01).** Bước `owns` phải kèm `ownership`, tức bằng chứng sở hữu: `{"session": true}` (tài nguyên nằm trong session mới mà server vừa cấp cho mẫu) hoặc `{"json_equals": {...}}` có nonce của mẫu (bản ghi trả về phải lặp lại nonce). Status 201 hay identifier do server trả **không** chứng minh sở hữu. Từ lúc gửi request tạo, tài nguyên được ghi nhận là "đã yêu cầu". Nếu chứng minh được thì nó được dọn bằng chính session của mẫu, kể cả sau lỗi, stop, trần run hoặc Ctrl+C. Nếu không chứng minh được thì cleanup báo `UNRESOLVED_OWNERSHIP` và **không xóa**. Bước dọn có deadline riêng, không bị cancel và chạy trong `finally`. `releases` nghĩa là luồng đã tự trả tài nguyên.
- **Danh tính cleanup đóng băng lúc tạo (fix-02).** Cookie gửi kèm request tạo được giữ làm credential cleanup. Set-Cookie sau đó (trong chính response, ở redirect hay ở bước sau) không đổi được danh tính dọn dẹp, và request cleanup không cập nhật cookie jar. Session chỉ được tính là sở hữu khi cookie trong jar đúng là session mẫu vừa được cấp. Bản ghi chứng minh bằng nonce được dọn theo identifier capture cùng bước chứng minh; spec có path cleanup dùng biến capture sau bước đó bị `SpecError`. Cleanup hết thời gian báo `GRACE_EXPIRED` hoặc `CLEANUP_TIMEOUT` (tài nguyên có thể còn, operator xem journal).
- **Ngắt.** SIGINT/SIGTERM ở CLI và KeyboardInterrupt trong giao dịch đều đi đường cancel: cleanup có giới hạn vẫn chạy, mẫu được ghi journal (`SAMPLE_CANCELLED`, reason `INTERRUPTED`) và không bao giờ thành PASS. Run kết thúc với `INTERRUPTED` sau khi gửi outbox trong `grace_s`. Cleanup của mẫu dở bị giới hạn bởi `grace_s` tính từ lúc dừng, không phải từ trần run ở tương lai (fix-02).
- **Journal bền (fix-02).** Ở CLI, journal được ghi ra đĩa (`--journal`, mặc định `<outbox>.journal.jsonl`; mỗi dòng fsync): `PROBE_STARTED`, `SAMPLE_CANCELLED` kèm kết quả cleanup, `INTERRUPTED`… vẫn còn sau khi process thoát, dù mẫu bị cancel không được phát. Summary in đường dẫn journal và `unresolved_cleanup` (mọi tài nguyên cleanup chưa DONE). Không ghi được journal thì probe từ chối chạy (exit 5) trước request đầu tiên; lỗi ghi journal giữa chừng dừng probe như lỗi outbox.

**Boutique** (`boutique-checkout/1`): home có link `/product/{id}` → trang sản phẩm có id (và tên sản phẩm nếu cấu hình) → `POST /cart` (quantity 1, sở hữu theo session mới) phải redirect về `/cart` → giỏ có **đúng một dòng**, dòng đó là sản phẩm yêu cầu, **quantity = 1** → checkout có "order is complete" và mã xác nhận UUID mới. Marker giỏ (`CART_MARKERS`: `line` "SKU #", `item` "SKU #{product_id}", `quantity_regex` `Quantity:\s*(\d+)`) theo hình dạng template giỏ của Online Boutique upstream. Đây là OBSERVED-SHAPE, phải đối chiếu trên trang pilot; plan có thể thay qua `flow_spec.args.cart_markers`. Trang xác nhận đơn chưa có bằng chứng giao diện để gắn với mặt hàng/số lượng, nên ràng buộc đó dừng ở giỏ (OPEN tới pilot). Nếu checkout không xác nhận, giỏ của mẫu được làm trống. Hình dạng luồng lấy từ phần purchase của `verify-local-lab.sh`; marker nội dung phải được đối chiếu với trang quan sát thật trong pilot (mục 6).

**Fixture** (`fixture-order/0-synthetic`, **SYNTHETIC**): `POST /fixture/orders` với `{item, note: nonce}` phải trả 201 `{order_ref, item, note, status: "STORED"}`; `GET /fixture/orders/{order_ref}` phải trả đúng bản ghi; `DELETE` dọn bản ghi. Đây là đề xuất giao diện cho ZER-41, chưa phải fixture đã tồn tại. Spec không chứa executor hay payload SQLi; item là hằng benign, nonce là hex ngẫu nhiên.

### 2.3 Mẫu, thời gian và phân loại lỗi

- `t_start` đọc từ đồng hồ probe. `t_end = t_start + elapsed`, với elapsed lấy từ bộ đếm monotonic, nên `t_end ≥ t_start` và latency là monotonic. `ts_event` của mọi event probe cũng đọc từ đồng hồ probe. Lưu theo định dạng ms floor.
- Đồng hồ `HOST_SHARED` đọc wall clock của host. Đồng hồ `OFF_HOST`/`UNKNOWN` neo wall clock một lần rồi tiến theo `perf_counter`, nên bước nhảy wall giữa trial không đảo thứ tự mẫu; CLOCK_SYNC đo chính đồng hồ này. `resolution_ms = max(1, độ phân giải khai báo, bước quan sát)`; trên Windows, `time.time` cho khoảng 15,6 ms.
- Nhịp chạy trên monotonic. Khi overrun, các slot đã lỡ bị bỏ qua (`SLOTS_SKIPPED_OVERRUN` trong journal), không chạy dồn để bù. Khoảng trống còn lộ rõ trong dữ liệu.
- Transport là client HTTP/1.1 tự viết trên socket. Connect, TLS, send và từng lát đọc 0,2 s đều dùng thời gian còn lại của giao dịch, nên body nhỏ giọt vẫn dừng đúng deadline và cancel được nhận giữa hai lát đọc.

| Lớp chi tiết (`detail.detail_class`) | `error_class` zd-event/1.0.0 |
| --- | --- |
| TIMEOUT (connect/TLS/send/đọc; reason `STEP_DEADLINE` hoặc `TRANSACTION_DEADLINE`) | TIMEOUT |
| CONNECT, TLS | CONNECT |
| HTTP (status, redirect, response hỏng), PARSE, SCHEMA, BUSINESS (nội dung, session/giỏ/response cũ) | CONTENT |
| SLOW (mọi bước đạt, latency > L) | SLOW |
| CANCELLED (stop, `RUN_BUDGET`, `INTERRUPTED`) | **Không phát mẫu**: chỉ ghi journal, không tiêu sequence, vẫn dọn tài nguyên |

Mẫu bị cancel không phải đạt cũng không phải lỗi. Thời gian của nó trở thành khoảng trống mà scorer tính là U. Probe chết, slot bị bỏ hay mẫu bị mất đều hiện ra dưới dạng khoảng trống thời gian hoặc lỗ sequence, không bao giờ thành healthy.

### 2.4 Trường bổ sung của PROBE_SAMPLE — đề xuất MINOR

Contract để chi tiết từng bước của PROBE_SAMPLE cho ZER-38 bổ sung theo quy tắc MINOR. Bản này **chưa đổi contract**. Probe vẫn phát `schema_version = zd-event/1.0.0` với đủ trường đã khóa, cộng một object tùy chọn `payload.detail`; consumer 1.0.0 bỏ qua object này nhưng giữ nguyên trong raw:

```json
{"schema": "zd-probe-detail/0", "detail_class": "BUSINESS", "reason": "STALE_SESSION",
 "steps": [{"name": "home", "status": 200, "ok": true, "ms": 12.4}], "requests": 5,
 "cleanup": {"cart": "DONE"}, "captures": {"order_id_sha256_16": "…"},
 "spec_version": "boutique-checkout/1", "provenance": "…"}
```

`detail` không chứa body, cookie, giá trị form hay số thẻ. Giá trị capture chỉ được giữ dưới dạng tiền tố SHA-256. **Đề xuất MINOR `zd-event/1.1.0` cụ thể:** (a) công nhận `payload.detail` là trường tùy chọn; (b) thêm `TLS`, `HTTP`, `PARSE`, `SCHEMA`, `BUSINESS` vào `error_class`. Nếu đề xuất được khóa, ánh xạ ở bảng trên có thể bỏ. Scorer chỉ dùng các trường đã khóa.

### 2.5 H sink và outbox

- Mọi event được nối và fsync vào outbox JSONL trước khi gửi. Gửi lại luôn dùng **cùng** envelope (cùng `event_id`); thứ tự giữ nguyên, event sau không vượt event trước chưa gửi.
- `POST /events` của H gateway: chỉ **201** với `status` RECORDED/DUPLICATE/SEALED_DUPLICATE và đúng `event_id`, từ đúng URL đã cấu hình, mới là đã giao. 422 là quarantine vĩnh viễn và 409 là late: cả hai được ghi vào outbox, không gửi lại. 5xx, 429, timeout, lỗi kết nối hay 202 (ack chưa bền, ví dụ broker) nghĩa là chưa rõ kết quả nên gửi lại sau. 401/403 làm probe dừng với `SINK_UNAUTHORIZED`.
- **Không redirect, không proxy (fix-01).** Sink dùng chính client HTTP/1.1 có giới hạn của probe (`flows.request`, từ fix-02): không có proxy và không theo 3xx, nên bearer token chỉ đi tới origin H đã cấu hình. 3xx, 2xx khác 201, ACK sai `event_id`/`status` làm probe dừng với `SINK_REFUSED`. Event vẫn nằm trong outbox, không bị đánh dấu đã giao.
- **Deadline tổng cho mỗi lần gửi (fix-02).** Một lần gửi kết thúc trước min(`timeout_s`, deadline của flush); deadline phủ connect, gửi, header và toàn bộ body ACK, nên ACK chậm hay nhỏ giọt không giữ được probe. Publisher kiểm deadline trước mỗi lần thử, kể cả retry, và không mở request mới sau deadline. Hết hạn thì event giữ pending trong outbox; heartbeat/sample phát qua cùng deadline.
- Ghi outbox lỗi thì probe dừng ngay (`PERSISTENCE_FAILED`), vì raw sẽ mất. Dòng outbox bị cắt dở thì không mở được, cần operator xử lý.
- Probe khởi động lại trong cùng trial thì tiếp tục sequence từ outbox, vì khóa mẫu là `(trial_id, probe_id, probe_version, sequence)`.

### 2.6 Đồng hồ và CLOCK_SYNC (phương pháp OPEN)

`cristian()` ghi `offset = trung điểm(gửi, nhận) − số đọc tham chiếu`, `uncertainty = RTT/2 + hai độ phân giải`, cùng `method = "cristian-http/0"` trong mỗi CLOCK_SYNC. Endpoint tham chiếu (`{"clock_id","utc_ms","resolution_ms"}` trên đồng hồ host) **chưa có trong lab**. Khi sync lỗi, probe đếm lỗi và **không** phát offset 0, nên đồng hồ chưa xác minh. Đọc tham chiếu dùng cùng client có giới hạn, theo deadline của run (trần hoặc cuối grace), không proxy, không theo redirect (3xx là đọc lỗi) (fix-02). Phương pháp đo, mô hình trôi và ngưỡng sai số vẫn là F-01/ZER-38 OPEN.

## 3. Recovery evaluator (§7.5, D-04)

`evaluate(samples, t_eff, K, S, gap, cap)` chạy trên số đọc của đồng hồ probe:

1. Chỉ xét mẫu có `t_start ≥ T_eff`, bắt đầu sau mẫu lỗi đầu tiên.
2. Chuỗi K mẫu đạt liên tiếp, mỗi cặp cách nhau tối đa `gap` **và sequence liên tiếp**. T_rec là `t_start` của mẫu thứ K.
3. Cửa sổ S: mẫu lỗi trong (T_rec, T_rec+S] là RELAPSE, tìm tiếp sau mẫu lỗi. Gặp khoảng trống hay lỗ sequence là `GAP_IN_S`, tìm tiếp sau khoảng trống. Hết dữ liệu là `DATA_ENDS_IN_S`. S = 0 thì mẫu thứ K đủ điều kiện.
4. Ứng viên có T_rec đúng bằng `T_eff + cap` vẫn được xét đủ S; ứng viên sau mốc đó không được xét.
5. `sample_seq_range = [mẫu đầu chuỗi K, mẫu đầu tiên tại hoặc sau T_rec+S]`. `evidence_complete_at` là `t_end` lớn nhất trong khoảng; `samples_sha256 = "sha256:" + SHA-256(JSON chuẩn hóa danh sách event_id)`.
6. Kết quả: VERIFIED; TIMEOUT khi probe phủ tới `T_eff + cap` mà không có ứng viên chưa xác minh được; ngược lại là MISSING_PROBE.

**Quyết định cần Codex review:** một sequence bị thiếu giữa hai mẫu cách nhau ≤ gap được coi là khoảng trống. Lý do: mẫu đã được đo nhưng mất kết quả thì không biết đạt hay lỗi. Quy tắc này chặt hơn oracle ZER-37 (oracle chỉ xét khoảng cách thời gian), nhưng không đổi kết quả của ca nào trong §10.

`RecoveryMonitor` nhận mẫu tăng dần và phát mỗi quyết định đúng một lần. RELAPSE được phát khi thấy mẫu lỗi; RECOVERY_VERIFIED chỉ được phát sau khi đã có mẫu tại hoặc sau T_rec+S.

## 4. Scorer

### 4.1 Đầu vào và kiểm raw

`raw.Export` chỉ nhận export `zd-export/2` đúng plane. Các kiểm bắt buộc: hash/size của mọi file khớp `export.json`; `manifest.json` khớp seal; hash raw và rejections khớp seal; số dòng khớp; hash từng dòng khớp; mọi bản ghi raw đúng `run_id`. Lệch bất kỳ điểm nào là `RawError` và không có output. Raw không bao giờ bị sửa.

### 4.2 Phân loại dữ liệu

| Nguồn | Xử lý |
| --- | --- |
| Bản trùng cùng `event_id` và cùng hash | Đếm `duplicates`, giữ bản đầu |
| Cùng `event_id`, khác hash; quarantine INTEGRITY_ERROR; hai mẫu cùng khóa | INTEGRITY_ERROR → incident liên quan MISSING |
| Validator transport + kiểm liên trường của scorer (PROBE_SAMPLE, CLOCK_SYNC, EFFECT, RV/RELAPSE, LLM_CALL…) | INVALID; thuộc loại mốc bắt buộc thì incident liên quan MISSING (§6.4) |
| Quarantine `MISSING_FIELD/INVALID/SEMANTIC/INVALID_ID/INVALID_TIMESTAMP`, binding `RUN/TRIAL_CONTEXT_MISSING`, `CONTEXT_IMMUTABLE` | Như INVALID |
| Quarantine/raw SOURCE_VIOLATION, PLANE_VIOLATION, UNSUPPORTED | Lưu, đếm, không dùng; tự chúng không làm incident MISSING |
| Quarantine LINK_CONFLICT | LINK_CONFLICT cho incident cùng `incident_id`, hoặc cùng trial và trong cửa sổ |
| MODE_VIOLATION (raw hoặc quarantine) | Trial không dùng được cho nhóm đó: incident **MISSING** kèm lý do MODE_VIOLATION, vẫn ở lại N (quyết định bảo thủ cần review) |
| LEAK_DETECTED bị quarantine ở O | Kết quả rò của trial là LEAK_DETECTED |
| `late.jsonl` (LATE_INGEST sau seal) | Đếm, không dùng; KPI vẫn tính lại từ mẫu. Riêng ATTACK_REQUESTED đến muộn thì lượt đó vẫn ở cohort (xem dưới) |
| ATTACK_REQUESTED không dùng được (INVALID/quarantine/late/UNSUPPORTED/archive scope) (fix-01) | Lượt requested **vẫn ở lại N**: incident MISSING với `REQUEST_INVALID` hoặc `REQUEST_LATE`, `TARGETS_UNKNOWN`. Chỉ đọc run/trial/incident ID; không đoán target, flow hay thời gian. Request không gán được ID tin cậy làm cohort `INCOMPLETE` (cờ `COHORT_INCOMPLETE`), khi đó mọi verdict KPI là UNKNOWN. Bản ghi từ nguồn khác harness (SOURCE/PLANE_VIOLATION) không phải request. TRIAL_STARTED/TRIAL_CONTEXT không tạo incident giả |
| Hai event khác nhau cùng khóa nghiệp vụ (DECISION/`decision_id`, GUARD_VERDICT/`decision_id`, API_ACCEPTED/`action_id`) (fix-01) | `cardinality_violations`; khóa đó bị đánh conflicted, metric báo chưa rõ, không chọn theo thứ tự ingest |
| Quarantine phạm vi archive (UNSCOPED) | Đếm; không gán vào run theo thời gian |
| Event của run khác mang `incident_id`/`trial_id` của run này | LINK_CONFLICT. Cần truyền `--other-export`; thiếu thì run mang cờ `CROSS_RUN_LINKS_UNCHECKED` |

### 4.3 Ghép, mốc và nhãn

- Ghép theo §6.3: ID tường minh, rồi chuỗi nhân quả (inputs/decision_id/action_id/causation_id, lan truyền tới điểm dừng), rồi luật cửa sổ cho DETECTED không có đường nào khác, rồi lan truyền lại. Các đường dẫn tới incident khác nhau, sai trial hoặc `decision_id` lệch HEAL_STARTED đều là LINK_CONFLICT. Nhiều ứng viên sau khi lọc service là AMBIGUOUS. DETECTED lệch service là TARGET_MISMATCH. ORPHAN thuộc loại bắt buộc nằm trong cửa sổ, kể cả khi `incident_id` không tồn tại, làm incident MISSING.
- Đồng hồ (§4.3): đồng hồ được xác minh khi có CLOCK_SYNC ≤ TRIAL_STARTED và ≥ TRIAL_ENDED, mọi lần đo có uncertainty và resolution đã biết; HOST_SHARED là tham chiếu. Offset được nội suy tuyến tính trên trục của chính đồng hồ. So sánh xuyên đồng hồ chưa xác minh là MISSING kèm `CLOCK_UNVERIFIED`. Total recovery (cùng đồng hồ probe) và reaction (cùng host) vẫn được báo. Sai số đi kèm từng duration.
- **Bằng chứng tồn tại nhưng không xếp được thứ tự (fix-01).** DETECTED đã gắn vào incident mà không so được với T_req thì `t_det_status = CLOCK_UNVERIFIED`: MTTD, MTTR và reaction là MISSING, nhãn họ RECOVERED thành MISSING (vì UNDETECTED/BEFORE_DETECT/RECOVERED đều cần T_det), total vẫn báo, và **không bao giờ** thành MISSED. Tương tự, ACTION_COMPLETED SUCCESS trên đồng hồ executor chưa xác minh làm reaction MISSING (`ACTION_CLOCK_UNVERIFIED`), không phải NO_SUCCESS. DECISION trên đồng hồ chưa xác minh cho M1 `MISSING_ORDER` và M10 `clock_missing`. Hai proposal cùng thời điểm sớm nhất cũng là `MISSING_ORDER`.
- **Mốc không dựng được (fix-02).** Trial không có TRIAL_STARTED dùng được (thiếu, INVALID/quarantine hoặc trùng) thì không có mô hình đồng hồ cho trial: incident MISSING với `TRIAL_MISSING`, vẫn ở N, kể cả khi request của nó cũng hỏng. T_stop hoặc SUCCESS không đặt được thì không vào sort/min: `t_stop_status = CLOCK_UNVERIFIED`, AFTER_STOP và reaction là MISSING, không bao giờ là "không có stop" hay NO_SUCCESS. Incident ở trial khác giữ nguyên kết quả. Uptime vẫn liệt kê trial đó với `TRIAL_BOUNDS_MISSING`.
- Mốc: T_req/T_stop từ harness; T_eff từ EFFECT_EVALUATED; T_det là DETECTED sớm nhất đúng service trong [T_req−ε, T_eff+cap_det]; T_rec tính lại từ PROBE_SAMPLE. RECOVERY_VERIFIED/RELAPSE chỉ dùng để so trên mọi trường (EVALUATOR_MISMATCH khi lệch, vắng, INVALID hoặc phát trước `evidence_complete_at`).
- Không lấy heal history, replica, ACTION SUCCESS hay `ts_ingest` làm mốc. Action FAILED, PARTIAL, TIMEOUT, thiếu terminal hay không có action vẫn có thể có recovery, nhưng gắn `NO_ACTION_BEFORE_RECOVERY`, không ghi công healer.
- Nhãn: MISSING, UNKNOWN_EFFECT, CONFIRMED_NO_EFFECT, RECOVERED, RECOVERED_AFTER_STOP, RECOVERED_BEFORE_DETECT, RECOVERED_UNDETECTED, TIMEOUT, MISSING_PROBE, theo bảng §7.5. CONFIRMED_NO_EFFECT chỉ được nhận khi mẫu raw phủ kín [T_req, T_req+W_eff] với khoảng cách ≤ gap và không có mẫu lỗi.

### 4.4 Tổng hợp (`metrics.py`)

- **KPI (ZER-32 §3.4, D-01):** requested, CONFIRMED, CONFIRMED_NO_EFFECT, UNKNOWN_EFFECT và N; tỷ lệ MTTD < 60, MTTR < 120 và < 180, reaction < 60 trên N; cận missing; mean mô tả; verdict EMPTY, NO_ELIGIBLE, UNKNOWN, NOT_PASS, PASS hoặc FAIL. Dấu `<` là nghiêm ngặt. Báo kèm recovered rate, failure rate (TIMEOUT), unknown rate, phân phối total/MTTR của các lượt recovered và nhãn theo trial.
- **M8 R(t):** cận dưới và cận trên tại 120, 180 và cap_rec, cùng trạng thái median.
- **Uptime (§3.7, D-05):** W = [warmup_end, TRIAL_ENDED); hợp U của mọi luồng bắt buộc với outage. D_point, D_min, D_lower và A_lower, A_point, A_upper; PASS chỉ khi A_lower ≥ 0,999. Luồng bắt buộc chưa đăng ký probe thì U = W. Thiếu cấu hình hoặc warm-up chưa đạt cho ra NO_REQUIRED_FLOWS, WARMUP_NOT_REACHED hoặc INVALID_WINDOW; đồng hồ chưa xác minh cho ra CLOCK_UNVERIFIED.
- **Quyết định (ZER-8 §5.3–5.5):** quyết định đầu tiên là PROPOSAL sớm nhất sau T_det từ bên quyết định của nhóm. Fallback RULES sau lượt LLM lỗi là FALLBACK_RULES. Các tầng M1 (cohort `decision_required`, cận UNKNOWN_GT/UNKNOWN_COHORT/MISSING_ORDER/DECISION_CONFLICT, macro C1–C4 với trọng số cố định, không bỏ lớp rỗng), M1c (kèm coverage), M2 (phễu, thêm `trigger_unknown`), M3 (chấm từng proposal tới guard: chặn đúng, chặn nhầm, chưa rõ, `conflicting_verdicts`), M4, M10, cùng số action thực thi, terminal (thêm `CONFLICT`), false action và coverage. M4 chỉ tính incident có T_det quan sát thật (không dùng nhãn cohort), số T_det chưa xếp được báo riêng. B0 là N/A.
- **Kiểm tham số action** dùng bộ quy tắc đề xuất `zd-gt-constraints/0`: SCALE_UP (`service` ∈ target, `replicas` nguyên và `≤ max_replicas`, với `max_replicas` nguyên ≥ 1), BLOCK_IP (`sources` là chuỗi, khác rỗng, ⊆ S_att; TTL trong [min, max] với 0 ≤ min ≤ max), ROLLBACK (`revision` = known_good). Mọi trường ground truth được kiểm kiểu/phạm vi trước khi so (fix-01). Trường hỏng không làm scorer crash và không được thay bằng mặc định: `decision_required` hỏng thành UNKNOWN_COHORT, `acceptable_actions`/ràng buộc hỏng thành UNKNOWN_GT kèm `reason`. Thiếu dữ liệu ràng buộc, target chưa biết (request không dùng được) hoặc action ngoài bộ này cũng là UNKNOWN_GT. Enum action và tham số thật thuộc ZER-50.
- **M11 usage/cost:** mỗi `call_id` đếm đúng một lần, retry được tính, redelivery thì không. **Coverage bắt đầu từ các DECISION của tác tử LLM** (fix-01): mỗi DECISION như vậy cần ít nhất một LLM_CALL hợp lệ. Nếu thiếu, hoặc có LLM_CALL/DECISION bị INVALID/quarantine/late, hoặc `call_id` xung đột, thì `call_coverage_status`, `usage_status` và `cost_status` là MISSING ở run và ở trial/incident/tác tử liên quan, `status` là MISSING kèm `reasons`, và tổng chỉ là cận dưới. Bản ghi hỏng không được đếm thành cuộc gọi provider (`raw_call_records` báo riêng). Mỗi bản ghi của một `call_id` xung đột đánh MISSING mọi nhóm mà nó nêu (run/tác tử/model/trial/incident), kể cả model chỉ xuất hiện trong bản ghi xung đột; cuộc gọi vẫn đếm một lần (`conflicting_call_records`) (fix-02). Nhóm không dùng LLM và không có dấu vết LLM là N/A, không phải 0. Giá chỉ lấy từ `cost.usd` và `price_ref` của event, không hardcode giá và không gọi API.
- **M5/M6 (fix-01):** chỉ chạy khi có chỉ định C0 (`benign.trial_ids`), `slot_s` và `episode_gap_s`.
  - **Slot:** slot không có alert mà thiếu coverage của detector là unknown. Alert không xếp được (đồng hồ) hoặc DETECTED bị INVALID trong trial làm mọi slot chưa hit thành unknown. Báo cận [hit/N, (hit+unknown)/N] kèm `slot_verdict`.
  - **Episode:** khóa là (signature, hoặc `rule_id` khi không có signature; service mục tiêu); mỗi khóa nối các firing cách nhau ≤ g_b. Episode/giờ chỉ có giá trị khi coverage khai báo phủ **toàn bộ** W và không có alert không xếp được hoặc INVALID (`episode_verdict` OK). Nếu không, chỉ báo số episode quan sát được, không coi là cận dưới.
  - **M6:** đếm action_id có HEAL_STARTED trong W. Terminal (thiếu, xung đột), tác hại (`M6_harm` UNKNOWN khi có action, vì export chưa ghép bằng chứng ảnh hưởng benign) và coverage log action được báo tách nhau. `M6_verdict` OK chỉ khi log action được khai báo đủ và không có action không xếp được hoặc INVALID.
  - **B0:** M6 là N/A; M5 là N/A khi run không có DETECTED nào (detector tắt), không bao giờ là 0.
  - Không chia cho số lượt tấn công.
- **M12:** CONTAINMENT_VERIFIED trên C2/C5. Request success rate benign, CPU P179 và containment suy từ availability đều **MISSING** có lý do, vì export chưa có dữ liệu đó.

### 4.5 Output (`zd-measurement-score/1`)

Output là thư mục mới (ghi tạm vào thư mục ẩn cùng cấp rồi rename), gồm:
- `score.json`: `schema`, `scorer_version`, `options`, input hash (`export.json` của H/O/other) và `runs[]` (incident, findings, `run_flags`, `mode_findings`, `leak`, `metrics`).
- `incidents.csv`, với cột ổn định: `run_id, group, trial_id, incident_id, flow, effect, label, mttd_s, mttr_s, total_s, reaction_s, u_mttd_ms, u_mttr_ms, u_total_ms, u_reaction_ms, relapses, action_attempts, evaluator_mismatch, flags, missing_reasons`.
- `usage.csv`: `level, key, calls, retries, input_tokens, output_tokens, usage_status, usd, cost_status, price_refs`.

Cùng raw và cùng options thì cho cùng giá trị, chỉ khác `generated_at`. ZER-11 đọc output này, không đọc lại dashboard.

## 5. Điểm giao diện cần chốt

1. **Tên khóa `f01_params`.** Contract §5.3 chỉ liệt kê nội dung. Scorer đọc `delta_s, k, s_s, l_ms, gap_s, eps_s, cap_det_s, cap_rec_s`, khớp các trường đã khóa của RECOVERY_VERIFIED. Harness cần phát đúng các tên này; thiếu hay sai thì `PARAMS_INVALID` và mọi incident MISSING.
2. **MINOR `zd-event/1.1.0`** cho `payload.detail` và các lớp lỗi mở rộng (mục 2.4).
3. **Endpoint đồng hồ tham chiếu và phương pháp sync** (F-01/ZER-38).
4. **Bộ tham số action** `zd-gt-constraints/0` (ZER-50).
5. **Chỉ định C0, `slot_s`, `episode_gap_s`, `ingest_grace`** (ZER-53). Hiện scorer dùng seal làm cutoff. ATTACK_REQUESTED đến muộn vẫn giữ lượt trong N (REQUEST_LATE) cho tới khi chấm lại với version mới.
6. **Nhiều probe cùng một luồng** (OPEN ZER-38): hiện là MISSING, không trộn probe.
7. **MODE_VIOLATION → MISSING** và **lỗ sequence = khoảng trống**: Codex review đã chấp nhận hướng này (codex-review §4).
8. **Ack 202 của H gateway ở chế độ Kafka** (fix-01): sink coi là chưa bền nên gửi lại sau. Nếu probe chạy qua gateway Kafka, cần chốt ack nào là đã giao trước runtime.
9. **Marker giỏ Boutique** (fix-01): `CART_MARKERS` là OBSERVED-SHAPE theo template upstream, phải đối chiếu trên trang pilot. Ràng buộc mặt hàng/số lượng với trang xác nhận đơn chờ bằng chứng giao diện.


## Kiểm chứng bổ sung fix-03 — 20/10/2026

Deadline truyền xuống HTTP có thể là bound động nội bộ: mọi phase connect/TLS/send/read và cleanup phân giải lại mốc stop+grace sớm nhất; workload cancel tức thì và quyền cleanup trong grace là hai việc khác nhau. Không snapshot min(deadline) làm mất stop đến muộn; event chưa nhận ACK bền ở lại outbox. Kiểm session sau mỗi response trước hop kế tiếp, pin session đầu của bướcissue; cleanup luôn dùng credential/target đã đóng băng. M11 gắn incident theo event record để conflict call_id xuyên incident không mất bucket, nhưng call toànrun chỉ tính một.

[Runtime-01](../evidence/ZER-10/runtime-01/README.md) xác minh probe trên Boutique và SQLite file-backed thật. Spec fixture cấu hình trong receipt ghi provenanceOBSERVED; builtin fixture_spec mặc định vẫn là giao diện đề xuất cho ZER-41. Đây không phải hoàn tất vectorSQLi hoặc số KPI formal. Các giới hạn DNS/fsync/hardkill và giá trịpilot được giữ rõ trong runbook.
