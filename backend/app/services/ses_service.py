"""
SES Service
-----------
Handles sending emails via Amazon SES.
Place this file at: app/services/ses_service.py
"""

import boto3
from botocore.exceptions import ClientError
from app.config import settings


class SESService:
    """
    Wrapper around AWS SES for sending transactional emails.
    """

    def __init__(self):
        self.client = boto3.client(
            "ses",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.sender = settings.SES_SENDER_EMAIL

    def send_otp_email(self, recipient: str, otp: str, purpose: str = "login"):
        """
        Send an OTP email to the given recipient.

        Args:
            recipient: The target email address.
            otp: The 6-digit OTP string.
            purpose: Either 'login' or 'forgot_password'.
        """

        if purpose == "forgot_password":
            subject = "PR Health Dashboard — Password Reset OTP"
            heading = "Password Reset Verification"
            message_line = "Use the OTP below to reset your password."
        else:
            subject = "PR Health Dashboard — Login OTP"
            heading = "Login Verification"
            message_line = "Use the OTP below to complete your login."

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 480px; margin: auto; background: #ffffff;
                        border-radius: 8px; padding: 32px; text-align: center;">
                <h2 style="color: #333;">{heading}</h2>
                <p style="color: #555;">{message_line}</p>
                <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px;
                            color: #1a73e8; margin: 24px 0;">
                    {otp}
                </div>
                <p style="color: #999; font-size: 13px;">
                    This code expires in 5 minutes. Do not share it with anyone.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"{heading}\n\nYour OTP is: {otp}\n\nIt expires in 5 minutes."

        try:
            self.client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )
            return True

        except ClientError as e:
            print(f"SES send failed: {e.response['Error']['Message']}")
            return False

    def send_pr_review_email(
        self,
        recipient: str,
        tech_lead_name: str,
        project_name: str,
        pull_requests: list[dict],
    ):
        """
        Send a PR review reminder email to a tech lead.

        Args:
            recipient: Tech lead's email address.
            tech_lead_name: Tech lead's display name.
            project_name: Name of the project.
            pull_requests: List of PR dicts with keys:
                title, author, days_open, url, is_stale
        """

        subject = f"PR Review Reminder — {project_name}"

        # Build PR rows
        pr_rows = ""
        for pr in pull_requests:
            stale_badge = (
                '<span style="color:#dc2626;font-weight:700;">STALE</span>'
                if pr.get("is_stale")
                else '<span style="color:#16a34a;font-weight:600;">Fresh</span>'
            )

            pr_rows += f"""
            <tr>
                <td style="padding:12px 14px;border-bottom:1px solid #e2e8f0;font-size:14px;">
                    <a href="{pr['url']}" style="color:#2563eb;text-decoration:none;font-weight:600;">
                        {pr['title']}
                    </a>
                </td>
                <td style="padding:12px 14px;border-bottom:1px solid #e2e8f0;font-size:14px;text-align:center;">
                    {pr['author']}
                </td>
                <td style="padding:12px 14px;border-bottom:1px solid #e2e8f0;font-size:14px;text-align:center;">
                    {pr['days_open']} days
                </td>
                <td style="padding:12px 14px;border-bottom:1px solid #e2e8f0;font-size:14px;text-align:center;">
                    {stale_badge}
                </td>
            </tr>
            """

        stale_count = sum(1 for pr in pull_requests if pr.get("is_stale"))
        total_count = len(pull_requests)

        html_body = f"""
        <html>
        <body style="font-family:Arial,sans-serif;padding:20px;background-color:#f4f4f4;margin:0;">
            <div style="max-width:680px;margin:auto;background:#ffffff;border-radius:12px;
                        overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

                <!-- Header -->
                <div style="background:linear-gradient(135deg,#2563eb,#4f46e5);padding:28px 32px;">
                    <h1 style="color:#ffffff;margin:0;font-size:22px;">
                        PR Review Reminder
                    </h1>
                    <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;font-size:14px;">
                        Project: <strong>{project_name}</strong>
                    </p>
                </div>

                <!-- Body -->
                <div style="padding:28px 32px;">
                    <p style="color:#334155;font-size:15px;line-height:1.6;margin:0 0 8px;">
                        Hi <strong>{tech_lead_name}</strong>,
                    </p>
                    <p style="color:#475569;font-size:14px;line-height:1.6;margin:0 0 20px;">
                        There are <strong>{total_count} open pull request(s)</strong>
                        in <strong>{project_name}</strong>
                        ({stale_count} stale). Please review and take action.
                    </p>

                    <!-- PR Table -->
                    <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;
                                  border-radius:8px;overflow:hidden;">
                        <thead>
                            <tr style="background:#f8fafc;">
                                <th style="padding:12px 14px;text-align:left;font-size:12px;
                                           font-weight:800;color:#334155;text-transform:uppercase;
                                           letter-spacing:0.05em;border-bottom:2px solid #e2e8f0;">
                                    Pull Request
                                </th>
                                <th style="padding:12px 14px;text-align:center;font-size:12px;
                                           font-weight:800;color:#334155;text-transform:uppercase;
                                           letter-spacing:0.05em;border-bottom:2px solid #e2e8f0;">
                                    Author
                                </th>
                                <th style="padding:12px 14px;text-align:center;font-size:12px;
                                           font-weight:800;color:#334155;text-transform:uppercase;
                                           letter-spacing:0.05em;border-bottom:2px solid #e2e8f0;">
                                    Days Open
                                </th>
                                <th style="padding:12px 14px;text-align:center;font-size:12px;
                                           font-weight:800;color:#334155;text-transform:uppercase;
                                           letter-spacing:0.05em;border-bottom:2px solid #e2e8f0;">
                                    Status
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {pr_rows}
                        </tbody>
                    </table>

                    <p style="color:#64748b;font-size:13px;margin:20px 0 0;line-height:1.5;">
                        Please review these pull requests and close or merge them as appropriate.
                    </p>
                </div>

                <!-- Footer -->
                <div style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;">
                    <p style="color:#94a3b8;font-size:12px;margin:0;text-align:center;">
                        This is an automated notification from PR Health Dashboard.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        pr_lines = "\\n".join(
            f"- {pr['title']} by {pr['author']} ({pr['days_open']} days) — {pr['url']}"
            for pr in pull_requests
        )

        text_body = (
            f"Hi {tech_lead_name},\\n\\n"
            f"There are {total_count} open PR(s) in {project_name} "
            f"({stale_count} stale):\\n\\n"
            f"{pr_lines}\\n\\n"
            f"Please review and take action."
        )

        try:
            self.client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )
            print(f"PR review email sent to {recipient} for project '{project_name}'")
            return True

        except ClientError as e:
            print(f"SES PR email failed for {recipient}: {e.response['Error']['Message']}")
            return False