# R0 / G0 — đối chiếu tích hợp chờ nghiệm thu và publication

**Kết luận kỹ thuật ngày 19/10/2026, 11:49 +07:** bốn vế gate có bằng chứng phù hợp sau sửa RV36-01/RV8-06. **G0 delivery chưa đóng**: còn Hoàng chấp nhận gói ZER-36/ZER-7/ZER-8, commit/push/PR/CI/merge mã probe mới, chia sẻ tài liệu và read-back Linear. Không dùng số issue Done thay gate. Không có API/lab mới trong lượt retest.

## Baseline và nguồn

Gate gốc ở [R0 README](../../delivery/milestones/R0-foundations/README.md): lab có giao dịch kiểm chứng được; một backend LLM trả kết quả thật; phạm vi/RQ/đối chứng và nhãn/evidence được khóa. AC sống ZER-36/ZER-7/ZER-8 đọc qua linear_zero_door trong lượt này: cả ba In Progress, AC giữ nguyên; không ghi Linear.

HEAD làm việc df5d542aaf726e62ea8ccb17a94490cd88322ee0, branch zer-5-scope-acceptance. Đây là bản local dirty để nghiệm thu, chưa là revision publication cuối. Snapshot hash dưới đây khóa bản đang trình; sau publication phải nối receipt commit/PR/CI/merge/artifact read-back thật, không tự tạo URL revision chưa tồn tại.

