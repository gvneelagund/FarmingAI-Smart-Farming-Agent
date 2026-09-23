# FarmingAI — AI Agent for Smart Farming Advice

FarmingAI is an AI-agent-based smart agriculture application designed to provide farmers with practical, data-informed farming guidance through a Streamlit dashboard.

## Problem Statement

**Problem Statement No. 14 — AI Agent for Smart Farming Advice**

The project addresses the challenge of providing farmers with accessible, integrated assistance for crop selection, weather and irrigation planning, pest and disease diagnosis, market-related analysis, and agricultural knowledge.

## Key Capabilities

FarmingAI uses a central `FarmingOrchestrator` with five specialized agents:

1. **Crop Advisory Agent** — crop/seed recommendations, fertilizer guidance, and crop schedules.
2. **Weather & Irrigation Agent** — current weather, forecast information, and irrigation recommendations using OpenWeatherMap.
3. **Pest & Disease Detection Agent** — crop/leaf image diagnosis using a multimodal Groq model, with a text-based fallback.
4. **Market Insights Agent** — MSP/cost-oriented analysis and break-even calculations.
5. **Agricultural Knowledge / RAG Agent** — retrieves information from a curated 12-topic agricultural knowledge base using keyword/tag matching.

The Streamlit interface presents the functionality through a multi-tab dashboard and includes Plotly-based visualizations.

## Technology Stack

- Python 3.11+
- Streamlit
- Groq API
- Groq Llama models
- Llama 4 Scout Vision for multimodal crop/leaf analysis
- OpenWeatherMap API
- Plotly
- Pandas / NumPy
- Pillow
- python-dotenv

## Project Structure

```text
FarmingAI/
├── app.py
├── config.py
├── requirements.txt
├── run.bat
├── README.md
├── ProblemStatement_No14_SmartAgriculture.pdf
├── FarmingAI_Project_Presentation_Template_Matched.pptx
├── .env.example
├── .gitignore
└── agents/
    ├── __init__.py
    ├── orchestrator.py
    ├── crop_advisory_agent.py
    ├── weather_agent.py
    ├── pest_agent.py
    ├── market_agent.py
    └── knowledge_agent.py
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/gvneelagund/FarmingAI-Smart-Farming-Agent.git
cd FarmingAI-Smart-Farming-Agent
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv myenv
myenv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure API keys

Create a file named `.env` in the project root.

```env
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
```

**Never commit `.env` or real API keys to GitHub.**

The repository includes `.env.example` only to show the required variable names.

### 5. Run the application

```powershell
streamlit run app.py
```

Or, on Windows, you can use:

```powershell
run.bat
```

## API Keys

### Groq API

FarmingAI uses the Groq API for its language and multimodal AI processing.

Create a Groq API key from the official Groq developer platform and place it only in your local `.env` file.

### OpenWeatherMap API

The Weather & Irrigation Agent uses OpenWeatherMap for current weather and forecast information.

Create an OpenWeatherMap API key and place it only in your local `.env` file.

Do not publish either key in source code, screenshots, documentation, or Git history.

## Agent Workflow

```text
Farmer Profile / Query
        |
        v
FarmingOrchestrator
        |
        +--> Crop Advisory Agent
        +--> Weather & Irrigation Agent
        +--> Pest & Disease Agent
        +--> Market Insights Agent
        +--> Agricultural Knowledge / RAG Agent
        |
        v
Integrated Farming Advice
        |
        v
Streamlit Dashboard
```

## Agricultural Knowledge Retrieval

The current knowledge component uses a curated 12-topic agricultural knowledge base with **keyword/tag-based matching**. It is not a vector database or embedding-based semantic retrieval system.

Possible future improvements include vector/semantic RAG and a persistent knowledge store.

## Security

- Keep `.env` local.
- Use `.env.example` for variable-name documentation only.
- Never hard-code API keys in Python files.
- If an API key is exposed, revoke/rotate it immediately.

## Future Scope

Potential extensions include:

- Vector/semantic RAG with embeddings
- IoT soil-moisture and environmental sensors
- Automated irrigation integration
- Multilingual and voice interaction
- Live mandi/eNAM market data
- Satellite/NDVI-based crop monitoring
- Persistent database support
- WhatsApp/SMS farmer notifications
- Integration with IBM watsonx / Granite models

## Project Files

- `app.py` — Streamlit application entry point.
- `config.py` — configuration and environment settings.
- `agents/orchestrator.py` — coordinates the specialized agents.
- `agents/crop_advisory_agent.py` — crop recommendations and advisory.
- `agents/weather_agent.py` — weather and irrigation functionality.
- `agents/pest_agent.py` — pest/disease analysis.
- `agents/market_agent.py` — market and break-even analysis.
- `agents/knowledge_agent.py` — agricultural knowledge retrieval.
- `requirements.txt` — Python dependencies.
- `run.bat` — Windows launch helper.

## Disclaimer

FarmingAI provides AI-generated informational guidance for educational and decision-support purposes. Recommendations should be validated with local agricultural experts, agronomists, government advisories, and current local conditions before making important farming, financial, chemical, or crop-management decisions.
