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


## Gói triển khai ZER-9 — 19/10/2026

Hoàng yêu cầu Codex hoàn thiện ZER-9 rồi để Claude xác nhận độc lập. Writer duy nhất: Codex; chưa chuyển Claude trong lúc sửa. AC sống đã đọc qua linear_zero_door: AC-01 contract đã khóa bởi ZER-37; AC-02 HTTP/Kafka/raw/export; AC-03 ranh giới H/O và đối chứng rò. Không sửa contract/KPI/R0.

Baseline trước tạo nhánh: HEAD 5644939576a582207581f09fc81aaa680b1291ff; nhánh zer-9-event-pipeline từ origin/main 2af4d33bf02c59d7802901d523b1bb2eb39f05a3 (nội dung package37 giống nhau). Dirty có sẵn: AGENTS.md, NOW.md, delivery README/WORKFLOW, R1 README và WORKING-AGREEMENT.md untracked; SHA bảo vệ ở scratch/zer9/baseline.json. Không stage hoặc ghi đè chúng, ngoại trừ prepend checkpoint NOW được quy trình cho phép.

Phạm vi file/action trước triển khai:
- Mới agent-orchestrator/event_pipeline/{__init__,contract,store,gateway,client,audit}.py và Dockerfile/requirements.txt: factory nguồn, validator, recorder append-only/fsync, Kafka bridge O, gateway H/O tách process/credential/storage, export có hash, kiểm rò theo contract.
- Gaia và Hephaestus main.py/Dockerfile: adapter opt-in R1, context O trước onset, nhận/phát envelope không suy ID, không lấy dữ liệu H. Đổi context build của hai image trong CI và script Bash liên quan để dùng chung module; kiểm hồi quy build/scripts. Legacy chưa bật R1 không được lấy làm dữ liệu nghiên cứu.
- tests/test_event_pipeline.py; infrastructure/scripts/verify-event-pipeline.py và .sh; infrastructure/manifests/r1-event-pipeline.yaml; docs/runbooks/r1-event-pipeline.md; docs/evidence/ZER-9/verification.md và receipt thực nếu chạy. Không thêm framework/dependency mới ngoài thư viện đang có ở agent.
- Chỉ nối handoff vào ghi chú này, prepend NOW. Không sửa evidence đã nghiệm thu.

Cách kiểm: unit failure/duplicate/conflict/restart/export/hash/nguồn/mode/leak; HTTP loopback thực; Kafka thực và phép thử quyền trong namespace thử riêng nếu preflight tài nguyên phù hợp. Chỉ dữ liệu vô hại; không attack/heal/reset, không model/API trả phí, không đổi workload/PVC hiện hành. Trước thao tác runtime ghi đúng namespace/image/resources/cleanup; không dùng alert inject làm bằng chứng detect/recovery/KPI. Không commit/push/merge/Done trước Claude review và Hoàng chấp nhận bản mã cuối.

Giới hạn kiến trúc: broker legacy có H commands nên O client không được truy cập trực tiếp broker trong profile R1. Gateway O là biên duy nhất phục vụ O; gateway H có kho và quyền riêng. ZER-9 không triển khai thuật toán probe/scorer/LLM/healing hậu điều kiện của issue khác. R1 adapter fail-closed khi guard thực thi chưa cấu hình; không tạo action/recovery giả để làm đủ trace.

Bổ sung allowlist kiểm trong cùng outcome: tests/test_event_agents.py kiểm HTTP loopback qua source Gaia/Hephaestus thật, không chạy startup/Kubernetes/Kafka hoặc model; event_pipeline/telemetry.py và adapters.py nằm trong module runtime dùng chung. Venv scratch/zer9/venv chỉ bổ sung dependency đã khai báo của hai agent, không đổi môi trường toàn máy.


## Codex triển khai ZER-9 — checkpoint trước kiểm live, 19/10/2026 15:20 +07:00

Writer vẫn Codex; Hoàng yêu cầu hoàn thiện rồi Claude xác nhận, nên chưa chuyển writer/review cho Claude khi còn thiếu live. [Verification](../../../evidence/ZER-9/verification.md) và [runbook](../../../runbooks/r1-event-pipeline.md) mô tả đúng phần đã/chưa kiểm.

Đã có: event_pipeline/ (contract/factory, archive, gateway/Kafka bridge, O client, adapters và telemetry/audit); Gaia/Hephaestus bật R1 qua ZD_EVENT_URL; Dockerfile/build context/CI; hai bộ test mới; manifest profile riêng và verifier live. Nguồn contract1.0.0 và dirty work ngoài scope giữ nguyên. Đã retest cuối: 22/22 core, 2/2 source thật qua HTTP loopback; Bash behavioral toàn bộ, Nemesis3/3, contract release9/9; AST/YAML/Bash syntax/help/diff sạch. Rejection có run được đưa vào export, B2/B3 không giả rules fallback; stream raw/manifest để tránh nạp cả file H vào RAM. Hash source sau cùng sẽ lưu trong scratch/zer9/source-manifest.json; patch vẫn chưa commit trên HEAD2af4d33.

**Chưa được nhận Done:** chưa có Kafka/PVC/NetworkPolicy runtime receipt; chưa build image/CI/Claude review/merge/nghiệm thu bản mã. Automatic approval review đã từ chối chạy verifier live vì thiếu phê duyệt trực tiếp cho tạo PVC/resources, gửi/xóa topic và dọn namespace. Lệnh bị chặn trước thực thi, live-01 chưa được tạo; không đổi đường để lách. Không có lab mutation/attack/heal/model/cloud, commit/push/PR/merge/Linear write trong phiên này.

Bước cần Hoàng cho phép cụ thể: chạy verifier trên k3d-zero-door/desktop-linux; tạo namespace mới zd-zer9-<random>, topic zd.events.o.<random>, hai PVC64Mi và hai recorder/pod O giới hạn tài nguyên; kiểm HTTP/Kafka, quyền/mount thực và restart recorder tạm; export H/O đối chiếu hash, sau đó xóa đúng tài nguyên tạm mới bằng UID/nonce. Nếu FAIL giữ PVC chẩn đoán. Sau khi có quyền, Codex chạy/sửa gom/retest rồi đưa Claude một gói xác nhận độc lập đủ AC. Không suy kết quả profile tạm thành deployment legacy/G1 hay BM audit đã đạt.


## Claude xác nhận ZER-9 — gói cuối 19/10/2026

### Kết quả bàn giao và baseline

Hoàng yêu cầu Codex thực hiện ZER-9 rồi Claude xác nhận độc lập. Codex đã triển khai, tự sửa gom và kiểm offline/live; gói này chuyển sang review, không phải thông báo Done. Branch zer-9-event-pipeline, HEAD2af4d33bf02c59d7802901d523b1bb2eb39f05a3, staged rỗng lúc chốt. [Verification](../../../evidence/ZER-9/verification.md) ghi đầy đủ AC, raw, lịch sử FAIL và giới hạn. [Package manifest](../../../evidence/ZER-9/package-manifest.json) là snapshot hash để Claude chụp/đối chiếu khi nhận.

Core22/22, source-agent HTTP2/2, Bash behavioral/Nemesis3/3/contract9/9 đạt. Verifier cuối live-11 PASS18/18, kết thúc15:51:19 +07; raw H2/O5 seal/hash khớp, source hashes receipt khớp file hiện tại; đối chiếu độc lập không dùng product validator đạt. [Cleanup read-back](../../../evidence/ZER-9/cleanup-readback.json) xác nhận mọi namespace/PV/rule ES tạm đã mất. Topic được xác nhận vắng sau dừng subscriber; mọi failure receipt/export giữ ở history. Không có attack/heal/reset/LLM/cloud/spend hoặc thay workload/PVC/topic legacy.

Quyền live do Hoàng duyệt trực tiếp trong chat: namespace mới, hai PVC64Mi, topic O riêng, quyền/mount/network, restart recorder tạm, export/hash trước cleanup; duyệt bổ sung một rule monitoring mới chỉ namespace nonce + events-o → ES9200 rồi xóa đúng rule. Quyền này là của gói Codex đã kết thúc, không tự cho Claude chạy lại lab. Không commit/push/PR/merge hay đổi Linear. AC read-back Zero Door In Progress; snapshot nguyên văn ở linear-ac-snapshot.json. ZER-37 vẫn Done, contract1.0.0 giữ nguyên.

Dirty có sẵn phải giữ: AGENTS.md, delivery README/WORKFLOW, R1 README, WORKING-AGREEMENT.md chưa track. NOW có con trỏ mới nhưng toàn bộ suffix trước ZER-9 giữ nguyên; protected-check.json xác nhận6file + suffix. Không reset/stash/stage chúng để làm gói sạch. Phần ZER-9 trong event-contract.md chỉ nối thêm; các đoạn ZER-37 và gói cũ là lịch sử, không sửa.

### Claude cần đọc và kiểm

