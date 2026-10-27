# Codex review — ZER-42 / ZER-13 AC-03–04

**CHANGES_REQUIRED_OFFLINE — 26/10/2026, Asia/Ho_Chi_Minh.** Chưa đủ điều kiện chạy nghiệm thu runtime hoặc đóng issue. Đây là review local dirty package trên HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, nhánh `zer-41-sqli-fixture`; staged rỗng. Không sửa source sản phẩm, không chạy lab/build/model, không commit/push hay đổi Linear.

Đã đọc trực tiếp AC sống của ZER-42 và cha ZER-13 qua `linear_zero_door`, URL đúng `linear.app/zero-door/`; cả hai In Progress. Đối chiếu gói ở cuối [issue note](../../delivery/milestones/R2-chaos-scenarios/sqli-fixture.md), contract event §4.2/5.2/7.2 và consumer scorer. Không mở lại nghiệm thu ZER-41.

## Findings gom

### ZR42-01 — P2 — Effect dùng sai thời điểm và chưa chứng minh phủ cửa sổ

Vị trí: `infrastructure/scripts/sqli_executor_runtime.py:40–61`; `chaos-worker/internal/attack/sqli.go:77–90,110`.

`t_eff` lấy từ `AttackResult.timestamp`, được tạo trước vòng gửi HTTP. Nó không phải thời điểm mẫu thực sự trả hàng restricted; raw từng send cũng không có timestamp/sequence/clock để suy ra thời điểm ấy. Đồng hồ CLI mặc định `clock-unknown` không bổ sung bằng chứng đồng hồ nguồn.

Nhánh NO_EFFECT chỉ so `clean >= min_clean_sends`, không dùng `w_eff_s` để kiểm [T_req, T_req+W_eff] hay khoảng trống. Phản ví dụ chạy được:

- Mẫu disclosure tại +4 s vẫn nhận `t_eff` tại thời điểm bắt đầu command (+0 s).
- Một mẫu sạch duy nhất cho cửa sổ 30 s → `CONFIRMED_NO_EFFECT`.
- Một mẫu sạch rồi một lỗi TRANSPORT → vẫn `CONFIRMED_NO_EFFECT`.
- `min_clean_sends=0`, không có mẫu → vẫn `CONFIRMED_NO_EFFECT`.

Contract §4.2/7.2 yêu cầu thời điểm của bằng chứng thật và phủ kín cửa sổ. Scorer còn tái kiểm phần phủ từ raw PROBE_SAMPLE (`measurement/scorer.py:409–429`), nên payload evaluator hiện tại không tự chứng minh được phần này. Dùng thời điểm command làm T_eff cũng có thể làm sai MTTD/total.

**Sửa:** ghi quan sát có thời điểm/sequence và đồng hồ nguồn rõ; T_eff phải gắn mẫu disclosure thực tế theo tiêu chí đã khóa. Nhánh NO_EFFECT kiểm cửa sổ và gap từ bằng chứng raw thích hợp; thiếu thời gian/clock/phủ, dữ liệu lỗi hay tham số đánh giá không hợp lệ không được thành NO_EFFECT. Giữ nguyên schema/scorer đã khóa; nếu cần mô tả cách biểu diễn raw SQLi, ghi quyết định ngắn trước sửa, không tự đổi định nghĩa KPI.

### ZR42-02 — P2 — HTTP 200 sai schema bị coi là dữ liệu sạch

Vị trí: `chaos-worker/internal/attack/sqli.go:260–279`; consumer `sqli_executor_runtime.py:41–47`.

`json.Unmarshal` thành công chưa chứng minh response là kết quả catalog hợp lệ. Fake transport trả `{}`, `null`, hoặc `{"results":null,"count":0}` đều cho `SUCCESS`, rows=0, restrictedRows=0, không có error. Count âm và row thiếu visibility cũng được nhận.

Tôi đưa chính JSON result từ Go vào evaluator Python: ba trường hợp đầu đều thành `CONFIRMED_NO_EFFECT`. Đây là chuỗi lỗi thực qua hai consumer, không chỉ đầu vào giả gọi evaluator riêng.

**Sửa:** kiểm các trường bắt buộc, kiểu dữ liệu, count không âm và khớp rows, SKU/visibility hợp lệ trước khi đánh dấu mẫu sạch. Sai schema/count hoặc thiếu dữ liệu phải có lỗi rõ và giữ UNKNOWN khi đánh giá effect. Thêm regression trên response đầy đủ, thiếu và mâu thuẫn; không cần đổi fixture ZER-41.

