import duckdb

my_connection = duckdb.connect()
df_patients = my_connection.execute("""
    SELECT
        id AS patient_id,
        gender,
        DATE_DIFF('year', CAST(birthday AS DATE), CURRENT_DATE) AS chronological_age
    FROM
        './data/csv/patients.csv'
""").df()