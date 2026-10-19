# ZER-12 + ZER-40 — Claude review độc lập gói Codex 22:33

**Verdict gom: CHANGES_REQUIRED.** Chưa phải nghiệm thu hay Done. 1 finding P1, 4 finding P2, 5 finding P3. Mọi kiểm đều chạy offline: fake transport, executor, Kafka và model. Không sửa product source, test, pin hay receipt. Không commit/push/Linear/lab/Docker/model/secret.

## Baseline đã đối chiếu

- HEAD c09452a, nhánh zer-12-command-guards, staged rỗng. Trạng thái working tree giống bàn giao.
- [source-manifest.json](source-manifest.json): SHA-256 af4795b8…4039 khớp con số trong note. Lúc bắt đầu, `verify_package.py` báo PASS (253 file hash, 99 test Python, 17 test Go, 3 fail-before, control PASS).
- Tôi chạy lại độc lập trên Go 1.21.13. `go test ./...` qua 6/6 package và vet PASS. Python 3.11.9 dùng đúng test lock: guards 7/7, modes 3/3, integration 10/10, ci 4/4, event_agents 4/4. Log ở scratch/zer12/claude-review/{go,py}/independent-*.
- Review này chỉ nối vào note và thêm đầu NOW đúng như quyền được giao. Chạy lại `verify_package.py` sau khi nối vẫn PASS. Staged rỗng.
- AC sống trên Linear: connector Linear của Claude không tìm thấy ZER-12/ZER-40 (khác workspace). Tôi chỉ dựa vào snapshot AC trong note và verification, không tự đọc lại Linear.

## Phản ví dụ tự dựng

| ID | Cách chạy | Kết quả |
| --- | --- | --- |
| CR-GO-1 | `go test -overlay` thêm file test tạm vào internal/guard; không ghi file product | `{"enabled":false,"Enabled":true}` qua StrictJSON và cho ra enabled=true. Payload command có `Source` cạnh `source` cũng được nhận |
| CR-GO-2 | Dispatcher thật với ledger temp và executor đếm. Gửi cùng envelope ở t+1, t+30, t+61 | t+30 trả lại kết quả SUCCESS cũ (đúng). t+61 trả REJECTED AUTH_CONTEXT_OR_EXPIRY với commandId rỗng. Executor 1 lần, không replay |
| CR-GO-3 | Verify với issuedAt sớm hơn đồng hồ worker 1 giây | Bị từ chối, không có dung sai lệch giờ |
| CR-PY-1 | ASGI `/attack/trigger`, fake `get_kafka_producer` trả None, rồi bình thường lại | 503 PRODUCER_UNAVAILABLE và claim NULL vĩnh viễn. Gửi lại cùng key được 409 OUTCOME_UNKNOWN. Key mới được 409 ACTIVE_OR_UNKNOWN_REQUEST. Producer.send = 0 |
| CR-PY-2 | ASGI `/attack/llm-plan` theo từng nhóm, model và Kafka đều fake | B0/BM/B1 nhận 409. B2/B3 nhận 200, fake model được gọi 2 lần, publish 2 lần |
| CR-PY-3 | HEAD và GET `/api/logs` không gửi token | HEAD 405, GET 401. Không có bypass |
| CR-MF-1 | Parse YAML ba manifest | Mọi key `ZD_COMMAND_*`/`ZD_OPERATOR_TOKEN_FILE` nằm trong `metadata` của ServiceAccount/ConfigMap; không key nào nằm trong `data` hay container env |

Mã và log: scratch/zer12/claude-review/go/review_test.go, overlay.json, result.txt; py/review_counterexamples.py, result.txt; manifest-env-placement.txt.

## Findings

