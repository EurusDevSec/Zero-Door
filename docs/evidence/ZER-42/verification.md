# ZER-42 SQLi executor — offline verification

Status: **PARTIAL — READY_FOR_CODEX_RETEST_OFFLINE.** Offline only. No lab, broker, Docker, Kubernetes, model
or network was used. No commit/push/PR/merge and no Linear change. Runtime AC-04 is prepared, not run.

Codex review `codex-review.md` (CHANGES_REQUIRED_OFFLINE) raised five P2 findings; all are fixed in one pass
(ZR42-01…05) — see [decision-note.md](decision-note.md) §9 for the design and the "Codex review fixes" case
section below. Pre-fix snapshot and new raw: `scratch/zer42/codex-fix/`.

Baseline: HEAD `7db9d9f` on `zer-41-sqli-fixture` (checkout kept; not switched — dirty outside the package must
be preserved). Design note: [decision-note.md](decision-note.md). Intake + snapshot: `scratch/zer42/claude/`.

## AC mapping

| AC | Scope here | State |
|----|-----------|-------|
| ZER-42 AC-01 = ZER-13 AC-03 | A valid locked template runs end to end through admission + signed dispatch within the locked limits; everything out of scope is refused. | **Met offline** after ZR42-03/04 fixes (pacing, ingress/peer limit); admission + executor + evaluator tested; no live run. |
| ZER-13 AC-04 | before/after, benign control, trusted source IP, request-id stitching. | **Prepared, not run**: request-id/response-id trace + `emit_evidence` event wiring exercised offline against a fake sink; live source-IP proof and producer publish are runtime. |
| ZER-13 AC-01/02 | Fixture design/evidence. | Cross-checked against ZER-41; fixture unchanged. |

## Cases → expected/actual

Commands (offline):
- Go: `cd chaos-worker && go test ./... && go vet ./...` (CI also runs `go test -race` on Linux/CGO).
- Python (both production pins): `cd tests && <pin> -m unittest test_sqli_executor test_command_guards test_command_guard_integration test_command_guard_ci`.
- Effect CLI: `<pin> infrastructure/scripts/sqli_executor_runtime.py --evaluate <result.json>`.
- Fail-before: `NEMESIS=<pin> <pin> docs/evidence/ZER-42/fail_before.py`.

### Admission / validation (Go + Python parity)
- **Valid SQLI admitted** only with opt-in capability enabled, exact fixture target/endpoint, concurrency 1,
  intensity LOW, duration ≤ cap, `customParams == {"template": "<known id>"}`. Expected admit → actual admit
  (Go `TestAdmitSQLiValid`; Python `SqliCommand.test_valid_command_shape`).
- **Refused before I/O**: disabled / capability absent, wrong namespace/service, endpoint host-mismatch, query
  on endpoint, wrong path, concurrency ≠ 1, intensity ≠ LOW, duration over cap/zero, safety namespace/limit
  wrong, empty/extra/wrong-key customParams, non-string/unknown template. Expected reject → actual reject
  (Go `TestAdmitSQLiRejections`; Python `SqliCommand.test_rejections`, `test_duration_clamped_to_capability`).
- **Endpoint shape — narrow ingress profile** (Go `TestValidateSQLiEndpoint`, Python `EndpointValidation`,
  ZR42-04): only `http`, an **in-cluster Service DNS host** `<service>.<namespace>.svc.cluster.local` (never an
  IP literal, so a public TEST-NET / loopback address is refused; never the fixture Service directly, so the
  ingress observation point is preserved), optional numeric port, no query/fragment/userinfo/uppercase, path
  exactly `/fixture/catalog/search`. IP literals, bare hosts, and the direct fixture host rejected on both sides.
- **Legacy unchanged**: a legacy command still rejects any `customParams` (including the SQLi template key) and
  cannot target the fixture (Go `TestLegacyStillRejectsCustomParams`; Python
  `test_legacy_still_rejects_customparams_and_sqli_target`).
- **Policy validation**: bad endpoint / over-ceiling `maxSends`/`maxCommandSec` fail closed (Go
  `TestSQLiPolicyValidation`; Python `SqliPolicyValidation`).
- **Cross-language catalog**: Go and Python catalog ids both equal `tests/fixtures/zer42/catalog-ids.json`; the
  injection category equals `tests/fixtures/zer41/expected.json` `injection.category`; no DELETE/UNION/DDL/`;`
  token in any catalog entry; exactly one injection template (Go
  `TestSQLiCatalogMatchesZER41OracleAndStaysMinimal`, Python `CatalogParity`).

### Executor (budget / cancel / no-retry) — Go `internal/attack/sqli_executor_test.go`
- Disclosure template → one GET with the verbatim category; records the restricted SKUs (`...RecordsRestricted`).
- Benign control → no restricted rows (`...BenignHasNoRestricted`).
- Send cap honoured: exactly `MaxSends` sends (`...RespectsSendCap`).
- Cancel before start → 0 sends, TIMEOUT (`...CancelledBeforeStart`); cancel mid-run → stops creating sends,
  ≤ a couple in flight (`...StopsCreatingSendsOnCancel`).
