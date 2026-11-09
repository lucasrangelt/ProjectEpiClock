import sys
import duckdb
import numpy as np

patients_csv = sys.argv[1]
cpg_matrix_parquet = sys.argv[2]
horvath1_csv = sys.argv[3]
epigenetic_results_csv = sys.argv[4]
intercept = 0.696186304

con = duckdb.connect()

def horvath_anti_tranformation(raw_score, adult_age=20): #converts invert transformation function to biological age in years.
    return np.where(raw_score < 0, (1.0 + adult_age) * np.exp(raw_score) - 1.0, (1.0 + adult_age) * raw_score + adult_age)

df_epigenetic_results = con.execute(f"""
    WITH horvath_probes AS (
        SELECT CpGmarker AS cpg_id, CoefficientTraining AS weight
        FROM '{horvath1_csv}'
    ),
    patient_ages AS (
        SELECT
            Id AS patient_id,
            GENDER as gender,
            DATE_DIFF('year', CAST(BIRTHDATE AS DATE), CURRENT_DATE) AS chronological_age
        FROM
            '{patients_csv}'
    )
    SELECT
        p.patient_id,
        p.gender,
        p.chronological_age,
        SUM(m.beta_value * h.weight) + {intercept} AS raw_score
    FROM (
        SELECT cpg_id, patient_id, beta_value
        FROM '{cpg_matrix_parquet}'
        UNPIVOT (beta_value FOR patient_id IN (COLUMNS(* EXCLUDE (cpg_id))))
    ) m
    INNER JOIN horvath_probes h ON m.cpg_id = h.cpg_id
    INNER JOIN patient_ages p ON m.patient_id = p.patient_id
    GROUP BY p.patient_id, p.gender, p.chronological_age
""").df()

raw_scores = df_epigenetic_results["raw_score"].to_numpy()
df_epigenetic_results["biological_age"] = np.round(horvath_anti_tranformation(raw_scores), 2)
df_epigenetic_results["age_acceleration_delta"] = np.round(df_epigenetic_results["biological_age"] - df_epigenetic_results["chronological_age"], 2)
df_epigenetic_results.drop(columns=["raw_score"], inplace=True)
df_epigenetic_results.to_csv(epigenetic_results_csv, index=False)
con.close()
print("Finished script 2 successfully and created epigenetic_results_csv file")