# ZER-37 — Hợp đồng sự kiện và trạng thái phục hồi R1

[Ghi chú issue và gói giao](../delivery/milestones/R1-measurement/event-contract.md) · [Milestone R1](../delivery/milestones/R1-measurement/README.md) · [Checkpoint](../delivery/NOW.md) · Issue: [ZER-37](https://linear.app/zero-door/issue/ZER-37/khoa-hop-djong-event-va-trang-thai-phuc-hoi), cha [ZER-9](https://linear.app/zero-door/issue/ZER-9/thong-nhat-hop-djong-su-kien-va-luu-dau-vet)

**Trạng thái: LOCKED. Phiên bản zd-event/1.0.0.** Codex audit cuối không còn finding chặn; Hoàng đã nghiệm thu contract, các lựa chọn ở mục 11 và cho phép publication trong chat ngày 19/10/2026. Đây là thiết kế đã khóa, chưa phải producer/consumer triển khai hay bằng chứng runtime. Mọi ví dụ ở mục 10 vẫn là SYNTHETIC/OFFLINE.

**Người soạn:** Claude, 19/10/2026, từ 12:45 +07:00. Giờ chốt, hash và kết quả kiểm ghi ở bàn giao cuối ghi chú issue.

**Bản sửa 1 (19/10/2026, sau Codex review lúc 13:34 +07:00).** Sửa gom RV37-01…05 trong [ghi chú issue](../delivery/milestones/R1-measurement/event-contract.md): bằng chứng và thời điểm phát RECOVERY_VERIFIED (mục 7.5), quy tắc rò tài nguyên harness (mục 8.3), chuẩn hóa đồng hồ (mục 4.3), ràng buộc liên trường và nhóm (mục 5.3, 6.4, 7.4), bất biến ghép (mục 6.3). Bản review đầu (`0.1.0`, SHA-256 `7409c1a1…94e21c`) được giữ ở bàn giao để đối chiếu. Không đổi D-01…D-05, B3/M1/B2 hay tham số F-01…F-09.

**Revision nền.** Nhánh `zer-36-g0-receipt`, HEAD `42af1c1afd90a51e80f2d01e690169162e79444b`, staged rỗng. Dirty có sẵn ngoài phạm vi: `AGENTS.md`, `docs/delivery/NOW.md`, `docs/delivery/README.md`, `docs/delivery/WORKFLOW.md`, `docs/delivery/milestones/R1-measurement/README.md`, `docs/delivery/milestones/R1-measurement/event-contract.md` (gói Codex) và `docs/delivery/WORKING-AGREEMENT.md` (untracked). Source sản phẩm khảo sát ở mục 2 sạch so với HEAD.

**AC.** Claude không có kết nối `linear_zero_door`, và gói giao cấm connector thay thế. Tài liệu này dùng snapshot AC trong gói giao, do Codex đọc trực tiếp lúc khoảng 12:40 +07 ngày 19/10:
- ZER-37 AC-01: ID, timestamp, trạng thái; schema/version và ví dụ; nguồn riêng cho effect/detect/action/recovery/stop; action terminal không đồng nhất với RECOVERY_VERIFIED.
- ZER-9 AC-01 tương ứng. AC-02 (truyền và lưu raw) và AC-03 (chống rò) còn phải thực thi ở gói sau. Contract phải đủ phục vụ chúng, nhưng không nhận đã đạt runtime.

Codex cần đối chiếu AC sống khi review.

## 0. Tóm tắt và nhãn nguồn

| Nhãn | Nghĩa |
| --- | --- |
| **ACC** | Quy ước đã được Hoàng chấp nhận: ZER-32 mục 3–4, 7 (D-01…D-05, RV-01…RV-03) và ZER-8 mục 4–5, 11–13 |
| **LOCK** | Quy ước của contract này đã được Codex review và Hoàng chấp nhận ở ZER-37; không sửa các nguồn ACC |
| **OPEN** | Điểm chưa có nguồn, giao cho issue sở hữu (ZER-38, ZER-10, ZER-53…); không tự khóa |
| **SYNTHETIC** | Dữ liệu giả định của ví dụ; không phải số đo lab |
| **UNKNOWN** | Chưa kiểm được; không suy thành PASS hay 0 |

Contract chốt ba điều:
1. **Mỗi mốc có đúng một loại nguồn được phát.** Effect do bộ đánh giá effect, detect do detector, action do executor, recovery do bộ đánh giá probe, stop do harness. Event đúng tên nhưng sai nguồn bị loại khỏi phép đo.
2. **Bốn sự kiện tách nhau:** quyết định (trước guard), API nhận lệnh, action hoàn tất (SUCCESS/FAILED/PARTIAL/TIMEOUT sau kiểm hậu điều kiện) và RECOVERY_VERIFIED. Không trạng thái action nào tự tạo recovery.
3. **Mỗi trường thuộc một mặt dữ liệu H/O/S** và có quy tắc hiển thị riêng. Bên chữa lỗi chỉ thấy O. Không có ID, topic, path hay payload nào ở O mang nhãn case, lệnh tấn công, đáp án, canary, seed/onset hay kết quả probe.

Thiếu dữ liệu luôn được ghi là thiếu. Contract không cho phép sinh ID, sinh timestamp hoặc suy mốc để làm đủ KPI.

## 1. Phiên bản và quy tắc tương thích

**Phiên bản contract:** `1.0.0` (LOCKED). Mỗi event ghi `schema_version = "zd-event/1.0.0"`. Bản sửa 1 thêm trường bắt buộc và đổi quy tắc đồng hồ so với `0.1.0`; chưa producer nào phát `0.1.0`, nên không cần đường chuyển đổi.

| Thay đổi | Mức version | Consumer cũ |
| --- | --- | --- |
| Đổi nghĩa trường, đổi đơn vị/múi giờ, đổi giá trị enum đã có, xóa hoặc đổi tên trường, đổi nguồn được phát của một mốc, đổi mặt dữ liệu của trường | MAJOR | Phải từ chối event có MAJOR lạ; không đoán |
| Thêm event type, thêm trường tùy chọn, thêm giá trị enum mới ở trường cho phép mở rộng (`reason_code`, `error_class`) | MINOR | Bỏ qua trường lạ nhưng giữ nguyên trong raw; event type lạ lưu là UNSUPPORTED, không dùng tính KPI |
| Sửa câu chữ, ví dụ, không đổi ngữ nghĩa | PATCH | Không ảnh hưởng |

- Bản `0.x` chưa có bảo đảm tương thích. Bản đầu được khóa là `1.0.0`, sau khi Codex review và Hoàng nghiệm thu ZER-37.
- Phiên bản phép đo tách khỏi phiên bản contract. `method_version` trỏ tới bộ quy tắc chấm (ZER-32 ACC và tham số F-01) mà run dùng. `config_ref` trỏ tới manifest cấu hình run (detector, guard, prompt, executor, probe). Đổi tham số Δ, K, S, L, gap, cap không đổi `schema_version`, nhưng đổi `method_version`.
- Raw event luôn giữ version gốc. Script tái tính đọc version của từng event và từ chối tổ hợp không được hỗ trợ, không âm thầm nâng cấp.

## 2. Hiện trạng producer/consumer và chỗ cần migration

Khảo sát source ở HEAD `42af1c1`. Theo AGENTS, đã chạy `gitnexus query` trên index local (lastCommit `df5d542`; source sản phẩm không đổi từ đó tới HEAD, chỉ thêm probe R0). Graph chỉ dùng để định vị; mọi kết luận dưới đây đọc trực tiếp source. Đây là hành vi theo mã, chưa chạy runtime.

| Thành phần (file) | Hiện phát / đọc | Khác contract | Việc cần làm (issue) |
| --- | --- | --- | --- |
| Nemesis, `agent-orchestrator/nemesis/main.py` | Topic `attack.commands`: `commandId`, `timestamp`, `attackType`, `target`, `parameters`, `safetyLimits`. Endpoint `/attack/trigger` ép duration ≥ 90 s; `/attack/llm-plan` để LLM chọn case mỗi lần gọi | Không có `run_id`/`trial_id`/`incident_id`. Không có kế hoạch fault khóa trước, seed, onset hay T_stop. Nội dung lệnh thuộc H nhưng topic không có ranh giới quyền | Harness phát ATTACK_REQUESTED/ATTACK_STOPPED theo kế hoạch khóa (ZER-9 AC-02, ZER-13/14); LLM sinh kịch bản tách khỏi benchmark (ZER-8 mục 4.1) |
| chaos-worker, `chaos-worker/internal/attack/*.go`, `cmd/main.go` | Topic `attack.results`: `resultId`, `commandId`, `status` SUCCESS/FAILED/REJECTED/TIMEOUT, `duration` | Status là kết quả executor, **không phải effect**. Pod stress tên `<service>-stress-<id>`, label `app=chaos-stress`, `chaos-worker=true`, `chaos-command-id` nằm trong namespace mục tiêu, nên detector và bên quyết định nhìn thấy. Đây đúng là kênh rò ở ZER-8 mục 5.7 | FAULT_EXECUTOR_RESULT ở H. Đặt tài nguyên fault ngoài tầm truy vấn của O hoặc dùng tên/label trung tính, đăng ký trong HARNESS_MANIFEST (mục 8.3; ZER-9 AC-03, ZER-44) |
| Gaia, `agent-orchestrator/gaia/main.py` | Topic `monitoring.alerts`: `alertId`, `timestamp`, `type`, `severity`, `affectedService`, `metric`, `currentValue`, `threshold`, `description`, `suggestedAction`; `system.logs` | Không có ID run/trial. Dedup bằng cooldown 60 s trong bộ nhớ. `get_service_name` cắt hậu tố `-stress` và gán CPU của pod stress cho service | DETECTED theo mục 5. `suggestedAction` là gợi ý triệu chứng của detector: chỉ được giữ nếu giống nhau ở mọi nhóm và nằm trong phiên bản gói evidence (ZER-8 mục 4.2) |
| Hephaestus, `agent-orchestrator/hephaestus/main.py` | Đọc `monitoring.alerts` (auto-commit, `latest`). Phát `healing.actions`: `healingId`, `triggerAlertId`, `action`, `target`, `status` SUCCESS/FAILED/PARTIAL, `details`; `heal_history` trong bộ nhớ qua `/heal/history` | Quyết định nằm trong ma trận `DECISION_MATRIX`, không có bản ghi quyết định hay guard. SCALE_UP, ROLLBACK, BLOCK_IP báo SUCCESS ngay khi API Kubernetes trả về, tức là API_ACCEPTED, chưa kiểm hậu điều kiện. ROLLBACK chỉ đổi annotation. BLOCK_IP dùng `0.0.0.0` khi không có IP. Không khử trùng alert theo `alertId`; redelivery có thể tạo action lặp (cooldown chỉ giảm nhẹ). `/heal/trigger` thực thi ngay, không có bản ghi quyết định của người vận hành | Tách DECISION → GUARD_VERDICT → HEAL_STARTED → API_ACCEPTED → ACTION_COMPLETED (ZER-9 AC-02, ZER-12, ZER-16/17). MANUAL chỉ thực thi khi có quyết định của người vận hành (ZER-11) |
| Runner cũ, `infrastructure/scripts/experiment_runner*.py` | Tính MTTD/MTTR từ thời điểm xuất hiện trong `/heal/history` hoặc thời điểm publish Kafka | Trái ZER-32: detect không lấy từ heal history; recovery phải do probe xác minh | Chỉ là provenance; ZER-10 thay bằng scorer đọc raw |
| Dashboard Nemesis, `agent-orchestrator/nemesis/static/app.js` | Tính MTTR từ heal history và cộng `Math.random()` theo loại action | Số giả trình bày như kết quả | ZER-11 bỏ; dashboard đọc cùng đầu ra scorer (mục 9) |
| Kafka, `infrastructure/helm-values/kafka-values.yaml` | 5 topic, 1 partition, RF 1, retention 24 h (`system.logs` 48 h) | Không phải kho bền: raw mất sau một ngày. Thứ tự chỉ có trong từng partition, không xuyên topic | Recorder ghi raw bền và export (mục 8, ZER-9 AC-02) |
| Timestamp hiện tại | Python `isoformat()` cho micro-giây và `+00:00`; Go `RFC3339Nano` cho nano-giây và `Z` | Không đồng nhất; không ghi đồng hồ nguồn | Chuẩn hóa theo mục 4 |
| Chưa tồn tại | Harness, probe độc lập, bộ đánh giá effect/recovery, guard, recorder, scorer, kho H tách quyền | — | ZER-38 (probe), ZER-9 AC-02/03, ZER-12 (guard), ZER-10 (scorer), ZER-13/14 (tiêu chí effect) |

Contract này không tuyên bố bất kỳ thành phần nào đã tuân thủ. Mapping trên là danh sách việc cho gói sau, không phải thay đổi đã làm.

## 3. Định danh và cardinality

### 3.1 Định dạng ID (LOCK)

Mọi ID có dạng `<loại>_<32 ký tự hex của UUIDv4>`, ví dụ `inc_7c523f4b6159457d865cb5646721e217`. Loại: `run`, `trl` (trial), `inc` (incident), `evt` (event), `alt` (alert), `dec` (decision), `act` (action), `cal` (lượt gọi LLM), `ing` (bản ghi ingest của recorder).

- Phần sau dấu gạch dưới phải là UUIDv4 ngẫu nhiên. Không dùng UUIDv1/v7, ULID, số đếm, timestamp, hash của tên case hay bất kỳ giá trị nào suy được thứ tự, thời điểm tạo hoặc lớp case. ID có thời gian sẽ lộ onset; ID đếm sẽ lộ thứ tự.
- Tiền tố loại chỉ nói đây là ID gì, giống nhau ở mọi case, nên không mang thông tin đáp án.
- ID do thành phần sở hữu sinh một lần (bảng 3.2) và không bao giờ được sinh lại để vá dữ liệu thiếu.
- Định dạng đúng không chứng minh ID ngẫu nhiên. Helper ở mục 10 sinh ID dạng UUIDv4 từ hash tên case để ví dụ tái lập được; đó là dữ liệu SYNTHETIC, producer thật phải dùng bộ sinh ngẫu nhiên.

### 3.2 Ai sinh ID, cardinality

| ID | Sinh bởi | Thời điểm | Cardinality | Mặt |
| --- | --- | --- | --- | --- |
| `run_id` | Harness | Bắt đầu run | Một run có một nhóm cấu hình (B0/B1/B2/B3/BM), một `method_version`, một `config_ref`, và 1..n trial | H, O, S |
| `trial_id` | Harness | Bắt đầu trial | Thuộc đúng một run; 0..n incident (C0 không có incident thật; trial đơn case có 1; War Game có nhiều) | H, O, S |
| `incident_id` | Harness | Xem mục 3.3 | Thuộc đúng một trial; đúng một ATTACK_REQUESTED. Slot ID của trial C0 (mục 3.3) không có ATTACK_REQUESTED nên không phải incident | H, S; O có điều kiện |
| `event_id` | Producer của event | Khi tạo event, trước lần gửi đầu | Duy nhất toàn cục; giữ nguyên qua mọi lần gửi lại | Mọi mặt |
| `alert_id` | Detector | Khi rule kích hoạt | 1 DETECTED; 0..n quyết định dùng nó | O, S |
| `decision_id` | Bên quyết định | Khi tạo đề xuất | 0..1 GUARD_VERDICT cho mỗi đề xuất; 0..n action | O, S |
| `action_id` | Executor | Mỗi **lần thử** thực thi | ≤ 1 HEAL_STARTED, ≤ 1 API_ACCEPTED, ≤ 1 ACTION_COMPLETED; retry có `action_id` mới | O, S |
| `call_id` | Adapter LLM | Mỗi lần gọi provider, kể cả retry | Thuộc đúng một `decision_id` | O, S |

Khi nhóm là B0, không có `decision_id`, `action_id` hay `call_id` của ZERO DOOR (mục 7.4).

### 3.3 `incident_id` ở mặt O (LOCK)

ZER-8 mục 5.6 đặt `incident_id` ở cả H và O. Nếu harness đưa ID của incident mới vào O tại T_req, chính sự xuất hiện của ID đó báo onset cho bên chữa lỗi. Vì vậy:
- **Trial một incident:** harness cấp `incident_id` ngay khi bắt đầu trial, trước warm-up và onset jitter, và đưa vào ngữ cảnh trial ở O. **Trial C0 cũng được cấp một ID slot như vậy.** Nếu C0 không có ID, việc thiếu ID sẽ lộ lớp case. Slot của C0 không có ATTACK_REQUESTED, nên không phải incident, không vào N và không làm tăng số incident requested; H ghi slot đó không dùng.
- **Trial nhiều incident (War Game):** O không mang `incident_id`. Event O chỉ mang `run_id`, `trial_id` và chuỗi nhân quả `alert_id → decision_id → action_id`. Scorer ghép incident ở mặt S theo mục 6.3.
- Dù có `incident_id` ở O, scorer vẫn kiểm ngữ cảnh run/trial và mọi đường ghép khác theo mục 6.3. Lệch là LINK_CONFLICT, incident thành MISSING.

## 4. Thời gian và đồng hồ

### 4.1 Định dạng

Mọi timestamp là chuỗi UTC dạng `YYYY-MM-DDTHH:MM:SS.mmmZ`, cắt (floor) về mili-giây. Không ghi `+00:00`, micro-giây hay giờ địa phương. Báo cáo hiển thị +07:00 (ACC ZER-32 mục 3.1).

**Mili-giây là định dạng lưu, không phải độ chính xác.** Độ chính xác thật phụ thuộc đồng hồ nguồn: độ phân giải, độ lệch và chu kỳ lấy mẫu. Ví dụ, trên máy Windows dùng ở R0, `time.time` và `time.monotonic` của Python có bước khoảng 15,625 ms ([review ZER-36](../evidence/ZER-36/claude-review.md)). Vì vậy mỗi event ghi đồng hồ nguồn (mục 4.3), và kết quả thời gian báo kèm Δ, độ phân giải và sai số.

### 4.2 Các loại thời gian

| Trường | Do ai ghi | Nghĩa | Dùng cho |
| --- | --- | --- | --- |
| `ts_event` | Producer, theo đồng hồ của nó | Thời điểm producer xác lập sự việc của event (bảng 5.2 nói rõ cho từng loại) | Sắp xếp và tính mốc khi bảng 5.2 nói mốc = `ts_event` |
| Trường mốc trong payload, ví dụ `t_eff`, `t_rec`, `recovery_verified_at` | Bộ đánh giá | Thời điểm của mẫu bằng chứng, có thể sớm hơn lúc phát event nhiều | Mốc KPI khi bảng 5.2 trỏ tới |
| `ts_publish` | Producer, ngay trước lần gửi đầu (tùy chọn) | T_pub của ZER-32 | Phân rã độ trễ transport |
| `ts_ingest` | **Recorder**, lúc ghi bền | Thời điểm hệ thống lưu nhận | Kiểm độ trễ lưu, trạng thái muộn; **không bao giờ** là mốc KPI |

- T_con (consumer nhận) được ghi trong event của chính consumer: `DECISION.payload.inputs[].received_at`.
- Thiếu `ts_event` hoặc trường mốc thì mốc đó MISSING. Không suy từ `ts_ingest`, thứ tự nhận, offset Kafka hay thời điểm của event khác (ACC ZER-32 mục 4).

**Đồng hồ sở hữu từng timestamp (sửa RV37-03).** `ts_event`, `ts_publish` và mọi timestamp trong payload thuộc đồng hồ ghi ở `clock` của envelope, trừ hai trường hợp:
- Payload có `evidence_clock_id` (EFFECT_EVALUATED, RECOVERY_VERIFIED): các mốc trong payload thuộc đồng hồ đó, tức đồng hồ của probe đã tạo mẫu bằng chứng.
- `CLOCK_SYNC.payload.measured_at` thuộc đồng hồ tham chiếu.

Ví dụ: `DECISION.inputs[].received_at` thuộc đồng hồ của bên quyết định; `PROBE_SAMPLE.t_start`/`t_end` thuộc đồng hồ của probe.

### 4.3 Danh tính và chất lượng đồng hồ

Mỗi event có object `clock`:

| Trường | Kiểu | Nghĩa |
| --- | --- | --- |
| `clock_id` | chuỗi trung tính | Đồng hồ vật lý/tiến trình đã tạo `ts_event`, ví dụ `clk_host_lab` |
| `clock_source` | enum `HOST_SHARED`, `OFF_HOST`, `UNKNOWN` | `HOST_SHARED`: container trong k3d dùng chung đồng hồ kernel của Docker host (ACC ZER-32 mục 3.1). `OFF_HOST`: probe hoặc harness chạy ngoài host đó |
| `resolution_ms` | số hoặc null | Bước nhỏ nhất của đồng hồ đã biết; null là UNKNOWN |

**Đồng hồ tham chiếu và chuẩn hóa (LOCK, sửa RV37-03).**
- RUN_STARTED ghi `reference_clock_id`, là đồng hồ của Docker host. Đồng hồ `HOST_SHARED` dùng chung kernel với host nên được coi là đồng hồ tham chiếu, offset 0 (ACC ZER-32 mục 3.1).
- Đồng hồ khác (`OFF_HOST`, `UNKNOWN`) chỉ được so với đồng hồ khác sau khi chuẩn hóa bằng event CLOCK_SYNC (H). Trường: `clock_id`, `reference_clock_id`, `offset_ms` (đồng hồ này trừ đồng hồ tham chiếu), `uncertainty_ms`, `method`, `measured_at` (theo đồng hồ tham chiếu). Cách đo thuộc ZER-38 (OPEN).
- **Phủ trial.** Đồng hồ được xác minh cho một trial khi đủ bốn điều kiện: có CLOCK_SYNC cùng `trial_id` với `measured_at` ≤ thời điểm TRIAL_STARTED; có CLOCK_SYNC với `measured_at` ≥ thời điểm TRIAL_ENDED; mọi lần đo có `uncertainty_ms`; `clock.resolution_ms` đã biết. Hai lần đo chỉ bao quanh T_req là chưa đủ.
- **Chuẩn hóa.** `t_ref = t_local − offset(t_local)`. Offset được nội suy tuyến tính giữa các lần đo, trên trục của chính đồng hồ đó (`measured_at + offset_ms`). Ngoài khoảng đo thì dùng lần đo gần nhất. Cách này bù được trôi tuyến tính. Đây là quy tắc cho ví dụ, không khóa phương pháp đo của F-01.
- **Sai số.** Mốc đã chuẩn hóa có sai số bằng `uncertainty_ms` lớn nhất của các lần đo cộng `resolution_ms`. Mốc của đồng hồ tham chiếu có sai số bằng `resolution_ms`. Duration giữa hai đồng hồ có sai số bằng tổng sai số hai đầu. Duration trong cùng một đồng hồ không phụ thuộc offset; sai số bằng 2 × `resolution_ms`. Kết quả báo sai số cạnh giá trị. Contract không đặt ngưỡng sai số chấp nhận (F-01, ZER-38).
- **Quy tắc chạy trên đồng hồ nguồn.** D-04 (K, S, gap, cap_rec) chạy trên số đọc của đồng hồ probe; chỉ các mốc kết quả được chuẩn hóa. Sắp xếp, cửa sổ ghép và so sánh giữa các thành phần dùng giá trị đã chuẩn hóa.

**Quy tắc thời gian giữ theo ACC ZER-32**, áp dụng sau chuẩn hóa:
- INVALID_CLOCK: chuỗi T_det ≤ T_pub ≤ T_con ≤ T_hs và T_api ≤ T_ac vi phạm quá ε. Mọi duration của incident thành MISSING.
- EARLY_DETECT: T_req − ε ≤ T_det < T_eff thì MTTD = 0 có cờ.
- Dấu `<` của ngưỡng là nghiêm ngặt.

**CLOCK_UNVERIFIED (LOCK).** Đồng hồ không đủ điều kiện phủ trial ở trên thì:
- Mọi duration và phép so sánh **xuyên** đồng hồ đó là MISSING, cờ CLOCK_UNVERIFIED. Với probe OFF_HOST, đó là MTTD (T_eff của probe so với T_det của host), MTTR, thứ tự T_rec/T_det và so `recovery_verified_at` với T_stop.
- Duration **trong cùng** một đồng hồ vẫn tính và báo: total recovery (T_rec − T_eff, cùng đồng hồ probe) và reaction (T_ac − T_det, cùng host).
- Nhãn phục hồi cần so xuyên đồng hồ nên là MISSING.
- Không suy offset, không thay offset bằng 0.

Đây là cách áp dụng bảo thủ yêu cầu “phải ghi độ lệch” của ZER-32 mục 3.1, không phải ngưỡng mới. Thay đổi quy tắc này sau khóa phải qua review, nghiệm thu và version theo mục 1.

Contract không đặt giá trị ε, Δ hay ngưỡng sai số. Các giá trị đó là tham số F-01, khóa trong protocol ZER-53. Ví dụ ở mục 10 dùng bộ minh họa của ZER-32 mục 3.6.

## 5. Envelope

### 5.1 Trường chung

| Trường | Kiểu | Bắt buộc | Ai đặt | Ghi chú |
| --- | --- | --- | --- | --- |
| `schema_version` | chuỗi | Có | Producer | `zd-event/1.0.0` |
| `event_id` | ID `evt_` | Có | Producer | Giữ nguyên khi gửi lại; xem mục 6.1 |
| `event_type` | enum (mục 5.2) | Có | Producer | Quyết định mặt dữ liệu và nguồn được phát |
| `plane` | `H`, `O`, `S` | Có | Producer | Phải khớp bảng 5.2 |
| `run_id` | ID `run_` | Có | Lấy từ ngữ cảnh run | Không có thì event là ORPHAN |
| `trial_id` | ID `trl_` hoặc null | Theo loại | Lấy từ ngữ cảnh trial | Null chỉ với event cấp run |
| `incident_id` | ID `inc_`, null hoặc vắng | Theo loại và mục 3.3 | Harness cấp | Không bao giờ do consumer đoán |
| `alert_id`, `decision_id`, `action_id`, `call_id` | ID hoặc vắng | Theo loại | Thành phần sở hữu (bảng 3.2) | — |
| `causation_id` | `event_id` hoặc null | Theo loại | Producer | Event trực tiếp gây ra event này; null khi là gốc |
| `group` | `B0`, `B1`, `B2`, `B3`, `BM` | Có | Ngữ cảnh run | Phải khớp manifest run |
| `method_version` | chuỗi | Có | Ngữ cảnh run | Bộ quy tắc chấm và tham số F-01 |
| `config_ref` | chuỗi `sha256:…` | Có | Ngữ cảnh run | Hash manifest cấu hình run |
| `source_component` | enum (mục 5.2) | Có | Producer | Kiểm theo bảng quyền phát |
| `source_instance` | chuỗi trung tính | Có | Producer | Tiến trình cụ thể, ví dụ `det-0`; không chứa tên case/vector |
| `producer_version` | chuỗi | Có | Producer | Digest image hoặc revision |
| `stream` | chuỗi trung tính | Có | Producer | Luồng logic: `h.control`, `h.eval`, `h.probe`, `h.audit`, `o.context`, `o.alert`, `o.decision`, `o.action`, `s.score` |
| `seq` | số nguyên ≥ 0 | Có | Producer | Tăng liên tục theo `(source_instance, stream)`; dùng phát hiện mất event và giữ thứ tự nguồn |
| `target` | object hoặc null | Theo loại | Producer | `namespace`, `service`, `flow`; chỉ mục tiêu quan sát được, không ghi lớp case |
| `clock` | object (mục 4.3) | Có | Producer | — |
| `ts_event` | timestamp | Có | Producer | Thiếu thì event sai schema; mốc của nó là MISSING |
| `ts_publish` | timestamp | Tùy chọn | Producer | T_pub |
| `payload` | object | Có | Producer | Theo loại (mục 5.3) |

Recorder bọc mỗi lần nhận vào một **bản ghi ingest**, không sửa envelope:

| Trường | Nghĩa |
| --- | --- |
| `ingest_id` | ID ngẫu nhiên của lần nhận |
| `ts_ingest` | Thời điểm ghi bền theo đồng hồ recorder |
| `transport` | Object: `kind` là `kafka`, `http` hoặc `file`; với Kafka thêm `topic`, `partition`, `offset`; với HTTP thêm request ID |
| `envelope_sha256` | Hash JSON chuẩn hóa (khóa sắp xếp, không khoảng trắng, UTF-8) của envelope |
| `envelope` | Envelope nguyên văn |

### 5.2 Loại event, nguồn được phát và mốc

`ts_event` của event phát sau sự việc (đánh giá, xác minh) là lúc phát. Khi đó mốc KPI nằm trong payload. Cột “Mốc ZER-32” chỉ ra trường nào là mốc.

| `event_type` | Mặt | `source_component` được phát | `incident_id` | ID khác bắt buộc | Mốc ZER-32 |
| --- | --- | --- | --- | --- | --- |
| RUN_STARTED, RUN_CLOSED | H | `harness` | Vắng | — | — |
| RUN_CONTEXT | O | `harness` | Vắng | — | Ngữ cảnh run cho thành phần O: `group`, `config_ref`, `method_version`; không có nhãn |
| TRIAL_STARTED, TRIAL_ENDED | H | `harness` | Vắng | `trial_id` | Ranh giới trial; warm-up ghi trong payload |
| TRIAL_CONTEXT | O | `harness` | Có ở trial một incident, vắng ở War Game (mục 3.3) | `trial_id` | — |
| HARNESS_MANIFEST | H | `harness` | Vắng | `trial_id` | Giá trị do harness tạo có thể xuất hiện ở O (mục 8.3) |
| GROUND_TRUTH_LOCKED | H | `harness` | Vắng (khóa theo variant) | — | — |
| SCHEDULE_SEALED | H | `harness` | Vắng | — | Hash lịch trial và thời điểm niêm phong |
| SCHEDULE_ACCESS | H | `harness` (audit kho H) | Vắng | `trial_id` của phần lịch được xem | — |
| AUDIT_COVERAGE | H | `harness` | Vắng | — | Khoảng thời gian audit kho H có hiệu lực |
| CLOCK_SYNC | H | `harness`, `probe` | Vắng | `trial_id` | — |
| ATTACK_REQUESTED | H | `harness` | Có | `trial_id` | T_req = `ts_event` |
| FAULT_EXECUTOR_RESULT | H | `fault_executor` | Có | `trial_id` | Không phải mốc; kết quả executor ≠ effect |
| ATTACK_STOPPED | H | `harness` | Có | `trial_id` | T_stop = `ts_event` |
| EFFECT_EVALUATED | H | `effect_evaluator` | Có | `trial_id` | T_eff = `payload.t_eff` khi CONFIRMED |
| PROBE_SAMPLE | H | `probe` | Vắng | `trial_id` hoặc null ngoài trial | Mẫu probe; thời điểm mẫu = `payload.t_start` |
| PROBE_HEARTBEAT | H | `probe` | Vắng | — | Phân biệt probe chết với dịch vụ lỗi |
| RELAPSE | H | `recovery_evaluator` | Có | `trial_id` | Hủy ứng viên `payload.candidate_t_rec` |
| RECOVERY_VERIFIED | H | `recovery_evaluator` | Có | `trial_id` | T_rec = `payload.t_rec`; `recovery_verified_at` và `evidence_complete_at` không phải mốc KPI (mục 7.5) |
| CONTAINMENT_VERIFIED | H | `recovery_evaluator` | Có | `trial_id` | Containment SQLi; tách khỏi availability Boutique |
| DETECTED | O | `detector` | Theo mục 3.3 | `alert_id` | T_det = `ts_event` |
| DECISION | O | `decision_rules`, `decision_llm`, `decision_single_llm`, `operator_console` | Theo mục 3.3 | `decision_id` | Quyết định trước guard; T_con = `payload.inputs[].received_at` |
| LLM_CALL | O | `decision_llm`, `decision_single_llm` | Theo mục 3.3 | `decision_id`, `call_id` | — |
| GUARD_VERDICT | O | `guard` | Theo mục 3.3 | `decision_id` | — |
| HEAL_STARTED | O | `executor` | Theo mục 3.3 | `decision_id`, `action_id` | T_hs = `ts_event` |
| API_ACCEPTED | O | `executor` | Theo mục 3.3 | `action_id`; `decision_id` tùy chọn, nếu có phải khớp HEAL_STARTED | T_api = `ts_event` |
| ACTION_COMPLETED | O | `executor` | Theo mục 3.3 | `action_id`; `decision_id` như API_ACCEPTED | T_ac = `ts_event`; `payload.status` |
| INCIDENT_LINK, INCIDENT_SCORE, LEAK_CHECK | S | `scorer` | Có (INCIDENT_LINK, INCIDENT_SCORE) | — | Kết quả chấm sau trial |

Hai mốc `attack_effect_started` và `effect_evaluation` của ZER-32 mục 3.3 gộp trong EFFECT_EVALUATED: record CONFIRMED mang T_eff. `published`/`consumed` không thành event riêng mà là `ts_publish` của producer và `received_at` của consumer.

Event hợp lệ về schema nhưng `source_component` không thuộc cột “được phát” là **SOURCE_VIOLATION**: lưu, không dùng cho mốc. Ví dụ: RECOVERY_VERIFIED do `executor` phát, hoặc DETECTED dựng từ heal history.

### 5.3 Payload bắt buộc

| `event_type` | Trường payload bắt buộc (khác null trừ khi ghi “nullable”) |
| --- | --- |
| RUN_STARTED | `canary_token`, `protocol_ref`, `schedule_ref` (hash, không phải lịch), `f01_params` (Δ, K, S, L, gap, ε, cap_det, cap_rec), `reference_clock_id` |
| RUN_CLOSED | `close_reason` (`COMPLETED`, `ABORTED`), `recorder_manifest_ref` (nullable) |
| RUN_CONTEXT | Object rỗng `{}`. `group`, `config_ref`, `method_version` nằm ở envelope; không thêm nhãn |
| TRIAL_STARTED | `warmup_end` (nullable khi chưa đạt), `planned_window`, `probes` (danh sách `{probe_id, flow, probe_version, clock_id}` đăng ký cho trial) |
| TRIAL_ENDED | `end_reason` (`PLANNED`, `HORIZON`, `ABORTED`) |
| TRIAL_CONTEXT | Object rỗng `{}`; `incident_id` theo mục 3.3 nằm ở envelope. Trường thêm vào đây vẫn chịu kiểm rò mục 8.3 |
| HARNESS_MANIFEST | `manifest_version`, `allowlist_version`, `reveal_terms`, `entries` (mục 8.3) |
| CLOCK_SYNC | Các trường ở mục 4.3. `uncertainty_ms` nullable, nhưng null làm đồng hồ CLOCK_UNVERIFIED |
| GROUND_TRUTH_LOCKED | `variant_id`, `case_class`, `cause`, `decision_required`, `acceptable_actions`, `constraints`, `label_version`, `reviewers`, `locked_at` |
| SCHEDULE_SEALED | `schedule_sha256`, `sealed_at`, `generated_after_label_lock` (bool) |
| SCHEDULE_ACCESS | `actor_role` (`EVALUATOR`, `OPERATOR`, `HARNESS`), `scope_trial_ids`, `accessed_at` |
| AUDIT_COVERAGE | `from`, `to`, `complete` (bool) |
| ATTACK_REQUESTED | `variant_ref` (khóa tới GROUND_TRUTH_LOCKED), `fault_params`, `attack_command`, `seed`, `onset_offset_ms`, `s_att` (nullable), `known_good_revision` (nullable), `target_services` |
| FAULT_EXECUTOR_RESULT | `executor_status` (`SUCCESS`, `FAILED`, `REJECTED`, `TIMEOUT`), `command_ref`, `duration_ms` (nullable) |
| ATTACK_STOPPED | `stop_reason` (`PLANNED`, `HORIZON`, `ABORTED`, `EXECUTOR_ENDED`), `executor_confirmed` (bool) |
| EFFECT_EVALUATED | `status` (`CONFIRMED`, `CONFIRMED_NO_EFFECT`, `UNKNOWN_EFFECT`), `t_eff` (nullable, chỉ có khi CONFIRMED), `evidence_clock_id`, `criteria_version`, `w_eff_s`, `evidence` (`flow`; `first_sample_t`, `last_sample_t`, `max_gap_s`, `sample_seq_range` nullable), `reason` |
| PROBE_SAMPLE | `probe_id`, `flow`, `sequence`, `t_start`, `t_end`, `pass` (bool), `error_class` (nullable: `TIMEOUT`, `CONNECT`, `CONTENT`, `SLOW`), `latency_ms`, `probe_version`. Chi tiết từng bước do ZER-38 bổ sung (MINOR) |
| PROBE_HEARTBEAT | `probe_id`, `flow`, `last_sequence` (nullable), `probe_version` |
| RELAPSE | `flow`, `candidate_t_rec`, `failing_sample_t`, `rule_version` |
| RECOVERY_VERIFIED | `flow`, `probe_id`, `probe_version`, `evidence_clock_id`, `t_rec`, `recovery_verified_at`, `evidence_complete_at`, `k`, `s_s`, `delta_s`, `l_ms`, `gap_s`, `cap_rec_s`, `sample_seq_range` (`[sequence đầu, sequence cuối]`), `samples_sha256`, `rule_version` (mục 7.5) |
| CONTAINMENT_VERIFIED | `blocked_source_ref` (tham chiếu H), `enforcement_point`, `fixture_probe_ref`, `boutique_probe_ref`, `t_contained` |
| DETECTED | `rule_id`, `rule_version`, `signature`, `metric`, `value`, `threshold`, `severity`, `description` (chỉ triệu chứng) |
| DECISION | `stage` (`ANALYSIS`, `PROPOSAL`), `decision_source` (`RULES`, `LLM`, `SINGLE_LLM`, `MANUAL`), `inputs` (danh sách `{event_id, received_at}`), `response_kind` (`ACTION`, `NO_ACTION`, `ABSTAIN`, `SCHEMA_INVALID`, `TIMEOUT`, `REFUSAL`), `proposal` (nullable: `action_type`, `params`), `fallback` (bool), `fallback_of` (nullable `decision_id`), `prompt_version` và `prompt_sha256` (null nếu không dùng LLM), `evidence_package_version` |
| LLM_CALL | `attempt_no`, `retry_reason` (nullable), `provider`, `model`, `prompt_version`, `prompt_sha256`, `latency_ms`, `outcome` (`OK`, `TIMEOUT`, `HTTP_ERROR`, `SCHEMA_INVALID`, `REFUSAL`), `usage` (`input_tokens`, `output_tokens`, `status`: `COMPLETE`, `MISSING`, `NOT_APPLICABLE`), `cost` (`usd` nullable, `status`, `price_ref`) |
| GUARD_VERDICT | `verdict` (`ACCEPT`, `REJECT`), `reason_code`, `guard_version` |
| HEAL_STARTED | `action_type`, `params`, `attempt_no`, `retry_of` (nullable `action_id`), `initiator` (`AUTO`, `OPERATOR`) |
| API_ACCEPTED | `api`, `response_ref` |
| ACTION_COMPLETED | `status` (`SUCCESS`, `FAILED`, `PARTIAL`, `TIMEOUT`), `postcondition` (`name`, `checked`, `satisfied`, `observed`), `error` (nullable) |
| INCIDENT_LINK | `links` (danh sách `{event_id, method, flags}`), `ambiguous` (bool) |
| INCIDENT_SCORE | Nhãn và giá trị theo ZER-32/ZER-8 (mục 7), `scorer_version`, `input_manifest_sha256`, `cutoff` |
| LEAK_CHECK | `result` (`CLEAN`, `LEAK_DETECTED`, `UNKNOWN`), `findings` |

Trường không có trong bảng được phép thêm theo quy tắc MINOR; consumer giữ nguyên trong raw. Thiếu trường bắt buộc không bao giờ được consumer tự đoán.

**Ràng buộc liên trường (sửa RV37-04).** Event đủ trường nhưng vi phạm một ràng buộc dưới đây là INVALID:
- `ACTION_COMPLETED.status = SUCCESS` khi và chỉ khi `postcondition.checked = true` và `satisfied = true`. Status khác mà hậu điều kiện đã thỏa cũng là mâu thuẫn. Ví dụ hậu điều kiện: replica Ready đạt số mong muốn; digest image/config đúng known-good; policy có hiệu lực tại điểm thực thi. API trả 2xx chỉ tạo API_ACCEPTED.
- Executor tự đặt hạn chờ hậu điều kiện. Hết hạn thì phát ACTION_COMPLETED `TIMEOUT`. Không có ACTION_COMPLETED hợp lệ thì action là **ACTION_TERMINAL_MISSING**, không phải TIMEOUT.
- PROBE_SAMPLE: `pass = true` khi và chỉ khi `error_class = null`; mẫu đạt phải có `latency_ms` ≤ L của run (`f01_params`); `t_end` ≥ `t_start`.
- EFFECT_EVALUATED: `t_eff` khác null khi và chỉ khi `status = CONFIRMED`.
- DECISION: `decision_source` khớp `source_component` (RULES – `decision_rules`, LLM – `decision_llm`, SINGLE_LLM – `decision_single_llm`, MANUAL – `operator_console`). `proposal` khác null khi và chỉ khi `response_kind = ACTION`. `fallback = true` khi và chỉ khi có `fallback_of`, và chỉ với RULES. Quyết định LLM/SINGLE_LLM phải có `prompt_sha256`. Mỗi phần tử `inputs` có `event_id` và `received_at`.
- HEAL_STARTED: `attempt_no` > 1 khi và chỉ khi có `retry_of`. LLM_CALL: `attempt_no` > 1 khi và chỉ khi có `retry_reason`.
- RELAPSE: `failing_sample_t` sau `candidate_t_rec`. AUDIT_COVERAGE: `to` ≥ `from`.
- RECOVERY_VERIFIED: các ràng buộc ở mục 7.5.
- Im lặng không phải NO_ACTION. NO_ACTION/ABSTAIN chỉ có khi bên quyết định phát DECISION với `response_kind` tương ứng (ACC ZER-8 mục 5.3).

**Phân loại lỗi.** Phép kiểm event phải trả một loại lỗi cụ thể; không im lặng cho qua, không dừng giữa chừng vì payload sai dạng:

| Loại | Nghĩa | Xử lý |
| --- | --- | --- |
| MISSING_FIELD | Thiếu trường envelope, ID bắt buộc theo bảng 5.2 hoặc trường payload theo bảng 5.3 | Event INVALID (mục 6.4) |
| INVALID | Sai kiểu, sai enum, sai định dạng ID/timestamp, payload không phải object | Event INVALID (mục 6.4) |
| SEMANTIC | Đủ trường nhưng vi phạm ràng buộc liên trường | Event INVALID (mục 6.4) |
| SOURCE_VIOLATION | Nguồn không thuộc cột “được phát” của bảng 5.2 | Lưu, không dùng |
| MODE_VIOLATION | Event hợp lệ nhưng trái ràng buộc của nhóm (mục 7.4) | Trial không dùng làm nhóm đó |
| LINK_CONFLICT, ORPHAN, UNSCOPED | Ghép mâu thuẫn hoặc không ghép được (mục 6.3) | Theo mục 6.3 |

### 5.4 Ví dụ envelope (SYNTHETIC)

Một DETECTED và một ACTION_COMPLETED của trace E01 ở mục 10. Mọi ID là UUIDv4 ngẫu nhiên.

```json
[
  {
    "schema_version": "zd-event/1.0.0",
    "event_id": "evt_18a5c5d9dbd64c6d91646cb615f3e337",
    "event_type": "DETECTED",
    "plane": "O",
    "run_id": "run_df92aea8b2464ce394b989e50400dfbe",
    "trial_id": "trl_91737ae5dd084a49843e048f3c3af88b",
    "incident_id": "inc_f357cc98b68e436b8dfe28bbe34f429c",
    "alert_id": "alt_359eb0a2c3a74270befaf7a209def455",
    "causation_id": null,
    "group": "B2",
    "method_version": "zer32-acc+f01-illustrative",
    "config_ref": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "source_component": "detector",
    "source_instance": "det-0",
    "producer_version": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "stream": "o.alert",
    "seq": 17,
    "target": {"namespace": "target-app", "service": "frontend", "flow": null},
    "clock": {"clock_id": "clk_host_lab", "clock_source": "HOST_SHARED", "resolution_ms": 1},
    "ts_event": "2026-10-19T06:02:11.000Z",
    "ts_publish": "2026-10-19T06:02:11.200Z",
    "payload": {
      "rule_id": "cpu_limit_ratio",
      "rule_version": "r1",
      "signature": "cpu_limit_ratio/frontend",
      "metric": "cpu_usage_ratio_of_limit",
      "value": 0.93,
      "threshold": 0.8,
      "severity": "WARNING",
      "description": "CPU usage of frontend is 93% of its limit."
    }
  },
  {
    "schema_version": "zd-event/1.0.0",
    "event_id": "evt_229b206c673e47dfba0acd618ce76a0c",
    "event_type": "ACTION_COMPLETED",
    "plane": "O",
    "run_id": "run_df92aea8b2464ce394b989e50400dfbe",
    "trial_id": "trl_91737ae5dd084a49843e048f3c3af88b",
    "incident_id": "inc_f357cc98b68e436b8dfe28bbe34f429c",
    "decision_id": "dec_ffd74eb7183d44218543d9b697d20db7",
    "action_id": "act_ce4bdf8c2f584184a6fc8e95633a2f7a",
    "causation_id": "evt_f2f542de650141829bfed4b0383162ef",
    "group": "B2",
    "method_version": "zer32-acc+f01-illustrative",
    "config_ref": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "source_component": "executor",
    "source_instance": "exec-0",
    "producer_version": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
    "stream": "o.action",
    "seq": 5,
    "target": {"namespace": "target-app", "service": "frontend", "flow": null},
    "clock": {"clock_id": "clk_host_lab", "clock_source": "HOST_SHARED", "resolution_ms": 1},
    "ts_event": "2026-10-19T06:02:30.000Z",
    "payload": {
      "status": "SUCCESS",
      "postcondition": {"name": "replicas_ready", "checked": true, "satisfied": true, "observed": "2/2 Ready"},
      "error": null
    }
  }
]
```

Bản ghi ingest của RECOVERY_VERIFIED trong E01, nhận muộn 68 s sau `ts_event`. T_rec vẫn là `payload.t_rec`:

```json
{
  "ingest_id": "ing_e76f37b3c7cd4bc59beb98e7ac9febfd",
  "ts_ingest": "2026-10-19T06:04:50.000Z",
  "transport": {"kind": "kafka", "topic": "zd.h.eval.v0", "partition": 0, "offset": 412},
  "envelope_sha256": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
  "envelope": {
    "schema_version": "zd-event/1.0.0",
    "event_id": "evt_4f302b44ce6a4d07ad0a5df48bb12e4d",
    "event_type": "RECOVERY_VERIFIED",
    "plane": "H",
    "run_id": "run_df92aea8b2464ce394b989e50400dfbe",
    "trial_id": "trl_91737ae5dd084a49843e048f3c3af88b",
    "incident_id": "inc_f357cc98b68e436b8dfe28bbe34f429c",
    "causation_id": null,
    "group": "B2",
    "method_version": "zer32-acc+f01-illustrative",
    "config_ref": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "source_component": "recovery_evaluator",
    "source_instance": "rec-0",
    "producer_version": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
    "stream": "h.eval",
    "seq": 3,
    "target": {"namespace": "target-app", "service": "frontend", "flow": "checkout"},
    "clock": {"clock_id": "clk_probe_ext", "clock_source": "OFF_HOST", "resolution_ms": 16},
    "ts_event": "2026-10-19T06:03:42.000Z",
    "payload": {
      "flow": "checkout",
      "probe_id": "prb-0",
      "probe_version": "p0",
      "evidence_clock_id": "clk_probe_ext",
      "t_rec": "2026-10-19T06:03:11.000Z",
      "recovery_verified_at": "2026-10-19T06:03:41.000Z",
      "evidence_complete_at": "2026-10-19T06:03:41.250Z",
      "k": 3,
      "s_s": 30,
      "delta_s": 1,
      "l_ms": 2000,
      "gap_s": 2,
      "cap_rec_s": 600,
      "sample_seq_range": [189, 221],
      "samples_sha256": "sha256:5555555555555555555555555555555555555555555555555555555555555555",
      "rule_version": "zer32-d04"
    }
  }
}
```

`envelope_sha256`, `config_ref`, `producer_version` và `samples_sha256` trong ví dụ là giá trị giữ chỗ, không phải hash thật. Mẫu thứ 221 bắt đầu lúc 06:03:41.000Z và kết thúc lúc 06:03:41.250Z, nên event phát lúc 06:03:42.000Z là hợp lệ; phát lúc 06:03:41.000Z là quá sớm (mục 7.5).

## 6. Ghép, khử trùng, thứ tự và dữ liệu lỗi

### 6.1 Gửi lại khác thử lại

| Tình huống | Nhận biết | Xử lý |
| --- | --- | --- |
| Redelivery (Kafka giao lại, producer gửi lại do timeout ack) | Cùng `event_id`, cùng `envelope_sha256` | Giữ bản ingest đầu, đếm bản trùng; không tạo action hay mốc mới |
| Xung đột | Cùng `event_id`, khác `envelope_sha256` | INTEGRITY_ERROR: lưu tất cả bản; incident liên quan thành MISSING (ACC ZER-32 mục 4) |
| Retry thật của action | `action_id` mới, `attempt_no` tăng, `retry_of` trỏ `action_id` trước | Lưu mọi lần thử. Reaction dùng SUCCESS đầu tiên; MTTR không phụ thuộc số action (ACC) |
| Retry thật của lượt gọi LLM | `call_id` mới cùng `decision_id`, `attempt_no` tăng | Mọi lượt vào usage/cost; M1 giữ kết quả của attempt đầu trong hạn (ACC ZER-8 mục 5.3) |
| Consumer xử lý lại cùng alert | Hai DECISION có cùng `inputs[].event_id` | Lưu cả hai; quyết định đầu theo `ts_event` vào M1, các quyết định sau là hành động tiếp theo |

Consumer phải idempotent theo `event_id` của input: một alert giao lại không được tạo thêm action. Hiện Hephaestus chưa làm được việc này (mục 2).

### 6.2 Thứ tự

- Mốc và duration tính theo `ts_event` hoặc trường mốc đã hiệu chỉnh đồng hồ, không theo thứ tự nhận, `ts_ingest` hay offset Kafka.
- Thứ tự trong cùng nguồn dùng `seq` theo `(source_instance, stream)`. Hai event cùng nguồn có `ts_event` ngược với `seq` là CLOCK_REGRESSION của nguồn đó, ghi cờ cho incident.
- Không có thứ tự tổng xuyên thành phần. Hai event khác đồng hồ chỉ so được trong sai số ở mục 4.3.
- Lỗ hổng `seq` là bằng chứng mất event. Ghi SEQ_GAP với khoảng bị mất, không điền.
- Scorer chạy sau khi trial kết thúc và chờ thêm `ingest_grace` do protocol khóa (OPEN, ZER-10/ZER-53). Mỗi lần chấm ghi `cutoff`. Event có `ts_ingest` sau cutoff là LATE_INGEST: không lặng lẽ bỏ, phải chấm lại với version chấm mới nếu dùng.

### 6.3 Ghép event vào incident

**Phạm vi run (sửa RV37-05).** Scorer chấm từng run. Event không có `run_id` là **UNSCOPED**: lưu, đếm và báo ở cấp kho, nhưng không gán vào run nào theo thời gian và không đổi nhãn của run nào, kể cả khi trùng cửa sổ. Event có `run_id` khác thuộc run của nó. Nếu event của run khác mang `incident_id` hoặc `trial_id` của run đang chấm thì đó là LINK_CONFLICT cho các incident liên quan.

Trong một run có ba đường ghép:
1. **ID tường minh:** `incident_id` có trong event. `incident_id` không tồn tại trong run thì event là ORPHAN.
2. **Chuỗi nhân quả:**
   - DECISION ghép qua `inputs[].event_id` của DETECTED đã ghép.
   - LLM_CALL, GUARD_VERDICT, HEAL_STARTED ghép qua `decision_id`.
   - API_ACCEPTED và ACTION_COMPLETED ghép qua bản đồ `action_id → incident` lập từ HEAL_STARTED, kể cả khi event thiếu `decision_id` (ACC ZER-32: “liên kết được qua action_id”), và qua `decision_id` nếu có.
   - Mọi event ghép qua `causation_id` khi nó trỏ tới event đã ghép.
3. **Quy tắc cửa sổ của scorer (LOCK, chỉ cho DETECTED không có đường 1–2):** ứng viên là các incident cùng `trial_id` có T_req − ε ≤ `ts_event` ≤ T_eff + cap_det (hoặc T_req + W_eff + cap_det khi chưa có T_eff). Nhiều ứng viên thì lọc theo service mục tiêu; còn khác một là AMBIGUOUS, các incident liên quan thành MISSING (ACC ZER-32 mục 4, incident chồng lấn).

**Bất biến ngữ cảnh.** ID tường minh không được tin hơn các đường còn lại:
- Mọi đường có được phải chỉ về cùng một incident.
- `trial_id` của event, nếu có, phải bằng trial của incident đó; event H có `incident_id` cũng vậy.
- `decision_id` trên API_ACCEPTED/ACTION_COMPLETED, nếu có, phải bằng `decision_id` của HEAL_STARTED cùng `action_id`.

Vi phạm là **LINK_CONFLICT**: event bị cách ly (lưu, không dùng), mọi incident liên quan thành MISSING. Không sửa ID để cứu số liệu.

**Service lệch mục tiêu.** DETECTED ghép được qua đường 1 hoặc 3 nhưng `target.service` không thuộc tập service mục tiêu ở H thì gắn cờ TARGET_MISMATCH và **không** được tính là detect bình thường, vì quy tắc nhận alert lệch service còn OPEN (ZER-10/ZER-53). Incident không còn DETECTED đúng service nào là MISSING với cờ TARGET_MISMATCH, không phải MISSED.

Event không ghép được theo 1–3 là **ORPHAN**: lưu, không dùng. Nếu trong cửa sổ của incident, cùng trial hoặc không ghi trial, có ORPHAN thuộc loại mốc bắt buộc (DETECTED, ACTION_COMPLETED, EFFECT_EVALUATED), incident thành MISSING, không phải MISSED (ACC ZER-32 mục 4: thiếu mốc vì thiếu correlation thì MISSING).

### 6.4 Event không hợp lệ

- Event INVALID (MISSING_FIELD, INVALID, SEMANTIC ở mục 5.3) được lưu nguyên văn, không dùng cho mốc.
- Event INVALID thuộc loại mốc bắt buộc (ATTACK_REQUESTED, ATTACK_STOPPED, EFFECT_EVALUATED, PROBE_SAMPLE, DETECTED, DECISION, HEAL_STARTED, API_ACCEPTED, ACTION_COMPLETED) làm incident liên quan thành MISSING, cờ INVALID_EVENT. Liên quan nghĩa là: cùng `incident_id`; hoặc cùng trial (hay không ghi trial) và nằm trong cửa sổ incident; với PROBE_SAMPLE là cùng luồng và sau T_req − ε.
- Không coi event INVALID như không tồn tại để ra MISSED, TIMEOUT hay PASS. Action có HEAL_STARTED nhưng ACTION_COMPLETED bị INVALID còn mang cờ ACTION_TERMINAL_MISSING.
- RECOVERY_VERIFIED/RELAPSE INVALID là đầu ra sai của evaluator: scorer tái tính từ mẫu raw và báo EVALUATOR_MISMATCH (mục 7.5).

## 7. Trạng thái và state machine

Năm miền tách nhau. Không chuyển trạng thái giữa miền bằng suy luận: một miền chỉ đổi khi chính nguồn của nó phát event.

### 7.1 Điều khiển fault (H)

```text
PLANNED --ATTACK_REQUESTED--> REQUESTED --ATTACK_STOPPED--> STOPPED
                                  |
                                  +--FAULT_EXECUTOR_RESULT(REJECTED/FAILED)--> (vẫn REQUESTED; effect do bộ đánh giá kết luận)
```

FAULT_EXECUTOR_RESULT chỉ cho biết executor đã chạy hay từ chối. Executor từ chối không tự là CONFIRMED_NO_EFFECT; vẫn cần EFFECT_EVALUATED đủ bằng chứng.

### 7.2 Effect (H)

Mỗi incident có **đúng một** EFFECT_EVALUATED cho mỗi `criteria_version`:
- CONFIRMED: có `t_eff` hợp lệ theo tiêu chí vector.
- CONFIRMED_NO_EFFECT: có record NO_EFFECT, **và** mẫu bằng chứng phủ kín [T_req, T_req + W_eff] với khoảng trống không quá `gap`, không mẫu nào thỏa tiêu chí effect. Scorer kiểm lại phần phủ bằng mẫu raw, không tin riêng trường `evidence` của record.
- UNKNOWN_EFFECT: mọi trường hợp khác, kể cả thiếu record. Ở lại N như lượt thiếu dữ liệu.

Không lấy T_eff từ detector, action hay FAULT_EXECUTOR_RESULT. NO_EFFECT rời N; N = 0 là EMPTY hoặc NO_ELIGIBLE, không bao giờ PASS (ACC ZER-32 mục 3.2, 3.4). Tiêu chí và W_eff theo vector là F-05 (ZER-13/14).

### 7.3 Detect, quyết định, guard, action (O)

```text
DETECTED(alert) --> DECISION(stage=PROPOSAL, trước guard) --> GUARD_VERDICT
                                                                |
                         REJECT: dừng, lưu lý do <--------------+
                         ACCEPT --> HEAL_STARTED --> API_ACCEPTED --> ACTION_COMPLETED{SUCCESS|FAILED|PARTIAL|TIMEOUT}
                                         \--(không có terminal)--> ACTION_TERMINAL_MISSING
                                         \--(retry: action_id mới, retry_of)--> HEAL_STARTED ...
```

- Trạng thái terminal của action là ACTION_COMPLETED với một trong bốn status, hoặc ACTION_TERMINAL_MISSING do scorer gán. **Không trạng thái nào trong miền này tạo RECOVERY_VERIFIED.**
- Quyết định đúng chấm trên đề xuất trước guard (ACC ZER-8 mục 5.3). Guard từ chối không biến quyết định sai thành đúng.
- Chỉ DECISION có `stage = PROPOSAL` vào M1. `ANALYSIS` là bước phân tích của Gaia ở B2, được ghi để tính call/token theo tác tử (M11).
- Fallback: DECISION của RULES có `fallback = true` và `fallback_of` trỏ quyết định LLM lỗi. Lượt fallback không tính là lượt AI (ACC ZER-8 mục 5.4).

### 7.4 Ràng buộc theo nhóm (LOCK, phục vụ ZER-11/ZER-39)

| Nhóm | DECISION được phép (`source_component` / `decision_source`) | LLM_CALL được phép | `initiator` của HEAL_STARTED |
| --- | --- | --- | --- |
| B0 | Không có. Chỉ telemetry tự nhiên; DETECTED chỉ khi detector chạy chế độ quan sát (ZER-8 mục 4.1) | Không | Không có action |
| B1 | `decision_rules` / RULES | Không | AUTO |
| B2 | `decision_llm` / LLM; fallback `decision_rules` / RULES có `fallback = true` | Chỉ từ `decision_llm` | AUTO |
| B3 | `decision_single_llm` / SINGLE_LLM; fallback như B2 | Chỉ từ `decision_single_llm` | AUTO |
| BM | `operator_console` / MANUAL | Không | OPERATOR |

- Ở B0, mọi DECISION, LLM_CALL, GUARD_VERDICT, HEAL_STARTED, API_ACCEPTED, ACTION_COMPLETED của ZERO DOOR là MODE_VIOLATION; trial không dùng làm B0.
- Ở mọi nhóm khác, mỗi HEAL_STARTED phải có `decision_id` trỏ tới một DECISION hợp lệ trong cùng run, với `stage = PROPOSAL`, `response_kind = ACTION` và nguồn được phép của nhóm. Thiếu quyết định như vậy là MODE_VIOLATION; với BM, đó là auto-heal trong MANUAL dù action ghi `initiator = OPERATOR`.
- DECISION, LLM_CALL hay `initiator` ngoài cột được phép, hoặc event có `group` khác nhóm của run, đều là MODE_VIOLATION.

Controller Kubernetes/HPA tự scale không phát event action của ZERO DOOR. Thay đổi replica của nó là telemetry O, được ghi để quy trách nhiệm đúng (ACC ZER-32 RM-03).

### 7.5 Probe, recovery, relapse (H) và chấm sau run (S)

Bộ đánh giá recovery áp dụng ACC ZER-32 mục 3.4 (D-04) trên mẫu probe của luồng bị ảnh hưởng:
1. Chỉ tìm sau T_eff, và sau mẫu lỗi đầu tiên của incident.
2. T_rec = `t_start` của mẫu đạt thứ K trong chuỗi K mẫu đạt liên tiếp, khoảng cách giữa hai mẫu không quá `gap`. Contract chọn `t_start` vì ZER-32 mục 3.7 định nghĩa mẫu “bắt đầu tại t_i” (LOCK). `t_end` vẫn lưu.
3. Cửa sổ ổn định S sau T_rec: mọi mẫu trong (T_rec, T_rec + S] phải đạt; khoảng cách liên tiếp từ T_rec tới mẫu đầu tiên tại hoặc sau T_rec + S không quá `gap`. Có mẫu lỗi trong S thì phát RELAPSE, hủy ứng viên, tìm tiếp sau mẫu lỗi. Thiếu mẫu trong S thì ứng viên không xác minh được; tìm tiếp sau khoảng trống.
4. Chỉ xét ứng viên có T_rec ≤ T_eff + cap_rec. Ứng viên đúng trần vẫn được xét đủ S; ứng viên sau trần không được xét. Cap không cắt S.
5. **Chỉ phát RECOVERY_VERIFIED khi mọi mẫu cần dùng đã kết thúc (sửa RV37-01).** Ba thời điểm tách nhau:
   - `t_rec`: mốc đo, là `t_start` của mẫu đạt thứ K.
   - `recovery_verified_at = t_rec + S`: ranh giới logic của cửa sổ ổn định, tính trên đồng hồ probe.
   - `evidence_complete_at`: `t_end` lớn nhất của các mẫu trong `sample_seq_range`. Một mẫu chỉ có kết quả đạt/lỗi sau `t_end` của nó.

   Ràng buộc: `evidence_complete_at` ≥ `recovery_verified_at`, và `ts_event` ≥ `evidence_complete_at` (so sau chuẩn hóa nếu khác đồng hồ). `ts_ingest` có thể muộn hơn nữa. MTTR và total recovery chỉ dùng `t_rec`. D-04 không đổi; việc chọn `t_start` đã được chấp nhận ở mục 11 (LOCK).
6. **Tham chiếu bằng chứng đủ duy nhất.** RECOVERY_VERIFIED ghi:
   - `trial_id` (envelope), `flow`, `probe_id`, `probe_version`; probe phải được đăng ký trong `TRIAL_STARTED.probes`.
   - `sample_seq_range` = [sequence của mẫu đầu chuỗi K, sequence của mẫu đầu tiên tại hoặc sau T_rec + S], phủ ít nhất K mẫu.
   - `samples_sha256` = SHA-256 của danh sách JSON chuẩn hóa các `event_id` của những mẫu trong khoảng đó, theo thứ tự.

   Khóa của một mẫu là (`trial_id`, `probe_id`, `probe_version`, `sequence`). Hai event khác nhau cùng khóa là INTEGRITY_ERROR.

Scorer (S) tái tính toàn bộ bước trên từ PROBE_SAMPLE raw và so với RECOVERY_VERIFIED trên mọi trường: `t_rec`, `recovery_verified_at`, `sample_seq_range`, `evidence_complete_at`, `samples_sha256`, nguồn gốc mẫu (`probe_id`, `probe_version`, `flow`) và thời điểm phát. Lệch, hoặc RECOVERY_VERIFIED bị INVALID, là EVALUATOR_MISMATCH: dùng giá trị tái tính, báo riêng kèm danh sách trường lệch. Nhãn cuối mỗi incident theo đúng bảng ACC ZER-32 mục 3.4:

| Nhãn | Điều kiện (rút gọn từ ACC) |
| --- | --- |
| RECOVERED | Có T_det, T_rec ≥ T_det, `recovery_verified_at` ≤ T_stop nếu có T_stop; cờ NO_ACTION_BEFORE_RECOVERY khi không có ACTION_COMPLETED=SUCCESS trước T_rec |
| RECOVERED_AFTER_STOP | T_stop < `recovery_verified_at` |
| RECOVERED_BEFORE_DETECT | T_rec < T_det |
| RECOVERED_UNDETECTED | Không detect, có T_rec |
| TIMEOUT | Probe phủ đủ tới T_eff + cap_rec, không có ứng viên xác minh được |
| MISSING_PROBE | Không có T_rec và có khoảng trống probe, hoặc có ứng viên không xác minh được vì thiếu mẫu |
| MISSING | INVALID_CLOCK, INTEGRITY_ERROR, LINK_CONFLICT, AMBIGUOUS, INVALID_EVENT, TARGET_MISMATCH khi không còn detect đúng service, thiếu mốc bắt buộc do ORPHAN, hoặc CLOCK_UNVERIFIED khi nhãn cần so xuyên đồng hồ (duration cùng đồng hồ vẫn báo, mục 4.3) |
| UNKNOWN_EFFECT | Effect không xác định |

**Phục hồi không có nguyên nhân được gán.** Probe xác nhận dịch vụ đã phục hồi; nó không xác nhận ai làm dịch vụ phục hồi. Khi action FAILED, PARTIAL, TIMEOUT, thiếu terminal, hoặc không có action, mà probe vẫn thấy phục hồi, scorer ghi phục hồi kèm cờ NO_ACTION_BEFORE_RECOVERY. Không ghi công cho healer. Ngay cả khi có SUCCESS trước T_rec, INCIDENT_SCORE không có trường “do action”. Đóng góp riêng của ZERO DOOR chỉ kết luận qua đối chứng B0 (ACC ZER-32 RM-06, ZER-8 mục 4).

**SQLi (C5).** Containment là CONTAINMENT_VERIFIED: request mới từ nguồn bị chặn bị từ chối tại điểm thực thi tin cậy, và probe benign của fixture vẫn đạt. Availability Boutique tính riêng trên luồng của nó. Hai luồng không gộp (ACC ZER-32 mục 3.4).

## 8. Mặt dữ liệu, quyền đọc và chống rò

### 8.1 Mặt dữ liệu (ACC ZER-8 mục 5.6, chi tiết hóa)

| Mặt | Ghi | Đọc trong lúc trial | Đọc sau trial |
| --- | --- | --- | --- |
| H | harness, fault_executor, effect_evaluator, probe, recovery_evaluator | Chỉ các thành phần H | Evaluator, scorer |
| O | detector, bên quyết định, guard, executor, telemetry lab; harness chỉ ghi RUN_CONTEXT/TRIAL_CONTEXT | Bên quyết định của nhóm theo quyền vai trò; người vận hành BM qua dashboard O | Evaluator, scorer |
| S | scorer | Không ai (chưa tồn tại) | Người chấm; dashboard đọc kết quả đã chấm (mục 9) |

### 8.2 Trường không bao giờ được vào O

Áp dụng cho mọi trường ở mọi độ sâu của payload, cho `stream`, `source_instance`, `target`, ID, tên topic, path, tên/label/annotation Kubernetes do harness tạo, tag image, header do harness đặt và nội dung prompt/kết quả truy vấn của bên quyết định:

| Thông tin | Nằm ở | Lý do |
| --- | --- | --- |
| `case_class`, `variant_id`, `cause`, tên vector | H | Nhãn đáp án |
| `attack_command`, `fault_params`, `s_att` (danh sách nguồn tấn công) | H | Lệnh và đáp án. IP nguồn quan sát tự nhiên trong log request vẫn ở O |
| `decision_required`, `acceptable_actions`, `expected_action`, `known_good_revision` (dạng nhãn) | H | Đáp án. Lịch sử release thật vẫn ở O |
| `seed`, `onset_offset_ms`, lịch trial, thứ tự case | H | Lộ onset/thứ tự (ZER-8 mục 13) |
| `canary_token` | H | Xuất hiện ở O là bằng chứng rò |
| PROBE_SAMPLE, effect status, RECOVERY_VERIFIED, RELAPSE | H | Healer không dùng probe để tự đóng incident (ACC ZER-32 mục 6) |
| INCIDENT_SCORE, nhãn chấm | S | Chỉ tạo sau trial |

**Được giữ ở O vì là bằng chứng vận hành thật:** metric, log request kèm IP quan sát tại điểm tin cậy, lịch sử release và trạng thái deploy, alert mô tả triệu chứng, quyết định, action, trạng thái HPA. Không xóa các dấu vết này để “làm sạch” (ACC ZER-8 mục 5.7).

### 8.3 Phép kiểm rò cho ZER-9 AC-03 (LOCK; contract offline, chưa phải kiểm runtime)

Scorer phát LEAK_CHECK cho mỗi trial:
1. **Canary:** tìm `canary_token` của run trong mọi event O đã tuần tự hóa và trong prompt/kết quả truy vấn được lưu theo `prompt_sha256`. Gặp là LEAK_DETECTED.
2. **Khóa cấm:** tên trường ở mục 8.2 xuất hiện ở bất kỳ độ sâu nào trong payload O là LEAK_DETECTED.
3. **Trường định danh:** ID phải đúng định dạng mục 3.1. Giá trị nhãn trong GROUND_TRUTH_LOCKED (`case_class`, `variant_id`, `cause`), `attack_type` và `reveal_terms` của HARNESS_MANIFEST xuất hiện trong ID, `stream`, `source_instance`, `target` của event O là LEAK_DETECTED (so khớp như mục 4 bên dưới). Không quét free text telemetry tự nhiên (log request, mô tả alert) bằng từ khóa; đó chỉ là tín hiệu rà soát (ACC ZER-8 mục 5.7).
4. **Giá trị do harness tạo (sửa RV37-02).** Harness tạo pod, label, annotation, tag image, header, path, topic, hoặc biết trước một dấu vết như IP nguồn tấn công. Việc harness tạo ra một giá trị không tự làm nó thành đáp án. Thứ bị cấm là giá trị mang thông tin case. Vì vậy mỗi trial có một HARNESS_MANIFEST (H) với `manifest_version` và `allowlist_version`. Mỗi mục trong `entries` gồm `kind`, `value`, `o_visible` (giá trị nằm ở nơi O truy vấn được, ví dụ namespace mục tiêu) và `class`:
   - `NEUTRAL`: định danh trung tính, cùng dạng ở mọi case, ví dụ tên pod ngẫu nhiên `wrk-5d2c9e71` hoặc digest image. Xuất hiện ở O là bình thường. Nếu giá trị chứa nhãn case (`case_class`, `variant_id`, `cause`, `attack_type`), một `reveal_terms` của manifest (tên vector như `stress`) hoặc canary, thì là LEAK_DETECTED khi `o_visible` hoặc khi gặp ở O.
   - `SECRET`: giá trị chỉ harness được biết, như ID lệnh fault hay tham số tấn công. Gặp ở O, hoặc `o_visible`, là LEAK_DETECTED.
   - `OBSERVABLE`: dấu vết tự nhiên mà harness biết trước, như IP nguồn tấn công. Mục có `allowed_o`: danh sách cặp (`source_component`, trường) được phép, ví dụ (`detector`, `payload.description`) hay (`decision_llm`, `prompt`). Gặp ở cặp ngoài danh sách là LEAK_DETECTED, ví dụ harness tự ghi IP vào TRIAL_CONTEXT.

   So khớp nhãn dùng chữ thường và coi `-`, `_`, `.`, khoảng trắng, `/`, `:`, `=` là cùng một dấu nối. Bề mặt quét là mọi trường của event O và prompt/kết quả truy vấn đã lưu theo `prompt_sha256`. Ngoài các giá trị đã đăng ký, không quét free text bằng từ khóa. Trial không có HARNESS_MANIFEST, hoặc DECISION có `prompt_sha256` mà không lưu prompt, cho kết quả UNKNOWN, không phải CLEAN. Pod `<service>-stress-<id>` hiện tại của chaos-worker trong namespace mục tiêu sẽ là LEAK_DETECTED theo quy tắc này (mục 2). Helper kiểm quy tắc trên dữ liệu giả định; phép thử trên Kubernetes thật thuộc ZER-9 AC-03.
5. **Lịch BM:** SCHEDULE_ACCESS với `actor_role = OPERATOR` và phạm vi chứa trial chưa kết thúc tại `accessed_at` là LEAK_DETECTED, cờ `operator_saw_schedule_before_trial`. Rà nhãn theo variant trước khi niêm phong lịch không phải rò. Run BM không có AUDIT_COVERAGE đầy đủ phủ trial thì kết quả là UNKNOWN, không phải CLEAN (ACC ZER-8 mục 5.7, mục 13).
6. **Đối chứng:** trace sạch phải ra CLEAN; chèn tên case vào `incident_id` phải ra LEAK_DETECTED (ACC ZER-8 mục 5.7). Thêm cho mục 4: pod trung tính và IP quan sát ở trường được phép phải ra CLEAN; pod có tên vector, hoặc IP do harness ghi vào ngữ cảnh O, phải ra LEAK_DETECTED; thiếu manifest phải ra UNKNOWN.

Trial có LEAK_DETECTED vẫn được lưu và chấm; cách dùng trong phân tích formal khóa ở ZER-53 (ACC ZER-8 mục 5.4).

Các ràng buộc quyền đọc ở mục 8.1 là **thiết kế đã khóa, chưa triển khai**. Contract không chứng minh ACL Kafka, RBAC Kubernetes hay quyền kho dữ liệu đã được áp dụng; đó là việc của ZER-9 AC-03 và ZER-12.

## 9. Lưu trữ, export và consumer

Thiết kế, chưa triển khai. Phù hợp phạm vi lab local một máy.

**Kho raw (LOCK).**
- Recorder ghi append-only mỗi bản ghi ingest vào file JSONL theo `(run_id, plane)`, không sửa hay xóa. Mỗi file có manifest: số dòng, SHA-256, `seq` đầu/cuối theo nguồn, khoảng `ts_ingest`, version contract.
- Kafka chỉ là đường truyền. Retention 24 h hiện tại không đủ làm kho. Run chỉ đóng khi recorder đã ghi manifest.
- Kho H tách quyền đọc khỏi O: thư mục hoặc bucket riêng, tài khoản đọc riêng. Bên quyết định không có đường đọc kho H.
- Export cho tái tính là bản sao bất biến của các file raw cùng manifest có hash, gắn `run_id` (ACC ZER-32 RM-15).

**Consumer trực tiếp và dữ liệu họ cần từ contract:**

| Consumer | Đọc | Dùng | Ghi chú |
| --- | --- | --- | --- |
| ZER-9 AC-02 | Mọi event | Truyền ID qua Kafka/HTTP, recorder, export | Phải bảo toàn `event_id` qua hop; HTTP mang envelope nguyên vẹn |
| ZER-9 AC-03 | O + H canary/nhãn/HARNESS_MANIFEST | LEAK_CHECK mục 8.3, kiểm quyền thật | Phải có đối chứng sạch và lỗi chạy thật |
| ZER-38 | — (producer) | PROBE_SAMPLE, PROBE_HEARTBEAT, CLOCK_SYNC; đăng ký probe trong TRIAL_STARTED | Bổ sung trường từng bước (MINOR); chọn cách đo offset và mô hình trôi |
| ZER-10 (scorer) | Raw H/O | MTTD/MTTR/total/reaction, nhãn mục 7.5, M1–M12 của ZER-8 | Đọc raw export, không đọc dashboard hay heal history. Usage/cost giữ `MISSING`/`NOT_APPLICABLE`, không điền 0 |
| ZER-11 (dashboard, ZER-39) | Đầu ra scorer + O | Cùng `run_id` → cùng KPI như export; trạng thái “không có dữ liệu”; độ trễ cập nhật = thời điểm hiển thị − `ts_event` | Kiểm MODE_VIOLATION của B0/BM theo mục 7.4 |
| ZER-12 (guard, ZER-40) | DECISION | GUARD_VERDICT; từ chối event sai schema/trùng/sai nguồn | CI kiểm contract (ZER-40) |

Child ZER-37 Done chỉ phủ AC-01 của ZER-9. Không đóng cha hay gate G1.

## 10. Ví dụ offline và phản ví dụ (SYNTHETIC)

**Tham số minh họa**, lấy từ ZER-32 mục 3.6 (chưa khóa formal): Δ = 1 s, K = 3, S = 30 s, gap = 2 s, ε = 1 s, cap_det = 300 s, cap_rec = 600 s, W_eff = 300 s. Thời gian ghi bằng giây tính từ T0 = 2026-10-19T06:00:00.000Z.

Helper [check_contract.py](../evidence/ZER-37/check_contract.py) dựng envelope đầy đủ từ [fixtures.json](../evidence/ZER-37/fixtures.json). Nó kiểm trường bắt buộc và ràng buộc liên trường (mục 5.3), nguồn, mặt dữ liệu, đồng hồ (mục 4.3), khử trùng, ghép (mục 6), event không hợp lệ, nhóm, bằng chứng recovery và rò (mục 7–8), rồi tính nhãn. Expected được tính tay và ghi vào fixtures trước lần chạy. Helper chỉ kiểm thiết kế; nó không phải validator runtime hay scorer ZER-10, và không tái hiện uptime, CPU hay aggregate của ZER-32. Bản helper/fixtures của lượt review đầu được giữ nguyên ở `scratch/zer37/v1/`.

### 10.1 Trace sạch E01 (đầy đủ chuỗi, ingest muộn)

Nhóm B2, trial một incident, luồng `checkout`. Probe OFF_HOST có CLOCK_SYNC ở đầu và cuối trial.

| t (s) | Event | Nguồn | Mặt | Ghi chú |
| --- | --- | --- | --- | --- |
| 0 | RUN_STARTED, RUN_CONTEXT | harness | H, O | Canary ở H |
| 10 | TRIAL_STARTED (đăng ký probe `prb-0`), HARNESS_MANIFEST, TRIAL_CONTEXT, CLOCK_SYNC | harness | H, H, O, H | `incident_id` cấp trước onset |
| 20–100 | PROBE_SAMPLE đạt | probe | H | — |
| 100 | ATTACK_REQUESTED | harness | H | T_req |
| 101–188 | PROBE_SAMPLE lỗi | probe | H | — |
| 131 | DETECTED (`ts_publish` 131,2) | detector | O | T_det |
| 133 | DECISION PROPOSAL SCALE_UP (`received_at` 131,4) | decision_llm | O | T_con = 131,4 |
| 133,1 | GUARD_VERDICT ACCEPT | guard | O | — |
| 133,5 / 134 | HEAL_STARTED / API_ACCEPTED | executor | O | T_hs, T_api |
| 150 | ACTION_COMPLETED SUCCESS, hậu điều kiện thỏa | executor | O | T_ac |
| 160 | EFFECT_EVALUATED CONFIRMED, `t_eff` = 101 | effect_evaluator | H | T_eff |
| 189–260 | PROBE_SAMPLE đạt | probe | H | Mẫu thứ 3 tại 191 |
| 222 (ingest 290) | RECOVERY_VERIFIED `t_rec` 191, `recovery_verified_at` 221, `evidence_complete_at` 221,25, mẫu [189, 221] | recovery_evaluator | H | Mẫu 221 kết thúc 221,25; ingest muộn 68 s |
| 240 | ATTACK_STOPPED | harness | H | T_stop ≥ 221 |
| 300 | TRIAL_ENDED, CLOCK_SYNC | harness | H | — |

Tính tay: MTTD = 131 − 101 = 30 s. T_rec = 191, MTTR = 191 − 131 = 60 s, total = 191 − 101 = 90 s, reaction = 150 − 131 = 19 s. Nhãn RECOVERED, không có cờ. Nếu dùng nhầm `recovery_verified_at` thì MTTR = 90 s; dùng nhầm `ts_ingest` thì MTTR = 159 s. LEAK_CHECK: CLEAN.

Sai số theo mục 4.3, với host có `resolution_ms` = 1, probe có `resolution_ms` = 16 và `uncertainty_ms` = 20: MTTD và MTTR xuyên đồng hồ có sai số 1 + (20 + 16) = 37 ms; total cùng đồng hồ probe có 2 × 16 = 32 ms; reaction cùng host có 2 ms.

### 10.2 Bảng AC → điều khoản → ví dụ → expected

Cột “Actual” ghi kết quả của helper; số phép kiểm và hash ở bàn giao. Các biến thể dùng chung timeline E01, chỉ khác phần ghi trong cột “Đầu vào”.

| Case | AC / điều khoản | Đầu vào (khác E01) | Expected | Actual |
| --- | --- | --- | --- | --- |
| E01 | AC-01 ID, mốc, nguồn; 4.2, 7.5 | Trace sạch, ingest muộn | MTTD 30, MTTR 60, total 90, reaction 19; RECOVERED; CLEAN | Khớp |
| E02 | Action ≠ recovery; 7.3, 7.5 | Probe lỗi 101–760 dù SUCCESS tại 150 | TIMEOUT; reaction 19; không T_rec | Khớp |
| E03F / E03P / E03T | Terminal FAILED/PARTIAL/TIMEOUT; 7.5 | ACTION_COMPLETED tại 138 (trước T_rec) với status tương ứng; probe lỗi 101–140, đạt từ 141 | T_rec 143, MTTR 12, RECOVERED + NO_ACTION_BEFORE_RECOVERY; reaction NO_SUCCESS | Khớp |
| E03N | Không action; 7.5 | DECISION NO_ACTION, không action; probe như E03F | Như E03F | Khớp |
| E03M | Thiếu terminal; 5.3 | HEAL_STARTED + API_ACCEPTED, không ACTION_COMPLETED; probe như E03F | ACTION_TERMINAL_MISSING; RECOVERED + NO_ACTION_BEFORE_RECOVERY; reaction NO_SUCCESS | Khớp |
| E05 | Relapse trong S; 7.5 bước 3 | Probe lỗi 101–140, đạt 141–150, lỗi 151–160, đạt từ 161 | Ứng viên 143 bị hủy (RELAPSE); T_rec 163, MTTR 32 | Khớp |
| E06 | Mất probe trong S | Probe lỗi 101–140, đạt 141–150, sau đó không có mẫu | MISSING_PROBE (không phải TIMEOUT) | Khớp |
| E07 | T_rec đúng cap | Probe lỗi 101–698, đạt 699–800; stop 800 | T_rec 701 = T_eff + 600, xét đủ S → RECOVERED, MTTR 570, total 600 | Khớp |
| E08 | T_rec sau cap | Probe lỗi 101–699, đạt 700–800; stop 800 | Ứng viên 702 không xét → TIMEOUT | Khớp |
| E09 | Stop giữa T_rec và hết S | Probe lỗi 101–140, đạt từ 141; stop 160 | T_rec 143, verified_at 173 > 160 → RECOVERED_AFTER_STOP | Khớp |
| E10 | UNKNOWN_EFFECT; 7.2 | Không có EFFECT_EVALUATED | UNKNOWN_EFFECT, ở lại N, MTTD/MTTR MISSING | Khớp |
| E11 | NO_EFFECT đủ phủ | Record NO_EFFECT; probe đạt 100–400 | CONFIRMED_NO_EFFECT, rời N | Khớp |
| E12 | NO_EFFECT thiếu phủ | Record NO_EFFECT; probe đạt chỉ 100–200 | UNKNOWN_EFFECT | Khớp |
| A1 / A2 / A3 | N và EMPTY/NO_ELIGIBLE | Tập {E10, E11}; tập rỗng; tập {E11} | N = 1 (requested 2, NO_EFFECT 1, UNKNOWN 1); EMPTY; NO_ELIGIBLE | Khớp |
| E13 | Redelivery vs retry; 6.1 | DETECTED và ACTION_COMPLETED FAILED (`act` 1, tại 140) giao lại cùng `event_id`; retry `act` 2 (`retry_of`), SUCCESS tại 155 | 2 bản trùng bị bỏ; 2 lần thử; reaction 24; RECOVERED | Khớp |
| E14 | Out-of-order; 6.2 | Thêm DETECTED thứ hai tại 140; DETECTED 131 ingest tại 200, sau bản 140 | T_det 131 (theo `ts_event`), MTTD 30 | Khớp |
| E15 | `event_id` trùng, payload mâu thuẫn | ACTION_COMPLETED cùng `event_id`, SUCCESS rồi FAILED | INTEGRITY_ERROR → MISSING | Khớp |
| E16 | Thiếu ID; 6.3 | DETECTED không có `trial_id`, `incident_id`; không có quyết định/action | ORPHAN; incident MISSING (không phải MISSED) | Khớp |
| E17 | Nguồn trái quyền; 5.2 | Thêm DETECTED tại 125 và RECOVERY_VERIFIED `t_rec` 150 do `executor`; probe lỗi 101–760 | 2 SOURCE_VIOLATION; T_det 131; TIMEOUT | Khớp |
| E18 | Đồng hồ chưa xác minh; 4.3 | Probe OFF_HOST, không có CLOCK_SYNC | CLOCK_UNVERIFIED → nhãn MISSING (LOCK); MTTD, MTTR MISSING; total 90 và reaction 19 vẫn báo vì cùng đồng hồ | Khớp |
| E19 | INVALID_CLOCK; 4.3 | `received_at` = 128 < T_pub 131,2 − ε | INVALID_CLOCK → MISSING | Khớp |
| E20 | EARLY_DETECT | DETECTED tại 100,5 (T_req 100, T_eff 101) | EARLY_DETECT, MTTD 0; MTTR 90,5 | Khớp |
| L1 | Rò qua ID; 8.3 | `incident_id` = `inc_c4_resource-0003` (chứa `case_class` của trial) | LEAK_DETECTED (định dạng ID, nhãn trong ID); 13 loại event mang ID đó bị INVALID | Khớp |
| L2 | Rò canary | Canary H xuất hiện trong prompt của DECISION | LEAK_DETECTED | Khớp |
| L3 | Rò seed/onset | Payload DETECTED có `onset_offset_ms` | LEAK_DETECTED (khóa cấm) | Khớp |
| L4 | Rò lịch BM | Nhóm BM; SCHEDULE_ACCESS OPERATOR tại 50 cho trial đang chạy | LEAK_DETECTED, `operator_saw_schedule_before_trial` | Khớp |
| L5 | Thiếu audit BM | Nhóm BM; không có AUDIT_COVERAGE | UNKNOWN | Khớp |
| B0V | B0 không phát action | Nhóm B0, có HEAL_STARTED/ACTION_COMPLETED | MODE_VIOLATION | Khớp |
| B0C | B0 sạch | Nhóm B0, detector tắt, không action; probe như E03F | RECOVERED_UNDETECTED; MTTD/MTTR N/A; CLEAN | Khớp |
| BMV | MANUAL tự heal | Nhóm BM; DECISION `RULES`, action `AUTO` | MODE_VIOLATION | Khớp |
| BMC | MANUAL sạch | Nhóm BM; DECISION `MANUAL` từ operator_console, action `OPERATOR`; audit đủ, không xem lịch | RECOVERED; CLEAN | Khớp |
| W1 | War Game ghép theo cửa sổ; 6.3 | Hai incident cách nhau ≥ cap_rec + S, O không có `incident_id` | Mỗi DETECTED ghép đúng một incident | Khớp |
| W2 | War Game chồng lấn | Hai incident cùng service, cửa sổ chồng | AMBIGUOUS → cả hai MISSING | Khớp |

Các case thêm ở bản sửa 1, mỗi nhóm có ca lỗi và ca sạch đi kèm (E01 là ca sạch chung khi không ghi khác):

| Case | Finding / điều khoản | Đầu vào (khác E01) | Expected | Actual |
| --- | --- | --- | --- | --- |
| R1 | RV37-01; 7.5 bước 5 | RECOVERY_VERIFIED phát lúc 221, trước khi mẫu 221 kết thúc (221,25) | Event INVALID (phát sớm), EVALUATOR_MISMATCH; scorer vẫn tái tính T_rec 191, MTTR 60 | Khớp |
| R2 | RV37-01; 7.5 bước 6 | `sample_seq_range` = [150, 182], các trường khác đúng | EVALUATOR_MISMATCH tại `sample_seq_range` | Khớp |
| R3 | RV37-01; 7.5 bước 6 | `probe_id` = `prb-9` (không có mẫu) | EVALUATOR_MISMATCH tại nguồn gốc mẫu | Khớp |
| R4 | RV37-01; 7.5 bước 6 | `samples_sha256` sai | EVALUATOR_MISMATCH tại `samples_sha256` | Khớp |
| R5 | RV37-01; khóa mẫu | Thêm mẫu thứ hai, khác kết quả, cùng khóa sequence 190 | INTEGRITY_ERROR → MISSING | Khớp |
| L6 | RV37-02; 8.3 mục 4 (ca sạch) | Manifest: pod NEUTRAL `wrk-5d2c9e71`, IP OBSERVABLE cho phép ở mô tả alert và prompt; cả hai xuất hiện ở O | CLEAN | Khớp |
| L7 | RV37-02 | Pod NEUTRAL `frontend-cpu-stress-5d2c` hiện trong prompt | LEAK_DETECTED | Khớp |
| L8 | RV37-02 | Như L6, thêm IP vào TRIAL_CONTEXT do harness ghi | LEAK_DETECTED | Khớp |
| L9 | RV37-02 | Không có HARNESS_MANIFEST | UNKNOWN | Khớp |
| C1 | RV37-03; 4.3 (ca sạch) | Đồng hồ probe lệch +10 s, CLOCK_SYNC ghi `offset_ms` = 10000 ở đầu và cuối trial | MTTD 30, MTTR 60, total 90, không cờ, không mismatch | Khớp |
| C2 | RV37-03 | CLOCK_SYNC chỉ tại 10 và 101; trial kết thúc 300 | CLOCK_UNVERIFIED; MTTD, MTTR MISSING; total 90, reaction 19 | Khớp |
| C3 | RV37-03 (ca sạch) | Đồng hồ probe trôi 10 ms/s, offset 0 tại 10 và 2,9 s tại 300 | Nội suy cho MTTD 30, MTTR 60, total 90 | Khớp |
| C5 / C6 | RV37-03 | `uncertainty_ms` null / `resolution_ms` null | CLOCK_UNVERIFIED; total 90 vẫn báo | Khớp |
| V1 | RV37-04; 5.3 | ACTION_COMPLETED SUCCESS với `satisfied = false` | Event INVALID; INVALID_EVENT → MISSING; reaction MISSING; ACTION_TERMINAL_MISSING | Khớp |
| V2 | RV37-04 | Mẫu đạt có `latency_ms` 5000 > L, `error_class` SLOW | PROBE_SAMPLE INVALID → MISSING, không RECOVERED | Khớp |
| V3 | RV37-04 | DETECTED có `payload` null | Event INVALID, không dừng bộ kiểm; MISSING | Khớp |
| BMD | RV37-04; 7.4 | Như BMC nhưng không có DECISION MANUAL; action vẫn ghi OPERATOR | MODE_VIOLATION | Khớp |
| B1C / B1V | RV37-04; 7.4 | B1 với `decision_rules` / B1 với `operator_console` và OPERATOR | Không vi phạm / MODE_VIOLATION | Khớp |
| B3C / B3V | RV37-04; 7.4 | B3 với `decision_single_llm` / B3 với `decision_llm` | Không vi phạm / MODE_VIOLATION | Khớp |
| X1 | RV37-05; 6.3 | DETECTED mang `incident_id` đúng nhưng `run_id` của run khác | LINK_CONFLICT → MISSING | Khớp |
| X2 | RV37-05 | DETECTED mang `incident_id` đúng nhưng `trial_id` khác | LINK_CONFLICT → MISSING | Khớp |
| X3 | RV37-05 | DETECTED duy nhất ở service `cartservice` | TARGET_MISMATCH → MISSING, không tính detect | Khớp |
| U1 | RV37-05 (ca sạch) | Thêm DETECTED lúc 125 không có `run_id` | UNSCOPED 1, không ghép theo thời gian; T_det 131, MTTD 30 | Khớp |
| W3 | RV37-05 (ca sạch) | War Game; API_ACCEPTED/ACTION_COMPLETED chỉ mang `action_id`, không `decision_id`/`causation_id` | Không ORPHAN; reaction 19 ở incident đầu | Khớp |
| W4 | RV37-05 | War Game; HEAL_STARTED có `decision_id` của incident 1 nhưng `causation_id` trỏ DETECTED của incident 2 | LINK_CONFLICT → cả hai MISSING | Khớp |

### 10.3 Helper có bắt được lỗi không

Helper có chế độ mutant: mỗi lần chạy đổi đúng một quy tắc trong bộ tính, rồi so với cùng expected. Đối chứng sạch phải khớp toàn bộ. Mỗi mutant phải làm ít nhất một case lệch. Bản sửa 1 thêm mutant cho từng quy tắc mới, gồm cả quy tắc cũ của `0.1.0` mà review chỉ ra là sai (ví dụ chỉ kiểm sync quanh T_req, coi mọi giá trị harness là rò). Danh sách mutant và kết quả ghi ở bàn giao.

### 10.4 Phản ví dụ độc lập của Codex

[independent_checks.py](../evidence/ZER-37/independent_checks.py) là bản portable của script review Codex, gọi helper qua các hàm `build`, `validate`, `analyse` với chữ ký giữ nguyên từ bản đầu. Script/kết quả gốc của Codex giữ trong scratch để truy vết. Bản portable chỉ đổi đường dẫn và đích kết quả; xem [verification](../evidence/ZER-37/verification.md).

## 11. Quyết định đã nghiệm thu và phần OPEN

**Codex đã review và Hoàng đã chấp nhận các quy ước sau để khóa `1.0.0`; không đổi D-01…D-05:**
1. `incident_id` ở O chỉ cấp trước onset cho trial một incident; trial C0 có ID slot nhưng slot đó không phải incident và không vào N; War Game ghép ở S (mục 3.3).
2. CLOCK_UNVERIFIED: đồng hồ không đủ CLOCK_SYNC phủ đầu và cuối trial (kèm sai số và độ phân giải) thì duration và so sánh xuyên đồng hồ là MISSING; duration cùng đồng hồ vẫn báo (mục 4.3).
3. T_rec dùng `t_start` của mẫu thứ K; RECOVERY_VERIFIED chỉ phát sau `evidence_complete_at` (mục 7.5).
4. Quy tắc cửa sổ ghép DETECTED khi không có đường ghép khác; ORPHAN trong cửa sổ làm incident MISSING; ID tường minh phải qua bất biến ngữ cảnh (mục 6.3).
5. Định dạng ID `<loại>_<UUIDv4>`, cấm ID có thời gian hoặc số đếm (mục 3.1).
6. Manifest giá trị harness với ba lớp NEUTRAL/SECRET/OBSERVABLE và allowlist có version (mục 8.3).
7. Event INVALID thuộc loại mốc bắt buộc làm incident MISSING (mục 6.4).

**OPEN, giao issue sở hữu:**
- Cách đo offset đồng hồ, mô hình trôi và ngưỡng sai số chấp nhận: ZER-38, F-01. Nội suy tuyến tính ở mục 4.3 chỉ là quy tắc của ví dụ.
- `ingest_grace` và quy tắc chấm lại LATE_INGEST: ZER-10/ZER-53.
- Có tính DETECTED lệch service làm detect không: ZER-10/ZER-53. Đến khi chốt, contract giữ TARGET_MISMATCH ngoài detect bình thường (mục 6.3).
- Tiêu chí effect/containment, W_eff theo vector: F-05, ZER-13/14.
- Trường từng bước của PROBE_SAMPLE; nhiều probe cùng một luồng: ZER-38.
- Enum action và tham số thật: ZER-50.
- Kiểm HEAL_STARTED phải sau GUARD_VERDICT ACCEPT: ZER-12/ZER-40. Contract mô tả thứ tự ở mục 7.3; helper chưa kiểm.
- Danh sách `reveal_terms` và allowlist thật theo vector: ZER-9 AC-03, ZER-44.

**Đối chiếu AC:** Codex đọc live ZER-37/ZER-9 trong audit cuối, khớp snapshot gói. Phần UNKNOWN lúc Claude soạn là lịch sử. **UNKNOWN:** mọi hành vi runtime của producer/consumer. Contract không chứng minh truyền ID, lưu bền, quyền đọc hay chống rò đã hoạt động.
