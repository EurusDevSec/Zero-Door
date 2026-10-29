## ZER-49 — nghiệm thu chức năng đạt, publication —29/10/2026

[Inference02](../../../evidence/ZER-49/inference-02/README.md) và review độc lập đạt:1realcallgpt-6-luna/653+86tokens/6.140smodel/6.203sdiagnosis/0.0001083USDestimate, APPLICATION_ERROR/refcontext đúng/NO_ACTION/no fallback; processreaped6.859s/0lab. DETECTED giữ nguyên, khoảng chờapproval/replay không làMTTD; scorerkhôngđổi.56originaltests+7runner02checks vàbaselinePASS.01NOT_MET/ABSTAIN giữ nguyên. [Publication](../../../evidence/ZER-49/publication-package.md) đã được Hoàng duyệt có điều kiện; code6pins giữ nguyên, không cần thêm model/lab. Done chỉ sauCI/review/merge/ownerconditionalacceptance. ChỉZER49functional; khôngdeployed/Oarchive/G3/G4/KPI/parentZER20/ZER50claim. Các mốc bên dưới là lịch sử.

# Issue — Gaia và Hephaestus có quyết định LLM được giới hạn

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-20](https://linear.app/zero-door/issue/ZER-20/gaia-va-hephaestus-co-quyet-djinh-llm-djuoc-gioi-han). Nguồn đối chiếu: `R4-T02`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

ZER-49 đã được Hoàng giao ngày29/10/2026. Codex là writer duy nhất trên checkout zer-46-publication, branch codex/zer-49-gaia-diagnosis/base9b5287c. [Phạm vi file/action và dirty baseline](../../../evidence/ZER-49/scope.json) khóa Gaia main/diagnosis/CLI/Docker, test Gaia, CI, evidenceZER49 và delta ghi chú/NOW; không mở ZER-50 hoặc sửa MTTD/scorer/shared infrastructure. Chưa có quyền inference/publication từ việc giao issue.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T02-S01 | Nối evidence → chẩn đoán Gaia, giữ mốc phát hiện trước khi chờ LLM. | [ZER-49](https://linear.app/zero-door/issue/ZER-49/noi-evidence-vao-chan-djoan-llm-cua-gaia) |
| R4-T02-S02 | Cho Hephaestus chọn trong action enum, gồm NO_ACTION/ABSTAIN khi phù hợp, rồi qua guard và xác minh hồi phục. | [ZER-50](https://linear.app/zero-door/issue/ZER-50/noi-quyet-djinh-llm-cua-hephaestus-qua-policy-guard) |
| R4-T02-S03 | Thử JSON sai, timeout, 429 và thiếu bằng chứng; fallback được đánh dấu. | AC của [ZER-20](https://linear.app/zero-door/issue/ZER-20/gaia-va-hephaestus-co-quyet-djinh-llm-djuoc-gioi-han) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T02-S01

Incident có metric/log đầu vào, diagnosis và latency; MTTD không bị định nghĩa lại.

### R4-T02-S02

Trace đề xuất, action, lý do chấp nhận/từ chối, decision latency và probe kết quả; không chữa thừa ở case lành tính.

### R4-T02-S03

Các trường hợp lỗi không tạo action ngoài allowlist và không bị ghi nhãn AI thành công.

## Phụ thuộc cần đối chiếu

[R4-T01-S01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/llm-adapter-and-nemesis.md) (mục nguồn trong ghi chú), [R3-T02](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/block-ip-and-rollback.md), [R3-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/consumer-and-controller.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

ZER-49, AC01 đọc live29/10/2026; prerequisites ZER-48/10/7 đọc lại Done. [Evidence/AC matrix](../../../evidence/ZER-49/README.md) và [gói hoàn tất](../../../evidence/ZER-49/completion-proposal.md).18Gaia+4event-agent+22adapter+6runner+6CIboundary tests đạt, baselinechecker PASS. Chẩn đoán chạy nền sau DETECTED; writer evidence ra thread riêng, cancel drain trước close; shared run budget, closed schema/ref check, no action/retry/fake fallback success. Defaultdisabled, explicit R1/B2 config/output; standalone CLI cùng Diagnoser dùng inputO synthetic benign cố định. Source review READY sau sửa blockingdisk; review wrapper/proposal cuối READY_FOR_OWNER_APPROVAL; không còn finding chặn.

GitNexus index stale/incomplete; không claim graph/taint/PDG coverage từ zero hits. Source17pins và offline logs khóa, primaryR/unrelated dirty giữ nguyên. Doppler credential xác nhận hiện được cấp vào childenvironment,0modelcall/0lab trong chuẩn bị. Chưa inference/publication/Done; không coi local journal là authenticated O archive hoặc deployed/integration/G3/G4/KPI. Bước tiếp là duyệt đúng1call và publication có điều kiện theo WORKFLOW; fail/UNKNOWN thì khép blocker, không retry. ParentZER20 và ZER50 giữ gate riêng.

## ZER-49 — kết quả inference01 và bước bù có giới hạn —29/10/2026

Hoàng đã duyệt completionproposal;17sourcepins giữ nguyên,1realcall gpt-6-luna,657+87tokens/3.079s/0.0001092USDestimate. [Raw/conclusion](../../../evidence/ZER-49/inference-01/README.md): schema/IDs/timestamp đúng nhưng diagnosisUNKNOWN/ABSTAIN, vì positiveinput chỉsentinel không có evidenceincident. Giữ NOT_MET; đây là lỗi chuẩn bị case, không quyRAM/Doppler hoặc chuyển thànhAI PASS. Childreaped3.562s/0lab/0publication. Review độc lập xác nhận nguyên nhân/gate còn thiếu.

[Continuation proposal](../../../evidence/ZER-49/continuation-proposal.md) đã chuẩn bị offline: fixedsyntheticapplication-error rõnghĩa/provenance tách ngoàiobservation, khôngexpectedlabel/GT gửiLLM; product/prompt/model/schema giữ nguyên.7runner02checksđạt,19pinskhóa gồm raw/final01. Chưa duyệt/chạy02; cần một quyền mới vì gói01 cấm dùng lại approval. Không03/noautomaticretry/noHephaestus. Nếu02đạt mới publication/CI/review/merge/Done theo ownerconditionalacceptance; nếu02fail cleanup và khépblocker.
