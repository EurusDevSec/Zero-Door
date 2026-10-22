# Runbook — SQLi catalog fixture (ZER-41)

Scope: how to run the fixture **offline** and the **proposed** runtime/cleanup plan to request once, after
review. This runbook is not an execution grant: building the image, applying the manifest and creating the
route each need a separately approved lab turn. Source: `services/sqli-fixture/`,
`infrastructure/manifests/sqli-fixture.yaml`. Current checkpoint22/10: image built once in [runtime-01](../evidence/ZER-41/runtime-01/README.md); stock manifest NOT_APPLIED, private overlays cleaned. Initial isolation failure retained; [runtime-02](../evidence/ZER-41/runtime-02/README.md) subsequently passed the approved private profile after recovery. Pending CI/merge/acceptance.

## 1. Offline, no container

```bash
# Safe profile (default): injection has no effect.
ZD_SQLI_DB_DIR=$(mktemp -d) python3 services/sqli-fixture/app.py
# Vulnerable profile (local testing only):
ZD_SQLI_DB_DIR=$(mktemp -d) ZD_SQLI_PROFILE=vulnerable python3 services/sqli-fixture/app.py
```

Then, from another shell:

```bash
curl -s 'http://127.0.0.1:9140/fixture/catalog/search?category=apparel'          # public rows only
curl -s "http://127.0.0.1:9140/fixture/catalog/search?category=zzz'%20OR%20visibility='restricted'%20--"
```

On `safe` the injected query returns nothing; on `vulnerable` it returns the `restricted` rows — the effect.

## 2. Offline checks (what this package verifies)

```bash
python3 -B tests/test_sqli_fixture.py            # loopback HTTP -> real SQLite; 42 tests
python3 -B tests/test_sqli_fixture_http.py       # socket-level lifecycle; 15 tests
python3 -B docs/evidence/ZER-41/check_manifest.py # pinned OpenAPI models + manifest semantics
```

The suite locks expected values in `tests/fixtures/zer41/expected.json` (computed from the seed before the
assertions were written); it never takes stdout "SUCCESS" as the oracle.

## 3. Preflight before any lab turn (to request, not run here)

1. Build the image from `services/sqli-fixture/Dockerfile` (pinned distroless base, non-root). Record the
   digest. Until then the manifest's `image: sqli-fixture:latest` has no built artefact.
2. Confirm the k3d/Traefik lab is the approved one (`kubectl --context k3d-zero-door`) and that
   `ingressClassName: traefik` resolves.
3. Verify the Traefik controller's actual pod labels before deploying the NetworkPolicy, since the allow
   rule selects `app.kubernetes.io/name=traefik` in `kube-system`:
   `kubectl --context k3d-zero-door -n kube-system get pods -l app.kubernetes.io/name=traefik`.
   If the chart labels differ, update the manifest peer; do not widen it to the whole namespace.
4. Decide `ZD_SQLI_TOPOLOGY` and `ZD_SQLI_TRUSTED_PROXIES`. Behind Traefik, set `ZD_SQLI_TOPOLOGY=proxied`
   (the ConfigMap default). With `forwardedHeaders.trustedIPs: []` the fixture sees the svclb/Traefik peer
   and records the client IP as **UNKNOWN**; it never treats the peer as the end client. Set a narrow,
   anti-spoof-checked `ZD_SQLI_TRUSTED_PROXIES` only once a real chain is proven — never a broad range to
   make an IP appear. `ZD_SQLI_TOPOLOGY=direct` is only for a deliberately direct (no-proxy) exposure.

## 4. Proposed runtime envelope (needs a separate approval; nothing run here)

A concrete envelope to approve as one unit. Preparation only; do not run it.

- **Context:** `k3d-zero-door` explicitly. Namespace `zd-sqli-lab`.
- **Namespace ownership:** create-if-absent and stamp an owner label `zero-door.io/run=<run-uid>`. If the
  namespace already exists **without** this run's owner label, **abort** — do not adopt or delete a namespace
  this run does not own.
- **Network exposure:** ClusterIP only, default-deny, plus the single allow rule (Traefik controller pod in
  kube-system → 9140, and DNS egress). Allowed origin is the Traefik `/fixture` route **only**. Note:
  ClusterIP does **not** prove loopback-only host access — `/fixture` is reachable from the host through the
  existing Traefik LoadBalancer and the k3d `8080:80` mapping. A successful loopback request does not show
  who else can reach it, so record the actual host binding (read-only) **before** enabling the vulnerable
  profile:
  1. `docker port k3d-zero-door-serverlb` — the host address bound for container port 80 (`127.0.0.1:8080`
     vs `0.0.0.0:8080` / `[::]:8080`).
  2. On the Windows host, `netstat -ano | grep ':8080 '` — every listening address for 8080 and its owning
     process id.
  3. The Traefik access log for one `/fixture` and one `/` request — `ServiceName` must be the fixture
     Service for `/fixture` and still the Boutique frontend for `/`.
  If any listener is not loopback-only, the vulnerable route would be reachable beyond this host: **stop**
  before switching profiles. Changing the k3d binding or a host firewall is Hoang's decision, outside this
  package. This package does not claim the current binding either way.
