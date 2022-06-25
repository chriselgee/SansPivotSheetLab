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

resource "aws_security_group" "website" {
  name   = "website"
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

data "template_file" "linux_website_data" {
  template = file("./scripts/linux-website.yaml")
}

resource "aws_instance" "linux_website" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.website.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_website_data.rendered

  tags = {
    Name    = "Linux-Website"
    Project = "HammerCTF22"
  }
}

data "template_file" "linux_client_data" {
  template = file("./scripts/linux-client.yaml")
}

resource "aws_instance" "linux_client" {
  ami                         = data.aws_ami.ubuntu.id
  count                       = var.instance_count
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.website.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_client_data.rendered

  tags = {
    Name    = "Linux-Client-${count.index + 1}"
    Project = "HammerCTF22"
  }
}

data "template_file" "linux_attacker_data" {
  template = file("./scripts/linux-attacker.yaml")
}

resource "aws_instance" "linux_attacker" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.website.id]
  associate_public_ip_address = true
  user_data                   = data.template_file.linux_attacker_data.rendered
  
  tags = {
    Name    = "Linux-Attacker"
    Project = "HammerCTF22"
  }
}
