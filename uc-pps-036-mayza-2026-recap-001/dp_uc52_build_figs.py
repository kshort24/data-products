"""dp_uc52_build_figs.py — ten figures for UC #52 / uc-pps-036 (PNG for the PDF, JSON for the dashboard).
Rules (house, as in dp_uc48/49/51_build_figs): reads ONLY out/dp_uc52_* receipts; computes no KPI; each figure
asserts the claim its title/subtitle makes before it is written; print = plotly_white + Arial; brand-palette check.
PL-3 pitch palette validated light + dark (out/dp_uc52_palette_validation.txt)."""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC52_OUT", HERE / "out"))
RED, NAVY, GRAY, LGRAY, INK, MUTED = "#E81828", "#002D72", "#8C8C8C", "#D9D9D9", "#1b1b1b", "#5b6170"
PITCH = {"SI": "#C77800", "SL": "#6250D6", "FF": "#D22D49", "FS": "#3B6FD8"}
PNAME = {"SI": "Sinker", "SL": "Slider", "FF": "Four-Seam", "FS": "Splitter"}
STAND = {"L": "#3B6FD8", "R": "#D22D49"}
ALLOWED = {RED, NAVY, GRAY, LGRAY, INK, MUTED, "#ffffff", *PITCH.values(), *STAND.values(),
           "rgba(140,140,140,0.35)", "rgba(140,140,140,0.18)", "rgba(232,24,40,0.08)", "rgba(98,80,214,0.10)"}
LAYOUT = dict(template="plotly_white", font=dict(family="Arial", size=13, color=INK),
              margin=dict(l=72, r=30, t=118, b=66), legend=dict(orientation="h", y=-0.2, x=0, yanchor="top"))
