# ZER-12 + ZER-40 — khép ghi chú N1–N4 sau Claude retest

**OFFLINE_PASS — sẵn sàng publication/CI khi Hoàng cho phép. Chưa Done.** Baseline HEAD c09452a, nhánh zer-12-command-guards, staged rỗng. Gói trước đã được [Claude retest độc lập](../claude-retest.md), không còn P1/P2; gói này chỉ khép bốn ghi chú P3.

| Ghi chú | Sửa | Kiểm ảnh hưởng |
| --- | --- | --- |
| N1 | Effective-env gate kiểm namespace thực, prefix, env override, mount → volume → đúng loại/tên nguồn, ledger ghi được; cấm subPath/profile ngoài mẫu | 24 mutant wiring/rollout bị chặn, 3 manifest hợp lệ qua; 20 phản ví dụ Claude được chạy lại nguyên logic đều bị bắt |
| N2 | Sau lời gọi send, cả Refused từ ledger.complete cũng trả 503 OUTCOME_UNKNOWN; giữ lý do gốc ở log | ASGI fake: send/ack thành công rồi complete lỗi; retry 409 UNKNOWN, send đúng một lần. Snapshot fix-01 fail đúng response LEDGER_UNAVAILABLE |
| N3 | Runbook yêu cầu fault-operator, heal-operator và signer sinh độc lập, khác giá trị; provisioning so digest cục bộ và chỉ in PASS/FAIL trước bật heal | Review tài liệu; không đọc hay kiểm Secret thật. Gate YAML không chứng minh giá trị secret khác nhau |
| N4 | Worker và Nemesis strategy Recreate, không RollingUpdate mặc định trên một ledger | OpenAPI + gate bắt bỏ strategy; chưa thử rollout/PVC thực |

Phạm vi source đúng sáu file trong before/. Không sửa executor, command guard core, event contract/pipeline, dependency/pin/CI workflow. 33 method trên mỗi graph production Nemesis/Hephaestus (7 guard +3 mode +13 integration +6 CI +4 event agents), cộng consumer 3: **36 method riêng biệt,69 lượt**, tất cả đạt; OpenAPI cả hai env đạt. Bandit 1.7.9 trên Python 3.12.4 không có issue; HTTP tests dùng Python 3.11.9 và production pins như fix-01. Go22/vet/Linux/Gosec, transport/storage regression và locked contract giữ kết quả fix-01/Claude; không chạy lại vì nguồn liên quan không đổi.

[Portable replay](replay_before.py) dùng sáu snapshot exact fix-01: old effective gate bỏ lọt24 subcase,3 valid controls đạt; old trigger sai thông điệp sau send. Script chỉ thay function trong process test, không ghi source. Chạy trong môi trường test production đã cài:

~~~bash
python -B docs/evidence/ZER-12/fix-02/verify_fix.py
python -B docs/evidence/ZER-12/fix-02/replay_before.py
~~~

[delta-manifest](delta-manifest.json) seal toàn bộ79 source hiện tại, snapshot sáu file, evidence mới, cùng bằng chứng cũ/protected/dirty ngoài gói. Checker chỉ đọc hash/log, không thay cho independent review hay CI. Manifest/checker v1 và fix-01 giữ lịch sử; chúng báo source drift sau fix-02 là đúng, không sửa hash cũ.

F9 residual giữ nguyên: production healer disabled; AUTO/fallback mới offline, B0 chưa có audit bền riêng. Không đóng ZER-11/39/G1. Còn remote CI (race, production graphs, image build/smoke), review delta phù hợp và Hoàng nghiệm thu; không nhận historical runtime ZER-9 làm proof revision guard. Không commit/push/PR/merge, Linear write, Docker/lab/model/cloud hoặc real secret.
