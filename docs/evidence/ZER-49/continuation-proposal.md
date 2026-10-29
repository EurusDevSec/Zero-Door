# ZER-49 — một lượt bù sau sửa positive acceptance input

PREPARED_NOT_AUTHORIZED. [Lượt01](inference-01/README.md) giữ NOT_MET/ABSTAIN và cleanupPROCESS_REAPED; đúng1call đã tiêu thụ. Owner approval cho gói01 không tự cấp02. Không sửa raw/gate để nhận ABSTAIN thànhPASS, không publication khi gate01 chưa đạt.

## Nguyên nhân và sửa tối thiểu

Input01 chỉ là diagnostic sentinel và tự nói không có request/action; model không có căn cứ để kết luận application incident. Independent review đồng ý đây là positive test input mơ hồ, không phải transport/schema/Doppler/RAM failure. Component giữ đúng hành vi abstain và trace.

Input02 tại inference-prep-02/observation.json là đúng một synthetic application-error sample, sinh qua cùng Gaia.poll_elasticsearch_logs/Detector, metric log_pattern_match=1/threshold0. Log cố định:

> ERROR catalog lookup failed: sqlite3.OperationalError: database is locked; request returned HTTP 503.

Đây là log giả cho kiểm chức năng, không phải lỗi lab thật hoặc SQL payload. Provenance tại input-origin.json; không gửi expected label/ground truth hoặc chỉ dẫn ép classification vào model. Không tạo lỗi database thật, không chạy query/traffic hoặc thay dữ liệu. Nhãn kỳ vọngAPPLICATION_ERROR nằm ở protocol/checker phía ngoài, không ở observation. Không chọn dữ liệu theo output nhiều lần; chưa gọi model cho input02.

Model/prompt/schema/6productpins giữ nguyên. Không hạ AC hoặc giá trịUNKNOWN/refusal/fallback thành success. Lượt02 chỉ đổi fixed input/config/run-trial-incident mới; wrapper derivative đổi đúng tên proposal/prep/output và thêm gate cleanup01, expectedAPPLICATION_ERROR. run_once.py và input01 giữ nguyên để tái kiểm17pins cũ.

## Envelope và điều kiện dừng

- Chỉ1inference-02/1call/1attempt/0retry qua OpenAI/gpt-6-luna Responses cố định và adapter hiện có; storefalse/tools[]/defaulttier/reasoningnone.
- ≤8192requestbytes/≤256outputtokens/reservation≤9472tokens, estimate≤0.005USD cho riêng02, không phải billing hard cap. Lượt01 đã dùng0.0001092USDestimate; không gộp để giả định chưa tiêu thụ.
- Attempt20s/call25s/async30s cooperative; owned native child timeout40s, finallykill/reap≤5s cho timeout/interrupt/waiterror. Cửa sổ≤5phút gồm cleanup.0lab/Docker/build/import/pull/apply/restart,0fixtureHTTP/0TCP, không hạ guard hay thay shared.
- Dopplerexistingrouting ở primaryR, key vào childenvironment, không in/ghi key, không sửa auth/config. Source/output vẫn ở checkoutC. Thiếu credential/quota→dừng.
- Exactnewownerapproval khóa continuationproposal+manifest02; không dùng authorization01. Giữ17pins01 và raw01; manifest02 khóa cả final/receipt01.01phảiNOT_MET,1call và PROCESS_REAPED trước admission02. Output02exclusive; không replay/no03.
- PASS02 cần classificationAPPLICATION_ERROR/schema hợp lệ, evidence/context/causation/DETECTEDtimestamp đúng, mộtLLMtraceOK, usage/cost đầy đủ không overage, childreaped và independentreview. UNKNOWN/ABSTAIN/refusal/schema/ref/timeout/unknownusage→NOT_MET, cleanup và chốt blocker, không tự chạy03 hoặc thaypromptđểépnhãn.

## Publication có điều kiện

Nếu02đạt và review đủ: tiếp tục scope publication đã duyệt cho ZER-49 (Gaia4files/test/CI/evidenceZER49, note/NOWdelta, .gitattributes scopedbytepreservation khi cần); giữ cả01NOT_MET và02result. Commit/push/PR/CI/review/merge, owner conditionalacceptanceAC01 và Done chỉ khi đủ gate. Không publish/Done khi02fail. Không mở ZER-50, không deployed/Oarchive/G3/G4/KPI/formalbenchmark claim. Giữ unrelateddirty/primaryR.

Lệnh chỉ dùng sau approval02 thật:

~~~bash
cd /r/_Projects/Eurus_Workspace/zero_door
doppler run -- /r/_Projects/Eurus_Workspace/zero_door/scratch/zer12/production-nemesis/Scripts/python.exe -B \
  C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door/docs/evidence/ZER-49/run_once_02.py --execute \
  --authorization C:/Users/ACER/.codex/worktrees/zer-46-publication/zero_door/docs/evidence/ZER-49/authorization-02.json
~~~

Cần quyền mới vì gói01 quy định “không dùng lại approval để chạy02”, và WORKFLOW giữ inference/publication gates. Chuẩn bị02 hoàn toànoffline; không cấp quyền mới từ việc sửa input hoặc reviewsource.
