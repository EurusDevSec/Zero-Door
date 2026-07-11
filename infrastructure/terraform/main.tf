terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.0"
}

# ── Provider ────────────────────────────────────────────────────────────────
provider "digitalocean" {
  token = var.do_token
}

# ── SSH Key ─────────────────────────────────────────────────────────────────
resource "digitalocean_ssh_key" "zero_door" {
  name       = "zero-door-key"
  public_key = file(var.ssh_public_key_path)
}

# ── Droplet ─────────────────────────────────────────────────────────────────
resource "digitalocean_droplet" "zero_door" {
  name     = "zero-door-k3s"
  region   = var.region
  size     = var.droplet_size   # s-4vcpu-8gb (~$48/tháng)
  image    = "ubuntu-22-04-x64"
  ssh_keys = [digitalocean_ssh_key.zero_door.fingerprint]

  # cloud-init: tự động chạy deploy.sh khi Droplet boot lần đầu
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    github_pat    = var.github_pat
    deploy_script = base64encode(file("${path.module}/../scripts/deploy.sh"))
    patch_script  = base64encode(file("${path.module}/../scripts/patch_manifests.py"))
  })

  tags = ["zero-door", "k3s", "research"]

  lifecycle {
    create_before_destroy = true
  }
}

# ── Cloud Firewall ───────────────────────────────────────────────────────────
resource "digitalocean_firewall" "zero_door" {
  name = "zero-door-firewall"

  droplet_ids = [digitalocean_droplet.zero_door.id]

  # Inbound: SSH chỉ cho IP cá nhân (hoặc 0.0.0.0/0 nếu không biết IP)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.allowed_ssh_ips
  }

  # Inbound: HTTP công khai (Boutique + Dashboard)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Inbound: HTTPS (tương lai nếu cần Let's Encrypt)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Bài học: KHÔNG mở 6443 ra ngoài — deploy từ bên trong Droplet qua SSH
  # K8s API (6443) giữ ĐÓNG

  # Outbound: cho phép Droplet tải packages, pull images
  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
