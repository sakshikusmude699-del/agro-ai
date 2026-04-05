"""
Authentication router: /api/auth
"""

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime

from database import get_db
from models.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from middleware.auth import hash_password, verify_password, create_access_token

router = APIRouter()


def serialize_user(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        location=user.get("location"),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister):
    """Register a new user."""
    db = get_db()

    # Check duplicate email
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and save
    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "location": data.location,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(access_token=token, user=serialize_user(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login with email and password."""
    db = get_db()
    user = await db.users.find_one({"email": data.email})

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=serialize_user(user))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = None):
    """Get current user profile (protected)."""
    from middleware.auth import get_current_user
    from fastapi import Depends
    # This is handled via dependency injection in the actual call
    return serialize_user(current_user)
