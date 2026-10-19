# ZER-9 fix-03 — lỗi đọc nguồn archive (FX02-R1)

19/10/2026, Claude. Nhánh `zer-9-event-pipeline`, HEAD `2af4d33`, chưa commit. **READY_FOR_CODEX_RETEST.** Đây không phải READY_FOR_HOANG_ACCEPTANCE và chưa Done: source sau fix-01..03 chưa chạy live, CI chưa chạy, chưa có bằng chứng trên chính actor.

## Finding → nguyên nhân

[Codex retest fix-02](../codex-fix02-review/README.md), P2 FX02-R1:
- `records()` chỉ bắt ArchiveFailure. OSError khi open/read raw lọt ra: `GET /events` ngắt kết nối, `readyz` vẫn 200 và POST sau đó vẫn 201.
- Export bỏ sót lỗi đọc `late.jsonl` và quarantine phạm vi archive (6/6 nhánh nguồn trong ma trận H/O).

Nguyên nhân: lỗi được bắt ở từng caller theo loại exception. Code chưa có một ranh giới phân biệt "đọc nguồn archive" với "ghi đích export". Rà lại toàn bộ trước khi sửa ([ma trận](../../../../scratch/zer9/claude-fix03/matrix.md)) cho thấy cùng nguyên nhân ở ba chỗ khác:
1. Kiểm tồn tại bằng `Path.exists/is_symlink/is_dir`. Trên 3.11/3.12 các hàm này ném OSError khi gặp EIO/EACCES; từ 3.13 `exists` nuốt mọi lỗi. Lỗi stat ở `manifest.json` khi ingest/quarantine/submit Kafka, hoặc ở thư mục run khi seal, đều không sticky.
2. `shutil.copyfile` đọc nguồn và ghi đích trong cùng một lời gọi, nên không phân biệt được hai loại lỗi.
3. Hướng ngược lại: bản sao ở đích đọc lại lệch hash thì ném ArchiveFailure và **làm dừng archive nguồn khỏe**.

## Fix (chỉ `store.py`)

- Hai helper ở ranh giới nguồn:
  - `entry(path)`: lstat; trả None khi file vắng (FileNotFoundError); mọi lỗi khác thành ArchiveFailure.
  - `reading()`: OSError trong khối đọc nguồn thành ArchiveFailure, giữ `__cause__`.
- Các helper được dùng ở `iter_file` (mọi lần đọc file archive), `summary`, `path`, kiểm tồn tại trong init/ingest/reject/sealed/manifest/seal/export, và phần đọc của bản sao export.
- Op dưới khóa đổi ArchiveFailure thành `fail()` sticky:
  - records, seal, export: đã có từ fix-02;
  - `path()`, `run_dir`: sửa trong fix-03;
  - `lookup()` cho sealed/ingest/reject.
  `fail()` ghi tên lỗi I/O gốc, ví dụ `ARCHIVE_FAILED:OSError`, giống lỗi ghi; dữ liệu hỏng vẫn là `INTEGRITY`.
- Bản sao export được chép bằng vòng lặp riêng: đọc nguồn (sticky, hash luồng phải khớp summary) và ghi đích (OSError). Bản sao ở đích lệch hash là `OSError(EIO)`: export thất bại, nguồn vẫn Ready. Thư mục đích, file con, export.json, fsync và chmod không được bọc.
- Không đổi gateway: `GET /events` và `/seal` đã có nhánh ArchiveFailure → 503. Không truncate, reset hay xóa evidence, không thêm abstraction tổng quát. Một thay đổi hành vi nhỏ: symlink thư mục run (tamper) nay sticky ở mọi op, trước đây chỉ khi export.

## Regression mới — `SourceReadFailureTests` (4 method, fail-before/pass-after)

Lỗi là `OSError(EIO)` thật, đặt ở `builtins.open`/`os.stat`/`os.lstat` cho đúng một đường dẫn, bên dưới mọi hàm của store; không patch hàm cấp cao để sẵn ArchiveFailure. Mỗi ca kiểm:
- lỗi đến đúng lần đọc dự kiến (đếm lần open);
- `failure == "OSError"`;
- readyz 503 `ARCHIVE_FAILED:OSError`, livez 200;
- POST event, input sai, `/seal`, `records()` và export sau đó đều bị từ chối;
- bytes của plane không đổi;
- restart mở lại được, vì lỗi thoáng qua và evidence nguyên vẹn.

