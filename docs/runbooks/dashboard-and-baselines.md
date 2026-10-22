# Dashboard kết quả và các chế độ đối chứng (ZER-11, ZER-39)

Runbook này mô tả phần đã làm, cách kiểm offline và kế hoạch runtime chờ duyệt. Hiện **chưa** chạy cluster, Docker hay model. Bằng chứng nằm ở [docs/evidence/ZER-11](../evidence/ZER-11/README.md).

## 1. Đã làm gì

- **KPI chỉ đến từ scorer.** Console vận hành (`/dashboard/index.html`) không còn tự tính MTTD/MTTR/uptime/success. Đường cũ ghép heal history với log, cộng `Math.random()`, có fallback 12.3s/100% và tính PARTIAL là thành công; toàn bộ đã bị bỏ. KPI chỉ hiện ở trang kết quả `/dashboard/results.html`.
- **Trang kết quả đọc đúng artifact của export.** Trang chỉ đọc `score.json` của run đã đóng và đã đăng ký. Đó là cùng thư mục với `incidents.csv` và `usage.csv` mà CLI ZER-10 ghi ra.
- **Adapter `nemesis/measurement_view.py`:**
  - Kiểm hash từng file theo registry, kiểm schema, run_id và group.
  - Từ chối JSON có NaN/Infinity, số tràn hay khóa trùng.
  - Tự sinh lại hai CSV từ `score.json` và từ chối nếu khác file.
  - Không nhận đường dẫn từ request: chặn traversal, symlink và mọi file ngoài root.
  - Lỗi chỉ trả mã lý do, không lộ path, khóa hay text exception.
  - `score.json` thiếu hoặc sai kiểu ở các trường adapter và trang dùng (digest export H/O, các mục KPI, milestones, findings vi phạm mode, leak, uptime, cột CSV) bị từ chối bằng mã 422 khi đăng ký và khi đọc, không thành lỗi 500. Giá trị bên trong các trường đó vẫn đi nguyên như scorer ghi.
- **Hiện đúng trạng thái thiếu dữ liệu:**
  - null hiện là "no data", không thành 0. EMPTY/NO_ELIGIBLE không có rate.
  - MISSING/UNKNOWN và N/A của B0 giữ nguyên.
  - Artifact lỗi thì không hiện số nào.
  - Poll lỗi vận chuyển hay upstream tạm thời (không có phản hồi, 502/503/504 trừ các lý do cấu hình của store) thì giữ số cũ với nhãn STALE kèm giờ lấy cuối.
  - Poll trả lỗi integrity/schema (422), mất quyền (401/403), run không còn đăng ký (404), registry/khóa sai cấu hình hay câu trả lời lệch run thì xóa số đã hiện, KPI và nút tải, rồi hiện lỗi. Mất quyền còn kết thúc phiên: dừng poll, cần kết nối lại.
  - Chuyển run hay đổi khóa thì bỏ câu trả lời muộn của run/khóa trước; đổi khóa xóa số cũ trước khi đọc danh sách run mới.
- **Độ trễ cập nhật** = thời điểm hiển thị − mốc event mới nhất đã chấm trên trục đồng hồ tham chiếu đã xác minh. `generated_at` chỉ là lúc scorer ghi file, không dùng làm mốc. Không có mốc đã xác minh thì độ trễ là UNKNOWN.
- **Quyền đọc kết quả tách riêng.** `/api/results/*` chỉ nhận GET với khóa `results-reader` (file `ZD_RESULTS_TOKEN_FILE`, purpose `results-reader`).
  - Khóa operator bị từ chối (401), còn khóa reader không mở API khác.
  - Hai khóa trùng secret thì trả 503 `KEY_SEPARATION`.
  - `nemesis-deployment.yaml` hiện không mount root kết quả hay khóa reader. Vì vậy operator BM không xem được S trong lúc run.
- **API cũ trả lỗi thật:**
  - `/api/status` trả null kèm trạng thái nguồn (OK/PARTIAL/ERROR) khi Prometheus lỗi. Giá trị 0 chỉ khi Prometheus trả 0.
  - `/api/heal-history` trả 503/502 khi upstream lỗi, không trả danh sách rỗng.
  - `/api/logs` ghi rõ nguồn nào lỗi.
  - `/api/chat` không còn ghép câu "reasoning" cố định: AI chưa có producer nên trả UNAVAILABLE.
  - Log và text không tin cậy được render bằng `textContent`.
- **Mode MANUAL=BM, RULES=B1, AI=B2.** B3 là AI_SINGLE, B0 là K8S_BASELINE. Mode lấy từ `group` của run trong `score.json` (nguồn raw), query không đổi được.
  - Consumer thật của Hephaestus chỉ tự quyết ở B1. Nhóm khác ghi một dòng audit vận hành `MODE_AUDIT … AUTO_DECISION_DISABLED_FOR_GROUP`; dòng này là log, không phải event O.
  - `/heal/trigger` chỉ nhận decision MANUAL của operator trong BM. Executor production vẫn khóa (`R1_EXECUTOR_DISABLED`).
  - Seam `R1_EXECUTOR` chỉ test gán. Khi có executor giả, mỗi decision chỉ cho một action; replay trả kết quả cũ.
- **Profile B0/HPA** ở `infrastructure/manifests/r1-baselines.yaml` gồm ConfigMap mô tả nhóm và 2 HPA `*-hpa-r1`. Đây là profile tùy chọn: không đổi lab mặc định và không có script setup nào áp nó.

## 2. Kiểm offline

Chạy từ gốc repo bằng Git Bash. Dùng interpreter có đúng pin production (CI cài từ `tests/requirements-command-{nemesis,hephaestus}.lock`). Ví dụ local:

```bash
ZD_PYTHON=scratch/zer12/production-nemesis/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-baselines.sh offline
```

```bash
python -B docs/evidence/ZER-11/fail_before.py --nemesis <python nemesis pins> --hephaestus <python hephaestus pins>
```

```bash
python -B docs/evidence/ZER-11/check_mutants.py --nemesis <python nemesis pins> --hephaestus <python hephaestus pins>
```

Regression của trang kết quả chạy chính `results.js` trong Node VM (không browser, không mạng). Test `StaticPages` gọi nó; chạy riêng:

```bash
node tests/results_page_vm.cjs
```

Harness H-RT1 (mục 5.9) có suite offline riêng, gọi từ `offline` và CI. Suite chạy chính mã orchestration của CLI với kubectl giả, target giả và thang thời gian rút gọn:

```bash
python -B tests/test_dashboard_baseline_runtime.py
```

`--help`, `offline`, `fixture-server`, `register`, `serve-results`, `plan-check`, `rt1` (không có `--execute`) và `rt1-score` không chạm cluster, Docker hay model. Kiểm browser cục bộ với dữ liệu SYNTHETIC:

```bash
ZD_PYTHON=scratch/zer12/production-nemesis/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-baselines.sh fixture-server --port 8711
```

