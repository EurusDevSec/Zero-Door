# ZER-23 — technical acceptance evidence

Live issue: https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc

Current review, 03/11/2026: **READY for technical acceptance/publication**, with the failed live CANCEL case preserved. This is SQLi-only host-composed integration through actual private Kafka, not a deployed autonomous service integration or a formal experiment. Merge and Hoang's acceptance remain separate Done gates.

| AC | Evidence and actual result | Boundary |
| --- | --- | --- |
| AC-01 versions/config | runtime-prep-02/source-manifest.json pins143 exact source/config files; runtime02/source snapshot, cached image admissions, workload UID/spec, model/prompt/version/usage receipts | Exact cached artifact reproduction; original worker complete build-context unavailable, only3 historical source pins attested. CI Git newline normalization is recorded separately from as-executed bytes. |
| AC-02 whole SQLi path | Real Nemesis selector -> signed Kafka/Go worker -> delivered3 restricted rows -> native Gaia reader/LLM diagnosis -> exact authenticated Kafka packet/receiver claim -> guarded Healer action -> attacker403 and benign CRUD200/201/200/200/404 | Independent native access/request/response/fixtureUID joins; no alert injection or /heal/trigger. Fixture containment/business only, no Boutique incident-recovery claim. |
| AC-03 benign/failure/stop/cancel/cleanup | C0 native control PASS; Gaia ABSTAIN and no handoff/Healer/policy write. Actual memory guard stop retained. Actual Session pre-send and in-flight transport cancellation, broker failure/tamper/replay tested offline. All owned resources ultimately CLEAN | Live CANCEL did not reach its intended cancellation. Original cleanup INCOMPLETE remains unchanged; separately recorded cleanup-only continuation CLEAN. No success/accuracy relabeling. |

## Results retained

- runtime-01: NOT_MET at NetworkPolicy admission, zero model/traffic/resources, cleanup CLEAN. Not replayed.
- Specific one agent restart approved by Hoang and executed once; BASELINE_READY in47.016s,19 native pod firewall hooks restored,3PVC/deployment specs preserved. Server not restarted. Stale cached node-IP inference is consistent with upstream code and recovery; no in-memory cache inspection proves the complete cause.
- runtime-02 SQLI: observed full pipeline,3 model calls,8 HTTP/2TCP/1 ConfigMap replace, cleanup CLEAN. Action act_9e2ce160172d4d94ad7283a3b95f3b31.
- runtime-02 C0: observed benign business control,1 model call,8 HTTP/2TCP/0write, Gaia ABSTAIN (INSUFFICIENT_EVIDENCE), Healer NOT_RUN, cleanup CLEAN. Not counted as correct NO_ACTION.
- runtime-02 CANCEL: NOT_MET before model/fixture traffic, genuine MEMORY_STOP. Host available671129600bytes<1GiB; VM2301268KiB and PSI0 passed. This identifies the failing predicate, not the culprit process. Original resource guard blocked topic deletion; namespace absent/specs and restarts preserved. Cleanup-resume-01 failed before lab actions on Python import; corrected bootstrap cleanup-resume-02 passed unchanged guards, verified exact3 owned topics absent, CLEAN/process closed and reaped. No runtime case retry.
- Batch acceptance.json remains NOT_MET. Root final-audit.json reports AC_EVIDENCE_READY_WITH_DISCLOSED_FAILURES, not batch success or Done.

Actual total:4 model calls,2331 input/253 output tokens, USD0.0003596 historical estimate (not billing);16 HTTP/4TCP/1 replace, within proposal caps. No further lab/model run is needed for this issue's acceptance surface.

## Verification and sharing

[Final review](final-review.md), [raw reconciliation](final-audit.json), [110-test offline verification](offline-verification.json), [clean Git-source16-test verification](clean-ci-verification.json).

[evidence-bundle.zip](evidence-bundle.zip) preserves the original raw receipts, all failures, authorization/proposals, policy diagnosis/recovery, both runtime source snapshots and cleanup continuations. Paths such as runtime-02/SQLI/ inside this document are paths under docs/evidence/ZER-23/ in that archive. [artifact-sha256.json](artifact-sha256.json) records every archived entry and published summary hash; extract without newline conversion and verify SHA256 before use. The consumed runtime-prep-02 README/proposal and old pending checkpoints are immutable historical snapshots; this README is the current interpretation. Do not rerun a consumed packet.

Five historical runner dependencies are published verbatim from the already accepted PR39 archive solely to make CI imports reproducible. Tests block network/process calls; no provider/lab calls in CI.

Limits: host-composed Gaia/privateKafka/Healer, not deployed main.py consumers/R1 authenticated O archive; no clock-sync/KPI/RQ2 superiority or Boutique recovery claim. Host-only HMAC key was not retained, so posthoc MAC recomputation is unavailable; exact packet hash/claim/native broker joins and executable receiver checks were verified. The cached worker full source-build provenance gap remains disclosed. Publication/CI/merge and owner acceptance are tracked separately; no automatic Done from a successful probe.