| Method | Ca (H và O) | Snapshot fix-02 |
|---|---|---|
| records/seal | records lỗi open; records lỗi đọc dòng 2; `GET /events` (O) lỗi open và lỗi giữa file → 503 NOT_DURABLE; `POST /seal` lỗi stat thư mục run → 503; `POST /seal` lỗi open raw (control) | OSError lọt / RemoteDisconnected / failure None; control đạt |
| export | late: stat, open (summary), open thứ 2 (hash), đọc lần 2 của bản sao; quarantine phạm vi archive: stat, open, giữa bản sao; raw: giữa bản sao (lần open thứ 5) | OSError lọt, không sticky |
| write path | POST H/O lỗi stat `manifest.json`; O Kafka: submit HTTP (`sealed()`) và recorder (ingest; restart bridge không xóa lỗi, commit 0) | 503 nhưng failure None, readyz 200 |
| destination | đích đã tồn tại, ENOSPC khi ghi, bản sao đọc lại lệch, chmod, fsync export.json → OSError, nguồn Ready, bytes nguồn không đổi; sau đó export đủ và input mới được lưu | bản sao lệch → `ARCHIVE_FAILED:INTEGRITY` (dừng nguồn khỏe) |

Kết quả ([before-after](before-after.json), [offline](offline-results.txt)):
- Source cuối: 42/42 method đạt.
- Snapshot fix-02: 38 method cũ đạt; 4 method mới fail (1 FAIL, 3 ERROR) với 30 subtest fail đúng lý do. Các control đạt ở cả hai.

## Probe Codex nguyên bản, assert theo giá trị

[probe-results](probe-results.json), [asserter](../../../../scratch/zer9/claude-fix03/assert_probes.py):
- `read_http.py`: GET 503 NOT_DURABLE, failure `OSError`, readyz 503, POST sau 503. Trên fix-02: RemoteDisconnected, readyz 200, POST 201.
- `read_matrix.py`, 10 hàng: records, export_late và export_global của H/O chuyển sang ArchiveFailure, không Ready (6 hàng trước đây bỏ sót). Seal giữ ArchiveFailure/OSError (2 control). Destination giữ FileExistsError và Ready (2 control).
- `deep_http.py` và `h_partial_http.py` (fix-01) giữ đúng giá trị Codex đã assert.

## Kiểm khác

| Kiểm | Kết quả |
|---|---|
| Core | 22/22 |
| Agent HTTP (venv) | 4/4 |
| `reconcile_raw.py` | 57/58 như trước: check duy nhất fail so receipt live-11 với file hiện tại (7 file, có store.py). Receipt so với bản trước fix-01 PASS 10/10; không sửa receipt |
| py_compile, `git diff --check`, whitespace, link | đạt (link chạy lại sau khi tạo fix-03, cuối [offline](offline-results.txt)) |
| Bash 37 / Nemesis 3 / ZER-37 | không chạy lại: file không đổi từ fix-02, không import `event_pipeline`; gateway/consumer không đổi |

## Phạm vi, hash, bảo vệ

[delta-manifest](delta-manifest.json). Đổi đúng 4 file trong allowlist: `store.py`, regression, runbook, verification. Ngoài ra chỉ thêm fix-03/scratch, append note và prepend NOW. `gateway.py`, audit, contract, client/adapters/telemetry, Gaia/Hephaestus, verifier, manifest, CI, Dockerfile, requirements và setup không đổi.

Kiểm bảo vệ:
- `codex-fix02-review/**` khớp checksums 11/11;
- `codex-fix01-review/**` khớp 9/9;
- `fix-02/**` khớp hash bàn giao 5/5; `fix-01/**` khớp 6/6;
- `evidence-checksums.json` 61/62, chỉ lệch `verification.md` (được phép);
- không thay đổi ngoài phạm vi. HEAD `2af4d33`, staged rỗng.

## Giới hạn

- Lỗi I/O chỉ giả lập bằng patch; chưa thử EIO/ENOSPC trên đĩa thật, mất điện hay NFS/PVC.
- Trạng thái lỗi nằm trong một process. Lỗi đọc thoáng qua được xóa bằng restart nếu file đọc lại được; lỗi bền làm archive không mở.
- Export thất bại có thể để lại bản sao dở ở đích, không có export.json hoàn tất. Operator bỏ thư mục đó và export lại.
- Lỗi đọc trong `__init__` vẫn làm archive không mở (ArchiveFailure hoặc OSError); không cần sticky vì process chưa phục vụ.
- Các giới hạn của fix-01/fix-02 giữ nguyên: một process, fsync thư mục trên Windows, `MAX_DEPTH`, ZR9-05/06/10, `publish-images` chưa `needs` R1, CI/image chưa chạy.

Bước tiếp:
1. Codex retest độc lập fix-03.
2. Khi offline khép, Codex chuẩn bị kiểm tích hợp trên source cuối và ranh giới actor.
3. Sau đó mới đến các cổng publication và nghiệm thu của Hoàng.
