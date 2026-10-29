# ZER-19 — independent review

Verdict: READY_OFFLINE / READY_TO_REQUEST_AUTHORIZATION. Reviewer /root/zer48_review, read-only against HEAD/base093e924000861da3096185427994d9ea736df36d and final9 source pins in source-hashes.json. No provider/lab/build/publication actions.

Four confirmed findings were fixed and independently rechecked:

1. HIGH: Kafka high-level metadata/position APIs could retry forever and cancellation drained a stuck thread. Replaced by pinned low-level metadata cache polling in finite ticks/absolute5s and public end_offsets with finite2000ms request/retry limit, concrete seeks, auto_offset_reset none. Actual pinned Fetcher retry probes on both production environments terminated around31ms for a30ms test bound. GroupNone/no auto commit avoids group cleanup loop.
2. MEDIUM: publish-images still used narrow Nemesis context after Dockerfile began copying shared package. Both image-smoke and publish contexts now match shared root + explicit Dockerfile; regression resolves COPY source paths from both contexts.
3. MEDIUM: direct image CLI import could not find /nemesis; importing main first masked it. PYTHONPATH now includes / and image smoke calls PLAN_ONLY CLI before main. Host module import/PLAN_ONLY and source/context checks passed; actual image build remains CI gate.
4. HIGH: full Session.stop during executor metadata setup did not propagate into executor and could send after stop. Added request_stop interface and dispatch lock. Full-session metadata/offset setup tests verify CANCELLED_BEFORE_SEND,0send/0completedround; post-publication stop keeps bounded result collection. Cancellation never invents remote cancellation or refunds budget.

Reviewer reran12 IO cases on each production pin,24passed, after final topic-isolation delta. Its first fixed-source stop recheck accidentally used a wrapper omitting request_stop; correcting the probe to preserve the actual production interface yielded expected0dispatch. That wrapper failure is not reported as a remaining product defect or a successful pre-fix regression.

Additional source checks: only registry IDs and existing guard authority; closed fresh O projection/evidence references; no H/raw result in model feedback; shared budget/round/deadline/usage handling; durable claims retain unknown sends; callback failures do not become PASS; no benchmark endpoint weakening; no new payload/executor/vector. Functional topic pair is derived from validated run context and never accesses formal attack.commands/results.

Graph limitation: index points to primary9567830, incompleteincremental-in-progress, FTS absent. No complete graph/taint/PDG review claimed; direct source and empirical tests supplied evidence, owner instruction avoided a heavy refresh merely for checkpoint.

Prepared runtime artifacts/proposal were then independently checked: six exact source projections; scope/config hash; initial policy disabled/fixture safe; four cached workloads withNever pull; isolated topic pair; no new RBAC/PVC/embedded Secret contents. READY_TO_REQUEST_AUTHORIZATION only. All runtime helper source must be checked/pinned before first mutation. No actual Nemesis model→executor runtime proof, authenticated archive, benchmark, effect/recovery/KPI/G3/G4 or Done established.

## Approved runtime helper review

Hoàng approved exact completion proposal; completion-authorization.json records answer/sha. Read-only cache/nodes inventory found4image tags present on Docker/node. Helper13offlinechecksPASS and independent reviewerREADY_TO_EXECUTE after atomicnamespace/foreigntopic/regex/failuretraceharvest fixes. run.pySHA256a25e7b355502db6e145affbab65be2e886537330509edddb0c53ddcd30b1d629; source-manifest.json locks actual helper/source/config. No runtime PASS inferred. Native retained Popen handles bound child work; stop-file wrapper signals ownCLIprocess; failuretraces captured beforeUIDdelete, unknown topicownership never deleted. Worker starts onceafter privateenable; exactenabledpolicycopy forCLI avoids staleConfigMap projection, stillrevalidatedunchangedguard.

## Correction — unsafe reviewer probe mutation

The earlier helper claim of zero lab mutations was wrong: a reviewer namespace-race probe mocked apply/get but not nativePopen; an import/edit race afteratomiccreate causedone realnamespacecreate. Root audited UID/timestamp/runlabel, preservedunsafeprobe/receipts, thenUIDdeleted theemptyownednamespace and verifiedabsent. NoPods/model/HTTP/topics/Secrets. Runtime01hadstoppedNAMESPACE_PREEXISTS beforeanycomponent. OriginalNOT_MET/INCOMPLETEretained; see runtime-01/incident-conclusion.json. Both scratchprobe and offlinecheck runner nowdeny nativeexternalclients;15testsPASS. This invalidates the historical zero-mutation claim, not a runtimeACpass. runtime02 requiresnewownerpermission and newexclusiveattemptgate.
