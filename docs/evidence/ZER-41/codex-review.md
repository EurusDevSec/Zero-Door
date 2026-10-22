# Codex review — ZER-13 AC-01 + ZER-41 offline — 22/10/2026

**Verdict: NOT_READY_OFFLINE / CHANGES_REQUIRED.** The intended toy fixture is appropriate, and nominal safe/vulnerable and CRUD tests pass. Eight consolidated corrections below are required before asking to execute the proposed lab. ZER-13 AC-01 remains a proposed design pending source-IP clarification and owner acceptance of F-05; ZER-41 stays PARTIAL. ZER-42 and parent AC-03/04 are not reviewed as implemented outcomes.

## Provenance and coverage

- Local untracked ZER-41 package, not a PR. HEAD 4ccd6c324f0e1dbde8bff351ea808efe5361bb00 on zer-11-g1-acceptance; observed origin/main 5a87e1c487cb64ea030e17e3817321091357c607. Accepted G1 content is unchanged. No branch switch, source edit, Docker build, cluster/model/API invocation, Git publication or Linear mutation.
- Read the full service, tests, both seeds/expected, Dockerfile, manifest/checker, README, runbook and verification. Direct consumers checked: measurement.flows.fixture_spec/Flow, existing image conventions, Traefik values/route and Fluent Bit collection. Live ZER-13 and ZER-41 read again on 22/10 from verified zero-door project; both now In Progress at read time. That state is not acceptance.
- Re-ran 30 tests on each existing production pin (Nemesis and Hephaestus, Python 3.11.9): both PASS. Original manifest checker PASS. Source manifest 10/10 matches Claude's hashes; protected unrelated dirty files 10/10 match the pre-package baseline.
- Review probes use only temporary SQLite and loopback; source snapshots and outputs are under scratch/zer13/codex-review/. Parent replayed the HTTP probes. No deliberately large allocation or exhaustion test was run.
- GitNexus refreshed locally with analyze --pdg --index-only (51 s). Context confirms Store.search → _readonly; file impact identifies tests/test_sqli_fixture.py. detect_changes does not include the untracked package in its diff listing, so source reads are authoritative. PDG confirms existence-only unlink and query error branches. explain returned zero findings with its callback/implicit-flow caveat. MCP still reports a four-commit stale warning after refresh; do not claim a complete or exact graph audit. Dynamic BaseHTTPRequestHandler callbacks and Kubernetes/log paths were inspected directly.

## Findings and required regression

### ZR41-01 — P1: the profile leaks through the actual container log path

Anchor: services/sqli-fixture/app.py:375–377. Consumer: infrastructure/logging/fluent-bit.yaml:28–31,66.

build_server prints profile=vulnerable (or safe), seed ID, row count and DB path to stderr. Fluent Bit tails every container CRI log and explicitly parses BOTH stdout and stderr; stderr is not an H-plane channel. A startup probe captured the active profile verbatim. The test only captures stdout, so its omission check passes while the production recipe discloses the profile.

Remove H-only profile/seed/answer context from every container stream (including error/startup paths), or use an actually isolated operator receipt outside the O log pipeline. Keep ordinary health/error diagnostics without the variant. Add a test capturing stdout AND stderr for both startup profiles and failures, and check the real collector boundary. Do not fix this by claiming stderr is private.

### ZR41-02 — P1: HTTP connection lifecycle corrupts request identity and framing

Anchors: services/sqli-fixture/app.py:265–269 and :333–340. Consumer: request/log correlation required by the ZER-13 design.

setup runs once per connection, but HTTP/1.1 processes several requests on the same handler. GET /health and GET /ready on one connection returned the same X-Request-Id; after 350 ms idle the second duration included that idle time (~360 ms). Metadata is per connection rather than per request.

Additionally, rejected POST bodies are neither drained nor followed by connection close. A POST /no-route whose declared body contains a harmless GET /health, followed by a real GET /ready, yielded THREE responses/access records for TWO requests (404, 200 health, 200 ready), all sharing one ID. Oversize/bad length and unsupported framing need the same review, as do bodies on GET/DELETE.

Use a clear per-request lifecycle. Either support persistent framing correctly or deliberately close after one request; do not add a second HTTP framework just for this fix. Start metadata per parsed request, and reject/close unsupported or unread bodies consistently. Regression: two real persistent requests have distinct IDs and request-only timings; an early-rejected body's bytes never become another request; malformed/duplicate length and unsupported transfer framing cannot produce extra accepted operations.

### ZR41-03 — P2: advertised work limits do not bound admission or transport

