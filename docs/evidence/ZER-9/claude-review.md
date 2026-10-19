# ZER-9 — Claude review độc lập gói cuối

19/10/2026 (+07:00), Claude. Đối tượng: mục “Claude xác nhận ZER-9 — gói cuối 19/10/2026” trong [ghi chú issue](../../delivery/milestones/R1-measurement/event-contract.md), [verification](verification.md), [runbook](../../runbooks/r1-event-pipeline.md), source/test/manifest/verifier trong package manifest và raw [live-11](live-11/). Review chỉ đọc source và chạy kiểm offline. Không chạy lab/Docker/Kube/Kafka/model/API, không sửa product/config/test/contract/evidence của Codex, không commit/push/Linear.

## Kết luận

**NOT_READY.** Có 3 finding P1 chặn AC-02/AC-03. Raw live-11 tự đối chiếu độc lập đạt và toàn bộ test offline của gói đều xanh. Tuy vậy, recorder O dừng hẳn khi gặp một message lỗi. Một số rejection không được lưu vào raw. Phép kiểm rò thì báo rò nhầm trên trace sạch khi dùng nhãn case thật, và bỏ sót `reveal_terms`/`attack_type` ở trường định danh. Các lỗi này sửa được trong code, test và tài liệu, rồi retest offline. Gói sửa không cần chạy lab lại, trừ khi Hoàng muốn có receipt live mới cho phần recorder (xem mục “Gói sửa hợp nhất”). Không pre-approve Done.

## Baseline lúc nhận

- Nhánh `zer-9-event-pipeline`, HEAD `2af4d33bf02c59d7802901d523b1bb2eb39f05a3`, staged rỗng.
- `git status`: 14 file sửa và 9 mục untracked, đúng tập trong gói.
- 26 file nguồn trong [package-manifest](package-manifest.json) khớp SHA-256.
- Tệp bảo vệ khớp: AGENTS, delivery README/WORKFLOW, R1 README, WORKING-AGREEMENT, contract `fe09beb5…`. NOW khớp `now_sha256` `5e6cda5e…`.
- Receipt live-11 khớp `76b757fe…`. [evidence-checksums](evidence-checksums.json) khớp 62/62.
- Lịch sử live-01…10 có verdict đúng như bảng trong verification (06 PASS, còn lại FAIL).
- Ghi chú issue lúc nhận: 64499 byte, SHA-256 `2bfdb5d1…a3726b`.
- AC sống: Claude không có `linear_zero_door`, nên trạng thái sống là UNKNOWN. Review dùng [linear-ac-snapshot](linear-ac-snapshot.json); AC-01…03 trong snapshot khớp bảng của verification.

## Kiểm đã chạy (Git Bash, root)

| Lệnh | Kết quả |
| --- | --- |
| `python -B tests/test_event_pipeline.py` | 22/22 OK |
| `scratch/zer9/venv/Scripts/python.exe -B tests/test_event_agents.py` | 2/2 OK |
| `bash tests/shell/run.sh` | Mọi behavioral check PASS, exit 0 |
| `python -B tests/test_nemesis_consumer.py` | 3/3 OK |
| `python -B docs/evidence/ZER-37/verify_release.py` | 9/9 focused, 3 ví dụ JSON, link PASS |
| `git diff --check` | Sạch |
| `python -I -B scratch/zer9/claude/reconcile_raw.py` | **PASS 58/58**. Chỉ dùng thư viện chuẩn, không import validator hay checker của Codex |
| `python -I -B scratch/zer9/claude/probes.py` | 10/10 phản ví dụ cho kết quả lệch contract/runbook (chi tiết ở dưới) |
| `python -I -B scratch/zer9/claude/probe_label_hex.py` | Trace sạch với `case_class` C4: 119/200 ra LEAK_DETECTED. Với C0: 83/200. Với nhãn không phải hex: 0/200. Số đếm thay đổi theo ID ngẫu nhiên |

`reconcile_raw.py` tự tính lại từ export live-11:
- sha/bytes/dòng của từng file và mã hóa canonical;
- `envelope_sha256` của từng bản ghi;
- định dạng ID/thời gian;
- `seq` đầu/cuối, không có lỗ;
- khoảng ingest;
- chuỗi context → DETECTED → DECISION giữ run/trial/incident/group/config;
- `causation_id` và `inputs`;
- DETECTED gửi lại hai lần có cùng hash nhưng khác ingest/request/offset;
- đúng một DECISION, offset Kafka 0–4 liên tục, H chỉ đi HTTP;
- canary vắng trong O và trong query surface;
- O không có khóa chỉ thuộc H;
- source hash trong receipt khớp file hiện tại.

