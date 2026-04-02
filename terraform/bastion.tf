# # =====================================================
# # Temporary Bastion EC2 — for database migration only
# # DELETE THIS FILE after migration is complete
# # =====================================================

# # Security group for bastion — SSH from your IP
# resource "aws_security_group" "bastion" {
#   name        = "${var.project_name}-bastion-sg"
#   description = "SSH access for bastion host"
#   vpc_id      = aws_vpc.main.id

#   ingress {
#     description = "SSH from my IP"
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["73.234.117.195/32"]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     Name = "${var.project_name}-bastion-sg"
#   }
# }

# # Allow bastion to connect to RDS
# resource "aws_security_group_rule" "rds_from_bastion" {
#   type                     = "ingress"
#   from_port                = 5432
#   to_port                  = 5432
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.bastion.id
#   security_group_id        = aws_security_group.rds.id
#   description              = "PostgreSQL from bastion"
# }

# # Get latest Amazon Linux 2023 AMI
# data "aws_ami" "amazon_linux" {
#   most_recent = true
#   owners      = ["amazon"]

#   filter {
#     name   = "name"
#     values = ["al2023-ami-*-x86_64"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }

# # Key pair — you'll create this in the next step
# resource "aws_key_pair" "bastion" {
#   key_name   = "${var.project_name}-bastion-key"
#   public_key = var.bastion_public_key
# }

# # Bastion EC2 instance
# resource "aws_instance" "bastion" {
#   ami                    = data.aws_ami.amazon_linux.id
#   instance_type          = "t2.micro"
#   subnet_id              = aws_subnet.public_a.id
#   vpc_security_group_ids = [aws_security_group.bastion.id]
#   key_name               = aws_key_pair.bastion.key_name

#   associate_public_ip_address = true

#   tags = {
#     Name = "${var.project_name}-bastion"
#   }
# }

# output "bastion_public_ip" {
#   description = "Bastion host public IP — SSH into this"
#   value       = aws_instance.bastion.public_ip
# }