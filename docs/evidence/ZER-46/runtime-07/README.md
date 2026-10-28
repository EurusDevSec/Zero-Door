# ZER-46 runtime07 — block/benign đạt trước replacement, thiếu join sau replacement

28/10/2026. **PARTIAL_RUNTIME / NOT_MET_POST_REPLACEMENT_ACCESS_JOIN / NOT_READY_FOR_PUBLICATION.** Attempt đã kết thúc sau320,30giây; không tựretry.

- 0build/import/pull,55guard samples đạt: hostmin3.314.962.432byte,WSLmin2.327.556KiB,PSImax0. Private fixture/proxy/source trênagent-0; header trust/spoof và2TCP direct-access negative controls đã kiểm trước replacement.
- 16fixtureHTTP,15request/access-log joins. Trước replacement, nguồnA GET và POST bị403 SOURCE_BLOCKED đúng action; nguồnB200 vàownedCRUD201/200/200/404 đạt. Rule API được tạo TTL180giây; API accepted không tự thành effect PASS.
- Fixture Pod thay UID và có hook/Ready. Request16 HTTP403 nhưng thiếu fixture access join: raw0166/0168 stderr ghi Found2pods,usingoldPod sqli-fixture-7855cbd589-cddmx; collector logs deployment tự lấy Pod cũ. Không suy HTTP403 này là fullpostrestart proof. Writer replay, expiry/unblock và API+mount rule cleanup chưa chạy tới.
- Cleanup namespace UID75a8d78d-6722-4862-96b4-1760d776d4ff đọc lại absent; sharedspec/UID/restart/3PVC nguyên, ownedCLEAN.16BoutiqueHTTP,labhealth chưa đạt. WriterlauncherPID21076 vàactualRPCPID17444 đều ABSENT theo writer-exit-readback.json; không giả định haiPID giống nhau trên Windowsvenv.
- Đã thử đọc một lần log known owned container sau namespace cleanup; runtime trả NotFound, lưu post-cleanup-log-read.json. Không tạo request hoặc actor mới để lấp missing trace.

[Raw reconciliation](independent-verification.json) xác nhận các kết quả và giới hạn trên, không dùng runner acceptance để thay proof. Raw/scripts giữ nguyên. Chưa review bởi người/agent khác; AC toàn chuỗi chưa đạt,khôngDone/KPI/end-to-end.

Futureharness đã sửa logs theo Pod+UID+owner+node, đọc lại oldPodabsent trong45giây cóUIDpin trước hậu restart; khôngforce-delete, khôngnới guard.35offlineharness tests đạt, gồmtwoPod/UIDdrift/alreadyabsent/timeout. [Gói08](../runtime-prep/logs-retry-proposal.md) NOT_APPROVED/NOT_RUN.
