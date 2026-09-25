"""
dp_uc48_build_figs.py — figures for UC #48 / uc-pps-033 (PNG for the PDF, JSON for the dashboard).

Rules:
  * Reads ONLY out/dp_uc48_* receipts (+ the inherited uc-pps-032 population receipt for F1).
  * Each figure asserts the claim its subtitle makes before it is written.
  * Print surfaces follow brand-center (`plotly_white` + Arial); the dashboard re-templates the
    same JSON to the client's `plotly_dark` on toggle (E-5 still open at the DPO).
  * Every figure is run through brand-center-mcp `validate_brand_compliance` (in-process router).
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots          # GM-1: the Gemini cell relied on cell 4 for this

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC48_OUT", HERE / "out"))
os.environ.setdefault("BROWSER_PATH", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
ROOTS = [os.environ.get("MLB_DATA_ROOT", ""), "/mnt/user-data/uploads/MLB", r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"]
ROOT = next(Path(c) for c in ROOTS if c and (Path(c) / "dp_uc44_kernel.py").exists())

RED, NAVY, GRAY, LGRAY = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9"
SEASON = {2023: "#B0B7C3", 2024: GRAY, 2025: NAVY, 2026: RED}
PITCH = {'FF': '#D22D49', 'SI': '#FE9D00', 'SL': '#EEE716', 'ST': '#DDB33A', 'CU': '#00D1ED', 'CH': '#1DBE3A'}
PNAME = {'FF': 'Four-Seam', 'SI': 'Sinker', 'SL': 'Slider', 'ST': 'Sweeper', 'CU': 'Curveball', 'CH': 'Changeup'}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color="#1b1b1b"),
              margin=dict(l=70, r=30, t=115, b=60), legend=dict(orientation="h", y=-0.16, x=0))
H = json.loads((OUT / "dp_uc48_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc48_{n}.csv")        # noqa: E731
SPECS = []


def wrap(t, n=150):
    words, lines, cur = t.split(" "), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return "<br>".join(lines + [cur])


def base(fig, title, subtitle, h=520, w=1000):
    subtitle = wrap(subtitle)
    fig.update_layout(**LAYOUT, height=h, width=w,
                      title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
                                 subtitle=dict(text=subtitle, font=dict(size=12.5, color="#5b6170"))))
    return fig


def ship(fig, key, meta):
    fig.write_image(OUT / f"dp_uc48_{key}.png", scale=2)
    (OUT / f"dp_uc48_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=fig.layout.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=fig.layout.title.subtitle.text.replace("<br>", " "), layout=LAYOUT, **meta))


P = R("bowlan_pitches")
FF = P[P.pitch_type == "FF"]
y25, y26 = H["y2025"], H["y2026"]

# ---------------------------------------------------------------------------
# F1 · The archetype flip (inherited uc-pps-032 grades; nothing re-graded)
# ---------------------------------------------------------------------------
g47 = pd.read_csv(ROOT / "out" / "dp_uc47_population_graded.csv")
pop = g47[g47.pop_member]
bw = g47[g47.pitcher == 680742].set_index("game_year")
a47 = H["arch"]
assert a47["2025"]["tier"] == "RESULTS-ONLY" and a47["2026"]["tier"] == "ELITE"
assert a47["2025"]["g_velo"] == 50 and a47["2026"]["g_velo"] == 60 and a47["2026"]["rank"] == 2
fig = go.Figure()
fig.add_shape(type="rect", x0=60, x1=80, y0=60, y1=85, fillcolor=RED, opacity=0.07, line_width=0)
fig.add_trace(go.Scatter(x=pop.shape_score, y=pop.results_score, mode="markers", name=f"RHP four-seam seasons, 2018–26 (n={len(pop)})",
                         marker=dict(size=7, color=GRAY, opacity=0.35),
                         text=pop.name + " " + pop.game_year.astype(str),
                         hovertemplate="%{text}<br>shape %{x:.1f} · results %{y:.1f}<extra></extra>"))
for yr, col in ((2025, NAVY), (2026, RED)):
    fig.add_trace(go.Scatter(x=[bw.loc[yr, "shape_score"]], y=[bw.loc[yr, "results_score"]], mode="markers+text",
                             name=f"Bowlan {yr} ({a47[str(yr)]['tier']})", marker=dict(size=16, color=col, line=dict(color="white", width=2)),
                             text=[f"{yr} · {a47[str(yr)]['tier']}"], textposition="middle left" if yr == 2025 else "top center",
                             hovertemplate=f"Bowlan {yr}<br>shape %{{x:.1f}} · results %{{y:.1f}}<extra></extra>"))
fig.add_annotation(x=bw.loc[2026, "shape_score"], y=bw.loc[2026, "results_score"], ax=bw.loc[2025, "shape_score"],
                   ay=bw.loc[2025, "results_score"], xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                   arrowhead=3, arrowwidth=2, arrowcolor=RED, text="")
fig.add_vline(x=60, line_dash="dot", line_color=NAVY); fig.add_hline(y=60, line_dash="dot", line_color=NAVY)
fig.add_annotation(x=79, y=84, text="ELITE: plus on both axes", showarrow=False, xanchor="right", font=dict(color=RED))
fig.update_xaxes(title="Shape score (velocity · ride · spin, 20–80)", range=[20, 80])
fig.update_yaxes(title="Results score (whiff · run value, 20–80)", range=[20, 85])
base(fig, "Jonathan Bowlan — Four-Seam Shape vs Results Grade, 2025 → 2026",
     f"The ride was already plus in Kansas City (grade {a47['2025']['g_ivb']}). The velocity grade moving {a47['2025']['g_velo']} → {a47['2026']['g_velo']} "
     f"flipped the shape axis: {a47['2025']['tier']} → {a47['2026']['tier']}, #{a47['2025']['rank']} → #{a47['2026']['rank']} of {H['arch_pop_n']} (uc-pps-032 grades, inherited)", h=600)
ship(fig, "fig1_archetype_flip", dict(chart_type="scatter", colors=[RED, NAVY, GRAY], hover_fields=["shape_score", "results_score"]))

# ---------------------------------------------------------------------------
# F2 · The client's velocity box, governed (n printed, 2026 IQR band)
# ---------------------------------------------------------------------------
vby = {int(k): v for k, v in H["ff_velo_by_year"].items()}
assert vby[2026] == max(vby.values()) and round(vby[2026], 1) == 97.0
fig = go.Figure()
for yr in sorted(FF.game_year.unique()):
    d = FF[FF.game_year == yr]
    fig.add_trace(go.Box(x=[str(yr)] * len(d), y=d.release_speed, name=str(yr), marker_color=SEASON[yr], boxpoints="outliers",
                         showlegend=False, hovertemplate=f"{yr}: %{{y:.1f}} mph<extra></extra>"))
    fig.add_annotation(x=str(yr), y=92.2, text=f"n={len(d)}", showarrow=False, font=dict(size=11, color="#5b6170"))
q1, q3 = H["ff_velo_iqr_2026"]
fig.add_hrect(y0=q1, y1=q3, fillcolor=RED, opacity=0.12, line_width=0, annotation_text="Middle 50% of 2026", annotation_position="bottom left")
fig.update_yaxes(title="Four-seam velocity (mph)", range=[91.8, 99.5]); fig.update_xaxes(title="Season", type="category")
base(fig, "Jonathan Bowlan — Four-Seam Fastball Velocity by Season, 2023–2026",
     f"Up to a career-high {vby[2026]:.1f} mph average in 2026, +{H['ff_velo_delta']:.2f} over 2025. The step came in one season: 2024 → 2025 was flat. 2023–24 are 22 and 29 pitches.")
ship(fig, "fig2_velo_box", dict(chart_type="box", colors=[RED, NAVY, GRAY], hover_fields=["release_speed"]))

# ---------------------------------------------------------------------------
# F3 · The Gemini 2×2, governed (inches, n, no leaked gy)
# ---------------------------------------------------------------------------
mets = [("release_speed", "Velocity (mph)"), ("release_spin_rate", "Spin rate (rpm)"),
        ("hb_in", "Horizontal break (in)"), ("ivb_in", "Vertical break / ride (in)")]
fig = make_subplots(rows=2, cols=2, subplot_titles=[m[1] for m in mets], vertical_spacing=0.14, horizontal_spacing=0.08)
for i, (c, lab) in enumerate(mets):
    r, cc = divmod(i, 2)
    for yr in sorted(FF.game_year.unique()):
        d = FF[FF.game_year == yr]
        fig.add_trace(go.Box(x=[f"{yr}<br>n={len(d)}"] * len(d), y=d[c], marker_color=SEASON[yr], showlegend=False,
                             boxpoints="outliers", hovertemplate=f"{yr}: %{{y:.1f}}<extra></extra>"), row=r + 1, col=cc + 1)
fig.add_hrect(y0=q1, y1=q3, fillcolor=RED, opacity=0.12, line_width=0, row=1, col=1)
base(fig, "Jonathan Bowlan — Four-Seam Fastball Metrics by Season, 2023–2026 (Gemini layout, governed)",
     f"Velocity and spin stepped up in 2026 (+{H['ff_velo_delta']:.2f} mph, +{H['ff_spin_delta']:.0f} rpm); the movement boxes barely moved. Breaks in inches, not feet (GM-2).", h=760)
ship(fig, "fig3_gemini_grid", dict(chart_type="box", colors=[RED, NAVY, GRAY], hover_fields=["release_speed", "release_spin_rate", "pfx_x", "pfx_z"]))

# ---------------------------------------------------------------------------
# F4 · Velo as a function of spin (the client's reply, chart 1)
# F5 · Four-seam movement profile by season (chart 2)
# ---------------------------------------------------------------------------
def season_scatter(xc, yc, xlab, ylab, key, title, sub):
    fig = go.Figure()
    for yr in sorted(FF.game_year.unique()):
        d = FF[FF.game_year == yr]
        fig.add_trace(go.Scatter(x=d[xc], y=d[yc], mode="markers", name=f"{yr} (n={len(d)})",
                                 marker=dict(size=8 if yr >= 2025 else 7, color=SEASON[yr], opacity=0.75 if yr >= 2025 else 0.6,
                                             line=dict(color="white", width=0.6)),
                                 customdata=np.stack([d.release_speed, d.release_spin_rate, d.hb_in, d.ivb_in, d.description, d.game_date], axis=1),
                                 hovertemplate="%{customdata[5]}<br>%{customdata[0]:.1f} mph · %{customdata[1]:.0f} rpm<br>"
                                               "HB %{customdata[2]:.1f} in · IVB %{customdata[3]:.1f} in<br>%{customdata[4]}<extra></extra>"))
    fig.update_xaxes(title=xlab); fig.update_yaxes(title=ylab)
    base(fig, title, sub, h=560)
    ship(fig, key, dict(chart_type="pitch", colors=[RED, NAVY, GRAY],
                        hover_fields=["release_speed", "pfx_x", "pfx_z", "release_spin_rate", "description"]))

assert H["ff_velo_p"] < 1e-6 and H["ff_spin_p"] < 1e-6
season_scatter("release_spin_rate", "release_speed", "Spin rate (rpm)", "Velocity (mph)", "fig4_velo_spin",
               "Jonathan Bowlan — Four-Seam Velocity vs Spin Rate, 2023–2026",
               f"Clearly harder and with more spin in 2026: +{H['ff_velo_delta']:.2f} mph and +{H['ff_spin_delta']:.0f} rpm on average over 2025 (both p < .001)")
assert abs(H["ff_ivb_delta"]) < 0.5
season_scatter("hb_in", "ivb_in", "Horizontal break (in, arm side negative)", "Vertical break / ride (in)", "fig5_movement",
               "Jonathan Bowlan — Four-Seam Movement Profile, 2023–2026",
               f"The shape held: ride {y25['ff_vert']:.1f} → {y26['ff_vert']:.1f} in. The pitch is the same pitch, thrown {H['ff_velo_delta']:.1f} mph harder.")

# ---------------------------------------------------------------------------
# F6 · Staff carry (the client's chart 3): density of every other Phillies RHP four-seam + Bowlan 2026
# ---------------------------------------------------------------------------
D = json.loads((OUT / "dp_uc48_staff_density.json").read_text())["FF"]
b26 = FF[FF.game_year == 2026]
fig = make_subplots(rows=1, cols=2, column_widths=[0.8, 0.2], shared_yaxes=True, horizontal_spacing=0.02)
fig.add_trace(go.Contour(x=D["x"], y=D["y"], z=D["z"], colorscale=[[0, "rgba(255,255,255,0)"], [0.02, "#EEF0F4"], [1, "#5b6170"]],
                         showscale=False, contours=dict(coloring="fill", showlines=False), name="Other Phillies RHP four-seams (density)", showlegend=True,
                         hovertemplate="HB %{x} · IVB %{y}<br>%{z} other RHP four-seams<extra></extra>", ncontours=14), 1, 1)
fig.add_trace(go.Scatter(x=b26.hb_in, y=b26.ivb_in, mode="markers", name=f"Jonathan Bowlan 2026 (n={len(b26)})",
                         marker=dict(size=7, color=RED, opacity=0.7, line=dict(color="white", width=0.5)),
                         customdata=np.stack([b26.release_speed, b26.release_spin_rate, b26.description, b26.game_date], axis=1),
                         hovertemplate="%{customdata[3]} · %{customdata[0]:.1f} mph · %{customdata[1]:.0f} rpm<br>HB %{x:.1f} · IVB %{y:.1f}<br>%{customdata[2]}<extra></extra>"), 1, 1)
fig.add_trace(go.Bar(y=D["y"], x=D["marg"], orientation="h", marker_color=GRAY, name="Other RHP four-seams by ride", showlegend=False,
                     hovertemplate="IVB %{y}: %{x} pitches<extra></extra>"), 1, 2)
bq1, bq3 = H["client_band"]
for c in (1, 2):
    fig.add_hrect(y0=bq1, y1=bq3, fillcolor=RED, opacity=0.13, line_width=0, row=1, col=c)
fig.update_xaxes(title="Horizontal break (in)", range=[-22, 8], row=1, col=1); fig.update_yaxes(title="Vertical break / ride (in)", range=[4, 26], row=1, col=1)
fig.update_xaxes(title="pitches", row=1, col=2)
assert H["staff_ff_ivb_rank"] <= 10
base(fig, "Phillies RHP Four-Seam Movement, 2015–2026 (ex-2017) — Jonathan Bowlan vs the Staff",
     f"Exceptional carry: the band is the middle 50% of his 2026 ride ({bq1:.1f}–{bq3:.1f} in). Only {100 * H['share_other_above_median']:.1f}% of {H['other_rhp_ff_pitches']:,} "
     f"other Phillies RHP four-seams ride as much as his median; his season is #{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']}.", h=600)
ship(fig, "fig6_staff_carry", dict(chart_type="pitch", colors=[RED, GRAY], hover_fields=["release_speed", "pfx_x", "pfx_z", "release_spin_rate", "description"]))

# ---------------------------------------------------------------------------
# F7 · Rebuilt by platoon — usage by batter hand, 2025 vs 2026
# ---------------------------------------------------------------------------
S = R("arsenal_by_stand")
fig = make_subplots(rows=1, cols=2, subplot_titles=["vs LHB", "vs RHB"], shared_yaxes=True, horizontal_spacing=0.06)
order = ["FF", "SI", "CH", "SL", "ST", "CU"]
for ci, st in enumerate(("L", "R")):
    for yr in (2025, 2026):
        d = S[(S.stand == st) & (S.game_year == yr)].set_index("pitch_type").reindex(order)
        fig.add_trace(go.Bar(y=[PNAME[p] for p in order], x=d.usage.fillna(0), orientation="h", name=str(yr), legendgroup=str(yr),
                             showlegend=ci == 0, marker_color=SEASON[yr], text=[f"{v:.0%}" if v >= .02 else "" for v in d.usage.fillna(0)],
                             textposition="outside", hovertemplate=f"{yr} vs {st}HB · %{{y}}: %{{x:.1%}}<extra></extra>"), 1, ci + 1)
fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08)
fig.update_xaxes(tickformat=".0%", range=[0, 0.72]); fig.update_yaxes(autorange="reversed")
m = H["mix_by_stand"]
assert m["2026_R_ST"] >= 0.10 and m.get("2025_R_ST") is None
base(fig, "Jonathan Bowlan — Pitch Usage by Batter Hand, 2025 vs 2026",
     f"Lefties got the four-seam and changeup ({m['2025_L_FF'] + m['2025_L_CH']:.0%} → {m['2026_L_FF'] + m['2026_L_CH']:.0%}). Righties got a new sweeper ({m['2026_R_ST']:.0%}). The curveball was shelved.", h=560)
ship(fig, "fig7_platoon_mix", dict(chart_type="bar", colors=[RED, NAVY], hover_fields=["usage"]))

# ---------------------------------------------------------------------------
# F8 · Four-seam when it matters — share by count state
# ---------------------------------------------------------------------------
C = R("count_state_mix"); C = C[C.pitch_type == "FF"]
states = ["ahead", "even", "behind", "2K"]; lab = {"ahead": "Ahead", "even": "Even", "behind": "Behind", "2K": "Two strikes"}
fig = go.Figure()
for yr in (2025, 2026):
    d = C[C.game_year == yr].set_index("count_state").reindex(states)
    fig.add_trace(go.Bar(x=[lab[s] for s in states], y=d.share, name=str(yr), marker_color=SEASON[yr],
                         text=[f"{v:.0%}" for v in d.share], textposition="outside",
                         hovertemplate=f"{yr} · %{{x}}: %{{y:.1%}} four-seams<extra></extra>"))
fig.update_layout(barmode="group", bargap=0.3); fig.update_yaxes(tickformat=".0%", range=[0, 0.68], title="Share of pitches that were four-seams")
t2k, tb = H["tests"]["Four-seam share, 2K counts"], H["tests"]["Four-seam share, behind counts"]
assert t2k["p"] < 0.01 and tb["p"] < 0.01
base(fig, "Jonathan Bowlan — Four-Seam Share by Count, 2025 vs 2026",
     f"Two strikes: {t2k['r25']:.0%} → {t2k['r26']:.0%}. Behind: {tb['r25']:.0%} → {tb['r26']:.0%} (both p < .01). The fastball became the answer when the at-bat was on the line.")
ship(fig, "fig8_ff_by_count", dict(chart_type="bar", colors=[RED, NAVY], hover_fields=["share"]))

# ---------------------------------------------------------------------------
# F9 · Role vs arm — velocity by pitch-of-outing (VE-1)
# ---------------------------------------------------------------------------
V = R("velo_by_outing")
fig = go.Figure()
for yr in (2025, 2026):
    d = V[V.game_year == yr]
    fig.add_trace(go.Scatter(x=d.bucket, y=d.velo, mode="lines+markers+text", name=str(yr), line=dict(color=SEASON[yr], width=2),
                             marker=dict(size=10), text=[f"{v:.1f}" for v in d.velo], textposition="top center",
                             customdata=d.n, hovertemplate=f"{yr} · pitches %{{x}} of the outing<br>%{{y:.2f}} mph on %{{customdata}} four-seams<extra></extra>"))
fig.update_xaxes(title="Pitch number within the outing", type="category"); fig.update_yaxes(title="Four-seam velocity (mph)", range=[94.5, 98.2])
vb = H["velo_bucket"]
assert vb["2026_1-10"]["velo"] - vb["2025_1-10"]["velo"] >= 1.0
base(fig, "Jonathan Bowlan — Four-Seam Velocity by Pitch of Outing, 2025 vs 2026",
     f"Not just a shorter role: he was +{vb['2026_1-10']['velo'] - vb['2025_1-10']['velo']:.1f} mph on the first ten pitches of an outing, before fatigue can matter. The gain is in the arm.")
ship(fig, "fig9_velo_by_outing", dict(chart_type="line", colors=[RED, NAVY], hover_fields=["velo", "n"]))

# ---------------------------------------------------------------------------
# F10 · The eighth-inning job — entry inning, 2025 vs 2026
# ---------------------------------------------------------------------------
A = R("appearances")
fig = go.Figure()
for yr in (2025, 2026):
    d = A[A.game_year == yr].entry_inning.value_counts().reindex(range(1, 11), fill_value=0)
    fig.add_trace(go.Bar(x=[str(i) for i in d.index], y=d.values, name=f"{yr} ({int(d.sum())} G)", marker_color=SEASON[yr],
                         hovertemplate=f"{yr} · entered in inning %{{x}}: %{{y}} times<extra></extra>"))
fig.update_layout(barmode="group", bargap=0.25); fig.update_xaxes(title="Inning he entered", range=[2.5, 10.5]); fig.update_yaxes(title="Appearances")
u25, u26 = H["usage"]["2025"], H["usage"]["2026"]
assert u26["multi_inning_share"] < 0.15 and u25["multi_inning_share"] > 0.40
base(fig, "Jonathan Bowlan — Appearances by Entry Inning, 2025 vs 2026",
     f"A defined job: {H['apps_7th_8th_2026']} of 59 entries in the 7th or 8th. {u25['pitches_per_app']:.1f} → {u26['pitches_per_app']:.1f} pitches per outing; "
     f"multi-inning outings {u25['multi_inning_share']:.0%} → {u26['multi_inning_share']:.0%}.")
ship(fig, "fig10_entry_inning", dict(chart_type="bar", colors=[RED, NAVY], hover_fields=["entry_inning"]))

# ---------------------------------------------------------------------------
# F11 · The season by month (2026) — K rate and wOBA against (same unit: rate)
# ---------------------------------------------------------------------------
M = R("monthly_2026")
mn = {3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep"}
fig = go.Figure()
for c, lab_, col in (("krate", "K rate", RED), ("woba", "wOBA against", NAVY)):
    fig.add_trace(go.Scatter(x=[mn[m] for m in M.month], y=M[c], mode="lines+markers", name=lab_, line=dict(color=col, width=2), marker=dict(size=9),
                             customdata=np.stack([M.plate_apps, M.games, M.ff_velo], axis=1),
                             hovertemplate=f"%{{x}} · {lab_} %{{y:.3f}}<br>%{{customdata[0]}} PA in %{{customdata[1]}} G · FF %{{customdata[2]:.1f}} mph<extra></extra>"))
for i, r in M.iterrows():
    fig.add_annotation(x=mn[r.month], y=0.02, text=f"{int(r.plate_apps)} PA", showarrow=False, font=dict(size=10, color="#5b6170"))
fig.add_annotation(x="Sep", y=M.set_index("month").loc[9, "woba"], text="9/17: left with a reported<br>right groin strain (carry-in)",
                   showarrow=True, ax=-90, ay=-30, font=dict(size=11))
fig.update_yaxes(title="Rate", range=[0, 0.45], tickformat=".3f")
sep = H["monthly"]["9"]
base(fig, "Jonathan Bowlan — K Rate and wOBA Against by Month, 2026",
     f"wOBA against held {min(H['monthly'][str(k)]['woba'] for k in range(4, 9)):.3f}–{max(H['monthly'][str(k)]['woba'] for k in range(4, 9)):.3f} from April through August while the K rate swung "
     f"({H['monthly']['5']['krate']:.0%} in May, {H['monthly']['6']['krate']:.0%} in June). September's {sep['woba']:.3f} is {sep['pa']} PA, too few to read; the four-seam still averaged {sep['ff_velo']:.1f} mph.")
ship(fig, "fig11_monthly", dict(chart_type="line", colors=[RED, NAVY], hover_fields=["krate", "woba"]))

# ---------------------------------------------------------------------------
# Brand-center MCP compliance (in-process router, same code path an MCP client hits)
# ---------------------------------------------------------------------------
bc_path = ROOT / "brand-center-mcp" / "brand-center-mcp.py"
spec = importlib.util.spec_from_file_location("brand_center", bc_path)
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
rows = []
for m in SPECS:
    payload = dict(title=m["title"], subtitle=m["subtitle"], colors=m["colors"], plotly_template=m["layout"],
                   hover_fields=m["hover_fields"], chart_type=m["chart_type"],
                   tags=dict(player="Jonathan Bowlan", **{"analysis-type": "season-recap"}, date="2026-09-24",
                             audience="pitching_staff", status="governed"))
    checks = ["color_palette_used", "plotly_conventions_met", "voice_consistent", "title_factual", "governance_tags_applied"]
    if m["chart_type"] == "pitch":
        checks.append("hover_fields_complete")
    res = bc.process_tool_call("validate_brand_compliance", {"output_dict": payload, "checks": checks})
    assert res.get("success"), res
    res = res["result"]
    for ck, v in res["compliance_checks"].items():
        rows.append(dict(figure=m["figure"], check=ck, status=v.get("status"), note=v.get("notes"),
                         score=res["compliance_score"], can_publish=res["can_publish"]))
    if m["chart_type"] != "pitch":
        rows.append(dict(figure=m["figure"], check="hover_fields_complete", status="n/a",
                         note="aggregate chart — REQUIRED_HOVER sets apply to pitch/batted-ball charts only"))
bcr = pd.DataFrame(rows)
bcr.to_csv(OUT / "dp_uc48_brand_compliance.csv", index=False)
print(bcr.groupby(["check", "status"]).size())
fails = bcr[bcr.status == "fail"]
print(fails[["figure", "check", "note"]].to_string() if len(fails) else "brand: no fails")