Cleanup read-back cần cluster nên Claude không tự kiểm. Phần đó chỉ dựa trên receipt của Codex.

## Theo AC

| AC | Verdict của Claude | Căn cứ / còn thiếu |
| --- | --- | --- |
| AC-01 | **PASS (kế thừa)** | ZER-37 Done, contract `fe09beb5…` giữ nguyên. Factory/validator transport khớp các trường bắt buộc và nguồn mà Claude đã kiểm. ZR9-04 làm yếu việc “nguồn ghi riêng” khi rollout |
| AC-02 | **FAIL** (đến khi sửa ZR9-01/02) | Chuỗi ID qua HTTP/Kafka, append/fsync, seal/export/hash đều đạt trên raw thật. Nhưng recorder O chết vĩnh viễn với một message lỗi, seal lúc Kafka còn event chưa ghi, hoặc lỗi binding. Vài loại rejection và event sau seal cũng không để lại dấu trong raw/export. Nếu sửa xong mà không có thêm bằng chứng runtime, AC-02 chỉ là PASS cho transport qua hàm source thật chạy trên máy host (ZR9-05). Hoàng quyết có cần agent chạy trong cluster hay không |
| AC-03 | **FAIL** (đến khi sửa ZR9-03) | Tách H/O về process/UID/PVC/key và gate quyền ba vòng đạt cho pod observer trên node server. Audit lệch §8.3(3): báo rò nhầm trên trace sạch với nhãn C0–C5, và bỏ sót `reveal_terms`/`attack_type` ở target/stream. Đối chứng “cố ý lộ” live chỉ bị bắt bởi INVALID_ID. Prompt LLM/BM chưa tồn tại: N/A/UNKNOWN đúng phạm vi |

## Findings

P1 = chặn nghiệm thu AC. P2 = phải sửa hoặc ghi lại trong cùng gói vì ảnh hưởng tính đúng của AC hoặc claim. P3 = gia cố, tài liệu hoặc thuộc rollout sau.

### ZR9-01 (P1, AC-02) — Recorder Kafka chết vĩnh viễn với lỗi của từng message

