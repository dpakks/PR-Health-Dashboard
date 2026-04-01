"""
Scheduler
---------
Runs background scheduled jobs using APScheduler.
Currently schedules daily PR review notification emails.

Place this file at: app/scheduler.py
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notification_service import send_pr_review_notifications


scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Start the background scheduler.
    Runs the PR review notification job every day at 9:00 AM.
    """

    scheduler.add_job(
        func=send_pr_review_notifications,
        trigger=CronTrigger(hour=7, minute=0),  # Every day at 9:00 AM
        id="daily_pr_review_notifications",
        name="Daily PR Review Email Notifications",
        replace_existing=True,
    )

    scheduler.start()
    print("[Scheduler] Started — PR review emails scheduled daily at 7:00 AM")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] Stopped")