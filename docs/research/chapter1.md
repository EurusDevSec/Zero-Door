# CHƯƠNG 1: MỞ ĐẦU

## 1.1. Tính cấp thiết của đề tài

Trong kỷ nguyên chuyển đổi số, kiến trúc dịch vụ siêu nhỏ (Microservices) đã trở thành mô hình phát triển phần mềm phổ biến cho các hệ thống phân tán lớn nhờ khả năng mở rộng độc lập, tính linh hoạt và chu kỳ phát triển nhanh. Tuy nhiên, tính phân tán cao của mô hình này cũng tạo ra sự gia tăng đáng kể về bề mặt tấn công (attack surface) và số lượng điểm lỗi tiềm ẩn (points of failure). Các dịch vụ giao tiếp qua mạng liên tục làm phát sinh các nguy cơ nghẽn mạng, lỗi dịch vụ và rò rỉ an ninh thông tin ở tầng ứng dụng (Application Layer).

Các phương pháp bảo mật và vận hành hệ thống truyền thống hiện nay chủ yếu dựa trên cơ chế phản ứng sự cố thủ công. Khi có sự cố xảy ra, quy trình xử lý thông thường yêu cầu kỹ sư vận hành (On-call SRE/DevOps) phải nhận cảnh báo, phân tích nhật ký hoạt động (logs), tìm kiếm nguyên nhân gốc, kiểm thử bản vá và tiến hành triển khai thủ công. Quy trình này tồn tại một số hạn chế cốt lõi:
*   **Độ trễ phản hồi (Response Latency):** Thời gian trung bình để phát hiện lỗi (Mean Time To Detect - MTTD) và thời gian trung bình để khắc phục lỗi (Mean Time To Recover - MTTR) phụ thuộc lớn vào sự sẵn sàng của con người. Điều này dẫn đến nguy cơ gián đoạn dịch vụ kéo dài, ảnh hưởng trực tiếp tới hoạt động kinh doanh của tổ chức.
*   **Sai sót do yếu tố con người (Human Error):** Dưới áp lực khắc phục sự cố khẩn cấp, các thao tác cấu hình thủ công hoặc can thiệp trực tiếp vào môi trường vận hành (Production) rất dễ dẫn đến các lỗi phụ (side-effects) nghiêm trọng hơn.
*   **Tính thụ động (Reactive Nature):** Hệ thống chỉ được bảo vệ sau khi lỗ hổng đã bị khai thác hoặc sự cố vật lý đã xảy ra, thay vì chủ động phát hiện và ngăn chặn điểm yếu từ sớm.

Nhằm giảm thiểu thời gian gián đoạn dịch vụ và tăng cường độ tin cậy của hệ thống phân tán, xu hướng nghiên cứu bảo mật hiện đại đang dịch chuyển mạnh mẽ từ mô hình phòng thủ thụ động sang cơ chế tự phục hồi tự trị (Autonomous Self-Healing). Sự phát triển của các hệ thống đa tác tử thông minh (Multi-Agent AI Systems) kết hợp với các mô hình ngôn ngữ lớn (LLM) và kỹ thuật hỗn mang (Chaos Engineering) mở ra cơ hội xây dựng một cơ chế phòng thủ khép kín. Trong đó, hệ thống có khả năng tự phát sinh lỗi, tự kiểm thử, tự nhận diện dị thường và tự thực thi các kịch bản khắc phục sự cố ở mức độ thời gian thực (real-time).

Xuất phát từ các vấn đề thực tiễn trên, nhóm nghiên cứu thực hiện đề tài **"Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Tự phục hồi cho hệ thống Microservices"** làm nền tảng cho việc nghiên cứu và xây dựng giải pháp phòng thủ chủ động khép kín. Giải pháp hướng tới việc tự động hóa hoàn toàn quy trình xử lý sự cố tầng ứng dụng, giảm thiểu sự can thiệp của con người và triệt tiêu các rủi ro downtime trong vận hành hệ thống microservices.