### ZR42-03 — P2 — Ticker có thể phát hai request cách nhau dưới một giây

Vị trí: `chaos-worker/internal/attack/sqli.go:170–184`.

Fake response đầu mất 1,5 s. Tick cũ bị giữ trong channel; ba lần bắt đầu gửi cách nhau **1,5002 s rồi 0,5003 s**. Concurrency vẫn 1 và tổng send vẫn có trần, nhưng nhịp gửi không còn giữ khoảng cách một giây như giới hạn gói/runbook. Test hiện tại chỉ đo hai request trả nhanh nên không bắt được.

**Sửa:** đặt lịch gửi tiếp từ lần gửi thực tế và không phát bù tick tích lại; chờ vẫn bị ngắt bởi context/deadline. Regression có response chậm rồi nhanh, kiểm tất cả khoảng cách gửi cùng trần thời gian/tổng send.

### ZR42-04 — P2 — Exact match chưa thực thi ranh giới private ingress

Vị trí: `chaos-worker/internal/validation/target.go:30–39`, `internal/guard/policy.go:75–84,148–157`; Python `nemesis/command_guard.py:95–108`.

Nếu trusted policy chứa endpoint sai, cả hai phía vẫn chấp nhận endpoint TEST-NET `http://203.0.113.10/fixture/catalog/search`. Go còn chấp nhận loopback; hai phía chấp nhận URL service fixture trực tiếp. Target namespace/service trong JSON vẫn ghi đúng fixture, nhưng địa chỉ kết nối chỉ phụ thuộc URL. Không có kiểm private/ingress identity hoặc resolved peer trong đường transport hiện tại.

**Đây là cấu hình trusted sai được nhận, không phải operator ghi đè endpoint vượt exact match.** Mặc định disabled và exact comparison vẫn có giá trị. Tuy nhiên chúng chưa đáp ứng giới hạn gói: chỉ private fixture qua proxy, không endpoint ngoài lab hay đi tắt bỏ điểm quan sát IP. Các probe này chỉ validate/admit dữ liệu, không kết nối địa chỉ TEST-NET/public/loopback.

**Sửa:** biểu diễn profile ingress được phép đủ hẹp, đồng nhất Python/Go; từ chối cấu hình ngoài lab/đi thẳng fixture. Đường kết nối/preflight phải kiểm địa chỉ thực dùng theo profile được cho phép, không chỉ suffix/contains host. Dùng fake resolver/transport cho kiểm offline; địa chỉ private thật và quyền lab chốt riêng sau review, không nới endpoint công khai để test qua.

### ZR42-05 — P2 / thiếu đầu ra gói — Chưa nối dấu vết request và event H

Vị trí: `chaos-worker/internal/attack/sqli.go:77–90,239–250`; `infrastructure/scripts/sqli_executor_runtime.py:65–85`; [verification](verification.md), phần residual.

Request không có correlation header; response `X-Request-Id` bị bỏ. Probe fake ghi `request headers=map[]`, và `X-Request-Id=request-123` không xuất hiện trong raw result. Không có khóa ghép command → từng HTTP request → fixture log/IP. Điều này chặn đường chuẩn bị AC-04 đã giao, dù việc chứng minh IP runtime vẫn phải chờ lab.

CLI hiện chỉ đọc result JSON rồi in payload; không nối result transport với `FAULT_EXECUTOR_RESULT`, `EFFECT_EVALUATED` và kho H. `build_event` mới được gọi ở unit test. Gói đã thành thật khai báo residual này, nhưng bảng AC vẫn ghi valid template chạy end-to-end và AC-04 verification path prepared, mạnh hơn đầu ra thực có. Runbook §6 cũng chưa có envelope tổng thời gian/pod/image/tổng HTTP+health/ES cụ thể để duyệt.

**Sửa:** giữ correlation/response request ID trung tính có giới hạn ở từng send; nối raw/result → event H đúng role, causation/context/clock và reference bằng chứng, dùng lại contract/client hiện có. Kiểm offline xuyên entrypoint bằng fake tới đường evidence này, không chỉ gọi builder riêng. Chuẩn bị envelope runtime cụ thể và cleanup theo ownership; chưa chạy. Không đưa template/oracle/seed vào O và không sửa contract/scorer/fixture để dễ đạt.

## Phần đã xác nhận đúng

