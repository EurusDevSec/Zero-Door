# ZER-11 + ZER-39 — H-RT1 chuẩn bị offline (Claude)

**Verdict: READY_FOR_RUNTIME_REVIEW (offline).**

- Harness H-RT1 đã có, chạy được và kiểm được bằng fake.
- Runtime vẫn **NOT_RUN**: chưa có quyền RT1, chưa chạm cluster, Docker hay model.
- Đây không phải Done, không phải nghiệm thu AC-04 và không phải kết luận G1.
- Codex review harness này trước. Chỉ sau đó mới xin Hoàng quyền RT1, một lần gom.

## Baseline và phạm vi

- **Git:** HEAD `1694133`, nhánh `zer-10-independent-measurement`, không đổi nhánh, staged rỗng.
- **Snapshot trước sửa:** `scratch/zer11/claude-rt1/before/` + `before.json`, lấy bằng `snapshot_before.py` (script từ chối chạy lần hai).
  - Bản sao 6 file sẽ sửa.
  - Hash của 190 file chỉ đọc: toàn bộ `docs/evidence/ZER-11` (gồm fix-01, codex-review, codex-retest01), measurement, event_pipeline, nemesis, chaos-worker, manifests, tests.
  - 10/10 hash protected khớp.
  - Manifest fix-01: 26/28 file khớp. Hai file lệch là note và NOW, do Codex retest append/prepend, đúng dự kiến.
- **AC sống:** kết nối Linear của Claude trong phiên này không thấy ZER-11/ZER-39 (workspace khác), nên không đọc được. Gói dựa vào AC mà Codex đọc lại qua `linear_zero_door` ngày 21/10 ([codex-retest01.md](../codex-retest01.md)). Không sửa Linear.
- **Sửa:**
  - `infrastructure/scripts/verify-dashboard-baselines.py`: thêm `rt1`, `rt1-score`; SUITES thêm test mới.
  - `docs/runbooks/dashboard-and-baselines.md`: mục 2, 5, 5.2, 5.5; thêm 5.9; một hàng của bảng mục 6.
  - `.github/workflows/ci.yml`: thêm 1 dòng test vào mỗi job dashboard.
  - Note: append. NOW: prepend.
- **Thêm:** `infrastructure/scripts/r1_baseline_runtime.py`, `tests/test_dashboard_baseline_runtime.py` và thư mục này.
- **Không sửa:** scorer, contract, event_pipeline, chaos-worker, measurement_view, main.py, evidence cũ. [manifest-rt1.json](manifest-rt1.json) kiểm lại.

## Harness làm gì

Chi tiết ở runbook mục 5.9. Ma trận đầy đủ ở [rt1-matrix.json](results/rt1-matrix.json), in bằng `verify-dashboard-baselines.py rt1`.

| Pha | Thao tác ghi lên cluster (bảng `ACTIONS`; mọi thao tác ghi khác bị từ chối trước khi gọi kubectl) | Khôi phục |
| --- | --- | --- |
| P0 | Không: context, phiên bản kubectl, node Ready, image có trên node, UID/spec/replicas của Deployment, HPA lạ, Metrics API, ConfigMap/namespace trùng, ClusterIP frontend, `auth can-i` của hephaestus-sa (chỉ ghi lại) | — |
| P1 | Tạo namespace `zd-zer11-<nonce>`, ConfigMap harness, pod agent; **xóa ConfigMap harness với một UID sai**, phải bị Conflict; tạo ConfigMap profile; scale Gaia/Hephaestus về 0 | P7 |
| P2 | Run positive control riêng (O hợp lệ được ghi; DECISION RULES cho B0 bị quarantine MODE_VIOLATION); Deployment canary 0→1→0, manager `kubectl*` | Mất cùng namespace |
| P3 | Đúng **1** lần xóa pod frontend, có UID precondition, ngay sau ATTACK_REQUESTED đã được ack bền | Không (controller tạo lại pod là điều được quan sát) |
| P4 | Tạo 2 HPA, chờ `currentMetrics` (không có thì bỏ trial: HPA_NOT_MEASURABLE); pod tải trong namespace tạm (20 req/s, 10 kết nối, 180 s, ≤ 3600 request), xóa theo UID nếu chạy quá giờ | P7 |
| P5 | Không: RUN_CLOSED, seal, export H/O của run chính và run positive control; kéo tar về (chỉ nhận file thường) | — |
| P7 | Xóa HPA, ConfigMap, namespace theo UID; trả replicas target (chỉ khi cùng UID và spec) và Gaia/Hephaestus; đọc lại namespace đã vắng; so với P0 | — |
| P8 | Offline: CLI scorer, `register`, kết luận từng trial; lệnh `serve-results` | — |

