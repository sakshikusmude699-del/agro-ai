"""
Crop prediction router: /api/prediction
Combines weather data + ML model to recommend crops.
"""

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, date

from database import get_db
from models.schemas import FarmInput, PredictionResponse, CropSelection
from middleware.auth import get_current_user
from services.weather import get_weather
from services.ml_predictor import predict_crops
from services.timeline_generator import generate_timeline, get_total_days

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    data: FarmInput,
    current_user: dict = Depends(get_current_user),
):
    """
    Receive farm inputs, fetch weather, run ML model, return top 3 crops.
    Also stores farm data and prediction in the database.
    """
    db = get_db()
    user_id = str(current_user["_id"])

    # 1. Fetch weather for location
    try:
        weather = await get_weather(data.location)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e}")

    # 2. Save farm data
    farm_doc = {
        "user_id": user_id,
        "soil": data.soil.model_dump(),
        "location": data.location,
        "previous_crop": data.previous_crop,
        "created_at": datetime.utcnow(),
    }
    farm_result = await db.farm_data.insert_one(farm_doc)
    farm_id = str(farm_result.inserted_id)

    # 3. Run ML prediction
    try:
        ml_result = predict_crops(
            nitrogen=data.soil.nitrogen,
            phosphorus=data.soil.phosphorus,
            potassium=data.soil.potassium,
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            ph=data.soil.ph,
            rainfall=weather["rainfall"],
            previous_crop=data.previous_crop,
        )
    except FileNotFoundError:
        # Model not trained yet — return mock predictions
        ml_result = _mock_predictions()

    # 4. Store prediction in DB
    pred_doc = {
        "user_id": user_id,
        "farm_id": farm_id,
        "recommendations": ml_result["recommendations"],
        "previous_crop_option": ml_result["previous_crop_option"],
        "weather": weather,
        "created_at": datetime.utcnow(),
    }
    pred_result = await db.predictions.insert_one(pred_doc)
    prediction_id = str(pred_result.inserted_id)

    return PredictionResponse(
        prediction_id=prediction_id,
        recommendations=ml_result["recommendations"],
        previous_crop_option=ml_result["previous_crop_option"],
        weather=weather,
        farm_id=farm_id,
    )


@router.post("/select-crop")
async def select_crop(
    data: CropSelection,
    current_user: dict = Depends(get_current_user),
):
    """
    User selects a crop from recommendations.
    Generates and stores the full crop lifecycle timeline.
    """
    db = get_db()
    user_id = str(current_user["_id"])

    # Validate prediction exists
    try:
        pred = await db.predictions.find_one({"_id": ObjectId(data.prediction_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prediction ID")

    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Determine sowing date
    sowing_date = (
        date.fromisoformat(data.sowing_date) if data.sowing_date else date.today()
    )

    # Generate timeline
    tasks = generate_timeline(data.selected_crop, sowing_date)
    total_days = get_total_days(data.selected_crop)

    # Store timeline
    timeline_doc = {
        "user_id": user_id,
        "prediction_id": data.prediction_id,
        "crop": data.selected_crop,
        "sowing_date": sowing_date.isoformat(),
        "tasks": tasks,
        "total_days": total_days,
        "active": True,
        "created_at": datetime.utcnow(),
    }
    timeline_result = await db.timelines.insert_one(timeline_doc)

    # Update prediction with selection
    await db.predictions.update_one(
        {"_id": ObjectId(data.prediction_id)},
        {"$set": {"selected_crop": data.selected_crop, "timeline_id": str(timeline_result.inserted_id)}},
    )

    return {
        "message": f"Crop '{data.selected_crop}' selected successfully!",
        "timeline_id": str(timeline_result.inserted_id),
        "crop": data.selected_crop,
        "sowing_date": sowing_date.isoformat(),
        "total_tasks": len(tasks),
        "total_days": total_days,
    }


def _mock_predictions():
    """Return mock predictions when model is not trained."""
    return {
        "recommendations": [
            {"crop": "Rice", "confidence": 82.4, "is_rotation_friendly": True,
             "reason": "High humidity and rainfall suit paddy cultivation well."},
            {"crop": "Maize", "confidence": 71.1, "is_rotation_friendly": True,
             "reason": "Warm climate and good phosphorus levels favor maize."},
            {"crop": "Chickpea", "confidence": 65.5, "is_rotation_friendly": True,
             "reason": "Low moisture and neutral pH suit chickpea perfectly."},
        ],
        "previous_crop_option": None,
    }
