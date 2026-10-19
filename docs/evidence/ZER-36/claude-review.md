# Claude review độc lập — ZER-36/ZER-7, delta ZER-8 và đối chiếu G0

[Gói giao và bàn giao](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/llm-backend.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md) · Issue: [ZER-36](https://linear.app/zero-door/issue/ZER-36/chon-backend-llm-va-gioi-han-su-dung), [ZER-7](https://linear.app/zero-door/issue/ZER-7/xac-nhan-mot-backend-llm-that), [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung)

**Người review:** Claude, 19/10/2026, 11:28–11:40 +07:00. Đây là review-only. Claude không viết probe, test hay receipt được review. Kết luận ở đây là kết luận kỹ thuật của reviewer; Hoàng chưa nghiệm thu, chưa publication.

## 1. Baseline, quyền và nguồn

- Git Bash lúc 11:28:41 +07:00: nhánh `zer-5-scope-acceptance`, HEAD `df5d542aaf726e62ea8ccb17a94490cd88322ee0`, staged rỗng. Dirty và untracked đúng như gói ghi.
- Tám file trong bảng hash của gói khớp từng byte lúc nhận (bảng ở mục 7). Snapshot lưu tại `scratch/zer36/claude/hash-before.sha`, bản sao NOW và ghi chú ở `scratch/zer36/claude/base/`.
- **AC sống: UNKNOWN với Claude.** Phiên này không có `linear_zero_door`; gói cấm connector thay thế. Review dùng snapshot AC trong gói (llm-backend.md mục “Snapshot AC và quyết định thật”) và các lần Codex đọc AC sống ghi trong [verification](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/verification.md). Trạng thái Linear trong báo cáo này là snapshot, không phải đọc mới.
- Không gọi API, không đọc Doppler hay secret, không chạy Docker/kubectl/lab, không commit/push/merge, không ghi Linear. Có một lượt đọc trang tài liệu công khai của OpenAI (mục 2.3) và một lượt `git ls-remote` chỉ đọc (mục 5).
- Ghi file: báo cáo này; nối bàn giao cuối llm-backend.md; con trỏ đầu NOW; scratch `scratch/zer36/claude/` (gitignored). Không sửa probe, test, README, verification, receipt, ZER-8 hay nguồn khác.

## 2. ZER-36/ZER-7 — kiểm chứng độc lập

### 2.1 Trace probe

Đường chạy: `verify-llm-backend.sh` chỉ `exec python` với nguyên tham số; không có mặc định ẩn. Python → `run_probe` → `curl_transport` → `validate_response` → nhãn/fallback → `clean` → receipt → exit code.

| Điểm soát | Kết quả đọc mã và kiểm |
| --- | --- |
| Trần attempts | `MAX_ATTEMPTS = 2` là vòng lặp duy nhất; curl `--retry 0`, không `-L`. Không có retry ẩn ở revision này. Test chưa ghim `--retry 0` (RV36-01) |
| Timeout transport | curl `--connect-timeout 10 --max-time 30`; Python `timeout=35` và giết tiến trình con. Trường hợp xấu nhất khoảng 2 × 35 + 1 s |
| Không retry auth/quota | Chỉ retry `curl_exit_28/6/7`, `process_timeout`, 500/502/503/504, và 429 có `code == rate_limit_exceeded`. 401/403/400, 429 không mã và năm mã quota/budget đều dừng. Đúng |
| HTTP 200 không phải PASS | Chỉ PASS khi `status == completed`, model khớp, không refusal, JSON đủ key, đúng enum/kỳ vọng tổng hợp và usage hợp lệ. Lỗi validate thì dừng, không retry, nhãn RULES |
| Thiếu usage | Attempt không có usage hợp lệ vào `unknown_usage_attempts`; `cost_estimate_complete=false`. Tổng không bị ghi thành chi phí đầy đủ |
| Secret | Key đi qua stdin config của curl, không nằm trong argv; `--disable` là tham số đầu nên không đọc curlrc. Header lưu theo allowlist, stderr bị bỏ. `clean` thay key và chuỗi `sk-…` trước khi ghi. Grep `sk-…`/`Bearer` trên evidence và scratch zer36: chỉ thấy khóa giả trong test |
| Đường dẫn và ghi đè | Receipt ở `scratch/zer36/runs/run-<uuid>/`, `exist_ok=False`; file tạm trong `TemporaryDirectory`, endpoint cố định `https://api.openai.com/v1/responses`, `--proto =https` |
| Fallback | Luôn `decision_source=RULES`, `degraded=true`, `verdict=FAIL`, exit 1. Quyết định fallback là hằng số theo policy fixture, không phải bộ quy tắc runtime; đủ cho mục đích ghi nhãn của R0 |

### 2.2 Receipt thật

Kiểm lại trực tiếp [live-receipt.json](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/live-receipt.json), không dựa vào dòng PASS của tác giả:

- Trùng từng byte với `scratch/zer36/runs/run-47adfcce-8427-4c40-884e-b103da4e73a0/receipt.json`. Thư mục `runs/` chỉ có một lượt live này.
- `request` trùng `REQUEST` của probe hiện tại. Tính lại `request_sha256` 4699e6d4… và `probe_sha256` 37de4d63… đều khớp. JSON trong `input` trùng FIXTURE.
- `validate_response(body)` chạy lại trên body thật cho đúng `decision` đã ghi.
- Một attempt, HTTP 200, `completed`, model trả `gpt-6-luna`, `x-request-id` req_5041abe6…, response `resp_0754202c…`. `tools: []`, `store: false`, `service_tier: default`, reasoning `none`.
- Usage 259 + 68 = 327; cached 0, cache write 0, reasoning 0. Ước tính (259 × 0,10 + 68 × 0,50) / 10⁶ = 0,0000599 USD, khớp.
- Thời điểm nhất quán: `started_at` 04:20:38.966Z, `created_at` của provider 04:20:39Z, `completed_at` 04:20:40Z, `finished_at` 04:20:41.942Z.
- Header `x-ratelimit-limit-requests=30000`, `x-ratelimit-limit-tokens=180000000`. Đây là giới hạn tốc độ, không phải quota còn lại hay số dư.
- Ghi chú đo: `latency_ms` và `elapsed_ms` cùng là 2969.0, attempt timestamp trùng `finished_at` đến micro giây. Lý do: trên máy này `time.monotonic()` dùng GetTickCount64 và `time.time()` dùng GetSystemTimeAsFileTime, độ phân giải 15,625 ms (`time.get_clock_info`). Ba chữ số thập phân trong receipt không có nghĩa là chính xác tới micro giây. Không ảnh hưởng AC-02; ảnh hưởng thiết kế đo MTTD ở R1 (RV36-05).

### 2.3 Nguồn giá và giới hạn model

Đọc lại trang [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) lúc khoảng 11:31 +07:00, nguồn OpenAI chính thức:
- input 0,10 USD, cached input 0,01 USD, output 0,50 USD trên 1 triệu token; khớp hằng số probe;
- context 1.050.000 token, max output 128.000;
- giới hạn mặc định tier Grow 30.000 RPM / 180.000.000 TPM, khớp header receipt; trang không nói project này đang ở tier nào;
- snapshot chỉ liệt kê `gpt-6-luna` là snapshot mặc định. Vì vậy revision bất biến UNKNOWN là khai báo đúng.

Trần chi phí xấu nhất mỗi lượt chạy probe, với input 259 token mỗi attempt: 2 × (259 × 0,10 + 512 × 0,50) / 10⁶ ≈ 0,00056 USD. Verification chưa ghi con số này (RV36-05).

### 2.4 Bộ test offline và boundary

- `python docs/evidence/ZER-36/test_probe.py`: 8/8 OK. `bash -n` entrypoint: OK. Hai file JSON evidence parse được. Không có CR hay khoảng trắng cuối dòng trong các file của gói.
- **Mutation** (`scratch/zer36/claude/mutants.py`): chạy suite gốc không sửa trên 14 bản probe bị sửa một chỗ, kèm đối chứng sạch. Đối chứng sạch đạt; 7 mutant bị bắt, **7 sống sót**. Kết quả ở `mutants.out`.

| Mutant | Suite | Ý nghĩa |
| --- | --- | --- |
| Không retry `curl_exit_28` (timeout thật của curl) | Sống | Đường timeout thực tế không được test (RV36-01) |
| Không retry `curl_exit_6/7` (DNS/kết nối) | Sống | Như trên |
| `--retry 0` → `--retry 3` | Sống | Retry ẩn có thể phá trần 2 attempts mà test không biết (RV36-01) |
| Bỏ `--proto =https` | Sống | Hardening không được ghim |
| Bỏ kiểm refusal | Sống | Test refusal vẫn FAIL nhưng vì JSON rỗng, không vì refusal |
| Bỏ kiểm classification kỳ vọng | Sống | `NORMAL` đủ evidence không có test |
| Chấp nhận HTTP 200 kèm lỗi transport | Sống | Ca 200 + `curl_exit_28` không có test |
| `process_timeout`, MAX_ATTEMPTS 3, retry mọi 429, bỏ status, fallback nhãn LLM, cost luôn đủ, bỏ trần output | Bị bắt | Các ràng buộc cốt lõi của AC-03 có test |

- **Boundary** (`scratch/zer36/claude/boundary.py`, transport giả): hành vi ở revision hiện tại đúng với `curl_exit_28` hai lần (2 attempts, RULES, chi phí chưa đủ), 429 rate limit hai lần, 500 mang `insufficient_quota`, NaN confidence và `NORMAL`. Phát hiện ba điểm yếu nhỏ: output item không phải object làm crash (RV36-02), model `gpt-6-luna-mini` được chấp nhận theo tiền tố (RV36-03), evidence ID trùng lặp được chấp nhận (RV36-04). Lỗi 401 có thể trả lại bốn ký tự cuối của key sau `clean`; OpenAI vốn hiển thị phần này, không coi là lộ secret.

### 2.5 Mức bằng chứng AC-03

Fault injection ở tầng transport là đúng mức cho **probe R0 độc lập**. Không cần provider outage thật hay adapter R4. Với revision 37de4d63, hành vi timeout, retry giới hạn, không retry auth/quota và fallback RULES không mang nhãn LLM đều đã được tôi kiểm độc lập ở mục 2.4.

Tuy nhiên bằng chứng trong repo chưa đủ. [offline-cases.json](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/offline-cases.json) và test chỉ dùng `process_timeout` (Python giết curl ở 35 s). Đường thực tế là curl tự dừng ở 30 s với exit 28, và đường này sống sót mutation. Sửa chỉ cần thêm test, không đổi probe, nên receipt live vẫn khớp revision probe.

## 3. ZER-8 — delta mục 11–13 và tính nhất quán

Phạm vi: chỉ delta quyết định. Không mở lại RV8-01…05, B3/M1/B2 đã được chấp nhận hay 45 test cũ. Artifact SHA-256 452493ab…4aefc khớp bảng gói. Bản bb27ff88 và 43715562 không còn lưu nguyên byte trong scratch, nên tôi không tái lập được diff giữa các bản receipt; nội dung mục 12–13 và các ô đã cập nhật được đọc trực tiếp.

- **Khớp:** mục 13 tách đúng ba thứ: hard limit 1 USD của project kiểm backend, trần pilot 5 USD đã duyệt về kế hoạch, và 300 USD là nguồn người dùng. Mục 13 không tự tăng hard limit, không dự báo đủ mẫu, giữ formal cho ZER-53, giữ B3 có điều kiện tại ZER-22. Quy tắc dừng khi hết trần và không cắt case rồi gọi pilot là đủ khớp mục 3.2/5.4.
- **Với giá đã kiểm ở mục 2.3,** ví dụ ILLUSTRATIVE ở mục 4.4 cho chi phí tối đa B3 pilot khoảng 0,648 × 0,10 + 0,054 × 0,50 ≈ 0,09 USD, B2 tương tự. Nên trần API 5 USD rộng; ràng buộc thật là 8 giờ lab (RV8-08).
- Findings: RV8-06, RV8-07, RV8-08 ở mục 4.

## 4. Findings

### 4.1 Cần sửa trước nghiệm thu (P2)

| ID | Vị trí | Bằng chứng / phản ví dụ | Ảnh hưởng | Sửa đề xuất | Retest |
| --- | --- | --- | --- | --- | --- |
| RV36-01 | [test_probe.py:49-56](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/test_probe.py), [:105-116](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/test_probe.py); offline-cases `timeout_exhausted` | Mutant bỏ retry `curl_exit_28` hoặc `6/7`, và mutant `--retry 3`, đều qua 8/8 test (mục 2.4). Test và log lỗi chỉ dùng `process_timeout` | AC-03 nêu timeout/retry giới hạn; bằng chứng hồi quy trong repo không bảo vệ đường timeout thực tế hay trần retry của curl. Probe hiện tại đúng, nhưng một sửa sau có thể phá mà không test nào báo | Thêm subTest cho `curl_exit_28`, `curl_exit_6`, `curl_exit_7` vào test timeout. Ghim cặp `--retry 0` và `--proto =https` trong argv. Nên thêm ca 200 + `curl_exit_28`, refusal kèm `output_text` hợp lệ, `NORMAL` đủ evidence. Có thể ghi thêm ca `curl_exit_28` vào log lỗi, giữ nhãn OFFLINE_SIMULATED. Không sửa probe | `python docs/evidence/ZER-36/test_probe.py`; `python -I -B scratch/zer36/claude/mutants.py` phải cho mọi mutant ở bảng mục 2.4 KILLED trừ đối chứng; probe SHA vẫn 37de4d63… |
| RV8-06 | [research-design.md:216](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md) với [:526](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md) | Mục 5.1: harness ghi ground truth, gồm seed onset jitter và lệnh fault, “sau khi Hoàng và Hòa rà”. Mục 13: Hoàng chạy BM, harness giấu thứ tự/onset. Nếu Hoàng rà bản ghi từng trial trước khi chạy, việc che lịch mất tác dụng | Đây đúng ranh giới nhãn/evidence mà G0 yêu cầu khóa. Không phải lỗi phương pháp mới, chỉ là hai câu đã chốt mâu thuẫn nhau | Một đoạn làm rõ: Hoàng/Hòa rà nhãn và tập A **theo variant**; thứ tự, seed và onset từng trial sinh sau khi rà, niêm phong ở mặt H, không hiện cho người chạy BM tới hết trial; nếu cần rà mức trial thì Hòa làm hoặc rà sau run. Sửa luôn ô BM ở mục 5.7 trỏ tới quyết định mục 13 | Đọc lại 5.1, 5.7, 13; ZER-9 thêm cờ “operator đã thấy lịch” vào phép thử rò |

### 4.2 Không chặn (P3)

| ID | Vị trí | Nội dung | Đề xuất |
| --- | --- | --- | --- |
| RV36-02 | [verify-llm-backend.py:75-80](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/verify-llm-backend.py), [:175](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/verify-llm-backend.py) | Output item không phải object gây `AttributeError` không được bắt. Probe crash sau một call trả phí và không ghi receipt. Không thể thành PASS; API thật trả object nên khó xảy ra | Đưa vào adapter R4 (bắt lỗi kiểu, ghi receipt trong `finally`). Không sửa probe R0 lúc này: đổi probe làm receipt live 37de4d63 lệch revision cuối, phải chạy live lại |
| RV36-03 | [verify-llm-backend.py:72](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/verify-llm-backend.py) | `startswith("gpt-6-luna-")` chấp nhận cả tên model khác họ như `gpt-6-luna-mini`. Receipt thật trả đúng `gpt-6-luna` | R4 dùng danh sách snapshot cho phép hoặc regex ngày |
| RV36-04 | [verify-llm-backend.py:96](R:/_Projects/Eurus_Workspace/zero_door/infrastructure/scripts/verify-llm-backend.py) | Evidence ID trùng lặp được chấp nhận vì so bằng `set` | Không ảnh hưởng receipt; ghi cho schema R1/R4 |
| RV36-05 | [verification.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/verification.md), [README.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-36/README.md) | (a) Chưa ghi trần chi phí xấu nhất mỗi lượt ≈ 0,00056 USD cho AC-01 “cost mỗi run”. (b) Header remaining/reset bị allowlist bỏ, không phải provider không trả; cần phân biệt khi khai báo trường thiếu. (c) Receipt không ghi đường dẫn và phiên bản curl/Python. Máy có hai curl (Git 8.9.0 và System32 8.21.0); CreateProcess thường chọn System32. (d) Độ phân giải đồng hồ 15,625 ms | Thêm vài dòng vào verification. Mục (d) chuyển cho ZER-9/ZER-37: dùng `perf_counter`/`time_ns` và ghi nguồn đồng hồ khi đo MTTD |
| RV8-07 | [research-design.md:47](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md), [:352](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md), [:465-467](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md) | Bảng kết luận mục 0 đã cập nhật ô AC-02 nhưng ô AC-01 vẫn “chờ Hoàng chấp nhận metric chính”, dù mục 12 đã chấp nhận. Ô BM ở 5.7 vẫn “Cần Hoàng chọn”. Mục 9 vẫn ghi trần 1 USD “chưa duyệt”. Dòng 12 có ghi nhãn trước mục 12 là lịch sử, nhưng bảng mục 0 là kết luận hiện hành | Sửa ô AC-01 mục 0 và ô BM 5.7 trỏ mục 12/13; mục 9 thêm một câu trỏ mục 13 |
| RV8-08 | [research-design.md:525](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md), [:529](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-8/research-design.md) | Với giả định ILLUSTRATIVE mục 4.4 (1.050 s mỗi trial), chỉ một lượt qua 5 nhóm × 6 lớp đã cần 30 trial ≈ 8,75 giờ, vượt trần 8 giờ; r = 3 cần khoảng 26 giờ. Kèm quy tắc không cắt case rồi gọi đủ, pilot vòng đầu gần như chắc chạm trần giữa ma trận, và ZER-22 có thể thiếu số đo B3. Ngoài ra trần 5 USD lớn hơn hard limit 1 USD/tháng của project | Không phải lỗi quyết định; Hoàng đã ghi trần không dự báo đủ. Khi soạn ZER-51, khai báo trước tập cell của vòng đầu (đo thời gian trial trên vài cell mỗi nhóm, có B3) và gọi đó là pilot từng phần. Ghi rõ điều kiện trước pilot: Hoàng nâng hard limit hoặc tách project, không tự nâng |
| G0-01 | Ghi chú repo | `git ls-remote` lúc 11:33 +07:00: `main` = ab800056 “Merge pull request #20 … zer-5-scope-acceptance”. Cây của ab80005 trùng df5d542 (diff rỗng), nên main đã chứa tài liệu ZER-32/33/34/6/5. Repo chưa ghi sự kiện PR #20 này; receipt ZER-5 ghi “không tạo PR hay merge” ở thời điểm 08:21 | Ghi trong receipt G0. Tôi không thấy ai merge hay lúc nào, chỉ thấy reflog fetch cục bộ |

Không biến giới hạn đã khai báo thành lỗi: fixture tổng hợp, revision model UNKNOWN, hard limit chưa đọc dashboard, lab hiện tại UNKNOWN, AC-03 là fault injection.

## 5. Bảng G0

Gate: “Lab có giao dịch kiểm chứng được, một backend LLM trả kết quả thật; phạm vi, RQ, đối chứng và ranh giới nhãn/evidence được khóa.” ([R0 README](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md))

| Vế gate | Nguồn / revision | Bằng chứng | Giới hạn | Verdict kỹ thuật |
| --- | --- | --- | --- | --- |
| Lab có giao dịch kiểm chứng được | ZER-6/ZER-34 Done (snapshot); [ZER-34 review mục 9](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-34/claude-review.md) d7e75847…; mã lab PR #19 merge 5471b58; tài liệu ở 968cc50, nay trong main ab80005 | Raw verify-final 18/10 18:36–18:37: checkout order, Kafka correlation, PromQL, ES sentinel; 31 mẫu ổn định 15 phút; Hoàng nghiệm thu 19/10 00:47 | Bằng chứng lịch sử ngày 18/10. Trạng thái lab hiện tại UNKNOWN; nhánh create/start chỉ có mock (RV6-01) | **Đạt** ở mức nghiệm thu lịch sử |
| Một backend LLM trả kết quả thật | ZER-36/ZER-7; probe 37de4d63 (untracked); receipt 688efc5d… | Một inference thật 19/10 11:20:38 +07, HTTP 200, schema và kỳ vọng khớp, usage/cost/request ID có; tôi tái kiểm độc lập ở mục 2 | Fixture tổng hợp, không nối lab, không chứng minh phát hiện sự cố thật hay KPI. Khác cửa sổ thời gian với lab (18/10) và không chạy đồng thời | **Đạt kỹ thuật** sau review này; còn RV36-01, nghiệm thu, commit/PR/CI/merge vì là mã mới |
| Phạm vi được khóa | ZER-5 Done (snapshot); df5d542, trong main ab80005 | Ba AC PASS, SCOPE f73c38d9…, ZER-32/33 đã nghiệm thu | Không có | **Đạt** |
| RQ, đối chứng, ranh giới nhãn/evidence được khóa | ZER-8 (Todo theo snapshot); artifact 452493ab… untracked | Thiết kế đã review (mục 11), hướng được chấp nhận (mục 12), nguồn lực/BM chốt (mục 13); delta nhất quán trừ RV8-06 | Tham số formal khóa ở ZER-53 theo thiết kế, không phải thiếu. Artifact chưa chia sẻ được cho Hòa/reviewer (WORKFLOW mục Evidence) | **Đạt sau khi sửa RV8-06**; còn nghiệm thu toàn ZER-8 và publication |

**Kết luận G0:** chưa đóng. Về kỹ thuật, R0 gần đủ: lab và phạm vi đạt; backend đạt kỹ thuật; ZER-8 đạt sau một đoạn làm rõ RV8-06. Còn thiếu các bước không phải kỹ thuật:
1. Codex sửa RV36-01 và RV8-06 (P3 tùy chọn), retest.
2. Hoàng nghiệm thu ZER-36, ZER-7 và ZER-8.
3. Publication: probe là mã mới nên cần commit, PR, CI, merge; tài liệu ZER-8 và ZER-36 cần đưa lên nơi chia sẻ được.
4. Cập nhật Linear qua `linear_zero_door`.
5. Một receipt G0 riêng ghi bảng trên với revision cuối.

Không suy G0 từ số issue Done.

## 6. Kết luận theo issue

| Issue | Verdict review | Còn thiếu để Done |
| --- | --- | --- |
| ZER-36 | **PASS kỹ thuật** cho AC-01. Provider/model có căn cứ: quyền inference thật, giá và giới hạn model đối chiếu nguồn chính thức, rate limit quan sát trong header, caps probe rõ. Hard limit 1 USD là xác nhận của Hoàng, chưa đọc dashboard | Hoàng chấp nhận lựa chọn `gpt-6-luna` và caps; RV36-05(a) nên bổ sung; probe là mã nên cần commit/PR/CI/merge |
| ZER-7 | AC-01 như ZER-36. **AC-02 PASS** (receipt tái kiểm độc lập). **AC-03 PASS về hành vi** ở probe R0 độc lập; bằng chứng hồi quy chưa đủ cho đường timeout thực tế (RV36-01, P2) | Sửa RV36-01 rồi retest; Hoàng nghiệm thu; commit/PR/CI/merge; không N/A merge |
| ZER-8 | Delta mục 12–13 **nhất quán** với thiết kế đã review, trừ **RV8-06 (P2)**; RV8-07/08 là P3 | Sửa RV8-06; Hoàng nghiệm thu toàn ZER-8; CI/merge mã N/A vì chỉ tài liệu, nhưng **không** N/A chia sẻ artifact |
| G0 | **Chưa đóng**; xem mục 5 | Các bước 1–5 ở mục 5 |

## 7. Tự kiểm

| Nguồn được bảo vệ | SHA-256 lúc nhận | Sau review |
| --- | --- | --- |
| infrastructure/scripts/verify-llm-backend.py | 37de4d63ca72e4b690b5dbc256c3af6819ce16a3235967928e771188641e9c52 | Không đổi |
| infrastructure/scripts/verify-llm-backend.sh | 7850b18a49783cb22353e4c63235585718484464479df6abc44bc23ce82e777d | Không đổi |
| docs/evidence/ZER-36/test_probe.py | 1564179054f484766a10ffe12d9b9f5e9795ed5ae4564e724ed558b57df99f98 | Không đổi |
| docs/evidence/ZER-36/README.md | 2a9f9d741501542c9786dcbe5082d39bca139eb342ebe63ab4d9e2224ae34cd1 | Không đổi |
| docs/evidence/ZER-36/verification.md | f5a404ef6e8368bc5de592095295b01ea151844661ff8a113ff5d3bf45f143ed | Không đổi |
| docs/evidence/ZER-36/live-receipt.json | 688efc5d1b79a9ad68ce34cfc2aca6640a2921621341ad7779c6cc7791035e76 | Không đổi |
| docs/evidence/ZER-36/offline-cases.json | 0511ad7f7f35fb46768ce41a4c2e179b96096e4c8f05f752056dda197df4ba59 | Không đổi |
| docs/evidence/ZER-8/research-design.md | 452493abc947a3a78176c33674a6a7d0cb1cf103dc036bfacd6d0e619034aefc | Không đổi |

- Các file dirty theo quy ước (AGENTS, README, WORKFLOW, WORKING-AGREEMENT, research-questions) và SCOPE được kiểm bằng `scratch/zer36/claude/check.py`. llm-backend.md và NOW chỉ được nối hoặc chèn con trỏ; checker so với bản sao baseline.
- Scratch: `mutants.py` 2b953ce0…f7c881, `mutants.out` 26aefc10…dbdff2, `boundary.py` d571923b…63adeb, `boundary.out` e8a71241…a74fe8.
- Khi chạy test, Python có thể ghi `__pycache__` (gitignored). Các lượt kiểm sau đó dùng `-B`.
- Hash của báo cáo này ghi ở bàn giao cuối llm-backend.md, vì không thể tự ghi hash của chính file.
