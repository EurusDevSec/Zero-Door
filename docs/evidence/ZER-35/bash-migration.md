# Chuyển công cụ vận hành sang Bash

## Yêu cầu và phạm vi trước sửa

Ngày 18/10/2026, Hoàng yêu cầu thay toàn bộ script PowerShell trong repo và các hướng dẫn/caller liên quan sang Bash. Đây là maintenance được người dùng trực tiếp cho phép; hỗ trợ ZER-35, không phải xác nhận toàn bộ lab hoàn tất hoặc quyền triển khai.

HEAD trước sửa: `1f43ff1461c2199bc99e9962483956c3df0fa975`, branch main. Dirty đã có và giữ lại: NOW.md, local-lab.md, docs/evidence/ (inventory, cluster baseline).

Phạm vi: thay 7 script `.ps1` bằng `.sh` cùng tên gốc; thêm thư viện `infrastructure/scripts/lib/common.sh`, requirements thực nghiệm, kiểm thử CLI mock dưới `tests/shell/`, hướng dẫn `docs/runbooks/bash-tooling.md`, kiểm tra Bash trong CI và quy tắc LF trong .gitattributes. Cập nhật README, AGENTS, .agent/QUICK_START.md, .agent/rules/{CONTEXT,PLAN,LESSONS_LEARNED}.md, .agent/workflows/session_memory.md, docs/demo_script.md, các runbook phase1–7/legacy-demo-restart, thông báo mất kết nối trong agent-orchestrator/nemesis/static/app.js, docs/research/chapter4.md, delivery/reference/audit-findings.md, delivery/milestones/R0-foundations/local-lab.md và NOW.md. Các archive/handoff/review/evidence cũ có tên script lịch sử sẽ được ghi rõ provenance và dẫn bản Bash hiện hành; không thay sự kiện/claim nguồn thành hành vi mới.

Không chạy setup thật, build/import image, rollout, reset/attack/heal, xóa cluster/volume, cài dependency toàn máy, gọi model/cloud, commit/push hoặc đổi metadata Linear. Kiểm chứng: bash -n, --help không có side effect, CLI mock về context/failure/cleanup/Secret/explicit flags, rà tham chiếu và diff. Runtime dựng đủ lab nằm ngoài phiên chuyển đổi.

## Kết quả kiểm chứng và bàn giao

- 7 entry point Bash thay 7 script PowerShell; không còn file `.ps1/.psm1/.psd1` trong working tree của repo (không tính Git history). deploy.sh đã là Bash cho cloud và không được chạy/sửa trong phiên.
- `bash -n` qua toàn bộ 10 file shell hiện có: 7 entry point mới, thư viện common, test runner và deploy.sh cũ. 85 khối lệnh Bash trong tài liệu đã kiểm tra cú pháp riêng (placeholder `<pod-name>`/`<namespace>` thay bằng token ví dụ chỉ cho bước phân tích cú pháp; không thực thi nội dung).
- `node --check agent-orchestrator/nemesis/static/app.js`: PASS. Chỉ đổi chuỗi hướng dẫn trong showConnectionWarning; không đổi luồng reset/attack/metric. GitNexus impact báo HIGH do hàm này được nhiều flow dùng; đã giới hạn diff ở chuỗi thông báo và đối chiếu nguồn trực tiếp.
- `bash tests/shell/run.sh`: **21 nhóm kiểm thử offline PASS**, dùng CLI giả lập và checkout tạm có dấu cách. Bao phủ --help không side effect, cờ xác nhận xóa đúng cluster, build/rollout/Helm lỗi, malformed inventory, context/cluster/image, bảo toàn Secret/không coi lỗi API là Secret vắng, RBAC mismatch, localhost backup/custom KUBECONFIG, process ownership/port collision, phase5 mặc định không cài/attack, tham số smoke và Python wrapper cách ly CSV/context bằng fixture vô hại. Không dùng test fixture như số liệu nghiên cứu.
- Native Windows smoke: dùng thư viện common mở đúng một tunnel `kube-system/svc/kube-dns`, bind `127.0.0.1:15853`, xác minh TCP kết nối được; cleanup rồi xác minh cổng không còn nghe. Output: `NATIVE_FORWARD_OPEN: 127.0.0.1:15853`, `NATIVE_FORWARD_CLOSED: cleanup verified`, exit 0. Không thay tài nguyên Kubernetes. Đây là phép thử native kubectl/process cleanup, không là full demo.
- Rà cú pháp PowerShell trong hướng dẫn hiện hành: không còn fence powershell/cmdlet/$env/ExecutionPolicy. Tên cũ chỉ giữ trong provenance, audit/archive/ảnh cũ và ghi chú migration. Những khối gợi ý lệnh trong hai handoff được dịch sang Bash, có ngày cập nhật; dữ kiện lịch sử khác không được đổi thành kết quả hiện tại.
- CI có job kiểm tra Bash syntax + offline tests và là prerequisite của job publish-images. CI chưa chạy trên GitHub trong phiên; local dùng Git Bash 5.2.26. ShellCheck không có trong PATH và chưa được cài/chạy. .gitattributes giữ LF cho shell; .gitignore bổ sung venv thực nghiệm. docs/README thêm điểm vào Bash.

