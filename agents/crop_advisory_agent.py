"""
Crop Advisory Agent
Generates personalised seed selection, fertiliser schedules, and harvest timelines
based on the farmer's profile and land conditions.
"""

from groq import Groq
from config import GROQ_API_KEY, PRIMARY_MODEL


# Crop calendar reference data
CROP_CALENDAR = {
    "rice": {"kharif": {"sow": "Jun–Jul", "harvest": "Oct–Nov"}, "rabi": {"sow": "Nov–Dec", "harvest": "Mar–Apr"}},
    "wheat": {"rabi": {"sow": "Oct–Nov", "harvest": "Mar–Apr"}},
    "maize": {"kharif": {"sow": "Jun–Jul", "harvest": "Sep–Oct"}, "rabi": {"sow": "Dec–Jan", "harvest": "Apr–May"}},
    "cotton": {"kharif": {"sow": "May–Jun", "harvest": "Nov–Jan"}},
    "soybean": {"kharif": {"sow": "Jun–Jul", "harvest": "Sep–Oct"}},
    "tomato": {"year_round": {"sow": "Jun–Jul / Oct–Nov / Jan–Feb", "harvest": "90-120 days after transplant"}},
    "sugarcane": {"year_round": {"sow": "Feb–Mar / Oct–Nov", "harvest": "12-14 months after planting"}},
    "mustard": {"rabi": {"sow": "Oct–Nov", "harvest": "Feb–Mar"}},
    "groundnut": {"kharif": {"sow": "Jun–Jul", "harvest": "Sep–Oct"}},
    "onion": {"rabi": {"sow": "Oct–Nov", "harvest": "Mar–Apr"}},
}

SEED_RECOMMENDATIONS = {
    "rice": ["Swarna Sub1 (flood tolerant)", "Pusa Basmati 1121 (aromatic)", "IR-64 (high yield)", "DRR Dhan 44"],
    "wheat": ["HD-2967 (high yield)", "WB-02 (rust resistant)", "PBW-343 (Punjab)", "K-307 (UP)"],
    "maize": ["Pioneer 30V92 (hybrid)", "DKC-9144 (drought tolerant)", "Vivek QPM-9 (quality protein)"],
    "cotton": ["Bunny BG-II (Bt hybrid)", "Rasi 659 BG-II", "NHH-44 (non-BT)"],
    "tomato": ["Arka Rakshak (disease resistant)", "Pusa Ruby (open pollinated)", "US-440 (hybrid)"],
    "soybean": ["JS-9560 (high yield)", "NRC-7 (early maturing)", "MACS-450 (broad adaptation)"],
    "sugarcane": ["Co-0238 (high sugar %)", "CoSe-92423 (early maturing)", "CoJ-64"],
    "mustard": ["Pusa Bold (high oil%)", "RH-749 (hybrid)", "Bio-902"],
    "groundnut": ["ICGV-86031 (ICRISAT)", "TAG-24 (high yield)", "GG-20 (drought tolerant)"],
    "onion": ["Agrifound Dark Red", "Pusa Red", "N-53"],
}


class CropAdvisoryAgent:
    """Personalised Crop Advisory Agent."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.name = "Crop Advisory Agent"

    def get_seed_recommendations(self, crop: str) -> list[str]:
        return SEED_RECOMMENDATIONS.get(crop.lower(), ["Consult local agricultural extension officer for seed varieties."])

    def get_crop_calendar(self, crop: str, season: str) -> dict:
        crop_data = CROP_CALENDAR.get(crop.lower(), {})
        return crop_data.get(season.lower(), crop_data.get("year_round", {}))

    def generate_advisory(self, farmer_profile: dict) -> str:
        crop = farmer_profile.get("crop", "rice")
        seeds = self.get_seed_recommendations(crop)
        calendar = self.get_crop_calendar(crop, farmer_profile.get("season", "kharif"))

        seeds_str = "\n".join(f"  • {s}" for s in seeds[:4])
        calendar_str = (
            f"Sowing: {calendar.get('sow', 'N/A')} | Harvest: {calendar.get('harvest', 'N/A')}"
            if calendar
            else "Refer local KVK for planting schedule."
        )

        system_prompt = (
            "You are a Senior Crop Science Advisor. Generate a comprehensive, personalised farming plan "
            "covering: 1) Best seed varieties with reasons, 2) Complete fertiliser schedule (basal + top dressing) "
            "with specific doses, 3) Irrigation schedule aligned to crop stages, 4) Pesticide/fungicide calendar, "
            "5) Harvesting timeline and indicators, 6) Expected yield range, 7) Special tips for the farmer's "
            "specific conditions. Be specific with quantities, dates/days, and product names."
        )

        user_message = (
            f"Farmer Profile:\n"
            f"  Name: {farmer_profile.get('name', 'Farmer')}\n"
            f"  Location: {farmer_profile.get('location', 'N/A')}\n"
            f"  Crop: {crop}\n"
            f"  Land Area: {farmer_profile.get('land_area', 'N/A')} acres\n"
            f"  Soil Type: {farmer_profile.get('soil_type', 'N/A')}\n"
            f"  Season: {farmer_profile.get('season', 'N/A')}\n"
            f"  Irrigation Source: {farmer_profile.get('irrigation', 'N/A')}\n"
            f"  Previous Crop: {farmer_profile.get('prev_crop', 'N/A')}\n"
            f"  Budget (₹/acre): {farmer_profile.get('budget', 'N/A')}\n\n"
            f"Recommended Seed Varieties:\n{seeds_str}\n\n"
            f"Crop Calendar Reference: {calendar_str}\n\n"
            "Generate a complete season-long advisory plan."
        )

        response = self.client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=1400,
        )
        return response.choices[0].message.content
