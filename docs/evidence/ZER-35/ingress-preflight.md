# ZER-35 — Ingress preflight: chọn controller cho lab local

**Cập nhật 18/10/2026 14:40: Hoàng chọn B (Traefik).** Gói phạm vi, patch và kế hoạch triển khai chờ Codex review nằm ở [traefik-migration.md](traefik-migration.md). Phần còn lại của file là bản preflight gốc, giữ nguyên để đối chiếu. Phát hiện bổ sung: `frontend-external` (LoadBalancer) đang giữ port 80 của node, nên phương án A cũng sẽ vướng.

**Trạng thái gốc: chờ Hoàng quyết định một câu hỏi (mục 5).** Chưa cài controller nào. `chart-versions.yaml` để trống `ingress-nginx`, nên `setup-phase1.sh --component ingress` dừng có chủ ý. Nhánh `all` bỏ qua ingress kèm cảnh báo. Các nhóm khác của ZER-35 vẫn dựng tiếp; Boutique được probe qua port-forward loopback. Probe loopback **không** chứng minh đường ingress hoạt động.

Người viết: Claude Code, 18/10/2026 (+07:00). Người review: Codex. Người quyết định: Hoàng.

## 1. Nguồn và vòng đời

- Theo [Kubernetes blog 11/11/2025](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/), Ingress NGINX chỉ được bảo trì best-effort tới 03/2026. Sau đó không còn release, bugfix hay bản vá bảo mật. Deployment cũ vẫn chạy và artifact vẫn tải được.
- [Tuyên bố của Steering/SRC 29/01/2026](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) nói rằng tiếp tục dùng sau khi dự án dừng là chịu rủi ro bảo mật. Bài cũng nói không có lựa chọn thay thế nào drop-in.
- Index chart upstream (đọc 18/10/2026 qua Helm home riêng trong `scratch/`):

| Chart | Controller | Ngày tạo | kubeVersion |
| --- | --- | --- | --- |
| 4.15.1 (mới nhất) | 1.15.1 | 2026-03-19 | `>=1.21.0-0` |
| 4.15.0 | 1.15.0 | 2026-03-09 | `>=1.21.0-0` |

  Như vậy 4.15.1 là bản cuối, phát hành trước mốc dừng bảo trì.
- Chart `ingress-nginx-4.15.1.tgz` có SHA-256 `3eff0bd18151d6e6b1c441463410571443dda1ac78292cb189346628de784f0c`. Image upstream `registry.k8s.io/ingress-nginx/controller:v1.15.1` đọc được manifest.
- Lab dùng K3s `v1.31.5+k3s1`, nằm trong khoảng kubeVersion của chart. Điều này chưa chứng minh controller chạy đúng runtime.

## 2. Yêu cầu thực tế trong repo (không chỉ annotation legacy)

| Phụ thuộc | Vị trí | Ý nghĩa nghiên cứu |
| --- | --- | --- |
| Metric `nginx_ingress_controller_requests` và `nginx_ingress_controller_request_duration_seconds_bucket` | `agent-orchestrator/gaia/main.py:202-224`; `agent-orchestrator/nemesis/main.py:194-195`; `infrastructure/manifests/prometheus-rules.yaml:34,54` | Gaia dùng để phát hiện tỷ lệ lỗi và độ trễ, tức tín hiệu của vector DDoS tầng ứng dụng. Nemesis dùng để đọc RPS và tỷ lệ lỗi |
| `ingressClassName: nginx`, annotation `nginx.ingress.kubernetes.io/rewrite-target` và `use-regex` | `target-app-ingress.yaml:9`; `nemesis-deployment.yaml:135-138`; `hephaestus-deployment.yaml:178-181` | Định tuyến Boutique và hai dashboard tác tử |
| Port K3d `8080:80`, `8443:443` trên loadbalancer | `infrastructure/k3d-config.yaml:14-20` | Đường truy cập từ host; không đổi trong gói này |
| Values: admission webhook tắt; access log JSON; `enable-real-ip: "false"` | `helm-values/ingress-nginx-values.yaml:21-25` | Log truy cập đi vào Fluent Bit → Elasticsearch. Gaia tìm chuỗi SQLi trong field `message` của mọi container (`gaia/main.py:288-292`) |
| WAF (ModSecurity) | Không có trong repo | Không phải yêu cầu hiện hành |

