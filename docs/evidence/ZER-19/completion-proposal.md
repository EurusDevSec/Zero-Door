# ZER-19 — gói xác minh chức năng và publication có điều kiện

PREPARED / NOT_APPROVED / NOT_RUN. Hoàng đã giao thực hiện ZER-19; quyền inference/lab/publication của ZER-48 đã dùng hết. Chưa có tài nguyên hay provider call nào của gói này được chạy.

## Kết quả cần chốt

AC01 dùng lại ZER-48/PR34; AC02 cần một chuỗi thật observation → Nemesis/shared adapter → ID template hợp lệ → signed existing Go executor → result khớp command; AC03 cần phiên tự dừng đúng max rounds/calls, trace stop/cancel và usage. Offline đã review READY:54 lượt focused trên hai pin +78 regression,37 kiểm Bash; cancellation được kiểm với transport/Kafka giả. Không dùng mock để tuyên bố đã có chuỗi runtime.

## Nguồn và cấu hình đã chuẩn bị

Branch codex/zer-19-nemesis-session, HEAD/base093e924000861da3096185427994d9ea736df36d. Chín source/CI paths trong source-hashes.json phải giữ nguyên; nếu sửa lỗi runtime phải review/retest delta trước tác động tiếp. runtime-config.json và runtime-rendered-disabled.yaml đã render offline từ renderer ZER-42, chưa apply. config_ref trỏ SHA256 scope.json. B2 trong local LLM_CALL envelope chỉ tương thích schema; purpose FUNCTIONAL_ONLY_NOT_BENCHMARK và benchmark_eligible=false. Không ghi vào dataset/recorder formal và không mở endpoint benchmark /attack/llm-plan.

Manifest ban đầu giữ executor và SQLi capability DISABLED, fixture safe;4 workloads riêng (fixture, proxy, worker, Nemesis), bỏ2 source Pod thừa. Dùng đúng4 image lịch sử trong runtime-images.json; verify digest/content cache cả Docker/node trước khi apply. Không tự rebuild/reimport/pull khi thiếu cache. Source session/adapter được mount read-only bằng ConfigMap, không sửa image cache. API key lấy từ cấu hình Doppler hiện có, chỉ truyền stdin tới Secret tạm zer19-provider, không argv/log/artifact; hai signing/operator key tạm khác nhau. Xóa cả ba cùng namespace khi cleanup.

## Một lượt duy nhất, trần hành động

- Chỉ Docker desktop-linux/Kubernetes k3d-zero-door; namespace zd-sqli-lab phải absent trước bắt đầu. Tạo đúng namespace đó,4 workloads trên k3d-zero-door-agent-0 và các Service/ConfigMap/NetworkPolicy tường minh trong manifest. Không shared workload restart, DNS/CNI/resource/Prometheus/WSL/RBAC/PVC change. Không build/import/pull; không đóng app hoặc kill tiến trình khác.
- Tối đa20 phút gồm5 phút cleanup cuối; bắt đầu attempt marker trước mutation,0 tự retry nếu fail. Preflight120s với host/WSL available ≥1GiB, memory PSI some avg10≤5; giữ guard trong cửa sổ. Guard/cache/identity/readiness lệch thì dừng; không recovery mới hay nới ngưỡng.
- Giữ policy-release gate fixture: đối chiếu Pod UID/IP/node và kube-router hook trước bind; pin private ingress Service IP cho worker và proxy IP trusted/32 cho fixture. Chỉ sau baseline thành công mới bật private policy đúng maxSends=1/maxCommandSec=1. Không bật/sửa policy shared.
- Đúng1 OpenAI gpt-6-luna Responses call qua adapter đã review,0 retry,≤256 output token; attempt20s/call25s/session120s. Max calls1, reserved tokens9472, reservation estimate ≤0.005 USD; đây là estimate ứng dụng, không billing hard cap. Chỉ gửi health O projection trung tính; không raw result/H oracle/seed/payload vào model.
- Chỉ cho chọn benign-apparel hoặc STOP; không injection mới, payload mới, vector/target mới. Nếu chọn STOP hoặc output/usage/schema/evidence không hợp lệ thì giữ kết quả đó,0 executor dispatch, không cố gọi lại để lấy PASS.
- Tối đa1 signed SQLI command, template benign-apparel đã có trong registry; duration1s,maxSends1,concurrency1,≤1RPS. Policy/URL/namespace/service không do model quyết định. Không dùng disclosure template trong lượt chức năng này; effect SQLi đã có ở ZER-13, gói này xác minh đường điều phối.
- Tổng≤3 fixture HTTP lành (baseline1 +executor1 +post1), concurrency1/≤1RPS;≤1 TCP denial control. Không Boutique workload/observer/healing vì không thuộc outcome Nemesis này; không suy KPI/G3/G4/end-to-end.
- Chỉ tạo/đọc/xóa đúng2 topic `e0e0aea10613` theo tên đầy đủ trong protocol dưới; xác minh absent trước tạo, không tác động attack.commands/results formal. Một worker consumer group riêng. Worker/Nemesis Pod có activeDeadlineSeconds900. Không gửi lại nếu ack/result UNKNOWN; ledger giữ claim.

