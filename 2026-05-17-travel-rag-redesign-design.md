# Travel RAG Redesign — Design Document

**Date**: May 17, 2026  
**Project**: AI Travel Assistant (Constraint-Aware RAG)  
**Timeline**: 4 days (May 17-21)  
**Team**: Ilgın Güven + Claude  
**Scope**: Redesign current RAG to generate structured, multi-option itineraries with budget validation  

---

## Executive Summary

The current RAG system gives **poor, non-specific answers** because it treats trip planning as pure semantic search + generic text generation. This redesign pivots to a **Constraint-Aware RAG** that:

1. ✅ Retrieves structured travel data (hotels, restaurants, transport) with metadata filtering
2. ✅ Generates **3 structured options** (Budget/Comfort/Luxury) with day-by-day itineraries
3. ✅ **Validates constraints** (budget, real places, accurate costs)
4. ✅ Shows **trade-offs** ("Pay €35 more for: 3-star hotel + better restaurants")
5. ✅ Outputs **JSON + readable text** for both validation and presentation

**Why this meets Prof. Reck's requirements:**
- Uses **semantic search + ChromaDB** (RAG compliance ✓)
- **Retrieval grounds generation** (no hallucination, uses real data)
- Demonstrates **constraint satisfaction** + multi-step reasoning
- Shows the system works reliably on constrained problems

---

## Problem Statement

**Current System Issues:**
1. Generic prompt → single generic text answer
2. No budget/constraint awareness → LLM hallucinates prices, violates budget
3. No structured output → hard to validate or present
4. No alternative options → user has no choice
5. Hallucination risk → invented restaurant names, inaccurate prices

**Example of Current Failure:**
```
User: "€500, Berlin→Paris, 5 days, what can I do?"
Current Output: "Paris is a beautiful city with many restaurants. You could visit 
the Louvre, try some French cuisine, and stay in hotels. Budget-friendly options 
exist..."
[Generic, inaccurate costs, no itinerary, no specifics]
```

**What We Need:**
- Real, verified places from knowledge base
- Accurate cost breakdown per day
- Multiple options ranked by value
- Clear trade-offs between options
- Validated constraint satisfaction

---

## Architecture

### System Flow

```
User Query
    ↓
Query Enhancement (extract: city, budget, duration, preferences)
    ↓
Semantic Search + Metadata Filtering (ChromaDB)
    - Retrieve hotels in [city] under [budget/night]
    - Retrieve restaurants in [city]
    - Retrieve transport routes [start→end]
    ↓
Multi-Option Generation (LLM)
    - Generate 3 structured options (Budget/Comfort/Luxury)
    - Format as day-by-day itinerary JSON
    ↓
Constraint Validation
    - Check: total cost ≤ budget?
    - Check: all places exist in KB?
    - Check: cost accuracy ±5%?
    ↓
Output Formatting
    - JSON (for validation/metrics)
    - Readable text (for demo/presentation)
    ↓
User
```

### 4 Core Components

**1. Data Layer**
- Open-source datasets (Kaggle, public APIs)
- Preprocessing: normalize prices (→ EUR), extract metadata (city, type, price, rating)
- Storage: ChromaDB with metadata fields (`city`, `price_eur`, `type`, `rating`)
- Scope: 5-6 cities (Berlin, Paris, Barcelona, Amsterdam, Rome, London)

**2. Retrieval Layer (Semantic Search)**
- Query → extract constraints (budget, city, duration)
- ChromaDB semantic search: "affordable hotels in Paris"
- Metadata filtering: only hotels under €30/night
- Combine results: hotels + restaurants + transport all in one context
- **Still RAG-compliant**: uses vector DB + semantic search

**3. Generation Layer (Multi-Option LLM)**
- Structured prompt template (generates JSON, not text)
- Creates 3 options:
  - **Budget**: Stay under €500 strictly
  - **Comfort**: +€20-50, show what improves
  - **Luxury**: Show what's possible with higher budget
- Format: day-by-day breakdown with real place names + costs from KB
- **Never hallucinate**: only mention places that exist in retrieved data

