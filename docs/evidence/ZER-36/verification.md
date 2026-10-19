# ZER-36 / ZER-7 — Xác minh backend R0

Đọc lại AC sống cả hai issue qua linear_zero_door ngày 19/10/2026, 11:22 +07; cả hai In Progress. Không ghi Linear. Codex đối chiếu receipt người dùng chạy với probe và request hiện tại; không phát sinh lượt API mới. Đây là retest receipt và tự review probe của Codex, chưa là review độc lập của một người viết khác.

## Lượt gọi thật

- Evidence: [live-receipt.json](live-receipt.json), SHA-256 688efc5d1b79a9ad68ce34cfc2aca6640a2921621341ad7779c6cc7791035e76. Sao chép nguyên byte từ scratch/zer36/runs/run-47adfcce-8427-4c40-884e-b103da4e73a0/receipt.json; không sửa raw.
- Run ID: zer36-502a6f48-9bee-4a1a-89a9-a13481898cc9. Bắt đầu 2026-10-19T04:20:38.965641+00:00 (11:20:38 +07), kết thúc 04:20:41.942088 UTC. Thời điểm lấy từ receipt, không dùng đồng hồ trang trí terminal.
- HTTP 200, completed, một attempt; request ID req_5041abe670da4f36a9b0ff9b956d4a3b; response ID resp_0754202c3eeee663016ad59a970b4887d081d2dcf2ed965907.
- Model yêu cầu/trả về gpt-6-luna; reasoning none, service_tier default, store=false, tools rỗng. Provider chỉ trả alias, revision snapshot bất biến UNKNOWN và đã ghi rõ.
- Client attempt latency 2969 ms, tổng 2969 ms; một mẫu, không suy phân phối latency hoặc KPI.
- Usage: input 259 (cached 0, cache writes 0), output 68 (reasoning 0), total 327.
- Ước tính Standard: (259 × 0,10 + 68 × 0,50) / 1.000.000 = 0,0000599 USD. Không có attempt thiếu usage; đây không là hóa đơn/account-spend read-back. [Giá model đã đối chiếu](https://developers.openai.com/api/docs/models/gpt-6-luna).
- Header x-ratelimit-limit-requests=30000 và x-ratelimit-limit-tokens=180000000: đã quan sát trực tiếp trong receipt, khớp số Hoàng cung cấp. Không phải remaining quota hoặc chứng minh ngân sách.
- Output đúng schema và expected: HIGH_CPU, frontend, bằng chứng cpu-01/duration-01; 88% >80% trong 75 s. Fixture tổng hợp, không đọc lab/production.

## Retest và ca lỗi

Probe SHA-256 37de4d63ca72e4b690b5dbc256c3af6819ce16a3235967928e771188641e9c52 khớp file đã chạy; request và request_sha256 khớp request hiện tại. Codex chạy lại parser/schema/expected/result/cost trên raw receipt chỉ đọc: PASS. Script retest local ở scratch/zer36/retest-live.py. Không sửa probe sau lượt live, không cần chạy trả phí lại để lấy cùng bằng chứng.

Bộ kiểm offline trước lượt live: 8 nhóm đạt, có 13 biến thể HTTP 200 sai bị chặn; auth/quota/budget không retry; timeout/network/transient được giới hạn; key không nằm trong argv; response/header parser. Nhánh thiếu curl có xử lý OSError trong mã, chưa có test riêng. Chi tiết case trong [test_probe.py](test_probe.py).

Bổ sung [offline-cases.json](offline-cases.json), SHA-256 0511ad7f7f35fb46768ce41a4c2e179b96096e4c8f05f752056dda197df4ba59, để reviewer đọc log từng attempt. Mọi run trong file đều OFFLINE_SIMULATED, không gọi OpenAI:

| Case | Expected | Actual | Verdict kiểm |
| --- | --- | --- | --- |
| Timeout hết hai attempts | Dừng sau một retry, RULES/degraded, usage UNKNOWN | 2 attempts, RULES, FAIL, unknown_usage=[1,2] | PASS component |
| 429 tạm thời rồi thành công | Một retry, chỉ output hợp lệ mới nhãn LLM | 2 attempts, LLM, PASS; attempt lỗi còn usage UNKNOWN | PASS component |
| 401 | Không retry, fallback RULES | 1 attempt, RULES, FAIL | PASS component |
| Project hard limit 429 | Không retry, fallback RULES | 1 attempt, RULES, FAIL | PASS component |

Các verdict FAIL trong log lỗi là kết quả probe mong đợi; không sửa thành LLM PASS. Ca timeout là fault injection tại transport, chưa chứng minh outage của OpenAI hoặc đường lỗi trong agent đang triển khai.

## Đối chiếu AC và giới hạn nghiệm thu

| AC | Bằng chứng | Kết luận kỹ thuật hiện tại |
| --- | --- | --- |
| ZER-36 AC-01 / ZER-7 AC-01 | Chọn OpenAI/gpt-6-luna có structured output, quyền inference thực, header rate limits, giá/model limits và caps probe tại README | Đủ evidence kỹ thuật cho lựa chọn R0; project 1 USD + hard limit là xác nhận Hoàng, chưa dashboard read-back; không suy ngân sách pilot/formal |
| ZER-7 AC-02 | Lượt mới có timestamp/run_id/request ID/model/latency/usage, schema và expected khớp | PASS kỹ thuật trên đầu vào giám sát tổng hợp; immutable model revision UNKNOWN được khai báo |
| ZER-7 AC-03 | Timeout/retry/fallback và nhãn RULES kiểm bằng fault injection; có raw log OFFLINE_SIMULATED | PASS thành phần ở probe độc lập; không nhận là lỗi provider thật hoặc integration test của agent |

Gói sẵn sàng review độc lập/nghiệm thu. Chưa Done: mã probe mới chưa review độc lập, commit/push/merge hoặc Hoàng nghiệm thu. Chưa thực hiện publication/Linear. Không ép provider phát sinh timeout/429 thật để lấy bằng chứng; reviewer đánh giá mức component fault injection đúng AC trước khi nghiệm thu.

Bảo toàn 10 file ngoài scope bằng SHA-256 baseline, gồm ba agent, SCOPE, dirty quy ước và ZER-8. git diff --check sẽ kiểm sau cập nhật evidence. GitNexus analyze --index-only phiên 19594 đã hoàn tất exit 0 (2973 nodes, 3598 edges, 29 clusters, 48 flows); cảnh báo 7 field timestamp xuyên ngôn ngữ không được resolve, không suy kết quả rỗng là không dùng. Không runtime lab mới; G0 không tự đạt từ receipt này.

## Codex sửa gom sau review độc lập — 19/10/2026

- **RV36-01 đóng kỹ thuật:** suite mới 12 nhóm đạt; thêm curl exit28/6/7 với cả exhaustion và retry→success, HTTP200 kèm lỗi transport, refusal kèm output_text hợp lệ, NORMAL/UNKNOWN hợp schema nhưng sai expected. Ghim --retry0, --proto=https, connect10/max-time30; không sửa probe. Chạy nguyên 14 mutant của reviewer: 14 KILLED, đối chứng CONTROL_OK. Test được nối vào job bash-tooling của CI; mới kiểm local, CI remote chưa chạy. Log retest bổ sung ở retest.json; không sửa offline-cases/live-receipt/báo cáo Claude gốc.
- **RV8-06 đóng thiết kế:** Hoàng/Hòa rà variant và nhãn/A trước; harness sinh/niêm phong thứ tự/seed/onset sau đó. Hoàng BM không đọc lịch trước/trong trial; Hòa rà mức trial nếu cần, Hoàng rà lịch đã kết thúc. Mục5.7 ghi cờ người vận hành đã thấy lịch và phân biệt UNKNOWN audit; chưa nhận là kiểm runtime.
- **RV36-05 (P3):** với giả định input vẫn 259 token/attempt như lượt đo, tối đa hai attempts × (259×0,10 +512×0,50)/1M = **0,0005638 USD**. Đây là ước tính có điều kiện cho request/model hiện tại, không hard cap tiền tuyệt đối (tokenizer/overhead/giá có thể đổi), không hóa đơn hoặc quyền tiêu ngân sách. Hard limit project1 USD là xác nhận người dùng, có độ trễ enforcement.
- Receipt không có header remaining/reset vì probe chỉ lưu allowlist, không phải bằng chứng OpenAI không trả. Không phục dựng các header đã bỏ.
- Đọc công cụ local sau review: Python3.12.4, Bash PATH curl8.9.0 trong Git; máy cũng có System32 curl8.21.0. Receipt cũ không lưu executable/version: curl thực dùng cho lượt lịch sử **UNKNOWN**, không suy từ PATH/shutil.which hoặc chọn phiên bản có lợi. Không đổi probe chỉ để điền metadata giả.
- Đo clock local hiện tại: monotonic GetTickCount64/time GetSystemTimeAsFileTime resolution0,015625s; perf_counter QueryPerformanceCounter resolution1e-7s. Receipt giữ nguyên; số thập phân không chứng minh độ chính xác cao hơn clock. Ghi yêu cầu provenance/clock cho R1, không nhận đã sửa phép đo MTTD runtime.
- **P3 code RV36-02/03/04** vẫn được khai báo: output item sai kiểu có thể crash, model chấp nhận prefix, evidence ID trùng. Receipt thật không gặp; không nhận probe R0 là adapter production. R1/R4 cần xử lý theo các finding này; không tạo issue hoặc đổi scope ở đây.
- **RV8-07/08:** cập nhật con trỏ AC-01/BM/ngữ cảnh ngân sách ở ZER-8; nguồn lực pilot vẫn giữ quyết định. Theo ví dụ1050s/trial,30 cell≈8,75h, vượt trần8h: vòng đầu cần khai báo subset/cell trước, có B3 để đo khả thi, báo pilot từng phần; không đổi quyết định hoặc tự chạy pilot. Hard limit1 USD và budgetpilot5 USD phải được đối chiếu/nâng theo quyền trước thực thi.
- **G0-01 verified:** GitHub PR20 đã merged, head df5d542aaf726e62ea8ccb17a94490cd88322ee0, merge ab800056962b1bfd24c9276f90ff4431235bdc3f; git ls-remote xác nhận main ở merge này. Cả hai có tree3c8358585b0c94b88f0d2d31950644258f6ea7b8. Không sửa receipt08:21 (đúng thời điểm đó); đây là read-back mới. Mã/evidence32/33/34/6/5 đã có trên main; probe/ZER-8 mới chưa publication.
