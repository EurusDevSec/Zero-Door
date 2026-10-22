# Codex review — ZER-11 + ZER-39 — 21/10/2026

Verdict: **CHANGES_REQUIRED_OFFLINE / NOT_READY_FOR_RUNTIME**. Hai finding P2 cần sửa; một ghi chú P3 không chặn. Không có finding P1 được xác nhận. Review local, chưa nghiệm thu hay Done.

## Findings

### ZR11-01 — P2 — Refresh giữ PASS khi artifact đã bị từ chối vì integrity

**Vị trí:** agent-orchestrator/nemesis/static/results.js:240 (nhánh240–246).

Sau khi run tải thành công, mọi lỗi refresh vào nhánh S.view && refresh, gắn STALE rồi return. Không phân biệt503 upstream với422 ARTIFACT_HASH_MISMATCH,401 UNAUTHORIZED hay404 RUN_NOT_REGISTERED. clearView/ARTIFACT_ERROR bên dưới chỉ chạy khi không có cache. Run đã bị xác định không còn hợp lệ vẫn hiện PASS/100%/KPI/download, trong khi tải export hiện tại bị từ chối. Trái runbook dashboard-and-baselines.md:18 (artifact lỗi không hiện số) và AC-01/02 về lỗi/nguồn nhất quán. Trường hợp401 là xử lý trạng thái hiển thị sai, không phải bypass xác thực.

**Đã chạy:** browser fixture SYNTHETIC reviewer tạo trên127.0.0.1:8721. B1 hiện MTTD30/MTTR60/reaction19/PASS. Thêm một byte khoảng trắng vào score.json, giữ registry hash. Poll sau trả ARTIFACT_HASH_MISMATCH; DOM vẫn bốn hàng PASS/rate100%, trạng thái STALE. File fixture đã restore nguyên byte, không sửa artifact Claude. Ảnh: codex-review/stale-integrity.png.

**Replay:** node docs/evidence/ZER-11/codex-review/ui-counterexample.cjs → ui-counterexample.json. Chạy chính results.js trong DOM/fetch fake:503 giữ STALE là control đúng;422/401/404 cũng giữ PASS. Một nguyên nhân chung, không ba finding riêng.

**Sửa:** chỉ giữ last-good STALE với lỗi vận chuyển/upstream tạm thời theo policy rõ. Integrity/schema, mất quyền hoặc run bị rút phải xóa cache/view/download và hiển thị lỗi tương ứng. Kết nối lại/đổi khóa cần vô hiệu response cũ trước đọc danh sách mới. Regression good→fatal, good→transient→good; giữ A→B. Không thêm công thức KPI.

**Test cũ lọt:** ASGI kiểm422 riêng; browser kiểm artifact hỏng khi chưa có cache và STALE503 riêng. Thiếu good→integrity lỗi trong refresh. GitNexus context loadRun xác nhận get/render/clearView/setState, process LoadRun→$; proof chính là browser/VM.

### ZR11-02 — P2 — Runtime plan chưa nhất quán để xin duyệt thực thi

**Vị trí:** docs/runbooks/dashboard-and-baselines.md:122,:125,:137,:156,:158,:176; đối chiếu infrastructure/scripts/verify-dashboard-baselines.py:55,:148.

Năm điểm cùng gói runtime:

1. P1 scale Gaia0, chỉ restore P7; Nếu bật P6, pha này triển khai Nemesis/Hephaestus nhưng đòi DETECTED thật từ Gaia. Không có producer được cấu hình trong pha đó.
2. Trần đúng một lần xóa pod frontend; P3 xóa một và P6 lặp P3 thêm một. P6 tùy chọn nhưng khi duyệt vẫn vượt tổng.
3. P5 đề nghị fixture-server trỏ root thật; script luôn tạo/sinh fixture SYNTHETIC, parser chỉ nhận port. Không có đường chạy như mô tả để chứng minh dashboard đọc run runtime thật.
4. Trial tối đa6phút nhưng cap_rec600s; stop condition nói chưa phục hồi thì TIMEOUT. Coverage6phút không đủ600s: phải giữ incomplete/MISSING nếu dừng sớm, không ép TIMEOUT. Không đổi scorer/criteria đã khóa để che giới hạn.

5. Trần30giao dịch/trial, một giao dịch là một sample (agent-orchestrator/measurement/probe.py:93). Ở nhịp1s/mẫu đã ghi, K=3 rồi S=30s cần tối thiểu33mẫu pass liên tục (recovery.py:44–66), chưa tính warm-up/failure. Trần30không đủ điều kiện xác minh recovery. Cần budget/cadence và gap được review nhất quán, giữ criteria đã khóa.

**Sửa:** ma trận pha/tài nguyên/budget/rollback nhất quán; chỉ rõ P6 có/không, ai phát DETECTED, tổng thao tác khớp trần. Chuẩn bị đường chỉ đọc root S thật với startup cô lập, không tự bật Kafka/model; lệnh chạy được và test không thay dữ liệu thật bằng fixture. Thời gian đủ cap hoặc stop sớm phải incomplete. Xin quyền đúng gói sau review, chưa chạy lab; không mở R2/R3/R4.

