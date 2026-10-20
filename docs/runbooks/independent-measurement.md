> Kết quả mới nhất 20/10/2026: [fix-03](../evidence/ZER-10/fix-03/README.md) và [runtime AC-01](../evidence/ZER-10/runtime-01/README.md) đã thực hiện trong quyền lab cụ thể của Hoàng. Mục 3 bên dưới là đề xuất lịch sử; không coi 900 mẫu/15 phút ở đó là receipt đã chạy. Lượt thật dùng 24 mẫu, tối đa30 giao dịch/đích, giữ cold failure/warm-up và đã cleanup.

# R1 — Đo độc lập: probe, recovery evaluator, scorer (ZER-10 / ZER-38)

[Thiết kế giao diện](../design/r1-measurement.md) · [Verification](../evidence/ZER-10/verification.md) · [Ghi chú issue](../delivery/milestones/R1-measurement/probes-and-metrics.md)

Runbook gồm tái lập offline và runtime plan lịch sử; lượt runtime đã duyệt và giới hạn của nó nằm ở receipt mới nhất. Mọi lệnh dùng Bash/Git Bash từ gốc repo.

## 1. Tái lập offline

Chỉ cần Python 3.11 và thư viện chuẩn, không cài gói. Test tự tạo server loopback và archive tạm của riêng mình.

```bash
bash infrastructure/scripts/verify-measurement.sh --help
```

```bash
bash infrastructure/scripts/verify-measurement.sh --offline
```

```bash
python -B docs/evidence/ZER-10/check_mutants.py
```

```bash
python -B docs/evidence/ZER-10/crosscheck_zer37.py
```

```bash
python -B docs/evidence/ZER-10/fix-01/retest_counterexamples.py
```

```bash
python -B docs/evidence/ZER-10/fix-02/fail_before.py
```

- `--offline` chạy toàn bộ `tests/test_measurement_*.py`, rồi tái tính E01 từ một export sealed và so với số tính tay. Trong lúc chạy có chốt socket: kết nối tới địa chỉ không phải loopback (kể cả tên miền cần DNS) bị từ chối. Kết quả `OFFLINE_PASS` chỉ có nghĩa là code đúng trên dữ liệu SYNTHETIC.
- `check_mutants.py` cố ý làm sai từng quy tắc (mốc T_rec, UNKNOWN rời N, missing thành PASS, H lọt vào O, gap thành up, mất sequence, chỉ xét status, cancel thành lỗi, NO_EFFECT không cần phủ, đồng hồ chưa sync, tin evaluator). Nhóm mutant `FIX01_*` khôi phục từng hành vi Codex đã chỉ ra (ZR10-01…11, N1). Mỗi mutant phải bị test bắt. Nhóm `FIX02_*` đặt lại đúng một dòng đã sửa cho codex-retest01 (FX01-R1…R3, N1, journal) bằng đột biến mã nguồn trong bộ nhớ.
- `fix-02/fail_before.py` chạy regression mới và hai script phản ví dụ của codex-retest01 trên snapshot trước sửa (`fix-02/before/`) và trên cây hiện tại, mỗi bên trong cây tạm riêng. Test NEGATIVE phải fail trước và đạt sau; test CONTROL phải đạt sau.
- `fix-01/retest_counterexamples.py` chạy lại mọi phản ví dụ của Codex trong `codex-review/` và so với expected của review. Script của Codex được chạy nguyên trạng; riêng `probe/counterexamples.py` có hai dòng chẩn đoán phụ thuộc hành vi cũ nên được chạy từ chính source với đúng hai chỗ thích nghi, có ghi trong output. File của Codex chỉ được đọc.
- `crosscheck_zer37.py` dựng 62 ca §10 của contract bằng oracle ZER-37, nạp qua `Archive` thật, seal/export rồi chấm bằng scorer, và so với expected tính tay của ZER-37.
- Muốn chọn interpreter khác: `ZD_PYTHON=/đường/dẫn/python bash infrastructure/scripts/verify-measurement.sh --offline`.

### Chấm lại từ export sealed

