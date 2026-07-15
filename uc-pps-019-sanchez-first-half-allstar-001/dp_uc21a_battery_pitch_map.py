"""
============================================================================
uc-pps-019 ADDENDUM (v1.1.0, additive) — dp_uc21a
Battery pitch maps: Sanchez's pitch location/mix/results by catcher, 2026
============================================================================
Pattern source: Kellen's plotly pitch-map graph (px.scatter, location
centroids sized by usage, faceted by stand, animated by catcher, strike-zone
rect) — adopted as a house visual for battery/location questions.

Additive to dp_uc21 (v1.0.0). NEW files only; no v1.0.0 receipt overwritten.
No new formula-KPI: panel uses locked KPIs (whiff/chase/putaway/hard-hit,
barrel = launch_speed_angle==6 per glossary) + descriptive location
centroids (plate_x/plate_z means). Spec note in the addendum doc.

Receipts -> <MLB repo>/out/:
  dp_uc21a_battery_pitch_map.csv   catcher x stand x pitch: n, usage,
                                   centroids, in-zone, whiff/chase/putaway,
                                   HH/barrel, xwOBA, velo
  dp_uc21a_battery_game_mix.csv    catcher x game_date pitch counts —
                                   the game-mix confound receipt
Figures:
  dp_uc21a_battery_pitch_map.html  interactive (Kellen's plotly format)
  dp_uc21a_fig4_battery_pitch_map.png  static, Phillies brand (report-safe)
Both figure files also copied into this package folder.
============================================================================
"""
from __future__ import annotations
import os, shutil
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SANCHEZ = 650911

_DATA_CANDIDATES = [
    os.environ.get("MLB_DATA_ROOT", ""),
    os.path.join(HERE, "data", "phillies"),
    r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB\data\phillies",
]
PHIL_DIR = next((p for p in _DATA_CANDIDATES if p and os.path.isdir(p)), None)
REPO_ROOT = os.path.dirname(os.path.dirname(PHIL_DIR)) if PHIL_DIR else HERE
OUT_DIR = os.path.join(REPO_ROOT, "out"); os.makedirs(OUT_DIR, exist_ok=True)

SWINGS = ["foul","foul_bunt","foul_tip","hit_into_play","missed_bunt",
          "swinging_pitchout","swinging_strike","swinging_strike_blocked"]
WHIFFS = ["foul_tip","missed_bunt","swinging_pitchout",
          "swinging_strike","swinging_strike_blocked"]
PHI_RED, PHI_NAVY, PHI_GRAY, PHI_LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"Sinker": "#8C564B", "Changeup": "#FF7F0E", "Slider": "#1F77B4"}

