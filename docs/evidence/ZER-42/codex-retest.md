# Codex retest — ZER-42 / ZER-13 AC-03–04

**NOT_READY / CHANGES_REQUIRED_OFFLINE — 26/10/2026 (+07:00).** Hai finding cũ đã đóng; ba finding cũ mới sửa một phần. Không mở lại nghiệm thu ZER-41. Review source chỉ đọc; không lab/build/model/Git publication/Linear write. HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, checkout `zer-41-sqli-fixture`, staged rỗng. AC sống ZER-42 và cha ZER-13 đã đọc qua `linear_zero_door`, đúng workspace; cả hai In Progress.

## Finding còn chặn, gom theo nguyên nhân

### FX42-R1 — P2 — Timestamp mới vẫn chưa là mốc bằng chứng dùng được

Vị trí: `chaos-worker/internal/attack/sqli.go:307–310,357–358`; `infrastructure/scripts/sqli_executor_runtime.py:105–109`.

`observedAt` được ghi ngay khi `client.Do` trả header, **trước** `io.ReadAll` và trước khi biết body chứa hàng gì. Fake response có body chậm 450 ms cho thấy timestamp sớm hơn lúc đọc được body **450 ms**. Nếu body chứa disclosure, T_eff vẫn sớm hơn bằng chứng thật; đổi command start thành header time chưa khép ZR42-01.

Ngoài ra, `isoAt` dùng RFC3339Nano và evaluator chép nguyên chuỗi vào `t_eff`. Tôi lấy JSON do **Go executor thực** tạo qua fake response, đưa vào evaluator → `build_event` → consumer `measurement.scorer.semantic`: `t_eff=2026-10-26T15:03:51.0639923Z`, status CONFIRMED; transport validator nhận nhưng **scorer trả INVALID**. Test mới chỉ dùng chuỗi có đúng ba chữ số nên bỏ sót chênh lệch này. Contract §4.1 bắt buộc floor UTC về `.mmmZ`; `measurement/clock.py:24–29` và scorer:92–93 thực thi chuẩn đó.

**Sửa:** chốt quan sát sau khi đọc/kiểm body thành công; lỗi đọc cũng có thời điểm kết thúc thực. Chuẩn hóa mốc đưa vào event theo contract, giữ raw độ phân giải cao riêng nếu cần. Kiểm bằng chính JSON Go → evaluator → scorer, gồm body chậm; không nới parser/scorer/contract để nhận dữ liệu sai. Giữ clock của producer và clock của bằng chứng đúng nguồn, không tự đổi UNKNOWN thành HOST_SHARED.

### FX42-R2 — P2 — Raw thiếu/mâu thuẫn vẫn bị biến thành NO_EFFECT

Vị trí: `infrastructure/scripts/sqli_executor_runtime.py:64–76,89–132`.

Các phản ví dụ độc lập, ngoài 21 test hiện có:

- Sáu mẫu sạch phủ 5 s, nhưng một mẫu có `restrictedRows=1` mà thiếu `restrictedSkus`: `_usable` vẫn nhận và evaluator kết luận **CONFIRMED_NO_EFFECT**. Có dấu hiệu restricted nhưng chưa biết đó là SKU nào phải giữ UNKNOWN, không thành dữ liệu sạch.
- Cùng chuỗi phủ sạch, thêm một record `error=TRANSPORT` **không có observedAt**: record bị bỏ khỏi `in_window`, kết luận vẫn NO_EFFECT. Không biết record lỗi thuộc lúc nào không phải bằng chứng nó nằm ngoài cửa sổ.
- Thêm phần tử `null` vào sends làm `AttributeError` ở nhánh `s.get`, thay vì trả UNKNOWN có lý do.

Probe còn ghi nhận `gap_s=inf` cho một mẫu duy nhất vẫn NO_EFFECT; đây là cùng thiếu kiểm tham số hữu hạn. Không cần dựng framework validation mới: kiểm hình dạng, kiểu/giá trị và tính nhất quán của raw/tham số tại biên evaluator; dữ liệu không đủ căn cứ phải UNKNOWN. Nhánh CONFIRMED cũng cần thời gian hợp lệ và thứ tự có căn cứ, không chỉ một chuỗi parse được. Giữ giới hạn so sánh xuyên đồng hồ theo contract; UNKNOWN clock không tự phủ nhận duration trong cùng đồng hồ.

**Sửa:** required SKU list khi restrictedRows > 0, kiểm kiểu phần tử/list và count; giữ record lỗi/thiếu thời gian như thiếu dữ liệu, không lọc mất để tạo coverage. Validate gap và các tham số hữu hạn. Regression phải có cả đối chứng raw đầy đủ vẫn đạt, không chỉ đổi mọi kết luận thành UNKNOWN.

