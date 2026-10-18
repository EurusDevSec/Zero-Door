# ZERO DOOR — Bắt đầu một phiên

Điểm vào hiện hành: `docs/delivery/README.md` → `docs/delivery/NOW.md` → issue Linear và ghi chú kỹ thuật tương ứng. SCOPE giữ cam kết nghiên cứu; WORKFLOW giữ quy tắc phối hợp/QA. Các ghi chú tháng 7 chỉ là lịch sử, không chứng minh lab hay KPI hiện tại.

Dùng Bash (Git Bash trên Windows). Hướng dẫn đầy đủ: [Bash tooling](R:/_Projects/Eurus_Workspace/zero_door/docs/runbooks/bash-tooling.md).

## Kiểm tra chỉ đọc

```bash
git status --short
git log --oneline -5
docker context show
docker ps
k3d cluster list
kubectl --context k3d-zero-door get nodes --request-timeout=10s
kubectl --context k3d-zero-door get pods -A
docker stats --no-stream
```

Xem READY, restart, Events và luồng nghiệp vụ; Running riêng lẻ chưa chứng minh hệ thống hoạt động. Lệnh lỗi không được coi là inventory rỗng.

## Mở dashboard của lab đã có

```bash
bash start-demo.sh
```

Giữ terminal mở. Ctrl+C chỉ dừng tunnel do lần chạy này tạo. Cổng bận: dừng đúng terminal cũ hoặc tự kiểm tra tiến trình, không kill toàn bộ kubectl. Script không tạo cluster/deploy dịch vụ.

## Các thao tác có thay đổi môi trường

Chỉ chạy khi issue/scope và người dùng đã cho phép tương ứng; các ví dụ không tự cấp quyền.

```bash
# Rebuild Nemesis, import image và rollout; không mở tunnel mới
bash rebuild-nemesis.sh --no-forward

# Health/HTTP port-forward phục vụ công cụ thực nghiệm; không tự chạy attack
bash infrastructure/scripts/setup-phase5.sh
```

`--run-smoke` là lựa chọn riêng cho legacy E1; dữ liệu tách trong scratch, không phải dataset chính thức. Không tự chạy runner/reset/analysis để kiểm tra sức khỏe. LLM credential/provider/chi phí vẫn cần quyết định ở issue tương ứng.

## Nguyên tắc

- Python FastAPI cho các agent, Go cho worker; không thêm lại Java/Maven.
- Mọi lệnh Kubernetes/Helm local phải chỉ rõ context ZERO DOOR.
- Build lỗi hoặc rollout timeout là lỗi; không suy thành thành công từ dòng log DONE.
- Direct runner/inject alert bỏ qua một phần vòng thật; không dùng làm bằng chứng Gaia phát hiện.
- GitNexus hỗ trợ định vị; nguồn trực tiếp và runtime evidence mới quyết định kết luận.
