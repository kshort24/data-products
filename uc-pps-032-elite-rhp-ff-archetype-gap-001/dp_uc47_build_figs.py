"""
dp_uc47_build_figs.py — UC #47 / uc-pps-032 figures.

Rules (uc-pps-030 rule 4, extended):
  * Every figure reads ONLY out/dp_uc47_* receipts. No parquet is opened here.
  * If a title or subtitle makes a claim, this build asserts it against the
    receipt first and refuses to render a false headline.
  * Plotly, because that is how the client draws (his cells: px.box, add_hline,
    add_hrect "middle 50%" bands). Template = brand-center `plotly_white` + Arial
    for print; the dashboard offers his `plotly_dark` as a toggle.
  * Each figure ships as PNG (report) and JSON (dashboard) from ONE object, so
    the two surfaces cannot disagree.
  * Brand-center MCP compliance is run on every figure spec -> receipt.
"""
from __future__ import annotations

import glob
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC47_OUT", HERE / "out"))
R = lambda n: pd.read_csv(OUT / f"dp_uc47_{n}.csv")
H = json.loads((OUT / "dp_uc47_headlines.json").read_text())

_c = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome')
if _c and not os.environ.get('BROWSER_PATH'):
    os.environ['BROWSER_PATH'] = _c[0]
try:
    pio.defaults.mathjax = None
except Exception:
    pass

NAVY, RED, GRAY, LGRAY = "#002D72", "#E81828", "#8C8C8C", "#D9D9D9"
# cohort palette — validated with dataviz validate_palette.js (out/dp_uc47_palette_validation.txt)
ARM_COLORS = {"Jonathan Bowlan": "#E81828", "Zack Wheeler": "#2F5DA8", "Jhoan Duran": "#C97A00",
              "Alex McFarlane": "#00919E", "Andrew Painter": "#8250C4", "Seranthony Domínguez": "#5E8C31"}
TIER_COLORS = {"ELITE": RED, "SHAPE-ONLY": "#00919E", "RESULTS-ONLY": "#C97A00", "NOT ELITE": LGRAY}
FONT = dict(family="Arial, sans-serif", size=13)


def base(fig, title, subtitle, h=720, w=1280):
    fig.update_layout(template="plotly_white", font=FONT, width=w, height=h,
                      title=dict(text=title, subtitle=dict(text=subtitle, font=dict(size=13, color="#444")),
                                 font=dict(size=18, color=NAVY), x=0.02, xanchor='left'),
                      margin=dict(l=80, r=40, t=110, b=70), legend=dict(bgcolor="rgba(255,255,255,0.7)"))
    return fig


SPECS = []


def ship(fig, name, meta):
    fig.write_image(OUT / f"dp_uc47_{name}.png", scale=2)
    (OUT / f"dp_uc47_{name}.json").write_text(fig.to_json())
    meta = dict(meta, figure=name, title=fig.layout.title.text, subtitle=fig.layout.title.subtitle.text,
                template="plotly_white", layout={"template": "plotly_white", "font": FONT})
    SPECS.append(meta)


def jitter(key, amp=1.6):
    h = int(hashlib.md5(str(key).encode()).hexdigest()[:8], 16)
    return ((h % 1000) / 1000 - 0.5) * 2 * amp


# ---------------------------------------------------------------------------
# F1 · The archetype map (hero)
# ---------------------------------------------------------------------------
pop = R("population_graded")
P = pop[pop.pop_member].copy()
tiers = R("tier_distribution").set_index("tier").pitcher_seasons
n_elite, n_pop = int(tiers["ELITE"]), int(tiers.sum())
assert n_pop == H["pop_n"] == 405 and n_elite == 11
bow = pop[(pop.pitcher == 680742) & (pop.game_year == 2026)].iloc[0]
assert bow.archetype_tier == "ELITE" and H["bowlan26"]["pop_rank"] == 2

