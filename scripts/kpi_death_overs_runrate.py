import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------- Paths ----------
INPUT_CSV = Path.home() / "data" / "ball_by_ball_ipl.csv"
OUT_DIR = Path.home() / "outputs"
OUT_DIR.mkdir(exist_ok=True)

OUT_ALL = OUT_DIR / "kpi_death_overs_runrate.csv"
OUT_COMPLETE = OUT_DIR / "kpi_death_overs_runrate_complete_only.csv"

# ---------- Load ----------
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

# Stable view: only full death overs (30 valid balls)
agg_complete = agg[agg["death_balls"] >= 30].copy()

# Save KPI outputs
agg.to_csv(OUT_ALL, index=False)
agg_complete.to_csv(OUT_COMPLETE, index=False)

print("Saved:", OUT_ALL)
print("Saved:", OUT_COMPLETE)

# ---------- Chart helpers ----------
mean_rr = agg_complete["death_run_rate"].mean()
median_rr = agg_complete["death_run_rate"].median()

# 1) Histogram (distribution) + mean/median lines
plt.figure(figsize=(9.5, 5.8))
vals = agg_complete["death_run_rate"].dropna()
plt.hist(vals, bins=30)
plt.axvline(mean_rr, linewidth=2, label=f"Mean = {mean_rr:.2f}")
plt.axvline(median_rr, linewidth=2, label=f"Median = {median_rr:.2f}")
plt.title("Death-overs Run Rate (Overs 16–20): Distribution (Complete death overs only)")
plt.xlabel("Run rate (runs per over)")
plt.ylabel("Count of match-innings-team cases")
plt.legend()
fig1 = OUT_DIR / "fig1_death_runrate_distribution.png"
plt.savefig(fig1, dpi=220, bbox_inches="tight")
plt.close()
print("Saved:", fig1)

# 2) Top 10 teams by average death run rate
team_avg = (
    agg_complete.groupby("batting_team", as_index=False)
    .agg(avg_death_run_rate=("death_run_rate", "mean"),
         matches=("Match ID", "nunique"))
)
team_avg = team_avg[team_avg["matches"] >= 20].sort_values("avg_death_run_rate", ascending=False)
top10 = team_avg.head(10)

plt.figure(figsize=(10, 5.8))
plt.bar(top10["batting_team"], top10["avg_death_run_rate"])
plt.axhline(mean_rr, linewidth=2, label=f"Overall mean = {mean_rr:.2f}")
plt.title("Top 10 Teams by Average Death-overs Run Rate (Overs 16–20)")
plt.xlabel("Team")
plt.ylabel("Average run rate (runs per over)")
plt.xticks(rotation=25, ha="right")
plt.legend()
fig2 = OUT_DIR / "fig2_top10_teams_death_runrate.png"
plt.savefig(fig2, dpi=220, bbox_inches="tight")
plt.close()
print("Saved:", fig2)

# 3) Boxplot: innings 1 vs innings 2
inn1 = agg_complete.loc[agg_complete["Innings"] == 1, "death_run_rate"].dropna()
inn2 = agg_complete.loc[agg_complete["Innings"] == 2, "death_run_rate"].dropna()

plt.figure(figsize=(8.5, 5.8))
plt.boxplot([inn1, inn2], labels=["Innings 1", "Innings 2"], showmeans=True)
plt.title("Death-overs Run Rate by Innings (Boxplot, complete death overs only)")
plt.ylabel("Run rate (runs per over)")
fig3 = OUT_DIR / "fig3_death_runrate_by_innings.png"
plt.savefig(fig3, dpi=220, bbox_inches="tight")
plt.close()
print("Saved:", fig3)

print("\nDone. Outputs saved in:", OUT_DIR)