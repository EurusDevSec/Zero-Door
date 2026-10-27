# SQLi executor runbook (ZER-42)

Status: [runtime-01](../evidence/ZER-42/runtime-01/README.md) attempted under direct approval on 26/10; two
actor images built/imported, private bootstrap namespaces created and cleaned. Both attempts stopped before
fixture release because Pod policy hooks were not verified. No SQLi command or vulnerable request was sent.
Further recovery/runtime still requires appropriate owner authority; this runbook does not grant it.

## 1. What the executor is, and is not

The SQLi executor replays **one locked catalog template** against the ZER-41 fixture's single read-only search
endpoint, through the existing Nemesis → guard → Kafka → Go-worker chain. It is **not** a scanner, a fuzzer, or
an arbitrary-SQL tool:

- The catalog (`chaos-worker/internal/attack/sqli.go`) holds exactly one injection template — the disclosure
  pattern already reviewed in ZER-41 (`tests/fixtures/zer41/expected.json` → `injection.category`) — plus
  benign public-category controls. No destructive/DDL strings exist in the catalog.
- The executor only URL-encodes a catalog entry into the `category` parameter of `/fixture/catalog/search`.
  It never accepts raw SQL, raw payloads, arbitrary method/path/headers/URL, filesystem/shell, host/schema
  scans, or DB writes.
- The executor's result is **raw observation only** (plane F `FAULT_EXECUTOR_RESULT`). Whether an effect
  occurred is decided separately by the H-plane evaluator (`infrastructure/scripts/sqli_executor_runtime.py`),
  which emits `EFFECT_EVALUATED`.

## 2. Admission and the opt-in lock

Both guards (Python `agent-orchestrator/nemesis/command_guard.py`, Go `chaos-worker/internal/guard/policy.go`)
admit a `SQLI` command only when:

- the policy carries an **opt-in `sqli` capability with `enabled: true`** — it is absent/disabled by default,
  so SQLI is refused until a lab explicitly turns it on;
- the target is exactly `zd-sqli-lab` / `sqli-fixture` and the command URL equals the one configured endpoint
  (exact host, `http`, path exactly `/fixture/catalog/search`, no query/fragment/userinfo/uppercase);
- concurrency is 1, intensity `LOW`, duration within the capability ceiling;
- `customParams` holds exactly `{"template": "<known catalog id>"}`.

The four legacy executors (HTTP_FLOOD/CPU_STRESS/MEMORY_STRESS/POD_KILL) are unchanged: they still reject any
`customParams` and still resolve targets only to `target-app`, so none of them can be pointed at the fixture
even when SQLi is enabled.

## 3. Request budget (hard ceilings)

Per command, enforced in code and never silently raised (config may only lower them):

| Limit | Value |
|-------|-------|
| concurrency | 1 (no extra goroutine) |
| rate | ≤ 1 request/second |
| total sends | ≤ 20 (counts every send; no implicit retry, no redirect following) |
| command window | ≤ 30 s (absolute deadline) |
| per-request timeout | ≤ 3 s, clamped by the remaining command deadline |
| response read | ≤ 256 KiB |

Stop/cancel/SIGTERM: the worker context cancels, the executor stops creating sends, closes the body/connection
and returns; no send is issued after cancellation and no goroutine is left running.

## 4. Read-only preflight before any lab run

Do these read-only checks first; if any fails, stop and do not enable the capability.

1. Confirm the fixture route is private and loopback/ingress-only, exactly as in
   [sqli-fixture.md](sqli-fixture.md) §4 (host-binding check: `docker port`, `netstat`, Traefik ServiceName
   for `/fixture` vs `/`). The executor must reach the fixture **through the Traefik ingress**, never straight
   to the `sqli-fixture` ClusterIP — going direct loses the source-IP observation point.
2. Confirm the one network path the executor needs: chaos-worker egress → Traefik ingress → `zd-sqli-lab`
   `/fixture`. The executor adds no Kubernetes RBAC and opens no other connection.
