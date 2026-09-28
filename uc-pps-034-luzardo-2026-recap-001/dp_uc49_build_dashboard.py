"""
dp_uc49_build_dashboard.py — the narrative dashboard for UC #49 / uc-pps-034 ("The Chase").

Reads ONLY out/dp_uc49_* receipts (figure JSON, CSVs, headlines). Computes nothing that is published as a KPI.
Also writes the human-parent reconciliation receipt (out/dp_uc49_hp_reconciliation.csv) from headline values.

Outputs:
  dp_uc49_luzardo_2026_dashboard.html            repo copy: full document, offline (plotly.js inlined)
  dp_uc49_luzardo_2026_dashboard_artifact.html   Artifact body variant (no doctype/html/head/body)
"""
from __future__ import annotations

import html
import json
import os
from pathlib import Path

import pandas as pd
import plotly
import plotly.io as pio

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DP_UC49_OUT", HERE / "out"))
H = json.loads((OUT / "dp_uc49_headlines.json").read_text())
R = lambda n: pd.read_csv(OUT / f"dp_uc49_{n}.csv")        # noqa: E731
FIG = lambda k: json.loads((OUT / f"dp_uc49_{k}.json").read_text())   # noqa: E731
pct = lambda x, d=1: f"{100 * x:.{d}f}%"                   # noqa: E731
f3 = lambda x: f"{x:.3f}".lstrip("0")                        # noqa: E731
esc = html.escape

y25, y26, ld, gs, v, c26 = H["y2025"], H["y2026"], H["ld"], H["gs"], H["velo"], H["ctx"]["2026"]
kp, t, hv, oc = H["kp"], H["tests"], H["halves"], H["oc"]

# ---------------------------------------------------------------------------
# Human-parent reconciliation (HP) — the client's cell, graded. Values come from headlines only.
# ---------------------------------------------------------------------------
HP = pd.DataFrame([
    dict(id="HP-01", client="Luzardo does not need to be in the strike zone, he gets chase and whiff", verdict="SUPPORTED",
         governed=f"In-zone {pct(y26['in_zone_rate'])} (2025: {pct(y25['in_zone_rate'])}, p = {t['In-zone rate (tracked)']['p']:.3f}), "
                  f"his lowest since 2021 ({pct(H['y2021']['in_zone_rate'])}); chase {pct(y26['chase_rate'])} (a career high), whiff {pct(y26['whiff_rate'])}. Walks {pct(y26['bbrate'])} "
                  f"vs {pct(H['cmd26']['expected'])} expected for a Phillies lefty at that zone rate."),
    dict(id="HP-02", client="He does this better than most pitchers in my dataset", verdict="SUPPORTED, sized",
         governed=f"Chase #{c26['rank_chase']} and whiff #{c26['rank_whiff']} of {H['ctx_n']} Phillies pitcher-seasons (≥150 pitches); "
                  f"only {c26['dominated_by']} beat him on both (none a starter's workload); among {H['ctx_sw']['n']} starter workloads he is #1 in whiff and unbeaten on both. Among {H['ctx_n_lhp']} lefty seasons: chase #{c26['rank_chase_lhp']}, whiff #{c26['rank_whiff_lhp']}. "
                  f"The plus/plus quadrant holds {H['ctx_plus_plus_n']} seasons, so 'in the quadrant' alone is not rare; the depth into it is."),
    dict(id="HP-03", client="The best shift of his Major League career", verdict="SUPPORTED (by Game Score, not by strikeouts)",
         governed=f"GS-1 100, #1 of {gs['n_starts']} career starts (next: {gs['next_best']}); his only 27-out game. "
                  f"12 K is not his high ({gs['career_max_k']})."),
    dict(id="HP-04", client="An All-Star for the first time in his career in 2026", verdict="CARRY-IN, verified",
         governed="Named 7/7 as a replacement; ASG 7/14 at Citizens Bank Park (MLB.com). Not computed on."),
    dict(id="HP-05", client="A ballpark he will call home for the next 5 seasons", verdict="CARRY-IN, verified",
         governed="5 years / $135M covering 2027–2031, 2032 club option; signed 3/10/2026 (MLB.com)."),
    dict(id="HP-06", client="Could look to be one of the best acquisitions by Dave Dombrowski", verdict="NOT GRADED",
         governed=f"No transaction table in either repo, so 'acquired by' cannot be keyed (product P8, not bid). What the data can say: "
                  f"2026 K rate {kp['krate']['pct']}th and whiff {kp['whiff_rate']['pct']}th house percentile (Phillies pitcher-seasons ≥100 PA)."),
    dict(id="HP-07", client="Given that it is done for the regular season", verdict="SUPERSEDED",
         governed=f"His season stopped at {H['last_appearance']} (Labor Day). Carry-ins: scratched 9/12, 15-day IL 9/15 (shoulder inflammation), "
                  "activated for Game 162 as a reliever."),
    dict(id="HP-08", client="jl = pps[pn] + nphl[pn] (the career frame)", verdict="DIFFERS, explained",
         governed=f"The client frame carries {H['client_postseason_pitches_total']} postseason pitches inside season rows and loses "
                  f"{H['nphl_lost_to_dedup']} regular-season pitches to get_nphillies_data's keep-first dedup (O-26). 2026 is identical in both."),
    dict(id="HP-09", client="Whiff × chase scatter, 'Phillies Pitcher-Seasons, min 150 pitches'", verdict="REPRODUCED",
         governed=f"Name-keyed with postseason: n = {H['client_ctx']['n']}, Luzardo 2026 whiff #{H['client_ctx']['luz26_rank_whiff']}, chase "
                  f"#{H['client_ctx']['luz26_rank_chase']}. Id-keyed, regular season: n = {H['ctx_n']}, #{c26['rank_whiff']} / #{c26['rank_chase']}. Same picture."),
    dict(id="HP-10", client="Walk rate × in-zone rate with trendline='ols', color='jl_color'", verdict="DEFECT (chart)",
         governed="With color set, plotly fits one OLS line per color group, so the 'Luzardo' line is drawn through his own two seasons. "
                  f"Governed: one fit per handedness over the population (LHP slope {H['cmd26']['slope']:.2f})."),
    dict(id="HP-11", client="Pitch map from lhb_/rhb_pitch_mix", verdict="REPRODUCED, rounding noted",
         governed="pitch_mix rounds locations to 0.1 ft (O-25); PM-1 centroids are unrounded. Largest difference 0.05 ft: cosmetic here."),
    dict(id="HP-12", client="Pitch-map subtitle reads gy after the loop", verdict="CORRECT BY ACCIDENT",
         governed="The frame is filtered to 2026, so the loop runs once and the leaked gy (HP-18, uc-pps-033) happens to be right. "
                  "It will be wrong on any multi-season frame."),
    dict(id="HP-13", client="def edge_rate(...) (unfinished)", verdict="RULE-1: EXISTS",
         governed="Edge rate is an approved UC8 KPI (dp_uc8, uc-pps-008). Inherit it; do not finish a second one."),
])
HP.to_csv(OUT / "dp_uc49_hp_reconciliation.csv", index=False)

