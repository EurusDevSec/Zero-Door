# Claude cross-review — ZER-42 Codex fix-02

**Verdict: READY_FOR_BOUNDED_LAB_REVIEW / PARTIAL — 26/10/2026 (+07:00).** Đã review độc lập gói Codex
fix-02 (`codex-fix02/README.md`) đóng `FX42-R1…R4` của [codex-retest.md](codex-retest.md). Không còn finding
P1/P2 offline. **Chưa Done**: runtime (image/manifest/lab), CI Linux/race và owner acceptance vẫn chưa có;
chứng minh source-IP thật tại fixture vẫn là việc của một lab bounded được duyệt riêng.

Review chỉ đọc + chạy offline. HEAD `7db9d9f9bc265b07a4cb361923ee535f707adeda`, checkout `zer-41-sqli-fixture`,
staged rỗng, `git diff --check` sạch. Không lab/build/model/API, không commit/push/PR, không đổi Linear. Không
sửa ZER-41, scorer/contract R1 hay dirty ngoài gói. Báo cáo Codex (`codex-review.md`, `codex-retest.md`) và gói
fix-02 giữ chỉ đọc; mọi probe độc lập của tôi chạy ngoài repo (session scratchpad), scratch/ đã gitignore nên
review không thêm dirty nào.

## 1. Kiểm lại chuỗi offline (tự chạy, không chỉ tin script Codex)

| Hạng mục | Kết quả |
| --- | --- |
| Python SQLi `test_sqli_executor` — pin Nemesis / Hephaestus | **24 / 24 mỗi pin** |
| Legacy `test_command_guards` — hai pin | **7 / 7 mỗi pin** (không regress) |
| Bandit `sqli_executor_runtime.py` ngưỡng `-lll -iii` | 0 finding |
| Go `go test ./...` (6 package) / `go vet ./...` / `gofmt -l` nguồn SQLi | PASS / sạch / rỗng |
| Bridge: Go result thật → evaluator → event → `scorer.semantic` | PASS, `t_eff` khớp `contract.STAMP` `.mmmZ`, scorer nhận |
| fail-before (`scratch/zer42/codex-fix02/fail-before.sh`) | before = CONFIRMED_NO_EFFECT/AttributeError/header-stamp/generic-service; after = UNKNOWN/REJECT |
| Toàn vẹn (`final-check.sh`) | ZER-41 app `37c7a045…`, seed `ec9f818b…`, expected `a626930d…`, receipt runtime-02 `60e6e60b…`, retest `e1e53052…` nguyên; không còn authority `traefik.*` cũ |

## 2. Đóng FX42-R1…R4 — xác nhận độc lập

- **FX42-R1 timestamp/consumer — CLOSED offline.** `one()` chốt `observedAt` trong `defer` chạy sau khi đọc/
  kiểm body (hoặc lỗi terminal), không còn ở header; `isoAt` floor UTC về `.mmmZ`
  ([sqli.go:299–303,365–368](../../../chaos-worker/internal/attack/sqli.go)). Go result thật cho `startedAt`
  `.157Z` → `observedAt` `.278Z` (bám body chậm ~121 ms), và scorer **nhận** `t_eff` đã floor — đúng phản ví dụ
  retest trước đây làm scorer trả INVALID.
- **FX42-R2 raw thiếu/mâu thuẫn — CLOSED offline.** Evaluator validate hình dạng/kiểu/count/thời gian và tham số
  hữu hạn ở biên; thiếu/không nhất quán → UNKNOWN; đối chứng raw đầy đủ vẫn CONFIRMED/CONFIRMED_NO_EFFECT. Bốn
  phản ví dụ retest (`restrictedRows>0` thiếu SKU, record lỗi thiếu `observedAt`, phần tử `null`, `gap=inf`) nay
  đều UNKNOWN; fail-before chứng minh before-source trả sai.
- **FX42-R3 endpoint/peer thực — CLOSED offline (phần kiểm được offline).** Profile thu về đúng authority
  `zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000` ở cả Go (`u.Host`) và Python (`u.netloc`), bỏ regex
  nhận mọi `<svc>.<ns>` — khép lỗ "trusted-but-wrong config" (frontend.target-app, fixture-copy) retest nêu.
  `checkPeer` bắt **mọi** IP resolve phải private **và** `== ApprovedIP`; `pinnedDial` dial thẳng IP số đã duyệt
  (không resolve lại), kiểm `address==authority` và peer sau khi nối, `DisableKeepAlives` nên mỗi send nối lại +
  kiểm lại. `main.go` fail-closed khi SQLi bật mà `ZD_SQLI_INGRESS_IP` thiếu/không private. Source-IP thật tại
  fixture vẫn cần lab — gói nêu đúng, không tự nhận.
