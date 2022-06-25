output "sg" {
  description = "Security Group"
  value       = aws_security_group.website.id
}

output "vpc" {
  description = "Range VPC"
  value       = aws_vpc.vpc.id
}

output "linux_attacker_public_ip" {
  description = "Linux attacker public IP address"
  value       = aws_instance.linux_attacker.public_ip
}

# output "linux_attacker_private_ip" {
#   description = "Linux attacker private IP address"
#   value       = aws_instance.linux_attacker.private_ip
# }
 
output "linux_client_public_ip" {
  description = "Linux client public IP address"
  value       = ["${aws_instance.linux_client.*.public_ip}"]
}

# output "linux_client_private_ip" {
#   description = "Linux client private IP address"
#   value       = ["${aws_instance.linux_client.*.private_ip}"]
# }
 
output "linux_website_public_ip" {
  description = "Linux website public IP address"
  value       = aws_instance.linux_website.public_ip
}

# output "linux_website_private_ip" {
#   description = "Linux website private IP address"
#   value       = aws_instance.linux_website.private_ip
# }
