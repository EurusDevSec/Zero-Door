# 🚀 HƯỚNG DẪN TRIỂN KHAI CLOUD (PHASE 7 CLOUD DEPLOYMENT RUNBOOK)
> **Môi trường**: DigitalOcean Droplet (Ubuntu 22.04 LTS) + K3s  
> **Mục tiêu**: Deploy Zero Door stack lên môi trường Cloud thực tế với chi phí tối thiểu (~$6/tháng)  

---

## 1. Chuẩn bị Hạ tầng DigitalOcean Droplet

### 1.1. Khởi tạo Droplet (VM)
1. Đăng nhập vào DigitalOcean Control Panel.
2. Nhấn **Create** $\rightarrow$ **Droplets**.
3. Cấu hình chi tiết:
   * **Choose Region**: Chọn Singapore (`sgp1`) hoặc Bangalore (`blr1`) để có latency tốt nhất về Việt Nam.
   * **Choose an OS**: `Ubuntu 22.04 LTS (x64)`.
   * **Choose Size**: Chọn gói **Basic** $\rightarrow$ CPU Options chọn **Regular** $\rightarrow$ Chọn cấu hình **`$6/month (1 GB RAM / 1 vCPU / 25 GB SSD)`** hoặc tốt nhất là **`$12/month (2 GB RAM / 1 vCPU / 50 GB SSD)`** để đảm bảo Kafka + Prometheus + 3 Agents chạy không bị nghẽn RAM.
   * **Authentication**: Chọn **SSH Key** để kết nối bảo mật tuyệt đối.

### 1.2. Cấu hình DigitalOcean Cloud Firewall
Tạo một Firewall gắn vào Droplet và mở các cổng sau:

| Chiều (Direction) | Cổng (Port) | Giao thức (Protocol) | Mục đích (Purpose) | Nguồn (Source) |
|---|---|---|---|---|
| Inbound | `22` | TCP | Quản trị SSH | Chỉ cho phép từ IP cá nhân của bạn (My IP) |
| Inbound | `80` | TCP | HTTP Traffic (Ingress) | Internet công cộng (`0.0.0.0/0`) |
| Inbound | `443` | TCP | HTTPS Traffic (SSL Ingress) | Internet công cộng (`0.0.0.0/0`) |
| Inbound | `8080` | TCP | Cổng phụ (Ingress Target App) | Internet công cộng (`0.0.0.0/0`) |

---

## 2. Cài đặt K3s trên Droplet

SSH vào Droplet bằng IP công cộng (`<droplet-ip>`):

```bash
ssh root@<droplet-ip>
```

Chạy lệnh cài đặt K3s tối giản (đã tích hợp sẵn Traefik Ingress Controller mặc định):

```bash
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

Kiểm tra trạng thái cluster:

```bash
# Kubeconfig được tự động lưu tại /etc/rancher/k3s/k3s.yaml
kubectl get nodes
```
*Kết quả hiển thị node Droplet ở trạng thái `Ready` là thành công.*

---

## 3. Cấu hình Kéo Image từ GitHub Container Registry (GHCR)

Do các Docker images của Agents được đẩy lên repo cá nhân/tổ chức trên GHCR dưới dạng Private theo mặc định, bạn cần tạo một **ImagePullSecret** trên cụm K3s để kéo image về:

### 3.1. Tạo GitHub Personal Access Token (PAT)
1. Trên GitHub, vào **Settings** $\rightarrow$ **Developer Settings** $\rightarrow$ **Personal Access Tokens (classic)**.
2. Nhấn **Generate new token (classic)**.
3. Chọn các quyền: `read:packages`.
4. Copy token nhận được (ví dụ: `ghp_ABC123xyz...`).

### 3.2. Tạo Secret trên K3s Droplet
Chạy lệnh sau trên terminal của Droplet (thay thế thông tin tương ứng):

```bash
# Tạo Namespace trước
kubectl create namespace zero-door
kubectl create namespace target-app

# Tạo Secret kéo image trên cả 2 namespaces
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<TEN-TAI-KHOAN-GITHUB> \
  --docker-password=<GITHUB-PAT-TOKEN> \
  --docker-email=<EMAIL-CUA-BAN> \
  -n zero-door

kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<TEN-TAI-KHOAN-GITHUB> \
  --docker-password=<GITHUB-PAT-TOKEN> \
  --docker-email=<EMAIL-CUA-BAN> \
  -n target-app
```

---

## 4. Deploy Helm Stack lên Cloud

### 4.1. File cấu hình Cloud: `cloud-values.yaml`
Tạo file `infrastructure/helm/cloud-values.yaml` trên máy local để ghi đè các cấu hình local.

*Điểm khác biệt chính trên Cloud*:
*   Không dùng `imagePullPolicy: Never` (vì ta cần kéo từ internet).
*   Thêm `imagePullSecrets` trỏ đến `ghcr-secret`.
*   Cấu hình domain động dùng dịch vụ miễn phí `.nip.io` (ví dụ: `http://<droplet-ip>.nip.io`).

```yaml
global:
  environment: cloud
  imagePullSecrets:
    - name: ghcr-secret

# Cấu hình kéo image cụ thể cho từng Agent từ GHCR
gaia:
  image:
    repository: ghcr.io/eurusdevsec/zero-door/gaia
    tag: latest
    pullPolicy: Always

nemesis:
  image:
    repository: ghcr.io/eurusdevsec/zero-door/nemesis
    tag: latest
    pullPolicy: Always
  ingress:
    enabled: true
    hosts:
      - host: nemesis.<droplet-ip>.nip.io
        paths:
          - path: /
            pathType: ImplementationSpecific

hephaestus:
  image:
    repository: ghcr.io/eurusdevsec/zero-door/hephaestus
    tag: latest
    pullPolicy: Always

chaosWorker:
  image:
    repository: ghcr.io/eurusdevsec/zero-door/chaos-worker
    tag: latest
    pullPolicy: Always
```

### 4.2. Deploy lệnh từ máy Local
Để deploy từ máy local của bạn, tải file kubeconfig `/etc/rancher/k3s/k3s.yaml` từ Droplet về máy cá nhân, sửa IP `127.0.0.1` bên trong thành IP public của Droplet, sau đó chạy lệnh deploy:

```powershell
# Ví dụ download kubeconfig từ Droplet về máy local
scp root@<droplet-ip>:/etc/rancher/k3s/k3s.yaml ~/.kube/config-do

# Chạy deploy sử dụng Helm trỏ vào file config cloud
$env:KUBECONFIG="$HOME/.kube/config-do"
helm upgrade --install zero-door ./infrastructure/helm/zero-door \
  -f ./infrastructure/helm/cloud-values.yaml \
  -n zero-door
```

---

## 5. Verify & So sánh Hiệu năng

Sau khi deploy hoàn tất, hãy truy cập các đường dẫn sau để xác nhận:
*   **Target App**: `http://<droplet-ip>:8080/`
*   **Nemesis Dashboard**: `http://nemesis.<droplet-ip>.nip.io/`

Chạy lại kịch bản kiểm thử (Scenarios 1-4) và ghi nhận MTTD, MTTR để so sánh với kết quả chạy local K3d trước đó, hoàn thành báo cáo Chương 5 trong luận văn NCKH.
