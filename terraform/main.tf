# =====================================================
# Terraform Configuration + Remote State with Lock
# =====================================================
# The S3 backend stores your terraform.tfstate in the
# cloud so your team can share it. The DynamoDB table
# acts as a lock — if someone is running "terraform apply",
# no one else can run it at the same time.
#
# IMPORTANT: You must create the S3 bucket and DynamoDB
# table BEFORE running "terraform init" with this backend.
# Run these AWS CLI commands first:
#
# aws s3api create-bucket --bucket pr-dashboard-tf-state --region us-east-1
# aws dynamodb create-table \
#   --table-name pr-dashboard-tf-lock \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --billing-mode PAY_PER_REQUEST \
#   --region us-east-1
# =====================================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "pr-dashboard-tf-state"
    key            = "infra/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "pr-dashboard-tf-lock"
    encrypt        = true
  }
}

# =====================================================
# AWS Provider
# =====================================================

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}