# ---------------------------------------------------------------------------
# Data for the page
# ---------------------------------------------------------------------------
figs = {k: FIG(k) for k in ["fig1_the_chase", "fig2_command", "fig3_career_arc", "fig4_season_by_start",
                            "fig5_laborday_pitch_by_pitch", "fig6_two_game_plans", "fig7_pitch_map", "fig8_career_game_scores"]}
for k, f in figs.items():   # responsive in the page; print sizes stay in the PNGs
    f["layout"].pop("width", None)
    f["layout"].pop("height", None)
    f["layout"]["autosize"] = True
    f["layout"]["title"]["text"] = ""          # the page carries the title and subtitle as HTML
    f["layout"]["title"]["subtitle"] = {"text": ""}
    f["layout"]["margin"]["t"] = 40
PA = R("laborday_pa")
LDP = R("laborday_pitches")
PL = R("postseason_ledger")
CARD = R("october_card")
HIST = R("october_card_postseason_history")
ST = R("starts_2026")
SPECS = {s["figure"]: s for s in json.loads((OUT / "dp_uc49_figure_specs.json").read_text())}
payload = dict(
    figs=figs,
    pa=PA.to_dict("records"),
    pitches=LDP[["pitch_of_game", "at_bat_number", "pitch_type", "release_speed", "description", "count", "is_whiff"]].to_dict("records"),
    starts=ST[["start_no", "game_date", "opp", "venue", "ip_display", "h", "r", "bb", "k", "pitches", "game_score", "first_n_ff_velo"]].round(2).to_dict("records"),
    dark=json.loads(json.dumps(pio.templates["plotly_dark"].to_plotly_json(), default=str)),
    light=json.loads(json.dumps(pio.templates["plotly_white"].to_plotly_json(), default=str)),
)


def sub(k):
    return esc(SPECS[k]["subtitle"])


