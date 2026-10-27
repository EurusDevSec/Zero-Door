# ZER-42 Codex fix-02 — ready for Claude cross-review offline

**Verdict: READY_FOR_CLAUDE_REVIEW_OFFLINE / PARTIAL — 26/10/2026 (+07:00).** Codex fixed the four
blocking findings `FX42-R1…R4` from `../codex-retest.md` as one outcome-sized package. This is not runtime
acceptance or Done: no image was built, no manifest was applied, no lab/model/API was run, and no Git
publication or Linear write occurred.

## Baseline and boundary

- Intake: branch `zer-41-sqli-fixture`, HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, staged empty.
- Exact before-source hashes and scope are in `scratch/zer42/codex-fix02/source-baseline.json` and `plan.md`;
  before copies are in `scratch/zer42/codex-fix02/before/`.
- Existing unrelated dirty files were preserved. ZER-41 remained locked: `app.py` `37c7a045…a755`, seed
  `ec9f818b…f90b`, expected `a626930d…9407`; accepted runtime-02 receipt remained
  `60e6e60b…52aa`. The Codex retest report remained `e1e53052…8aa4`.

## Findings closed offline

| Finding | Change | Independent check/result |
| --- | --- | --- |
| FX42-R1 timestamp/consumer | Go stamps `observedAt` only after body read/validation or terminal error; UTC is floored to contract `.mmmZ`. CI consumes an actual Go JSON result through Python evaluator, event builder and scorer. | Delayed-body Go control proves the observation follows body completion. Go → evaluator → scorer bridge PASS; scorer accepts `t_eff`. |
| FX42-R2 missing/contradictory raw | Evaluator validates finite parameters, collection/entry shape, unique sequence, required times/order, counts and positive restricted SKU evidence. Missing or inconsistent evidence remains `UNKNOWN_EFFECT`; valid controls retain their prior result. | New Python cases cover null entry, error without time, positive restricted count without SKUs and infinite gap. Fail-before shows the old code returned NO_EFFECT or raised `AttributeError`; current code returns UNKNOWN. |
| FX42-R3 endpoint/actual peer | Python/Go accept only the runtime-02 Service `zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000` and exact path. Worker requires operator-read-back `ZD_SQLI_INGRESS_IP`; DNS must equal that private IP, transport dials the numeric IP once and verifies the connected peer while preserving Host/route. | Fake resolver/dialer proves no unchecked re-resolution; wrong authority/peer fails closed. Fail-before proves old target validation admitted an arbitrary in-cluster Service. |
| FX42-R4 durable evidence/export | Full bounded executor result plus canonical SHA-256 is retained in `FAULT_EXECUTOR_RESULT`. A write-once local bundle is replayed unchanged through the existing H Archive, seal/export and `measurement.raw.Export`; recheck validates context, causation, raw hash and recomputed effect. Executor-only NO_EFFECT is deliberately downgraded to UNKNOWN until independent `PROBE_SAMPLE` coverage exists. | Archive/export/replay/recheck regression PASS, including exact duplicate replay and binding conflict. Runbook §6 now proposes concrete time/pod/image/HTTP/ES/cleanup limits without granting runtime authority. |

During final review, Codex found that the accepted ZER-41 Service name was `zer41-private-ingress`, not the
technology label `traefik`; source, policies, manifests, tests and runbook were corrected to the receipt-backed
identity. The first full check then correctly failed because one Python fixture still used the old endpoint; it
was updated and the full check rerun. The verification script was also tightened so unformatted Go files fail
instead of merely printing `gofmt -d` output.

## Verification

- `scratch/zer42/codex-fix02/fail-before.sh`: PASS. Old snapshot reproduces early timestamp + generic Service
  admission, NO_EFFECT from incomplete evidence, null crash and missing archive adapter; current source rejects
  or returns UNKNOWN as expected.
- `scratch/zer42/codex-fix02/bridge.sh`: PASS. Actual Go result with delayed body → evaluator → contract event →
  scorer, not a hand-authored JSON-only substitute.
- Python SQLi suite: **24/24** on both Nemesis and Hephaestus production pins.
- Legacy command-guard regression: **7/7** on both pins.
- Bandit evaluator at CI threshold `-lll -iii`: zero findings.
- Go: all six packages PASS; `go vet ./...` PASS; `gofmt -l` empty.
- `git diff --check`: PASS.

## Remaining before acceptance

- Claude must cross-review this delta independently, especially peer pinning, archive/export replay and the
  decision to keep executor-only NO_EFFECT as UNKNOWN.
- Linux CI/race, image build/import, broker/runtime topology and AC-04 lab evidence are not yet observed.
- A future lab requires a new, explicit authorization against the proposed envelope in
  `docs/runbooks/sqli-executor.md` §6. Do not reuse ZER-41's past permission.
- ZER-42 and parent ZER-13 remain not Done until cross-review, approved runtime, CI/publication and owner
  acceptance are complete.

