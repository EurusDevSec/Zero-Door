# Independent review — ZER-49 source and one-call package

Reviewer: /root/zer19_runner_review03. **READY_FOR_OWNER_APPROVAL**, no remaining blocking findings. Read-only source/hash/diff/log review; reviewer did not call model, lab or rerun tests. Base/HEAD9b5287c140d704b8009f6dfe53f31f720b4b23a4, local17pin manifestcf47fcc57951921556e9aaa63edaa71130aefe3810a53c82ee7aa081e544397a.

Covered all6product paths, actual polling/startup/shutdown, diagnosis/CLI, Docker/CI, shared Detector/Adapter/RunBudget/contract and direct consumers; then generator/fixed input/origin, wrapper, tests, proposal and PASS conditions.18Gaia+4event-agent+22adapter+6runner+6CI-boundary tests and baselinechecker logs verified as separately run by implementer. Graph/taint/PDG incomplete/stale, not complete coverage.

Two findings fixed and retested before READY:
1. Synchronous sink/fsync could block detector eventloop. Diagnoser.record now moves sink to owned thread, shield/drains on cancellation before journal close. Slow-disk test verifies next detection proceeds, cancellation during pre-call persistence dispatches0providercalls.
2. Wrapper cleaned child only on TimeoutExpired. run_child now uses finally to kill/reap live owned child for timeout, KeyboardInterrupt or wait error. Native Windows regression confirms interruption/timeout/completion cleanup.

DETECTED published before scheduling inference and ts_event preserved; scorer/MTTD untouched. Defaultdisabled and explicit R1/B2 activation, closed output/evidence joins, shared run budget, no actions/retries/fallback-success, exclusive run marker. Local journal not authenticated O archive. Input is synthetic benign functional evidence, not real lab telemetry or integration benchmark.

Wrapper defaultPLAN_ONLY, exact owner approval/proposal/manifest required,17pins match, source drift refused, inference01exclusive/no02.40s child timeout/kill/reap5s covers cooperative30s asyncio/localIO limit; no server-side cancel/billing cap claim. PASS requires real structured diagnosis, correctID/time/causation,1trace/attempt,completeusage/budget and reaped child. Refusal/ABSTAIN/UNKNOWN remain notPASS. No lab/deploy/action/G3/G4/KPI claim.

Final proposal SHA34fa4f581af2274024f9f86bd18b2c0f82da80eb5c64effba51e3bbf73931926; runnerf16aadc6f18291fc7b85ef3a15d6afdc894f1464fd207aa32efccb298f10b3cb; runner test72b75bba056f0b3c2ecffd089a543ab516679f1884a36ea69ed97d9f73013f2b. Six product hashes in source-hashes.json. Authorization and inference01 absent at review; no inference/publication/Done. This review authorizes asking owner, not executing instead of owner.

## Inference01 review — NOT_MET confirmed

Same reviewer verified17pins and exact authorization/receipt/events:1call/1attempt/0retry,657+87tokens,3.079s,0.0001092USDestimate; context/IDs/DETECTEDtimestamp correct, receipt and event match. Actual diagnosisUNKNOWN/ABSTAIN/INSUFFICIENT_EVIDENCE, fallbackfalse/proposalnull. Sentinel-only positive input lacked an application-incident signal; abstention is justified, not PASS. No transport/schema failure established or RAM attribution. Childexit1/no timeout/reaped,3.562s; no publication gate. Raw01 remains unchanged.

## Continuation02 review — READY_TO_REQUEST_ONE_NEW_ATTEMPT_APPROVAL

Read-only review verified19pins02 and17pins01, wrapper/input/proposal and7runner02offline test log. Input02 specifically describes an application error; provenance synthetic outside observation; expectedAPPLICATION_ERROR only in protocol/checker, no groundtruth instruction injected into observation. Actual Gaia polling/Detector generated the sample with sockets blocked. Product6pins, prompt/model/schema unchanged. New run/trial/incident, prior01NOT_MET/1call/PROCESS_REAPED gate, exactnewapproval, output02exclusive/no03. Envelope unchanged:1call/256output/0retry/9472reservation/0.005USDestimate/40sownedchild andcleanup. Input clarity is not a guarantee of model success. UNKNOWN/ABSTAIN/failure remainsNOT_MET. No authorization02/inference02/inference03 at review.

Proposal SHA f29190565163bf2c6655c96a4847b608b1eaed8f77db1a5994db688c9670c6aa;19pin manifest02 SHA90a97fda6a6d542ad913ae63751d1bb536083835f00ba216d39c6da8bcd88f2e;wrapper02 SHA82d802fa8c639447d02e17df1e090040072467e6dcbc218318485a06572bead1. Reviewer did not invoke model/lab/test execution; no remaining blocking finding for asking owner.

## Inference02 review — READY_FOR_SCOPED_PUBLICATION

Reviewer /root/zer19_runner_review03 read/hash verified all19pins02 and17pins01, exact authorization02/proposal/manifest, observation/events/receipt/causalIDs/usage/budget/cleanup. One realcall02/attempt1/0retry, gpt-6-luna,653+86tokens/0.0001083USDestimate,model6140ms/diagnosis6203ms. APPLICATION_ERROR summary supported by SQLite lock/HTTP503 synthetic sample, not malicious-activity claim. DETECTEDtimestamp unchanged; replay/approvalgap is not MTTD. NO_ACTION/proposalnull/fallbackfalse/localonly/benchmarkfalse. Nativechildexit0/no timeout/reaped6.859s.01remainsNOT_MET/ABSTAIN/reaped;2calls approved separately, no03/lab. No blocking findings; no additional inference/lab needed. Done still needs approved scoped publication/CI/review/merge and ownerconditionalacceptance. Reviewer did not execute model/lab/tests.
