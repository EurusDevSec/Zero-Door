# R1 / G1 — receipt nghiệm thu tích hợp

**Kết luận kỹ thuật: G1 PASS trong phạm vi nền tảng sự kiện, phép đo và kiểm soát của R1.** Đã đối chiếu từng vế gate với raw, source/revision và kết quả tích hợp; không suy từ 8 issue Done. **Hoàng đã nghiệm thu G1 và cho phép chốt Git/Linear qua call_14679eef95074e0cb7e1f1e98d21556a.** Publication/CI/merge và read-back milestone là các bước tiếp theo; chưa nhận chúng là đã thực hiện.

Kiểm ngày **22/10/2026, 09:44 +07:00**; thời điểm máy ghi trong [JSON kiểm chứng](g1-verification.json) là UTC. Không chạy lab, gọi model, sửa mã sản phẩm, commit/push hay ghi Linear.

## Nguồn và revision

Gate sống đọc từ milestone **R1 — Sự kiện và phép đo**, ID 6d06ae3c-f27b-4ce9-bee9-3596221aaed7, project P-ZER-1, đúng workspace linear.app/zero-door/:

> Một sự cố có ID xuyên suốt, metric hồi phục/quyết định tái tính được; evidence không lộ đáp án, B0/MANUAL không auto-heal và guard hoạt động.

[README R1](../../delivery/milestones/R1-measurement/README.md) mở rộng cách kiểm: raw xuất được, probe nghiệp vụ độc lập, missing/failure không thành PASS, revision/config và bằng chứng truy cập được. Không thay AC, KPI ZER-32/ZER-8 hoặc phạm vi R2–R6.

