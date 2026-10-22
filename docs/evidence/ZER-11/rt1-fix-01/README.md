# ZER-11 + ZER-39 — rt1-fix-01 (Claude, offline)

**Verdict: READY_FOR_CODEX_RETEST_OFFLINE.**

- Đã sửa RT1-01…05 từ [codex-rt1-review.md](../codex-rt1-review.md) trong một gói.
- N1 đã được phân loại, có số liệu.
- Runtime vẫn **NOT_RUN**: chưa có quyền RT1, chưa chạm cluster, Docker, image build hay model. Không commit, không Linear.
- Đây không phải Done, không phải nghiệm thu AC-04/ZER-39 hay G1.
- Bước kế: Codex retest. Sau đó mới xin Hoàng quyền RT1 cho bản đã review.

## Baseline và phạm vi

- **Git:** HEAD `1694133`, nhánh `zer-10-independent-measurement`, không đổi nhánh, staged rỗng.
- **Snapshot trước sửa:** `scratch/zer11/claude-rt1-fix01/before/` + `before.json`, lấy bằng `snapshot_before.py` (script từ chối chạy lần hai).
  - Bản sao 6 file có thể sửa: harness, suite, runbook, verify, note, NOW.
  - Hash của 246 file chỉ đọc: toàn bộ `docs/evidence/ZER-11` (gồm báo cáo/probe Codex và evidence H-RT1), measurement, event_pipeline, nemesis, chaos-worker, manifests, tests khác, `.github`.
  - 10/10 hash protected khớp.
  - Manifest H-RT1 `843369a2…10db`: 19/21 file khớp. Hai file lệch là note và NOW, do Codex review append/prepend, đúng dự kiến.
- **Sửa (4 file + note/NOW):**
  - `infrastructure/scripts/r1_baseline_runtime.py`.
  - `tests/test_dashboard_baseline_runtime.py`.
  - `docs/runbooks/dashboard-and-baselines.md`: chỉ các phần 5.5 (hàng P2) và 5.9 nói về hành vi và kiểm chứng đã đổi.
  - `infrastructure/scripts/verify-dashboard-baselines.py`: 2 dòng (lý do ở dưới).
  - Note: append. NOW: prepend.
- **Thêm:** thư mục này.
- **Không sửa:** scorer, contract, event_pipeline, chaos-worker, measurement_view, CI, evidence cũ (gồm báo cáo và probe của Codex). [manifest-rt1-fix01.json](manifest-rt1-fix01.json) kiểm lại.
- **AC sống:** kết nối Linear của Claude không thấy ZER-11/39. Gói dựa vào AC Codex đọc qua `linear_zero_door` trong review 21/10 (AC không đổi). Không sửa Linear.

## Đã sửa gì (theo finding)

