# Issue — Thực nghiệm chính thức và khóa dữ liệu

[Milestone R6](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R6-paper/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-27](https://linear.app/zero-door/issue/ZER-27/thuc-nghiem-chinh-thuc-va-khoa-du-lieu). Nguồn đối chiếu: `R6-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R6-T02-S01 | Kiểm tra gate, protocol, nhãn không lộ đáp án và các lỗi/KPI chưa đạt trước formal run. | AC của [ZER-27](https://linear.app/zero-door/issue/ZER-27/thuc-nghiem-chinh-thuc-va-khoa-du-lieu) |
| R6-T02-S02 | Chạy đủ số lặp B0/B1/B2/BM và B3 nếu giữ claim RQ2, kể cả manual có thao tác thật. | [ZER-58](https://linear.app/zero-door/issue/ZER-58/chay-cac-nhom-thuc-nghiem-theo-protocol-dja-khoa) |
| R6-T02-S03 | Phân tích tỷ lệ phục hồi, action đúng/sai/thừa, KPI, độ bất định và overhead/cost theo RQ. | [ZER-59](https://linear.app/zero-door/issue/ZER-59/phan-tich-kpi-chat-luong-quyet-djinh-va-chi-phi) |
| R6-T02-S04 | Khóa dataset và đối chiếu từng claim với RQ, nhóm đo và phạm vi kết luận. | AC của [ZER-27](https://linear.app/zero-door/issue/ZER-27/thuc-nghiem-chinh-thuc-va-khoa-du-lieu) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R6-T02-S01

G5 PASS, protocol khóa theo R5-T02-S02 (mục tiêu điều chỉnh 30/10) và checklist đo hợp lệ; thiếu core/phép đo/đối chứng cần thiết thì BLOCKED, sửa và cập nhật lịch.

### R6-T02-S02

Raw run/failure, seed/fault/tải tương ứng và thứ tự xen kẽ; reset có xác nhận, cùng version/evidence/budget, không chỉnh rules/prompt theo case formal.

### R6-T02-S03

Bảng/plot cùng mẫu số; báo AI thực/fallback, failure/timeout, độ đúng trước guard; B2/B3 chỉ kết luận nếu đã đo, không chọn riêng case AI thắng.

### R6-T02-S04

Hash/version và ma trận claim → RQ/cấu hình/metric/trace; bỏ claim ưu thế phối hợp nếu thiếu B3, phân tích trung thực khi AI không tốt hơn rules.

## Phụ thuộc cần đối chiếu

[R5-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/technical-handoff.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## ZER-27 checkpoint — 12/11/2026

Preserved opt-in formal decision capture, durable B2 budget/call evidence, formal scorer and containment-join code with regression tests. The [checkpoint report](../../../evidence/ZER-27/README.md) records the successful benign 330-second window and native O integration with a synthetic provider, including limits and failed attempts. Raw evidence stays owner-held.

Hoàng selected solo BM operation with hidden schedule/onset, deterministic scoring and post-cohort technical review. The [addendum](../../../evidence/ZER-53/solo-operation-addendum.md) remains review-required before formal; the locked base protocol is unchanged. AC-01 remains incomplete and FORMAL_HOLD: real B2/C5 readiness, five detector variants, actual BM interaction, live audit/M12 capture, common-profile review and account budget still need verification. Merging this checkpoint is not formal admission or issue acceptance.

## ZER-27 AC-01 — 15/11/2026, actual readiness checks complete

Live ZER-27 AC read again15/11, zero-door workspace. BaseHEAD5ab2391fceccc647094b6c43509174e14aa116a6, initially clean, same tree as main6698e29d. One writer Codex. Exact production scope:measurement/{formal_containment.py,formal.py,metrics.py,scorer.py,containment_join.py}; tests/{test_formal_containment.py,test_measurement_formal.py,test_formal_readiness.py}; report/handoff/checkpoint. No protocol/prompt/seed/detector edits. Private runtime fixes/raw retained in snapshot.

[AC-01 report](../../../evidence/ZER-27/README.md) supersedes old remaining list:five native triggers; actual two-call B2/positive H containment/complete usage; actual owner BM/action/M10;66/66 samples/330s; exact profile restoration/owned cleanup. BM Boutique NOT_VERIFIED and old paidB2 usageUNKNOWN retained. Final B2 baseline43ms/post200ms; estimate0.0002044USD/no retry/no further funded calls.

Actual H/O arithmetic calibration passes; real formal audit remains UNVERIFIED and readiness0formal. Native H lacks complete formal RUN/TRIAL/HARNESS metadata; do not backfill it. Solo method/profile/source pins in report; no independent-human or Claude-review claim. Separate laptop local-evidence/ZER-27/ac01-20261115/ retains source/all attempts/checksums/replay. Separate-copy replay passed B2/five variants and retained BM PARTIAL. Tests20runner/18console/8profile plus154measurement/11M12/28readiness/5config passed. Docker stopped.

Next: exact code/report delta review/CI/merge under full-project authority, then AC01-only checklist readback. Parent remains open for AC02-04. AC02/ZER58 not started; before its first request seal schedule/config and record full metadata/prompts/eight audit surfaces from start, with current budget/attendance/resource gates. Fail closed if capture absent; no new research scope/framework.
