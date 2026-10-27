# ZER-42 SQLi executor — design decision note (pre-code)

Status: DESIGN — no executor code written yet; offline only; no lab/build/model/commit/Linear.
Baseline: HEAD `7db9d9f` on `zer-41-sqli-fixture`; origin/main `ab1003b`; ZER-41 Done (PR #29 merged).
Intake + source snapshot + hashes: `scratch/zer42/claude/intake-baseline.txt`, `scratch/zer42/claude/before/`.

This note records the decisions required by the package (sqli-fixture.md §273 step 1) before any edit.
The sole writer is Claude since Hoàng handed the prompt; Codex reviews after handoff.

## 1. Replay mechanism: minimal stdlib HTTP replay, no external tool

Decision: implement the SQLi command as a **minimal, deterministic HTTP replay** of a locked template
set, built on the Go standard library (`net/http`) for the executor and Python stdlib on the Nemesis
admission side. Do **not** adapt or install sqlmap / Burp / any scanner, and do **not** add a new
dependency.

Why:
- The acceptance target (ZER-42 AC-01 = ZER-13 AC-03) is "a valid template runs; out-of-scope is
  refused" against the **fake, self-owned** ZER-41 fixture. That is a *locked template set*, not a
  general prober/scanner. A fuzzer/scanner would be more capability than the AC needs and would
  directly conflict with the package's prohibition on arbitrary SQL, arbitrary URLs, host/schema
  scanning, and exploitation-technique expansion (§277).
- stdlib replay is the least code and carries no supply-chain or capability surface a scanner would.
- Limit of the conclusion this buys: a passing replay proves *this fixture, this template, this route*
  behaves as the oracle expects. It is not evidence about any real service, nor a general SQLi finding.
  The runbook and verification.md state this explicitly.

If any adapter genuinely needed a dependency or architecture beyond this package, that is a handoff
decision point to record — not something to self-approve — and the offline parts proceed regardless.

## 2. Integration: through the existing guard, never around it

The real path to prepare (not run live) is:
operator request → Nemesis admission (`command_guard.py`) → claim/sign → `attack.commands` →
Go `Dispatcher` authenticate/admit/ledger → SQLi executor → durable result → `attack.results`.

Decisions:
- Plug the SQLi executor into the existing `executors map[string]attack.Executor` registry in
  `cmd/main.go` and the existing `guard.Dispatcher`. Offline tests drive the **entrypoint** with a fake
  broker / loopback fixture; they must not call the executor directly and call that "integrated".
- Keep `auth.go`, `ledger.go`, `dispatch.go` read-only unless an integration genuinely cannot use the
  current contract; if so, record the decision point rather than patching around the guard.
- Preserve replay/dedup after restart, expired redelivery, UNKNOWN-after-lost-ack, fail-closed, and the
  ZER-12 mode semantics already enforced by the ledger. A SQLi command is one more admitted command
  type under the same ledger discipline; it adds no new re-execution path.

## 3. Admission is additive and type-scoped — current refusals stay refusals

Today both guards accept only `HTTP_FLOOD | CPU_STRESS | MEMORY_STRESS | POD_KILL`, always reject
`customParams`, and resolve targets only to `target-app` (frontend `/`). The SQLi path must not weaken
any of that:
- Add `SQLI` as an accepted `attackType` **only** on a new, separate admission branch.
- The general target validator (`validation/target.go`, `url_valid` in Python) stays locked to
  `target-app`/frontend and keeps rejecting query strings and arbitrary URLs. SQLi gets its **own**
  narrow validation to one private-ingress host + the single path `/fixture/catalog/search`. The
  fixture namespace is never added to the shared target list, so legacy executors can never reach the
  fixture even when SQLi is enabled.
- `customParams` for a SQLi command carries only a typed, closed key set (template id enum + the
  required IDs); **legacy command types continue to reject `customParams` entirely** (the existing
  `CUSTOM_PARAMETER` / empty-`customParams` checks are unchanged for them).
- Python and Go must accept/reject the **same** inputs (parity tests), so a divergence cannot admit
  something on one side the other would refuse.

## 4. The locked catalog (reused verbatim from ZER-41, no new technique)

One template, taken verbatim from `tests/fixtures/zer41/expected.json`:
- `category = "zzz' OR visibility='restricted' --"`
- Oracle: vulnerable profile returns exactly `["RES-APP-900","RES-INT-001","RES-INT-002"]`; safe profile
  returns `[]`.
- Benign controls (same route, no injection) from `expected.json.benign`, e.g. `category=apparel` →
  `["PUB-APP-001","PUB-APP-002"]`.

The catalog is a versioned, internal, read-only enum. The executor builds the request **only** by
URL-encoding a catalog entry into the `category` query param of `/fixture/catalog/search`. It never
accepts raw SQL, raw payloads, arbitrary method/path/headers/URL, filesystem/shell, host/schema scans,
or DB writes/deletes. The destructive and UNION-non-text strings that ZER-41 already proved are refused
by the fixture are kept **as negative-control catalog cases**, asserting the fixture's clean 4xx — not
as new attack capability.

## 5. Design budget ceiling (offline; not an authorization to emit lab traffic)

Per §279, as a hard design ceiling baked into the proposed code/plan:
- one active command, concurrency 1, ≤ 1 request/second, ≤ 20 total sends, ≤ 30 s/command;
- request timeout ≤ 3 s and clamped by the remaining command deadline; response ≤ 256 KiB.
- Effective ceiling = min(trusted config, command, context); out-of-range SQLi values are rejected, never
  silently raised; every send/retry/redirect counts (prefer no implicit retry; no redirect following).
- stop/cancel/SIGTERM: stop creating new requests, close body/connection, wait for a bounded goroutine;
  a slow read must not extend the timeout or run cap (reuse the DeadlineReader discipline the fixture
  already demonstrates on the server side).

## 6. Result ≠ effect; H stays separate

- The executor emits a `FAULT_EXECUTOR_RESULT` (plane F): neutral request/correlation/command/run/trial
  IDs and bounded raw observation (requests sent, HTTP status, rows / restricted_rows as returned by the
  fixture, timing). Errors/timeouts/lost data do **not** become "no effect".
- A separate H-plane `effect_evaluator` emits `EFFECT_EVALUATED` per the contract
  (`{status, t_eff, evidence_clock_id, criteria_version, w_eff_s, evidence, reason}`), with
  `status ∈ {CONFIRMED, CONFIRMED_NO_EFFECT, UNKNOWN_EFFECT}` and `CONFIRMED ⇔ t_eff != null`.
- Criterion (Hoàng-locked): CONFIRMED only when the actual restricted seed rows are truly returned —
  not HTTP 200, not a log line containing "SQL". Insufficient coverage of the window → `UNKNOWN_EFFECT`.
- The O plane never carries seed/variant/expected/template-label/onset schedule; observed query/log
  signal is not deleted to flatter a detector; the evaluator must not read the answer key and emit a
  verdict on the detector's behalf. If the current event format cannot represent the SQLi evidence, the
  gap is described rather than the schema/scorer changed ad hoc.

## 7. Policy opt-in, default disabled; runtime deferred

- A separate SQLi policy capability, default **disabled**. When enabled it locks the namespace/service +
  the specific private-ingress endpoint taken from the accepted runtime-02 profile, single path
  `/fixture/catalog/search`. No public endpoint, userinfo, fragment, host/port/path variants, no
  environment redirect/proxy. Loopback/transport tests keep their own fixture; localhost/public URLs are
  never added to the production policy.
- Runtime AC-04 (before/after, benign control traffic, trusted source IP, request-ID stitching across
  response/proxy/fixture/log, two separate sources, anti-spoofed-XFF) is **prepared** here as an offline
  verification path + a proposed runtime envelope — **not run**, not claimed. Lab state is unverified;
  ZER-41 runtime results are history in the accepted profile.

## 8. File scope actually planned (subset of the allowlist)

Go: `cmd/main.go` (register SQLI executor), `internal/attack/sqli.go` + `sqli_test.go` +
`internal/attack/testdata/zer42/`, `internal/guard/policy.go` + `sqli_test.go`,
`internal/validation/target.go` + `target_test.go` (separate SQLi target validation).
Python: `nemesis/command_guard.py`, `nemesis/main.py`, `tests/test_sqli_executor.py`,
`tests/fixtures/zer42/`.
Manifests (render-only, disabled sample): `command-guard-config.yaml`, `sqli-executor-lab.yaml`.
Scripts (offline/prepare, no side effect on `--help`): `infrastructure/scripts/verify-sqli-executor.sh`,
`sqli_executor_runtime.py`.
CI: add SQLi checks to the existing offline job only.
Docs: `docs/runbooks/sqli-executor.md`, `docs/evidence/ZER-42/verification.md` + raw.

Out of scope / unchanged: `executor.go` type schema beyond what SQLI needs, locked event contract,
ZER-41 fixture app/seed/expected and R1 evidence, auth/ledger/dispatch internals, measurement/scorer,
Gaia/Hephaestus, dashboard, and the CPU/flood/kill executors. No commit/push/PR/merge/Linear.

## 9. Sửa gom theo Codex review (ZR42-01…05) — 26/10/2026

Codex review (`codex-review.md`) chốt CHANGES_REQUIRED_OFFLINE. Ghi quyết định biểu diễn raw/đánh giá
trước khi sửa; không đổi định nghĩa KPI, schema event hay scorer đã khóa.

**Biểu diễn raw SQLi có thời điểm/chuỗi/đồng hồ (ZR42-01/03/05).** `SQLiObservation` thêm `clockId`,
`clockSource` (enum contract HOST_SHARED|OFF_HOST|UNKNOWN; executor loopback offline = UNKNOWN) và
`windowStart` (T_req — mốc bắt đầu command). Mỗi `SQLiSend` thêm `seq` (1-based), `startedAt` (lúc phát
send), `observedAt` (lúc quan sát response/lỗi — đây là mốc bằng chứng thực), `requestId` (correlation id
executor gửi đi, bounded ASCII) và `responseId` (X-Request-Id fixture trả, khóa ghép sang log/IP fixture).
Thời điểm trên trục đồng hồ executor, không phải `AttackResult.timestamp` (tạo trước vòng gửi).

**Đánh giá effect bám mẫu thật + phủ cửa sổ (ZR42-01/02), soi gương `scorer.no_effect`.** CONFIRMED chỉ
khi một send *dùng được* (clean, đúng schema) trả hàng restricted thuộc oracle; T_eff = `observedAt` của
chính send ấy. Thiếu `observedAt`/clock đã xác thực → không stamp được → UNKNOWN (không CONFIRMED với mốc
giả). NO_EFFECT chỉ khi: có clock + `windowStart`, `w_eff_s`≥1 và `min_clean_sends`≥1 hợp lệ; cửa sổ
[T_req, T_req+W_eff] được các send dùng được phủ kín (mẫu đầu cách T_req ≤ gap, T_req+W_eff cách mẫu cuối
≤ gap, mọi khoảng liên tiếp ≤ gap), đủ `min_clean_sends`, và không có send lỗi/sai-schema rơi vào cửa sổ.
Mọi trường hợp khác (thiếu thời gian/clock/phủ, dữ liệu lỗi, tham số đánh giá không hợp lệ) → UNKNOWN. KPI
`t_eff`/`w_eff_s`/MTTD không đổi định nghĩa; chỉ nguồn mốc được sửa cho đúng.

**Schema response (ZR42-02).** HTTP 200 chỉ được coi dữ liệu sạch khi `results` là mảng có mặt, `count`
có mặt, `count`≥0 và `count==len(results)`, mỗi row có `sku` chuỗi khác rỗng và `visibility` ∈
{public,restricted}. Thiếu/null/`count` âm/mâu thuẫn/row thiếu field → lỗi `SCHEMA` rõ, không clean,
effect giữ UNKNOWN. Không dùng DisallowUnknownFields ở row (fixture có name/category/price_cents).

**Nhịp gửi (ZR42-03).** Thay ticker bằng lịch tính từ mốc phát thực tế: `nextAt = startSend+interval`,
chờ bằng timer tới `nextAt`, không phát bù tick tích lại; chờ vẫn bị ngắt bởi context/deadline. Response
chậm chỉ đẩy send muộn hơn, không bao giờ nhanh hơn interval.

**Ranh giới private ingress (ZR42-04).** Thu hẹp profile endpoint (Go+Python đồng nhất): host phải là DNS
in-cluster dạng `<service>.<namespace>.svc.cluster.local` (từ chối IP literal → chặn TEST-NET/loopback;
từ chối host trần), và từ chối đi thẳng fixture (`sqli-fixture.zd-sqli-lab`) — phải qua ingress để giữ
điểm quan sát IP. Executor thêm preflight resolver (injectable; mặc định `net` thật) kiểm *mọi* địa chỉ
phân giải phải là private (RFC1918/ULA), không loopback/link-local/public → REJECT 0 send; test offline
dùng fake resolver (10.x cho phép, 203.0.113.x/127.0.0.1 từ chối). Địa chỉ private thật + quyền lab chốt
riêng sau review; không nới endpoint công khai để test.

**Dấu vết request → event H (ZR42-05).** Executor gửi `X-Correlation-Id` mỗi send và ghi `responseId`
(X-Request-Id fixture) để ghép command→request→log fixture. `sqli_executor_runtime.py` thêm
`emit_evidence(result, context, clock, sink)` xuyên entrypoint: dựng FAULT_EXECUTOR_RESULT (plane H,
source `fault_executor`) rồi EFFECT_EVALUATED (source `effect_evaluator`) với `causation_id` =
event_id của FAULT_EXECUTOR_RESULT, dùng lại `contract.Producer`; sink là hàm thuần (list) — không Kafka,
không broker. Kiểm offline qua fake sink: hai event validate, causation nối, không lọt seed/oracle sang O.

File bổ sung trong allowlist cho lượt này: `scratch/zer42/codex-fix/` (snapshot before + log),
`chaos-worker/internal/attack/testdata` nếu cần. `dispatch.go`, auth/ledger, legacy executors,
fixture/seed/expected ZER-41, contract/scorer, shared agents, dirty sửa tài nguyên: giữ nguyên.