**Image dùng thật (không build):**

- Image `zero-door/measurement:zer10-574a0c3a2dad`, id `sha256:baf75538e5b84408f7d53d55b3c8601cb0f6221b3703d3cf05a877dce82d8932`, chạy trên `k3d-zero-door-server-0`, `imagePullPolicy: Never`.
- Pod chạy non-root 65532, không token service account, drop ALL capabilities, giới hạn 500m/256Mi. `activeDeadlineSeconds` bằng trần tổng 3600 s.
- Measurement/event_pipeline trong image trùng từng byte với HEAD. Phiên này kiểm lại cả 21 file trong `runtime-01/attempt-03/source-manifest.json` (20 file measurement/event_pipeline cùng `acceptance.py`).

**Ngân sách** (đối chiếu [plan-check.json](results/plan-check.json); test `test_budgets_match_plan_check_and_pod_delete_cap` kiểm hai bên bằng nhau):

| Hạng mục | Giá trị |
| --- | --- |
| Probe mỗi trial | 995 s, 995 mẫu, 8955 request |
| Trường hợp xấu nhất theo plan | 3250 s |
| Trần tổng | 3600 s, harness tự giữ: P0–P5 phải xong trước 3300 s; P7 có 300 s dự trữ trong cùng trần, tính cả lệnh đang chờ |
| Giới hạn host mỗi trial | 995 + 10 (grace) + 10 (transaction) + 10 = 1025 s |
| Xóa pod | 1 |
| Request tải | ≤ 3600 |

Nếu trial dùng tới phần dư 30 s ở trường hợp xấu nhất thì run gặp `TOTAL_CAP` và dừng ở (d), không vượt trần. Không đổi F-01, gap hay timeout.

## Kiểm đã chạy

| Kiểm | Kết quả | Artifact |
| --- | --- | --- |
| Suite H-RT1, 17 test, trên Nemesis và Hephaestus production pins | 17/17 trên cả hai | [regressions.txt](results/regressions.txt), `tests/test_dashboard_baseline_runtime.py` |
| Mutant (12) + control + fail-before | 12/12 bị bắt; control 17/17; fail-before: không có module thì suite không import được (`ModuleNotFoundError`) | [mutants.json](results/mutants.json), [check_mutants.py](check_mutants.py) |
| Hồi quy: dashboard33, modes7, check_r1_baselines, CI boundary 6, plan-check, ma trận rt1, `--execute` thiếu quyền bị từ chối, Bandit 0, whitespace | OVERALL exit 0 | [regressions.txt](results/regressions.txt), [run_regressions.sh](run_regressions.sh) |
| Clean checkout: `git archive HEAD` + 24 file của các gói, không có `scratch/` | OVERALL exit 0; suite H-RT1 17/17 trên cả hai pins | [clean-checkout.txt](results/clean-checkout.txt), [clean_checkout.sh](clean_checkout.sh) |

**Ca kiểm và expected/actual** (actual ở log trên):

