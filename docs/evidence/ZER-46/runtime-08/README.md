# ZER-46 runtime08 — dừng memory PSI guard, cleanup sạch

28/10/2026. **NOT_MET_GUARD_STOP / OWNED_RESOURCE_CLEAN / NOT_READY_FOR_PUBLICATION.** Hoàng duyệt đúng gói collector Pod/UID. Attempt kết thúc sau203,05giây; không tự chạy lại.

## Kết quả và giới hạn

- Preflight120giây đạt, cache đúng artifact04;0 build/import/pull. Fixture trên agent-0 có hook firewall và Ready; collector cleanup đã đọc đúng Pod/UID.
- Có33 mẫu guard. Một mẫu PSI avg10=16,37 vượt ngưỡng5, trong khi host available3.533.672.448byte≈3,29GiB và WSL2.339.372KiB≈2,23GiB vẫn trên ngưỡng1GiB. Guard dừng đúng; không tăng ngưỡng hoặc suy thiếu RAM dung lượng.
- Counter admission fixture=1; **một remote client exec đã dispatch rồi bị guard hủy**, không có client response receipt. Cleanup log không có record khớp correlation e29ae6606f7c46a0b0ebbf9c4bb16408. Kết quả HTTP đầu tiên là **UNKNOWN**, không được ghi0 request thực sự gửi hay HTTP PASS. Raw0070 giữ lỗi cancellation.
- 0 writer process,0 containment rule,0 TCP controls; chưa thực hiện block/benign/TTL/replacement/replay/expiry trong08. Kết quả partial07 giữ riêng, không cộng hai lượt thành một PASS.
- 15 Boutique scriptHTTP; ba observer flow đạt tiêu chí function/active-time của harness, gồm hai flow sau cleanup. Không là R1 wall-SLO/KPI/recovery/end-to-end PASS; các flag formal vẫn false.

## Chẩn đoán đã có

Snapshot đúng bốn owned Pod UID tại lúc guard dừng: sourceA memory PSI some/full avg10=48,64; fixture/proxy/sourceB=0. SourceA memory.current17.530.880byte, memory.max50.331.648byte; memory.events max/oom/oom_kill đều0 ở bốn Pod. SourceA có CPU throttle44/56 periods,throttled3.954ms; snapshot không chứng minh CPU là nguyên nhân duy nhất của memory stall hoặc diễn biến peak trước đó. Dữ liệu tập trung vào client execution, không đủ căn cứ sửa shared services/WSL/CNI hay yêu cầu giải phóng RAM thêm.

Đây là snapshot sau phát hiện guard, không có counter delta trước/sau cho mọi cgroup, nên giới hạn nhân quả được giữ. Không tạo thêm workload để chẩn đoán sau stop.

## Cleanup và evidence

Xóa namespace bằng UID096728fe-7e47-497b-bf01-bb2a8043a548 và đọc lại absent. Shared spec/UID/restart và3PVC giữ nguyên; không có writer được khởi động. Owned resource cleanup CLEAN. Raw acceptance NOT_MET, guard violation và missing response giữ nguyên.

[Reconciliation offline riêng với runner](independent-verification.json) kiểm script hashes, approval/source manifest, cancellation/UNKNOWN, guard/cgroup và UID cleanup từ raw. Chưa review bởi người/agent độc lập. Utility reconcile_completed_protocol.py chỉ dành khi có đủ chuỗi artifact; không dùng để nghiệm thu lượt08 thiếu dữ liệu.

**ZER-46 chưa đạt AC toàn chuỗi và chưa sẵn sàng publication.** Còn thiếu trace đầy đủ sau replacement, writer restart/replay, expiry/unblock và policy API+mount cleanup trong một lượt hợp lệ. Lượt08 đã đóng; chưa chuẩn bị/duyệt/chạy lượt09. Bước tiếp theo cần chốt readiness của client A trước khi đề nghị lượt containment mới, giữ mọi guard/AC.
