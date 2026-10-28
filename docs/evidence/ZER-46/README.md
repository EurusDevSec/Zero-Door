# ZER-46 — ĐẠT NGHIỆM THU KỸ THUẬT COMPONENT

[Runtime09](runtime-09/README.md) đã được raw verifier và [reviewer độc lập](runtime-09/independent-review.md) chấp nhận đủ AC-01/02: block/benign, fixture+writer restart, replay,TTL180/expiry/unblock và cleanup thực đo.29HTTP/29joins/4TCP,83guard samples/PSImax0,36; toàn bộ actor đã dừng. **READY_FOR_PUBLICATION_REVIEW; không cần thêm lượt lab.**

[Gói publication](publication-package.md) đã chuẩn bị, chưa commit/push/PR/CIremote/merge/Hoàngacceptance/Done. Boutique business chưa đạt; không labhealth/R1/KPI/LLM/end-to-endPASS. Historicalfailed/UNKNOWNgiữ nguyên, không cộng các lượt thànhPASS. Các checkpoint dưới là lịch sử.

# Kết luận hiện hành — điều tra PSI và review đã khép

[Hai lỗi runner đã sửa, review độc lập đạt](gate-audit/psi-resolution.md),68testoffline và native Windows identity/exit proof đạt. Chrome/Claude là giả thuyết chưa chứng minh; current25mẫu/120sPSI0. [Gói AC một lần](runtime-prep/acceptance-proposal.md) nguồn38file đã khóa, **NOT_APPROVED/NOT_RUN**, đang chờ Hoàng chấp nhận rationale readiness hiện tại và fullboundedrun. Không reuse08/diagnostic hoặc tựretry; ZER-46 vẫn ACpartial/NOT_READY_FOR_PUBLICATION. Các checkpoint dưới là lịch sử.

# Cập nhật hiện hành — runner hoàn chỉnh offline và diagnostic01 đã khép

59/59offline đạt, [gói sửa](gate-audit/runner-complete.md) + [receipt](gate-audit/runner-complete-verification.json). [Một chẩn đoán đã duyệt](client-diagnostic-01/README.md) kết thúc234,89s:1GET200+trace,guardPSImax0,12,cleanup tài nguyên riêngCLEAN/shared3PVCnguyên;Boutique chưa khỏe. PSI08 chưa tái hiện, chưa causal fix. **AC_PARTIAL / NOT_READY_FOR_PUBLICATION; dừng runtime, không tựretry.** Còn fullAC runtime/review/merge/Hoàngacceptance. Các checkpoint dưới là lịch sử.

> **Checkpoint hiện hành28/10: NO_GO cho runtime tiếp theo.** [Audit trọn runner và điểm dừng](gate-audit/stop-audit.md):08 khép/HTTP UNKNOWN/owned cleanup CLEAN; ba sửa runner được kiểm38/38 offline. Root cause PSI và điều kiện Ready toàn gói chưa khép. Không lượt09, không PASS/Done/publication. Các checkpoint dưới là lịch sử.

# ZER-46 — checkpoint hiện hành, 28/10/2026

> **Mới nhất: [runtime08](runtime-08/README.md)** đã được duyệt và kết thúc203,05s tại PSI16,37>5; host/WSL vẫn đủ dung lượng. Fixture Ready; một client exec bị guard hủy, HTTP UNKNOWN/không response receipt,0writer/rule. Snapshot stall tập trung sourceA (PSI48,64), không OOM; CPU throttle đồng thời, chưa root cause duy nhất. Cleanup UIDabsent/shared spec/UID/restart/3PVC nguyên. **NOT_MET / NOT_READY_FOR_PUBLICATION.** Không cộng partial07 thành PASS; chưa có lượt09 hoặc quyền retry. Các con trỏ phía dưới là lịch sử.

> **Mới nhất: [runtime07](runtime-07/README.md)** quan sát block A403, benign B200+CRUD, nguồn IP/spoof/isolation trước replacement. Dừng sau thay Pod vì collector chọn log Pod cũ; HTTP16 chưa join nên AC toàn chuỗi chưa đạt. Writer replay/expiry chưa chạy tới. Cleanup riêng CLEAN/shared preserved, hai PID writer đã thoát. Collector Pod/UID đã sửa;35 harness tests đạt. [Gói08](runtime-prep/logs-retry-proposal.md) NOT_APPROVED/NOT_RUN. Các checkpoint06/05 bên dưới là lịch sử.

