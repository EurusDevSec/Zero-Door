

# PROJECT PLAN: ZERO DOOR (Self-Healing DevSecOps)

### 1. Thông tin Dự án

* 
**Tên đề tài:** Ứng dụng kiến trúc Multi-Agent AI và kỹ thuật Chaos Engineering xây dựng cơ chế Self-Healing cho hệ thống Microservices.


* **Mã dự án (Internal):** Zero Door.
* 
**Thời gian thực hiện:** 06 tháng (01/2026 - 06/2026).


* 
**Ngân sách vận hành:** 4.900.000 VNĐ (Cloud Server, API Token, Domain).



### 2. Bối cảnh & Mục đích (Context & Goal)

* 
**Bối cảnh:** Các cuộc tấn công mạng ngày càng tự động hóa, trong khi quy trình bảo mật cũ phụ thuộc con người (Human-in-the-loop) gây chậm trễ.


* **Mục đích cốt lõi:** Chuyển từ "Phòng thủ thụ động" sang **"Phòng thủ chủ động" (Proactive Defense)**. Xây dựng hệ thống tự trị có khả năng **Self-Healing (Tự phục hồi)**: tự tấn công để tìm lỗ hổng và tự vá lỗi trước khi triển khai thực tế.


* 
**Mục tiêu "Zero Door":** Triệt tiêu các cửa hậu (backdoors) và tối ưu hóa độ tin cậy (SRE) thông qua mô hình Red Team vs. Blue Team nội bộ.



### 3. Tech Stack & Kiến trúc Hệ thống

A. Tech Stack 

* **Hạ tầng (Infrastructure):** Docker, Kubernetes (K3s/Minikube hoặc Cloud Cluster).
* **Backend Core:** Java Spring Boot.
* **AI Integration:** Spring AI kết nối với LLM (OpenAI/Local LLM).
* 
**Message Broker:** Kafka hoặc RabbitMQ (để giao tiếp giữa các Agent).


* **Monitoring:** Prometheus (Metrics), Visual Log dashboard.

B. Kiến trúc 3 Trụ cột (The 3 Agents) 

Hệ thống hoạt động dựa trên vòng lặp kín: **Attack -> Detect -> Heal**.

1. **Agent Nemesis (Red Team - Tấn công):**
* *Nhiệm vụ:* Sử dụng GenAI để sinh payload tấn công tự động.
* 
*Vũ khí:* SQL Injection, DDoS (Application Layer), Resource Exhaustion (Tấn công tài nguyên).




2. **Agent Gaia (Observer - Giám sát):**
* *Nhiệm vụ:* Giám sát Metrics, phân tích Logs thời gian thực.
* 
*Visual:* Dashboard hiển thị trạng thái "Chiến tranh AI".




3. **Agent Hephaestus (Blue Team - Phòng thủ):**
* *Nhiệm vụ:* Tương tác trực tiếp với Kubernetes API.
* 
*Hành động:* Scale up/down Pods, Block IP, Rollback phiên bản lỗi.





4. Lộ trình Thực hiện & Tasks (Phân chia theo tháng) 

| Giai đoạn | Thời gian | Công việc Chính (Tasks) | KPI / Sản phẩm đầu ra |
| --- | --- | --- | --- |
| **Phase 1: Setup** | **Tháng 01** | - Nghiên cứu tài liệu Chaos Engineering & Spring AI.<br>

<br>- Thiết lập Kubernetes Cluster. | - Môi trường K8s sẵn sàng hoạt động.<br>

<br>- Báo cáo tổng quan. |
| **Phase 2: Target** | **Tháng 02** | - Code ứng dụng E-commerce (Target App).<br>

<br>- Xây dựng Agent **Gaia** (Module giám sát). | - Source code App E-commerce.<br>

<br>- Dashboard Gaia hiển thị metrics thời gian thực. |
| **Phase 3: Attack** | **Tháng 03** | - Phát triển Agent **Nemesis**.<br>

<br>- Tích hợp LLM sinh kịch bản tấn công. | - Nemesis thực hiện được SQL Injection & Stress Test.<br>

<br>- **KPI:** Đẩy CPU target app > 80%. |
| **Phase 4: Defend** | **Tháng 04** | - Phát triển Agent **Hephaestus**.<br>

<br>- Lập trình logic tương tác K8s API. | - Hephaestus tự động Scale pod khi CPU cao.<br>

<br>- **KPI:** Thời gian phản ứng < 1 phút. |
| **Phase 5: War Game** | **Tháng 05** | - Tích hợp toàn hệ thống (3 Agents đấu nhau).<br>

<br>- Đo đếm thông số thực nghiệm. | - Video demo quá trình Tấn công - Tự phục hồi.<br>

<br>- Bảng số liệu MTTD/MTTR. |
| **Phase 6: Closing** | **Tháng 06** | - Viết báo cáo tổng kết, đóng gói sản phẩm.<br>

<br>- Làm Slide/Poster bảo vệ. | - Báo cáo toàn văn.<br>

<br>- Mã nguồn đầy đủ. |

### 5. Chỉ số Đánh giá Thành công (KPIs)

Để nghiệm thu đề tài, hệ thống phải đạt các chỉ số sau:

* **Thời gian phát hiện sự cố (MTTD):** < 1 phút.
* **Thời gian phục hồi dịch vụ (MTTR):** < 2-3 phút.
* **Độ sẵn sàng (Uptime):** ≥ 99.9% ngay cả khi đang bị Nemesis tấn công.

6. Sản phẩm Bàn giao 

1. Full Source Code (Java Spring Boot).
2. File cấu hình Kubernetes (Manifests/Helm Charts).
3. Video Demo kịch bản thực tế.
4. Báo cáo khoa học.