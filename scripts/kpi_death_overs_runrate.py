import pandas as pd
import numpy as np
from pathlib import Path

INPUT_CSV = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/data/ball_by_ball_ipl.csv")
OUTPUT_DIR = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

OUT_ALL = OUTPUT_DIR / "kpi_death_overs_runrate.csv"
OUT_COMPLETE = OUTPUT_DIR / "kpi_death_overs_runrate_complete_only.csv"

df = pd.read_csv(INPUT_CSV)

# Derive batting team for each delivery
df["batting_team"] = np.where(df["Innings"] == 1, df["Bat First"], df["Bat Second"])

# Death overs: 16–20, valid balls only
death = df[(df["Over"] >= 16) & (df["Over"] <= 20) & (df["Valid Ball"] == 1)].copy()

agg = (
    death.groupby(["Match ID", "Innings", "batting_team"], as_index=False)
    .agg(death_runs=("Runs From Ball", "sum"),
         death_balls=("Valid Ball", "sum"))
)

agg["death_overs"] = agg["death_balls"] / 6.0
agg["death_run_rate"] = agg["death_runs"] / agg["death_overs"]

# Optional stable view: only full death overs (30 valid balls)
agg_complete = agg[agg["death_balls"] >= 30].copy()

agg.to_csv(OUT_ALL, index=False)
agg_complete.to_csv(OUT_COMPLETE, index=False)

print("Saved:", OUT_ALL)
print("Saved:", OUT_COMPLETE)
print("\nTop 10 (all cases):")
print(agg.sort_values("death_run_rate", ascending=False).head(10))
print("\nTop 10 (complete death overs only, >=30 balls):")
print(agg_complete.sort_values("death_run_rate", ascending=False).head(10))