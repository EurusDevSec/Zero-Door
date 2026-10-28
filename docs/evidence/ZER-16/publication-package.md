# Gói publication ZER-16

**PREPARED / NOT_AUTHORIZED / NOT_COMMITTED.** Gói offline đã review READY; Hoàng chưa cấp quyền publication của issue này. Quyền ZER-46 đã dùng xong và không được tái sử dụng.

## Outcome và scope cụ thể

Commit/push riêng bộ theo dõi hậu điều kiện action SQLi, test/packaging/CI, tạo PR vào main, kiểm CI/review đúng head, merge rồi chuyển riêng ZER-16 Done nếu đủ gate và Hoàng chấp nhận gói này. Không có runtime/deploy hoặc issue tiếp theo trong quyền đề nghị.

Base `6bf7d558d569b75af8d85ab108984d1ecd96623d`, branch `codex/zer-16-recovery-state`. Code được review khóa trong source-hashes.json:

1. `agent-orchestrator/hephaestus/sqli_action_state.py` mới.
2. `tests/test_sqli_action_state.py` mới.
3. `agent-orchestrator/hephaestus/Dockerfile`: copy prepared containment/state modules, không bật executor.
4. `.github/workflows/ci.yml`: thêm đúng một test invocation và import smoke của image Hephaestus.
5. `docs/evidence/ZER-16/`: replay read-only, report, hashes, kết quả và review.
6. `docs/delivery/milestones/R3-recovery/recovery-state-and-scaling.md`: handoff ZER-16.
7. `docs/delivery/NOW.md`: chỉ checkpoint ZER-16 trên baseline main; không đưa delta lịch sử ZER-17 đang dirty vào commit này.

Không stage `docs/evidence/ZER-17/`, note block-ip-and-rollback hoặc dirty primaryR. Không đổi writer/fixture/guard/manifests/evidence ZER-46/AC. Không `git add .`, force push, bypass check hoặc merge khi head thay đổi. Chuẩn bị index được đối chiếu scope trước commit; giữ các thay đổi local ngoài scope.

## Gate và điều kiện dừng

- 131 lượt test offline đạt, raw09 replay và review độc lập READY. Packaging import simulation đạt; chưa thay bằng Docker runtime claim.
- CI remote phải chạy trên đúng head, gồm test mới và build/import smoke image thực tế. Lỗi CI/review phải được xử lý trong scope và kiểm lại phần ảnh hưởng; không báo Done khi còn blocker.
- Merge dùng expected head pin, không admin bypass. Đọc lại commit merge và Linear Done/AC01 sau nghiệm thu; AC scale/HPA bổ sung vẫn unchecked.
- Không lab mới, không gọi LLM, không build/pull/import/deploy local, không sửa hạ tầng dùng chung hoặc mở ZER-18 trong gói này.
- Boutique NOT_MET, independent recovery chưa xác minh; production observer/consumer/LLM/end-to-end và gateR3 vẫn chưa đạt.

Quyền cần Hoàng duyệt: **commit/push scoped ZER-16, tạo PR, kiểm CI/review, merge và chấp nhận chuyển Done chỉ khi các gate đạt**. Không cần thêm checkpoint approval cho từng thao tác nhỏ trong gói đã duyệt.
