# ZER-37 — Verification và nghiệm thu schema 1.0.0

**Verdict: PASS cho thiết kế/offline.** Hoàng đã chấp nhận contract và bảy quy ước ở mục11 trong chat ngày19/10/2026, sau audit Codex. Chấp thuận bao gồm khóa1.0.0, commit/push, PR/merge sau CI đạt và cập nhật ZER-37 Done. Không cấp quyền chạy lab/API hoặc mở triển khai producer/consumer.

[Contract đã khóa](../../design/r1-event-contract.md) · [Review và handoff](../../delivery/milestones/R1-measurement/event-contract.md)

## AC và kết quả

| AC-01 | Evidence | Kết quả |
| --- | --- | --- |
| ID/cardinality/correlation | Contract mục3/6; E13–E16, X1–X3, U1, W1–W4 | PASS offline |
| Schema/version/timestamp/source | Envelope mục4/5, ba envelope JSON, C1/C2/C3/C5/C6, E17–E20 | PASS offline |
| Effect/detect/action/recovery/stop tách nguồn | Bảng5.2, miền trạng thái mục7; E01–E12 | PASS offline |
| SUCCESS/FAILED/PARTIAL/TIMEOUT không tự tạo recovery | E02/E03, V1/V2, R1–R5; phản ví dụ Codex | PASS offline |
| Review và Hoàng chấp nhận | RV37-01…05 đóng sau retest; chấp thuận trực tiếp trong chat | Đạt |

## Chạy lại

Từ root của checkout, Python3.11+, chỉ thư viện chuẩn. Không cần credential, Docker, Kubernetes, Kafka hoặc mạng.

    python -I -B docs/evidence/ZER-37/check_contract.py
    python -I -B docs/evidence/ZER-37/independent_checks.py
    python -I -B docs/evidence/ZER-37/verify_release.py

- Bộ kiểm chính: 62 case +3 aggregate, khớp238/238 kỳ vọng;32/32 mutant bị bắt trên1.0.0.
- Phản ví dụ độc lập Codex:10/10 expectation_met, gồm đối chứng sạch.
- Release checks: ba envelope JSON1.0.0 hợp lệ, link tương đối tồn tại,9/9 ca trọng tâm C1/C3/R1/W3/L6/V1/L7/L8/L9 đạt.
- Không thêm CI step cho gói này; receipt CI của PR và merge nằm trên GitHub, link publication ghi trong Linear. Workflow hiện có được giữ nguyên.

## Provenance của gói portable

check_contract.py giữ nguyên các hàm logic đã review của helper scratch/zer37 (bản2). Chỉ đổi ROOT sang vị trí checkout, đường fixture, schema1.0.0, dòng hướng dẫn và main chạy control/mutant; bỏ package checks vốn pin HEAD/dirty/NOW của máy Hoàng. Fixtures giữ nguyên SHA-256 c9144d7500f11a468f8d9b2f30bb3ee6ab9e1b47364890932ef5a8c78e2382a2. Independent_checks là bản portable của script Codex, chỉ đổi đường import và thay ghi đè report lịch sử bằng assertion để exit khác0 khi có ca trượt. verify_release là wrapper kiểm version/link/JSON và9 ca trọng tâm đã dùng trong audit.

Contract1.0.0 SHA-256: fe09beb590ecc7fd82452e8108215565558e74886765da215954450415fe91fc.

Helper gốc do Claude viết cả logic và expected; Codex đã review và thử phản ví dụ độc lập. ID hash theo tên case chỉ là SYNTHETIC để tái lập, không phải generator runtime. CLOCK_OFFSET_10S của script cũ không dịch trường evidence_complete_at mới, nên evaluator_mismatch=true là đúng; C1 dịch đầy đủ và đòi cả KPI30/60/90 cùng mismatch=false. C3 kiểm trôi tuyến tính trên dữ liệu giả định.

## Giới hạn

Tất cả case là SYNTHETIC/OFFLINE, không phải lab data, telemetry hay kết quả formal. Helper là minh họa thiết kế, không phải validator production hoặc scorer ZER-10 hoàn chỉnh. Chưa chứng minh uptime, CPU, containment SQLi, đa probe cùng luồng, guard ACCEPT trước HEAL_STARTED, truyền ID Kafka/HTTP, lưu raw bền hoặc quyền H/O thực tế. Những OPEN ở mục11 vẫn thuộc issue sở hữu. ZER-37 chỉ phủ AC-01 của ZER-9; cha9 và gate G1 chưa hoàn thành. Không đổi D-01…D-05, KPI, B3/M1/B2 hoặc khóa F-01…09.
