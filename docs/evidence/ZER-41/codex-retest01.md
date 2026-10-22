# Codex retest fix01 — ZER-13/41 — 22/10/2026

**Verdict: CHANGES_REQUIRED_OFFLINE.** Normal startup, connection framing, DB preservation, proxy attribution and controller selector improved as intended. Three residual branches of the original findings still fail independent probes; no new executor, framework or broader R1 work is requested. ZER-41 remains PARTIAL and no lab/build/publication/Linear action was performed.

## Target and checks

Local untracked fixture package on HEAD 4ccd6c324f0e1dbde8bff351ea808efe5361bb00, branch zer-11-g1-acceptance. Scope: fix01 delta in app/test/README, manifest/checker, runbook/verification. Staging is empty. Read complete fixed app and focused tests, original review, fix verification, checker/manifest and runbook; checked direct measurement fixture contract and existing Fluent Bit boundary from the review. No source edits during retest.

- Independently ran main **37/37** and HTTP **8/8** on both production pins (Nemesis and Hephaestus, CPython 3.11.9); current manifest checker PASS.
- Replayed supplied fail-before runner into a fresh scratch output: old main 6 failures/12 errors, old HTTP 5 failures/3 errors, old manifest rejected; after 37/37 + 8/8 + manifest PASS. Some old failures are API incompatibilities (new helper/signature absent), not individual behavioral proof for every branch. The new probes below test observable behavior directly.
- Confirmed 40/40 protected Codex files and 10/10 unrelated dirty files match Claude intake. Fixed source hashes match review intake. Existing report/probes/snapshots untouched.
- GitNexus locally refreshed with --pdg --index-only (51.1 s). Store.search context now reflects _connect/_classify; controls query returns updated source guards. The MCP still warns four commits stale, dynamic HTTP callbacks/imports are incomplete, and detect_changes omits untracked source. explain returns no persisted findings with callback/implicit-flow caveat. Direct source/wire evidence decides this retest, not graph zeros. One combined service/packaging review pass was used; no delegation or new test framework.
- No independent Bandit rerun; Claude's prior result is reported evidence only. No Docker, cluster, CNI, ingress, paid API or model checks.

## Remaining fixes (all P2)

### FX41-R1 — ZR41-03: an idle timeout is still presented as a wall deadline

Anchors: services/sqli-fixture/app.py:337,342–345,349–358,412–429; tests/test_sqli_fixture_http.py:153.

SOCKET_TIMEOUT_S is installed with socket.settimeout(5), while read_body/drain use buffered reads with no absolute transport expiry. Progress within each idle timeout keeps the read alive. A single loopback POST sends just eight bytes at 0.8 s intervals, then the remainder of a small valid body: the service waits **6.406 s**, then returns 503 BUSY and logs duration_ms=6406.0. Both advertised limits (3 s request budget and 5 s transport deadline) have elapsed; BUSY is emitted only after the read finishes. This is not a load/exhaustion test. The existing test sends one byte and then stops completely, so it exercises idle expiry rather than dribbling progress.

Enforce a real absolute deadline across request-line/header/body/drain and response transmission (including repeated progress), with bounded cancellation/connection closure and correct terminal observation. Preserve existing DB admission/query caps. A per-socket idle timeout alone does not implement this. Add small progressive header/body tests, an idle control and cleanup checks; do not increase the documented caps or weaken assertions to make this pass.

### FX41-R2 — ZR41-04: the inherited unsupported-method path still bypasses observation

Anchors: services/sqli-fixture/app.py:349–366,536–540.

PUT/PATCH/OPTIONS/HEAD are mapped to the structured 405 handler, but BaseHTTPRequestHandler dispatches any other unimplemented method to inherited send_error. An ordinary **TRACE /health** gets **501 HTML**, lacks X-Request-Id, and produces **zero structured records**. Normal method rejection need not be 405 universally, but the promised structured response and one terminal record must hold. The current test only exercises PUT.

