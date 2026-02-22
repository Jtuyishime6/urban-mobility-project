"""
load_trips.py
-------------
Bulk-loads the cleaned trip data into the MySQL 'trips' table.

HOW TO RUN (from the project root):
    python load_trips.py

Prerequisites:
  1. Make sure your database and schema are set up (run schema.sql first).
  2. Make sure yellow_cleaned_tripdata.csv exists in the data/ folder.
  3. Check that database/config.py has the correct DB credentials.

If a previous load was interrupted, the script will report how many rows
already exist and skip the load to avoid duplicates.
To reload from scratch, run this in MySQL first:
    TRUNCATE TABLE trips;
Then re-run this script.
"""

import csv
import os
import sys
import time

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
CLEANED_FILE = os.path.join(BASE_DIR, "data", "yellow_cleaned_tripdata.csv")
BATCH_SIZE   = 5_000

# Add database/ folder to path so we can import config
sys.path.insert(0, os.path.join(BASE_DIR, "database"))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from database import get_db_connection  # backend/database.py


# ── Helpers ───────────────────────────────────────────────────────────────────

def count_existing(conn):
    """Return how many trip rows are already in the table."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS n FROM trips")
    row = cursor.fetchone()
    cursor.close()
    return int(row[0]) if row else 0


def to_none(v):
    """Convert empty strings to None (NULL in DB)."""
    return None if v == "" or v is None else v


# ── Main loader ───────────────────────────────────────────────────────────────

def load_trips(conn, csv_path):
    """
    Loads trips from the cleaned CSV using batched INSERT statements.
    Commits every BATCH_SIZE rows and prints progress.
    """
    print("  Loading trips via batched INSERT...")

    INSERT_SQL = """
        INSERT INTO trips (
            vendor_id, ratecode_id, payment_type_id,
            pickup_location_id, dropoff_location_id,
            pickup_datetime, dropoff_datetime,
            passenger_count, trip_distance, store_and_fwd_flag,
            fare_amount, extra, mta_tax, tip_amount, tolls_amount,
            improvement_surcharge, congestion_surcharge, total_amount,
            trip_duration_minutes, fare_per_mile, pickup_hour,
            is_weekend, avg_speed_mph
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
    """

    cursor = conn.cursor()
    batch  = []
    total  = 0
    start  = time.time()

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total += 1
            batch.append((
                to_none(row.get("VendorID")),
                to_none(row.get("RatecodeID")),
                to_none(row.get("payment_type")),
                to_none(row.get("PULocationID")),
                to_none(row.get("DOLocationID")),
                to_none(row.get("tpep_pickup_datetime")),
                to_none(row.get("tpep_dropoff_datetime")),
                to_none(row.get("passenger_count")) or 1,
                to_none(row.get("trip_distance"))   or 0,
                row.get("store_and_fwd_flag")        or "N",
                to_none(row.get("fare_amount"))      or 0,
                to_none(row.get("extra"))            or 0,
                to_none(row.get("mta_tax"))          or 0,
                to_none(row.get("tip_amount"))       or 0,
                to_none(row.get("tolls_amount"))     or 0,
                to_none(row.get("improvement_surcharge"))  or 0,
                to_none(row.get("congestion_surcharge"))   or 0,
                to_none(row.get("total_amount"))     or 0,
                to_none(row.get("trip_duration_minutes")),
                to_none(row.get("fare_per_mile")),
                to_none(row.get("pickup_hour")),
                to_none(row.get("is_weekend")),
                to_none(row.get("avg_speed_mph")),
            ))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(INSERT_SQL, batch)
                conn.commit()
                batch.clear()
                elapsed = time.time() - start
                print(f"  {total:>10,} rows  |  {total / elapsed:,.0f} rows/sec")

    # Flush remaining rows
    if batch:
        cursor.executemany(INSERT_SQL, batch)
        conn.commit()

    cursor.close()
    elapsed = time.time() - start
    print(f"\n  Done: {total:,} rows in {int(elapsed // 60)}m {elapsed % 60:.1f}s")
    return total


# ── Entry point ───────────────────────────────────────────────────────────────

def run():
    print("=" * 55)
    print("  Trip Data Loader")
    print("=" * 55)

    # Check file exists
    if not os.path.exists(CLEANED_FILE):
        print(f"\n[ERROR] Cleaned data file not found:\n  {CLEANED_FILE}")
        print("\nMake sure yellow_cleaned_tripdata.csv is in the data/ folder.")
        return

    size_mb = os.path.getsize(CLEANED_FILE) / (1024 * 1024)
    print(f"\nFile: {os.path.basename(CLEANED_FILE)} ({size_mb:.1f} MB)")

    # Connect
    print("\nConnecting to database...")
    conn = get_db_connection()

    # Check for existing data
    existing = count_existing(conn)
    if existing > 0:
        print(f"\n[INFO] The trips table already has {existing:,} rows.")
        print("  To reload, run this in MySQL first:")
        print("    TRUNCATE TABLE trips;")
        print("  Then re-run this script.")
        conn.close()
        return

    # Load
    print("\nLoading trips...\n")
    total = load_trips(conn, CLEANED_FILE)

    # Verify
    verify_count = count_existing(conn)
    conn.close()

    print(f"\n{'=' * 55}")
    print(f"  Load complete!")
    print(f"  Rows inserted : {total:,}")
    print(f"  Rows in DB    : {verify_count:,}")
    print(f"{'=' * 55}")
    print("\nNext: start the backend and open the frontend.")
    print("  cd backend && python app.py")


if __name__ == "__main__":
    run()