- **FX42-R4 raw bền/export — CLOSED offline.** `FAULT_EXECUTOR_RESULT` giữ full `raw_result` + `raw_result_sha256`;
  `prepare_bundle` ghi write-once (`xb`), `archive_bundle` đi qua H Archive/export R1, `recheck_export` tái tính
  từ raw. Executor-only CONFIRMED_NO_EFFECT bị hạ UNKNOWN chờ `PROBE_SAMPLE` độc lập.

## 3. Ba vùng được yêu cầu đào sâu — phản ví dụ độc lập (đều fail-closed đúng)

Probe của tôi (ngoài repo, pin Nemesis) — OVERALL PASS:

1. **DNS/dial peer.** Test Go `TestSQLiExecutorPeerCheck` từ chối public TEST-NET/loopback/empty/resolver-error/
   mixed(private≠approved) → 0 send; `TestSQLiPinnedDialUsesApprovedNumericPeer` chứng minh dial ghim
   `10.1.2.3:8000` và authority lạ bị chặn. Tôi xác nhận không còn đường resolve lại không kiểm (transport dùng
   `DialContext` ghim IP số). *Khoảng trống kiểm thử (không phải lỗi):* nhánh từ chối peer-mismatch **sau** dial
   chưa có test case fail (trong production là tautology vì đã dial IP số) — an toàn, nên là nit test-coverage.
2. **Replay archive.** Ngoài test gói (replay idempotent, binding-conflict, duplicate dedup theo `event_id`,
   COVER5→UNKNOWN), tôi thêm: (a) sửa `raw_result` trên bundle đã lưu rồi archive → **RAW_RESULT_CONFLICT**;
   (b) export bị seal **read-only**, và khi cố gỡ event EFFECT thì loader `measurement.raw.Export` bắt ngay bằng
   **hash/size mismatch** (`RawError`) — tamper bị chặn ở cả tầng binding lẫn tầng hash export.
3. **NO_EFFECT không có PROBE_SAMPLE.** `archive_payload` hạ CONFIRMED_NO_EFFECT → UNKNOWN_EFFECT trong event
   phát ra (giữ `executor_assessment` để truy vết), đúng yêu cầu scorer. Thêm probe: 21 send → UNKNOWN; disclosure
   có `observedAt < startedAt` → UNKNOWN (không bịa `t_eff`); hai disclosure → CONFIRMED tại `t_eff` sớm nhất.

## 4. Quan sát không chặn (P3 — để polish, không ảnh hưởng hành vi/an toàn)

1. `pinnedDial` hard-code `remote.Port != 8000`, lặp port của authority khóa. Fail-closed nếu port đổi, nhưng nên
   suy ra từ authority để tránh landmine bảo trì.
2. `main.go` dùng `IsPrivate/IsLoopback/IsLinkLocalUnicast` thay vì gọi thẳng helper `isPrivateClusterIP` mà
   `checkPeer` dùng; kết quả tương đương (checkPeer tái kiểm, fail-closed) nhưng hai nơi nên dùng chung một hàm.
3. CLI `--evaluate` in được `CONFIRMED_NO_EFFECT` (đánh giá thuần), trong khi event archive hạ UNKNOWN; đã ghi rõ
   trong docstring, nhưng người đọc output CLI như verdict có thể hiểu nhầm.

## 5. Còn lại trước khi Done (không thuộc gói offline này)

- Lab bounded được **duyệt riêng** theo envelope đề xuất `docs/runbooks/sqli-executor.md` §6 (không dùng lại quyền
  ZER-41): chứng minh source-IP tin cậy tại fixture, before/after + benign control, stitch correlation/request ID
  xuyên worker↔proxy↔fixture↔H archive↔export.
- CI Linux + `-race`, image build/import, broker/runtime topology, parent ZER-13 AC-04.
- ZER-42 và cha ZER-13 giữ **In Progress / không Done** đến khi có runtime được duyệt, CI/publication và owner
  acceptance.
