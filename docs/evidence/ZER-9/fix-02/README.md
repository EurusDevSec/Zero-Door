# ZER-9 fix-02 — Claude sửa FX01/FX02 sau Codex retest (19/10/2026)

**Verdict: READY_FOR_CODEX_RETEST.** Hai P2 của [Codex retest fix-01](../codex-fix01-review/README.md) đã khép offline. Không tự nhận READY_FOR_HOANG_ACCEPTANCE hay Done: source sau fix-01/fix-02 chưa chạy live, CI chưa chạy, bằng chứng trên chính actor Gaia/Hephaestus chưa có. Mọi kiểm ở đây là offline (HTTP loopback, Kafka giả trong bộ nhớ, fault injection bằng patch). Đây không phải thử đĩa hỏng hay mất điện thật.

## Baseline lúc nhận writer

- HEAD `2af4d33`, nhánh `zer-9-event-pipeline`, staged rỗng. `git status` giống hệt lúc nhận và lúc bàn giao.
- Hash mọi file trong [fix-01 delta manifest](../fix-01/delta-manifest.json) khớp bản sau fix-01 (không lệch). Note và NOW chỉ khác vì bàn giao fix-01 được nối sau manifest.
- Bản sao source/test fix-01 nằm ở `scratch/zer9/claude-fix02/baseline-src/`, ảnh chụp hash ở `scratch/zer9/claude-fix02/baseline.json`. Đây là baseline fix-02, khác bản trước fix-01 của live-11 (`scratch/zer9/claude-fix/baseline-src/`).

## FX01 — JSON lồng sâu thoát khỏi quarantine

**Nguyên nhân.** JSON hợp lệ 2.053 byte, lồng 520 tầng, qua strict decode và canonical. Sau đó `forbidden_keys` của validator đệ quy và ném RecursionError. Kết quả: HTTP trả 503 và không có gì vào quarantine; recorder Kafka dừng ở offset 0 và chặn event kế tiếp.

