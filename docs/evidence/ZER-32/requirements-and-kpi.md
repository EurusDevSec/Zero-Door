# ZER-32 — Ma trận yêu cầu và định nghĩa KPI

[Ghi chú issue và gói giao](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md) · Issue: [ZER-32](https://linear.app/zero-door/issue/ZER-32/lap-ma-tran-yeu-cau-va-djinh-nghia-kpi), cha [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia)

**Người soạn:** Claude, 18/10/2026, 21:43–22:03 +07:00. **Sửa gom** RV-01…RV-03 theo [Codex review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md): 18/10/2026, 22:20–22:32 +07:00.

**Chốt audit Codex:** tự sửa phần còn lại theo yêu cầu Hoàng ngày 18/10/2026; không chuyển thêm vòng Claude. Kết quả cuối ở [review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md).

**Trạng thái:** đây là bản định nghĩa và kiểm tra logic bằng dữ liệu giả định (SYNTHETIC/OFFLINE). Nó chưa phải kết quả thực nghiệm. Không hàng nào trong tài liệu này đã được chạy hoặc đã PASS trên lab.

**Thay đổi so với bản đầu (`afff4068…`).** Ba lỗi logic Codex tìm thấy, đều là lỗi định nghĩa chứ không phải quyết định phạm vi:
- **RV-01 (mục 3.7):** cận dưới uptime dùng độ dài **hợp** của khoảng chưa quan sát U với outage, và hợp U trên mọi luồng bắt buộc. Trước đây công thức cộng trùng và lấy max U của một luồng, có thể cho PASS sai.
- **RV-02 (mục 3.2, 3.4):** tách effect thành ba trạng thái. Chỉ NO_EFFECT có bằng chứng phủ đủ cửa sổ mới rời N. UNKNOWN_EFFECT ở lại N như lượt thiếu dữ liệu.
- **RV-03 (mục 3.4):** khi N = 0, tỷ lệ và mean không xác định; verdict là EMPTY hoặc NO_ELIGIBLE, không bao giờ PASS.

Ngưỡng 60 s, 120/180 s, 99,9% và các đề xuất D-01…D-05 giữ nguyên ý. Expected của mọi case cũ không đổi. Riêng đầu vào case F được bổ sung record đánh giá effect, vì quy tắc mới đòi bằng chứng mới cho rời N. Mục 5 thêm case cho từng lỗi.

**Baseline.** Lúc bắt đầu, Git Bash cho thấy:
- Nhánh `codex/zer-35-local-lab`, HEAD `a224ce54fc0e742bbb647c61e6e9201094a9de25`.
- Dirty đúng hai file do Codex soạn gói: `docs/delivery/NOW.md` (sha256 `b8594d45…e5f056`) và `scope-and-criteria.md` (sha256 `35fb2ded…df4e59`).
- Claude giữ nguyên hai thay đổi này, chỉ nối thêm phần của mình theo allowlist.

**AC.** Claude chưa đọc lại được AC sống.
- Connector Linear của phiên Claude trỏ tới workspace khác. Gói giao cấm dùng connector thay thế, nên Claude không gọi nó.
- Thay vào đó dùng snapshot: gói giao lúc 21:25, do Codex soạn sau khi đọc AC sống của ZER-32 và ZER-5 lúc khoảng 21:24 qua `linear_zero_door`.
- Gói giao không chép nguyên văn AC-01 ZER-32 hay AC-02 ZER-5. Vì vậy mục 8 đối chiếu với năm yêu cầu nội dung của gói giao và yêu cầu kiểm chứng R0-T01-S02. Codex đã đối chiếu AC sống ZER-32/AC-02 ZER-5 trong review; đọc lại ZER-32 lúc 22:39 +07 ngày 18/10 và không thấy thay đổi AC.

**DOCX.** Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX. Nguồn: [bản trích](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md), SHA-256 DOCX `0FAA8794…CD964`. Vị trí Pn là đoạn thứ n của `word/document.xml`, không phải số trang.

## 1. Loại nguồn dùng trong tài liệu

| Nhãn | Nghĩa | Ví dụ |
| --- | --- | --- |
| **SRC** | Câu chữ của thuyết minh DOCX (qua bản trích) | P107 “MTTD < 1 phút; MTTR < 2-3 phút” |
| **USER** | Xác nhận hiện hành của Hoàng ghi trong [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) | Python/Go + Online Boutique; giữ cả ba vector |
| **PLAN** | Quy tắc phương pháp đã có trong repo ([verification](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/verification.md), [research-design](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/research-design.md)); không phải câu chữ DOCX | MTTR từ detect; báo cả 120 s và 180 s; War Game 4h |
| **PROP** | Đề xuất của tài liệu này để operationalize; **cần chấp nhận**, không phải cam kết đã duyệt | Mẫu số CPU = limit; K = 3 mẫu xác nhận phục hồi |
| **UNKNOWN** | Chưa có nguồn; không suy thành PASS hay rỗng | Kỷ yếu nhận bài; thời lượng formal |

## 2. Ma trận yêu cầu → phép thử → bằng chứng

**Cách đọc bảng.**
- Cột “Downstream” liệt kê issue có trong [mapping Linear](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/mapping.json). Mapping ở trạng thái APPLIED_VERIFIED, read-back 17/10. Claude đã xác minh ID/tiêu đề theo mapping, **không đọc live**.
- “Phép thử” là mô tả cần chạy ở issue downstream. Mô tả ở đây không có nghĩa là đã chạy.
- ID `RM-xx` chỉ dùng để truy vết trong tài liệu, không tạo hệ issue mới.
- Bằng chứng runtime phải là dữ liệu mới, gắn `run_id`. Ghi chú Complete cũ, CSV legacy hay ảnh chụp dashboard cũ chỉ là provenance (xem [audit](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/audit-findings.md)).

| ID | Nguồn | Cam kết | Điều kiện / kịch bản cần thử | Expected và tiêu chí đạt | Bằng chứng cần lưu | Downstream | Giới hạn |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RM-01 | SRC P104; USER SCOPE “tối thiểu 5 microservices… không chỉ đủ số pod” | Cluster Kubernetes có ≥5 microservices mẫu có nghiệp vụ | Snapshot workload của namespace mục tiêu. Probe giao dịch mua hàng Boutique đầu-cuối chạy qua ingress | ≥5 Deployment khác nhau Ready **và** giao dịch mua hàng thành công với nội dung đúng. Có bằng chứng giao dịch đi qua ≥5 service | Manifest/revision; danh sách Deployment và Ready; log probe giao dịch (status, nội dung, latency); metric hoặc log request theo service | ZER-6 (AC R0-T02-S03), ZER-35, ZER-38 | Đếm pod hay API trả 200 không đủ. Bằng chứng “≥5 service nằm trên luồng” cần trace hoặc metric theo service: **UNKNOWN** lab hiện có tracing hay không |
| RM-02 | SRC P105, P177; USER 17/10 giữ cả ba vector | Nemesis tự động thực hiện SQLi, DDoS tầng ứng dụng, resource exhaustion | Mỗi vector được kích hoạt bởi Nemesis/harness, không có lệnh tay. Tiêu chí effect do issue vector khóa | Với từng vector: lượt có **effect** theo tiêu chí đã khóa. Báo số lượt yêu cầu, effect xác nhận, no-effect xác nhận và effect không xác định (mục 3.2). Tỷ lệ effect = effect xác nhận / lượt yêu cầu, kèm cận trên khi tính cả lượt không xác định. Attack requested không tự là effect (mục 3.3) | Log kế hoạch/lệnh phía điều khiển (tách khỏi evidence của bên chữa lỗi); bằng chứng effect độc lập; cleanup | ZER-13 (ZER-41, ZER-42), ZER-14 (ZER-43, ZER-44), ZER-15, ZER-19 | SQLi kiểm trên fixture riêng theo [scenario-design](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/scenario-design.md), không mô tả như lỗ hổng sẵn có của Boutique. Tiêu chí effect từng vector chưa khóa (F-05) |
| RM-03 | SRC P106, P184, P185 | Hephaestus tự động scale up/down | Case tải hoặc cạn tài nguyên trên workload mục tiêu; sau đó là cửa sổ tải thấp | Scale up: số replica Ready tăng, capacity tăng và probe cải thiện. Scale down: chỉ xảy ra sau cửa sổ tải thấp, không dao động. Quyền điều khiển với HPA phải được ghi rõ | Replica desired/ready theo thời gian; metric capacity; probe trước/sau; action timeline | ZER-16, ZER-18 | Lab có HPA `frontend`/`cartservice` (70% request CPU), nên phải quy đúng ai scale (mục 4, “tự hồi phục do Kubernetes”) |
| RM-04 | SRC P106, P184; USER 17/10 (chặn được nguồn thay vì phục hồi lặp mãi) | Block IP nguồn tấn công trong khi benign traffic vẫn hoạt động | Một nguồn tấn công và một client benign chạy đồng thời | Request từ nguồn bị chặn bị từ chối tại điểm thực thi tin cậy. Request success rate của benign giữ trong ngưỡng. Hiệu lực và TTL/cleanup còn đúng sau restart | Nguồn IP quan sát tại điểm tin cậy; log chặn/cho phép; request success rate benign (mục 3.7); trạng thái policy trước/sau TTL | ZER-17 (ZER-46) | Không chấp nhận IP mặc định hay việc tạo được policy làm bằng chứng. Ngưỡng benign chưa có nguồn (F-08) |
| RM-05 | SRC P106 | Rollback phiên bản lỗi | Deploy bản lỗi đã biết, có ground truth ở harness | Danh tính image/config/revision trở về bản known-good **và** probe phục hồi trong cửa sổ định trước | Revision/image digest trước/sau; probe; action timeline | ZER-17 (ZER-47) | Thay annotation riêng lẻ không đủ. Không rollback mọi 5xx |
| RM-06 | SRC P100 | Ba agent tự phát hiện, cô lập và phục hồi, không cần con người can thiệp | Đường thật: effect → detect → transport → action → probe, ở chế độ có tác tử | Mỗi incident có chuỗi sự kiện đủ mốc (mục 3.3). “Cô lập” được xác minh bằng containment (RM-04) hoặc hành động hạn chế tác động có hậu điều kiện đo được. Log thao tác người vận hành rỗng trong cửa sổ trial. Phục hồi được probe xác minh | Chuỗi event cùng `run_id`/`incident_id`; log thao tác người vận hành; probe | ZER-20 (ZER-49, ZER-50), ZER-21 (ZER-51), ZER-23 | Phục hồi nhờ controller Kubernetes vẫn là “tự động” ở mức hệ thống, nhưng phải gắn cờ attribution. Chỉ đối chứng B0 (ZER-39) mới cho biết đóng góp riêng của ZERO DOOR |
| RM-07 | SRC P107; PLAN verification #2–3 | MTTD < 1 phút | Mọi incident đủ điều kiện của formal run | Theo mục 3.4: báo mean MTTD và tỷ lệ lượt MTTD < 60 s trên N đủ điều kiện, kèm missed/missing | Event effect và detect có timestamp; bảng incident | ZER-37, ZER-38, ZER-10, ZER-53, ZER-59 | Verdict của mean cần chấp nhận (D-01). Rủi ro khả thi với scrape 30 s (mục 3.8, cuối) |
| RM-08 | SRC P107 “MTTR < 2-3 phút”; PLAN báo cả 120 và 180 s, thêm tỷ lệ phục hồi | MTTR < 2–3 phút; recovery được xác minh | Như RM-07 | Mean MTTR và tỷ lệ lượt < 120 s, < 180 s trên N, cùng phân loại RECOVERED/TIMEOUT/MISSING. Không chọn lại một ngưỡng sau khi có kết quả | Event detect; mốc RECOVERY_VERIFIED kèm mẫu probe làm căn cứ | ZER-37, ZER-38, ZER-10, ZER-53, ZER-59 | “2-3 phút” không khóa ngưỡng duy nhất. Tài liệu giữ cả hai, không giải quyết thay sự mơ hồ |
| RM-09 | PLAN verification #2 | Total recovery từ effect | Như RM-07 | Báo phân phối kèm số lượt | Như RM-07/08 | ZER-10, ZER-59 | Không có ngưỡng nguồn; chỉ báo cáo |
| RM-10 | SRC P108 | Uptime ≥ 99,9% dưới áp lực tấn công liên tục | Cửa sổ formal có tấn công, probe nghiệp vụ độc lập chạy liên tục | Theo mục 3.7: A_lower ≥ 0,999 thì PASS; A_upper < 0,999 thì FAIL; còn lại UNKNOWN. Request success rate báo riêng | Mọi mẫu probe thô (gồm lỗi); log heartbeat của probe; ranh giới cửa sổ | ZER-38, ZER-10, ZER-54 | Thời lượng formal chưa chốt; 4h chỉ là ví dụ kế hoạch repo (F-03) |
| RM-11 | SRC P109 | Dashboard Gaia hiển thị thời gian thực trạng thái tấn công/phòng thủ | Dashboard đọc cùng event store trong một run | Cùng `run_id` cho cùng KPI như bộ xuất dữ liệu. Có trạng thái “không có dữ liệu”. Đo được độ trễ cập nhật | Ảnh/video kèm `run_id`; độ trễ hiển thị so với timestamp event; so khớp KPI với export | ZER-11 | “Thời gian thực” chưa có ngưỡng độ trễ: **UNKNOWN**/F-09. Không dùng số ngẫu nhiên hoặc mô phỏng |
| RM-12 | SRC P176; P100 (Agent AI) | Tích hợp LLM sinh kịch bản tấn công; tác tử dùng LLM | Lượt gọi LLM thật qua adapter | Trace có model/version, prompt version, usage, latency. Kế hoạch sinh ra được kiểm hợp lệ với registry trước khi thực thi. Fallback được đánh dấu riêng | Log lượt gọi (không lộ bí mật); kết quả kiểm schema/registry | ZER-7 (ZER-36), ZER-19 (ZER-48), ZER-20 | Provider chưa chốt (ZER-36). Lượt fallback RULES không tính là lượt AI |
| RM-13 | SRC P179 | CPU target app tăng > 80% | Lượt vector tải hoặc cạn tài nguyên trên workload mục tiêu | Theo mục 3.8 (đề xuất D-03) | Chuỗi usage CPU theo container; limit/request theo pod; số replica | ZER-14 (ZER-44), ZER-10 | Mẫu số và thời lượng chưa có nguồn; đây là đề xuất |
| RM-14 | SRC P187 | Thời gian phản ứng < 1 phút | Mọi incident có detect | Theo mục 3.5 (đề xuất D-02). Không đồng nhất với MTTD hay MTTR | Event detect; trạng thái action theo thời gian | ZER-16, ZER-37, ZER-10 | Nguồn không khóa mốc đầu/cuối; cần chấp nhận |
| RM-15 | SRC P192, P195 | Chạy thử nghiệm và bảng số liệu MTTR/MTTD | Tái tính từ dataset formal | Bảng có N, mẫu số và phân loại failure. Mỗi số tái tạo được từ raw có hash | Dataset manifest/hash; script tái tính; bảng. Dataset được bàn giao như sản phẩm | ZER-24 (AC R5-T02-S04, ZER-53, ZER-54), ZER-59, ZER-25 (ZER-55), ZER-30 (ZER-63) | Tách legacy/pilot/formal |
| RM-16 | SRC P193, P210 | Video demo tấn công – tự phục hồi thực tế | Quay trên phiên bản đã chốt | Video ghép được với raw event cùng `run_id`, không dùng số mô phỏng | Video; `run_id`; phiên bản | ZER-30 (ZER-62), ZER-31 (ZER-65) | Demo không thay dữ liệu formal |
| RM-17 | SRC P198, P201, P211 | Báo cáo toàn văn và báo cáo khoa học chi tiết | Viết từ dữ liệu đã khóa | Báo cáo có chuỗi yêu cầu → sản phẩm → kết quả, kèm giới hạn và số chưa đạt | Word/PDF; liên kết tới dataset | ZER-30 (ZER-61), ZER-26, ZER-27, ZER-28 | — |
| RM-18 | SRC P203 | Slide thuyết trình, poster | Từ báo cáo đã chốt | Số liệu khớp báo cáo và dữ liệu | File slide/poster | ZER-30 (ZER-62) | — |
| RM-19 | SRC P208, P209; USER đổi stack sang Python/Go | Bộ mã nguồn và manifest/Helm | Đóng gói release | Có version/commit, manifest/Helm và hướng dẫn tái lập. Báo cáo ghi rõ đổi Java/Spring sang Python/Go đã được xác nhận | Gói release; hướng dẫn | ZER-30 (ZER-63) | P208 ghi Java Spring Boot. Không quay lại Java theo USER |
| RM-20 | USER SCOPE: bài được chấp nhận đăng trước nghiệm thu | Chấp nhận đăng trong kỷ yếu trường | Nộp bài vào đợt hợp lệ | Có xác nhận chấp nhận đăng. Nộp bài ≠ chấp nhận ≠ nghiệm thu | Biên nhận nộp; thư chấp nhận | ZER-26 (ZER-57), ZER-28, ZER-29, ZER-31 | Tên kỷ yếu, mẫu bài, lịch nhận bài: **UNKNOWN** |
| RM-21 | USER SCOPE: Python/Go, Google Online Boutique | Stack và hệ thống mục tiêu | Rà nghiệm thu | Báo cáo/paper nêu đúng lựa chọn đã được xác nhận | Báo cáo | ZER-5 (AC R0-T01-S01), ZER-30 (ZER-61) | — |
| RM-22 | PLAN verification #9 (bổ trợ P100/RM-04) | Cửa sổ bình thường: false alarm và false action | Tải lành tính, không có fault | Báo false alarm và false action trên mẫu số đã định nghĩa. Không hardcode 0 | Event detect/action trong cửa sổ không có fault; nhãn ground truth ở harness | ZER-10 (AC R1-T02-S03), ZER-8 | Mẫu số FPR do ZER-8/ZER-10 khóa; ZER-32 chỉ nêu yêu cầu |

Ngoài phạm vi ma trận KPI: chênh lệch thời gian DOCX (P55–P56, tháng 01–06/2026) với hạn 31/12/2026 thuộc ZER-33 và ZER-64. ZER-32 không truy vết thay source ledger.

## 3. Từ điển phép đo

### 3.1 Đơn vị, thời gian, đồng hồ

- **Đơn vị:** giây (s), lưu đến mili-giây. Phần trăm luôn có mẫu số ghi kèm.
- **Timestamp:** lưu UTC theo ISO-8601 với mili-giây. Báo cáo hiển thị +07:00.
- Mỗi event ghi đồng hồ của thành phần tạo ra nó (`ts_event`), tách khỏi thời điểm hệ thống lưu nhận (`ts_ingest`).
- **Clock source (PROP):**
  - Các container trong k3d cùng chạy trên một Docker host nên dùng chung đồng hồ kernel của host. Probe hoặc harness chạy ngoài host đó phải ghi độ lệch so với đồng hồ tham chiếu lúc bắt đầu và kết thúc trial.
  - Dung sai ε = 1 s. Hai mốc ngược thứ tự quá ε làm incident thành INVALID_CLOCK (mục 4).
  - Cách đo độ lệch cụ thể do ZER-38 chọn.
- **Ground truth:** harness giữ thời điểm attack requested/stopped, loại fault và tập hành động chấp nhận được. Bên chữa lỗi không đọc được ground truth (theo [research-design](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/research-design.md)).
- **Điều kiện hợp lệ của một mốc:** có `run_id` và `incident_id` (hoặc liên kết được qua `action_id`), có timestamp, không vi phạm thứ tự trong dung sai, và nguồn ghi đúng vai trò (bảng mục 3.3).

### 3.2 Trial, incident, cửa sổ đo

**Trial** là một lần phát lại một kế hoạch fault đã khóa dưới một cấu hình (B0/B1/B2/B3/BM), có `run_id` và `trial_id` riêng. Một trial đơn case chứa một incident. War Game chứa nhiều incident.

**Incident** là một lần fault được harness yêu cầu trên một mục tiêu, có `incident_id` trung tính.

**Trạng thái effect của incident.** Bộ đánh giá effect độc lập gán đúng một trong ba trạng thái:

| Trạng thái | Điều kiện | Vào mẫu số N của MTTD/MTTR/reaction? |
| --- | --- | --- |
| CONFIRMED | Có T_eff hợp lệ theo tiêu chí effect của vector | Có |
| CONFIRMED_NO_EFFECT | Có record NO_EFFECT của bộ đánh giá, **và** chuỗi bằng chứng (probe hoặc metric theo tiêu chí vector) phủ kín cửa sổ quan sát effect [T_req, T_req + W_eff]: mẫu đầu cách T_req không quá `gap`, mẫu cuối cách cuối cửa sổ không quá `gap`, giữa hai mẫu không quá `gap`, và không mẫu nào thỏa tiêu chí effect | **Không**; lưu kèm lý do |
| UNKNOWN_EFFECT | Mọi trường hợp còn lại: thiếu T_eff mà không có record NO_EFFECT; record NO_EFFECT nhưng bằng chứng có khoảng trống hoặc không có mẫu; record mâu thuẫn với mẫu | **Có**, như một lượt thiếu dữ liệu (MISSING): không có giá trị, không đạt, kéo verdict mean thành UNKNOWN |

- Thiếu mốc effect không chứng minh tấn công không có hiệu lực. Vì vậy chỉ CONFIRMED_NO_EFFECT được rời N, theo quy tắc khóa trước formal run.
- Không gán T_eff hay duration giả cho UNKNOWN_EFFECT, kể cả khi detector đã báo.
- W_eff là tham số theo vector, chốt cùng tiêu chí effect ở F-05.

**Incident đủ điều kiện** (mẫu số N) = mọi incident được yêu cầu trừ CONFIRMED_NO_EFFECT. Tức N = CONFIRMED + UNKNOWN_EFFECT.
- Mỗi tổng hợp báo bốn số: requested, CONFIRMED, CONFIRMED_NO_EFFECT, UNKNOWN_EFFECT.
- NO_EFFECT vẫn được lưu và vẫn tính vào tỷ lệ effect của vector (RM-02).
- Ngoài NO_EFFECT, incident chỉ bị loại khỏi N theo lý do đã ghi trong protocol trước formal run, và vẫn được lưu kèm lý do.

**Cửa sổ của một trial:**
- **Warm-up:** từ lúc khởi động đến khi probe đạt K mẫu liên tiếp trước fault đầu tiên. Không tính vào uptime. Thời lượng tối thiểu: F-02.
- **Cửa sổ đo W:** từ hết warm-up đến hết cửa sổ phục hồi của incident cuối cùng.
  - W **gồm mọi khoảng có tấn công và mọi outage**. Không bỏ outage trong lúc phục hồi.
  - Thời lượng formal: F-03. War Game 4h trong kế hoạch repo chỉ là ví dụ.
- **Trần chờ (PROP):**
  - Detect: `cap_det` = 300 s từ effect.
  - Recovery: `cap_rec` = 600 s từ effect.
  - Trần dài hơn ngưỡng để thấy phân phối vượt 180 s thay vì cắt ở ngưỡng. Hết trần thì là MISSED hoặc TIMEOUT.
- **Quy tắc duy trì tải (PROP, D-04):** giữ fault đến khi đã xác nhận đủ S, hoặc hết horizon quan sát T_eff + cap_rec + S. Ứng viên recovery vẫn phải có T_rec ≤ T_eff + cap_rec; phần S chỉ để xác minh, không gia hạn ngưỡng hay nhận ứng viên muộn. Protocol khóa horizon trước run. Nếu tải thực tế dừng sớm thì giữ T_stop thật và phân loại theo mục 3.4, không giả là tải vẫn còn.

### 3.3 Mốc sự kiện và trạng thái

| Mốc | Ký hiệu | Nguồn ghi | Ghi chú |
| --- | --- | --- | --- |
| attack_requested | T_req | Harness/Nemesis (phía điều khiển) | Không tự là effect |
| attack_effect_started | T_eff | Bộ đánh giá độc lập theo tiêu chí effect của vector: probe hoặc metric/log mục tiêu do ZER-13/ZER-14 khóa | Với vector làm hỏng nghiệp vụ: PROP lấy mẫu probe lỗi đầu tiên sau T_req. Không lấy từ detector |
| effect_evaluation | — | Cùng bộ đánh giá effect | Một record cho mỗi incident: trạng thái effect, phiên bản tiêu chí, W_eff và tham chiếu bằng chứng. Event T_eff hợp lệ do bộ đánh giá độc lập phát cũng là record CONFIRMED. Thiếu cả record kết luận và T_eff có nguồn hợp lệ thì là UNKNOWN_EFFECT |
| detected | T_det | Detector Gaia, ghi tại thời điểm quyết định | Không lấy từ heal history hay việc replica tăng. Alert đã firing trước T_req − ε không thuộc incident này |
| published / consumed | T_pub, T_con | Producer / consumer Kafka | Chỉ dùng phân rã độ trễ và kiểm thứ tự |
| heal_started | T_hs | Healer | Mốc bắt đầu thực thi action |
| API_ACCEPTED | T_api | Healer, khi API đích nhận lệnh | **Không** là hoàn tất, cũng không là phục hồi |
| ACTION_COMPLETED | T_ac + trạng thái SUCCESS / FAILED / PARTIAL / TIMEOUT | Healer, sau khi kiểm hậu điều kiện của action | Ví dụ: replica Ready, revision đổi, policy có hiệu lực. SUCCESS **không** là phục hồi |
| RECOVERY_VERIFIED | T_rec | Bộ đánh giá probe độc lập, ngoài luồng healer (ZER-38) | Định nghĩa ở mục 3.4 |
| attack_stopped | T_stop | Harness | Không tự là recovery |

### 3.4 MTTD, MTTR, total recovery và tổng hợp

**Mốc phục hồi T_rec (PROP, D-04).** Đánh giá trên probe nghiệp vụ của luồng bị ảnh hưởng, với chu kỳ Δ:
1. Tìm sau T_eff, và chỉ sau khi probe đã ghi nhận lỗi của incident.
2. Xác nhận phục hồi khi có **K mẫu đạt liên tiếp**. Mẫu đạt = đúng nội dung + latency ≤ L. Giữa hai mẫu liên tiếp không có khoảng trống quá `gap`.
3. T_rec là thời điểm của mẫu đạt thứ K. Đây là mốc bảo thủ, không lùi về mẫu đạt đầu tiên.
4. Sau T_rec phải có cửa sổ ổn định S không có mẫu lỗi và không có khoảng trống vượt `gap`. Nếu có mẫu lỗi trong S thì là RELAPSE: hủy mốc và tìm tiếp. Nếu thiếu dữ liệu trong S thì không xác nhận được.
5. Trần `cap_rec` giới hạn **mốc ứng viên T_rec**, không cắt mất bằng chứng ổn định sau mốc đó. Thu probe tới ít nhất T_eff + cap_rec + S; ứng viên đúng trần được xét, ứng viên sau trần không được xét. Ghi riêng `recovery_verified_at = T_rec + S` (mốc đủ bằng chứng; thời điểm nhận event có thể muộn hơn), không đổi T_rec hay MTTR bằng thời điểm nhận. Không phát RECOVERY_VERIFIED trước khi đủ bằng chứng.
6. Để được tính là phục hồi trong lúc tải còn duy trì, T_stop phải không sớm hơn `recovery_verified_at`. Nếu dừng tải giữa T_rec và hết S thì RECOVERED_AFTER_STOP, không tính đạt ngưỡng. Nếu không đủ quan sát S thì MISSING_PROBE, không suy TIMEOUT hay PASS.

Tiêu chí recovery phải là phủ định của tiêu chí effect, đo bằng cùng probe. Với vector không làm hỏng luồng mua hàng (SQLi trên fixture), recovery là **containment đã xác minh**:
- Request mới từ nguồn bị chặn tại điểm thực thi tin cậy.
- Probe benign của fixture và của Boutique vẫn đạt.

Hai luồng này báo riêng, không gộp.

**Theo từng incident i:**
- `MTTD_i = T_det − T_eff`.
  - Nếu T_req − ε ≤ T_det < T_eff thì gắn cờ EARLY_DETECT và ghi `MTTD_i = 0`. Detector thấy dấu hiệu trước khi probe xác nhận effect; giá trị âm không được đưa vào mean.
  - Không detect trong `cap_det` thì MISSED. Giá trị không quan sát được; không điền 0 hay trần.
- `MTTR_i = T_rec − T_det`, chỉ xác định khi có cả hai mốc **và** T_rec ≥ T_det.
- `TotalRecovery_i = T_rec − T_eff`.

**Phân loại phục hồi** (mỗi incident đúng một nhãn):

| Nhãn | Điều kiện | Tính “đạt” MTTR < θ? |
| --- | --- | --- |
| RECOVERED | Có T_det, T_rec ≥ T_det và recovery_verified_at ≤ T_stop (nếu có T_stop) | Có, nếu MTTR_i < θ. Gắn thêm cờ `NO_ACTION_BEFORE_RECOVERY` khi không có ACTION_COMPLETED=SUCCESS nào trước T_rec |
| RECOVERED_AFTER_STOP | T_stop trước recovery_verified_at, kể cả khi T_rec ≤ T_stop | **Không** (PROP, D-04); báo riêng kèm giá trị |
| RECOVERED_BEFORE_DETECT | T_rec < T_det | Không; MTTR không xác định. Báo total recovery (D-04) |
| RECOVERED_UNDETECTED | Không detect, có T_rec | Không; báo total recovery |
| TIMEOUT | Probe phủ đủ tới `cap_rec`, không có T_rec | Không; censored tại `cap_rec` |
| MISSING_PROBE | Không có T_rec và có khoảng trống probe | Không; UNKNOWN, báo riêng |
| MISSING | INVALID_CLOCK, thiếu correlation hoặc thiếu mốc bắt buộc | Không; UNKNOWN, báo riêng |
| UNKNOWN_EFFECT | Trạng thái effect không xác định (mục 3.2). MTTD, MTTR, total và reaction đều MISSING | Không; UNKNOWN, báo riêng |

**Tổng hợp trên tập N incident đủ điều kiện** (mục 3.2; mỗi tổng hợp ghi rõ mẫu số):
- Luôn báo requested, CONFIRMED, CONFIRMED_NO_EFFECT, UNKNOWN_EFFECT và N.
- Tỷ lệ đạt MTTD < 60 s = #{DETECTED và MTTD_i < 60} / N.
- Tỷ lệ đạt MTTR < 120 s và tỷ lệ đạt MTTR < 180 s = #{RECOVERED và MTTR_i < θ} / N. Luôn báo **cả hai**.
- Báo thêm khoảng ảnh hưởng của dữ liệu thiếu: [đạt / N, (đạt + thiếu) / N]. “Thiếu” gồm MISSING, MISSING_PROBE và UNKNOWN_EFFECT (với MTTD: lượt detect MISSING, gồm cả INVALID_CLOCK và UNKNOWN_EFFECT).
  - Khoảng này phủ cả hai khả năng của lượt UNKNOWN_EFFECT: thật ra có effect (ở lại N) hoặc thật ra không effect (rời N). Vì đạt ≤ CONFIRMED, tỷ lệ tính riêng trên CONFIRMED luôn nằm trong khoảng.
- Tỷ lệ phục hồi được xác minh (PLAN) = #{RECOVERED, RECOVERED_AFTER_STOP, RECOVERED_BEFORE_DETECT, RECOVERED_UNDETECTED} / N. Báo kèm số lượng từng nhãn.
- Mean/median/phân phối MTTR chỉ tính trên các lượt RECOVERED. Luôn báo cạnh tỷ lệ và số lượng từng nhãn.
- Không thay N bằng số lượt có dữ liệu. Không dùng mean để che lượt không phục hồi.

**Khi N = 0** (cùng quy tắc cho MTTD, MTTR và reaction):

| Tình huống | Trạng thái tổng hợp | Tỷ lệ, mean | Verdict |
| --- | --- | --- | --- |
| Dataset không có incident nào được yêu cầu | EMPTY | Không xác định (không phải 0/0 = 0 hay 100%) | **EMPTY** |
| Có incident được yêu cầu, tất cả CONFIRMED_NO_EFFECT | NO_ELIGIBLE | Không xác định | **NO_ELIGIBLE** |

- Cả hai đều **không phải PASS**. Vẫn xuất số requested/no-effect/unknown để thấy vì sao rỗng.
- Toàn bộ là UNKNOWN_EFFECT **không** phải N = 0: N bằng số lượt đó, không lượt nào đạt, khoảng ảnh hưởng là [0, 1], verdict UNKNOWN.
- Với P107, run NO_ELIGIBLE nghĩa là kịch bản chưa tạo được effect. Đó là vấn đề của kịch bản (RM-02), không phải bằng chứng MTTD/MTTR đạt.

**Mean hay tỷ lệ là KPI chính.** P107 dùng tên MTTD/MTTR (Mean Time…), nên đọc theo câu chữ thì KPI nguồn là **mean**. Verification bắt buộc báo thêm tỷ lệ từng lượt. Nguồn không quy định tỷ lệ đạt tối thiểu, và tài liệu này **không đặt** con số đó.

Verdict đề xuất cho mean (PROP, D-01):

| Dữ liệu trong N | Verdict |
| --- | --- |
| N = 0 | **EMPTY** hoặc **NO_ELIGIBLE** (bảng trên); không có mean |
| Có lượt MISSING/MISSING_PROBE/UNKNOWN_EFFECT (hoặc detect MISSING) | **UNKNOWN**; mean của lượt quan sát được chỉ là mô tả |
| Không có lượt thiếu dữ liệu, nhưng có lượt không quan sát được giá trị (TIMEOUT, MISSED, RECOVERED_*) | **NOT_PASS**; mean trên toàn N không xác định, không được tuyên bố đạt |
| Mọi lượt quan sát được | PASS nếu mean < θ, ngược lại FAIL |

Dấu `<` là nghiêm ngặt: đúng 60,000 s, 120,000 s hay 180,000 s là **không đạt** ngưỡng tương ứng. Độ phân giải thời gian của MTTR bị giới hạn bởi Δ và K. Phải báo Δ cùng kết quả.

### 3.5 Thời gian phản ứng P187 (PROP, D-02)

P187 nằm trong mục tháng 04 cho Hephaestus (scale, block). Nguồn không khóa mốc đầu và mốc cuối.

**Đề xuất:** `Reaction_i = T_ac(SUCCESS, đầu tiên, ≥ T_det) − T_det`, tức từ detect đến action phòng thủ đầu tiên hoàn tất với hậu điều kiện thỏa.
- **Khác MTTD:** MTTD đo từ effect đến detect.
- **Khác MTTR:** MTTR cần probe xác minh nghiệp vụ.
- API_ACCEPTED hoặc ACTION_COMPLETED=FAILED/PARTIAL không đóng reaction. Không có SUCCESS trong `cap_rec` (tính từ T_eff) thì censored, không đạt.
- Trạng thái theo lượt: REACTED (có giá trị); NO_SUCCESS (censored); NO_DETECT (không detect nên reaction không xác định, không đạt); MISSING (INVALID_CLOCK, UNKNOWN_EFFECT).
- Báo thêm phân rã T_con − T_det (transport) và T_hs − T_con (quyết định) để thấy độ trễ nằm ở đâu.
- Tổng hợp giống MTTD, trên cùng N của mục 3.2: tỷ lệ < 60 s, khoảng ảnh hưởng của MISSING, mean và verdict theo D-01. NO_SUCCESS và NO_DETECT là lượt không quan sát được giá trị (NOT_PASS nếu không có lượt thiếu). N = 0 theo bảng ở mục 3.4.

Phương án thay thế cần Hoàng chọn nếu không chấp nhận đề xuất: đo từ T_eff. Khi đó Reaction bao gồm cả MTTD.

### 3.6 Tham số đề xuất (PROP, chốt trước formal run, F-01)

| Tham số | Giá trị đề xuất | Lý do |
| --- | --- | --- |
| Chu kỳ probe Δ | 1 s | Budget 14,4 s cho 4h (mục 3.7). Scrape Prometheus 30 s quá thô để đo uptime |
| Khoảng trống tối đa `gap` | 2Δ = 2 s | Cho phép trễ một mẫu; lớn hơn thì coi là chưa quan sát |
| K (xác nhận phục hồi, đóng outage) | 3 mẫu | Tránh nhiễu một mẫu. T_rec chậm thêm tối đa (K−1)Δ = 2 s, được ghi là sai số bảo thủ |
| Cửa sổ ổn định S | 30 s | Phát hiện relapse ngay sau phục hồi |
| Latency L cho mỗi giao dịch probe; timeout probe | **UNKNOWN**. Gợi ý ban đầu 2 s, cần pilot | Rule cảnh báo hiện có dùng p99 > 1 s. Chưa có số đo giao dịch trên lab |
| ε (lệch đồng hồ) | 1 s | Cùng bậc với Δ |
| `cap_det`, `cap_rec` | 300 s, 600 s | Gấp ≥ 2,5 lần ngưỡng để thấy phân phối |
| Cửa sổ quan sát effect W_eff | Theo vector (F-05); bộ kiểm dùng 300 s | Cần đủ dài để xác nhận NO_EFFECT, không chỉ vài mẫu sau T_req |

### 3.7 Uptime, downtime, request success rate

**Đầu vào hợp lệ.** Phải có tập luồng bắt buộc được khai báo và cửa sổ W có độ dài dương. Thiếu cấu hình luồng → NO_REQUIRED_FLOWS; cửa sổ bằng 0 hoặc âm → INVALID_WINDOW. Các đại lượng availability/downtime không xác định, verdict UNKNOWN, không chia 0 hay trả PASS. Một luồng đã khai báo nhưng không có mẫu là trường hợp khác: U = W, A_lower = 0, A_upper = 1, UNKNOWN.

**Mẫu probe.** Một mẫu là một lần chạy giao dịch nghiệp vụ đã định, bắt đầu tại t_i.
- Mẫu đạt khi mọi bước trả đúng status, **đúng nội dung** (ví dụ xác nhận đơn hàng) và tổng latency ≤ L.
- Timeout, lỗi kết nối, sai nội dung hoặc chậm hơn L đều là mẫu lỗi.
- Scrape `up`, `/healthz`, Pod Ready hay API trả 200 **không** là bằng chứng uptime.

**Outage.**
- Mở tại mẫu lỗi đầu tiên.
- Đóng tại mẫu đạt đầu tiên của chuỗi K mẫu đạt liên tiếp.
- Mẫu đạt lẻ giữa các mẫu lỗi vẫn thuộc outage.

**Mọi đại lượng dưới đây là tập khoảng thời gian nửa mở [a, b)**, cắt theo W. Độ dài |·| luôn lấy trên **hợp** các khoảng, không cộng độ dài từng phần.

**Chưa quan sát U_f của luồng f.** Gồm:
- [đầu W, mẫu đầu tiên);
- [mẫu trước + Δ, mẫu kế tiếp) khi hai mẫu liên tiếp cách nhau quá `gap`;
- [mẫu cuối + Δ, cuối W).

Trong U_f, trạng thái của luồng f không biết: không tính là up, cũng không tính là down chắc chắn.

**Outage của luồng f.**
- Mở tại mẫu lỗi đầu tiên. Đóng tại mẫu đạt đầu tiên của chuỗi K mẫu đạt liên tiếp (chuỗi không vắt qua khoảng trống). Mẫu đạt lẻ giữa các mẫu lỗi vẫn thuộc outage.
- Outage chưa đóng đến cuối W (kể cả khi probe ngừng giữa outage) được cắt tại cuối W. Phần sau mẫu cuối đã nằm trong U_f.
- Ba khoảng cho mỗi outage: `point` = [mẫu lỗi đầu, mẫu đạt đóng); `min` = [mẫu lỗi đầu, mẫu lỗi cuối); `max` = [mẫu đạt liền trước, mẫu đạt đóng), hoặc từ đầu W nếu không có mẫu đạt trước. Thời điểm bắt đầu thật nằm trong `max`.

**Hệ thống nhiều luồng bắt buộc.** Hệ thống down khi bất kỳ luồng nào down. Với tập luồng bắt buộc F:
- `U = ∪_f U_f`: chỉ cần một luồng chưa quan sát là trạng thái hệ thống có thể là down.
- `D_point = |∪_f (point_f \ U_f)|`: downtime đã quan sát. Phần U nằm trong outage không được đếm là down chắc chắn.
- `D_min = |∪_f (min_f \ U_f)|`: downtime chắc chắn tối thiểu. Downtime đã quan sát ở luồng A không bị xóa vì luồng B chưa quan sát.
- `D_lower = |∪_f max_f ∪ U|`: downtime xấu nhất. Phần U chồng lên outage chỉ đếm một lần.

**Time-based availability:**
- `A_lower = 1 − D_lower/|W|`: cận dưới, coi mọi khoảng chưa quan sát là down.
- `A_upper = 1 − D_min/|W|`: cận trên, coi U là up và outage ngắn nhất có thể.
- `A_point = 1 − D_point/|W|`: chỉ mô tả phần đã quan sát, luôn báo cùng |U|. Không dùng để kết luận.
- Mẫu số luôn là |W|, không phải phần thời gian có dữ liệu. Luôn có 0 ≤ A_lower ≤ A_point ≤ A_upper ≤ 1.

**Verdict (PROP, D-05):** PASS khi A_lower ≥ 0,999; FAIL khi A_upper < 0,999; còn lại UNKNOWN. Thiếu probe phải đi vào U, không tự được tính up. Vẫn có thể PASS nếu cận dưới sau khi tính toàn bộ U đạt ngưỡng (ví dụ U7); U riêng lẻ không được coi là downtime chắc chắn để kết luận FAIL.

**Giả định của ước lượng từ probe rời rạc.** Hai cận trên là cận **theo mô hình lấy mẫu**, không phải chứng minh:
- Giữa hai mẫu đạt liên tiếp cách nhau ≤ `gap`, hệ thống được coi là up. Outage ngắn hơn khoảng cách mẫu có thể lọt qua mà không thấy.
- Vì vậy kết quả uptime phải báo kèm Δ, `gap`, K và số mẫu thực tế. Δ càng lớn thì PASS càng yếu.
- Request success rate của client benign (bên dưới) là bằng chứng bổ trợ cho các khoảng giữa mẫu probe.

**Budget ví dụ.** |W| = 4h = 14.400 s, nên downtime cho phép = 14.400 × 0,1% = **14,4 s**. 4h là ví dụ War Game trong kế hoạch repo (ZER-54), chưa phải thời lượng formal đã chốt (F-03).

**Luồng P108 (PROP, F-04).** Luồng mua hàng Boutique là luồng P108. Probe fixture SQLi báo riêng, không gộp để che luồng lỗi.

**Request success rate** = request benign đạt (cùng tiêu chí nội dung/latency) / tổng request benign trong W. Đây là đại lượng khác với availability theo thời gian: lưu lượng dày trong lúc tốt có thể che khoảng thời gian lỗi. Báo cả hai.

### 3.8 CPU target app > 80% (P179; PROP, D-03)

**Nguồn chỉ nói:** “KPI: CPU target app tăng > 80%”, trong mục tháng 03 cho Nemesis. Đây là KPI hiệu lực của tấn công tải/tài nguyên, không phải KPI phục hồi.

**Đề xuất operationalize:**
- **Target:** container ứng dụng của Deployment bị nhắm trong namespace mục tiêu. Không lấy CPU toàn node, CPU của pod stress riêng, hay mức tăng tương đối so với baseline.
- **Đại lượng:** tốc độ dùng CPU (core) từ counter `container_cpu_usage_seconds_total`, lấy theo cửa sổ rate w.
- **Mẫu số:** **CPU limit**. Nếu limit thiếu/bằng 0 hoặc thiếu usage thì UNKNOWN; không thay bằng request hay chia 0. Tổng usage và limit phải thuộc cùng tập container ứng dụng, cùng thời điểm; loại sidecar và không điền 0 cho metric thiếu. Lý do: limit là trần thực tế trước khi bị throttling, nên >80% limit nghĩa là gần bão hòa. Lab cho thấy mẫu số đổi kết quả rất mạnh:
  - Manifest repo (đọc cấu hình, không phải runtime): `frontend` request 50m, limit 200m; HPA đặt 70% **request**.
  - Cùng mức dùng 320m trên 2 pod: 80% limit, 320% request, khoảng 8% của 4 core máy.
  - Phần trăm theo request vượt 80% ở tải rất nhẹ, nên không phân biệt được tấn công.
- **Aggregation:** tỷ lệ của tổng trên Deployment, `Σ_pods usage / Σ_pods limit`, theo các pod đang chạy ở mỗi lần đánh giá. Báo thêm max theo pod.
  - Khi đã scale out, tỷ lệ giảm vì tổng limit tăng (ví dụ 322m/600m ≈ 53,7%).
  - KPI P179 đo trước khi phòng thủ có tác dụng, hoặc trong B0 nếu protocol chọn vậy (F-06).
- **Ngưỡng:** > 80% (nghiêm ngặt), duy trì liên tục ≥ 60 s. Với bước đánh giá 30 s, tức ≥ 3 lần đánh giá liên tiếp.
- **Kết quả theo lượt:** đạt / không đạt / UNKNOWN (thiếu chuỗi metric). Tổng hợp = số lượt đạt / số lượt có effect của vector.

**Điểm cần chốt trước thực nghiệm (F-06):**
- Rate window w. Scrape hiện là 30 s, nên `rate[1m]` chỉ có khoảng 2 mẫu. Đề xuất w ≥ 2m, hoặc giảm scrape cho target, do ZER-38/ZER-44 quyết định.
- Thời lượng duy trì.
- Pha đo của P179.

**Gap ghi nhận (không sửa ở ZER-32):**
- Rule `HighCPUUsage` trong `infrastructure/manifests/prometheus-rules.yaml` dùng ngưỡng tuyệt đối 0,16 core cho mọi container, `for: 30s`. Đó là 80% của limit 200m, nhưng không phải 80% với container có limit khác. Ghi cho ZER-44/ZER-49 khi định nghĩa detector.
- **Rủi ro khả thi MTTD:** cảnh báo Prometheus có trễ cộng dồn. Scrape 30 s + `for` + chu kỳ đánh giá 30 s có thể chiếm phần lớn hoặc vượt 60 s. Điều này không đổi định nghĩa MTTD, nhưng ZER-38/ZER-49 cần đo pilot.

## 4. Quy tắc dữ liệu và tình huống biên

Mọi lượt bị loại hoặc gắn nhãn đều được lưu cùng lý do. Thiếu nguồn thì là UNKNOWN, không phải PASS hay rỗng.

| Tình huống | Quy tắc | Mẫu số / censoring |
| --- | --- | --- |
| Event trùng | Khử trùng theo `event_id`, giữ bản đầu. Cùng `event_id` mà khác payload thì INTEGRITY_ERROR, incident thành MISSING | Ở lại N |
| Event đến sai thứ tự | Sắp theo `ts_event`, không theo thứ tự nhận. Thứ tự Kafka không phải căn cứ thời gian | — |
| Thiếu correlation ID | Event không gắn được vào incident thì là ORPHAN: lưu, không dùng. Incident thiếu mốc bắt buộc vì vậy thì MISSING | Ở lại N |
| Thiếu timestamp | Không suy từ `ts_ingest` hay thứ tự. Mốc đó MISSING | Ở lại N |
| Lệch đồng hồ hoặc duration âm | Chuỗi T_det ≤ T_pub ≤ T_con ≤ T_hs và T_api ≤ T_ac phải đúng trong ±ε. Vi phạm thì INVALID_CLOCK, mọi duration của incident là MISSING. Âm do detect sớm (T_req − ε ≤ T_det < T_eff) thì EARLY_DETECT, MTTD = 0 có cờ | Ở lại N |
| Nhiều action cho một incident | Lưu tất cả. Reaction dùng SUCCESS đầu tiên. MTTR không phụ thuộc số action. Ghi số action và action thừa | — |
| Incident chồng lấn | PROP: protocol giãn incident cùng mục tiêu ≥ `cap_rec` + S. Nếu vẫn chồng mà không gán được detect/recovery duy nhất thì cả hai thành MISSING (AMBIGUOUS). Uptime dùng hợp outage | Ở lại N |
| Thiếu detect | MISSED, censored tại `cap_det`. MTTR không xác định. Total recovery vẫn tính nếu có T_rec | Ở lại N, không đạt |
| Thiếu recovery hoặc timeout | Probe phủ đủ thì TIMEOUT, censored tại `cap_rec`. Probe có khoảng trống thì MISSING_PROBE | Ở lại N, không đạt |
| Attack không có effect, đã xác nhận | CONFIRMED_NO_EFFECT: record NO_EFFECT và bằng chứng phủ kín W_eff (mục 3.2). Loại khỏi N của MTTD/MTTR/reaction. Tính vào tỷ lệ effect của vector | Ra khỏi N, có lý do |
| Effect không xác định | Thiếu T_eff mà không có record NO_EFFECT, hoặc bằng chứng effect có khoảng trống, hoặc mất probe toàn cửa sổ effect: UNKNOWN_EFFECT. Không gán T_eff giả, kể cả khi detector đã báo | Ở lại N, không đạt, verdict UNKNOWN |
| Không có lượt đủ điều kiện (N = 0) | EMPTY nếu không có incident nào; NO_ELIGIBLE nếu mọi incident là CONFIRMED_NO_EFFECT. Tỷ lệ và mean không xác định | Không PASS (mục 3.4) |
| Action SUCCESS nhưng probe vẫn lỗi | Không có RECOVERY_VERIFIED. Kết thúc là TIMEOUT hoặc MISSING_PROBE | Ở lại N, không đạt |
| Tự hồi phục do Kubernetes | Recovery trước mọi ACTION_COMPLETED=SUCCESS thì RECOVERED kèm cờ `NO_ACTION_BEFORE_RECOVERY` (MTTR mức hệ thống). Recovery trước detect thì RECOVERED_BEFORE_DETECT. Đóng góp của ZERO DOOR chỉ kết luận qua B0 | Ở lại N |
| Recovery sau khi attack dừng | RECOVERED_AFTER_STOP, không đạt ngưỡng (D-04) | Ở lại N |
| Probe mất dữ liệu | Khoảng trống quá `gap` là U, không phải up và không phải down chắc chắn. U hợp trên mọi luồng bắt buộc và hợp với outage trước khi tính cận dưới (mục 3.7). Chuỗi K mẫu không được vắt qua khoảng trống. MTTR quan sát được sau khoảng trống là cận trên (gắn cờ PROBE_GAP) | Ở lại N |
| Thiếu chuỗi metric CPU | Lượt P179 là UNKNOWN | Ở lại mẫu số P179 |

## 5. Kiểm bằng tình huống giả định (SYNTHETIC/OFFLINE)

**Thực hiện.** Script `R:/_Projects/Eurus_Workspace/zero_door/scratch/zer32/kpi_check.py` hiện thực đúng các quy tắc của mục 3–4.
- `scratch/` bị Git bỏ qua, nên script không track.
- Hash script và output ghi trong bàn giao. Bản đầu được giữ ở `scratch/zer32/v1/kpi_check.py` để đối chiếu.
- Lệnh chạy: `python scratch/zer32/kpi_check.py`; mutant: `python scratch/zer32/mutate.py`. Chạy từ gốc repo.
- Expected được tính tay và ghi vào script **trước** lần chạy. Các bảng dưới ghi đủ đầu vào, expected và actual để tái lập khi không có scratch.
- Tham số: Δ = 1 s, K = 3, S = 30 s, gap = 2 s, caps 300/600 s, ε = 1 s.
- Các mẫu probe trong case có chu kỳ 1 s. Thời gian tính từ effect, trừ khi ghi khác.

**Kết quả cuối Codex: 190/190 phép so khớp đạt, exit 0; 18/18 mutant bị bắt bằng assertion, không crash.** Bản Claude v2 có 177 phép kiểm (112 dòng cũ giữ nguyên); Codex thêm 13 kiểm cho đầu vào availability và biên xác nhận ổn định. Đây không phải dữ liệu lab/runtime.

### 5.1 Từng incident

| Case | Đầu vào chính (s) | Phép tính expected | Actual | Kiểm điều gì |
| --- | --- | --- | --- | --- |
| A | req 4, eff 5, det 35, pub 35,2, con 35,4, hs 36, api 36,5, ac 50 SUCCESS; probe lỗi 6–88, đạt từ 89 | MTTD = 35−5 = 30; T_rec = mẫu thứ 3 = 91; MTTR = 91−35 = 56; total = 86; reaction = 50−35 = 15 | Khớp, RECOVERED | Timeline đầy đủ |
| B1 | eff 0, det 60,000; đạt từ 178 | MTTD = 60,000 → không < 60; T_rec = 180; MTTR = 120,000 → không < 120, có < 180 | Khớp | Biên 60/120 |
| B2 | det 59,999; mẫu tại x,999; đạt từ 237,999 | MTTD = 59,999 đạt; T_rec = 239,999; MTTR = 180,000 → không < 180 | Khớp | Biên 180 |
| B3 | det 10; đạt từ 127,999 | T_rec = 129,999; MTTR = 119,999 → đạt < 120 | Khớp | Ngay dưới biên |
| C | det 20; action FAILED; probe lỗi tới hết trần | Không T_rec; probe phủ đủ, nên TIMEOUT; reaction censored | TIMEOUT | Timeout, không recovery |
| D | det 20; action **SUCCESS** tại 40; probe lỗi tới hết trần | Reaction = 20; vẫn TIMEOUT | Khớp | Action thành công nhưng nghiệp vụ lỗi |
| E | det 15; lỗi 1–50; **không có mẫu** 51–99; đạt từ 100 | Chuỗi không vắt qua khoảng trống; T_rec = 102; MTTR = 87 (cận trên, cờ PROBE_GAP) | Khớp | Missing probe có phục hồi |
| E2 | det 15; lỗi 1–50; sau đó mất probe | Không T_rec, có khoảng trống, nên MISSING_PROBE (không phải TIMEOUT) | Khớp | Missing probe không phục hồi |
| F | req 0; không T_eff; record NO_EFFECT, probe đạt mỗi 1 s từ 0 đến 300 (phủ kín W_eff = 300 s) | CONFIRMED_NO_EFFECT, ra khỏi N | Khớp | No-effect đã xác nhận |
| G | req 5, eff 10, **det 8**; lỗi 11–40, đạt từ 41; ac 60 | EARLY_DETECT, MTTD = 0; T_rec = 43; MTTR = 43−8 = 35; total = 33; cờ NO_ACTION_BEFORE_RECOVERY | Khớp | Detect sớm; tự hồi phục trước action |
| H | det 30, **stop 150**; đạt từ 158 | T_rec = 160 > stop; RECOVERED_AFTER_STOP; MTTR 130 không tính đạt | Khớp | Recovery sau khi dừng tấn công |
| I | det 20, pub 20,1, **con 14** | con < pub − ε, nên INVALID_CLOCK; MTTD/MTTR là MISSING | Khớp | Đồng hồ lệch |
| J | det 50; lỗi 1–27, đạt từ 28 | T_rec = 30 < det; RECOVERED_BEFORE_DETECT; total = 30 | Khớp | Hồi phục trước detect |
| K | det 10; lỗi 1–20, đạt 21–29, **lỗi lại 30–40**, đạt từ 41 | Các xác nhận 23/26/29 bị relapse trong S; T_rec = 43; MTTR = 33 | Khớp | Relapse |
| M | Không detect; lỗi 1–47, đạt từ 48 | MISSED; RECOVERED_UNDETECTED; total = 50 | Khớp | Thiếu detect |

### 5.2 Tổng hợp trên A–M

N = 14 (F loại vì CONFIRMED_NO_EFFECT).

| Đại lượng | Expected | Actual |
| --- | --- | --- |
| requested / CONFIRMED / CONFIRMED_NO_EFFECT / UNKNOWN_EFFECT | 15 / 14 / 1 / 0 | Khớp |
| Lượt MTTD < 60 s | 11/14 (B1 = 60 không đạt; I missing; M missed) | 11/14 |
| Khoảng ảnh hưởng MTTD < 60 s | [11/14, 12/14] = [0,786; 0,857] (thiếu: I) | Khớp |
| Khoảng ảnh hưởng MTTR < 120 s / < 180 s | [5/14, 7/14] / [6/14, 8/14] (thiếu: I, E2) | Khớp |
| Reaction < 60 s | 11/14; C là NO_SUCCESS, M là NO_DETECT, I là MISSING | Khớp |
| Mean reaction trên 11 lượt REACTED | 180,001/11 = 16,364 s; verdict **UNKNOWN** vì có I | Khớp |
| Lượt MTTR < 120 s | 5/14 (A, B3, E, G, K) | 5/14 |
| Lượt MTTR < 180 s | 6/14 (thêm B1; B2 = 180 và H after-stop không đạt) | 6/14 |
| Nhãn phục hồi | RECOVERED 7, AFTER_STOP 1, BEFORE_DETECT 1, UNDETECTED 1, TIMEOUT 2, MISSING_PROBE 1, MISSING 1 | Khớp |
| Mean MTTD trên 12 lượt detect | 319,999/12 = 26,667 s; verdict **UNKNOWN** vì có I | Khớp |
| Mean MTTR trên 7 RECOVERED | 630,999/7 = 90,143 s; verdict **UNKNOWN** / UNKNOWN | Khớp |
| Tập con {A, B3, E, G, K} | MTTR mean 66,200 → PASS/PASS; MTTD mean 13 → PASS; reaction mean (15+10+15+52+8)/5 = 20 → PASS | Khớp |
| Tập con {B1, B2} | MTTR mean 150 → FAIL (< 120), PASS (< 180) | Khớp |
| Tập con {A, C} | Có TIMEOUT, không thiếu dữ liệu, nên NOT_PASS / NOT_PASS. Reaction: C không có SUCCESS, nên NOT_PASS | Khớp |
| D2 (riêng, không vào A–M): như D nhưng SUCCESS hoàn tất tại 650 s > `cap_rec` 600 s | Reaction censored: NO_SUCCESS, không có giá trị; recovery TIMEOUT | Khớp |

Ví dụ mean che thất bại: mean của 7 lượt RECOVERED là 90,1 s, nhỏ hơn 120 s, nhưng chỉ 5/14 lượt đạt < 120 s. Vì vậy tỷ lệ và nhãn phải luôn đi cùng mean.

### 5.2b Effect không xác định (RV-02)

| Case | Đầu vào | Expected | Actual |
| --- | --- | --- | --- |
| F2 | Bản sao A, chỉ bỏ T_eff; giữ req/det/action/probe; không có record đánh giá effect | UNKNOWN_EFFECT, ở lại N; MTTD/MTTR/total/reaction đều MISSING | Khớp |
| F3 | req 0; record NO_EFFECT nhưng bằng chứng chỉ phủ 0–100 s trong W_eff = 300 s | UNKNOWN_EFFECT (bằng chứng có khoảng trống), ở lại N | Khớp |
| F4 | req 0; detector báo tại 20 s, action SUCCESS tại 30 s; record NO_EFFECT nhưng không có mẫu nào (mất probe toàn cửa sổ effect) | UNKNOWN_EFFECT; không gán T_eff từ detector | Khớp |
| {A, F2} (phản ví dụ của Codex) | Một lượt hợp lệ và một lượt mất effect | requested 2, CONFIRMED 1, NO_EFFECT 0, UNKNOWN 1, N = 2; khoảng MTTD < 60 và MTTR < 120 đều [0,5; 1,0]; mean MTTD 30 s chỉ mô tả; verdict MTTD, MTTR (120/180) và reaction đều **UNKNOWN**. Bản đầu cho N = 1, tỷ lệ 1/1 và PASS | Khớp |

### 5.2c Không có lượt đủ điều kiện (RV-03)

| Case | Đầu vào | Expected | Actual |
| --- | --- | --- | --- |
| EMPTY | Dataset rỗng | Trạng thái EMPTY, N = 0; tỷ lệ và mean không xác định; verdict MTTD/MTTR/reaction đều **EMPTY**; không lỗi | Khớp |
| ALL_NO_EFFECT | Chỉ F (CONFIRMED_NO_EFFECT) | NO_ELIGIBLE; requested 1, no-effect 1, N = 0; tỷ lệ/mean không xác định; verdict **NO_ELIGIBLE**. Bản đầu dừng với TypeError | Khớp |
| ALL_UNKNOWN | F2, F3, F4 | Không phải N = 0: requested 3, UNKNOWN 3, CONFIRMED 0, N = 3; khoảng MTTD < 60 = [0, 1]; không có mean; verdict **UNKNOWN** | Khớp |

### 5.3 Uptime và CPU

| Case | Đầu vào | Expected | Actual |
| --- | --- | --- | --- |
| Budget | \|W\| = 14.400 s × 0,1% | 14,4 s | Khớp |
| U1: outage chồng lấn, hai luồng | Luồng 1 lỗi 100–109; luồng 2 lỗi 105–117 | Cộng thô 10 + 13 = 23 s (sai); hợp = [100,118) = 18 s; D_min = 17 s; A_upper = 0,998819 < 0,999, nên **FAIL** | Khớp |
| U2: một outage | Lỗi 1000–1009 | D_point = 10 s; D_max = 11 s; A_lower = 0,999236, nên **PASS** | Khớp |
| U3: U2 + mất probe | Không mẫu 5001–5009 | U = 9 s; A_lower = 1 − 20/14400 = 0,998611; A_upper = 0,999375, nên **UNKNOWN** (không thành PASS; mẫu số vẫn 14.400 s) | Khớp |
| U4: chập chờn | Lỗi 10–11, đạt 12, lỗi 13, đạt từ 14 (W = 100 s) | Một outage [10,14) = 4 s; D_max = 5 s | Khớp |
| U5: U nằm trong outage (phản ví dụ 1 của Codex) | Một luồng: đạt 0–99; lỗi 100–104; không mẫu 105–113; lỗi 114–119; đạt từ 120 | U = [105,114) = 9 s; D_lower = \|[99,120) ∪ U\| = 21 s (không phải 21 + 9 = 30); D_point = [100,105) ∪ [114,120) = 11 s; D_min = 10 s; A_lower = 0,998542, A_upper = 0,999306, nên **UNKNOWN**. Bản đầu coi U là down chắc chắn (D_min 19 s) và ra FAIL | Khớp |
| U6: gap rời ở hai luồng (phản ví dụ 2 của Codex) | Luồng A thiếu 1001–1009; luồng B thiếu 5001–5009; mọi mẫu khác đạt | U = 9 + 9 = 18 s (hợp, rời nhau); A_lower = 0,998750; A_upper = 1, nên **UNKNOWN**. Bản đầu lấy max U = 9 s và ra PASS sai | Khớp |
| U7: gap chồng giữa hai luồng | Luồng A: đạt 0–1000 và từ 1010; luồng B: đạt 0–1004 và từ 1015 | U = [1001,1010) ∪ [1005,1015) = [1001,1015) = 14 s (cộng thô 19 s); A_lower = 0,999028, nên **PASS** | Khớp |
| U8a: outage chưa đóng tại cuối W | Đạt 0–14389; lỗi 14390–14399 | Cắt tại 14.400 s: D_point 10 s, D_max 11 s, D_min 9 s, U = 0; A_lower = 0,999236, nên **PASS** | Khớp |
| U8b: probe ngừng giữa outage | Đạt 0–999; lỗi 1000–1009; sau đó không còn mẫu | U = [1010, 14400) = 13.390 s; D_point = 10 s (không đếm U); D_lower = \|[999, 14400)\| = 13.401 s; A_lower = 0,069375 ≥ 0; A_upper = 0,999375, nên **UNKNOWN**. Bản đầu cho A_lower = −0,860 | Khớp |
| U9: luồng A down chắc chắn khi luồng B chưa quan sát | A: đạt 0–1999, lỗi 2000–2009, đạt từ 2010; B: đạt 0–1999, không mẫu tới 2021 | D_point = 10 s, D_min = 9 s (U của B không xóa downtime của A); D_lower = \|[1999,2021)\| = 22 s; A_lower = 0,998472, A_upper = 0,999375, nên **UNKNOWN** | Khớp |
| U10–U12: đầu vào availability không hợp lệ | Không khai báo luồng; W = 0; W âm | NO_REQUIRED_FLOWS / INVALID_WINDOW; bounds và downtime không xác định, verdict UNKNOWN. Trước sửa: PASS / ZeroDivisionError / PASS | Khớp |
| U13: luồng được khai báo nhưng mất toàn bộ mẫu | Một luồng rỗng, W = 14.400 s | U = W; A_lower = 0, A_upper = 1; UNKNOWN | Khớp |
| R1/R2/R3: ứng viên recovery sát trần | Probe lỗi 0–587, đạt 588–650 → T_rec 590; lỗi 0–597, đạt từ 598 → T_rec 600; lỗi 0–598, đạt từ 599 → T_rec 601. Đơn vị s, cap 600, K 3, S 30 | 590 và 600 được xác nhận sau đủ S; 601 không được xét, TIMEOUT. Trước sửa, 590/600 bị cắt mất bằng chứng ổn định | Khớp |
| R4/R5: thiếu hoặc relapse trong S | R1 nhưng mẫu chỉ tới 600; hoặc R1 với mẫu lỗi tại 610 | MISSING_PROBE / TIMEOUT; không có recovery được xác nhận | Khớp |
| R6: dừng fault trong S | eff 0, det 20, action SUCCESS 30; probe lỗi 1–40, đạt 41–200; stop 50 | T_rec 43, verified_at 73 > stop 50: RECOVERED_AFTER_STOP, không đạt dù MTTR quan sát 23 s | Khớp |
| Request success rate | 9.985 / 10.000 | 99,85%, báo tách khỏi A | Khớp |
| CPU | 170m + 150m trên 2 × limit 200m | 0,80, **không** > 0,80; cùng mức trên request 2 × 50m = 3,2 (320%) | Khớp |
| CPU duy trì | Chuỗi 30 s: [80,5; 82; 79; 85]; [80,5; 82; 81]; [80,0; 82; 81] | Không đạt; đạt; không đạt (80,0 không > 80) | Khớp |
| CPU sau scale | 322m / 3 × 200m | 0,537 | Khớp |

### 5.4 Bộ kiểm có bắt lỗi thật không

Mỗi mutant là một bản sao tạm của script, chỉ đổi đúng một quy tắc rồi chạy lại. `mutate.py` kiểm chuỗi cần đổi xuất hiện đúng một lần. Script mutant phải exit 1. Bảy mutant đầu là bộ của bản đầu, nhắm lại theo mã mới; số BAD tăng vì có thêm phép kiểm. Các mutant từ `u_additive` trở xuống tái tạo đúng lỗi của bản đầu hoặc biến thể gần.

| Mutant | Lỗi logic giả lập | Kết quả |
| --- | --- | --- |
| `le` | MTTD dùng `≤` thay `<` | exit 1, 2 BAD |
| `le_mttr` | MTTR dùng `≤` | exit 1, 4 BAD |
| `sum_union` | Cộng outage thay vì hợp nhất | exit 1, 1 BAD |
| `drop_timeout` | Bỏ TIMEOUT khỏi mẫu số | exit 1, 12 BAD |
| `neg_mttd` | Giữ MTTD âm | exit 1, 3 BAD |
| `gap_as_up` | Coi khoảng mất probe là up | exit 1, 15 BAD |
| `cpu_ge` | CPU dùng `≥ 80%` | exit 1, 1 BAD (case 80,0 thêm ở bản đầu) |
| `u_additive` | Cận dưới cộng D_max + U thay vì hợp (RV-01) | exit 1, 6 BAD (U5, U8b, U9) |
| `u_max_flow` | Lấy U của một luồng lớn nhất thay vì hợp mọi luồng (RV-01) | exit 1, 5 BAD (U6 ra PASS sai, U7) |
| `dmin_keep_u` | D_min giữ phần U nằm trong outage (RV-01) | exit 1, 3 BAD (U5 ra FAIL) |
| `dpt_keep_u` | D_point giữ phần U (RV-01) | exit 1, 2 BAD (U5, U8b) |
| `noeff_default` | Thiếu record effect thì coi là NO_EFFECT (RV-02) | exit 1, 8 BAD ({A, F2} ra PASS) |
| `noeff_no_coverage` | Chấp nhận record NO_EFFECT dù bằng chứng có khoảng trống (RV-02) | exit 1, 3 BAD (F3) |
| `unk_drop` | Loại UNKNOWN_EFFECT khỏi N (RV-02) | exit 1, 7 BAD |
| `n0_pass` | N = 0 trả PASS (RV-03) | exit 1, 2 BAD |
| `react_no_cap` | Reaction không áp `cap_rec` | exit 1, 1 BAD; lần đầu sống sót, đã thêm case D2 |

**Kết quả cuối: 18/18 mutant bị bắt.** Hai mutant Codex thêm: bỏ guard luồng bắt buộc → 2 BAD; cắt bằng chứng stability tại cap_rec → 3 BAD. Tất cả exit 1 có BAD, không Traceback; runner không coi crash là bắt được lỗi logic.

**Giới hạn.** Script kiểm logic của chính định nghĩa này, không kiểm dữ liệu hay producer thật.
- Case SQLi/containment không được mô hình hóa bằng số, vì tiêu chí effect của fixture chưa khóa (F-05).
- Bộ đánh giá effect trong script dùng một chuỗi mẫu dạng probe (đạt = tiêu chí effect không thỏa). Với vector dùng metric (CPU) thì ZER-13/ZER-14 phải khóa chuỗi bằng chứng tương ứng.
- Hai cận uptime phụ thuộc mô hình lấy mẫu (mục 3.7): outage ngắn hơn khoảng cách mẫu không được bắt.

## 6. Dữ liệu cần ZER-37 và ZER-38 cung cấp

Không khóa schema hay sửa producer/consumer ở đây. Tên trường chỉ để mô tả nhu cầu.

**ZER-37 (event):**
- ID: `run_id`, `trial_id`, `incident_id` trung tính, `action_id`, `event_id` duy nhất (để khử trùng), `method_version` hoặc phiên bản tham số đo.
- Nhóm cấu hình: B0/B1/B2/B3/BM.
- Mỗi event: `event_type` theo bảng mục 3.3, `ts_event` UTC ms theo đồng hồ của thành phần tạo, `ts_ingest`, `source_component`, định danh host/đồng hồ, service/luồng mục tiêu.
- Trạng thái action là chuỗi riêng: API_ACCEPTED → ACTION_COMPLETED với SUCCESS/FAILED/PARTIAL/TIMEOUT và kết quả kiểm hậu điều kiện.
- RECOVERY_VERIFIED chỉ do bộ đánh giá probe phát sau khi đủ cửa sổ ổn định. Tách T_rec (mẫu đạt thứ K), recovery_verified_at (T_rec + S) và ts_ingest; event mang tham chiếu mẫu làm căn cứ và phiên bản quy tắc (Δ, K, S, L).
- Ghi cả RELAPSE.
- Event phía điều khiển (attack_requested, attack_stopped, effect, ground truth) lưu ở kho tách biệt với dữ liệu bên chữa lỗi được truy vấn. Chúng chỉ liên kết qua ID trung tính.
- Một record `effect_evaluation` cho **mọi** incident được yêu cầu, kể cả khi không có effect: trạng thái CONFIRMED / CONFIRMED_NO_EFFECT / UNKNOWN_EFFECT, phiên bản tiêu chí effect, W_eff, tham chiếu mẫu bằng chứng đầu/cuối và khoảng trống lớn nhất. Event T_eff có nguồn hợp lệ là bằng chứng CONFIRMED; thiếu cả event đó lẫn record kết luận thì UNKNOWN_EFFECT, không phải NO_EFFECT.
- Event phải tái tính được từ bản lưu bền, không chỉ từ dashboard.

**ZER-38 (probe):**
- Mỗi mẫu: `probe_id`, luồng (Boutique mua hàng; fixture riêng), `sequence` tăng liên tục (để phát hiện mất mẫu), `t_start`, `t_end`, latency từng bước và tổng, status, kết quả kiểm nội dung, lớp lỗi (timeout/kết nối/nội dung/chậm), vị trí client và độ lệch đồng hồ, phiên bản probe.
- Heartbeat riêng của tiến trình probe, để phân biệt “probe chết” với “dịch vụ lỗi”. Thu đủ cửa sổ ổn định sau ứng viên T_rec, kể cả tới cap_rec + S; dừng fault sau khi đã xác nhận hoặc sau cửa sổ quan sát cuối đã định trong protocol.
- Đủ dữ liệu để dựng lại **khoảng** chưa quan sát của từng luồng bắt buộc (không chỉ tổng thời lượng thiếu), vì ZER-10 phải hợp U giữa các luồng và với outage (mục 3.7). Ranh giới W ghi rõ.
- Chuỗi bằng chứng effect phủ cửa sổ W_eff sau mỗi T_req, kể cả khi không thấy effect, để xác nhận được NO_EFFECT.
- Log request của client benign: nguồn, kết quả và latency, phục vụ request success rate.
- Metric cho P179: chuỗi usage CPU theo container, snapshot request/limit theo pod theo thời gian, replica desired/ready.
- Ghi rõ scrape interval và rate window đã dùng.
- Probe chạy ngoài luồng healer. Healer không dùng kết quả probe để tự đóng incident.

## 7. Quy ước đã chấp nhận và tham số protocol còn mở

**Đã được Hoàng chấp nhận** trong chat ZD2-CODEX ngày 18/10/2026, 22:48 +07:00 sau kết luận audit/fix và câu hỏi xác nhận D-01…D-05. Bộ quy ước dưới đây được dùng làm chuẩn ngữ nghĩa cho ZER-37/ZER-38/ZER-10. Đây là chấp nhận phương pháp đo; không phải kết quả KPI runtime, không tự khóa các tham số formal ở F-01…F-09.

Bản kỹ thuật Hoàng chấp nhận có SHA-256 `eb35f30bdd952ad81ded97d803b7c3cb736cd806dfd09f7a1e13b890646216e9`; lượt này chỉ thêm receipt nghiệm thu, không đổi công thức hoặc case.

| ID | Quyết định | Quy ước được chấp nhận |
| --- | --- | --- |
| D-01 | Verdict của KPI mean khi có censored/missing; mean hay tỷ lệ là verdict chính | Bảng verdict mục 3.4; luôn báo cả hai; không đặt tỷ lệ đạt tối thiểu |
| D-02 | Mốc đầu/cuối của “thời gian phản ứng” P187 | T_det đến ACTION_COMPLETED=SUCCESS đầu tiên |
| D-03 | Định nghĩa CPU > 80% P179 | Container mục tiêu; Σusage/Σlimit; > 80% duy trì ≥ 60 s |
| D-04 | T_rec tại mẫu thứ K, xác minh sau S; AFTER_STOP / BEFORE_DETECT; horizon cap_rec + S | Như mục 3.2 và 3.4; không xét ứng viên sau cap_rec, không tính đạt nếu dừng fault trước xác minh ổn định |
| D-05 | Verdict uptime ba trạng thái theo cận | PASS chỉ khi A_lower ≥ 0,999, với cận tính bằng hợp khoảng như mục 3.7 |

Các quy tắc sửa theo RV-01…RV-03 (hợp khoảng U, ba trạng thái effect, nhánh N = 0) là sửa lỗi số học và xử lý thiếu dữ liệu, không phải quyết định phạm vi. Chúng không thêm mục cần Hoàng chọn. W_eff theo vector đi cùng F-05.

**Chốt trước formal run, trong protocol ZER-53; không chặn nghiệm thu định nghĩa:**

| ID | Nội dung |
| --- | --- |
| F-01 | Giá trị số Δ, K, S, gap, ε, `cap_det`, `cap_rec`; L và timeout probe sau pilot |
| F-02 | Thời lượng warm-up tối thiểu |
| F-03 | Thời lượng cửa sổ formal; War Game 4h là ví dụ |
| F-04 | Luồng bắt buộc cho P108 (đề xuất: Boutique mua hàng); fixture báo riêng |
| F-05 | Tiêu chí effect và recovery/containment của từng vector (ZER-13/ZER-14), gồm cửa sổ quan sát W_eff và chuỗi bằng chứng dùng để xác nhận NO_EFFECT |
| F-06 | Rate window/scrape cho CPU; pha đo P179 |
| F-07 | Số lượt formal và mẫu số N mỗi nhóm; lý do loại được phép (thống kê thuộc ZER-8/ZER-53, không quyết ở đây) |
| F-08 | Ngưỡng request success rate của benign khi block |
| F-09 | Ngưỡng độ trễ “thời gian thực” cho dashboard P109 |

Không có mâu thuẫn nguồn nào buộc đổi cam kết. Không cần hỏi Hoàng thêm quyền. Các ngưỡng 60 s, 120/180 s và 99,9% được giữ nguyên.

## 8. Tự kiểm

**Đối chiếu với yêu cầu gói giao.** Snapshot gói giao lúc 21:25. AC sống chưa được Claude đọc; Codex đã đối chiếu AC sống ZER-32/AC-02 ZER-5 trong review và xác nhận khớp phạm vi.

| Yêu cầu | Nơi đáp ứng | Kết quả tự kiểm |
| --- | --- | --- |
| 1. Ma trận phủ P100, P104–P109, P176, P179, P187, P193, P195, P201, P203, P208–P211 cùng xác nhận SCOPE | Mục 2: RM-01…RM-22. P100 → RM-06; P104 → RM-01; P105 → RM-02; P106 → RM-03/04/05; P107 → RM-07/08; P108 → RM-10; P109 → RM-11; P176 → RM-12; P179 → RM-13; P187 → RM-14; P193/P210 → RM-16; P195 → RM-15; P201/P211 → RM-17; P203 → RM-18; P208/P209 → RM-19; chấp nhận đăng → RM-20; Python/Go + Boutique → RM-21 | Đủ; mỗi hàng có loại nguồn, phép thử, bằng chứng, downstream, giới hạn |
| 2. Từ điển và công thức; giữ ngữ nghĩa verification; MTTD < 60, 120/180, 99,9%; budget 14,4 s; CPU | Mục 3 | MTTD effect→detect, MTTR detect→recovery xác minh, total từ effect: khớp verification #2 và ZER-10. Không hạ ngưỡng |
| 3. Quy tắc dữ liệu và tình huống biên | Mục 4 | Đủ 12 tình huống được nêu, thêm thiếu metric CPU, effect không xác định và N = 0 |
| 4. Kiểm bằng timeline giả định | Mục 5 | 190/190 OK; 18/18 mutant bị bắt, không crash |
| Codex RV-01…RV-03 | Mục 3.2, 3.4, 3.5, 3.7, 4, 5.2b, 5.2c, 5.3, 6 | Các phản ví dụ của Codex nay cho kết quả đúng: U5 cận dưới 21 s và UNKNOWN; U6 UNKNOWN; {A, F2} giữ N = 2 và UNKNOWN. Probe N = 0 của Codex dùng bản sao A mất effect, nên theo quy tắc mới là UNKNOWN_EFFECT, N = 1, verdict UNKNOWN, không lỗi. Trường hợp no-effect đã xác nhận (chỉ F) ra NO_ELIGIBLE; dataset rỗng ra EMPTY |
| Codex tự sửa sau retest | Mục 3.4, 3.7, 5.3, 6 | U10–U13 và R1–R6; sửa đầu vào rỗng, biên ổn định/cap/stop và đồng bộ record effect |
| 5. Dữ liệu cho ZER-37/ZER-38; quyết định mở | Mục 6–7 | Không khóa schema; D/F tách loại chặn và loại trước formal |
| R0-T01-S02: “Ma trận truy vết; MTTR 120/180 giây, MTTD < 60 giây, uptime ≥ 99,9%, không hạ ngưỡng” | Mục 2, 3.4, 3.7 | Đạt ở mức định nghĩa |

**Phần còn lại.** Kiểm path, diff allowlist, hash cuối và giới hạn được ghi trong mục bàn giao của [ghi chú issue](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md). Hash của chính file này không ghi được bên trong nó.

**Không áp dụng (N/A):** build, CI, runtime, lab, merge. Lý do: gói chỉ gồm tài liệu và tính toán offline; không sửa mã, manifest hay CI. Không đóng ZER-32 hay ZER-5; không đổi Linear.