---

## 1.2. Mục tiêu nghiên cứu

### 1.2.1. Mục tiêu tổng quát
Mục tiêu tổng quát của đề tài là nghiên cứu và xây dựng thành công một hệ thống DevSecOps tự trị khép kín trên nền tảng điều phối container Kubernetes. Hệ thống tích hợp ba tác tử AI độc lập cùng một bộ tiêm lỗi hỗn mang để tự động hóa toàn bộ vòng đời ứng cứu sự cố bao gồm các pha: Tấn công giả lập (Attack) $\rightarrow$ Giám sát phát hiện (Detect) $\rightarrow$ Quyết định và Thực thi vá lỗi (Heal) mà không cần sự can thiệp của con người.

### 1.2.2. Mục tiêu cụ thể (KPIs kỹ thuật)
Để đánh giá tính hiệu quả thực tế của giải pháp, đề tài đặt ra các mục tiêu kỹ thuật cụ thể cần chứng minh thông qua thực nghiệm:
1.  **Thiết kế và Triển khai hạ tầng:** Xây dựng cụm Kubernetes (K3s/K3d) chạy ổn định ứng dụng kiểm thử microservices đa ngôn ngữ chuẩn công nghiệp gồm ít nhất 5 dịch vụ thành phần, áp dụng cơ chế cô lập mạng và hạn mức tài nguyên nghiêm ngặt.
2.  **Khả năng Tấn công giả lập (Nemesis & Chaos Worker):** Hiện thực hóa khả năng tiêm lỗi chủ động hướng ứng dụng gồm ít nhất 3 dạng lỗi phổ biến: Lỗi cạn kiệt tài nguyên (CPU/Memory Stress), Lỗi gián đoạn dịch vụ (Pod Kill), và Lỗi quá tải tầng ứng dụng (HTTP Flood).
3.  **Khả năng Vá lỗi tự động (Hephaestus):** Tự động đưa ra quyết định cứu hộ tương ứng từ Ma trận Quyết định (Decision Matrix) để thực thi 4 hành động vá lỗi qua API K8s: Scale Up, Restart Pod, Rollback phiên bản lỗi, và chặn IP tấn công bằng NetworkPolicy động.
4.  **Chỉ số Thời gian Phản ứng:**
    *   Thời gian phát hiện sự cố trung bình (MTTD) dưới 1 phút.
    *   Thời gian tự phục hồi trung bình (MTTR) dưới 3 phút (tính từ thời điểm nhận diện sự cố đến khi dịch vụ trở lại trạng thái bình thường).
5.  **Chỉ số Độ sẵn sàng và Uptime:** Đảm bảo hệ thống mục tiêu duy trì tỷ lệ hoạt động ổn định (Uptime) $\ge$ 99.9% dưới áp lực tấn công liên tục từ tác tử giả lập.

---

## 1.3. Đối tượng và phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu
*   Kiến trúc Microservices trên nền tảng container và cơ chế điều phối tài nguyên của Kubernetes.
*   Cơ chế giao tiếp hướng sự kiện (Event-Driven Architecture) trong hệ thống phân tán sử dụng Apache Kafka.
*   Cơ chế phát hiện dị thường (Anomaly Detection) dựa trên thu thập số liệu metrics (Prometheus) và phân tích nhật ký log tập trung (Elasticsearch).
*   Mô hình ra quyết định tự phục hồi (Self-Healing logic) và kỹ thuật Chaos Engineering tiêm lỗi mức ứng dụng.
*   Ứng dụng mô hình ngôn ngữ lớn (LLM - Gemini, OpenAI) trong việc phân tích trạng thái và sinh kịch bản tấn công.

