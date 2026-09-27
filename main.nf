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