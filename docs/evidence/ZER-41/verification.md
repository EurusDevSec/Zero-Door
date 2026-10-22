# ZER-41 verification — SQLi catalog fixture (offline package, Claude)

Verdict: **READY_FOR_CODEX_RETEST_OFFLINE** (after fix rounds fix01 for ZR41-01…08 and fix02 for
FX41-R1…R3; see the fix sections at the end). ZER-13 AC-01 (design) proposed and implemented; ZER-41 is **PARTIAL** (image NOT_BUILT, manifest
NOT_APPLIED, no runtime IP/log/ingress evidence). ZER-13 AC-03/04 and ZER-42 are **not** done by this
package. Nothing was committed, pushed, applied, or changed in Linear.

> The AC table and "Package source" hashes below are the original submission; the fix-round section at the
> end records the ZR41-01…08 corrections, the new regressions, their fail-before on the pre-fix snapshot and
> the updated source hashes. Where they differ, the fix section is current.

- HEAD at work: `4ccd6c324f0e1dbde8bff351ea808efe5361bb00` (in origin/main `5a87e1c`), branch
  `zer-11-g1-acceptance`, staged empty. Intake and source hashes: `scratch/zer13/claude/intake.json`
  (`intake.py --check` re-compares). Note/NOW before edit: `scratch/zer13/claude/before/`.
- Interpreters (offline, lab untouched): production pins `scratch/zer12/production-{nemesis,hephaestus}`
  (CPython 3.11.9); Bandit from `scratch/zer12/test-venv` (3.12.4).

## AC → check → result

| AC / requirement | Check | Result |
| --- | --- | --- |
| AC-01 role/business/safe-vulnerable/limits/probe/packaging/ingress/IP/trace design | Design implemented in `services/sqli-fixture/` + `infrastructure/manifests/sqli-fixture.yaml`; rationale in `services/sqli-fixture/README.md` and `docs/runbooks/sqli-fixture.md` | PASS (design); runtime PARTIAL |
| Seed reproducible, baseline row count, seed id | `Seed.*` (3 tests); `tests/fixtures/zer41/expected.json` locked from seed before assertions | PASS: seed `zer41-catalog/1`, 8 rows (5 public, 3 restricted) |
| Benign input equivalent on safe and vulnerable; no restricted leak | `Search.test_benign_categories_are_equivalent_on_both_profiles` | PASS across apparel/home/electronics/internal/nonexistent |
| Effect = restricted row the benign query never returns, on vulnerable only | `Search.test_injection_leaks_restricted_rows_only_on_the_vulnerable_profile` | PASS: vulnerable returns RES-APP-900/RES-INT-001/RES-INT-002; safe returns none. 200 is not the oracle |
| Read-only, single statement, caps | `Search.test_stacked_statement_injection_is_rejected_not_executed`, `test_rejected_injection_returns_client_error`, `test_category_over_length_is_rejected` | PASS: stacked/DROP rejected 400; catalog intact after; category >120 → 400 |
| CRUD via `measurement.flows.fixture_spec`: create → independent read → owned cleanup | `Crud.test_owned_order_round_trip_then_cleanup` | PASS: ok=True, cleanup order=DONE |
| Cleanup scoped/parameterised; wrong ref deletes nothing | `Crud.test_delete_is_scoped_to_one_ref_and_is_parameterised` | PASS: `' OR '1'='1` deletes 0; only the named ref removed |
| Unproven ownership not cleaned | `Crud.test_unproven_ownership_is_not_cleaned` | PASS: cleanup reports UNRESOLVED_OWNERSHIP, record left |
| DB error/lock, oversized, malformed input | `Crud.test_db_lock_surfaces_as_503_...`, `test_oversized_body_is_refused`, `test_malformed_body_is_refused` | PASS: 503 on real lock, 413 oversized, 400 malformed |
| Source IP: no trust of client header; UNKNOWN without proof | `Source.*` (7 tests) | PASS: direct peer is source; forged XFF ignored; trusted proxy → forwarded client; no/ malformed/all-trusted forward → UNKNOWN |
| Config refuses start on invalid values | `ConfigGuards.*` (6 tests) | PASS: bad profile / missing or bad DB dir / bad proxy / missing seed all raise |
| Log hygiene: no profile/variant, server request id, sanitised correlation id | `Logs.*` (2 tests) | PASS: "vulnerable"/"profile" absent from log; request id 32-hex ≠ client id; ill-formed correlation id dropped |
| Readiness checks DB; health is process only | `Readiness.*` | PASS |
| Manifest OpenAPI + isolation semantics | `docs/evidence/ZER-41/check_manifest.py` | OVERALL PASS (8 resources) |

