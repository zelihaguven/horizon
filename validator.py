"""
Travel Itinerary Validator
Detects hallucinations, enforces constraints, and validates logical consistency
Day 3 core component for quality assurance
"""

import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"  # Budget exceeded, duration mismatch
    WARNING = "warning"    # Minor cost discrepancies, unknown attractions
    INFO = "info"          # Suggestions for improvement


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    level: ValidationLevel
    component: str  # "budget", "hallucination", "logic", "dates"
    message: str
    value: str = ""
    expected: str = ""
    severity_score: float = 1.0  # 0-100 impact


class HallucinationDetector:
    """
    Detects made-up attractions, restaurants, hotels
    Compares against known real places database
    """

    def __init__(self):
        # Real attractions, hotels, restaurants verified in real data
        self.known_places = {
            "Berlin": {
                "attractions": [
                    "Brandenburg Gate", "Berlin Wall Memorial", "East Side Gallery",
                    "Reichstag Dome", "Museum Island", "Charlottenburg Palace",
                    "Potsdamer Platz", "Kreuzberg", "Berghain"
                ],
                "hotels": [
                    "Hostel Berliner Mitte", "Hotel Berlin Central", "Adlon Kempinski"
                ],
                "restaurants": ["Local Café", "tapas bar", "fine restaurant"]
            },
            "Paris": {
                "attractions": [
                    "Louvre Museum", "Eiffel Tower", "Notre-Dame", "Arc de Triomphe",
                    "Montmartre", "Sacré-Cœur", "Musée d'Orsay", "Sainte-Chapelle",
                    "Champs-Élysées", "Latin Quarter"
                ],
                "hotels": [
                    "Hostel du Marais", "Hotel du Marais", "Ritz Paris"
                ],
                "restaurants": ["Bistro", "Michelin-starred", "Café"]
            },
            "Barcelona": {
                "attractions": [
                    "Sagrada Familia", "Park Güell", "Gothic Quarter",
                    "Picasso Museum", "Barceloneta Beach", "Las Ramblas",
                    "Montjuïc", "Bunkers del Carmel", "Casa Batlló"
                ],
                "hotels": [
                    "Barcelona Backpackers", "Hotel Sagrada Familia", "Mandarin Oriental Barcelona"
                ],
                "restaurants": ["tapas bar", "beachfront restaurant", "fine dining"]
            },
            "Amsterdam": {
                "attractions": [
                    "Anne Frank House", "Canal tour", "Rijksmuseum",
                    "Van Gogh Museum", "Dam Square", "Red Light District"
                ],
                "hotels": [
                    "ClinkNOORD Hostel", "Canal House Amsterdam", "Waldorf Astoria Amsterdam"
                ],
                "restaurants": ["Local café", "Dutch restaurant", "fine dining"]
            },
            "Rome": {
                "attractions": [
                    "Colosseum", "Vatican", "Roman Forum", "Pantheon",
                    "Spanish Steps", "Trevi Fountain", "Castel Sant'Angelo"
                ],
                "hotels": [
                    "The Yellow Hostel", "Hotel Colonna", "Hotel Eden"
                ],
                "restaurants": ["Trattoria", "Pizzeria", "fine dining"]
            },
            "London": {
                "attractions": [
                    "Tower of London", "Big Ben", "Tower Bridge",
                    "British Museum", "Buckingham Palace", "Thames River"
                ],
                "hotels": [
                    "Travelodge London", "Hotel Premier London", "Claridge's"
                ],
                "restaurants": ["Pub", "British restaurant", "fine dining"]
            }
        }

    def check_hallucination(self, place_name: str, city: str, place_type: str) -> Tuple[bool, str]:
        """
        Check if a place is hallucinated (made up)
        Returns: (is_real, confidence_message)
        """
        if city not in self.known_places:
            return True, f"City '{city}' not in database (unknown risk)"

        known_list = self.known_places[city].get(place_type + "s", [])

        # Exact match
        if place_name in known_list:
            return True, f"✓ Verified {place_type}"

        # Partial match (e.g., "Louvre" matches "Louvre Museum")
        place_lower = place_name.lower()
        for known in known_list:
            if place_lower in known.lower() or known.lower() in place_lower:
                return True, f"✓ Likely real {place_type}"

        # Generic matches (e.g., "local bistro", "nice restaurant")
        generic_terms = ["local", "nice", "fine", "budget", "traditional"]
        if any(term in place_lower for term in generic_terms):
            return True, f"⚠️ Generic {place_type} (assumed available)"

        # Likely hallucination
        return False, f"❌ UNKNOWN {place_type.upper()}: '{place_name}'"


