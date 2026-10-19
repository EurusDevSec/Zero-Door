# ZER-9 fix-01 — kế hoạch kiểm runtime trên chính actor (chưa chạy)

Claude, 19/10/2026. Đây là checklist để Codex chuẩn bị phạm vi và xin quyền; **không phải bằng chứng** và chưa được chạy. Gói fix-01 chỉ sửa và kiểm offline. Lượt live-11 không thay được phép kiểm này: hai agent chạy trong process verifier trên host qua port-forward, và cổng quyền chỉ đo pod observer (ZR9-05). Hoàng quyết AC-02/03 có cần phép kiểm này trước Done, hay chấp nhận profile transport và ghi phạm vi.

## Điều kiện trước khi chạy

- Quyền vận hành riêng cho lượt này: namespace/topic/PVC tạm mới, image build, rule ES tạm nếu cần. Quyền live-11 của Codex không tự chuyển sang lượt này.
- Revision cuối đã qua Codex retest offline. Image build từ Dockerfile production của revision đó (CI `r1-image-build` hoặc build local có ghi digest), không dùng image COPY-only cũ.
- Node `k3d-zero-door-server-0` còn chỗ. Pod Pending hoặc gate fail thì **dừng trước data**, không tự bỏ nodeSelector hay fallback sang node agent (ZR9-06).

## Thứ tự và kiểm

1. **Recorder.** Áp template với probe `httpGet /readyz` và `/livez`. Ghi trạng thái NOT_READY khi bridge còn đuổi offset lúc khởi động. Nếu Hoàng muốn receipt runtime cho ZR9-01, gửi một message rác lên topic tạm của nonce, kiểm recorder vẫn Ready, offset tăng và `rejections.jsonl` gốc có bản ghi.
2. **Secret theo actor.** Tạo `event-o-gaia` {detector, reader}, `event-o-hephaestus` {decision_rules, reader}, `event-o-observer` {reader}. Không có Secret chung. Kiểm mount thật trong từng pod chỉ có đúng file của nó.
3. **Policy cho actor.** Template hiện chỉ cho `role: observer` cùng namespace vào events-o. Cần thêm rule ingress/egress cụ thể cho label của pod Gaia/Hephaestus, review trước khi áp. Không mở broker, telemetry trực tiếp, H, hay Kube API cho actor.
4. **Gate trước request đầu tiên của chính actor.** Chạy cùng cổng ba vòng liên tiếp (trần 40) **trong pod actor**, hoặc init container cùng label/policy/node: O API 200; H, Kafka, Elasticsearch, Prometheus trực tiếp bị chặn. Không có token Kube; `/raw-*` không mount. Actor chỉ khởi động producer sau khi gate đạt; lưu mọi vòng còn mở.
5. **Quyền âm/dương trên actor.** Token Gaia không ghi được DECISION; token Hephaestus không ghi được DETECTED; cả hai không gọi được `/seal`; reader không POST được. Hephaestus `/heal/trigger` và `/experiment/reset` trả 409 khi R1 bật.
6. **Telemetry thật qua actor.** Gaia gọi Prometheus và Elasticsearch bằng client thật của nó qua proxy (`/prometheus`, `/elasticsearch`). Lưu query/kết quả làm surface audit. Đường ES client đã kiểm offline với upstream giả; runtime cần kiểm thêm.
7. **Transport → raw → seal/export.** Gửi DETECTED thật từ pod Gaia (payload SYNTHETIC ghi rõ), DECISION thật từ pod Hephaestus, gửi lại đúng envelope và restart recorder. Dùng `/seal` có xử lý 409, export mới có `export.json`, đối chiếu hash PVC/export.
8. **Audit.** HARNESS_MANIFEST khai mọi giá trị harness tạo ra: namespace, topic, image, pod, PVC, Secret, header. Đối chứng nhãn ở stream/target với ID hợp lệ phải ra LABEL_IN_METADATA; trace sạch phải CLEAN. Nhãn synthetic chỉ dùng trong RAM.
9. **Dọn.** Theo thứ tự hiện có: dừng recorder rồi xóa topic, xác minh UID/nonce, read-back.

Không cần phát fault, heal hay LLM để chứng minh vận chuyển. Không sửa CNI/node agent/broker/policy toàn cluster trong ZER-9. Profile server-node vẫn chỉ chứng minh đúng node đã kiểm, không chứng minh cluster an toàn.
