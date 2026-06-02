# Horizons - AI-Powered European Travel Planning

Generate personalized, AI-powered travel itineraries for European cities with intelligent recommendations, real-time validation, and hallucination detection.

---

## 🌍 Supported Destinations

- **London** 🇬🇧 | **Paris** 🇫🇷 | **Berlin** 🇩🇪
- **Barcelona** 🇪🇸 | **Amsterdam** 🇳🇱 | **Rome** 🇮🇹

---

## ✨ Key Features

### 🎯 Intelligent Itinerary Generation
- **RAG + Semantic Search**: ChromaDB vector store with 44 pre-embedded documents
- **Groq LLaMA 3.3 70B**: Fast generation (3-5 seconds per itinerary)
- **Google Gemini 1.5 Pro**: Optional mode with 1M token context + caching (40% cost savings)
- **Day-by-Day Planning**: Automatic 4-day progression with morning/afternoon/evening activities

### 🧠 Advanced Features

**Recommendation Model**
- 4-dimensional intelligent ranking system
- Scoring: Budget fit (25%) | Activity match (30%) | Profile fit (30%) | Value (15%)
- Confidence scores and explainable recommendations per itinerary

**Hallucination Detection**
- Real places validation using known attractions database
- Prevents fake restaurants, hotels, or activities
- Per-city verified location lists

**Comprehensive 4-Layer Validation**
1. **Constraint Validation**: Budget limits, date ranges, traveler counts
2. **Hallucination Detection**: All place names against known real attractions
3. **Cost Integrity**: Daily/total budget verification
4. **Logic Validation**: Sensible activity distribution, temporal consistency

**Quality Scoring System**
- Automatic 0-100 quality assessment for every itinerary
- Penalty structure:
  - **-15 points**: Critical issues (budget overrun, hallucination)
  - **-5 points**: Warning-level issues (logical inconsistencies)
  - **-2 points**: Minor issues (suboptimal spacing)

### 📊 Real & Curated Data Sources

**100% Real Data (Kaggle-Verified)**
| Category | Source | Records |
|----------|--------|---------|
| **Hotels** | Datafiniti + TBO + Booking.com | 50,000+ |
| **Restaurants** | TripAdvisor European Dataset | 15,000+ |
| **Flights** | Kaggle Airlines Dataset | Real IATA codes |

**Curated, Traveler-Recommended Data**
| Category | Count | Source |
|----------|-------|--------|
| **Activities** | 12 per city | Expert-verified attractions |
| **Transport Routes** | 14 routes | FlixBus, train, flight data |
| **Ratings** | User feedback | Integrated into scoring |

All data sources are clearly labeled in the output JSON for transparency.

### ⚡ Performance

| Operation | Time |
|-----------|------|
| Semantic search (ChromaDB) | ~100ms |
| Groq itinerary generation | 3-5 seconds |
| Validation (4-layer) | ~50ms |
| **Total end-to-end** | **5-10 seconds** |

**With Google Gemini (Optional)**
- Context window: 1M tokens (125x larger than standard LLMs)
- Prompt caching: Reduces token cost by 40%
- Ideal for: Complex custom requests, multi-destination planning

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/zelihaguven/horizon.git
cd horizon

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for Gemini mode)
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for advanced features)
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

