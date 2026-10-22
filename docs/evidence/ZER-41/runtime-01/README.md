# ZER-41 private runtime-01 — BLOCKED_RUNTIME_ISOLATION

Date: 22/10/2026, Asia/Saigon. HEAD4ccd6c3, dirty fixture package; no commit/Linear writes.
Owner explicitly approved the private envelope and F-05 synthetic restricted-row oracle in this chat.
[Machine receipt](verification.json). This is **not** a passed runtime AC or a formal experiment.

## Completed

- Test-capture race fixed without changing application behavior:42main+15HTTP on both dependency pins;
  delayed emit300ms fails the actual old test and passes the fixed test (two passes per pin).
- Built/imported one fixture image from app37c7a045e098; Docker image ID `sha256:e95d058b11defba91a76d3a13c703811f846ddc40e877bf3459fc8c1b6f6b17c`.
- Applied only private overlays in an owned temporary namespace: fixture + private Traefik + two sources,
  four Pods maximum, existing/data64Mi. No shared Kubernetes Ingress or host binding/firewall changes.
- Attempt02 sourceA:12manual responses independently match fixture request ID, correlation, status and
  observed end-client IP. Benign seed searches, safe injection contrast, CRUD independent readback and
  nonce-owned delete passed for this source. Forged XFF203.0.113.77 did not replace sourceA IP.
  [Independent comparison](safe-a-observations.json). SourceB was not run; do not generalize to two sources.

## Attempts retained

| Attempt | Result | Last cleanup, elapsed from original turn start |
| --- | --- | --- |
|01|Safe route connection refused; stopped before any business response|103s, CLEAN|
|02|Private port-consistent route works; direct fixture TCP connection from sourceA also succeeds, contrary to required isolation; stopped before vulnerable|393s, CLEAN|
|03|Application held in init until actual node policy rule appears; required owned-Pod rule not observed within bounded gate; application never released|827s, CLEAN|

Attempt01 changed private Service/target-port wiring, readiness and log-stream timeout together before02;
this does not isolate the first failure's individual root cause. All original logs/scripts are retained.
No retry-until-green or passing result was substituted for these failures.

## Remaining blocker and limits

The current lab did not prove enforcement for the new namespace. Attempt02's direct TCP connection must
be treated as a failed isolation gate. Attempt03 found no owned-namespace rule through either nft/legacy
views while the application was held in init. This does not establish the underlying controller defect.
Filtered current-boot logs show K3s started the embedded controller; bridge netfilter and IP forwarding
are1. No disable-network-policy flag was found in the inspected configuration. No controller/node restart
or firewall change was attempted. Existing old chains alone do not prove current reconciliation.

K3s uses an embedded kube-router policy controller ([official documentation](https://docs.k3s.io/networking/networking-services#network-policy-controller),
[exact K3s source](https://github.com/k3s-io/k3s/blob/v1.31.5%2Bk3s1/pkg/agent/netpol/netpol.go)); the
read-only investigation does not prove a separate pod restart target exists or that a restart will fix it.

- Vulnerable profile/effect runtime: **NOT_RUN** in all three attempts.
- Two-source trusted-IP and complete trace: **PARTIAL**, only sourceA verified safe.
- Elasticsearch ingestion: **NOT_RUN**,0of12queries used.
- Manual HTTP:13attempts total,12responses completed. Observed access records:4+19; exact total including
  failed kubelet attempts is UNKNOWN because attempt01's log stream timed out. Do not report a passing
  complete request-budget audit. Later streams used no global request timeout.
- Stock shared-Ingress manifest: **NOT_APPLIED**. Private file-provider proxy is a distinct profile.
- SQLi containment/HPA/ZER-42/parent AC03/04: not established by this turn.

## Cleanup and next action

All three DELETE operations used namespace UID preconditions, fresh owner-label checks, and verified
namespace absence. Last owned resource cleanup finished at13m47s of the original30min turn. Final
namespace read-back is empty. No vulnerable workload remains. Owned log streams were stopped; no ES
port-forward was started. The built image is retained as declared. Existing replicas/PVCs were not changed.

A concrete recovery proposal is prepared but **not authorized**: pause Gaia/Hephaestus, restart only the
existing k3d-zero-door-server-0 container once to reinitialize its embedded controller, read back API/node,
PVC UIDs and workload state, then rerun the same private test only if enforcement is demonstrated. This
has broader effects than the temporary namespace: server currently hosts frontend, checkout pods,
Gaia/Hephaestus and Elasticsearch, so API/services may be temporarily unavailable. The pre-repair Pods,
workloads, three PVC UIDs and server mounts are recorded. Do not recreate cluster/delete volumes or use
force-finalizer cleanup. Recovery/retest needs its own explicit scope/time grant; no guarantee of repair.

ZER-41 remains PARTIAL; no Git publication, merge, acceptance or Linear Done is implied.

Empty per-poll policy diagnostics are consolidated losslessly in raw/empty-policy-observations.json within the applicable attempt (original names, bytes, hashes and observation times); original empty files are also retained locally. Request/response, failure and positive policy records remain unchanged.
