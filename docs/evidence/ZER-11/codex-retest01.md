# Codex retest fix-01 — ZER-11 + ZER-39 — 21/10/2026

**RETEST_PASS_OFFLINE. Không còn finding P1/P2 mở trong delta đã review. Chưa READY_FOR_RUNTIME và chưa Done.** H-RT1 chưa được viết; AC-04/ZER-39 còn thiếu bằng chứng B0 runtime. Đây là phần thực hiện còn lại đã khai báo, không phải lỗi mới phát hiện trong fix-01.

## Target và phạm vi

- HEAD `169413303340fc01eea8597c121ce39455892af0`, nhánh `zer-10-independent-measurement`; `origin/main` local ref `22a89db11a041faa1db797a6a9f1afee1abde647`. Không fetch, switch, commit hay stage.
- Review delta so với `scratch/zer11/claude-fix01/before/`, không gộp dirty work của Hoàng thành thay đổi của fix-01. Manifest fix-01: 28 đường dẫn (7 modified, 21 added), 28/28 hash khớp lúc nhận. Ngoài delta, 55/55 file trong snapshot giữ nguyên; 10/10 owner-protected hash khớp intake độc lập.
- Đã đọc lại AC sống qua `linear_zero_door`: URL thuộc `linear.app/zero-door/`, ZER-11 và ZER-39 đều In Progress. Không sửa Linear.
- Code review: `results.js`, `measurement_view.py`, script verify, test JS/Python và runbook. Đọc consumer trực tiếp `register`, `ResultsStore.artifact/view`, route kết quả Nemesis, CLI `serve_results` và test entrypoint. Không đổi source.

## Retest từng finding

| Finding | Bằng chứng độc lập | Kết luận |
| --- | --- | --- |
| ZR11-01, refresh giữ KPI sau lỗi fatal | Chạy chính JS hiện tại: 19/19 ca đạt. Cùng harness trên snapshot trước sửa: 12 ca fail, 7 control đạt. Replay phản ví dụ Codex nguyên bản qua wrapper chỉ bổ sung timer global của browser: 503 giữ STALE; 422/401/404 xóa KPI. Kiểm direct source nhánh transient/fatal, invalidation khi đổi khóa và response run cũ | FIXED |
| ZR11-02, kế hoạch và đường phục vụ root thật | `ResultsServer` 4 test và `RuntimePlan` 3 test đạt trên cả hai production environment. `results_app` dùng root được chỉ định, chỉ phục vụ trang S và API results; bỏ startup Kafka, route khác bị chặn, file tải khớp byte/hash, root không đổi. Receipt có mốc đầu/cuối và exit 5 nếu root đổi. Kế hoạch: P6 tách riêng; một delete; 995 mẫu/trial, tối thiểu 33 mẫu đạt để xác minh; 1260 + 2 × 995 = 3250 s trong trần 3600 s | FIXED ở mức thiết kế/offline; H-RT1 vẫn thiếu |
| N1 P3, shape artifact gây 500 | Replay 6 ca của Codex: 5 ca lỗi được từ chối bằng ResultError; control thêm `kpi.N` không ai tiêu thụ vẫn được nhận. Test shape kiểm cả register/read với reason-code 422; không thêm scorer hay schema framework | Các phản ví dụ đã nêu được khép |

Đã xem ảnh browser `fix-01/browser/01-good-then-hash-mismatch-cleared.jpg`: ARTIFACT_ERROR, KPI trống đúng như bàn giao. Đây là ảnh do Claude chụp; lượt Codex này kiểm JS/ASGI độc lập, **không chạy lại browser**. Không nhận ảnh đó thành một lượt browser của reviewer.

## Kiểm Codex thực sự chạy

- Production Nemesis: dashboard **33/33**, modes **7/7** (tool transcript, exit 0).
- Production Hephaestus: dashboard **33/33**, gồm serving/plan/shape; log [production-hephaestus.log](codex-retest01/production-hephaestus.log).
- JS **19/19**, snapshot fail-before **12 negative / 7 control**; [current](codex-retest01/ui-current.json), [before](codex-retest01/ui-before.json).
- [UI replay cũ](codex-retest01/ui-independent-replay.json) và [adapter replay cũ](codex-retest01/adapter-independent-replay.jsonl) được đọc theo giá trị, không chỉ exit code.
- [plan-check](codex-retest01/plan.json): problems rỗng; số học nêu trên là ngân sách đề xuất, không phải thời lượng runtime đã quan sát.
- Bandit hai file Python sửa: exit 0, không finding; Node syntax JS trang/harness và `git diff --check` đạt.
- Không chạy lại measurement 134, mutant 12/12, clean checkout hay ma trận 3 interpreter của Claude. Chúng vẫn là bằng chứng lịch sử trong fix-01, không phải lượt retest độc lập này.

## Graph và review theo miền

GitNexus đã refresh local bằng `analyze --pdg --index-only`, hoàn tất exit 0; metadata `2026-10-21T05:01:53.461Z`, HEAD đúng, 934 files. Context/impact dẫn tới `register`, `artifact`, `serve_results` và file UI; các consumer đó đã được đọc. PDG `loadRun` xác nhận STALE chỉ được chọn khi có last-good, refresh và transient; nhánh còn lại đi qua `dropView`. `check_document` có guard digest trước dựng view/CSV. Explain ba file không có finding, nhưng không dùng kết quả rỗng làm chứng minh an toàn.

Giới hạn graph: results_app có 3 receiver chưa resolve; process extraction có budget truncation và cross-language field gaps. Đã bù bằng source và HTTP/JS thực thi. Bằng chứng chính là hành vi quan sát được, không phải risk label của graph. Có thêm một lens độc lập đọc serving/runtime; không tìm thấy P1/P2 mới. Code không thêm abstraction hay dependency ngoài yêu cầu của gói.

## AC và phần còn thiếu

| AC | Kết quả hiện có | Còn thiếu |
| --- | --- | --- |
| ZER-11 AC-01 | Đạt kiểm offline/UI; không còn KPI giả ở đường kết quả | CI/merge/nghiệm thu chủ dự án |
| AC-02 | Adapter, API, file và JS cùng artifact; fatal/transient đúng | Artifact B0 thật được chấm rồi hiển thị qua serve-results |
| AC-03 | Consumer/MANUAL/rules/AI và negative/positive control đạt offline; delta không sửa mode | Runtime BM trên image mới thuộc RT2 nếu cần cho G1; không suy fake thành heal/LLM thật |
| AC-04 = ZER-39 AC-01 | Profile/guard/probe config và kế hoạch nhất quán | H-RT1, review offline harness, quyền RT1, quan sát B0 thực và cleanup |

HPA chỉ tồn tại hoặc không kích hoạt không chứng minh HPA phục hồi. Nếu lượt chạy không có effect, phải giữ NO_EFFECT; thiếu coverage giữ MISSING/UNKNOWN. Controller hồi pod nhưng probe chưa đạt cũng không được coi là phục hồi nghiệp vụ. Không đổi F-01 để ép kết quả.

Giữ residual đã khai báo: pane dưới khoảng 610 px cuộn ngang; console H không phải O-console BM; B2/B3 chưa có producer. Không mở rộng fix-01 sang R3/R4. Bước tiếp theo là **chuẩn bị H-RT1 offline**, không phải gửi lại hai finding đã khép hoặc xin chạy lab khi harness chưa có.

Không lab, Docker/build, model/API, commit/push/PR/merge, Linear write hay nhắn chat khác. Note chỉ append, NOW chỉ prepend. Writer source giữ nguyên; report/receipt ở thư mục retest này.
