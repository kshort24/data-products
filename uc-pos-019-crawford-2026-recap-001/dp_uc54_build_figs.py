"""dp_uc54_build_figs.py - ten figures for UC #54 / uc-pos-019 (PNG for the PDF, JSON for the dashboard).
House rules (dp_uc48-53_build_figs): reads ONLY out/dp_uc54_* receipts; computes no KPI; each figure asserts the claim its
subtitle makes before it is written; print = plotly_white + Arial; brand-palette check -> out/dp_uc54_brand_checks.csv.
Pitch-group palette PG-1 validated light + dark (out/dp_uc54_palette_validation.txt). Cumulative panels are CM-1b
(multi-panel ghost lines over CM-1 frames). Plate locations are catcher's view."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
RED, NAVY, GRAY, LGRAY, INK, MUTED, GHOST = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170", "#C3C9D2"
PG = {"fastball": "#C77800", "breaking": "#6250D6", "offspeed": "#1A9E77"}          # PG-1 (validated)
VERD = {"PRESENT": RED, "WEAK": GRAY, "ABSENT": LGRAY, "CONTRA": NAVY, "NO DATA": LGRAY}
ALLOWED = {RED, NAVY, GRAY, LGRAY, INK, MUTED, GHOST, "#ffffff", *PG.values(), "#F4B6BB", "#9DB0D3", "#EEF1F5",
           "rgba(232,24,40,0.07)", "rgba(0,45,114,0.06)", "rgba(140,140,140,0.25)", "rgba(140,140,140,0.12)",
           "rgba(232,24,40,0.55)", "rgba(0,45,114,0.45)", "rgba(196,201,210,0.55)", "rgba(0,0,0,0)", "#C9A66B", "#E9DCC0", "#7FA36B"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=72, r=30, t=118, b=66), legend=dict(orientation="h", y=-0.16, x=0, yanchor="top"))
H = json.loads((OUT / "dp_uc54_headlines.json").read_text(encoding="utf-8"))
R = lambda n: pd.read_csv(OUT / f"dp_uc54_{n}.csv")              # noqa: E731
SPECS, BRAND = [], []
pct = lambda x, d=0: f"{100 * x:.{d}f}%"                           # noqa: E731
f3 = lambda x: f"{x:.3f}".replace("0.", ".", 1) if abs(x) < 1 else f"{x:.3f}"   # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
HL = "Crawford 2026"
SZ_TOP, SZ_BOT, HX, BALL = H["sz_mean"]["top"], H["sz_mean"]["bot"], 0.83, 0.25


def wrap(t, n=150):
    out, cur = [], ""
    for w in t.split(" "):
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return "<br>".join(out + [cur])


def base(fig, title, subtitle, h=560, w=1100):
    nl = wrap(subtitle).count("<br>") + 1
    lay = dict(LAYOUT); lay["margin"] = dict(LAYOUT["margin"], t=96 + 19 * nl + 34)     # subtitle never meets panel titles
    fig.update_layout(**lay, height=h + 19 * max(nl - 2, 0), width=w, title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
                      subtitle=dict(text=wrap(subtitle), font=dict(size=12.5, color=MUTED))))
    fig.update_xaxes(gridcolor="#eeeeee", zeroline=False); fig.update_yaxes(gridcolor="#eeeeee", zeroline=False)
    return fig


def colors_in(fig):
    js, found = fig.to_plotly_json(), set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("color", "fillcolor", "bgcolor", "line_color") and isinstance(v, str): found.add(v)
                elif k == "color" and isinstance(v, (list, tuple)): found.update(x for x in v if isinstance(x, str))
                else: walk(v)
        elif isinstance(o, (list, tuple)):
            for x in o: walk(x)
    walk(js["data"]); walk(js["layout"].get("shapes", [])); walk(js["layout"].get("annotations", []))
    return found


def ship(fig, key, claim_ok: bool, meta: dict):
    lay = fig.layout
    off = sorted(c for c in colors_in(fig) if c not in ALLOWED)
    checks = dict(claim_asserted=bool(claim_ok), font_arial=lay.font.family == "Arial", has_title=bool(lay.title.text),
                  has_subtitle=bool(lay.title.subtitle.text), palette_ok=not off)
    BRAND.append(dict(figure=key, **checks, off_palette=";".join(off)))
    assert all(checks.values()), (key, checks, off)
    fig.write_image(OUT / f"dp_uc54_{key}.png", scale=2)
    (OUT / f"dp_uc54_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


def zone(fig, row=None, col=None, heart=False):
    kw = dict(row=row, col=col) if row else {}
    fig.add_shape(type="rect", x0=-HX, x1=HX, y0=SZ_BOT, y1=SZ_TOP, line=dict(color=INK, width=1.6), **kw)
    if heart:
        fig.add_shape(type="rect", x0=-HX + BALL, x1=HX - BALL, y0=SZ_BOT + BALL, y1=SZ_TOP - BALL,
                      line=dict(color=GRAY, width=1, dash="dot"), fillcolor="rgba(140,140,140,0.12)", **kw)


def ghost_panels(metrics, labels, fmts, title, subtitle, key, claim_ok, rank_note, h=560):
    """CM-1b: one panel per metric; CX-1 seasons as ghost lines, Crawford 2026 in red; best/worst comps direct-labelled."""
    fig = make_subplots(rows=1, cols=len(metrics), horizontal_spacing=0.07, subplot_titles=[f"<b>{l}</b>" for l in labels])
    for i, (m, fmt) in enumerate(zip(metrics, fmts), start=1):
        cf = R(f"cum_{m}").dropna(subset=["value"])
        ends = cf.groupby("series").last()
        me_end, yr_ = ends.loc[HL, "value"], cf.value.max() - cf.value.min()
        others = ends.drop(HL)
        hi_s, lo_s = others.value.idxmax(), others.value.idxmin()
        for sname, g in cf.groupby("series"):
            if sname == HL:
                continue
            lab = sname in (hi_s, lo_s)
            fig.add_trace(go.Scatter(x=g.cum_pa, y=g.value, mode="lines", line=dict(color=GRAY if lab else GHOST, width=1.6 if lab else 1.2),
                                     name="Phillies CF seasons 2015-25 (CX-1)", legendgroup="ghost", showlegend=(i == 1 and sname == others.index[0]),
                                     hovertemplate=f"{sname}<br>PA %{{x}}<br>{labels[i-1]} %{{y:{fmt}}}<extra></extra>"), row=1, col=i)
            if lab:
                dy = g.value.iloc[-1] - me_end
                ys = (16 if dy >= 0 else -16) if abs(dy) < 0.05 * yr_ else 0                   # dodge Crawford's end label
                fig.add_annotation(x=g.cum_pa.iloc[-1], y=g.value.iloc[-1], text=f"{sname} {format(g.value.iloc[-1], fmt).lstrip('0')}",
                                   showarrow=False, xanchor="left", xshift=4, yshift=ys, font=dict(size=10.5, color=MUTED), row=1, col=i)
        me = cf[cf.series == HL]
        j1 = me[pd.to_datetime(me.game_date) >= "2026-06-01"].cum_pa.min()
        fig.add_vline(x=j1, line=dict(color=NAVY, width=1, dash="dot"), row=1, col=i)
        fig.add_trace(go.Scatter(x=me.cum_pa, y=me.value, mode="lines", line=dict(color=RED, width=3.4), name="Crawford 2026",
                                 legendgroup="hi", showlegend=(i == 1),
                                 hovertemplate=f"Crawford 2026<br>PA %{{x}}<br>{labels[i-1]} %{{y:{fmt}}}<extra></extra>"), row=1, col=i)
        fig.add_annotation(x=me.cum_pa.iloc[-1], y=me.value.iloc[-1], text=f"<b>{format(me.value.iloc[-1], fmt).lstrip('0')}</b>", showarrow=False,
                           xanchor="left", xshift=6, font=dict(color=RED, size=14), row=1, col=i)
        fig.update_yaxes(tickformat=fmt if fmt.endswith("%") else ".3f", row=1, col=i)
        fig.update_xaxes(title_text="Plate appearance", range=[0, 760], row=1, col=i)
    fig.add_annotation(x=0, y=-0.36, xref="paper", yref="paper", showarrow=False, xanchor="left", font=dict(size=11, color=MUTED),
                       text=f"Dotted navy line: his first PA on or after June 1. {rank_note}")
    base(fig, title, subtitle, h=h, w=1180)
    fig.update_layout(margin=dict(l=60, r=110, b=130))
    ship(fig, key, claim_ok, dict(source=[f"cum_{m}" for m in metrics] + ["cf_matched_volume"]))


cx = H["cx"]
# F1 ----------------------------------------------------------------------------------------------------------
mvol = R("cf_matched_volume")
cxc = R("cf_context_card").set_index("series")
CXPA = int(cxc.loc[HL, "plate_apps"])
ok = int(mvol[mvol.series == HL].rank_woba.iloc[0]) == cx["rank"]["woba"] and abs(R("cum_woba").dropna().query("series == @HL").value.iloc[-1] - cxc.loc[HL, "woba"]) < 1e-9
ghost_panels(["ba", "ops", "woba"], ["Batting average", "OPS", "wOBA"], [".3f", ".3f", ".3f"],
             f"A rookie line that climbed out of a June hole: {f3(H['ba'])} / {f3(H['ops'])} OPS / {f3(H['woba'])} wOBA",
             f"Cumulative by plate appearance, regular season, against the {cx['n'] - 1} other Phillies primary centre-field seasons of the Statcast era "
             f"(CX-1: >80 games in CF, CF games only, so his line runs {CXPA} of {int(H['plate_apps'])} PA). Bottom on June 13 (PA {H['cum_woba_min']['pa']}): BA {f3(H['cum_ba_min']['value'])}, "
             f"wOBA {f3(H['cum_woba_min']['value'])}. At {cx['matched_pa']} PA he ranks {ordn(cx['rank']['ba'])} of {cx['n']} in BA and "
             f"{ordn(cx['rank']['woba'])} in wOBA.", "f1_cumulative_slash", ok,
             f"Panel endpoints are his CF-games line ({CXPA} PA) and reconcile to K40 on that frame (CM-1, tol 1e-9); the title is the full season. Lines start at 25 PA.")

# F2 ----------------------------------------------------------------------------------------------------------
rf, bs = R("rolling_100pa"), R("breakpoint_scan")
fig = make_subplots(rows=2, cols=1, row_heights=[0.66, 0.34], vertical_spacing=0.16,
                    subplot_titles=["<b>Trailing 100-PA wOBA and xwOBA</b>", "<b>Change in wOBA after each candidate breakpoint (post minus pre)</b>"])
rf["game_date"] = pd.to_datetime(rf.game_date)
fig.add_vrect(x0=rf.game_date.min(), x1="2026-06-01", fillcolor="rgba(0,45,114,0.06)", line_width=0, row=1, col=1)
fig.add_trace(go.Scatter(x=rf.game_date, y=rf.roll_xwoba, mode="lines", line=dict(color=NAVY, width=2, dash="dash"), name="xwOBA (XW-1)",
                         hovertemplate="%{x|%b %d}<br>xwOBA %{y:.3f}<extra></extra>"), row=1, col=1)
fig.add_trace(go.Scatter(x=rf.game_date, y=rf.roll_woba, mode="lines", line=dict(color=RED, width=3), name="wOBA",
                         hovertemplate="%{x|%b %d}<br>wOBA %{y:.3f}<extra></extra>"), row=1, col=1)
for lab, d, v in (("trough", H["roll_min"]["date"], H["roll_min"]["woba"]), ("peak", H["roll_max"]["date"], H["roll_max"]["woba"])):
    fig.add_annotation(x=d, y=v, text=f"{lab} {f3(v)}<br>{pd.Timestamp(d):%b %d}", showarrow=True, arrowhead=0, ax=0, ay=(30 if lab == "trough" else -30),
                       font=dict(size=11, color=INK), row=1, col=1)
fig.add_vline(x="2026-06-01", line=dict(color=NAVY, width=1, dash="dot"), row=1, col=1)
fig.add_annotation(x="2026-06-01", y=0.36, text="June 1", showarrow=False, xanchor="left", xshift=4, font=dict(size=11, color=NAVY), row=1, col=1)
bs["breakpoint"] = pd.to_datetime(bs.breakpoint)
for r in bs.itertuples():
    fig.add_trace(go.Scatter(x=[r.breakpoint, r.breakpoint], y=[0, r.d_woba], mode="lines", line=dict(color=LGRAY, width=2), showlegend=False,
                             hoverinfo="skip"), row=2, col=1)
fig.add_trace(go.Scatter(x=bs.breakpoint, y=bs.d_woba, mode="markers+text", marker=dict(size=11, color=[RED if v > 0 else NAVY for v in bs.d_woba],
                         line=dict(color="#ffffff", width=2)), text=[f"{v:+.3f}".replace("0.", ".") for v in bs.d_woba],
                         textposition=["top center" if v > 0 else "bottom center" for v in bs.d_woba], textfont=dict(size=10.5, color=INK),
                         showlegend=False, customdata=np.c_[bs.pre_pa, bs.post_pa],
                         hovertemplate="split %{x|%b %d}<br>Δ wOBA %{y:+.3f}<br>PA %{customdata[0]} / %{customdata[1]}<extra></extra>"), row=2, col=1)
fig.add_hline(y=0, line=dict(color=GRAY, width=1), row=2, col=1)
fig.update_yaxes(title_text="wOBA", tickformat=".3f", row=1, col=1); fig.update_yaxes(title_text="Δ wOBA", tickformat="+.3f", range=[-0.08, 0.06], row=2, col=1)
fig.update_xaxes(range=["2026-04-01", "2026-09-30"], row=2, col=1)
j = H["scan"]["2026-06-01"]
ok = abs(bs.loc[bs.breakpoint == "2026-06-01", "d_woba"].iloc[0] - j["d_woba"]) < 1e-12 and H["scan_positive"] == int((bs.d_woba > 0).sum())
base(fig, "The turn was a June-to-August surge, not a new level",
     f"Rolling wOBA bottomed at {f3(H['roll_min']['woba'])} on {pd.Timestamp(H['roll_min']['date']):%b %d} and peaked at {f3(H['roll_max']['woba'])} on "
     f"{pd.Timestamp(H['roll_max']['date']):%b %d}, then gave most of it back. A June 1 split gains only {j['d_woba']:+.3f} wOBA "
     f"({j['pre_pa']} vs {j['post_pa']} PA); {H['scan_positive']} of {H['scan_n']} candidate breakpoints show any gain (RC-5).", h=700)
ship(fig, "f2_rolling_form", ok, dict(source=["rolling_100pa", "breakpoint_scan"]))

# F3 TR-1 ----------------------------------------------------------------------------------------------------
tr = R("tr1_ledger").iloc[::-1]
units = tr.delta * tr.direction / tr.bar
fig = go.Figure()
fig.add_vrect(x0=1, x1=2.2, fillcolor="rgba(232,24,40,0.07)", line_width=0)
fig.add_vrect(x0=-0.25, x1=0.25, fillcolor="rgba(140,140,140,0.12)", line_width=0)
for y, u in zip(tr.label, units):
    fig.add_trace(go.Scatter(x=[0, u], y=[y, y], mode="lines", line=dict(color=LGRAY, width=2), showlegend=False, hoverinfo="skip"))
fmt = lambda m, v: pct(v, 1) if m in ("krate", "bbrate", "chase_rate", "hard_hit_rate", "whiff_rate") else f3(v)   # noqa: E731
for v, c in VERD.items():
    t = tr[tr.verdict == v]
    if not len(t):
        continue
    u = t.delta * t.direction / t.bar
    fig.add_trace(go.Scatter(x=u, y=t.label, mode="markers", marker=dict(size=15, color=c, line=dict(color="#ffffff", width=2)), name=v,
                             customdata=np.c_[[fmt(m, a) for m, a in zip(t.metric, t.pre)], [fmt(m, b) for m, b in zip(t.metric, t.post)], t.family],
                             hovertemplate="%{y} (%{customdata[2]})<br>%{customdata[0]} → %{customdata[1]}<br>%{x:.2f} bars<extra>" + v + "</extra>"))
for r, u in zip(tr.itertuples(), units):
    fig.add_annotation(x=2.25, y=r.label, text=f"{fmt(r.metric, r.pre)} → {fmt(r.metric, r.post)}  <b>{r.verdict}</b>", showarrow=False,
                       xanchor="left", font=dict(size=11.5, color=INK))
fig.add_hline(y=5.5, line=dict(color=GRAY, width=1, dash="dot"))
fig.add_annotation(x=-1.95, y=9.35, text="RESULTS", showarrow=False, xanchor="left", font=dict(size=11, color=MUTED))
fig.add_annotation(x=-1.95, y=5.2, text="PROCESS", showarrow=False, xanchor="left", font=dict(size=11, color=MUTED))
fig.update_xaxes(title_text="Movement in the predicted direction, in pre-registered bars (1 = PRESENT threshold)", range=[-2, 4.2],
                 tickvals=[-2, -1, 0, 1, 2], zeroline=True, zerolinecolor=GRAY)
T = H["tr1"]
ok = T["call"] == "NO TURN" and (tr.verdict == "PRESENT").sum() == 1
base(fig, f"TR-1 verdict: {T['call']}. Batting average turned; the skills did not",
     f"Ten signatures registered in the BID before any split was computed; pre = Mar 26-May 31 ({T['pre_pa']} PA), post = Jun 1-Sep 27 ({T['post_pa']} PA). "
     f"Results {T['results']}, process {T['process']}. BABIP {f3(T['pre_babip'])} → {f3(T['post_babip'])} carried the BA gain; walks went the wrong way "
     f"(CONTRA) and chase did not move.", h=600, w=1180)
fig.update_layout(margin=dict(l=170, r=40, b=80))
ship(fig, "f3_tr1_ledger", ok, dict(source=["tr1_ledger"]))

# F4 percentile profile ----------------------------------------------------------------------------------------
pr = R("profile_percentiles")
groups = [("Approach", ["swing_rate", "chase_rate", "whiff_rate", "ooz_contact_rate", "krate", "bbrate"]),
          ("Contact", ["hard_hit_rate", "barrel_rate", "gb_rate", "mean_la", "attack_angle_mu", "bat_speed_mu"]),
          ("Results", ["babip", "ba", "obp", "iso", "woba", "xwoba"])]
fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.12, subplot_titles=[f"<b>{g}</b>" for g, _ in groups])
def pcol(p):
    return RED if p >= 67 else ("#F4B6BB" if p >= 50 else ("#9DB0D3" if p >= 33 else NAVY))
for i, (g, ms) in enumerate(groups, start=1):
    t = pr.set_index("metric").loc[ms].iloc[::-1].reset_index()
    labs = [f"{l}" for l in t.label]
    fig.add_trace(go.Bar(x=[100] * len(t), y=labs, orientation="h", marker=dict(color="#EEF1F5"), showlegend=False, hoverinfo="skip", width=0.22), row=1, col=i)
    fig.add_trace(go.Bar(x=t.better_than, y=labs, orientation="h", marker=dict(color=[pcol(p) for p in t.better_than]), width=0.22, showlegend=False,
                         hoverinfo="skip"), row=1, col=i)
    vals = [pct(v, 1) if m not in ("mean_la", "attack_angle_mu", "bat_speed_mu", "babip", "ba", "obp", "iso", "woba", "xwoba")
            else (f"{v:.1f}°" if m in ("mean_la", "attack_angle_mu") else (f"{v:.1f} mph" if m == "bat_speed_mu" else f3(v))) for m, v in zip(t.metric, t.value)]
    fig.add_trace(go.Scatter(x=t.better_than, y=labs, mode="markers+text", marker=dict(size=26, color=[pcol(p) for p in t.better_than], line=dict(color="#ffffff", width=2)),
                             text=[str(int(p)) for p in t.better_than], textfont=dict(color="#ffffff", size=11), showlegend=False,
                             customdata=np.c_[vals, t.n, t.pool_median], hovertemplate="%{y}: %{customdata[0]}<br>better than %{x}% of %{customdata[1]}<extra></extra>"),
                  row=1, col=i)
    for y, v in zip(labs, vals):
        fig.add_annotation(x=104, y=y, text=v, showarrow=False, xanchor="left", font=dict(size=11, color=INK), row=1, col=i)
    fig.update_xaxes(range=[-6, 135], showticklabels=False, showgrid=False, title_text="", row=1, col=i)
la = H["profile"]["mean_la"]
ok = H["la_rank_low"] <= 2 and H["aa_rank_low"] == 1 and H["profile"]["whiff_rate"]["better"] >= 80 and H["profile"]["chase_rate"]["better"] <= 20
base(fig, "The profile, scored: elite bat-to-ball, a chase habit, and the flattest swing in the house",
     f"Percentile = better than X% of {H['pool_n']} Phillies hitter-seasons {H['pool_years']} (≥50 PA; launch angle n={la['n']}, bat tracking 2024+ "
     f"n={H['profile']['attack_angle_mu']['n']}). Lower is better for chase, whiff, K% and GB%; swing rate is shown raw (no good direction). "
     f"Red = top third, navy = bottom third. Value at right.", h=560, w=1240)
fig.update_layout(margin=dict(l=150, r=40, b=40), bargap=0.5, barmode="overlay")
ship(fig, "f4_profile", ok, dict(source=["profile_percentiles", "hitter_pool"]))

# F5 attack regions -------------------------------------------------------------------------------------------
ar = R("attack_regions")
me, hs = ar[ar._k == "Crawford"].set_index("region"), ar[ar._k != "Crawford"].set_index("region")
fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.1,
                    subplot_titles=["<b>Swing rate by attack region (catcher's view)</b>", "<b>Whiff rate on swings, by region</b>"])
rings = [("waste", 1.75, 1.15), ("shadow_out", HX + BALL, BALL), ("shadow_in", HX, 0.0), ("heart", HX - BALL, -BALL)]
for reg, hw, pad in rings:
    d = me.loc[reg, "swing_rate"] - hs.loc[reg, "swing_rate"]
    fill = "rgba(232,24,40,0.55)" if d > 0.04 else ("#F4B6BB" if d > 0 else ("#9DB0D3" if d > -0.04 else "rgba(0,45,114,0.45)"))
    y0, y1 = (0.6, 4.4) if reg == "waste" else (SZ_BOT - pad, SZ_TOP + pad)
    fig.add_shape(type="rect", x0=-hw, x1=hw, y0=y0, y1=y1, fillcolor=fill, line=dict(color="#ffffff", width=2), row=1, col=1)
lab_y = {"waste": 4.15, "shadow_out": SZ_TOP + 0.13, "shadow_in": SZ_TOP - 0.12, "heart": (SZ_TOP + SZ_BOT) / 2}
for reg, y in lab_y.items():
    nm = {"waste": "Chase / waste", "shadow_out": "Shadow (out)", "shadow_in": "Shadow (in)", "heart": "Heart"}[reg]
    fig.add_annotation(x=0, y=y, text=f"<b>{nm}</b>  {pct(me.loc[reg, 'swing_rate'])} <span style='color:{MUTED}'>(house {pct(hs.loc[reg, 'swing_rate'])})</span>",
                       showarrow=False, font=dict(size=11.5, color=INK), row=1, col=1)
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=12, color="rgba(232,24,40,0.55)", symbol="square"), name="swings more than the house"), row=1, col=1)
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=12, color="rgba(0,45,114,0.45)", symbol="square"), name="swings less"), row=1, col=1)
fig.update_xaxes(range=[-1.9, 1.9], title_text="Horizontal location (ft)", row=1, col=1); fig.update_yaxes(range=[0.5, 4.5], title_text="Height (ft)", scaleanchor="x", row=1, col=1)
order = ["heart", "shadow_in", "shadow_out", "waste"]
rn = ["Heart", "Shadow (in)", "Shadow (out)", "Chase / waste"]
for x, a, b in zip(rn, hs.loc[order, "whiff_rate"], me.loc[order, "whiff_rate"]):
    fig.add_trace(go.Scatter(x=[x, x], y=[a, b], mode="lines", line=dict(color=LGRAY, width=3), showlegend=False, hoverinfo="skip"), row=1, col=2)
fig.add_trace(go.Scatter(x=rn, y=hs.loc[order, "whiff_rate"], mode="markers+text", marker=dict(size=14, color=GRAY, line=dict(color="#ffffff", width=2)),
                         text=[pct(v) for v in hs.loc[order, "whiff_rate"]], textposition="middle right", textfont=dict(color=MUTED, size=11),
                         name="Phillies 2026 (others)", hovertemplate="%{x}: %{y:.1%}<extra>house</extra>"), row=1, col=2)
fig.add_trace(go.Scatter(x=rn, y=me.loc[order, "whiff_rate"], mode="markers+text", marker=dict(size=14, color=RED, line=dict(color="#ffffff", width=2)),
                         text=[pct(v) for v in me.loc[order, "whiff_rate"]], textposition="middle left", textfont=dict(color=INK, size=11),
                         name="Crawford", customdata=me.loc[order, "pitches"], hovertemplate="%{x}: %{y:.1%} (%{customdata} pitches)<extra>Crawford</extra>"), row=1, col=2)
fig.update_yaxes(title_text="Whiffs per swing", tickformat=".0%", range=[0, 0.6], row=1, col=2); fig.update_xaxes(title_text="Region", row=1, col=2)
rg, rgh = H["regions"], H["regions_house"]
ok = rg["waste"]["swing"] > rgh["waste"]["swing"] and rg["shadow_out"]["swing"] > rgh["shadow_out"]["swing"]
base(fig, "He swings like a hitter who expects to make contact, because he does",
     f"UC22 attack regions (ball width 0.25 ft, per-pitch zone). Crawford swings at {pct(rg['waste']['swing'])} of chase/waste pitches (house "
     f"{pct(rgh['waste']['swing'])}) and {pct(rg['shadow_out']['swing'])} just off the edge (house {pct(rgh['shadow_out']['swing'])}), yet whiffs on only "
     f"{pct(rg['waste']['whiff'])} of those chase swings (house {pct(rgh['waste']['whiff'])}). House = other Phillies hitters, 2026.", h=600, w=1180)
ship(fig, "f5_attack_regions", ok, dict(source=["attack_regions"]))

# F6 GB and HH cumulative --------------------------------------------------------------------------------------
ok = abs(R("cum_gb_rate").dropna().query("series == @HL").value.iloc[-1] - cxc.loc[HL, "gb_rate"]) < 1e-9
ghost_panels(["gb_rate", "hard_hit_rate"], ["Ground-ball rate", "Hard-hit rate"], [".1%", ".1%"],
             f"Ground balls never let go: {pct(H['gb_rate'], 1)} GB rate, {pct(H['hard_hit_rate'], 1)} hard-hit",
             f"Cumulative by plate appearance vs the CX-1 centre-field seasons. Hard contact was mid-pack ({ordn(cx['rank']['hh'])} of {cx['n']} at matched volume); "
             f"the grounders were not ({ordn(cx['rank']['gb'])} of {cx['n']}, lower is better). Mean launch angle {H['mean_la']:.1f}° against {H['la_house_2026_mean']:.1f}° "
             f"for the rest of the 2026 Phillies; average attack angle {H['attack_angle_mu']:.1f}°, lowest of {H['profile']['attack_angle_mu']['n']} tracked Phillies seasons.",
             "f6_cumulative_gb_hh", ok, "Hard-hit = BIP ≥ 95 mph over all BIP (inherited O-8 denominator; 4 untracked).", h=540)

# F7 chase map vs RHP ------------------------------------------------------------------------------------------
op = R("ooz_pitches")
op = op[op.p_throws == "R"]
grp = ["fastball", "breaking", "offspeed"]
cc = H["cc1"]["by"]
fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.05,
                    subplot_titles=[f"<b>{g.title()}</b>: chased {pct(cc[f'R_{g}']['chase'])} of {cc[f'R_{g}']['ooz']} · CC-1 {cc[f'R_{g}']['runs']:.1f} runs" for g in grp])
for i, g in enumerate(grp, start=1):
    t = op[op.pitch_group == g]
    tk, sw = t[~t.swing], t[t.swing]
    fig.add_trace(go.Scatter(x=tk.plate_x, y=tk.plate_z, mode="markers", marker=dict(size=5, color=LGRAY), name="taken", legendgroup="t", showlegend=(i == 1),
                             hoverinfo="skip"), row=1, col=i)
    fig.add_trace(go.Scatter(x=sw.plate_x, y=sw.plate_z, mode="markers", marker=dict(size=8, color=PG[g], line=dict(color="#ffffff", width=1)),
                             name=f"chased ({g})", customdata=np.c_[sw.pitch_type, sw.balls, sw.strikes],
                             hovertemplate="%{customdata[0]} in %{customdata[1]}-%{customdata[2]}<extra>chase</extra>"), row=1, col=i)
    mx, mz = t.plate_x.mean(), t.plate_z.mean()
    fig.add_trace(go.Scatter(x=[mx], y=[mz], mode="markers", marker=dict(size=16, symbol="x-thin", line=dict(color=INK, width=3)), name="mean location (client chart)",
                             legendgroup="m", showlegend=(i == 1), hovertemplate=f"mean {g}: %{{x:.2f}}, %{{y:.2f}}<extra></extra>"), row=1, col=i)
    zone(fig, 1, i)
    fig.update_xaxes(range=[-2.6, 2.6], title_text="ft (catcher's view)", row=1, col=i); fig.update_yaxes(range=[-0.6, 5.0], scaleanchor=f"x{'' if i == 1 else i}", row=1, col=i)
fig.update_yaxes(title_text="Height (ft)", row=1, col=1)
rr = sum(v["runs"] for k, v in cc.items() if k.startswith("R_"))
ok = cc["R_breaking"]["chase"] > cc["R_fastball"]["chase"] and cc["R_fastball"]["runs"] == max(v["runs"] for v in cc.values())
base(fig, "Where the walks went: righty spin below the zone, righty heat above it",
     f"Out-of-zone pitches from RHP, catcher's view; coloured dots are chases. He chases RHP breaking balls ({pct(cc['R_breaking']['chase'])}) and changeups "
     f"({pct(cc['R_offspeed']['chase'])}), far above the house chase median ({pct(H['cc1']['pool_chase_median'])}), but the costliest chases by volume are elevated fastballs. CC-1 = runs given up versus the "
     f"house take in the same count: {rr:.1f} of his {H['cc1']['runs']:.1f} came against righties.", h=560, w=1240)
ship(fig, "f7_chase_map_rhp", ok, dict(source=["ooz_pitches", "cc1_by_hand_group"]))

# F8 RHP breaking balls -----------------------------------------------------------------------------------------
bb, hh = R("rhp_breaking_bip"), R("rhp_breaking_hits")
LV = {"AAA 2025": NAVY, "MLB 2026": RED}
fig = make_subplots(rows=1, cols=3, column_widths=[0.42, 0.29, 0.29], horizontal_spacing=0.06,
                    subplot_titles=["<b>Exit velocity on contact, by pitch</b>", "<b>Where his hits came from: AAA 2025</b>", "<b>MLB 2026</b>"])
types = [t for t in ["SL", "ST", "CU", "KC", "SV"] if t in set(bb.pitch_type)]
for lvl, c in LV.items():
    t = bb[(bb.level == lvl) & bb.pitch_type.isin(types)]
    fig.add_trace(go.Box(x=t.pitch_type, y=t.launch_speed, name=lvl, marker=dict(color=c, size=5), line=dict(color=c, width=1.6), boxpoints="all",
                         jitter=0.5, pointpos=0, fillcolor="rgba(0,0,0,0)", offsetgroup=lvl, legendgroup=lvl,
                         hovertemplate=lvl + " %{x}: %{y:.1f} mph<extra></extra>"), row=1, col=1)
fig.add_hline(y=95, line=dict(color=GRAY, width=1, dash="dot"), row=1, col=1)
fig.add_annotation(x=0.01, xref="x domain", y=95, text="95 mph", showarrow=False, xanchor="left", yshift=-9, font=dict(size=10.5, color=MUTED), row=1, col=1)
fig.update_layout(boxmode="group")
fig.update_yaxes(title_text="Exit velocity (mph)", row=1, col=1); fig.update_xaxes(title_text="Pitch type", categoryorder="array", categoryarray=types, row=1, col=1)
for i, lvl in ((2, "AAA 2025"), (3, "MLB 2026")):
    t = hh[hh.level == lvl]
    zone(fig, 1, i, heart=True)
    fig.add_trace(go.Scatter(x=t.plate_x, y=t.plate_z, mode="markers",
                             marker=dict(size=11, color=LV[lvl], line=dict(color="#ffffff", width=1.5), symbol=["star" if e != "single" else "circle" for e in t.events]),
                             showlegend=False, customdata=np.c_[t.pitch_name, t.events, t.region],
                             hovertemplate="%{customdata[0]} → %{customdata[1]}<br>%{customdata[2]}<extra>" + lvl + "</extra>"), row=1, col=i)
    hz = H["rhp_bb_hits_heart"][lvl]
    fig.add_annotation(x=0, y=0.2, text=f"{hz['heart']} of {hz['hits']} hits on heart pitches", showarrow=False, font=dict(size=11.5, color=INK), row=1, col=i)
    fig.update_xaxes(range=[-2.0, 2.0], title_text="ft (catcher's view)", row=1, col=i); fig.update_yaxes(range=[0, 4.6], scaleanchor=f"x{i}", row=1, col=i)
A, M = H["rhp_bb"]["AAA 2025"], H["rhp_bb"]["MLB 2026"]
ok = H["rhp_bb_hits_heart"]["AAA 2025"]["share"] > H["rhp_bb_hits_heart"]["MLB 2026"]["share"] and A["hh"] > M["hh"]
base(fig, "Righty spin: the hangers stopped coming, and so did the hard contact",
     f"RHP breaking balls (SL/ST/CU/KC). Hard-hit {pct(A['hh'])} in AAA 2025 → {pct(M['hh'])} in MLB 2026; average EV {A['ev']:.1f} → {M['ev']:.1f} mph; "
     f"chase {pct(A['chase'])} → {pct(M['chase'])}. In AAA most of his hits came on breaking balls left in the heart (dotted box); in MLB only a few did. "
     f"AAA is a supporting tier (different level, {H['aaa']['ev_untracked_bip']} untracked BIP). Stars = extra-base hits.", h=580, w=1240)
ship(fig, "f8_rhp_breaking", ok, dict(source=["rhp_breaking_bip", "rhp_breaking_hits", "rhp_breaking_by_level"]))

# F9 spray chart on a drawn field ------------------------------------------------------------------------------
sp = R("spray_bip")
dims = {-45: 329, -22.5: 374, 0: 401, 22.5: 369, 45: 330}            # CBP park-dimension SoT (cbp-spray_AI.md)
ang = np.linspace(-45, 45, 91)
rad = np.interp(ang, list(dims.keys()), list(dims.values()))
wx, wy = rad * np.sin(np.radians(ang)), rad * np.cos(np.radians(ang))
ia = np.linspace(-45, 45, 60); irad = 155
fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.04, subplot_titles=["<b>AAA 2025</b>", "<b>MLB 2026</b>"])
for i, lvl in ((1, "AAA 2025"), (2, "MLB 2026")):
    fig.add_trace(go.Scatter(x=np.r_[0, wx, 0], y=np.r_[0, wy, 0], fill="toself", fillcolor="#EEF1F5", line=dict(color=GRAY, width=1.4), hoverinfo="skip",
                             showlegend=False), row=1, col=i)
    fig.add_trace(go.Scatter(x=np.r_[0, irad * np.sin(np.radians(ia)), 0], y=np.r_[0, irad * np.cos(np.radians(ia)), 0], fill="toself", fillcolor="#E9DCC0",
                             line=dict(color="#C9A66B", width=1), hoverinfo="skip", showlegend=False), row=1, col=i)
    b = 90 / np.sqrt(2)
    fig.add_trace(go.Scatter(x=[0, b, 0, -b, 0], y=[0, b, 2 * b, b, 0], fill="toself", fillcolor="#7FA36B", line=dict(color="#ffffff", width=1.5),
                             hoverinfo="skip", showlegend=False), row=1, col=i)
    for s in (-1, 1):   # DR-1 wedge boundaries (slope 4.7)
        fig.add_trace(go.Scatter(x=[0, s * 420 / 4.7], y=[0, 420], mode="lines", line=dict(color=GRAY, width=1, dash="dot"), hoverinfo="skip", showlegend=False), row=1, col=i)
    t = sp[(sp.level == lvl) & (sp.rhp_breaking)]
    o = sp[(sp.level == lvl) & (~sp.rhp_breaking) & (sp.is_hit)]
    fig.add_trace(go.Scatter(x=o.loc_x, y=o.loc_y, mode="markers", marker=dict(size=5, color="rgba(196,201,210,0.55)"), name="hits on everything else",
                             legendgroup="o", showlegend=(i == 1), hoverinfo="skip"), row=1, col=i)
    for flag, c, nm, sz in ((False, GRAY, "outs, RHP breaking ball", 7), (True, RED, "hits, RHP breaking ball", 11)):
        u = t[t.is_hit == flag]
        fig.add_trace(go.Scatter(x=u.loc_x, y=u.loc_y, mode="markers", marker=dict(size=sz, color=c, line=dict(color="#ffffff", width=1.2),
                                 symbol=["star" if e in ("double", "triple", "home_run") else "circle" for e in u.events]), name=nm, legendgroup=nm,
                                 showlegend=(i == 1), customdata=np.c_[u.events, u.pitch_type, u.launch_speed.round(1)],
                                 hovertemplate="%{customdata[1]} → %{customdata[0]}<br>%{customdata[2]} mph<extra></extra>"), row=1, col=i)
    d = {k.split("|")[2]: v for k, v in H["direction"].items() if k.startswith(f"{lvl}|rhpbb")}
    for nm, x in (("Oppo", -230), ("Straightaway", 0), ("Pull", 230)):
        fig.add_annotation(x=x, y=448, text=f"<b>{nm} {pct(d[nm]['share'])}</b>", showarrow=False, font=dict(size=12, color=RED if nm == "Pull" else INK), row=1, col=i)
    fig.update_xaxes(range=[-340, 340], visible=False, row=1, col=i); fig.update_yaxes(range=[-20, 520], visible=False, scaleanchor=f"x{'' if i == 1 else i}", row=1, col=i)
mp, mo = H["direction"]["MLB 2026|rhpbb|Pull"]["share"], H["direction"]["MLB 2026|other|Pull"]["share"]
ok = mp > mo + 0.15
base(fig, f"Against righty spin he still pulls: {pct(mp)} to right field, against {pct(mo)} on everything else",
     f"Balls in play against RHP breaking balls, schematic field at CBP dimensions (329-374-401-369-330). Dotted lines are the house DR-1 pull/straightaway/oppo "
     f"boundaries; shares are of classifiable BIP. On everything else his hits already go the other way ({pct(H['dir_mlb_hits']['Oppo'])} of 2026 hits went oppo). "
     f"Stars = extra-base hits.", h=640, w=1240)
fig.update_layout(plot_bgcolor="#ffffff")
ship(fig, "f9_spray_rhp_breaking", ok, dict(source=["spray_bip", "direction_shares"]))

# F10 centre field --------------------------------------------------------------------------------------------
xo = R("xo2_opportunities")
xo = xo[xo.xout.notna()].copy()
xo["loc_x"], xo["loc_y"] = 2.495671 * (xo.hc_x - 125.42), 2.495671 * (198.27 - xo.hc_y)
xo["game_date"] = pd.to_datetime(xo.game_date)
xo = xo.sort_values(["game_date", "game_pk", "at_bat_number"])
xo["cum_oae"] = xo.oae.cumsum()
fig = make_subplots(rows=1, cols=2, column_widths=[0.46, 0.54], horizontal_spacing=0.07,
                    subplot_titles=["<b>Every CF-sector air ball with him in centre</b>", "<b>Running outs above expected (XO-2)</b>"])
fig.add_trace(go.Scatter(x=np.r_[0, wx, 0], y=np.r_[0, wy, 0], fill="toself", fillcolor="#EEF1F5", line=dict(color=GRAY, width=1.4), hoverinfo="skip", showlegend=False), row=1, col=1)
for s in (-1, 1):
    a15 = np.radians(15)
    fig.add_trace(go.Scatter(x=[0, s * 430 * np.sin(a15)], y=[0, 430 * np.cos(a15)], mode="lines", line=dict(color=GRAY, width=1, dash="dot"), hoverinfo="skip",
                             showlegend=False), row=1, col=1)
cats = [("caught", xo[xo.is_out], NAVY, "outs"), ("fell, likely out (xOut ≥ 70%)", xo[~xo.is_out & (xo.xout >= 0.7)], RED, "should-have-been outs"),
        ("fell, tough (xOut < 70%)", xo[~xo.is_out & (xo.xout < 0.7)], GHOST, "hits on tough balls")]
for nm, t, c, _ in cats:
    fig.add_trace(go.Scatter(x=t.loc_x, y=t.loc_y, mode="markers", name=nm, marker=dict(size=4 + 10 * t.xout, color=c, line=dict(color="#ffffff", width=1)),
                             customdata=np.c_[t.events, (100 * t.xout).round(0), t.launch_speed, t.launch_angle],
                             hovertemplate="%{customdata[0]}<br>xOut %{customdata[1]}%<br>%{customdata[2]} mph, %{customdata[3]}°<extra></extra>"), row=1, col=1)
fig.update_xaxes(range=[-260, 260], visible=False, row=1, col=1); fig.update_yaxes(range=[60, 470], visible=False, scaleanchor="x", row=1, col=1)
fig.add_trace(go.Scatter(x=xo.game_date, y=xo.cum_oae, mode="lines", line=dict(color=RED, width=3), name="Crawford 2026, running OAE",
                         hovertemplate="%{x|%b %d}: %{y:+.1f}<extra></extra>"), row=1, col=2)
fig.add_hline(y=0, line=dict(color=GRAY, width=1), row=1, col=2)
for m, txt in ((4, "Mar/Apr: −3 OAA (CI-3)"), (5, "May: OAA 0 (CI-3)")):
    d = xo[xo.game_date.dt.month == m]
    fig.add_annotation(x=d.game_date.iloc[-1], y=d.cum_oae.iloc[-1], text=txt, showarrow=True, arrowhead=0, ax=30, ay=-34, font=dict(size=10.5, color=MUTED), row=1, col=2)
fig.add_annotation(x=xo.game_date.iloc[-1], y=xo.cum_oae.iloc[-1], text=f"<b>{H['xo2']['oae']:+.1f}</b>", showarrow=False, xanchor="left", xshift=6,
                   font=dict(color=RED, size=14), row=1, col=2)
fig.update_yaxes(title_text="Outs minus expected outs", row=1, col=2); fig.update_xaxes(title_text="", row=1, col=2)
X, S = H["xo2"], H["xo2_sens"]
ok = abs(xo.oae.sum() - X["oae"]) < 1e-9 and H["xo2_sign_stable"]
base(fig, f"Centre field: about {abs(X['oae']):.0f} outs short of what the ball flight said, and the notebook's method could not see it",
     f"XO-2 proxy: {X['scored']} air balls ≥150 ft within 15° of dead centre with him in CF, each scored by the out share of similar balls (EV ±3, LA ±2, "
     f"distance ±10 ft, direction ±10°) in {X['pool_n']:,} house comparisons. {X['outs']} outs vs {X['xouts']:.1f} expected = {X['oae']:+.1f}, "
     f"{ordn(X['ctx_rank'])} of {X['ctx_n']} Phillies CF seasons since 2015. Every neighbourhood variant is negative ({S['v1']['oae']:+.1f} to {S['v3']['oae']:+.1f}). "
     f"External: −8 OAA, −2 DRS (CI-2). No catch probability in the log; read the rank and the sign, not the decimal.", h=600, w=1240)
ship(fig, "f10_centre_field", ok, dict(source=["xo2_opportunities", "xo2_sensitivity", "xo2_cf_context"]))

pd.DataFrame(BRAND).to_csv(OUT / "dp_uc54_brand_checks.csv", index=False)
(OUT / "dp_uc54_figure_specs.json").write_text(json.dumps(SPECS, indent=1), encoding="utf-8")
print("figures:", len(SPECS), "all brand checks pass")
