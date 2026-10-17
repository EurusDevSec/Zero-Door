# Issue — Fixture và executor SQL injection

[Milestone R2](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection). Nguồn đối chiếu: `R2-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R2-T01-S01 | Chốt fixture nghiệp vụ giả lập, dữ liệu giả, route vulnerable/safe và nguồn IP. | AC của [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection) |
| R2-T01-S02 | Triển khai fixture/database nhẹ và đường ingress quan sát được. | [ZER-41](https://linear.app/zero-door/issue/ZER-41/dung-sqli-fixture-va-route-quan-sat-trong-lab) |
| R2-T01-S03 | Bổ sung executor SQLi bằng template và giới hạn đã chốt. | [ZER-42](https://linear.app/zero-door/issue/ZER-42/bo-sung-executor-sqli-co-gioi-han) |
| R2-T01-S04 | Chứng minh tác động SQLi, log và phân biệt lưu lượng tấn công với benign. | AC của [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R2-T01-S01

Thiết kế fixture, tiêu chí tác động SQLi và cách liên hệ với luồng microservices.

### R2-T01-S02

Fixture hoạt động, route/query/log được kiểm chứng; phiên bản đóng gói.

### R2-T01-S03

Payload hợp lệ chạy được; tham số ngoài phạm vi bị từ chối.

### R2-T01-S04

Kết quả trước/sau, truy vết request, IP đáng tin cậy và traffic đối chứng.

## Phụ thuộc cần đối chiếu

[R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md), [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [R1-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md) (mục nguồn trong ghi chú).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
