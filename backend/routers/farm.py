"""
Farm data router: /api/farm
"""

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime

from database import get_db
from models.schemas import FarmInput, FarmDataResponse
from middleware.auth import get_current_user

router = APIRouter()


@router.post("/input", response_model=FarmDataResponse, status_code=201)
async def save_farm_input(
    data: FarmInput,
    current_user: dict = Depends(get_current_user),
):
    """Save farm soil and location data for the current user."""
    db = get_db()
    user_id = str(current_user["_id"])

    farm_doc = {
        "user_id": user_id,
        "soil": data.soil.model_dump(),
        "location": data.location,
        "previous_crop": data.previous_crop,
        "avoid_previous": data.avoid_previous,
        "created_at": datetime.utcnow(),
    }
    result = await db.farm_data.insert_one(farm_doc)

    return FarmDataResponse(
        farm_id=str(result.inserted_id),
        user_id=user_id,
        soil=data.soil,
        location=data.location,
        previous_crop=data.previous_crop,
        created_at=farm_doc["created_at"],
    )


@router.get("/latest")
async def get_latest_farm_data(current_user: dict = Depends(get_current_user)):
    """Get the most recent farm input for the current user."""
    db = get_db()
    doc = await db.farm_data.find_one(
        {"user_id": str(current_user["_id"])},
        sort=[("created_at", -1)],
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No farm data found")

    doc["_id"] = str(doc["_id"])
    return doc
