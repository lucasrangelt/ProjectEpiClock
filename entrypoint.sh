if [ -f /output/csv/patients.csv ] || [ -f /output/patients.csv ]; then
  echo "Synthea data already exists in /output. Skipping generation..."
  exit 0
else
  echo "No existing synthea data found. Generating fresh biological data..."
  ./run_synthea -p 100 --exporter.csv.export=true --exporter.baseDirectory=/output
fi