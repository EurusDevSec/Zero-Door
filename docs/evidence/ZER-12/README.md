# ZER-12 + ZER-40 — gói Codex

Đầu mối [verification](verification.md): AC cha/con, thay đổi, môi trường đúng lock, kết quả và giới hạn. Đây là implementation + kiểm offline, chưa Done.

- [Source/evidence hashes](source-manifest.json)
- [Tổng hợp kết quả](result-summary.json)
- [Metadata pin chính thức](pin-metadata.json)
- [Runbook](../../runbooks/r1-command-guards.md)
- [Kiểm gói chỉ đọc](verify_package.py)

Log được copy và chuẩn hóa newline LF; bản gốc giữ trong scratch/zer12/codex/results. Không sửa receipt lịch sử ZER-9/37. Binary Linux chỉ build, không chạy; không có model call hay thao tác lab trong gói này.

Reviewer đọc bàn giao cuối [issue note](../../delivery/milestones/R1-measurement/guards-and-ci.md). Kiểm cả ba AC của ZER-12 và AC-01 ZER-40 dùng chung evidence AC-03; không chỉ review một child hoặc chỉ đếm test.