**4. Validation Layer**
- Post-processing: parse JSON, check constraints
- Verify: total cost ≤ budget
- Verify: all place names exist in KB
- Verify: cost breakdown adds up
- Flag errors → regenerate or output "insufficient data"
- Add "remaining budget" field

---

## Data Sources & Integration

### Datasets to Use

**Transport:**
- Kaggle: `tcreusen/train-tickets-germany-2019` (example)
- OR: Rome2Rio API (free tier)
- OR: FlixBus/Ryanair public pricing

**Accommodation:**
- Kaggle: `stefanoleone992/airbnb-listings` (or Booking.com scrape limited)
- Your existing TripAdvisor hotel reviews

**Restaurants & Activities:**
- Your existing TripAdvisor review data (cleaned)
- Kaggle restaurant datasets

### Data Preprocessing Pipeline

```python
# Pseudo-code
1. Load all CSVs
2. For each record:
   - Extract: [city, name, type, price_original, rating, description]
   - Normalize price → EUR
   - Create metadata: {city, type, price_eur, rating}
   - Clean text (remove junk)
3. Chunk descriptions (700 chars, 50 char overlap)
4. Store in ChromaDB with metadata
```

### Scope Declaration (For Presentation)

> "For this demo, we implemented trip planning for: **Berlin, Paris, Barcelona, Amsterdam, Rome, London** with transport via **FlixBus/Ryanair** and accommodation from **hotel/hostel data**. This covers ~50,000 real records (hotels, restaurants, activities) in these 6 cities."

---

## Generation Strategy

### Why Current RAG Fails

1. **Generic prompt** → asks for text, not structure
2. **No constraint awareness** → LLM doesn't check if answer fits budget
3. **Single answer** → no alternatives
4. **Hallucination risk** → LLM invents places

### The Fix: Structured, Multi-Option Generation

**Improved Prompt Template:**

```
You are a trip planner. The user wants a trip with specific constraints.

User request:
{user_query}

Example: "€500, Berlin→Paris, 5 days, romantic"

Constraints:
- Budget: €500 (MUST NOT EXCEED)
- Duration: 5 days
- Route: Berlin → Paris

Retrieved real data (hotels, restaurants, transport):
{context_from_chromadb}

IMPORTANT RULES:
1. ONLY mention places that appear in the data above (never invent names)
2. Use real prices from the data
3. Generate EXACTLY 3 options: Budget, Comfort, Luxury
4. Format output as JSON with day-by-day breakdown
5. Each option must show cost breakdown: transport, accommodation, food, activities
6. For Comfort/Luxury: explain the trade-off vs Budget option

Generate 3 complete itinerary options as JSON:
{
  "options": [
    {
      "name": "Budget Option",
      "totalCost": <number>,
      "itinerary": [
        {
          "day": 1,
          "activities": [
            {"time": "HH:MM", "activity": "<real place from data>", "cost": <number>}
          ],
          "dayTotal": <number>
        }
      ],
      "costBreakdown": {...}
    }
  ]
}
```

### Generation Process

1. **Retrieval**: Get hotels, restaurants, transport from ChromaDB
2. **Prompt**: Use structured template above
3. **LLM Call**: Generate 3 options with real places + prices
4. **Validation**: Check JSON structure, costs, place names
5. **Error Handling**: If invalid → regenerate or flag "insufficient data"

---

## Output Format

### What User Sees (Readable Text)

```
========================================
✈️  BUDGET OPTION (€485 / €500 budget)
========================================

DAY 1: Berlin → Paris (Travel Day)
─────────────────────────────────────
08:00 - FlixBus Berlin→Paris (€40, 14h)
22:00 - Hostel du Marais, Paris (€25/night)

Meals: Café breakfast (€8) + Budget bistro dinner (€12)
Day Total: €85 | Spent: €85 | Remaining: €415

[Days 2-5...]

COST BREAKDOWN:
├─ Transport: €120
├─ Accommodation: €125
├─ Food: €180
└─ Activities: €60
TOTAL: €485 ✅ Within budget!

────────────────────────────────────────────

💎 COMFORT OPTION (€520)
Pay €35 more → Upgrade: 3-star hotel + better restaurants
[Full itinerary...]

────────────────────────────────────────────

👑 LUXURY OPTION (€750)
[Full itinerary...]
```