Get free API keys:
- **Groq**: [groq.com](https://groq.com) (30 requests/min on free tier)
- **Google**: [console.cloud.google.com](https://console.cloud.google.com)

### Running the Application

```bash
# Start Streamlit web UI (Recommended)
streamlit run app.py

# Or use as Python module
python main.py --destination Barcelona --days 5 --budget 3000
```

The Streamlit UI opens at `http://localhost:8501`

---

## 🏗️ How It Works

### 1️⃣ User Input Processing
- Destination (6 European cities)
- Duration (1-14 days)
- Budget (EUR)
- Traveler profile (budget/comfort/luxury)
- Special interests (optional)

### 2️⃣ Data Retrieval (RAG Pipeline)
```
User Query
    ↓
ChromaDB Semantic Search (44 embeddings)
    ↓
Relevant hotel/restaurant/activity documents
    ↓
SimpleRetriever (CSV-based restaurant lookups)
    ↓
Context documents → LLM
```

- **ChromaDB**: Semantic similarity matching (not keyword search)
- **SimpleRetriever**: Fast, deterministic CSV lookups for restaurants
- **Combined**: Best of both semantic and structured data

### 3️⃣ Itinerary Generation
- **LLM Selection**:
  - Default: Groq LLaMA 3.3 70B (fast, affordable)
  - Optional: Google Gemini 1.5 Pro (larger context, better for complex requests)
- **Output Format**: Structured JSON with day-by-day breakdown

### 4️⃣ Validation & Scoring
- 4-layer validation (constraints → hallucinations → costs → logic)
- Quality score calculation (0-100)
- Confidence indicators per recommendation

### 5️⃣ Multi-Variant Generation
- **Budget**: Cost-optimized option
- **Comfort**: Balanced price/experience
- **Luxury**: Premium experiences regardless of budget

---

## 📁 Project Structure

```
horizon/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
│
├── src/
│   ├── main.py                       # CLI entry point
│   ├── app.py                        # Streamlit web interface
│   ├── generator.py                  # Groq itinerary generation
│   ├── generator_gemini.py           # Google Gemini generation (optional)
│   ├── validator.py                  # 4-layer validation system
│   ├── recommendation_model.py       # ML-based ranking (4-dimensional)
│   ├── retriever.py                  # ChromaDB semantic search
│   ├── simple_retriever.py           # CSV-based restaurant lookups
│   ├── prompts.py                    # LLM system prompts
│   └── utils.py                      # Helper functions
│
├── data/
│   ├── processed/
│   │   └── travel_data.csv           # 44 embedded documents
│   ├── cities/
│   │   ├── london.json               # Known places (hallucination detection)
│   │   ├── paris.json
│   │   ├── berlin.json
│   │   └── ... (6 cities total)
│   └── examples/
│       ├── demo_paris_budget.json    # Example outputs
│       ├── demo_berlin_comfort.json
│       └── demo_barcelona_luxury.json
│
├── chroma_db/                        # Vector store (auto-initialized)
│   ├── index/
│   └── data/
│
└── tests/
    ├── test_generator.py
    ├── test_validator.py
    ├── test_retriever.py
    └── test_recommendation_model.py
```

---

## 🔧 Components Deep Dive

### ChromaDB Vector Store

- **44 Pre-embedded Documents**: Hotels, restaurants, activities, routes
- **Embedding Model**: OpenAI or Hugging Face (configurable)
- **Search Type**: Semantic similarity (finds contextually similar results, not keyword matches)
- **Lookup Time**: ~100ms per query
- **Storage**: Local file-based database (`chroma_db/`)

### Recommendation Model

Scores each itinerary option across 4 dimensions:

```python
score = (
    budget_fit_score * 0.25 +
    activity_match_score * 0.30 +
    user_profile_score * 0.30 +
    value_score * 0.15
)
```

- **Budget Fit (25%)**: How well the itinerary respects the budget constraint
- **Activity Match (30%)**: How well activities align with user interests
- **Profile Fit (30%)**: How well the experience matches traveler type (budget/comfort/luxury)
- **Value (15%)**: Price-to-experience ratio

Each dimension returns 0-100, final score is weighted average.

### Validation System

**Layer 1: Constraint Validation**
- Budget check: Total cost ≤ specified budget
- Date check: Duration matches requested days
- Traveler count: Valid for 1-10 people

**Layer 2: Hallucination Detection**
- Every hotel, restaurant, and activity is cross-referenced with a per-city database of known places
- Unknown places trigger a -15 penalty
- City-specific validation (e.g., a Barcelona restaurant in London itinerary = hallucination)

**Layer 3: Cost Integrity**
- Daily budgets sum to total budget
- No negative costs
- Tax/fee calculations are consistent

**Layer 4: Logic Validation**
- Activities are temporally consistent (no 3 evening activities on one day)
- Travel times between locations are realistic
- Activity distribution is balanced (not all activities in one day)

### LLM Options

**Default: Groq LLaMA 3.3 70B**
```python
from src.generator import GroqGenerator

gen = GroqGenerator(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)
itinerary = gen.generate(
    destination="Paris",
    days=5,
    budget=3000,
    style="comfort"
)
```
- **Speed**: 3-5 seconds per itinerary
- **Cost**: ~0.0001 USD per request
- **Rate limit**: 30 requests/minute (free tier)

**Optional: Google Gemini 1.5 Pro**
```python
from src.generator_gemini import GeminiGenerator

gen = GeminiGenerator(api_key=os.getenv("GOOGLE_API_KEY"))
itinerary = gen.generate(...)  # Same interface
```
- **Context**: 1M tokens (vs. 4K typical)
- **Caching**: 40% token cost reduction for repeated queries
- **Quality**: Better handling of complex custom requests
- **Cost**: Higher per-request, offset by caching

### SimpleRetriever

Fast, deterministic restaurant lookups:

```python
from src.simple_retriever import SimpleRetriever

retriever = SimpleRetriever("data/processed/travel_data.csv")
restaurants = retriever.search(
    city="Barcelona",
    cuisine="Spanish",
    price_range="€€",
    limit=5
)
```

- Loads CSV once
- Returns matching rows instantly
- Useful for: Quick restaurant suggestions, price filtering, cuisine-specific queries
- Complement to ChromaDB for structured data

---

## 📊 Example Output

```json
{
  "request": {
    "destination": "Barcelona",
    "duration_days": 5,
    "budget_eur": 3000,
    "travelers": 2,
    "style": "comfort"
  },
  "variants": [
    {
      "name": "Budget",
      "recommendation_score": 78.5,
      "label": "Most Affordable",
      "total_cost": 1200,
      "daily_budget": 240,
      "itinerary": {
        "day_1": [
          {
            "time": "morning",
            "activity": "Gothic Quarter Walking Tour",
            "location": "Barri Gòtic",
            "duration_hours": 2,
            "estimated_cost": 25,
            "type": "activity"
          }
        ]
      }
    },
    {
      "name": "Comfort",
      "recommendation_score": 92.3,
      "label": "⭐ BEST FOR YOU",
      "total_cost": 1800,
      "daily_budget": 360
    },
    {
      "name": "Luxury",
      "recommendation_score": 85.2,
      "label": "Premium Experience",
      "total_cost": 2800,
      "daily_budget": 560
    }
  ],
  "validation": {
    "status": "VALID",
    "quality_score": 94,
    "warnings": [],
    "hallucination_check": {
      "status": "PASSED",
      "verified_places": 28,
      "unknown_places": 0
    }
  },
  "metadata": {
    "generation_time_seconds": 4.2,
    "llm_used": "groq/llama-3.3-70b",
    "semantic_search_documents": 12,
    "generated_at": "2025-06-02T14:30:00Z"
  }
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_validator.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

Test coverage:
- **Generator**: Prompt formatting, output parsing
- **Validator**: All 4 validation layers
- **Recommendation Model**: Scoring calculations
- **Retriever**: ChromaDB queries, CSV fallback
- **End-to-end**: Full itinerary generation pipeline

---

## 🔑 API Requirements

### Required
- **Groq API Key**: [Get free key](https://console.groq.com)
  - Free tier: 30 requests/minute, unlimited daily requests
  - Sign up → Create API key → Add to `.env`

### Optional
- **Google API Key**: [Create at Cloud Console](https://console.cloud.google.com)
  - Enable Vertex AI API
  - Create service account credentials
  - Required only if using Gemini mode

### Testing the Connection

```bash
python -c "import os; from groq import Groq; print('✓ Groq connected')"
```

---

## 🔧 Troubleshooting

### "GROQ_API_KEY not found"
```bash
# Verify .env file exists and has correct key
cat .env

# Verify key is active at groq.com/console
# Try with explicit export
export GROQ_API_KEY=your_key
python main.py
```

### "ChromaDB error" / Vector store not found
```bash
# ChromaDB auto-initializes on first run
# If issue persists, clear and reinitialize:
rm -rf chroma_db/
python -c "from src.retriever import Retriever; Retriever().initialize()"
```

### "Rate limit exceeded"
- Free Groq tier: 30 requests/minute
- Solution 1: Wait 60 seconds before next request
- Solution 2: Use Gemini mode with caching
- Solution 3: Upgrade to Groq paid plan

### "RestaurantData not found"
- Verify `data/processed/travel_data.csv` exists (>1MB)
- Verify it has columns: `name`, `city`, `cuisine`, `price_range`, `rating`
- Run: `python -c "import pandas as pd; print(pd.read_csv('data/processed/travel_data.csv').head())"`

### "Streamlit not responding"
```bash
# Check port 8501 is available
lsof -i :8501

# Or use different port
streamlit run app.py --server.port 8502
```

### "Hallucination Detection returning false positives"
- Known places database is per-city in `data/cities/`
- Update with new verified places: `data/cities/{city}.json`
- Format:
  ```json
  {
    "restaurants": ["Tapas Bar", "Casa de Comidas"],
    "hotels": ["Hotel Barcelona", "Pension Central"],
    "attractions": ["Sagrada Familia", "Park Güell"]
  }
  ```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Easy Wins
- Add new cities (update `data/processed/travel_data.csv` + create `data/cities/{city}.json`)
- Add test cases (create `tests/test_*.py`)
- Improve UI/UX (modify `app.py`)
- Fix typos, improve documentation
- Add new validation layers

### New Features
- Multi-language itinerary support
- Additional LLM providers (OpenAI, Anthropic)
- Real-time price APIs (Booking.com, Skyscanner)
- Mobile app (React Native)
- Image generation for activities (DALL-E integration)

### How to Submit
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add feature: ...'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request with description of changes

### Code Style
- Follow PEP 8
- Type hints required for functions
- Docstrings for all modules/classes
- Tests required for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋 Support

- **Issues & Bugs**: [GitHub Issues](https://github.com/zelihaguven/horizon/issues)
- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical deep-dive
- **Email**: Open an issue on GitHub

---

## 🎯 Project Status

✅ **Production Ready** — All core features implemented and tested
- Semantic search with ChromaDB
- 4-layer validation system
- Hallucination detection
- Multi-variant recommendation model
- Streamlit UI deployment
- Support for 6 European cities

---

## 📈 Credits & Acknowledgments

- **Groq**: Fast LLM inference via LLaMA 3.3 70B
- **Google**: Gemini API & context caching
- **ChromaDB**: Vector database for semantic search
- **Streamlit**: Interactive web framework
- **Kaggle**: Real hotel, restaurant, and flight data
- **TripAdvisor**: European restaurant dataset

---

**Made with ❤️ for European travelers**


