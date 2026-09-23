"""
Weather & Irrigation Agent
Fetches real-time weather from OpenWeatherMap and generates irrigation advice via Groq.
"""

import requests
from groq import Groq
from config import GROQ_API_KEY, OPENWEATHER_API_KEY, FAST_MODEL

OWM_BASE = "https://api.openweathermap.org/data/2.5"
OWM_GEO  = "https://api.openweathermap.org/geo/1.0"


def _get_coordinates(location: str) -> tuple[float, float] | None:
    """Convert city/location name to lat/lon."""
    if not OPENWEATHER_API_KEY:
        return None
    try:
        r = requests.get(
            f"{OWM_GEO}/direct",
            params={"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY},
            timeout=8,
        )
        data = r.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
    except Exception:
        pass
    return None


def _fetch_current_weather(lat: float, lon: float) -> dict | None:
    try:
        r = requests.get(
            f"{OWM_BASE}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=8,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _fetch_forecast(lat: float, lon: float) -> dict | None:
    try:
        r = requests.get(
            f"{OWM_BASE}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt": 8,           # 24 hours (3-hourly × 8)
            },
            timeout=8,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _mock_weather(location: str) -> dict:
    """Fallback simulated weather when no API key is provided."""
    return {
        "source": "simulated",
        "location": location,
        "temperature": 28,
        "feels_like": 31,
        "humidity": 65,
        "wind_speed": 12,
        "description": "Partly cloudy",
        "rainfall_24h": 0,
        "forecast_summary": (
            "Partly cloudy with chances of light rain in next 24 hours. "
            "Temperatures expected between 24-32°C. Humidity 60-70%."
        ),
    }


def get_weather_data(location: str) -> dict:
    """Return structured weather data for the given location."""
    coords = _get_coordinates(location) if OPENWEATHER_API_KEY else None

    if coords is None:
        return _mock_weather(location)

    lat, lon = coords
    current = _fetch_current_weather(lat, lon)
    forecast = _fetch_forecast(lat, lon)

    if current is None:
        return _mock_weather(location)

    rainfall = current.get("rain", {}).get("1h", 0) * 24  # approximate 24h

    # Summarise next-day forecast
    fc_temps = []
    fc_rain = 0.0
    if forecast and "list" in forecast:
        for item in forecast["list"]:
            fc_temps.append(item["main"]["temp"])
            fc_rain += item.get("rain", {}).get("3h", 0)

    forecast_summary = (
        f"Next 24h: Temp range {min(fc_temps):.0f}–{max(fc_temps):.0f}°C, "
        f"Expected rainfall {fc_rain:.1f} mm."
        if fc_temps
        else "Forecast unavailable."
    )

    return {
        "source": "OpenWeatherMap",
        "location": current.get("name", location),
        "temperature": current["main"]["temp"],
        "feels_like": current["main"]["feels_like"],
        "humidity": current["main"]["humidity"],
        "wind_speed": current["wind"]["speed"],
        "description": current["weather"][0]["description"].capitalize(),
        "rainfall_24h": rainfall,
        "forecast_summary": forecast_summary,
    }


class WeatherIrrigationAgent:
    """Weather & Irrigation Agent — real-time weather + LLM-driven irrigation advice."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.name = "Weather & Irrigation Agent"

    def get_advice(self, location: str, crop: str, soil_type: str, growth_stage: str) -> tuple[dict, str]:
        weather = get_weather_data(location)

        weather_summary = (
            f"Location: {weather['location']}\n"
            f"Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)\n"
            f"Humidity: {weather['humidity']}%\n"
            f"Wind Speed: {weather['wind_speed']} km/h\n"
            f"Condition: {weather['description']}\n"
            f"Rainfall last 24h: {weather['rainfall_24h']} mm\n"
            f"Forecast: {weather['forecast_summary']}\n"
            f"Data Source: {weather['source']}"
        )

        system_prompt = (
            "You are an expert Irrigation and Weather Agronomist. Based on current weather conditions, "
            "provide precise irrigation scheduling, water quantity recommendations, and weather-related "
            "farming advisories. Include: irrigation frequency, amount per session, best time of day to "
            "irrigate, any weather risk warnings, and adjustments needed for the current conditions."
        )

        user_message = (
            f"Weather Data:\n{weather_summary}\n\n"
            f"Crop: {crop}\n"
            f"Soil Type: {soil_type}\n"
            f"Current Growth Stage: {growth_stage}\n\n"
            "Provide detailed irrigation scheduling and weather-based farming advice for the next 7 days."
        )

        response = self.client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=900,
        )

        return weather, response.choices[0].message.content
