# =====================================================
# IAM User for GitHub Actions CI/CD
# =====================================================
# This user has permissions to:
# - Push Docker images to ECR
# - Update ECS services (trigger new deployments)
# - Sync files to S3 (frontend deployment)
# - Invalidate CloudFront cache
# =====================================================

resource "aws_iam_user" "cicd" {
  name = "${var.project_name}-cicd-user"

  tags = {
    Purpose = "GitHub Actions CI/CD deployments"
  }
}

resource "aws_iam_policy" "cicd" {
  name        = "${var.project_name}-cicd-policy"
  description = "Permissions for GitHub Actions to deploy backend and frontend"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRAuth"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Sid    = "ECRPush"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = aws_ecr_repository.backend.arn
      },
      {
        Sid    = "ECSUpdate"
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:ListTasks",
          "ecs:DescribeTasks"
        ]
        Resource = "*"
      },
      {
        Sid    = "PassRole"
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_execution.arn,
          aws_iam_role.ecs_task.arn
        ]
      },
      {
        Sid    = "S3Frontend"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.frontend.arn,
          "${aws_s3_bucket.frontend.arn}/*"
        ]
      },
      {
        Sid    = "CloudFrontInvalidate"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation"
        ]
        Resource = aws_cloudfront_distribution.frontend.arn
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "cicd" {
  user       = aws_iam_user.cicd.name
  policy_arn = aws_iam_policy.cicd.arn
}

resource "aws_iam_access_key" "cicd" {
  user = aws_iam_user.cicd.name
}

# =====================================================
# Outputs for GitHub Secrets
# =====================================================

output "cicd_access_key_id" {
  description = "CI/CD IAM Access Key ID — add to GitHub Secrets"
  value       = aws_iam_access_key.cicd.id
}

output "cicd_secret_access_key" {
  description = "CI/CD IAM Secret Key — add to GitHub Secrets"
  value       = aws_iam_access_key.cicd.secret
  sensitive   = true
}