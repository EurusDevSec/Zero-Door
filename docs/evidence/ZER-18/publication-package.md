# ZER-18 publication package — owner decision pending

Outcome: nonblocking decision consumer with bounded persistent outbox, validated ack/dedup/cooldown/retry, failclosed configuration, owned shutdown and truthful restart/missing-result handling. [AC/evidence](README.md), [test receipt](verification.json), [independent READY review](independent-review.md).

Base: reviewedHEAD b60cc55c693a462909b7b3c70edcadf344019b72, same tree as mergedmain2f489e61c38a33c2d5cce03580e0462df84dd206; verify before staging. Proposed branch `codex/zer-18-consumer-retry`. Keep every preexistingZER-16/17 dirty byte andprimaryR unchanged.

## Exact scope

- `agent-orchestrator/event_pipeline/adapters.py`
- `agent-orchestrator/event_pipeline/client.py`
- `agent-orchestrator/event_pipeline/decision_journal.py`
- `agent-orchestrator/hephaestus/main.py`
- `tests/test_hephaestus_consumer.py`
- `tests/test_event_agents.py`
- `chaos-worker/internal/guard/sqli_restart_test.go`
- `.github/workflows/ci.yml`
- `docs/delivery/milestones/R3-recovery/consumer-and-controller.md`
- `docs/delivery/NOW.md`
- `docs/evidence/ZER-18/`
- `tests/test_event_pipeline.py`
- `infrastructure/scripts/verify-event-actors.py`
- `tests/test_event_actor_verifier.py`

Stage only the allowlist. ForNOW, publish only the newZER-18 prefix on cleanbase; preserve unrelated dirty history locally. Evidence manifest must match committed bytes. No private database, credentials, other issue evidence or closing ledger included.

## Requested final authority

Commit/push this package, create onePR, run requiredCI includingLinuxGo-race/image import/production pins, consolidate in-scope review fixes, merge only when gates pass, then obtain/read back owner acceptance and update namedZeroDoorLinear. Owner may accept documented componentAC01/03; any stricter deployed criterion must remain open, never silently checkedPASS. Publication is separate from deployedPVC/broker/G3/end-to-end proof.

No new local lab/deploy/PVC/image operation/model/payload/cloud/other issue is included. FailedCI/review gates stop merge; no bypass. ZER-16 publication permission does not coverZER-18; noZER-18 publication action has been taken.

## In-scope CI correction after approval

The approved consolidated review/CI-fix authority includes these direct callers: tests/test_dashboard_modes.py, tests/test_dashboard_mode_runtime.py, infrastructure/scripts/r1_mode_runtime.py. Scope was recorded before edits. ci-fix.md documents two failed jobs and22 passing retests; guard/AC/acceptance limits remain unchanged. Original approved proposal snapshot and reply stay immutable.
