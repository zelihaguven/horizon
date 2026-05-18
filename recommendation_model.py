"""
Travel Itinerary Recommendation Model
Intelligently ranks Budget/Comfort/Luxury variants based on user profile
Learns from preferences, past bookings, and spending patterns
"""

import json
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class SpendingProfile(Enum):
    """User spending tendency"""
    BUDGET_CONSCIOUS = "budget"
    BALANCED = "balanced"
    LUXURY_SEEKER = "luxury"


@dataclass
class UserProfile:
    """Represents a user's travel preferences and history"""
    destination_count: int = 0
    avg_budget_per_trip: float = 0.0
    preferred_activities: List[str] = None
    spending_profile: SpendingProfile = SpendingProfile.BALANCED
    past_variant_choices: Dict[str, str] = None  # destination -> chosen variant
    satisfaction_ratings: List[float] = None

    def __post_init__(self):
        if self.preferred_activities is None:
            self.preferred_activities = []
        if self.past_variant_choices is None:
            self.past_variant_choices = {}
        if self.satisfaction_ratings is None:
            self.satisfaction_ratings = []


class VariantRecommender:
    """
    Recommends optimal variants (Budget/Comfort/Luxury) for users
    Uses preference matching + spending profile analysis
    """

    def __init__(self):
        self.user_profiles = {}
        self.variant_thresholds = {
            "budget": {"max_budget": 500, "activity_density": "low"},
            "comfort": {"min_budget": 400, "max_budget": 2000, "activity_density": "medium"},
            "luxury": {"min_budget": 1500}
        }

    def analyze_user_profile(
        self,
        preferences: List[str],
        budget: float,
        duration: int,
        travelers: int = 1
    ) -> UserProfile:
        """Analyze user input to determine spending and activity profile"""

        # Determine spending profile
        budget_per_person_per_day = budget / travelers / duration

        if budget_per_person_per_day < 75:
            spending = SpendingProfile.BUDGET_CONSCIOUS
        elif budget_per_person_per_day > 200:
            spending = SpendingProfile.LUXURY_SEEKER
        else:
            spending = SpendingProfile.BALANCED

        profile = UserProfile(
            preferred_activities=preferences or [],
            spending_profile=spending
        )

        return profile

    def score_variant(
        self,
        variant: Dict,
        user_profile: UserProfile,
        preferences: List[str],
        budget: float,
        travelers: int
    ) -> Dict:
        """
        Score a variant (Budget/Comfort/Luxury) based on fit with user profile
        Returns score, reasoning, and match metrics
        """
        variant_name = variant.get("name", "Unknown").lower()
        cost_breakdown = variant.get("cost_breakdown", {})
        variant_cost = cost_breakdown.get("total_eur", 0)
        per_person_cost = cost_breakdown.get("per_person_eur", 0)
        highlights = variant.get("highlights", [])

        scores = {
            "budget_fit": 0,
            "activity_fit": 0,
            "user_profile_fit": 0,
            "value_score": 0,
            "overall_score": 0.0
        }

        reasoning = []

        # 1. BUDGET FIT (25% weight)
        if variant_cost <= budget:
            budget_fit = 100 * (1 - (variant_cost / budget) ** 0.5)
            scores["budget_fit"] = max(0, budget_fit)
            reasoning.append(f"Budget fit: {scores['budget_fit']:.0f}/100 (€{variant_cost} of €{budget})")
        else:
            scores["budget_fit"] = 0
            reasoning.append(f"⚠️ EXCEEDS BUDGET: €{variant_cost} > €{budget}")

        # 2. ACTIVITY FIT (30% weight)
        if preferences:
            highlight_lower = [h.lower() for h in highlights]
            preference_matches = sum(
                1 for pref in preferences
                if any(pref.lower() in h.lower() for h in highlight_lower)
            )
            activity_fit = (preference_matches / len(preferences)) * 100
            scores["activity_fit"] = activity_fit
            reasoning.append(
                f"Activity match: {scores['activity_fit']:.0f}/100 "
                f"({preference_matches}/{len(preferences)} preferences matched)"
            )

        # 3. USER PROFILE FIT (30% weight)
        if user_profile.spending_profile == SpendingProfile.BUDGET_CONSCIOUS:
            if variant_name == "budget":
                profile_fit = 100
            elif variant_name == "comfort":
                profile_fit = 60
            else:
                profile_fit = 20
            reasoning.append(
                f"Profile fit: {profile_fit}/100 (Budget-conscious user choosing {variant_name})"
            )
        elif user_profile.spending_profile == SpendingProfile.LUXURY_SEEKER:
            if variant_name == "luxury":
                profile_fit = 100
            elif variant_name == "comfort":
                profile_fit = 60
            else:
                profile_fit = 20
            reasoning.append(
                f"Profile fit: {profile_fit}/100 (Luxury-seeker user choosing {variant_name})"
            )
        else:  # BALANCED
            if variant_name == "comfort":
                profile_fit = 100
            elif variant_name in ["budget", "luxury"]:
                profile_fit = 70
            else:
                profile_fit = 50
            reasoning.append(
                f"Profile fit: {profile_fit}/100 (Balanced user choosing {variant_name})"
            )

        scores["user_profile_fit"] = profile_fit

        # 4. VALUE SCORE (15% weight)
        # Price per activity/experience
        activities_count = len(variant.get("activities", []))
        if activities_count > 0:
            cost_per_activity = variant_cost / activities_count
            value_score = 100 * (1 - (cost_per_activity / 100) ** 0.3)
            scores["value_score"] = max(0, value_score)
        else:
            scores["value_score"] = 50

        reasoning.append(
            f"Value score: {scores['value_score']:.0f}/100 "
            f"(€{variant_cost/max(1,travelers):.0f} per person)"
        )

        # WEIGHTED OVERALL SCORE
        scores["overall_score"] = (
            scores["budget_fit"] * 0.25 +
            scores["activity_fit"] * 0.30 +
            scores["user_profile_fit"] * 0.30 +
            scores["value_score"] * 0.15
        )

        return {
            "variant_name": variant_name,
            "scores": scores,
            "overall_score": scores["overall_score"],
            "reasoning": reasoning,
            "recommendation_confidence": min(100, scores["overall_score"] * 1.2)
        }

    def rank_variants(
        self,
        variants: List[Dict],
        preferences: List[str],
        budget: float,
        travelers: int = 1,
        duration_days: int = 3
    ) -> List[Dict]:
        """
        Rank all variants and return sorted by recommendation score
        Returns variants with detailed scoring and recommendation explanation
        """

        # Analyze user profile
        user_profile = self.analyze_user_profile(preferences, budget, duration_days, travelers)

        # Score each variant
        scored_variants = []
        for variant in variants:
            if not isinstance(variant, dict):
                continue

            score_result = self.score_variant(
                variant=variant,
                user_profile=user_profile,
                preferences=preferences,
                budget=budget,
                travelers=travelers
            )

            # Attach scoring to variant
            variant_with_scores = {
                **variant,
                "recommendation_score": score_result["overall_score"],
                "recommendation_reasoning": score_result["reasoning"],
                "recommendation_confidence": score_result["recommendation_confidence"],
                "detailed_scores": score_result["scores"]
            }

            scored_variants.append(variant_with_scores)

        # Sort by overall score
        ranked = sorted(scored_variants, key=lambda x: x.get("recommendation_score", 0), reverse=True)

        # Add ranking metadata
        for rank, variant in enumerate(ranked, 1):
            variant["recommended_rank"] = rank
            if rank == 1:
                variant["recommendation_label"] = "⭐ BEST FOR YOU"
            elif rank == 2:
                variant["recommendation_label"] = "✓ GOOD OPTION"
            else:
                variant["recommendation_label"] = "• ALTERNATIVE"

        return ranked

    def get_recommendation_summary(self, ranked_variants: List[Dict]) -> Dict:
        """Generate human-readable recommendation summary"""
        if not ranked_variants:
            return {"summary": "No variants to rank"}

        top_variant = ranked_variants[0]

        summary = {
            "recommended_variant": top_variant.get("name"),
            "recommendation_score": f"{top_variant.get('recommendation_score', 0):.1f}/100",
            "confidence": f"{top_variant.get('recommendation_confidence', 0):.0f}%",
            "key_reasons": [],
            "cost_range": {
                "min": min(v.get("cost_breakdown", {}).get("per_person_eur", 0) for v in ranked_variants),
                "max": max(v.get("cost_breakdown", {}).get("per_person_eur", 0) for v in ranked_variants),
                "recommended": top_variant.get("cost_breakdown", {}).get("per_person_eur", 0)
            }
        }

        # Extract top reasons
        for reason in top_variant.get("recommendation_reasoning", [])[:3]:
            if reason and not "⚠️" in reason:
                summary["key_reasons"].append(reason)

        # Add alternative options
        summary["other_options"] = [
            {
                "variant": v.get("name"),
                "score": f"{v.get('recommendation_score', 0):.1f}/100",
                "cost_per_person": f"€{v.get('cost_breakdown', {}).get('per_person_eur', 0):.0f}"
            }
            for v in ranked_variants[1:]
        ]

        return summary