Đọc Delivery README → WORKING-AGREEMENT/NOW → gói này, AC sống ZER-9 qua named linear_zero_door nếu có (phải workspace zero-door), verification/runbook, contract khóa và phần ZER-32/8 liên quan. Không khảo sát lại toàn dự án. Nếu thiếu Linear, đối chiếu snapshot và ghi UNKNOWN live-status, vẫn review source/raw. Theo GitNexus freshness/query/context cho navigation; graph không là runtime proof. Untracked files phải review trực tiếp vì detect_changes dựa git diff không bao phủ đầy đủ chúng.

Nguồn triển khai trong manifest:
- Shared package agent-orchestrator/event_pipeline/{contract,client,adapters,store,gateway,telemetry,audit}.py, __init__, Dockerfile/requirements.
- Gaia/Hephaestus main và Dockerfile; build context agent-orchestrator trong setup-local-apps.sh/setup-phase4.sh/CI; tests/shell/run.sh.
- tests/test_event_pipeline.py, tests/test_event_agents.py.
- infrastructure/manifests/r1-event-pipeline.yaml, infrastructure/scripts/verify-event-pipeline.{py,sh}; runbook/evidence và handoff hiện tại.
Không mở rộng sửa Nemesis, chaos-worker, dashboard, scorer, guard hoặc contract đã nghiệm thu.

Review độc lập cả gói, không chỉ tìm các finding dưới đây. Ưu tiên:
1. ID/causation/source/seq/context/mode qua adapter + HTTP/Kafka; retry/redelivery/conflict/out-of-order/missing giữ raw/provenance; không chữa missing ID bằng timestamp. B1 chỉ proposal; B0/BM/B2/B3 không chạy rules giả; không init hoặc rẽ legacy executor khi R1 bật.
2. Lưu append/fsync, OS ownership, startup/hash/tail lỗi, offset commit, seal/export/rejection/unscoped quarantine, không mất hoặc giấu failure. Tự tính lại raw cuối bằng JSON/hash, không chỉ chạy helper do Codex viết.
3. H/O credentials/API/PVC/process; Kafka HMAC; giới hạn query/index/namespace; khả năng H/label/command/expected action/canary đi vào evidence/prompt. Natural IP/request không bị cấm máy móc. Prompt thực của LLM/BM chưa có: N/A/UNKNOWN đúng phạm vi, không tuyên bố chúng đã được vận hành.
4. Finding runtime quan trọng: live-09 probe agent mở H/Kafka/Prom cả40 vòng; snapshot agent0 chain KUBE-POD-FW/server20. Lượt06 probe server PASS không chứng minh actor agent an toàn. Bản cuối khóa recorder/probe/cleanup nodeSelector server, kiểm placement và cổng quyền dương/âm ba lượt trước data, có lưu attempt chưa sẵn sàng. Đánh giá ràng buộc này có đủ cho profile local hay còn P1/P2. Không tự coi sửa template đã sửa CNI toàn cluster hoặc triển khai Gaia/Hephaestus service thật.
5. Tránh claim vượt bằng chứng: live dùng payload detector synthetic qua source function thật và decision matrix thật. Nó kiểm transport; không thay proof fault/detection/guard/action/recovery/KPI, không dùng alert inject làm thực nghiệm chính. AC scope trên Linear phải được đọc đúng, ghi rõ phần cần bổ sung nếu bằng chứng này chưa đáp ứng. Legacy service deployment chưa rollout R1; production Dockerfiles/CI chưa được build/kiểm remote.

Kiểm offline được phép:
```bash
python -B tests/test_event_pipeline.py
scratch/zer9/venv/Scripts/python.exe -B tests/test_event_agents.py
bash tests/shell/run.sh
python -B tests/test_nemesis_consumer.py
python -B docs/evidence/ZER-37/verify_release.py
git diff --check
```
Dùng venv có sẵn cho source-agent test; nếu thiếu dependency ghi hạn chế, không tự cài/thay global. Có thể viết phép đối chiếu/negative test của Claude ở scratch/zer9/claude/ mới, standard library/fixture offline; không sửa checker/log/raw của Codex hoặc chạy scratch/zer9/reconcile.py vì script đó còn đọc cluster. Không chạy verifier --live, Docker/Kube/Kafka/model/API/port-forward, package install hoặc đọc Doppler/private keys để review. Các kiểm chỉ đọc live cần quyền riêng nếu thật sự cần, không làm chúng thành điều kiện ngầm cho việc đọc source.

### Quyền ghi review và đầu ra

Codex kết thúc writer sau khi chốt hash/checks; Claude nhận writer review khi Hoàng chuyển prompt. Chỉ ghi:
- docs/evidence/ZER-9/claude-review.md mới;
- nối bàn giao cuối event-contract.md hiện tại;
- thêm con trỏ đầu NOW.md, giữ phần cũ;
- scratch/zer9/claude/ nếu cần phép kiểm riêng.

Không sửa product/config/test/contract, evidence đã chốt hoặc manifest baseline, không publication/Linear/messages. Gom toàn bộ finding trong một báo cáo: file:line, P1/P2/P3, trigger/phản ví dụ/bằng chứng, tác động AC, cách sửa và retest. Nêu rõ PASS/FAIL/UNKNOWN theo từng AC/phạm vi; không pre-approve Done. Phân biệt blocker và phần thuộc issue khác. Giữ source hash ngoài allowlist; ghi HEAD/status/baseline delta, test/kết quả và hash báo cáo. Nếu không có blocker, trả READY_FOR_HOANG_ACCEPTANCE_AND_PUBLICATION (CI/merge vẫn chờ quyền), không đổi status. Nếu có, trả NOT_READY với một gói sửa hợp nhất cho Codex; Codex sửa/retest affected behavior, không yêu cầu Hoàng chuyển từng lỗi lẻ. Cuối lượt trả writer Codex, không agent nào sửa đồng thời.


## Claude review ZER-9 — 19/10/2026, 16:14 +07:00

**Verdict: NOT_READY.** [Báo cáo đầy đủ](../../../evidence/ZER-9/claude-review.md) (SHA-256 `86fc92388dbd4b4482dfe13e8b1fd744a403915cb551d7af50cbab06dd1403c4`) có 14 finding: 3 P1, 3 P2, 8 P3.

**Baseline lúc nhận.**
- HEAD `2af4d33`, staged rỗng, `git status` đúng tập trong gói.
- 26 file nguồn và receipt live-11 khớp package manifest; evidence checksum 62/62.
- Tệp bảo vệ khớp, NOW khớp `5e6cda5e…`.
- Ghi chú này trước khi nối: 64499 byte, SHA-256 `2bfdb5d1…a3726b`.
- AC sống UNKNOWN với Claude (không có `linear_zero_door`); review dùng snapshot.

**Kiểm offline.**
- Core 22/22, source-agent 2/2, Bash PASS, Nemesis 3/3, ZER-37 release 9/9, diff sạch.
- Đối chiếu raw độc lập của Claude PASS 58/58: thư viện chuẩn, không import validator. Chuỗi ID, hash, seq, redelivery, một DECISION, canary vắng.
- Phản ví dụ ở `scratch/zer9/claude/` đều lệch so với contract/runbook.

**Theo AC.**
- AC-01: PASS, kế thừa từ ZER-37.
- AC-02: FAIL đến khi sửa ZR9-01/02.
- AC-03: FAIL đến khi sửa ZR9-03.

**Blocker.**
- ZR9-01: recorder Kafka chết vĩnh viễn và không commit offset khi gặp message rác trên broker không xác thực, khi seal lúc còn event in-flight, hoặc khi lỗi binding. Pod vẫn Ready.
- ZR9-02: LINK_CONFLICT, TRIAL_CONTEXT_MISSING, RUN_SEALED, NaN và quarantine gốc không được lưu, hoặc không vào export.
- ZR9-03: audit so chuỗi con trên ID hex, nên trace sạch với `case_class` C4 ra LEAK 119/200 lần. Audit bỏ sót `reveal_terms`/`attack_type` ở target/stream. Đối chứng “cố ý lộ” live chỉ bị bắt bởi INVALID_ID.

**P2.**
- ZR9-04: một secret O client chứa cả token detector và decision_rules.
- ZR9-05: Gaia/Hephaestus của lượt live chạy trong process verifier trên host qua port-forward; gate quyền chỉ chứng minh cho pod observer. Hoàng quyết phạm vi rollout.
- ZR9-06: đánh giá ràng buộc node server: đủ cho profile local; trước khi chạy actor thật vẫn còn rủi ro từ node agent, broker và cửa sổ khởi động.

Phần thuộc issue khác và gói sửa hợp nhất nằm trong báo cáo.

**Bước tiếp:** Codex sửa ZR9-01…05 trong một lượt (P3 rẻ thì làm luôn) và retest theo danh sách trong báo cáo; gói sửa không bắt buộc chạy lab. Sau đó trả Claude retest phần delta. Không sửa product/config/test/contract/evidence của Codex, không chạy lab/API, không commit/push hay Linear, không đổi trạng thái. **Writer trả Codex.**


## Gói Claude sửa gom ZER-9 sau review — 19/10/2026

### Chỉ đạo, nguồn và writer

