# =====================================================
# RDS PostgreSQL — your database in the cloud
# =====================================================

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
  ]

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"

  engine         = "postgres"
  engine_version = "15"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 50
  storage_type          = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Temporarily public for migration — change back to false after
  publicly_accessible = false

  # Backup
  backup_retention_period = 7
  backup_window           = "03:00-04:00"

  # Maintenance
  maintenance_window = "Mon:04:00-Mon:05:00"

  skip_final_snapshot = true
  multi_az            = false

  tags = {
    Name = "${var.project_name}-db"
  }
}