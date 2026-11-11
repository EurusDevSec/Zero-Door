# ZER-25 và ZER-55 — Hồ sơ kỹ thuật R5

Gói hồ sơ bắt đầu review ngày 08/11/2026, cập nhật ngày 11/11/2026 (UTC+7). Phạm vi hiện hành là SQLi C5 và C0 trên laptop của Hoàng. Nguồn quyết định là [quyết định SQLi-only ngày 28/10](../../delivery/SCOPE.md#quyết-định-hiện-hành--sqli-only-hoàng-xác-nhận-28102026), [hợp đồng KPI](../ZER-32/requirements-and-kpi.md) và [protocol ZER-53 đã khóa](../ZER-53/protocol.md). Độ đủ của gói và quyền công bố được xét riêng.

## Nghiệm thu và phần còn mở

| AC | Bằng chứng | Kết luận để review |
| --- | --- | --- |
| ZER-25 AC-01 | Danh sách lỗi, các sửa đổi đã chạy trong Runtime07 và 57 phép kiểm lại ngoại tuyến | Phần pilot đủ chứng cứ theo các giới hạn bên dưới. Bất thường tài nguyên chưa xác định được nguồn. Sai quyết định B2/C0 và KPI chưa đo được giữ nguyên. |
| ZER-25 AC-02 / ZER-55 AC-01 | [Runbook](runbook.md), [manifest](dataset-manifest.json), [phát lại](replay-pilot.py), [kết quả kiểm](verification.json) | Tái lập được số liệu pilot từ bản lưu đã seal. [Kiểm dựng lại](rebuild-verification.json) xác nhận fixture dựng từ snapshot và đạt health/readiness ở chế độ an toàn. CI đã dựng worker từ 30/30 tệp khớp byte với snapshot và kiểm worker từ chối thiếu cấu hình. Biên bản build cũ khớp ID worker pilot. Nguồn đầy đủ của bản build worker lịch sử chưa được chứng thực. Biên bản pilot xác nhận ID Nemesis trong 12/12 ca. [CI Nemesis](https://github.com/EurusDevSec/Zero-Door/actions/runs/42453718435/job/128648162817) đã dựng và kiểm import từ cây Git trùng revision pilot. Hai đầu vào build thiếu trong snapshot lấy được từ Git. Việc tái tạo image cache lịch sử vẫn chưa được chứng minh. Hoàng chốt lưu riêng trên laptop tại `local-evidence/ZER-55/`. Đã kiểm khôi phục và phát lại đủ 12 ca từ bản lưu này. Pin bản dựng formal là cổng riêng. |
| ZER-25 AC-03 | Luồng hệ thống, ma trận claim, nguồn và H01–H08 dưới đây | Đạt sau khi đối chiếu nguồn, số liệu và H01–H08. Hoàng dùng hồ sơ để tự viết báo cáo sau khi các R hoàn tất. Xem [biên bản AC-03](../../delivery/milestones/R5-integration/technical-handoff.md#nghiệm-thu-hồ-sơ-theo-ac-03-đã-cập-nhật--11112026). |

## Các lỗi phát hiện trong pilot

| Hiện tượng | Xử lý và kiểm lại | Điều còn chưa chứng minh |
| --- | --- | --- |
| R01 admission thiếu hook NetworkPolicy | Biên bản ZER-52 ghi phục hồi đúng hook của lab, giữ PVC/spec. R07 qua admission cả 12 ca. Kiểm identity/drift và điều kiện admission trong bộ offline. | Bằng chứng giới hạn ở lab và baseline đã xác minh. |
| R02 MEMORY_STOP và R04 timeout lúc tạo topic, cleanup gốc INCOMPLETE | Giữ nguyên receipt gốc. Reconciliation riêng cho từng lượt đã đọc lại broker, xác nhận topic vắng mặt. Runtime07 chỉ dùng timeout 30 s cho đúng lệnh create topic sở hữu, giữ UNKNOWN khi timeout và không retry. 7 kiểm topic đạt. R07 có 36 readback topic rỗng. | Timeout dài hơn hỗ trợ hoàn tất lệnh hợp lệ. Nguồn gây I/O stall còn UNKNOWN. |
| R03 memory settle vượt ngưỡng | Quiet cố định 60 s cho mọi ca trước settle 30 s. 4 kiểm quiet đạt, gồm stop trước settle và giữ ngưỡng cũ. R07 đi qua cả 12 ca dưới tải 6 GiB. | Chưa có bằng chứng dưới tải ở 5,5 GiB. |
| R05 Windows dưới sàn, R06 guest PSI vượt sàn trong transport readiness | Kiểm RAM trước claim, dừng an toàn theo guard và giữ nguyên hai nhãn MEMORY_STOP/TRANSPORT_DEPENDENCIES_NOT_READY của R06. 5 kiểm headroom và 9 kiểm telemetry đạt. I/O PSI giữ riêng, không thay thế memory PSI. | Kết quả guard chỉ định được điều kiện dừng. Chưa xác định nguồn gây áp lực. |
| Cửa sổ terminal R07 đầu trả ServiceUnavailable trước claim | Kiểm hai case offline xác nhận API tạm lỗi được chờ trong giới hạn, lỗi vĩnh viễn hoặc hết hạn dừng. Cửa sổ r2 qua bước readiness và đủ 12 ca. Revision chính xác của launcher lúc thực thi là UNKNOWN vì launcher nằm ngoài seal batch. Phép kiểm offline dùng bản launcher/profile có hash tại bàn giao. | Lượt đầu vẫn WINDOW_FAILED/OFFLINE. |
| Nhãn worker, abstention, usage và pin setup của analyzer qua các lượt đầu | Giữ output cũ và bản đã sửa, chạy lại 16 phép kiểm analyzer v4 trên fixture giả. Phát lại Runtime07 khớp bản thống kê đã giữ, bao gồm hai B2/C0 ABSTAIN và usage của mọi ca. | Bản đo này dùng host monotonic cho workflow. MTTD và reaction thiếu chứng cứ timestamp/join. |
| C0 có cảnh báo giả định value=threshold=0 | Báo riêng điều kiện harness. B2 C0 có 0/2 quyết định đúng và 0/2 ca thực thi chặn nhầm. C0 formal đi qua detector đã pin. | Chưa kiểm đường detector với 5 seed mới. Không đổi điểm hay chỉnh rule từ mẫu pilot. |

Năm bộ kiểm runtime prep07 có 39 case. Analyzer v4 có 16 case. Hai case còn lại kiểm readiness của launcher. [Runbook](runbook.md#phạm-vi-phát-lại-và-kiểm-hồi-quy) phân biệt dữ liệu trong ZIP với các đầu vào cần để chạy lại đủ 57 case. Các phép kiểm dùng dữ liệu giả hoặc bản lưu cục bộ. [Biên bản kiểm](verification.json) ghi lần chạy đầu chặn nhầm socket nội bộ của test và lượt kiểm lại.

Batch R07 gốc ghi `RECONCILE_REQUIRED`. Review độc lập ZER-52 xác nhận đủ bằng chứng cho pilot mô tả và Hoàng đã nghiệm thu ZER-52. Replay hiển thị cả trạng thái gốc lẫn kết luận đối soát.

## Luồng hệ thống và ma trận câu hỏi

```text
Đối chứng C0 / ca C5 → fixture + Go chaos-worker → response và quan sát gắn UID
                                     │
                    B0 quan sát      ├─ B1 RulesController
                                     └─ B2 Gaia → Kafka riêng → Hephaestus
                                                         │
                              quyết định trước guard → guard → thực thi
                                                         │
              hậu điều kiện từ nguồn độc lập, benign probe, cleanup readback
```

ZER-23 đã kiểm đường chức năng có Nemesis chọn kịch bản. Trong Runtime07, cùng template cố định ở cả ba nhóm, không dùng chọn kịch bản thích ứng. Nhánh B2 trong pilot được ghép trên host qua Gaia, Kafka riêng và Hephaestus. Mô tả này dùng cho kiến trúc đã quan sát; [ZER-23](../ZER-23/README.md) ghi giới hạn native archive và cached worker.

| Câu hỏi | Cấu hình và tín hiệu | Claim được phép ở R5 | Claim chờ formal | Bảng hoặc biểu đồ nguồn |
| --- | --- | --- | --- | --- |
| RQ1 quyết định và containment | Pilot B1/B2 × SQLi, 2 ca mỗi ô. So receipt quyết định với fixture UID, nguồn, policy/action và probe 403, kiểm benign từ nguồn khác. B0 đối chứng effect. | B1/B2 mỗi nhóm containment fixture 2/2. B0 thấy effect 2/2 và giữ uncontained theo thiết kế. Điểm first-action theo quy tắc pilot. | ZER-53 M1/M1c cần bản ghi trước guard, resolver đúng source/UID/TTL 180 s và cặp B1/B2 trên cùng seed. M12 cần cả fixture và Boutique theo protocol. | [ZER-24, bảng từng ca AC-01](../ZER-24/README.md#ac-01--tái-tính-runtime07) và [M1/M1c/M12](../ZER-53/protocol.md) |
| RQ1 overhead | Host monotonic observation ready → treatment + probe, tách sum model-call latency. | B2 trừ B1 trung bình +25,18 s SQLi và +3,79 s C0. C0 B2 dừng trước Kafka. n=2/ô và chênh lệch workflow gồm nhiều thành phần. | So overhead theo nhóm và block, giữ failure và missing. Ưu thế thống kê hoặc suy nhân quả riêng cho LLM cần bằng chứng tương ứng. | [Biểu đồ workflow](pilot-workflow.svg) và [ZER-24, bảng theo ô AC-01](../ZER-24/README.md#ac-01--tái-tính-runtime07) |
| RQ3 cảnh báo/chặn nhầm và benign | Sáu ca pilot C0, cảnh báo do harness tạo. C0 formal định nghĩa cửa sổ benign và exposure cho M5/M6. | C0 không thực thi chặn nhầm 0/6; B2 ABSTAIN 2/2 được chấm sai quyết định pilot. Benign fixture đạt 12/12 trên toàn bộ pilot. | M5 theo slot có coverage, M6 theo action ID, benign fixture và Boutique báo riêng. BM chỉ mô tả và lượt thứ hai mỗi block bị lộ theo thiết kế. | [ZER-24, bảng ca C0 AC-01](../ZER-24/README.md#ac-01--tái-tính-runtime07) và [M5/M6](../ZER-53/protocol.md) |
| KPI nguồn | Mốc onset/detect/action/probe với clock đã xác nhận và phép ghép đúng ID. | MTTD/reaction UNKNOWN. MTTR/TotalRecovery/M7/M8 NOT_EVALUABLE_BY_DESIGN cho C5 một request với NO_OUTAGE_OBSERVED. Uptime P108 NOT_MEASURED. | D-01 áp cho MTTD/reaction khi đủ dữ liệu. C5 này không phát verdict MTTR. P179, RQ2/B3 và War Game nằm ngoài phạm vi hiện hành. | [ZER-24, bảng KPI AC-04](../ZER-24/README.md#ac-04--kết-quả-kpi-và-giới-hạn) và [D-01/D-04](../ZER-32/requirements-and-kpi.md) |

So với bản đăng ký gốc, ngưỡng CPU ứng dụng đích >80% (P179), scale up/down, rollback và yêu cầu bao phủ đủ ba vector đều được ghi là **chưa đáp ứng trong phạm vi thu hẹp**, và hiện chưa có văn bản điều chỉnh thuyết minh hay xác nhận mới của trường. [Quyết định phạm vi 28/10](../../delivery/SCOPE.md)

Dùng bảng 12 ca và bảng tổng hợp tại [ZER-24](../ZER-24/README.md) làm bảng nguồn. [Biểu đồ workflow](pilot-workflow.svg) hiển thị từng ca theo block và nhóm, đơn vị giây. Các điểm lấy từ `response_workflow_ms` trong bản phân tích đã seal. Các biểu đồ legacy trong `docs/experiments/analysis/` chỉ để truy vết nguồn cũ. Dòng SD tối thiểu 1,83 s trong protocol có [đính chính 0,30 s](protocol-erratum.md) đã khóa riêng. Giữ đúng hash protocol đã duyệt.

## H01–H08 và sổ nguồn

| ID | Xử lý trong bàn giao | Nguồn hoặc bước còn lại |
| --- | --- | --- |
| H01 | Giữ UNKNOWN cho lý do/lời chấp thuận thiếu chat gốc. | [Audit gốc](../../delivery/reference/audit-findings.md) và scope; phân loại xác nhận trực tiếp, nhận định và suy luận. |
| H02 | Tách thời hạn đăng ký tháng 01–06 và mốc 31/12 Hoàng xác nhận. | [Scope](../../delivery/SCOPE.md); khi hoàn thiện hồ sơ phải đối chiếu nguồn có thẩm quyền. |
| H03 | Kiểm đủ 8 CSV, 40 dòng và ngày attack_start 25/06/2026 theo từng file. Tách ngày dữ liệu với ngày nhập Git/phân tích. | [Manifest](dataset-manifest.json); ID legacy có nghĩa trong từng file. |
| H04 | FAILED/PARTIAL và terminal status được giữ. Recovery đòi probe độc lập; C5 pilot không sinh MTTR. | [Hợp đồng KPI](../ZER-32/requirements-and-kpi.md) và [protocol](../ZER-53/protocol.md); clock/scorer còn HOLD. |
| H05 | Gắn evidence runtime thật vào claim chức năng. Tách test giả, kế hoạch và quan sát runtime. | [ZER-23](../ZER-23/README.md), [ZER-52](../ZER-52/README.md), [biên bản replay](verification.json). Nguồn cho thao tác cloud lịch sử còn giới hạn ở xác nhận của Hoàng. |
| H06 | Runbook tách start cụm có sẵn với dựng lại và việc build/import một service. | [Lab restoration](../ZER-35/lab-restoration.md) và [runbook](runbook.md). Kiểm trước bất kỳ hành động dựng lại nào. |
| H07 | Bỏ khỏi kết luận các claim <100 MB, 88%, 157 MB và ưu thế AIOps cũ. R07 có số đo 6 GiB, 5,5 GiB chỉ kiểm idle. | [ZER-52](../ZER-52/README.md) và [manifest](dataset-manifest.json). Lợi ích chia vai RQ2/B3 ngoài scope. |
| H08 | Chuẩn hóa đường dẫn và loại nguồn. Tách người chấm Hòa với người vận hành BM, chưa xác minh lịch trực. Không gán tài khoản cũ cho Hòa. | [Audit gốc](../../delivery/reference/audit-findings.md), [protocol](../ZER-53/protocol.md). Nơi nhận bài xử lý ở R6. |

Sổ nguồn theo thứ tự sử dụng:

1. **Quyết định** — AC sống [ZER-25](https://linear.app/zero-door/issue/ZER-25/chot-ky-thuat-va-luu-ho-so-r5), [ZER-55](https://linear.app/zero-door/issue/ZER-55/djong-bang-ban-dung-runbook-va-dataset-manifest), khóa protocol trong [note ZER-24](../../delivery/milestones/R5-integration/pilot-and-war-game.md).
2. **Đo thực thi** — [báo cáo ZER-52](../ZER-52/README.md) và [tái tính ZER-24](../ZER-24/README.md). Raw ở thư mục cục bộ trong manifest. Có cả lý do loại R01–R06 và lần terminal chưa claim.
3. **Phép đo/kỹ thuật** — [thiết kế ZER-8](../ZER-8/research-design.md), [ZER-32](../ZER-32/requirements-and-kpi.md), [ZER-23](../ZER-23/README.md). Lời mô tả lịch sử dùng để tra cứu.
4. **Dữ liệu legacy** — tám CSV đã kê tên trong manifest. Báo cáo nghiên cứu cũ có claim phải xét lại theo scope và evidence mới.

**FORMAL_HOLD.** Trước R6 cần nguồn build/image đủ pin, seed/detector, đồng hồ, scorer/resolver, blind audit, BM và Hòa tách vai, một vòng B2/C5 kiểm tải 5,5 GiB và CLEAN, sau khi Hoàng duyệt gói vận hành. G5 chờ review hồ sơ và hoàn tất công bố, CI, merge và nghiệm thu các AC còn lại.
