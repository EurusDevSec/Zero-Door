# ZER-19 — điều tra nguyên nhân runtime-02, 29/10/2026

**Kết luận: đã xác nhận một đợt chậm đồng thời ở Docker/K3s trong WSL, có áp lực CPU và bộ nhớ; guard dừng đúng. Chưa xác định được tiến trình khởi phát đợt chậm. Chưa có căn cứ chạy lại nghiệm thu hoặc tuyên bố đã sửa lab.**

Điều tra này chỉ đọc log, trạng thái và dữ liệu Prometheus đã lưu. Không chạy runtime-03, gọi model, gửi HTTP/TCP fixture, tạo tài nguyên hoặc sửa hạ tầng. Linear ZER-19 đọc lại vẫn Backlog; AC02/03 chưa được nghiệm thu. Source sản phẩm 9 pin và 26 pin lúc runtime-02 đều giữ nguyên. 183 artifact cũ đã kiểm hash/size trước khi thêm liên kết báo cáo; không sửa raw runtime-01/02.

## Chuỗi bằng chứng

Các giờ dưới đây là **UTC ngày 28/10**; cộng 7 giờ để đổi sang giờ Việt Nam. Sự cố chính xảy ra khoảng **22:55:30–22:55:49 giờ Việt Nam**.

| Mốc / phép đo | Bằng chứng | Diễn giải |
|---|---|---|
| 15:55:23.461 | runtime-02/raw/0057-release-fixture.json | Runner đang đợi lệnh mở cổng khởi động fixture; khi bị ngắt không có return code. Kết quả ghi file từ xa vẫn UNKNOWN. |
| 15:55:26.529 | runtime-02/raw/0058-memory.json | Mẫu cuối thành công: MemAvailable 2.34 triệu KiB, memory PSI avg10 0.08. Đây là mẫu trước sự cố. |
| 15:55:31.625 | runtime-02/raw/0059-memory.json | Lệnh thu mẫu kế tiếp hết hạn 4 giây; watchdog dừng tác vụ. |
| 15:55:32.029 → 15:55:48.940 | [Docker exec transaction](docker-exec-window.json), exec ID ff65663e… | Giao dịch exec-start kéo dài **16.911 giây** ở log Docker, độc lập với log Python. Không phải thời gian CPU riêng của lệnh cat. |
| Cùng cửa sổ | [K3s server log](live-readonly/server-history.json) | Kine truy vấn bắt đầu 15:55:30.539 mất **17.696 giây**; truy vấn khác mất 10–15 giây; housekeeping **9.915 giây**, Metrics Controller mất heartbeat. |
| Bắt đầu 15:55:32.022 | [Prometheus scrape](historical-metrics/scrapes.json) | Scrape cAdvisor của server mất **16.655 giây**; nhiều lịch scrape bị trễ rồi cùng tiếp tục lúc 15:55:47.978. Các điểm up=1 không chứng minh không có độ trễ. |
| 15:55:24.989 → 15:55:48.449 | [Cart CPU](historical-metrics/cart-throttling.json) | **164/166 chu kỳ CPU hoạt động bị throttle**, với limit 200m; đây là tỷ lệ chu kỳ, không phải 98.8% toàn bộ thời gian treo. |
| 15:55:48–55 | runtime-02/final-audit/01.json và [containerd](history-readonly/agent-containerd-history.json) | Health check cart timeout; containerd gửi SIGTERM lúc 15:55:53.283; cart thoát Completed/0 và được khởi động lại, restart 41→42. Không thấy OOM kill. |
| 15:55:52–15:56:32 | K3s server log | metrics-server mất endpoint, gây discovery lỗi và chậm xóa namespace. Sau khi phục hồi, namespace bị xóa lúc 15:56:32.235. Không cần ép bỏ finalizer. |

Docker logs được ghép bằng thời gian, tên node và exec ID; chúng không chứa command body nên không có độc lập xác nhận payload của exec từ log daemon. Runner ghi rõ câu lệnh đọc /proc; các giao dịch tuần tự trước đó khớp cùng nhịp thu mẫu.

## Áp lực tài nguyên đã được xác nhận, nhưng chưa quy cho một ứng dụng

[Phép tính tái lập](analyze.py) → [analysis.json](analysis.json) dùng một node-exporter duy nhất: hai node k3d dùng chung kernel WSL, không cộng hai bản bộ đếm.

Trong khoảng **15:55:00.987–15:55:47.978** (46.991 giây):

- CPU waiting tăng **18.874 giây**, tương đương **40.16%** cửa sổ; ở khoảng 12.999 giây tiếp theo, tỷ lệ khoảng **85.72%**.
- Memory waiting tăng **3.090 giây**; memory full stall tăng **2.866 giây**.
- I/O waiting tăng **3.166 giây**; I/O full stall tăng **0.176 giây**.
- MemAvailable ở hai đầu khoảng vẫn khoảng **2.36–2.37 GB**; bộ đếm oom_kill bằng 0. Có thêm major page faults/swap activity, nhưng dữ liệu không chứng minh thiếu dung lượng RAM kéo dài.

