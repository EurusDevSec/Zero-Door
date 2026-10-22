# ZER-11 / ZER-39 — RT2 MANUAL/RULES trên image production

**PASS_SCOPED_RT2; chưa phải issue Done hoặc G1 PASS.** Quyền Hoàng: `call_ceeb7a350665410ab2df1b2bf7a3471b`. HEAD `169413303340fc01eea8597c121ce39455892af0`; nhánh hiện có `zer-10-independent-measurement`; chưa commit/push/PR/Linear. Khoảng được dùng: **23:58:48 ngày 21/10–00:18:39 ngày 22/10/2026, giờ Việt Nam**, tổng 1.191,619 s dưới 45 phút, gồm cleanup. Raw lưu UTC.

## Kết quả và giới hạn

| Phần kiểm | Kết quả thực | Giới hạn kết luận |
| --- | --- | --- |
| BM | 81 mẫu GET frontend trong 180,386 s; 14 lỗi và67 đạt được giữ. DETECTED thật, một DECISION MANUAL từ console O riêng; guard trả 409 R1_EXECUTOR_DISABLED; consumer audit không tự quyết định | Operator được script mô phỏng; không phải BM do người vận hành mù. HTTP availability, không phải probe nghiệp vụ/Gaia |
| B1 | Một DETECTED synthetic trong run riêng → đúng một DECISION RULES qua consumer thật, không bản trùng | Positive control transport, không chứng minh recovery |
| B2/B3 | Consumer audit AUTO_DECISION_DISABLED_FOR_GROUP, không DECISION hoặc action | Không có LLM producer trong lượt này; không chứng minh AI thành công |
| Source/image | Build/import đúng một image; sáu pod attest source và driver đạt; bốn actor giữ source/ENTRYPOINT production, health transport R1 và executor disabled | Không patch/fake executor trong lab |
| Auth/separation | Token guard sai 401; O thiếu token 401; console không truy cập control 9140 và không đọc gateway/rules keys | Kiểm đường truy cập này; không thay đánh giá mọi đường mạng trên cluster |
| Raw/cleanup | 14 envelope O seal/export; 98/98 kiểm độc lập đạt. Namespace tạm vắng; cả 13 deployment giữ UID/spec/replicas và Ready; quota/HPA/target policy UID/spec không đổi | Đã xóa đúng một pod frontend theo UID; pod mới do controller, deployment không đổi |

**Không gọi LLM/API trả phí, không chấm MTTD/MTTR, không claim human-blind BM, AI quality hoặc phục hồi nghiệp vụ từ RT2.** Đồng hồ envelope UNKNOWN. Bằng chứng B0/KPI/dashboard ở [RT1](../runtime-01/README.md) giữ nguyên, kể cả HPA no-effect, quota chặn thêm pod, PROBE_GAP và cleanup cart chưa xác minh.

## Bằng chứng đọc trực tiếp

- [Receipt host](receipt.json), [assessment boundary](assessment.json), [audit độc lập](independent-audit.json), [mã audit](independent-audit.py).
- [Summary/81 quan sát](summary.json), [warm-up riêng](warmup.json), [operator receipt](manual.json), [log actor](logs.json), [kiểm network](boundary-network.json).
- Raw và manifest: [BM](raw/BM/O.jsonl), [B1](raw/B1/O.jsonl), [B2](raw/B2/O.jsonl), [B3](raw/B3/O.jsonl). BM run `run_448f91cf7fca4e89ba40a4b957f86a96`.
- [reproduction.zip](reproduction.zip):168 file, gồm mọi receipt/argv/result, baseline/postflight, source/image attest, log build, lịch sử chuẩn bị, raw của cả lần lỗi, nguồn checker/host và snapshot source cuối. SHA-256 **`02f98226164274f135ddde74ed8d8e9c9d1a48184c106b0bd29577adab7a5860`**. [Verification/hash từng entry](verification.json).
- Khóa Secret thử và private-resources.json **không** nằm trong archive; scan giá trị khóa thực đạt. Giữ các bundle private trong scratch, không commit. Image mới được giữ, không prune image dùng chung.

