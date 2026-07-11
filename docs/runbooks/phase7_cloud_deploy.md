# Phase 7 — Cloud Deploy Runbook (Terraform + deploy.sh IaC)

> **Phiên bản:** v2.0 — IaC approach (Terraform + cloud-init)
> **Cập nhật:** 2026-07-11
> **Môi trường:** DigitalOcean Droplet — Ubuntu 22.04 LTS, 4vCPU/8GB RAM/160GB SSD
> **K8s Engine:** K3s v1.36.2+k3s1 (Nginx Ingress, không dùng Traefik)

---

## Tóm tắt Kiến trúc

```
[Terraform: main.tf]
    │
    ├── digitalocean_droplet   → Droplet 4vCPU/8GB (sgp1)
    ├── digitalocean_firewall  → Port 22 (SSH) + 80/443 (HTTP/HTTPS) | 6443 ĐÓNG
    └── digitalocean_ssh_key   → Upload public key
              │
              └── user_data: cloud-init.yaml
                        │
                        └── Tự động khi Droplet boot:
                            1. Clone repo từ GitHub
                            2. GITHUB_PAT=xxx bash deploy.sh

[deploy.sh] — chạy bên trong Droplet:
    ├── Cài K3s --disable traefik
    ├── Symlink kubeconfig (~/.kube/config)
    ├── Cài Helm
    ├── Tạo namespaces + ghcr-secret
    ├── Cài Nginx Ingress Controller
    ├── Helm: Prometheus + Grafana
    ├── Helm: Kafka KRaft
    ├── kubectl apply: ResourceQuotas
    ├── kubectl apply: Target App (Boutique)
    ├── python3 patch_manifests.py → /tmp/manifests-cloud/
    ├── kubectl apply: Agents (Nemesis, Gaia, Hephaestus, Chaos)
    └── Verify endpoints: HTTP 200 ✅
```

---

## Bài học từ Deploy Lần 1 (QUAN TRỌNG)

| Lỗi đã gặp | Nguyên nhân | Giải pháp trong v2 |
|---|---|---|
| `kubectl` từ local timeout | DO Firewall chặn port 6443 | Deploy 100% từ bên trong Droplet, port 6443 luôn đóng |
| PowerShell heredoc/escaping | Bash code truyền qua SSH bị parse | Tất cả script viết vào `.sh` file — không inline bash qua SSH |
| `gaia` image sai | Manifest dùng `zero-door/gaia:latest` + `Never` | `patch_manifests.py` xử lý riêng case này |
| Helm không tìm kubeconfig | `~/.kube/config` chưa symlink | `deploy.sh` tạo symlink ngay đầu script |
| Traefik conflict với Nginx | K3s default bật Traefik | Cài K3s với `--disable traefik` từ đầu |
| `sed` regex không portable | Bash `sed` phức tạp | Dùng Python `re.sub` trong `patch_manifests.py` |

---

## Cấu trúc File

```
infrastructure/
├── terraform/
│   ├── main.tf                  ← Droplet + Firewall + SSH key
│   ├── variables.tf             ← Các biến cấu hình
│   ├── outputs.tf               ← In ra IP và URLs sau deploy
│   ├── cloud-init.yaml          ← Auto-run deploy.sh khi boot
│   └── terraform.tfvars.example ← Template (COPY → terraform.tfvars)
│
└── scripts/
    ├── deploy.sh                ← Script deploy toàn bộ stack
    └── patch_manifests.py       ← Patch GHCR image + imagePullSecrets
```

---

## Prerequisites (Làm 1 lần)

### 1. Cài Terraform trên máy Windows
```powershell
# Dùng Chocolatey (nếu đã cài choco):
choco install terraform -y

# Hoặc tải trực tiếp:
# https://developer.hashicorp.com/terraform/install
terraform version  # verify: >= 1.0
```

### 2. Cài OpenSSH và tạo SSH key (nếu chưa có)
```powershell
# Kiểm tra key đã tồn tại chưa
ls ~/.ssh/id_rsa.pub

# Nếu chưa có, tạo mới:
ssh-keygen -t rsa -b 4096 -C "zero-door-deploy"
```

