## Runtime-03 đã đóng — NOT_MET / cleanup CLEAN,29/10/2026

[Kết luận](runtime-03/README.md) và [review độc lập](runtime-03/independent-review.md): gate POLICY_HOOK_MISSING trước model/executor;0call/HTTP/topic/Secret. Namespace absent/sharedinventory giữ nguyên,9product và27invocationpins khớp. Chưa AC02/03, publication hoặc Done; không tự runtime04. Blocker dataplane cần xử lý riêng, không coi bộ nhớ/CNI hay model đã sửa. Phần dưới là các snapshot chuẩn bị/lịch sử.

## Runtime-03 candidate — đã review, chưa duyệt/chưa chạy

[Proposal](acceptance-03-proposal.md) và [review độc lập](runner-fix/independent-review-03.md):35 tests đạt,27 source pins; admission mới fail-closed khi chưa có quyền. Không runtime-03/model/lab/publication hoặc Done; không coi runner fix là chữa xong stall lab. Các gói30tests/lượt01/02 dưới đây là lịch sử có pin riêng.

## Runner fix — offline verified, 29/10/2026

[Delta và verification](runner-fix/README.md):30/30 test; receipt/PSI diagnostics và preflight shared restart đã sửa, giữ mọi guard. 9 product pins không đổi; raw runtime-01/02 và điều tra giữ nguyên. **Chưa chứng minh lab ổn định, chưa runtime-03/inference/publication/Done.** Các kết luận lịch sử dưới đây không phải revision của helper hiện tại.

## ZER-19 — bổ sung điều tra nguyên nhân, 29/10/2026

[Điều tra và bước tiếp theo](investigation/README.md): Docker exec-start chậm 16.911 giây, K3s/Kine và scrape cùng chậm; Prometheus xác nhận CPU/memory pressure tăng trong khoảng mẫu guard bị mất. Cart bị throttle 164/166 chu kỳ và restart theo liveness. Chưa biết tiến trình khởi phát; không quy cho Chrome/Claude hoặc khẳng định đã sửa lab. 9 pin sản phẩm/26 pin runtime giữ nguyên, namespace absent; runtime-02 NOT_MET và cleanup INCOMPLETE giữ nguyên. Chưa chạy runtime-03/model/publication. Bước tiếp: delta nhỏ cho receipt/CPU-I/O observability và kiểm shared restart trong preflight hiện có, review trước một gói runtime mới. Phần dưới là checkpoint lịch sử.

# ZER-19 — kết luận hiện tại: BLOCKED, chưa nghiệm thu runtime

Runtime-02 đã dừng ở guard Docker exec timeout4s, trước model/fixture HTTP. 28 mẫu hợp lệ vẫn đạt RAM/PSI; cartservice tăng restart41→42, có events timeout liveness/readiness1s. Namespace riêng đã UID-delete và xác minh absent, nhưng cleanup tổng thể giữ INCOMPLETE vì shared restart. [Kết luận cuối](runtime-02/final-conclusion.json), [raw/diễn giải](runtime-02/README.md). Không runtime03, publication hoặc Done.

Source/offline vẫn đã review:132 lượt Python chính,37 kiểm Bash;15 helper cases có deny native external clients. Lỗi probe review tạo namespace rỗng trước lượt01 đã được audit/UID-cleanup và không che khỏi evidence. Những phần bên dưới giữ lịch sử chuẩn bị, không phải runtime PASS.

# ZER-19 — phần Nemesis AC02/03

**OFFLINE_READY; runtime chưa chạy, chưa publication/Done.** Hoàng giao tiếp ZER-19 sau khi ZER-48 Done. [Verification](verification.json), [review](independent-review.md), [source pins](source-hashes.json).

| AC | Bằng chứng hiện có | Còn thiếu |
|---|---|---|
| AC01 shared adapter | Dùng lại ZER-48/PR34 đã merge/nghiệm thu | Không triển khai lại |
| AC02 observation → plan → executor → result | Closed fresh O input, shared adapter, registry-only plan, evidence check, unchanged guard, signed Kafka dispatch, matching result; fake IO tests | Một chuỗi chức năng thật qua code mới |
| AC03 bounded start/stop/session | Một task/shared budget, round/call/token/cost/time bounds, six-second pacing, cancellation/setup stop, no replay of unknown; tests trên2pins | Phiên thật tự kết thúc và trace/call/cleanup |

54lượt focused (27case ×2productionpins) +78regression =132lượt Python chính đạt;37kiểm Bash hành vi và entrypoint PLAN_ONLY/cú pháp đạt. Reviewer chạy thêm24IOlượt độc lập; không cộng lại vào132. Bandit0HIGHseverity/highconfidence, không claim toànseverity. Giữ các lỗi fixture test ban đầu trong results/, không hạ parser/context/usage contract để PASS.

Source9paths trên branchcodex/zer-19-nemesis-session/base093e924. Main benchmark /attack/llm-plan vẫn bị khóa; functional CLI purpose FUNCTIONAL_ONLY_NOT_BENCHMARK và receipt benchmark_eligible=false. B2localenvelope chỉ tương thích adapter schema, không phát vào dataset formal. Ledger UNKNOWN không được gửi lại; stop trước send và sau send có ý nghĩa khác nhau. SUCCESS worker không có nghĩa effect/recovery.

[Offline receipt](offline-receipt.json) ghi rõ fake transport/executor và0provider/labrequest. [Gói xin quyền](completion-proposal.md) đã có config và manifestdisabled render/OpenAPI/hash kiểm offline:1privateattempt≤20min/5cleanup,1modelcall,1benignregistrycommand,≤3fixtureHTTP+1TCPcontrol,cache-only/0retry. **Chưa có approval hay apply.** Giữ trần/guard và không dùng lại runner bốn-case ZER-42 nguyên gói.

Nếu được duyệt, chốt helper offline/pins rồi chỉ1lượt; fail thì cleanup/khép blocker, không tự retry. Đạt mới reviewraw và publication/CI/merge/Hoàng acceptance theoWORKFLOW. Không mở issue tiếp theo, không claim G3/G4/end-to-end/KPI. Dirty cũ vàprimaryR được giữ, không stage/commit/push.

## Current correction — runtime-01 stopped; owned empty namespace cleaned

The approvedattempt stoppedbeforemodel/HTTP becauseanunsafe reviewerprobe hadcreated theemptyownednamespace. Root verifiedandUIDdeletedit; namespaceabsent,0Pods/0provider/0fixtureHTTP/0topics. OriginalNOT_MET/INCOMPLETEkept; [incident](runtime-01/incident-conclusion.json) explainsmissingbeforebaselineversusactualdrift. Offline testsnowdeny allnativeexternalclients;15helperchecksPASS. **ZER-19 isnotDone.** [One boundedcontinuation](continuation-proposal.md) needsnewownerpermission; noautomaticretry/publication. Earlieroffline0-mutationstatements applyonlybeforetheunsafeprobe and arecorrectedhere.
