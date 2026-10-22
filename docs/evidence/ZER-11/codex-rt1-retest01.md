# Codex retest — ZER-11 / ZER-39 rt1-fix-01

**CHANGES_REQUIRED — một P2 còn mở trong RT1-05.** Review ngày 21/10/2026, HEAD `169413303340fc01eea8597c121ce39455892af0`, local delta rt1-fix-01, staged rỗng. Không mở lại dashboard fix-01, scorer hoặc contract.

## FXRT1-01 — P2 — attribution controller chưa kiểm thứ tự thời gian

Vị trí: [controller_replacement](../../../infrastructure/scripts/r1_baseline_runtime.py#L1688), caller [interpret](../../../infrastructure/scripts/r1_baseline_runtime.py#L1737).

RT1-05 đã sửa nhận diện UID ReplicaSet, pod mới và tên pod trong Event, nhưng nhánh CTRL không dùng `identity.t_req`, `Event.t_ms` hay `incident.milestones.t_rec`. Vì vậy vẫn nhận `CONTROLLER_RECOVERY_OBSERVED` khi Event tạo pod xảy ra **sau** thời điểm probe xác nhận nghiệp vụ phục hồi, không có thời gian, hoặc trước trial. Nhánh HPA đã có các kiểm thời gian tương ứng.

Phản ví dụ độc lập: T_req = 1800000000000 ms, T_rec = T_req + 20 s; UID ReplicaSet đúng, pod replacement mới và Ready khi thu bằng chứng; Event SuccessfulCreate đúng pod nhưng ở T_req + 25 s. Hàm hiện trả `CONTROLLER_RECOVERY_OBSERVED`. Đây có thể xảy ra với deployment nhiều replica (P0 chỉ yêu cầu replicas > 0): request phục hồi qua pod còn sống trước khi controller tạo replacement; khi thu bằng chứng cuối trial, replacement đã Ready. Quan sát đó chứng minh controller tạo lại pod, chưa đủ để quy kết lần phục hồi nghiệp vụ trước đó cho replacement.

[Script](codex-rt1-retest01/claim_window.py), [expected/actual](codex-rt1-retest01/claim_window.json): đối chứng Event trong cửa sổ đúng được nhận; ba ca thời gian không hợp lệ cũng bị nhận. Script dùng hàm production, không gọi cluster/network. Bộ test mới tại test_dashboard_baseline_runtime.py:953 kiểm identity cho CTRL nhưng chỉ thay thời gian ở các ca HPA, nên không bắt phần thiếu này.

Sửa tối thiểu: truyền mốc phục hồi vào kiểm CTRL; đòi đủ thời gian hợp lệ, Event thuộc cửa sổ trial và đủ sớm trước T_rec để phân biệt thứ tự với độ phân giải Event. Thiếu hoặc chồng lấn thì MISSING/AMBIGUOUS, giữ nhãn scorer và raw nguyên vẹn. Thêm ca valid, trước trial, thiếu timestamp, tại/sau recovery. Đồng bộ đúng đoạn runbook CTRL. Đây là phần còn sót của RT1-05, không phải AC mới.

## Những phần đã khép

- RT1-01: P7 trong finally; lỗi host/cleanup từng bước được cô lập, DeleteOptions qua stdin, receipt best effort sau cleanup. Các ca ENOSPC/ValueError và lỗi HPA đầu đạt trên hai pins.
- RT1-02: query cần ownership có cờ managedFields; fake mô phỏng mặc định; manager sai bị chặn.
- RT1-03: host kiểm ba dữ kiện positive control, không dùng dispatch ok làm verdict; ba ca thất bại dừng trước target.
- RT1-04: intent trước create, reconcile nhãn/UID khi mất phản hồi; đối tượng khác được giữ và INCOMPLETE. Các ca lost ACK/foreign UID đạt.
- RT1-05 phần HPA và identity CTRL đã sửa; chỉ phần thời gian CTRL ở trên còn mở.

## Kiểm độc lập và N1

- Manifest 66/66 hash khớp; 246/246 nguồn read-only khớp snapshot. Note chỉ append, NOW chỉ prepend. Snapshot harness trước sửa khớp hash intake.
- AC live đọc qua `linear_zero_door`, URL `linear.app/zero-door/`: ZER-11/39 In Progress, AC không đổi. AC-04 cha = AC-01 con. Chưa runtime, CI/merge hay owner acceptance.
- Nemesis production: **26/27**, một test fail; Hephaestus production: **27/27**. Toàn bộ lớp Findings (RT1-01…05 hiện có) đạt trên cả hai pins. Log và raw thất bại giữ nguyên trong [gói retest](codex-rt1-retest01/).
- Ca Nemesis `test_no_recovery_with_coverage_is_timeout_and_without_coverage_is_missing_probe` mong MISSING_PROBE nhưng nhận UNKNOWN_EFFECT. [Raw H](codex-rt1-retest01/failed-hang-raw/export-H-H.jsonl) và [agent receipt](codex-rt1-retest01/failed-hang-raw/agent-receipt.json): ATTACK_REQUESTED ACK mất **4091.6 ms**, state DELIVERED; cửa sổ effect của fake chỉ 2 s. Chỉ có bốn mẫu trước T_req, không có mẫu sau đó; trial dừng `PROBE_ENDED:MAX_DURATION`, effect `STOPPED_BEFORE_W_EFF_DECIDED`. [Host receipt](codex-rt1-retest01/failed-hang-raw/host-receipt.json) ghi ABORTED và cleanup CLEAN.
- Đây là lượt fail thật, không đổi thành PASS và không chạy lại suite tới khi xanh. Dấu vết phù hợp giới hạn timing đã công bố; lượt Codex này chỉ đo được ACK chậm, không instrument fsync nên không khẳng định nguyên nhân phần cứng/antivirus. Không có bằng chứng TypeError fake ở lượt này. Kết luận UNKNOWN và cleanup là thận trọng; lỗi này không tạo PASS giả.
- Đối chiếu matrix fail-before Claude đã lưu: 11/11 dòng match, không ca AFTER lỗi; không chạy lại toàn bộ matrix/clean checkout chỉ để tăng số. Điều này không bao phủ phản ví dụ thời gian CTRL mới.

Hồi quy độc lập: dashboard 33/33, modes 7/7, CI boundary 6/6, check_r1_baselines và plan-check đạt; Bandit không báo issue. Runner kết thúc exit 1 vì ca Nemesis ở trên, không che lỗi bằng các bộ khác đạt. [Log Nemesis](codex-rt1-retest01/nemesis-runtime.log), [log Hephaestus](codex-rt1-retest01/hephaestus-runtime.log), [tổng hợp](codex-rt1-retest01/checks.json).

## Phạm vi và giới hạn review

Đã đọc diff bốn file được phép và caller P0–P8/CLI/tests/runbook. GitNexus reindex local `--pdg --index-only` xong trước test; CLI context/impact xác nhận caller CLI/test. MCP detect_changes/explain/pdg_query lỗi Transport closed: không nhận coverage taint/PDG query đầy đủ; diff/source và phản ví dụ là căn cứ. Không sửa source, không chạy lab/Docker/LLM, không commit/push hay đổi Linear.

Đề xuất gói sửa tiếp chỉ gồm hàm CTRL/caller, regression thời gian và đoạn runbook tương ứng; retest tập trung phản ví dụ mới và đối chứng, không mở lại audit toàn repo. Không tự nhắn Claude hoặc sửa source. Sau khi khép mới xem quyền RT1 theo kế hoạch đã ghi; chưa được chạy RT1 trong lượt này.
