# Issue — Khôi phục môi trường local

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local). Nguồn đối chiếu: `R0-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước S01 chỉ đọc môi trường; file đầu ra: `docs/evidence/R0-T02-S01/inventory.md`. Không start/recreate/delete hoặc đọc secret trong bước này. S02/S03 chỉ mở sau inventory và phạm vi thao tác được chốt; không chạy mù start-demo/recreate.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T02-S01 | Kiểm tra context, container, volume, cổng và tài nguyên Docker/Kubernetes bằng truy vấn mới. | [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc) |
| R0-T02-S02 | Chọn start hay recreate theo inventory và khôi phục một đường triển khai có thể lặp lại. | [ZER-35](https://linear.app/zero-door/issue/ZER-35/khoi-phuc-lab-tu-inventory-dja-kiem-chung) |
| R0-T02-S03 | Kiểm tra Kafka, Prometheus, Elasticsearch/log và luồng mua hàng Online Boutique. | AC của [ZER-6](https://linear.app/zero-door/issue/ZER-6/khoi-phuc-moi-truong-local) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T02-S01

Inventory có timestamp/kết quả hoặc lỗi rõ, context/Git/containers/volumes/ports/resources và phiên bản/args K3s khi truy cập; xác định nguyên nhân API không truy cập được. Truy vấn lỗi/bị ngắt không được coi là inventory rỗng hoặc container exited.

### R0-T02-S02

Kubernetes API truy cập; dữ liệu cần giữ được bảo toàn; lệnh dựng và profile tài nguyên được ghi. Kiểm tra script đúng chức năng; start-demo.ps1 hiện dừng mọi kubectl và dùng context hiện hành nên không chạy mù; rebuild-nemesis.ps1 build/import/rollout, không tạo cluster. Giữ volume/dữ liệu và ghi phạm vi thao tác.

### R0-T02-S03

Log/message truy vết, truy vấn metric và giao dịch mẫu; trạng thái Running riêng lẻ chưa đủ.

## Phụ thuộc cần đối chiếu

Không có.

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

Inventory đã có sáu AC đầy đủ tại [ZER-34](https://linear.app/zero-door/issue/ZER-34/kiem-ke-lab-local-bang-truy-van-chi-djoc); không tiếp tục duy trì checklist sống thứ hai ở ghi chú này. Đầu ra dự kiến vẫn là `docs/evidence/R0-T02-S01/inventory.md`.