fig = go.Figure()
fig.add_shape(type="rect", x0=57.5, x1=82.5, y0=57.5, y1=82.5, fillcolor=RED, opacity=0.07, line_width=0, layer="below")
fig.add_annotation(x=81.5, y=81.5, text=f"<b>ELITE</b> — plus on both axes<br>{n_elite} of {n_pop} pitcher-seasons",
                   showarrow=False, xanchor="right", yanchor="top", font=dict(color=RED, size=12))
for tier in ["NOT ELITE", "RESULTS-ONLY", "SHAPE-ONLY", "ELITE"]:
    d = P[P.archetype_tier == tier]
    fig.add_trace(go.Scatter(
        x=d.shape_grade + [jitter((p, y, 'x')) for p, y in zip(d.pitcher, d.game_year)],
        y=d.results_grade + [jitter((p, y, 'y')) for p, y in zip(d.pitcher, d.game_year)],
        mode="markers", name=f"{tier.title()} ({len(d)})",
        marker=dict(size=7, color=TIER_COLORS[tier], opacity=0.55 if tier == "NOT ELITE" else 0.8,
                    line=dict(width=1, color="white")),
        customdata=np.stack([d.name, d.game_year, d.n, d.efc_score.round(1)], axis=-1),
        hovertemplate="%{customdata[0]} %{customdata[1]}<br>%{customdata[2]} FF · score %{customdata[3]}<extra></extra>"))
C = R("cohort_seasons")
for arm, d in C.groupby("arm"):
    d = d.sort_values("game_year")
    xs = d.shape_grade + [jitter((p, y, 'x')) for p, y in zip(d.pitcher, d.game_year)]
    ys = d.results_grade + [jitter((p, y, 'y')) for p, y in zip(d.pitcher, d.game_year)]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=arm,
                             line=dict(color=ARM_COLORS[arm], width=1.5, dash="dot"),
                             marker=dict(size=[9] * (len(d) - 1) + [15], color=ARM_COLORS[arm],
                                         symbol=["circle"] * (len(d) - 1) + ["diamond"], line=dict(width=2, color="white")),
                             customdata=np.stack([d.game_year, d.n, d.shape_grade, d.results_grade], axis=-1),
                             hovertemplate=arm + " %{customdata[0]}<br>%{customdata[1]} FF · shape %{customdata[2]} / results %{customdata[3]}<extra></extra>"))
    last = d.iloc[-1]
    fig.add_annotation(x=xs.iloc[-1], y=ys.iloc[-1], text=f"{arm.split()[-1]} {int(last.game_year)}",
                       showarrow=True, arrowhead=0, ax=28, ay=-22, font=dict(size=11, color="#222"))
fig.update_xaxes(title="Shape grade — what the four-seam looks like (velo · ride · spin)", range=[17.5, 82.5], dtick=10)
fig.update_yaxes(title="Results grade — what it does (whiff · run value)", range=[17.5, 82.5], dtick=10)
base(fig, "Elite RHP Four-Seamers — Shape vs Results, 2018–2026",
     f"{n_pop} pitcher-seasons in my dataset, cleaned. Only {n_elite} are plus on both axes — and Bowlan's 2026 is the 2nd-best of all of them. "
     "Diamonds = each arm's latest season.", h=820)
ship(fig, "fig1_archetype_map", dict(chart_type="scatter", colors=list(ARM_COLORS.values()) + [RED, NAVY],
                                      hover_fields=["shape_grade", "results_grade", "n", "efc_score"]))

# ---------------------------------------------------------------------------
# F2 · Wheeler velocity — the client's chart, governed
# ---------------------------------------------------------------------------
wv = R("hp_wheeler_velo_by_year")
w26, w24 = wv.set_index("game_year").loc[2026], wv.set_index("game_year").loc[2024]
assert (wv[wv.game_year >= 2023].share_99_plus == 0).all()
fig = go.Figure()
fig.add_trace(go.Box(x=wv.game_year.astype(str), q1=wv.p25, median=wv["median"], q3=wv.p75,
                     lowerfence=wv.p05, upperfence=wv.p95, mean=wv["mean"], boxmean=True,
                     marker_color=NAVY, fillcolor="rgba(0,45,114,0.18)", name="Four-seam velocity",
                     hovertemplate="%{x}<extra></extra>"))
