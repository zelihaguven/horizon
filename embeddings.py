"""
Embeddings: Initialize and configure embeddings for ChromaDB
Uses Chroma's default embeddings to avoid external dependencies
"""

class ChromaDefaultEmbeddings:
    """
    Default embeddings using Chroma's built-in embedding function.
    This uses the default all-MiniLM-L6-v2 equivalent without requiring sentence_transformers.
    """
    def __new__(cls):
        # Return None to use Chroma's default embedding function
        # Chroma will use its built-in embedding which handles everything
        return None


if __name__ == "__main__":
    # Quick test
    embeddings = ChromaDefaultEmbeddings()
    test_text = "This is a test sentence"
    vector = embeddings.embed_query(test_text)
    print(f"✅ Embeddings initialized successfully")
    print(f"   Model: all-MiniLM-L6-v2")
    print(f"   Vector dimension: {len(vector)}")
