variable "cidr_vpc" {
  description = "CIDR block for the VPC"
  default     = "10.1.0.0/16"
}

variable "cidr_subnet" {
  description = "CIDR block for the subnet"
  default     = "10.1.0.0/18"
}

variable "region" {
  description = "The region Terraform deploys your instance"
  default = "us-east-2"
}
