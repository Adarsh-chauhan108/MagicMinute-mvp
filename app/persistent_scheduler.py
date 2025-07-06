import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from gmail_utils import send_email
from datetime import datetime
import pytz

# Path to SQLite DB
DB_PATH = "sqlite:///app/magic_scheduler/jobs.sqlite"

# Ensure folder exists
os.makedirs("app/magic_scheduler", exist_ok=True)

# Configure jobstore
jobstores = {
    'default': SQLAlchemyJobStore(url=DB_PATH)
}

# Initialize the scheduler
scheduler = BackgroundScheduler(jobstores=jobstores, timezone=pytz.timezone("Asia/Kolkata"))


def start_scheduler():
    """Starts the persistent background scheduler."""
    if not scheduler.running:
        scheduler.start()
        print("✅ Background scheduler started.")


def schedule_email_background(recipient, subject, body, time_str):
    """Schedules an email to be sent at a specific time."""
    now = datetime.now().astimezone(pytz.timezone("Asia/Kolkata"))
    target_time = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo
    )

    if target_time < now:
        target_time = target_time + timedelta(days=1)

    job_id = f"{recipient}-{target_time.strftime('%H%M')}"

    scheduler.add_job(
        func=send_email,
        trigger="date",
        run_date=target_time,
        args=[recipient, subject, body],
        id=job_id,
        replace_existing=True
    )
    print(f"📅 Scheduled email to {recipient} at {target_time.strftime('%H:%M')}")

# ---- alias for backward‑compatibility ----
schedule_email = schedule_email_background   # 👈 makes old import work