# Current conclusion — technical functional PASS, publication pending

29/10/2026: [native runtime-01](runtime-01/README.md) completed exactly once under direct approval and independently reviewed READY_TECHNICAL_FUNCTIONAL_SCOPE. C0benignNO_ACTION/noAPI;C1BLOCKguard/nativeA403+benignCRUD verified.2modelcalls/9HTTP/2TCP/1dispatch,CLEAN.78snapshotpins/191rawreceipts checked. No extra lab/model required for accepted functional scope. Publication/CI/merge/Hoangacceptance still pending; no Done/parent/G3/G4/Hrecovery claim. The preparation section below records the earlier checkpoint.

# ZER-50 — source và runner đã review, chờ quyền runtime

Ngày 29/10/2026 (Asia/Saigon). AC sống được đọc qua `linear_zero_door`; URL đúng workspace zero-door, ZER-50 Backlog và parent ZER-20 Backlog tại lần đọc. ZER-48/17/18/7 đọc lại Done. Không thay trạng thái/AC/assignment Linear trong gói này.

Hoàng giao bắt đầu issue tiếp theo sau hydration. Writer duy nhất là ZD4-CODEX tại checkout `C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door`, nhánh `zer-50-hephaestus-guard`, HEAD nền `39d1bb7b5d2ec86a9cd2cdfdaf057529da7d4598`. Scope/dirty baseline tại [scope.json](scope.json); 33 dirty paths cũ được giữ. Primary R chỉ cung cấp quyết định SQLi-only/working agreement và Python environment đã có; không sửa source primary.

## Thay đổi và entrypoint

`hephaestus.recovery.Healer` là entry API chức năng tường minh cho trusted operator/harness: shared Adapter/RunBudget → enum BLOCK_IP/NO_ACTION/ABSTAIN → ModeGate và SQLi evidence guard → SqliContainment → SqliActionState với probe độc lập. Một observation, một inference attempt, không tự retry. Model không cung cấp IP/TTL/target/command; các giá trị đó đến từ policy pins của operator. Không nối executor vào default FastAPI service hoặc mở HTTP body thành quyền execution. Image chỉ đóng gói module để caller được cấp quyền import nó.

Journal tạo run directory exclusive; cùng Journal không được dùng lại qua engine khác. Ghi OBSERVATION/DECISION/GUARD trước dispatch intent; lỗi fsync ngăn tác động mới. API/fsync chạy ngoài event loop và drain owner khi cancel. API timeout sau dispatch giữ UNKNOWN; cancel không có nghĩa đã undo. Outer runtime process vẫn phải có hard deadline vì Python không cưỡng chế được native I/O đang kẹt.

## AC → kiểm → giới hạn

| AC-01 | Kiểm hiện có | Kết luận |
| --- | --- | --- |
| Enum, NO_ACTION/ABSTAIN, source/evidence refs | Closed Pydantic schema, real Adapter với fake transport; malformed JSON/enum/extra/ref/reason/usage/429/timeout/refusal | Offline PASS, chưa model thật |
| Đề xuất → mode/policy guard → action | Real ModeGate + SqliContainment, fake CAS API; source A/private proxy/TTL/UID/context pinned, thiếu disclosure hoặc source B bị từ chối | Offline PASS, chưa live write/enforcement |
| Trace proposal/action/reason/decision latency/probes | Local journal + valid DECISION/GUARD envelopes; decision/action/request joins, budget, unknown/cancel | Offline PASS; không authenticated O archive |
| Probe sau action, giữ benign | Real SqliActionState kiểm A403 + B catalog/CRUD200/201/200/200/404; wrong/missing contents và timeout không thành SUCCESS | Offline PASS; chưa live probe/recovery |
| Benign không chữa thừa | Model NO_ACTION/ABSTAIN và cố ý BLOCK_IP sai trên access benign đều không gọi API/probe | Offline PASS, chưa inference C0 thật |

23 test methods mới đạt trên cả hai môi trường production pin đã có (Nemesis/Hephaestus). 54 regression methods liên quan đạt trên Hephaestus: shared adapter22, mode3, SQLi action-state14, consumer15. Baseline checker PASS và diff whitespace PASS. Log tại [offline/](offline/). Mọi fake trong test mới có socket-connect guard; không có provider, lab, Kafka hoặc native external API call. Đã sửa lỗi fixture/test ban đầu (ID không phải UUID4, Windows close order) và phân biệt API timeout với probe timeout; không hạ guard để lấy PASS.

[Review độc lập](independent-review.md) READY cho source/offline, retest22/22. Không claim review runtime hoặc graph/taint coverage: GitNexus index9567830 stale/incomplete/FTS missing, query/context không có symbol. Source và tests mới được đọc trực tiếp. Không heavy reindex, embeddings hay publication index.

## Trusted runtime reader đã chuẩn bị, chưa chạy thật

Access projection bắt buộc `run_id/trial_id/fixture_uid/detection_event_id` khớp context và fixture đang pin trước model. Metadata này do reader tin cậy gắn sau raw joins; không phải raw log fields hoặc xác thực mật mã. Reader phải giữ raw log/ref/hash/request-ID/correlation/timestamps/Pod UID của đúng lượt. Không chuyển một file shape-valid từ lượt khác thành evidence hiện hành.

`restricted_rows` là observable O telemetry được fixture tính từ response tại `services/sqli-fixture/app.py:578–583`; không là H oracle. Success access log không có `delivered`; chỉ delivery failure ghi `False`. Reader phải project delivered=True sau khi đối chiếu HTTP receipt thành công với request-ID/raw log, không mặc định một log bất kỳ là delivered. Native reader/probe đã được chuẩn bị và review tại [runtime-prep](runtime-prep/README.md); chưa có nghiệm thu native runtime.

Runner mới đã có deadline/owned-process cleanup, preflight source/config/identity/resource/cache/NetworkPolicy, raw joins và probe độc lập; các kiểm này mới có source/offline evidence, phải được quan sát thật trong lượt runtime được duyệt. Không tái chạy nguyên runtime09 hoặc các lượt cũ; không thêm payload/vector/action, không sửa shared lab để dò lỗi. Quyền ZER-49 đã dùng hết; gói mới phải có envelope/pins và quyền mới trước model/lab.

**Chưa Done**: còn quyền model/lab mới và nghiệm thu thật, rồi publication/CI/merge/Hoàng acceptance riêng. Chưa xác minh G3/G4, deployed main integration, authenticated archive, availability recovery/MTTD/MTTR/uptime hay parent ZER-20. Không thay conclusion/component Done đã có của R3.

## Chốt gói chuẩn bị nghiệm thu — 29/10/2026

[Proposal runtime-01](runtime-prep/proposal.md) đã review độc lập:≤2modelcalls,9fixtureHTTP,2TCP,1dispatch,TTL180,600swork +285scleanup;0build/pull/import/sharedrestart/Kafka/BoutiqueHTTP.16runner testsPASS,23Healer tests trên2pinsPASS,baseline/diff/Bash/defaultPLAN_ONLYPASS.54regression trước đó không đổi, giữ log nguồn. Max probe của trusted caller nâng30→120s để chứa native ConfigMap projection, default20 giữ nguyên; test boundary mới đạt. Reviewer sửa/kiểm actual UID, direct-child approval/replay gate, cleanup owner và process tree. Final manifest78file; approval templatefalse, runtime directoryabsent. Không đọc key hoặc gọi provider/lab trong chuẩn bị. Xem [review](runtime-prep/independent-review.md) và [verification](verification.json). Next duy nhất là xin Hoàng duyệt đúng lượt này; chưa publication/Done/parent/G3/G4.
