# CHƯƠNG 6: KẾT LẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Các đóng góp chính của đề tài

Sau 6 tháng nghiên cứu và triển khai thực tế, đề tài đã đạt được các kết quả khoa học và thực tiễn quan trọng, đáp ứng đầy đủ các mục tiêu đề ra ban đầu:

1.  **Xây dựng thành công vòng lặp tự trị đóng kín (Closed-Loop Self-Healing):** Hiện thực hóa mô hình MAPE-K tích hợp giữa Chaos Engineering chủ động (Red Team - Nemesis và Chaos Worker) và phòng thủ tự khắc phục sự cố (Blue Team - Gaia và Hephaestus). Cơ chế truyền tin phi đồng bộ hướng sự kiện qua Kafka KRaft hoạt động ổn định, đảm bảo tính cô lập và khả năng mở rộng.
2.  **Đo lường thực nghiệm đạt chuẩn KPI:** Thực nghiệm kiểm chứng với 40 lượt chạy chứng minh thời gian phát hiện dị thường (MTTD) chỉ mất trung bình dưới **25.6 giây** và thời gian vá lỗi (MTTR) qua API chỉ tốn **1.01 giây**. Hệ thống mục tiêu duy trì tỷ lệ **Uptime 100%** dưới áp lực tấn công dồn dập.
3.  **Tối ưu hóa tài nguyên xuất sắc (FinOps):** Chuyển đổi thành công kiến trúc từ Java Spring Boot sang Python FastAPI và Go. Cải tiến này giúp giảm lượng RAM tiêu hao của các tác tử điều phối từ **1300MB xuống còn 157MB** (tiết kiệm gần 88%), giúp đề tài có khả năng vận hành mượt mà trên cả máy tính cá nhân 16GB RAM lẫn trên hạ tầng điện toán đám mây đám mây giá rẻ.
4.  **Tự động hóa hạ tầng đám mây an toàn:** Áp dụng thành công Terraform để tự động hóa 100% quy trình tạo lập VM và Firewall trên Cloud. Triển khai quy trình bảo mật Container Hardening (Google Distroless nonroot) giúp triệt tiêu hoàn toàn bề mặt tấn công shell injection và các lỗ hổng bảo mật CVE.

---

## 6.2. Hạn chế của hệ thống hiện tại

Mặc dù đạt được những kết quả khả quan, nhóm nghiên cứu cũng thẳng thắn nhìn nhận một số hạn chế kỹ thuật cốt lõi cần khắc phục:

*   **Độ trễ khởi động của Container (Warmup Latency):** Dù Hephaestus thực hiện lệnh gọi API vá lỗi chỉ trong 1.01 giây, hệ thống vẫn phải chịu một độ trễ vật lý tự nhiên từ 20-40 giây để Kubernetes tải image (nếu chưa có sẵn trên node), khởi tạo container và chạy các chương trình khởi động trước khi pod đạt trạng thái `Ready` để nhận tải.
*   **Hiện tượng Tranh chấp cứu hộ (Race Condition):** Trong kịch bản xóa pod đột ngột (Pod Kill), sự can thiệp chồng chéo của Hephaestus lên cơ chế tự phục hồi mặc định của Kubernetes (ReplicaSet Controller) dẫn đến tỷ lệ lỗi API call cao (lên đến 80%), gây hao phí tài nguyên xử lý vô ích.
*   **Độ tin cậy của Mô hình ngôn ngữ lớn (LLM Reliability):** Tác tử Nemesis phụ thuộc vào cấu trúc đầu ra JSON của LLM. Mặc dù đã áp dụng prompt design chặt chẽ, đôi khi LLM vẫn gặp hiện tượng ảo tưởng (hallucination) sinh ra các cấu trúc JSON lỗi hoặc các kiểu tấn công không nằm trong registry hỗ trợ của Chaos Worker.
*   **Tính tĩnh của Ma trận Quyết định (Decision Matrix):** Hephaestus hiện tại đang đưa ra hành động dựa trên ma trận quyết định được định nghĩa tĩnh từ trước. Điều này khiến hệ thống thiếu linh hoạt khi gặp phải các dạng dị thường phức tạp chưa có trong kịch bản mẫu.

---

## 6.3. Hướng nghiên cứu phát triển tương lai

Để giải quyết các hạn chế nêu trên và nâng cấp độ phức tạp của hệ thống, nhóm đề xuất các hướng phát triển tiếp theo của đề tài:

1.  **Ứng dụng học máy tăng cường (Reinforcement Learning) cho Decision Engine:** Thay thế ma trận quyết định tĩnh của Hephaestus bằng một mô hình học máy tự động ra quyết định dựa trên phần thưởng (Reward-based). Agent sẽ tự học hỏi từ lịch sử thực nghiệm để đưa ra hành động cứu hộ tối ưu nhất cho từng trạng thái cụ thể của hệ thống.
2.  **Tích hợp Công nghệ giám sát tầng sâu (eBPF Telemetry):** Thay thế hoặc bổ sung cho Prometheus/cAdvisor bằng eBPF (Extended Berkeley Packet Filter). eBPF cho phép thu thập số liệu mạng và hệ thống trực tiếp từ nhân Linux kernel mà không tốn tài nguyên overhead, giúp Gaia phát hiện tấn công ở cấp độ cuộc gọi hệ thống (system calls) với độ chính xác cao hơn.
3.  **Hỗ trợ kiến trúc Service Mesh (Linkerd / Istio):** Sử dụng Service Mesh để thu thập chi tiết sơ đồ kết nối (network topology) và thực hiện các hành động bảo mật ở tầng mạng phức tạp hơn như tự động cô lập microservices bị nhiễm độc (circuit breaking, traffic shifting) thay vì chỉ dùng NetworkPolicy cơ bản.
4.  **Thử nghiệm trên hạ tầng Multi-Cloud phân tán:** Đánh giá hiệu năng và tính ổn định của hệ thống đa tác tử khi triển khai phân tán trên nhiều nhà cung cấp dịch vụ đám mây khác nhau (AWS, Google Cloud, Azure), hướng tới chuẩn hóa sản phẩm sẵn sàng cho môi trường doanh nghiệp quy mô lớn.
