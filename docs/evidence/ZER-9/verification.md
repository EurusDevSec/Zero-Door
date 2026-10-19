# ZER-9 — verification triển khai

## Kết quả mới nhất — runtime actor cuối, 19/10/2026

[Actor runtime](actor-runtime/README.md): PASS10/10; đối chiếu độc lập68/68. Source sau fix-01..03 đã chạy trong production image/pod Gaia và Hephaestus riêng, gate quyền trước trial, query client thật, Kafka poison/good-next/commit/restart/seal/export PVC và cleanup đạt. Core22/regression42/agentHTTP4 đã retest độc lập; verifier mới4/4. Receipt live-11 và các kết luận fix-01..03 dưới đây là lịch sử, giữ nguyên. Chỉ chứng minh transport với alert synthetic; không fault/heal/LLM/KPI hoặc đóng G1. Hoàng đã cho phép hoàn tất commit/PR/Linear sau đủ kiểm; CI/merge còn chờ tại mốc ghi này.

19/10/2026 (+07:00), Codex. Nhánh `zer-9-event-pipeline`, HEAD nền `2af4d33bf02c59d7802901d523b1bb2eb39f05a3`. Patch chưa commit. Nguồn quyền: Hoàng yêu cầu hoàn thiện ZER-9 rồi Claude xác nhận; sau đó duyệt gói namespace/PVC/topic tạm và duyệt riêng rule ES tạm. [Runbook](../../runbooks/r1-event-pipeline.md), [contract khóa](../../design/r1-event-contract.md), [ghi chú issue/gói Claude](../../delivery/milestones/R1-measurement/event-contract.md).

## Trạng thái hiện tại — fix-03 (Claude, 19/10/2026)

**FX02-R1 (lỗi đọc nguồn) đã sửa offline — READY_FOR_CODEX_RETEST. Không phải READY_FOR_HOANG_ACCEPTANCE, chưa Done.**

- [Codex retest fix-02](codex-fix02-review/README.md) trả NOT_READY với một P2: lỗi đọc nguồn ở `records()`/`GET /events` và export (late, quarantine phạm vi archive) không làm archive dừng. Gói [fix-03](fix-03/README.md) chỉ đổi `event_pipeline/store.py`, regression, runbook và file này; hash trước/sau ở [delta manifest](fix-03/delta-manifest.json).
- Mọi đọc phía nguồn archive (stat/lstat, open, read, hash, copy-đọc) đổi lỗi thành ArchiveFailure, và op dưới khóa đặt failure sticky. File tùy chọn vắng là trống; EIO/quyền không bao giờ thành trống. `GET /events` gặp lỗi nguồn trả 503, sau đó readyz 503, request sau 503, không thêm byte, cho H/O ghi trực tiếp và Kafka.
- Lỗi ở thư mục đích export (tạo, ghi, fsync, chmod, bản sao lệch hash) chỉ làm export thất bại; nguồn vẫn Ready. Trước fix-03, bản sao lệch hash ở đích làm dừng nguồn khỏe; nay đã tách.
- Fault injection offline bằng OSError EIO tại open/read/stat; không phải đĩa hỏng thật. Source sau fix-01..03 **chưa chạy live**, CI chưa chạy. Các điều kiện còn mở ở fix-01 vẫn giữ nguyên.

## Trạng thái fix-02 (Claude, 19/10/2026; Codex retest sau đó NOT_READY, xem fix-03)

**FX01/FX02 đã sửa offline — READY_FOR_CODEX_RETEST. Không phải READY_FOR_HOANG_ACCEPTANCE, chưa Done.**

