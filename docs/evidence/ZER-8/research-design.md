# ZER-8 — Thiết kế nghiên cứu, đối chứng và cách chấm

[Ghi chú issue và gói giao](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md) · Issue: [ZER-8](https://linear.app/zero-door/issue/ZER-8/khoa-cau-hoi-nghien-cuu-va-thiet-ke-djoi-chung) · Định nghĩa KPI đã nghiệm thu: [ZER-32](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md)

**Người soạn:** Claude, 19/10/2026, từ 07:45 +07:00; giờ chốt ghi ở bàn giao cuối ghi chú issue.

**Trạng thái.** Đây là **thiết kế đề xuất** để Codex review và Hoàng nghiệm thu. Nó chưa phải:
- protocol đã khóa: số lặp, tham số và tập action cụ thể khóa ở [ZER-53](https://linear.app/zero-door/issue/ZER-53/khoa-protocol-truoc-thuc-nghiem-chinh-thuc);
- schema runtime: tên trường ở mục 5.6 là contract đề xuất cho ZER-9/ZER-37;
- kết quả thực nghiệm: mọi con số ở mục 4.4 và mục 6 là giả định OFFLINE.

**Cập nhật nghiệm thu 19/10, 08:14 +07:00:** Hoàng đã chấp nhận hướng giữ B3 có điều kiện, M1 làm metric chính và B2 báo KPI phục hồi; xem mục 12. Nguồn lực pilot và cách tổ chức BM đã được Hoàng chốt ở mục 13 ngày 19/10; formal chốt sau pilot. Các nhãn PROP/PENDING trước mục 12 giữ lịch sử bản đề xuất; không suy đã cấp quyền chạy lab/API hoặc publication.

**Baseline.** Git Bash lúc 07:45:22 +07:00:
- Nhánh `zer-34-lab-acceptance`, HEAD `968cc50f3797c243b8fa26e5327db647a8644802`, staged rỗng.
- Dirty có sẵn: `AGENTS.md`, `docs/delivery/NOW.md`, `docs/delivery/README.md`, `docs/delivery/WORKFLOW.md`, `docs/delivery/milestones/R0-foundations/research-questions.md` (M) và `docs/delivery/WORKING-AGREEMENT.md` (untracked).
- NOW và research-questions mang gói Codex soạn lúc 07:42. Claude chỉ nối thêm vào hai file đó, không sửa phần có sẵn.

**AC.** Claude chưa đọc được AC sống. Phiên này không có kết nối `linear_zero_door`, và gói cấm dùng connector thay thế. Snapshot dùng để làm:
- ba mục checklist R0-T04-S01…S03 trong [mapping Linear](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/linear/mapping.json) (APPLIED_VERIFIED, read-back 17/10);
- diễn giải AC trong gói Codex 07:42, soạn sau khi Codex đọc Linear ngày 19/10.

Codex cần đối chiếu AC sống khi review.

**DOCX.** Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX. Xem [bản trích](R:/_Projects/Eurus_Workspace/zero_door/docs/handoff/2026-10-17-registration-requirements-excerpt.md).

**Nguồn trực tiếp** (SHA-256 lúc đọc; mọi file sạch so với HEAD trừ chỗ ghi):

| Nguồn | SHA-256 | Revision |
| --- | --- | --- |
| [SCOPE](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/SCOPE.md) | `f73c38d9…4d51c2` | 1f43ff1 |
| [research-design](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/research-design.md) | `ab0de7be…c10709` | 1f43ff1 |
| [verification](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/verification.md) | `d65b38ab…7261f7` | 1f43ff1 |
| [scenario-design](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/scenario-design.md) | `77c4c6f3…c6187d` | 1f43ff1 |
| [ai-provider](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/ai-provider.md) | `34f7db4a…dd31a3` | 1f43ff1 |
| ZER-32 artifact đã nghiệm thu | `a5579b90…ba3a24c` | 8e7b74f |
| Bản trích DOCX | `819f5794…fa185d` | 1f43ff1 |
| [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md) | `ded0fdee…f15ffb` | dirty có sẵn |
| [WORKING-AGREEMENT](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKING-AGREEMENT.md) | `fc34c9ae…64bc87` | untracked có sẵn |

Ghi chú downstream chỉ đọc phần đầu ra để dẫn đúng ID: [event-contract](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/event-contract.md), [single-agent-baseline](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/single-agent-baseline.md), [multi-agent-evidence](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/multi-agent-evidence.md), [pilot-and-war-game](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/pilot-and-war-game.md). Không đọc source ứng dụng; tên action ở đây là loại hành động theo P106, enum thật do ZER-50 khóa.

## 0. Kết luận

| AC ZER-8 (snapshot) | Kết quả | Trạng thái đề xuất |
| --- | --- | --- |
| AC-01 — RQ1–RQ3, đóng góp dự kiến, giới hạn claim | Mục 2–3: hai mạch kết quả, bảng RQ → so sánh → metric → claim, quy tắc báo chênh lệch/độ bất định, thang claim | Hướng metric/claim đã được Hoàng chấp nhận ở mục 12; chờ nghiệm thu toàn gói/publication |
| AC-02 — khóa B0/B1/B2, giữ BM; quyết định B3 và budget | Mục 4: ma trận năm nhóm, bất biến công bằng, phiếu quyết định B3 có công thức nhu cầu | **Đủ ở mức thiết kế R0 sau mục 12–13**: B3 có điều kiện, budget pilot và BM đã chốt; formal theo ZER-53 sau pilot; chưa phải Done/publication |
| AC-03 — ground truth, tập action đúng, ranh giới không lộ đáp án | Mục 5–6: nhãn C0–C5, quy tắc action có điều kiện, mẫu số từng metric, ba mặt dữ liệu, kênh rò và cách thử; 10 ví dụ OFFLINE | Đủ để review; là contract đề xuất cho ZER-9/37 |

Ba điểm thiết kế cần chú ý khi review:
1. **B0 không có detector của ZERO DOOR.** MTTD cần cả T_eff và T_det; MTTR và reaction bắt đầu từ T_det, nên cả ba không xác định cho B0 khi không có T_det. So sánh phục hồi giữa các nhóm phải dùng tỷ lệ phục hồi được xác minh và TotalRecovery tính từ effect. MTTR của B0 không được ghi là 0 hay “nhanh hơn”.
2. **B1, B2 và B3 dùng chung detector** (theo [ai-provider](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/ai-provider.md): mốc phát hiện không chờ LLM). Vì vậy MTTD gần như không phân biệt các nhóm này. Giá trị LLM, nếu có, phải hiện ở quyết định, phục hồi và chi phí.
3. **BM có thể lộ đáp án.** Nếu người vận hành thủ công biết lịch case, họ có ground truth mà bên tự động không có. Cách xử lý cần Hoàng chọn (mục 8).

## 1. Nhãn nguồn

| Nhãn | Nghĩa |
| --- | --- |
| **SRC** | Câu chữ thuyết minh qua bản trích (Pn) |
| **USER** | Xác nhận của Hoàng ghi trong SCOPE, NOW hoặc gói giao |
| **PLAN** | Quy tắc đã có trong research-design, verification, scenario-design |
| **ACC** | Quy ước ZER-32 đã được Hoàng nghiệm thu (D-01…D-05 và các quy tắc RV-01…RV-03) |
| **PROP** | Đề xuất của tài liệu này; cần chấp nhận, chưa phải quyết định |
| **PENDING** | Quyết định thật của Hoàng còn thiếu (mục 8) |
| **OFFLINE** | Ví dụ giả định để thử cách chấm; không phải dữ liệu lab |
| **ILLUSTRATIVE** | Số giả định để minh họa công thức nhu cầu; không phải budget hay số đo |
| **UNKNOWN** | Chưa có nguồn; không suy thành PASS hay 0 |

## 2. Hai mạch kết quả

Theo PLAN research-design: đáp ứng thuyết minh và trả lời câu hỏi nghiên cứu là hai điều kiện riêng.

| Mạch | Câu hỏi | Bằng chứng | Được kết luận | Không được suy ra |
| --- | --- | --- | --- | --- |
| Thuyết minh: chức năng, KPI, sản phẩm | Hệ thống có làm được và đạt ngưỡng đã đăng ký không | RM-01…RM-22 của ZER-32; KPI theo D-01…D-05 (ACC) | Đạt, không đạt hoặc UNKNOWN cho từng KPI trên cấu hình được báo | LLM có giá trị; chia vai trò có lợi; tốt hơn quy tắc |
| Nghiên cứu: RQ1–RQ3 | LLM và chia vai trò có tạo khác biệt đo được không, với đánh đổi gì | Đối chứng mục 4, chấm mục 5, phân tích mục 3.2 | Chênh lệch có hướng kèm độ bất định, trên case và lab đã đo | KPI thuyết minh đạt; tổng quát ngoài phạm vi đo |

**PROP:** KPI phục hồi của thuyết minh (P107, P108, P187) báo chính trên **B2**, vì đó là cấu hình ZERO DOOR đầy đủ. B1, B3 và BM báo cùng định nghĩa để đối chiếu. B0 chỉ báo các đại lượng xác định được (mục 4.1). P179 (CPU > 80%) là KPI hiệu lực tấn công, không phải KPI phục hồi: đo trước khi phòng thủ có tác dụng hoặc trong B0, theo pha chốt ở F-06 (ACC ZER-32 mục 3.8).

Hai mạch có thể cho kết quả khác chiều. Ví dụ B2 và B1 đều đạt MTTR < 180 s: thuyết minh đạt, nhưng KPI đó không chứng minh LLM có giá trị. Ngược lại, B2 không hơn B1 vẫn là kết quả nghiên cứu hợp lệ nếu phép đo hợp lệ. Không mạch nào yêu cầu AI thắng.

## 3. AC-01 — Câu hỏi, metric và claim

### 3.1 Bảng RQ → so sánh → metric → claim

Giữ nguyên nghĩa ba RQ của research-design. Metric chính là **PROP**, cần Hoàng chấp nhận hướng phân tích tại R0; phiên bản protocol số hóa khóa trước formal ở ZER-53. Định nghĩa từng metric và mẫu số ở mục 5.5.

| RQ | So sánh | Đơn vị phân tích | Metric chính (PROP) | Metric phụ | Dữ liệu tối thiểu |
| --- | --- | --- | --- | --- | --- |
| RQ1 — giá trị LLM | B2 với B1 (chính); B2 với B0 (hạ tầng tự phục hồi được đến đâu); B2 với BM (chỉ khi kết luận về thủ công) | Incident trong khối ghép cặp (case, variant, seed); mỗi nhóm chạy cùng khối | M1: độ đúng quyết định đầu tiên trước guard, trên incident cần quyết định của tập dễ nhầm C1–C4, trung bình macro theo lớp | M7 tỷ lệ phục hồi được xác minh; M8 đường TotalRecovery; M9 KPI; M10 decision latency; M11 call/token/cost; M5–M6 ở C0; M12 containment C2/C5; kết quả riêng từng lớp | Cùng khối cho B1/B2; giữ mọi failure/timeout/missing; pilot ZER-51/52 trước formal; số lặp do ZER-53 khóa |
| RQ2 — giá trị chia vai trò | B2 với B3, cùng model, evidence, tools, guard và trần call/token | Như RQ1 | Như RQ1, M1 | M7, M10; M11 tính theo incident (overhead phối hợp); tỷ lệ schema sai và fallback | Chỉ khi B3 chạy formal trên cùng khối với B2 |
| RQ3 — giới hạn guard/fallback | Mô tả trên B1, B2 (và B3 nếu chạy); không cần nhóm thắng | Đề xuất (cho guard); incident (cho fallback); slot và giờ benign (cho C0) | Không có một metric chính: báo đủ M3, M4, M5, M6 và tác động lên benign | Kiểu hỏng còn lại theo lớp; hành động có hại; recovery khi fallback | Mọi đề xuất trước guard được lưu; mọi fallback được đánh dấu; cửa sổ C0 đủ dài |

| RQ | Được kết luận | Chưa được kết luận |
| --- | --- | --- |
| RQ1 | “Trên các case X, B2 chọn đúng k₂/N, B1 chọn đúng k₁/N; chênh lệch Δ, khoảng 95% [a, b]”; đánh đổi latency/token/cost đo được | “LLM tốt hơn quy tắc” nói chung; ngoài case và lab đã đo; gán phục hồi do fallback RULES hoặc HPA cho LLM; coi CI chứa 0 là “tương đương” |
| RQ2 | Nếu có B3 formal: chênh lệch B2 với B3 trên case đã đo, kèm overhead call/token thực tế | Lợi ích của toàn bộ ba tác tử hay riêng Nemesis; ưu thế chia vai trò khi chưa chạy B3; ép số call bằng nhau rồi so |
| RQ3 | Tần suất guard chặn đúng/sai, fallback và hệ quả, hành động thừa trên benign, kèm mẫu số | “Guard bảo đảm an toàn”; guard chặn biến đề xuất sai thành đúng; fallback thành công là AI thành công |

Vì sao M1 là metric chính của RQ1/RQ2: phục hồi phụ thuộc chung vào executor, HPA và controller ở mọi nhóm. Độ đúng của quyết định là phần LLM thực sự thay đổi. M7/M8 vẫn bắt buộc báo cạnh M1, để quyết định đúng mà không phục hồi không bị che.

### 3.2 Quy tắc báo chênh lệch và độ bất định (PROP)

1. **Khóa trước formal:** RQ, metric chính mỗi RQ, tập action, mẫu số, rules/prompt/model/temperature và phiên bản script phân tích. Dữ liệu pilot ZER-51/52 không trộn vào formal.
2. **Ghép cặp và thứ tự:** mỗi khối (case, variant, seed) được phát lại cho mọi nhóm. Thứ tự nhóm trong khối xen kẽ theo seed ghi lại. Mỗi trial bắt đầu sau reset đã xác minh.
3. **Tỷ lệ và cặp:** báo tử/mẫu số cùng cận do thiếu dữ liệu của từng lớp và nhóm. Khi có nhãn nhị phân đầy đủ và đơn vị độc lập phù hợp, có thể dùng Wilson 95% cho k/N; không gọi cận [đạt/N, (đạt + chưa rõ)/N] là khoảng tin cậy. Giữ mọi khối đã lên lịch, kể cả no-effect/missing khác nhau giữa hai nhóm. Không lập bảng 2×2 nhị phân cho cặp có một vế UNKNOWN/không đủ điều kiện; báo riêng số cặp đầy đủ, cặp bất đối xứng và cận/sensitivity. Chênh lệch B2−B1 hoặc B2−B3 dùng trọng số lớp cố định; bootstrap theo khối ghép cặp trong từng lớp, giữ các trial phụ thuộc trong cùng khối. Số vòng, seed và xử lý lớp rỗng khóa trước formal ở ZER-53; không bỏ lớp rỗng rồi đổi trọng số hoặc tự gọi mẫu độc lập. Bảng 2×2 chỉ mô tả các cặp chấm được, luôn kèm coverage.
4. **Thời gian giữa nhóm:** không so mean MTTR khi tỷ lệ phục hồi khác nhau. Với t ≤ cap_rec, báo R_lower(t) = số lượt có TotalRecovery hợp lệ ≤ t / N và R_upper(t) = (số đó + số lượt chưa rõ có thể đã phục hồi trước t) / N. UNKNOWN_EFFECT không có mốc effect để tính TotalRecovery; missing probe/clock hoặc mất quan sát trước t cũng không phải timeout đã quan sát đủ. Chỉ lượt có bằng chứng không phục hồi tới t mới được coi là chưa phục hồi chắc chắn. Khi không có lượt chưa rõ, hai cận trùng thành R(t). Cùng cap_rec không tự loại sai lệch do missing hoặc dừng quan sát sớm; không tuyên bố “không lệch do censoring”. Báo cận tại 120 s, 180 s và cap_rec. Median là điểm đầu R(t) đạt 0,5 khi xác định được; nếu R_upper(cap_rec) < 0,5 thì median > cap_rec; nếu R_lower(cap_rec) < 0,5 ≤ R_upper(cap_rec) thì median UNKNOWN hoặc chỉ báo khoảng xác định được; nếu R_lower(cap_rec) ≥ 0,5 thì biết median ≤ cap_rec nhưng vẫn cần đường theo thời gian để xác định điểm. Ví dụ 4/10 recovered, 2/10 missing ở cap cho [0,4; 0,6], không đủ để nói median > cap. Mốc 120/180 s ở đây từ effect, **không thay KPI MTTR** tính từ detect.
5. **Thiếu dữ liệu:** giữ nguyên quy tắc ZER-32 (ACC). Lượt UNKNOWN_EFFECT, UNKNOWN_GT hoặc MISSING ở lại mẫu số; báo ước lượng chính trên N cùng khoảng [đạt/N, (đạt + chưa rõ)/N].
6. **Diễn đạt:** khoảng chứa 0 thì viết “chưa phát hiện khác biệt trong phạm vi đo”, không viết “tương đương”. P95/P99 từ mẫu nhỏ chỉ là thăm dò. Phân tích phụ hoặc thăm dò phải gắn nhãn; không chọn metric sau khi thấy kết quả.
7. **Số lượt:** không khóa ở đây. ZER-52 ước lượng biến thiên và thời gian/chi phí mỗi trial. ZER-53 khóa số lặp, ví dụ theo độ rộng khoảng tin cậy mong muốn cho metric chính. Nếu nguồn lực không đủ, ghi formal là nghiên cứu mô tả. Không tuyên bố “đủ mẫu” hay “có ý nghĩa thống kê” khi chưa có tính toán tương ứng.
8. **Không bắt buộc AI thắng.** B2 bằng hoặc kém B1 vẫn được báo đầy đủ, claim đi theo dữ liệu (PLAN verification #7).

### 3.3 Đóng góp dự kiến và thang claim

Đóng góp dự kiến giữ như research-design: cơ chế phối hợp tác tử với hành động có giới hạn, bằng chứng vận hành và xác minh phục hồi nghiệp vụ, cùng dữ liệu đối chứng về khi nào LLM hữu ích. Đây là dự kiến, chưa phải kết quả.

| Dữ liệu đã có | Claim được phép |
| --- | --- |
| Chỉ chức năng và KPI trên một cấu hình | “Trên lab này, hệ thống đạt/không đạt KPI X với mẫu số N”; không nói gì về giá trị LLM |
| Thêm B0/B1/B2 formal | Trả lời RQ1 trên case đã đo, có chênh lệch và độ bất định |
| Thêm B3 formal | Trả lời RQ2 trên case đã đo |
| Thêm tổng quan tài liệu [ZER-56](https://linear.app/zero-door/issue/ZER-56/djoi-chieu-nghien-cuu-lien-quan-va-gioi-han-tinh-moi) | Định vị so với AIOpsLab, ITBench và công trình khác |

Trước khi ZER-56 hoàn tất, không dùng “mới”, “đầu tiên” hay “vượt trội”. Research-design đã ghi điều này; artifact chỉ nhắc lại để ZER-26 dùng đúng.

## 4. AC-02 — Đối chứng và phạm vi B3

### 4.1 Ma trận nhóm

| Nhóm | Phát hiện | Phân tích và quyết định | Thực thi | Guard | Đầu vào bên quyết định | Biên chi phí | Metric N/A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B0 K8S_BASELINE | Không có detector ZERO DOOR (PROP tùy chọn ở dưới) | Controller Kubernetes và HPA theo profile chung; ZERO DOOR không ra quyết định | Kubernetes | N/A | N/A | Không LLM; thời gian lab | MTTD, MTTR, reaction (nếu không chạy detector quan sát); M1–M4, M10, M11. Ghi N/A, **không** ghi 0 |
| B1 RULES | Detector chung | Policy quy tắc, hiệu chỉnh ở pilot rồi khóa | Executor/healer chung | Guard chung | Gói evidence chung | Không LLM | Token/cost LLM, M4 fallback |
| B2 MULTI_LLM | Detector chung | Gaia phân tích bằng LLM; Hephaestus chọn action trong enum bằng LLM | Executor chung | Guard chung | Gói evidence chung | Call/token theo tác tử, trong trần chung mỗi incident | — |
| B3 SINGLE_LLM (nếu giữ) | Detector chung | Một agent LLM gộp phân tích và chọn action | Executor chung | Guard chung | Gói evidence chung | Cùng model, version, temperature và trần như B2; ghi call/token thực tế | — |
| BM MANUAL | Detector chung, alert hiện trên dashboard | Người vận hành | Người vận hành, qua cùng loại action và budget theo runbook, có log thao tác | Không có guard tự động; ghi đề xuất là thao tác đầu tiên | Chỉ dashboard/telemetry thuộc mặt vận hành (mục 5.6) | Giờ người; không LLM | Token/cost LLM, M3, M4 |

Mọi nhóm giữ cùng probe độc lập, profile HPA và quyền scale. Probe không đưa kết quả cho bên quyết định (ACC ZER-32: healer không dùng probe để tự đóng incident).

**B0 với detector quan sát (PROP, tùy ZER-39):** chạy detector ở chế độ chỉ ghi, không có consumer hay đường action, để có T_det cho B0. Nếu ZER-39 không bảo đảm được đường action đã tắt, giữ MTTD/MTTR của B0 là N/A. Dù chọn cách nào, so sánh phục hồi giữa nhóm vẫn dùng M7/M8.

**B0 không có lượt quyết định,** kể cả NO_ACTION, nên metric quyết định là N/A. Không gán latency 0 hoặc “đúng” cho B0 ở C0.

**Nemesis/harness:** trong benchmark phục hồi, harness phát lại cùng kế hoạch fault đã khóa cho mọi nhóm. Nemesis không chọn case riêng cho nhóm nào. Chi phí LLM để sinh kế hoạch ghi ở tài khoản harness, tách khỏi chi phí quyết định phục hồi (PLAN).

### 4.2 Bất biến giữa các nhóm

| Thành phần | Giữ giống giữa | Ghi vào evidence |
| --- | --- | --- |
| Kế hoạch fault, workload, seed, intensity, duration, onset jitter | Mọi nhóm | Phiên bản kế hoạch, seed, T_req/T_stop thực tế |
| Image, config, manifest | Mọi nhóm | Digest/revision |
| Profile HPA và quyền scale | Mọi nhóm | Spec HPA, min/max, chủ sở hữu replicas (ZER-16/ZER-39) |
| Executor, action budget (max replicas, khoảng TTL, registry release known-good) | B1, B2, B3; BM theo runbook cùng budget | Phiên bản executor, budget |
| Guard | B1, B2, B3 | Phiên bản guard, quyết định chấp nhận/từ chối kèm lý do |
| Detector | B1, B2, B3, BM | Phiên bản rule/ngưỡng |
| Gói evidence cho bên quyết định | B1, B2, B3 | Schema, phiên bản truy vấn |
| Model, version, temperature; bộ prompt khóa trước formal | B2, B3 | Model/cấu hình sampling chung; prompt có phiên bản riêng theo vai trò/nhóm, giữ input telemetry và công cụ tương đương; không ép prompt phân vai B2 giống hệt prompt gộp B3 |
| Trần call/token mỗi incident, timeout, retry | B2, B3 | Usage thực tế, lý do dừng |
| Probe và tham số F-01 | Mọi nhóm | Phiên bản probe, Δ, K, S, L |
| Reset đã xác minh, thứ tự xen kẽ | Mọi nhóm | Kết quả kiểm reset, thứ tự đã chạy |

Biến thể dùng để hiệu chỉnh rules/prompt ở pilot không được dùng lại làm biến thể đánh giá formal (PLAN).

### 4.3 Phần kiểm chức năng riêng

Khả năng lập kế hoạch thích nghi của Nemesis và sinh kịch bản bằng LLM (P176) được kiểm chức năng ở ZER-19/ZER-48. Không suy giá trị của chúng từ benchmark phục hồi. B3 chỉ thay cách chia Gaia/Hephaestus, nên RQ2 không nói gì về Nemesis.

### 4.4 Phiếu quyết định B3, claim RQ2 và budget (PENDING)

**Dữ kiện.**
- PLAN: B3 bắt buộc nếu claim chia vai trò có lợi; không có B3 thì giới hạn claim, không bỏ cam kết gốc hay BM.
- USER: quỹ giờ mới chưa có; 10 giờ/tuần là thông tin cũ (SCOPE).
- USER: khoảng 300 USD credit OpenAI API (NOW, 19/10). Chưa xác minh số dư, hạn dùng, quyền model hay quota; chưa duyệt dùng hết.
- Đề xuất trần 1 USD của Codex chỉ cho kiểm backend R0, chưa được duyệt, không phải budget pilot/formal/B3.
- Sub-issue B3 có điều kiện (R4-T04-S03) chưa được tạo; quyết định giữ RQ2 thuộc AC [ZER-22](https://linear.app/zero-door/issue/ZER-22/djoi-chung-single-agent-cho-claim-chia-vai-tro).

| | (a) Giữ phép thử B3 | (b) Không thực hiện B3 |
| --- | --- | --- |
| Việc thêm | Cấu hình SINGLE_LLM dùng chung adapter/tools/guard; pilot B2/B3; formal B3 trên cùng khối | ZER-22 đóng bằng quyết định giới hạn claim |
| RQ2 | So sánh B2 với B3, claim theo dữ liệu | Chỉ mô tả cách phối hợp: trace, latency và chi phí theo tác tử |
| Cam kết gốc | Giữ ba tác tử, B0/B1/B2/BM | Giữ nguyên; bài không khẳng định nhiều tác tử tốt hơn một tác tử |
| Chi phí tăng | Thời gian lab và call/token của một nhóm nữa (công thức dưới) | Không |
| Rủi ro | Lịch 31/10 (mục tiêu nội bộ) chặt hơn | Phản biện có thể hỏi vì sao cần nhiều tác tử; bài phải tự giới hạn |

**Công thức nhu cầu** cho nhóm g (dùng được cho cả B2, B3):
- Số trial: T_g = Σ_c (số variant của lớp c) × r_g, với r_g là số lặp.
- Thời gian lab: H_g = T_g × (t_warm + t_obs + t_reset) / 3600, với t_obs được dự trù ít nhất đủ khoảng chờ effect đã khóa + cap_rec + S và overhead đo; case không effect dùng W_eff, C0 dùng cửa sổ benign riêng. D-04 là horizon quan sát recovery, không bảo đảm toàn trial hoàn tất trong từng đó giây.
- Call: C_g ≤ T_g × k_cap, với k_cap là trần call mỗi incident, đã gồm retry.
- Token: Tin_g ≤ C_g × t_in_max; Tout_g ≤ C_g × t_out_max.
- Chi phí: Cost_g = (Tin_g × p_in + Tout_g × p_out) / 10⁶ USD, với p_in, p_out là đơn giá USD trên 1 triệu token, lấy từ trang giá provider có ghi ngày khi ZER-36 chốt model.
- BM thêm giờ người: T_BM × (t_obs + thời gian chuẩn bị).

**Ví dụ minh họa (ILLUSTRATIVE, không phải budget).** Giả định: 6 lớp C0–C5, mỗi lớp 1 variant; r = 3 cho pilot, r = 10 cho formal; t_warm = 120 s, t_obs = 630 s, t_reset = 300 s (1.050 s mỗi trial); k_cap = 6; t_in_max = 6.000; t_out_max = 500. Mọi số này chưa có nguồn đo.

| Riêng B3 | Trial | Giờ lab | Call tối đa | Token vào tối đa | Token ra tối đa | Chi phí tối đa (USD) |
| --- | --- | --- | --- | --- | --- | --- |
| Pilot | 18 | 5,25 | 108 | 648.000 | 54.000 | 0,648 p_in + 0,054 p_out |
| Formal | 60 | 17,5 | 360 | 2.160.000 | 180.000 | 2,16 p_in + 0,18 p_out |

Với cùng giả định, formal năm nhóm cần 300 trial, khoảng 87,5 giờ lab; B3 chiếm 20%. BM thêm khoảng 17,5 giờ có người trực. Điều này gợi ý ràng buộc chính có thể là thời gian lab và giờ người, không chỉ tiền API. Kết luận này chỉ đúng với giả định minh họa; ZER-51/52 phải đo lại.

**Khuyến nghị (PROP): (a) có điều kiện.**
- Giữ B3 trong thiết kế và kế hoạch pilot ngay bây giờ. Chốt đi tiếp hay chuyển (b) tại ZER-22, sau khi pilot ZER-51 đo được thời gian và call/token thật mỗi trial.
- Chuyển sang (b) nếu: dự báo B3 formal vượt trần giờ lab hoặc trần API mà Hoàng duyệt; hoặc B2 pilot chưa ổn định (tỷ lệ schema sai/timeout cao tới mức so sánh B2/B3 không đo được quyết định).
- Lý do:
  1. Đề tài đặt tên theo kiến trúc Multi-Agent. Không có B3 thì bài chỉ mô tả được, không trả lời được vì sao cần chia vai trò.
  2. Dùng chung adapter, tools và guard có thể giảm phần triển khai B3, nhưng chưa đo công sức hay chi phí thực. Ước lượng 87,5 giờ chỉ là minh họa, cần pilot để dự báo nguồn lực.
  3. Cả hai phương án đều giữ B0/B1/B2/BM và cam kết gốc. R0 cần Hoàng chọn chính sách có điều kiện hoặc bỏ B3 ngay, cùng ranh giới nguồn lực; quyết định chạy formal ở ZER-22 sau pilot không thay việc chấp nhận thiết kế R0.
- Nếu Hoàng muốn giảm rủi ro lịch ngay, (b) là lựa chọn trung thực và an toàn. Khi đó bài, ZER-26 và ZER-22 phải ghi rõ giới hạn RQ2.

## 5. AC-03 — Ground truth, cách chấm và evidence

### 5.1 Ground truth của mỗi incident

Hoàng và Hòa rà **nhãn, decision_required, tập action A và ràng buộc theo variant**, trước khi sinh lịch chạy (PLAN). Việc rà này không bao gồm thứ tự trial, seed onset jitter hoặc thời điểm bắt đầu fault của từng trial. Sau khi khóa variant, harness mới sinh thứ tự/seed/onset từng trial, niêm phong ở mặt H (mục 5.6), không cho Hoàng trong vai người vận hành BM xem tới khi trial kết thúc. Nếu cần rà mức trial trước run, Hòa thực hiện ở vai evaluator; Hoàng chỉ được rà lịch của trial đã kết thúc, không xem lịch trial kế tiếp. Harness ghi các trường sau ở H trước mỗi trial:
- lớp case, variant, nguyên nhân thật, tập service mục tiêu;
- tham số và lệnh fault, T_req, T_stop, seed của onset jitter;
- tập nguồn tấn công S_att quan sát tại điểm tin cậy (nếu có);
- revision known-good của service bị đổi (C3);
- `decision_required` và tập action chấp nhận A, kèm ràng buộc tham số;
- kỳ vọng cho hành động tiếp theo (scale down, TTL, rollback);
- phiên bản nhãn, người rà và thời điểm khóa.

Tập A và decision_required khóa theo **variant** trước run, không suy từ việc detector có trigger hay không. Bảng 5.2 là mặc định; variant có thể thay A nếu ghi trước. C1 cần quyết định vẫn vào M1 khi missed detection; C1 cho NO_ACTION vẫn là lượt cần phản hồi đánh giá, không tự loại khỏi mẫu số. C0 không vào M1 nhưng mọi alert/action vẫn vào M5/M6. Thiếu decision_required là UNKNOWN_COHORT, báo số lượt và cận theo khả năng thuộc cohort; không tự gán false rồi loại lượt.

### 5.2 Các lớp case

| Lớp | Ground truth | Cần quyết định | Tập action chấp nhận A (tiền đề) | Không chấp nhận (ví dụ) | Hậu điều kiện để chấm hiệu lực |
| --- | --- | --- | --- | --- | --- |
| C0 — tải lành ổn định | Không có fault | Không | Không có action (NO_ACTION hoặc không trigger) | Mọi action của ZERO DOOR là false action; block hoặc rollback là false action có hại | Probe và request benign giữ đạt |
| C1 — khách hợp lệ tăng | Tải hợp lệ tăng, nguồn và mẫu request bình thường, không đổi release | Có theo decision_required khóa trước run, kể cả khi không trigger | SCALE_UP service quá tải, trong budget; NO_ACTION chỉ khi variant ghi trước rằng HPA đủ phục hồi trong cap | BLOCK_IP nguồn hợp lệ; ROLLBACK | Replica Ready tăng, probe đạt L; request benign không bị chặn |
| C2 — DDoS L7 | Tải từ S_att qua route giám sát, có thể cùng triệu chứng CPU/latency với C1 | Có | BLOCK_IP với tập nguồn khác rỗng ⊆ S_att và TTL trong khoảng cho phép (containment); SCALE_UP trong budget (giảm nhẹ) | Block có chứa bất kỳ nguồn benign nào; ROLLBACK | Request từ nguồn bị chặn bị từ chối tại điểm tin cậy; benign giữ ngưỡng (F-08); TTL/cleanup đúng |
| C3 — release lỗi | Deploy revision lỗi tại T_req | Có | ROLLBACK service bị đổi về revision known-good | SCALE_UP đơn thuần; BLOCK_IP; rollback service khác; rollback mọi 5xx không có thay đổi release | Digest image/config trở về known-good và probe phục hồi |
| C4 — cạn tài nguyên | Cạn CPU trên workload mục tiêu (ZER-44) | Có | SCALE_UP trong budget khi tải chia được qua replica mới; variant mà scale không giúp phải ghi A khác trước run | BLOCK_IP khi không có nguồn tấn công; ROLLBACK khi không đổi release | Throttling/latency giảm, probe đạt |
| C5 — SQLi trên fixture | Request SQLi từ S_att vào fixture riêng | Có | BLOCK_IP với tập nguồn khác rỗng ⊆ S_att tại điểm tin cậy, TTL trong khoảng | SCALE_UP; ROLLBACK Boutique; block nguồn benign | Containment đã xác minh (ACC ZER-32 mục 3.4); availability Boutique báo riêng |

- Cặp chồng triệu chứng cần có: C1 với C2, và C2 với C4 (ZER-45). Không giả tạo metric giống nhau bằng dữ liệu mô phỏng.
- Ở C2, cả BLOCK_IP và SCALE_UP đều thuộc A. Tỷ lệ containment (M12) báo riêng, để SCALE_UP không bị đếm như đã chặn được nguồn.
- **Hành động tiếp theo** chấm riêng, không vào M1:
  - SCALE_DOWN chỉ đúng sau cửa sổ tải thấp và khỏe đủ dài, trong min/max, không đảo chiều liên tục, và không làm hỏng benign (ZER-16).
  - Policy block hết hiệu lực hoặc được dọn đúng TTL, kể cả sau restart (ZER-46).
  - Rollback giữ known-good tới hết cửa sổ ổn định (ZER-47).
- PodKill theo scenario-design là phép thử bổ sung cho controller và can thiệp thừa; không thuộc C0–C5 và không vào RQ chính.

### 5.3 Quy tắc action đúng

Một đề xuất a đúng cho incident i khi thỏa đủ:
1. Loại action ∈ A(variant của i).
2. Tham số thỏa ràng buộc của A, đối chiếu ground truth tại thời điểm quyết định: mục tiêu thuộc tập service bị ảnh hưởng; trong action budget; tập nguồn block khác rỗng ⊆ S_att, có nguồn quan sát tin cậy và TTL hợp lệ; đích rollback là known-good. Membership tên action đơn thuần chưa đủ. Bộ chấm ví dụ chỉ dùng action đã giả định kiểm tham số, không xác minh điều kiện này từ runtime.
3. Nếu A cho phép NO_ACTION/ABSTAIN, quyết định đó là phản hồi hợp lệ có ghi nhận đúng schema. Im lặng không phải NO_ACTION.

Ba lớp kết quả tách nhau: **quyết định đúng** (đề xuất trước guard), **action hoàn tất** (ACTION_COMPLETED với hậu điều kiện, ACC ZER-32 mục 3.3) và **phục hồi** (RECOVERY_VERIFIED). Quyết định đúng mà action thất bại vẫn là quyết định đúng, nhưng không phục hồi. Phục hồi nhờ HPA sau quyết định sai vẫn là quyết định sai, có cờ NO_ACTION_BEFORE_RECOVERY nếu không có action thành công trước T_rec.

**Quyết định đầu tiên** của incident là bản ghi quyết định sớm nhất theo `ts_event`, sau T_det, của bên quyết định được cấu hình cho nhóm: rule engine (B1), Hephaestus sau Gaia (B2), single agent (B3), thao tác đầu tiên trong log người vận hành (BM). Giữ kết quả của attempt đầu trong deadline, gồm sai schema/timeout/refusal; không bỏ attempt lỗi để chọn bản hợp lệ đến muộn. Với timestamp không xác định/đồng hồ mâu thuẫn, ghi MISSING, không tự chọn thứ tự. Nhiều alert của cùng incident dẫn tới nhiều quyết định thì chỉ quyết định sớm nhất vào M1; các quyết định sau tính vào hành động tiếp theo.

### 5.4 Kết quả quyết định đầu tiên

| Kết quả | Điều kiện | Vào mẫu số M1 | Tính đúng |
| --- | --- | --- | --- |
| CORRECT | Đề xuất thỏa mục 5.3 | Có | Có |
| INCORRECT | Đề xuất hợp lệ schema nhưng không thuộc A, hoặc sai tham số | Có | Không, kể cả khi guard chặn |
| NO_ACTION_VALID, ABSTAIN_VALID | Phản hồi rõ ràng đúng schema, và A cho phép | Có | Có |
| NO_ACTION_INVALID, ABSTAIN_INVALID | Phản hồi rõ ràng nhưng A không cho phép | Có | Không |
| NO_TRIGGER | Không detect trong cap_det nên không có quyết định (missed detection) | Có | Không |
| NO_RESPONSE | Có trigger nhưng không có quyết định trong timeout | Có | Không; không tự gán NO_ACTION |
| SCHEMA_INVALID | Đầu ra sai schema hoặc ngoài enum | Có | Không |
| FALLBACK_RULES | LLM lỗi hoặc timeout, RULES ra quyết định thay | Có | Không tính đúng cho LLM; quyết định RULES được chấm riêng và có cờ fallback |
| UNKNOWN_GT | Thiếu hoặc mâu thuẫn ground truth: thiếu tập A, ground truth hỏng, sự cố thật ngoài kế hoạch, incident chồng không tách được | Có | Chưa rõ; mở rộng cận trên |
| OUT_NO_EFFECT | Effect là CONFIRMED_NO_EFFECT (ACC) | Không, rời N kèm lý do | — |

Thiếu telemetry không phải một kết quả riêng. Nếu bên quyết định chủ động trả ABSTAIN vì thiếu dữ liệu thì chấm theo ABSTAIN. Nếu không phản hồi thì là NO_RESPONSE. Nếu chính evaluator thiếu dữ liệu để chấm thì là UNKNOWN_GT.

Trial phát hiện lộ đáp án (mục 5.7) được gắn cờ LEAK_DETECTED và vẫn lưu. Cách xử lý trong phân tích formal là PROP: báo kết quả cả khi có và khi không có các khối bị lộ, không âm thầm bỏ. Quy tắc cuối khóa ở ZER-53.

### 5.5 Mẫu số từng metric

Không ép mọi metric dùng cùng N.

| ID | Metric | Đơn vị | Tử số | Mẫu số | Rời mẫu số chỉ khi | N/A |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | Độ đúng quyết định đầu tiên trước guard | Incident có decision_required khóa trước run | CORRECT + *_VALID | Mọi incident thuộc cohort đã khóa, trừ OUT_NO_EFFECT; giữ NO_TRIGGER | CONFIRMED_NO_EFFECT | B0; cohort/nhãn thiếu báo UNKNOWN |
| M1c | Độ đúng có điều kiện, luôn báo kèm độ phủ | Incident có trigger | Như M1 | Incident có trigger và ground truth rõ; độ phủ = có trigger / mẫu số M1 | — | B0 |
| M2 | Phễu quyết định | Incident | Từng tầng: requested, CONFIRMED, NO_EFFECT, UNKNOWN_EFFECT, có trigger, có phản hồi hợp lệ, action hoàn tất, phục hồi | Requested | — | Tầng quyết định N/A ở B0 |
| M3 | Guard từ chối | Từng đề xuất tới guard | Số bị từ chối, tách chặn đúng (đề xuất sai), chặn nhầm (đề xuất đúng), chưa rõ (thiếu ground truth/điều kiện) | Mọi đề xuất tới guard; báo coverage phần chấm được | — | B0, BM |
| M4 | Fallback | Incident có trigger ở B2/B3 | Số incident chuyển sang RULES; kèm kết quả phục hồi của nhóm này | Incident có trigger ở B2/B3 | — | B0, B1, BM |
| M5 | False alarm trên benign | Slot w_b của cửa sổ C0 | Slot có ít nhất một alert được lưu; episode được quan sát | Mọi slot đã khai báo trong W, giữ slot thiếu evidence; episode báo trên toàn giờ W kèm coverage/cận | — | B0 nếu detector tắt; missing không phải 0 |
| M6 | False action trên benign | Thời gian và cửa sổ C0 | Số action ZERO DOOR thực thi; số action có hại hoặc chưa rõ tác hại khi thiếu probe | Toàn giờ W và số cửa sổ C0, kèm độ phủ log action/probe | — | B0 (ghi riêng nếu controller tự scale); log thiếu không suy 0 |
| M7 | Tỷ lệ phục hồi được xác minh | Incident | Các nhãn RECOVERED* của ZER-32 | N của ZER-32 (CONFIRMED + UNKNOWN_EFFECT) | CONFIRMED_NO_EFFECT | — |
| M8 | R(t) theo TotalRecovery | Incident | #{TotalRecovery ≤ t} | N của ZER-32 | Như M7 | — |
| M9 | KPI MTTD, MTTR 120/180, reaction, uptime, CPU | Theo ZER-32 | Theo D-01…D-05 (ACC) | Theo ZER-32 | Theo ZER-32 | MTTD/MTTR/reaction ở B0 nếu không có detector quan sát |
| M10 | Decision latency | Incident có quyết định | Thời điểm quyết định − T_det ở B1/B2/B3/BM; BM báo thêm độ trễ alert hiển thị và thời gian từ hiển thị tới thao tác | Incident có quyết định; báo cùng timeout/NO_RESPONSE/clock missing và coverage | — | B0 |
| M11 | Call, token, cost | Incident và run, tách theo tác tử | Usage thực tế | Incident có trigger; tổng theo run | — | B0, B1, BM; ghi N/A, không ghi 0 |
| M12 | Containment và benign | Incident C2/C5 | Containment đã xác minh; request success rate benign | Incident C2/C5 trong N | Như M7 | — |

**Cohort và macro M1 (PROP).** Metric chính RQ1/RQ2 là trung bình bằng trọng số 1/4 của tỷ lệ M1 từng lớp C1–C4, mỗi lớp công bố k/N và cận thiếu nhãn. Không trộn C5 vào macro chính; C5 báo riêng. Lớp có N = 0 khiến macro chính không xác định (EMPTY/NO_ELIGIBLE theo nguyên nhân), không gán 0, không bỏ lớp rồi lấy trung bình lớp còn lại. M1c chỉ dùng tử số trong đúng tập triggered ∩ ground-truth-known; báo cả coverage trigger/N và coverage tập chấm được/N. Bảng pooled ở mục 6 kiểm số học, không phải macro RQ1/RQ2. UNKNOWN_EFFECT vẫn có thể chấm quyết định nếu nguyên nhân/tập A/tham số có nguồn độc lập đầy đủ; thiếu effect không tự làm mọi metric UNKNOWN_GT, cũng không tự xác nhận recovery.

**Quy tắc cửa sổ benign và khử trùng (PROP, tham số khóa ở ZER-53):**
- Cửa sổ benign là cửa sổ đo W của trial C0, bỏ warm-up. Alert trong trial C1–C5 không vào M5.
- Đề xuất w_b = 60 s; lý do: cùng bậc ngưỡng MTTD và hai chu kỳ scrape hiện tại 30 s. Dùng W = [0, T), slot i = [i × w_b, min((i+1) × w_b, T)); slot cuối ngắn vẫn tính một slot. N_slot = ceil(T/w_b), báo độ dài slot cuối; tỷ lệ slot không phải tỷ lệ thời gian.
- Khóa khử trùng là (rule hoặc signature của detector, service mục tiêu). Các lần firing cùng khóa cách nhau không quá g_b = 90 s (ba chu kỳ scrape) là một episode.
- Chỉ alert/action có timestamp trong [0,T) mới vào tử số; sự kiện ngoài W lưu riêng. Episode cùng khóa tính trên các firing trong W; sự kiện ngoài W không nối hoặc tăng episode trong W. Báo trạng thái biên cửa sổ, không coi đây là số incident nguyên vẹn bên ngoài W.
- Cần heartbeat/coverage độc lập cho detector, transport và kho alert; log action/probe cho M6. Không có alert khi collector chết là thiếu dữ liệu. Slot có alert chắc chắn là hit; slot không alert nhưng coverage không đủ là unknown; còn lại là no-hit đã quan sát. Giữ mọi slot trong N_slot, báo [hit/N_slot, (hit + unknown)/N_slot]. Không có coverage thì mặc định unknown, không mặc định đầy đủ. Episode/giờ chỉ là giá trị xác định khi alert stream đầy đủ; thiếu coverage chỉ báo số episode quan sát được với verdict UNKNOWN, không coi đó là cận dưới: firing bị mất có thể nối hai episode quan sát rời nhau. Không suy là 0. Hành động có hại/chưa rõ báo riêng nếu thiếu probe. Ở C1, báo riêng block/rollback sai và ảnh hưởng lên request benign trên toàn cohort C1 đã khóa, kèm coverage; không gộp slot C1 vào mẫu số C0 của M5/M6 hoặc bỏ tác hại C1 chỉ vì không thuộc C0.
- M5 báo tỷ lệ slot cùng cận, coverage và episode mỗi giờ benign. Không chia false alarm cho số attack mà gọi FPR (PLAN verification #9). B0 detector tắt thì M5 N/A; không thể coi không chạy detector là không false alarm.
- Cửa sổ có độ dài 0 hoặc âm là INVALID_WINDOW, không tính tỷ lệ.

**Missed detection phải hiện:** M1 giữ NO_TRIGGER trong mẫu số. M1c chỉ được báo cùng độ phủ. M2 cho thấy incident rơi ở tầng nào. Không chọn riêng lượt đã trigger để tuyên bố chất lượng chung.

**N = 0:** theo ACC ZER-32 cho mẫu số KPI incident. Với M1, chỉ xét cohort decision_required trước: không có trial thuộc cohort thì EMPTY; cohort có trial nhưng đều CONFIRMED_NO_EFFECT thì NO_ELIGIBLE. Thiếu cohort là UNKNOWN_COHORT, không suy EMPTY. Tỷ lệ không xác định, verdict không phải PASS. Toàn bộ UNKNOWN_GT không phải N = 0: khoảng là [0, 1].

### 5.6 Ba mặt dữ liệu

Đây là contract đề xuất cho ZER-9 (R1-T01-S03) và ZER-37, chưa phải schema runtime.

| Mặt | Ai ghi | Ai được đọc | Nội dung |
| --- | --- | --- | --- |
| H — harness/evaluator | Harness, bộ đánh giá effect, probe độc lập | Harness và người chấm sau run | Ground truth mục 5.1; log điều khiển Nemesis/worker; effect_evaluation; mẫu probe; canary |
| O — vận hành | Telemetry của lab, detector, bên quyết định, executor | Bên quyết định của nhóm (B1/B2/B3/BM) theo quyền vai trò; evaluator đọc lại sau run | Metric, log request kèm IP quan sát, lịch sử release, trạng thái deploy, alert, quyết định, action |
| S — ghép chấm | Script chấm sau run | Người chấm | Bảng ghép theo ID trung tính, kết quả chấm, phiên bản quy tắc |

| Trường | Mặt | Nguồn ghi | Timestamp | Khi thiếu | Ghi chú rò rỉ |
| --- | --- | --- | --- | --- | --- |
| `run_id`, `trial_id`, `incident_id` | H, O | Harness sinh | — | Không ghép được: ORPHAN/MISSING (ACC) | Chuỗi ngẫu nhiên, không chứa lớp case, vector hay số thứ tự case |
| `case_class`, `variant_id`, `cause` | H | Harness | Thời điểm khóa nhãn | UNKNOWN_GT | Không bao giờ vào O |
| `acceptable_actions`, `decision_required` | H | Harness, đã rà | Thời điểm khóa nhãn | UNKNOWN_GT | Không vào prompt dưới dạng gợi ý |
| `fault_params`, `attack_command`, `S_att` | H | Harness/worker | T_req, T_stop | Thiếu log điều khiển ghi missing; effect theo bộ đánh giá độc lập. T_eff hợp lệ vẫn CONFIRMED, không hạ thành UNKNOWN chỉ vì mất lệnh | IP nguồn vẫn hiện tự nhiên trong log request ở O; danh sách S_att thì không |
| `known_good_revision` | H | Harness | Lúc deploy bản lỗi | UNKNOWN_GT | Lịch sử release thật vẫn ở O |
| `effect_evaluation`, T_eff | H | Bộ đánh giá effect | `ts_event` | UNKNOWN_EFFECT (ACC) | — |
| Mẫu probe | H | Probe độc lập | `t_start`, `t_end` | U, MISSING_PROBE (ACC) | Không đưa cho bên quyết định |
| Metric, log request, release history | O | Prometheus, Elasticsearch, Kubernetes | Theo nguồn | Đánh dấu thiếu; không điền 0 | Nhãn job, tên topic, pod và image phải trung tính |
| Alert, T_det | O | Detector | `ts_event` | MISSED | Văn bản alert chỉ mô tả triệu chứng |
| Bản ghi quyết định | O | Bên quyết định | `ts_event` | NO_RESPONSE | Lưu đề xuất trước guard, model/prompt version, usage |
| Kết quả guard, action | O | Guard, executor | `ts_event` | Action MISSING | — |
| `canary_token` | H | Harness | — | — | Xuất hiện ở O là bằng chứng rò |
| Bảng ghép | S | Script chấm | Thời điểm chấm | — | Chỉ tạo sau khi trial kết thúc |

Theo ACC ZER-32 mục 6, event phía điều khiển và ground truth lưu ở kho tách khỏi nguồn bên chữa lỗi truy vấn; hai bên chỉ liên kết qua ID trung tính.

### 5.7 Kênh rò đáp án và cách thử

Bằng chứng vận hành thật được giữ: lịch sử release, log request, IP quan sát tại điểm tin cậy, metric. Che các dấu vết đó làm phép thử thiếu thực tế. Thứ cần chặn là thông tin chỉ harness mới biết.

| Kênh | Ví dụ lộ | Phòng ngừa (PROP) |
| --- | --- | --- |
| Prompt và alert | “Có vẻ là DDoS, hãy block”, tên case, gợi ý action | Prompt chỉ liệt kê enum action như menu cố định, giống nhau mọi case; alert chỉ mô tả triệu chứng |
| ID có nghĩa | `incident_id = c3-badrelease-07` | ID ngẫu nhiên; ánh xạ ID → case chỉ ở H |
| Đường dẫn và topic | Thư mục `scenarios/sqli/`, topic `attack.ddos` | Tên trung tính; bên quyết định không đọc kho H |
| Đối tượng Kubernetes | Pod `nemesis-sqli-worker`, label `chaos=ddos` thấy được qua API | Harness/worker ở namespace riêng; quyền truy vấn của bên quyết định giới hạn ở namespace mục tiêu |
| Image tag | `frontend:v2-broken` | Dùng digest hoặc tag trung tính; lịch sử release vẫn hiện |
| Dấu hiệu tải | User-Agent `nemesis/1.0` | Header thực tế hoặc trung tính, ghi ở H |
| Nhịp thời gian | Fault luôn bắt đầu đúng phút thứ 5 | Onset jitter theo seed, giống nhau giữa nhóm |
| Người vận hành BM | Người chạy BM đã thấy thứ tự/seed/onset từng trial trước khi chạy | Hoàng rà nhãn theo variant; harness sinh và niêm phong lịch sau rà, Hòa rà mức trial hoặc Hoàng rà sau trial; theo mục 5.1 và quyết định mục 13 |

**Phép thử rò cho ZER-9 (PROP):**
0. Ghi cờ `operator_saw_schedule_before_trial` cùng bằng chứng thời điểm/role truy cập lịch H. Hoàng đã xem thứ tự/seed/onset của trial trước hoặc trong trial thì gắn LEAK_DETECTED; mất audit coverage thì UNKNOWN. Việc rà nhãn theo variant trước sinh lịch không tự là rò lịch. Đây là yêu cầu thiết kế cho ZER-9, chưa có kiểm runtime.
1. Harness đặt một canary ngẫu nhiên vào mặt H mỗi run. Quét mọi đầu vào và đầu ra của bên quyết định (prompt, kết quả truy vấn, log quyết định). Gặp canary thì LEAK_DETECTED.
2. Kiểm các trường định danh do harness sinh (ID/topic/path/pod/label/image) theo manifest giá trị có thể tiết lộ case. Tên vector/case hoặc chỉ dẫn đáp án ở các trường đó là ứng viên LEAK_DETECTED. Các từ “attack/chaos/nemesis” đơn lẻ là tín hiệu rà soát, không tự chứng minh rò khi chúng chỉ là tên service/menu cố định giống nhau mọi nhóm. Không quét rồi xóa triệu chứng trong log request/release history/IP hợp lệ. Dùng allowlist theo trường/nguồn có phiên bản; canary H hoặc nhãn case thật ra O là bằng chứng rò.
3. Đối chứng sạch: một trial được dựng đúng phải ra không có cờ. Đối chứng lỗi: chèn tên case vào `incident_id` phải ra có cờ.

### 5.8 Đối chiếu ZER-32 đã nghiệm thu

| Quy ước ZER-32 (ACC) | Cách artifact này dùng | Kết quả |
| --- | --- | --- |
| Ngưỡng MTTD < 60 s, MTTR < 120/< 180 s, uptime ≥ 99,9% | M9 giữ nguyên; mốc 120/180 s của M8 ghi rõ là từ effect và không thay KPI | Khớp |
| D-01 verdict mean và tỷ lệ | M9 dùng nguyên bảng verdict | Khớp |
| D-02 reaction từ T_det | M9; B0 N/A nếu không có detector | Khớp |
| D-03 CPU Σusage/Σlimit | M9; không đổi | Khớp |
| D-04 T_rec mẫu thứ K, sau S; AFTER_STOP; horizon | M7/M8 dùng nhãn ZER-32; t_obs trong công thức budget theo horizon | Khớp |
| D-05 uptime ba trạng thái | M9 | Khớp |
| UNKNOWN_EFFECT ở lại N; chỉ CONFIRMED_NO_EFFECT có chứng cứ đủ mới rời N | M1, M7, M8, M12 dùng cùng quy tắc; ví dụ i8/i9 | Khớp |
| EMPTY/NO_ELIGIBLE không PASS | M1 và M7 dùng cùng nhánh; ví dụ E7 | Khớp |
| Probe thiếu không tự up | Không đổi; M5 không suy benign từ thiếu alert | Khớp |
| Recovery sau dừng fault báo riêng | M7 dùng RECOVERED_AFTER_STOP như ZER-32 | Khớp |
| Mẫu số FPR do ZER-8/ZER-10 khóa (RM-22) | M5/M6 định nghĩa ngữ nghĩa; w_b, g_b khóa ở ZER-53 | Đã đóng phần ngữ nghĩa |
| F-07 số lượt và lý do loại thuộc ZER-8/ZER-53 | Mục 3.2 khóa quy tắc phân tích; số lượt để ZER-53 | Giữ ownership |
| F-01…F-06, F-08, F-09 | Không chốt giá trị; chỉ dẫn tới | Giữ ownership |

## 6. Ví dụ chấm OFFLINE

Dữ liệu giả định cho một nhóm B2, 11 incident. Mục đích là chứng minh cách chấm, **không phải kết quả nghiên cứu**. Bộ chấm tác giả `scratch/zer8/score.py` kiểm 32 giá trị kỳ vọng của phiên bản nhận trước Codex review; giữ nguyên để đối chiếu lịch sử. Các ranh giới đã sửa được kiểm riêng ở `scratch/zer8/codex/retest.py`, mục 11. Cả hai chỉ là ví dụ, không phải scorer production; membership action giả định tham số đã hợp lệ. Thư mục `scratch/` bị Git bỏ qua.

| ID | Ví dụ | Đầu vào | Kết quả quyết định | Nhãn phục hồi | Giới hạn |
| --- | --- | --- | --- | --- | --- |
| i1 | E1 — hai action hợp lệ | C2, A = {BLOCK_IP, SCALE_UP}; đề xuất SCALE_UP | CORRECT | RECOVERED | Không tính containment trong M12 |
| i2 | E1 | C2, cùng A; đề xuất BLOCK_IP nguồn ⊆ S_att | CORRECT | RECOVERED | Tính containment nếu hậu điều kiện đạt |
| i3 | E2 — guard chặn đề xuất sai | C3, A = {ROLLBACK}; đề xuất BLOCK_IP; guard từ chối | INCORRECT | TIMEOUT | Guard chặn đúng; M1 vẫn sai |
| i4 | E3 — LLM timeout, RULES phục hồi | C3; LLM timeout, RULES rollback thành công | FALLBACK_RULES | RECOVERED, cờ fallback | Phục hồi tính cho hệ thống, không tính cho LLM |
| i5 | E4 — NO_ACTION hợp lệ | C1, variant ghi trước HPA đủ; trả NO_ACTION đúng schema | NO_ACTION_VALID | RECOVERED, cờ NO_ACTION_BEFORE_RECOVERY | Hợp lệ chỉ vì variant cho phép |
| i6 | E4 — không phản hồi | C3; có trigger, không có quyết định trong timeout | NO_RESPONSE | TIMEOUT | Không gán NO_ACTION |
| i7 | E5 — missed detection | C4; không detect trong cap_det | NO_TRIGGER | TIMEOUT | Ở lại mẫu số M1 |
| i8 | E6 — effect không xác định | C2, UNKNOWN_EFFECT; đề xuất BLOCK_IP | CORRECT | UNKNOWN_EFFECT | Ở lại N; mở cận trên M7 |
| i9 | E6 — không effect đã xác nhận | C5, CONFIRMED_NO_EFFECT | OUT_NO_EFFECT | — | Rời N kèm lý do |
| i10 | E9 — thiếu nhãn | C4, thiếu tập A; đề xuất SCALE_UP | UNKNOWN_GT | RECOVERED | Mở cận trên M1 |
| i11 | Schema sai | C1, A = {SCALE_UP}; đầu ra sai schema, guard từ chối; HPA tự phục hồi | SCHEMA_INVALID | RECOVERED, cờ NO_ACTION_BEFORE_RECOVERY | Phục hồi không do quyết định |

**Tổng hợp pooled minh họa (khớp bộ chấm tác giả; không phải macro C1–C4 của RQ):**

| Metric | Tử / mẫu số | Giá trị | Ghi chú |
| --- | --- | --- | --- |
| Mẫu số M1 | 11 requested − 1 OUT_NO_EFFECT | N = 10 | i7 (NO_TRIGGER) và i8 (UNKNOWN_EFFECT) ở lại |
| M1 | 4 / 10 (i1, i2, i5, i8) | 0,40 | Cận [4/10, 5/10] = [0,40; 0,50] do i10 UNKNOWN_GT |
| Độ phủ trigger | 9 / 10 | 0,90 | i7 không trigger |
| M1c | 4 / 8 | 0,50 | 8 = có trigger và ground truth rõ (trừ i7, i10); luôn báo cùng độ phủ |
| M3 | 2 bị từ chối / 7 đề xuất tới guard | 2 chặn đúng, 0 chặn nhầm | i3 sai loại action, i11 sai schema |
| M7 | 6 / 10 (i1, i2, i4, i5, i10, i11) | 0,60 | Cận [0,60; 0,70] do i8 |
| Phân rã phục hồi | 1 có fallback; 2 không có action thành công trước T_rec; 3 sau action chính | — | Chỉ 3 lượt phục hồi sau action không fallback; không suy toàn bộ 0,60 là nhờ LLM |

Nếu đếm sai, kết quả sai đáng kể: tính i4 là đúng cho LLM thì M1 = 5/10; bỏ i7 khỏi mẫu số thì M1 = 4/9 ≈ 0,44 và che mất missed detection.

**E7 — N = 0.** Tập rỗng cho verdict EMPTY. Tập chỉ có i9 (CONFIRMED_NO_EFFECT) cho NO_ELIGIBLE. Cả hai không có tỷ lệ, không PASS.

**E8 — benign có alert trùng.** Cửa sổ C0 1.800 s, w_b = 60 s, nên 30 slot. Rule latency trên frontend firing 7 lần từ 300 s đến 420 s, mỗi 20 s. Rule CPU trên cartservice firing một lần lúc 1.500 s. Bên quyết định thực thi SCALE_UP một lần lúc 330 s.

| Đại lượng | Tử / mẫu số | Giá trị |
| --- | --- | --- |
| Tỷ lệ slot có alert | 4 / 30 (slot 5, 6, 7, 25) | 0,133 |
| Episode | 2 (7 firing cách nhau 20 s ≤ g_b gộp thành một) | 4 mỗi giờ benign |
| False action | 1 trong 0,5 giờ | 2 mỗi giờ; không có hại vì benign vẫn đạt |
| Sai nếu đếm firing thô | 8 firing | Thổi phồng false alarm gấp 4 lần theo episode |

Chia 2 episode cho số attack (ví dụ 5) để gọi “FPR 40%” là sai mẫu số và bị cấm.

**E10 — rò qua metadata (định tính).** Prompt B2 chứa danh sách pod có `nemesis-sqli-worker`, hoặc image tag `frontend:v2-broken`, hoặc canary của mặt H. Trial gắn cờ LEAK_DETECTED; quyết định không được tính CORRECT như một lượt sạch. Báo kết quả cả khi có và khi không có khối bị lộ, theo quy tắc khóa ở ZER-53.

**Kiểm bộ chấm tác giả tại lúc nhận (trước sửa ranh giới).**
- `python -I scratch/zer8/score.py`: 32 OK / 0 FAIL, exit 0.
- `python -I scratch/zer8/score.py mutants`: 6/6. Đối chứng sạch khớp mọi giá trị. Năm mutant đều bị bắt: tính fallback là đúng (5 sai khác); bỏ NO_TRIGGER khỏi mẫu số (3); giữ CONFIRMED_NO_EFFECT trong N (6); loại UNKNOWN_EFFECT khỏi N (2); đếm firing thô (4). Mutant crash không được tính là bắt.
- Giới hạn: bộ chấm kiểm logic của chính định nghĩa này trên dữ liệu giả định. Nó không kiểm dữ liệu thật, producer hay detector. E10 không được mô hình bằng số.

## 7. AC → bằng chứng → verdict

| AC (snapshot) | Yêu cầu trong gói | Bằng chứng | Verdict tự kiểm |
| --- | --- | --- | --- |
| AC-01 | Giữ nghĩa RQ1–RQ3; mỗi RQ có so sánh, đơn vị, metric chính/phụ, dữ liệu tối thiểu, kết luận được và chưa được phép | Mục 3.1 | Đạt |
| AC-01 | Tách đạt thuyết minh khỏi đóng góp nghiên cứu; không bắt AI thắng | Mục 2, 3.2 điểm 8 | Đạt |
| AC-01 | Không khẳng định mới/đầu tiên/vượt trội khi chưa có căn cứ | Mục 3.3 | Đạt |
| AC-01 | Cách báo chênh lệch, failure, bất định; không tự khóa số lượt | Mục 3.2 | Đạt; metric chính chờ Hoàng chấp nhận |
| AC-02 | Ma trận B0/B1/B2/BM và B3: ai phát hiện, quyết định, thực thi; guard, probe, HPA, đầu vào, biên chi phí | Mục 4.1 | Đạt |
| AC-02 | B0 không có metric LLM; không gán 0 | Mục 4.1, 5.5 | Đạt |
| AC-02 | B1/B2 cùng evidence, executor, budget, guard, probe; B3 cùng model, evidence, tools, trần; ghi overhead thật | Mục 4.1, 4.2 | Đạt |
| AC-02 | BM giữ trong cam kết | Mục 4.1, 4.4 | Đạt |
| AC-02 | Replay cùng fault, xen kẽ, reset, tách pilot/formal, khóa rules/prompt/model; Nemesis không chọn case dễ cho B2; adaptive kiểm riêng | Mục 3.2, 4.1, 4.2, 4.3 | Đạt |
| AC-02 | Phiếu B3 hai lựa chọn, khuyến nghị, công thức, không bịa quota/đơn giá/model | Mục 4.4 | Đạt ở mức đề xuất; **quyết định PENDING** |
| AC-03 | Định nghĩa C0–C5; action là tập có tiền đề/hậu điều kiện; không một đáp án cho mọi CPU/5xx | Mục 5.1–5.3 | Đạt |
| AC-03 | Giữ scale down, benign, TTL/cleanup, rollback known-good; SQLi và uptime Boutique báo tách | Mục 5.2 | Đạt |
| AC-03 | Ba mặt dữ liệu; field, quyền thấy, nguồn, timestamp, thiếu dữ liệu, liên kết; kênh rò | Mục 5.6, 5.7 | Đạt; contract đề xuất cho ZER-9/37 |
| AC-03 | Mẫu số M1, false alarm, recovery/KPI; dedup, cửa sổ, trigger; NO_ACTION/ABSTAIN khác im lặng, timeout, schema sai, thiếu telemetry | Mục 5.4, 5.5 | Đạt; w_b, g_b khóa ở ZER-53 |
| AC-03 | Missed detection hiện; guard không biến sai thành đúng; fallback không thành LLM; unknown ground truth hiện | Mục 5.4, 5.5, 6 | Đạt |
| AC-03 | Khớp ZER-32 accepted; F-01…F-09 giữ ownership | Mục 5.8 | Đạt |
| Tự kiểm | Ví dụ OFFLINE đủ 10 nhóm tình huống; checker có đối chứng sạch và ca lỗi thật | Mục 6 | Đạt |

## 8. Quyết định cần Hoàng (gom một lần sau review)

1. **B3 và claim RQ2.** Khuyến nghị (a) có điều kiện, chốt tại ZER-22 sau pilot ZER-51. Hoặc chọn (b) ngay. Mục 4.4.
2. **Trần nguồn lực cho pilot.**
   - Trần USD từ credit API, sau khi ZER-36 xác minh số dư, model và đơn giá. Trần này tách khỏi đề xuất 1 USD kiểm backend R0.
   - Quỹ giờ lab và giờ người mỗi tuần có thể bố trí.
   - Không cần số formal ngay: số đó chốt ở ZER-53 sau pilot.
3. **Người vận hành BM và cách che lịch case.** Ví dụ: một người không soạn lịch (Hòa hoặc người khác) chạy BM; hoặc harness chọn thứ tự và onset ngẫu nhiên, ẩn với người vận hành. Nếu Hoàng vừa soạn vừa chạy, BM phải ghi giới hạn “người vận hành biết lịch”.
4. **Chấp nhận các đề xuất phương pháp:** metric chính M1 cho RQ1/RQ2; B2 là cấu hình báo KPI thuyết minh; R(t) từ effect để so nhóm; quy tắc slot/episode; xử lý trial bị lộ. Giá trị số w_b, g_b và số lặp vẫn khóa ở ZER-53.

Không cần Hoàng quyết lại D-01…D-05, ba vector, BM hay B0/B1/B2: các mục đó đã có nguồn.

## 9. Ngữ cảnh và khoảng trống nguồn

**Cập nhật sau quyết định:** các gạch đầu dòng “chưa duyệt/UNKNOWN” dưới đây ghi bối cảnh bản đề xuất ban đầu. Quyết định hiện hành ở mục 12–13: 1 USD kiểm backend theo xác nhận Hoàng; pilot 5 USD/2 giờ mỗi phiên/8 giờ tổng; formal chốt sau pilot. Model/quota/đơn giá R0 đã có receipt ZER-36, không suy ngân sách formal hoặc số dư hiện tại.

- **Hai đề xuất trần API theo ngữ cảnh khác nhau, đều chưa duyệt:**
  - [ai-provider](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/reference/ai-provider.md) đề xuất 10 USD cho thử LLM ban đầu, trong ngữ cảnh credit Azure.
  - NOW ghi đề xuất 1 USD của Codex cho kiểm backend R0, trong ngữ cảnh credit OpenAI.
  - Hai con số thuộc hai nguồn credit và mục đích khác nhau. Đề xuất: ZER-36 ghi một bảng duy nhất; artifact này không chọn hộ.
- **Bảng B0 của research-design** không nói rõ MTTD/MTTR của B0 khi không có detector. Mục 4.1 nêu cách xử lý; không sửa nguồn.
- **C1 trong research-design** ghi “scale hoặc không can thiệp theo điều kiện case”. Mục 5.2 cụ thể hóa thành điều kiện theo variant ghi trước; không đổi nghĩa.
- **Enum action thật** chưa có (ZER-50). Mục 5 dùng loại action theo P106 cùng NO_ACTION/ABSTAIN; tên cụ thể đổi theo ZER-50 mà không đổi quy tắc chấm.
- **UNKNOWN:** đơn giá, model, quota (ZER-36); quỹ giờ; thời lượng trial thực tế; tiêu chí effect từng vector (F-05); tracing theo service (ZER-32 RM-01).

## 10. Tự kiểm và giới hạn

- Đã đối chiếu từng hàng với research-design, verification, scenario-design, ai-provider, SCOPE và ZER-32 accepted. Không thấy cam kết gốc nào bị bỏ hoặc ngưỡng nào bị hạ.
- Các con số ở mục 4.4 và 6 được tính lại bằng tay và bằng bộ chấm. Ví dụ budget chỉ là phép nhân giả định, có ghi nhãn.
- Không chạy lab, chaos, heal, API hay model; không gọi Docker/Kubernetes; không chi tiền; không sửa source, config, SCOPE, reference, evidence ZER-32/33/34/35 hay raw CSV.
- Không commit, push hay đổi Linear. Build, CI, runtime, merge: N/A vì gói chỉ gồm tài liệu và tính toán offline. N/A không phải PASS của thiết kế.
- Hash cuối của file này ghi ở bàn giao trong ghi chú issue, vì không thể ghi hash của file vào chính nó.


## 11. Codex review, sửa gọn và retest — 19/10/2026, 08:08 +07:00

**Kết luận:** thiết kế đề xuất PASS sau sửa các lỗi phương pháp dưới đây; chưa phải ZER-8 Done hay thiết kế đã được Hoàng nghiệm thu. AC-02 vẫn PARTIAL vì quyết định B3/claim/nguồn lực chưa chốt. ZER-5 đủ căn cứ kỹ thuật cho cả ba AC, chờ Hoàng nghiệm thu riêng. Không cần gửi lại Claude một vòng sửa các lỗi đã xử lý.

Codex đã đọc AC sống qua đúng linear_zero_door: ZER-8 Backlog, ZER-5 In Progress; nội dung AC khớp snapshot. ZER-32/33 Done, AC con checked và completedAt/receipt khớp ghi chú. Trạng thái này là lúc đọc, không thay cho Linear sống. Đã đọc toàn artifact và đối chiếu SCOPE, nguồn nghiên cứu/verification/provider, ZER-32 cùng contract trực tiếp của ZER-9 và ZER-22; không kiểm producer runtime.

Baseline nhận: HEAD 968cc50f3797c243b8fa26e5327db647a8644802; nhánh zer-34-lab-acceptance; artifact SHA-256 51ee6e1199a63fdef388ebbbe0857737ae0d146c5ef38742d30b51ff0ec1adfd. Bản nhận và script gốc được giữ tại scratch/zer8/codex/. Ghi chú Claude ở mục 6/7/10 mô tả tự kiểm lúc nhận; kết luận retest hiện hành là mục này.

| Finding (P2, đã sửa) | Bằng chứng/ảnh hưởng của bản nhận | Sửa và retest |
| --- | --- | --- |
| RV8-01 — cohort và phép chấm | Mục 5.2 ghi C1 cần quyết định “nếu trigger”, trái quy tắc giữ missed detection; macro C1–C4 chưa nói cách xử lý lớp rỗng, ví dụ pooled có cả C5 có thể bị dùng nhầm | decision_required/tập A khóa trước run; giữ C1 không trigger; thiếu cohort là UNKNOWN_COHORT; trọng số bốn lớp cố định, không bỏ lớp rỗng; tách pooled và macro. M1c có coverage tập chấm được; block cần tập nguồn khác rỗng và tham số hợp lệ; attempt lỗi đầu không bị thay bằng quyết định đến muộn. Retest cohort, macro và nhánh lớp rỗng đạt |
| RV8-02 — cửa sổ benign | score.py: T=30 s, slot=60 s gây ZeroDivisionError; T=61 s có alert ở 0/60 cho 2/1=200%; alert ở -1/1800 vẫn cho 2 episode trong cửa sổ [0,1800). Không khai báo coverage nên có thể biến collector chết thành zero alarm/action | N_slot=ceil(T/w_b), slot cuối ngắn khai báo rõ; half-open W thống nhất cho alert/action/episode; coverage thiếu mặc định unknown, tỷ lệ slot báo cận; episode thiếu stream không được coi là giá trị thật hoặc cận dưới. Log action/probe thiếu không suy zero/harm-free. B0 detector tắt là N/A; tác hại C1 báo riêng. Phản ví dụ và ca sạch cũ đều đạt |
| RV8-03 — chấm guard khi thiếu nhãn | guard_metrics([{acceptable=None, guard=REJECT}]) cho false_block=1, dù chưa biết action có đúng không | Tách true_block/false_block/unknown_block, giữ tất cả trong mẫu số và báo coverage; chấm từng proposal thay vì dùng nhãn first decision cho mọi proposal cùng incident. Retest ba nhánh và nhiều proposal cùng incident đạt |
| RV8-04 — R(t), missing và median | Mục 3.2 nói cùng cap_rec thì không lệch do censoring, và R(cap)<50% suy median>cap; 4/10 recovered +2/10 missing cho cận [0,4;0,6] nên median chưa xác định | R_lower/R_upper theo thời điểm, giữ UNKNOWN_EFFECT/missing không có gốc thời gian; chỉ tuyên bố median>cap khi upper<0,5. Cặp thiếu/không đủ điều kiện được báo riêng, không ép thành 2×2 nhị phân hoặc bỏ cặp. Retest cận/median UNKNOWN, >cap và ≤cap đạt. Khoảng thiếu dữ liệu không gọi là khoảng tin cậy; phương pháp CI formal cần khóa theo thiết kế phụ thuộc thực |
| RV8-05 — contract và khẳng định vượt nguồn | Bảng bất biến đòi cùng prompt version cho B2/B3, mâu thuẫn thay phân vai; mất attack_command tự thành effect UNKNOWN dù có T_eff độc lập; scan từ khóa cố định có thể gắn nhãn rò cho tên service chung; câu MTTD bắt đầu từ T_det sai | Prompt riêng theo vai trò có version và khóa trước formal, model/evidence/tools tương đương; effect theo bằng chứng độc lập của ZER-32; scan theo field/provenance, tách nghi vấn với bằng chứng rò; MTTD từ effect tới detect. Bổ sung cảnh báo ước lượng giờ lab không phải trần thực thi, không khẳng định B3 ít công sức khi chưa đo. Đối chiếu nguồn/consumer và đọc lại delta đạt |

**Kiểm thực hiện.**

- Trước sửa: tác giả 32/32 expectation; năm mutant bị bắt, đối chứng sạch khớp (6/6 lượt); selftest checker 6/6; kiểm gói 31/31. Các phản ví dụ ở bảng trên vẫn tái lập lỗi dù suite đó PASS.
- Sau sửa: scratch/zer8/codex/retest.py đạt **45/45 OFFLINE**. Gồm giữ 32 expectation cũ (một phép đối chiếu tổng), năm mutant cũ, case mới của cohort/macro/benign/guard/R(t), 71 nguồn bảo toàn và năm blob nguồn đã nghiệm thu. Kết quả JSON ở scratch/zer8/codex/retest-result.json. Đây không phải 45 phép kiểm runtime, cũng không phải 45 test độc lập của hệ thống.
- Soát cuối bổ sung hai đối chứng EMPTY/NO_ELIGIBLE cho cohort: helper mới ban đầu lọc no-effect trước khi xác định trạng thái, làm ALL_NO_EFFECT thành EMPTY. Codex đã sửa helper, cả hai đối chứng đạt và tổng retest thành 45/45. Đây là sửa bộ tính minh họa mới, không đổi nguồn đã nghiệm thu.
- Bản tính mới scratch/zer8/codex/score_review.py chỉ minh họa ranh giới đã sửa. score.py/check.py tác giả không đổi; score.py còn các giới hạn bản cũ, không dùng làm scorer formal. Chưa kiểm tham số action thực, schema runtime, thuật toán bootstrap hay producer lab.
- Kiểm ZER-5 độc lập: SCOPE và hai cặp artifact/review ZER-32/33 giữ hash, byte blob tại 1f43ff1/8e7b74f/10a26b0 khớp. Đã đọc receipt Linear con; AC-01 ghi nhận đúng phạm vi, AC-02 định nghĩa/KPI giữ ngưỡng, AC-03 baseline/source ledger giữ UNKNOWN lịch sử. Không coi child Done tự đóng parent; merge tài liệu N/A theo WORKFLOW, không là thiếu bằng chứng runtime của ZER-5.
- 71 nguồn đã bảo vệ giữ nguyên, gồm 9 CSV; dirty ngoài phạm vi không đổi. Chỉ artifact ZER-8, phần nối hai ghi chú issue, con trỏ NOW và scratch/zer8/codex/ được sửa. Hash cuối artifact ở handoff note, không tự ghi vào file.

**Còn cần Hoàng chốt (không phải lỗi giao lại Claude):** nghiệm thu ZER-5; chấp nhận hướng phương pháp M1/macro, B2 báo KPI phục hồi, R(t) có cận và cách chấm benign; chọn B3 có điều kiện hoặc bỏ claim RQ2; nguyên tắc nguồn lực và che lịch BM. Khuyến nghị giữ B3 trong thiết kế có điều kiện, chỉ triển khai/pilot/formal khi budget và quyền tương ứng được cấp; không gọi “có điều kiện” là đã cấp ngân sách. Các tham số/số lượt formal vẫn chốt ở ZER-53 sau pilot. Chưa duyệt hay chi USD nào trong gói này. Không đóng G0: backend thật ZER-36/ZER-7 chưa có evidence mới.


## 12. Hoàng chấp nhận hướng thiết kế — 19/10/2026, 08:14 +07:00

Sau báo cáo Codex đã sửa RV8-01…RV8-05, retest 45/45 OFFLINE và câu hỏi “Bạn đồng ý nghiệm thu ZER-5 và hướng thiết kế này cho ZER-8 chứ?”, Hoàng trả lời “được” trong chat ZD2-CODEX. Bản đã review trước receipt có SHA-256 bb27ff8839b35cac1343f5a57eaaf5db39b3975662df56f2d8075436f93459a5.

Phạm vi chấp nhận: giữ B3 trong thiết kế có điều kiện, chưa claim ưu thế chia vai trò trước đối chứng; M1 là metric chính của RQ1/RQ2 theo định nghĩa được review; B2 là cấu hình báo KPI phục hồi. Các quy tắc sửa số học/missing/cohort trong mục 11 giữ hiệu lực. Nghiệm thu ZER-5 ghi riêng trong scope-and-criteria.md.

Ngân sách và giờ cho pilot/formal chưa được cấp, chưa có quyết định người vận hành/cách che lịch BM. Trần 1 USD kiểm backend R0 vẫn là đề xuất chưa được duyệt; 300 USD credit do người dùng báo không phải ngân sách được phép chi. Vì vậy chưa kết luận AC-02 ZER-8 hoàn tất hay ZER-8 Done; cần cụ thể hóa nguồn lực ở ZER-36/7 và trước pilot/ZER-22/ZER-53 theo mục đích. Không yêu cầu chọn lại B3/M1/B2 đã được chấp nhận.

Receipt này không cấp quyền commit/push/PR/merge, sửa Linear, chạy lab/API/model hoặc chi tiền. Không có runtime mới; G0 vẫn chưa nghiệm thu.

## 13. Hoàng chốt nguồn lực pilot và BM — 19/10/2026, 11:26 +07:00

Trong chat ZD2-CODEX, Hoàng trả lời **“Đồng ý gói đề xuất”** cho gói nguồn lực/cách vận hành dưới đây. Đây là quyết định kế hoạch R0, không là lệnh chạy lab/API ngay. SHA-256 trước bổ sung quyết định: 43715562f431ed1c5cf60747e15d73304cc85508c6e0a6da95936e88e3c8f4b5. Hướng phương pháp/B3/M1/B2 đã chấp nhận ở mục 12 giữ nguyên; không mở lại RV8-01…RV8-05.

- **Pilot vòng đầu:** trần **5 USD API**, tối đa **2 giờ mỗi phiên**, **8 giờ lab tổng cộng**. Đây là trần được duyệt cho lập kế hoạch, không dự báo đủ hoàn tất mọi cell/số lặp, không phải quỹ giờ mỗi tuần và không là số giờ đã chạy. Hết bất kỳ trần nào thì dừng, ghi mọi failure/thiếu coverage và đánh giá lại; không tự cắt case/nhóm rồi nhận pilot đầy đủ.
- **BM:** Hoàng là người vận hành. Harness phải giấu thứ tự case và onset; seed/manifest chứa đáp án ở phía evaluator, không đưa vào dashboard vận hành. Vì Hoàng biết thiết kế case, chỉ nhận che thứ tự/onset, không gọi blind hoàn toàn. Nếu lịch/onset thực tế bị lộ thì gắn cờ và báo giới hạn; xử lý trial bị lộ theo phương pháp đã chấp nhận, không âm thầm bỏ. BM giữ cùng action budget/runbook theo mục 4; không tự biến thành nhóm có guard AI.
- **B3:** giữ có điều kiện theo mục 12; quyết định triển khai/đi formal và claim RQ2 tại ZER-22 sau pilot có số đo thật. Không dùng trần 8 giờ để suy số mẫu hoặc claim ưu thế.
- **Formal:** chưa cấp ngân sách/giờ hoặc quyền thực nghiệm; ZER-53 khóa sau số đo pilot, gồm số lượt, horizon và tiêu chí còn mở của ZER-32. Không cần bịa số formal để hoàn tất thiết kế R0.
- **Tách ngân sách:** 1 USD + hard limit OpenAI hiện tại là kiểm backend R0 theo xác nhận Hoàng sau mục 12; 5 USD ở đây là trần pilot đề xuất đã được chấp nhận về kế hoạch, không tự tăng hard limit project. Chưa đọc lại dashboard hoặc xác minh số dư/expiry hiện tại. Chuẩn bị pilot phải đối chiếu headroom, cấu hình thực thi và quyền chạy riêng; không coi số dư 300 USD là quyền chi toàn bộ.

Với quyết định này, khoảng trống nguồn lực/BM ở AC-02 đã được xử lý ở mức thiết kế R0. Toàn bộ ZER-8 còn cần kết luận review/nghiệm thu và chia sẻ artifact trong quyền thực tế; chưa tự đặt Done hoặc chốt G0. Không chạy lab, gọi API, đổi Linear, commit/push/merge trong bước ghi receipt này.