H = json.loads((OUT / "dp_uc52_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc52_{n}.csv")          # noqa: E731
SPECS, BRAND = [], []
pct = lambda x, d=0: f"{100 * x:.{d}f}%"                       # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0") if abs(x) < 1 else f"{x:.3f}"  # noqa: E731
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
SUBJ, YR = 641835, 2026


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
                if k in ("color", "fillcolor", "bgcolor") and isinstance(v, str): found.add(v)
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
    fig.write_image(OUT / f"dp_uc52_{key}.png", scale=2)
    (OUT / f"dp_uc52_{key}.json").write_text(fig.to_json())
    SPECS.append(dict(figure=key, title=lay.title.text.replace("<b>", "").replace("</b>", ""),
                      subtitle=lay.title.subtitle.text.replace("<br>", " "), **meta))


S, CR = H["season"], H["career_rank"]
car = R("career"); yrs = car.game_year.astype(str).tolist()

# F1 career wOBA / xwOBA -----------------------------------------------------------------
ok = CR["woba_sc_low"] == 4 and CR["xwoba_low"] == 5 and CR["woba_low"] == 3 and S["xwoba"] < S["woba_sc"]
fig = go.Figure()
fig.add_trace(go.Scatter(x=car.game_year.tolist(), y=car.woba_sc.tolist(), mode="lines+markers", name="wOBA allowed (Statcast basis)", line=dict(color=RED, width=2), marker=dict(size=9),
                         customdata=car[["plate_apps"]], hovertemplate="%{x} · wOBA %{y:.3f} · %{customdata[0]} PA<extra></extra>"))
fig.add_trace(go.Scatter(x=car.game_year.tolist(), y=car.xwoba.tolist(), mode="lines+markers", name="xwOBA allowed", line=dict(color=NAVY, width=2, dash="dot"),
                         marker=dict(size=8, symbol="diamond"), hovertemplate="%{x} · xwOBA %{y:.3f}<extra></extra>"))
for nm, col, y, ys in [("wOBA", RED, S["woba_sc"], 9), ("xwOBA", NAVY, S["xwoba"], -9)]:
    fig.add_annotation(x=2026, y=y, text=f"{nm} {f3(y)}", showarrow=False, xanchor="left", xshift=10, yshift=ys, font=dict(color=INK, size=12))
small = [str(y) for y in H["career_prior"]["small_seasons"]]
fig.update_xaxes(title_text="Season (regular season; no 2020 rows)", tickvals=car.game_year.tolist(), range=[2016.5, 2026.9]); fig.update_yaxes(title_text="wOBA / xwOBA allowed", tickformat=".3f")
base(fig, "One of his best seasons, and the expected number is better still",
     f"Same basis (Statcast weights): 2026 wOBA {f3(S['woba_sc'])} ({ordn(CR['woba_sc_low'])}-best of {CR['n_seasons']}), xwOBA {f3(S['xwoba'])} ({ordn(CR['xwoba_low'])}-best). "
     f"On the house basis his {f3(S['woba'])} ranks {ordn(CR['woba_low'])}. "
     f"Small seasons: {', '.join(small)} (<400 pitches). Sources: Statcast via the house logs; 2017-25 from his own pitcher file.")
ship(fig, "f01_career_woba", ok, dict(section="2 Results", asserts="woba_sc_low==4, xwoba_low==5, woba_low==3, xwoba<woba_sc"))

# F2 contact quality by year ---------------------------------------------------------------
ok = CR["hh_high"] == 2 and CR["barrel_low"] == 6
fig = make_subplots(rows=1, cols=2, subplot_titles=("Hard-hit rate (95+ mph)", "Barrel rate"), horizontal_spacing=0.1)
for i, c in enumerate(["hard_hit_rate", "barrel_rate"], 1):
    cols = [RED if y == "2026" else LGRAY for y in yrs]
    fig.add_trace(go.Bar(x=yrs, y=car[c], marker=dict(color=cols), showlegend=False,
                         hovertemplate="%{x} · %{y:.1%}<extra></extra>"), row=1, col=i)
    fig.update_yaxes(title_text="Share of batted balls", tickformat=".0%", row=1, col=i)
    fig.update_xaxes(title_text="Season", row=1, col=i)
base(fig, "Contact got louder: second-highest hard-hit rate of his career",
     f"2026 hard-hit {pct(S['hard_hit_rate'], 1)} (only his 2017 rookie year was higher); barrel rate {pct(S['barrel_rate'], 1)}, "
     f"{ordn(CR['barrel_low'])} lowest of {CR['n_seasons']}. Average launch angle {S['la_mu']:.1f}°, up from 2021-23.")
ship(fig, "f02_contact_by_year", ok, dict(section="3 Contact", asserts="hh_high==2, barrel_low==6"))

# F3 barrel -> wOBA, house LHP ------------------------------------------------------------
B = H["barrel_context"]; bw = R("house_lhp_barrel_woba")
ok = B["resid"] < 0 and B["n"] >= 30 and S["xwoba"] < S["woba_sc"]
o = bw[~((bw.pitcher == SUBJ) & (bw.game_year == YR))]; m = bw[(bw.pitcher == SUBJ) & (bw.game_year == YR)]
fig = go.Figure()
fig.add_trace(go.Scatter(x=o.barrel_rate, y=o.woba, mode="markers", name="Phillies LHP seasons (100+ PA)",
                         marker=dict(color="rgba(140,140,140,0.35)", size=9, line=dict(color="#ffffff", width=1)),
                         customdata=o[["player_name", "game_year", "plate_apps"]],
                         hovertemplate="%{customdata[0]} %{customdata[1]}<br>barrel %{x:.1%} · wOBA %{y:.3f} · %{customdata[2]} PA<extra></extra>"))
xs = np.linspace(bw.barrel_rate.min(), bw.barrel_rate.max(), 20)
fig.add_trace(go.Scatter(x=xs, y=B["intercept"] + B["slope"] * xs, mode="lines", name="Least-squares line", line=dict(color=GRAY, width=2, dash="dash"), hoverinfo="skip"))
fig.add_trace(go.Scatter(x=m.barrel_rate, y=m.woba, mode="markers+text", name="Mayza 2026", text=["Mayza 2026"], textposition="top center",
                         textfont=dict(color=INK), marker=dict(color=RED, size=14, line=dict(color="#ffffff", width=2)),
                         hovertemplate="Mayza 2026<br>barrel %{x:.1%} · wOBA %{y:.3f}<extra></extra>"))
fig.update_xaxes(title_text="Barrel rate allowed", tickformat=".0%"); fig.update_yaxes(title_text="wOBA allowed", tickformat=".3f")
base(fig, f"On barrels alone he 'should' have allowed {f3(B['woba_fit'])}; he allowed {f3(B['woba'])}",
     f"{B['n']} Phillies LHP pitcher-seasons, 2015-26, 100+ PA, house wOBA basis (r = {B['r']:.2f}: barrels alone explain little). xwOBA, which also prices "
     f"strikeouts and walks, expects {f3(S['xwoba'])} against his {f3(S['woba_sc'])} on Statcast's basis: he was not lucky.")
ship(fig, "f03_barrel_woba_house", ok, dict(section="3 Contact", asserts="barrel_context.resid<0, n>=30"))

# F4 pitch map by batter side ---------------------------------------------------------------
wp = R("weapons_2026"); wp = wp[wp.pitches >= 10]
ok = H["weapons"]["SI_vs_L"]["usage"] > 0.5 and H["weapons"]["SI_vs_R"]["usage"] > 0.5
fig = make_subplots(rows=1, cols=2, subplot_titles=("vs left-handed batters", "vs right-handed batters"), shared_yaxes=True)
for i, st in enumerate(["L", "R"], 1):
    for pt in ["SI", "SL", "FF", "FS"]:
        r = wp[(wp.stand == st) & (wp.pitch_type == pt)]
        if r.empty: continue
        r = r.iloc[0]
        fig.add_trace(go.Scatter(x=[r.plate_x], y=[r.plate_z], mode="markers+text", text=[pt], textposition="middle center",
                                 textfont=dict(color="#ffffff", size=11), name=PNAME[pt], legendgroup=pt, showlegend=(i == 1),
                                 marker=dict(color=PITCH[pt], size=18 + 60 * r.usage, line=dict(color="#ffffff", width=2)),
                                 hovertemplate=f"{PNAME[pt]} vs {st}HB<br>usage {r.usage:.0%} · in zone {r.in_zone_rate:.0%}<extra></extra>"), row=1, col=i)
    fig.add_shape(type="rect", x0=-0.83, x1=0.83, y0=1.6, y1=3.4, line=dict(color=GRAY, width=1), fillcolor="rgba(140,140,140,0.18)", row=1, col=i)
    fig.update_xaxes(title_text="Plate side (ft, catcher view)", range=[-1.9, 1.9], row=1, col=i)
fig.update_yaxes(title_text="Plate height (ft)", range=[0.6, 3.8], row=1, col=1)
fig.update_yaxes(range=[0.6, 3.8], row=1, col=2)
base(fig, "Sinker first to both sides; the slider lives below the zone to righties",
     f"Mean location per pitch, sized by usage. Sinker {pct(H['weapons']['SI_vs_L']['usage'])} of pitches to LHB and {pct(H['weapons']['SI_vs_R']['usage'])} to RHB, "
     f"in the zone {pct(H['si_zone']['L']['in_zone'])}/{pct(H['si_zone']['R']['in_zone'])} of the time. Shaded box: average rulebook zone.", h=560)
ship(fig, "f04_pitch_map", ok, dict(section="4 Platoon", asserts="SI usage > 50% vs both sides"))

# F5 arsenal movement ---------------------------------------------------------------------
A = H["arsenal"]; ok = H["bullet_slider"]["bullet"] and A["SI"]["usage"] > 0.5
fig = go.Figure()
for pt in ["SI", "SL", "FF", "FS"]:
    a = A[pt]
    fig.add_trace(go.Scatter(x=[a["hb_in"]], y=[a["ivb_in"]], mode="markers+text", name=f"{PNAME[pt]} ({pct(a['usage'])})",
                             text=[f"{pt} {a['velo']:.1f}"], textposition="bottom center" if pt == "FS" else "top center", textfont=dict(color=INK),
                             marker=dict(color=PITCH[pt], size=14 + 40 * a["usage"], line=dict(color="#ffffff", width=2)),
                             hovertemplate=f"{PNAME[pt]}<br>HB %{{x:.1f}} in · IVB %{{y:.1f}} in<br>{a['velo']:.1f} mph · {a['pitches']} thrown<extra></extra>"))
fig.add_shape(type="rect", x0=-4, x1=4, y0=-4, y1=4, line=dict(color="#6250D6", width=1, dash="dot"), fillcolor="rgba(98,80,214,0.10)")
fig.add_annotation(x=0, y=-4, text="bullet box (BS-1: |HB| and |IVB| ≤ 4 in)", showarrow=False, yshift=-12, font=dict(color=MUTED, size=11))
fig.add_vline(x=0, line=dict(color=LGRAY, width=1)); fig.add_hline(y=0, line=dict(color=LGRAY, width=1))
fig.update_xaxes(title_text="Horizontal break, in (Statcast pfx_x × 12, catcher view)")
fig.update_yaxes(title_text="Induced vertical break, in (pfx_z × 12)", range=[-8, 18])
base(fig, "A sinker that doesn't run much, and a hard slider that barely moves",
     f"2026 averages. Slider {A['SL']['velo']:.1f} mph with {abs(A['SL']['hb_in']):.1f} in of horizontal and {abs(A['SL']['ivb_in']):.1f} in of vertical break: "
     f"a bullet. Sinker {A['SI']['hb_in']:.1f} in of run ({ordn(H['shapes']['SI']['absHB_pct_below'])} percentile of house LHP sinkers). Four-seam IVB "
     f"{A['FF']['ivb_in']:.1f} in ({ordn(H['shapes']['FF']['ivb_pct_below'])} percentile): it doesn't ride.")
ship(fig, "f05_arsenal_movement", ok, dict(section="5 Stuff", asserts="BS-1 bullet true; SI usage>50%"))

# F6 release point + extension vs house LHP ---------------------------------------------
dt = R("delivery_house_lhp"); D = H["delivery"]
ok = D["ext_pct"]["pct_below"] >= 80 and D["rel_z_pct"]["pct_below"] >= 70 and D["rel_x_pct"]["pct_below"] <= 30
o = dt[dt.pitcher != SUBJ]; m = dt[(dt.pitcher == SUBJ) & (dt.game_year == YR)]
fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4], subplot_titles=("Release point", "Extension"), horizontal_spacing=0.12)
fig.add_trace(go.Scatter(x=o.rel_x, y=o.rel_z, mode="markers", name="Phillies LHP seasons (150+ pitches)", marker=dict(color="rgba(140,140,140,0.35)", size=9),
                         customdata=o[["player_name", "game_year"]], hovertemplate="%{customdata[0]} %{customdata[1]}<br>x %{x:.2f} · z %{y:.2f} ft<extra></extra>"), row=1, col=1)
