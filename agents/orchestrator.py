"""
Multi-Agent Orchestrator
Coordinates all farming agents into a unified comprehensive report.
"""

from groq import Groq
from config import GROQ_API_KEY, PRIMARY_MODEL
from agents.knowledge_agent import AgriculturalKnowledgeAgent
from agents.weather_agent import WeatherIrrigationAgent
from agents.crop_advisory_agent import CropAdvisoryAgent
from agents.market_agent import MarketInsightsAgent


class FarmingOrchestrator:
    """
    Orchestrates all agents to produce a holistic farming advisory.
    Acts as the master coordinator — delegates tasks to specialised agents
    and synthesises the combined output into actionable insights.
    """

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.knowledge_agent = AgriculturalKnowledgeAgent()
        self.weather_agent = WeatherIrrigationAgent()
        self.crop_agent = CropAdvisoryAgent()
        self.market_agent = MarketInsightsAgent()

    def run_full_advisory(self, farmer_profile: dict, progress_callback=None) -> dict:
        """
        Run all agents sequentially and return a combined results dict.
        progress_callback(step: int, message: str) is called between steps.
        """
        results = {}

        def _progress(step, msg):
            if progress_callback:
                progress_callback(step, msg)

        # ── Step 1: Crop Advisory ────────────────────────────────────────────
        _progress(1, "🌱 Crop Advisory Agent generating personalised plan…")
        results["crop_advisory"] = self.crop_agent.generate_advisory(farmer_profile)

        # ── Step 2: Weather & Irrigation ────────────────────────────────────
        _progress(2, "🌦️ Weather & Irrigation Agent fetching conditions…")
        weather_data, weather_advice = self.weather_agent.get_advice(
            location=farmer_profile.get("location", "Delhi"),
            crop=farmer_profile.get("crop", "rice"),
            soil_type=farmer_profile.get("soil_type", "loamy"),
            growth_stage=farmer_profile.get("growth_stage", "vegetative"),
        )
        results["weather_data"] = weather_data
        results["weather_advice"] = weather_advice

        # ── Step 3: Market Insights ──────────────────────────────────────────
        _progress(3, "📈 Market Insights Agent analysing prices & costs…")
        market_data, cost_analysis, market_advice = self.market_agent.generate_insights(farmer_profile)
        results["market_data"] = market_data
        results["cost_analysis"] = cost_analysis
        results["market_advice"] = market_advice

        # ── Step 4: Knowledge RAG ────────────────────────────────────────────
        _progress(4, "📚 Agricultural Knowledge Agent retrieving best practices…")
        crop = farmer_profile.get("crop", "rice")
        rag_query = (
            f"Best practices for {crop} cultivation including fertilizer, irrigation, pest control, "
            f"and harvesting in {farmer_profile.get('soil_type', 'loamy')} soil"
        )
        results["knowledge_advice"] = self.knowledge_agent.answer(rag_query, farmer_profile)

        # ── Step 5: Master Summary ───────────────────────────────────────────
        _progress(5, "🤖 Orchestrator synthesising comprehensive report…")
        results["master_summary"] = self._synthesise(farmer_profile, results)

        return results

    def _synthesise(self, farmer_profile: dict, results: dict) -> str:
        """Combine all agent outputs into a single executive summary."""
        system_prompt = (
            "You are the Chief Agricultural Intelligence Coordinator. You have received reports from "
            "4 specialised AI agents: Crop Advisory, Weather & Irrigation, Market Insights, and "
            "Agricultural Knowledge. Synthesise all information into a concise, prioritised action plan. "
            "Format: 1) Top 5 Immediate Actions (this week), 2) Short-term Plan (next 30 days), "
            "3) Season-long Strategy, 4) Key Risks & Mitigation, 5) Expected Outcome summary. "
            "Be actionable, specific, and farmer-friendly."
        )

        farmer_str = (
            f"Farmer: {farmer_profile.get('name', 'Farmer')}, "
            f"Crop: {farmer_profile.get('crop', 'N/A')}, "
            f"Location: {farmer_profile.get('location', 'N/A')}, "
            f"Land: {farmer_profile.get('land_area', 'N/A')} acres"
        )

        user_message = (
            f"{farmer_str}\n\n"
            f"CROP ADVISORY HIGHLIGHTS:\n{results.get('crop_advisory','')[:600]}\n\n"
            f"WEATHER & IRRIGATION:\n{results.get('weather_advice','')[:400]}\n\n"
            f"MARKET INSIGHTS:\n{results.get('market_advice','')[:400]}\n\n"
            f"AGRICULTURAL KNOWLEDGE:\n{results.get('knowledge_advice','')[:400]}\n\n"
            "Synthesise these into a comprehensive executive farming action plan."
        )

        response = self.client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1200,
        )
        return response.choices[0].message.content