Hoàng yêu cầu Codex xem lại review và nếu phù hợp thì giao Claude sửa để đáp ứng nghiệm thu. Codex đã đối chiếu source và chạy lại phản ví dụ offline; đồng ý REQUEST_CHANGES / NOT_READY. Đây là quyền sửa code/test/tài liệu trong gói này; không là nghiệm thu, quyền chạy lab hoặc publication. Codex chỉ chuẩn bị gói, không sửa product song song. **Claude nhận writer thực hiện sau khi Hoàng chuyển prompt; cuối gói trả Codex retest độc lập.**

AC sống đã đọc lại qua linear_zero_door ngày19/10: [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet) vẫn In Progress; outcome/AC-01…03 không đổi so snapshot. Không dùng alert inject làm bằng chứng chính. [Contract1.0.0](../../../design/r1-event-contract.md) mục6,8,9 giữ nguyên. Gói sửa không tự hạ AC hoặc coi profile host/observer đã chứng minh quyền của actor thật.

Baseline: branch zer-9-event-pipeline, HEAD2af4d33bf02c59d7802901d523b1bb2eb39f05a3, staged rỗng. [Review Claude](../../../evidence/ZER-9/claude-review.md) SHA-256 86fc92388dbd4b4482dfe13e8b1fd744a403915cb551d7af50cbab06dd1403c4. Khi Codex nhận,25/26 file trong package-manifest còn đúng hash; chỉ issue note đã được Claude nối review, NOW được prepend đúng phạm vi. Mã/config/test chưa đổi. Snapshot trước append này: issue note a8ff939c1bb2bd41776a43c33fc4589a9d392f8bdbe11ba34e314e2d95d18f85, NOW 534638c431e950cdc9cdd3a4a94f7601e6e9f19d53f5ca1f5bd3e714a324ecc6; scratch/zer9/codex-review/baseline.json giữ hash nhận việc. Đọc actual Git/dirty/hash khi nhận, không suy HEAD mô tả toàn bộ patch uncommitted.

### Codex đã kiểm lại gì

- Đọc trực tiếp KafkaBridge.record/Gateway.submit/binding, Archive.ingest/seal/export, audit và các nhánh liên quan. GitNexus index HEAD2af4d33 được dùng để định vị; đường thread và HTTP động vẫn đối chiếu source trực tiếp. Đây là triage báo cáo, không phải một lượt audit lại toàn bộ implementation.
- Chạy nguyên bản probes.py bằng fake Kafka/temp archive:10/10 phản ví dụ còn lệch yêu cầu. K1/K3 dừng với ValueError, K2 UnicodeDecodeError; đều0commit. LINK_CONFLICT/NaN/ID dạngdict không có quarantine; export không chứa root rejection. T1 cross-index lookup lọt; D1 tái gửi cùng event cũ sau422.
- Chạy nguyên bản probe_label_hex.py: lần này C4 báo rò nhầm128/200, C0 94/200, Cx0/200; attack_type trong stream vẫn CLEAN. Số đếm ngẫu nhiên không phải tiêu chí regression.
- Chạy nguyên bản reconcile_raw.py:58/58PASS, giữ nguyên tính hợp lệ lịch sử của raw live-11; không chứng minh code sau sửa đã chạy live.
- Kết quả riêng ở scratch/zer9/codex-review/{probes-replay.json,labels-replay.json,raw-replay.txt}; không ghi đè kết quả/script Claude. git diff --check sạch. Không Docker/Kube/Kafka thật/API/model/Linear write.
- Một số anchor trong báo cáo không trỏ đúng dòng của file hiện tại: audit.py chỉ101dòng (metadata/labels ở khoảng38–61), telemetry.py42dòng (DSL khoảng29–34), adapters.py63dòng (pending khoảng14–25), client.py66dòng. Finding hành vi tái hiện được; khi báo sửa phải ghi lại line thực và hash, không sửa review lịch sử để che sai anchor.

### File/action scope của Claude

Một writer, giữ toàn bộ dirty work ngoài phạm vi. Không tạo/switch/reset nhánh hay stage. Được sửa đúng các file hiện có:
- agent-orchestrator/event_pipeline/{gateway,store,audit,client,adapters,telemetry}.py;
- agent-orchestrator/{gaia,hephaestus}/main.py nếu cần sửa đường consumer/reset hoặc kiểm client thật;
- tests/test_event_pipeline.py, tests/test_event_agents.py; được thêm tests/test_event_pipeline_regressions.py cho failure/concurrency/auth/audit, không thêm framework;
- infrastructure/scripts/verify-event-pipeline.py và .sh; infrastructure/manifests/r1-event-pipeline.yaml: sửa logic verifier/profile và credential/gate, chỉ trên đĩa;
- .github/workflows/ci.yml: nối kiểm offline mới/agent HTTP và kiểm build không push cho image liên quan ở PR; không thực thi remote workflow hay sửa điều kiện publish-image ngoài nhu cầu gói;
- docs/runbooks/r1-event-pipeline.md và docs/evidence/ZER-9/verification.md: cập nhật trạng thái hiện tại, phân biệt rõ receipt cũ/source cũ và delta offline;
- artifact mới dưới docs/evidence/ZER-9/fix-01/ (kết quả, AC→test→result, delta manifest/hash), scratch/zer9/claude-fix/ (helper/log mới); nối bàn giao cuối note này và prepend NOW, giữ nguyên phần cũ.

Không sửa contract1.0.0, requirements/Dockerfiles/setup scripts hoặc vùng khác nếu không có lý do phụ thuộc thật đã đối chiếu. Nếu thấy cần ngoài allowlist, ghi exact file và lý do cho Codex trong handoff; làm xong phần độc lập trước. Không sửa AGENTS/delivery README/WORKFLOW/WORKING-AGREEMENT/R1 README, evidence R0/ZER-37, review Claude cũ, package-manifest/evidence-checksums baseline, raw/receipt/history/cleanup/diagnostics cũ hoặc checker/replay của Codex/Claude. Manifest delta mới không thay snapshot baseline. Không cài dependency/global environment; dùng venv sẵn có và stdlib.

### Sửa theo cùng nguyên nhân, không chỉ làm xanh từng probe

1. **ZR9-01/02 — recorder/quarantine/seal/export.** Một đường xử lý rejection thống nhất cho HTTP/Kafka, gồm parse UTF-8/JSON, non-object, NaN/Infinity, ID khônghashable, binding/conflict/context, chữ ký/header không hợp lệ, late ingest. Không tin run_id/source của message chưa xác thực để gán nguồn hoặc đưa vào O read API. Lưu bytes đầu vào gốc khi không canonical hóa được, classification và provenance; kho quarantine chỉ evaluator đọc.
   - Lỗi dữ liệu từng message phải được lưu+fsync trước commit đúng offset, rồi xử lý message kế tiếp; restart không mắc lại poison pill. Không bắt blanket exception rồi commit. Lỗi I/O/fsync/archive corruption hoặc lỗi chương trình không phân loại được phải fail closed, không ACK/commit và có health báo lỗi. Kafka errors/rebalance không bị giả thành thành công.
   - Seal O phải có hàng rào giữa submit/publish và seal: không seal khi còn ACK chưa durable; kiểm race submit/seal đồng thời, nhiều partition, gửi lại, và trạng thái sau restart. Tập pending chỉ RAM không tự chứng minh đã drain sau crash. Nếu chọn409 thay chờ, client/verifier phải xử lý đúng, không nhận409 là sealPASS.
   - Event mới đến sau seal phải có LATE_INGEST/quarantine bền ngoài raw đã seal; duplicate cùng event/hash sau seal phải có quy tắc giữ nguyên raw rõ ràng. Không sửa hash/raw/manifest đã seal để nhét thêm dữ liệu.
   - Export có snapshot/count/bytes/hash kiểm lại cho run rejection/late và quarantine broker/root, kể cả không gán được run. Global quarantine phải được mô tả là phạm vi global, không gán nhầm của run; không để lộ H/secret qua O hoặc log. Snapshot đang append phải nhất quán/được khóa khi copy; export mới vào thư mục mới, không ghi đè export cũ. Test sửa file rejection/late phải phát hiện sai hash.
   - Làm luôn phần đúng dữ liệu ZR9-12: seal run chỉ có rejection, và binding+ingest nguyên tử ở đường khôngKafka; kiểm hai context xung đột gửi đồng thời. Giữ tương thích đọc raw/manifest live-11; nếu thêm version archive metadata phải nêu cách đọc bản cũ, không đổi schema envelope đã khóa.
   - Readiness HTTP phản ánh recorder sẵn sàng/thất bại thay TCP thuần; tách readiness và liveness đúng ý nghĩa, tránh dùng restart loop để che archive hỏng.
2. **ZR9-03 — audit.** Tập nhãn gồm case_class/variant_id/cause/attack_type và reveal_terms trước quét. Chuẩn hóa dấu phân cách theo contract rồi so theo ranh giới/dãy token, không so chuỗi con vào token hex. Áp dụng cả quy tắc NEUTRAL để không còn false positive cùng nguyên nhân; SECRET/OBSERVABLE/canary không bị nới lỏng. Không quét từ khóa nhãn trong triệu chứng telemetry tự nhiên ngoài phạm vi contract.
   - Đối chứng nhãn trong stream/target/source_instance dùng ID hợp lệ phải bị bắt bởi LABEL_IN_METADATA, không dựa vào INVALID_ID. Giữ ca incident_id sai định dạng riêng đúng contract; không đổi định dạng ID để làm đối chứng mới.
   - Tái dựng H có GROUND_TRUTH_LOCKED/manifest đầy đủ để audit lại O live-11 offline, lưu thành artifact mới ghi rõ OFFLINE_RECONSTRUCTION; không sửa raw cũ hoặc gọi nó là runtime receipt mới.
