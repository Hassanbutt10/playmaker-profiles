"""
Playmaker Profiles - Cycle 4, Day 6 project
Applies the xT zone grid (from xt-model) across the WHOLE WC2022 tournament.

Part 1: split each player's total xT into pass-xT vs carry-xT
Part 2: compare total xT against actual goals+assists to find undervalued players

Reuses: all_wc2022_events.csv, zone_values.csv (copy these into this folder
from the xt-model project before running)
"""

import pandas as pd
import ast

# ---------- Step 0: load ----------
events = pd.read_csv("all_wc2022_events.csv", low_memory=False)
zone_values = pd.read_csv("zone_values.csv")

# ---------- Step 1: score every pass and carry ----------
PITCH_X, PITCH_Y = 120, 80
GRID_X, GRID_Y = 12, 8
CELL_X, CELL_Y = PITCH_X / GRID_X, PITCH_Y / GRID_Y

zone_lookup = {
    (int(row.zone_x), int(row.zone_y)): row.zone_value
    for row in zone_values.itertuples()
}

def get_zone(x, y):
    zx = min(int(x // CELL_X), GRID_X - 1)
    zy = min(int(y // CELL_Y), GRID_Y - 1)
    return zx, zy

def zone_value(x, y):
    zx, zy = get_zone(x, y)
    return zone_lookup.get((zx, zy), 0)

def parse_loc(val):
    # location fields are stored as string lists, e.g. "[60.0, 40.0]"
    if pd.isna(val):
        return None, None
    try:
        coords = ast.literal_eval(val)
        return coords[0], coords[1]
    except (ValueError, SyntaxError, IndexError):
        return None, None

actions = events[events["type"].isin(["Pass", "Carry"])].copy()

actions[["x", "y"]] = actions["location"].apply(lambda v: pd.Series(parse_loc(v)))

end_loc = actions["pass_end_location"].where(
    actions["type"] == "Pass", actions["carry_end_location"]
)
actions[["end_x", "end_y"]] = end_loc.apply(lambda v: pd.Series(parse_loc(v)))

actions = actions.dropna(subset=["x", "y", "end_x", "end_y"])

actions["start_value"] = actions.apply(lambda r: zone_value(r["x"], r["y"]), axis=1)
actions["end_value"] = actions.apply(lambda r: zone_value(r["end_x"], r["end_y"]), axis=1)
actions["xt"] = actions["end_value"] - actions["start_value"]

actions.to_csv("all_actions_scored.csv", index=False)
print(f"\nScored {len(actions)} pass/carry actions across the tournament.")

# ---------- Step 2a: pass-xT vs carry-xT per player ----------
xt_split = (
    actions.groupby(["player", "team", "type"])["xt"]
    .sum()
    .unstack(fill_value=0)
    .rename(columns={"Pass": "pass_xt", "Carry": "carry_xt"})
)
xt_split["total_xt"] = xt_split.get("pass_xt", 0) + xt_split.get("carry_xt", 0)
xt_split = xt_split.reset_index().sort_values("total_xt", ascending=False)

# ---------- Step 2b: actual goals + assists per player ----------
goals = (
    events[(events["type"] == "Shot") & (events["shot_outcome"] == "Goal")]
    .groupby("player")
    .size()
    .rename("goals")
)
assists = (
    events[events["pass_goal_assist"] == True]
    .groupby("player")
    .size()
    .rename("assists")
)

profiles = xt_split.merge(goals, on="player", how="left")
profiles = profiles.merge(assists, on="player", how="left")
profiles[["goals", "assists"]] = profiles[["goals", "assists"]].fillna(0)
profiles["g_plus_a"] = profiles["goals"] + profiles["assists"]

profiles["xt_rank"] = profiles["total_xt"].rank(ascending=False)
profiles["ga_rank"] = profiles["g_plus_a"].rank(ascending=False)
profiles["undervalued_score"] = profiles["ga_rank"] - profiles["xt_rank"]

profiles = profiles.sort_values("total_xt", ascending=False)
profiles.to_csv("playmaker_profiles.csv", index=False)

print("\nTop 10 by total xT:")
print(profiles[["player", "team", "pass_xt", "carry_xt", "total_xt", "g_plus_a"]].head(10))

print("\nTop 10 most undervalued (high xT rank, low G+A rank):")
print(profiles.sort_values("undervalued_score", ascending=False)
      [["player", "team", "total_xt", "g_plus_a", "undervalued_score"]].head(10))

# ---------- Step 3: visualization for LinkedIn ----------
import matplotlib.pyplot as plt

# filter out noise: players with very few actions barely register
plot_df = profiles[profiles["total_xt"] > 1.0].copy()
top_undervalued = plot_df.sort_values("undervalued_score", ascending=False).head(8)

fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#0d1b2a")
ax.set_facecolor("#0d1b2a")

ax.scatter(plot_df["g_plus_a"], plot_df["total_xt"],
           color="#4a90d9", alpha=0.5, s=40, label="All players")
ax.scatter(top_undervalued["g_plus_a"], top_undervalued["total_xt"],
           color="#f4a300", s=80, label="Most undervalued", zorder=5)

for _, row in top_undervalued.iterrows():
    ax.annotate(row["player"].split()[-1],
                (row["g_plus_a"], row["total_xt"]),
                textcoords="offset points", xytext=(6, 4),
                color="white", fontsize=9)

ax.set_xlabel("Goals + Assists", color="white")
ax.set_ylabel("Total xT (whole tournament)", color="white")
ax.set_title("High xT, Low Goal Contribution: WC 2022's Hidden Playmakers",
              color="white", fontsize=13)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_color("#3a4a5a")
ax.legend(facecolor="#0d1b2a", labelcolor="white", edgecolor="#3a4a5a")

plt.tight_layout()
plt.savefig("playmaker_profiles.png", dpi=150, facecolor=fig.get_facecolor())
print("\nSaved chart: playmaker_profiles.png")