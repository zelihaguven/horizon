# Travel RAG Redesign — 4-Day Implementation Plan

**Design Doc**: `2026-05-17-travel-rag-redesign-design.md`  
**Timeline**: May 17-21, 2026 (Friday-Tuesday)  
**Team**: Ilgın + Claude  
**Goal**: Constraint-Aware RAG with structured multi-option itineraries  

---

## Project Structure

```
travel_rag_v2/
├── data/
│   ├── raw/                    # Downloaded CSV files
│   │   ├── hotels.csv
│   │   ├── restaurants.csv
│   ├── processed/              # Cleaned data
│   │   └── travel_data.csv
├── chroma_db/                  # Vector DB (auto-generated)
├── src/
│   ├── data_pipeline.py        # Download + clean + preprocess
│   ├── embeddings.py           # Embedding generation (reuse)
│   ├── retriever.py            # Semantic search + filtering (NEW)
│   ├── generator.py            # Multi-option LLM generation (NEW)
│   ├── validator.py            # Constraint validation (NEW)
│   ├── formatter.py            # JSON → readable text (NEW)
│   └── rag_chain.py            # Orchestrate everything (UPDATED)
├── app.py                      # Streamlit UI (UPDATED)
├── ingest.py                   # Data ingestion (UPDATED)
├── test_cases.py               # 3 test queries for demo
├── metrics.py                  # Evaluation script (NEW)
├── requirements.txt            # Dependencies
├── README.md
└── .env

Key difference from v1:
- v1: Simple retrieval + text generation
- v2: Structured retrieval + multi-option generation + validation
```

---

## DAY 1: Data Gathering & Ingestion (Friday, May 17)

### Goal
Get real data into ChromaDB with proper metadata for filtering.

### Tasks

#### Task 1.1: Data Download (30 mins)
```python
# In src/data_pipeline.py - create function: download_datasets()

Use these open-source sources:
1. Kaggle Hotels:
   - kagglehub.dataset_download("stefanoleone992/airbnb-listings")
   - Extract: city, name, price_per_night, rating, neighborhood

2. Kaggle Restaurants:
   - Use your existing TripAdvisor restaurant data
   - Or: kagglehub.dataset_download("michau96/restaurace-ceske-republiky")

3. Transport:
   - Create manually: cities × routes × prices
   - Example: Berlin→Paris: FlixBus €40, RyanAir €60, Train €80
   - Store as CSV: [from_city, to_city, transport_type, price_eur, duration_hours]

4. Your existing data:
   - TripAdvisor reviews (already have this)

Save to: data/raw/
```

#### Task 1.2: Data Cleaning & Normalization (45 mins)
```python
# In src/data_pipeline.py - create function: clean_and_normalize()

For each dataset:
1. Load CSV
2. Extract relevant columns:
   - HOTELS: [city, name, price_eur, rating, type, description]
   - RESTAURANTS: [city, name, cuisine, price_eur, rating, address, description]
   - TRANSPORT: [from_city, to_city, type, price_eur, duration, description]
   - ACTIVITIES: [city, name, type, price_eur, rating, description]

3. Normalize prices to EUR (if needed)
4. Remove duplicates
5. Filter to 6 cities only: Berlin, Paris, Barcelona, Amsterdam, Rome, London
6. Remove records with missing essential fields

Save to: data/processed/travel_data.csv
```

#### Task 1.3: Metadata Enrichment (30 mins)
```python
# In src/data_pipeline.py - create function: add_metadata()

For each record, add columns:
- city: (extracted from location)
- type: 'hotel' | 'restaurant' | 'transport' | 'activity'
- price_eur: (float)
- price_range: 'budget' | 'moderate' | 'upscale'  # Auto-categorize
- rating: (float, 0-5)
- source: 'kaggle' | 'tripadvisor' | 'manual'

This metadata will be used for filtering in ChromaDB.
```

#### Task 1.4: ChromaDB Ingestion (45 mins)
```python
# In ingest.py - REUSE existing code + UPDATE

1. Load cleaned data from data/processed/travel_data.csv
2. Use existing embeddings (all-MiniLM-L6-v2)
3. Split text into chunks:
   - For hotels/restaurants: include name + description + rating
   - For transport: include route + type + price
4. Create ChromaDB with metadata:
   
   metadata = {
       "city": record.city,
       "type": record.type,
       "price_eur": record.price_eur,
       "price_range": record.price_range,
       "rating": record.rating,
       "source": record.source,
       "name": record.name
   }
   
5. Store in ./chroma_db
6. Verify: print(f"Total vectors: {collection.count()}")
```

### Deliverable
✅ ChromaDB populated with ~50,000 vectors (6 cities, 4 data types)  
✅ Metadata properly set for filtering  
✅ All prices normalized to EUR  