3. **ZR9-04 — danh tính nguồn.** File/Secret của Gaia chỉ detector+reader, Hephaestus chỉ decision_rules+reader; operator riêng; actor không có harness/evaluator/H/actor-key khác. Gateway giữ server key riêng. Loader phải từ chối key file thừa quyền theo actor, không chỉ verifier tự tạo đúng file. Test token khác nguồn bị từ chối; không đưa khóa thật vào evidence/log.
4. **ZR9-05/06/13 — phạm vi proof và chuẩn bị runtime đúng boundary.** Ghi rõ live-11 hai source function chạy trong process verifier trên Windows có quyền quản trị; pod observer là đối tượng được kiểm quyền. CLEAN chỉ dựa trên manifest entries rỗng khi đó. Không đổi receipt lịch sử. Verifier từ đây khai namespace/topic/tên tài nguyên/header/image do harness tạo trong HARNESS_MANIFEST với phân lớp và allowed_o hợp lý.
   - Ghi checklist/runtime plan cụ thể để sau sửa Codex kiểm bằng chính actor Gaia/Hephaestus tách process/pod/secret, đúng node/label/policy/mount, gate trước request đầu tiên, quyền âm/dương trên chính actor, đường Elasticsearch client thật, transport→raw→seal/export. Profile host+observer hiện tại không thay được kiểm này. Không yêu cầu phát fault/heal hoặc LLM chỉ để chứng minh vận chuyển.
   - Chưa sửa CNI/node-agent/broker/policy global, chưa bật R1 thay service legacy; server placement là điều kiện profile, không là bằng chứng cluster an toàn. Node Pending/access gate fail thì dừng trước data, không tự fallback node. Nêu rõ đường triển khai còn cần cấp quyền; không tự tạo follow-up Linear hoặc dời nghĩa vụ AC sang issue khác để nhận PASS.
5. **Sửa liên quan cùng lượt:** ZR9-07 allowlist/giới hạn DSL thực sự cần cho Gaia, chặn cross-index lookup/script/clauses chưa hỗ trợ và độ sâu/độ lớn; kiểm đường ES client thật offline bằng fake upstream chứ không chỉ URL. ZR9-08 phân biệt lỗi permanent4xx với lỗi retryable (timeout/5xx/429 theo policy), bỏ envelope permanent để alert sau có ID/timestamp/value mới; giữ cùng ID khi kết quả gửi chưa biết. ZR9-09 trả409 cho reset ở R1 và không gọi Kubernetes/clear state giả.
6. **Giới hạn/cổng còn lại:** ZR9-10 hiệu năng và fsync thư mục/count sequence còn lại củaZR9-12 phải ghi đánh giá có căn cứ cho profile/budget, điều kiện trước trial thật và nơi xử lý hiện hữu; không tự rewrite framework. ZR9-11 ghi một process gắn một trial, restart và state isolation rõ ràng. ZR9-14 nối test nguồn agent và regression vào CI, chuẩn bị build thực image production ở PR, không lấy build COPY-only cũ làm bằng chứng. Nếu thay đổi trong gói làm giới hạn P3 thành lỗi chặn thì sửa đúng nguyên nhân hoặc trả NOT_READY có bằng chứng.

### Retest và đầu ra trọn gói

- Chụp actual baseline/hash, giữ script phản ví dụ cũ bất biến. Viết regression có assertions chuẩn trước sửa, chứng minh baseline fail và bản sửa pass; tránh đếm finding=True cố định của probe cũ (E1 trong probes.py ghi True vô điều kiện). Có thể gọi lại probe cũ để so before/after, nhưng nó không thay test pass/fail mới.
- Kafka giả kiểm malformed UTF-8/JSON/list/NaN/signature/header, binding, poison message→message hợp lệ kế tiếp→restart, commit chỉ sau durable; inject lỗi I/O phải0commit và health non-ready. Seal in-flight/race/restart, duplicate/conflict, late, rejection-only run, hash tamper/export/global quarantine, atomic context có assertions riêng. Không gọi broker thật.
- Audit deterministic cases có ID hex chứa c4/c0/ab ở vị trí UUIDv4 hợp lệ; các nhãn v1 và C0–C5 được kiểm như nhãn, không ép v1 vào chuỗi hex. Thêm ít nhất1000 trace sạch cho mỗi nhãn C0–C5/v1/ab:0false positive. Positive controls label/attack_type/reveal_terms trong metadata với ID hợp lệ; canary/SECRET/OBSERVABLE/UNKNOWN và natural telemetry giữ nghĩa cũ. Seed/fixture cố định nếu cần để tái chạy ổn định.
- Secret mỗi actor/excesskey/source auth, fake ES upstream từ chối DSL và cho query thật Gaia đi qua, retry permanent/transient/reset409, health/mode boundary có test. Không nhận count tăng nếu các ca không assertion hành vi.
- Chạy core tests, agent HTTP tests bằng scratch/zer9/venv/Scripts/python.exe, regression mới, Bash behavioral, Nemesis3/3, ZER-37 release, reconcile_raw.py nguyên bản58/58; Bash syntax/help/YAML/diff--check và hash tệp bảo vệ. Không chạy scratch/zer9/reconcile.py (đọc cluster). Khi refactor consumer/HTTP, xem caller trực tiếp và regression tương ứng, không chỉ chạy lại counterexample.
- Không chạy Docker/Kube/Kafka thật/port-forward/verifier--live/LLM/Doppler/API/cài package; quyền live cũ của Codex không tự chuyển sang gói Claude sửa này. Không commit/push/PR/merge/Linear/messages. Không sửa code song song với Codex.
- Mọi ZR9-01…14 có một hàng: lỗi→cách xử lý hoặc giới hạn còn lại→test/bằng chứng→ảnh hưởng AC→còn cần bước nào. Giữ lịch sử FAIL, review và receipt cũ. Báo hash source delta, kết quả và giới hạn trong fix-01/; append handoff và prependNOW; cuối gói trả writerCodex.

**Verdict bàn giao:** có thể READY_FOR_CODEX_RETEST khi không còn blocker offline; không tự READY_FOR_HOANG_ACCEPTANCE/DONE dựa riêng vào offline. Codex retest delta/failure paths độc lập, sau đó xác định kiểm tích hợp trên revision cuối và chuẩn bị phạm vi runtime cụ thể cho Hoàng nếu cần quyền thêm. Trước nghiệm thu phải có bằng chứng H/O trên chính actor tương ứng hoặc quyết định phạm vi được Hoàng chấp nhận rõ ràng; lần giao sửa này không phải quyết định miễn bằng chứng runtime. CI/merge/publication và Hoàng chấp nhận vẫn là các cổng riêng.

## Bàn giao Claude — sửa gom ZER-9 (fix-01) — 19/10/2026, 17:00 +07:00

**Verdict: READY_FOR_CODEX_RETEST.** Không còn blocker offline. Không tự nhận READY_FOR_HOANG_ACCEPTANCE hay Done: source sau sửa chưa chạy live, CI chưa chạy, bằng chứng trên chính actor chưa có. Chi tiết từng finding, AC→test và giới hạn: [fix-01](../../../evidence/ZER-9/fix-01/README.md) (SHA-256 `a01fd06f464102b7256ed04d031dcfad1bb51352cf3f36c8f9e2344e9c1d3547`).

**Baseline lúc nhận writer.**
- HEAD `2af4d33`, staged rỗng, `git status` đúng tập trong gói.
- Note `e7c7c0cf…`, NOW `e1598bd3…`.
- Source khớp `scratch/zer9/codex-review/baseline.json`. Ảnh chụp ở `scratch/zer9/claude-fix/baseline.json`.
- `event_pipeline/` chưa track trong Git. Bản trước sửa lấy từ build context live-11, khớp hash 13/13, giữ ở `scratch/zer9/claude-fix/baseline-src/` để chạy before/after.

**Đã sửa (chỉ file trong allowlist).**
- ZR9-01/02/12:
  - một đường quarantine cho HTTP/Kafka/sau seal, JSON chặt và giữ bytes gốc, chỉ gán run khi đã xác thực;
  - recorder commit sau khi quarantine bền; I/O, archive hỏng hay lỗi Kafka thì dừng, không commit, `/readyz` 503, `/livez` tách riêng;
  - seal có hàng rào offset đã ack, chưa xong thì 409; sau seal vào `late.jsonl`;
  - export vào thư mục mới, có `export.json` kèm late/archive-scope;
  - binding+append một giao dịch; seal được run chỉ có rejection; fsync thư mục (POSIX); thêm `stream_seq_counts`. Seal cũ live-11 vẫn đọc được.
