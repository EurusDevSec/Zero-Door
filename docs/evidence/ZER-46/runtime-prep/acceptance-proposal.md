# ZER-46 — một lượt nghiệm thu đầy đủ sau điều tra

**PREPARED / NOT_APPROVED / NOT_RUN.** Không dùng lại quyền runtime08 hoặc diagnostic01. Gói này cần Hoàng chấp nhận cách quyết định readiness bên dưới và duyệt đúng một cửa sổ; không tự retry.

## Căn cứ và điều chưa biết

PSI08 là stall bộ nhớ thực. PSI đã ở mức0,18 trước client exec, tăng4,08 rồi16,37 khi client chạy; HTTP vẫn UNKNOWN. RAM khả dụng trên1GiB và owned Pod không ghi OOM/max events. Không có timeline process Windows tương ứng để quy cho Chrome/Claude. Lời Hoàng cung cấp là giả thuyết hợp lý cần giữ riêng, không phải causal proof.

Diagnostic01 trước đó có1GET200 và trace, PSImax0,12, cleanup tài nguyên riêng CLEAN. Điều tra mới có25mẫu/120,11s chỉ đọc, PSI0, host available tối thiểu4.206.899.200byte và WSL2.278.748KiB; không HTTP hoặc mutation. Đây là readiness hiện tại, không chứng minh tác nhân lịch sử. Không thêm yêu cầu phải biết tên app gây PSI cũ vào AC sản phẩm.

Review độc lập tìm và đã kiểm delta sửa hai blocker: kiểm nhầm đường dẫn Windows venv với native image; deadline của foreground rò sang watchdog. Giữ kiểm logical/native executable, PID, creation time, nonce, exit và global/resource guard.64case offline đạt; helper Windows lành tính đo được hai PID khác nhau, retained handle ALIVE→EXITED, launcher exit0, không writer/API/lab. Wrapper và admission thêm4case, tổng68case.

**Rationale cần chấp nhận:** cho phép một lượt nghiệm thu nếu preflight mới đạt trong môi trường người dùng đã giải phóng, giữ nguyên guard trong cả lượt. Không tuyên bố PSI cũ đã được sửa hoặc không thể tái diễn. Mọi guard/failure/UNKNOWN vẫn chặn PASS. Đây là điều chỉnh quyết định GO hữu hạn sau điều tra, không giảm AC.

## Scope và trần thực thi

- HEAD9567830020954bf3f30fd5a74240747be0c8ec1c; Docker context desktop-linux; Kubernetes context k3d-zero-door/API127.0.0.1:7356. Chỉ namespace private zd-sqli-lab; bốn workload riêng trên k3d-zero-door-agent-0.
- Một attempt tối đa20phút, dành5phút cuối cleanup. Preflight25mẫu/120s, watchdog mỗi5s. Host/WSL available≥1GiB, memory PSI some avg10≤5. Dừng nếu guard, profile, cache hoặc inventory lệch.
- Không đổi tài nguyên, ngưỡng, DNS/CNI/frontend/Prometheus/WSL, không restart shared. Không tự đóng app hay kill tiến trình. Không chạy test/job nặng khác trong cửa sổ đo.
- **0build/import/pull**; imagePullPolicy Never, đúng cache artifact04 theo run_cached_fixture.py. Cache thiếu/lệch phải dừng. Namespace phải absent trước tạo; proxy/A/B khởi động tuần tự. Chỉ release fixture khi policy hook đúng Pod/IP/node và Ready.
- **≤29fixture HTTP +≤32Boutique observer HTTP**, tổng≤61HTTP; ≤2RPS, concurrency1 tính từ completion; ≤4TCP denial controls. Chỉ request catalog/order lành đã có, không payload mới, SQLi executor, tải hoặc mục tiêu ngoài local.
- Một block nguồnA đã xác minh qua trusted proxy, giữ catalog/CRUD nguồnB; giữ header-spoof và TCP isolation controls. Một TTL180s gốc, đúng1fixture Pod replacement và1writer restart (2process). Replay không renew hoặc đổi state/revision.
- Sáu pha active tối đa40/35/10/30/35/10s, tổng160s; reserve15s, còn5s overhead ban đầu. Mỗi pha bảo lưu các pha sau theo expiry gốc và dừng khi thiếu ngân sách. Old Pod UID-absence vẫn bắt buộc, kiểm trong khoảng TTL idle sau proof Pod mới/replay.
- Sau expiry gốc mới kiểm A200/B200+CRUD; expired record vẫn giữ nguyên. Cleanup phải thấy rules rỗng ở API và mounted digest, A/B200, hai actual writer exit proof; namespace UID-delete+absent và shared spec/UID/restart/3PVC nguyên. Không dùng reset thay expiry hoặc API accepted thay effect.
- Boutique vẫn observer trước/sau; lỗi business giữ riêng. Không R1/KPI/AI/end-to-end PASS. Gói này chỉ nghiệm thu component ZER-46; production pipeline/LLM ngoài quyền.

## Khóa nguồn và chạy

Entrypoint trong runtime-prep: run_acceptance.sh --execute. Cần acceptance-authorization.json APPROVED với hash exact proposal và acceptance-source-manifest.json; chưa tạo file approval. Source/path drift chặn trước tạo Lab. runtime-09/started.json hoặc acceptance.json tồn tại chặn replay. Snapshot source/script và authorization lưu trước actor. Một writer Codex, reviewer chỉ đọc.

## Điều kiện kết luận và dừng cuối

Full verifier phải đối chiếu raw:29HTTP/29joins đúng PodUID,4TCP denial, attribution/anti-spoof, block/benign sau fixture và writer restart, replay giữ nguyên, expiry/unblock, API+mount cleanup, hai actual writer exit proof, không guard/failure/unknown và shared preservation. Thiếu bằng chứng là NOT_MET.

Nếu lỗi: dừng, thực hiện cleanup trong reserve, giữ dispatch/partial/UNKNOWN; **không tự chạy attempt10 hoặc probe bổ sung**. Khép blocker cùng phần đạt/chưa đạt. Nếu đủ: chốt component AC observed/raw reconciled và trạng thái kỹ thuật sẵn sàng publication; vẫn cần review kết quả, merge và Hoàng acceptance trước Done. Không tự commit/push/merge hoặc đổi Linear Done.