def demonstrate_recommendation():
    """Demo: Show how recommendation model works"""
    print("\n" + "="*60)
    print("RECOMMENDATION MODEL DEMO")
    print("="*60)

    # Example variant (would come from generator)
    variant_budget = {
        "name": "Budget",
        "cost_breakdown": {
            "total_eur": 264,
            "per_person_eur": 264
        },
        "highlights": ["World-class museums", "Iconic landmarks", "Authentic local experiences"],
        "activities": [
            {"name": "Louvre Museum", "cost_eur": 20},
            {"name": "Eiffel Tower", "cost_eur": 18},
            {"name": "Montmartre walk", "cost_eur": 0}
        ]
    }

    variant_comfort = {
        "name": "Comfort",
        "cost_breakdown": {
            "total_eur": 300,
            "per_person_eur": 300
        },
        "highlights": ["Guided experiences", "Quality dining", "Mix of famous and hidden attractions"],
        "activities": [
            {"name": "Louvre", "cost_eur": 20},
            {"name": "Seine Cruise", "cost_eur": 18},
            {"name": "Museums", "cost_eur": 14}
        ]
    }

    # Create recommender
    recommender = VariantRecommender()

    # Test 1: Budget-conscious user
    print("\n📊 Test 1: Budget-Conscious User")
    print("-" * 40)
    ranked = recommender.rank_variants(
        variants=[variant_budget, variant_comfort],
        preferences=["museums", "food"],
        budget=600,
        travelers=1,
        duration_days=3
    )

    for v in ranked:
        print(f"\n{v.get('recommendation_label')} {v.get('name').upper()}")
        print(f"  Score: {v.get('recommendation_score', 0):.1f}/100")
        print(f"  Confidence: {v.get('recommendation_confidence', 0):.0f}%")
        for reason in v.get("recommendation_reasoning", []):
            print(f"  • {reason}")

    # Show summary
    summary = recommender.get_recommendation_summary(ranked)
    print(f"\n📋 SUMMARY")
    print(f"  Recommended: {summary['recommended_variant']} ({summary['recommendation_score']})")
    print(f"  Confidence: {summary['confidence']}")


if __name__ == "__main__":
    demonstrate_recommendation()