- Response bounded at 256 KiB (`...BoundsResponse`); redirect not followed (`...DoesNotFollowRedirect`);
  no implicit retry, all-errored command is FAILED not no-effect (`...NoImplicitRetry`); default pace is
  1 send/second (`...DefaultPaceIsOnePerSecond`); every guard rejection sends nothing
  (`...GuardRejectionsSendNothing`).

### Codex review fixes — executor (Go `internal/attack/sqli_executor_test.go`)
- **Malformed 200 is not clean (ZR42-02)**: `{}`, `null`, `results:null`, missing `sku`/`visibility`, negative
  or mismatched `count`, bad visibility → `error=SCHEMA`, never a clean rows=0 observation; the command is
  FAILED (`...RejectsMalformed200`).
- **Pacing cannot burst after a slow response (ZR42-03)**: the next send is scheduled from the actual dispatch
  time (no accumulated-tick catch-up), so every consecutive `startedAt` gap ≥ the pace even when the first
  response is 3× the interval (`...PacingNeverBurstsAfterSlowResponse`).
- **Private-peer preflight (ZR42-04)**: the endpoint host must resolve to a private cluster address; a public
  (TEST-NET), loopback, unresolvable, or mixed-public result is REJECTED (`SQLI_GUARD:peer`) with zero sends; a
  private address proceeds (`...PeerCheck`, via an injectable fake resolver).
- **Request trace (ZR42-05)**: each send carries a neutral `X-Correlation-Id` and records the fixture's
  `X-Request-Id` response id, plus per-send `seq`/`startedAt`/`observedAt` and the observation's
  `clockId`/`clockSource`/`windowStart` (`...RecordsCorrelationAndResponseID`).

### Effect evaluator (H plane, separate from executor) — Python `EffectEvaluator`
- Oracle equals ZER-41 (`test_oracle_matches_zer41`).
- **CONFIRMED** only when a clean, well-formed send actually returned a restricted seed row; `t_eff` is **that
  send's observed instant** (ZR42-01), not the command start — a disclosure at +4 s stamps +4 s
  (`test_confirmed_stamps_the_disclosing_send_not_command_start`); a disclosure without a time/clock is UNKNOWN
  (`test_disclosure_without_time_or_clock_is_unknown`).
- **CONFIRMED_NO_EFFECT** only when clean, well-formed sends cover the whole window `[T_req, T_req+W_eff]` at
  ≤ gap spacing with a verified clock and valid params, and no errored/malformed send falls inside it
  (`test_confirmed_no_effect_needs_full_window_coverage`). A single sample for a long window, an error or a
  malformed 200 inside the window, invalid `min_clean_sends`/`w_eff_s`, or a missing clock → UNKNOWN
  (`test_single_clean_sample...`, `test_error_inside_window...`, `test_malformed_200_in_window...`,
  `test_invalid_eval_params...`, `test_missing_clock...`). Mirrors `measurement.scorer.no_effect`'s coverage rule.
- **UNKNOWN_EFFECT** also for all-errored and a restricted row outside the oracle (`test_all_errored...`,
  `test_restricted_outside_oracle...`).
- **Entrypoint wiring (ZR42-05)** `EmitEvidence`: `emit_evidence` threads one result into a
  `FAULT_EXECUTOR_RESULT` (plane H, source `fault_executor`) then a causally-linked `EFFECT_EVALUATED`
  (`causation_id` = the fault event id) through a plain sink — no broker; both validate, and no
  seed/variant/expected/canary/onset key leaks (`test_entrypoint_emits_two_linked_events`,
  `test_entrypoint_leaks_no_seed`).
- `build_event` produces a contract-valid `EFFECT_EVALUATED` (plane H, source `effect_evaluator`,
  `CONFIRMED ⇔ t_eff != null`); no forbidden key appears (`test_evidence_carries_no_oracle_or_seed_keys`).

### Manifests
- `command-guard-config.yaml` (SQLi block added, disabled) and `sqli-executor-lab.yaml` (render-only, default
  safe): OpenAPI field/type shape PASS (pinned Kubernetes models), load through Python `CommandGuard` and the
  Go policy path (`TestSampleManifestsLoadInGo`), both with `enabled: false` and `sqli.enabled: false`.
  CI also covers them via helm-lint (parse) and Trivy (IaC CRITICAL).

## Results (offline)
- Go: `go test ./...` OK (attack, config, guard, kafka, validation, cmd); `go vet ./...` clean; `gofmt -l` clean.
  SQLi executor tests now 14 (+4: malformed-200, pacing-burst, peer-check, correlation/response-id), plus
  validation + guard SQLi tests. `-race` deferred to CI (no local CGO/gcc).
