# ZER-11 + ZER-39 fix-01 — Claude sửa gom sau Codex review

**Verdict: READY_FOR_CODEX_RETEST_OFFLINE.** Hai P2 (ZR11-01, ZR11-02) đã sửa kèm regression; N1 (P3) đã khép bằng validation nhỏ. Runtime vẫn **NOT_RUN** và RT1 còn một điều kiện trước khi xin quyền (harness H-RT1, xem dưới). Không có gì ở đây là Done hay kết luận G1.

## Baseline và phạm vi

- **Git:** HEAD `1694133`, nhánh `zer-10-independent-measurement`, không đổi nhánh. Staged rỗng.
- **Snapshot trước sửa:** `scratch/zer11/claude-fix01/before/` và `before.json`. Gồm 62 file: mọi file trong manifest gói đầu, note, NOW và toàn bộ `docs/evidence/ZER-11/` (kể cả báo cáo/probe của Codex). Lấy bằng `scratch/zer11/claude-fix01/snapshot_before.py`, script từ chối chạy lần hai.
- **Bằng chứng cũ giữ nguyên:** evidence gói đầu và `codex-review/` không bị sửa; [manifest-fix01.json](manifest-fix01.json) kiểm lại hash của chúng so với snapshot.
- **File sửa trong fix-01:** `nemesis/static/results.js`, `nemesis/measurement_view.py`, `tests/test_dashboard_measurement.py`, `infrastructure/scripts/verify-dashboard-baselines.py`, `docs/runbooks/dashboard-and-baselines.md`. **Thêm:** `tests/results_page_vm.cjs` và thư mục này. `main.py` không đổi. Measurement/event_pipeline/chaos-worker/contract vẫn chỉ đọc.

## Finding → sửa → kiểm