Use one consistent fallback/rejection observation path, rather than just enumerating a few method names. Cover a method not explicitly listed, and parser/framing errors through the same boundary where a request can be identified. Preserve one response/one log/connection-close and avoid recursion or claiming successful delivery on disconnect. TRACE need not be enabled.

### FX41-R3 — ZR41-01: startup failure still sends H-side seed context to stderr

Anchors: services/sqli-fixture/app.py:201–205,583–589; existing collector infrastructure/logging/fluent-bit.yaml:28–31,66.

The normal banner is now neutral, but main only catches ConfigError while constructing Config. open_or_create raises outside that catch. A real CLI subprocess on an incompatible temporary fixture DB exits 1 and prints a traceback containing stored seed canary **hidden-seed-canary**, expected seed id and full DB path to stderr. Fluent Bit collects that stream. This does not show an active profile leaking on normal startup; it demonstrates the failure path required by the original H/O finding remains open. The test captures the successful startup banner only.

Fail closed with a neutral structured startup reason/code on container streams. Keep detailed seed/path/variant diagnostics in an actually private operator channel if needed. Exercise the real CLI on mismatched/foreign DB and seed/config failures; capture BOTH streams and assert no H-side canaries/traceback. Existing DB must remain intact and failure exit must remain nonzero.

## Original finding disposition and runtime preparation

| Original | Retest disposition |
| --- | --- |
| ZR41-01 | Normal banner fixed; failure branch still FX41-R3 |
| ZR41-02 | One request/connection and embedded-body regression pass; retain while fixing shared HTTP handling |
| ZR41-03 | Connection/DB admission and SQLite length cap pass; absolute transport expiry still FX41-R1 |
| ZR41-04 | Missing/locked DB, BLOB and mapped-method cases pass; generic rejection still FX41-R2 |
| ZR41-05 | Reopen preserves orders; invalid config/foreign DB refuses without erase in focused suite |
| ZR41-06 | Default proxied UNKNOWN, explicit direct and narrow trusted chain pass offline; no live source proof |
| ZR41-07 | Namespace AND Traefik pod selector and positive/negative static checks pass; CNI untested |
| ZR41-08 | Ownership/abort/storage/allowed route substantially improved; concretize details below before lab approval |

The proposed runbook is still preparation. Before asking to execute it, replace “a per-phase cap” with actual phase minutes and a cleanup reserve inside the 30-minute total. State one total HTTP-attempt cap including both profiles, both sources, order read/delete/health and retries; clarify whether “3 retries” means up to four attempts. Record how the actual host binding is checked, not just a successful loopback request. These can be clarified in the existing runbook alongside this fix; no new runtime harness/framework is required for the offline retest. No lab authority is implied. F-05/effect and final runtime envelope remain Hoang decisions.

## Replay and bounded next package

Evidence: scratch/zer13/codex-retest01/{intake.json,preservation.json,edges.py,edges.json,main.log,http.log,main-hephaestus.log,http-hephaestus.log,manifest.log,fail-before/summary.txt,graph.log}. before/app.py preserves exact fix01 source for next fail-before. The first scratch draft had a string-escaping syntax error; it was corrected before collecting the final successful probe. No failed production test is suppressed.

~~~bash
bash scratch/zer13/codex-retest01/edges.sh
~~~

The probe records observations and exits zero when collection completes; inspect/assert JSON values, not that exit code. If behavior changes to close the connection earlier, adapt a separate retest harness to accept timely close/408 and never edit the original evidence.

Fix FX41-R1…R3 and related branches together within the existing app/test/README/runbook/verification scope. Keep all Codex reports/probes/snapshots read-only and unrelated dirty intact. Preserve neutral-ID and DB/proxy/policy regressions. Use the fix01 snapshot for behavioral fail-before; add focused regressions and run the 37+8 affected suites on both pins, without unrelated full R1/mutant runs. Record one fix section in existing verification and append/prepend the usual note/NOW. Return READY_FOR_CODEX_RETEST_OFFLINE. No lab, build, model, Git publication or Linear mutation.