### FX42-R3 — P2 — ZR42-04 mới kiểm DNS trước kết nối, chưa khóa địa chỉ thực dùng

Vị trí: `chaos-worker/internal/attack/sqli.go:179–196,360–392`; `internal/validation/target.go:15–24,37–46`; Python `command_guard.py:92–115`.

Từ chối IP literal và địa chỉ resolver không private là tiến bộ đúng. Tuy nhiên `checkPeer` bỏ danh sách IP đã kiểm; `http.Transport` mặc định vẫn tự resolve/dial lại hostname. Code chưa bảo đảm peer thực là IP đã duyệt. `verification.md` cũng xác nhận điều này và chuyển việc bind peer sang runtime, trong khi đây là phần triển khai có thể và cần kiểm offline trước lab; runtime chỉ chứng minh topology thật.

Profile hiện tại cũng nhận mọi `<service>.<namespace>.svc.cluster.local`, trừ đúng một tên fixture. Probe validate (không kết nối) nhận cả `frontend.target-app.../fixture/catalog/search` và `fixture-copy.zd-sqli-lab.../fixture/catalog/search`. Chúng không chứng minh một endpoint là ingress đã được duyệt. **Đây vẫn là cấu hình trusted sai được nhận, không phải operator vượt endpoint exact-match.** Không có request nào gửi đến các địa chỉ này trong review.

**Sửa:** chốt profile ingress được phép và kiểm endpoint/peer thực theo profile đó; production dial phải dùng/kiểm địa chỉ đã duyệt, giữ Host/route và fail closed. Đồng nhất Go/Python. Fake resolver/dialer đủ kiểm không có đường resolve lại không kiểm; địa chỉ/Service thật và source IP vẫn cần preflight/runtime riêng. Không cho phép mọi private address chỉ vì cùng dải RFC1918.

**Không xếp thành lỗi production về trần thời gian:** gọi riêng executor với Background cho thấy DNS chưa nằm trong deadline nội bộ và DurationMs bỏ phần DNS. Nhưng tôi kiểm consumer trực tiếp: `Dispatcher.Handle:91–93` đã đặt deadline bao ngoài. Signed command hợp lệ duration=1 s, fake resolver đợi 1,2 s bị ngắt sau **1002 ms**, sends=0. Do đó phản ví dụ direct-call không đủ kết luận production vượt trần. Giữ control này khi sửa dial/preflight.

### FX42-R4 — P2 / thiếu đầu ra gói — ZR42-05 chưa giữ được raw để kiểm lại

Vị trí: `infrastructure/scripts/sqli_executor_runtime.py:141–175,178–194`; `docs/runbooks/sqli-executor.md:79–93`.

Correlation/response ID nay được giữ đúng trong **AttackResult**, và hai event có causation đúng. Nhưng `emit_evidence` gửi vào sink chỉ:

1. FAULT_EXECUTOR_RESULT với status, command_ref, duration;
2. EFFECT_EVALUATED với số đếm tóm tắt.

Không event nào giữ raw `sends`, observedAt, windowStart, requestId/responseId, hay tham chiếu bền có hash đến raw. Probe fake sink nhận status NO_EFFECT nhưng không giữ được cả request ID, response ID và mẫu thời gian để tái tính. CLI vẫn chỉ in payload `--evaluate`; không có đường chạy/export kết quả xuyên archive đã kiểm offline. `scorer.no_effect:409–429` cần raw PROBE_SAMPLE/flow tương ứng, không tin số đếm trong `evidence`; hai event trên chưa đủ khép đường này.

**Sửa:** chuẩn bị một đường nhận result → lưu raw bất biến/ghép context → event H → export/tái kiểm, dùng client/archive hiện có hoặc adapter nhỏ trong allowlist. Fake sink/transport phải kiểm nội dung xuất thật, retry/dedup nếu dùng client, không chỉ độ dài list=2. Không gắn nhãn executor observation thành probe độc lập một cách tùy tiện; nếu raw chưa biểu diễn đủ theo contract, nêu đúng khoảng trống và giữ UNKNOWN/PARTIAL, không nới scorer/schema hoặc tuyên bố NO_EFFECT đã tái kiểm.

Runbook §6 vẫn chưa có **đề xuất** envelope thời gian/pod/image/tổng HTTP+health/ES và cleanup cụ thể. Chuẩn bị con số đề xuất không phải tự cấp quyền chạy lab; Hoàng chỉ duyệt sau khi có gói reviewable. Không cần hỏi lại tiêu chí effect đã khóa, không dùng lượt ZER-41 cũ làm quyền ZER-42.

