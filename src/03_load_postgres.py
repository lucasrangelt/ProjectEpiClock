import sys
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

if len(sys.argv) < 2:
    print("PROVIDE THE PATH TO THE EPIGENETIC RESULT FILE AS AN ARGUMENT")
    sys.exit(1)
results_csv = sys.argv[1]
if not os.path.exists(results_csv):
    print("results_csv not found")
    sys.exit(1)

load_dotenv()

df = pd.read_csv(results_csv)
df.columns = df.columns.str.lower()
records = [tuple(x) for x in df[['patient_id', 'gender', 'chronological_age', 'biological_age', 'age_acceleration_delta']].to_numpy()]

con = psycopg2.connect(
    dbname=os.environ.get("ENV_DATABASE"),
    user=os.environ.get("ENV_USER"),
    password=os.environ.get("ENV_PASSWORD"),
    host=os.environ.get("ENV_HOST"),
    port=5432
)
cursor = con.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_epigenetic_metrics (
        patient_id VARCHAR(100) PRIMARY KEY,
        gender VARCHAR(10),
        chronological_age INT,
        biological_age FLOAT,
        age_acceleration_delta FLOAT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

upsert_query = """
    INSERT INTO patient_epigenetic_metrics (
        patient_id,
        gender,
        chronological_age,
        biological_age,
        age_acceleration_delta
    )
    VALUES %s
    ON CONFLICT (patient_id) DO UPDATE SET
        gender = EXCLUDED.gender,
        chronological_age = EXCLUDED.chronological_age,
        biological_age = EXCLUDED.biological_age,
        age_acceleration_delta = EXCLUDED.age_acceleration_delta,
        processed_at = CURRENT_TIMESTAMP;
"""

execute_values(cursor, upsert_query, records)
con.commit()
cursor.close()
con.close()

print(f"Bulk loaded {len(records)} patient records into PostgreSQL!")