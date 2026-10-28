# ZER-46 runtime-05 — cached-only, dừng policy gate

28/10/2026. **NOT_MET / CLEAN_OWNED_RESOURCES_ONLY / NOT_READY_FOR_PUBLICATION.**
Hoàng duyệt cached-fixture-proposal.md; attempt đã kết thúc sau 304,00 giây, không tự chạy lại.

- 0 build/import/pull; cache đúng artifact04, mọi workload imagePullPolicy=Never. Proxy, source A và B Ready tuần tự.
- Fixture Running trên server-0, không restart, nhưng 32 lần kiểm trong khoảng 110 giây không thấy rule KUBE-POD-FW cho Pod. Startup gate không được mở.
- 52 mẫu guard: host tối thiểu 4.139.417.600 byte, WSL tối thiểu 2.398.732 KiB, PSI avg10 tối đa 0. RAM không là điểm chặn của attempt này.
- 0 fixture HTTP, 0 TCP controls, 0 writer; chưa thử block, benign, TTL hoặc restart. Boutique observer 9 HTTP, chưa đạt sức khỏe; không có KPI/end-to-end PASS.
- Xóa đúng UID namespace 45a7bd82-9c56-4d02-948a-a06f7d8f6293 và xác nhận absent; shared spec/UID/restart và 3 PVC giữ nguyên. Không còn tài nguyên của lượt thử.

[Đối chiếu raw độc lập](independent-verification.json) dùng reconcile_runtime05.py (offline, không gọi lab), kiểm command receipts, script snapshots, guard, pull policy, UID delete và inventory. Đây là reconciliation riêng với receipt runner, chưa phải review bởi người/agent khác. Raw và scripts giữ nguyên.

Chẩn đoán chỉ đọc sau attempt tại [gate-audit](../gate-audit/README.md). AC-01/02 vẫn chưa đạt trên revision mới.
