# ZER-12 + ZER-40 — Claude retest độc lập gói fix-01

**Verdict: RETEST_PASS_OFFLINE — không còn finding chặn (P1/P2).** Còn 4 ghi chú P3 không chặn. Đây không phải nghiệm thu hay Done: vẫn cần CI từ xa (race, build/smoke image), owner acceptance và các bước publication theo quyền riêng.

Phạm vi: retest F1–F10 của [review gốc](claude-review.md) trên bản sửa [fix-01](fix-01/README.md), kèm phản ví dụ mới. Toàn bộ chạy offline: overlay Go, ASGI với fake Kafka/model/Kubernetes, YAML không apply. Không sửa product source, test, pin hay receipt. Không commit, push, ghi Linear, chạy lab/Docker/model hay đọc secret. Code và log nằm ở `scratch/zer12/claude-retest/`.

## Baseline đã đối chiếu

- HEAD c09452ac975ec581bbc2ff1f0fb5ca94f58b5267, nhánh zer-12-command-guards, staged rỗng; `git status --short` có 62 dòng trước và sau retest.
- SHA-256 của `fix-01/delta-manifest.json` là ef2ac4dd…6df5, khớp bàn giao 23:28. `verify_fix.py` PASS với 323 file đã hash. Checker v1 báo drift ở `ci.yml`, đúng như dự kiến vì source đã đổi sau v1.
- Đã đọc diff before→after của các file auth/dispatch/ledger/executor/main.go, Nemesis command_guard/main, Hephaestus main, 3 manifest và ci.yml, cùng các file mới: check_agent_dependencies, check_guard_manifests, review_regression_test, loop_test và runbook.

## Kết quả chạy lại độc lập

| Kiểm | Kết quả |
| --- | --- |
| Go 1.21.13, `GOPROXY=off`, `go test ./...` + `go vet` | 6/6 package OK, 22 top-level test, vet PASS |
| Python 3.11.9 trên production-nemesis: guard/modes/integration/ci/event_agents | 7 / 3 / 12 / 5 / 4, OK |
| Python 3.11.9 trên production-hephaestus: cùng bộ | 7 / 3 / 12 / 5 / 4, OK |
| Hồi quy event_pipeline / regressions / actor_verifier / nemesis_consumer, trên cả hai env | 22 / 42 / 4 / 3, OK |
| `check_agent_dependencies` (nemesis, hephaestus) + `check_guard_manifests` | PASS |
| So lock độc lập (script riêng, không dùng checker của Codex) | Nemesis: 41/41 pin production nằm trong test lock, cùng phiên bản. Hephaestus: 52/52. Phiên bản đã cài khớp, chỉ uvloop bị bỏ qua vì win32. 59/59 pin test lock và lock YAML đều có hash |
| `replay_before.py` manifest / python / go | Bản cũ bị bắt đúng lỗi (3 manifest, 2 Python, Go regression), đối chứng sạch PASS |

## Phản ví dụ mới