- **Resource / storage budget:** 1 replica, requests 25m/32Mi, limits 150m/96Mi, read-only root, `/data`
  emptyDir with `sizeLimit: 64Mi`.
- **Time budget (30 min total, cleanup reserve inside it):**

  | Phase | Cap |
  | --- | --- |
  | P0 preflight: context, Traefik labels, host binding, namespace absence | 3 min |
  | P1 build and import the image | 7 min |
  | P2 apply, rollout Ready on `safe` | 3 min |
  | P3 `safe` probe window | 4 min |
  | P4 switch to `vulnerable`, rollout Ready | 2 min |
  | P5 `vulnerable` probe window | 4 min |
  | Cleanup reserve (never spent by earlier phases; cleanup starts by minute 23 at the latest) | 7 min |

  A phase that hits its cap ends the run and goes straight to cleanup; nothing is extended.
- **Request/work budget:** **one total cap of 4000 HTTP attempts for the whole run**, counting every attempt
  of every kind — both profiles, both sources, search, order create/read/delete, `/health`, `/ready` and
  every retry. Within it, ≤ 1000 attempts per source per profile (2 sources × 2 profiles); cadence ≤ 20
  attempts/s per source. Retries: at most 3 retries per logical operation, i.e. **at most 4 attempts**, each
  counted in the totals; no retry after a 4xx and no retry-until-green. Reaching any cap ends the probe
  window. Per-request caps enforced by the service: body ≤ 4096 B, response ≤ 256 KiB, ≤ 200 rows, category
  ≤ 120 chars, ≤ 500 ms/query, ≤ 16 concurrent queries, ≤ 8 concurrent writes, ≤ 64 connections, a 3 s
  absolute request budget (receive the whole request and decide; steady byte-by-byte progress does not
  extend it) and a 5 s absolute transport deadline per connection, including writing the response.
- **Two distinct lab sources:** drive the probe from two separate in-cluster sources (not a host
  port-forward, which k3d serverlb NAT collapses) to show source attribution and, later, source-based
  containment. The offline package proves none of this.
- **Profile control:** start `safe`; switch to `vulnerable` only within this approved turn, recording the
  change; never leave `vulnerable` running past the turn.
- **Source receipts / raw to keep:** the service stdout access log (request id, method/path, status,
  duration, tcp_peer, source method/confidence, client IP, row/restricted counts), the Traefik access log
  (`ClientHost`, `ClientAddr`), and the probe samples.
- **Rollback / cleanup / ownership:** teardown deletes **only** resources carrying this run's owner label,
  then the namespace if it is owned. The order probe deletes only records proven owned (nonce echo). Cleanup
  that fails or cannot be verified is **UNKNOWN / UNRESOLVED**, never CLEAN.
- **Stop conditions:** a restricted row returned on the **safe** profile; any write observed outside `/data`;
  the fixture reachable at any origin other than the approved Traefik `/fixture` route; a resource/time/work
  budget exceeded; cleanup unverified; a pre-existing unowned `zd-sqli-lab`.

## 5. What this fixture does not do

No executor (ZER-42), no arbitrary-SQL endpoint, no scan or exploit of any external target, no destructive
SQL, no containment/EFFECT_CONFIRMED claim. SQLi containment and the business availability of the fixture
and of Boutique are reported as separate probe flows, never merged.


## 6. Private-ingress runtime proposal after host-binding preflight — 22/10/2026

**Approved and attempted22/10; BLOCKED_RUNTIME_ISOLATION.** See [runtime receipt](../evidence/ZER-41/runtime-01/README.md). No vulnerable profile was started; all owned resources cleaned. The original proposal below records the granted envelope, not a new grant. Read-only preflight found the shared serverlb mapping and host listeners on
`0.0.0.0:8080` and IPv6 wildcard. Therefore §4's shared-route vulnerable phase is blocked. Do not
change host bindings/firewall or expose this fixture through that controller as a workaround.

