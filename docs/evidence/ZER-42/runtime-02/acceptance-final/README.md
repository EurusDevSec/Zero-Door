# ZER-42 — technical acceptance closure, 27/10/2026

**TECHNICAL_PASS_READY_FOR_PUBLICATION.** Retained attempt `zer42-74545a02be28` contains all four cases. No new application test request was needed. This receipt closes evidence packaging and owned-topic cleanup; it does not mark Done or authorize Git publication.

Base HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, branch `zer-41-sqli-fixture`; existing dirty work/staging retained. Live ZER-42 AC-01 and parent ZER-13 AC-03/04 were read via the named Zero Door connection on 27/10; both issues were In Progress at that read.

## Technical AC result

Original observations: **27/10/2026 approximately 16:56–16:58 Asia/Saigon (09:56–09:58 UTC)**. Repack: 17:22 Asia/Saigon. See [acceptance.json](acceptance.json) and [request-joins.json](request-joins.json).

| Profile / existing template | Sends | Rows per response | Restricted per response | Technical result | Formal H status |
| --- | ---: | ---: | ---: | --- | --- |
| safe / disclose-restricted | 3 | 0 | 0 | PASS | UNKNOWN_EFFECT |
| safe / benign-apparel | 3 | 2 | 0 | PASS | UNKNOWN_EFFECT |
| vulnerable / disclose-restricted | 3 | 3 | 3 | PASS | CONFIRMED |
| vulnerable / benign-apparel | 3 | 2 | 0 | PASS | UNKNOWN_EFFECT |

- **ZER-42 AC-01 / ZER-13 AC-03:** four unique commands/results, three sends each, five-second cap, concurrency one. Invalid-template runtime control returned HTTP400/`SQLI_TEMPLATE` without a fifth command. Existing admission/evaluator/parity tests pass on both production dependency pins.
- **ZER-13 AC-04:** all **12/12** executor correlation IDs join once to fixture response IDs and proxy origin/downstream IDs. Status/row counts agree. Vulnerable disclosure returned exactly the three fixed synthetic restricted SKUs; safe disclosure returned none. Benign commands returned the same two public rows in both profiles.
- **IP/isolation:** four source-A/B benign controls join responses/logs; two captured source Pod IPs differ. Proxy ClientHost matches fixture client_ip; trusted TCP peer matches captured proxy Pod IP. Forged XFF `203.0.113.77` never replaces the observed source. Four direct fixture TCP controls were denied. Each profile was released only after a successful policy snapshot contained its exact Pod hook.
- **Replay:** the command-topic read after completed-ID replay contains only the original four records. Logs collected afterward contain exactly twelve executor GETs and four source-control GETs: no additional command/request in the retained window.

This closes the bounded executor/effect/benign/trace/IP technical scope. It provides no containment/R3/AI/KPI claim, no claim of a Boutique vulnerability, and does not close G2's other vectors.

## Packaging fix and provenance

The old renderer padded a twelve-hex label with zeros, creating run/trial IDs without the UUIDv4 version/variant bits required by the event contract. Collection completed before the first bundle failed. Renderer IDs now use stable UUIDv4-shaped values derived from the unique run label. Contract/scorer/oracle/fixture/executor source are unchanged.

Historical signed commands are neither edited nor re-signed. [id-mapping.json](id-mapping.json) binds their original context and envelope hash to new H packaging IDs/incidents. Method `zer42-h-repack/1` explicitly identifies a **post-collection operation**, not an in-run producer. Raw result bodies/timestamps and UNKNOWN clock provenance remain intact.

Four write-once bundles passed existing H Archive → export → verified loader → raw/hash recomputation. There is one CONFIRMED disclosure and three UNKNOWN_EFFECT cases. Per [the reviewed preparation](../../runtime-prep/README.md), executor-only safe/benign observations remain UNKNOWN without independent PROBE_SAMPLE coverage; their response contrast is independently checked as technical AC evidence, not formal research NO_EFFECT/KPI proof.

[original-artifact-sha256.json](original-artifact-sha256.json) verifies **160 original files**, including the FAILED/INVALID_ID receipt, unchanged. Seven historical source-manifest hashes still match. Actor image tags, matching host digests and successful Pod Ready waits remain; final actor container-imageID/PodIP snapshots were not retained. Executor IP is observed via command-correlated fixture/proxy requests, not represented as a captured actor Pod status. Ephemeral keys were not archived: original signatures remain, but cannot now be independently cryptographically revalidated.

## Live cleanup

[cleanup-receipt.json](cleanup-receipt.json), **27/10/2026 17:17:34 Asia/Saigon**, verifies:

- namespace absent; historical deletion tied to captured UID/run label;
- exactly `zer42-c2d30a7145ff.{commands,results}` and `zer42-15ddc1ba1c91.{commands,results}` absent after deletion/polling;
- first pair owned by successful creates; second pair traced to earlier accidental reads of those names: [ownership references](topic-ownership.json);
- unrelated topics preserved; all existing deployment UID/replica/generation values and all three PVC UID/volume pairs identical to historical-after and current-before snapshots.

No new test traffic, namespace, image, workload change, restart, cloud/model call or external-system action occurred. The old harness deleted topics before stopping consumers, allowing possible auto-creation; exact Kafka internal causality was not captured. Cleanup now removes/verifies the owned namespace first and defers topics if ownership/shutdown cannot be verified. Live cleanup ran with actors absent and succeeded. The original unresolved receipt remains preserved.

## Verification and delivery boundary

- Actual before snapshots reproduce both regressions: malformed IDs and topics deleted before consumer shutdown. [Expected failing tests](fail-before.log), [before sources](before/).
- Packaging/cleanup **2/2 per pin**, including unchanged malformed-ID rejection and wrong-owner refusal: [Nemesis](packaging-nemesis.log), [Hephaestus](packaging-hephaestus.log).
- Existing SQLi tests **24/24 per pin**: [Nemesis](executor-nemesis.log), [Hephaestus](executor-hephaestus.log).
- Final artifact recheck passed on the other production pin; direct new CI test invocation passed. Bandit at the existing high-severity/high-confidence threshold passed: **0 medium/high**, 101 low-severity findings, principally assertions/subprocess use. No claim of zero total findings. YAML inspection and `git diff --check` passed. No Go source changed; previous Go checks were not repeated. Remote CI has not run. GitNexus refresh was attempted locally and timed out after 180s; graph freshness remains unverified, so all acceptance conclusions use direct source/raw/export checks.

Delta: runtime-prep renderer/run cleanup, `tests/test_sqli_runtime_packaging.py`, one added invocation in existing r2-fixture CI matrix, runtime-02 reconciliation/cleanup/read-only-check helpers and final artifacts, runtime README, technical handoff and NOW. [Intake](intake.json) records before hashes/scope. Unrelated dirty work remains untouched.

Repeat verification without lab access:

```bash
cd /r/_Projects/Eurus_Workspace/zero_door
scratch/zer12/production-hephaestus/Scripts/python.exe -B docs/evidence/ZER-42/runtime-02/check_acceptance.py
```

Reconciliation/cleanup outputs are write-once; use the read-only checker for review. **Publication/review ready; independent delta review, remote CI, merge and Hoang acceptance remain before Done.** No commit/push/PR/Linear change or cross-chat message was performed.
