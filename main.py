"""
Main Orchestration: Constraint-Aware Travel RAG System (Enhanced Day 3)
Now includes: Gemini support + context caching + recommendations + validation
"""

import json
import os
from typing import Dict, List, Optional
from generator import ConstraintAwareGenerator
from retriever import TravelRetriever
from recommendation_model import VariantRecommender
from validator import TravelItineraryValidator

# Try to import Gemini generator (optional)
try:
    from generator_gemini import ConstraintAwareGeneratorGemini
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class TravelRAG:
    """
    Complete Constraint-Aware RAG system for travel itinerary generation.

    Architecture (Day 3 Enhanced):
    - Data Layer: ChromaDB with hotel/restaurant/activity/transport metadata
    - Retrieval Layer: Semantic search + metadata filtering
    - Generation Layer: LLM (Groq OR Gemini with context caching)
    - Recommendation Layer: ML-based variant ranking by preference fit
    - Validation Layer: Constraint enforcement + hallucination detection
    """

    def __init__(self, use_gemini: bool = False):
        """Initialize RAG components"""
        self.retriever = TravelRetriever()

        # Choose generator
        if use_gemini and GEMINI_AVAILABLE:
            self.generator = ConstraintAwareGeneratorGemini()
            self.generator_name = "Gemini (1M token context + caching)"
        else:
            self.generator = ConstraintAwareGenerator()
            self.generator_name = "Groq LLaMA 3.3 70B"

        # Initialize recommendation and validation layers
        self.recommender = VariantRecommender()
        self.validator = TravelItineraryValidator()

        print(f"✓ Travel RAG system initialized")
        print(f"  Generator: {self.generator_name}")
        print(f"  Validation: Enabled (budget, duration, hallucination checks)")
        print(f"  Recommendations: Enabled (variant ranking)")

    def plan_trip(
        self,
        destination: str,
        duration_days: int,
        budget_eur: float,
        preferences: Optional[List[str]] = None,
        travelers: int = 1,
        validate: bool = True,
        rank_variants: bool = True
    ) -> Dict:
        """
        Generate constraint-aware multi-option itinerary with validation.

        Args:
            destination: Target city/region
            duration_days: Trip length
            budget_eur: Total budget
            preferences: Optional preferences list
            travelers: Number of people
            validate: Run validation checks
            rank_variants: Use recommendation model to rank variants

        Returns:
            Structured itinerary with Budget/Comfort/Luxury variants
            Includes recommendation scores and validation report
        """
        print(f"\n{'='*60}")
        print(f"TRAVEL RAG: {duration_days}-day trip to {destination}")
        print(f"{'='*60}")
        print(f"Budget: €{budget_eur} | Travelers: {travelers}")
        if preferences:
            print(f"Preferences: {', '.join(preferences)}")

        # 1. GENERATE ITINERARY
        print(f"\n📍 Generating itinerary...")
        result = self.generator.generate_itinerary(
            destination=destination,
            duration_days=duration_days,
            budget_eur=budget_eur,
            preferences=preferences,
            travelers=travelers
        )

        # 2. RANK VARIANTS using recommendation model
        if rank_variants and result.get("variants"):
            print(f"⭐ Ranking variants by preference fit...")
            variants = result.get("variants", [])
            ranked = self.recommender.rank_variants(
                variants=variants,
                preferences=preferences or [],
                budget=budget_eur,
                travelers=travelers,
                duration_days=duration_days
            )
            result["variants"] = ranked

            # Add recommendation summary
            summary = self.recommender.get_recommendation_summary(ranked)
            result["recommendation_summary"] = summary

        # 3. VALIDATE ITINERARY
        if validate:
            print(f"✓ Validating itinerary...")
            validation_report = self.validator.validate_itinerary(
                itinerary=result,
                max_budget_eur=budget_eur,
                duration_days=duration_days,
                travelers=travelers
            )
            result["validation"] = validation_report
            print(f"  {validation_report['summary']}")

        return result

    def save_itinerary(self, itinerary: Dict, filename: Optional[str] = None) -> str:
        """Save itinerary to JSON file"""
        if filename is None:
            dest = itinerary.get("request", {}).get("destination", "trip")
            filename = f"itinerary_{dest.lower()}.json"

        filepath = filename if filename.startswith("/") else f"/Users/ilginguven/Desktop/RAG-PROJECT/{filename}"

        with open(filepath, 'w') as f:
            json.dump(itinerary, f, indent=2, default=str)

        print(f"\n✓ Itinerary saved: {filepath}")
        return filepath

    def print_itinerary(self, itinerary: Dict) -> None:
        """Pretty-print itinerary with variants, rankings, and validation"""
        request = itinerary.get("request", {})
        variants = itinerary.get("variants", [])

        print(f"\n{'='*60}")
        print(f"📍 {request.get('destination')}")
        print(f"{'='*60}")
        print(f"Duration: {request.get('duration_days')} days")
        print(f"Budget: €{request.get('budget_eur')} ({request.get('travelers')} traveler(s))")
        if request.get("preferences"):
            print(f"Preferences: {', '.join(request['preferences'])}")

        # Print recommendation summary if available
        rec_summary = itinerary.get("recommendation_summary")
        if rec_summary:
            print(f"\n⭐ RECOMMENDED: {rec_summary.get('recommended_variant')}")
            print(f"   Confidence: {rec_summary.get('confidence')}")
            for reason in rec_summary.get("key_reasons", [])[:2]:
                print(f"   ✓ {reason}")

        # Print validation status
        validation = itinerary.get("validation", {})
        if validation:
            print(f"\n✓ Validation Status: {validation.get('status')}")
            print(f"  Quality Score: {validation.get('quality_score', 0):.0f}/100")
            if validation.get("critical_issues", 0) > 0:
                print(f"  ⚠️ Critical Issues: {validation.get('critical_issues')}")

        # Print variants
        for i, variant in enumerate(variants, 1):
            if not isinstance(variant, dict):
                continue

            name = variant.get("name", f"Option {i}")
            breakdown = variant.get("cost_breakdown", {})
            rec_label = variant.get("recommendation_label", "")

            print(f"\n{i}. {name.upper()} {rec_label}")
            print(f"   {'-'*40}")

            if breakdown:
                print(f"   Accommodation: €{breakdown.get('accommodation_total', 0):.2f}")
                print(f"   Meals:         €{breakdown.get('meals_total', 0):.2f}")
                print(f"   Activities:    €{breakdown.get('activities_total', 0):.2f}")
                print(f"   Transport:     €{breakdown.get('transport_total', 0):.2f}")
                print(f"   {'─'*40}")
                print(f"   TOTAL:         €{breakdown.get('total_eur', 0):.2f}")

            # Show recommendation score
            rec_score = variant.get("recommendation_score")
            if rec_score:
                print(f"   Recommendation Score: {rec_score:.1f}/100")

            highlights = variant.get("highlights", [])
            if highlights:
                print(f"   Highlights: {', '.join(highlights[:3])}")

            notes = variant.get("notes", "")
            if notes:
                print(f"   Note: {notes[:80]}...")

        print(f"\n{'='*60}\n")

    def print_validation_report(self, validation_report: Dict) -> None:
        """Print detailed validation report"""
        print(f"\n{'='*60}")
        print(f"VALIDATION REPORT")
        print(f"{'='*60}")

        print(f"\n{validation_report.get('summary')}")
        print(f"Quality Score: {validation_report.get('quality_score', 0):.0f}/100")
        print(f"Total Issues: {validation_report.get('total_issues', 0)}")
        print(f"  - Critical: {validation_report.get('critical_issues', 0)}")
        print(f"  - Warnings: {validation_report.get('warnings', 0)}")

        if validation_report.get("issues"):
            print(f"\nIssue Details:")
            for issue in validation_report.get("issues", [])[:10]:
                level_icon = "❌" if issue["level"] == "critical" else "⚠️" if issue["level"] == "warning" else "ℹ️"
                print(f"  {level_icon} [{issue['component'].upper()}] {issue['message']}")

        if validation_report.get("hallucinations_found"):
            print(f"\nHallucination Check:")
            for halluc in validation_report.get("hallucinations_found", []):
                print(f"  {halluc}")

        print(f"\n{'='*60}\n")