fig.add_trace(go.Scatter(x=m.rel_x, y=m.rel_z, mode="markers+text", name="Mayza 2026", text=["Mayza 2026"], textposition="top center", textfont=dict(color=INK),
                         marker=dict(color=RED, size=14, line=dict(color="#ffffff", width=2)), hovertemplate="Mayza 2026<br>x %{x:.2f} · z %{y:.2f} ft<extra></extra>"), row=1, col=1)
fig.add_trace(go.Box(y=o.ext, name="House LHP", marker=dict(color=GRAY), line=dict(color=GRAY), boxpoints="all", jitter=0.4, pointpos=0,
                     showlegend=False, hovertemplate="%{y:.2f} ft<extra></extra>"), row=1, col=2)
fig.add_trace(go.Scatter(x=["House LHP"], y=m.ext, mode="markers+text", text=[f"Mayza {D['ext']:.2f} ft"], textposition="middle right",
                         textfont=dict(color=INK), marker=dict(color=RED, size=14, symbol="diamond", line=dict(color="#ffffff", width=2)), showlegend=False,
                         hovertemplate="Mayza 2026 · %{y:.2f} ft<extra></extra>"), row=1, col=2)
fig.update_xaxes(title_text="Release side (ft, catcher view)", row=1, col=1); fig.update_yaxes(title_text="Release height (ft)", row=1, col=1)
fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2); fig.update_yaxes(title_text="Extension (ft)", row=1, col=2)
base(fig, "Not 'bang average': higher, tighter to the body, and deeper down the mound",
     f"Release height {ordn(D['rel_z_pct']['pct_below'])} percentile, side {ordn(D['rel_x_pct']['pct_below'])} percentile (narrower than most), extension "
     f"{D['ext']:.2f} ft = {ordn(D['ext_pct']['pct_below'])} percentile of {D['ext_pct']['n']} Phillies LHP seasons, 2015-26. Mound position is not in Statcast.", h=560)