### 3. Lấy DigitalOcean API Token
1. Vào [https://cloud.digitalocean.com/account/api/tokens](https://cloud.digitalocean.com/account/api/tokens)
2. Click **Generate New Token**
3. Token Name: `zero-door-terraform`
4. Expiration: 90 days
5. Scope: **Full Access**
6. Click **Generate Token** → Copy ngay (chỉ hiện 1 lần!)

### 4. Tạo terraform.tfvars
```powershell
cd r:\_Projects\Eurus_Workspace\zero_door\infrastructure\terraform
Copy-Item terraform.tfvars.example terraform.tfvars
# Mở terraform.tfvars và điền do_token + github_pat
```

---

## Quy trình Deploy (Từ đầu → Xong)

### Bước 1: Init Terraform
```powershell
cd r:\_Projects\Eurus_Workspace\zero_door\infrastructure\terraform
terraform init
```

### Bước 2: Preview những gì sẽ tạo
```powershell
terraform plan
# Review: 1 Droplet + 1 Firewall + 1 SSH Key
```

### Bước 3: Deploy! (1 lệnh)
```powershell
terraform apply
# Xác nhận bằng cách gõ "yes"
# Terraform sẽ in ra IP sau khi tạo xong
```

### Bước 4: Theo dõi quá trình deploy
```powershell
# Lấy IP từ output
$IP = terraform output -raw droplet_ip

# Theo dõi log deploy trên Droplet (cloud-init chạy deploy.sh)
ssh root@$IP "tail -f /var/log/zero-door-deploy.log"

# Quá trình mất khoảng 5-8 phút
```

### Bước 5: Verify
```powershell
$IP = terraform output -raw droplet_ip

curl.exe http://$IP/                              # Boutique → 200 OK
curl.exe http://$IP/nemesis/healthz               # {"status":"UP"}
curl.exe http://$IP/nemesis/dashboard/            # Dashboard HTML
curl.exe http://$IP/hephaestus/healthz            # {"status":"UP"}
```

---

## Quy trình Destroy & Rebuild

```powershell
# Xóa toàn bộ (Droplet + Firewall + SSH Key)
terraform destroy

# Rebuild từ đầu (Droplet mới, IP mới)
terraform apply
```

---

## Các Lệnh Quản trị Thường dùng

```bash
# SSH vào Droplet
ssh root@$(terraform output -raw droplet_ip)

# Xem tất cả pods
kubectl get pods -A

# Xem logs agent
kubectl logs -n zero-door -l app=nemesis -f
kubectl logs -n zero-door -l app=hephaestus -f
kubectl logs -n zero-door -l app=gaia -f

# Port-forward Grafana (từ máy local)
ssh -L 3000:localhost:3000 root@$(terraform output -raw droplet_ip) \
  "kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
# Mở: http://localhost:3000 (admin / zerodoor123)

# Port-forward Prometheus
ssh -L 9090:localhost:9090 root@$(terraform output -raw droplet_ip) \
  "kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring"
# Mở: http://localhost:9090

# Restart một agent
kubectl rollout restart deployment/nemesis -n zero-door

# Xem ingresses
kubectl get ingress -A

# Xem deploy log
cat /var/log/zero-door-deploy.log
```

---

## Ghi chú Kỹ thuật

### Tại sao không mở port 6443?
K8s API port (6443) bị giữ đóng trên Cloud Firewall. Đây là **security best practice**. Tất cả thao tác kubectl/helm thực hiện trực tiếp trên Droplet qua SSH. Không cần port-forward hay VPN.

### Tại sao không dùng Traefik?
Tất cả manifest dùng `ingressClassName: nginx` và annotations `nginx.ingress.kubernetes.io/*`. Nginx Ingress giữ nguyên 100% compatibility.

### Klipper LoadBalancer
K3s built-in Klipper LB tự động map port 80/443 của host → `ingress-nginx-controller` (type: LoadBalancer). Không cần mua external DO Load Balancer (~$12/tháng).

### gaia-deployment.yaml đặc biệt
File này dùng `image: zero-door/gaia:latest` (KHÁC với các agent khác `gaia:latest`) và `imagePullPolicy: Never`. `patch_manifests.py` có logic riêng để xử lý case này.

### emailservice CrashLoopBackOff
`emailservice` của Google Boutique dùng Python gRPC với startup chậm. **Không ảnh hưởng tới Zero-Door system**. Frontend vẫn `200 OK`.
