import pandas as pd
import numpy as np
from pathlib import Path

INPUT_CSV = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/data/ball_by_ball_ipl.csv")
OUTPUT_DIR = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

OUT_ALL = OUTPUT_DIR / "kpi_powerplay_runrate.csv"
OUT_COMPLETE = OUTPUT_DIR / "kpi_powerplay_runrate_complete_only.csv"

df = pd.read_csv(INPUT_CSV)

# Batting team depends on innings
df["batting_team"] = np.where(df["Innings"] == 1, df["Bat First"], df["Bat Second"])

# Powerplay overs = 1–6, valid balls only
pp = df[(df["Over"] >= 1) & (df["Over"] <= 6) & (df["Valid Ball"] == 1)].copy()

agg = (
    pp.groupby(["Match ID", "Innings", "batting_team"], as_index=False)
      .agg(
          pp_runs=("Runs From Ball", "sum"),
          pp_balls=("Valid Ball", "sum"),
      )
)

agg["pp_overs"] = agg["pp_balls"] / 6.0
agg["pp_run_rate"] = agg["pp_runs"] / agg["pp_overs"]

# Stable view: full powerplay has 36 valid balls
agg_complete = agg[agg["pp_balls"] >= 36].copy()

agg.to_csv(OUT_ALL, index=False)
agg_complete.to_csv(OUT_COMPLETE, index=False)

print("Saved:", OUT_ALL)
print("Saved:", OUT_COMPLETE)
print("\nTop 10 powerplay run rates (all cases):")
print(agg.sort_values("pp_run_rate", ascending=False).head(10))
print("\nTop 10 powerplay run rates (complete only, >=36 balls):")
print(agg_complete.sort_values("pp_run_rate", ascending=False).head(10))