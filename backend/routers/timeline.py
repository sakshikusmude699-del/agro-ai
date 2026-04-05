"""
Timeline router: /api/timeline
"""

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import date

from database import get_db
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/active")
async def get_active_timeline(current_user: dict = Depends(get_current_user)):
    """Get the currently active crop timeline for the user."""
    db = get_db()
    doc = await db.timelines.find_one(
        {"user_id": str(current_user["_id"]), "active": True},
        sort=[("created_at", -1)],
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No active timeline found")

    # Calculate current day
    sowing = date.fromisoformat(doc["sowing_date"])
    current_day = (date.today() - sowing).days + 1

    doc["_id"] = str(doc["_id"])
    doc["current_day"] = current_day
    return doc


@router.get("/all")
async def get_all_timelines(current_user: dict = Depends(get_current_user)):
    """Get all crop timelines for the user (history)."""
    db = get_db()
    cursor = db.timelines.find(
        {"user_id": str(current_user["_id"])},
        sort=[("created_at", -1)],
    )
    timelines = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        sowing = date.fromisoformat(doc["sowing_date"])
        doc["current_day"] = (date.today() - sowing).days + 1
        timelines.append(doc)
    return timelines


@router.patch("/{timeline_id}/task/{day}/complete")
async def complete_task(
    timeline_id: str,
    day: int,
    current_user: dict = Depends(get_current_user),
):
    """Mark a specific day's task as completed."""
    db = get_db()
    result = await db.timelines.update_one(
        {
            "_id": ObjectId(timeline_id),
            "user_id": str(current_user["_id"]),
            "tasks.day": day,
        },
        {"$set": {"tasks.$.completed": True}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task marked as completed"}
