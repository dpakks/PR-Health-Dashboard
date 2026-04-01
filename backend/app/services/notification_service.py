"""
Notification Service
--------------------
Gathers open PRs per project, resolves assigned tech leads,
and sends review reminder emails via SES.

Place this file at: app/services/notification_service.py
"""

import threading
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Project, User, UserProject
from app.services.github_service import GitHubService
from app.services.ses_service import SESService

STALE_DAYS = 7


def _extract_owner_repo(repo_url: str):
    """Parse owner/repo from a GitHub URL."""
    repo_url = repo_url.rstrip("/")
    parts = repo_url.split("/")
    return parts[-2], parts[-1]


def _fetch_open_prs(owner: str, repo: str) -> list[dict]:
    """Fetch and normalize open PRs from GitHub."""
    github = GitHubService()

    try:
        raw_prs = github.get_open_pull_requests(owner=owner, repo=repo)
    except Exception as e:
        print(f"GitHub fetch failed for {owner}/{repo}: {e}")
        return []

    now = datetime.now(timezone.utc)
    normalized = []

    for pr in raw_prs:
        created_at = datetime.fromisoformat(
            pr["created_at"].replace("Z", "+00:00")
        )
        days_open = (now - created_at).days

        normalized.append({
            "title": pr["title"],
            "author": pr["user"]["login"],
            "days_open": days_open,
            "is_stale": days_open > STALE_DAYS,
            "url": pr["html_url"],
        })

    return normalized


def send_pr_review_notifications():
    """
    Main notification job:
    1. Get all projects
    2. For each project, fetch open PRs
    3. Find assigned tech leads
    4. Send one email per tech lead per project
    """

    print(f"[Notification] Starting PR review notification job at {datetime.now()}")

    db: Session = SessionLocal()
    ses = SESService()

    try:
        projects = db.query(Project).all()

        if not projects:
            print("[Notification] No projects found. Skipping.")
            return

        total_emails = 0

        for project in projects:
            # --- Fetch open PRs ---
            try:
                owner, repo = _extract_owner_repo(project.repo_url)
            except Exception:
                print(f"[Notification] Invalid repo URL for project '{project.name}'. Skipping.")
                continue

            prs = _fetch_open_prs(owner, repo)

            if not prs:
                print(f"[Notification] No open PRs for '{project.name}'. Skipping.")
                continue

            # --- Find assigned tech leads ---
            assigned_users = (
                db.query(User)
                .join(UserProject, User.id == UserProject.user_id)
                .filter(UserProject.project_id == project.id)
                .all()
            )

            if not assigned_users:
                print(f"[Notification] No tech leads assigned to '{project.name}'. Skipping.")
                continue

            # --- Send email to each tech lead ---
            for user in assigned_users:
                try:
                    ses.send_pr_review_email(
                        recipient=user.email,
                        tech_lead_name=user.name,
                        project_name=project.name,
                        pull_requests=prs,
                    )
                    total_emails += 1
                except Exception as e:
                    print(f"[Notification] Failed to email {user.email}: {e}")

        print(f"[Notification] Job complete. Sent {total_emails} email(s).")

    except Exception as e:
        print(f"[Notification] Job failed with error: {e}")

    finally:
        db.close()


def run_notifications_in_background():
    """Run the notification job in a background thread."""
    thread = threading.Thread(
        target=send_pr_review_notifications,
        daemon=True,
    )
    thread.start()