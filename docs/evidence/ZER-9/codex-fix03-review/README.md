# Codex retest ZER-9 fix-03 — 19/10/2026

**READY_OFFLINE / không có finding mới chặn gói fix-03.** FX02-R1 đã khép trong phạm vi offline được giao. ZER-9 chưa Done: source fix-01..03 chưa có receipt runtime trên actor thật, CI/merge/Hoàng nghiệm thu còn thiếu. Writer Codex; không sửa source sản phẩm trong lượt review.

## Target và bằng chứng

- Local fix-03 so snapshot fix-02, trên nhánh zer-9-event-pipeline, HEAD 2af4d33bf02c59d7802901d523b1bb2eb39f05a3; staged rỗng. Không có commit mới hoặc merge-base mới. Không resolve được origin/HEAD; phạm vi ở đây là snapshot delta đã chỉ định, không giả định default branch.
- Snapshot store fix-02 2b9a051a932e14c1b6218e6798e14f84c13b7e5fc6ca2ee8e584a5f2a70f5d7c; source cuối de30c0acd10679da38b3864c562e184fa4cddb16ee3c3a3d2befd31d68f157c6.
- [Intake](intake.json): 44 mục source/protected khớp delta fix-03, không lệch; note/NOW có handoff nối/prepend nên được tách khỏi phép so full-file. Đúng bốn file thay đổi: store, regression, runbook, verification. [Diff store](store.diff), [diff tests](tests.diff).
- README Claude SHA-256 2ac57681e238cd60925a6303eba55f86b7fe5a8bb87b624e4c3e700cafc064d7; delta 4150a99e6683917399f76fdf1d0ba441bb74c501916a5503a99ac60c919e31fa.
- Linear Zero Door đọc trực tiếp: ZER-9 In Review, AC-01..03 còn unchecked. Không ghi Linear.

## Finding và xác nhận

Không có finding mới cần sửa trước bước runtime. Rà đầy đủ diff và consumer trực tiếp; một domain lưu archive, review kết hợp kiến trúc, Python, test, Done và độ đơn giản.

- [entry/reading](../../../../agent-orchestrator/event_pipeline/store.py#L73) chuyển lỗi stat/open/read phía nguồn thành ArchiveFailure; lookup/path/run_dir và records/seal/export đặt failure dưới khóa. File tùy chọn vắng vẫn hợp lệ; lỗi quyền/EIO không bị coi là trống.
- [copy](../../../../agent-orchestrator/event_pipeline/store.py#L493) tách đọc nguồn khỏi ghi đích. Digest của luồng nguồn lệch là lỗi archive; bản sao ở đích lệch hay lỗi ghi/fsync/chmod là lỗi export, không làm dừng nguồn khỏe. HTTP gateway cũ đã bắt ArchiveFailure thành 503, nên không cần sửa gateway.
- Giữ nguyên cơ chế bytes/hash, duplicate, quarantine trước commit, seal fence và refusal sau lỗi. Không truncate/reset hoặc sửa receipt để làm xanh.

## Actual kiểm độc lập

[Log retest](retest.txt) được Codex chạy lại bằng Bash, output riêng. Runner không fail-fast; đã đọc từng exit và kết quả, không lấy exit cuối làm PASS toàn gói.

| Kiểm | Actual |
|---|---|
| Core | 22/22 PASS |
| Regression source cuối | 42/42 PASS |
| Regression cùng test trên snapshot fix-02 | 38 method cũ PASS, 4 method mới fail ở 30 subcase (6 failure + 24 error); control đúng như dự kiến |
| Bốn probe Codex nguyên bản | 4/4 assert theo JSON actual; xem [probes](probes.json) |
| Actor HTTP offline với dependencies hiện có | 4/4 PASS |
| Probe bổ sung Codex độc lập | 6/6 PASS; xem [source](extended.py), [actual](extended.json) |
| Syntax / diff-check / whitespace / relative links | PASS |

Probe bổ sung dùng fixture sự kiện hiện có nhưng tự viết fault injection và assertions: H và O, PermissionError phía nguồn, luồng copy nguồn bị đổi bytes sau summary, và ghi đích dở rồi ENOSPC. Hai lỗi nguồn dừng archive, từ chối ghi sau, bytes nguồn không đổi. Ghi dở đích chỉ làm export thất bại; archive Ready và export đầy đủ vào đích mới đạt. Đây là fake I/O trên thư mục tạm, không phải lỗi đĩa/PVC thật.

Bốn probe cũ: read_http GET503/readyz503/POST503; ma trận10 hàng gồm6 nhánh nguồn đã sửa,2 seal control,2 destination control; deep HTTP422 có quarantine/commit/event kế tiếp; H partial503 và không nhận ghi tiếp. Các file probe lịch sử nguyên hash.

reconcile_raw vẫn 57/58: chỉ check source hiện tại so receipt live-11 lệch7 file vì đã sửa. Receipt so đúng snapshot trước fix-01 PASS10/10. Không dùng receipt cũ làm bằng chứng source mới. Không chạy lại Bash37/Nemesis3/ZER-37 vừa PASS ở lượt trước vì file/consumer liên quan không đổi.

## Hash và graph

[Protection](protection.json): Codex fix-01 review9/9, fix-02 review11/11; các artifact được delta fix-01/fix-02/fix-03 liệt kê đều khớp. historical checksum61/62 chỉ verification.md lệch theo allowlist. Intake còn xác nhận README/delta cũ và raw/receipt.

[GitNexus](graph.json) cập nhật cục bộ --pdg --index-only thành công, commit trên và indexed_at 2026-10-19T12:42:34.538Z; 9530 symbols/123 flows. Query → context lookup (4 caller ingest/reject/seal/sealed, entry/fail) → upstream impact mọi symbol đổi; direct caller ngoài diff (gateway, read_file/init và test/probe) đối chiếu source/test. Một số receiver typing là lower-bound; sealed không có caller trong graph nhưng Gateway.submit gọi trực tiếp, được test Kafka thực thi offline. detect_changes toàn checkout87symbol/14trackedfile/15flow gồm dirty ngoài phạm vi; không dùng count đó làm review delta, vì source mới untracked. explain store0finding không chứng minh an toàn; PDG _export41edge xác nhận hai nhánh digest và ghi bản sao khác nhau, source/test/probe là bằng chứng hành vi. Graph có cảnh báo7 property timestamp khác ngôn ngữ; closure/property/implicit flows vẫn hạn chế.

## Bước còn lại

[Phạm vi runtime đề xuất](runtime-scope.md) cụ thể hóa kế hoạch actor cũ cho source cuối. Chưa được chạy, chưa là quyền vận hành. Giữ việc trên chính pod Gaia/Hephaestus và recorder, không thay bằng process host hoặc chỉ observer. Sau runtime đạt mới publication/CI/merge/Hoàng nghiệm thu trong quyền tương ứng. AC-01 kế thừa ZER-37; phần triển khai AC-02/03 đạt offline nhưng chưa chốt acceptance.

Giới hạn giữ nguyên: một process/archive, Windows không fsync thư mục, không thử mất điện, export lỗi có thể để bản sao dở, node server profile không chứng minh toàn cluster, Kafka chưa auth/global policy, không có bằng chứng KPI/detection/healing/LLM từ lượt này.
