# SQLi catalog fixture (ZER-41)

A small internal test service for the SQLi vector. It is an **added experimental component** with fully
synthetic e-commerce data, not a flaw of Google Online Boutique, and it never talks to anything outside the
lab. Python standard library + SQLite only — no third-party dependency.

## Why two profiles

The service answers `GET /fixture/catalog/search?category=…` on two configuration profiles over the **same
seed and interface**:

- `safe` (default): the category is a bound parameter. Injection has no effect.
- `vulnerable` (opt-in, `ZD_SQLI_PROFILE=vulnerable`): the category is interpolated into the SQL — the
  deliberate flaw. Set it only in a lab run approved for it.

The *effect* criterion is a query that returns a `visibility=restricted` row that a benign query never
returns. HTTP 200, or a SQL string appearing in a log, is **not** effect. The profile/variant is an H-plane
fact: it never appears on **any** container stream (stdout or stderr — Fluent Bit tails both).

## Request lifecycle, limits and logging

One request per connection (`Connection: close`): request identity and timing are per request, and an unread
or over-long body can never be reparsed as a second request. Deadlines are absolute and are not extended by
progress: the whole request (line, headers, body) must arrive and be decided within 3 s, including any wait
for a DB slot; the connection, including writing the response, ends within 5 s. A request still arriving at
3 s gets 408; an idle connection that sent nothing is closed without a record. Other bounds: ≤ 64 concurrent
connections, ≤ 16 concurrent catalog queries and ≤ 8 concurrent order writes (a busy service returns 503
BUSY fast; a request whose budget was already spent gets 503 DEADLINE_EXCEEDED), body ≤ 4096 B, response
≤ 256 KiB, ≤ 200 rows, category ≤ 120 chars, ≤ 500 ms/query, and a SQLite value-length cap.

Every outcome of a parsed request goes through one boundary: exactly one structured JSON response with
`X-Request-Id` and exactly one access record. That includes every unsupported method (listed or not → 405),
malformed request lines (400), unsupported HTTP versions (505), too many headers (431), invalid SQL (4xx),
an unavailable/locked DB (503), an unsupported result type (422) and a client disconnect (recorded as 499,
never a success). The access log is JSON on stdout with a server-assigned request id; it carries no profile,
cookies, auth or full headers, and the client correlation id is validated. A failed startup prints one
neutral line on stderr — `{"event":"startup_failed","reason":…,"setting":…}` — and exits nonzero, never a
traceback, path, seed id or attempted value; a request-thread crash is reported as its error type only.

## Source IP (topology)

`ZD_SQLI_TOPOLOGY` says how the service is reached. `direct`: the observed TCP peer is the client.
`proxied` (default): the peer is an ingress hop, so the client is read from X-Forwarded-For **only** through
a configured trusted proxy; an untrusted peer or absent/malformed forwarded data leaves the client UNKNOWN.
The observed peer is always recorded separately from the attributed client, and a client-declared header is
never trusted.

Even on the vulnerable profile the query runs on a **read-only** SQLite connection as a **single statement**
with a row cap, a length cap and a wall-clock budget, so an injection can only *read* synthetic rows.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | process liveness only (does not prove the DB works) |
| GET | `/ready` | readiness: runs a trivial SELECT against the DB |
| GET | `/fixture/catalog/search?category=…` | catalog search (returns only rows the query grants) |
| POST | `/fixture/orders` | create one owned order, read back on an independent connection |
| GET | `/fixture/orders/{ref}` | read one order |
| DELETE | `/fixture/orders/{ref}` | delete one order by ref (parameterised) |

The CRUD endpoints are compatible with `measurement.flows.fixture_spec` (ownership by nonce echo).

## Configuration (environment)

| Variable | Default | Meaning |
| --- | --- | --- |
| `ZD_SQLI_PROFILE` | `safe` | `safe` or `vulnerable`; any other value refuses to start |
| `ZD_SQLI_DB_DIR` | — (required) | the only directory the service writes (the SQLite file) |
| `ZD_SQLI_SEED` | `./seed.json` | synthetic catalog seed |
| `ZD_SQLI_HOST` / `ZD_SQLI_PORT` | `127.0.0.1` / `9140` | listen address |
| `ZD_SQLI_TOPOLOGY` | `proxied` | `direct` (peer is the client) or `proxied` (peer is an ingress hop) |
| `ZD_SQLI_TRUSTED_PROXIES` | empty | CIDRs of proxies whose forwarded client address may be believed; empty = trust none |

An invalid profile or topology, a missing/unwritable DB dir, a bad proxy CIDR, an out-of-range port or a
missing seed all refuse startup. On startup an existing compatible DB (matching seed id) is reused so order
state survives a restart; a foreign or incompatible DB refuses startup instead of being erased.

## ZER-46 containment candidate (offline, opt-in)

The default behavior above is unchanged. Supplying **both** `ZD_SQLI_CONTAINMENT_FILE` (absolute path to a
read-only projected ConfigMap file) and `ZD_SQLI_CONTAINMENT_SCOPE` opts into source containment. A partial
configuration refuses startup. There is no management HTTP endpoint or new payload. All supported
`/fixture` operations check the existing trusted-source resolver **before** running queries or writes.
An active rule for that attributed client returns403 `SOURCE_BLOCKED`, while another client behind the
same proxy remains allowed. UNKNOWN/unusable source or missing/corrupt/wrong-scope policy returns503;
these are not evidence of successful containment. `/health` remains liveness; `/ready` also validates
the policy when opted in. Logs carry the policy SHA256, enforcement point and matching action IDs.

State lives in a dedicated ConfigMap outside the fixture/healer Pods, not the fixture's ephemeral SQLite
volume. Mount the whole ConfigMap directory, never `subPath`, so projected replacements can be observed.
The file is opened afresh per request, capped32KiB/32rules. Each rule expires at an absolute UTC epoch
deadline, at most300s from its joined source observation; the request check ignores it at that exact
deadline even if the healer is stopped. Expiry unblocks traffic but does not erase the stored rule.
Explicit owned runner cleanup removes rules by compare-and-swap; resetting order data does not.

The prepared writer is `agent-orchestrator/hephaestus/sqli_containment.py`: namespace/name/UID/scope and
run/trial pins, distinct approved attacker/benign addresses, exact proxy `/32`, bounded TTL/CAS retries.
It never initializes a client, creates/deletes resources, or enables production R1 execution. Its input
must be a source record independently joined to the trusted observation and authenticated decision;
model/HTTP-supplied source labels alone are insufficient. A replace response is only `API_ACCEPTED`.
The existing production ModeGate/executor-disabled boundary is retained; this is a prepared component,
not a completed Gaia→healer integration. Future integration must retain the durable decision ledger.

The candidate RBAC/ConfigMap is `infrastructure/manifests/sqli-containment-lab.yaml`, **NOT_APPLIED**.
Projection delay, real source/benign separation, Pod/healer restart, independent probes and observed
cleanup still require an approved bounded private-lab run. Unit/loopback tests cannot prove them.

```bash
python3 -B tests/test_sqli_containment.py
```

## Run locally (offline)

```bash
ZD_SQLI_DB_DIR=$(mktemp -d) python3 services/sqli-fixture/app.py
```

Tests: `python3 -B tests/test_sqli_fixture.py` (loopback HTTP against a real SQLite DB in a temp dir).

Container image and Kubernetes manifest are prepared but **not built or applied** in this package; see
`docs/runbooks/sqli-fixture.md`.
