# Issue — Consumer, retry và tương tác controller

[Milestone R3](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/README.md) · [Checkpoint](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/NOW.md)

**Issue Linear:** [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller). Nguồn đối chiếu: `R3-T03`. Ghi chú này giữ yêu cầu kỹ thuật và bàn giao; AC/trạng thái/lịch hiện hành đọc issue Linear.

## Phạm vi kỹ thuật

Chưa mở bước sửa mã. Khi giao bước cụ thể, ghi danh sách đường dẫn được sửa (kể cả test/probe/schema), owner và base HEAD trong mục Phạm vi phiên này. Bản kế hoạch không tự cấp quyền sửa mọi file liên quan.

## Đầu ra và cách chia issue

| Nguồn | Đầu ra / bước nghiệm thu | Liên kết Linear / checklist |
| --- | --- | --- |
| R3-T03-S01 | Sửa blocking consumer, ack, dedup, cooldown và retry có giới hạn. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |
| R3-T03-S02 | Thử restart, nhiều replica, PodKill và tương tác HPA. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |
| R3-T03-S03 | Thử worker/healer restart và mất telemetry. | AC của [ZER-18](https://linear.app/zero-door/issue/ZER-18/consumer-retry-va-tuong-tac-controller) |

## Yêu cầu kiểm chứng từ kế hoạch nguồn

### R3-T03-S01

Một action cho một event hiệu lực; lỗi không kẹt consumer hoặc lặp lệnh vô hạn.

### R3-T03-S02

Log tác nhân gây hồi phục; phân biệt hiệu ứng Kubernetes/HPA với healer.

### R3-T03-S03

Run dở có trạng thái rõ; dữ liệu thiếu không sinh kết luận thành công.

## Phụ thuộc cần đối chiếu

[R1-T04](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R1-measurement/guards-and-ci.md), [R3-T01](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/milestones/R3-recovery/recovery-state-and-scaling.md).

Đây là prerequisite candidate; đọc contract/evidence trước khi tạo relation, không chặn theo thứ tự thư mục.

## Bàn giao kỹ thuật

Chưa có bàn giao thực thi mới. Khi thực hiện, ghi issue Linear và thời điểm đọc AC, HEAD/dirty, phạm vi file/thao tác, kiểm tra/kết quả, evidence, giới hạn và bước tiếp theo. Theo [WORKFLOW](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md); trạng thái, lịch và phân công cập nhật trên Linear.

## Phạm vi phiên ZER-18 — 28/10/2026

Hoàng giao tiếp issue cuối R3. Codex là writer duy nhất, HEAD `b60cc55c693a462909b7b3c70edcadf344019b72`; dirty ZER-16/17 và primary R giữ nguyên. AC đọc live 10:30–10:36 UTC, SQLi-only AC01/03; AC02 bổ sung không nghiệm thu.

Allowlist: event_pipeline/{adapters.py,client.py,decision_journal.py}, hephaestus/main.py; tests/{test_hephaestus_consumer.py,test_event_agents.py,test_event_pipeline.py}; chaos-worker/internal/guard/sqli_restart_test.go; .github/workflows/ci.yml; note này, NOW và docs/evidence/ZER-18/. Kiểm offline bằng fake transport, SQLite thật và process/thread restart thật; không gọi lab/model/build/deploy, không payload mới. Git publication và owner acceptance chưa được cấp cho ZER-18.

Gói sửa: durable decision outbox tùy cấu hình path, trần retry/age/cooldown, receipt/cursor hợp lệ và shutdown có join; worker giữ guard/ledger hiện có, bổ sung case SQLi. Chỉ kết luận mức component có bằng chứng; không tự coi runtime09 hoặc mock là consumer deployed/G3 PASS.

### Bàn giao cuối — 2026-10-28T10:54:46.565412+00:00

Amendment trước sửa: thêm verify-event-actors.py và test_event_actor_verifier.py để cấp state path bắt buộc trong verifier hiện có; chỉ render emptyDir16Mi, khôngapply/PVC. Scope snapshot ở docs/evidence/ZER-18/scope.json.

149 lượt test Python,3Go packages đạt; review độc lậpREADY sau sửa poisonrecord. Expected/actual/hash/giới hạn ở docs/evidence/ZER-18/. Local-race chưa chạy doCGOdisabled, gateLinuxCI giữ nguyên. Worker effect làcounterlocal; healer process/outbox dùngfake transport; khôngclaim deployedbroker/PVC/recovery. Khônglab/traffic/model; chưaGitpublication/merge/owneracceptance/Done/G3PASS. Bước cuối cần duyệt publication-package.md; không mởR4 tronggói này.

### CI publication correction — 2026-10-28T12:31:55.221030+00:00

PR33 firstheadc676c7a failed2jobs sharing test_dashboard_modes caller missing mandatory statepath andoldone-tick hook; one matrixjobcanceled. Scope amendedbeforeedit with test_dashboard_modes.py,test_dashboard_mode_runtime.py,r1_mode_runtime.py. Migratedcallers/bundle and requiredDockerCOPYmodules; keptallassertions,main/guardsunchanged.22additional localtests passed,171total. See docs/evidence/ZER-18/ci-fix.md. RemoteCI/review/merge stillrequired; noDone/lab/G3claim.
