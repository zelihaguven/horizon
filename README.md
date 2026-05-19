# 🌍 Horizons - AI-Powered Travel Planning

> Premium, intelligent travel itinerary generation using Retrieval-Augmented Generation (RAG) and Groq LLaMA 3.3 70B

A beautifully designed web application that generates personalized, budget-aware travel itineraries using advanced AI and real restaurant data.

## ✨ Features

- **🤖 AI-Powered Generation**: Uses Groq LLaMA 3.3 70B for intelligent itinerary creation
- **🏨 Real Restaurant Database**: 30 verified restaurants across 6 European cities
- **💰 Smart Budget Breakdown**: Automatic cost distribution across accommodation, meals, activities, and transport
- **🎯 Multiple Budget Tiers**: Budget, Comfort, and Luxury variants for every trip
- **📊 4-Part Cost System**: Detailed breakdown of all expenses with per-person calculations
- **🎨 Clean Interface**: Minimalist light theme with professional styling and smooth animations
- **⚡ Fast Retrieval**: CSV-based SimpleRetriever for instant restaurant lookups
- **✅ Smart Validation**: Constraint checking and budget-aware planning

## 🌆 Supported Destinations

| City | Restaurants | Cuisine Types |
|------|------------|---------------|
| 🇬🇧 London | 5+ | Fine Dining, Casual, Street Food |
| 🇫🇷 Paris | 5+ | Bistro, Haute Cuisine, Cafés |
| 🇩🇪 Berlin | 5+ | Traditional, Street Food, Modern |
| 🇪🇸 Barcelona | 5+ | Tapas, Molecular, Catalan |
| 🇳🇱 Amsterdam | 5+ | Dutch, Fine Dining, Casual |
| 🇮🇹 Rome | 5+ | Traditional, Fine Dining, Local |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key (free tier available at [groq.com](https://groq.com))
- 4GB RAM minimum

### Installation

```bash
# Clone the repository
git clone https://github.com/zelihaguven/horizon.git
cd horizon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 How It Works

### System Architecture

```
User Input
    ↓
[Travel Information] → Departure/Destination Cities, Duration, Budget, Travelers, Preferences
    ↓
[RAG Retriever] → SimpleRetriever searches restaurant database (CSV)
    ↓
[Context Assembly] → Builds context with relevant restaurants and travel constraints
    ↓
[LLM Generation] → Groq LLaMA 3.3 70B generates detailed itinerary
    ↓
[Validation] → Validates against budget constraints and preferences
    ↓
[Formatting] → Generates 3 variants: Budget, Comfort, Luxury
    ↓
Output: Complete itineraries with daily schedules and cost breakdowns
```

### Key Components

1. **Retriever** (`retriever.py`, `simple_retriever.py`)
   - CSV-based restaurant lookup
   - Fast filtering by city and preferences
   - No external database required

2. **Generator** (`generator.py`, `generator_gemini.py`)
   - Groq LLaMA 3.3 70B for itinerary generation
   - Optional Google Gemini support
   - Multi-variant generation

3. **Prompts** (`prompts.py`)
   - Carefully engineered system and user prompts
   - Budget-aware generation instructions
   - Preference-based customization

4. **Validator** (`validator.py`)
   - Budget constraint validation
   - Preference matching verification
   - Cost breakdown verification

5. **Interface** (`app.py`)
   - Streamlit web UI with clean, minimalist design
   - Real-time budget calculations
   - Interactive city selection dropdowns
   - Beautiful variant cards display

## 📊 Output Example

For a 3-day trip from London to Paris with €900 budget and 2 travelers:

```
BUDGET VARIANT
├─ Daily Cost: €150/person
├─ Accommodation: Hotel (€40/night)
├─ Meals: Street food & cafés
├─ Activities: Free museums, parks
└─ Transport: Public transit pass

COMFORT VARIANT
├─ Daily Cost: €300/person
├─ Accommodation: 3-star hotel (€80/night)
├─ Meals: Nice restaurants (€25-35/meal)
├─ Activities: Guided tours, galleries
└─ Transport: Taxi + Metro

LUXURY VARIANT
├─ Daily Cost: €450/person
├─ Accommodation: 5-star hotel (€200/night)
├─ Meals: Michelin-starred restaurants
├─ Activities: Private tours, experiences
└─ Transport: Private car service
```

## 🛠 Configuration

### Environment Variables

```env
# Required
GROQ_API_KEY=your_api_key_here

# Optional
GOOGLE_API_KEY=your_gemini_key_here  # For Gemini support
USE_CACHE=true
LOG_LEVEL=INFO
```

### Customization

- **Add new cities**: Update `data/processed/travel_data.csv`
- **Modify prompts**: Edit `prompts.py`
- **Change budget tiers**: Update cost ratios in `main.py`
- **Customize theme**: Modify CSS in `app.py`

## 📁 Project Structure

```
horizon/
├── app.py                          # Streamlit web interface
├── main.py                         # TravelRAG main class
├── retriever.py                    # Retrieval logic
├── simple_retriever.py             # SimpleRetriever implementation
├── generator.py                    # Groq LLaMA generation
├── generator_gemini.py             # Google Gemini alternative
├── prompts.py                      # LLM prompt templates
├── validator.py                    # Budget & constraint validation
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore
├── README.md
├── ARCHITECTURE.md                 # Detailed system design
├── data/
│   └── processed/
│       └── travel_data.csv         # Restaurant database
└── examples/
    ├── demo_paris_budget.json
    ├── demo_berlin_comfort.json
    └── demo_barcelona_luxury.json
```

## 🧪 Testing

The project includes demo itineraries for testing:

```bash
# These JSON files show example outputs
examples/demo_paris_budget.json
examples/demo_berlin_comfort.json
examples/demo_barcelona_luxury.json
```

## 🔧 API Requirements

### Groq API
- **Free tier**: Excellent for development and testing
- **Rate limits**: Up to 30 calls per minute
- **Model**: LLaMA 3.3 70B (latest)
- **Get key**: [groq.com](https://groq.com)

### Optional: Google Gemini
- **Alternative LLM**: For comparison or fallback
- **API key**: From [Google AI Studio](https://aistudio.google.com)

## 📚 Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system design and prompt engineering
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive installation guide
- **[examples/](examples/)** - Sample outputs and use cases

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more cities and restaurants
- [ ] Support for more languages
- [ ] Mobile-responsive design improvements
- [ ] Additional LLM providers
- [ ] Performance optimizations
- [ ] Unit and integration tests

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Ilgın Güven** - AI & Travel Enthusiast

## 🙏 Acknowledgments

- [Groq](https://groq.com) - LLaMA 3.3 70B API
- [Streamlit](https://streamlit.io) - Web framework
- [LangChain](https://langchain.com) - RAG framework
- European city data - Manual curation & research

## 📞 Support

For issues, questions, or suggestions:
1. Open an [issue](https://github.com/zelihaguven/horizon/issues)
2. Check existing documentation
3. Review example outputs

---

**Built with ❤️ using RAG and AI** | *Making travel planning intelligent and accessible*