## Khác biệt hành vi cần biết

- Port-forward chạy foreground và dọn child thuộc session, không kill mọi kubectl hoặc tiến trình đang chiếm cổng. API/tunnel/rollout lỗi trả mã lỗi. Health HTTP không được gọi là khôi phục nghiệp vụ.
- Mọi kubectl/Helm trong entry point local chỉ định context ZERO DOOR; đường dẫn host được đổi bằng cygpath trên Windows, giữ nguyên đối số container.
- setup-phase1 có --component để dựng/đo từng nhóm; cấu hình tài nguyên/chart legacy chưa được tối ưu hay pin thêm version trong refactor này.
- setup-phase3 giữ Secret có sẵn, không chạy go mod tidy; setup3/4 restart deployment sau apply để image latest vừa import được dùng trong rollout mới.
- setup-phase5 mặc định không install/attack; install-deps dùng venv riêng. run-smoke là lựa chọn riêng, runner legacy được bọc để output vào scratch/experiments và child kubectl chỉ thấy context đã chọn. Không tự chạy analysis lên CSV cũ. Các lỗi/giới hạn nghiên cứu của runner vẫn còn.
- recreate phải có --confirm-delete-zero-door; chỉ dựng lại hạ tầng, không tự khôi phục app/agent/dữ liệu. Không chạy nhánh đó trên cluster thật trong phiên.

## Giới hạn và bước tiếp theo

GitNexus MCP query/context/impact/detect_changes hoạt động, nhưng index còn ở `6337b31`, sau HEAD hiện tại 2 commit. Đã thử `gitnexus analyze --index-only`: lần đầu không có tiến triển sau banner và được dừng; lần sau đặt riêng env Git tắt fsmonitor và timeout 40s, kết thúc exit 124. Không xóa lock/index hoặc bật embeddings; chưa xác định nguyên nhân. Graph chỉ dùng định vị/impact của thông báo JS; không coi detect_changes là coverage đủ cho các file Bash mới/untracked. Rà `rg`, đọc script trực tiếp và kiểm thử là căn cứ chính cho chuyển đổi này. Cần làm mới index trong phiên xử lý công cụ riêng trước khi dựa vào graph của code mới.

Chưa kiểm chứng full chart/image pull, build/import, rollout stack thật, các endpoint app đầy đủ, RBAC thật sau deploy, broker advertised listeners hoặc LLM. Không thực hiện attack/heal/reset, cloud, cài gói toàn máy, commit/push/merge hay thay field/AC Linear. Các AC Linear đang nhắc tên .ps1 là snapshot trước refactor; ghi chú issue dẫn đối chiếu Bash, không tự sửa nguồn AC sống. Tiếp tục review diff rồi khôi phục từng nhóm workload theo ZER-35, giữ baseline cluster và giao dịch/probe làm bằng chứng riêng.

Kiểm tra cuối: `git diff --check` PASS; CI YAML parse bằng PyYAML PASS, job bash-tooling nằm trong needs của publish-images. File shell mới không CRLF/BOM, không trailing whitespace; source không còn script PowerShell. Probe/snippet tạm do phiên này tạo đã được dọn sau kiểm tra, không xóa dữ liệu có trước.