def table(df, cols, heads, cls=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in heads)
    rows = "".join("<tr>" + "".join(f"<td>{esc(str(r[c]))}</td>" for c in cols) + "</tr>" for _, r in df.iterrows())
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'


PLt = PL.assign(date=PL.game_date.astype(str).str[:10], line=PL.ip_display.map(lambda x: f"{float(x):.1f}") + " IP, " + PL.h.astype(str) + " H, " + PL.r.astype(str) + " R, "
                + PL.bb.astype(str) + " BB, " + PL.k.astype(str) + " K")
PLt = PLt.merge(HIST.rename(columns={"game_date": "date"})[["date", "verdict"]], on="date", how="left")
post_tbl = table(PLt, ["date", "round", "team", "home_team", "role", "line", "pitches", "verdict"],
                 ["Date", "Round", "For", "Home team", "Role", "Line", "Pitches", "October card"])
CARDt = CARD.assign(bar_fmt=[f"{b:.1f} mph" if c == "first_n_ff_velo" else (f"{b:.1f}" if c == "whiff_per_100" else pct(b))
                             for b, c in zip(CARD.bar, CARD.column)],
                    med_fmt=[f"{b:.1f} mph" if c == "first_n_ff_velo" else (f"{b:.1f}" if c == "whiff_per_100" else pct(b))
                             for b, c in zip(CARD.season_median, CARD.column)],
                    rule=["at or above" if d == "higher" else "at or below" for d in CARD.direction])
card_tbl = table(CARDt, ["signature", "label", "rule", "bar_fmt", "med_fmt"], ["#", "Signature", "Holds when", "Bar (his 2026 edge)", "His 2026 median"])
hp_tbl = table(HP, ["id", "client", "verdict", "governed"], ["#", "Your notebook said", "Verdict", "What the governed build shows"], "hp")

hero_tiles = [
    ("29", "starts, the last on Labor Day", f"{H['pitches_2026']:,} regular-season pitches"),
    (pct(y26["krate"]), "K rate", f"{kp['krate']['pct']}th house percentile · #{kp['krate']['staff_rank']} on the 2026 staff"),
    (pct(y26["chase_rate"]), "chase rate", f"#{c26['rank_chase']} of {H['ctx_n']} Phillies pitcher-seasons"),
    ("100", "Game Score, Labor Day", f"#1 of {gs['n_starts']} career starts"),
]
tiles = "".join(f'<div class="tile"><div class="big">{a}</div><div class="lab">{esc(b)}</div><div class="note">{esc(c)}</div></div>'
                for a, b, c in hero_tiles)

