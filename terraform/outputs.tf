# =====================================================
# Outputs — values you'll need after terraform apply
# =====================================================

# ALB URL — your backend API endpoint
output "alb_dns_name" {
  description = "ALB DNS name — use this to test your backend"
  value       = aws_lb.main.dns_name
}

# CloudFront URL — your frontend
output "cloudfront_url" {
  description = "CloudFront URL — your React app"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

# S3 bucket name — needed for frontend deployment
output "s3_bucket_name" {
  description = "S3 bucket for frontend files"
  value       = aws_s3_bucket.frontend.bucket
}

# ECR repository URL — needed for Docker push
output "ecr_repository_url" {
  description = "ECR repo URL for backend Docker images"
  value       = aws_ecr_repository.backend.repository_url
}

# RDS endpoint — for database migration
output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.endpoint
}

# Redis endpoint
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

# CloudFront distribution ID — needed for cache invalidation
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = aws_cloudfront_distribution.frontend.id
}

# SES credentials
output "ses_iam_access_key_id" {
  description = "Access Key ID for the SES IAM user"
  value       = aws_iam_access_key.ses_user_key.id
}

output "ses_iam_secret_access_key" {
  description = "Secret Access Key for the SES IAM user"
  value       = aws_iam_access_key.ses_user_key.secret
  sensitive   = true
}