| ID | Kịch bản | Kỳ vọng | Thực tế |
| --- | --- | --- | --- |
| CR2-GO-1 | Policy có `"rps":5,"rpſ":100`. Ký tự ſ được encoding/json fold thành s, còn bộ dò key trùng coi đây là hai key khác nhau | Bị từ chối | Bản mới: `SCHEMA_FIELD:rpſ`. **Fail-before trên executor.go cũ: StrictJSON chấp nhận và rps=100.** Escape `"rps"` (đúng tag) vẫn được nhận. Alias lồng `Group`, `ſervice` và key thừa trong context đều bị từ chối |
| CR2-GO-2 | Biên thời gian: TTL 60/61; lead 0/2/3 giây; tại thời điểm hết hạn; iat ≤ 0; exp < iat | Chỉ TTL ≤ 60 và lead ≤ 2 được nhận | Đúng 10/10 ca. Ghi chú: với lead 2 giây, cửa sổ hiệu lực đo theo đồng hồ worker là 62 giây; expiresAt tuyệt đối không bị nới |
| CR2-GO-3 | Lookup trước expiry chỉ đọc: lệnh hợp lệ nhưng policy disabled; sau đó MAC giả cho một ID đã có kết quả | Không tạo claim; MAC giả không đọc được kết quả | Không có claim. MAC giả bị REJECTED với `AUTH_SIGNATURE` và commandId rỗng. Executor chạy 1 lần |
| CR2-GO-4 | Dispatcher và ledger thật trong `consumeCommands`: SIGTERM khi effect đang chạy, sau đó restart và redelivery lúc exp+600 giây | Kết quả bền, Ack trên context còn sống, redelivery trả lại đúng receipt | Exit 0; Send 1 lần; Ack thấy `ctx.Err()=nil`. Redelivery trả về đúng kết quả đã lưu; executor chạy 1 lần |
| CR2-GO-5 | SIGTERM sau Poll nhưng trước admission | Không có effect hay claim | REJECTED `context canceled`, có commandId; Send rồi Ack. Lệnh không được giao lại. Chấp nhận được (xem ghi chú) |
| CR2-GO-6 | Policy disabled khi chạy qua `runWithContext` | Chờ signal, exit 0, không mở ledger | Vẫn chạy sau 400 ms; exit 0 sau cancel; thư mục ledger không được tạo |
| CR2-PY-1 | Chạy lại v1 CR-PY-1 bằng cách lùi thời gian claim trong DB tạm (độc lập với cách patch clock của Codex) | REFUSED là kết quả cuối; ack lỗi vẫn là UNKNOWN | Producer None: 503, retry cùng key vẫn 503 (lỗi đã lưu). Key mới trong cửa sổ pacing: 429; sau pacing: 200. Ack mất: 503 OUTCOME_UNKNOWN; cùng key → 409; key mới → 409 ACTIVE_OR_UNKNOWN. Send = 2. Kết quả giống nhau trên cả hai pin |
| CR2-PY-2 | Send thành công, sau đó `complete(PUBLISHED)` lỗi | Claim vẫn UNKNOWN | Claim NULL; retry → 409 OUTCOME_UNKNOWN. Response đầu tiên lại là 503 `LEDGER_UNAVAILABLE` (xem N2) |
| CR2-PY-3 | Mỗi nhóm B0/BM/B1/B2/B3: gọi llm-plan rồi trigger, mỗi nhóm một ledger riêng | Model luôn đóng; fault theo kế hoạch không phụ thuộc nhóm | llm-plan trả 409 `BENCHMARK_SCENARIO_LLM_DISABLED`, không tạo file ledger; trigger 200 ở cả 5 nhóm. Model gọi 0 lần, send 5 lần |
| CR2-PY-4 | Secret heal-operator dùng lại đúng giá trị token fault-operator | Phân vai không phụ thuộc giá trị secret | Token fault vượt qua auth của Hephaestus và chỉ dừng ở `R1_EXECUTOR_DISABLED` (xem N3) |
| CR2-MF | 6 mutant wiring cho mỗi manifest, chạy qua hai gate (`scratch/.../manifest_mutants.py`) | Gate bắt được lỗi wiring | Lỗi gốc ở metadata bị cả hai gate bắt. Năm mutant khác qua cả hai gate (xem N1). Đánh giá độc lập 3 manifest hiện tại: env, mount và nguồn volume đều đúng |

## Đối chiếu F1–F10

| Finding | Retest | Bằng chứng |
| --- | --- | --- |
| F1 P1 manifest | **ĐÃ SỬA** | Các key ZD_* nằm trong data của ConfigMap cùng namespace, được tham chiếu bằng envFrom không prefix và không bị env ghi đè. Mount đúng nguồn: policy là ConfigMap readOnly; operator/fault là Secret readOnly; ledger là PVC ghi được. Hephaestus dùng `zd-heal-operator`. Lỗi gốc bị cả hai gate bắt |
| F2 P2 known vs unknown | **ĐÃ SỬA** | CR2-PY-1 và CR2-PY-2: ranh giới UNKNOWN nằm ở lời gọi send. Lỗi trước send được lưu thành REFUSED và không chặn key mới sau pacing |
| F3 P2 expiry/Ack | **ĐÃ SỬA** | CR2-GO-3, CR2-GO-4 và test của Codex. Thứ tự là MAC/schema → lookup → expiry/policy → claim. Ack và Send dùng context mới, timeout 10 giây |
| F4 P2 llm-plan | **ĐÃ SỬA** | CR2-PY-3. `generate_attack_plan_from_llm` chỉ còn được gọi từ route đã đóng |
| F5 P2 pins | **ĐÃ SỬA** | So lock độc lập ở bảng trên. CI có job matrix `r1-production-http`, và publish cần job này |
| F6 P3 JSON alias | **ĐÃ SỬA** (lỗ cũ rộng hơn ghi nhận) | CR2-GO-1: không chỉ biến thể hoa/thường, fold Unicode (ſ, K) cũng ghi đè được trường |
| F7 P3 clock | **ĐÃ SỬA** | CR2-GO-2 |
| F8 P3 credential | **ĐÃ SỬA trong code**, còn N3 | Kiểm purpose theo file và dùng Secret riêng. Phân vai vẫn dựa vào việc hai Secret có giá trị khác nhau |
| F9 P3 mode | **RESIDUAL được chấp nhận như đã ghi** | Production healer chỉ có BM và executor None. AUTO/fallback mới chỉ kiểm offline. Không dùng để đóng ZER-11/39/G1 |
| F10 P3 CI/worker | **ĐÃ SỬA** | YAML cài từ lock có hash; build image worker trên PR kèm smoke exit 1 khi thiếu cấu hình; worker disabled chờ signal (CR2-GO-6) |