**Sửa** (không đụng `contract.py`, không nâng recursionlimit, không bỏ kiểm khóa cấm):
- [`too_deep`](../../../../agent-orchestrator/event_pipeline/store.py#L82) kiểm độ sâu container bằng vòng lặp, không đệ quy. Giới hạn [`MAX_DEPTH = 32`](../../../../agent-orchestrator/event_pipeline/store.py#L34) tính cho cả envelope; live-11 chỉ sâu 4.
- Kiểm này chạy trước validator, binding và audit ở [`Gateway.check`](../../../../agent-orchestrator/event_pipeline/gateway.py#L41) (HTTP và Kafka) và [`Archive.ingest`](../../../../agent-orchestrator/event_pipeline/store.py#L318) (gọi trực tiếp). Vượt giới hạn là INVALID, một classification có sẵn trong contract.
- [`reject`](../../../../agent-orchestrator/event_pipeline/store.py#L282) không lưu bản parse của input quá sâu. Nó lưu bytes gốc kèm `raw_sha256`/`raw_hex`. Input đã xác thực (token HTTP, HMAC Kafka) được gán run/nguồn như fix-01. Gọi trực tiếp không có bytes gốc thì [`render`](../../../../agent-orchestrator/event_pipeline/store.py#L99) thử canonical, rồi repr, rồi bytes rỗng có `raw_kind`; hàm này không ném lỗi, nên đường reject/hash không chết lại.
- JSON sâu tới mức decoder không đọc được vẫn là INVALID ở phạm vi archive như fix-01, không gán run.
- Lỗi I/O và lỗi chương trình không bị đổi thành Rejected; chỉ giới hạn độ sâu tường minh ra INVALID.

**Test** ([`DepthLimitTests`](../../../../tests/test_event_pipeline_regressions.py#L953)):
- Kafka giả ký đúng, list 520 và dict 520: decode không báo lỗi. Cả hai được quarantine với bytes/hash, gán run và `detector`, không có `envelope`. Hook ở commit xác nhận mỗi offset chỉ được commit khi dòng tương ứng đã nằm trên đĩa. Event tốt kế tiếp được ghi. Restart bridge và restart process đều không gặp lại poison; offset vẫn 3.
- HTTP có token, cả O có Kafka và O ghi trực tiếp: list 520, dict 520 và 33 tầng đều ra 422 INVALID với đúng bytes trong quarantine, không publish lên Kafka. Ca 32 tầng vẫn được nhận (control).
- `Archive.ingest` trực tiếp với dict 520 tầng (lưu canonical) và 5.000 tầng (vượt cả `json.dumps`/repr, lưu `unrepresentable`) đều Rejected INVALID, không ném RecursionError. Event tốt sau đó vẫn RECORDED; archive mở lại được.

## FX02 — H vẫn nhận thành công sau append ghi dở

**Nguyên nhân.** Lỗi append chỉ dừng recorder Kafka. Gateway H và O ghi trực tiếp vẫn READY, request sau trả 201 và nối vào sau dòng bị cắt; `records()` ném JSONDecodeError.

**Sửa** (archive tự giữ trạng thái lỗi, áp chung cho H/O, có hay không Kafka):
- Mọi lần append đi qua [`Archive.write`](../../../../agent-orchestrator/event_pipeline/store.py#L205). Bất kỳ exception nào ở đây (ghi, flush, fsync) đều qua [`fail`](../../../../agent-orchestrator/event_pipeline/store.py#L198) đặt `failure` dưới khóa và ném ArchiveFailure.
- Tạo thư mục run, seal (ghi hoặc đọc), `records()` và export gặp dòng hỏng hoặc hash lệch cũng đặt `failure` như vậy.
- [`usable`](../../../../agent-orchestrator/event_pipeline/store.py#L194) chạy đầu `Gateway.check`, `ingest`, `reject`, `records`, `seal` và export. Khi đã lỗi, không gì được trả thành công hoặc ghi thêm.
- [`readiness`](../../../../agent-orchestrator/event_pipeline/gateway.py#L120) trả 503 `ARCHIVE_FAILED:<lý do>`; `/livez` vẫn 200.
- [`iter_file`](../../../../agent-orchestrator/event_pipeline/store.py#L248) đổi dòng không đọc được hoặc không phải object thành ArchiveFailure. Khi mở lại, dòng bị cắt hoặc hỏng làm archive không mở. Code không truncate, xóa lỗi, reset hay sửa file.
- Lỗi dữ liệu đã quarantine thành công và lỗi chương trình xảy ra trước khi ghi không làm archive dừng. Lỗi ở thư mục đích của export (ví dụ đã tồn tại) cũng không.
- Phục hồi là restart process, việc của operator. Restart bridge trong cùng process không xóa được lỗi. Các ca operator phải xử lý ghi ở [runbook](../../../runbooks/r1-event-pipeline.md#L176).

**Test** ([`StickyFailureTests`](../../../../tests/test_event_pipeline_regressions.py#L1044), cùng [test I/O cũ đã cập nhật](../../../../tests/test_event_pipeline_regressions.py#L309)):
- H qua HTTP và O ghi trực tiếp, append ghi dở rồi OSError. Control trước lỗi: input sai ra 422, event tốt ra 201, readyz 200. Sau lỗi:
  - request đầu 503; readyz 503 `ARCHIVE_FAILED:OSError`; livez 200;
  - request hợp lệ sau đó 503, input sai 503 (không quarantine được), `/seal` 503;
  - `records()` và export ném ArchiveFailure, không tạo thư mục export;
  - mọi file `.jsonl` không thêm byte;
  - close/reopen ném ArchiveFailure, bytes dòng bị cắt giữ nguyên.
- fsync lỗi sau khi đã ghi đủ dòng: dừng như trên. Khi mở lại, dòng đủ được đọc lại; producer đã nhận 503 thì gửi lại thành DUPLICATE.
- Append quarantine ghi dở (NaN): request đó 503 và archive dừng.
- Recorder Kafka gặp append ghi dở: bridge dừng, offset 0; HTTP 503 và không publish thêm. Restart bridge trong process vẫn lỗi, không commit; mở lại archive bị từ chối.
- Lỗi dữ liệu (RUN_CONTEXT_MISSING, không decode được, không phải object) ra 422 và archive vẫn chạy. Lỗi chương trình trước khi ghi ra 503 nhưng `failure` vẫn None. Seal được, và export vào thư mục đã tồn tại không làm archive dừng.
- [`test_io_failure_is_not_acknowledged_and_turns_readiness_off`](../../../../tests/test_event_pipeline_regressions.py#L309) của fix-01 được sửa theo yêu cầu mới. Restart bridge trong process không còn phục hồi; phải restart process. Archive được kiểm lại vì không có byte nào được ghi, rồi Kafka giao lại message, event được ghi đúng một lần và readyz 200.

## Nhánh SECRET sạch của audit

[`audit.py`](../../../../agent-orchestrator/event_pipeline/audit.py#L101): SECRET không gặp ở O và không `o_visible` trước đây rơi xuống nhánh `else` và bị báo UNKNOWN_MANIFEST_CLASS. Nay nó là sạch. Gặp ở O hoặc `o_visible` vẫn là HARNESS_SECRET; lớp lạ, thiếu manifest hoặc thiếu bằng chứng quyền vẫn là UNKNOWN ([test](../../../../tests/test_event_pipeline_regressions.py#L846)). Chỉ đổi một nhánh, không viết lại audit.

## Retest gom một lượt trên source cuối

[Kết quả đầy đủ](offline-results.txt), chạy bằng `scratch/zer9/claude-fix02/retest.sh`.

| Kiểm | Kết quả |
|---|---|
| Core `test_event_pipeline.py` | 22/22 |
| Regression cập nhật | 38/38 (30 cũ + 7 FX01/FX02 + 1 SECRET) |
| Cùng file regression trên snapshot fix-01 | 30 ok, 7 FAIL, 1 ERROR; đủ 8 test mới/sửa fail đúng lý do, control `data_errors` đạt ([bảng](before-after.json)) |
| Probe Codex `deep_http.py`, chạy nguyên bản từ root | 422 INVALID; quarantine 1; recorder không lỗi; commit 2; readyz 200; event kế tiếp được ghi ([so với fix-01](probe-results.json)) |
| Probe Codex `h_partial_http.py`, chạy nguyên bản | đầu 503; readyz 503 `ARCHIVE_FAILED:OSError`; request sau 503; đọc raw ra ArchiveFailure |
| Agent HTTP (venv có sẵn) | 4/4 |
| Bash / Nemesis / ZER-37 release | 37 PASS / 3/3 / 9/9 |
| `reconcile_raw.py` nguyên bản | 57/58: chỉ check source receipt live-11 so với file hiện tại, lệch đúng 7 file đã đổi từ fix-01 (fix-02 chỉ đổi 3 trong số đó) |
| Source receipt live-11 so với bản trước fix-01 | PASS 10/10 |
| Verifier `--help` / thiếu `--live` | không vào lab / exit 2 đúng |
| YAML, parse source, `git diff --check`, whitespace file chưa track | 13 document, đạt, sạch, sạch |
| Link tương đối | chạy lại sau khi tạo fix-02, ghi ở cuối kết quả |

Probe Codex đổi kỳ vọng đúng như gói yêu cầu: offset tiến, quarantine có bytes và event kế tiếp được ghi, thay vì báo lỗi. Script và kết quả gốc của Codex không bị sửa.

## Phạm vi và file được bảo vệ

Chi tiết trong [delta manifest](delta-manifest.json): hash fix-01 → fix-02 và mục `protection`.
- Đổi đúng sáu file trong allowlist:
  - `gateway.py` `bef7f517…` → `74fef63b…`
  - `store.py` `e1426d0d…` → `2b9a051a…`
  - `audit.py` `313681f3…` → `b7ebc319…`
  - regression `82c70cf7…` → `dd1dc89e…`
  - runbook `2fda69ee…` → `302b0df7…`
  - `verification.md` `b31ef06f…` → `65717a65…`
- Không đổi ngoài allowlist: `contract.py`, `__init__.py`, client/adapters/telemetry, Gaia/Hephaestus, verifier, manifest, CI, Dockerfile, requirements và setup scripts.
- `codex-fix01-review/**` khớp checksums của chính nó 9/9.
- `fix-01/**` khớp hash trong bàn giao fix-01 6/6.
- `evidence-checksums.json` 61/62: chỉ lệch `verification.md`, là file được phép cập nhật; snapshot đó không bị sửa.
- Raw, receipt và history live-11 không đổi, nằm trong 61 file khớp.
- Không cài package. Không Docker/Kube/Kafka thật/port-forward/verifier `--live`/LLM/Doppler/API. Không stage/commit/push/PR/Linear/tin nhắn.

## Giới hạn còn lại

- Trạng thái lỗi nằm trong một process. Restart xóa nó; khi đó archive kiểm lại mọi dòng, nhưng dòng đầy đủ mà fsync đã báo lỗi vẫn được nhận lại. Độ bền của dòng đó khi mất điện chưa được chứng minh. Windows không fsync thư mục.
- Fault injection chỉ patch `Archive.append`/`os.fsync`; chưa thử ENOSPC, EIO hay mất điện thật.
- `MAX_DEPTH` 32 là giới hạn transport, không phải điều khoản contract; contract 1.0.0 không đổi. Event hợp lệ sâu hơn 32 tầng sẽ bị INVALID. Live-11 và mọi payload hiện tại đều nông hơn nhiều.
- Các giới hạn đã khai từ fix-01 giữ nguyên:
  - ZR9-10: client chặn vòng async và đọc cả run;
  - hàng rào seal nằm trong RAM của một process, một trial mỗi process;
  - ZR9-05/06: chưa có bằng chứng quyền thật trên actor Gaia/Hephaestus;
  - `publish-images` chưa `needs` hai job R1;
  - CI và image build chưa chạy.

## Bước tiếp

- Codex retest độc lập fix-02: delta, các đường lỗi và probe. Sau đó mới chuẩn bị kiểm tích hợp trên revision cuối và ranh giới actor tương ứng.
- Hoàng giữ quyền nghiệm thu, claim và quyết định về bằng chứng runtime trên chính actor. Chưa có miễn bằng chứng runtime.
