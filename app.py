"""
Horizons - AI-Powered Travel Planning
Beautiful, intelligent travel itinerary generation using RAG and Groq LLaMA 3.3
"""

import streamlit as st
import json
from datetime import datetime
import sys
import os
import pandas as pd

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load available cities from the data
@st.cache_data
def load_available_cities():
    """Load list of available cities from restaurant data"""
    try:
        df = pd.read_csv("data/processed/travel_data.csv")
        # Get unique cities from the data
        cities = sorted(df[df['type'] == 'restaurant']['city'].unique().tolist())
        return cities if cities else ["Paris", "Berlin", "Barcelona", "Amsterdam", "Rome", "London"]
    except FileNotFoundError:
        # Fallback to default cities if data not found
        return ["Paris", "Berlin", "Barcelona", "Amsterdam", "Rome", "London"]

# Page config
st.set_page_config(
    page_title="Horizons | Travel Planning",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# PREMIUM HORIZONS THEME - Ultra-modern dark with vibrant accents
# ============================================================================
st.markdown("""
    <style>
    /* Enhanced color palette */
    :root {
        --bg-primary: #050B15;
        --bg-secondary: #0D1420;
        --bg-tertiary: #141D2B;
        --bg-card: #1A2332;
        --border-subtle: #2A3F5F;
        --border-accent: #4A5F7F;
        --purple-bright: #C084FC;
        --purple-main: #9333EA;
        --purple-dark: #6D28D9;
        --cyan-accent: #06B6D4;
        --emerald-accent: #10B981;
        --rose-accent: #F472B6;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
    }

    * {
        color-scheme: dark;
    }

    /* Main container with premium gradient */
    .main {
        padding: 0;
        background: linear-gradient(135deg, #050B15 0%, #0D1420 50%, #0A0F1B 100%);
        min-height: 100vh;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050B15 0%, #0D1420 50%, #0A0F1B 100%);
    }

    /* Sidebar enhancement */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1420 0%, #141D2B 100%);
        border-right: 1px solid rgba(74, 95, 127, 0.3);
    }

    /* Typography - premium styling */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC;
        font-weight: 700;
        letter-spacing: -0.8px;
    }

    p, span, label, div {
        color: #CBD5E1;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    /* Hero section - premium look */
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #C084FC 0%, #9333EA 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        letter-spacing: -1.5px;
        text-transform: none;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        color: #94A3B8;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 0.3px;
    }

    /* Input sections - premium cards */
    .input-section {
        background: linear-gradient(135deg, rgba(20, 29, 43, 0.8) 0%, rgba(26, 35, 50, 0.5) 100%);
        border: 1px solid rgba(74, 95, 127, 0.4);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .input-section:hover {
        border-color: #9333EA;
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.05) 0%, rgba(6, 182, 212, 0.03) 100%);
        box-shadow: 0 0 30px rgba(147, 51, 234, 0.2), 0 8px 32px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }

    .input-section h3 {
        color: #C084FC;
        margin-top: 0;
        font-size: 1.15rem;
        margin-bottom: 1.25rem;
        font-weight: 700;
        letter-spacing: 0.2px;
    }

    /* Premium form inputs - Streamlit specific */
    input[type="text"],
    input[type="number"],
    input[type="email"],
    select,
    textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] input {
        background: linear-gradient(135deg, #0A0F1B 0%, #141D2B 100%) !important;
        border: 1.5px solid rgba(147, 51, 234, 0.4) !important;
        color: #F8FAFC !important;
        border-radius: 12px !important;
        padding: 0.95rem 1.1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4), 0 0 20px rgba(147, 51, 234, 0.1) !important;
    }

    input:hover[type="text"],
    input:hover[type="number"],
    select:hover,
    textarea:hover,
    [data-testid="stNumberInput"] input:hover,
    [data-testid="stSelectbox"] input:hover {
        border-color: rgba(147, 51, 234, 0.8) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4), 0 0 30px rgba(147, 51, 234, 0.25) !important;
    }

    input:focus[type="text"],
    input:focus[type="number"],
    select:focus,
    textarea:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] input:focus {
        border-color: #9333EA !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4), 0 0 0 4px rgba(147, 51, 234, 0.2) !important;
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%) !important;
    }

    /* Selectbox dropdown styling */
    [data-testid="stSelectbox"] > div > div {
        background: linear-gradient(135deg, #0A0F1B 0%, #141D2B 100%) !important;
        border: 1.5px solid rgba(147, 51, 234, 0.4) !important;
    }

    /* Number input styling */
    [data-testid="stNumberInput"] {
        width: 100%;
    }

    [data-testid="stNumberInput"] > div > input {
        background: linear-gradient(135deg, #0A0F1B 0%, #141D2B 100%) !important;
        border: 1.5px solid rgba(147, 51, 234, 0.4) !important;
        color: #F8FAFC !important;
    }

    /* Selectbox and Multiselect styling */
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"] {
        width: 100%;
    }

    /* Dropdown menu styling */
    [data-testid="stSelectbox"] ul,
    [data-testid="stMultiSelect"] ul {
        background: linear-gradient(135deg, #141D2B 0%, #0D1420 100%) !important;
        border: 1.5px solid rgba(147, 51, 234, 0.4) !important;
    }

    [data-testid="stSelectbox"] li,
    [data-testid="stMultiSelect"] li {
        color: #F8FAFC !important;
        background: transparent !important;
    }

    [data-testid="stSelectbox"] li:hover,
    [data-testid="stMultiSelect"] li:hover {
        background: rgba(147, 51, 234, 0.2) !important;
        color: #C084FC !important;
    }

    /* Premium buttons with enhanced effects */
    .stButton > button {
        background: linear-gradient(135deg, #9333EA 0%, #C084FC 100%);
        color: #F8FAFC !important;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(147, 51, 234, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        letter-spacing: 0.3px;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(147, 51, 234, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* Reset button variant */
    .stButton > button:nth-of-type(2) {
        background: linear-gradient(135deg, #6D28D9 0%, #9333EA 100%);
    }

    /* Variant cards - premium styling */
    .variant-card {
        background: linear-gradient(135deg, rgba(20, 29, 43, 0.9) 0%, rgba(26, 35, 50, 0.6) 100%);
        border: 1.5px solid #2A3F5F;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .variant-card:hover {
        border-color: #9333EA;
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%);
        box-shadow: 0 0 40px rgba(147, 51, 234, 0.25), 0 8px 32px rgba(0, 0, 0, 0.3);
        transform: translateY(-4px);
    }

    .budget-card {
        border-left: 5px solid #F59E0B;
    }

    .comfort-card {
        border-left: 5px solid #10B981;
    }

    .luxury-card {
        border-left: 5px solid #F472B6;
    }

    /* Cost section - premium styling */
    .cost-section {
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
        border: 1.5px solid rgba(147, 51, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }

    .cost-item {
        display: flex;
        justify-content: space-between;
        padding: 0.9rem 0;
        border-bottom: 1px solid rgba(147, 51, 234, 0.15);
        color: #CBD5E1;
        font-weight: 500;
    }

    .cost-item:last-child {
        border-bottom: none;
        padding-top: 0.7rem;
        font-weight: 700;
        color: #C084FC;
        font-size: 1.05rem;
    }

    /* Premium metric display */
    .metric-value {
        color: #C084FC;
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* Dividers - subtle premium look */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, rgba(74, 95, 127, 0), rgba(147, 51, 234, 0.3), rgba(74, 95, 127, 0));
        margin: 2.5rem 0;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(20, 29, 43, 0.7) 0%, rgba(26, 35, 50, 0.4) 100%);
        border: 1px solid #2A3F5F;
        border-radius: 12px;
    }

    /* Alert boxes */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
        border: 1.5px solid rgba(147, 51, 234, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
        border: 1.5px solid rgba(16, 185, 129, 0.4) !important;
    }

    .stError {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.1) 0%, rgba(244, 63, 94, 0.05) 100%);
        border: 1.5px solid rgba(244, 63, 94, 0.4) !important;
    }

    /* Spinners */
    .stSpinner {
        color: #C084FC;
    }

    /* Premium footer */
    .footer-section {
        background: linear-gradient(135deg, rgba(20, 29, 43, 0.8) 0%, rgba(26, 35, 50, 0.5) 100%);
        border-top: 1.5px solid rgba(147, 51, 234, 0.3);
        border-radius: 16px;
        padding: 2.5rem;
        margin-top: 4rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .footer-section h2 {
        background: linear-gradient(135deg, #C084FC 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .footer-section p {
        color: #94A3B8;
        line-height: 1.9;
    }

    /* Summary box - premium styling */
    .summary-box {
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
        border: 1.5px solid rgba(147, 51, 234, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(147, 51, 234, 0.1);
    }

    /* Smooth transitions */
    * {
        transition: color 0.2s ease, border-color 0.2s ease;
    }

    /* Premium number input styling */
    [data-testid="stNumberInput"] input {
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
    }

    /* Slider styling */
    [data-testid="stSlider"] {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    [data-testid="stSlider"] > div > div {
        padding: 1rem 0 !important;
    }

    /* Premium multiselect styling */
    [data-testid="stMultiSelect"] {
        width: 100%;
    }

    /* Hover glow effect for form sections */
    .input-section {
        position: relative;
    }

    .input-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(ellipse at center, rgba(147, 51, 234, 0) 0%, rgba(147, 51, 234, 0.05) 100%);
        border-radius: 16px;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }

    .input-section:hover::before {
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")
use_gemini = st.sidebar.checkbox("Use Gemini (instead of Groq)", value=False)
show_advanced = st.sidebar.checkbox("Show advanced settings", value=False)

# ============================================================================
# HERO SECTION - Premium Landing
# ============================================================================
st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.15) 0%, rgba(6, 182, 212, 0.08) 100%);
        border-bottom: 2px solid rgba(147, 51, 234, 0.3);
        padding: 4rem 2rem;
        margin: -3rem -2rem 2rem -2rem;
        text-align: center;
    ">
        <div style="font-size: 4.5rem; font-weight: 900; background: linear-gradient(135deg, #C084FC, #06B6D4);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    background-clip: text; margin-bottom: 0.5rem; letter-spacing: -2px;">
            🌍 Horizons
        </div>
        <div style="font-size: 1.35rem; color: #94A3B8; font-weight: 300; letter-spacing: 0.5px; margin-bottom: 0;">
            AI-powered travel planning • Real restaurants • Perfect itineraries
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# PLAN YOUR TRIP - Premium Form Section
# ============================================================================
st.markdown("## ✈️ Plan Your Dream Trip")

# Load available cities
available_cities = load_available_cities()

# Create three columns for input
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(20, 29, 43, 0.9) 0%, rgba(26, 35, 50, 0.6) 100%);
            border: 2px solid rgba(147, 51, 234, 0.3);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        ">
            <div style="color: #C084FC; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: 0.5px;">
                📍 Travel Information
            </div>
            <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.5rem; font-weight: 400;">
                Select your departure and destination cities
            </div>
        </div>
    """, unsafe_allow_html=True)
    origin = st.selectbox(
        "Departure City",
        options=available_cities,
        index=0 if "London" not in available_cities else available_cities.index("London"),
        label_visibility="collapsed",
        key="origin_select",
        help="Choose your departure city from the list"
    )
    destination = st.selectbox(
        "Destination City",
        options=available_cities,
        index=2 if len(available_cities) > 2 else 0,
        label_visibility="collapsed",
        key="dest_select",
        help="Choose your destination city from the list"
    )

with col2:
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(20, 29, 43, 0.9) 0%, rgba(26, 35, 50, 0.6) 100%);
            border: 2px solid rgba(147, 51, 234, 0.3);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        ">
            <div style="color: #C084FC; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: 0.5px;">
                📅 Trip Duration
            </div>
            <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.5rem; font-weight: 400;">
                Set how many days you'll stay
            </div>
        </div>
    """, unsafe_allow_html=True)
    duration = st.slider(
        "How many days?",
        min_value=1,
        max_value=30,
        value=3,
        step=1,
        label_visibility="collapsed",
        key="duration_slider",
        help="Choose the duration of your trip"
    )
    st.markdown(f"""
        <div style="text-align: center; color: #C084FC; font-size: 1.5rem; font-weight: 800; margin-top: 1.5rem; letter-spacing: -0.5px;">
            {duration} days
        </div>
        <div style="text-align: center; color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem;">
            {duration * 1} nights
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(20, 29, 43, 0.9) 0%, rgba(26, 35, 50, 0.6) 100%);
            border: 2px solid rgba(147, 51, 234, 0.3);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        ">
            <div style="color: #C084FC; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: 0.5px;">
                💰 Budget & Travelers
            </div>
            <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.5rem; font-weight: 400;">
                Set your budget and group size
            </div>
        </div>
    """, unsafe_allow_html=True)
    budget = st.number_input(
        "Total Budget (€)",
        min_value=100,
        max_value=50000,
        value=900,
        step=100,
        label_visibility="collapsed",
        key="budget_input",
        help="Your total travel budget in euros"
    )
    travelers = st.number_input(
        "Number of travelers?",
        min_value=1,
        max_value=10,
        value=2,
        step=1,
        label_visibility="collapsed",
        key="travelers_input",
        help="How many people are traveling"
    )
    st.markdown(f"""
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(147, 51, 234, 0.2); color: #CBD5E1; font-size: 0.9rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Budget per person:</span>
                <span style="color: #C084FC; font-weight: 700;">€{budget // travelers}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Per day/person:</span>
                <span style="color: #C084FC; font-weight: 700;">€{(budget // travelers) // 3}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Preferences
st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(20, 29, 43, 0.9) 0%, rgba(26, 35, 50, 0.6) 100%);
        border: 2px solid rgba(147, 51, 234, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    ">
        <div style="color: #C084FC; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: 0.5px;">
            🎯 Your Interests
        </div>
        <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.5rem; font-weight: 400;">
            Select activities and experiences you're interested in
        </div>
    </div>
""", unsafe_allow_html=True)

available_preferences = [
    "Museums",
    "Food",
    "Beaches",
    "Nature",
    "Nightlife",
    "Historical Sites",
    "Shopping",
    "Sports",
    "Art",
    "Culture"
]
preferences = st.multiselect(
    "Select Your Interests",
    options=available_preferences,
    default=["Museums", "Food"],
    help="Select at least one preference to personalize your itinerary",
    label_visibility="collapsed",
    key="preferences_select"
)

# Generate button with spacing
st.markdown("<div style='margin-top: 2rem; margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([2, 1], gap="large")

with col_btn1:
    generate_button = st.button(
        "🚀 Generate Itinerary",
        use_container_width=True,
        type="primary",
        help="Click to generate your personalized travel itinerary"
    )

with col_btn2:
    if st.button("↺ Reset", use_container_width=True, help="Clear all inputs and start over"):
        st.rerun()

st.markdown('<hr/>', unsafe_allow_html=True)

# Generation logic
if generate_button:
    if not origin or not destination or not preferences:
        st.error("❌ Please select departure city, destination city, and at least one preference!")
    else:
        with st.spinner("🔄 Generating itinerary..."):
            try:
                # Try to import and use the TravelRAG system
                try:
                    from main import TravelRAG

                    # Initialize RAG system
                    rag = TravelRAG(use_gemini=use_gemini)

                    # Generate itinerary
                    st.info(f"📡 Creating travel plan from {origin} to {destination}...")

                    result = rag.plan_trip(
                        destination=destination,
                        duration_days=duration,
                        budget_eur=budget,
                        preferences=preferences,
                        travelers=travelers
                    )

                    # Display results
                    if result and result.get("variants"):
                        st.success("✅ Itinerary generated successfully!")

                        # Summary stats
                        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                        st.markdown("### 📊 Trip Summary")
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.markdown(f'<div style="text-align: center;"><div class="metric-value">{destination}</div><div style="color: #CBD5E1; font-size: 0.9rem;">Destination</div></div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<div style="text-align: center;"><div class="metric-value">{duration}</div><div style="color: #CBD5E1; font-size: 0.9rem;">Days</div></div>', unsafe_allow_html=True)
                        with col3:
                            st.markdown(f'<div style="text-align: center;"><div class="metric-value">€{budget:,.0f}</div><div style="color: #CBD5E1; font-size: 0.9rem;">Budget</div></div>', unsafe_allow_html=True)
                        with col4:
                            st.markdown(f'<div style="text-align: center;"><div class="metric-value">{travelers}</div><div style="color: #CBD5E1; font-size: 0.9rem;">Travelers</div></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<hr/>', unsafe_allow_html=True)

                        # Display variants
                        st.markdown("### ✨ Your Itinerary Options")

                        variants = result.get("variants", [])

                        for idx, variant in enumerate(variants):
                            variant_name = variant.get("name", f"Variant {idx+1}")
                            variant_emoji = "🛫" if "BUDGET" in variant_name.upper() else ("✨" if "COMFORT" in variant_name.upper() else "👑")
                            variant_class = "budget-card" if "BUDGET" in variant_name.upper() else (
                                "comfort-card" if "COMFORT" in variant_name.upper() else "luxury-card"
                            )

                            with st.container():
                                st.markdown(f"""
                                    <div class="variant-card {variant_class}">
                                    <h3>{variant_emoji} {variant_name}</h3>
                                    """, unsafe_allow_html=True)

                                # Trip Overview
                                st.markdown(f"""
                                    <div style="background: rgba(124, 58, 237, 0.08); border: 1px solid rgba(124, 58, 237, 0.2); padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                                    <strong style="color: #A78BFA;">📍 Trip Overview</strong><br>
                                    <span style="color: #CBD5E1;">From: <strong style="color: #F1F5F9;">{origin}</strong> → To: <strong style="color: #F1F5F9;">{destination}</strong></span><br>
                                    <span style="color: #CBD5E1;">Duration: <strong style="color: #F1F5F9;">{duration} days</strong> | Budget: <strong style="color: #F1F5F9;">€{budget:,.0f}</strong></span>
                                    </div>
                                """, unsafe_allow_html=True)

                                # Daily Itinerary
                                st.write("**📅 Day-by-Day Itinerary:**")
                                daily_itinerary = variant.get("daily_itinerary", [])

                                if daily_itinerary:
                                    for day_plan in daily_itinerary:
                                        day_num = day_plan.get("day", 1)
                                        activities_list = day_plan.get("activities", [])
                                        day_cost = day_plan.get("estimated_cost_eur", 0)

                                        with st.expander(f"📆 Day {day_num} - Estimated €{day_cost}", expanded=(day_num==1)):
                                            if isinstance(activities_list, list):
                                                for activity in activities_list:
                                                    if isinstance(activity, dict):
                                                        time = activity.get("time", "TBA")
                                                        name = activity.get("name", activity.get("activity", "Activity"))
                                                        cost = activity.get("cost", "included")
                                                        st.write(f"🕐 **{time}** - {name} (€{cost})")
                                                    else:
                                                        st.write(f"• {activity}")
                                else:
                                    st.info("Daily schedule will be generated based on your preferences")

                                st.divider()

                                # Cost breakdown
                                col1, col2 = st.columns(2, gap="large")

                                with col1:
                                    cost_breakdown = variant.get("cost_breakdown", {})
                                    st.markdown('<div class="cost-section">', unsafe_allow_html=True)
                                    st.markdown("**💰 Cost Breakdown**")

                                    metrics_data = [
                                        ("🏨 Accommodation", cost_breakdown.get("accommodation_total", 0)),
                                        ("🍽️ Meals", cost_breakdown.get("meals_total", 0)),
                                        ("🎭 Activities", cost_breakdown.get("activities_total", 0)),
                                        ("🚌 Transport", cost_breakdown.get("transport_total", 0)),
                                    ]

                                    for label, value in metrics_data:
                                        st.markdown(f'<div class="cost-item"><span>{label}</span><span>€{value:,.0f}</span></div>', unsafe_allow_html=True)

                                    st.markdown(f"""
                                        <div class="cost-item" style="font-weight: 700; color: #A78BFA; border-bottom: none; padding-top: 0.5rem;">
                                        <span>Total</span><span>€{cost_breakdown.get('total_eur', 0):,.0f}</span>
                                        </div>
                                        <div class="cost-item" style="color: #CBD5E1; font-size: 0.9rem; border-bottom: none;">
                                        <span>Per Person</span><span>€{cost_breakdown.get('per_person_eur', 0):,.0f}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)

                                with col2:
                                    # Accommodation info
                                    accommodation = variant.get("accommodation", {})
                                    st.markdown('<div class="cost-section">', unsafe_allow_html=True)
                                    st.markdown("**🏨 Accommodation**")
                                    st.write(f"{accommodation.get('name', 'N/A')}")
                                    st.markdown(f'<div class="cost-item"><span>Price/Night</span><span style="color: #A78BFA;">€{accommodation.get("price_per_night_eur", 0)}</span></div>', unsafe_allow_html=True)
                                    st.markdown(f'<div class="cost-item"><span>Duration</span><span style="color: #A78BFA;">{accommodation.get("nights", 0)} nights</span></div>', unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)

                                # Activities section
                                st.write("**Recommended Activities:**")
                                activities = variant.get("activities", [])
                                if activities:
                                    for activity in activities[:5]:
                                        if isinstance(activity, dict):
                                            name = activity.get("name", "Activity")
                                            cost = activity.get("cost_eur", 0)
                                            day = activity.get("day", "TBA")
                                            st.write(f"  • {name} (€{cost} - Day {day})")
                                        else:
                                            st.write(f"  • {activity}")
                                else:
                                    highlights = variant.get("highlights", [])
                                    for h in highlights[:3]:
                                        st.write(f"  • {h}")

                                # Transport section
                                st.write("**Transport:**")
                                transport = variant.get("transport", {})
                                if isinstance(transport, dict):
                                    st.write(f"  • {transport.get('description', 'Local transport')}")
                                    st.write(f"    Cost: €{transport.get('cost_eur', 0)}")
                                else:
                                    st.write(f"  • {transport}")

                                # Notes
                                notes = variant.get("notes", "")
                                if notes:
                                    st.write(f"**📝 Note:** {notes}")

                                st.markdown("</div>", unsafe_allow_html=True)
                                st.divider()

                        # Export options
                        st.markdown('<hr/>', unsafe_allow_html=True)
                        st.markdown("### 💾 Export Your Itinerary")
                        col1, col2, col3 = st.columns(3, gap="medium")

                        with col1:
                            st.download_button(
                                label="📥 Download JSON",
                                data=json.dumps(result, indent=2, ensure_ascii=False),
                                file_name=f"itinerary_{destination.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )

                        with col2:
                            if st.button("📧 Send Email", use_container_width=True):
                                st.info("✨ SMTP configuration required to send email")

                        with col3:
                            if st.button("🖨️ Download PDF", use_container_width=True):
                                st.info("✨ WeasyPrint library required to generate PDF")
                    else:
                        st.error("❌ Unable to generate itinerary. Please check your parameters.")

                except ImportError as e:
                    st.error(f"❌ Module could not be loaded: {e}")
                    st.info("💡 All dependencies must be installed for the RAG system to work properly")

                    # Show test data
                    st.markdown("### 📋 Sample Itinerary")
                    test_result = {
                        "request": {
                            "origin": origin,
                            "destination": destination,
                            "duration_days": duration,
                            "budget_eur": budget,
                            "travelers": travelers,
                            "preferences": preferences
                        },
                        "variants": [
                            {
                                "name": "Budget",
                                "cost_breakdown": {
                                    "accommodation_total": budget * 0.45 / travelers,
                                    "meals_total": budget * 0.35 / travelers,
                                    "activities_total": budget * 0.15 / travelers,
                                    "transport_total": budget * 0.05 / travelers,
                                    "total_eur": budget,
                                    "per_person_eur": budget / travelers
                                },
                                "accommodation": {
                                    "name": "Budget Hotel",
                                    "price_per_night_eur": 40,
                                    "nights": duration - 1
                                },
                                "activities": [
                                    {"name": "City Museum Visit", "cost_eur": 12, "day": 1},
                                    {"name": "Walking Food Tour", "cost_eur": 15, "day": 2},
                                    {"name": "Local Park & Beach", "cost_eur": 0, "day": 3}
                                ],
                                "daily_itinerary": [
                                    {
                                        "day": 1,
                                        "activities": [
                                            {"time": "06:00 AM", "name": "Depart from " + origin, "cost": "Flight"},
                                            {"time": "10:30 AM", "name": "Arrive in " + destination, "cost": "included"},
                                            {"time": "12:00 PM", "name": "Check-in to Hotel", "cost": "included"},
                                            {"time": "01:00 PM", "name": "Lunch at Local Restaurant", "cost": "€12"},
                                            {"time": "03:00 PM", "name": "City Museum Visit", "cost": "€12"},
                                            {"time": "06:00 PM", "name": "Walk around City Center", "cost": "free"},
                                            {"time": "08:00 PM", "name": "Dinner", "cost": "€10"}
                                        ],
                                        "estimated_cost_eur": 34
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast", "cost": "€5"},
                                            {"time": "09:30 AM", "name": "Walking Food Tour", "cost": "€15"},
                                            {"time": "12:30 PM", "name": "Lunch - Street Food", "cost": "€7"},
                                            {"time": "02:00 PM", "name": "Local Markets Exploration", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Relax at Café", "cost": "€5"},
                                            {"time": "08:00 PM", "name": "Dinner", "cost": "€10"}
                                        ],
                                        "estimated_cost_eur": 42
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast", "cost": "€5"},
                                            {"time": "09:00 AM", "name": "Local Park Visit", "cost": "free"},
                                            {"time": "12:00 PM", "name": "Lunch", "cost": "€8"},
                                            {"time": "02:00 PM", "name": "Beach Time", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Sunset View", "cost": "free"},
                                            {"time": "07:00 PM", "name": "Final Dinner & Farewell", "cost": "€12"},
                                            {"time": "10:00 PM", "name": "Depart to " + origin, "cost": "Flight"}
                                        ],
                                        "estimated_cost_eur": 25
                                    }
                                ],
                                "transport": {
                                    "description": "Public Transport Pass (3-day)",
                                    "cost_eur": 25
                                },
                                "highlights": ["Museums", "Street Food", "Walking Tour"],
                                "notes": "Budget-friendly options"
                            },
                            {
                                "name": "Comfort",
                                "cost_breakdown": {
                                    "accommodation_total": budget * 0.35 / travelers,
                                    "meals_total": budget * 0.30 / travelers,
                                    "activities_total": budget * 0.30 / travelers,
                                    "transport_total": budget * 0.05 / travelers,
                                    "total_eur": budget,
                                    "per_person_eur": budget / travelers
                                },
                                "accommodation": {
                                    "name": "3-Star Hotel",
                                    "price_per_night_eur": 80,
                                    "nights": duration - 1
                                },
                                "activities": [
                                    {"name": "Museum & Gallery Tour", "cost_eur": 25, "day": 1},
                                    {"name": "Cooking Class", "cost_eur": 45, "day": 2},
                                    {"name": "Guided City Tour", "cost_eur": 35, "day": 3}
                                ],
                                "daily_itinerary": [
                                    {
                                        "day": 1,
                                        "activities": [
                                            {"time": "06:00 AM", "name": "Depart from " + origin, "cost": "Flight"},
                                            {"time": "10:30 AM", "name": "Arrive in " + destination, "cost": "included"},
                                            {"time": "12:00 PM", "name": "Check-in to 3-Star Hotel", "cost": "included"},
                                            {"time": "01:30 PM", "name": "Lunch at Nice Restaurant", "cost": "€20"},
                                            {"time": "03:30 PM", "name": "Museum & Gallery Tour", "cost": "€25"},
                                            {"time": "06:00 PM", "name": "Rest & Refresh", "cost": "free"},
                                            {"time": "08:00 PM", "name": "Dinner at Local Bistro", "cost": "€25"}
                                        ],
                                        "estimated_cost_eur": 70
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast at Hotel", "cost": "€12"},
                                            {"time": "09:30 AM", "name": "Traditional Cooking Class", "cost": "€45"},
                                            {"time": "01:00 PM", "name": "Enjoy Your Cooked Lunch", "cost": "included"},
                                            {"time": "03:00 PM", "name": "Local Market Tour", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Wine Tasting Session", "cost": "€15"},
                                            {"time": "08:00 PM", "name": "Dinner at Restaurant", "cost": "€28"}
                                        ],
                                        "estimated_cost_eur": 100
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast at Hotel", "cost": "€12"},
                                            {"time": "10:00 AM", "name": "Professional Guided City Tour", "cost": "€35"},
                                            {"time": "01:00 PM", "name": "Lunch at Recommended Restaurant", "cost": "€25"},
                                            {"time": "03:00 PM", "name": "Shopping & Leisure", "cost": "€20"},
                                            {"time": "05:30 PM", "name": "Café Break with Dessert", "cost": "€10"},
                                            {"time": "08:00 PM", "name": "Farewell Dinner", "cost": "€30"},
                                            {"time": "10:00 PM", "name": "Depart to " + origin, "cost": "Flight"}
                                        ],
                                        "estimated_cost_eur": 132
                                    }
                                ],
                                "transport": {
                                    "description": "Public Transport + Occasional Taxis",
                                    "cost_eur": 40
                                },
                                "highlights": ["Museums", "Restaurant", "Guided Tour"],
                                "notes": "Balanced experience"
                            },
                            {
                                "name": "Luxury",
                                "cost_breakdown": {
                                    "accommodation_total": budget * 0.40 / travelers,
                                    "meals_total": budget * 0.35 / travelers,
                                    "activities_total": budget * 0.20 / travelers,
                                    "transport_total": budget * 0.05 / travelers,
                                    "total_eur": budget,
                                    "per_person_eur": budget / travelers
                                },
                                "accommodation": {
                                    "name": "5-Star Luxury Hotel",
                                    "price_per_night_eur": 200,
                                    "nights": duration - 1
                                },
                                "activities": [
                                    {"name": "Private Museum Tour with Expert", "cost_eur": 120, "day": 1},
                                    {"name": "Michelin-Starred Restaurant Experience", "cost_eur": 150, "day": 2},
                                    {"name": "Private City Tour & Helicopter View", "cost_eur": 200, "day": 3}
                                ],
                                "daily_itinerary": [
                                    {
                                        "day": 1,
                                        "activities": [
                                            {"time": "06:00 AM", "name": "VIP Lounge Access & Depart from " + origin, "cost": "included"},
                                            {"time": "10:00 AM", "name": "First-Class Arrival in " + destination, "cost": "included"},
                                            {"time": "10:30 AM", "name": "Limousine Pickup from Airport", "cost": "included"},
                                            {"time": "11:30 AM", "name": "Check-in to 5-Star Luxury Hotel", "cost": "included"},
                                            {"time": "01:00 PM", "name": "Gourmet Lunch at Hotel Restaurant", "cost": "€60"},
                                            {"time": "03:00 PM", "name": "Private Museum Tour with Expert Guide", "cost": "€120"},
                                            {"time": "06:00 PM", "name": "Spa & Wellness Treatment", "cost": "€80"},
                                            {"time": "08:30 PM", "name": "Dinner at 5-Star Restaurant", "cost": "€120"}
                                        ],
                                        "estimated_cost_eur": 380
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast in Room with Personal Chef", "cost": "€50"},
                                            {"time": "10:00 AM", "name": "Personal Shopping Tour with Stylist", "cost": "€100"},
                                            {"time": "01:00 PM", "name": "Michelin-Starred Restaurant Lunch", "cost": "€150"},
                                            {"time": "03:30 PM", "name": "Exclusive Art Gallery Private Viewing", "cost": "€75"},
                                            {"time": "05:30 PM", "name": "Premium Spa Treatment", "cost": "€90"},
                                            {"time": "08:00 PM", "name": "Michelin-Starred Dinner Experience", "cost": "€180"}
                                        ],
                                        "estimated_cost_eur": 645
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Champagne Breakfast", "cost": "€50"},
                                            {"time": "10:00 AM", "name": "Private Helicopter City Tour", "cost": "€200"},
                                            {"time": "12:30 PM", "name": "VIP Lunch with City Views", "cost": "€100"},
                                            {"time": "02:00 PM", "name": "Personal Concierge Shopping Time", "cost": "€80"},
                                            {"time": "04:00 PM", "name": "Final Spa Treatment", "cost": "€80"},
                                            {"time": "07:00 PM", "name": "Private Farewell Dinner", "cost": "€200"},
                                            {"time": "10:00 PM", "name": "Limousine to VIP Airport Lounge & Depart", "cost": "included"}
                                        ],
                                        "estimated_cost_eur": 710
                                    }
                                ],
                                "transport": {
                                    "description": "Private Car Service & VIP Airport Transfer",
                                    "cost_eur": 150
                                },
                                "highlights": ["Private Tour", "Michelin Restaurant", "VIP Experience"],
                                "notes": "Premium options"
                            }
                        ]
                    }

                    # Display test variants
                    for variant in test_result.get("variants", []):
                        st.write(f"**{variant['name'].upper()} VARIANT**")
                        cb = variant.get("cost_breakdown", {})
                        st.write(f"Total: €{cb.get('total_eur', 0):,.0f} | Per Person: €{cb.get('per_person_eur', 0):,.0f}")
                        st.divider()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Please ensure all dependencies are installed")

# Footer
st.markdown('<hr/>', unsafe_allow_html=True)
st.markdown("""
<div class="footer-section">
<h2>🌍 Horizons</h2>
<p><strong>AI-Powered Travel Planning</strong></p>
<div style="border-top: 1px solid #334155; margin: 1rem 0; padding-top: 1rem;">
<p style="margin: 0.5rem 0;">🤖 <strong>Engine:</strong> Groq LLaMA 3.3 70B</p>
<p style="margin: 0.5rem 0;">🏨 <strong>Database:</strong> 30 real restaurants across 6 cities</p>
<p style="margin: 0.5rem 0;">📊 <strong>Cost Breakdown:</strong> Accommodation + Meals + Activities + Transport</p>
<p style="margin: 0.5rem 0;">💰 <strong>Options:</strong> Budget, Comfort & Luxury tiers</p>
<p style="margin: 0.5rem 0;">✅ <strong>Smart:</strong> Constraint validation & budget-aware planning</p>
</div>
</div>
""", unsafe_allow_html=True)
