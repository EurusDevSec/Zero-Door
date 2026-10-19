# Issue — Thống nhất hợp đồng sự kiện và lưu dấu vết

[Milestone R1](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet). Nguồn đối chiếu: `R1-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Bước soạn draft S01 chỉ ghi `docs/design/r1-event-contract.md`. Có thể soạn khi lab/LLM chưa sẵn sàng; khóa schema và nghiệm thu vẫn chờ phụ thuộc R0. S02/S03 chưa mở allowlist mã, test hoặc schema dùng chung.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R1-T01-S01 | Chốt run_id, incident_id, action_id, timestamp và trạng thái của vòng phát hiện–phục hồi. | [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi) |
| R1-T01-S02 | Truyền ID qua Kafka/HTTP và lưu sự kiện gốc phục vụ tái tính. | AC của [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet) |
| R1-T01-S03 | Tách ground truth/log điều khiển khỏi evidence dành cho bên chữa lỗi. | AC của [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R1-T01-S01

Schema/version và ví dụ; mốc attack effect/detect/action/recovery/stop có nguồn ghi riêng. Terminal action SUCCESS/FAILED/PARTIAL được tách khỏi RECOVERY_VERIFIED.

### R1-T01-S02

Một chuỗi sự kiện xuyên thành phần; bản ghi bền vững có thể xuất và đối chiếu.

### R1-T01-S03

Phép thử kiểm tra prompt/query không lộ case label, attack command hoặc đáp án; ID trung tính vẫn truy vết được ở harness.

## Phụ thuộc cần đối chiếu

[R0-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/scope-and-criteria.md), [R0-T04-S03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md) (mục nguồn trong ghi chú).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## Gói ZER-37 cho Claude — 19/10/2026, 12:43 +07:00

### Kết quả và phân vai

Hoàng yêu cầu bắt đầu issue đầu R1 với Codex, Claude và Hoàng cùng làm. Gói này hoàn thiện bản contract ZER-37 để Codex review độc lập và Hoàng nghiệm thu, chưa triển khai producer/consumer. Claude là writer sau khi Hoàng chuyển prompt; Codex kết thúc ghi gói và chuyển sang reviewer. Không cần xin lại quyền cho sửa tài liệu/ví dụ offline trong allowlist này. Hoàng quyết định nếu có thay đổi phương pháp đã nghiệm thu hoặc phạm vi mới; các lựa chọn kỹ thuật thông thường Claude đề xuất rõ và tự kiểm trước bàn giao.

AC sống đọc trực tiếp qua linear_zero_door ngày 19/10/2026 khoảng 12:40 +07, URL đúng workspace zero-door:
- ZER-37 AC-01: ID, timestamp, trạng thái; schema/version và ví dụ; nguồn riêng cho effect/detect/action/recovery/stop; action terminal không đồng nhất RECOVERY_VERIFIED.
- Cha ZER-9 AC-01 tương ứng; AC-02 truyền/lưu raw và AC-03 chống rò còn phải thực thi trong gói tiếp. Thiết kế hiện tại phải đủ phục vụ chúng nhưng không nhận đã đạt runtime.
- ZER-32 và ZER-8 read-back Done; thiết kế đã nghiệm thu là nguồn ngữ nghĩa. Không mở lại lựa chọn B3/M1/B2 hay D-01…D-05.

### Baseline và phạm vi chính xác

Baseline Codex: branch zer-36-g0-receipt, HEAD 42af1c1afd90a51e80f2d01e690169162e79444b. Có sẵn modified: AGENTS.md; docs/delivery/NOW.md; docs/delivery/README.md; docs/delivery/WORKFLOW.md; docs/delivery/milestones/R1-measurement/README.md. Có sẵn untracked docs/delivery/WORKING-AGREEMENT.md. docs/design/ chưa tồn tại. Claude phải chụp HEAD/status và hash lại khi nhận; nếu nguồn đổi, đối chiếu delta trước khi dựa vào baseline, không reset/stash/ghi đè dirty work.

Chỉ ghi:
1. docs/design/r1-event-contract.md — artifact thiết kế chính, mới; cho phép tạo thư mục docs/design/.
2. Ghi chú event-contract.md hiện tại — chỉ nối bàn giao ở cuối, giữ nguyên gói và phần cũ.
3. docs/delivery/NOW.md — thêm một con trỏ ngắn ở đầu, giữ toàn bộ nội dung cũ.
4. Nếu cần kiểm máy cho ví dụ: scratch/zer37/check_contract.py, scratch/zer37/fixtures.json, scratch/zer37/check-results.txt. Chỉ dùng standard library và dữ liệu giả định; không ghi đè codex-package-baseline.json hoặc script review của Codex. Helper là kiểm thiết kế offline, không là validator runtime hay phép thử tự chứng minh semantics.

Không sửa source/test sản phẩm, schema runtime dùng chung, manifest, CI, dependency, evidence đã nghiệm thu hoặc tài liệu ngoài allowlist. Không chạy Docker/Kubernetes/Kafka/HTTP/model/API, attack/heal/reset, cài gói hoặc đổi Doppler. Không commit/push/PR/merge, đổi Linear hay tự gửi tin. Chưa cần tạo nhánh trong bước tài liệu này; publication sau dùng tên zer-37-event-contract, không codex prefix. Đây là scope đã cụ thể hóa từ yêu cầu bắt đầu, không phải quyền vận hành gói tiếp.

### Nguồn cần đọc

Bắt đầu Delivery README, WORKING-AGREEMENT, NOW và gói này; SCOPE/WORKFLOW theo quy tắc repo. Dùng AC sống ZER-37 cùng cha ZER-9 nếu có connection; nếu không, dùng snapshot trên và ghi giới hạn, không chặn việc đọc nguồn/soạn draft.

- docs/evidence/ZER-32/requirements-and-kpi.md: mục 3–4, mục 6–7 và case liên quan ở mục 5. SHA-256 a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c.
- docs/evidence/ZER-8/research-design.md: mục 4–5, các sửa mục 11 và quyết định mục 12–13. SHA-256 cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8.
- docs/delivery/milestones/R1-measurement/README.md và ghi chú probes-and-metrics.md, dashboard-and-baselines.md, guards-and-ci.md: chỉ phần consumer trực tiếp.
- Chỉ khảo sát source cần để lập bảng hiện trạng → contract đề xuất. Theo AGENTS, bắt đầu GitNexus context/freshness rồi query/context nếu khám phá mã; kiểm lại source thật ở revision hiện tại. Không chạy index/CLI công việc ngoài scope chỉ để có graph; nếu công cụ không dùng được, ghi rõ và đọc source có mục tiêu. Không suy hành vi runtime từ index.

### Nội dung bắt buộc của artifact

1. Ghi rõ DRAFT_FOR_REVIEW, revision nền, nguồn đã nghiệm thu, phiên bản contract và quy tắc tương thích/đổi version. Bảng hiện trạng producer/consumer trực tiếp, chỗ mapping/migration còn thiếu; không biến thiết kế thành tuyên bố đã triển khai.
2. Envelope và payload đặc tả ngay trong Markdown (bảng trường/kiểu, JSON minh họa, ràng buộc): event_id, run_id, trial_id, incident_id trung tính, action_id khi có action, correlation/causation nếu cần, schema_version, method/config version, source_component, target/stream, clock identity/source, ts_event và ts_ingest. Định nghĩa cardinality, trường required/nullable/absent theo loại event, nguồn có quyền phát và cách ghép khi mất ID; thiếu dữ liệu không tự sinh ID/mốc để cứu KPI. Model multiple actions/retry, phân biệt redelivery cùng event_id với lần thử thật có ID riêng; lưu thứ tự nguồn và xử lý out-of-order/duplicate/conflict/orphan ở thiết kế. Không bắt toàn pipeline có thứ tự tổng khi clock/Kafka không bảo đảm.
3. Timestamp UTC ms; tách thời gian sự kiện, ingest và các mốc tính KPI. Clock offset/resolution/uncertainty phải biểu diễn được; timestamp có ms không chứng minh đồng hồ chính xác ms. Giữ quy tắc INVALID_CLOCK/EARLY_DETECT theo nguồn. Clock tolerance và tham số minh họa không tự khóa formal F-01…F-09; cách đo offset thực thuộc ZER-38.
4. Event và state machine tách các miền: điều khiển requested/stopped; effect evaluation CONFIRMED/CONFIRMED_NO_EFFECT/UNKNOWN_EFFECT; detector detected; decision/guard; heal_started, API_ACCEPTED, ACTION_COMPLETED kèm SUCCESS/FAILED/PARTIAL/TIMEOUT; probe recovery/relapse và kết quả chấm sau run. Ghi ai phát mỗi mốc. FAILED/PARTIAL/timeout/missing không tạo recovery từ action; probe độc lập vẫn có thể ghi nhận phục hồi vì nguyên nhân khác và phải giữ provenance, không tự nhận causal attribution cho healer.
5. Recovery theo ZER-32: T_rec là mẫu đạt thứ K, đủ ổn định S rồi mới xác minh; lưu riêng recovery_verified_at, ts_event và ts_ingest với ý nghĩa rõ. Tham chiếu probe samples/coverage và version Δ,K,S,L,gap,cap; relapse hủy ứng viên; cap giới hạn T_rec chứ không cắt S. Stop trước hết S ra AFTER_STOP; thiếu probe không là TIMEOUT/PASS. SQLi containment và Boutique availability tách luồng. Effect UNKNOWN ở lại N; NO_EFFECT phải có coverage đầy đủ W_eff; N=0 không PASS. Không tự đặt ngưỡng/formal protocol mới.
6. H/O/S theo ZER-8: harness/effect/probe/ground truth ở H; telemetry tự nhiên/alert/decision/guard/action ở O; ghép chấm sau trial ở S. ID trung tính không mã hóa vector/class/thứ tự; không rò label, command, expected action, canary, seed/onset hoặc probe scoring qua payload/topic/path/query tới healer/BM. Chốt visibility theo trường/event, không chỉ gắn nhãn plane rồi để payload tùy ý. Audit/ràng buộc O là đề xuất, chưa chứng minh access control runtime. Hoàng chỉ rà variant trước sinh/niêm phong lịch, không xem lịch trial trước/trong BM; thiếu audit là UNKNOWN. Đừng che telemetry/IP/release history tự nhiên hợp lệ.
7. Dữ liệu đủ phục vụ ZER-9 AC-02/03 và ZER-10/11/12: raw export/replay giữ event gốc và version, decision trước guard, retry/usage/cost có trạng thái missing/N/A, B0/MANUAL không ngầm sinh heal. Ghi thiết kế durability/access phù hợp scope, không triển khai storage hay adapter. Chỉ định consumer/mapping và phần việc tiếp theo; child Done không đóng cha.

### Kiểm chứng vừa đủ trước bàn giao

Lập AC → điều khoản/field → ví dụ → expected/actual. Ví dụ phải thể hiện event liên kết được và vai trò/visibility; dữ liệu synthetic ghi rõ. Dùng bảng trace hoặc JSON đủ để Codex tái tính độc lập, không chỉ câu tuyên bố PASS. Tập trung các phản ví dụ:
- Recovery hợp lệ, có mốc T_rec, hết S, ingest muộn; so sánh KPI dùng đúng mốc.
- API accepted/action SUCCESS nhưng probe lỗi; FAILED/PARTIAL/timeout hoặc không action nhưng dịch vụ tự phục hồi (không gán công healer).
- Relapse trong S; mất probe trong S; T_rec đúng cap và sau cap; stop giữa T_rec và hết S.
- UNKNOWN_EFFECT, NO_EFFECT đủ/thiếu coverage; EMPTY/NO_ELIGIBLE. Không triển khai lại cả bộ KPI ZER-32.
- Kafka redelivery, retry thực, out-of-order, event_id trùng payload mâu thuẫn, thiếu ID/source trái quyền, clock không đủ tin cậy.
- Một trace sạch H/O/S và trace lỗi có nhãn/canary/seed-onset rò O; group B0/MANUAL không phát action ZERO DOOR. Đây là case contract offline, chưa là leak/mode runtime test.

Tự review toàn artifact và ví dụ, sửa gom các lỗi cùng nguyên nhân. Nếu dùng helper, kiểm có đối chứng sạch và sửa cố ý một điều kiện quan trọng để chắc bộ kiểm có thể bắt lỗi; không tối ưu số lượng assertion/mutant. Kiểm link nội bộ, bảng Markdown, git diff --check, diff ngoài allowlist và hash nguồn bảo vệ. Không thêm framework hay bộ kiểm chỉ tìm từ khóa để tự nhận AC đạt.

### Bàn giao một lần

Nối cuối ghi chú này: HEAD/dirty lúc nhận và lúc trả; file đã ghi/hash; AC → case → kết quả; command kiểm; phần thiếu/UNKNOWN; lựa chọn cần Hoàng quyết thật sự. NOW chỉ trỏ artifact và Codex review. Trả quyền writer cho Codex sau tự kiểm; không chỉnh tiếp trong lúc Codex review. Kết quả là contract chờ review/nghiệm thu, không tự khóa schema hoặc Done ZER-37/ZER-9/G1. Codex kiểm độc lập với nguồn accepted, trace thời gian và các consumer trực tiếp; gom findings rồi retest delta. Không hứa chắc chỉ một vòng review.

## Bàn giao Claude — ZER-37 contract sự kiện — 19/10/2026, 13:05 +07:00

**Kết quả.** Bản contract [docs/design/r1-event-contract.md](R:/_Projects/Eurus_Workspace/zero_door/docs/design/r1-event-contract.md) (DRAFT_FOR_REVIEW, `zd-event/0.1.0`), SHA-256 `7409c1a141e5c9cb59fc8969889bec7fca3eb1437cc246e6bbd924d3ea94e21c`, 634 dòng. Đây là thiết kế chờ Codex review và Hoàng nghiệm thu. Nó không khóa schema, không đánh dấu Done ZER-37/ZER-9/G1 và không chứng minh runtime.

**Baseline lúc nhận (12:45 +07) và lúc trả (13:05 +07) giống nhau.**
- Nhánh `zer-36-g0-receipt`, HEAD `42af1c1afd90a51e80f2d01e690169162e79444b`, staged rỗng.
- Dirty có sẵn giữ nguyên: AGENTS.md, NOW, delivery README, WORKFLOW, README R1, ghi chú này (gói Codex), WORKING-AGREEMENT (untracked).
- Tám hash trong `scratch/zer37/codex-package-baseline.json` và SCOPE khớp lúc nhận và lúc trả.
- AC sống: Claude không có `linear_zero_door`, không dùng connector thay thế. Dùng snapshot AC của gói (Codex đọc lúc 12:40).

**File đã ghi.** Đúng allowlist:
1. `docs/design/r1-event-contract.md`: mới, tạo thư mục `docs/design/`.
2. Ghi chú này: chỉ nối mục bàn giao.
3. `docs/delivery/NOW.md`: một con trỏ ở đầu.
4. `scratch/zer37/fixtures.json` (`585fadaa…8701bf`), `scratch/zer37/check_contract.py` (`67e5c409…06bf31`), `scratch/zer37/check-results.txt`. `scratch/` bị Git bỏ qua.

Không sửa source, test, schema runtime, manifest, CI hay evidence đã nghiệm thu. Không chạy lab/API/Kafka/Docker, không commit/push hay đổi Linear. Bản sao baseline của NOW và ghi chú này nằm ngoài repo (scratchpad phiên Claude), chỉ để tự kiểm.

**Nội dung chính của contract.**
- Version và quy tắc tương thích.
- Bảng hiện trạng producer/consumer theo source tại HEAD. Có đọc qua `gitnexus query` trên index `df5d542`; source sản phẩm không đổi từ đó.
- Envelope, bản ghi ingest, ID UUIDv4 có tiền tố loại, cardinality, nguồn được phát của từng mốc.
- Thời gian: `ts_event`, trường mốc trong payload, `ts_publish`, `ts_ingest`; danh tính đồng hồ và CLOCK_SYNC.
- Khử trùng/retry, thứ tự, ghép incident, ORPHAN.
- Năm miền trạng thái; ràng buộc B0/BM; recovery theo D-04 có tái tính từ probe raw.
- Mặt H/O/S theo từng trường, phép kiểm rò, thiết kế kho raw/export, consumer ZER-9/10/11/12/38.

**Phát hiện hiện trạng đáng chú ý** (theo mã, chưa chạy):
- Hephaestus báo SUCCESS ngay khi API trả về cho SCALE_UP/ROLLBACK/BLOCK_IP. Đó là API_ACCEPTED, chưa kiểm hậu điều kiện.
- Pod stress của chaos-worker mang tên/label lộ vector trong namespace mục tiêu. Gaia còn gán CPU của pod đó cho service.
- Dashboard cộng `Math.random()` vào MTTR.
- Kafka retention 24 h nên không phải kho raw.
- Không thành phần nào mang `run_id`/`trial_id`/`incident_id`.

**AC → case → kết quả.** Helper OFFLINE dựng envelope từ fixtures, áp quy tắc mục 4–8 và so với expected tính tay trước lần chạy đầu.
- Đối chứng sạch: **129/129** expectation trên 34 case và 3 aggregate.
- Mutant: **14/14** bị bắt, mỗi mutant đổi một quy tắc. Ví dụ: KPI dùng `ts_ingest`; SUCCESS coi là recovery; FAILED/PARTIAL/TIMEOUT xóa cờ NO_ACTION_BEFORE_RECOVERY; dedup bỏ qua xung đột payload; chọn detect theo thứ tự ingest; bỏ quyền nguồn; cap cắt S; UNKNOWN_EFFECT rời N; tin record NO_EFFECT không kiểm phủ; bỏ quét ID; cho action trong B0; ORPHAN thành MISSED; bỏ quy tắc CLOCK_SYNC.

| AC ZER-37 (snapshot) | Điều khoản | Case | Kết quả |
| --- | --- | --- | --- |
| ID, timestamp, trạng thái | 3, 4, 5, 7 | E01, E13–E16, E19–E20, W1–W2 | Khớp |
| Schema/version và ví dụ | 1, 5.4, 10 | 2 khối JSON trong artifact được kiểm schema; E01 | Khớp |
| Nguồn riêng effect/detect/action/recovery/stop | 5.2 | E17 (2 SOURCE_VIOLATION), E10–E12 | Khớp |
| Action terminal ≠ RECOVERY_VERIFIED | 5.3, 7.3, 7.5 | E02, E03F/P/T/N/M, E05–E09 | Khớp |
| Phục vụ ZER-9 AC-02/03 (chưa runtime) | 6, 8, 9 | L1–L5, B0V/B0C, BMV/BMC | Khớp ở mức contract offline |

Kiểm gói 24/24 (lần chạy cuối ghi trong `scratch/zer37/check-results.txt`):
- link nội bộ, bảng Markdown, CR/trailing space, khối JSON hợp lệ;
- 9 hash nguồn bảo vệ;
- ghi chú chỉ nối thêm, NOW giữ thân cũ;
- `git status` đúng baseline cộng artifact, HEAD không đổi, staged rỗng;
- `git diff --check`, không có chuỗi dạng khóa.

Lệnh (Git Bash, gốc repo):

```bash
python -I -B scratch/zer37/check_contract.py
```

**Giới hạn.**
- Helper chỉ kiểm thiết kế, không phải validator runtime hay scorer ZER-10. Nó không tái hiện uptime/CPU/aggregate đầy đủ của ZER-32, không kiểm SQLi containment bằng số và chưa mô phỏng telemetry Kubernetes, nên quy tắc 8.3 mục 4 chờ ZER-9 AC-03.
- Expected và helper cùng do Claude viết. Mutant chỉ chứng minh bộ kiểm nhạy với các quy tắc đã chọn, không chứng minh semantics đúng. Codex cần tái tính độc lập E01 và vài phản ví dụ từ bảng 10.2.
- AC sống UNKNOWN với Claude.

**Cần Codex review.** Năm điểm PROP ở mục 11 của artifact: `incident_id` ở O; CLOCK_UNVERIFIED; T_rec dùng `t_start`; quy tắc cửa sổ ghép và ORPHAN trong cửa sổ; định dạng ID.

**Cần Hoàng quyết sau review.** Hai điểm chạm phương pháp đã nghiệm thu:
1. Thu hẹp “`incident_id` ở H và O” của ZER-8 mục 5.6: O chỉ mang ID cấp trước onset ở trial một incident, kể cả slot C0; War Game ghép ở S.
2. Coi duration xuyên đồng hồ là MISSING khi đồng hồ OFF_HOST thiếu CLOCK_SYNC. Đây là cách áp dụng bảo thủ ZER-32 mục 3.1, thay vì chỉ gắn cờ.

Không mở lại B3/M1/B2 hay D-01…D-05.

**OPEN, giao issue sở hữu:** cách đo offset (ZER-38/F-01); `ingest_grace` (ZER-10/53); alert lệch service (ZER-10/53); tiêu chí effect W_eff (F-05, ZER-13/14); trường probe từng bước (ZER-38); enum action (ZER-50).

**Bước tiếp theo.** Claude trả quyền writer cho Codex và không chỉnh tiếp trong lúc review. Codex review độc lập với nguồn đã nghiệm thu, trace thời gian và consumer trực tiếp, gom findings rồi retest delta. Sau nghiệm thu, publication dùng nhánh `zer-37-event-contract` khi Hoàng cấp quyền.


## Codex review ZER-37 — 19/10/2026, 13:34 +07:00

**Verdict: NOT READY để khóa schema/nghiệm thu ZER-37.** Đã review toàn bộ 634 dòng contract, helper/fixtures và consumer trực tiếp. Đây là review thiết kế/offline; không là runtime. Có năm nhóm P2 cần sửa gom bên dưới. Không đổi phương pháp đã nghiệm thu hoặc trạng thái Linear. Bản Claude được giữ nguyên để đối chiếu; writer chuyển Claude khi Hoàng chuyển gói sửa, sau đó trả Codex retest.

### Provenance và phần đạt

- Target: artifact mới/untracked docs/design/r1-event-contract.md tại HEAD 42af1c1afd90a51e80f2d01e690169162e79444b, SHA-256 7409c1a141e5c9cb59fc8969889bec7fca3eb1437cc246e6bbd924d3ea94e21c. Helper 67e5c409048729255dc7f7cd852c5d27a4733a19a08335236d006a2e9f06bf31; fixtures 585fadaac79ab7f2ae208f4d4849eac27875c0c1b3551dbfc8b12e5c658701bf. Không review lại các dirty quy ước ngoài gói như thay đổi của Claude.
- AC sống ZER-37 và cha ZER-9 đã đọc lại trực tiếp qua linear_zero_door, đúng URL linear.app/zero-door/. Khớp snapshot gói; ZER-37 vẫn Backlog, cha Todo. Review không sửa AC/state/relations.
- Nguồn accepted ZER-32/ZER-8 được đối chiếu; chín hash nguồn bảo vệ vẫn khớp. Ghi nhận đúng sự tách action khỏi recovery, giữ UNKNOWN_EFFECT trong N, NO_EFFECT cần coverage, H/O/S, raw replay, version và child không đóng cha.
- Source claims về Gaia, Hephaestus, Nemesis, worker, runner, dashboard và Kafka có căn cứ tĩnh. Hephaestus action_scale_up tại main.py:197–205 chỉ xác nhận API; process_alert:415–482 quyết định/thực thi và lưu memory; app.js:669–675 cộng random MTTR; cpu_stress.go:51,66–68 lộ dấu hiệu vector; Kafka values:69–93 retention. Chưa thử runtime, không biến các thiếu sót sẵn có thành regression của contract.
- GitNexus query/context(process_alert) và detect_changes đã dùng để điều hướng. Index df5d542 chậm 6 commit; so hash 10 file producer/consumer/source trực tiếp đều khớp byte hiện tại. detect_changes không bao phủ artifact untracked/helper ignored. Lượt analyze --index-only không hoàn tất, đã dừng tiến trình do lượt review mở; không coi index được refresh. Không có production symbol đổi, nên không chạy impact/PDG/taint sản phẩm; review hợp đồng và helper bằng đọc trực tiếp + phản ví dụ, không nhận graph review toàn diện.
- Chạy lại helper gốc: 129/129 expectation, 14/14 mutant, kiểm gói 24/24 đúng như bàn giao. Sau khi thêm con trỏ review, kiểm NOW lịch sử của helper có hash baseline cứng sẽ cần cập nhật có căn cứ; không đổi golden chỉ để che lỗi.
- Tính độc lập E01: 131−101=30; 191−131=60; 191−101=90; 150−131=19 giây. Ingest290 không vào KPI.

### Finding phải sửa gom

**RV37-01 | P2 | Recovery chưa ràng buộc đủ thời điểm có bằng chứng và tham chiếu mẫu.**
Anchor contract:458–461 và helper:488–490. T_rec lấy t_start là quy ước minh họa có thể review, nhưng mẫu chỉ biết pass/content/latency sau t_end. Chỉ yêu cầu ts_event ≥ T_rec+S cho phép phát RECOVERY_VERIFIED tại221 khi mẫu bắt buộc ở221 chỉ hoàn tất221.25. Helper vẫn chấp nhận và không báo evaluator_mismatch. Thay sample_seq_range bằng[0,0] cũng không bị phát hiện vì chỉ so t_rec. Điều này trái yêu cầu không phát xác minh trước khi đủ bằng chứng của ZER-32 mục3.4.
Sửa: tách mốc đo t_rec, ranh giới logic recovery_verified_at và thời điểm thực có đủ mọi sample hoàn tất; kiểm producer ts_event không sớm hơn thời điểm đó, không đổi MTTR sang ingest. Tham chiếu sample phải xác định probe/flow/trial/version đủ duy nhất và thực sự hỗ trợ K+S, kiểm range/hash/provenance khi có. Bổ sung ca end muộn, sample ref sai và ca sạch tương ứng. Không cần đổi D-04 hoặc tự chọn t_end làm T_rec để sửa lỗi phát sớm.

**RV37-02 | P2 | Quy tắc rò gắn nhầm mọi tài nguyên harness thành đáp án.**
Anchor contract:512 so với chính:504 và nguồn ZER-8 mục5.7. Theo câu hiện tại, một pod tên UUID trung tính do harness tạo, tag image trung tính hoặc IP nguồn quan sát tự nhiên được đăng ký manifest H rồi xuất hiện trong telemetry O đều LEAK_DETECTED. Ví dụ đổi tên pod stress sang tên trung tính theo mục2 vẫn không bao giờ sạch. Nguồn accepted chỉ cấm canary/nhãn/đáp án/lịch hoặc dấu hiệu mang thông tin case, giữ telemetry tự nhiên.
Sửa: manifest phân biệt giá trị bí mật/có nghĩa đáp án với định danh trung tính và trường quan sát hợp lệ; quy tắc so khớp theo field/source có version. Không cho phép mọi giá trị H, nhưng cũng không cấm chỉ vì harness là người tạo. Thêm hai đối chứng offline: tài nguyên trung tính + telemetry hợp lệ phải CLEAN (khi coverage đủ); tên/label chứa nhãn case hoặc canary ra O phải LEAK_DETECTED. Chưa cần runtime Kubernetes để kiểm đúng quy tắc thiết kế này.

**RV37-03 | P2 | Helper chưa kiểm được quy tắc đồng hồ mà artifact dùng làm bằng chứng.**
Anchor contract:131–141; helper:426–432,453–475. Dịch tất cả timestamp OFF_HOST của E01 thêm10s và ghi CLOCK_SYNC offset_ms=10000 thì dữ liệu vật lý không đổi; expected sau hiệu chỉnh vẫn MTTD30/MTTR60. Helper cho20/70, không cờ. Hai sync tại10 và101 vẫn được chấp nhận cho trial kết thúc300 vì chỉ bracket T_req100. Tất cả fixtures gốc dùng offset0 nên mutant hiện tại không phát hiện.
Sửa: đặc tả rõ clock owner của các timestamp payload/received_at và normalization sang reference trước ghép/so/thực hiện KPI. Chọn rõ cách dùng hai phép đo/độ trôi cho ví dụ hoặc trả UNKNOWN khi không đủ; phương pháp đo thật vẫn ZER-38, không khóa F-01 formal. Kiểm coverage đầu và cuối trial và uncertainty/resolution. Thiếu sync chỉ làm missing các khoảng phụ thuộc clock đó; không tự xóa duration hợp lệ cùng đồng hồ. Thêm offset khác0, thiếu sync cuối và ca cùng clock. Không cần gọi API/lab.

**RV37-04 | P2 | Kiểm schema/semantics bỏ lọt bằng chứng SUCCESS, probe pass và mode BM mâu thuẫn.**
Anchor contract:223–251,450; helper:248–267,426–427,482–487,541–550. Ba phản ví dụ đều lọt: (a) ACTION_COMPLETED=SUCCESS nhưng postcondition.satisfied=false vẫn reaction19; (b) pass=true nhưng latency5s>L2s, error_class=SLOW vẫn RECOVERED; (c) xóa DECISION MANUAL trong trace BMC, giữ initiator=OPERATOR trên action, mode_violation vẫn false. Những case này trực tiếp vi phạm các bất biến artifact tuyên bố được kiểm. Helper có thể đơn giản, nhưng không dùng kiểm envelope sơ bộ để nhận ví dụ hợp lệ đầy đủ.
Sửa: kiểm các ràng buộc liên trường thiết yếu này, malformed/missing payload và nguồn/ID bắt buộc của event trong ví dụ; lỗi phân biệt invalid/missing/violation, không im lặng PASS hoặc crash. Bảng5.3 cần chốt payload cho các loại còn thiếu như RUN_CLOSED/RUN_CONTEXT/TRIAL_CONTEXT/TRIAL_ENDED/PROBE_HEARTBEAT (có thể ghi object rỗng hợp lệ, đừng để consumer tự đoán); CLOCK_SYNC đã mô tả ở4.3 thì dẫn rõ. Không mở rộng thành framework schema runtime hay viết lại toàn bộ scorer. Thêm ca B1/B2/B3 nhất quán group/source nếu sửa chung mode checker, giữ ownership downstream.

**RV37-05 | P2 | Ghép ID tường minh thiếu bất biến ngữ cảnh và chuỗi action_id bị đứt trong helper.**
Anchor contract:85,99,213–214,395–402; helper:375–410. (a) Đổi run_id của DETECTED sang run khác nhưng giữ incident_id: helper vẫn MTTD30, không LINK_CONFLICT. (b) War Game có HEAL_STARTED hợp lệ, API_ACCEPTED/ACTION_COMPLETED chỉ mang action_id như bảng5.2 cho phép: helper không đi qua map action_id đã biết, ghi2 ORPHAN và incident MISSING thay vì reaction19. Nếu ID tường minh luôn được tin thì bước kiểm S đã hứa ở3.3 không xảy ra.
Sửa: ID tường minh/chuỗi nhân quả chỉ dùng khi run/trial/incident/target ownership nhất quán; xung đột giữ raw/quarantine và báo LINK_CONFLICT, không sửa ID để cứu số liệu. Lập map action_id từ HEAL_STARTED để terminal/API ghép được dù thiếu decision_id; nếu hai đường liên kết mâu thuẫn phải phát hiện. Thêm ca sạch action_id-only và ca sai run/trial/causation, không chỉ malformed ID. Với target mismatch còn OPEN, phải ghi rõ chưa được tính thành detect bình thường khi policy chưa chốt. ORPHAN thiếu run không được gán theo thời gian, cũng không được làm nhiễm mọi run khác chỉ vì trùng cửa sổ.

### Bằng chứng tái hiện độc lập

Giữ nguyên file Claude. Codex thêm riêng scratch/zer37/codex-review-probes.py và codex-review-results.json (dữ liệu giả định, không network). Script gọi helper như một hàm thuần trên bản copy của fixtures; không sửa expected/helper gốc.

| Ca | Expected | Actual đã quan sát |
| --- | --- | --- |
| CONTROL_E01 | MTTD30, MTTR60, total90, reaction19 | Đúng |
| CLOCK_OFFSET_10S | MTTD30, MTTR60 sau hiệu chỉnh | 20,70, không cờ |
| SYNC_END_MISSING | CLOCK_UNVERIFIED | RECOVERED, không cờ |
| SUCCESS_POSTCONDITION_FALSE | SUCCESS không hợp lệ, không reaction19 | validate không lỗi, reaction19 |
| BM_MANUAL_DECISION_MISSING | MODE_VIOLATION | false |
| PROBE_SLOW_PASS | Không RECOVERED từ mẫu mâu thuẫn | RECOVERED |
| ACTION_ID_ONLY_VALID_TERMINAL | Không orphan, reaction19 incident đầu | 2orphan, MISSING |
| PUBLISH_BEFORE_LAST_PROBE_FINISHED | Bắt phát sớm221 trước mẫu kết thúc221.25 | validate không lỗi, mismatch=false |
| EXPLICIT_CONTEXT_CONFLICT | LINK_CONFLICT/quarantine | MTTD30, không cờ |
| INVALID_RECOVERY_EVIDENCE_RANGE | evaluator mismatch | false |

Kết quả: một đối chứng sạch đạt, chín phản ví dụ xác nhận khoảng trống hiện tại. Đây không phải9 runtime defect, không phải toàn bộ validation suite của tương lai. Ca rò tài nguyên trung tính là phản ví dụ trực tiếp của quy tắc văn bản; helper hiện chưa thực hiện quy tắc đó.

Lệnh từ Git Bash ở root: python -I -B scratch/zer37/codex-review-probes.py. Script in actual/expected và ghi JSON; mã exit0 chỉ cho biết script review đã chạy xong, không phải contract PASS. Khi retest phải đọc expectation_met, không dựa exit0.

### Ý kiến về năm PROP và quyết định Hoàng

1. ID trung tính cấp trước onset là hướng hợp lý. Tuy nhiên C0 có0 incident thật và incident hiện bắt buộc1 ATTACK_REQUESTED (mục3.2) nên cần phân biệt ID slot dự phòng với incident requested; không để C0 tăng N. War Game không mang incident_id trong O và ghép S là điều chỉnh cụ thể của ZER-8, giữ PROP để Hoàng chấp nhận cùng bản sửa. Không có phê duyệt mới ở lượt review này.
2. OFF_HOST thiếu bằng chứng clock thì duration phụ thuộc clock là MISSING: tôi khuyến nghị, phù hợp yêu cầu ghi offset của ZER-32. Sửa RV37-03 trước; không nhận đây là cách đo offset đã được kiểm thật.
3. t_start có thể là thời điểm đại diện của mẫu để tương thích cách tính uptime; cần ghi giới hạn lấy mẫu và sửa RV37-01. Chưa nâng PROP thành ACC hoặc đổi D-04 ở nguồn.
4. Window linking/ORPHAN có thể dùng bảo thủ khi không biết; cần sửa RV37-05, không nhận target mismatch thành detect đúng khi policy đang mở.
5. UUIDv4 có tiền tố loại là lựa chọn kỹ thuật hợp lý, không cần đổi phạm vi nghiên cứu. ID format tự nó không chứng minh generator ngẫu nhiên; helper tạo UUID từ hash case là dữ liệu test tái lập, phải ghi rõ SYNTHETIC, không dùng generator đó cho runtime.

Hai lựa chọn phương pháp của Hoàng được gom nghiệm thu sau bản sửa và retest; không hỏi Hoàng chọn phương pháp để vá các lỗi logic nêu trên. Giữ DRAFT_FOR_REVIEW, không tăng1.0.0/Done lúc này.

### Gói sửa gom cho Claude và điều kiện bàn giao lại

Dùng lại allowlist gốc: artifact contract; helper/fixtures/check-results của Claude trong scratch/zer37; chỉ nối ghi chú issue; thêm con trỏ NOW. Được sửa RV37-01…05 và lỗi cùng nguyên nhân, tự kiểm xuyên suốt trong gói docs/offline. Không sửa source/CI/runtime, nguồn accepted hoặc script/results review của Codex. Nếu đổi API helper, duy trì wrapper cho build/analyse/validate hoặc ghi adapter rõ để retest không mất nghĩa; không đổi dữ liệu/script Codex để làm xanh kết quả. Không cần tăng số assertion; cần ca lỗi bị bắt và ca sạch tương ứng còn qua.

Bàn giao một lần: từng RV → sửa → case → expected/actual; hash mới và baseline; bảo toàn kết quả gốc129 kỳ vọng về mặt ngữ nghĩa, mọi thay đổi expected phải giải thích từ nguồn (không giữ số đếm bằng mọi giá); chạy lại mutants phù hợp và các ca Codex, thêm cặp neutral/leaking resource offline. Giữ bản gốc helper/fixtures nếu cần trong scratch/zer37/v1/; không sửa log/handoff cũ. Hash nguồn accepted/dirty ngoài scope phải giữ nguyên.

Codex retest delta + chín phản ví dụ và ca rò sạch/lỗi; sau đó mới trình Hoàng chấp nhận contract/PROP và tính publication riêng. ZER-9 AC-02/03 và G1 chưa được mở/đóng bởi gói này. Chưa commit/push hoặc đổi Linear.

## Bàn giao Claude — sửa gom ZER-37 theo Codex review — 19/10/2026, 14:10 +07:00

**Kết quả: đã sửa RV37-01…05 và các lỗi cùng nguyên nhân ở mức thiết kế/offline; trả writer cho Codex retest.** Contract giữ DRAFT_FOR_REVIEW, nâng `zd-event/0.1.0` → `0.2.0` vì thêm trường bắt buộc (chưa producer nào phát bản cũ). Không chạy lab/API/Docker/Kafka, không sửa source/test/CI/runtime, không commit/push, không đổi Linear. Không mở lại D-01…D-05, B3/M1/B2; không khóa F-01…F-09.

**Baseline lúc nhận gói.** HEAD `42af1c1afd90a51e80f2d01e690169162e79444b`, nhánh `zer-36-g0-receipt`, staged rỗng. Ghi chú này trước bàn giao: 34696 byte, SHA-256 `d4c0cae9…c177c1`. NOW trước con trỏ mới: `2d8bf435…12edb7`. Dirty ngoài phạm vi giữ nguyên; `git status` đúng tập baseline cộng contract.

### Tệp và hash

| Tệp | SHA-256 | Ghi chú |
| --- | --- | --- |
| [docs/design/r1-event-contract.md](../../../design/r1-event-contract.md) | `5c30a324b552713cafa42482277b3a2c4fc6d168791c7ef123e8d6975c3b04da` | 766 dòng; bản review đầu `7409c1a1…94e21c` |
| `scratch/zer37/check_contract.py` | `c2e0bf6cc8e2d3b97551b949ff7726b073936c50495ee99b357a2623f4df75c5` | Helper bản 2; giữ chữ ký `build`/`validate`/`analyse` cho script Codex |
| `scratch/zer37/fixtures.json` | `c9144d7500f11a468f8d9b2f30bb3ee6ab9e1b47364890932ef5a8c78e2382a2` | 62 case + 3 aggregate |
| `scratch/zer37/check-results.txt` | `cd82f663dddeac35bd7252e373095653904ff9422444cec8c3a14f245f8ba2e4` | Đầu ra lần chạy cuối |
| `scratch/zer37/v1/` | `67e5c409…06bf31`, `585fadaa…8701bf`, `b7074721…efaa19e6` | Bản helper/fixtures/kết quả lượt đầu, giữ nguyên byte; chỉ để đối chiếu (helper v1 đọc fixtures ở đường dẫn gốc) |
| Script/kết quả Codex | `65d7504d…`, `958c2083…`, `3d75023f…`, baseline `783d444c…` | Không sửa; helper kiểm hash |

### Từng finding

| RV | Sửa contract | Sửa helper | Ca lỗi → kết quả | Ca sạch | Probe Codex |
| --- | --- | --- | --- | --- | --- |
| RV37-01 | Mục 7.5 bước 5–6: tách `t_rec`, `recovery_verified_at`, `evidence_complete_at`; `ts_event` ≥ `evidence_complete_at`; tham chiếu mẫu bằng `probe_id`, `probe_version`, `flow`, trial, `sample_seq_range`, `samples_sha256`; khóa mẫu. Bảng 5.3, ví dụ 5.4 | Kiểm phát sớm và số học ở `validate`; scorer so mọi trường, hash, nguồn gốc mẫu; khóa mẫu trùng là INTEGRITY_ERROR | R1 phát lúc 221 → INVALID + EVALUATOR_MISMATCH; R2 range sai, R3 probe sai, R4 hash sai → mismatch đúng trường; R5 mẫu trùng khóa → MISSING | E01: range [189, 221], không mismatch | PUBLISH_BEFORE_LAST_PROBE_FINISHED, INVALID_RECOVERY_EVIDENCE_RANGE: đạt |
| RV37-02 | Mục 8.3 mục 3, 4, 6: HARNESS_MANIFEST với lớp NEUTRAL/SECRET/OBSERVABLE, `o_visible`, `allowed_o`, `allowlist_version`; thiếu manifest là UNKNOWN | Quét bề mặt O và prompt theo manifest; so khớp đã chuẩn hóa dấu nối | L7 pod `frontend-cpu-stress-5d2c` → LEAK; L8 IP do harness ghi vào TRIAL_CONTEXT → LEAK; L9 thiếu manifest → UNKNOWN | L6 pod trung tính + IP ở trường được phép → CLEAN | Ca rò tài nguyên trung tính của review nay CLEAN (L6) |
| RV37-03 | Mục 4.2 đồng hồ sở hữu từng timestamp; mục 4.3 đồng hồ tham chiếu, phủ đầu và cuối trial, nội suy offset, sai số, CLOCK_UNVERIFIED chỉ làm MISSING phần xuyên đồng hồ | Chuẩn hóa trước ghép/so/KPI; D-04 chạy trên số đọc của probe; báo `u_ms` | C2 sync 10/101 → CLOCK_UNVERIFIED, MTTD/MTTR MISSING, total 90, reaction 19; C5 thiếu `uncertainty_ms`, C6 thiếu `resolution_ms` → CLOCK_UNVERIFIED | C1 lệch +10 s → 30/60/90; C3 trôi 10 ms/s → 30/60/90; E01 `u_ms` 37/37/32/2 | CLOCK_OFFSET_10S, SYNC_END_MISSING: đạt |
| RV37-04 | Bảng 5.3 thêm RUN_CLOSED, RUN_CONTEXT, TRIAL_ENDED, TRIAL_CONTEXT, HARNESS_MANIFEST, CLOCK_SYNC, PROBE_HEARTBEAT; ràng buộc liên trường; phân loại lỗi; mục 6.4; bảng nhóm 7.4 | Kiểm trường/kiểu/enum/ID theo loại, ràng buộc liên trường, lỗi MISSING_FIELD/INVALID/SEMANTIC; payload sai dạng không làm dừng; nhóm kiểm nguồn, LLM_CALL, initiator, action → quyết định | V1 SUCCESS + `satisfied=false` → INVALID, MISSING, reaction MISSING; V2 mẫu đạt chậm → MISSING; V3 payload null → MISSING; BMD, B1V, B3V → MODE_VIOLATION | E01, BMC, B1C, B3C | SUCCESS_POSTCONDITION_FALSE, PROBE_SLOW_PASS, BM_MANUAL_DECISION_MISSING: đạt |
| RV37-05 | Mục 3.3, 6.3: phạm vi run (UNSCOPED, run khác), đường ghép qua bản đồ `action_id` và `causation_id`, bất biến ngữ cảnh, TARGET_MISMATCH không tính detect | Ghép theo thứ tự nhân quả, phát hiện đường mâu thuẫn, cách ly event | X1 run khác, X2 trial khác → LINK_CONFLICT; X3 service lệch → MISSING, cờ TARGET_MISMATCH; W4 `causation_id` trỏ incident khác → cả hai MISSING | U1 DETECTED thiếu `run_id` không ghép theo thời gian; W3 chỉ `action_id` → reaction 19, không ORPHAN | EXPLICIT_CONTEXT_CONFLICT, ACTION_ID_ONLY_VALID_TERMINAL: đạt |

**Lỗi cùng nguyên nhân đã sửa thêm:** timestamp trong payload chưa được kiểm định dạng; `evidence` của EFFECT_EVALUATED chưa kiểm; ID sai định dạng chỉ là phát hiện rò mà không làm event INVALID; `decision_source` không đối chiếu `source_component`; `attempt_no`/`retry_of`/`retry_reason` không đối chiếu; đồng hồ thiếu `resolution_ms` vẫn được tin; mẫu cùng khóa bị ghi đè lặng lẽ; slot C0 có thể bị đếm là incident (mục 3.2–3.3, theo ý kiến PROP 1 của Codex); helper sinh ID từ hash nay ghi rõ là SYNTHETIC (PROP 5). SOURCE_VIOLATION được xét trước lỗi payload, nên E17 giữ nguyên.

**Expected cũ.** 129 kỳ vọng của bản đầu giữ nguyên giá trị; không aggregate nào đổi. Thêm 9 kỳ vọng vào case cũ, đều có lý do:
- E01: `u_ms`, `rejected_types` rỗng, `unscoped` 0, `foreign` 0.
- E18: MTTD/MTTR MISSING, total 90, reaction 19, theo quy tắc CLOCK_UNVERIFIED hẹp của RV37-03.
- L1: 13 loại event mang `inc_c4_resource-0003` bị INVALID, vì ID sai định dạng nay là lỗi schema.

28 case mới mang 100 kỳ vọng. Tổng 238.

### Lệnh và kết quả

Từ Git Bash ở root:

```bash
python -I -B scratch/zer37/check_contract.py
```

- CONTROL 238/238 kỳ vọng khớp.
- Mutant 32/32 bị bắt: 14 mutant cũ và 18 mutant mới. Mutant mới gồm cả quy tắc cũ mà review chỉ ra là sai: chỉ kiểm sync quanh T_req, tin ID tường minh, coi mọi giá trị harness là rò.
- Kiểm gói 33/33:
  - hash 9 nguồn bảo vệ, 4 tệp Codex và 3 tệp v1;
  - ghi chú chỉ nối thêm sau byte 13657 và 34696;
  - NOW giữ nguyên thân sau review;
  - `git status`, HEAD, staged, `diff --check`;
  - ví dụ JSON hợp lệ, không có chuỗi giống khóa.

**Phản ví dụ Codex.** Đã chạy một bản sao ở scratchpad phiên. Bản sao chỉ đổi đường dẫn ghi kết quả (diff 1 dòng), để không ghi đè `codex-review-results.json`. Kết quả 10/10 `expectation_met`: đối chứng E01 vẫn 30/60/90/19, chín phản ví dụ nay bị bắt. Hai điểm cần đọc đúng:
- CLOCK_OFFSET_10S có `evaluator_mismatch = true`. Script viết cho bản đầu nên không dịch trường mới `evidence_complete_at`, khiến RECOVERY_VERIFIED tự mâu thuẫn và bị báo đúng. Case C1 dịch đủ trường thì không mismatch.
- PROBE_SLOW_PASS có `evaluator_mismatch = true` vì RECOVERY_VERIFIED trỏ tới mẫu INVALID.

Codex retest bằng script gốc (`python -I -B scratch/zer37/codex-review-probes.py`); script đó ghi lại tệp kết quả của Codex.

### Giới hạn và phần còn thiếu

- Expected và helper vẫn do cùng Claude viết. Nên tính lại độc lập C1, C3 (offset, trôi), R1, W3, L6 và V1.
- Nội suy tuyến tính chỉ là quy tắc của ví dụ; ngưỡng sai số chấp nhận chưa đặt (F-01, ZER-38).
- TARGET_MISMATCH tạm đứng ngoài detect; quy tắc OPEN ở ZER-10/ZER-53.
- Chưa kiểm HEAL_STARTED phải sau GUARD_VERDICT ACCEPT (ZER-12/ZER-40); chưa mô hình nhiều probe cùng luồng (ZER-38).
- Không có phép thử runtime: truyền ID, recorder, ACL/RBAC, manifest thật và kiểm rò trên Kubernetes vẫn thuộc ZER-9 AC-02/AC-03.
- AC sống: Codex đã đọc lại lúc review; Claude vẫn không có `linear_zero_door`, nên với Claude AC sống là UNKNOWN.

### Điểm review và quyết định

- PROP mới cho Codex review: 6 (manifest giá trị harness) và 7 (event INVALID làm incident MISSING), mục 11 của contract.
- Hai lựa chọn của Hoàng giữ nguyên và chờ retest:
  1. `incident_id` ở O; nay đã phân biệt slot C0 với incident.
  2. CLOCK_UNVERIFIED; nay chỉ làm MISSING phần xuyên đồng hồ.

  Không ghi đây là quyết định đã duyệt.

**Tiếp theo:** Codex retest phần delta, chín phản ví dụ và cặp rò sạch/lỗi; sau đó trình Hoàng chấp nhận contract và PROP. Publication trên nhánh `zer-37-event-contract` làm riêng. ZER-9 AC-02/AC-03 và G1 không mở hay đóng ở gói này. **Writer trả Codex.**


## Codex audit cuối ZER-37 — 19/10/2026, 14:19 +07:00

**Verdict: READY_FOR_ACCEPTANCE.** RV37-01…05 đã đạt retest; không còn finding chặn trong gói thiết kế/offline, không cần chuyển lại Claude. Contract vẫn DRAFT_FOR_REVIEW, zd-event/0.2.0, chờ Hoàng nghiệm thu.

### Phạm vi và kết quả

Live Linear Zero Door: ZER-37 In Progress (AC-01 chưa checked), cha ZER-9 Todo (AC-02/03 còn mở); AC sống khớp snapshot. HEAD42af1c1afd90a51e80f2d01e690169162e79444b, staged rỗng, dirty ngoài phạm vi giữ nguyên. GitNexus meta vẫn df5d542; không nhận index đã refresh hoặc review graph đầy đủ. Lượt này review tài liệu/helper offline; không đổi production source.

| Kiểm | Expected / Actual | Verdict |
| --- | --- | --- |
| Bộ kiểm Claude chạy lại | 238/238 kỳ vọng; 32/32 mutant bị bắt | PASS |
| Phản ví dụ Codex | 10/10 expectation_met | PASS |
| C1 offset +10 s và C3 trôi tuyến tính | MTTD30, MTTR60, total90, không evaluator mismatch | PASS |
| R1 phát trước mẫu cuối hoàn tất | Event INVALID, mismatch; raw vẫn tái tính t_rec191, MTTR60 | PASS |
| W3 terminal chỉ mang action_id | reaction19, không ORPHAN | PASS |
| L6 / L7 / L8 / L9 | CLEAN / LEAK_DETECTED / LEAK_DETECTED / UNKNOWN | PASS |
| V1 SUCCESS với hậu điều kiện false | MISSING, không reaction hợp lệ | PASS |
| Đóng gói và tài liệu | 33/33 gồm 9 nguồn protected, JSON, bảng, link, diff check | PASS |

Tính độc lập E01: 131−101=30 (MTTD), 191−131=60 (MTTR), 191−101=90 (total), 150−131=19 (reaction). R1 chỉ đủ bằng chứng sau t_end221.25, không phải221. C1/C3 được kiểm cả không mismatch, tránh nhận phép tính đúng chỉ vì event bị loại. L6 giữ tài nguyên trung tính và IP quan sát tự nhiên đúng trường/nguồn; thiếu manifest ra UNKNOWN.

### Sửa nhỏ Codex thực hiện

- Link ổ R: trong contract đổi sang link tương đối, để đọc được trên GitHub; không đổi schema/ngữ nghĩa.
- Checker NOW tìm suffix lịch sử đúng SHA-256 thay vì giả định luôn chỉ có một checkpoint mới. Không đổi build/analyse/recover/semantic, fixtures hoặc expected. Mutant đã đạt trên chính logic đó; chỉ retest package check sau sửa này.
- Lệnh retest gốc ghi lại codex-review-results.json và làm kiểm hash lịch sử báo FAIL. Đã tách kết quả mới vào codex-final-counterexamples.json; khôi phục kết quả lịch sử bằng helper/fixtures v1, chỉ ghi khi SHA-256 khớp chính xác 958c2083cc8e206a2f91918dd9e45de78e282b8d1a02f0ca85be0dfeab2023b9. Không sửa bằng tay để làm xanh. Script audit cuối không ghi đè report lịch sử.

Lệnh cuối từ Git Bash: python -I -B scratch/zer37/codex-final-audit.py. Evidence local: codex-final-audit-results.json và codex-final-counterexamples.json; cả10/10 phản ví dụ và9/9 ca delta đạt. Scratch không phải artifact đã chia sẻ hoặc scorer runtime; bảng kết quả trong ghi chú này là receipt bền.

### Hash bản trình nghiệm thu

| File | SHA-256 |
| --- | --- |
| Contract | 469a081de0a5b0ec2658c31dd7780edd9a21207bba9ca7f2e405ecfbfcbedb9a |
| Helper | 5050e58d380826bfd24b0a924522e23ee39334f5cb92615a34b36461687487d7 |
| Fixtures | c9144d7500f11a468f8d9b2f30bb3ee6ab9e1b47364890932ef5a8c78e2382a2 |
| Codex final audit script | 3444f6f66172d87b1ad6868659454776614da44044ef6f9331aab9ba21d99c33 |
| Codex final results | d95cb0c2ff479a7b91454e7bddad82573655c82a8b33d4775f130ca558c748ce |
| Codex final counterexamples | bf88c48144e4ea3fc76d6f76ae171d4c4f98781b72a8767da65238716623c4d3 |

### Nghiệm thu và publication còn chờ

Codex khuyến nghị chấp nhận cả7 PROP ở mục11 trong ranh giới thiết kế. Hai lựa chọn phương pháp: (1) cấp ID trung tính trước onset cho cả trial một incident và C0, slot C0 không vào N, War Game không đưa incident_id vào O; (2) thiếu bằng chứng clock thì phần xuyên clock MISSING, vẫn báo phần cùng clock có căn cứ. Manifest phân lớp và event INVALID→MISSING là cách bảo thủ để tránh nhận dữ liệu lỗi thành PASS; không đổi KPI/B3/M1/B2 hoặc F-01…09.

Gói cụ thể trình Hoàng: chấp nhận contract trên, khóa1.0.0 bằng đổi version không thêm ngữ nghĩa, kiểm lại ví dụ/hash; tạo nhánh zer-37-event-contract; commit/push contract và ghi chú issue, tạo PR/merge sau CI đạt rồi cập nhật ZER-37 Done bằng link immutable. Nếu cần đưa helper/fixtures thành evidence có thể tái chạy trên GitHub thì đóng gói riêng trong docs/evidence/ZER-37, không mở implementation/runtime. Không stage dirty quy ước AGENTS/README/WORKFLOW/WORKING-AGREEMENT/R1 README/NOW.

Chưa commit/push/PR/merge, chưa viết Linear, chưa chạy lab/API. Schema chưa khóa thay Hoàng. ZER-9 chỉ có thể đối chiếu AC-01 sau khóa, vẫn còn AC-02/03; G1 chưa đạt. Cách đo clock/ngưỡng sai số, đa probe, guard ACCEPT trước HEAL_STARTED và telemetry/ACL runtime còn thuộc ZER-38/10/12/40/53 và triển khai ZER-9; gói docs/offline này không chứng minh chúng đã hoạt động.


## Nghiệm thu Hoàng và khóa1.0.0 — 19/10/2026

Hoàng trả lời “được” trực tiếp sau câu hỏi nghiệm thu và quyền khóa1.0.0/commit-push/PR/merge khi CI đạt/cập nhậtZER-37Done. Chấp nhận gồm hai lựa chọn ID trước onset/C0 và CLOCK_UNVERIFIED, cùng bảy quy ước ở mục11. Đây là phê duyệt publication cho ZER-37, không phải quyền chạy lab/API hoặc mở implementation.

Codex đã khóa [contract](../../../design/r1-event-contract.md) zd-event/1.0.0 (SHA-256 fe09beb590ecc7fd82452e8108215565558e74886765da215954450415fe91fc), không thêm ngữ nghĩa so với bản đã audit. [Evidence portable](../../../evidence/ZER-37/verification.md) có helper/fixtures, phản ví dụ độc lập và kiểm release để chạy từ checkout bất kỳ. Control238/238,mutant32/32,independent10/10,focused9/9,ba envelope JSON và link đạt.

Nhánh publication zer-37-event-contract; allowlist đúng7file: contract, ghi chú issue này, check_contract.py/fixtures.json/independent_checks.py/verify_release.py/verification.md trong docs/evidence/ZER-37. Logic hàm của helper giữ nguyên, chỉ adapt đường dẫn/main/schema. Giữ .github/workflows/ci.yml và dirty quy ước ngoài scope. CI/PR/merge receipt cuối theo GitHub và mục publication trên Linear; chưa nhận merge thành công trước khi read-back.

ZER-37 chỉ phủ AC-01 của ZER-9. Không đóng cha9/G1 hoặc nhận runtime proof từ gói offline. Các phần OPEN giữ nguyên chủ sở hữu như contract mục11.
