# ZER-27 — Formal measurement checkpoint, 12 November 2026

**AC-01 incomplete. FORMAL_HOLD. No formal trials are reported here.** This checkpoint preserves completed code and readiness observations so work can resume without repeating the day’s investigation. Merging this checkpoint does not authorize a formal experiment or activate the formal configuration.

## Implemented code

- Explicit formal configuration and pre-guard decision capture for rules and LLM callers. Timeout, invalid schema and resolver errors retain their specified outcomes; missing evidence stays unknown.
- Durable B2 budget claims, call-record archival before subsequent decisions/actions, and session-stop propagation when evidence or usage cannot be verified.
- Formal C5-only MTTD/reaction denominators, first-action scoring and digest-checked audit originals. Recovery metrics for this design remain NOT_EVALUABLE_BY_DESIGN.
- Strict containment evidence joining. The join is not connected to the live formal evaluator yet; runtime M12 remains UNVERIFIED.

These paths are opt-in. Existing non-formal callers retain their behavior. No model key, formal schedule or deployment configuration is included.

## Readiness observations

The owner-held local evidence was sealed before publication; raw logs, archives and host details are not published in this checkpoint. These are local verification results reported by the implementer, not an independently reproduced formal dataset.

| Observation | Result | Limit |
| --- | --- | --- |
| Benign Boutique window | 66/66 samples passed across 330 s at 5 s spacing; two additional warm-up GETs; no skipped slots or undelivered records | B0/C0 readiness only; no C5, model calls or formal trial |
| Admission | 25 samples over 120.093 s; minimum Windows available memory 3,074 MiB; 3,090 MiB at claim | The admission floor remained 2,868 MiB |
| Work resources | Minimum Windows/guest available memory 3,074/2,419 MiB; maximum memory PSI 0; maximum telemetry age 1.078 s | One window, not a reliability guarantee |
| H/O | Separate process identities/keys, common-kernel clock, sealed exports and raw replay passed | Applies to the benign helper |
| Native B2/O integration | Two synthetic model-call records and one NO_ACTION decision archived; durable ledger settled; caller/recorder clock and access checks passed | Fake provider and Kubernetes; direct HTTP recorder, not Kafka or a live B2/C5 experiment |
| Cleanup | Helper, forward and telemetry client removed; logging specs restored; all three lab nodes stopped | Read back locally after the runs |

WSL remained at 5.5 GiB, four vCPUs and 2 GiB swap. The benign preparation temporarily paused Elasticsearch/Fluent Bit and issued one 1 GiB proactive file-cache reclaim request before quiet/admission. Both logging specs were restored. The bounded session allocation changed to 2,700 s while the 1,500 s work cutoff and 1,800 s claim reserve remained unchanged. Guard thresholds were retained. This preparation has not been approved as the common formal profile; verify the real detector/telemetry dependencies before adopting it. The observed before/after memory change does not establish a unique root cause or the exact amount returned to Windows.

Failures preceding the successful run remain in local evidence, including a pre-mutation Engine timeout and an admission failure at 2,195 MiB. The first native O harness attempt omitted an incident binding and was rejected before a call; its receipt/source/log survive, but its unsealed tmpfs archive was not exported. Later attempts preserve caller clock and raw ledger. None of these attempts count as formal observations.

Local completion manifest: SHA-256 `6aeac0946ed5eb8f1ac9599f4c50e5dd625cecc8295e573916a8472c2703bf22`, covering 387 owner-held files/references. A hash identifies that local snapshot; it does not make unpublished evidence independently accessible.

## BM operation selected by the owner

The owner will operate BM. The harness hides/seals schedule and onset, the pinned scorer computes metrics, and Codex/Claude may inspect evidence after the cohort. The [solo-operation addendum](../ZER-53/solo-operation-addendum.md) records this choice and its review requirement. It preserves descriptive-only BM reporting and UNBLINDED_BY_DESIGN for the second BM position in each block. It does not claim a second independent human evaluator or human-level independent blinded evaluation. The [locked base protocol](../ZER-53/protocol.md) remains byte-for-byte unchanged.

## Remaining before formal admission

1. Wire and verify one real B2/C5 readiness cycle at 5.5 GiB, including the intended session caller, recorder/transport, H containment capture, probe/scorer join, clock and CLEAN cleanup.
2. Fix and seal five variant seeds before checking their schema/oracle and the pinned detector; retain misses without selecting replacements.
3. Verify the O-only BM console, alert-display timestamp, actual manual decisions/actions and readback. Review and pin the solo-operation addendum and the common resource profile before formal.
4. Retain original audit material for every required surface and confirm account credit/spend limits before paid inference.

No synthetic-provider result proves model performance or containment. Missing coverage remains UNKNOWN/UNVERIFIED; merging does not close ZER-27.

## Offline verification

CI runs the suites on pinned Python 3.11 dependencies. From a repository checkout with those dependencies:

~~~bash
python -B -m unittest discover -s tests -p test_formal_config.py
python -B -m unittest discover -s tests -p test_formal_readiness.py
python -B -m unittest discover -s tests -p test_measurement_formal.py
~~~

These suites use fake transports/fixtures; they do not admit lab or provider operations. Related legacy suites and image-import checks must also pass before merge.
