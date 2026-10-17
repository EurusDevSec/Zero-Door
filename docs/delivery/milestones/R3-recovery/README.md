# Milestone R3 — Phục hồi và block IP

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

## Điều kiện nghiệm thu tích hợp

**Gate G3:** Scale up/down, block IP và rollback có tác động thật; phân biệt API chấp nhận với hồi phục; có kiểm tra restart, HPA và trạng thái thất bại.

Milestone **R3** đã được tạo trong [project P-ZER-1](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039); ID thật lưu trong mapping. Lịch và kết luận nghiệm thu delivery đọc Linear.

## Issues

- [Trạng thái hồi phục và scale](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/recovery-state-and-scaling.md) — [ZER-16](https://linear.app/zero-door/issue/ZER-16/trang-thai-hoi-phuc-va-scale) (nguồn `R3-T01`).
- [Block IP thực thi được và rollback đúng phiên bản](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/block-ip-and-rollback.md) — [ZER-17](https://linear.app/zero-door/issue/ZER-17/block-ip-thuc-thi-djuoc-va-rollback-djung-phien-ban) (nguồn `R3-T02`).
- [Consumer, retry và tương tác controller](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md) — [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) (nguồn `R3-T03`).

Đối chiếu evidence của các issue với gate, ghi kết quả kiểm chứng có revision và giới hạn rồi liên kết từ Linear. Tất cả issue Done không tự chứng minh milestone đạt; gate đạt không thay bằng chứng KPI hoặc chấp nhận bài báo.
