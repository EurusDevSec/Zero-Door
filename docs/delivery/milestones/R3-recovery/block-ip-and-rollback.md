# Issue — Block IP thực thi được và rollback đúng phiên bản

[Milestone R3](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-17](https://linear.app/zero-door/issue/ZER-17/block-ip-thuc-thi-djuoc-va-rollback-djung-phien-ban). Nguồn đối chiếu: `R3-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R3-T02-S01 | Chốt enforcement point và nguồn IP; xử lý NAT/header tin cậy. | [ZER-46](https://linear.app/zero-door/issue/ZER-46/kiem-chung-block-ip-ttl-va-benign-traffic) |
| R3-T02-S02 | Chặn attacker, giữ traffic benign, có TTL và gỡ chặn. | [ZER-46](https://linear.app/zero-door/issue/ZER-46/kiem-chung-block-ip-ttl-va-benign-traffic) |
| R3-T02-S03 | Tạo phiên bản lỗi/known-good và case C3 có kiểm soát, tách nhãn đáp án khỏi telemetry. | [ZER-47](https://linear.app/zero-door/issue/ZER-47/rollback-ve-known-good-release-va-kiem-chung-nghiep-vu) |
| R3-T02-S04 | Khôi phục image/config/revision thật và xác minh rollout lẫn probe. | [ZER-47](https://linear.app/zero-door/issue/ZER-47/rollback-ve-known-good-release-va-kiem-chung-nghiep-vu) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R3-T02-S01

Sơ đồ request, selector/nhãn pod và thử xác nhận IP; không dùng IP mặc định 0.0.0.0. Đối chiếu controller K3s/args thực tế; không suy Flannel bỏ policy hoặc thay CNI khi chưa có bằng chứng.

### R3-T02-S02

Request bị chặn/được phép đúng đối tượng; hiệu lực và hết hạn được kiểm tra sau restart. Không dựa duy nhất vào threading.Timer; tách endpoint reset (không xóa policy), runner reset (có lệnh xóa theo nhãn) và TTL; hậu điều kiện cleanup phải đo được.

### R3-T02-S03

Image/config/revision, triệu chứng và ground truth có danh tính rõ; bên chữa lỗi nhận lịch deploy/log thật, không nhận đáp án rollback.

### R3-T02-S04

Danh tính trước/sau và dịch vụ hồi phục; thay annotation riêng lẻ không đủ.

## Phụ thuộc cần đối chiếu

[R1-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/probes-and-metrics.md), [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
