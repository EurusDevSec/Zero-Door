# ZER-46 — gói publication đã được duyệt

**READY_FOR_PUBLICATION_REVIEW.** [Runtime09](runtime-09/README.md) đã được raw verifier và reviewer độc lập chấp nhận đủ AC-01/02 ở phạm vi component. Không cần runtime10. Hoàng đã duyệt commit/push/PR/CI/review/merge và đóng Done khi đủ gate. Remote publication đang thực hiện; không chạy thêm lab.

## Nội dung trong scope

- Fixture opt-in trusted-client containment: services/sqli-fixture/{app.py,containment.py,Dockerfile,README.md}.
- Durable ConfigMap/CAS/absolute TTL writer: agent-orchestrator/hephaestus/sqli_containment.py, tests/test_sqli_containment.py và infrastructure/manifests/sqli-containment-lab.yaml.
- Evidence/runner/tests/approval/source snapshot dưới docs/evidence/ZER-46/, giữ cả failure/UNKNOWN cũ và full success09. Canonical hiện hành: runtime-09/{README.md,independent-verification.json,independent-review.md,technical-acceptance.json}; artifact-sha256.json giữ file hashes.
- Handoff kỹ thuật tại docs/delivery/NOW.md và docs/delivery/milestones/R3-recovery/block-ip-and-rollback.md, chỉ hunks ZER-46.
- CI chỉ thêm invocation test_sqli_containment.py vào job fixture hiện có. Đã xác minh current CI trừ đúng một dòng đó bằng byte-for-byte baseline trước ZER-46. Không stage cả file để vô tình kéo delta ZER-43 đã dirty sẵn.

## Khi được giao publication

Dựng diff/commit chỉ scope trên, rà staged hunks và cấu hình hash sau khi tách CI. Source pin CI lúc runtime có delta dirty trước đó, nên nếu metadata CI khi xuất bản khác thì cập nhật pin hiện hành có provenance riêng và kiểm offline liên quan; frozen runtime09 phải giữ nguyên, không viết lại as-executed. Không cần chạy lại lab chỉ vì đóng gói/CI metadata thay đổi.

Sau đó mới commit/push/PR, kiểm CI/review thực tế và merge theo quyền Hoàng cấp. Không coi68offline tests hoặc local source review là GitHub CI đã chạy. Issue Done chờ merge và Hoàng acceptance; parent ZER-17 không tự khép. Scratch và các thay đổi ngoài scope không stage.

## Giới hạn đã giữ

Boutique business chưa đạt, không claim toàn lab khỏe/R1/KPI/production healing/LLM/end-to-end. Namespace/ConfigMap/process cleanup và shared preservation của component đã có proof. Không đổi dữ liệu, giảm AC hoặc giấu failed attempts để publication.

## Đóng gói trên main sạch

Checkout publication riêng lấy main 2687297, chỉ thêm invocation CI của ZER-46; giữ nguyên toàn bộ raw/as-executed snapshots. .gitattributes khóa byte evidence ZER-46, source-hashes hiện hành ghi riêng CI hash publication và as-executed. Checkout chính cùng dirty work ngoài scope được giữ nguyên.
