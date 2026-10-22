# ZER-41 runtime-02 — technical PASS in the approved private profile

22/10/2026, Asia/Saigon. Owner approved one server recovery and the private fixture retest, capped35min
including10mincleanup/restore. Runtime source HEAD4ccd6c3 dirty; appSHA37c7a045e098… unchanged.
**Pending remote CI, merge and owner acceptance; not Linear Done.** [Receipt](verification.json).

## AC evidence

| Check | Actual result |
| --- | --- |
|Packaged fixture/database|Image built once in runtime-01, reused here; non-root/read-only root and dataemptyDir64Mi worked. Runtime imageID703664716e063e062f5babef7487f519647e3b9ca901a30afba823aef8b3370f|
|Ingress/query|Private Traefik file-provider /fixture route, ClusterIP8000→fixture9140.48requests,24perprofile|
|SQLi oracle|Both sources: safe returns0restrictedrows; vulnerable returns exactly3synthetic restricted SKUs from the fixed seed; benign queries stay public|
|Source IP and spoof|SourceA10.42.1.199 and B10.42.1.200 observed distinctly through proxy10.42.1.201; forged XFF203.0.113.77 was not accepted|
|Isolation|Direct fixture TCP from both sources denied, with source egress explicitly allowing that destination; private proxy route succeeds|
|Trace and business CRUD|48unique requestIDs +48unique neutral correlations; independent readback, nonce ownership, delete and404after-delete for4orders|
|Logs|Both profile sentinels received in Elasticsearch via existing FluentBit;2read-onlyqueries; service log has no profile field|
|Cleanup and recovery|Namespace UID-conditioned DELETE verified absent; agents restored1each, all desired replicas match baseline,3PVCUIDs/volume names unchanged|

The application was held in an init-container gate on the existing/data volume until the exact Pod's
node policy rule was observed. The gate was applied independently to safe and vulnerable rollouts.
After the approved server restart, rules appeared (safe round2, vulnerable round1), and the actual
negative connection tests passed. This confirms the recovered profile; it does not establish the earlier
controller's underlying defect or policy enforcement on every node.

## Independent raw verification

[Independent comparison](independent-verification.json) recomputes the48ID/status/IP joins and SQLi
contrast from raw responses and the seed, verifies four owned order deletions and distinct sourceIPs.
It does not use the runner's PASS string as its oracle. Raw in attempt-01/raw; applied variant and
executed helpers are retained in scripts. The stock shared-Ingress manifest remains NOT_APPLIED.
This isolated file-provider proxy is the owner-approved runtime variant, not a shared-controller proof.

## Retained failures and restoration

Runtime-01 retains all three earlier failed attempts; none is relabeled PASS. Here the first automatic
restore failed because Windows produced CRLF in the replica TSV (kubectl rejected1\r). That failure is
preserved in recovery.log and recovery-process-initial.json. Replica values were regenerated literally
from the captured baseline with LF and restore repeated; restore-verification.json confirms final state.
Actual verified restoration completed at2026-10-22T09:39:02.631Z,496s after turn start,
inside35min. The future helper now emits LF. No extra node restart, cluster recreate, PVC/volume delete,
manual firewall change, model/paidAPI call or external target was used.

A subsequent read-only frontend check saw HTTP500 (cart connection refused). After an independently
observed cart-container restart, one explicit recheck returned200. Both responses/logs are kept. PodReady
alone is not business recovery, and this is not a stability/uptime99.9% claim. We did not restart another
node, modify Boutique replicas or suppress the failed response.

## Verification and limits

- Offline42main+15HTTP per production pin after the test-capture fix; delayed-emit before/after control.
- Existing CI workflow-boundary6tests and fixtureBandit0; packaged image import succeeds with no network.
- Dedicated fixture CI job is prepared for both production test locks; remote CI has not run yet.
-48manual HTTPrequests;78observed fixture accessrecords,30health/readiness. Failed kubelet attempts
  are not independently counted; do not cite78as an exact total network-attempt count. The configured
  health/readiness cadence and bounded windows are recorded; no formal experiment budget claim.
- Service stdout/Traefik logs and Elasticsearch ingestion are runtime proof; no Gaia detection/healer,
  HPA/containment, executorZER42, full parentZER13, multi-node isolation or formal research KPI claim.
- No commit/push/PR/merge or Linear write in this turn. ParentAC03/04 and ZER42 remain separate.

Empty per-poll policy diagnostics are consolidated losslessly in raw/empty-policy-observations.json within the applicable attempt (original names, bytes, hashes and observation times); original empty files are also retained locally. Request/response, failure and positive policy records remain unchanged.