PR [#20](https://github.com/EurusDevSec/Zero-Door/pull/20) đã merged: head df5d542, merge ab800056962b1bfd24c9276f90ff4431235bdc3f; GitHub metadata xác nhận merged=true, git ls-remote origin main khớp merge này. Tree của head/merge cùng 3c8358585b0c94b88f0d2d31950644258f6ea7b8. Tài liệu R0 cũ đã vào main; receipt lúc08:21 không có PR là lịch sử đúng lúc ghi, không phải state hiện tại. Chưa có PR cho probe/ZER-8 mới.

## Gate → bằng chứng → giới hạn

| Vế G0 | Nguồn/revision | Bằng chứng và kết luận kỹ thuật | Giới hạn |
| --- | --- | --- | --- |
| Lab có giao dịch | [ZER-34 review](../ZER-34/claude-review.md), [ZER-35 restoration](../ZER-35/lab-restoration.md), mã lab đã merge PR #19 5471b58; nghiệm thu ZER-6/34 ở 968cc50 đã vào main qua PR #20 | Checkout hoàn tất, Kafka correlation, Prometheus query, ES sentinel;9 pod Boutique;31 mẫu trong15m17s; đã được Hoàng nghiệm thu18/10–19/10 | Bằng chứng lịch sử, không đo lại lab hiện tại; wrapper create/start chỉ mock; không suy uptime99,9% |
| Phạm vi/KPI/ledger | [ZER-32](../ZER-32/requirements-and-kpi.md), [ZER-33](../R0-T01-S03/baseline-source-ledger.md), [nghiệm thu ZER-5](../../delivery/milestones/R0-foundations/scope-and-criteria.md); commits8e7b74f/10a26b0/df5d542 đã vào main | Cam kết gốc giữ nguyên; D01–05 đã chấp nhận; ledger nguồn/legacy có review/acceptance | F01–09 và protocol formal còn khóa ởZER-53 theo giai đoạn; không dùng legacy làm LLM/lab mới |
| Một backend thật | [verification](../ZER-36/verification.md), [live receipt](../ZER-36/live-receipt.json), [Claude độc lập](../ZER-36/claude-review.md), [retest](../ZER-36/retest.json) | gpt-6-luna completed HTTP200, request ID/usage/latency/schema; probe37de4d63 khớp raw;12 test/14 mutant retest đạt sauRV36-01 | Fixture tổng hợp; model snapshot bất biến UNKNOWN; hard limit1USD do Hoàng xác nhận; AC03 fault injection, không provider outage/agent integration |
| RQ/control/GT/evidence | [research-design](../ZER-8/research-design.md) mục11–13, mục5.1/5.7 đã sửaRV8-06; [handoff](../../delivery/milestones/R0-foundations/research-questions.md) | B0/B1/B2/BM giữ, B3 có điều kiện; M1 chính/B2 KPI đã chấp nhận; pilot5USD/2hphiên/8 giờ tổng và BM đã chốt; GT theo variant rà trước sinh/niêm phong lịch từng trial, BM không xem lịch | Chưa vận hành harness; biết thiết kế case không là blind hoàn toàn; formal số lượt/budget khóa sau pilot;8h không dự báo đủpilot; chưa nâng hard limit |

Các vế thuộc các thời điểm khác nhau; gate không nhận chúng là một lượt end-to-end đồng thời. Không yêu cầu chạy lại lab hoặc API để làm đẹp thời gian khi chưa có thay đổi làm mất hiệu lực bằng chứng đã nghiệm thu.

## Sửa và retest sau review

- RV36-01: bổ sung coverage curl_exit28/6/7, retryẩn, proto,200+transport-error/refusal/expected-class. Suite12/12;14 mutantKILLED +CONTROL_OK. CI được thêm đúng một bước offline, YAML local parse đạt; chưa có CI remote.
- RV8-06: rà nhãn/A theo variant trước; schedule/seed/onset sinh sau và niêm phong; vai BM không xem trước/trongtrial;5.7 ghi cờ và audit UNKNOWN. Rà lại5.1/5.7/13 nhất quán; không có test runtimeharness.
- P3 tài liệu/provenance đã bổ sung trongverification; ba P3 code parser/prefix/IDduplicate giữ cho R1/R4, không ảnh hưởng receipt thật. Không tự tạo issue hoặc chỉnh scope.
-10file protected (probe Python/Bash, receipts gốc, báo cáo Claude, SCOPE và dirty quy ước) giữ hash. Không sửa raw hoặc báo cáo độc lập để đổi verdict của reviewer. Codex retest delta này là bước sau review, không phải một review độc lập mới toàn gói.

## Hash bản đang trình

| File | SHA-256 |
| --- | --- |
| Probe Python |37de4d63ca72e4b690b5dbc256c3af6819ce16a3235967928e771188641e9c52|
| Live receipt |688efc5d1b79a9ad68ce34cfc2aca6640a2921621341ad7779c6cc7791035e76|
| Claude review |8413a2ab834b606f537b6a7f3e36cdf1a031b5b5bb21f45b5f480112a56fcfbe|
| Test sau sửa |3a01c2cbda603448e6bfc5c880c68d1db101f2d967dce26d6555f6c1a96b4bbc|
| ZER-8 sau sửa |cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8|
| Retest offline |cf51cbb525e579085cbf21312167c2765486a939f5577414256ee5f6f8b9a4fb|

## Phần publication/nghiệm thu chưa thực hiện

Dự kiến nhánh zer-36-r0-acceptance, base origin/main đã xác minh ab800056, giữ mọi dirty ngoài scope. Allowlist ở scratch/zer36/codex-fix/publication-files.txt. Không dùng git add . hoặc gom quy ước/AGENTS/README/WORKFLOW/WORKING-AGREEMENT/NOW vào commit.

Sau Hoàng chấp nhận và cấp quyền: commit/push allowlist, mở PR và attach vào chat; chờ CI gồm suiteprobeoffline, giải quyết failure trong scope; merge chỉ sau CI đạt ở head cuối; đọc lại main/blob/receipt. Sau merge cập nhật ba issue36/7/8 và receipt G0 trên Linear trong quyền được cấp, không đổi lịch/assignment/quan hệ/issue khác. Khi ấy mới nối kết luận delivery thực vào đây. Hiện tất cả bước này PENDING; không tự chốt R0.

### Allowlist publication (14 file)

```text
.github/workflows/ci.yml
infrastructure/scripts/verify-llm-backend.py
infrastructure/scripts/verify-llm-backend.sh
docs/evidence/ZER-36/README.md
docs/evidence/ZER-36/test_probe.py
docs/evidence/ZER-36/verification.md
docs/evidence/ZER-36/claude-review.md
docs/evidence/ZER-36/live-receipt.json
docs/evidence/ZER-36/offline-cases.json
docs/evidence/ZER-36/retest.json
docs/evidence/ZER-8/research-design.md
docs/delivery/milestones/R0-foundations/llm-backend.md
docs/delivery/milestones/R0-foundations/research-questions.md
docs/evidence/R0/g0-acceptance.md
```

## Nghiệm thu và quyền publication — 19/10/2026

Hoàng đã chấp nhận gói ZER-36/ZER-7/ZER-8 sau sửa và retest, đồng thời yêu cầu: “commit push mở pr ci merge update linear và chốt receipt G0”. Quyền gồm publication, merge khi CI đạt ở head cuối và cập nhật Linear/G0. Không mở rộng thành quyền chạy lab/API/pilot hoặc nâng hard limit. Các đoạn PENDING phía trên là snapshot trước nghiệm thu; kết quả thực sẽ được nối sau khi GitHub/Linear đọc lại thành công.
