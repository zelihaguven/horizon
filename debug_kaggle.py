"""
Debug Script: Inspect Kaggle datasets to understand their structure
"""

import pandas as pd
from pathlib import Path

def debug_hotels():
    """Inspect hotel reviews dataset."""
    print("\n" + "="*60)
    print("DEBUGGING: Hotel Reviews Dataset")
    print("="*60)

    try:
        import kagglehub
        path = kagglehub.dataset_download("andrewmvd/trip-advisor-hotel-reviews")
        csv_files = list(Path(path).glob("**/*.csv"))

        if csv_files:
            df = pd.read_csv(csv_files[0], nrows=5)
            print(f"\n✓ Found CSV: {csv_files[0].name}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            print(f"\nData types:\n{df.dtypes}")
        else:
            print("❌ No CSV files found")
    except Exception as e:
        print(f"❌ Error: {e}")


def debug_restaurants():
    """Inspect restaurants dataset."""
    print("\n" + "="*60)
    print("DEBUGGING: Restaurants Dataset")
    print("="*60)

    try:
        import kagglehub
        path = kagglehub.dataset_download("stefanoleone992/tripadvisor-european-restaurants")
        csv_files = list(Path(path).glob("**/*.csv"))

        if csv_files:
            df = pd.read_csv(csv_files[0], nrows=5)
            print(f"\n✓ Found CSV: {csv_files[0].name}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            print(f"\nData types:\n{df.dtypes}")
        else:
            print("❌ No CSV files found")
    except Exception as e:
        print(f"❌ Error: {e}")


def debug_activities():
    """Inspect travel recommendation dataset."""
    print("\n" + "="*60)
    print("DEBUGGING: Travel Recommendation Dataset")
    print("="*60)

    try:
        import kagglehub
        path = kagglehub.dataset_download("amanmehra23/travel-recommendation-dataset")
        csv_files = list(Path(path).glob("**/*.csv"))

        if csv_files:
            df = pd.read_csv(csv_files[0], nrows=5)
            print(f"\n✓ Found CSV: {csv_files[0].name}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            print(f"\nData types:\n{df.dtypes}")
        else:
            print("❌ No CSV files found")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("KAGGLE DATASET STRUCTURE DEBUG")
    print("="*60)

    debug_hotels()
    debug_restaurants()
    debug_activities()

    print("\n" + "="*60)
    print("✅ Debug complete! Check column names above.")
    print("="*60 + "\n")
