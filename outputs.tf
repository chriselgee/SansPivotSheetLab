output "linux_attack_public_ip" {
  description = "Linux attack box public IP address"
  value       = aws_instance.linux_attack.public_ip
}

output "linux_attack_private_ip" {
  description = "Linux attack box private IP address"
  value       = aws_instance.linux_attack.private_ip
}

output "linux_pivot_public_ip" {
  description = "Linux pivot box public IP address"
  value       = aws_instance.linux_pivot.public_ip
}

output "linux_pivot_private_ip" {
  description = "Linux pivot box private IP address"
  value       = aws_instance.linux_pivot.private_ip
}

output "linux_target_public_ip" {
  description = "Linux target box public IP address"
  value       = aws_instance.linux_target.public_ip
}

output "linux_target_private_ip" {
  description = "Linux target box private IP address"
  value       = aws_instance.linux_target.private_ip
}

output "sg_pivot" {
  description = "Pivot Security Group"
  value       = aws_security_group.sg_pivot.id
}

output "vpc" {
  description = "Pivot Range VPC"
  value =       aws_vpc.vpc.id
}

# output "windows_pivot_public_ip" {
#   description = "Windows pivot box public IP address"
#   value = aws_instance.windows_pivot.public_ip
# }
