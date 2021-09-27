terraform {
  required_version = ">= 0.13"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}


provider "aws" {
  region = var.region
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*20*-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_vpc" "vpc" {
  cidr_block           = var.cidr_vpc
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_subnet" "subnet_public" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = var.cidr_subnet
}

resource "aws_route_table" "rtb_public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "rta_subnet_public" {
  subnet_id      = aws_subnet.subnet_public.id
  route_table_id = aws_route_table.rtb_public.id
}

resource "aws_security_group" "sg_pivot" {
  name   = "sg_pivot"
  vpc_id = aws_vpc.vpc.id

  # Let it rip
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "sg_attack" {
  name   = "sg_attack"
  vpc_id = aws_vpc.vpc.id

  # Let it rip
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "sg_target" {
  name   = "sg_target"
  vpc_id = aws_vpc.vpc.id

  # Let it rip
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.1.2.0/23"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "template_file" "linux_attack_data" {
  template = file("./scripts/linux-attack.yaml")
}

resource "aws_instance" "linux_attack" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_attack.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_attack_data.rendered
  private_ip                  = "10.1.1.1"

  tags = {
    Name    = "Linux-Attack"
    Project = "PivotPlay"
  }
}

data "template_file" "linux_pivot_data" {
  template = file("./scripts/linux-pivot.yaml")
}

resource "aws_instance" "linux_pivot" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_pivot.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_pivot_data.rendered
  private_ip                  = "10.1.2.1"

  tags = {
    Name    = "Linux-Pivot"
    Project = "PivotPlay"
  }
}

data "template_file" "linux_target_data" {
  template = file("./scripts/linux-target.yaml")
}

resource "aws_instance" "linux_target" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_target.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_target_data.rendered
  private_ip                  = "10.1.3.1"
  # provisioner "file" {
  #   source      = "./assets/webserve.py"
  #   destination = "/tmp/webserve2.py"
  #   connection {
  #     type     = "ssh"
  #     user     = "target"
  #     private_key = file("../tf-cloud-init")
  #     host     = aws_instance.linux_target.public_ip
  #     }
  #   }

  tags = {
    Name    = "Linux-Target"
    Project = "PivotPlay"
  }
}

# data "template_file" "windows_pivot_data" {
#   template = file("./scripts/windows-pivot.yaml")
# }
# 
# resource "aws_instance" "windows_pivot" {
#   ami                         = "ami-0f8a21019cb8e9c33"
#   instance_type               = "t2.micro"
#   subnet_id                   = aws_subnet.subnet_public.id
#   vpc_security_group_ids      = [aws_security_group.sg_pivot.id]
#   associate_public_ip_address = true
#   user_data                   = data.template_file.windows_pivot_data.rendered
#   private_ip = "10.1.2.2"
#   tags = {
#     Name = "Windows-Target"
#     Project = "PivotPlay"
#   }
# }
