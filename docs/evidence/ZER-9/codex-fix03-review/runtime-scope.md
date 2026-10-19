# ZER-9 — phạm vi lượt runtime sau fix-03 (đề xuất, chưa được phép chạy)

Nguồn cuối đã qua [Codex retest](README.md); HEAD2af4d33 và hash source theo [delta fix-03](../fix-03/delta-manifest.json). Không sửa hay thay thế [kế hoạch lịch sử](../fix-01/runtime-plan.md). Trang này là phạm vi để Hoàng duyệt, không phải receipt hoặc quyền triển khai. Writer Codex; Claude chỉ nhận review khi Hoàng giao.

## Kết quả cần lấy

Một receipt mới trên source cuối chứng minh AC-02/03 trong profile transport: code Gaia và Hephaestus thực sự chạy trong pod riêng từ image production, chỉ có key đúng vai trò và truy cập được O qua HTTP. Chuỗi ID qua Kafka vào raw PVC, poison/quarantine không khóa recorder, restart giữ dữ liệu, seal/export có hash; audit sạch và đối chứng rò hợp lệ. Synthetic DETECTED phải ghi rõ là fixture vận chuyển, không kết luận phát hiện fault/KPI/LLM/healing.

## File/action scope đề nghị

- Chuẩn bị verifier actor riêng trong infrastructure/scripts/verify-event-actors.py và .sh, manifest overlay riêng infrastructure/manifests/r1-event-actors.yaml, test offline tests/test_event_actor_verifier.py; runbook/verification, thư mục evidence lượt mới và scratch riêng; append issue note, prepend NOW. Không sửa receipt/probe/review cũ, contract, agent logic hay kho raw lịch sử. Nếu source sản phẩm cần sửa thêm do runtime, ghi finding và scope trước, không tự đổi contract hoặc điều kiện PASS.
- Docker context desktop-linux, Kubernetes context k3d-zero-door được kiểm rõ. Đọc tình trạng/tài nguyên/node/policy/namespace trước build. Metrics API thiếu hoặc node memory trên80% thì dừng như guard cũ; thiếu chỗ trên server thì dừng, không fallback node agent.
- Build cục bộ ba image từ Dockerfile production events/Gaia/Hephaestus, tag zer-9 kèm nonce, ghi source hash và image ID/digest; import chỉ vào cluster zero-door. Có thể tải base/dependency đã pin của Dockerfile nếu chưa cache; không cài dependency lên host, không push registry hay thay image workload hiện hữu. Không dùng COPY-only image của live-11.
- Tạo duy nhất namespace mới zd-zer9-<nonce>, topic zd.events.o.<nonce> một partition + consumer group riêng, hai PVC raw-h/raw-o64Mi (tổng128Mi), ServiceAccount không token tự mount, Secret riêng gateway/actor/observer, ConfigMap query và policy chỉ trong namespace này. Không đổi topic/group/PVC/workload cũ.
- Tối đa5pod đồng thời: hai recorder, Gaia, Hephaestus và observer/probe; cleanup pod ngắn hạn thay một pod đã dừng. Requests tổng tối đa110m CPU/208Mi; limits tổng tối đa900m/800Mi. Đây là trần pod, không phải cam kết peak bộ nhớ của Docker build. Dùng server node k3d-zero-door-server-0 cho tất cả, không thêm node hay sửa CNI/firewall.
- Ngoại lệ ngoài namespace mới duy nhất: nếu ES cần, tạo một NetworkPolicy mới có nonce trong monitoring, chọn đúng ES pod, chỉ cho namespace nonce VÀ pod events-o tới TCP9200; không sửa rule cũ. Ghi UID và xóa đúng rule này cuối lượt. Không mở Gaia/Hephaestus tới ES/Prometheus/Kafka/H/Kube API trực tiếp.
- Có thể dùng port-forward loopback do verifier sở hữu cho harness/evaluator điều phối H/O; producer và consumer đang được chứng minh phải chạy trong pod riêng. Không đưa server/harness/evaluator key hay raw PVC vào actor. Token tạm ở private local output, không commit hoặc in log.
- Một phiên tối đa2giờ tính từ bắt đầu vận hành; timeout/gate lỗi dừng, không chạy lặp vô hạn. Không gọi model/API trả phí hoặc Doppler; không phát fault/heal/reset và không sửa tài nguyên ứng dụng đích.

## Trình tự và điều kiện dừng

1. Verifier/overlay kiểm offline trước; ghi hash scope/baseline và preflight. Không áp overlay vào namespace đã có.
2. Policy mặc định deny; thêm đúng rule cho actor vào O và DNS. Init gate trong từng pod actor (cùng labels/node/network) phải có3vòng liên tiếp O200, H/Kafka/ES/Prometheus trực tiếp bị chặn, tối đa40vòng; không khởi động producer/consumer trước gate. Lưu cả vòng hở. Không coi YAML, sleep hoặc observer là bằng chứng quyền actor.
3. Kiểm mounted key thực tế, không token Kube, không raw; Gaia không ghi DECISION, Hephaestus không ghi DETECTED, reader không POST, actor không seal. Hephaestus heal/trigger và experiment/reset trả409 trong R1; không thực thi nhánh legacy.
4. Gaia dùng client thật gọi Prometheus/ES qua O gateway, query/kết quả có surface audit; tối đa3lượt query, không thay query hoặc giá trị để làm xanh. Nếu guard/policy không đạt thì không tạo event trial.
5. Seed context trung tính qua harness, một synthetic DETECTED từ pod Gaia, một DECISION RULES từ pod Hephaestus; duplicate giữ envelope. Gửi poison trên topic riêng từ harness kiểm quarantine/hash/commit rồi good event tiếp. Restart recorder O có kiểm readiness và offsets; seal có tối đa timeout hữu hạn. Không cố gây lỗi đĩa/PVC thật hoặc phá raw để kiểm FX02.
6. Dừng writer trước evaluator export; đọc PVC bằng evaluator đúng quyền, output đích mới, export.json + checksum từng file + source digest + actor execution. Audit CLEAN phải có manifest/prompt/query và bằng chứng access đủ; đối chứng nhãn trong target/stream dùng ID hợp lệ phải ra LABEL_IN_METADATA. Thiếu bằng chứng là UNKNOWN, không làm đẹp verdict.
7. Sau receipt/export đạt và đã đối chiếu UID/nonce: dừng recorder O trước khi xóa topic để tránh auto-create; xác nhận topic vắng, xóa đúng namespace/PVC tạm và ES rule nonce. Dừng chỉ các port-forward của lượt này. Không dùng wildcard/prune hoặc xóa image/volume hiện hữu. Nếu FAIL, giữ output và tài nguyên tạm để chẩn đoán, báo chính xác còn gì; không tự lặp hoặc xóa evidence để thử lại.

## Quyền còn tách riêng

Duyệt trang này chỉ cấp chuẩn bị + chạy + cleanup lượt runtime được mô tả. Không stage/commit/push/PR/merge/Linear hoặc gửi tin Claude; publication/CI/merge/Hoàng chấp nhận cần căn cứ quyền tương ứng. Source hay placement khác sau lượt này làm receipt phải được đánh giá lại; không suy actor isolation toàn cluster, uptime nghiên cứu hay G1 từ transport PASS.