- Opt-in capability, template enum, command shape và legacy target/customParams tách riêng hoạt động trên các case hiện có.
- Nemesis ASGI thật + fake Kafka: request hợp lệ 200, gửi lại cùng ID 200 nhưng publish chỉ một lần; template/target override/kiểu duration sai bị từ chối trước publish.
- Chính envelope do ASGI tạo được Go Authenticate → Policy.Admit → Dispatcher → SQLIExecutor thật với fake HTTP nhận đúng, một send.
- Thiếu executor trả `DISPATCH_CONFIG` trước claim. Redelivery sau expiry + đóng/mở ledger thật trả đúng result ID cũ và vẫn chỉ một send. Không có finding ở routing/replay này.
- Redirect không theo, transport không cấu hình proxy môi trường; send/response/deadline đã có các trần hiện hữu. Findings ở trên không phủ nhận toàn bộ executor.

## Kiểm đã chạy và giới hạn

| Kiểm | Kết quả trực tiếp |
| --- | --- |
| Python SQLi, production Nemesis và Hephaestus | 14 test mỗi môi trường, OK |
| Python guard/integration/CI hiện có, production Nemesis | 26 test, OK |
| Go `go test ./... -count=1 -timeout=120s` | 6 package OK; Go 1.25.6 Windows |
| Go `go vet ./...` | Exit 0 |
| Go overlay counterexamples + signed/replay controls | Tái hiện rate/schema/trace/endpoint; cross-language và replay controls đạt |
| `tests/check_guard_manifests.py` | Các manifest hiện có và command-guard-config OpenAPI PASS |
| Bandit evaluator `-lll -iii` | Exit 0, không finding |
| CLI `--help`, `git diff --check` | Exit 0 |
| Hash 23 file intake trước ghi report/handoff | Không drift; ba nguồn fixture ZER-41 nguyên hash |

Không chạy lại `fail_before.py` vì nó sửa source rồi restore, không phù hợp lượt review chỉ đọc. Không coi mutant là fail-before revision thật. Không chạy CI/race Linux, build, Kubernetes/broker/ES hay lab. Không tuyên bố manifest lab mới đã được kubeconform kiểm chỉ từ gate manifest hiện có; đã đọc YAML/embedded policy và Go sample load trong suite.

GitNexus context đọc được nhưng index ngày 22/10 thiếu file SQLi mới; `Admit` chỉ dẫn tới Dispatcher cũ, không chứng minh completeness. Các lần refresh có giới hạn trong lượt sửa tài nguyên trước đã timeout; không lặp tải index lúc máy còn áp lực RAM. Review này dựa diff/source và probe, **không có taint/PDG cập nhật**, không nhận là review graph đầy đủ.

Kết quả, source hashes và raw phản ví dụ: [codex-review-results.json](codex-review-results.json). Script/log tái hiện ở `scratch/zer42/codex-review/`: `evaluator_probes.py`, `consume-malformed.py`, `asgi_probe.py`, `go/` overlays và các `.sh` launcher. Test tái hiện lỗi có thể PASS vì assertion xác nhận hành vi sai đang tồn tại; không đọc chữ PASS ấy thành nghiệm thu sản phẩm.

## Gói sửa gom và retest

Claude sửa cả ZR42-01…05 trong một lượt, giữ snapshot trước sửa để regression fail-before thật. Phạm vi nguồn vẫn theo gói cũ: SQLi executor/result, validator/policy Python–Go, evaluator/runtime helper và test SQLi; bổ sung entrypoint wrapper/testdata/evidence trong allowlist nếu cần. `dispatch.go`, auth/ledger, legacy executors, fixture/seed/expected ZER-41, locked contract/scorer, shared agents và dirty sửa tài nguyên giữ nguyên. Nếu cần chỉnh ngoài allowlist, ghi đề xuất cụ thể thay vì tự mở rộng.

Không dựng framework mới, không chạy lại mọi bộ QA không liên quan. Chạy hồi quy bị ảnh hưởng và các phản ví dụ trên; lưu raw mới, giữ báo cáo Codex chỉ đọc. Một verification cập nhật, handoff ngắn tại note/NOW. Verdict sau sửa là READY_FOR_CODEX_RETEST_OFFLINE, chưa runtime/Done. Codex retest các ranh giới đã sửa rồi mới chuẩn bị một lượt lab có quyền riêng; không yêu cầu Hoàng duyệt từng sửa nhỏ offline đã giao.

**AC hiện tại:** ZER-42 AC-01 / ZER-13 AC-03 chưa đạt trọn giới hạn đã chốt vì ZR42-03/04; đường valid/signed/replay đạt offline. ZER-13 AC-04 chưa đạt, cả logic evidence lẫn runtime còn thiếu. ZER-41 giữ nguyên nghiệm thu trước; không đóng cha hay sub-issue từ report này.