| # | P | File:line | Repro: expected / actual | AC ảnh hưởng | Hướng sửa |
| --- | --- | --- | --- | --- | --- |
| F1 | P1 | infrastructure/manifests/chaos-worker.yaml:6-8, nemesis-deployment.yaml:6-9, hephaestus-deployment.yaml:6-7 | CR-MF-1. Expected: container nhận đường dẫn policy/signer/ledger/operator. Actual: key nằm trong `metadata` của ServiceAccount/ConfigMap. Worker gọi `LoadPolicy("")` rồi exit 1; mọi POST và GET có guard của Nemesis/Hephaestus trả 503 POLICY_UNAVAILABLE; apply ở chế độ strict sẽ từ chối field lạ trong metadata. Hệ thống fail closed nên không vượt trần, nhưng đường production có guard không bao giờ khởi động được. `test_command_guard_ci` chỉ kiểm volume nên bỏ lọt | AC-01/02 (wiring triển khai), AC-03 = ZER-40 (gate manifest) | Chuyển key vào `data` của chaos-worker-config / nemesis-config / hephaestus-config, hoặc vào `env` của container. Thêm assert CI: env hiệu lực của Deployment chứa đủ key, metadata chỉ có field chuẩn; render bằng kubeconform hoặc `kubectl --dry-run=client --validate=strict` mà không apply |
| F2 | P2 | agent-orchestrator/nemesis/main.py:484-513 | CR-PY-1. Expected: lỗi đã biết chắc là chưa publish (producer None) phải thành terminal REFUSED, giống llm-plan. Actual: claim NULL, mọi command sau bị chặn cho tới khi operator đối chiếu thủ công dù không có tác động nào | AC-02 (phân biệt known rejection với unknown) | Kiểm producer trước khi claim, hoặc dùng cờ `claimed and not sent`: trước `producer.send` thì complete REFUSED; sau `send` thì để UNKNOWN. Thêm test entrypoint |
| F3 | P2 | chaos-worker/internal/guard/dispatch.go:40-69; cmd/main.go:139 | CR-GO-2. Expected: redelivery của command đã hoàn tất trả lại kết quả trong ledger (hoặc UNKNOWN) có commandId. Actual: sau 60 giây, kiểm expiry chạy trước tra ledger nên trả REJECTED với commandId rỗng; kết quả thật bị mất, rồi ack. `consumer.Ack(ctx)` dùng ctx đã hủy sau SIGTERM, nên mỗi lần dừng có command đang chạy đều chắc chắn dẫn tới redelivery; restart quá 60 giây thì rơi vào ca này | AC-02 (restart/offset/dedup) | Thứ tự: xác thực MAC trước, rồi tra ledger theo commandId+hash (trả previous hoặc DUPLICATE_OUTCOME_UNKNOWN), chỉ áp expiry cho claim mới. Ack và Send bằng context mới có timeout. Tách vòng lặp main qua interface để test Handle→Send→Ack, lỗi ledger và shutdown bằng fake |
| F4 | P2 | agent-orchestrator/nemesis/command_guard.py:230-232 | CR-PY-2. Contract (docs/design/r1-event-contract.md:56, ZER-8 mục 4.1): kịch bản do LLM sinh phải tách khỏi benchmark. Actual: llm-plan bị chặn ở B0/BM/B1 nhưng được phép ở B2/B3, nên nguồn fault khác nhau theo nhóm điều trị. Đây là ghép nhãn treatment vào H, trái 21:05 về tách nguồn fault và mode | AC-03 = ZER-40 (mode policy), AC-02 | Không gate theo B2/B3. Từ chối llm-plan trong mọi run context benchmark, hoặc chỉ cho trong context thăm dò riêng ngoài benchmark. Hoàng/Codex chọn và ghi lại |
| F5 | P2 | tests/requirements-command-guards.lock so với agent-orchestrator/{nemesis,hephaestus}/requirements.lock; .github/workflows/ci.yml:53-65 | Test entrypoint chạy trên fastapi 0.110.0, starlette 0.36.3, pydantic 2.6.4, kafka-python-ng 2.2.2. Image Nemesis/Hephaestus dùng fastapi 0.111.0, starlette 0.37.2, pydantic 2.7.4, kafka-python 2.0.2 (Hephaestus thêm httpx 0.28.1). Smoke image chỉ `import main`. Middleware, body stream và `send().get()` của bản ship chưa được kiểm | AC-03 = ZER-40 (gate chạy đúng đường production) | Chạy guard/integration test theo matrix agent với lock của chính agent đó, hoặc chạy trong image vừa build ở r1-image-build; hoặc thống nhất phiên bản |
| F6 | P3 | chaos-worker/internal/attack/executor.go:85-141 | CR-GO-1. encoding/json khớp tên field không phân biệt hoa thường, nên duplicate khác hoa thường lọt qua và giá trị cuối thắng. Python thì từ chối SCHEMA_FIELDS, nên cùng một file policy được Go và Python đọc khác nhau. Signer và config là nguồn tin cậy nên không khai thác từ xa được, nhưng claim strict schema chưa trọn | AC-02 | Chỉ nhận key khớp đúng tag JSON: đối chiếu tập key với tag, hoặc gom seen theo lowercase. Thêm vector chéo Python–Go |
| F7 | P3 | chaos-worker/internal/guard/auth.go:54 | CR-GO-3. Signer sớm 1 giây là bị từ chối; issuedAt tính bằng giây nên lệch dưới 1 giây cũng gây từ chối ngẫu nhiên. Hệ thống fail closed (chỉ ảnh hưởng availability) | AC-02 | Cho dung sai nhỏ có trần (≤ 2 giây) và test biên; ghi yêu cầu NTP vào runbook |
| F8 | P3 | infrastructure/manifests/nemesis-deployment.yaml:115, hephaestus-deployment.yaml:155; nemesis/command_guard.py:220 | Cùng một Secret và purpose `operator` cho phép cả gửi fault (Nemesis) lẫn gọi `/heal/trigger` (Hephaestus). R1 chưa có tác động vì executor bị tắt và cần record operator_console, nhưng tách quyền fault/heal chưa có ở tầng credential | AC-03 mode (tách fault/heal) | Tách Secret/purpose cho operator heal (ví dụ `heal-operator`), có test cross-role |
| F9 | P3 | agent-orchestrator/hephaestus/command_guard.py:7-48, hephaestus/main.py:531-553 | Nhánh B1/B2/B3 và fallback evidence của ModeGate chỉ được unit test gọi; entrypoint thật chỉ dùng BM. GuardedRules chỉ gate theo nhóm. B0 bị từ chối chỉ ghi log, chưa có kênh audit. R1 chưa có auto-dispatch nên chấp nhận được, nhưng là residual | AC-03 mode | Ghi residual. Khi có decision_llm hoặc executor, dispatcher bắt buộc đi qua ModeGate.admit với fallback_decision thật, kèm test chặn đường vòng |
| F10 | P3 | .github/workflows/ci.yml:20,124; ci.yml publish-images; cmd/main.go:48-50 | `pip install PyYAML==6.0.2` ở bash-tooling và helm-lint chưa có hash. Dockerfile chaos-worker không được build-smoke trên PR (chỉ build khi publish main). Vòng lặp main không có test fake. Worker disabled exit 0 nên Deployment restart liên tục | AC-03 = ZER-40 | Dùng lock có hash cho PyYAML; thêm chaos-worker vào r1-image-build; xử lý cùng F3; có thể cho worker disabled chặn chờ tín hiệu thay vì exit |