| Ca | Fake | Expected |
| --- | --- | --- |
| Controller + HPA phục hồi | Pod frontend Ready lại sau 0,6 s; tải làm frontend 503 khi 1 replica; HPA rescale lên 2 sau 0,3 s | Cả hai trial dừng ở (a). Một ATTACK/EFFECT/RECOVERY_VERIFIED/AUDIT_COVERAGE mỗi trial, đúng nguồn. O chỉ có CONTEXT. P8: `CONTROLLER_RECOVERY_OBSERVED` và `HPA_RECOVERY_OBSERVED`, MTTD/MTTR N/A, không lệch evaluator. Positive control: 1 quarantine. `serve-results` trả đúng artifact. Cleanup trả frontend 2→1 **sau** khi xóa HPA |
| HPA không kích hoạt | Tải không gây lỗi, không rescale | B0-HPA dừng (b) CONFIRMED_NO_EFFECT; `HPA_NOT_ACTIVATED_NO_EFFECT`; không có RECOVERY_VERIFIED; frontend UNCHANGED |
| Khoảng trống trong W_eff mà không có lỗi | Target chậm nhưng đạt khi có tải, nên mẫu cách nhau quá gap | (d) UNKNOWN_EFFECT `W_EFF_NOT_COVERED`; scorer cũng UNKNOWN_EFFECT; không phải NO_EFFECT |
| Không phục hồi, có phủ | Pod mới không bao giờ Ready | (c) HORIZON, scorer TIMEOUT `NOT_RECOVERED_WITHIN_CAP`. Trial HPA không tới được bước tạo lỗi (BASELINE_UNHEALTHY, không có pod tải) |
| Không phục hồi, không phủ | Request treo tới deadline | Scorer MISSING_PROBE, không TIMEOUT |
| Watcher lỗi 1,5 s | `get pods -n zero-door` lỗi | Không có AUDIT_COVERAGE cho B0-CTRL; `RECOVERED_BUT_ABSENCE_AUDIT_INCOMPLETE`; B0-HPA (watch hoạt động lại) có AUDIT_COVERAGE |
| Pod Gaia xuất hiện | Có người scale gaia lên 1 trong cửa sổ | Abort `ZERO_DOOR_COMPONENT_RUNNING`, (d), không có AUDIT_COVERAGE, không có trial HPA |
| Ack H hỏng | Archive H lỗi sau khi xóa pod | Abort PERSISTENCE; export H lỗi được ghi lại; P8 `MAIN_EXPORTS_MISSING`; outbox/journal được kéo về; cleanup sạch |
| UID target đổi | Frontend bị tạo lại (UID mới, 2 replica) | P7 `REFUSED_UID_CHANGED`, giữ nguyên 2 replica, không scale frontend; so với P0 báo UID_CHANGED; cleanup INCOMPLETE; namespace vẫn bị xóa |
| Ctrl+C trong trial và trong cleanup | Ngắt ở `status` sau lỗi và ở lệnh scale đầu tiên của P7 | Abort INTERRUPTED, trial (d) ABORTED, vẫn export và chấm (không TIMEOUT); bước dọn chạy lại một lần (attempts 2); sạch |
| Trần tổng | Đồng hồ host nhảy qua deadline chính | Abort TOTAL_CAP; cleanup xong trong phần dự trữ; elapsed ≤ trần |
| Trần mẫu | `max_samples` 12, target không phục hồi | (d) MAX_SAMPLES ≤ 12 mẫu; scorer MISSING_PROBE/UNKNOWN_EFFECT |
| Precondition UID không được tôn trọng | Fake xóa theo tên | Dừng ở P1 `UID_PRECONDITION_SELFTEST_FAILED`; không có thao tác ghi nào ở P2–P4 |
| Ranh giới | — | `rt1` không gọi subprocess; `--execute` thiếu quyền hoặc sai context bị từ chối; ghi ngoài `ACTIONS` hoặc sai tên bị từ chối trước kubectl; tar có `..` bị từ chối; tải dừng đúng ở `max_requests` |

## Lần chạy lỗi giữ lại

- **Suite chạy lần 1–4** (log trong `scratch/zer11/claude-rt1/run*.log`):
  - Lần 1: 6/15.
  - Lần 2: 10/15.
  - Lần 3: 12/15.
  - Lần 4: 14/15.
- **Các lỗi thật của harness tìm ra và đã sửa:**
  - Khóa `cleanup` trong receipt bị kết quả run ghi đè.
  - Một trial bị abort thì host không lưu summary.
  - Deadline tổng không được kiểm trước giới hạn riêng của trial.
  - Lệnh abort lỗi thì salvage bỏ luôn bước export.
  - P8 vẫn chấm khi thiếu export H.
  - RECOVERY_VERIFIED được phát trước `evidence_complete_at`; scorer bắt được (`published_before_evidence_complete`) trong ca end-to-end. Lỗi này sẽ xảy ra cả trên lab.
- **Các lỗi của fake hoặc assertion:** pod ban đầu dùng độ trễ của pod tạo lại; assertion về HPA ở ca timeout sai.
- **Sửa thêm từ tự review khi đọc `kubectl --help` (offline):**
  - `kubectl scale` không có `--field-manager`, manager có thể là `kubectl.exe`; điều kiện đổi thành tiền tố `kubectl`.
  - Thêm self-test UID precondition ở P1, vì hành vi `delete --raw -f` chỉ kiểm được trên cluster thật.
