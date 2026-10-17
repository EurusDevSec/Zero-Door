# Issue — Khóa phạm vi và tiêu chí đánh giá

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia). Nguồn đối chiếu: `R0-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước S03 đã có đầu ra dự kiến duy nhất: `docs/evidence/R0-T01-S03/baseline-source-ledger.md`. Không sửa dữ liệu gốc. S02 là việc lập ma trận/định nghĩa, chưa chốt đường dẫn đầu ra. Không dùng phạm vi S03 để sửa toàn issue.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T01-S01 | Ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI và bài được chấp nhận đăng. | AC của [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia) |
| R0-T01-S02 | Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số. | [ZER-32](https://linear.app/zero-door/issue/ZER-32/lap-ma-tran-yeu-cau-va-djinh-nghia-kpi) |
| R0-T01-S03 | Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08. | [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T01-S01

Các xác nhận của người dùng đã được ghi trong file SCOPE.md của delivery.

### R0-T01-S02

Ma trận truy vết; cách đánh giá MTTR 120/180 giây theo thuyết minh, MTTD <60 giây và uptime ≥99,9%, không hạ ngưỡng.

### R0-T01-S03

HEAD/dirty files, hash và số dòng từng CSV, timestamp lưu trong dữ liệu tách khỏi timeline Git; nguồn DOCX/xác nhận mới/IDE/chat được phân loại, path được kiểm tra. Giữ nguyên raw/handoff; thiếu lịch sử hoặc danh tính thì UNKNOWN.

## Phụ thuộc cần đối chiếu

Không có.

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
