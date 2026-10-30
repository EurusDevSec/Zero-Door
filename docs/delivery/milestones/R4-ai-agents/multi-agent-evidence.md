# Issue — Chứng minh vòng multi-agent và đối chứng RULES

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-21](https://linear.app/zero-door/issue/ZER-21/chung-minh-vong-multi-agent-va-djoi-chung-rules). Nguồn đối chiếu: `R4-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T03-S01 | Chạy một vòng có trace observation–decision–result cho cả ba agent. | AC của [ZER-21](https://linear.app/zero-door/issue/ZER-21/chung-minh-vong-multi-agent-va-djoi-chung-rules) |
| R4-T03-S02 | Pilot B0/B1/B2 với cùng workload/fault đã khóa, ghi action đúng/sai, recovery và usage. | [ZER-51](https://linear.app/zero-door/issue/ZER-51/pilot-djoi-chung-b0-b1-va-b2-cung-djieu-kien) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T03-S01

Trace có ID liên kết và backend/model thật; phân biệt rõ quyết định rule và LLM.

### R4-T03-S02

Bảng đối chứng controller/rules/multi-LLM; cùng evidence cho B1/B2, guard/probe/profile HPA cố định; không mặc định AI tốt hơn.

## Phụ thuộc cần đối chiếu

[R4-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/llm-adapter-and-nemesis.md), [R4-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/gaia-and-hephaestus.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md), [R0-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/research-questions.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.


## ZER-21 — scope/source checkpoint, 30/10/2026

Hoàng giao tiếp tục issue kế tiếp. Đọc lại Linear Zero Door: ZER-21/child51 còn Backlog, prerequisite19/20 Done; giữ AC01 trace chung và AC02 pilot riêng. [Gói source/readiness](../../../evidence/ZER-21/README.md) ghi HEADa593885/branchzer-21-linked-agent-cycle, writerZD4,53dirtyhash cũ và file/action scope. Chỉ chuẩn bị tài liệu/source audit; chưa sửa mã/test/probe, chưa model/lab hoặc quyền publication/Linear.

Khoảng trống: Session/KafkaExecutor, Gaia Diagnoser và functional Healer đã có, nhưng chưa có raw join cùng một execution. Gaia publish detection trước inference; Healer guard/probe vẫn độc lập. Consumer legacy chưa tự nối sang functional executor. Không ghép các receipt cũ khác run thành AC01, không nâng fixture containment thành Boutique recovery/KPI/G3/G4. File plan và các negative checks cho runner ở evidence; chốt exact source/hash trước implementation. Chưa có runner/manifest/proposal runtime đã review; không xin duyệt một lượt chưa chạy được. AC01/AC02 chưa đạt; next là gói nối source/offline, rồi review proposal model/lab một lượt, chưa Done.


### Phạm vi native preparation — 30/10/2026

Writer ZD4, checkout C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door, HEAD a593885e15dc474b83590c4dcf1b214395492fcf, branch zer-21-linked-agent-cycle; index rỗng. Bảo toàn 53 dirty file cùng 12 pin source/artifact trong scope.json. Mở rộng allowlist runtime-prep với run.py/run.sh/lab.py/render.py/remote.py/test_runner.py/proposal.md/source-manifest.json/approval-template.json; các file evidence/checkpoint đã có vẫn theo scope cũ. Không sửa product source, guard, template SQLi, shared manifests hoặc evidence cũ.

Harness cycle.py/test_cycle.py đã qua 14 test actual-class bằng fake transport trên hai Python env và review độc lập READY_SOURCE_OFFLINE sau hai sửa cancellation/reconciliation. Native package tiếp nối tái dùng supervisor/fixture ZER-50, signed KafkaExecutor và cached Go executor, một vòng ba model call và một send; chỉ nối native reader/probe đã có. Khóa source/pin/target/budget/cleanup trong proposal trước runtime; offline test phải chặn socket và fake toàn bộ native ports. Receipt build ZER-42 khớp host/config image ID và ba file Go đã ghi; không có full build-context attestation. Đây là source/offline preparation, chưa runtime/model/key retrieval/build/deploy/traffic, chưa publication/Linear. AC01/AC02 vẫn chưa đạt.


### Bàn giao source/offline + native preparation — 30/10/2026

Checkpoint này thay phần preparation-only ở trên; các đoạn cũ giữ lịch sử. Actual Session/Diagnoser/Healer được nối trong cycle.py, shared Adapter/budget/full context; native reader join worker→raw access; Gaia diagnosis là data, Healer guard/O access độc lập. Giữ signed command schema3, full context6 ở root trace. 14 cycle tests PASS trên Hephaestus/Nemesis env và14 native boundary tests PASS; offline fake transports/socket-deny, không native/provider call. Reviewer /root/zer50_review read-only READY_SOURCE_OFFLINE và READY_SOURCE_OFFLINE_NATIVE_PREP sau gom sửa cancellation/reconciliation và UID/IP/fixture refresh trước API. Hash/test/review ở docs/evidence/ZER-21/;53dirty/12pins và original NOW suffix/note prefix bảo toàn, HEADa593885/branchzer-21-linked-agent-cycle, git indexrỗng.

Runner native mặc định PLAN_ONLY, templateapproved=false/exactSHA/expiry/exclusive output+claim+Job stdin gate. Proposal khóa một attempt3modelcalls/1send/8HTTP/2TCP/1CMreplace/TTL180/work900s+cleanup300s, private namespace mới và2freshownedtopics, không build/pull/import/sharedworkload. Cached artifact build/image receipt khớp3Go source pins; không full historical build-context attestation. Không lấy key, model/lab/build/deploy/traffic, publication hoặc Linear mutation trong gói này. AC01/AC02 vẫn chưa đạt; fixture containment không Boutique recovery/KPI/G3/G4. Next Hoàng duyệt model/lab riêng theo proposal, một execution và independent raw reconciliation; AC02 thuộcZER51, không chạytrùng hoặc tựDone cha. Publication/CI/merge/owner acceptance còn theoWORKFLOW.


### Quyền runtime-01 — 2026-10-30T01:42:21.871975+00:00

Hoàng trả lời “được” cho đúng proposal model/lab đã review. Exact SHA, HEAD/dirty, file/action scope, đường Doppler zero-door/dev chỉ OPENAI_API_KEY và trần một attempt ở docs/evidence/ZER-21/runtime-scope.json. Cho phép một execution, native cleanup và raw reconciliation; chưa chạy tại lúc ghi. Không thêm quyền publication/Linear/pilot hoặc tự Done. Giữ kết quả STOP/failure/UNKNOWN, không replay.


### Admission review và xác nhận rõ — 2026-10-30T01:43:45.735822+00:00

Lệnh runtime ban đầu bị automatic approval review từ chối trước CreateProcess do xác nhận ngắn chưa đủ cụ thể. Không có runtime directory/launch log, không lấy key/model/lab. Sau câu hỏi nêu toàn bộ target/budget/action, Hoàng xác nhận “Tôi cho phép đúng một lượt theo toàn bộ giới hạn trên”. Lưu nguyên lớp lỗi và quyền mới ở runtime-approval-review.json; thử lại cùng launcher, không workaround hoặc thay scope/source.


### Runtime-01 và bản sửa, bàn giao — 2026-10-30T02:00:50.068560+00:00

[Evidence](../evidence/ZER-21/README.md): một attempt137.203s dừng TypeError kube kwargs ởbootstrap,0model/HTTP/TCP/Healerwrite. OriginalcleanupINCOMPLETE giữ nguyên; readonly4queries xác nhậnnamespace+2topicsabsent/cùngbrokerUID/sharedspecs+UID+restartspreserved, CLEAN_AFTER_READ_ONLY_RECONCILIATION; ownedprocessesclosed/reaped. Sửa wrapperZER21+actualseamregression: trướcTypeError/sauPASS,15native testsPASS,reviewREADY_SOURCE_OFFLINE_FIX. [Proposal02](../evidence/ZER-21/runtime-prep-02/proposal.md) inert/runnable126pins/templatefalse/15testsPASS/reviewREADY_PROPOSAL_RUNTIME02_SOURCE_OFFLINE, cùngtrần3calls/1send/8HTTP/2TCP/1CMreplace/900+300s/estimate0.015USD. Next Hoàng duyệt riêng exactproposal02; không replay01. AC01/AC02/G3/G4/KPI chưađạt;53dirty+12pins giữ nguyên,indexrỗng,noGitpublication/Linearwrite. 

Quyền explicit duyệt một attempt đã dùng hết; source snapshot/receipt gốc giữ nguyên. Root đã ghi failure TypeError, reviewer xác nhận lỗi và điểm mock seam bị bỏ sót; chỉ sửa bounded kube wrapper và thêm regression thật qua fake command. Proposal02 source-only đổi hai attemptliteral, templatefalse/exactSHA. Hoàng cần duyệt lượt2 riêng trước model/lab; không Git/Linear/pilot authority.


### Quyền runtime-02 — 2026-10-30T02:07:33.416899+00:00

Hoàng xác nhận rõ “Tôi cho phép đúng một lượt runtime-02 theo toàn bộ giới hạn trên” cho exactproposal2cb6aca9/manifest18766270 đã review. HEAD/dirty/file/action scope và trần3model/1send/8HTTP/2TCP/1CMreplace/900+300s/estimate0.015USD ghi runtime-02-scope.json. Một execution mới với IDs/topic mới và cleanup, không replay01 hoặc mở rộng scope; không Git/Linear/pilot authority. Source126pins và original53dirty+12pins/126snapshot01 được xác minh trước ghi.


### Bàn giao runtime-02 — 2026-10-30T02:21:54.874463+00:00

[Evidence](../evidence/ZER-21/README.md): một runtime02 đượcHoàngduyệt,1gpt-6-luna callOK/PLANSTOP/216+23tokens/estimate0.0000331USD;1benignHTTP+2TCP/0SQLisend/0Gaia-Healer. Worker sidecar đãchạysetup, khôngdispatchcommand; AC01/AC02/G3/G4/recovery/KPI chưađạt. OriginalcleanupINCOMPLETE/MEMORY_STOP giữnguyên; guardedresumeCLEAN trongdeadline300sgốc, namespace+2topicsabsent/sharedspecs+restarts giữnguyên/processesclosedreaped. Reviewđộclập xácnhậnNOT_MET_LEGITIMATE_MODEL_STOP+CLEAN_AFTER_GUARDED_CLEANUP_RESUME,khôngsourcefindingmới.126executedpins/oldruntime01artifacts/53dirty+12pins bảo toàn,indexrỗng. Next làmrõ contractnhiệmvụNemesis qua [audit](../evidence/ZER-21/runtime-02/selector-contract-audit.md), chưasửa prompt/chuẩn bị03 hoặc quyền mới; khôngretry01/02,noGitpublication/Linearwrite/pilot51. Checkpoint dưới là lịch sử.



Giữ rawSTOP và cleanupfailure thayvì đổi thànhsuccess hoặc replay. Actual modelreturned gpt-6-luna, revisionUNKNOWN; estimatekhôngbilling; khôngrationale để giải thíchvìsaoSTOP. Quyềnruntime02đãdùnghết, currentintentcontract là follow-upcandidate/chưa sourcebugxácnhận. Nguồncode/promptkhôngđổi; chưapublication/merge/Linearwrite/ownernghiệmthuAC.


## Claude điều tra ZER-21 — triệu chứng, bug và evidence

Hoàng yêu cầu bàn giao điều tra sau runtime-02; chưa giao sửa hoặc chạy thêm. Checkpoint 2026-10-30T02:25:54.046419+00:00: sole writer ZD4, checkout `C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door`, branch `zer-21-linked-agent-cycle`, HEAD `a593885e15dc474b83590c4dcf1b214395492fcf`, index rỗng, dirty work nhiều issue đã có. Phiên soạn handoff chỉ đọc nguồn/receipt và append chính note này; không đổi product/prompt/test/evidence cũ, không model/lab/Git/Linear. Trước khi nhận điều tra, tự đọc safeguards/working-agreement, Git state và assigned issue live; không checkout/reset/clean hoặc mở issue khác. R:/ primary không phải writer checkout này. Chưa khẳng định root cause của MODEL_STOP.

### 1. Blocker chính: gói AC01 không đạt vòng ba agent; MODEL_STOP chưa được giải thích

Expected AC01: một execution thật có trace liên kết Nemesis → signed Kafka/Go worker → native O reader → Gaia → Hephaestus → probe. Actual runtime-02: một OpenAI gpt-6-luna call `outcome=OK`, usage216input+23output, PLAN `{template: STOP, evidence_ids: [ev-health-01]}`, completed_rounds0; receipt `NEMESIS_NOT_COMPLETED`. Không dispatch intent/result hoặc SQLi execution, không Gaia/Healer call. Go sidecar đã được khởi động trong setup. Đây không phải provider refusal/fallback/timeout; trace không có rationale/reason_code, nên chưa biết vì sao model chọn STOP.

Code cần nối và đối chiếu, trong đúng checkout trên:

- `agent-orchestrator/nemesis/session.py:27–31`: selector v1 cho phép STOP khi health unknown/unhealthy hoặc another round unnecessary. `:45–65` kiểm observation chỉ timestamp + evidence id/health. `:199–203` gửi instructions + observation/previous_execution_status/allowed_templates; `:217–221` ghi PLAN rồi dừng MODEL_STOP.
- `docs/evidence/ZER-21/runtime-prep-02/lab.py:323–351`: baseline HTTP200 được chiếu thành HEALTHY, ev-health-01; Session một round, allowed_templates chỉ disclose-restricted; harness đòi completed cycle/Healer action. Đối chiếu việc truyền ý định của một trial đã được owner duyệt với quyền selector tự kết luận round unnecessary. Đây là giả thuyết contract cần kiểm, không nguyên nhân đã chứng minh.
- `docs/evidence/ZER-21/runtime-prep-02/cycle.py`: consumer của receipt Nemesis, điều kiện đi tiếp Gaia/Healer và final verdict. Đừng đổi STOP thành completed, tự dispatch thay model hoặc retry để tìm output đẹp.

Evidence: `docs/evidence/ZER-21/runtime-02/{cycle-receipt.json,model-budget.json,http-001.json,work-result.json,acceptance.json,reconciliation.json,selector-contract-audit.md}`; journal `cycle/run_3115e2fbf97441ce967beaa9e1c5fa67/events.jsonl`. Đối chiếu request/response/event/decision/context IDs và source snapshot, không chỉ đọc summary.

Cần trả: phân biệt hành vi hợp lệ theo component contract với lỗi thiết kế harness/contract nhiệm vụ; chứng cứ nào xác định nguyên nhân, phần nào UNKNOWN; đề xuất thay đổi tối thiểu nếu có, cách kiểm offline có sức phân biệt. Không mặc định cần đổi prompt, không thêm H oracle/expected answer, không bỏ STOP/health/guard hoặc ép model thành công.

### 2. Vấn đề cleanup đã quan sát: late exception làm mất kết quả đã biết và chặn dọn topic

Code: `docs/evidence/ZER-50/runtime-prep/lab.py:386–395`: namespace absence/spec/restart đã được kiểm, sau đó `self.resources()` ném MEMORY_STOP; catch chung gán `absent = specs = restarts = False`. `docs/evidence/ZER-21/runtime-prep-02/lab.py:368–371` return ngay khi namespace_absent false, nên bỏ qua hai topic OWNED.

Actual: original cleanup raw10002 delete return0, raw10003 wait return0, raw10004 namespace get empty; raw10005 snapshot; raw10006 memory read. PSI avg10=8.06 > guard5; RAM vẫn trên ngưỡng. `cleanup.json` INCOMPLETE và namespace_absent/shared fields false, topic cleanup chưa chạy. Vấn đề cần điều tra là phân loại fact đã biết/UNKNOWN và control flow cleanup; MEMORY_STOP không tự chứng minh namespace còn tồn tại. Không nới ngưỡng memory hoặc bỏ owner/UID/broker guard để sửa.

Root đã resume nguyên cleanup_owned bằng state/before gốc, output riêng, Job kill-on-close và deadline vẫn tính từ cleanup ban đầu +300s. `cleanup-resume-02/supervisor.json` CLEAN/exit0/reaped/treeclosed, PSI0; đúng hai OWNED topics list→delete→absent, same brokerUID; hoàn tất61.64s trước deadline gốc. Original cleanup failure giữ nguyên. Cleanup-resume đầu lỗi ModuleNotFoundError httpx trước nativeaction do helper ngoài canonical runner thiếu PYTHONPATH; helper đã sửa giống PYTHONPATH có sẵn của canonical supervisor. Không kết luận canonical run.py có cùng lỗi import.

Cần trả: giải thích control flow và mô hình trạng thái cleanup phù hợp (known fact vs not checked vs failure), patch/test plan tối thiểu để late resource failure không làm sai evidence hoặc bỏ sót owned cleanup; giữ nguyên guard và deadline. Reuse existing receipt, không dựng lại lab để điều tra. Không reopen/đổi trạng thái ZER-50 đã Done; đây là inherited implementation seam của ZER-21.

### 3. Bug runtime-01 đã xác nhận và sửa — chỉ làm lịch sử/regression reference

Inherited `docs/evidence/ZER-46/runtime-prep/preflight.py:68` có `kube(self,*args)`, nhưng ZER21 topic/consumer calls truyền timeout/allowed, gây TypeError trước Kafka create command. Bản sửa ZER21-only ở `runtime-prep-02/lab.py:154–157` forward kwargs vào bounded command, giữ context/request-timeout. Test trước mock qua kube/topic nên bỏ sót seam; regression mới đi topic→kube thật→fake command, trước sửa ERROR TypeError/sau PASS;15native tests PASS. `runtime-01` là NOT_MET0model/0HTTP/0TCP, snapshot/raw vẫn nguyên. Không coi test PASS này là bằng chứng positive integration runtime02.

### Kết quả điều tra cần bàn giao và quyền

Trả findings theo `file:line | severity | observed defect/contract gap | evidence | proposed minimal fix`, tách confirmed/inferred/unknown và existing-fixed/new-open. Nêu AC01 bị chặn ở đâu, AC02/pilot51 vẫn riêng; không coi fixture cleanup là recovery/KPI/G3/G4. Kèm file/action scope và test/probe plan có thể review trước khi sửa, không overengineering hoặc rà toàn repo.

Điều tra read-only: không sửa source/prompt/tests/guard/receipts, không lấy key/Doppler/model/HTTP/Kafka/Kubernetes/build, không replay runtime01/02 hoặc tạo03, không commit/push/PR/merge/Linear mutation. Hai quyền one-attempt đã dùng hết. Nếu đề xuất sửa, đưa evidence và patch plan; không tự chạy lại để xác nhận. Hoàng sẽ đưa handoff này cho Claude; Codex không gửi ra chat khác.


## Codex review bản cleanup Claude — 30/10/2026

Scope/checkpoint: Hoàng giao “claude đã làm xong hãy kiểm tra”; review local delta của đúng ba file `runtime-prep-02/{lab.py,test_runner.py,source-manifest.json}` so với source/manifest được snapshot trong runtime-02. Checkout `C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door`, branch `zer-21-linked-agent-cycle`, HEAD/base `a593885e15dc474b83590c4dcf1b214395492fcf`; `origin/HEAD` không được cấu hình, dùng baseline main đã chốt (không suy từ remote HEAD). Nhiều dirty/untracked issue khác giữ nguyên, index rỗng lúc bắt đầu; không review gộp chúng. Đọc live ZER-21 qua named connection, URL zero-door, AC01/02 vẫn unchecked. Boundary của lượt review: đọc source/receipts và graph local, chạy hai entrypoint test và probe fake; chỉ append ghi chú này, không sửa product/prompt/test/manifest/authorization/receipt, không lấy key hoặc gọi lab/model/Git publication/Linear write. Timestamp kết review: 2026-10-30T03:17:33.783938+00:00.

**Verdict: NOT READY — một finding P2 còn chặn bản cleanup.**

`docs/evidence/ZER-21/runtime-prep-02/lab.py:422–426 | P2 | Nhánh shared snapshot lỗi cho phép topic cleanup dù resource guard chưa được kiểm.` `cleanup_namespace()` đặt `step="shared"` ở :399; snapshot/parse/spec/restart lỗi sẽ nhảy qua `resources()` :407 và trả `namespace_absent=True, failed_step="shared"`. Caller chỉ chặn `failed_step=="resources"`, nên đi vào topic list/delete. `command/check` kế thừa không gọi resource guard; cleanup_mode bỏ điều kiện stop của work, nên không có kiểm tài nguyên thay thế.

Repro độc lập offline: namespace owner/UID đúng và được xác nhận absent; `snapshot()` ném `RuntimeError:SNAPSHOT_FAILED`; fake `resources()` sẽ ném `MEMORY_STOP` nếu được gọi; topic OWNED. Actual: **resource_guard_calls=[]; topic_operations=[list,delete,list]**, verdict INCOMPLETE, topic_cleanup ATTEMPTED. Đây là control-flow đã tái hiện trên mã mới, không phải tuyên bố memory thật hiện đang thấp hoặc lab thật bị tác động. Probe tại `C:/Users/ACER/.codex/visualizations/2026/10/29/01a18832-a874-7f52-89a0-dd598c318302/zer21-review-claude-probe.py`; native subprocess/network bị chặn, không key/model. Lượt probe đầu bị chặn bởi import platform.system gọi subprocess; sửa riêng scratch harness bằng mock platform, lượt sau exit0 và assertions xác nhận defect. Không sửa source trong lúc probe.

Test mới `test_runner.py:262–268` chấp nhận nhánh này và chỉ assert topic attempt; không assert resource guard đã PASS trước attempt, vì vậy full suite xanh không bắt được lỗi. Sửa tối thiểu: cho bước kiểm resources độc lập với lỗi shared snapshot và chỉ cho phép topic effects sau resource check PASS; FAIL/UNKNOWN phải ghi trạng thái pending rõ ràng, giữ fact namespace/spec/restart đã biết và verdict INCOMPLETE khi có lỗi. Regression cần phân biệt hai case cùng snapshot failure: resources MEMORY_STOP/missing => không topic operation; resources PASS => được dọn đúng OWNED topic trong owner/UID/broker/deadline guards, shared facts vẫn UNKNOWN và verdict INCOMPLETE. Không nới guard, đổi STOP hoặc tạo runtime mới.

Đã xác minh: tự chạy `test_runner.py` **20/20 PASS**, `test_cycle.py` **14/14 PASS** trong production-hephaestus dependency env, `PYTHONDONTWRITEBYTECODE=1`, key unset; test/native fake đã đọc trước khi chạy. Cả 306 artifact runtime-02 trong ledger khớp hash; ZER-50 lab giữ SHA `df822efbf923eace35db3948a772286cc4e79936c379598608a4ac5135791a83`. Full diff chỉ thêm cleanup_namespace, sửa caller và test; manifest chỉ đổi đúng hai source hashes. Giữ fact True/False/None và chặn topic sau resource failure trực tiếp là sửa đúng. Không có source finding khác trong delta này. Lab/test/manifest SHA lần lượt: `674261531652aa793fa0fa34f844024709c24e3be5ec9b319ca17f6c6149c5b4`, `fa84ee90ef3f98ed91d923f35b61255760ded81f23ca30084d117bc7bb24559a`, `a9d3dda2dd702a82c0d4f94dff56cc4b7de8446a6aabbb162a2875c2564fa1b5`.

Graph/coverage: GitNexus alias zero_door_zd4 đúng checkout/HEAD; status ban đầu stale (11 changed, 296 added). Đã thử analyze --pdg --index-only; đóng đúng owned process bằng argv/PID sau hơn 6 phút, trước clean exit; không coi index refresh đã hoàn tất. Một số symbol rows mới đã ghi và đọc được: context exact UID Lab.cleanup_owned#0 đúng dòng417–447, outgoing cleanup_namespace/topic; namespace impact có caller cleanup_owned; cleanup_owned incoming lower-bound, thiếu3 call sites do receiver typing, risk UNKNOWN. detect_changes(all) trả86 symbols/33 tracked files thuộc dirty tổng, không bao phủ untracked ZER21; không dùng low/0 affected làm bằng chứng an toàn. explain(file) trả0 nhưng closure/property/implicit chưa modeled, index run chưa hoàn tất; PDG controls file chỉ đọc page12, chưa bao phủ cleanup. Vì vậy không claim complete graph/taint/dependence review. Finding được xác minh bằng full snapshot diff, direct source (namespace cleanup/caller/topic/bounded command/resources, inherited main và supervisor acceptance consumer), 34 existing tests và probe control-flow offline độc lập. Graph chỉ navigation, cần refresh hoàn tất khi có lượt sửa code kế tiếp; không mở thêm rebuild trong review này.

Nemesis MODEL_STOP không được sửa trong gói Claude này; nguyên nhân lựa chọn STOP vẫn UNKNOWN. AC01/AC02/pilot51/recovery/KPI/G3/G4 chưa đạt. Hai attempt cũ đã consumed; authorization cũ pin manifest cũ được giữ nguyên, không coi source mới là runtime đã duyệt hoặc dùng lại runtime-02. Next: Claude sửa gom đúng finding resource gate và retest offline; sau đó tiếp tục điều tra contract Nemesis theo handoff phía trên. Codex không tự gửi tin/delegate hoặc chạy runtime.


## Codex retest P2 resource gate — 30/10/2026

Checkpoint/scope: review delta sửa finding P2 theo bàn giao Claude, cùng checkout/branch/HEAD a593885 như review trước; chỉ đọc lab/test/manifest, consumer trực tiếp đã review, hash evidence và chạy lại hai entrypoint offline. Không source/prompt/guard/authorization/receipt edit, không model/lab/runtime/publication/Linear mutation; append đúng note hiện có. Thời điểm: 2026-10-30T03:28:40.576435+00:00. Git HEAD/branch/index đọc lại bằng wrapper retest, không staging.

**Verdict: READY_SOURCE_OFFLINE_CLEANUP_FIX — finding P2 phía trên CLOSED ở mức source/offline. Không có finding mới trong delta sửa.** `lab.py:409–416` kiểm resources bằng try độc lập với namespace/shared; failed_step giữ lỗi đầu tiên. `:429` gate topic bằng explicit resource_guard PASS, thiếu/FAIL không vào topic. Fact đã biết giữ nguyên; lỗi snapshot/guard vẫn làm INCOMPLETE. Tái dựng ngược đúng phần delta trên bytes trong memory khớp SHA lab đã review `67426153…`, xác nhận không có thay đổi lab khác ngoài resource try/field/gate. Không ghi đè file khi so sánh.

Tự chạy lại offline `test_runner.py` **21/21 PASS**, `test_cycle.py` **14/14 PASS**, production-hephaestus dependency env, key unset và no bytecode. Hai regression `test_runner.py:267`/`:275` xác nhận snapshot failure vẫn gọi guard đúng một lần: MEMORY_STOP => không topic operation, PENDING_RESOURCE_GUARD; PASS => guard chạy trước topic attempt, shared facts None, verdict INCOMPLETE. Đọc log Claude before/after: cùng hai case fail trên lab67426153 và pass trên0776130b vì đúng missing guard/field, không phải lỗi import. Các test owner/broker/OWNED và single-use admission vẫn PASS; không mở rộng test matrix hoặc lab để khép P2.

Manifest126 pins hiện tại đều khớp, so với executed runtime02 chỉ khác hai lab/test hash; cả 306 runtime02 ledger artifacts không đổi, ZER50 lab giữ df822efb…. SHA lab `0776130b5555398463c2b457da688128c15a75c80e583c83084157906e1b0d21`; test `1da915e4c99fa4b743387d2a61ef9fcd08f6c5c1e7a91b93260e8ae01b86ab02`; manifest `988b10ca399b74a653857705bc7e5fa36966af7a1e2bb53489abcbc49bfcfcd2`. Authorization cũ vẫn pin manifest cũ, không reauthorize/replay.

Giới hạn graph giữ từ review trước: refresh index-only/PDG bị dừng trước hoàn tất; context đọc lại vẫn trả dòng cleanup_owned417–447 của bản67426153, trong khi source mới424–454. Không dùng graph cũ để chứng minh delta/impact và không claim complete graph-backed/taint review. Consumer và control flow kiểm bằng source trực tiếp, snapshot diff và targeted regression; không phát lại rebuild để trì hoãn kết luận của sửa nhỏ này. Bản source mới chưa chạy cleanup lab thật.

Bước tiếp theo là điều tra contract nhiệm vụ Nemesis/MODEL_STOP theo handoff mục95 trở đi; không cần sửa thêm cleanup khi chưa có lỗi mới. P2 khép không đồng nghĩa ZER21 Done: AC01/02 chưa đạt, không recovery/KPI/G3/G4, hai attempt trước consumed, không có quyền runtime03 hoặc model call mới. Note review trước giữ nguyên như lịch sử; mục retest này thay kết luận NOT READY cho đúng delta cleanup.


## Codex review selector v2 patch plan — 30/10/2026

Scope: review attachment e178a42c patch plan, source session/session_cli/adapter/contract và fake consumers test_nemesis_session/test_nemesis_session_io/test_cycle. Cùng checkout branch zer-21-linked-agent-cycle, HEAD a593885; chưa triển khai. Chỉ append note này; không source/test/manifest/receipt edits, không runtime/model/lab/publication/Linear write. Review lúc 2026-10-30T03:41:10.829906+00:00. Git HEAD/branch/index đọc lại bởi wrapper; phần dirty cũ giữ nguyên. Boundary: đây là plan review, không phải source implementation acceptance hoặc runtime approval.

**Kết luận: hướng thiết kế phù hợp; cập nhật ba điểm trong plan trước khi triển khai cùng một gói offline.**

1. Sửa provenance/trạng thái: đã đọc live Linear Zero Door ZER19 Done, AC01–03 checked; runtime04 đã được nghiệm thu và PR35 merge 9b5287c140d704b8009f6dfe53f31f720b4b23a4. Không có pending verification run của ZER19 được kế thừa. session.py là shared product; v2 là thay đổi trong gói ZER21, kiểm regression consumer CLI nhưng không reopen hay sửa evidence/manifest lịch sử ZER19.
2. Manifest scope thiếu session_cli.py: file này đã nằm trong126 pins hiện tại và plan sửa nó, do đó phải repin đủ **session.py, session_cli.py, prep02/lab.py, prep02/test_cycle.py** (và bất kỳ file thực sự thay đổi nào đã có pin); không chỉ ba hash đã liệt kê. Thêm tests/test_nemesis_session_io.py vào allowlist nếu đặt các regression config_valid tại consumer hiện hữu này. Trước sửa ghi exact file/hash/HEAD/dirty checkpoint, một writer. Chọn sửa tại chỗ runtime-prep-02 cho source/offline như cleanup trước; giữ nguyên runtime02/source và raw, authorization cũ/attempt consumed. Không tự tạo proposal/approval/runtime03 hoặc làm mới manifest lịch sử để xanh kiểm cũ.
3. required_rounds=0 chỉ giữ **config compatibility**, không bảo đảm behavior compatibility: task mới, schema và prompt v2 đều thay model input/output; quy tắc completed>=0 cho phép ROUNDS_COMPLETE ngay round đầu. Ghi rõ zero nghĩa không yêu cầu số round tối thiểu; max_rounds vẫn là trần, required không ép thực thi. Với ZER21 required1, completed0 phải được truyền đúng. STOP tự báo ROUNDS_COMPLETE trái counter vẫn là model claim đã lưu, không được làm thay đổi actual completed_rounds hoặc thành công; giữ NOT_MET và UNSPECIFIED. Không hứa v2 sẽ chọn template.

Giữ proposed Plan stop_reason required enum NONE/ROUNDS_COMPLETE/NO_SUITABLE_TEMPLATE/UNSPECIFIED, cross-field validator STOP/nonSTOP, prompt/receipt version2, admission/health/evidence/allowlist/budget/cancel/worker guards nguyên trạng. task chỉ là nhiệm vụ chức năng, không quyền thực thi hay H answer; việc key không nằm FORBIDDEN chỉ là kiểm cấu trúc, không thay review ý nghĩa dữ liệu. Không cần sửa adapter/command_guard/observation_valid/cycle/Gaia/Healer.

Test trong gói: chọn template/STOP reasons/strict invalid schema; required_rounds biên gồm bool và sai kiểu; task có đúng purpose/required/completed, round sau mang actual completed count; config cũ default0, config mới và unknown-key rejection; pin request prompt/receipt version; giữ evidence/health/cancel/budget boundaries hiện có. Test negative phải assert đúng outcome ở đúng lớp: Plan schema qua adapter SCHEMA_INVALID, Session stop_reason MODEL_SCHEMA_INVALID; PLAN_EVIDENCE/allowlist runtime validation là VALIDATION_FAILED. Consumer cycle cần thêm explicit fake STOP case xác nhận NEMESIS_NOT_COMPLETED, 0 executor/observer/Gaia/Healer và không replay; chỉ chạy14 test cũ chưa chứng minh nhánh STOP vì chưa có case STOP trong test_cycle hiện tại. Toàn bộ session*.py và21 runner/14 cycle cộng case mới, offline không key/network/native lab.

Sau triển khai Claude trả exact diff/hashes/tests/failures cho Codex retest. Plan review không phải lệnh gửi sang Claude hay quyền chi phí/runtime; Hoàng đưa bàn giao. AC01/AC02 vẫn chưa đạt; cleanup P2 vẫn khép source/offline và không bị mở lại vì thay contract selector. Không cần lượt model chẩn đoán riêng; chỉ xem xét concrete runtime package sau source review.


## ZER-21 — scope hoàn tất selector và chuẩn bị runtime-03 — 30/10/2026

Hoàng giao hoàn thành issue theo yêu cầu. Codex tiếp nhận writer sau bàn giao Claude; HEAD a593885e15dc474b83590c4dcf1b214395492fcf / branch zer-21-linked-agent-cycle, index rỗng. Exact dirty hashes và allowlist ở `docs/evidence/ZER-21/offline/selector-v2-codex-checkpoint.json`. Review selector v2 và consumer, 67 targeted tests offline PASS (19 Session +12 IO +21 runner +15 cycle); source-manifest126 pins khớp, 312 artifact ledger runtime02 khớp. Không source finding chặn trong delta v2. Chuẩn bị bản copy runtime-prep-03, đổi đúng output/admission attempt, proposal và hash pins; giữ nguyên prep02/auth/source snapshot/raw lịch sử. Chưa runtime/model/key/lab/publication/Linear write. AC01 cần trace native sau v2; AC02/child51 cần pilot B0/B1/B2+C0 riêng, không được suy từ vòng functional.


### Quyền runtime-03 — 2026-10-30T03:55:19.988169+00:00

Hoàng xác nhận rõ “Tôi cho phép runtime-03 theo toàn bộ giới hạn trên” cho proposal5f1dc0dd/manifest9fec1be9.128sourcepins đã khớp;21native fake tests/defaultPLAN_ONLY PASS. Chạy đúng một attempt900s+cleanup300s,3calls/estimate0.015USD/1send/8HTTP/2TCP/1CMreplace; Dopplerzero-door/dev chỉOPENAI_API_KEY. Source đóng băng, khôngreplay02/03 hoặc tựretry. Runtime scope và dirty hashes ở runtime-03-scope.json; chưa cấp quyềnpilot51/Gitpublication/Linearwrite.


### Runtime-03 — đối soát cuối, 2026-10-30T04:02:39.166928+00:00

Hoàng đã duyệt đúng một attempt và quyền đã dùng hết. [Receipt/đối soát](../../../evidence/ZER-21/runtime-03/README.md): preflight25mẫu PASS; nativeTCP SourceA denied=true, SourceB kubectl exec timeout15.069s (raw0085,stdout/stderr rỗng, remoteTCP outcomeUNKNOWN). WorkNOT_MET trước0model/0HTTP/0SQLi/0Gaia-Healer/0Healerreplace; 2TCP reserved/started nhưng chỉ1responseconfirmed. Selectorv2 chưa được gọi thật; không quy lỗi này cho model hoặc source khi chưa đủ evidence. Nguyên nhân exec delay UNKNOWN; không tăngtimeout/bỏisolation/tựretry.

Cleanup gốc CLEAN: owner+namespaceUID precondition/absent,2OWNEDtopicdelete+finallistempty/cùngbrokerUID, sharedspecs/UID/restarts giữ nguyên/resourceguardPASS, hai ownedJob treesclosedreaped. Tổng253.344s; khôngcleanupresume hoặc querylab thêm. Codex recomputeindependent raw/hash tại runtime-03/reconciliation.json: 128live+snapshotpins và312historicalledgerentries của02 đều khớp; unrelateddirtybytes giữ nguyên. Khôngsource/test/guardedit trong runtime; indexrỗng; khôngpublication/Linearwrite.

Source/offline selectorv2 READY, khôngfindingchặn: required_rounds/task và reasonenum/crossfield/version2 đúng, STOP vẫnNOT_MET/0laterstage.67targetedtests PASS +21nativefaketests/defaultPLAN_ONLY của prep03 PASS. Graphrefresh fullrebuild exit1 do aliascollisionzero_door với Rcheckout; metadata cònincremental-in-progress; query/context/impact/detect_changes/explain chỉnavigation khôngcompletegraph/taintclaim.

**ZER21 chưa hoàn tất:** AC01NOT_MET, AC02/child51NOT_RUN. Blocker hiện tại là nativeexec SourceB thiếucompletionreceipt; sau đó vẫn cần pilot B0/B1/B2+C0 đúng workload/evidence/guard/probe vàpublication/merge/Hoàngacceptance đểDone. Khôngghép runtimecũ thànhPASS hoặc xin thêm lượt blindretry. Mộtdiagnostic mới phải nhằm phân biệt nguyên nhân với exacttarget/budget/stop/cleanup; hiệnchưacógói/quyền đó vàkhôngruntime04.


## ZER-21 — điều tra native exec runtime-03 — 30/10/2026

Hoàng giao điều tra nguyên nhân cụ thể. Cùng HEAD a593885/branch zer-21-linked-agent-cycle, index rỗng; source và historical raw giữ nguyên. Đọc source/log Docker/containerd và lịch sử Prometheus qua GET-only, không exec probe mới, model/key/fixture traffic hoặc lab mutation. Scope/dirty hashes và phép đối soát tại [runtime-03-investigation](../../../evidence/ZER-21/runtime-03-investigation/README.md).

**Đã xác nhận CPU throttling kéo dài trong Source B; đây là hướng nhân quả mạnh nhất, root cause sâu hơn chưa chốt.** Nối đúng UID d9d88007…/container9b1728d8…: 03:58:35.919–52.009 UTC, CFS tăng161/161 chu kỳ có throttle, 2 process vẫn tồn tại qua lúc client bị cắt03:58:42.777. CPU container tăng1.272388s ở cửa sổ chứa probe; đối chứng runtime02 cùng image/50m hoàn tất1.523s với CPU delta0.075825s. Tỷ lệ chu kỳ không phải tỷ lệ thời gian; metric throttle seconds không có, thiếu PID/stack/stage markers nên chưa xác định Python/runc/kernel hay chứng minh nâng CPU sửa được lỗi. TCP Source B vẫnUNKNOWN.

API GET vẫn trả0.208s lúc03:58:38; Ready/restart/memory và containerd lifecycle không cho thấy OOM/crash trước cleanup. Resource PASS hiện chỉ kiểm memory, không CPU/CFS. Client hiện tại1.33.5-dispatcher/server1.31.5 ngoài supported skew; k3d entrypoint có vòng uncordon lỗi localhost8080. Hai vấn đề phụ chưa được chứng minh gây timeout; stdout EOF containerd lúc03:58:56 chưa nối execID với Source B. Báo cáo tách confirmed/inferred/unknown, không quy lỗi cho selector chưa được gọi.

Next: diagnostic lành riêng cho exec startup/CFS với marker unbuffered, PID/state và CPU profile có giới hạn; chưa chạy hoặc cấp quyền bằng note này. Không tăng timeout/bỏ isolation/replay03. AC01NOT_MET/AC02NOT_RUN, cleanup03CLEAN; khôngpublication/Linearwrite. 128 source pins và312+272 historical ledger entries đối chiếu lại; source không đổi nên không chạy lại product tests. Graph index vẫn incomplete, chỉ navigation.


## ZER-21 — review gói CPU của Claude — 30/10/2026

Hoàng đưa gói Claude và yêu cầu đánh giá đã gần tìm được nguyên nhân hay chưa. Review chỉ đọc source/evidence và chạy test offline; không runtime/model/key/fixture traffic/lab mutation hoặc publication/Linear write. HEAD a593885e15dc474b83590c4dcf1b214395492fcf, branch zer-21-linked-agent-cycle, index rỗng. Gói REVIEW-PACKET.md SHA ca5a7a8f745fbc2fe22211ca6b31e8ca8d5d3eb9824cc27475469ab2a61d16f7; lab76afd82a/render25a1eb5a/manifestd9a811fb. Các gói A/B đã review trước giữ source pin; lượt này retest delta C và consumer.

**Không tìm thấy lỗi code chặn trong delta CPU đã kiểm.** Retest độc lập prep03 runner28/28 +cycle15/15 PASS, key unset, fake subprocess/network; không gọi lại toàn110 test không đổi. 128 manifest pins khớp; ledger02=312/312,03=272/272,investigation=20/20 và diagnostic SHA256SUMS24/24 khớp. Tính lại raw: 270 stress exec rc0/anomaly0 (CPU>300ms hoặc wall>5s); cộng15 exec50m ban đầu thành285, không tái hiện. 15 exec500m rc0, wall0.304647–0.394013s, CPU66.235–76.633ms. Đây là bằng chứng normal-path; chưa tái hiện sự cố để chứng minh bản sửa loại bỏ nó. Chỉ 2 source limits đổi500m, requests giữ5m; isolation/timeout15s/STOP/cleanup guard giữ semantics. Gate300ms/5s phù hợp làm admission bảo thủ, không chứng minh không còn lỗi ở exec sau; không cần thêm nr_throttled làm gate vì normal50m cũng throttle.

**Đính chính mức kết luận:** sustained throttle và CPU delta bất thường là fact; cơ chế negative runtime/CPU debt là suy luận mạnh từ lịch sử, chưa được đo trực tiếp ở incident. Không gọi “kernel trả nợ20s đã xác nhận”, “500m chắc chắn hấp thụ sự cố” hoặc loại trừ mọi host transient từ metric tổng hợp. Tài liệu kernel https://docs.kernel.org/scheduler/sched-bwc.html mô tả quota/period và throttling; không tự chứng minh nguyên nhân của incident này. Khoản CPU1.27s phát sinh từ đâu vẫn UNKNOWN. Rule-of-three ~1.05% chỉ có nghĩa khi coi các mẫu độc lập/cùng phân phối; không phải tỷ lệ lỗi toàn lab. Không cần tiếp tục stress-repro để khép issue.

**Bước kế tiếp cụ thể:** chuẩn bị prep04/runtime04 riêng từ bản sửa đã kiểm; đổi output/admission attempt và repin, cập nhật proposal nêu500m,2warm-up exec,4 normal cgroup reads và timeout snapshots có trần theo deadline. Giữ nguyên authorization03 đã tiêu và raw lịch sử; không replay03. Chỉ xin quyền runtime khi gói mới review được; note này không cấp quyền thực thi. Client skew/k3d loop và nguồn CPU spike được ghi residual, chưa có bằng chứng là prerequisite phải sửa hết. Mục tiêu lượt tiếp là chứng minh functional AC01; AC02/pilot B0/B1/B2+C0 vẫn còn, không gọi toàn ZER21 gần Done từ CPU fix. Graph index incomplete/stale với delta mới, query/context không có symbol; direct source/diff +fake tests là căn cứ review, không claim complete graph/taint coverage.


## ZER-21 — prep04 hoàn tất offline, chờ exact runtime approval — 30/10/2026

Hoàng giao thực hiện bước tiếp sau CPU review. Cùng HEAD a593885e15dc474b83590c4dcf1b214395492fcf/branch zer-21-linked-agent-cycle, index rỗng. Scope trước write và37dirty hashes ở offline/runtime04-prep-checkpoint.json. Tạo riêng runtime-prep-04 gồm runner/render/lab/cycle/remote/tests/proposal/pins/approval-template(false), không copy authorization03, không tạo runtime04 output. Tất cả923 file ZER21 có trước và128 pins được đối chiếu khớp, không sửa prep03/raw/auth lịch sử. Diff hành vi mới: output/admission04 và giới hạn1 native CPU snapshot attempt/work, reserve trước read kể cả lỗi; thêm case old attempt03 bị chặn với hash/expiry mới. CPU500m,2warm-ups,4 normal cgroup reads và tối đa1 timeout snapshot đã ghi rõ proposal;15s exec/3model/8HTTP/2TCP/1SQLi/1CMreplace/900+300s/cleanup guards giữ nguyên. Không runtime/model/key/lab/publication/Linearwrite.

29runner+15cycle PASS;29runner retest sau case admission, Bash syntax/defaultPLAN_ONLY PASS. Node đọc lại128pins và923old files độc lập,0mismatch. [Gói chuẩn bị](../../../evidence/ZER-21/runtime-prep-04/README.md), review/log offline/runtime04-prep-*. Proposal SHA eccba4a333963f3655ad06e0dda43a03a3c3f26db1b9b64b72ca8c14d581bc6b; manifest SHA 9aa21e063e39fbc10414befff690a4c32bcc18a2103b462dd4193f194a358208. READY_TO_REQUEST_SINGLE_ATTEMPT_APPROVAL; chưa owner approval mới, không tạo authorization hoặc tiêu attempt. Source mitigation chưa liveverified, spike origin UNKNOWN. Next: xin một xác nhận cho đúng proposal/hash và giới hạn, chạy đúng một attempt khi được duyệt, đối soát native+cleanup; không blindretry. AC01NOT_MET/AC02NOT_RUN; không suy thành Done. Graph vẫn incomplete, review dựa direct delta và fake tests, không claim complete graph/taint.


### Quyền runtime-04 — 2026-10-30T07:03:28.084115+00:00

Hoàng xác nhận rõ “Tôi cho phép đúng một lượt runtime-04 theo toàn bộ giới hạn trên” cho proposal eccba4a33396/manifest9aa21e063e39.128pins và923old evidence files khớp;44affected tests PASS. Chạy đúng1attempt với source500m/2warmups/max5cgroupreads,900swork+300scleanup,3modelcalls estimate0.015USD, 1SQLisend/8HTTP/2TCP/1CMreplace;Dopplerzero-door/dev chỉOPENAI_API_KEY. Source đóng băng;khôngreplay04/retry/runtime05/pilot51/publication/Linearwrite. Scope/dirty hashes ở runtime-04-scope.json.


### Runtime-04 — kết quả và lỗi transport cụ thể — 2026-10-30T07:10:23.506757+00:00

[Đối soát](../../../evidence/ZER-21/runtime-04/README.md):244.204s,CPUgatePASS(A0.219s/B0.203s),2TCPdenied~0.312s;Nemesis selectorv2 realgpt-6-luna OK/370+31tokens/estimate0.0000525USD,PLANdisclose-restricted/NONE,guardaccepted. Transport exit1 trước stdin/sign/Kafkasend:ModuleNotFoundError kafka(session_cli.py:17). Render PYTHONPATH=/current đã bỏ /usr/local/lib/python3.11/site-packages; Dockerfile/referenceZER19 cần đường này. Đây là lỗi cấu hình đã bỏ sót trong review,không kết luận cachedimage thiếupackage nếu chưa kiểm nội dung.1benignHTTPconfirmed/2reserved,0SQLi/0Gaia-Healer/0replace. CPUfix vượt gate lượt này,nguồn spike03 vẫnUNKNOWN. CleanupCLEAN:namespace+2topicsabsent,brokerUID/sharedspecs+UID/restarts giữ nguyên,resourceguardPASS,ownedtreesclosed/reaped.128pins/923oldevidencefiles/unrelateddirty khớp. Quyền04consumed;khôngretry/runtime05. AC01NOT_MET/AC02NOT_RUN. Nextsource:restoredependencyPYTHONPATH vàstartupimportgate trướcmodel trong gói mới,khôngsửa consumed04;khôngcầnbuildđểsửaenv.


### Offline fix sau runtime04 — prep05,30/10/2026

Gói mới giữ nguyên consumed04:restore PYTHONPATH=/current:/usr/local/lib/python3.11/site-packages, không thay image/build/install. Thêm1exec15s runpy import-only exactremote với run_name khôngmain trướcTCP/HTTP/model; khôngkeyread/sign/ledger/Kafkaclient/network,failclosedTRANSPORT_DEPENDENCIES_NOT_READY vàcleanup. 31runner+15cycle/Bash/defaultPLAN_ONLY PASS;test đườngdependency,gatePASS/FAIL+ordering vàoldattempt03/04rejection. 128pins/1245oldfiles và302runtime04ledgerentries khớp. [Prep05](../../../evidence/ZER-21/runtime-prep-05/README.md),proposal b4fd1de3c3722bef18bf91ecd5326c05fc518196173f03fe32d1924663743ffa,manifest 5a82e96aef72e19e11a54c4358d40f715b7a3a1afc9bce817a6a1911044d4552. Chưaauthorization05/runtime05/liveimport/key/lab/model/publication/Linearwrite. Readyxin1approvalmới; khôngcoi bản sửaoffline là livePASS. AC01NOT_MET/AC02NOT_RUN.


### Quyền runtime-05 — 2026-10-30T07:14:57.968842+00:00

Hoàng xác nhận rõ “Tôi cho phép đúng một lượt runtime-05 theo toàn bộ giới hạn trên” cho proposal b4fd1de3c372/manifest5a82e96aef72.128pins và1245old evidence files khớp;46affected tests PASS. Chạy đúng1attempt với restoredPYTHONPATH/1importcheck/source500m/2warmups/max5cgroupreads,900swork+300scleanup,3modelcalls estimate0.015USD, 1SQLisend/8HTTP/2TCP/1CMreplace;Dopplerzero-door/dev chỉOPENAI_API_KEY. Source đóng băng;khôngreplay05/retry/runtime06/pilot51/publication/Linearwrite. Scope/dirty hashes ở runtime-05-scope.json.


### Runtime05 — selector Kafka không chọn source pod — 2026-10-30T07:23:59.754533+00:00

[Đối soát](../../../evidence/ZER-21/runtime-05/README.md):238.797s,CLEAN;importgate/CPUgate/2TCPPASS. Nemesis1gpt-6-luna call370+31tokens chọn disclose-restricted/NONE,guardPASS. TransportRESULT_TOPIC_UNAVAILABLE trướcproducer/send;0SQLi/0Gaia-Healer/0replace,1benignHTTPconfirmed(2reserved). Topiccreate0046/0049OK,workergroupStable0062. Defect xác nhận từbootstrap+podsnapshot: Kafka policyselectorapp=zer46-source-a nhưng podsapp=zer46-source,match0pod. Chưa packettrace đểgán lànguyênnhânduynhất;khôngbịa conntrack/timing. Namespace+2topicsabsent/brokerUID/sharedspecsUIDrestarts/resourceguardPASS/ownedtreesclosedreaped; 128pins/1245oldfiles/unrelateddirty khớp.05consumed,khôngretry06. Nextoffline:owner-scoped unique labelA vàpolicyselectAonly,regressionrenderedlabelsA/B/foreign; giữDNS/privateproxy/9092target/guards. AC01NOT_MET/AC02NOT_RUN.


### Offline selector fix — prep06,30/10/2026

Không sửa consumed05. Renderer thêmowner-scoped label chỉA,policyđòicảowner+label đó,khôngB/foreign; giữapplabels/DNS/privatepolicy/Kafkadestination9092/PYTHONPATH/importgate/CPU/budgets. Cross-render regression chọnactualpodlabels:beforeprep05 đúng1FAIL/0ERROR,after06PASS;32runner+15cycle/Bash/defaultPASS. 128pins/1568oldfiles/runtime05ledger304khớp. [Prep06](../../../evidence/ZER-21/runtime-prep-06/README.md):proposalb26192f376970994aaaa5f53b6875ffa5176bc42005334665932f7ff645dea58,manifest2dc091e426590b9b401ab5fb4e4b24b0264eda3c514b08cc39a751c6ab465ba4. Chưaauthorization06/runtime06/liveegresscheck. Không key/model/lab/publication/Linearwrite. Nextexactapproval1attempt khiđượcduyệt,khôngretry05. AC01NOT_MET/AC02NOT_RUN;khôngclaimsolecause hoặcDone.


### Quyền runtime-06 — 2026-10-30T07:28:27.046327+00:00

Hoàng xác nhận rõ “Tôi cho phép đúng một lượt runtime-06 theo toàn bộ giới hạn trên” cho proposal b26192f37697/manifest2dc091e42659.128pins và1568old evidence files khớp;47affected tests PASS. Chạy đúng1attempt với restoredPYTHONPATH/1importcheck/source500m/2warmups/max5cgroupreads,900swork+300scleanup,3modelcalls estimate0.015USD, 1SQLisend/8HTTP/2TCP/1CMreplace;Dopplerzero-door/dev chỉOPENAI_API_KEY. Source đóng băng;khôngreplay06/retry/runtime07/pilot51/publication/Linearwrite. Scope/dirty hashes ở runtime-06-scope.json.


### Runtime06 — Kafka/SQLi chạy được,join precision và memory stop — 2026-10-30T07:38:45.522754+00:00

[Đối soát](../../../evidence/ZER-21/runtime-06/README.md):245.110s,CLEAN. CPU/import/2TCPPASS; 1Nemesis realcall370+31tokens/estimate0.0000525USD,MAX_ROUNDS1;transport0,workerSUCCESS1SQLi. Nativeaccessraw0114joinID/source/HTTP200/3rows3restricted.0Gaia-Healer/0replace. Có2blocker độc lập:memoryPSI7.06>5 dùhost/WSLavailđủ;pureproject_worker trênactualdata rejectNATIVE_WORKER_ACCESS_JOIN vìGoobservedAt.871Ztruncmilli<raw.871327Z. Controlcopyclampmemoryonlypasses,khôngsửareceipts/acceptance. CyclechỉghiValueErrortype, khôngchốt memorylàfirst/solecause;commentarybanđầuđãđínhchính. Cleanupnamespace+2topicsabsent/sharedUIDspecsrestarts/resourceguardPASS/ownedtreesclosedreaped. 128pins/1568oldfiles/unrelateddirtykhớp.06consumed;khôngretry07. Nextofflinefixknownmillisecondinterval+boundarytests,giữmemoryguard. AC01NOT_MET/AC02NOT_RUN.


### Precision fix offline — prep07,30/10/2026

Gói source-only không sửa consumed06:canonicalGo.dddZ observedAt làinterval[observed,observed+1ms),upperexclusive; giữrawts/IDUID/source/count/window/ageguards,khônggenericclocktolerance/pressurethresholdchange. 34runner+15cycle/Bash/defaultPASS;before06regression2expectedValueError/0assertionfail;actualraw06pureprojectionPASSgiữts.871327. 128pins/1906oldfiles/runtime06ledger318khớp. [Prep07](../../../evidence/ZER-21/runtime-prep-07/README.md),offline/runtime07-prep-review.json. Chưa xinapproval07/chưaruntime;nextreadonlyresourcepressurediagnosis/condition,tránhblindretry. MemoryPSI7.06vẫnvalidguardstop,nguồnspikeUNKNOWN. Khôngsửaactualacceptance;AC01NOT_MET/AC02NOT_RUN.


### PSI mitigation và quyền runtime07 — 2026-10-30T07:59:20.931562+00:00

Hoàng cho phép điều tra/khắc phục PSI và đúng1runtime07 trong project. Không xin lại quyền đã cấp. Readonlydiagnosis:pressure thật/noOOM/sampledlimitfail0,heap384MiB bịinherit sangadminCLI;task-leveloriginUNKNOWN,khônggánTHP/Kafkalàsolecause. Prep07capchildJVM16–128MiB+fixed30s/7memorysamplesPSI<=1 trướcTCP/HTTP/model+vmstat cùngread4s;guard5/hostWSLmin/CPU/traffic/model/deadlinecleanup giữ.52offline testsPASS/oldsource2expectedassertionfails.128pins,318runtime06ledger và1901priorfilespreserved. Proposal30a1c049de9f57274fb2eae00b108c2282dce411d7d828a65dbdeba9a8638ff8/manifest7a604999e43a3ee0c524d044e4064dbf1a9b7d13bb31dfa66e32b21abdf882a8. Sourcefrozen,authorization ghi đúng usermessagevàhashthựctế,khôngclaimownerđãgõhash. Khôngretry/pilot51/publication/Linearwrite. Đọc runtime07 started/acceptance/cleanup trướcresume.


### Runtime07 — AC01 technical functional PASS,cleanupCLEAN — 2026-10-30T08:27:37.613634+00:00

[Receipt](../../../evidence/ZER-21/runtime-07/README.md):384.391s,3realgpt-6-luna calls1686+157tokens/estimateUSD0.0002471,nofallback. NemesisMAX_ROUNDS1→signedKafka/GoSUCCESS1SQLi→nativeUID/ID/IPjoin→RULESDETECTED→GaiaLLMdiagnosisOK→HealerLLMBLOCK_IP/guardACCEPT/1replace→A403+B200/201/200/200/404,actioncompleted.8HTTP/2TCP/4CPUreads,notimeouts. Memorysettle7samplesPASSmax0.12;all72work+1cleanupPSImax0.36<5,hostWSLminPASS. ChildCLIheap16–128MiB/settlemitigationlivepass;PSI06uniquetaskcauseUNKNOWN,notcausalABproof. CleanupnamespaceUIDabsence/2OWNEDtopicsabsent/samebrokerUID/sharedspecUIDrestartpreserved/resourcePASS/ownedtreesclosedreaped.128pins/1901priorfiles/unrelateddirtypreserved;indexempty.07consumed,no08/retry. AC01hastechnicalfunctionalevidence;AC02pilot51NOT_RUN,notformalDone/publication/Hoàngacceptance/Linearwrite/KPI. Nextfinishexistingpilotpackageandrequiredreview/publication,notmorefunctionalstressrepro.


### AC02/child51 source package — 2026-10-30T08:49:00.479463+00:00

Hoàng yêu cầu hoàn thành phần còn lại để khépissue sauAC01runtime07PASS. Newscope ZER51/scope.json khóaHEADa593885/branchzer21linked/2450oldfiles;writerZD4. SáucellB0/B1/B2xSQLiC0 xen kẽ,operatorfixedplan/noNemesisinference;B1actualHealerobservation/actionguard+ModeGate+SqliContainment/State,sameprobeB2. B0nohealAPI/key/model;B1nokey/model. Operationalinvarianthash phải paircase,rawidentityđượcgiữkhácnhaukhôngclaimbyteidentical.17offline testsPASS/Bash/default/compile,135pins/517runtime07ledgerkhớp. Reviewagentsmỗibêntrả1findingrồidừngquota:missingthreading vàpartial403misscoređãsửa;roothoàntấtfullseamreview,khôngclaimindependentREADY. Actualseamtestcònbắtcycleimportpathđãsửa. Source-review/proposal/hashatZER51. Onebatchmax6cells/4modelUSD.02/48HTTP12TCP6workersends3SQLi/max4replace/6namespaces12topics/3600s,600work300cleanup,khôngretry/sharedmutation/publication/Linearwrite. Authorization ghi đúng taskintent,inferredscopekhôngclaimownergõexacthash. AC02NOT_RUNtạicheckpoint;đọcstarted/progress/acceptance trướcresume.


### Pilot01 dừng ở cleanup/sharedrestart; prep02 chờ quyền — 2026-10-30T09:06:42.752282+00:00

[Batch01](../../../evidence/ZER-51/runtime-01/README.md):606.641s,0model,16HTTP4TCP1SQLi1replace. B0C0businessPASS/noheal/CLEAN;B1SQLiRULESblock/actioncompleted/businessPASS nhưngcleanup topiclist10stimeout. BatchINCOMPLETE,4cellNOT_RUN,noreplay. Cleanupresume trong300sgốc namespace+2topicsabsent/resourcePASS/sharedspecUIDpreserved,sharedrestartfalse cartservice51→52;originalINCOMPLETEgiữ. EventKillinglivenessgRPCtimeout1s,causeoflatencyUNKNOWN/notOOMclaim. CurrentcartReady,no sharedmutation.823ledger01+517runtime07+oldsourcepinskhớp,indexempty. AC01functionalPASSgiữ/AC02NOT_MET. [Prep02](../../../evidence/ZER-51/runtime-prep-02/README.md):19offline testsPASS/144pins,pureCASpatch2timeoutcart1→3s+fresh6cellbaseline,scope4model/.02USD48HTTP12TCP3SQLi/max4replace/6namespaces12topics/300sbaseline+3600sbatch;khôngraisePSI/Kafka10s. Proposald19555dc7127/manifest2c18162337fb,templatefalse/noauth/no02output. Cầnownerduyệtmớivìsharedrolloutngoàigói01vàattemptconsumed. Publication/review/merge/Hoàngacceptanceremain;noLinearwrite. Revieweragentsquotaendedafterfindings,rootcompletedseamreview;notindependentREADY.


### Quyền baselinecart+pilot02 — 2026-10-30T09:08:55.124982+00:00

Hoàng xác nhận rõ “Cho phép rollout cartservice và một pilot mới theo toàn bộ giới hạn trên” cho proposald19555dc7127/manifest2c18162337fb.144pins/823pilot01ledger/517runtime07ledgerkhớp,indexempty. Cho phépduynhấtcartprobe2field1→3sUID/RVCAS/300srollout,rồifresh6cellpilot3600s/max4modelUSD.02/48HTTP12TCP3SQLi3benign/max4replace/6namespaces12topics+cleanup;600work300cleanup/cell. Sourcefrozen,no retry/build/sharedothermutation/publication/Linearwrite. Scope/runtime-02-scope.json;đọcbaseline/started/progress/acceptance trướcresume.


### Baseline02 bootstrap trước effect lỗi; retry bị auto-review từ chối — 2026-10-30T09:11:45.321779+00:00

Hoàngduyệt exactsharedrollout+onepilot02đãghi. Firstownedbootstrap failedModuleNotFoundErrorhttpx vìparentthiếuPYTHONPATHkhiTreechọnphysicalPython;rawrỗng/patchintentabsent/0lab0model/cartchưapatch/pilot02absent. Originalworker.log/acceptancegiữ. Correctedlauncher dùngreviewedrun.child_env(nokey,removeINDEX);inertimportphysicalPythonPASSoffline. Automaticapprovalreview rejectedbeforeCreateProcess:khôngretrytrongquyềnrolloutkểcảchưaKuberneteseffect. Khôngworkaround. Chuẩnbịhelperrequireexplicitretryapprovalfilemới+300sdeadline/exclusivemarker;filechưacó. Nextxinđúng1bootstrapretry,chỉsauReady thì1pilot02cũ,khôngtăng4model/.02USD48HTTP12TCP3SQLi/max4replace.144pins/823pilot01ledger/indexemptykhớp. AC01PASSgiữ/AC02chưađạt,noGitpublication/Linearwrite.


### Explicit bootstrap retry approval — 2026-10-30T09:12:26.919321+00:00

Hoàng xác nhận “Cho phép đúng một bootstrap retry và pilot-02 theo các giới hạn trên”;sameproposal/manifest144pins,nativeimportofflinePASS,rawempty/patchintentabsent. Mởđúng1bootstrapretryvới300sdeadline mới,khôngthêmquyềnsourceretrysauđó;onepilot02sauBASELINE_READY,cáctrầncũgiữnguyên. Originalbootstrapfailure/auto-reviewrejectionbảotoàn.


### Pilot02 dừng vì watcher shutdown race;fix03offline — 2026-10-30T09:31:59.380921+00:00

Baselinecartprobe3sREADY sauexplicitbootstrapretry;bothpilot02cleanupCLEAN/sharedspecUIDrestartspreserved.593.437s,0model16HTTP4TCP1SQLi1replace;B0C0complete,B1SQLiRULESACTION_COMPLETED/nativebusinessPASSnhưngoriginalworkNOT_MET. raw0237return0 rồiGUARD_OR_CLEANUP_RESERVE:[] trùngmainnormalstop,khôngcartrestart/PSI. Actualmain cũstop.settrướcwatcherjoin;deterministicreprooldstopfirstfail. Newprep03watch_shutdown riêng,drainread<=20srồistop;genuineMEMORY_STOP/stuckthreadvẫnFAIL.23offline tests/Bash/defaultPASS,154pins/800runtime02/823runtime01/517runtime07ledgerkhớp,indexempty. Proposal6f47a08a6890/manifestaf01409640a1,authfalse,no03output. Chỉđềnghị4never-runcellsB2C0/B0SQLi/B1C0/B2SQLi,max4modelUSD.02/32HTTP8TCP2SQLi2benign/max3replace/4namespace8topics/2400batch600work300cleanup;no sharedpatch/noreplay2oldcells. OriginalB1guardfailure giữ,protocoldeviationnêu;không6allPASS/KPI. Cầnownerapprovalmớivìpilot02consumed/no retry;noGitpublication/Linearwrite. AC01PASS/AC02NOT_MET.


### Quyền continuation03 — 2026-10-30T09:33:37.258820+00:00

Hoàngduyệt “Cho phép continuation bốn ca theo toàn bộ giới hạn trên” cho proposal6f47a08a6890/manifestaf01409640a1.154pins/823+800+517historicalledgers/baselineledgerkhớp,indexempty. Chỉ4never-runcells B2C0/B0SQLi/B1C0/B2SQLi,max4modelUSD.02/32HTTP8TCP2SQLi2benign/max3replace/4namespaces8topics/2400sbatch600work300cleanup;baselinecart3sunchanged/no rollout/no replayfirst2/sourcefrozen/noretry/build/sharedmutation/publication/Linearwrite. Sourcefixwatch_shutdowndrainbeforeguardstop,realguardsunchanged. OriginalB1failuregiữ. Scope/runtime-03-scope.json,đọcstarted/progress/acceptance trướcresume.


### Continuation03 hoàn tất; chốt evidence AC01/AC02 — 2026-10-30T10:03:13.428125+00:00

Outcome ZER-21/51: chỉ reconciliation/handoff offline sau lượt continuation được Hoàng duyệt; không mở thêm runtime. HEAD a593885e15dc474b83590c4dcf1b214395492fcf, branch zer-21-linked-agent-cycle, index trống; giữ dirty ngoài scope. [Pilot comparison](../../../evidence/ZER-51/pilot-comparison/README.md), reconciliation.json và final-verification.json là đầu vào review.

Bốn ca mới B2/C0, B0/SQLi, B1/C0, B2/SQLi hoàn tất trong 1200.157s, work/cleanup exit0, cả bốn CLEAN, không shared rollout/retry. 3 model calls / 1923 input + 205 output / estimate USD0.0002948; 32HTTP/8TCP/2SQLi+2benign/1replace. Quyền continuation consumed. Watcher shutdown fix không còn tạo false guard ở bốn ca này; genuine guard không được nới.

Gộp đúng hai ca runtime-02 và bốn ca runtime-03: sáu native observations, whole-trial success 5/6, sáu cleanup CLEAN. Giữ nguyên B1/SQLi NOT_MET do shutdown race mặc dù native BLOCK_IP/containment/business probe đạt. RULES chọn đúng BLOCK_IP/NO_ACTION; B2 SQLi chọn BLOCK_IP, B2 C0 Gaia ABSTAIN và không có correct first action theo locked scoring. Không force model tránh abstain, không replay/drop failure. Operational evidence/workload/guard/probe/HPA hashes đối ứng khớp, IDs/IP/time gốc giữ riêng; protocol deviation sau watcher fix được ghi rõ.

Ledger cuối: runtime07 517, pilot01 823, pilot02 800, pilot03 1443 entries cùng baseline/comparison đều khớp; prep03 154 source pins khớp. 23 pilot/watcher/baseline tests và 31 selector Session/IO tests đã PASS ở checkpoint tương ứng; không gọi kiểm hash là test runtime mới. AC01 technical functional PASS; AC02 pilot evidence present with disclosed failure/abstention, pending review/owner acceptance. Không claim AI superiority/formal dataset/KPI/Boutique recovery hoặc formal Done.

Phần còn lại: full independent final review chưa có (review agents trước đó hết quota sau finding; root đã sửa/retest nhưng không tự ghi independent READY), publication/CI/merge và Hoàng acceptance. Đã có local PR draft và exact file inventory; chưa có quyền commit/push/PR/merge/Linear write. Không stage toàn NOW do mixed issue history. Publication phải giữ byte/hash của evidence Windows (CRLF), không normalize hoặc sửa ledger lịch sử.


### Review cuối ZER-21/51 đã chốt — 2026-10-30T15:33:03.768017+00:00

[Final review](../../../evidence/ZER-51/pilot-comparison/final-review.md) và final-review.json: READY_FOR_TECHNICAL_ACCEPTANCE, không có finding chặn mới. Ba reviewer độc lập selector/measurement/lifecycle đều READY; root raw AC01 và 3615 ledger +154 pins/5632 ZIP entries khớp. Selector31/31 +focused watcher4/4 PASS; credit full23 suite trước. HEAD a593885e15dc474b83590c4dcf1b214395492fcf/branch zer-21-linked-agent-cycle/index trống; giữ unrelated dirty, không sửa product hoặc lab/model/publication.

AC01 technical PASS; AC02/child51 AC01 technical PASS cho pilot có giới hạn công bố. Sáu ca đã chạy, 5/6 whole-trial success, sáu cleanup CLEAN; B1 NOT_MET và Gaia C0 ABSTAIN giữ nguyên. Không cần runtime thêm. Không claim statistical superiority/formal dataset/Boutique recovery/KPI hoặc complete fresh graph/taint coverage. Formal Done còn publication/CI/merge/Hoàng acceptance; chưa Git/Linear write. ZIP frozen trước review giữ nguyên, báo cáo cuối là addendum. Next quyền publication/nghiệm thu theo Hoàng, không mở lại kiểm đã đủ AC.