Lệnh in URL `http://127.0.0.1:8711/dashboard/results.html`, file khóa reader SYNTHETIC và file điều khiển. Trong file điều khiển, `{"fail": true}` giả lập lỗi upstream để xem STALE; `{"delay": {"<run_id>": 4}}` làm run đó trả muộn để kiểm chuyển run.

`fixture-server` luôn tự sinh dữ liệu SYNTHETIC; không dùng nó cho run thật. Root của một run thật được phục vụ bằng `serve-results` (mục 5.5, P8).

## 3. Đăng ký run sau khi đóng

Chỉ đăng ký sau RUN_CLOSED, khi scorer đã ghi output mới bằng `python -m measurement score`.

1. Chép thư mục output vào root S cố định; tên thư mục khớp `[A-Za-z0-9][A-Za-z0-9._-]*`.
2. Chạy lệnh dưới. Lệnh kiểm CSV đúng bằng `measurement.output` của chính `score.json`, rồi thêm entry `CLOSED` với SHA-256 của ba file vào `registry.json`. Run hoặc thư mục đã có thì bị từ chối, không ghi đè.

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py register --root <root S> --dir <tên thư mục>
```

Dashboard không quét root: run không có trong registry thì không được liệt kê hay phục vụ.

## 4. Ma trận nhóm (contract 7.4, ZER-8 4.1)

| Nhóm | Mode | Ai quyết định | Ai thực thi | Thành phần ZERO DOOR chạy | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| B0 | K8S_BASELINE | Không ai | Deployment/ReplicaSet controller (luôn bật) và HPA `*-hpa-r1` | Không có Gaia hay Hephaestus | Detector tắt nên MTTD/MTTR/reaction là N/A. Mọi DECISION/LLM_CALL/GUARD_VERDICT/HEAL_STARTED/API_ACCEPTED/ACTION_COMPLETED là MODE_VIOLATION |
| BM | MANUAL | `operator_console` | Operator qua `/heal/trigger` (executor R1 khóa) | Gaia, Hephaestus | Không tự quyết; decision RULES trong BM bị gateway quarantine |
| B1 | RULES | `decision_rules` | Executor chung (R1 khóa) | Gaia, Hephaestus | Positive control của consumer |
| B2 | AI | `decision_llm`, fallback RULES | Executor chung | Chưa có producer | Dashboard ghi AI unavailable, không gọi model |
| B3 | AI_SINGLE | `decision_single_llm`, fallback RULES | Executor chung | Chưa có producer | Chỉ khi cấu hình thật, không giả là B2 |

Mọi nhóm dùng cùng target, probe, kế hoạch fault đã khóa và giới hạn scale 1..3, bằng `MAX_REPLICAS` của Hephaestus. Probe và recorder là thành phần H; observer không nhận lệnh điều khiển hay ground truth.

## 5. Kế hoạch runtime chờ duyệt (G-ZER11-RT1)

Chưa được phép chạy. Codex review kế hoạch này và harness H-RT1 (5.9) trước, sau đó Hoàng duyệt một lần cho đúng gói này. Lệnh `runtime-preflight` từ chối nếu thiếu `--runtime-approval` và chỉ đọc; `rt1` không có `--execute` chỉ in ma trận. Mọi con số ở 5.3 do `plan-check` tính và kiểm; sửa số thì sửa `RT1` trong `verify-dashboard-baselines.py`, chạy lại lệnh và test.

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py plan-check
```

### 5.1 Mục tiêu và giới hạn

- **ZER-39/ZER-11 AC-04:**
  - Trong B0, Kubernetes tự phục hồi: tách phần do Deployment controller (trial B0-CTRL) và phần do HPA (trial B0-HPA).
  - ZERO DOOR không phát lệnh heal, có coverage và positive control.
  - Probe độc lập vẫn đo được.
- **AC-02 runtime:** trang kết quả đọc artifact của chính run này qua `serve-results` và khớp export.
- **P6 (BM trên image mới) KHÔNG thuộc RT1.** RT1 không build image, không bật Gaia/Hephaestus và không xin xóa pod lần hai. P6 cần một gói riêng (G-ZER11-RT2) với các điều kiện ở 5.7.
- **Không làm:** pilot, vector R2/R3, LLM, provider trả phí, sửa target để "chữa hộ". Không dùng việc operator scale về làm bằng chứng tự phục hồi. Không đổi scorer, F-01 hay criteria để che giới hạn thời gian.

### 5.2 Context, tài nguyên, ownership

- **Context:** chỉ `k3d-zero-door`. Cluster khác thì dừng.
- **Đọc trước (P0, lưu bằng `runtime-preflight --output <file mới>`):**
  - UID, generation và spec hash của mọi Deployment trong `target-app`.
  - Replicas hiện tại (runtime-01 ghi frontend 1, checkoutservice 3; phải đọc lại, không giả định).
  - HPA ở mọi namespace và trạng thái `v1beta1.metrics.k8s.io`.
  - Deployment/RBAC của Gaia và Hephaestus trong `zero-door`, kèm replicas để khôi phục.
- **Tạo mới, nhãn `zero-door.io/run=<run_id>`, ghi UID ngay khi tạo, xóa ở P7 theo tên + nhãn + UID:**
  - Namespace tạm `zd-zer11-<8 hex>`: gateway/recorder H và O (production gateway như ZER-10 runtime-01, ack 201), harness B0, probe, một pod tải HTTP, một Deployment test `zd-scale-canary` (0 replica) cho positive control.
  - ConfigMap `zd-r1-baseline-profiles` trong `zero-door` (P1).
  - HPA `frontend-hpa-r1`, `cartservice-hpa-r1` trong `target-app`, chỉ áp ở đầu P4 để trial B0-CTRL không có HPA.
- **Sửa tạm, khôi phục theo UID:**
  - Scale `gaia` và `hephaestus` trong `zero-door` về 0 trong toàn cửa sổ B0, rồi trả về replicas đã đọc ở P0.
  - Sau khi xóa HPA, trả `spec.replicas` của frontend/cartservice về baseline nếu HPA đã đổi. Đây là cleanup, không phải bằng chứng phục hồi.
- **Image:** chỉ image đã có (target, gateway, probe ZER-10). Không Docker build.
- **Root S (offline, trên host):** `scratch/zer11/runtime-<nonce>/results/`, tạo mới, không trùng run cũ. Khóa `results-reader` sinh mới cho run, ghi file ngoài repo, không in ra.

**Harness:** H-RT1 ở `infrastructure/scripts/r1_baseline_runtime.py`, chạy qua `verify-dashboard-baselines.py rt1` (mục 5.9). Harness phát RUN_STARTED/RUN_CONTEXT/TRIAL_CONTEXT (`group=B0`, `config_ref` = SHA-256 của `r1-baselines.yaml`), TRIAL_STARTED/TRIAL_ENDED, ATTACK_REQUESTED/ATTACK_STOPPED (vai `harness`), EFFECT_EVALUATED (vai `effect_evaluator`), RELAPSE/RECOVERY_VERIFIED (vai `recovery_evaluator`, dùng `measurement.recovery.RecoveryMonitor`) và AUDIT_COVERAGE. Nó tự dừng trial theo 5.4 và giữ trần 5.3. Codex review harness trước khi xin quyền.

