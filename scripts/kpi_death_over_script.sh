#!/bin/bash
set -euo pipefail

S3_BUCKET="ipl-kpi-results"
S3_PREFIX="death_runrate"   # folder path inside bucket
PY_SCRIPT="$HOME/scripts/kpi_death_overs_runrate.py"

OUT_CSV_1="$HOME/outputs/kpi_death_overs_runrate.csv"
OUT_CSV_2="$HOME/outputs/kpi_death_overs_runrate_complete_only.csv"

OUT_PNG_1="$HOME/outputs/fig1_death_runrate_distribution.png"
OUT_PNG_2="$HOME/outputs/fig2_top10_teams_death_runrate.png"
OUT_PNG_3="$HOME/outputs/fig3_death_runrate_by_innings.png"

RUN_ID=$(date -u +"%Y%m%d_%H%M%S")
LOG_FILE="$HOME/logs/death_run_${RUN_ID}.log"
S3_BASE="s3://${S3_BUCKET}/${S3_PREFIX}/${RUN_ID}"

mkdir -p "$HOME/logs" "$HOME/outputs"

echo "RUN_ID=$RUN_ID"
echo "Logging to: $LOG_FILE"
echo "Uploading to: $S3_BASE"

# Log start
echo "START: $(date -u '+%Y-%m-%d %H:%M:%S') UTC" | tee "$LOG_FILE"

# Run KPI script (capture stdout+stderr into log)
python3 "$PY_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

# Log end
echo "END:   $(date -u '+%Y-%m-%d %H:%M:%S') UTC" | tee -a "$LOG_FILE"

# Helper: check file exists
check_file () {
  if [[ ! -f "$1" ]]; then
    echo "ERROR: Missing file: $1" | tee -a "$LOG_FILE"
    exit 1
  fi
}

# Check required outputs exist
check_file "$OUT_CSV_1"
check_file "$OUT_CSV_2"
check_file "$OUT_PNG_1"
check_file "$OUT_PNG_2"
check_file "$OUT_PNG_3"

# Upload ONLY this run's files
aws s3 cp "$LOG_FILE" "${S3_BASE}/logs/death_run.log"

aws s3 cp "$OUT_CSV_1" "${S3_BASE}/outputs/$(basename "$OUT_CSV_1")"
aws s3 cp "$OUT_CSV_2" "${S3_BASE}/outputs/$(basename "$OUT_CSV_2")"

aws s3 cp "$OUT_PNG_1" "${S3_BASE}/outputs/$(basename "$OUT_PNG_1")"
aws s3 cp "$OUT_PNG_2" "${S3_BASE}/outputs/$(basename "$OUT_PNG_2")"
aws s3 cp "$OUT_PNG_3" "${S3_BASE}/outputs/$(basename "$OUT_PNG_3")"

# Verify
echo "Uploaded files:"
aws s3 ls "${S3_BASE}/" --recursive

echo "DONE. Run folder: ${S3_BASE}/"