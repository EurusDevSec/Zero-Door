# Milestone R2 — Ba kịch bản Chaos

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

## Điều kiện nghiệm thu tích hợp

**Gate G2:** SQLi, DDoS L7 và resource exhaustion gây được tác động đúng mục tiêu, có dấu vết và cleanup; chạy phối hợp vẫn giữ giới hạn.

Milestone **R2** đã được tạo trong [project P-ZER-1](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039); ID thật lưu trong mapping. Lịch và kết luận nghiệm thu delivery đọc Linear.

## Issues

- [Fixture và executor SQL injection](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md) — [ZER-13](https://linear.app/zero-door/issue/ZER-13/fixture-va-executor-sql-injection) (nguồn `R2-T01`).
- [DDoS L7 và cạn tài nguyên đúng mục tiêu](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/ddos-and-resource-exhaustion.md) — [ZER-14](https://linear.app/zero-door/issue/ZER-14/ddos-l7-va-can-tai-nguyen-djung-muc-tieu) (nguồn `R2-T02`).
- [Chạy phối hợp và dừng có kiểm soát](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/combined-run-and-cleanup.md) — [ZER-15](https://linear.app/zero-door/issue/ZER-15/chay-phoi-hop-va-dung-co-kiem-soat) (nguồn `R2-T03`).

Đối chiếu evidence của các issue với gate, ghi kết quả kiểm chứng có revision và giới hạn rồi liên kết từ Linear. Tất cả issue Done không tự chứng minh milestone đạt; gate đạt không thay bằng chứng KPI hoặc chấp nhận bài báo.