3. Confirm the endpoint in the policy equals the accepted runtime-02 Service exactly:
   `http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search`. Capture that
   Service's current `clusterIP` and pass it to the worker as `ZD_SQLI_INGRESS_IP`. Startup fails closed if the
   value is absent or not a private unicast address. Before the first request, DNS must resolve only to that
   pinned IP; the HTTP transport then dials the numeric IP and verifies the connected peer while retaining the
   approved Host header/route. A Service recreation changes the IP and therefore requires a new preflight and
   worker restart; it is never silently accepted.
4. Confirm the fixture profile for the run (safe for a negative control; the vulnerable profile only under the
   approved run, set on the fixture, never by the executor).

## 5. Enabling for an approved run (not done here)

An approved lab run, and only then:

1. mounts `infrastructure/manifests/sqli-executor-lab.yaml` in place of the default command-guard config and
   flips both `enabled` and `sqli.enabled` to `true`, with a real `run_id`/`trial_id`/`group` context;
2. keeps `sqli.endpoint` at the exact private-ingress DNS name above and sets `ZD_SQLI_INGRESS_IP` to the
   read-back ClusterIP from that same Service (do not use a Pod IP, fixture Service IP, public IP or loopback);
3. keeps `maxSends`/`maxCommandSec` at or below the ceilings in §3;
4. provisions the operator token, command signer and ledger separately (unchanged from the existing guard).

## 6. Runtime AC-04 envelope (proposed, not run)

For the before/after + benign-control + trusted-source-IP evidence (parent ZER-13 AC-04), the proposed turn is
bounded as follows. These numbers are a reviewable proposal, **not permission to execute**:

| Boundary | Proposed maximum |
| --- | --- |
| elapsed time | 35 minutes total, including 10 minutes reserved for cleanup/restore |
| images | build/import one chaos-worker image; reuse the already accepted ZER-41 fixture/Traefik images |
| temporary topology | namespace `zd-sqli-lab`; at most four fixture-profile pods total (fixture, private Traefik, two sources), plus the existing worker/Nemesis/H recorder components required by the signed path |
| executor traffic | at most four signed commands; each remains capped by §3, therefore at most 80 fixture GETs total |
| readiness/health traffic | at most 400 requests total; no public listener/route |
| evidence queries | at most 12 read-only Elasticsearch queries; no model or paid API call |

The run must:

- record namespace UID/ownership labels, baseline replicas/config and the private Service UID/ClusterIP before
  enabling SQLi; abort on a pre-existing unowned namespace or any endpoint/IP mismatch;
- run the disclosure template on the **vulnerable** profile and expect `EFFECT_EVALUATED = CONFIRMED` only when
  the restricted seed rows are actually returned; run the same command on **safe** as a negative candidate,
  but keep the final result `UNKNOWN_EFFECT` unless independent `PROBE_SAMPLE` coverage satisfies the locked
  scorer contract;
- run benign controls separately, drive the two approved sources and one forged-XFF control, and stitch
  correlation/request IDs across worker result, private proxy, fixture, H archive and verified export;
- persist the write-once result bundle before archive ingest, replay only the identical bundle, seal/export H,
  and independently recheck the exported raw hash and effect computation;
- always delete only resources matching the recorded namespace UID/ownership labels, restore exact baseline
  replicas/config, and retain raw/export plus cleanup receipts;
- stop on any deadline, budget, policy, peer-pin, archive/export or restoration failure. Do **not** claim
  containment/IP blocking/R3 or an Online-Boutique vulnerability from this run.

Lab state is currently unverified; the ZER-41 runtime results are history in the accepted profile.

## 7. Concrete runtime preparation after cross-review (not executed)

The [runtime preparation](../evidence/ZER-42/runtime-prep/README.md) records current cluster/image read-back,
the offline renderer and the proposed acceptance/cleanup sequence. It supersedes §6's earlier proposal for
this next turn: **45 minutes including 10 minutes cleanup, two actor image builds/imports, six temporary pods,
two uniquely named Kafka topics**, with the same private target and traffic ceilings. Existing deployments
remain at their read-back replica counts; temporary Nemesis/worker run inside the owned namespace. The policy
defaults remain disabled. Explicit owner approval is still required before runtime operations.
