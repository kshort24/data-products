"""dp_uc56_build_figs.py - nine figures for UC #56 / uc-pos-021 (PNG for the PDF, JSON for the dashboard).
House rules (dp_uc48-55_build_figs; UC55 shell carried verbatim, shells carried): reads ONLY out/dp_uc56_* receipts; computes no KPI; each figure asserts
the claim its subtitle makes before it is written; print = plotly_white + Arial; brand-palette check ->
out/dp_uc56_brand_checks.csv. Encoding: Phillies red = the highlight (2026, a Good era), gray = context (prior seasons, Bad
eras), navy = reference lines. The red/navy/gray trio is a highlight-vs-context encoding with direct labels, not a categorical
palette (validator: separation PASS, lightness/chroma flags on navy/gray by design - out/dp_uc56_palette_validation.txt).
Direction / pitch-group trio PG-1 validated light + dark."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dp_uc56_kernel as K  # noqa: E402  (constants only; no KPI is computed here)

OUT = K.OUT
RED, NAVY, GRAY, LGRAY, INK, MUTED, GHOST = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170", "#C3C9D2"
PG = {"fastball": "#C77800", "breaking": "#6250D6", "offspeed": "#1A9E77"}          # PG-1 (validated)
DIRC = {"Pull": "#C77800", "Straightaway": "#6250D6", "Oppo": "#1A9E77"}              # same validated trio
VERD = {"PRESENT": RED, "WEAK": GRAY, "ABSENT": LGRAY, "CONTRA": NAVY, "NO DATA": LGRAY}
ALLOWED = {RED, NAVY, GRAY, LGRAY, INK, MUTED, GHOST, "#ffffff", *PG.values(), "#F4B6BB", "#9DB0D3", "#EEF1F5", "#f3f3f3",
           "rgba(232,24,40,0.08)", "rgba(232,24,40,0.10)", "rgba(0,45,114,0.06)", "rgba(140,140,140,0.25)", "rgba(140,140,140,0.12)",
           "rgba(232,24,40,0.55)", "rgba(0,45,114,0.45)", "rgba(196,201,210,0.55)", "rgba(0,0,0,0)", "#C9A66B", "#E9DCC0", "#7FA36B",
           "rgba(127,163,107,0.18)", "rgba(201,166,107,0.18)", "rgba(0,45,114,0.10)"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=72, r=30, t=118, b=66), legend=dict(orientation="h", y=-0.16, x=0, yanchor="top"))
H = json.loads((OUT / f"{K.P}headlines.json").read_text(encoding="utf-8"))
R = lambda n: pd.read_csv(OUT / f"{K.P}{n}.csv")              # noqa: E731
SPECS, BRAND = [], []
pct = lambda x, d=0: f"{100 * x:.{d}f}%"                       # noqa: E731
f3 = lambda x: f"{x:.3f}".replace("0.", ".", 1) if abs(x) < 1 else f"{x:.3f}"   # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
YEARS = [2022, 2023, 2024, 2025, 2026]
S = H["season"]


def wrap(t, n=150):
    out, cur = [], ""
    for w in t.split(" "):
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return "<br>".join(out + [cur])


def base(fig, title, subtitle, h=560, w=1100):
    nl = wrap(subtitle).count("<br>") + 1
    lay = dict(LAYOUT)
    lay["margin"] = dict(LAYOUT["margin"], t=96 + 19 * nl + 34)
    fig.update_layout(**lay, height=h + 19 * max(nl - 2, 0), width=w,
                      title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
                                 subtitle=dict(text=wrap(subtitle), font=dict(size=12.5, color=MUTED))))
    fig.update_xaxes(gridcolor="#eeeeee", zeroline=False)
    fig.update_yaxes(gridcolor="#eeeeee", zeroline=False)
    return fig


def colors_in(fig):
    js, found = fig.to_plotly_json(), set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("color", "fillcolor", "bgcolor", "line_color") and isinstance(v, str):
                    found.add(v)
                elif k == "color" and isinstance(v, (list, tuple)):
                    found.update(x for x in v if isinstance(x, str))
                elif k == "colorscale":
                    continue
                else:
                    walk(v)
        elif isinstance(o, (list, tuple)):
            for x in o:
                walk(x)
    walk(js["data"])
    walk(js["layout"].get("shapes", []))
    walk(js["layout"].get("annotations", []))
    return found


def ship(fig, key, claim_ok: bool, meta: dict):
    lay = fig.layout
    off = sorted(c for c in colors_in(fig) if c not in ALLOWED)
    checks = dict(claim_asserted=bool(claim_ok), font_arial=lay.font.family == "Arial", has_title=bool(lay.title.text),
                  has_subtitle=bool(lay.title.subtitle.text), palette_ok=not off)
    BRAND.append(dict(figure=key, **checks, off_palette=";".join(off)))
    assert all(checks.values()), (key, checks, off)
    fig.write_image(OUT / f"{K.P}{key}.png", scale=2)
    (OUT / f"{K.P}{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


POSC = {"2B": "#C77800", "3B": "#6250D6", "SS": "#1A9E77", "LF": NAVY, "CF": GRAY}   # PG-1 trio + navy/gray (validated, 05 §4)
ALLOWED |= set(POSC.values())
S = {int(k): v for k, v in H["season"].items()}
GOV = [2023, 2024, 2025, 2026]


def fmtv(m, v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if m in ("ev_mu", "ev50", "ev90", "ev_max", "bat_speed_mu"):
        return f"{v:.1f}"
    if m in ("ba", "obp", "slg", "ops", "woba", "xwoba", "oz_ba", "oz_xba", "babip", "iso"):
        return f3(v)
    return pct(v, 1)


# F1 - cumulative wOBA and OPS, 2026 over 2022-25 (house cumulative-chart skill; CM-1 frames) ---------------------------
fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.10, subplot_titles=["<b>wOBA</b>", "<b>OPS</b>"])
ok = H["cum_2026_last_of_4_share"] == 1.0
for i, m in enumerate(("woba", "ops"), start=1):
    cf = R(f"cum_{m}").dropna(subset=["value"])
    cf["series"] = cf.series.astype(str)
    ends = cf.groupby("series").last()
    ok &= abs(ends.loc["2026", "value"] - S[2026][m]) < 1e-9
    basev = H["baseline"][m]
    for yr in YEARS[:-1]:
        g = cf[cf.series == str(yr)]
        fig.add_trace(go.Scatter(x=g.cum_pa, y=g.value, mode="lines", line=dict(color=GHOST if yr != 2025 else GRAY, width=1.3, dash="dot" if yr == 2022 else "solid"),
                                 name="2022-25 (2025 darker; 2022 dotted, 59 PA)", legendgroup="ghost", showlegend=(i == 1 and yr == 2022),
                                 hovertemplate=f"{yr}<br>PA %{{x}}<br>{m} %{{y:.3f}}<extra></extra>"), row=1, col=i)
        fig.add_annotation(x=g.cum_pa.iloc[-1], y=g.value.iloc[-1], text=f"{yr} {f3(g.value.iloc[-1])}", showarrow=False, xanchor="left",
                           xshift=4, font=dict(size=10.5, color=MUTED), row=1, col=i)
    me = cf[cf.series == "2026"]
    fig.add_hline(y=basev, line=dict(color=NAVY, dash="dot", width=1.4), row=1, col=i)
    fig.add_annotation(x=8, y=basev, text=f"2023-25 pooled {f3(basev)}", showarrow=False, xanchor="left", yshift=9,
                       font=dict(size=10.5, color=NAVY), row=1, col=i)
    fig.add_trace(go.Scatter(x=me.cum_pa, y=me.value, mode="lines", line=dict(color=RED, width=3.4), name="2026",
                             legendgroup="hi", showlegend=(i == 1), hovertemplate=f"2026<br>PA %{{x}}<br>{m} %{{y:.3f}}<extra></extra>"), row=1, col=i)
    fig.add_annotation(x=me.cum_pa.iloc[-1], y=me.value.iloc[-1], text=f"<b>{f3(me.value.iloc[-1])}</b>", showarrow=False, xanchor="left",
                       xshift=6, yshift=-10, font=dict(color=RED, size=14), row=1, col=i)
    fig.update_xaxes(title_text="Plate appearance", range=[0, 335], row=1, col=i)
    fig.update_yaxes(tickformat=".3f", row=1, col=i)
fig.add_annotation(x=0, y=-0.3, xref="paper", yref="paper", showarrow=False, xanchor="left", font=dict(size=11, color=MUTED),
                   text="Lines start at 25 PA; endpoints reconcile to the house season line (CM-1, tol 1e-9). Regular season only (no spring, no Wild Card).")
base(fig, f"2026 trailed every prior Phillies season, start to finish: {f3(S[2026]['woba'])} wOBA, {f3(S[2026]['ops'])} OPS",
     f"Cumulative by plate appearance, 2026 against his 2022-25 Phillies seasons. At every 50-PA checkpoint (50 to 250) 2026 ranked last of his four "
     f"full Phillies seasons in both wOBA and OPS. The late climb (from {f3(H['cum_ck']['woba_200']['v'])} at 200 PA) only got it back to the bottom of the pack.",
     h=560, w=1180)
fig.update_layout(margin=dict(l=60, r=110, b=120))
ship(fig, "f1_cumulative", ok, dict(source=["cum_woba", "cum_ops", "cum_checkpoints"]))

# F2 - season card ---------------------------------------------------------------------------------------------------
card = R("season_card")
mets = ["woba", "xwoba", "obp", "bbrate", "krate", "chase_rate", "contact_rate", "ooz_contact_rate", "oz_ba", "hard_hit_rate",
        "barrel_rate", "ev50", "ev90", "ev_max", "pull_air_rate", "bat_speed_mu"]
labs = dict(zip(card.metric, card.label))
z, txt = [], []
for m in mets:
    row_z, row_t = [], []
    for y in YEARS:
        r = card[(card.metric == m) & (card.game_year == y)]
        v, b = (r.value.iloc[0], r.better_than.iloc[0]) if len(r) else (np.nan, np.nan)
        row_z.append(b)
        row_t.append(fmtv(m, None if pd.isna(v) else float(v)))
    z.append(row_z)
    txt.append(row_t)
fig = go.Figure(go.Heatmap(z=z, x=[f"{y}{' (59 PA)' if y == 2022 else ''}" for y in YEARS], y=[labs[m] for m in mets], text=txt, texttemplate="%{text}",
                           colorscale=[[0, "#9DB0D3"], [0.5, "#f3f3f3"], [1, "#F4B6BB"]], zmin=0, zmax=100, xgap=2, ygap=2,
                           colorbar=dict(title="Better than<br>% of house", ticksuffix="%", len=0.8),
                           hovertemplate="%{y} %{x}: %{text}<br>better than %{z:.0f}% of Phillies hitter-seasons<extra></extra>"))
fig.update_yaxes(autorange="reversed")
orw = H["own_rank_2026"]
ok = orw["woba"] == 4 and orw["xwoba"] == 1 and orw["ev90"] == 1 and orw["chase_rate"] == 4
base(fig, f"Results down, contact quality up: 2026 had his worst wOBA and his best xwOBA and EV90",
     f"Five Phillies seasons on the house KPI panel plus the client's batted-ball asks. Cell colour = share of {H['pool_n']} Phillies hitter-seasons "
     f"({H['pool_years']}, ≥50 PA) he beat; red = better, blue = worse (low K% and chase colour red). Of 2023-26, 2026 ranks 4th in wOBA, 1st in xwOBA "
     f"and EV90, 4th (worst) in chase and pull-air. EV50 = median EV (client definition, GL-1). Bat speed ships from 2024.", h=700, w=900)
ship(fig, "f2_season_card", ok, dict(source=["season_card"]))

# F3 - 2026 form: rolling 100-PA wOBA and xwOBA, the break (TR-1), ER-1 ------------------------------------------------
rf = R("rolling_100pa")
g = rf[rf.game_year == 2026].copy()
g["game_date"] = pd.to_datetime(g.game_date)
T = H["tr1"]["rows"]
asb = pd.Timestamp(H["asb_first_game_2026"])
# Q-1 (render QA): plotted on the PA index, not the date - same-day PAs stacked into vertical jumps on a date axis
bpa = int(g[g.game_date >= asb].pa_idx.min()) if (g.game_date >= asb).any() else None
nbreak = int(H["tr1"]["pre_pa"]) + 1                       # first post-break PA in the season sequence
fig = go.Figure()
fig.add_vrect(x0=nbreak, x1=int(g.pa_idx.max()) + 2, fillcolor="rgba(0,45,114,0.06)", line_width=0)
fig.add_trace(go.Scatter(x=g.pa_idx, y=g.roll_woba, mode="lines", line=dict(color=RED, width=3.2), name="wOBA, last 100 PA",
                         customdata=g.game_date.dt.strftime("%b %d"), hovertemplate="PA %{x} (%{customdata})<br>wOBA %{y:.3f}<extra></extra>"))
fig.add_trace(go.Scatter(x=g.pa_idx, y=g.roll_xwoba, mode="lines", line=dict(color=NAVY, width=2, dash="dash"), name="xwOBA, last 100 PA",
                         customdata=g.game_date.dt.strftime("%b %d"), hovertemplate="PA %{x} (%{customdata})<br>xwOBA %{y:.3f}<extra></extra>"))
fig.add_hline(y=H["er1"]["woba"]["career"], line=dict(color=GRAY, dash="dot", width=1.2))
fig.add_annotation(x=100, y=H["er1"]["woba"]["career"], text=f"Phillies 2023-26 wOBA {f3(H['er1']['woba']['career'])}", showarrow=False,
                   xanchor="left", yshift=9, font=dict(size=10.5, color=MUTED))
fig.add_annotation(x=nbreak, y=1.03, yref="paper", text=f"<b>After the break</b> ({asb:%b %d}, PA {nbreak}): wOBA {f3(T['R1']['pre'])} → {f3(T['R1']['post'])}, "
                   f"xwOBA {f3(T['P1']['pre'])} → {f3(T['P1']['post'])}", showarrow=False, xanchor="left", font=dict(size=11.5, color=NAVY))
fig.update_yaxes(tickformat=".3f", title_text="Rolling 100-PA rate")
fig.update_xaxes(title_text="2026 plate appearance (each point = his previous 100 PA)", range=[95, int(g.pa_idx.max()) + 4])
pw = H["er1"]["woba"]["power_2026"]
ok = H["tr1"]["call"] == "RESULTS TURN" and H["er1"]["woba"]["n_seg_2026"] == 1 and T["P1"]["post"] < T["P1"]["pre"]
base(fig, "The second-half uptick was the results catching up, not a better hitter",
     f"Rolling 100-PA wOBA (red) and xwOBA (navy) through 2026; shaded from the first game after the All-Star break (fixed in the BID before looking). "
     f"TR-1 call: {H['tr1']['call']} - results improved on all four signatures, process on none (xwOBA, K%, hard-hit and whiff moved the wrong way). "
     f"ER-1 finds no change point in 2026 (at 250 PA it would catch a .080 step only {pct(pw['0.08'])} of the time). Lines start at his 100th PA (early June).", h=540, w=1100)
ship(fig, "f3_form_2026", ok, dict(source=["rolling_100pa", "tr1_asb_ledger", "er1_segments_woba"]))

# F4 - over the hump? batted-ball indicators by season --------------------------------------------------------------
pan = [("bat_speed_mu", "Bat speed (mph)"), ("ev50", "EV50 = median EV"), ("ev90", "EV90 (mph)"), ("ev_max", "Max EV (mph)"),
       ("hard_hit_rate", "Hard-hit rate"), ("barrel_rate", "Barrel / BIP"), ("pull_air_rate", "Pull AIR%"), ("xwoba", "xwOBA")]
fig = make_subplots(rows=2, cols=4, subplot_titles=[f"<b>{l}</b>" for _, l in pan], vertical_spacing=0.2, horizontal_spacing=0.07)
for k, (m, lab) in enumerate(pan):
    rr, cc = k // 4 + 1, k % 4 + 1
    ys = [y for y in YEARS if S[y].get(m) is not None]
    vals = [S[y][m] for y in ys]
    fig.add_trace(go.Bar(x=[str(y) for y in ys], y=vals, marker_color=[RED if y == 2026 else (LGRAY if y == 2022 else GRAY) for y in ys],
                         text=[fmtv(m, v) for v in vals], textposition="outside", textfont=dict(size=10), showlegend=False, cliponaxis=False,
                         hovertemplate="%{x}: %{text}<extra></extra>"), row=rr, col=cc)
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.6 + (0.5 if m in ("bat_speed_mu", "ev50", "ev90", "ev_max") else 0.01)
    fig.update_yaxes(range=[lo - pad, hi + pad], showticklabels=False, row=rr, col=cc)
dfl = H["df"]
ok = H["wa1"]["df_count"] == 0
base(fig, f"Over the hump? Not by the batted ball: {H['wa1']['df_count']} of 6 pre-registered decline flags tripped",
     f"Season values, 2026 in red (2022 = 59 PA, pale). Against his 2023-25 Phillies mean, 2026 bat speed {dfl['DF-1']['delta']:+.1f} mph, EV90 {dfl['DF-2']['delta']:+.1f} mph, "
     f"hard-hit {100 * dfl['DF-3']['delta']:+.1f} pts, barrel {'flat' if abs(dfl['DF-4']['delta']) < 0.0005 else format(100 * dfl['DF-4']['delta'], '+.1f') + ' pts'}, xwOBA {dfl['DF-5']['delta']:+.3f}. The one slide is shape, not force: "
     f"pull-air {pct(S[2026]['pull_air_rate'], 1)} (his lowest) with ground balls at {pct(S[2026]['gb_rate'], 1)} (his highest).", h=640, w=1180)
ship(fig, "f4_over_the_hump", ok, dict(source=["season_panel", "wa1_decline_flags"]))

# F5 - approach: chase x OOZ contact among Phillies RHB, and OZ-1 -------------------------------------------------------
rhb = R("rhb_pool_2022_26")
me = rhb[rhb.batter == K.SUBJECT_ID].sort_values("game_year")
ot = rhb[rhb.batter != K.SUBJECT_ID]
fig = make_subplots(rows=1, cols=2, column_widths=[0.58, 0.42], horizontal_spacing=0.1,
                    subplot_titles=["<b>Chase rate × out-of-zone contact</b> (Phillies RHB, 2022-26)", "<b>OZ-1: out-of-zone BA vs expected</b>"])
fig.add_trace(go.Scatter(x=ot.chase_rate, y=ot.ooz_contact_rate, mode="markers", marker=dict(color=GHOST, size=np.sqrt(ot.plate_apps) * 0.9, line=dict(width=0)),
                         name="Other Phillies RHB seasons", text=ot.player_name + " " + ot.game_year.astype(str),
                         hovertemplate="%{text}<br>chase %{x:.1%} · OOZ contact %{y:.1%}<extra></extra>"), row=1, col=1)
fig.add_trace(go.Scatter(x=me.chase_rate, y=me.ooz_contact_rate, mode="lines+markers+text", line=dict(color=RED, width=1.6),
                         marker=dict(color=[RED if y == 2026 else "#F4B6BB" for y in me.game_year], size=np.sqrt(me.plate_apps) * 0.9, line=dict(color=RED, width=1)),
                         text=me.game_year.astype(str), textposition="top center", textfont=dict(color=RED, size=11), name="Sosa",
                         hovertemplate="Sosa %{text}<br>chase %{x:.1%} · OOZ contact %{y:.1%}<extra></extra>"), row=1, col=1)
fig.add_vline(x=H["rhb_chase_median"], line=dict(color=NAVY, dash="dot", width=1.2), row=1, col=1)
fig.add_hline(y=H["rhb_ooz_contact_median"], line=dict(color=NAVY, dash="dot", width=1.2), row=1, col=1)
fig.update_xaxes(title_text="Chase rate", tickformat=".0%", row=1, col=1)
fig.update_yaxes(title_text="Out-of-zone contact", tickformat=".0%", row=1, col=1)
fig.add_trace(go.Bar(x=[str(y) for y in GOV], y=[S[y]["oz_ba"] for y in GOV], marker_color=[RED if y == 2026 else GRAY for y in GOV], name="OZ-BA",
                     text=[f3(S[y]["oz_ba"]) for y in GOV], textposition="outside", hovertemplate="%{x} OZ-BA %{y:.3f}<extra></extra>"), row=1, col=2)
fig.add_trace(go.Scatter(x=[str(y) for y in GOV], y=[S[y]["oz_xba"] for y in GOV], mode="markers", marker=dict(symbol="line-ew-open", size=26, color=NAVY, line=dict(width=3)),
                         name="OZ-xBA (expected)", hovertemplate="%{x} OZ-xBA %{y:.3f}<extra></extra>"), row=1, col=2)
fig.update_yaxes(tickformat=".3f", range=[0, 0.26], row=1, col=2)
rk = H["rhb_rank"]["2026"]
ok = rk["chase"]["rank"] == rk["chase"]["n"] and S[2026]["oz_call"] == "EARNED" and S[2026]["ooz_contact_rate"] > H["rhb_ooz_contact_median"]
base(fig, "The most aggressive chaser on the roster, and the out-of-zone contact is real",
     f"Left: {H['rhb_n']} Phillies RHB seasons (≥50 PA), dot size = PA; navy lines = medians. His {pct(S[2026]['chase_rate'], 1)} chase in 2026 is the highest in the pool; "
     f"his out-of-zone contact ({pct(S[2026]['ooz_contact_rate'], 1)}) sits above the median. Right: BA on PAs ending out of the zone vs the expected BA on the same at-bats "
     f"(OZ-1). 2026 ran {abs(S[2026]['oz_gap']) * 1000:.0f} points under expected - not luck carrying him. Each chase cost {H['cc1']['2026']['per100']:.1f} runs per 100 "
     f"(RHB median {H['cc1_rhb_median_per100']:.1f}); the bill is volume.", h=600, w=1180)
ship(fig, "f5_approach", ok, dict(source=["rhb_pool_2022_26", "season_panel", "cc1_chase_cost"]))

# F6 - pitch groups by season ------------------------------------------------------------------------------------
pgs = ["fastball 95+", "fastball <95", "breaking", "offspeed"]
PG_ = H["pg"]
PB = H["pg_base"]
fig = make_subplots(rows=1, cols=4, shared_yaxes=True, horizontal_spacing=0.03,
                    subplot_titles=[f"<b>{p}</b>" for p in pgs])
for i, p in enumerate(pgs, start=1):
    xs = [str(y) for y in GOV]
    xv = [PG_[f"{p}|{y}"]["xwoba"] for y in GOV]
    wv = [PG_[f"{p}|{y}"]["whiff"] for y in GOV]
    n = [PG_[f"{p}|{y}"]["pa"] for y in GOV]
    fig.add_trace(go.Bar(x=xs, y=xv, marker_color=[RED if y == 2026 else GRAY for y in GOV], showlegend=False,
                         text=[f"{f3(v)}<br><span style='font-size:9px'>whiff {pct(w)}</span>" for v, w in zip(xv, wv)], textposition="outside",
                         customdata=np.c_[n, wv], hovertemplate="%{x}: xwOBA %{y:.3f}<br>PA %{customdata[0]} · whiff %{customdata[1]:.1%}<extra></extra>"), row=1, col=i)
    fig.add_hline(y=PB[p]["xwoba"], line=dict(color=NAVY, dash="dot", width=1.2), row=1, col=i)
fig.update_yaxes(tickformat=".3f", range=[0, 0.47], title_text="xwOBA (PA ending on the group)", row=1, col=1)
ok = PG_["breaking|2026"]["xwoba"] > PB["breaking"]["xwoba"] and PG_["offspeed|2026"]["whiff"] > PB["offspeed"]["whiff"] \
    and PG_["fastball 95+|2026"]["whiff"] < PB["fastball 95+"]["whiff"]
base(fig, "Velocity and breaking balls held; offspeed is where he swings and misses",
     f"xwOBA on PAs ending on each pitch group, with whiff rate per swing under each bar; navy dotted = his 2023-25 pooled xwOBA. Against 95+ fastballs his "
     f"whiff fell ({pct(PB['fastball 95+']['whiff'], 1)} → {pct(PG_['fastball 95+|2026']['whiff'], 1)}) and xwOBA matched the pooled line ({f3(PB['fastball 95+']['xwoba'])} → "
     f"{f3(PG_['fastball 95+|2026']['xwoba'])}), though below 2024-25 - a watch item, not a fall-off. Breaking balls were never a strength ({f3(PB['breaking']['woba'])} wOBA 2023-25) and 2026 was his best "
     f"expected year against them. Offspeed: whiff {pct(PG_['offspeed|2026']['whiff'], 1)} and chase {pct(PG_['offspeed|2026']['chase'], 1)}, both his worst - though the contact he made was fine. Samples are 28-83 PA per bar.",
     h=560, w=1180)
ship(fig, "f6_pitch_groups", ok, dict(source=["pitch_group_by_season", "pitch_group_baseline_2023_25"]))

# F7 - the client's scatter, rebuilt ----------------------------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=ot.swing_rate, y=ot.woba, mode="markers", marker=dict(color=GHOST, size=np.sqrt(ot.plate_apps) * 0.9), name="Other Phillies RHB seasons",
                         text=ot.player_name + " " + ot.game_year.astype(str) + " · " + ot.plate_apps.astype(str) + " PA",
                         hovertemplate="%{text}<br>swing %{x:.1%} · wOBA %{y:.3f}<extra></extra>"))
fig.add_trace(go.Scatter(x=me.swing_rate, y=me.woba, mode="lines+markers+text", line=dict(color=RED, width=1.6),
                         marker=dict(color=[RED if y == 2026 else "#F4B6BB" for y in me.game_year], size=np.sqrt(me.plate_apps) * 0.9, line=dict(color=RED, width=1)),
                         text=[f"{y}{' (59 PA)' if y == 2022 else ''}" for y in me.game_year], textposition="middle right", textfont=dict(color=RED, size=11),
                         name="Sosa", hovertemplate="Sosa %{text}<br>swing %{x:.1%} · wOBA %{y:.3f}<extra></extra>"))
fig.add_vline(x=H["rhb_swing_median"], line=dict(color=NAVY, dash="dot", width=1.2))
fig.add_hline(y=H["rhb_woba_median"], line=dict(color=NAVY, dash="dot", width=1.2))
fig.update_xaxes(title_text="Swing rate", tickformat=".0%")
fig.update_yaxes(title_text="wOBA", tickformat=".3f")
rr = H["rhb_rank"]
above = [y for y in rr if S[int(y)]["woba"] > H["rhb_woba_median"]]
ok = all(rr[y]["swing"]["percentile"] >= 75 for y in rr) and set(above) == {"2022", "2025"}
base(fig, "Always a swinger; above the RHB wOBA median only in 2025 (and 2022's 59 PA)",
     f"Your scatter, rebuilt on the house pool: {H['rhb_n']} Phillies RHB seasons 2022-26 with ≥50 PA, regular season only, dot size = PA, navy = medians. "
     f"Sosa's swing rate sat in the top quartile every season ({rr['2026']['swing']['percentile']}th percentile in 2026). Across the pool, swing rate barely tracks wOBA "
     f"(r = {H['hp09_corr']['r']:.2f}; {H['hp09_corr']['r_pa_weighted']:.2f} PA-weighted).", h=600, w=1000)
ship(fig, "f7_swing_woba", ok, dict(source=["rhb_pool_2022_26"]))

# F8 - five seasons: games by position + platoon -----------------------------------------------------------------
posg = R("games_by_position")
fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.1,
                    subplot_titles=["<b>Games by position</b> (house log)", "<b>wOBA by pitcher hand</b>"])
for p, col in POSC.items():
    g2 = posg[posg.position == p].set_index("game_year").reindex(YEARS).games.fillna(0)
    fig.add_trace(go.Bar(x=[str(y) for y in YEARS], y=g2.values, name=p, marker_color=col, hovertemplate=f"{p} %{{x}}: %{{y}} games<extra></extra>"), row=1, col=1)
fig.update_layout(barmode="stack")
pl = H["platoon"]
for hand, lab, col in (("L", "vs LHP", RED), ("R", "vs RHP", NAVY)):
    xs = [str(y) for y in GOV]
    vals = [pl[f"{hand}|{y}"]["woba"] for y in GOV]
    fig.add_trace(go.Scatter(x=xs, y=vals, mode="lines+markers+text", line=dict(color=col, width=2.4), name=lab, text=[f3(v) for v in vals],
                             textposition="top center", textfont=dict(size=10, color=col), hovertemplate=f"{lab} %{{x}}: %{{y:.3f}}<extra></extra>"), row=1, col=2)
    fig.add_hline(y=H["rhb_platoon_woba"][hand], line=dict(color=col, dash="dot", width=1), row=1, col=2)
fig.update_yaxes(title_text="Games", row=1, col=1)
fig.update_yaxes(tickformat=".3f", range=[0.2, 0.42], row=1, col=2)
car = H["phi_career"]
ok = H["pos_count_2026"] == 4 and all(pl[f"L|{y}"]["woba"] > pl[f"R|{y}"]["woba"] for y in GOV) and pl["R|base"]["woba"] < H["rhb_platoon_woba"]["R"]
base(fig, "Five seasons, five positions, one job: hit left-handers",
     f"Phillies 2022-26: {car['pa']} PA, {f3(car['ba'])}/{f3(car['obp'])}/{f3(car['slg'])}, {car['hr']} HR, wOBA {f3(car['woba'])} - {ordn(H['tenure_board']['woba_rank'])} of "
     f"{H['tenure_board']['n']} Phillies with ≥800 PA. Left: games at each position (a late move counts both; B-Ref carry-in beside it in the report). Right: "
     f"vs LHP {f3(pl['L|base']['woba'])} in 2023-25, vs RHP {f3(pl['R|base']['woba'])}; dotted = all Phillies RHB 2022-26 by hand.", h=580, w=1180)
ship(fig, "f8_tenure_platoon", ok, dict(source=["games_by_position", "platoon_by_season", "phi_2022_26_tenure_board"]))

# F9 - walkaway ladder (carry-ins + WA-1) -------------------------------------------------------------------------
wa = H["wa1"]
rows = [(f"Sosa {y} salary", v, GRAY) for y, v in wa["salary"].items()] + \
       [(f"{c['player']} ({c['team']}, {c['years']}y)", c["aav"], NAVY) for c in sorted(wa["comps"], key=lambda c: c["aav"])]
fig = go.Figure()
fig.add_vrect(x0=wa["floor"], x1=wa["ceiling"], fillcolor="rgba(232,24,40,0.08)", line_width=0)
fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h", marker_color=[r[2] for r in rows], showlegend=False,
                     text=[f"${r[1]:.1f}M" for r in rows], textposition="outside", hovertemplate="%{y}: $%{x:.2f}M<extra></extra>"))
fig.add_vline(x=wa["ceiling"], line=dict(color=RED, width=3))
fig.add_annotation(x=wa["ceiling"], y=1.04, yref="paper", text=f"<b>Walkaway ${wa['ceiling']:.1f}M / yr, {wa['term']}</b>", showarrow=False,
                   xanchor="left", xshift=6, font=dict(color=RED, size=13))
fig.add_annotation(x=wa["floor"], y=1.04, yref="paper", text=f"band floor &#36;{wa['floor']:.1f}M (2026 salary)", showarrow=False, xanchor="right", xshift=-6, font=dict(color=MUTED, size=11))
fig.update_xaxes(title_text="$M per year (AAV)", range=[0, 8.2])
fig.update_yaxes(autorange="reversed")
ok = wa["df_count"] == 0 and wa["years"] == 2 and wa["ceiling"] == 6.0
base(fig, f"The walkaway: ${wa['ceiling']:.1f}M a year, no more than {wa['years']} years",
     (f"Gray: his arbitration salaries 2022-26 (carry-in CI-3). Navy: 2025-26 offseason utility deals, AAV (CI-5). Shaded: the WA-1 band from his 2026 salary to the top comp "
     f"(${wa['comp_max_aav']:.1f}M, rounded down to $0.5M). Term: {wa['df_count']} of 6 decline flags tripped, so up to 2 years. An offer above this line is everyday-player money; "
     f"let it go. Carry-in arithmetic, not a valuation model.").replace("$", "&#36;"), h=560, w=1050)
ship(fig, "f9_walkaway", ok, dict(source=["wa1_comps", "wa1_decline_flags"]))

pd.DataFrame(BRAND).to_csv(OUT / f"{K.P}brand_checks.csv", index=False)
(OUT / f"{K.P}figure_specs.json").write_text(json.dumps(SPECS, indent=1), encoding="utf-8")
print(f"{len(SPECS)} figures shipped; brand checks all pass")