class ConstraintValidator:
    """Validates hard constraints: budget, duration, dates"""

    @staticmethod
    def validate_budget(
        itinerary: Dict,
        max_budget_eur: float,
        travelers: int
    ) -> List[ValidationIssue]:
        """Check that costs don't exceed budget"""
        issues = []
        variants = itinerary.get("variants", [])

        for variant in variants:
            if not isinstance(variant, dict):
                continue

            total_cost = variant.get("cost_breakdown", {}).get("total_eur", 0)
            per_person_cost = variant.get("cost_breakdown", {}).get("per_person_eur", 0)

            # Hard constraint: MUST NOT exceed budget
            if total_cost > max_budget_eur:
                overage = total_cost - max_budget_eur
                issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    component="budget",
                    message=f"BUDGET EXCEEDED: {variant.get('name')} costs €{total_cost} (budget: €{max_budget_eur})",
                    value=f"€{total_cost}",
                    expected=f"€{max_budget_eur}",
                    severity_score=100.0
                ))

            # Warning: at >90% of budget
            elif total_cost > max_budget_eur * 0.90:
                usage = (total_cost / max_budget_eur) * 100
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    component="budget",
                    message=f"HIGH USAGE: {variant.get('name')} uses {usage:.0f}% of budget",
                    value=f"€{total_cost}",
                    expected=f"€{max_budget_eur}",
                    severity_score=50.0
                ))

        return issues

    @staticmethod
    def validate_duration(itinerary: Dict, expected_days: int) -> List[ValidationIssue]:
        """Check that itinerary matches requested duration"""
        issues = []
        variants = itinerary.get("variants", [])

        for variant in variants:
            if not isinstance(variant, dict):
                continue

            itinerary_days = variant.get("daily_itinerary", [])
            actual_days = len(itinerary_days)

            if actual_days != expected_days:
                issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    component="duration",
                    message=f"DURATION MISMATCH: {variant.get('name')} has {actual_days} days (expected {expected_days})",
                    value=f"{actual_days} days",
                    expected=f"{expected_days} days",
                    severity_score=100.0
                ))

        return issues

    @staticmethod
    def validate_daily_costs(itinerary: Dict, daily_budget: float) -> List[ValidationIssue]:
        """Check that daily costs don't exceed daily budget"""
        issues = []
        variants = itinerary.get("variants", [])

        for variant in variants:
            daily_itinerary = variant.get("daily_itinerary", [])

            for day_data in daily_itinerary:
                day_num = day_data.get("day", 0)
                day_cost = day_data.get("estimated_cost_eur", 0)

                if day_cost > daily_budget * 1.5:  # Allow 50% variance
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        component="daily_costs",
                        message=f"{variant.get('name')} Day {day_num}: €{day_cost} exceeds daily budget (€{daily_budget})",
                        value=f"€{day_cost}",
                        expected=f"€{daily_budget}",
                        severity_score=40.0
                    ))

        return issues


class CostIntegrityValidator:
    """Validates that cost calculations are mathematically correct"""

    @staticmethod
    def validate_cost_breakdown(variant: Dict) -> List[ValidationIssue]:
        """Check that cost components sum correctly"""
        issues = []

        breakdown = variant.get("cost_breakdown", {})
        accommodation = breakdown.get("accommodation_total", 0)
        meals = breakdown.get("meals_total", 0)
        activities = breakdown.get("activities_total", 0)
        transport = breakdown.get("transport_total", 0)
        total = breakdown.get("total_eur", 0)

        calculated_total = accommodation + meals + activities + transport
        expected_total = breakdown.get("total_eur", 0)

        tolerance = 5  # Allow €5 rounding error

        if abs(calculated_total - expected_total) > tolerance:
            issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                component="cost_integrity",
                message=f"COST MATH ERROR: Components sum to €{calculated_total}, total shows €{expected_total}",
                value=f"€{calculated_total}",
                expected=f"€{expected_total}",
                severity_score=80.0
            ))

        return issues

    @staticmethod
    def validate_activity_costs(variant: Dict) -> List[ValidationIssue]:
        """Check that activity costs match breakdown"""
        issues = []

        activities = variant.get("activities", [])
        breakdown = variant.get("cost_breakdown", {})
        activities_total = breakdown.get("activities_total", 0)

        calculated_activities_cost = sum(a.get("cost_eur", 0) for a in activities)

        tolerance = 10  # €10 tolerance

        if abs(calculated_activities_cost - activities_total) > tolerance:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                component="activity_costs",
                message=f"ACTIVITY COST MISMATCH: Activities sum to €{calculated_activities_cost}, breakdown shows €{activities_total}",
                value=f"€{calculated_activities_cost}",
                expected=f"€{activities_total}",
                severity_score=30.0
            ))

        return issues


