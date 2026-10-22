# ZER-11 + ZER-39 — gói offline của Claude

**Verdict: READY_FOR_CODEX_REVIEW_OFFLINE.**

- AC-01, AC-02, AC-03 của ZER-11 đạt ở mức offline/browser cục bộ.
- AC-04 của ZER-11 (= ZER-39 AC-01) đạt phần cấu hình và đường mã. Phần runtime B0 trên cluster là **NOT_RUN** vì chưa có quyền. Kế hoạch chi tiết ở [runbook mục 5](../../runbooks/dashboard-and-baselines.md#5-kế-hoạch-runtime-chờ-duyệt-g-zer11-rt1).
- Không có gì ở đây là Done hay kết luận G1.

## Baseline và phạm vi

- **Git:** HEAD `1694133`, nhánh `zer-10-independent-measurement`. `git diff HEAD origin/main` rỗng (cùng tree với `22a89db`).
- **Không tạo nhánh `zer-11-dashboard-baselines`.** Phiên Claude dùng chung checkout và không được switch branch. Nhánh này do Codex/Hoàng tạo khi publication.
- **Dirty sẵn có giữ nguyên.** 10 protected hash của intake vẫn khớp. Staged rỗng.
- **Snapshot trước sửa:** `scratch/zer11/claude/before/` và [before.json](../../../scratch/zer11/claude/before.json). Có 16 file có sẵn chép nguyên byte; 10 file mới ghi là absent.
- **Delta:** xem [manifest.json](manifest.json), gồm hash before/after của từng file: 11 file sửa, 35 file thêm. Manifest do `scratch/zer11/claude/make_manifest.py` sinh, kèm kiểm protected hash và staged rỗng.
- **Read-only, không đổi:** `measurement/`, `event_pipeline/`, `chaos-worker/`, evidence ZER-9/10/12/37, contract và thiết kế.

## AC → ca kiểm → kết quả

| AC | Ca kiểm | Expected | Actual | Artifact |
| --- | --- | --- | --- | --- |
| ZER-11 AC-01 bỏ số giả, hiện "không có dữ liệu" và nguồn | Console không còn đường KPI/Math.random/fallback; `/api/status` khi Prometheus lỗi; NaN; giá trị 0 thật; `/api/chat` | Không số giả; null thay cho 0; nguồn/trạng thái/giờ lấy | Đạt: fail-before 4 NEGATIVE; browser ảnh 08 | `test_dashboard_measurement.py` (StaticPages, Http), [browser/](browser/) |
| AC-01 (trang S) | EMPTY, TIMEOUT (mttr null), MISSING/CLOCK_UNVERIFIED, artifact lỗi | EMPTY không có rate; null là "no data"; artifact lỗi không hiện số | Đạt; ảnh 03, 04, 05 | AdapterValues, AdapterIntegrity |
| AC-02 chung phép đo, cùng run_id cùng KPI, hiện lỗi và độ trễ | E01 tính tay (30/60/90/19 s, N=1, PASS); KPI = `score.json`; bảng = `incidents.csv`; API = adapter; tải file = byte trên đĩa và hash; re-score cùng trace và options | Khớp từng giá trị; 422 khi tamper hash/CSV/run/group/schema/NaN/1e999/khóa trùng | Đạt; mutant bắt đủ, kể cả HASH/EXPORT/RUN/GROUP | [mutants.json](results/mutants.json) |
| AC-02 lỗi, stale, chuyển run | Poll lỗi; run A trả muộn 4 s sau khi đã chọn B | Giữ số cũ nhãn STALE kèm giờ; trang chỉ hiện B | Đạt trong browser (network log: A trả 200 sau B, trang vẫn B) | ảnh 06, mục "Browser" |
| AC-02 độ trễ cập nhật | `data_time` = mốc event mới nhất đã xác minh; `generated_at` không phải mốc | E01: 240 s sau T0 (t_stop); EMPTY → UNKNOWN | Đạt; mutant DATA_TIME_FROM_GENERATED_AT bị bắt | AdapterValues |
| AC-03 tách MANUAL/RULES/AI, MANUAL không auto-heal, có log | Consumer thật của Hephaestus qua gateway thật cho 5 nhóm; `/heal/trigger` thật | Chỉ B1 ra DECISION RULES (positive control); nhóm khác có `MODE_AUDIT`; BM được admit rồi `R1_EXECUTOR_DISABLED`; executor giả chạy đúng 1 lần, replay không lặp; RULES qua đường manual bị từ chối | Đạt; fail-before 4 NEGATIVE + 2 CONTROL | `test_dashboard_modes.py` |
| AC-03 nhãn mode | Mode lấy từ group của `score.json`; query `?group=B2` bị bỏ qua | B1→RULES, BM→MANUAL, B0→K8S_BASELINE | Đạt | Http, AdapterValues |
| AC-04 = ZER-39 AC-01 cấu hình | `r1-baselines.yaml` qua OpenAPI pin k8s; bảng nhóm = fixture contract 7.4; B0 không decider/executor/LLM/RBAC; HPA 1..3 = `MAX_REPLICAS`, target có CPU request; Nemesis live không mount kết quả | Đạt | Đạt | `check_r1_baselines.py` |
| AC-04 dữ liệu B0 | B0 không action: TotalRecovery 90 s, MTTD/MTTR/reaction N/A; B0 có DECISION → 4 MODE_VIOLATION, MISSING | Đúng contract 7.4 và ZER-8 4.1 | Đạt (fixture) | ca `b0_*` |
| AC-04 runtime | Controller/HPA tự phục hồi, ZERO DOOR không phát heal (có coverage và positive control), probe độc lập đo | — | **NOT_RUN** (chưa có quyền) | runbook 5 |

## Kiểm đã chạy

Interpreter dùng venv production pin của ZER-12:

- `scratch/zer12/production-nemesis`: Python 3.11.9, FastAPI 0.111.0, Pydantic 2.7.4, Starlette 0.37.2.
- `production-hephaestus`: cùng pin, có kubernetes 28.1.0.
- `pinned-venv`: lock guards, FastAPI 0.110.0, kafka-python-ng 2.2.2.

Kết quả:

- **Fail-before** ([txt](results/fail-before.txt), [json](results/fail-before.json)): 8 NEGATIVE fail trên source trước sửa và đạt sau sửa; 5 CONTROL đạt cả hai. Test dùng bản hiện tại, source dùng snapshot.
- **Mutant** ([txt](results/mutants.txt), [json](results/mutants.json)): 17 mutant cho các bất biến chưa có phiên bản trước (adapter, route, seam), đều bị bắt; control sạch đạt.
- **Hồi quy** ([regressions.txt](results/regressions.txt)):
  - Suite mới và suite liên quan trên 3 interpreter.
  - `check_r1_baselines`, `check_guard_manifests`, `test_command_guard_ci`, `check_agent_dependencies`.
  - Measurement ZER-10 offline (mã không đổi), `node --check`.
  - Bandit 0 finding. Ba dòng subprocess của script verify có `nosec` kèm lý do: argv cố định, không shell.
  - `git diff --check`.
- **Clean checkout** ([clean-checkout.txt](results/clean-checkout.txt)): `git archive HEAD` cộng đúng các file của gói, không có `scratch/`, chạy suite mới bằng venv pin.

### Browser

Kiểm trên pane browser của Claude Desktop với `fixture-server` (dữ liệu SYNTHETIC, 127.0.0.1, không Kafka/Prometheus/model). Ảnh trong [browser/](browser/):

| # | Trạng thái quan sát |
| --- | --- |
| 01 | Chưa có khóa: `NO_ACCESS`. Khóa sai: `UNAUTHORIZED` |
| 02 | B1 loaded: nguồn, hash, `generated_at` ghi rõ không phải mốc event, độ trễ cập nhật, KPI 30/60/60/19 s |
| 03 | TIMEOUT: MTTR `NOT_PASS`, mean "no data" (không phải 0) |
| 04 | EMPTY: verdict EMPTY, không có rate |
| 05 | Artifact bị sửa sau đăng ký: `ARTIFACT_ERROR ARTIFACT_HASH_MISMATCH`, không hiện số |
| 06 | Upstream lỗi: `STALE` kèm giờ lần thành công cuối, số cũ giữ nguyên |
| 07 | B0 có DECISION: 4 MODE_VIOLATION, MISSING |
| 08 | Console vận hành: không có KPI; nguồn lỗi hiện STALE; AI hiện unavailable |

- Chuyển run khi A trả muộn: network log cho thấy A trả 200 **sau** khi đã chọn B; DOM vẫn là B (TIMEOUT).
- Bảng incident trên trang khớp từng ô với `incidents.csv` tải về (hash header = registry).
- Viewport desktop 1024 px không cuộn ngang toàn trang.

**Sửa sau khi kiểm browser:**

- Cột ghi chú trống hiện "no data"; `rows` của decision hiện `[object Object]`; flags rỗng hiện "no data" thay vì "none".
- Trang cuộn ngang toàn trang.
- Trình duyệt chạy `results.js` cũ đã cache. Đã thêm `Cache-Control: no-cache` (ETag/304) cho `/dashboard`.

## Lần chạy lỗi giữ lại

- Lần đầu chạy fail-before/mutant crash trước khi chạy test nào, vì đường interpreter tương đối khi đổi cwd. Log lần đó không giữ; script đã đổi sang đường tuyệt đối.
- **attempt1** ([fail-before-attempt1.txt](results/fail-before-attempt1.txt), [mutants-attempt1.txt](results/mutants-attempt1.txt)):
  - Control `test_command_guard_integration` fail cả trước lẫn sau. Test tôi sửa đòi dòng log ở vị trí đầu, nhưng chính lệnh từ chối cũng ghi log; đã sửa thành `assertIn`.
  - Mutant `RESULTS_ACCEPT_WRITES` sống sót, vì route chỉ có GET nên FastAPI cũng trả 405. Test đã siết, đòi mã `READ_ONLY` của middleware, kể cả trên đường không có route.

## Thay đổi giao diện cần biết

- Biến môi trường mới cho Nemesis: `ZD_RESULTS_ROOT` và `ZD_RESULTS_TOKEN_FILE` (khóa `{"id","purpose":"results-reader","secret"}`). Không đặt thì `/api/results/*` trả 503 `RESULTS_NOT_CONFIGURED`.
- `/api/status` trả null kèm `source`. `/api/heal-history` trả 503/502 khi upstream lỗi. `/api/chat` trả UNAVAILABLE. `/api/chat/clear` thành no-op.
- Hephaestus: lỗi `/heal/trigger` log dạng `MODE_AUDIT {json}`. Seam `R1_EXECUTOR` chỉ test gán. GuardedRules có thêm thuộc tính `skipped`.
- Dockerfile Nemesis copy `measurement_view.py`. CI thêm suite mới vào job `r1-agent-http` và `r1-production-http`. Chưa build image.

## Residual / UNKNOWN

1. **Console Nemesis là console tấn công (H).** Người giữ khóa operator vẫn thấy log kết quả tấn công (`attackType`) qua `/api/logs`. Repo chưa có O-console riêng cho operator BM. Gói này chỉ chặn kết quả S; BM runtime cần console O riêng hoặc ẩn log H. Đây là việc ngoài AC hiện tại.
2. **Console vận hành không gửi Authorization.** Hành vi này có từ ZER-12, nên trên deployment thật các GET `/api/*` trả 401 và trang hiện lỗi nguồn. Gói không thêm ô nhập khóa operator.
3. **Độ trễ cập nhật chỉ biết khi có mốc event đã xác minh.** Run rỗng hoặc chỉ có đồng hồ chưa xác minh thì ghi UNKNOWN. Không dùng `ts_ingest` của export vì adapter chỉ đọc artifact S.
4. **B2/B3 không có producer**, nên dashboard ghi unavailable. Không có số liệu AI thật nào.
5. **Runtime B0 (P0–P5), BM trên image mới (P6) và build image: NOT_RUN.**
