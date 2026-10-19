# ZER-36 / ZER-7 — OpenAI backend probe R0

## Phạm vi và nguồn

Probe độc lập tại `infrastructure/scripts/verify-llm-backend.py`, entrypoint Bash cùng tên `.sh`.
Không import agent, không đọc Prometheus/Kafka/Kubernetes, không thực thi hành động.
Fixture tổng hợp dùng các trường alert ở `agent-orchestrator/gaia/main.py:89` và định nghĩa CPU >80% kéo dài ≥60 s của ZER-32.
Schema `r0_observation_v1` là schema riêng cho smoke test; không khóa event contract R1 hoặc chứng minh năng lực phát hiện trên dữ liệu thật.

Đã đối chiếu AC sống ZER-36/ZER-7 ngày 19/10/2026 qua `linear_zero_door`.
Baseline HEAD `df5d542aaf726e62ea8ccb17a94490cd88322ee0`, branch `zer-5-scope-acceptance`; probe mới chưa commit.
Model được đề xuất: `gpt-6-luna`, Responses API, Standard (`service_tier=default`), reasoning `none`, không tools, `store=false`.
Lưu đúng chuỗi model provider trả; alias không chứng minh revision bất biến. Khi chưa được trả snapshot thì revision bất biến UNKNOWN.

Nguồn người dùng ngày 19/10: Doppler truyền OPENAI_API_KEY; GET /v1/models thành công HTTP 200; model hiển thị 180.000.000 TPM và 30.000 RPM; project đặt 1 USD/tháng và bật hard limit.
Codex chưa đọc dashboard hoặc gọi API trực tiếp. Đây là số người dùng cung cấp; credit/quota không thay cho receipt inference.
Trần tháng của project khác với budget pilot/formal. Hard limit có độ trễ enforcement; không hứa dừng chính xác tại 1,000 USD.

Nguồn OpenAI đã đọc ngày 19/10/2026:

- [Model và giá](https://developers.openai.com/api/docs/models/gpt-6-luna): Standard input 0,10 USD / 1M token; output 0,50 USD / 1M token; context 1.050.000, max output 128.000; probe tự giới hạn thấp hơn.
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs): dùng `text.format`, `json_schema`, `strict=true`; tự kiểm refusal/incomplete và dữ liệu sau nhận.
- [Spend limits](https://developers.openai.com/api/docs/guides/spend-limits): hard limit khác alert; có thể trễ và vượt nhẹ; không thay cho giới hạn attempts/token.

## Cách chạy bằng Git Bash

Chạy từ checkout này. Không thêm key vào tham số, file source, Git hoặc output.

```bash
# Chỉ xem request; không mạng, không cần Doppler/key.
bash infrastructure/scripts/verify-llm-backend.sh

# Kiểm offline, không đọc Doppler hoặc gọi API.
python docs/evidence/ZER-36/test_probe.py

# Lượt thật: Doppler chỉ truyền key cho tiến trình con.
doppler run -- bash infrastructure/scripts/verify-llm-backend.sh --live
```

Lệnh live gửi tối đa 2 attempts (một retry), 512 output token/attempt; request cố định ≤8192 byte, không nhận prompt tùy ý.
`curl` không đọc curlrc, không tự retry hoặc theo redirect; endpoint cố định HTTPS OpenAI.
Mỗi attempt: connect timeout 10 s, curl max-time 30 s, Python chặn tiến trình 35 s; retry cách 1 s.
Không tự nâng model/quota hoặc cài dependency. Cần `python` và `curl` có sẵn trong PATH; Python dùng standard library.

Một retry chỉ cho timeout/network xác định, 429 `rate_limit_exceeded` hoặc 500/502/503/504.
401/403/400, quota/budget/429 không rõ nguyên nhân, refusal, incomplete hoặc schema sai đều dừng; không gửi tiếp chỉ để lấy PASS.
Timeout có thể đã phát sinh token phía provider: receipt giữ usage UNKNOWN cho attempt không có số liệu, không ghi tổng chi phí bằng 0.
Không chạy lặp nhiều lần khi FAIL; gửi receipt để chẩn đoán.

## Receipt và ý nghĩa kết quả

Mỗi lượt live tạo `scratch/zer36/runs/run-<uuid>/receipt.json`, thư mục mới không ghi đè.
Scratch đã gitignore; chỉ chọn evidence để publication sau review. Không tự commit/push/Linear.
Receipt gồm run_id, UTC timestamps, fixture, request/schema, SHA-256 probe/request, từng HTTP status/request ID/header quota khả dụng, model/output/usage và latency.
Key được cấp qua stdin cho curl, không xuất hiện trong argv; dữ liệu được che key và chuỗi `sk-...` trước ghi receipt.
Header chỉ lưu allowlist; không lưu Authorization, Cookie hoặc stderr curl.

- `PASS`, `decision_source=LLM`, `degraded=false`: HTTP 200, completed, đúng model, đúng schema và ca tổng hợp, có usage hợp lệ. Đây là inference thật trên fixture tổng hợp, không là hiệu quả nghiên cứu/lab hay G0 tự động đạt.
- `FAIL`, `decision_source=RULES`, `degraded=true`: fallback cố định theo policy CPU của fixture; không nhận là quyết định LLM, exit 1.
- `OFFLINE_SIMULATED`: chỉ mock, kể cả khi kết quả test giả lập mang nhãn LLM. Không dùng như log inference thật.
- `known_usage_cost_estimate_usd`: ước tính Standard của các attempts có usage hợp lệ, chưa áp giảm cache; không là billing receipt. Xem `cost_estimate_complete` và `unknown_usage_attempts`. Request ID thiếu được liệt kê, không tự chế ID provider.

## Kết quả chuẩn bị

19/10/2026: 8 nhóm test offline đạt, gồm success/caps, timeout exhaustion → RULES, retry transient → success, auth/quota/budget không retry, 13 biến thể HTTP 200 sai không PASS, bảo vệ key/timeout, invalid key không gửi và parser transport/header.
Live inference vẫn PENDING; không pre-check AC-02 hoặc tuyên bố ZER-36/ZER-7 Done từ test này.
AC-03 mới có kiểm lỗi mô phỏng của probe, chưa là lỗi model/lab runtime; cần reviewer đối chiếu mức bằng chứng trước nghiệm thu.

## Cập nhật sau lượt live — 19/10/2026

Lượt inference thật đã PASS; xem [xác minh và đối chiếu AC](verification.md), [receipt thật](live-receipt.json) và [log lỗi mô phỏng](offline-cases.json). Nội dung PENDING ở phần chuẩn bị phía trên là checkpoint trước lượt này. Không gọi API lại chỉ để lặp bằng chứng. Gói chờ review độc lập/nghiệm thu/publication theo quyền; chưa đổi Linear.

## Sau review độc lập

RV36-01 đã bổ sung test cho curl timeout/network, retry ẩn, refusal và HTTP200+transport-error; suite12/12 và14/14 mutant bị bắt. Probe và receipt live giữ nguyên; không gọi API lại. Các P3 giới hạn parser/model/evidence và provenance xem verification.md. Ước tính tối đa0,0005638 USD nếu input giữ259 token/attempt, không phải hard cap tiền. Header remaining/reset không được lưu; phiên bản curl của lượt lịch sử UNKNOWN. Bản gate G0 chờ nghiệm thu/publication ở ../R0/g0-acceptance.md.
