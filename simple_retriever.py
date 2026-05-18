"""
Simple Retriever: Load data from CSV and provide semantic search
without ChromaDB dependencies
"""

import pandas as pd
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class SimpleRetriever:
    """
    Simple retriever that loads data from CSV and provides filtering.
    Works without external embedding dependencies.
    """

    def __init__(self, csv_path: str = "data/processed/travel_data.csv"):
        """Load data from CSV"""
        try:
            self.data = pd.read_csv(csv_path)
            print(f"✓ Loaded {len(self.data)} travel items from {csv_path}")

            # Show what we have
            types = self.data['type'].value_counts()
            print(f"  - {types.get('restaurant', 0)} restaurants")
            print(f"  - {types.get('hotel', 0)} hotels")
            print(f"  - {types.get('activity', 0)} activities")
            print(f"  - {types.get('transport', 0)} transport")
        except FileNotFoundError:
            print(f"⚠ CSV not found at {csv_path}")
            self.data = pd.DataFrame()

    def retrieve_by_category(
        self,
        query: str,
        category: str,
        city: Optional[str] = None,
        k: int = 3
    ) -> List[Dict]:
        """
        Retrieve items by category with simple text matching.
        Returns ALL items in category/city since LLM handles semantic understanding.
        """
        if self.data.empty:
            return []

        # Filter by type
        filtered = self.data[self.data['type'] == category]

        # Filter by city if specified
        if city:
            filtered = filtered[filtered['city'] == city]

        if filtered.empty:
            return []

        # Simple text-based relevance scoring
        query_lower = query.lower()
        results = []

        for _, row in filtered.iterrows():
            # Score based on keyword matches in description
            desc_lower = str(row['description']).lower()
            name_lower = str(row['name']).lower()

            # Check if query keywords appear in description
            query_words = [w for w in query_lower.split() if len(w) > 2]  # Skip tiny words
            if query_words:
                matches = sum(1 for word in query_words if word in desc_lower or word in name_lower)
                score = matches / len(query_words)
            else:
                score = 1.0  # Default high score if no meaningful query words

            # Include all items in the category/city, sorted by relevance
            results.append({
                "text": row['description'],
                "metadata": {
                    "city": row['city'],
                    "type": row['type'],
                    "name": row['name'],
                    "price_eur": float(row['price_eur']),
                    "price_range": row['price_range'],
                    "rating": float(row['rating']),
                    "source": row['source']
                },
                "relevance": score
            })

        # Sort by rating and relevance score, return top k
        results.sort(key=lambda x: (-x['metadata']['rating'], -x['relevance']))
        return results[:k]

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Generic retrieval with optional filters"""
        if self.data.empty:
            return []

        filtered = self.data.copy()

        # Apply filters
        if filters:
            if 'type' in filters:
                filtered = filtered[filtered['type'] == filters['type']]
            if 'city' in filters:
                filtered = filtered[filtered['city'] == filters['city']]

        if filtered.empty:
            return []

        # Simple keyword matching
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for _, row in filtered.iterrows():
            desc_lower = str(row['description']).lower()
            name_lower = str(row['name']).lower()

            matches = sum(1 for word in query_words if word in desc_lower or word in name_lower)
            score = matches / len(query_words) if query_words else 0

            if score > 0:
                results.append({
                    "text": row['description'],
                    "metadata": {
                        "city": row['city'],
                        "type": row['type'],
                        "name": row['name'],
                        "price_eur": float(row['price_eur']),
                        "price_range": row['price_range'],
                        "rating": float(row['rating']),
                        "source": row['source']
                    },
                    "relevance": score
                })

        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:k]

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if self.data.empty:
            return {"total_items": 0, "error": "No data loaded"}

        return {
            "total_items": len(self.data),
            "by_type": self.data['type'].value_counts().to_dict(),
            "cities": self.data['city'].unique().tolist(),
            "status": "ready"
        }


def test_simple_retriever():
    """Test the simple retriever"""
    print("\n" + "="*60)
    print("TEST: Simple Retriever")
    print("="*60)

    retriever = SimpleRetriever()

    stats = retriever.get_collection_stats()
    print(f"\nCollection stats: {stats}")

    # Test 1: Restaurants in Paris
    print("\n[Test 1] Restaurants in Paris")
    results = retriever.retrieve_by_category(
        query="good dining restaurants",
        category="restaurant",
        city="Paris",
        k=3
    )
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['metadata']['name']} - €{r['metadata']['price_eur']}")

    # Test 2: Hotels in Berlin
    print("\n[Test 2] Hotels in Berlin")
    results = retriever.retrieve_by_category(
        query="comfortable hotels",
        category="hotel",
        city="Berlin",
        k=3
    )
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['metadata']['name']} - €{r['metadata']['price_eur']}")

    # Test 3: Activities
    print("\n[Test 3] Activities")
    results = retriever.retrieve_by_category(
        query="museums attractions tours",
        category="activity",
        k=3
    )
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['metadata']['name']} - €{r['metadata']['price_eur']}")

    print("\n✅ Simple retriever test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_simple_retriever()
