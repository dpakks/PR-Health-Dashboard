# =====================================================
# SES — Email service (existing config, moved here)
# =====================================================

resource "aws_ses_email_identity" "sender" {
  email = var.ses_sender_email
}

resource "aws_iam_user" "ses_user" {
  name = var.iam_user_name
  tags = {
    Purpose = "PR Health Dashboard - SES OTP Emails"
  }
}

resource "aws_iam_policy" "ses_send_policy" {
  name        = "ses-send-email-policy"
  description = "Allows sending emails via Amazon SES"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowSESSend"
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "ses_user_policy" {
  user       = aws_iam_user.ses_user.name
  policy_arn = aws_iam_policy.ses_send_policy.arn
}

resource "aws_iam_access_key" "ses_user_key" {
  user = aws_iam_user.ses_user.name
}