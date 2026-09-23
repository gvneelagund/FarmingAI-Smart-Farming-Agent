"""
Agricultural Knowledge RAG Agent
Uses an in-memory knowledge base + Groq LLM to answer crop/farming queries.
"""

import json
import numpy as np
from groq import Groq
from config import GROQ_API_KEY, PRIMARY_MODEL

# ---------------------------------------------------------------------------
# Static knowledge base (acts as the RAG corpus)
# ---------------------------------------------------------------------------
FARMING_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "topic": "Rice Cultivation",
        "content": (
            "Rice requires 20-25°C temperature. Transplanting should be done 20-25 days after sowing. "
            "Apply 120 kg N, 60 kg P2O5, and 60 kg K2O per hectare. Use SRI (System of Rice Intensification) "
            "for water saving. Harvest when 80-85% grains turn golden yellow. "
            "Common pests: Brown Plant Hopper, Stem Borer. Use Carbofuran 3G @ 25 kg/ha for stem borer control."
        ),
        "tags": ["rice", "paddy", "cereal", "water", "transplanting"],
    },
    {
        "id": "kb_002",
        "topic": "Wheat Cultivation",
        "content": (
            "Wheat is a rabi crop sown October–December. Optimum temperature 20–25°C during germination. "
            "Apply 120 kg N, 60 kg P, 40 kg K per hectare. Sow seeds 5–6 cm deep at 22.5 cm row spacing. "
            "Irrigate at crown root initiation (21 DAS), tillering (45 DAS), jointing (65 DAS). "
            "Yellow rust is a major disease; use Propiconazole 25 EC spray. Harvest at golden yellow stage."
        ),
        "tags": ["wheat", "rabi", "cereal", "irrigation"],
    },
    {
        "id": "kb_003",
        "topic": "Tomato Cultivation",
        "content": (
            "Tomato grows best at 21–24°C. Use hybrid varieties like Arka Rakshak, Pusa Ruby. "
            "Transplant 25-30 day old seedlings. Apply 200 kg N, 100 kg P, 100 kg K per hectare in splits. "
            "Drip irrigation saves 30-40% water. Common diseases: Early blight, Late blight — use Mancozeb. "
            "Fruit borer control: Spinosad 45 SC @ 0.15 ml/L. Harvest 60-70 days after transplanting."
        ),
        "tags": ["tomato", "vegetable", "drip", "hybrid"],
    },
    {
        "id": "kb_004",
        "topic": "Soil Health Management",
        "content": (
            "Ideal soil pH for most crops: 6.0–7.5. Conduct soil test every 3 years. "
            "Add lime to raise pH; sulfur to lower it. Organic matter improves water retention. "
            "Apply FYM (Farm Yard Manure) @ 10-15 tonnes/ha annually. "
            "Green manure crops like Sesbania improve nitrogen by 40-60 kg/ha. "
            "Micronutrient deficiency: Zinc deficiency — apply ZnSO4 @ 25 kg/ha. "
            "Boron deficiency in mustard — apply Borax 10 kg/ha."
        ),
        "tags": ["soil", "pH", "fertilizer", "organic", "micronutrient"],
    },
    {
        "id": "kb_005",
        "topic": "Integrated Pest Management (IPM)",
        "content": (
            "IPM combines biological, cultural, mechanical, and chemical methods. "
            "Use pheromone traps to monitor pest population. Release Trichogramma cards @ 50,000/ha for egg parasitism. "
            "Neem-based pesticides (NSKE 5%) are eco-friendly. "
            "Spray thresholds: apply pesticides only when pest density crosses economic threshold. "
            "Rotate pesticides to prevent resistance. Use sticky yellow traps for whitefly and aphid monitoring."
        ),
        "tags": ["pest", "IPM", "biological", "neem", "trichogramma"],
    },
    {
        "id": "kb_006",
        "topic": "Cotton Farming",
        "content": (
            "Cotton requires 180-200 frost-free days. Sow May-June in north India. "
            "Bt cotton has built-in resistance to bollworm. Apply 180 kg N, 80 kg P, 60 kg K/ha. "
            "Pink bollworm is a key pest — use pheromone traps. "
            "Whitefly spreads leaf curl virus; use Imidacloprid seed treatment. "
            "Harvest when bolls open fully, over 3-4 pickings. Avoid water stress during boll development."
        ),
        "tags": ["cotton", "bt", "bollworm", "kharif"],
    },
    {
        "id": "kb_007",
        "topic": "Maize Cultivation",
        "content": (
            "Maize grows in temperature 21–27°C. Sow June-July for kharif, January-February for rabi. "
            "Plant population: 65,000-75,000 plants/ha. Apply 150 kg N, 75 kg P, 50 kg K/ha in 3 splits. "
            "Critical irrigation at knee-high, tasseling, and grain filling stages. "
            "Fall Armyworm (FAW) is a major threat — spray Chlorantraniliprole 18.5 SC @ 0.4 ml/L. "
            "Harvest at physiological maturity (black layer formation at kernel base)."
        ),
        "tags": ["maize", "corn", "kharif", "rabi", "FAW"],
    },
    {
        "id": "kb_008",
        "topic": "Water & Irrigation Management",
        "content": (
            "Drip irrigation saves 40-50% water vs flood irrigation. "
            "Sprinkler irrigation suits flat terrain and covers large areas. "
            "Soil moisture sensor-based irrigation improves WUE (Water Use Efficiency). "
            "Critical crop water stages: rice (tillering, panicle initiation), wheat (crown root, jointing), "
            "maize (tasseling, silking). Deficit irrigation during vegetative stage is tolerable but avoid during reproductive."
        ),
        "tags": ["irrigation", "drip", "sprinkler", "water", "moisture"],
    },
    {
        "id": "kb_009",
        "topic": "Organic Farming Practices",
        "content": (
            "Organic farming avoids synthetic chemicals. Use compost, vermicompost, and biofertilizers. "
            "Rhizobium inoculant for legumes fixes 50-200 kg N/ha. Azospirillum and PSB (Phosphate Solubilizing Bacteria) "
            "improve nutrient availability. Crop rotation with legumes builds soil nitrogen. "
            "Certification takes 3 years conversion period. Premium price for organic produce is 20-50% higher."
        ),
        "tags": ["organic", "compost", "biofertilizer", "certification", "vermicompost"],
    },
    {
        "id": "kb_010",
        "topic": "Government Schemes for Farmers",
        "content": (
            "PM-KISAN: ₹6,000/year direct income support in 3 installments. "
            "Pradhan Mantri Fasal Bima Yojana (PMFBY): Crop insurance at 2% premium for kharif, 1.5% for rabi. "
            "Kisan Credit Card (KCC): Short-term credit at 4% interest for crop production. "
            "PM Krishi Sinchai Yojana: Subsidy on drip and sprinkler irrigation up to 55-75%. "
            "eNAM (National Agriculture Market): Online platform for MSP-based price discovery and trade."
        ),
        "tags": ["scheme", "government", "insurance", "credit", "subsidy"],
    },
    {
        "id": "kb_011",
        "topic": "Sugarcane Cultivation",
        "content": (
            "Sugarcane requires 75-150 cm annual rainfall and 25-30°C temperature. "
            "Plant February-March (spring) or October-November (autumn). Use 3-eye setts at 90 cm row spacing. "
            "Apply 250 kg N, 115 kg P, 115 kg K per hectare. "
            "Ratoon crop reduces cost by 30-40%. Harvest 12-14 months after planting. "
            "Pyrilla pest: use Epiricania melanoleuca egg parasitoid for biological control."
        ),
        "tags": ["sugarcane", "ratoon", "setts", "tropical"],
    },
    {
        "id": "kb_012",
        "topic": "Soybean Farming",
        "content": (
            "Soybean is a kharif legume fixing 40-100 kg N/ha. Sow June-July with 45 cm row spacing. "
            "Use Bradyrhizobium inoculant for nitrogen fixation. Apply starter nitrogen 20 kg/ha. "
            "Critical irrigation at flowering and pod filling. "
            "Girdle beetle and whitefly are key pests. Avoid waterlogging at any stage. "
            "Harvest when leaves turn yellow and pods rattle. Yield 1.5-2.5 tonnes/ha under good management."
        ),
        "tags": ["soybean", "legume", "kharif", "nitrogen", "Bradyrhizobium"],
    },
]


