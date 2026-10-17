# Vai trò AI và lựa chọn provider

[Tổng quan](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/README.md)

Đây là thiết kế/đề xuất đã chuyển từ roadmap 17/10, chưa phải xác nhận provider đang hoạt động. Thông tin model, quyền và chi phí phải xác minh lại khi chọn backend. Claude Code là công cụ phát triển, không mặc định là backend runtime.

## Quyết định về AI và provider

Một agent cần quan sát, giữ trạng thái mục tiêu, chọn hành động, dùng công cụ và kiểm tra kết quả. Một endpoint gọi LLM rồi trả JSON chưa đủ chứng minh vòng lặp tự trị; giao diện chat diễn giải sự kiện cũng không tự trở thành ba agent AI.

| Tác tử | Hành vi cần hoàn thành | Vai trò LLM | Phần mã kiểm soát |
| --- | --- | --- | --- |
| Nemesis | Chọn kịch bản từ trạng thái lab, thực thi, đọc kết quả và quyết định lượt tiếp theo trong phiên giới hạn | Chọn vector/intensity, sinh biến thể SQLi theo mẫu sandbox và giải thích ngắn bằng dữ kiện | Target allowlist, payload schema, request/duration/concurrency budget, start/stop và worker thực thi |
| Gaia | Thu metrics/log/probe, phát hiện sự cố và phân tích nguyên nhân có bằng chứng | Phân loại sự cố, đối chiếu log/metrics gần nhất, trả anomaly/evidence/confidence có cấu trúc | Threshold/signature/probe phát hiện nhanh, timestamp, IP nguồn, dedup; không chờ LLM mới ghi mốc phát hiện |
| Hephaestus | Chọn hành động theo sự cố và trạng thái deploy, thực thi, kiểm tra hồi phục và ghi kết quả | Xếp hạng/chọn action trong enum được phép, dùng evidence và release history | Policy gate, invariants, cooldown, hạn số lần chữa, thao tác K8s/gateway, xác nhận readiness và giao dịch nghiệp vụ |

Ba tác tử có trạng thái, nhiệm vụ và hợp đồng dữ liệu riêng; có thể dùng chung một model/API. Không cần tải ba model cùng lúc. LLM không được sinh và thực thi lệnh shell tùy ý hoặc tự sửa mã ứng dụng trong luồng chữa lỗi.

Sự cố cần phản ứng nhanh được bộ phát hiện ghi nhận ngay. Inference có timeout và retry giới hạn. Khi LLM không khả dụng, chế độ suy giảm dùng policy đã khai báo; raw event và dataset phải đánh dấu đã fallback. Một lượt không gọi được model không được ghi như lượt AI đầy đủ. Đo riêng latency inference và overhead quyết định để kiểm tra ảnh hưởng lên KPI.

**Provider đề xuất:** API là backend chính cho thực nghiệm, nhằm tránh inference trên cùng máy làm nhiễu tài nguyên của cluster. Chọn model nhỏ có structured output sau khi xác nhận endpoint/quota và một lượt test thật. Không chốt tên model từ manifest cũ, không tự nâng subscription, không tự tạo VM/GPU hoặc dịch vụ mất phí trong lượt lập kế hoạch.

**Ollama bổ sung:** nếu API chưa sẵn sàng, thử duy nhất một ứng viên nhỏ, chẳng hạn [qwen2.5:3b Q4_K_M](https://ollama.com/library/qwen2.5:3b), trước khi triển khai nhiều lựa chọn. Trang model ghi khoảng 1,9 GB weights, không phải tổng RAM/VRAM vận hành. Đặt context nhỏ cho telemetry đã tóm tắt và đo thực tế cùng lab; chỉ dùng nếu latency và memory không làm hỏng phép đo. Ollama hỗ trợ [JSON schema/structured outputs](https://docs.ollama.com/capabilities/structured-outputs); [context dài làm tăng bộ nhớ](https://docs.ollama.com/context-length). Chưa có benchmark để hứa model này đáp ứng KPI hoặc chất lượng phân loại.

Chỉ cần interface thay provider, không bắt buộc vận hành hai backend trong tháng 10. Khi đo chính thức, khóa provider/model/version/prompt; không chuyển provider âm thầm giữa các lượt. Thực nghiệm cloud/local song song và so sánh model là phần hoãn nếu làm trễ nghiệm thu.

Microsoft xác nhận [Azure for Students có credit 100 USD trong 12 tháng nhưng không áp dụng cho Marketplace offers](https://learn.microsoft.com/en-us/azure/education-hub/faq). Quyền model/quota còn phụ thuộc subscription/deployment. Trước khi dùng API Azure, kiểm tra eligibility, billing và giới hạn cụ thể; không mặc định mọi model đều dùng được credit. Đề xuất giới hạn thử nghiệm LLM ban đầu 10 USD từ credit, chỉ khi được xác nhận phương án; code có max calls, token budget, timeout và tracking usage. Budget alert của cloud không thay cho giới hạn request trong ứng dụng; chưa phát sinh chi phí trong kế hoạch này.