- **Vị trí:** [gateway.py:188-220](../../../agent-orchestrator/event_pipeline/gateway.py#L188)
  - `json.loads` không bọc lỗi;
  - danh sách lỗi được nuốt ở dòng 213 thiếu `RUN_SEALED`, `RUN_CONTEXT_MISSING`, `TRIAL_CONTEXT_MISSING`, `LINK_CONFLICT`, `CONTEXT_IMMUTABLE`;
  - `except` ở dòng 217 dừng thread mà không commit.
- **Liên quan:** [gateway.py:39-43](../../../agent-orchestrator/event_pipeline/gateway.py#L39) và `/seal` ở dòng 104-105 không chờ consumer bắt kịp các event đã nhận ACK. Readiness chỉ là TCP ([manifest:64-68](../../../infrastructure/manifests/r1-event-pipeline.yaml#L64)).
- **Phản ví dụ (`probes.py`):**
  - K1: event đã ACK Kafka, `/seal` chạy trước khi recorder ghi → `failure=ValueError`, 0 commit, event không nằm ở file nào, message kế tiếp không được xử lý.
  - K2: một message `\xffnot-json` → `UnicodeDecodeError`, 0 commit, không quarantine.
  - K3: DETECTED hợp lệ nhưng thiếu TRIAL_CONTEXT → thread chết, không quarantine.
- **Tác động:**
  - Broker legacy không xác thực, và namespace `zero-door` không có NetworkPolicy chặn ingress, nên mọi pod trong lab có thể gửi message rác.
  - Offset không commit, nên mỗi lần restart sẽ đọc lại đúng message đó: vòng lỗi vĩnh viễn.
  - Pod vẫn Ready. Mọi POST sau đó nhận 503, và raw của run dừng lại.
  - Seal vào cuối trial là thao tác thường lệ, nên K1 có thể xảy ra trong vận hành bình thường.
- **Cách sửa:**
  - Mọi lỗi của từng message phải đi vào quarantine bền rồi commit offset (xem ZR9-02):
    - JSON không parse được hoặc không phải object → `broker-rejections` kèm `raw_hex`;
    - lỗi binding hoặc RUN_SEALED → quarantine theo run.
  - Chỉ lỗi I/O ghi kho mới được dừng thread.
  - Thread chết thì readiness/liveness phải báo không sẵn sàng, ví dụ đổi sang `httpGet` một endpoint kiểm `bridge.failure`.
  - `/seal` của O chỉ chạy khi không còn event đã ACK mà chưa ghi. Ví dụ: giữ tập `event_id` đã gửi mà chưa ghi, hoặc so offset cuối đã produce với vị trí consumer. Nếu chưa xong thì trả 409.
  - Event đến sau seal được ghi là LATE_INGEST (contract §6.2).
- **Retest:**
  - K1–K3 phải ra: commit tăng, thread còn sống, message kế tiếp được ghi, quarantine có `classification`.
  - Khởi tạo lại bridge sau message rác không lặp lỗi.
  - Seal khi còn event in-flight bị từ chối hoặc phải chờ.
  - 22 test cũ vẫn đạt.

### ZR9-02 (P1, AC-02) — Rejection ngoài `Archive.ingest` bị mất hoặc không vào export

- **Vị trí:**
  - [gateway.py:38](../../../agent-orchestrator/event_pipeline/gateway.py#L38): `binding()` raise trước khi gọi ingest, nên LINK_CONFLICT, TRIAL_CONTEXT_MISSING và CONTEXT_IMMUTABLE chỉ trả 422 mà không lưu.
  - [store.py:129-133](../../../agent-orchestrator/event_pipeline/store.py#L129): event hợp lệ không trùng đến sau seal thì raise RUN_SEALED mà không ghi.
  - [store.py:110-112](../../../agent-orchestrator/event_pipeline/store.py#L110): `canonical()` gặp NaN (do `json.loads` nhận NaN) hoặc `event_id` không hash được thì raise trước khi ghi rejection.
  - [store.py:117-125](../../../agent-orchestrator/event_pipeline/store.py#L117), [160-163](../../../agent-orchestrator/event_pipeline/store.py#L160) và [187-190](../../../agent-orchestrator/event_pipeline/store.py#L187): rejection sau seal nằm ở `rejections.jsonl` gốc, còn `broker-rejections.jsonl` không được seal hay export nào tham chiếu.
- **Phản ví dụ:**
  - H1: DETECTED có `incident_id` khác TRIAL_CONTEXT → `LINK_CONFLICT`, không có file rejection nào.
  - H2: NaN và `event_id` là dict → ValueError/TypeError, thư mục archive rỗng.
  - E1: rejection sau seal chỉ nằm ở file gốc; export chỉ có `O.jsonl` và `manifest.json`, với `rejections: null`.
- **Tác động:**
  - Contract §6.3 yêu cầu LINK_CONFLICT được “cách ly (lưu, không dùng)”, và §6.2 cấm lặng lẽ bỏ LATE_INGEST.
  - Runbook dòng 18 và 140 nói consumer “commit sau quarantine bền” và “INVALID/INTEGRITY_ERROR không được giấu khỏi evaluator”.
  - Evaluator đọc export sẽ không thấy các failure này.
- **Cách sửa:**
  - Mọi rejection đi qua một đường quarantine duy nhất, gọi trước mọi `raise`, bao gồm cả lỗi binding.
  - Envelope không canonical hóa được thì lưu bytes gốc dạng hex kèm classification INVALID.
  - Rejection sau seal có `run_id` hợp lệ ghi vào file riêng của run, ví dụ `late.jsonl`, với hash riêng và nằm ngoài hash của raw đã seal.
  - Export sao chép và kiểm hash cả rejection và late. Nó cũng ghi số dòng và hash của quarantine gốc/broker để evaluator biết có tồn tại.
  - Export kiểm lại hash của `rejections.jsonl`; hiện chỉ kiểm raw.
- **Retest:** H1/H2/E1 phải có bản ghi kèm classification, export chứa và khớp hash các file đó; thêm test HTTP cho từng lỗi binding.

### ZR9-03 (P1, AC-03) — Kiểm nhãn ở trường định danh lệch contract §8.3(3)

- **Vị trí:** [audit.py:299-321](../../../agent-orchestrator/event_pipeline/audit.py#L299)
  - (a) Dòng 313 so chuỗi con trên `canonical(metadata)`. Metadata có các ID hex 32 ký tự, nên nhãn ngắn như C0–C5 hay `v1` khớp ngẫu nhiên.
  - (b) Dòng 301-303 không đọc `attack_type`. Dòng 321 chỉ thêm `reveal_terms` vào `labels` sau vòng quét metadata, nên `reveal_terms` không bao giờ được so với ID/stream/source_instance/target.
  - (c) [verify-event-pipeline.py:364-367](../../../infrastructure/scripts/verify-event-pipeline.py#L364) cố ý lộ bằng cách đặt `incident_id="inc_cpu-stress-case-1"`, và receipt chỉ ghi `findings: ["INVALID_ID"]`. H live không có GROUND_TRUTH_LOCKED, nên đường so nhãn chưa từng chạy trên dữ liệu live.
- **Phản ví dụ:**
  - `probe_label_hex.py`: một DETECTED sạch, GROUND_TRUTH_LOCKED có `case_class=C4` → LEAK_DETECTED 119/200 lần; C0 → 83/200.
  - `probes.py` A1: `target.service=frontend-stress` hoặc `stream=o.cpu-stress` với `reveal_terms=["stress"]` → CLEAN. `attack_type=cpu-hog` trong stream → CLEAN.
- **Tác động:**
  - Áp vào trial thật thì phần lớn trial sạch bị đánh LEAK_DETECTED, mà theo contract trial bị đánh dấu vẫn được chấm và xử lý riêng ở ZER-53.
  - Đồng thời một nhãn lộ qua target/stream lại lọt qua.
  - AC-03 “phép thử kiểm prompt/query không lộ case label” vì vậy chưa có phép thử đáng tin.
- **Cách sửa:**
  - Chuẩn hóa theo §8.3, rồi tách theo dấu nối và so theo **ranh giới token**: chuỗi token của nhãn phải là một dãy token liên tiếp. Phần hex của ID là một token nguyên.
  - Đưa `attack_type` và `reveal_terms` vào tập nhãn trước khi quét metadata.
  - Giữ quy tắc riêng của NEUTRAL/SECRET/OBSERVABLE.
- **Retest offline:**
  - Property test ≥1000 trace sạch với nhãn C0–C5, `v1`, `ab`: phải 0 false positive.
  - `reveal_terms` ở target.service/stream/source_instance → LEAK; `attack_type` ở stream → LEAK.
  - Nhãn GROUND_TRUTH ghép vào stream với ID hợp lệ → LEAK_DETECTED do LABEL_IN_METADATA, không phải do INVALID_ID.
  - Chạy lại audit trên export live-11 kèm H có GROUND_TRUTH_LOCKED synthetic, ghi rõ là tái dựng offline: phải CLEAN.
  - Sửa đối chứng “injected” trong verifier để có một ca chỉ bắt được bằng đường so nhãn. Có thể kiểm bằng unit; không bắt buộc chạy lại live.

### ZR9-04 (P2, AC-01/02) — Một secret O client chứa token của hai nguồn

- **Vị trí:**
  - [verify-event-pipeline.py:179](../../../infrastructure/scripts/verify-event-pipeline.py#L179): `client_keys` gồm detector, decision_rules và reader.
  - [runbook:29-31](../../../docs/runbooks/r1-event-pipeline.md#L29) quy định token O client là đúng tập đó.
  - [client.py:220-225](../../../agent-orchestrator/event_pipeline/client.py#L220) đọc `keys[source]` từ file chung.
- **Tác động:** gateway gắn `source_component` với token ([gateway.py:26-30, 110](../../../agent-orchestrator/event_pipeline/gateway.py#L26)). Khi dùng chung file, Gaia có thể phát DECISION dưới tên `decision_rules`, và Hephaestus có thể phát DETECTED. “Nguồn ghi riêng” của AC-01 khi đó chỉ đúng nếu tin process.
- **Cách sửa:**
  - Mỗi actor có một Secret riêng: Gaia `detector`+`reader`, Hephaestus `decision_rules`+`reader`, operator console riêng.
  - Probe kiểm token của actor khác không có trong file.
  - Cập nhật runbook.
- **Retest:** unit kiểm file key của từng actor; khi rollout thì kiểm mount thật.

### ZR9-05 (P2, claim AC-02/03) — Bằng chứng live chạy agent trên host, không phải trong pod O

- **Vị trí:**
  - [verify-event-pipeline.py:217-220, 289, 321-334](../../../infrastructure/scripts/verify-event-pipeline.py#L217): Gaia/Hephaestus được import vào chính process verifier trên Windows và nối O qua `kubectl port-forward`. Cùng process đó giữ key server O (có `harness`/`evaluator`), key H và context kube quản trị.
  - Gate quyền ở dòng 225-255 chạy trong một pod observer riêng.
  - [manifest:188-198](../../../infrastructure/manifests/r1-event-pipeline.yaml#L188) chỉ cho `role: observer` cùng namespace vào events-o. Gaia/Hephaestus ở namespace `zero-door` theo template này không gọi được gateway.
  - Phần log của telemetry live gọi thẳng proxy ([verifier:298](../../../infrastructure/scripts/verify-event-pipeline.py#L298)), không đi qua client ES của Gaia. Đường `poll_elasticsearch_logs` qua proxy mới chỉ được kiểm URL ([test_event_agents.py:90](../../../tests/test_event_agents.py#L90)).
- **Tác động:** [verification.md:16-17](verification.md) viết “Gaia.publish_alert thật → …” và “Process/UID/PVC/key riêng; O client không H key…” mà không nói hai agent chạy trên host. Bằng chứng cách ly runtime chỉ áp cho pod observer, không cho process đã sinh dữ liệu.
- **Cách sửa:**
  - Ghi rõ trong verification, runbook và handoff.
  - Ghi riêng các điều kiện cho rollout thật: namespace/label policy, secret theo actor, gate trước request đầu tiên của chính actor, kiểm đường ES client của Gaia.
  - Hoàng quyết AC-02/03 có cần agent chạy trong cluster trước Done, hay chấp nhận transport profile và chuyển rollout sang follow-up.
- **Retest:** soát tài liệu; không cần lab.

### ZR9-06 (P2, rủi ro rollout — đánh giá mục 4 của gói) — Ràng buộc node server

Đánh giá nodeSelector server cùng gate ba vòng:
- **Đủ cho profile transport local hiện tại:**
  - recorder H/O và observer cùng nằm trên node có KUBE-POD-FW;
  - ingress events-h được chặn tại node server;
  - nodeSelector làm pod Pending thay vì tự chạy sang node agent.
- **Còn rủi ro P2 cho rollout:**
  - node agent không có enforcement;
  - broker Kafka không có policy, nên mọi pod có thể ghi topic O (gây ra ZR9-01) hoặc đọc topic legacy có lệnh H;
  - lượt 0 của live-11 còn mở Kafka/Prometheus. Actor thật như Gaia gọi telemetry ngay khi khởi động, trước khi có gate riêng của nó.

Đây không phải blocker của profile transport, nhưng là điều kiện bắt buộc trước khi chạy actor thật hoặc mở G1. Việc sửa CNI hay node thuộc hạ tầng hoặc issue rollout, không thuộc gói sửa ZER-9 này. Không suy ra rằng sửa template là đã sửa CNI toàn cluster.

### ZR9-07 (P3, AC-03 gia cố) — Proxy log chuyển nguyên query DSL

[telemetry.py:350-356](../../../agent-orchestrator/event_pipeline/telemetry.py#L350) nhét nguyên `query` của bên gọi vào `bool.must`. Probe T1 cho thấy terms-lookup trỏ tới `any-other-index` đi qua nguyên vẹn. Terms-lookup, `more_like_this` và `percolate` có thể đọc tài liệu ở index khác, cần biết `_id`; `script`, `regexp` và `wildcard` có chi phí không giới hạn. Kiểm namespace của hits không chặn được kênh phụ này. Cách sửa: allowlist mệnh đề (`match`, `term`, `range`, `bool` lồng nhau…), từ chối lookup/script, giới hạn độ sâu. Retest: unit từ chối từng loại.

### ZR9-08 (P3) — Detector gửi lại envelope đã bị từ chối vĩnh viễn

[adapters.py:273-284](../../../agent-orchestrator/event_pipeline/adapters.py#L273): khi publish lỗi, `pending[(service, alert_type)]` được giữ bất kể mã lỗi. Probe D1: sau 422, alert mới mười phút sau, giá trị 0.99 và CRITICAL, gửi lại event cũ với giá trị 0.9; detect mới bị mất và `ts_event` cũ bị dùng lại. Cách sửa: chỉ giữ để gửi lại khi timeout, 5xx hoặc `KAFKA_ACK_WITHOUT_DURABLE_RECEIPT`; với 4xx thì bỏ và ghi log.

### ZR9-09 (P3) — `/experiment/reset` của Hephaestus chưa bị chặn khi bật R1

[hephaestus/main.py:655-680](../../../agent-orchestrator/hephaestus/main.py#L655) trả “replicas reset to 1” dù `apps_v1` là None, tức thông báo thành công giả. Endpoint mutation legacy này vẫn mở. Cách sửa: trả 409 như `/heal/trigger`, kèm test trong `test_event_agents.py`.

### ZR9-10 (P3) — Hiệu năng và vòng sự kiện

- [client.py:250-259](../../../agent-orchestrator/event_pipeline/client.py#L250) dùng `urlopen` đồng bộ, rồi quét toàn bộ run tối đa 10 s, ngay trong vòng `async` của Gaia. Điều này chặn event loop.
- `RulesConsumer.poll` ([adapters.py:292-297](../../../agent-orchestrator/event_pipeline/adapters.py#L292)) đọc cả run mỗi giây.
- `binding` ([gateway.py:51](../../../agent-orchestrator/event_pipeline/gateway.py#L51)) đọc cả run cho mỗi event, nên chi phí tăng O(n²).

Đủ cho kiểm transport, nhưng cần `run_in_executor` hoặc client async, cursor và index trước khi chạy trial thật.

### ZR9-11 (P3) — Một process chỉ gắn với một trial

`ZD_RUN_ID`/`ZD_TRIAL_ID` cố định khi khởi động ([client.py:225](../../../agent-orchestrator/event_pipeline/client.py#L225)), và RulesConsumer lọc theo trial đó ([adapters.py:301](../../../agent-orchestrator/event_pipeline/adapters.py#L301)). Runbook chưa nói phải restart agent mỗi trial, cũng chưa nói về trạng thái cooldown/pending còn sót sang trial sau. Cần ghi vào runbook, hoặc đọc TRIAL_CONTEXT hiện hành.

### ZR9-12 (P3) — Chi tiết độ bền và manifest

- Không fsync thư mục cha sau khi tạo file hay thư mục run ([store.py:98-104, 121-122, 175-178](../../../agent-orchestrator/event_pipeline/store.py#L98)). Giới hạn mất điện đã được khai báo.
- Seal một run chỉ có rejection sẽ gặp FileNotFoundError ([store.py:164](../../../agent-orchestrator/event_pipeline/store.py#L164)).
- Manifest không có số event theo stream, nên SEQ_GAP (§6.2) chỉ thấy được khi đọc raw.
- Ở chế độ không Kafka, binding và ingest không nằm chung một lock ([gateway.py:38-44](../../../agent-orchestrator/event_pipeline/gateway.py#L38)): hai TRIAL_CONTEXT khác nhau gửi đồng thời đều có thể được nhận.

### ZR9-13 (P3, evidence) — Live audit CLEAN dựa trên manifest rỗng

H dòng 2 của live-11 là HARNESS_MANIFEST với `entries: []`. Trong khi đó harness đã tạo namespace `zd-zer9-…`, topic `zd.events.o.…` (O đọc được qua `transport.topic`), pod và PVC. §8.3(4) yêu cầu giá trị harness tạo ra phải được khai trong manifest. Kết quả CLEAN vẫn đúng với manifest đã khai, nhưng độ phủ yếu. Cách sửa: verifier khai các giá trị đó (NEUTRAL hoặc SECRET), và verification ghi rõ giới hạn.

### ZR9-14 (P3, cổng merge) — Image production và CI

- `event_pipeline/Dockerfile` và context mới của Gaia/Hephaestus chưa được build. Live dùng image COPY-only từ Gaia local.
- Hephaestus pin `kafka-python==2.0.2`; event_pipeline/Gaia dùng `kafka-python-ng==2.2.2`. Hephaestus không import gateway nên hiện không lỗi, nhưng cần build thật trên CI.
- `tests/test_event_agents.py` chưa nằm trong CI.

Đã khai báo; đây là cổng CI/merge, không phải lỗi của gói.

## Phần thuộc issue khác (không chặn ZER-9 sau khi sửa)

| Phần | Chủ sở hữu |
| --- | --- |
| Guard/executor, ACTION_COMPLETED/hậu điều kiện | ZER-12/40 |
| Probe/clock/recovery | ZER-38 |
| Scorer, LATE_INGEST cutoff, chấm | ZER-10/53 |
| Prompt LLM thật | R4 |
| Operator console BM | Issue BM/dashboard |
| Enforcement node agent và policy broker | Hạ tầng / rollout |
| G1 | Không đóng ở ZER-9 |

## Gói sửa hợp nhất cho Codex

Codex sửa một lượt, theo một writer:
1. ZR9-01 và ZR9-02:
   - một đường quarantine duy nhất cho HTTP, Kafka và seal;
   - recorder không chết với lỗi của từng message;
   - readiness phản ánh trạng thái bridge;
   - seal không bỏ sót event đã nhận ACK;
   - LATE_INGEST/rejection/quarantine gốc có mặt trong export kèm hash.
2. ZR9-03: so khớp theo ranh giới token, thêm `attack_type`/`reveal_terms`, đối chứng mới, tái dựng audit offline trên live-11.
3. ZR9-04: secret theo actor (verifier, runbook, probe kiểm).
4. ZR9-05 và ZR9-13: sửa wording trong verification, runbook và handoff; manifest khai giá trị harness. Hoàng quyết phạm vi rollout.
5. P3 nên làm cùng lượt vì rẻ: ZR9-08, ZR9-09, ZR9-07. Các P3 còn lại có thể ghi follow-up.

**Retest tối thiểu:** 22 test cũ, cộng test mới cho K1–K3, H1, H2, E1, A1, label-hex, T1, D1 và reset 409. Thêm `reconcile_raw.py` của Claude (không đổi) và `git diff --check`. Live: tự nó không bắt buộc với ZR9-01…05. Nếu Hoàng muốn có receipt runtime cho recorder sau khi sửa (gửi message rác lên topic tạm, rồi seal khi còn event in-flight), cần quyền riêng giống live-11. Khi sửa xong, trả Claude retest phần delta.

## Hash và phạm vi ghi của Claude

| File Claude ghi | SHA-256 |
| --- | --- |
| `scratch/zer9/claude/reconcile_raw.py` | `c91f8d0bc7ff5436bb610db4b00e9c4fd34dd8763d7e98a6bb1c01c491df5202` |
| `scratch/zer9/claude/reconcile-results.json` | `0c7b4a398d8ff7bc8524a3b48ae8a37f681f1ecc5bea886068228c7c3ea13cb2` |
| `scratch/zer9/claude/probes.py` | `bfdb33f6f69658d0d0cf66cf81029559ffc1b06ea2531eb3352913e713655cb9` |
| `scratch/zer9/claude/probe-results.json` | `4b64750a02c5a9adc7b9b63ddbe410838212c18d43c82b64a4c25bb48edda3be` (ID ngẫu nhiên; verdict ổn định) |
| `scratch/zer9/claude/probe_label_hex.py` | `15def0d392a63b8fa071a2872023b5778303a1f1435e008127a2fe38e48b1c1b` |
| `scratch/zer9/claude/probe-label-hex-results.json` | `25d9e970b970c1e43488a0d8a93816306d950dba32b835d8a5fe4913d78b4ecf` (số đếm ngẫu nhiên, >0 với C0/C4) |
| `scratch/zer9/claude/offline-run.txt`, `shell-run.txt` | `c7c13430…0fe0901d`, `6f1e12e9…09f4f2` |

Ngoài các file trên, Claude chỉ ghi báo cáo này, nối bàn giao vào cuối ghi chú issue và thêm con trỏ ở đầu NOW. Hash của báo cáo này nằm trong bàn giao ở ghi chú issue. Không đổi product/config/test/contract/evidence của Codex, manifest baseline hay Linear. **Writer trả Codex.**
