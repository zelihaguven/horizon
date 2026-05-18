"""
Generation Layer: Multi-option itinerary generation with Groq LLM
Creates Budget, Comfort, and Luxury variants with cost breakdowns
Integrated with prompt engineering for optimized output quality
"""

import json
import os
from typing import Dict, List, Optional
from groq import Groq
from simple_retriever import SimpleRetriever
from prompts import TravelPromptTemplates, PromptOptimizer
from dotenv import load_dotenv

load_dotenv()


class ConstraintAwareGenerator:
    """
    Generate multi-option itineraries using Groq LLaMA 3.3 70B.
    Creates 3 variants: Budget, Comfort, Luxury with constraint validation.
    """

    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize generator with Groq client and optimized prompts"""
        if groq_api_key is None:
            groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        self.retriever = SimpleRetriever()
        # Load optimized system prompt
        self.system_prompt = TravelPromptTemplates.get_groq_system_prompt()
        print(f"✓ Generator initialized with {self.model}")
        print(f"✓ Prompt engineering layer loaded (optimized for {self.model})")
        print(f"✓ Using SimpleRetriever (CSV-based, no external dependencies)")

    def generate_itinerary(
        self,
        destination: str,
        duration_days: int,
        budget_eur: float,
        preferences: Optional[List[str]] = None,
        travelers: int = 1
    ) -> Dict:
        """
        Generate multi-option itinerary respecting constraints.

        Args:
            destination: City or region (e.g., "Paris", "Berlin")
            duration_days: Trip length in days
            budget_eur: Total budget in EUR
            preferences: Activities/interests (e.g., ["museums", "food", "nightlife"])
            travelers: Number of travelers (for cost breakdown)

        Returns:
            Dict with budget/comfort/luxury itinerary variants
        """
        print(f"\n[Generating] {duration_days}-day trip to {destination} (€{budget_eur})")

        # Step 1: Retrieve relevant options
        print(f"  • Retrieving travel options...")
        retrieved_options = self._retrieve_options(destination, preferences)

        # Step 2: Generate variants
        print(f"  • Generating itinerary variants...")
        variants = self._generate_variants(
            destination=destination,
            duration_days=duration_days,
            budget_eur=budget_eur,
            travelers=travelers,
            preferences=preferences or [],
            retrieved_options=retrieved_options
        )

        # Step 3: Validate constraints
        print(f"  • Validating constraints...")
        variants = self._validate_constraints(variants, budget_eur, duration_days)

        result = {
            "request": {
                "destination": destination,
                "duration_days": duration_days,
                "budget_eur": budget_eur,
                "travelers": travelers,
                "preferences": preferences or []
            },
            "variants": variants,
            "status": "generated"
        }

        return result

    def _retrieve_options(
        self,
        destination: str,
        preferences: Optional[List[str]] = None
    ) -> Dict:
        """Retrieve hotels, restaurants, activities, transport for destination"""
        preferences = preferences or []
        pref_str = " ".join(preferences) if preferences else "travel"

        retrieved = {
            "hotels": self.retriever.retrieve_by_category(
                query=f"hotels in {destination} {pref_str}",
                category="hotel",
                city=destination,
                k=5
            ),
            "restaurants": self.retriever.retrieve_by_category(
                query=f"restaurants dining in {destination} {pref_str}",
                category="restaurant",
                city=destination,
                k=5
            ),
            "activities": self.retriever.retrieve_by_category(
                query=f"things to do attractions {pref_str} in {destination}",
                category="activity",
                city=destination,
                k=8
            ),
            "transport": self.retriever.retrieve(
                query=f"travel transport flights trains buses",
                k=5
            )
        }

        return retrieved

    def _generate_variants(
        self,
        destination: str,
        duration_days: int,
        budget_eur: float,
        travelers: int,
        preferences: List[str],
        retrieved_options: Dict
    ) -> List[Dict]:
        """Generate Budget, Comfort, Luxury variants using LLM with optimized prompts"""

        # Format retrieved options for context
        options_context = self._format_options_context(retrieved_options)

        # Use optimized prompt from prompt engineering layer
        prompt = TravelPromptTemplates.get_itinerary_generation_prompt(
            destination=destination,
            duration_days=duration_days,
            budget_eur=budget_eur,
            travelers=travelers,
            preferences=preferences,
            retrieved_options=options_context
        )

        # Add chain-of-thought reasoning for better constraint handling
        prompt = PromptOptimizer.add_reasoning_chain(prompt, include_cot=True)

        try:
            # Call Groq with system prompt and optimized user prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                top_p=0.9
            )

            response_text = response.choices[0].message.content

            # Parse JSON response
            # Find JSON array in response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                variants = json.loads(json_str)
                return variants if isinstance(variants, list) else [variants]
            else:
                # Fallback: return empty structure
                print(f"  ⚠ Could not parse JSON from response. Using fallback variants.")
                return self._create_fallback_variants(destination, budget_eur, duration_days)

        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parsing error: {e}")
            return self._create_fallback_variants(destination, budget_eur, duration_days)
        except Exception as e:
            print(f"  ⚠ Generation error: {e}")
            return self._create_fallback_variants(destination, budget_eur, duration_days)

    def _format_options_context(self, retrieved_options: Dict) -> str:
        """Format retrieved options for LLM context"""
        lines = []

        if retrieved_options.get("hotels"):
            lines.append("HOTELS:")
            for h in retrieved_options["hotels"][:3]:
                meta = h.get("metadata", {})
                lines.append(f"  - {meta.get('name')}: €{meta.get('price_eur')}/night ({meta.get('price_range')})")

        if retrieved_options.get("restaurants"):
            lines.append("\nRESTAURANTS:")
            for r in retrieved_options["restaurants"][:3]:
                meta = r.get("metadata", {})
                lines.append(f"  - {meta.get('name')}: €{meta.get('price_eur')} ({meta.get('price_range')})")

        if retrieved_options.get("activities"):
            lines.append("\nACTIVITIES:")
            for a in retrieved_options["activities"][:4]:
                meta = a.get("metadata", {})
                lines.append(f"  - {meta.get('name')}: €{meta.get('price_eur')}")

        return "\n".join(lines) if lines else "[Limited data - using baseline costs]"

    def _create_fallback_variants(
        self,
        destination: str,
        budget_eur: float,
        duration_days: int
    ) -> List[Dict]:
        """Create baseline itineraries if LLM fails"""
        return [
            {
                "name": "Budget",
                "cost_breakdown": {
                    "accommodation_total": budget_eur * 0.4,
                    "meals_total": budget_eur * 0.4,
                    "activities_total": budget_eur * 0.15,
                    "transport_total": budget_eur * 0.05,
                    "total_eur": budget_eur,
                    "per_person_eur": budget_eur
                },
                "highlights": ["City walking tours", "Local markets", "Street food"],
                "notes": "Budget-focused with emphasis on free/low-cost attractions"
            },
            {
                "name": "Comfort",
                "cost_breakdown": {
                    "accommodation_total": budget_eur * 0.35,
                    "meals_total": budget_eur * 0.35,
                    "activities_total": budget_eur * 0.25,
                    "transport_total": budget_eur * 0.05,
                    "total_eur": budget_eur,
                    "per_person_eur": budget_eur
                },
                "highlights": ["Mixed hotels and hostels", "Diverse dining", "Major attractions"],
                "notes": "Balanced experience with good value for money"
            },
            {
                "name": "Luxury",
                "cost_breakdown": {
                    "accommodation_total": budget_eur * 0.4,
                    "meals_total": budget_eur * 0.4,
                    "activities_total": budget_eur * 0.15,
                    "transport_total": budget_eur * 0.05,
                    "total_eur": budget_eur,
                    "per_person_eur": budget_eur
                },
                "highlights": ["Premium hotels", "Michelin dining", "Exclusive tours"],
                "notes": "Luxury experience focusing on premium accommodations and dining"
            }
        ]

    def _validate_constraints(
        self,
        variants: List[Dict],
        budget_eur: float,
        duration_days: int
    ) -> List[Dict]:
        """Validate and fix budget overages"""
        validated = []

        for variant in variants:
            # Check if cost breakdown exists
            if "cost_breakdown" in variant:
                total = variant["cost_breakdown"].get("total_eur", 0)
                if total > budget_eur:
                    # Scale down proportionally
                    scale = budget_eur / total if total > 0 else 1
                    for key in ["accommodation_total", "meals_total", "activities_total", "transport_total"]:
                        variant["cost_breakdown"][key] = variant["cost_breakdown"].get(key, 0) * scale
                    variant["cost_breakdown"]["total_eur"] = budget_eur
                    variant["cost_breakdown"]["per_person_eur"] = budget_eur
                    variant["notes"] = (variant.get("notes", "") + " [Adjusted to match budget]").strip()

            validated.append(variant)

        return validated


def test_generator():
    """Test generation with sample request"""
    print("\n" + "="*60)
    print("TEST: Generation Layer")
    print("="*60)

    generator = ConstraintAwareGenerator()

    # Generate sample itinerary
    result = generator.generate_itinerary(
        destination="Paris",
        duration_days=3,
        budget_eur=900,
        preferences=["museums", "food", "walks"],
        travelers=2
    )

    print("\n✅ Itinerary generated!")
    print(f"\nVariants created: {len(result['variants'])}")
    for v in result["variants"]:
        if isinstance(v, dict) and "name" in v:
            name = v.get("name", "Unknown")
            cost = v.get("cost_breakdown", {}).get("total_eur", "N/A")
            print(f"  • {name}: €{cost}")

    print("\n✅ Generation layer operational!")
    print("="*60 + "\n")

    return result


if __name__ == "__main__":
    result = test_generator()
    print("\nFull result structure:")
    print(json.dumps(result, indent=2, default=str)[:500] + "...")
