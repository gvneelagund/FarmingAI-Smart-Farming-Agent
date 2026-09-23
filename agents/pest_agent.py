"""
Pest & Disease Detection Agent
Uses Groq's vision model to analyse uploaded crop images and identify pests/diseases.
"""

import base64
from io import BytesIO
from PIL import Image
from groq import Groq
from config import GROQ_API_KEY, VISION_MODEL, PRIMARY_MODEL


def _image_to_base64(image: Image.Image, max_size: int = 1024) -> str:
    """Resize and encode a PIL image to a base64 JPEG string."""
    # Downscale if needed (API limits)
    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        image = image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    buf = BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class PestDiseaseAgent:
    """Multimodal Pest & Disease Detection Agent using Groq vision."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.name = "Pest & Disease Detection Agent"

    def analyse_image(self, image: Image.Image, crop_type: str, symptoms: str) -> dict:
        """
        Analyse a crop image for pests and diseases.

        Returns a dict with keys:
          detected_issues, severity, affected_area_estimate,
          treatment_chemical, treatment_biological, prevention, urgency
        """
        b64 = _image_to_base64(image)

        system_prompt = (
            "You are an expert Plant Pathologist and Entomologist with 20+ years of experience. "
            "Analyse the provided crop image and identify ANY visible pests, diseases, nutrient deficiencies, "
            "or abnormalities. Provide a structured JSON-like response with: "
            "1. Detected Issues (list each issue with confidence %) "
            "2. Severity Level (Low/Medium/High/Critical) "
            "3. Estimated % of plant/crop affected "
            "4. Chemical treatment recommendation (product name, dose, frequency) "
            "5. Biological/organic alternative treatment "
            "6. Prevention measures for future "
            "7. Urgency (Immediate action needed / Monitor / Routine). "
            "If the image is not a plant/crop, clearly state that."
        )

        user_message = [
            {
                "type": "text",
                "text": (
                    f"Crop Type: {crop_type}\n"
                    f"Observed Symptoms: {symptoms}\n\n"
                    "Please analyse this crop image and provide a detailed diagnosis with treatment recommendations."
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            },
        ]

        response = self.client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1200,
        )

        raw = response.choices[0].message.content

        # Parse structured sections from the text response
        return {"raw_analysis": raw, "crop_type": crop_type, "symptoms": symptoms}

    def get_text_diagnosis(self, crop_type: str, symptoms: str, location: str) -> str:
        """Text-only pest/disease diagnosis when no image is available."""
        system_prompt = (
            "You are a Plant Disease and Pest Expert. Based on the described symptoms, "
            "identify the most likely pest or disease, provide diagnosis confidence, "
            "and give immediate actionable treatment steps with specific chemical/biological products, "
            "dosages, and application methods."
        )

        user_message = (
            f"Crop: {crop_type}\n"
            f"Location/Region: {location}\n"
            f"Symptoms Observed: {symptoms}\n\n"
            "Diagnose the pest/disease and provide treatment protocol."
        )

        response = self.client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=900,
        )
        return response.choices[0].message.content