- [Codex retest fix-01](codex-fix01-review/README.md) trả NOT_READY với hai P2. Gói [fix-02](fix-02/README.md) chỉ đổi `event_pipeline/{gateway,store,audit}.py`, regression, runbook và file này; hash trước/sau ở [delta manifest](fix-02/delta-manifest.json).
- FX01: JSON lồng sâu nhưng hợp lệ được chặn bằng kiểm độ sâu lặp (32 tầng) trước validator, là INVALID, lưu bytes/hash vào quarantine trước khi commit; event kế tiếp được ghi, restart không gặp lại.
- FX02: lỗi ghi/fsync/đọc toàn vẹn làm archive dừng hẳn cho H và O: `/readyz` 503, request sau 503, không thêm byte; mở lại từ chối dòng bị cắt. Mô tả phục hồi ở [runbook](../../runbooks/r1-event-pipeline.md). Đây là fault injection offline, không phải thử mất điện hay đĩa hỏng thật.
- Nhánh SECRET sạch của audit không còn ra UNKNOWN nhầm; thiếu bằng chứng vẫn UNKNOWN.
- Receipt live-11 vẫn là bằng chứng của source trước fix-01; source sau fix-01 và fix-02 **chưa chạy live**, CI chưa chạy. Các điều kiện còn mở ở mục fix-01 dưới đây vẫn giữ nguyên.

## Trạng thái fix-01 (Claude, 19/10/2026; Codex retest sau đó NOT_READY, xem fix-02)

**REQUEST_CHANGES đã sửa offline — READY_FOR_CODEX_RETEST. Không phải READY_FOR_HOANG_ACCEPTANCE, chưa Done.**

- [Claude review](claude-review.md) trả NOT_READY (ZR9-01…14). Gói sửa [fix-01](fix-01/README.md) đổi source `event_pipeline/{gateway,store,audit,client,adapters,telemetry}.py`, `hephaestus/main.py`, tests, verifier, manifest, CI và runbook; hash trước/sau ở [delta manifest](fix-01/delta-manifest.json).
- **Receipt live-11 và raw bên dưới là của source trước fix-01.** Chúng vẫn hợp lệ cho revision đó (receipt khớp 10/10 file của bản sao trước sửa). Source sau sửa **chưa chạy live**; mọi bằng chứng của nó là offline ([kết quả](fix-01/offline-results.txt)).
- Đính chính claim của bảng dưới, không sửa receipt:
  - AC-02: Gaia `publish_alert` và Hephaestus `decide_action` chạy trong chính process verifier trên host Windows, nối O qua port-forward. Không có pod Gaia/Hephaestus.
  - AC-03: “process/UID/PVC/key riêng” và cổng quyền ba vòng áp cho recorder H/O và pod observer, không cho process agent. Lượt đó dùng một secret client chung có cả token detector và decision_rules (ZR9-04, nay đã tách).
  - Audit CLEAN của live-11 dựa trên HARNESS_MANIFEST có `entries: []`. Ca “cố ý lộ” chỉ bị bắt bởi INVALID_ID. Audit cũ còn báo nhầm theo chuỗi con hex (ZR9-03). [Tái dựng offline](fix-01/live11-offline-audit.json) bằng audit mới ra CLEAN; đây không phải receipt runtime.
- Còn mở trước nghiệm thu: Codex retest độc lập; bằng chứng runtime trên chính actor theo [kế hoạch](fix-01/runtime-plan.md), hoặc Hoàng quyết phạm vi; CI/merge; Hoàng nghiệm thu.

## Kết luận lượt Codex trước review (source live-11; lịch sử)

**IMPLEMENTED / OFFLINE_VERIFIED / LIVE_PROFILE_VERIFIED — READY_FOR_CLAUDE_REVIEW. Chưa Done.** (Trạng thái lúc đó; xem mục trên.)

[Receipt cuối live-11](live-11/receipt.json) PASS **18/18**, kết thúc15:51:19 +07. Dữ liệu SYNTHETIC kiểm transport qua source Gaia/Hephaestus thật; không phải kết quả fault/detection/healing/KPI. Profile chỉ hỗ trợ actor trên node server đã kiểm enforcement. [Đối chiếu raw độc lập](reconciliation.txt) và [cleanup read-back](cleanup-readback.json) PASS: không còn namespace/PV/rule ES tạm của các lượt này. Không sửa node, firewall hay triển khai thay workload legacy.

AC sống đọc qua linear_zero_door ngày19/10, workspace zero-door/project f6343559-080f-465f-aa7a-eda6074de51f; ZER-9 vẫn In Progress. Chưa đánh dấu checkbox, đổi Linear, publication hoặc merge.

