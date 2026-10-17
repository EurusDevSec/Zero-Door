# Issue — Sửa dashboard và các chế độ đối chứng

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung). Nguồn đối chiếu: `R1-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T03-S01 | Bỏ số ngẫu nhiên và nội dung mô phỏng khỏi phần được trình bày là kết quả thực. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S02 | Cho dashboard và bộ xuất dữ liệu dùng chung phép đo. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S03 | Tách MANUAL, RULES và AI; MANUAL không tự kích hoạt healer. | AC của [ZER-11](https://linear.app/zero-door/issue/ZER-11/sua-dashboard-va-cac-che-djo-djoi-chung) |
| R1-T03-S04 | Dựng profile B0 chỉ để controller Kubernetes/HPA tự phục hồi. | [ZER-39](https://linear.app/zero-door/issue/ZER-39/dung-djoi-chung-b0-kubernetescontroller) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T03-S01

Dashboard hiển thị trạng thái không có dữ liệu và nguồn của số liệu.

### R1-T03-S02

Cùng run_id cho ra cùng KPI; phản ánh lỗi và độ trễ cập nhật.

### R1-T03-S03

Log ba chế độ và phép thử chứng minh đối chứng manual không bị auto-heal.

### R1-T03-S04

Cấu hình HPA/guard/probe được ghi rõ; chứng minh ZERO DOOR không phát lệnh heal trong B0, vẫn có đo độc lập.

## Phụ thuộc cần đối chiếu

[R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/probes-and-metrics.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