Phát hiện thêm: values hiện **không bật** `controller.metrics`, nên chart không tạo Service/ServiceMonitor metric (đã kiểm bằng render 4.15.1). Kể cả khi cài nguyên trạng, Prometheus cũng chưa có `nginx_ingress_controller_*`; các query trên sẽ rỗng. Muốn có tín hiệu thì phải bật `controller.metrics.enabled` và `serviceMonitor` trong values.

Values hiện dùng image mirror `docker.io/dyrnq/ingress-nginx-controller:v1.15.1`, không rõ nguồn. Phương án nào cũng nên dùng image upstream.

## 3. Render ứng viên legacy (không cài)

`helm template` chart 4.15.1 với values repo, namespace `kube-system`, kube-version 1.31.5, exit 0. Kết quả gồm:
- 1 Deployment `ingress-nginx-controller`: request 50m / 90Mi, limit 300m / 150Mi;
- ConfigMap, Service `LoadBalancer`, ServiceAccount, Role/RoleBinding trong `kube-system`;
- cluster-scoped: ClusterRole, ClusterRoleBinding, IngressClass `nginx`.

Không có hook hay Job. `kube-system` không có ResourceQuota, nên quota `monitoring` không áp cho controller. Render không chứng minh admission hay runtime.

## 4. Hai phương án

| | A. Legacy cố định: ingress-nginx 4.15.1 / controller 1.15.1 | B. Controller còn bảo trì: Traefik v3 (chart `traefik/traefik` 42.0.0, app v3.7.14) cài bằng Helm vào `kube-system`, không bật lại Traefik built-in của K3s |
| --- | --- | --- |
| Vòng đời | Không còn bản vá từ 03/2026. Chấp nhận được cho lab local loopback, không phơi ra mạng ngoài; phải ghi là giới hạn của nghiên cứu | Đang được bảo trì; là controller mặc định của K3s |
| File phải đổi | `chart-versions.yaml` (pin 4.15.1); `ingress-nginx-values.yaml` (image upstream, bật metrics + ServiceMonitor) | Values Traefik mới; thêm chart vào `chart-versions.yaml` và một nhánh trong `setup-phase1.sh`; 3 Ingress đổi class và đổi rewrite sang Middleware CRD; `prometheus-rules.yaml`; **query trong `gaia/main.py` và `nemesis/main.py`** (metric `traefik_service_requests_total` và `traefik_service_request_duration_seconds_bucket`, label khác) |
| Hành vi | Giữ nguyên tên metric, annotation và định dạng log mà Gaia/Nemesis đang dùng | Tên metric, label `service` và định dạng access log khác. Ngưỡng và cách tính error rate/latency của Gaia phải được kiểm lại |
| Khối lượng | Nhỏ: 2 file trong allowlist, sau đó cài và kiểm | Lớn hơn và **vượt allowlist** (sửa logic agent Python), ảnh hưởng tín hiệu nghiên cứu DDoS; cần issue/scope riêng |
| Rủi ro | Bảo mật dài hạn; lệch với khuyến nghị upstream | Tốn công hơn; có thể đổi kết quả đo so với dữ liệu lịch sử |

**Khuyến nghị của Claude: A cho lab local hiện tại**, dùng image upstream và bật metrics. Ghi rõ là legacy, chỉ dùng loopback, và đưa việc chuyển sang controller còn bảo trì (B hoặc Gateway API) vào một issue nghiên cứu riêng. Không tự mở rộng gói này thành migration.

## 5. Câu hỏi duy nhất cho Hoàng

**Chọn A (pin ingress-nginx 4.15.1 legacy, image upstream, bật metrics, chỉ dùng local) hay B (chuyển sang Traefik v3 qua một issue riêng, tạm không có ingress trong ZER-35)?**

Nếu chọn A, Claude sẽ:
1. sửa `chart-versions.yaml` và `ingress-nginx-values.yaml`;
2. chạy `bash infrastructure/scripts/setup-phase1.sh --component ingress`;
3. apply `target-app-ingress.yaml`;
4. probe `http://127.0.0.1:8080/` và kiểm metric `nginx_ingress_controller_requests` có dữ liệu.

Rollback theo ownership: chỉ release `ingress-nginx` trong `kube-system` do lượt đó tạo, và chỉ khi Hoàng duyệt.
