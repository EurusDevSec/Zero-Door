## ZER-48 — inference thật đạt, publication đã được duyệt — 28/10/2026

Hoàng duyệt toàn bộ [gói hoàn tất](completion-proposal.md); [authorization](completion-authorization.json) giữ exact reply và hash của [proposal đã duyệt](approved-completion-proposal.md). Đúng một inference qua adapter mới lúc14:06:22–14:06:27UTC (21:06 Việt Nam): NORMAL/health-01,1attempt/0retry,162input+22output,4.625s,0.0000272USD ước tính; request req_94202bcdbe4f43c1a56339f4debd4b19. [Receipt](live-receipt.json), [capture provenance](live-capture.json) và verification giữ source/IDs/usage/accounting. Client owned scope kết thúc và helper exit0; không pod/lab/build/deploy. Alias immutable revisionUNKNOWN.

AC01 đủ bằng chứng kỹ thuật ở mức shared adapter; còn scoped commit/PR/CI/review/merge và owner conditional acceptance trước Done. Nhánh publication được neo lại từ reviewed0b72edd sang main33001a3 có tree y hệt để PR chỉ gồm ZER-48; source5pins không đổi. Các trạng thái chờ quyền/live ở checkpoint dưới là lịch sử. G3/G4/agent consumer/end-to-end/KPI chưa được nghiệm thu.

# ZER-48 — adapter async và trace dùng chung

**Gói offline đã hoàn tất và review độc lập READY. Chưa đủ AC-01/Done: còn inference thật qua adapter mới và publication/CI/merge/nghiệm thu.** Cập nhật 2026-10-28 13:44:57 UTC (UTC; Việt Nam +07:00).