Prepared alternative for Hoang's approval: an isolated Traefik **inside** `zd-sqli-lab`, same immutable
image observed on the current controller, with a file-provider route `/fixture` → fixture Service. Both
Services are ClusterIP, no Kubernetes Ingress/NodePort/LoadBalancer/hostPort/hostNetwork is created. The
existing shared controller and Boutique stay untouched. This proves the fixture behind a private Traefik
proxy; it does **not** establish runtime proof for the shared-controller Ingress in the stock manifest.
The variant and that limitation must appear in the acceptance receipt.

Reviewable preparation: `scratch/zer13/codex-completion/runtime-private.yaml` (14 resources, pinned OpenAPI
validation passed), renderer `render_private.py`, finite client `runtime_probe.py`. These are local
preparation, not published artifacts or a grant to apply them. Rendered fixture profile starts safe;
proxy trust remains empty until the observed proxy Pod IP is recorded, then only that exact /32 is set.

- Scope: explicit context `k3d-zero-door`; create namespace only if absent; record namespace UID and run
  label before children. Refuse an existing namespace. All resources and Pod templates carry the run label.
  Two Deployments (one fixture, one private proxy), two source Pods; no cluster-scoped resources or tokens.
  All four Pods pinned to `k3d-zero-door-server-0`; this does not prove policy enforcement—test it.
- Budget: keep §4's **30 minutes total / 7 minutes reserved cleanup / 4000 total fixture HTTP attempts**,
  including kubelet health/readiness probes and retries. P0 3m, build/import 7m, safe rollout 3m, safe cases
  4m, vulnerable rollout 2m, vulnerable cases 4m. At any cap stop cases and clean up; cleanup starts no later
  than minute 23. A build/rollout over cap aborts rather than borrowing cleanup time.
- Limits: fixture 150m/96Mi, proxy 150m/96Mi, each source 50m/48Mi: total 400m/288Mi CPU/memory limits;
  fixture /data emptyDir 64Mi, no host writes/mounts. One source window at a time, max32 attempts, <=5/s,
  max90s including20s cleanup grace; max4 windows total128 manual attempts, no automatic retries.
  Keep a global ledger including health probes; stop probe windows well before4000. A missing count is
  UNKNOWN, never evidence of staying under the cap. Observe max12 Elasticsearch read queries separately.
- Cases per profile/source: known benign categories vs fixed seed, fixed synthetic restricted-row contrast,
  independent CRUD readback and nonce-verified deletion, request IDs, forged XFF address
  `203.0.113.77`. Collect each source Pod IP, private proxy peer IP, proxy access logs, fixture stdout,
  and H-only client receipts. Match correlation/request ID; require distinct observed end-client IPs and
  reject the forged IP. If NAT collapses identity or a chain cannot be established, record UNKNOWN and stop
  before claiming trusted IP. Do not widen trust ranges.
- Isolation: both sources must reach via the proxy and fail direct fixture access. Source egress explicitly
  permits the direct test, so its denial is not merely caused by the source's egress policy. Stop before
  vulnerable if the fixture is directly reachable or the isolation/route checks fail. No shared /fixture
  Ingress is applied in either profile.
- Logging: existing Fluent Bit configuration tails all container logs; it has not yet proved ingestion of
  this namespace. Confirm the exact fixture request sentinel in Elasticsearch (read-only query/temporary
  loopback port-forward if needed); do not modify monitoring policies/collector configuration to force it.
- Cleanup: collect raw before deletion, remove only the namespace after fresh UID+owner-label match; this
  also removes this run's private proxy/sources/fixture. Do not delete/adopt unrelated objects. Verify
  namespace absence, record image ID retained locally, and mark failures UNRESOLVED. No vulnerable
  workload is intentionally left running. No target-app/agent/HPA/quota/replica changes, LLM/API calls,
  executor ZER-42, paid cloud, Git publication or Linear writes are included.

F-05 proposed oracle remains actual restricted **synthetic seed rows** returned only in the vulnerable
contrast, never HTTP200 alone. Hoang's approval must cover this definition and the private runtime variant
before execution. Parent ZER-13 AC03/04 and ZER-42 remain separate work.


## 7. Verified private profile after recovery — 22/10/2026

[Runtime-02](../evidence/ZER-41/runtime-02/README.md) records48requests/two sources, safe0restricted vs vulnerable3, CRUD/IDs/IP-spoof rejection, two ESsentinels and verified cleanup/restore. Private variant uses Service8000→Traefik8000→fixtureService9140→Pod9140. Main app waits in a non-root init gate using existing/data until the exact Pod policy rule is observed; only then release and test direct denial. TCPreadiness on proxy is separate from policy readiness. Stock shared Ingress was never applied. Earlier failures and CRLFrestore correction remain in receipts. No future execution grant is implied; never restart a node or reuse this lab scope without actual authorization.