| Finding | Sửa | Bằng chứng sửa |
| --- | --- | --- |
| **RT1-01 P1** — OSError/ValueError bỏ P7 | `run()`: lỗi bất ngờ thành abort `UNEXPECTED (...)`; salvage bắt mọi lỗi; P7 nằm trong `finally`. Mỗi bước P7 cô lập lỗi, xóa HPA và trả replicas cô lập theo từng đối tượng. DeleteOptions đi qua stdin (`delete --raw … -f -`), nên mọi lệnh xóa không còn phụ thuộc đĩa host. Run đóng một lần, việc kéo `tar` thử lại riêng; không kéo được thì bước 1 là `FAILED`. Receipt ghi best effort và ghi sau cùng. | Đĩa host ENOSPC từ lúc Gaia=0 (pha chính) và từ cleanup (bước đầu); `ValueError` trong trial; `OSError` ở lần xóa HPA đầu. Mọi lệnh trả replicas đều được gửi (exit 0), cluster về P0. |
| **RT1-02 P2** — managedFields bị kubectl bỏ | `Kube.json(..., managed_fields=True)` thêm `--show-managed-fields=true` cho lần đọc canary (P2) và frontend (watch HPA). Fake bỏ managedFields khi thiếu cờ, như kubectl. | e2e đi qua P2 với fake mặc định thật. Manager sai (`argocd-application-controller`) vẫn bị `ATTRIBUTION_CONTROL_FAILED`. |
| **RT1-03 P2** — control fail bị ghi thành ok | Agent: `ok` chỉ là dispatch. Lệnh nào trả kết quả có `ok` thì bị từ chối (`RESULT_SHADOWS_OK`). Control trả `{"control": …}`. Host tự quyết bằng `control_passed()` từ 3 dữ kiện: O ghi được, `REJECTED`, `MODE_VIOLATION`. DECISION thử tối đa 3 lần trong hạn. | Mất ACK riêng DECISION, sai classification, DECISION được nhận: cả ba `POSITIVE_CONTROL_FAILED`, không có ghi P2/P3/P4, cleanup CLEAN. |
| **RT1-04 P2** — mất phản hồi create, vẫn CLEAN | `create()` ghi ý định trước khi gửi. Mất phản hồi thì `owned_uid()` đọc lại theo tên + namespace + nhãn run: ngay lúc đó, và lần nữa ở P7. Xóa theo UID qua `delete_owned()`. Tên bị đối tượng không mang nhãn run giữ thì `NOT_OURS`: để nguyên, cleanup `INCOMPLETE`. `final_diff` có thêm namespace tạm. Dùng chung cho namespace, ConfigMap, HPA, pod tải. | Mất phản hồi cho namespace (kể cả khi lần đọc lại đầu lỗi), HPA, pod tải, ConfigMap profile: đều được tìm lại và xóa theo UID, CLEAN. Namespace bị chiếm: không xóa, INCOMPLETE. ConfigMap bị thay UID: không xóa, INCOMPLETE. |
| **RT1-05 P2** — Event cũ/downscale dùng để claim | Lưu danh tính trial: UID pod bị xóa, UID ReplicaSet chủ, mọi pod trước lúc xóa (Ready hay không), UID HPA của run, replicas ngay trước T_req, T_req. Event giữ UID đối tượng. CTRL cần một pod Ready mới, cùng UID ReplicaSet, và `SuccessfulCreate` của chính RS đó nêu tên pod. HPA cần scale-up (`New size` > replicas trước) của đúng HPA (UID), do HPA controller phát, trong [T_req − 1 s, T_rec − 1 s). Thiếu hay mơ hồ thì ra `…_EVIDENCE_MISSING` / `…_AMBIGUOUS`. | 6 ca CTRL và 13 ca HPA (Event cũ, UID khác, downscale, trước T_req, biên 1 s, sau T_rec, không có thời gian, không do HPA, thiếu bằng chứng); e2e có Event của HPA lượt trước vẫn ra `HPA_NOT_ACTIVATED_NO_EFFECT`. |

**Thêm, ngoài 5 finding:**

- **Siết kiểm attribution ở P2.** Bộ kiểm giờ chỉ tính manager sở hữu `spec.replicas` qua subresource `scale`; `kubectl-create` không tính.
  - Đây là gia cố, không phải lỗi đã chứng minh. Fake cũ giữ quyền sở hữu của người tạo; Kubernetes thật chuyển quyền khi có Update. Fake nay chuyển quyền như vậy, nên kiểm tra cũ cũng bắt được manager sai trong chế độ isolated.
  - Rủi ro: server không ghi `subresource` trong managedFields sẽ fail closed ở P2.
- **CLI `rt1 --execute`** in thêm `errors`, và trả exit 0 chỉ khi COMPLETED + CLEAN + không có lỗi.
  - Lý do: theo RT1-01, receipt có thể không ghi được (đĩa đầy). Khi đó stdout là bản ghi duy nhất, nên không được giấu `RECEIPT_NOT_WRITTEN`.
- **`control_deliveries`** trong receipt của agent ghi thời gian, số lần thử lại và trạng thái của từng control event.
  - Abort `PERSISTENCE` mang theo chi tiết đó.
  - Lỗi `CONTROL_NOT_DURABLE` của `attack_requested` nay cũng là `PERSISTENCE` (trước là `AGENT_CONTROL_NOT_DURABLE`).

## Fail-before / expected-fixed

[fail_before.sh](fail_before.sh) dựng hai cây sạch: `git archive HEAD` + file gói, không có `scratch/`. Hai cây giống nhau trừ harness: BEFORE lấy từ snapshot, AFTER lấy từ cây làm việc. Cả hai dùng suite rt1-fix-01, chạy qua [focused.py](focused.py) ở ba chế độ. [check_fail_before.py](check_fail_before.py) so expected/actual.

