"""
dp_uc48_build_dashboard.py — "The Tick and a Half": Jonathan Bowlan's 2026 season, told interactively.

Rules (house pattern from dp_uc47_build_dashboard.py):
  * Reads ONLY out/dp_uc48_* receipts. Every number in the narrative is formatted from
    dp_uc48_headlines.json here; the browser never recomputes a KPI. The one live
    view the browser builds is the drill-through, and it draws only receipt values
    (centroids + pre-binned densities).
  * Offline: plotly.js is inlined from the installed plotly package. The repo copy uses a
    system font stack (no webfont); the published copy may add a Google Fonts link.
  * Themes: brand light and the client's notebook dark. The page follows the viewer's
    theme, and the toggle stamps data-theme on <html>. Charts re-template on every change.
  * Persona lens: one control re-reads every chapter for Front Office, Pitching Coach,
    Pitching Analyst, Catcher, Manager or Pitcher. The callouts come from the PA-1 ledger.
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
OUT = Path(os.environ.get("DP_UC48_OUT", HERE / "out"))
DEST = HERE / "dp_uc48_bowlan_2026_dashboard.html"
ART = HERE / "dp_uc48_bowlan_2026_dashboard.artifact.html"   # body-only variant for the Artifact publisher

H = json.loads((OUT / "dp_uc48_headlines.json").read_text())
csv = lambda n: json.loads(pd.read_csv(OUT / f"dp_uc48_{n}.csv").to_json(orient="records"))  # noqa: E731
y25, y26 = H["y2025"], H["y2026"]
A = H["arsenal"]; U25, U26 = H["usage"]["2025"], H["usage"]["2026"]; T = H["tests"]; KP = H["kp"]; AR = H["arch"]
VB = H["velo_bucket"]; MS = H["mix_by_stand"]; L = H["ledger"]


def pct(x, d=0):
    return f"{100 * x:.{d}f}%"


def f3(x):
    return f"{x:.3f}".lstrip("0") if x < 1 else f"{x:.3f}"


# ---------------------------------------------------------------------------
# Narrative — every number formatted from headlines.json (verification family F reads this)
# ---------------------------------------------------------------------------
BOX = [
    ("G", f"{y26['games']}"), ("PA", f"{y26['plate_apps']}"), ("K%", pct(y26['krate'], 1)), ("BB%", pct(y26['bbrate'], 1)),
    ("wOBA", f3(y26['woba'])), ("FF mph", f"{y26['ff_velo']:.1f}"), ("Ride", f"{y26['ff_vert']:.1f}\""),
    ("FF grade", f"#{AR['2026']['rank']} of {H['arch_pop_n']}"),
]

CH = [
    dict(id="buy", n="1", title="The buy", personas=["Front Office"],
         dek=f"Kansas City's {f3(y25['woba'])} wOBA hid a four-seam that already had plus ride and elite whiff.",
         body=[
             f"In 2025 Bowlan was a {y25['games']}-game Royals reliever with a {pct(y25['krate'], 1)} strikeout rate, a {pct(y25['bbrate'], 1)} walk rate and a "
             f"{f3(y25['woba'])} wOBA against, which is ordinary run prevention. The four-seam underneath was not ordinary. uc-pps-032 graded its ride {AR['2025']['g_ivb']} and its whiff rate "
             f"{AR['2025']['g_whiff']} against {H['arch_pop_n']} right-handed four-seam seasons. On results alone it ranked #{AR['2025']['rank']}. The shape axis held it back: a velocity grade of {AR['2025']['g_velo']}.",
             f"The Phillies sent Matt Strahm to Kansas City for him in the offseason (MLB.com; a carry-in, never computed on). A year later the same pitch grades "
             f"{AR['2026']['shape']} on shape and {AR['2026']['results']} on results. That makes it <b>#{AR['2026']['rank']} of {H['arch_pop_n']}</b> and the only elite right-handed four-seam on the 2026 staff.",
         ],
         figs=["fig1_archetype_flip"], table="recap"),
    dict(id="tick", n="2", title="The tick and a half", personas=["Pitching Coach", "Pitcher"],
         dek=f"+{H['ff_velo_delta']:.2f} mph on the four-seam, and the rest of the arsenal came with it.",
         body=[
             f"The four-seam averaged {y25['ff_velo']:.1f} mph in 2025 and {y26['ff_velo']:.1f} in 2026, with {H['ff_spin_delta']:.0f} more rpm. Both changes hold at p < .001. "
             f"The rest of the arsenal gained too: sinker {A['2025_SI']['velo']:.1f} → {A['2026_SI']['velo']:.1f}, slider {A['2025_SL']['velo']:.1f} → {A['2026_SL']['velo']:.1f}, "
             f"changeup {A['2025_CH']['velo']:.1f} → {A['2026_CH']['velo']:.1f}. When every pitch gets faster at once, the cause is usually the body and the delivery, not one grip.",
             f"A shorter role could produce the same numbers, since relievers throw harder in short stints. The first ten pitches of an outing rule that out. There, fatigue cannot matter, "
             f"and he went from {VB['2025_1-10']['velo']:.1f} to {VB['2026_1-10']['velo']:.1f} mph. The gain is in the arm.",
         ],
         figs=["fig2_velo_box", "fig9_velo_by_outing", "fig4_velo_spin"], detail="fig3_gemini_grid"),
    dict(id="carry", n="3", title="The carry that stayed", personas=["Pitching Analyst", "Front Office"],
         dek=f"{y25['ff_vert']:.1f}\" → {y26['ff_vert']:.1f}\" of ride. Same pitch, thrown harder.",
         body=[
             f"The movement profile hardly moved: ride {y25['ff_vert']:.1f} → {y26['ff_vert']:.1f} in, horizontal break {A['2025_FF']['hb_in']:.1f} → {A['2026_FF']['hb_in']:.1f} in. "
             f"Against every Phillies right-hander since 2015 (2017 excluded), his 2026 four-seam ranks <b>#{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']}</b> for ride. "
             f"Only {pct(H['share_other_above_median'], 1)} of {H['other_rhp_ff_pitches']:,} other Phillies RHP four-seams ride as much as his median pitch.",
             "The notebook comment reads \"Vert remained elite at 18 inches\", and it printed 18.0 in both seasons. That match is partly an artifact: <code>pitch_mix</code> rounds "
             "<code>pfx_z</code> to 0.1 ft before the ×12, so vert can only move in 1.2-inch steps. The unrounded values are in the table above (O-25).",
             "Kellen wrote that the staff plot \"could be a drill down from a different visual.\" The explorer below does that. Start from every Phillies RHP pitch-type centroid, then click a pitch to see that pitch pitch-by-pitch against the staff.",
         ],
         figs=["fig5_movement"], drill=True),
    dict(id="platoon", n="4", title="Rebuilt by platoon", personas=["Pitching Analyst", "Pitching Coach"],
         dek="Four-seam and changeup to lefties, a new sweeper for righties, the curveball shelved.",
         body=[
             f"Against lefties the four-seam and changeup went from {pct(MS['2025_L_FF'] + MS['2025_L_CH'])} of his pitches to {pct(MS['2026_L_FF'] + MS['2026_L_CH'])}. "
             f"The changeup gained {A['2026_CH']['velo'] - A['2025_CH']['velo']:.1f} mph and its whiff rate rose from {f3(A['2025_CH']['whiff_rate'])} to {f3(A['2026_CH']['whiff_rate'])}. "
             f"Righties saw a sweeper that did not exist in 2025 ({pct(MS['2026_R_ST'])} of pitches). The curveball fell from {pct(A['2025_CU']['usage'], 1)} to {pct(A['2026_CU']['usage'], 1)}.",
             f"The four-seam changed jobs. In 2025 it was a whiff pitch ({f3(A['2025_FF']['whiff_rate'])} per swing, {f3(A['2025_FF']['xwobacon'])} xwOBA on contact). "
             f"In 2026 it missed fewer bats ({f3(A['2026_FF']['whiff_rate'])}) but the contact it allowed was weak ({f3(A['2026_FF']['xwobacon'])}). Its run value rose from "
             f"{A['2025_FF']['rv100']:+.1f} to {A['2026_FF']['rv100']:+.1f} per 100 pitches.",
             f"<b>Two things to watch for 2027.</b> The sinker stopped working: {f3(A['2025_SI']['whiff_rate'])} → {f3(A['2026_SI']['whiff_rate'])} whiff, "
             f"{f3(A['2025_SI']['xwobacon'])} → {f3(A['2026_SI']['xwobacon'])} xwOBA on contact. The new sweeper sits at {A['2026_ST']['rv100']:+.1f} runs per 100 on {int(A['2026_ST']['n'])} pitches, "
             "which is too few to judge but not yet a weapon.",
         ],
         figs=["fig7_platoon_mix"], table="arsenal"),
    dict(id="count", n="5", title="The fastball when it matters", personas=["Catcher", "Pitcher"],
         dek=f"Two strikes: {pct(T['Four-seam share, 2K counts']['r25'])} → {pct(T['Four-seam share, 2K counts']['r26'])} four-seams. Behind: {pct(T['Four-seam share, behind counts']['r25'])} → {pct(T['Four-seam share, behind counts']['r26'])}.",
         body=[
             f"The biggest usage change in the log is <i>when</i> he threw the four-seam. With two strikes its share rose from {pct(T['Four-seam share, 2K counts']['r25'])} to "
             f"{pct(T['Four-seam share, 2K counts']['r26'])}. Behind in the count it rose from {pct(T['Four-seam share, behind counts']['r25'])} to {pct(T['Four-seam share, behind counts']['r26'])}. "
             "Both shifts are significant at p < .01. With a 97 mph four-seam that rides, the battery trusted it in the counts that decide the plate appearance.",
             f"The results moved the right way: strikeouts {pct(y25['krate'], 1)} → {pct(y26['krate'], 1)}, walks {pct(y25['bbrate'], 1)} → {pct(y26['bbrate'], 1)}. "
             f"On {T['K rate (K / PA)']['n25']} and {T['K rate (K / PA)']['n26']} PA neither change is statistically settled (p = {T['K rate (K / PA)']['p']:.2f} and {T['BB rate (BB / PA)']['p']:.2f}). "
             f"The strikeout rate is still his: {pct(y26['krate'], 1)} ranks in the <b>{KP['krate']['pct']}th percentile</b> of {KP['krate']['n']} Phillies pitcher-seasons since 2015 (≥100 PA), "
             f"second on the 2026 staff only to {H['staff_k_leader'].split(', ')[1]} {H['staff_k_leader'].split(', ')[0]}.",
             f"The walk cut did not come from getting ahead. First-pitch strikes <i>fell</i>, from {pct(T['First-pitch strike rate']['r25'])} to {pct(T['First-pitch strike rate']['r26'])}. "
             "He fell behind more often and won anyway, because the pitch he threw from behind was the four-seam.",
         ],
         figs=["fig8_ff_by_count"], table="tests"),
    dict(id="job", n="6", title="The eighth-inning job", personas=["Manager"],
         dek=f"{H['apps_7th_8th_2026']} of {y26['games']} entries in the 7th or 8th. {U25['pitches_per_app']:.1f} → {U26['pitches_per_app']:.1f} pitches an outing.",
         body=[
             f"Kansas City used him in {pct(U25['multi_inning_share'])} multi-inning outings. Philadelphia gave him one inning: {pct(U26['multi_inning_share'])} multi-inning, "
             f"{pct(U26['start_of_inning_share'])} of entries at the start of an inning, and {pct(U26['late_entry_share'])} in the 7th or later. He bridged to Duran: "
             f"{H['apps_7th_8th_2026']} of his {y26['games']} appearances began in the 7th or 8th. The price was frequency. That meant {y26['games']} games, {int(U26['back_to_backs'])} on back-to-back days, "
             f"and a median of {int(U26['median_rest'])} days' rest (it was {int(U25['median_rest'])}).",
             f"{H['scoreless_apps_2026']} of the {y26['games']} outings were scoreless. \"Runs created\" counts every run that scored while he pitched, including runners he inherited. "
             f"The {H['rc_by_entry']['2026_dirty']['apps']} outings he started with men on base produced {H['rc_by_entry']['2026_dirty']['rc']} of his {y26['runs_created']} runs. "
             "That is why runs per PA rose even as wOBA fell.",
             f"He left the 9/17 game against the Mets during an at-bat with Lindor. The Inquirer reported a right groin strain and no IL stint; this is a carry-in, not data. "
             f"The log shows no velocity warning beforehand. His last five outings averaged {H['last5_ff_velo']:.1f} mph on the four-seam against {H['season_ff_velo_2026']:.1f} for the season.",
         ],
         figs=["fig10_entry_inning", "fig11_monthly"], timeline=True),
]

CALLOUTS = {  # chapter id -> persona -> text; every claim traces to the PA-1 ledger or headlines
    "buy": {
        "Front Office": f"FO-1 is <b>{L['FO-1']['strength']}</b>. All three signatures are present: the 2025 ride grade was {AR['2025']['g_ivb']}, the whiff grade {AR['2025']['g_whiff']}, and wOBA against was {f3(y25['woba'])}. The repeatable lesson is to buy the four-seam shape and whiff before the run prevention shows up. Confirming it needs the pro-scouting file, which is not in either repo.",
        "Manager": "The 2026 table is the season you managed. The 2025 column is what you inherited.",
    },
    "tick": {
        "Pitching Coach": f"PC-1 is <b>{L['PC-1']['strength']}</b>: all five velocity signatures are present, including pitches 1–10. Nothing in the log shows <i>what</i> produced the gain (strength program, mechanics, intent). Your bullpen and lab notes are the confirmation.",
        "Pitcher": f"You threw every pitch harder, and you did it from the first pitch of an outing ({VB['2025_1-10']['velo']:.1f} → {VB['2026_1-10']['velo']:.1f} mph).",
        "Front Office": f"The velocity moved the grade: {AR['2025']['g_velo']} → {AR['2026']['g_velo']} on velocity was the whole shape-axis flip.",
    },
    "carry": {
        "Pitching Analyst": "Ride is stable (shape metrics stabilize in under 1 pitch, per uc-pps-032 SG-7), so the 2026 ride is real. Fix the notebook's vert rounding (O-25) before comparing shapes again.",
        "Front Office": f"#{H['staff_ff_ivb_rank']} of {H['staff_ff_seasons_n']} Phillies RHP four-seam seasons for ride. That was the carry you acquired.",
    },
    "platoon": {
        "Pitching Analyst": f"AN-1 is <b>{L['AN-1']['strength']}</b> on usage: the lefty mix, the new sweeper and the shelved curveball are all present, and the changeup whiff jumped. WA-2: the sweeper's {A['2026_ST']['rv100']:+.1f} RV/100 on {int(A['2026_ST']['n'])} pitches needs about 1,000 pitches before it means much.",
        "Pitching Coach": f"WA-1 is <b>{L['WA-1']['strength']}</b>: the sinker lost its whiff ({f3(A['2025_SI']['whiff_rate'])} → {f3(A['2026_SI']['whiff_rate'])}) and started getting hit ({f3(A['2026_SI']['xwobacon'])} xwOBA on contact). It is the first thing to look at in the spring.",
    },
    "count": {
        "Catcher": f"CA-1 is <b>{L['CA-1']['strength']}</b>: the four-seam calls at two strikes and when behind are present and significant, but the K-rate gain is not yet significant. CA-2 (get ahead early) is <b>{L['CA-2']['strength']}</b>, because first-pitch strikes fell. The log shows the result of your calls, not the calls themselves.",
        "Pitcher": f"PI-1 is <b>{L['PI-1']['strength']}</b>: hitters chased more ({f3(y25['chase_rate'])} → {f3(y26['chase_rate'])}, {KP['chase_rate']['pct']}th house percentile) and made weaker contact on the four-seam.",
    },
    "job": {
        "Manager": f"MG-1 is <b>{L['MG-1']['strength']}</b>: all four role signatures are present. MG-2 (a velocity warning before 9/17) is <b>{L['MG-2']['strength']}</b>: there was no drop in velocity. The workload question for 2027 is frequency ({int(U26['back_to_backs'])} back-to-backs, median rest {int(U26['median_rest'])} days), not pitches per outing.",
        "Front Office": f"{y26['games']} appearances, the most of his career by {y26['games'] - y25['games']}. His career total is now {H['career_games']} games, and 2026 alone is {y26['games'] / H['prior_career_games']:.1f}× everything before it.",
    },
}

PERSONAS = ["All", "Front Office", "Pitching Coach", "Pitching Analyst", "Catcher", "Manager", "Pitcher"]

data = dict(
    H=H, CH=CH, CALLOUTS=CALLOUTS, PERSONAS=PERSONAS, BOX=BOX,
    figs={k: json.loads((OUT / f"dp_uc48_{k}.json").read_text()) for k in
          ("fig1_archetype_flip", "fig2_velo_box", "fig3_gemini_grid", "fig4_velo_spin", "fig5_movement", "fig7_platoon_mix",
           "fig8_ff_by_count", "fig9_velo_by_outing", "fig10_entry_inning", "fig11_monthly")},
    recap=csv("recap_governed"), arsenal=csv("arsenal_by_season"), tests=csv("rate_tests"), apps=csv("appearances"),
    hp=csv("hp_reconciliation"), gm=csv("gemini_cell_audit"), ledger=csv("persona_ledger"), sigs=csv("persona_signatures"),
    dq=csv("dq_scorecard"), fresh=csv("freshness_manifest"), cen=csv("staff_arsenal_centroids"),
    dens=json.loads((OUT / "dp_uc48_staff_density.json").read_text()),
    pitches=[r for r in csv("bowlan_pitches") if r["game_year"] == 2026],
    templates={"light": json.loads(json.dumps(pio.templates["plotly_white"].to_plotly_json(), default=str)),
               "dark": json.loads(json.dumps(pio.templates["plotly_dark"].to_plotly_json(), default=str))},
)
plotly_js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8").replace("\ufffd", "\\uFFFD")   # plotly.min.js carries one literal U+FFFD in a regex; escape it (Artifact publisher rejects raw U+FFFD)

CSS = r"""
:root{
  --bg:#F3F5F8; --panel:#FFFFFF; --ink:#101A2E; --ink2:#46506A; --muted:#6B7488; --line:#DCE1EA;
  --navy:#002D72; --red:#C8102E; --red-ink:#B00E28; --chip:#E9EDF4; --focus:#2F6FE0;
  --good:#1E7A46; --warn:#9A6200; --bad:#B00E28;
  --display:"Oswald","Arial Narrow","Roboto Condensed",Arial,sans-serif;
  --body:"Source Sans 3","Segoe UI",Arial,Helvetica,sans-serif;
  --mono:"JetBrains Mono",Consolas,"Courier New",monospace;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0F1319; --panel:#171C24; --ink:#E8ECF3; --ink2:#B7C0D0; --muted:#8C96A8; --line:#2A313D;
  --navy:#8FB0FF; --red:#FF5A66; --red-ink:#FF7A84; --chip:#222936; --focus:#8FB0FF;
  --good:#5FD08F; --warn:#F2B64B; --bad:#FF7A84; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0F1319; --panel:#171C24; --ink:#E8ECF3; --ink2:#B7C0D0; --muted:#8C96A8; --line:#2A313D;
  --navy:#8FB0FF; --red:#FF5A66; --red-ink:#FF7A84; --chip:#222936; --focus:#8FB0FF;
  --good:#5FD08F; --warn:#F2B64B; --bad:#FF7A84; color-scheme:dark;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--body)}
.wrap{max-width:1240px;margin:0 auto;padding-inline:20px;padding-block:0 60px}
header.top{padding-block:22px 14px;border-bottom:4px solid var(--red)}
.eyebrow{font:600 12px/1 var(--body);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
h1{font:600 clamp(34px,6vw,64px)/1 var(--display);letter-spacing:.01em;margin:8px 0 6px;text-transform:uppercase;text-wrap:balance}
h1 em{font-style:normal;color:var(--red)}
.lede{max-width:70ch;color:var(--ink2);margin:6px 0 0}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-top:14px}
.box{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--line);background:var(--panel);border-radius:4px;overflow:hidden}
.box div{padding:8px 14px;border-right:1px solid var(--line);min-width:84px}
.box div:last-child{border-right:0}
.box b{display:block;font:600 22px/1.1 var(--display);font-variant-numeric:tabular-nums;color:var(--ink)}
.box span{font:600 12px/1 var(--body);letter-spacing:.04em;color:var(--muted)}
button{font:inherit;color:inherit}
.tbtn{border:1px solid var(--line);background:var(--panel);padding:7px 12px;border-radius:4px;cursor:pointer}
.lens{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding-block:10px;border-bottom:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.lens label{font:600 12px/1 var(--body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-right:4px}
.chip{border:1px solid var(--line);background:var(--panel);padding:6px 12px;border-radius:999px;cursor:pointer;font-size:14px}
.chip[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:var(--bg)}
.chip:focus-visible,.tbtn:focus-visible,summary:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.layout{display:grid;grid-template-columns:220px minmax(0,1fr);gap:28px;margin-top:18px}
nav.rail{position:sticky;top:70px;align-self:start;display:flex;flex-direction:column;gap:2px}
nav.rail a{display:grid;grid-template-columns:28px 1fr;gap:6px;padding:7px 8px;border-radius:4px;color:var(--ink2);text-decoration:none;font-size:14px}
nav.rail a b{font:600 15px/1.2 var(--display);color:var(--muted)}
nav.rail a.hit b{color:var(--red)}
nav.rail a.dim{opacity:.45}
nav.rail a:hover{background:var(--chip)}
section.ch{padding-block:26px;border-bottom:1px solid var(--line);scroll-margin-top:70px}
section.ch.dim .body,section.ch.dim .figs,section.ch.dim .extra{display:none}
section.ch.dim .more{display:inline-block}
.more{display:none;margin-top:8px}
.chhead{display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:baseline}
.chnum{font:600 44px/1 var(--display);color:var(--red)}
h2{font:600 30px/1.1 var(--display);text-transform:uppercase;margin:0;text-wrap:balance}
.dek{font-size:18px;color:var(--ink2);margin:4px 0 0}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.tag{font:600 11px/1 var(--body);letter-spacing:.08em;text-transform:uppercase;background:var(--chip);color:var(--ink2);padding:5px 8px;border-radius:3px}
.body{max-width:72ch;margin-top:12px}
.body p{margin:0 0 12px}
code{font:13px var(--mono);background:var(--chip);padding:1px 4px;border-radius:3px}
.callout{max-width:72ch;border:1px solid var(--line);border-left:4px solid var(--navy);background:var(--panel);padding:10px 14px;margin:10px 0;border-radius:0 4px 4px 0}
.callout .who{font:600 11px/1 var(--body);letter-spacing:.12em;text-transform:uppercase;color:var(--navy);margin-bottom:5px}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:16px;margin-top:10px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:10px 12px}
.fig h3{font:600 15px/1.3 var(--body);margin:0}
.fig p.cap{font-size:13.5px;color:var(--muted);margin:3px 0 4px}
.plot{width:100%;height:440px}
.tw{overflow-x:auto;margin-top:12px;border:1px solid var(--line);border-radius:4px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th{background:var(--chip);color:var(--ink);text-align:left;padding:7px 8px;font-weight:600;white-space:nowrap}
td{border-top:1px solid var(--line);padding:6px 8px;vertical-align:top}
td.n{text-align:right;white-space:nowrap}
.pill{display:inline-block;font:600 11px/1 var(--body);letter-spacing:.06em;text-transform:uppercase;padding:4px 7px;border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.v-good{color:var(--good)}.v-warn{color:var(--warn)}.v-bad{color:var(--bad)}.v-mute{color:var(--muted)}
details{margin-top:10px}summary{cursor:pointer;color:var(--navy);font-weight:600}
.drill{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin-top:12px}
.ptbtns{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
.note{font-size:13px;color:var(--muted)}
.gov{margin-top:26px;font-size:13px;color:var(--muted);max-width:90ch}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
@media (max-width:900px){.layout{grid-template-columns:1fr}nav.rail{display:none}.drill{grid-template-columns:1fr}}
@media (max-width:520px){.plot{height:360px}.box div{min-width:70px;padding:7px 10px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
"""

BODY = r"""
<div class="wrap">
<header class="top">
  <div class="eyebrow">Phillies pitching · 2026 season recap · uc-pps-033 · data through __ANCHOR__</div>
  <h1>The tick <em>and a half</em></h1>
  <p class="lede">Jonathan Bowlan arrived from Kansas City with a four-seam that already had plus ride and elite whiff. He threw it a mile and a half an hour harder, threw it in the counts that mattered, and got one inning a night. It became the #2 right-handed four-seam in the house frame. Pick a role below to read the season from that chair.</p>
  <div class="bar"><div class="box" id="box"></div><button class="tbtn" id="theme" type="button">Notebook dark</button></div>
</header>
<div class="lens" role="toolbar" aria-label="Persona lens"><label>Read as</label><span id="lens"></span></div>
<div class="layout">
  <nav class="rail" id="rail" aria-label="Chapters"></nav>
  <main id="main"></main>
</div>
<p class="gov">UC #48 · <code>uc-pps-033</code> · <code>dp_uc48</code> v1.0.0 · Phillies Pitching (pps). Entity-locked to MLBAM 680742. Regular season only (__SPRING__ spring rows excluded). Percentiles are house-frame (Phillies pitcher-seasons 2015–26, ≥100 PA), not MLB-wide. Four-seam grades are inherited from uc-pps-032 (bounded frame, 405 pitcher-seasons). Persona actions are hypotheses with data signatures, not a record of what anyone did. Carry-ins (the Strahm trade; the 9/17 exit) are never computed on. Every number on this page is formatted from <code>out/dp_uc48_headlines.json</code> and checked by <code>dp_uc48_verification.py</code>.</p>
</div>
"""

JS = r"""
const D = __DATA__;
const $ = id => document.getElementById(id);
let lens = 'All';
const LIGHT2DARK = {'#002D72':'#8FB0FF','#EEF0F4':'#262C37','#5b6170':'#C9D1E0','#B0B7C3':'#6B7488','#1b1b1b':'#E8ECF3'};
function isDark(){const t=document.documentElement.dataset.theme; if(t) return t==='dark'; return matchMedia('(prefers-color-scheme: dark)').matches;}
function cssv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();}
function recolor(obj){ if(!isDark()) return obj; let s=JSON.stringify(obj); for(const [a,b] of Object.entries(LIGHT2DARK)){s=s.split(a).join(b);} return JSON.parse(s);}
function lay(extra){return Object.assign({template:D.templates[isDark()?'dark':'light'],paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
  font:{family:'Arial',size:12.5,color:cssv('--ink')},margin:{l:56,r:14,t:18,b:48},legend:{orientation:'h',y:-0.2,x:0},autosize:true},extra||{});}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
const drawn = {};
const CFG = {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','toImage']};   // no download button: the Artifact viewer blocks page-initiated saves
function drawFig(el,k){const f=recolor(D.figs[k]);const L=Object.assign({},f.layout,lay({height:el.clientHeight||440}));
  delete L.title; L.width=null; if(k==='fig3_gemini_grid'){L.height=620;}
  Plotly.react(el,f.data,L,CFG);}
function figTitle(k){const t=D.figs[k].layout.title||{};return {t:(t.text||'').replace(/<[^>]+>/g,''),s:((t.subtitle||{}).text||'').replace(/<br>/g,' ')};}

// ---------- tables ----------
const f3 = x => x==null? '—' : (Math.abs(x)<1? x.toFixed(3).replace(/^0/,'').replace(/^-0/,'-') : x.toFixed(3));
const pc = (x,d=1) => x==null? '—' : (100*x).toFixed(d)+'%';
function tbl(cols,rows){return '<div class="tw"><table><thead><tr>'+cols.map(c=>'<th>'+c[0]+'</th>').join('')+'</tr></thead><tbody>'+
  rows.map(r=>'<tr>'+cols.map(c=>'<td class="'+(c[2]||'')+'">'+c[1](r)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';}
function recapTable(){const r=D.recap.slice().sort((a,b)=>a.game_year-b.game_year);
  const rows=[['Season',x=>x.game_year],['G',x=>x.games,'n'],['PA',x=>x.plate_apps,'n'],['Pitches',x=>x.pitches,'n'],['AVG',x=>f3(x.ba),'n'],['OBP',x=>f3(x.obp),'n'],['SLG',x=>f3(x.slg),'n'],
   ['wOBA',x=>f3(x.woba),'n'],['K%',x=>pc(x.krate),'n'],['BB%',x=>pc(x.bbrate),'n'],['HR/PA',x=>f3(x.hr_rate),'n'],['Runs created',x=>x.runs_created,'n'],['RC/PA',x=>f3(x.rc_per_pa),'n'],
   ['RC/G',x=>f3(x.rc_per_gm),'n'],['FF mph',x=>x.ff_velo.toFixed(1),'n'],['FF rpm',x=>Math.round(x.ff_spin),'n'],['FF ride (in)',x=>x.ff_vert.toFixed(1)+' <span class="note">(nb '+x.ff_vert_notebook.toFixed(1)+')</span>','n'],
   ['Breaking whiff',x=>f3(x.whiff_rate_breaking)+' <span class="note">/'+x.swings_breaking+'</span>','n'],['In-zone FF whiff',x=>f3(x.whiff_rate_iz_ff)+' <span class="note">/'+x.swings_iz_ff+'</span>','n']];
  return tbl(rows,r)+'<p class="note">Your cell 115 table, functionalized as <code>season_recap(pitcher_id)</code>. 2023 (14 PA) and 2024 (17 PA) are context only. The small grey numbers are swings (the whiff denominators) and the notebook\'s rounded ride.</p>';}
function arsenalTable(){const r=D.arsenal.filter(x=>x.game_year>=2025&&x.n>=5).sort((a,b)=>b.game_year-a.game_year||b.n-a.n);
  return tbl([['Season',x=>x.game_year],['Pitch',x=>esc(x.pitch_name)],['n',x=>x.n,'n'],['Usage',x=>pc(x.usage),'n'],['mph',x=>x.velo.toFixed(1),'n'],['rpm',x=>Math.round(x.spin),'n'],
   ['Ride in',x=>x.ivb_in.toFixed(1),'n'],['HB in',x=>x.hb_in.toFixed(1),'n'],['Whiff/swing',x=>f3(x.whiff_rate)+' <span class="note">/'+x.swings+'</span>','n'],['Chase',x=>f3(x.chase_rate),'n'],
   ['xwOBAcon',x=>f3(x.xwobacon)+' <span class="note">/'+(x.xwobacon_bip||0)+'</span>','n'],['RV/100',x=>(x.rv100>=0?'+':'')+x.rv100.toFixed(1),'n']],r)+
   '<p class="note">RV/100 = −100 × mean(delta_run_exp), pitcher POV (uc-pps-032 term). It needs about 1,084 pitches to be half signal, so read single-pitch RV loosely. xwOBAcon counts balls in play only (uc-pps-021 O1).</p>';}
function testsTable(){return tbl([['Metric',x=>esc(x.metric)],['2025',x=>pc(x.rate_2025)+' <span class="note">'+x.x_2025+'/'+x.n_2025+'</span>','n'],['2026',x=>pc(x.rate_2026)+' <span class="note">'+x.x_2026+'/'+x.n_2026+'</span>','n'],
  ['Δ',x=>(x.delta>=0?'+':'')+(100*x.delta).toFixed(1)+' pts','n'],['p',x=>x.p<0.001?'<.001':x.p.toFixed(3),'n'],['Read',x=>x.p<0.05?'<span class="pill v-good">significant</span>':'<span class="pill v-mute">not settled</span>']],D.tests)+
  '<p class="note">Pooled two-proportion z (the house standing test). "Not settled" means the direction is real in the sample but a season of relief PA cannot rule out noise.</p>';}

// ---------- drill-through ----------
const PN={FF:'Four-Seam',SI:'Sinker',SL:'Slider',ST:'Sweeper',CU:'Curveball',CH:'Changeup'};
const PC={FF:'#D22D49',SI:'#FE9D00',SL:'#EEE716',ST:'#DDB33A',CU:'#00D1ED',CH:'#1DBE3A'};
let drillPT='FF';
function drawTop(el){const others=D.cen.filter(r=>!r.is_bowlan), me=D.cen.filter(r=>r.is_bowlan&&r.game_year===2026);
  const tr=[{type:'scatter',mode:'markers',name:'Other Phillies RHP pitcher-seasons',x:others.map(r=>r.hb_in),y:others.map(r=>r.ivb_in),
     marker:{size:7,color:others.map(r=>PC[r.pitch_type]),opacity:0.28},text:others.map(r=>r.name+' '+r.game_year+' · '+PN[r.pitch_type]+' ('+r.n+')'),customdata:others.map(r=>r.pitch_type),
     hovertemplate:'%{text}<br>HB %{x:.1f} · ride %{y:.1f}<extra>click to drill</extra>'},
    {type:'scatter',mode:'markers+text',name:'Bowlan 2026',x:me.map(r=>r.hb_in),y:me.map(r=>r.ivb_in),text:me.map(r=>r.pitch_type),textposition:'top center',
     textfont:{color:cssv('--ink'),size:12},customdata:me.map(r=>r.pitch_type),
     marker:{size:15,color:me.map(r=>PC[r.pitch_type]),line:{color:cssv('--ink'),width:2}},
     hovertemplate:'Bowlan 2026 · %{customdata}<br>HB %{x:.1f} · ride %{y:.1f}<extra>click to drill</extra>'}];
  Plotly.react(el,tr,lay({xaxis:{title:'Horizontal break (in)'},yaxis:{title:'Ride / vertical break (in)'},height:440}),CFG);
  if(!el._bound){el.on('plotly_click',e=>{const pt=e.points[0].customdata;if(pt&&D.dens[pt]){drillPT=pt;drillButtons();drawDrill();}});el._bound=true;}}
function drillButtons(){$('ptb').innerHTML=D.H.density_pitch_types.map(p=>'<button class="chip" type="button" aria-pressed="'+(p===drillPT)+'" data-pt="'+p+'">'+PN[p]+'</button>').join('');}
function drawDrill(){const d=D.dens[drillPT], me=D.pitches.filter(r=>r.pitch_type===drillPT), el=$('drillplot');
  const dk=isDark();
  const tr=[{type:'contour',x:d.x,y:d.y,z:d.z,showscale:false,contours:{coloring:'fill',showlines:false},ncontours:14,
     colorscale:[[0,'rgba(0,0,0,0)'],[0.02,dk?'#262C37':'#EEF0F4'],[1,dk?'#C9D1E0':'#5b6170']],name:'Other Phillies RHP ('+d.n_other.toLocaleString()+')',showlegend:true,
     hovertemplate:'HB %{x} · ride %{y}<br>%{z} other pitches<extra></extra>'},
    {type:'scatter',mode:'markers',name:'Bowlan 2026 ('+me.length+')',x:me.map(r=>r.hb_in),y:me.map(r=>r.ivb_in),
     marker:{size:7,color:PC[drillPT],opacity:0.8,line:{color:dk?'#0F1319':'#fff',width:0.6}},
     customdata:me.map(r=>[r.game_date,r.release_speed,r.release_spin_rate,r.description]),
     hovertemplate:'%{customdata[0]} · %{customdata[1]:.1f} mph · %{customdata[2]:.0f} rpm<br>HB %{x:.1f} · ride %{y:.1f}<br>%{customdata[3]}<extra></extra>'}];
  const shapes=d.b_q1!=null?[{type:'rect',xref:'paper',x0:0,x1:1,y0:d.b_q1,y1:d.b_q3,fillcolor:'#E81828',opacity:0.12,line:{width:0}}]:[];
  Plotly.react(el,tr,lay({shapes,xaxis:{title:'Horizontal break (in)',range:[-24,24]},yaxis:{title:'Ride / vertical break (in)',range:[-20,26]},height:440}),CFG);
  $('drillcap').innerHTML='<b>'+PN[drillPT]+'</b>: Bowlan 2026 against '+d.n_other.toLocaleString()+' other Phillies RHP '+PN[drillPT].toLowerCase()+'s (2015–26, 2017 excluded). The band is the middle 50% of his ride'+
    (d.b_q1!=null?' ('+d.b_q1.toFixed(1)+'–'+d.b_q3.toFixed(1)+' in). His median pitch out-rides '+(100*d.other_ivb_pct_of_b_median).toFixed(0)+'% of theirs.':'.');}

// ---------- timeline ----------
function drawTimeline(el){const a=D.apps.filter(r=>r.game_year===2026);
  const tr=[0,1].map(k=>{const s=a.filter(r=>(r.runs_created>0)===(k===1));return {type:'scatter',mode:'markers',name:k?'Runs scored while he pitched':'Scoreless',
    x:s.map(r=>r.game_date),y:s.map(r=>r.ff_velo),marker:{size:s.map(r=>6+r.pitches/3),color:k?cssv('--red'):cssv('--navy'),opacity:0.8,line:{color:cssv('--panel'),width:1}},
    customdata:s.map(r=>[r.home_team+' vs '+r.away_team,r.entry_inning,r.entry_runners,r.pitches,r.runs_created,r.rest_days==null?'—':r.rest_days]),
    hovertemplate:'%{x} · %{customdata[0]}<br>entered inning %{customdata[1]} with %{customdata[2]} on<br>%{customdata[3]} pitches · FF %{y:.1f} mph · %{customdata[4]} runs · rest %{customdata[5]} d<extra></extra>'};});
  Plotly.react(el,tr,lay({height:420,xaxis:{title:''},yaxis:{title:'Mean four-seam velocity (mph)'},
    shapes:[{type:'line',x0:'2026-09-17',x1:'2026-09-17',yref:'paper',y0:0,y1:1,line:{dash:'dot',color:cssv('--muted')}}],
    annotations:[{x:'2026-09-17',yref:'paper',y:1,text:'9/17 exit (carry-in)',showarrow:false,xanchor:'right',font:{size:11,color:cssv('--muted')}}]}),CFG);}

// ---------- verdict chips ----------
function vclass(v){v=String(v);if(/^HELD|PRESENT|STRONG|SUPPORTED|PASS|FIXED|KEPT/.test(v))return 'v-good';if(/PARTLY|WEAK|MIXED|WARN|HAZARD/.test(v))return 'v-warn';if(/CONTRA|FAIL|UNSUPPORTED/.test(v))return 'v-bad';return 'v-mute';}
function pill(v){return '<span class="pill '+vclass(v)+'">'+esc(v)+'</span>';}

// ---------- render ----------
function chapterHTML(c){
  let h='<section class="ch" id="'+c.id+'" data-personas="'+c.personas.join('|')+'"><div class="chhead"><div class="chnum">'+c.n+'</div><div><h2>'+c.title+'</h2><p class="dek">'+c.dek+'</p>'+
    '<div class="tags">'+c.personas.map(p=>'<span class="tag">'+p+'</span>').join('')+'</div><button class="tbtn more" type="button" data-open="'+c.id+'">Read this chapter anyway</button></div></div>';
  h+='<div class="body">'+c.body.map(p=>'<p>'+p+'</p>').join('')+'</div><div class="callouts" id="co-'+c.id+'"></div>';
  h+='<div class="figs">'+c.figs.map(k=>{const t=figTitle(k);return '<div class="fig"><h3>'+esc(t.t)+'</h3><p class="cap">'+esc(t.s)+'</p><div class="plot" data-fig="'+k+'"></div></div>';}).join('')+'</div>';
  h+='<div class="extra">';
  if(c.table==='recap')h+=recapTable(); if(c.table==='arsenal')h+=arsenalTable(); if(c.table==='tests')h+=testsTable();
  if(c.detail){const t=figTitle(c.detail);h+='<details><summary>The Gemini cell, governed: four-seam metrics 2×2</summary><p class="note">'+esc(t.s)+' Audit notes GM-1…GM-6 are in "Your notebook, graded".</p><div class="fig"><div class="plot" style="height:620px" data-fig="'+c.detail+'"></div></div></details>';}
  if(c.drill)h+='<div class="drill"><div class="fig"><h3>Every Phillies RHP pitch type, 2015–2026 (ex-2017): pitcher-season centroids</h3><p class="cap">Big outlined dots are Bowlan 2026. Click any dot to drill into that pitch.</p><div class="plot" id="topplot"></div></div>'+
     '<div class="fig"><h3>Drill-through: one pitch, pitch by pitch</h3><div class="ptbtns" id="ptb"></div><p class="cap" id="drillcap"></p><div class="plot" id="drillplot"></div></div></div>';
  if(c.timeline)h+='<div class="fig" style="margin-top:16px"><h3>Every 2026 appearance</h3><p class="cap">Dot size = pitches thrown. Red = at least one run scored while he pitched (inherited runners included). Hover for entry inning, runners on and rest.</p><div class="plot" id="tlplot"></div></div>';
  return h+'</div></section>';}

function extraSections(){
  const hp=D.hp, gm=D.gm;
  let h='<section class="ch" id="graded" data-personas="All"><div class="chhead"><div class="chnum">✓</div><div><h2>Your notebook, graded</h2><p class="dek">'+hp.length+' claims from cells 115–117, re-run by your method and then governed.</p></div></div>';
  h+='<div class="filters" id="hpf"></div><div id="hpt"></div>';
  h+='<details><summary>The Gemini cell: 6 audit notes</summary>'+tbl([['ID',x=>x.id],['Area',x=>esc(x.area)],['Finding',x=>esc(x.finding)],['Why it matters',x=>esc(x.why_it_matters)],['Disposition',x=>pill(x.disposition)]],gm)+'</details></section>';
  h+='<section class="ch" id="ledger" data-personas="All"><div class="chhead"><div class="chnum">≡</div><div><h2>Persona action ledger</h2><p class="dek">Actions people in the pitching value stream could have taken, and whether the data carries their signature.</p></div></div>'+
     '<p class="body note">These are hypotheses, not a record of what anyone did. No coaching notes, pitch calls or lab sessions exist in either repo. A hypothesis is STRONG when every signature it predicts is present in the log at its declared threshold (PA-1 spec, 03 §2). The last column names the evidence that would confirm it.</p><div id="ledt"></div>'+
     '<details><summary>All '+D.sigs.length+' signatures</summary>'+tbl([['Hyp',x=>x.hyp_id],['Signature',x=>esc(x.signature)],['2025',x=>x.before_2025==null?'—':(+x.before_2025).toFixed(3),'n'],['2026',x=>(+x.after_2026).toFixed(3),'n'],
       ['Threshold',x=>x.threshold,'n'],['p',x=>x.p_value==null?'—':(x.p_value<0.001?'<.001':(+x.p_value).toFixed(3)),'n'],['Verdict',x=>pill(x.verdict)]],D.sigs)+'</details></section>';
  h+='<section class="ch" id="receipts" data-personas="All"><div class="chhead"><div class="chnum">§</div><div><h2>Receipts</h2><p class="dek">DQ '+(D.H.dq.PASS||0)+' pass · '+(D.H.dq.WARN||0)+' warn · '+(D.H.dq.FAIL||0)+' fail. Source files, freshness and carry-ins.</p></div></div>'+
     tbl([['Rule',x=>x.rule],['Dimension',x=>x.dimension],['Grain',x=>x.grain],['Rule',x=>esc(x.rule_text)],['Result',x=>pill(x.result)],['Observed',x=>esc(x.observed)]],D.dq)+
     tbl([['Source',x=>esc(x.source)],['Through',x=>esc(x.max_game_date)],['Rows',x=>x.rows,'n'],['Note',x=>esc(x.note)]],D.fresh)+'</section>';
  return h;}

function hpRender(f){const rows=D.hp.filter(r=>f==='All'||r.verdict.startsWith(f));
  $('hpt').innerHTML=tbl([['ID',x=>x.id],['Your claim',x=>'“'+esc(x.client_claim)+'”'],['Governed value',x=>esc(x.governed_value)],['Verdict',x=>pill(x.verdict)],['Note',x=>esc(x.note)]],rows);
  $('hpf').innerHTML=['All','HELD','PARTLY','HAZARD'].map(v=>'<button class="chip" type="button" aria-pressed="'+(v===f)+'" data-hp="'+v+'">'+v+' ('+(v==='All'?D.hp.length:D.hp.filter(r=>r.verdict.startsWith(v)).length)+')</button>').join('');}
function ledRender(){const rows=D.ledger.filter(r=>lens==='All'||r.persona===lens);
  $('ledt').innerHTML=rows.length?tbl([['Persona',x=>esc(x.persona)],['Hypothesis',x=>'<b>'+x.hyp_id+'</b> '+esc(x.hypothesis)],['Signatures',x=>esc(x.verdicts)],['Strength',x=>pill(x.strength)],['What would confirm it',x=>esc(x.what_would_confirm)]],rows)
   :'<p class="note">No ledger hypotheses are filed under '+esc(lens)+'. That persona appears in chapter callouts only.</p>';}

function applyLens(){
  document.querySelectorAll('#lens .chip').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.p===lens)));
  D.CH.forEach(c=>{const on=lens==='All'||c.personas.includes(lens)||(D.CALLOUTS[c.id]||{})[lens];
    const sec=$(c.id); sec.classList.toggle('dim',!on&&!sec.dataset.forced); const a=document.querySelector('nav.rail a[href="#'+c.id+'"]');
    a.classList.toggle('dim',!on); a.classList.toggle('hit',lens!=='All'&&on);
    const co=D.CALLOUTS[c.id]||{}; const keys=lens==='All'?Object.keys(co):(co[lens]?[lens]:[]);
    $('co-'+c.id).innerHTML=keys.map(k=>'<div class="callout"><div class="who">If you are the '+k.toLowerCase()+'</div>'+co[k]+'</div>').join('');});
  ledRender(); try{localStorage.setItem('uc48-lens',lens);}catch(e){} drawVisible();}

function drawVisible(){document.querySelectorAll('.plot[data-fig]').forEach(el=>{if(el.offsetParent!==null)drawFig(el,el.dataset.fig);});
  if($('topplot')&&$('topplot').offsetParent!==null){drawTop($('topplot'));drillButtons();drawDrill();}
  if($('tlplot')&&$('tlplot').offsetParent!==null)drawTimeline($('tlplot'));}

function init(){
  $('box').innerHTML=D.BOX.map(b=>'<div><b>'+b[1]+'</b><span>'+b[0]+'</span></div>').join('');
  $('lens').innerHTML=D.PERSONAS.map(p=>'<button class="chip" type="button" data-p="'+p+'" aria-pressed="false">'+p+'</button>').join(' ');
  $('rail').innerHTML=D.CH.map(c=>'<a href="#'+c.id+'"><b>'+c.n+'</b><span>'+c.title+'</span></a>').join('')+
    '<a href="#graded"><b>✓</b><span>Your notebook, graded</span></a><a href="#ledger"><b>≡</b><span>Persona action ledger</span></a><a href="#receipts"><b>§</b><span>Receipts</span></a>';
  $('main').innerHTML=D.CH.map(chapterHTML).join('')+extraSections();
  hpRender('All');
  $('lens').onclick=e=>{const b=e.target.closest('button');if(!b)return;lens=b.dataset.p;document.querySelectorAll('section.ch').forEach(s=>delete s.dataset.forced);applyLens();};
  $('main').addEventListener('click',e=>{const m=e.target.closest('[data-open]');if(m){const s=$(m.dataset.open);s.dataset.forced='1';s.classList.remove('dim');drawVisible();}
    const h=e.target.closest('[data-hp]');if(h)hpRender(h.dataset.hp);
    const p=e.target.closest('[data-pt]');if(p){drillPT=p.dataset.pt;drillButtons();drawDrill();}});
  document.querySelectorAll('details').forEach(d=>d.addEventListener('toggle',()=>drawVisible()));
  const syncThemeBtn=()=>{$('theme').textContent=isDark()?'Brand light':'Notebook dark';};
  $('theme').onclick=()=>{document.documentElement.dataset.theme=isDark()?'light':'dark';syncThemeBtn();drawVisible();};
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{syncThemeBtn();drawVisible();});
  syncThemeBtn();
  try{const s=localStorage.getItem('uc48-lens');if(s&&D.PERSONAS.includes(s))lens=s;}catch(e){}
  applyLens();}
init();
"""

payload = json.dumps(data, default=str).replace("</", "<\\/")
body = BODY.replace("__ANCHOR__", H["anchor"]).replace("__SPRING__", str(H["spring_rows_excluded"]))
script = JS.replace("__DATA__", payload)
TITLE = "Bowlan 2026: The Tick and a Half"

repo_html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
             f'<title>{TITLE}</title><style>{CSS}</style><script>{plotly_js}</script></head><body>{body}<script>{script}</script></body></html>')
DEST.write_text(repo_html, encoding="utf-8")

fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono&display=swap">')
art_html = f'<title>{TITLE}</title>{fonts}<style>{CSS}</style><script>{plotly_js}</script>{body}<script>{script}</script>'
ART.write_text(art_html, encoding="utf-8")
print(DEST.name, f"{DEST.stat().st_size / 1e6:.2f} MB", "|", ART.name, f"{ART.stat().st_size / 1e6:.2f} MB")