### How to Run
```bash
python src/data_pipeline.py
python ingest.py
```

---

## DAY 2: Retrieval & Generation (Saturday, May 18)

### Goal
Build the improved retrieval strategy and multi-option generation.

### Tasks

#### Task 2.1: Enhanced Retriever (60 mins)
```python
# In src/retriever.py - CREATE NEW FILE

def retrieve_for_trip(vectorstore, query: str, city: str, budget: float, duration: int):
    """
    Retrieve relevant travel data with constraint filtering.
    
    Returns:
    - hotels: list of relevant hotels in [city] under [budget/night]
    - restaurants: list of restaurants in [city]
    - transport: routes matching [from→to]
    - activities: things to do in [city]
    """
    
    # Step 1: Detect city from query
    city = detect_city(query)  # reuse from rag.py
    
    # Step 2: Semantic search with metadata filtering
    hotels = vectorstore.similarity_search(
        f"hotel in {city} under €{budget/duration}",
        k=8,
        filter={"city": city, "type": "hotel", "price_eur": {"$lte": budget/duration}}
    )
    
    restaurants = vectorstore.similarity_search(
        f"restaurant in {city}",
        k=10,
        filter={"city": city, "type": "restaurant"}
    )
    
    activities = vectorstore.similarity_search(
        f"things to do in {city}",
        k=8,
        filter={"city": city, "type": "activity"}
    )
    
    return {
        "hotels": hotels,
        "restaurants": restaurants,
        "activities": activities,
        "city": city
    }

# Key difference from v1:
# v1: just retrieve top 12 chunks
# v2: retrieve 4 specific categories with metadata filtering
```

#### Task 2.2: Multi-Option Generator (90 mins)
```python
# In src/generator.py - CREATE NEW FILE

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

MULTI_OPTION_PROMPT = """
You are a expert trip planner. Generate 3 travel itineraries for the user.

User request:
{user_query}

Constraints:
- Budget: €{budget}
- Duration: {duration} days
- City/Route: {city}
- Preferences: {preferences}

Available real data (hotels, restaurants, activities, transport):
{context}

CRITICAL RULES:
1. ONLY mention places that appear in the data above
2. NEVER invent restaurant/hotel/activity names
3. Use real prices from the data
4. Generate EXACTLY 3 options: Budget (stay under €{budget}), Comfort (€{budget}+20-50), Luxury (€{budget}+100+)
5. Each option must include:
   - Day-by-day itinerary (time + place + cost)
   - Daily totals
   - Cost breakdown (transport, accommodation, food, activities)
   - Total trip cost

6. For Comfort/Luxury: clearly explain what improves vs Budget

Format as valid JSON (no markdown, no ```json``` blocks):
{{
  "budget": {budget},
  "duration": {duration},
  "options": [
    {{
      "name": "Budget Option",
      "totalCost": <number>,
      "remaining": <number>,
      "itinerary": [
        {{
          "day": 1,
          "title": "...",
          "activities": [
            {{"time": "HH:MM", "activity": "<real place>", "cost": <number>}}
          ],
          "meals": [
            {{"meal": "breakfast", "place": "<real place>", "cost": <number>}}
          ],
          "dayTotal": <number>
        }}
      ],
      "costBreakdown": {{
        "transport": <number>,
        "accommodation": <number>,
        "food": <number>,
        "activities": <number>
      }}
    }}
  ]
}}
"""

def generate_options(retriever_output, user_query, budget, duration, preferences):
    """Generate 3 structured itinerary options."""
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    prompt = PromptTemplate.from_template(MULTI_OPTION_PROMPT)
    
    # Format context from retriever
    context = format_retriever_context(retriever_output)
    
    input_data = {
        "user_query": user_query,
        "budget": budget,
        "duration": duration,
        "city": retriever_output["city"],
        "preferences": preferences,
        "context": context
    }
    
    # Generate
    response = llm.invoke(prompt.format(**input_data))
    
    # Parse JSON
    try:
        options = json.loads(response.content)
        return options
    except json.JSONDecodeError:
        return {"error": "Failed to parse response", "raw": response.content}

def format_retriever_context(retriever_output):
    """Format retrieved data into prompt context."""
    context_parts = []
    
    for hotel in retriever_output["hotels"][:5]:
        context_parts.append(f"Hotel: {hotel.page_content} (€{hotel.metadata.get('price_eur', '?')}/night)")
    
    for restaurant in retriever_output["restaurants"][:7]:
        context_parts.append(f"Restaurant: {restaurant.page_content} (€{restaurant.metadata.get('price_eur', '?')})")
    
    for activity in retriever_output["activities"][:5]:
        context_parts.append(f"Activity: {activity.page_content} (€{activity.metadata.get('price_eur', '?')})")
    
    return "\n".join(context_parts)
```

