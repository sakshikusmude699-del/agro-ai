"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ─── Auth Models ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    location: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    location: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Farm Data Models ─────────────────────────────────────────────────────────

class SoilData(BaseModel):
    nitrogen: float = Field(..., ge=0, le=140, description="Nitrogen (N) ratio in soil")
    phosphorus: float = Field(..., ge=5, le=145, description="Phosphorus (P) ratio in soil")
    potassium: float = Field(..., ge=5, le=205, description="Potassium (K) ratio in soil")
    ph: float = Field(..., ge=3.5, le=10, description="Soil pH level")
    moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")


class FarmInput(BaseModel):
    soil: SoilData
    location: str = Field(..., description="City name for weather lookup")
    previous_crop: Optional[str] = None
    avoid_previous: bool = True


class FarmDataResponse(BaseModel):
    farm_id: str
    user_id: str
    soil: SoilData
    location: str
    previous_crop: Optional[str]
    created_at: datetime


# ─── Prediction Models ────────────────────────────────────────────────────────

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    description: str


class CropRecommendation(BaseModel):
    crop: str
    confidence: float
    is_rotation_friendly: bool
    reason: str


class PredictionResponse(BaseModel):
    prediction_id: str
    recommendations: List[CropRecommendation]
    previous_crop_option: Optional[CropRecommendation]
    weather: WeatherData
    farm_id: str


class CropSelection(BaseModel):
    prediction_id: str
    selected_crop: str
    sowing_date: Optional[str] = None  # ISO date string, defaults to today


# ─── Timeline Models ──────────────────────────────────────────────────────────

class TimelineTask(BaseModel):
    day: int
    task_type: str   # sowing, irrigation, fertilizer, pest_check, harvest
    title: str
    description: str
    completed: bool = False
    skipped: bool = False
    skip_reason: Optional[str] = None


class TimelineResponse(BaseModel):
    timeline_id: str
    user_id: str
    crop: str
    sowing_date: str
    tasks: List[TimelineTask]
    current_day: int
    total_days: int


# ─── Notification Models ──────────────────────────────────────────────────────

class NotificationRecord(BaseModel):
    notification_id: str
    user_id: str
    message: str
    task_type: str
    date: datetime
    status: str   # sent, failed, skipped


# ─── Chat Models ──────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    language: str = "en"   # "en", "hi", "mr"


class ChatResponse(BaseModel):
    reply: str
    language: str
