# Issue — DDoS L7 và cạn tài nguyên đúng mục tiêu

[Milestone R2](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-14](https://linear.app/zero-door/issue/ZER-14/ddos-l7-va-can-tai-nguyen-djung-muc-tieu). Nguồn đối chiếu: `R2-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R2-T02-S01 | Cho HTTP flood đi qua route/cổng được giám sát, có RPS và thời lượng giới hạn. | [ZER-43](https://linear.app/zero-door/issue/ZER-43/djua-http-flood-qua-djung-route-djuoc-giam-sat) |
| R2-T02-S02 | Tạo CPU exhaustion trên workload mục tiêu, giới hạn tài nguyên rõ ràng. | [ZER-44](https://linear.app/zero-door/issue/ZER-44/gay-cpu-exhaustion-tren-djung-workload-muc-tieu) |
| R2-T02-S03 | Kiểm tra cleanup, traffic bình thường và memory variant nếu đưa vào protocol. | AC của [ZER-14](https://linear.app/zero-door/issue/ZER-14/ddos-l7-va-can-tai-nguyen-djung-muc-tieu) |
| R2-T02-S04 | Chuẩn bị tải C0/C1 cùng biến thể C2/C4 có triệu chứng chồng lấp. | [ZER-45](https://linear.app/zero-door/issue/ZER-45/dung-case-catalog-co-trieu-chung-chong-lap) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R2-T02-S01

Metric và log trên đúng đường giao dịch; tác động latency/error có thể tái hiện.

### R2-T02-S02

CPU/latency/error của chính dịch vụ bị tác động; KPI CPU target >80% (DOCX P179) có mẫu số, cửa sổ và attribution rõ; không suy từ pod stress riêng.

### R2-T02-S03

Target trở lại baseline; cleanup có return code và kiểm tra tài nguyên còn sót, không giữ SUCCESS khi cleanup lỗi mà giấu lỗi. Memory variant có bằng chứng hoặc quyết định loại khỏi protocol.

### R2-T02-S04

Case catalog, ground truth/action set và seed/tải tái lập; tách biến thể pilot với đánh giá, không giả lập metric.

## Phụ thuộc cần đối chiếu

[R0-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/local-lab.md), [R1-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [R1-T04-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md) (mục nguồn trong ghi chú), [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
