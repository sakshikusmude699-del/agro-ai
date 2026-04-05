"""
APScheduler job runner.
Runs a daily check at 7:00 AM to send farming notifications to all active users.
"""

import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = BackgroundScheduler()


def _run_daily_notifications():
    """Sync wrapper to run the async notification check."""
    from database import get_db
    from scheduler.notification_logic import check_and_notify_user

    async def _async_job():
        db = get_db()
        if db is None:
            print("⚠️ DB not connected, skipping notification job")
            return

        # Get all users with active timelines
        active_user_ids = await db.timelines.distinct(
            "user_id", {"active": True}
        )

        total = 0
        for uid in active_user_ids:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(uid)})
            if user:
                count = await check_and_notify_user(user)
                total += count

        print(f"📬 Daily notifications: {total} sent to {len(active_user_ids)} farmers")

    # Create a new event loop for the background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_job())
    finally:
        loop.close()


def start_scheduler():
    """Start the APScheduler with daily job at 7:00 AM."""
    scheduler.add_job(
        _run_daily_notifications,
        trigger=CronTrigger(hour=7, minute=0),
        id="daily_notifications",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    print("⏰ Scheduler started — daily notifications at 7:00 AM")


def stop_scheduler():
    """Gracefully stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("⏹️ Scheduler stopped")