Evaluator xuất từng plane bằng `Archive.export` khi writer đã dừng (xem [r1-event-pipeline](r1-event-pipeline.md)), rồi chạy:

```bash
bash infrastructure/scripts/verify-measurement.sh --recompute --h-export <export-H> --o-export <export-O> --required-flow checkout --output <thư-mục-mới>
```

- Thư mục output phải chưa tồn tại và nằm ngoài các export; scorer không ghi đè gì. Export bị sửa hay lệch hash thì exit 3 và không có output.
- Thêm `--options <file.json>` cho `criteria_version`, `benign` (`trial_ids`, `slot_s`, `episode_gap_s`, `detector_coverage`, `action_log_complete`, `provenance`) và `surfaces` (prompt đã lưu để kiểm rò).
- Thêm `--other-export <export của run khác>` (lặp lại được, cả H và O) để kiểm LINK_CONFLICT liên run (§6.3). Thiếu tham số này thì kết quả mang cờ `CROSS_RUN_LINKS_UNCHECKED`; khi chấm formal phải truyền mọi run khác của cùng archive.

## 2. Kiểm plan trước runtime

```bash
cd agent-orchestrator && python -B -m measurement plan-check --plan ../tests/fixtures/zer10/plan-synthetic-boutique.json
```

Lệnh này chỉ đọc plan và in giới hạn: số request tối đa mỗi mẫu, budget và origin. Nó không mở kết nối nào. Plan mẫu là SYNTHETIC; L và timeout vẫn UNKNOWN cho tới khi có pilot.

## 3. Runtime plan ban đầu (lịch sử; đối chiếu receipt mới nhất trước dùng)

Lệnh `--runtime` từ chối chạy nếu thiếu `--runtime-approval <tham chiếu phê duyệt>`, thiếu plan/context/outbox mới/H URL/H key. Gói ZER-10 **không** chạy runtime. Bảng dưới gom mọi thứ cần quyết một lần.

