# =====================================================
# VPC — Your private network in AWS
# =====================================================
# 10.0.0.0/16 gives you 65,536 IP addresses.
# We split it into 4 subnets:
#   Public  AZ-a: 10.0.1.0/24 (256 IPs) — ALB, NAT
#   Public  AZ-b: 10.0.2.0/24 (256 IPs) — ALB redundancy
#   Private AZ-a: 10.0.3.0/24 (256 IPs) — ECS, RDS, Redis
#   Private AZ-b: 10.0.4.0/24 (256 IPs) — RDS standby
# =====================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# =====================================================
# Internet Gateway — front door to the internet
# Attaches to the VPC so public subnets can reach out
# =====================================================

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# =====================================================
# Public Subnets (2 AZs — required by ALB)
# These can talk to the internet directly via the IGW
# =====================================================

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = var.availability_zones[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-b"
  }
}

# =====================================================
# Private Subnets (2 AZs — required by RDS)
# NO internet access from outside. Only outbound via NAT.
# =====================================================

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = var.availability_zones[0]

  tags = {
    Name = "${var.project_name}-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = var.availability_zones[1]

  tags = {
    Name = "${var.project_name}-private-b"
  }
}

# =====================================================
# Elastic IP for NAT Gateway
# A static public IP that the NAT gateway uses
# =====================================================

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-nat-eip"
  }
}

# =====================================================
# NAT Gateway — sits in public subnet
# Lets private subnet resources (ECS, etc.) make
# outbound calls (GitHub API, SES) without being
# reachable from the internet
# =====================================================

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id

  tags = {
    Name = "${var.project_name}-nat"
  }

  depends_on = [aws_internet_gateway.main]
}

# =====================================================
# Route Tables
# Public → routes to Internet Gateway
# Private → routes to NAT Gateway
# =====================================================

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

# =====================================================
# Associate subnets with their route tables
# =====================================================

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}