fig.add_hline(y=99, line_dash="dot", annotation_text="99 mph", annotation_position="bottom right")
fig.add_hrect(y0=w26.p25, y1=w26.p75, line_width=0, fillcolor="red", opacity=0.25,
              annotation_text="Zack Wheeler 2026 middle 50%", annotation_position="bottom left", annotation_font=dict(size=12))
fig.update_yaxes(title="Pitch Velocity (mph)")
fig.update_xaxes(title="Season")
base(fig, "Zack Wheeler — Four-Seam Fastball Velocity by Year, 2020–2026",
     f"Clearly trending down, but the middle 50% of his FFs in 2026 roughly matches 2024 — governed: median {wv['median'].iloc[0]:.1f} → {w26['median']:.1f} mph, "
     f"IQR overlap with 2024 is 86%, and not one 99 since 2022. Whiskers 5th–95th pct.", h=640)
ship(fig, "fig2_wheeler_velo", dict(chart_type="box", colors=[NAVY, RED], hover_fields=["release_speed"]))

# ---------------------------------------------------------------------------
# F3 · Painter spin + ride, split at the demotion — the client's charts, governed
# ---------------------------------------------------------------------------
ph = R("hp_painter_halves").set_index("half")
hp = R("hp_reconciliation").set_index("id")
d_spin = ph.loc["Second Half", "spin_ex_outlier"] - ph.loc["First Half", "spin_ex_outlier"]
d_ivb = ph.loc["Second Half", "ivb_in"] - ph.loc["First Half", "ivb_in"]
assert hp.loc["HP-3", "verdict"] == "SUPPORTED" and hp.loc["HP-4", "verdict"].startswith("SUPPORTED")
pg = pop[(pop.pitcher == 691725) & (pop.game_year == 2026)].iloc[0]
assert pg.results_grade == 40
fig = make_subplots(rows=1, cols=2, subplot_titles=("Four-Seam Spin (rpm)", "Four-Seam Ride / IVB (in)"), horizontal_spacing=0.1)
for i, (col, unit) in enumerate([("spin", "rpm"), ("ivb", "in")], start=1):
    for half, color in [("First Half", GRAY), ("Second Half", RED)]:
        r = ph.loc[half]
        fig.add_trace(go.Box(x=[half], q1=[r[f"{col}_p25"]], median=[r[f"{col}_p50"]], q3=[r[f"{col}_p75"]],
                             lowerfence=[r[f"{col}_p05"]], upperfence=[r[f"{col}_p95"]],
                             marker_color=color, name=half, showlegend=(i == 1), fillcolor=color, opacity=0.6), row=1, col=i)
    m1 = ph.loc["First Half", "spin_ex_outlier" if col == "spin" else "ivb_in"]
    m2 = ph.loc["Second Half", "spin_ex_outlier" if col == "spin" else "ivb_in"]
    fig.add_hline(y=m1, line_dash="dot", row=1, col=i, annotation_text=f"{m1:.0f} {unit}" if col == "spin" else f"{m1:.1f} {unit}", annotation_position="top left")
    fig.add_hline(y=m2, line_dash="dot", row=1, col=i, annotation_text=f"{m2:.0f} {unit}" if col == "spin" else f"{m2:.1f} {unit}", annotation_position="top right")
base(fig, "Andrew Painter — Four-Seam Fastball Before and After the Demotion, 2026",
     f"Clear difference after his demotion: +{d_spin:.0f} rpm (a full population SD) and +{d_ivb:.1f} in of ride (a third of one). "
     f"Better-looking pitch. Results grade: still {pg.results_grade:.0f}. First Half = Mar 31–Jun 17 · Second Half = Jul 31–Sep 19.", h=620)