## Commands (offline, from repo root, Bash)

```bash
N=scratch/zer12/production-nemesis/Scripts/python.exe; H=scratch/zer12/production-hephaestus/Scripts/python.exe
$N -B tests/test_sqli_fixture.py && $H -B tests/test_sqli_fixture.py     # 30 tests each, OK
$N -B docs/evidence/ZER-41/check_manifest.py                              # OVERALL PASS
scratch/zer12/test-venv/Scripts/python.exe -m bandit -lll -iii -r services/sqli-fixture docs/evidence/ZER-41/check_manifest.py tests/test_sqli_fixture.py  # exit 0
```

Results saved under `docs/evidence/ZER-41/results/` (suite.txt, bandit.txt).

## Security scan note

At the CI threshold (`bandit -lll -iii`, high severity + high confidence) the package is clean (exit 0), the
same gate `.github/workflows/ci.yml` applies. `app.py` raises no Bandit finding at any level. At the default
threshold, only test/evidence helpers raise low/medium findings — B101 (asserts in `check_manifest.py`) and
B310 (`urlopen` of a loopback `http://127.0.0.1` origin in the test) — both benign and test-only. The
deliberate interpolated query on the vulnerable profile is commented as intentional; Bandit does not flag it.

## Limits / what needs a lab (nothing run here)

- Image **NOT_BUILT**: `image: sqli-fixture:latest` has no artefact yet; build and pin the digest in a lab.
- Manifest **NOT_APPLIED**; namespace/route creation needs a separately approved lab turn.
- Source-IP decision is verified as **logic only**. It does not prove NAT behaviour, that Traefik forwards
  (or does not) a client address, or that a NetworkPolicy blocks a source after the proxy. k3d serverlb NAT
  means a host port-forward cannot stand in for two distinct clients; runtime needs two separate lab sources.
- Real Event/log formats, HPA/containment and the Fluent Bit/ES consumer accepting a new namespace are
  unproven offline.
- Decisions left for Hoang at handoff: approve the proposed `zd-sqli-lab` runtime budget; confirm the SQLi
  effect criterion (F-05) this fixture encodes (restricted-row exposure) before it is locked for scoring.

## Package source (sha256)

```
4cd07f66b22b3f99700726fcb3cf91b0fb886f546a45fa29875fa2faab83f53e  services/sqli-fixture/app.py
ec9f818b85a3dce1dbe4b7d87572890b6bbf244ffaea33df549f6079612af90b  services/sqli-fixture/seed.json
5a0966a282fabea5ab770431331bb8a503ced999037f7ba27a3293d5a37d11de  services/sqli-fixture/Dockerfile
c3d272ffba9e86f3afa5751b39947d3489535446611921adccc2968ab0ca400f  services/sqli-fixture/README.md
aaad96165fda7806c4eb8410013f6d307829618b191bfb5586e10f7dded3098f  tests/test_sqli_fixture.py
ec9f818b85a3dce1dbe4b7d87572890b6bbf244ffaea33df549f6079612af90b  tests/fixtures/zer41/seed.json
a626930ded63cc654055c24bc2be8f23aa3f46619349c4dbf544ff4adb859407  tests/fixtures/zer41/expected.json
4957f67829cbf1524290498a654b0d0d140b0c84e67649628c089c14f645175a  infrastructure/manifests/sqli-fixture.yaml
7ce3635a828b700dfb0eed38bb5ba2b7ebc86d07d3e9cd96ce9f24cb4a501742  docs/runbooks/sqli-fixture.md
cc1a28e4d4082ef2d69448b07963a506d8093e8cb3ee8d59eee0ee65488db1d7  docs/evidence/ZER-41/check_manifest.py
```

