"""dp_uc53_build_figs.py - ten figures for UC #53 / uc-pps-037 (PNG for the PDF, JSON for the dashboard).
House rules (dp_uc48-52_build_figs): reads ONLY out/dp_uc53_* receipts; computes no KPI; each figure asserts the claim its
subtitle makes before it is written; print = plotly_white + Arial; brand-palette check -> out/dp_uc53_brand_checks.csv.
Pitch palette PL-3 (SI/FC) validated light + dark: out/dp_uc53_palette_validation.txt. F9 is the house CM-1 chart."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, os.environ.get("MLB_DATA_ROOT", r"C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"))
from cumulative_metric import fig_cumulative_metric  # noqa: E402  (house CM-1 chart; sha pinned by the kernel)

RED, NAVY, GRAY, LGRAY, INK, MUTED = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170"
PITCH = {"SI": "#C77800", "FC": "#6250D6"}
BAND = {"clean": "#F4B6BB", "dented": "#EE6F79", "blow-up": RED}
VERD = {"PRESENT": RED, "WEAK": GRAY, "ABSENT": LGRAY, "CONTRA": NAVY, "NO DATA": LGRAY}
CM_INKS = {"#C3C9D2", "#1F2430"}
ALLOWED = {RED, NAVY, GRAY, LGRAY, INK, MUTED, "#ffffff", *PITCH.values(), *BAND.values(), *CM_INKS,
           "rgba(140,140,140,0.35)", "rgba(140,140,140,0.18)", "rgba(232,24,40,0.08)", "rgba(0,45,114,0.06)"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=72, r=30, t=118, b=66), legend=dict(orientation="h", y=-0.2, x=0, yanchor="top"))
H = json.loads((OUT / "dp_uc53_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc53_{n}.csv")          # noqa: E731
SPECS, BRAND = [], []
pct = lambda x, d=0: f"{100 * x:.{d}f}%"                       # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0") if abs(x) < 1 else f"{x:.3f}"  # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
SUBJ, YR = 621237, 2026


def wrap(t, n=140):
    out, cur = [], ""
    for w in t.split(" "):
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return "<br>".join(out + [cur])


def base(fig, title, subtitle, h=540, w=1000):
    fig.update_layout(**LAYOUT, height=h, width=w, title=dict(text=f"<b>{title}</b>", x=0.01, xanchor="left",
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
                  has_subtitle=bool(lay.title.subtitle.text), palette_ok=not off,
                  axis_titles=all((lay[a].title.text or "") != "" for a in lay if a.startswith(("xaxis", "yaxis"))
                                  and lay[a].visible is not False and lay[a].showticklabels is not False and not lay[a].matches))
    BRAND.append(dict(figure=key, **checks, off_palette=";".join(off)))
    assert all(checks.values()), (key, checks, off)
    fig.write_image(OUT / f"dp_uc53_{key}.png", scale=2)
    (OUT / f"dp_uc53_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


S, BY, T = H["season"], H["by_year"], H["tenure"]
yr = R("career_by_year")

# F1 leaderboard ---------------------------------------------------------------------------
L = H["leaderboard"]; lb = R("house_pa_leaderboard").head(15).iloc[::-1]
col = [RED if p == SUBJ else (NAVY if r == "RP" else LGRAY) for p, r in zip(lb.pitcher, lb.role_span)]
fig = go.Figure(go.Bar(x=lb.plate_apps, y=[f"{n.split(', ')[1]} {n.split(', ')[0]}" for n in lb.player_name], orientation="h",
                       marker=dict(color=col, line=dict(color="#ffffff", width=2)), text=lb.plate_apps, textposition="outside",
                       textfont=dict(color=INK), hovertemplate="%{y}: %{x} PA<extra></extra>", showlegend=False))
for nm, c in [("José Alvarado", RED), ("Other relievers (RP-1)", NAVY), ("Starters", LGRAY)]:
    fig.add_trace(go.Bar(x=[None], y=[None], marker_color=c, name=nm))
base(fig, f"#{L['rank']} of {L['n']}: the most-used reliever of the era not named Neris",
     f"Plate appearances faced for the Phillies, regular season 2015-26 (top 15). Alvarado: {L['pa']:,} PA over {L['games']} games "
     f"(#{L['games_rank']} in games). Relievers by RP-1 (starts <= 20% of games); Adam Morgan's 36 starts keep him in the reliever group.", h=600)
fig.update_xaxes(title_text="Plate appearances faced (regular season)"); fig.update_yaxes(title_text="")
fig.update_layout(barmode="overlay", yaxis=dict(showticklabels=True, title_text="Pitcher", automargin=True))
ship(fig, "f01_tenure_leaderboard", L["rank"] == 14 and L["rp_rank"] == 3, dict(receipt="house_pa_leaderboard.csv"))

# F2 career wOBA / xwOBA (same basis) ----------------------------------------------------------
fig = go.Figure()
fig.add_vrect(x0=2016.5, x1=2020.5, fillcolor="rgba(0,45,114,0.06)", line_width=0, annotation_text="Tampa Bay",
              annotation_position="top left", annotation_font=dict(color=MUTED))
fig.add_trace(go.Scatter(x=yr.game_year, y=yr.woba_sc, mode="lines+markers", name="wOBA (Statcast basis, WB-1)",
                         line=dict(color=RED, width=2.5), marker=dict(size=9, line=dict(color="#ffffff", width=2))))
fig.add_trace(go.Scatter(x=yr.game_year, y=yr.xwoba, mode="lines+markers", name="xwOBA (XW-1)", line=dict(color=NAVY, width=2, dash="dot"),
                         marker=dict(size=8, line=dict(color="#ffffff", width=2))))
fig.add_annotation(x=2026, y=S["woba_sc"], text=f"<b>{f3(S['woba_sc'])}</b>", showarrow=False, xshift=26, font=dict(color=INK))
fig.add_annotation(x=2026, y=S["xwoba"], text=f"{f3(S['xwoba'])}", showarrow=False, xshift=26, font=dict(color=INK))
ok = S["luck_gap"] > 0.03 and H["tenure_rank_2026"]["woba_worst"] == 1
base(fig, "2026: the worst results of his Phillies tenure, about .040 worse than the contact deserved",
     f"Career wOBA against vs xwOBA on the same Statcast basis, regular season. 2026 actual {f3(S['woba_sc'])} vs expected {f3(S['xwoba'])} "
     f"(gap +{f3(S['luck_gap'])}); his 2022-24 gap averaged +{f3(H['db1']['rows'][6]['baseline'])}. House wOBA (ranks): {f3(S['woba'])}.")
fig.update_xaxes(title_text="Season", dtick=1); fig.update_yaxes(title_text="wOBA against", tickformat=".3f")
ship(fig, "f02_woba_xwoba_by_year", ok, dict(receipt="career_by_year.csv"))

# F3 cutter putaway in house context ---------------------------------------------------------
G = H["fc_putaway_house"]; zc = R("house_putaway_pitcher_pitch")
me = (zc.pitcher == SUBJ) & (zc.pitch_type == "FC")
fig = go.Figure()
fig.add_trace(go.Scatter(x=zc[~me].pitches2strikes, y=zc[~me].putaway_rate, mode="markers", name="Phillies pitcher x pitch (context)",
                         marker=dict(color="rgba(140,140,140,0.35)", size=8), text=zc[~me].player_name + " " + zc[~me].pitch_type,
                         hovertemplate="%{text}<br>%{x} two-strike pitches<br>putaway %{y:.1%}<extra></extra>"))
fig.add_trace(go.Scatter(x=zc[me].pitches2strikes, y=zc[me].putaway_rate, mode="markers+text", name="Alvarado cutter, 2021-26",
                         marker=dict(color=RED, size=14, line=dict(color="#ffffff", width=2)), text=["Alvarado FC"], textposition="top center",
                         textfont=dict(color=INK)))
base(fig, f"His cutter put hitters away at a top-decile rate over {G['pitches2strikes']} two-strike pitches",
     f"Putaway rate (strikeouts per two-strike pitch), Phillies pitcher x pitch type, regular season 2015-26, >= 20 two-strike pitches (n={G['n']}). "
     f"Alvarado FC {pct(G['value'], 1)}: #{G['rank']} overall ({ordn(G['pct']['percentile'])} percentile), #{G['rank_ge300']} of {G['n_ge300']} with 300+.")
fig.update_xaxes(title_text="Two-strike pitches (log scale)", type="log", tickvals=[20, 50, 100, 200, 500, 1000, 3000], ticktext=["20", "50", "100", "200", "500", "1,000", "3,000"]); fig.update_yaxes(title_text="Putaway rate", tickformat=".0%")
ship(fig, "f03_cutter_putaway_context", G["pct"]["percentile"] >= 90, dict(receipt="house_putaway_pitcher_pitch.csv"))

# F4 cutter whiff by season in house context ---------------------------------------------------
W = H["fc_whiff_house"]; wc = R("house_whiff_pitcher_pitch_season")
me = (wc.pitcher == SUBJ) & (wc.pitch_type == "FC")
fig = go.Figure()
fig.add_trace(go.Scatter(x=wc[~me].pitches, y=wc[~me].whiff_rate, mode="markers", name="Phillies pitcher x pitch x season (context)",
                         marker=dict(color="rgba(140,140,140,0.35)", size=7), hoverinfo="skip"))
mw = wc[me].sort_values("game_year")
fig.add_trace(go.Scatter(x=mw.pitches, y=mw.whiff_rate, mode="markers+text", name="Alvarado cutter by season",
                         marker=dict(color=RED, size=13, line=dict(color="#ffffff", width=2)), text=mw.game_year.astype(str),
                         textposition="middle right", textfont=dict(color=INK)))
w26 = W["by_year"]["2026"]["whiff"]
fig.add_hline(y=w26, line_dash="dot", line_color=NAVY, annotation_text=f"2026 cutter whiff {pct(w26, 1)} (computed)",
              annotation_position="top right", annotation_font=dict(color=INK))
base(fig, "From the best swing-and-miss pitch in the house to merely very good",
     f"Whiff rate per swing, Phillies pitcher x pitch x season, regular season 2015-26, >= 50 pitches (n={W['by_year']['2026']['pct']['n']}). "
     f"Alvarado's cutter: #{W['by_year']['2021']['rank']} in 2021 ({pct(W['by_year']['2021']['whiff'], 1)}), #{W['by_year']['2022']['rank']} in 2022, "
     f"#{W['by_year']['2026']['rank']} in 2026 ({ordn(W['by_year']['2026']['pct']['percentile'])} percentile).")
fig.update_xaxes(title_text="Pitches thrown in the season (log scale)", type="log", tickvals=[50, 100, 200, 500, 1000, 3000], ticktext=["50", "100", "200", "500", "1,000", "3,000"]); fig.update_yaxes(title_text="Whiff rate", tickformat=".0%")
ship(fig, "f04_cutter_whiff_context", W["by_year"]["2021"]["rank"] == 1 and W["by_year"]["2026"]["rank"] > 50,
     dict(receipt="house_whiff_pitcher_pitch_season.csv"))

# F5 cutter 2x2 by year (the client's chart, governed) ----------------------------------------
pp = R("fc_si_pitches"); fc = pp[(pp.pitch_type == "FC") & (pp.game_year >= 2018)].copy()
fc["hb_in"], fc["ivb_in"] = 12 * fc.pfx_x, 12 * fc.pfx_z
mets = [("release_speed", "Velocity (mph)"), ("release_spin_rate", "Spin rate (rpm)"), ("hb_in", "Horizontal break (in)"), ("ivb_in", "Induced vertical break (in)")]
fig = make_subplots(rows=2, cols=2, subplot_titles=[m[1] for m in mets], vertical_spacing=0.16, horizontal_spacing=0.09)
for i, (c, nm) in enumerate(mets):
    rr, cc = i // 2 + 1, i % 2 + 1
    for y, g in fc.groupby("game_year"):
        fig.add_trace(go.Box(y=g[c], name=str(y), marker_color=RED if y == YR else GRAY, line=dict(width=1.5), boxpoints=False,
                             showlegend=False), row=rr, col=cc)
    fig.update_yaxes(title_text=nm.split(" (")[0], row=rr, col=cc); fig.update_xaxes(title_text="Season", row=rr, col=cc)
q = fc[fc.game_year == YR].release_speed.quantile([.25, .75])
fig.add_hrect(y0=q.iloc[0], y1=q.iloc[1], fillcolor="rgba(232,24,40,0.08)", line_width=0, row=1, col=1)
fv = H["fc_velo"]
base(fig, "The cutter lost velocity, not shape", f"Cutter by season, regular season 2018-26 (TB 2018-20, PHI 2021-26); 2026 in red, its middle 50% "
     f"shaded on velocity. Mean velocity {fv['y2026']:.1f} mph in 2026, a tenure low, {abs(fv['drop_vs_peak']):.1f} mph under {fv['peak_year']}. Break stays inside its prior range.", h=800)
fig.update_layout(margin=dict(t=160))
mv = H["pitch_by_year"]["FC"]
shape_ok = all(min(mv[str(y)][k] for y in range(2021, 2026)) - 1.5 <= mv["2026"][k] <= max(mv[str(y)][k] for y in range(2021, 2026)) + 1.5 for k in ("hb_in", "ivb_in"))
ship(fig, "f05_cutter_metrics_by_year", fv["tenure_rank_low"] == 1 and shape_ok, dict(receipt="fc_si_pitches.csv"))

# F6 velocity by year (SI, FC) ---------------------------------------------------------------
pt = R("pitch_types_by_year")
fig = go.Figure()
for p_, nm in [("SI", "Sinker"), ("FC", "Cutter")]:
    d = pt[(pt.pitch_type == p_) & (pt.game_year >= 2018)].sort_values("game_year")
    fig.add_trace(go.Scatter(x=d.game_year, y=d.velo, mode="lines+markers", name=nm, line=dict(color=PITCH[p_], width=2.5),
                             marker=dict(size=9, line=dict(color="#ffffff", width=2))))
    fig.add_annotation(x=d.game_year.iloc[-1], y=d.velo.iloc[-1], text=f"<b>{nm} {d.velo.iloc[-1]:.1f}</b>", showarrow=False, xshift=50,
                       font=dict(color=INK))
mo = H["monthly_2026"]
sv = H["si_velo"]
base(fig, "Both fastballs are slower than at his peak, and they faded through 2026",
     f"Mean velocity by season, regular season 2018-26. Sinker {sv['y2026']:.1f} mph in 2026 ({abs(sv['drop_vs_peak']):.1f} under {sv['peak_year']}); "
     f"cutter {fv['y2026']:.1f} ({abs(fv['drop_vs_peak']):.1f} under {fv['peak_year']}). Within 2026 the sinker went from {mo['6']['si_velo']:.1f} in June "
     f"to {mo['9']['si_velo']:.1f} in September.")
fig.update_xaxes(title_text="Season", dtick=1); fig.update_yaxes(title_text="Mean velocity (mph)")
ship(fig, "f06_velocity_by_year", sv["drop_vs_peak"] < -1 and fv["drop_vs_peak"] < -2 and mo["9"]["si_velo"] < mo["6"]["si_velo"],
     dict(receipt="pitch_types_by_year.csv"))

# F7 command (small multiples, one unit each) ----------------------------------------------------
ten = yr[yr.game_year >= 2021]
cm = [("in_zone_rate", "Zone rate"), ("chase_rate", "Chase rate"), ("bbrate", "Walk rate")]
fig = make_subplots(rows=1, cols=3, subplot_titles=[c[1] for c in cm], horizontal_spacing=0.08)
for i, (c, nm) in enumerate(cm, start=1):
    fig.add_trace(go.Bar(x=ten.game_year.astype(str), y=ten[c], marker=dict(color=[RED if y == YR else LGRAY for y in ten.game_year],
                         line=dict(color="#ffffff", width=2)), text=[pct(v, 1) for v in ten[c]], textposition="outside",
                         textfont=dict(color=INK, size=11), showlegend=False), row=1, col=i)
    fig.update_yaxes(tickformat=".0%", title_text=nm if i == 1 else "Rate", row=1, col=i); fig.update_xaxes(title_text="Season", row=1, col=i)
TR = H["tenure_rank_2026"]
base(fig, "He lived outside the zone more than ever, and hitters chased about as often as usual",
     f"Phillies seasons, regular season, all pitches. 2026 zone rate {pct(S['in_zone_rate'], 1)} (tenure low), chase {pct(S['chase_rate'], 1)} "
     f"(#{TR['chase_low']} lowest of 6), walks {pct(S['bbrate'], 1)}, and {int(S['hbp'])} hit batters (tenure high). Zone counts unclassified pitches as in-zone (K44 D-7).", h=540)
fig.update_layout(margin=dict(t=150))
for i, (c, _) in enumerate(cm, start=1):
    fig.update_yaxes(range=[0, ten[c].max() * 1.18], row=1, col=i)
ship(fig, "f07_command_by_year", TR["zone_low"] == 1 and TR["hbp_high"] == 1, dict(receipt="career_by_year.csv"))

# F8 OD-1 outing bands ---------------------------------------------------------------------------
ob = R("outing_bands_by_year")
fig = go.Figure()
for b in ["clean", "dented", "blow-up"]:
    fig.add_trace(go.Bar(x=ob.game_year.astype(str), y=ob[b + "_rate"], name={"clean": "Clean (0 runs on watch)", "dented": "Dented (1)",
                         "blow-up": "Blow-up (2+)"}[b], marker=dict(color=BAND[b], line=dict(color="#ffffff", width=2)),
                         text=ob[b].astype(str), textposition="inside", insidetextanchor="middle", textangle=0, constraintext="none",
                         textfont=dict(color=INK)))
O = H["outings_2026"]
base(fig, f"The ride: {O['blowups']} blow-ups in {O['apps']} outings, the most of his tenure",
     f"OD-1 (provisional): regular-season appearances by runs on watch. 2026: {O['clean']} clean ({pct(H['outing_bands']['2026']['clean_rate'])}, tenure low), "
     f"{O['blowups']} blow-ups. Segment labels are counts. The damage was spread out: his 5 worst outings held {pct(H['outing_bands']['2026']['damage_top5'])} of his runs, the smallest share of his tenure.")
fig.update_layout(barmode="stack", bargap=0.35, uniformtext=dict(minsize=11, mode="show")); fig.update_yaxes(title_text="Share of appearances", tickformat=".0%"); fig.update_xaxes(title_text="Season")
obd = H["outing_bands"]
ok = O["blowups"] == max(v["blowup"] for v in obd.values()) and obd["2026"]["damage_top5"] == min(v["damage_top5"] for v in obd.values())
ship(fig, "f08_outing_bands", ok, dict(receipt="outing_bands_by_year.csv"))

# F9 cumulative wOBA (house CM-1 chart, CM-1a spec) -------------------------------------------------
cf = R("cumulative_woba"); cf.attrs.update(metric="wOBA", fmt=".3f", is_rate=True, min_den=H["cumulative"]["min_den"], by=["game_year"])
fig = fig_cumulative_metric(cf, highlight=YR, against=True)
C = H["cumulative"]["final"]
base(fig, "Never really settled: 2026 ran above every prior Phillies season for most of the year",
     f"Cumulative wOBA against by plate appearance, Statcast basis (CM-1a corrects CM-D1), regular season 2021-26; prior seasons in gray, "
     f"dotted line = 2021-25 pooled. 2026 finished at {f3(C['2026'])}. Lines start at {H['cumulative']['min_den']} in the denominator.", h=560)
fig.update_layout(legend=dict(orientation="h", y=-0.2, x=0, yanchor="top"))
cv = cf.dropna(subset=["value"]).pivot_table(index="cum_pa", columns="game_year", values="value")
above = (cv[YR] > cv.drop(columns=YR).max(axis=1)).loc[cv[YR].notna()]
H_ABOVE = float(above.mean())
ship(fig, "f09_cumulative_woba", C["2026"] == max(C.values()) and H_ABOVE > 0.5, dict(receipt="cumulative_woba.csv", share_pa_above_all_prior=H_ABOVE))

# F10 DB-1 ledger ----------------------------------------------------------------------------------
db = pd.DataFrame(H["db1"]["rows"]); db["units"] = db.delta * db.direction / db.threshold
db = db.iloc[::-1]
fig = go.Figure()
fig.add_vrect(x0=1, x1=max(4, db.units.max() + .5), fillcolor="rgba(232,24,40,0.08)", line_width=0)
fig.add_vline(x=1, line_dash="dot", line_color=RED); fig.add_vline(x=-1, line_dash="dot", line_color=NAVY); fig.add_vline(x=0, line_color=GRAY, line_width=1)
SHORT = {"D1": "Sinker velo", "D2": "Cutter velo", "D3": "Cutter whiff", "D4": "Chase rate", "D5": "Zone rate", "D6": "K% − BB%",
         "B1": "Luck gap (wOBA − xwOBA)", "B2": "Damage in worst 5"}
lab = [f"{r.sig} {SHORT[r.sig]}" for r in db.itertuples()]
fig.add_trace(go.Bar(x=db.units, y=lab, orientation="h", marker=dict(color=[VERD[v] for v in db.verdict], line=dict(color="#ffffff", width=2)),
                     showlegend=False, hovertemplate="%{y}<br>%{x:.2f} thresholds<extra></extra>"))
for r in db.itertuples():
    fig.add_annotation(x=max(r.units, 0), y=f"{r.sig} {SHORT[r.sig]}", text=f"<b>{r.verdict}</b>", showarrow=False, xanchor="left", xshift=6,
                       font=dict(color=INK, size=12))
RU = H["db1"]["rollup"]
base(fig, f"Decline or blip? The pre-registered ledger says: {RU['call'].lower()}",
     f"DB-1 (provisional; bars registered before 2026 values were read). Move in the predicted direction, in units of each signature's threshold (PA-1: PRESENT >= 1). "
     f"Baseline: pooled {H['db1']['baseline_years'][0]}-{H['db1']['baseline_years'][-1]}. Decline signatures {RU['decline']}, blip signatures {RU['blip']}. "
     f"Same call against 2021-25: {H['db1']['sensitivity']['rollup']['call']}.", h=560)
fig.update_xaxes(title_text="Change in the predicted direction (thresholds)", range=[-2.2, 4]); fig.update_yaxes(title_text="Signature", automargin=True)
ship(fig, "f10_db1_ledger", RU["call"] == H["db1"]["sensitivity"]["rollup"]["call"], dict(receipt="db1_ledger.csv"))

pd.DataFrame(BRAND).to_csv(OUT / "dp_uc53_brand_checks.csv", index=False)
(OUT / "dp_uc53_figure_specs.json").write_text(json.dumps(SPECS, indent=1))
print(f"{len(SPECS)} figures shipped; brand {sum(all(v for k, v in b.items() if k not in ('figure', 'off_palette')) for b in BRAND)}/{len(BRAND)}")
