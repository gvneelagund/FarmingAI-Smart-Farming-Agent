"""
Market Insights Agent
Forecasts crop demand, suggests market prices, and recommends cost-efficient practices.
"""

from groq import Groq
from config import GROQ_API_KEY, FAST_MODEL

# Reference MSP data (₹/quintal) — 2023-24 season
MSP_DATA = {
    "rice": {"msp": 2183, "trend": "stable", "demand": "high"},
    "wheat": {"msp": 2275, "trend": "rising", "demand": "high"},
    "maize": {"msp": 2090, "trend": "rising", "demand": "high"},
    "cotton": {"msp": 7020, "trend": "stable", "demand": "medium"},
    "soybean": {"msp": 4600, "trend": "falling", "demand": "medium"},
    "sugarcane": {"msp": 315, "trend": "stable", "demand": "high"},  # per quintal FRP
    "mustard": {"msp": 5650, "trend": "rising", "demand": "high"},
    "groundnut": {"msp": 6377, "trend": "stable", "demand": "medium"},
    "onion": {"msp": None, "trend": "volatile", "demand": "high"},
    "tomato": {"msp": None, "trend": "volatile", "demand": "high"},
    "pulses": {"msp": 7000, "trend": "rising", "demand": "high"},
}

# Average input costs per acre (₹)
INPUT_COSTS = {
    "rice": {"seeds": 800, "fertilizer": 2500, "pesticide": 1200, "labor": 4000, "irrigation": 1500},
    "wheat": {"seeds": 600, "fertilizer": 2000, "pesticide": 800, "labor": 2500, "irrigation": 1200},
    "maize": {"seeds": 500, "fertilizer": 1800, "pesticide": 900, "labor": 2000, "irrigation": 1000},
    "cotton": {"seeds": 900, "fertilizer": 3000, "pesticide": 2500, "labor": 5000, "irrigation": 2000},
    "tomato": {"seeds": 1200, "fertilizer": 3500, "pesticide": 2000, "labor": 6000, "irrigation": 2500},
    "soybean": {"seeds": 700, "fertilizer": 1200, "pesticide": 800, "labor": 1800, "irrigation": 800},
    "default": {"seeds": 700, "fertilizer": 2000, "pesticide": 1000, "labor": 3000, "irrigation": 1200},
}


def _calculate_cost_analysis(crop: str, land_area: float) -> dict:
    costs = INPUT_COSTS.get(crop.lower(), INPUT_COSTS["default"])
    total_per_acre = sum(costs.values())
    total = total_per_acre * land_area
    return {
        "per_acre_costs": costs,
        "total_per_acre": total_per_acre,
        "total_cost": total,
        "land_area": land_area,
    }


class MarketInsightsAgent:
    """Market Insights Agent — pricing, demand forecast, and cost optimisation."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.name = "Market Insights Agent"

    def get_market_data(self, crop: str) -> dict:
        return MSP_DATA.get(crop.lower(), {"msp": "N/A", "trend": "unknown", "demand": "unknown"})

    def get_cost_analysis(self, crop: str, land_area: float) -> dict:
        return _calculate_cost_analysis(crop, land_area)

    def generate_insights(self, farmer_profile: dict) -> tuple[dict, dict, str]:
        crop = farmer_profile.get("crop", "rice")
        land_area = float(farmer_profile.get("land_area", 1))

        market_data = self.get_market_data(crop)
        cost_analysis = self.get_cost_analysis(crop, land_area)

        msp_str = f"₹{market_data['msp']}/quintal" if market_data["msp"] else "No MSP (market-driven)"

        system_prompt = (
            "You are an Agricultural Economist and Market Analyst. Provide comprehensive market insights "
            "including: 1) Current price trends and MSP analysis, 2) Demand-supply forecast for next 3-6 months, "
            "3) Best markets/mandis to sell (eNAM, local APMC), 4) Cost reduction strategies with specific tips, "
            "5) Value addition opportunities (storage, processing), 6) Income maximisation strategies, "
            "7) Risk factors and mitigation. Provide realistic price projections with reasoning."
        )

        user_message = (
            f"Farmer Profile:\n"
            f"  Crop: {crop}\n"
            f"  Land Area: {land_area} acres\n"
            f"  Location: {farmer_profile.get('location', 'N/A')}\n"
            f"  Season: {farmer_profile.get('season', 'N/A')}\n"
            f"  Budget: ₹{farmer_profile.get('budget', 'N/A')}/acre\n\n"
            f"Market Reference Data:\n"
            f"  MSP: {msp_str}\n"
            f"  Price Trend: {market_data['trend']}\n"
            f"  Market Demand: {market_data['demand']}\n\n"
            f"Estimated Input Costs:\n"
            f"  Total per acre: ₹{cost_analysis['total_per_acre']:,}\n"
            f"  Total for {land_area} acres: ₹{cost_analysis['total_cost']:,.0f}\n\n"
            "Provide detailed market insights, price forecasts, and income optimisation strategies."
        )

        response = self.client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=1000,
        )

        return market_data, cost_analysis, response.choices[0].message.content
