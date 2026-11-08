# Issue — Pilot, khóa protocol và War Game

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-khoa-protocol-va-war-game). Nguồn đối chiếu: `R5-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T02-S01 | Pilot lặp trên case đơn giản và dễ nhầm lẫn để đánh giá độ biến thiên, overhead và lỗi đo. | [ZER-52](https://linear.app/zero-door/issue/ZER-52/pilot-lap-dje-xac-djinh-bien-thien-va-loi-djo) |
| R5-T02-S02 | Khóa RQ, ground truth/action set, số lặp, thứ tự, cấu hình đối chứng và cách tính metric/KPI. | [ZER-53](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc) |
| R5-T02-S03 | Chạy War Game mục tiêu 4 giờ theo protocol và budget đã chốt. | [ZER-54](https://linear.app/zero-door/issue/ZER-54/chay-war-game-co-probe-va-budget-dja-duyet) |
| R5-T02-S04 | Tái tính KPI; phân loại pass/fail, thiếu dữ liệu và nguyên nhân. | AC của [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-khoa-protocol-va-war-game) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T02-S01

Dữ liệu pilot nguyên bản cho B0/B1/B2 và B3 nếu giữ RQ2; căn cứ chọn số lặp và đánh giá lại thời lượng trong trần nguồn lực.

### R5-T02-S02

Protocol cố định trước formal run; B0/B1/B2/BM, quyết định B3/claim RQ2, profile HPA, biến thể đánh giá và ranh giới không lộ đáp án.

### R5-T02-S03

Timeline/probe raw, giới hạn tác động và bố trí giám sát; ghi rõ nếu run bị dừng.

### R5-T02-S04

Bảng kết quả tái tính; không lọc failure hoặc sửa số để đạt ngưỡng.

## Phụ thuộc cần đối chiếu

[R5-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/end-to-end-pipeline.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

### ZER-52 — Pilot Runtime07

[Hồ sơ pilot Runtime07](../../../evidence/ZER-52/README.md) lưu 12 ca, hai mẫu mỗi tổ hợp B0/B1/B2 × SQLi/C0, cùng kết quả review, cleanup và ước tính thời lượng cho ZER-53. Hồ sơ đáp ứng phần pilot AC-01 của ZER-24.

### Quy ước bàn giao

Mỗi lượt thực thi cần ghi issue Linear, thời điểm đọc AC, HEAD và thay đổi cục bộ, phạm vi file và thao tác, kết quả kiểm tra, bằng chứng, giới hạn và bước tiếp theo. Xem [quy trình bàn giao](../../WORKFLOW.md). Trạng thái, lịch và phân công cập nhật trên Linear.

### ZER-24 — Tái tính pilot và bàn giao review — 08/11/2026

Gói này đối chiếu AC-01, AC-02, AC-04 trên [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-va-khoa-protocol-sqli). Scope ngoại tuyến gồm báo cáo nghiệm thu và ghi chú này. Git HEAD lúc nhận `9567830020954bf3f30fd5a74240747be0c8ec1c`, branch `zer-42-bounded-sqli`, 56 dòng trạng thái có sẵn, gồm NOW đã dirty. Hai đường dẫn trong phạm vi sạch hoặc chưa tồn tại lúc bắt đầu. Dữ liệu gốc và protocol đã khóa được mở chỉ đọc.

[Báo cáo đối chiếu ZER-24](../../../evidence/ZER-24/README.md), SHA-256 `690b1786547bff02527263cad4216caa684e74cfaa2243d272d3bf14db0907e6`. Tái tính đủ 12 ca từ receipt Runtime07, kiểm 4.549 hash và 265 pin. Bảng ghi sai quyết định B2/C0, toàn bộ lượt dừng và KPI nguồn thiếu dữ liệu. Đính chính SD trọn vòng nhỏ nhất là 0,30 s. Dự toán theo sáu ô và lịch 5 block đã khóa giữ được căn cứ. AC-03 là yêu cầu nguồn chuyển bổ sung. FORMAL_HOLD theo §5 ZER-53.

**Bàn giao Claude review độc lập.** Đọc báo cáo đúng SHA-256 ở trên, AC sống của ZER-24 và dữ liệu gốc tại `R:/_Projects/Eurus_Workspace/zero_door/scratch/zer52-checkout/docs/evidence/ZER-52/`. Protocol khóa tại `R:/_Projects/Eurus_Workspace/zero_door/scratch/zer53-checkout/docs/evidence/ZER-53/protocol.md`. Dùng tệp cục bộ chỉ đọc. Đối chiếu ba AC và tái tính độc lập số liệu 12 ca, mẫu số C0/SQLi, các KPI theo D-01…D-05, lượt dừng và dự toán. Xác nhận phạm vi ảnh hưởng của đính chính 0,30 s ở §3. Kiểm phân biệt containment trên fixture với M12 formal, và đề nghị cách ghi phần thiếu dữ liệu trước nghiệm thu. Trả hash đã review, verdict theo từng AC, finding theo mức độ kèm file/dòng/receipt, và điều kiện còn thiếu để Hoàng chấp nhận. Codex sẽ xử lý finding và kiểm lại delta. Bước review dùng evidence sẵn có và không phát sinh lượt lab.

**Checkpoint tiếp theo.** Chờ Claude trả review trên đúng hash, xử lý finding rồi đưa Hoàng nghiệm thu. Bước này mới hoàn tất gói tài liệu cục bộ. Linear và publication xử lý theo quyền ở bước nghiệm thu.


### ZER-24 — Xử lý review độc lập — 08/11/2026

Claude review đúng báo cáo SHA-256 `690b1786547bff02527263cad4216caa684e74cfaa2243d272d3bf14db0907e6`. Biên bản review có SHA-256 `4f05c3623e4d2319771724ab5505dc9c67f5111194c679cd4504aebb40c8bc81`. Claude tái tính khớp 12 ca, 4.549 hash raw và 265 pin, không có P1. AC-01 đạt ở mức pilot mô tả. AC-02 đạt có điều kiện lưu bền bản khóa. AC-04 có ba P2 về diễn giải và trình bày.

Đọc lại AC hiện hành của [ZER-24](https://linear.app/zero-door/issue/ZER-24/pilot-va-khoa-protocol-sqli) ngày 08/11/2026. AC-01/02/04 giữ phạm vi SQLi-only, AC-03 nguồn chuyển bổ sung. Scope của delta ngoại tuyến gồm báo cáo ZER-24, bản sao nguyên byte protocol và ghi chú này. HEAD `9567830020954bf3f30fd5a74240747be0c8ec1c`. Báo cáo và ghi chú đã có thay đổi cục bộ của gói trước, tệp protocol chưa có ở đường dẫn đích khi bắt đầu.

- **P2-01.** Đã đối chiếu sáu ca C0 và hai Gaia receipt. Báo cáo giữ 0/2 và ghi cảnh báo do harness tạo với value=0, threshold=0, cùng giới hạn ngoại suy.
- **P2-02.** Đã dùng nhãn theo nguyên nhân, bổ sung B1 trên cùng định nghĩa D-01. MTTR pilot/formal được ghi theo giới hạn thiết kế C5 một request và thiếu phép đo outage/phục hồi. P108 chưa đo, P179 và War Game ngoài đợt này.
- **P2-04.** Đã sửa hàng phân cách bảng 12 ca và đối chiếu hai bảng số với bản Claude đã review. Bổ sung dẫn chiếu review Runtime07, biên bản đối soát CLEAN riêng của Runtime02 và hai nhãn dừng của Runtime06. SHA-256 báo cáo mới `0633c8cc9b1cfb97c8798d37d5faf96f52f5b7c7b92ae75d1bb95f3b2a5a7dea`. [Báo cáo ZER-24](../../../evidence/ZER-24/README.md)

#### Biên bản khóa ZER-53 và nơi lưu — P2-03

Hoàng duyệt protocol v3 ngày 08/11/2026 sau khi Claude kiểm đúng SHA-256 `c9a6950de02a0d7e33417194da82afef317ee69a3e429e06653cc844b81ecfd8`. Base của bản khóa `22f668a0a3d7aec36fd5a878ef596f06de10dd89`. Đã đặt [bản đúng byte](../../../evidence/ZER-53/protocol.md) tại đường dẫn tài liệu chính thức và đối chiếu với bản lưu trong checkout ZER-53. Biên bản này ghi trạng thái khóa cho đúng revision đó. Tệp chứa hai dòng trạng thái lúc soạn để giữ byte đã duyệt. Tệp đang ở cây làm việc, bước lưu bền còn cần quyền ghi vào Git cùng biên bản này. Base công bố phải chứa báo cáo ZER-52 để liên kết pilot trong protocol trỏ đúng tài liệu. [Biên bản duyệt ZER-53 trên Linear](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc)

**Đính chính §3.** SD trọn vòng nhỏ nhất là 0,298399 s ở B1/C0. Khoảng đúng là 0,30–15,08 s. Dự toán lấy min/mean/max từng ô, số lặp lấy theo mục tiêu thăm dò. Claude xác nhận sai lệch chỉ ở phần mô tả.

**Điểm kiểm readiness formal.** Hai ca pilot B2/SQLi có DECISION `ANALYSIS/NO_ACTION` của Gaia trước `PROPOSAL/BLOCK_IP` của Hephaestus. Kiểm scorer chọn quyết định điều phối đúng vai và giai đoạn theo §4, bao gồm ABSTAIN nếu Gaia kết thúc luồng. Chọn bản ghi DECISION sớm nhất theo thời gian có thể chấm sai cả hai ca. Thực hiện phép kiểm ở gói readiness, trong khi formal giữ HOLD.

**Checkpoint tiếp theo.** Claude chỉ cần kiểm hash và delta của báo cáo này. Hoàng duyệt nghiệm thu và quyền ghi Git cho ba tệp thuộc gói trước khi chốt AC trên Linear.

**Nghiệm thu trước công bố — 08/11/2026.** Claude kiểm delta và xác nhận báo cáo đúng SHA-256 `0633c8cc9b1cfb97c8798d37d5faf96f52f5b7c7b92ae75d1bb95f3b2a5a7dea` đủ căn cứ nghiệm thu AC-01, AC-02 và AC-04 sau khi lưu bền protocol. Hoàng duyệt nghiệm thu và công bố ba tệp. Chốt Linear sau khi đọc lại bản merge. Formal vẫn HOLD theo §5.