class TravelItineraryValidator:
    """
    Main validator orchestrating all checks
    Returns comprehensive validation report with issues and recommendations
    """

    def __init__(self):
        self.hallucination_detector = HallucinationDetector()
        self.constraint_validator = ConstraintValidator()
        self.cost_validator = CostIntegrityValidator()

    def validate_itinerary(
        self,
        itinerary: Dict,
        max_budget_eur: float,
        duration_days: int,
        travelers: int = 1
    ) -> Dict:
        """
        Comprehensive validation of entire itinerary
        Returns detailed report with all issues and quality score
        """

        issues = []
        hallucinations_found = []

        # 1. CONSTRAINT VALIDATION
        issues.extend(self.constraint_validator.validate_budget(itinerary, max_budget_eur, travelers))
        issues.extend(self.constraint_validator.validate_duration(itinerary, duration_days))
        issues.extend(self.constraint_validator.validate_daily_costs(
            itinerary,
            max_budget_eur / (travelers * duration_days)
        ))

        # 2. COST INTEGRITY VALIDATION
        for variant in itinerary.get("variants", []):
            if isinstance(variant, dict):
                issues.extend(self.cost_validator.validate_cost_breakdown(variant))
                issues.extend(self.cost_validator.validate_activity_costs(variant))

        # 3. HALLUCINATION DETECTION
        destination = itinerary.get("request", {}).get("destination", "")

        for variant in itinerary.get("variants", []):
            if not isinstance(variant, dict):
                continue

            # Check accommodation
            accommodation = variant.get("accommodation", {})
            is_real, msg = self.hallucination_detector.check_hallucination(
                accommodation.get("name", ""),
                destination,
                "hotel"
            )
            if not is_real:
                hallucinations_found.append(msg)
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    component="hallucination",
                    message=msg,
                    severity_score=60.0
                ))

            # Check activities
            for activity in variant.get("activities", []):
                is_real, msg = self.hallucination_detector.check_hallucination(
                    activity.get("name", ""),
                    destination,
                    "attraction"
                )
                if not is_real and "UNKNOWN" in msg:
                    hallucinations_found.append(msg)
                    issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        component="hallucination",
                        message=msg,
                        severity_score=20.0
                    ))

        # CALCULATE QUALITY SCORE
        critical_count = sum(1 for i in issues if i.level == ValidationLevel.CRITICAL)
        warning_count = sum(1 for i in issues if i.level == ValidationLevel.WARNING)

        quality_score = 100.0
        quality_score -= critical_count * 50
        quality_score -= warning_count * 10
        quality_score = max(0, quality_score)

        # Determine status
        if critical_count > 0:
            status = "INVALID"
        elif warning_count > 0:
            status = "WARNING"
        else:
            status = "VALID"

        return {
            "status": status,
            "quality_score": quality_score,
            "total_issues": len(issues),
            "critical_issues": critical_count,
            "warnings": warning_count,
            "issues": [
                {
                    "level": i.level.value,
                    "component": i.component,
                    "message": i.message,
                    "severity": i.severity_score
                }
                for i in sorted(issues, key=lambda x: x.severity_score, reverse=True)
            ],
            "hallucinations_found": hallucinations_found,
            "summary": self._generate_summary(status, quality_score, len(issues), critical_count)
        }

    @staticmethod
    def _generate_summary(status: str, quality: float, total_issues: int, critical: int) -> str:
        """Generate human-readable validation summary"""
        if status == "VALID":
            return f"✓ VALID ITINERARY - Quality: {quality:.0f}/100 ({total_issues} minor notes)"
        elif status == "WARNING":
            return f"⚠️ REVIEW NEEDED - {total_issues} issues found (none critical)"
        else:
            return f"❌ INVALID - {critical} critical issues must be fixed"


def demo_validation():
    """Demo: Show validator in action"""
    print("\n" + "="*60)
    print("VALIDATION LAYER DEMO")
    print("="*60)

    validator = TravelItineraryValidator()

    # Example itinerary (from demo_paris_budget.json)
    test_itinerary = {
        "request": {
            "destination": "Paris",
            "duration_days": 3,
            "budget_eur": 600,
            "travelers": 1
        },
        "variants": [
            {
                "name": "Budget",
                "accommodation": {
                    "name": "Hostel du Marais",
                    "total_eur": 56
                },
                "activities": [
                    {"name": "Louvre Museum Ticket", "cost_eur": 20},
                    {"name": "Eiffel Tower Visit", "cost_eur": 18},
                    {"name": "Walk through Montmartre", "cost_eur": 0}
                ],
                "cost_breakdown": {
                    "accommodation_total": 56,
                    "meals_total": 105,
                    "activities_total": 38,
                    "transport_total": 0,
                    "total_eur": 199,
                    "per_person_eur": 199
                },
                "daily_itinerary": [
                    {"day": 1, "activities": ["Arrive", "Louvre"], "estimated_cost_eur": 35},
                    {"day": 2, "activities": ["Eiffel Tower", "Museums"], "estimated_cost_eur": 49},
                    {"day": 3, "activities": ["Montmartre"], "estimated_cost_eur": 38}
                ]
            }
        ]
    }

    # Run validation
    report = validator.validate_itinerary(
        itinerary=test_itinerary,
        max_budget_eur=600,
        duration_days=3,
        travelers=1
    )

    # Print report
    print(f"\n{report['summary']}")
    print(f"\nQuality Score: {report['quality_score']:.0f}/100")
    print(f"Issues: {report['total_issues']} total ({report['critical_issues']} critical)")

    if report['issues']:
        print("\nDetailed Issues:")
        for issue in report['issues'][:5]:
            print(f"  [{issue['level'].upper()}] {issue['message']}")


if __name__ == "__main__":
    demo_validation()