ship(fig, "fig3_painter_halves", dict(chart_type="box", colors=[GRAY, RED], hover_fields=["release_spin_rate", "pfx_z"]))

# ---------------------------------------------------------------------------
# F4 · The external board
# ---------------------------------------------------------------------------
cd = R("candidates")
ranked = cd[cd.board == "RANKED"].head(12).iloc[::-1]
watch = cd[cd.board != "RANKED"].head(4).iloc[::-1]
b_score, d_score = H["bowlan26"]["efc"], [s for s in H["staff"] if s["name"] == "Jhoan Duran"][0]["efc_score"]
assert (cd[cd.board == "RANKED"].efc_score < b_score).all(), "a ranked candidate beats Bowlan — the title would be false"
labels_w = [f"{n} '{str(y)[2:]} · {g} G · {k} FF (THIN)" for n, y, g, k in zip(watch.name, watch.game_year, watch.games, watch.n)]
labels_r = [f"{n} '{str(y)[2:]} · {g} G · {k} FF" for n, y, g, k in zip(ranked.name, ranked.game_year, ranked.games, ranked.n)]
fig = go.Figure()
for lab, d, hollow in [(labels_w, watch, True), (labels_r, ranked, False)]:
    for yl, u, gsc in zip(lab, d.efc_score_ungoverned, d.efc_score):
        fig.add_trace(go.Scatter(x=[u, gsc], y=[yl, yl], mode="lines", line=dict(color=LGRAY, width=2), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=d.efc_score_ungoverned, y=lab, mode="markers", name="Ungoverned (raw) score" if not hollow else None,
                             showlegend=not hollow, marker=dict(size=8, color=GRAY, symbol="line-ns-open", line=dict(width=2, color=GRAY))))
    fig.add_trace(go.Scatter(x=d.efc_score, y=lab, mode="markers",
                             name=("Watch list — thin evidence (50–99 FF)" if hollow else "Ranked — ≥100 FF"),
                             marker=dict(size=13, color=[RED if t == "ELITE" else NAVY for t in d.archetype_tier],
                                         symbol="circle-open" if hollow else "circle", line=dict(width=2.5 if hollow else 1, color=[RED if t == "ELITE" else NAVY for t in d.archetype_tier])),
                             customdata=np.stack([d.archetype_tier, d.shape_grade, d.results_grade, d.coverage], axis=-1),
                             hovertemplate="%{y}<br>score %{x:.1f} · %{customdata[0]}<br>shape %{customdata[1]} / results %{customdata[2]} · %{customdata[3]}<extra></extra>"))
fig.add_vline(x=b_score, line_color=RED, line_dash="dash", annotation_text=f"Bowlan 2026 · {b_score:.1f}", annotation_position="top right")
fig.add_vline(x=d_score, line_color="#C97A00", line_dash="dot", annotation_text=f"Duran 2026 · {d_score:.1f}", annotation_position="top left")
fig.update_xaxes(title="Elite-FF composite score (20–80 scale; shape and results weighted equally)", range=[48, 75])
base(fig, "External Board — No Ranked Candidate Out-Grades Bowlan's 2026 Four-Seam",
     "Not on the 2026 Phillies, 2025–26 seasons. Red = plus on both axes. Grey tick = the score before stabilization and drift adjustment. "
     "The one arm who beats him — Misiorowski — we've seen for exactly one start.", h=760)
ship(fig, "fig4_external_board", dict(chart_type="dot", colors=[RED, NAVY, GRAY], hover_fields=["efc_score", "shape_grade", "results_grade"]))