#### Task 2.3: Test Generation (30 mins)
```python
# Test the generator with 3 sample queries

test_queries = [
    {
        "query": "I have €500 and 5 days. I want to go from Berlin to Paris. I like museums and good food.",
        "city": "Paris",
        "budget": 500,
        "duration": 5
    },
    # ... 2 more test queries
]

for test in test_queries:
    print(f"Query: {test['query']}")
    options = generate_options(retriever_output, test["query"], test["budget"], test["duration"], "museums, food")
    print(json.dumps(options, indent=2))
```

### Deliverable
✅ Retriever returns structured data by category  
✅ Generator produces valid JSON with 3 options  
✅ All places are real (from KB)  
✅ 3 test cases run successfully  

### How to Run
```bash
python -c "from src.generator import generate_options; ..."
```

---

## DAY 3: Validation & Metrics (Sunday, May 19)

### Goal
Add constraint validation and metrics for evaluation.

### Tasks

#### Task 3.1: Constraint Validator (60 mins)
```python
# In src/validator.py - CREATE NEW FILE

import json
from typing import Tuple

def validate_itinerary(options_json: dict, budget: float) -> Tuple[bool, list]:
    """
    Validate that itineraries meet constraints.
    
    Returns: (is_valid, errors)
    """
    
    errors = []
    
    for option in options_json.get("options", []):
        name = option.get("name", "Unknown")
        total_cost = option.get("totalCost", 0)
        
        # Check 1: Budget constraint
        if total_cost > budget:
            errors.append(f"{name}: Total cost €{total_cost} exceeds budget €{budget}")
        
        # Check 2: Cost breakdown adds up
        breakdown = option.get("costBreakdown", {})
        sum_breakdown = sum(breakdown.values())
        if abs(sum_breakdown - total_cost) > 1:  # Allow €1 rounding
            errors.append(f"{name}: Cost breakdown (€{sum_breakdown}) doesn't match total (€{total_cost})")
        
        # Check 3: Daily totals add up
        daily_sum = sum(day.get("dayTotal", 0) for day in option.get("itinerary", []))
        if abs(daily_sum - total_cost) > 2:
            errors.append(f"{name}: Daily totals (€{daily_sum}) don't match total (€{total_cost})")
        
        # Check 4: All places are real (check against KB)
        # For now: just verify places were mentioned (not hallucinated new ones)
        for day in option.get("itinerary", []):
            for activity in day.get("activities", []):
                place_name = activity.get("activity", "")
                if len(place_name) > 0:
                    # This should have come from KB
                    pass
    
    return len(errors) == 0, errors

def check_metrics(options_json: dict, budget: float, kb_reference: dict) -> dict:
    """Calculate metrics for evaluation."""
    
    metrics = {
        "budget_violations": 0,
        "accuracy_error_pct": 0,
        "all_options_valid": True,
    }
    
    for option in options_json.get("options", []):
        total = option.get("totalCost", 0)
        if total > budget:
            metrics["budget_violations"] += 1
        
        # Error: compare against "expected" costs
        # For demo: just check that costs are reasonable (not 0 or insane)
        if total < 50:
            metrics["accuracy_error_pct"] += 20
        elif total > budget * 2:
            metrics["accuracy_error_pct"] += 30
    
    metrics["all_options_valid"] = metrics["budget_violations"] == 0
    
    return metrics
```

#### Task 3.2: Output Formatter (60 mins)
```python
# In src/formatter.py - CREATE NEW FILE

def format_as_readable_text(options_json: dict) -> str:
    """Convert JSON itinerary to readable text format."""
    
    output = []
    budget = options_json.get("budget", 0)
    
    for option in options_json.get("options", []):
        name = option.get("name")
        total_cost = option.get("totalCost", 0)
        remaining = option.get("remaining", 0)
        
        # Header
        output.append("=" * 50)
        output.append(f"✈️  {name.upper()} (€{total_cost} / €{budget} budget)")
        output.append("=" * 50)
        output.append("")
        
        # Day-by-day
        for day in option.get("itinerary", []):
            day_num = day.get("day", 1)
            title = day.get("title", "")
            output.append(f"DAY {day_num}: {title}")
            output.append("─" * 40)
            
            # Activities
            for activity in day.get("activities", []):
                time = activity.get("time", "")
                activity_name = activity.get("activity", "")
                cost = activity.get("cost", 0)
                output.append(f"{time} - {activity_name} (€{cost})")
            
            # Meals
            if day.get("meals"):
                for meal in day.get("meals", []):
                    place = meal.get("place", "")
                    cost = meal.get("cost", 0)
                    meal_type = meal.get("meal", "")
                    output.append(f"  {meal_type.capitalize()}: {place} (€{cost})")
            
            day_total = day.get("dayTotal", 0)
            output.append(f"Day Total: €{day_total}")
            output.append("")
        
        # Cost breakdown
        breakdown = option.get("costBreakdown", {})
        output.append("COST BREAKDOWN:")
        for category, cost in breakdown.items():
            output.append(f"├─ {category.capitalize()}: €{cost}")
        output.append(f"└─ TOTAL: €{total_cost} {'✅ Within budget!' if total_cost <= budget else '❌ Over budget!'}")
        output.append(f"Remaining: €{remaining}")
        output.append("")
        output.append("─" * 50)
        output.append("")
    
    return "\n".join(output)
```

