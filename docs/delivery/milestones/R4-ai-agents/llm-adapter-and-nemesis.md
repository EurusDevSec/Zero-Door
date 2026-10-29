## ZER-19 — nghiệm thu chức năng đạt; publication — 29/10/2026

[Runtime-04](../../../evidence/ZER-19/runtime-04/README.md) và review độc lập xác nhận AC02/03 trong phạm vi SQLi-only:1inference gpt-6-luna/216+26tokens/3.211s/0.0000346USDestimate; observation→LLMplan→validate→executor→result,1benign-apparel send200/0restrictedRows,3HTTP200/1TCPdenied,MAX_ROUNDS1. CleanupCLEAN:namespace và2topic absent,sharedspec/UID/restart giữ nguyên,3PVCBound. AC01 dùng ZER48/PR34;132Python+37Bash kiểm sản phẩm và44helper kiểm offline đã đạt. 9productpins và43runtimepins khớp. Hoàng duyệt publication có điều kiện tại [gói](../../../evidence/ZER-19/publication-package.md); commit/PR/CI/review/merge và ownerconditionalacceptance còn là gate trước Done. Giữ raw01–03 NOT_MET/UNKNOWN; không formal benchmark/healing/KPI/G3/G4/live-cancel claim, không thêm lab/model/issue khác.

## ZER-48 — live adapter verified, đang publication — 28/10/2026

Hoàng duyệt toàn bộ gói hoàn tất. [Live receipt](../../../evidence/ZER-48/live-receipt.json):1call/1attempt, NORMAL/health01,162+22tokens,4.625s,0.0000272USDestimate; source5pins và trace joins khớp, không retry/lab/deploy.144test lượt+review READY offline; review live evidence đã đối chiếu schema/model/usage/IDs/caps. **AC01 kỹ thuật đủ; chưa Done trước remoteCI/review/merge và acceptance.**

Publication branchcodex/zer-48-llm-adapter được neo lên main33001a3, tree bằng reviewed0b72edd, để không cuốn lịch sử ZER18. [Evidence](../../../evidence/ZER-48/README.md) và [authorization](../../../evidence/ZER-48/completion-authorization.json). Chỉ đưa code5paths/evidenceZER48 và prefixZER48 của note/NOW trên cleanbase vào commit; giữ nguyên dirty handoff/queue/R3/16/17/18 vàprimaryR. Không mở issue sau; checkpoint dưới là lịch sử.

## Codex tiếp nhận ZER-48 — gói offline đã review, chờ quyền hoàn tất — 28/10/2026

Hoàng đổi người thực hiện từ Claude sang Codex và yêu cầu làm riêng ZER-48. Branch codex/zer-48-llm-adapter/base0b72edd; một writer, giữ dirty handoff/R3/ZER16/17/18/primaryR. [Evidence](../../../evidence/ZER-48/README.md): shared async adapter/schema/trace/budget, helper bounded;22focused tests mỗi pin+100regression=144lượt đạt, independent reviewer READY sau sửa3finding.5sourcefile đã khóa, không dependency/agent executor/guard change; module được COPY theo package Gaia/Hephaestus, Nemesis integration thuộc ZER19.

AC01 **chưa đủ Done** vì mới OFFLINE_SIMULATED;0provider/lab calls, chưa publication/Linear write. [Gói hoàn tất chờ duyệt](../../../evidence/ZER-48/completion-proposal.md) gồm đúng1inference lành tính/1attempt/256output/20s timeout/25s call/30s overall,0.005USDreservation-estimate và publication có điều kiện nếu đủ gate. Không tự thử lại hoặc mở issue tiếp theo. Hướng dẫn giao Claude dưới đây là checkpoint lịch sử; Codex đã tiếp nhận theo yêu cầu mới.

Exact file/action allowlist và hash: [verification](../../../evidence/ZER-48/verification.json), [source pins](../../../evidence/ZER-48/source-hashes.json). Code5paths, evidenceZER48, prefixnote/NOW; metadata gói mới không cuốn dirty trước. Graph/PDG không đủ, source/direct probes được dùng; G3 vẫnNOT_VERIFIED, không G4/KPI/end-to-end claim. Thông báo một lần qua app đã được đặt theo yêu cầu Hoàng, không bảo đảm đánh thức khi thiết bị ngủ.

# Issue — LLM adapter chung và Nemesis

[Milestone R4](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis). Nguồn đối chiếu: `R4-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R4-T01-S01 | Dựng adapter async dùng chung: schema, model/prompt version, usage, timeout. | [ZER-48](https://linear.app/zero-door/issue/ZER-48/dung-llm-adapter-va-trace-dung-chung) |
| R4-T01-S02 | Nối observation → kế hoạch Nemesis → executor → kết quả. | AC của [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis) |
| R4-T01-S03 | Thêm start/stop, max rounds/calls và điều kiện dừng. | AC của [ZER-19](https://linear.app/zero-door/issue/ZER-19/llm-adapter-chung-va-nemesis) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R4-T01-S01

Interface và trace thật; quota/cost được cộng theo run.

### R4-T01-S02

LLM chọn kế hoạch trong registry hợp lệ; kế hoạch được kiểm tra trước khi thực thi.

### R4-T01-S03

Một phiên tự kết thúc trong budget; log stop/cancel và số gọi model.

## Phụ thuộc cần đối chiếu

[R0-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R0-foundations/llm-backend.md), [R2-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md), [R2-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R2-chaos-scenarios/combined-run-and-cleanup.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.
