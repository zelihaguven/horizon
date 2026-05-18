"""
Prompt Engineering Layer: Optimized prompts for Groq and Gemini generators
Includes system prompts, few-shot examples, and constraint guidance for better itinerary generation
"""

from typing import Dict, List, Optional


class TravelPromptTemplates:
    """
    Centralized prompt templates for travel itinerary generation.
    Optimized for both Groq (8K context) and Gemini (1M context).
    """

    @staticmethod
    def get_groq_system_prompt() -> str:
        """System prompt optimized for Groq LLaMA 3.3 70B (8K context window)"""
        return """You are an expert travel itinerary planner with deep knowledge of destinations worldwide.

YOUR CORE TASK:
Generate 3 distinct itinerary variants (Budget, Comfort, Luxury) that strictly respect all constraints.

KEY RESPONSIBILITIES:
1. Create realistic, practical itineraries matching the exact duration
2. Ensure costs NEVER exceed the specified budget per person
3. Match recommended activities to stated user preferences
4. Provide specific venue/restaurant/activity names (not generic recommendations)
5. Include realistic pricing based on market data
6. Distribute daily costs evenly to avoid budget overruns
7. Ensure each variant has a distinct experience level

BUDGET ALLOCATION STRATEGY:
- Budget variant: 45% accommodation, 35% meals, 15% activities, 5% transport
- Comfort variant: 35% accommodation, 30% meals, 30% activities, 5% transport
- Luxury variant: 40% accommodation, 35% meals, 20% activities, 5% transport

VARIANT CHARACTERISTICS:
Budget: Hostels/budget hotels (€30-60/night), street food/local markets, free/walking tours, public transport
Comfort: 3-star hotels (€70-120/night), good restaurants, paid tours, metro passes
Luxury: 5-star hotels (€150-300+/night), Michelin/high-end dining, private guides, premium experiences

HARD CONSTRAINTS (NON-NEGOTIABLE):
- Total cost per person = (total budget) / (number of travelers)
- Sum of all line items must equal stated budget
- Daily costs must be feasible (realistically achievable)
- Activities must be appropriate for the duration and location
- No hallucinated venues - use only plausible, well-known locations

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no explanation text)
- Use exact JSON structure provided
- All monetary values in EUR (€)
- All day numbers starting from 1
- Ensure mathematical consistency across all totals"""

    @staticmethod
    def get_gemini_system_prompt() -> str:
        """System prompt optimized for Gemini 1.5 Pro (1M context window)"""
        return """You are an elite travel experience designer with expertise in constraint-aware itinerary planning.

Your mission: Create 3 perfectly-tailored itinerary variants that balance experience quality with strict budget adherence.

CORE COMPETENCIES:
1. Destination expertise: Geography, logistics, costs, peak seasons
2. Constraint engineering: Impossible budgets → creative solutions
3. Personalization: Match activities precisely to traveler profiles
4. Cost optimization: Maximum value within budget ceiling
5. Experience design: Each variant tells a distinct story

DEEP REASONING APPROACH:
Before generating each variant:
- Analyze the destination's cost structure (accommodation, food, transport)
- Identify the traveler's implicit preferences and travel style
- Map activities to budget constraints
- Find hidden gems that maximize value
- Create narrative arcs for each day (rest → explore → relax)

VARIANT DESIGN PHILOSOPHY:
Budget: "Smart travel" - locals' experience, authentic culture, minimal luxury, maximum exploration
Comfort: "Balanced journey" - mix of comfort and exploration, good dining, major attractions covered
Luxury: "Curated excellence" - premium everything, insider experiences, personalized service, no compromises

PRICING GUARDRAILS:
- Verify each line item is realistic for the destination and date
- Build in 10% buffer for unexpected costs
- Ensure daily cash is manageable (€20-100 per person typical)
- Account for currency fluctuations and local economic factors

CONSTRAINT ENFORCEMENT:
- Total cost per person = Total budget / Number of travelers
- No line item may exceed this per-person daily average by 30%
- Activities must be sequential and logistically feasible
- Include realistic travel times between locations

QUALITY MARKERS:
- Specific venue names (not generic categories)
- Realistic opening hours and operational considerations
- Seasonal appropriateness
- Weather-appropriate suggestions
- Cultural sensitivity in activity recommendations

OUTPUT STANDARD:
- Perfect JSON, no extra text
- All values mathematically consistent
- All assumptions stated in "notes" field
- Confidence indicators in variant names if uncertain"""

    @staticmethod
    def get_itinerary_generation_prompt(
        destination: str,
        duration_days: int,
        budget_eur: float,
        travelers: int,
        preferences: List[str],
        retrieved_options: str
    ) -> str:
        """
        Main prompt for itinerary generation.
        Adapted for Groq's 8K context limit.
        """
        preferences_str = ", ".join(preferences) if preferences else "general tourism"
        budget_per_person = budget_eur / travelers if travelers > 0 else budget_eur

        return f"""Generate 3 distinct itinerary variants for {destination}.

REQUEST PARAMETERS:
- Destination: {destination}
- Duration: {duration_days} days
- Total Budget: €{budget_eur}
- Travelers: {travelers}
- Budget per person: €{budget_per_person:.2f}
- Preferences: {preferences_str}

AVAILABLE LOCAL OPTIONS:
{retrieved_options}

GENERATION REQUIREMENTS:

For EACH of the 3 variants (Budget, Comfort, Luxury), create a JSON object with:
{{
  "name": "Budget|Comfort|Luxury",
  "daily_budget_eur": <€{budget_per_person:.2f}>,
  "accommodation": {{
    "name": "<specific hotel/hostel name or type>",
    "price_per_night_eur": <number>,
    "nights": {duration_days - 1},
    "total_eur": <number>
  }},
  "meals": {{
    "breakfast_lunch_dinner_per_day_eur": <number>,
    "total_eur": <number>
  }},
  "activities": [
    {{"name": "<activity>", "cost_eur": <number>, "day": <1-{duration_days}>}},
    ...
  ],
  "transport": {{
    "description": "<specific transport type: metro, bike, walking, etc>",
    "cost_eur": <number>
  }},
  "daily_itinerary": [
    {{"day": 1, "activities": ["<morning>", "<afternoon>", "<evening>"], "estimated_cost_eur": <number>}},
    ...
  ],
  "cost_breakdown": {{
    "accommodation_total": <€ {(budget_per_person * 0.35):.2f}>,
    "meals_total": <€ {(budget_per_person * 0.35):.2f}>,
    "activities_total": <€ {(budget_per_person * 0.25):.2f}>,
    "transport_total": <€ {(budget_per_person * 0.05):.2f}>,
    "total_eur": {budget_per_person},
    "per_person_eur": {budget_per_person}
  }},
  "highlights": ["<key attraction 1>", "<key attraction 2>", ...],
  "notes": "<summary of trade-offs, special tips, or unique features>"
}}

CRITICAL RULES:
1. BUDGET ADHERENCE: total_eur must equal €{budget_eur} exactly (for {travelers} travelers)
2. DAILY DISTRIBUTION: Each day's estimated_cost_eur must be near €{budget_per_person:.2f}
3. MATH CONSISTENCY: Sum of accommodation + meals + activities + transport = total_eur
4. REALISM: All venue names must be real or plausibly realistic for {destination}
5. SEQUENCING: Activities should follow a logical geographic/temporal pattern
6. DURATION: Must include exactly {duration_days} days of activities

PREFERENCE MATCHING:
{f'- Prioritize: {preferences_str}' if preferences else '- General tourism: major attractions and cultural sites'}
- Avoid activities that don't match user interests
- Suggest alternatives if preferences are niche

VARIANT DISTINCTION:
- Budget: €{budget_per_person * 0.9:.2f} or less (find value), hostels/budget hotels, local food
- Comfort: €{budget_per_person:.2f}, 3-star hotels, nice restaurants, popular attractions
- Luxury: €{budget_per_person:.2f}, premium hotels, fine dining, exclusive experiences

Return ONLY the JSON array with 3 variants. NO markdown, NO explanation, NO additional text.
Start with [ and end with ]."""

    @staticmethod
    def get_gemini_itinerary_prompt(
        destination: str,
        duration_days: int,
        budget_eur: float,
        travelers: int,
        preferences: List[str],
        retrieved_options: str
    ) -> str:
        """
        Main prompt for Gemini itinerary generation.
        Optimized for 1M context window with deeper reasoning.
        """
        preferences_str = ", ".join(preferences) if preferences else "general tourism, cultural sites"
        budget_per_person = budget_eur / travelers if travelers > 0 else budget_eur

        return f"""You are designing a {duration_days}-day journey to {destination}.

TRAVELER PROFILE:
- Destination: {destination}
- Days available: {duration_days}
- Total budget: €{budget_eur} (€{budget_per_person:.2f} per person)
- Party size: {travelers} traveler(s)
- Interests: {preferences_str}

LOCAL MARKET DATA:
{retrieved_options}

DESIGN PROCESS:
1. Analyze {destination}'s cost structure and logistics
2. Map 3 distinct experience levels within the budget
3. Ensure each variant has unique character and value proposition
4. Verify daily costs are sustainable (not front-loading, not back-loading)
5. Match activities to preferences and destination strengths

EACH VARIANT MUST INCLUDE:
{{
  "name": "Budget|Comfort|Luxury",
  "daily_budget_eur": {budget_per_person},
  "accommodation": {{
    "name": "<specific venue>",
    "price_per_night_eur": <number>,
    "nights": {duration_days - 1},
    "total_eur": <number>
  }},
  "meals": {{
    "breakfast_lunch_dinner_per_day_eur": <number>,
    "total_eur": <number>
  }},
  "activities": [
    {{"name": "<activity>", "cost_eur": <number>, "day": <1-{duration_days}>}},
    ...
  ],
  "transport": {{
    "description": "<method>",
    "cost_eur": <number>
  }},
  "daily_itinerary": [
    {{"day": 1, "activities": ["<morning activity>", "<afternoon activity>", "<evening activity>"], "estimated_cost_eur": {budget_per_person}}},
    ...
  ],
  "cost_breakdown": {{
    "accommodation_total": <number>,
    "meals_total": <number>,
    "activities_total": <number>,
    "transport_total": <number>,
    "total_eur": {budget_eur},
    "per_person_eur": {budget_per_person}
  }},
  "highlights": ["<attraction>", ...],
  "notes": "<why choose this variant>"
}}

VARIANT STRATEGY:
Budget (€{budget_per_person:.2f}): Maximize experiences within minimal spend
  - Accommodation: Hostels, budget hotels (€30-60/night)
  - Food: Street food, local markets, casual eateries (€8-15/meal)
  - Activities: Free walks, museums on free days, hiking, local neighborhoods
  - Transport: Public transit, walking, shared transport

Comfort (€{budget_per_person:.2f}): Balance comfort with exploration
  - Accommodation: 3-star hotels, nice guesthouses (€70-120/night)
  - Food: Good local restaurants, some upscale dining (€15-25/meal)
  - Activities: Guided tours, main attractions, experiences (€20-50/activity)
  - Transport: Metro passes, occasional taxis, organized transport

Luxury (€{budget_per_person:.2f}): Premium experience throughout
  - Accommodation: 5-star hotels, luxury resorts (€150-300+/night)
  - Food: Michelin restaurants, fine dining (€40+/meal)
  - Activities: Private guides, exclusive tours, VIP experiences
  - Transport: Uber/taxis, airport transfers, premium services

QUALITY STANDARDS:
✓ Each activity is specific (not "visit museums" but "Prado Museum")
✓ Daily costs are realistic and achievable
✓ Activities are geographically sensible (no impossible logistics)
✓ Each variant has a distinct narrative and value proposition
✓ All costs are consistent with {destination} market rates
✓ Preferences guide activity selection but don't limit discovery
✓ Seasonal considerations are noted
✓ Cultural sensitivity is maintained

COST VALIDATION:
- Accommodation: {{accommodation.total_eur}} = {{accommodation.price_per_night_eur}} × {{accommodation.nights}}
- Meals: {{meals.total_eur}} = {{meals.breakfast_lunch_dinner_per_day_eur}} × {duration_days}
- Activities: Sum of all activity.cost_eur must be reasonable
- Transport: {{transport.cost_eur}} must be realistic for {duration_days} days in {destination}
- TOTAL: {{cost_breakdown.total_eur}} must equal €{budget_eur}
- PER PERSON: {{cost_breakdown.per_person_eur}} must equal €{budget_per_person:.2f}

Return a JSON array with exactly 3 variant objects. No markdown, no explanations, no extra text.
Only valid JSON starting with [ and ending with ]."""

    @staticmethod
    def get_few_shot_examples() -> List[Dict]:
        """Few-shot examples for prompt enhancement"""
        return [
            {
                "destination": "Barcelona",
                "duration_days": 3,
                "budget_eur": 600,
                "travelers": 2,
                "preferences": ["architecture", "food", "beaches"],
                "example_budget_variant": {
                    "name": "Budget",
                    "accommodation": {
                        "name": "Casa Granda Hostel",
                        "price_per_night_eur": 45,
                        "nights": 2,
                        "total_eur": 90
                    },
                    "meals": {
                        "breakfast_lunch_dinner_per_day_eur": 25,
                        "total_eur": 75
                    },
                    "activities": [
                        {"name": "Park Güell (free walk)", "cost_eur": 0, "day": 1},
                        {"name": "Sagrada Familia", "cost_eur": 26, "day": 1},
                        {"name": "Barceloneta Beach", "cost_eur": 0, "day": 2},
                        {"name": "Gothic Quarter walking tour", "cost_eur": 15, "day": 2},
                        {"name": "La Boqueria Market", "cost_eur": 0, "day": 3}
                    ],
                    "cost_breakdown": {
                        "accommodation_total": 90,
                        "meals_total": 75,
                        "activities_total": 41,
                        "transport_total": 24,
                        "total_eur": 300,
                        "per_person_eur": 150
                    }
                }
            },
            {
                "destination": "Berlin",
                "duration_days": 4,
                "budget_eur": 800,
                "travelers": 1,
                "preferences": ["history", "museums", "nightlife"],
                "example_comfort_variant": {
                    "name": "Comfort",
                    "accommodation": {
                        "name": "Hotel Altberlin",
                        "price_per_night_eur": 85,
                        "nights": 3,
                        "total_eur": 255
                    },
                    "meals": {
                        "breakfast_lunch_dinner_per_day_eur": 30,
                        "total_eur": 120
                    },
                    "activities": [
                        {"name": "German History Museum", "cost_eur": 12, "day": 1},
                        {"name": "Memorial to the Murdered Jews", "cost_eur": 0, "day": 1},
                        {"name": "East Side Gallery", "cost_eur": 0, "day": 2},
                        {"name": "Checkpoint Charlie", "cost_eur": 15, "day": 2},
                        {"name": "Pergamon Museum", "cost_eur": 12, "day": 3}
                    ],
                    "cost_breakdown": {
                        "accommodation_total": 255,
                        "meals_total": 120,
                        "activities_total": 88,
                        "transport_total": 37,
                        "total_eur": 500,
                        "per_person_eur": 500
                    }
                }
            }
        ]

    @staticmethod
    def get_constraint_guidance() -> str:
        """Guidance for constraint handling in prompt"""
        return """CONSTRAINT HANDLING GUIDE:

When budget is very tight:
- Prioritize accommodation over activities (sleep is essential)
- Focus on free activities: walking tours, parks, beach time
- Choose areas with cheap food (markets, street vendors)
- Use public transport exclusively

When budget is comfortable:
- Mix 3-star accommodation with nice restaurants
- Include 2-3 paid activities/tours
- Add buffer for spontaneous experiences

When budget is generous:
- Maximize quality of experiences (hotels, restaurants, tours)
- Include unique/premium experiences (spa, helicopter, exclusive dining)
- Reduce time pressure (slower pace)

Geographic constraints:
- Consider distances between attractions
- Factor realistic travel times
- Group activities by area

Seasonal constraints:
- Note if season affects pricing
- Mention weather/closure considerations
- Suggest best times for outdoor activities"""

    @staticmethod
    def get_quality_validation_prompt() -> str:
        """Prompt for self-validation before returning"""
        return """BEFORE RETURNING YOUR RESPONSE, VALIDATE:

Budget Mathematics:
☐ accommodation_total + meals_total + activities_total + transport_total = total_eur
☐ total_eur = stated budget for all travelers
☐ per_person_eur = total_eur / travelers
☐ daily_itinerary costs sum close to daily budget

Realism Check:
☐ All venue names are real or plausibly realistic
☐ Prices match typical ranges for the destination
☐ Activities are actually available in the destination
☐ Daily schedules are physically feasible
☐ No impossible logistics (e.g., two activities 50km apart in same slot)

Variant Quality:
☐ Budget variant is actually cheaper than Comfort
☐ Luxury variant is genuinely more premium
☐ All 3 variants respect the total budget
☐ Variants are distinct (not just different accommodation prices)

Data Consistency:
☐ accommodation.total_eur = accommodation.price_per_night_eur × accommodation.nights
☐ meals.total_eur = meals.breakfast_lunch_dinner_per_day_eur × duration_days
☐ All day numbers are between 1 and duration_days
☐ Activity costs are reasonable for destination

User Preference Matching:
☐ Recommended activities align with stated preferences
☐ Activities are varied and interesting
☐ Each day has a mix of activity types
☐ "Notes" explain how variant matches preferences

If any check fails, correct the variant before returning."""