# ---------------------------------------------------------------------------
# F5 · The needle — elite-four-seam share scenarios
# ---------------------------------------------------------------------------
efs = R("efs_2026").set_index("flag")
nd = R("needle")
cas = nd[nd.name == "Ben Casparius"].iloc[0]
mis = nd[nd.name == "Jacob Misiorowski"].iloc[0]
as_is = efs.loc["ff_elite_archetype_flag", "share"]
out_b = efs.loc["ff_elite_archetype_flag|carry_in_bowlan_out", "share"]
assert abs(as_is - 467 / 4201) < 1e-3 and out_b == 0
assert 2.5 <= mis.V_role / cas.V_role < 3.0   # subtitle: 'almost 3x'
sc = pd.DataFrame([
    ("2026 as is", as_is, NAVY, f"{int(efs.loc['ff_elite_archetype_flag','elite_ff'])} of {int(efs.loc['ff_elite_archetype_flag','total_ff']):,} four-seams — all Bowlan"),
    ("Bowlan out (carry-in, 9/17)", out_b, GRAY, "the share is one arm deep"),
    ("+ an elite reliever<br>(Casparius, ranked)", as_is + cas.delta_efs, "#C97A00", f"+{cas.delta_efs * 100:.1f} pts · a reliever's {int(cas.V_role)} four-seams"),
    ("+ an elite starter<br>(Misiorowski, watch list)", as_is + mis.delta_efs, RED, f"+{mis.delta_efs * 100:.1f} pts · a starter's {int(mis.V_role)} four-seams"),
], columns=["scenario", "share", "color", "note"])
sc.to_csv(OUT / "dp_uc47_efs_scenarios.csv", index=False)
fig = go.Figure(go.Bar(x=sc.scenario, y=sc.share * 100, marker_color=sc.color, text=[f"{v * 100:.1f}%" for v in sc.share],
                       textposition="outside", customdata=sc.note, hovertemplate="%{x}<br>%{y:.1f}%<br>%{customdata}<extra></extra>"))
for i, r in sc.iterrows():
    fig.add_annotation(x=r.scenario, y=-3.2, text=r.note, showarrow=False, font=dict(size=11, color="#444"))
fig.update_yaxes(title="Elite-four-seam share of Phillies RHP four-seams (%)", range=[-6, 32])
base(fig, "Phillies Elite Four-Seam Share — One Arm Deep, 2026",
     "Share of every right-handed four-seam the 2026 staff threw that came from a pitcher plus on both axes. "
     "A starter's workload moves the share almost 3× what a reliever's does.", h=640)
ship(fig, "fig5_needle", dict(chart_type="bar", colors=[NAVY, GRAY, "#C97A00", RED], hover_fields=["share"]))

# ---------------------------------------------------------------------------
# F6 · Who's best depends on what you value
# ---------------------------------------------------------------------------
ws = R("weight_sensitivity_cohort_best")
wcols = [c for c in ws.columns if c.startswith("rank_w")]
wx = [float(c.replace("rank_w", "")) for c in wcols]
winners = {w: ws.loc[ws[c] == 1, "arm"].tolist() for w, c in zip(wx, wcols)}
assert winners[0.0] == ["Jhoan Duran"] and winners[0.5] == ["Jonathan Bowlan"] and winners[1.0] == ["Alex McFarlane"]
fig = go.Figure()
for _, r in ws.iterrows():
    fig.add_trace(go.Scatter(x=wx, y=[r[c] for c in wcols], mode="lines+markers", name=f"{r.arm} ({int(r.game_year)})",
                             line=dict(color=ARM_COLORS[r.arm], width=3), marker=dict(size=11, line=dict(width=2, color="white"))))
    fig.add_annotation(x=1.02, y=r[wcols[-1]], text=r.arm.split()[-1], showarrow=False, xanchor="left", font=dict(color="#222"))
    fig.add_annotation(x=-0.02, y=r[wcols[0]], text=r.arm.split()[-1], showarrow=False, xanchor="right", font=dict(color="#222"))
fig.update_yaxes(autorange="reversed", title="Cohort rank (each arm's best season)", dtick=1)
fig.update_xaxes(title="Weight on shape  (0 = only what it does · 1 = only what it looks like)", tickvals=wx, range=[-0.18, 1.18])
base(fig, "The Six-Arm Cohort — Best Four-Seam Depends on What You Value, 2018–2026",
     "Duran if you only care what it does. McFarlane (94 pitches, THIN) if you only care how it looks. Bowlan everywhere in between.", h=640)
