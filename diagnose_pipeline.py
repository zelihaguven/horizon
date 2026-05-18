"""
Diagnostic script to trace restaurant data through the entire RAG pipeline.
Identifies where restaurant names are lost or transformed.
"""

import json
import os
from data_pipeline import create_restaurant_data, load_all_real_data, add_metadata, create_text_chunks
from retriever import TravelRetriever

def diagnose():
    """Run full diagnostic of the pipeline"""
    print("\n" + "="*70)
    print("RESTAURANT DATA PIPELINE DIAGNOSTIC")
    print("="*70)

    # STAGE 1: Check create_restaurant_data function
    print("\n[STAGE 1] Raw Restaurant Data Creation")
    print("-" * 70)
    try:
        restaurants = create_restaurant_data()
        print(f"✓ Created {len(restaurants)} restaurants")
        print("\nSample restaurants:")
        for i, (_, row) in enumerate(restaurants.head(3).iterrows()):
            print(f"  {i+1}. {row['name']} ({row['city']}) - €{row['price_eur']} - {row.get('cuisine', 'N/A')}")

        # Check data structure
        print(f"\nColumns: {list(restaurants.columns)}")
        print(f"Data types:\n{restaurants.dtypes}")
    except Exception as e:
        print(f"✗ Error in create_restaurant_data: {e}")
        return

    # STAGE 2: Check load_all_real_data
    print("\n[STAGE 2] Full Data Pipeline (load_all_real_data)")
    print("-" * 70)
    try:
        all_data = load_all_real_data()

        if 'restaurants' in all_data:
            rest_df = all_data['restaurants']
            print(f"✓ Loaded {len(rest_df)} restaurants via pipeline")
            print("\nFirst 3 restaurants in pipeline:")
            for i, (_, row) in enumerate(rest_df.head(3).iterrows()):
                print(f"  {i+1}. {row['name']} ({row['city']}) - Source: {row['source']}")
        else:
            print("✗ No restaurants in loaded data!")

    except Exception as e:
        print(f"✗ Error in load_all_real_data: {e}")
        import traceback
        traceback.print_exc()
        return

    # STAGE 3: Check data after metadata addition
    print("\n[STAGE 3] After Metadata Addition")
    print("-" * 70)
    try:
        # Combine all data like the pipeline does
        frames = []
        for key, df in all_data.items():
            if not df.empty:
                df_clean = df[["city", "name", "type", "price_eur", "rating", "description", "source"]].copy()
                df_clean = df_clean.dropna(subset=["city", "name", "description"])
                frames.append(df_clean)

        if frames:
            df_combined = __import__('pandas').concat(frames, ignore_index=True)

            # Filter for restaurants
            restaurants_in_combined = df_combined[df_combined['type'] == 'restaurant']
            print(f"✓ {len(restaurants_in_combined)} restaurants in combined data")

            if len(restaurants_in_combined) > 0:
                print("\nFirst 3 restaurants in combined data:")
                for i, (_, row) in enumerate(restaurants_in_combined.head(3).iterrows()):
                    print(f"  {i+1}. {row['name']} ({row['city']}) - Type: {row['type']}")

            # Add metadata
            df_with_metadata = add_metadata(df_combined)
            restaurants_with_meta = df_with_metadata[df_with_metadata['type'] == 'restaurant']
            print(f"\n✓ After metadata: {len(restaurants_with_meta)} restaurants")

        else:
            print("✗ No frames to combine!")

    except Exception as e:
        print(f"✗ Error in metadata stage: {e}")
        import traceback
        traceback.print_exc()
        return

    # STAGE 4: Check chunks created for embedding
    print("\n[STAGE 4] Text Chunks for ChromaDB")
    print("-" * 70)
    try:
        chunks = create_text_chunks(df_with_metadata)

        restaurant_chunks = [c for c in chunks if 'restaurant' in c['text'].lower() and c['metadata']['type'] == 'restaurant']
        print(f"✓ Created {len(restaurant_chunks)} restaurant chunks")

        if len(restaurant_chunks) > 0:
            print("\nFirst restaurant chunk:")
            chunk = restaurant_chunks[0]
            print("TEXT:")
            print(chunk['text'][:300])
            print("\nMETADATA:")
            print(json.dumps(chunk['metadata'], indent=2))

    except Exception as e:
        print(f"✗ Error in chunk creation: {e}")
        import traceback
        traceback.print_exc()
        return

    # STAGE 5: Check ChromaDB
    print("\n[STAGE 5] ChromaDB Content")
    print("-" * 70)
    try:
        retriever = TravelRetriever()
        stats = retriever.get_collection_stats()
        print(f"✓ ChromaDB has {stats.get('total_vectors', 'unknown')} total vectors")

        # Try to retrieve restaurants
        results = retriever.retrieve_by_category(
            query="restaurants dining food",
            category="restaurant",
            city="Paris",
            k=5
        )

        if results:
            print(f"\n✓ Retrieved {len(results)} restaurants from Paris")
            for i, r in enumerate(results[:3]):
                meta = r['metadata']
                print(f"  {i+1}. {meta.get('name', 'N/A')} - Type: {meta.get('type')}")
                print(f"     Similarity: {r.get('similarity', 'N/A'):.3f}")
        else:
            print("\n✗ No restaurants retrieved from ChromaDB for Paris!")
            print("  Trying generic retrieve...")
            generic = retriever.retrieve("restaurants Paris", k=5)
            if generic:
                print(f"  Found {len(generic)} generic results:")
                for i, r in enumerate(generic[:3]):
                    print(f"    {i+1}. {r['metadata'].get('name', 'N/A')} (Type: {r['metadata'].get('type')})")

    except Exception as e:
        print(f"✗ Error accessing ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return

    # STAGE 6: Check Generator with retrieved data
    print("\n[STAGE 6] Generator with Retrieved Data")
    print("-" * 70)
    try:
        from generator import ConstraintAwareGenerator

        gen = ConstraintAwareGenerator()

        # Get what gets retrieved
        retrieved = gen._retrieve_options(destination="Paris", preferences=["food"])

        if retrieved['restaurants']:
            print(f"✓ Generator retrieved {len(retrieved['restaurants'])} restaurants for Paris")
            for i, r in enumerate(retrieved['restaurants'][:3]):
                meta = r['metadata']
                print(f"  {i+1}. {meta.get('name')} - €{meta.get('price_eur')}")

            # Check what format context uses
            context = gen._format_options_context(retrieved)
            print("\nContext formatted for LLM (RESTAURANTS section):")
            lines = context.split('\n')
            for line in lines:
                if 'RESTAURANT' in line or (len(lines) > 0 and lines[0] in line):
                    print(line)
                    # Print next 3 lines
                    for j in range(3):
                        if lines.index(line) + j + 1 < len(lines):
                            print(lines[lines.index(line) + j + 1])
                    break
        else:
            print("✗ Generator retrieved NO restaurants for Paris")

    except Exception as e:
        print(f"✗ Error in generator check: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    diagnose()
