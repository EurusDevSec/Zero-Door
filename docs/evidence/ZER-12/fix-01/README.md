# ZER-12 + ZER-40 — Codex sửa gom sau Claude review

**READY_FOR_CLAUDE_RETEST — OFFLINE_PASS.** Chưa phải nghiệm thu, CI từ xa, rollout hoặc Done. Codex xử lý F1–F8/F10; F9 là residual đã ghi rõ vì production AUTO healer chưa bật. [Review gốc](../claude-review.md) giữ nguyên; [source-manifest v1](../source-manifest.json) và [verification v1](../verification.md) là lịch sử trước sửa, không phải checksum source hiện hành. Checker v1 sẽ báo source drift khi chạy trên bản sửa: dùng verify_fix.py của gói này cho revision mới.

Baseline: HEAD c09452ac975ec581bbc2ff1f0fb5ca94f58b5267, branch zer-12-command-guards, staged rỗng. Linear Zero Door đọc lại khi nhận: ZER-12 và ZER-40 In Progress, chưa tích AC. Manifest v1 af4795b8…4039 đã đối chiếu; source/report/receipt gốc có hash và snapshot trước sửa. [delta-manifest.json](delta-manifest.json) khóa source hiện hành, before snapshots và log cuối. Không commit/push/PR/Linear, không lab/Docker/model/secret.

## Finding → sửa → kiểm

| Finding | Thay đổi và bằng chứng | AC |
| --- | --- | --- |
| F1 P1 | Chuyển các ZD_* vào data của ConfigMap được Deployment envFrom tham chiếu. Gate độc lập dựa OpenAPI model kubernetes==28.1.0 kiểm unknown field/type; gate effective env kiểm đúng envFrom/giá trị/mount/readOnly/Secret. Ba manifest cũ bị cả hai validator bắt, ba đối chứng mới đạt; thêm mutant mất envFrom/mount | AC-01/02/03 = ZER-40 |
| F2 P2 | Trigger lưu terminal REFUSED khi chắc chắn chưa gọi send: producer None/setup exception/signing refusal. Retry giữ lỗi cũ; key mới sau pacing được publish. Từ chính lần gọi send, kể cả send ném lỗi hoặc mất ack, giữ UNKNOWN. ASGI quan sát send/model counters; không xóa claim | AC-02 |
| F3 P2 | MAC + strict schema → lookup ledger ID/hash → trả terminal/UNKNOWN; chỉ claim mới mới kiểm expiry/policy và thực thi. Redelivery sau restart/hết hạn/disabled không làm mất kết quả. Forged MAC, ID conflict và lệnh mới hết hạn vẫn bị chặn. Main loop được test qua fake Handle/durable-check/Send/Ack; Ack dùng context mới timeout10s, Send vốn đã dùng context mới timeout10s; lỗi poll/ledger/publish/commit dừng đúng thứ tự | AC-02 |
| F4 P2 | Chặn /attack/llm-plan ở cả B0/BM/B1/B2/B3 trước model/ledger/publish. Đây là áp dụng contract khóa §2 và ZER-8 §4.1, không đổi nghiên cứu hay thêm exploration context. Fault theo kế hoạch khóa vẫn được chấp nhận độc lập treatment | AC-02/03 |
| F5 P2 | Thêm CI matrix Nemesis/Hephaestus, test lock universal constraint bởi toàn bộ production lock từng agent. Checker đối chiếu version thực nạp với mọi package trong image lock; Windows chỉ bỏ uvloop. FastAPI0.111.0/Starlette0.37.2/Pydantic2.7.4/Kafka-python2.0.2, httpx0.27.0 Nemesis và0.28.1 Hephaestus. ASGI/guard/mode/event tests chạy trên cả hai graph, không đổi production pins. Môi trường Gaia cũ vẫn riêng | AC-03 = ZER-40 |
| F6 P3 | Go strict schema đối chiếu exact JSON tag đệ quy tại mọi struct boundary; từ chối Enabled đơn lẻ và alias source/Source, cả nested context/target. Valid control giữ nguyên | AC-02 |
| F7 P3 | Dung sai signer đi trước tối đa2s; TTL≤60s và expiresAt không nới. Test0/1/2s đạt,3s bị chặn, tại expiry bị chặn. Runbook yêu cầu đồng bộ đồng hồ; không đổi clock/KPI contract | AC-02 |
| F8 P3 | Hephaestus chỉ nhận purpose heal-operator với Secret zd-heal-operator, tách token fault purpose operator/Secret zd-command-operator. ASGI cross-role/nhầm mount file bị chặn; đối chứng BM hợp lệ tới R1_EXECUTOR_DISABLED. Không có Secret thật được tạo | AC-03 |
| F9 P3 | Giữ residual rõ ràng: production heal chỉ BM và executor None; AUTO/fallback mới kiểm offline, B0 audit chỉ log. Trước bật AUTO/executor thật phải đi qua ModeGate với gateway evidence và test entrypoint chống bypass. Không giả runtime để khép ZER-11/39 | Mode boundary |
| F10 P3 | Hai job YAML dùng hash lock; thêm worker vào PR image build/smoke; publish cần cả production dependency matrix. Disabled worker chờ shutdown trước signer/ledger/clients thay vì exit/restart loop. Main loop fake test xử lý cùng F3 | AC-03 = ZER-40 |