Các khoảng stall có thể chồng nhau, không cộng chúng thành tổng thời gian lỗi. Đây là delta bộ đếm qua cửa sổ scrape, **không phải avg10** và không tái tạo được mẫu guard đã mất. Theo [tài liệu PSI của Linux](https://docs.kernel.org/accounting/psi.html), bộ đếm total giúp thấy các đợt stall ngắn mà số trung bình có thể bỏ lỡ. Vì vậy “28 mẫu guard đạt” không phủ nhận áp lực trong khoảng mù.

[CPU từng workload](historical-attribution/workload-cpu.json) không đủ để chỉ ra một thủ phạm duy nhất: cadence khác nhau, thiếu thống kê toàn bộ tiến trình Windows/WSL và root-cgroup metric không có series. Fixture/proxy đã tiêu CPU lúc khởi động; chúng có thể góp tải nhưng không đủ bằng chứng quy toàn bộ stall cho chúng. Không quy cho Chrome, Claude, Defender, lỗi đĩa hoặc một tiến trình cụ thể. Truy vấn System event log trong cửa sổ 15:48–15:58 không trả sự kiện phù hợp; điều đó cũng không loại trừ các nguyên nhân này.

Cart đã có lỗi probe/restart trước lượt02 (restart trước lúc 15:49:25). Throttle CPU và timeout probe là yếu tố góp phần có bằng chứng; **chưa chứng minh chỉ tăng CPU limit sẽ chữa đợt chậm toàn VM**. [Kubernetes mô tả](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) liveness thất bại liên tiếp dẫn đến restart; event/exit/containerd ở đây phù hợp cơ chế đó. Không tự tăng timeout probe để biến hệ thống chậm thành khỏe.

## Phần thuộc runner và phần thuộc lab

- Guard 4 giây hoạt động đúng: mất khả năng quan sát thì dừng. Log độc lập loại trừ giải thích “chỉ lỗi chờ subprocess Python” cho toàn bộ sự cố.
- Readiness hiện chỉ kiểm RAM/memory PSI trong 120 giây; chưa ghi CPU/I/O PSI và chưa đối chiếu shared restart ở cuối cửa sổ đó. Vì vậy READY chỉ có giá trị với các kiểm đã làm, không dự báo được đợt chậm phát sinh khi setup.
- Receipt command chỉ có thời điểm bắt đầu/error_type khi lỗi; chưa có elapsed/returncode/output sau kill. Đây là thiếu sót chẩn đoán, không có bằng chứng nó gây stall. Không bổ sung ngược dữ liệu không biết vào raw cũ.
- Lượt01 là lỗi probe review của agent, đã sửa boundary và cleanup. Không gộp lỗi đó vào nguyên nhân tài nguyên của lượt02.

## Bước tiếp theo tối thiểu trước khi xin chạy lại

1. Chuẩn bị một delta nhỏ cho runner: ghi elapsed và lý do timeout/cancel, exit/cleanup của child; thêm CPU/I/O PSI trong **cùng lệnh đọc /proc hiện có**, giữ nguyên timeout 4 giây, ngưỡng RAM/memory PSI và hành vi fail-closed. Không thêm framework hoặc đổi AC. Không ghi stdin/credentials vào receipt.
2. Trong 120 giây preflight sẵn có, đối chiếu shared restart đầu/cuối và trạng thái control path; nếu đã có drift/timeout thì kết luận NO-GO trước tạo fixture. Kiểm offline riêng các hành vi thêm, khóa lại source và review delta. CPU/I/O là dữ liệu chẩn đoán, không tự đặt ngưỡng mới chưa được thống nhất.
3. Chỉ sau delta đó mới chuẩn bị đúng một gói nghiệm thu mới. Giữ kiểm trong suốt setup, vì idle preflight sạch vẫn không bảo đảm phase khởi động sạch. Nếu cùng đợt stall tái diễn thì thu bằng chứng và kết thúc, không nối chuỗi retry; khi đó cần quyết định ổn định/đổi môi trường hoặc gói điều chỉnh tài nguyên cụ thể có đo trước–sau.

Ba bước trên là đề xuất từ điều tra, **chưa áp dụng** và chưa cấp quyền runtime mới. Không tăng timeout lên 20 giây để bỏ qua stall 17 giây; không sửa shared cart/WSL/Docker dựa vào phỏng đoán.

## Trạng thái cuối và giới hạn

Lần đọc hiện tại cho thấy Docker/WSL đã được khởi động lại lúc **09:38:42 ngày 29/10 giờ Việt Nam**, sau sự cố; đây không phải thao tác của lượt điều tra. Các lệnh đọc hiện tại trả nhanh, cart Ready/restart43 và namespace riêng vẫn absent. Điều này chỉ mô tả trạng thái mới, không chứng minh nguyên nhân cũ đã được sửa hoặc độ ổn định khi có setup.

Runtime-02 giữ **NOT_MET / cleanup INCOMPLETE** do shared restart; tài nguyên riêng đã xóa. ZER-19 **chưa Done**, chưa publication. Phần Nemesis/model/executor chưa được thực thi trong lượt02, nên không kết luận nó thành công hay thất bại chức năng. Điều tra kết thúc với chuỗi nguyên nhân gần đã có bằng chứng; tác nhân khởi phát cuối cùng vẫn UNKNOWN.