| Finding | Sửa | Ca kiểm | Kết quả | Artifact |
| --- | --- | --- | --- | --- |
| **ZR11-01** refresh giữ PASS sau 422/401/404 | `results.js`: chỉ lỗi vận chuyển (fetch không có phản hồi) và 502/503/504 ngoài các lý do cấu hình của store mới giữ STALE. 422, 401/403, 404, 500, 503 `REGISTRY_*`/`RESULTS_*`/`KEY_SEPARATION`, câu trả lời lệch run và view không render được đều xóa view, KPI và nút tải. Mất quyền còn kết thúc phiên (dừng poll). Đổi khóa xóa số cũ và vô hiệu mọi câu trả lời cũ trước khi đọc registry mới. View chỉ thành "last good" sau khi render xong | `tests/results_page_vm.cjs` chạy chính `results.js` trong Node VM, 19 ca: 11 good→fatal, 4 good→transient→good, fatal→transient, A→B trả muộn, đổi khóa có request cũ đang bay, đổi sang khóa đúng | 19/19 sau sửa; 12/19 fail trên snapshot, 7 control đạt cả hai | [fail-before](results/fail-before.txt) |
| ZR11-01 replay của Codex | — | `ui-counterexample.cjs` của Codex, chạy nguyên qua [replay_codex_ui.cjs](replay_codex_ui.cjs). Wrapper chỉ thêm `setInterval`/`clearInterval` mà trình duyệt luôn có; đường 401 mới gọi chúng, còn VM của Codex không cấp | 503 STALE giữ số (control); 422/401/404 xóa KPI | [codex-ui-counterexample-after.json](results/codex-ui-counterexample-after.json) |
| ZR11-01 browser | — | fixture-server SYNTHETIC; thêm 1 byte vào `score.json` của B1 như Codex | Poll sau: `ARTIFACT_ERROR ARTIFACT_HASH_MISMATCH`, 0 hàng KPI, 0 nút tải. Trả byte lại: poll sau hiện PASS mới. `{"fail": true}`: STALE giữ số kèm giờ. Đổi sang khóa sai: NO_ACCESS, xóa view/danh sách run, 18 s sau không có request nào | [browser/01–03](browser/) |
| **ZR11-02 (3)** không có đường đọc root S thật | `verify-dashboard-baselines.py serve-results`: app Nemesis thật trên 127.0.0.1, chỉ `results.html`/`results.js` và `/api/results/*`; route khác 404 `NOT_SERVED_IN_RESULTS_MODE` trước khi vào mã Nemesis; xóa startup (không consumer Kafka); không sinh fixture. Receipt ghi hash mọi file của root lúc khởi động và lúc thoát; có đổi thì exit 5 | `ResultsServer` (4 test): phục vụ đúng registry của root đã cho, view/hash/file khớp đĩa, POST 405, route khác 404 không gọi upstream, startup rỗng, root không đổi, receipt đầu/cuối, root thiếu registry hay đường tương đối bị từ chối | Đạt | [fail-before](results/fail-before.txt), [mutants](results/mutants.txt) |
| ZR11-02 (3) browser | — | `serve-results` trên một root dựng sẵn (2 run SYNTHETIC đã chấm và đăng ký; không phải dữ liệu runtime) | Trang chỉ liệt kê 2 run của root; hàng incident và hash score/incidents trên trang khớp từng ô với file và registry; `/dashboard/index.html`, `/api/status`, `/healthz` trả 404. Digest root sau khi phục vụ trùng digest lúc khởi động | [browser/04](browser/04-serve-results-standin-root.jpg) |
| **ZR11-02 (1, 2, 4, 5)** plan mâu thuẫn | Runbook mục 5 viết lại. P6 tách khỏi RT1 thành gói RT2 riêng (nguồn DETECTED, Docker, lần xóa pod và trần riêng, O-console BM). RT1 đúng 1 lần xóa pod. Cửa sổ trial phủ đủ W_eff 300 s và cap_rec 600 s + S; mốc dừng sớm ứng với đúng kết quả scorer (MISSING_PROBE/UNKNOWN_EFFECT, không TIMEOUT). Budget mỗi trial ≤ 995 mẫu (đủ K+S = 33 mẫu, đủ phủ TIMEOUT). Tổng worst case 3250 s trong trần 3600 s. HPA chỉ áp ở P4 | `plan-check` mã hóa ma trận và kiểm số học; `RuntimePlan` (3 test): budget đủ phủ, số cũ (35 phút, 30 giao dịch, P6 bật, xóa pod lần 2) bị từ chối, runbook trích đúng số tính ra | Đạt | `plan-check` trong [regressions](results/regressions.txt) |
| **N1 (P3)** shape → 500 | `check_document`: digest export H/O phải là SHA-256 hex (`INPUT_DIGEST_MISSING`); kiểm kiểu đúng các trường adapter, CSV và trang dùng; `incident_rows` chạy trong kiểm tra. `register` kiểm shape trước khi `measurement.output` dựng lại CSV | `test_shape_of_consumed_fields_is_a_reason_code`: 12 ca, mỗi ca 422 cả khi đăng ký lẫn khi đọc; control: khóa không ai đọc (`kpi.N`) vẫn đi nguyên | Đạt. Probe của Codex: 5 ca ra mã lý do, `kpi_type` (thêm `kpi.N`) vẫn nhận vì không trường nào dùng | [codex-adapter-probe-after.jsonl](results/codex-adapter-probe-after.jsonl) |

## Kiểm đã chạy

- **Fail-before** ([txt](results/fail-before.txt), [json](results/fail-before.json)): toàn bộ `test_dashboard_measurement.py` (33 test) chạy trên cây có source snapshot và cây hiện tại, cùng test hiện tại. 9 NEGATIVE fail trước và đạt sau; 24 CONTROL đạt cả hai. Regression trang: 12/19 ca fail trên `results.js` snapshot.
  - Bốn test `ResultsServer` và ba test `RuntimePlan` fail trước chỉ vì tính năng chưa có. Vì vậy bất biến của chúng được chứng minh thêm bằng mutant.