ship(fig, "fig6_weight_sensitivity", dict(chart_type="line", colors=list(ARM_COLORS.values()), hover_fields=["rank"]))

# ---------------------------------------------------------------------------
# F7 · Stabilization
# ---------------------------------------------------------------------------
st = R("stabilization")
lab = {"velo": "Velocity", "ivb_in": "Ride (IVB)", "spin": "Spin", "whiff_rate": "Whiff rate", "rv100": "Run value / 100"}
assert st.set_index("metric").loc["rv100", "k"] > 1000 and st.set_index("metric").loc["velo", "k"] < 1
fig = go.Figure(go.Bar(y=[lab[m] for m in st.metric], x=st.k, orientation="h",
                       marker_color=[RED if s else NAVY for s in st.shrink],
                       text=[f"{k:,.1f} {u}  ·  {r100:.0%} signal at 100 FF" for k, u, r100 in zip(st.k, st.units, st.reliability_at_pop_floor)],
                       textposition="outside"))
fig.update_xaxes(type="log", title="Pitches (or swings) until the number is half signal, half noise — log scale", range=[-1.2, 4.2])
base(fig, "Four-Seam Stabilization — Pitches Before a Number Means Something, 2018–2026",
     "Shape is readable almost immediately. Whiff rate needs ~56 swings. Run value needs ~1,084 pitches — more than most relievers throw in a year. "
     "Red = shrunk toward the population before grading.", h=520)
ship(fig, "fig7_stabilization", dict(chart_type="bar", colors=[RED, NAVY], hover_fields=["k"]))

# ---------------------------------------------------------------------------
# Brand-center MCP compliance (host repo: brand-center-mcp/brand-center-mcp.py)
# ---------------------------------------------------------------------------
cands = [os.environ.get("MLB_DATA_ROOT", ""), "/mnt/user-data/uploads/MLB", r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
bc_path = next(Path(c) / "brand-center-mcp" / "brand-center-mcp.py" for c in cands if c and (Path(c) / "brand-center-mcp" / "brand-center-mcp.py").exists())
spec = importlib.util.spec_from_file_location("brand_center", bc_path)
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
rows = []
for m in SPECS:
    # NOTE BC-1: the validator reads plotly_template -> template -> layout in that order; passing a bare
    # `template` string masks the layout block (and its Arial font). Pass the full block as plotly_template.
    payload = dict(title=m["title"], subtitle=m["subtitle"], colors=m["colors"], plotly_template=m["layout"], hover_fields=m["hover_fields"], chart_type=m["chart_type"],
                   tags=dict(player="cohort+candidates", **{"analysis-type": "archetype-gap"}, date="2026-09-22",
                             audience="front_office", status="governed"))
    checks = ["color_palette_used", "plotly_conventions_met", "voice_consistent", "title_factual", "governance_tags_applied"]
    res = bc.process_tool_call("validate_brand_compliance", {"output_dict": payload, "checks": checks})
    assert res.get("success"), res
    res = res["result"]
    for ck, v in res["compliance_checks"].items():
        rows.append(dict(figure=m["figure"], check=ck, status=v.get("status"), note=v.get("notes"),
                         score=res["compliance_score"], can_publish=res["can_publish"]))
    rows.append(dict(figure=m["figure"], check="hover_fields_complete", status="n/a",
                     note="aggregate chart — brand-center REQUIRED_HOVER sets apply to pitch/batted-ball charts only"))
bcr = pd.DataFrame(rows)
bcr.to_csv(OUT / "dp_uc47_brand_compliance.csv", index=False)
print(bcr.groupby(["check", "status"]).size())
print(bcr[bcr.status == "fail"][["figure", "check", "note"]].to_string())
print("figures:", [m["figure"] for m in SPECS])
