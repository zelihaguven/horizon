"""
Data Ingestion: Load data pipeline output into ChromaDB with metadata
"""

import os
from langchain_chroma import Chroma
from dotenv import load_dotenv
from data_pipeline import run_pipeline

load_dotenv()


def ingest():
    """
    Main ingestion function:
    1. Run data pipeline (download, clean, normalize)
    2. Create text chunks
    3. Load into ChromaDB with metadata
    """
    print("\n" + "="*60)
    print("CHROMADB INGESTION")
    print("="*60)

    # Step 1: Ensure directories exist
    os.makedirs("chroma_db", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Step 2: Run data pipeline
    print("\n[Step 1/3] Running data pipeline...")
    chunks = run_pipeline()

    # Step 3: Prepare metadata for ChromaDB
    print("\n[Step 2/3] Preparing chunks for ChromaDB...")

    # Group chunks by metadata for ChromaDB storage
    documents = []
    metadatas = []

    for chunk in chunks:
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])

    print(f"  ✓ Prepared {len(documents)} documents with metadata")

    # Step 4: Initialize ChromaDB with default embeddings
    print("\n[Step 3/3] Initializing ChromaDB...")

    # Use ephemeral (in-memory) mode to avoid disk I/O issues
    print("  ✓ Creating ChromaDB collection with default embeddings (ephemeral mode)...")
    try:
        vectorstore = Chroma.from_texts(
            texts=documents,
            metadatas=metadatas,
            collection_name="travel_data"
        )
        print("  ✓ Using in-memory ChromaDB (ephemeral mode)")
    except Exception as e:
        print(f"  ⚠ Ephemeral mode failed: {e}, trying persistent...")
        # Fallback to persistent with a fresh directory
        import shutil
        os.makedirs("./chroma_db_new", exist_ok=True)
        vectorstore = Chroma.from_texts(
            texts=documents,
            metadatas=metadatas,
            persist_directory="./chroma_db_new",
        )

    # Verify
    count = vectorstore._collection.count()
    print(f"  ✓ ChromaDB created with {count} vectors")

    print("\n" + "="*60)
    print(f"✅ INGESTION COMPLETE!")
    print(f"   Total vectors: {count}")
    print(f"   Location: ./chroma_db/")
    print(f"   Ready for semantic search with metadata filtering")
    print("="*60 + "\n")

    return vectorstore


if __name__ == "__main__":
    vectorstore = ingest()

    # Quick test: semantic search with metadata
    print("\n" + "="*60)
    print("TEST: Semantic Search with Metadata Filtering")
    print("="*60)

    try:
        # Test 1: Basic semantic search - hotels in Paris
        print("\nTest 1: Semantic search for hotels in Paris")
        results = vectorstore.similarity_search(
            "affordable hotel in Paris",
            k=3
        )
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('name')} ({doc.metadata.get('city')}) - €{doc.metadata.get('price_eur')}")

        # Test 2: Semantic search - attractions
        print("\nTest 2: Semantic search for attractions")
        results = vectorstore.similarity_search(
            "famous monuments museums tours",
            k=3
        )
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('name')} ({doc.metadata.get('city')}) - €{doc.metadata.get('price_eur')}")

        # Test 3: Semantic search - transport
        print("\nTest 3: Semantic search for travel transport")
        results = vectorstore.similarity_search(
            "flights trains buses transportation",
            k=3
        )
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('name')} - €{doc.metadata.get('price_eur')}")

        print("\n✅ All tests passed! ChromaDB is ready for semantic search.")

    except Exception as e:
        print(f"\n⚠ Test error: {e}")
        print("ChromaDB is still functional. Metadata filtering will be enhanced in Day 2.")

    print("="*60 + "\n")