- **Mutant** ([txt](results/mutants.txt), [json](results/mutants.json)): 12 mutant, mỗi cái phá một bất biến fix-01 thêm, đều bị bắt; control sạch đạt.
- **Hồi quy** ([regressions.txt](results/regressions.txt)): `run_regressions.sh` của gói đầu chạy nguyên trên 3 interpreter pin (suite mới và liên quan, `check_r1_baselines`, guard manifests, CI boundary, `check_agent_dependencies`, measurement ZER-10 offline, `node --check`, Bandit, `git diff --check`). Sau đó thêm: regression trang, `plan-check`, hai replay của Codex, Bandit cho file Python sửa.
- **Clean checkout** ([clean-checkout.txt](results/clean-checkout.txt)): `git archive HEAD` cộng 22 file của gói (gồm harness JS và runbook), không có `scratch/`.

## Lần chạy lỗi giữ lại

- **mutants-attempt1** ([txt](results/mutants-attempt1.txt)): 11/12. Mutant `UNRENDERED_VIEW_IS_LAST_GOOD` đặt `S.view = view` trước `render()` và sống sót. Lý do: sau khi lỗi không có HTTP status đã là fatal, thứ tự này chỉ là phòng thủ, nên mutant tương đương. Tôi thay bằng `STATUSLESS_ERROR_TRANSIENT`, phá đúng bất biến thật (coi lỗi không có HTTP status là tạm thời, đúng như phân loại cũ); mutant mới bị bắt.
- Một lần chạy lại mutant y hệt attempt1 (do sửa script qua heredoc bị lỗi, script không đổi) đã bị xóa vì trùng nội dung attempt1.
- Lần đầu chạy phản ví dụ của Codex trực tiếp crash ở `clearInterval is not defined` (VM của Codex không có global này). Log không giữ; wrapper ở trên ghi rõ phần bổ sung.
- Ba log `.txt` (mutant, hồi quy) có khoảng trắng cuối các dòng có phần tóm tắt rỗng; đã xóa khoảng trắng đó sau khi chạy, nội dung không đổi. `run_regressions.sh` của fix-01 giờ tự làm bước này.
- Lần đầu chạy `serve-results` trong browser bị dừng cứng (không có Ctrl+C trong môi trường này), nên receipt lúc thoát không được ghi; digest được so bằng `root_digest` từ ngoài. Sau đó lệnh được sửa để ghi receipt ngay lúc khởi động, và đường thoát có test riêng.

## Thay đổi giao diện cần biết

- `results.js`: chính sách lỗi như trên. Đổi khóa giờ luôn xóa số cũ ngay; khóa bị từ chối kết thúc phiên.
- `measurement_view`: thêm mã lý do `INPUT_DIGEST_MISSING` (422). Score thiếu digest export hoặc sai kiểu ở trường được dùng giờ bị từ chối khi đăng ký và khi đọc; trước đây được nhận hoặc gây 500.
- `verify-dashboard-baselines.py`: thêm `serve-results` (cổng mặc định 8712) và `plan-check`. `fixture-server` không đổi.
- CI không đổi file: test mới nằm trong `test_dashboard_measurement.py`, vốn đã chạy ở `r1-agent-http`/`r1-production-http`. Test trang gọi `node` (có sẵn trên `ubuntu-latest`); thiếu `node` thì test fail, không skip.

## Residual / UNKNOWN

1. **Harness H-RT1 chưa có.** Không có mã nào trong repo phát ATTACK_REQUESTED/STOPPED, EFFECT_EVALUATED và RECOVERY_VERIFIED cho B0 ở runtime. Runbook 5.2 ghi đây là điều kiện trước khi xin quyền RT1. Harness cần test offline và review riêng; fix-01 không viết vì đó là mã lab chưa thể kiểm.
2. **Màn hình hẹp:** dưới khoảng 610 px, ô chọn run và bảng KPI làm trang cuộn ngang. Đây là CSS trong `results.html`, có từ gói đầu và nằm ngoài phạm vi file fix-01. Gói đầu đã kiểm ở 1024 px không cuộn; pane browser lần này rộng 455 px.
3. Residual gói đầu vẫn còn: console Nemesis H chưa phải O-console BM; console vận hành không gửi Authorization; B2/B3 chưa có producer; runtime và build image NOT_RUN.