- `isolated`: harness BEFORE với fake trả managedFields như fake H-RT1, để từng finding hiện riêng.
- `kubectl-default`: harness BEFORE với mặc định thật của kubectl.
- `after`: harness AFTER, suite nguyên trạng.

Kết quả: [expected-vs-actual.json](results/fail-before/expected-vs-actual.json) có **11/11 dòng khớp** (BEFORE FAIL, AFTER ok), AFTER không có ca nào không đạt. Hash cây ở [trees.txt](results/fail-before/trees.txt).

| Finding | Ca hồi quy (BEFORE → AFTER) | Lỗi đầu tiên ở BEFORE |
| --- | --- | --- |
| RT1-01 | 3 ca | `OSError: [Errno 28]` ×2, `ValueError` thoát khỏi `run()`, P7 không chạy |
| RT1-02 | e2e; manager sai | `ATTRIBUTION_CONTROL_FAILED`; `'argocd-application-controller' not found in []` |
| RT1-03 | 3 ca con + kiểm dispatch | run đi tiếp sau control fail (`KeyError: 'abort'`); `{'ok': True}` |
| RT1-04 | 5 ca mất phản hồi; 2 ca không phải của mình | `created` rỗng (`IndexError`/`StopIteration`); bước xóa ConfigMap báo `DONE` |
| RT1-05 | ma trận claim; Event HPA cũ trong e2e | `CONTROLLER_RECOVERY_OBSERVED` từ Event lịch sử; `NO_EFFECT` thay vì `HPA_NOT_ACTIVATED_NO_EFFECT` |
| N1 (negative control) | ACK trễ hơn hạn | `AGENT_CONTROL_NOT_DURABLE`, không có thời gian ACK |

Probe của Codex (chỉ đọc, chạy nguyên bản trên cây mới): [results/codex-probes](results/codex-probes).

- `counterexamples.py` dừng ở assert đầu tiên. Lý do: run không còn abort ở P2, mà đi hết hai trial với manager `kubectl`/`scale`.
- `pod-counterexamples.py` dừng ở `KeyError: 'ok'`. Lý do: kết quả control không còn mang `ok`.
- Đây là probe khẳng định hành vi hỏng. Giờ chúng fail đúng như kỳ vọng sau sửa; chúng không phải test nghiệm thu. Bản kỳ vọng-sau-sửa là lớp `Findings`.

## N1 — lỗi ngắt quãng

**Kết luận: N1 gồm hai loại lỗi riêng, cả hai đều có căn cứ đo được. Không loại nào là lỗi logic của harness.** Không bỏ assert, không chạy lại suite tới khi xanh, không đổi F-01 hay tham số runtime.

Công cụ ở [n1/](n1/).

- `n1_run.py` chạy suite với các wrapper chỉ đo thời gian (không đổi source): `Gateway.submit`, `Archive.append` (gồm fsync) và `HttpHSink.deliver`.
- `n1_loop.sh` chạy lặp, tuần tự hoặc song song, và giữ file của ca fail (`RT1_KEEP`).
- `n1_analyse.py` tính phân bố độ trễ.
- `n1_failures.py` gắn mỗi ca fail với độ trễ lớn nhất đo được trong chính ca đó.

**Loại A: nghẽn I/O của host (dấu vết của Codex).**

- Lượt Nemesis-2 của Codex: 2 FAIL + 1 ERROR đều từ `PERSISTENCE (CONTROL_NOT_DURABLE)`, kèm WinError 10053 khi gateway trả ACK.
  - `KeyError: 'B0-HPA'` là hệ quả: run đã dừng ở CTRL.
  - 10053 nghĩa là gateway đã ghi event bền, nhưng trả lời sau khi client đã bỏ vì quá hạn (2 s trong fake cũ).
- Trên bản trước sửa, 24 lượt (12 tuần tự, 12 song song 3 tiến trình) đều đạt.
  - 14 121 lần `append`+fsync: p99 ≤ 2,2 ms, tối đa 197 ms, không lần nào trên 1 s.
  - Số liệu: [timing-before.json](n1/results/timing-before.json).
  - Vậy đường code bình thường cách xa hạn 2 s.