| AC | Thực hiện và bằng chứng | Giới hạn / review còn lại |
| --- | --- | --- |
| AC-01: ID, mốc, nguồn, action tách recovery | Contract zd-event/1.0.0 từ ZER-37 giữ SHAfe09beb590ecc7fd82452e8108215565558e74886765da215954450415fe91fc. Factory/validator transport và tests kiểm source/mode/ID | Contract đã nghiệm thu; không triển khai scorer/recovery/clock normalization trong gói này |
| AC-02: ID HTTP/Kafka, raw bền/export, một chuỗi xuyên thành phần | Gaia.publish_alert thật → HTTP nguồn detector → Kafka O có HMAC → recorder/PVC → Hephaestus.decide_action thật → DECISION. ID/cause/inputs giữ nguyên; redelivery giữ envelope, một decision; restart recorder giữ raw; seal/export khớp hash | Alert payload là fixture có ghi rõ, không là proof Attack→Gaia→Heal. Không dùng nó làm bằng chứng phát hiện fault/KPI. Reviewer đối chiếu đủ phạm vi AC transport theo issue; chưa xác nhận rollout service production |
| AC-03: H/O tách, query/prompt không lộ đáp án | Process/UID/PVC/key riêng; O client không H key/PVC/token Kube; O API dương và H/broker/telemetry trực tiếp âm ba vòng trước data. Query Prom/ES thật lưu trong receipt, có dữ liệu dương; canary không vào O/query. Audit sạch + ca cố ý lộ label bị bắt | Chỉ profile server đã kiểm. Real LLM prompt chưa tồn tại trong adapter R1, không gọi model. Unit kiểm prompt/hash/missing; thiếu audit BM vẫn UNKNOWN; không tuyên bố mọi rollout hay cluster-admin bị cách ly |

## Kiểm offline

- [Core](offline/test-results.txt):22/22. Duplicate/conflict, rejection export, sealed archive, incomplete tail, writer lock, context, source/plane/token/mode, retry nguyên envelope, telemetry allowlist/filter.
- [Source agents](offline/agent-http-results.txt):2/2. Hàm Gaia và consumer-thread Hephaestus thật qua HTTP loopback; chặn Kafka constructor/action trong test, không startup hooks. Kiểm R1 từ chối heal legacy, không init executor và telemetry chỉ qua O proxy.
- [Bash](offline/shell-results.txt): behavioral checks đạt với mock Docker/Kube/Helm/curl; context/Dockerfile đổi nhất quán.
- [Nemesis](offline/nemesis-results.txt):3/3 hồi quy; [contract](offline/contract-regression.txt):9/9 release, JSON/schema/link đạt.
- AST verifier, Bash syntax/--help không lab, YAML13 documents/readiness/nodeSelector, diff --check đạt. Source package/Gaia/Hephaestus/tests giữ đúng hash sau các lượt offline; delta sau đó chỉ verifier, manifest, runbook và evidence/handoff.

Python offline3.12.4 Windows; venv scratch/zer9/venv kế thừa có sẵn, bổ sung kubernetes28.1.0 và elasticsearch8.13.0, không đổi global. Runtime COPY-only từ image Gaia local, base ID và image ID trong receipt, Python3.11. Chưa build ba Dockerfile production mới hoặc chạy GitHub CI.

## Raw cuối và phép đối chiếu

Run `run_bfa1fd0ca6cb4980811b34329d5aa3fe`, B1 transport-only, clock UNKNOWN. [H](live-11/export/H/H.jsonl):2 dòng/2333bytes, SHA272d49f152d45e2f3817d69d9f10c024580287985ac64a39c09f3b0a810a777c. [O](live-11/export/O/O.jsonl):5 dòng/6604bytes, SHAec7d46f1a2809082cf76e029265340e1e7b4a22e06aea5ef9da54d215df54d06. Mỗi plane có manifest seal cùng thư mục.

O gồm RUN_CONTEXT, TRIAL_CONTEXT, DETECTED hai ingest cùng envelope/event_id, DECISION một lần. Không có HEAL_STARTED/ACTION_COMPLETED/RECOVERY_VERIFIED. Raw giữ Kafka topic/partition/offset + HTTP request ID, envelope hash và ingest ID/time. Script đối chiếu độc lập dùng JSON/hash trực tiếp, không import validator: số dòng/bytes/hash, chain/cause/inputs, source hashes hiện tại, không có canary H trong O/query và không có action/recovery. Không chấm KPI từ trial này.