- ZR9-03: nhãn gồm `attack_type`/`reveal_terms`, so theo dãy token mục 8.3; NEUTRAL cùng cách. Verifier có đối chứng stream/target chỉ bắt qua LABEL_IN_METADATA.
- ZR9-04: file key đúng một actor; gateway từ chối role ngoài plane; verifier/template/runbook dùng Secret riêng.
- ZR9-05/13: verification/runbook/receipt mới ghi rõ agent chạy trong process host; HARNESS_MANIFEST khai giá trị harness tạo ra. Có [runtime plan](../../../evidence/ZER-9/fix-01/runtime-plan.md).
- ZR9-07: allowlist DSL log. ZR9-08: 4xx bỏ envelope, chưa rõ kết quả thì gửi lại. ZR9-09: reset 409. ZR9-11: runbook một process một trial. ZR9-14: CI thêm regression, agent HTTP, build image không push ở PR.

**Retest offline** ([kết quả](../../../evidence/ZER-9/fix-01/offline-results.txt)).
- Core 22/22, regression mới 30/30 (5/5 lượt), agent HTTP 4/4 gồm ES client thật qua proxy, Bash 37 PASS, Nemesis 3/3, ZER-37 release PASS, verifier help/từ chối, YAML, `diff --check` và whitespace file mới sạch.
- Cùng 30 regression trên source trước sửa: 1 ok, 22 FAIL, 7 ERROR ([before-after](../../../evidence/ZER-9/fix-01/before-after.json)).
- `reconcile_raw.py` giữ nguyên: 57/58. Check duy nhất fail là receipt `source_hashes` so với file hiện tại, lệch đúng 7 file đã sửa; receipt khớp bản trước sửa 10/10.
- Tái dựng audit live-11 offline: CLEAN 12/12 ([JSON](../../../evidence/ZER-9/fix-01/live11-offline-audit.json)); không phải receipt runtime.
- `probes.py` cũ không chạy được trên bridge mới vì dựa vào nội bộ cũ; hành vi của nó đã có trong regression.

**Hash source/test sau sửa:** đầy đủ trong [delta manifest](../../../evidence/ZER-9/fix-01/delta-manifest.json) (SHA-256 `e20e0660…d18fc`).
- gateway `bef7f517…`, store `e1426d0d…`, audit `313681f3…`, client `b2c3057d…`, adapters `10ca7c69…`, telemetry `d0cfcb9c…`;
- hephaestus/main `2db3b8ac…`;
- regression `82c70cf7…`, agents `d600e636…`;
- verifier `4493ba94…`, manifest `9519d224…`;
- CI `b7454b89…`, runbook `2fda69ee…`, verification `b31ef06f…`.

Không đổi contract, `contract.py`, Gaia, Dockerfile, requirements, setup scripts, tài liệu bảo vệ, review cũ, package manifest/checksums hay raw/receipt/history. `evidence-checksums.json` nay lệch `verification.md`; đây là file gói cho phép cập nhật, còn snapshot baseline thì không được sửa.

**Giới hạn còn lại.**
- ZR9-10: `Client.publish` vẫn chặn vòng async của Gaia khi chờ receipt; consumer/`records()` đọc cả run. Đủ cho transport lab, cần cursor/async trước trial thật.
- Hàng rào seal nằm trong RAM một process (template 1 replica).
- Mất điện chưa chứng minh; Windows không fsync thư mục.
- ZR9-06 là việc hạ tầng/rollout.
- CI và image chưa chạy.

**Cần quyết / bước tiếp.**
- Codex retest độc lập phần delta và failure paths, rồi chốt kiểm tích hợp trên revision cuối.
- Hoàng quyết AC-02/03 có cần bằng chứng trên chính actor ([plan](../../../evidence/ZER-9/fix-01/runtime-plan.md)) trước Done hay chấp nhận phạm vi transport.

Không lab/API/Docker/Kafka thật, không commit/push/Linear/tin nhắn. **Writer trả Codex.**

## Codex retest fix-01 và gói Claude fix-02 — ZER-9 — 19/10/2026

**NOT_READY.** [Báo cáo Codex](../../../evidence/ZER-9/codex-fix01-review/README.md) SHA-256 be245e80b7d8e6614699432ce35d1ded80505c85f4168c6691f43ab44ec3f502. Bộ kiểm đã chạy lại: core22/22, regression30/30, agentHTTP4/4, Bash37, Nemesis3/3, release9/9 đạt. Raw/receipt lịch sử giữ nguyên; reconcile57/58 chỉ lệch check source hiện tại, source receipt khớp snapshot trước sửa10/10. Hai phản ví dụ độc lập vẫn fail, không phải việc mới ngoài AC-02:

- **FX01 P2:** JSON hợp lệ 2,053byte với520 tầng list qua decode nhưng validate ném RecursionError; HTTP503 không quarantine. Message cùng dạng ký đúng nguồn làm Kafka recorder dừng/offset0, chặn event tốt tiếp theo. Cần bảo đảm input vượt độ sâu an toàn được lưu bytes/hash vào quarantine; không biến lỗi I/O/programming tùy ý thành Rejected.
- **FX02 P2:** H ghi một phần dòng rồi OSError; HTTP đầu503 nhưng readyz200, lần sau201 RECORDED nối vào raw hỏng và records() JSONDecodeError. Cần giữ trạng thái archive lỗi cho cả direct H/O và Kafka, ngừng success/append/seal/export cho tới recovery an toàn; không tự sửa/truncate evidence.

### Gói Claude sửa bổ sung fix-02

Đây là phần tiếp nối gói sửa gom đã được Hoàng giao, không là quyền lab/publication. Mục tiêu duy nhất: khép hai ca FX01/02 và kiểm hồi quy liên quan, không rewrite framework hoặc mở rộng scope nghiên cứu. Codex không sửa sản phẩm trong lượt review này. **Writer Codex giữ tới khi Hoàng chuyển prompt; sau đó Claude nhận writer duy nhất.**

**Baseline trước sửa:** HEAD2af4d33, zer-9-event-pipeline, staged rỗng. Chụp status và hash source/test/docs lúc nhận; fix-01 delta manifest đã kiểm khớp. Ghi bản sao source fix-01 vào scratch/zer9/claude-fix02/baseline-src/ trước khi sửa để hai regression mới chứng minh fail-before/pass-after. Không nhầm baseline pre-fix-01 của live-11 với baseline fix-02.

**File/action allowlist:**