### 5.3 Trần và budget (output của `plan-check`)

F-01 là bộ minh họa ZER-32 mục 3.6, dùng làm input PILOT, không đổi: Δ = 1 s, K = 3, S = 30 s, gap = 2 s, L = 2000 ms, cap_rec = 600 s, W_eff = 300 s.

| Hạng mục | B0-CTRL | B0-HPA | Tổng / trần |
| --- | --- | --- | --- |
| Lỗi | Xóa 1 pod frontend | Tải GET frontend 180 s (20 req/s, 10 kết nối) | 1 lần xóa pod; 3600 request tải |
| Warm-up (ngoài cửa sổ trial) | 30 s | 30 s | — |
| Cửa sổ trial tối đa | 965 s = 30 baseline + 300 W_eff + 600 cap_rec + 30 S + 5 | 965 s | — |
| Probe tối đa (warm-up + trial) | 995 s, 995 mẫu, 8955 request | 995 s, 995 mẫu, 8955 request | 1990 mẫu, 17910 request; trần 1000 mẫu/trial |
| Mẫu tối thiểu để xác minh recovery | K + S/Δ = 33 mẫu đạt liên tục | 33 | — |
| Pha khác (P0, P1, P2, chờ HPA, seal/export, P7) | — | — | 180 + 300 + 180 + 120 + 180 + 300 s |
| Thời gian | — | — | worst case 3250 s; trần 3600 s, kể cả cleanup |

- Một mẫu probe là một giao dịch checkout (`probe.py` `sample`), tối đa 9 request. Plan probe mỗi trial đặt `budget.max_duration_s` 995, `max_samples` 995, `max_requests` 8955, `grace_s` 10.
- Thường trial ngắn hơn nhiều: pod frontend tạo lại trong vài chục giây, nên B0-CTRL dừng sớm ở mốc (a) dưới đây. Trần là worst case, không phải dự kiến.
- Không thêm fault nào khác. Không gọi model.

### 5.4 Khi nào một trial kết thúc

Harness dừng trial ở mốc đến trước trong các mốc sau. Mỗi mốc ứng với đúng một kết quả của scorer; không có mốc nào đổi thiếu dữ liệu thành TIMEOUT hay PASS.

| Mốc | Điều kiện | Scorer chấm |
| --- | --- | --- |
| (a) Phục hồi xác minh | `evidence_complete_at` của RECOVERY_VERIFIED + 5 s | RECOVERED (B0: RECOVERED_UNDETECTED, MTTD/MTTR N/A) |
| (b) Không có hiệu ứng | Mẫu phủ liên tục [T_req, T_req + 300 s] không có lỗi | CONFIRMED_NO_EFFECT, rời N |
| (c) Hết cap_rec | Mẫu phủ liên tục tới T_eff + 600 s cộng S cho ứng viên đúng trần (T_eff + 635 s) | TIMEOUT |
| (d) Dừng sớm | Abort 5.5, trần tổng 3600 s, hoặc probe hết budget | Cửa sổ không đủ phủ: MISSING_PROBE hoặc UNKNOWN_EFFECT, ghi là chưa hoàn tất |

Khoảng trống > gap = 2 s trong lúc target sập (giao dịch timeout 10 s, slot bị bỏ như runtime-01) làm cửa sổ không phủ liên tục. Khi đó scorer chấm MISSING_PROBE chứ không phải TIMEOUT. Đây là kết quả đúng, không chỉnh gap hay timeout để tránh.

### 5.5 Các pha và thao tác

| Pha | Việc | Thao tác ghi lên cluster |
| --- | --- | --- |
| P0 | Preflight chỉ đọc: context, UID/spec, không có HPA nào trỏ frontend/cartservice (có thì dừng), Metrics API Available, node Ready, `kubectl auth can-i` của `zero-door:hephaestus-sa` với `patch deployments/scale` và `delete pods` ở `target-app` | Không |
| P1 | Tạo namespace tạm; ConfigMap `zd-rt1-harness` chứa đúng file harness; **tự kiểm precondition**: xóa ConfigMap đó với một UID sai phải bị từ chối (Conflict) và ConfigMap phải còn, nếu không thì dừng trước khi chạm target; pod agent (gateway H/O, harness, probe), agent báo SHA-256 file phải trùng host; áp ConfigMap profile; scale Gaia và Hephaestus về 0 và xác nhận 0 pod | 1 namespace + 2 đối tượng trong đó; 1 lệnh xóa bị từ chối có chủ đích; 1 ConfigMap; 2 lệnh scale |
| P2 | Positive control trước trial, trong **một run B0 riêng** (ngoài cohort chính; export riêng `pc-export-H/O`, chấm riêng ở P8): (1) harness phát một event O hợp lệ, thấy nó trong archive O; (2) gửi một DECISION `decision_rules` cho run B0 đó qua gateway, phải bị quarantine MODE_VIOLATION; (3) `kubectl scale` `zd-scale-canary` 0→1→0. Đọc với `--show-managed-fields=true`: `spec.replicas` phải do subresource `scale` sở hữu, với manager bắt đầu bằng `kubectl` (kubectl/kubectl.exe, theo user agent); `kubectl-create` không tính; không có `horizontal-pod-autoscaler`; pod mới do `replicaset-controller` tạo. Host tự quyết (1)+(2) từ ba dữ kiện đã ghi (event O được ghi, DECISION `REJECTED`, `MODE_VIOLATION`), không dựa vào `ok` của lệnh gọi agent. Thiếu một dữ kiện là `POSITIVE_CONTROL_FAILED`, trước mọi ghi P2/P3/P4 | 1 Deployment và 2 lệnh scale trong namespace tạm |
| P3 | B0-CTRL: warm-up, baseline, harness xóa đúng 1 pod frontend (ATTACK_REQUESTED → delete → ATTACK_STOPPED), ghi Events, UID pod trước/sau, trạng thái ReplicaSet; dừng theo 5.4 | 1 lần xóa pod |
| P4 | Áp 2 HPA, chờ `currentMetrics` (tối đa 120 s; không có thì ghi "HPA không đo được" và bỏ trial). B0-HPA: ATTACK_REQUESTED, pod tải chạy 180 s trong trần, ATTACK_STOPPED; ghi `desiredReplicas`/`currentReplicas` và Event `SuccessfulRescale`; dừng theo 5.4. Không tự scale về | 2 HPA; pod tải trong namespace tạm |
| P5 | RUN_CLOSED, seal, export H/O của run chính và run positive control; host kéo về bằng `kubectl exec ... tar` (giải nén chỉ nhận file/thư mục thường) | Không |
| P7 | Cleanup, luôn chạy kể cả khi abort: xóa HPA và ConfigMap theo tên + nhãn + UID; trả frontend/cartservice về replicas baseline; trả Gaia/Hephaestus về replicas P0; xóa namespace tạm rồi đọc lại xác nhận đã vắng; diff UID/spec với P0, chỉ được khác replicas trong lúc chạy | Xóa đúng đối tượng đã tạo; ≤ 4 lệnh scale khôi phục |
| P8 (offline, sau P7) | Chấm và hiển thị, không cần cluster: harness tự chạy CLI scorer và `register` khi có đủ export H và O; thiếu một trong hai thì ghi `MAIN_EXPORTS_MISSING`, không chấm. Lệnh tay ở dưới | Không |