## Protocol và điều kiện kết luận

1. Snapshot shared spec/UID/restart và3PVC cùng cache identity; source/config/manifest hashes khớp. Namespace/topic pair đều absent; RAM/PSI/preflight đạt. Khóa attempt duy nhất và deadline20 phút, cleanup reserve5 phút.
2. Apply manifest disabled theo thứ tự namespace/config/policy → proxy → gated fixture, rồi pin ingress/proxy và kiểm policy hook; tạo hai topic riêng và ba Secret tạm. Start worker/Nemesis tuần tự. Chưa inference hay dispatch trong setup. Giữ thực tế stdout/error đã che bí mật; không phát lại API create bất định.
3. Một TCP denial control direct fixture phải bị chặn. Một GET catalog/search category apparel qua proxy từ Nemesis phải200. Tạo observation observed_at thật/evidence ev-health-01 từ response này, ghi raw/hash riêng; thiếu/muộn quá60s thì dừng trước model. Bật private policy với đúng context/config; shared policy giữ nguyên.
4. Chạy đúng một CLI module nemesis.session_cli --live với config đã khóa và observation mới, output parent /ledger. Mount source/adapter đúng pins, provider key chỉ qua Secret env. CLI mkdir run directory exclusive chặn replay; giữ started/events.jsonl/receipt. Đọc kết quả đã join từ topic riêng và log worker/fixture/proxy; trace must show1 real provider attempt, valid usage and proposal. Chỉ1 admitted command/1send/200/source-IP join; acknowledgement không thay kết quả. Nếu STOP/failure/UNKNOWN thì NOT_MET, không call/dispatch thêm.
5. Session tự kết thúc MAX_ROUNDS với completed_rounds1/calls1; timestamp, prompt/model/config pins và command/result match. Capture CLI exit/owned processes. Post GET lành200; không chấm effect hoặc recovery từ receipt SUCCESS.
6. Cleanup trước deadline: stop/delete owned consumers, thu receipt/log và đợi owned Pod/process kết thúc; UID-delete namespace và xác minh absent; sau đó delete đúng topic pair và list xác nhận absent. Không delete theo prefix rộng, không xóa namespace có UID/owner khác. Đọc lại shared snapshot/3PVC unchanged, không credential/copy source tạm còn lại. Thiếu cleanup/identity/guard evidence chặn technical PASS.

Topic commands: zer19-e0e0aea10613.commands; results: zer19-e0e0aea10613.results. Legacy zer42-* workload names chỉ do tái dùng renderer; toàn bộ owned namespace mới có UID/run label riêng. Không chạy nguyên runner ZER-42 (nó có build và bốn case ngoài gói này).

Nếu đạt: independent review đối chiếu raw/source/config; chỉ sau đó scoped commit/push/PR, CI gồm image import, review/merge và Hoàng conditional acceptance mới chuyển Done. Nếu fail: cleanup rồi khép blocker/phần đạt/chưa đạt và số request thực; không tự attempt02, không bỏ failure hoặc mở issue khác.

## Quyền cần duyệt một lần

Duyệt toàn bộ envelope trên:1 private functional attempt/1 model call và scoped publication có điều kiện; không phải quyền thử không giới hạn. Runtime preparation/check helpers nếu cần chỉ phục vụ protocol này, phải kiểm offline và khóa trước first mutation, không là lý do tự tăng envelope. Không có approval file nào được tạo trước khi Hoàng trả lời.
