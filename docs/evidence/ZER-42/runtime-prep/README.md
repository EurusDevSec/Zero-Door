# ZER-42 runtime acceptance preparation — 26/10/2026

Prepared after Claude's [cross-review](../claude-crossreview-fix02.md), which found no remaining P1/P2 offline.
**Historical preparation below; subsequently approved and attempted.** [Runtime-01](../runtime-01/README.md)
retains two failures before the fixture policy gate was released, both with verified cleanup. These files
do not grant another lab turn, publication, merge, acceptance or a Linear change.

## Current read-back

- HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, branch `zer-41-sqli-fixture`, staged empty.
- Live ZER-42 and ZER-13 are In Progress in `linear.app/zero-door/`, project
  `f6343559-080f-465f-aa7a-eda6074de51f`. ZER-42 AC-01 maps to parent AC-03; parent AC-04 additionally requires
  real effect contrast, benign traffic, request joins and trustworthy source IP.
- Both K3d nodes are Ready; Kafka, logging and the nine Boutique deployments are running. `zd-sqli-lab` is
  absent. Existing worker, Nemesis, Gaia, Hephaestus and Grafana deployments are at zero replicas.
- The accepted fixture image `zer41-fixture:37c7a045e098` is present locally. Existing Nemesis/worker images
  predate the reviewed SQLi source, so acceptance must build two source-specific images instead of silently
  testing old images. No deployment has been changed by this preflight.

## Concrete proposed execution scope

This supersedes the earlier *proposal* of 35 minutes and one image in runbook §6 for the forthcoming turn.
It preserves that proposal's target, traffic and evidence boundaries while making actor packaging explicit.

| Item | Bound |
| --- | --- |
| cluster | explicit context `k3d-zero-door`; server node only for all temporary pods |
| time | 45 minutes from before the first build/import, including 10 minutes reserved for cleanup |
| builds | two sequential builds/imports: current chaos-worker and current Nemesis from their pinned Dockerfiles; reuse accepted fixture and observed private Traefik digest |
| temporary pods | maximum six: fixture, private Traefik, worker, Nemesis, source A and source B; fixture uses Recreate plus the policy init gate |
| new resources | only `zd-sqli-lab` after an absence check and unique run label; the offline renderer emits 21 resources there; add two ephemeral key Secrets there after authorization |
| namespace defaults | fixture safe, both SQLi policy switches disabled; explicit Service ClusterIP pin and exact observed proxy Pod IP must be supplied before enablement |
| broker | exactly two run-specific topics `<run>.commands` and `<run>.results`, one partition/replica; dedicated consumer groups; preserve all existing topics/config/PVCs |
| traffic | maximum four unique signed commands, each limited to three sends/five seconds in this profile; hard ceiling 80 executor fixture GETs for the whole turn including replay; at most 400 health/control requests and 12 read-only ES queries |
| isolation | private ClusterIP only; no Ingress/NodePort/hostPort; no Internet/paid model credentials in actors; actor egress only DNS, approved proxy, dedicated Kafka path and client-to-Nemesis path as applicable |
| storage | fresh namespace-scoped emptyDirs only, ledger 16Mi per actor and fixture data 64Mi; preserve existing PVCs/volumes |
| existing workloads | no scale/image/config change to existing deployments, no node restart or cluster/resource-profile change |

The six-pod manifest requests approximately 160m CPU/224Mi memory and caps main containers at 800m CPU/608Mi.
These are workload bounds, not a guarantee of available host RAM. Builds are sequential. Check host/VM/node
pressure first and abort before build/apply if the lab cannot stay within the existing WSL 6GB profile.

## Execution and evidence sequence

1. Start the overall deadline before build/import. Save Git/source/image hashes, node/workload/replica state,
   the three existing PVC UIDs and topic absence. Abort on an existing unowned namespace or topic. Generate
   two random ephemeral keys without displaying them or putting them in committed evidence.
2. Build/import the exact current actor images. Create only the owned namespace, default-deny policies and
   private bootstrap resources. Read back Service UID/ClusterIP, image IDs and Pod IPs. Populate the worker IP
   pin and fixture trusted-proxy address from those read-backs, rather than from historical addresses.
3. Hold each new fixture Pod at its init gate until the exact Pod's server-side policy rule is observed, as in
   accepted ZER-41 runtime-02. Start safe first. Confirm source A/B reach the proxy while direct fixture TCP is
   denied with explicit source egress to that fixture. A failed/missing policy check stops before vulnerable.
4. Use current Nemesis HTTP admission, signing, dedicated Kafka topics and current worker. Submit safe disclosure
   and safe benign controls, then vulnerable disclosure and vulnerable benign controls. Reject out-of-scope
   HTTP requests without publishing extra commands. Replay a completed ID and verify no new HTTP effect.
5. Read raw result-topic records and collect proxy/fixture logs for both profiles before rollout/cleanup. Join
   command/correlation/request IDs; verify returned restricted SKUs against the fixed synthetic oracle, safe and
   benign results against their expected rows, and distinguish the observed worker/source IPs. Preserve forged
   XFF as a control and require it not to replace the observed source identity. A transport SUCCESS alone fails
   acceptance if the raw response/log joins do not prove the expected result.
6. Save each bounded executor result and context through the reviewed write-once H bundle, Archive and export.
   Recompute from the exported raw/hash. Keep safe executor-only observations UNKNOWN in the formal effect
   event until independent PROBE_SAMPLE coverage is available; actual safe/benign response contrast is retained
   as technical AC evidence, not a formal research NO_EFFECT/KPI claim.
7. In `finally`/EXIT/INT/TERM handling: collect owned diagnostics within deadline, delete only the two exact
   owned topic names, delete the namespace with its captured UID precondition and run-label check, stop only
   recorded child port-forwards, and verify absence. Compare existing replicas/config/PVC UIDs with baseline.
   Any unresolved cleanup or verification marks the receipt FAILED/UNKNOWN and is reported explicitly.

## Offline preparation performed

- [render.py](render.py) produces the reviewed topology from the existing fixture manifest, removes the shared
  Ingress, supplies exact private Service identity, default-deny and scoped rules, and adds temporary actors.
  No network/process/build/apply is performed by this renderer. It writes only to a new explicit local path.
- Existing pinned OpenAPI validator accepted **21 resources / six pods**. Structural checks confirm safe and
  disabled defaults, ClusterIP-only Services and no Role/RoleBinding/ClusterRole/PVC/Secret manifests.
- Proposed names/images were rendered to `scratch/zer42/runtime-prep/rendered-review.yaml` for inspection.
  Source-specific tags in that example are placeholders for reviewed source hashes, not built image evidence.
- `git diff --check` passed; staged remained empty. Existing source tests were already cross-reviewed and
  were not rerun merely for this preparation-only delta.

## Pending authority

Hoang must approve this concrete scope before the first build/import, topic creation, namespace creation or
application request. After the bounded runtime succeeds, publication/merge and owner acceptance/Linear remain
separate scopes unless directly authorized. The previous ZER-41 lab permission has already been consumed.
