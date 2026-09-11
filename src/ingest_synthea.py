import duckdb

with duckdb.connect() as my_connection:
    df_patients = my_connection.execute("""
        SELECT
            id AS patient_id,
            gender,
            DATE_DIFF('year', CAST(BIRTHDATE AS DATE), CURRENT_DATE) AS chronological_age
        FROM
            './data/csv/patients.csv'
    """).df()
    
print(df_patients.head())