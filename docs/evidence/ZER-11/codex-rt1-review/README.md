# Codex H-RT1 review evidence — 21/10/2026

Verdict CHANGES_REQUIRED / NOT_READY_FOR_RUNTIME; [report](../codex-rt1-review.md). Five concrete findings, no source/lab/model/publication/Linear writes.

- Host counterexamples.jsonl: managedFields default abort; lost create ACK leaves namespace but CLEAN; host ENOSPC skips P7 (Gaia/Hephaestus remain0).
- pod-replay.json: false positive-control success and historical controller/HPA attribution; root reran these assertions.
- Full suite logs: Nemesis1 17/17, Hephaestus1 17/17; Nemesis2 2FAIL+1ERROR/17. Separate diagnostic02 3/3 PASS does not erase that failure. diagnostic.log capture failure is reviewer instrumentation copying locked .owner, not a package defect.
- Hash intake21/21, read-only190/190, protected10/10; only note/NOW later append/prepend. Bandit0, dashboard33/modes7/CI6/profile PASS.
- Local GitNexus index finished; MCP stale/closed transport; CLI context/impact/PDG used. Taint explain unavailable via CLI/MCP, no full taint coverage claim. Detect-changes includes other dirty packages; exact manifest determines this review scope.

From repo root, Bash (pinned Python already present):

~~~bash
scratch/zer12/production-nemesis/Scripts/python.exe -B docs/evidence/ZER-11/codex-rt1-review/counterexamples.py
scratch/zer12/production-nemesis/Scripts/python.exe -B docs/evidence/ZER-11/codex-rt1-review/pod-counterexamples.py
~~~

These are evidence probes asserting the broken observations at this revision; they are not acceptance tests for a corrected revision. Keep them read-only and add fixed-expectation regressions for rt1-fix-01. Only portable root discovery differs from executed scratch copies. New pod/evaluator source and work evidence are fake/loopback only. No active reviewer server/process remains after tests.