> **Mới nhất: [runtime06](runtime-06/README.md)** fixture đã qua hooked-policy gate và Ready trên agent. Lượt dừng trước fixtureHTTP do collector docker top thiếuPID; lỗi harness đã sửa và lệnh đúng kiểm chỉ đọc thành công. Owned cleanup CLEAN/shared preserved, Boutique chưa khỏe. [Gói07](runtime-prep/agent-retry-proposal.md) giữ nguyên envelope/AC, NOT_APPROVED/NOT_RUN. AC chưa đạt, chưa publication. Các đoạn05/profile-agent bên dưới là checkpoint trước06.

**OFFLINE_COMPONENT_VERIFIED / RUNTIME05_POLICY_GATE_STOP / AC_PARTIAL / NOT_READY_FOR_PUBLICATION.**

Hoàng đã giải phóng RAM và duyệt các gói runtime03/04/05; tất cả đã kết thúc. Không còn chờ báo RAM. Chưa có quyền hoặc lượt runtime06 mới.

| Lượt | Kết quả | Cleanup / giới hạn |
| --- | --- | --- |
| [03](runtime-03/README.md) | Hai pinned pull; dừng Boutique warmup, chưa build/apply fixture | Không tài nguyên mới, business chưa khỏe |
| [04](runtime-04/README.md) | Build/import1 lần thành công; PSI15,02 dừng startup | Namespace absent/shared preserved theo raw reconciliation; receipt collector INCOMPLETE giữ nguyên |
| [05](runtime-05/README.md) | Cached-only0build/import/pull; RAM đạt, proxy +2source Ready; fixture gate không có rule32poll | Owned resources CLEAN, shared spec/UID/restart/3PVC nguyên;0fixtureHTTP/0writer, Boutique chưa khỏe |

[Gate audit](gate-audit/README.md) chốt server-0 thiếu Pod firewall và dấu hiệu stale node IP ở startup; chưa causal proof trong bộ nhớ controller. Agent-0 có18Pod hiện hữu với hook đúng và cache đúng artifact04. Không sửa hạ tầng dùng chung. [Gói node agent](runtime-prep/agent-fixture-proposal.md) giữ mọi guard/AC và chuẩn bị một lượt20phút gồm5phút cleanup, cached-only, **NOT_APPROVED / NOT_RUN**.

Kiểm hiện hành: containment24cases trên mỗi production pin (delta replay sau restart); baseline cũ102×2 được giữ dưới đây, không ghi thành một full-suite run mới. Harness31cases đạt; parser offline đối chiếu18Pod snapshot thật. Bandit harness chỉ kiểm ngưỡng high severity/high confidence, không finding trong ngưỡng. GitNexus query thiếu FTS/index stale; không là proof.

AC-01 còn thiếu fresh fixture IP/trust/anti-spoof/isolation trên revision mới. AC-02 còn thiếu block attacker/benign CRUD, TTL180, Pod/writer restart, expiry và policy cleanup thực. Production R1 executor/consumer vẫn disabled; chưa tích hợp Gaia→healer, chưa KPI/end-to-end/review độc lập/merge/Hoàng acceptance. Không Done hoặc publication.

---

## Baseline source offline và các checkpoint ban đầu — lịch sử

### Source containment và TTL trước runtime03–05

**OFFLINE_COMPONENT_VERIFIED / RUNTIME_PREFLIGHT_STOPPED / AC_PARTIAL / NOT_READY_FOR_PUBLICATION.**

[Runtime-01](runtime-01/README.md) được Hoàng duyệt sau gói offline: Kubernetes API127.0.0.1:7356 refused, Docker ps timeout12s; dừng trước mọi build/mutation/app probe. Không tạo tài nguyên; live inventory readback INCOMPLETE. Docker Desktop/backend có process, engine health chưa xác minh. Không restart Docker/WSL hoặc tự retry.
HEAD9567830020954bf3f30fd5a74240747be0c8ec1c, dirty branch zer-42-bounded-sqli. Hoàng giao riêng ZER-46 sau
khi chốt SQLi-only; issue đã In Progress trên Linear. Không tạo payload, mở lại ZER-43 hoặc chạy lab.

## Thay đổi và lý do

Legacy action_block_ip tạo NetworkPolicy cho target-app và chỉ hẹn threading.Timer; fixture nằm trong
zd-sqli-lab sau private proxy, nên peer TCP không phải client cần chặn. Production R1 hiện không khởi tạo
executor; legacy SUCCESS chỉ chứng minh API create, chưa chứng minh containment. Không suy Flannel không
hỗ trợ policy; ZER-41 đã có proof controller/rule/isolation ở profile hồi phục, cần kiểm lại fresh runtime.

