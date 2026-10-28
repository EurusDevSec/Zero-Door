# ZER-46 — kết luận điều tra PSI và readiness, 28/10/2026

**Hai blocker runner đã sửa và review độc lập. Có cơ sở đề nghị một lượt AC đầy đủ có guard; chưa có full AC PASS.** Không có thêm HTTP hoặc mutation lab trong gói điều tra này. [Gói đề nghị](../runtime-prep/acceptance-proposal.md) cần quyền mới, không reuse08/diagnostic01.

## Kết luận về nguyên nhân

1. **Điều xác minh được:**08 dừng do memory PSI16,37 vượt guard5. Chuỗi mẫu0,18 trước dispatch →4,08 →16,37 xác nhận pressure có thật; HTTP bị hủy vẫn UNKNOWN. SourceA có stall lớn và CPU throttle, không OOM/max event. Không có bằng chứng lỗi chức năng SQLi/block gây dừng vì chưa chạy tới block.
2. **Điều chưa thể quy:**Hoàng báo từng mở rồi đóng Chrome/Claude rất nhanh; không có timestamp hay process telemetry lịch sử để nối sự kiện này với08. Nó có thể là một yếu tố tài nguyên, nhưng không được ghi thành nguyên nhân đã chứng minh. Các mẫu RAM khả dụng vẫn trên1GiB cũng không loại trừ stall giữa các mẫu.
3. **Phân biệt đúng metric:**PSI đo tỷ lệ thời gian task bị stall theo các cửa sổ10/60/300s, không đo phần trăm RAM dùng. Global và cgroup là hai phạm vi khác nhau; OOM/max events ghi ranh giới memory controller, CPU throttle thuộc CPU bandwidth. Theo [kernel PSI](https://docs.kernel.org/accounting/psi.html) và [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html). Không suy CPU throttle chính là memory PSI.
4. **Điều kiện máy hiện tại đã đo:**25mẫu/120,11s chỉ đọc, PSImax0, host available min4.206.899.200byte/WSL2.278.748KiB. Không có chrome.exe/claude.exe trong tên process được chọn; node.exe không được quy mục đích vì không đọc command line. Direct reclaim/allocstall/OOM delta0, nhưng vẫn có background kswapd và14page swap-out; không ghi rằng toàn VM không reclaim/swap.

.wslconfig được đọc chọn lọc:6GB RAM/4CPU/2GB swap. Không sửa hoặc restart WSL. Windows host và VM dùng các phạm vi tài nguyên khác nhau; cấu hình trong file không tự chứng minh current runtime đã áp dụng toàn bộ. [Microsoft WSL settings](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

## Lỗi runner tìm được qua review độc lập

- **HIGH — kiểm nhầm executable của writer Windows venv.** sys.executable là venv launcher, native image là Python nền. Probe benign trên chính máy tái hiện WRITER_EXECUTABLE_MISMATCH. Sửa tách logical path và physical kernel image, kiểm cả hai cùng PID/creation/nonce; không nới native match. Phù hợp [CPython launcher](https://github.com/python/cpython/blob/v3.11.9/PC/launcher.c#L1807-L1859) và [Win32 QueryFullProcessImageNameW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew).
- **MEDIUM — deadline foreground rò sang watchdog.** Resource read khởi động trước phase transition có thể giữ deadline cũ và báo timeout giả. Sửa chỉ áp phase/log deadline cho thread protocol; watchdog giữ own timeout/global/work/stop guard. Post-command check chặn fast-exit lọt deadline.

Hai lỗi này nằm trong candidate mới, không được dùng để viết lại nguyên nhân08:08 có memory stall thực và chưa dùng TTL phase mới. Các lỗi collector06/07 đã có căn cứ riêng; không trộn chúng thành một nguyên nhân RAM.

## Bằng chứng sửa và review

5case mới fail-before2failures/3errors (bao gồm helper còn thiếu); sau sửa5/5. Tổng64case offline runner đạt, thêm4case admission wrapper đạt:68case. Tất cả process/HTTP trong unit test bị mock. Probe native riêng dùng một helper Python lành tính tự thoát3s:launcher13148/RPC21592, logical/native paths khác, retained handle ALIVE→EXITED, launcher0,3,118s;0writer/API/lab, không force terminate.

Reviewer /root/zer46_independent_review chỉ đọc, xác nhận hai finding đã khép và READY để chuẩn bị một full AC run được duyệt riêng. Không coi self-audit trước đây là independent review. Graph/PDG không đủ vì index GitNexus incomplete/FTS missing; không refresh gây áp lực RAM, kiểm trực tiếp source và runtime receipts.

Artifacts phân tích, observation, fail-before/retest và native proof mang prefix psi-resolution- trong thư mục này. Source/hash baseline trong scratch/zer46/psi-resolution; raw01–08 và diagnostic01 giữ nguyên.

## Quyết định hữu hạn

Không cần thêm nhiều phép chẩn đoán để cố chứng minh tên app lịch sử. **Đề nghị chấp nhận một readiness gate hiện tại**: môi trường đã giải phóng, preflight120s mới phải đạt, guard không đổi xuyên suốt, một lượt AC29fixtureHTTP+≤32observerHTTP/≤4TCP trong20phút gồm5cleanup. Không hạ TTL, guard, trace, restart, expiry hoặc hậu điều kiện cleanup.

Đây là rationale mới cần Hoàng chấp nhận cùng gói bounded; không tự xóa điểm dừng đã chốt. Nếu lượt AC lỗi:cleanup,giữUNKNOWNvàkhépblocker,không tựattempt10. Nếu đủ:technicalACobserved/rawreconciled,reviewkếtquảvàreadinesspublication;merge/Hoàngacceptancevẫnriêng. Không Done/publication từ diagnostic hoặc68mocktests.


## Kết quả sau quyết định của Hoàng

Hoàng đã chấp nhận rationale và duyệt đúng một runtime09. [Full component AC và raw review đã đạt](../runtime-09/README.md), không cần thêm lượt lab. Chuyển sang publication review trong scope, không tự commit/merge/Done. Các nhãn NOT_APPROVED phía trên là checkpoint lúc chuẩn bị proposal; không thay metadata bytes của proposal đã khóa.
