import sys
import duckdb

patients_csv = sys.argv[1]
cpg_matrix_parquet = sys.argv[2]
horvath1_csv = sys.argv[3]
epigenetic_results_csv = sys.argv[4]
intercept = 0.696186304

con = duckdb.connect()
df_epigenetic_results = con.execute(f"""
    WITH horvath_probes AS (
        SELECT CpGmarker AS cpg_id, Coefficient AS weight
        FROM '{horvath1_csv}'
    ),
    patient_ages AS (
        SELECT patient_id, gender, chronological_age
        FROM '{patients_csv}'
    )
    SELECT
        p.patient_id,
        p.gender,
        p.chronological_age,
        ROUND(SUM(m.beta_value * h.weight) + {intercept}, 2) AS biological_age,
        ROUDN((SUM(m.beta_value * h.weight) + {intercept}) - p.chronological_age, 2) AS age_acceleration_delta
    FROM (
        SELECT cpg_id, patient_id, beta_value
        FROM '{cpg_matrix_parquet}'
        UNPIVOT (beta_value FOR patient_id IN (COLUMNS(* EXCLUDE (cpg_id))))
    ) m
    INNER JOIN horvath_probes h ON m.cpg_id = h.cpg_id
    INNER JOIN patient_ages p ON m.patient_id = p.patient_id
    GROUP BY p.patient_id, p.gender, p.chronological_age
""").df()

df_epigenetic_results.to_csv(epigenetic_results_csv, index=False)
con.close()
print("Finished script 2 successfully and created epigenetic_results_csv file")