variable "do_token" {
  description = "DigitalOcean API Token (Full Access). Lấy từ: https://cloud.digitalocean.com/account/api/tokens"
  type        = string
  sensitive   = true
}

variable "github_pat" {
  description = "GitHub Personal Access Token để pull images từ GHCR (ghcr.io/eurusdevsec/zero-door/...)"
  type        = string
  sensitive   = true
}

variable "ssh_public_key_path" {
  description = "Đường dẫn tới public SSH key để upload lên DigitalOcean"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "sgp1"  # Singapore — gần Việt Nam nhất
}

variable "droplet_size" {
  description = "Droplet size slug. s-4vcpu-8gb = 4vCPU/8GB RAM (~$48/tháng)"
  type        = string
  default     = "s-4vcpu-8gb"
}

variable "allowed_ssh_ips" {
  description = "Danh sách IP được phép SSH vào Droplet. Mặc định: tất cả (0.0.0.0/0)"
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"]
}