Anchors: services/sqli-fixture/app.py:171–175, :342, :373.

Twenty incomplete, below-MAX_BODY POSTs left twenty request threads waiting after 800 ms while all sixteen search slots remained available. ThreadingHTTPServer has no connection admission limit or body/header/idle deadline. CRUD also bypasses the search semaphore. In a controlled queue test, a search waited 813 ms before its 500 ms deadline even started, then returned 200. This is not a claim that sixteen queries are a total request limit; it demonstrates the missing limits outside the DB section.

Define and enforce separate bounded connection/request and DB admission, deadline-before-wait, transport read/write/idle deadlines and CRUD/storage work. A client that dribbles bytes must not extend a wall deadline indefinitely. SQLite's progress callback/row count alone also does not bound a single large value allocation; set appropriate SQLite/result-size limits before materialising results. Probe only small values in tests, never OOM the host. Add controlled queue, partial-body, idle and write-path tests with reliable cleanup and timing margins; document exactly which cap each test proves.

### ZR41-04 — P2: failure paths lose or misclassify the observable request

Anchors: services/sqli-fixture/app.py:172, :184–188, :271–282, :315–320.

Missing DB escapes _readonly as OperationalError before translation: actual HTTP gets RemoteDisconnected, traceback and no structured access record. A real exclusive SQLite lock on a benign category returns 400 QUERY_REJECTED, classifying availability failure as bad client SQL. A small 2 KiB BLOB result from an in-scope toy UNION is returned as bytes by Store and then raises TypeError during JSON encoding. PUT /health uses the inherited 501 HTML response without server request ID/access log. Client disconnects raise before emit and likewise disappear from structured observations.

Introduce a consistent terminal observation/error path for parsed requests. Distinguish invalid query (4xx) from DB unavailable/locked/IO (503); reject unsupported result types explicitly; handle unsupported method and disconnect truthfully. Emit exactly one outcome even when response transmission fails, without claiming delivery or hiding the error. Required regressions: missing/locked DB, small BLOB result, unsupported method and disconnect; each has the correct status/reason when deliverable and a single terminal record when the request was parsed. Preserve the original client failure rather than turning it into success.

### ZR41-05 — P2: ordinary startup destroys the existing DB before validation/bind completes

Anchors: services/sqli-fixture/app.py:133–148 and :371–373.

build_db unconditionally unlinks any existing fixture.sqlite in the configured directory before opening the listening socket. The negative-port probe first creates an owned order, then tries startup on the same directory with port=-1: startup raises OverflowError, and the original order is gone. A normal container restart with the same emptyDir also reseeds and deletes all order state. Existence is the only guard; no run ownership or explicit reset is checked.

Validate config before mutation; initialise a fresh owned DB or open a compatible existing DB without erasing it. Reset must be explicit and scoped to proven fixture/run ownership. Do not delete arbitrary pre-existing files just because their basename is fixture.sqlite. Regression: normal reopen preserves orders; invalid config/bind/seed failure preserves existing bytes; explicit reset only affects an owned run. A unique fresh temp dir remains a valid test isolation mechanism.

### ZR41-06 — P2: ingress peer is reported as client when proxy provenance is unknown

Anchors: services/sqli-fixture/app.py:98–102; infrastructure/manifests/sqli-fixture.yaml:34–37; docs/runbooks/sqli-fixture.md:41–43,53–55.

The actual manifest routes through Traefik but configures no trusted proxies. resolve_source('10.42.0.7', '198.51.100.9', []) sets client_ip=10.42.0.7, method=DIRECT_PEER, confidence=OBSERVED_PEER. The runbook instead promises UNKNOWN. The function has not proved that peer is a direct end client rather than an unrecognised ingress hop, so downstream block selection could target the shared proxy. Observing TCP peer is valid evidence; asserting it as the end-client is the problem.

Represent observed peer separately from proven client attribution. Make direct-client vs expected-proxy deployment topology explicit; ingress with no validated chain must keep client_ip UNKNOWN. Keep client-supplied XFF untrusted. Regression covers actual manifest defaults behind a proxy, an explicitly direct loopback client, a narrow valid chain, missing/bad forward and spoofed input. No offline test proves actual NAT/source enforcement; retain the two-source runtime prerequisite.

### ZR41-07 — P2: controller-only NetworkPolicy admits unrelated system pods

Anchor: infrastructure/manifests/sqli-fixture.yaml:141–147; checker docs/evidence/ZER-41/check_manifest.py:62–65.