seed.json is byte-identical in `services/sqli-fixture/` and `tests/fixtures/zer41/` (drift test enforces it).

---

## Fix round fix01 — ZR41-01…08 (Codex review 22/10/2026)

Verdict after fixes: **READY_FOR_CODEX_RETEST_OFFLINE**. Scope held to the service/packaging boundary:
`services/sqli-fixture/{app.py,README.md}`, `tests/test_sqli_fixture.py`, new `tests/test_sqli_fixture_http.py`,
`infrastructure/manifests/sqli-fixture.yaml`, `docs/evidence/ZER-41/check_manifest.py`,
`docs/runbooks/sqli-fixture.md`, this report. No Dockerfile/seed change. `measurement.flows`, agents, worker,
logging, Traefik shared config, CI and historical evidence untouched. Codex report/probes/source snapshot are
read-only; intake + hashes at `scratch/zer13/claude-fix01/intake.json`.

Fail-before is shown on Codex's own `before/` snapshot (byte-identical to the reviewed app), not on inverted
mutants: the **updated** suites fail there and pass on the fixed service.

```bash
NEMESIS=$(pwd)/scratch/zer12/production-nemesis/Scripts/python.exe \
  bash docs/evidence/ZER-41/fix01/fail_before.sh docs/evidence/ZER-41/fix01/results
```

Result (`docs/evidence/ZER-41/fix01/results/summary.txt`): pre-fix snapshot — main `FAILED (failures=6,
errors=12)`, http `FAILED (failures=5, errors=3)`, manifest checker fails; fixed service — main `OK` (37),
http `OK` (8), manifest `OVERALL PASS`.

| Finding | Fix | Fail-before anchor (pre-fix snapshot) |
| --- | --- | --- |
| ZR41-01 profile leaks via stderr | Startup banner is neutral (no profile/seed/db); the profile reaches no stdout or stderr stream. | `Logs.test_no_container_stream_discloses_the_profile` FAILs (banner prints `profile=vulnerable`) |
| ZR41-02 connection lifecycle / smuggling | One request per connection (`Connection: close`); per-request id and timing set in `handle_one_request`; declared bodies are read or drained so unread bytes never reparse. | `Framing.test_pipelined_second_request_is_not_served`, `test_embedded_request_in_a_body_is_not_smuggled`, `test_separate_connections_get_distinct_request_ids` FAIL |
| ZR41-03 missing admission/transport limits | Bounded connections (`FixtureServer`, 64), 5 s transport deadline, deadline-before-wait for the DB slot (busy → 503 fast), separate write gate, `SQLITE_LIMIT_LENGTH` cap. | `Transport.test_connection_admission_limit_refuses_excess_fast`, `test_partial_request_is_closed_by_the_idle_deadline`, `Admission.test_search_fails_fast_when_all_db_slots_are_busy` ERROR |
| ZR41-04 failure paths lose/misclassify | One terminal record per parsed request; invalid SQL 4xx vs unavailable/locked DB 503 (by SQLite error name); non-scalar result → 422; unsupported method → structured 405; disconnect → truthful record, never success. | `Failures.test_missing_db_is_503_with_a_record_not_a_disconnect` ERROR, `test_locked_db_...is_503` FAIL (was 400), `Search.test_blob_union_result_is_rejected_not_crashed` ERROR, `Methods.test_unsupported_method_is_structured_405_with_request_id` FAIL (was 501 HTML) |
| ZR41-05 startup erases DB before bind | `open_or_create` reuses a compatible DB (seed id in a `meta` table) and never unlinks before bind; a foreign/incompatible DB refuses startup; `reset_orders` is explicit and scoped to the orders table. | `Startup.test_normal_reopen_preserves_orders`, `test_invalid_config_refuses_before_any_mutation`, `test_foreign_db_refuses_start_without_erasing` FAIL/ERROR |
| ZR41-06 ingress peer reported as client | `ZD_SQLI_TOPOLOGY`: `proxied` (default) never attributes the peer as client without a validated trusted-proxy chain → UNKNOWN; observed peer recorded separately; `direct` only for a no-proxy exposure. ConfigMap sets `proxied`. | `Source.test_proxied_ingress_without_trusted_proxy_is_unknown` and the other `Source.*` topology cases FAIL/ERROR |
| ZR41-07 NetworkPolicy admits all kube-system | Allow peer now carries `namespaceSelector` AND `podSelector app.kubernetes.io/name=traefik` in one `from` entry; checker evaluates the selector (traefik admitted, unrelated kube-system denied, in-ns probe denied); preflight verifies real labels. | new checker on the snapshot manifest fails; Codex `packaging/policy-output.json` shows unrelated-system-pod ADMITTED before |
| ZR41-08 runtime plan lacks bounded envelope | Runbook §4 rewritten: explicit `k3d-zero-door`, finite time/request/storage/retry budgets, two distinct lab sources, profile control, source receipts, namespace create-if-absent + owner UID with abort-if-unowned, teardown of owned resources only; stop conditions corrected (allowed origin = Traefik `/fixture`; ClusterIP ≠ no host exposure); manifest `emptyDir.sizeLimit: 64Mi`. | checker now asserts `sizeLimit`; runbook/manifest diff vs snapshot |

