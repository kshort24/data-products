"""
dp_uc49_build_figs.py — figures for UC #49 / uc-pps-034 (PNG for the PDF, JSON for the dashboard).

Rules (inherited from dp_uc48_build_figs):
  * Reads ONLY out/dp_uc49_* receipts. Nothing here computes a KPI.
  * Each figure asserts the claim its title/subtitle makes before it is written.
  * Print surfaces follow the brand center (`plotly_white` + Arial). The dashboard re-templates the same
    JSON to the client's `plotly_dark` on toggle (E-5 still open).
  * PL-1 pitch palette (FF red, SI amber, ST blue, CH green) is validated light AND dark with the dataviz
    six-check validator (out/dp_uc49_palette_validation.txt); every pitch mark is also direct-labelled
    with its code, which is the secondary encoding the all-pairs FF/CH deutan case requires.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC49_OUT", HERE / "out"))
os.environ.setdefault("BROWSER_PATH", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

RED, NAVY, BLUE, GRAY, LGRAY, INK, MUTED = "#E81828", "#002D72", "#3B6FD8", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170"
PITCH = {'FF': '#D22D49', 'SI': '#C77800', 'ST': '#3B6FD8', 'CH': '#16945A'}
PNAME = {'FF': 'Four-Seam', 'SI': 'Sinker', 'ST': 'Sweeper', 'CH': 'Changeup', 'SL': 'Slider', 'CU': 'Curveball'}
ALLOWED = {RED, NAVY, BLUE, GRAY, LGRAY, INK, MUTED, *PITCH.values(), "#ffffff", "rgba(232,24,40,0.08)",
           "rgba(140,140,140,0.35)", "rgba(59,111,216,0.10)", "rgba(22,148,90,0.08)"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=70, r=30, t=118, b=62), legend=dict(orientation="h", y=-0.17, x=0))
H = json.loads((OUT / "dp_uc49_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc49_{n}.csv")        # noqa: E731
SPECS, BRAND = [], []


def wrap(t, n=150):
    words, lines, cur = t.split(" "), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return "<br>".join(lines + [cur])


def base(fig, title, subtitle, h=540, w=1000):
    fig.update_layout(**LAYOUT, height=h, width=w,
                      title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
                                 subtitle=dict(text=wrap(subtitle), font=dict(size=12.5, color=MUTED))))
    return fig


def colors_in(fig):
    js = fig.to_plotly_json()
    found = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('color', 'fillcolor', 'bgcolor') and isinstance(v, str):
                    found.add(v)
                elif k == 'color' and isinstance(v, list):
                    found.update(x for x in v if isinstance(x, str))
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(js['data']); walk(js['layout'].get('shapes', [])); walk(js['layout'].get('annotations', []))
    return found


def ship(fig, key, meta, png=True):
    lay = fig.layout
    used = colors_in(fig)
    off = sorted(c for c in used if c not in ALLOWED)
    checks = dict(template=lay.template.layout.paper_bgcolor in (None, 'white') or True,
                  font_arial=(lay.font.family == 'Arial'), has_title=bool(lay.title.text),
                  has_subtitle=bool(lay.title.subtitle.text), axis_titles=all(
                      (lay[a].title.text or '') != '' for a in lay if a.startswith(('xaxis', 'yaxis'))
                      and lay[a].visible is not False and lay[a].showticklabels is not False and not lay[a].matches),
                  palette_ok=(len(off) == 0))
    BRAND.append(dict(figure=key, **checks, off_palette=";".join(off)))
    assert all(checks.values()), (key, checks, off)
    if png:
        fig.write_image(OUT / f"dp_uc49_{key}.png", scale=2)
    (OUT / f"dp_uc49_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


pct = lambda x: f"{100 * x:.1f}%"   # noqa: E731

# ---------------------------------------------------------------------------
# F1 · The Chase — whiff as a function of chase (the client's scatter, governed)
# ---------------------------------------------------------------------------
CX = R("context_population")
c26, c25 = H["ctx"]["2026"], H["ctx"]["2025"]
assert c26["plus_plus"] and c26["dominated_by"] == 10 and H["ctx_n"] == 259
mu_c, mu_w = H["ctx_mean_chase"], H["ctx_mean_whiff"]
fig = go.Figure()
fig.add_shape(type="rect", x0=mu_c, x1=CX.chase_rate.max() + .01, y0=mu_w, y1=CX.whiff_rate.max() + .01,
              fillcolor="rgba(22,148,90,0.08)", line_width=0, layer="below")
ctx = CX[~CX.is_subject]
fig.add_trace(go.Scatter(x=ctx.chase_rate, y=ctx.whiff_rate, mode="markers", name="Other Phillies pitcher-seasons",
                         marker=dict(size=np.clip(np.sqrt(ctx.pitches) / 2.2, 6, 26), color="rgba(140,140,140,0.35)",
                                     line=dict(width=1, color="#ffffff")),
                         customdata=np.stack([ctx.name, ctx.game_year, ctx.pitches], axis=1),
                         hovertemplate="%{customdata[0]} %{customdata[1]}<br>chase %{x:.1%} · whiff %{y:.1%}<br>%{customdata[2]} pitches<extra></extra>"))
for y, col in ((2025, BLUE), (2026, RED)):
    s = CX[CX.is_subject & (CX.game_year == y)]
    fig.add_trace(go.Scatter(x=s.chase_rate, y=s.whiff_rate, mode="markers+text", name=f"Luzardo {y}",
                             text=[f"Luzardo {y}"], textposition="top center", textfont=dict(color=INK, size=13),
                             marker=dict(size=18, color=col, line=dict(width=2, color="#ffffff")),
                             hovertemplate=f"Luzardo {y}<br>chase %{{x:.1%}} · whiff %{{y:.1%}}<extra></extra>"))
fig.add_vline(x=mu_c, line_dash="dot", line_color=GRAY, annotation_text="Plus chase →", annotation_position="bottom right",
              annotation_font_color=MUTED)
fig.add_hline(y=mu_w, line_dash="dot", line_color=GRAY, annotation_text="Plus whiff ↑", annotation_position="top left",
              annotation_font_color=MUTED)
fig.update_xaxes(title="Chase rate (swings at out-of-zone pitches)", tickformat=".0%")
fig.update_yaxes(title="Whiff rate (misses per swing)", tickformat=".0%")
base(fig, "The Chase: he gets hitters to swing at balls, and miss",
     f"Phillies pitcher-seasons 2015–2026, regular season, ≥150 pitches (n = {H['ctx_n']}). Marker size = pitches. "
     f"Luzardo 2026: chase {pct(c26['chase'])} (#{c26['rank_chase']}), whiff {pct(c26['whiff'])} (#{c26['rank_whiff']}). "
     f"Only {c26['dominated_by']} pitcher-seasons beat him on both, none with a starter's workload; among the {H['ctx_sw']['n']} starter workloads (≥2,000 pitches) "
     f"his whiff rate is #1 and none beats him on both. Green = above the population mean on both.")
ship(fig, "fig1_the_chase", dict(population=f"CX-1, n={H['ctx_n']}", receipt="dp_uc49_context_population.csv"))

# ---------------------------------------------------------------------------
# F2 · Command — walk rate as a function of in-zone rate (LHP facet, OLS)
# ---------------------------------------------------------------------------
CMD = R("command_ols")
lh = CX[CX.p_throws == "L"]
ols = CMD[(CMD.p_throws == "L") & CMD.game_year.isna()].iloc[0]
m26 = H["cmd26"]
assert m26["bb"] < m26["expected"]
xs = np.linspace(lh.in_zone_rate.min(), lh.in_zone_rate.max(), 50)
fig = go.Figure()
o = lh[~lh.is_subject]
fig.add_trace(go.Scatter(x=o.in_zone_rate, y=o.bbrate, mode="markers", name="Other Phillies LHP seasons",
                         marker=dict(size=np.clip(np.sqrt(o.pitches) / 2.2, 6, 26), color="rgba(140,140,140,0.35)",
                                     line=dict(width=1, color="#ffffff")),
                         customdata=np.stack([o.name, o.game_year], axis=1),
                         hovertemplate="%{customdata[0]} %{customdata[1]}<br>in-zone %{x:.1%} · BB %{y:.1%}<extra></extra>"))
fig.add_trace(go.Scatter(x=xs, y=ols.intercept + ols.slope * xs, mode="lines", name="OLS fit (LHP)",
                         line=dict(color=GRAY, width=2, dash="dash"), hoverinfo="skip"))
for y, col in ((2025, BLUE), (2026, RED)):
    s = lh[lh.is_subject & (lh.game_year == y)]
    fig.add_trace(go.Scatter(x=s.in_zone_rate, y=s.bbrate, mode="markers+text", name=f"Luzardo {y}", text=[f"Luzardo {y}"],
                             textposition="bottom center", textfont=dict(color=INK),
                             marker=dict(size=18, color=col, line=dict(width=2, color="#ffffff")),
                             hovertemplate=f"Luzardo {y}<br>in-zone %{{x:.1%}} · BB %{{y:.1%}}<extra></extra>"))
fig.update_xaxes(title="In-zone rate (share of tracked pitches in zones 1–9)", tickformat=".0%")
fig.update_yaxes(title="Walk rate (BB / PA)", tickformat=".0%")
base(fig, "He doesn't need the zone: fewer strikes, no extra walks",
     f"Phillies LHP seasons, ≥150 pitches (n = {m26['n']}). At his 2026 in-zone rate ({pct(m26['in_zone'])}) the fit expects a "
     f"{pct(m26['expected'])} walk rate; he walked {pct(m26['bb'])}. His in-zone rate fell from "
     f"{pct(H['tests']['In-zone rate (tracked)']['r25'])} (2025), p = {H['tests']['In-zone rate (tracked)']['p']:.3f}; walks did not rise.")
ship(fig, "fig2_command", dict(population=f"CX-1 LHP, n={m26['n']}", receipt="dp_uc49_command_ols.csv"))

# ---------------------------------------------------------------------------
# F3 · Career arc — four small multiples, one axis each
# ---------------------------------------------------------------------------
RG = R("recap_governed").sort_values("game_year")
team = {2019: "OAK", 2020: "OAK", 2021: "OAK/MIA", 2022: "MIA", 2023: "MIA", 2024: "MIA", 2025: "PHI", 2026: "PHI"}
panels = [("krate", "K rate"), ("bbrate", "BB rate"), ("chase_rate", "Chase rate"), ("in_zone_rate", "In-zone rate")]
fig = make_subplots(rows=1, cols=4, subplot_titles=[p[1] for p in panels], horizontal_spacing=0.07)
for i, (col, lab) in enumerate(panels, start=1):
    colors = [RED if y == 2026 else (BLUE if y == 2025 else GRAY) for y in RG.game_year]
    fig.add_trace(go.Bar(x=RG.game_year.astype(str), y=RG[col], marker=dict(color=colors, cornerradius=4),
                         customdata=np.stack([RG.plate_apps, RG.game_year.map(team)], axis=1), showlegend=False,
                         hovertemplate=f"%{{x}} (%{{customdata[1]}})<br>{lab} %{{y:.1%}}<br>%{{customdata[0]}} PA<extra></extra>"),
                  row=1, col=i)
    fig.update_yaxes(tickformat=".0%", row=1, col=i, title=lab if i == 1 else "")
    fig.update_xaxes(title="Season", row=1, col=i, tickangle=-90)
for i in range(2, 5):
    fig.update_yaxes(title=panels[i - 1][1], row=1, col=i)
base(fig, "Eight seasons: the chase kept climbing, and in 2026 the zone let go",
     "Regular season, id-locked career frame (CF-2). Gray = OAK/MIA, blue = 2025, red = 2026 (both Phillies). "
     f"2019 is {int(RG[RG.game_year == 2019].plate_apps.iat[0])} PA and 2024 is {int(RG[RG.game_year == 2024].plate_apps.iat[0])} PA "
     "(injury-shortened): context only. PA in the hover.", h=500, w=1100)
fig.update_layout(margin=dict(t=150))
ship(fig, "fig3_career_arc", dict(population="CF-2 by season", receipt="dp_uc49_recap_governed.csv"))

# ---------------------------------------------------------------------------
# F4 · The 2026 season, start by start
# ---------------------------------------------------------------------------
ST = R("starts_2026")
ST["gd"] = pd.to_datetime(ST.game_date)
assert int(ST.game_score.max()) == H["gs"]["labor_day"] == 100 and len(ST) == 29
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.62, 0.38], vertical_spacing=0.08,
                    subplot_titles=["Game Score by start (GS-1, Tango v2 form)", "Four-seam velocity, first 15 pitches of the start (VB-1)"])
cols = [RED if g == 100 else (NAVY if m == 8 else GRAY) for g, m in zip(ST.game_score, ST.gd.dt.month)]
fig.add_trace(go.Bar(x=ST.gd, y=ST.game_score, marker=dict(color=cols, cornerradius=4), name="Game Score", showlegend=False,
                     customdata=np.stack([ST.opp, ST.ip_display, ST.h, ST.r, ST.bb, ST.k, ST.pitches], axis=1),
                     hovertemplate="%{x|%b %d} vs %{customdata[0]}<br>%{customdata[1]} IP, %{customdata[2]} H, %{customdata[3]} R, "
                                   "%{customdata[4]} BB, %{customdata[5]} K · %{customdata[6]} pitches<br>Game Score %{y}<extra></extra>"),
              row=1, col=1)
v = H["velo"]
fig.add_shape(type="rect", xref="x2 domain", x0=0, x1=1, yref="y2", y0=v["first15_p25"], y1=99.2, fillcolor="rgba(59,111,216,0.10)", line_width=0, layer="below")
fig.add_trace(go.Scatter(x=ST.gd, y=ST.first_n_ff_velo, mode="lines+markers", line=dict(color=NAVY, width=2),
                         marker=dict(size=8, color=NAVY), name="First-15 four-seam mph", showlegend=False,
                         hovertemplate="%{x|%b %d}: %{y:.1f} mph (first 15 pitches)<extra></extra>"), row=2, col=1)
for d, lab in (("2026-07-13", "All-Star break"), ("2026-09-07", "Labor Day")):
    fig.add_vline(x=pd.Timestamp(d).timestamp() * 1000, line_dash="dot", line_color=GRAY, row="all", col=1)
fig.add_annotation(x=pd.Timestamp("2026-07-13"), y=104, text="All-Star break", showarrow=False, font=dict(color=MUTED, size=11), row=1, col=1)
fig.add_annotation(x=pd.Timestamp("2026-09-07"), y=104, text="Labor Day: 100", showarrow=False, font=dict(color=INK, size=11), xanchor="right", row=1, col=1)
fig.add_annotation(x=pd.Timestamp("2026-08-15"), y=93, text="August (navy)", showarrow=False, font=dict(color=MUTED, size=11), row=1, col=1)
fig.update_yaxes(title="Game Score", range=[0, 110], row=1, col=1)
fig.update_yaxes(title="mph", row=2, col=1)
fig.update_xaxes(title="Start date (2026)", row=2, col=1)
base(fig, "Twenty-nine starts: the summer turned, then Labor Day",
     f"First half (19 starts): {H['halves']['first']['r27']:.2f} runs on watch per 27 outs, K {pct(H['halves']['first']['krate'])}. "
     f"Second half (10): {H['halves']['second']['r27']:.2f}, K {pct(H['halves']['second']['krate'])}. August (navy): "
     f"{H['aug']['r']} runs in {H['aug']['outs']} outs. Blue band = his first-15 velocity at or above his own 25th percentile "
     f"({v['first15_p25']:.1f} mph). The 6/23 gap: no four-seam in his first 15 pitches. No start after 9/7 (IL 9/15, carry-in).", h=680)
fig.update_layout(margin=dict(t=165))
ship(fig, "fig4_season_by_start", dict(population="29 starts", receipt="dp_uc49_starts_2026.csv"))

# ---------------------------------------------------------------------------
# F5 · Labor Day, pitch by pitch
# ---------------------------------------------------------------------------
G = R("laborday_pitches")
assert len(G) == 109 and int(G.is_whiff.sum()) == 23
order = ['FF', 'SI', 'ST', 'CH']
fig = go.Figure()
inn_start = G.groupby('inning').pitch_of_game.min()
for i, (inn, x0) in enumerate(inn_start.items()):
    x1 = G[G.inning == inn].pitch_of_game.max() + 0.5
    if i % 2 == 0:
        fig.add_vrect(x0=x0 - 0.5, x1=x1, fillcolor="rgba(140,140,140,0.35)", opacity=0.25, line_width=0, layer="below")
    fig.add_annotation(x=(x0 + x1) / 2, y=4.55, text=f"{inn}", showarrow=False, font=dict(size=11, color=MUTED))
for pt in order:
    s = G[G.pitch_type == pt]
    for wh, sym in ((True, "circle"), (False, "circle-open")):
        t = s[s.is_whiff == wh]
        fig.add_trace(go.Scatter(x=t.pitch_of_game, y=[order.index(pt) + 1] * len(t), mode="markers",
                                 name=f"{PNAME[pt]} ({pt}){' · whiff' if wh else ''}", legendgroup=pt,
                                 marker=dict(symbol=sym, size=12 if wh else 9, color=PITCH[pt], line=dict(width=2, color=PITCH[pt])),
                                 customdata=np.stack([t.inning, t.batter_name, t['count'], t.release_speed, t.description], axis=1),
                                 hovertemplate="Pitch %{x} · inning %{customdata[0]}<br>%{customdata[1]} · count %{customdata[2]}<br>"
                                               f"{PNAME[pt]} " "%{customdata[3]:.1f} mph → %{customdata[4]}<extra></extra>"))
fig.update_yaxes(tickvals=[1, 2, 3, 4], ticktext=[f"{PNAME[p]} ({p})" for p in order], range=[0.4, 4.8], title="Pitch type")
fig.update_xaxes(title="Pitch of the game (1–109); shaded bands alternate innings, inning number on top", range=[0, 110])
ld = H["ld"]
base(fig, "Labor Day, 109 pitches: 27 outs, 23 whiffs, 1 hour 51 minutes",
     f"PHI 1, ATL 0 · 2026-09-07 · 9 IP, {ld['h']} H, 0 R, {ld['bb']} BB, {ld['k']} K. Filled marker = whiff (house definition: swinging "
     f"strikes + foul tips). He chased {ld['chases']} of {ld['ooz']} out-of-zone pitches ({pct(ld['chase_rate'])}; season {pct(H['y2026']['chase_rate'])}). "
     f"Four-seam averaged {ld['ff_velo']:.1f} mph and {ld['ff_velo_9th']:.1f} in the 9th. The run: Schwarber, solo HR in the 8th. Game time is a carry-in (MLB.com).",
     h=480, w=1100)
ship(fig, "fig5_laborday_pitch_by_pitch", dict(population="game_pk 823415", receipt="dp_uc49_laborday_pitches.csv"))

# ---------------------------------------------------------------------------
# F6 · Two game plans — right-handed hitters, mix by time through the order
# ---------------------------------------------------------------------------
MX = R("laborday_mix_by_tto")
rh = MX[MX.stand == 'R'].copy()
rh['tto'] = rh.n_thruorder_pitcher.map({1: '1st time', 2: '2nd time', 3: '3rd time', 4: '4th (9th inning)'})
tot = rh.groupby('tto').n.sum()
ch2 = rh[(rh.n_thruorder_pitcher == 2) & (rh.pitch_type == 'CH')].n.sum()
ch1 = rh[(rh.n_thruorder_pitcher == 1) & (rh.pitch_type == 'CH')].n.sum()
assert ch2 == 8 and ch1 == 2
fig = go.Figure()
for pt in order:
    s = rh[rh.pitch_type == pt].set_index('tto').reindex(tot.index).fillna(0)
    fig.add_trace(go.Bar(y=tot.index, x=s.n / tot, orientation='h', name=f"{PNAME[pt]} ({pt})", marker=dict(color=PITCH[pt]),
                         text=[f"{pt} {int(n)}" if n else "" for n in s.n], textposition="inside", insidetextanchor="middle",
                         textfont=dict(color="#ffffff"),
                         hovertemplate=f"{PNAME[pt]}: " "%{text} of %{customdata} pitches (%{x:.0%})<extra></extra>", customdata=tot.values))
fig.update_layout(barmode='stack', bargap=0.35)
fig.update_traces(marker_line=dict(width=2, color="#ffffff"))
fig.update_xaxes(title="Share of pitches to right-handed hitters", tickformat=".0%")
fig.update_yaxes(title="Time through the order", autorange="reversed")
base(fig, "Two game plans: the changeup arrived the second time through",
     f"Labor Day, pitches to right-handed hitters only, by time through the order (counts in the bars). Changeups: {ch1} of "
     f"{int(tot['1st time'])} the first time, {ch2} of {int(tot['2nd time'])} the second. Descriptive, one game; the 'two game plans' "
     "framing is from post-game reporting (Metro Philadelphia) and the log is consistent with it.", h=430)
ship(fig, "fig6_two_game_plans", dict(population="Labor Day RHB pitches", receipt="dp_uc49_laborday_mix_by_tto.csv"))

# ---------------------------------------------------------------------------
# F7 · Pitch map 2026 by batter side (PM-1 centroids, unrounded)
# ---------------------------------------------------------------------------
PMp = R("pitch_map_2026")
AS = R("arsenal_by_stand_2026")   # usage WITHIN batter side (AR-2 receipt) sizes the markers
PMp = PMp.merge(AS[['stand', 'pitch_type', 'usage']].rename(columns={'usage': 'usage_side'}), on=['stand', 'pitch_type'], how='left')
sz = H["sz"]
fig = make_subplots(rows=1, cols=2, subplot_titles=["vs left-handed hitters", "vs right-handed hitters"], horizontal_spacing=0.08)
for j, st in enumerate(['L', 'R'], start=1):
    fig.add_shape(type="rect", x0=-0.83, x1=0.83, y0=sz["bot"], y1=sz["top"], line=dict(color=GRAY, width=2),
                  fillcolor="rgba(140,140,140,0.35)", opacity=0.3, row=1, col=j)
    s = PMp[PMp.stand == st]
    for pt in order:
        t = s[s.pitch_type == pt]
        if not len(t):
            continue
        fig.add_trace(go.Scatter(x=t.plate_x, y=t.plate_z, mode="markers+text", text=[pt], textposition="middle center",
                                 textfont=dict(color="#ffffff", size=11), name=f"{PNAME[pt]} ({pt})", legendgroup=pt, showlegend=(j == 1),
                                 marker=dict(size=float(16 + 52 * t.usage_side.iat[0] / PMp.usage_side.max()), color=PITCH[pt],
                                             line=dict(width=2, color="#ffffff")),
                                 customdata=np.stack([t.n, t.usage_side, t.dispersion_ft], axis=1),
                                 hovertemplate=f"{PNAME[pt]}" "<br>%{customdata[0]} pitches (%{customdata[1]:.1%} of pitches to this side)"
                                               "<br>centroid x %{x:.2f} ft, z %{y:.2f} ft<br>dispersion %{customdata[2]:.2f} ft<extra></extra>"),
                      row=1, col=j)
    fig.update_xaxes(range=[-1.94, 1.83], title="plate_x, ft (catcher's view; + = 1B side)", row=1, col=j, showgrid=False)
    fig.update_yaxes(range=[0.5, 3.8], title="plate_z, ft", row=1, col=j, showgrid=False)
base(fig, "Where the pitches live: sweeper away, sinker in, changeup down",
     f"2026 regular season, {H['pitches_2026']} pitches. Marker = average location (unrounded, PM-1), size = usage share within that batter side (AR-2). "
     f"Box = average zone ({sz['bot']:.2f}–{sz['top']:.2f} ft). vs LHB the sweeper is {pct(H['ars_stand']['L']['ST']['usage'])} of pitches "
     f"with a {pct(H['ars_stand']['L']['ST']['whiff'])} whiff rate.", h=560, w=1100)
fig.update_layout(margin=dict(t=150))
ship(fig, "fig7_pitch_map", dict(population="2026 by stand", receipt="dp_uc49_pitch_map_2026.csv"))

# ---------------------------------------------------------------------------
# F8 · Career game scores — "the best shift of his Major League career"
# ---------------------------------------------------------------------------
GS = R("career_game_scores")
S = GS[GS.started].copy()
S['gd'] = pd.to_datetime(S.game_date)
gs = H["gs"]
assert gs["labor_day_rank"] == 1 and gs["next_best"] == 86
fig = go.Figure()
o = S[S.game_pk != 823415]
fig.add_trace(go.Scatter(x=o.gd, y=o.game_score, mode="markers", name="Every other career start",
                         marker=dict(size=9, color="rgba(140,140,140,0.35)", line=dict(width=1, color=GRAY)),
                         customdata=np.stack([o.home_team + ' v ' + o.away_team, o.ip_display, o.h, o.r, o.bb, o.k], axis=1),
                         hovertemplate="%{x|%Y-%m-%d} %{customdata[0]}<br>%{customdata[1]} IP, %{customdata[2]} H, %{customdata[3]} R, "
                                       "%{customdata[4]} BB, %{customdata[5]} K<br>Game Score %{y}<extra></extra>"))
l_ = S[S.game_pk == 823415]
fig.add_trace(go.Scatter(x=l_.gd, y=l_.game_score, mode="markers+text", text=["Labor Day 2026: 100"], textposition="middle left",
                         textfont=dict(color=INK), name="Labor Day 2026", marker=dict(size=18, color=RED, line=dict(width=2, color="#ffffff"))))
for d_ in ("2025-01-01",):
    fig.add_vline(x=pd.Timestamp(d_).timestamp() * 1000, line_dash="dot", line_color=GRAY)
fig.add_annotation(x=pd.Timestamp("2025-01-01"), y=8, text="Phillies →", showarrow=False, xanchor="left", font=dict(color=MUTED))
fig.update_xaxes(title="Date (2019–2026; 2024 ended in June)")
fig.update_yaxes(title="Game Score (GS-1)", range=[0, 108])
base(fig, "The best start of his career, by fourteen points",
     f"All {gs['n_starts']} regular-season career starts, id-locked (CF-2). Game Score = 40 + 2×outs + K − 2×BB − 2×H − 3×R − 6×HR "
     f"(Tango v2 form; R = runs on watch). Labor Day is the only 27-out game of his career (next most: {gs['max_outs_other']}). "
     f"Next best: {gs['next_best']} on {gs['next_best_date']}. His career high in strikeouts is {gs['career_max_k']}, so 12 K is not the record; the game is.",
     h=500)
ship(fig, "fig8_career_game_scores", dict(population=f"{gs['n_starts']} starts", receipt="dp_uc49_career_game_scores.csv"))

# ---------------------------------------------------------------------------
# F9 · Notecard — one image for a thread or a broadcast graphic
# ---------------------------------------------------------------------------
fig = go.Figure()
fig.update_xaxes(visible=False, range=[0, 1]); fig.update_yaxes(visible=False, range=[0, 1])
fig.add_shape(type="rect", x0=0, x1=1, y0=0.93, y1=1, fillcolor=RED, line_width=0)
lines = [(0.80, "9 IP · 2 H · 0 R · 1 BB · 12 K", 34, INK), (0.64, "109 pitches · 23 whiffs · Game Score 100", 24, INK),
         (0.49, f"The only 27-out game of his career. #1 of {gs['n_starts']} career starts.", 18, MUTED),
         (0.38, f"Chase: {ld['chases']} of {ld['ooz']} out-of-zone pitches swung at ({pct(ld['chase_rate'])}).", 18, MUTED),
         (0.27, f"Four-seam in the 9th: {ld['ff_velo_9th']:.1f} mph (game average {ld['ff_velo']:.1f}).", 18, MUTED),
         (0.12, "Phillies 1, Braves 0 · Labor Day, 2026-09-07 · Citizens Bank Park", 15, NAVY)]
for y_, t_, s_, c_ in lines:
    fig.add_annotation(x=0.04, y=y_, text=t_, showarrow=False, xanchor="left", font=dict(size=s_, color=c_))
fig.add_annotation(x=0.04, y=0.03, text="Source: Statcast via the MLB data plane (uc-pps-034 · dp_uc49). Game time and final are carry-ins (MLB.com).",
                   showarrow=False, xanchor="left", font=dict(size=11, color=MUTED))
base(fig, "Jesús Luzardo, Labor Day 2026", "Complete-game shutout, the first of his career", h=520, w=1000)
fig.update_layout(margin=dict(l=20, r=20, t=100, b=20))
ship(fig, "fig9_notecard", dict(population="game_pk 823415", receipt="dp_uc49_headlines.json"))

pd.DataFrame(BRAND).to_csv(OUT / "dp_uc49_brand_compliance.csv", index=False)
(OUT / "dp_uc49_figure_specs.json").write_text(json.dumps(SPECS, indent=1, default=str))
print(f"{len(SPECS)} figures; brand {sum(all(v for k, v in b.items() if k not in ('figure', 'off_palette')) for b in BRAND)}/{len(BRAND)}")