ship(fig, "f06_release_extension", ok, dict(section="5 Stuff", asserts="ext pct>=80, rel_z pct>=70, rel_x pct<=30"))

# F7 slider shapes ---------------------------------------------------------------------------
bs = R("bullet_slider"); BS = H["bullet_slider"]
ok = BS["bullet"] and BS["n_bullet_others"] >= 1
o = bs[bs.pitcher != SUBJ]; m = bs[(bs.pitcher == SUBJ) & (bs.game_year == YR)]
fig = go.Figure()
fig.add_shape(type="rect", x0=-4, x1=4, y0=-4, y1=4, line=dict(color="#6250D6", width=1, dash="dot"), fillcolor="rgba(98,80,214,0.10)")
fig.add_trace(go.Scatter(x=o.hb_in, y=o.ivb_in, mode="markers", name="Phillies LHP slider seasons (50+)", marker=dict(color="rgba(140,140,140,0.35)", size=10),
                         customdata=o[["player_name", "game_year", "velo"]], hovertemplate="%{customdata[0]} %{customdata[1]}<br>HB %{x:.1f} · IVB %{y:.1f} in · %{customdata[2]:.1f} mph<extra></extra>"))
sz = o[o.player_name.str.contains("nchez", na=False)]
fig.add_trace(go.Scatter(x=sz.hb_in, y=sz.ivb_in, mode="markers", name="Sánchez seasons", text=sz.game_year.astype(str),
                         marker=dict(color=NAVY, size=10, symbol="square"),
                         hovertemplate="Sánchez %{text}<br>HB %{x:.1f} · IVB %{y:.1f} in<extra></extra>"))
