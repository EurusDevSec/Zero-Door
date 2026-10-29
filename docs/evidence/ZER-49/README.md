# ZER-49 — Gaia evidence → real LLM diagnosis

**Technical PASS / independently reviewed; publication/CI/merge/Done pending at packaging.** Owner approved one corrected inference and conditional publication in authorization-02.json. Live issue: [ZER-49](https://linear.app/zero-door/issue/ZER-49/noi-evidence-vao-chan-djoan-llm-cua-gaia). Prerequisites ZER-48/ZER-10/ZER-7 read back Done; no other issue opened.

Base9b5287c140d704b8009f6dfe53f31f720b4b23a4, branch codex/zer-49-gaia-diagnosis. [Scope/dirty baseline](scope.json), [6product pins](source-hashes.json), [19inference02 pins](inference-prep-02/source-manifest.json), [exact executed snapshots](source-snapshots.json). Current SQLi-only owner scope governs; no new attack method/payload, lab/deploy or shared infrastructure mutation.

## Acceptance matrix — AC01

| Required behavior | Check and actual result |
| --- | --- |
| Observer metric/log reaches diagnosis | Actual Gaia polling/Detector with fake telemetry creates pinned O sample; same Diagnoser used in integrated background path and standalone CLI. Real inference02 returns APPLICATION_ERROR with correct evidence reference. |
| Incident keeps evidence, diagnosis, latency | [inference02 raw/conclusion](inference-02/README.md): metric log_pattern_match1/threshold0 plus full error log, structured SQLite-lock/HTTP503 diagnosis, context/incident/decision/causation join, model6.140s/diagnosis6.203s. |
| Detection before inference; MTTD unchanged | DETECTED published before scheduling; frozen timestamp preserved. Offline slow-model and slow-disk tests show next alert can be published while inference/evidence writer waits. No MTTD/scorer change; replay approval gap is not latency/KPI. |
| Failure and stop remain honest | JSON/action/ref errors, missing log/metric/context,429/timeout/refusal/UNKNOWN, cancellation, shared budgets and duplicate/restart admission covered offline. UNKNOWN stays ABSTAIN, no action/fake fallback success. [Inference01](inference-01/README.md) retains NOT_MET/ABSTAIN. |
| Bounded real model/cleanup | Exactly1call02/attempt1/0retry;653input+86output,usagecomplete,nooverage,0.0001083USDestimate. Owned childexit0/reaped6.859s,HTTP resources closed;0lab/fixtureHTTP/TCP/build/apply/restart. |
| Review and publication | [Independent source/wrapper/raw review](independent-review.md) READY_FOR_SCOPED_PUBLICATION. [Publication package](publication-package.md); CI/merge/Done remain separate until actually completed. |

56 original test methods PASS (18Gaia+4event-agent+22adapter+6runner+6CIboundary) and R1 baseline checker PASS. The corrected runner02 adds7 focused validation executions, including prior-cleanup admission and native Windows timeout/interrupt kill/reap. No repeated product suite or new lab was needed after unchanged product pins. Logs are retained.

## Behavior and boundaries

Default Gaia makes no model call. Explicit ZD_GAIA_DIAGNOSIS_CONFIG / ZD_GAIA_DIAGNOSIS_OUTPUT and matching R1/B2 context enable a run-scoped functional diagnoser. Publish DETECTED first; bounded background tasks preserve the polling path. Evidence write/flush/fsync uses an owned thread, drained on cancellation before journal close. Configuration/budget shared per run; exclusive output marker prevents automatic replay/restart.

Closed output schema allows diagnosis data only. Model references must match the observed event; no generated action/shell/healer dispatch. UNKNOWN maps toABSTAIN; malformed/refused/failed calls never become accepted diagnosis or fallback success. The local incident/LLM_CALL/ANALYSIS records explicitly do not establish authenticated O-archive delivery.

Input02 is **synthetic application-error functional evidence**, captured through actual Gaia functions using a fake Elasticsearch result and socket guard. It is not a real lab error/attack effect, deployed-agent proof, G3/G4, KPI or formal benchmark. Expected classification is protocol-side, not injected into observation. Prompt/model/schema stayed unchanged between01/02. DECTECTED04:52:08Z to diagnosis05:27:50Z includes owner approval/replay delay, not MTTD; monotonic model/diagnosis intervals are recorded separately.

The first prepared input was only a sentinel, so real model correctly abstained. [Inference01 NOT_MET](inference-01/README.md) remains intact. Owner approved one distinct corrected attempt;02PASS does not rewrite01. Across both separately approved calls:1310input+173outputtokens,0.0002175USDestimate,not verified billing. No call03.

Doppler existing primaryR routing supplied credentials only to child environment; no key printed/persisted/auth/config changed. Async30s is cooperative under disk I/O; outer owned native process waits40s and finally kills/reaps≤5s on timeout/interruption/waiterror. Forced stop or missing receipt remains UNKNOWN, not proof no provider request. No extra inference/lab is required for this accepted functional scope.

GitNexus index was stale/incomplete/FTS missing; empty impact/query/taint/PDG results do not provide coverage. Complete changed source/new files/shared adapter/Detector/contract/direct consumers and tests were read directly. No complete graph/taint/PDG claim or heavy reindex.
