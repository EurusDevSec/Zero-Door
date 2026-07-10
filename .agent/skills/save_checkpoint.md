---
name: save_checkpoint
description: Compress current session memory, optimize token footprint, and output a high-fidelity context handover state for a fresh chat session.
---

# 💾 Skill: Context Checkpointing & Memory Compaction

Khi cuộc trò chuyện kéo dài, bộ nhớ ngữ cảnh (Context Window) sẽ bị phình to dẫn đến **tăng độ trễ, lãng phí token và gây ảo giác (hallucination)** cho Agent. Skill này giúp đóng gói toàn bộ "tinh túy" (Core Context) của phiên hiện tại vào file lưu trữ để phiên sau có thể tiếp nhận ngay lập tức với chi phí token tối thiểu.

---

## 🛠️ Quy trình thực hiện (Step-by-Step)

Mỗi khi người dùng yêu cầu lưu checkpoint (`/checkpoint`), bạn phải thực hiện các bước sau:

### Bước 1: Tổng hợp & Nén ngữ cảnh vào `session_memory.md`
Cập nhật file [session_memory.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/workflows/session_memory.md) theo mẫu nén tối ưu:
- Tóm tắt ngắn gọn trạng thái hiện tại, branch và các tasks hoàn thành.
- Đường dẫn cụ thể đến các file mới/file sửa đổi để agent sau đọc trực tiếp.

### Bước 2: Đồng bộ hóa Lộ trình & Bài học kinh nghiệm (PLAN.md & LESSONS_LEARNED.md)
1. Cập nhật các ô tích chọn (`[x]`) cho các tác vụ đã hoàn thành và thêm các cập nhật kỹ thuật vào [PLAN.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/PLAN.md) và [docs/plan.md](file:///r:/_Projects/Eurus_Workspace/zero_door/docs/plan.md).
2. Nếu phát hiện lỗi hoặc kinh nghiệm kỹ thuật mới (như rate limits, resource constraints, port issues), cập nhật ngay vào [LESSONS_LEARNED.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/LESSONS_LEARNED.md).
3. Nếu có thay đổi về hạ tầng hay thiết kế, cập nhật trực tiếp vào [CONTEXT.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/CONTEXT.md).

### Bước 3: Dọn dẹp & Xác thực
1. Kiểm tra code đảm bảo biên dịch và chạy thành công (Go build, Docker images, K8s pods).
2. Commit toàn bộ thay đổi còn lại vào Git.

### Bước 4: Tạo "Handover Prompt" cho người dùng
Xuất ra màn hình một đoạn Prompt ngắn gọn để người dùng sao chép (copy) và dán (paste) khi mở phiên chat mới. Định dạng mẫu:

> **📋 [Handover Prompt cho Session mới]**
> *"Tôi muốn bắt đầu một session mới. Vui lòng đọc file [session_memory.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/workflows/session_memory.md), [PLAN.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/PLAN.md), [LESSONS_LEARNED.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/LESSONS_LEARNED.md) và [CONTEXT.md](file:///r:/_Projects/Eurus_Workspace/zero_door/.agent/rules/CONTEXT.md) để nắm toàn bộ kiến thức và tiếp tục triển khai các bước tiếp theo trong mục Next Steps."*
