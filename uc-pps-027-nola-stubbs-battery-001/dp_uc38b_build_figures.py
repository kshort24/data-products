"""dp_uc38b_build_figures.py -- addendum figures for uc-pps-027 / dp_uc38.
Reads ONLY from ./out receipts written by dp_uc38b_battery_addendum.py.
No number is computed here; this file draws what the build already proved."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
RED, NAVY, GRAY, LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
BP = pd.Timestamp("2026-07-05")
CCOL = {"Stubbs, Garrett": RED, "Realmuto, J.T.": NAVY, "Marchán, Rafael": GRAY}
made = []


def save(fig, name):
    p = os.path.join(OUT, name); fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
    made.append(name); print("  wrote", name)


# --- figA: per-start changeup share, breakpoint marked -----------------
d = pd.read_csv(os.path.join(OUT, "dp_uc38b_per_start_approach_2026.csv"))
d["game_date"] = pd.to_datetime(d.game_date)
fig, ax = plt.subplots(figsize=(11.5, 4.8))
ax.axvspan(BP, d.game_date.max() + pd.Timedelta(days=4), color=LGRAY, alpha=.45, zorder=0)
for nm, g in d.groupby("catcher"):
    ax.scatter(g.game_date, g.ch_share, s=118, color=CCOL.get(nm, GRAY),
               label=nm, zorder=3, edgecolor="white", linewidth=1.4)
ax.plot(d.game_date, d.ch_share, color=GRAY, linewidth=1.1, zorder=2, alpha=.75)
ax.axvline(BP, color=NAVY, linestyle="--", linewidth=1.6, zorder=1)
ax.annotate("breakpoint 7/05", xy=(BP, ax.get_ylim()[1] * .96), xytext=(6, 0),
            textcoords="offset points", color=NAVY, fontsize=9, fontweight="bold")
ax.set_title("Changeup share by start, 2026 — the ramp starts before the Stubbs stretch does",
             color=NAVY, fontweight="bold")
ax.set_ylabel("changeup share of pitches"); ax.legend(frameon=False, fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
save(fig, "dp_uc38b_figA_changeup_ramp.png")

# --- figB: TR-1 travel test -------------------------------------------
t = pd.read_csv(os.path.join(OUT, "dp_uc38b_travel_test.csv"))
lbl = {"ch_share": "changeup share", "kc_share": "knuckle-curve share",
       "fb_share": "fastball share", "offspeed_share": "offspeed share",
       "fp_offspeed_share": "1st-pitch offspeed", "first_pitch_strike_rate": "1st-pitch strike rate",
       "two_strike_fb_rate": "2-strike fastball rate", "two_strike_ch_rate": "2-strike changeup rate",
       "behind_ch_rate": "changeup when behind", "in_zone_rate": "in-zone rate",
       "whiff_rate": "whiff rate", "chase_rate": "chase rate"}
t = t[t.metric != "offspeed_share"].copy()          # identical to ch_share for this arsenal
t["lab"] = t.metric.map(lbl)
t = t.sort_values("stubbs_delta")
y = np.arange(len(t))
fig, ax = plt.subplots(figsize=(10.5, 5.6))
for i, r in enumerate(t.itertuples()):
    ax.plot([r.non_stubbs_delta, r.stubbs_delta], [i, i], color=LGRAY, linewidth=3, zorder=1)
ax.scatter(t.non_stubbs_delta, y, s=105, color=NAVY, label="other catchers", zorder=3)
ax.scatter(t.stubbs_delta, y, s=105, color=RED, label="Stubbs starts", zorder=3)
ax.axvline(0, color="black", linewidth=1)
ax.set_yticks(y); ax.set_yticklabels(t.lab, fontsize=9)
ax.set_xlabel("change since 2026-07-05 (percentage points, as a rate)")
ax.set_title("The adjustment travels: same direction with and without Stubbs",
             color=NAVY, fontweight="bold")
ax.legend(frameon=False, fontsize=9, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "dp_uc38b_figB_travel_test.png")

# --- figC: uc-pps-021 tripwire ----------------------------------------
tr = pd.read_csv(os.path.join(OUT, "dp_uc38b_uc_pps_021_tripwire.csv"))
fig, axes = plt.subplots(1, len(tr), figsize=(12.4, 3.9))
for ax, r in zip(axes, tr.itertuples()):
    vals = [r.before_bp, r.since_bp]
    ax.bar([0, 1], vals, color=[GRAY, RED], width=.62)
    if r.then == r.then:
        ax.axhline(r.then, color=NAVY, linestyle="--", linewidth=1.5)
        ax.annotate(f"uc-pps-021: {r.then:.3f}", xy=(1.45, r.then), fontsize=7.5,
                    color=NAVY, ha="right", va="bottom")
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["before 7/05", "since 7/05"], fontsize=8.5)
    ax.set_title(f"{r.indicator}\n(want: {r.direction_wanted})", fontsize=9,
                 color=NAVY, fontweight="bold")
    ax.set_ylim(0, max(vals + ([r.then] if r.then == r.then else [])) * 1.32)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("uc-pps-021 tripwire — three of four indicators moved the right way",
             color=NAVY, fontweight="bold", y=1.04)
save(fig, "dp_uc38b_figC_tripwire.png")

# --- figD: opponent-quality control -----------------------------------
o = pd.read_csv(os.path.join(OUT, "dp_uc38b_catcher_opponent_difficulty.csv"))
e = pd.read_csv(os.path.join(OUT, "dp_uc38b_era_by_catcher.csv"))
agg = (e.assign(num=e.woba * e.plate_apps).groupby("catcher", as_index=False)
       .agg(num=("num", "sum"), pa=("plate_apps", "sum")))
agg["woba"] = agg.num / agg.pa
m = o.merge(agg[["catcher", "woba", "pa"]], on="catcher")
fig, ax = plt.subplots(figsize=(8.6, 5.2))
for r in m.itertuples():
    c = CCOL.get(r.catcher, GRAY)
    ax.scatter(r.mean_opp_difficulty, r.woba, s=90 + r.starts * 34, color=c, zorder=3,
               edgecolor="white", linewidth=1.6)
    ax.annotate(f"{r.catcher.split(',')[0]}\n{r.starts} GS · {int(r.pa)} PA",
                xy=(r.mean_opp_difficulty, r.woba), xytext=(0, -34),
                textcoords="offset points", ha="center", fontsize=8.5, color=c,
                fontweight="bold")
ax.set_xlabel("slate difficulty → rest-of-staff wOBA allowed vs the same opponents")
ax.set_ylabel("Nola's wOBA allowed")
ax.set_title("Stubbs's edge is not a soft-slate artifact\n(right = harder opponents · low = better)",
             color=NAVY, fontweight="bold")
ax.margins(.28)
ax.spines[["top", "right"]].set_visible(False)
save(fig, "dp_uc38b_figD_opponent_control.png")

print(f"\n{len(made)} figures written to ./out")
