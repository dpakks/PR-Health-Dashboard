# =====================================================
# AWS Credentials
# =====================================================

variable "aws_access_key_id" {
  description = "AWS Access Key ID for the admin account"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key for the admin account"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

# =====================================================
# Project
# =====================================================

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "pr-dashboard"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# =====================================================
# VPC & Networking
# =====================================================

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of AZs to use (need at least 2 for ALB and RDS)"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# =====================================================
# RDS (PostgreSQL)
# =====================================================

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "pr_dashboard"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro"
}

# =====================================================
# ECS
# =====================================================

variable "ecs_cpu" {
  description = "CPU units for ECS task (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Memory in MB for ECS task"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "container_port" {
  description = "Port your FastAPI app listens on"
  type        = number
  default     = 8000
}

# =====================================================
# Application Secrets (passed to ECS as env vars)
# =====================================================

variable "jwt_secret_key" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "ses_access_key_id" {
  description = "AWS Access Key for the SES IAM user"
  type        = string
  sensitive   = true
}

variable "ses_secret_access_key" {
  description = "AWS Secret Key for the SES IAM user"
  type        = string
  sensitive   = true
}

variable "ses_sender_email" {
  description = "Verified SES sender email"
  type        = string
}

# =====================================================
# SES IAM
# =====================================================

variable "iam_user_name" {
  description = "Name for the SES IAM user"
  type        = string
  default     = "pr-dashboard-ses-user"
}

# =====================================================
# Frontend domain (for CloudFront + Route53 later)
# =====================================================

variable "domain_name" {
  description = "Your custom domain name (e.g. prdashboard.com)"
  type        = string
  default     = ""
}

variable "bastion_public_key" {
  description = "SSH public key for bastion host"
  type        = string
}