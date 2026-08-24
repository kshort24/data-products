"""
dp_uc36 — interactive dashboard builder (Layer-5 consumable).
Reads ONLY the CSV receipts in ./out (surfaces round once, from receipts —
dp_uc35 D4-family rule). plotly.js is INLINED (vendored, not CDN — the
uc-pos-011 standing rule). Views V1-V4 per 02_engineering_design.md sec 4.
The V3 pitch-type dropdown implements the DPO's own interactive pattern from
the use-case notebook.
"""
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
RED, NAVY, GRAY, LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
PITCH_COLORS = {"4-Seam Fastball": RED, "Cutter": NAVY, "Sweeper": "#1F77B4",
                "Changeup": "#2CA02C", "Slider": "#6BAED6", "Sinker": "#FF7F0E",
                "Curveball": "#8C564B"}
TPL = "plotly_white"

ud = pd.read_csv(f"{OUT}/dp_uc36_usage_by_season.csv")
season = pd.read_csv(f"{OUT}/dp_uc36_season_log.csv")
mix = pd.read_csv(f"{OUT}/dp_uc36_mix_by_hand_season.csv")
stuff = pd.read_csv(f"{OUT}/dp_uc36_stuff_by_pitch_season.csv")
plat = pd.read_csv(f"{OUT}/dp_uc36_platoon_by_phase.csv")
arc = pd.read_csv(f"{OUT}/dp_uc36_monthly_arc_2024_25.csv")
terc = pd.read_csv(f"{OUT}/dp_uc36_outing_terciles.csv")

PHASE_ORDER = ["2019 NYY relief/bulk", "2021 transition", "2022 peak",
               "2023-24 decline", "2025 final (MIL-SD)"]

figs = {}

# ---- V1: deployment timeline ------------------------------------------------
f = make_subplots(rows=1, cols=2, subplot_titles=(
    "Appearances by shape (hover for UD detail)", "Role shares by season"))
f.add_trace(go.Bar(x=ud.game_year, y=ud.starts, name="Starts", marker_color=RED,
                   customdata=ud[["innings_per_gm", "plate_apps_per_gm", "role_label"]],
                   hovertemplate="%{x}: %{y} starts<br>IP/gm (delta): %{customdata[0]:.2f}"
                                 "<br>PA/gm: %{customdata[1]:.1f}<br>role: %{customdata[2]}"
                                 "<extra></extra>"), 1, 1)
f.add_trace(go.Bar(x=ud.game_year, y=ud.bulks, name="Bulk (UD-2)", marker_color=NAVY,
                   hovertemplate="%{x}: %{y} bulk games<extra></extra>"), 1, 1)
f.add_trace(go.Bar(x=ud.game_year, y=ud.games - ud.starts - ud.bulks,
                   name="Other relief", marker_color=LGRAY,
                   hovertemplate="%{x}: %{y} other relief<extra></extra>"), 1, 1)
for col, nm, cc, dash in [("start_share", "Start share (UD-1)", RED, None),
                          ("bulk_share", "Bulk share (UD-2)", NAVY, "dash"),
                          ("relief_share", "Relief share (UD-5)", GRAY, "dot")]:
    f.add_trace(go.Scatter(x=ud.game_year, y=ud[col], name=nm, mode="lines+markers",
                           line=dict(color=cc, dash=dash)), 1, 2)
f.update_layout(barmode="stack", template=TPL, height=420,
                title="V1 · Deployment — how he has been used (UD family, DPO definitions)",
                legend=dict(orientation="h", y=-0.18))
figs["v1"] = f

# ---- V2: arsenal evolution by hand (DPO's pm-frame view) --------------------
f = make_subplots(rows=1, cols=2, subplot_titles=("vs LHB", "vs RHB"), shared_yaxes=True)
for j, hand in enumerate(["L", "R"], start=1):
    sub = mix[(mix.stand == hand) & (mix.usage >= 0.02)]
    for pn in sub.pitch_name.unique():
        s = sub[sub.pitch_name == pn].sort_values("game_year")
        f.add_trace(go.Scatter(
            x=s.game_year, y=s.usage, name=pn, legendgroup=pn, showlegend=(j == 1),
            mode="lines+markers", line=dict(color=PITCH_COLORS.get(pn, GRAY)),
            customdata=s[["velo", "spin", "whiff_rate", "xwobacon", "pitches"]],
            hovertemplate=f"{pn} %{{x}}<br>usage %{{y:.3f}} (%{{customdata[4]}} pitches)"
                          "<br>velo %{customdata[0]:.1f} · spin %{customdata[1]:.0f}"
                          "<br>whiff %{customdata[2]:.3f} · xwOBAcon %{customdata[3]:.3f}"
                          "<extra></extra>"), 1, j)
