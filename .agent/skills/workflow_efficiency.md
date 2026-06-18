---
name: workflow_efficiency
description: Quy tắc tối ưu hóa tốc độ làm việc, tiết kiệm token và tránh lặp lại lỗi cho dự án Java, Go, và Kubernetes.
---

# Cẩm Nang Rút Kinh Nghiệm & Tối Ưu Hóa Quy Trình (K8s, Java, Go)

Tài liệu này ghi lại các bài học kinh nghiệm và quy tắc làm việc tối ưu nhằm tránh lặp lại lỗi, giảm thời gian xử lý và tiết kiệm token tối đa cho dự án **Zero Door**.

---

## 1. Tối ưu hóa Token qua việc đọc/tìm kiếm thông tin (Context Budget)
*   **Bài học:** Đọc toàn bộ thư mục lớn hoặc gọi quá nhiều tool nhỏ nhặt (như đọc file, grep search liên tục) gây lãng phí ngân sách Token của phiên chat.
*   **Quy tắc:**
    *   Sử dụng `list_dir` có mục tiêu trước khi đi sâu vào đọc code.
    *   Hạn chế chèn toàn bộ nội dung file lớn vào chat nếu chỉ cần chỉnh sửa một đoạn nhỏ. Sử dụng `view_file` với tham số `StartLine` and `EndLine`.
    *   Gộp các chỉnh sửa không liên tiếp trong cùng một file vào một cuộc gọi `multi_replace_file_content` duy nhất thay vì gọi `replace_file_content` nhiều lần liên tục.

## 2. Quy tắc phát triển Kubernetes & Kafka
*   **Tiết kiệm RAM local**: Google Online Boutique có hơn 10 microservices, cộng với Kafka, Prometheus, và 3 Agents. Chạy tất cả có thể làm treo máy máy dev của bạn.
    *   **Giải pháp**: Cấu hình `resources.requests` và `resources.limits` cực nhỏ cho các microservices test (ví dụ: `memory: 128Mi`, `cpu: 100m`).
    *   **Tắt bớt services**: Chỉ chạy các services chính của Boutique app phục vụ cho kịch bản chaos (ví dụ: Frontend, CartService, ProductCatalog) thay vì chạy toàn bộ 10+ services nếu RAM local không đủ.
*   **Kafka Topic Partitioning**: Ở local sandbox, chỉ cần dùng 1 Partition và Replication Factor = 1 cho mỗi topic để giảm tải cho Kafka cluster. Tránh over-engineering thiết lập 3 replicas ở local.
*   **12-Factor App Config**: Tuyệt đối không hardcode bootstrap server của Kafka (`localhost:9092`) trong code Java/Go. Luôn lấy từ env `KAFKA_BOOTSTRAP_SERVERS` để chuyển đổi dễ dàng giữa local K3d (trong cluster service DNS) và EC2.

## 3. Quy tắc làm việc với Spring AI & LLMs
*   **Local LLM Fallback**: Luôn tích hợp Ollama làm option chạy offline/local. Sử dụng các models nhẹ như `llama3:8b` hoặc `phi3` để chạy mượt ở máy local.
*   **Token Logging**: Khi Nemesis gọi LLM để sinh payload tấn công, hãy in log chi tiết số lượng Token tiêu thụ (Prompt/Completion Tokens) để dễ phân tích hiệu năng và chi phí.
*   **Avoid Infinite Loops**: Thiết kế cơ chế ngắt (Circuit Breaker hoặc Counter limit) để ngăn Nemesis và Hephaestus gọi LLM lặp vô hạn khi phân tích lỗi/tấn công liên tục.
