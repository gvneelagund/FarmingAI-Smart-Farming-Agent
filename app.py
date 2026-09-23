"""
FarmingAI — Smart Farming Agentic Application
Streamlit frontend that ties together all farming agents.
"""

import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import APP_TITLE, APP_ICON, GROQ_API_KEY
from agents.knowledge_agent import AgriculturalKnowledgeAgent
from agents.weather_agent import WeatherIrrigationAgent, get_weather_data
from agents.pest_agent import PestDiseaseAgent
from agents.crop_advisory_agent import CropAdvisoryAgent
from agents.market_agent import MarketInsightsAgent
from agents.orchestrator import FarmingOrchestrator

# ─────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FarmingAI",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS  (v2 — rich colours + animations)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ════════════════════════════════════════
       KEYFRAME ANIMATIONS
    ════════════════════════════════════════ */
    @keyframes fadeSlideDown {
        from { opacity: 0; transform: translateY(-18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; } to { opacity: 1; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(76,175,80,0.45); }
        50%       { box-shadow: 0 0 0 10px rgba(76,175,80,0); }
    }
    @keyframes shimmer {
        0%   { background-position: -600px 0; }
        100% { background-position:  600px 0; }
    }
    @keyframes spinLeaf {
        0%   { transform: rotate(0deg) scale(1); }
        50%  { transform: rotate(180deg) scale(1.15); }
        100% { transform: rotate(360deg) scale(1); }
    }
    @keyframes borderDance {
        0%,100% { border-color: #43a047; }
        33%      { border-color: #00acc1; }
        66%      { border-color: #fb8c00; }
    }
    @keyframes float {
        0%,100% { transform: translateY(0px); }
        50%      { transform: translateY(-6px); }
    }
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.7); }
        to   { opacity: 1; transform: scale(1); }
    }

    /* ════════════════════════════════════════
       GLOBAL / APP BACKGROUND
    ════════════════════════════════════════ */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 10% 10%, rgba(56,142,60,0.12) 0%, transparent 55%),
            radial-gradient(ellipse at 90% 90%, rgba(0,172,193,0.10) 0%, transparent 55%),
            linear-gradient(160deg, #f1f8f1 0%, #e8f5e9 40%, #e0f2f1 70%, #fafffe 100%);
        min-height: 100vh;
    }
    /* scrollbar */
    ::-webkit-scrollbar { width: 7px; }
    ::-webkit-scrollbar-track { background: #e8f5e9; }
    ::-webkit-scrollbar-thumb { background: #66bb6a; border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: #43a047; }

    /* ════════════════════════════════════════
       SIDEBAR
    ════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(195deg, #0a3d14 0%, #1b5e20 30%, #2e7d32 65%, #1565c0 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #e8f5e9 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] label { color: #b9f6ca !important; font-size: 0.82rem !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18) !important; }

    /* ════════════════════════════════════════
       ANIMATED HEADER BANNER
    ════════════════════════════════════════ */
    .farm-header {
        background: linear-gradient(120deg, #0a3d14 0%, #1b5e20 25%, #2e7d32 50%, #00695c 75%, #00838f 100%);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite, fadeSlideDown 0.7s ease both;
        border-radius: 20px;
        padding: 2.2rem 2.8rem;
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 32px rgba(27,94,32,0.35), 0 2px 8px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    @keyframes gradientShift {
        0%,100% { background-position: 0% 50%; }
        50%      { background-position: 100% 50%; }
    }
    .farm-header::before {
        content: "";
        position: absolute; top: -40%; right: -8%;
        width: 280px; height: 280px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .farm-header::after {
        content: "";
        position: absolute; bottom: -50%; left: 5%;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }
    .farm-header h1 {
        font-size: 2.8rem; font-weight: 900; margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .farm-header p {
        font-size: 1.05rem; margin: 0.5rem 0 0;
        opacity: 0.88; font-weight: 400;
    }
    .farm-header .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        margin-top: 0.7rem;
        backdrop-filter: blur(4px);
    }

    /* ════════════════════════════════════════
       TABS
    ════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.6);
        padding: 6px 8px;
        border-radius: 14px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(76,175,80,0.2);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.45rem 1.1rem;
        font-weight: 600;
        font-size: 0.88rem;
        color: #2e7d32 !important;
        transition: all 0.25s ease;
        border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(76,175,80,0.12) !important;
        border-color: rgba(76,175,80,0.3) !important;
        transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2e7d32, #00695c) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(46,125,50,0.4) !important;
        border-color: transparent !important;
    }

    /* ════════════════════════════════════════
       BUTTONS
    ════════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(135deg, #1b5e20, #2e7d32, #00695c);
        background-size: 200% 200%;
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 0.55rem 1.6rem;
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
        box-shadow: 0 3px 12px rgba(46,125,50,0.35);
    }
    .stButton > button:hover {
        background-position: right center;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46,125,50,0.45);
    }
    .stButton > button:active { transform: translateY(0); }

    /* ════════════════════════════════════════
       AGENT CARDS  (animated entry)
    ════════════════════════════════════════ */
    .agent-card {
        background: white;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        border-left: 5px solid #43a047;
        box-shadow: 0 3px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: fadeSlideUp 0.5s ease both;
    }
    .agent-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(46,125,50,0.18);
    }
    .agent-card h4 { color: #1b5e20; margin: 0 0 0.4rem; font-size: 1rem; font-weight: 700; }

    /* ════════════════════════════════════════
       SECTION CARDS  (glowing border)
    ════════════════════════════════════════ */
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        border: 1px solid rgba(76,175,80,0.2);
        margin-bottom: 1.2rem;
        animation: fadeSlideUp 0.6s ease both;
        transition: box-shadow 0.3s;
    }
    .section-card:hover { box-shadow: 0 8px 32px rgba(46,125,50,0.15); }

    /* ════════════════════════════════════════
       METRIC CARDS (animated, colour-coded)
    ════════════════════════════════════════ */
    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-top: 4px solid #43a047;
        animation: countUp 0.5s ease both;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
    .metric-card .metric-value { font-size: 1.85rem; font-weight: 800; color: #1b5e20; }
    .metric-card .metric-label { font-size: 0.78rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card.blue  { border-top-color: #0288d1; }
    .metric-card.orange{ border-top-color: #f57c00; }
    .metric-card.teal  { border-top-color: #00838f; }
    .metric-card.red   { border-top-color: #c62828; }

    /* ════════════════════════════════════════
       STAT PILL BADGES
    ════════════════════════════════════════ */
    .stat-pill {
        display: inline-flex; align-items: center; gap: 6px;
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border: 1px solid #a5d6a7;
        border-radius: 20px;
        padding: 0.3rem 0.9rem;
        font-size: 0.83rem;
        font-weight: 600;
        color: #1b5e20;
        margin: 0.2rem 0.2rem;
    }

    /* ════════════════════════════════════════
       PROFILE SUMMARY BAR
    ════════════════════════════════════════ */
    .profile-bar {
        background: linear-gradient(135deg, #e8f5e9, #e0f7fa);
        border: 1px solid #a5d6a7;
        border-radius: 12px;
        padding: 0.7rem 1.2rem;
        font-size: 0.9rem;
        color: #1b5e20;
        font-weight: 500;
        margin-bottom: 1rem;
        animation: fadeIn 0.6s ease;
    }

    /* ════════════════════════════════════════
       ALERT BOXES
    ════════════════════════════════════════ */
    .alert-success {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border: 1px solid #81c784;
        border-left: 4px solid #43a047;
        border-radius: 10px; padding: 0.9rem 1.2rem; margin: 0.5rem 0;
        animation: fadeSlideUp 0.4s ease;
    }
    .alert-warning {
        background: linear-gradient(135deg, #fff8e1, #fffde7);
        border: 1px solid #ffd54f;
        border-left: 4px solid #ffa000;
        border-radius: 10px; padding: 0.9rem 1.2rem; margin: 0.5rem 0;
        animation: fadeSlideUp 0.4s ease;
    }
    .alert-danger {
        background: linear-gradient(135deg, #ffebee, #fce4ec);
        border: 1px solid #ef9a9a;
        border-left: 4px solid #e53935;
        border-radius: 10px; padding: 0.9rem 1.2rem; margin: 0.5rem 0;
        animation: fadeSlideUp 0.4s ease;
    }
    .alert-info {
        background: linear-gradient(135deg, #e3f2fd, #e8eaf6);
        border: 1px solid #90caf9;
        border-left: 4px solid #1976d2;
        border-radius: 10px; padding: 0.9rem 1.2rem; margin: 0.5rem 0;
        animation: fadeSlideUp 0.4s ease;
    }

    /* ════════════════════════════════════════
       CHAT BUBBLES
    ════════════════════════════════════════ */
    .chat-container { max-height: 440px; overflow-y: auto; padding: 0.5rem; }
    .chat-user {
        background: linear-gradient(135deg, #e3f2fd, #e8eaf6);
        border-radius: 18px 18px 4px 18px;
        padding: 0.85rem 1.1rem;
        margin: 0.6rem 0;
        max-width: 82%;
        margin-left: auto;
        box-shadow: 0 2px 10px rgba(25,118,210,0.15);
        border: 1px solid rgba(144,202,249,0.4);
        animation: fadeSlideUp 0.3s ease;
    }
    .chat-bot {
        background: linear-gradient(135deg, #ffffff, #f1f8f1);
        border-radius: 18px 18px 18px 4px;
        padding: 0.85rem 1.1rem;
        margin: 0.6rem 0;
        max-width: 82%;
        box-shadow: 0 2px 10px rgba(46,125,50,0.12);
        border-left: 4px solid #43a047;
        animation: fadeSlideUp 0.3s ease;
    }

    /* ════════════════════════════════════════
       QUICK QUESTION CHIPS
    ════════════════════════════════════════ */
    .stButton[data-testid*="quick"] > button {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9) !important;
        color: #2e7d32 !important;
        border: 1.5px solid #a5d6a7 !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.8rem !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        transition: all 0.2s !important;
    }
    .stButton[data-testid*="quick"] > button:hover {
        background: linear-gradient(135deg, #c8e6c9, #dcedc8) !important;
        transform: translateY(-1px) !important;
    }

    /* ════════════════════════════════════════
       EXPANDERS
    ════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #1b5e20 !important;
        border: 1px solid #c8e6c9 !important;
        transition: all 0.2s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #dcedc8, #c8e6c9) !important;
        box-shadow: 0 3px 12px rgba(46,125,50,0.15) !important;
    }
    .streamlit-expanderContent {
        border: 1px solid #e8f5e9 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        animation: fadeSlideDown 0.3s ease;
    }

    /* ════════════════════════════════════════
       PROGRESS BAR
    ════════════════════════════════════════ */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1b5e20, #43a047, #00acc1) !important;
        border-radius: 10px !important;
        animation: shimmer 1.8s infinite linear;
        background-size: 600px 100% !important;
    }

    /* ════════════════════════════════════════
       SPINNER
    ════════════════════════════════════════ */
    .stSpinner > div { border-top-color: #43a047 !important; }

    /* ════════════════════════════════════════
       DATAFRAME / TABLE
    ════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 3px 14px rgba(0,0,0,0.07);
        border: 1px solid #e8f5e9 !important;
        animation: fadeIn 0.5s ease;
    }

    /* ════════════════════════════════════════
       FILE UPLOADER
    ════════════════════════════════════════ */
    [data-testid="stFileUploader"] {
        border: 2px dashed #81c784 !important;
        border-radius: 14px !important;
        background: linear-gradient(135deg, #f1f8e9, #fafffe) !important;
        transition: border-color 0.3s, background 0.3s;
        padding: 1rem !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #43a047 !important;
        background: linear-gradient(135deg, #e8f5e9, #e0f7fa) !important;
    }

    /* ════════════════════════════════════════
       RADIO BUTTONS
    ════════════════════════════════════════ */
    [data-testid="stRadio"] label {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        border: 1.5px solid #c8e6c9;
        border-radius: 10px;
        padding: 0.4rem 1rem;
        margin: 0.2rem;
        font-weight: 500;
        color: #1b5e20;
        transition: all 0.2s;
        cursor: pointer;
    }
    [data-testid="stRadio"] label:hover {
        background: linear-gradient(135deg, #dcedc8, #c8e6c9);
        border-color: #81c784;
        transform: translateY(-1px);
    }

    /* ════════════════════════════════════════
       SELECTBOX / TEXT INPUT
    ════════════════════════════════════════ */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 9px !important;
        border: 1.5px solid #c8e6c9 !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #43a047 !important;
        box-shadow: 0 0 0 3px rgba(67,160,71,0.15) !important;
    }

    /* ════════════════════════════════════════
       AGENT PIPELINE STEP BOXES
    ════════════════════════════════════════ */
    .pipeline-step {
        display: flex; align-items: center; gap: 12px;
        background: linear-gradient(135deg, #f1f8f1, #e8f5e9);
        border-radius: 10px;
        padding: 0.7rem 1.1rem;
        margin: 0.35rem 0;
        border-left: 4px solid #43a047;
        font-weight: 500;
        font-size: 0.9rem;
        color: #1b5e20;
        animation: fadeSlideUp 0.4s ease both;
    }
    .pipeline-step .step-num {
        background: linear-gradient(135deg, #2e7d32, #00695c);
        color: white;
        width: 26px; height: 26px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.78rem; font-weight: 700;
        flex-shrink: 0;
    }

    /* ════════════════════════════════════════
       FLOATING AGENT CARDS (About tab)
    ════════════════════════════════════════ */
    .agent-about-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        border-top: 4px solid #43a047;
        text-align: center;
        animation: float 4s ease-in-out infinite;
        transition: box-shadow 0.3s;
    }
    .agent-about-card:hover { box-shadow: 0 10px 32px rgba(46,125,50,0.2); animation: none; transform: translateY(-4px); }
    .agent-about-card .card-icon { font-size: 2rem; }
    .agent-about-card h4 { color: #1b5e20; margin: 0.4rem 0 0.2rem; font-size: 0.95rem; }
    .agent-about-card p  { color: #555; font-size: 0.8rem; margin: 0; }

    /* ════════════════════════════════════════
       SECTION HEADINGS
    ════════════════════════════════════════ */
    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1b5e20;
        border-left: 5px solid #43a047;
        padding-left: 0.8rem;
        margin: 1.2rem 0 0.8rem;
        animation: fadeSlideDown 0.4s ease;
    }

    /* ════════════════════════════════════════
       HIDE STREAMLIT CHROME
    ════════════════════════════════════════ */
    #MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
def _init_session():
    defaults = {
        "chat_history": [],
        "farmer_profile": {},
        "advisory_results": None,
        "agents_initialised": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ─────────────────────────────────────────────
# Agent singleton cache
# ─────────────────────────────────────────────
@st.cache_resource
def load_agents():
    return {
        "knowledge": AgriculturalKnowledgeAgent(),
        "weather": WeatherIrrigationAgent(),
        "pest": PestDiseaseAgent(),
        "crop": CropAdvisoryAgent(),
        "market": MarketInsightsAgent(),
        "orchestrator": FarmingOrchestrator(),
    }


# ─────────────────────────────────────────────
# Sidebar — Farmer Profile
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 👨‍🌾 Farmer Profile")
        st.markdown("---")

        name = st.text_input("Your Name", value="Ramesh Kumar", key="sb_name")
        location = st.text_input("📍 Location / City", value="Pune, Maharashtra", key="sb_location")

        crop = st.selectbox(
            "🌾 Primary Crop",
            ["rice", "wheat", "maize", "cotton", "tomato", "soybean",
             "sugarcane", "mustard", "groundnut", "onion"],
            key="sb_crop",
        )

        season = st.selectbox("🗓️ Season", ["kharif", "rabi", "zaid"], key="sb_season")

        soil_type = st.selectbox(
            "🪨 Soil Type",
            ["loamy", "clay", "sandy loam", "black cotton", "red laterite", "alluvial"],
            key="sb_soil",
        )

        land_area = st.number_input("🏡 Land Area (acres)", min_value=0.5, max_value=500.0,
                                    value=5.0, step=0.5, key="sb_land")

        irrigation = st.selectbox(
            "💧 Irrigation Source",
            ["canal", "borewell", "drip", "sprinkler", "rainfed", "river"],
            key="sb_irrigation",
        )

        growth_stage = st.selectbox(
            "🌿 Current Growth Stage",
            ["land preparation", "sowing", "germination", "vegetative",
             "flowering", "fruiting", "maturity", "harvest"],
            key="sb_stage",
        )

        prev_crop = st.text_input("🔄 Previous Crop", value="fallow", key="sb_prev")
        budget = st.number_input("💰 Budget (₹/acre)", min_value=1000, max_value=100000,
                                 value=15000, step=500, key="sb_budget")

        # Save profile
        st.session_state.farmer_profile = {
            "name": name,
            "location": location,
            "crop": crop,
            "season": season,
            "soil_type": soil_type,
            "land_area": land_area,
            "irrigation": irrigation,
            "growth_stage": growth_stage,
            "prev_crop": prev_crop,
            "budget": budget,
        }

        st.markdown("---")
        api_configured = bool(GROQ_API_KEY)
        if api_configured:
            st.success("✅ Groq API Connected")
        else:
            st.error("❌ Set GROQ_API_KEY in .env")

        st.markdown("---")
        st.markdown(
            "<p style='font-size:0.75rem;opacity:0.7;text-align:center'>"
            "FarmingAI v1.0 • Powered by Groq</p>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# Helper renderers
# ─────────────────────────────────────────────
def render_header():
    st.markdown(
        """
        <div class="farm-header">
            <h1>🌾 FarmingAI</h1>
            <p>Your AI-powered Smart Farming Companion — Personalised advice for better yield, less cost, more profit.</p>
            <div>
                <span class="header-badge">🤖 Multi-Agent AI</span>
                <span class="header-badge">🌦️ Live Weather</span>
                <span class="header-badge">🔬 Vision Analysis</span>
                <span class="header-badge">📈 Market Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_weather_card(weather: dict):
    cols = st.columns(4)
    metrics = [
        ("🌡️ Temperature", f"{weather['temperature']}°C", f"Feels {weather['feels_like']}°C"),
        ("💧 Humidity", f"{weather['humidity']}%", weather["description"]),
        ("🌬️ Wind Speed", f"{weather['wind_speed']} km/h", "Surface wind"),
        ("🌧️ Rainfall", f"{weather['rainfall_24h']} mm", "Last 24 hours"),
    ]
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.metric(label, value, delta)


def render_cost_chart(cost_analysis: dict):
    costs = cost_analysis["per_acre_costs"]
    labels = [k.replace("_", " ").title() for k in costs.keys()]
    values = list(costs.values())

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(
                colors=["#2e7d32", "#43a047", "#00acc1", "#f57c00", "#e53935"],
                line=dict(color="white", width=2),
            ),
            textfont=dict(size=13, color="white"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Input Cost Breakdown (per acre)", font=dict(size=14, color="#1b5e20")),
        height=320,
        margin=dict(t=45, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(font=dict(size=11), bgcolor="rgba(241,248,233,0.8)", bordercolor="#c8e6c9", borderwidth=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_agent_status_banner(active_agent: str):
    agent_icons = {
        "Crop Advisory Agent": "🌱",
        "Weather & Irrigation Agent": "🌦️",
        "Market Insights Agent": "📈",
        "Agricultural Knowledge Agent": "📚",
        "Orchestrator": "🤖",
    }
    icon = agent_icons.get(active_agent, "⚙️")
    st.info(f"{icon} **{active_agent}** is processing your request…")


# ─────────────────────────────────────────────
# TAB 1 — Full Advisory Dashboard
# ─────────────────────────────────────────────
def tab_full_advisory():
    st.markdown('<div class="section-title">🤖 Multi-Agent Full Farm Advisory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alert-info">⚡ Activates all 4 specialised AI agents in sequence — '
        'Crop Advisory → Weather & Irrigation → Market Insights → Knowledge RAG — '
        'then synthesises a master action plan.</div>',
        unsafe_allow_html=True,
    )

    profile = st.session_state.farmer_profile
    if not profile:
        st.warning("Fill in your Farmer Profile in the sidebar first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f'<div class="profile-bar">'
            f'👨‍🌾 <b>{profile.get("name")}</b> &nbsp;|&nbsp; '
            f'🌾 <b>{profile.get("crop","").title()}</b> &nbsp;|&nbsp; '
            f'📍 {profile.get("location")} &nbsp;|&nbsp; '
            f'🏡 {profile.get("land_area")} acres &nbsp;|&nbsp; '
            f'🗓️ {profile.get("season","").title()}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        run_btn = st.button("🚀 Run Full Advisory", use_container_width=True)

    if run_btn:
        agents = load_agents()
        orchestrator = agents["orchestrator"]

        progress_bar = st.progress(0)
        status_text = st.empty()
        total_steps = 5

        def update_progress(step: int, message: str):
            progress_bar.progress(step / total_steps)
            status_text.info(f"**Step {step}/{total_steps}:** {message}")

        with st.spinner("Multi-agent pipeline running…"):
            results = orchestrator.run_full_advisory(profile, progress_callback=update_progress)

        progress_bar.progress(1.0)
        status_text.success("✅ All agents completed successfully!")
        st.session_state.advisory_results = results

    results = st.session_state.advisory_results
    if not results:
        st.markdown(
            '<div class="alert-warning">ℹ️ Click <strong>🚀 Run Full Advisory</strong> above to activate all agents '
            'and generate your personalised farming plan.</div>',
            unsafe_allow_html=True,
        )
        # Pipeline preview
        st.markdown('<div class="section-title">🔄 Agent Pipeline</div>', unsafe_allow_html=True)
        steps = [
            ("1", "🌱", "Crop Advisory Agent", "Seeds · Fertiliser schedule · Harvest timeline"),
            ("2", "🌦️", "Weather & Irrigation Agent", "Live weather · Irrigation scheduling · 7-day forecast"),
            ("3", "📈", "Market Insights Agent", "MSP prices · Cost breakdown · Break-even analysis"),
            ("4", "📚", "Agricultural Knowledge Agent (RAG)", "Best practices · Crop guidelines · Pest control"),
            ("5", "🤖", "Orchestrator", "Synthesises all agent outputs → Master action plan"),
        ]
        for num, icon, name, desc in steps:
            st.markdown(
                f'<div class="pipeline-step">'
                f'<div class="step-num">{num}</div>'
                f'<div>{icon} <strong>{name}</strong> — <span style="color:#555;font-weight:400">{desc}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        return

    # ── Master Summary ───────────────────────────────────────────────────────
    with st.expander("🤖 **Master Summary — Orchestrator Output**", expanded=True):
        st.markdown(results.get("master_summary", ""))

    # ── Four-agent columns ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Individual Agent Reports</div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)

    with r1:
        with st.expander("🌱 Crop Advisory Agent", expanded=False):
            st.markdown(results.get("crop_advisory", ""))

    with r2:
        with st.expander("🌦️ Weather & Irrigation Agent", expanded=False):
            weather = results.get("weather_data", {})
            if weather:
                render_weather_card(weather)
            st.markdown(results.get("weather_advice", ""))

    r3, r4 = st.columns(2)

    with r3:
        with st.expander("📈 Market Insights Agent", expanded=False):
            cost = results.get("cost_analysis")
            if cost:
                render_cost_chart(cost)
            st.markdown(results.get("market_advice", ""))

    with r4:
        with st.expander("📚 Agricultural Knowledge Agent (RAG)", expanded=False):
            st.markdown(results.get("knowledge_advice", ""))


# ─────────────────────────────────────────────
# TAB 2 — Crop Advisory
# ─────────────────────────────────────────────
def tab_crop_advisory():
    st.markdown('<div class="section-title">🌱 Personalised Crop Advisory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alert-success">🌿 Get a complete season plan — seed varieties, fertiliser schedule, '
        'irrigation timing, pest calendar, and harvest indicators.</div>',
        unsafe_allow_html=True,
    )

    profile = st.session_state.farmer_profile
    agents = load_agents()

    if st.button("🌾 Generate Crop Advisory Plan", use_container_width=False):
        with st.spinner("Crop Advisory Agent working…"):
            advice = agents["crop"].generate_advisory(profile)
        st.session_state["crop_adv_result"] = advice

    if "crop_adv_result" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["crop_adv_result"])

        # Seed recommendations table
        seeds = agents["crop"].get_seed_recommendations(profile.get("crop", "rice"))
        st.markdown("#### 🌱 Recommended Seed Varieties")
        df = pd.DataFrame({"Variety": seeds, "Rank": range(1, len(seeds) + 1)})
        st.dataframe(df.set_index("Rank"), use_container_width=True)


# ─────────────────────────────────────────────
# TAB 3 — Weather & Irrigation
# ─────────────────────────────────────────────
def tab_weather():
    st.markdown('<div class="section-title">🌦️ Weather & Irrigation Advisory</div>', unsafe_allow_html=True)

    profile = st.session_state.farmer_profile
    agents = load_agents()

    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("📍 Location", value=profile.get("location", "Pune"), key="wx_location")
    with col2:
        growth_stage = st.selectbox(
            "Growth Stage",
            ["land preparation", "sowing", "germination", "vegetative",
             "flowering", "fruiting", "maturity"],
            index=3,
            key="wx_stage",
        )

    if st.button("🌤️ Get Weather & Irrigation Advice"):
        with st.spinner("Fetching weather data and generating advice…"):
            weather, advice = agents["weather"].get_advice(
                location=location,
                crop=profile.get("crop", "rice"),
                soil_type=profile.get("soil_type", "loamy"),
                growth_stage=growth_stage,
            )

        st.markdown("#### 🌡️ Current Weather Conditions")
        render_weather_card(weather)

        if weather.get("source") == "simulated":
            st.caption("⚠️ Using simulated weather data. Add OPENWEATHER_API_KEY in .env for real data.")

        st.markdown("---")
        st.markdown("#### 💧 Irrigation & Weather Advisory")
        st.markdown(advice)

        # 7-day temperature forecast chart
        st.markdown('<div class="section-title">📊 7-Day Temperature Forecast</div>', unsafe_allow_html=True)
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        base_temp = weather["temperature"]
        import random; random.seed(42)
        highs = [round(base_temp + random.uniform(0, 4), 1) for _ in days]
        lows  = [round(base_temp - random.uniform(2, 6), 1) for _ in days]
        mids  = [round((h + l) / 2, 1) for h, l in zip(highs, lows)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=highs, name="High °C",
            line=dict(color="#e53935", width=3, shape="spline"),
            mode="lines+markers",
            marker=dict(size=8, color="#e53935", symbol="circle"),
            fill="tonexty", fillcolor="rgba(229,57,53,0.07)",
        ))
        fig.add_trace(go.Scatter(
            x=days, y=mids, name="Average °C",
            line=dict(color="#43a047", width=2, dash="dot", shape="spline"),
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=days, y=lows, name="Low °C",
            line=dict(color="#1e88e5", width=3, shape="spline"),
            mode="lines+markers",
            marker=dict(size=8, color="#1e88e5", symbol="circle"),
        ))
        fig.update_layout(
            title=dict(text="7-Day Temperature Forecast (°C)", font=dict(size=14, color="#1b5e20")),
            yaxis_title="Temperature (°C)",
            height=300,
            margin=dict(t=45, b=10, l=10, r=10),
            plot_bgcolor="rgba(241,248,233,0.6)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#c8e6c9", borderwidth=1),
            xaxis=dict(gridcolor="rgba(200,230,201,0.5)"),
            yaxis=dict(gridcolor="rgba(200,230,201,0.5)"),
        )
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 4 — Pest & Disease Detection
# ─────────────────────────────────────────────
def tab_pest_detection():
    st.markdown('<div class="section-title">🔬 Pest & Disease Detection</div>', unsafe_allow_html=True)

    agents = load_agents()
    profile = st.session_state.farmer_profile

    detection_mode = st.radio(
        "Detection Mode",
        ["📸 Upload Crop Image (Vision AI)", "📝 Describe Symptoms (Text AI)"],
        horizontal=True,
    )

    if detection_mode == "📸 Upload Crop Image (Vision AI)":
        st.markdown("Upload a clear photo of the affected plant part (leaf, stem, fruit, etc.)")

        uploaded_file = st.file_uploader(
            "Choose an image", type=["jpg", "jpeg", "png", "webp"], key="pest_img"
        )

        symptoms = st.text_area(
            "Describe what you observe (optional but helps accuracy):",
            placeholder="e.g., Yellow spots on leaves, wilting, holes in leaves, sticky residue…",
            height=80,
        )

        if uploaded_file and st.button("🔍 Analyse Image"):
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded crop image", width=400)

            with st.spinner("Vision AI analysing the image…"):
                result = agents["pest"].analyse_image(
                    image=image,
                    crop_type=profile.get("crop", "unknown"),
                    symptoms=symptoms or "No additional description provided.",
                )

            st.markdown("---")
            st.markdown("#### 🧬 AI Diagnosis Report")
            st.markdown(result["raw_analysis"])

    else:
        col1, col2 = st.columns(2)
        with col1:
            crop_type = st.text_input("Crop Type", value=profile.get("crop", "rice"), key="pd_crop")
        with col2:
            location = st.text_input("Location", value=profile.get("location", "N/A"), key="pd_loc")

        symptoms = st.text_area(
            "Describe symptoms in detail:",
            placeholder=(
                "e.g., Brown circular spots on leaves with yellow halo, "
                "appearing first on lower leaves, 30% of plants affected…"
            ),
            height=120,
        )

        if st.button("🔍 Diagnose Pest/Disease"):
            if not symptoms:
                st.warning("Please describe the symptoms you observed.")
                return
            with st.spinner("Diagnosing based on symptoms…"):
                result = agents["pest"].get_text_diagnosis(
                    crop_type=crop_type,
                    symptoms=symptoms,
                    location=location,
                )
            st.markdown("---")
            st.markdown("#### 🧬 AI Diagnosis Report")
            st.markdown(result)


# ─────────────────────────────────────────────
# TAB 5 — Market Insights
# ─────────────────────────────────────────────
def tab_market():
    st.markdown('<div class="section-title">📈 Market & Cost Insights</div>', unsafe_allow_html=True)

    agents = load_agents()
    profile = st.session_state.farmer_profile

    if st.button("💹 Generate Market Analysis"):
        with st.spinner("Market Insights Agent analysing…"):
            market_data, cost_analysis, advice = agents["market"].generate_insights(profile)

        # MSP card
        msp = market_data.get("msp")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("MSP Price", f"₹{msp}/qtl" if msp else "Market-driven", market_data.get("trend", "").title())
        with c2:
            st.metric("Market Demand", market_data.get("demand", "N/A").title(), "")
        with c3:
            st.metric("Total Input Cost", f"₹{cost_analysis['total_cost']:,.0f}", f"For {cost_analysis['land_area']} acres")

        # Cost breakdown pie
        render_cost_chart(cost_analysis)

        # Break-even analysis
        if msp:
            expected_yield_per_acre = 20  # quintals (conservative)
            total_expected_revenue = msp * expected_yield_per_acre * cost_analysis["land_area"]
            net_profit = total_expected_revenue - cost_analysis["total_cost"]

            st.markdown("#### 💰 Break-even Analysis")
            be_cols = st.columns(3)
            be_cols[0].metric("Expected Revenue", f"₹{total_expected_revenue:,.0f}", f"@ {expected_yield_per_acre} qtl/acre")
            be_cols[1].metric("Total Cost", f"₹{cost_analysis['total_cost']:,.0f}", "All inputs")
            be_cols[2].metric(
                "Estimated Profit",
                f"₹{net_profit:,.0f}",
                "📈 Profit" if net_profit > 0 else "⚠️ Loss",
                delta_color="normal" if net_profit > 0 else "inverse",
            )

        st.markdown("---")
        st.markdown("#### 📋 Market Advisory")
        st.markdown(advice)


# ─────────────────────────────────────────────
# TAB 6 — Knowledge Chat (RAG)
# ─────────────────────────────────────────────
def tab_knowledge_chat():
    st.markdown('<div class="section-title">📚 Agricultural Knowledge Chat</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alert-info">💬 Ask any farming question — powered by <strong>Retrieval-Augmented Generation (RAG)</strong> '
        'with a 12-topic agricultural knowledge base and Groq LLM.</div>',
        unsafe_allow_html=True,
    )

    agents = load_agents()
    profile = st.session_state.farmer_profile

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">👨‍🌾 <strong>You:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bot">🌾 <strong>FarmingAI:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    # Quick question chips
    st.markdown("**Quick Questions:**")
    quick_qs = [
        "How much fertilizer should I apply to my crop?",
        "What are the signs of nitrogen deficiency?",
        "When is the best time to irrigate?",
        "How do I control stem borer in rice?",
        "What government schemes are available for farmers?",
        "How to improve soil health organically?",
    ]
    cols = st.columns(3)
    for i, q in enumerate(quick_qs):
        with cols[i % 3]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state["pending_question"] = q

    # Chat input
    user_input = st.chat_input("Ask me anything about farming…")

    # Handle quick question or typed input
    question = st.session_state.pop("pending_question", None) or user_input

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})

        with st.spinner("Retrieving knowledge and generating answer…"):
            answer = agents["knowledge"].answer(question, farmer_profile=profile)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


# ─────────────────────────────────────────────
# TAB 7 — About
# ─────────────────────────────────────────────
def tab_about():
    st.markdown('<div class="section-title">ℹ️ About FarmingAI</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="alert-success"><strong>FarmingAI</strong> is an agentic AI system built to empower farmers '
        'with real-time, personalised, and data-driven agricultural advice — powered by Groq\'s ultra-fast LLM inference.</div>',
        unsafe_allow_html=True,
    )

    # Agent cards grid
    st.markdown('<div class="section-title">🤖 Agent Architecture</div>', unsafe_allow_html=True)
    agents_info = [
        ("🌱", "Crop Advisory", "Seeds · Fertiliser · Harvest", "#2e7d32"),
        ("🌦️", "Weather & Irrigation", "Live weather · Irrigation", "#0288d1"),
        ("🔬", "Pest & Disease", "Vision AI · Text diagnosis", "#e53935"),
        ("📈", "Market Insights", "MSP · Cost · Break-even", "#f57c00"),
        ("📚", "Knowledge RAG", "12-topic KB · Q&A Chat", "#6a1b9a"),
        ("🤖", "Orchestrator", "Coordinates all agents", "#00695c"),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc, color) in enumerate(agents_info):
        with cols[i % 3]:
            st.markdown(
                f'<div class="agent-about-card" style="border-top-color:{color};animation-delay:{i*0.15}s">'
                f'<div class="card-icon">{icon}</div>'
                f'<h4>{name}</h4>'
                f'<p>{desc}</p>'
                f'</div><br>',
                unsafe_allow_html=True,
            )

    # Tech stack pills
    st.markdown('<div class="section-title">🛠️ Tech Stack</div>', unsafe_allow_html=True)
    tech = [
        ("🐍", "Python 3.11+"), ("🎈", "Streamlit"), ("⚡", "Groq API"),
        ("🦙", "Llama 3.3 / 4 / 3.1"), ("🌤️", "OpenWeatherMap"), ("📊", "Plotly"),
        ("🖼️", "Pillow (Vision)"), ("🔍", "RAG (Keyword Search)"),
    ]
    pills_html = "".join(f'<span class="stat-pill">{icon} {label}</span>' for icon, label in tech)
    st.markdown(f'<div style="margin:0.5rem 0 1.2rem">{pills_html}</div>', unsafe_allow_html=True)

    # Setup
    st.markdown('<div class="section-title">🚀 Quick Start</div>', unsafe_allow_html=True)
    st.code(
        "python -m venv myenv\n"
        "myenv\\Scripts\\activate\n"
        "pip install -r requirements.txt\n"
        "# Copy .env.example → .env and add GROQ_API_KEY\n"
        "streamlit run app.py",
        language="bash",
    )

    st.markdown('<div class="section-title">🔑 API Keys</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="alert-warning">'
        '<b>GROQ_API_KEY</b> (required) — <a href="https://console.groq.com">console.groq.com</a><br>'
        '<b>OPENWEATHER_API_KEY</b> (optional) — <a href="https://openweathermap.org/api">openweathermap.org/api</a>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────
def main():
    render_sidebar()
    render_header()

    # API key guard
    if not GROQ_API_KEY:
        st.error(
            "⚠️ **GROQ_API_KEY not configured.** "
            "Copy `.env.example` to `.env` and add your Groq API key, then restart the app."
        )
        st.stop()

    tabs = st.tabs([
        "🤖 Full Advisory",
        "🌱 Crop Advisory",
        "🌦️ Weather & Irrigation",
        "🔬 Pest Detection",
        "📈 Market Insights",
        "📚 Knowledge Chat",
        "ℹ️ About",
    ])

    with tabs[0]: tab_full_advisory()
    with tabs[1]: tab_crop_advisory()
    with tabs[2]: tab_weather()
    with tabs[3]: tab_pest_detection()
    with tabs[4]: tab_market()
    with tabs[5]: tab_knowledge_chat()
    with tabs[6]: tab_about()


if __name__ == "__main__":
    main()
