# ZER-42 runtime-01 — blocked before fixture release

**BLOCKED_RUNTIME_PREFLIGHT — 26/10/2026, UTC / Asia-Saigon UTC+07.** Two bounded attempts were retained.
Neither released the fixture's policy gate, enabled vulnerable, created a Kafka topic, or sent a SQLi command.
Both cleaned their exact owned namespace and verified that existing deployment UIDs/replicas/generations and
all three PVC UIDs/volume names matched baseline. The code's successful offline cross-review is unchanged;
the actual acceptance path is not yet proven.

## Authority and successful work

Hoang directly approved the [concrete lab packet](../runtime-prep/README.md): 45 minutes including ten for
cleanup, two actor image builds/imports, up to six private pods, two run-specific topics and bounded traffic.
It explicitly excluded restarting nodes or changing existing deployments/PVCs.

The current reviewed actor images were built once and imported successfully:

| Image | Local image ID |
| --- | --- |
| `zer42-worker:e80bc554b7ef` | `sha256:250be486034d652fc74e0e15d6c7c61bc4f54e826ffcbb54b8803153c9e5cace` |
| `zer42-nemesis:e80bc554b7ef` | `sha256:d1896d5e4e9f1ea2b97e33fab518f3718b40525ff87ae12b5b511ae0ba07f199` |

Source hashes, build/import outputs, baseline, rendered disabled manifest and namespace UID ownership are in
the first attempt. The second verified and reused those exact image IDs without another build/import. It
retained the first attempt's authorization start and deadline instead of resetting the 45-minute allowance.

## Preserved attempts

| Attempt | Actual observation | Outcome |
| --- | --- | --- |
| [zer42-d042c1ab05f1](zer42-d042c1ab05f1/process-receipt.json) | Four temporary bootstrap pods existed; fixture stayed Pending in its init gate. The full `iptables-save` read eventually exceeded 15 seconds before an exact fixture Pod hook was observed. | FAILED; cleanup problems `[]`; 250.0 seconds; no topics or application requests |
| [zer42-ee5131c87eca](zer42-ee5131c87eca/process-receipt.json) | Retest read only the filter table, tolerated slow reads, and waited 150 seconds. Policy-definition chains existed, but no `POD name:… namespace: zd-sqli-lab` hook for any new owned Pod appeared. Running source/proxy Pods were present, while fixture remained gated. | FAILED `POLICY_RULE_MISSING`; cleanup problems `[]`; 229.8 seconds; cumulative authorization time at cleanup 632.0 seconds |

The second attempt's [raw filter-table observations](zer42-ee5131c87eca/raw/140-policy.json) show existing
Pod hooks for older workloads and new policy definitions, but do not establish enforcement for the new
namespace. [Pending Pod observation](zer42-ee5131c87eca/raw/023-gate-pods.json) and the other gate observations
retain the new fixture UID/IP/state. The absence check was on actual stdout values, not a script PASS label.

Read-only follow-up confirmed the server container hostname and server Node PodCIDR `10.42.1.0/24` agree;
the observed new Pods were scheduled there. The server process PATH uses `/bin/aux/iptables-save`, linked to
`xtables-nft-multi`, version `1.8.9 (nf_tables)`. No alternate bundled path was found at the inspected default
location. This narrows a possible tooling mismatch; it does not establish the controller's root cause.

## Cleanup and remaining acceptance

- Both namespace deletions used captured UID preconditions plus the exact run label and verified absence.
- Neither attempt reached key creation, topic creation, command dispatch, vulnerable profile or H archive.
- Both `baseline.json`/`after.json` pairs match exactly. Existing actor replicas remain zero and three PVCs
  retain their UIDs/volumes. No node was restarted, no firewall was edited, and no existing workload changed.
- No model/API, commit/push/PR/merge or Linear update was performed. ZER-42 AC-01 and ZER-13 AC-03/04 remain
  pending runtime proof. There is no PASS receipt, no effect claim and no research KPI result from this turn.

## Concrete recovery proposal — requires new owner approval

A single controlled restart of **only `k3d-zero-door-server-0`**, followed by the same private acceptance
retest, is proposed because the namespace-scoped actions above did not produce verifiable Pod hooks. The
accepted ZER-41 history contains a successful recovery/retest after such a restart, but does not guarantee
this one will repair the current condition or identify its cause.

Proposed new window: **35 minutes including ten minutes cleanup**, beginning before restart. Reuse the two
image IDs above; no additional build. Capture node/workload/replica/PVC baseline, restart the server container
once, wait for API/nodes/workloads and verify the three PVC UIDs, then attempt the same maximum six-pod/two-topic
private lab with at most four signed commands, 80 executor GETs, 400 health/control requests and 12 read-only
ES queries. Always clean only owned resources and verify existing replica/config/PVC restoration. If hooks or
direct-denial proof remain unavailable, stop before vulnerable. Do not recreate the cluster, delete volumes,
manually change firewall, alter WSL limits or call a paid model/API.

Restart may temporarily interrupt Kubernetes API, checkout/frontend and observability even though their
deployment specifications remain unchanged. This action is outside the just-consumed namespace-only scope;
it has not been executed. Publication and Linear acceptance remain separate.
