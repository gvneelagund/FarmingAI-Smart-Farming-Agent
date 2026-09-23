import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Groq Models
PRIMARY_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
FAST_MODEL = "llama-3.1-8b-instant"

# App Config
APP_TITLE = "🌾 FarmingAI — Smart Farming Agent"
APP_ICON = "🌾"