The allow rule selects the whole kube-system namespace, without a podSelector. The offline selector counterexample admits both a Traefik pod and an unrelated system pod; the original checker still says OVERALL PASS. This violates the declared controller-only inbound scope.

AND the actual Traefik pod labels with the namespace selector in one peer, with a preflight that verifies those labels before deployment. Add semantic positive/negative checks for the permitted controller and an unrelated kube-system pod. Do not broaden all source namespaces to make a probe connect. These selector tests are static, not proof of live CNI enforcement.

### ZR41-08 — P2: the proposed lab plan lacks a bounded, ownership-safe execution envelope

Anchor: docs/runbooks/sqli-fixture.md:47–62.

The plan lists per-query caps but no total duration (including build/cleanup), request totals by operation/source, disk budget or finite retry budget. It declares namespace ownership and proposes deleting the whole fixed namespace without checking pre-existence/run UID. Its stop condition says any reachability from outside zd-sqli-lab, contradicting the intended Traefik controller in kube-system. ClusterIP also does not prove no host exposure: /fixture uses the existing Traefik LoadBalancer and k3d host mapping.

Write one concrete proposed runtime envelope for later approval, including explicit context k3d-zero-door, finite build/test/cleanup time, request and storage totals, allowed origins, two distinct lab sources, profile changes, source receipts, namespace create-if-absent/owner UID and exact restoration/deletion. Abort on unowned pre-existing namespace. Verify actual host binding/access boundary before enabling vulnerable profile; do not assert public exposure is currently proven. Prepare the plan, do NOT run it. Check paths reflect intended ingress rather than forbidding the permitted route.

## Passed behavior and non-findings

- The toy SQLi result on the supplied fixed case exposes actual seeded restricted rows; safe parameter binding yields none. Same benign categories agree across profiles. No need to rewrite Boutique or add another DB.
- Current Flow compatibility and owned cleanup by nonce echo pass. Flow is the owner-checking caller; parameterised delete-by-ref is not an independent caller authentication guarantee. Do not claim that all service callers have ownership enforcement. No measurement/event pipeline change is required by this finding list.
- Fixed-shape catalog seed duplication has a drift test; stdlib implementation avoids dependency churn. Static Docker UID/GID/fsGroup, DB mount/env and interpreter align with existing agents. Actual build/startup/CNI/Fluent Bit ingestion remain untested.
- Broad trusted CIDRs and malformed-left-prefix examples were explored; right-to-left trust parsing may legitimately ignore client-controlled left prefixes. No separate vulnerability finding is asserted for those probes.
- No requirement to run every R1 suite, create another checker framework, or implement executor/healer/HPA. These would add scope without closing the listed defects.

## Replay and bounded fix package

Evidence (local scratch, not claimed shared/committed): counterexamples.py / counterexamples.json; http/observations.json; http/framing-observations.json; packaging/policy-output.json; suite-nemesis.txt; suite-hephaestus.txt; manifest.txt; intake.json and before/ source snapshot. The initial Windows same-port bind control did not fail reliably and is NOT used as a bind-failure finding; the portable invalid-port case above does.

From repo root with Bash:

~~~bash
bash scratch/zer13/codex-review/counterexamples.sh
bash scratch/zer13/codex-review/http/probe.sh
bash scratch/zer13/codex-review/http/framing.sh
bash scratch/zer13/codex-review/tests.sh
~~~

Fix all ZR41-01…08 together and related branches in the same service/packaging boundary. File scope: app.py, services/sqli-fixture/README.md, tests/test_sqli_fixture.py (or one focused HTTP test file), infrastructure/manifests/sqli-fixture.yaml, docs/evidence/ZER-41/check_manifest.py, docs/runbooks/sqli-fixture.md, verification.md; append issue note and prepend NOW. Dockerfile/seed changes only if concretely required and explained. Existing Codex report/probes/source snapshots are read-only. Keep fixture_spec, agents, worker, logging, Traefik shared config, CI and historical evidence untouched. Use the existing before/ snapshot to demonstrate fail-before on these defects, not only inverted mutants. Adapt a separate retest harness where the old probe deliberately assumes a response shape; do not edit the originals.

Retest the changed behavior and existing 30 cases on the production pins. Preserve timeout/failure evidence, report missing tools honestly, and write one concise fix section in verification.md plus one handoff. Stop only for a real scope/design/authority decision. Offline fixes are within the existing package; lab/build/model/publication/Linear remain ungranted. Owner F-05/design acceptance comes after fixes and review, not from a test PASS. Return READY_FOR_CODEX_RETEST_OFFLINE, not Done.
