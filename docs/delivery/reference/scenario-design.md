# Thiết kế kịch bản và phục hồi

Thiết kế nguồn, cần khóa contract và kiểm chứng trước kết luận thực nghiệm. Issues tương ứng nằm ở milestone R2 và R3; không duy trì lớp work-package riêng.

## SQLi với Google Online Boutique

Không giả định Boutique hiện có SQL database hoặc endpoint dễ bị SQLi. Để giữ hệ thống mục tiêu được thầy chấp thuận, đề xuất bổ sung một dịch vụ tìm kiếm/catalog thử nghiệm với dữ liệu e-commerce giả lập, database nhẹ như SQLite và route qua ingress lab. Có bản dễ tổn thương phục vụ phép thử và bản dùng truy vấn tham số; tất cả giới hạn trong namespace nghiên cứu, không công khai ra Internet. Đây là phần bổ sung mô hình thực nghiệm, phải ghi rõ trong kiến trúc/paper, không mô tả như lỗ hổng sẵn có của Google Boutique.

Giữ Boutique và luồng mua hàng làm đối tượng availability; dùng fixture để kiểm chứng vector SQLi và containment. Nếu kết luận về availability áp dụng cho cả hai, định nghĩa hai luồng probe và báo kết quả riêng, không gộp để che luồng thất bại. Không cần viết lại toàn bộ ứng dụng thương mại điện tử hoặc thêm PostgreSQL để có phép thử SQLi.

## Mô hình chữa lỗi cần hợp lý với nguyên nhân

- CPU/resource quá tải: gây tải vào workload target thật; kiểm tra scale có giảm latency/error hoặc throttling. Pod stress riêng chỉ dùng nếu nghiên cứu đúng tranh chấp node và có bằng chứng tác động, không ánh xạ mức CPU của attacker thành CPU của app.
- SQLi: ghi nguồn từ kết nối/ingress tin cậy, không lấy một X-Forwarded-For bất kỳ do client khai. Chặn tại điểm nhìn thấy nguồn trước NAT hoặc gateway phù hợp. Không coi IP `0.0.0.0` và NetworkPolicy tạo được là bằng chứng containment.
- Bad release: fault phiên bản ứng dụng/config và rollback về release tốt đã biết. Error rate cao do flood không tự là bằng chứng bản deploy sai; không rollback mọi 5xx.
- Scale-down: chỉ sau cửa sổ tải thấp/khỏe đủ dài, giới hạn min/max và tránh HPA giành quyền replicas. Reset thí nghiệm tách khỏi logic hồi phục.
- Pod Kill: giữ như phép thử bổ sung để đánh giá controller mặc định và xem healer có can thiệp thừa; không dùng thay SQLi.