class PromptOptimizer:
    """Helper class for prompt optimization and variant selection"""

    @staticmethod
    def select_prompt_variant(
        is_gemini: bool,
        destination: str,
        duration_days: int,
        budget_eur: float,
        travelers: int,
        preferences: List[str],
        retrieved_options: str
    ) -> str:
        """
        Select appropriate prompt variant based on LLM and parameters.
        """
        if is_gemini:
            return TravelPromptTemplates.get_gemini_itinerary_prompt(
                destination=destination,
                duration_days=duration_days,
                budget_eur=budget_eur,
                travelers=travelers,
                preferences=preferences,
                retrieved_options=retrieved_options
            )
        else:
            return TravelPromptTemplates.get_itinerary_generation_prompt(
                destination=destination,
                duration_days=duration_days,
                budget_eur=budget_eur,
                travelers=travelers,
                preferences=preferences,
                retrieved_options=retrieved_options
            )

    @staticmethod
    def get_system_prompt(is_gemini: bool) -> str:
        """Get system prompt optimized for the target LLM."""
        if is_gemini:
            return TravelPromptTemplates.get_gemini_system_prompt()
        else:
            return TravelPromptTemplates.get_groq_system_prompt()

    @staticmethod
    def add_reasoning_chain(base_prompt: str, include_cot: bool = True) -> str:
        """
        Optionally add chain-of-thought reasoning to prompt.
        Helps LLM think through complex constraints.
        """
        if not include_cot:
            return base_prompt

        cot_instruction = """

REASONING APPROACH (Think step-by-step):
1. First, calculate the daily budget: total_budget / duration_days = daily_budget
2. Allocate accommodation: daily_budget × 0.35 (or variant-specific %)
3. Allocate meals: daily_budget × 0.30-0.35
4. Allocate activities: daily_budget × 0.15-0.25
5. Allocate transport: daily_budget × 0.05
6. Verify: Sum of all allocations = daily_budget
7. Create daily itineraries that respect these allocations
8. List specific activities with exact costs
9. Double-check total = stated budget

THINK ALOUD about trade-offs:
- "For budget variant: use hostels (€40/night) to save €X for activities"
- "Comfort variant trades €Y for better accommodation, reducing activities budget slightly"
- "Luxury variant focuses on premium experiences because budget allows"

This reasoning helps ensure mathematical consistency."""

        return base_prompt + cot_instruction


