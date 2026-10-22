# Codex retest fix02 — ZER-13 AC-01 / ZER-41

22/10/2026. **SOURCE_RETEST_PASS_OFFLINE**, with a non-blocking test-harness timing note. FX41-R1…R3 are closed for the reviewed offline scope. No new P1/P2 source finding. This is not runtime acceptance or Done.

## Target and scope

Local untracked fixture package, fix01 snapshot → fix02 source. HEAD `4ccd6c324f0e1dbde8bff351ea808efe5361bb00`, branch `zer-11-g1-acceptance`, staging empty. App SHA-256 `37c7a045e098f1c169a3b356a03e0807670b1f2876f342db0710b137810aa755`. Reviewed app delta, both suites, service README, runbook phase/request budget, verification claims and replay; unchanged DB/proxy/policy behavior retains the previous retest. No executor ZER-42, general R1 rewrite, Docker build, cluster or model activity.

Live Linear Zero Door read-back: ZER-13 and ZER-41 In Progress. ZER-41 still requires deployment, observable route/query/log and packaged version. Parent AC-03/04 remain outside this implementation package. No Linear writes.

## Residual findings disposition

| Item | Independent evidence | Result |
| --- | --- | --- |
| FX41-R1 absolute receive deadline | Real loopback progress in body, headers and first line stopped at 3.000 / 2.984 / 3.000 seconds, respectively. Exactly one 408 record per request; incomplete POST wrote no order. Production suites also cover idle close, capacity and DB admission. Source: app.py:344–361, 390–424, 487–504. | Closed offline |
| FX41-R2 generic rejection boundary | An unlisted UNLISTED method returned 405 JSON plus X-Request-Id and exactly one record; malformed line 400 and unsupported version 505 likewise. TRACE/FOO/HEAD/header limits covered in HTTP suite and replay. Source: app.py:390–430. | Closed offline |
| FX41-R3 startup stream leakage | Actual CLI subprocess on a mismatched-seed DB exited 2 with only startup_failed / DB_INCOMPATIBLE / ZD_SQLI_DB_DIR; no canary, expected seed, path or traceback. DB bytes identical. Supplied startup cases also exercise foreign DB, invalid seed/config. Source: app.py:664–705. | Closed offline |
| Runtime envelope clarification | Runbook §4 now specifies 3+7+3+4+2+4+7 = 30 minutes, cleanup by minute 23; 4000 total HTTP attempts across all operations/profiles/sources/retries, 3 retries = 4 attempts; host binding must be checked before vulnerable profile. | Proposal sufficiently concrete; still requires owner approval and execution preparation |

## Verification actually run

- Nemesis CPython 3.11.9: main **42/42**, HTTP **15/15**. Replay on current source again 42/42 + 15/15.
- Hephaestus CPython 3.11.9: HTTP **15/15**; main first run **41 passed / 1 error** in the existing Logs test (StopIteration while reading a log snapshot). Do not report this run as 42/42 or discard it.
- Same failing test independently diagnosed below: test reads before asynchronous emit; production record was emitted afterwards. No evidence of a fixture request/log-loss defect from this failure.
- Real fail-before replay of Claude's supplied fail_before.sh: snapshot main **7 failures / 42**, HTTP **9 failures / 15**, **no API errors**; current **42 + 15 pass**. Before replay body had no response by 12 s, TRACE 501, canary+traceback present; after 408 at 3 s, TRACE 405, no canary/traceback. Original Codex snapshot and probes unchanged.
- Manifest checker PASS; Bandit app.py `-lll -iii` exit 0 (reported zero issues at every level); git diff --check clean. No repetition of unrelated R1 suites.

Evidence: `scratch/zer13/codex-retest02/` — intake.json, source.diff, independent.py / independent.json, per-pin logs, fail-before/summary.txt, flake_control.py / flake_control.log, manifest.log, bandit.log and preservation.json. All JSON observations were read, not inferred from process exit alone.

## Test timing note — fix before CI publication

At `tests/test_sqli_fixture.py:473–479`, Logs.test_no_container_stream_discloses_the_profile snapshots the capture before the server has necessarily emitted the 200 access record; next(...) then raises StopIteration. This code was already present before fix02 and is not a newly introduced source finding. The HTTP dribble tests' bounded settled_records helper does not cover this main-suite test.

An independent scratch-only control delayed emit by 0.3 s: the exact test failed consistently with StopIteration while both 200 and 400 terminal records appeared afterwards. In the test helper, teardown may restore app.LOG before those late records, so they appear on the process stdout rather than the capture. Production uses its ordinary stdout sink and does not perform this test teardown. Keep the original failed log. Before CI, wait with a bounded condition for the required records (or join request handlers before snapshot/restoring the capture), preserving exact cardinality and leakage assertions. No blind rerun-until-green and no new application framework are needed.

This note does not reopen FX41-R1…R3 or require another architecture/executor package. The application is ready for bounded runtime preparation; the official suite still needs this synchronization cleanup before publication.

## Coverage limits and provenance

The extra blocked-response probe tried one 200000-byte response with small loopback socket buffers. Windows accepted it in 16 ms: the blocked-write path was **not reached**. The first diagnostic asserted blockage and failed; it is retained as independent-v1.py / independent.log. The corrected diagnostic records this as inconclusive, not as proof of a write-timeout failure or success. Receive deadlines are empirically verified; the write-side absolute bound remains source-reviewed, without blocked-write runtime proof.

GitNexus refreshed locally with analyze --pdg --index-only (52.9 s); current handler range and emit/respond/send_error edges match source. detect_changes covers tracked dirty docs, not the new untracked app. Context/impact still report a four-commit staleness warning despite refresh; dynamic stdlib callback dispatch is not resolved as an incoming caller. Impact UNKNOWN, explain zero findings with callback/field caveats, PDG truncated control sample; none is used as evidence of safety. Direct source and real loopback/SQLite observations establish the conclusions.

67/67 prior Codex evidence hashes and 11/11 unchanged files from Claude intake match; reviewed source stayed unchanged during retest. Snapshots were taken before writing this report. Report/note/NOW are the only durable review edits; no source changes, commit/push/PR, build/apply, model or Linear mutation.

## Next boundary

Prepare one bounded runtime package against runbook §4, with the test synchronization fix included before CI. Obtain Hoang's F-05 decision (effect = real restricted synthetic seed row returned, absent on benign safe query) and lab authority before build/import/apply. Verify host binding; abort before vulnerable exposure if any relevant listener is not loopback-only. Real two-source IP/NAT, NetworkPolicy, Traefik routing and Fluent Bit/Elasticsearch evidence remain unverified. ZER-41 remains PARTIAL; ZER-13 AC-03/04 and ZER-42 are not complete.
