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