Hoàng giao Codex tiếp nhận sau khi Claude không tiếp tục. Chỉ thực hiện riêng ZER-48, không mở issue kế tiếp. [AC sống](https://linear.app/zero-door/issue/ZER-48/dung-llm-adapter-va-trace-dung-chung), parent ZER-19. ZER-36/37 đã đọc lại Done; R0 receipt cũ chỉ chứng minh backend riêng, không thay trace adapter mới.

## Kết quả trong scope

- Thêm event_pipeline/llm.py: fixed Responses endpoint/model gpt-6-luna từ R0; async httpx, no tools/redirect/proxy-env/SDK retries; tối đa2 attempts, timeout30s/call deadline65s, response≤1MiB, request≤8192byte. Không bật executor/consumer tác tử.
- Caller dùng một RunBudget chung cho cả run; reserve trước mọi dispatch, giữ reservation khi timeout/cancel/mất usage. Call/token/ước tính chi phí và duration có giới hạn, accounting theo run, không reset âm thầm. Đây là process-local accounting; không chứng minh budget tồn tại qua restart.
- Output model Pydantic phải closed/required; strict JSON chặn duplicate key, nonfinite và exponent overflow; normalize input rồi kiểm trường H bị cấm. Refusal/incomplete/invalid output không thành LLM success hoặc action.
- LLM_CALL có run/trial/decision/call IDs, attempt/retry, model/prompt hash/version, latency, usage/cost và trạng thái rõ. Không ghi provider exception/raw credential vào trace. Usage thiếu giữ UNKNOWN; inference hợp lệ có thể có accounting chưa đủ, và helper không nghiệm thu PASS khi cost incomplete.
- Fixed conservative estimate dùng Standard uncached rates0.10/0.50 USD per1M input/output, đối chiếu28/10 tại [model docs](https://developers.openai.com/api/docs/models/gpt-6-luna). Reservation dựa request UTF8 bytes+1024 overhead: giả định policy, không tokenizer guarantee/billing hard cap; cache/price/tier thực phải đối chiếu khi áp dụng. Observed usage vượt reservation làm budget blocked. Không suy quota còn lại từ receipt/header.
- Helper verify-llm-adapter.sh mặc định PLAN_ONLY, --offline fake; --live fixed đúng1call/1attempt,256output,20s attempt/25s call/30s async process,9472reservedtokens/0.005USD estimate. Lượt thật **chưa chạy**.
- Gaia/Hephaestus hiện COPY cả package event_pipeline nên có module khi build; CI thêm import smoke và focused tests. Nemesis image integration/copy còn thuộc ZER-19; không claim ba runtime đã dùng adapter.

Thiết kế request/edge handling theo [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses); không nâng OpenAI SDK1.35.5, model hoặc dependency lock.

## AC → evidence → verdict

| AC-01 | Kiểm hiện có | Kết luận |
| --- | --- | --- |
| Async/schema/version/usage/timeout |22 focused cases ×2 production pins (httpx0.27.0 và0.28.1); JSON/schema, cancel/resource close, retry, mode, secrets, concurrent shared budget, run deadline, normalization; [logs](results/). |Đạt offline component. |
| Consumer/contract/packaging không regression |100 lượt test liên quan: pipeline22, regressions42, agents4, consumer15, dashboard modes7, native mode bundle4, CIguard6. |Đạt; không chạy lại sau sửa module độc lập vì không đổi consumer/contract/CI wiring. |
| Review độc lập |Ba finding được tái hiện/sửa/retest, final READY trên5source pins; [review](independent-review.md). |Đạt cho offline package. |
| Trace thật qua adapter mới, usage/cost theo run |Chỉ có [receipt OFFLINE_SIMULATED](offline-receipt.json) ghim đúng source cuối; R0 live receipt không thay. |PENDING quyền chạy gói [hoàn tất](completion-proposal.md). |
| Publication/CI remote/merge/owner acceptance |Chưa commit/push/PR/merge hoặc đổi Linear trong gói này. |PENDING; không Done. |

Tổng **144 lượt test Python áp dụng đạt** (44 adapter+100 regression); reviewer còn tự chạy22case riêng. Bandit high severity/high confidence hai file mới:0findings; không là chứng nhận mọi severity. Bash syntax, entrypoint plan/offline và --live với key cố ý loại khỏi child environment đã kiểm. Không cài gói mới. Không provider/Kubernetes/Kafka/lab request hoặc build/deploy.

## Lỗi và giới hạn được giữ

Hai regression deadline-backoff và overflow đã fail trên source trước sửa, log review-regression-before.log giữ nguyên kết quả. Review còn tái hiện tuple bypass trước sửa bằng fake transport; regression mới yêu cầu0reservation/dispatch đã đạt. Root attempted pre-fix normalization check khởi chạy bất đồng bộ rồi source thay trước import, nên lượt đó PASS code đã sửa; **không dùng nó làm bằng chứng before-fix**. Một assertion dựa20ms Windows timer từng thấy2attempt khi timeout sớm sát deadline; test dùng clock xác định hết run trong pending request, giữ nguyên cap sản phẩm. Log windows-deadline-test-initial.log giữ failure này. Bandit lần đầu không có trong runtime test venv; chuyển đúng test-venv scanner đã có, không cài mới.

Graph zero_door vẫn primary9567830/incomplete/thiếu FTS; context Adapter không tìm thấy, detect_changes15files/0symbols không là coverage. Không có fresh graph/PDG/taint claim; review dựa source và probe offline trực tiếp. Giữ G3 NOT_VERIFIED, không G4/LLMagent/end-to-end/KPI PASS. Budget restart durability và authenticated event recorder delivery thuộc caller integration, không được suy từ helper.

[Verification/hash/preservation](verification.json), [source pins](source-hashes.json), [gói cần duyệt](completion-proposal.md). Mọi raw/evidence R3 và primary R giữ nguyên; metadata note/NOW chỉ thêm checkpoint. Các log phát hành chuẩn hóa CRLF→LF và whitespace cuối dòng, hash raw capture được giữ trong verification; không bỏ failure.