## Hai lần chuẩn bị lỗi được giữ nguyên

1. Attempt01 dừng **trước ghi cluster** vì host so nhầm Docker OCI index digest với CRI config digest. Sửa phép kiểm host; xác minh hash chuỗi index → linux/amd64 manifest → config và RootFS. Dùng lại image đã build/import, không build/import lần hai. Receipt và script trong archive.
2. Attempt02 có ba timeout ban đầu khi kết nối, dừng trước fault; raw chưa seal được giữ. Namespace dọn sạch và các deployment trả baseline. Cùng tên namespace được tạo lại ở attempt03 với UID mới ghi trong receipt; không thêm target hoặc fault. Không coi lần này PASS. Không biết chính xác tổng GET vì observer còn chạy đến lúc pod bị dọn; snapshot có 46 mẫu không phải tổng cuối.
3. Attempt03 warm-up riêng10GET200, rồi bắt đầu đầy đủ cửa sổ 180 s; có ≥10 mẫu khỏe trước khi xóa pod. Không bỏ bất kỳ mẫu lỗi nào trong cửa sổ chính; cuối cửa sổ vẫn có timeout và được giữ. Dừng/xóa actor theo UID trước seal để không còn writer muộn.

Deadline và request cap dùng chung cho cả ba lần, không đặt lại. Từ vòng đời observer lần02 cộng biên 10 s, cận trên bảo thủ167 GET. Phần còn 193 được chia tối đa 20 warm-up +173 quan sát; lần03 dùng interval 2 s, warm-up 10 và81 mẫu. **Cận trên tổng ≤258 GET**, dưới 360; không nói số thực chính xác. Một pod delete tổng; các attempt trước đều0. Hạ rate/cap không thay cửa sổ hay criterion lỗi thật. Tool chỉ cho siết interval/cap, có test biên từ chối giá trị vượt trần/NaN/bool.

## Kiểm và thay đổi cuối

- RT2 suite cuối **4/4 trên mỗi production pin** Nemesis/Hephaestus; tiến trình Uvicorn và gateway thật trên loopback, chỉ observer HTTP được inject trong test. Test không cấp bằng chứng runtime.
- Mode hồi quy 7/7 ở gói chuẩn bị; Bandit 0 finding, Bash syntax và diff-check đạt. Log cảnh báo parser chú thích nosec được giữ. Không chạy lại full RT1suite đến xanh; các failure lịch sử vẫn còn.
- Kiểm độc lập không import assessor/host: envelope/raw manifest hash, IDs/context/causation, MANUAL/RULES/disabled audits, source attests, request/timecap và đọc cluster sau cleanup. Một lỗi kiểu trong checker ban đầu (string401 so với integer401) đã sửa sau đối chiếu producer; raw không thay.
- Delta runtime chỉ thêm khả năng **siết** interval/max_gets cho driver và regression; không sửa Hephaestus/guard/event_pipeline/scorer/RT1. Hash bảy nguồn bảo vệ vẫn giữ. [Gói chuẩn bị](../rt2-preparation/README.md) là snapshot lịch sử ba test; không sửa hash cũ thành hash mới.

## Đối chiếu AC và bước còn lại

| AC | Bằng chứng để reviewer/Hoàng nghiệm thu |
| --- | --- |
| ZER-11 AC-01/02 | Dashboard không số giả; read-only S/export/hash và browser/offline ở gói gốc, fix-01 và RT1 |
| ZER-11 AC-03 | Mode tests/guard; RT2 actor production + MANUAL-refusal, RULES positive control, AI disabled audit, giới hạn như trên |
| ZER-11 AC-04 = ZER-39 AC-01 | B0 profile/guard, RT1 native controller và HPA no-effect, độc lập nghiệp vụ/ownership; không đổi claim HPA thành recovery |

Đây là gói kỹ thuật đã có runtime trong phạm vi được duyệt. Còn **publication, CI từ xa, review/merge và Hoàng chấp nhận kết quả** trước Done; G1 cần kiểm gate riêng. Chưa có quyền publication/Linear cho gói này. Không chuyển vòng sửa mới sang Claude.