Checks after fix (offline, production pins CPython 3.11.9): `tests/test_sqli_fixture.py` 37/37 on Nemesis and
Hephaestus; `tests/test_sqli_fixture_http.py` 8/8 on both; `docs/evidence/ZER-41/check_manifest.py` OVERALL
PASS; Bandit `-lll -iii` exit 0 over the service, checker and both test files; `measurement.flows` consumers
(`test_measurement_{probe,boundaries,recovery}`) still pass. Results under `docs/evidence/ZER-41/results/`
and `docs/evidence/ZER-41/fix01/results/`.

Still PARTIAL / needs a lab (unchanged): image NOT_BUILT, manifest NOT_APPLIED; source-IP is logic only
(no proof of real NAT / Traefik forwarding / NetworkPolicy source enforcement — two distinct lab sources
required); real Event/log formats, HPA/containment and Fluent Bit ingestion of the new namespace unproven.
Owner decisions unchanged: approve the `zd-sqli-lab` runtime envelope; confirm the SQLi effect criterion
(F-05). ZER-13 AC-03/04 and ZER-42 remain out of scope.

### Package source after fix (sha256)

```
9e41f8c549d7eb72ab66a86089826102ebca868a11dc6212d1e4945fed8c1ffc  services/sqli-fixture/app.py
79d5c43769e502dc82eeac6d5269729875cc977717ac171815ce8ba18f201c4a  services/sqli-fixture/README.md
5a0966a282fabea5ab770431331bb8a503ced999037f7ba27a3293d5a37d11de  services/sqli-fixture/Dockerfile
ec9f818b85a3dce1dbe4b7d87572890b6bbf244ffaea33df549f6079612af90b  services/sqli-fixture/seed.json
1d99f686f76db6811f5e6890daaac627eb250e4d5abaf1a8393de5ef0fdd3274  tests/test_sqli_fixture.py
b8bf565738ef71c3ac1edc08a65b277468b11cdb0bc3c7ae9972de352029aca0  tests/test_sqli_fixture_http.py
ec9f818b85a3dce1dbe4b7d87572890b6bbf244ffaea33df549f6079612af90b  tests/fixtures/zer41/seed.json
a626930ded63cc654055c24bc2be8f23aa3f46619349c4dbf544ff4adb859407  tests/fixtures/zer41/expected.json
4e795e9fd2e8d32be786038f1c34acc7dc729edabaad9a0fd2123bec1e8f4233  infrastructure/manifests/sqli-fixture.yaml
2f13866ea83bfea42bd7c233124d4a16b9d5168e189a29c070ac6387896236a3  docs/runbooks/sqli-fixture.md
89e7ab34d6268e4ff6fa75fe326dc7fdd2e3239e3069b8fa07fe9d56b3737be2  docs/evidence/ZER-41/check_manifest.py
0c7a9b8886224c14645be02971f58e4d457097118a00abd6966bf4d7ab73425e  docs/evidence/ZER-41/fix01/fail_before.sh
```

