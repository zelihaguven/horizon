# Day 2: Retrieval & Generation - Setup & Testing

## Status: ✅ Complete (Files Created)

Three core files have been created for Day 2:
- **retriever.py** - Semantic search + metadata filtering layer
- **generator.py** - LLM-based multi-option itinerary generation  
- **main.py** - Full orchestration pipeline

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Or install key packages individually:
```bash
pip install groq sentence-transformers langchain-chroma langchain-community --break-system-packages
```

### 2. Set Environment Variables

Create a `.env` file in the project directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com/keys

## Architecture Overview

```
Data Layer (ChromaDB)
    ↓
Retriever (semantic search + filtering)
    ↓
Generator (LLM-based creation)
    ↓
Validator (constraint checking)
    ↓
Structured Output (JSON itineraries)
```

## Testing Components

### Test Retriever Only
```bash
python retriever.py
```

This tests:
- ChromaDB initialization
- Semantic search functionality
- Category-specific filtering
- Metadata extraction

### Test Generator Only
```bash
python generator.py
```

This tests:
- Groq LLM connection
- Prompt generation
- JSON parsing
- Cost breakdown creation

### Run Full Demo
```bash
python main.py
```

This runs complete end-to-end demos:
1. Budget Paris trip (3 days, €600)
2. Comfort Berlin trip (4 days, €1200)
3. Luxury Barcelona trip (5 days, €3000)

Output: Saves JSON files with all variants

## Component Details

### retriever.py

**Class: TravelRetriever**
- `retrieve()` - Generic semantic search with optional metadata filters
- `retrieve_by_category()` - Category-specific search (hotel/restaurant/activity/transport)
- `get_collection_stats()` - Check ChromaDB status

**Returns:**
```json
{
  "text": "hotel description",
  "metadata": {
    "name": "Hotel Name",
    "city": "Paris",
    "price_eur": 85,
    "type": "hotel",
    "rating": 4.5
  },
  "similarity": 0.92
}
```

### generator.py

**Class: ConstraintAwareGenerator**
- `generate_itinerary()` - Main method for creating multi-option itineraries
- Returns variants with cost breakdowns and daily itineraries
- Uses Groq LLaMA 3.3 70B model for generation

**Input:**
```python
generator.generate_itinerary(
    destination="Paris",
    duration_days=3,
    budget_eur=900,
    preferences=["museums", "food"],
    travelers=2
)
```

**Output:** 3 variants (Budget, Comfort, Luxury) with:
- Daily itinerary breakdown
- Cost breakdown (accommodation, meals, activities, transport)
- Highlights and notes
- Per-person cost calculation

### main.py

**Class: TravelRAG**
- `plan_trip()` - Generate complete itinerary
- `print_itinerary()` - Pretty-print output
- `save_itinerary()` - Export to JSON

**Usage:**
```python
rag = TravelRAG()
itinerary = rag.plan_trip(
    destination="Paris",
    duration_days=3,
    budget_eur=900,
    preferences=["museums"],
    travelers=2
)
rag.print_itinerary(itinerary)
rag.save_itinerary(itinerary)
```

## Expected Output Example

```
TRAVEL RAG: 3-day trip to Paris
============================================================
Budget: €900 | Travelers: 2
Preferences: museums, food

1. BUDGET
   ────────────────────────────────
   Accommodation: €150.00
   Meals:         €300.00
   Activities:    €300.00
   Transport:     €150.00
   ────────────────────────────────
   TOTAL:         €900.00
   Highlights: Louvre Museum, Street Food, Seine Walk

2. COMFORT
   ────────────────────────────────
   Accommodation: €250.00
   Meals:         €350.00
   Activities:    €225.00
   Transport:     €75.00
   ────────────────────────────────
   TOTAL:         €900.00
   Highlights: Versailles, Michelin Restaurant, Seine Cruise

3. LUXURY
   ────────────────────────────────
   Accommodation: €400.00
   Meals:         €350.00
   Activities:    €100.00
   Transport:     €50.00
   ────────────────────────────────
   TOTAL:         €900.00
   Highlights: 5-Star Hotel, Michelin 3-Star, Private Tours
```

## Troubleshooting

### Error: "No module named 'groq'"
```bash
pip install groq --break-system-packages
```

### Error: "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers --break-system-packages
```

### Error: "GROQ_API_KEY not found"
- Create `.env` file with `GROQ_API_KEY=your_key`
- Or set environment variable: `export GROQ_API_KEY=your_key`

### ChromaDB not found
- Run `python ingest.py` from Day 1 first to create ChromaDB
- Verify `./chroma_db/` directory exists

## Next Steps (Day 3)

Day 3 will add:
- Constraint validation layer (enforce budget, check place availability)
- Metrics collection (token usage, generation time, quality scores)
- Hallucination detection (verify LLM doesn't invent attractions)
- Evaluation script comparing Budget vs Comfort vs Luxury variants

## Files Generated

Running `main.py` creates:
- `demo_paris_budget.json` - Full itinerary with metadata
- `demo_berlin_comfort.json` - Full itinerary with metadata  
- `demo_barcelona_luxury.json` - Full itinerary with metadata

Each JSON contains:
- Request parameters
- All variants with cost breakdowns
- Daily activity breakdown
- Generation metadata
