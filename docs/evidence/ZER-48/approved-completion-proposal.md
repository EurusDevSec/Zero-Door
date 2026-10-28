# Gói hoàn tất ZER-48 — chờ Hoàng duyệt

**PREPARED_NOT_AUTHORIZED.** Code/test offline đã đủ review:144 lượt test áp dụng đạt, independent review READY, source5file đã khóa. Gói này chỉ cho riêng ZER-48, không mở issue sau hoặc chạy lab.

## 1. Đúng một lượt inference thật qua adapter mới

- Backend/model giữ lựa chọn R0: OpenAI/gpt-6-luna, HTTPS cố định https://api.openai.com/v1/responses, service_tier=default/reasoning=none/store=false, tools rỗng; không endpoint/provider/model khác.
- Input synthetic health summary lành tính cố định trong verify_llm_adapter.py; không request SQLi, không tạo payload, không lấy dữ liệu/credential lab.
- **1run,1call,1attempt,0retry**, request≤8192byte, output≤256tokens, reservation≤9472tokens; app estimated-cost reservation≤0.005USD. Mức này là ước tính policy theo giá đã đối chiếu28/10, không provider billing hard cap; quan sát usage vượt reservation hoặc thiếu usage→không nghiệm thu, không thử lại.
- Timeout attempt20s, call25s, async overall30s; cửa sổ thao tác tối đa5phút gồm chuẩn bị và xác minh receipt/cleanup. Không gửi lượt thứ hai nếu fail/timeout/UNKNOWN; chưa biết request có đến provider vẫn phải giữ UNKNOWN.
- Credential chỉ qua environment của process con từ cơ chế Doppler đã dùng ở R0; không in/ghi key, không dump secrets, không đổi auth/config. Nếu Doppler/key/quota không sẵn sàng: dừng, ghi blocker.
- Client/response đóng trong async ownership kể cả timeout/cancel. Không pod/process background/tunnel/build/import/pull/namespace/shared mutation; cleanup là owned HTTP resources và process kết thúc.
- Raw reply đã redact, event trace, request/model/usage/cost, source hash và timestamp UTC được lưu run directory mới trong scratch/zer48/runs; không ghi đè raw cũ. Chỉ đưa receipt đã kiểm/redact vào evidence.
- PASS technical chỉ khi đúng source/model/schema/expected NORMAL, LLM_CALL joins khớp, usage hợp lệ và accounting đầy đủ. Alias vẫn immutable revisionUNKNOWN. Không nhận đây là deployed agent/pipeline/G3/G4/KPI.

Lệnh sau **chỉ dùng sau duyệt**; chạy từ primary R để dùng cấu hình Doppler hiện có nhưng helper/source thuộc checkout C:
~~~bash
cd /r/_Projects/Eurus_Workspace/zero_door
PYTHON=/r/_Projects/Eurus_Workspace/zero_door/scratch/zer12/production-nemesis/Scripts/python.exe \
  doppler run -- bash /c/Users/ACER/.codex/worktrees/zer-46-publication/zero_door/infrastructure/scripts/verify-llm-adapter.sh --live
~~~

Nếu key không được cấp thì dừng; không sửa cấu hình Doppler để tiếp tục. Đối chiếu cấu hình/model/API docs còn phù hợp trước dispatch, không đổi request đã khóa sau approval.

## 2. Publication có điều kiện sau khi inference thật đạt

Chỉ khi mục1 đạt và review evidence đúng source cuối: cho scoped commit/push branch codex/zer-48-llm-adapter, tạo PR, kiểm CI/review, merge và nghiệm thu riêng ZER-48/AC01 khi tất cả gate đạt.

Allowlist publication:
- agent-orchestrator/event_pipeline/llm.py
- tests/test_llm_adapter.py
- infrastructure/scripts/verify_llm_adapter.py
- infrastructure/scripts/verify-llm-adapter.sh
- .github/workflows/ci.yml (chỉ test adapter + import smoke Gaia/Hephaestus)
- docs/evidence/ZER-48/ (gồm authorization và live receipt đã redact)
- note llm-adapter-and-nemesis.md và NOW: **chỉ delta ZER-48 của gói này trên clean base**; giữ dirty handoff/queue/R3/16/17/18 ở working tree.

Không git add toàn bộ, force push, bypass CI/review, sửa protected rule hoặc gửi thông báo bên ngoài. Không đưa primaryR/unrelated dirty hoặc credential vào commit. Remote image build/import CI là kiểm trong pipeline; không deploy local lab. CI failures giữ nguyên và sửa consumer trực tiếp trong scope trước retest; nếu buộc mở rộng action scope thì dừng gói.

Hoàng có thể duyệt toàn bộ gói một lần có điều kiện: **chỉ chuyển ZER-48 Done sau inference thật + review + CI + merge + owner acceptance**; ZER-19 cha, các issue kế tiếp và G3/G4 giữ kết luận riêng. Nếu mục1 không đạt thì không publication/Done dưới quyền có điều kiện này.

Lý do cần duyệt: WORKFLOW quy định model/lab và Git publication là quyền riêng; quyền R0/R3 trước đó không cấp lượt inference/publication ZER-48 mới. Gói offline đã hoàn tất trước khi xin quyền; không yêu cầu duyệt lại từng sửa/test nội bộ.