Đã thêm enforcement opt-in trước toàn bộ supported /fixture handlers, dùng resolver trusted-source cũ.
Reader ConfigMap file mở lại mỗi request, strict schema/size bounds, missing/corrupt/UNKNOWN trả503 riêng;
active source bị403; client lành cùng proxy vẫn200. /ready kiểm cả policy; /health vẫn liveness. Log giữ
requestID và thêm enforcement point/policy SHA/action IDs, không thêm profile/seed labels.

Prepared writer pin namespace/name/UID/scope/run/trial, attacker khác benign/proxy, exact proxy /32,
joined source observation≤60s, TTL≤300s, CAS≤3 và timeout. Trạng thái ở ConfigMap ngoài Pod; expiry tuyệt
đối kiểm theo thời gian request nên không cần healer/timer sống. API accepted, effective block, expiry và
storage cleanup là các mốc riêng. Replay không kéo dài expiry; ambiguous timeout giữ action ID để reconcile.
Production ModeGate/R1_EXECUTOR/consumer/reset không thay đổi; backend chưa được copy/wire vào production
Hephaestus image. Tích hợp phải giữ authenticated decision, binding observation và durable claim ledger;
không được lấy body/model label làm source evidence. Component harness không thay vòng Gaia→healer.

```text
source A / source B → private Traefik (no public ingress) → fixture:9140
                           XFF verified against exact proxy /32
fixture trusted client → projected ConfigMap rule → query/CRUD or403
writer component → UID+scope+resourceVersion CAS → dedicated ConfigMap
absolute expiry → unblock per request, independent of writer lifecycle
```

## Kiểm chứng

- Hai dependency pin sản xuất: **102/102 mỗi pin**, tổng204 lượt kiểm: containment23,
  fixture42, HTTP lifecycle15, command integration13, modes3, CI6. Logs trong results/. Không lab/network
  ngoài disposable loopback service và temp DB/policy. Không dùng payload cho containment tests.
- Fail-before: HTTPBoundary trên app trước sửa chạy6case, **4 failures,0errors** đúng các hành vi block,
  UNKNOWN/state và restart còn thiếu; hai case default/expired vốn trả200 vẫn đạt. Mã hiện tại6/6 đạt.
- Bandit không phát hiện issue ở fixture và backend. Candidate ConfigMap/Role/RoleBinding qua OpenAPI;
  RBAC chỉ get/update đúng một ConfigMap. CI fixture thêm test containment trong matrix hai pin hiện có.
- Renderer private17resources kiểm offline:2Deployment,2source Pod,ClusterIP,không public route; command
  gate compile cả outer/inner mà không execute. review-only.safe.yaml có IP giả, chưa apply; live pins phải
  lấy mới. Artifact ZER-41/42 và dirty ngoài allowlist giữ nguyên, xác minh hash ở verification.json.

Test logs pre-review được giữ riêng; chỉ kết quả root results/ là lượt final source. Mọi raw runtime cũ
giữ nguyên; không biến test loopback thành chứng minh NAT/K3s/controller/ConfigMap projection thật.

## AC và phần còn thiếu

| AC sống ZER-46/ZER-17 | Có trong gói này | Còn thiếu |
| --- | --- | --- |
| AC-01 nguồn IP/enforcement/NAT/controller | Chọn fixture trusted-client, giữ anti-spoof resolver, topology/selector candidate, reuse proof ZER-41 làm provenance | Fresh actual controller/args,2sourceIPs,proxy trust/isolation/probe trên revision mới |
| AC-02 block/benign/TTL/restart/reset/cleanup | Offline403/200,TTL boundary,persistent external state,CAS/idempotency/error cases; reset tách storage cleanup | Real projection/block/benign,Pod restart/unblock,observed cleanup và review/integration theo AC |

[Gói lab đề nghị](runtime-prep/next-run-proposal.md): một attempt20phút gồm5phút cleanup, chỉ private
safe fixture/ordinary probes, một TTL180s và một Pod fixture replacement. **Đã được Hoàng duyệt cho runtime-01; lượt này dừng preflight, component chưa chạy.**
Không publication, merge hoặc Hoàng acceptance. Source pin ở source-hashes.json; intake/preservation và
baseline trước sửa ở scratch/zer46/. Linear giữ live metadata/AC, không dùng README làm board.

GitNexus đã được gọi refresh local sau sửa source nhưng bulk COPY thất bại: LadybugDB buffer pool256MiB exhausted. Log ở results/gitnexus-index.log. Không tăng RAM/global config hoặc bật embeddings để xử lý. Index sau lượt lỗi không được coi fresh/complete; review ở đây dựa source trực tiếp, impact trước sửa và regression. Cần refresh thành công trước khi dựa graph cho lần sửa sau.
