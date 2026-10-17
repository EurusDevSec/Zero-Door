# ZERO DOOR — D8. Phản hồi review Codex (C01–C05)

**Trạng thái: COMPLETE — đã điền đủ C01–C05; chờ Codex review.**

File bổ sung có liên kết cho [hydration gốc](2026-10-17-claude-code-hydration-handoff.md). File này trả lời các yêu cầu E3 (C01–C05), theo cách làm Codex ghi ở E5 và ở phần Codex cuối [báo cáo blockers](2026-10-17-claude-code-session-blockers.md). Đây không phải một bản hydration độc lập.

- Người viết: Claude Code. Bắt đầu 2026-10-17 17:59 Asia/Saigon.
- Repo `main`, HEAD `f9623a31c1062adb1ca7880041b4183cc8a7d28f`.
- Trước khi ghi: chỉ có ba file untracked trong `docs/handoff/` (hydration gốc, blockers, bản trích DOCX). Không có thay đổi tracked.
- File được ghi trong lượt này: **chỉ file này**. Hydration gốc, blockers, bản trích DOCX và mã ứng dụng giữ nguyên.
- Không chạy lab, gọi endpoint gây tác động, gọi LLM, build/deploy, sửa quyền/model hay commit/push.
- Nhãn bằng chứng dùng như mục C2 của hydration gốc.

Mỗi mục gồm bốn phần: kết luận cũ bị thay thế, kết luận mới, nguồn, và điều chưa chứng minh.

## C01 — Controller NetworkPolicy và hiệu lực block IP

**Kết luận cũ bị thay thế.** Các câu sau trong hydration gốc được rút lại: "Flannel mặc định của K3s bỏ qua NetworkPolicy", "BLOCK_IP gần như không enforce", "tạo policy thành công ≠ chặn thật vì CNI". Chúng nằm ở bảng D1 (dòng manifests), D2 ý (3), Q05 mục Block IP, D4 đoạn "CNI Flannel", D5 dòng CNI và D7 dòng grep CNI. Đề xuất ở D5 kiểm tra bằng `kubectl get pods -n kube-system` cũng được thay.

**Lỗi của tôi.** Tôi đã coi một comment trong manifest là căn cứ kỹ thuật. Comment là ghi chú của người viết, không phải bằng chứng về hành vi của K3s.

**Kết luận mới.**
- Repo **không có cấu hình tắt** controller policy của K3s. `infrastructure/k3d-config.yaml:22-27` chỉ truyền `--disable=traefik`. Grep `disable-network-policy` trên `k3d-config.yaml` và `infrastructure/scripts/setup-phase1.ps1` không có kết quả (LIVE_READ_ONLY, 17:08). Đây là SOURCE_VERIFIED cho cấu hình trong repo, chưa phải cho cluster đang chạy.
- Theo tài liệu K3s, K3s nhúng một network policy controller và tắt nó bằng `--disable-network-policy`. Vì vậy dùng Flannel không tự suy ra được policy bị bỏ qua.
- Lab hiện có enforce policy hay không: **UNKNOWN**. Tôi không có bằng chứng runtime theo chiều nào.
- Thiếu sót của BLOCK_IP đã chứng minh từ source (SOURCE_VERIFIED), không phụ thuộc controller:
  - Gaia không gắn `sourceIP` vào alert SUSPICIOUS_LOG (`agent-orchestrator/gaia/main.py:337-347`).
  - Hephaestus lấy IP từ `sourceIP`, rồi regex trên `description`, cuối cùng fallback `0.0.0.0` (`agent-orchestrator/hephaestus/main.py:457-465`).
  - Status SUCCESS chỉ phản ánh API tạo policy thành công (`hephaestus/main.py:371-386`), chưa có kiểm chứng hiệu lực.
  - TTL xóa policy chạy bằng `threading.Timer` trong bộ nhớ (`hephaestus/main.py:375-378`); timer mất nếu Hephaestus khởi động lại.

