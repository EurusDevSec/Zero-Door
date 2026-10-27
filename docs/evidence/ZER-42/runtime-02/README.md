# ZER-42 runtime-02 — technical closure

**27/10/2026 — TECHNICAL_PASS_READY_FOR_PUBLICATION.** [Final receipt](acceptance-final/README.md) reconciles the
already-collected attempt `zer42-74545a02be28`: 4 commands/results, 12 independent joins, 4 benign source
controls, four verified H exports and live CLEAN restoration. No test traffic was rerun. INVALID_ID was a
post-collection renderer/context defect; original raw/FAILED receipt remain unchanged. Safe/benign formal H
statuses remain UNKNOWN_EFFECT, as required by the reviewed preparation.

Earlier dataplane/interruption verdicts below are historical. The completed attempt and later cleanup
receipt supersede their next-action requests. No Git/Linear publication, remote CI, merge or Done action.
See the final receipt for provenance limits and remaining delivery gates.

## Historical recovery/runtime-02 — interrupted, not acceptance evidence

Date: 26–27/10/2026. Verdict: **RETEST_REQUIRED**.

Hoàng approved one bounded 35-minute recovery/retest with one restart of
`k3d-zero-door-server-0`. That restart restored the API, workloads and all three
PVC identities. The executor images from runtime-01 were reused; no image was
rebuilt.

The recovery attempts exposed and corrected three harness-only defects before a
complete acceptance receipt could be produced:

- the private Traefik policy omitted DNS egress;
- Kafka admin CLIs inherited broker `JMX_PORT=5555`, so their child JVMs tried to
  bind the broker's live JMX port;
- one `iptables-save` snapshot failed while nftables replaced a set. The gate now
  retries that transient read inside the existing deadline.

Attempt `zer42-159121a614e0` reached the safe phase: direct fixture access was
blocked, both private sources passed benign controls, the worker consumer group
was Stable, Nemesis was healthy and two safe commands produced results. It then
failed before the vulnerable phase completed. Later observation found all three
k3d containers `Exited (255)` and the Kubernetes API refused connections. The
Windows runner ended without `process-receipt.json` or `after.json`; therefore
namespace/topic cleanup is **UNKNOWN** and the safe partial result is not promoted
to acceptance evidence. See `zer42-159121a614e0/interruption-observation.json`.

Earlier failed attempts and their raw logs remain unchanged. The two topic names
left by `zer42-c2d30a7145ff` were explicitly deleted and a live broker list showed
neither name before the final attempt. No Linear or publication action was taken.

## Required next action

A new bounded authorization is needed because the approved restart was used and
the 35-minute window expired. Start the existing cluster, first verify/remove only
the owned `zd-sqli-lab` namespace and the two ZER-42 topic names, confirm the three
PVC identities and existing deployment snapshot, then rerun the four-case private
acceptance with the already-built images. A fresh independent reconciliation and
clean restoration receipt are required before ZER-42 or ZER-13 can be accepted.

## Controlled final recovery — 27/10/2026

Hoàng later approved one full stop/start of the existing cluster and another
bounded final acceptance run. The recovery preserved all three PVC UID/volume
pairs and restored both nodes plus existing deployment replica counts. The
fixture gate was also corrected so the Pod can become Running while the
application remains unbound; this removes the init-container/controller
deadlock without weakening the policy requirement.

The final runs still stopped before topics, signed commands or vulnerable
traffic. A new fixture Pod became Ready on each node, but neither node acquired
the required `KUBE-POD-FW-*` hook after 150 seconds or after an extended 420
second window. Both k3s processes reported kube-router network-policy controller
startup, yet the hook remained absent after the full cluster stop/start. Every
attempt failed closed as `POLICY_RULE_MISSING`, deleted its owned namespace by
UID, and reported an empty cleanup-problem list. The interrupted attempt's last
ZER-42 Kafka topic was also explicitly deleted and verified absent.

Current verdict remains **RETEST_REQUIRED**. Source/offline acceptance remains
valid, but AC-04 runtime cannot be promoted. The next action is a separately
approved repair of the k3s/kube-router dataplane (or reconstruction of the lab),
followed by one clean four-case run and independent reconciliation. Do not
disable NetworkPolicy or bypass the gate merely to obtain a passing receipt.