- Lượt sau sửa attempt1: 17 lượt, 3 lượt fail, 4 ca ([failures-attempt1.json](n1/results/failures-attempt1.json), log ở [logs-attempt1](n1/results/logs-attempt1/)). Trong lúc đó tôi chạy song song fail-before (thêm 3 tiến trình suite).
  - `ATTACK_REQUESTED` hết hạn 10 s mới. Trong ca đó, một lần `Archive.append` của gateway mất **10 854 ms**. Trước đó, bước ghi outbox phía agent đã ăn khoảng 9,2 s, nên lần gửi đầu chỉ còn 822 ms ngân sách. Không có I/O nào trong khoảng ~10 s.
  - Hai ca `BASELINE_UNHEALTHY`: nghẽn submit/append 2,4–2,9 s rơi vào cửa sổ chờ baseline 3 s đã nén của fake.
  - Số liệu: [timing-after-attempt1.json](n1/results/timing-after-attempt1.json), có 5 lần append > 2 s.
- Phân loại: fsync của thư mục Temp trên host bị nghẽn nhiều giây khi máy có tải I/O đồng thời (lượt của Codex chạy cùng GitNexus reindex; lượt của tôi chạy cùng fail-before).
  - Harness làm đúng: control event không được ack bền trong hạn thì run dừng ở `PERSISTENCE`, trial ở (d), cleanup vẫn chạy. Không bao giờ thành PASS giả.
  - Chưa chứng minh được nguồn nghẽn trên máy của Codex (antivirus, đĩa, hay lịch CPU). Chỉ chứng minh được nó xảy ra ở fsync và ACK, ngoài đường code.
- Đã đổi:
  - Fake giữ hạn ACK control (`grace_s` 10 s) và `ack_stall_s` (15 s) ở giá trị production. Lý do: thang giây của fake không làm nghẽn host ngắn lại.
  - Negative control [`test_control_ack_later_than_its_deadline_fails_closed`](../../../../tests/test_dashboard_baseline_runtime.py) giữ đường hạn 2 s: gateway ghi event nhưng trả lời trễ, thì run dừng `PERSISTENCE`, `control_deliveries` cho thấy ms ≥ hạn, không có lệnh xóa pod nào. Ca này tái hiện đúng dấu vết 10053 của Codex.
  - Agent ghi `control_deliveries` để phân loại được nếu chuyện này xảy ra trên lab.

**Loại B: lỗi của fake (một ca hang).**

- Ca `test_no_recovery…` ra `UNKNOWN_EFFECT` thay vì `MISSING_PROBE`, không có nghẽn I/O (append tối đa 84 ms).
  - Dòng thời gian: sau ATTACK_REQUESTED không có PROBE_SAMPLE nào; trial kết thúc đúng ở +2 s, tức hạn của step.
- Nguyên nhân, đã chứng minh xác định bằng [fake_hang_cleanup.py](n1/fake_hang_cleanup.py):
  - Lỗi rơi đúng sau `add_to_cart`, nên transaction đang sở hữu giỏ hàng. `Flow.cleanup` gửi `POST /cart/empty` với deadline sống (callable).
  - Fake cũ so `perf_counter_ns() < deadline_ns`, nên ném `TypeError: '<' not supported between instances of 'int' and 'function'` ([fake-hang-old-fake.json](n1/results/fake-hang-old-fake.json)). `Flow` chỉ bắt `Failure`, nên probe chết và trial dừng ở (d).
  - Fake đã sửa (`deadline_value`) cho sample `TIMEOUT/STEP_DEADLINE`, cleanup `GRACE_EXPIRED` ([fake-hang-fixed-fake.json](n1/results/fake-hang-fixed-fake.json)).
  - Thêm test của chính fake: `Boundaries.test_fake_hang_honours_the_live_deadline_of_a_cleanup_request`.
- Lỗi chỉ xảy ra khi lỗi target rơi giữa một transaction đã giữ giỏ hàng, nên hiếm: 40 lượt chạy riêng ca này trên fake cũ đều đạt. Vì vậy phải chứng minh bằng cách đặt thời điểm có chủ đích.
- ProbeRunner và runtime không đổi. Đây là test double.

