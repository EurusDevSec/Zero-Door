# Codex review — ZER-32

**Verdict hiện tại: ACCEPTED — audit/fix đạt, Hoàng chấp nhận D-01…D-05 ngày 18/10/2026, 22:48 +07:00; xem receipt cuối file.**

**Lịch sử bản đầu: NOT READY — sửa gom RV-01…RV-03 rồi retest.** Review tài liệu và logic offline ngày 18/10/2026, 22:14–22:18 +07:00; không là kết quả lab. Claude đã bàn giao quyền ghi; Codex chỉ tạo báo cáo, nối handoff và cập nhật NOW, không sửa artifact/script của Claude.

## Bản được review và nguồn

- Target: gói local ZER-32, không phải PR #19 hoặc mã ZER-35. Nhánh codex/zer-35-local-lab, HEAD a224ce54fc0e742bbb647c61e6e9201094a9de25. Không có staged diff. Base tracked = HEAD; artifact untracked được đọc toàn bộ, không có merge-base áp dụng.
- Artifact [requirements-and-kpi.md](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md), SHA-256 afff4068fc0ae5190f2d14f6b089c4e0c883174ff64ce67e6d19e23e6abc370c.
- Bộ kiểm scratch/zer32/kpi_check.py, SHA-256 725ab5a3eb6f4e2d9fb523aa4b1c6a1e89ca4bb3ed27e82f40f05d2441f9e9f2. Scratch bị ignore, không phải mã ứng dụng hoặc artifact đã publish.
- Đọc lại AC sống qua linear_zero_door: [ZER-32](https://linear.app/zero-door/issue/ZER-32/lap-ma-tran-yeu-cau-va-djinh-nghia-kpi), [ZER-5](https://linear.app/zero-door/issue/ZER-5/khoa-pham-vi-va-tieu-chi-djanh-gia); consumer trực tiếp [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi), [ZER-38](https://linear.app/zero-door/issue/ZER-38/dung-probe-nghiep-vu-djoc-lap). Đúng workspace zero-door. AC-01 ZER-32 / AC-02 ZER-5 khớp phạm vi đã giao. Không sửa Linear; downstream khác chưa đọc live.
- Đối chiếu SCOPE, bản trích thuyết minh có Pn/hash, verification, ghi chú event/probe. Không đọc lại DOCX gốc. Ma trận 22 hàng phủ các đoạn bắt buộc, sản phẩm và xác nhận hiện hành; không phát hiện việc tự hạ ngưỡng.
- Dirty trước review: AGENTS.md, NOW.md, README.md delivery, scope-and-criteria.md; untracked WORKING-AGREEMENT.md và ZER-32/. Giữ nguyên ba file quy ước ngoài gói. Những thay đổi mà Claude ghi nhận đã có trong trạng thái tiếp nối, không suy đó là Claude sửa.

## Findings

### RV-01 — [P2] Tính hợp khoảng chưa quan sát với outage trước khi kết luận uptime

**Vị trí:** [requirements-and-kpi.md:205](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md:205), công thức dòng 215 và giới hạn dòng 355. Script: availability dòng 249, 254–257.

Công thức cộng độ dài D_max và U mà không loại phần giao. Script còn lấy max(U từng luồng) thay vì hợp khoảng trên mọi luồng bắt buộc. D-05 vì vậy chưa đủ tin cậy để chấp nhận.

**Tái hiện OFFLINE, W = 14.400 s, probe 1 s:**

1. Một luồng: đạt 0–99; lỗi 100–104; không mẫu 105–113; lỗi 114–119; đạt từ 120. Actual D_max = 21 s, U = 9 s, D_max + U = 30 s. Nhưng U nằm toàn bộ trong [99,120), nên hợp chỉ dài 21 s. Không được đếm 9 s hai lần.
2. Hai luồng bắt buộc, không có mẫu lỗi: A thiếu mẫu 1001–1009; B thiếu 5001–5009; mọi mẫu khác đạt. Actual U = 9 s, A_lower = 0,999375, **PASS**. Hợp U = 18 s, A_lower theo chính mô hình đề xuất = 0,99875; A_upper = 1, nên expected **UNKNOWN**. Đây là false PASS có thể làm sai nghiệm thu 99,9%.

Các case hiện có chỉ có một luồng bị gap và gap ngoài outage nên không bắt được. Dòng 355 đã nêu đơn giản hóa nhưng chưa khắc phục false PASS hay công thức cộng trùng.

**Sửa:** giữ các khoảng thời gian, hợp U trên mọi luồng; cận dưới dùng độ dài hợp D_max với U. Làm rõ U trong cận trên, không vừa gọi một khoảng là UNKNOWN vừa coi nó là downtime chắc chắn. Thống nhất gap/outage chưa đóng và cắt theo W. Nêu giả định của ước lượng từ probe rời rạc: cận theo mô hình lấy mẫu không chứng minh không có outage ngắn giữa hai mẫu đạt. Thêm hai case trên, gap chồng giữa luồng, outage chưa đóng; sửa công thức/bảng kiểm/giới hạn cùng nhau.

### RV-02 — [P2] Tách UNKNOWN_EFFECT khỏi NO_EFFECT trước khi chọn mẫu số

**Vị trí:** [requirements-and-kpi.md:86](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md:86), dòng 268 và case F dòng 299. Script: evaluate dòng 91–93; aggregate dòng 169–171.

Chưa có trạng thái “không xác định được effect vì thiếu bằng chứng”. Script coi mọi eff=None là NO_EFFECT rồi loại khỏi N. Thiếu mốc không chứng minh attack không có hiệu lực; quy tắc missing không thành dữ liệu rỗng/PASS chưa bao phủ bước chọn N.

**Tái hiện OFFLINE:** sao chép A, chỉ làm mất eff, giữ req/det/action/probe. Actual class=NO_EFFECT. Gộp A hợp lệ với bản thiếu effect: N=1, excluded=[UNKNOWN_EFFECT], tỷ lệ MTTD/MTTR=1/1 và mean verdict PASS. Lượt thiếu đã biến mất khỏi đánh giá.

**Sửa:** phân biệt confirmed effect, confirmed no-effect và UNKNOWN_EFFECT/không đủ quan sát. Chỉ NO_EFFECT có bằng chứng đủ cửa sổ mới được loại theo quy tắc khóa trước. Nêu số requested, confirmed-effect, confirmed-no-effect, unknown eligibility; quy tắc verdict/cận phải bảo toàn nhóm chưa rõ, không âm thầm PASS. Không gán effect/duration giả. Thêm case thiếu effect timestamp, mất probe toàn cửa sổ effect, no-effect được xác minh; cập nhật nhu cầu dữ liệu ZER-37/ZER-38.

### RV-03 — [P2] Định nghĩa kết quả khi N=0

**Vị trí:** [requirements-and-kpi.md:148](R:/_Projects/Eurus_Workspace/zero_door/docs/evidence/ZER-32/requirements-and-kpi.md:148), bảng verdict dòng 160–164. Script: mean_verdict dòng 156–165.

Run có thể không có incident đủ điều kiện vì mọi fault được xác minh NO_EFFECT, hoặc dataset không có incident. Tỷ lệ chia N và quy tắc “mọi lượt quan sát được” chưa có nhánh tập rỗng. Script tính mean=None rồi so với ngưỡng.

**Tái hiện OFFLINE:** aggregate tập chỉ chứa một phần tử class NO_EFFECT trả TypeError: '<' not supported between instances of 'NoneType' and 'int'. Không được coi mean rỗng, 0/0 hoặc “không có lỗi” là PASS.

**Sửa:** thêm EMPTY/NO_ELIGIBLE với mean/rate không xác định và verdict không phải PASS; vẫn xuất số requested/no-effect/unknown. Thống nhất MTTD, MTTR, reaction. Thêm dataset rỗng, tất cả confirmed-no-effect, toàn unknown-effect và phân biệt ba trường hợp.

## Kiểm độc lập và giới hạn

| Kiểm | Expected | Actual / verdict |
| --- | --- | --- |
| Chạy nguyên bộ kiểm Claude | Exit 0, 112 so khớp | Exit 0; 112 dòng OK; SUMMARY: ALL OK — OFFLINE |
| RV-01 | Hợp khoảng/verdict đúng | Cộng trùng 30 s thay vì 21 s; false PASS với hai gap rời — xác nhận finding |
| RV-02 | Thiếu effect không thành confirmed no-effect | NO_EFFECT, loại khỏi N và PASS phần còn lại — xác nhận finding |
| RV-03 | Kết quả không xác định, không crash | TypeError — xác nhận finding |
| Hash artifact | Khớp bàn giao | Khớp toàn bộ SHA-256 |
| Link local trong artifact | Có đích | 9 đường dẫn duy nhất tồn tại |
| git diff --check trước review | Không lỗi whitespace tracked | Exit 0 |

Lệnh: python scratch/zer32/codex_review_check.py qua Git Bash. Probe reviewer nạp đúng script Claude, bắt SystemExit và chỉ dùng dữ liệu giả định; không sửa script gốc. Lần đầu phần in JSON của reviewer lỗi vì Python set; đã sửa phần in, không đổi case. Lần chạy lại exit 0, in các sai khác/exception ở trên. Exit 0 ở đây nghĩa là hoàn tất tái hiện, **không** là gói KPI PASS.

Bảy mutant là bằng chứng tự kiểm Claude; Codex không chạy lại toàn bộ mutant, không lấy đó làm chứng nhận đủ tình huống. Tái chạy 112 kiểm và phản ví dụ tập trung đủ xác định finding hiện tại.

GitNexus detect_changes(scope=all) trả 0 changed symbols/0 affected processes trên 4 file tracked; index chậm 3 commit tại 6337b319b075bf389d484a6be13a4bc094f94a82. Artifact untracked được đọc trực tiếp. Không dùng zero hit chứng minh đúng logic, không refresh hay claim review graph hoàn chỉnh. Không có symbol ứng dụng đổi để chạy impact/taint/PDG. Không build/CI/runtime/LLM/lab; N/A cho gói này.

## Gói sửa và bước tiếp

- Claude sửa gom RV-01…RV-03 trong artifact và bộ kiểm scratch hiện có. Giữ nguồn/ngưỡng 60/120/180 s, 99,9%; không mở rộng sang triển khai probe.
- Tái tính case cũ và bổ sung; ghi input/expected/actual/verdict đủ tái lập trong artifact khi không có scratch. Không chỉ tăng assert hoặc đổi expected cho khớp actual.
- Cập nhật hash/handoff ở ghi chú issue: finding → cách sửa → case → kết quả. Không sửa báo cáo Codex để đổi verdict.
- Allowlist cũ: artifact, nối handoff scope-and-criteria.md, con trỏ NOW và scratch offline không track. Không source/config/CI/manifest/SCOPE/schema, lab/model/cloud, Git publication hoặc Linear.
- D-01…D-05 vẫn chờ Hoàng chấp nhận sau khi logic đã sửa. Không biến lỗi số học/missing thành quyết định phạm vi cho Hoàng. F-01…F-09 giữ ở protocol tương ứng. Không cần Hoàng trả lời từng D để sửa các finding rõ này.
- Codex nhường ghi cho Claude khi Hoàng chuyển gói sửa; sau handoff hoàn chỉnh sẽ retest delta/regression liên quan. Chưa Done.

## Chốt audit và tự sửa — Codex — 18/10/2026, 22:43 +07:00

**Kết luận hiện tại: READY FOR ACCEPTANCE — không còn finding kỹ thuật mở trong gói ZER-32.** Phần NOT READY ở đầu báo cáo là kết luận bản đầu afff4068, được giữ làm lịch sử; không áp cho artifact cuối dưới đây. Hoàng yêu cầu “audit này xong fix luôn đừng gửi nữa cho xong issue này”; Codex đã nhận quyền ghi từ bàn giao Claude và tự sửa, không chuyển tiếp sang Claude.

### Revision cuối và phạm vi

- HEAD/nhánh giữ nguyên: a224ce54fc0e742bbb647c61e6e9201094a9de25 / codex/zer-35-local-lab.
- Artifact Claude v2 nhận vào: 12ed9c5a87dc0a9aa77828bd09f6787fad027fa21b5b6aa5a6378d5f325c0f2b.
- Artifact cuối: **eb35f30bdd952ad81ded97d803b7c3cb736cd806dfd09f7a1e13b890646216e9**.
- Scratch checker cuối: ed40ab524c33a8b04374b9b748d6fe8259bac3e252be9e073fc4c9255a8c56f1.
- Mutant runner cuối: a28aa4f8c4bb8f3aecd81e5660acc245910bcf886d46ccfb77339ecea7cb39cc.
- Bộ tái hiện cuối: scratch/zer32/codex_final_check.py, SHA-256 b8cb2c1be2e4f57c4209b36ba1d8c8c0568ef4b599bea41b427d8bb21f091cd9.
- Codex sửa artifact, bổ sung báo cáo hiện tại, nối handoff, đổi con trỏ NOW; các checker/runner trong scratch bị ignore. Bản checker Claude v2 trước khi Codex sửa lưu ở scratch/zer32/v2/claude-final-kpi_check.py. Không sửa mã ứng dụng hoặc schema.
- SHA-256 AGENTS.md, docs/delivery/README.md và WORKING-AGREEMENT.md khớp lúc nhận lượt này; mọi dirty ngoài scope được giữ nguyên. Không Git publication hoặc Linear mutation.

### Finding → sửa → retest

| Nội dung | Sửa / kiểm | Kết quả |
| --- | --- | --- |
| RV-01 | Đọc delta, tái chạy U5/U6 và hồi quy hợp U/outage. U5 D_lower 21 s và UNKNOWN; U6 U 18 s và UNKNOWN | CLOSED |
| RV-02 | Tái chạy A mất T_eff cùng A hợp lệ: N=2, unknown=1; mean verdict UNKNOWN; confirmed no-effect có chứng cứ mới rời N | CLOSED |
| RV-03 | Dataset rỗng EMPTY; toàn confirmed-no-effect NO_ELIGIBLE; toàn unknown-effect vẫn ở N, UNKNOWN | CLOSED |
| CF-01: thiếu luồng bắt buộc / W không hợp lệ | Tái hiện trước sửa: không luồng → PASS; W=0 → ZeroDivisionError; W âm → PASS. Tự thêm guard, metrics không xác định và UNKNOWN với lý do NO_REQUIRED_FLOWS/INVALID_WINDOW. Luồng khai báo nhưng mất mẫu hoàn toàn vẫn là U=W | FIXED, U10–U13 PASS |
| CF-02: cắt mất bằng chứng ổn định ở cap_rec | Trước sửa: mẫu đạt từ 588, K=3 cho T_rec=590 nhưng cap=600 cắt mất S tới 620, dù raw có mẫu tới 650; bị MISSING_PROBE sai. Cho phép lấy tail tới cap+S để chứng nhận ứng viên T_rec≤cap; không nhận ứng viên muộn | FIXED, R1–R5 PASS |
| CF-02: dừng fault trong S | Tách T_rec khỏi recovery_verified_at=T_rec+S. Case T_rec=43, verified_at=73, stop=50 → AFTER_STOP, không đạt. Giữ fault tới xác minh hoặc horizon cap+S đã khóa, không kéo dài threshold KPI | FIXED, R6 PASS |
| Nhất quán tài liệu | T_eff hợp lệ do evaluator phát là bằng chứng CONFIRMED; thiếu cả T_eff lẫn record kết luận mới UNKNOWN_EFFECT. Sửa câu tuyệt đối “missing không bao giờ PASS” vì U7 có thể PASS sau khi tính đủ budget. Ghi CPU limit thiếu/0 hoặc usage thiếu → UNKNOWN | Đã đồng bộ định nghĩa/consumer, không hạ ngưỡng |

### Bằng chứng kiểm cuối

- python scratch/zer32/codex_review_check.py: **190 dòng OK**, SUMMARY: ALL OK, author exit 0. Các phản ví dụ cũ cho giá trị đúng. Dòng ACTUAL_ADDITIVE_MS=30000 trong probe lịch sử là phép cộng do probe tự in để minh họa lỗi cũ, không phải D_lower_bound đang dùng (21000).
- python scratch/zer32/mutate.py: **18/18 mutant bị bắt**, mỗi mutant exit 1 có BAD, không Traceback. Runner được siết để crash không bị tính là kiểm logic thành công.
- Trong lượt sửa, mutant bỏ guard luồng lần đầu crash vì assert reviewer truy cập khóa input_status bị thiếu. Đã sửa assert dùng get để báo BAD; chạy lại toàn suite 18/18 không crash. Không sửa expected để che lỗi.
- python scratch/zer32/codex_final_check.py: tái hiện NO_REQUIRED_FLOWS/INVALID_WINDOW → UNKNOWN với metrics null; luồng all-missing → [0,1], UNKNOWN; late recovery → (590000, FOUND).
- 10 đường dẫn local duy nhất trong artifact tồn tại; không có hàng bảng lệch cột. Hash ba file ngoài scope giữ nguyên.
- git diff --check sau sửa: exit 0. Build/CI/runtime/lab/merge N/A vì đây là tài liệu và số học offline; không gọi Docker/Kubernetes, attack/healer, model/cloud.
- AC sống ZER-32 đọc lại qua đúng linear_zero_door lúc 22:39 +07: outcome/AC không đổi so với review. Linear vẫn là nguồn trạng thái; chưa cập nhật field.

### AC và phần nghiệm thu còn lại

AC-01 ZER-32 / AC-02 ZER-5 đã có ma trận truy vết, định nghĩa MTTD/MTTR/total/reaction, downtime/uptime/mẫu số và cách báo cả MTTR 120/180 s; 60 s và 99,9% giữ nguyên. Bằng chứng ở mức **định nghĩa + kiểm logic offline** đã đủ review; không có claim đã đạt KPI thực nghiệm.

D-01…D-05 là các lựa chọn đo lường được Codex khuyến nghị, **chưa ghi là Hoàng đã chấp nhận**:

| Quy ước | Khuyến nghị cuối |
| --- | --- |
| D-01 | Mean là verdict chính theo P107, báo cả tỷ lệ từng lượt; missing → UNKNOWN, timeout/không đủ outcome → không PASS, N=0 có nhãn riêng |
| D-02 | Reaction từ detect đến action SUCCESS đầu tiên đã kiểm hậu điều kiện; tách khỏi MTTD/MTTR |
| D-03 | CPU tổng usage/tổng limit của container app trên Deployment; >80%, đề xuất duy trì 60 s; thiếu metric/limit → UNKNOWN. Tham số/pilot khóa theo F-06 |
| D-04 | T_rec ở mẫu đạt thứ K, chỉ xác nhận sau S; tách verified_at, giữ đủ quan sát; không tính đạt nếu stop trước xác minh hoặc recovery trước detect |
| D-05 | Uptime theo cận của mô hình probe rời rạc: hợp U/outage trên mọi luồng, PASS chỉ nếu A_lower≥99,9%; phần không kết luận được → UNKNOWN |

Cần Hoàng chấp nhận bộ diễn giải trên trước khi dùng làm chuẩn downstream; đây là quyết định phương pháp, không còn là yêu cầu gửi Claude sửa. F-01…F-09 vẫn khóa trong protocol ZER-53 trước formal run và không cần vận hành lab để nghiệm thu tài liệu này. Chưa tự ghi Done/đổi Linear hay commit/push; nghiệm thu tài liệu và cập nhật tracking là bước riêng sau chấp nhận.

## Hoàng chấp nhận — ZER-32 — 18/10/2026, 22:48 +07:00

Hoàng trả lời “được” khi Codex hỏi chấp nhận D-01…D-05 sau audit/fix hoàn chỉnh. **AC-01 ZER-32 / AC-02 ZER-5 được nghiệm thu ở phạm vi tài liệu và kiểm logic offline**; không còn finding kỹ thuật hoặc quyết định D mở. F-01…F-09 vẫn chốt trong protocol trước formal run. Bản kỹ thuật đã review: eb35f30bdd952ad81ded97d803b7c3cb736cd806dfd09f7a1e13b890646216e9. Artifact sau thêm receipt: a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c.

Không đổi công thức, checker hoặc case từ bản 190/190 OFFLINE đạt, 18/18 mutant bị bắt. Không cần chạy lại kiểm số học cho thay đổi ghi nhận chấp nhận. Không commit/push/merge, không chạy lab/model/cloud; trạng thái sống và receipt tracking đọc Linear. Không đóng ZER-5 vì còn phần nguồn/baseline riêng.

**Receipt Linear — 18/10/2026, 22:50 +07:00:** sau Hoàng chấp nhận, cập nhật riêng ZER-32: AC-01 checked, bổ sung receipt nghiệm thu và chuyển Done qua linear_zero_door. Đã đọc lại đúng URL zero-door, trạng thái Done, completedAt 2026-10-18T15:49:46.098Z và nội dung evidence khớp. Không đổi issue cha/assignee/relations.