**Test cũ lọt:** checker manifest kiểm config/schema, không chạy pha runtime hay lệnh phục vụ root thật. Đã đối chiếu source/runbook trực tiếp; không dùng cluster trong review.

### ZR11-N1 — P3 — Validation chỉ kiểm một phần shape của artifact

**Vị trí:** agent-orchestrator/nemesis/measurement_view.py:234,:263,:306,:310.

Output scorer thật được sửa bằng quyền local trước register: kpi={} hoặc thiếu input hash vẫn register/view; milestones=list, findings.mode_violations=int, leak=list được register nhưng view ném AttributeError/TypeError→HTTP500 thay vì422 reason-code. Reader request không ghi artifact/registry; file sửa sau register bị hash chặn. Cần quyền local và output bình thường hợp lệ nên đây là P3, không bypass auth/P2 mới.

Repro: docs/evidence/ZER-11/codex-review/adapter-probe.py + adapter-results.jsonl. Nếu khép, kiểm đúng trường adapter tiêu thụ và input digest rồi chuyển lỗi shape thành ResultError; không framework schema mới/catch-all che lỗi.

## Target và provenance

- Repo R:/_Projects/Eurus_Workspace/zero_door. Local unstaged+untracked thuộc manifest Claude; staged rỗng. HEAD169413303340fc01eea8597c121ce39455892af0, branch zer-10-independent-measurement; origin/main22a89db11a041faa1db797a6a9f1afee1abde647. origin/HEAD chưa cấu hình; main lấy từ handoff/refs đã đọc.
- Intake46/46after hash khớp;10/10 file ngoài scope khớp. Không sửa source/evidence Claude trong review.
- AC sống đúng Linear Zero Door: ZER-11/39 In Progress; childAC01=parentAC04. Không đổi status/checkbox.
- Scope: adapter/auth/Nemesis backend+static; Hephaestus mode/consumer; baseline/checker; CI/Dockerfile wiring; tests/evidence/runbook.
- GitNexus query/context/impact/detect_changes/explain/PDG controls đã dùng. Refresh --pdg --index-only đã sinh symbol ResultsStore/loadRun mới nhưng chưa nhận receipt hoàn tất và đã ngắt; không claim index toàn repo hoàn chỉnh. ResultsStore lower-bound8receiver sites, manual_heal lower-bound1. Không coi0caller/0taint là proof an toàn. detect_changes gồm dirty owner và không tự bao hết untracked: manifest/direct reads là surface thật.

## Kiểm độc lập và giới hạn

- Hai production env Nemesis/Hephaestus: Python3.11.9/FastAPI0.111.0/Pydantic2.7.4. Mỗi env dashboard24,modes7,command_modes3,guard_integration13,event_agents4 PASS (51method/env); baseline OpenAPI/profile và guard manifests PASS.
- Fixture đi qua Archive/scorer/CSV/register; E01 MTTD30/MTTR60/Total90/reaction19 khớp nguồn/browser. Không là runtime.
- Node syntax app.js/results.js PASS. Bandit bằng scratch/zer12/test-venv PASS0finding; hai interpreter thử trước không có Bandit, giữ log, không cài thêm. git diff --check PASS.
- VM3fatal case sai+1transient control đúng. Browser xác nhận good→hash422→STALE giữ PASS.
- Không chạy lại17mutant/fail-before/clean checkout/134measurement; mã measurement không đổi và có log Claude. Không nhận các con số này là reviewer tự chạy.
- Không Kubernetes/Docker/model/provider/build/CI từ xa/commit/push/PR/Linear. Chưa có quyền runtimeZER11/39. Fixture loopback, tamper đã restore.

## AC và tiếp theo

| AC | Review hiện tại | Còn thiếu |
| --- | --- | --- |
| ZER-11 AC-01 | Đường KPI/AI giả đã bỏ; no data/nguồn có; CHANGES_REQUIRED ở refresh integrity | ZR11-01 |
| AC-02 | API/export cùng artifact, hash/CSV/run và số tính tay đạt; CHANGES_REQUIRED ở UI lỗi | ZR11-01,run thật theo plan đã sửa |
| AC-03 | PASS_OFFLINE ở consumer/HTTP thật dùng fake, positive control1action/replay; production executor disabled | Build/CI theo quyền; không claim LLM/heal runtime |
| AC-04=ZER-39 AC-01 | Config/entrypoint PASS_OFFLINE; runtime NOT_RUN | ZR11-02,quyền và evidence B0/controller/HPA thật |

G1 chưa PASS. Console Nemesis H không tự được dùng làm console BM/O; B2/B3 chưa có producer là giới hạnR1, không yêu cầu làmR4. BM evidence isolation cần chứng minh trướcG1, không gắn nhãn ngoàiAC rồi dùng consoleH làm đối chứng.

Gói fix-01: sửa haiP2+regression+runtime plan sẵn chạy; có thể khépN1 bằng validation nhỏ. Snapshot trước sửa; giữ report/probe/hash reviewer. Claude tự review gom rồi Codex retest phần ảnh hưởng; runtime/publication vẫn riêng. Không nhân probes/mutants để tăng số lượng.