- **[mutants-attempt1.json](results/mutants-attempt1.json): 10/11.** Mutant `NO_EFFECT_WITHOUT_COVERAGE` sống sót vì chưa có ca khoảng trống trong W_eff mà không có lỗi. Đã thêm ca đó (lần thử riêng xác nhận nó bắt mutant), cùng mutant mới `WRITE_NAME_NOT_CHECKED`. Lượt cuối có 12 mutant.
- **[mutants-attempt2.json](results/mutants-attempt2.json): 11/12.** Mutant `WRITES_NOT_GUARDED` không chạy được vì pattern cũ không còn khớp sau khi siết `write()`. Đã sửa pattern; mutant không bị bỏ.
- **[regressions-attempt1.txt](results/regressions-attempt1.txt): OVERALL exit 1.** Bandit B108 báo `"/tmp/rt1"`, là đường mount emptyDir riêng của pod chứ không phải thư mục tạm dùng chung trên host. Đã tách thành hằng `AGENT_ROOT` một dòng, có `# nosec B108` kèm lý do. Các bước khác của lượt đó đều đạt.
- **[clean-checkout-attempt1.txt](results/clean-checkout-attempt1.txt): đạt**, nhưng chạy trên bản module trước khi tách hằng. Đã chạy lại trên bản cuối.
- **[regressions-attempt2.txt](results/regressions-attempt2.txt): một lỗi ngắt quãng chưa xác định.** Trên bản cuối, suite H-RT1 trên Nemesis có một lượt fail đúng 1 test (75,7 s, so với khoảng 80 s thường lệ). Script khi đó chỉ ghi dòng tóm tắt nên không biết test nào. Các lượt khác của cùng bản đều đạt: control mutant, 2 lượt clean checkout, Hephaestus trong cùng lượt hồi quy, 10 lượt chạy lặp (5 Nemesis, 5 Hephaestus) và lượt hồi quy cuối, tức 15/16 lượt. Script hồi quy giờ lưu toàn bộ output khi một bước fail (`*.failed.txt`). Chưa tìm ra nguyên nhân; xem residual 6.
- **Một lần sửa bằng `Path.write_text` trên Windows** đã đổi ba file sang CRLF. Đã đưa về LF trước mọi lần chạy được ghi lại.

## Residual / UNKNOWN (trước khi xin quyền RT1)

1. **Chưa kiểm được offline:**
   - Hành vi thật của `kubectl delete --raw -f` với UID precondition (self-test P1 dừng run nếu sai).
   - Định dạng Event/managedFields thật của k3s.
   - Thời gian kubectl thật; mỗi tick khoảng 5 lệnh, watch gap 10 s.
   - Tải 20 req/s có làm CPU frontend vượt 70% hay không. Nếu không, kết quả đúng là `HPA_NOT_ACTIVATED_NO_EFFECT`.
2. **Gateway H và O** chạy trong cùng một process agent, như runtime-01: archive, khóa và cổng riêng, nhưng không tách OS identity.
3. **AUDIT_COVERAGE** dựa trên lần đọc kubectl của host, được agent đóng dấu thời gian khi nhận (trễ tối đa bằng thời gian một lệnh exec). Một pod Gaia sống ngắn hơn một tick có thể lọt. B0 vẫn cần thêm bằng chứng: generation và replicas lúc so với P0, và O không nhận event nào.
4. **Một trial dừng ở (d) thì dừng cả run.** Đây là lựa chọn thận trọng, nên trial HPA có thể không chạy.
5. **Residual của các gói trước vẫn giữ:**
   - O-console cho BM (RT2).
   - Trang kết quả cuộn ngang dưới khoảng 610 px.
   - B2/B3 chưa có producer.
   - Khóa `results-reader` cho `serve-results` phải được sinh tay, ngoài repo.
6. **Suite có lỗi ngắt quãng 1/16 lượt, chưa xác định.** Các ca dùng thời gian thật đã rút gọn: gap 0,6 s, Δ 0,2 s, trên Windows. Cách đọc an toàn là coi một ca nào đó có thể nhạy với độ trễ lập lịch. Khi review, Codex nên chạy suite vài lần; nếu ca đó lộ ra, sửa fake hoặc nới thang thời gian của test, không nới logic harness.

Không chạy lab, Docker/build hay model. Không commit/push/PR, không đổi Linear.
