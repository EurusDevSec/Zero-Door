# Independent fix-03 M11 lens

Verdict: PASS_OFFLINE for the bounded changed attribution path; no P1/P2 or concrete P3 found. FX02-N1 is closed in this scope.

Compared current metrics.py against exact fix-03/before source. Production delta is the narrow substitution of event_id -> incident for call records; existing decision_id fallback remains for invalid records. Existing call_id de-dup/counting/conflict rules and lower-bound status are preserved. No extra service, pipeline or unnecessary abstraction was introduced.

Ran five independently assembled traces through real temporary Archive/seal/export/load and scorer/run_metrics:
- distinct calls in two trials/incident: 2 global calls, both incident buckets COMPLETE, all levels COMPLETE, no lower-bound warning;
- shared conflicting call_id: both incident buckets MISSING, all other named levels MISSING, global calls=1, incident calls sum=1, no conflicting token/cost added;
- same trace in reversed ingest order: same coverage/count invariants;
- conflict also names another model: both models and both incidents MISSING, no double count;
- second call invalid (usage field absent): valid first incident COMPLETE, second incident attributed via its valid decision and MISSING; top-level MISSING and lower bound, global valid calls=1.

All five assertions PASS (results.json); all incident labels remain RECOVERED with N=2, as model metadata errors do not alter independently derived business recovery. Source and docs untouched.

This is offline review, not full issue acceptance. Parent owns runtime/CI/publication/owner-acceptance and fixture/contract boundaries.
