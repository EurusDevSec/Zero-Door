# ZER-11 / ZER-39 — RT1 thật và sửa trực tiếp

**PASS_SCOPED_RT1, chưa phải ZER-11/39 Done hoặc G1 PASS.** Hoàng cho phép sửa trực tiếp rồi duyệt RT1 qua `call_84d20afcbd014088a379b9fc172d89da`. Context `k3d-zero-door`, HEAD `169413303340fc01eea8597c121ce39455892af0`, chưa commit/push/Linear. Ngày 21/10/2026; thời gian bên dưới là UTC (Việt Nam +7 giờ).

## Kết quả thực

Run `run_57384640937b4fedab2e07d588ce46db`, [receipt](attempt-04/receipt.json), [cluster evidence](attempt-04/cluster-evidence.json), [scorer](attempt-04/results/rt1-57384640937b/score.json).

| Trial | Bằng chứng độc lập | Kết luận |
| --- | --- | --- |
| B0-CTRL | Xóa đúng 1 pod frontend theo UID; probe xác nhận effect và recovery; pod Ready mới cùng ReplicaSet UID; Event tạo pod nằm sau T_req và trước T_rec; audit đủ, 0 hành động O | RECOVERED_UNDETECTED / CONTROLLER_RECOVERY_OBSERVED; TotalRecovery **39,997 s**; MTTD/MTTR incident N/A |
| B0-HPA | Hai HPA đọc được CPU; frontend có SuccessfulRescale 1→2→3; 364 mẫu checkout đều đạt, phủ W_eff=300 s | CONFIRMED_NO_EFFECT / NO_EFFECT, ra khỏi N; **không** claim HPA đã phục hồi nghiệp vụ |

- B0-CTRL: 104 mẫu (70 đạt, 34 lỗi), 410 request; HPA: 364 mẫu, 1.820 request. Tải GET riêng: **3.599/3.600 request**, 180 s, 0 error. Một pod delete tổng cộng; không gọi model/API trả phí.
- Lượt thành công mất 606,313 s. Các lần chuẩn bị bắt đầu 15:47:47; cluster cleanup xong 16:09:32, dưới deadline chung 16:47:47. Lượt cuối rút cap tổng còn 2.901 s để giữ deadline chung, gồm 300 s dự trữ cleanup; không đổi F-01/cap_rec/W_eff hay trần request. Nếu chạm cap chung vẫn phải trả incomplete, không bảo đảm fit worst case 3.250 s của plan gốc; thực tế hai cửa sổ đã hoàn tất.
- Main O chỉ có RUN_CONTEXT và hai TRIAL_CONTEXT. Positive control riêng: event hợp lệ được ghi, DECISION bị quarantine MODE_VIOLATION; manual scale được nhìn thấy qua manager kubectl/subresource scale và controller Event.
- [Audit độc lập](independent-audit.json): 676 hash envelope khớp (673 H + 3 O), ID không trùng, tính lại T_rec − T_eff = 39,997 s, N=1 sau khi loại trial no-effect.
- Postflight độc lập: cả **13 deployment** giữ nguyên UID và toàn bộ spec/replicas; tất cả Ready đúng số baseline; không còn HPA/profile/namespace của lượt chạy. Gaia/Hephaestus trở về 1; checkout vẫn 3 và currency vẫn 2 như lúc nhận.

## Giới hạn phải giữ khi đọc kết quả

- **Quota chặn thêm pod frontend:** Event FailedCreate ghi requested limits.cpu=200m, used=2825m, limit=3000m. HPA đã yêu cầu scale, nhưng không chứng minh thêm năng lực phục vụ hoặc HPA chữa lỗi. Không đổi quota hoặc giảm checkout/currency vì ngoài quyền RT1. Cần tính lại headroom trước các thí nghiệm HPA về sau.
- Có một cleanup giỏ hàng B0-CTRL bị CONNECTION_RESET trong outage, giữ trong receipt/probe; **cluster cleanup CLEAN không đồng nghĩa mọi cleanup dữ liệu nghiệp vụ đã xác minh**. Không xóa dữ liệu khi thiếu bằng chứng.
- Có PROBE_GAP; scorer giữ uptime CTRL=FAIL, HPA=UNKNOWN. Aggregate MTTR 120/180 là NOT_PASS/unobserved; không biến 39,997 s TotalRecovery thành MTTR đạt KPI. CPU P179, benign, request-success, leak/access evidence vẫn MISSING/UNKNOWN như artifact. Đây là kiểm pipeline/đối chứng, không dataset nghiên cứu chính thức.

## Các sửa đã làm, không chuyển vòng sửa qua Claude

[Diff đúng phạm vi](source.diff), [hash](source-hashes.json), [snapshot/script/log tái kiểm](reproduction.zip).

