# Day 3: Quick Start Guide

## 5-Minute Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
# (Includes google-generativeai for Gemini support)
```

### 2. Verify existing .env
```bash
cat .env
# Should have: GROQ_API_KEY="..."
```

### 3. (Optional) Add Gemini API key
```bash
echo 'GOOGLE_API_KEY="your-key-here"' >> .env
```

### 4. Run demo
```bash
# With Groq (no setup needed)
python main.py

# With Gemini (if API key added)
python main.py --gemini
```

---

## Three Key Features

### 🤖 Recommendation Model
Automatically ranks Budget/Comfort/Luxury variants by user fit

```python
from recommendation_model import VariantRecommender

recommender = VariantRecommender()
ranked = recommender.rank_variants(
    variants=[budget, comfort, luxury],
    preferences=["beaches", "art"],
    budget=3000,
    travelers=2
)

# Returns variants with:
# - recommendation_score (0-100)
# - recommendation_label ("⭐ BEST FOR YOU", etc)
# - detailed_scores (budget_fit, activity_fit, etc)
```

### 🚀 Gemini with Context Caching
Switch to Google Gemini for longer context & cheaper tokens

```python
from generator_gemini import ConstraintAwareGeneratorGemini

gen = ConstraintAwareGeneratorGemini()
result = gen.generate_itinerary(
    destination="Barcelona",
    duration_days=5,
    budget_eur=3000,
    preferences=["beaches", "art"],
    travelers=2
)

# Get cache stats
stats = gen.get_cache_statistics()
# {
#   'total_input_tokens': 1200,
#   'cached_tokens': 480,
#   'cache_efficiency': '40.0%'
# }
```

### ✅ Validation Layer
Detects hallucinations & enforces constraints

```python
from validator import TravelItineraryValidator

validator = TravelItineraryValidator()
report = validator.validate_itinerary(
    itinerary=result,
    max_budget_eur=3000,
    duration_days=5
)

# Returns:
# {
#   'status': 'VALID|WARNING|INVALID',
#   'quality_score': 95,
#   'critical_issues': 0,
#   'issues': [...],
#   'hallucinations_found': [...]
# }
```

---

## Usage Patterns

### Pattern 1: Full Pipeline (Recommended)
```python
from main import TravelRAG

rag = TravelRAG(use_gemini=False)  # True if Gemini key available

result = rag.plan_trip(
    destination="Paris",
    duration_days=3,
    budget_eur=600,
    preferences=["museums", "food"],
    travelers=1,
    validate=True,        # ✓ Enable validation
    rank_variants=True    # ✓ Enable recommendations
)

# Result includes:
# - variants (ranked by recommendation_score)
# - recommendation_summary (best variant + reasoning)
# - validation (quality_score + issues)

rag.print_itinerary(result)  # Pretty-print with all metrics
rag.save_itinerary(result, "my_trip.json")
```

### Pattern 2: Just Validation
```python
from generator import ConstraintAwareGenerator
from validator import TravelItineraryValidator

gen = ConstraintAwareGenerator()
validator = TravelItineraryValidator()

result = gen.generate_itinerary(...)
report = validator.validate_itinerary(result, max_budget_eur=3000, duration_days=5)

print(f"Quality: {report['quality_score']}/100")
print(f"Status: {report['status']}")
for issue in report['issues']:
    print(f"  - {issue['message']}")
```

### Pattern 3: Just Recommendations
```python
from generator import ConstraintAwareGenerator
from recommendation_model import VariantRecommender

gen = ConstraintAwareGenerator()
recommender = VariantRecommender()

result = gen.generate_itinerary(...)
ranked = recommender.rank_variants(
    variants=result['variants'],
    preferences=["beaches"],
    budget=3000
)

best = ranked[0]
print(f"Best for you: {best['name']} (Score: {best['recommendation_score']:.1f}/100)")
```

### Pattern 4: Gemini with Caching
```python
from generator_gemini import ConstraintAwareGeneratorGemini