- Main GitHub đọc trực tiếp: **5d55ac35f0e3aefb6147536747e593a1965df921**. Local HEAD 7d095fd70c8fdbf9f9e5749057f9e3252009234f có cùng tree; dirty tài liệu riêng được giữ ngoài receipt.
- Bốn PR tích hợp đã merge và là ancestor của main: [#24](https://github.com/EurusDevSec/Zero-Door/pull/24) (c09452a, ZER-9), [#25](https://github.com/EurusDevSec/Zero-Door/pull/25) (55200c9, ZER-12), [#26](https://github.com/EurusDevSec/Zero-Door/pull/26) (22a89db, ZER-10), [#27](https://github.com/EurusDevSec/Zero-Door/pull/27) (5d55ac3, ZER-11).
- Read-back CI PR: lần lượt **11 / 15 / 16 / 16 job SUCCESS**, mỗi PR có image publication SKIPPED đúng điều kiện. [CI cuối tại head nghiệm thu](https://github.com/EurusDevSec/Zero-Door/actions/runs/39708349809) bảo vệ measurement, contract/raw, guard/mode, hai production dependency graphs, Go race và image smoke.
- Read-back Linear: ZER-9/10/11/12 và ZER-37/38/39/40 đều Done, **18 AC đã tích, 0 AC chưa tích**. Nghiệm thu từng issue đã ghi trên Linear; phần trăm 100% không tự là verdict G1.

## Gate → bằng chứng → kết luận

| Vế G1 | Expected / actual và bằng chứng | Kết luận, phạm vi |
| --- | --- | --- |
| ID xuyên thành phần và raw xuất được | [ZER-9 actor runtime](../ZER-9/actor-runtime/README.md): Gaia production pod → HTTP → Kafka → recorder/PVC → Hephaestus production pod; cùng run/trial/incident/causation. Poison/good-next, redelivery, restart, seal/late/export có receipt. Chạy lại reconcile nguyên bản trên source lịch sử c09452a: **68/68**. | PASS runtime transport; alert synthetic, không coi là phát hiện fault thật. |
| Phục hồi do probe nghiệp vụ, metric tái tính được | [ZER-10 runtime](../ZER-10/runtime-01/README.md): Boutique và SQLite thật, **66 raw / 24 mẫu / 8 pha**, healthy/failure/restored, audit chạy lại PASS. [RT1](../ZER-11/runtime-01/README.md): **676 envelope**, cùng incident effect→business recovery **39,997 s**, 0 action ZERO DOOR. Tái tính bằng scorer hiện tại từ H/O và hai positive-control exports: score giống toàn bộ giá trị đã lưu (trừ generated_at), hai CSV giống từng byte. | PASS đường đo và tái tính recovery. B0 không có detector: MTTD/MTTR N/A; không gọi total recovery là MTTR. |
| Quyết định và mốc tính được đúng semantics | E01 từ fixture đã commit, qua Archive thật/seal/export → scorer/metrics hiện tại: **MTTD 30 s, MTTR 60 s, total 90 s, reaction 19 s**; một incident xuyên effect/detect/proposal/guard/action/probe. M1 pooled 1/1 CORRECT; M3 accept_correct=1; M4 fallback=0/1; M10 decision latency=2 s. [Bộ kiểm và oracle ZER-10](../ZER-10/fix-03/README.md), CI cuối có E01, 40 mutant và 178 đối chiếu. | PASS controlled integration, **SYNTHETIC/OFFLINE**. Macro M1 vẫn UNDETERMINED khi thiếu lớp; không nâng thành hiệu quả LLM/KPI runtime. |
| Ground truth không vào bên chữa lỗi | ZER-9 actor thực có key/role riêng, gate O-only trước trial, không raw H/PVC/token Kube; query Prom/ES qua O; canary H vắng trong O; audit CLEAN và ca cố ý lộ target/stream với ID hợp lệ bị bắt. Reconcile lịch sử xác nhận lại các điều kiện này. | PASS profile đã kiểm, khóa server node và chờ policy hội tụ. **RT1 leak audit vẫn UNKNOWN**, không gán CLEAN của run khác cho RT1; B0 không có healer hoạt động. |
| B0/MANUAL không tự heal | RT1: không DECISION/LLM/GUARD/action O, positive control B0 bị quarantine MODE_VIOLATION; native controller tạo replacement và probe xác nhận recovery. [RT2](../ZER-11/runtime-02/README.md): BM consumer không tự quyết định; 1 MANUAL scripted từ O-console bị executor từ chối **409 R1_EXECUTOR_DISABLED**; B1 có đúng 1 RULES; B2/B3 disabled và 0 decision. Raw RT2 có **14 event**, causal IDs khớp; giữ **14 mẫu lỗi / 81** trong đủ 180 s. | PASS ranh giới mode. MANUAL là script kiểm đường vận hành; chưa là BM người thật theo protocol formal. |
| Guard và CI bảo vệ các hành vi trên | [ZER-12 fix-02](../ZER-12/fix-02/README.md), [Claude retest](../ZER-12/claude-retest.md), [CI bootstrap](../ZER-12/ci-01/README.md): target/budget/auth/schema/role, duplicate/UNKNOWN/restart/expiry/Ack; remote Go race, production pins/image smoke. Lượt này chạy lại entrypoint mode **7/7**, command mode **3/3**; RT2 token sai 401, MANUAL 409 và không action thật. | PASS offline/CI + runtime boundary đã có; không coi fake executor là runtime fault/heal. |
| Dashboard/export và provenance nhất quán | RT1 browser và API đọc cùng score/CSV đã đăng ký; stopped/root_unchanged, không KPI giả. Lượt này tái tính score/CSV, kiểm **329 file source/evidence** trùng blob main, ZIP RT2 **168 entry** trùng hash. Bốn PR đã merge, các issue đã được Hoàng nghiệm thu. | PASS kết quả tích hợp/phép đo của R1; receipt G1 mới cần được chia sẻ và Hoàng nghiệm thu riêng. |

Đây là các bằng chứng bổ trợ tại những thời điểm/profile có ghi rõ. Không ghép chúng thành một trial tự nhiên duy nhất “fault → Gaia → LLM → heal → recovery”. R1 khóa hạ tầng đo/kiểm; vector có tác động, recovery executor, LLM và thí nghiệm so sánh thuộc R2–R6. Không yêu cầu các chức năng chưa đến milestone phải chạy để làm đẹp G1, cũng không nhận kiểm transport là dataset nghiên cứu.

## Kết quả tái kiểm và bảo toàn

- **444/444 điều kiện kiểm tổng hợp đạt**, gồm 329 đối chiếu byte với main; đây là số predicate, không phải 444 thử nghiệm độc lập. Chi tiết trong [g1-verification.json](g1-verification.json).
- Checker ZER-9 được chạy trên đúng source/receipt lịch sử, thay vì so hash Dockerfile/actor cũ với phiên bản đã đổi ở R1. Raw lịch sử khớp bản merge c09452a.
- Checker ZER-10 raw chỉ đọc được chạy nguyên bản. E01 dùng fixture/Archive/scorer hiện tại; RT1 dùng CLI verify-measurement.py --recompute với required-flow checkout và đầy đủ other-export.
- **Không chạy lại** runtime-02/independent-audit.py: script đó gọi kubectl và ghi lại file lịch sử. Chỉ đối chiếu raw/manifest/ZIP/source và kết quả audit 98/98 đã ghi, không làm mới thời gian cleanup.
- Mã audit điều phối và output đầy đủ nằm local scratch/g1/audit.py, scratch/g1/run-01/; không có test framework mới hoặc thay đổi producer/consumer/scorer.

## Giới hạn chuyển tiếp bắt buộc

1. **HPA NO_EFFECT:** quota chặn pod bổ sung; chưa chứng minh HPA phục hồi hay tăng năng lực phục vụ. Cần kiểm headroom trước thí nghiệm HPA tiếp theo.
2. RT1 giữ **PROBE_GAP**, uptime **FAIL/UNKNOWN**, metric/data **MISSING/UNKNOWN**, MTTR threshold **NOT_PASS/unobserved**, một cleanup cart **CONNECTION_RESET chưa xác minh**. Cleanup cluster không có nghĩa mọi dữ liệu nghiệp vụ đã sạch.
3. RT2 dùng HTTP availability observer, không Gaia/business recovery; B1 alert synthetic; B2/B3 không gọi LLM. Clock UNKNOWN và không chấm MTTD/MTTR RT2.
4. Cô lập mạng chỉ có bằng chứng trong profile đã gate; không khẳng định mọi node/CNI/startup window đã được bảo vệ. Lỗi đĩa tiêm offline không chứng minh mất điện/PVC hỏng thật.
5. Fixture SQLite AC probe là CRUD an toàn tối thiểu, **không hoàn tất ZER-41/SQLi/R2**. Chưa có kết luận AI tốt hơn RULES/BM, KPI formal, uptime 99,9% hoặc nghiên cứu/paper hoàn thành.
6. Cleanup dựa read-back lịch sử từng runtime; lượt G1 này không hỏi cluster hiện tại. Không có quyền lab/model mới từ receipt.

## Delivery và bước kế

**Hoàng đã nghiệm thu G1 trong phạm vi trên**, trả lời trực tiếp “Nghiệm thu G1 và cho phép chốt Git/Linear”. Quyền gồm commit/push đúng hai file receipt, mở rồi merge PR tài liệu khi CI đạt và ghi G1 PASS trên milestone R1. Publication/CI/merge/read-back chưa thực hiện tại thời điểm đóng gói này; receipt delivery cuối sẽ nằm trên milestone Linear, liên kết tới revision thực sau merge. Không tự đổi status issue khác, milestone date/assignment/relations hoặc chạy R2.

Đã đọc live ZER-13 cùng hai child ZER-41/42: bước R2 ưu tiên là **chốt thiết kế fixture/route/source-IP của ZER-13 AC-01 rồi dựng ZER-41**, sau đó mới executor ZER-42 và kiểm tác động/benign AC-04. ZER-6/9/12 đã Done, nhưng state Backlog và quyền triển khai/lab R2 không đổi. Không dùng fixture probe R1 để đóng child ZER-41.

## Quyền chốt delivery — 22/10/2026

Nguồn trực tiếp: call_14679eef95074e0cb7e1f1e98d21556a, câu trả lời của Hoàng ở trên. Chỉ publication hai file g1-acceptance.md và g1-verification.json; checkpoint NOW/README và dirty quy ước không thuộc commit. Không có quyền triển khai R2, lab/model hoặc đổi metadata khác. Hoàng chấp nhận các giới hạn đã ghi, không sửa raw/KPI để đổi kết quả.
