output "droplet_ip" {
  description = "Public IP của Droplet — dùng để truy cập các services"
  value       = digitalocean_droplet.zero_door.ipv4_address
}

output "boutique_url" {
  description = "URL Google Boutique (target app)"
  value       = "http://${digitalocean_droplet.zero_door.ipv4_address}/"
}

output "dashboard_url" {
  description = "URL Zero-Door Control Dashboard"
  value       = "http://${digitalocean_droplet.zero_door.ipv4_address}/nemesis/dashboard/"
}

output "nemesis_health" {
  description = "URL Nemesis Agent health check"
  value       = "http://${digitalocean_droplet.zero_door.ipv4_address}/nemesis/healthz"
}

output "hephaestus_health" {
  description = "URL Hephaestus Agent health check"
  value       = "http://${digitalocean_droplet.zero_door.ipv4_address}/hephaestus/healthz"
}

output "ssh_command" {
  description = "Lệnh SSH vào Droplet"
  value       = "ssh root@${digitalocean_droplet.zero_door.ipv4_address}"
}

output "deploy_log" {
  description = "Xem log deploy trên Droplet"
  value       = "ssh root@${digitalocean_droplet.zero_door.ipv4_address} 'tail -f /var/log/zero-door-deploy.log'"
}
