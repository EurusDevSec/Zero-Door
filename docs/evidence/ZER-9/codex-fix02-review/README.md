# Codex retest fix-02 — ZER-9 — 19/10/2026

**NOT_READY — còn một P2 thuộc FX02.** Hai phản ví dụ cũ đã đạt, nhưng việc chuyển archive sang trạng thái lỗi chưa phủ đường đọc nguồn. Không yêu cầu chạy lab khi lỗi này còn mở. Source sau fix-02 chưa có bằng chứng runtime/CI/merge hoặc Hoàng nghiệm thu.

## Finding P2: FX02-R1 — lỗi đọc nguồn chưa làm archive dừng

- [store.py:353–356](../../../../agent-orchestrator/event_pipeline/store.py#L353): records chỉ bắt ArchiveFailure, bỏ lọt OSError khi open/read raw. [export:430–451](../../../../agent-orchestrator/event_pipeline/store.py#L430) cũng chỉ bắt ArchiveFailure; lỗi nguồn tại summary/file_sha/copyfile đối với late/global quarantine không được đổi sang failure. Seal đã bắt OSError đúng.
- [Probe HTTP độc lập](read_http.py), [kết quả](read_http.json): giả lập EIO khi đọc đúng file O.jsonl qua GET /events; client nhận RemoteDisconnected, archive.failure vẫn null, GET /readyz vẫn 200 READY; POST event tốt sau đó trả 201 RECORDED. Không phải thử ổ đĩa hỏng thật.
- [Ma trận độc lập H/O](read_matrix.py), [kết quả](read_matrix.json): records, export đọc late và export đọc quarantine toàn archive đều ném OSError nhưng readiness vẫn true (6/6 nhánh nguồn chưa dừng). Cùng lỗi ở seal tạo ArchiveFailure, readiness false (2/2 đối chứng). Thư mục export đích đã tồn tại trả FileExistsError và archive còn Ready (2/2 đối chứng đúng).
- Yêu cầu đã có trong gói fix-02: I/O/integrity của archive phải sticky, không tiếp tục ghi sau khi biết nguồn bằng chứng không đọc được. Runbook hiện tại dòng176–183 và handoff tuyên bố rộng hơn code. Đây là phần còn thiếu của FX02, không là yêu cầu mới về mất điện hay disk benchmark.
- Nguyên nhân: bắt lỗi rải ở caller theo loại exception, chưa phân biệt nhất quán lỗi đọc nguồn archive với lỗi đích export. Test mới phủ append/fsync và dữ liệu hỏng, chưa giả lập OSError trên đường đọc nguồn.
- Sửa: đưa lỗi I/O nguồn về ArchiveFailure + fail dưới khóa tại ranh giới đọc nguồn dùng chung hoặc các đường tương ứng; HTTP phải trả503; request sau không thêm bytes. Không bắt toàn bộ OSError quanh export rồi dừng archive vì lỗi ở đích; không sửa/truncate nguồn, không đổi lỗi thành thành công.

## Phạm vi đã kiểm

- Local delta fix-01 → fix-02 trên HEAD 2af4d33bf02c59d7802901d523b1bb2eb39f05a3, nhánh zer-9-event-pipeline, staged rỗng. Sáu file đúng allowlist. [Intake](intake.json) khóa hash; [protection](protection.json): 41 file source/protected khớp delta, 3 artifact fix-02 khớp hash, Codex fix-01 9/9, fix-01 4 artifact được manifest liệt kê khớp. Historical checksums61/62, chỉ verification.md được phép cập nhật. Các bàn giao note/NOW thay sau manifest theo thiết kế.
- Đã đọc diff source/test và caller trực tiếp của write/usable/fail/depth, luồng Gateway submit/admit/KafkaBridge handle/record, records/seal/export và audit. Ba code file thuộc cùng miền event pipeline, review inline cả correctness, dữ liệu/quyền, regression, độ đơn giản và DoD; không sửa sản phẩm.
- GitNexus refresh local --pdg --index-only thành công: 9,191nodes/23,603edges/109flows. [Graph](graph.json): query/context/upstream impact có tests, explain ba code file, PDG guard too_deep. Index có receiver typing gaps; graph không bao phủ mọi dynamic call/untracked diff. detect_changes toàn working tree báo82symbols/14trackedfiles/15affected, gồm dirty ngoài phạm vi; không dùng số đó như phạm vi delta fix-02. Explain0 finding không phải chứng minh an toàn; kết luận dựa source và probe.

## Kiểm độc lập

[Kết quả mới](retest.txt), không ghi đè log Claude. Chạy runner đã đọc bằng Bash; mọi HTTP đều loopback, Kafka giả trong bộ nhớ.

| Kiểm | Actual |
|---|---|
| Core / regression source cuối | 22/22 / 38/38 |
| Cùng regression trên snapshot fix-01 | 8 method fail như mong đợi: 7 FAIL,1 ERROR; unittest đếm9FAIL subtest +1ERROR. Control data_errors đạt. Không sửa expected để làm đẹp |
| Hai probe Codex cũ nguyên bản | [Assert theo giá trị](old-probes-asserted.json) đạt: deep422/quarantine1/commit2/next good; H partial503/ready503/next503/ArchiveFailure |
| Agent HTTP | 4/4 |
| Bash / Nemesis / ZER-37 | 37PASS / 3/3 / 9checks đạt |
| Raw lịch sử | 57/58, chỉ check source hiện tại khác receipt live-11 (7 file). Source receipt so đúng snapshot trước fix-01 đạt10/10 |
| Syntax/help/YAML/diff/whitespace/link | đạt; verifier thiếu --live exit2 đúng |
| Probe đọc nguồn mới | tái hiện FX02-R1 như trên |

FX01 được khép offline: guard độ sâu bằng vòng lặp trước validator, reject giữ bytes/hash an toàn; không đổi contract.py. FX02 partial append/fsync, quarantine và Kafka poison/write failure đã sửa đúng. Nhánh SECRET sạch/rò/thiếu bằng chứng đạt. Chưa khép toàn FX02 vì finding trên.

## Còn lại

Sau sửa đọc nguồn, retest tập trung và chuẩn bị profile Gaia/Hephaestus thật trong cluster trên source cuối; live-11 chỉ chứng minh profile cũ có agent process trên host. Không tự miễn nghĩa vụ actor H/O. CI/image build, publication/merge và Hoàng chấp nhận vẫn là các bước riêng. Không chạy lab/API/Doppler/Docker, không Git publication hoặc Linear write trong lượt này. Live Linear đọc đầu lượt: ZER-9 In Review; AC vẫn unchecked. Không thay trạng thái.
