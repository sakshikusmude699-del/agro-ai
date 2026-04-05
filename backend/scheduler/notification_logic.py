"""
Daily notification logic.
For each user with an active timeline, checks today's tasks
and sends smart email notifications.
"""

from datetime import date
from database import get_db
from services.email_service import send_notification_email
from services.weather import get_rain_probability_today


async def check_and_notify_user(user: dict) -> int:
    """
    Check today's tasks for a user and send notifications.
    Returns count of notifications sent.
    """
    db = get_db()
    user_id = str(user["_id"])
    email = user["email"]
    name = user.get("name", "Farmer")
    today_str = date.today().isoformat()
    sent_count = 0

    # Get active timeline
    timeline = await db.timelines.find_one(
        {"user_id": user_id, "active": True},
        sort=[("created_at", -1)],
    )
    if not timeline:
        return 0

    crop = timeline["crop"]
    location = user.get("location", "")

    # Get rain probability for smart irrigation logic
    rain_prob = 0.0
    if location:
        try:
            rain_prob = await get_rain_probability_today(location)
        except Exception:
            rain_prob = 0.0

    # Find today's tasks
    today_tasks = [
        t for t in timeline.get("tasks", [])
        if t.get("scheduled_date") == today_str and not t.get("completed") and not t.get("skipped")
    ]

    for task in today_tasks:
        task_type = task["task_type"]
        title = task["title"]
        day = task["day"]

        subject, message, skip = _build_notification(
            task_type, title, crop, name, rain_prob, day
        )

        # Log notification to DB
        notif_doc = {
            "user_id": user_id,
            "crop": crop,
            "task_type": task_type,
            "message": message,
            "date": date.today().isoformat(),
            "status": "skipped" if skip else "sent",
        }

        if skip:
            # Update task as skipped in timeline
            await db.timelines.update_one(
                {"_id": timeline["_id"], "tasks.day": day},
                {"$set": {
                    "tasks.$.skipped": True,
                    "tasks.$.skip_reason": f"Rain expected ({rain_prob:.0f}% probability)",
                }},
            )
        else:
            # Send email
            success = await send_notification_email(
                to_email=email,
                subject=subject,
                message=message,
                crop=crop,
                task_type=task_type,
            )
            notif_doc["status"] = "sent" if success else "failed"

        await db.notifications.insert_one(notif_doc)
        sent_count += 1

    # Weather alerts (independent of tasks)
    if rain_prob > 80:
        msg = (f"Heavy rain expected today ({rain_prob:.0f}% probability). "
               f"Avoid spraying pesticides or fertilizers. Ensure field drainage.")
        await send_notification_email(email, "Heavy Rain Alert", msg, crop, "rain_alert")
        sent_count += 1

    return sent_count


def _build_notification(
    task_type: str, title: str, crop: str, name: str, rain_prob: float, day: int
) -> tuple:
    """Build notification subject, message. Returns (subject, message, should_skip)."""

    if task_type == "irrigation":
        if rain_prob > 70:
            return (
                "Irrigation Skipped — Rain Expected",
                (f"Dear {name}, today's irrigation for your {crop} crop (Day {day}) has been "
                 f"automatically skipped. Rain probability is {rain_prob:.0f}%. "
                 f"Save water and check back tomorrow!"),
                True,   # skip = True
            )
        return (
            f"Irrigation Reminder — Day {day}",
            (f"Dear {name}, it's time to irrigate your {crop} crop (Day {day}). "
             f"Current rain probability is only {rain_prob:.0f}%. "
             f"Ensure adequate water coverage for optimal growth."),
            False,
        )

    elif task_type == "fertilizer":
        return (
            f"Fertilizer Application — Day {day}",
            (f"Dear {name}, today is fertilizer application day for your {crop} crop (Day {day}). "
             f"Apply as per the recommended dosage. Best time: early morning or late evening. "
             f"Avoid application before expected rainfall ({rain_prob:.0f}% probability today)."),
            False,
        )

    elif task_type == "pest_check":
        return (
            f"Pest Monitoring Reminder — Day {day}",
            (f"Dear {name}, please inspect your {crop} field today (Day {day}). "
             f"Look for signs of pest damage, discoloration, or unusual growth patterns. "
             f"Early detection saves your crop!"),
            False,
        )

    elif task_type == "harvest":
        return (
            f"🎉 Harvest Time! — Day {day}",
            (f"Congratulations {name}! Your {crop} crop is ready for harvest (Day {day}). "
             f"Check grain/fruit maturity before harvesting. "
             f"Choose a dry day — rain probability today is {rain_prob:.0f}%."),
            False,
        )

    elif task_type == "sowing":
        return (
            f"Sowing Reminder — Day {day}",
            (f"Dear {name}, it's sowing/transplanting day for your {crop} crop (Day {day}). "
             f"Ensure field is prepared and seeds/seedlings are ready. "
             f"Good luck with your growing season!"),
            False,
        )

    else:
        return (
            f"{title} — Day {day}",
            (f"Dear {name}, today's task for your {crop} crop: {title} (Day {day}). "
             f"Please complete this task for optimal crop health."),
            False,
        )
