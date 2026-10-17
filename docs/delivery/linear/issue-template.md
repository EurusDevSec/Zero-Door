# Mẫu issue cho ZERO DOOR

Thích nghi canonical kit v1.0; thay mọi placeholder trước Ready. Giữ ngắn theo outcome; không sao chép ví dụ UI/backlog S-cool.

## Outcome

Actor/result/context và dấu hiệu quan sát được để nghiệm thu đầu ra.

## Scope / workflow / contracts

Includes, excludes; flow từ đầu vào tới kết quả; nguồn scope/design/setup; schema/API/data consumers và compatibility; invariant, validation và shared boundaries. Quyết định ghi CONFIRMED/PROPOSED/OPEN. Tên người/agent không đặt trong technical body để thay cho metadata phân công.

## Acceptance criteria

- [ ] AC-01: Given bối cảnh/đầu vào cụ thể, when hành động được phép, then kết quả quan sát và artifact kiểm tra được.
- [ ] AC-02: Given input/target/state không hợp lệ, hệ thống từ chối và giữ invariant được chỉ rõ.
- [ ] AC-03: Given failure/timeout/retry/missing/cleanup error, ghi trạng thái trung thực, không tạo recovery/KPI giả.
- [ ] AC-04: Review/handoff và checks cần thiết khớp candidate cuối; consumer bị ảnh hưởng được kiểm tra.

Điều chỉnh số AC theo outcome; không giữ ví dụ không liên quan chỉ để đủ bốn mục. Không pre-check từ hydration, code inspection hoặc trạng thái snapshot.

## Dependencies / failure cases

Blocked by: prerequisite contract/evidence hoặc None. Blocks: consumer/điểm bàn giao thật. Related: phối hợp không chặn. Liệt kê authorization/privacy/input, retry/cleanup, provider/cost và research integrity phù hợp; không bịa tenant hoặc browser matrix.

## Verification / evidence

Automated/manual/integration phù hợp rủi ro; environment/synthetic data, success/negative/failure cases và retest consumers. Exact commands chỉ khi biết từ repo. Ghi revision/dirty diff, time/timezone, môi trường, AC → case → result → shared artifact; Pending/Pass/Fail/Blocked/Not verified/N/A có lý do. Review/CI/merge và remaining gaps tách riêng.

## Metadata — nhập bằng field Linear

Project/team/milestone/parent theo ID thật. Assignee/priority/estimate/due/cycle chỉ theo quyền và quyết định tương ứng. Mã R*-T*-S* là alias provenance; Linear ID là định danh delivery chuẩn. Không lặp tên/ngày/status trong technical body như một bản metadata khác.

Ready khi contract/AC/prerequisite/metadata/verification đủ rõ và thực thi được trong quyền hiện có. Quyết định bắt buộc còn OPEN thì Backlog, hoặc chỉ mở phần chuẩn bị có boundary rõ. Done theo [QA và Done](R:/_Projects/Eurus_Workspace/zero_door/docs/delivery/WORKFLOW.md).