Nếu HPA không scale vì tải không vượt 70% CPU thì ghi đúng "HPA không kích hoạt", không tuyên bố đã kiểm HPA. Nếu B0-HPA có hiệu ứng mà phục hồi chỉ xảy ra sau ATTACK_STOPPED, không có `SuccessfulRescale` trước đó, thì phục hồi là do tải dừng, không quy cho HPA.

**P8, chấm và hiển thị trên host (offline, loopback):**

```bash
python -m measurement score --h-export <export H> --o-export <export O> --output <root S>/<thư mục run> --required-flow checkout
```

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py register --root <root S> --dir <thư mục run>
```

```bash
ZD_PYTHON=scratch/zer12/production-nemesis/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-baselines.sh serve-results --root <root S tuyệt đối> --reader-key-file <khóa results-reader> --port 8712 --receipt <file mới>
```

`serve-results` phục vụ đúng root đã cho: không sinh fixture, không chấm, không ghi. Nó chỉ mở `results.html`, `results.js` và GET `/api/results/*`; mọi route khác trả 404 trước khi tới mã Nemesis. Không có consumer Kafka, Prometheus, Hephaestus hay model. Khi dừng, lệnh so hash mọi file trong root lúc đầu và lúc cuối, ghi vào receipt. Có thay đổi thì exit 5. So KPI, bảng incident và hash trên trang với `score.json`/CSV, rồi chụp màn hình.

### 5.6 Dừng khẩn

Dừng ngay, chạy P7 và ghi lại khi gặp một trong các trường hợp sau. Trial đang chạy kết thúc ở mốc (d), tức là chưa hoàn tất.

- Context sai, hoặc HPA lạ trỏ cùng target.
- Node NotReady.
- Chạm trần thời gian, mẫu, request hay số lần xóa pod.
- Gaia/Hephaestus có pod trong cửa sổ B0, hoặc có event DECISION/HEAL được nhận (không phải bị quarantine).
- Lỗi persistence của outbox hoặc journal.

Target không phục hồi trong cap_rec **không** phải abort. Trial dừng ở mốc (c) và được chấm TIMEOUT nếu đã phủ liên tục. P7 vẫn chạy, nhưng không ai chữa target bằng tay trước khi export xong.

### 5.7 P6 / G-ZER11-RT2 (ngoài RT1)

Gói thực hiện đã chuẩn bị ở **mục 6**. Chỉ cần build/import **một image Hephaestus**; O-console tách riêng nên không cần build hoặc thay Nemesis. Dùng quan sát HTTP thật được ghi rõ nguồn thay vì sửa cấu hình Gaia đang chạy. Đây là kiểm ranh giới chế độ, không phải nghiệm thu detector Gaia, vận hành BM mù hay KPI nghiên cứu. Quyền RT1 không áp dụng cho RT2.

### 5.8 Bằng chứng và cách đọc

| Kết luận | Bằng chứng cần có | Không đủ nếu chỉ có |
| --- | --- | --- |
| B0 không phát heal | Gaia/Hephaestus 0 pod suốt cửa sổ (đọc trước/sau, Events); export O không có event cấm ngoài quarantine; AUDIT_COVERAGE phủ cửa sổ; positive control P2 cho thấy vi phạm và thao tác scale đều sẽ bị thấy | "Không thấy log" |
| Controller tự phục hồi | Pod UID mới do `replicaset-controller`; probe RECOVERED_UNDETECTED theo 5.4 (a), TotalRecovery tính từ effect | Thấy pod Running |
| HPA tự phục hồi | `SuccessfulRescale` từ `horizontal-pod-autoscaler` trước mốc phục hồi, replicas tăng trong trial, probe đạt | HPA tồn tại trong manifest |
| Trial chưa hoàn tất | Mốc (d) và lý do được ghi; scorer ra MISSING_PROBE/UNKNOWN_EFFECT | Gọi là TIMEOUT hay PASS |
| Dashboard = export | Receipt `serve-results` (`root_unchanged`), hash ba file = registry; KPI và incident trên trang = `score.json`/CSV; chụp màn hình | Hai consumer cùng đọc một số sai |

### 5.9 Harness H-RT1 (thực thi)

Một file `infrastructure/scripts/r1_baseline_runtime.py`, hai nửa:

- **Host (Orchestrator):** chạy P0–P7 rồi P8.
  - Mọi lệnh là argv kubectl có `--context k3d-zero-door` và `--request-timeout`, không qua shell.
  - Mọi thao tác ghi đi qua một hàm duy nhất và bị từ chối nếu không có trong bảng `ACTIONS` (in bằng `rt1`).
  - Xóa dùng `kubectl delete --raw <đường dẫn> -f -`, DeleteOptions có `preconditions.uid` đi qua stdin nên không lệnh dọn nào phụ thuộc đĩa host. Scale dùng `--current-replicas` và `--resource-version`.
  - Mọi đối tượng tạo ra đều mang nhãn run. Ý định tạo được ghi **trước** khi gửi. Nếu API đã tạo nhưng mất phản hồi (timeout, đứt kết nối), harness đọc lại theo tên + namespace + nhãn để lấy UID, ngay lúc đó và lần nữa ở P7, rồi xóa theo UID.
    - Không bao giờ xóa theo tên.
    - Tên bị đối tượng không mang nhãn run giữ thì để nguyên (`NAME_HELD_BY_OTHER_OBJECT`) và cleanup là `INCOMPLETE`.
    - Không đọc được quyền sở hữu thì cũng `INCOMPLETE`.
  - Đọc quyền sở hữu field (`managedFields`) luôn kèm `--show-managed-fields=true`, vì `kubectl get` mặc định bỏ trường này.
  - Dừng khi chạm deadline tổng (trần 3600 s), tính cả lệnh đang chờ. P7 có phần dự trữ riêng 300 s trong cùng trần.
  - Lỗi bất ngờ ở host (đĩa đầy, lỗi code, JSON hỏng) là một abort `UNEXPECTED (...)` như mọi abort khác. P7 nằm trong `finally` nên vẫn chạy.
- **Pod (Agent):**
  - Chạy trong pod tạm, từ image ZER-10 sẵn có `zero-door/measurement:zer10-574a0c3a2dad` (`sha256:baf75538…8d32`, `imagePullPolicy: Never`, không build). Measurement/event_pipeline trong image trùng từng byte với cây hiện tại (`runtime-01/attempt-03/source-manifest.json`).
  - File harness được mount chỉ đọc từ ConfigMap; agent báo SHA-256 của nó và host so.
  - Agent giữ gateway H/O production: archive và khóa riêng cho từng plane, khóa sinh mới chỉ trong bộ nhớ, ack 201 bền. Ngoài ra là ProbeRunner ZER-10 cho từng trial, bộ đánh giá effect, `RecoveryMonitor` và AUDIT_COVERAGE.
  - Host chỉ nói chuyện với agent qua `kubectl exec ... call <json>`.

**Mốc và nguồn:**

- T_req là `ts_event` của ATTACK_REQUESTED. Event này được phát và ack bền **trước** khi xóa pod hay tạo pod tải.
- EFFECT_EVALUATED (`zd-rt1-effect/0`):
  - Mẫu lỗi đầu tiên trong [T_req, T_req + W_eff] cho CONFIRMED.
  - Mẫu phủ liên tục cả cửa sổ mà không có lỗi cho CONFIRMED_NO_EFFECT.
  - Cửa sổ có khoảng trống, hoặc trial dừng trước khi quyết được, cho UNKNOWN_EFFECT.
- Bộ đánh giá chỉ dùng mẫu probe đã được gateway H ack bền, theo đúng thứ tự sequence.
- RECOVERY_VERIFIED chỉ phát khi đồng hồ harness đã qua `evidence_complete_at`.
  - Lý do: `t_end` của mẫu là giờ wall lúc bắt đầu cộng thời gian monotonic, nên có thể vượt số đọc wall ngay sau đó.
  - Nếu phát sớm hơn, scorer báo `published_before_evidence_complete`.
- Controller tạo pod mới, hay HPA scale, không phải là mốc phục hồi. Phục hồi chỉ đến từ mẫu probe.
- Harness không phát DETECTED, DECISION hay HEAL trong run chính.

**Theo dõi vắng mặt (AUDIT_COVERAGE):**

- Mỗi vòng poll, host đọc pod Gaia/Hephaestus và trạng thái node, rồi gửi kết quả cho agent. Agent đóng dấu thời gian bằng đồng hồ harness.
- AUDIT_COVERAGE (`complete: true`, phạm vi `B0_ZERO_DOOR_ABSENCE`) chỉ được phát khi đủ ba điều kiện:
  - Mọi lần đọc đều thành công và cho 0 pod.
  - Không có khoảng trống quá 10 s, kể cả ở đầu và cuối trial.
  - Archive O của run chính không nhận event nào ngoài RUN_CONTEXT/TRIAL_CONTEXT.
- Một lần đọc lỗi thì không phát AUDIT_COVERAGE. Khi đó P8 ghi `RECOVERED_BUT_ABSENCE_AUDIT_INCOMPLETE`, không kết luận "không ai heal".

**Dừng và dọn (5.4, 5.6):**

- Trial kết thúc ở (d) thì cả run dừng. (d) gồm: abort, budget probe, ngắt, hoặc khoảng trống trong W_eff.
- Khi đó trial đang mở được đóng lại rồi run được export:
  - ATTACK_STOPPED `ABORTED` nếu lỗi chưa dừng.
  - TRIAL_ENDED `ABORTED`.
- P7 luôn chạy, theo thứ tự:
  1. Kéo bằng chứng.
  2. Xóa HPA theo UID.
  3. Trả replicas của target. Chỉ làm với đúng đối tượng có cùng UID và cùng spec trừ replicas; khác thì để nguyên và ghi `REFUSED_UID_CHANGED`/`REFUSED_SPEC_CHANGED`.
  4. Trả replicas của Gaia/Hephaestus.
  5. Xóa ConfigMap profile.
  6. Xóa namespace, đọc lại để xác nhận đã vắng.
  7. So với P0.
- Ctrl+C trong một bước dọn thì bước đó chạy lại một lần. Các bước đều idempotent nhờ precondition.
- Mỗi bước được cô lập lỗi. Trong bước xóa HPA và bước trả replicas, từng đối tượng cũng được cô lập. Một lỗi (API, đĩa host, lỗi code) làm bước đó `FAILED` nhưng các bước sau vẫn chạy trong deadline.
- Run chỉ đóng một lần; lần kéo bằng chứng sau đó chỉ thử lại `tar`. Không kéo được thì bước 1 là `FAILED` (`EVIDENCE_NOT_PULLED`), không ghi DONE.
- Receipt được ghi sau cùng, theo kiểu best effort. Không ghi được thì `run()` vẫn trả kết quả kèm `RECEIPT_NOT_WRITTEN`.
- Bước 7 có cả namespace tạm, vì namespace này vắng ở P0.
- Agent ghi lại thời gian ACK, số lần thử lại và trạng thái của từng control event (`control_deliveries` trong receipt của agent). Một event không được ack bền trong hạn `grace_s` (10 s) thì run dừng ở `PERSISTENCE`, kể cả khi gateway đã ghi event đó nhưng trả lời quá muộn.

**P8, đọc kết quả:** nhãn của scorer cộng với bằng chứng cluster cho ra kết luận của trial.

Event được giữ cùng UID của đối tượng. Một Event cũ hơn, của đối tượng khác cùng tên (ví dụ của lượt chạy trước) hay chỉ là downscale đều không được tính.

Positive control P2 lưu ownership ngay sau từng bước canary 0→1 và 1→0, kèm UID/resourceVersion. Trên k3s v1.31.5 đã quan sát ownership của `spec.replicas` có ở 1 nhưng biến mất khi về 0; không chỉ đọc trạng thái cuối. Vẫn bắt buộc thấy manager kubectl qua subresource `scale` và controller Event, không thay bằng suy luận từ lệnh gửi thành công. Preflight bỏ qua image inventory có `names: null` nhưng vẫn đòi image cụ thể có mặt; dry-run manifest đọc đủ từng JSON document do kubectl trả.

- B0-CTRL được kết luận `CONTROLLER_RECOVERY_OBSERVED` chỉ khi đủ các điều kiện:
  - Nhãn RECOVERED_UNDETECTED.
  - AUDIT_COVERAGE đủ.
  - Có một pod Ready mới, với UID chưa có trước lúc xóa, thuộc đúng ReplicaSet (cùng UID) của pod đã xóa.
  - Event `SuccessfulCreate` của chính ReplicaSet đó, do `replicaset-controller` phát, nêu tên pod mới này.
  - Có đủ T_req, T_rec và thời gian Event. Event phải lớn hơn T_req − 1 s và sớm hơn T_rec quá 1 s; dung sai tại T_req chỉ để bù Event core làm tròn xuống giây, giống nhánh HPA. Thiếu thời gian, chồng lấn độ phân giải hoặc Event sau phục hồi không đủ để quy kết lần phục hồi nghiệp vụ cho controller.
  - Thiếu một trong các điều trên thì là `RECOVERED_CONTROLLER_EVIDENCE_MISSING`.
- B0-HPA được kết luận `HPA_RECOVERY_OBSERVED` chỉ khi có Event `SuccessfulRescale` thỏa cả bốn điều:
  - Của đúng HPA tạo trong run này (cùng UID), do `horizontal-pod-autoscaler` phát.
  - `New size` lớn hơn số replicas lúc T_req.
  - Không sớm hơn T_req quá 1 s (Event core có độ phân giải giây, làm tròn xuống).
  - Sớm hơn T_rec quá 1 s.
- Các kết luận khác:
  - `HPA_NOT_ACTIVATED_NO_EFFECT`: chỉ khi có bằng chứng cluster và HPA của trial không scale-up.
  - `HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS`: chỉ có Event cũ, của UID khác, downscale, không có thời gian, hoặc trước T_req.
  - `RECOVERED_HPA_EVIDENCE_MISSING`: không thu được Events hoặc danh tính trial.
  - `RESCALE_ORDER_AMBIGUOUS_OR_AFTER_RECOVERY`.
  - `RECOVERED_AFTER_LOAD_STOP_NOT_HPA`.
  - `RESCALE_NOT_BY_HPA`.
  - `NOT_RECOVERED_WITHIN_CAP` (TIMEOUT).
  - `INCOMPLETE:<nhãn>`.

**Chạy (sau khi có quyền):**

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py rt1
```

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py rt1 --execute --runtime-approval <tham chiếu quyền Hoàng> --context k3d-zero-door --out <thư mục mới ngoài repo>
```

`--execute` chỉ ghi lại tham chiếu quyền; nó không cấp quyền. Thư mục `--out` nhận:

- `preflight.json`.
- `receipt.json`: pha, mọi thao tác ghi, cleanup, so với P0, P8.
- `cluster-evidence.json` và `kubectl-calls.json`.
- `raw/`: export H/O, outbox, journal, receipt của agent.
- `results/`: root S đã đăng ký.

Sau đó phục vụ `results/` bằng `serve-results` (P8), với một khóa `results-reader` sinh mới ngoài repo. Chấm lại offline:

```bash
python -B infrastructure/scripts/verify-dashboard-baselines.py rt1-score --raw <out>/raw --root <root S mới>
```

**Kiểm offline** (`tests/test_dashboard_baseline_runtime.py`, chạy trong `offline` và CI):

- Phần giả:
  - kubectl: cluster trong bộ nhớ có ReplicaSet controller, HPA và Events (kèm UID đối tượng). Fake mô phỏng các mặc định thật mà review chỉ ra: `get` bỏ managedFields nếu không có cờ, quyền sở hữu field chuyển sang người scale qua `/scale`, `AlreadyExists`, DeleteOptions đọc từ stdin.
  - Khả năng truy cập target: fake Boutique ZER-10 trên loopback, bị cắt khi không có pod frontend Ready.
  - Thang thời gian tính bằng giây (bản SYNTHETIC của RT1).
- Phần thật: harness, gateway và archive, ProbeRunner, RecoveryMonitor, CLI scorer, `register` và app `serve-results`.

Ca kiểm:

- Controller và HPA phục hồi, chấm và phục vụ.
- HPA không kích hoạt.
- Không phục hồi khi có phủ cho TIMEOUT; không phục hồi khi không phủ cho MISSING_PROBE.
- Watcher lỗi.
- Pod Gaia xuất hiện.
- Ack H hỏng.
- UID target đổi.
- Ctrl+C trong trial và trong cleanup.
- Chạm trần tổng.
- Chạm trần số mẫu.
- Precondition UID không được tôn trọng.
- Ghi ngoài `ACTIONS`.
- Tar không an toàn.
- Trần request của tải.
- ACK control trễ hơn hạn: run dừng ở `PERSISTENCE` (negative control của N1).
- Fake ở chế độ hang tôn trọng deadline sống (callable) của request dọn `POST /cart/empty` (N1).
- Thang thời gian của fake: hạn ACK control (`grace_s` 10 s) và ngưỡng ACK probe (`ack_stall_s` 15 s) giữ giá trị production, vì một lần nghẽn I/O của host không co lại theo thang giây. Các tham số khác vẫn nén, nên một lần nghẽn fsync vài giây trên máy chạy test (đã đo tới 10,8 s) vẫn có thể làm một ca fail. Ca đó phải được phân loại bằng `docs/evidence/ZER-11/rt1-fix-01/n1/`, không được chạy lại cho tới khi xanh.
- Gói rt1-fix-01 (lớp `Findings`, một ca cho mỗi lỗi RT1-01…05):
  - Đĩa host đầy ở pha chính, và từ cleanup trở đi; lỗi bất ngờ trong trial và trong một bước dọn.
  - Manager sai vẫn bị bắt; lần đọc canary có cờ managedFields.
  - Positive control fail (mất ACK riêng DECISION, sai classification, DECISION được nhận) dừng trước target.
  - Mất phản hồi create (namespace, HPA, pod tải, ConfigMap profile), tên bị đối tượng khác giữ, ConfigMap bị thay UID.
  - Event cũ, UID khác, downscale, trước T_req, sau T_rec.
- Đặt `RT1_KEEP=<thư mục>` để giữ file của ca fail (thư mục out, gốc agent với outbox và archive, `kept.json`) trước khi test dọn. Thêm `RT1_KEEP_ALL=1` để giữ mọi ca.

Chưa kiểm được offline:

- Hành vi thật của `kubectl delete --raw -f -` (body đọc từ stdin) trên cluster. Self-test ở P1 dùng đúng đường này trước khi chạm target; nếu sai thì run dừng ở `UID_PRECONDITION_SELFTEST_FAILED`.
- Định dạng thật của Events và managedFields của k3s.
- Thời gian kubectl thực tế.

## 6. G-ZER11-RT2 — gói kiểm MANUAL/RULES trên image production

**Kế hoạch dưới đây đã được Hoàng duyệt và chạy trong một cửa sổ RT2 riêng; kết quả ngày 22/10/2026 tại [runtime-02](../evidence/ZER-11/runtime-02/README.md). Quyền đó đã dùng xong, không cấp phép chạy lại.** Không dùng lại quyền RT1. Gói không tự ghi Kubernetes: Codex thực hiện có giám sát theo bảng thao tác dưới đây sau khi Hoàng duyệt, ghi mọi argv/result/UID và giữ một deadline chung. Không giao người dùng tự ráp hoặc tự chạy cả khối.

### 6.1 Kết luận cần kiểm, không mở rộng sang KPI

- **BM:** một quan sát HTTP lỗi thật đi vào O; consumer Hephaestus chạy nhưng ghi `AUTO_DECISION_DISABLED_FOR_GROUP`, không tự tạo DECISION hoặc phát action. Một đề xuất MANUAL hợp lệ từ O-console riêng được nhận, rồi `/heal/trigger` trả 409 `R1_EXECUTOR_DISABLED` và có audit đúng context.
- **B1:** một DETECTED *synthetic transport control* trong **run khác** tạo đúng một DECISION RULES qua consumer thật; polling lại không tạo bản trùng.
- **B2/B3:** run control riêng ghi audit bỏ qua; không tự giả RULES/LLM, không gọi model. Đây là log ranh giới chế độ AI khi chưa có producer LLM, **không chứng minh AI chạy thành công**.
- Nguồn quan sát BM là `rt2-http-availability/1`: đọc GET frontend, phát DETECTED qua Client/Producer production với producer/rule_version đúng của observer này. **Không phải Gaia**, không dùng nhãn rule Gaia hoặc sửa ngưỡng/quy tắc Gaia. Đồng hồ `UNKNOWN`, không chạy scorer và không claim MTTD/MTTR hay phục hồi nghiệp vụ. Kết quả RT1 đã chấm giữ nguyên.
- O-console là CLI trong pod riêng chỉ nhận khóa `operator_console/reader` và token gọi guard; không có H/raw/archive/attack key. Operator được script mô phỏng để kiểm route, không phải một trial BM có người vận hành mù.

### 6.2 Chuẩn bị offline và build input

```bash
ZD_PYTHON=scratch/zer12/production-hephaestus/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-modes.sh plan
```

```bash
ZD_PYTHON=scratch/zer12/production-hephaestus/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-modes.sh prepare --output scratch/zer11/rt2-bundle-<nonce> --namespace zd-zer11-rt2-<8hex>
```

`prepare` chỉ ghi thư mục mới; không gọi Docker/kubectl, không nối mạng. Bundle có build context tối thiểu chép byte-identical từ Hephaestus Dockerfile, lock, source và event_pipeline; source-manifest/hash; config; kế hoạch; List JSON **private-resources.json có khóa thử sinh mới**. Không in khóa hoặc đưa manifest private vào evidence/commit. Tên đã có thì dừng. Chạy lại khi source thay đổi; không ghi đè bundle cũ.

Image dự kiến `zero-door/hephaestus:zer11-rt2-<source_sha256 đầu16>`. Sau quyền, build từ `build/` với `-f build/hephaestus/Dockerfile`, import đúng cluster `zero-door`. Không build/restart Nemesis. Host giữ log build, inspect config digest/ENTRYPOINT và IDs thực trong từng pod; `attest --config /rt2/config.json` trong **mọi pod** phải khớp source runtime và script mount, không chỉ tin tag. Chưa kiểm Docker/Linux image build ở bước offline.

### 6.3 Phạm vi thao tác đề nghị cho một lượt

| Pha | Thao tác và điều kiện | Giới hạn / khôi phục |
| --- | --- | --- |
| Preflight chỉ đọc | Context `k3d-zero-door`; Docker `desktop-linux`; không DOCKER_HOST; node Ready; ghi UID/spec/replicas/Ready của cả 13 deployment, pod frontend/owner ReplicaSet, quota và HPA. Có HPA khác trỏ frontend thì dừng. Kiểm RAM/CPU headroom cho pod tạm, không tự tăng quota | Không sửa current-context, quota, PVC, Secret sẵn có, target replicas hoặc HPA |
| Build/import | Một image Hephaestus theo bundle và Dockerfile đã khóa; đối chiếu source/build/pod image IDs | Không áp deployment production, không chạy setup/rebuild legacy; không tải/chạy model |
| Tạo | Một namespace `zd-zer11-rt2-<8hex>`; Secret/ConfigMap, Service O, policy ingress, driver, 4 actor BM/B1/B2/B3 và console từ bundle. Mọi đối tượng có nhãn run; create intent ghi trước, UID sau; Secret không ghi nội dung vào log | 6 pod nonroot, filesystem chỉ đọc, emptyDir riêng, không SA token; imagePullPolicy Never; node server; 300m CPU/576Mi requests, 1500m/1152Mi limits tổng |
| Cô lập production | Tạm scale Gaia/Hephaestus về 0, xác nhận không còn pod Running/Pending. Giữ UID/spec/replicas ban đầu để trả đúng; không đổi image/env của chúng | Chỉ hai deployment này; worker/Nemesis và target giữ spec |
| Sẵn sàng | Đợi `/healthz` từng actor báo `transport=r1-o-gateway`, execution disabled. Chạy attest, lấy log audit đúng context. Kiểm thiếu token đọc O bị từ chối, control port9140 không có Service; console không đọc được khóa gateway | Lỗi preflight/wiring thì dọn trước fault; chưa chạm target |
| BM thật | Warm-up riêng tối đa20GET và giữ raw; sau đó `call monitor`, đợi ít nhất 10 mẫu GET200 liên tiếp (mặc định ≥5s), chụp pod frontend + UID/Ready ngay trước khi xóa. Chỉ xóa **đúng một pod frontend** thuộc UID ReplicaSet đã ghi, DeleteOptions precondition UID. Theo dõi đủ180s, ≥1 GET lỗi rồi có DETECTED thật | Tối đa360 GET **tổng mọi attempt và warm-up**, interval tối thiểu0,5s, timeout1s, không retry ngầm/redirect/proxy; không tạo tải khác. Không thấy lỗi: INCONCLUSIVE, không xóa lần hai để tìm PASS |
| Operator | Khi có DETECTED thật, console đọc O và tạo đúng một proposal MANUAL; gọi guard BM bằng token thử, lấy HTTP409/audit. Một request token sai phải401. Lưu receipt không chứa token | Không gắn executor giả, không sửa `R1_EXECUTOR`, không gọi route legacy/reset/attack |
| Controls | `call controls` phát DETECTED synthetic vào các run B1/B2/B3 riêng. Đợi hai poll và kiểm B1 đúng một RULES; B2/B3 audit disabled, không LLM/action. Thu health/log actor cuối cửa sổ | Không cộng control vào run BM hoặc cohort KPI |
| Thu và dọn | Lưu logs, image/source attest, frontend UID/RS/Event; dừng/xóa actor theo UID trước seal để không có writer muộn; `call finish`; kéo exports/summary/observations từ emptyDir. Dọn namespace theo nhãn+UID, xác nhận vắng; trả Gaia/Hephaestus theo UID/spec/resourceVersion và replicas baseline, đợi Ready; đọc lại cả13deployment | P7 luôn chạy trong finally kể cả Ctrl+C/lỗi. Create mất phản hồi phải reconcile tên+nhãn để lấy UID. Owner/spec đổi: để nguyên, báo INCOMPLETE; không xóa/scale theo tên trần |

**Trần đề nghị:** 45 phút **tổng từ trước build/import**, gồm 5 phút cuối dành cleanup; từng lệnh có timeout trong deadline chung. Chạm hạn chính thì dừng quan sát, giữ failure và dọn; không gọi là đủ cửa sổ. Pod có `activeDeadlineSeconds=2700` là lớp dự phòng, không thay deadline host. Không dùng GET này làm business probe; nó không tạo giỏ hàng hoặc checkout. Không gọi API/model trả phí. Không tự xóa image dùng chung hay prune Docker để rollback; chỉ để lại image mới với receipt nguồn.

### 6.4 Lệnh trong pod và bằng chứng

Driver chạy `/rt2/r1_mode_runtime.py driver` thay entrypoint **chỉ ở pod gateway**. Actor giữ nguyên ENTRYPOINT Uvicorn của image production và source không patch; không fake Kafka/Kubernetes/executor trong lab.

```bash
# Các argv bên dưới chỉ dùng SAU quyền lab, qua kubectl exec với context/namespace rõ.
# Trong pod driver:
/usr/bin/python3 -B /rt2/r1_mode_runtime.py call monitor
/usr/bin/python3 -B /rt2/r1_mode_runtime.py call status
/usr/bin/python3 -B /rt2/r1_mode_runtime.py call controls
# Sau khi actor đã dừng và log đã lưu:
/usr/bin/python3 -B /rt2/r1_mode_runtime.py call finish
```

```bash
# Trong pod console, IP Hephaestus BM lấy từ read-back đúng pod UID, không đoán:
/usr/bin/python3 -B /rt2/r1_mode_runtime.py operator --config /rt2/config.json --keys /keys/operator.json --token /keys/heal-operator.json --url http://rt2-o:9141 --heal-url http://<BM-pod-IP>:8000 --output /work/manual.json
```

CLI console chỉ mở O và endpoint guard riêng, không có đường export/H. Không phát lại operator command khi outcome chưa rõ: dừng, đọc O đối chiếu event_id thay vì tạo proposal mới. Khóa private nằm trong bundle scratch/Secret mới, không lẫn raw export; chỉ giữ hash và metadata trong báo cáo.

Chấm **boundary**, không chấm recovery:

```bash
ZD_PYTHON=scratch/zer12/production-hephaestus/Scripts/python.exe bash infrastructure/scripts/verify-dashboard-modes.sh assess --summary <summary.json> --logs <JSON group-to-log> --manual <manual.json> --output <file mới>
```

`PASS_BOUNDARY_ONLY` yêu cầu cửa sổ thật đủ180s, có khỏe trước lỗi, nguồn DETECTED đúng, BM chỉ có một MANUAL có causation đúng, B1 chỉ có một RULES, B2/B3 không quyết định, không action/LLM, audit đúng group/run/trial và HTTP409 khớp decision. Test có HTTP giả bắt buộc profile `OFFLINE_TEST_ONLY` và chỉ ra `PASS_BOUNDARY_OFFLINE`. Cả hai verdict đều **chưa xác nhận image/firewall/ownership/cleanup**: host phải đối chiếu các receipt đó độc lập trước nghiệm thu AC.

Bằng chứng runtime tối thiểu trong một thư mục mới: source/image hashes, argv/result không secrets, pre/postflight13deployment, audit/log4nhóm, raw O seal/export từng run, các quan sát HTTP, operator receipt, boundary verdict, cleanup theo UID và AC→case→kết quả. BM không có DETECTED, observer thiếu cửa sổ, log/health/source thiếu hoặc cleanup hỏng là INCOMPLETE/NOT_READY; không sửa criterion hoặc dùng control synthetic thay lỗi thật.

### 6.5 Receipt RT2 ngày 22/10/2026

[Runtime-02](../evidence/ZER-11/runtime-02/README.md): PASS_SCOPED_RT2, cleanup CLEAN, một frontend pod delete. Cửa sổ host chung 19phút52giây, không đặt lại deadline khi chuẩn bị lỗi. Image chỉ build/import một lần; Docker OCI index → linux/amd64 manifest → config được đối chiếu bằng hash với CRI. Không so trực tiếp index digest với config digest như cùng một kiểu.

Lần chuẩn bị đầu dừng vì kiểm nhầm kiểu digest; lần tiếp có timeout ngay lúc kết nối ban đầu, dừng trước fault và giữ raw. Tổng GET lần này không biết chính xác vì observer tiếp tục đến khi pod bị dọn; tính cận trên bảo thủ167 trên toàn vòng đời, có biên10s. Phần còn lại193GET được phân bổ tối đa20warm-up +173mẫu quan sát. Tool chỉ cho **siết** rate/cap: interval từ0,5 đến10s, max_gets từ1 đến360; không đổi cửa sổ180s hay criterion lỗi thật. Lần cuối dùng interval2s, warm-up10GET và81mẫu trong180,386s (14lỗi giữ nguyên). Cận trên tổng mọi lần là258GET, dưới360; không claim tổng chính xác.

BM có DETECTED từ HTTP thật và một MANUAL scripted bị executor từ chối409; B1 riêng có một RULES; B2/B3 riêng có audit disabled và không DECISION. Actor là image/source/ENTRYPOINT production, không fake executor. Sáu pod attest đạt, console O-only; O thiếu token401 và control port không truy cập từ console. Dừng actor trước seal;14envelope được kiểm hash độc lập. Namespace đã vắng,13deployment và quota/HPA/policy giữ UID/spec, Ready baseline. Không gọi model, không tính KPI, không chứng minh Gaia hoặc human-blind BM. Hết lượt này chưa đồng nghĩa issue Done/G1 PASS: còn publication/CI/review/merge và Hoàng nghiệm thu.

## 7. Ánh xạ gate G1 (kế thừa và còn thiếu)

| Điều kiện G1 | Đã có | ZER-11/39 thêm | Còn thiếu |
| --- | --- | --- | --- |
| ID xuyên pipeline | ZER-9 (transport/archive, runtime đã nghiệm thu), ZER-37 contract | Dashboard đọc run_id/trial_id/incident_id từ artifact đã chấm | — |
| Raw/export và KPI tái tính | ZER-10 scorer, runtime-01 | Dashboard/API/export cùng artifact; RT1 run B0 thật được chấm/hiển thị, hash và root unchanged trong evidence runtime-01 | Publication/CI/acceptance của gói hiện tại |
| Evidence không lộ đáp án | ZER-9 AC-03 leak check, ZER-10 LEAK_CHECK | Kết quả S chỉ đọc bằng khóa riêng; deployment live không mount; lỗi không lộ path | RT2 có O-console riêng chỉ mount khóa O; console Nemesis gốc vẫn chứa log H nên không dùng làm BM blind console |
| B0/BM không auto-heal | ModeGate/GuardedRules ZER-12 | B0 runtime RT1 đã có trong giới hạn ghi rõ; consumer và manual route kiểm offline | RT2 đã chạy image production: BM scripted/manual-refusal, B1 RULES, B2/B3 audit disabled. Chưa chứng minh LLM hoặc BM human-blind |
| Guard hoạt động | ZER-12/40 (CI, guard đã nghiệm thu) | Không đổi guard; executor production vẫn khóa | — |

Bảng này không kết luận G1 PASS.
