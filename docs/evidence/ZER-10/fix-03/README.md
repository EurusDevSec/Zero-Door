# ZER-10 / ZER-38 — consolidated Codex fix-03

**Technical verification completed; publication/CI/merge and Hoàng acceptance are separate gates.** Live AC reread from Linear Zero Door on 20/10/2026; no AC or status changed by this package.

Base HEAD `55200c9143565c1773cbff57553a9ce858ffe858`, branch `zer-10-independent-measurement`, staged empty at intake. Hoàng asked Codex to finish the issue directly after repeated handoffs. [before.json](before.json) records all 57 fix-02 package files copied byte-for-byte to `before/`; historical manifests, reviews and evidence remain read-only.

## Findings closed by invariants

| Finding | Change | Discriminating verification |
| --- | --- | --- |
| FX02-R1 | Validate and pin the session after every response, before following any redirect. Issuance pins the first session even across a redirect chain. Cleanup retains its frozen credential and target. | Foreign-session 301/302/303/307/308, first and later hop; issue-step chain; same-session controls. Real loopback foreign cart survives. |
| FX02-R2 | Shared live stop/grace bound reaches already-running H, reference and cleanup exchanges. Earliest stop wins. TCP connect, TLS handshake and send use nonblocking readiness slices; reads recheck the bound before accepting a reply. Final flush cannot restart grace. | Active H/reference/cleanup/final flush, repeated stop, fast controls; stalled TLS and blocked send. Unchanged original probes finish 0.306–0.315 s after stop for grace 0.3 s; pending/unresolved evidence is retained. |
| FX02-N1 | Incident association is per event record, not last-write-wins by conflicting call_id. Global call remains counted once. | Two incidents, reversed ingest, different models, invalid-call decision fallback and distinct-call controls through real Archive/seal/export/load. |

The [genuine fail-before log](fail-before.txt) ran eight new test methods on unchanged fix-02: **17 failing subcases across five methods**, three control methods passed. The same regressions now pass. This uses the actual old source, not a mutant substituted for a missing snapshot.

## AC evidence

| Linear AC | Evidence | Technical verdict |
| --- | --- | --- |
| ZER-10 AC-01 = ZER-38 AC-01 | [Real runtime acceptance](../runtime-01/README.md): real Boutique and SQLite, healthy/failure/recovery, observed markers, cadence, timestamps, raw hashes, restored replicas, owned cleanup | PASS runtime |
| AC-02 | [Offline E01](offline/offline-summary.json): effect→detect 30 s, detect→recovery 60 s, total 90 s, reaction 19 s; [178 contract comparisons](crosscheck.json); recovery is probe-derived, not action SUCCESS | PASS controlled/raw recompute; no live detector-performance claim |
| AC-03 | 134-test suite: failed action without recovery, missing/timeout/censored states, explicit denominators and unknown uptime; preserved frontend timeout/skips and failed cold warm-ups in real receipt | PASS; missing is never 0/PASS |
| AC-04 | Decision/recovery/usage/cost tests and independent M11 archive cases, preserving retries, proposal/guard/action distinctions and conflicting-call lower bounds | PASS controlled traces; no real paid usage claim |

## Verification

- [Full offline run](offline.txt): **134/134**, no skips/errors; E01 matches hand values. First attempt had a real Windows select-error classification regression; it was fixed and [failed log](offline-attempt1.txt) retained.
- [Original counterexamples](replay.txt): **29/29**, unchanged historical scripts remain read-only.
- [ZER-37 crosscheck](crosscheck.json): **178/178** values on 62 cases.
- [Original stop probe](stop-io.json), [redirect](redirect.json), [usage/trial matrix](metrics.json) compare actual JSON, not exit status alone.
- Independent review lenses report no remaining P1/P2 in the changed probe and usage boundaries. Their notes/results are preserved with this package.
- The mutation gate required by CI and Bandit results are recorded separately; do not substitute earlier fix-02 results for a new run.

OS DNS lookup, certificate-store setup, filesystem fsync and hard process kill are not universally interruptible by this socket loop. The executed runtime uses numeric IP origins and HTTP, with measured timing and this limitation stated. Formal timing/clock pilot values remain open in the later protocol work.

The live run does not close ZER-41, ZER-11/39, G1 or a research benchmark. Code-changing Done still requires independent review, publication, CI, merge and owner acceptance. No Git/Linear publication authority is inferred from the lab approval.

### Final local gates

[Mutation evidence](mutants.json): all40registeredmutants were caught. The first exact command caught31 then aborted on an obsolete source selector; its log remains mutants-attempt1.txt. Two selectors were adapted to bounded_deadline and the remaining9 were run by the same checker: control107/107 and9/9caught. Full baseline134/134 also passed; this is explicitly PASS_RESUMED, not one uninterrupted command. Remote CI runs the complete standard command. [Bandit](bandit.json):0findings/0errors.

`check_package.py --check` verifies the shareable sealed package; `--check --local` additionally checks8ownerfiles alreadydirty/unpublished before this issue. Only the new NOW pointer is staged; existing owner changes are retained. Git attributes preserve exact accepted bytes because core.autocrlf=input would otherwise rewrite source/snapshots at commit.
