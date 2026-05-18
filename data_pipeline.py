"""
Data Pipeline: Download, Clean, Normalize REAL Data for ChromaDB

This module handles:
1. Downloading REAL datasets from Kaggle
2. Cleaning and normalizing data
3. Adding metadata for filtering
4. Preparing data for embedding
"""

import os
import pandas as pd
import json
from typing import List, Dict
from pathlib import Path

# Target cities for the demo
TARGET_CITIES = [
    "Berlin", "Paris", "Barcelona", "Amsterdam", "Rome", "London"
]

# Price categories
PRICE_RANGES = {
    "budget": (0, 50),
    "moderate": (50, 100),
    "upscale": (100, 300),
}


def ensure_directories():
    """Create necessary directories."""
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    print("✅ Directories ready: data/raw, data/processed")


def load_kaggle_restaurants() -> pd.DataFrame:
    """
    Load TripAdvisor restaurants from Kaggle.
    Dataset: stefanoleone992/tripadvisor-european-restaurants
    """
    print("\n  📥 Downloading restaurant data from Kaggle...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("stefanoleone992/tripadvisor-european-restaurants")

        csv_files = list(Path(path).glob("**/*.csv"))
        if not csv_files:
            print("    ⚠ No CSV files found, skipping restaurants")
            return pd.DataFrame()

        df_list = []
        for csv_file in csv_files[:1]:  # Use first CSV
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', nrows=1000)
                df_list.append(df)
            except Exception as e:
                print(f"    ⚠ Error reading {csv_file}: {e}")

        if not df_list:
            print("    ⚠ Could not read restaurant files")
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)

        rows = []
        for _, row in df.iterrows():
            # Use correct column names from actual dataset
            name = str(row.get("restaurant_name", "")).strip()
            city = str(row.get("city", "")).strip()
            cuisines = str(row.get("cuisines", "")).strip()
            rating = row.get("avg_rating", 4.0)
            price_level = str(row.get("price_level", "€")).strip()

            # Extract just the city name (may have country info)
            city_found = None
            for target_city in TARGET_CITIES:
                if target_city.lower() in city.lower():
                    city_found = target_city
                    break

            # Filter for target cities
            if not name or not city_found:
                continue

            # Estimate price from price level
            price_eur = len(price_level) * 15 if price_level else 25.0

            description = f"Restaurant: {name}. Cuisine: {cuisines}. Price Level: {price_level}"

            rows.append({
                "city": city_found,
                "name": name,
                "type": "restaurant",
                "price_eur": price_eur,
                "rating": float(rating) if rating else 4.0,
                "description": description,
                "source": "tripadvisor_restaurants"
            })

        result = pd.DataFrame(rows)
        print(f"    ✓ Restaurants: {len(result)} records")
        return result

    except Exception as e:
        print(f"    ✗ Error loading restaurants: {e}")
        return pd.DataFrame()