gen = ConstraintAwareGeneratorGemini()
result = gen.generate_itinerary(...)

# Show cache performance
stats = gen.get_cache_statistics()
print(f"Cached: {stats['cached_tokens']} tokens")
print(f"New: {stats['new_tokens']} tokens")
print(f"Efficiency: {stats['cache_efficiency']}")
```

---

## Output Examples

### Recommendation Score in Output
```json
{
  "name": "Comfort",
  "recommendation_score": 92.3,
  "recommendation_label": "⭐ BEST FOR YOU",
  "recommendation_confidence": 95.0,
  "detailed_scores": {
    "budget_fit": 85.0,
    "activity_fit": 100.0,
    "user_profile_fit": 100.0,
    "value_score": 75.0,
    "overall_score": 92.3
  },
  ...
}
```

### Validation Report in Output
```json
{
  "validation": {
    "status": "VALID",
    "quality_score": 95,
    "total_issues": 2,
    "critical_issues": 0,
    "warnings": 2,
    "issues": [
      {
        "level": "warning",
        "component": "daily_costs",
        "message": "Day 2 exceeds daily budget by €15",
        "severity": 40.0
      }
    ],
    "hallucinations_found": [],
    "summary": "✓ VALID ITINERARY - Quality: 95/100"
  }
}
```

---

## Environment Variables

### Required
```bash
GROQ_API_KEY="gsk_..."  # For Groq (default)
```

### Optional
```bash
GOOGLE_API_KEY="AI..."  # For Gemini support
```

### Check your .env
```bash
cat /Users/ilginguven/Desktop/RAG-PROJECT/.env
# Should show both keys
```

---

## Common Questions

### Q: Which should I use, Groq or Gemini?
**A:** Start with Groq (default, no setup needed). Use Gemini if you need:
- Longer context for complex requests
- Context caching for multiple requests
- Lower token costs at scale

### Q: What if validation finds issues?
**A:** Check the `issues` array:
- `critical` = Budget exceeded or duration mismatch (regenerate)
- `warning` = Minor cost discrepancies (usually fine)
- `info` = Suggestions (can ignore)

### Q: What's a good quality_score?
**A:**
- 90+ = Excellent, ready to use
- 75-89 = Good, minor notes
- 60-74 = Acceptable, review carefully
- <60 = Problematic, regenerate

### Q: How does recommendation scoring work?
**A:** Weighted formula:
```
Score = (
  budget_fit * 25% +
  activity_fit * 30% +
  user_profile_fit * 30% +
  value_score * 15%
)
```

### Q: Can I use just one component?
**A:** Yes! Each is independent:
```python
# Just recommendation
recommender.rank_variants(...)

# Just validation
validator.validate_itinerary(...)

# Just Gemini
gen = ConstraintAwareGeneratorGemini()
```

---

## File Changes Summary

**New Files:**
- `generator_gemini.py` - Gemini with caching
- `recommendation_model.py` - Variant ranking
- `validator.py` - Validation layer
- `DAY3_ENHANCEMENTS.md` - Full documentation

**Modified Files:**
- `main.py` - Integrated all 3 components
- `requirements.txt` - Added google-generativeai

---

## Next: Day 4

Day 3 ✅ Complete
- ✓ Gemini integration
- ✓ Recommendation model
- ✓ Validation layer

Day 4 (Next):
- Web UI (Flask/Streamlit)
- PDF export
- Email integration
- Analytics dashboard

---

## Support

### Test Individual Components
```bash
# Test recommendation model
python recommendation_model.py

# Test validation
python validator.py

# Test Gemini (if configured)
python generator_gemini.py
```

### Run Full Demo
```bash
# With Groq (default)
python main.py

# With Gemini (if key available)
python main.py --gemini
```

### Debug Issues
```python
# Enable detailed output
import logging
logging.basicConfig(level=logging.DEBUG)

# Run generation
rag = TravelRAG(use_gemini=True)
result = rag.plan_trip(...)
```

---

**You now have production-grade travel itinerary generation! 🚀**