def load():
    d = pd.read_parquet(os.path.join(PHIL_DIR, "phils_2026.parquet"))
    d = d[(d.phillies_role=="pitching")&(d.pitcher==SANCHEZ)&(d.game_type=="R")]
    d = d.drop_duplicates(["game_pk","at_bat_number","pitch_number"])
    for c in ["plate_x","plate_z","zone","launch_speed","launch_speed_angle",
              "strikes","pfx_x","pfx_z","release_speed","sz_top","sz_bot"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

def catcher_names(d):
    """Resolve fielder_2 ids from batting-side rows (no hand-keying)."""
    ids = [int(x) for x in d.fielder_2.dropna().unique()]
    b = pd.read_parquet(os.path.join(PHIL_DIR,"phils_2026.parquet"),
                        columns=["batter","player_name","phillies_role"])
    b = b[b.phillies_role=="batting"]
    out = {}
    for i in ids:
        s = b[b.batter==i].player_name
        out[i] = s.mode().iat[0] if len(s) else f"id:{i}"
    return out

def main():
    d = load()
    names = catcher_names(d)
    d = d.copy(); d["catcher"] = d.fielder_2.map(names)

    rows=[]
    for (cat, st, pn), g in d.groupby(["catcher","stand","pitch_name"]):
        sw = g[g.description.isin(SWINGS)]; wh = g[g.description.isin(WHIFFS)]
        ooz = g[g.zone>9]; ch = ooz[ooz.description.isin(SWINGS)]
        bip = g[g.type=="X"]
        s2 = g[g.strikes==2]
        k  = g[g.events.isin(["strikeout","strikeout_double_play"])]
        rows.append(dict(catcher=cat, stand=st, pitch_name=pn,
            pitch_type={"Sinker":"SI","Changeup":"CH","Slider":"SL"}.get(pn,pn[:2].upper()),
            pitches=len(g), bip=len(bip),
            plate_x=g.plate_x.mean(), plate_z=g.plate_z.mean(),
            pfx_x=g.pfx_x.mean(), pfx_z=g.pfx_z.mean(),
            release_speed=g.release_speed.mean(),
            in_zone_rate=1-len(ooz)/len(g),
            whiff_rate=len(wh)/len(sw) if len(sw) else np.nan,
            chase_rate=len(ch)/len(ooz) if len(ooz) else np.nan,
            putaway_rate=len(k)/len(s2) if len(s2) else np.nan,
            hard_hit_rate=(bip.launch_speed>=95).mean() if len(bip) else np.nan,
            barrel_rate=(bip.launch_speed_angle==6).mean() if len(bip) else np.nan,
            xwoba=g.estimated_woba_using_speedangle.mean()))
    t = pd.DataFrame(rows)
    t["usage"] = t.pitches / t.groupby(["catcher","stand"]).pitches.transform("sum")
    t = t.round(3).sort_values(["catcher","stand","pitch_name"])
    t.to_csv(os.path.join(OUT_DIR,"dp_uc21a_battery_pitch_map.csv"), index=False)

    gm = (d.groupby(["catcher","game_date"],as_index=False)
            .agg(pitches=("description","size")))
    gm["game_date"] = gm.game_date.astype(str).str[:10]
    gm.to_csv(os.path.join(OUT_DIR,"dp_uc21a_battery_game_mix.csv"), index=False)

    sz_bot, sz_top = float(d.sz_bot.mean()), float(d.sz_top.mean())

    # --- interactive: Kellen's plotly format --------------------------------
    try:
        import plotly.express as px
        figp = px.scatter(t, x="plate_x", y="plate_z", size="usage",
            color="pitch_name", animation_frame="catcher", facet_col="stand",
            text="pitch_type", template="plotly_dark",
            color_discrete_map=PITCH_COLORS,
            hover_data=["pitches","in_zone_rate","whiff_rate","chase_rate",
                        "putaway_rate","hard_hit_rate","barrel_rate","xwoba"],
            title="Cristopher Sanchez throwing to different Catchers in 2026"
                  " — centroids sized by usage (dp_uc21a; catcher's view)",
            labels={"plate_x":"Horizontal Location (ft)","plate_z":"Vertical Location (ft)",
                    "pitch_name":"Pitch","catcher":"Catcher","stand":"Batter Stand"})
        figp.add_shape(type="rect", x0=-0.83, x1=0.83, y0=sz_bot, y1=sz_top,
                       line=dict(color="White", width=1), row="all", col="all")
        figp.update_xaxes(range=[-2.2,2.2]); figp.update_yaxes(range=[0.5,3.6])
        html = os.path.join(OUT_DIR,"dp_uc21a_battery_pitch_map.html")
        figp.write_html(html, include_plotlyjs="cdn")
    except Exception as e:
        print("plotly skipped:", e)

    # --- static: Phillies-brand PNG for the addendum doc --------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    cats = ["Realmuto, J.T.","Marchán, Rafael","Stubbs, Garrett"]
    cats = [c for c in cats if c in set(t.catcher)] + \
           [c for c in sorted(set(t.catcher)) if c not in cats]
    fig, axes = plt.subplots(2, len(cats), figsize=(3.6*len(cats), 7.4),
                             sharex=True, sharey=True)
    for j, cat in enumerate(cats):
        for i, st in enumerate(["L","R"]):
            ax = axes[i][j] if len(cats)>1 else axes[i]
            ax.add_patch(Rectangle((-0.83, sz_bot), 1.66, sz_top-sz_bot,
                         fill=False, edgecolor=PHI_NAVY, lw=1.2, zorder=1))
            sub = t[(t.catcher==cat)&(t.stand==st)]
            for _, r in sub.iterrows():
                ax.scatter(r.plate_x, r.plate_z, s=3200*r.usage,
                           color=PITCH_COLORS.get(r.pitch_name,PHI_GRAY),
                           alpha=.75, edgecolor="white", lw=1, zorder=3)
                ax.annotate(f"{r.pitch_type} {r.usage:.0%}\n({int(r.pitches)}p)",
                            (r.plate_x, r.plate_z), ha="center", va="center",
                            fontsize=6.6, color="white", weight="bold", zorder=4)
            n_cs = int(t[(t.catcher==cat)&(t.stand==st)].pitches.sum())
            ax.set_title(f"{cat.split(',')[0]} — vs {st}HB ({n_cs}p)",
                         fontsize=9, color=PHI_NAVY, weight="bold")
            ax.set_xlim(-2.0,2.0); ax.set_ylim(0.7,3.5)
            ax.grid(color=PHI_LGRAY, lw=.4, zorder=0)
            if i==1: ax.set_xlabel("plate_x (ft, catcher's view)", fontsize=8)
            if j==0: ax.set_ylabel("plate_z (ft)", fontsize=8)
    fig.suptitle("Sánchez 2026 — pitch centroids by catcher (size = usage; counts printed; non-JTR panels are 1–3 games)",
                 color=PHI_NAVY, weight="bold", fontsize=11)
    fig.tight_layout()
    png = os.path.join(OUT_DIR,"dp_uc21a_fig4_battery_pitch_map.png")
    fig.savefig(png, dpi=160); plt.close(fig)

    for f in ["dp_uc21a_battery_pitch_map.html","dp_uc21a_fig4_battery_pitch_map.png"]:
        src = os.path.join(OUT_DIR,f)
        if os.path.isfile(src):
            shutil.copy(src, os.path.join(HERE, ("out_" if f.endswith("png") else "")+f))

    pd.set_option("display.width",240)
    print("ADDENDUM BUILD COMPLETE\n")
    print(t.to_string(index=False),"\n")
    print(gm.to_string(index=False))

if __name__ == "__main__":
    main()