CSS = """
:root{--bg:#fbfaf7;--surface:#ffffff;--ink:#1b1b1b;--ink2:#4a4f5c;--muted:#6b7080;--rule:#e3e6ec;--red:#E81828;--navy:#002D72;
--blue:#3B6FD8;--chip:#f1f3f6;--warn:#fff4f5;--warnrule:#E81828;--shadow:0 1px 2px rgba(0,0,0,.05)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;
--rule:#2e3138;--navy:#8FB0F0;--chip:#262a31;--warn:#2a1a1c;--shadow:none;color-scheme:dark}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#141414;--surface:#1c1c1c;--ink:#ececec;--ink2:#c5c8d0;--muted:#9aa0ad;--rule:#2e3138;--navy:#8FB0F0;
--chip:#262a31;--warn:#2a1a1c;--shadow:none}
*{box-sizing:border-box;min-width:0}code{overflow-wrap:anywhere}html,body{margin:0;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.55}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px 64px}
header.top{border-top:6px solid var(--red);padding:28px 0 8px}
.kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
h1{font-size:44px;line-height:1.05;margin:6px 0 4px;color:var(--navy)}h1 span{color:var(--red)}
.dek{font-size:18px;color:var(--ink2);max-width:820px;margin:6px 0 18px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0 18px}
.bar button{font:inherit;font-size:13px;}.bar button:focus-visible,.stepper button:focus-visible,nav.toc a:focus-visible{outline:2px solid var(--red);outline-offset:2px}.bar button{border:1px solid var(--rule);background:var(--surface);color:var(--ink);padding:6px 12px;border-radius:999px;cursor:pointer}
.bar button[aria-pressed="true"]{background:var(--navy);color:var(--bg);border-color:var(--navy)}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--rule);display:flex;gap:4px;overflow-x:auto;padding:8px 0}
nav.toc a{white-space:nowrap;font-size:13px;color:var(--ink2);text-decoration:none;padding:4px 10px;border-radius:6px}
nav.toc a:hover,nav.toc a.on{background:var(--chip);color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:10px 0 18px}
.tile{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px;box-shadow:var(--shadow)}
.tile .big{font-size:30px;font-weight:700;color:var(--navy)}.tile .lab{font-weight:600}.tile .note{font-size:12.5px;color:var(--muted)}
.warn{background:var(--warn);border-left:4px solid var(--warnrule);padding:12px 14px;border-radius:6px;font-size:13.5px;color:var(--ink2)}
.warn ul{margin:6px 0 0;padding-left:18px}
section.ch{padding:30px 0 6px;border-bottom:1px solid var(--rule)}
.chno{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--red);font-weight:700}
h1,h2{text-wrap:balance}h2{font-size:28px;margin:4px 0 8px;color:var(--ink)}
.lede{font-size:17px;color:var(--ink2);max-width:860px}
.fig{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:10px 10px 4px;margin:14px 0;box-shadow:var(--shadow)}
.fig h3{font-size:16px;margin:4px 6px 2px}.fig .sub{font-size:13px;color:var(--muted);margin:0 6px 6px}
.plot{width:100%;height:470px}.plot.tall{height:600px}.plot.short{height:380px}
.two{display:grid;grid-template-columns:1.25fr 1fr;gap:14px}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px;font-size:14px}
.panel h4{margin:0 0 6px;font-size:14px;color:var(--navy)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.chip{font-size:12.5px;padding:4px 8px;border-radius:6px;background:var(--chip);border-left:4px solid var(--muted)}
.chip.w{font-weight:700}
.stepper{display:flex;gap:8px;align-items:center;margin:6px 0 10px}
.stepper button{font:inherit;border:1px solid var(--rule);background:var(--surface);color:var(--ink);padding:6px 12px;border-radius:6px;cursor:pointer}
.stepper input{flex:1}
.tw{overflow-x:auto;margin:10px 0}table{border-collapse:collapse;width:100%;font-size:13px}
th{background:var(--navy);color:var(--bg);text-align:left;padding:7px 9px;font-weight:600}td{border-bottom:1px solid var(--rule);padding:7px 9px;vertical-align:top}
table.hp td:nth-child(3){font-weight:700;white-space:nowrap}
.quote{font-size:19px;border-left:4px solid var(--red);padding:4px 0 4px 14px;margin:14px 0;color:var(--ink)}
.carry{font-size:12px;color:var(--muted)}.tag{display:inline-block;font-size:11px;padding:1px 6px;border-radius:4px;background:var(--chip);color:var(--muted);margin-left:6px}
footer{font-size:12.5px;color:var(--muted);padding:24px 0}
.products{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0}
.prod{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;font-size:13px}
.prod b{display:block;color:var(--navy)}.prod .st{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
@media (max-width:820px){h1{font-size:32px}.tiles,.products{grid-template-columns:repeat(2,minmax(0,1fr))}.two{grid-template-columns:1fr}.plot{height:400px}.plot.tall{height:520px}}
"""


def chapter(no, anchor, title, lede, body):
    return f'<section class="ch" id="{anchor}"><div class="chno">Chapter {no}</div><h2>{esc(title)}</h2><p class="lede">{lede}</p>{body}</section>'


def figbox(key, title, cls=""):
    return f'<div class="fig"><h3>{esc(title)}</h3><p class="sub">{sub(key)}</p><div class="plot {cls}" id="{key}"></div></div>'


post25 = [p for p in H["post"] if p["team"] == "PHI"]
ch = []
ch.append(chapter(1, "arrival", "The arrival",
    f"The Phillies traded for him in December 2024 <span class='carry'>(carry-in, MLB.com)</span>. His first Phillies season: {y25['games']} starts, "
    f"K {pct(y25['krate'])}, BB {pct(y25['bbrate'])}, wOBA {f3(y25['woba'])}. Then October: {post25[0]['ip']} scoreless innings in a Division Series start at "
    f"home and {post25[1]['ip']} more in relief at Dodger Stadium. <b>{sum(p['outs'] for p in post25)} outs, 0 runs on his watch.</b> The Phillies still went home.",
    figbox("fig3_career_arc", "Eight seasons: the chase kept climbing, and in 2026 the zone let go")))