fig.add_trace(go.Scatter(x=m.hb_in, y=m.ivb_in, mode="markers+text", name="Mayza 2026", text=["Mayza 2026"], textposition="top center", textfont=dict(color=INK),
                         marker=dict(color=RED, size=15, line=dict(color="#ffffff", width=2)), hovertemplate="Mayza 2026<br>HB %{x:.1f} · IVB %{y:.1f} in<extra></extra>"))
fig.update_xaxes(title_text="Slider horizontal break, in (pfx_x × 12)"); fig.update_yaxes(title_text="Slider induced vertical break, in")
base(fig, "Uncommon, not unique: the bullet slider is Cristopher Sánchez's pitch too",
     f"{BS['n_pop']} other Phillies LHP slider seasons (2015-26, 50+ sliders); {BS['n_bullet_others']} sit inside the bullet box with Mayza's. "
     f"His is the harder one: {BS['velo']:.1f} mph ({ordn(H['shapes']['SL']['velo_pct_below'])} percentile for velocity).")
ship(fig, "f07_slider_shapes", ok, dict(section="5 Stuff", asserts="BS-1 bullet and n_bullet_others>=1"))

# F8 weapons: wOBA and whiff by pitch x side --------------------------------------------
W = H["weapons"]
ok = W["SI_vs_L"]["woba"] < W["SL_vs_L"]["woba"] and W["SL_vs_R"]["woba"] < W["SI_vs_R"]["woba"]
fig = make_subplots(rows=1, cols=2, subplot_titles=("wOBA allowed on PAs ending with the pitch", "Whiff rate (whiffs / swings)"), horizontal_spacing=0.1)
for st in ["L", "R"]:
    pts = [p for p in ["SI", "SL", "FF"] if (W.get(f"{p}_vs_{st}") or {}).get("pa", 0) and W[f"{p}_vs_{st}"]["pa"] >= 10]
    lab = "vs LHB" if st == "L" else "vs RHB"
    fig.add_trace(go.Bar(x=[PNAME[p] for p in pts], y=[W[f"{p}_vs_{st}"]["woba"] for p in pts], name=lab, marker=dict(color=STAND[st]),
                         customdata=[[W[f"{p}_vs_{st}"]["pa"]] for p in pts], hovertemplate=f"%{{x}} {lab}<br>wOBA %{{y:.3f}} · %{{customdata[0]}} PA<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Bar(x=[PNAME[p] for p in pts], y=[W[f"{p}_vs_{st}"]["whiff"] for p in pts], name=lab, marker=dict(color=STAND[st]), showlegend=False,
                         hovertemplate=f"%{{x}} {lab}<br>whiff %{{y:.0%}}<extra></extra>"), row=1, col=2)
fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08)
fig.update_yaxes(title_text="wOBA", tickformat=".3f", row=1, col=1); fig.update_yaxes(title_text="Whiff rate", tickformat=".0%", row=1, col=2)
fig.update_xaxes(title_text="Pitch (10+ PA ended)", row=1, col=1); fig.update_xaxes(title_text="Pitch", row=1, col=2)
base(fig, "Two weapons: the sinker against lefties, the slider against righties",
     f"Sinker vs LHB {f3(W['SI_vs_L']['woba'])} wOBA ({W['SI_vs_L']['pa']} PA); slider vs RHB {f3(W['SL_vs_R']['woba'])} with a {pct(W['SL_vs_R']['whiff'])} whiff rate. "
     f"The slider to lefties is the soft spot: {f3(W['SL_vs_L']['woba'])} wOBA, {pct(W['SL_vs_L']['whiff'])} whiffs. Small samples: read direction, not decimals.")
