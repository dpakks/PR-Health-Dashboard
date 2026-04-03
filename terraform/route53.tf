# =====================================================
# Route 53 — DNS management for your domain
# =====================================================
# A hosted zone is like a phone book for your domain.
# It tells the internet where to find your services.
# prmonitor.site → CloudFront (frontend)
# api.prmonitor.site → ALB (backend)
# =====================================================

resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = {
    Name = "${var.project_name}-zone"
  }
}

# =====================================================
# ACM Certificate — free SSL for your domain
# =====================================================
# This certificate covers both the root domain and
# all subdomains (*.prmonitor.site).
# ACM validates ownership via DNS records that
# Terraform creates automatically in Route 53.
# =====================================================

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"

  tags = {
    Name = "${var.project_name}-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# DNS records that prove you own the domain (for ACM validation)
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Wait for certificate to be validated
resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# =====================================================
# DNS Records — point domain to your services
# =====================================================

# prmonitor.site → CloudFront (frontend)
resource "aws_route53_record" "frontend" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

# api.prmonitor.site → ALB (backend)
resource "aws_route53_record" "backend" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# =====================================================
# Outputs
# =====================================================

output "nameservers" {
  description = "Set these nameservers in Namecheap"
  value       = aws_route53_zone.main.name_servers
}