**Một ca không truy được:** clean checkout lần 1 có 1 test fail trên Hephaestus ([clean-checkout-attempt1.txt](results/clean-checkout-attempt1.txt)). Script chép từ H-RT1 chỉ ghi dòng tóm tắt, nên không biết là test nào. Script nay giữ toàn bộ output và file của ca fail. Lần 2 đạt.

**Đợt cuối trên bản cuối** (không chạy gì khác song song, có giữ file ca fail): [exits-final.txt](n1/results/exits-final.txt), [timing-final.json](n1/results/timing-final.json), [failures-final.json](n1/results/failures-final.json).

- Tuần tự Nemesis 4/4, Hephaestus 4/4.
- Song song 3 tiến trình: vòng 1 đạt 3/3, vòng 2 fail 0/3.
  - Cả ba fail **cùng một ca, cùng một lúc**: lớp con "ConfigMap bị thay UID" của `test_rt1_04_an_object_that_is_not_ours…`.
  - File đã giữ ([kept-final](n1/results/kept-final/), log ở [logs-final](n1/results/logs-final/)) cho thấy run đã dừng ở P1 với `PERSISTENCE (CONTROL_NOT_DURABLE: RUN_STARTED None after ~10 002 ms)`, nên kịch bản không tới bước cần kiểm.
  - Cả ba tiến trình đo cùng một lần nghẽn: `append` 3 705 ms, `submit` 6 388 ms.
  - Đây là loại A: nghẽn I/O trên toàn host, không phải lỗi harness. Harness dừng an toàn và vẫn dọn sạch.
- Một lượt tuần tự Nemesis cũng có một lần `append` 2 482 ms mà không ca nào fail.
- Không có ca loại B nào sau khi sửa fake.

**Giới hạn còn lại, nói chính xác:**

- Ngoài hạn ACK, các tham số của fake vẫn nén theo giây: chờ baseline 3 s, W_eff 2 s, gap 0,6 s.
- Một lần nghẽn fsync vài giây trên máy chạy test vẫn có thể làm một ca fail: baseline không kịp khỏe, hoặc có khoảng trống trong W_eff.
- Ca như vậy phải được phân loại bằng `n1_failures.py` trên file đã giữ, không được chạy lại tới khi xanh.
- Trên lab, các hạn này ở giá trị production (phút/chục giây).

## Kiểm khác

| Kiểm | Kết quả | File |
| --- | --- | --- |
| Suite H-RT1 (27 test: 17 cũ + 8 `Findings` + negative control ACK + test fake hang) trên hai pin production | Nemesis 27/27, Hephaestus 27/27 | [regressions.txt](results/regressions.txt) |
| Hồi quy: dashboard 33, modes 7 (hai pin), CI boundary 6, check_r1_baselines, plan-check, ma trận rt1 (22 thao tác ghi), `--execute` thiếu quyền bị từ chối, Bandit 0, `diff --check` so snapshot, không CR | OVERALL exit 0 | [regressions.txt](results/regressions.txt), [run_regressions.sh](run_regressions.sh) |
| Clean checkout (`git archive HEAD` + 24 file gói, không `scratch/`) | Lần 1: OVERALL 1 (1 test Hephaestus, không truy được; xem N1). Lần 2: OVERALL 0 | [clean-checkout-attempt1.txt](results/clean-checkout-attempt1.txt), [clean-checkout.txt](results/clean-checkout.txt) |
| Fail-before / expected-fixed | 11/11 khớp. Lần đầu chạy trên suite trước khi sửa fake hang cũng 11/11 | [fail-before](results/fail-before/), [fail-before-attempt1](results/fail-before-attempt1/) |
| Entrypoint offline không gọi kubectl | `Boundaries.test_offline_entrypoints_never_run_kubectl` đạt (`subprocess.run` bị chặn) | suite |
| Manifest | 6 file sửa (harness, suite, runbook, verify, note chỉ append, NOW chỉ prepend; đã so byte với snapshot), 60 file thêm (thư mục này); 246/246 file chỉ đọc không đổi; 10/10 protected; staged rỗng | [manifest-rt1-fix01.json](manifest-rt1-fix01.json) |