ch.append(chapter(2, "bet", "The bet",
    "In March the Phillies bought the next five years: $135 million, 2027 through 2031, with a club option for 2032 "
    "<span class='carry'>(carry-in, MLB.com, 3/10/2026)</span>. What they were buying is in the arsenal. The slider became a sweeper in 2025; "
    f"in 2026 the sweeper became his first pitch ({pct(H['ars']['2026']['ST']['usage'])} of pitches, whiff {pct(H['ars']['2026']['ST']['whiff'])}), "
    f"the four-seam gave up share ({pct(H['ars']['2025']['FF']['usage'])} → {pct(H['ars']['2026']['FF']['usage'])}) and the sinker grew "
    f"({pct(H['ars']['2025']['SI']['usage'])} → {pct(H['ars']['2026']['SI']['usage'])}). The sweeper-first redesign was first documented in uc-pps-017.",
    figbox("fig7_pitch_map", "Where the pitches live, 2026")))
ch.append(chapter(3, "chase", "The chase",
    f"Your notebook said it first: <i>he does not need to be in the strike zone, he gets chase and whiff.</i> Among {H['ctx_n']} Phillies pitcher-seasons "
    f"since 2015, his 2026 is #{c26['rank_chase']} in chase and #{c26['rank_whiff']} in whiff, and only {c26['dominated_by']} seasons beat it on both. "
    "<b>Click any dot</b> to read that season.",
    '<div class="two">' + figbox("fig1_the_chase", "Whiff as a function of chase", "tall") +
    '<div class="panel" id="drill"><h4>Drill-through</h4><p>Click a pitcher-season on the chart.</p>'
    f'<p><b>Among starters he stands alone.</b> Of the {H["ctx_sw"]["n"]} Phillies seasons with a starter\'s workload (≥2,000 pitches), his 2026 has the '
    f'highest whiff rate (next: Wheeler 2025, {pct(float(H["ctx_sw"]["next_whiff"]["whiff_rate"]))}), the #{H["ctx_sw"]["rank_chase"]} chase rate, and no season beats it on both. '
    f'None of the {c26["dominated_by"]} seasons that beat it overall carried a starter\'s workload.</p>'
    f'<p class="carry">Sources: out/dp_uc49_context_population.csv, _starter_workloads.csv, _frontier.csv (CX-1, CX-1b).</p></div></div>'))
ch.append(chapter(4, "zone", "Letting go of the zone",
    f"His in-zone rate fell from {pct(y25['in_zone_rate'])} to {pct(y26['in_zone_rate'])} (p = {t['In-zone rate (tracked)']['p']:.3f}), his lowest since 2021, "
    f"and his walk rate did not rise ({pct(y25['bbrate'])} → {pct(y26['bbrate'])}). For a Phillies lefty at his zone rate the fit expects "
    f"{pct(H['cmd26']['expected'])}; he is {abs(H['cmd26']['residual']) * 100:.1f} points better, a smaller walk residual than "
    f"{H['cmd26']['residual_pctile']}% of Phillies lefty seasons.",
    figbox("fig2_command", "Walk rate as a function of in-zone rate (LHP)")))
ch.append(chapter(5, "summer", "The summer",
    f"He was named an All-Star on July 7, for the first time, and the game was played at Citizens Bank Park <span class='carry'>(carry-in, MLB.com)</span>. "
    f"Before the break: {hv['first']['starts']} starts, {hv['first']['r27']:.2f} runs on watch per 27 outs. After it: {hv['second']['starts']} starts, "
    f"{hv['second']['r27']:.2f}, K {pct(hv['second']['krate'])}, wOBA {f3(hv['second']['woba'])}. August: {H['aug']['starts']} starts, K {pct(H['aug']['krate'])}, "
    f"{H['aug']['r']} runs in {H['aug']['outs']} outs, and NL Pitcher of the Month <span class='carry'>(carry-in)</span>. "
    "<b>Hover any bar</b> for the line.",
    figbox("fig4_season_by_start", "Twenty-nine starts", "tall")))
ch.append(chapter(6, "laborday", "Labor Day",
    f"September 7, the Braves in town, four games behind them in the division <span class='carry'>(carry-in)</span>. {ld['pitches']} pitches, "
    f"{ld['batters']} batters, {ld['whiffs']} whiffs, {ld['chases']} chases on {ld['ooz']} pitches out of the zone. Schwarber homered in the eighth. "
    f"The four-seam was faster in the ninth ({ld['ff_velo_9th']:.1f}) than in the game overall ({ld['ff_velo']:.1f}). "
    "<b>Step through it one plate appearance at a time.</b>",
    figbox("fig5_laborday_pitch_by_pitch", "Labor Day, pitch by pitch", "short") +
    '<div class="panel"><div class="stepper"><button id="prev" aria-label="Previous plate appearance">◀</button>'
    '<input type="range" id="pa" min="0" max="29" value="0" aria-label="Plate appearance"><button id="next" aria-label="Next plate appearance">▶</button></div>'
    '<div id="paout"></div></div>' +
    figbox("fig6_two_game_plans", "Two game plans", "short") +
    figbox("fig8_career_game_scores", "Where Labor Day sits in his career")))
