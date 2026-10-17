# Lịch sử kế hoạch — chỉ tra cứu

Kế hoạch làm việc hiện hành chỉ có tại [docs/delivery](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md). Không cập nhật status, lịch, phân công hoặc tiến độ vào khu lịch sử này.

## Nguồn được bảo toàn

| Tài liệu | Nội dung |
| --- | --- |
| [research-plan.md](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/research-plan.md) | Bản nghiên cứu nội bộ trước đây `docs/plan_original_v3.md`; không thay thuyết minh đăng ký |
| [devops-plan.md](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/devops-plan.md) | Bản DevOps trước đây `docs/plan.md` |
| [phases — lịch sử](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/phases/README.md) | Specs phase triển khai tháng 7; không phải milestone delivery hiện tại |
| [roadmap.md](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/roadmap.md) | Roadmap đầy đủ đã cập nhật 17/10 trước khi tách; giữ nguyên byte |
| [workflow.md](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/workflow.md) | Quy trình trước chuyển Linear; giữ nguyên byte |
| [before-unification.md](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/before-unification.md) | Snapshot các file recovery/plans trước dọn: lịch, owner, phase/task/subtask, W0–W6, checkpoints và discovery cũ |
| [organization.json](R:/_Projects/Eurus_Workspace/zero_door/docs/archive/planning/organization.json) | Bảng đường dẫn cũ → mới, hash nguồn và phạm vi lần tổ chức lại |

Handoff/review và các tài liệu lịch sử giữ nguyên cách ghi đường dẫn tại thời điểm lập để bảo toàn provenance/hash. Khi gặp `docs/recovery`, `docs/plans`, `docs/phases` hoặc tên plan cũ trong đó, tra `pathMap` trong organization.json. Không còn giữ thư mục redirect song song; liên kết chat bên ngoài theo đường dẫn cũ không tự chuyển hướng.

## Lần tổ chức lại — 17/10/2026

Base Git `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`; checkout đã có nhiều tài liệu dirty/untracked trước khi làm. Phạm vi: tài liệu delivery, nguồn kế hoạch được lưu trữ, mapping local và liên kết ở các entrypoint liên quan. Không ghi Linear/Slack, sửa mã ứng dụng, chạy lab/LLM, commit/push hay deploy.

Đã chuyển cách đọc hiện hành sang 8 milestone, 27 ghi chú issue và đủ 92 mục yêu cầu nguồn. Lịch/assignment/status snapshot chỉ giữ để đối chiếu; không nhập metadata hoặc tự tạo mã Linear. Các nội dung lịch sử không phải runtime proof.