- Python both pins (nemesis, hephaestus): `test_sqli_executor` **21 OK** (+7 for the rewritten window evaluator
  and `EmitEvidence`); legacy `test_command_guards` 7, `test_command_guard_integration` 13,
  `test_command_guard_ci` 6 — all OK (no regression).
- `check_guard_manifests.py` PASS (command-guard-config + the other manifests). Runtime `--help` no side effect.

## Fail-before (mutation of easy-to-slip boundaries)
`docs/evidence/ZER-42/fail_before.py` — **OVERALL PASS**. Eleven single-boundary mutations each turn exactly one
guarding test RED, then the file is restored byte-for-byte. Original five: drop endpoint exact-match (guard) ·
drop capability-enabled requirement (guard) · accept any path (validation) · accept an unknown template id
(nemesis) · drop the lowercase-endpoint parity guard (nemesis). Codex-fix six: drop the 200-schema check
(ZR42-02) · drop send pacing (ZR42-03) · drop the private-peer preflight (ZR42-04) · accept the fixture Service
directly (ZR42-04) · drop the window end-coverage check (ZR42-01) · drop the fault→effect causation link
(ZR42-05). After restore the real suites are green again (`go ./internal/... rc=0`, `test_sqli_executor rc=0`).

## Baseline / integrity
- ZER-41 locked artifacts unchanged: `services/sqli-fixture/app.py` `37c7a045…`, `tests/fixtures/zer41/seed.json`
  `ec9f818b…`, `tests/fixtures/zer41/expected.json` `a626930d…`.
- Dirty outside the package (AGENTS.md, docs/delivery/*, WORKING-AGREEMENT.md, detail_zero-door.md, learning/)
  untouched; staged empty; no branch switch.
- Incident handled in the open: the first fail-before run used Python text I/O, whose Windows newline
  translation rewrote the three guard files to CRLF. Caught by hash comparison, restored to the exact LF
  originals, and the harness switched to byte I/O; the three files are now byte-identical to before the run.

### Source hashes (sha256)
```
96c2ce26…  chaos-worker/internal/attack/sqli.go            (updated: ZR42-02/03/04/05)
74f3ebd9…  chaos-worker/internal/guard/policy.go           (unchanged this pass)
bd786fa0…  chaos-worker/internal/validation/target.go      (updated: ZR42-04)
2ffecd0c…  chaos-worker/cmd/main.go                         (unchanged this pass)
3b96274b…  chaos-worker/internal/attack/executor.go         (unchanged this pass)
8ddb1fa8…  agent-orchestrator/nemesis/command_guard.py      (updated: ZR42-04)
ae563368…  infrastructure/scripts/sqli_executor_runtime.py  (updated: ZR42-01/02/05)
07f2ca68…  infrastructure/manifests/command-guard-config.yaml (unchanged; traefik ingress host already fits)
1b3c917e…  infrastructure/manifests/sqli-executor-lab.yaml    (unchanged)
0c3c5f4f…  tests/fixtures/zer42/catalog-ids.json              (unchanged)
bec8bb15…  .github/workflows/ci.yml                            (unchanged this pass)
187d1492…  docs/evidence/ZER-42/fail_before.py                (updated: +6 mutations)
```

## Residual / not done / decisions for review
- **No runtime**: lab not run, image NOT_BUILT, manifests NOT_APPLIED; no live NAT/CNI/Fluent Bit/source-IP
  proof. AC-04 is only prepared (offline path + proposed envelope in the runbook).
- **One command = up to MaxSends identical sends** of the same template (sampling within the window); the
  current catalog/command model carries no multi-template batch. Noted, not a defect.
- **Effect evidence representation**: the executor's raw observation rides in `AttackResult.details.sqli`
  (omitempty), now with per-send `seq`/`startedAt`/`observedAt`/`requestId`/`responseId` and the observation
  `clockId`/`clockSource`/`windowStart`. `emit_evidence` threads one result into `FAULT_EXECUTOR_RESULT` →
  causally-linked `EFFECT_EVALUATED` through a plain sink and is exercised end-to-end offline — but only against
  a fake sink; **a live producer/Kafka publish and the actual fixture access-log/source-IP join are runtime
  (AC-04), not run here.** The locked contract/scorer are unchanged.
- **Peer preflight is a resolver check**: the offline preflight resolves the host and gates on a private
  address via an injectable resolver; binding the *dialed* peer end-to-end (TOCTOU-free) and proving the real
  source IP at the fixture is a runtime task for the lab, not covered offline.
- **Endpoint host** in the samples is a Traefik-ingress placeholder that fits the new ingress profile; the real
  private-ingress address is a lab-topology decision (runtime envelope) for Hoàng.
- Out of scope and unchanged: ZER-42 for the other executors, measurement/scorer, Gaia/Hephaestus, dashboard,
  the locked event contract, and the ZER-41 fixture app/seed/expected.