## Bốn chú thích Gosec G304

- `LoadKey` và `LoadPolicy` (auth.go:35, policy.go:29): đường dẫn lấy từ env do Deployment đặt, thuộc biên operator tin cậy, không đến từ request hay message. **Chấp nhận.** Lưu ý: vì F1, các env này hiện chưa được giao tới container.
- owner.lock (ledger.go:45): basename cố định với O_CREATE|O_EXCL, không đi theo symlink có sẵn. **Chấp nhận.**
- claims.jsonl (ledger.go:62): Lstat rồi mới OpenFile, không có O_NOFOLLOW, nên còn TOCTOU về lý thuyết. Muốn khai thác phải ghi được vào PVC riêng với cùng UID, tức đã ngoài biên đe dọa. **Chấp nhận như residual.** Hardening tùy chọn: mở bằng O_NOFOLLOW rồi Fstat.
- SAST xanh không phải lý do chấp nhận. Kết luận trên dựa vào biên cấu hình/volume nêu ở từng mục.

## Đã kiểm và không thấy lỗi

- Target exact ở cả Go và Python: scheme, host, port, path; cấm query/fragment/userinfo/encoded; URL dựng sẵn cũng được kiểm; cấm redirect; pod kill chỉ một UID; stress cleanup dùng context mới và UID precondition, cleanup lỗi thành FAILED.
- Budget lấy min(request, command, operator, config); ticker RPS dùng chung; MaxRequests; một dispatcher tuần tự; pacing 6 giây.
- MAC phủ version/key/purpose/expiry/payload bytes; role fault tách khỏi operator.
- Claim fsync trước tác động; unknown không replay; offset commit sau publish.
- Strict JSON Python (duplicate, NaN, depth, size, kiểu).
- B0 không auto-heal; BM chỉ chấp nhận MANUAL từ operator_console được gateway xác thực, cùng run/trial; legacy heal/reset/consumer bị đóng; key model không nằm trong URL hay log.
- Pin action theo SHA, image theo digest, lock có `--require-hashes`, Gosec/Trivy/Go/Python có version. Import path của Dockerfile Nemesis và Hephaestus đúng với `sys.path` (`/nemesis`, `/hephaestus`, `/event_pipeline`).

## Verdict từng AC

| AC | Verdict | Lý do |
| --- | --- | --- |
| ZER-12 AC-01 | CHANGES_REQUIRED | Logic guard target/budget/cancel/UID PASS offline. F1 làm cấu hình guard không tới được runtime |
| ZER-12 AC-02 | CHANGES_REQUIRED | F2 và F3 (known/unknown, restart/expiry/ack); F6 và F7 là phụ |
| ZER-12 AC-03 = ZER-40 AC-01 | CHANGES_REQUIRED | F1 gate manifest bỏ lọt, F4 mode ghép fault theo nhóm, F5 test không chạy trên dependency production; F8–F10 là phụ |

Các ca chưa kiểm được (không tính là PASS): Go `-race` (máy Windows không có CGO), CI từ xa, build/smoke Docker, render bằng kubeconform/kubectl, PVC/fsync thật, runtime và hiệu ứng fault. ZER-11/39 và G1 không thay đổi.

Bước tiếp theo: Codex nhận các finding gom, sửa F1–F5 (và F6–F10 nếu chọn), retest phần bị ảnh hưởng, seal lại manifest, rồi mới bàn QA/publication/nghiệm thu theo quyền. F4 cần Hoàng chốt hướng.
