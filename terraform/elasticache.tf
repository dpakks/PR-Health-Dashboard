# =====================================================
# ElastiCache Redis — replaces your local Docker Redis
# =====================================================
# Sits in private subnets. Only ECS can connect.
# cache.t3.micro is the smallest (free-tier eligible).
# =====================================================

resource "aws_elasticache_subnet_group" "main" {
  name = "${var.project_name}-redis-subnet"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
  ]

  tags = {
    Name = "${var.project_name}-redis-subnet"
  }
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  tags = {
    Name = "${var.project_name}-redis"
  }
}