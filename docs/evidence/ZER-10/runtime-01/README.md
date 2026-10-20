# ZER-10 / ZER-38 — runtime acceptance, 20/10/2026

**AC-01 runtime PASS**, independently checked in [audit.json](audit.json) by [audit_raw.py](audit_raw.py). This is service/probe acceptance, not a research benchmark or a claim about detector/LLM performance.

Hoàng explicitly approved k3d-zero-door, temporary H/probe/SQLite namespace, at most 15 minutes and 30 transactions per target, one-at-a-time frontend/checkoutservice scale-down and restoration, owned-resource cleanup, no paid API. The successful pod ran the frozen [attempt-03 source](attempt-03/source-manifest.json), image identified in [image-id.txt](attempt-03/image-id.txt). Probe and harness share the same container clock (`HOST_SHARED`, observed resolution 1 ms); neither imports the healer. H uses the production authenticated gateway and direct durable 201 acknowledgements, not Kafka 202.

## Actual observations

| Phase | Samples | Observed result |
| --- | ---: | --- |
| Boutique healthy | 3 | Real product/cart/checkout, all pass, 233–282 ms |
| Checkoutservice replicas 0 | 3 | All fail `STATUS_500`; independent home still 200 |
| Checkoutservice restored to 3 | 3 | All pass, 251–450 ms |
| Frontend replicas 0 | 3 | One step timeout, two connect failures; two skipped slots remain visible |
| Frontend restored to 1 | 3 | All pass, 37–393 ms |
| SQLite fixture healthy | 3 | HTTP create → committed file-backed SQL → read via another connection → owned delete, all pass |
| SQLite held under an exclusive write lock | 3 | All fail `STATUS_503` from actual SQLite contention; process `/health` stays 200 |
| SQLite lock released | 3 | All pass; final database contains 0 probe rows |

The fixed cadence is Δ=1 s, K=3, S=2 s, L=2000 ms, gap=2 s; these are PILOT inputs, not locked formal parameters. Measured start periods are in the audit. The unavailable frontend produced a 3.010 s interval and two skipped slots, not three invented one-second observations. Every emitted sample has a real timestamp, duration and status. Steady healthy samples all meet the unchanged 2 s threshold.

The [sealed H export](attempt-03/raw-final/export-H/export.json) has **66 records / 24 samples**, raw SHA-256 `b76675a84e1ace819e7a6037e6d1b8f50d82aa0b6ff213f8d4de3a78b7c1d6ce`. Independent audit verifies file hashes/sizes, unique IDs, trial windows, sequence 0/1/2, clock registration, start/end duration arithmetic, failure reasons and deployment restoration. [Recompute](recompute.txt) reads the real sealed export. There is no detector or ATTACK_REQUESTED cohort in this acceptance profile: incident N=0/EMPTY is expected, not a PASS for MTTD/MTTR.

## Failed preparation and recovery are retained

1. Initial pod did not import `/app`; no target was scaled. Its pod log and host receipt remain at this folder's root. The image was corrected with `PYTHONPATH=/app`.
2. [Attempt-02](attempt-02/raw/observation.json) observed a real cold home response around 9.2 s and a transaction timeout at 10 s. It is retained as a failed observation. Subsequent measurement used an explicit recorded warm-up outside the trial window; the healthy threshold was never increased.
3. During attempt-03, the host script compared a UID containing Windows CRLF and stopped at restoration. UID-checked restoration immediately returned checkoutservice to 3 replicas; [receipt](attempt-03/restored-after-crlf.json). The script now strips CR and uses an explicit baseline argument. Existing successful phases were resumed, not repeated.
4. The first frontend recovery warm-up failed to connect although the deployment was Ready. Its [actual result](attempt-03/raw-resumed/frontend-restored.warmup.json) is retained. After a separate real GET returned 200, a second warm-up succeeded; only then was the recovery trial started. This is a cold-routing/availability limitation, not hidden in a healthy sample.
5. The final namespace delete request succeeded but its watch timed out. A separate read-back verified absence. The two earlier preparation namespaces were also deleted; [complete namespace read-back](namespaces-final.json) and the audit confirm all three are absent.

The successful harness wall time was **321.7 s**. It counted **20 Boutique transactions, including failed/successful warm-ups, and 9 fixture transactions**. Attempt-02 adds one failed Boutique transaction: **21/30 total Boutique, 9/30 fixture**. Read-only diagnostic home GETs did not submit orders. The first namespace was created at 22:50:57 +07, final business export at 23:00:52 +07, and cleanup was issued around 23:02:58 +07. Raw snapshots before and after resumes remain separate.

The initial/final deployment UID and entire spec match, frontend is **1/1**, checkoutservice **3/3**, no HPA or unrelated deployment was changed. No token, cookie, real card or API credential is in the raw export. Form card data is Online Boutique demo input.

## Boundary of this fixture

[acceptance.py](acceptance.py) provides a real SQLite CRUD prerequisite for validating the probe. It has parameterized SQL, not a SQL injection executor or vulnerable route. It does **not** complete ZER-41, R2, containment, the formal experiment, uptime 99.9%, or any AI claim. The fixture and H archive were temporary and exported before cleanup.

Scripts [run.sh](run.sh), [resume.sh](resume.sh), and [complete.sh](complete.sh) document the executed sequence; they perform lab actions and are not part of offline CI. A future run needs its own explicit operating scope. Existing receipts/raw and failed observations must not be overwritten.
