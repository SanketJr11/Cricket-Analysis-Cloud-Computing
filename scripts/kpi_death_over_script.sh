#!/bin/bash
set -euo pipefail

# --------- EDIT THESE ----------
S3_BUCKET="ipl-kpi-results"
S3_PREFIX="death_runrate"   # folder path inside bucket
PY_SCRIPT="$HOME/scripts/kpi_death_overs_runrate.py"

OUT1="$HOME/outputs/kpi_death_overs_runrate.csv"
OUT2="$HOME/outputs/kpi_death_overs_runrate_complete_only.csv"
# ------------------------------

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

# Ensure outputs exist
if [[ ! -f "$OUT1" ]]; then
  echo "ERROR: Missing output file: $OUT1" | tee -a "$LOG_FILE"
  exit 1
fi

if [[ ! -f "$OUT2" ]]; then
  echo "ERROR: Missing output file: $OUT2" | tee -a "$LOG_FILE"
  exit 1
fi

# Upload ONLY this run's files
aws s3 cp "$LOG_FILE" "${S3_BASE}/logs/death_run.log"
aws s3 cp "$OUT1"     "${S3_BASE}/outputs/kpi_death_overs_runrate.csv"
aws s3 cp "$OUT2"     "${S3_BASE}/outputs/kpi_death_overs_runrate_complete_only.csv"

# Verify
echo "Uploaded files:"
aws s3 ls "${S3_BASE}/" --recursive

echo "DONE. Run folder: ${S3_BASE}/"