ch.append(chapter(7, "silence", "The silence",
    f"There is no start after Labor Day. He was scratched from his next turn with shoulder stiffness and went on the 15-day IL on 9/15 with shoulder "
    f"inflammation; the Phillies activated him for Game 162, out of the bullpen <span class='carry'>(carry-ins: Phillies Nation 9/24, SI 9/27)</span>. "
    f"<b>What the log can say, and nothing more:</b> his first-15 four-seam velocity on Labor Day was {v['ld_first15']:.1f} mph against a season median of "
    f"{v['first15_med']:.1f}; the 109 pitches were his second-highest count of the year (high {v['max_pitches']}); the four-seam was "
    f"{ld['ff_velo_9th']:.1f} in the ninth. One earlier start, 8/26 at Seattle, sat below his band ({v['last3'][0]:.1f} mph average). "
    "The log shows velocity and workload. It does not show an injury, and this product does not infer one.", ""))
ch.append(chapter(8, "october", "October",
    f"Your notebook ended on it: <i>2026 could be the season to celebrate, forever. For Jesús Luzardo, it could be.</i> His postseason ledger so far is "
    f"{H['post_tot']['games']} games and {H['post_tot']['pa']} batters, from a Wild Card at the Bank in a Marlins uniform (3.2 IP, 8 H, 3 R) to "
    "7.2 scoreless innings last October. What would a <b>defining</b> October look like in his data? We wrote it down before it happened.",
    '<div class="two"><div><h3>The October card, registered 2026-09-27</h3>' + card_tbl +
    f'<p style="font-size:13.5px">An outing is <b>on-script</b> when it holds at least 3 of the 4 signatures. Each bar is the edge of his own 2026 range '
    f'(25th or 75th percentile of his 29 starts), and the signatures read the same for a start or a relief outing.</p>'
    f'<div class="warn"><b>Calibration, stated plainly.</b> Run on his own 2026 starts, the card calls {oc["backtest_on"]} on-script and '
    f'{oc["backtest_off"]} off-script, and the off-script starts allowed <i>fewer</i> runs ({oc["off_r27"]:.2f} vs {oc["on_r27"]:.2f} per 27 outs). '
    'It is a sameness card: it tells you whether October Luzardo is the pitcher of this season. It does not predict runs.</div></div>'
    '<div><h3>His Octobers so far</h3>' + post_tbl + '<p class="carry">Postseason pitches never enter a season rate here. Samples are tiny; every line prints its denominators. '
    '"Home team" is the scheduled home club (the 2020 Division Series was played in a neutral bubble).</p></div></div>'))

products = [("Narrative dashboard", "Built", "The season as an arc you can walk. This page."),
            ("Game story", "Built", "Labor Day pitch by pitch, with a stepper (chapter 6)."),
            ("October card", "Built", "Pre-registered signatures, graded after the fact (chapter 8)."),
            ("Feature report", "Built", "The long read, PDF (dp_uc49_…_report.pdf)."),
            ("Context board", "Built", "Your three scatters, governed, with drill-through (ch. 3–4)."),
            ("Notecard", "Built", "One image for a thread or broadcast (out/…fig9_notecard.png)."),
            ("Postseason ledger", "Built", "Career October, pitch-level (chapter 8)."),
            ("Acquisitions board", "Not built", "Needs a transaction table; offered as the next use case.")]
prod_html = "".join(f'<div class="prod"><span class="st">{esc(s)}</span><b>{esc(n)}</b>{esc(d)}</div>' for n, s, d in products)

def _clean(o):
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(x) for x in o]
    return o