def run_demo():
    """Run comprehensive demo with Day 3 enhancements"""
    print("\n" + "="*70)
    print("CONSTRAINT-AWARE TRAVEL RAG SYSTEM - DAY 3 DEMO")
    print("="*70)
    print("\nFeaturing:")
    print("  ✓ Multi-LLM support (Groq + Gemini with context caching)")
    print("  ✓ ML-based variant recommendations")
    print("  ✓ Comprehensive validation (constraints + hallucination detection)")

    # Initialize with Groq (Gemini requires GOOGLE_API_KEY)
    rag = TravelRAG(use_gemini=False)

    # Demo 1: Budget trip to Paris
    print("\n[Demo 1] Budget Paris Trip - with Validation")
    itinerary_1 = rag.plan_trip(
        destination="Paris",
        duration_days=3,
        budget_eur=600,
        preferences=["museums", "food"],
        travelers=1,
        validate=True,
        rank_variants=True
    )
    rag.print_itinerary(itinerary_1)
    if itinerary_1.get("validation"):
        rag.print_validation_report(itinerary_1["validation"])
    rag.save_itinerary(itinerary_1, "demo_paris_budget_day3.json")

    # Demo 2: Comfortable Berlin trip
    print("\n[Demo 2] Comfort Berlin Trip - with Recommendations")
    itinerary_2 = rag.plan_trip(
        destination="Berlin",
        duration_days=4,
        budget_eur=1200,
        preferences=["culture", "nightlife", "history"],
        travelers=2,
        validate=True,
        rank_variants=True
    )
    rag.print_itinerary(itinerary_2)
    rag.save_itinerary(itinerary_2, "demo_berlin_comfort_day3.json")

    # Demo 3: Luxury Barcelona trip
    print("\n[Demo 3] Luxury Barcelona Trip - Full Pipeline")
    itinerary_3 = rag.plan_trip(
        destination="Barcelona",
        duration_days=5,
        budget_eur=3000,
        preferences=["beaches", "art", "dining"],
        travelers=2,
        validate=True,
        rank_variants=True
    )
    rag.print_itinerary(itinerary_3)
    rag.save_itinerary(itinerary_3, "demo_barcelona_luxury_day3.json")

    print("\n" + "="*70)
    print("✅ DAY 3 DEMO COMPLETE")
    print("="*70)
    print("\nWhat's New in Day 3:")
    print("  ✓ Recommendation Model: Intelligently ranks variants by user fit")
    print("  ✓ Validation Layer: Detects hallucinations + enforces constraints")
    print("  ✓ Gemini Support: Long context (1M tokens) + context caching (40% cost savings)")
    print("  ✓ Metrics: Quality scores and validation reports included")
    print("\nFiles saved with _day3 suffix for comparison with Day 2\n")

    return [itinerary_1, itinerary_2, itinerary_3]


