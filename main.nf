nextflow.enable.dsl=2

params.synthea_csv = "$projectDir/data/csv/patients.csv"
params.horvarth1_csv = "$projectDir/helper_files/Horvath1.csv"

process GENERATE_PARQUET {
    tag "GENERATE_PARQUET_TAG"

    input:
    path patients_csv
    path horvath1_csv

    path "cpg_matrix.parquet", emit: cpg_matrix_parquet

    script:
    """
    python3 $projectDir/src/01_generate_parquet.py ${patients_csv} ${horvath1_csv} cpg_matrix.parquet
    """
}

process CALCULATE_CLOCK {
    tag "CALCULATE_CLOCK_TAG"

    input:
    path patients_csv
    path cpg_matrix_parquet
    path horvath1_csv

    path "epigenetic_results.csv", emit: epigenetic_results_csv

    script:
    """
    python3 $projectDir/src/02_calculate_clock.py ${patients_csv} ${cpg_matrix_parquet} ${horvath1_csv} epigenetic_results.csv
    """   
}

process LOAD_POSTGRES {
    tag "LOAD_POSTGRES_TAG"

    input:
    path epigenetic_results_csv

    script:
    """
    python3 $projectDir/src/03_load_postgres.py ${epigenetic_results_csv}
    """
}

workflow {
    // Generate Parquet file from Synthea CSV and Horvath1 CSV
    parquet_ch = GENERATE_PARQUET(FILE(params.synthea_csv), FILE(params.horvarth1_csv))

    // Calculate Epigenetic Clock using the generated Parquet file
    results_ch = CALCULATE_CLOCK(FILE(params.synthea_csv), parquet_ch.cpg_matrix_parquet, FILE(params.horvarth1_csv))

    // Load results into PostgreSQL
    LOAD_POSTGRES(results_ch.epigenetic_results_csv)
}