**Nguồn.**
- Tài liệu K3s: [Networking Services — Network Policy Controller](https://docs.k3s.io/networking/networking-services#network-policy-controller), đọc qua WebFetch lúc ~17:12 ngày 17/10. Trang nói controller dựng trên thư viện netpol của kube-router và tắt bằng `--disable-network-policy`. Trang không nói về Flannel.
- `infrastructure/k3d-config.yaml:22-27`; `infrastructure/manifests/network-policies.yaml:4-5` (comment cần sửa ở task riêng).
- Mã như liệt kê ở trên.

**Chưa chứng minh và cách kiểm chứng tiếp.**
- Phiên bản K3s và args thật của server node. Kiểm tra log K3s về network policy controller. Vì controller chạy trong tiến trình K3s, liệt kê pod `kube-system` đơn lẻ chưa đủ.
- Selector của policy là `app=<service>` (`hephaestus/main.py:351-353`), còn Gaia đặt service theo `container_name` (`gaia/main.py:340`). INFERENCE: cần đối chiếu với nhãn pod thật trong `target-app` xem hai giá trị có khớp không.
- IP nguồn quan sát được sau ingress/NAT và nơi chặn phù hợp.
- Kiểm thử theo protocol của roadmap: nguồn bị chặn mất truy cập, client hợp lệ vẫn hoàn tất giao dịch.
- Không có căn cứ đề xuất thay CNI hay dựng lại cluster.

## C02 — Duration trong lệnh so với thời gian và tác động thực thi

**Kết luận cũ bị thay thế.** Ở Q02 tôi viết rằng cả hai endpoint "luôn chạy tối thiểu 90 giây" và gọi nhầm sẽ "thực sự phát một lượt tấn công ≥90s". D4 có ý tương tự ở đoạn "Tác dụng phụ health-check". Câu đó gộp tham số trong lệnh với hành vi thực thi, nên được thay.

**Kết luận mới.**
- Nemesis chỉ đặt **tham số** `parameters.duration`: tối thiểu 90 ở đường manual (`agent-orchestrator/nemesis/main.py:434`), trong khoảng 90–120 ở đường LLM (`:477-478`). Lệnh cũng mang `safetyLimits.maxDuration` (`:177-180`). Đây là SOURCE_VERIFIED về nội dung lệnh, không phải về thời gian chạy.
- Thời gian và tác động thật phụ thuộc vào worker:
  - Lệnh có thể bị từ chối trước khi chạy: namespace, URL hoặc loại không hỗ trợ đều trả `REJECTED` (`chaos-worker/cmd/main.go:128-182`).
  - Chỉ một số executor dùng `EffectiveDuration` (`chaos-worker/internal/attack/executor.go:86-96`): `http_flood.go:41` và `cpu_stress.go:34`.
  - Executor xóa pod không dùng duration. Nó xử lý tối đa `killCount` pod (mặc định 1) rồi trả kết quả (`pod_kill.go:41-45,78-118`).
  - Worker còn đặt timeout ngoài là `MaxDurationSec + 10` giây (`cmd/main.go:186-188`).
- Status `SUCCESS` trong `attack.results` chỉ nói executor chạy xong nhánh của nó. Status này không chứng minh target bị ảnh hưởng (xem Q04 trong hydration gốc).
- **Diễn đạt thay thế cho Q02:** các endpoint POST của Nemesis có thể phát lệnh gây tác động lên lab. Duration là tham số; thời gian và tác động phải kiểm tra theo executor và kết quả thực tế. Vẫn giữ khuyến nghị: kiểm tra sức khỏe bằng `GET /healthz` (`nemesis/main.py:413`), không dùng các endpoint POST.

**Chưa chứng minh.**
- Thời gian chạy thật của từng loại lệnh trên lab: chưa đo, cần log worker kèm `commandId`.
- Comment của `EffectiveDuration` ghi "lower of the command duration and the global max-duration". Code lại ưu tiên `maxDuration` trong lệnh khi giá trị này lớn hơn 0 (`executor.go:88-91`). Điểm này trùng F09 của audit cũ và cần xử lý ở task sửa mã, không thuộc lượt này.

## C03 — Tác dụng phụ của script, các đường reset và cleanup

**Kết luận cũ bị thay thế.**
- Q08: nhóm "Script chỉ rebuild/khởi động (an toàn)" gồm `start-demo.ps1` và `rebuild-nemesis.ps1`.
- Q08: câu gộp "`experiment_runner_direct.py`/`/experiment/reset` thay đổi replicas + xóa `heal_history`/NetworkPolicy".
- Q04, cột Cleanup của resource exhaustion: "auto-delete pod sau duration".

**Kết luận mới — script (SOURCE_VERIFIED).**
- `start-demo.ps1` không chỉ mở port-forward. Dòng 30-32 lấy **mọi** tiến trình tên `kubectl` trên máy rồi `Stop-Process -Force`, kể cả tiến trình của project khác. Dòng 14 và các lệnh port-forward dùng context hiện hành, không chỉ định `--context`.
- `rebuild-nemesis.ps1` thay đổi workload: build image không cache (`:14`), import vào K3d (`:24`), `rollout restart` Nemesis (`:34`). Sau đó dừng tiến trình đang giữ cổng 9092 (`:45-53`).
- `recreate-cluster.ps1:20` xóa cluster (giữ nguyên như Q08 cũ).

**Kết luận mới — ba đường dọn dẹp tách riêng (SOURCE_VERIFIED).**

| Đường | Điểm vào | Làm gì | Không làm gì |
| --- | --- | --- | --- |
| Runner reset | `reset_steady_state()` trong `infrastructure/scripts/experiment_runner_direct.py:136-149`, gọi ở `:488` khi không có `--no-reset` | Scale `frontend`, `cartservice`, `productcatalogservice` về 1; chạy `kubectl delete networkpolicies -n target-app -l hephaestus.io/managed=true --ignore-not-found=true` (`:143-147`); chờ 15s | Không kiểm tra return code của `subprocess.run`, nên có lệnh xóa chưa có nghĩa xóa thành công |
| Endpoint reset | `POST /experiment/reset` của Hephaestus (`agent-orchestrator/hephaestus/main.py:629-653`). Runner gọi mỗi lượt qua `experiment_reset()` (`experiment_runner_direct.py:256-261,271`). Dashboard gọi qua `/api/reset` (`static/app.js:415` → `nemesis/main.py:719-733`) | Xóa cooldown và `heal_history`; scale 9 deployment về 1 | **Không** xóa NetworkPolicy; không dừng lệnh đang chạy; không dọn pod stress |
| TTL cleanup | `threading.Timer` tạo trong `action_block_ip` (`hephaestus/main.py:375-378`) → `_sync_expire_network_policy` (`:396-408`) | Xóa đúng policy đó sau `NETWORK_POLICY_TTL_SEC` (mặc định 300s) | Timer chỉ trong bộ nhớ; mất nếu Hephaestus khởi động lại |

**Ghi nhận đính chính.** Ban đầu E3-C03 ghi runner direct không có lệnh xóa NetworkPolicy. Codex đã kiểm lại, xác nhận dòng `:143-147` và sửa E3-C03. Báo cáo blockers phần Codex cũng ghi đính chính này. Tôi đồng ý với bản đã sửa: có ba đường riêng, không gộp làm một.

**Kết luận mới — pod stress.** `cpu_stress.go:124-130` **có nhánh thử xóa** pod stress. Khi xóa lỗi, executor chỉ ghi warning rồi vẫn đặt `SUCCESS` (`:134`). Nên viết "có nhánh thử cleanup", chưa viết "cleanup được bảo đảm".

**Chưa chứng minh.**
- Lệnh xóa của runner có thành công trên lab cũ không: UNKNOWN, không có log return code.
- INFERENCE cần kiểm tra: lệnh xóa pod stress dùng lại `ctx` (`cpu_stress.go:125`). Nếu vòng chờ ở `:119-122` kết thúc vì `ctx` đã hết hạn, lệnh xóa có thể thất bại vì cùng context đó. Cần đọc log hoặc thử trong một task sửa mã.
- Số pod stress hoặc policy còn sót trên lab hiện tại: UNKNOWN cho tới khi có inventory.

## C04 — Phạm vi đã đọc: DOCX, GitNexus, lịch sử dữ liệu

### C04a. DOCX thuyết minh

**Kết luận cũ bị thay thế.** D1 ghi DOCX "CHƯA ĐỌC… lượt này không mở/convert tài liệu ngoài". Bảng D1 ghi "Không (ngoài repo, ngoài phạm vi lượt này)". D5 ghi "Cần Hoàng xác nhận/đưa hồ sơ". Lý do "ngoài phạm vi" là sai, vì C1 cho phép đọc DOCX nếu truy cập được. Cũng không cần xin Hoàng cung cấp lại tài liệu.

**Thực tế đã xảy ra.**
- Ở lượt D8 đầu tiên, tôi đã thử đọc DOCX bằng một script Python chỉ đọc, ghi ra scratchpad. Lệnh bị bộ phân loại quyền chặn với lý do `[PII Data Handling]` (ghi tại B02 của báo cáo blockers).
- Theo hướng dẫn của Codex, lượt này không thử lại và không quét Downloads.

**Nguồn dùng thay.** Đối chiếu trích xuất do Codex đọc trực tiếp; tôi chưa trực tiếp đọc DOCX. Nguồn: `docs/handoff/2026-10-17-registration-requirements-excerpt.md`, có SHA-256 của DOCX và vị trí đoạn Pn. Nhãn: HISTORICAL_EVIDENCE thứ cấp, không phải SOURCE_VERIFIED của phiên Claude.

**Đối chiếu với Q01 cũ.**
- **Khớp:** ≥5 microservices (P104); ba loại tấn công SQLi, DDoS tầng ứng dụng, Resource Exhaustion (P105); Scale up/down, Block IP, Rollback (P106); MTTD <1 phút, MTTR <2–3 phút (P107); uptime ≥99,9% dưới tấn công liên tục (P108); thời gian 6 tháng, 01–06/2026 (P55–P56); ngày ghi trên văn bản 04/01/2026 (P35); Java Spring Boot ở danh mục sản phẩm (P208), đã được thay bằng Python/Go theo xác nhận của Hoàng.
- **Q01 cũ còn thiếu, nay bổ sung:**
  - Mục tiêu tổng quát gồm "cô lập mối nguy" và tự phục hồi "mà không cần con người can thiệp" (P100).
  - Dashboard hiển thị Attack vs Defense theo thời gian thực (P109).
  - Tích hợp LLM để sinh kịch bản tấn công (P176). Mã Nemesis có đường tích hợp cho việc này; vận hành thật vẫn UNKNOWN (Q06).
  - KPI tiến độ: CPU target app tăng >80% (P179). Điều này nối trực tiếp với Q04 và F06: pod stress riêng chưa chứng minh được CPU của chính app tăng.
  - Thời gian phản ứng <1 phút (P187).
  - Sản phẩm: video demo, bảng MTTR/MTTD, báo cáo, slide, poster (P193, P195, P198–P203, P210–P211).
- Ngày ở P35 không chứng minh ngày ký, nộp hay duyệt. Khác biệt giữa 01–06/2026 và hạn 31/12/2026 do Hoàng xác nhận vẫn là khoảng trống hồ sơ; không tự kết luận có hay không có gia hạn.

### C04b. GitNexus

**Kết luận cũ bị thay thế.** D1 ghi "KHÔNG dùng được… không chạy CLI (lượt hydration cấm…)". D7 ghi "không dùng GitNexus (không khả dụng)". Cả hai sai: lượt hydration không cấm CLI chỉ đọc.

**Thực tế (LIVE_READ_ONLY, 17/10).**
- MCP resource `gitnexus://` không có trong bộ công cụ của phiên Claude.
- CLI có tại `/c/Program Files/nodejs/gitnexus`, bản 1.6.11.
- `gitnexus query "block ip network policy" -r zero_door --limit 3` chạy được, exit 0.
- `gitnexus context "action_block_ip" … --file agent-orchestrator/hephaestus/main.py` trả `found`, dòng 323-393, caller `process_alert`. Kết quả khớp source.
- `gitnexus status` hết thời gian chờ 60s (exit 143). Codex đã khoanh được một bước chậm; không dùng `status` làm điều kiện bắt buộc.

**Freshness (LIVE_READ_ONLY, 18:01).** `.gitnexus/meta.json` ghi `lastCommit` = `6337b319…`, `indexedAt` = `2026-10-09T02:00:34Z`; HEAD là `f9623a3`. `git diff --name-only 6337b31 HEAD` chỉ gồm `.gitignore`, `.gitnexusrc`, `AGENTS.md` và tài liệu trong `docs/handoff`, `docs/plans`, `docs/reviews`, `docs/runbooks`. Không có mã agent/worker/runner trong diff, nên graph dùng được để định vị; kết luận vẫn dựa trên source.

### C04c. Lịch sử dữ liệu thực nghiệm

**Kết luận cũ bị thay thế.**
- Dòng D7 ghi lệnh là `git log --oneline -- docs/experiments/raw_data`. Lệnh đó không in ngày. Lệnh tôi thực sự chạy có `--format='%h %ad %s' --date=short`, nên D7 ghi sai lệnh.
- Q07 ghi provenance bằng một commit duy nhất (`a179aad`). Như vậy là chưa đủ.

**Kết luận mới.** Ghi tách ba loại ngày (LIVE_READ_ONLY, `git log --date=iso-strict --name-status`, 17:08 và 18:01):

| Loại ngày | Giá trị | Nguồn |
| --- | --- | --- |
| Ngày trong dữ liệu (`attack_start`) | 2026-06-25, 15:30–15:54 UTC (22:30–22:54 giờ Việt Nam); 8 file, mỗi file 5 dòng | Cột `attack_start` của 8 CSV trong `docs/experiments/raw_data/` |
| Ngày commit đưa dữ liệu vào | `a179aad` 2026-06-25T22:55:38+07:00 thêm 8 CSV và `analysis/summary_statistics.csv` | `git log` |
| Ngày chỉnh inventory | `54ff513` 2026-07-12T20:19:45+07:00 thêm `e2_http_flood/results_20260712T100633.csv`; `0b402e4` 2026-07-13T13:13:24+07:00 xóa lại file đó | `git log --name-status` |

- `summary_statistics.csv` chỉ có một commit (`a179aad`). Session memory kể đã chạy lại `analysis.py` vào tháng 7. INFERENCE: nếu có chạy lại, output trùng bản tháng 6 nên Git không ghi thay đổi. Chưa có log chứng minh lần chạy lại.
- Timestamp trong CSV do runner ghi bằng đồng hồ máy. Đó không phải bằng chứng độc lập về thời điểm chạy. Tôi chưa thấy log gốc của lượt chạy, chỉ có CSV và commit.

## C05 — Phạm vi file không giao nhau và phụ thuộc

**Kết luận cũ bị thay thế.**
- Q10 giao "Claude → `agent-orchestrator/*`", trong khi D6 việc 2 giao `nemesis/static/app.js` cho Codex. Hai phạm vi chồng nhau, vì `app.js` nằm trong `agent-orchestrator/`.
- D6 việc 1 ghi "Hoàng chạy (chạm máy/credential)", như thể mọi lệnh lab đều phải do Hoàng gõ.
- D6 việc 2 và 3 phụ thuộc #1, tức là bắt thiết kế R1 chờ lab và LLM chạy thật.
- Cột ước lượng 3h/4h/5h có thể bị đọc như tổng công sức hoặc bằng chứng kịp cuối tháng.

**Kết luận mới — quy tắc (đề xuất, chưa phải phân công đã chốt).**
1. Mỗi task có **allowlist theo đường dẫn file cụ thể**, không giao cả thư mục. Trong một task, mỗi file chỉ có một owner. Task ghi rõ owner, base HEAD, đầu ra, người review và điều kiện đóng.
2. **Khóa event schema trước khi sửa producer hay consumer.** Schema gồm tên field, ý nghĩa, nguồn ghi mốc thời gian, terminal status (tách API_ACCEPTED, ACTION_COMPLETED, RECOVERY_VERIFIED, FAILED, TIMEOUT, SKIPPED) và công thức MTTD/MTTR. Bên còn lại review và đồng ý thì mới mở task sửa mã.
3. **Thiết kế tách khỏi bằng chứng runtime.** Thiết kế contract, kiểm nguồn và viết test đơn vị không cần lab hay LLM. Chỉ tích hợp và bằng chứng runtime mới chờ inventory lab và backend LLM.
4. **Quyết định của Hoàng khác với thao tác.** Agent có thể chạy lệnh chỉ đọc hoặc lệnh đã được duyệt khi phiên có quyền. Hoàng quyết định: đăng nhập và credential, chọn provider/model, chi phí, và các thao tác thay đổi hoặc xóa cluster. Không ghi secret vào file bàn giao.
5. Giờ ước lượng ở D6 chỉ là **giả định giờ tương tác của Hoàng**, không phải tổng công sức hay lịch đã xác nhận. Lập lại lịch sau inventory và khi đã phân rã task.

**Đề xuất thứ tự và allowlist (để Hoàng và Codex chọn; chưa tự nhận việc).**

| Task | Phụ thuộc | Allowlist ghi | Owner đề xuất / review | Đầu ra và điều kiện đóng |
| --- | --- | --- | --- | --- |
| T1 — Inventory lab chỉ đọc (R0-T02-S01) | Không; cần Hoàng cho phép chạy lệnh đọc Docker/K8s trong phiên | File mới `docs/evidence/R0-T02-S01/inventory-<ngày>.md` (thư mục chưa có; roadmap dòng 204 đề xuất) | Phiên nào có quyền chạy lệnh / bên còn lại review | Lệnh, timestamp, kết quả hoặc lỗi rõ; có phiên bản và args K3s cho C01; không start, recreate hay xóa gì |
| T2 — Bản nháp event contract R1 (R1-T01-S01) | Không; song song với T1 | File mới `docs/design/r1-event-contract.md` (thư mục chưa có) | Claude / Codex | Schema, ví dụ, công thức metric, quy ước ID xuyên suốt; liệt kê endpoint dashboard đang đọc (`/api/status`, `/api/logs`, `/api/chat`, `/api/heal-history`, `/api/reset` trong `static/app.js:98-610`). Đóng khi Codex và Hoàng duyệt |
| T3a — Producer/consumer phía agent và worker | T2 đã khóa | `agent-orchestrator/gaia/main.py`, `agent-orchestrator/hephaestus/main.py`, `agent-orchestrator/nemesis/main.py`, `chaos-worker/internal/attack/executor.go`, `chaos-worker/cmd/main.go`, kèm file test mới tương ứng | Claude / Codex | ID truyền qua Kafka và HTTP; status tách đúng; test đơn vị pass. Chưa coi là bằng chứng runtime |
| T3b — Đo đạc và hiển thị | T2 đã khóa; chạy song song với T3a vì không chung file | `infrastructure/scripts/experiment_runner_direct.py`, `infrastructure/scripts/analysis.py`, `agent-orchestrator/nemesis/static/app.js`, script probe mới | Codex / Claude | Tính lại KPI từ raw event; bỏ số ngẫu nhiên và fallback; dashboard dùng chung nguồn với analysis |
| T4 — Bằng chứng tích hợp | T1, T3a, T3b; backend LLM nếu đo nhánh AI | Chỉ thư mục evidence của task | Theo phân công khi đó | Một sự cố có ID xuyên suốt, probe xác nhận; ghi cả lượt thất bại |

Ghi chú: ở T3a và T3b, `nemesis/main.py` (API) và `static/app.js` (UI) có owner khác nhau. Hai bên ràng buộc qua contract của T2, không qua việc cùng sửa một file. Nếu contract phải đổi giữa chừng, owner T2 cập nhật và bàn giao trước khi bên kia sửa tiếp.

**Chưa chứng minh.** Quỹ giờ thật của Hoàng sau 17/10 chưa được xác nhận (phần B). Các task T1–T4 chưa được giao; file này không phải quyết định phân công.

## Trạng thái hoàn thành

Đã điền cả năm mục C01–C05; mỗi mục được lưu rồi đọc lại trước khi sang mục sau. Hydration gốc, báo cáo blockers, bản trích DOCX và mã ứng dụng không bị sửa (đối chiếu SHA-256 trước và sau ở cuối lượt). Chưa chạy lab, endpoint gây tác động, LLM, build/deploy; chưa commit/push. File này cần Codex review trước khi cập nhật điểm hoặc giao task triển khai.