### 1.3.2. Phạm vi nghiên cứu
*   **Môi trường thử nghiệm:** Đề tài tập trung triển khai trên cụm Kubernetes cục bộ (K3d Cluster) giả lập tài nguyên giới hạn (16GB RAM) để tối ưu chi phí phát triển ban đầu, sau đó chuyển đổi và đánh giá hiệu năng trên hạ tầng đám mây công cộng (DigitalOcean Droplet).
*   **Ứng dụng mục tiêu:** Sử dụng hệ thống Google Online Boutique microservices làm môi trường chịu tác động tấn công, tập trung kiểm thử trên các dịch vụ cốt lõi như `frontend` và `cartservice`.
*   **Giới hạn an ninh:** Các kịch bản tấn công chỉ giới hạn trong môi trường kiểm thử nội bộ biệt lập. Chaos Worker được cấu hình các bộ lọc an toàn để đảm bảo không gây ảnh hưởng đến các thành phần hạ tầng cốt lõi như Kafka hay Prometheus.

---

## 1.4. Ý nghĩa khoa học và thực tiễn

### 1.4.1. Ý nghĩa khoa học
*   Đề tài góp phần chứng minh tính khả thi của việc ứng dụng mô hình Đa tác tử thông minh (Multi-Agent System) trong lĩnh vực kỹ nghệ độ tin cậy hệ thống (Site Reliability Engineering - SRE) và bảo mật tự động.
*   Đóng góp một mô hình Closed-loop thực nghiệm hoàn chỉnh kết hợp giữa Chaos Engineering chủ động và phản ứng tự phục hồi tự động, làm tài liệu tham khảo cho các nghiên cứu tiếp theo về bảo mật tự động hóa.

### 1.4.2. Ý nghĩa thực tiễn
*   **Tối ưu hóa tài nguyên vận hành:** Giúp các tổ chức giảm thiểu sự phụ thuộc vào kỹ sư trực ca (On-call support), giải phóng sức lao động của con người trong các tác vụ ứng cứu sự cố lặp đi lặp lại.
*   **Triệt tiêu Downtime đột xuất:** Rút ngắn thời gian khôi phục hệ thống từ mức độ hàng chục phút (khi thao tác thủ công) xuống mức độ giây (khi tự động hóa qua API), bảo vệ trải nghiệm của người dùng cuối.
*   **Công cụ học tập trực quan:** Sản phẩm cung cấp mô hình trực quan hỗ trợ công tác nghiên cứu, thực hành thực tế về an toàn thông tin hệ thống microservices và quy trình DevSecOps nâng cao cho sinh viên ngành Công nghệ thông tin.

---

## 1.5. Cấu trúc báo cáo nghiên cứu khoa học

Báo cáo nghiên cứu khoa học được cấu trúc thành 6 chương chính như sau:

*   **Chương 1: Mở đầu:** Giới thiệu tính cấp thiết, mục tiêu nghiên cứu, đối tượng, phạm vi và ý nghĩa của đề tài.
*   **Chương 2: Cơ sở lý thuyết và công nghệ liên quan:** Trình bày lý thuyết nền tảng về Kubernetes, Chaos Engineering, Apache Kafka, kiến trúc Multi-Agent AI và các công cụ DevOps/SecOps liên quan.
*   **Chương 3: Thiết kế kiến trúc hệ thống Zero Door:** Phân tích chi tiết thiết kế logic, luồng dữ liệu khép kín và kiến trúc thành phần của 3 Agent (Nemesis, Gaia, Hephaestus) và Chaos Worker.
*   **Chương 4: Hiện thực hóa và triển khai hệ thống:** Chi tiết hóa mã nguồn triển khai, kỹ thuật bảo mật container (Distroless), và tự động hóa hạ tầng đám mây sử dụng Terraform IaC.
*   **Chương 5: Thực nghiệm, đo đếm và đánh giá kết quả:** Trình bày số liệu thực nghiệm thu được từ các kịch bản tấn công giả lập, phân tích các chỉ số MTTD/MTTR và đánh giá giới hạn hệ thống.
*   **Chương 6: Kết luận và hướng phát triển:** Tổng kết các đóng góp chính của đề tài, thẳng thắn nhìn nhận các hạn chế và đề xuất giải pháp cải tiến trong tương lai.
