import duckdb
import pandas as pd
import numpy as np

df_horvath = pd.read_csv("helper_files/Horvath1.csv")
horvath_ids = df_horvath["CpGmarker"].values
intercept = 0.696186304

with duckdb.connect() as my_connection:
    df_patients = my_connection.execute("""
        SELECT
            id AS patient_id,
            gender,
            DATE_DIFF('year', CAST(BIRTHDATE AS DATE), CURRENT_DATE) AS chronological_age
        FROM
            './data/csv/patients.csv'
    """).df()
patient_ids = df_patients['patient_id'].values
ages = df_patients['chronological_age'].values

total_cpgs = 850000
cpgs_remaining = total_cpgs - len(horvath_ids)
filler_cpg_numbers = np.arange(10000000, 10000000 + cpgs_remaining)
filler_cpg_ids = np.char.add("cg", filler_cpg_numbers.astype(str))
all_cpgs = np.concatenate([horvath_ids, filler_cpg_ids])

matrix = np.zeros((total_cpgs, len(patient_ids)), dtype=np.float32)
for i, age in enumerate(ages):
    age_factor = np.clip(age / 100.0, 0, 1)
    matrix[:193, i] = np.clip(0.1 + 0.8 * age_factor + np.random.normal(0, 0.02, 193), 0, 1) # hypermethylated
    matrix[193:353, i] = np.clip(0.9 - 0.8 * age_factor + np.random.normal(0, 0.02, 160), 0, 1) # hypomethylated
matrix[353:, :] = np.random.uniform(0.0, 1.0, size=(len(filler_cpg_ids), len(patient_ids))).astype(np.float32)
df_cpg = pd.DataFrame(matrix, columns=patient_ids)
df_cpg.insert(0, "cpg_id", all_cpgs)

df_cpg.to_parquet("./src/cpg_matrix.parquet", engine="pyarrow", compression="snappy")
print(matrix)
# print(df_patients.head())
# print(df_horvath.head())