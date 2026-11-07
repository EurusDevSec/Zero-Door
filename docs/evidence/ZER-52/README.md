# ZER-52 — Kết quả pilot Runtime07

Ngày 07/11/2026 (UTC+7). [AC-01 trên Linear](https://linear.app/zero-door/issue/ZER-52/pilot-lap-dje-xac-djinh-bien-thien-va-loi-djo). Pilot mô tả trên lab local, với một case SQLi và case lành tính C0. Hai block bao phủ đủ B0, B1 và B2 theo phạm vi SQLi-only đã chốt sau khi bỏ RQ2.

## Kết quả và kiểm chứng

- Hoàn tất 12/12 ca với hai mẫu cho mỗi tổ hợp trong 4.637,015 giây, dưới trần pilot 7.200 giây. Runtime07 dùng trần WSL 6 GiB.
- Review độc lập xác minh 12 fixture và namespace riêng, 12 cleanup CLEAN, 24 cây tiến trình đã đóng và 36 topic Kafka đã xóa với readback rỗng. Terminal ghi nhận lab OFFLINE.
- B1 và B2 đều chặn nguồn ở 2/2 ca SQLi. B0 SQLi giữ vai trò đối chứng. Probe nghiệp vụ lành tính đạt ở cả 12 ca. Hai B2/C0 trả Gaia ABSTAIN trước Kafka, được tính là sai quyết định đầu tiên.
- Batch dùng 96 HTTP, 24 TCP và 6 lượt model, với 3.915 token vào, 431 token ra và chi phí ước tính 0,000607 USD. Trong lúc chạy hoặc cleanup, Windows còn ít nhất 1.208 MiB khả dụng và guest còn ít nhất 1.951 MiB. Memory PSI some avg10 của guest cao nhất 3,04.

## Số liệu theo ca

Các cột thời gian tính bằng giây. Trọn vòng gồm thực thi và cleanup. Dấu — biểu thị trường không áp dụng hoặc không ghi nhận chặn nguồn.

| Ca | Block | Nhóm | Case | Workflow | Trọn vòng | Inference | Quyết định đầu tiên | Chặn nguồn |
| ---: | ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | 1 | B0 | C0 | 17.172 | 353.438 | — | — | — |
| 2 | 1 | B1 | SQLi | 40.531 | 385.171 | — | Đúng | Có |
| 3 | 1 | B2 | C0 | 22.360 | 373.625 | 4.984 | Sai (ABSTAIN) | — |
| 4 | 1 | B0 | SQLi | 17.641 | 365.234 | — | — | — |
| 5 | 1 | B1 | C0 | 17.625 | 362.734 | — | Đúng | — |
| 6 | 1 | B2 | SQLi | 80.688 | 425.203 | 6.031 | Đúng | Có |
| 7 | 2 | B2 | SQLi | 59.718 | 403.875 | 4.501 | Đúng | Có |
| 8 | 2 | B1 | C0 | 17.688 | 363.156 | — | Đúng | — |
| 9 | 2 | B0 | SQLi | 17.625 | 362.641 | — | — | — |
| 10 | 2 | B2 | C0 | 20.531 | 364.594 | 2.968 | Sai (ABSTAIN) | — |
| 11 | 2 | B1 | SQLi | 49.515 | 394.016 | — | Đúng | Có |
| 12 | 2 | B0 | C0 | 17.593 | 361.750 | — | — | — |

## Biến thiên, overhead và lỗi đo

Trung bình ± độ lệch chuẩn mẫu, tính bằng giây.

| Nhóm | Case | n | Workflow | Trọn vòng |
| --- | --- | ---: | ---: | ---: |
| B0 | SQLi | 2 | 17.63 ± 0.01 | 363.94 ± 1.83 |
| B0 | C0 | 2 | 17.38 ± 0.30 | 357.59 ± 5.88 |
| B1 | SQLi | 2 | 45.02 ± 6.35 | 389.59 ± 6.25 |
| B1 | C0 | 2 | 17.66 ± 0.04 | 362.94 ± 0.30 |
| B2 | SQLi | 2 | 70.20 ± 14.83 | 414.54 ± 15.08 |
| B2 | C0 | 2 | 21.45 ± 1.29 | 369.11 ± 6.39 |

Workflow B2 lâu hơn B1 trung bình 25,18 giây ở SQLi và 3,79 giây ở C0. Inference B2 trung bình 5,27 giây ở SQLi và 3,98 giây ở C0. Cả hai B2/C0 dừng trước handoff Kafka. Workflow bao gồm nhiều bước và chênh lệch tổng không cô lập chi phí từng bước.

Analyzer v4 không phát hiện lỗi đo hoặc thiếu dữ liệu trong 12 ca Runtime07. Những lượt dừng trước Runtime07 được lưu riêng và không gộp vào bảng. Đồng hồ monotonic của host hỗ trợ đo thời lượng workflow. Với hai mẫu mỗi tổ hợp và thiếu nguồn onset/recovery đồng bộ, pilot này phục vụ mô tả và lập kế hoạch. MTTD, MTTR, uptime và hiệu quả thống kê chưa được xác lập.

## Đầu vào cho thực nghiệm chính thức

Đề xuất thăm dò 5 ca mỗi tổ hợp. Ngoại suy từ trọn vòng của pilot cho khoảng 186–190 phút với 30 ca, chưa gồm BM, điều phối và overhead phiên thực nghiệm. Đây là ước tính thực nghiệm, chưa phải lịch hay trần ngân sách. Số lần lặp, điều kiện chạy và KPI được khóa riêng trong [ZER-53](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc).

## Nguồn và kiểm toàn vẹn

- Revision repo tại lúc đo `7f806f13bc989934b7c880dcef5dfb6897c73695`. Protocol Runtime07 SHA-256 `5f66e9307c6fb50a436037f2715e3b41e1ffde8a2d57c397bb139fe415b529e9`. 265 hash nguồn được đối chiếu.
- Seal Runtime07 ghi SHA-256 của 4.549 tệp dữ liệu gốc, biên bản terminal và kết quả phân tích. SHA-256 của seal `d1b2a99c179db096dc48c9af90159467a65bc9c21b73565a0b6f4868b1ac5c3a`.
- Bản GitHub gồm số liệu tổng hợp và theo ca. Log gốc và biên bản chi tiết lưu cục bộ để đối chiếu. [Hồ sơ nghiệm thu trên Linear](https://linear.app/zero-door/document/zer-52-bang-chung-nghiem-thu-runtime07-070481791812).
