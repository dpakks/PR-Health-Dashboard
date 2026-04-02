# Database Migration — Local PostgreSQL to AWS RDS

## Overview

Migrating the `pr_dashboard` PostgreSQL database from a local Windows machine to an AWS RDS instance running in a private subnet within a VPC.

**Final result:** 5 users, 2 projects, 12 user-project assignments successfully migrated.

---

## What We Tried (and Why It Failed)

### Attempt 1 — Direct connection from local machine to RDS

**Approach:** Add our public IP to the RDS security group and connect directly.

**File changes:**
- `security.tf` — Added temporary ingress rule to `aws_security_group.rds`:
  ```hcl
  ingress {
    description = "Temporary - local migration access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["73.234.117.195/32"]
  }
  ```

**Command:**
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h pr-dashboard-db.ck96w06io9q1.us-east-1.rds.amazonaws.com -d pr_dashboard -f C:\Users\Deepa\pr_dashboard_backup.sql
```

**Result:** Connection timed out.

**Why it failed:** RDS was in a private subnet. Private subnets have no route to/from the internet — only through a NAT gateway (outbound only). Even with the security group allowing our IP, the network routing made it unreachable from outside the VPC.

---

### Attempt 2 — Make RDS publicly accessible

**Approach:** Set `publicly_accessible = true` on the RDS instance so AWS assigns it a public IP.

**File changes:**
- `rds.tf` — Changed `publicly_accessible = false` to `publicly_accessible = true`

**Command:**
```powershell
terraform apply
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h pr-dashboard-db.ck96w06io9q1.us-east-1.rds.amazonaws.com -d pr_dashboard -f C:\Users\Deepa\pr_dashboard_backup.sql
```

**Result:** Connection timed out. RDS resolved to a public IP (44.193.236.108) but still unreachable.

**Why it failed:** `publicly_accessible = true` assigns a public IP, but the RDS instance was still in a private subnet whose route table points to the NAT gateway, not the internet gateway. A public IP without an internet gateway route is useless — traffic has no return path.

---

### Attempt 3 — Move RDS subnet group to public subnets

**Approach:** Change the RDS subnet group to use public subnets (which have internet gateway routes) so the public IP would actually work.

**File changes:**
- `rds.tf` — Changed subnet group to include public subnets:
  ```hcl
  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]
  ```

**Result:** Failed with error: `Some of the subnets to be deleted are currently in use`. AWS cannot remove subnets from a DB subnet group while the RDS instance is using them.

**Why it failed:** RDS was already running in one of the private subnets. AWS doesn't allow removing in-use subnets from a subnet group without stopping or migrating the instance first.

---

### Attempt 3b — Add all subnets to the group

**Approach:** Instead of replacing private with public subnets, add all 4 subnets to the group.

**File changes:**
- `rds.tf` — Subnet group with all 4 subnets:
  ```hcl
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]
  ```

**Command:**
```powershell
terraform apply
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h pr-dashboard-db.ck96w06io9q1.us-east-1.rds.amazonaws.com -d pr_dashboard -f C:\Users\Deepa\pr_dashboard_backup.sql
```

**Result:** Still timed out. RDS stayed in its original private subnet (10.0.3.89) — adding public subnets to the group didn't move the instance.

**Why it failed:** RDS doesn't automatically move to a different subnet when you modify the subnet group. The instance stays wherever it was originally placed. It would require a reboot or recreation to actually move.

---

### Attempt 4 — EC2 Bastion Host (SUCCESS)

**Approach:** Instead of connecting from outside the VPC, launch a small EC2 instance inside the VPC's public subnet. SSH into it from our local machine, then connect to RDS from inside the VPC where the private subnet routing works.

**Why this works:** The bastion sits in the public subnet (reachable via SSH from the internet). RDS sits in the private subnet. Both are inside the same VPC, so the bastion can reach RDS directly through internal VPC routing — no internet gateway or NAT gateway needed for this internal traffic.

```
Local machine → SSH (port 22) → Bastion (public subnet)
                                    ↓ (internal VPC routing)
                                 RDS (private subnet, port 5432)
```

**File changes:**

1. Created `bastion.tf`:
   - Security group allowing SSH from our IP (73.234.117.195/32)
   - Security group rule allowing bastion to connect to RDS on port 5432
   - EC2 instance (t2.micro, Amazon Linux 2023) in public subnet
   - Key pair for SSH access

2. Added to `variables.tf`:
   ```hcl
   variable "bastion_public_key" {
     description = "SSH public key for bastion host"
     type        = string
   }
   ```

3. Added to `terraform.tfvars`:
   ```hcl
   bastion_public_key = "ssh-rsa AAAAB3... (public key content)"
   ```

**Commands (in order):**

Step 1 — Generate SSH key pair (local PowerShell):
```powershell
ssh-keygen -t rsa -b 4096 -f C:\Users\Deepa\.ssh\bastion-key
Get-Content C:\Users\Deepa\.ssh\bastion-key.pub
```

Step 2 — Create bastion infrastructure:
```powershell
cd C:\Users\Deepa\OneDrive\Documents\Projects\pr-health-dashboard\terraform
terraform apply
terraform output bastion_public_ip
```

Step 3 — Export local database (local PowerShell):
```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -U postgres -h localhost -d pr_dashboard -F p -f C:\Users\Deepa\pr_dashboard_backup.sql
```

Step 4 — Copy backup to bastion:
```powershell
scp -i C:\Users\Deepa\.ssh\bastion-key C:\Users\Deepa\pr_dashboard_backup.sql ec2-user@54.166.24.88:/home/ec2-user/
```

Step 5 — SSH into bastion:
```powershell
ssh -i C:\Users\Deepa\.ssh\bastion-key ec2-user@54.166.24.88
```

Step 6 — Install PostgreSQL client on bastion:
```bash
sudo dnf install -y postgresql15
```

Step 7 — Import into RDS:
```bash
psql -U postgres -h pr-dashboard-db.ck96w06io9q1.us-east-1.rds.amazonaws.com -d pr_dashboard -f /home/ec2-user/pr_dashboard_backup.sql
```

Step 8 — Verify data:
```bash
psql -U postgres -h pr-dashboard-db.ck96w06io9q1.us-east-1.rds.amazonaws.com -d pr_dashboard
SELECT count(*) FROM users;         -- Expected: 5
SELECT count(*) FROM projects;      -- Expected: 2
SELECT count(*) FROM user_projects;  -- Expected: 12
\q
exit
```

**Result:** All data migrated successfully.

---

## Cleanup After Migration

1. Delete `bastion.tf` from the terraform folder
2. Revert `rds.tf`:
   - `publicly_accessible = false`
   - Subnet group back to private subnets only
3. Remove temporary ingress rule from `security.tf` (the one with `73.234.117.195/32`)
4. Remove `bastion_public_key` from `variables.tf` and `terraform.tfvars`
5. Apply:
   ```powershell
   terraform apply
   ```
   This destroys the bastion EC2 instance, its security group, and locks RDS back down.

---

## Key Lesson

**You cannot connect to an RDS instance in a private subnet from the public internet**, even with `publicly_accessible = true` and security group rules allowing your IP. The subnet's route table must have a route to an internet gateway for public access to work. Private subnets route through NAT gateways which only support outbound traffic.

**The correct approach** for one-time migrations to private RDS is to use a bastion host (or SSM Session Manager) inside the VPC that can reach both the internet (for SSH) and the private subnet (for database access).