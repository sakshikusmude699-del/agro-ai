"""
Notifications router: /api/notifications
"""

from fastapi import APIRouter, Depends
from bson import ObjectId
from datetime import datetime

from database import get_db
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/history")
async def get_notification_history(current_user: dict = Depends(get_current_user)):
    """Get all notifications sent to the current user."""
    db = get_db()
    cursor = db.notifications.find(
        {"user_id": str(current_user["_id"])},
        sort=[("date", -1)],
        limit=50,
    )
    notifications = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        notifications.append(doc)
    return notifications


@router.post("/trigger-daily")
async def trigger_daily_check(current_user: dict = Depends(get_current_user)):
    """
    Manually trigger the daily notification check for the current user.
    Useful for testing.
    """
    from scheduler.notification_logic import check_and_notify_user
    user_id = str(current_user["_id"])
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    count = await check_and_notify_user(user)
    return {"message": f"Triggered check. {count} notification(s) sent."}
