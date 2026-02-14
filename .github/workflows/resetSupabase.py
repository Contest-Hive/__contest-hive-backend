"""
This script updates the daily statistics and resets the daily statistics to 0 for Supabase.
Untested.
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Database credentials
USER = os.getenv("user", "postgres.uizfbklinelvplmvydba")
PASSWORD = os.getenv("password")
HOST = os.getenv("host", "aws-1-ap-south-1.pooler.supabase.com")
PORT = os.getenv("port", "6543")
DBNAME = os.getenv("dbname", "postgres")

utc_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    cursor = connection.cursor()

    # 1. Ensure the history table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.daily_stats_history (
            date DATE PRIMARY KEY,
            past24api INTEGER,
            past24page INTEGER
        );
    """)

    # 2. Get the current statistics from the production table
    cursor.execute("SELECT past24api, past24page FROM public.stats WHERE id = 1;")
    stats = cursor.fetchone()

    if stats:
        past24api_val, past24page_val = stats[0], stats[1]

        # 3. Update/Upsert the daily statistics history table
        upsert_query = """
        INSERT INTO public.daily_stats_history (date, past24api, past24page)
        VALUES (%s, %s, %s)
        ON CONFLICT (date) 
        DO UPDATE SET 
            past24api = EXCLUDED.past24api,
            past24page = EXCLUDED.past24page;
        """
        cursor.execute(upsert_query, (utc_date, past24api_val, past24page_val))

        # 4. Reset the daily statistics in the production table
        # Values: past24=1, past24api=1, past24page=2
        reset_query = """
        UPDATE public.stats 
        SET past24 = 1, past24api = 1, past24page = 2 
        WHERE id = 1;
        """
        cursor.execute(reset_query)

        # Commit both operations as a single transaction
        connection.commit()

        print(f"Reset the daily statistics for {utc_date}.")
        print(f"past24api: {past24api_val}")
        print(f"past24page: {past24page_val}")
    else:
        print("Error: No stats found with id = 1 in public.stats.")

except Exception as e:
    print(f"Failed to execute reset: {e}")
    if 'connection' in locals():
        connection.rollback()

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
        print("Connection closed.")