---

## Fix round fix02 — FX41-R1…R3 (Codex retest01, 22/10/2026)

Verdict: **READY_FOR_CODEX_RETEST_OFFLINE**. Same boundary as fix01: `services/sqli-fixture/{app.py,README.md}`,
both test files, `docs/runbooks/sqli-fixture.md`, this report; new `docs/evidence/ZER-41/fix02/`. No manifest,
checker, Dockerfile or seed change. Codex reports/probes/snapshots read-only (intake
`scratch/zer13/claude-fix02/intake.json`); unrelated dirty untouched.

| Finding | Fix | Behavioural fail-before on the fix01 snapshot (`scratch/zer13/codex-retest01/before/app.py`) |
| --- | --- | --- |
| FX41-R1 idle timeout presented as a wall deadline | `DeadlineReader` replaces the socket file: every recv gets only the time left of an **absolute** 3 s request budget (request line, headers, body, drain), so steady progress cannot extend it; a request still arriving gets 408, an idle connection that sent nothing is closed without a record; the response write is bounded by an absolute 5 s transport deadline (undeliverable → `delivered:false`). An already-spent budget at DB admission is `503 DEADLINE_EXCEEDED`, not BUSY. | `Transport.test_dribbled_body_…`, `…_headers_…`, `…_request_line_…`, `test_idle_connection_…` FAIL (old: no answer / close only after the 5 s idle timer) |
| FX41-R2 inherited method path bypasses observation | Own `handle_one_request` (stdlib's swallows timeouts) and `send_error` override: every unsupported method, listed or not, and every parser rejection (400 line, 414, 431, 505) answers structured JSON with `X-Request-Id`, one record, close. Explicit `do_PUT/…` mappings removed. | `Methods.test_unsupported_methods_…` (TRACE, FOO), `test_malformed_request_line_…`, `test_unsupported_http_version_…`, `test_too_many_headers_…` FAIL (501/400 HTML, no record) |
| FX41-R3 startup failure leaks seed context | `main` catches every startup failure and prints one neutral stderr line `{"event":"startup_failed","reason":…,"setting":…}` with nonzero exit; `ConfigError` carries a neutral code/setting and keeps details in-process only; a non-SQLite file is `DB_INCOMPATIBLE`; `FixtureServer.handle_error` prints only the error type (default prints a traceback). Existing DB kept. | `StartupFailure.*` (real CLI subprocess, both streams: mismatched seed DB, foreign file, ill-formed seed, invalid settings; handler error) FAIL (traceback with canary, path, expected seed id) |

Same-cause branches found in self-review and fixed: a request cut mid-first-line crashed the reply path
(`log_request` read the unset `requestline`; `send_response` read the unset `request_version`) and lost its
record — both now initialised, covered by `test_dribbled_request_line_…`; malformed targets map to 400 via
`route()`; body shorter than declared → 400 `BODY_INCOMPLETE`; method names in the log are sanitised.

Runbook (Codex note on ZR41-08): §4 now has phase minutes summing to 30 with a 7-minute cleanup reserve; one
total cap of 4000 HTTP attempts covering both profiles, both sources, all operations and retries; "3 retries"
defined as at most 4 attempts, each counted; and a read-only host-binding check (`docker port
k3d-zero-door-serverlb`, `netstat` on 8080, Traefik `ServiceName` for `/fixture` vs `/`) with a stop before
the vulnerable profile if any listener is not loopback-only. Still a proposal; no lab authority implied.

Commands and results (production pins, CPython 3.11.9):

```bash
NEMESIS=$(pwd)/scratch/zer12/production-nemesis/Scripts/python.exe \
  bash docs/evidence/ZER-41/fix02/fail_before.sh docs/evidence/ZER-41/fix02/results
```

- Snapshot: main `FAILED (failures=7)` of 42, http `FAILED (failures=9)` of 15 — only the new regressions,
  every older case passes; adapted edge replay: dribbled body unanswered after 12 s, TRACE → 501 HTML, failed
  startup prints the canary and a traceback.
- Current: main 42/42, http 15/15 on Nemesis **and** Hephaestus; edge replay: dribbled body → 408 at 3.0 s
  with one POST/408 record, TRACE → 405 JSON with id and one record, failed startup exit 2 with only
  `DB_INCOMPATIBLE`, DB bytes kept.
- Manifest checker OVERALL PASS (unchanged); Bandit `-lll -iii` exit 0 (app.py: no finding at default level);
  `test_measurement_{probe,boundaries,recovery}` pass.
- Intermittent failure, diagnosed not retried away: a first loop (8 runs × 2 pins,
  `scratch/zer13/claude-fix02/runs/loop-*`) showed 4/8 Nemesis runs failing the dribble tests with an empty
  record list while the 408 had already arrived. Cause: the record is written right after the response (to
  know `delivered`), and the test read the log after only the first chunk. The tests now wait (bounded, 2 s)
  for the record and still require exactly one 408. After that and the request-line fix, a second loop was
  16/16 OK (`runs/loop2-summary.txt`).
- `docs/evidence/ZER-41/fix02/edges_replay.py` is an adapted copy of Codex's `edges.py` (which assumes the old
  read-to-the-end behaviour); the original is untouched.