1. **FXRT1-01:** CTRL cần đủ T_req/Event/T_rec và thứ tự hợp lệ với độ phân giải Event một giây; thiếu/mơ hồ giữ MISSING, không đổi scorer/KPI. Regression 12 ca: trước sửa 10 ca sai fail, 2 đối chứng đạt; sau sửa và replay độc lập 4/4 đúng. [Báo cáo focused trước runtime](../codex-rt1-fix02.md).
2. **Runtime P0:** ảnh node thật có `names:null`; bỏ qua inventory không tên nhưng vẫn bắt buộc có đúng image. Regression có/không image fail trước, đạt sau.
3. **Runtime P1:** kubectl dry-run multi-document trả nhiều JSON document, không phải List. Parser đọc đủ stream; fake sửa theo output thật; end-to-end fail-before đúng JSONDecodeError, đạt sau.
4. **Runtime P2:** k3s có ownership tại 1 replica nhưng mất khi về 0. Chẩn đoán lưu raw từng mốc, rồi lưu observation UID/resourceVersion/managers tại cả hai bước. Giữ nguyên điều kiện đúng manager/subresource/controller; test manager sai vẫn bị chặn. Không gán tác giả từ lệnh thành công.
5. **P8 shutdown:** Uvicorn re-raise KeyboardInterrupt làm thiếu receipt cuối. Bắt đúng Ctrl+C sau shutdown rồi kiểm hash; test cả root nguyên vẹn và root bị đổi, giữ exit 5 cho integrity failure. Trước sửa exit130/stopped=false được giữ; sau sửa Ctrl+C thật exit0, root_unchanged=true.

Source chỉ đổi harness, CLI, hai test suite và đoạn runbook tương ứng; checkpoint note/NOW được cập nhật. 245 nguồn ngoài phạm vi khớp hash snapshot. Không sửa measurement/scorer/event_pipeline/worker/CI/quota/image workload.

## Kiểm và P8

- Hồi quy harness cuối: **29/29** trên Nemesis, 144 s; các ca trực tiếp liên quan **5/5 trên cả hai production pins**.
- ResultsServer: **5/5 trên mỗi pin**, gồm unchanged/tampered/Ctrl+C/khóa/route; Bandit 0; diff whitespace sạch. Source trước sửa và fail-before thực nằm trong reproduction.zip.
- Dashboard browser thật chọn đúng run B0; cùng hash score/CSV, N=1, nhãn, lỗi uptime và missing giữ nguyên. [Ảnh overview](dashboard-overview.png), [incident](dashboard-incidents.png), [AX state](dashboard-state.txt).
- GET API có auth: run/provenance khớp và ba file `score.json`, `incidents.csv`, `usage.csv` trùng từng byte với export/scorer. [Receipt đọc root sau Ctrl+C](serve-receipt.json): stopped=true, root_unchanged=true, changed=[]. Server đã dừng, khóa tạm đã xóa.
- Không chạy lại suite tới xanh: failure Nemesis26/27 và raw ở review trước giữ nguyên; lượt29/29 này chạy một lần sau thay đổi fake/thu bằng chứng. Không thay bằng chứng lịch sử hoặc tuyên bố lỗi timing host đã biến mất.

## Lượt dừng và phần còn lại

[Attempt01](attempt-01/receipt.json): P0 TypeError, 0 writes. [Attempt02](attempt-02/receipt.json): P1 JSONDecodeError, chỉ namespace/agent, cleanup sạch. [Attempt03](attempt-03/receipt.json): attribution control fail, 0 target pod delete, cleanup sạch. [Canary diagnostic](canary-diagnostic/): chụp manager ở 0/1/0, 0 target pod delete, cleanup sạch. Các lỗi đều giữ nguyên; chỉ attempt04 chạy fault thật. P8 trước sửa có [receipt chưa kết thúc](serve-before-fix.json), không ghi đè bằng receipt mới.

AC live đã đọc lại bằng linear_zero_door: ZER-11/39 vẫn In Progress, URL thuộc zero-door. AC-01/02 có offline + dashboard/runtime thật; AC-04 cha = AC-01 con có profile B0, không ZERO DOOR heal và phép đo độc lập trong phạm vi trên. Chưa có claim HPA recovery. **AC-03 còn RT2/MANUAL-RULES runtime theo runbook §5.7**; offline mode boundary đã có, chưa triển khai image mới hoặc chạy P6. Sau đó còn CI/review/publication/merge và Hoàng nghiệm thu trước Done. Không tự đổi trạng thái hoặc mở milestone mới.

Các script runtime trong reproduction.zip là bản ghi thao tác đã chạy, không cấp quyền chạy lại cluster. Chỉ dùng checker offline hoặc xin quyền tương ứng trước thao tác runtime/publication.