| Hạng mục | Đề xuất cụ thể | Còn thiếu / ai quyết |
| --- | --- | --- |
| Mục tiêu và đường đi | Boutique: `frontend` qua port-forward loopback do verifier sở hữu (`127.0.0.1:<port>` → `svc/frontend` ns `target-app`), giống phần purchase của `verify-local-lab.sh`. Fixture: endpoint `/fixture/orders` của ZER-41 | Fixture chưa tồn tại (ZER-41 Backlog). Marker sản phẩm và trang checkout cần quan sát thật một lần rồi ghi vào plan |
| Origin allowlist / redirect | `allowed_origins` chỉ gồm origin port-forward; redirect ngoài allowlist là lỗi; không theo redirect sang host khác. H sink không bao giờ theo redirect và bỏ qua proxy môi trường; 3xx hay ACK lạ thì probe dừng `SINK_REFUSED`, outbox giữ nguyên (exit 5) | Nếu H gateway chạy chế độ Kafka (ack 202), cần chốt ack nào là đã giao |
| Danh tính và mặt dữ liệu | Probe dùng vai `probe` trên H gateway riêng, file key chỉ chứa `probe`; recovery evaluator dùng vai `recovery_evaluator`; không có quyền O | Cần H gateway chạy trong lab và một namespace/PVC tạm theo mẫu ZER-9 |
| Đồng hồ | Probe chạy trên host Windows là OFF_HOST, phải có CLOCK_SYNC trước TRIAL_STARTED và sau TRIAL_ENDED; hoặc probe chạy trong cluster là HOST_SHARED, không cần sync | Endpoint đồng hồ tham chiếu chưa có; phương pháp và ngưỡng sai số thuộc F-01 |
| Cadence và budget pilot | Δ = 1 s, timeout bước 5 s, giao dịch 10 s, L = 2 s (gợi ý ZER-32, chưa khóa); 1 phiên tối đa 15 phút: `max_samples` 900, `max_requests` 9 × 900 = 8.100; heartbeat 5 s; `grace_s` 10. Trần 15 phút cắt cả giao dịch đang chạy; sau trần chỉ còn cleanup và gửi outbox trong 10 s, nên thời gian thực tế ≤ 15 phút + 10 s; mọi ghi H, đọc đồng hồ và cleanup sau khi dừng đều kết thúc trong cửa sổ grace đó (event chưa giao giữ trong outbox) | Nằm trong trần pilot 2 giờ/phiên, 8 giờ tổng của ZER-8 §13; tải thêm ~5 request/s lên frontend phải được Hoàng chấp nhận |
| Tài nguyên | Probe là một tiến trình Python, không tạo pod tải; outbox khoảng 1–2 KB mỗi mẫu (~2 MB/phiên) | — |
| Marker nghiệp vụ | Trước khi phát mẫu đầu tiên: mở trang sản phẩm, giỏ (một dòng, `SKU #<id>`, `Quantity: 1`) và trang xác nhận một lần trên Boutique thật; nếu khác `CART_MARKERS` thì ghi marker quan sát được vào `flow_spec.args.cart_markers` | Quan sát này nằm trong lượt runtime được duyệt; không tự khóa marker |
| Lỗi tối thiểu cần quan sát (AC ZER-38) | (1) Dừng `frontend` có kiểm soát (scale 0 rồi về 1) để thấy CONNECT/HTTP rồi phục hồi; (2) dừng `checkoutservice` để thấy checkout không xác nhận (BUSINESS) trong khi home vẫn 200 | Đây là thao tác lab có hệ quả, cần quyền riêng; không chạy fault/flood của Nemesis |
| Stop và cleanup | Ctrl+C/SIGTERM đi đường cancel: mẫu dở không được phát (journal `INTERRUPTED`), giỏ của mẫu được làm trống trong `grace_s`. Tài nguyên không chứng minh được sở hữu (`UNRESOLVED_OWNERSHIP`) hoặc dọn không kịp (`GRACE_EXPIRED`) được để nguyên cho operator xem, không xóa: journal trên đĩa (`<outbox>.journal.jsonl`) và `unresolved_cleanup` trong summary liệt kê chúng. Dừng port-forward do verifier sở hữu; scale lại đúng replica ban đầu; seal, export rồi chấm offline | Ghi receipt; lỗi thì giữ tài nguyên để chẩn đoán, không tự chạy lại |
| Output | Thư mục mới `scratch/zer10/runtime-<nonce>/`: outbox, journal/summary probe, export H/O, output scorer; evidence chọn lọc vào `docs/evidence/ZER-10/` | Không ghi secret, cookie hay thẻ |

Sau runtime vẫn còn: quan sát thật một mẫu đạt và một mẫu lỗi cho cả Boutique lẫn fixture, đây là điều kiện AC-01. Fixture thật thuộc ZER-41. Phần còn lại là review, CI từ xa, merge và Hoàng nghiệm thu.

## 4. Bản sửa cuối và receipt thật

- Deadline socket dùng chung mốc stop sớm nhất cho H, reference và cleanup đang chạy, kể cả TLS/send; stop lặp không gia hạn. DNS hệ điều hành, tải certificate store, fsync và hard kill không có bảo đảm ngắt tức thì phổ quát; lượt thật dùng IP literal/HTTP và ghi độ phân giải clock.
- Session được kiểm sau từng response trước redirect tiếp theo, gồm hop cấp session đầu. Cleanup giữ credential/target ban đầu.
- Kiểm gói hiện hành: `python -B docs/evidence/ZER-10/check_package.py --check` (đọc fix-03 khi đã seal).
- Raw runtime được kiểm độc lập bằng `python -B docs/evidence/ZER-10/runtime-01/audit_raw.py`. Script này chỉ đọc artifact, không mở kết nối.
- Fixture SQLite là prerequisite CRUD thật cho probe; ZER-41 SQLi và G1 không tự hoàn thành. Runtime không có detector/LLM cohort, N=0 là EMPTY, không phải PASS MTTD/MTTR. Xem receipt để biết các lần chuẩn bị lỗi, warm-up, rollback và cleanup watch timeout.