Not covered by a test: a client that stops reading a response larger than the socket buffers (no route in
the 8-row seed produces one), so the write-side deadline is exercised by code path only. Unchanged PARTIAL:
image NOT_BUILT, manifest NOT_APPLIED, no live NAT/CNI/Fluent Bit/source proof; F-05 and the runtime envelope
are Hoang's decisions; ZER-13 AC-03/04 and ZER-42 out of scope.

### Package source after fix02 (sha256)

```
37c7a045e098f1c169a3b356a03e0807670b1f2876f342db0710b137810aa755  services/sqli-fixture/app.py
8305acf722ac97ba9781c119a528fbfe239be82148c8eb38f41271a08ba8d92b  services/sqli-fixture/README.md
93c747a3e83c1382d0a04ff6d3784fbc677f7adbea269dab2bd7cf14a180ba6b  tests/test_sqli_fixture.py
8f64e7451ad94a259731d9527a4043c92611aecbb9f605c7182e05e5d8d1bda7  tests/test_sqli_fixture_http.py
84e556d3d348794d171e2b81856fc5823987543fd875d9967cfc3f5a5934d126  docs/runbooks/sqli-fixture.md
ab35614b0bc8c568de8173b3d3630fe70f7aa49ab1eff38e073f3e394c975c66  docs/evidence/ZER-41/fix02/fail_before.sh
85e940cae554035aed3a0871d6e50c5c84df643a7669d3aaeca3adfd250b1f4e  docs/evidence/ZER-41/fix02/edges_replay.py
4e795e9fd2e8d32be786038f1c34acc7dc729edabaad9a0fd2123bec1e8f4233  infrastructure/manifests/sqli-fixture.yaml
89e7ab34d6268e4ff6fa75fe326dc7fdd2e3239e3069b8fa07fe9d56b3737be2  docs/evidence/ZER-41/check_manifest.py
5a0966a282fabea5ab770431331bb8a503ced999037f7ba27a3293d5a37d11de  services/sqli-fixture/Dockerfile
ec9f818b85a3dce1dbe4b7d87572890b6bbf244ffaea33df549f6079612af90b  services/sqli-fixture/seed.json
```


## Codex completion — offline and private runtime verified — 22/10/2026

[Runtime-02](runtime-02/README.md): technicalPASSprivateprofile after owner-approved server recovery,48requestIDs/correlations matched independently across safe/vulnerable and two sources; safe0/vulnerable3restrictedrows,4ownedordersdeleted, directfixturedenied, spoofrejected,2ESsentinels. Namespaceclean, agentsrestored,3PVCUIDsandallreplicasunchanged. Failedruntime-01/initialCRLFrestore/frontend500→200 historyretained; no formalstabilityclaim.42+15testsmỗipin, CIboundary6/Bandit0/imageimportpass; fixtureCIjobprepared, remoteCI/merge/owneracceptancepending. StocksharedIngressnotapplied, ZER42/parentAC03/04notDone.
