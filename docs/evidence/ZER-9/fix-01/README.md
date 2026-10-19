# ZER-9 fix-01 — Claude sửa gom sau review

Claude, 19/10/2026, nhánh `zer-9-event-pipeline`, HEAD `2af4d33`, patch chưa commit. Nguồn quyền: [gói sửa gom](../../../delivery/milestones/R1-measurement/event-contract.md) do Hoàng giao sau triage của Codex. Chỉ sửa và kiểm offline; không lab/API/commit/Linear.

**Verdict: READY_FOR_CODEX_RETEST.** Không còn blocker offline. Đây **không** phải READY_FOR_HOANG_ACCEPTANCE hay Done: source sau sửa chưa chạy live, CI chưa chạy, và bằng chứng H/O trên chính actor còn chờ Codex/Hoàng quyết phạm vi.

## Bằng chứng

| File | Nội dung |
| --- | --- |
| [offline-results.txt](offline-results.txt) | Toàn bộ retest: core 22/22, regression 30/30, agent HTTP 4/4, Bash 37 PASS, Nemesis 3/3, ZER-37 release, `reconcile_raw.py`, kiểm verifier/YAML/diff/whitespace; kèm replay probe cũ và đo race |
| [before-after.json](before-after.json) | Cùng 30 regression trên bản source trước sửa: 1 ok, 22 FAIL, 7 ERROR, kèm lý do từng ca. Sau sửa 30/30, ổn định 5/5 lượt |
| [live11-offline-audit.json](live11-offline-audit.json) | OFFLINE_RECONSTRUCTION: O live-11 (không sửa) với audit mới và nhãn C0–C5 synthetic → CLEAN 12/12; đối chứng stream → LABEL_IN_METADATA |
| [runtime-plan.md](runtime-plan.md) | Checklist kiểm trên chính actor (chưa chạy) |
| [delta-manifest.json](delta-manifest.json) | Hash trước/sau từng file; không thay `package-manifest.json`/`evidence-checksums.json` |

Bản source trước sửa (dùng cho before-after) nằm ở `scratch/zer9/claude-fix/baseline-src/`, sao từ build context live-11 và khớp hash 13/13 với `scratch/zer9/codex-review/baseline.json`.

`reconcile_raw.py` (giữ nguyên) ra 57/58. Check duy nhất fail so `source_hashes` của receipt live-11 với file **hiện tại**, nên lệch đúng 7 file fix-01 đã sửa. Check bổ sung cho thấy receipt khớp 10/10 với bản trước sửa; raw/receipt live-11 vẫn hợp lệ cho revision của nó.

`probes.py` không chạy được trên code mới vì dựng `KafkaBridge` bằng `__new__` với thuộc tính nội bộ cũ. Script giữ nguyên; mọi hành vi K1–K3/H1/H2/E1/A1/T1/D1 của nó có assertion trong regression mới. `probe_label_hex.py` chạy nguyên bản: C4/C0/Cx 0/200, `attack_type` trong stream → LEAK_DETECTED.

## Từng finding

Đường dẫn tương đối từ thư mục này; số dòng là của file sau sửa.