## Ghi chú P3 không chặn

| # | File / vị trí | Repro: kỳ vọng → thực tế | Ảnh hưởng AC | Hướng sửa |
| --- | --- | --- | --- | --- |
| N1 | `tests/test_command_guard_ci.py:49` (`effective_guard_environment`) và `tests/check_guard_manifests.py` | Mutant `envFrom.prefix`, đổi chéo tên mount↔volume, mount ledger `readOnly: true`, ConfigMap khác namespace, env `valueFrom` ghi đè ZD_*: kỳ vọng gate bắt → thực tế cả hai gate PASS. Mutant policy volume trỏ sang Secret chỉ bị assert bên ngoài gate bắt | AC-03 = ZER-40 (độ bền của gate chống tái phát F1). Runtime vẫn fail closed; manifest hiện tại đúng | Gate từ chối `prefix`; kiểm mount.name → loại và tên nguồn của volume; yêu cầu mount ledger không readOnly; namespace ConfigMap bằng namespace Deployment; từ chối env ZD_* dùng `valueFrom` |
| N2 | `agent-orchestrator/nemesis/main.py` (`trigger_attack`, nhánh `except Refused` khi đã gọi send) | Send OK rồi `complete` lỗi: kỳ vọng response OUTCOME_UNKNOWN → thực tế 503 `LEDGER_UNAVAILABLE`, dù claim vẫn UNKNOWN đúng | AC-02, chỉ ở mức thông điệp; trạng thái đúng và không có replay | Khi `sent=True`, ánh xạ mọi Refused sang 503 OUTCOME_UNKNOWN; ghi log lý do ledger riêng |
| N3 | `docs/runbooks/r1-command-guards.md:23-27`, `CommandGuard.authorize` | Secret heal dùng lại giá trị của fault-operator: kỳ vọng 401 → thực tế qua auth (CR2-PY-4) | AC-03 (credential theo vai); hiện không có effect vì R1 executor disabled | Runbook ghi rõ hai token phải khác giá trị và được sinh độc lập; thêm bước kiểm khi provisioning (so hash, không in giá trị) trước khi bật heal |
| N4 | `infrastructure/manifests/chaos-worker.yaml`, `nemesis-deployment.yaml` | Không khai `strategy`, nên mặc định là RollingUpdate. Pod mới có thể chạy song song pod cũ trên PVC RWO có owner lock: kỳ vọng thay pod tuần tự → thực tế pod mới CrashLoop với `LEDGER_OWNER` cho tới khi pod cũ thoát (đọc code, chưa chạy runtime) | AC-02 (restart). Fail closed | Dùng `strategy: Recreate` như r1-event-pipeline |

Chấp nhận, không coi là lỗi:
- **CR2-GO-5:** lệnh tới đúng lúc shutdown được trả REJECTED và ack, không có claim hay effect. Nếu để giao lại thì lệnh cũng sẽ hết TTL 60 giây và bị REJECTED.
- **Lead 2 giây:** cửa sổ hiệu lực đo theo đồng hồ worker dài tối đa 62 giây.
- **REFUSED đã lưu:** retry cùng Idempotency-Key luôn nhận lại lỗi cũ, kể cả 503. Client phải dùng key mới; hành vi này đã có trong README fix-01.

## Verdict theo AC

| AC | Verdict retest | Còn lại trước Done |
| --- | --- | --- |
| ZER-12 AC-01: target, budget, cancel, UID | **PASS offline** | CI từ xa, `-race`, runtime/effect thật theo quyền riêng |
| ZER-12 AC-02: role, MAC, schema, dedup, restart, offset | **PASS offline**, ghi chú N2 và N4 | CI từ xa, PVC thật, owner acceptance |
| ZER-12 AC-03 = ZER-40 AC-01: pins, CI, mode guard | **PASS offline**, ghi chú N1 và N3 | Job `r1-production-http`, `r1-image-build` (gồm worker) và `go test -race` phải xanh trên CI; owner acceptance |

Issue cha ZER-12 chỉ đóng được khi đủ ba AC; child ZER-40 dùng chung AC-03. Không có gì được đánh dấu Done.

## Chưa kiểm

- `go test -race`: máy này CGO=0.
- CI từ xa, Docker build/pull/smoke, kubeconform, server admission, rollout.
- PVC thật, fsync hay mất điện thật, clock skew thật, nhiều replica.
- Gosec và Bandit chưa chạy lại; tôi dựa vào log fix-01. Không có chú thích G304 mới.
- AC sống trên Linear: connector của Claude trỏ sang workspace khác. Tôi dựa vào read-back của Codex trong README fix-01.