PAYLOAD_JS = json.dumps(_clean(payload), default=str, allow_nan=False).replace("</", "<\\/")
BODY = f"""
<div class="wrap">
<header class="top">
 <div class="kicker">Phillies Pitching · uc-pps-034 · 2026 season recap · data through {H['anchor']}</div>
 <h1>The <span>Chase</span></h1>
 <p class="dek">Jesús Luzardo missed more bats than any Phillies starter of the Statcast era, stopped needing the strike zone to do it,
 threw the best game of his life on Labor Day, and then went quiet. This is his season, in eight chapters, ending on the question October will answer.</p>
 <div class="bar"><button id="t-auto" aria-pressed="true">Match my system</button><button id="t-light" aria-pressed="false">Brand light</button>
 <button id="t-dark" aria-pressed="false">Notebook dark</button></div>
</header>
<nav class="toc" aria-label="Chapters"><a href="#arrival">1 · Arrival</a><a href="#bet">2 · The bet</a><a href="#chase">3 · The chase</a><a href="#zone">4 · The zone</a>
<a href="#summer">5 · Summer</a><a href="#laborday">6 · Labor Day</a><a href="#silence">7 · Silence</a><a href="#october">8 · October</a><a href="#notebook">Your notebook</a><a href="#products">Products</a></nav>
<div class="tiles">{tiles}</div>
<div class="warn"><b>Read this first.</b><ul>
<li>Entity lock: MLBAM 666200, never a name filter. Regular season for every rate; {H['spring_rows_excluded']} spring rows excluded; postseason lives only in chapter 8.</li>
<li>Career frame (CF-2): Phillies log 2025–26 plus <code>luzardo.parquet</code> 2019–24, de-duplicated across {H['opp_files_with_subject']} opponent files that also hold his pitches ({H['dup_removed']} duplicates removed).</li>
<li>"House" percentiles and ranks are Phillies pitcher-seasons 2015–2026, not MLB-wide.</li>
<li>"Runs on watch" = runs scored during the plate appearances he threw (house <code>runs_created</code>); it includes unearned runs. ERA is not computed here (2.87 in 29 starts is a carry-in).</li>
<li>Carry-ins (trade, extension, All-Star, Labor Day box time, Pitcher of the Month, the IL, Game 162) are labelled where they appear and never computed on.</li></ul></div>
{''.join(ch)}
<section class="ch" id="notebook"><div class="chno">Appendix</div><h2>Your notebook, graded</h2>
<p class="lede">Every claim and chart choice in <code>September 2026.ipynb</code> cells 51 and 118, reproduced by your method, then by the governed one.</p>{hp_tbl}</section>
<section class="ch" id="products"><div class="chno">Appendix</div><h2>Eight ways to tell this story</h2>
<p class="lede">The organization scoped eight product forms against the narrative and built seven. Each owns a part of the story no other form tells.</p>
<div class="products">{prod_html}</div></section>
<footer>uc-pps-034 · dp_uc49 v1.0.0 · kernel dp_uc49_kernel.py (imports dp_uc48_kernel sha256 0f63857a…, dp_uc44_kernel a2c11909…) ·
receipts out/dp_uc49_* · governance trail: Agents for Data Products/data-products/uc-pps-034-luzardo-2026-recap-001/ ·
Internal: Phillies pitching and front office. Carry-in sources: MLB.com (12/2024, 3/10, 7/7, 9/7), Phillies Nation (9/24), SI (9/27).</footer>
</div>
<script id="payload" type="application/json">{PAYLOAD_JS}</script>
<script>
(function(){{
const P=JSON.parse(document.getElementById('payload').textContent);
const PC={{FF:'#D22D49',SI:'#C77800',ST:'#3B6FD8',CH:'#16945A'}};const PN={{FF:'Four-Seam',SI:'Sinker',ST:'Sweeper',CH:'Changeup'}};
const root=document.documentElement;
function isDark(){{const t=root.getAttribute('data-theme');if(t)return t==='dark';return window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches;}}
function css(v){{return getComputedStyle(root).getPropertyValue(v).trim();}}
function lay(base){{const L=JSON.parse(JSON.stringify(base));const d=isDark();L.template=d?P.dark:P.light;
 L.paper_bgcolor=css('--surface');L.plot_bgcolor=css('--surface');L.font=Object.assign({{}},L.font||{{}},{{color:css('--ink'),family:'Arial'}});return L;}}
const drawn={{}};
function themed(f){{if(!isDark())return f;let s=JSON.stringify(f);const m={{'#1b1b1b':css('--ink'),'#5b6170':css('--muted'),'#ffffff':css('--surface')}};
 for(const k in m)s=s.split('"'+k+'"').join('"'+m[k]+'"');return JSON.parse(s);}}
function draw(k){{const f=themed(P.figs[k]);const el=document.getElementById(k);if(!el)return;
 Plotly.react(el,f.data,lay(f.layout),{{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','toImage']}});drawn[k]=true;}}
function drawAll(){{Object.keys(P.figs).forEach(draw);}}
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting&&!drawn[e.target.id]){{draw(e.target.id);if(e.target.id==='fig1_the_chase')hookDrill();if(e.target.id==='fig5_laborday_pitch_by_pitch')showPA(+document.getElementById('pa').value);}}}}),{{rootMargin:'300px'}});
Object.keys(P.figs).forEach(k=>{{const el=document.getElementById(k);if(el)io.observe(el);}});
function setTheme(m){{if(m==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',m);
 ['auto','light','dark'].forEach(x=>document.getElementById('t-'+x).setAttribute('aria-pressed',String(x===m)));
 try{{localStorage.setItem('uc49-theme',m);}}catch(e){{}}Object.keys(drawn).forEach(draw);if(drawn['fig5_laborday_pitch_by_pitch'])showPA(+document.getElementById('pa').value);}}
['auto','light','dark'].forEach(x=>document.getElementById('t-'+x).addEventListener('click',()=>setTheme(x)));
try{{const s=localStorage.getItem('uc49-theme');if(s)setTheme(s);}}catch(e){{}}
if(window.matchMedia)matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{{if(!root.getAttribute('data-theme'))Object.keys(drawn).forEach(draw);}});
function hookDrill(){{const el=document.getElementById('fig1_the_chase');el.on('plotly_click',ev=>{{const p=ev.points[0];const cd=p.customdata;
 const name=cd?cd[0]+' '+cd[1]:p.data.name;const pitches=cd?cd[2]+' pitches':'';
 document.getElementById('drill').innerHTML='<h4>'+name+'</h4><p>Chase <b>'+(100*p.x).toFixed(1)+'%</b> · whiff <b>'+(100*p.y).toFixed(1)+'%</b><br>'+pitches+'</p>'+
 '<p>Against Luzardo 2026 (chase 33.7%, whiff 31.9%): '+(p.x>0.337?'more':'less')+' chase, '+(p.y>0.319?'more':'less')+' whiff.</p><p class="carry">Source: out/dp_uc49_context_population.csv (CX-1).</p>';}});}}
function showPA(i){{const a=P.pa[i];const ps=P.pitches.filter(x=>x.at_bat_number===a.at_bat_number);
 const chips=ps.map(x=>'<span class="chip'+(x.is_whiff?' w':'')+'" style="border-left-color:'+PC[x.pitch_type]+'">'+x.count+' · '+PN[x.pitch_type]+' '+Number(x.release_speed).toFixed(1)+' · '+x.description.replace(/_/g,' ')+'</span>').join('');
 document.getElementById('paout').innerHTML='<h4>PA '+(i+1)+' of 30 · inning '+a.inning+' · '+a.batter_name+' ('+a.stand+'HB), time through '+a.tto+'</h4><div class="chips">'+chips+'</div><p>'+a.des+'</p>';
 const el=document.getElementById('fig5_laborday_pitch_by_pitch');if(drawn['fig5_laborday_pitch_by_pitch']){{const x0=Math.min(...ps.map(x=>x.pitch_of_game))-0.5,x1=Math.max(...ps.map(x=>x.pitch_of_game))+0.5;
 const base=(P.figs['fig5_laborday_pitch_by_pitch'].layout.shapes||[]);Plotly.relayout(el,{{shapes:base.concat([{{type:'rect',xref:'x',yref:'paper',x0:x0,x1:x1,y0:0,y1:1,line:{{color:'#E81828',width:2}},fillcolor:'rgba(232,24,40,0.08)'}}])}});}}}}
const s=document.getElementById('pa');s.addEventListener('input',()=>showPA(+s.value));
document.getElementById('prev').addEventListener('click',()=>{{s.value=Math.max(0,+s.value-1);showPA(+s.value);}});
document.getElementById('next').addEventListener('click',()=>{{s.value=Math.min(29,+s.value+1);showPA(+s.value);}});
showPA(0);
const links=[...document.querySelectorAll('nav.toc a')];const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const so=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{links.forEach(l=>l.classList.toggle('on',l.getAttribute('href')==='#'+e.target.id));}}}}),{{rootMargin:'-40% 0px -55% 0px'}});
secs.forEach(x=>x&&so.observe(x));
}})();
</script>
"""

plotly_js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8").replace("\ufffd", "\\uFFFD")  # literal U+FFFD in a regex -> escape
HEAD = f"<title>Luzardo's 2026 Chase</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>{CSS}</style><script>{plotly_js}</script>"
full = f"<!doctype html><html lang='en'><head><meta charset='utf-8'>{HEAD}</head><body>{BODY}</body></html>"
(HERE / "dp_uc49_luzardo_2026_dashboard.html").write_text(full, encoding="utf-8")
(HERE / "dp_uc49_luzardo_2026_dashboard_artifact.html").write_text(HEAD + BODY, encoding="utf-8")
print("dashboard", round(len(full) / 1e6, 2), "MB; HP rows", len(HP))