f.update_layout(template=TPL, height=430,
                title="V2 · Arsenal evolution by batter hand (TRACKED usage share)")
figs["v2"] = f

# ---- V3: stuff tracker with PITCH-TYPE DROPDOWN (the DPO's pattern) ---------
metrics = [("velo", "Velocity (mph)", 1, 1), ("spin", "Spin (rpm)", 1, 2),
           ("ivb_in", "IVB (in)", 2, 1), ("hb_in", "HB, arm-side + (in)", 2, 2)]
ptypes = [p for p in stuff.pitch_name.unique()
          if stuff[stuff.pitch_name == p].pitches.sum() >= 100]
f = make_subplots(rows=2, cols=2, subplot_titles=[m[1] for m in metrics])
trace_map = {}
ti = 0
for pn in ptypes:
    trace_map[pn] = []
    s = stuff[stuff.pitch_name == pn].sort_values("game_year")
    for col, lab, r, c in metrics:
        f.add_trace(go.Scatter(
            x=s.game_year, y=s[col], mode="lines+markers",
            line=dict(color=PITCH_COLORS.get(pn, GRAY)), showlegend=False,
            visible=(pn == ptypes[0]),
            customdata=s[["pitches"]],
            hovertemplate=f"{pn} %{{x}}: %{{y:.2f}} ({lab})"
                          "<br>n=%{customdata[0]}<extra></extra>"), r, c)
        trace_map[pn].append(ti)
        ti += 1
buttons = []
for pn in ptypes:
    vis = [False] * ti
    for k in trace_map[pn]:
        vis[k] = True
    buttons.append(dict(label=pn, method="update",
                        args=[{"visible": vis},
                              {"title": f"V3 · Tracking the stuff: {pn} (season means; "
                                        "2025 = injury-shortened, directional)"}]))
f.update_layout(template=TPL, height=560,
                title=f"V3 · Tracking the stuff: {ptypes[0]} (season means; "
                      "2025 = injury-shortened, directional)",
                updatemenus=[dict(buttons=buttons, direction="down", x=1.02, y=1.08,
                                  xanchor="left", yanchor="top", showactive=True)])
figs["v3"] = f

# ---- V4: platoon board + monthly arc ---------------------------------------
f = make_subplots(rows=1, cols=2, subplot_titles=(
    "wOBA against by phase and hand (PA in hover)",
    "2024-25 monthly arc — FF velo vs xwOBAcon"),
    specs=[[{}, {"secondary_y": True}]])
for hand, cc in [("L", RED), ("R", NAVY)]:
    s = plat[plat.stand == hand].set_index("phase").reindex(PHASE_ORDER).reset_index()
    f.add_trace(go.Bar(x=s.phase, y=s.woba, name=f"vs {'LHB' if hand=='L' else 'RHB'}",
                       marker_color=cc, customdata=s[["plate_apps", "krate", "xwobacon"]],
                       hovertemplate="%{x} vs " + hand + "HB<br>wOBA %{y:.3f} "
                                     "(%{customdata[0]:.0f} PA)<br>K %{customdata[1]:.3f}"
                                     " · xwOBAcon %{customdata[2]:.3f}<extra></extra>"), 1, 1)
f.add_trace(go.Scatter(x=arc.month, y=arc.ff_velo, name="FF velo (mph)",
                       mode="lines+markers", line=dict(color=RED)),
            row=1, col=2, secondary_y=False)
f.add_trace(go.Scatter(x=arc.month, y=arc.xwobacon, name="xwOBAcon",
                       mode="lines+markers", line=dict(color=NAVY, dash="dot")),
            row=1, col=2, secondary_y=True)
f.update_yaxes(title_text="FF velo (mph)", row=1, col=2, secondary_y=False)
f.update_yaxes(title_text="xwOBAcon", row=1, col=2, secondary_y=True)
f.update_layout(template=TPL, height=430, barmode="group",
                title="V4 · Platoon splits and the pre-surgery arc",
                legend=dict(orientation="h", y=-0.25))
figs["v4"] = f

