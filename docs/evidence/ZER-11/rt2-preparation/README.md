# ZER-11/39 — RT2 đã chuẩn bị, chưa chạy lab

Verdict: **READY_FOR_SCOPED_RT2_REVIEW**. [Phạm vi và thứ tự thực hiện](../../../runbooks/dashboard-and-baselines.md#6-g-zer11-rt2--gói-kiểm-manualrules-trên-image-production). Quyền hiện có chỉ là chuẩn bị/kiểm offline; chưa build/import, chưa ghi cluster, chưa CI/publication/Linear hoặc Done.

## Gói cụ thể

- [Tool RT2](../../../../infrastructure/scripts/r1_mode_runtime.py) tạo bundle mới với context/Secret riêng, source-digest image tag, manifest và source attest; không gọi Docker/kubectl. Trong pod, nó giữ gateway O production, observer HTTP và control endpoint loopback. Actor là pod khác, giữ nguyên ENTRYPOINT Uvicorn/source Hephaestus.
- [Bash entrypoint](../../../../infrastructure/scripts/verify-dashboard-modes.sh), [test](../../../../tests/test_dashboard_mode_runtime.py); thêm test vào cả hai job Python production lock của CI, chưa chạy CI từ xa.
- BM dùng lỗi GET thật từ observer phiên bản rt2-http-availability/1; không giả danh Gaia. B1/B2/B3 synthetic transport control ở ba run khác. Console CLI chỉ có O/operator keys; không có H/archive/attack key hoặc SA token. Không claim BM có người vận hành mù.
- Không sửa source Hephaestus, command guard, scorer, event_pipeline hoặc harness RT1. [Hash nguồn và kết quả](verification.json).

## Kiểm đã chạy

- **3/3 test trên từng pin Nemesis và Hephaestus**: render bundle/credential projection/entrypoint/source; từ chối namespace hoặc thư mục cũ; luồng thật qua 4 tiến trình Uvicorn và O gateway. BM không tự quyết, MANUAL hợp lệ nhận HTTP409 và audit; token sai401; B1 đúng một RULES sau nhiều poll; B2/B3 không có quyết định/action/LLM.
- Những kết quả này là **PASS_BOUNDARY_OFFLINE**, HTTP quan sát được tiêm vào diagnostic observer. Counterexample loại mất lỗi thật, thiếu RULES, có HEAL_STARTED, thiếu audit, guard trả200 và cửa sổ runtime chưa đủ đều bị bắt.
- Hồi quy mode cũ **7/7**, Bandit0, Bash syntax/help/plan đạt, diff whitespace sạch. Hai cảnh báo Bandit ban đầu là đường dẫn file token và bind cổng O có auth/namespace ingress; có chú thích cụ thể. Log cũ giữ nguyên trong reproduction.zip.
- Chạy lại suite khi source đổi để sửa provenance observer và thêm điều kiện cửa sổ; không dùng lượt offline làm bằng chứng image/cluster. [Log, receipt đã bỏ khóa và snapshot](reproduction.zip).

## Quyền cần cho bước kế

Một lượt tối đa **45 phút từ trước build/import, gồm5phút cleanup** trên k3d-zero-door: build/import một image Hephaestus; một namespace tạm có6pod và tài nguyên bundle; tạm scale Gaia/Hephaestus0; xóa đúng một pod frontend theo UID; tối đa360GET trong cửa sổ180s; thu log/raw O, xóa tài nguyên của run và trả đúng replicas/spec/UID baseline. Không HPA, không đổi quota/target replicas, không LLM/API trả phí. Lỗi/thiếu cửa sổ/không quan sát được lỗi thật thì INCOMPLETE, không thêm lần xóa pod để tìm PASS.

RT2 chưa chạy nên image, filesystem/NetworkPolicy thật, HTTP outage và cleanup còn chưa xác minh. Sau runtime vẫn cần review, CI/merge và Hoàng nghiệm thu trước Done; RT1 và giới hạn quota của nó giữ nguyên. Gói này không tự khép G1.
