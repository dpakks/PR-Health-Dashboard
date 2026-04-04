# 🚀 PR Health Dashboard

A full-stack web application for monitoring pull request health across GitHub repositories. Built with FastAPI + React, deployed on AWS with automated CI/CD and production-grade cloud infrastructure.

---

## ✨ Features

- 🔐 **OTP-based Authentication** — Email + password → 6-digit OTP via AWS SES → JWT token
- 🔑 **Forgot Password** — Email verification → OTP → secure password reset
- 📊 **PR Dashboard** — Real-time open PRs, stale detection, summary stats, trends
- 👥 **Role-based Access** — Admins manage users and projects, Tech Leads view assigned projects
- 📧 **Daily PR Notifications** — Automated emails to tech leads listing open PRs needing review
- 🔄 **Redis Caching** — PR data cached to reduce GitHub API calls

---

## 🏗️ Architecture

```
Users ──▶ Route 53 (prmonitor.site)
              │
     ┌────────┴────────┐
     ▼                  ▼
 CloudFront          ALB (HTTPS)
 + S3 Bucket         ┌───┴───┐
 (React App)     ECS Task  ECS Task  ◀── Auto Scaling (1-4)
                     │         │
              ┌──────┴─────────┘
              ▼                ▼
        RDS PostgreSQL    ElastiCache Redis
        (KMS Encrypted)
```

---

## 🔐 Auth Flow

```
Login:    Email + Password ──▶ OTP via SES ──▶ Verify OTP ──▶ JWT ──▶ Dashboard
Reset:    Email ──▶ OTP via SES ──▶ Verify ──▶ New Password ──▶ Auto Login
```

---

## 🚀 CI/CD

Automated via GitHub Actions on every push to `main`:

- **Backend:** Docker build → Push to ECR → Rolling deploy to ECS Fargate
- **Frontend:** npm build → Sync to S3 → CloudFront cache invalidation

---

## ☁️ AWS Infrastructure (Terraform)

| Layer | Services |
|---|---|
| 🌐 **Networking** | VPC, public/private subnets (2 AZs), NAT Gateway, Internet Gateway |
| ⚖️ **Compute** | ECS Fargate, ALB with HTTPS, Auto Scaling (CPU/Memory based) |
| 💾 **Data** | RDS PostgreSQL, ElastiCache Redis — both in private subnets |
| 🖥️ **Frontend** | S3 + CloudFront CDN with custom domain |
| 🔒 **Security** | KMS encryption (RDS, S3, CloudWatch), ACM SSL, security groups |
| 📊 **Monitoring** | CloudWatch logs, metrics, alarms (CPU, memory, 5xx) |
| 🔧 **DevOps** | ECR, GitHub Actions CI/CD, DynamoDB state locking |
| 📧 **Email** | SES for OTP and PR notification emails |

---

## 🧪 Load Testing

Verified ALB traffic distribution and auto scaling with a Python load test script. Successfully scaled from 1 → 4 ECS tasks under load with zero 5xx errors.

---

## 👤 Author

**Deepak Kumar Somasundaram**
Master's Student | 2026