- agent-orchestrator/event_pipeline/gateway.py, store.py; tests/test_event_pipeline_regressions.py cho hai lỗi và các nhánh ảnh hưởng.
- audit.py chỉ nếu sửa nhánh SECRET sạch bị false UNKNOWN đã nêu trong báo cáo; một thay đổi nhỏ kèm cả clean/leaked SECRET tests, giữ UNKNOWN thiếu bằng chứng. Đây là giới hạn cũ liên quan, không là một blocker mới hoặc yêu cầu rewrite audit.
- docs/runbooks/r1-event-pipeline.md, docs/evidence/ZER-9/verification.md để mô tả chính xác fail closed/recovery; tạo docs/evidence/ZER-9/fix-02/** và scratch/zer9/claude-fix02/**.
- Chỉ append issue note này, prepend NOW; không sửa bàn giao hay các báo cáo cũ. Không tự sửa contract.py hoặc contract prose/schema: xử lý giới hạn ở transport/storage. Nếu thật sự cần một file phụ ngoài allowlist, ghi cụ thể lý do/dependency và làm hết phần độc lập trước, không đổi âm thầm.

**Yêu cầu hành vi:**

1. Giới hạn cấu trúc/đệ quy phải kiểm an toàn trước validator, canonicalization hoặc bước đệ quy không an toàn; xét cả HTTP/Kafka/direct Archive.ingest khi cần. Cùng dữ liệu JSON bị từ chối phải có bản bytes/hash bền trước commit và không chết lại ở chính đường reject/hash. Chỉ gán run/source khi đủ xác thực như fix-01. Không nâng recursionlimit toàn process hoặc bỏ forbidden-key checks.
2. Lỗi archive I/O/fsync/integrity phải giữ trạng thái lỗi sticky dưới khóa cho cả hai plane và mọi đường append/quarantine/late/seal/export liên quan. Không thành công sau khi ghi không chắc chắn. readyz503, livez vẫn200; request sau không thêm bytes vào archive hỏng. Invalid input đã quarantine thành công vẫn xử lý tiếp. Không tự truncate, clear failure, reset archive hoặc tự sửa file; restart/recovery phải tiếp tục từ chối raw đứt và khai rõ khi nào operator phải xử lý.
3. Không sửa failure thành success trên receipt lịch sử; không gọi offline fault injection là thử mất điện thật. Giữ đặc tính one writer, không H read API, không giảm ràng buộc source/mode, seal/hash/export và các fix audit/key/DSL trước.

**Retest bắt buộc, chạy gom một lượt trên source cuối:**

- Hai test hồi quy độc lập assert failed-before trên snapshot fix-01, passed-after: (a) deep-list và deep-dict input parse được nhưng vượt recursion path hiện tại, qua HTTP có token và Kafka giả ký đúng, quarantine có bytes/hash, offset được commit đúng sau lưu, event tốt tiếp theo và restart không lặp poison; (b) H và direct O ghi dở rồi OSError, cùng lỗi fsync/quarantine append: request đầu503, readyz503, request sau không được201/202/success và raw không thêm bytes; close/reopen từ chối phần dòng đứt; không trộn lỗi dữ liệu với I/O fatal. Có ca healthy/invalid-control để tránh mọi thứ luôn503.
- Đọc và chạy nguyên probes Codex ở codex-fix01-review/ (chạy từ root), hoặc bản sao giữ nguyên hành vi; kết quả mới nằm trong fix-02. Probe deep_http.py sẽ đổi expectation: offset tiến/quarantine/event kế được ghi thay vì failure; không chỉnh expected thành PASS giả. Probe h_partial_http.py phải không nhận request sau hoặc báo READY trên raw lỗi.
- Core, regression cập nhật, agentHTTP bằng venv có sẵn, Bash37, Nemesis3, releaseZER37; verifier help/refuse-without-live, YAML/syntax, diff/whitespace file chưa track. Chỉ lặp thêm khi có code change, race hoặc lỗi chưa giải thích; không cần5lượt mọi test thường lệ.
- Historical hashes giữ nguyên ngoài verification.md được cập nhật. Source hashes live-11 vẫn phải đối chiếu với baseline đúng của nó; report riêng current delta. Không sửa script reconcile/hash manifest cũ chỉ để tăng57/58 thành58/58.

**Bảo vệ:** toàn bộ raw/receipt/history, claude-review.md, fix-01/**, codex-fix01-review/**, package/checksums, checkers Codex/Claude cũ, contract, Dockerfile/requirements/setup/CI hiện tại và dirty quy ước ngoài allowlist giữ nguyên. Không Docker/Kube/Kafka thật/port-forward/verifier--live/LLM/Doppler/API/cài package. Không stage/commit/push/PR/merge/Linear/messages. Không tự mở claim actor isolation hoặc chuyển nghĩa vụ ZR9-05/06 sang issue khác; chưa có miễn bằng chứng runtime.

**Bàn giao một lần:** hai finding→fix→test actual→hash; scope/protected check; snapshot trước/sau source; giới hạn còn lại. Verdict tối đa READY_FOR_CODEX_RETEST, chưa Hoàng nghiệm thu/Done. Trả writer Codex cuối gói. Sau retest Codex mới chuẩn bị kiểm tích hợp trên revision cuối và actor boundary tương ứng; không hỏi quyền lab trong khi lỗi offline còn tồn tại.

## Bàn giao Claude — fix-02 ZER-9 (FX01/FX02) — 19/10/2026, 18:50 +07:00

**Verdict: READY_FOR_CODEX_RETEST.** Hai P2 của Codex retest fix-01 đã khép offline. Không tự nhận READY_FOR_HOANG_ACCEPTANCE hay Done: source sau fix-01/fix-02 chưa chạy live, CI chưa chạy, chưa có bằng chứng trên chính actor. Chi tiết finding→fix→test→hash và giới hạn: [fix-02](../../../evidence/ZER-9/fix-02/README.md) (SHA-256 `70571292dacb84cb3c4043fdfdd0f05e2f3b238d91e40d991f252f6122e2c3e0`).

**Baseline lúc nhận writer.**
- HEAD `2af4d33`, staged rỗng, `git status` giống lúc bàn giao.
- Note `c1be46ee…`, NOW `8c9021f9…`. Hash source/test/docs khớp fix-01 delta manifest, không lệch.
- Bản sao source fix-01 ở `scratch/zer9/claude-fix02/baseline-src/`, ảnh chụp ở `scratch/zer9/claude-fix02/baseline.json`. Đây không phải baseline trước fix-01 của live-11.

**FX01 — JSON lồng sâu.**
- Fix: `too_deep` kiểm độ sâu bằng vòng lặp, giới hạn 32 tầng cho cả envelope (live-11 sâu 4). Kiểm chạy trước validator và binding ở `Gateway.check` (HTTP, Kafka) và `Archive.ingest` (gọi trực tiếp); vượt giới hạn là INVALID. Quarantine lưu bytes gốc kèm hash, không lưu bản parse. Input đã xác thực gán run/nguồn như fix-01. `render` không ném lỗi, nên đường reject/hash không chết lại. Không đổi `contract.py`, không nâng recursionlimit, không bỏ kiểm khóa cấm.
- Test thực tế:
  - Kafka ký đúng, list và dict 520 tầng: quarantine có bytes/hash; commit chỉ sau khi dòng đã trên đĩa (kiểm bằng hook); event kế tiếp được ghi; restart bridge và restart process không gặp lại poison.
  - HTTP trên O có Kafka và O ghi trực tiếp: 422 INVALID, không publish; ca 32 tầng vẫn được nhận.
  - Gọi trực tiếp 520 và 5.000 tầng: Rejected, không RecursionError.
  - Probe `deep_http.py` chạy nguyên bản: 422, quarantine 1, recorder không lỗi, commit 2, readyz 200, event kế tiếp được ghi.

**FX02 — lỗi archive phải sticky.**
- Fix: mọi append đi qua `Archive.write`. Exception khi ghi, fsync, tạo thư mục run, seal, hoặc đọc toàn vẹn ở records/seal/export đặt `failure` dưới khóa. `usable()` chặn check/ingest/reject/records/seal/export cho cả H và O, có hay không Kafka. `/readyz` 503 `ARCHIVE_FAILED:<lý do>`, `/livez` 200. Dòng không đọc được là ArchiveFailure, nên mở lại thì từ chối. Không truncate/clear/reset/sửa file; phục hồi là restart process, ca operator phải xử lý ghi ở runbook.
- Test thực tế:
  - H và O ghi trực tiếp, append ghi dở: request đầu 503, readyz 503; request hợp lệ sau đó 503, input sai 503, `/seal` 503; records/export ArchiveFailure; không thêm byte nào; mở lại từ chối, bytes giữ nguyên.
  - fsync lỗi và append quarantine ghi dở: archive cũng dừng.
  - Recorder Kafka gặp lỗi: HTTP 503, không publish, offset 0; restart bridge trong process không xóa được lỗi.
  - Control: lỗi dữ liệu 422 và lỗi chương trình trước khi ghi không làm archive dừng; export vào thư mục đã tồn tại cũng không.
  - Probe `h_partial_http.py` chạy nguyên bản: 503, readyz 503, request sau 503, đọc ra ArchiveFailure.
- Test I/O của fix-01 được sửa theo yêu cầu mới: phải restart process (archive được kiểm lại) mới phục hồi.

**SECRET sạch.** Một nhánh audit: SECRET không gặp ở O nay là CLEAN thay vì UNKNOWN nhầm. Rò rỉ hoặc `o_visible` vẫn HARNESS_SECRET; lớp lạ hoặc thiếu bằng chứng vẫn UNKNOWN. Có test cho cả ba.

**Retest gom một lượt trên source cuối** ([kết quả](../../../evidence/ZER-9/fix-02/offline-results.txt)).
- Core 22/22; regression 38/38.
- Cùng file test trên snapshot fix-01: 30 ok, 7 FAIL, 1 ERROR. Đủ 8 test mới/sửa fail đúng lý do; control đạt ([before-after](../../../evidence/ZER-9/fix-02/before-after.json)).
- Hai probe Codex chạy nguyên bản ([so sánh](../../../evidence/ZER-9/fix-02/probe-results.json)).
- Agent HTTP 4/4, Bash 37 PASS, Nemesis 3/3, ZER-37 release 9/9.
- `reconcile_raw.py` nguyên bản 57/58: chỉ lệch check source live-11 so với file hiện tại (7 file từ fix-01). Source receipt so với bản trước fix-01 PASS 10/10.
- Verifier help đạt, thiếu `--live` bị từ chối (exit 2). YAML 13 document. `diff --check`, whitespace và link sạch.

**Hash fix-01 → fix-02** ([delta manifest](../../../evidence/ZER-9/fix-02/delta-manifest.json), SHA-256 `9949c2e60623ef5a51fb1d9c87544b8cbb9b40e8da1a9c3ea113455d8c64cffb`).
- gateway `bef7f517…` → `74fef63b…`
- store `e1426d0d…` → `2b9a051a…`
- audit `313681f3…` → `b7ebc319…`
- regression `82c70cf7…` → `dd1dc89e…`
- runbook `2fda69ee…` → `302b0df7…`
- verification `b31ef06f…` → `65717a65…`

**Phạm vi và file được bảo vệ.**
- Không đổi gì ngoài allowlist: contract, client/adapters/telemetry, Gaia/Hephaestus, verifier, manifest, CI, Dockerfile, requirements và setup đều giữ nguyên.
- `codex-fix01-review/**` khớp checksums của chính nó 9/9; `fix-01/**` khớp hash bàn giao 6/6.
- `evidence-checksums.json` 61/62: chỉ lệch `verification.md`, file được phép cập nhật. Raw, receipt và history giữ nguyên.

**Giới hạn còn lại.**
- Trạng thái lỗi nằm trong một process. Sau restart, dòng đầy đủ mà fsync đã báo lỗi vẫn được nhận lại; độ bền khi mất điện chưa chứng minh. Windows không fsync thư mục.
- Fault injection chỉ là patch; chưa thử ENOSPC, EIO hay mất điện thật.
- `MAX_DEPTH` là giới hạn transport, không phải điều khoản contract.
- Giới hạn fix-01 còn nguyên:
  - ZR9-10;
  - hàng rào seal một process;
  - ZR9-05/06 và quyền trên actor thật;
  - `publish-images` chưa `needs` job R1;
  - CI và image chưa chạy.

**Bước tiếp.**
- Codex retest độc lập fix-02, rồi chuẩn bị kiểm tích hợp trên revision cuối và ranh giới actor.
- Hoàng giữ quyền nghiệm thu và quyết định bằng chứng runtime; chưa có miễn bằng chứng.

Không lab/API/Docker/Kafka thật/cài package, không stage/commit/push/Linear/tin nhắn. **Writer trả Codex.**


## Codex retest fix-02 — FX02 còn nhánh đọc nguồn — 19/10/2026

**NOT_READY: một P2 FX02-R1.** [Báo cáo](../../../evidence/ZER-9/codex-fix02-review/README.md), SHA-256 a03be5240784317cfc306adf965c94bd50e9769b7842c4cf427b482654ed9c4a. Đã retest core22/regression38/agentHTTP4/Bash37/Nemesis3/release9 và assert hai probe cũ: đều đạt. FX01 đã khép offline; FX02 ghi dở/fsync đã sửa đúng. Lỗi còn lại thuộc cùng cơ chế chuyển archive sang trạng thái lỗi:

- records() chỉ bắt ArchiveFailure, không bắt OSError nguồn; export bỏ sót lỗi đọc late/global quarantine. Probe HTTP EIO: RemoteDisconnected, readyz200, POST sau201; ma trậnH/O tái hiện6nhánh bỏ sót. Seal bắt lỗi nguồn đúng; lỗi thư mục đích export hiện giữ archive Ready đúng. Không gọi đây là thử đĩa thật.
- Raw/receipt cũ không đổi.41source/protected khớp deltafix02,3artifactfix02 khớp; Codexfix01 9/9; historical61/62 chỉ verification.md theo allowlist. HEAD2af4d33, staged rỗng. Linear được đọc In Review, không ghi.

### Gói Claude fix-03 — hoàn tất cơ chế lỗi nguồn của FX02

Hoàng chuyển đoạn giao việc thì Claude nhận writer; trước đó Codex giữ writer. Phạm vi là phần FX02 còn thiếu trong gói sửa đã giao, không mở rộng research/lab. Không tiếp tục vá từng exception riêng mà chưa rà hết ranh giới nguồn/đích.

**Trước sửa:** snapshot/hash source fix-02, HEAD/dirty/staged; giữ bản sao ở scratch/zer9/claude-fix03/baseline-src/. Đối chiếu lại yêu cầu FX02: lỗi ghi không chắc chắn hoặc lỗi đọc nguồn archive phải dừng archive; lỗi input đã quarantine thành công, lỗi logic trước ghi và lỗi đích export không tự làm hỏng archive. Ghi ngắn ma trận từng đường và vị trí chuyển lỗi trước khi triển khai, không cần framework mới.

**Allowlist:**
- agent-orchestrator/event_pipeline/store.py và tests/test_event_pipeline_regressions.py. gateway.py chỉ nếu cần bắt ArchiveFailure để trả503 tại consumer; hiện GET đã có nhánh đó nên ưu tiên chuyển exception đúng tại source.
- docs/runbooks/r1-event-pipeline.md, docs/evidence/ZER-9/verification.md; tạo fix-03/** trong evidence và scratch/zer9/claude-fix03/**; append note này và prepend NOW.
- Giữ contract.py/contract, audit/client/adapters/telemetry, Gaia/Hephaestus, verifier, CI/manifests/Dockerfiles/requirements/setup và dirty quy ước ngoài phạm vi. Bảo vệ fix-01/**, fix-02/**, cả hai codex-fix*-review/**, raw/receipt/history, review/checksums cũ, test/probe cũ không chỉnh để đổi verdict.

**Hành vi và giới hạn:**
1. Rà đường đọc nguồn records/manifest/seal và export nguồn raw/rejections/late/global quarantine; lỗi open/read/stat/hash/copy đọc phía nguồn phải qua ArchiveFailure và failure sticky dưới khóa. Phân biệt tồn tại file tùy chọn hợp lệ với EIO/permission failure; không biến lỗi đọc thành file rỗng hoặc bỏ qua. Lỗi dữ liệu hỏng vẫn dừng như trước.
2. O HTTP GET gặp lỗi nguồn trả503 NOT_DURABLE thay vì ngắt kết nối. Sau lỗi, readyz503/livez200, mọi ghi/quarantine/seal/export bị từ chối và không thêm byte; H/O trực tiếp và Kafka không được né trạng thái archive failure. Không cần đổi thiết kế network hay chạy lab.
3. Lỗi tạo/ghi/fsync/chmod ở thư mục đích export phải thất bại export, không đặt lỗi lên nguồn khỏe. Không bọc cả export bằng catch OSError rồi fail archive một cách vô điều kiện. Không truncate/reset/sửa hoặc tự xóa evidence. Code thay đổi tối thiểu tại ranh giới nguồn/đích, không abstraction tổng quát.

**Kiểm cùng nguyên nhân một lần:**
- Tạo regression mới độc lập fail-before trên snapshotfix02/pass-after. H/O, records(), seal(), export đọc late và global quarantine; dùng lỗi nguồn OSError EIO thật trong patch tại open/read hoặc hàm đọc nguồn, không chỉ patch hàm cấp cao để sẵn ArchiveFailure. Có ca lỗi nguồn ngay giữa export/copy và trước export (stat/hash) nếu đường mới khác; kiểm actual readiness, request sau, byte không đổi, HTTP503 khi applicable. Đối chứng nguồn khỏe/invalid input vẫn chạy và export lỗi ở đích không làm nguồn chết.
- Hai probe trong codex-fix02-review/read_http.py và read_matrix.py nguyên bản (từ root): HTTP kết quả mới503/503/503; matrix6nhánh nguồn đang bỏ sót phải chuyển ArchiveFailure/non-ready, hai sealcontrol giữ đúng, hai destinationcontrol vẫnReady. Đọc/assert JSON, không coi exit0 của probe là PASS vì nó in quan sát.
- Giữ core22 và mọi regression38 cũ đạt cùng test mới; chạy agentHTTP4 và hai probe codexfix01 nguyên bản có assertions theo giá trị. Bộ Bash37/Nemesis3/ZER37 vừa đạt trên file không đổi: không lặp chỉ tăng counter; chạy lại nếu sửa consumer liên quan hoặc có thất bại mới. Syntax/diff--check/whitespace/link/hash cuối gói. Không đổi test cũ thành chỉ thử ArchiveFailure để bỏ qua OSError.
- Chỉ ghi kết quả mới trong fix-03/scratch riêng. Source receiptlive11 so đúng baseline của nó, không sửa hash receipt để khớp source mới.

**Quyền:** chỉ offline temp archive/HTTP loopback/fakeKafka/fault injection; không Docker/Kube/broker thật/port-forward/LLM/Doppler/API/cài package. Không stage/commit/push/PR/merge/Linear/messages. Một writer, không sửa song song. Không tự miễn runtime actor. Đối chiếu contract và ma trận lỗi trước sửa vì đây là cơ chế cùng nguyên nhân còn sót qua hai gói, không coi số vòng là lý do hạ chuẩn nghiệm thu.

**Handoff:** finding→nguyên nhân→fix→actual regression/probe→hash/scope/protection/giới hạn. Tự review toàn ma trận trước trả, một bàn giao cuối; writer trả Codex. Verdict tối đa READY_FOR_CODEX_RETEST. Khi offline thật sự khép, Codex chuẩn bị kiểm tích hợp source cuối và actor boundary, sau đó mới các cổng publication/Hoàng nghiệm thu.

## Bàn giao Claude — fix-03 ZER-9 (FX02-R1 lỗi đọc nguồn) — 19/10/2026, 19:45 +07:00

**Verdict: READY_FOR_CODEX_RETEST.** FX02-R1 đã khép offline: mọi đọc nguồn archive lỗi đều làm archive dừng sticky; lỗi ở đích export chỉ làm export thất bại. Không tự nhận READY_FOR_HOANG_ACCEPTANCE hay Done: source sau fix-01..03 chưa chạy live, CI chưa chạy, chưa có bằng chứng trên chính actor. Chi tiết finding→nguyên nhân→fix→test→hash: [fix-03](../../../evidence/ZER-9/fix-03/README.md) (SHA-256 `2ac57681e238cd60925a6303eba55f86b7fe5a8bb87b624e4c3e700cafc064d7`).

**Baseline lúc nhận writer.**
- HEAD `2af4d33`, staged rỗng, `git status` giống lúc bàn giao.
- Note `54d955f0…`, NOW `9666c87d…`. Hash source/test/docs khớp delta fix-02, không lệch.
- Bản sao source fix-02 ở `scratch/zer9/claude-fix03/baseline-src/`, ảnh chụp ở `baseline.json`.
- Ma trận nguồn/đích viết trước khi sửa: `scratch/zer9/claude-fix03/matrix.md`.

**Nguyên nhân.** Lỗi được bắt theo từng caller, không có ranh giới chung giữa đọc nguồn và ghi đích. Rà toàn bộ thấy thêm ba chỗ cùng nguyên nhân ngoài hai nhánh Codex nêu (records, export late/global):
- kiểm tồn tại bằng `Path.exists/is_symlink/is_dir`: stat `manifest.json` khi ingest/quarantine/submit Kafka, thư mục run khi seal;
- `shutil.copyfile` trộn đọc nguồn với ghi đích;
- hướng ngược lại: bản sao ở đích lệch hash làm dừng nguồn khỏe.

**Fix (chỉ `store.py`; gateway không đổi).**
- `entry()`: lstat; file vắng là None, lỗi khác là ArchiveFailure. `reading()`: OSError khi đọc nguồn là ArchiveFailure.
- Hai helper dùng cho mọi đọc nguồn: iter_file, summary, path, kiểm tồn tại ở init/ingest/reject/sealed/manifest/seal/export, phần đọc của bản sao export.
- Op dưới khóa đặt failure sticky: records, seal, export, path, run_dir, `lookup()`. Tên lỗi I/O gốc vào `ARCHIVE_FAILED:<lý do>`.
- Bản sao export: vòng lặp tách phần đọc nguồn (sticky, hash luồng phải khớp) với phần ghi đích (OSError). Bản sao lệch là `OSError(EIO)`.
- Không truncate, reset hay xóa. Symlink thư mục run nay sticky ở mọi op (trước đây chỉ khi export).

**Test thực tế.**
- `SourceReadFailureTests` (4 method, H và O). Lỗi là `OSError(EIO)` thật tại `open`/`os.stat`/`os.lstat` của đúng một file, đếm lần đọc. Các ca: records (open, giữa file), `GET /events` 503, `/seal` (stat thư mục run; raw open là control), export (late stat/open/hash/giữa bản sao, quarantine phạm vi archive stat/open/giữa bản sao, raw giữa bản sao), write path (POST H/O, Kafka submit và recorder).
- Mỗi ca kiểm: readyz 503 và livez 200; POST, input sai, seal, records, export sau đó bị từ chối; bytes không đổi; restart mở lại được.
- Destination control: đích tồn tại, ENOSPC, bản sao lệch, chmod, fsync đều là OSError, nguồn Ready; sau đó export đủ.
- Source cuối 42/42. Snapshot fix-02: 38 method cũ đạt, 4 method mới fail với 30 subtest đúng lý do: OSError lọt, RemoteDisconnected, failure None, hoặc đích làm nguồn `INTEGRITY`. Control đạt ([before-after](../../../evidence/ZER-9/fix-03/before-after.json)).
- Probe Codex nguyên bản, assert theo giá trị ([kết quả](../../../evidence/ZER-9/fix-03/probe-results.json)):
  - `read_http`: 503 / readyz 503 / POST 503;
  - `read_matrix`: 6 nhánh nguồn chuyển ArchiveFailure, không Ready; 2 seal control giữ; 2 destination control vẫn Ready;
  - `deep_http` và `h_partial_http` giữ đúng.
- Core 22/22, agent HTTP 4/4.
- `reconcile_raw` 57/58 như trước (7 file). Receipt so với bản trước fix-01 PASS 10/10.
- py_compile, `diff --check`, whitespace, link đạt ([offline](../../../evidence/ZER-9/fix-03/offline-results.txt)).
- Bash/Nemesis/ZER-37 không chạy lại: file không đổi, không import `event_pipeline`, consumer không đổi.

**Hash fix-02 → fix-03** ([delta manifest](../../../evidence/ZER-9/fix-03/delta-manifest.json), SHA-256 `4150a99e6683917399f76fdf1d0ba441bb74c501916a5503a99ac60c919e31fa`).
- store `2b9a051a…` → `de30c0ac…`
- regression `dd1dc89e…` → `b2196133…`
- runbook `302b0df7…` → `946aa7f4…`
- verification `65717a65…` → `d879ed2d…`

**Phạm vi và bảo vệ.**
- Không đổi gì ngoài allowlist; gateway, audit, contract và các file được bảo vệ đều giữ nguyên.
- `codex-fix02-review/**` 11/11, `codex-fix01-review/**` 9/9, `fix-02/**` 5/5, `fix-01/**` 6/6.
- `evidence-checksums.json` 61/62, chỉ lệch `verification.md`. Raw, receipt và history giữ nguyên.

**Giới hạn.**
- Lỗi I/O chỉ là patch; chưa thử đĩa thật, mất điện hay PVC.
- Trạng thái lỗi nằm trong một process.
- Export thất bại có thể để lại bản sao dở, không có export.json hoàn tất; operator export lại vào thư mục mới.
- Giới hạn fix-01/fix-02 còn nguyên.

**Bước tiếp.**
- Codex retest độc lập fix-03.
- Khi offline khép, Codex chuẩn bị kiểm tích hợp source cuối và ranh giới actor, rồi mới đến các cổng publication.
- Hoàng giữ quyền nghiệm thu; chưa có miễn bằng chứng runtime.

Không lab/API/Docker/Kafka thật/cài package, không stage/commit/push/Linear/tin nhắn. **Writer trả Codex.**


## Codex retest fix-03 — offline đã khép, chuẩn bị runtime actor — 19/10/2026

**READY_OFFLINE. Không có finding mới chặn fix-03.** [Báo cáo](../../../evidence/ZER-9/codex-fix03-review/README.md) và [phạm vi runtime để Hoàng duyệt](../../../evidence/ZER-9/codex-fix03-review/runtime-scope.md). Core22/22, regression42/42, agentHTTP4/4; snapshotfix02 fail đúng30subcase mới; bốn probe Codex assert JSON đạt. Sáu probe độc lập PermissionError/luồng nguồn đổi/ghi đích dở trên H/O đạt: lỗi nguồn dừng archive, lỗi đích giữ nguồn khỏe, không đổi bytes nguồn. FX02-R1 khép offline.

44 mục intake khớp deltafix03; chỉ bốn file đổi theo allowlist. Codexfix01review9/9, fix02review11/11 và artifact hash được các delta liệt kê khớp; historical61/62 chỉ verification.md theo allowlist. Receiptlive11 so đúng source cũ10/10; so source hiện tại57/58 do7file đã sửa, không dùng làm proof mới. HEAD2af4d33, zer-9-event-pipeline, staged rỗng. Linear đọc In Review, chưa ghi.

Codex không sửa sản phẩm, không lab/API/install/Git publication/Linear. Writer Codex. Runtime source cuối và chính pod Gaia/Hephaestus còn thiếu; gói đề xuất dùng context k3d-zero-door/desktop-linux, ba production image build/import, namespace/topic nonce mới, hai PVC64Mi, tối đa5pod, key/policy theo actor, ES rule tạm giới hạn nếu cần, pre-data gate từ chính actor, receipt/export/audit và cleanup đúngUID/nonce. Không fault/heal/LLM. Đây là phạm vi đề xuất chưa là quyền chạy; CI/merge/Hoàng nghiệm thu còn sau đó.


## Codex thực hiện gói actor và publication ZER-9 — 19/10/2026

Hoàng trực tiếp yêu cầu hoàn tất đúng AC ZER-9, đồng ý gói runtime đề xuất và cho phép commit/PR/cập nhật Done trên Linear khi đủ nghiệm thu. Codex writer, baseline HEAD2af4d33, staged rỗng; dirty ngoài ZER-9 được bảo vệ theo scratch/zer9/actors/baseline.json. File mới: verify-event-actors.py/.sh, r1-event-actors.yaml, test_event_actor_verifier.py; cập nhật runbook/verification/evidence và CI cần thiết để kiểm gói. Không đổi contract, legacy actor logic hay receipt cũ. Publication chỉ gồm gói ZER-9; quyền làm trọn issue bao gồm push, PR, kiểm CI và merge sau khi đạt. Không fault/heal/LLM. Runtime đúng [phạm vi đã duyệt](../../../evidence/ZER-9/codex-fix03-review/runtime-scope.md), tối đa2h, tài nguyên mới nonce riêng. Preflight trực tiếp node31–34% memory, contexts khớp. Offline verifier4/4 đạt, có ca từ chối access gate mở và export lệch hash.


## Codex runtime actor cuối ZER-9 — 19/10/2026,20:03 +07:00

[Evidence](../../../evidence/ZER-9/actor-runtime/README.md): PASS10/10 runtime; đối chiếu raw/image độc lập68/68, source khớp hash fix-03. Hai pod actor production có gate riêng trước context, khóa server node; O-only role keys/query, healer/reset409; chuỗi ID Kafka/PVC, poison offset5/good-next6/commit7, restart, seal, late/export và cleanup đạt. Không product source change sau fix-03; chỉ thêm verifier/overlay/test, runbook/CI. Verifier mới4/4. Giới hạn hội tụ policy, host harness/evaluator, synthetic alert, chưa fault/KPI/LLM/PVC hỏng giữ rõ trong evidence. Đang chuẩn bị commit/PR/CI/merge trong quyền Hoàng vừa cấp; Linear vẫn In Review cho tới khi merge đạt.
