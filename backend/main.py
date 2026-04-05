"""
AgroSmart AI - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import connect_db, disconnect_db
from routers import auth, farm, prediction, timeline, notifications, chat
from scheduler.job_runner import start_scheduler, stop_scheduler

load_dotenv()

# ─── Lifespan: startup & shutdown ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    await connect_db()
    start_scheduler()
    yield
    stop_scheduler()
    await disconnect_db()

# ─── App Init ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AgroSmart AI",
    description="AI-powered farming assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth.router,          prefix="/api/auth",          tags=["Authentication"])
app.include_router(farm.router,          prefix="/api/farm",          tags=["Farm Data"])
app.include_router(prediction.router,    prefix="/api/prediction",    tags=["Crop Prediction"])
app.include_router(timeline.router,      prefix="/api/timeline",      tags=["Crop Timeline"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(chat.router,          prefix="/api/chat",          tags=["AI Chat"])

# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "AgroSmart AI is running 🌱"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