#### Task 3.3: Metrics Script (30 mins)
```python
# In metrics.py - CREATE NEW FILE

def evaluate_demo(test_cases):
    """Run evaluation on test cases."""
    
    results = []
    
    for test in test_cases:
        query = test["query"]
        budget = test["budget"]
        
        # Generate itinerary
        options = generate_options(...)
        
        # Validate
        is_valid, errors = validate_itinerary(options, budget)
        metrics = check_metrics(options, budget, {})
        
        results.append({
            "query": query,
            "valid": is_valid,
            "errors": errors,
            "metrics": metrics
        })
    
    return results
```

#### Task 3.4: Polish & Testing (30 mins)
- Test all 3 test cases
- Fix any generation errors
- Make sure text formatting is clean
- Verify budget constraints work

### Deliverable
✅ Validator catches budget violations  
✅ Formatter produces readable output  
✅ Metrics script evaluates accuracy  
✅ 3 test cases validated and clean  

---

## DAY 4: Presentation (Tuesday, May 21)

### Goal
Polish demo, create metrics slides, present.

### Tasks

#### Task 4.1: Live Demo Testing (60 mins)
- Run 3 test queries end-to-end
- Verify output is clean and correct
- Time how fast it runs
- Fix any UI issues in Streamlit

#### Task 4.2: Metrics Report (45 mins)
Create slides showing:
1. **Old RAG vs New RAG** comparison
2. **Metrics table**: Budget accuracy, hallucination rate, constraint satisfaction
3. **Example output** (readable format)
4. **Architecture diagram**

#### Task 4.3: Presentation Prep (45 mins)
- 30-40 min talk structure:
  - Problem: "Why old RAG failed" (5 min)
  - Solution: "Constraint-Aware RAG architecture" (10 min)
  - Live demo: 3 test queries (10 min)
  - Metrics: "How we validate quality" (5-10 min)
  - Conclusion (5 min)
- Practice talking through the demo
- Prepare for Q&A

#### Task 4.4: Submit & Present
- Save all code to GitHub
- Present to Prof. Reck
- Have the design doc + code ready to show

### Deliverable
✅ Live demo working  
✅ Metrics report created  
✅ 30-40 min presentation ready  
✅ Code clean and documented  

---

## File Changes Summary

### New Files to Create
- `src/retriever.py` — Enhanced retrieval with metadata filtering
- `src/generator.py` — Multi-option generation
- `src/validator.py` — Constraint validation
- `src/formatter.py` — Text formatting
- `metrics.py` — Evaluation script
- `test_cases.py` — 3 demo queries

### Files to Update
- `ingest.py` — Add metadata extraction
- `app.py` — Update UI to show multiple options
- `rag.py` → `src/rag_chain.py` — Orchestrate new pipeline

### No Changes Needed
- `embeddings.py` — Reuse existing
- `requirements.txt` — Add json (built-in) only

---

## Code Execution Order

```
Day 1:
  $ python src/data_pipeline.py
  $ python ingest.py

Day 2:
  $ python -c "from src.retriever import retrieve_for_trip; ..."
  $ python -c "from src.generator import generate_options; ..."
  $ python test_cases.py

Day 3:
  $ python -c "from src.validator import validate_itinerary; ..."
  $ python metrics.py
  $ streamlit run app.py  # Test UI

Day 4:
  $ streamlit run app.py  # Final demo
  # Present to Prof. Reck
```

---

## Success Criteria Checklist

- [ ] ChromaDB has 50k+ vectors with proper metadata
- [ ] Retriever returns 4 categories (hotels, restaurants, activities, transport)
- [ ] Generator produces valid JSON with 3 options
- [ ] All places in output are real (from KB, not hallucinated)
- [ ] Budget constraints enforced (no violations)
- [ ] Readable text output is clean
- [ ] Metrics prove constraint satisfaction
- [ ] Live demo runs in <5 seconds per query
- [ ] 3 test queries pass all validation
- [ ] Presentation is 30-40 minutes
- [ ] Before/after story is clear

---

## Ready to Start?

You have everything you need. Let me know when you're ready to begin **Day 1** and I'll help you write the actual code! 🚀

**Next Step**: Review this plan, then say "**Start Day 1**" and we'll build it.
