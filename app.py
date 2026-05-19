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

@st.cache_data
def load_available_cities():
    """Load list of available cities from restaurant data"""
    try:
        df = pd.read_csv("data/processed/travel_data.csv")
        cities = sorted(df[df['type'] == 'restaurant']['city'].unique().tolist())
        return cities if cities else ["Paris", "Berlin", "Barcelona", "Amsterdam", "Rome", "London"]
    except FileNotFoundError:
        return ["Paris", "Berlin", "Barcelona", "Amsterdam", "Rome", "London"]

# Page config
st.set_page_config(
    page_title="Horizons | Travel Planning",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CLEAN LIGHT THEME CSS (Minimalist)
# ============================================================================
st.markdown("""
    <style>
    /* Remove default top padding */
    .block-container {
        padding-top: 0rem;
    }

    /* Typography & Core */
    h1, h2, h3 {
        color: #0f172a;
        letter-spacing: -0.02em;
    }

    /* Custom Variant Cards */
    .variant-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .variant-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    /* Top border accents for tiers */
    .budget-card { border-top: 4px solid #10b981; }  /* Emerald */
    .comfort-card { border-top: 4px solid #3b82f6; } /* Blue */
    .luxury-card { border-top: 4px solid #8b5cf6; }  /* Purple */

    /* Cost Breakdown Section */
    .cost-section {
        background-color: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 8px;
        padding: 1.25rem;
        margin-top: 1rem;
    }
    .cost-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px dashed #cbd5e1;
        color: #475569;
        font-size: 0.95rem;
    }
    .cost-item:last-child {
        border-bottom: none;
        font-weight: 700;
        color: #0f172a;
        font-size: 1.1rem;
        padding-top: 0.75rem;
    }

    /* Summary Box */
    .summary-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0284c7;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }

    /* Dividers */
    hr {
        border-color: #e2e8f0;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")
use_gemini = st.sidebar.checkbox("Use Gemini (instead of Groq)", value=False)

# ============================================================================
# HERO SECTION
# ============================================================================
st.markdown("""
    <div style="text-align: center; padding: 4rem 0 3rem 0; background-color: #ffffff; margin: 0 -4rem 2rem -4rem; border-bottom: 1px solid #e2e8f0;">
        <h1 style="font-size: 3.5rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.03em;">🌍 Horizons</h1>
        <p style="font-size: 1.1rem; color: #64748b; font-weight: 400;">AI-powered travel planning • Real restaurants • Perfect itineraries</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# PLAN YOUR TRIP
# ============================================================================
st.markdown("### ✈️ Plan Your Trip")

available_cities = load_available_cities()

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    origin = st.selectbox("Departure City", options=available_cities, index=0 if "London" not in available_cities else available_cities.index("London"))
    destination = st.selectbox("Destination City", options=available_cities, index=2 if len(available_cities) > 2 else 0)

with col2:
    duration = st.slider("Duration (Days)", min_value=1, max_value=30, value=3, step=1)
    st.markdown(f"<div style='text-align:center; padding-top:1rem; color:#64748b;'>{duration} days / {duration-1} nights</div>", unsafe_allow_html=True)

with col3:
    budget = st.number_input("Total Budget (€)", min_value=100, max_value=50000, value=900, step=100)
    travelers = st.number_input("Travelers", min_value=1, max_value=10, value=2, step=1)
    st.markdown(f"<div style='text-align:right; font-size:0.9rem; color:#64748b;'>Per person: <strong style='color:#0284c7;'>€{budget // travelers}</strong></div>", unsafe_allow_html=True)

available_preferences = ["Museums", "Food", "Beaches", "Nature", "Nightlife", "Historical Sites", "Shopping", "Sports", "Art", "Culture"]
preferences = st.multiselect("Select Your Interests", options=available_preferences, default=["Museums", "Food"])

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([4, 1], gap="medium")
with col_btn1:
    generate_button = st.button("🚀 Generate Itinerary", use_container_width=True, type="primary")
with col_btn2:
    if st.button("↺ Reset", use_container_width=True):
        st.rerun()

st.markdown('<hr/>', unsafe_allow_html=True)

# Helper function to render UI (used for both real and fake data)
def render_itinerary_ui(result):
    # Summary stats
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div style="text-align: center;"><div class="metric-value">{result["request"]["destination"]}</div><div class="metric-label">Destination</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="text-align: center;"><div class="metric-value">{result["request"]["duration_days"]}</div><div class="metric-label">Days</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="text-align: center;"><div class="metric-value">€{result["request"]["budget_eur"]:,.0f}</div><div class="metric-label">Budget</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div style="text-align: center;"><div class="metric-value">{result["request"]["travelers"]}</div><div class="metric-label">Travelers</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### ✨ Recommended Options")
    variants = result.get("variants", [])
    for idx, variant in enumerate(variants):
        variant_name = variant.get("name", f"Variant {idx+1}")

        # Determine card styling
        card_class = "budget-card" if "BUDGET" in variant_name.upper() else ("comfort-card" if "COMFORT" in variant_name.upper() else "luxury-card")
        emoji = "🎒" if "BUDGET" in variant_name.upper() else ("🧳" if "COMFORT" in variant_name.upper() else "🥂")

        with st.container():
            st.markdown(f"""
                <div class="variant-card {card_class}">
                <h3 style="margin-top:0; margin-bottom:0.5rem;">{emoji} {variant_name.upper()}</h3>
                <p style="color:#64748b; font-size:0.95rem; margin-bottom:1.5rem;">{variant.get('notes', '')}</p>
                """, unsafe_allow_html=True)

            # Daily Itinerary
            daily_itinerary = variant.get("daily_itinerary", [])
            if daily_itinerary:
                st.markdown("<strong>📅 Daily Schedule</strong>", unsafe_allow_html=True)
                for day_plan in daily_itinerary:
                    day_num = day_plan.get("day", 1)
                    activities_list = day_plan.get("activities", [])
                    day_cost = day_plan.get("estimated_cost_eur", 0)

                    with st.expander(f"Day {day_num} • Estimated €{day_cost}", expanded=(day_num==1)):
                        if isinstance(activities_list, list):
                            for activity in activities_list:
                                if isinstance(activity, dict):
                                    time = activity.get("time", "")
                                    name = activity.get("name", activity.get("activity", "Activity"))
                                    cost = activity.get("cost", "included")
                                    time_str = f"**{time}** " if time else ""
                                    st.markdown(f"- {time_str}{name} <span style='color:#94a3b8; font-size:0.9em;'>(€{cost})</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"- {activity}", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Cost breakdown
            col1, col2 = st.columns(2, gap="large")
            with col1:
                cost_breakdown = variant.get("cost_breakdown", {})
                st.markdown('<div class="cost-section">', unsafe_allow_html=True)
                st.markdown("<div style='font-weight:700; color:#0f172a; margin-bottom:0.5rem;'>💰 Cost Breakdown</div>", unsafe_allow_html=True)

                metrics_data = [
                    ("🏨 Accommodation", cost_breakdown.get("accommodation_total", 0)),
                    ("🍽️ Meals", cost_breakdown.get("meals_total", 0)),
                    ("🎭 Activities", cost_breakdown.get("activities_total", 0)),
                    ("🚌 Transport", cost_breakdown.get("transport_total", 0)),
                ]
                for label, value in metrics_data:
                    st.markdown(f'<div class="cost-item"><span>{label}</span><span>€{value:,.0f}</span></div>', unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="cost-item">
                        <span>Total (Group)</span>
                        <span style="color:#0284c7;">€{cost_breakdown.get('total_eur', 0):,.0f}</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                accommodation = variant.get("accommodation", {})
                st.markdown('<div class="cost-section">', unsafe_allow_html=True)
                st.markdown("<div style='font-weight:700; color:#0f172a; margin-bottom:0.5rem;'>🛌 Accommodation</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-weight:500; color:#334155; margin-bottom:1rem;'>{accommodation.get('name', 'N/A')}</div>", unsafe_allow_html=True)
                st.markdown(f'<div class="cost-item"><span>Price per night</span><span>€{accommodation.get("price_per_night_eur", 0)}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cost-item" style="border:none;"><span>Duration</span><span>{accommodation.get("nights", 0)} nights</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# Generation logic
if generate_button:
    if not origin or not destination or not preferences:
        st.error("Please select departure city, destination city, and at least one preference.")
    else:
        with st.spinner("Generating your personalized itinerary..."):
            try:
                try:
                    from main import TravelRAG
                    rag = TravelRAG(use_gemini=use_gemini)
                    result = rag.plan_trip(
                        destination=destination,
                        duration_days=duration,
                        budget_eur=budget,
                        preferences=preferences,
                        travelers=travelers
                    )
                    if result and result.get("variants"):
                        st.success("✅ Itinerary generated successfully!")
                        render_itinerary_ui(result)
                except ImportError as e:
                    # Fallback: Show sample itinerary when modules can't be loaded
                    st.error(f"❌ Module could not be loaded: {e}")
                    st.info("💡 All dependencies must be installed for the RAG system to work properly")

                    st.markdown("### 📋 Sample Itinerary")

                    # Sample data for demonstration
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
                                            {"time": "01:00 PM", "name": "Lunch at Local Restaurant", "cost": "12"},
                                            {"time": "03:00 PM", "name": "City Museum Visit", "cost": "12"},
                                            {"time": "06:00 PM", "name": "Walk around City Center", "cost": "free"},
                                            {"time": "08:00 PM", "name": "Dinner", "cost": "10"}
                                        ],
                                        "estimated_cost_eur": 34
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast", "cost": "5"},
                                            {"time": "09:30 AM", "name": "Walking Food Tour", "cost": "15"},
                                            {"time": "12:30 PM", "name": "Lunch - Street Food", "cost": "7"},
                                            {"time": "02:00 PM", "name": "Local Markets Exploration", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Relax at Café", "cost": "5"},
                                            {"time": "08:00 PM", "name": "Dinner", "cost": "10"}
                                        ],
                                        "estimated_cost_eur": 42
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast", "cost": "5"},
                                            {"time": "09:00 AM", "name": "Local Park Visit", "cost": "free"},
                                            {"time": "12:00 PM", "name": "Lunch", "cost": "8"},
                                            {"time": "02:00 PM", "name": "Beach Time", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Sunset View", "cost": "free"},
                                            {"time": "07:00 PM", "name": "Final Dinner & Farewell", "cost": "12"},
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
                                            {"time": "01:30 PM", "name": "Lunch at Nice Restaurant", "cost": "20"},
                                            {"time": "03:30 PM", "name": "Museum & Gallery Tour", "cost": "25"},
                                            {"time": "06:00 PM", "name": "Rest & Refresh", "cost": "free"},
                                            {"time": "08:00 PM", "name": "Dinner at Local Bistro", "cost": "25"}
                                        ],
                                        "estimated_cost_eur": 70
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast at Hotel", "cost": "12"},
                                            {"time": "09:30 AM", "name": "Traditional Cooking Class", "cost": "45"},
                                            {"time": "01:00 PM", "name": "Enjoy Your Cooked Lunch", "cost": "included"},
                                            {"time": "03:00 PM", "name": "Local Market Tour", "cost": "free"},
                                            {"time": "05:00 PM", "name": "Wine Tasting Session", "cost": "15"},
                                            {"time": "08:00 PM", "name": "Dinner at Restaurant", "cost": "28"}
                                        ],
                                        "estimated_cost_eur": 100
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast at Hotel", "cost": "12"},
                                            {"time": "10:00 AM", "name": "Professional Guided City Tour", "cost": "35"},
                                            {"time": "01:00 PM", "name": "Lunch at Recommended Restaurant", "cost": "25"},
                                            {"time": "03:00 PM", "name": "Shopping & Leisure", "cost": "20"},
                                            {"time": "05:30 PM", "name": "Café Break with Dessert", "cost": "10"},
                                            {"time": "08:00 PM", "name": "Farewell Dinner", "cost": "30"},
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
                                            {"time": "06:00 AM", "name": "VIP Lounge Access & Depart", "cost": "included"},
                                            {"time": "10:00 AM", "name": "First-Class Arrival in " + destination, "cost": "included"},
                                            {"time": "10:30 AM", "name": "Limousine Pickup from Airport", "cost": "included"},
                                            {"time": "11:30 AM", "name": "Check-in to 5-Star Luxury Hotel", "cost": "included"},
                                            {"time": "01:00 PM", "name": "Gourmet Lunch at Hotel Restaurant", "cost": "60"},
                                            {"time": "03:00 PM", "name": "Private Museum Tour with Expert Guide", "cost": "120"},
                                            {"time": "06:00 PM", "name": "Spa & Wellness Treatment", "cost": "80"},
                                            {"time": "08:30 PM", "name": "Dinner at 5-Star Restaurant", "cost": "120"}
                                        ],
                                        "estimated_cost_eur": 380
                                    },
                                    {
                                        "day": 2,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Breakfast in Room with Personal Chef", "cost": "50"},
                                            {"time": "10:00 AM", "name": "Personal Shopping Tour with Stylist", "cost": "100"},
                                            {"time": "01:00 PM", "name": "Michelin-Starred Restaurant Lunch", "cost": "150"},
                                            {"time": "03:30 PM", "name": "Exclusive Art Gallery Private Viewing", "cost": "75"},
                                            {"time": "05:30 PM", "name": "Premium Spa Treatment", "cost": "90"},
                                            {"time": "08:00 PM", "name": "Michelin-Starred Dinner Experience", "cost": "180"}
                                        ],
                                        "estimated_cost_eur": 645
                                    },
                                    {
                                        "day": 3,
                                        "activities": [
                                            {"time": "08:00 AM", "name": "Champagne Breakfast", "cost": "50"},
                                            {"time": "10:00 AM", "name": "Private Helicopter City Tour", "cost": "200"},
                                            {"time": "12:30 PM", "name": "VIP Lunch with City Views", "cost": "100"},
                                            {"time": "02:00 PM", "name": "Personal Concierge Shopping Time", "cost": "80"},
                                            {"time": "04:00 PM", "name": "Final Spa Treatment", "cost": "80"},
                                            {"time": "07:00 PM", "name": "Private Farewell Dinner", "cost": "200"},
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
                    render_itinerary_ui(test_result)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown('<hr/>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 1rem 0; color: #94a3b8; font-size: 0.9rem;">
    <div><strong>Horizons</strong> • AI-Powered Travel Planning</div>
</div>
""", unsafe_allow_html=True)
