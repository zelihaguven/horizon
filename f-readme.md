# 🌍 Horizons - AI-Powered Travel Planning

Premium travel itinerary generator using RAG and Groq LLaMA 3.3

## Features
- 🤖 AI-powered itinerary generation
- 🏨 Real restaurant database (30 locations, 6 cities)
- 💰 Budget breakdown (Accommodation, Meals, Activities, Transport)
- 🎯 3 budget tiers (Budget, Comfort, Luxury)
- 🎨 Premium dark theme interface

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your API keys to .env

# Run the app
streamlit run app.py
```

## Architecture

The system uses a 4-part RAG pipeline:
1. **Retrieval**: SimpleRetriever (CSV-based) pulls relevant restaurants
2. **Generation**: Groq LLaMA 3.3 70B generates recommendations
3. **Validation**: Budget constraints & preference validation
4. **Formatting**: Structured itinerary with costs & schedules

See ARCHITECTURE.md for detailed design.

## Cities Supported
- London
- Paris
- Berlin
- Barcelona
- Amsterdam
- Rome

## Requirements
- Python 3.8+
- Groq API key
- 4GB RAM minimum