## Đối chiếu finding cũ và AC

| Finding cũ | Retest |
| --- | --- |
| ZR42-01 thời gian/phủ | PARTIAL — mẫu thưa và lỗi có timestamp đã UNKNOWN; còn FX42-R1/R2 |
| ZR42-02 schema HTTP 200 | **CLOSED offline** — `{}`, `null`, results null/count âm bị SCHEMA/FAILED; không sửa fixture |
| ZR42-03 nhịp gửi | **CLOSED offline** — timer theo lần phát thực tế; test slow→fast và mặc định 1 rps đạt |
| ZR42-04 private ingress | PARTIAL — IP literal/direct fixture chính/private preflight đã chặn; FX42-R3 còn mở |
| ZR42-05 trace/event H | PARTIAL — ID ở AttackResult và causation đã đúng; raw/export/envelope còn FX42-R4 |

ZER-42 AC-01 / cha AC-03: valid/signed/replay đã đạt offline, nhưng chưa khép ranh giới endpoint đã giao. Cha AC-04 chưa đủ đường bằng chứng và chưa runtime. **Chưa Done, chưa runtime-ready.** Việc đã làm vẫn được giữ; không làm lại fixture ZER-41 hoặc lịch sử R1.

## Kiểm đã chạy và giới hạn

- Python production pins Nemesis/Hephaestus: SQLi **21/21 mỗi pin**; legacy guard **26/26**.
- Go 1.25.6 Windows: `go test ./... -count=1 -timeout=120s` **6 package đạt**, vet exit 0; gofmt các nguồn SQLi sạch. Khác toolchain 1.21.13 trong báo cáo Claude.
- Go overlay fake: timestamp/body, schema/trace và JSON result thật; signed Dispatcher valid, thiếu executor, expired replay và ledger close/open restart giữ đúng **1 send**; control deadline ở trên đạt.
- Python probe: các đối chứng đầy đủ/thưa/disclosure + raw lỗi; JSON Go → evaluator → scorer. Mọi probe kết luận theo giá trị, không coi exit 0 của script chẩn đoán là verdict sản phẩm PASS.
- Bandit evaluator ngưỡng CI exit 0, không finding; help không side effect; `git diff --check` sạch. Manifest/CI/policy/main/executor base không đổi so với review trước, không lặp render/build chưa liên quan.
- Không chạy lại mutant harness vì nó sửa/khôi phục source; không nâng self-report 11 mutant của Claude thành retest độc lập. Chưa race/CI Linux/build/broker/lab/API/model.
- GitNexus query/detect_changes/context đã dùng để điều hướng. Index 22/10 khớp HEAD nhưng chưa có SQLi dirty/new; hai lần refresh trước đã timeout trong gói tài nguyên. Không lặp indexing nặng khi máy đang áp lực RAM; không tuyên bố graph/PDG/taint đầy đủ. Phạm vi source và consumer được đọc trực tiếp. Agent phụ review Go bị classifier chặn, không có kết quả dùng làm bằng chứng; các probe trên do Codex chạy trực tiếp.
- Local review, origin/HEAD chưa có symbolic ref; `main` chỉ là fallback tên default branch. Không fetch/switch/reset; không review một PR remote.

Raw/log/hash/snapshot: [codex-retest-results.json](codex-retest-results.json), `scratch/zer42/codex-retest/`. Bản review cũ giữ nguyên SHA-256 `47a21e7c6ebe5d36d315789767ee90d148a456af5dbf2c719b65bd6d144e0ca0`. ZER-41 app/seed/expected và các nguồn ngoài fix đối chiếu giữ nguyên.

## Gói sửa gom và retest kế tiếp

Giữ một writer và allowlist hiện có. Chụp source trước sửa, giữ report/probe Codex chỉ đọc. Sửa **FX42-R1…R4 cùng nguyên nhân liên quan** trong một gói: timestamp/consumer; validation/coverage; ingress/dial; raw/export và đề xuất lab. Không thêm scanner/dependency/framework, không đổi ZER-41, R1 contract/scorer, maintenance 6GB hoặc legacy executors để vượt test. Nếu cần file adapter ngoài allowlist, ghi rõ trước thay đổi theo issue note.

Tự kiểm trên fake/loopback và hai pin, tái chạy signed Dispatcher/replay và consumer scorer với JSON Go thật. Dùng các case ở đây làm expected độc lập; đối chứng hợp lệ phải tiếp tục đạt. Hoàn tất một verification ngắn + handoff, rồi Codex retest phần ảnh hưởng. **Chưa lab/build/model/publication/Linear**; đề xuất envelope không phải quyền thực hiện.
