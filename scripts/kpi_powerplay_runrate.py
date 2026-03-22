import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#INPUT_CSV = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/data/ball_by_ball_ipl.csv")
INPUT_CSV = Path.home() / "data" / "ball_by_ball_ipl.csv"
# OUT_DIR = Path("/Users/sanket/Cricket-Analysis-Cloud-Computing/outputs")
OUT_DIR = Path.home() / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# ---- EC2 cost parameters (EDIT THESE) ----
EC2_PRICE_PER_HOUR = 0.0208
ALWAYS_ON_HOURS_PER_DAY = 24.0
ON_DEMAND_HOURS_PER_DAY = 0.75  # (startup + runtime)/60

df = pd.read_csv(INPUT_CSV)

# Batting team depends on innings
df["batting_team"] = np.where(df["Innings"] == 1, df["Bat First"], df["Bat Second"])

# KPI: Powerplay (overs 1–6), valid balls only
pp = df[(df["Over"] >= 1) & (df["Over"] <= 6) & (df["Valid Ball"] == 1)].copy()

pp_agg = (
    pp.groupby(["Match ID", "Innings", "batting_team"], as_index=False)
      .agg(pp_runs=("Runs From Ball", "sum"),
           pp_balls=("Valid Ball", "sum"))
)
pp_agg["pp_overs"] = pp_agg["pp_balls"] / 6.0
pp_agg["pp_run_rate"] = pp_agg["pp_runs"] / pp_agg["pp_overs"]

# Save KPI output
pp_agg.to_csv(OUT_DIR / "kpi_powerplay_runrate.csv", index=False)

# Team-level average (only teams with decent sample size)
team_avg = (
    pp_agg.groupby("batting_team", as_index=False)
          .agg(avg_pp_run_rate=("pp_run_rate", "mean"),
               matches=("Match ID", "nunique"))
)
team_avg = team_avg[team_avg["matches"] >= 20].sort_values("avg_pp_run_rate", ascending=False)

overall_mean = pp_agg["pp_run_rate"].mean()
overall_median = pp_agg["pp_run_rate"].median()

# -------------------------
# FIG 1: Distribution + mean/median lines
# -------------------------
plt.figure(figsize=(9.5, 5.8))
vals = pp_agg["pp_run_rate"].dropna()
plt.hist(vals, bins=30)

plt.axvline(overall_mean, linewidth=2, label=f"Mean = {overall_mean:.2f}")
plt.axvline(overall_median, linewidth=2, label=f"Median = {overall_median:.2f}")

plt.title("Powerplay Run Rate (Overs 1–6): How it is distributed across all matches")
plt.xlabel("Run rate (runs per over)")
plt.ylabel("Number of match-innings-team cases")
plt.legend()
fig1 = OUT_DIR / "fig1_pp_runrate_distribution.png"
plt.savefig(fig1, dpi=220, bbox_inches="tight")
plt.close()

# -------------------------
# FIG 2: Team comparison (Top 10) + mean reference line
# -------------------------
top10 = team_avg.head(10).copy()

plt.figure(figsize=(10, 5.8))
plt.bar(top10["batting_team"], top10["avg_pp_run_rate"])

plt.axhline(overall_mean, linewidth=2, label=f"Overall mean = {overall_mean:.2f}")

plt.title("Top 10 Teams by Average Powerplay Run Rate (Overs 1–6)")
plt.xlabel("Team")
plt.ylabel("Average run rate (runs per over)")
plt.xticks(rotation=25, ha="right")
plt.legend()
fig2 = OUT_DIR / "fig2_top10_teams_pp_runrate.png"
plt.savefig(fig2, dpi=220, bbox_inches="tight")
plt.close()

# -------------------------
# FIG 3: Innings comparison (Boxplot) + median markers
# -------------------------
inn1 = pp_agg.loc[pp_agg["Innings"] == 1, "pp_run_rate"].dropna()
inn2 = pp_agg.loc[pp_agg["Innings"] == 2, "pp_run_rate"].dropna()

plt.figure(figsize=(8.5, 5.8))
plt.boxplot([inn1, inn2], labels=["Innings 1", "Innings 2"], showmeans=True)

plt.title("Powerplay Run Rate by Innings (Boxplot)")
plt.ylabel("Run rate (runs per over)")
fig3 = OUT_DIR / "fig3_pp_runrate_by_innings.png"
plt.savefig(fig3, dpi=220, bbox_inches="tight")
plt.close()

# -------------------------
# FIG 4: Cost comparison (make it explainable)
# -------------------------
days = np.array([1, 7, 30], dtype=float)
always_cost = days * ALWAYS_ON_HOURS_PER_DAY * EC2_PRICE_PER_HOUR
ond_cost = days * ON_DEMAND_HOURS_PER_DAY * EC2_PRICE_PER_HOUR

x = np.arange(len(days))
width = 0.35

plt.figure(figsize=(9.5, 5.8))
plt.bar(x - width/2, always_cost, width, label="Always-on EC2 (pays 24h/day)")
plt.bar(x + width/2, ond_cost, width, label="On-demand start/stop (pays only run-time)")

plt.title("Estimated EC2 Compute Cost: Always-on vs On-demand (Example)")
plt.xlabel("Time horizon (days)")
plt.ylabel("Estimated compute cost (USD)")
plt.xticks(x, [f"{int(d)} day(s)" for d in days])
plt.legend()

# add a simple note directly in chart area (easy for reader)
plt.text(0.5, 0.92,
         f"Assumptions: ${EC2_PRICE_PER_HOUR}/hour, on-demand = {ON_DEMAND_HOURS_PER_DAY*60:.0f} min/day",
         transform=plt.gca().transAxes, ha="center", va="center")

fig4 = OUT_DIR / "fig4_ec2_cost_comparison.png"
plt.savefig(fig4, dpi=220, bbox_inches="tight")
plt.close()

print("Saved figures:")
print(fig1)
print(fig2)
print(fig3)
print(fig4)
print("Saved KPI CSV:", OUT_DIR / "kpi_powerplay_runrate.csv")