def load_kaggle_hotels() -> pd.DataFrame:
    """
    Load REAL hotel data from Datafiniti hotel reviews.
    Dataset: datafiniti/hotel-reviews
    """
    print("\n  📥 Downloading hotel data from Kaggle...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("datafiniti/hotel-reviews")

        csv_files = list(Path(path).glob("**/*.csv"))
        if not csv_files:
            print("    ⚠ No CSV files found, falling back to sample hotels")
            return create_hotel_data()

        df_list = []
        for csv_file in csv_files[:1]:  # Use first CSV
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', nrows=500)
                df_list.append(df)
            except Exception as e:
                print(f"    ⚠ Error reading {csv_file}: {e}")

        if not df_list:
            print("    ⚠ Could not read hotel files, falling back to sample hotels")
            return create_hotel_data()

        df = pd.concat(df_list, ignore_index=True)

        rows = []
        for _, row in df.iterrows():
            # Extract relevant fields from hotel reviews dataset
            name = str(row.get("name", "")).strip()
            city = str(row.get("city", "")).strip()
            rating = row.get("rating", 4.0)
            price = row.get("price", None)

            # Extract city name if it contains country info
            city_found = None
            for target_city in TARGET_CITIES:
                if target_city.lower() in city.lower():
                    city_found = target_city
                    break

            if not name or not city_found:
                continue

            # Estimate price if not available
            if pd.isna(price) or price is None:
                price_eur = 60.0  # Default mid-range price
            else:
                try:
                    price_eur = float(price) if isinstance(price, (int, float)) else 60.0
                except:
                    price_eur = 60.0

            description = f"Hotel: {name}. City: {city_found}. Rating: {rating}/5"

            rows.append({
                "city": city_found,
                "name": name,
                "type": "hotel",
                "price_eur": price_eur,
                "rating": float(rating) if rating else 4.0,
                "description": description,
                "source": "datafiniti_hotels"
            })

        result = pd.DataFrame(rows)
        if len(result) > 0:
            print(f"    ✓ Hotels: {len(result)} records from Datafiniti")
            return result
        else:
            print("    ⚠ No hotel records extracted, falling back to sample hotels")
            return create_hotel_data()

    except Exception as e:
        print(f"    ✗ Error loading hotels: {e}")
        print("    ℹ Falling back to alternate datasets")
        return pd.DataFrame()


def load_tbo_hotels() -> pd.DataFrame:
    """
    Load hotel data from TBO Hotels dataset.
    Dataset: raj713335/tbo-hotels-dataset
    """
    print("\n  📥 Downloading TBO hotels dataset...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("raj713335/tbo-hotels-dataset")

        csv_files = list(Path(path).glob("**/*.csv"))
        if not csv_files:
            print("    ⚠ No CSV files found in TBO dataset")
            return pd.DataFrame()

        df_list = []
        for csv_file in csv_files[:1]:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', nrows=300)
                df_list.append(df)
            except Exception as e:
                print(f"    ⚠ Error reading {csv_file}: {e}")

        if not df_list:
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)
        rows = []

        for _, row in df.iterrows():
            name = str(row.get("name", "") or row.get("hotel_name", "")).strip()
            city = str(row.get("city", "") or row.get("location", "")).strip()
            rating = row.get("rating", row.get("avg_rating", 4.0))
            price = row.get("price", row.get("avg_price", None))

            city_found = None
            for target_city in TARGET_CITIES:
                if target_city.lower() in city.lower():
                    city_found = target_city
                    break

            if not name or not city_found:
                continue

            try:
                price_eur = float(price) if pd.notna(price) else 65.0
            except:
                price_eur = 65.0

            rows.append({
                "city": city_found,
                "name": name,
                "type": "hotel",
                "price_eur": price_eur,
                "rating": float(rating) if pd.notna(rating) else 4.0,
                "description": f"Hotel: {name} in {city_found}",
                "source": "tbo_hotels"
            })

        result = pd.DataFrame(rows)
        if len(result) > 0:
            print(f"    ✓ TBO Hotels: {len(result)} records")
        return result

    except Exception as e:
        print(f"    ✗ Error loading TBO hotels: {e}")
        return pd.DataFrame()


def load_booking_hotels() -> pd.DataFrame:
    """
    Load hotel data from Hotel Booking Dataset.
    Dataset: abdulmannann/hotel-booking-dataset-csv
    """
    print("\n  📥 Downloading booking hotels dataset...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("abdulmannann/hotel-booking-dataset-csv")

        csv_files = list(Path(path).glob("**/*.csv"))
        if not csv_files:
            print("    ⚠ No CSV files found in booking dataset")
            return pd.DataFrame()

        df_list = []
        for csv_file in csv_files[:1]:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', nrows=300)
                df_list.append(df)
            except Exception as e:
                print(f"    ⚠ Error reading {csv_file}: {e}")

        if not df_list:
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)
        rows = []

        for _, row in df.iterrows():
            name = str(row.get("hotel_name", "") or row.get("name", "")).strip()
            city = str(row.get("city", "") or row.get("location", "")).strip()
            rating = row.get("hotel_rating", row.get("rating", 4.0))
            price = row.get("adr", row.get("price", None))  # ADR = Average Daily Rate

            city_found = None
            for target_city in TARGET_CITIES:
                if target_city.lower() in city.lower():
                    city_found = target_city
                    break

            if not name or not city_found:
                continue

            try:
                price_eur = float(price) if pd.notna(price) else 70.0
            except:
                price_eur = 70.0

            rows.append({
                "city": city_found,
                "name": name,
                "type": "hotel",
                "price_eur": price_eur,
                "rating": float(rating) if pd.notna(rating) else 4.0,
                "description": f"Hotel: {name} in {city_found}",
                "source": "booking_hotels"
            })

        result = pd.DataFrame(rows)
        if len(result) > 0:
            print(f"    ✓ Booking Hotels: {len(result)} records")
        return result

    except Exception as e:
        print(f"    ✗ Error loading booking hotels: {e}")
        return pd.DataFrame()


def create_hotel_data() -> pd.DataFrame:
    """
    Create sample hotel data for target cities.
    Supplementary data since Kaggle hotel dataset lacks city/name info.
    """
    print("\n  ✏️  Creating hotel data...")

    hotels = [
        # Berlin
        {"city": "Berlin", "name": "Hotel Berlin Central", "price_eur": 45, "rating": 4.2, "description": "3-star hotel near Brandenburg Gate with comfortable rooms and good breakfast"},
        {"city": "Berlin", "name": "Hostel Berliner Mitte", "price_eur": 25, "rating": 4.0, "description": "Budget hostel in the heart of Berlin, great for backpackers"},
        {"city": "Berlin", "name": "Adlon Kempinski", "price_eur": 250, "rating": 4.8, "description": "Luxury 5-star hotel with historic charm and top service"},

        # Paris
        {"city": "Paris", "name": "Hotel du Marais", "price_eur": 40, "rating": 4.3, "description": "Charming 3-star hotel in the vibrant Marais district"},
        {"city": "Paris", "name": "Hostel du Marais", "price_eur": 28, "rating": 4.1, "description": "Social hostel with communal kitchen and rooftop terrace"},
        {"city": "Paris", "name": "Ritz Paris", "price_eur": 300, "rating": 4.9, "description": "Ultra-luxury palace hotel on Place Vendôme"},

        # Barcelona
        {"city": "Barcelona", "name": "Hotel Sagrada Familia", "price_eur": 50, "rating": 4.4, "description": "Modern 3-star hotel near the iconic Sagrada Familia"},
        {"city": "Barcelona", "name": "Barcelona Backpackers", "price_eur": 30, "rating": 4.2, "description": "Lively hostel with great social atmosphere"},
        {"city": "Barcelona", "name": "Mandarin Oriental Barcelona", "price_eur": 280, "rating": 4.9, "description": "Luxury seaside hotel with Michelin-starred dining"},

        # Amsterdam
        {"city": "Amsterdam", "name": "Canal House Amsterdam", "price_eur": 55, "rating": 4.5, "description": "Charming 3-star hotel in a converted canal palace"},
        {"city": "Amsterdam", "name": "ClinkNOORD Hostel", "price_eur": 35, "rating": 4.3, "description": "Hip hostel with great bar and views over the Amstel River"},
        {"city": "Amsterdam", "name": "Waldorf Astoria Amsterdam", "price_eur": 350, "rating": 4.9, "description": "Ultra-luxury hotel in six connected canal palaces"},

        # Rome
        {"city": "Rome", "name": "Hotel Colonna", "price_eur": 48, "rating": 4.3, "description": "Comfortable 3-star hotel near the Colosseum"},
        {"city": "Rome", "name": "The Yellow Hostel", "price_eur": 32, "rating": 4.1, "description": "Budget-friendly hostel with prime location near Forum"},
        {"city": "Rome", "name": "Hotel Eden", "price_eur": 280, "rating": 4.8, "description": "Luxury 5-star hotel with rooftop bar overlooking the city"},

        # London
        {"city": "London", "name": "Hotel Premier London", "price_eur": 60, "rating": 4.4, "description": "3-star hotel in vibrant Shoreditch with modern amenities"},
        {"city": "London", "name": "Travelodge London", "price_eur": 50, "rating": 4.0, "description": "Budget hotel near Oxford Street with clean rooms"},
        {"city": "London", "name": "Claridge's", "price_eur": 320, "rating": 4.9, "description": "Iconic luxury hotel in Mayfair with impeccable service"},
    ]

    result = pd.DataFrame(hotels)
    result["type"] = "hotel"
    result["source"] = "manual_hotels"
    print(f"    ✓ Hotels: {len(result)} records")
    return result


def create_activity_data() -> pd.DataFrame:
    """
    Create sample activity data for target cities.
    """
    print("\n  ✏️  Creating activity data...")

    activities = [
        # Berlin
        {"city": "Berlin", "name": "Brandenburg Gate Tour", "price_eur": 15, "rating": 4.6, "description": "Guided tour of Berlin's most iconic landmark with historical insights"},
        {"city": "Berlin", "name": "Berlin Wall Memorial Visit", "price_eur": 0, "rating": 4.7, "description": "Free visit to the East Side Gallery - the longest remaining Berlin Wall section"},

        # Paris
        {"city": "Paris", "name": "Louvre Museum Ticket", "price_eur": 20, "rating": 4.8, "description": "Entry to the world's most famous art museum with the Mona Lisa"},
        {"city": "Paris", "name": "Eiffel Tower Visit", "price_eur": 18, "rating": 4.7, "description": "Ascend the iconic iron tower for breathtaking Paris views"},

        # Barcelona
        {"city": "Barcelona", "name": "Sagrada Familia Tour", "price_eur": 25, "rating": 4.7, "description": "Guided visit to Gaudí's masterpiece with architectural details explained"},
        {"city": "Barcelona", "name": "Park Güell Entrance", "price_eur": 16, "rating": 4.6, "description": "Colorful hilltop park with stunning city views and mosaic art"},

        # Amsterdam
        {"city": "Amsterdam", "name": "Anne Frank House", "price_eur": 16, "rating": 4.8, "description": "Moving museum dedicated to Anne Frank's life during WWII"},
        {"city": "Amsterdam", "name": "Canal Boat Cruise", "price_eur": 18, "rating": 4.5, "description": "Scenic cruise through Amsterdam's picturesque canal system"},

        # Rome
        {"city": "Rome", "name": "Colosseum Tour", "price_eur": 18, "rating": 4.7, "description": "Ancient amphitheater tour with gladiator history and underground tunnels"},
        {"city": "Rome", "name": "Vatican Museums & Sistine Chapel", "price_eur": 22, "rating": 4.8, "description": "One of the world's greatest art collections and Michelangelo's masterpiece"},

        # London
        {"city": "London", "name": "Tower of London", "price_eur": 30, "rating": 4.6, "description": "Historic fortress with Crown Jewels and royal history"},
        {"city": "London", "name": "Big Ben & Houses of Parliament", "price_eur": 20, "rating": 4.5, "description": "Iconic Gothic architecture and guided tour of British Parliament"},
    ]

    result = pd.DataFrame(activities)
    result["type"] = "activity"
    result["source"] = "manual_activities"
    print(f"    ✓ Activities: {len(result)} records")
    return result


def load_kaggle_flights() -> pd.DataFrame:
    """
    Load REAL flight data from Kaggle.
    Dataset: weil41/flights
    """
    print("\n  📥 Downloading flights data from Kaggle...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("weil41/flights")

        csv_files = list(Path(path).glob("**/*.csv"))
        if not csv_files:
            print("    ⚠ No CSV files found in flights dataset")
            return pd.DataFrame()

        df_list = []
        for csv_file in csv_files[:1]:  # Use first CSV
            try:
                df = pd.read_csv(csv_file, encoding='utf-8', nrows=500)
                df_list.append(df)
            except Exception as e:
                print(f"    ⚠ Error reading {csv_file}: {e}")

        if not df_list:
            print("    ⚠ Could not read flights files")
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)
        rows = []

        for _, row in df.iterrows():
            # Extract origin and destination cities
            origin = str(row.get("origin", "") or row.get("Origin", "") or row.get("ORIGIN_CITY_NAME", "")).strip()
            dest = str(row.get("destination", "") or row.get("Dest", "") or row.get("DEST_CITY_NAME", "")).strip()

            # Extract price/fare (different datasets use different column names)
            price = row.get("price", row.get("fare", row.get("Fare", None)))

            # Find matching target cities
            origin_found = None
            dest_found = None

            for target_city in TARGET_CITIES:
                if target_city.lower() in origin.lower():
                    origin_found = target_city
                if target_city.lower() in dest.lower():
                    dest_found = target_city

            # Skip if we can't find both cities or if same city
            if not origin_found or not dest_found or origin_found == dest_found:
                continue

            # Estimate price if not available
            if pd.isna(price) or price is None:
                price_eur = 65.0  # Default flight price
            else:
                try:
                    price_eur = float(price) if isinstance(price, (int, float)) else 65.0
                except:
                    price_eur = 65.0

            # Clamp price to reasonable range
            price_eur = max(20, min(500, price_eur))

            rows.append({
                "city": origin_found,
                "name": f"Flight: {origin_found} → {dest_found}",
                "type": "transport",
                "price_eur": price_eur,
                "rating": 4.3,
                "description": f"Flight from {origin_found} to {dest_found}",
                "source": "kaggle_flights"
            })

        # Remove duplicates and keep unique routes
        result_df = pd.DataFrame(rows)
        if not result_df.empty:
            result_df = result_df.drop_duplicates(subset=["city", "name"])
            print(f"    ✓ Flights: {len(result_df)} real flight routes")
            return result_df

        return pd.DataFrame()

    except Exception as e:
        print(f"    ✗ Error loading flights: {e}")
        return pd.DataFrame()


def create_restaurant_data() -> pd.DataFrame:
    """
    Create comprehensive restaurant data with REAL restaurant names per city.
    This provides the detailed dining options needed for itineraries.
    """
    print("\n  ✏️  Creating restaurant data with real names...")

    restaurants = [
        # BERLIN
        {"city": "Berlin", "name": "Curry 36", "cuisine": "German/Street Food", "neighborhood": "Kreuzberg", "price_eur": 8, "rating": 4.6, "description": "Famous currywurst stand - iconic Berlin street food"},
        {"city": "Berlin", "name": "Tim Raue", "cuisine": "Asian Fusion", "neighborhood": "Mitte", "price_eur": 120, "rating": 4.8, "description": "Michelin-starred restaurant with creative Asian cuisine"},
        {"city": "Berlin", "name": "Zur Letzten Instanz", "cuisine": "German", "neighborhood": "Mitte", "price_eur": 25, "rating": 4.5, "description": "Historic restaurant (1525) serving traditional Berlin cuisine"},
        {"city": "Berlin", "name": "Markthalle Neun", "cuisine": "International", "neighborhood": "Friedrichshain", "price_eur": 15, "rating": 4.4, "description": "Street food market with international cuisines"},
        {"city": "Berlin", "name": "Prater Garten", "cuisine": "German", "neighborhood": "Prenzlauer Berg", "price_eur": 18, "rating": 4.3, "description": "Berlin's oldest beer garden with traditional Bavarian fare"},

        # PARIS
        {"city": "Paris", "name": "L'As du Fallafel", "cuisine": "Middle Eastern", "neighborhood": "Marais", "price_eur": 12, "rating": 4.7, "description": "Famous fallafel spot on Rue des Rosiers - Paris institution"},
        {"city": "Paris", "name": "L'Astrance", "cuisine": "French", "neighborhood": "Passy", "price_eur": 150, "rating": 4.9, "description": "3 Michelin stars - innovative French haute cuisine"},
        {"city": "Paris", "name": "Café de Flore", "cuisine": "French", "neighborhood": "Saint-Germain", "price_eur": 35, "rating": 4.4, "description": "Historic literary café - perfect for people watching"},
        {"city": "Paris", "name": "L'Ami Jean", "cuisine": "French", "neighborhood": "Montagne Sainte-Geneviève", "price_eur": 28, "rating": 4.6, "description": "Cozy bistro with traditional French dishes"},
        {"city": "Paris", "name": "Du Pain et des Idées", "cuisine": "Bakery", "neighborhood": "Canal Saint-Martin", "price_eur": 6, "rating": 4.8, "description": "Best croissants and pastries in Paris"},

        # BARCELONA
        {"city": "Barcelona", "name": "Can Culleretes", "cuisine": "Catalan", "neighborhood": "Barri Gòtic", "price_eur": 32, "rating": 4.5, "description": "Oldest restaurant in Barcelona (1786) - traditional Catalan"},
        {"city": "Barcelona", "name": "Tickets Bar", "cuisine": "Spanish Tapas", "neighborhood": "Parallel", "price_eur": 80, "rating": 4.8, "description": "Molecular gastronomy tapas - highly innovative"},
        {"city": "Barcelona", "name": "La Boqueria Market", "cuisine": "Market Food", "neighborhood": "Las Ramblas", "price_eur": 18, "rating": 4.5, "description": "Famous food market with fresh seafood and local specialties"},
        {"city": "Barcelona", "name": "Cervecería Catalana", "cuisine": "Spanish Tapas", "neighborhood": "Eixample", "price_eur": 25, "rating": 4.6, "description": "Popular tapas bar with excellent wine selection"},
        {"city": "Barcelona", "name": "Pujol", "cuisine": "Catalan", "neighborhood": "Sant Antoni", "price_eur": 95, "rating": 4.7, "description": "Contemporary Catalan cuisine with cultural twist"},

        # AMSTERDAM
        {"city": "Amsterdam", "name": "De Kas", "cuisine": "French", "neighborhood": "Oost", "price_eur": 110, "rating": 4.8, "description": "Michelin-starred restaurant in a historic glasshouse"},
        {"city": "Amsterdam", "name": "Stroopwafels", "cuisine": "Dutch Dessert", "neighborhood": "Albert Cuyp Market", "price_eur": 3, "rating": 4.7, "description": "Sweet waffle sandwich - iconic Dutch treat"},
        {"city": "Amsterdam", "name": "Pancakes Amsterdam", "cuisine": "Dutch", "neighborhood": "Centrum", "price_eur": 12, "rating": 4.5, "description": "Traditional Dutch pancakes (savory and sweet)"},
        {"city": "Amsterdam", "name": "Café de jaren", "cuisine": "Dutch", "neighborhood": "Centrum", "price_eur": 20, "rating": 4.4, "description": "Waterfront café with traditional Dutch food"},
        {"city": "Amsterdam", "name": "Café de Reiger", "cuisine": "International", "neighborhood": "Jordaan", "price_eur": 28, "rating": 4.6, "description": "Cozy neighborhood spot with Mediterranean influences"},

        # ROME
        {"city": "Rome", "name": "Flavio al Velavevodetto", "cuisine": "Roman", "neighborhood": "Monti", "price_eur": 45, "rating": 4.6, "description": "Traditional Roman cuisine in historic Monti district"},
        {"city": "Rome", "name": "Il Sorpasso", "cuisine": "Italian", "neighborhood": "Via Properzio", "price_eur": 32, "rating": 4.5, "description": "Modern Italian with vintage Roman atmosphere"},
        {"city": "Rome", "name": "Cacio e Pepe", "cuisine": "Roman", "neighborhood": "Trastevere", "price_eur": 15, "rating": 4.7, "description": "Famous Roman pasta dish (cheese and pepper) - iconic"},
        {"city": "Rome", "name": "Sora Lella", "cuisine": "Roman", "neighborhood": "Isola Tiberina", "price_eur": 50, "rating": 4.6, "description": "Historic Roman trattoria with traditional dishes"},
        {"city": "Rome", "name": "Gelato di San Crispino", "cuisine": "Dessert", "neighborhood": "Trevi", "price_eur": 5, "rating": 4.8, "description": "Award-winning gelato near Trevi Fountain"},

        # LONDON
        {"city": "London", "name": "Borough Market", "cuisine": "Street Food", "neighborhood": "Southwark", "price_eur": 18, "rating": 4.6, "description": "Historic food market with international cuisines"},
        {"city": "London", "name": "The Ledbury", "cuisine": "French", "neighborhood": "Notting Hill", "price_eur": 140, "rating": 4.8, "description": "Michelin-starred French cuisine in Notting Hill"},
        {"city": "London", "name": "Fish & Chips @ Poppies", "cuisine": "British", "neighborhood": "Spitalfields", "price_eur": 16, "rating": 4.5, "description": "Classic British fish and chips - must try"},
        {"city": "London", "name": "Dishoom", "cuisine": "Indian", "neighborhood": "Covent Garden", "price_eur": 28, "rating": 4.7, "description": "Popular Indian restaurant with Bombay vibes"},
        {"city": "London", "name": "Sketch", "cuisine": "French", "neighborhood": "Mayfair", "price_eur": 120, "rating": 4.6, "description": "Artistic fine dining with stunning Michelin experience"},
    ]

    result = pd.DataFrame(restaurants)
    result["type"] = "restaurant"
    result["source"] = "manual_restaurants"
    print(f"    ✓ Restaurants: {len(result)} records with real names per city")
    return result


def create_transport_data() -> pd.DataFrame:
    """
    Create fallback transport data between target cities.
    Used if real flight data is unavailable.
    """
    print("\n  ✏️  Creating fallback transport routes...")

    transport_routes = [
        {"from_city": "Berlin", "to_city": "Paris", "transport_type": "FlixBus", "price_eur": 40, "duration_hours": 14},
        {"from_city": "Berlin", "to_city": "Paris", "transport_type": "Train", "price_eur": 80, "duration_hours": 10},
        {"from_city": "Berlin", "to_city": "Amsterdam", "transport_type": "FlixBus", "price_eur": 30, "duration_hours": 8},
        {"from_city": "Berlin", "to_city": "Barcelona", "transport_type": "Flight", "price_eur": 70, "duration_hours": 3},
        {"from_city": "Paris", "to_city": "Barcelona", "transport_type": "Flight", "price_eur": 55, "duration_hours": 2.5},
        {"from_city": "Paris", "to_city": "Barcelona", "transport_type": "FlixBus", "price_eur": 45, "duration_hours": 16},
        {"from_city": "Paris", "to_city": "Amsterdam", "transport_type": "Train", "price_eur": 75, "duration_hours": 4},
        {"from_city": "Paris", "to_city": "Rome", "transport_type": "Flight", "price_eur": 60, "duration_hours": 2},
        {"from_city": "Barcelona", "to_city": "Amsterdam", "transport_type": "Flight", "price_eur": 70, "duration_hours": 3},
        {"from_city": "Barcelona", "to_city": "Rome", "transport_type": "Flight", "price_eur": 75, "duration_hours": 2.5},
        {"from_city": "Barcelona", "to_city": "London", "transport_type": "Flight", "price_eur": 65, "duration_hours": 2},
        {"from_city": "Amsterdam", "to_city": "Rome", "transport_type": "Flight", "price_eur": 85, "duration_hours": 2.5},
        {"from_city": "Amsterdam", "to_city": "London", "transport_type": "Train", "price_eur": 100, "duration_hours": 6},
        {"from_city": "Rome", "to_city": "London", "transport_type": "Flight", "price_eur": 75, "duration_hours": 2.5},
    ]

    rows = []
    for route in transport_routes:
        rows.append({
            "city": route["from_city"],
            "name": f"{route['transport_type']}: {route['from_city']} → {route['to_city']}",
            "type": "transport",
            "price_eur": route["price_eur"],
            "rating": 4.2,
            "description": f"Travel from {route['from_city']} to {route['to_city']} via {route['transport_type']} ({route['duration_hours']}h)",
            "source": "manual_transport"
        })

    result = pd.DataFrame(rows)
    print(f"    ✓ Fallback transport: {len(result)} routes")
    return result


def load_all_real_data() -> Dict[str, pd.DataFrame]:
    """
    Load all data: REAL restaurants, hotels, and flights from Kaggle + supplementary activities/fallback transport.
    """
    print("\n" + "="*60)
    print("LOADING REAL & SUPPLEMENTARY DATASETS")
    print("="*60)

    all_data = {}

    # Load REAL restaurant data from Kaggle
    restaurants = load_kaggle_restaurants()
    if restaurants.empty:
        print("\n  ⚠ No restaurant data from Kaggle, using comprehensive restaurant fallback")
        restaurants = create_restaurant_data()

    all_data["restaurants"] = restaurants

    # Load REAL hotel data - try multiple datasets
    print("\n  🏨 Loading hotel data from multiple sources...")
    hotels = pd.DataFrame()

    # Try Datafiniti first
    datafiniti_hotels = load_kaggle_hotels()
    if not datafiniti_hotels.empty:
        hotels = pd.concat([hotels, datafiniti_hotels], ignore_index=True)

    # Try TBO Hotels
    tbo_hotels = load_tbo_hotels()
    if not tbo_hotels.empty:
        hotels = pd.concat([hotels, tbo_hotels], ignore_index=True)

    # Try Booking Hotels
    booking_hotels = load_booking_hotels()
    if not booking_hotels.empty:
        hotels = pd.concat([hotels, booking_hotels], ignore_index=True)

    # Fall back to synthetic if no real data
    if hotels.empty:
        print("\n  ⚠ No real hotel data found, using supplementary data")
        hotels = create_hotel_data()

    all_data["hotels"] = hotels

    activities = create_activity_data()
    all_data["activities"] = activities

    # Load REAL flight data from Kaggle
    print("\n  ✈️  Loading flight data from Kaggle...")
    flights = load_kaggle_flights()
    if not flights.empty:
        all_data["transport"] = flights
    else:
        # Fall back to synthetic transport if no real flights available
        print("\n  ⚠ No real flight data found, using fallback routes")
        all_data["transport"] = create_transport_data()

    print(f"\n✓ Total real records loaded: {sum(len(df) for df in all_data.values())}")

    return all_data


def clean_and_normalize(all_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Clean and normalize all datasets into a single DataFrame.
    """
    print("\n[Data Cleaning & Normalization]")

    frames = []

    for key, df in all_data.items():
        if df.empty:
            continue

        # Standardize columns
        df_clean = df[["city", "name", "type", "price_eur", "rating", "description", "source"]].copy()

        # Data cleaning
        df_clean = df_clean.dropna(subset=["city", "name", "description"])
        df_clean = df_clean[df_clean["city"].isin(TARGET_CITIES)]
        df_clean = df_clean.drop_duplicates(subset=["city", "name"])

        frames.append(df_clean)
        print(f"  ✓ {key.capitalize()}: {len(df_clean)} records")

    # Combine
    df_combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    print(f"  ✓ Combined: {len(df_combined)} total records")

    return df_combined


def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add metadata columns for filtering in ChromaDB.
    """
    print("\n[Adding Metadata]")

    # Add price range category
    def get_price_range(price):
        for range_name, (min_p, max_p) in PRICE_RANGES.items():
            if min_p <= price < max_p:
                return range_name
        return "luxury"

    df["price_range"] = df["price_eur"].apply(get_price_range)
    df["rating"] = df["rating"].fillna(4.0).astype(float)

    print(f"  ✓ Added price_range and normalized ratings")

    return df


def create_text_chunks(df: pd.DataFrame) -> List[Dict]:
    """
    Create text chunks with metadata for ChromaDB.
    """
    print("\n[Creating Text Chunks]")

    chunks = []

    for _, row in df.iterrows():
        text = f"""
Name: {row['name']}
Type: {row['type'].title()}
City: {row['city']}
Rating: {row['rating']}/5
Price: €{row['price_eur']}
Price Range: {row['price_range'].title()}

Description: {row['description']}
""".strip()

        metadata = {
            "city": row["city"],
            "type": row["type"],
            "price_eur": float(row["price_eur"]),
            "price_range": row["price_range"],
            "rating": float(row["rating"]),
            "source": row["source"],
            "name": row["name"]
        }

        chunks.append({
            "text": text,
            "metadata": metadata
        })

    print(f"  ✓ Created {len(chunks)} chunks for embedding")

    return chunks


def save_processed_data(df: pd.DataFrame):
    """Save processed data to CSV."""
    output_path = "data/processed/travel_data.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Processed data saved to: {output_path}")


def run_pipeline() -> List[Dict]:
    """
    Run the complete data pipeline.
    Real Kaggle restaurants + supplementary hotels/activities/transport.

    Returns: List of text chunks with metadata ready for ChromaDB
    """
    print("\n" + "="*60)
    print("TRAVEL RAG v2 - DATA PIPELINE")
    print("="*60)

    # Step 1: Setup
    ensure_directories()

    # Step 2: Load data (REAL restaurants + supplementary)
    all_data = load_all_real_data()

    if not all_data:
        print("\n❌ ERROR: No data loaded")
        return []

    # Step 3: Clean & normalize
    df_combined = clean_and_normalize(all_data)

    if df_combined.empty:
        print("\n❌ ERROR: No data after cleaning")
        return []

    # Step 4: Add metadata
    df_with_metadata = add_metadata(df_combined)

    # Step 5: Create chunks
    chunks = create_text_chunks(df_with_metadata)

    # Step 6: Save
    save_processed_data(df_with_metadata)

    print("\n" + "="*60)
    print(f"✅ PIPELINE COMPLETE: {len(chunks)} chunks ready for ChromaDB")
    print("="*60 + "\n")

    return chunks


if __name__ == "__main__":
    chunks = run_pipeline()
    if chunks:
        print(f"Sample chunk:\n{json.dumps(chunks[0], indent=2)}")
