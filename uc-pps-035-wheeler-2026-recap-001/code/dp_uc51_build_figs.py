"""
dp_uc51_build_figs.py — figures for UC #51 / uc-pps-035 (PNG for the PDF, JSON for the dashboard).

Rules (inherited from dp_uc48/49_build_figs):
  * Reads ONLY out/dp_uc51_* receipts. Nothing here computes a KPI.
  * Each figure asserts the claim its title/subtitle makes before it is written.
  * Print surfaces follow the brand center (`plotly_white` + Arial). The dashboard re-templates the same JSON for dark.
  * PL-2 pitch palette (six pitches; extends uc-pps-034's PL-1): FF red, FS blue, SI amber, ST green, FC violet,
    CU magenta, in usage order. Validated light + dark with the dataviz six-check validator
    (out/dp_uc51_palette_validation.txt): ALL PASS, one adjacent pair (ST/SI, protan ΔE 6.1) in the 6–8 floor band,
    so every pitch mark is also direct-labelled with its code (the secondary encoding the floor band requires).
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
OUT = Path(os.environ.get("DP_UC51_OUT", HERE / "out"))

RED, NAVY, BLUE, GRAY, LGRAY, INK, MUTED = "#E81828", "#002D72", "#284898", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170"
PITCH = {'FF': '#D22D49', 'FS': '#3B6FD8', 'SI': '#C77800', 'ST': '#16945A', 'FC': '#6250D6', 'CU': '#D55181'}
PORDER = ['FF', 'FS', 'SI', 'ST', 'FC', 'CU']
PNAME = {'FF': 'Four-Seam', 'FS': 'Splitter', 'SI': 'Sinker', 'ST': 'Sweeper', 'FC': 'Cutter', 'CU': 'Curveball'}
STAND = {'L': '#284898', 'R': '#D22D49'}
PERIOD = {'first_half': GRAY, 'opener': GRAY, 'stretch': RED, 'finish': NAVY}
PLAB = {'first_half': 'First half (15)', 'opener': '7/21 (1)', 'stretch': 'The stretch, 7/27–8/24 (6)', 'finish': 'The finish, 8/30–9/27 (6)'}
ALLOWED = {RED, NAVY, BLUE, GRAY, LGRAY, INK, MUTED, *PITCH.values(), *STAND.values(), "#ffffff",
           "rgba(232,24,40,0.08)", "rgba(140,140,140,0.35)", "rgba(0,45,114,0.08)", "rgba(140,140,140,0.18)"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=72, r=30, t=118, b=66), legend=dict(orientation="h", y=-0.2, x=0, yanchor="top"))
H = json.loads((OUT / "dp_uc51_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc51_{n}.csv")        # noqa: E731
SPECS, BRAND = [], []
pct = lambda x, d=1: f"{100 * x:.{d}f}%"                    # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0") if x < 1 else f"{x:.3f}"  # noqa: E731


def wrap(t, n=150):
    words, lines, cur = t.split(" "), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return "<br>".join(lines + [cur])


def base(fig, title, subtitle, h=560, w=1000, top=None):
    lay = dict(LAYOUT)
    if top is None:
        top = 168 if any(a.get('font') is not None and a.get('yref') == 'paper' and a.get('showarrow') is False and a.get('y', 0) >= 1
                         for a in fig.to_plotly_json()['layout'].get('annotations', [])) else 118
    lay['margin'] = dict(LAYOUT['margin'], t=top)
    fig.update_layout(**lay, height=h, width=w,
                      title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
                                 subtitle=dict(text=wrap(subtitle), font=dict(size=12.5, color=MUTED))))
    fig.update_xaxes(gridcolor="#eeeeee", zeroline=False); fig.update_yaxes(gridcolor="#eeeeee", zeroline=False)
    return fig


def colors_in(fig):
    js = fig.to_plotly_json(); found = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('color', 'fillcolor', 'bgcolor') and isinstance(v, str):
                    found.add(v)
                elif k == 'color' and isinstance(v, (list, tuple)):
                    found.update(x for x in v if isinstance(x, str))
                else:
                    walk(v)
        elif isinstance(o, (list, tuple)):
            for x in o:
                walk(x)
    walk(js['data']); walk(js['layout'].get('shapes', [])); walk(js['layout'].get('annotations', []))
    return found


def ship(fig, key, meta, png=True):
    lay = fig.layout
    off = sorted(c for c in colors_in(fig) if c not in ALLOWED)
    checks = dict(font_arial=(lay.font.family == 'Arial'), has_title=bool(lay.title.text),
                  has_subtitle=bool(lay.title.subtitle.text),
                  axis_titles=all((lay[a].title.text or '') != '' for a in lay if a.startswith(('xaxis', 'yaxis'))
                                  and lay[a].visible is not False and lay[a].showticklabels is not False and not lay[a].matches),
                  palette_ok=(len(off) == 0))
    BRAND.append(dict(figure=key, **checks, off_palette=";".join(off)))
    assert all(checks.values()), (key, checks, off)
    if png:
        fig.write_image(OUT / f"dp_uc51_{key}.png", scale=2)
    (OUT / f"dp_uc51_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


L26, CS, ER = H['line26'], H['ctx_sw'], H['era_seasons']
YRS = [str(y) for y in range(2020, 2027)]
YAX = dict(tickvals=list(range(2020, 2027)), ticktext=[f"'{y % 100:02d}" for y in range(2020, 2027)], tickangle=0)

# ---------------------------------------------------------------------------
# F1 · Still Zack Wheeler — the starter-workload board (CX-1b, xwOBA × K-BB)
# ---------------------------------------------------------------------------
SW = R("context_starter_workloads")
w26 = SW[(SW.pitcher == 554430) & (SW.game_year == 2026)].iloc[0]
assert int(w26.rank_xwoba) == CS['rank_xwoba'] == 6 and CS['n'] == 41 and CS['wheeler_seasons_top10_xwoba'] == 6
assert abs(w26.xwoba - 0.263) < 0.0005
fig = go.Figure()
oth = SW[SW.pitcher != 554430]
fig.add_trace(go.Scatter(x=oth.k_minus_bb, y=oth.xwoba, mode="markers", name="Other Phillies starter seasons",
                         marker=dict(size=11, color="rgba(140,140,140,0.35)", line=dict(width=1, color="#ffffff")),
                         customdata=np.stack([oth.name, oth.game_year, oth.pitches], axis=1),
                         hovertemplate="%{customdata[0]} %{customdata[1]}<br>K-BB %{x:.1%} · xwOBA %{y:.3f}<br>%{customdata[2]} pitches<extra></extra>"))
wz = SW[SW.pitcher == 554430].sort_values('game_year')
fig.add_trace(go.Scatter(x=wz.k_minus_bb, y=wz.xwoba, mode="markers+text", name="Wheeler seasons (2026 in red)",
                         text=[str(y) for y in wz.game_year], textposition="middle right", textfont=dict(color=INK, size=12),
                         marker=dict(size=[20 if y == 2026 else 13 for y in wz.game_year],
                                     color=[RED if y == 2026 else NAVY for y in wz.game_year], line=dict(width=2, color="#ffffff")),
                         customdata=np.stack([wz.game_year, wz.rank_xwoba], axis=1),
                         hovertemplate="Wheeler %{customdata[0]}<br>K-BB %{x:.1%} · xwOBA %{y:.3f}<br>xwOBA rank %{customdata[1]} of 41<extra></extra>"))
fig.update_yaxes(autorange="reversed", title="xwOBA allowed (lower is better ↑)", tickformat=".3f")
fig.update_xaxes(title="K% minus BB% (higher is better →)", tickformat=".0%")
base(fig, "Still Zack Wheeler: six of the ten best starter seasons by xwOBA since 2015 are his",
     f"Phillies pitcher-seasons with a starter's workload (≥2,000 regular-season pitches), 2015–2026, n = 41. 2026 (red): "
     f"xwOBA {f3(w26.xwoba)}, #{int(w26.rank_xwoba)} of 41; K-BB {pct(w26.k_minus_bb)}, #{int(w26.rank_k_minus_bb)}. "
     f"Phillies-only frame (CX-1b), not MLB-wide. xwOBA = XW-1 (PA-denominated).", h=580)
ship(fig, "fig1_still_wheeler", dict(receipt="context_starter_workloads.csv", claim="rank 6 of 41; 6 of top 10"))

# ---------------------------------------------------------------------------
# F2 · Top-level results by season (client cell 21), small multiples
# ---------------------------------------------------------------------------
RG = R("recap_governed"); RG = RG[RG.era == 'PHI'].sort_values('game_year')
assert H['era_rank']['bbrate']['rank_best'] == 7 and abs(L26['bbrate'] - 0.073) < 0.0005
fig = make_subplots(rows=1, cols=4, subplot_titles=("wOBA and xwOBA allowed", "OPS allowed", "K rate", "BB rate"),
                    horizontal_spacing=0.07)
for i, (cols, fmt) in enumerate([(('woba', 'xwoba'), '.3f'), (('ops',), '.3f'), (('krate',), '.0%'), (('bbrate',), '.1%')], 1):
    for c in cols:
        is_x = c == 'xwoba'
        fig.add_trace(go.Scatter(x=RG.game_year, y=RG[c], mode="lines+markers", showlegend=(i == 1),
                                 name={'woba': 'wOBA', 'xwoba': 'xwOBA'}.get(c, c),
                                 line=dict(width=2, color=GRAY if is_x else NAVY, dash="dot" if is_x else "solid"),
                                 marker=dict(size=[12 if y == 2026 else 8 for y in RG.game_year],
                                             color=[RED if (y == 2026 and not is_x) else (GRAY if is_x else NAVY) for y in RG.game_year],
                                             line=dict(width=1.5, color="#ffffff")),
                                 hovertemplate=f"%{{x}} · {c} %{{y:{fmt}}}<extra></extra>"), row=1, col=i)
    fig.update_yaxes(tickformat=fmt, row=1, col=i, title=dict(text=["wOBA / xwOBA", "OPS", "K per PA", "BB per PA"][i - 1]))
    fig.update_xaxes(**YAX, row=1, col=i, title="Season")
fig.add_annotation(x=2026, y=L26['bbrate'], xref="x4", yref="y4", text=f"{pct(L26['bbrate'])}: highest of his Phillies years",
                   showarrow=True, ax=-60, ay=-30, font=dict(size=11, color=INK))
base(fig, "Results: the walk rate is the one line that set a Phillies-tenure high",
     f"Regular season, 2020–2026, entity-locked to MLBAM 554430. 2026: wOBA {f3(L26['woba'])} (xwOBA {f3(L26['xwoba'])}), "
     f"OPS {f3(L26['ops'])}, K {pct(L26['krate'])}, BB {pct(L26['bbrate'])} over {L26['plate_apps']} PA. BB vs his 2021–25 rate "
     f"({pct(H['base']['bbrate'])}): p = {H['tests']['BB per PA · 2026 vs 2021-25']['p']:.2f}.", h=500, w=1100)
ship(fig, "fig2_results_by_season", dict(receipt="recap_governed.csv", claim="BB 7.3% rank 7 of 7"))

# ---------------------------------------------------------------------------
# F3 · Zone expansion — in-zone × chase, connected by season
# ---------------------------------------------------------------------------
tz, tc = H['tests']['In-zone (tracked) · 2026 vs 2021-25'], H['tests']['Chase (swings / out-of-zone) · 2026 vs 2021-25']
assert H['era_rank']['in_zone_rate']['rank_best'] == 7 and H['era_rank']['chase_rate']['rank_best'] == 1 and tz['p'] < .001
fig = go.Figure()
fig.add_trace(go.Scatter(x=RG.in_zone_rate, y=RG.chase_rate, mode="lines+markers+text", name="Wheeler by season",
                         text=[str(y) for y in RG.game_year], textposition="top center", textfont=dict(size=12, color=INK),
                         line=dict(width=2, color=LGRAY),
                         marker=dict(size=[18 if y == 2026 else 11 for y in RG.game_year],
                                     color=[RED if y == 2026 else NAVY for y in RG.game_year], line=dict(width=2, color="#ffffff")),
                         customdata=np.stack([RG.game_year, RG.edge_rate], axis=1),
                         hovertemplate="%{customdata[0]}<br>in-zone %{x:.1%} · chase %{y:.1%}<br>edge (ER-1) %{customdata[1]:.1%}<extra></extra>"))
fig.update_xaxes(title="In-zone rate (zones 1–9 ÷ tracked pitches)", tickformat=".0%")
fig.update_yaxes(title="Chase rate (swings ÷ out-of-zone pitches)", tickformat=".0%")
base(fig, "Zone expansion: fewer strikes thrown than ever, more chases than ever",
     f"2026 in-zone {pct(L26['in_zone_rate'])} vs {pct(tz['r2'])} in 2021–25 (p < .001); chase {pct(L26['chase_rate'])} vs "
     f"{pct(tc['r2'])} (p = {tc['p']:.3f}). Edge rate (ER-1, within one baseball of the zone line) held at {pct(L26['edge_rate'])} "
     f"vs {pct(H['base']['edge'])} (p = {H['tests']['Edge (ER-1) · 2026 vs 2021-25']['p']:.2f}). Regular season, Phillies tenure.", h=560)
ship(fig, "fig3_zone_expansion", dict(receipt="recap_governed.csv; rate_tests.csv", claim="in-zone lowest, chase highest"))

# ---------------------------------------------------------------------------
# F4 · The stretch — walks and contact by start, the six-start window shaded
# ---------------------------------------------------------------------------
ST = R("starts_2026").sort_values('game_date')
ST['bb_per_pa'] = ST.bb / ST.pa
PSt = H['periods']['stretch']; tb = H['stretch_tests']['BB per PA']
assert PSt['starts'] == 6 and abs(PSt['r27'] - 8.51) < 0.005 and tb['p'] < .01
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                    subplot_titles=("Walks per plate appearance, by start", "xwOBA allowed, by start"))
for r_, c, fmt in ((1, 'bb_per_pa', '.0%'), (2, 'xwoba', '.3f')):
    fig.add_trace(go.Bar(x=ST.game_date, y=ST[c], marker_color=[PERIOD[p] for p in ST.period], showlegend=False,
                         customdata=np.stack([ST.opp, ST.ip_display, ST.bb, ST.pa, ST.r], axis=1),
                         hovertemplate="%{x} vs %{customdata[0]}<br>%{customdata[1]} IP · %{customdata[2]} BB / %{customdata[3]} PA · "
                                       f"%{{customdata[4]}} R<br>{c} %{{y:{fmt}}}<extra></extra>"), row=r_, col=1)
    fig.update_yaxes(tickformat=fmt, row=r_, col=1, title=["BB per PA", "xwOBA"][r_ - 1])
for p, lab in PLAB.items():
    if p != 'opener':
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color=PERIOD[p], name=lab), row=1, col=1)
fig.add_vrect(x0="2026-07-24", x1="2026-08-27", fillcolor="rgba(232,24,40,0.08)", line_width=0, layer="below")
fig.add_vline(x="2026-07-14", line_dash="dot", line_color=GRAY)
fig.add_annotation(x="2026-07-14", y=1.0, yref="y domain", text="All-Star break", showarrow=False, xanchor="left", font=dict(size=11, color=MUTED))
fig.update_xaxes(title="Start date", row=2, col=1)
base(fig, "The walk rate is one six-start stretch, not a season",
     f"Stretch 7/27–8/24: BB {pct(PSt['bbrate'])} ({PSt['walks']} in {PSt['pa']} PA) vs {pct(tb['rest'])} in his other 22 starts "
     f"(p = {tb['p']:.3f}); {PSt['r27']:.2f} runs on watch per 27 outs, which reconciles to the reported 8.51 ERA. "
     f"The finish (8/30–9/27): BB {pct(H['periods']['finish']['bbrate'])}, {H['periods']['finish']['r27']:.2f} runs per 27 outs.", h=640, w=1100)
ship(fig, "fig4_the_stretch", dict(receipt="starts_2026.csv; stretch_tests.csv; stretch_windows.csv", claim="BB 13.4% vs 5.9%, p=.004"))

# ---------------------------------------------------------------------------
# F5 · Where the misses went, and where the ball left the hand
# ---------------------------------------------------------------------------
PE = R("periods_2026"); PE = PE[PE.period != 'opener'].set_index('period').loc[['first_half', 'stretch', 'finish']]
ta = H['stretch_tests']['Arm-side share of clear misses']; tx = H['stretch_tests']['FF release x (ft)']; tz_ = H['stretch_tests']['FF release height (ft)']
assert ta['p'] < .05 and tx['p'] > .2 and tz_['p'] > .2
fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.12,
                    subplot_titles=("Clear misses by side (share of misses)", "Four-seam release point by start (catcher's view)"))
sides = [('miss_arm_share', 'Arm side', RED), ('miss_glove_share', 'Glove side', MUTED), ('miss_high_share', 'High', GRAY), ('miss_low_share', 'Low', LGRAY)]
labs = [PLAB[p].split(' (')[0].replace(', 7/27–8/24', '').replace(', 8/30–9/27', '') for p in PE.index]
for c, nm, col in sides:
    fig.add_trace(go.Bar(y=labs, x=PE[c], orientation="h", name=nm, marker=dict(color=col, line=dict(color="#ffffff", width=2)),
                         text=[pct(v, 0) for v in PE[c]], textposition="inside", insidetextanchor="middle",
                         hovertemplate=f"%{{y}} · {nm} %{{x:.1%}}<extra></extra>"), row=1, col=1)
fig.update_layout(barmode="stack")
fig.update_xaxes(tickformat=".0%", title="Share of clear misses (>2 baseballs outside the zone)", row=1, col=1)
fig.update_yaxes(title="Period", autorange="reversed", row=1, col=1)
for grp, s in (('Other 2026 start', ST[ST.period != 'stretch']), ('Stretch start (7/27–8/24)', ST[ST.period == 'stretch'])):
    st_ = grp.startswith('Stretch')
    fig.add_trace(go.Scatter(x=s.rel_x, y=s.rel_z, mode="markers", name=grp,
                             marker=dict(size=13 if st_ else 9, color=RED if st_ else GRAY, line=dict(width=1.5, color="#ffffff")),
                             customdata=np.stack([s.game_date, s.opp], axis=1),
                             hovertemplate="%{customdata[0]} vs %{customdata[1]}<br>release x %{x:.2f} ft · height %{y:.2f} ft<extra></extra>"),
                  row=1, col=2)
fig.update_xaxes(title="Release x (ft; − = third-base side)", row=1, col=2)
fig.update_yaxes(title="Release height (ft)", row=1, col=2)
base(fig, "The misses moved arm side during the stretch; the release point did not move",
     f"Arm-side share of clear misses: {pct(ta['stretch'])} in the stretch vs {pct(ta['rest'])} otherwise (p = {ta['p']:.3f}). "
     f"Four-seam release x {tx['stretch']:.2f} vs {tx['rest']:.2f} ft (p = {tx['p']:.2f}), height {tz_['stretch']:.2f} vs {tz_['rest']:.2f} ft "
     f"(p = {tz_['p']:.2f}), start means, Welch. Reported cause (a dropped glove, over-rotation) is a carry-in; the log cannot see a glove.",
     h=560, w=1100)
ship(fig, "fig5_misses_and_release", dict(receipt="periods_2026.csv; starts_2026.csv; stretch_tests.csv", claim="arm-side 25.5 vs 17.8, p=.033; release flat"))

# ---------------------------------------------------------------------------
# F6 · Contact quality — "most of the other results appear to just be noise"
# ---------------------------------------------------------------------------
tests = {k: H['tests'][f'{k} · 2026 vs 2021-25'] for k in ('Hard-hit per BIP', 'Barrel per BIP', 'Line drive per BIP')}
assert all(t['p'] > .3 for t in tests.values())
fig = make_subplots(rows=1, cols=3, subplot_titles=("Hard-hit rate (≥95 mph)", "Barrel rate", "Line-drive rate"), horizontal_spacing=0.08)
for i, (c, k) in enumerate([('hard_hit_rate', 'Hard-hit per BIP'), ('barrel_rate', 'Barrel per BIP'), ('line_drive_rate', 'Line drive per BIP')], 1):
    b = tests[k]['r2']
    fig.add_hline(y=b, line_dash="dot", line_color=GRAY, row=1, col=i)
    fig.add_trace(go.Scatter(x=RG.game_year, y=RG[c], mode="lines+markers", showlegend=False, line=dict(width=2, color=NAVY),
                             marker=dict(size=[12 if y == 2026 else 8 for y in RG.game_year],
                                         color=[RED if y == 2026 else NAVY for y in RG.game_year], line=dict(width=1.5, color="#ffffff")),
                             hovertemplate=f"%{{x}} · %{{y:.1%}}<extra></extra>"), row=1, col=i)
    fig.update_yaxes(tickformat=".0%", title="Share of balls in play", row=1, col=i)
    fig.update_xaxes(**YAX, title="Season", row=1, col=i)
base(fig, "Contact quality: nothing moved beyond noise",
     "Dotted line = his pooled 2021–25 rate. 2026 vs that baseline: " + "; ".join(
         f"{k.split(' per')[0].lower()} {pct(t['r1'])} vs {pct(t['r2'])} (p = {t['p']:.2f})" for k, t in tests.items())
     + f". {L26['bips']} balls in play in 2026.", h=480, w=1100)
ship(fig, "fig6_contact_quality", dict(receipt="recap_governed.csv; rate_tests.csv", claim="all p > .3"))

# ---------------------------------------------------------------------------
# F7 · Tied-up rate — the population, named
# ---------------------------------------------------------------------------
JP = R("tied_up_population").sort_values('tied_up_rate')
tp = H['tied_pop']
assert tp['rank'] == 11 and tp['n'] == 45 and tp['rank_big'] == 6
JP['lab'] = JP.name + " " + JP.game_year.astype(str)
isw = JP.pitcher == 554430
fig = go.Figure()
fig.add_trace(go.Scatter(x=JP.tied_up_rate, y=JP.tracked_swings, mode="markers", name="Phillies pitcher-seasons 2025–26",
                         marker=dict(size=10, color=["rgba(140,140,140,0.35)" if not w else (RED if y == 2026 else NAVY)
                                                     for w, y in zip(isw, JP.game_year)], line=dict(width=1, color="#ffffff")),
                         customdata=JP.lab, hovertemplate="%{customdata}<br>tied-up %{x:.1%} of %{y} tracked swings<extra></extra>"))
for _, r_ in JP[isw].iterrows():
    fig.add_annotation(x=r_.tied_up_rate, y=r_.tracked_swings, text=f"Wheeler {r_.game_year}", showarrow=True, ax=40, ay=-25,
                       font=dict(size=12, color=INK))
fig.add_vline(x=tp['mean'], line_dash="dot", line_color=GRAY, annotation_text=f"mean {pct(tp['mean'])}",
              annotation_font_color=MUTED, annotation_position="top")
fig.update_xaxes(title="Tied-up rate (JR-1: tracked swings with intercept < 32.5 in)", tickformat=".0%")
fig.update_yaxes(title="Tracked swings")
base(fig, "Tied-up rate: above the room, not at the top of it",
     f"Phillies pitcher-seasons 2025–26 with ≥50 tracked swings (JR-1 floor), keyed by MLBAM id, n = {tp['n']}. Wheeler 2026: "
     f"{pct(tp['value'])}, #{tp['rank']} of {tp['n']}; #{tp['rank_big']} of {tp['n_big']} with ≥500 tracked swings. Leader: "
     f"{tp['leader']['name']} {tp['leader']['game_year']} ({pct(float(tp['leader']['tied_up_rate']))}). A public-data proxy for "
     "Savant's swing-timing bucket, not Savant's number.", h=560)
ship(fig, "fig7_tied_up_population", dict(receipt="tied_up_population.csv", claim="rank 11 of 45"))

# ---------------------------------------------------------------------------
# F8 · Swing timing by pitch × batter side (ST-1)
# ---------------------------------------------------------------------------
SP = R("swing_timing_by_pitch_stand_2026")
si = H['si_jam']
assert si['bip'] == 55 and si['swings'] == 124
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("vs left-handed batters", "vs right-handed batters"),
                    horizontal_spacing=0.06)
for j, sd in enumerate(['L', 'R'], 1):
    d = SP[SP.stand == sd].set_index('pitch_type').reindex(PORDER).dropna(subset=['tracked_swings'])
    for b, nm, col in (('tied_up_rate', 'Tied-up', NAVY), ('centered_rate', 'Centered', LGRAY), ('flail_rate', 'Flail', GRAY)):
        fig.add_trace(go.Bar(y=[PNAME[p] for p in d.index], x=d[b], orientation="h", name=nm, showlegend=(j == 1),
                             marker=dict(color=col, line=dict(color="#ffffff", width=2)),
                             text=[pct(v, 0) for v in d[b]], textposition="inside", insidetextanchor="middle",
                             customdata=np.stack([d.tracked_swings.astype(int), d.below_floor], axis=1),
                             hovertemplate=f"%{{y}} · {nm} %{{x:.1%}}<br>%{{customdata[0]}} tracked swings · below floor %{{customdata[1]}}<extra></extra>"),
                      row=1, col=j)
    fig.update_xaxes(tickformat=".0%", title="Share of tracked swings", row=1, col=j)
fig.update_layout(barmode="stack"); fig.update_yaxes(title="Pitch", autorange="reversed", row=1, col=1)
base(fig, "Swing timing by pitch: the sinker ties up righties",
     f"ST-1 buckets of tracked swings, 2026: tied-up < 32.5 in (JR-1) · centered 32.5–41 in · flail > 41 in (provisional, the client's "
     f"histogram line). Sinker vs RHB: {si['swings']} tied-up swings, {si['bip']} in play, {si['hits']} hits, {si['ev']:.1f} mph average EV, "
     f"{pct(si['gb_share'], 0)} grounders.", h=520, w=1100)
ship(fig, "fig8_swing_timing_by_pitch", dict(receipt="swing_timing_by_pitch_stand_2026.csv", claim="SI vs RHB 55 BIP"))

# ---------------------------------------------------------------------------
# F9 · Platoon — the client's wOBA-by-season scatter, governed
# ---------------------------------------------------------------------------
PLt = R("platoon_by_season").sort_values('game_year')
pt = H['platoon_tests']['Hard-hit']
assert pt['p'] < .01 and H['platoon']['2026L']['woba'] > H['platoon']['2026R']['woba']
fig = make_subplots(rows=1, cols=2, subplot_titles=("wOBA allowed", "xwOBA allowed"), horizontal_spacing=0.08)
for j, c in enumerate(['woba', 'xwoba'], 1):
    for sd in ('L', 'R'):
        d = PLt[PLt.stand == sd]
        fig.add_trace(go.Scatter(x=d.game_year, y=d[c], mode="lines+markers+text", name=f"vs {sd}HB", showlegend=(j == 1),
                                 text=[f3(v) if y == 2026 else "" for v, y in zip(d[c], d.game_year)], textposition="top center",
                                 textfont=dict(size=11, color=INK), line=dict(width=2, color=STAND[sd]),
                                 marker=dict(size=np.clip(np.sqrt(d.plate_apps) / 1.6, 6, 18), color=STAND[sd], line=dict(width=1.5, color="#ffffff")),
                                 customdata=d.plate_apps, hovertemplate=f"%{{x}} vs {sd}HB · {c} %{{y:.3f}} · %{{customdata}} PA<extra></extra>"),
                      row=1, col=j)
    fig.update_yaxes(tickformat=".3f", title=["wOBA", "xwOBA"][j - 1], row=1, col=j)
    fig.update_xaxes(**YAX, title="Season", row=1, col=j)
p26 = H['platoon']
base(fig, "Platoon: lefties did more damage, and it shows in contact quality",
     f"2026 vs LHB: wOBA {f3(p26['2026L']['woba'])} / xwOBA {f3(p26['2026L']['xwoba'])} over {p26['2026L']['pa']} PA; vs RHB "
     f"{f3(p26['2026R']['woba'])} / {f3(p26['2026R']['xwoba'])} over {p26['2026R']['pa']} PA. Hard-hit {pct(pt['L'])} vs {pct(pt['R'])} "
     f"(p = {pt['p']:.3f}). Marker size = PA. The gap was wider in 2024 ({f3(H['platoon_gap']['2024'])} wOBA).", h=500, w=1100)
ship(fig, "fig9_platoon", dict(receipt="platoon_by_season.csv; platoon_tests.csv", claim="HH 41.9 vs 25.7, p=.001"))

# ---------------------------------------------------------------------------
# F10 · Pitch map 2026 (PM-1) by batter side
# ---------------------------------------------------------------------------
PM = R("pitch_map_2026")
sz = H['sz']
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("vs left-handed batters", "vs right-handed batters"),
                    horizontal_spacing=0.05)
for j, sd in enumerate(['L', 'R'], 1):
    fig.add_shape(type="rect", x0=-0.83, x1=0.83, y0=sz['bot'], y1=sz['top'], line=dict(color=GRAY, width=1.5),
                  fillcolor="rgba(140,140,140,0.18)", layer="below", row=1, col=j)
    d = PM[PM.stand == sd]
    for p in PORDER:
        s = d[d.pitch_type == p]
        if not len(s):
            continue
        fig.add_trace(go.Scatter(x=s.plate_x, y=s.plate_z, mode="markers+text", name=PNAME[p], showlegend=(j == 1), text=[p],
                                 textposition="middle center", textfont=dict(size=11, color="#ffffff"),
                                 marker=dict(size=np.clip(s.usage * 130, 26, 56), color=PITCH[p], line=dict(width=2, color="#ffffff")),
                                 customdata=np.stack([s.usage, s.n, s.dispersion_ft], axis=1),
                                 hovertemplate=f"{PNAME[p]} vs {sd}HB<br>usage %{{customdata[0]:.1%}} · %{{customdata[1]}} pitches<br>"
                                               "centre (%{x:.2f}, %{y:.2f}) ft · spread %{customdata[2]:.2f} ft<extra></extra>"), row=1, col=j)
    fig.update_xaxes(range=[-1.94, 1.83], title="Plate x (ft, catcher's view; + = first-base side)", row=1, col=j)
fig.update_yaxes(range=[0.5, 4.0], title="Plate height (ft)", row=1, col=1)
base(fig, "Pitch map: where each pitch lives, by batter side (2026)",
     f"Average location (PM-1 centroid, unrounded) of each pitch type; marker size = share of that side's pitches. "
     f"Shaded box = rulebook zone at his average zone ({sz['bot']:.2f}–{sz['top']:.2f} ft). {L26['pitches']:,} regular-season pitches.",
     h=600, w=1100)
ship(fig, "fig10_pitch_map", dict(receipt="pitch_map_2026.csv", claim="PM-1 centroids"))

# ---------------------------------------------------------------------------
# F11 · Pitch plot — movement, 2026, and the YoY change
# ---------------------------------------------------------------------------
PT_ = R("wheeler_pitches_2026")
AR = R("arsenal_by_season")
a26 = AR[AR.game_year == 2026].set_index('pitch_type'); a25 = AR[AR.game_year == 2025].set_index('pitch_type')
assert a26.loc['FS', 'usage'] > a25.loc['FS', 'usage']
fig = go.Figure()
for p in PORDER:
    s = PT_[PT_.pitch_type == p]
    fig.add_trace(go.Scatter(x=s.hb_in, y=s.ivb_in, mode="markers", name=f"{PNAME[p]} ({pct(a26.loc[p, 'usage'], 0)})",
                             marker=dict(size=5, color=PITCH[p], opacity=0.45), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[a26.loc[p, 'hb_in']], y=[a26.loc[p, 'ivb_in']], mode="markers+text", showlegend=False, text=[p],
                             textposition="middle center", textfont=dict(size=10, color="#ffffff"),
                             marker=dict(size=26, color=PITCH[p], line=dict(width=2, color="#ffffff")),
                             hovertemplate=f"{PNAME[p]} 2026<br>{a26.loc[p, 'velo']:.1f} mph · IVB %{{y:.1f}} in · HB %{{x:.1f}} in<br>"
                                           f"usage {a26.loc[p, 'usage']:.1%} · whiff {a26.loc[p, 'whiff_rate']:.1%}<extra></extra>"))
fig.update_xaxes(title="Horizontal break (in, catcher's view; − = arm side for a RHP)", zeroline=True, zerolinecolor=LGRAY)
fig.update_yaxes(title="Induced vertical break (in)", zeroline=True, zerolinecolor=LGRAY)
base(fig, "Pitch plot: the splitter became his second pitch",
     f"Every 2026 regular-season pitch (pfx × 12); large markers = pitch-type means. Splitter usage {pct(a25.loc['FS', 'usage'])} → "
     f"{pct(a26.loc['FS', 'usage'])}, whiff {pct(a26.loc['FS', 'whiff_rate'])}. Sinker whiff {pct(a26.loc['SI', 'whiff_rate'])} "
     f"(lowest of the six). Four-seam {a26.loc['FF', 'velo']:.1f} mph (2025: {a25.loc['FF', 'velo']:.1f}).", h=620)
ship(fig, "fig11_pitch_plot", dict(receipt="wheeler_pitches_2026.csv; arsenal_by_season.csv", claim="FS 8.9% -> 16.3%"))

# ---------------------------------------------------------------------------
# F12 · The Still-Wheeler card for 2027 (OC-1, second use)
# ---------------------------------------------------------------------------
CARD = R("still_wheeler_card"); BT = R("still_wheeler_backtest_2026")
C = H['card']
assert C['on'] == 20 and C['off'] == 8 and C['on_r27'] < C['off_r27'] and C['backtest_by_period']['finish'] == '6/6'
sig = ST.rename(columns={'chase_rate': 'chase_rate', 'bb_rate': 'bb_rate'})
fig = make_subplots(rows=1, cols=4, subplot_titles=("A · Arm: four-seam, first 15", "B · The chase", "C · Swing-and-miss", "D · Control"),
                    horizontal_spacing=0.07)
cols = {'OC-A': ('first_n_ff_velo', '.1f', 'mph, first 15 pitches'), 'OC-B': ('chase_rate', '.0%', 'chase rate'),
        'OC-C': ('whiff_per_100', '.1f', 'whiffs per 100'), 'OC-D': ('bb_rate', '.0%', 'walks per PA')}
for j, sid in enumerate(['OC-A', 'OC-B', 'OC-C', 'OC-D'], 1):
    c, fmt, ttl = cols[sid]
    jitter = (np.arange(len(sig)) % 7 - 3) * 0.05
    fig.add_trace(go.Scatter(x=jitter, y=sig[c], mode="markers", showlegend=False,
                             marker=dict(size=9, color=[PERIOD[p] for p in sig.period], line=dict(width=1, color="#ffffff")),
                             customdata=np.stack([sig.game_date, sig.opp], axis=1),
                             hovertemplate=f"%{{customdata[0]}} vs %{{customdata[1]}} · %{{y:{fmt}}}<extra></extra>"), row=1, col=j)
    fig.add_hline(y=C['bars'][sid], line_color=RED, line_width=2, row=1, col=j)
    fig.add_hline(y=C['bars_prime'][sid], line_color=NAVY, line_dash="dot", line_width=2, row=1, col=j)
    fig.add_trace(go.Scatter(x=[0.35], y=[C['wc_values'][c]], mode="markers+text", text=["WC G3"], textposition="middle right",
                             textfont=dict(size=10, color=INK), showlegend=False,
                             marker=dict(size=13, symbol="diamond", color=INK, line=dict(width=1, color="#ffffff")),
                             hovertemplate=f"Wild Card G3 relief (post hoc) · %{{y:{fmt}}}<extra></extra>"), row=1, col=j)
    fig.update_yaxes(tickformat=fmt, title=ttl, row=1, col=j)
    fig.update_xaxes(showticklabels=False, range=[-0.4, 0.9], title="2026 starts", row=1, col=j)
fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=RED, width=2), name="2027 bar (his 2026 edge)"), row=1, col=1)
fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=NAVY, width=2, dash="dot"), name="Same rule on 2021–25"), row=1, col=1)
for p in ('first_half', 'stretch', 'finish'):
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=9, color=PERIOD[p]), name=PLAB[p].split(' (')[0]), row=1, col=1)
base(fig, "The Still-Wheeler card: what 2027 has to look like, written down first",
     f"OC-1 rule (uc-pps-034), second use: a start is ON-SCRIPT when ≥3 of 4 hold. Bars = his 2026 starts at the 25th percentile "
     f"(75th for walks); registered 2026-10-12, before any 2027 pitch. Backtest: on-script starts {C['on']} ({C['on_r27']:.2f} runs per 27 outs), "
     f"off-script {C['off']} ({C['off_r27']:.2f}); the finish 6/6. Wild Card G3 relief, graded after the fact: {C['wc_posthoc']['verdict']}.",
     h=560, w=1150)
ship(fig, "fig12_still_wheeler_card", dict(receipt="still_wheeler_card.csv; still_wheeler_backtest_2026.csv", claim="20 on / 8 off"))

# ---------------------------------------------------------------------------
# F13 · Notecard (one image, one line)
# ---------------------------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Bar(x=[s[5:] for s in ST.game_date.astype(str)], y=ST.xwoba, marker_color=[PERIOD[p] for p in ST.period],
                     showlegend=False, hovertemplate="%{x} · xwOBA %{y:.3f}<extra></extra>"))
fig.add_hline(y=L26['xwoba'], line_dash="dot", line_color=NAVY, annotation_text=f"season xwOBA {f3(L26['xwoba'])}",
              annotation_position="top right", annotation_font_color=INK)
fig.update_xaxes(title="2026 start (month-day)", tickangle=-60, type="category"); fig.update_yaxes(title="xwOBA allowed", tickformat=".3f")
base(fig, f"Zack Wheeler, 2026: {L26['games']} starts, {H['carry']['ip']} IP, {L26['strikeouts']} K, xwOBA {f3(L26['xwoba'])}",
     f"Six of the ten best Phillies starter seasons by xwOBA since 2015 are his. The red bars are the six-start stretch "
     f"(7/27–8/24, {pct(PSt['bbrate'])} walks); the navy bars are the finish ({H['periods']['finish']['r27']:.2f} runs per 27 outs). "
     "Still Zack Wheeler.", h=620, w=1000)
ship(fig, "fig13_notecard", dict(receipt="starts_2026.csv; headlines.json", claim="notecard"))

pd.DataFrame(BRAND).to_csv(OUT / "dp_uc51_brand_compliance.csv", index=False)
(OUT / "dp_uc51_figure_specs.json").write_text(json.dumps(SPECS, indent=1))
print(pd.DataFrame(BRAND).to_string())