**Self-review** toàn diff và các consumer P0–P8:

- `run`/`salvage`/P7/`restore`/cleanup.
- `create`/`owned_uid`/`delete_owned`, cùng mọi caller: P1 namespace/ConfigMap/pod agent/profile, P2 canary, P4 HPA/pod tải, `stop_fault`.
- `p2`, `watch`, `fault`, `collect_events`, `interpret`, `p5`, CLI `rt1`.

Ngoài các sửa theo finding, review tìm và sửa thêm:

- Đọc replicas của HPA trước khi phát ATTACK_REQUESTED, không phải sau.
- `pods_before` gồm cả pod chưa Ready.
- Dung sai 1 s cho Event so với T_req.
- `message` có thể rỗng.
- Seam `RT1_KEEP`: Python 3.11 đặt lại `_outcome.success` khi chạy cleanup, nên seam đọc danh sách lỗi của result thay vào đó.

## Residual

1. **Chưa kiểm được offline**, cần lab:
   - `kubectl delete --raw -f -` đọc body từ stdin. Self-test P1 đi đúng đường này trước khi chạm target; nếu sai thì `UID_PRECONDITION_SELFTEST_FAILED`.
   - managedFields của k3s có `subresource: scale` cho `kubectl scale`. Không có thì P2 fail closed.
   - Event thật có `involvedObject.uid`, `Created pod: <tên>`, `New size: N`, thời gian độ phân giải giây.
   - Đồng hồ pod agent và API server cùng nhân VM k3d. Đây là giả định, dùng để so Event với T_req/T_rec.
   - Tải có kích hoạt HPA hay không.
2. **N1:** chưa chứng minh được vì sao lượt của Codex chậm hơn 2 s. Trên lab, ACK chậm hơn 10 s sẽ làm run dừng ở `PERSISTENCE`, tốn một run nhưng không bao giờ thành PASS giả. `control_deliveries` cho số liệu để phân loại.
3. **Create bị API áp dụng muộn hơn lần đọc lại ở P7** (cực hiếm) có thể để lại đối tượng. Bước so P0 vẫn bắt được namespace, HPA hay ConfigMap profile còn sót (INCOMPLETE); pod tải nằm trong namespace.
4. **Đĩa host đầy:** receipt không ghi được, chỉ còn kết quả trên stdout của `rt1 --execute`.
5. **Kế thừa H-RT1:**
   - Gateway H/O chạy chung một process.
   - Watch dựa trên poll của host.
   - Trial dừng ở (d) thì dừng cả run.
6. Không chạy lại mutant: theo gói, không tăng mutant/check chỉ để tăng số. Ma trận fail-before ở trên là bằng chứng cho từng finding.

## Lệnh cho Codex retest

Từ thư mục gốc repo, Bash, pin production:

~~~bash
N=scratch/zer12/production-nemesis/Scripts/python.exe; H=scratch/zer12/production-hephaestus/Scripts/python.exe
$N -B tests/test_dashboard_baseline_runtime.py && $H -B tests/test_dashboard_baseline_runtime.py
NEMESIS=$(pwd)/$N bash docs/evidence/ZER-11/rt1-fix-01/fail_before.sh scratch/zer11/claude-rt1-fix01/before <thư mục kết quả mới>
$N -B docs/evidence/ZER-11/rt1-fix-01/check_fail_before.py <thư mục kết quả đó>
NEMESIS=$(pwd)/$N HEPHAESTUS=$(pwd)/$H BANDIT=$(pwd)/scratch/zer12/test-venv/Scripts/python.exe bash docs/evidence/ZER-11/rt1-fix-01/run_regressions.sh scratch/zer11/claude-rt1-fix01/before <log mới>
NEMESIS=$(pwd)/$N HEPHAESTUS=$(pwd)/$H bash docs/evidence/ZER-11/rt1-fix-01/clean_checkout.sh <log mới>
bash docs/evidence/ZER-11/rt1-fix-01/n1/make_tree.sh <cây mới tuyệt đối> . && bash docs/evidence/ZER-11/rt1-fix-01/n1/n1_loop.sh $(pwd)/$N <cây> <thư mục mới> 4 3
~~~