## Các lỗi live đã giữ và cách xử lý

Không bỏ receipt FAIL để lấy PASS cuối; [history](history/) giữ nguyên receipt, export/snapshot và cleanup của từng lượt. Snapshot lỗi được ghi STABLE_FAILURE_SNAPSHOT_NOT_SEALED, không đánh đồng với sealed export.

| Lượt | Kết quả | Điều đã học / xử lý |
| --- | --- | --- |
| 01 | FAIL trước Kube | Bare image digest bị BuildKit hiểu là repository; dùng named local tag từ digest kiểm trước, ghi base ID |
| 02 | FAIL readiness | HTTP chưa nghe dù pod Running; thêm readiness TCP |
| 03 | FAIL ES | Monitoring policy chặn namespace mới; Hoàng duyệt rule mới giới hạn namespace nonce + events-o + TCP9200; không sửa policy cũ |
| 04–05 | FAIL quyền | O pod nối thẳng broker; chờ cố định không đủ; thêm access gate thật trước data |
| 06 | PASS16/16 | Probe nằm node server, recorders ở agent; không đủ suy toàn profile an toàn. Topic vắng được xác nhận bổ sung sau khi namespace dọn |
| 07 | FAIL telemetry | Giữ thất bại; verifier cuối tối đa3 lượt query giống nhau và lưu mọi attempt, không đổi response |
| 08 | FAIL preflight | Metrics API không khả dụng, dừng trước build/deploy; không bỏ guard/reset lab |
| 09 | FAIL40 vòng | Probe agent nối H/Kafka/Prom qua cả40 vòng; không chỉ startup race. Snapshot agent có0 chain KUBE-POD-FW, server20. Khóa profile/nodeSelector vào server và kiểm placement |
| 10 | FAIL đường dương | O API chưa sẵn sàng khi policy đang cập nhật; cho cả đường dương và âm vào cùng gate hữu hạn, không nhận data trước đạt |
| 11 | PASS18/18 | Toàn bộ profile/probe trên server; ba vòng quyền đạt trước data; query lần đầu đạt, restart/hash/audit và cleanup topic đã xác nhận |

[Snapshot firewall](diagnostics/) là quan sát tại thời điểm kiểm, không là bản sửa CNI hay chứng minh nguyên nhân nội bộ k3s. Gate cuối còn lưu attempt0 chưa sẵn sàng, rồi attempt1–3 đạt; không che cửa sổ trước gate. R1 actor thật phải giữ placement, không đưa H credential vào O ngay khi pod sinh, và chạy kiểm quyền trước trial. Không tự chuyển actor sang agent khi server thiếu chỗ.

Cleanup topic dừng recorder subscriber trước, đợi pod vắng, dùng pod admin tạm không mount raw/key để xóa đúng topic và xác nhận vắng; tránh Kafka auto-create lại. Xác minh namespace UID/nonce và rule ES UID/nonce trước xóa. Các lượt lỗi export ổn định/hash trước cleanup; receiptFAIL được giữ. Final read-back không còn namespace/PV/policy thuộc các lượt1–11. Image cache local giữ cho review, không có workload tạm đang chạy. Không động deployment/PVC/topic cũ, không attack/heal/reset/LLM/cloud hoặc chi phí API.

## Điều kiện còn lại

Claude review cả gói + consumer trực tiếp, gom findings để Codex sửa/retest một lượt. Hoàng nghiệm thu, commit/PR/CI/merge và chia sẻ evidence theo quyền riêng trước Done. G1 chưa đóng. Không dùng dataset legacy/Nemesis dashboard hay alert fixture này làm thực nghiệm chính. Transport validator không thay toàn bộ causal/clock/coverage/scorer; BM thiếu audit/LLM prompt thiếu thì UNKNOWN. File readonly không là WORM/power-loss proof. Việc sửa enforcement node agent và rollout các actor thật chưa được thực hiện bởi gói này.