## Kết quả thực chạy

- Python3.11.9: mỗi production environment đạt guard7 + modes3 + integration12 + CI5 + event_agents4 =31 method. Tổng62 lượt trên hai graph;102 method Python riêng biệt khi tính thêm hồi quy pipeline22/regression42/actor-verifier4/Nemesis-consumer3 (=71 method). Tổng133 lượt thực chạy; không gọi133 là133 test riêng biệt.
- Go1.21.13:22 top-level test đạt (có các subcase), vet và build Linux CGO=0 đạt. Main loop test gồm shutdown/poll error/ledger error/publish error/ack error; real Dispatcher test gồm restart, terminal/UNKNOWN, forged MAC/ID conflict/expiry.
- SAST: Gosec2.19.0 trên Go1.21.13 và Bandit1.7.9 (môi trường tool Python3.12.4 riêng) đạt. Bốn nosec G304 giữ nguyên, theo biên tin cậy được Claude chấp nhận; không tắt rule mới.
- Fail-before:4 Go regression fail do assertion đúng lỗi, valid policy control đạt;2 Python assertion fail đúng hành vi,2 clean control đạt. F4 được phát hiện do B2 thực sự gọi fake model/publish200, không chỉ khác reason text. Manifest cũ3/3 bị OpenAPI và effective-env checker bắt,3/3 bản mới đạt.
- Contract release, source/evidence/dirty boundary và diff-check được kiểm; Bash tools không đổi nên giữ receipt lịch sử v1, không khai chạy lại.

## Replay offline

Trong venv test đúng tests/requirements-command-{nemesis,hephaestus}.lock, Python3.11.9:

~~~bash
python -B docs/evidence/ZER-12/fix-01/verify_fix.py
python -B tests/check_agent_dependencies.py nemesis
python -B tests/check_guard_manifests.py
python -B tests/test_command_guard_integration.py
python -B docs/evidence/ZER-12/fix-01/replay_before.py python
python -B docs/evidence/ZER-12/fix-01/replay_before.py manifest
GOTOOLCHAIN=go1.21.13 python -B docs/evidence/ZER-12/fix-01/replay_before.py go
~~~

Đổi nemesis thành hephaestus khi kiểm environment tương ứng. Go replay dùng overlay để không đổi source; Python replay tạo temp source riêng trong scratch rồi xóa chính temp đó. Before source lưu dạng .txt để không bị index thành code đang dùng. verify_fix.py chỉ kiểm checksum/log, không thay chạy test hay review. Có thể kiểm hiện hành bằng go test ./... và go vet ./... trong chaos-worker.

## Giới hạn và verdict AC

Cả ba AC có implementation và kiểm offline sau sửa, **chờ Claude retest độc lập**, remote CI/image build/smoke và owner acceptance trước Done; ZER-40 dùng cùng AC-03. Không còn finding F1–F5 được biết chưa xử lý trong gói, không tự suy QA cuối đã đạt.

Không chạy Docker/build/pull/container, broker/Kubernetes/model thật, PVC/fsync đĩa lỗi thật, node crash hay mất điện. Go race chưa chạy vì local CGO=0; Linux CI có gate race. OpenAPI model check là kiểm trường/kiểu offline, không full kubeconform/server admission/rollout. Dependency equality không chứng minh image đã chạy. Application tag legacy :latest vẫn là template chưa rollout: phải seal digest từ build đã review/CI khi được phép. Không đóng ZER-11/39/G1.

Ledger sticky state là process-local; lock bỏ lại sau crash vẫn cần operator đối chiếu, không tự xóa/replay. Residual TOCTOU đọc ledger dưới private PVC cùng UID giữ nguyên theo review, không nhận power-loss/exactly-once guarantee. Gói này không mở quyền vận hành hay publication.

GitNexus: refresh đầu thất bại ở worker ready5s; lượt dùng một worker/heap768MiB/DB256MiB/ready30s đã index thành công. Index có14 cảnh báo field xuyên ngôn ngữ không liên kết; không dùng khoảng trống graph làm chứng minh không caller. detect_changes so toàn diff HEAD (gồm implementation v1 và dirty quy ước) báo critical vì đi qua main/guard/executor/Nemesis/heal; phạm vi đó đã đọc source/test, không có tác động lab. Receipt graph cuối giữ trong scratch/zer12/codex-fix01 để việc ghi receipt không tự làm index drift.
