"""
AI Chat router: /api/chat
Uses Anthropic Claude API for farming Q&A.
"""

import os
import anthropic
from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv

from models.schemas import ChatMessage, ChatResponse
from middleware.auth import get_current_user
from database import get_db

load_dotenv()
router = APIRouter()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are AgroSmart AI, an expert farming assistant for Indian farmers.
You have deep knowledge of:
- Crop selection and rotation practices
- Soil health and fertilizer recommendations  
- Pest and disease management
- Irrigation scheduling
- Seasonal farming calendar for India
- Organic and conventional farming methods

Keep responses concise, practical, and farmer-friendly. Use simple language.
When asked in Hindi or Marathi, respond in the same language.
Always give actionable advice tailored to Indian farming conditions.
Format: short paragraphs, no excessive bullet points."""


@router.post("/message", response_model=ChatResponse)
async def chat(
    msg: ChatMessage,
    current_user: dict = Depends(get_current_user),
):
    """Send a farming question and get an AI response."""
    if not ANTHROPIC_API_KEY:
        # Mock response for development
        return ChatResponse(
            reply=_mock_response(msg.message),
            language=msg.language,
        )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # Add user context to the message
        db = get_db()
        # Get latest farm data for context
        farm_data = await db.farm_data.find_one(
            {"user_id": str(current_user["_id"])},
            sort=[("created_at", -1)],
        )

        context = ""
        if farm_data:
            soil = farm_data.get("soil", {})
            context = (
                f"\n[User's farm context: Location={farm_data.get('location','N/A')}, "
                f"N={soil.get('nitrogen','?')}, P={soil.get('phosphorus','?')}, "
                f"K={soil.get('potassium','?')}, pH={soil.get('ph','?')}, "
                f"Previous crop={farm_data.get('previous_crop','None')}]"
            )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": msg.message + context}],
        )

        reply = response.content[0].text
        return ChatResponse(reply=reply, language=msg.language)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


def _mock_response(message: str) -> str:
    """Simple keyword-based mock responses for development."""
    msg_lower = message.lower()
    if "crop" in msg_lower and "grow" in msg_lower:
        return ("Based on seasonal patterns, consider rice or wheat depending on your region. "
                "Use the Crop Recommendation tool for a personalized suggestion based on your soil data.")
    elif "fertilizer" in msg_lower:
        return ("For most crops, a balanced NPK fertilizer (like 10-26-26) as basal dose works well. "
                "Add urea as top dressing at vegetative stage. Always do a soil test first.")
    elif "pest" in msg_lower or "disease" in msg_lower:
        return ("Integrated Pest Management (IPM) is best. Use neem-based sprays for mild infestations. "
                "For fungal diseases, apply Mancozeb or Carbendazim. Monitor fields regularly.")
    elif "water" in msg_lower or "irrigation" in msg_lower:
        return ("Drip irrigation saves 40–60% water. For most field crops, irrigate at critical stages: "
                "germination, flowering, and grain fill. Avoid waterlogging.")
    else:
        return ("Great question! For personalized advice, I recommend entering your soil data in the "
                "Farm Input section. I can then give you crop-specific recommendations based on your exact conditions.")