### Behind the Scenes (JSON)

- Stored as JSON for metrics/validation
- Enables programmatic checking of costs
- Proves all places are real (verified against KB)

---

## Evaluation & Metrics

### Live Demo (30-40 min presentation)

**Example Queries:**
1. "€500, Berlin→Paris, 5 days, romantic"
2. "€300, Amsterdam, 3 days, budget backpacker"
3. "€1000, Barcelona→Rome, 7 days, luxury"

**What to Show:**
- Real-time generation of 3 options
- Readable itinerary output
- All places are real + verified
- Costs are accurate

### Metrics Report (Slides)

| Metric | Target | Method |
|--------|--------|--------|
| Budget Accuracy | 100% stayed within budget | Parse JSON, check totalCost ≤ budget |
| Hallucination Rate | 0% invented places | Verify all place names exist in KB |
| Cost Estimation Error | ±5% | Compare generated costs vs real data |
| Multi-Option Generation | 3 options per query | Count options in output |
| Constraint Satisfaction | 100% valid | Programmatic validation |

### Before/After Comparison

**Old RAG:**
- Generic text answers
- Inaccurate/missing prices
- No structure
- Single option
- Hallucinated place names

**New RAG:**
- 3 structured options
- Validated budget
- Day-by-day breakdown
- Real places + accurate costs
- Trade-off explanations

---

## Implementation Plan (4 Days)

### Day 1: Data Gathering & Setup
- Download open-source datasets (transport, hotels, restaurants)
- Data cleaning & preprocessing (normalize prices, extract metadata)
- Load into ChromaDB
- **Deliverable**: Knowledge base ready (5-6 cities, ~50k records)

### Day 2: Retrieval & Generation
- Improve retrieval (metadata filtering + semantic search)
- Write structured prompt template
- Implement multi-option generation
- Test on 3-4 sample queries
- **Deliverable**: Generation pipeline working

### Day 3: Validation & Metrics
- Build constraint validation logic
- Implement metrics/evaluation script
- Polish prompt (reduce hallucination)
- Prepare 3 demo queries
- **Deliverable**: System stable, test cases pass

### Day 4: Presentation
- Final polish + live demo testing
- Create metrics report slides
- Before/after comparison visuals
- **Deliverable**: Working demo + presentation ready

---

## Technical Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Vector DB | ChromaDB | Existing; reuse setup |
| Embeddings | all-MiniLM-L6-v2 | Existing; keep it |
| LLM | Groq LLaMA 3.3 70B | Existing API |
| Data Processing | Pandas + Python | Standard stack |
| UI | Streamlit | Existing; may update |
| Output Validation | Python + JSON schema | New |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data gathering takes too long | Use Kaggle preloaded datasets, not scraping |
| LLM hallucination | Validation layer checks all place names exist |
| Budget constraint violations | Post-processing validates totalCost ≤ budget |
| Missing data for some queries | Output "insufficient data in KB for this query" |
| Tight timeline | Focus on 5-6 cities, not all possible cities |

---

## Success Criteria

✅ **System generates 3 structured options** per query  
✅ **All places are real** (verified against KB)  
✅ **Budget constraints enforced** (100% of options ≤ budget)  
✅ **Cost accuracy** (±5% of real data)  
✅ **Live demo works** (3 test cases presented)  
✅ **Metrics report proves improvement** (before/after comparison)  
✅ **Presentation tells the story** ("Generic RAG → Constraint-Aware RAG")  

---

## Approval Checklist

- [x] Architecture clear?
- [x] Data sources realistic?
- [x] Generation strategy addresses hallucination?
- [x] Output format presentation-ready?
- [x] Evaluation plan solid?
- [x] 4-day timeline realistic?
- [x] Prof. Reck's RAG requirements met?

**Status**: ✅ **APPROVED** (May 17, 2026)