def run_gemini_demo():
    """Demo using Gemini (requires GOOGLE_API_KEY in .env)"""
    print("\n" + "="*70)
    print("GEMINI-POWERED TRAVEL RAG DEMO (with Context Caching)")
    print("="*70)

    if not GEMINI_AVAILABLE:
        print("\n⚠️ Gemini support not available.")
        print("To enable: pip install google-generativeai")
        return

    rag = TravelRAG(use_gemini=True)

    # Single demo with Gemini
    print("\n[Gemini Demo] Luxury Rome Trip")
    itinerary = rag.plan_trip(
        destination="Rome",
        duration_days=4,
        budget_eur=2000,
        preferences=["art", "history", "food"],
        travelers=1,
        validate=True,
        rank_variants=True
    )
    rag.print_itinerary(itinerary)

    # Show cache statistics if using Gemini
    if hasattr(rag.generator, 'get_cache_statistics'):
        print("\n📊 Cache Performance:")
        stats = rag.generator.get_cache_statistics()
        print(f"  Cached tokens: {stats.get('cached_tokens', 0)}")
        print(f"  New tokens: {stats.get('new_tokens', 0)}")
        print(f"  Cache efficiency: {stats.get('cache_efficiency', 'N/A')}")

    rag.save_itinerary(itinerary, "demo_rome_gemini.json")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--gemini":
        run_gemini_demo()
    else:
        # Run standard demo with Groq
        results = run_demo()
        print(f"\n✓ Generated {len(results)} itineraries with full Day 3 pipeline")
        print("  Next: Run `python main.py --gemini` to test Gemini features")
