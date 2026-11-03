## ZER-23 — kỹ thuật READY, đang publication — 03/11/2026

SQLi đi qua effect→Gaia→Kafka→Healer→native containment/business probe; C0 an toàn, Gaia ABSTAIN/Healer NOT_RUN giữ nguyên. Batch runtime02 NOT_MET vì ca CANCEL bị host RAM guard dừng trước model/traffic; cancel kiểm offline. Cleanup cuối toàn bộ CLEAN sau continuation riêng, failure gốc không đổi.110 offline và16 clean-source tests PASS; hai lens review READY. Không cần runtime03. Đọc docs/evidence/ZER-23/README.md/final-review.md/final-audit.json. Còn publication, CI/merge và Hoàng acceptance để Done; giữ dirty ngoài scope. Các checkpoint dưới là lịch sử.

# Issue — Chạy đầy đủ đường tấn công–phát hiện–hồi phục

[Milestone R5](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R5-integration/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc). Nguồn đối chiếu: `R5-T01`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Gói ZER-23 hiện hành do Codex thực hiện theo chỉ đạo Hoàng ngày03/11/2026; SQLi/C0/cancel, không mở lại ba vector/bad release. Checkout C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door, nhánh zer-23-sqli-pipeline, base d5b22414a66ddec3f02f549b4d18143f9b0c5880. Giữ toàn bộ dirty ngoài allowlist tại docs/evidence/ZER-23/scope.json. Source/test mới: gaia/sqli_observer.py, event_pipeline/sqli_handoff.py, hephaestus/sqli_pipeline.py, tests/test_sqli_pipeline.py, runtime-prep/test_runtime.py và invocation CI; không đổi guard/LLM selector/action source cũ.

[Ma trận AC và evidence](../../../evidence/ZER-23/README.md), [review trước runtime](../../../evidence/ZER-23/pre-runtime-review.md) và proposal/manifest dưới runtime-prep ghi ranh giới offline/runtime. 110 test offline đạt, hai reviewer độc lập READY,167sourcepins. Đang chạy một batch mới SQLi/C0/cancel theo quyền dự án; đọc runtime-01/started,progress,acceptance và cleanup trước khi tiếp nối, không phát lại lệnh. Chưa có kết luận AC/Done tại checkpoint này.

Các mục ba-vector/bad-release trong bảng nguồn bên dưới là lịch sử; AC sống SQLi-only trên Linear được ưu tiên.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R5-T01-S01 | Chụp phiên bản image/config/model/prompt và workload của đợt tích hợp. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |
| R5-T01-S02 | Chạy từng vector qua toàn pipeline và đo bằng probe độc lập. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |
| R5-T01-S03 | Thử bad release, benign traffic, thất bại và cleanup. | AC của [ZER-23](https://linear.app/zero-door/issue/ZER-23/chay-djay-dju-djuong-tan-cong-phat-hien-hoi-phuc) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R5-T01-S01

Manifest/version/run metadata đủ dựng lại.

### R5-T01-S02

Ba incident có trace đầy đủ; không dùng /heal/trigger làm đường đo chính.

### R5-T01-S03

Mỗi tình huống có verdict và log; failure được giữ trong dữ liệu.

## Phụ thuộc cần đối chiếu

[R4-T03](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/multi-agent-evidence.md), [R4-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R4-ai-agents/single-agent-baseline.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

## Bàn giao 03/11/2026 — source READY, baseline chưa được khôi phục

110 test offline đạt, hai reviewer độc lập xác nhận READY; 16/16 test mới được kiểm lại trên source sạch. Runtime-01 NOT_MET tại NetworkPolicy admission: 0 model call, HTTP, TCP, namespace hoặc topic mới. Cleanup CLEAN; work/cleanup process tree đã đóng và reap. Không phát lại lượt này.

Điều tra ghi nhận 0/19 pod hook; log khởi động đọc Node IP cũ .4 trong khi interface và pod HostIP hiện là .3. Mã kube-router 2.2.1 phù hợp giả thuyết giữ IP cũ; chưa có bằng chứng khôi phục để kết luận nhân quả. Recovery riêng agent, tối đa 300 giây, đã được review READY. Automatic approval review từ chối vì restart/drain có thể mất dữ liệu emptyDir mẫu và tái tạo pod; câu hỏi xác nhận cụ thể đang chờ trả lời. Chưa thực hiện recovery.

Runtime-prep-02 đã chuẩn bị, NOT_RUN và chưa có authorization; admission yêu cầu BASELINE_READY cùng owned recovery process đã đóng/reap. AC01 còn partial, AC02 chưa đạt, AC03 mới có phần offline/cleanup; chưa publication/merge/Done. Receipt và bước tiếp nối ở docs/evidence/ZER-23/README.md và automatic-review-rejection.json.
