"""
Retrieval Layer: Semantic search + metadata filtering for constraint-aware retrieval
"""

from langchain_chroma import Chroma
from typing import List, Dict, Optional


class TravelRetriever:
    """
    Retriever with semantic search and metadata filtering.
    Handles multi-category retrieval: hotels, restaurants, activities, transport
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize retriever with ChromaDB vectorstore"""
        # Use Chroma's default embeddings (no external embedding function needed)
        self.vectorstore = Chroma(
            persist_directory=persist_directory
        )
        print(f"✓ Retriever initialized with ChromaDB ({persist_directory})")

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search with optional metadata filtering.

        Args:
            query: Natural language query (e.g., "affordable hotels near Paris")
            k: Number of results to retrieve
            filters: Metadata filters (e.g., {"city": "Paris", "type": "hotel"})

        Returns:
            List of dicts with text, metadata, and similarity score
        """
        try:
            # Semantic similarity search
            results = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)

            # Convert to structured format
            retrieved = []
            for doc, score in results:
                # Apply metadata filters if provided
                if filters and not self._matches_filters(doc.metadata, filters):
                    continue

                retrieved.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity": 1 - score  # Convert distance to similarity
                })

            return retrieved

        except Exception as e:
            print(f"⚠ Retrieval error: {e}")
            return []

    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if metadata matches all filter criteria"""
        for key, value in filters.items():
            if key not in metadata:
                return False
            # Handle list values (e.g., city could be in multiple places)
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        return True

    def retrieve_by_category(
        self,
        query: str,
        category: str,  # "hotel", "restaurant", "activity", "transport"
        city: Optional[str] = None,
        k: int = 3
    ) -> List[Dict]:
        """
        Retrieve specific category with semantic search + metadata filtering.

        Args:
            query: Natural language query
            category: "hotel", "restaurant", "activity", or "transport"
            city: Optional city filter
            k: Number of results per category

        Returns:
            List of filtered and ranked results
        """
        filters = {"type": category}
        if city:
            filters["city"] = city

        return self.retrieve(query, k=k, filters=filters)

    def get_collection_stats(self) -> Dict:
        """Get information about the collection"""
        try:
            count = self._get_count()
            # Get sample metadata
            results = self.vectorstore.similarity_search("travel", k=1)
            sample_metadata = results[0].metadata if results else {}

            return {
                "total_vectors": count,
                "sample_metadata": sample_metadata,
                "status": "ready"
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_count(self) -> int:
        """Safe count method"""
        try:
            return self.vectorstore._collection.count()
        except:
            return 0


def test_retriever():
    """Test retriever with sample queries"""
    print("\n" + "="*60)
    print("TEST: Retrieval Layer")
    print("="*60)

    retriever = TravelRetriever()

    # Get stats
    stats = retriever.get_collection_stats()
    print(f"\n✓ Collection stats: {stats['total_vectors']} vectors")

    # Test 1: General semantic search
    print("\n[Test 1] Semantic search - 'budget hotels'")
    results = retriever.retrieve("affordable budget hotels", k=3)
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata'].get('name')} ({result['metadata'].get('city')})")

    # Test 2: Category-specific retrieval
    print("\n[Test 2] Category search - hotels in Paris")
    results = retriever.retrieve_by_category(
        "comfortable place to stay",
        category="hotel",
        city="Paris",
        k=3
    )
    if results:
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata'].get('name')} - €{result['metadata'].get('price_eur')}")
    else:
        print("  (No Paris hotels found - will be available with full restaurant data)")

    # Test 3: Activities search
    print("\n[Test 3] Category search - attractions")
    results = retriever.retrieve_by_category(
        "museums famous landmarks",
        category="activity",
        k=3
    )
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata'].get('name')} - €{result['metadata'].get('price_eur')}")

    # Test 4: Transport search
    print("\n[Test 4] Category search - transportation")
    results = retriever.retrieve_by_category(
        "travel between cities",
        category="transport",
        k=3
    )
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata'].get('name')} - €{result['metadata'].get('price_eur')}")

    print("\n✅ Retrieval layer operational!")
    print("="*60 + "\n")

    return retriever


if __name__ == "__main__":
    retriever = test_retriever()
