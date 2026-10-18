# ZER-35 — Cluster nền và sửa endpoint local

## Phạm vi và revision

- Kiểm tra ngày 18/10/2026, 09:58–10:00, Asia/Saigon (+07:00).
- [ZER-35](https://linear.app/zero-door/issue/ZER-35/khoi-phuc-lab-tu-inventory-dja-kiem-chung), AC đọc lại trong phiên này.
- HEAD `1f43ff1461c2199bc99e9962483956c3df0fa975`, branch main.
- Dirty đầu phiên: `docs/delivery/NOW.md`, `docs/delivery/milestones/R0-foundations/local-lab.md`, `docs/evidence/` từ phiên inventory. Giữ nguyên phần trước đó.
- Hoàng cho biết đã chạy `k3d cluster create --config ./infrastructure/k3d-config.yaml`; Codex không chạy lại hoặc xóa cluster.
- Thao tác môi trường: kiểm tra chỉ đọc, sao lưu kubeconfig và sửa duy nhất server endpoint của entry `k3d-zero-door`. Không triển khai workload, sửa WSL, restart Docker, xóa dữ liệu, gọi model hoặc chạy thực nghiệm.
- Phạm vi repo: artifact này, nối bàn giao vào `local-lab.md` và checkpoint `NOW.md`. Probe Bash tạm trong scratch được xóa sau kiểm tra. Không sửa mã ứng dụng hoặc manifest.

## Lỗi tái hiện và đối chiếu

Git Bash 5.2.26, Docker context `desktop-linux`. `KUBECONFIG` không được đặt; CLI dùng file mặc định của tài khoản ACER.

```bash
k3d cluster list
kubectl --context k3d-zero-door get nodes --request-timeout=10s
docker stats --no-stream
docker port k3d-zero-door-serverlb 6443/tcp
```

- `k3d cluster list`: `zero-door`, server `1/1`, agent `1/1`, load balancer `true`.
- `kubectl` lỗi connection refused tới `https://host.docker.internal:7356`, hostname resolve thành `192.168.1.4`.
- Docker publish cổng API: `0.0.0.0:7356` → `6443/tcp` của serverlb.
- Thử cùng context với `--server=https://127.0.0.1:7356` thành công: hai node Ready, ba pod hệ thống Running. Không tắt kiểm tra TLS.
- `docker stats --no-stream` thành công trong các lần kiểm tra của Codex. Chưa tái hiện được lỗi lệnh này mà Hoàng báo; không kết luận lỗi terminal của Hoàng đã được giải quyết.

Đã chứng minh endpoint localhost truy cập được trong khi endpoint hostname bị từ chối. Chưa xác định vì sao kubeconfig được tạo với hostname này; không suy thành cluster hỏng hoặc cần recreate.

## Sửa và xác minh

Lúc 10:00:24–10:00:29, sao lưu bằng `cp -p`, xác minh tên cluster rồi đổi server:

```bash
task_kubeconfig="$HOME/.kube/config"
task_cluster=$(kubectl --kubeconfig="$task_kubeconfig" --context=k3d-zero-door \
  config view --minify -o 'jsonpath={.clusters[0].name}')
[[ "$task_cluster" == k3d-zero-door ]] || exit 1
task_backup="$task_kubeconfig.zero-door-backup-$(date +%Y%m%dT%H%M%S)"
cp -p -- "$task_kubeconfig" "$task_backup"
kubectl --kubeconfig="$task_kubeconfig" config set-cluster "$task_cluster" \
  --server=https://127.0.0.1:7356
```

Backup thực tế: `C:/Users/ACER/.kube/config.zero-door-backup-20261018T100026`. Chỉ giữ local, không đưa nội dung kubeconfig/credential vào repo. Cổng 7356 là mapping của cluster hiện tại; khi tạo cluster khác phải kiểm kê lại, không dùng như hằng số chung.

Lệnh sửa dùng [`kubectl config set-cluster`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/kubectl_config_set-cluster/), chỉ định trường server của entry có tên đã đối chiếu.

Sau sửa, chạy không có override `--server`:

```bash
kubectl --context k3d-zero-door get nodes -o wide --request-timeout=10s
kubectl --context k3d-zero-door get pods -A --request-timeout=10s
kubectl --context k3d-zero-door top nodes --request-timeout=10s
kubectl --context k3d-zero-door top pods -A --request-timeout=10s
docker stats --no-stream
```

Tất cả exit 0. Hai node `k3d-zero-door-server-0`, `k3d-zero-door-agent-0` Ready, K3s `v1.31.5+k3s1`; CoreDNS, local-path-provisioner, metrics-server đều `1/1 Running`, restart 0. Chưa có namespace/workload ZERO DOOR trong kết quả pods.

## Mốc tài nguyên

Docker stats lúc khoảng 10:00:29:

| Container | CPU % | Memory usage |
| --- | ---: | ---: |
| k3d-zero-door-server-0 | 2.92 | 384.5 MiB |
| k3d-zero-door-agent-0 | 0.86 | 131.5 MiB |
| k3d-zero-door-serverlb | 0.00 | 7.777 MiB |
| k3d-zero-door-tools | 0.00 | 2.477 MiB |

Tổng usage hiển thị khoảng **526.3 MiB**, không bao gồm toàn bộ Docker Desktop/WSL/host/file cache. Limit 6.772 GiB ở mỗi dòng là trần môi trường hiển thị, không cộng thành RAM riêng được cấp cho từng container. Mẫu Docker trước đó khoảng 525 MiB và lúc khởi động khoảng 574 MiB; đây là mẫu ngắn, chưa là benchmark ổn định lâu dài.

`kubectl top nodes`: agent 61m CPU/131Mi, server 50m CPU/384Mi. `top pods`: CoreDNS 2m/14Mi, provisioner 1m/7Mi, metrics-server 4m/18Mi. Không cộng các pod này thêm vào usage node/container vì có thể đếm trùng; các công cụ khác nhau có thời điểm và cách hạch toán khác nhau.

## Verdict, giới hạn và tiếp theo

- PASS: cluster nền tồn tại; API truy cập bằng cấu hình đã sửa; node/pod hệ thống sẵn sàng ở thời điểm kiểm tra; có mốc tài nguyên để đối chiếu.
- Chưa đủ kết luận toàn bộ ZER-35 hoặc ZER-6 hoàn tất: chưa khôi phục dependency, agent, Boutique và chưa kiểm chứng Kafka/metric/log/luồng mua hàng.
- Chưa chứng minh tối ưu tổng thể hoặc khả năng chạy đầy đủ trên RAM 16GB. Cần chốt profile tài nguyên và thêm từng nhóm workload, đo chênh lệch so với baseline này.
- Nếu `docker stats --no-stream` vẫn lỗi ở terminal của Hoàng, cần nguyên văn lỗi và đường dẫn lệnh được resolve ở chính terminal đó; không có bằng chứng để tự sửa PATH/Docker vì giả thuyết.
- Không commit/push, cập nhật trạng thái Linear hoặc tự coi artifact local là đã được reviewer chấp nhận.
