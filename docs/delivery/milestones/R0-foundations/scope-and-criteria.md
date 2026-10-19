# Issue — Khóa phạm vi và tiêu chí đánh giá

[Milestone R0](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia). Nguồn đối chiếu: `R0-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước S03 đã có đầu ra dự kiến duy nhất: `docs/evidence/R0-T01-S03/baseline-source-ledger.md`. Không sửa dữ liệu gốc. Gói ZER-32/S02 ngày 18/10 bên dưới chốt đầu ra `docs/evidence/ZER-32/requirements-and-kpi.md`. Không dùng phạm vi S03 để sửa toàn issue.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R0-T01-S01 | Ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI và bài được chấp nhận đăng. | AC của [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia) |
| R0-T01-S02 | Lập ma trận yêu cầu → phép thử; định nghĩa MTTD, MTTR, downtime, uptime và mẫu số. | [ZER-32](https://linear.app/zero-door/issue/ZER-32/lap-ma-tran-yeu-cau-va-djinh-nghia-kpi) |
| R0-T01-S03 | Chụp baseline Git/cấu hình; lập inventory legacy và source ledger từ review H01–H08. | [ZER-33](https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R0-T01-S01

Các xác nhận của người dùng đã được ghi trong file SCOPE.md của delivery.

### R0-T01-S02

Ma trận truy vết; cách đánh giá MTTR 120/180 giây theo thuyết minh, MTTD <60 giây và uptime ≥99,9%, không hạ ngưỡng.

### R0-T01-S03

HEAD/dirty files, hash và số dòng từng CSV, timestamp lưu trong dữ liệu tách khỏi timeline Git; nguồn DOCX/xác nhận mới/IDE/chat được phân loại, path được kiểm tra. Giữ nguyên raw/handoff; thiếu lịch sử hoặc danh tính thì UNKNOWN.

## Phụ thuộc cần đối chiếu

Không có.

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

## Gói giao Claude — ZER-32 — 18/10/2026, 21:25 +07:00

### Quyền và mục tiêu

Hoàng yêu cầu trực tiếp trong chat ZD2-CODEX: giao Claude thực hiện trọn ZER-32, tự kiểm/sửa trước khi bàn giao, rồi Codex review tổng hợp một lượt để giảm gửi qua lại. Đây là quyền thực hiện gói tài liệu bên dưới; phân vai làm việc này không tự cập nhật assignee Linear.

Claude là bên ghi tiếp theo trên checkout; Codex nhường ghi trong lúc Claude thực hiện. Hoàn thành một gói đủ review thay vì trả từng bảng/công thức. Theo vòng phối hợp trong WORKFLOW: một review tổng hợp → sửa gom nếu có finding → retest phần bị ảnh hưởng; không tự duyệt nếu còn lỗi chặn chỉ để đạt một vòng.

Mục tiêu: người triển khai phép đo và người viết báo cáo có thể xác định mỗi cam kết được thử thế nào, lấy bằng chứng từ đâu, tính KPI ra sao và khi nào được kết luận đạt/chưa đạt/UNKNOWN. Đây là định nghĩa và kiểm tra logic bằng dữ liệu giả định, chưa phải kết quả thực nghiệm.

### Baseline, nguồn và phạm vi ghi

Codex đã đọc AC sống của ZER-32 và issue cha ZER-5 ngày 18/10/2026, khoảng 21:24 +07:00 qua kết nối `linear_zero_door`; URL thuộc `linear.app/zero-door/`. Khi bắt đầu, Claude đọc lại AC hoặc ghi rõ dùng snapshot dưới đây nếu phiên không có kết nối. Không cài lại MCP hay dùng connector EurusDevSec/S-cool thay thế.

Git Bash kiểm trước khi Codex soạn gói: nhánh `codex/zer-35-local-lab`, HEAD `a224ce54fc0e742bbb647c61e6e9201094a9de25`, working tree sạch. Sau bước soạn này sẽ có thay đổi tài liệu trong ghi chú hiện tại và NOW. Claude phải kiểm lại HEAD/dirty thực tế; giữ nguyên mọi thay đổi ngoài scope. Nhánh này là nhánh publication ZER-35 cũ, không phải nhánh ZER-32 đã được tạo. Không tự checkout/reset/pull/stash hoặc commit lên nhánh đó; ghi tài liệu local không cần đổi nhánh, còn publication xử lý riêng sau review.

Đọc theo thứ tự README → NOW → issue/ghi chú này → SCOPE/WORKFLOW. Các nguồn trực tiếp cho gói:

- `docs/handoff/2026-10-17-registration-requirements-excerpt.md`: yêu cầu DOCX có hash và vị trí Pn. Nếu chỉ đọc bản trích, ghi đúng: “Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX.”
- `docs/delivery/SCOPE.md`: xác nhận hiện hành, gồm Python/Go và Online Boutique, ba vector, KPI, sản phẩm và chấp nhận đăng.
- `docs/delivery/reference/verification.md`: mốc thời gian, mẫu số, probe độc lập và giới hạn kết luận hiện có. Mâu thuẫn với nguồn phải nêu rõ, không âm thầm thay nghĩa.
- `docs/delivery/milestones/R1-measurement/event-contract.md` và `docs/delivery/milestones/R1-measurement/probes-and-metrics.md`: chỉ đọc phần consumer trực tiếp để đầu ra đủ dùng cho ZER-37/ZER-38. Không cần khảo sát toàn codebase hoặc hydration lại ZER-35.

Allowlist ghi cho Claude:

1. Tạo `docs/evidence/ZER-32/requirements-and-kpi.md`: artifact chính, chứa cả ma trận, định nghĩa, ví dụ kiểm và tự review; không tách thành nhiều báo cáo nhỏ.
2. Bổ sung bàn giao cuối gói vào ghi chú issue hiện tại; giữ nguyên lịch sử/nguồn.
3. Cập nhật phần con trỏ đầu `docs/delivery/NOW.md` để dẫn tới artifact và bước Codex review; không sao chép board/status/nhật ký.

Được đọc nguồn repo liên quan, chạy kiểm tra Git chỉ đọc và tính toán offline với dữ liệu giả định. Nếu cần script tính tay dùng scratch/tmp không track, ghi phép tính có thể tái lập trong artifact. Không thêm framework, test mã ứng dụng hoặc probe mới cho gói tài liệu này.

Không sửa source/config/CI/manifest, raw CSV/legacy/source ledger ZER-33, SCOPE hoặc schema ZER-37. Không gọi Docker/Kubernetes, attack/healer/LLM/cloud hay cài dependency; không commit/push/PR/merge, sửa Linear, xuất bản/nộp bài hoặc gửi thông báo. Không lặp lại lab ZER-35. Nếu phát hiện thiếu thực thi thì ghi gap và issue liên quan, không tự sửa ngoài gói.

### Nội dung bắt buộc của artifact

**1. Ma trận yêu cầu → phép thử → bằng chứng.** Mỗi hàng có ID ổn định trong artifact, nguồn/đoạn cụ thể, nội dung cam kết, điều kiện/kịch bản cần thử, expected và tiêu chí đạt, bằng chứng cần lưu, issue downstream đã xác minh hoặc UNKNOWN, và giới hạn. ID hàng dùng truy vết tài liệu, không tạo hệ issue mới. Không coi việc mô tả phép thử là đã chạy hoặc đã PASS.

Bao phủ tối thiểu P100/P104–P109, P176/P179/P187 và các sản phẩm P193/P195/P201/P203/P208–P211 của bản trích cùng xác nhận hiện hành: ít nhất 5 microservices có nghiệp vụ; SQLi/DDoS L7/resource exhaustion; scale up/down, block nguồn tấn công với benign traffic còn hoạt động, rollback bản tốt; tự phát hiện/cô lập/phục hồi; LLM; dashboard; KPI; source/manifests/video/dữ liệu/báo cáo/slide/poster; chấp nhận đăng theo SCOPE. Không chỉ liệt kê pod hoặc API trả thành công. Phân biệt yêu cầu nguồn, xác nhận người dùng, lựa chọn đo lường đề xuất và điều chưa biết. Liên kết provenance không biến ghi chú Complete hoặc dữ liệu legacy thành runtime proof. Chỉ truy vết yêu cầu source ledger của ZER-33, không làm thay ZER-33.

**2. Từ điển phép đo và công thức.** Định nghĩa incident/trial/cửa sổ đo; đơn vị, timestamp/timezone, clock source/độ lệch, nguồn ground truth và điều kiện hợp lệ. Có các mốc attack effect, detection, publish/consume, heal start, action completed, recovery verified, attack stopped; phân biệt API_ACCEPTED, ACTION_COMPLETED và RECOVERY_VERIFIED. Attack requested không tự là attack có hiệu lực; attack stopped không tự là recovery.

Giữ ngữ nghĩa hiện có trong verification: MTTD từ effect đến detect, MTTR từ detect đến recovery được probe nghiệp vụ độc lập xác minh; báo thêm total recovery từ effect. Phân biệt duration từng incident với mean trên tập incident và nêu rõ mẫu số của mỗi tổng hợp. Định nghĩa riêng phản ứng <60s (P187); nếu nguồn không khóa đủ mốc thì đề xuất rõ và đánh dấu cần chấp nhận, không đồng nhất với MTTD hoặc MTTR.

Giữ MTTD <60s; báo cả tỷ lệ MTTR <120s và <180s cùng số lượng/mẫu số, không chọn lại ngưỡng sau kết quả. Phân phối của các lượt recovered phải đi kèm recovery/failure/timeout/missing trên tổng lượt đủ điều kiện. Không biến MTTR không quan sát được thành 0, loại thất bại khỏi mẫu số đạt ngưỡng hoặc dùng bình quân để che lượt không phục hồi. Làm rõ KPI trên mean hay tỷ lệ từng lượt và phần nguồn chưa quy định; không tự bịa tỷ lệ đạt được phép hay tuyên bố giải quyết sự mơ hồ của cam kết.

Định nghĩa uptime theo thời gian ≥99,9%, downtime, warm-up/trial/recovery window, điều kiện probe thành công (đúng nghiệp vụ/nội dung và latency) và quy tắc đóng/mở outage. Tách time-based availability khỏi request success rate; xử lý khoảng lấy mẫu, mất mẫu và độ bất định thay vì dùng scrape up/healthz làm bằng chứng uptime. Có ví dụ budget 4h × 0,1% = 14,4s, ghi rõ 4h là ví dụ từ kế hoạch repo, chưa phải thời lượng formal đã chốt. Không thay denominator bằng phần có dữ liệu để làm đẹp uptime; không tự bỏ outage trong recovery. Ngưỡng latency, cadence, số probe liên tiếp và cửa sổ formal chưa được nguồn khóa thì đề xuất giá trị/lý do hoặc ghi cần quyết định, không giả làm cam kết đã duyệt.

CPU target app >80% phải có target, aggregation, đơn vị, mẫu số (request/limit/core...), cửa sổ và thời lượng duy trì được nêu rõ. Không tự lấy CPU toàn node hay phần trăm tăng tương đối thay thế. Phân biệt đại lượng nguồn yêu cầu với cách operationalize được đề xuất và điểm cần chốt trước thực nghiệm.

**3. Quy tắc dữ liệu và tình huống biên.** Xử lý ít nhất: duplicate/out-of-order event, thiếu correlation/timestamp, clock lệch hoặc duration âm, nhiều action cho một incident, incident chồng lấn, detect/recovery thiếu, timeout, attack không có effect, action SUCCESS nhưng probe vẫn lỗi, tự hồi phục do Kubernetes, và probe mất dữ liệu. Nêu denominator/exclusion/censoring cùng lý do; giữ dấu vết mọi lượt bị loại. Uptime hợp nhất outage chồng lấn thay vì cộng hai lần. Nguồn thiếu là UNKNOWN, không suy thành PASS hoặc dữ liệu rỗng.

**4. Kiểm bằng tình huống giả định.** Tối thiểu một timeline tính được đầy đủ MTTD/MTTR/total recovery; case biên đúng 60/120/180s để kiểm dấu <; timeout/không recovery; action thành công nhưng nghiệp vụ lỗi; missing probe; outage chồng lấn và denominator. Có dữ liệu đầu vào, phép tính expected, actual từ tự kiểm, verdict và giới hạn. Chỉ chạy số case đủ bắt các lỗi logic này; ghi rõ SYNTHETIC/OFFLINE, không báo thành nghiên cứu/runtime PASS.

**5. Bàn giao dữ liệu cần cho ZER-37/ZER-38.** Nêu mốc/ID/nguồn event, cách phân biệt trạng thái và dữ liệu probe cần thu thập; không khóa schema hay sửa producer/consumer ở ZER-32. Các quyết định chưa có nguồn được gom thành một danh sách ngắn, chỉ rõ cái nào chặn nghiệm thu định nghĩa và cái nào chỉ cần chốt trước formal run. Không quyết định nghiên cứu đối chứng/thống kê thay toàn bộ ZER-8.

### Tự kiểm, bàn giao và review

Trước khi trả gói, Claude tự đối chiếu tất cả hàng với nguồn và AC-01 ZER-32/AC-02 ZER-5, tính lại ví dụ/các ngưỡng và mẫu số, kiểm link/path và diff allowlist. Sửa toàn bộ lỗi liên quan phát hiện được trong một lượt. Không viết test chỉ grep lại nội dung Markdown rồi gọi đó là kiểm chứng KPI.

Artifact và bàn giao ghi HEAD/dirty thực tế, thời điểm/timezone, AC snapshot/live, danh sách file thay đổi, phép kiểm expected/actual/verdict, hash SHA-256 artifact cuối và giới hạn. Dùng đường dẫn local thật để Codex review cùng checkout, không bịa GitHub blob link hoặc tuyên bố đã publish. Ghi build/CI/runtime/merge N/A cho gói docs với lý do; không tự đóng ZER-32 hoặc ZER-5.

Chỉ dừng để hỏi Hoàng khi có mâu thuẫn nguồn làm đổi cam kết, cần quyền ngoài allowlist, hoặc quyết định bắt buộc mà không thể ghi đề xuất/UNKNOWN một cách trung thực. Gom các câu hỏi một lần và tiếp tục phần độc lập; không hỏi lại các quyền tài liệu đã được cấp ở đây.

Khi xong, trả một thông báo ngắn cho Hoàng dẫn artifact và bàn giao; ghi đủ phần đạt/còn chặn, nhường writer cho Codex. Hoàng đưa kết quả về ZD2-CODEX để review. Codex sẽ đọc toàn artifact/nguồn trực tiếp, tái tính các case và gom finding theo vị trí, mức độ, ảnh hưởng, cách sửa trong một báo cáo; nếu cần sửa, Claude xử lý cả danh sách rồi Codex retest có trọng tâm.

## Bàn giao Claude — ZER-32 — 18/10/2026, 22:05 +07:00

**Kết quả: gói đủ để Codex review tổng hợp.** Đây là định nghĩa kèm kiểm logic offline, chưa phải kết quả thực nghiệm. Claude nhường quyền ghi checkout cho Codex. Không tự đóng ZER-32/ZER-5 và không đổi Linear.

**Artifact:** [`docs/evidence/ZER-32/requirements-and-kpi.md`](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md), SHA-256 `afff4068fc0ae5190f2d14f6b089c4e0c883174ff64ce67e6d19e23e6abc370c`, 422 dòng. Nội dung:
- Ma trận RM-01…RM-22.
- Từ điển phép đo: MTTD, MTTR, total recovery, reaction P187, uptime/downtime, request success rate, CPU P179.
- Quy tắc dữ liệu và tình huống biên.
- 15 incident giả định cùng case uptime/CPU.
- Nhu cầu dữ liệu cho ZER-37/ZER-38.
- Danh sách quyết định D-01…D-05 và F-01…F-09.

**Baseline và AC.**
- Nhánh `codex/zer-35-local-lab`, HEAD `a224ce54fc0e742bbb647c61e6e9201094a9de25`.
- Lúc bắt đầu chỉ dirty `docs/delivery/NOW.md` (`b8594d45…e5f056`) và ghi chú này (`35fb2ded…df4e59`). Hai file vẫn đúng hash đó ngay trước khi Claude nối bàn giao.
- AC sống: Claude không đọc được, vì connector của phiên trỏ workspace khác và gói cấm dùng thay thế. Claude dùng snapshot là gói giao lúc 21:25. Gói không chép nguyên văn AC-01 ZER-32/AC-02 ZER-5, nên Codex cần đối chiếu AC sống.
- DOCX: đối chiếu trích xuất do Codex đọc trực tiếp; Claude chưa trực tiếp đọc DOCX.

**File Claude thay đổi:**
1. Tạo artifact trên.
2. Nối mục này vào ghi chú issue.
3. Sửa con trỏ đầu `NOW.md`.
4. Tạo scratch không track: `scratch/zer32/kpi_check.py` (`725ab5a3…e9f2`), `kpi_check.out` (`41235cd5…6cc0`), cùng các `mut_*.out`.

**Thay đổi không do Claude, ngoài scope:** lúc 22:02:35 xuất hiện sửa đổi ở `AGENTS.md`, `docs/delivery/README.md` và file mới `docs/delivery/WORKING-AGREEMENT.md`. Claude không đọc, không sửa, không đưa vào gói. Bên ghi các file này cần tự xác nhận, vì có rủi ro vi phạm quy tắc một bên ghi.

**Kiểm (expected / actual / verdict):**

| Phép kiểm | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| `python scratch/zer32/kpi_check.py` | Expected tính tay khớp | 112/112 OK, exit 0 | PASS (OFFLINE) |
| 7 mutant: `<` thành `≤` (MTTD, MTTR), cộng outage thay vì hợp, bỏ TIMEOUT khỏi mẫu số, giữ MTTD âm, coi khoảng mất probe là up, CPU `≥` | Mỗi mutant làm script exit 1 | 7/7 exit 1. `cpu_ge` lần đầu sống sót, đã thêm case 80,0% | PASS |
| Tái tính tay biên và budget | 60,000 / 120,000 / 180,000 s không đạt; 14.400 × 0,1% = 14,4 s; U1 hợp 18 s (cộng thô 23 s) | Khớp | PASS |
| Đường dẫn `R:/…` trong artifact | Tồn tại | Đủ | PASS |
| ID ZER trong artifact | Có trong mapping | Không ID lạ | PASS |
| Phủ P100, P104–P109, P176, P179, P187, P193, P195, P201, P203, P208–P211 | Có trong ma trận | Đủ | PASS |
| `git diff --check` | Không lỗi whitespace | Không lỗi | PASS |

**N/A:** build, CI, runtime, lab, merge. Gói chỉ có tài liệu và tính toán offline. Không gọi Docker/Kubernetes, attack, healer, LLM hay cloud.

**Giới hạn:**
- Downstream được xác minh theo mapping read-back 17/10, không đọc live.
- Script chỉ kiểm logic của định nghĩa, không kiểm producer hay dữ liệu thật. Containment SQLi chưa mô hình hóa bằng số (F-05).
- Thông tin lab trong artifact là đọc cấu hình repo (scrape 30 s, HPA 70% request, limit/request frontend, rule `HighCPUUsage`), không phải đo runtime.

**Cần quyết định:**
- D-01…D-05 chặn việc dùng định nghĩa làm chuẩn: verdict của mean, mốc reaction P187, mẫu số CPU P179, mốc T_rec và nhãn after-stop/before-detect, verdict uptime theo cận.
- F-01…F-09 chốt trong protocol ZER-53 trước formal run.
- Không có mâu thuẫn nguồn buộc đổi cam kết. Giữ nguyên 60 s, 120/180 s và 99,9%.

**Bước tiếp:**
1. Codex review toàn artifact và nguồn trực tiếp, tái tính case, rồi gom finding một lượt.
2. Claude sửa gom nếu có finding.
3. Hoàng chấp nhận hoặc sửa D-01…D-05.

## Review Codex — ZER-32 — 18/10/2026, 22:18 +07:00

**NOT READY:** đã review toàn artifact, đối chiếu AC sống ZER-32/AC-02 ZER-5 và consumer ZER-37/ZER-38. Hash khớp; chạy lại nguyên 112 kiểm OFFLINE đạt. Ba finding P2 tái hiện độc lập: RV-01 hợp khoảng missing/outage sai (có false PASS uptime); RV-02 UNKNOWN_EFFECT thành NO_EFFECT và loại khỏi N; RV-03 N=0 gây lỗi và thiếu verdict. [Báo cáo và gói sửa](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md) giữ input/expected/actual, giới hạn và yêu cầu sửa gom.

Không sửa artifact/script Claude; chỉ tạo review, scratch reviewer, nối handoff và đổi NOW; giữ dirty ngoài scope. Không lab/LLM/source/Git publication/Linear. Bước tiếp: Claude sửa gom RV-01…RV-03 theo allowlist cũ, tự kiểm/bàn giao hash mới; Codex retest delta/regression. Hoàng chấp nhận D-01…D-05 sau khi sửa logic. Codex nhường ghi khi Hoàng chuyển gói; không tự gửi tin sang phiên khác.

## Bàn giao Claude — ZER-32 sửa gom RV-01…RV-03 — 18/10/2026, 22:33 +07:00

**Kết quả: đã sửa đủ ba finding, sẵn sàng cho Codex retest delta/regression.** Vẫn là định nghĩa kèm kiểm logic OFFLINE, không phải kết quả lab. Claude nhường quyền ghi checkout cho Codex. Không sửa [báo cáo review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md) (`28b58916…cadcfb`, giữ nguyên) và scratch reviewer `codex_review_check.py` (`df66b9c8…40d92`, giữ nguyên).

**Artifact:** [`requirements-and-kpi.md`](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md), SHA-256 `12ed9c5a87dc0a9aa77828bd09f6787fad027fa21b5b6aa5a6378d5f325c0f2b`, 526 dòng. Bản trước `afff4068…abc370c`.

**Baseline lúc nhận gói (22:19):** HEAD `a224ce54…`; artifact `afff4068…`, ghi chú này `98589123…580278`, NOW `f3d579ad…80317`. Ghi chú và NOW vẫn đúng hash đó ngay trước khi nối mục này. Ba file ngoài gói (`AGENTS.md` `fe18d000…`, `docs/delivery/README.md` `c7b9f0f8…`, `WORKING-AGREEMENT.md` `26cd7860…`) không đổi và Claude không động vào.

**Finding → cách sửa → case → kết quả:**

| Finding | Cách sửa (mục artifact) | Case kiểm | Kết quả |
| --- | --- | --- | --- |
| RV-01: cộng trùng D_max + U; lấy max U một luồng; U trong outage bị coi là down chắc chắn | 3.7: mọi đại lượng là tập khoảng nửa mở cắt theo W. `U = ∪_f U_f`; `D_lower = \|∪ max_f ∪ U\|`; `D_point`, `D_min` chỉ tính phần đã quan sát của chính luồng. Outage chưa đóng cắt tại cuối W. Nêu giả định lấy mẫu rời rạc. Bảng mục 4 cập nhật | U5 (phản ví dụ 1), U6 (phản ví dụ 2), U7 gap chồng giữa luồng, U8a outage mở tại cuối W, U8b probe ngừng giữa outage, U9 downtime luồng A khi luồng B chưa quan sát | U5: cận dưới 21 s (không phải 30), UNKNOWN (bản đầu FAIL). U6: U = 18 s, UNKNOWN (bản đầu PASS sai). U7: 14 s, PASS. U8b: A_lower 0,069 ≥ 0 (bản đầu −0,860). Khớp expected tính tay |
| RV-02: thiếu effect bị coi là NO_EFFECT và rời N | 3.2: ba trạng thái CONFIRMED / CONFIRMED_NO_EFFECT / UNKNOWN_EFFECT. Chỉ no-effect có record và bằng chứng phủ kín W_eff mới rời N. UNKNOWN_EFFECT ở lại N như lượt thiếu dữ liệu. 3.4: báo requested/effect/no-effect/unknown, khoảng ảnh hưởng gồm cả unknown. 6: record `effect_evaluation` cho mọi incident; coverage W_eff | F2 (bản sao A mất effect), F3 (record NO_EFFECT, bằng chứng có khoảng trống), F4 (mất probe toàn cửa sổ effect, detector vẫn báo), F (no-effect đã xác nhận), {A, F2} | {A, F2}: N = 2, unknown 1, khoảng [0,5; 1,0], verdict UNKNOWN (bản đầu N = 1, PASS). F3/F4 là UNKNOWN_EFFECT; F vẫn rời N |
| RV-03: N = 0 gây TypeError, không có verdict | 3.4: bảng N = 0. EMPTY khi dataset rỗng; NO_ELIGIBLE khi tất cả no-effect đã xác nhận; tỷ lệ/mean không xác định; không bao giờ PASS. Áp chung cho MTTD, MTTR và reaction (3.5) | EMPTY, ALL_NO_EFFECT (chỉ F), ALL_UNKNOWN (F2, F3, F4) | EMPTY / NO_ELIGIBLE / UNKNOWN (N = 3, khoảng [0, 1]); không lỗi |

**Thay đổi kèm theo, cùng lý do:**
- Reaction (3.5) có trạng thái REACTED / NO_SUCCESS / NO_DETECT / MISSING và tổng hợp cùng N. `cap_rec` nay được áp khi đóng reaction; case D2 (SUCCESS tại 650 s) bắt việc này. Bổ sung này phát hiện được vì mutant `react_no_cap` sống sót ở lần chạy đầu.
- Đầu vào case F thêm record đánh giá effect phủ 0–300 s. Expected của F (rời N) không đổi.
- Sửa ô `|W|` trong bảng 5.3 bị vỡ cột do ký tự `|` chưa escape.
- D-01…D-05 giữ nguyên ý; D-05 ghi rõ cận tính bằng hợp khoảng. F-05 thêm W_eff và chuỗi bằng chứng no-effect. Không có quyết định mới cho Hoàng.

**File Claude thay đổi trong lượt này:**
1. Artifact (sửa tại chỗ).
2. Nối mục này vào ghi chú issue.
3. Sửa con trỏ đầu `NOW.md`.
4. Scratch không track:
   - `scratch/zer32/kpi_check.py` v2 (`a635cdf7…bf032`);
   - bản đầu sao lưu `scratch/zer32/v1/kpi_check.py` (`725ab5a3…e9f2`, đúng hash bàn giao trước) và `v1/kpi_check.out`;
   - `scratch/zer32/mutate.py` mới (`59c0fffb…ce422`);
   - output `scratch/zer32/v2/kpi_check.out` (`50a509ca…78791`), `v2/mut_*.out`, bản mutant tạm `v2/mut/*.py`.

   Output cũ `kpi_check.out` và `mut_*.out` ở `scratch/zer32/` giữ nguyên làm lịch sử.

**Kiểm (expected / actual / verdict):**

| Phép kiểm | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| `python scratch/zer32/kpi_check.py` | Expected tính tay khớp | 177/177 OK, exit 0 | PASS (OFFLINE) |
| Hồi quy case cũ | 112 dòng OK của bản đầu có mặt nguyên văn | 112/112 có mặt, 0 dòng mất | PASS |
| `python scratch/zer32/mutate.py` (16 mutant: 7 cũ nhắm lại, 9 mới cho RV-01…RV-03 và cap reaction) | Mọi mutant exit 1 | 16/16 bị bắt, không mutant nào crash | PASS |
| Chạy lại probe Codex `codex_review_check.py` (chỉ đọc, không sửa) | Phản ví dụ cho giá trị đúng | U trong outage: `D_lower_bound` 21 s, UNKNOWN; gap rời hai luồng: U 18 s, UNKNOWN; known + unknown: N = 2, UNKNOWN; bộ “ALL_NO_EFFECT” của probe dùng bản sao A mất effect nên nay là UNKNOWN_EFFECT, N = 1, UNKNOWN, không lỗi. Nhãn `ACTUAL_ADDITIVE_MS` của probe vẫn in D_max + U = 30 s vì probe tự cộng hai trường, không phải giá trị script dùng | PASS |
| Bảng markdown artifact | Mỗi hàng đúng số cột của header | 0 hàng lệch | PASS |
| Đường dẫn `R:/…` trong artifact | Tồn tại | 11/11 | PASS |
| ID ZER trong artifact | Có trong mapping | Không ID lạ | PASS |
| Phủ Pn bắt buộc | Có trong ma trận | Đủ | PASS |
| `git diff --check` | Không lỗi whitespace | exit 0 | PASS |

**N/A:** build, CI, runtime, lab, merge. Không gọi Docker/Kubernetes, attack, healer, LLM hay cloud; không commit/push; không đổi Linear.

**Giới hạn còn lại:**
- Hai cận uptime là cận theo mô hình lấy mẫu; outage ngắn hơn khoảng cách mẫu không được bắt (đã ghi ở 3.7).
- Bộ đánh giá effect trong script dùng chuỗi mẫu dạng probe. Vector dùng metric (CPU) cần ZER-13/ZER-14 khóa chuỗi bằng chứng tương ứng (F-05).
- Containment SQLi chưa mô hình hóa bằng số (F-05).

**Bước tiếp:**
1. Codex retest delta RV-01…RV-03 và hồi quy liên quan.
2. Nếu PASS, Hoàng chấp nhận hoặc sửa D-01…D-05.
3. Chưa Done.

## Chốt audit/fix Codex — ZER-32 — 18/10/2026, 22:43 +07:00

Hoàng yêu cầu Codex tự sửa phần còn lại, không gửi Claude thêm vòng. **READY FOR ACCEPTANCE; không còn finding kỹ thuật mở.** RV-01…RV-03 đã retest và đóng. Codex sửa thêm đầu vào availability rỗng/cửa sổ không hợp lệ (trước đây PASS/crash), và biên xác nhận ổn định ở cap_rec/T_stop; đồng bộ record effect, CPU thiếu mẫu số và câu chữ uptime. Không hạ ngưỡng hoặc đổi SCOPE.

Artifact cuối: SHA-256 eb35f30bdd952ad81ded97d803b7c3cb736cd806dfd09f7a1e13b890646216e9. Checker scratch: ed40ab524c33a8b04374b9b748d6fe8259bac3e252be9e073fc4c9255a8c56f1. HEAD a224ce54fc0e742bbb647c61e6e9201094a9de25, nhánh codex/zer-35-local-lab; không commit.

Kiểm cuối: 190/190 OFFLINE đạt; 18/18 mutant exit 1 có BAD, không crash; phản ví dụ của Codex đúng; link/bảng hợp lệ; git diff --check sạch; hash AGENTS/README/WORKING-AGREEMENT giữ nguyên. Chi tiết actual/expected, hash và giới hạn trong mục “Chốt audit và tự sửa” của [codex-review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md).

D-01…D-05 đã có khuyến nghị cuối, cần Hoàng chấp nhận phương pháp trước khi dùng làm chuẩn downstream; không tự ghi đã được duyệt. F-01…F-09 ở protocol trước formal run. Gói tài liệu đạt review kỹ thuật; build/CI/runtime/merge N/A có lý do. Chưa đổi Linear/publication, chưa coi kiểm offline là KPI nghiên cứu đạt.

## Hoàng chấp nhận — ZER-32 — 18/10/2026, 22:48 +07:00

Hoàng trả lời “được” khi Codex hỏi chấp nhận D-01…D-05 sau audit/fix hoàn chỉnh. **AC-01 ZER-32 / AC-02 ZER-5 được nghiệm thu ở phạm vi tài liệu và kiểm logic offline**; không còn finding kỹ thuật hoặc quyết định D mở. F-01…F-09 vẫn chốt trong protocol trước formal run. Bản kỹ thuật đã review: eb35f30bdd952ad81ded97d803b7c3cb736cd806dfd09f7a1e13b890646216e9. Artifact sau thêm receipt: a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c.

Không đổi công thức, checker hoặc case từ bản 190/190 OFFLINE đạt, 18/18 mutant bị bắt. Không cần chạy lại kiểm số học cho thay đổi ghi nhận chấp nhận. Không commit/push/merge, không chạy lab/model/cloud; trạng thái sống và receipt tracking đọc Linear. Không đóng ZER-5 vì còn phần nguồn/baseline riêng.

**Receipt Linear — 18/10/2026, 22:50 +07:00:** sau Hoàng chấp nhận, cập nhật riêng ZER-32: AC-01 checked, bổ sung receipt nghiệm thu và chuyển Done qua linear_zero_door. Đã đọc lại đúng URL zero-door, trạng thái Done, completedAt 2026-10-18T15:49:46.098Z và nội dung evidence khớp. Không đổi issue cha/assignee/relations.

## Gói giao Claude — ZER-33 — 18/10/2026, 23:10 +07:00

### Mục tiêu, quyền và baseline

Hoàng yêu cầu Codex commit riêng ZER-32 rồi soạn yêu cầu để Claude thực hiện ZER-33. Claude làm trọn gói tài liệu, tự kiểm và sửa các lỗi trong gói trước bàn giao; Codex review độc lập sau đó. Codex nhường quyền ghi checkout khi gửi gói này cho Hoàng; không có thao tác gửi tự động sang Claude.

Ưu tiên thuộc R0: bổ sung baseline/source ledger còn thiếu của ZER-5 sau khi ZER-32 đã được nghiệm thu. Gói này không đòi hỏi lab hoặc inference và không chứng minh G0 hoàn tất. Đọc cả ZER-33 và issue cha ZER-5, không chọn tiếp ZER-37 từ chuỗi consumer.

- Issue: https://linear.app/zero-door/issue/ZER-33/chup-baseline-va-lap-source-ledger ; cha: https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia .
- Codex đọc lại AC ZER-33 qua kết nối linear_zero_door khoảng 23:07 +07:00, 18/10/2026. AC-01 / AC-03 của cha yêu cầu HEAD/dirty/cấu hình; inventory legacy và ledger H01–H08; hash/số dòng từng CSV; timestamp dữ liệu tách timeline Git; phân loại DOCX/xác nhận mới/IDE/chat; kiểm path; giữ raw/handoff; lịch sử/danh tính thiếu nguồn là UNKNOWN. Đọc lại AC sống khi bắt đầu; không có kết nối thì ghi rõ dùng snapshot này, không giả đã đọc live hoặc cài lại MCP.
- ZER-32 đã commit local: 8e7b74f1cacc87387e5f35d078e5b1bb48c318fe, nhánh zer-32-requirements-kpi, đúng 3 file (artifact, review, ghi chú issue này). Chưa push/PR/merge cho commit đó. Artifact đã nghiệm thu SHA-256 a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c; không thay công thức/receipt.
- Checkout giao việc: R:/_Projects/Eurus_Workspace/zero_door ; nhánh zer-33-baseline-source-ledger được tạo từ commit ZER-32 trên. Quy ước mới do Hoàng yêu cầu: nhánh mới đặt theo mã issue, không dùng tiền tố codex.
- Trước khi soạn gói, dirty ngoài ZER-33: AGENTS.md, docs/delivery/NOW.md, docs/delivery/README.md, docs/delivery/WORKFLOW.md và docs/delivery/WORKING-AGREEMENT.md (untracked). Gói soạn này sẽ sửa thêm ghi chú issue hiện tại, con trỏ NOW và quy ước tên nhánh trong WORKING-AGREEMENT. Đây là thay đổi hợp lệ có sẵn, không phải toàn bộ do Claude tạo.
- Claude phải chụp lại branch/HEAD, staged/unstaged/untracked và thời điểm thực tế trước khi viết; không dùng snapshot này thay baseline mới. Không checkout/reset/stash/pull hoặc gom các dirty trên vào gói. Nếu có writer khác, dừng phần ghi để giải quyết ownership; vẫn có thể đọc nguồn an toàn.

### Nguồn cần đọc và phạm vi file/thao tác

Theo README → WORKING-AGREEMENT → NOW → AC/ghi chú này → SCOPE/WORKFLOW; chỉ đọc tham chiếu liên quan, không hydration toàn dự án. Nguồn trực tiếp:

1. docs/delivery/SCOPE.md và docs/handoff/2026-10-17-registration-requirements-excerpt.md: cam kết/xác nhận và bản trích DOCX có hash, vị trí Pn. Đọc bản trích không được tự ghi đã đọc DOCX; chỉ đọc DOCX gốc nếu có đường dẫn nguồn thật, cần thiết và truy cập được.
2. docs/reviews/2026-10-09-antigravity-handoff-review.md: H01–H08 và các nguồn IDE được chỉ cuối file. docs/delivery/reference/audit-findings.md: đính chính C01–C05 và giới hạn lịch sử.
3. docs/handoff/2026-10-09-antigravity-gemini-context-handoff.md cùng handoff/hydration ngày 17/10 được dẫn từ audit-findings: nguồn để phân loại, không phải chứng cứ mọi câu cũ đã đúng. Không sửa các nguồn này.
4. docs/experiments/raw_data/ (tất cả CSV thực có), docs/experiments/analysis/summary_statistics.csv và tài liệu phân tích liên quan. Dự kiến lịch sử 8 raw CSV/40 bản ghi, 5/file là mốc để đối chiếu, không ép kết quả hiện tại khớp.
5. Cấu hình trên đĩa dưới infrastructure/manifests/, infrastructure/helm-values/, cấu hình cluster và pin dependency cần cho baseline; đọc nội dung an toàn, hash theo file, không đọc/đưa giá trị secret vào báo cáo. Phân biệt cấu hình Git với cấu hình đã triển khai chưa được truy vấn. docs/evidence/ZER-35/ và inventory ZER-34 chỉ dùng như bằng chứng đã lưu có thời điểm; không gọi lại lab.
6. Git log/show/diff/ls-files chỉ đọc để kiểm timeline và đường dẫn. Nếu cần xác nhận cơ chế runner/analysis, đọc đúng đoạn nguồn liên quan; GitNexus là điều hướng khi index đủ mới, source hiện tại mới quyết định kết luận. Không chạy runner/analysis hoặc sinh lại biểu đồ.

Allowlist ghi:
- Tạo duy nhất artifact chính docs/evidence/R0-T01-S03/baseline-source-ledger.md.
- Chỉ nối bàn giao ZER-33 ở cuối ghi chú scope-and-criteria.md hiện tại, giữ nguyên toàn bộ lịch sử ZER-32.
- Chỉ sửa con trỏ đầu docs/delivery/NOW.md dẫn artifact/bước Codex review.
- Script kiểm offline nếu cần đặt scratch/zer33/ (gitignored), không thêm framework/test mã ứng dụng. Ghi cách kiểm đủ tái lập trong artifact.

Được đọc file nguồn liên quan và Git, tính SHA-256, parse CSV và đối chiếu số liệu offline. Không sửa raw/handoff/ảnh/report cũ, SCOPE, artifact/review ZER-32, mã/config/CI/manifest hoặc WORKFLOW/WORKING-AGREEMENT/AGENTS/README. Không Docker/Kubernetes, health/attack/healer/reset/LLM, gọi cloud, cài dependency, chạy dataset hay benchmark. Không commit/push/PR/merge, đổi Linear/assignment/relations hoặc gửi tin. Đường dẫn local để Codex review cùng checkout là hình thức bàn giao hiện tại; không bịa link đã xuất bản.

### Nội dung artifact phải đủ để review độc lập

**A. Baseline có thời điểm.** Branch/HEAD đầy đủ, timezone, Git dirty chia staged/unstaged/untracked và các dirty có sẵn so với delta Claude. Liệt kê cấu hình/pin quan trọng kèm path thật, SHA-256 và revision hoặc nhãn dirty. Hash chỉ chứng minh nội dung đã đọc, không chứng minh cấu hình đang chạy. Không cần dump toàn bộ source hoặc mọi biến môi trường.

**B. Inventory dữ liệu legacy.** Mỗi raw CSV một hàng: path chuẩn, SHA-256 bytes gốc, kích thước, header/schema, số dòng vật lý và số bản ghi dữ liệu (không tính header), scenario/mode theo trường thực có, phạm vi timestamp lưu trong dữ liệu, timezone nếu có hoặc UNKNOWN, lỗi parse/thiếu trường và giới hạn. CSV parser xử lý quoted/multiline đúng; không đồng nhất số dòng vật lý với số trial. Có tổng kiểm số file/bản ghi, không coi lỗi đọc hoặc bộ lọc hụt là 0 dữ liệu. Liệt kê summary CSV là dữ liệu dẫn xuất riêng; không cộng nó vào số raw trials. Nếu có file thử bị loại/di chuyển được Git hoặc nguồn chỉ tới, ghi riêng provenance/tình trạng, không đưa vào mẫu formal hay tự di chuyển. Không quét toàn ổ C để tìm lịch sử.

Tách ba lớp: timestamp/filename CSV; thời điểm đưa/sửa/xóa trong Git; thời điểm analysis/chèn hình được nguồn ghi nhận. Không suy ngày thực thi hoặc chất lượng đồng hồ chỉ từ filename, mtime hay commit. Đối chiếu những điểm H03 quan trọng (40 files so với 8 files, ngày 25/06 so với 12–13/07, E3 AUTO FAILED/MTTR, P95 so với max) bằng dữ liệu/nguồn thật. Chỉ tính trực tiếp tối thiểu cần kiểm, không chạy lại pipeline phân tích.

**C. Source ledger.** Mỗi thông tin cần truy nguồn có: nội dung/claim, nguồn và vị trí cụ thể, loại nguồn, ngày của nguồn/ngày sự kiện nếu biết, trực tiếp hay trích qua người khác, mức xác minh, mâu thuẫn/UNKNOWN và tác động đến cách dùng kết quả. Tách DOCX gốc/bản trích có attribution, xác nhận Hoàng có vị trí lưu, code/config, raw CSV, Git, log runtime, báo cáo tự đánh giá/kế hoạch, IDE checkpoint/chat recall và suy luận. Không gắn mọi thứ một nhãn VERIFIED; nguồn tồn tại không làm claim bên trong đúng.

Bao phủ H01–H08 và các đính chính liên quan: ý định/lời duyệt thiếu chat; DOCX tháng 01–06 so với mốc 31/12 theo Hoàng (không suy đã được gia hạn); inventory/timeline; hạn chế MTTR/terminal status; plan khác runtime/LLM/cloud; chức năng script và path cũ; claim RAM/ưu thế chưa đối chứng; danh tính hp8001 chưa xác nhận. Với IDE S12/S13/S14, kiểm đường dẫn được dẫn trong review/handoff nếu truy cập được, ghi đúng artifact/metadata chứ không tự gọi là chat gốc. Nếu file/path/nguồn không có hoặc bị chặn, lưu UNKNOWN và cách đã kiểm, không bịa nội dung hoặc hỏi lại lịch sử không chặn AC.

H01–H08 là đầu mục audit để ledger xử lý; không tự tuyên bố đã đóng mọi lỗi runtime/nghiên cứu hoặc sửa thay các issue khác. Nêu phần được làm rõ bằng nguồn, phần còn UNKNOWN và nơi xử lý downstream nếu đã có mapping; không tự tạo relation/issue. Các nhắc .ps1 trong review thuộc revision cũ, lệnh vận hành hiện tại dùng Bash; không chạy script phục hồi để kiểm một câu lịch sử.

**D. Kiểm chứng và giới hạn.** Có AC-01 ZER-33 / AC-03 ZER-5 → kiểm → expected/actual/verdict, không chỉ checklist đã đọc. Ghi lệnh hoặc thuật toán parse/hash/kiểm path có thể tái lập, lỗi đọc/parse riêng, kết quả diff allowlist và git diff --check. Chụp hash raw/handoff nguồn trước/sau để chứng minh không đổi; các file nguồn khác đã dùng nếu đổi giữa lúc đọc thì ghi biến động và kiểm lại phần bị ảnh hưởng trước khi kết luận. Script nếu có phải bắt được thiếu file/parse lỗi/sai tổng, không chỉ grep câu trong Markdown.

Tự kiểm link/path nội bộ, bảng Markdown, tổng số và mọi con số trong ledger; giữ cả failure/UNKNOWN. Không thêm test ứng dụng cho thay đổi tài liệu. Runtime/model/cloud/CI N/A vì không thuộc thao tác gói, không coi N/A là KPI PASS. Kết luận PARTIAL khi còn thiếu bằng chứng bắt buộc; UNKNOWN được ghi đúng nguồn không tự làm gói thất bại, nhưng không được che nguồn bắt buộc chưa kiểm.

### Bàn giao một gói và điều kiện dừng

Làm xuyên suốt artifact → tự review → sửa lỗi liên quan → kiểm cuối. Trả artifact + SHA-256 cuối, branch/HEAD/dirty và danh sách delta, tóm tắt AC/kết quả/giới hạn; nối receipt ngắn ở cuối ghi chú này, cập nhật NOW rồi nhường writer cho Codex. Codex sẽ đọc toàn ledger, kiểm lại inventory/hash/timeline/attribution và bảo toàn nguồn, gom finding rồi retest phần sửa; không yêu cầu Hoàng ráp các checkpoint.

Chỉ hỏi Hoàng khi có mâu thuẫn làm thay đổi cam kết cần quyết định, quyền vượt allowlist hoặc xung đột writer. Thiếu chat gốc, hồ sơ gia hạn, danh tính hoặc lịch sử cloud được ghi UNKNOWN và tiếp tục phần độc lập, không kéo sang khôi phục tài khoản/cluster. Không tự đóng ZER-33 hoặc ZER-5. Không có quyền publication của ZER-32 áp sang gói này.

## Bàn giao Claude — ZER-33 — 18/10/2026, 23:30 +07:00

**Kết quả: gói đủ để Codex review; đạt theo snapshot AC trong gói giao.** Claude nhường quyền ghi checkout cho Codex. Không tự đóng ZER-33/ZER-5, không đổi Linear, không commit/push.

**Artifact:** [`docs/evidence/R0-T01-S03/baseline-source-ledger.md`](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/baseline-source-ledger.md), SHA-256 `383d0b6cd654bfb3bf1fc61219d62f41e40e99a927fe14adf48bacbefafa79d5`, 494 dòng.

**Baseline và AC.**
- Chụp lúc 23:12:07: nhánh `zer-33-baseline-source-ledger`, HEAD `8e7b74f1cacc87387e5f35d078e5b1bb48c318fe`, staged rỗng. Dirty có sẵn gồm 5 file M và `WORKING-AGREEMENT.md` untracked; giữ nguyên, hash ở mục A.1 của artifact.
- AC sống: Claude không đọc được, vì không có kết nối Linear được phép dùng. Gói dùng snapshot Codex đọc lúc 23:07. Codex cần đối chiếu AC sống.
- DOCX: Claude chỉ kiểm hash file (khớp bản trích); nội dung dùng bản trích do Codex đọc trực tiếp.

**Kết quả chính.**
- **Baseline cấu hình:** 47 file cấu hình/pin sạch, khớp HEAD. Image k3s không được pin. Cấu hình đã triển khai chưa truy vấn.
- **Raw CSV:** 8 file, 48 dòng vật lý, 40 bản ghi, 5 bản ghi/file, 0 lỗi parse. `attack_start` nằm trong 25/06/2026, 15:30:27–15:54:22 UTC. Summary là dẫn xuất; tính lại khớp, chênh tối đa 0,004.
- **File thử 12/07:** tách riêng, gồm blob Git và bản sao trong `scratch/`. Không đưa vào mẫu, không di chuyển.
- **H03 xác nhận:** 8 file/40 bản ghi; dữ liệu ngày 25/06, không phải 12–13/07. E3 AUTO có 4/5 FAILED vẫn mang MTTR 1,01–1,02 s. 9,24 s là P95, max là 11,26 s.
- **Phát hiện mới:**
  - Cột timestamp không tái lập được MTTD/MTTR (lệch tới khoảng 3,3 s).
  - `run_id` lặp giữa AUTO/MANUAL ở E1/E2.
  - 40 lượt chỉ trải khoảng 24 phút, trái lý do “2 phút/lượt” của báo cáo tự đánh giá.
  - Mục CHECKPOINT trong transcript IDE có tóm tắt yêu cầu do IDE sinh, bị cắt cụt; không phải chat gốc.
- **Ledger:** 30 mục L01–L30 phủ H01–H08.
  - UNKNOWN: chat gốc/lời duyệt, hồ sơ gia hạn, danh tính `hp8001`, log cloud/LLM, nguyên nhân E3 FAILED, mã thực sự chạy và chất lượng đồng hồ.

**Kiểm.**
- Script `scratch/zer33/ledger_check.py` (gitignored), SHA-256 `9a116a1c7f56af03978f052286feee4c5316a08cd13644c2be750d3c942148e2`.
- Selftest 10/10 OK: bắt cột thừa, header sai, non-UTF-8, số lỗi, multiline, hàng rỗng, TIMEOUT, thiếu file, đổi hash.
- `run`: 128 OK, 0 FAIL. `compare`: 42 nguồn được bảo vệ không đổi trước/sau.
- 16 link nội bộ hợp lệ; bảng Markdown không lệch cột; `git diff --check` sạch.
- Lệnh tái lập ở mục D.2 của artifact.

**Delta.** Ba file theo allowlist: tạo artifact, nối mục này cuối ghi chú issue, sửa con trỏ đầu `NOW.md`. Ngoài repo chỉ ghi `scratch/zer33/`. Kết quả kiểm allowlist ở mục D.4 của artifact.

**Giới hạn.** Không chạy lab/model/runner/analysis, không gọi Docker/Kubernetes/cloud và không cài dependency. Không tìm toàn repo hoặc toàn ổ C. Build/CI/runtime N/A vì gói chỉ tạo tài liệu; N/A không phải KPI PASS.

**Tiếp theo.** Codex review toàn ledger, kiểm lại inventory/hash/timeline/attribution và đối chiếu AC sống. Sau review, Hoàng quyết định nghiệm thu.

## Codex review và sửa gọn — ZER-33 — 18/10/2026, 23:42 +07:00

**PASS về kỹ thuật tài liệu; chờ Hoàng nghiệm thu.** Codex đã đối chiếu AC sống ZER-33/ZER-5 qua đúng linear_zero_door và review toàn gói; [báo cáo](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/codex-review.md). Bản nhận 383d0b6c…fa79d5 có một P2 (RV-01): L20/C.4 dẫn tạo/start sang script recreate có xóa cluster. Codex sửa đúng hai hàng 307/330 để dẫn setup-phase1.sh --component cluster và phân biệt nhánh xóa cần quyền riêng; không chuyển thêm vòng Claude. Artifact cuối SHA-256 cbbd334caaeb3e03513939f1ab3563883073d48f38b487087e68ae67a0bb029d.

Retest: selftest 10/10, run 128 OK/0 FAIL, compare 42/42 nguồn không đổi, link 16/16; exit từng lệnh 0. Kiểm độc lập hash 47 cấu hình, parser JS 8 CSV/40 bản ghi và số liệu/timeline/ảnh/attribution đều khớp. Sau sửa chỉ dẫn nguồn: kiểm đúng delta, bảng/link và bảo toàn; không cần chạy lại suite số học không đổi. ZER-32 giữ nguyên hash. Không chạy lab/model/runner/analysis, không đổi Linear hoặc commit/push. Các UNKNOWN lịch sử/đồng hồ/danh tính/hồ sơ vẫn giữ; PASS này không là runtime/G0.

## Hoàng nghiệm thu và cấp quyền publication — ZER-33 — 18/10/2026

Hoàng trả lời “đưuọc commit push rồi hoàn thành linear” sau review PASS. Chấp nhận kết quả baseline/source ledger và cho phép commit/push gói ZER-33, ghi receipt nghiệm thu rồi chuyển riêng ZER-33 Done trên Linear. Artifact cuối SHA-256 cbbd334caaeb3e03513939f1ab3563883073d48f38b487087e68ae67a0bb029d, không thay nội dung so với bản review cuối. Giới hạn UNKNOWN và N/A runtime vẫn giữ.

Publication dùng nhánh zer-33-baseline-source-ledger, cha 8e7b74f1cacc87387e5f35d078e5b1bb48c318fe (ZER-32). Allowlist commit: artifact và codex-review.md dưới docs/evidence/R0-T01-S03/, cùng ghi chú issue hiện tại. Không gom dirty quy ước/NOW/README/AGENTS, không commit scratch. Receipt commit remote và read-back Linear lưu trên issue sau push; không merge hoặc tự đóng issue cha ZER-5.

## Đối chiếu nghiệm thu ZER-5 — Claude — 19/10/2026, 08:00 +07:00

**Kết luận: cả ba AC của ZER-5 có căn cứ kỹ thuật để nghiệm thu; đề nghị Codex review rồi Hoàng quyết định.** Hai issue con ZER-32 và ZER-33 Done không tự đóng issue cha. Nghiệm thu ZER-5 và cập nhật Linear là bước riêng của Hoàng/Codex. Claude không đổi Linear, không commit.

**Phạm vi và nguồn.** Thực hiện trong gói “Gói Claude — ZER-8 và đối chiếu ZER-5” cuối [research-questions.md](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md). Baseline 07:45 +07:00: nhánh zer-34-lab-acceptance, HEAD 968cc50f3797c243b8fa26e5327db647a8644802, staged rỗng; dirty có sẵn ghi ở artifact ZER-8. Claude không đọc được AC sống vì phiên không có linear_zero_door. AC dùng ở đây là ba mục R0-T01-S01…S03 trong [mapping](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/mapping.json) cùng cách đánh số đã dùng trong review ZER-32/33: AC-02 ứng với ZER-32, AC-03 ứng với ZER-33. Codex cần đối chiếu AC sống. Không làm lại ma trận KPI hay ledger đã nghiệm thu.

| AC ZER-5 (snapshot) | Nguồn / file / revision | Bằng chứng đã chấp nhận | Kiểm lại lượt này | Kết luận và khoảng trống |
| --- | --- | --- | --- | --- |
| AC-01 — ghi nhận phạm vi đã chốt: Python/Go, Online Boutique, ba vector, KPI, bài được chấp nhận đăng | [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) dòng 7 (Python/Go, Boutique), 9 (ba vector, scale/block/rollback, MTTD/MTTR/uptime), 10 (≥5 microservices, P104), 11 (giữ ba vector, quyết định 17/10), 12 (P179/P187/P100/P109/P176 và sản phẩm), 13 (chấp nhận đăng trước nghiệm thu). SHA-256 f73c38d9e9658ddbdbf063ab4c94c80f90fce3faa7af4c448f157711fb4d51c2, revision 1f43ff1, có trong origin/main. [Bản trích DOCX](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md) P104–P109, P208–P211 | ZER-32 RM-01, RM-02, RM-07…RM-10, RM-19…RM-21 truy vết đủ các cam kết này tới phép thử; Hoàng đã nghiệm thu ZER-32 | Đọc từng dòng SCOPE và bản trích; đối chiếu RM tương ứng. Python/Go là USER, khác P208 Java Spring Boot; SCOPE và RM-19 đã ghi lý do. Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX | **Đạt ở mức ghi nhận phạm vi.** Tên kỷ yếu, mẫu và lịch nhận bài còn UNKNOWN; đó là việc của ZER-57, không phải thiếu ghi nhận. Chênh lệch thời hạn tháng 01–06 với 31/12 đã ghi ở SCOPE và ledger ZER-33; đối chiếu hồ sơ ở ZER-64 |
| AC-02 — ma trận yêu cầu → phép thử; MTTD, MTTR, downtime, uptime, mẫu số | [requirements-and-kpi.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md), SHA-256 a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c; [review và receipt](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/codex-review.md), SHA-256 f7c2454e79b8c22d773a3c800abf1778e4be2ef408e886fc902757027098bb16; commit 8e7b74f | Codex review: 190/190 OFFLINE, 18/18 mutant. Hoàng chấp nhận D-01…D-05 lúc 22:48 ngày 18/10. Receipt ghi ZER-32 Done, completedAt 2026-10-18T15:49:46.098Z | Hash file trên đĩa và blob tại 8e7b74f đều khớp a5579b90…; sạch so với HEAD. 13 link local trong artifact và 4 trong review tồn tại. Ngưỡng 60 s, 120/180 s, 99,9% còn nguyên | **Đạt.** F-01…F-09 thuộc protocol ZER-53, không chặn AC-02. Semantics FPR của RM-22 nay có đề xuất ở artifact ZER-8, chờ review |
| AC-03 — baseline Git/cấu hình, inventory legacy, source ledger H01–H08 | [baseline-source-ledger.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/baseline-source-ledger.md), SHA-256 cbbd334caaeb3e03513939f1ab3563883073d48f38b487087e68ae67a0bb029d; [review](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/R0-T01-S03/codex-review.md), SHA-256 96ab89ce2def895d59205f025c3424ff87a402b8c31b91126e15915b3b177d7e; commit 10a26b0 | Codex review PASS sau sửa RV-01. Hoàng nghiệm thu 18/10. NOW ghi ZER-33 Done, completedAt 2026-10-18T16:58:27.655Z | Hash file và blob tại 10a26b0 khớp; sạch so với HEAD. 16 link local trong artifact và 1 trong review tồn tại. 9 CSV dưới docs/experiments giữ hash trong suốt lượt này | **Đạt.** Các UNKNOWN lịch sử (chat gốc, hồ sơ gia hạn, danh tính hp8001, log cloud/LLM, nguyên nhân E3 FAILED, chất lượng đồng hồ) là giới hạn nguồn đã ghi đúng theo AC |

**Publication.** Đọc Git chỉ đọc khoảng 07:50 +07:00 (git ls-remote): origin/zer-33-baseline-source-ledger ở 10a26b0, origin/zer-34-lab-acceptance ở 968cc50; cả hai chứa 8e7b74f và 10a26b0. origin/main ở 5471b58 chưa chứa hai commit này; nhánh zer-32-requirements-kpi không có trên remote. Theo WORKFLOW, issue tài liệu có thể ghi merge là N/A có lý do; việc có mở PR đưa các commit tài liệu vào main hay không là quyết định publication riêng, không chặn nghiệm thu ZER-5.

**Đề nghị.** Codex đối chiếu AC sống và receipt Linear của ZER-32/33. Nếu khớp, Hoàng nghiệm thu ZER-5, rồi cập nhật Linear trong quyền được giao. Nghiệm thu ZER-5 không chứng minh G0: còn ZER-8 (đang review) và ZER-36/ZER-7 (backend LLM thật).


## Codex đối chiếu nghiệm thu ZER-5 — 19/10/2026, 08:08 +07:00

**PASS kỹ thuật cả ba AC; chờ Hoàng nghiệm thu, chưa đổi Linear/publication.** Đã đọc live ZER-5 (In Progress), ZER-32/33 (Done, AC checked, receipt/completedAt khớp) qua linear_zero_door. Bảng Claude ở trên khớp AC sống và SCOPE dòng 7–13; artifact/review 32/33 có hash và byte blob tại 8e7b74f/10a26b0 khớp file hiện tại, SCOPE khớp 1f43ff1. Không có delta vào các nguồn đã nghiệm thu, không làm lại baseline hay phép đo cũ.

AC-01 đạt ghi nhận cam kết và nguồn xác nhận; AC-02 đạt ma trận/định nghĩa, D-01…D-05 giữ hiệu lực và F-01…F-09 còn đúng ownership; AC-03 đạt ledger/baseline/bảo toàn raw và UNKNOWN lịch sử. Không còn finding chặn nghiệm thu tài liệu ZER-5. Review chi tiết được lưu local ở `docs/evidence/ZER-8/research-design.md`, mục 11 (ngoài publication ZER-5); retest độc lập 45/45 gồm kiểm blob/hash, 71 nguồn bảo toàn. Nghiệm thu cha là quyết định riêng, không tự suy từ con Done. Không có bằng chứng backend hay G0 mới.


## Hoàng nghiệm thu ZER-5 — 19/10/2026, 08:14 +07:00

Hoàng trả lời “được” sau khi Codex báo PASS kỹ thuật cả ba AC và hỏi chấp nhận nghiệm thu ZER-5 cùng hướng thiết kế ZER-8. **ZER-5 đã được Hoàng nghiệm thu về kết quả tài liệu**: AC-01 ghi nhận SCOPE/cam kết; AC-02 ma trận và định nghĩa ZER-32; AC-03 baseline/source ledger ZER-33. Căn cứ review và hash nguồn ở mục Codex đối chiếu ngay trên; không có thay đổi artifact 32/33, không chạy lại lab hay suy KPI/G0 đạt.

Quyền vừa cấp là nghiệm thu kết quả; chưa bao gồm commit/push hay cập nhật Linear. Giữ trạng thái Linear như đã đọc cho tới khi có quyền tracking phù hợp; không ghi nghiệm thu local thành receipt Done sống. Publication tài liệu là bước riêng.


## Publication và đối chiếu cuối ZER-5 — 19/10/2026, 08:21 +07:00

Hoàng yêu cầu trực tiếp: “kiểm tra zer 5 xong chưa cập nhật lại status của nó trên linear (nhớ commit push nếu cần)”. Quyền này bổ sung cho nghiệm thu kết quả lúc 08:14: commit/push đúng tài liệu ZER-5 và cập nhật riêng issue đó trên Linear Zero Door. Không bao gồm publication ZER-8, đổi issue khác hoặc đóng milestone R0.

**Baseline và scope.** HEAD `968cc50f3797c243b8fa26e5327db647a8644802`, nhánh `zer-34-lab-acceptance`, staged rỗng. Dirty có sẵn: AGENTS, README, WORKFLOW, NOW, research-questions, ghi chú này; WORKING-AGREEMENT và artifact ZER-8 untracked. Publication dùng nhánh `zer-5-scope-acceptance`; allowlist commit chỉ ghi chú `docs/delivery/milestones/R0-foundations/scope-and-criteria.md`. NOW chỉ được cập nhật con trỏ local, không gom lịch sử dirty của các gói khác vào commit.

**Đối chiếu cuối trước publication.** Đọc lại AC sống ZER-5 và hai issue con qua `linear_zero_door`, URL thuộc `linear.app/zero-door/`: ba AC không đổi; ZER-32/33 Done và AC đã checked. Năm nguồn SCOPE, artifact/review ZER-32 và artifact/review ZER-33 có SHA-256 khớp chính xác bảng nghiệm thu ở trên, sạch so với HEAD; hai commit nghiệm thu con đều là tổ tiên HEAD. Không có thay đổi phương pháp/số liệu phải chạy lại suite offline.

| AC | Kết luận cuối và nguồn đã xuất bản |
| --- | --- |
| AC-01 | PASS: phạm vi Python/Go, Boutique, ba vector, KPI, sản phẩm và chấp nhận đăng được ghi tại [SCOPE ở revision nguồn](https://github.com/EurusDevSec/Zero-Door/blob/1f43ff1461c2199bc99e9962483956c3df0fa975/docs/delivery/SCOPE.md); hash f73c38d9e9658ddbdbf063ab4c94c80f90fce3faa7af4c448f157711fb4d51c2 |
| AC-02 | PASS: [ma trận và định nghĩa ZER-32](https://github.com/EurusDevSec/Zero-Door/blob/8e7b74f1cacc87387e5f35d078e5b1bb48c318fe/docs/evidence/ZER-32/requirements-and-kpi.md), [review và chấp nhận D-01…D-05](https://github.com/EurusDevSec/Zero-Door/blob/8e7b74f1cacc87387e5f35d078e5b1bb48c318fe/docs/evidence/ZER-32/codex-review.md); 190/190 OFFLINE và 18/18 mutant là bằng chứng lịch sử đã nghiệm thu, không phải runtime mới |
| AC-03 | PASS: [baseline/source ledger ZER-33](https://github.com/EurusDevSec/Zero-Door/blob/10a26b0a0001046b23f57f667a3cb7be33e69090/docs/evidence/R0-T01-S03/baseline-source-ledger.md), [review/nghiệm thu](https://github.com/EurusDevSec/Zero-Door/blob/10a26b0a0001046b23f57f667a3cb7be33e69090/docs/evidence/R0-T01-S03/codex-review.md); các UNKNOWN về nguồn/lịch sử được bảo toàn đúng AC |

**Kết luận:** không còn finding hoặc quyết định chặn ZER-5. Hoàng đã chấp nhận cả ba AC; đủ điều kiện chuyển riêng ZER-5 Done sau khi push và đọc lại remote. Build/test ứng dụng, CI bắt buộc và merge N/A có lý do: đây là gói nghiệm thu tài liệu, không sửa mã; không tạo PR hay merge. Kiểm mới giới hạn ở hash/ancestry/diff/link và bảo toàn dirty ngoài scope.

Commit SHA, artifact remote và receipt Done/completedAt sẽ lưu trên issue Linear sau khi push/read-back thành công; phần này không tự tuyên bố thao tác chưa diễn ra. ZER-8 AC-02, backend ZER-36/ZER-7 và nghiệm thu G0 vẫn là các phần riêng còn mở. Không chạy lab/API/model/cloud hoặc chi tiền.