| ID | Lỗi | Cách xử lý / giới hạn còn lại | Test / bằng chứng | AC | Còn cần |
| --- | --- | --- | --- | --- | --- |
| ZR9-01 P1 | Recorder chết vĩnh viễn, không commit với message rác, lỗi binding, seal lúc còn in-flight; pod vẫn Ready | [`KafkaBridge.handle/record`](../../../../agent-orchestrator/event_pipeline/gateway.py#L310): lỗi dữ liệu từng message → quarantine bền → commit → message kế. I/O, archive hỏng, lỗi Kafka/commit → dừng, không commit, `/readyz` 503. [`Gateway.seal`](../../../../agent-orchestrator/event_pipeline/gateway.py#L89) dựng hàng rào: chờ submit dở, chờ recorder tới offset đã ack của run, nếu không thì 409 SEAL_PENDING. Readiness chỉ Ready khi đã xử lý các offset có từ lúc khởi động (event đã ack trước crash). Manifest dùng `httpGet /readyz`, `/livez` | `RecorderTests` (poison ×7 rồi restart, binding, I/O, commit error); `SealFenceTests` (in-flight, 40 submit đồng thời + seal, restart, 2 partition) | AC-02 | Codex retest; receipt runtime chỉ khi Hoàng muốn ([plan](runtime-plan.md) bước 1) |
| ZR9-02 P1 | LINK_CONFLICT, thiếu context, sau seal, NaN, ID không hash được, quarantine gốc không lưu hoặc không export | Một đường [`Archive.reject`](../../../../agent-orchestrator/event_pipeline/store.py#L217) cho HTTP/Kafka/sau seal. JSON chặt (UTF-8, object, không NaN/Infinity); không canonical được thì giữ bytes gốc. Chỉ gán run khi đã xác thực. Sau seal → `late.jsonl` (LATE_INGEST/INTEGRITY_ERROR), raw đã seal không đổi. [`export`](../../../../agent-orchestrator/event_pipeline/store.py#L344) giữ khóa, thư mục mới, kiểm hash từng file, ghi `export.json` gồm late và `archive-scope/` (ARCHIVE_GLOBAL_NOT_ATTRIBUTED_TO_RUN) | `QuarantineTests` (binding ×4 qua HTTP, 7 body hỏng, late/duplicate/conflict, run chỉ có rejection, sửa dòng late/rejection bị phát hiện) | AC-02 | Codex retest |
| ZR9-03 P1 | Audit so chuỗi con trên ID hex; thiếu `attack_type`/`reveal_terms`; đối chứng chỉ bắt bằng INVALID_ID | [`label_terms`/`contains`](../../../../agent-orchestrator/event_pipeline/audit.py#L22): gom đủ nhãn trước khi quét, so theo dãy token sau chuẩn hóa mục 8.3, từng trường ID/stream/source_instance/target riêng. NEUTRAL dùng cùng cách so; canary/SECRET/OBSERVABLE giữ nghĩa cũ. Verifier có đối chứng stream/target với ID hợp lệ | `AuditTests` (hex chứa c4/c0/ab; 1000 trace × C0–C5/v1/ab: 0 báo nhầm; 6 vị trí nhãn → chỉ LABEL_IN_METADATA; quy tắc cũ; NEUTRAL; live-11); `VerifierTests`; [tái dựng live-11](live11-offline-audit.json) | AC-03 | Codex retest; live đối chứng theo plan bước 8 |
| ZR9-04 P2 | Một secret client có cả token detector và decision_rules | [`Client.from_env`](../../../../agent-orchestrator/event_pipeline/client.py#L26) yêu cầu đúng {role của actor, reader}. Gateway [`load_keys`](../../../../agent-orchestrator/event_pipeline/gateway.py#L406) từ chối role ngoài plane. Verifier tạo `event-o-gaia`/`-hephaestus`/`-observer`; observer chỉ `reader`. Runbook/template cập nhật | `BoundaryRegressionTests`, `VerifierTests`, agent test file chung bị từ chối | AC-01/02 | Kiểm mount thật khi rollout (plan bước 2) |
| ZR9-05 P2 | Agent live chạy trên host, gate chỉ đo observer | Không đổi receipt. [verification.md](../verification.md), runbook và receipt mới (`agent_execution`) ghi rõ ranh giới. Thêm [runtime plan](runtime-plan.md). Đường ES client thật của Gaia đã kiểm offline qua proxy với upstream giả | `test_actual_gaia_elasticsearch_client_goes_through_gateway_proxy` | Claim AC-02/03 | **Hoàng quyết** có cần kiểm trên chính actor trước Done |
| ZR9-06 P2 | Ràng buộc node server: đủ cho profile, rủi ro rollout | Không sửa CNI/node/broker/policy toàn cluster (ngoài ZER-9). Plan giữ nodeSelector, dừng khi Pending hoặc gate fail, cần policy riêng cho label actor | Tài liệu | Rollout | Hạ tầng/rollout; Hoàng chọn nơi xử lý |
| ZR9-07 P3 | Proxy log chuyển nguyên DSL (terms lookup…) | [`check_query`](../../../../agent-orchestrator/event_pipeline/telemetry.py#L32): allowlist bool/term/terms (giá trị)/match/match_phrase/range/exists/match_all; trường `_*` bị cấm; độ sâu ≤6, ≤32 mệnh đề, ≤8 KB, `size` phải là int | `LogQueryTests` (query Gaia qua, 10 dạng bị chặn trước upstream); agent test ES thật | AC-03 gia cố | — |
| ZR9-08 P3 | Detector gửi lại envelope bị từ chối vĩnh viễn | [`permanent`](../../../../agent-orchestrator/event_pipeline/client.py#L17): 4xx trừ 408/429 là kết luận → bỏ envelope; timeout/5xx/429/ack chưa bền → gửi lại đúng envelope. RulesConsumer không sinh lại DECISION bị từ chối | `RetryTests` | AC-02 | — |
| ZR9-09 P3 | `/experiment/reset` báo thành công giả | [hephaestus/main.py:656](../../../../agent-orchestrator/hephaestus/main.py#L656) trả 409 khi R1 bật, không xóa state hay gọi Kube | AST test + agent test thật | — | — |
| ZR9-10 P3 | Client đồng bộ trong vòng async; quét cả run | Binding nay O(1) nhờ chỉ mục context trong archive. **Còn lại:** `Client.publish` vẫn chặn vòng async của Gaia tối đa ~10 s mỗi alert khi chờ receipt; RulesConsumer và `records()` đọc cả run mỗi lần. Đủ cho transport/budget lab (vài chục event một trial). Trước trial thật cần cursor theo offset và client async/executor | Đánh giá; không rewrite | — | Trước trial thật; Codex/Hoàng chọn issue |
| ZR9-11 P3 | Một process gắn một trial | Runbook: mỗi trial một process mới, dừng process cũ trước TRIAL_CONTEXT kế; cooldown/pending/refused nằm trong RAM | Tài liệu | — | Harness tuân theo khi rollout |
| ZR9-12 P3 | Độ bền và manifest | fsync thư mục cha khi tạo file/run (POSIX; Windows không làm được, đã khai). Seal run chỉ có rejection với raw rỗng. Manifest thêm `stream_seq_counts`, `archive_format: 2`; seal cũ đọc và seal lại không đổi. Binding+append một giao dịch | `test_rejection_only…`, `test_conflicting_contexts…` (có làm chậm binding), `test_live11_raw…` | AC-02 | Mất điện vẫn chưa chứng minh |
| ZR9-13 P3 | HARNESS_MANIFEST live rỗng | Verifier khai namespace/topic/image/nonce/pod/PVC/Secret/header (NEUTRAL). Receipt live-11 giữ nguyên, có đính chính trong verification | `VerifierTests` | AC-03 | Live sau sửa nếu có |
| ZR9-14 P3 | Image production/CI | CI: regression vào job offline; job `r1-agent-http`; job `r1-image-build` build không push + smoke import ở PR. `publish-images` không đổi | YAML parse; **CI chưa chạy, image chưa build** | Cổng merge | CI trên PR |

## AC → test

- **AC-01:** contract không đổi (`contract.py` cùng hash). Nguồn ghi riêng nay có cả file key theo actor: `test_actor_key_files_and_source_binding`, `test_agent_refuses_a_key_file_with_another_actors_role`. PASS offline, kế thừa ZER-37.
- **AC-02:** `RecorderTests`, `SealFenceTests`, `QuarantineTests`, `RetryTests`, agent HTTP 4/4, core 22/22. Blocker offline đã gỡ. Bằng chứng runtime trên source mới: chưa có.
- **AC-03:** `AuditTests`, `LogQueryTests`, `VerifierTests`, tái dựng live-11. Blocker offline đã gỡ. Quyền runtime của actor thật: chưa có (ZR9-05).

## Giới hạn và rủi ro mới

- Hàng rào seal và offset đã ack nằm trong RAM của một process gateway. Template chỉ có `replicas: 1` với `Recreate`; nhiều replica sẽ cần cơ chế khác. Sau crash, readiness bù cho phần ack trước đó.
- Producer đã xác thực có thể tạo thư mục run cho `run_id` hợp lệ bất kỳ khi bị từ chối. Đây là quarantine riêng tư, không đọc được qua O API.
- HMAC của message Kafka nay kiểm trên bytes gốc (producer gửi đúng bytes canonical đã ký); tương thích với cách gateway ký từ trước.
- Readiness/liveness HTTP và job CI mới chưa chạy trên cluster/GitHub.
- Hằng `SEAL_TIMEOUT` 10 s; verifier thử lại `/seal` tối đa 10 lần, mỗi lần cách 1 s.

Không sửa: contract 1.0.0, `contract.py`, Dockerfile, requirements, setup scripts, `tests/shell/run.sh`, tài liệu bảo vệ, review cũ, package manifest/checksums, raw/receipt/history.
