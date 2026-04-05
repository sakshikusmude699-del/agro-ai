"""
Weather service: fetches current + forecast data from OpenWeatherMap.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"


async def get_weather(location: str) -> dict:
    """
    Fetch current weather + 7-day rain probability for a location.
    Returns: {temperature, humidity, rainfall, rain_probability, description}
    """
    if not API_KEY:
        # Return mock data if no API key (for development)
        return _mock_weather()

    async with httpx.AsyncClient(timeout=10) as client:
        # Current weather
        current_resp = await client.get(
            f"{BASE_URL}/weather",
            params={"q": location, "appid": API_KEY, "units": "metric"},
        )
        current_resp.raise_for_status()
        current = current_resp.json()

        # 5-day forecast (3-hour intervals)
        forecast_resp = await client.get(
            f"{BASE_URL}/forecast",
            params={"q": location, "appid": API_KEY, "units": "metric"},
        )
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()

    temp = current["main"]["temp"]
    humidity = current["main"]["humidity"]
    description = current["weather"][0]["description"]

    # Estimate 7-day rainfall from forecast entries
    rain_mm = sum(
        entry.get("rain", {}).get("3h", 0)
        for entry in forecast["list"][:56]  # 56 * 3h = 7 days
    )

    # Estimate rain probability (max pop in next 24 hrs)
    rain_prob = max(
        (entry.get("pop", 0) * 100) for entry in forecast["list"][:8]
    )

    return {
        "temperature": round(temp, 1),
        "humidity": round(humidity, 1),
        "rainfall": round(rain_mm, 1),
        "rain_probability": round(rain_prob, 1),
        "description": description,
    }


async def get_rain_probability_today(location: str) -> float:
    """Return today's max rain probability (0–100) for notification logic."""
    data = await get_weather(location)
    return data.get("rain_probability", 0.0)


def _mock_weather() -> dict:
    """Mock weather data for development without API key."""
    return {
        "temperature": 28.5,
        "humidity": 65.0,
        "rainfall": 5.2,
        "rain_probability": 30.0,
        "description": "partly cloudy (mock)",
    }
