# ZER-9 — kiểm actor thật trên source cuối

**Runtime PASS10/10, đối chiếu độc lập68/68.** Chạy19/10/2026,19:56:14–20:03:46 +07:00 (12:56:14–13:03:46UTC), trên desktop-linux / k3d-zero-door. Hoàng duyệt gói runtime và yêu cầu hoàn tất commit/PR/Linear; writer Codex. Baseline2af4d33; receipt ghi hash source thật, image và UID. CI/merge được ghi riêng khi publication hoàn tất.

| AC | Bằng chứng | Kết quả |
| --- | --- | --- |
| AC-01 | Contract zd-event/1.0.0 đã khóa ở ZER-37; schema/nguồn/timestamp riêng; không sửa contract trong lượt này | PASS kế thừa và regression |
| AC-02 | Gaia production trong pod → HTTP → Kafka → PVC O → consumer Hephaestus production trong pod; cùng run/trial/incident/causation; redelivery, poison, good-next, restart, seal/late/export | PASS runtime |
| AC-03 | Init gate trong từng actor, Secret đúng vai trò, không token/PVC; query Prom/ES qua O; H canary không vào O; CLEAN + nhãn ở target/stream với ID hợp lệ bị bắt | PASS runtime + audit |

[Receipt nguyên bản](receipt.json), [overlay đã render](rendered.yaml), [raw O](export/O/O.jsonl), [raw H](export/H/H.jsonl), [đối chiếu độc lập](reconcile.json). Lệnh tái kiểm chỉ đọc:

```bash
python -B docs/evidence/ZER-9/actor-runtime/reconcile.py
```

Gaia gọi query/publish production trong pod; lifecycle polling tắt để chỉ phát fixture transport bounded. Hephaestus dùng startup/consumer R1 thật. Alert HIGH_CPU là synthetic; không tạo tác động workload, không heal/reset/LLM, không kết luận KPI/phát hiện/phục hồi/G1. Một DECISION RULES nối đúng DETECTED; ba ingest DETECTED giữ nguyên envelope. Poison ở offset5 được giữ bytes/hash trong quarantine, good-next ở offset6 được ghi, group commit7; restart không lặp poison hoặc đổi raw. Hai writer dừng trước evaluator mở PVC và gọi Archive.export; toàn bộ file export, quarantine và late có hash.

Hai actor có sáu vòng gate: ba vòng đầu policy còn hội tụ (giữ nguyên trong receipt), ba vòng cuối O200 và mọi đường trực tiếp H/broker/telemetry bị chặn. Chưa đưa trial vào trước gate. Do giới hạn firewall theo node đã biết, tất cả pod được khóa server node; đây là profile kiểm có gate, chưa chứng minh cô lập toàn cluster hoặc cửa sổ pod startup bằng0.

Docker inspect ghi OCI index, CRI báo config digest. [Mapping containerd](imported-images.txt), ba oci-index và ba oci-manifest nối hash index → manifest linux/amd64 → config digest khớp pod. Checker bổ sung ban đầu so nhầm CRI config với manifest (62/65); đã sửa đúng loại digest, kết quả68/68. Không sửa receipt/raw để làm xanh. Bản đối chiếu raw trước phần image-chain59/59 cũng được giữ.

Cleanup đã xác nhận: O subscriber dừng trước xóa topic; topic vắng, namespace/PVC và rule ES nonce vắng, port-forward sở hữu đã dừng. Image cục bộ giữ lại để truy vết; không prune volume/image cũ. Postflight node memory34%/38%. Tệp private chỉ ở scratch, không đưa vào gói.

Offline: [Codex retest fix-03](../codex-fix03-review/README.md) core22/22, regression42/42, agentHTTP4/4, bốn probe cũ và6probe độc lập. Verifier actor mới4/4. Không chạy lại suite nguồn không đổi chỉ để tăng số kiểm. CI bổ sung test actor verifier và yêu cầu job HTTP/image trước publish-images. Không sửa legacy actor logic, contract, receipt live-11 hay review cũ trong lượt này.

Giới hạn: lỗi EIO/ENOSPC chỉ được tiêm offline, chưa kiểm mất điện/PVC hỏng thật; sticky failure chỉ trong process; một process/trial và một owner/archive; client đồng bộ/quét cả run cần đánh giá trước dataset lớn.