def _simple_keyword_search(query: str, top_k: int = 3) -> list[dict]:
    """Keyword-overlap retrieval — no external embedding model needed."""
    query_words = set(query.lower().split())
    scored = []
    for doc in FARMING_KNOWLEDGE_BASE:
        text = (doc["topic"] + " " + doc["content"] + " " + " ".join(doc["tags"])).lower()
        score = sum(1 for w in query_words if w in text)
        # Tag exact match bonus
        score += sum(2 for tag in doc["tags"] if tag in query.lower())
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k] if _ > 0] or [scored[0][1]]


class AgriculturalKnowledgeAgent:
    """RAG-based Agricultural Knowledge Agent powered by Groq."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.name = "Agricultural Knowledge Agent"

    def retrieve_context(self, query: str) -> str:
        docs = _simple_keyword_search(query, top_k=3)
        context_parts = []
        for doc in docs:
            context_parts.append(f"[{doc['topic']}]\n{doc['content']}")
        return "\n\n---\n\n".join(context_parts)

    def answer(self, query: str, farmer_profile: dict | None = None) -> str:
        context = self.retrieve_context(query)
        profile_str = ""
        if farmer_profile:
            profile_str = (
                f"\nFarmer Profile: Location={farmer_profile.get('location','N/A')}, "
                f"Crop={farmer_profile.get('crop','N/A')}, "
                f"Land={farmer_profile.get('land_area','N/A')} acres, "
                f"Soil Type={farmer_profile.get('soil_type','N/A')}, "
                f"Season={farmer_profile.get('season','N/A')}"
            )

        system_prompt = (
            "You are an expert Agricultural Knowledge Advisor with deep knowledge of crop science, "
            "soil science, and sustainable farming practices. Use the retrieved knowledge context to "
            "give accurate, practical, and actionable advice. Always provide specific recommendations "
            "with quantities, timings, and methods. Format your response with clear sections."
        )

        user_message = (
            f"Knowledge Base Context:\n{context}\n"
            f"{profile_str}\n\n"
            f"Farmer's Question: {query}\n\n"
            "Provide detailed, personalized agricultural advice based on the context and farmer profile."
        )

        response = self.client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=1024,
        )
        return response.choices[0].message.content
