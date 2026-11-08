# ZER-24 — Đối chiếu pilot, protocol và KPI

Ngày 08/11/2026, UTC+7. Phạm vi SQLi/C0 theo quyết định 28/10. Bản cập nhật sau review độc lập của Claude, chờ kiểm diff và Hoàng chấp nhận. [AC trên Linear](https://linear.app/zero-door/issue/ZER-24/pilot-va-khoa-protocol-sqli) · [Phạm vi](../../delivery/SCOPE.md)

| AC | Kỳ vọng | Kết quả đề nghị |
| --- | --- | --- |
| AC-01 | Pilot lặp đủ B0/B1/B2 × SQLi/C0, thấy biến thiên, overhead, lỗi đo và có căn cứ chọn số lặp | Đủ bằng chứng ở mức pilot mô tả. Runtime07 có 12/12 ca hợp lệ cho các phép đo pilot, hai ca mỗi ô. Dự toán 30 ca tự động là 186,04–190,25 phút từ số liệu 6 GiB. |
| AC-02 | Protocol đối chứng được khóa trước formal | Có biên bản Hoàng duyệt đúng hash ZER-53. Bản đúng byte đã đặt vào đường dẫn tài liệu chính thức cục bộ, chờ lưu vào lịch sử Git. FORMAL_HOLD theo §5. |
| AC-04 | Tái tính từ dữ liệu gốc, phân loại đạt, không đạt và thiếu dữ liệu, lưu mọi lượt dừng | Claude đã tái tính khớp số liệu của bản trước. Bản này làm rõ cách phân loại và điều kiện quan sát, chờ kiểm diff. |
| AC-03 nguồn | War Game 4 giờ | Chuyển phần bổ sung theo quyết định 28/10. Chưa có kết quả đạt 4 giờ. [ZER-54](https://linear.app/zero-door/issue/ZER-54/chay-war-game-co-probe-va-budget-dja-duyet) |

## AC-01 — Tái tính Runtime07

Nguồn gốc ở `scratch/zer52-checkout/docs/evidence/ZER-52/runtime-07/`. Biên bản terminal kết thúc lúc **18:29:48 +07:00 ngày 07/11/2026**, trạng thái OFFLINE, runner exit 0. Source `7f806f13bc989934b7c880dcef5dfb6897c73695`. Protocol pilot SHA-256 `5f66e9307c6fb50a436037f2715e3b41e1ffde8a2d57c397bb139fe415b529e9`. Bảng seal SHA-256 `d1b2a99c179db096dc48c9af90159467a65bc9c21b73565a0b6f4868b1ac5c3a`. Đã đối chiếu 4.549/4.549 hash tệp batch, 265/265 pin nguồn, hash biên bản terminal và phân tích v4. [Báo cáo ZER-52](https://linear.app/zero-door/document/zer-52-bang-chung-nghiem-thu-runtime07-070481791812)

**Cách tái tính.** Theo từng `trial-NN`, đối chiếu nhóm, case, block và UID trong `pilot-cell.json`, `worker-native-join.json` và `postcondition-probe.json`. Kiểm hash `worker-result.json` theo bản ghi join. Đọc quyết định hành động từ `decision-receipt.json`, giữ Gaia ABSTAIN ở `gaia-receipt.json` nếu luồng dừng tại đó. Với containment trên fixture, kiểm cùng nguồn và UID, probe 403, policy hash/action ID khớp và hậu điều kiện terminal SUCCESS. Chuỗi benign kỳ vọng từ nguồn khác là 200/201/200/200/404. Workflow và inference lấy từ hai trường `response_workflow_ms`, `model_latency_ms` trong `timing.json` rồi chia 1.000. Trọn vòng bằng `work_elapsed_s + cleanup_elapsed_s` trong `acceptance.json`. Độ lệch chuẩn mẫu chia cho n−1. Tính lại độc lập rồi so với `session-20261107/runtime07-analysis-v4.json`.

| Ca | Block | Nhóm/case | Quyết định pilot | Probe cùng nguồn | Workflow (s) | Trọn vòng (s) | Inference (s) |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 01 | 1 | B0/C0 | BASELINE | 200 | 17.172 | 353.438 | 0.000 |
| 02 | 1 | B1/SQLI | BLOCK_IP | 403 | 40.531 | 385.171 | 0.000 |
| 03 | 1 | B2/C0 | ABSTAIN | 200 | 22.360 | 373.625 | 4.984 |
| 04 | 1 | B0/SQLI | BASELINE | 200 | 17.641 | 365.234 | 0.000 |
| 05 | 1 | B1/C0 | NO_ACTION | 200 | 17.625 | 362.734 | 0.000 |
| 06 | 1 | B2/SQLI | BLOCK_IP | 403 | 80.688 | 425.203 | 6.031 |
| 07 | 2 | B2/SQLI | BLOCK_IP | 403 | 59.718 | 403.875 | 4.501 |
| 08 | 2 | B1/C0 | NO_ACTION | 200 | 17.688 | 363.156 | 0.000 |
| 09 | 2 | B0/SQLI | BASELINE | 200 | 17.625 | 362.641 | 0.000 |
| 10 | 2 | B2/C0 | ABSTAIN | 200 | 20.531 | 364.594 | 2.968 |
| 11 | 2 | B1/SQLI | BLOCK_IP | 403 | 49.515 | 394.016 | 0.000 |
| 12 | 2 | B0/C0 | BASELINE | 200 | 17.593 | 361.750 | 0.000 |

Cả hai block đủ sáu ô. Mỗi ca có UID riêng. Profile workload và bản ghi điều kiện quan sát khớp giữa các nhóm trong cùng case. Probe benign fixture đạt 12/12. Cleanup CLEAN 12/12, 24 cây tiến trình đóng và thu hồi, spec và số lần restart của thành phần dùng chung khớp. Review Runtime07 đã xác nhận 36 readback topic rỗng. B0 giữ hành vi đối chứng, SQLi quan sát được effect trong 2/2 ca và probe nguồn vẫn 200. B1 và B2 mỗi nhóm có 2/2 ca SQLi thấy effect rồi chặn đúng nguồn ở fixture. Hai B2/C0 ABSTAIN trước Kafka, đều chấm sai quyết định pilot, cả hai không thực thi chặn nhầm. Căn cứ chọn 12/12 ca là review độc lập trong `session-20261107/runtime07-result.md:35`, sau khi batch gốc ghi `RECONCILE_REQUIRED` và các ca ghi `OBSERVED_PENDING_REVIEW`.

**Điều kiện C0 của pilot.** Harness tạo bản ghi `SUSPICIOUS_LOG` mức WARNING cho cả sáu ca C0, với `value=0` và `threshold=0` trong `pilot-cell.json`. B1 nhận cùng tín hiệu và trả `NO_ACTION`. Hai `gaia-receipt.json` của ca 03 và 10 ghi Gaia ABSTAIN vì chỉ số 0 không xác lập hoạt động đáng ngờ dù sự kiện mang nhãn cảnh báo. Kết quả 0/2 phản ánh cách B2 xử lý tín hiệu do harness tạo. Giữ kết quả theo quy tắc pilot và giới hạn diễn giải ở điều kiện đó. C0 formal dùng đường detector đã pin và có thể không sinh cảnh báo.

| Nhóm/case | n | Workflow (s) | Trọn vòng (s) | Inference (s) |
| --- | ---: | ---: | ---: | ---: |
| B0/SQLI | 2 | 17.63 ± 0.01 | 363.94 ± 1.83 | 0.00 ± 0.00 |
| B0/C0 | 2 | 17.38 ± 0.30 | 357.59 ± 5.88 | 0.00 ± 0.00 |
| B1/SQLI | 2 | 45.02 ± 6.35 | 389.59 ± 6.25 | 0.00 ± 0.00 |
| B1/C0 | 2 | 17.66 ± 0.04 | 362.94 ± 0.30 | 0.00 ± 0.00 |
| B2/SQLI | 2 | 70.20 ± 14.83 | 414.54 ± 15.08 | 5.27 ± 1.08 |
| B2/C0 | 2 | 21.45 ± 1.29 | 369.11 ± 6.39 | 3.98 ± 1.43 |

Bảng báo mean ± SD. So B2−B1, workflow trung bình chênh **+25,18 s** trên SQLi và **+3,79 s** trên C0. Workflow gồm phần xử lý hành động/probe của từng đường chạy. Hai ca B2/C0 dừng trước Kafka, nên chênh lệch C0 chỉ mô tả hai đường chạy quan sát được. Inference là số đo riêng. Hai mẫu mỗi ô chỉ đủ mô tả pilot.

**Tài nguyên và ngân sách quan sát được.** Batch 4.637,015 s < 7.200 s. Mỗi ca 8 HTTP và 2 TCP, tổng 96 HTTP và 24 TCP. Sáu lượt model, 23.611 token dự trữ, 3.915 input, 431 output, 0,000607 USD ước tính. Cả 12 có receipt ngân sách, không lượt nào thiếu usage. Trước claim, 25 mẫu trong 120 s có Windows Available thấp nhất 4.098 MiB, tại claim 4.190 MiB, ngưỡng 2.868 MiB. Trong 825 mẫu work/cleanup, Windows thấp nhất 1.208,10 MiB và guest 1.950,76 MiB, đều trên sàn 1.024 MiB, PSI some avg10 cao nhất 3,04 so với trần 5. Các số trên thuộc profile pilot 6 GiB.

**Cơ sở số lặp.** Với 5 ca mỗi ô B0/B1/B2, lấy 5 lần tổng min/mean/max trọn vòng của sáu ô, chia 60. Kết quả lần lượt **186,04 / 188,14 / 190,25 phút**. Đây là kịch bản lập lịch mô tả, chưa tính điều phối, BM hoặc pha đo formal. Vượt cửa sổ đơn 120 phút. Chọn 5 ca mỗi ô để thăm dò, với một ca tương ứng 20 điểm phần trăm nếu đủ cả năm. Formal có thêm BM, tổng 40 ca. Ước lượng 516–532 phút ở §3 ZER-53 dùng giả định BM và phần đo bổ sung của protocol. Mỗi phiên vẫn theo giới hạn 120 phút và reserve 1.800 s trước claim.

## AC-02 — Đối chiếu bản đã khóa

[Bản protocol tại đường dẫn tài liệu chính thức](../ZER-53/protocol.md) được sao nguyên byte từ hồ sơ khóa và có SHA-256 `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8`, khớp biên bản Hoàng duyệt và hash Claude đã review. Base của bản khóa `22f668a0a3d7aec36fd5a878ef596f06de10dd89`. Bản sao cục bộ chờ lưu vào lịch sử Git cùng biên bản khóa và đính chính. [Biên bản khóa ZER-53](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc)

| Nội dung AC-02 | Vị trí và đối chiếu |
| --- | --- |
| RQ và cấu hình đối chứng | §1 giữ RQ1/RQ3, B0 đối chứng, B1 rules, B2 LLM và BM mô tả, HPA fixture OFF. B3 và claim RQ2 ngoài scope. |
| Ground truth, hành động và che đáp án | §2 khóa C5 effect là dữ liệu restricted, BLOCK_IP đúng nguồn/UID với TTL 180 s. C0 dùng dữ liệu public, NO_ACTION, ABSTAIN chấm riêng. Năm seed đánh giá tách pilot. H/O/S tách vai. BM thứ hai mỗi block có nhãn UNBLINDED_BY_DESIGN. |
| Số lặp, lịch và tài nguyên | §3 khóa 5 block × 8 ô, quy tắc PRNG/thứ tự, tiếp nối lịch đã seal, trần phiên, thời gian, traffic và budget. |
| Metric, KPI và điều kiện sẵn sàng | §4 giữ M1 trước guard, mẫu số và thiếu dữ liệu, phân biệt MTTD/reaction, containment và phục hồi. §5 khóa pins và điều kiện HOLD trước formal. |

**Đính chính mô tả ở §3 ZER-53.** Độ lệch chuẩn trọn vòng qua sáu ô pilot là **0,30–15,08 s**. B1/C0 có SD 0,298399 s, trong khi 1,83 s là SD của B0/SQLi. Dự toán 186,04–190,25 phút dùng min/mean/max của từng ô, nên kết quả dự toán và lịch 5 block không phụ thuộc sai lệch này. Claude đã xác nhận đính chính chỉ ảnh hưởng phần mô tả. Đính chính cũng có cạnh biên bản khóa trong ghi chú issue.

**FORMAL_HOLD.** §5 còn yêu cầu detector trên 5 variant đã pin, join clock và scorer/probe, BM và người chấm tách vai, cùng kiểm một vòng B2/C5 ở 5,5 GiB với cleanup. Kết quả idle 5,5 GiB và pilot dưới tải 6 GiB là hai bằng chứng riêng.

## AC-04 — Kết quả KPI và giới hạn

| Chỉ tiêu | Mẫu số, kết quả tái tính và lý do |
| --- | --- |
| Quyết định đầu tiên theo pilot | B1 SQLi **2/2 đạt**, C0 **2/2 đạt**. B2 SQLi **2/2 đạt**, C0 **0/2 đạt** do ABSTAIN. B0 không có quyết định. Pilot chấm theo quy tắc Runtime07, còn M1 formal yêu cầu bằng chứng tham số trước guard từ resolver đã pin và audit của cohort formal. |
| Chặn nguồn và probe lành tính | Trong 6 ca SQLi có 6/6 effect fixture quan sát được. B1 và B2 mỗi nhóm **2/2 đạt containment trên fixture**. B0 vẫn uncontained 2/2 theo đối chứng. C0 có **0/6 chặn nhầm**, benign fixture **12/12 đạt**. M12 formal còn cần probe Boutique theo protocol, chưa có kết quả M12 formal ở đây. |
| P107 MTTD <60 s | **`UNKNOWN` (D-01).** B1 và B2 mỗi nhóm có 2 ca SQLi quan sát được effect. Cả hai nhóm có 0/2 ca với phép ghép T_eff/T_det đủ chuẩn. Mean không xác định, xác minh đạt 0/2, thiếu 2/2 và cận do thiếu dữ liệu [0, 1] ở mỗi nhóm. |
| P187 reaction <60 s | **`UNKNOWN` (D-01).** B1 và B2 đều có action SUCCESS 2/2 ca SQLi, nhưng mỗi nhóm có 0/2 ca với phép ghép T_det/T_ac đủ chuẩn. Mean không xác định, xác minh đạt 0/2, thiếu 2/2 và cận do thiếu dữ liệu [0, 1] ở mỗi nhóm. |
| P107 MTTR <120 s và <180 s, TotalRecovery, M7/M8 | **`NOT_EVALUABLE_BY_DESIGN`** cho phép đánh giá C5 một request. Pilot giới hạn `max_worker_sends=1` và dùng probe kiểm containment, thiếu chuỗi lỗi nghiệp vụ và phục hồi ổn định cần cho D-04. Protocol formal ghi trước cùng giới hạn thiết kế. MTTR của cam kết nguồn chưa được đánh giá. |
| P108 uptime ≥99,9% | **`NOT_MEASURED`.** Thiếu cửa sổ và chuỗi probe nghiệp vụ Boutique dưới tải liên tục đủ để tính cận D-05. Tỷ lệ fixture benign 12/12 thuộc phép kiểm khác. |
| P179 CPU >80% và War Game 4 giờ | **`OUT_OF_SCOPE`** trong đợt SQLi-only. Cam kết nguồn chưa được đánh giá ở đợt này. |

Nguồn công thức và ngưỡng là ZER-32 §3.2–3.8 và bản trích đăng ký. B2 là nhóm báo KPI nguồn theo protocol. B1 dùng cùng định nghĩa để đối chiếu. Analyzer v4 ghi `NOT_ESTIMATED` chung cho các KPI thời gian và uptime. Bảng dùng nhãn riêng theo nguyên nhân và quy ước nguồn. Chỉ số workflow dùng đồng hồ monotonic của host, còn các phép ghép mốc giữa nguồn thời gian khác nhau cần bằng chứng đồng bộ. [ZER-32](../ZER-32/requirements-and-kpi.md) · [Cam kết nguồn](../../handoff/2026-10-17-registration-requirements-excerpt.md)

### Các lượt dừng và lỗi đo được giữ lại

Số liệu từ `runtime-0N/acceptance.json` và biên bản từng lượt. Cột quan sát là số ô có `OBSERVED_PENDING_REVIEW` trong biên bản gốc. Phần này bảo toàn lịch sử, tách khỏi mẫu số thống kê của Runtime07.

| Lượt | Quan sát / dừng / NOT_RUN | Lý do dừng và cleanup gốc |
| --- | --- | --- |
| Runtime01 | 0 / 1 / 11 | NetworkPolicy thiếu hook khi admission. Dừng trước traffic, CLEAN. |
| Runtime02 | 1 / 1 / 10 | B1/SQLi dừng với MEMORY_STOP. Bản ghi ownership topic thiếu xác nhận, cleanup gốc INCOMPLETE. Biên bản riêng `session-20261104/cleanup-01/result.json` xác nhận CLEAN và toàn bộ topic của ca đã vắng mặt. |
| Runtime03 | 3 / 1 / 8 | B0/SQLi không qua memory settle, mẫu PSI 1,18 vượt ngưỡng settle 1. CLEAN. |
| Runtime04 | 0 / 1 / 11 | Timeout lệnh tạo topic và ownership UNKNOWN, chưa gửi workload. Cleanup gốc INCOMPLETE, biên bản reconcile riêng xác nhận CLEAN sau đó. |
| Runtime05 | 0 / 1 / 11 | Dừng trước workload, Windows Available 899 MiB dưới sàn 1.024 MiB. CLEAN. |
| Runtime06 | 6 / 1 / 5 | Dừng trong kiểm transport với `MEMORY_STOP` khi PSI guest 24,97 vượt 5, dù Windows còn khoảng 3.590 MiB. Biên bản work ghi `ValueError:TRANSPORT_DEPENDENCIES_NOT_READY`. CLEAN. Nguồn gây áp lực còn UNKNOWN. |
| Cửa sổ terminal Runtime07 trước batch | Chưa claim batch | API Kubernetes trả ServiceUnavailable lúc khởi động. Terminal WINDOW_FAILED và OFFLINE. Biên bản riêng ở `session-20261107/runtime07-terminal/result.json`. |
| Runtime07 r2 | 12 / 0 / 0 | Đủ 12/12 ca pilot có biên bản và CLEAN. Hai quyết định B2/C0 sai vẫn ở mẫu số. |

Runtime01 giữ cả nhãn analyzer ban đầu về trạng thái worker và bản sửa sau khi đối chiếu process. Runtime03 giữ phân tích ban đầu và bản sửa đếm abstention/usage, gồm ô thiếu receipt budget. Runtime04 giữ kết quả gốc và kiểm hồi quy của analyzer v4 cho pin timeout Kafka. Bản đối chiếu hiện tại có đủ trường để tính các đại lượng pilot đã nêu. KPI cần join đồng hồ hoặc probe liên tục vẫn thiếu bằng chứng. Mọi lượt dừng, cleanup gốc và biên bản đối soát giữ riêng theo run.

## Bàn giao

Công việc là đối chiếu tài liệu và dữ liệu gốc ngoại tuyến, không sửa mã sản phẩm. Build, CI và merge mã sản phẩm không áp dụng cho bản nghiệm thu này. Claude đã tái tính độc lập bản trước và khớp số liệu. Bước tiếp là kiểm diff, SHA-256 của bản này và lưu protocol vào lịch sử Git theo quyền của Hoàng. Xem biên bản trong [ghi chú issue](../../delivery/milestones/R5-integration/pilot-and-war-game.md). Điều kiện G5 còn có bàn giao, snapshot và dataset manifest của ZER-25/ZER-55.