def test_prompts():
    """Test prompt generation"""
    print("=" * 60)
    print("PROMPT ENGINEERING LAYER - TEST")
    print("=" * 60)

    # Test Groq system prompt
    groq_sys = TravelPromptTemplates.get_groq_system_prompt()
    print(f"\n✓ Groq system prompt: {len(groq_sys)} chars")

    # Test Gemini system prompt
    gemini_sys = TravelPromptTemplates.get_gemini_system_prompt()
    print(f"✓ Gemini system prompt: {len(gemini_sys)} chars")

    # Test itinerary prompt generation
    sample_options = "Hotels: 5-star €200/night, 3-star €80/night, Budget €40/night\nRestaurants: Michelin €80, Nice €30, Street food €10"
    groq_prompt = TravelPromptTemplates.get_itinerary_generation_prompt(
        destination="Paris",
        duration_days=3,
        budget_eur=900,
        travelers=2,
        preferences=["museums", "food"],
        retrieved_options=sample_options
    )
    print(f"✓ Groq itinerary prompt: {len(groq_prompt)} chars")

    gemini_prompt = TravelPromptTemplates.get_gemini_itinerary_prompt(
        destination="Paris",
        duration_days=3,
        budget_eur=900,
        travelers=2,
        preferences=["museums", "food"],
        retrieved_options=sample_options
    )
    print(f"✓ Gemini itinerary prompt: {len(gemini_prompt)} chars")

    # Test few-shot examples
    examples = TravelPromptTemplates.get_few_shot_examples()
    print(f"✓ Few-shot examples: {len(examples)} examples")

    # Test optimizer
    selected = PromptOptimizer.select_prompt_variant(
        is_gemini=False,
        destination="Berlin",
        duration_days=4,
        budget_eur=800,
        travelers=1,
        preferences=["history"],
        retrieved_options=sample_options
    )
    print(f"✓ PromptOptimizer works: {len(selected)} chars")

    print("\n" + "=" * 60)
    print("✅ Prompt engineering layer ready!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_prompts()
