# ZERO DOOR — Delivery

Đầu mối duy nhất cho công việc hiện hành. Tổ chức theo **milestone → issue → sub-issue** của Linear. Linear giữ outcome/AC, trạng thái, phân công, độ ưu tiên, estimate, lịch và quan hệ; repo giữ phạm vi nghiên cứu, thiết kế, mã và bằng chứng kỹ thuật.

**Project đang dùng:** [ZERO DOOR — Nghiên cứu và nghiệm thu](https://linear.app/zero-door/project/zero-door-nghien-cuu-va-nghiem-thu-d14f8467a039), `P-ZER-1`. Đã tạo và read-back 8 milestone, 27 issue chính và 34 sub-issue; ID/URL thật ở mapping. Tra live state trên Linear.

## Bắt đầu ở đâu

1. Mở [NOW — checkpoint phiên](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md).
2. Mở issue trên Linear và ghi chú kỹ thuật tương ứng trong milestone bên dưới. Link issue thật đã gắn vào đầu từng ghi chú.
3. Đọc [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) khi cần đối chiếu cam kết; theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md) để thực hiện, kiểm chứng và bàn giao.

## Milestones

| Milestone | Kết quả cần đạt | Issues nguồn |
| --- | --- | --- |
| [R0 — Nền tảng](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) | Phạm vi/RQ được khóa, lab và một backend LLM hoạt động thật | 4 |
| [R1 — Phép đo](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) | Event, probe, metric, guard và đối chứng kiểm chứng được | 4 |
| [R2 — Kịch bản](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/README.md) | SQLi, DDoS L7, resource exhaustion có tác động và cleanup | 3 |
| [R3 — Phục hồi](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/README.md) | Scale, block IP và rollback có hậu điều kiện thực | 3 |
| [R4 — Tác tử AI](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) | Trace LLM thật, guard/fallback và đối chứng phù hợp claim | 4 |
| [R5 — Tích hợp](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) | Pipeline, pilot, protocol và bàn giao kỹ thuật | 3 |
| [R6 — Bài báo](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R6-paper/README.md) | Dataset chính thức, kết luận có đối chứng và biên nhận nộp | 3 |
| [R7 — Nghiệm thu](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R7-acceptance/README.md) | Chấp nhận đăng, sản phẩm và hồ sơ nghiệm thu | 3 |

R0–R7 là mã milestone kế thừa. Tên file issue theo nội dung, ví dụ `local-lab.md`; mã `R0-T02-S01` chỉ dùng đối chiếu yêu cầu cũ. Dùng mã Linear thật như ZER-34 để giao việc và bàn giao; không đặt thêm hệ mã phase/task mới.

## Cấu trúc và trách nhiệm

```text
delivery/
  README.md           điểm vào và danh mục milestone
  NOW.md              checkpoint / bước tiếp theo
  SCOPE.md            cam kết nghiên cứu và nguồn xác nhận
  WORKFLOW.md         cách làm việc, Ready/Done và QA
  milestones/        mỗi milestone có README và ghi chú issue
  reference/         thiết kế và tiêu chí dùng chung
  linear/            kết nối, kế hoạch import, mẫu issue, mapping ID
```

Một ghi chú issue chứa phạm vi kỹ thuật, đầu ra, yêu cầu kiểm chứng, prerequisite và bàn giao. Chỉ tách sub-issue có đầu ra/nghiệm thu độc lập; phần nhỏ giữ checklist AC trong Linear. Không tạo thêm một file cho mỗi sub-issue để sao chép board. Lịch, status và owner cũ đã ra khỏi các bảng issue đang đọc.

## Tra cứu theo nhu cầu

- [Thiết kế nghiên cứu và đối chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/research-design.md).
- [Phép đo và kiểm chứng](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/verification.md).
- [Thiết kế kịch bản và phục hồi](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/scenario-design.md).
- [Vai trò AI và lựa chọn provider](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/ai-provider.md).
- [Audit và các đính chính](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/audit-findings.md).
- [Kết nối Linear](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/README.md) · [Kế hoạch nhập backlog](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/import.md).

Kế hoạch/lịch/phân công trước đây chỉ nằm trong [lịch sử](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/README.md). Đã bảo toàn 8 gate, 27 issue nguồn và đủ 92 mục yêu cầu. Các mục tiêu 31/10, 14/11, 31/12 và giới hạn nguồn được giữ ở SCOPE/lịch sử; không là due date Linear đã áp.