# ---- KPI cards (full-precision from receipts, rounded once here) ------------
peak = season[season.game_year == 2022].iloc[0]
dec = plat[(plat.phase == "2023-24 decline")]
lhb2324 = dec[dec.stand == "L"].iloc[0]
y25 = season[season.game_year == 2025].iloc[0]
bulk19 = ud[ud.game_year == 2019].iloc[0]
cards = [
    ("2022 peak wOBA against", f"{peak.woba:.3f}", f"{int(peak.plate_apps)} PA · All-Star season"),
    ("2023-24 vs LHB", f"{lhb2324.woba:.3f}", f"{int(lhb2324.plate_apps)} PA — the lefty edge held"),
    ("2025 (injury year)", f"{y25.woba:.3f}", f"{int(y25.plate_apps)} PA · 8 G · directional only"),
    ("2019 bulk share", f"{bulk19.bulk_share:.1%}", f"{int(bulk19.bulks)} of {int(bulk19.games)} G — he has done the bulk job"),
    ("FF velo, last look", "90.1 mph", "2025 season mean; 92.1 in 2024 — the #1 return cue"),
    ("2026 data", "TRUE GAP", "zero competitive pitches since 2025-09-03 (surgery)"),
]
card_html = "".join(
    f'<div class="card"><div class="v">{v}</div><div class="t">{t}</div>'
    f'<div class="s">{s}</div></div>' for t, v, s in cards)

parts = []
for i, (k, fg) in enumerate(figs.items()):
    parts.append(pio.to_html(fg, include_plotlyjs=(i == 0), full_html=False,
                             config={"displaylogo": False}))

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Cortes Acquisition Read — dp_uc36</title>
<style>
 body {{ font-family: Georgia, 'Times New Roman', serif; margin: 0; background:#f6f6f4; color:#1a1a1a; }}
 header {{ background:{NAVY}; color:white; padding:22px 34px; border-bottom:6px solid {RED}; }}
 header h1 {{ margin:0 0 4px 0; font-size:24px; }}
 header p {{ margin:0; font-size:13px; opacity:.85; }}
 .cards {{ display:flex; flex-wrap:wrap; gap:12px; padding:18px 34px; }}
 .card {{ background:white; border-left:5px solid {RED}; border-radius:6px;
          padding:12px 16px; min-width:170px; flex:1; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
 .card .v {{ font-size:22px; font-weight:bold; color:{NAVY}; }}
 .card .t {{ font-size:12px; font-weight:bold; margin-top:2px; }}
 .card .s {{ font-size:11px; color:#555; margin-top:2px; }}
 section {{ background:white; margin:14px 34px; border-radius:6px; padding:8px 12px;
            box-shadow:0 1px 3px rgba(0,0,0,.08); }}
 footer {{ padding:14px 34px 26px; font-size:11.5px; color:#555; }}
 .warn {{ background:#fdf3e7; border-left:4px solid {RED}; margin:0 34px; padding:10px 16px;
          font-size:12.5px; }}
</style></head><body>
<header><h1>Nestor Cortes — Acquisition Read (LHP · MLBAM 641482)</h1>
<p>UC #37 · uc-pps-026 · dp_uc36 · signed PHI 2026-08-19 (1-yr prorated ML; Brian Keller DFA'd
for the 40-man spot) · data: career 2018 – 2025-09-03, regular season rates · built {pd.Timestamp('2026-08-20').date()}</p></header>
<div class="warn"><b>Read this first:</b> Cortes has thrown <b>zero competitive pitches since
2025-09-03</b> (arm surgery, mid-Oct 2025). Everything here is a pre-return baseline. 2025 cells
are 8 games / 157 PA — directional only. Postseason is context, never blended into rates.</div>
<div class="cards">{card_html}</div>
<section>{parts[0]}</section>
<section>{parts[1]}</section>
<section>{parts[2]}</section>
<section>{parts[3]}</section>
<footer>Receipts: dp_uc36_usage_by_season.csv · dp_uc36_mix_by_hand_season.csv ·
dp_uc36_stuff_by_pitch_season.csv · dp_uc36_platoon_by_phase.csv · dp_uc36_monthly_arc_2024_25.csv
— all in <code>out/</code>. plotly.js vendored inline (no CDN). Governance trail 00–07 in this
folder. Internal use only.</footer>
</body></html>"""

path = os.path.join(HERE, "dp_uc36_cortes_dashboard.html")
with open(path, "w") as fh:
    fh.write(html)
print("dashboard written:", path, f"{os.path.getsize(path)/1e6:.2f} MB")
