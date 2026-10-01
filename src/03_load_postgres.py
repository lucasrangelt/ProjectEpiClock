import sys
import os
import pandas as pd
import psycopg2

if len(sys.argv) < 2:
    print("PROVIDE THE PATH TO THE EPIGENETIC RESULT FILE AS AN ARGUMENT")
    sys.exit(1)
results_csv = sys.argv[1]
if not os.path.exists(results_csv):
    print("results_csv not found")
    sys.exit(1)

df = pd.read_csv(results_csv)

con = psycopg2.connect(
    dbname=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    port="5433"
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
    INSERT INTO petient_epigenetic_metrics (
        patient_id,
        gender,
        chronological_age,
        biological_age,
        age_acceleration_delta
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (patient_id) DO UPDATE SET
        gender = EXCLUDED.gender,
        chronological_age = EXCLUDED.chronological_age,
        biological_age = EXCLUDED.biological_age,
        age_acceleration_delta = EXCLUDED.age_acceleration_delta,
        processed_at = CURRENT_TIMESTAMP;
"""

for _, row in df.iterrows():
    cursor.execute(upsert_query,(
        str(row['patient_id']),
        str(row['gender']),
        int(row['chronological_age']),
        float(row['biological_age']),
        float(row['age_acceleration_delta'])
    ))
con.commit()
cursor.close()
con.close()