ship(fig, "f08_weapons", ok, dict(section="6 Weapons", asserts="SI<SL vs L and SL<SI vs R on wOBA"))

# F9 quick-AB rate --------------------------------------------------------------------------
qa = R("quick_ab_house"); Q = H["quick_ab"]
ok = Q["rate"] > Q["house_median"]
o = qa[~((qa.pitcher == SUBJ) & (qa.game_year == YR))]; m = qa[(qa.pitcher == SUBJ) & (qa.game_year == YR)]
fig = go.Figure()
fig.add_trace(go.Scatter(x=o.qa_pas, y=o.quick_ab_rate, mode="markers", name="Phillies pitcher-seasons (100+ PA)", marker=dict(color="rgba(140,140,140,0.35)", size=8),
                         customdata=o[["player_name", "game_year", "role"]], hovertemplate="%{customdata[0]} %{customdata[1]} (%{customdata[2]})<br>%{y:.1%} over %{x} PA<extra></extra>"))
fig.add_hline(y=Q["house_median"], line=dict(color=GRAY, dash="dash", width=1.5), annotation_text=f"house median {pct(Q['house_median'], 1)}",
              annotation_position="bottom right", annotation_font=dict(color=MUTED))
fig.add_trace(go.Scatter(x=m.qa_pas, y=m.quick_ab_rate, mode="markers+text", name="Mayza 2026", text=["Mayza 2026"], textposition="top center", textfont=dict(color=INK),
                         marker=dict(color=RED, size=14, line=dict(color="#ffffff", width=2)), hovertemplate="Mayza 2026<br>%{y:.1%} over %{x} PA<extra></extra>"))
fig.update_xaxes(title_text="Plate appearances"); fig.update_yaxes(title_text="Quick-AB success rate (QA-1)", tickformat=".0%")
base(fig, f"The Mayza Success Rate: {pct(Q['rate'], 1)} of PAs went his way within three pitches",
     f"QA-1 = two strikes or a ground ball within the first three pitches. {ordn(Q['house']['percentile'])} percentile of {Q['house']['n']} Phillies pitcher-seasons "
     f"(both hands, 2015-26). Career {pct(Q['career'], 1)} over {Q['career_pas']:,} PA; 2026 was his lowest season, by a hair.")
ship(fig, "f09_quick_ab_rate", ok, dict(section="8 Quick-AB rate", asserts="2026 QA-1 above house median"))

# F10 nearest comps -----------------------------------------------------------------------
ds = R("delivery_distance").head(6)
ok = "nchez" in ds.player_name.iloc[0] and H["delivery"]["alvarado"]["rank"] <= 3
lab = [f"{n.split(', ')[1]} {n.split(', ')[0]} {y}" for n, y in zip(ds.player_name, ds.game_year)][::-1]
cols = [NAVY if "Alvarado" in l or "nchez" in l else LGRAY for l in lab]
fig = go.Figure(go.Bar(x=ds.distance[::-1], y=lab, orientation="h", marker=dict(color=cols), text=[f"{d:.2f}" for d in ds.distance[::-1]],
                       textposition="outside", textfont=dict(color=INK), customdata=ds[["primary_fb"]][::-1],
                       hovertemplate="%{y}<br>distance %{x:.2f} · primary FB %{customdata[0]}<extra></extra>"))
fig.update_xaxes(title_text="DS-1 distance to Mayza 2026 (z-units; smaller = more alike)"); fig.update_yaxes(title_text="Nearest season per pitcher")
base(fig, "Who throws like him? Sánchez's 2021 delivery, then José Alvarado",
     f"DS-1: release side/height, extension, and primary-fastball velocity, run and ride, z-scored over {H['delivery']['n_pop']} Phillies LHP seasons "
     f"({H['delivery']['n_pitchers']} pitchers). Alvarado 2026 ranks #{H['delivery']['alvarado']['rank']}: 'Alvarado lite' holds for the delivery, not the results.", h=500)
ship(fig, "f10_comps", ok, dict(section="9 Comps", asserts="Sánchez nearest; Alvarado rank<=3"))

pd.DataFrame(SPECS).to_csv(OUT / "dp_uc52_figure_specs.csv", index=False)
pd.DataFrame(BRAND).to_csv(OUT / "dp_uc52_brand_checks.csv", index=False)
print(len(SPECS), "figures shipped; brand checks all pass:", all(all(v for k, v in b.items() if k not in ("figure", "off_palette")) for b in BRAND))
